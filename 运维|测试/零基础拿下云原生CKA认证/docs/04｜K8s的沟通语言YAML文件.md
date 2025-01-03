你好，我是雪飞。

上一课我介绍了 K8s 的管理节点和工作节点上的组件，以及 K8s 丰富的资源对象，这些资源对象就像 K8s 给我们提供的工具包，满足了我们部署应用和管理集群的各种要求。有两种方式与这些资源对象打交道：一种是使用 kubectl 命令，另一种是使用 YAML 文件。它们分别对应着命令式与声明式这两种操作模式。

## 命令式与声明式

命令式操作就像是直接下达指令，比如告诉 K8s 创建或删除某个资源对象。这种方式很直接，但如果是多人同时操作或者频繁修改，就可能引发混乱，因为它不会记录所有的操作过程。

声明式操作则是向 K8s 说明对于某个资源对象你所期望达到的状态，使用 “kubectl apply” 命令让 K8s 读取文件并且自动将资源对象的当前状态变更为你所期望的状态。这种方式的好处在于，你可以随时查看声明文件，清晰地知道资源对象的期望状态，并可以通过修改文件来实现对资源对象的管理。

简单来说，命令式操作适合快速执行简单任务，而声明式操作则适合需要精细管理的复杂场景，特别是在团队协作和自动化部署中非常有用。K8s 鼓励使用声明式操作，因为这种方式更符合K8s 自动化和自我修复的设计哲学。

## YAML 文件的优势

YAML（YAML Ain’t Markup Language）文件就是 K8s 中最常用的声明式文件类型，CKA 考试中也会让你实际编写或者修改YAML 文件，从而完成对 K8s 资源对象的操作。使用 YAML 文件有这样几个优势。

首先，YAML 文件能够处理复杂的数据结构，比如嵌套的列表和字典。它允许在同一个文件中定义多个相互关联的资源对象，这使得 YAML 文件非常适合描述 K8s 资源对象的复杂关系。

其次，YAML 文件是纯文本格式，它的结构清晰，易于理解和编辑，这可以轻松地存储在如 Git 这种版本控制系统中，便于跟踪和管理文件的变更历史，这对于生产环境的应用部署维护至关重要。

最后，YAML 文件的可重用性和可共享性，使得在不同环境（如开发、测试和生产）间部署资源对象变得简单。你可以为每个环境定义不同的 YAML 文件，或者使用相同的文件但是覆盖特定的参数。

所以，使用 YAML 文件进行 K8s 的容器化应用部署是一种最佳实践，它提升了集群管理和应用部署的效率、可靠性及可维护性。接下来，我们看一下 YAML 文件的结构组成。

## YAML 文件语法

YAML 文件的结构是基于键值对的层级系统，通过缩进来表示数据之间的层次关系。下面我来简单介绍 YAML 文件的一些基本元素和规则。

### 键值对

YAML 文件由一系列的键值对 “key: value” 组成，其中键和值之间使用冒号（：）和空格进行分隔。键 key 是字符串类型，值 value 可以是基础数据类型，也可以是列表或字典这种复合类型。

### 基础数据类型

YAML 文件支持多种数据类型，包括字符串、整数、浮点数、布尔值（True 和 False）、空值（Null）等。字符串可以不使用引号，但如果包含特殊字符，则需要使用单引号或双引号，多行字符串可以使用 “\|” 和 “>” 符号连接。

### 缩进

YAML 文件中使用缩进来表示层级关系。通常，每个层级的缩进为两个空格。缩进格式非常重要，也很容易出错，你在写 YAML 文件时一定要多注意。例如：

```yaml
parent_key:
  child_key: child_value

```

### 列表

YAML 文件中的列表使用短横线（-）表示，每个列表项都在新的一行。列表项可以是简单的值，也可以是嵌套的结构。例如：

```yaml
list_key:
- item1
- item2
- sub_list:
  - sub_item1
  - sub_item2

```

### 嵌套结构

