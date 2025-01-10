相信一直坚持学习专栏的同学对Hook一定不会陌生，在前面很多期里我无数次提到Hook。可能有不少同学对于Hook还是“懵懵懂懂”，那今天我们从来头了解一下什么是Hook。

Hook直译过来就是“钩子”的意思，是指截获进程对某个API函数的调用，使得API的执行流程转向我们实现的代码片段，从而实现我们所需要得功能，这里的功能可以是监控、修复系统漏洞，也可以是劫持或者其他恶意行为。

相信许多新手第一次接触Hook时会觉得这项技术十分神秘，只能被少数高手、黑客所掌握，那Hook是不是真的难以掌握？希望今天的文章可以打消你的顾虑。

## Native Hook的不同流派

对于Native Hook技术，我们比较熟悉的有GOT/PLT Hook、Trap Hook以及Inline Hook，下面我来逐个讲解这些Hook技术的实现原理和优劣比较。

**1\. GOT/PLT Hook**

在 [Chapter06-plus](https://github.com/AndroidAdvanceWithGeektime/Chapter06-plus) 中，我们使用了PLT Hook技术来获取线程创建的堆栈。先来回顾一下它的整个流程，我们将libart.so中的外部函数pthread\_create替换成自己的方法pthread\_create\_hook。

![](https://static001.geekbang.org/resource/image/71/f5/715e03d40d7c5f185959e284c23e9df5.png?wh=1772*1042)

你可以发现，GOT/PLT Hook主要是用于替换某个SO的外部调用，通过将外部函数调用跳转成我们的目标函数。GOT/PLT Hook可以说是一个非常经典的Hook方法，它非常稳定，可以达到部署到生产环境的标准。

那GOT/PLT Hook的实现原理究竟是什么呢？你需要先对SO库文件的ELF文件格式和动态链接过程有所了解。

**ELF格式**

ELF（Executableand Linking Format）是可执行和链接格式，它是一个开放标准，各种UNIX系统的可执行文件大多采用ELF格式。虽然ELF文件本身就支持三种不同的类型（重定位、执行、共享），不同的视图下格式稍微不同，不过它有一个统一的结构，这个结构如下图所示。

![](https://static001.geekbang.org/resource/image/18/96/181d3fed100b9ca11360a03625db5296.png?wh=1242*1324)

网上介绍ELF格式的文章非常多，你可以参考 [《ELF文件格式解析》](https://felixzhang00.github.io/2016/12/24/2016-12-24-ELF%E6%96%87%E4%BB%B6%E8%A3%85%E8%BD%BD%E9%93%BE%E6%8E%A5%E8%BF%87%E7%A8%8B%E5%8F%8Ahook%E5%8E%9F%E7%90%86/)。顾名思义，对于GOT/PLT Hook来说，我们主要关心“.plt”和“.got”这两个节区：

- **.plt**。该节保存过程链接表（Procedure Linkage Table）。

- **.got**。该节保存着全局的偏移量表。


我们也可以使用 `readelf -S` 来查看ELF文件的具体信息。

**链接过程**

接下来我们再来看看动态链接的过程，当需要使用一个Native库（.so文件）的时候，我们需要调用 `dlopen("libname.so")` 来加载这个库。

在我们调用了 `dlopen("libname.so")` 之后，系统首先会检查缓存中已加载的ELF文件列表。如果未加载则执行加载过程，如果已加载则计数加一，忽略该调用。然后系统会用从libname.so的 `dynamic` 节区中读取其所依赖的库，按照相同的加载逻辑，把未在缓存中的库加入加载列表。

你可以使用下面这个命令来查看一个库的依赖：

```
readelf -d <library> | grep NEEDED

```

下面我们大概了解一下系统是如何加载的ELF文件的。

- 读ELF的程序头部表，把所有PT\_LOAD的节区mmap到内存中。

- 从“.dynamic”中读取各信息项，计算并保存所有节区的虚拟地址，然后执行重定位操作。

- 最后ELF加载成功，引用计数加一。


但是这里有一个关键点，在ELF文件格式中我们只有函数的绝对地址。如果想在系统中运行，这里需要经过 **重定位**。这其实是一个比较复杂的问题，因为不同机器的CPU架构、加载顺序不同，导致我们只能在运行时计算出这个值。不过还好动态加载器（/system/bin/linker）会帮助我们解决这个问题。

如果你理解了动态链接的过程，我们再回头来思考一下“.got”和“.plt”它们的具体含义。

- **The Global Offset Table (GOT)**。简单来说就是在数据段的地址表，假定我们有一些代码段的指令引用一些地址变量，编译器会引用GOT表来替代直接引用绝对地址，因为绝对地址在编译期是无法知道的，只有重定位后才会得到 ，GOT自己本身将会包含函数引用的绝对地址。

- **The Procedure Linkage Table (PLT)**。PLT不同于GOT，它位于代码段，动态库的每一个外部函数都会在PLT中有一条记录，每一条PLT记录都是一小段可执行代码。 一般来说，外部代码都是在调用PLT表里的记录，然后PLT的相应记录会负责调用实际的函数。我们一般把这种设定叫作“ [蹦床](http://en.wikipedia.org/wiki/Trampoline_%28computing%29)”（Trampoline）。


PLT和GOT记录是一一对应的，并且GOT表第一次解析后会包含调用函数的实际地址。既然这样，那PLT的意义究竟是什么呢？PLT从某种意义上赋予我们一种懒加载的能力。当动态库首次被加载时，所有的函数地址并没有被解析。下面让我们结合图来具体分析一下首次函数调用，请注意图中黑色箭头为跳转，紫色为指针。

![](https://static001.geekbang.org/resource/image/b8/33/b86ff32360acd5151050fd30e1762233.png?wh=438*288)

- 我们在代码中调用func，编译器会把这个转化为func@plt，并在PLT表插入一条记录。

- PLT表中第一条（或者说第0条）PLT\[0\]是一条特殊记录，它是用来帮助我们解析地址的。通常在类Linux系统，这个的实现会位于动态加载器，就是专栏前面文章提到的/system/bin/linker。

- 其余的PLT记录都均包含以下信息：
  - 跳转GOT表的指令（jmp \*GOT\[n\]）。

  - 为上面提到的第0条解析地址函数准备参数。

  - 调用PLT\[0\]，这里resovler的实际地址是存储在GOT\[2\] 。
- 在解析前GOT\[n\]会直接指向jmp \*GOT\[n\]的下一条指令。在解析完成后，我们就得到了func的实际地址，动态加载器会将这个地址填入GOT\[n\]，然后调用func。


如果对上面的这个调用流程还有疑问，你可以参考 [《GOT表和PLT表》](https://www.jianshu.com/p/0ac63c3744dd) 这篇文章，它里面有一张图非常清晰。

![](https://static001.geekbang.org/resource/image/8b/c6/8bacb98e41eaa8ed048294dbf42896c6.png?wh=1000*664)

当第一次调用发生后，之后再调用函数func就高效简单很多。首先调用PLT\[n\]，然后执行jmp \*GOT\[n\]。GOT\[n\]直接指向func，这样就高效的完成了函数调用。

![](https://static001.geekbang.org/resource/image/08/1e/08d7d70593533b9908426945d16ad91e.png?wh=396*335)

总结一下，因为很多函数可能在程序执行完时都不会被用到，比如错误处理函数或一些用户很少用到的功能模块等，那么一开始把所有函数都链接好实际就是一种浪费。为了提升动态链接的性能，我们可以使用PLT来实现延迟绑定的功能。

对于函数运行的实际地址，我们依然需要通过GOT表得到，整个简化过程如下：

![](https://static001.geekbang.org/resource/image/69/27/698af1afdf2327233ef5bf2d09df4c27.png?wh=1406*970)

看到这里，相信你已经有了如何Hack这一过程的初步想法。这里业界通常会根据修改PLT记录或者GOT记录区分为GOT Hook和PLT Hook，但其本质原理十分接近。

**GOT/PLT Hook实践**

GOT/PLT Hook看似简单，但是实现起来也是有一些坑的，需要考虑兼容性的情况。一般来说，推荐使用业界的成熟方案。

- 微信Matrix开源库的 [ELF Hook](https://github.com/Tencent/matrix/tree/master/matrix/matrix-android/matrix-android-commons/src/main/cpp/elf_hook)，它使用的是GOT Hook，主要使用它来做性能监控。

- 爱奇艺开源的的 [xHook](https://github.com/iqiyi/xHook)，它使用的也是GOT Hook。

- Facebook的 [PLT Hook](https://github.com/facebookincubator/profilo/tree/master/deps/plthooks)。


如果不想深入它内部的原理，我们只需要直接使用这些开源的优秀方案就可以了。因为这种Hook方式非常成熟稳定，除了Hook线程的创建，我们还有很多其他的使用范例。

- “I/O优化”中使用 [matrix-io-canary](https://github.com/Tencent/matrix/tree/master/matrix/matrix-android/matrix-io-canary) Hook文件的操作。

- “网络优化”中使用Hook了Socket的相关操作，具体你可以参考 [Chapter17](https://github.com/AndroidAdvanceWithGeektime/Chapter17)。


这种Hook方法也不是万能的，因为它只能替换导入函数的方式。有时候我们不一定可以找到这样的外部调用函数。如果想Hook函数的内部调用，这个时候就需要用到我们的Trap Hook或者Inline Hook了。

**2\. Trap Hook**

对于函数内部的Hook，你可以先从头想一下，会发现调试器就具备一切Hook框架具有的能力，可以在目标函数前断住程序，修改内存、程序段，继续执行。相信很多同学都会使用调试器，但是对调试器如何工作却知之甚少。下面让我们先了解一下软件调试器是如何工作的。

**ptrace**

一般软件调试器都是通过ptrace系统调用和SIGTRAP配合来进行断点调试，首先我们来了解一下什么是ptrace，它又是如何断住程序运行，然后修改相关执行步骤的。

所谓合格的底层程序员，对于未知知识的了解，第一步就是使用 `man` 命令来查看系统文档。

> The ptrace() system call provides a means by which one process (the “tracer”) may observe and control the execution of another process (the “tracee”), and examine and change the tracee’s memory and registers. It is primarily used to implement breakpoint debugging and system call tracing.

这段话直译过来就是，ptrace提供了一种让一个程序（tracer）观察或者控制另一个程序（tracee）执行流程，以及修改被控制程序内存和寄存器的方法，主要用于实现调试断点和系统调用跟踪。

我们再来简单了解一下调试器（GDB/LLDB）是如何使用ptrace的。首先调试器会基于要调试进程是否已启动，来决定是使用fork或者attach到目标进程。当调试器与目标程序绑定后，目标程序的任何signal（除SIGKILL）都会被调试器做先拦截，调试器会有机会对相关信号进行处理，然后再把执行权限交由目标程序继续执行。可以你已经想到了，这其实已经达到了Hook的目的。

**如何Hook**

但更进一步思考，如果我们不需要修改内存或者做类似调试器一样复杂的交互，我们完全可以不依赖ptrace，只需要接收相关signal即可。这时我们就想到了句柄（signal handler）。对！我们完全可以主动raise signal，然后使用signal handler来实现类似的Hook效果。

业界也有不少人将Trap Hook叫作断点Hook，它的原理就是在需要Hook的地方想办法触发断点，并捕获异常。一般我们会利用SIGTRAP或者SIGKILL（非法指令异常）这两种信号。下面以SIGTRAP信号为例，具体的实现步骤如下。

![](https://static001.geekbang.org/resource/image/07/cc/0746c1505e06c80345cbeb30b7c6c6cc.png?wh=1920*842)

- 注册信号接收句柄（signal handler），不同的体系结构可能会选取不同的信号，我们这里用SIGTRAP。

- 在我们需要Hook得部分插入Trap指令。

- 系统调用Trap指令，进入内核模式，调用我们已经在开始注册好的信号接收句柄（signal handler）。

- 执行我们信号接收句柄（signal handler），这里需要注意，所有在信号接收句柄（signal handler）执行的代码需要保证 [async-signal-safe](http://man7.org/linux/man-pages/man7/signal-safety.7.html)。这里我们可以简单的只把信号接收句柄当作蹦床，使用logjmp跳出这个需要async-signal-safe（正如我在“崩溃分析”所说的，部分函数在signal回调中使用并不安全）的环境，然后再执行我们Hook的代码。

- 在执行完Hook的函数后，我们需要恢复现场。这里如果我们想继续调用原来的函数A，那直接回写函数A的原始指令并恢复寄存器状态。


**Trap Hook实践**

Trap Hook兼容性非常好，它也可以在生产环境中大规模使用。但是它最大的问题是效率比较低，不适合Hook非常频繁调用的函数。

对于Trap Hook的实践方案，在“ [卡顿优化（下）](https://time.geekbang.org/column/article/72642)”中，我提到过Facebook的 [Profilo](https://github.com/facebookincubator/profilo)，它就是通过定期发送SIGPROF信号来实现卡顿监控的。

**3\. Inline Hook**

跟Trap Hook一样，Inline Hook也是函数内部调用的Hook。它直接将函数开始（Prologue）处的指令更替为跳转指令，使得原函数直接跳转到Hook的目标函数函数，并保留原函数的调用接口以完成后续再调用回来的目的。

与GOT/PLT Hook相比，Inline Hook可以不受GOT/PLT表的限制，几乎可以Hook任何函数。不过其实现十分复杂，我至今没有见过可以用在生产环境的实现。并且在ARM体系结构下，无法对叶子函数和很短的函数进行Hook。

在深入“邪恶的”细节前，我们需要先对Inline Hook的大体流程有一个简单的了解。

![](https://static001.geekbang.org/resource/image/b7/56/b78e7fd925a5299b13058ef54d094d56.jpg?wh=1254*656)

如图所示，Inline Hook的基本思路就是在已有的代码段中插入跳转指令，把代码的执行流程转向我们实现的Hook函数中，然后再进行指令修复，并跳转回原函数继续执行。这段描述看起来是不是十分简单而且清晰？

对于Trap Hook，我们只需要在目标地址前插入特殊指令，并且在执行结束后把原始指令写回去就可以了。但是对Inline Hook来说，它是直接进行指令级的复写与修复。怎么理解呢？就相当于我们在运行过程中要去做ASM的字节码修改。

当然Inline Hook远远比ASM操作更加复杂，因为它还涉及不同CPU架构带来的指令集适配问题，我们需要根据不同指令集来分别进行指令复写与跳转。

下面我先来简单说明一下Android常见的CPU架构和指令集：

- **x86和MIPS架构**。这两个架构已经基本没有多少用户了，我们可以直接忽视。一般来说我们只关心主流的ARM体系架构就可以了。

- **ARMv5和ARMv7架构**。它的指令集分为4字节对齐的定长的ARM指令集和2字节对齐的变长Thumb/Thumb-2指令集。Thumb-2指令集虽为2字节对齐，但指令集本身有16位也有32位。其中ARMv5使用的是16位的Thumb16，在ARMv7使用的是32位的Thumb32。 **不过目前ARMv5也基本没有多少用户了，我们也可以放弃Thumb16指令集的适配**。

- **ARMv8架构**。64位的ARMv8架构可以兼容运行32位，所以它在ARM32和Thumb32指令集的基础上，增加了ARM64指令集。关于它们具体差异，你可以查看 [ARM的官方文档](http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0801b/IBAIEGDJ.html)。


ARM64目前我还没有适配，不过Google Play要求所有应用在2019年8月1日之前需要支持64位，所以今年上半年也要折腾一下。但它们的原理基本类似，下面我以最主流的ARMv7架构为例，为你庖丁解牛Inline Hook。

**ARM32指令集**

ARMv7中有一种广为流传的 `$PC=$PC+8` 的说法。这是指ARMv7中的三级流水线（取指、解码、执行），换句话说 `$PC` 寄存器总是指向正在取指的指令，而不是指向正在执行的指令。取指总会比执行快2个指令，在ARM32指令集下2个指令的长度为8个字节，所以 `$PC` 寄存器的值总是比当前指令地址要大8。

![](https://static001.geekbang.org/resource/image/bb/f9/bb8ea924c24a27638d575e25ca101cf9.png?wh=715*373)

是不是感觉有些复杂，其实这是为了引出ARM指令集的常用跳转方法：

```
LDR PC, [PC, #-4] ;0xE51FF004
$TRAMPOLIN_ADDR

```

在了解了三级流水线以后，就不会对这个PC-4有什么疑惑了。

按照我们前面描述的Inline Hook的基本步骤，首先插入跳转指令，跳入我们的蹦床（Trampoline），执行我们实现的Hook后函数。这里还有一个“邪恶的”细节，由于指令执行是依赖当前运行环境的，即所有寄存器的值，而我们插入新的指令是有可能更改寄存器的状态的，所以我们要保存当前全部的寄存器状态到栈中，使用BLX指令跳转执行Hook后函数，执行完成后，再从栈中恢复所有的寄存器，最后才能像未Hook一样继续执行原先函数。

![](https://static001.geekbang.org/resource/image/05/2d/0589d761c3079aad02287b13a7c0612d.jpg?wh=1292*638)

在执行完Hook后的函数后，我们需要跳转回原先的函数继续执行。这里不要忘记我们在一开始覆盖的LDR指令，我们需要先执行被我们复写的指令，然后再使用如下指令，继续执行原先函数。

```
LDR PC, [PC, #-4]
HOOKED_ADDR+8

```

是不是有一种大功告成的感觉？其实这里还有一个巨大的坑在等着我们，那就是 **指令修复**。前面我提到保存并恢复了寄存器原有的状态，已达到可以继续像原有程序一样的继续执行。但仅仅是恢复寄存器就足够么？显然答案是否定的，虽然寄存器被我们完美恢复了，但是2条备份的指令被移动到了新的地址。当执行它们的时候， `$PC` 寄存器的值是与原先不同的。这条指令的操作如果涉及 `$PC` 的值，那么它们将会执行出完全不同的结果。

到这里我就不对指令修复再深入解析了，感兴趣的同学可以在留言区进行讨论。

**Inline Hook实践**

对于Inline Hook，虽然它功能非常强大，而且执行效率也很高，但是业界目前还没有一套完全稳定可靠的开源方案。Inline Hook一般会使用在自动化测试或者线上疑难问题的定位，例如“UI优化”中说到libhwui.so崩溃问题的定位，我们就是利用Inline Hook去收集系统信息。

业界也有一些不错的参考方案：

- [Cydia Substrate](http://www.cydiasubstrate.com/)。在 [Chapter3](https://github.com/AndroidAdvanceWithGeektime/Chapter03) 中，我们就使用它来Hook系统的内存分配函数。

- [adbi](https://github.com/crmulliner/adbi)。支付宝在 [GC抑制](https://juejin.im/post/5be1077d518825171140dbfa) 中使用的Hook框架，不过已经好几年没有更新了。


## 各个流派的优缺点比较

最后我们再来总结一下不同的Hook方式的优缺点：

1.GOT/PLT Hook是一个比较中庸的方案，有较好的性能，中等的实现难度，但其只能Hook动态库之间的调用的函数，并且无法Hook未导出的私有函数，而且只存在安装与卸载2种状态，一旦安装就会Hook所有函数调用。

2.Trap Hook最为稳定，但由于需要切换运行模式（R0/R3），且依赖内核的信号机制，导致性能很差。

3.Inline Hook是一个非常激进的方案，有很好的性能，并且也没有PLT作用域的限制，可以说是一个非常灵活、完美的方案。但其实现难度极高，我至今也没有看到可以部署在生产环境的Inline Hook方案，因为涉及指令修复，需要编译器的各种优化。

![](https://static001.geekbang.org/resource/image/db/b9/dbaf5281ac153571b5f2b93f75ae2db9.jpg?wh=1186*430)

但是需要注意，无论是哪一种Hook都只能Hook到应用自身的进程，我们无法替换系统或其他应用进程的函数执行。

## 总结

总的来说Native Hook是一门非常底层的技术，它会涉及库文件编译、加载、链接等方方面面的知识，而且很多底层知识是与Android甚至移动平台无关的。

在这一领域，做安全的同学可能会更有发言权，我来讲可能班门弄斧了。不过希望通过这篇文章，让你对看似黑科技的Hook有一个大体的了解，希望可以在自己的平时的工作中使用Hook来完成一些看似不可能的任务，比如修复系统Bug、线上监控Native内存分配等。

## 课后作业

今天的信息量是不是有点大？关于Native Hook，你对它有什么看法，还有哪些疑问？欢迎留言跟我和其他同学一起讨论。

Native Hook技术的确非常复杂，即使我们不懂得它的内部原理，我们也应该学会使用成熟的开源框架去实现一些功能。当然对于想进一步深入研究的同学，推荐你学习下面这些资料。

- [链接程序和库指南](https://docs.oracle.com/cd/E37934_01/pdf/E36754.pdf)

- [程序员的自我修养：链接、装载与库](https://item.jd.com/10067200.html)

- [链接器和加载器 Linkers and Loaders](https://item.jd.com/42971729145.html)

- [Linux二进制分析 Learning Linux Binary Analysis](https://item.jd.com/12240585.html)


如果你对调试器的研究也非常有兴趣，强烈推荐 [Eli Bendersky](https://eli.thegreenplace.net/) 写的博客，里面有一系列非常优秀的底层知识文章。其中一些关于debugger的，感兴趣的同学可以去阅读，并亲手实现一个简单的调试器。

- [how-debuggers-work-part-1](https://eli.thegreenplace.net/2011/01/23/how-debuggers-work-part-1)

- [how-debuggers-work-part-2-breakpoints](https://eli.thegreenplace.net/2011/01/27/how-debuggers-work-part-2-breakpoints)

- [how-debuggers-work-part-3-debugging-information](https://eli.thegreenplace.net/2011/02/07/how-debuggers-work-part-3-debugging-information)


欢迎你点击“请朋友读”，把今天的内容分享给好友，邀请他一起学习。最后别忘了在评论区提交今天的作业，我也为认真完成作业的同学准备了丰厚的“学习加油礼包”，期待与你一起切磋进步哦。