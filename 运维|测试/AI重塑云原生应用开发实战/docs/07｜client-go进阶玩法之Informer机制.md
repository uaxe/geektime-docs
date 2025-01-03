你好，我是邢云阳。

在上一节课中，我们讲解了 client-go 的四种客户端的功能与使用场景，并且介绍了 RestMapper 的用法。RestMapper 就像一个全国联网的警务平台一样，可以在仅提供资源名称 resource 的情况下，拿到资源的 GVK、GVR、scope 等等全部信息。一旦得到 GVR，我们便可以利用动态客户端与 Kubernetes 资源进行交互。

我们还知道，无论使用哪种客户端方式，本质还是通过 Rest API 的方式去请求目标 Kubernetes 集群的 API Server。这样就不可避免的会对 API Server 造成访问压力。幸好，官方提供了 Informer 机制，为我们解决了这个问题。

这套机制是对 List && Watch 做了封装，并加入了缓存等功能。在初始时可以将资源全部缓存到本地，并且之后可以通过监听增删改事件来更新缓存中的资源状态。这样，我们在做查询操作时，就可以从本地缓存中获取到最新资源状态，无需访问 API Server。

接下来，我们就从 Lsit && Watch 开始讲起，看看如何从实操角度，在我们的业务中利用起 Informer。

## List && Watch

List && Watch 是 Kubernetes 为我们提供的查询资源的两种方式。

List 意思是列出资源，是一个一次性的动作。就如同军训时，教官说：“立正！”，于是全体学员都会立正，保持不动了。而 Watch 代表观察，是一个持续的动作。就如同教官说：“都立正站好，我看看谁乱动！”此时教官就会持续观察着每一个学员的状态，每一个学员从静止到动的全过程都能尽收教官眼底。

我们可以通过 curl 的方式来体会一下二者的区别。

首先是 List。

```powershell
curl -k -H "Authorization: Bearer $TOKEN" $APISERVER/api/v1/namespaces/default/pods

```

把 `$TOKEN` 和 `$APISERVER` 换成你自己的。执行后效果如下：

