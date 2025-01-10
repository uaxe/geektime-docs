你好，我是张磊。今天我和你分享的主题是：深入解析Pod对象之基本概念。

在上一篇文章中，我详细介绍了Pod这个Kubernetes项目中最重要的概念。而在今天这篇文章中，我会和你分享Pod对象的更多细节。

现在，你已经非常清楚：Pod，而不是容器，才是Kubernetes项目中的最小编排单位。将这个设计落实到API对象上，容器（Container）就成了Pod属性里的一个普通的字段。那么，一个很自然的问题就是：到底哪些属性属于Pod对象，而又有哪些属性属于Container呢？

要彻底理解这个问题，你就一定要牢记我在上一篇文章中提到的一个结论：Pod扮演的是传统部署环境里“虚拟机”的角色。这样的设计，是为了使用户从传统环境（虚拟机环境）向Kubernetes（容器环境）的迁移，更加平滑。

而如果你能把Pod看成传统环境里的“机器”、把容器看作是运行在这个“机器”里的“用户程序”，那么很多关于Pod对象的设计就非常容易理解了。

比如， **凡是调度、网络、存储，以及安全相关的属性，基本上是Pod 级别的。**

这些属性的共同特征是，它们描述的是“机器”这个整体，而不是里面运行的“程序”。比如，配置这个“机器”的网卡（即：Pod的网络定义），配置这个“机器”的磁盘（即：Pod的存储定义），配置这个“机器”的防火墙（即：Pod的安全定义）。更不用说，这台“机器”运行在哪个服务器之上（即：Pod的调度）。

接下来，我就先为你介绍Pod中几个重要字段的含义和用法。

**NodeSelector：是一个供用户将Pod与Node进行绑定的字段**，用法如下所示：

```
apiVersion: v1
kind: Pod
...
spec:
 nodeSelector:
   disktype: ssd

```

这样的一个配置，意味着这个Pod永远只能运行在携带了“disktype: ssd”标签（Label）的节点上；否则，它将调度失败。

**NodeName**：一旦Pod的这个字段被赋值，Kubernetes项目就会被认为这个Pod已经经过了调度，调度的结果就是赋值的节点名字。所以，这个字段一般由调度器负责设置，但用户也可以设置它来“骗过”调度器，当然这个做法一般是在测试或者调试的时候才会用到。

**HostAliases：定义了Pod的hosts文件（比如/etc/hosts）里的内容**，用法如下：

```
apiVersion: v1
kind: Pod
...
spec:
  hostAliases:
  - ip: "10.1.2.3"
    hostnames:
    - "foo.remote"
    - "bar.remote"
...

```

在这个Pod的YAML文件中，我设置了一组IP和hostname的数据。这样，这个Pod启动后，/etc/hosts文件的内容将如下所示：

```
cat /etc/hosts
# Kubernetes-managed hosts file.
127.0.0.1 localhost
...
10.244.135.10 hostaliases-pod
10.1.2.3 foo.remote
10.1.2.3 bar.remote

```

其中，最下面两行记录，就是我通过HostAliases字段为Pod设置的。需要指出的是，在Kubernetes项目中，如果要设置hosts文件里的内容，一定要通过这种方法。否则，如果直接修改了hosts文件的话，在Pod被删除重建之后，kubelet会自动覆盖掉被修改的内容。

除了上述跟“机器”相关的配置外，你可能也会发现， **凡是跟容器的Linux Namespace相关的属性，也一定是Pod 级别的**。这个原因也很容易理解：Pod的设计，就是要让它里面的容器尽可能多地共享Linux Namespace，仅保留必要的隔离和限制能力。这样，Pod模拟出的效果，就跟虚拟机里程序间的关系非常类似了。

举个例子，在下面这个Pod的YAML文件中，我定义了shareProcessNamespace=true：

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  shareProcessNamespace: true
  containers:
  - name: nginx
    image: nginx
  - name: shell
    image: busybox
    stdin: true
    tty: true

