你好，我是盛延敏。今天是网络编程课程的第一课，我想你一定满怀热情，期望快速进入到技术细节里，了解那些你不熟知的编程技能。而今天我却想和你讲讲历史，虽然这些事情看着不是“干货”，但它可以帮助你理解网络编程中各种技术的来龙去脉。

你我都是程序员，说句实在话，我们正处于一个属于我们的时代里，我们也正在第一线享受着这个时代的红利。在我看来，人类历史上还从来没有一项技术可以像互联网一样深刻地影响人们生活的方方面面。

而具体到互联网技术里，有两件事最为重要，一个是TCP/IP协议，它是万物互联的事实标准；另一个是Linux操作系统，它是推动互联网技术走向繁荣的基石。

今天，我就带你穿越时间的走廊，看一看TCP/IP事实标准和Linux操作系统是如何一步一步发展到今天的。

## TCP发展历史

一般来说，我们认为互联网起源于阿帕网（ARPANET）。

最早的阿帕网还是非常简陋的，网络控制协议（Network Control Protocol，缩写NCP）是阿帕网中连接不同计算机的通信协议。

在构建阿帕网（ARPANET）之后，其他数据传输技术的研究又被摆上案头。NCP诞生两年后，NCP的开发者温特·瑟夫（Vinton Cerf）和罗伯特·卡恩（Robert E. Kahn）一起开发了一个阿帕网的下一代协议，并在1974年发表了以分组、序列化、流量控制、超时和容错等为核心的一种新型的网络互联协议，一举奠定了TCP/IP协议的基础。

### OSI & TCP/IP

