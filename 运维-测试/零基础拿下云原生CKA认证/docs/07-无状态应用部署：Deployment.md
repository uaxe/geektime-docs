你好，我是雪飞。

今天开始，我们进入到 K8s 中级篇。我会带你了解部署各类应用所需要的 K8s 资源对象，掌握这些资源对象的使用，你就能够为应用设计合适的部署方案，并在 K8s 集群中完整地部署应用。

这节课我带你了解一个非常重要的资源对象——Deployment，它适用于部署无状态应用。

## 认识 Deployment

之前介绍过无状态应用，简单来说，这类应用不管部署在哪里都可以独立完整的运行，所以无状态应用更易于扩展和维护。网站 Web 应用就是一种常见的无状态应用，可以同时部署多个 Web 应用，但是不管用户访问哪一个，得到的响应结果都一样。

Deployment 被设计用于同时部署和管理多个独立完整的 Pod，每个 Pod 里都运行相同的应用镜像，这正好对应着无状态应用的特点，所以说 Deployment 适合部署无状态应用。

Deployment 可以管理多个应用的 Pod 副本，最大的好处就是多个 Pod 一起工作，从而提高应用的处理能力。此外，即使部分 Pod 出现故障崩溃，其他 Pod 仍能继续运行，确保业务的持续可用。

举个生活中的例子，想象一下在火车站排队买票，起初只有一个售票窗口，当乘客增多时，单个售票员处理不过来，队伍就会变长，导致乘客等待时间增加。此时，如果开设多个售票窗口，乘客就会被分散到不同的窗口，加快了购票的速度。即使某个窗口的售票员临时离开，其他窗口依然可以继续服务，不会导致售票服务中断。在这个例子中，每个售票窗口就好比一个 Pod，而 Deployment 则负责管理这些窗口（Pod），确保服务的高效和稳定。

下面我们来动手部署一个 Deployment。

## 部署 Deployment

Deployment 有两种部署方式，使用 kubectl 命令和使用 YAML 文件。

### kubectl 命令部署

可以使用 “kubectl create” 命令创建 Deployment。

```bash
kubectl create deployment <deployment名称> --image=nginx --replicas=3

```

- **–image=nginx**：表示 Deployment 部署的 Pod 的容器镜像是 Nginx。
- **–replicas=3**：表示 Pod 副本数量为3个，即运行了 3 个 Pod，每个 Pod 的容器都使用 Nginx 镜像。

### YAML 文件部署

上述创建 Deployment 的命令等同于以下 YAML 文件（my-nginx-dep.yaml）。

```yaml
# my-nginx-dep.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-nginx-dep
spec:
  replicas: 3 # Pod 副本预期数量
  selector:   # 通过选择器来管理 Pod
    matchLabels:
      pod: my-nginx  # 要管理的 Pod 的标签
  template:   # 定义 Pod 的模板
    metadata:
      labels:
        pod: my-nginx # Pod 的标签
    spec:
      containers:
      - name: nginx
        image: nginx

```

- **apiVersion**：Deployment 的 apiVersion 值是 “apps/v1”。
- **replicas**：同 “kubectl create” 命令中的参数，用来设置 Pod 副本数量。
- **selector**：用来设置 Deployment 要管理的 Pod 的标签。Deployment 和它所管理的 Pod 之间是松散耦合的关系，Deployment 通过标签选择匹配的 Pod 来管理，因此，在 matchLabels 属性中指定的 “key: value” 标签必须与下面 Pod 模板 template 中的 labels 指定的 key: value 标签一致。
- **template**：用来定义 Pod 的模板，这样 Deployment 就可以从这个模板创建出 Pod。模板里面的属性与 Pod 的 YAML 文件中的 spec 部分非常相似，不再详细介绍。需要注意的是，在 Pod 模板中，我们不需要再为 Pod 定义名称，因为部署后 Deployment 会自动为这3个 Pod 分配名称。但是一定要记得给 Pod 添加标签 labels，而且要保证这个 labels 与 Deployment 中的 matchLabels 一致。

使用 “kubectl apply” 命令部署 Deployment 的 YAML 文件。

```bash
kubectl apply -f my-nginx-dep.yaml

```

### 查看部署结果

执行部署命令后稍等一会，因为 Deployment 需要同时部署 3 个 Pod，这要花费一点时间。然后我们使用 “kubectl get” 命令分别查看一下 Deployment 和 Pod 的运行情况。

