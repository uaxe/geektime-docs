你好，我是雪飞。

前面我们学习了通过 Deployment 部署无状态应用 Pod，其中有些 Pod 中的应用是提供 Web 访问服务，所以需要通过网络访问到这些 Pod。

在部署 Pod 的时候，K8s 集群给它们分配了自己的 IP 地址，Pod 可以直接通过集群内部 IP 地址相互访问。但是我们还需要解决两个问题：

第一个是服务发现，K8s 中 Pod 的 IP 地址是动态分配的，每次 Pod 重启后都会重新分配一个内部 IP，因此无法使用固定的 IP 来访问 Pod。

第二个是负载均衡，Deployment 管理的 Pod 是多副本的，并且可以扩缩容，因此需要一个统一的访问入口将访问请求自动分配给这些 Pod 副本。为了解决这两个问题，Service 资源对象应运而生。

## 认识 Service

Service 是 K8s 中负责网络服务发现和负载均衡的资源对象，它定义了通过网络访问 Pod 的方式。当我们访问 Service 时，它自动将访问请求转发到相应的 Pod 上，然后由 Pod上的应用处理访问请求。

Service 主要处理“服务发现”和“负载均衡”这两个重要问题。服务发现是指当 Pod 发生变化时（如故障重启、扩容缩容等），Service 仍能自动找到变化后的 Pod。负载均衡是指 Service 可以代理多个 Pod 的网络访问，通过一定机制把访问 Service 的请求自动分配到这些代理的 Pod 中。

Service 和要代理的 Pod 是松散耦合的，按照在 Service 定义时所指定标签来匹配 Pod 定义时的标签，二者相互关联绑定。如下图所示，Service 指定关联的标签是 “app: nginx”，此时在任何节点上只要标签是 “app: nginx” 的 Pod ，那么访问 Service 的请求就会自动分配到这些 Pod 上。

