你好，我是张磊。今天我和你分享的主题是：容器存储实践之CSI插件编写指南。

在上一篇文章中，我已经为你详细讲解了CSI插件机制的设计原理。今天我将继续和你一起实践一个CSI插件的编写过程。

为了能够覆盖到CSI插件的所有功能，我这一次选择了DigitalOcean的块存储（Block Storage）服务，来作为实践对象。

DigitalOcean是业界知名的“最简”公有云服务，即：它只提供虚拟机、存储、网络等为数不多的几个基础功能，其他功能一概不管。而这，恰恰就使得DigitalOcean成了我们在公有云上实践Kubernetes的最佳选择。

我们这次编写的CSI插件的功能，就是：让我们运行在DigitalOcean上的Kubernetes集群能够使用它的块存储服务，作为容器的持久化存储。

> 备注：在DigitalOcean上部署一个Kubernetes集群的过程，也很简单。你只需要先在DigitalOcean上创建几个虚拟机，然后按照我们在第11篇文章 [《从0到1：搭建一个完整的Kubernetes集群》](https://time.geekbang.org/column/article/39724) 中从0到1的步骤直接部署即可。

而有了CSI插件之后，持久化存储的用法就非常简单了，你只需要创建一个如下所示的StorageClass对象即可：

```
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: do-block-storage
  namespace: kube-system
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: com.digitalocean.csi.dobs

```

有了这个StorageClass，External Provisoner就会为集群中新出现的PVC自动创建出PV，然后调用CSI插件创建出这个PV对应的Volume，这正是CSI体系中Dynamic Provisioning的实现方式。

> 备注： `storageclass.kubernetes.io/is-default-class: "true"` 的意思，是使用这个StorageClass作为默认的持久化存储提供者。

不难看到，这个StorageClass里唯一引人注意的，是provisioner=com.digitalocean.csi.dobs这个字段。显然，这个字段告诉了Kubernetes，请使用名叫com.digitalocean.csi.dobs的CSI插件来为我处理这个StorageClass相关的所有操作。

那么，Kubernetes又是如何知道一个CSI插件的名字的呢？

**这就需要从CSI插件的第一个服务CSI Identity说起了。**

其实，一个CSI插件的代码结构非常简单，如下所示：

```
tree $GOPATH/src/github.com/digitalocean/csi-digitalocean/driver
$GOPATH/src/github.com/digitalocean/csi-digitalocean/driver
├── controller.go
├── driver.go
├── identity.go
├── mounter.go
└── node.go

```

其中，CSI Identity服务的实现，就定义在了driver目录下的identity.go文件里。

当然，为了能够让Kubernetes访问到CSI Identity服务，我们需要先在driver.go文件里，定义一个标准的gRPC Server，如下所示：

```
// Run starts the CSI plugin by communication over the given endpoint
func (d *Driver) Run() error {
 ...

 listener, err := net.Listen(u.Scheme, addr)
 ...

 d.srv = grpc.NewServer(grpc.UnaryInterceptor(errHandler))
 csi.RegisterIdentityServer(d.srv, d)
 csi.RegisterControllerServer(d.srv, d)
 csi.RegisterNodeServer(d.srv, d)

 d.ready = true // we're now ready to go!
 ...
 return d.srv.Serve(listener)
}

```

可以看到，只要把编写好的gRPC Server注册给CSI，它就可以响应来自External Components的CSI请求了。

**CSI Identity服务中，最重要的接口是GetPluginInfo**，它返回的就是这个插件的名字和版本号，如下所示：

> 备注：CSI各个服务的接口我在上一篇文章中已经介绍过，你也可以在这里找到 [它的protoc文件](https://github.com/container-storage-interface/spec/blob/master/csi.proto)。

```
func (d *Driver) GetPluginInfo(ctx context.Context, req *csi.GetPluginInfoRequest) (*csi.GetPluginInfoResponse, error) {
 resp := &csi.GetPluginInfoResponse{
  Name:          driverName,
  VendorVersion: version,
 }
 ...
}

```

其中，driverName的值，正是"com.digitalocean.csi.dobs"。所以说，Kubernetes正是通过GetPluginInfo的返回值，来找到你在StorageClass里声明要使用的CSI插件的。

> 备注：CSI要求插件的名字遵守 [“反向DNS”格式](https://en.wikipedia.org/wiki/Reverse_domain_name_notation)。

另外一个 **GetPluginCapabilities接口也很重要**。这个接口返回的是这个CSI插件的“能力”。

比如，当你编写的CSI插件不准备实现“Provision阶段”和“Attach阶段”（比如，一个最简单的NFS存储插件就不需要这两个阶段）时，你就可以通过这个接口返回：本插件不提供CSI Controller服务，即：没有csi.PluginCapability\_Service\_CONTROLLER\_SERVICE这个“能力”。这样，Kubernetes就知道这个信息了。

最后， **CSI Identity服务还提供了一个Probe接口**。Kubernetes会调用它来检查这个CSI插件是否正常工作。

一般情况下，我建议你在编写插件时给它设置一个Ready标志，当插件的gRPC Server停止的时候，把这个Ready标志设置为false。或者，你可以在这里访问一下插件的端口，类似于健康检查的做法。

> 备注：关于健康检查的问题，你可以再回顾一下第15篇文章 [《深入解析Pod对象（二）：使用进阶》](https://time.geekbang.org/column/article/40466) 中的相关内容。

然后，我们要开始编写CSI 插件的第二个服务，即CSI Controller服务了。它的代码实现，在controller.go文件里。

在上一篇文章中我已经为你讲解过，这个服务主要实现的就是Volume管理流程中的“Provision阶段”和“Attach阶段”。

**“Provision阶段”对应的接口，是CreateVolume和DeleteVolume**，它们的调用者是External Provisoner。以CreateVolume为例，它的主要逻辑如下所示：

```
func (d *Driver) CreateVolume(ctx context.Context, req *csi.CreateVolumeRequest) (*csi.CreateVolumeResponse, error) {
 ...

 volumeReq := &godo.VolumeCreateRequest{
  Region:        d.region,
  Name:          volumeName,
  Description:   createdByDO,
  SizeGigaBytes: size / GB,
 }

 ...

 vol, _, err := d.doClient.Storage.CreateVolume(ctx, volumeReq)

 ...

 resp := &csi.CreateVolumeResponse{
  Volume: &csi.Volume{
   Id:            vol.ID,
   CapacityBytes: size,
   AccessibleTopology: []*csi.Topology{
    {
     Segments: map[string]string{
      "region": d.region,
     },
    },
   },
  },
 }

 return resp, nil
}

```

可以看到，对于DigitalOcean这样的公有云来说，CreateVolume需要做的操作，就是调用DigitalOcean块存储服务的API，创建出一个存储卷（d.doClient.Storage.CreateVolume）。如果你使用的是其他类型的块存储（比如Cinder、Ceph RBD等），对应的操作也是类似地调用创建存储卷的API。

而“ **Attach阶段”对应的接口是ControllerPublishVolume和ControllerUnpublishVolume**，它们的调用者是External Attacher。以ControllerPublishVolume为例，它的逻辑如下所示：

```
func (d *Driver) ControllerPublishVolume(ctx context.Context, req *csi.ControllerPublishVolumeRequest) (*csi.ControllerPublishVolumeResponse, error) {
 ...

  dropletID, err := strconv.Atoi(req.NodeId)

  // check if volume exist before trying to attach it
  _, resp, err := d.doClient.Storage.GetVolume(ctx, req.VolumeId)

 ...

  // check if droplet exist before trying to attach the volume to the droplet
  _, resp, err = d.doClient.Droplets.Get(ctx, dropletID)

 ...

  action, resp, err := d.doClient.StorageActions.Attach(ctx, req.VolumeId, dropletID)

 ...

 if action != nil {
  ll.Info("waiting until volume is attached")
 if err := d.waitAction(ctx, req.VolumeId, action.ID); err != nil {
  return nil, err
  }
  }

  ll.Info("volume is attached")
 return &csi.ControllerPublishVolumeResponse{}, nil
}

```

可以看到，对于DigitalOcean来说，ControllerPublishVolume在“Attach阶段”需要做的工作，是调用DigitalOcean的API，将我们前面创建的存储卷，挂载到指定的虚拟机上（d.doClient.StorageActions.Attach）。

其中，存储卷由请求中的VolumeId来指定。而虚拟机，也就是将要运行Pod的宿主机，则由请求中的NodeId来指定。这些参数，都是External Attacher在发起请求时需要设置的。

我在上一篇文章中已经为你介绍过，External Attacher的工作原理，是监听（Watch）了一种名叫VolumeAttachment的API对象。这种API对象的主要字段如下所示：

```
// VolumeAttachmentSpec is the specification of a VolumeAttachment request.
type VolumeAttachmentSpec struct {
 // Attacher indicates the name of the volume driver that MUST handle this
 // request. This is the name returned by GetPluginName().
 Attacher string

 // Source represents the volume that should be attached.
 Source VolumeAttachmentSource

 // The node that the volume should be attached to.
 NodeName string
}

```

而这个对象的生命周期，正是由AttachDetachController负责管理的（这里，你可以再回顾一下第28篇文章 [《PV、PVC、StorageClass，这些到底在说啥？》](https://time.geekbang.org/column/article/42698) 中的相关内容）。

这个控制循环的职责，是不断检查Pod所对应的PV，在它所绑定的宿主机上的挂载情况，从而决定是否需要对这个PV进行Attach（或者Dettach）操作。

而这个Attach操作，在CSI体系里，就是创建出上面这样一个VolumeAttachment对象。可以看到，Attach操作所需的PV的名字（Source）、宿主机的名字（NodeName）、存储插件的名字（Attacher），都是这个VolumeAttachment对象的一部分。

而当External Attacher监听到这样的一个对象出现之后，就可以立即使用VolumeAttachment里的这些字段，封装成一个gRPC请求调用CSI Controller的ControllerPublishVolume方法。

最后，我们就可以编写CSI Node服务了。

CSI Node服务对应的，是Volume管理流程里的“Mount阶段”。它的代码实现，在node.go文件里。

我在上一篇文章里曾经提到过，kubelet的VolumeManagerReconciler控制循环会直接调用CSI Node服务来完成Volume的“Mount阶段”。

不过，在具体的实现中，这个“Mount阶段”的处理其实被细分成了NodeStageVolume和NodePublishVolume这两个接口。

这里的原因其实也很容易理解：我在第28篇文章 [《PV、PVC、StorageClass，这些到底在说啥？》](https://time.geekbang.org/column/article/42698) 中曾经介绍过，对于磁盘以及块设备来说，它们被Attach到宿主机上之后，就成为了宿主机上的一个待用存储设备。而到了“Mount阶段”，我们首先需要格式化这个设备，然后才能把它挂载到Volume对应的宿主机目录上。

在kubelet的VolumeManagerReconciler控制循环中，这两步操作分别叫作 **MountDevice和SetUp。**

其中，MountDevice操作，就是直接调用了CSI Node服务里的NodeStageVolume接口。顾名思义，这个接口的作用，就是格式化Volume在宿主机上对应的存储设备，然后挂载到一个临时目录（Staging目录）上。

对于DigitalOcean来说，它对NodeStageVolume接口的实现如下所示：

```
func (d *Driver) NodeStageVolume(ctx context.Context, req *csi.NodeStageVolumeRequest) (*csi.NodeStageVolumeResponse, error) {
 ...

 vol, resp, err := d.doClient.Storage.GetVolume(ctx, req.VolumeId)

 ...

 source := getDiskSource(vol.Name)
 target := req.StagingTargetPath

 ...

 if !formatted {
  ll.Info("formatting the volume for staging")
  if err := d.mounter.Format(source, fsType); err != nil {
   return nil, status.Error(codes.Internal, err.Error())
  }
 } else {
  ll.Info("source device is already formatted")
 }

...

 if !mounted {
  if err := d.mounter.Mount(source, target, fsType, options...); err != nil {
   return nil, status.Error(codes.Internal, err.Error())
  }
 } else {
  ll.Info("source device is already mounted to the target path")
 }

 ...
 return &csi.NodeStageVolumeResponse{}, nil
}

```

可以看到，在NodeStageVolume的实现里，我们首先通过DigitalOcean的API获取到了这个Volume对应的设备路径（getDiskSource）；然后，我们把这个设备格式化成指定的格式（ d.mounter.Format）；最后，我们把格式化后的设备挂载到了一个临时的Staging目录（StagingTargetPath）下。

而SetUp操作则会调用CSI Node服务的NodePublishVolume接口。有了上述对设备的预处理工作后，它的实现就非常简单了，如下所示：

```
func (d *Driver) NodePublishVolume(ctx context.Context, req *csi.NodePublishVolumeRequest) (*csi.NodePublishVolumeResponse, error) {
 ...
 source := req.StagingTargetPath
 target := req.TargetPath

 mnt := req.VolumeCapability.GetMount()
 options := mnt.MountFlag
    ...

 if !mounted {
  ll.Info("mounting the volume")
  if err := d.mounter.Mount(source, target, fsType, options...); err != nil {
   return nil, status.Error(codes.Internal, err.Error())
  }
 } else {
  ll.Info("volume is already mounted")
 }

 return &csi.NodePublishVolumeResponse{}, nil
}

```

可以看到，在这一步实现中，我们只需要做一步操作，即：将Staging目录，绑定挂载到Volume对应的宿主机目录上。

由于Staging目录，正是Volume对应的设备被格式化后挂载在宿主机上的位置，所以当它和Volume的宿主机目录绑定挂载之后，这个Volume宿主机目录的“持久化”处理也就完成了。

当然，我在前面也曾经提到过，对于文件系统类型的存储服务来说，比如NFS和GlusterFS等，它们并没有一个对应的磁盘“设备”存在于宿主机上，所以kubelet在VolumeManagerReconciler控制循环中，会跳过MountDevice操作而直接执行SetUp操作。所以对于它们来说，也就不需要实现NodeStageVolume接口了。

在编写完了CSI插件之后，我们就可以把这个插件和External Components一起部署起来。

首先，我们需要创建一个DigitalOcean client授权需要使用的Secret对象，如下所示：

```
apiVersion: v1
kind: Secret
metadata:
  name: digitalocean
  namespace: kube-system
stringData:
  access-token: "a05dd2f26b9b9ac2asdas__REPLACE_ME____123cb5d1ec17513e06da"

```

接下来，我们通过一句指令就可以将CSI插件部署起来：

```
$ kubectl apply -f https://raw.githubusercontent.com/digitalocean/csi-digitalocean/master/deploy/kubernetes/releases/csi-digitalocean-v0.2.0.yaml

```

这个CSI插件的YAML文件的主要内容如下所示（其中，非重要的内容已经被略去）：

```
kind: DaemonSet
apiVersion: apps/v1beta2
metadata:
  name: csi-do-node
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: csi-do-node
  template:
    metadata:
      labels:
        app: csi-do-node
        role: csi-do
    spec:
      serviceAccount: csi-do-node-sa
      hostNetwork: true
      containers:
        - name: driver-registrar
          image: quay.io/k8scsi/driver-registrar:v0.3.0
          ...
        - name: csi-do-plugin
          image: digitalocean/do-csi-plugin:v0.2.0
          args :
            - "--endpoint=$(CSI_ENDPOINT)"
            - "--token=$(DIGITALOCEAN_ACCESS_TOKEN)"
            - "--url=$(DIGITALOCEAN_API_URL)"
          env:
            - name: CSI_ENDPOINT
              value: unix:///csi/csi.sock
            - name: DIGITALOCEAN_API_URL
              value: https://api.digitalocean.com/
            - name: DIGITALOCEAN_ACCESS_TOKEN
              valueFrom:
                secretKeyRef:
                  name: digitalocean
                  key: access-token
          imagePullPolicy: "Always"
          securityContext:
            privileged: true
            capabilities:
              add: ["SYS_ADMIN"]
            allowPrivilegeEscalation: true
          volumeMounts:
            - name: plugin-dir
              mountPath: /csi
            - name: pods-mount-dir
              mountPath: /var/lib/kubelet
              mountPropagation: "Bidirectional"
            - name: device-dir
              mountPath: /dev
      volumes:
        - name: plugin-dir
          hostPath:
            path: /var/lib/kubelet/plugins/com.digitalocean.csi.dobs
            type: DirectoryOrCreate
        - name: pods-mount-dir
          hostPath:
            path: /var/lib/kubelet
            type: Directory
        - name: device-dir
          hostPath:
            path: /dev
---
kind: StatefulSet
apiVersion: apps/v1beta1
metadata:
  name: csi-do-controller
  namespace: kube-system
spec:
  serviceName: "csi-do"
  replicas: 1
  template:
    metadata:
      labels:
        app: csi-do-controller
        role: csi-do
    spec:
      serviceAccount: csi-do-controller-sa
      containers:
        - name: csi-provisioner
          image: quay.io/k8scsi/csi-provisioner:v0.3.0
          ...
        - name: csi-attacher
          image: quay.io/k8scsi/csi-attacher:v0.3.0
          ...
        - name: csi-do-plugin
          image: digitalocean/do-csi-plugin:v0.2.0
          args :
            - "--endpoint=$(CSI_ENDPOINT)"
            - "--token=$(DIGITALOCEAN_ACCESS_TOKEN)"
            - "--url=$(DIGITALOCEAN_API_URL)"
          env:
            - name: CSI_ENDPOINT
              value: unix:///var/lib/csi/sockets/pluginproxy/csi.sock
            - name: DIGITALOCEAN_API_URL
              value: https://api.digitalocean.com/
            - name: DIGITALOCEAN_ACCESS_TOKEN
              valueFrom:
                secretKeyRef:
                  name: digitalocean
                  key: access-token
          imagePullPolicy: "Always"
          volumeMounts:
            - name: socket-dir
              mountPath: /var/lib/csi/sockets/pluginproxy/
      volumes:
        - name: socket-dir
          emptyDir: {}

```

可以看到，我们编写的CSI插件只有一个二进制文件，它的镜像是digitalocean/do-csi-plugin:v0.2.0。

而我们 **部署CSI插件的常用原则是：**

**第一，通过DaemonSet在每个节点上都启动一个CSI插件，来为kubelet提供CSI Node服务**。这是因为，CSI Node服务需要被kubelet直接调用，所以它要和kubelet“一对一”地部署起来。

此外，在上述DaemonSet的定义里面，除了CSI插件，我们还以sidecar的方式运行着driver-registrar这个外部组件。它的作用，是向kubelet注册这个CSI插件。这个注册过程使用的插件信息，则通过访问同一个Pod里的CSI插件容器的Identity服务获取到。

需要注意的是，由于CSI插件运行在一个容器里，那么CSI Node服务在“Mount阶段”执行的挂载操作，实际上是发生在这个容器的Mount Namespace里的。可是，我们真正希望执行挂载操作的对象，都是宿主机/var/lib/kubelet目录下的文件和目录。

所以，在定义DaemonSet Pod的时候，我们需要把宿主机的/var/lib/kubelet以Volume的方式挂载进CSI插件容器的同名目录下，然后设置这个Volume的mountPropagation=Bidirectional，即开启双向挂载传播，从而将容器在这个目录下进行的挂载操作“传播”给宿主机，反之亦然。

**第二，通过StatefulSet在任意一个节点上再启动一个CSI插件，为External Components提供CSI Controller服务**。所以，作为CSI Controller服务的调用者，External Provisioner和External Attacher这两个外部组件，就需要以sidecar的方式和这次部署的CSI插件定义在同一个Pod里。

你可能会好奇，为什么我们会用StatefulSet而不是Deployment来运行这个CSI插件呢。

这是因为，由于StatefulSet需要确保应用拓扑状态的稳定性，所以它对Pod的更新，是严格保证顺序的，即：只有在前一个Pod停止并删除之后，它才会创建并启动下一个Pod。

而像我们上面这样将StatefulSet的replicas设置为1的话，StatefulSet就会确保Pod被删除重建的时候，永远有且只有一个CSI插件的Pod运行在集群中。这对CSI插件的正确性来说，至关重要。

而在今天这篇文章一开始，我们就已经定义了这个CSI插件对应的StorageClass（即：do-block-storage），所以你接下来只需要定义一个声明使用这个StorageClass的PVC即可，如下所示：

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: csi-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: do-block-storage

```

当你把上述PVC提交给Kubernetes之后，你就可以在Pod里声明使用这个csi-pvc来作为持久化存储了。这一部分使用PV和PVC的内容，我就不再赘述了。

## 总结

在今天这篇文章中，我以一个DigitalOcean的CSI插件为例，和你分享了编写CSI插件的具体流程。

基于这些讲述，你现在应该已经对Kubernetes持久化存储体系有了一个更加全面和深入的认识。

举个例子，对于一个部署了CSI存储插件的Kubernetes集群来说：

当用户创建了一个PVC之后，你前面部署的StatefulSet里的External Provisioner容器，就会监听到这个PVC的诞生，然后调用同一个Pod里的CSI插件的CSI Controller服务的CreateVolume方法，为你创建出对应的PV。

这时候，运行在Kubernetes Master节点上的Volume Controller，就会通过PersistentVolumeController控制循环，发现这对新创建出来的PV和PVC，并且看到它们声明的是同一个StorageClass。所以，它会把这一对PV和PVC绑定起来，使PVC进入Bound状态。

然后，用户创建了一个声明使用上述PVC的Pod，并且这个Pod被调度器调度到了宿主机A上。这时候，Volume Controller的AttachDetachController控制循环就会发现，上述PVC对应的Volume，需要被Attach到宿主机A上。所以，AttachDetachController会创建一个VolumeAttachment对象，这个对象携带了宿主机A和待处理的Volume的名字。

这样，StatefulSet里的External Attacher容器，就会监听到这个VolumeAttachment对象的诞生。于是，它就会使用这个对象里的宿主机和Volume名字，调用同一个Pod里的CSI插件的CSI Controller服务的ControllerPublishVolume方法，完成“Attach阶段”。

上述过程完成后，运行在宿主机A上的kubelet，就会通过VolumeManagerReconciler控制循环，发现当前宿主机上有一个Volume对应的存储设备（比如磁盘）已经被Attach到了某个设备目录下。于是kubelet就会调用同一台宿主机上的CSI插件的CSI Node服务的NodeStageVolume和NodePublishVolume方法，完成这个Volume的“Mount阶段”。

至此，一个完整的持久化Volume的创建和挂载流程就结束了。

## 思考题

请你根据编写FlexVolume和CSI插件的流程，分析一下什么时候该使用FlexVolume，什么时候应该使用CSI？

感谢你的收听，欢迎你给我留言，也欢迎分享给更多的朋友一起阅读。