YAML 文件支持多层嵌套结构，可以通过增加缩进来表示。例如：

```yaml
nested_key:
  first_level:
    second_level: second_level_value
  another_first_level: another_second_level_value

```

### 注释与分割符

YAML 文件通常使用 “#” 号开头作为单行注释，使用 “—” 三个短横线作为分割多个文档。

这些 YAML 文件的语法是不是很简单呢？基本上你在写 K8s 的 YAML 文件时，记住这些写法就够了。

## K8s 中 YAML 文件组成

在 K8s 中，通过 YAML 文件来描述一个资源对象需要有固定的格式。其中包含了通用的常规属性（也称作字段），也包含不同类型资源对象所具有的特殊含义的属性。简单来说，K8s 的 YAML 文件中所涉及到 Key 都是事先定义好的，有的是通用的属性，也有定义不同类型资源对象所需要的属性。所以你需要熟悉这些属性，才能写好 K8s 的 YAML 文件。

一个典型的 K8s 资源对象的 YAML 文件包含以下几个通用属性：

- **apiVersion** **：** 定义要创建的资源对象对应使用的 API 的版本。这决定了 K8s 使用哪个 API 模式来解析文件中的属性。
- **kind** **：** 定义要创建的资源对象的类型，如 Pod、Service、Deployment 等。
- **metadata** **：** 提供关于要创建的资源对象的基本信息，如名称、命名空间、标签、注解等。
- **spec** **：** 描述要创建的资源对象的期望状态及相关特殊属性，如容器的镜像、端口配置、持久化卷声明等。

下面是一个简单的 Pod 资源对象的 YAML 文件（nginx-pod.yaml）示例， **YAML 文件后缀名可以使用 “.yaml ” 或 “.yml”。**

```yaml
# nginx-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
    - name: nginx-container
      image: nginx:latest # latest表示使用镜像的最新版本
      ports:
        - containerPort: 80

```

在这个例子中，apiVersion 指定了 Pod 使用的 API 是 v1 版本；kind 指定了要创建的资源对象是一个 Pod；metadata 里定义了 Pod 的名称是叫 nginx-pod，并且 Pod 有一个标签是 “app: nginx”；Spec 的部分描述了 Pod 的规格，即该 Pod 中要运行的容器名称是 nginx-container，容器镜像是 “nginx:latest”，容器暴露端口是 80 端口。

除了 Pod 之外，K8s 的其他资源对象（如 Deployment、Service、ConfigMap 等）也都是用类似的 YAML 文件格式进行定义和配置。看懂、能够手写并且能够修改 YAML 文件，这是 CKA 考试中的必备技能，所以你一定要上手去编写 YAML 文件，多敲几遍，多运行几次，基本上就能掌握了。

## 如何编写 YAML 文件

下面你就来自己动手编写一个 YAML 文件吧。在编写 K8s 的YAML 文件的过程中，有几个小技巧能帮你写出正确美观的 YAML 文件。我给你介绍一下。

### 查看资源对象的 apiVersion 和 kind

确定好要创建的资源对象类型之后，就需要查看它的 apiVersion 和 kind 属性，毕竟 YAML 文件的前两行就是这两个属性。你可以在终端窗口中输入 “kubectl api-resources” 命令，它能列出所有的 K8s 资源对象对应的缩写、API 版本、类型名称以及是否支持命名空间。

```yaml
[root@k8s-master ~]# kubectl api-resources
NAME                    SHORTNAMES   APIVERSION  NAMESPACED   KIND
bindings                             v1          true         Binding
componentstatuses       cs           v1          false        ComponentStatus
configmaps              cm           v1          true         ConfigMap
endpoints               ep           v1          true         Endpoints
events                  ev           v1          true         Event
limitranges             limits       v1          true         LimitRange
namespaces              ns           v1          false        Namespace
nodes                   no           v1          false        Node
persistentvolumeclaims  pvc          v1          true         PersistentVolumeClaim
persistentvolumes       pv           v1          false        PersistentVolume
pods                    po           v1          true         Pod
deployments             deploy       apps/v1     true         Deployment
.......

```

