你好，我是陈皓，网名左耳朵耗子。

这一篇章，是本系列中最长的一篇，其中包括了如下的内容。

- **系统底层相关**。 主要是以Linux系统为主，其中有大量的文章可以让你学习到Linux内核，以及内存、网络、异步I/O模型、Lock-free的无锁编程，还有其它和系统底层相关的东西。注意，系统底层要是深下去是可以完全不见底的。而且内存方面的知识也是比较多的，所以，这里还是主要给出一些非常有价值的基础性的知识和技术。学好这些东西，你会对系统有很深的理解，而且可以把这些知识反哺到架构设计上来。

- **数据库相关**。数据库方面主要是MySQL和各种开源NoSQL的一些相关的有价值的文章和导读，主要是让你对这些数据库的内在有一定的了解，但又不会太深。真正的深入是需要扎入到源代码中的。需要说明的是，这块技术不是我的长项，但又是每个架构师需要知道的，所以，我在这里给的学习资源可能会比较浅，这点还希望你来补充和指正。

- **分布式架构**。这一部分是最长最多的。其中有架构入门、分布式理论中各种非常有价值的经典论文，然后是一些分布式工程设计方面的文章，其中包括设计模式和工程应用，最后还有各大公司的架构供参考。

- **微服务**。有了分布式架构理论和工程的基础，接下来是对微服务的学习。在这部分内容中，我会罗列几个介绍微服务架构非常系统的文章，然后比较一下微服务和SOA的差别，最后则是一些工程实践和最佳实践。

- **容器化和自动化运维**。在容器化和自动化运维中，主要是学习Docker和Kubernetes这两个自动化运维的杀手型技术。而不是Salt、Puppet、Chef和Ansible这样比较传统的工具。原因很简单，因为自动化部署根本不够，还需要对环境和运行时的管理和运维才够，而只有Docker和Kubernetes才是未来。所以，这里重点让你学习这两个技术，其中有很多文章需要一些系统底层的知识。

- **机器学习和人工智能**。机器学习和人工智能，也不是我的长项，我也只是一个入门者。这里，我主要给了一些基础性的知识，其中包括基本原理、图书、课程、文章和相关的算法。你顺着我画的这路走，不能说能成为一个人工智能专家，但成为一个机器学习的高级工程师甚至准专家还是可能的。

- **前端开发**。这里的前端主要是HTML 5的前端了，这一节会带你学习一下前端开发所需要知道的基础知识，尤其是对前端开发语言JavaScript的学习，我花费了相当的篇幅列出了很多很经典的学习资料，必定会让你成为一个JavaScript高手。然后你还需要了解浏览器是怎样工作的，还有相关的网络协议和一些性能优化的技巧。最后则是JavaScript框架的学习，这里我只给了React.js和Vue.js，并通过React.js带出来函数式编程的学习。我虽然不是一个前端程序员，但是，我相信我这个后端程序员给出来的这组前端开发的学习资料和路径会比前端程序员更靠谱一些。

- **信息源**。最后，则是一些信息源，其中包括各大公司的技术Blog，还有相关的论文集散地。


另外，这里需要说明几点。

- 我假设你在前面已经打下了非常扎实的基础，但是要成为一个高手，基础知识只是一个地基，你还需要很多更为具体的技术。对我来说，就是看各种各样的文章、手册、论文、分享…… 其实，学习到一定程度，就是要从书本中走出去，到社区里和大家一起学习，而且还需要自己找食吃了。所以，对于这里面的文章，有很多都是在罗列各种文章和资源，只是为你梳理信息源，而不是喂你吃饭。

- **老实说，我已经为你梳理并过滤掉了很多的信息，这里只留下了30%我觉得最经济也最有价值的信息**。虽然对于不同定位和不同需求的人还可以再对这些信息进行删减，但是觉得我这么一做就会对其它人不公平了。所以，这也是我觉得最小数量集的信息和资源吧。 **你也可以把我这里的东西当成一个索引来对待**。

- 这些内容，不能说是隔离开来的，应该说是相辅相成的。也没什么顺序，可以各取所需。虽然看上去内容很多，但你也别害怕，真的不用害怕，你会越学越快，越实践越有感觉，也越有效率。在一开始可能会很慢，但是坚持住，积累一段时间后就会越来越快的。 而且，我要告诉你，绝大多数人是坚持不下来的。只要你能坚持下来，我保证，你一定会成为各个大公司的抢手货，这点你一定要相信我。 **你不需要特别努力，只需要日进一步，3-5年后，你就会发现，绝大多数人都在你身后很远的地方了。**