```

这就意味着这个Pod里的容器要共享PID Namespace。

而在这个YAML文件中，我还定义了两个容器：一个是nginx容器，一个是开启了tty和stdin的shell容器。

我在前面介绍容器基础时，曾经讲解过什么是tty和stdin。而在Pod的YAML文件里声明开启它们俩，其实等同于设置了docker run里的-it（-i即stdin，-t即tty）参数。

如果你还是不太理解它们俩的作用的话，可以直接认为tty就是Linux给用户提供的一个常驻小程序，用于接收用户的标准输入，返回操作系统的标准输出。当然，为了能够在tty中输入信息，你还需要同时开启stdin（标准输入流）。

于是，这个Pod被创建后，你就可以使用shell容器的tty跟这个容器进行交互了。我们一起实践一下：

```
$ kubectl create -f nginx.yaml

```

接下来，我们使用kubectl attach命令，连接到shell容器的tty上：

```
$ kubectl attach -it nginx -c shell

```

这样，我们就可以在shell容器里执行ps指令，查看所有正在运行的进程：

```
$ kubectl attach -it nginx -c shell
/ # ps ax
PID   USER     TIME  COMMAND
    1 root      0:00 /pause
    8 root      0:00 nginx: master process nginx -g daemon off;
   14 101       0:00 nginx: worker process
   15 root      0:00 sh
   21 root      0:00 ps ax

```

可以看到，在这个容器里，我们不仅可以看到它本身的ps ax指令，还可以看到nginx容器的进程，以及Infra容器的/pause进程。这就意味着，整个Pod里的每个容器的进程，对于所有容器来说都是可见的：它们共享了同一个PID Namespace。

类似地， **凡是Pod中的容器要共享宿主机的Namespace，也一定是Pod级别的定义**，比如：

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  hostNetwork: true
  hostIPC: true
  hostPID: true
  containers:
  - name: nginx
    image: nginx
  - name: shell
    image: busybox
    stdin: true
    tty: true

```

在这个Pod中，我定义了共享宿主机的Network、IPC和PID Namespace。这就意味着，这个Pod里的所有容器，会直接使用宿主机的网络、直接与宿主机进行IPC通信、看到宿主机里正在运行的所有进程。

当然，除了这些属性，Pod里最重要的字段当属“Containers”了。而在上一篇文章中，我还介绍过“Init Containers”。其实，这两个字段都属于Pod对容器的定义，内容也完全相同，只是Init Containers的生命周期，会先于所有的Containers，并且严格按照定义的顺序执行。

Kubernetes项目中对Container的定义，和Docker相比并没有什么太大区别。我在前面的容器技术概念入门系列文章中，和你分享的Image（镜像）、Command（启动命令）、workingDir（容器的工作目录）、Ports（容器要开发的端口），以及volumeMounts（容器要挂载的Volume）都是构成Kubernetes项目中Container的主要字段。不过在这里，还有这么几个属性值得你额外关注。

**首先，是ImagePullPolicy字段**。它定义了镜像拉取的策略。而它之所以是一个Container级别的属性，是因为容器镜像本来就是Container定义中的一部分。

ImagePullPolicy的值默认是Always，即每次创建Pod都重新拉取一次镜像。另外，当容器的镜像是类似于nginx或者nginx:latest这样的名字时，ImagePullPolicy也会被认为Always。

而如果它的值被定义为Never或者IfNotPresent，则意味着Pod永远不会主动拉取这个镜像，或者只在宿主机上不存在这个镜像时才拉取。

**其次，是Lifecycle字段**。它定义的是Container Lifecycle Hooks。顾名思义，Container Lifecycle Hooks的作用，是在容器状态发生变化时触发一系列“钩子”。我们来看这样一个例子：

```
apiVersion: v1
kind: Pod
metadata:
  name: lifecycle-demo
spec:
  containers:
  - name: lifecycle-demo-container
    image: nginx
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c", "echo Hello from the postStart handler > /usr/share/message"]
      preStop:
        exec:
          command: ["/usr/sbin/nginx","-s","quit"]

```

这是一个来自Kubernetes官方文档的Pod的YAML文件。它其实非常简单，只是定义了一个nginx镜像的容器。不过，在这个YAML文件的容器（Containers）部分，你会看到这个容器分别设置了一个postStart和preStop参数。这是什么意思呢？

