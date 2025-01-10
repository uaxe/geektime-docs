你好，我是雪飞。

上节课我和你一起体验了 CKA 认证考试的报名流程，你按照课程中的步骤操作就可以成功预约考试。最后两节课，我来给你讲一讲本专栏的超级干货——考试真题。实际上 CKA 考试真题的复现率很高，理解真题的考点，多动手写几遍代码，相信你就能高分通过。

CKA 考试是 17 道题目，我分为上下两个部分。接下来就开始第一部分的真题讲解，你准备好了吗？开始吧！

首先要说明一下，在每道题答题开始之前都需要切换集群，考试题目中会给出切换集群的命令，你直接复制粘贴执行即可。 **注意：一定要先执行题目中的切换集群命令，否则答题时可能当前集群没有你需要的环境，或者会破坏当前的集群环境。**

```bash
# 答题时先执行题目中的切换集群命令，例如：
kubectl config use-context k8s

```

## 第一题 RBAC

#### 题目

为部署流水线创建一个新的 ClusterRole 并将其绑定到范围为特定的 Namespace 的特定 ServiceAccount。

1. 创建一个名为 deployment-clusterrole 且仅允许创建以下资源类型的新 ClusterRole：Deployment StatefulSet DaemonSet。
2. 在现有的 Namespace “app-team1” 中创建一个名为 cicd-token 的新 ServiceAccount。限于 Namespace “app-team1” 中，将新的 ClusterRole “deployment-clusterrole” 绑定到新的 ServiceAccount “cicd-token”。

#### 答题要点

这道题主要考 K8s 集群的访问安全策略，创建 ClusterRole 和 ServiceAccount，绑定时要求限定为 app-team1 的命名空间，所以要使用 RoleBinding 进行绑定。

