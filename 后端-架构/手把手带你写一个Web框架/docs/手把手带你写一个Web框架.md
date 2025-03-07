在 Web 领域，特别是中小型项目，开发效率往往是业务的第一需求。一个产品拥有的市场机会转瞬即逝，抢占市场依靠的是更快的开发速度和迭代速度。为了提效，前端轮子太多已经是共识。不管什么语言，在 Web 领域，开发必备的框架总有很多款。

因此，就有很多实际的问题摆在了我们面前：

- 市面上众多框架如何迅速上手？如何选择？
- 业务快速迭代时，框架如何迅速拓展？
- 想要自研一款称手的 Web 框架，如何设计？

全方位提升开发效能成为突破瓶颈的最佳解决方案。叶剑峰根据自己的十余年一线 Web 后端研发经验，梳理了一套系统的 Web 框架搭建方法论。他将使用 Go 语言，从标准库开始，逐步演进，**手把手带你研发一个工业级的 Go Web 框架，以基本概念与核心理论为指导，实战演练总结底层框架的设计技巧**。

![](https://static001.geekbang.org/resource/image/43/a1/43004529c0683a7468a916e89c3739a1.jpeg)

### 课程模块设计

整个专栏分为实战四关，你会从零开始，收获一个自己的工业级 Go Web 框架。

**实战第一关**：分析 Web 框架的本质，从最底层的 Go 的 HTTP 库讲起，如何基于 HTTP 库搭建 server、如何搭建路由、如何增加中间件等等，从而搭建出一个 Web 框架最核心的设计部分。

**实战第二关**：框架核心搭建好后，基于具体业务场景重新思考，要设计的框架目标到底是什么? 框架的设计感和要解决的问题在哪里? 框架的倾向性是什么? 如果要搭建出一个“一切皆服务”的框架，应该如何设计。

思考清楚后，我们会用 Gin 框架集成实战第一关自研的 Web 框架的核心，力求站在巨人的肩膀上看世界，然后一步步实现框架核心的功能服务。

**实战第三关**：为这个框架增加不同的周边功能，在添加功能时，会首先讨论目前社区中的标准做法，以及有没有更好的设计，最终把这些标准做法融合到我们的框架中。

**实战第四关**：现在框架已经基本搭建完成了，我们会用这个框架应用开发一个问答后台，使用 vue-element-admin 来做前端封面，再结合框架开发具体的统计展示和计算业务。