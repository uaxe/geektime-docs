你好，我是陈皓，网名左耳朵耗子。

前两篇文章分享的是系统底层方面的内容，今天我们进入高手成长篇的第二部分——Java底层知识。

# Java 字节码相关

首先，Java最黑科技的玩法就是字节码编程，也就是动态修改或是动态生成Java字节码。Java的字节码相当于汇编，其中的一些细节你可以从下面的这几个教程中学习。

- [Java Zone: Introduction to Java Bytecode](https://dzone.com/articles/introduction-to-java-bytecode) ，这篇文章图文并茂地向你讲述了Java字节码的一些细节，是一篇很不错的入门文章。

- [IBM DeveloperWorks: Java bytecode](https://www.ibm.com/developerworks/library/it-haggar_bytecode/index.html) ，虽然这篇文章很老了，但是这篇文章是一篇非常好的讲Java 字节码的文章。

- [Java Bytecode and JVMTI Examples](https://github.com/jon-bell/bytecode-examples)，这是一些使用 [JVM Tool Interface](http://docs.oracle.com/javase/7/docs/platform/jvmti/jvmti.html) 操作字节码的比较实用的例子。包括方法调用统计、静态字节码修改、Heap Taggin和Heap Walking。


当然，一般来说，我们不使用JVMTI操作字节码，而是用一些更好用的库。这里有三个库可以帮你比较容易地做这个事。

- [asmtools](https://wiki.openjdk.java.net/display/CodeTools/asmtools) \- 用于生产环境的Java .class文件开发工具。
- [Byte Buddy](http://bytebuddy.net/) \- 代码生成库：运行时创建Class文件而不需要编译器帮助。
- [Jitescript](https://github.com/qmx/jitescript) \- 和 [BiteScript](https://github.com/headius/bitescript) 类似的字节码生成库。

就我而言，我更喜欢Byte Buddy，它在2015年还获了Oracle的 “ [Duke’s Choice](https://www.oracle.com/corporate/pressrelease/dukes-award-102815.html)”大奖，其中说Byte Buddy极大地发展了Java的技术。

使用字节码编程可以玩出很多高级玩法，最高级的还是在Java程序运行时进行字节码修改和代码注入。听起来是不是一些很黑客，也很黑科技的事？是的，这个方式使用Java这门静态语言在运行时可以进行各种动态的代码修改，而且可以进行无侵入的编程。

比如， 我们不需要在代码中埋点做统计或监控，可以使用这种技术把我们的监控代码直接以字节码的方式注入到别人的代码中，从而实现对实际程序运行情况进行统计和监控。如果你看过我的《编程范式游记》，你就知道这种技术的威力了，其可以很魔法地把业务逻辑和代码控制分离开来。

要做到这个事，你还需要学习一个叫Java Agent的技术。Java Agent使用的是 “ [Java Instrumentation API](https://stackoverflow.com/questions/11898566/tutorials-about-javaagents)”，其主要方法是实现一个叫 `premain()` 的方法（嗯，一个比 `main()` 函数还要超前执行的 main 函数），然后把你的代码编译成一个jar文件。

在JVM启动时，使用这样的命令行来引入你的jar文件： `java -javaagent:yourAwesomeAgent.jar -jar App.jar`。更为详细的文章你可以参看：“ [Java Code Geeks: Java Agents](https://www.javacodegeeks.com/2015/09/java-agents.html)”，你还可以看一下这个示例项目： [jvm-monitoring-agent](https://github.com/toptal/jvm-monitoring-agent) 或是 [EntryPointKR/Agent.java](https://gist.github.com/EntryPointKR/152f089f6f3884047abcd19d39297c9e)。如果想用ByteBuddy来玩，你可以看看这篇文章 “ [通过使用Byte Buddy，便捷地创建Java Agent](http://www.infoq.com/cn/articles/Easily-Create-Java-Agents-with-ByteBuddy)”。如果你想学习如何用Java Agent做监控，你可以看一下这个项目 [Stage Monitor](http://www.stagemonitor.org/)。

# JVM 相关

接下来讲讲Java底层知识中另一个非常重要的内容——JVM。

说起JVM，你有必要读一下JVM的规格说明书，我在这里放一个Java 8的， [The Java Virtual Machine Specification Java SE 8 Edition](https://docs.oracle.com/javase/specs/jvms/se8/jvms8.pdf) 。对于规格说明书的阅读，我认为是系统了解JVM规范的最佳文档，这个文档可以让你对于搞不清楚或是诡异的问题恍然大悟。关于中文翻译，有人在GitHub上开了个Repo - “ [java-virtual-machine-specification](https://github.com/waylau/java-virtual-machine-specification)”。

另外，也推荐一下 [JVM Anatomy Park](https://shipilev.net/jvm-anatomy-park/) JVM解剖公园，这是一个系列的文章，每篇文章都不长，但是都很精彩，带你一点一点地把JVM中的一些技术解开。

学习Java底层原理还有Java的内存模型，官方文章是 [JSR 133](http://www.jcp.org/en/jsr/detail?id=133)。还有马里兰大学的威廉·皮尤（William Pugh）教授收集的和Java内存模型相关的文献 - [The Java Memory Model](http://www.cs.umd.edu/~pugh/java/memoryModel/) ，你可以前往浏览。

对于内存方面，道格·利（Doug Lea）有两篇文章也是很有价值的。

- [The JSR-133 Cookbook for Compiler Writers](http://gee.cs.oswego.edu/dl/jmm/cookbook.html)，解释了怎样实现Java内存模型，特别是在考虑到多处理器（或多核）系统的情况下，多线程和读写屏障的实现。

- [Using JDK 9 Memory Order Modes](http://gee.cs.oswego.edu/dl/html/j9mm.html)，讲了怎样通过VarHandle来使用plain、opaque、release/acquire和volatile四种共享内存的访问模式，并剖析了底层的原理。


垃圾回收机制也是需要好好学习的，在这里推荐一本书 《 [The Garbage Collection Handbook](https://book.douban.com/subject/6809987/)》，在豆瓣上的得分居然是9.9（当然，评价人数不多）。这本书非常全面地介绍了垃圾收集的原理、设计和算法。但是这本书也是相当难啃的。中文翻译《 [垃圾回收算法手册](https://book.douban.com/subject/26740958/)》翻译得很一般，有人说翻译得很烂。所以，如果可能，还是读英文版的。如果你对从事垃圾回收相关的工作有兴趣，那么你需要好好看一下这本书。

当然，更多的人可能只需要知道怎么调优垃圾回收， 那么推荐读读 [Garbage Collection Tuning Guide](http://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/) ，它是Hotspot Java虚拟机的垃圾回收调优指南，对你很有帮助。

[Quick Tips for Fast Code on the JVM](https://gist.github.com/djspiewak/464c11307cabc80171c90397d4ec34ef) 也是一篇很不错的文章，里面有写出更快的Java代码的几个小提示，值得一读。

# 小结

好了，总结一下今天学到的内容。Java最黑科技的玩法就是字节码编程，也就是动态修改或是动态生成Java字节码。Java的字节码相当于汇编，学习其中的细节很有意思，为此我精心挑选了3篇文章，供你学习。我们一般不使用JVMTI操作字节码，而是用一些更好用的库，如asmtools、Byte Buddy和BiteScript等。使用字节码编程可以玩出很多高级玩法，其中最高级的玩法是在Java程序运行时进行字节码修改和代码注入。同时，我介绍了Java Agent技术，帮助你更好地实现这种高级玩法。

JVM也是学习Java过程中非常重要的一部分内容。我推荐阅读一下JVM的规格说明书，我认为，它是系统了解JVM规范的最佳文档，可以让你对于搞不清楚或是诡异的问题恍然大悟。同时推荐了 [JVM Anatomy Park](https://shipilev.net/jvm-anatomy-park/) 系列文章，也非常值得一读。

随后介绍的是Java的内存模型和垃圾回收机制，尤其给出了如何调优垃圾回收方面的资料。这些内容都很底层，但也都很重要。对于想成为高手的你来说，还是有必要花时间来啃一啃的。

下篇文章是数据库方面的内容，我们将探讨各种类型的数据库，非常有意思。敬请期待。

下面是《程序员练级攻略》系列文章的目录。

- [开篇词](https://time.geekbang.org/column/article/8136)
- 入门篇
  - [零基础启蒙](https://time.geekbang.org/column/article/8216)
  - [正式入门](https://time.geekbang.org/column/article/8217)
- 修养篇
  - [程序员修养](https://time.geekbang.org/column/article/8700)
- 专业基础篇
  - [编程语言](https://time.geekbang.org/column/article/8701)
  - [理论学科](https://time.geekbang.org/column/article/8887)
  - [系统知识](https://time.geekbang.org/column/article/8888)
- 软件设计篇
  - [软件设计](https://time.geekbang.org/column/article/9369)
- 高手成长篇
  - [Linux系统、内存和网络（系统底层知识）](https://time.geekbang.org/column/article/9759)
  - [异步I/O模型和Lock-Free编程（系统底层知识）](https://time.geekbang.org/column/article/9851)
  - [Java底层知识](https://time.geekbang.org/column/article/10216)
  - [数据库](https://time.geekbang.org/column/article/10301)
  - [分布式架构入门（分布式架构）](https://time.geekbang.org/column/article/10603)
  - [分布式架构经典图书和论文（分布式架构）](https://time.geekbang.org/column/article/10604)
  - [分布式架构工程设计(分布式架构)](https://time.geekbang.org/column/article/11232)
  - [微服务](https://time.geekbang.org/column/article/11116)
  - [容器化和自动化运维](https://time.geekbang.org/column/article/11665)
  - [机器学习和人工智能](https://time.geekbang.org/column/article/11669)
  - [前端基础和底层原理（前端方向）](https://time.geekbang.org/column/article/12271)
  - [前端性能优化和框架（前端方向）](https://time.geekbang.org/column/article/12389)
  - [UI/UX设计（前端方向）](https://time.geekbang.org/column/article/12486)
  - [技术资源集散地](https://time.geekbang.org/column/article/12561)