建议使用 kubectl 命令进行配置，这样更快。知识点参考专栏 [第 13 课](https://time.geekbang.org/column/article/796009)，下面我给出参考答案。

#### 参考答案

```bash
# 创建 ClusterRole
kubectl create clusterrole deployment-clusterrole --verb=create --resource=deployments,statefulsets,daemonsets

# 创建 ServiceAccount
kubectl create serviceaccount cicd-token -n app-team1

# 创建 RoleBinding
kubectl create rolebinding cicd-token-rolebinding --clusterrole=deployment-clusterrole --serviceaccount=app-team1:cicd-token -n app-team1

```

#### 验证

有些题目答完之后可以验证一下，这道题我们就可以使用 “kubectl auth can-i” 命令快速验证一下。

```bash
# 期望返回 no
kubectl auth can-i create deployment --as system:serviceaccount:app-team1:cicd-token

# 期望返回 yes
kubectl auth can-i create deployment --as system:serviceaccount:app-team1:cicd-token -n app-team1

```

## 第二题 Deployment 扩容

#### 题目

将 Deployment “presentation” 扩展至 4 个 Pods。

#### 答题要点

这道题主要考 Deployment 资源对象的弹性伸缩命令，知识点参考专栏 [第 7 课](https://time.geekbang.org/column/article/794207)，下面我给出参考答案。

#### 参考答案

```bash
# 执行扩容命令
kubectl scale deployment presentation --replicas=4

```

#### 验证

查看 Deployment，READY 显示 4/4，说明已经扩容到 4 个 Pods。

```bash
[root@k8s-master ~]# kubectl get deployment presentation
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
presentation   4/4     4            4           9d

```

## 第三题 NetworkPolicy

#### 题目

在现有的 Namespace “my-app” 中创建一个名为 “allow-port-from-namespace” 的新 NetworkPolicy。确保新的 NetworkPolicy 允许 Namespace “echo” 中的 Pods 连接到 namespace “my-app” 中的 Pods 的 9000 端口。

进一步确保新的 NetworkPolicy：不允许对没有在监听端口 9000 的 Pods 的访问，不允许非来自 Namespace “echo” 中的 Pods 的访问。

#### 答题要点

这道题主要考创建网络策略 NetworkPolicy，知识点参考专栏 [第 14 课](https://time.geekbang.org/column/article/796302)。

做这道题一定要理解题目。首先要搞清楚谁是访问来源 Pod，谁是被访问的 Pod，从题目中可以得知 echo 命名空间中的 Pod 是访问者，my-app 命名空间中的 Pod 是被保护的 Pod，所以网络策略要创建在 my-app 命名空间中。其次，题目最后两句话的意思是，仅允许访问端口为 9000，仅允许 echo 命名空间中的 Pod 访问。

所以我们要创建一个 my-app 命名空间中的网络策略，用来保护该命名空间中的所有 Pod。其中定义 ingress 规则，使用 namespaceSelector 属性来筛选访问来源的 Pod。这里需要通过标签来选择命名空间，所以我们还需要给 echo 命名空间打个标签。然后定义 ports 属性来满足 9000 端口号的要求。

#### 参考答案

1. 给 echo 命名空间打个标签 “ns=echo”。

```bash
kubectl label ns echo ns=echo

```

2. 按照题目要求，编写网络策略的 YAML 文件（networkpolicy.yaml）。

**注意：如果记不住 YAML 文件，可以点击考试题目提供的官方技术文档，通常可以在文档里找到相关的 YAML 文件，拷贝内容过来修改一下就行。所以你平时写 YAML 文件时就要学会从官方文档上拷贝模板过来修改。**

```yaml
# networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-port-from-namespace
  namespace: my-app
spec:
  podSelector: {} # 被保护 Pod 为命名空间下所有 Pod
  policyTypes:
   - Ingress
  ingress:
    - from: # 入方向允许流量策略
      - namespaceSelector:
          matchLabels:
            ns: echo   # 通过标签匹配访问来源 Pod 的命名空间
      ports:
        - protocol: TCP
          port: 9000    # 访问端口

```

3. 应用策略

```bash
kubectl apply -f networkpolicy.yaml

```

#### 验证

这道题可以通过 “kubectl describe” 命令来查看部署后的网络策略详情是否满足题目要求。

```bash
[root@k8s-master ~]# kubectl describe networkpolicy allow-port-from-namespace -n my-app
Name:         allow-port-from-namespace
Namespace:    my-app
Created on:   2024-06-18 23:28:09 +0800 CST
Labels:       <none>
Annotations:  <none>
Spec:
  PodSelector:    <none> (Allowing the specific traffic to all pods in this namespace)
  Allowing ingress traffic:
    To Port: 9000/TCP
    From:
      NamespaceSelector: ns=echo
  Not affecting egress traffic
  Policy Types: Ingress

```

## 第四题 Service

#### 题目

请重新配置现有的 Deployment “front-end” 以及添加名为 “http” 的端口规范来公开现有容器 Nginx 的端口 80/tcp。创建一个名为 “front-end-svc” 的新 Service，以公开容器端口 “http”。配置此 Service，以通过各个 Pod 所在的节点上的 NodePort 来公开它们。

#### 答题要点

这道题考两个知识点：在 Deployment 中增加 Pod 容器的暴露端口，以及创建 NodePort 类型的 Service 暴露该端口。知识点参考专栏 [第 7 课](https://time.geekbang.org/column/article/794207) 和 [第 9 课](https://time.geekbang.org/column/article/794708)。

因为 Deployment 已经存在，所以需要使用 “kubectl edit” 命令直接对 Deployment 进行实时修改，编辑时会自动打开 vi 编辑器，你需要进入编辑模式，修改完成保存后立即生效。 **注意：** 不要写错属性层级，如果出错，可能会无法保存或者无法生效。

然后，Service 暴露现有的 Deployment 可以直接使用 “kubectl expose” 命令。

#### 参考答案

1. 编辑 Deployment，增加 ports 属性，修改部分如下图所示：

```plain
kubectl edit deployment front-end

```

![图片](https://static001.geekbang.org/resource/image/e1/cb/e186bc610b8b379302bf530847e026cb.png?wh=868x946)

2. 暴露对应端口。

```plain
kubectl expose deployment front-end --type=NodePort --port=80 --target-port=80 --name=front-end-svc

```

#### 验证

可以通过 “curl” 命令访问 Nginx，从而验证 Service 暴露端口是否成功。

```bash
[root@k8s-master ~]# kubectl get svc front-end-svc
NAME            TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
front-end-svc   NodePort   10.104.106.175   <none>        80:32280/TCP   6m52s
[root@k8s-master ~]# curl 10.104.106.175:80
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
......

```

## 第五题 Ingress

#### 题目

如下创建一个新的 nginx Ingress 资源：

- 名称：ping
- Namespace：ing-internal
- 使用服务端口 5678 在路径 /hello 上公开服务 hello

可以使用以下命令检查服务 hello 的可用性，该命令应返回 hello。

```bash
curl -kL <INTERNAL_IP>/hello

```

#### 答题要点

这道题主要考配置 Ingress 规则，知识点参考专栏 [第 10 课](https://time.geekbang.org/column/article/794715)。

题目中已经给出名称、命名空间、具体规则，你需要先查看一下 IngressClass，然后通过 YAML 文件编写 Ingress 规则即可。

#### 参考答案

1. 查看 IngressClass。

```bash
[root@k8s-master ~]# kubectl get ingressclass
NAME          CONTROLLER                     PARAMETERS   AGE
nginx         k8s.io/ingress-nginx           <none>       15d

```

2. 按照题目要求，编写 Ingress 的 YAML 文件（ingress.yaml）。

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ping
  namespace: ing-internal
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx    # 上一步查到的 ingressClass 名字
  rules:
  - http:
      paths:
      - path: /hello    # 路径
        pathType: Prefix
        backend:
          service:
            name: hello   # 后端service名称
            port:
              number: 5678  # Port

```

3. 应用策略。

```bash
kubectl apply -f ingress.yaml

```

#### 验证

题目中给出了验证方法，所以你最好用它提供的方法验证一下。

使用 “kubectl get ingress -n ing-internal” 命令查看 Ingress 的 IP 地址，即返回结果中的 ADDRESS，然后运行题目提供的 curl 命令，替换 <INTERNAL\_IP> 为 Ingress 的 IP 地址，测试结果是否返回 hello。 注意：创建 Ingress 后，需要等约 3 分钟后，才会获取到 IP 地址。

## 第六题 查看 CPU 消耗

#### 题目

通过 Pod label “name=cpu-loader”，找到运行时占用大量 CPU 的 Pod，并将占用 CPU 最高的 Pod 名称写入文件 /opt/KUTR000401/KUTR00401.txt（已存在）。

#### 答题要点

这道题主要考使用 “kubectl top” 命令查看 Pod 的 CPU 消耗，知识点参考专栏 [第 16 课](https://time.geekbang.org/column/article/797497)。

#### 参考答案

```bash
# 对 pod 消耗 CPU 排序，-l 指定 Pod 标签，-A 表示所有命名空间
kubectl top pod -l name=cpu-loader --sort-by=cpu -A
# 将 cpu 占用最多的 Pod 的名称写入文件
echo <查出来的 Pod 名称> > /opt/KUTR000401/KUTR00401.txt

```

#### 验证

通过 cat 命令查看一下文件中是否写入 Pod 名称。

```bash
cat /opt/KUTR000401/KUTR00401.txt

```

## 第七题 Pod 调度

#### 题目

按如下要求调度一个 Pod：

- 名称：nginx-kusc00401
- Image：nginx
- Node selector：disk=ssd

#### 答题要点

这道题主要考指定节点调度，知识点参考专栏 [第 6 课](https://time.geekbang.org/column/article/793925)。

通过 YAML 文件创建一个 Pod，设置 nodeSelector 属性。

#### 参考答案

1. 按照题目要求，编写 Pod 的 YAML 文件（pod.yaml）。

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-kusc00401
spec:
  nodeSelector:
    disk: ssd
  containers:
  - image: nginx
    name: nginx-kusc00401

```

2. 部署 Pod。

```bash
kubectl apply -f pod.yaml

```

#### 验证

1. 查看节点标签，找到标记了 “disk=ssd” 标签的节点。

```bash
kubectl get node --show-labels | grep 'disk=ssd'

```

2. 查看 Pod 是否调度到该节点上。

```bash
kubectl get pod nginx-kusc00401 -o wide

```

## 第八题 节点数量统计

#### 题目

检查有多少 nodes 已准备就绪（不包括被打上 Taint：NoSchedule 的节点），并将数量写入 /opt/KUSC00402/kusc00402.txt。

#### 答题要点

这道题主要考如何查看节点详情以及找到其中的 Taint 属性，并且了解 Linux 系统的常用命令。知识点参考专栏 [第 6 课](https://time.geekbang.org/column/article/793925)。

首先要找到准备就绪的节点，然后在这些节点中排除 “Taint：NoSchedule” 的节点，统计出数量后写在指定文件中。使用参考答案中 Linux 的管道命令可以快速把这些步骤串到一起，你最好理解并且记住这条命令，当然你也可以按照这个过程，挨个节点去手动统计，不过会比较耗时。

#### 参考答案

```bash
kubectl describe node $(kubectl get node | grep Ready | awk '{print $1}') |grep Taint | grep -vc NoSchedule
# kubectl get node | grep Ready | awk '{print $1}' 这是找到所有的准备就绪的节点，并输出节点名称
# kubectl describe node $(...) |grep Taint | grep -vc NoSchedule 这是逐个查看节点详情并排除"Taint：NoSchedule"之后统计数量

echo <查出来的数字> > /opt/KUSC00402/kusc00402.txt

```

#### 验证

通过 cat 命令查看一下文件中是否写入正确数量。

```bash
cat /opt/KUSC00402/kusc00402.txt

```

## 第九题 多容器 Pod

#### 题目

按如下要求调度一个 Pod：

- 名称：kucc8
- Containers：2 个
- Container 名称/ Images：
  - nginx
  - memcached

#### 答题要点

这道题主要考创建多容器的 Pod。知识点参考专栏 [第 5 课](https://time.geekbang.org/column/article/793385)，下面我给出参考答案。

#### 参考答案

1. 按照题目要求，编写 Pod 的 YAML 文件（two-containers.yaml）。

```yaml
# two-containers.yaml
apiVersion: v1
kind: Pod
metadata:
  name: kucc8
spec:
  containers:
  - image: nginx
    name: nginx
  - image: memcached
    name: memcached

```

2. 部署 Pod。

```bash
kubectl apply -f two-containers.yaml

```

#### 验证

查看 Pod 运行状态，READY 是否是2/2。

```bash
kubectl get pod kucc8

```

## **小结**

今天我给你讲了真题的上半部分，希望你一定要动手把命令和 YAML 文件都在电脑上敲一敲，多熟悉几遍。如果对上面的真题有任何问题，可以留言给我。