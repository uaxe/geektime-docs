“天下苦秦久矣”，不管是H5、React Native，还是过去两年火热的小程序，这些跨平台方案在性能和稳定性上总让我们诟病不已。最明显的例子是React Native已经发布几年了，却一直还处在Beta阶段。

Flutter作为今年最火热的移动开发新技术，从我们首次看到Beta测试版，到2018年12月的1.0正式版，总共才经过了9个多月。Flutter在保持原生性能的前提下实现了跨平台开发，而且更是成为Google下一代操作系统Fuchsia的UI框架，为移动技术的未来发展提供了非常大的想象空间。

高性能、跨平台，而且更是作为Google下一个操作系统的重要部分，Flutter已经有这么多光环加身，那我们是否应该立刻投身这个浪潮之中呢？新的技术、新的框架每一年都在不断涌现，我们又应该如何跟进呢？

## Flutter的前世今生

大部分所谓的“新技术”最终都会被遗忘在历史的长河中，面对新技术，我们首先需要持怀疑态度，在决定是否跟进之前，你需要了解它的方方面面。下面我们就一起来看看Flutter的前世今生。

Flutter的早期开发者Eric Seidel曾经参加过一个访谈 [What is Flutter](https://www.youtube.com/watch?v=h7HOt3Jb1Ts)，在这个访谈中他谈到了当初为什么开发Flutter，以及Flutter的一些设计原则和方向。

﻿﻿

![](https://static001.geekbang.org/resource/image/ac/5c/aca58328ba1b4f1463d1b2b806c5ad5c.png?wh=1920*1061)

Eric Seidel和Flutter早期的几位开发人员都是来自Chrome团队，他们在排版和渲染方面具有非常丰富的经验。那为什么要去开发Flutter？一直以来他们都为浏览器的性能而感到沮丧，有一天他们决定跳出Web的范畴，在Chromium基础上通过删除大量的代码，抛弃Web的兼容性，竟然发现性能是之前的20倍。对此我也深有感触，最近半年也一直在做主App的Lite版本，安装包也从42MB降到8MB，通过删除大量的历史业务，性能比主包要好太多太多。

正如访谈中所说，Flutter是一个Google内部孵化多年的产品，从它开发之初到现在，一直秉承着两个最重要的设计原则：

- **性能至上**。内置布局和渲染引擎，使用Skia通过GPU做光栅化。选择Dart语言作为开发语言，在发布正式版本时使用AOT编译，不再需要通过解析器解释执行或者JIT。并且支持Tree Shaking无用代码删除，减少发布包的体积。

- **效率至上**。在开发阶段支持代码的 [Hot Reload](https://juejin.im/post/5bc80ef7f265da0a857aa924)，实现秒级编译更新。重视开发工具链，从开发、调试、测试、性能分析都有完善的工具。内置Runtime实现真正的跨平台，一套代码可以同时生成Android/iOS应用，降低开发成本。


那为什么要选择Dart语言？“Dart团队办公室离Flutter团队最近”肯定是其中的一个原因，但是Dart也为Flutter追求性能和效率的道路提供了大量的帮助，比如AOT编译、Tree Shaking、Hot Reload、多生代无锁垃圾回收等。正因为这些特性，Flutter在筛选了多种语言后，最终选择了Dart。这里也推荐你阅读 [Why Flutter Uses Dart](https://hackernoon.com/why-flutter-uses-dart-dd635a054ebf) 这篇文章。

总的来说，Flutter内置了布局和渲染引擎，使用Dart作为开发语言，采用React方式编写UI，支持一套代码在多端运行的框架。但是正如专栏前面所说的，大前端时代的核心诉求是跨平台和动态化，下面我们就一起来看看Flutter在这两方面的表现。

**1\. Flutter的跨平台开发**

虽然React Native/Weex使用了系统原生UI组件，通过原生渲染的方式来提升渲染速度和UI流畅度，但是因为JS执行效率、JSBridge的通信代价等因素，性能依然存在瓶颈，而且我们也无法抹平不同系统的平台差异，因此这样的跨平台方案注定艰难。

![](https://static001.geekbang.org/resource/image/64/09/64ee06b802ca55df19b8f1a30e422809.png?wh=1398*756)

正如Eric Seidel在访谈所说，Flutter是从浏览器引擎简化而来，无论是它的布局引擎（例如也是使用CSS Flexbox布局），还是渲染流水线的设计，都跟浏览器都有很多相似之处。但是它抛弃了浏览器沉重的历史包袱和Web的兼容性，实现了在保持性能的前提下的跨平台开发。

回想一下在专栏第37期 [《工作三年半，移动开发转型手游开发》](https://time.geekbang.org/column/article/88442) 中，我们还描述过另外一套内置Runtime的跨平台方案： [Cocos引擎](https://github.com/cocos2d/cocos2d-x)。

![](https://static001.geekbang.org/resource/image/87/6f/87abff685ed21a61a5b1bf89da143f6f.png?wh=1920*953)

在我看来，Cocos和Unity这些游戏引擎才是最早并且成熟的跨平台框架，它们对性能的要求也更加苛刻。即使是“王者荣耀”和“吃鸡”这么复杂的游戏，我们也可以做得非常流畅。

Flutter和游戏引擎一样，也提供了一套自绘界面的UI Toolkit。游戏引擎虽然能实现跨平台开发，但它致力于服务更有“钱途”的游戏开发。游戏引擎对于App开发，特别是混合开发支持并不完善。

如下图所示，我们可以看到三种跨平台方案的对比，Flutter可以说是三者中最为轻量的。

![](https://static001.geekbang.org/resource/image/a2/02/a297b66d9b4378679d384ef4fe378c02.jpg?wh=1206*616)

**2\. Flutter的动态化实践**

在专栏第40期 [《动态化实践，如何选择适合自己的方案》](https://time.geekbang.org/column/article/89555) 中，我提到了一个观点：“相比跨平台能力，国内对大前端的动态化能力更加偏执”。

在性能、跨平台、动态性这个“铁三角”中，我们不能同时将三个都做到最优。如果Flutter在性能、跨平台和动态性都比浏览器更好，那就不会出现Flutter这个框架了，而是成为Chromium的一个跨时代版本。

![](https://static001.geekbang.org/resource/image/b9/7b/b9288c3aedb11afe45957557b90f257b.png?wh=1488*782)

浏览器选择的是跨平台和动态性，而Flutter选择的就是性能和跨平台。Flutter正是牺牲了Web的动态性，使用Dart语言的AOT编译，使用只有5MB的轻量级引擎，才能实现浏览器做不到的高性能。Flutter的第一波受众是Android上使用Java、Kotlin，iOS上使用Objective-C、Swift的Native开发。未来Flutter是否能以此为突破口，进一步蚕食Web领域的份额，现在还不得而知。

那Flutter是否支持动态更新呢？由于编译成AOT代码，在iOS是绝对不可以动态更新的。对于Android，Flutter的动态更新能力其实Tinker就已经实现了。从官方的提供方案来看，其实也只是替换下面的变化文件，可以说是Tinker的简化版。

![](https://static001.geekbang.org/resource/image/6a/9c/6a410383cadbaae7c8822dee6f455d9c.png?wh=816*606)

官方的动态修复方案可以说是非常鸡肋的，并且也是要求应用重启才能生效。如果同时修改了Native代码，这也是不支持的。

更进一步说，Flutter在Google Play上是否允许动态更新也是抱有疑问的。从Google Play上面的开发者政策中心 [规定](https://play.google.com/intl/zh-CN_ALL/about/privacy-security-deception/malicious-behavior/) 上看，在Google Play也是不允许动态更新可执行文件。

![](https://static001.geekbang.org/resource/image/03/55/0369ac6b78069e2b5ea983bd1fa14d55.png?wh=1834*540)

从 [《从Flutter的编译模式》](https://www.stephenw.cc/2018/07/30/flutter-compile-mode/) 一文中，我们可以通过 `flutter build apk --build-shared-library` 将Dart代码编译成app.so。无论是libflutter.so，还是app.so（其实 `vm_*`、 `isolate_*` 也是可执行文件）的动态更新，都违反了Google Play的政策。

![](https://static001.geekbang.org/resource/image/85/99/8580a8da34098dc918e4cb7c7330c199.png?wh=734*622)

当然不排除Google为了推广Flutter，为它的动态更新开绿灯。最近我也在咨询Google Play的政策组，目前还没有收到答复，如果后续有进一步的结果，我也可以同步给各位同学。

总的来说，Flutter的动态化能力理论上只能通过JIT编译模式解决，但是这会带来性能和代码体积的巨大影响。当然，闲鱼也在探索一套Flutter的布局动态化方案，你可以参考文章 [《Flutter动态化的方案对比及最佳实现》](https://mp.weixin.qq.com/s/N5ih-DY5TuKyn_a0P2mz0Q)。

## 面对新技术，该如何选择

通过上面的学习，我们总算对Flutter的方方面面都有所了解。可以说Flutter是一个性能和效率至上，但是动态化能力非常有限的框架。

目前 [闲鱼App](https://www.yuque.com/xytech/flutter/tc8lha)、 [美团外卖](https://tech.meituan.com/2018/08/09/waimai-flutter-practice.html)、 [今日头条App](https://mp.weixin.qq.com/s/-vyU1JQzdGLUmLGHRImIvg)、 [爱奇艺开播助手](https://mp.weixin.qq.com/s/7GSPvP_hOWCv64esLLc0iw)、 [网易新闻客户端](http://mp.weixin.qq.com/s/a0in4DqB8Bay046knkRr1g)、京东 [JDFlutter](https://mp.weixin.qq.com/s/UhfgfNEdogm7Busr0apAGQ)、 [马蜂窝旅游App](https://mp.weixin.qq.com/s/WBnj_6sOonjR9XUnB-wZPA)，都分享过他们在使用Flutter的一些心得体会。如果有兴趣接入Flutter，非常推荐你认真看看前人的经验和教训。

无论是Flutter，还是其他新的技术，在抉择是否跟进的时候，我们需要考虑以下一些因素：

- **收益**。接入新的技术或者框架，给我们带来什么收益，例如稳定性、性能、效率、安全性等方面的提升。

- **迁移成本**。如果想得到新技术带来的收益，需要我们付出什么代价，例如新技术的学习成本、原来架构的改造成本等。

- **成熟度**。简单来说，就是这个新技术是否靠谱。跟选择开源项目一样，团队规模、能力是否达标、对项目是否重视都是我们需要考虑的因素。

- **社区氛围**。主要是看跟进这个技术的人够不够多、文档资料是否丰富、遇到问题能否得到帮助等。


**1\. 对于Flutter，我是怎么看的**

Flutter是一个非常有前景的技术，这一点是毋庸置疑的。我曾经专门做过一次全面的评估分析，但是得出的结论是暂时不会在我负责的应用中接入，主要原因如下。

![](https://static001.geekbang.org/resource/image/23/ba/2316c956d3895fb2e4b2514a521e1bba.jpg?wh=1158*1160)

目前我还没有跟进Flutter的核心原因在于收益不够巨大，如果有足够大的收益，其他几个因素都不是问题。而我负责的应用目前使用H5、小程序作为跨平台和动态化方案，通过极致优化后性能基本可以符合要求。

从另外一方面来说，新技术的学习和引入，无论是对历史代码、架构，还是我们个人的知识体系，都是一次非常好的重构机会。我非常希望每过一段时间，可以引入一些新的东西，打破大家对现有架构的不满。

新的技术或多或少有很多不完善的地方，这是挑战，也是机会。通过克服一个又一个的困难和挑战，并且在过程中不断地总结和沉淀，我们最终可能还收获了团队成员技术和其他能力的成长。以闲鱼为例，他们在Flutter落地的同时，不仅将他们的经验总结成几十篇非常高质量的文章，而且也参加了QCon、GMTC等一些技术大会，同时开源了 [fish-redux](https://github.com/alibaba/fish-redux)、 [FlutterBoost](https://github.com/alibaba/flutter_boost) 等几个开源库，Flutter也一下成为了闲鱼的技术品牌。

可以相信，在过去一年，闲鱼团队在共同攻坚Flutter一个又一个难题的过程中，无论是团队的士气还是团队技术和非技术上的能力，都会有非常大的进步。

**2\. 对于Flutter，大家又是怎么看的**

由于我还并没有在实际项目中使用Flutter，所以在写今天的文章之前，我也请教了很多有实际应用经验的朋友，下面我们一起来看看他们对Flutter又是怎么看的。

![](https://static001.geekbang.org/resource/image/49/14/49ca149bb073fcbd0dc3b06494ddad14.jpg?wh=750*4423)

## 总结

曾几何时，我们一直对Chromium庞大的代码无从入手。而Flutter是一个完整而且比WebKit简单很多的引擎，它内部涉及从CPU到GPU，从上层到硬件的一系列知识，源码中有非常多值得我们挖掘去学习和研究的地方。

未来Flutter应用在小程序中也是一个非常有趣的课题，我们可以直接使用或者参考Flutter实现一个小程序渲染引擎。这样还可以带来另外一个好处，一个功能（例如微信的“附近的餐厅”）在不成熟的时候可以先以小程序的方式尝试，等到这个功能稳定之后，我们又可以无成本地转化为应用内的代码。

Dart语言从2011年启动以来，一直想以高性能为卖点，试图取代JavaScript，但是长期以来在Google外部使用得并不多。那在Flutter这个契机下，它未来是否可以实现弯道超车呢？这件事给我最大的感触是，机会可能随时会出现，但是需要我们时刻准备好。

“打铁还需自身硬”，我们还是要坚持修炼内功。对于是否要学习Flutter，我的答案是“多说无益，实践至上”。

## 课后作业

对于Flutter，你有什么看法？你是否准备在你的应用中跟进？欢迎留言跟我和其他同学一起讨论。

Flutter作为今年最为火热的技术，里面有非常多的机遇，可以帮我们打造自己的技术品牌（例如撰写文章、参加技术会议、开源你的项目等）。对于Flutter的学习，你可以参考下面的一些资料。

- 万物之中， [源码](https://github.com/flutter/flutter) 最美

- [Flutter官方文档](https://flutter.dev/docs)

- [闲鱼的Flutter相关文章](https://www.yuque.com/xytech/flutter)

- 各大应用的使用总结： [闲鱼App](https://www.yuque.com/xytech/flutter/tc8lha)、 [美团外卖](https://tech.meituan.com/2018/08/09/waimai-flutter-practice.html)、 [今日头条App](https://mp.weixin.qq.com/s/-vyU1JQzdGLUmLGHRImIvg)、 [爱奇艺开播助手](https://mp.weixin.qq.com/s/7GSPvP_hOWCv64esLLc0iw)、 [网易新闻客户端](http://mp.weixin.qq.com/s/a0in4DqB8Bay046knkRr1g)、京东 [JDFlutter](https://mp.weixin.qq.com/s/UhfgfNEdogm7Busr0apAGQ)、 [马蜂窝旅游App](https://mp.weixin.qq.com/s/WBnj_6sOonjR9XUnB-wZPA)

- 阿里Flutter开发者帮助App： [flutter-go](https://github.com/alibaba/flutter-go)


欢迎你点击“请朋友读”，把今天的内容分享给好友，邀请他一起学习。我也为认真思考、积极分享的同学准备了丰厚的“学习加油礼包”，期待与你一起切磋进步哦。