![图片](https://static001.geekbang.org/resource/image/59/1f/5999d9979fd04084b24a53424d43061f.png?wh=617x412)

Kubernetes 会返回 default 命名空间下的 pod 列表。

接下来是 Watch。

```powershell
curl -v -k -H "Authorization: Bearer $TOKEN" $APISERVER/api/v1/namespaces/default/pods?watch=true

```

我在开头加了 -v 参数方便观察返回的 HTTP 头，在结尾加了 &watch=true，这样就使用了Watch 模式。执行后的效果如下：

![图片](https://static001.geekbang.org/resource/image/97/bc/973dbcf24a38ace905c855f3d0dbb3bc.png?wh=800x193)

![图片](https://static001.geekbang.org/resource/image/71/cd/7198eeb5a93c13a4774b1ced43e055cd.png?wh=707x130)

可以看到第一张图在返回头中，有一个 “Transfer-Encoding: chunked” 字段，这个字段在我们平时做 HTTP 分块下载功能时也会用到，它的效果是会将相关的资源卡住，于是就出现了第二张图的效果。这样当 default 命名空间下的 pod 发生变化时，Kubernetes 会将相关数据继续传给我们。

那既然有了 Watch 这种优秀机制了，我们是否能将 Watch 到的数据缓存下来，以便后续再 List资源时，可以不用再通过调用 API，而是直接在本地获取呢？

官方已经帮我们想到了这一点，并进行了稳定的实现。这就是位于 client-go cache 包中的 Informer。

## Informer

Informer 的设计初衷就是为了让 Client-go更快地返回List/Get请求的结果，减少对Kubenetes API 的直接调用。因此 Informer 被设计实现为一个依赖 Kubernetes List/Watch API、可监听事件并触发回调函数的二级缓存工具包。接下来，我们通过代码实践来体会一下。

### 目录结构与初始化

代码目录非常简单，根目录包含 pkg 文件夹，pkg 下面包含 config 与 handlers 两个文件夹，config 主要是做配置相关的代码，目前包含 k8sconfig.go，做 client 的初始化操作。handlers 是资源的事件处理方法，一会在代码中，便可以知道它的作用。最后我们在main.go中做测试。

```powershell
.
|-- pkg
| |-- config
| | |-- k8sconfig.go
| |-- handlers
| | |-- podhandler.go
|-- go.mod
|-- go.sum
|-- main.go

```

首先来看 client 的初始化，本节课，我对代码做了一个封装。代码如下：

```go
package config

import (
    "path/filepath"

    "github.com/pkg/errors"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/client-go/util/homedir"
)

type K8sConfig struct {
    *rest.Config
    *kubernetes.Clientset
    e error
}

func NewK8sConfig() *K8sConfig {
    return &K8sConfig{}
}

// 初始化k8s配置
func (k *K8sConfig) InitRestConfig() *K8sConfig {
    kuebconfig := filepath.Join(homedir.HomeDir(), ".kube", "config")
    config, _ := clientcmd.BuildConfigFromFlags("", kuebconfig)

    k.Config = config

    return k
}

func (k *K8sConfig) Error() error {
    return k.e
}

// 初始化clientSet客户端
func (k *K8sConfig) InitClientSet() *kubernetes.Clientset {
    if k.Config == nil {
        k.e = errors.Wrap(errors.New("k8s config is nil"), "init k8s client failed")
        return nil
    }

    clientSet, err := kubernetes.NewForConfig(k.Config)
    if err != nil {
        k.e = errors.Wrap(err, "init k8s clientSet failed")
        return nil
    }
    return clientSet
}

```

代码封装是借鉴了面向对象编程的思想，创建了一个结构体，包含 restConfig、clientSet 以及用于处理错误的 error。

通过类似构造函数的 NewK8sConfig 创建结构体实例，通过 InitRestConfig 获取 K8s 配置，通过 InitClientSet 获取 clientSet客户端。三个函数都是返回自己，这样在写代码时可以形成链式调用的效果。就像这样：

```go
clientSet := config.NewK8sConfig().InitRestConfig().InitClientSet()

```

### Informer

在 client-go 中 Informer 分为好几种不同的功能模型。包括最基础的一个资源一个连接的 Informer，多资源共享连接的 sharedInformer 以及工厂模式的 sharedInformerFactory 等。我们一个个介绍，先来看基础款的 Informer，代码很简单。

```go
client := config.NewK8sConfig().InitRestConfig().InitClientSet()

lw := cache.NewListWatchFromClient(client.CoreV1().RESTClient(), "pods", "default", fields.Everything())

options := cache.InformerOptions{
        ListerWatcher: lw,
        ObjectType:    &v1.Pod{},
        ResyncPeriod:  0,
        Handler:       &handlers.PodHandler{},
    }

_, informer := cache.NewInformerWithOptions(options)

informer.Run(wait.NeverStop)

select {}

```

在创建了 clientSet 客户端后，需要通过 NewListWatchFromClient 初始化一个 ListWatch。参数很简单，第一个参数是一个 restClient 客户端，第二个参数是要监听的 resource，第三个是命名空间，第四个是标签过滤器，如果不过滤标签，则填写fields.Everything()。

之后就可以通过 cache.NewInformerWithOptions 构建 Informer了。我使用的 client-go 版本是 v0.31.2，在之前的一些版本中，比如 v0.26 以前的版本，是使用 cache.NewInformer 来创建 Informer。这两者，功能没有任何区别，只是入参的形式不一样，cache.NewInformerWithOptions 是把入参封装成了结构体的形式，这样方便后续扩展参数，增加设计的灵活性。

cache.InformerOptions 需要填写的共四个参数，第一个是 ListWatch，第二个是监听的对象实例，第三个是同步周期，填 0 即可，第四个是我们要重点讲解的事件处理 handler。

客户端在监听资源对象时，实际上监听的是增删改这三类事件。Informer 提供了添加自定义事件回调函数的功能，即 Handler。Handler 的类型如下图所示，是一个接口，包含了 Add、Update、Delete 三类方法，我们只需要实现下图所示的三个方法，便可以实现增删改三类事件的回调。

![图片](https://static001.geekbang.org/resource/image/0c/e5/0cf3101726193ac72e58f1268d792fe5.png?wh=592x145)

我在 handlers 文件夹下的 podhandler.go 中实现了针对这三个事件的回调，代码如下：

```go
package handlers

import (
    "fmt"

    v1 "k8s.io/api/core/v1"
)

type PodHandler struct {
}

func (h *PodHandler) OnAdd(obj interface{}, isInInitialList bool) {
    fmt.Println("PodHandler OnAdd: ", obj.(*v1.Pod).Name)
}

func (h *PodHandler) OnUpdate(oldObj, newObj interface{}) {
    fmt.Println("PodHandler OnUpdate: ", newObj.(*v1.Pod).Name)
}

func (h *PodHandler) OnDelete(obj interface{}) {
    fmt.Println("PodHandler OnDelete: ", obj.(*v1.Pod).Name)
}

```

为了演示简单，我没有在事件中做任何事情，只打印了资源名称。

在完成回调注册后，便可以使用 informer.Run(wait.NeverStop) 来启动 Informer，wait.NeverStop 是一个管道操作，用来阻塞住协程不要退出。因此，由于 Informer 是基于协程的，在主程序中，还需要写一个 select{}，来将主程序卡住，避免 Informer 还未启动好，主程序就结束退出了。

我们来看一下程序运行效果。

首先，在我的集群的 default NS 下，只有一个pod。

![图片](https://static001.geekbang.org/resource/image/0b/df/0bdb1218523fa2de887f77ca98e7a2df.png?wh=678x72)

我们运行程序后，可以看到，在 Add 事件回调中，打印出该 pod 的名字。

![图片](https://static001.geekbang.org/resource/image/3c/61/3c8c367a37f295f542a70b99a1c01561.png?wh=804x76)

此时，我们再创建一个 pod。

![图片](https://static001.geekbang.org/resource/image/71/f0/7124701319a993452b7c53979008e8f0.png?wh=802x180)

可以看到，监听到了 Add 和 Update 事件，并触发了对应的回调。

这种基础的 Informer 只能绑定一个 Handler。假设对于 pod 的监听事件，我们想创建两套 Handler，分别在回调中处理不同的业务，此时就只能创建两个 Informer 来分别绑定。这样相当于与 API Server 建立了两条链路，加大了资源开销。于是 client-go 中，又提供了 SharedInformer 的概念。

### SharedInformer

SharedInformer 可以理解为是共享链路的 Informer，它可以针对一个监听资源，添加多个 Handler，我们来看一下代码。

```go
type NewPodHandler struct {
}

func (h *NewPodHandler) OnAdd(obj interface{}, isInInitialList bool) {
    fmt.Println("NewPodHandler OnAdd: ", obj.(*v1.Pod).Name)
}

func (h *NewPodHandler) OnUpdate(oldObj, newObj interface{}) {
    fmt.Println("PodHandler OnUpdate: ", newObj.(*v1.Pod).Name)
}

func (h *NewPodHandler) OnDelete(obj interface{}) {
    fmt.Println("PodHandler OnDelete: ", obj.(*v1.Pod).Name)
}

```

首先，我们在 podhandler.go 中，新加一个 NewPodHandler。之后，SharedInformer 这样写：

```go
client := config.NewK8sConfig().InitRestConfig().InitClientSet()

lw := cache.NewListWatchFromClient(client.CoreV1().RESTClient(), "pods", "default", fields.Everything())

sharedInformer := cache.NewSharedInformer(lw, &v1.Pod{}, 0)
sharedInformer.AddEventHandler(&handlers.PodHandler{})
sharedInformer.AddEventHandler(&handlers.NewPodHandler{})
sharedInformer.Run(wait.NeverStop)

select {}

```

SharedInformer 相比 Informer 多了一个 AddEventHandler 方法，我们可以多次使用该方法来添加多个 Handler。最后看一下效果。

![图片](https://static001.geekbang.org/resource/image/27/70/272cdd14e0eb8619c76c21e138118a70.png?wh=797x95)

可以看到，启动后，两个 Handler 的 Add 回调都被触发了。

测试到这，可能很多同学还有新的需求，那就是，我们能否让监听的多个资源共享一条链路呢？答案是有的，下面要讲的 SharedInformerFactory 就可以满足我们的需求。

### SharedInformerFactory

SharedInformerFactory 从命名来看，它是 SharedInformer 的一个工厂，也就是说在工厂里有很多生产线，可以生产监听不同资源的 SharedInformer，但最后这些产品想要出厂，则必须经过工厂大门，因此它们是共享同一个大门的（链路）的。

了解了 SharedInformerFactory 的作用后，我们还是回到代码实践上。

首先，为了演示多资源，我们再新建一个 Service Handler，用于做 Service 资源的事件回调。

```go
package handlers

import (
    "fmt"

    v1 "k8s.io/api/core/v1"
)

type ServiceHandler struct {
}

func (h *ServiceHandler) OnAdd(obj interface{}, isInInitialList bool) {
    fmt.Println("ServiceHandler OnAdd: ", obj.(*v1.Service).Name)
}

func (h *ServiceHandler) OnUpdate(oldObj, newObj interface{}) {
    fmt.Println("ServiceHandler OnUpdate: ", newObj.(*v1.Service).Name)
}

func (h *ServiceHandler) OnDelete(obj interface{}) {
    fmt.Println("ServiceHandler OnDelete: ", obj.(*v1.Service).Name)
}

```

之后开始写 SharedInformerFactory 代码。

```go
client := config.NewK8sConfig().InitRestConfig().InitClientSet()

lw := cache.NewListWatchFromClient(client.CoreV1().RESTClient(), "pods", "default", fields.Everything())

fact := informers.NewSharedInformerFactoryWithOptions(client, 0, informers.WithNamespace("default"))

podInformer := fact.Core().V1().Pods()
podInformer.Informer().AddEventHandler(&handlers.PodHandler{})

svcInformer := fact.Core().V1().Services()
svcInformer.Informer().AddEventHandler(&handlers.ServiceHandler{})

fact.Start(wait.NeverStop)

```

可以看到，在代码中，创建了pod 和 svc 两个 Informer，并使用同一个 fact 完成了启动监听。看一下运行效果：

![图片](https://static001.geekbang.org/resource/image/a3/7b/a3dc123fe48cefcede7ab5660bb6277b.png?wh=813x171)

可以看到两个资源的回调都被触发了。

在上面的代码中，我们一直在演示 Watch，接下来，我们演示一下 Lister。先看代码：

```go
fact := informers.NewSharedInformerFactoryWithOptions(client, 0, informers.WithNamespace("default"))

podInformer := fact.Core().V1().Pods()
podInformer.Informer().AddEventHandler(&handlers.PodHandler{})

ch := make(chan struct{})
fact.Start(ch)
fact.WaitForCacheSync(ch)

podlist, _ := podInformer.Lister().List(labels.Everything())

fmt.Println(podlist)

```

在学习前面的理论时，我们知道 Informer 的 List 操作是在本地缓存中完成，因此上面的代码中，fact 的启动做了一点修改，加了一个 fact.WaitForCacheSync 方法，用于等待本地缓存的数据完成同步。否则在调用 List 的时候，很有可能返回的是空值。

缓存同步好后，直接使用第 10 行的代码，即可完成 List 操作。看一下实际效果：

![图片](https://static001.geekbang.org/resource/image/cc/43/ccb21015316aefca4202e20509d4d843.png?wh=1388x247)

可以看到 List 操作成功返回了 pod 列表。

最后介绍一下，SharedInformerFactory 通过 GVR 来创建 Informer。还是先上代码：

```go
fact := informers.NewSharedInformerFactoryWithOptions(client, 0, informers.WithNamespace("default"))

gvr := schema.GroupVersionResource{
    Group:    "",
    Version:  "v1",
    Resource: "pods",
}

informer, err := fact.ForResource(gvr)
if err != nil {
    panic(err)
}
informer.Informer().AddEventHandler(&cache.ResourceEventHandlerFuncs{})

ch := make(chan struct{})
fact.Start(ch)
fact.WaitForCacheSync(ch)

list, _ := informer.Lister().List(labels.Everything())

fmt.Println(list)

```

可以看到，在创建 Informer 时，可以使用 ForResource 方法进行创建。在设置监听事件时，你可以像之前的代码一样，传入具体的 Handler。但由于在这里，我用不到事件回调，我只是想用 Informer 的 List 功能，因此也可以像我一样传入 &cache.ResourceEventHandlerFuncs{} 这样一个空的 Handler。最后看一下效果：

![图片](https://static001.geekbang.org/resource/image/0c/bd/0c40a2e370f705c8f710yycddf587cbd.png?wh=1390x146)

可以看到，效果和之前是一样的。

## 总结

本节课，我讲述了 client-go 的另一种进阶玩法——Informer 机制。并从什么是 List && Watch 开始，使用代码为你演示了普通 Informer、进阶版的 SharedInformer 以及高阶版的 SharedInformerFactory的区别。我在课程中展示的代码，已经上传到了 GitHub，链接为： [https://github.com/xingyunyang01/Geek/tree/main/watch](https://github.com/xingyunyang01/Geek/tree/main/watch)

![图片](https://static001.geekbang.org/resource/image/cd/84/cdc6544313b1d03a0915yyff66df0f84.jpg?wh=1920x1116)

下面我用一张图，为你总结了一下今天的知识。在图中，最底层的是 Informer，对于单资源，如果想使用多个 Handler，需要创建多个 Informer。SharedInformer 解决了这一点，它允许一个资源绑定多个 Handler。而 SharedInformerFactory 在这个基础上又做了升级，它可以监听多个资源。不得不感叹，Kubernetes 在减轻 API Server 访问压力这一块的设计真的费心了。

讲到这里，再为你补充一点课外知识。在类似 Kubernetes 资源管理系统的前后端分离架构中，使用 REST API 进行通信时，Informer 机制可以结合 WebSocket 技术，实现前端资源列表的动态刷新。例如，当用户打开 Pod 列表页面时，如果底层 Kubernetes 集群中的某个 Pod 被删除，页面会自动更新显示最新状态，无需用户手动刷新。这种设计显著提升了数据同步的实时性和用户体验的流畅度。

这一方面得益于 Informer Watch 机制，能实时获取资源的最新状态，另一方面得益于 WebSocket 的全双工通信机制。使用 WebSocket 建立客户端和服务器之间的连接后，可以由服务器主动向客户端发送消息，因此当资源状态发生变化后，可以通知前端更新显示。

## 思考题

SharedInformerFactory 可以使用 GVR 来创建 Informer，那我们是否能够结合上一小节的 RestMapper，实现当用户传入 resource = pods 时，创建出监听 pod 的 Informer 呢？

欢迎你在留言区展示你的思考和测试结果，我们一起来讨论。如果你觉得这节课的内容对你有帮助的话，也欢迎你分享给其他朋友，我们下节课再见！