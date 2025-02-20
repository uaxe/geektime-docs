你好，我是邢云阳。

在前面 17 节课的学习过程中，相信你已经深入理解了 Agent 的核心原理，并掌握了如何运用 Agent 进行实际的应用开发。现在，我们终于来到了课程的收官阶段。如果你一直跟随课程循序渐进地学习，想必已经注意到我经常强调的一个重要观点：API 是 AI 时代的一等公民。

实际上，我们的课程设计也是围绕着这个理念展开的。从第一个实战项目“用自然语言操控 K8s”开始，我们就通过 API 来封装工具供 Agent 调用。在后续的“手撸可定制 API Agent”项目中，我们不仅基于 OpenAPI 实现了工具配置封装和调用的标准化，还为整个 Agent 的访问封装了 API，让用户可以通过 API 用自然语言与 Agent 交互。这种模式已经具备了 AI 微服务的雏形 ，即用户通过 API 调用，服务内部则由 Agent 实现具体功能。

说到微服务，就不得不提到 API 网关。传统的 API 网关作为微服务架构中的核心组件，负责处理所有外部请求，并将请求路由到相应的服务。在 AI 时代，API 网关也在不断进化，开始承载更多 AI 相关的功能。由阿里巴巴开源的 Higress 项目就是一个很好的例子，它已经从传统 API 网关演进成为了一个成熟的 AI 网关产品，我本人也是在该社区任职。本节课，我们就来探讨 AI 时代对网关的新需求，以及 Higress 是如何应对这些挑战的。