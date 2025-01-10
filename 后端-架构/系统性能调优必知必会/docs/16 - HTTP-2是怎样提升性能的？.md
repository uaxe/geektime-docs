你好，我是陶辉。

上一讲我们从多个角度优化HTTP/1的性能，但获得的收益都较为有限，而直接将其升级到兼容HTTP/1的HTTP/2协议，性能会获得非常大的提升。

HTTP/2协议既降低了传输时延也提升了并发性，已经被主流站点广泛使用。多数HTTP头部都可以被压缩90%以上的体积，这节约了带宽也提升了用户体验，像Google的高性能协议gRPC也是基于HTTP/2协议实现的。

目前常用的Web中间件都已支持HTTP/2协议，然而如果你不清楚它的原理，对于Nginx、Tomcat等中间件新增的流、推送、消息优先级等HTTP/2配置项，你就不知是否需要调整。

同时，许多新协议都会参考HTTP/2优秀的设计，如果你不清楚HTTP/2的性能究竟高在哪里，也就很难对当下其他应用层协议触类旁通。而且，HTTP/2协议也并不是毫无缺点，到2020年3月时它的替代协议 [HTTP/3](https://zh.wikipedia.org/wiki/HTTP/3) 已经经历了 [27个草案](https://tools.ietf.org/html/draft-ietf-quic-http-27)，推出在即。HTTP/3的目标是优化传输层协议，它会保留HTTP/2协议在应用层上的优秀设计。如果你不懂HTTP/2，也就很难学会未来的HTTP/3协议。

所以，这一讲我们就将介绍HTTP/2对HTTP/1.1协议都做了哪些改进，从消息的编码、传输等角度说清楚性能提升点，这样，你就能理解支持HTTP/2的中间件为什么会提供那些参数，以及如何权衡HTTP/2带来的收益与付出的升级成本。

## 静态表编码能节约多少带宽？

HTTP/1.1协议最为人诟病的是ASCII头部编码效率太低，浪费了大量带宽。HTTP/2使用了静态表、动态表两种编码技术（合称为HPACK），极大地降低了HTTP头部的体积，搞清楚编码流程，你自然就会清楚服务器提供的http2\_max\_requests等配置参数的意义。

我们以一个具体的例子来观察编码流程。每一个HTTP/1.1请求都会有Host头部，它指示了站点的域名，比如：

```
Host: test.taohui.tech\r\n

```

算上冒号空格以及结尾的\\r\\n，它占用了24字节。 **使用静态表及Huffman编码，可以将它压缩为13字节，也就是节约了46%的带宽！** 这是如何做到的呢？

我用Chrome访问站点test.taohui.tech，并用Wireshark工具抓包（关于如何用Wireshark抓HTTP/2协议的报文，如果你还不太清楚，可参见 [《Web协议详解与抓包实战》第51课](https://time.geekbang.org/course/detail/175-104932)）后，下图高亮的头部就是第1个请求的Host头部，其中每8个蓝色的二进制位是1个字节，报文中用了13个字节表示Host头部。

![](https://static001.geekbang.org/resource/image/09/1f/097e7f4549eb761c96b61368c416981f.png?wh=1529*651)

HTTP/2能够用13个字节编码原先的24个字节，是依赖下面这3个技术。

首先基于二进制编码，就不需要冒号、空格和\\r\\n作为分隔符，转而用表示长度的1个字节来分隔即可。比如，上图中的01000001就表示Host，而10001011及随后的11个字节表示域名。

其次，使用静态表来描述Host头部。什么是静态表呢？HTTP/2将61个高频出现的头部，比如描述浏览器的User-Agent、GET或POST方法、返回的200 SUCCESS响应等，分别对应1个数字再构造出1张表，并写入HTTP/2客户端与服务器的代码中。由于它不会变化，所以也称为静态表。

![](https://static001.geekbang.org/resource/image/5c/98/5c180e1119c1c0eb66df03a9c10c5398.png?wh=635*850)

这样收到01000001时，根据 [RFC7541](https://tools.ietf.org/html/rfc7541) 规范，前2位为01时，表示这是不包含Value的静态表头部：

![](https://static001.geekbang.org/resource/image/cd/37/cdf16023ab2c2f4f67f0039b8da47837.png?wh=752*348)

再根据索引000001查到authority头部（Host头部在HTTP/2协议中被改名为authority）。紧跟的字节表示域名，其中首个比特位表示域名是否经过Huffman编码，而后7位表示了域名的长度。在本例中，10001011表示域名共有11个字节（8+2+1=11），且使用了Huffman编码。

最后，使用静态Huffman编码，可以将16个字节的test.taohui.tech压缩为11个字节，这是怎么做到的呢？根据信息论，高频出现的信息用较短的编码表示后，可以压缩体积。因此，在统计互联网上传输的大量HTTP头部后，HTTP/2依据统计频率将ASCII码重新编码为一张表，参见 [这里](https://tools.ietf.org/html/rfc7541#page-27)。test.taohui.tech域名用到了10个字符，我把这10个字符的编码列在下表中。

![](https://static001.geekbang.org/resource/image/81/de/81d2301553c825a466b1f709924ba6de.jpg?wh=1164*1022)

这样，接收端在收到下面这串比特位（最后3位填1补位）后，通过查表（请注意每个字符的颜色与比特位是一一对应的）就可以快速解码为：

![](https://static001.geekbang.org/resource/image/57/50/5707f3690f91fe54045f4d8154fe4e50.jpg?wh=1808*338)

由于8位的ASCII码最小压缩为5位，所以静态Huffman的最大压缩比只有5/8。关于Huffman编码是如何构造的，你可以参见 [每日一课《HTTP/2 能带来哪些性能提升？》](https://time.geekbang.org/dailylesson/detail/100028441)。

## 动态表编码能节约多少带宽？

虽然静态表已经将24字节的Host头部压缩到13字节， **但动态表可以将它压缩到仅1字节，这就能节省96%的带宽！** 那动态表是怎么做到的呢？

你可能注意到，当下许多页面含有上百个对象，而REST架构的无状态特性，要求下载每个对象时都得携带完整的HTTP头部。如果HTTP/2能在一个连接上传输所有对象，那么只要客户端与服务器按照同样的规则，对首次出现的HTTP头部用一个数字标识，随后再传输它时只传递数字即可，这就可以实现几十倍的压缩率。所有被缓存的头部及其标识数字会构成一张表，它与已经传输过的请求有关，是动态变化的，因此被称为动态表。

静态表有61项，所以动态表的索引会从62起步。比如下图中的报文中，访问test.taohui.tech的第1个请求有13个头部需要加入动态表。其中，Host: test.taohui.tech被分配到的动态表索引是74（索引号是倒着分配的）。

![](https://static001.geekbang.org/resource/image/69/e0/692a5fad16d6acc9746e57b69b4f07e0.png?wh=808*829)

这样，后续请求使用到Host头部时，只需传输1个字节11001010即可。其中，首位1表示它在动态表中，而后7位1001010值为64+8+2=74，指向服务器缓存的动态表第74项：

![](https://static001.geekbang.org/resource/image/9f/31/9fe864459705513bc361cee5eafd3431.png?wh=876*313)

静态表、Huffman编码、动态表共同完成了HTTP/2头部的编码，其中，前两者可以将体积压缩近一半，而后者可以将反复传输的头部压缩95%以上的体积！

![](https://static001.geekbang.org/resource/image/c0/0c/c08db9cb2c55cb05293c273b8812020c.png?wh=1117*339)

那么，是否要让一条连接传输尽量多的请求呢？并不是这样。动态表会占用很多内存，影响进程的并发能力，所以服务器都会提供类似http2\_max\_requests这样的配置，限制一个连接上能够传输的请求数量，通过关闭HTTP/2连接来释放内存。 **因此，http2\_max\_requests并不是越大越好，通常我们应当根据用户浏览页面时访问的对象数量来设定这个值。**

## 如何并发传输请求？

HTTP/1.1中的KeepAlive长连接虽然可以传输很多请求，但它的吞吐量很低，因为在发出请求等待响应的那段时间里，这个长连接不能做任何事！而HTTP/2通过Stream这一设计，允许请求并发传输。因此，HTTP/1.1时代Chrome通过6个连接访问页面的速度，远远比不上HTTP/2单连接的速度，具体测试结果你可以参考这个 [页面](https://http2.akamai.com/demo)。

为了理解HTTP/2的并发是怎样实现的，你需要了解Stream、Message、Frame这3个概念。HTTP请求和响应都被称为Message消息，它由HTTP头部和包体构成，承载这二者的叫做Frame帧，它是HTTP/2中的最小实体。Frame的长度是受限的，比如Nginx中默认限制为8K（http2\_chunk\_size配置），因此我们可以得出2个结论：HTTP消息可以由多个Frame构成，以及1个Frame可以由多个TCP报文构成（TCP MSS通常小于1.5K）。

再来看Stream流，它与HTTP/1.1中的TCP连接非常相似，当Stream作为短连接时，传输完一个请求和响应后就会关闭；当它作为长连接存在时，多个请求之间必须串行传输。在HTTP/2连接上，理论上可以同时运行无数个Stream，这就是HTTP/2的多路复用能力，它通过Stream实现了请求的并发传输。

[![](https://static001.geekbang.org/resource/image/b0/c8/b01f470d5d03082159e62a896b9376c8.png?wh=576*468)](https://developers.google.com/web/fundamentals/performance/http2)

虽然RFC规范并没有限制并发Stream的数量，但服务器通常都会作出限制，比如Nginx就默认限制并发Stream为128个（http2\_max\_concurrent\_streams配置），以防止并发Stream消耗过多的内存，影响了服务器处理其他连接的能力。

HTTP/2的并发性能比HTTP/1.1通过TCP连接实现并发要高。这是因为， **当HTTP/2实现100个并发Stream时，只经历1次TCP握手、1次TCP慢启动以及1次TLS握手，但100个TCP连接会把上述3个过程都放大100倍！**

HTTP/2还可以为每个Stream配置1到256的权重，权重越高服务器就会为Stream分配更多的内存、流量，这样按照资源渲染的优先级为并发Stream设置权重后，就可以让用户获得更好的体验。而且，Stream间还可以有依赖关系，比如若资源A、B依赖资源C，那么设置传输A、B的Stream依赖传输C的Stream即可，如下图所示：

[![](https://static001.geekbang.org/resource/image/9c/97/9c068895a9d2dc66810066096172a397.png?wh=968*399)](https://developers.google.com/web/fundamentals/performance/http2)

## 服务器如何主动推送资源？

HTTP/1.1不支持服务器主动推送消息，因此当客户端需要获取通知时，只能通过定时器不断地拉取消息。HTTP/2的消息推送结束了无效率的定时拉取，节约了大量带宽和服务器资源。

![](https://static001.geekbang.org/resource/image/f0/16/f0dc7a3bfc5709adc434ddafe3649316.png?wh=800*402)

HTTP/2的推送是这么实现的。首先，所有客户端发起的请求，必须使用单号Stream承载；其次，所有服务器进行的推送，必须使用双号Stream承载；最后，服务器推送消息时，会通过PUSH\_PROMISE帧传输HTTP头部，并通过Promised Stream ID告知客户端，接下来会在哪个双号Stream中发送包体。

![](https://static001.geekbang.org/resource/image/a1/62/a1685cc8e24868831f5f2dd961ad3462.png?wh=1036*607)

在SDK中调用相应的API即可推送消息，而在Web资源服务器中可以通过配置文件做简单的资源推送。比如在Nginx中，如果你希望客户端访问/a.js时，服务器直接推送/b.js，那么可以这么配置：

```
location /a.js {
  http2_push /b.js;
}

```

服务器同样也会控制并发推送的Stream数量（如http2\_max\_concurrent\_pushes配置），以减少动态表对内存的占用。

## 小结

这一讲我们介绍了HTTP/2的高性能是如何实现的。

静态表和Huffman编码可以将HTTP头部压缩近一半的体积，但这只是连接上第1个请求的压缩比。后续请求头部通过动态表可以压缩90%以上，这大大提升了编码效率。当然，动态表也会导致内存占用过大，影响服务器的总体并发能力，因此服务器会限制HTTP/2连接的使用时长。

HTTP/2的另一个优势是实现了Stream并发，这节约了TCP和TLS协议的握手时间，并减少了TCP的慢启动阶段对流量的影响。同时，Stream之间可以用Weight权重调节优先级，还可以直接设置Stream间的依赖关系，这样接收端就可以获得更优秀的体验。

HTTP/2支持消息推送，从HTTP/1.1的拉模式到推模式，信息传输效率有了巨大的提升。HTTP/2推消息时，会使用PUSH\_PROMISE帧传输头部，并用双号的Stream来传递包体，了解这一点对定位复杂的网络问题很有帮助。

HTTP/2的最大问题来自于它下层的TCP协议。由于TCP是字符流协议，在前1字符未到达时，后接收到的字符只能存放在内核的缓冲区里，即使它们是并发的Stream，应用层的HTTP/2协议也无法收到失序的报文，这就叫做队头阻塞问题。解决方案是放弃TCP协议，转而使用UDP协议作为传输层协议，这就是HTTP/3协议的由来。

![](https://static001.geekbang.org/resource/image/38/d1/3862dad08cecc75ca6702c593a3c9ad1.png?wh=1280*635)

## 思考题

最后，留给你一道思考题。为什么HTTP/2要用静态Huffman查表法对字符串编码，基于连接上的历史数据统计信息做动态Huffman编码不是更有效率吗？欢迎你在留言区与我一起探讨。

感谢阅读，如果你觉得这节课对你有一些启发，也欢迎把它分享给你的朋友。