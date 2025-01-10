你好，我是陶辉，又见面了。结课并不意味着结束，有好的内容我依然会分享给你。今天这节加餐，整理自今年8月3号我在 [Nginx中文社区](https://www.nginx-cn.net/explore) 与QCon共同组织的 [QCon公开课](https://www.infoq.cn/video/VPK3Zu0xrv6U8727ZSXB?utm_source=in_album&utm_medium=video) 中分享的部分内容，主要介绍HTTP/3协议规范、应用场景及实现原理。欢迎一起交流探讨！

自2017年起，HTTP/3协议已发布了29个Draft，推出在即，Chrome、Nginx等软件都在跟进实现最新的草案。那它带来了哪些变革呢？我们结合HTTP/2协议看一下。

2015年，HTTP/2协议正式推出后，已经有接近一半的互联网站点在使用它：

[![](https://static001.geekbang.org/resource/image/0c/01/0c0277835b0yy731b11d68d44de00601.jpg?wh=1188*796)](https://w3techs.com/technologies/details/ce-http2)

HTTP/2协议虽然大幅提升了HTTP/1.1的性能，然而，基于TCP实现的HTTP/2遗留下3个问题：

- 有序字节流引出的 **队头阻塞（** [**Head-of-line blocking**](https://en.wikipedia.org/wiki/Head-of-line_blocking) **）**，使得HTTP/2的多路复用能力大打折扣；
- **TCP与TLS叠加了握手时延**，建链时长还有1倍的下降空间；
- 基于TCP四元组确定一个连接，这种诞生于有线网络的设计，并不适合移动状态下的无线网络，这意味着 **IP地址的频繁变动会导致TCP连接、TLS会话反复握手**，成本高昂。

而HTTP/3协议恰恰是解决了这些问题：

- HTTP/3基于UDP协议重新定义了连接，在QUIC层实现了无序、并发字节流的传输，解决了队头阻塞问题（包括基于QPACK解决了动态表的队头阻塞）；
- HTTP/3重新定义了TLS协议加密QUIC头部的方式，既提高了网络攻击成本，又降低了建立连接的速度（仅需1个RTT就可以同时完成建链与密钥协商）；
- HTTP/3 将Packet、QUIC Frame、HTTP/3 Frame分离，实现了连接迁移功能，降低了5G环境下高速移动设备的连接维护成本。

接下来我们就会从HTTP/3协议的概念讲起，从连接迁移的实现上学习HTTP/3的报文格式，再围绕着队头阻塞问题来分析多路复用与QPACK动态表的实现。虽然正式的RFC规范还未推出，但最近的草案Change只有微小的变化，所以现在学习HTTP/3正当其时，这将是下一代互联网最重要的基础设施。

## HTTP/3协议到底是什么？

就像HTTP/2协议一样，HTTP/3并没有改变HTTP/1的语义。那什么是HTTP语义呢？在我看来，它包括以下3个点：

- 请求只能由客户端发起，而服务器针对每个请求返回一个响应；
- 请求与响应都由Header、Body（可选）组成，其中请求必须含有URL和方法，而响应必须含有响应码；
- Header中各Name对应的含义保持不变。

HTTP/3在保持HTTP/1语义不变的情况下，更改了编码格式，这由2个原因所致：

首先，是为了减少编码长度。下图中HTTP/1协议的编码使用了ASCII码，用空格、冒号以及 \\r\\n作为分隔符，编码效率很低。

![](https://static001.geekbang.org/resource/image/f8/91/f8c65f3f1c405f2c87db1db1c421f891.jpg?wh=4997*2552)

HTTP/2与HTTP/3采用二进制、静态表、动态表与Huffman算法对HTTP Header编码，不只提供了高压缩率，还加快了发送端编码、接收端解码的速度。

其次，由于HTTP/1协议不支持多路复用，这样高并发只能通过多开一些TCP连接实现。然而，通过TCP实现高并发有3个弊端：

- 实现成本高。TCP是由操作系统内核实现的，如果通过多线程实现并发，并发线程数不能太多，否则线程间切换成本会以指数级上升；如果通过异步、非阻塞socket实现并发，开发效率又太低；
- 每个TCP连接与TLS会话都叠加了2-3个RTT的建链成本；
- TCP连接有一个防止出现拥塞的慢启动流程，它会对每个TCP连接都产生减速效果。

因此，HTTP/2与HTTP/3都在应用层实现了多路复用功能：

[![](https://static001.geekbang.org/resource/image/90/e0/90f7cc7fed1a46b691303559cde3bce0.jpg?wh=1792*834)](https://blog.cloudflare.com/http3-the-past-present-and-future/)

HTTP/2协议基于TCP有序字节流实现，因此 **应用层的多路复用并不能做到无序地并发，在丢包场景下会出现队头阻塞问题**。如下面的动态图片所示，服务器返回的绿色响应由5个TCP报文组成，而黄色响应由4个TCP报文组成，当第2个黄色报文丢失后，即使客户端接收到完整的5个绿色报文，但TCP层不允许应用进程的read函数读取到最后5个报文，并发也成了一纸空谈。

![](https://static001.geekbang.org/resource/image/12/46/12473f12db5359904526d1878bc3c046.gif?wh=720*520)

当网络繁忙时，丢包概率会很高，多路复用受到了很大限制。因此， **HTTP/3采用UDP作为传输层协议，重新实现了无序连接，并在此基础上通过有序的QUIC Stream提供了多路复用**，如下图所示：

[![](https://static001.geekbang.org/resource/image/35/d6/35c3183d5a210bc4865869d9581c93d6.png?wh=554*254)](https://blog.cloudflare.com/http3-the-past-present-and-future/)

最早这一实验性协议由Google推出，并命名为gQUIC，因此，IETF草案中仍然保留了QUIC概念，用来描述HTTP/3协议的传输层和表示层。HTTP/3协议规范由以下5个部分组成：

- QUIC层由 [https://tools.ietf.org/html/draft-ietf-quic-transport-29](https://tools.ietf.org/html/draft-ietf-quic-transport-29) 描述，它定义了连接、报文的可靠传输、有序字节流的实现；
- TLS协议会将QUIC层的部分报文头部暴露在明文中，方便代理服务器进行路由。 [https://tools.ietf.org/html/draft-ietf-quic-tls-29](https://tools.ietf.org/html/draft-ietf-quic-tls-29) 规范定义了QUIC与TLS的结合方式；
- 丢包检测、RTO重传定时器预估等功能由 [https://tools.ietf.org/html/draft-ietf-quic-recovery-29](https://tools.ietf.org/html/draft-ietf-quic-recovery-29) 定义，目前拥塞控制使用了类似 [TCP New RENO](https://tools.ietf.org/html/rfc6582) 的算法，未来有可能更换为基于带宽检测的算法（例如 [BBR](https://github.com/google/bbr)）；
- 基于以上3个规范， [https://tools.ietf.org/html/draft-ietf-quic-http-29](https://tools.ietf.org/html/draft-ietf-quic-http-29H) 定义了HTTP语义的实现，包括服务器推送、请求响应的传输等；
- 在HTTP/2中，由HPACK规范定义HTTP头部的压缩算法。由于HPACK动态表的更新具有时序性，无法满足HTTP/3的要求。在HTTP/3中，QPACK定义HTTP头部的编码： [https://tools.ietf.org/html/draft-ietf-quic-qpack-16](https://tools.ietf.org/html/draft-ietf-quic-qpack-16)。注意，以上规范的最新草案都到了29，而QPACK相对简单，它目前更新到16。

自1991年诞生的HTTP/0.9协议已不再使用，但1996推出的HTTP/1.0、1999年推出的HTTP/1.1、2015年推出的HTTP/2协议仍然共存于互联网中（HTTP/1.0在企业内网中还在广为使用，例如Nginx与上游的默认协议还是1.0版本），即将面世的HTTP/3协议的加入，将会进一步增加协议适配的复杂度。接下来，我们将深入HTTP/3协议的细节。

## 连接迁移功能是怎样实现的？

对于当下的HTTP/1和HTTP/2协议，传输请求前需要先完成耗时1个RTT的TCP三次握手、耗时1个RTT的TLS握手（TLS1.3）， **由于它们分属内核实现的传输层、openssl库实现的表示层，所以难以合并在一起**，如下图所示：

[![](https://static001.geekbang.org/resource/image/79/a2/79a1d38d2e39c93e600f38ae3a9a04a2.jpg?wh=1760*1234)](https://blog.cloudflare.com/http3-the-past-present-and-future/)

在IoT时代，移动设备接入的网络会频繁变动，从而导致设备IP地址改变。 **对于通过四元组（源IP、源端口、目的IP、目的端口）定位连接的TCP协议来说，这意味着连接需要断开重连，所以上述2个RTT的建链时延、TCP慢启动都需要重新来过。** 而HTTP/3的QUIC层实现了连接迁移功能，允许移动设备更换IP地址后，只要仍保有上下文信息（比如连接ID、TLS密钥等），就可以复用原连接。

在UDP报文头部与HTTP消息之间，共有3层头部，定义连接且实现了Connection Migration主要是在Packet Header中完成的，如下图所示：

![](https://static001.geekbang.org/resource/image/ab/7c/ab3283383013b707d1420b6b4cb8517c.png?wh=554*371)

这3层Header实现的功能各不相同：

- Packet Header实现了可靠的连接。当UDP报文丢失后，通过Packet Header中的Packet Number实现报文重传。连接也是通过其中的Connection ID字段定义的；
- QUIC Frame Header在无序的Packet报文中，基于QUIC Stream概念实现了有序的字节流，这允许HTTP消息可以像在TCP连接上一样传输；
- HTTP/3 Frame Header定义了HTTP Header、Body的格式，以及服务器推送、QPACK编解码流等功能。

为了进一步提升网络传输效率，Packet Header又可以细分为两种：

- Long Packet Header用于首次建立连接；
- Short Packet Header用于日常传输数据。

其中，Long Packet Header的格式如下图所示：

![](https://static001.geekbang.org/resource/image/5e/b4/5ecc19ba9106179cd3443eefc1d6b8b4.png?wh=554*248)

建立连接时，连接是由服务器通过Source Connection ID字段分配的，这样，后续传输时，双方只需要固定住Destination Connection ID，就可以在客户端IP地址、端口变化后，绕过UDP四元组（与TCP四元组相同），实现连接迁移功能。下图是Short Packet Header头部的格式，这里就不再需要传输Source Connection ID字段了：

![](https://static001.geekbang.org/resource/image/f4/26/f41634797dfafeyy4535c3e94ea5f226.png?wh=554*179)

上图中的Packet Number是每个报文独一无二的序号，基于它可以实现丢失报文的精准重发。如果你通过抓包观察Packet Header，会发现Packet Number被TLS层加密保护了，这是为了防范各类网络攻击的一种设计。下图给出了Packet Header中被加密保护的字段：

![](https://static001.geekbang.org/resource/image/5a/93/5a77916ce399148d0c2d951df7c26c93.png?wh=554*385)

其中，显示为E（Encrypt）的字段表示被TLS加密过。当然，Packet Header只是描述了最基本的连接信息，其上的Stream层、HTTP消息也是被加密保护的：

![](https://static001.geekbang.org/resource/image/9e/af/9edabebb331bb46c6e2335eda20c68af.png?wh=554*306)

现在我们已经对HTTP/3协议的格式有了基本的了解，接下来我们通过队头阻塞问题，看看Packet之上的QUIC Frame、HTTP/3 Frame帧格式。

## Stream多路复用时的队头阻塞是怎样解决的？

其实，解决队头阻塞的方案，就是允许微观上有序发出的Packet报文，在接收端无序到达后也可以应用于并发请求中。比如上文的动态图中，如果丢失的黄色报文对其后发出的绿色报文不造成影响，队头阻塞问题自然就得到了解决：

![](https://static001.geekbang.org/resource/image/f6/f4/f6dc5b11f8a240b4283dcb8de5b9a0f4.gif?wh=720*520)

在Packet Header之上的QUIC Frame Header，定义了有序字节流Stream，而且Stream之间可以实现真正的并发。HTTP/3的Stream，借鉴了HTTP/2中的部分概念，所以在讨论QUIC Frame Header格式之前，我们先来看看HTTP/2中的Stream长什么样子：

[![](https://static001.geekbang.org/resource/image/ff/4e/ff629c78ac1880939e5eabb85ab53f4e.png?wh=554*449)](https://developers.google.com/web/fundamentals/performance/http2)

每个Stream就像HTTP/1中的TCP连接，它保证了承载的HEADERS frame（存放HTTP Header）、DATA frame（存放HTTP Body）是有序到达的，多个Stream之间可以并行传输。在HTTP/3中，上图中的HTTP/2 frame会被拆解为两层，我们先来看底层的QUIC Frame。

一个Packet报文中可以存放多个QUIC Frame，当然所有Frame的长度之和不能大于PMTUD（Path Maximum Transmission Unit Discovery，这是大于1200字节的值），你可以把它与IP路由中的MTU概念对照理解：

![](https://static001.geekbang.org/resource/image/3d/47/3df65a7bb095777f1f8a7fede1a06147.png?wh=554*183)

每一个Frame都有明确的类型：

![](https://static001.geekbang.org/resource/image/0e/5d/0e27cd850c0f5b854fd3385cab05755d.png?wh=554*120)

前4个字节的Frame Type字段描述的类型不同，接下来的编码也不相同，下表是各类Frame的16进制Type值：

![](https://static001.geekbang.org/resource/image/45/85/45b0dfcd5c59a9c8be1c5c9e6f998085.jpg?wh=1236*900)

在上表中，我们只要分析0x08-0x0f这8种STREAM类型的Frame，就能弄明白Stream流的实现原理，自然也就清楚队头阻塞是怎样解决的了。Stream Frame用于传递HTTP消息，它的格式如下所示：

![](https://static001.geekbang.org/resource/image/10/4c/10874d334349349559835yy4d4c92b4c.png?wh=554*180)

可见，Stream Frame头部的3个字段，完成了多路复用、有序字节流以及报文段层面的二进制分隔功能，包括：

- Stream ID定义了一个有序字节流。当HTTP Body非常大，需要跨越多个Packet时，只要在每个Stream Frame中含有同样的Stream ID，就可以传输任意长度的消息。多个并发传输的HTTP消息，通过不同的Stream ID加以区别；
- 消息序列化后的“有序”特性，是通过Offset字段完成的，它类似于TCP协议中的Sequence序号，用于实现Stream内多个Frame间的累计确认功能；
- Length指明了Frame数据的长度。

你可能会奇怪，为什么会有8种Stream Frame呢？这是因为0x08-0x0f这8种类型其实是由3个二进制位组成，它们实现了以下3标志位的组合：

- 第1位表示是否含有Offset，当它为0时，表示这是Stream中的起始Frame，这也是上图中Offset是可选字段的原因；
- 第2位表示是否含有Length字段；
- 第3位Fin，表示这是Stream中最后1个Frame，与HTTP/2协议Frame帧中的FIN标志位相同。

Stream数据中并不会直接存放HTTP消息，因为HTTP/3还需要实现服务器推送、权重优先级设定、流量控制等功能，所以Stream Data中首先存放了HTTP/3 Frame：

![](https://static001.geekbang.org/resource/image/12/61/12b117914de00014f90d1yyf12875861.png?wh=554*150)

其中，Length指明了HTTP消息的长度，而Type字段（请注意，低2位有特殊用途，在QPACK一节中会详细介绍）包含了以下类型：

- 0x00：DATA帧，用于传输HTTP Body包体；
- 0x01：HEADERS帧，通过QPACK 编码，传输HTTP Header头部；
- 0x03：CANCEL\_PUSH控制帧，用于取消1次服务器推送消息，通常客户端在收到PUSH\_PROMISE帧后，通过它告知服务器不需要这次推送；
- 0x04：SETTINGS控制帧，设置各类通讯参数；
- 0x05：PUSH\_PROMISE帧，用于服务器推送HTTP Body前，先将HTTP Header头部发给客户端，流程与HTTP/2相似；
- 0x07：GOAWAY控制帧，用于关闭连接（注意，不是关闭Stream）；
- 0x0d：MAX\_PUSH\_ID，客户端用来限制服务器推送消息数量的控制帧。

总结一下，QUIC Stream Frame定义了有序字节流，且多个Stream间的传输没有时序性要求。这样，HTTP消息基于QUIC Stream就实现了真正的多路复用，队头阻塞问题自然就被解决掉了。

## QPACK编码是如何解决队头阻塞问题的？

最后，我们再看下HTTP Header头部的编码方式，它需要面对另一种队头阻塞问题。

与HTTP/2中的HPACK编码方式相似，HTTP/3中的QPACK也采用了静态表、动态表及Huffman编码：

[![](https://static001.geekbang.org/resource/image/af/94/af869abf09yy1d6d3b0fa5879e300194.jpg?wh=1568*532)](https://www.oreilly.com/content/http2-a-new-excerpt/)

先来看静态表的变化。在上图中，GET方法映射为数字2，这是通过客户端、服务器协议实现层的硬编码完成的。在HTTP/2中，共有61个静态表项：

![](https://static001.geekbang.org/resource/image/8c/21/8cd69a7baf5a02d84e69fe6946d5ab21.jpg?wh=1176*882)

而在QPACK中，则上升为98个静态表项，比如Nginx上的ngx\_http\_v3\_static\_table数组所示：

![](https://static001.geekbang.org/resource/image/0c/10/0c9c5ab8c342eb6545b00cee8f6b4010.png?wh=554*500)

你也可以从 [这里](https://tools.ietf.org/html/draft-ietf-quic-qpack-14#appendix-A) 找到完整的HTTP/3静态表。对于Huffman以及整数的编码，QPACK与HPACK并无多大不同，但动态表编解码方式差距很大。

所谓动态表，就是将未包含在静态表中的Header项，在其首次出现时加入动态表，这样后续传输时仅用1个数字表示，大大提升了编码效率。因此，动态表是天然具备时序性的，如果首次出现的请求出现了丢包，后续请求解码HPACK头部时，一定会被阻塞！

QPACK是如何解决队头阻塞问题的呢？事实上，QPACK将动态表的编码、解码独立在单向Stream中传输，仅当单向Stream中的动态表编码成功后，接收端才能解码双向Stream上HTTP消息里的动态表索引。

这里我们又引入了单向Stream和双向Stream概念，不要头疼，它其实很简单。单向指只有一端可以发送消息，双向则指两端都可以发送消息。还记得上一小节的QUIC Stream Frame头部吗？其中的Stream ID别有玄机，除了标识Stream外，它的低2位还可以表达以下组合：

![](https://static001.geekbang.org/resource/image/ae/0a/ae1dbf30467e8a7684d337701f055c0a.png?wh=429*202)

因此，当Stream ID是0、4、8、12时，这就是客户端发起的双向Stream（HTTP/3不支持服务器发起双向Stream），它用于传输HTTP请求与响应。单向Stream有很多用途，所以它在数据前又多出一个Stream Type字段：

![](https://static001.geekbang.org/resource/image/b0/52/b07521a11e65a24cd4b93553127bfc52.png?wh=554*84)

Stream Type有以下取值：

- 0x00：控制Stream，传递各类Stream控制消息；
- 0x01：服务器推送消息；
- 0x02：用于编码QPACK动态表，比如面对不属于静态表的HTTP请求头部，客户端可以通过这个Stream发送动态表编码；
- 0x03：用于通知编码端QPACK动态表的更新结果。

由于HTTP/3的Stream之间是乱序传输的，因此，若先发送的编码Stream后到达，双向Stream中的QPACK头部就无法解码，此时传输HTTP消息的双向Stream就会进入Block阻塞状态（两端可以通过控制帧定义阻塞Stream的处理方式）。

## 小结

最后对这一讲的内容做个小结。

基于四元组定义连接并不适用于下一代IoT网络，HTTP/3创造出Connection ID概念实现了连接迁移，通过融合传输层、表示层，既缩短了握手时长，也加密了传输层中的绝大部分字段，提升了网络安全性。

HTTP/3在Packet层保障了连接的可靠性，在QUIC Frame层实现了有序字节流，在HTTP/3 Frame层实现了HTTP语义，这彻底解开了队头阻塞问题，真正实现了应用层的多路复用。

QPACK使用独立的单向Stream分别传输动态表编码、解码信息，这样乱序、并发传输HTTP消息的Stream既不会出现队头阻塞，也能基于时序性大幅压缩HTTP Header的体积。

如果你觉得这一讲对你理解HTTP/3协议有所帮助，也欢迎把它分享给你的朋友。