先说postStart吧。它指的是，在容器启动后，立刻执行一个指定的操作。需要明确的是，postStart定义的操作，虽然是在Docker容器ENTRYPOINT执行之后，但它并不严格保证顺序。也就是说，在postStart启动时，ENTRYPOINT有可能还没有结束。

当然，如果postStart执行超时或者错误，Kubernetes会在该Pod的Events中报出该容器启动失败的错误信息，导致Pod也处于失败的状态。

而类似地，preStop发生的时机，则是容器被杀死之前（比如，收到了SIGKILL信号）。而需要明确的是，preStop操作的执行，是同步的。所以，它会阻塞当前的容器杀死流程，直到这个Hook定义操作完成之后，才允许容器被杀死，这跟postStart不一样。

所以，在这个例子中，我们在容器成功启动之后，在/usr/share/message里写入了一句“欢迎信息”（即postStart定义的操作）。而在这个容器被删除之前，我们则先调用了nginx的退出指令（即preStop定义的操作），从而实现了容器的“优雅退出”。

在熟悉了Pod以及它的Container部分的主要字段之后，我再和你分享一下 **这样一个的Pod对象在Kubernetes中的生命周期**。

Pod生命周期的变化，主要体现在Pod API对象的 **Status部分**，这是它除了Metadata和Spec之外的第三个重要字段。其中，pod.status.phase，就是Pod的当前状态，它有如下几种可能的情况：

1. Pending。这个状态意味着，Pod的YAML文件已经提交给了Kubernetes，API对象已经被创建并保存在Etcd当中。但是，这个Pod里有些容器因为某种原因而不能被顺利创建。比如，调度不成功。

2. Running。这个状态下，Pod已经调度成功，跟一个具体的节点绑定。它包含的容器都已经创建成功，并且至少有一个正在运行中。

3. Succeeded。这个状态意味着，Pod里的所有容器都正常运行完毕，并且已经退出了。这种情况在运行一次性任务时最为常见。

4. Failed。这个状态下，Pod里至少有一个容器以不正常的状态（非0的返回码）退出。这个状态的出现，意味着你得想办法Debug这个容器的应用，比如查看Pod的Events和日志。

5. Unknown。这是一个异常状态，意味着Pod的状态不能持续地被kubelet汇报给kube-apiserver，这很有可能是主从节点（Master和Kubelet）间的通信出现了问题。


更进一步地，Pod对象的Status字段，还可以再细分出一组Conditions。这些细分状态的值包括：PodScheduled、Ready、Initialized，以及Unschedulable。它们主要用于描述造成当前Status的具体原因是什么。

比如，Pod当前的Status是Pending，对应的Condition是Unschedulable，这就意味着它的调度出现了问题。

而其中，Ready这个细分状态非常值得我们关注：它意味着Pod不仅已经正常启动（Running状态），而且已经可以对外提供服务了。这两者之间（Running和Ready）是有区别的，你不妨仔细思考一下。

Pod的这些状态信息，是我们判断应用运行情况的重要标准，尤其是Pod进入了非“Running”状态后，你一定要能迅速做出反应，根据它所代表的异常情况开始跟踪和定位，而不是去手忙脚乱地查阅文档。

## 总结

在今天这篇文章中，我详细讲解了Pod API对象，介绍了Pod的核心使用方法，并分析了Pod和Container在字段上的异同。希望这些讲解能够帮你更好地理解和记忆Pod YAML中的核心字段，以及这些字段的准确含义。

实际上，Pod API对象是整个Kubernetes体系中最核心的一个概念，也是后面我讲解各种控制器时都要用到的。

在学习完这篇文章后，我希望你能仔细阅读$GOPATH/src/k8s.io/kubernetes/vendor/k8s.io/api/core/v1/types.go里，type Pod struct ，尤其是PodSpec部分的内容。争取做到下次看到一个Pod的YAML文件时，不再需要查阅文档，就能做到把常用字段及其作用信手拈来。

而在下一篇文章中，我会通过大量的实践，帮助你巩固和进阶关于Pod API对象核心字段的使用方法，敬请期待吧。

## 思考题

你能否举出一些Pod（即容器）的状态是Running，但是应用其实已经停止服务的例子？相信Java Web开发者的亲身体会会比较多吧。

感谢你的收听，欢迎你给我留言，也欢迎分享给更多的朋友一起阅读。