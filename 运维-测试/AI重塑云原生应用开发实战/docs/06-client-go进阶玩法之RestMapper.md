你好，我是邢云阳。

在上一节课中，我们探讨了通过自然语言操控 Kubernetes 的基本原理，并分析了为了提升系统的可用性和安全性所需考虑的一些关键设计点，例如如何有效地使用 client-go。针对用户可能对任意 Kubernetes 资源进行操作的需求，我们引入了通用化的处理方案 RestMapper。同时，为了缓解查询操作对 apiserver 的访问压力，我们还提出了 Informer 方法。

在本节课中，我将重点介绍 RestMapper 的概念与应用。

为了照顾到对 client-go 不是太熟悉的同学，我们先从基础入手，讲解一下 client-go 四种客户端的使用手法以及 GVR、GVK 等概念。

## 四种客户端

在 client-go 中，有四种可以与 Kubernetes 资源进行交互的客户端，分别是 ClientSet、DynamicClient、DiscoveryClient 以及 RestClient，它们各自适用于不同的场景。下面结合代码来体会一下。

### ClientSet

ClientSet 是最常用的客户端，用于与 Kubernetes 核心资源（如 Pod、Service、Deployment 等）进行交互。它封装了对各类资源的操作，提供了类型安全的接口。我们用一个列出 default 命名空间下的 pod 列表的例子，看一下代码如何实现。

```go
package main

import (
    "context"
    "fmt"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

func main() {
    config, err := clientcmd.BuildConfigFromFlags("", "/path/to/kubeconfig")
    if err != nil {
        panic(err)
    }

    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        panic(err)
    }

    pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{})
    if err != nil {
        panic(err)
    }

    for _, pod := range pods.Items {
        fmt.Printf("Pod Name: %s\n", pod.Name)
    }
}

```

**GVK 与 ClientSet 的关系**

在示例代码中，clientset.CoreV1().Pods().List() 是用于获取 Pod 列表的方法。为什么是 CoreV1()？这与 Kubernetes 资源的 GVK 密切相关。

GVK 是 Group、Version 和 Kind 的缩写。

- **Group**：表示资源所属的 API 组，比如 apps、batch 等。

- **Version** **：** 表示资源的版本，比如 v1、v1beta1 等。

- **Kind** **：** 表示资源的类型，比如 Pod、Service 等，注意是大写字母开头的单数形式。


GVK 用于标识 Kubernetes 中的每种资源，也就是描述“身份”。例如，邢云阳的 Group 是人类，Version 比如就是出生日期，Kind 是邢云阳。

在资源的 YAML 中，我们也会用到GVK。以下是一个 pod 的 YAML：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx-container
    image: nginx
    ports:
    - containerPort: 80

```

- **apiVersion** **：** 是由 Group/Version 组合而成，由于 Pod 的 Group 为 Core（核心 API 组，Group 名为空），Version 为 v1，因此只写了 v1。

- **kind**：即为 Kind。


因此，在 ClientSet 中，Pod 的方法位于 CoreV1() 下，这是因为 Core API Group 的名称为空，直接使用 Version 表示。

我们再来看一下 deployment 的 YAML：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
...

```

- **apiVersion**：apps/v1，表示 Group 为 apps，Version 为 v1。

- **kind**：Deployment。


因此，若需要操作 Deployment 资源，可以通过 clientset.AppsV1().Deployments().List() 方法来获取 Deployment 列表。

**总结：** 只要知道目标资源的 GVK，就可以快速定位到对应的 ClientSet 方法。例如：

- Pod 的 GVK 为 v1、Pod，对应 clientset.CoreV1().Pods()。

- Deployment 的 GVK 为 apps/v1、Deployment，对应 clientset.AppsV1().Deployments()。


这种基于 GVK 的设计，使得 ClientSet 在操作 Kubernetes 核心资源时直观、简洁且高效。

### DynamicClient

