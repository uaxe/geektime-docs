你好，我是雪飞。

上一课我们学习了 YAML 文件的相关知识，同时动手编写了 YAML 文件，现在你就可以使用 YAML 文件来与 K8s 集群沟通，从而实现应用部署和集群管理的需求。在接下来的课程中，我将继续深入介绍 K8s 中常用的资源对象，这些资源对象提供了应用部署、参数配置、网络访问、持久化存储、安全策略等等功能，满足各种实际的应用场景。对于 K8s 资源对象的管理，我会同时使用 kubectl 命令和 YAML 文件这两种方式来加深你的理解和记忆。

今天，我给你讲一下 K8s 中最核心的资源对象——Pod，它是 K8s 管理的最小可部署资源对象。其他很多资源对象都是基于 Pod 来实现更复杂的应用部署和管理。例如，Deployment 就是通过管理多个 Pod 来实现应用的高可用性和滚动更新。接下来，让我们详细了解一下什么是 Pod。

## 认识 Pod

Pod 的中文意思为豌豆荚，因为 Pod 中包含了一个或多个容器，容器和 Pod 的关系很像豌豆和豆荚的关系，所以这就是 Pod 名称的来历。在 K8s 中，Pod 是一个逻辑概念，而容器才是运行着应用镜像的实际载体，那为啥 K8s 不直接管理容器，而是还要搞出一个 Pod 呢？

