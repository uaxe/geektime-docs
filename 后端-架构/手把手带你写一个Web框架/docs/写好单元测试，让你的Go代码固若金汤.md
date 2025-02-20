大家好，我是轩脉刃。

在专栏[第 34 章](https://time.geekbang.org/column/article/464834)，完成问答系统的开发后，我们使用 GoConvey、SQLite 写了一些单元测试，对问答系统进行测试验证。当时，我们主要聚焦于专栏中开发的系统，详细描述了如何开发单测，并且展示了单测的代码。但单元测试是一套完整的方法论，不是如此简单就能描述完备的。

因此在这里，我想和你系统地讨论 Golang 业务中的单元测试，包括它的重要性、设计思路，以及编写单测的方法技巧。

在正常开发过程中，我发现一个很有意思的现象，所有开发同学都会说单元测试有用，但鲜少见到有人在开发过程中编写单元测试。究其原因，大致会是如下几种：

- 我是来写功能的，不是来写测试的
- 我写的代码不会出错，用不着单元测试
- 后面的集成测试会帮我测试出问题的
- 写单元测试太浪费时间了
- 我不知道怎么写单元测试

这些问题，我希望能在今天给出完美的解答。

# 为单元测试“正名”

业务代码对单元测试的接纳，首先必须是思想上的接纳。即思想上必须要想清楚一件事：为什么要有单元测试。

## 单元测试是将 Bug 控制在编码阶段的唯一手段

![图片](https://static001.geekbang.org/resource/image/87/df/87b7a338a3790ece86fd054486fb1edf.png?wh=1694x1114 "图片来自网络")

上图出自 Capers Jones 在 1996 年出版的 《Applied Software Measurement》，它是一张经典图表，展示了软件开发生命周期中的缺陷发现和修复成本。这张图在软件工程领域非常有影响力，经常被用来说明“尽早测试、尽早发现问题”的重要性。那接下来，我们就一起来分析这张图上的重要信息。