我对表头简单解释一下：

- **SHOTNAMES：** 资源对象缩写，可以用在 kubectl 命令中，例如，获取 Pod 信息的命令是 “kubectl get pod”，但是在上面返回信息中，可以看到 pods 资源对象的缩写是 po，那你就可以用 “kubectl get po” 来代替获取 Pod 信息的命令。
- **APIVERSION：** 资源对象对应的 API 的版本，也就是 YAML 文件中的 apiVersion 属性，写的时候一定要写完整 ，包含整个路径。
- **NAMESPACE：** 表示资源对象是否支持命名空间，命名空间 Namespace 是对资源对象的一种逻辑隔离方式，通过将资源对象划分到不同的命名空间中， 从而对它们进行分组管理。
- **KIND：** 表示资源对象的类型，也就是 YAML 文件中的 kind 属性。

### 查看资源对象属性含义

在 K8s 中，每个资源对象都会有一些自己的属性，例如：Pod 有 containers、image、ports 等属性，Deployment 有 replicas、selector、template 等属性，我们通过在 YAML 文件中使用这些属性来定义期望的资源对象状态。这些属性之间有着固定的嵌套关系，层级很深并且非常庞杂，很难全部记住它们。所以 K8s 也提供了 “kubectl explain” 命令来查看资源对象的属性介绍。通过返回结果，你可以快速了解这些属性以及用法。

```bash
[root@k8s-master ~]# kubectl explain pods.spec.containers
KIND:       Pod
VERSION:    v1

FIELD: containers <[]Container>

DESCRIPTION:
    List of containers belonging to the pod. Containers cannot currently be
    added or removed. There must be at least one container in a Pod. Cannot be
    updated.
    A single application container that you want to run within a pod.
......
  workingDir    <string>
    Container's working directory. If not specified, the container runtime's
    default will be used, which might be configured in the container image.
    Cannot be updated.

```

### 通过官方模板编写文件