```bash
[root@k8s-master ~]# kubectl get deployment
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
my-nginx-dep   3/3     3            3           39s

[root@k8s-master ~]# kubectl get pod
NAME                            READY   STATUS    RESTARTS       AGE
my-nginx-dep-5588cdb59b-bvzjx   1/1     Running   0              35s
my-nginx-dep-5588cdb59b-hbg2z   1/1     Running   0              35s
my-nginx-dep-5588cdb59b-qd7z4   1/1     Running   0              35s

```

返回结果中：

- **READY：** 表示运行的 Pod 数量，前面的数字是就绪数量，后面的数字是期望数量。
- **UP-TO-DATE：** 表示当前已经更新到最新状态的 Pod 数量。
- **AVAILABLE：** 表示健康状态的能够正常对外提供服务的 Pod 数量。

我们看到每个 Pod 的名称都是由 Deployment 的名称加上一个后缀组成。但是为什么后缀分为两段，第一段是相同的，而第二段则不同呢？这个问题将在稍后为你解答。

## 管理 Deployment

部署完 Deployment，就可以使用 kubectl 命令来管理 Deployment。在之前的课程中，我们已经使用过很多的 kubectl 命令，其实你可能已经发现很多命令是相同的，只是操作的资源对象类型或者资源对象名称不同，所以我在这里介绍一下通用的管理资源对象的命令，在后续介绍其他 K8s 资源对象时，就不再赘述这些基础的管理操作。

```bash
# 查看列表
kubectl get <资源对象类型> [-o wide] [-n <namespace名称>]

# 查看详情
kubectl describe <资源对象类型> <资源对象名称> [-n <namespace名称>]

# 通过 YAML 文件部署
kubectl apply -f <资源对象类型的YAML文件>

# 删除资源对象
kubectl delete <资源对象类型> <资源对象名称> [-n <namespace名称>]
kubectl delete -f <资源对象类型的YAML文件>

# 实时编辑资源对象，进入编辑器，保存后立即生效
kubectl edit <资源对象类型> <资源对象名称> [-n <namespace名称>]

```

**注意** **：**“-n <namespace名称> ” 表示如果资源对象属于某个命名空间，就要使用 -n 参数来指定命名空间名称，否则会提示找不到资源。

对于 Deployment ，只要将以上命令中的 <资源对象类型> 指定为 “deployment”，并将 <资源对象名称> 替换为具体部署的 Deployment 名称，就可以使用这些命令来管理 Deployment。

## Deployment 高级功能

了解了 Deployment 的基础用法，接下来通过两个场景让我们看看 Deployment 的高级功能。

### 水平扩缩容

你公司的应用通过 Deployment 部署了 3 个 Pod 副本，一直运行得挺稳定，刚才营销部同事说马上要搞一个优惠活动，预估会有大量访问，找你问问公司的应用能不能支撑住。这个时候，你只需要一个命令就能满足他的需求。这就需要用到 Deployment 的水平扩缩容功能。

Deployment 的水平扩缩容是指通过增加或减少 Pod 的副本数量来调整应用的并行处理能力，从而应对访问流量变化。所以当访问应用的流量大了，我们就增加 Pod 副本数量，提升并行处理能力；当访问应用的流量小了，我们就减少 Pod 副本数量，来节省资源消耗。

使用 “kubectl scale” 命令，可以方便地对 Deployment 指定新的副本数量。所以，对于营销部同事的要求，你大概估计了一下，可能需要 5 个 Pod 副本，这时，你只需要执行以下命令，就可以将 Pod 副本的数量扩充到了 5 个。（这里假设你公司的 Deployment 应用是我们上面部署的 my-nginx-dep）

```bash
[root@k8s-master ~]# kubectl scale deployment my-nginx-dep --replicas=5
deployment.apps/my-nginx-dep scaled

```

命令执行后，Scheduler 调度器会新调度两个同样应用的 Pod 副本。你可以通过 “kubectl get” 命令查看一下结果。

```bash
[root@k8s-master ~]# kubectl get deployment
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
my-nginx-dep   5/5     5            5           159m

[root@k8s-master ~]# kubectl get pod
NAME                            READY   STATUS    RESTARTS  AGE
my-nginx-dep-5588cdb59b-4l4zn   1/1     Running   0         26s
my-nginx-dep-5588cdb59b-bvzjx   1/1     Running   0         159m
my-nginx-dep-5588cdb59b-hbg2z   1/1     Running   0         159m
my-nginx-dep-5588cdb59b-qd7z4   1/1     Running   0         159m
my-nginx-dep-5588cdb59b-v8hww   1/1     Running   0         26s

```

