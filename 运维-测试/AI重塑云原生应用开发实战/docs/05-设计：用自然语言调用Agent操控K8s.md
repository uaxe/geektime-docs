你好，我是邢云阳。

在上一章中，我们深入探讨了 Function Calling 和 AI Agent 的原理，并通过 Go 语言实践了 ReAct Agent。在操作之后，你可能发现，看似复杂的 Agent 实际上只是将人类的工作经验传授给大模型，使其能够代替我们完成任务，理解起来并不困难。更为简单的是，在实际操作中，我们只需要设计出一套优质的 prompt 模板，就能完成 Agent 应用开发的一半工作，真是应了那句话：得 prompt 者得天下！

既然我们的课程主题是 AI + 云原生应用开发，那么接下来的两章，我将带领你通过 Agent 与 Kubernetes（K8s）进行实际操作与应用。本章我们将聚焦如何用自然语言来控制 Kubernetes，在下一章，我们再进一步探讨 Kubernetes 的智能运维。

## 传统的 Kubernetes 交互方式

众所周知，与 Kubernetes 交互的方式主要有以下几种：

- **kubectl 命令行**

Kubectl 是官方提供的命令行工具，用于与 Kubernetes 集群进行交互。比如要获取 default 命名空间下的 Pods 信息，命令如下：

```powershell
root@hi-test:~# kubectl get po
NAME                       READY   STATUS    RESTARTS   AGE
ng-test-7bdff759b9-r49jj   1/1     Running   0          13d

```

这种方式是用户最常使用的。

- **SDK**

Kubernetes 官方还提供了客户端 SDK，让程序员可以通过编程接口与 Kubernetes 交互。由于 Kubernetes 是用 Go 语言编写的，因此最流行的 SDK 是 client-go。以下是通过 client-go 列出 default 命名空间下 Pods 的示例代码：

```go
package main

import (
    "context"
    "fmt"
    "log"

    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
)

func main() {
    // 加载kubeconfig文件以获取客户端配置
    config, err := clientcmd.BuildConfigFromFlags("", "/root/.kube/config")
    if err != nil {
        log.Fatal(err)
    }

    // 创建Kubernetes客户端
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }

    // 列出default命名空间下的Pods
    pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{})
    if err != nil {
        log.Fatal(err)
    }

    // 遍历并打印Pod信息
    for _, pod := range pods.Items {
        fmt.Printf("Namespace: %v, Name: %v\n", pod.Namespace, pod.Name)
    }
}

```

运行结果如下：

```plain
Namespace: default, Nmae: ng-test-7bdff759b9-r49jj

```

- **GUI**

如果觉得命令行不够直观，用户还可以使用 Kubernetes 官方的 Dashboard 或类似 Kuboard 这样的图形化界面进行操作。如下图展示了 Kuboard 中一个 Deployment 资源的操作页面。

