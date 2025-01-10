你好，我是张磊。今天我和你分享的主题是：深入理解StatefulSet之存储状态。

在上一篇文章中，我和你分享了StatefulSet如何保证应用实例的拓扑状态，在Pod删除和再创建的过程中保持稳定。

而在今天这篇文章中，我将继续为你解读StatefulSet对存储状态的管理机制。这个机制，主要使用的是一个叫作Persistent Volume Claim的功能。

在前面介绍Pod的时候，我曾提到过，要在一个Pod里声明Volume，只要在Pod里加上spec.volumes字段即可。然后，你就可以在这个字段里定义一个具体类型的Volume了，比如：hostPath。

可是，你有没有想过这样一个场景： **如果你并不知道有哪些Volume类型可以用，要怎么办呢**？

更具体地说，作为一个应用开发者，我可能对持久化存储项目（比如Ceph、GlusterFS等）一窍不通，也不知道公司的Kubernetes集群里到底是怎么搭建出来的，我也自然不会编写它们对应的Volume定义文件。

所谓“术业有专攻”，这些关于Volume的管理和远程持久化存储的知识，不仅超越了开发者的知识储备，还会有暴露公司基础设施秘密的风险。

比如，下面这个例子，就是一个声明了Ceph RBD类型Volume的Pod：

```
apiVersion: v1
kind: Pod
metadata:
  name: rbd
spec:
  containers:
    - image: kubernetes/pause
      name: rbd-rw
      volumeMounts:
      - name: rbdpd
        mountPath: /mnt/rbd
  volumes:
    - name: rbdpd
      rbd:
        monitors:
        - '10.16.154.78:6789'
        - '10.16.154.82:6789'
        - '10.16.154.83:6789'
        pool: kube
        image: foo
        fsType: ext4
        readOnly: true
        user: admin
        keyring: /etc/ceph/keyring
        imageformat: "2"
        imagefeatures: "layering"

```

其一，如果不懂得Ceph RBD的使用方法，那么这个Pod里Volumes字段，你十有八九也完全看不懂。其二，这个Ceph RBD对应的存储服务器的地址、用户名、授权文件的位置，也都被轻易地暴露给了全公司的所有开发人员，这是一个典型的信息被“过度暴露”的例子。

这也是为什么，在后来的演化中， **Kubernetes项目引入了一组叫作Persistent Volume Claim（PVC）和Persistent Volume（PV）的API对象，大大降低了用户声明和使用持久化Volume的门槛。**

举个例子，有了PVC之后，一个开发人员想要使用一个Volume，只需要简单的两步即可。

**第一步：定义一个PVC，声明想要的Volume的属性：**

```
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: pv-claim
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi

```

可以看到，在这个PVC对象里，不需要任何关于Volume细节的字段，只有描述性的属性和定义。比如，storage: 1Gi，表示我想要的Volume大小至少是1 GiB；accessModes: ReadWriteOnce，表示这个Volume的挂载方式是可读写，并且只能被挂载在一个节点上而非被多个节点共享。

> 备注：关于哪种类型的Volume支持哪种类型的AccessMode，你可以查看Kubernetes项目官方文档中的 [详细列表](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes)。

**第二步：在应用的Pod中，声明使用这个PVC：**

```
apiVersion: v1
kind: Pod
metadata:
  name: pv-pod
spec:
  containers:
    - name: pv-container
      image: nginx
      ports:
        - containerPort: 80
          name: "http-server"
      volumeMounts:
        - mountPath: "/usr/share/nginx/html"
          name: pv-storage
  volumes:
    - name: pv-storage
      persistentVolumeClaim:
        claimName: pv-claim

```

可以看到，在这个Pod的Volumes定义中，我们只需要声明它的类型是persistentVolumeClaim，然后指定PVC的名字，而完全不必关心Volume本身的定义。

这时候，只要我们创建这个PVC对象，Kubernetes就会自动为它绑定一个符合条件的Volume。可是，这些符合条件的Volume又是从哪里来的呢？

答案是，它们来自于由运维人员维护的PV（Persistent Volume）对象。接下来，我们一起看一个常见的PV对象的YAML文件：

```
kind: PersistentVolume
apiVersion: v1
metadata:
  name: pv-volume
  labels:
    type: local
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  rbd:
    monitors:
    # 使用 kubectl get pods -n rook-ceph 查看 rook-ceph-mon- 开头的 POD IP 即可得下面的列表
    - '10.16.154.78:6789'
    - '10.16.154.82:6789'
    - '10.16.154.83:6789'
    pool: kube
    image: foo
    fsType: ext4
    readOnly: true
    user: admin
    keyring: /etc/ceph/keyring

```

