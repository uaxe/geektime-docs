众所周知，Tomcat 是应用最广泛的 Web应用服务器，不过在实际使用 Tomcat 过程中，我们总是会遇到各种复杂问题，比如：

- 如何管理多个 Servlet？
- 如何支持多个独立的应用？
- 大量用户请求的性能问题如何解决？
- 处理高并发请求时的内存泄漏问题怎么处理？
- ……

这些复杂的问题出现时，如果仅仅是会使用Tomcat是万万不能解决的，我们需要深入Tomcat原理，从底层的视角审视问题，并彻底解决问题。而掌握一项技术最好也是最扎实的方式就是重造轮子。

为此我们邀请了前 Sun Microsystems Java 研发工程师郭屹老师，他会带你一步步剖析源码，深入Tomcat底层原理，并让你从中领悟Tomcat的设计哲学，帮助你在面对复杂的生产问题时快速找到解决方案，同时也为你自己设计系统提供思路与最佳实践。

## 课程设计

MiniTomcat 的课程大体上分成四大块：HTTP Server、Connector、Container 和扩展部分。熟悉 Tomcat 的人想必更加清楚，Connector + Container 就是 Tomcat 的核心了。学习这些内容，会为进一步的研究打下良好的基础。

![](https://static001.geekbang.org/resource/image/aa/cd/aa29c570c704ef208c031ed6f116bdcd.jpg?wh=2872x2267)

**第一章 实现一个简单的 Web 应用服务器**

Web 应用的核心是对 HTTP 协议的支持，接收浏览器发送的 HTTP 请求，解析 URL，找到资源返回内容，显示在客户浏览器上。这一部分先不引进任何规范，而是自己简单地实现 Request 请求与 Response 响应。虽然它很简单，但是也是一个地道的 Web 应用服务器，不仅支持静态资源，还能运行程序动态返回内容。我们后面的改造都会基于这个简单服务器。

**第二章 实现专业的 Connector**

基于简单的应用服务器，这部分我们会来重点实现 MiniTomcat 连接层，并且按照 Servlet 规范进行改造。优化代码结构，将第一部分的 Server 拆分为 Connector 与 Processor。之后初步优化性能，引入 Processor 池化技术，支持 Processor 并发执行，提高 Server 的高并发能力。然后，我们就要按照规范行事，实现 Servlet 对请求和响应的接口规范。

这一部分的改造过后，MiniTomcat 的连接层就有模有样了。

**第三章 实现专业的 Container**

连接层解决后，我们再重点设计实现容器。先引入 Wrapper，实现 Context 与 Wrapper，形成两层容器，将整个框架进一步按照功能拆分成不同模块，每一部分各司其职。最后引入日志、过滤器、监听器等通用组件。这一部分之后，Tomcat 的核心就模仿出来了。

**第四章 完成 MiniTomcat 及扩展讨论**

这个部分我们将考虑多应用支持，进一步拆分功能，BootStrap 只负责启动服务器，业务代码都在 Context 内运行，支持不同路由转发到不同应用之中，而应用之前相互隔离。这个需求就要求我们改变标准的 Java 类加载机制，自定义加载过程。最后通过 web.xml 各项配置，启动Server，实现完整而基本的 Tomcat。

作为扩展，我们会探讨如何把 MiniSpring 打包放在 MiniTomcat 中运行，形成 Mini 系列的核心环境，还将探讨将网络 I/O 扩展为支持 NIO，以支持高并发场景的方案。