DynamicClient 适用于操作未知类型的自定义资源（CRD）。它不需要强类型定义，是通过动态结构处理任意资源。我们还是举一个 list 的例子：

```go
package main

import (
    "context"
    "fmt"
    "k8s.io/client-go/dynamic"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/apimachinery/pkg/runtime/schema"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func main() {
    config, err := clientcmd.BuildConfigFromFlags("", "/path/to/kubeconfig")
    if err != nil {
        panic(err)
    }

    dynamicClient, err := dynamic.NewForConfig(config)
    if err != nil {
        panic(err)
    }

    gvr := schema.GroupVersionResource{
        Group:    "example.com",
        Version:  "v1",
        Resource: "myresources",
    }

    resources, err := dynamicClient.Resource(gvr).Namespace("default").List(context.TODO(), metav1.ListOptions{})
    if err != nil {
        panic(err)
    }

    for _, item := range resources.Items {
        fmt.Printf("Resource Name: %s\n", item.GetName())
    }
}

```

可以看到 DynamicClient 的核心就是要定义好 GVR，即Group、Version、Resource。

- **Group** **：** 同 GVK 的 Group。

- **Version** **：** 同 GVK 的 Version。

- **Resource** **：** 资源的复数形式，用于 HTTP 路径中的资源名称，例如 pods、services。


在上文中，我们描述了 GVK，其偏向于表示资源类型、身份。而 GVR 则表示怎么找到某资源。例如可以在“邢府”找到邢云阳，因此邢云阳的 Resource 是“邢府”。

在上一小节中，我们使用过如下 curl 命令列出pod list。

```go
curl -k -H "Authorization: Bearer xxxxxxxxxxxxxxxxxx" \
>      https://<your k8s server ip>:<your k8s server port>/api/v1/namespaces/default/pods

```

在 /api/v1/namespaces/default/pods 中，Version 是 v1，Resource 是 pods。这与 GVR 的结构完全一致，体现了动态客户端工作的基础。

DynamicClient 的灵活性在于，它不像 ClientSet 那样为每种资源类型定义固定接口，而是将资源的具体操作交由开发者定义。这种设计让我们能够更自由地操作各种资源，从而显著提升了与 Kubernetes 交互的灵活性和扩展性。

### RestClient

RestClient 听这个名字就与 RestAPI “沾边”，实际上，它还真“沾边”。RestClient 是直接通过 url 来访问资源，就如同上文的 curl。我们看一下代码实现：

```go
package main

import (
    "fmt"
    "k8s.io/client-go/rest"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func main() {
    config, err := clientcmd.BuildConfigFromFlags("", "/path/to/kubeconfig")
    if err != nil {
        panic(err)
    }

    restClient, err := rest.RESTClientFor(config)
    if err != nil {
        panic(err)
    }

    result := restClient.Get().
        AbsPath("/api/v1/namespaces/default/pods").
        Do(context.TODO())

    if result.Error() != nil {
        panic(result.Error())
    }

    pods := &metav1.PartialObjectMetadataList{}
    err = result.Into(pods)
    if err != nil {
        panic(err)
    }

    for _, pod := range pods.Items {
        fmt.Printf("Pod Name: %s\n", pod.Name)
    }
}

```

可以看到，RestClient 用了很 HTTP 的方法，通过 Get Method 以及 url 实现了交互。这种方法，我们用得比较少，如果要用，通常是使用了聚合API 技术，自定义了 API（除CRD之外，第二种自定义资源的方式）后，通过这种方式去调用。

### DiscoveryClient

DiscoveryClient 用于发现 Kubernetes 集群支持的 GVR，我们常用的 kubectl api-resources 命令就是使用它实现的。

