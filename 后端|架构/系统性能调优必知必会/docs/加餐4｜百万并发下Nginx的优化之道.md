你好，我是专栏编辑冬青。今天的课程有点特别，作为一期加餐，我为你带来了陶辉老师在GOPS 2018 · 上海站的分享，以文字讲解+ PPT的形式向你呈现。今天的内容主要集中在Nginx的性能方面，希望能给你带来一些系统化的思考，帮助你更有效地去做Nginx。

## 优化方法论

今天的分享重点会看这样两个问题：

- 第一，如何有效使用每个连接分配的内存，以此实现高并发。
- 第二，在高并发的同时，怎样提高QPS。

当然，实现这两个目标，既可以从单机中的应用、框架、内核优化入手，也可以使用类似F5这样的硬件设备，或者通过DNS等方案实现分布式集群。

![](https://static001.geekbang.org/resource/image/1a/24/1a69ba079c318c227c9ccff842714424.jpg?wh=1888*1082)

而Nginx最大的限制是网络，所以将网卡升级到万兆，比如10G或者40G吞吐量就会有很大提升。作为静态资源、缓存服务时，磁盘也是重点关注对象，比如固态硬盘的IOPS或者BPS，要比不超过1万转每秒的机械磁盘高出许多。

![](https://static001.geekbang.org/resource/image/4a/2c/4aecd5772e4d164dc414d1f473440f2c.jpg?wh=1874*1076)

这里我们重点看下CPU，如果由操作系统切换进程实现并发，代价太大，毕竟每次都有5微秒左右的切换成本。Nginx将其改到进程内部，由epoll切换ngx\_connection\_t连接的处理，成本会非常低。OpenResty切换Lua协程，也是基于同样的方式。这样，CPU的计算力会更多地用在业务处理上。

从整体上看，只有充分、高效地使用各类IT资源，才能减少RTT时延、提升并发连接。

![](https://static001.geekbang.org/resource/image/9d/24/9d4721babd048bed55968c4f8bbeaf24.jpg?wh=1874*1072)

## 请求的“一生”

只有熟悉Nginx处理HTTP请求的流程，优化时才能做到有的放矢。

首先，我们要搞清楚Nginx的模块架构。Nginx是一个极其开放的生态，它允许第三方编写的C模块与框架协作，共同处理1个HTTP请求。比如，所有的请求处理模块会构成一个链表，以PipeAndFilter这种架构依次处理请求。再比如，生成HTTP响应后，所有过滤模块也会依次加工。

![](https://static001.geekbang.org/resource/image/8b/4d/8bb5620111efd7086b3fa89b1b7a3d4d.jpg?wh=1878*1074)

### 1\. 请求到来

试想一下，当用户请求到来时，服务器到底会做哪些事呢？首先，操作系统内核会将完成三次握手的连接socket，放入1个ACCEPT队列（如果打开了reuseport，内核会选择某个worker进程对应的队列），某个Nginx Worker进程事件模块中的代码，需要调用accept函数取出socket。

建立好连接并分配ngx\_connection\_t对象后，Nginx会为它分配1个内存池，它的默认大小是512字节（可以由connection\_pool\_size指令修改），只有这个连接关闭的时候才会去释放。

接下来Nginx会为这个连接添加一个默认60秒（client\_header\_timeout指令可以配置）的定时器，其中，需要将内核的socket读缓冲区里的TCP报文，拷贝到用户态内存中。所以，此时会将连接内存池扩展到1KB（client\_header\_buffer\_size指令可以配置）来拷贝消息内容，如果在这段时间之内没有接收完请求，则返回失败并关闭连接。

![](https://static001.geekbang.org/resource/image/17/63/171329643c8f003yy47bcd0d1b5f5963.jpg?wh=1884*1080)

### 2\. 处理请求

当接收完HTTP请求行和HEADER后，就清楚了这是一个什么样的请求，此时会再分配另一个默认为4KB（request\_pool\_size指令可以修改，这里请你思考为什么这个请求内存池比连接内存池的初始字节数多了8倍？）的内存池。

Nginx会通过协议状态机解析接收到的字符流，如果1KB内存还没有接收到完整的HTTP头部，就会再从请求内存池上分配出32KB，继续接收字符流。其中，这32KB默认是分成4次分配，每次分配8KB（可以通过large\_client\_header\_buffers指令修改），这样可以避免为少量的请求浪费过大的内存。

![](https://static001.geekbang.org/resource/image/f8/64/f8b2e2c3734188c4f00e8002f0966964.jpg?wh=1872*1066)

接下来，各类HTTP处理模块登场。当然，它们并不是简单构成1个链表，而是通过11个阶段构成了一个二维链表。其中，第1维长度是与Web业务场景相关的11个阶段，第2维的长度与每个阶段中注册的HTTP模块有关。

这11个阶段不用刻意死记，你只要掌握3个关键词，就能够轻松地把他们分解开。首先是5个阶段的预处理，包括post\_read，以及与rewrite重写URL相关的3个阶段，以及URL与location相匹配的find\_config阶段。

![](https://static001.geekbang.org/resource/image/a0/86/a048b12f5f79fee43856ecf449387786.jpg?wh=1886*1072)

其次是访问控制，包括限流限速的preaccess阶段、控制IP访问范围的access阶段和做完访问控制后的post\_access阶段。

最后则是内容处理，比如执行镜象分流的precontent阶段、生成响应的content阶段、记录处理结果的log阶段。

每个阶段中的HTTP模块，会在configure脚本执行时就构成链表，顺序地处理HTTP请求。其中，HTTP框架允许某个模块跳过其后链接的本阶段模块，直接进入下一个阶段的第1个模块。

![](https://static001.geekbang.org/resource/image/0e/fb/0ea57bd24be1fdae15f860b926cc25fb.jpg?wh=1872*1068)

content阶段会生成HTTP响应。当然，其他阶段也有可能生成HTTP响应返回给客户端，它们通常都是非200的错误响应。接下来，会由HTTP过滤模块加工这些响应的内容，并由write\_filter过滤模块最终发送到网络中。

![](https://static001.geekbang.org/resource/image/f4/39/f4fc5bc3ef64498ac6882a902f927539.jpg?wh=1876*1074)

### 3\. 请求的反向代理

Nginx由于性能高，常用来做分布式集群的负载均衡服务。由于Nginx下游通常是公网，网络带宽小、延迟大、抖动大，而上游的企业内网则带宽大、延迟小、非常稳定，因此Nginx需要区别对待这两端的网络，以求尽可能地减轻上游应用的负载。

比如，当你配置proxy\_request\_buffering on指令（默认就是打开的）后，Nginx会先试图将完整的HTTP BODY接收完，当内存不够（默认是16KB，你可以通过client\_body\_buffer\_size指令修改）时还会保存到磁盘中。这样，在公网上漫长的接收BODY流程中，上游应用都不会有任何流量压力。

接收完请求后，会向上游应用建立连接。当然，Nginx也会通过定时器来保护自己，比如建立连接的最长超时时间是60秒（可以通过proxy\_connect\_timeout指令修改）。

当上游生成HTTP响应后，考虑到不同的网络特点，如果你打开了proxy\_buffering on（该功能也是默认打开的）功能，Nginx会优先将内网传来的上游响应接收完毕（包括存储到磁盘上），这样就可以关闭与上游之间的TCP连接，减轻上游应用的并发压力。最后再通过缓慢的公网将响应发送给客户端。当然，针对下游客户端与上游应用，还可以通过proxy\_limit\_rate与limit\_rate指令限制传输速度。如果设置proxy\_buffering off，Nginx会从上游接收到一点响应，就立刻往下游发一些。

![](https://static001.geekbang.org/resource/image/9c/90/9c3d5be8ecc6b287a0cb4fc09ab0c690.jpg?wh=1878*1066)

### 4\. 返回响应

当生成HTTP响应后，会由注册为HTTP响应的模块依次加工响应。同样，这些模块的顺序也是由configure脚本决定的。由于HTTP响应分为HEADER（包括响应行和头部两部分）、BODY，所以每个过滤模块也可以决定是仅处理HEADER，还是同时处理HEADER和BODY。

![](https://static001.geekbang.org/resource/image/25/e8/2506dfed0c4792a7a1be390c1c7979e8.jpg?wh=1868*1070)

因此，OpenResty中会提供有header\_filter\_by\_lua和body\_filter\_by\_lua这两个指令。

![](https://static001.geekbang.org/resource/image/c4/81/c495fb95fed3b010a3fcdd26afd08c81.jpg?wh=1880*1070)

## 应用层优化

### 1\. 协议

应用层协议的优化可以带来非常大的收益。比如HTTP/1 HEADER的编码方式低效，REST架构又放大了这一点，改为HTTP/2协议后就大有改善。Nginx对HTTP/2有良好的支持，包括上游、下游，以及基于HTTP/2的gRPC协议。

![](https://static001.geekbang.org/resource/image/ee/91/eebe2bcd1349d51ee1d3cb60a238a391.jpg?wh=1874*1076)

### 2\. 压缩

对于无损压缩，信息熵越大，压缩效果就越好。对于文本文件的压缩来说，Google的Brotli就比Gzip效果好，你可以通过 [https://github.com/google/ngx\_brotli](https://github.com/google/ngx_brotli) 模块，让Nginx支持Brotli压缩算法。

对于静态图片通常会采用有损压缩，这里不同压缩算法的效果差距更大。目前Webp的压缩效果要比jpeg好不少。对于音频、视频则可以基于关键帧，做动态增量压缩。当然，只要是在Nginx中做实时压缩，就会大幅降低性能。除了每次压缩对CPU的消耗外，也不能使用sendfile零拷贝技术，因为从磁盘中读出资源后，copy\_filter过滤模块必须将其拷贝到内存中做压缩，这增加了上下文切换的次数。更好的做法是提前在磁盘中压缩好，然后通过add\_header等指令在响应头部中告诉客户端该如何解压。

### 3\. 提高内存使用率

只在需要时分配恰当的内存，可以提高内存效率。所以下图中Nginx提供的这些内存相关的指令，需要我们根据业务场景谨慎配置。当然，Nginx的内存池已经将内存碎片、小内存分配次数过多等问题解决了。必要时，通过TcMalloc可以进一步提升Nginx申请系统内存的效率。

同样，提升CPU缓存命中率，也可以提升内存的读取速度。基于cpu cache line来设置哈希表的桶大小，就可以提高多核CPU下的缓存命中率。

![](https://static001.geekbang.org/resource/image/aa/a7/aa7727a2dbf6a3a22c2bf933327308a7.jpg?wh=1872*1072)

### 4\. 限速

作为负载均衡，Nginx可以通过各类模块提供丰富的限速功能。比如limit\_conn可以限制并发连接，而limit\_req可以基于leacky bucket漏斗原理限速。对于向客户端发送HTTP响应，可以通过limit\_rate指令限速，而对于HTTP上游应用，可以使用proxy\_limit\_rate限制发送响应的速度，对于TCP上游应用，则可以分别使用proxy\_upload\_rate和proxy\_download\_rate指令限制上行、下行速度。

![](https://static001.geekbang.org/resource/image/3e/af/3e7dbd21efc06b6721ea7b0c08cd95af.jpg?wh=1878*1072)

### 5\. Worker间负载均衡

当Worker进程通过epoll\_wait的读事件获取新连接时，就由内核挑选1个Worker进程处理新连接。早期Linux内核的挑选算法很糟糕，特别是1个新连接建立完成时，内核会唤醒所有阻塞在epoll\_wait函数上的Worker进程，然而，只有1个Worker进程，可以通过accept函数获取到新连接，其他进程获取失败后重新休眠，这就是曾经广为人知的“惊群”现象。同时，这也很容易造成Worker进程间负载不均衡，由于每个Worker进程绑定1个CPU核心，当部分Worker进程中的并发TCP连接过少时，意味着CPU的计算力被闲置了，所以这也降低了系统的吞吐量。

Nginx早期解决这一问题，是通过应用层accept\_mutex锁完成的，在1.11.3版本前它是默认开启的：accept\_mutex on;

其中负载均衡功能，是在连接数达到worker\_connections的八分之七后，进行次数限制实现的。

我们还可以通过accept\_mutex\_delay配置控制负载均衡的执行频率，它的默认值是500毫秒，也就是最多500毫秒后，并发连接数较少的Worker进程会尝试处理新连接：accept\_mutex\_delay 500ms;

当然，在1.11.3版本后，Nginx默认关闭了accept\_mutex锁，这是因为操作系统提供了reuseport（Linux3.9版本后才提供这一功能）这个更好的解决方案。

![](https://static001.geekbang.org/resource/image/5f/7a/5f5f833b51f322ae963bde06c7f66f7a.jpg?wh=1868*1064)

图中，横轴中的default项开启了accept\_mutex锁。我们可以看到，使用reuseport后，QPS吞吐量有了3倍的提高，同时处理时延有明显的下降，特别是时延的波动（蓝色的标准差线）有大幅度的下降。

### 6\. 超时

Nginx通过红黑树高效地管理着定时器，这里既有面对TCP报文层面的配置指令，比如面对下游的send\_timeout指令，也有面对UDP报文层面的配置指令，比如proxy\_responses，还有面对业务层面的配置指令，比如面对下游HTTP协议的client\_header\_timeout。

![](https://static001.geekbang.org/resource/image/fy/f7/fyyb03d85d4b8312873b476888a1a0f7.jpg?wh=1870*1068)

### 7\. 缓存

只要想提升性能必须要在缓存上下工夫。Nginx对于七层负载均衡，提供各种HTTP缓存，比如http\_proxy模块、uwsgi\_proxy模块、fastcgi\_proxy模块、scgi\_proxy模块等等。由于Nginx中可以通过变量来命名日志文件，因此Nginx很有可能会并行打开上百个文件，此时通过open\_file\_cache，Nginx可以将文件句柄、统计信息等写入缓存中，提升性能。

![](https://static001.geekbang.org/resource/image/45/15/452d0ecf0fcd822c69e1df859fdeb115.jpg?wh=1868*1064)

### 8\. 减少磁盘IO

Nginx虽然读写磁盘远没有数据库等服务要多，但由于它对性能的极致追求，仍然提供了许多优化策略。比如为方便统计和定位错误，每条HTTP请求的执行结果都会写入access.log日志文件。为了减少access.log日志对写磁盘造成的压力，Nginx提供了批量写入、实时压缩后写入等功能，甚至你可以在另一个服务器上搭建rsyslog服务，然后配置Nginx通过UDP协议，将access.log日志文件从网络写入到 rsyslog中，这完全移除了日志磁盘IO。

![](https://static001.geekbang.org/resource/image/d5/da/d55cb817bb727a097ffc4dfe018539da.jpg?wh=1870*1076)

## 系统优化

最后，我们来看看针对操作系统内核的优化。

首先是为由内核实现的OSI网络层（IP协议）、传输层（TCP与UDP协议）修改影响并发性的配置。毕竟操作系统并不知道自己会作为高并发服务，所以很多配置都需要进一步调整。

![](https://static001.geekbang.org/resource/image/d5/15/d58dc3275745603b7525f690479d6615.jpg?wh=1868*1076)

其次，优化CPU缓存的亲和性，对于Numa架构的服务器，如果Nginx只使用一半以下的CPU核心，那么就让Worker进程只绑定一颗CPU上的核心。

![](https://static001.geekbang.org/resource/image/8f/c2/8f073d7222yy8e823ce1a7c16b945fc2.jpg?wh=1870*1064)

再次，调整默认的TCP网络选项，更快速地发现错误、重试、释放资源。

![](https://static001.geekbang.org/resource/image/32/d3/326cf5a1cb8a8522b89eb19e7ca357d3.jpg?wh=1876*1076)

还可以减少TCP报文的往返次数。比如FastOpen技术可以减少三次握手中1个RTT的时延，而增大初始拥塞窗口可以更快地达到带宽峰值。

![](https://static001.geekbang.org/resource/image/6f/09/6f0de237bd54cf2edf8cdcfb606c8c09.jpg?wh=1872*1074)

还可以提高硬件资源的利用效率，比如当你在listen指令后加入defer选项后，就使用了TCP\_DEFER\_ACCEPT功能，这样epoll\_wait并不会返回仅完成三次握手的连接，只有连接上接收到的TCP数据报文后，它才会返回socket，这样Worker进程就将原本2次切换就降为1次了，虽然会牺牲一些即时性，但提高了CPU的效率。

Linux为TCP内存提供了动态调整功能，这样高负载下我们更强调并发性，而低负载下则可以更强调高传输速度。

我们还可以将小报文合并后批量发送，通过减少IP与TCP头部的占比，提高网络效率。在nginx.conf文件中打开tcp\_nopush、tcp\_nodelay功能后，都可以实现这些目的。

![](https://static001.geekbang.org/resource/image/ac/04/ac69ce7af1abbf4df4bc0b42f288d304.jpg?wh=1876*1064)

为了防止处理系统层网络栈的CPU过载，还可以通过多队列网卡，将负载分担到多个CPU中。

![](https://static001.geekbang.org/resource/image/6b/82/6bacf6f3cyy3ffd730c6eb2f664fe682.jpg?wh=1880*1072)

为了提高内存、带宽的利用率，我们必须更精确地计算出BDP，也就是通过带宽与ping时延算出的带宽时延积，决定socket读写缓冲区（影响滑动窗口大小）。

![](https://static001.geekbang.org/resource/image/13/7d/1389fd8fea84cef63e6438de1e18587d.jpg?wh=1876*1076)

Nginx上多使用小于256KB的小内存，而且我们通常会按照CPU核数开启Worker进程，这样一种场景下，TCMalloc的性能要远高于Linux默认的PTMalloc2内存池。

![](https://static001.geekbang.org/resource/image/56/a8/56267e1yye31a7af808c8793c894b0a8.jpg?wh=1870*1074)

作为Web服务器，Nginx必须重写URL以应对网址变化，或者应用的维护，这需要正则表达式的支持。做复杂的URL或者域名匹配时，也会用到正则表达式。优秀的正则表达式库，可以提供更好的执行性能。

![](https://static001.geekbang.org/resource/image/55/f0/556b3359b43f2a641ef2bc4a13a334f0.jpg?wh=1878*1070)

以上就是今天的加餐分享，有任何问题欢迎在留言区中提出。