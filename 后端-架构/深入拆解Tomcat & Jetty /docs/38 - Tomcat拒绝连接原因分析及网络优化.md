专栏上一期我们分析各种JVM OutOfMemory错误的原因和解决办法，今天我们来看看网络通信中可能会碰到的各种错误。网络通信方面的错误和异常也是我们在实际工作中经常碰到的，需要理解异常背后的原理，才能更快更精准地定位问题，从而找到解决办法。

下面我会先讲讲Java Socket网络编程常见的异常有哪些，然后通过一个实验来重现其中的Connection reset异常，并且通过配置Tomcat的参数来解决这个问题。

## 常见异常

**java.net.SocketTimeoutException**

指超时错误。超时分为 **连接超时** 和 **读取超时**，连接超时是指在调用Socket.connect方法的时候超时，而读取超时是调用Socket.read方法时超时。请你注意的是，连接超时往往是由于网络不稳定造成的，但是读取超时不一定是网络延迟造成的，很有可能是下游服务的响应时间过长。

**java.net.BindException: Address already in use: JVM\_Bind**

指端口被占用。当服务器端调用new ServerSocket(port)或者Socket.bind函数时，如果端口已经被占用，就会抛出这个异常。我们可以用 `netstat –an` 命令来查看端口被谁占用了，换一个没有被占用的端口就能解决。

**java.net.ConnectException: Connection refused: connect**

指连接被拒绝。当客户端调用new Socket(ip, port)或者Socket.connect函数时，可能会抛出这个异常。原因是指定IP地址的机器没有找到；或者是机器存在，但这个机器上没有开启指定的监听端口。

解决办法是从客户端机器ping一下服务端IP，假如ping不通，可以看看IP是不是写错了；假如能ping通，需要确认服务端的服务是不是崩溃了。

**java.net.SocketException: Socket is closed**

指连接已关闭。出现这个异常的原因是通信的一方主动关闭了Socket连接（调用了Socket的close方法），接着又对Socket连接进行了读写操作，这时操作系统会报“Socket连接已关闭”的错误。

**java.net.SocketException: Connection reset/Connect reset by peer: Socket write error**

指连接被重置。这里有两种情况，分别对应两种错误：第一种情况是通信的一方已经将Socket关闭，可能是主动关闭或者是因为异常退出，这时如果通信的另一方还在写数据，就会触发这个异常（Connect reset by peer）；如果对方还在尝试从TCP连接中读数据，则会抛出Connection reset异常。

为了避免这些异常发生，在编写网络通信程序时要确保：

- 程序退出前要主动关闭所有的网络连接。
- 检测通信的另一方的关闭连接操作，当发现另一方关闭连接后自己也要关闭该连接。

**java.net.SocketException: Broken pipe**

指通信管道已坏。发生这个异常的场景是，通信的一方在收到“Connect reset by peer: Socket write error”后，如果再继续写数据则会抛出Broken pipe异常，解决方法同上。

**java.net.SocketException: Too many open files**

指进程打开文件句柄数超过限制。当并发用户数比较大时，服务器可能会报这个异常。这是因为每创建一个Socket连接就需要一个文件句柄，此外服务端程序在处理请求时可能也需要打开一些文件。

你可以通过 `lsof -p pid` 命令查看进程打开了哪些文件，是不是有资源泄露，也就是说进程打开的这些文件本应该被关闭，但由于程序的Bug而没有被关闭。

如果没有资源泄露，可以通过设置增加最大文件句柄数。具体方法是通过 `ulimit -a` 来查看系统目前资源限制，通过 `ulimit -n 10240` 修改最大文件数。

## Tomcat网络参数

接下来我们看看Tomcat两个比较关键的参数：maxConnections和acceptCount。在解释这个参数之前，先简单回顾下TCP连接的建立过程：客户端向服务端发送SYN包，服务端回复SYN＋ACK，同时将这个处于SYN\_RECV状态的连接保存到 **半连接队列**。客户端返回ACK包完成三次握手，服务端将ESTABLISHED状态的连接移入 **accept队列**，等待应用程序（Tomcat）调用accept方法将连接取走。这里涉及两个队列：

- **半连接队列**：保存SYN\_RECV状态的连接。队列长度由 `net.ipv4.tcp_max_syn_backlog` 设置。
- **accept队列**：保存ESTABLISHED状态的连接。队列长度为 `min(net.core.somaxconn，backlog)`。其中backlog是我们创建ServerSocket时指定的参数，最终会传递给listen方法：