![图片](https://static001.geekbang.org/resource/image/04/3f/04c1f7244598e1e0abec3a68a2d3fd3f.jpg?wh=659x638)

这里我还要介绍一下 Endpoints，它与 Service 一一对应，是一种特殊类型的资源对象。实际上，Endpoints 存储了 Service 代理的 Pod 的实际位置和 IP 信息。当你创建一个 Service 来访问一组 Pod 时，K8s 会自动创建一个 Endpoints 来维护这个 Service 代理的 Pod 列表。

## 使用 Service

介绍完概念，下面我们就来讲一下如何使用 Service。创建一个 Service 可以使用 kubectl 命令和 YAML 文件两种方式。

### kubectl 命令方式

使用 “kubectl expose deployment” 来创建一个 Service。这个命令意思是暴露一个针对 Deployment 的网络服务，所以需要先部署一个 Deployment。以下是具体操作命令：

```bash
# 创建 Deployment，名称 my-deployment
kubectl create deployment my-deployment --image=nginx --replicas=3

# 创建 Service，名称 my-service，暴露对象是 my-deployment
kubectl expose deployment my-deployment --port=80 --target-port=80 --name=my-service --type=ClusterIP

```

- **–port：** 表示 Service 自身对外暴露的端口。
- **–target-port：** 表示 Deployment 中的 Pod 容器暴露的端口。
- **–name：** 表示 Service 的名字，如果没有该参数，会使用 Deployment 的名字。
- **–type：** 表示 Service 的类型，Service 有四种类型，默认值就是 ClusterIP。

这里我顺便介绍一下 Service 的四种类型。

- **ClusterIP** **：** K8s 为 Service 创建的一个稳定的集群内部 IP 地址，只能在集群内访问。
- **NodePort** **：** K8s 在集群中的每个节点上将 Service 的端口和节点的一个特定端口绑定起来，这样就可以通过 “<节点IP>:<节点端口>” 访问到 Service，在之前课程部署 Nginx 的时候，我们体验过这种访问方式。
- **LoadBalancer** **：** 需要使用第三方的负载均衡器，来给 Service 生成一个集群外部的 IP 地址，从而通过访问这个 IP 地址来访问 Service。
- **ExternalName** **：** 当 K8s 集群内部需要访问集群外部的网络服务时，在集群内创建的一个外部服务的 Service 映射，通过访问这个 Service，就可以在集群内访问外部服务。

### YAML 文件方式

通过 YAML 文件（my-service.yaml）方式定义一个 Service，跟上面的命令方式创建的 Service 基本一样。需要注意，kubectl 命令方式创建 Service 时，不需要设置选择 Pod 的标签。但是在 YAML 文件定义时一定要在 selector 属性中注明要代理的 Pod 的标签。

```yaml
[root@k8s-master ~]# cat my-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: default
spec:
  selector:    # 通过 selector 确定代理哪些 Pod
    app: my-deployment
  type: ClusterIP    # 用于将来自同一个 IP 地址的请求定向到同一个 Pod 中
  ports: # 端口信息
  - name: 80-80
    protocol: TCP    # 端口协议
    port: 80         # Service 自身端口
    targetPort: 80   # Pod 容器端口

```

- **selector：** 用来指明要代理的 Pod 的标签，注意不是 Deployment 的标签，而是Deployment 中的 Pod 模板中的 Pod 标签。
- **ports：** 定义 Service 端口信息，可以配置多个端口。和命令参数一样，其中 port 表示 Service 自身对外暴露的端口。targetPort 表示 Deployment 中的 Pod 容器暴露的端口。protocol 表示端口使用的协议。Service 能够将任意 port 映射到 Pod 的 targetPort，出于方便，port会被设置为与 targetPort 属性相同的值。
- **type：** 同命令中的参数，表示 Service 的类型，默认是 ClusterIP，也可以选择其他三种类型。

部署 Service 的 YAML 文件，然后我们查看部署好的 Service 与 Endpoints，可以看到名叫 my-service 的 Service，它的类型（TYPE）是 ClusterIP，自动分配的集群内部 IP（CLUSTER-IP）为 “10.98.2.207”。从 Endpoints 可以看出 my-service 代理的 Pod 的 IP 地址（ENDPOINTS）是 “10.244.126.22，10.244.126.23，10.244.194.87”，也就是 Deployment 部署的三个 Pod 的 IP 地址。

```bash
[root@k8s-master ~]# kubectl apply -f my-service.yaml
service/my-service created
[root@k8s-master ~]# kubectl get svc   # svc 是 Service 的缩写
NAME         TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1     <none>        443/TCP   5d
my-service   ClusterIP   10.98.2.207   <none>        80/TCP    11s
[root@k8s-master ~]# kubectl get endpoints  # 查看 Endpoints
NAME         ENDPOINTS                                            AGE
kubernetes   10.0.16.11:6443                                      5d
my-service   10.244.126.22:80,10.244.126.23:80,10.244.194.87:80   15s

```

## Service 的访问方式

Service 已经准备好了，我们就要说一下怎么访问 Service 了。对于 Service 的访问可以分为集群内部访问和集群外部访问。

集群内部访问可以使用 Service 的 ClusterIP 和固定域名访问；集群外部访问可以使用 Service 的 NodePort 类型和 LoadBalancer 类型。下面我分别介绍一下。

![图片](https://static001.geekbang.org/resource/image/41/80/416dbde070d14aaf87737539ffe5ea80.jpg?wh=766x521)

### 集群内部访问

**1\. ClusterIP 访问**

ClusterIP 类型的 Service 会自动生成一个集群内部 IP，用于集群内部访问，例如多个微服务应用，部署成功后，每个应用都会部署自己的 Service，它们之间的相互访问就可以通过 Service 的集群内部 IP（CLUSTER-IP）。

我们模拟一下这种访问情况，上一小节已经部署了一个 Nginx 镜像的 Deployment，同时也部署了 my-service 来提供代理访问，通过查看命令已经知道 my-service 的集群内部 IP 是 “10.98.2.207”。我们把这个应用作为微服务 A。现在我们再部署一个 busybox 镜像的 Pod 作为微服务 B，我们进入到微服务 B 的 Pod 中，然后通过 “wget” 命令去访问微服务 A 的 Service（my-service）的集群内部 IP，如果可以获取到 Nginx 的 Web 服务的首页（index.html），就说明访问 Service 成功。

实验过程如下：

```bash
[root@k8s-master ~]# kubectl run bs --image=busybox -- sleep 3600
pod/bs created
[root@k8s-master ~]# kubectl exec -it bs -- sh
/ # wget 10.98.2.207
Connecting to 10.98.2.207 (10.98.2.207:80)
saving to 'index.html'
index.html           100% |**************************************************************************************|   615  0:00:00 ETA
'index.html' saved
/ # cat index.html
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
...

```

通过实验我们可以看出，微服务 B 的 Pod 可以直接访问微服务 A 的 Service 的集群内部 IP。

**2\. 域名访问**

第二种方式就是使用 Service 的域名。既然可以用域名，那就一定需要 DNS 解析。DNS 解析就是把域名解析成 IP 的工具，存放着域名和 IP 的对照关系。在 K8s 中，默认使用 CoreDNS 组件作为集群的 DNS 服务器，CoreDNS 应用监视 K8s 的 API Server，为每一个 Service 建立用于域名解析的 DNS 记录。这样我们就可以通过域名直接访问 Service。

DNS 域名的格式如下：

```yaml
<service-name>.<namespace-name>.svc.cluster.local

```

其中 “ **svc.cluster.local**” 是 K8s 集群内部服务的默认域，可以省略。因此，我们通常用以下方式访问 Service：

- 在同一个命名空间下，直接通过 Service 的名称即可访问对应的 Service，即 <service 名称>。
- 在不同命名空间下，还需要加上命名空间的名称来访问 Service，即 <service 名称>.<namespace 名称>。

对于上面的微服务 B 访问微服务 A 的例子，我们也可以不使用 my-service 的集群内部 IP 地址，从而直接使用 “my-service” 这个 Service 名称来访问微服务 A 的 Service。

```bash
[root@k8s-master ~]# kubectl exec -it bs -- sh
/ # wget my-service
Connecting to my-service (10.98.2.207:80)
saving to 'index.html'
index.html           100% |**************************************************************************************|   615  0:00:00 ETA
'index.html' saved

```

讲完了集群内部访问 Service，下面我介绍一下集群外部访问 Service，集群外部访问 Service 非常重要，它可以是其他集群中的应用访问集群中的 Service，也可以是通过公网（互联网）来访问集群中的 Service。NodePort 类型和 LoadBalancer 类型的 Service 都可以实现集群外部的访问。

### 集群外部访问

**1\. 通过 NodePort 类型**

NodePort 是一种常用的 Service 类型，它允许我们在集群外部访问 Service。它的工作原理是将 Service 的端口映射到每个节点的对应端口上，然后通过任意节点“<节点IP>:<节点端口>”来访问 Service。

我们来动手实验一下，修改上一小节的 Service 的 YAML 文件（my-service.yaml），将 Service 类型改为 NodePort，同时通过 “nodePort” 属性指定节点端口为 30001，然后重新部署一下。如果不指定节点端口为 30001，K8s 会为 NodePort 类型的 Service 自动分配一个节点端口，映射的节点端口范围是 30000-32767。

```yaml
...
  type: NodePort
  ports: # 端口信息
  - name: 80-80
    protocol: TCP    # 端口协议
    port: 80         # service 自身端口
    targetPort: 80   # pod 容器端口
    nodePort: 30001  # 自定义的节点映射端口

```

查看部署好的 Service，可以看到 my-service 的类型（TYPE）是 NodePort，Service 的 80 端口映射到了节点的 30001 端口（PORTS）。虽然 NodePort 是用于外部访问的 Service 类型，但它也为我们生成了用于内部访问的集群内部 IP（CLUSTER-IP）。因此，集群内部访问仍然可以使用这个内部 IP 地址。

```bash
[root@k8s-master ~]# kubectl apply -f my-service.yaml
service/my-service configured
[root@k8s-master ~]# kubectl get svc
NAME        TYPE       CLUSTER-IP     EXTERNAL-IP  PORT(S)       AGE
kubernetes  ClusterIP  10.96.0.1      <none>       443/TCP       5d17h
my-service  NodePort   10.97.192.251  <none>       80:30001/TCP  29m

```

此时，我们可以直接在自己的本地机器的浏览器中输入节点的公网 IP 和 30001 端口号来访问 Service，从而访问到 Service 代理的 Nginx 的应用 Pod，实现集群的外部访问。

![图片](https://static001.geekbang.org/resource/image/21/5c/21dc885ff5b82e9530e4ecc58690d25c.jpg?wh=1793x665)

**2\. 通过 LoadBalancer 类型**

LoadBalancer 类型和 NodePort 类型很相似，都可以向集群外部暴露一个节点的映射端口。区别在于 LoadBalancer 类型的 Service 需要使用集群外部的第三方负载均衡器来生成一个 “External-IP”，然后通过 “External-IP” 来访问 Service，而不用再使用任何节点的 IP。这种负载均衡器通常由云服务商提供，它在集群外部实现了一层额外的负载均衡。

**注意** **：** 一旦创建了 LoadBalancer 类型的 Service，K8s 也会自动映射一个 NodePort 端口，并允许通过节点 IP 和这个端口来访问 Service。

我们刚讲了访问 Service 的各种方式，现在说一下集群中的 Pod 访问集群外部应用的方式。当然 Pod 可以通过外部应用的 URL 地址或者 IP 直接访问，但是如果这个外部应用经常被集群内部的 Pod 访问，就可以使用一种更灵活的方式来访问它，这就是 ExternalName 类型的 Service。

### 访问外部应用

ExternalName 类型的 Service 用于引入集群外部的应用，它通过 ExternalName 属性指定外部应用的 URL 地址或者 IP 地址，然后就可以在集群内部访问此 Service 来访问外部的应用了。例如，在集群内部定义一个 Service，用来访问百度网站，下面是 YAML 文件的写法。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: baidu-service
spec:
  type: ExternalName # Service 类型
  externalName: www.baidu.com  # 使用外部服务的 IP 地址也可以

```

部署成功后，就可以在集群内部通过访问 “baidu-service” 这个 Service 来访问百度网站了。ExternalName 类型的 Service 不会生成集群内部 IP 地址，所以需要用 Service 的 DNS 域名访问。

```bash
[root@k8s-master ~]# kubectl get svc
NAME            TYPE           CLUSTER-IP  EXTERNAL-IP     PORT(S) AGE
baidu-service   ExternalName   <none>      www.baidu.com   <none>  42m

```

## Service 多端口

由于安全性的要求，我们通常需要使用 HTTPS 协议来访问应用 Pod。HTTP 协议默认使用 80 端口，而 HTTPS 协议则是使用 443 端口。在这种情况下，我们需要在 Service 中配置多个端口以代理 Pod 的不同端口。

以下是一个多端口 Service 的 YAML 文件，通过访问 443 端口也可以访问到 Pod 应用。随后，我们将学习 Ingress 资源对象，通过 Ingress 可以方便地配置 HTTPS 访问。

```yaml
...
  type: NodePort    # 用于将来自同一个 IP 地址的请求定向到同一个 Pod 中
  ports: # 端口信息
  - name: 80-80
    protocol: TCP    # 端口协议
    port: 80         # Service 自身端口
    targetPort: 80   # Pod 容器端口
  - name: 443-80
    protocol: TCP    # 端口协议
    port: 443        # Service 自身端口
    targetPort: 80   # Pod 容器端口

```

部署成功后，可以看到 Service 生成了两个端口，并且都映射到节点的不同 NodePort 端口。

```bash
[root@k8s-master ~]# kubectl get svc
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
my-service   NodePort    10.107.60.244   <none>        80:31955/TCP,443:31796/TCP   34s

```

## **小结**

今天，我介绍了 K8s 中的 Service，Service 是 K8s 中负责提供服务发现和负载均衡功能的资源对象。服务发现是指当 Pod 发生变化时（如故障重启、扩容缩容等），Service 仍然能够自动找到变化后的 Pod。负载均衡是指 Service 可以代理多个 Pod 的网络访问，通过一定机制把访问 Service 的请求自动分配到这些 Pod 中。Service 通过标签选择关联对应的 Pod，从而为这些 Pod 提供了一个稳定的访问入口，屏蔽了 Pod 的动态变化。

Service 有四种类型：ClusterIP 类型会生成一个稳定的集群内部 IP 地址，只能在集群内访问。NodePort 类型会在每个节点上将 Service 的端口和节点的特定端口绑定起来，然后通过 “<节点IP>:<节点端口>” 访问 Service。LoadBalancer 类型需要使用第三方的负载均衡器，从而给 Service 生成一个用于集群外部访问的 IP 地址。ExternalName 类型可以把集群外部应用映射到集群内部的 Service。

Service 既可以通过 kubectl 命令创建，也可以使用 YAML 文件的方式定义。要注意 Service 的标签选择器（selector）需要关联到正确的 Pod 标签，部署时会创建一个 Endpoints 来管理代理的 Pod 列表。

最后，介绍了访问 Service 的不同方式，集群内部可以通过 Service 的集群内部 IP 或者域名访问，集群外部可以通过 NodePort 类型的节点 IP 和端口访问，也可以通过 LoadBalancer 类型生成的外部 IP 访问。集群内部访问外部应用，可用使用 ExternalName 类型的 Service。

## 思考题

这就是今天的全部内容，Service 是 K8s 中非常重要的网络资源对象，在 CKA 中也会考到相关的知识点。我给你留一道练习题。

不要使用 Deployment，而是手动创建两个相同标签（app=back）的 Pod，一个 Pod 镜像是 Nginx，另一个 Pod 镜像是 Apache。然后创建一个 NodePort 类型的多端口的 Service 来代理这两个 Pod，尝试通过节点的 IP 和端口来访问这两个 Pod 的 Web 服务，观察一下实验结果。

相信经过动手实践，会让你对知识的理解更加深刻。