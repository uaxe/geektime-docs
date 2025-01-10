你好，我是张磊。今天我和你分享的主题是：深入理解StatefulSet之拓扑状态。

在上一篇文章中，我在结尾处讨论到了Deployment实际上并不足以覆盖所有的应用编排问题。

造成这个问题的根本原因，在于Deployment对应用做了一个简单化假设。

它认为，一个应用的所有Pod，是完全一样的。所以，它们互相之间没有顺序，也无所谓运行在哪台宿主机上。需要的时候，Deployment就可以通过Pod模板创建新的Pod；不需要的时候，Deployment就可以“杀掉”任意一个Pod。

但是，在实际的场景中，并不是所有的应用都可以满足这样的要求。

尤其是分布式应用，它的多个实例之间，往往有依赖关系，比如：主从关系、主备关系。

还有就是数据存储类应用，它的多个实例，往往都会在本地磁盘上保存一份数据。而这些实例一旦被杀掉，即便重建出来，实例与数据之间的对应关系也已经丢失，从而导致应用失败。

所以，这种实例之间有不对等关系，以及实例对外部数据有依赖关系的应用，就被称为“有状态应用”（Stateful Application）。

容器技术诞生后，大家很快发现，它用来封装“无状态应用”（Stateless Application），尤其是Web服务，非常好用。但是，一旦你想要用容器运行“有状态应用”，其困难程度就会直线上升。而且，这个问题解决起来，单纯依靠容器技术本身已经无能为力，这也就导致了很长一段时间内，“有状态应用”几乎成了容器技术圈子的“忌讳”，大家一听到这个词，就纷纷摇头。

不过，Kubernetes项目还是成为了“第一个吃螃蟹的人”。

得益于“控制器模式”的设计思想，Kubernetes项目很早就在Deployment的基础上，扩展出了对“有状态应用”的初步支持。这个编排功能，就是：StatefulSet。

StatefulSet的设计其实非常容易理解。它把真实世界里的应用状态，抽象为了两种情况：

1. **拓扑状态**。这种情况意味着，应用的多个实例之间不是完全对等的关系。这些应用实例，必须按照某些顺序启动，比如应用的主节点A要先于从节点B启动。而如果你把A和B两个Pod删除掉，它们再次被创建出来时也必须严格按照这个顺序才行。并且，新创建出来的Pod，必须和原来Pod的网络标识一样，这样原先的访问者才能使用同样的方法，访问到这个新Pod。

2. **存储状态**。这种情况意味着，应用的多个实例分别绑定了不同的存储数据。对于这些应用实例来说，Pod A第一次读取到的数据，和隔了十分钟之后再次读取到的数据，应该是同一份，哪怕在此期间Pod A被重新创建过。这种情况最典型的例子，就是一个数据库应用的多个存储实例。


所以， **StatefulSet的核心功能，就是通过某种方式记录这些状态，然后在Pod被重新创建时，能够为新Pod恢复这些状态。**

在开始讲述StatefulSet的工作原理之前，我就必须先为你讲解一个Kubernetes项目中非常实用的概念：Headless Service。

我在和你一起讨论Kubernetes架构的时候就曾介绍过，Service是Kubernetes项目中用来将一组Pod暴露给外界访问的一种机制。比如，一个Deployment有3个Pod，那么我就可以定义一个Service。然后，用户只要能访问到这个Service，它就能访问到某个具体的Pod。

那么，这个Service又是如何被访问的呢？

**第一种方式，是以Service的VIP（Virtual IP，即：虚拟IP）方式**。比如：当我访问10.0.23.1这个Service的IP地址时，10.0.23.1其实就是一个VIP，它会把请求转发到该Service所代理的某一个Pod上。这里的具体原理，我会在后续的Service章节中进行详细介绍。

**第二种方式，就是以Service的DNS方式**。比如：这时候，只要我访问“my-svc.my-namespace.svc.cluster.local”这条DNS记录，就可以访问到名叫my-svc的Service所代理的某一个Pod。

而在第二种Service DNS的方式下，具体还可以分为两种处理方法：

第一种处理方法，是Normal Service。这种情况下，你访问“my-svc.my-namespace.svc.cluster.local”解析到的，正是my-svc这个Service的VIP，后面的流程就跟VIP方式一致了。

而第二种处理方法，正是Headless Service。这种情况下，你访问“my-svc.my-namespace.svc.cluster.local”解析到的，直接就是my-svc代理的某一个Pod的IP地址。 **可以看到，这里的区别在于，Headless Service不需要分配一个VIP，而是可以直接以DNS记录的方式解析出被代理Pod的IP地址。**

那么，这样的设计又有什么作用呢？

想要回答这个问题，我们需要从Headless Service的定义方式看起。

下面是一个标准的Headless Service对应的YAML文件：

```
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
  selector:
    app: nginx

```

