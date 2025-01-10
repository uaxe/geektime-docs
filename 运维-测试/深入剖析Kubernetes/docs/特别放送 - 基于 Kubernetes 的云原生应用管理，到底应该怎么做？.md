你好，我是张磊。

虽然《深入剖析 Kubernetes》专栏已经完结了一段时间了，但是在留言中，很多同学依然在不时地推敲与消化专栏里的知识和案例。对此我非常开心，同时也看到大家在实践 Kubernetes的过程中存在的很多问题。所以在接下来的一段时间里，我会以 Kubernetes 最为重要的一个主线能力作为专题，对专栏内容从广度和深度两个方向上进行一系列延伸与拓展。希望这些内容，能够帮助你在探索这个全世界最受欢迎的开源生态的过程中，更加深刻地理解到 Kubernetes 项目的内涵与本质。

随着 Kubernetes 项目的日趋成熟与稳定，越来越多的人都在问我这样一个问题：现在的 Kubernetes 项目里，最有价值的部分到底是哪些呢？

为了回答这个问题，我们不妨一起回到第13篇文章 [《为什么我](https://time.geekbang.org/column/article/40092) [们需要P](https://time.geekbang.org/column/article/40092) [od？》](https://time.geekbang.org/column/article/40092) 中，来看一下几个非常典型的用户提问。

> 用户一：关于升级War和Tomcat那块，也是先修改yaml，然后Kubenertes执行升级命令，pod会重新启动，生产也是按照这种方式吗？所以这种情况下，如果只是升级个War包，或者加一个新的War包，Tomcat也要重新启动？这就不是完全松耦合了？

> 用户二：WAR包的例子并没有解决频发打包的问题吧? WAR包变动后, geektime/sample:v2包仍然需要重新打包。这和东西一股脑装在tomcat中后, 重新打tomcat 并没有差太多吧?

> 用户三：关于部署war包和tomcat，在升级war的时候，先修改yaml，然后Kubernetes会重启整个pod，然后按照定义好的容器启动顺序流程走下去？正常生产是按照这种方式进行升级的吗？

在《为什么我们需要Pod？》这篇文章中，为了讲解 Pod 里容器间关系（即：容器设计模式）的典型场景，我举了一个“WAR 包与 Web 服务器解耦”的例子。在这个例子中，我既没有让你通过 Volume 的方式将 WAR 包挂载到 Tomcat 容器中，也没有建议你把 WAR 包和 Tomcat 打包在一个镜像里，而是用了一个 InitContainer 将 WAR 包“注入”给了Tomcat 容器。

不过，不同用户面对的场景不同，对问题的思考角度也不一样。所以在这一节里，大家提出了很多不同维度的问题。这些问题总结起来，其实无外乎有两个疑惑：

1. 如果 WAR 包更新了，那不是也得重新制作 WAR 包容器的镜像么？这和重新打 Tomcat 镜像有很大区别吗？
2. 当用户通过 YAML 文件将 WAR 包镜像更新后，整个 Pod 不会重建么？Tomcat 需要重启么？

这里的两个问题，实际上都聚焦在了这样一个对于 Kubernetes 项目至关重要的核心问题之上： **基于 Kubernetes 的应用管理，到底应该怎么做？**

比如，对于第一个问题，在不同规模、不同架构的组织中，可能有着不同的看法。一般来说，如果组织的规模不大、发布和迭代次数不多的话，将 WAR 包（应用代码）的发布流程和 Tomcat （Web 服务器）的发布流程解耦，实际上很难有较强的体感。在这些团队中，Tomcat 本身很可能就是开发人员自己负责管理的，甚至被认为是应用的一部分，无需进行很明确的分离。

而对于更多的组织来说，Tomcat 作为全公司通用的 Web 服务器，往往有一个专门的小团队兼职甚至全职负责维护。这不仅包括了版本管理、统一升级和安全补丁等工作，还会包括全公司通用的性能优化甚至定制化内容。

在这种场景下，WAR 包的发布流水线（制作 WAR包镜像的流水线），和 Tomcat 的发布流水线（制作 Tomcat 镜像的流水线）其实是通过两个完全独立的团队在负责维护，彼此之间可能都不知晓。

这时候，在 Pod 的定义中直接将两个容器解耦，相比于每次发布前都必须先将两个镜像“融合”成一个镜像然后再发布，就要自动化得多了。这个原因是显而易见的：开发人员不需要额外维护一个“重新打包”应用的脚本、甚至手动地去做这个步骤了。

**这正是上述设计模式带来的第一个好处：自动化。**

当然，正如另外一些用户指出的那样，这个“解耦”的工作，貌似也可以通过把 WAR 包以 Volume 的方式挂载进 Tomcat 容器来完成，对吧？

然而，相比于 Volume 挂载的方式，通过在 Pod 定义中解耦上述两个容器，其实还会带来 **另一个更重要的好处，叫作：自描述。**

为了解释这个好处，我们不妨来重新看一下这个 Pod 的定义：

```
apiVersion: v1
kind: Pod
metadata:
  name: javaweb-2
spec:
  initContainers:
  - image: geektime/sample:v2
    name: war
    command: ["cp", "/sample.war", "/app"]
    volumeMounts:
    - mountPath: /app
      name: app-volume
  containers:
  - image: geektime/tomcat:7.0
    name: tomcat
    command: ["sh","-c","/root/apache-tomcat-7.0.42-v2/bin/start.sh"]
    volumeMounts:
    - mountPath: /root/apache-tomcat-7.0.42-v2/webapps
      name: app-volume
    ports:
    - containerPort: 8080
      hostPort: 8001
  volumes:
  - name: app-volume
    emptyDir: {}

```

现在，我来问你这样一个问题： **这个 Pod 里，应用的版本是多少？Tomcat 的版本又是多少？**

相信你一眼就能看出来：应用版本是 v2，Tomcat 的版本是 7.0.42-v2。

**没错！所以我们说，一个良好编写的 Pod的 YAML 文件应该是“自描述”的，它直接描述了这个应用本身的所有信息。**

但是，如果我们改用 Volume 挂载的方式来解耦WAR 包和 Tomcat 服务器，这个 Pod 的 YAML 文件会变成什么样子呢？如下所示：

```
apiVersion: v1
kind: Pod
metadata:
  name: javaweb-2
spec:
  containers:
  - image: geektime/tomcat:7.0
    name: tomcat
    command: ["sh","-c","/root/apache-tomcat-7.0.42-v2/bin/start.sh"]
    volumeMounts:
    - mountPath: /root/apache-tomcat-7.0.42-v2/webapps
      name: app-volume
    ports:
    - containerPort: 8080
      hostPort: 8001
  volumes:
  - name: app-volume
    flexVolume:
      driver: "alicloud/disk"
      fsType: "ext4"
      options:
        volumeId: "d-bp1j17ifxfasvts3tf40"

```

在上面这个例子中，我们就通过了一个名叫“app-volume”的数据卷（Volume），来为我们的 Tomcat 容器提供 WAR 包文件。需要注意的是，这个 Volume 必须是持久化类型的数据卷（比如本例中的阿里云盘），绝不可以是 emptyDir 或者 hostPath 这种临时的宿主机目录，否则一旦 Pod 重调度你的 WAR 包就找不回来了。

然而，如果这时候我再问你：这个 Pod 里，应用的版本是多少？Tomcat 的版本又是多少？

这时候，你可能要傻眼了：在这个 Pod YAML 文件里，根本看不到应用的版本啊，它是通过 Volume 挂载而来的！

**也就是说，这个 YAML文件再也没有“自描述”的能力了。**

更为棘手的是，在这样的一个系统中，你肯定是不可能手工地往这个云盘里拷贝 WAR 包的。所以，上面这个Pod 要想真正工作起来，你还必须在外部再维护一个系统，专门负责在云盘里拷贝指定版本的 WAR 包，或者直接在制作这个云盘的过程中把指定 WAR 包打进去。然而，无论怎么做，这个工作都是非常不舒服并且自动化程度极低的，我强烈不推荐。

**要想 “Volume 挂载”的方式真正能工作，可行方法只有一种：那就是写一个专门的 Kubernetes Volume 插件（比如，Flexvolume或者CSI插件）** 。这个插件的特殊之处，在于它在执行完 “Mount 阶段”后，会自动执行一条从远端下载指定 WAR 包文件的命令，从而将 WAR 包正确放置在这个 Volume 里。这个 WAR 包文件的名字和路径，可以通过 Volume 的自定义参数传递，比如：

```
...
volumes:
  - name: app-volume
    flexVolume:
      driver: "geektime/war-vol"
      fsType: "ext4"
      options:
        downloadURL: "https://github.com/geektime/sample/releases/download/v2/sample.war"

```

在这个例子中， 我就定义了 app-volume 的类型是 geektime/war-vol，在挂载的时候，它会自动从 downloadURL 指定的地址下载指定的 WAR 包，问题解决。

可以看到，这个 YAML 文件也是“自描述”的：因为你可以通过 downloadURL 等参数知道这个应用到底是什么版本。看到这里，你是不是已经感受到 “Volume 挂载的方式” 实际上一点都不简单呢？

在明白了我们在 Pod 定义中解耦 WAR 包容器和 Tomcat 容器能够得到的两个好处之后，第一个问题也就回答得差不多了。这个问题的本质，其实是一个关于“ Kubernetes 应用究竟应该如何描述”的问题。

**而这里的原则，最重要的就是“自描述”。**

我们之前已经反复讲解过，Kubernetes 项目最强大的能力，就是“声明式”的应用定义方式。这个“声明式”背后的设计思想，是在YAML 文件（Kubernetes API 对象）中描述应用的“终态”。然后 Kubernetes 负责通过“控制器模式”不断地将整个系统的实际状态向这个“终态”逼近并且达成一致。

而“声明式”最大的好处是什么呢？

**“声明式”带来最大的好处，其实正是“自动化”**。作为一个 Kubernetes 用户，你只需要在 YAML 里描述清楚这个应用长什么样子，那么剩下的所有事情，就都可以放心地交给 Kubernetes 自动完成了：它会通过控制器模式确保这个系统里的应用状态，最终并且始终跟你在 YAML 文件里的描述完全一致。

这种 **“把简单交给用户，把复杂留给自己”** 的精神，正是一个“声明式”项目的精髓所在了。

这也就意味着，如果你的 YAML 文件不是“自描述”的，那么 Kubernetes 就不能“完全”理解你的应用的“终态”到底是什么样子的，它也就没办法把所有的“复杂”都留给自己。这不，你就得自己去写一个额外 Volume 插件去了。

回到之前用户提到的第二个问题：当通过 YAML 文件将 WAR 包镜像更新后，整个 Pod 不会重建么？Tomcat 需要重启么？

实际上，当一个 Pod 里的容器镜像被更新后，kubelet 本身就能够判断究竟是哪个容器需要更新，而不会“无脑”地重建整个Pod。当然，你的 Tomcat 需要配置好 reloadable=“true”，这样就不需要重启 Tomcat 服务器了，这是一个非常常见的做法。

但是， **这里还有一个细节需要注意**。即使 kubelet 本身能够“智能”地单独重建被更新的容器，但如果你的 Pod 是用 Deployment 管理的话，它会按照自己的发布策略（RolloutStrategy） 来通过重建的方式更新 Pod。

这时候，如果这个 Pod 被重新调度到其他机器上，那么 kubelet “单独重建被更新的容器”的能力就没办法发挥作用了。所以说，要让这个案例中的“解耦”能力发挥到最佳程度，你还需要一个“原地升级”的功能，即：允许 Kubernetes 在原地进行 Pod 的更新，避免重调度带来的各种麻烦。

原地升级能力，在 Kubernetes 的默认控制器中都是不支持的。但，这是社区开源控制器项目 [https://](https://github.com/openkruise/kruise) [github.com/open](https://github.com/openkruise/kruise) [kru](https://github.com/openkruise/kruise) [ise/kruise](https://github.com/openkruise/kruise) 的重要功能之一，如果你感兴趣的话可以研究一下。

## 总结

说到这里，再让我们回头看一下文章最开始大家提出的共性问题：现在的 Kubernetes 项目里，最有价值的部分到底是哪些？这个项目的本质到底在哪部分呢？

实际上，通过深入地讲解 “Tomcat 与 WAR 包解耦”这个案例，你可以看到 Kubernetes 的“声明式 API”“容器设计模式”“控制器原理”，以及kubelet 的工作机制等很多核心知识点，实际上是可以通过一条主线贯穿起来的。这条主线，从“应用如何描述”开始，到“容器如何运行”结束。

**这条主线，正是 Kubernetes 项目中最具价值的那个部分，即：云原生应用管理（Cloud Native Application Management）**。它是一条连接 Kubernetes 项目绝大多数核心特性的关键线索，也是 Kubernetes 项目乃至整个云原生社区这五年来飞速发展背后唯一不变的精髓。

![](https://static001.geekbang.org/resource/image/96/25/96ef8576a26f5e6266c422c0d6519725.jpg?wh=1110*659)