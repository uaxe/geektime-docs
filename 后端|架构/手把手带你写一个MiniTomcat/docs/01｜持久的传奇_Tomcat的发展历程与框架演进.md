你好，我是郭屹，从今天开始我们来学习手写 MiniTomcat。

作为使用Java语言进行Web程序开发的人来说，对Tomcat想必是不陌生的。Tomcat是一款轻量级的Java应用服务器，最早是Sun公司在1998年开发的。当时开发Tomcat的目标是成为Sun公司的Java Servlet和JSP规范的参考实现。

如今Tomcat是业务开发首选的开源Web应用服务器，在Spring MVC项目中会把它作为程序的启动容器，甚至在Spring Boot框架中直接将Tomcat内置为Web应用的启动容器，不再需要程序开发者自行配置，进一步简化了开发门槛。可以说，虽然Tomcat不是Web服务器的唯一选择，但也和Spring一样，成为了Java开发领域事实上的标准。二十五年以来长盛不衰，在日新月异的IT领域，可谓是持久的传奇。

## 版本变化

跟任何一个成功的产品一样，Tomcat也不是一诞生就是现在这个样子的，它也是经历了逐渐完善和强大的发展历程。

![图片](https://static001.geekbang.org/resource/image/yy/ce/yy534ab3e199fe942495da89ab56bece.png?wh=1920x981)

Tomcat的发明人是James Duncan Davidson。他在1997年加入Sun公司，然后开始动手写Tomcat，这是Sun对外提供的一个Servlet容器的参考实现，后来大名鼎鼎的Spring发明人Rod Johnson也是Servlet专家组成员。1998年对外公开的时候标记为2.0版本，到了1999年，Sun公司就把它捐赠给了Apache基金会。

下面我们按照发布时间来梳理一下Tomcat的主要版本。

![](https://static001.geekbang.org/resource/image/ey/17/eyy97a8bec58d154e3edf356cb8f2d17.png?wh=5120x2190)

目前正在开发中的版本是11。

## 程序内部结构

作为程序员，除了了解版本发布情况之外，我们更要仔细琢磨Tomcat程序的内部结构，因为从内部结构中我们可以收获更多的技术思想。

我们先看一下它的宏观结构。

![图片](https://static001.geekbang.org/resource/image/84/37/8424cda2303f030e15c0f162f16e7737.png?wh=1920x1072)

一眼就可以看出，Tomcat的结构出奇地简单自然，从最顶层来看，就是一个Server提供Service，在内部通过容器管理Servlet，对外通过Connector接受客户端的访问。

如果你写过服务器程序，那么你应该对这个结构一点都不陌生，几乎所有的Server软件都是这个结构。往内部再细分，一般就是通过Socket完成客户端的连接管理，由一个内部容器按照规定的生命周期管理Servlet。

我们再仔细点，看看Tomcat是如何响应请求的。

01. 用户在浏览器输入地址，请求被发送到服务器端，按照Socket模型，这个访问被一个端口驻守的程序收到，如8080。在Tomcat中，负责这一块的是在那里监听的Coyote Connector。
02. Connector解析Socket来的请求流，再将该请求交给它所在的Service的Engine来处理，并等待Engine的回应。
03. Engine获得请求URI，匹配到合适的虚拟主机Host。
04. 这个Host获得请求串，匹配到合适的Context。
05. 在Context中寻找出对应的Servlet（其实是一个Wrapper） 处理数据。
06. 将构造HttpServletRequest对象和HttpServletResponse对象，作为参数调用Servlet的 `service()` 执行业务逻辑、数据存储等程序。
07. Context把执行完之后的HttpServletResponse对象返回给Host。
08. Host把HttpServletResponse对象返回给Engine。
09. Engine把HttpServletResponse对象返回Connector。
10. Connector把HttpServletResponse对象序列化返回给浏览器。

![图片](https://static001.geekbang.org/resource/image/3e/df/3e9479e9ff9c440a5710c140b5c4a4df.png?wh=1920x950)

以上就是 Tomcat 处理一个HTTP请求的完整流程。

核心道理很简单，说白了就是一个Socket Server，但是对应到工程上却并不容易。如果这个服务器只需要响应一次请求，确实是没有什么可做的，但是现实世界并不是这样，我们还要考虑一些啰嗦事。

1. 如何管理多个Servlet？
2. 如何支持多个独立的应用？
3. 大量用户请求的性能问题如何解决？

作为一款实用的Servlet应用服务器，考虑到这些事项，内部的程序结构会变得很复杂。这些在我们学习了Tomcat的源码后，会有很多的启发。

## 程序结构的演化

没有人能一步到达终点，软件的演化过程中有很多争论妥协，有的设计到后面又被抛弃了，反反复复。Tomcat也走过了同样的路，编程的顶级高手也是要呕心沥血才能修得正果的。接下来我们就来看一下，Tomcat是如何一步步演化的。

#### 第一步：设计一个简单的Socket Server

设计一个Socket Server，启动后负责监听网络来的请求，获得一个Socket连接。然后这个Server要解析请求串，知道需要处理什么事情，然后调用相关的程序完成相关任务。最后得到返回处理结果，将这个结果再通过Socket传回客户端。

这个简单的结构很有效，也很简明，但是缺点显而易见：请求监听和处理逻辑放在一起扩展性很差。处理是一个一个串行完成的，性能不好。

#### 第二步：将连接与处理分离

因为第一步显而易见的缺点，所以我们把Server拆分成两部分：Connector和Processor。Server只是一个外壳，负责启动。Connector来负责监听网络来的请求，获得一个Socket连接，解析请求后发给Processor，然后Processor调用相关的程序完成相关任务，最后得到返回处理结果，将这个结果返回给Connector，Connector再通过Socket传回网络客户端。

经过这一步的分工，Server的程序结构更加清晰，各司其职。但之前的缺点并没有完全优化，性能问题还没有解决。为了提高性能，需要设计多个Processor，放到一个池中，支持并发执行。

#### 第三步：多层容器Container

为了进一步扩展，这一步我们要把后面对Servlet的处理分成多层容器，首先是直接包装Servlet的Wrapper，然后对应一个应用Context，一个Context对象会包含多个Wrapper对象，用于分别管理多个 Servlet，而Context之间是独立的，再往上抽象出Host和Engine。

结构图如下：

![图片](https://static001.geekbang.org/resource/image/d9/9d/d9a7502b8a368f75cb0d36454119e19d.png?wh=1920x1110)

- Engine：这个是Tomcat的顶层容器，字如其义，一个 Engine就是一个完整的 Servlet 引擎，它接收来自Connector的请求，并传给合适的Host来处理，并将结果返回给Connector。
- Host：表示一个主机，即一个Tomcat可以管理多个虚拟的主机。
- Context：表示一个Web应用，即WebApp下的应用。一个Host可以有多个Context。
- Wrapper：表示一个Servlet，用来具体处理相应请求。一个Context可以有多个Wrapper。

这个多层嵌套的Container结构一直保留着，不过从实际效果上看，Engine和Host其实意义不大了，Docker技术的出现，将Tomcat的这个设计变成了鸡肋。

#### 第四步：Service

现在演化到了Connecter + 多层Container这个结构，继续扩展。用Service这个概念把Connector和Container包含进去了。

![图片](https://static001.geekbang.org/resource/image/f8/bc/f894c7c0c8ea457cb861a6854yy904bc.png?wh=1920x1154)

这样在一个Server中可以包含多个Service，每一个Service都是独立的。一个Service负责维护多个Connector和一个顶层Container。当需要使用多个端口时，只需要配置多个Service。

Tomcat默认会启动一个名为Catalina的Service。

![图片](https://static001.geekbang.org/resource/image/23/fa/23662f5cbb3abb5f347d7f5b72df27fa.png?wh=1920x944)

#### 第五步：生命周期（LifeCycle）

Tomcat中每个组件都有生命周期。Connector和Container都实现了LifeCycle接口。生命周期有BEFORE\_INIT\_EVENT、AFTER\_INIT\_EVENT、START\_EVENT等状态。生命周期相关的方法有init()、start()、stop、getState()等。

#### 第六步：引入NIO

为了支持高并发，在原有的BIO模式下已经很难继续扩展这个能力，于是Tomcat 6.0之后引入了NIO的支持。结构图示如下：

![图片](https://static001.geekbang.org/resource/image/27/48/27368da773161e4b110a231e517b3948.png?wh=1920x605)

对NIO的支持，宏观上主要影响的是Connector这一部分。它是现代Tomcat对高并发提供支持的设计，Tomcat 6.0中就提供了支持，早期的server.xml文件中，我们可以看到这么一个配置：

```plain
<Connector connectionTimeout="20000" maxThreads="1000" port="8080" protocol="org.apache.coyote.http11.Http11NioProtocol" redirectPort="8443"/>

```

这就表明它使用了NIO模式。

总体来看，对大规模企业应用，NIO性能上会明显优于BIO，所以Tomcat 9.0之后干脆就不支持BIO模式了。程序模式由BIO演化到NIO，是为了多路复用，技术上是比较困难的，从实际过程来回顾，这一部分的设计也经历了反复。

开始的结构是这样的：

![图片](https://static001.geekbang.org/resource/image/24/a5/2446a998f9b243ebb7565842bfdcfda5.png?wh=1920x923)

这个结构很庞大，有多个Acceptor和多个Poller，程序复杂性也高。由于复杂性以及实际效果，后面的版本将这个设计缩了回来，从Tomcat 9.0开始，NioEndpoint结构中Acceptor与Poller仅支持定义单个Acceptor和单个Poller。也就是说开始的构思有点过度设计了，可见高手也不是一次性能把事情弄好的，凡事都要不断切磋。现在的版本进一步将NIO变成了NIO2，成了完全的异步模式。

## MiniTomcat的路径

我们自己手写MiniTomcat的目的是学习Tomcat，更好地弄懂它。我们也会按照由简到繁的过程一步步构建，因为我们知道了Tomcat本身的发展过程，所以也按照它的过程一步步走过来。自己手写一遍是最好的学习方式，纸上得来终觉浅，绝知此事要躬行。

实际上，我们只会走到第四步，也就是Connector + 多层Container。这么考虑的原因是后面的内容难度比较高，篇幅也多，应当单独成书，未来有机会我们再公布出来。到了第四步，Tomcat早期版本的核心部分也都包含进来了，对应着Tomcat 6.0之前的状况。

我们在今后的学习过程中，心里要有这个大图景。

## 小结

Tomcat获得了持久的成功，对业界影响深远。这里的关键就在于创始者James Duncan Davidson，他立意高远，眼界宏大，终成数十年以来的“名门正派”。同时，我们也看到了，顶级程序员也不是神仙，并不能一次性构建好一个Server，也需要不断尝试，不断接受真实世界的反馈并调整设计方案，NIO实现中的Acceptor和Poller池最终被废弃就是明证。

我们作为后学者要学会沿着巨人的脚步，一步步前进。对技术的高峰，或许“虽不能至，而心向往焉”，相信沿途也会收获很多悟道的喜悦。

## 思考题

你可以说一说Tomcat的内部构造是怎样的吗，共包含哪几部分？欢迎你把答案分享到评论区，也欢迎你把这节课的内容分享给其他朋友，邀他一起学习。我们下节课再见！