你好，我是胜辉。

在过去几节课里，我们集中学习了TCP传输相关的知识，无论是 [第8讲](https://time.geekbang.org/column/article/484667) 的MTU、 [第9讲](https://time.geekbang.org/column/article/484923) 和 [第10讲](https://time.geekbang.org/column/article/485689) 的传输速度、 [第11讲](https://time.geekbang.org/column/article/486281) 的拥塞控制，还是第12和13讲的各种重传，我们可以说是把TCP传输相关的核心概念全部过了一遍。一方面学习了RFC规范和具体的Linux实现，一方面也通过案例，把这些知识灵活运用了起来。想必现在的你，再去处理TCP传输问题的时候，已经强大很多了。

不过，上面的种种，其实还是在协议规范这个大框架内的讨论和学习，默认前提就是通信两端是遵照了TCP规定而展开工作的，都可谓是谦谦君子，道德楷模。

但是，有明就有暗。不遵照TCP规范，甚至寻找漏洞、发起攻击，这种“小人”乃至“强盗”的行为，也并非少见，比如我们熟知的 **DDoS攻击**。

那么这节课，我们就不来学习怎么做君子了，当然，也不是教你做“小人”，而是我们要 **了解“小人”可能有的各种伎俩，通过Wireshark把这种种攻击行为照个彻底，认个清楚**。这样，以后你如果遇到这类情况，就心里有数，也有对策了。

## NTP反射攻击案例

我在公有云做技术工作的时候，发现游戏类业务遭到DDoS的情况比较多见。有一次，一个游戏客户就发现，他们的游戏服务器无法登录，被玩家投诉，可以说是十万火急。客户的工程师做了tcpdump抓包，然后赶紧把抓包文件传给我们一起分析。

> 补充：抓包示例文件已经上传至 [Gitee](https://gitee.com/steelvictor/network-analysis/tree/master/14)，建议Wireshark打开抓包文件，结合文稿一起学习。

从抓包文件概览来看，确实是不正常。按惯例，我们看一下Expert Information：

![图片](https://static001.geekbang.org/resource/image/fd/5a/fd308647a1b1fe2b1bb813113e857e5a.jpg?wh=1820x216)

游戏业务一般也是基于TCP，但这里并没多少TCP相关的信息。那我们看下具体报文呢？

![图片](https://static001.geekbang.org/resource/image/5b/0c/5beeb84467b2a31dd97a2e563f277c0c.jpg?wh=1920x980)

全部都是这种NTP Version 2, Private, Response, MON\_GETLIST\_1的报文。客户根本没有对外提供什么NTP服务，这些报文是怎么来的呢，这是攻击吗？

确实，这就是DDoS攻击的一种类型，叫 **NTP反射放大攻击**。NTP全称是Network Time Protocol，它的作用是通过网络服务来同步时间。其中有一项功能叫Monlist，它在一些比较老的设备上是默认启用的，会返回与NTP服务器进行过时间同步的最后600个客户端的IP。

响应包按照每6个IP进行分割，最多有100个响应包。这样的话，一个简单的NTP Monlist响应，就可能是请求的200多倍。想象一下，如果请求是1Gbps，那这次反射攻击就可以达到200Gbps以上，实在惊人！

我们还是用Wireshark，展开UDP部分，看一看这种Monlist响应报文的细节：

![图片](https://static001.geekbang.org/resource/image/26/f3/26cefaeyy5484c497d760719538301f3.jpg?wh=1660x680)

每个Monlist item占用72字节：

![图片](https://static001.geekbang.org/resource/image/4b/4a/4bbc3de9562104968a680e7bb9947a4a.jpg?wh=1264x1104)

选中一个Monlist item后，我们可以通过3种不同的方式找到它的长度：

- 它有个字段Size of data item的值是72，这是协议本身提供的元数据；
- 在下方的字节码部分，数一下有底色的字节数，也是72个；
- 窗口底部对我们选中的字段有提示字节数，这里也是72 bytes。

这些方法，对于你平时用Wireshark解读抓包文件，特别是需要核对字段的具体信息时，是挺有用的。

不过，现在Wireshark窗口里解读UDP报文长度不是很直观，这是因为 **Wireshark默认没有显示UDP长度的列，但我们可以自己添加**。在UDP详情里选中Length，然后右单击，选中Aplly as Column：

![图片](https://static001.geekbang.org/resource/image/b4/f1/b4cb43df336152e5d937de7ff63c19f1.jpg?wh=1920x985)

然后就能在主窗口里看到UDP报文长度了，这个列的默认名称是Length。当然你也可以把它改为UDP Length等你觉得更合适的名称。

![图片](https://static001.geekbang.org/resource/image/3b/8f/3b1e05cbab2fce92fd552af1f782ec8f.jpg?wh=1920x508)

从图上看，这些UDP报文的长度都不大，只有448字节，这是为什么呢？我们知道MTU一般是1500字节，去掉IP头20字节和UDP头8字节，最多还有1500-20-8=1472字节，远大于448字节，为什么不用足这1472字节呢？

其实，这里就涉及UDP的一个概念： **UDP报文的载荷最好不要大于512字节**。

这个限制来自于IPv4协议。在IPv4的协议规范 [RFC791](https://www.rfc-editor.org/rfc/rfc791#section-3.1) 里建议，虽然IP报文的长度字段是2个字节，最大可以到65535，但是由于网络不允许传输这么大的报文，所以IPv4规范建议，报文长度应该控制在相对小的范围内，这个范围是576字节，相应的UDP载荷在512字节以内：

```plain
The number 576 is selected to allow a reasonable sized data block to
    be transmitted in addition to the required header information.  For
    example, this size allows a data block of 512 octets plus 64 header
    octets to fit in a datagram.  The maximal internet header is 60
    octets, and a typical internet header is 20 octets, allowing a
    margin for headers of higher level protocols.

```

很多应用程序都做了这部分逻辑的处理，也就是控制UDP载荷在512字节以内，比如这次的NTP Monlist的长度就是NTP协议实现，而不是内核UDP实现的。另外像DNS解析，如果数据量超过512字节，也是会自动切换为TCP模式的，根本原因也是这个很早以前的规定。

那么检查了载荷，我们很快会发现新的问题：“这里怎么只有NTP回复，没有NTP请求呢？”

其实，这正是前面说的1Gbps能放大为200多Gbps的原因。它的背后，就是反射攻击的核心技巧： **它利用IP协议“不对源IP做验证”的不足，构造一个IP报文，其源IP为被攻击站点的IP，使得NTP服务器回复的报文也被发往被攻击站点**。大量的响应报文就被引到了被攻击站点这里。而且这个过程中，NTP服务器被利用了还不知道。我们看个示意图：

![](https://static001.geekbang.org/resource/image/cb/8e/cb817f657b773c832eceb3a0f9b52f8e.jpg?wh=2000x857)

如果我们面临这种攻击，该怎么办呢？

- 假如这些被利用的NTP服务器是我们的，那么需要升级版本，避免自己成为“帮凶”。
- 如果我们是单纯的被攻击者，那就需要上一些手段了，我会在这次课程的后半段讲到。这次的游戏客户，就是上了高防后，扛住了这次攻击。

我们再来看一个例子。

## SSDP反射型攻击案例

你可能听说过“肉机”这个词，这也是国内技术圈发明的一个有意思的词汇，它指的是被黑客掌握了系统权限的主机。作为傀儡，这些成千上万的“肉机”可以被黑客集中调动起来发起攻击行为。假如一个黑客组织掌握了1万台“肉机”，那么，只要每台“肉机”发起哪怕只有1Mbps的攻击流量，乘以1万，就是10个Gbps的流量，不可小视。

但是，要拿到这么多“肉机”却并非易事。于是，聪明的黑客又想到了另外一种思路：借力打力。

借什么力呢？借协议的“ **响应是请求的很多倍**”这个力。显然，前面介绍的NTP反射攻击就是这样的。所以这种攻击，英文里叫reflection attack with amplification。amplication就是放大的意思。在这种模式下，只需要量很少的“肉机”，就可以发起巨大的攻击流量。

下面是另外一个客户的案例。当时他们遭受了一波攻击，也正好做了抓包。我们看一下抓包文件的Expert Information：

![图片](https://static001.geekbang.org/resource/image/be/de/be8932473a55aeffef2557e0c5261fde.jpg?wh=1806x172)

> 补充：抓包示例文件已经上传至 [Gitee](https://gitee.com/steelvictor/network-analysis/tree/master/14)，建议Wireshark打开抓包文件，结合文稿一起学习。

你是不是也觉得比较奇怪？这里没有TCP握手报文，上来就是HTTP/1.1 200 OK，这HTTP有点“自来熟”啊。既然这里有51257个HTTP 200响应报文，那按常理也至少有几十个TCP连接，而这里连一个SYN和FIN都没有。

那就让我们直接看看这些HTTP 200具体是怎样的：

![图片](https://static001.geekbang.org/resource/image/a8/02/a86588af9b086c7fc91b108cb5152602.jpg?wh=859x724)

奇怪，这里srcPort和dstPort居然都是空白的？不过视线移到下方，很快就找到答案了：原来是用了UDP协议。我们上面的srcPort和dstPort列是指TCP的端口号，难怪是空白。

但更奇怪的问题来了：这里的HTTP竟然用了UDP作为传输协议？HTTP一般是用TCP协议的，那这里用UDP又是怎么回事呢？是不是感觉网络协议到处都可能有意想不到的情况？

其实，这就是有名的 **SSDP反射放大攻击**。SSDP是在UDP这个传输层协议上，用HTTP协议格式传送信息。2014年，人们发现SSDP可以被攻击者利用。启用了SSDP协议的主要是一些家用路由器，在它们的UPnP软件中有一个漏洞，这个漏洞被攻击者利用后，这些路由器会从端口1900返回响应报文。那么显然，这些响应报文的目的地址，是被攻击站点的IP，而不是攻击发起者自己的IP了。

具体的攻击过程，跟前面NTP反射攻击里面的图差不多，这里就不重复了。当时的应对方法也是上了高防系统，顶住了这次攻击。

> 补充：有趣的是，著名的网络服务公司Cloudflare把SSDP戏称为 **S** tupidly **S** imple **DDoS** **P** rotocol。你可以在 [这里](https://www.cloudflare.com/learning/ddos/ssdp-ddos-attack) 看到Cloudflare对SSDP攻击的更多解释。

如果你也担心自己家的路由器也中招了的话，可以自测一下。访问 [https://badupnp.benjojo.co.uk/](https://badupnp.benjojo.co.uk/) 这个站点，它会对你的出口IP（家用路由器的出口IP）进行探测，看看是否有1900端口可以被利用。如果没有漏洞，网页会提醒你“All good! It looks like you are not listening on UPnP on WAN”。

了解了这次攻击的类型，接下来我们再来看一下这次抓包的概览。这里我们要学习一个新的命令： **capinfos**。

capinfos这个命令，是Wireshark自带的工具集中的一个小工具，也就是你安装完Wireshark就有它了。我一般在命令行里用它来查看抓包文件的时长、总包量等信息。我们直接运行 **capinfos文件名**，输出如下：

```plain
$ capinfos SSDP_attack_example.pcap
File name:           SSDP_attack_example.pcap
File type:           Wireshark/tcpdump/... - pcap
File encapsulation:  Ethernet
File timestamp precision:  microseconds (6)
Packet size limit:   file hdr: 65535 bytes
Number of packets:   100 k
File size:           36 MB
Data size:           34 MB
Capture duration:    1.916902 seconds
First packet time:   2016-05-08 10:25:02.721642
Last packet time:    2016-05-08 10:25:04.638544
Data byte rate:      18 MBps
Data bit rate:       145 Mbps
Average packet size: 348.38 bytes
Average packet rate: 52 kpackets/s
SHA256:              8fa365f01c62023576623116410a6ca289915db4717e4805120009a575fdfb57
RIPEMD160:           5ab83442a5178b5f34bee1009a58ddb351bd292b
SHA1:                52a2c52644bc2753f9a11b7bf71eb1144f2c9a30
Strict time order:   True
Number of interfaces in file: 1
Interface #0 info:
                     Encapsulation = Ethernet (1 - ether)
                     Capture length = 65535
                     Time precision = microseconds (6)
                     Time ticks per second = 1000000
                     Number of stat entries = 0
                     Number of packets = 100000

```

上面的信息比较多，我们可以重点关注下面这几个信息：

```plain
Number of packets:   100 k
Capture duration:    1.916902 seconds
Average packet rate: 52 kpackets/s

```

可以看到，这次抓包一共抓取了10万个报文，耗时只有1.9秒，平均包率为52kpackets/s，也就是每秒5万2千个包。而且都是SSDP协议响应报文，所以是DDoS没错。

在平时，你想了解一个抓包文件的包率、时长、平均报文大小等信息的时候，都可以用capinfos命令来快速获得。

回顾完两个具体的案例，想必你对于DDoS有了感性的认识了，接下来我们就来系统地认识一下DDoS。

## 到底什么是DDoS攻击？

DDoS跟DOS有着密切的联系。DOS（Denial of Service），就是服务拒绝，黑客通过各种手段，使得被攻击者无法正常提供服务。DOS这种攻击早已经存在了，而DDoS（Distributed DOS）就是它的升级版， **通过调动分布在各地的客户端发起攻击，使得被攻击站点无法正常服务**。

DDoS属于“攻击”，但不是“入侵”。两者的区别是，攻击是破坏服务，入侵可能不破坏，但会窃取资料、劫持勒索等等。既然DDoS要破坏服务，那就需要破坏计算资源。那么，什么又是资源？

一般说的计算机资源还是CPU、内存这些。旨在耗尽CPU和内存资源，这也是早期的攻击形式，也跟很多年前软件病毒肆虐的时候类似。当时的攻击和病毒，主要目的是让被攻击站点本身失去服务能力。另外，早期的黑客大多也是极客，攻击是他们展现技术能力的一种方式。

不过，随着安全加固技术和意识的不断增强，攻破系统的成本越来越高，于是攻击者转换了方向。其实他们不需要想办法攻入对端，只要在前面的网络环节上搞破坏，同样可以达到让对方服务瘫痪的目的。这时，服务瘫痪的原因已经不是之前的服务本身不可用，而是变成：网络通道不可用了！

而这，就是DDoS的核心目标： **耗尽网络带宽**。

假设被攻击的站点的带宽为1Gbps，那么攻击者只要让到达这个站点的流量超过1Gbps，就可以让这个站点失去正常服务的能力。至于这些报文是否属于被攻击站点正在监听的有效流量，是没有关系的。它的目的很直接：把你家门口的路给堵死，让正常的流量没有机会进来。

我们看一下示意图：

![](https://static001.geekbang.org/resource/image/d4/0c/d46a0295a1b4f47b342c11c79f51530c.jpg?wh=2000x1125)

理解了原理，那么技术性问题就来了：如何产生巨大的流量呢？

一种常见的实现方式就是反射型攻击。它的核心方法论是：利用一些协议的“ **响应是请求的很多倍**”这样的特点，同时也利用“ **IP协议不验证源IP**”的不足，达到把流量引到被攻击站点上去的目的。

上面的NTP反射攻击和SSDP都是如此。除此以外，你有没有发现别的这种“响应报文是请求报文的很多倍”的情况呢？如果有，那么恭喜你，你也能找到反射攻击的方式了！

这可真的是“举一反三”。明白了反射型攻击的原理，你是不是好像也有机会自己创造出新的DDoS攻击手段了。当然，还有很多别的事情要搞定，但是核心思路你已经清楚了。现在的你，是不是对DDoS有了更加深刻的认识了呢？

这里还有个细节。你有没有发现，前面介绍的NTP反射攻击是依托于UDP协议的，其他很多DDoS类型也是利用了UDP。为什么都是UDP呢？让我们再来回答一下这个问题。

## 为什么UDP容易被用来做DDoS攻击？

TCP当然也可能被DDoS所用，但是相对来说，如果用同样的成本，选择反射型攻击更加高效。而反射型攻击，主要基于UDP，这是为什么呢？主要有两个原因。

### UDP报文简单易于构造

我们看一下UDP头部。 [RFC768](https://datatracker.ietf.org/doc/html/rfc768) 定义了UDP头部的格式：

![图片](https://static001.geekbang.org/resource/image/26/b2/26ed0d4f50a7cc54e910435c05b27bb2.jpg?wh=473x305)

由上图可见，UDP头部其实只有8个字节，分别是：

- 2个字节的源端口号；
- 2个字节的目的端口号；
- 2个字节的报文长度；
- 2个字节的校验和。

还是借助Wireshark，我们更加近距离地看一个UDP报文：

![图片](https://static001.geekbang.org/resource/image/90/98/90c05f5c609c11b49045b6f8d57a1298.jpg?wh=609x472)

而TCP头部就复杂多了，除了源目端口，还有序列号、确认号、各种标志位、各种TCP扩展选项等等。而因为UDP报文头部如此简单，这就减少了攻击者做伪造的难度，只要做好这几件事就好了：

- 伪造一个源IP；
- 找到NTP等有反射攻击漏洞的服务器；
- 向这些服务器发送构造好的虚假的UDP报文。

### UDP是无状态的

这可能是一个 **更加关键** 的原因。UDP是无状态的，不需要握手。像NTP反射攻击、SSDP反射攻击，都是只要“一问一答”即可，所以攻击者只需要伪造一个请求报文，那么后续的响应报文，自然就发送给了被攻击站点了。

![](https://static001.geekbang.org/resource/image/98/17/988449a5e4107ba3a0867f231c772917.jpg?wh=1698x806)

但是TCP就非常不同了。首先TCP需要三次握手，如果攻击者的SYN报文的源地址是伪造成被攻击站点的IP，那么SYN+ACK报文就直接回复到那个站点的IP了，而不是攻击者。然后会发生什么呢？

被攻击站点收到一个莫名其妙的SYN+ACK，就会被RST掉。这次TCP握手就这么结束了，攻击就没法继续了。

![](https://static001.geekbang.org/resource/image/04/8c/041893ed942fdf744bccbe8b520f8d8c.jpg?wh=1672x807)

那跳过TCP握手，直接发送应用层请求（源地址还是伪造成被攻击站点的IP）给反射服务呢？当然是直接被RST，因为连握手都没做过呢。

![](https://static001.geekbang.org/resource/image/bb/03/bb77fb1751yycf77e4bcae072dbc4503.jpg?wh=1687x807)

而且，即使通过了握手，后续通信双方还有对序列号和确认号进行校验等机制。虽然这些在技术上都可以实现，但难度大了很多，而选择UDP，就不需要考虑这么多问题。

所以， **用TCP的话就是直接攻击**，而不是反射攻击了。比如SYN攻击、半连接攻击、全连接攻击、CC攻击等等。从“性价比”上看，反射攻击的优势更大些。

## 如何对付DDoS？

前面我们分析了DDoS中最为典型的反射放大攻击。以后如果我们发现服务异常，比如客户端的请求十分卡顿的话，就可以在服务端抓包，然后进行分析，就能快速定位是否是DDoS攻击了。

当然，还有一个更为简单直接的证据，就是你的公网接口带宽使用图，如果图上有明显的突增，甚至达到了接口带宽的上限，那也基本可以判定是遭遇DDoS了。

![图片](https://static001.geekbang.org/resource/image/90/a4/9022db0b266107b161e2677yy309f8a4.jpg?wh=471x501)

上面都是排查的手段，那接下来如何处理呢？一般来说，你自己单干是不行的，这里给你介绍几种应对策略，这样你以后就心里有数了。

### 高防

一般来说，如果你的服务架设在公有云上，那么可以考虑使用云商或者其他专业安全服务商的高防产品。

**高防是需要放置在源站前面的一类安全防护和清洗系统。** 它利用了自身的足够大的带宽，以及强大的防护清洗集群，实现对流量清洗，最终把攻击流量拦截在外面，清洗过后的正常流量进入源站，得以被正常处理。示意图如下：

![](https://static001.geekbang.org/resource/image/3c/21/3c8bd54238a4b884dd42bfe95246fb21.jpg?wh=2000x1125)

> 补充：这里的源站，就是被攻击的站点。

由于高防按时计费而且费用高昂，一般平时是不接入高防的。只有探测到被攻击时，才自动或者手动转入高防。这里的“接入高防”是什么意思呢？其实就是把站点域名指向高防的域名，这样就把流量先流向高防，再经清洗后回到源站。

![](https://static001.geekbang.org/resource/image/59/75/595873d6f7d858f28d9e4be1592f4275.jpg?wh=2000x1125)

那如果攻击者不是通过域名解析，而是直接盯着IP做攻击的呢？也不难，你就把老的IP解绑，让攻击流量进入路由黑洞，然后绑定新的IP。这时候，不要暴露新的IP的信息，它只能给高防回源用，不能让更多的人知道。

你有没有发现，从防护的生效点来说，高防这种方式是作用在 **服务端这一侧**。那你可能会想到：如果我们能 **在攻击的源头就做防护**，那是不是效果会更好呢？这就是另一类DDoS防护产品的设计思想，其中比较典型的产品是电信云堤。

### 云堤

云堤本身属于运营商自己的系统，而无论被攻击站点还是肉机，都依托于运营商的公网线路才能进入因特网，所以云堤 **具有“地理”上的天然优势**。它可以作用在肉机的攻击流量进入骨干网之前，所以很可能这些攻击都没有机会走到被攻击站点的跟前了，相当于“扼杀在摇篮里”。我们看一下示意图：

![](https://static001.geekbang.org/resource/image/73/c7/733994d215a69b4b6372defde7dd48c7.jpg?wh=2000x1125)

### anycast和多POP

我们知道了DDoS的本质是挤占网络带宽，那么对付它的核心策略就是：

- 用更大的带宽来接纳，先解决正常流量被挤出网络的问题。
- 在接纳后进行清洗，把正常流量识别出来，发回给源站，让业务继续进行。

前面介绍了高防和云堤，两者分别在被攻击站点的近端和远端起到了作用，也都是商业服务。那么，另外一种方式是自己搞定，这也是一些 **自身规模比较大的网站会部署的架构**，它就是anycast和多POP。

anycast是网络术语，是指 **多个地点宣告同一个网段或者同一个IP地址的行为**。比如，最典型的电信的DNS服务地址114.114.114.114，还有谷歌的DNS服务8.8.8.8，就是在全国乃至全球各处做了anycast的IP地址。与这个词类似的，还有unicast和multicast，分别是指单播和多播。

比较大型的网站都会在各地部署POP点（也就是多POP），然后这些POP点会宣告相同的IP段。一旦有DDoS攻击，因为它的目标IP是属于anycast网段的，所以会被因特网的路由策略，相对均匀地分布到这些POP。

假如你有20个POP点宣告同一个网段，那么你就有机会把DDoS攻击化整为零，平均每个POP点承受1/20的攻击流量，大大降低了危害性。在攻击流量不高的时候，仅依靠自己的多个POP就可以吸收掉这些攻击流量，然后用自己的设备进行清洗就可以了。

这一点上看，anycast+多个POP+自有的清洗设备，这一整套做好以后，相当于自己建设了一个中小型的高防系统。我画了个示意图供你参考：

![](https://static001.geekbang.org/resource/image/dc/67/dc3faa23209f13da54799c62350c0267.jpg?wh=2000x1125)

> 补充：这里的anycast一般是作用在网段级别。而在单个IP级别的anycast应用还较局限，目前主要还是主要应用在基于UDP的服务，比如DNS服务上。基于anycast的HTTP是比较前沿的领域，目前有少数公司已经开始实践，相信在不久的将来，应该会看到越来越多的公司应用HTTP over anycast。

### CDN

与前一点类似，CDN也是通过“多点分布”来达到防护或者缓解DDoS攻击的目的。而且CDN服务商一般也会采用anycast等策略混合使用，使得其防护DDoS的能力更加出色。

## 小结

这节课，我们通过NTP反射攻击和SSDP反射攻击这两个典型的DDoS案例的学习，了解了反射放大攻击的特点，它主要利用了以下三点：

- **IP协议不对源IP进行校验**，所以可以伪造源IP，把它设定为被攻击站点的IP，这样就可以把响应流量引向被攻击站点。
- **UDP协议是无连接的**，可以直接进行应用层的一问一答，这就使得IP欺骗可以奏效。
- 某些服务具有“ **响应报文的大小是请求报文的很多倍**”的特点，使攻击行为达到了“四两拨千斤”的攻击效果。

我们也系统性地分析了DDoS的核心方法，也就是用“ **耗尽网络带宽**”的方式，让被攻击站点无法正常提供服务。在排查方面，当我们发现服务异常时，在服务端做抓包分析，可以快速定位是否有DDoS攻击。也可以直接根据带宽使用图，关注到突发的巨型流量时也可以直接判定是DDoS攻击。

另外，我们还了解了应对DDoS攻击的策略，包括：

- **使用高防产品**，可以防护非常巨大的攻击流量。
- 如果对防护效果有更高的需求，可以使用运营商的 **云堤类的产品。**
- 如果自身条件足够，可以部署 **多POP和anycast**，平均吸收攻击流量。
- 也可以 **上CDN**，让CDN天然的分布式布局减轻DDoS的影响。

在技术细节方面，你也可以记住这个新的命令 **capinfos**，用它可以快速获取到抓包文件的整体信息，包括抓包时长、总报文量、平均报文大小等信息。关于如何在Wireshark里解读出报文字段的长度，你也要知道至少下面这两种方法：

- 选中你要解读的报文字段，然后在下面的字节码部分，数一下有底色的字节个数。
- 还是选中你要解读的报文字段，在底边栏里也有对应的字节数的显示。

最后，你要知道这一点： **UDP载荷最好不要超过512字节**，这也是IPv4协议规范的建议，像NTP和DNS这些基于UDP的协议都实现了这个规范。

## 思考题

给你留两道思考题：

- “肉机”发出100Mbps的攻击流量，到达被攻击站点的时候，仍然是100Mbps吗？为什么呢？
- 为什么CDN可以达到缓解DDoS的效果呢？

欢迎你把答案和思考写到留言区，我们一起讨论，进步。