你好，我是蒋宏伟。我目前在58同城担任前端架构师，也是 58RN 框架的负责人。

六年来，我一直在围绕着 React Native 搞开发、搞基建、搞探索。从最初一线的 React Native 业务开发，到后来开始负责 58RN 的基础设施建设，再到 2021 年，我开始冲在最前沿做 React Native 新架构的调研，我用了 6 年的时间，朝着同一个方向一步一步地往前行。

在这期间，也得益于我所在的58用价中台的大前端团队，我接触到了各式各样的大前端技术。除了 React Native 之外，我直接负责过的跨端技术还有 Hybrid、小程序、Cocos 游戏，而且我也经常和 iOS、Android，以及 Flutter 的同学进行交流。

**我深刻地知道，没有完美的跨端技术，只有适合的场景。脱离适用场景去谈跨端技术没有什么意义。**

那么， React Native 适合哪些场景呢？

**第一，业务更新迭代较快的团队与出海团队。**

React Native 上手成本较低。对前端同学来说，React Native 和前端技术生态重合度很高，学习成本很低；对客户端同学来说，React Native 省去了大量的编译耗时，并且自带跨端光环， 一份源码可以同时编译成 Android 和 iOS 原生应用，并发布到安卓和苹果应用商店上。

所以，在一些业务迭代快的团队中，使用React Native 跨端方案不仅能够节约开发成本，还能带来接近原生的体验和性能。比如，现在大火的直播、短视频赛道中，React Native 能够通过集成声网提供原生 SDK，快速开发出一个直播、短视频应用。

而且，据我所知，一些出海团队也在使用 React Native 进行开发。针对于出海应用， React Native 有一套 Expo 方案，Expo 提供了一整套 React Native 的技术基础建设，极大地降低了开发一个新应用的成本，这就能帮助这些出海 App 用最低的成本、最快的速度获取海外用户。

**第二，既要支持动态更新，又要支持复杂业务的场景。**

在国内，无论大公司、小公司都钟情于应用的动态更新。因为动态更新能降低产品的试错成本。如果产品策略有调整，可以立马上线，线上有小问题也可以快速修复。但能够既满足动态更新，又能跨端，还能满足复杂业务需求的只有 JavaScript 语言。

目前几个主流的跨端框架，除了React Native之外，还有小程序、Weex、Flutter。但小程序只能让你的应用运行在别人的 App 上，Weex最终未能大规模流行起来，而Flutter使用的语言是Dart而非JavaScript，并不能很好支持动态更新。

换句话说，除了基于 JavaScript 的自研框架外， **目前能够既支持动态更新，又支持复杂业务的主流移动跨端框架只有使用 JavaScript 开发的 React Native。**

## 为什么你应该学习 React Native ？

**首先，React Native 是一个非常流行的跨端框架，开发者认可度很高。**