![图片](https://static001.geekbang.org/resource/image/a9/04/a9059aeyyc92yyffbc54897809a49e04.jpg?wh=300x205)

最重要的原因就是：在一些常见的应用场景下，容器并不是孤零零的存在，它可能会跟其他容器之间有着很亲密的关系，它们相互协作，一起启动，一起停止，一起提供服务，同时它们需要彼此间可以方便的通信以及访问相同的数据。所以 K8s 就在容器的基础上创建了 Pod 这个更高层级的资源对象，Pod 可以将多个容器组合到一起部署和管理，同一 Pod 中的容器可以共享网络和存储空间，这种机制保证了对容器管理的一致性和灵活性。

举个具体例子， Pod 中多容器常用于边车模式（Sidecar），这种模式包含主容器和辅助容器，主容器运行核心业务应用，而辅助容器则负责日志收集、监控等任务，在不影响主业务的情况下扩展了应用功能。这种关系类似三轮摩托车，在摩托车的一侧加装一个边车来增加额外的空间，所以被叫做边车模式。此外，新一代 Service Mesh（服务网格）技术也利用了这种边车模式来增强服务间的通信和管理能力。

![](https://static001.geekbang.org/resource/image/51/6e/51309a427a528f3644ea54de17108a6e.jpg?wh=1190x466)

在实际应用中，Pod 可以包含一个容器也可以包含多个容器，非常灵活。对于多个容器，Pod 实现了容器间共享网络和存储空间的机制，下面我们来看下 Pod 是如何实现这两种机制。

### 共享网络

首先，让我们讨论一下 Pod 中容器共享网络的机制。K8s 使用了一种简单的方式来实现共享网络，那就是在 Pod 中的容器启动之前，先自动运行一个 Infra Container（基础容器），这个容器运行了一个非常小的镜像，大概几百 KB，是一个 C 语言写的永远处于 pause（暂停）状态的容器，又叫 pause 容器。然后，当 Pod 中的其他容器启动时，它们都会加入到 Infra Container 的网络中，从而使用 Infra Container 的网络中的网络设备、IP 地址等网络相关的信息，这样就实现了容器之间共享网络。这有点像是一个电脑上同时有两个网络应用，它们都是用这个电脑的同一块网卡来处理网络请求，所以通过 localhost 也就能相互访问。

![](https://static001.geekbang.org/resource/image/3d/5d/3dc9921ef04eda18ed56b268yy5c8c5d.jpg?wh=1030x520)

### 共享存储

接下来，我们再看一下 Pod 中多个容器共享存储，Pod 是通过多个容器挂载共同的数据卷 Volume（数据卷）来实现共享存储的。你可以把数据卷想象成一个共享网盘，Pod 中的容器都可以通过它来存取文件。例如之前说到的边车模式，主容器可以将日志文件写到共享存储空间，然后边车容器可以直接读取共享存储空间的文件来获取日志信息，从而实现业务功能和统计分析功能的分离，就像两个同事共用一个文件夹一样方便。这样，不仅能让各个容器各司其职，还能让整个系统更加灵活和易于管理。

![](https://static001.geekbang.org/resource/image/68/1e/6829b76c9fccfa89ac36154c7499e11e.jpg?wh=1004x546)

### **部署一个多容器的 Pod**

了解了 Pod 的共享原理，下面我们就动手部署一个多容器的 Pod，来验证一下容器间的共享网络和共享存储。部署多容器的 Pod 是 CKA 考试的核心考点，考试中需要用 YAML 文件的方式部署 Pod，所以你要了解这个 YAML 文件的写法。

首先，编写一个包含两个容器的 Pod 的 YAML 文件（two\_container\_pod.yaml），其中一个是 Web 服务应用 Nginx，另一个是 Busybox。Busybox 是一个工具镜像，其中包含了 Linux 系统命令行工具，在Busybox容器启动的时候执行了一条 sleep 休眠命令，用于保持容器持续运行。

**注意：** 课程中的例子我都放到了公开的 [GitHub 仓库](https://github.com/wwwangxuefei/cka.git) 中供你参考，你可以使用 Git 工具把仓库拉到本地查看示例。

我在 Pod 的 spec 属性里创建了一个名为 data 的本地临时 Volume（数据卷类型是 emptyDir），同时在 Pod 的每个容器中都挂载了这个 Volume。

```yaml
# two_container_pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: test
spec:
  containers:
  - image: nginx
    name: nginx
    volumeMounts:   # 容器 Nginx 挂载 Volume
    - name: data
      mountPath: /data
  - image: busybox
    name: busybox
    command: ["/bin/sh","-c","sleep 3600"]
    volumeMounts:   # 容器 Busybox 挂载 Volume
    - name: data
      mountPath: /data
  volumes:          # 定义了一个临时 Volume
  - name: data
    emptyDir: {}

```

然后运行以下命令部署 YAML 文件，等待 Pod 运行成功。

```bash
[root@k8s-master ~]# kubectl apply -f two_container_pod.yaml
pod/test created

```

通过 “kubectl get pod -o wide” 命令，可以查看 Pod 部署的详细列表信息。此时，可以看到 Pod 已经成功部署到了 k8s-worker1 节点上。

```bash
[root@k8s-master ~]# kubectl get pod -o wide
NAME  READY  STATUS    RESTARTS   AGE   IP              NODE          NOMINATED NODE   READINESS GATES
test  2/2    Running   0          92s   10.244.194.68   k8s-worker1   <none>           <none>

```

**1\. 验证共享网络**

我们远程登录到 k8s-worker1 节点上，并使用 “docker ps” 命令查看节点上正在运行的容器。通过这种方式，我们可以确认在 k8s-worker1 节点上运行着 pause 容器，也就是提供共享网络的 Infra Container。

```bash
[root@k8s-worker1 ~]# docker ps | grep test
aab5e75d353f   busybox                                              "/bin/sh -c 'sleep 3…"   5 minutes ago       Up 5 minutes                 k8s_busybox_test_default_e20592c1-79fa-41f7-9f1a-f79e851db4dc_0
87a6c4de517d   nginx                                                "/docker-entrypoint.…"   6 minutes ago       Up 5 minutes                 k8s_nginx_test_default_e20592c1-79fa-41f7-9f1a-f79e851db4dc_0
438f772319e5   registry.aliyuncs.com/google_containers/pause:3.9    "/pause"                 6 minutes ago       Up 6 minutes                 k8s_POD_test_default_e20592c1-79fa-41f7-9f1a-f79e851db4dc_0

```

回到 Master 节点上，我们使用 “kubectl exec -it” 命令进入 Busybox 容器内部。

```bash
kubectl exec -it test -c busybox -- sh

```

- **-it：** 表示使用终端应用作为访问容器的标准输入。
- **-c：** 表示要进入的容器名称，如果 Pod 里只有一个容器，就不需要这个参数。
- **\-\- sh：** 表示进入容器之后打开 shell 终端应用。

Nginx 容器部署成功后，就会启动了一个 Web 服务，访问 Nginx 容器的 80 端口，就可以访问到它的默认 “index.html” 文件。所以我们在 Busybox 容器的终端应用中，使用 wget 命令来请求本地网络地址 Localhost 的 80 端口，这个命令通常用来远程获取文件，可以看到 wget 命令获取到了 Nginx 容器的 80 端口返回的 “index.html” 文件，这证明了两个容器共享同一个网络空间，并且可以通过 Localhost 地址互相通信。

```bash
[root@k8s-master ~]# kubectl exec -it test -c busybox -- sh
/ # wget localhost:80
Connecting to localhost:80 (127.0.0.1:80)
saving to 'index.html'
index.html    100% |****************************|   615  0:00:00 ETA
'index.html' saved

```

**2\. 验证共享存储**

我们继续在 Busybox 容器内，进入到 “/data” 目录，这个就是容器挂载数据卷的目录，在这个目录内创建一个内容为 “Hello, I am Busybox” 的文本文件（hello.txt）。

```bash
/ # cd /data
/ # echo "Hello, I am Busybox" > hello.txt

```

然后退出 Busybox 容器。只需输入 exit 命令，就可以回到集群 Master 节点的终端。

```bash
/ # exit
[root@k8s-master ~]#

```

这时，我们已经在共享存储空间中创建了一个文件，现在就要去 Nginx 容器中去看看是否能找到这个文件。使用 “kubectl exec -it” 命令进入到 Nginx 容器内部，然后通过 “cat” 命令直接查看 “/data/hello.txt” 文件内容。

```bash
[root@k8s-master ~]# kubectl exec -it test -c nginx -- sh
/ # cat /data/hello.txt
Hello, I am Busybox

```

此时可以看到，在 Nginx 容器挂载的 “/data” 目录下，已经可以读取到在 Busybox 容器中创建的 “/data/hello.txt” 文件内容了。这证明了同一个 Pod 下的多个容器通过挂载相同的数据卷 Volume 实现了共享存储空间。

## 使用 kubectl 命令管理 Pod

刚才我们用 YAML 文件的方式来创建了多容器的 Pod，然而通过 kubectl 命令是不能直接创建多容器的 Pod，它只能创建单容器的简单 Pod，所以我们也可以看出使用 kubectl 命令与 YAML 文件的一个区别，YAML 文件更适合实现复杂的部署要求。

现在我们就来学习如何使用 Kubectl 命令来管理 Pod。

### 创建 Pod

使用 “kubectl run” 命令可以快速创建一个简单的 Pod，命令后面可以根据不同的容器镜像应用类型而增加不同参数。

```bash
kubectl run <pod名称> --image=nginx [--port=80]
kubectl run <pod名称> --image=busybox [-- sleep 3600]

```

- **<pod名称>**：这是新创建的 Pod 的名称。
- **–image=nginx**：指定 Pod 使用的容器镜像是 nginx。
- **–port=80**：设置容器暴露的端口为 80，对于 Web 类型应用，外部请求会通过该端口号访问到容器。如果不需要端口访问，也可以不用该参数。
- **– sleep 3600**：–参数可以指定容器启动时要执行的命令，这里是执行 “sleep 3600” 命令，也就是让 Busybox 容器保持运行3600秒。如果容器启动时不需要执行命令，也可以不用该参数。

### 查看 Pod

使用 “kubectl get pod” 命令可以查看 Pod 列表信息，由于 Pod 的缩写（SHORTNAMES）是 po，也可以在命令中使用 po 代替 pod。命令后面可以根据需要增加不同参数。

```bash
kubectl get pod
kubectl get pod [-o wide] [-n <namespace名称>]
kubectl get pod <pod名称> [-o yaml]

```

- **-o wide：** 用来查看到更多的 Pod 信息，例如 Pod 的 IP 地址、部署所在节点等等。
- **-n <namespace名称>：**-n 参数可以指定命名空间名称，命名空间是对资源对象的一种逻辑分组隔离方式，Pod 可以创建到不同的命名空间下，这时就需要增加 -n 参数来指定 Pod 所在的命名空间，不加 -n 参数则是查看默认命名空间（default）下的 Pod。
- **-o yaml：** 用来以 YAML 文件的方式查看指定的 Pod。

使用 “kubectl describe pod” 命令可以查看 Pod 的详细信息。如果 Pod 不在默认命名空间，需要使用 “-n” 参数指定 Pod 所在的命名空间。

```bash
kubectl describe pod <pod名称> [-n <namespace名称>]

```

命令返回结果（返回信息太多，我用 “…” 做了省略）中看到的 Pod 信息非常丰富，包括基础信息、容器信息、状态信息、挂载存储卷信息、调度策略信息、事件信息等等。这些数据对 Pod 的故障排查非常有用，后续我们也会经常使用。

```bash
[root@k8s-master ~]# kubectl describe pod test
Name:             test
Namespace:        default
......
Containers:
  nginx:
......
Conditions:
  Type              Status
  Initialized       True
......
Volumes:
  data:
......
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  56s   default-scheduler  Successfully assigned default/test to k8s-worker1
  Normal  Pulling    55s   kubelet            Pulling image "nginx"

```

### 其他命令

管理 Pod 的其他命令参考以下小卡片，有些命令已经出现过很多次，相信你已经很熟悉了。如果 Pod 不在默认命名空间（default），这些命令都需要使用 “-n” 参数指定 Pod 所在的命名空间，否则会提示 Pod 没找到。

```bash
删除 Pod：kubectl delete pod <pod名称>
编辑 Pod，修改 YAML 文件后自动生效：kubectl edit pod <pod名称>
进入 Pod 内部：kubectl exec -it <pod名称> -- sh
查看 Pod 日志：kubectl logs <pod名称>

```

了解了 Pod 的共享机制和相关命令，我们对 Pod 已经有了一个全面的认识。最后我再给你讲一种特殊的 Pod —— 静态 Pod。

## 静态 Pod

在 K8s 中，静态 Pod 是一种非常特殊的 Pod，它的 YAML 文件就直接存放在集群各节点的指定目录位置（“/etc/kubernetes/manifests”），静态 Pod 会自动部署，而不是通过 K8s 的 API Server 创建。静态 Pod 通常用于部署集群级别的系统组件，如 K8s 集群自己的很多系统组件就是静态 Pod，这些组件需要在集群启动时就可用，并且可以随着节点重启而自动重启。对于静态 Pod 的任何更新都需要管理员手动修改它的 YAML 文件并重启 Pod。

创建静态 Pod 不需要使用任何命令，只需要把 Pod 的 YAML 文件放到该节点的“/etc/kubernetes/manifests” 目录下，节点的 kubelet 组件就会自动创建静态 Pod。其实集群搭建的时候我们已经部署了一些静态 Pod，我们就去看一下吧。

```bash
[root@k8s-master ~]# cd /etc/kubernetes/manifests/
[root@k8s-master manifests]# ls
etcd.yaml  kube-apiserver.yaml  kube-controller-manager.yaml  kube-scheduler.yaml

```

在管理节点上的 manifests 目录中，可以看到 etcd、kube-apiserver、kube-controller-manager、kube-scheduler 这些 K8s 组件就是以静态 Pod 的方式部署到集群 kube-system 的命名空间下。

## **小结**

今天，我重点介绍了 K8s 中的核心资源对象——Pod。在 K8s 中，Pod 是容器管理的基本单位，每个 Pod 可以包含一个或多个容器，这些容器通过 Infra Container（基础容器）共享网络，同时通过挂载相同的数据卷 Volume 来实现共享存储，这两种机制保证了 Pod 对容器管理的一致性和灵活性，简化了对容器的管理。

接着，我带你使用 YAML 文件的方式部署了一个包含两个容器的 Pod ，并且验证了 Pod 的共享网络和共享存储的机制。部署多容器 Pod 是 CKA 的考点，你一定要熟悉它的 YAML 文件的写法。你也需要熟悉 Pod 相关的 kubectl 命令，特别是创建 Pod 使用的 “kubectl run” 命令，以及查看 Pod 信息使用的 “kubectl get pod” 和 “kubectl describe pod” 命令。

最后，我介绍了静态 Pod。静态 Pod 是一种通过节点上指定目录（“/etc/kubernetes/manifests”）中的 YAML 文件自动部署的特殊 Pod，在集群启动时就可用，并且可以随着节点重启而自动重启，通常用于部署集群级别的系统组件，K8s 的组件就是以静态 Pod 的方式运行。创建静态 Pod 只需要把 Pod 的 YAML 文件放到该节点的指定目录下，节点的 kubelet 组件就会自动创建静态 Pod。

## 思考题

这就是今天的全部内容，这节课通常会有一个考点，就是给 Pod 配置多个容器，所以最后留两道练习题给你。

1. 创建一个 Pod，其中运行着 Nginx、Redis、Memcache 3 个容器。
2. 在节点 k8s-worker1 中运行一个 Nginx 的静态 Pod。

相信经过动手实践，会让你对知识的理解更加深刻。