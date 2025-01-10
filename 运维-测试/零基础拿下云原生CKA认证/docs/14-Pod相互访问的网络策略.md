你好，我是雪飞。

上一课我们讨论了用户和服务账号通过 API Server 访问集群的安全问题，通过 RBAC 权限控制有效应对了外部访问风险。今天，我带你了解一下 K8s 内部 Pod 之间相互访问的安全问题，从而防范 K8s 集群内部的安全风险。

默认情况下，K8s 集群内部网络没有任何网络访问限制，任何 Pod 都可以与其他 Pod 通信，甚至不同命名空间的 Pod 也可以相互访问。例如，在 A 命名空间下运行着一个转账的业务应用 Pod，然后有人偷偷在 B 命名空间中部署了一个给自己转账的应用，那么这个 Pod 就可能直接访问 A 中的 Pod 来给自己转账，这样就会出现严重的安全漏洞。因此，有时需要对 Pod 进行网络隔离，从而提升集群的安全性。

## 认识网络策略

K8s 提供了网络策略（NetworkPolicy）资源对象，用于确保只有授权的流量才能进入或离开 Pod，从而提供一种强大灵活的安全机制。网络策略允许管理员设置网络规则来控制 Pod 间的网络流量，这些规则通过标签选择器选定被保护的 Pod，并规定哪些来源 Pod（或者来源 IP）允许访问被保护的 Pod，或者规定这些被保护的 Pod 允许访问哪些目标 Pod（或者目标IP）。

我们看一下网络策略的三个组成部分：

- **Pod 选择器：** 通过标签来选择被保护的 Pod，最终在这些 Pod 上应用网络策略。
- **入口规则（Ingress）：** 定义允许进入 Pod 的来源流量。
- **出口规则（Egress）：** 定义允许从 Pod 流出的目标流量。

入口规则和出口规则中都包含两大组成部分，一是限定访问来源 Pod 或者访问目标 Pod，另一个是指定访问请求的端口号和协议，这两个部分是“并且”的关系，既要满足端口号和协议的要求，又要满足来源 Pod 或目标 Pod 的限制。