根据权威网站数据，现在使用 React Native 的开发者已经越来越多了。在 [npm trends](https://www.npmtrends.com/react-native) 网站上你可以看到，react-native 框架每周的下载次数，已经从5年前的不到10万次，到现在超过了 80 万次，5 年时间翻了 8 倍之多。

![图片](https://static001.geekbang.org/resource/image/d7/50/d75660fb448113ba4279962f88bc7b50.png?wh=1920x760)

这意味着，React Native 有一个繁荣和不断迭代的生态。

对于个人而言，强大的生态意味着很多功能都不用自己写，从社区拿来用就行，这极大地降低了开发成本。你可以在社区中选择最适合你业务的技术工具，比如状态管理、路由、动画、工具库和原生扩展等等。对于企业来说，使用 React Native 这类成熟框架开发移动应用成本更低，风险也更低，企业也更愿意招聘相关开发者。

**其次，React Native 是一个跨领域的融合技术，它是你现有技术的自然延伸。**

React Native 的生态和 JavaScript、React、iOS、Android 甚至 Node.js 的生态都有很大的交集。在 React Native 生态中，有来自各种技术领域的思想碰撞。相信你学习 React Native 时，这种感受会非常明显。

如果你是一个前端工程师，已经掌握 JavaScript、React 的相关技术，那么对 React Native 的学习，可以让你了解到那些独属于 Android 和 iOS 原生平台的特性。

比如，你可以亲手尝试使用 WebView 容器来加载 Web 页面，甚至你还可以用 WebView 中的 JavaScript 去调用 React Native 中的 JavaScript，把 Native 暴露给 React Native 的支付能力再暴露给 Web，这样你能更加深刻地体会到 Hybrid 的实现原理。

如果你是客户端工程师，已经掌握Android 或 iOS 的这些技术了，那你只需要学习一下 JavaScript 和 React 这些流行的前端技术即可，相信你能从中体会到热重载、热更新和跨端带来的乐趣。

而且，React Native 这门融合技术还有另一个好处，它能让前端和客户端更加紧密的协作。日常开发中，前端和客户端经常需要协作，比如很多公司就专门设立了大前端部门，为的就是方便前端和客户端一起做事。要更好地共事，就需要学会站在对方角度思考问题，通过学习 React Native 你就能了解对方技术栈的特点，就更容易换位思考，而这也能帮助你快速成长。

**更关键的是，React Native 新架构已经确定会在今年正式发布。**

2022 年，对于 React Native 来说是一个大年，因为重构已久的 React Native 新架构已经确定会在今年正式推出，目前的 0.68 版本已经出了新架构的测试版。根据业内已有的报告和我们团队的调研结果，相对于老架构，新架构在最关键的性能问题上有了非常大的提升，这将会为 React Native 开启一个全新的阶段。

## 期待已久的新架构会带来什么？

React Native 是 2013 年在 Facebook 一个内部的黑客马拉松项目中诞生的，到今年 2022 年新架构出来，已经整整十年了。

它诞生于移动互联网大爆发时代，当时国内外各大互联网公司都相继提出了“Mobile First”、“All in 无线”之类的口号。但后来，React Native 也因为性能等问题，让类似 Airbnb 这样的团队选择了放弃。

但技术的车轮还是滚滚向前，并不会停下它的脚步。

2021 年 7 月，经历 4 年漫长的等待，当我得知 React Native 新架构已经在 Facebook 落地的消息时，真是万分激动，期待已久的 [React Native 新架构终于要来了](https://www.infoq.cn/article/txsiq1wogk6il4bnqmja)，于是我马上开始了新架构的调研。

![图片](https://static001.geekbang.org/resource/image/b8/de/b8f55be43f5243a91de6aea7a00575de.png?wh=1920x1104)

到今天，经历过大半年的调研，我也大概摸清楚了 React Native 新架构的技术底层原理和发展方向，目前来看它至少会有这几个值得期待的亮点：

**首先，React Native 新架构的启动性能会有 2 倍左右的提升。**

React Native 新架构默认用的 JavaScript 引擎是 Hermes 引擎。Hermes 是一款专为移动端打造的 JavaScript 引擎，它支持 JavaScript 的 AOT 预编译。

一般而言，要执行一段 JavaScript 代码，首先要将 JavaScript 代码编译为字节码，再把字节码编译为二进制的机器码，才能被 CPU 等硬件执行。而 AOT 预编译技术可以让你在本地提前将 JavaScript 编译成字节码。这样一来，在启动 React Native 应用时，相对于老架构 JSCore 引擎的就少了一个步骤，因此 React Native 新架构的启动性能会有很大的提升。

**其次，React Native 新架构的通信性能会有 3 倍左右的提升。**

React Native 老架构通信用的是 JS Bridge，JS Bridge 的通信方式是“发送消息”。React Native 新架构通信的是 JSI（JavaScript Interface），JSI 把很多底层的 C++ 接口都直接暴露给了 JavaScript。有了 JSI 后，React Native 中的 JavaScript 就直接调用 C++了，就像 node.js 使用 addon 调用 C++ 、 Flutter 用 FFI 调用 C++ ，以及 Java 使用 JNI 调用 C++ 一样。

所以，使用 JSI 意味着不用发送消息，而是直接调用，没有序列化和反序列。少了这些多余的步骤，操作指令的传递效率就会高很多。

**第三，React Native 新架构的渲染流水有了很大的变化，这会带来更好的用户体验。**

在老架构中，React Native 只有异步渲染这一种方式。而我们知道原生视图的渲染是同步的，这时如果把 React Native 渲染到原生视图中，就可能导致布局抖动问题。而新架构提供了同步的渲染能力，这就提供了一种新的可能：一方面我们可以在原生页面中嵌套 React Native 视图，另一方面 React Native 应用也能更方便地引入一些需要同步 API 的原生组件。

另外，还有一个我非常关注的方向，就是 React Native 团队正在基于 React Native 新架构研究服务端渲染方案。React Native 的 SSR 和 Airbnb 的自行研发 [服务端渲染框架](https://medium.com/airbnb-engineering/whats-next-for-mobile-at-airbnb-5e71618576ab) 原理非常类似。国内的 [美团团队也在 React Native 老架构之上实现了 SSR](https://ppt.infoq.cn/slide/show?cid=94&pid=3696)，据说美团的 **页面渲染速度最快能达到50ms**。

希望在不远的将来，React Native SSR 能出一个类似于 Web 服务端渲染的 Next.js 的通用方案，用更低成本解决性能痛点。

总之我们有理由相信，React Native 新架构会给我们带来巨大的惊喜。

## 这门课是怎么设计的？

在调研新架构的过程中，我发现 React Native 本身的迭代非常快，现在并没有比较适合初学者和进阶者系统学习 React Native 的课程。我当时想等 React Native 新架构出来后，再出一个基于 React Native 新架构的课程，也算是回馈社区了。

但后来我决定采用 **动态专栏** 的形式和你见面。因为我发现，面对一个前沿技术，如果我们真要等它完全成熟了再来研究，可能就晚了。更重要的是，只有 **先坐上 React Native 新架构的这趟列车，才能享受到前沿技术变革带来的红利**。

但技术的实时性和课程的完整性又应该如何兼顾呢？

于是，我想到一个办法，先用 24 讲把 React Native 完整地给你介绍一遍，再用一年的时间，用12 讲的内容和你一起跟进 React Native 新架构最前沿的变化和进展。

![图片](https://static001.geekbang.org/resource/image/c8/2b/c816a5fa34106a6b5073af7fbb15c72b.jpg?wh=1357x1323)

**第一部分是核心基础篇。** 这里我们主要是把基础打牢，带你深入学习 React和React Native 的基础知识，包括状态和组件的使用，及其背后的设计原理，还有开发 UI 和调试代码的经验技巧。在这个阶段，我们的目标是要让你能够搭建一个 React Native 页面，我希望通过实践的方式，让你收获搭建 React Native 页面的能力，而不仅仅只是知识。

**第二部分是社区生态篇。** 这一部分中，我们的首要目的是帮你开阔眼界，让你知道社区有哪些成熟方案，需要时能够拿来即用，同时也让你能够借助 React Native 生态中最常用的几个工具，搭建一个完整的 React Native 应用。搭建一个完整应用是很有挑战的一件事情，我会把我搭建好的一个简易电商应用放在 GitHub 给你参考，希望能让你在代码层面，而不仅仅只是文字层面有所收获。

**第三部分是基础设施建设篇。** 这里我们会从技术应用层面，给你介绍从构建 React Native 混合应用到热更新，再到性能调优的全过程，让你能为团队搭建基础设施建设出谋献策，进一步提升你的架构能力。

而且，我还邀请了和我一起共事多年的两位老搭档况众文和朴惠姝，他们是 58RN Native 方向的负责人，我们会共同地把多年搭建 React Native 基础设施的心得和你分享。

后面动态更新的 12 讲，我会采用 **每个月 1 篇** 的更新形式，帮你跟踪 React Native 新架构的最新进展，并和你聊聊和 React Native 新架构相关的最前沿的新技术，包括且不限于 Hermes、Fabric、JSI、React Native Skia、React Native SSR ，等等。

具体你可以看看下面的目录：

![](https://static001.geekbang.org/resource/image/45/d0/45c912f5bdcdea16fb9a9d344b85efd0.jpg?wh=1563x5680)

最后，我希望这门课程能够帮到那些曾经和我一样对 React Native 跨端技术充满好奇的人，那些想弄明白如何搭建一套跨端基础设施的人，以及那些希望自己能够冲在技术最前沿的探索和创新的人。

**技术的世界如此精彩，我们当然不应该躺平，愿你的好奇、勇敢和行动能得到相应的回报。**