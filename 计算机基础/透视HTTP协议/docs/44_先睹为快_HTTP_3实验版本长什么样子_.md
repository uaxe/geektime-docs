你好，我是Chrono。

不知不觉，《透视HTTP协议》这个专栏马上就要两周岁了。前几天我看了一下专栏的相关信息，订阅数刚好破万，非常感谢包括你在内的所有朋友们的关心、支持、鼓励和鞭策。

在专栏的结束语里我曾经说过，希望HTTP/3发布之时能够再相会。而如今虽然它还没有发布，但也为时不远了。

所以今天呢，我就来和你聊聊HTTP/3的一些事，就当是“尝尝鲜”吧。

## HTTP/3的现状

从2019到2021的这两年间，大家对HTTP协议的关注重点差不多全都是放在HTTP/3标准的制订上。

最初专栏开始的时候，HTTP/3草案还是第20版，而现在则已经是第34版了，发展的速度可以说是非常快的，里面的内容也变动得非常多。很有可能最多再过一年，甚至是今年内，我们就可以看到正式的标准。

在标准文档的制订过程中，互联网业届也没有闲着，也在积极地为此做准备，以草案为基础做各种实验性质的开发。

这其中比较引人瞩目的要数CDN大厂Cloudflare，还有Web Server领头羊Nginx（而另一个Web Server Apache好像没什么动静）了。