可以看到，这个PV对象的spec.rbd字段，正是我们前面介绍过的Ceph RBD Volume的详细定义。而且，它还声明了这个PV的容量是10 GiB。这样，Kubernetes就会为我们刚刚创建的PVC对象绑定这个PV。

所以，Kubernetes中PVC和PV的设计， **实际上类似于“接口”和“实现”的思想**。开发者只要知道并会使用“接口”，即：PVC；而运维人员则负责给“接口”绑定具体的实现，即：PV。

这种解耦，就避免了因为向开发者暴露过多的存储系统细节而带来的隐患。此外，这种职责的分离，往往也意味着出现事故时可以更容易定位问题和明确责任，从而避免“扯皮”现象的出现。

而PVC、PV的设计，也使得StatefulSet对存储状态的管理成为了可能。我们还是以上一篇文章中用到的StatefulSet为例（你也可以借此再回顾一下 [《深入理解StatefulSet（一）：拓扑状态》](https://time.geekbang.org/column/article/41017) 中的相关内容）：

```
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.9.1
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi

```

这次，我们为这个StatefulSet额外添加了一个volumeClaimTemplates字段。从名字就可以看出来，它跟Deployment里Pod模板（PodTemplate）的作用类似。也就是说，凡是被这个StatefulSet管理的Pod，都会声明一个对应的PVC；而这个PVC的定义，就来自于volumeClaimTemplates这个模板字段。更重要的是，这个PVC的名字，会被分配一个与这个Pod完全一致的编号。

这个自动创建的PVC，与PV绑定成功后，就会进入Bound状态，这就意味着这个Pod可以挂载并使用这个PV了。

如果你还是不太理解PVC的话，可以先记住这样一个结论： **PVC其实就是一种特殊的Volume**。只不过一个PVC具体是什么类型的Volume，要在跟某个PV绑定之后才知道。关于PV、PVC更详细的知识，我会在容器存储部分做进一步解读。

当然，PVC与PV的绑定得以实现的前提是，运维人员已经在系统里创建好了符合条件的PV（比如，我们在前面用到的pv-volume）；或者，你的Kubernetes集群运行在公有云上，这样Kubernetes就会通过Dynamic Provisioning的方式，自动为你创建与PVC匹配的PV。

所以，我们在使用kubectl create创建了StatefulSet之后，就会看到Kubernetes集群里出现了两个PVC：

```
$ kubectl create -f statefulset.yaml
$ kubectl get pvc -l app=nginx
NAME        STATUS    VOLUME                                     CAPACITY   ACCESSMODES   AGE
www-web-0   Bound     pvc-15c268c7-b507-11e6-932f-42010a800002   1Gi        RWO           48s
www-web-1   Bound     pvc-15c79307-b507-11e6-932f-42010a800002   1Gi        RWO           48s

```

可以看到，这些PVC，都以“<PVC名字>-<StatefulSet名字>-<编号>”的方式命名，并且处于Bound状态。

我们前面已经讲到过，这个StatefulSet创建出来的所有Pod，都会声明使用编号的PVC。比如，在名叫web-0的Pod的volumes字段，它会声明使用名叫www-web-0的PVC，从而挂载到这个PVC所绑定的PV。

所以，我们就可以使用如下所示的指令，在Pod的Volume目录里写入一个文件，来验证一下上述Volume的分配情况：

```
$ for i in 0 1; do kubectl exec web-$i -- sh -c 'echo hello $(hostname) > /usr/share/nginx/html/index.html'; done

```

如上所示，通过kubectl exec指令，我们在每个Pod的Volume目录里，写入了一个index.html文件。这个文件的内容，正是Pod的hostname。比如，我们在web-0的index.html里写入的内容就是"hello web-0"。

此时，如果你在这个Pod容器里访问 `“http://localhost”`，你实际访问到的就是Pod里Nginx服务器进程，而它会为你返回/usr/share/nginx/html/index.html里的内容。这个操作的执行方法如下所示：

```
$ for i in 0 1; do kubectl exec -it web-$i -- curl localhost; done
hello web-0
hello web-1

```

现在，关键来了。

如果你使用kubectl delete命令删除这两个Pod，这些Volume里的文件会不会丢失呢？

```
$ kubectl delete pod -l app=nginx
pod "web-0" deleted
pod "web-1" deleted

```

可以看到，正如我们前面介绍过的，在被删除之后，这两个Pod会被按照编号的顺序被重新创建出来。而这时候，如果你在新创建的容器里通过访问 `“http://localhost”` 的方式去访问web-0里的Nginx服务：

```
# 在被重新创建出来的Pod容器里访问http://localhost
$ kubectl exec -it web-0 -- curl localhost
hello web-0

```

就会发现，这个请求依然会返回：hello web-0。也就是说，原先与名叫web-0的Pod绑定的PV，在这个Pod被重新创建之后，依然同新的名叫web-0的Pod绑定在了一起。对于Pod web-1来说，也是完全一样的情况。

**这是怎么做到的呢？**

其实，我和你分析一下StatefulSet控制器恢复这个Pod的过程，你就可以很容易理解了。

首先，当你把一个Pod，比如web-0，删除之后，这个Pod对应的PVC和PV，并不会被删除，而这个Volume里已经写入的数据，也依然会保存在远程存储服务里（比如，我们在这个例子里用到的Ceph服务器）。

此时，StatefulSet控制器发现，一个名叫web-0的Pod消失了。所以，控制器就会重新创建一个新的、名字还是叫作web-0的Pod来，“纠正”这个不一致的情况。

需要注意的是，在这个新的Pod对象的定义里，它声明使用的PVC的名字，还是叫作：www-web-0。这个PVC的定义，还是来自于PVC模板（volumeClaimTemplates），这是StatefulSet创建Pod的标准流程。

所以，在这个新的web-0 Pod被创建出来之后，Kubernetes为它查找名叫www-web-0的PVC时，就会直接找到旧Pod遗留下来的同名的PVC，进而找到跟这个PVC绑定在一起的PV。

这样，新的Pod就可以挂载到旧Pod对应的那个Volume，并且获取到保存在Volume里的数据。

**通过这种方式，Kubernetes的StatefulSet就实现了对应用存储状态的管理。**

看到这里，你是不是已经大致理解了StatefulSet的工作原理呢？现在，我再为你详细梳理一下吧。

**首先，StatefulSet的控制器直接管理的是Pod**。这是因为，StatefulSet里的不同Pod实例，不再像ReplicaSet中那样都是完全一样的，而是有了细微区别的。比如，每个Pod的hostname、名字等都是不同的、携带了编号的。而StatefulSet区分这些实例的方式，就是通过在Pod的名字里加上事先约定好的编号。

**其次，Kubernetes通过Headless Service，为这些有编号的Pod，在DNS服务器中生成带有同样编号的DNS记录**。只要StatefulSet能够保证这些Pod名字里的编号不变，那么Service里类似于web-0.nginx.default.svc.cluster.local这样的DNS记录也就不会变，而这条记录解析出来的Pod的IP地址，则会随着后端Pod的删除和再创建而自动更新。这当然是Service机制本身的能力，不需要StatefulSet操心。

**最后，StatefulSet还为每一个Pod分配并创建一个同样编号的PVC**。这样，Kubernetes就可以通过Persistent Volume机制为这个PVC绑定上对应的PV，从而保证了每一个Pod都拥有一个独立的Volume。

在这种情况下，即使Pod被删除，它所对应的PVC和PV依然会保留下来。所以当这个Pod被重新创建出来之后，Kubernetes会为它找到同样编号的PVC，挂载这个PVC对应的Volume，从而获取到以前保存在Volume里的数据。

这么一看，原本非常复杂的StatefulSet，是不是也很容易理解了呢？

## 总结

在今天这篇文章中，我为你详细介绍了StatefulSet处理存储状态的方法。然后，以此为基础，我为你梳理了StatefulSet控制器的工作原理。

从这些讲述中，我们不难看出StatefulSet的设计思想：StatefulSet其实就是一种特殊的Deployment，而其独特之处在于，它的每个Pod都被编号了。而且，这个编号会体现在Pod的名字和hostname等标识信息上，这不仅代表了Pod的创建顺序，也是Pod的重要网络标识（即：在整个集群里唯一的、可被访问的身份）。

有了这个编号后，StatefulSet就使用Kubernetes里的两个标准功能：Headless Service和PV/PVC，实现了对Pod的拓扑状态和存储状态的维护。

实际上，在下一篇文章的“有状态应用”实践环节，以及后续的讲解中，你就会逐渐意识到，StatefulSet可以说是Kubernetes中作业编排的“集大成者”。

因为，几乎每一种Kubernetes的编排功能，都可以在编写StatefulSet的YAML文件时被用到。

## 思考题

在实际场景中，有一些分布式应用的集群是这么工作的：当一个新节点加入到集群时，或者老节点被迁移后重建时，这个节点可以从主节点或者其他从节点那里同步到自己所需要的数据。

在这种情况下，你认为是否还有必要将这个节点Pod与它的PV进行一对一绑定呢？（提示：这个问题的答案根据不同的项目是不同的。关键在于，重建后的节点进行数据恢复和同步的时候，是不是一定需要原先它写在本地磁盘里的数据）

感谢你的收听，欢迎你给我留言，也欢迎分享给更多的朋友一起阅读。