在这之后，TCP/IP逐渐发展。咱们话分两头说，一头是一个叫ISO的组织发现计算机设备的互联互通是一个值得研究的新领域，于是，这个组织出面和众多厂商游说，“我们一起定义，出一个网络互联互通的标准吧，这样大家都遵守这个标准，一起把这件事情做大，大家就有钱赚了”。众多厂商觉得可以啊，于是ISO组织就召集了一帮人，认真研究起了网络互联这件事情，还真的搞出来一个非常强悍的标准，这就是OSI参考模型。这里我不详细介绍OSI参考模型了，你可以阅读 [罗剑锋老师的专栏](https://time.geekbang.org/column/article/99286)，他讲得很好。

这个标准发布的时候已经是1984年了，有点尴尬的是，OSI搞得是很好，大家也都很满意，不过，等它发布的时候，ISO组织却惊讶地发现满世界都在用一个叫做TCP/IP协议栈的东西，而且，跟OSI标准半毛钱关系都没有。

这就涉及到了另一头——TCP/IP的发展。

事实上，我在前面提到的那两位牛人卡恩和瑟夫，一直都在不遗余力地推广TCP/IP。当然，TCP/IP的成功也不是偶然的，而是综合了几个因素后的结果：

1. TCP/IP是免费或者是少量收费的，这样就扩大了使用人群；
2. TCP/IP搭上了UNIX这辆时代快车，很快推出了基于套接字（socket）的实际编程接口；
3. 这是最重要的一点，TCP/IP来源于实际需求，大家都在翘首盼望出一个统一标准，可是在此之前实际的问题总要解决啊，TCP/IP解决了实际问题，并且在实际中不断完善。

回过来看，OSI的七层模型定得过于复杂，并且没有参考实现，在一定程度上阻碍了普及。

不过，OSI教科书般的层次模型，对后世的影响很深远，一般我们说的4层、7层，也是遵从了OSI模型的定义，分别指代传输层和应用层。

我们说TCP/IP的应用层对应了OSI的应用层、表示层和会话层；TCP/IP的网络接口层对应了OSI的数据链路层和物理层。

![](https://static001.geekbang.org/resource/image/cb/b4/cb34e0e3b7769498ea703fe6231201b4.png?wh=958*738)

## UNIX操作系统发展历史

前面我们提到了TCP/IP协议的成功，离不开UNIX操作系统的发展。接下来我们就看下UNIX操作系统是如何诞生和演变的。

下面这张图摘自 [维基百科](https://en.wikipedia.org/wiki/File:Unix_timeline.en.svg)，它将UNIX操作系统几十年的发展历史表述得非常清楚。

![](https://static001.geekbang.org/resource/image/a6/0f/a68c3b9b267574ea2f309ed6a4e0de0f.png?wh=1579*1198)

UNIX的各种版本和变体都起源于在PDP-11系统上运行的UNIX分时系统第6版（1976年）和第7版（1979年），它们通常分别被称为V6和V7。这两个版本是在贝尔实验室以外首先得到广泛应用的UNIX系统。

这张图画得比较概括，我们主要从这张图上看3个分支：

- 图上标示的Research橘黄色部分，是由AT&T贝尔实验室不断开发的UNIX研究版本，从此引出UNIX分时系统第8版、第9版，终止于1990年的第10版（10.5）。这个版本可以说是操作系统界的少林派。天下武功皆出少林，世上UNIX皆出自贝尔实验室。
- 图中最上面所标识的操作系统版本，是加州大学伯克利分校（BSD）研究出的分支，从此引出4.xBSD实现，以及后面的各种BSD版本。这个可以看做是学院派。在历史上，学院派有力地推动了UNIX的发展，包括我们后面会谈到的socket套接字都是出自此派。
- 图中最下面的那一个部分，是从AT&T分支的商业派，致力于从UNIX系统中谋取商业利润。从此引出了System III和System V（被称为UNIX的商用版本），还有各大公司的UNIX商业版。

下面这张图也是源自维基百科，将UNIX的历史表达得更为详细。

![](https://static001.geekbang.org/resource/image/df/bb/df2b6d77a0a46e3d9b068f6d517a15bb.png?wh=2560*1774)

一个基本事实是，网络编程套接字接口，最早是在BSD 4.2引入的，这个时间大概是1983年，几经演变后，成为了事实标准，包括System III/V分支也吸收了这部分能力，在上面这张大图上也可以看出来。

其实这张图也说明了一个很有意思的现象，BSD分支、System III/System V分支、正统的UNIX分时系统分支都是互相借鉴的，也可以说是互相“抄袭”吧。但如果这样发展下去，互相不买对方的账，导致上层的应用程序在不同的UNIX版本间不能很好地兼容，这该怎么办？这里先留一个疑问，你也可以先想一想，稍后我会给你解答。

下面我再介绍几个你耳熟能详的重要UNIX玩家。

### SVR 4

SVR4（UNIX System V Release 4）是AT&T的UNIX系统实验室的一个商业产品。它基本上是一个操作系统的大杂烩，这个操作系统之所以重要，是因为它是System III/V分支各家商业化UNIX操作系统的“先祖”，包括IBM的AIX、HP的HP-UX、SGI的IRIX、Sun（后被Oracle收购）的Solaris等等。

### Solaris

Solaris是由Sun Microsystems（现为Oracle）开发的UNIX系统版本，它基于SVR4，并且在商业上获得了不俗的成绩。2005年，Sun Microsystems开源了Solaris操作系统的大部分源代码，作为OpenSolaris开放源代码操作系统的一部分。相对于Linux，这个开源操作系统的进展比较一般。

### BSD

BSD（Berkeley Software Distribution），我们上面已经介绍过了，是由加州大学伯克利分校的计算机系统研究组（CSRG）研究开发和分发的。4.2BSD于1983年问世，其中就包括了网络编程套接口相关的设计和实现，4.3BSD则于1986年发布，正是由于TCP/IP和BSD操作系统的完美拍档，才有了TCP/IP逐渐成为事实标准的这一历史进程。

### macOS X

用mac笔记本的同学都有这样的感觉：macOS提供的环境和Linux环境非常像，很多代码可以在macOS上以接近线上Linux真实环境的方式运行。

有心的同学应该想过，这背后有一定的原因。

答案其实很简单，macOS和Linux的血缘是相近的，它们都是UNIX基础上发展起来的，或者说，它们各自就是一个类UNIX的系统。

macOS系统又被称为Darwin，它已被验证过就是一个UNIX操作系统。如果打开Mac系统的socket.h头文件定义，你会明显看到macOS系统和BSD千丝万缕的联系，说明这就是从BSD系统中移植到macOS系统来的。

## Linux

我们把Linux操作系统单独拿出来讲，是因为它实在太重要了，全世界绝大部分数据中心操作系统都是跑在Linux上的，就连手机操作系统Android，也是一个被“裁剪”过的Linux操作系统。

Linux操作系统的发展有几个非常重要的因素，这几个因素叠加在一起，造就了如今Linux非凡的成就。我们一一来看。

### UNIX的出现和发展

第一个就是UNIX操作系统，要知道，Linux操作系统刚出世的时候， 4.2/4.3 BSD都已经出现快10年了，这样就为Linux系统的发展提供了一个方向，而且Linux的开发语言是C语言，C语言也是在UNIX开发过程中发明的一种语言。

### POSIX标准

UNIX操作系统虽然好，但是它的源代码是不开源的。那么如何向UNIX学习呢？这就要讲一下POSIX标准了，POSIX（Portable Operating System Interface for Computing Systems）这个标准基于现有的UNIX实践和经验，描述了操作系统的调用服务接口。有了这么一个标准，Linux完全可以去实现并兼容它，这从最早的Linux内核头文件的注释可见一斑。

这个头文件里定义了一堆POSIX宏，并有一句注释：“嗯，也许只是一个玩笑，不过我正在完成它。”

```
# ifndef _UNISTD_H

# define _UNISTD_H

/* ok, this may be a joke, but I'm working on it */

# define _POSIX_VERSION  198808L

# define _POSIX_CHOWN_RESTRICTED /* only root can do a chown (I think..) */

/* #define _POSIX_NO_TRUNC*/ /* pathname truncation (but see in kernel) */

# define _POSIX_VDISABLE '\0' /* character to disable things like ^C */

/*#define _POSIX_SAVED_IDS */ /* we'll get to this yet */

/*#define _POSIX_JOB_CONTROL */ /* we aren't there quite yet. Soon hopefully */

```

POSIX相当于给大厦画好了图纸，给Linux的发展提供了非常好的指引。这也是为什么我们的程序在macOS和Linux可以兼容运行的原因，因为大家用的都是一张图纸，只不过制造商不同，程序当然可以兼容运行了。

### Minix操作系统

刚才提到了UNIX操作系统不开源的问题，那么有没有一开始就开源的UNIX操作系统呢？这里就要提到Linux发展的第三个机遇，Minix操作系统，它在早期是Linux发展的重要指引。这个操作系统是由一个叫做安迪·塔能鲍姆（Andy Tanenbaum）的教授开发的，他的本意是用来做UNIX教学的，甚至有人说，如果Minix操作系统也完全走社区开放的道路，那么未必有现在的Linux操作系统。当然，这些话咱们就权当作是马后炮了。Linux早期从Minix中借鉴了一些思路，包括最早的文件系统等。

### GNU

Linux操作系统得以发展还有一个非常重要的因素，那就是GNU（GNU’s NOT UNIX），它的创始人就是鼎鼎大名的理查·斯托曼（Richard Stallman）。斯托曼的想法是设计一个完全自由的软件系统，用户可以自由使用，自由修改这些软件系统。

GNU为什么对Linux的发展如此重要呢？事实上，GNU之于Linux是要早很久的，GNU在1984年就正式诞生了。最开始，斯托曼是想开发一个类似UNIX的操作系统的。

> From CSvax:pur-ee:inuxc!ixn5c!ihnp4!houxm!mhuxi!eagle!mit-vax!mit-eddie!RMS@ MIT-OZ
>
> From: RMS% MIT-OZ@ mit-eddie
>
> Newsgroups: net.unix-wizards,net.usoft
>
> Subj ect: new UNIX implementation
>
> Date: Tue, 27-Sep-83 12:35:59 EST
>
> Organization: MIT AI Lab, Cambridge, MA
>
> Free Unix!
>
> Starting this Thanksgiving I am going to write a complete Unix-compatible software system called GNU (for Gnu’s Not Unix), and give it away free to everyone who can use it. Contributions of time,money, programs and equipment are greatly needed.
>
> To begin with, GNU will be a kernel plus all the utilities needed to write and run C programs: editor, shell, C compiler, linker, assembler, and a few other things. After this we will add a text formatter, a YACC, an Empire game, a spreadsheet, and hundreds of other things. We hope to supply, eventually, everything useful that normally comes with a Unix system, and anything else useful, including on-line and hardcopy documentation.
>
> …

在这个设想宏大的GNU计划里，包括了操作系统内核、编辑器、shell、编译器、链接器和汇编器等等，每一个都是极其难啃的硬骨头。

不过斯托曼可是个牛人，单枪匹马地开发出世界上最牛的编辑器Emacs，继而组织和成立了自由软件基金会（the Free Software Foundation - FSF）。

GNU在自由软件基金会统一组织下，相继推出了编译器GCC、调试器GDB、Bash Shell等运行于用户空间的程序。正是这些软件为Linux 操作系统的开发创造了一个合适的环境，比如编译器GCC、Bash Shell就是Linux能够诞生的基础之一。

你有没有发现，GNU独缺操作系统核心？

实际上，1990年，自由软件基金会开始正式发展自己的操作系统Hurd，作为GNU项目中的操作系统。不过这个项目再三耽搁，1991年，Linux出现，1993年，FreeBSD发布，这样GNU的开发者开始转向于Linux或FreeBSD，其中，Linux成为更常见的GNU软件运行平台。

斯托曼主张，Linux操作系统使用了许多GNU软件，正式名应为GNU/Linux，但没有得到Linux社群的一致认同，形成著名的GNU/Linux命名争议。

GNU是这么解释为什么应该叫GNU/Linux的：“大多数基于Linux内核发布的操作系统，基本上都是GNU操作系统的修改版。我们从1984 年就开始编写GNU 软件，要比Linus开始编写它的内核早许多年，而且我们开发了系统的大部分软件，要比其它项目多得多，我们应该得到公平对待。”

从这段话里，我们可以知道GNU和GNU/Linux互相造就了对方，没有GNU当然没有Linux，不过没有Linux，GNU也不可能大发光彩。

在开源的世界里，也会发生这种争名夺利的事情，我们也不用觉得惊奇。

## 操作系统对TCP/IP的支持

讲了这么多操作系统的内容，我们再来看下面这张图。图中展示了TCP/IP在各大操作系统的演变历史。可以看到，即使是大名鼎鼎的Linux以及90年代大发光彩的Windows操作系统，在TCP/IP网络这块，也只能算是一个后来者。

![](https://static001.geekbang.org/resource/image/0f/e1/0f783e74927d70794421cf5983f22ae1.png?wh=1450*1354)

## 总结

这是我们专栏的第一讲，我没有直接开始讲网络编程，而是对今天互联网技术的基石，TCP和Linux进行了简单的回顾。通过这样的回顾，熟悉历史，可以指导我们今后学习的方向，在后面的章节中，我们都将围绕Linux下的TCP/IP程序设计展开。

最后你不妨思考一下，Linux TCP/IP网络协议栈最初的实现“借鉴”了多少BSD的实现呢？Linux到底是不是应该被称为GNU/Linux呢？

欢迎你在评论区写下你的思考，我会和你一起讨论这些问题。如果这篇文章帮你厘清了TCP/IP和Linux的发展脉络，欢迎把它分享给你的朋友或者同事。