现在 K8s 集群中已经有 5 个 Pod 副本在运行应用了，同事也可以放心的开始营销活动，等活动结束你可以同样使用 “kubectl scale” 命令并且设置参数 replicas 的数量为 3，从而释放掉不需要的 Pod 副本，实现缩容功能。

### 滚动更新

过了几天，研发部那边对应用做了新的功能迭代，发布了新的镜像，这个时候，就需要你对 Deployment 部署的应用 Pod 副本进行更新升级，同时要求你在升级的过程中还要保持业务能正常访问。这就需要用到 Deployment 的自动化的滚动更新功能。

Deployment 的滚动更新是指在更新应用版本时，旧版本的 Pod 会逐个被新版本的 Pod 替换，直到所有 Pod 都更新完毕。这种方式确保在更新过程中，始终有能够提供服务的应用 Pod，从而实现业务没有停机时间。

Deployment 具有版本概念，它与 YAML 文件中的 Pod 模板（template）内容相关，版本号实际上是 Pod 模板内容的 Hash 值。因此，当 Pod 中的镜像、配置、标签等发生变更时，都会形成新的 Deployment 版本并自动开始滚动更新。

最主要的版本升级场景是应用的镜像包更新。以下是修改 Deployment 的三种方式，只要修改了 Pod 中的应用镜像，就自动触发滚动更新过程。

```bash
# 通过修改 Deployment 的 YAML 文件，修改 Pod 使用的容器镜像，然后重新部署
kubectl apply -f my-nginx-dep.yaml

# 通过 "kubectl set" 命令修改 deployment 中 Pod 的容器镜像
kubectl set image deployment/my-nginx-dep nginx=nginx:1.26.0

# 通过 "kubectl edit" 命令，直接打开编辑器对 deployment 进行修改，保存立即生效
kubectl edit deployment/my-nginx-dep

```

这里介绍一下滚动更新的原理。滚动更新主要通过一个隐藏的 ReplicaSet 资源对象实现。实际上，Deployment 并不直接管理 Pod，而是通过 ReplicaSet 来管理 Pod。ReplicaSet 实际上负责管理多个副本的 Pod，每个 ReplicaSet 对应一个 Deployment 的版本。当 Deployment 升级时，会同时创建一个新版本的 ReplicaSet，新版本的 ReplicaSet 开始创建新的 Pod，而旧版本的 ReplicaSet 则开始删除旧的 Pod。