```
int listen(int sockfd, int backlog);

```

如果我们设置的backlog大于 `net.core.somaxconn`，accept队列的长度将被设置为 `net.core.somaxconn`，而这个backlog参数就是Tomcat中的 **acceptCount** 参数，默认值是100，但请注意 `net.core.somaxconn` 的默认值是128。你可以想象在高并发情况下当Tomcat来不及处理新的连接时，这些连接都被堆积在accept队列中，而 **acceptCount** 参数可以控制accept队列的长度，超过这个长度时，内核会向客户端发送RST，这样客户端会触发上文提到的“Connection reset”异常。

而Tomcat中的 **maxConnections** 是指Tomcat在任意时刻接收和处理的最大连接数。当Tomcat接收的连接数达到maxConnections时，Acceptor线程不会再从accept队列中取走连接，这时accept队列中的连接会越积越多。

maxConnections的默认值与连接器类型有关：NIO的默认值是10000，APR默认是8192。

所以你会发现Tomcat的最大并发连接数等于 **maxConnections + acceptCount**。如果acceptCount设置得过大，请求等待时间会比较长；如果acceptCount设置过小，高并发情况下，客户端会立即触发Connection reset异常。

## Tomcat网络调优实战

接下来我们通过一个直观的例子来加深对上面两个参数的理解。我们先重现流量高峰时accept队列堆积的情况，这样会导致客户端触发“Connection reset”异常，然后通过调整参数解决这个问题。主要步骤有：

1.下载和安装压测工具 [JMeter](http://jmeter.apache.org/download_jmeter.cgi)。解压后打开，我们需要创建一个测试计划、一个线程组、一个请求和，如下图所示。

**测试计划**：

![](https://static001.geekbang.org/resource/image/a6/4d/a6ad806b55cab54098f2b179c2cf874d.png?wh=1920*476)

**线程组**（线程数这里设置为1000，模拟大流量）：

![](https://static001.geekbang.org/resource/image/59/3a/590569c1b516d10af6e6ca9ee99f6a3a.png?wh=1920*713)

**请求**（请求的路径是Tomcat自带的例子程序）：

![](https://static001.geekbang.org/resource/image/9e/3b/9efa851e885448e457b4883c8927ac3b.png?wh=1920*508)

2.启动Tomcat。

3.开启JMeter测试，在View Results Tree中会看到大量失败的请求，请求的响应里有“Connection reset”异常，也就是前面提到的，当accept队列溢出时，服务端的内核发送了RST给客户端，使得客户端抛出了这个异常。

![](https://static001.geekbang.org/resource/image/26/9c/267b3808cdc2673418f9b3ac44a59b9c.png?wh=1506*1118)

4.修改内核参数，在 `/etc/sysctl.conf` 中增加一行 `net.core.somaxconn=2048`，然后执行命令 `sysctl -p`。

5.修改Tomcat参数acceptCount为2048，重启Tomcat。

![](https://static001.geekbang.org/resource/image/d1/0b/d12ea2188bddf803b62613fd59d8af0b.png?wh=1620*174)

6.再次启动JMeter测试，这一次所有的请求会成功，也看不到异常了。我们可以通过下面的命令看到系统中ESTABLISHED的连接数增大了，这是因为我们加大了accept队列的长度。

![](https://static001.geekbang.org/resource/image/c6/e6/c6f610d4311c433a149ea9d3d4b5ade6.png?wh=1484*456)

## 本期精华

在Socket网络通信过程中，我们不可避免地会碰到各种Java异常，了解这些异常产生的原因非常关键，通过这些信息我们大概知道问题出在哪里，如果一时找不到问题代码，我们还可以通过网络抓包工具来分析数据包。

在这个基础上，我们还分析了Tomcat中两个比较重要的参数：acceptCount和maxConnections。acceptCount用来控制内核的TCP连接队列长度，maxConnections用于控制Tomcat层面的最大连接数。在实战环节，我们通过调整acceptCount和相关的内核参数 `somaxconn`，增加了系统的并发度。

## 课后思考

在上面的实验中，我们通过 `netstat` 命令发现有大量的TCP连接处在TIME\_WAIT状态，请问这是为什么？它可能会带来什么样的问题呢？

不知道今天的内容你消化得如何？如果还有疑问，请大胆的在留言区提问，也欢迎你把你的课后思考和心得记录下来，与我和其他同学一起讨论。如果你觉得今天有所收获，欢迎你把它分享给你的朋友。