![图片](https://static001.geekbang.org/resource/image/0b/2f/0b1062a8408797bf46629a52e3667d2f.png?wh=1363x310)

看一下，在代码中是如何使用 DiscoveryClient 的。

```go
package main

import (
    "fmt"
    "k8s.io/client-go/discovery"
    "k8s.io/client-go/tools/clientcmd"
)

func main() {
    config, err := clientcmd.BuildConfigFromFlags("", "/path/to/kubeconfig")
    if err != nil {
        panic(err)
    }

    discoveryClient, err := discovery.NewDiscoveryClientForConfig(config)
    if err != nil {
        panic(err)
    }

    apiGroups, err := discoveryClient.ServerGroups()
    if err != nil {
        panic(err)
    }

    for _, group := range apiGroups.Groups {
        fmt.Printf("API Group: %s\n", group.Name)
        for _, version := range group.Versions {
            fmt.Printf("  Version: %s\n", version.GroupVersion)
        }
    }
}

```

可以看到 DiscoveryClient 的用法还是很简单的，当然一般我们不这么用。我们通常会结合RestMapper，来实现 GVR 和 GVK 的转换。

## RestMapper

在讲完四种客户端之后，便可以来讲使用动态客户端 \+ RestMapper 进行所谓通用化的处理资源访问的方式了。

在上面使用客户端的过程中，我们知道使用动态客户端 DynamicClient 可以通过定义 GVR 来与 Kubernetes 资源做交互。但在用自然语言操控 Kubernetes 的场景中，用户肯定不会这样提问：“请帮我列出 default 命名空间下的 Group是 `""`，Version 是 v1，Resource 是 pods的列表”，而是会说：“请帮我列出 default 命名空间下的pod列表”。因此我们只能在用户的提问中得到 GVR 的 R 这一个信息。

为了应对这种场景，我们需要一种工具来帮助我们从资源名称（Resource）推导出完整的 GVR 信息，这就是 RestMapper。

RestMapper 是一个工具，用于解析和确定 Kubernetes 资源的元数据信息。它主要解决了两个问题：

- 资源类型到 API Group/Version 的映射：Kubernetes 支持多种 API 版本和组，不同的资源可能存在于不同的 API 组和版本中。RestMapper 可以帮助确定一个资源的具体 API 组和版本。

- 确定资源的操作方式：RestMapper 可以告诉客户端如何对资源进行增删改查等操作，例如资源的 URL 路径、是否支持命名空间等。


RestMapper 的返回值叫做 RestMapping，它包含了资源的详细信息：

- Group：资源所属的 API 组

- Version：资源的 API 版本

- Kind：资源的类型

- Scope：资源的作用范围（命名空间级别或集群级别）

- Resource：GVR

- Path：资源的 API 路径


其实，在生活中，也有类似的场景。例如我们只需要对警察报出身份证号，警察便可以通过警务平台工具得到我们的姓名、手机号、家庭住址等等全部信息。

OK，在讲完了概念后，我们还是以列出 pod 列表为例，看一下代码如何编写。

首先先定义出一个 restMapper。

```go
func InitRestMapper(clientSet *kubernetes.Clientset) meta.RESTMapper {
    gr, err := restmapper.GetAPIGroupResources(clientSet.Discovery())
    if err != nil {
        panic(err)
    }

    mapper := restmapper.NewDiscoveryRESTMapper(gr)

    return mapper
}

```

在第 2 行，restmapper.GetAPIGroupResources 的入参是一个 DiscoveryClient，其作用是通过 DiscoveryClient 来获取 Kubernetes 集群中所有 API 组和资源的信息。之后在第 7 行通过 restmapper.NewDiscoveryRESTMapper 可以获取一个真正的 RestMapper 工具实例。

有了 RestMapper 工具，我们就可以来做 Resource 到 GVR 的映射了。

```go
func mappingFor(resourceOrKindArg string, restMapper *meta.RESTMapper) (*meta.RESTMapping, error) {
    fullySpecifiedGVR, groupResource := schema.ParseResourceArg(resourceOrKindArg)
    gvk := schema.GroupVersionKind{}

    if fullySpecifiedGVR != nil {
        gvk, _ = (*restMapper).KindFor(*fullySpecifiedGVR)
    }
    if gvk.Empty() {
        gvk, _ = (*restMapper).KindFor(groupResource.WithVersion(""))
    }
    if !gvk.Empty() {
        return (*restMapper).RESTMapping(gvk.GroupKind(), gvk.Version)
    }

    return nil, nil
}

```

该函数的入参是 resourceOrKindArg 和 RestMapper 工具实例。resourceOrKindArg 的值有两种情况，第一种是 GVR 都存在的情况，例如：pod.v1 或者 deployment.v1.apps；第二种情况是只有 resource，例如：pod。

如果是第一种，第2行代码 schema.ParseResourceArg 会进行字符串切分操作，按.切分，将r.v.g 切分开，存入到类型为 \*schema.GroupVersionResource 的 fullySpecifiedGVR。如果是第二种，则将 Resource 赋值给类型为 schema.GroupResource 的 groupResource。

之后开始做判断，如果 fullySpecifiedGVR 有值，则直接调用 RestMapper 的 kindFor 方法，将 GVR 转成 GVK 就可以了。

那接下来，如果 GVK 是空的，说明刚才那一步没做，则也需要用 kindFor 获取 GVK 。但是由于 kindFor 需要的是 schema.GroupVersionResource 类型的入参，因此需要用groupResource.WithVersion( `""`) 这种方式将 schema.GroupResource 转为 schema.GroupVersionResource。WithVersion 在这里只起到了一个占位的作用。

在 GVK 获取到之后，便可以使用第 12 行的 restMapping 方法来获取到 restMapping 了。有了 restMapping，实际上 GVR 我们就已经拿到了。

之后的操作就很简单了，我们需要用动态客户端来 list 资源。

```go
if restMapping.Scope.Name() == "namespace" {
    ri = client.Resource(restMapping.Resource).Namespace(ns)
} else {
    ri = client.Resource(restMapping.Resource)
}

resources, err := ri.List(context.TODO(), metav1.ListOptions{})
if err != nil {
    panic(err)
}

for _, item := range resources.Items {
    fmt.Printf("Resource Name: %s\n", item.GetName())
}

```

用动态客户端 list 资源我们在上文中已经做过示例，在这里唯一要说的就是 restMapping.Scope 的用法。我们知道 Kubernetes 中的资源分为集群级别和命名空间级别两种，集群级别的相当于全局变量，不受命名空间的限制，例如 pv、clusterRole等资源；而命名空间级别的则是用命名空间进行隔离的，例如 pod、svc 等等。restMapping.Scope 存储了资源的级别，因此此处使用它做了判断。

## 总结

本节课，我们深入探讨了 client-go 四种客户端的使用场景以及原理，并为你讲述了 GVR 和 GVK 是什么。最后，我们结合用户实际使用场景，总结出用户通常只会提供 Resource 的名称，而不是 GVR 或 GVK 的全部内容，因此需要利用 RestMapper 工具，为 Resource 补全 Group 和 Version，从而实现通用化的与 Kubenetes 资源做交互的方法。

其实，通过这两节课的学习，你会发现，AI 的出现，确实革新了我们做应用开发的思路，让我们的产品能够变得更加智能，能够有更好的用户体验。但是，AI 也不是万能的，AI 自身存在的局限性以及幻觉等问题，使得现阶段，我们还是要通过编写一定量的业务代码，来配合 AI，帮助 AI，弥补 AI 的不足。因此，修炼好内功，才能让我们做出更好的 AI 产品。

## 思考题

在 mappingFor 函数中，resourceOrKindArg 参数的命名说明，我们的入参不只是 resource，还有可能是 kind。那如果入参是 kind，代码该如何编写呢？

欢迎你在留言区展示你的思考和测试结果，我们一起来讨论。如果你觉得这节课的内容对你有帮助的话，也欢迎你分享给其他朋友，我们下节课再见！