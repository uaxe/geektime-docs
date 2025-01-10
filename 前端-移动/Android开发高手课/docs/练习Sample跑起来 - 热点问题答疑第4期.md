你好，我是孙鹏飞。今天我们回到专栏第7期和第8期，来看看课后练习Sample的运行需要注意哪些问题。另外我结合同学们留言的疑问，也来谈谈文件顺序对I/O的影响，以及关于Linux学习我的一些方法和建议。

[专栏第7期](http://time.geekbang.org/column/article/73651) 的Sample借助于systrace工具，通过字节码处理框架对函数插桩来获取方法执行的trace。这个Sample实现相当完整，你在日常工作也可以使用它。

这个Sample使用起来虽然非常简单，但其内部的实现相对来说是比较复杂的。它的实现涉及Gradle Transform、Task实现、增量处理、ASM字节码处理、mapping文件使用，以及systrace工具的使用等。

对于Gradle来说，我们应该比较熟悉，它是Android平台下的构建工具。对于平时使用来说，我们大多时候只需要关注Android Gradle Plugin的一些参数配置就可以实现很多功能了，官方文档已经提供了很详细的参数设置 [说明](https://developer.android.com/studio/build/?hl=zh-cn)。对于一些需要侵入打包流程的操作，就需要我们实现自己的Task或者Transform代码来完成，比如处理Class和JAR包、对资源做一些处理等。

Gradle学习的困难更多来自于Android Gradle Plugin对Gradle做的一些封装扩展，而这部分Google并没有提供很完善的文档，并且每个版本都有一些接口上的变动。对于这部分内容的学习，我主要是去阅读别人实现的Gradle工具代码和 [Android Gradle Plugin代码](https://android.googlesource.com/platform/tools/base/+/studio-3.2.1/build-system/)。

关于这期的Sample实现，有几个可能产生疑问的地方我们来探讨一下。

这个Sample的Gradle插件是发布到本地Maven库的，所以如果没有执行发布直接编译需要先发布插件库到本地Maven中才能执行编译成功。

另一个可能遇到问题的是，如果你想把Sample使用到其他项目，需要自己将SampleApp中其p的e.systrace.TraceTag”类移植到自己的项目中，否则会产生编译错误。

对于字节码处理，在Sample中主要使用了ASM框架来处理。市面上关于字节码处理的框架有很多，常见的有 [ASM和Javassist框架](https://www.infoq.cn/article/Living-Matrix-Bytecode-Manipulation)，其他的框架你可以使用“Java bytecode manipulation”关键字在Google上搜索。使用字节码处理框架需要对字节码有比较深入的了解，要提醒你的是这里的字节码不是Dalvik bytecode而是Java bytecode。对于字节码的学习，你可以参考 [官方文档](https://docs.oracle.com/javase/specs/jvms/se8/html/index.html) 和《Java虚拟机规范》，里面对字节码的执行规则和指令说明都有很详细的描述。并且还可以配合javap命令查看反编译的字节码对应的源码，这样学习下来会有很好的效果。字节码处理是一个很细微的操作，稍有失误就会产生编译错误、执行错误或者Crash的情况，里面需要注意的地方也非常多，比如Try Catch Block对操作数栈的影响、插入的代码对本地变量表和操作数栈的影响等。

实现AOP的另一种方是可以接操作Dex文件进行Dalvik bytecode字节码注入，关于这种实现方式可以使用 [dexer](https://android.googlesource.com/platform/tools/dexter/) 库来完成，在Facebook的 [Redex](https://github.com/facebook/redex) 中也提供了针对dex的AOP功能。

下面我们来看 [专栏第8期](http://time.geekbang.org/column/article/74044)。我从文章留言里看到，有同学关于数据重排序对I/O性能的影响有些疑问，不太清楚优化的原理。其实这个优化原理理解起来是很容易的，在进行文件读取的操作过程中，系统会读取比预期更多的文件内容并缓存在Page Cache中，这样下一次读请求到来时，部分页面直接从Page Cache读取，而不用再从磁盘中获取数据，这样就加速了读取的操作。在 [《支付宝App构建优化解析》](https://mp.weixin.qq.com/s/79tAFx6zi3JRG-ewoapIVQ) 里“原理”一节中已经有比较详细的描述，我就不多赘述了。如果你对“预读”感兴趣的话，我给你提供一些资料，可以深入了解一下。

预读（readhead）机制的系统源码在 [readhead.c](https://github.com/torvalds/linux/blob/master/mm/readahead.c) 文件中。需要说明的是，预读机制可能在不同系统版本中有所变化，所以下面我提供的资料大多是基于 Linux 2.6.x的内核，在这以后的系统版本可能对 readhead 机制有修改，你需要留意一下。

关于预读机制详细的算法说明可以看 [《Linux readahead: less tricks for more》](https://www.kernel.org/doc/ols/2007/ols2007v2-pages-273-284.pdf) 和 [《Sequential File Prefetching In Linux》](http://www.ece.eng.wayne.edu/~sjiang/Tsinghua-2010/linux-readahead.pdf)、 [《Linux内核的文件预读（readahead）》](http://blog.51cto.com/wangergui/1841294) 这三篇文档。

从专栏前几篇的正文看，很多优化的内容是从Linux的机制入手的，如果你对Linux的机制和优化不了解的话，是不太容易想到这些方案的。举个例子，专栏文章提到的小文件系统是运行在用户态的代码，底层依然依赖现存文件系统提供的功能，因此需要深入了解Linux VFS、ext4的实现，以及它们的优缺点和原理，这样我们才能发现为什么大量的小文件依赖现存的文件系统管理是存在性能缺陷的，以及下一步如何填补这些性能缺陷。

作为Android开发工程师，我们该何学习Linux呢？我其实不建议上来就直接阅读系统源码分析相关的书，我建议是从理解操作系统概念开始，推荐两本操作系统相关的书：《深入理解计算机系统》和《计算机系统 系统架构与操作系统的高度集成》。Linux的系统实现其实和传统的操作系统概念在细节上会有不小的差别，再推荐一本解析Linux操作系统的书《操作系统之编程观察》，这本书结合源码对Linux的各方面机制都进行和很详细的分析。

对于从事Android开发的同学来说，确实很有必要深入了解Linux系统相关的知识，因为Android里很多特性都是依赖底层基础系统的，就比如我刚刚提到的“预读”机制，不光可以用在Android的资源加载上，也可以拓展到Flutter的资源加载上。假如我们以后面对一个不是Linux内核的系统，比如Fuchsia OS，也可以根据已经掌握的系统知识套用到现有的操作系统上，因为像内存管理、文件系统、信号机制、进程调度、系统调用、中断机制、驱动等内容都是共通的，在迁移到新的系统上的时候可以有一个全局的学习视角，帮助我们快速上手。对于操作系统内容，我的学习路线是先熟悉系统机制，然后熟悉系统提供的各个方向的接口，比如I/O操作、进程创建、信号中断处理、线程使用、epoll、通信机制等，按照《UNIX环境高级编程》这本书的内容一步步的走就可以完成这一步骤，熟悉之后可以按照自己的节奏，再去学习自己比较感兴趣的模块。此时可以找一本源码分析的书再去阅读，比如想了解fork机制的实现、I/O操作的read和write在内核态的调度执行，像这些问题就需要有目的性的进行挖掘。

上面这个学习路线是我在学习过程中不断踩坑总结出来的一些经验，对于操作系统我也只是个初学者，也欢迎你留言说说自己学习的经验和问题，一起切磋进步。

最后送出3本“极客周历”给用户故事“ [专栏学得苦？可能是方法没找对](http://time.geekbang.org/column/article/77342)”留言点赞数前三的同学，分别是@坚持远方、@蜗牛、@JIA，感谢同学们的参与。