可以看到，所谓的Headless Service，其实仍是一个标准Service的YAML文件。只不过，它的clusterIP字段的值是：None，即：这个Service，没有一个VIP作为“头”。这也就是Headless的含义。所以，这个Service被创建后并不会被分配一个VIP，而是会以DNS记录的方式暴露出它所代理的Pod。

而它所代理的Pod，依然是采用我在前面第12篇文章 [《牛刀小试：我的第一个容器化应用》](https://time.geekbang.org/column/article/40008) 中提到的Label Selector机制选择出来的，即：所有携带了app=nginx标签的Pod，都会被这个Service代理起来。

然后关键来了。

当你按照这样的方式创建了一个Headless Service之后，它所代理的所有Pod的IP地址，都会被绑定一个这样格式的DNS记录，如下所示：

```
<pod-name>.<svc-name>.<namespace>.svc.cluster.local

```

这个DNS记录，正是Kubernetes项目为Pod分配的唯一的“可解析身份”（Resolvable Identity）。

有了这个“可解析身份”，只要你知道了一个Pod的名字，以及它对应的Service的名字，你就可以非常确定地通过这条DNS记录访问到Pod的IP地址。

那么，StatefulSet又是如何使用这个DNS记录来维持Pod的拓扑状态的呢？

为了回答这个问题，现在我们就来编写一个StatefulSet的YAML文件，如下所示：

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

```

这个YAML文件，和我们在前面文章中用到的nginx-deployment的唯一区别，就是多了一个serviceName=nginx字段。

这个字段的作用，就是告诉StatefulSet控制器，在执行控制循环（Control Loop）的时候，请使用nginx这个Headless Service来保证Pod的“可解析身份”。

所以，当你通过kubectl create创建了上面这个Service和StatefulSet之后，就会看到如下两个对象：

```
$ kubectl create -f svc.yaml
$ kubectl get service nginx
NAME      TYPE         CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
nginx     ClusterIP    None         <none>        80/TCP    10s

$ kubectl create -f statefulset.yaml
$ kubectl get statefulset web
NAME      DESIRED   CURRENT   AGE
web       2         1         19s

```

这时候，如果你手比较快的话，还可以通过kubectl的-w参数，即：Watch功能，实时查看StatefulSet创建两个有状态实例的过程：

> 备注：如果手不够快的话，Pod很快就创建完了。不过，你依然可以通过这个StatefulSet的Events看到这些信息。

```
$ kubectl get pods -w -l app=nginx
NAME      READY     STATUS    RESTARTS   AGE
web-0     0/1       Pending   0          0s
web-0     0/1       Pending   0         0s
web-0     0/1       ContainerCreating   0         0s
web-0     1/1       Running   0         19s
web-1     0/1       Pending   0         0s
web-1     0/1       Pending   0         0s
web-1     0/1       ContainerCreating   0         0s
web-1     1/1       Running   0         20s

```

通过上面这个Pod的创建过程，我们不难看到，StatefulSet给它所管理的所有Pod的名字，进行了编号，编号规则是： `<statefulset name>-<ordinal index>`。

而且这些编号都是从0开始累加，与StatefulSet的每个Pod实例一一对应，绝不重复。

更重要的是，这些Pod的创建，也是严格按照编号顺序进行的。比如，在web-0进入到Running状态、并且细分状态（Conditions）成为Ready之前，web-1会一直处于Pending状态。

> 备注：Ready状态再一次提醒了我们，为Pod设置livenessProbe和readinessProbe的重要性。

当这两个Pod都进入了Running状态之后，你就可以查看到它们各自唯一的“网络身份”了。

我们使用kubectl exec命令进入到容器中查看它们的hostname：

```
$ kubectl exec web-0 -- sh -c 'hostname'
web-0
$ kubectl exec web-1 -- sh -c 'hostname'
web-1

```

可以看到，这两个Pod的hostname与Pod名字是一致的，都被分配了对应的编号。接下来，我们再试着以DNS的方式，访问一下这个Headless Service：

```
$ kubectl run -i --tty --image busybox:1.28.4 dns-test --restart=Never --rm /bin/sh

```

通过这条命令，我们启动了一个一次性的Pod，因为--rm意味着Pod退出后就会被删除掉。然后，在这个Pod的容器里面，我们尝试用nslookup命令，解析一下Pod对应的Headless Service：

```
$ kubectl run -i --tty --image busybox:1.28.4 dns-test --restart=Never --rm /bin/sh
$ nslookup web-0.nginx
Server:    10.0.0.10
Address 1: 10.0.0.10 kube-dns.kube-system.svc.cluster.local

Name:      web-0.nginx
Address 1: 10.244.1.7

$ nslookup web-1.nginx
Server:    10.0.0.10
Address 1: 10.0.0.10 kube-dns.kube-system.svc.cluster.local

Name:      web-1.nginx
Address 1: 10.244.2.7

```

从nslookup命令的输出结果中，我们可以看到，在访问web-0.nginx的时候，最后解析到的，正是web-0这个Pod的IP地址；而当访问web-1.nginx的时候，解析到的则是web-1的IP地址。

这时候，如果你在另外一个Terminal里把这两个“有状态应用”的Pod删掉：

```
$ kubectl delete pod -l app=nginx
pod "web-0" deleted
pod "web-1" deleted

```

然后，再在当前Terminal里Watch一下这两个Pod的状态变化，就会发现一个有趣的现象：

```
$ kubectl get pod -w -l app=nginx
NAME      READY     STATUS              RESTARTS   AGE
web-0     0/1       ContainerCreating   0          0s
NAME      READY     STATUS    RESTARTS   AGE
web-0     1/1       Running   0          2s
web-1     0/1       Pending   0         0s
web-1     0/1       ContainerCreating   0         0s
web-1     1/1       Running   0         32s

```

可以看到，当我们把这两个Pod删除之后，Kubernetes会按照原先编号的顺序，创建出了两个新的Pod。并且，Kubernetes依然为它们分配了与原来相同的“网络身份”：web-0.nginx和web-1.nginx。

通过这种严格的对应规则， **StatefulSet就保证了Pod网络标识的稳定性**。

比如，如果web-0是一个需要先启动的主节点，web-1是一个后启动的从节点，那么只要这个StatefulSet不被删除，你访问web-0.nginx时始终都会落在主节点上，访问web-1.nginx时，则始终都会落在从节点上，这个关系绝对不会发生任何变化。

所以，如果我们再用nslookup命令，查看一下这个新Pod对应的Headless Service的话：

```
$ kubectl run -i --tty --image busybox dns-test --restart=Never --rm /bin/sh
$ nslookup web-0.nginx
Server:    10.0.0.10
Address 1: 10.0.0.10 kube-dns.kube-system.svc.cluster.local

Name:      web-0.nginx
Address 1: 10.244.1.8

$ nslookup web-1.nginx
Server:    10.0.0.10
Address 1: 10.0.0.10 kube-dns.kube-system.svc.cluster.local

Name:      web-1.nginx
Address 1: 10.244.2.8

```

我们可以看到，在这个StatefulSet中，这两个新Pod的“网络标识”（比如：web-0.nginx和web-1.nginx），再次解析到了正确的IP地址（比如：web-0 Pod的IP地址10.244.1.8）。

通过这种方法， **Kubernetes就成功地将Pod的拓扑状态（比如：哪个节点先启动，哪个节点后启动），按照Pod的“名字+编号”的方式固定了下来**。此外，Kubernetes还为每一个Pod提供了一个固定并且唯一的访问入口，即：这个Pod对应的DNS记录。

这些状态，在StatefulSet的整个生命周期里都会保持不变，绝不会因为对应Pod的删除或者重新创建而失效。

不过，相信你也已经注意到了，尽管web-0.nginx这条记录本身不会变，但它解析到的Pod的IP地址，并不是固定的。这就意味着，对于“有状态应用”实例的访问，你必须使用DNS记录或者hostname的方式，而绝不应该直接访问这些Pod的IP地址。

## 总结

在今天这篇文章中，我首先和你分享了StatefulSet的基本概念，解释了什么是应用的“状态”。

紧接着 ，我为你分析了StatefulSet如何保证应用实例之间“拓扑状态”的稳定性。

如果用一句话来总结的话，你可以这么理解这个过程：

> StatefulSet这个控制器的主要作用之一，就是使用Pod模板创建Pod的时候，对它们进行编号，并且按照编号顺序逐一完成创建工作。而当StatefulSet的“控制循环”发现Pod的“实际状态”与“期望状态”不一致，需要新建或者删除Pod进行“调谐”的时候，它会严格按照这些Pod编号的顺序，逐一完成这些操作。

所以，StatefulSet其实可以认为是对Deployment的改良。

与此同时，通过Headless Service的方式，StatefulSet为每个Pod创建了一个固定并且稳定的DNS记录，来作为它的访问入口。

实际上，在部署“有状态应用”的时候，应用的每个实例拥有唯一并且稳定的“网络标识”，是一个非常重要的假设。

在下一篇文章中，我将会继续为你剖析StatefulSet如何处理存储状态。

## 思考题

你曾经运维过哪些有拓扑状态的应用呢（比如：主从、主主、主备、一主多从等结构）？你觉得这些应用实例之间的拓扑关系，能否借助这种为Pod实例编号的方式表达出来呢？如果不能，你觉得Kubernetes还应该为你提供哪些支持来管理这个拓扑状态呢？

感谢你的收听，欢迎你给我留言，也欢迎分享给更多的朋友一起阅读。