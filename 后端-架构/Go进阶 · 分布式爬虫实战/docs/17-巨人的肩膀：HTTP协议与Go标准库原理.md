你好，我是郑建勋。

在正式开始这节课之前，我想给你分享一段话。

> 学校教给我们很多寻找答案的方法。在我所研究的每一个有趣的问题中，挑战都是寻找正确的问题。当Mike Karels和我开始研究TCP拥堵时，我们花了几个月的时间盯着协议和数据包的痕迹，问 ：“为什么会失败？”。

> 有一天，在迈克的办公室里，我们中的一个人说：“我之所以搞不清楚它为什么会失败，是因为我不明白它一开始是怎么工作的。”这被证明是一个正确的问题，它迫使我们弄清楚使TCP工作的 “ack clocking”。在那之后，剩下的事情就很容易了。

这段话摘自《Computer Networking A Top-Down Approach 6th》这本书，它启发我们，解决网络方面的问题，核心就是要搞懂它的工作原理。

在上节课，我介绍了一个最简单的HTTP请求，了解了一个网络数据包是如何跨过千山万水到达对端的服务器的。不过就像前面引文说的那样，这是不够的。所以这节课，让我们更近一步，来看看当数据包到达对端服务器之后，操作系统和硬件会如何处理数据包，同时我将介绍HTTP协议，带你理清Go HTTP标准库高效处理网络数据包的底层设计原理。

## 操作系统处理数据包流程

当数据包到达目的地设备后，数据包需要经过复杂的逻辑处理最终到达应用程序。数据包的处理过程大致可以分为7步，我们可以根据下面这张流程图一层一层来理解。