![图片](https://static001.geekbang.org/resource/image/f4/4c/f429afdd320af0037dc6a3c5abcb7f4c.png?wh=1920x797)

这种方式实现的原理相对简单，主要是基于前后端分离的架构设计，如下图所示：

![图片](https://static001.geekbang.org/resource/image/0a/3a/0a0fa4c9e76f397cb519a4ecf2c3703a.jpg?wh=1920x292)

前端 GUI 通过预设的 REST API 与后端服务器交互，后端服务器再通过 client-go 访问 Kubernetes，最终将结果返回前端展示在 GUI 上。

无论使用哪种方式，核心都是通过访问 Kubernetes 的 API server 来实现的。举个例子，我们可以用 curl 命令直接与 Kubernetes API 交互：

```go
curl -k -H "Authorization: Bearer xxxxxxxxxxxxxxxxxx" \
>      https://<your k8s server ip>:<your k8s server port>/api/v1/namespaces/default/pods

```

该命令返回的结果如下（由于篇幅原因，省略部分输出）：

![图片](https://static001.geekbang.org/resource/image/4e/84/4e2c246fe7e2f3edc3d297e5abe85384.png?wh=610x508)

Kubernetes 自引入国内已有 10 年之久，从最早只需掌握基本操作，到如今要求熟悉源码，技术要求日益提高。而上面提到的这些交互方式，已经成了程序员的基本功。作为技术从业者，紧跟时代变革至关重要。在 AI 时代，我们可以利用更加智能的方式与 Kubernetes 进行交互。

## 用自然语言操控 Kubernetes 原理与设计

在上一章，我们学习了 Function Calling 和 AI Agent，了解到大模型不仅能够选择合适的工具，还可以利用执行结果进行推理。本章将介绍如何用自然语言控制 Kubernetes。其原理并不复杂，只需将 kubectl 命令或通过 client-go 开发的函数封装成工具，供 Agent 选择执行即可，如下图所示：

![图片](https://static001.geekbang.org/resource/image/ba/b3/ba30da253eebdd58f77762cc9216dcb3.jpg?wh=1623x900)

接下来我们深入讨论如何使用自然语言操控 Kubernetes 的设计实现。从架构到细节，这将涉及 Cobra 命令行工具、API 设计、Prompt 模板、优化大模型输出以及合规性验证等多个方面。下面将为你介绍如何通过这些技术构建一个智能化的 Kubernetes 交互系统。

### Cobra 命令行工具

对于后端程序员来说，命令行是最熟悉不过的了，它可以让我们在没有前端的时候，也可以做测试或者发布独立应用。

那用什么方式编写命令行应用呢？既然是云原生课程，那就可以模仿 kubectl 这套优秀的命令行工具。通过阅读 kubectl 源码，我们可以得知，其使用的是 Cobra 库。

![图片](https://static001.geekbang.org/resource/image/0d/2f/0db95d31a026f0981c8425769d36642f.png?wh=1261x349)

实际上，Cobra 不仅 kubectl 在用，像是比较出名的包管理工具 Helm 等等也在使用，其已经成为了 Go 语言编写命令行工具的最佳实践。

### API 设计

在开篇词中，我提到过，在 AI 时代，API 将成为一等公民。在 GUI 时代，对于 K8s 资源管理系统，API 是前端网页客户端访问后端HTTP Server 的工具。而在 AI 时代，API 将会是 Agent 操作 K8s 的工具。之前聚合在一起为前端服务的 API 将会被打散，形成 “AI 微服务”的应用模式。因此我会以 Go 的 Gin 框架为例，一节课让你快速掌握 HTTP Server 开发。

### client-go 进阶用法

常规的用 client-go 增删改查资源，可能许多从事云原生研发的同学都会。例如用 clientSet 获取 Kubernetes 标准资源，用动态客户端获取 CRD 资源等等。但是在本场景中，用户的需求是不确定的，比如用户说：“我要获取 default 命名空间下的 pod 列表”或者“请帮我删除 default 命名空间下的名字叫 foo 的 service”。我们无法预判用户要操作什么 Kubernetes 资源。

因此对于增删改操作，比较好的方法是利用 restMapper 获取到用户待操作资源的 GVR 后，用动态客户端来进行操作，这样可以实现通用化。而对于查操作，用 restMapper 当然也很方便。但如果每一次都通过访问 apiserver 在 Kubernetes 集群拿资源的话，一方面是会对 apiserver 造成流量压力，另一方面是速度会比较慢，因此业界的另一种做法是通过 Informer 机制，将资源缓存到本地，之后的查询全都在缓存中获取。而 Informer 还带有 Watch 机制，可以监听 Add、Delete、Update事件，实时更新缓存内容。

我们会在后面两节课中，对这两种方式都做一下讲解，便于你在实际业务中根据需要自由选择合适的方法。

### 多集群管理

云原生发展到 2024 年，应该同学们都或多或少的听过或了解云边端多云混合管理这类概念。企业不仅需要管理不同的云环境，还要考虑边缘计算节点和本地基础设施的协同，确保数据流、应用部署和资源调度的高效性与一致性。这种跨云、跨地域、跨平台的管理需求对云原生架构提出了更高的挑战，同时也带来了新的机遇。

在这样的背景下，Karmada 作为一个开源的多集群管理工具，应运而生。Karmada 允许用户在多个 Kubernetes 集群之间实现资源的统一管理与调度，同时提供了高可用性和跨云环境的支持。它不仅帮助企业简化了多集群管理的复杂性，还可以优化资源的使用，提升系统的弹性和可靠性。

我们也会在用自然语言操控 Kubernetes 的项目中介绍和应用该工具。

### Prompt 设计

操控 Kubernetes 资源的增删改查中，创建（增）是最为复杂的环节。因为我们需要大模型根据需求生成 Kubernetes 资源 YAML 文件，来用于安装部署。然而，大模型生成的 YAML 文件是否符合要求，往往需要进一步验证和优化。为此，我们可以通过精心设计和调整 prompt 来规范生成内容，确保最终输出的 YAML 文件能够直接用于安装和操作。

如果我直接对通义千问大模型这样说：“我要创建一个k8s pod 镜像名称是nginx”。效果是这样的：

![图片](https://static001.geekbang.org/resource/image/3b/67/3b035e794d32e2b5a95bef777af06d67.png?wh=1182x546)

如图所示，大模型会在 YAML 之前，给出一段文字。我们先不讨论 YAML 内容是否正确以及是否满足我们的要求，仅 YAML 前的这段文字，就需要我们用代码去做数据清洗（删除），非常不便。

因此，我们可以通过优化 prompt 来让大模型仅输出 YAML。prompt 如下：

```plain
SYSTEM
您是一名虚拟 k8s（Kubernetes）助手，可以根据用户输入生成 k8s yaml。yaml 保证能被 kubectl apply 命令执行。

#Guidelines
- 不做任何解释，只输出命令行或 yaml 内容。

HUMAN
用户输入: {user_input}

```

我们再次通过通义千问测试：

![图片](https://static001.geekbang.org/resource/image/10/d0/10047d05b741bd30504a434a798256d0.png?wh=1218x612)

可以看到这一次，通义千问直接给出了 YAML。

我们在实际业务开发中，其实还可以给出更多的约束规则，来确保大模型生成的 YAML 符合业务需求。例如：

```plain
#key point
- 必须为 pod 设置名称和端口，如 80。
- pod 必须有资源，其中必须设置限制和请求。如果未指定，则设置为 512M。
- 必须根据业务系统设置 pod 名称。例如，订单系统的 pod 名称为 order-pod。如果未指定，默认名称为 unkown-pod。

```

我们再来测试一次：

![图片](https://static001.geekbang.org/resource/image/e4/57/e43f5a0bfdb09c486dd463a266094357.png?wh=1237x645)

可以看到，这一次的 YAML 完全是按照我们的要求来的。在实际业务中，这部分规则，我们既可以预先填充，也可以结合 RAG 等知识库，让大模型来帮我们填充。总之，这些规则是可定制的。

### 验证用户输入是否符合 Kubernetes 资源要求

实际上，在上一步生成 YAML 模板之前，我们还需要做一些验证工作，用于验证用户输入的 prompt 是否是在创建一个正确的资源。例如用户输入：“我要创建一个k8s hello，镜像是nginx”，很显然，在 K8s 中，没有一个资源叫 hello，因此需要 Agent 在这一步调用工具做验证。

那验证方式，其实也很简单，我们只需要通过验证 kind 是否是在当前集群的资源列表中即可。为何要强调当前集群，因为除了K8s 内置资源外，还有自定义资源 CRD。

### 人类工具

“删库跑路”是 IT 圈的著名黑话，我们都懂其意思。因此当我们做删除资源操作时，是否放心真的交给 Agent 去做，而不再最后确认一遍呢？肯定是不放心的。因此 LangChain 社区开发了一款特殊的工具 HumanTool。即当 Agent 判断某些危险操作需要人类确认时，会调用该工具来寻求人类帮助。我们会在后面的课程中，用 Go 语言复刻一下，试试效果如何。

## 总结

本节课我带你回顾了几种传统的和 Kubernetes 交互的方式，并解析了其中的原理。那么，在 AI 时代，与时俱进的我们必然要掌握用自然语言“命令行”来操控 Kubernetes，实际上这样的方式也在业界被称作 LUI（语言用户界面，Language User Interface）。

从原理上看，用自然语言操控 Kubernetes 并不复杂，就是借助 Agent 推理和调用工具的能力，来根据用户请求调用相应的工具，完成与 Kubernetes 的交互。但实际上，Agent 只是一个 Copilot，主体业务逻辑还需要我们来思考完善。

这节课，我提到了 kubectl 插件的设计，prompt 模板设计与资源验证，client-go 处理通用资源的方法设计以及人类工具等等，都会在后面的课程中详细介绍。

在生产上，对 Kubernetes 的操作是严肃的，我们只有不断完善业务逻辑和工具细节，才能真正放心的将如此重任交给 AI。

## 思考题

除了课程中列出的这些设计点，你还能想到哪些点子，能够提升我们这个软件的可用性和安全性吗？

欢迎你在留言区展示你的思考过程，我们一起探讨。如果你觉得这节课的内容对你有帮助的话，也欢迎你分享给其他朋友，我们下节课再见！