怎样能写出好的 YAML 文件，最好的方式就是去查看 K8s 的 [官方技术文档](https://v1-28.docs.kubernetes.io/zh-cn/docs/home/)。官方文档上有大量YAML 文件模板，熟练掌握去官方文档上查找资料非常重要，因为 CKA 考试的时候虽然不能访问外网，但是是可以查阅官方文档，所以在考试中需要编写 YAML 文件，你就可以从官方文档中复制粘贴过来，然后修改一下，这样能保证考试时的效率和准确度。

![图片](https://static001.geekbang.org/resource/image/15/6e/15b7811e199450b88805e036f0a7716e.png?wh=2999x1523)

### 通过命令自动生成 YAML 文件模板

如果你没有现成的 YAML 文件模版，也可以使用 kubectl 命令快速生成模板。只需要在 kubectl 创建资源对象的命令后面加上 “–dry-run=client -o yaml” 参数就可以生成一个对应的 YAML 文件内容，然后就可以保存到文件中。“–dry-run=client” 表示不是真正创建资源对象，而是模拟执行；“-o yaml” 表示输出为 YAML 文件格式的内容。

例如：使用 “kubectl create” 命令创建 Deployment 的 YAML 文件模板。

```bash
kubectl create deployment my-nginx-deploy --image=nginx --dry-run=client -o yaml > my-nginx-deploy.yaml

```

在命令最后通过 “>” 符号把模板内容保存到 “my-nginx-deploy.yaml” 文件中。通过 “cat” 命令查看文件内容，就可以看到命令生成的 Deployment 的 YAML 文件内容。

```bash
[root@k8s-master cka-example-yaml]# cat my-nginx-deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: my-nginx-deploy
  name: my-nginx-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-nginx-deploy
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: my-nginx-deploy
    spec:
      containers:
      - image: nginx
        name: nginx
        resources: {}
status: {}

```

在这个 Deployment 的 YAML 文件中，有些属性字段没有用到（creationTimestamp、strategy、resources、status），可以删除这些属性，然后再按照你的要求修改这个模板文件就可以了。

所以编写 YAML 文件不用死记硬背，你平时多做积累总结，形成自己的或者团队的 YAML 文件模板库。用的时候只需要复制粘贴再做修改，就可以满足大多数的部署需求了。

### 编写 YAML 文件的注意事项

我总结了在编写 YAML 文件过程中的一些注意事项，希望能帮你更快地上手编写 YAML 文件。

- **多使用注释**，可以使用 “#” 对 YAML 文件注释，注释的语句不会执行，可以提高可读性和可维护性。
- **多个相关的资源对象可以写在一个 YAML 文件中同时部署**，使用 “—” 做分割，例如 Deployment 和 Service 通常是一起使用，就可以写到一个 YAML 文件中，部署的时候同时部署。
- 编写 YAML 文件一定要 **多注意文件格式**，比如层级关系缩进 2 个空格，冒号、逗号后缩进 1 个空格，注意这些小细节都能帮你写出正确美观的 YAML 文件。
- 建议你将 YAML 文件纳入版本控制系统，例如将 YAML 文件放到 GitHub 仓库，便于跟踪文件更改和历史记录。

## 如何使用 YAML 文件

编写完成 YAML 文件，就可以实际运行了，可以使用 “kubectl apply -f” 命令来运行 YAML 文件，从而部署文件中的资源对象。

```bash
kubectl apply -f <YAML文件名>

```

使用 “kubectl delete -f” 命令，可以删除 YAML 文件中所部署的全部资源对象。

```bash
kubectl delete -f <YAML文件名>

```

在正式应用 YAML 文件之前，可以使用 “kubectl apply -f  --dry-run” 命令验证文件格式和内容是否正确，此时 YAML 文件并不会真正执行，如果遇到错误可以去修改文件，确保文件的格式和语法都满足要求。

## **小结**

现在我们来简单回顾一下今天的内容。

我介绍了 K8s 中的两种操作方式——命令式和声明式。命令式就像是直接对电脑下命令，非常适合快速搞定一些简单的部署任务；而声明式更像是告诉电脑我们想要达到的最终状态，由它来自动实现我们的期望，这种方式特别适合应对那些复杂的项目，尤其是需要团队协作和自动化部署的场景。

接着，我们深入了解了 YAML 文件的语法结构，它是一种基于键值对的层级文件，支持多种数据类型以及复杂的数组和字典结构，它通过缩进表示嵌套层级，结构清晰，易于理解和编辑，成为 K8s 的应用程序部署的一种最佳实践。

在 K8s 中，通过 YAML 文件来描述一个资源对象需要有固定的格式。其中包含了通用的常规属性（也称作字段），也包含不同类型资源对象所具有的特殊含义的属性。常规属性包含 apiVersion、kind、metadata 以及 spec。不同资源对象的特殊含义的属性不太一样，需要你不断熟悉和积累。

然后，我还向你介绍了编写一个 K8s 资源对象的 YAML 文件的几个小技巧：通过 “kubectl api-resources” 命令查看资源对象的 apiVersion 和 kind 属性；通过 “kubectl explain” 命令来查看资源对象的属性介绍；通过官方技术文档中的模板编写YAML文件；以及通过 “kubectl” 命令来自动生成 YAML 文件模板。

最后，我们学习了使用 YAML 文件的两个命令，部署资源对象命令 “kubectl apply -f” 和删除资源对象命令“kubectl delete -f”。

## 思考题

这就是今天的全部内容，最后留一道练习题给你。

你在 K8s 的官方技术文档中找一个 Deployment 的 YAML 文件，直接拷贝到你的集群中，然后通过该 YAML 文件把它部署到你的集群中，部署完成后通过 “kubectl get deployment” 命令查看一下部署状态。

欢迎你把结果写到留言区。相信经过动手实践，会让你对知识的理解更加深刻。