![图片](https://static001.geekbang.org/resource/image/e7/ee/e7caaee0e1dyy95176868a29779fbfee.png?wh=1645x922)

当网络设备接收到数据，并储存到设备的缓冲区后（该缓冲区可能位于设备的内存，也可能通过 DMA 写入到主机内存），会首先通知操作系统内核对已接收的数据进行处理。

接收到新的数据包后，网卡设备将生成一个硬件中断信号。这个信号通常是由设备发送给中断控制器，再由中断控制器转发给 CPU。CPU 接到信号后，当前执行的任务被打断，转而执行由设备驱动注册的中断处理程序，中断处理程序将处理对应的设备事件。

Linux将中断处理程序分为两个部分：上半部和下半部，这是深思熟虑的结果。中断处理程序的上半部接受到中断时就立即执行，但是只做比较紧急的工作，这些工作都是在所有中断被禁止的情况下完成的。所以上半部要快，否则其他的中断就得不到及时的处理，导致硬件数据丢失。而耗时又不紧急的工作被推迟到下半部去做。上半部处理程序会将数据帧加入到内核的输入队列中，通知内核做进一步处理，并快速返回。

硬中断完成后，有可能会直接执行下半部处理程序，也有可能有更重要的任务要执行。当出现第二种情况，在后续会由每一个CPU 中都维护的ksoftirqd内核线程完成下半部处理程序。下半部处理程序中，操作系统会检查并剥离数据包Header，判断当前数据包应该被哪一个上层协议接收，依次传递到上层处理。整个过程中还穿插了hook函数，可以提供防火墙和拦截的功能（这是iptables等工具的工作原理）。

要深入了解Linux操作系统在这一过程的细节，你还可以参考《Understanding Linux Network Internals》这本书。

还记得之前提到的分层网络模型吗, 现代操作系统在处理网络协议栈时，链路层Ethernet协议、网络层IP协议、以及传输层TCP协议在当前都是在操作系统内核实现的。而应用层是在用户态，由应用程序实现的。应用程序与操作系统之间交流的接口是通过操作系统提供的Socket 系统调用API完成的。

下面这张图列出了硬件、操作系统内核、用户态空间中分别对应的组件和交互。操作系统与硬件之间通过设备驱动进行通信，而应用程序与操作系统之间通过Socket系统调用API进行通信。

![图片](https://static001.geekbang.org/resource/image/ce/f4/ce681ef43f89c3106779b57d48a5c5f4.jpg?wh=1920x1344)

Socket 相关的网络编程API用于实现连接、断开、监听、IO多路复用等功能。如果你想进一步了解Socket网络编程的细节，可以参考《UNIX Network Programming》。

另外，有许多工具可以方便查看、调试网络相关的状态，例如netstat工具可以查看网络连接状态，ss工具可以查看与Socket相关的信息。更多的网络工具还可以查看《Systems Performance, 2nd Edition》。

## HTTP协议解析

之前我们提到，TCP协议的处理是在操作系统内核实现的。操作系统最终会剥离TCP Header，识别具体的端口号，并通过Socket接口将数据传递到指定的应用程序，例如浏览器。当今使用最广泛的网络协议HTTP就位于应用层，对HTTP协议的处理也是在应用程序中完成的。

Go语言提供的HTTP库对HTTP协议进行了深度封装，这样开发者就不用自己实现协议中各种复杂和特殊的情况了，这是一种生产力的释放。

不过，就像武侠小说中学会了武功招式还需要深厚的内功才能发挥出招式的威力一样，开发的便利并不意味着我们不用了解HTTP协议。

例如，服务器返回了一个499状态码是什么意思；如何让程序模拟浏览器访问服务器；如果使用HTTP代理访问外部网络，HTTP协议有什么问题；为什么需要HTTPS、HTTP/2。要回答这些问题，都需要我们对HTTP协议有深入的了解。

下面我用curl命令访问外部网站，帮助你在这个过程中更好地理解HTTP协议。

```plain
» curl www.baidu.com -vvv
*   Trying 110.242.68.3...
* TCP_NODELAY set
* Connected to www.baidu.com (110.242.68.3) port 80 (#0)
> GET / HTTP/1.1
> Host: www.baidu.com
> User-Agent: curl/7.64.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Accept-Ranges: bytes
< Content-Length: 2381
< Content-Type: text/html
< Date: Mon, 27 Jun 2022 16:04:17 GMT
< Set-Cookie: BDORZ=27315; max-age=86400; domain=.baidu.com; path=/
<
<!DOCTYPE html>
...
* Closing connection 0

```

使用curl命令的 -vvv 标识可以打印出详细的协议日志，下面我逐行解读一下。

- 第一行：curl 命令是执行HTTP请求的常见工具。其中， [www.baidu.com](https://www.baidu.xn--com-t33er8od2z/) 是域名。\*
- 第二行通过DNS解析出它对应的IP地址为110.242.68.3。
- 第三行：“TCP\_NODELAY set ”表明 TCP 正在无延迟地直接发送数据，TCP\_NODELAY是TCP众多选项的一个。
- 第四行：“port 80” 代表连接到服务的80端口， 80端口其实是HTTP协议的默认端口。
- 有 `>` 标识的5-8行数据才是真正发送到服务器的HTTP请求。数据GET / HTTP/1.1 表明当前使用的是HTTP的GET方法，并且协议版本是HTTP1.1。
- HTTP协议可以在请求头中加入多个key-value信息。第六行“Host: [www.baidu.com](https://www.baidu.com)”表示当前请求的主机，我们这里是百度的域名。第七行“User-Agent”表示最终用户发出 HTTP 请求的计算机程序，在这里是curl工具。
- 另外，第七行Accept标头还告诉我们 Web 服务器客户端可以理解的内容类型。这里\*/\*表示类型不限，可能是图片、视频、文字等。
- 十到十七行表示服务端返回的信息，它们的规则跟前面类似。“HTTP/1.1 200 OK ”是服务器的响应。服务器使用 HTTP 版本和响应状态码进行响应。状态码 1XX 表示信息，2XX 表示成功，3XX 表示重定向，4XX 表示请求有问题，5XX 表示服务器异常。在这里状态码为 200 ，说明响应成功了。
- 第十二行：“Content-Length: 2381 ”表明服务器返回消息的大小为2381字节。下一行的“Content-Type: text/html ”表明当前返回的是HTML文本。
- 第十四行：“Date: Mon, 27 Jun 2022 16:04:17 GMT ”是当前Web服务器生成消息时的格林威治时间。
- 第十五行：“Set-Cookie”的意思是，服务器让客户端设置cookie信息，这样客户端再次请求该网站时，HTTP 请求头中将带上cookie信息，这样服务器可以减少鉴权操作，从而加快消息处理和返回的速度。
- 一连串响应头的后面是百度返回的HTML文本，这就是我们在浏览器上访问页面的源代码，并最终被浏览器渲染。
- 最后\\* Closing connection 0 表明连接最终被关闭。

如果你想更深入地学习HTTP协议，推荐你阅读《HTTP: The Definitive Guide》 和《High Performance Browser Networking》这两本书。

## HTTP协议的困境

HTTP1.0版本诞生于1995年，在20余年里，HTTP协议已经成为了最广泛使用的网络协议。但是随着互联网的快速发展，网络环境发生了不少变化，包括：

- 更多的资源分布在不同的主机中，当我们访问一个网页时，这个网页的图片等资源可能来自于外部几十个网站；
- 资源占用的空间也越来越大；
- 另外，相对于网络带宽，网络往返延迟变成最大的瓶颈。

在这个背景下，HTTP开始面临一系列性能问题，例如头阻塞问题（Head of Line）等。这就有了后续一系列对HTTP协议的优化，并产生了HTTP/2 和QUIC协议。

如果你想更深入地学习HTTP/2协议，推荐你阅读《HTTP/2 in Action》。如果你想深入了解QUIC协议，推荐你阅读QUIC的 [协议文档](https://datatracker.ietf.org/doc/html/rfc9000) 以及这篇解释HTTP/3的 [文章](https://www.smashingmagazine.com/2021/08/http3-core-concepts-part1/)。

## HTTP请求底层原理

我之前在 [第7讲](https://time.geekbang.org/column/article/596287) 已经介绍过，借助epoll多路复用的机制和Go语言的调度器，Go可以在同步编程的语义下实现异步I/O的网络编程。在这个认知基础上，我们继续来看看HTTP标准库如何高效实现HTTP协议的请求与处理。

我们还是继续使用发送请求这个简单的例子。当http.Get函数完成基本的请求封装后，会进入到核心的主入口函数Transport.roundTrip，参数中会传递request请求数据。

Transport.roundTrip函数会选择一个合适的连接来发送这个request请求，并返回response。整个流程主要分为两步：

- 使用getConn函数来获得底层TCP连接；
- 调用roundTrip函数发送request并返回response，此外还需要处理特殊协议，例如重定向、keep-alive等。

要注意的是，并不是每一次getConn函数都需要经过TCP的3次握手才能建立新的连接。具体的getConn函数如下：

```plain
// 获取链接
func (t *Transport) getConn(treq *transportRequest, cm connectMethod) (pc *persistConn, err error) {
	 ...

	// 第一步，查看idle conn连接池中是否有空闲链接，如果有，则直接获取到并返回。如果没有，当前w会放入到idleConnWait等待队列中。
	if delivered := t.queueForIdleConn(w); delivered {
		pc := w.pc
		return pc, nil
	}

	// 如果没有闲置的连接，则尝试与对端进行tcp连接。
    // 注意这里连接是异步的，这意味着当前请求是有可能提前从另一个刚闲置的连接中拿到请求的。这取决于哪一个更快。
	t.queueForDial(w)

	// Wait for completion or cancellation.
	// 拿到conn后会close(w.ready)
	select {
	case <-w.ready:
		return w.pc, w.err
	 // 处理请求的退出与
  case <-req.Cancel:
		return nil, errRequestCanceledConn
     ...
		}
		return nil, err
	}
}

```

可以看到，Go标准库在这里使用了连接池来优化获取连接的过程。之前已经与服务器完成请求的连接一般不会立即被销毁（HTTP/1.1默认使用了keep-alive:true，可以复用连接），而是会调用tryPutIdleConn函数放入到连接池中。通过下图左侧的部分可以看到请求结束后连接的归宿（连接也可能会直接被销毁，例如请求头中指定了keep-alive属性为false 或者连接已经超时）。

![](https://static001.geekbang.org/resource/image/2e/3f/2ef71447e2e1f6ceae194864ae10c43f.jpg?wh=1920x1667)

使用连接池的收益是非常明显的，因为复用连接之后就不用再进行TCP三次握手了，这大大减少了请求的时间。举个特别的例子，在使用了HTTPS协议时，在三次握手基础上还增加了额外的鉴权协调，初始化的建连过程甚至需要花费几十到上百毫秒。

另外连接池的设计也很有讲究，例如连接池中的连接到了一定的时间需要强制关闭。获取连接时的逻辑如下：

- 当连接池中有对应的空闲连接时，直接使用该连接；
- 当连接池中没有对应的空闲连接时，正常情况下会通过异步与服务端建连的方式获取连接，并将当前协程放入到等待队列中。

连接的第一步是通过Resolver.resolveAddrList方法访问DNS服务器，获取 [www.baidu.com](https://www.baidu.com) 网站对应的IP地址。下面这张图展示了借助DNS协议查找域名对应的IP地址的过程。

![图片](https://static001.geekbang.org/resource/image/66/9d/6608af192fe75a581yyf8d3411af779d.jpg?wh=1920x1047)

客户端首先查看是否有本地缓存，如果没有，则会用递归方式从权威域名服务器中获取DNS信息并缓存下来。如果你想深入了解DNS协议，可以参考《Introduction to Computer Networks and Cybersecurity》的第二章。

在与远程服务器建连的过程中，当前的协程会进入阻塞等待的状态。正常情况下，当前请求的协程会等待连接完毕。但是因为建立连接的过程还是比较耗时的，所以如果在这个过程中正好有一个其他连接使用完了，协程就会优先使用该连接。

这种巧妙的设计依托了轻量级协程的优势，获取连接的具体流程如下图右侧所示：

![](https://static001.geekbang.org/resource/image/2e/3f/2ef71447e2e1f6ceae194864ae10c43f.jpg?wh=1920x1667)

为利用协程并发的优势，Transport.roundTrip协程获取到连接后，会调用Transport.dialConn创建读写buffer以及读数据与写数据的两个协程，分别负责处理发送请求和服务器返回的消息：

```plain
func (t *Transport) dialConn(ctx context.Context, cm connectMethod) (pconn *persistConn, err error) {
	...
  // buffer
	pconn.br = bufio.NewReaderSize(pconn, t.readBufferSize())
	pconn.bw = bufio.NewWriterSize(persistConnWriter{pconn}, t.writeBufferSize())

	// 创建读写通道，writeLoop用于发送request，readLoop用于接收响应。roundTrip函数中会通过chan给writeLoop发送
    // pconn.br给readLoop使用，pconn.bw给writeLoop使用
	go pconn.readLoop()
	go pconn.writeLoop()
}

```

整个处理流程和协程间协调如下图所示：

![](https://static001.geekbang.org/resource/image/5b/17/5b18b3086f15317c87d11yyfca965017.jpg?wh=1920x1047)

HTTP请求调用的核心函数是roundTrip，它会首先传递请求给writeLoop协程，让writeLoop协程写入数据。接着，通知readLoop协程让它准备好读取数据。等writeLoop成功写入数据后，writeLoop会通知readLoop断开后是否可以重用连接。然后writeLoop会通知上游写入是否成功。如果写入失败，上游会直接关闭连接。

当readLoop接收到服务器发送的响应数据之后，会通知上游并且将response数据返回到上游，应用层会获取返回的response数据，并进行相应的业务处理 。应用层读取完毕response数据后，HTTP标准库会自动调用close函数，该函数会通知readLoop“数据读取完毕”。这样readLoop就可以进一步决策了。readLoop需要判断是继续循环等待服务器消息，还是将当前连接放入到连接池中，或者是直接销毁。

Go HTTP标准库使用了连接池等技术帮助我们更好地管理连接、高效读写消息、并托管了与操作系统之间的交互。

## 总结

数据包到达操作系统之后，借助硬件、驱动、CPU与操作系统之间的紧密配合，可以被快速处理。操作系统对网络协议做了大量的托管处理，依靠内核对链路层、网络层、传输层进行了处理。而应用层则需要依靠具体的应用程序进行处理。

在内核与应用程序之间，内核暴露了Socket编程的API和很多I/O多路复用的机制，它们被Go标准库封装起来，而HTTP标准库又在此基础上封装了HTTP协议。HTTP标准库处理复杂多样的协议语言（HTTP、HTTPS、HTTP/2），通过连接池对连接进行复用管理、并且将读写分离为两个协程，高效处理数据并形成清晰的语义。

## 课后题

学完这节课，我也给你留两道思考题吧。

1. 你认为Go标准库的这种实现方式有哪些不足的地方？
2. Go标准库使用了连接池，你觉得实现一个连接池应该考虑哪些因素？

欢迎你在留言区留下自己思考的结果，也可以把这节课分享给对这个话题感兴趣的同事和朋友，我们下节课再见！