今天分享的内容为系统底层知识中的Linux系统、内存和网络等方面的相关知识及推荐的学习资料。

# Linux系统相关

学习Linux操作系统的原理是通向系统工程师的必经之路。我觉得，Unix/Linux操作系统里的东西并不难学。你千万不要一下子扎到源代码里去，那样没用——你还是要在上层先通过读一些不错的文档来学习。下面我罗列了一些很不错的站点，其中有很多内容供你去钻研和探索。

我在这里默认你前面已经读过并读懂了我推荐的那些和Unix/Linux相关的图书了。所以，我相信你对Unix/Linux下的编程已经是有一些基础了，因此，你继续深挖Linux下的这些知识应该也不是很难的事了。

- [Red Hat Enterprise Linux文档](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/?version=7) 。Red Hat Enterprise Linux（RHEL）是老牌Linux厂商Red Hat出品的面向商业的Linux发行版。Red Hat网站上的这个文档中有很多很有价值的内容，值得一看。

- [Linux Insides](https://github.com/0xAX/linux-insides) ，GitHub上的一个开源电子书，其中讲述了Linux内核是怎样启动、初始化以及进行管理的。

- [LWN’s kernel page](http://lwn.net/Kernel/Index/) ，上面有很多非常不错的文章来解释Linux内核的一些东西。

- [Learn Linux Kernel from Android Perspective](http://learnlinuxconcepts.blogspot.com/2014/10/this-blog-is-to-help-those-students-and.html) ，从Android的角度来学习Linux内核，这个站点上的Blog相对于前面的比较简单易读一些。

- [Linux Kernel Doc](https://www.kernel.org/doc/)， Linux的内核文档也可以浏览一下。

- [Kernel Planet](http://planet.kernel.org/) ，Linux内核开发者的Blog，有很多很不错的文章和想法。

- [Linux Performance and Tuning Guidelines](https://lenovopress.com/redp4285.pdf) ，这是IBM出的红皮书，虽然有点老了，但还是非常值得一读的。

- [TLK: The Linux Kernel](http://tldp.org/LDP/tlk/tlk.html) ，这是一本相对比较老的书了，Linux内核版本为2.0.33，但了解一下前人的思路，也是很有帮助的。

- [Linux Performance](http://www.brendangregg.com/linuxperf.html) ，这个网站上提供了和Linux系统性能相关的各种工具和文章收集，非常不错。

- [Optimizing web servers for high throughput and low latency](https://blogs.dropbox.com/tech/2017/09/optimizing-web-servers-for-high-throughput-and-low-latency/) ，这是一篇非常底层的系统调优的文章，来自DropBox，从中你可以学到很多底层的性能调优的经验和知识。


# 内存相关

计算机内存管理是每一个底层程序员需要了解的非常重要的事儿。当然，这里我们重点还是Linux操作系统相关的内存管理上的知识。

首先，LWN.net上有一系列的 “ **What every programmer should know about memory**” 文章你需要读一下。当然，你可以直接访问一个完整的 [PDF文档](http://futuretech.blinkenlights.nl/misc/cpumemory.pdf)。下面是这个系列文章的网页版列表。读完这个列表的内容，你基本上就对内存有了一个比较好的知识体系了。

- [Part 1: Introduction](https://lwn.net/Articles/250967/) ，中译版为 “ [每个程序员都应该了解的内存知识【第一部分】](https://www.oschina.net/translate/what-every-programmer-should-know-about-memory-part1)”
- [Part 2: CPU caches](https://lwn.net/Articles/252125/)
- [Part 3 (Virtual memory)](http://lwn.net/Articles/253361/)
- [Part 4 (NUMA systems)](http://lwn.net/Articles/254445/)
- [Part 5 (What programmers can do - cache optimization)](http://lwn.net/Articles/255364/)
- [Part 6 (What programmers can do - multi-threaded optimizations)](http://lwn.net/Articles/256433/)
- [Part 7 (Memory performance tools)](http://lwn.net/Articles/257209/)
- [Part 8 (Future technologies)](https://lwn.net/Articles/258154/)
- [Part 9 (Appendices and bibliography)](https://lwn.net/Articles/258188/)

然后是几篇和内存相关的论文。下面这三篇论文是我个人觉得能对你非常有帮助的文章，尤其是你要做一些程序的性能优化方面。

- [Memory Barriers: a Hardware View for Software Hackers](http://irl.cs.ucla.edu/~yingdi/web/paperreading/whymb.2010.06.07c.pdf)。内存的读写屏障是线程并发访问共享的内存数据时，从程序本身、编译器到CPU都必须遵循的一个规范。有了这个规范，才能保证访问共享的内存数据时，一个线程对该数据的更新能被另一个线程以正确的顺序感知到。在SMP（对称多处理）这种类型的多处理器系统（包括多核系统）上，这种读写屏障还包含了复杂的缓存一致性策略。这篇文章做了详细解释。

- [A Tutorial Introduction to the ARM and POWER Relaxed Memory Models](http://www.cl.cam.ac.uk/~pes20/ppc-supplemental/test7.pdf)，对ARM和POWER的宽松内存模型的一个教程式的简介。本篇文章的焦点是ARM和POWER体系结构下多处理器系统内存并发访问一致性的设计思路和使用方法。与支持较强的TSO模型的x86体系结构不同，ARM和POWER这两种体系结构出于对功耗和性能的考虑，使用了一种更为宽松的内存模型。本文详细讨论了ARM和POWER的模型。

- [x86-TSO: A Rigorous and Usable Programmer’s Model for x86 Multiprocessors](http://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf)，介绍x86的多处理器内存并发访问的一致性模型TSO。


接下来是开发者最关心的内存管理方面的lib库。通常来说，我们有三种内存分配管理模块。就目前而言，BSD的jemalloc有很大的影响力。后面我们可以看到不同公司的实践性文章。

- [ptmalloc](http://www.malloc.de/en/) 是glibc的内存分配管理。

- [tcmalloc](https://github.com/gperftools/gperftools) 是Google的内存分配管理模块，全称是Thread-Caching malloc，基本上来说比glibc的ptmalloc快两倍以上。

- [jemalloc](http://jemalloc.net/) 是BSD提供的内存分配管理。其论文为 [A Scalable Concurrent malloc(3) Implementation for FreeBSD](https://people.freebsd.org/~jasone/jemalloc/bsdcan2006/jemalloc.pdf)，这是一个可以并行处理的内存分配管理器。


关于 C 的这些内存分配器，你可以参看Wikipedia的 “ [C Dynamic Memory Allocation](https://en.wikipedia.org/wiki/C_dynamic_memory_allocation#Thread-caching_malloc_(tcmalloc))”这个词条。

下面是几篇不错的文章，让你感觉一下上面那三种内存分配器的一些比较和工程实践。

- [ptmalloc，tcmalloc和jemalloc内存分配策略研究](https://owent.net/2013/867.html)
- [内存优化总结：ptmalloc、tcmalloc和jemalloc](http://www.cnhalo.net/2016/06/13/memory-optimize/)
- [Scalable memory allocation using jemalloc](https://www.facebook.com/notes/facebook-engineering/scalable-memory-allocation-using-jemalloc/480222803919)
- [Decreasing RAM Usage by 40% Using jemalloc with Python & Celery](https://zapier.com/engineering/celery-python-jemalloc/)

# 计算机网络

## 网络学习

首先，推荐一本书——《 [计算机网络（第五版）](https://book.douban.com/subject/10510747/)》，这本“计算机网络”和前面推荐的那本计算机网络不一样，前面那本偏扫盲，这本中有很多细节。这本书是国内外使用最广泛、最权威的计算机网络经典教材。全书按照网络协议模型自下而上（物理层、数据链路层、介质访问控制层、网络层、传输层和应用层）有系统地介绍了计算机网络的基本原理，并结合Internet给出了大量的协议实例。

这本书还与时俱进地引入了最新的网络技术，包括无线网络、3G蜂窝网络、RFID与传感器网络、内容分发与P2P网络、流媒体传输与IP语音，以及延迟容忍网络等。另外，本书针对当前网络应用中日益突出的安全问题，用了一整章的篇幅对计算机网络的安全性进行了深入讨论，而且把相关内容与最新网络技术结合起来阐述。这本书读起来并不枯燥，因为其中有很多小故事和小段子。

然后，有两个网上的教程和讲义也可以让人入门。

- 渥汰华大学的一个课程讲义你也可以一看 [Computer Network Design](http://www.site.uottawa.ca/~shervin/courses/ceg4185/lectures/) 。
- GeeksforGeeks 上也有一个简单的 [Computer Network Tutorials](https://www.geeksforgeeks.org/computer-network-tutorials/) 。

## 网络调优

接下来，你可能需要一些非常实用的可以操作的技术，下面的几篇文章相信可以帮助到你。

- 《Linux的高级路由和流量控制 HowTo》（ [Linux Advanced Routing & Traffic Control HOWTO](http://lartc.org/) ），这是一个非常容易上手的关于 iproute2、流量整形和一点 netfilter 的指南。

- 关于网络调优，你可以看一下这个文档 [Red Hat Enterprise Linux Network Performance Tuning Guide](https://access.redhat.com/sites/default/files/attachments/20150325_network_performance_tuning.pdf)。

- 还有一些网络工具能够帮上你的大忙，这里有一个网络工具的Awesome列表 [Awesome Pcap Tools](https://github.com/caesar0301/awesome-pcaptools) ，其中罗列了各种网络工具，能够让你更从容地调试网络相关的程序。

- [Making Linux TCP Fast](https://netdevconf.org/1.2/papers/bbr-netdev-1.2.new.new.pdf) ，一篇非常不错的TCP调优的论文。

- 下面是在PackageCloud上的两篇关于Linux网络栈相关的底层文章，非常值得一读。
  - [Monitoring and Tuning the Linux Networking Stack: Receiving Data](https://blog.packagecloud.io/eng/2016/06/22/monitoring-tuning-linux-networking-stack-receiving-data/)

  - [Monitoring and Tuning the Linux Networking Stack: Sending Data](https://blog.packagecloud.io/eng/2017/02/06/monitoring-tuning-linux-networking-stack-sending-data/)

## 网络协议

接下来，想要学习网络协议最好的方式就是学习通讯相关的RFC。所以，在这里我会推荐一系列值得读的RFC给你。读RFC有几个好处，一方面可以学习技术，另一方面，你可以通过RFC学习到一个好的技术文档是怎么写的，还能看到各种解决问题的方案和思路。

对于第2层链路层，你可能需要了解一下ARP：

- [RFC 826 - An Ethernet Address Resolution Protocol](https://tools.ietf.org/html/rfc826)

以及Tunnel相关的协议：

- [RFC 1853 - IP in IP Tunneling](https://tools.ietf.org/html/rfc1853)
- [RFC 2784 - Generic Routing Encapsulation (GRE)](https://tools.ietf.org/html/rfc2784)
- [RFC 2661 - Layer Two Tunneling Protocol “L2TP”](https://tools.ietf.org/html/rfc2661)
- [RFC 2637 - Point-to-Point Tunneling Protocol (PPTP)](https://tools.ietf.org/html/rfc2637)

对于第4层，你最需要了解的是TCP/IP了。和TCP相关的RFC相当多，这里给一系列经典的RFC。这些RFC我都引用在了我在CoolShell上的《 [TCP的那些事儿（上）](https://coolshell.cn/articles/11564.html)》和《 [TCP的那些事儿（下）](https://coolshell.cn/articles/11609.html)》两篇文章中。如果你看不懂RFC，你也可以去看我上述的文章。

- [RFC 793 - Transmission Control Protocol](https://tools.ietf.org/html/rfc793) \- 最初的TCP标准定义，但不包括TCP相关细节。

- [RFC 813 - Window and Acknowledgement Strategy in TCP](https://tools.ietf.org/html/rfc813) \- TCP窗口与确认策略，并讨论了在使用该机制时可能遇到的问题及解决方法。

- [RFC 879 - The TCP Maximum Segment Size and Related Topics](https://tools.ietf.org/html/rfc879) \- 讨论MSS参数对控制TCP分组大小的重要性，以及该参数与IP分段大小的关系等。

- [RFC 896 - Congestion Control in IP/TCP Internetworks](https://tools.ietf.org/html/rfc896) \- 讨论拥塞问题和TCP如何控制拥塞。

- [RFC 2581 - TCP Congestion Control](https://tools.ietf.org/html/rfc2581) \- 描述用于拥塞控制的四种机制：慢启动、拥塞防御、快重传和快恢复。后面这个RFC被 [RFC 5681](https://tools.ietf.org/html/rfc5681) 所更新。还有 [RFC 6582 - The NewReno Modification to TCP’s Fast Recovery Algorithm](https://tools.ietf.org/html/rfc6582) 中一个改进的快速恢复算法。

- [RFC 2018 - TCP Selective Acknowledgment Options](https://tools.ietf.org/html/rfc2018) \- TCP的选择确认。

- [RFC 2883 - An Extension to the Selective Acknowledgement (SACK) Option for TCP](https://tools.ietf.org/html/rfc2883) \- 对于RFC 2018的改进。

- [RFC 2988 - Computing TCP’s Retransmission Timer](https://tools.ietf.org/html/rfc2988) \- 讨论与TCP重传计时器设置相关的话题，重传计时器控制报文在重传前应等待多长时间。也就是经典的TCP Karn/Partridge重传算法。

- [RFC 6298 - Computing TCP’s Retransmission Timer](https://tools.ietf.org/html/rfc6298) \- TCP Jacobson/Karels Algorithm重传算法。


我个人觉得TCP最牛的不是不丢包，而是拥塞控制。对此，如果你感兴趣，可以读一下经典论文《 [Congestion Avoidance and Control](http://ee.lbl.gov/papers/congavoid.pdf)》。

关于Linux下的TCP参数，你需要仔仔细细地读一下 [TCP的man page](http://man7.org/linux/man-pages/man7/tcp.7.html) 。

对于第7层协议，HTTP协议是重点要学习的。

首先推荐的是《 [HTTP权威指南](https://book.douban.com/subject/10746113/) 》，这本书有点厚，可以当参考书来看。这本书中没有提到HTTP/2的事，但是可以让你了解到HTTP协议的绝大多数特性。

HTTP 1.1的原始RFC是1999年6月的 [RFC 2616](https://tools.ietf.org/html/rfc2616)，但其在2014后很快被下面这些RFC给取代了。

- [RFC 7230 - Hypertext Transfer Protocol (HTTP/1.1): Message Syntax and Routing](https://tools.ietf.org/html/rfc7230)

- [RFC 7231 - Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content](https://tools.ietf.org/html/rfc7231)

- [RFC 7232 - Hypertext Transfer Protocol (HTTP/1.1): Conditional Requests](https://tools.ietf.org/html/rfc7232)

- [RFC 7233 - Hypertext Transfer Protocol (HTTP/1.1): Range Requests](https://tools.ietf.org/html/rfc7233)

- [RFC 7234 - Hypertext Transfer Protocol (HTTP/1.1): Caching](https://tools.ietf.org/html/rfc7234)

- [RFC 7235 - Hypertext Transfer Protocol (HTTP/1.1): Authentication](https://tools.ietf.org/html/rfc7235)


关于 [HTTP/2](https://en.wikipedia.org/wiki/HTTP/2)，这是HTTP的一个比较新的协议，它于2015年被批准通过，现在基本上所有的主流浏览器都默认启用这个协议。所以，你有必要学习一下这个协议。下面是相关的学习资源。

- [Gitbook - HTTP/2详解](https://legacy.gitbook.com/book/ye11ow/http2-explained/details)

- [http2 explained](http://daniel.haxx.se/http2/)（ [中译版](https://www.gitbook.com/book/ye11ow/http2-explained/details)）

- [HTTP/2 for a Faster Web](https://cascadingmedia.com/insites/2015/03/http-2.html)

- [Nginx HTTP/2 白皮书](https://www.nginx.com/wp-content/uploads/2015/09/NGINX_HTTP2_White_Paper_v4.pdf)

- HTTP/2 的两个RFC：
  - [RFC 7540 - Hypertext Transfer Protocol Version 2 (HTTP/2)](https://httpwg.org/specs/rfc7540.html) ，HTTP/2的协议本身
  - [RFC 7541 - HPACK: Header Compression for HTTP/2](https://httpwg.org/specs/rfc7541.html) ，HTTP/2的压缩算法

最后，你可以上Wikipedia的 [Internet Protocol Suite](https://en.wikipedia.org/wiki/Internet_protocol_suite) 上看看，这是一个很不错的网络协议的词条汇集地。顺着这些协议，你可以找到很多有用的东西。

# 小结

好了，总结一下今天的内容。这是程序员练级攻略2018版第五篇章——高手成长篇的第一篇文章。前面的内容先介绍了一些这一系列内容的总体构成，及每一部分的学习重点。后面是这一篇章第一个主题系统底层知识中的部分内容，即Linux系统、内存和计算机网络，并给出了相应的学习资料。

我认为，学习到一定程度，就是要从书本中走出去，到社区里和大家一起学习，而且还需要自己找食吃了。所以，这篇文章中，我罗列了各种文章和资源，并给出了简短的推荐语言，就是在为你梳理信息源，而不是喂你吃饭。我更希望看到你自趋势地成长。

下篇文章中，我们分享的内容为系统底层知识中的异步I/O模型、Lock-Free编程以及其他一些相关的知识点和学习资源。敬请期待。

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