Cloudflare公司用Rust语言编写了一个QUIC支持库，名字叫“quiche”，然后在上面加了一层薄薄的封装，由此能够以一个C模块的形式加入进Nginx框架，为Nginx提供了HTTP/3的功能。（可以参考这篇文章： [HTTP/3：过去，现在，还有未来](https://blog.cloudflare.com/zh-cn/http3-the-past-present-and-future-zh-cn/)）

不过Cloudflare的这个QUIC支持库属于“民间行为”，没有得到Nginx的认可。Nginx的官方HTTP/3模块其实一直在“秘密”开发中，在去年的6月份，这个模块终于正式公布了，名字就叫“http\_v3\_module”。（可以参考这篇文章： [Introducing a Technology Preview of NGINX Support for QUIC and HTTP/3](https://www.nginx.com/blog/introducing-technology-preview-nginx-support-for-quic-http-3/)）

目前，http\_v3\_module已经度过了Alpha阶段，处于Beta状态，但支持的草案版本是29，而不是最新的34。

这当然也有情可原。相比于HTTP/2，HTTP/3的变化太大了，Nginx团队的精力还是集中在核心功能实现上，选择一个稳定的版本更有利于开发，而且29后面的多个版本标准其实差异非常小（仅文字编辑变更）。

Nginx也为测试HTTP/3专门搭建了一个网站： [quic.nginx.org](https://quic.nginx.org/)，任何人都可以上去测试验证HTTP/3协议。

所以，接下来我们就用它来看看HTTP/3到底长什么样。

## 初识HTTP/3

在体验之前，得先说一下浏览器，这是测试QUIC和HTTP/3的关键：最好使用最新版本的Chrome或者Firefox，这里我用的是Chrome88。

打开浏览器窗口，输入测试网站的URI（ [https://quic.nginx.org/](https://quic.nginx.org/)），如果“运气好”，刷新几次就能够在网页上看到大大的QUIC标志了。

![](https://static001.geekbang.org/resource/image/82/e0/827d261f49f6a20eb227f851dec667e0.png?wh=986*398)

不过你很可能“运气”没有这么好，在网页上看到的QUIC标志是灰色的。这意味着暂时没有应用QUIC和HTTP/3，这就需要对Chrome做一点设置，开启QUIC的支持。

首先要在地址栏输入“chrome://flags”，打开设置页面，然后搜索“QUIC”，找到启用QUIC的选项，把它改为“Enabled”，具体可以参考下面的图片。

![](https://static001.geekbang.org/resource/image/67/65/674ff32bf05b5859fb6985e29f8c1e65.png?wh=1724*716)

接下来，我们要在命令行里启动Chrome浏览器，在命令行里传递“enable-quic”“quic-version”等参数来要求Chrome使用特定的草案版本。

下面的示例就是我在macOS上运行Chrome的命令行。你也可以参考Nginx网站上的README文档，在Windows或者Linux上用类似的形式运行Chrome的命令行：

```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
--enable-quic --quic-version=h3-29 \
--origin-to-force-quic-on=quic.nginx.org:443

```

如果这样操作之后网页上仍然是显示灰色标志也不要紧，你还可以用“F12”打开Chrome的开发者工具面板，查看protocol一栏。

应该可以看到大部分资源显示的还是“h2”，表示使用的是HTTP/2协议，但有一小部分资源显示的是“h3-29”，这就表示它是使用HTTP/3协议传输的，而后面的“29”后缀，意思是基于第29版草案，也就是说启用了QUIC+HTTP/3协议。

![](https://static001.geekbang.org/resource/image/c3/e6/c3a532736412a4457ee81a280fc76be6.png?wh=1664*1320)

## Wireshark抓包分析

好了，大概看了HTTP/3是什么样，有了感性认识，我们就可以进一步来抓包分析。

网络抓包工具Wireshark你一定已经比较熟悉了，这里同样要用最新的，不然可能识别不了QUIC和HTTP/3的数据包，比如我用的就是3.4.3。

QUIC的底层是UDP，所以在抓包的时候过滤器要设置成“udp port 443”，然后启动就可以了。这次我抓的包也放到了GitHub的 [Wireshark目录](https://github.com/chronolaw/http_study/tree/master/wireshark)，文件名是“44-1.pcapng”。

![](https://static001.geekbang.org/resource/image/6d/d4/6d217ee87e1f777d432059f81fc2f5d4.png?wh=1758*1132)

因为HTTP/3内置了TLS加密（可参考之前的 [第32讲](https://time.geekbang.org/column/article/115564)），所以用Wireshark抓包后看到的数据大部分都是乱码，想要解密看到真实数据就必须设置SSLKEYLOG（参考 [第26讲](https://time.geekbang.org/column/article/110354)）。

不过非常遗憾，不知道是什么原因，虽然我导出了SSLKEYLOG，但在Wireshark里还是无法解密HTTP/3的数据，显示解密错误。但同样的设置和操作步骤，抓包解密HTTPS和HTTP/2却是正常的，估计可能是目前Wireshark自身对HTTP/3的支持还不太完善吧。

所以今天我也就只能带你一起来看QUIC的握手阶段了。这个其实与TLS1.3非常接近，只不过是内嵌在了QUIC协议里，如果你学过了“安全篇”“飞翔篇”的课程，看QUIC应该是不会费什么力气。

首先我们来看Header数据：

```
[Packet Length: 1350]
1... .... = Header Form: Long Header (1)
.1.. .... = Fixed Bit: True
..00 .... = Packet Type: Initial (0)
.... 00.. = Reserved: 0
.... ..00 = Packet Number Length: 1 bytes (0)
Version: draft-29 (0xff00001d)
Destination Connection ID Length: 20
Destination Connection ID: 3ae893fa047246e55f963ea14fc5ecac3774f61e
Source Connection ID Length: 0

```

QUIC包头的第一个字节是标志位，可以看到最开始建立连接会发一个长包（Long Header），包类型是初始化（Initial）。

标志位字节后面是4字节的版本号，因为目前还是草案，所以显示的是“draft-29”。再后面，是QUIC的特性之一“连接ID”，长度为20字节的十六进制字符串。

这里我要特别提醒你注意，因为标准版本的演变，这个格式已经与当初 [第32讲](https://time.geekbang.org/column/article/115564) 的内容（draft-20）完全不一样了，在分析查看的时候一定要使用 [对应的RFC文档](https://tools.ietf.org/html/draft-ietf-quic-transport-28#section-17.2)。

往下再看，是QUIC的CRYPTO帧，用来传输握手消息，帧类型是0x06：

```
TLSv1.3 Record Layer: Handshake Protocol: Client Hello
    Frame Type: CRYPTO (0x0000000000000006)
    Offset: 0
    Length: 309
    Crypto Data
    Handshake Protocol: Client Hello

```

CRYPTO帧里的数据，就是QUIC内置的TLS “Client Hello”了，我把里面的一些重要信息摘了出来：

```
Handshake Protocol: Client Hello
   Handshake Type: Client Hello (1)
   Version: TLS 1.2 (0x0303)
   Random: b4613d...
   Cipher Suites (3 suites)
       Cipher Suite: TLS_AES_128_GCM_SHA256 (0x1301)
       Cipher Suite: TLS_AES_256_GCM_SHA384 (0x1302)
       Cipher Suite: TLS_CHACHA20_POLY1305_SHA256 (0x1303)
   Extension: server_name (len=19)
       Type: server_name (0)
       Server Name Indication extension
           Server Name: quic.nginx.org
   Extension: application_layer_protocol_negotiation (len=8)
       Type: application_layer_protocol_negotiation (16)
       ALPN Protocol
           ALPN Next Protocol: h3-29
   Extension: key_share (len=38)
       Key Share extension
   Extension: supported_versions (len=3)
       Type: supported_versions (43)
       Supported Version: TLS 1.3 (0x0304)

```

你看，这个就是标准的TLS1.3数据（伪装成了TLS1.2），支持AES128、AES256、CHACHA20三个密码套件，SNI是“quic.nginx.org”，ALPN是“h3-29”。

浏览器发送完Initial消息之后，服务器回复Handshake，用一个RTT就完成了握手，包的格式基本一样，用了一个CRYPTO帧和ACK帧，我就不细分析了（可参考 [相应的RFC](https://tools.ietf.org/html/draft-ietf-quic-transport-28#section-17.2)），只贴一下里面的“Server Hello”信息：

```
Handshake Protocol: Server Hello
    Handshake Type: Server Hello (2)
    Version: TLS 1.2 (0x0303)
    Random: d6aede...
    Cipher Suite: TLS_AES_128_GCM_SHA256 (0x1301)
    Extension: key_share (len=36)
        Key Share extension
    Extension: supported_versions (len=2)
        Type: supported_versions (43)
        Supported Version: TLS 1.3 (0x0304)

```

这里服务器选择了“TLS\_AES\_128\_GCM\_SHA256”，然后带回了随机数和key\_share，完成了握手阶段的密钥交换。

## 小结

好了，QUIC和HTTP/3的“抢鲜体验”就到这里吧，我简单小结一下今天的要点：

1. HTTP/3的最新草案版本是34，很快就会发布正式版本。
2. Nginx提供了对HTTP/3的实验性质支持，目前是Beta状态，只能用于测试。
3. 最新版本的Chrome和Firefox都支持QUIC和HTTP/3，但可能需要一些设置工作才能启用。
4. 访问专门的测试网站“quic.nginx.org”可以检查浏览器是否支持QUIC和HTTP/3。
5. 抓包分析QUIC和HTTP/3需要用最新的Wireshark，过滤器用UDP，还要导出SSLKEYLOG才能解密。

希望你看完这一讲后自己实际动手操作一下，访问网站再抓包，如果能正确解密HTTP/3数据，就把资料发出来，和我们分享下。

如果你觉得有所收获，也欢迎把这一讲的内容分享给你的朋友。

![](https://static001.geekbang.org/resource/image/1b/4f/1b4266dcedc5785f3023f47083e4894f.jpg?wh=2800*4221)