![图片](https://static001.geekbang.org/resource/image/4f/27/4f3eb404986b0550a03119b48b458a27.jpg?wh=799x349)

当这些策略被创建并应用后，它们依赖于集群的网络插件来执行。我们部署集群时，安装的是 Calico 网络插件，它实现了网络策略能力。部署网络策略时，K8s 会告诉网络插件如何处理 Pod 之间的访问，网络插件会根据规则调整底层网络设置（路由器、交换机或防火墙等），确保只允许满足条件的访问。

K8s 网络策略可以通过 Pod标签、命名空间标签和 IP 地址这三种不同维度来选择来源或者目标 Pod 或者 IP，同时也会根据访问请求的协议类型、端口来选择要控制的入口或出口请求。常见应用场景包括：

- **Pod 间访问隔离：** 在微服务架构中，K8s 网络策略为不同安全级别的业务应用定制 Pod 的访问权限。例如，对于处理敏感支付信息的 Pod，可以配置网络策略仅允许订单 Pod 访问，从而阻止其他 Pod 访问。这种精确的网络策略配置增强了安全性，确保只有授权的 Pod 能够进行通信。
- **命名空间的访问隔离：** K8s 为不同项目分配独立的命名空间并配置特定的网络策略，保障项目间的访问隔离，防止数据泄露或未授权访问。
- **IP 白名单：** 对于一些向集群外部提供服务的 Pod，可以通过配置网络策略来限制访问请求的 IP 地址，严格控制外部访问请求。

合理设计和部署网络策略可以在不同场景下实现对应用的灵活精细的访问控制，从而确保 K8s 集群内部 Pod 的安全与稳定。了解了网络策略的概念，我们接着来实际配置网络策略。

## 使用网络策略

使用网络策略包含以下步骤：

1. 首先，要确定网络策略生效的命名空间，因为网络策略是保护该命名空间中的 Pod。
2. 其次，通过 Pod 的标签来选择该命名空间中被保护的 Pod。
3. 然后，确认入口 Ingress 和出口 Egress 规则。
4. 最后，编写网络策略的 YAML 文件，部署后生效。

### 创建网络策略

我带你动手部署一个网络策略。要求如下：

- 被保护的 Pod 是在命名空间 ns1 中，Pod 标签为 “app=back”。
- 入口流量规则：对于 TCP 协议并且端口为 80 的访问请求，以下三种来源可以允许访问被保护的 Pod：


  a. 命名空间 ns2 中的所有 Pod；


  b. 命名空间 ns1 中标签为 “app=front” 的所有 Pod；


  c. 请求来源 IP 地址为 192.168.2.0/8 网段。
- 出口流量规则：只允许被保护的 Pod 对外访问相同命名空间中的所有 Pod。

我们为这个网络策略编写一个 YAML 文件（back-pod-np.yaml）如下：

```yaml
# back-pod-np.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: back-pod-networkpolicy
  namespace: ns1
spec:
  podSelector:
    matchLabels:
      app: back
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          ns: ns2
    - podSelector:
        matchLabels:
          app: front
    - ipBlock:
        cidr: 192.168.2.0/8
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - podSelector: {}

```

- **namespace：** 网络策略是按照命名空间隔离的，所以它选择的被保护的 Pod 都是在这个命名空间中。
- **podSelector** **：** 每个网络策略都包括一个 podSelector，通过 Pod 标签选择一组被保护的 Pod。示例中的策略选择了命名空间 ns1 中带有 “app=back” 标签的 Pod。
- **policyTypes** **：** 指定规则中包含 Ingress 或者 Egress 规则，示例中两者兼有。
- **ingress** **：** 如果在 policyTypes 属性中包含了Ingress，则需要 ingress 属性来定义入口流量的规则列表，流量需要同时匹配 from 和 ports 属性的要求。示例中，ports 属性要求访问请求的协议是 TCP 并且访问端口是 80，同时 from 属性则要求来源 Pod（或者 IP）满足三个条件的任意一个：第一个通过 **namespaceSelector** 属性指定标签为 “ns=ns2” 的命名空间中的所有 Pod；第二个通过 **podSelector** 属性指定在网络策略的命名空间 ns1 中，标签为 “app=front” 的所有 Pod；第三个通过 **ipBlock** 属性指定 IP 地址为 192.168.2.0/8 网段的所有访问请求（ipBlock 比较特殊，限定的不是某个 Pod ，而是针对来源的 IP 地址）。
- **egress** **：** 如果在 policyTypes 属性中包含了Egress，则需要 egress 属性来定义出口流量的规则列表，流量需要同时匹配 to 和 ports 属性的要求。示例中，没有 ports 属性，所以规则针对所有协议和端口的出口流量，同时 to 属性则只要求目标 Pod 满足 podSelector 属性指定的 Pod。空的 podSelector（podSelector: {}）表示网络策略命名空间 ns1 下的所有 Pod。

from 和 to 属性都可以支持 namespaceSelector、podSelector 和 ipBlock 三种选择方式，来限制来源 Pod 或 来源 IP，以及限制目标 Pod 或目标 IP。这些方式可以相互嵌套，形成更复杂的规则。

部署网络策略，然后通过 “kubectl describe” 查看网络策略，通过返回结果可以清晰地了解网络策略的规则详情。

```yaml
[root@k8s-master ~]# kubectl apply -f back-pod-np.yaml
networkpolicy.networking.k8s.io/back-pod-networkpolicy created
[root@k8s-master example-14]# kubectl describe networkpolicy back-pod-networkpolicy -n ns1
Name:         back-pod-networkpolicy
Namespace:    ns1
Created on:   2024-06-28 22:32:46 +0800 CST
Labels:       <none>
Annotations:  <none>
Spec:
  PodSelector:     app=back
  Allowing ingress traffic:
    To Port: 80/TCP
    From:
      NamespaceSelector: ns=ns2
    From:
      PodSelector: app=front
    From:
      IPBlock:
        CIDR: 192.168.2.0/8
        Except:
  Allowing egress traffic:
    To Port: <any> (traffic allowed to all ports)
    To:
      PodSelector: <none>
  Policy Types: Ingress, Egress

```

### 验证网络策略

现在我们来简单验证一下网络策略，准备一下环境。

1. 准备两个命名空间，ns1 和 ns2，同时给 ns2 打标签 ns=ns2。

```bash
[root@k8s-master ~]# kubectl create ns ns1
namespace/ns1 created
[root@k8s-master ~]# kubectl create ns ns2
namespace/ns2 created
[root@k8s-master ~]# kubectl label ns ns2 ns=ns2
namespace/ns2 labeled

```

2. 准备 4 个 Pod

- 在命名空间 ns1 中创建一个运行 nginx 镜像的 Pod，名称为 ns1-nginx，打上标签 “app=back”；
- 在命名空间 ns1 中创建一个运行 busybox 镜像的 Pod，名称为 ns1-busybox；
- 在命名空间 ns1 中创建一个运行 busybox 镜像的 Pod，名称为 ns1-busybox-front，打上标签为 “app=front”；
- 在命名空间 ns2 中创建一个运行 busybox 镜像的 Pod，名称为 ns2-busybox。

```bash
[root@k8s-master ~]# kubectl run ns1-nginx --image=nginx -n ns1
pod/ns1-nginx created
[root@k8s-master ~]# kubectl label pod ns1-nginx -n ns1 app=back
pod/ns1-nginx labeled
[root@k8s-master ~]# kubectl run ns1-busybox --image=busybox -n ns1 -- sleep 3600
pod/ns1-busybox created
[root@k8s-master ~]# kubectl run ns1-busybox-front --image=busybox -n ns1 -- sleep 3600
pod/default-busybox created
[root@k8s-master ~]# kubectl label pod ns1-busybox-front -n ns1 app=front
pod/default-busybox labeled
[root@k8s-master ~]# kubectl run ns2-busybox --image=busybox -n ns2 -- sleep 3600
pod/ns2-busybox created

```

3. 验证过程

根据网络策略，名称为 ns1-nginx （命名空间为 ns1，同时标签为 “app=back”）的 Pod 就是符合规则的被保护的 Pod。由于 Pod 之间的访问可以通过它们的临时 IP 地址，我们查看一下 ns1-nginx 的 IP 地址，然后进入其他几个 Pod 中，使用 wget 命令来请求 ns1-nginx 的 Web 服务页面，根据请求是否成功来测试网络策略的规则。

```bash
[root@k8s-master ~]# kubectl get pod ns1-nginx -n ns1 -o wide
NAME        READY   STATUS    RESTARTS   AGE   IP              NODE          NOMINATED NODE   READINESS GATES
ns1-nginx   1/1     Running   0          11m   10.244.126.11   k8s-worker2   <none>           <none>

```

命名空间 ns1 中的 ns1-busybox 是否可以访问相同命名空间中的 ns1-nginx？

```bash
[root@k8s-master ~]# kubectl exec -it ns1-busybox -n ns1 -- sh
/ # wget 10.244.126.11
Connecting to 10.244.126.11 (10.244.126.11:80)

```

命名空间 ns2 中的 ns2-busybox 是否可以访问命名空间 ns1 中的 ns1-nginx？

```bash
[root@k8s-master ~]# kubectl exec -it ns2-busybox -n ns2 -- sh
/ # wget 10.244.126.11
Connecting to 10.244.126.11 (10.244.126.11:80)
saving to 'index.html'
index.html           100% |*********************|   615  0:00:00 ETA
'index.html' saved

```

命名空间 ns1 中的 ns1-busybox-front 是否可以访问命名空间 ns1 中的 ns1-nginx？

```bash
[root@k8s-master ~]# kubectl exec -it ns1-busybox-front -n ns1 -- sh
/ # wget 10.244.126.11
Connecting to 10.244.126.11 (10.244.126.11:80)
saving to 'index.html'
index.html           100% |*********************|   615  0:00:00 ETA
'index.html' saved

```

上面的 3 个问题代表了我们使用 3 种不同来源的 Pod 来访问被保护的 Pod（ns1-nginx），从访问请求结果可以看出，命名空间 ns2 中的 Pod（ns2-busybox）可以访问 ns1-nginx，相同命名空间中带有 “app=front” 标签的 Pod（default-busybox）也可以访问 ns1-nginx，但是相同命名空间中没有标签的 Pod（ns1-busybox）无法访问 ns1-nginx，这与我们部署的网络策略的入口流量规则是一致。对于出口流量的规则，你可以自己设计实验验证一下。

### 网络策略注意事项

通过上面动手设计并部署网络策略，你已经了解了网络策略的使用方式。那么在实际配置网络策略时，你要注意以下几点。

首先，网络策略是白名单机制。一旦使用网络策略，只有明确定义的访问请求才会被允许放行。在没有使用网络策略之前，Pod 默认允许所有入口和出口的访问请求。但是，一旦在网络策略中配置了 policyTypes，包含了 Ingress 和 Egress，则只有符合配置规则的入口或者出口访问请求才能成功。

其次，要允许从来源 Pod 到目的 Pod 的某个连接，来源 Pod 的出口策略和目的 Pod 的入口策略都需要允许此连接。如果任何一方不允许此连接，则连接将会失败。

最后，可以为 Pod 设置多个网络策略，网络策略的规则是相加的，不会产生冲突。但应该避免创建过于复杂的网络策略，因为这可能会导致网络通信中断或延迟。

对于多个规则在同一个 from 或 to 属性中，如果多个条件在一个列表项中，则是“并且”的关系，所有条件要同时满足。如果多个条件是多个列表项，则是“或者”的关系，所有条件满足其中一个就会放行。看下面两个 YAML 文件，虽然多了一个 “-”，但是表达的意思完全不同。

```yaml
...
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          user: dev
    - podSelector:
        matchLabels:
          role: client
  ...

```

此策略在 from 数组中包含两个列表项（每个 “-” 就是一个列表项）。该策略允许来自带有 “user=dev” 标签的命名空间中的所有 Pod 的访问，或者来自网络策略所在的命名空间中，带有 “role=client” 标签的所有 Pod 的访问 。

```yaml
...
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          user: dev
      podSelector:
        matchLabels:
          role: client
  ...

```

此策略在 from 数组中仅包含一个列表项（只有一个 “-”）。所以这个策略只允许来自带有 “user=dev” 标签的命名空间中，且带有 “role=client” 标签的 Pod 的访问。

如果是同一命名空间中部署了多个网络策略，这些网络策略是“或者”的关系，只要命中其中一个规则，就可以对访问放行。

## **小结**

今天，我带你了解了 K8s 集群中的网络安全策略（NetworkPolicy）。

首先，网络策略是 K8s 提供的针对内部 Pod 之间网络访问的控制机制，用于确保只有授权的流量才能进入或离开 Pod。网络策略由三个部分组成，Pod 选择器是通过标签来选择被保护的 Pod。入口规则（Ingress）定义允许进入 Pod 的来源流量。出口规则（Egress）定义允许从 Pod 流出的目标流量。

其次，网络策略可以通过 Pod 标签、命名空间标签和 IP 地址这三种不同维度来选择来源或者目标 Pod（或者 IP），同时也会根据访问请求的协议类型、端口来选择要控制的入口或出口请求。网络策略主要应用于 Pod 之间的访问隔离、命名空间之间的访问隔离以及设置IP白名单。

接着，我带你动手配置和验证了网络策略，学习了网络策略的 YAML 文件结构，注意 **podSelector、namespaceSelector** 和 **ipBlock** 这 3 个属性，使用起来非常灵活，用来限制的访问请求的来源或目标。

最后，注意网络策略是白名单机制，多个规则可以同时生效，只要满足其中一个，就可以放行访问请求。

## 思考题

这就是今天的全部内容，在 CKA 中也会考到相关的知识点。我给你留一道练习题。

创建一个网络策略，只允许 dev 命名空间中的 Pod 访问 prod 命名空间中的 Pod 的 80 端口。

相信经过动手实践，会让你对知识的理解更加深刻。