![图片](https://static001.geekbang.org/resource/image/f8/e0/f805d20259a36094b16b39583e48d2e0.jpg?wh=1021x436)

使用 “kubectl get replicaset” 命令来查看 ReplicaSet，可以看到 Deployment 确实自动生成了一个 ReplicaSet，而且你可以看到它的名称的后缀 “5588cdb59b”，就是刚才通过 Deployment 自动生成的 Pod 名称的第一段后缀（my-nginx-dep-5588cdb59b-bvzjx），这也说明了确实是 “Deployment -> ReplicaSet -> Pod” 这个关系。

```bash
[root@k8s-master ~]# kubectl get replicaset
NAME                      DESIRED   CURRENT   READY   AGE
my-nginx-dep-5588cdb59b   3         3         3       39m

```

假设你公司应用的 Deployment 是我们上面部署的 my-nginx-dep，之前业务镜像是 Nginx，默认为最新 Latest 版本，迭代功能后新发布的业务镜像是nginx:1.26.0，你就可以通过更新镜像的命令将 Nginx 的版本更新到 1.26.0。

```bash
[root@k8s-master ~]# kubectl set image deployment/my-nginx-dep nginx=nginx:1.26.0
deployment.apps/my-nginx-dep image updated

```

此时，我们查看 ReplicaSet，发现已经自动创建了两个 ReplicaSet，代表着新旧两个版本，旧版本后缀是 “5588cdb59b”，新版本后缀是 “84f5b57d87”。

```bash
[root@k8s-master ~]# kubectl get replicaset
NAME                      DESIRED   CURRENT   READY   AGE
my-nginx-dep-5588cdb59b   3         3         3       66m
my-nginx-dep-84f5b57d87   1         1         0       69s

```

我们还可以使用 “kubectl rollout status” 命令来查看滚动更新过程。在这个过程中，始终保持有 Pod 去对外提供服务，从而保证了更新时的应用的连续性。然而，这也意味着新旧两个应用会同时存在一段时间。

```plain
[root@k8s-master ~]# kubectl rollout status deployment my-nginx-dep
Waiting for deployment "my-nginx-dep" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "my-nginx-dep" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "my-nginx-dep" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "my-nginx-dep" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "my-nginx-dep" rollout to finish: 1 old replicas are pending termination...
deployment "my-nginx-dep" successfully rolled out

```

最终，通过 Deployment 的自动化的滚动更新功能，你只需要执行更新 Deployment 中 Pod 镜像的命令，就实现了不中断应用的更新需求。

**暂停和恢复滚动更新**

在部署过程中，如果发生特殊情况，可以使用以下命令暂停和恢复 Deployment 版本更新。

```bash
# 暂停更新
kubectl rollout pause deployment <deployment名称>

# 恢复更新
kubectl rollout resume deployment <deployment名称>

```

### 版本管理

在每次升级过程中，Deployment 都会生成一个新的版本，K8s 提供了相关的命令来查看和管理这些 Deployment 的版本。

**查看历史版本**

使用 “kubectl rollout history” 命令可以查看历史版本。

```bash
[root@k8s-master ~]# kubectl rollout history deployment my-nginx-dep
deployment.apps/my-nginx-dep
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

```

这里发现版本 REVISION 只是数字，而且 CHANGE-CAUSE 原因也没有说明，这样的展示结果不太友好。如果我们想在每次版本升级时增加一些说明，可以通过在 Deployment 的YAML 文件的 metadata 属性中添加 annotations 属性，用来增加注解信息。YAML 文件示例如下：

```yaml
...
metadata:
  name: my-nginx-dep
  annotations:
    kubernetes.io/change-cause: v1, 初始版本 # 可以在这里增加说明
...

```

这样部署 Deployment 之后，就可以在历史版本中查看到版本说明信息，方便我们了解每个版本的变更原因，非常友好。

```bash
[root@k8s-master ~]# kubectl rollout history deployment my-nginx-dep
deployment.apps/my-nginx-dep
REVISION  CHANGE-CAUSE
1         v1, 初始版本
2         v2, nginx=1.26.0

```

**版本回退**

如果在部署过程中遇到严重问题，可以使用版本回退功能。由于 Deployment 采用 ReplicaSet进行应用部署的版本管理，因此可以方便地回退到任意历史版本。回退过程与滚动更新相似，也能持续保持服务不间断，但是版本回退事实上并不是真的回到上一版本，而是会生成一个新的 Deployment 版本。

```bash
# 回滚上一个版本
kubectl rollout undo deployment <deployment名称>

# 回滚历史指定版本
kubectl rollout undo deployment <deployment名称> --to-revision=2

```

讲完了 Deployment 的高级功能，你是不是已经感受到它的强大。的确，在我们实际项目部署架构中，Deployment 是用得最多的应用部署方式，大量无状态应用（很多微服务应用也是无状态应用）都是使用 Deployment 部署到集群中。通过 Deployment 的多 Pod 副本、水平扩缩容、滚动更新等功能，保障了应用的高可用、可扩展和持续稳定。

## **小结**

今天，我介绍了 K8s 中的一个核心资源对象——Deployment。 Deployment 被设计用于同时部署和管理多个相同的 Pod，每个 Pod 里都运行相同的应用镜像，这些 Pod 独立运行在节点上，每个 Pod 就是应用的一个副本，所以它非常适合部署无状态应用。Deployment 部署多个Pod 的好处就是增加了业务的并发处理能力以及提供了高可用能力，确保应用更加稳定和连续。

接着我介绍了 Deployment 部署的两种方式，kubectl 命令和 YAML 文件部署，YAML 文件中的 replicas 属性用来指定 Pod 副本数量，selector 属性用来匹配要管理的 Pod 的标签，template 属性是 Pod 的内容模板。Deployment 和要管理的 Pod 是松散的关系，Deployment 是通过标签来选择要管理的 Pod，所以需要注意 YAML 文件中标签的对应匹配。然后我带你动手部署了 Nginx 镜像的 Deployment，并且整理了 K8s 中的一些常用命令。

最后，我通过两个场景给你介绍了 Deployment 的水平扩缩容和滚动更新这两个高级功能。水平扩缩容是指通过增加或减少 Pod 的副本数量来调整应用的并行处理能力，从而应对访问流量变化。而滚动更新是指在更新应用版本时，旧版本的 Pod 会逐个被新版本的 Pod 替换，直到所有 Pod 都更新完毕。这些功能都保障了业务的高可用和稳定性。

## 思考题

这就是今天的全部内容，这节课涉及到一个扩缩容的考点，所以今天练习题如下：

请你创建一个 Nginx 镜像的 Deployment， Pod 副本数为 3，然后通过 kubectl 命令把这个 Deployment 的 Pod 副本数扩容到 5 个。

相信经过动手实践，会让你对知识的理解更加深刻。