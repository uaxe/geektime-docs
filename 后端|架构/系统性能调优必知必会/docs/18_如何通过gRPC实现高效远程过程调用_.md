你好，我是陶辉。

这一讲我们将以一个实战案例，基于前两讲提到的HTTP/2和ProtoBuf协议，看看gRPC如何将结构化消息编码为网络报文。

直接操作网络协议编程，容易让业务开发过程陷入复杂的网络处理细节。RPC框架以编程语言中的本地函数调用形式，向应用开发者提供网络访问能力，这既封装了消息的编解码，也通过线程模型封装了多路复用，对业务开发很友好。

其中，Google推出的gRPC是性能最好的RPC框架之一，它支持Java、JavaScript、Python、GoLang、C++、Object-C、Android、Ruby等多种编程语言，还支持安全验证等特性，得到了广泛的应用，比如微服务中的Envoy、分布式机器学习中的TensorFlow，甚至华为去年推出重构互联网的New IP技术，都使用了gRPC框架。

然而，网络上教你使用gRPC框架的教程很多，却很少去谈gRPC是如何编码消息的。这样，一旦在大型分布式系统中出现疑难杂症，需要通过网络报文去定位问题发生在哪个系统、主机、进程中时，你就会毫无头绪。即使我们掌握了HTTP/2和Protobuf协议，但若不清楚gRPC的编码规则，还是无法分析抓取到的gRPC报文。而且，gRPC支持单向、双向的流式RPC调用，编程相对复杂一些，定位流式RPC调用引发的bug时，更需要我们掌握gRPC的编码原理。

这一讲，我就将以gRPC官方提供的example： [data\_transmisstion](https://github.com/grpc/grpc/tree/master/examples/python/data_transmission) 为例，介绍gRPC的编码流程。在这一过程中，会顺带回顾HTTP/2和Protobuf协议，加深你对它们的理解。虽然这个示例使用的是Python语言，但基于gRPC框架，你可以轻松地将它们转换为其他编程语言。

## 如何使用gRPC框架实现远程调用？

我们先来简单地看下gRPC框架到底是什么。RPC的全称是Remote Procedure Call，即远程过程调用，它通过本地函数调用，封装了跨网络、跨平台、跨语言的服务访问，大大简化了应用层编程。其中，函数的入参是请求，而函数的返回值则是响应。

gRPC就是一种RPC框架，在你定义好消息格式后，针对你选择的编程语言，gRPC为客户端生成发起RPC请求的Stub类，以及为服务器生成处理RPC请求的Service类（服务器只需要继承、实现类中处理请求的函数即可）。如下图所示，很明显，gRPC主要服务于面向对象的编程语言。

![](https://static001.geekbang.org/resource/image/c2/a1/c20e6974a05b5e71823aec618fc824a1.jpg?wh=1682*1182)

gRPC支持QUIC、HTTP/1等多种协议，但鉴于HTTP/2协议性能好，应用场景又广泛，因此HTTP/2是gRPC的默认传输协议。gRPC也支持JSON编码格式，但在忽略编码细节的RPC调用中，高效的Protobuf才是最佳选择！因此，这一讲仅基于HTTP/2和Protobuf，介绍gRPC的用法。

gRPC可以简单地分为三层，包括底层的数据传输层，中间的框架层（框架层又包括C语言实现的核心功能，以及上层的编程语言框架），以及最上层由框架层自动生成的Stub和Service类，如下图所示：

[![](https://static001.geekbang.org/resource/image/2a/4a/2a3f82f3eaabd440bf1ee449e532944a.png?wh=1380*557)](https://platformlab.stanford.edu/Seminar%20Talks/gRPC.pdf)

接下来我们以官网上的 [data\_transmisstion](https://github.com/grpc/grpc/tree/master/examples/python/data_transmission) 为例，先看看如何使用gRPC。

构建Python语言的gRPC环境很简单，你可以参考官网上的 [QuickStart](https://grpc.io/docs/quickstart/python/)。

使用gRPC前，先要根据Protobuf语法，编写定义消息格式的proto文件。在这个例子中只有1种请求和1种响应，且它们很相似，各含有1个整型数字和1个字符串，如下所示：

```
package demo;

message Request {
    int64 client_id = 1;
    string request_data = 2;
}

message Response {
    int64 server_id = 1;
    string response_data = 2;
}

```

请注意，这里的包名demo以及字段序号1、2，都与后续的gRPC报文分析相关。

接着定义service，所有的RPC方法都要放置在service中，这里将它取名为GRPCDemo。GRPCDemo中有4个方法，后面3个流式访问的例子我们呆会再谈，先来看简单的一元访问模式SimpleMethod 方法，它定义了1个请求对应1个响应的访问形式。其中，SimpleMethod的参数Request是请求，返回值Response是响应。注意，分析报文时会用到这里的类名GRPCDemo以及方法名SimpleMethod。

```
service GRPCDemo {
    rpc SimpleMethod (Request) returns (Response);
}

```

用grpc\_tools中的protoc命令，就可以针对刚刚定义的service，生成含有GRPCDemoStub类和GRPCDemoServicer类的demo\_pb2\_grpc.py文件（实际上还包括完成Protobuf编解码的demo\_pb2.py），应用层将使用这两个类完成RPC访问。我简化了官网上的Python客户端代码，如下所示：

```
with grpc.insecure_channel("localhost:23333") as channel:
    stub = demo_pb2_grpc.GRPCDemoStub(channel)
    request = demo_pb2.Request(client_id=1,
            request_data="called by Python client")
    response = stub.SimpleMethod(request)

```

示例中客户端与服务器都在同一台机器上，通过23333端口访问。客户端通过Stub对象的SimpleMethod方法完成了RPC访问。而服务器端的实现也很简单，只需要实现GRPCDemoServicer父类的SimpleMethod方法，返回response响应即可：

```
class DemoServer(demo_pb2_grpc.GRPCDemoServicer):
    def SimpleMethod(self, request, context):
        response = demo_pb2.Response(
            server_id=1,
            response_data="Python server SimpleMethod Ok!!!!")
        return response

```

可见，gRPC的开发效率非常高！接下来我们分析这次RPC调用中，消息是怎样编码的。

## gRPC消息是如何编码的？

**定位复杂的网络问题，都需要抓取、分析网络报文。** 如果你在Windows上抓取网络报文，可以使用Wireshark工具（可参考 [《Web协议详解与抓包实战》第37课](https://time.geekbang.org/course/detail/175-100973)），如果在Linux上抓包可以使用tcpdump工具（可参考 [第87课](https://time.geekbang.org/course/detail/175-118169)）。当然，你也可以从 [这里](https://github.com/russelltao/geektime_distrib_perf/blob/master/18-gRPC/data_transmission.pkt) 下载我抓取好的网络报文，用Wireshark打开它。需要注意，23333不是HTTP常用的80或者443端口，所以Wireshark默认不会把它解析为HTTP/2协议。你需要鼠标右键点击报文，选择“解码为”（Decode as），将23333端口的报文设置为HTTP/2解码器，如下图所示：

![](https://static001.geekbang.org/resource/image/74/f7/743e5038dc22676a0d48b56c453c1af7.png?wh=1241*425)

图中蓝色方框中，TCP连接的建立过程请参见 [\[第9讲\]](https://time.geekbang.org/column/article/237612)，而HTTP/2会话的建立可参见 [《Web协议详解与抓包实战》第52课](https://time.geekbang.org/course/detail/175-105608)（还是比较简单的，如果你都清楚就可以直接略过）。我们重点看红色方框中的gRPC请求与响应，点开请求，可以看到下图中的信息：

![](https://static001.geekbang.org/resource/image/ba/41/ba4d9e9a6ce212e94a4ced829eeeca41.png?wh=906*844)

先来分析蓝色方框中的HTTP/2头部。请求中有2个关键的HTTP头部，path和content-type，它们决定了RPC方法和具体的消息编码格式。path的值为“/demo.GRPCDemo/SimpleMethod”，通过“/包名.服务名/方法名”的形式确定了RPC方法。content-type的值为“application/grpc”，确定消息编码使用Protobuf格式。如果你对其他头部的含义感兴趣，可以看下这个 [文档](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)，注意这里使用了ABNF元数据定义语言（如果你还不了解ABNF，可以看下 [《Web协议详解与抓包实战》第4课](https://time.geekbang.org/course/detail/175-93589)）。

HTTP/2包体并不会直接存放Protobuf消息，而是先要添加5个字节的Length-Prefixed Message头部，其中用4个字节明确Protobuf消息的长度（1个字节表示消息是否做过压缩），即上图中的桔色方框。为什么要多此一举呢？这是因为，gRPC支持流式消息，即在HTTP/2的1条Stream中，通过DATA帧发送多个gRPC消息，而Length-Prefixed Message就可以将不同的消息分离开。关于流式消息，我们在介绍完一元模式后，再加以分析。

最后分析Protobuf消息，这里仅以client\_id字段为例，对上一讲的内容做个回顾。在proto文件中client\_id字段的序号为1，因此首字节00001000中前5位表示序号为1的client\_id字段，后3位表示字段的值类型是varint格式的数字，因此随后的字节00000001表示字段值为1。序号为2的request\_data字段请你结合上一讲的内容，试着做一下解析，看看字符串“called by Python client”是怎样编码的。

再来看服务器发回的响应，点开Wireshark中的响应报文后如下图所示：

![](https://static001.geekbang.org/resource/image/b8/cf/b8e71a1b956286b2def457c2fae78bcf.png?wh=962*723)

其中DATA帧同样包括Length-Prefixed Message和Protobuf，与RPC请求如出一辙，这里就不再赘述了，我们重点看下HTTP/2头部。你可能留意到，响应头部被拆成了2个部分，其中grpc-status和grpc-message是在DATA帧后发送的，这样就允许服务器在发送完消息后再给出错误码。关于gRPC的官方错误码以及message描述信息是如何取值的，你可以参考 [这个文档。](https://github.com/grpc/grpc/blob/master/doc/statuscodes.md)

这种将部分HTTP头部放在包体后发送的技术叫做Trailer， [RFC7230文档](https://tools.ietf.org/html/rfc7230#page-39) 对此有详细的介绍。其中，RPC请求中的TE: trailers头部，就说明客户端支持Trailer头部。在RPC响应中，grpc-status头部都会放在最后发送，因此它的帧flags的EndStream标志位为1。

可以看到，gRPC中的HTTP头部与普通的HTTP请求完全一致，因此，它兼容当下互联网中各种七层负载均衡，这使得gRPC可以轻松地跨越公网使用。

## gRPC流模式的协议编码

说完一元模式，我们再来看流模式RPC调用的编码方式。

所谓流模式，是指RPC通讯的一方可以在1次RPC调用中，持续不断地发送消息，这对订阅、推送等场景很有用。流模式共有3种类型，包括客户端流模式、服务器端流模式，以及两端双向流模式。在 [data\_transmisstion](https://github.com/grpc/grpc/tree/master/examples/python/data_transmission) 官方示例中，对这3种流模式都定义了RPC方法，如下所示：

```
service GRPCDemo {
    rpc ClientStreamingMethod (stream Request) returns Response);

    rpc ServerStreamingMethod (Request) returns (stream Response);

    rpc BidirectionalStreamingMethod (stream Request) returns (stream Response);
}

```

不同的编程语言处理流模式的代码很不一样，这里就不一一列举了，但通讯层的流模式消息编码是一样的，而且很简单。这是因为，HTTP/2协议中每个Stream就是天然的1次RPC请求，每个RPC消息又已经通过Length-Prefixed Message头部确立了边界，这样，在Stream中连续地发送多个DATA帧，就可以实现流模式RPC。我画了一张示意图，你可以对照它理解抓取到的流模式报文。

![](https://static001.geekbang.org/resource/image/4b/e0/4b1b9301b5cbf0e0544e522c2a8133e0.jpg?wh=1538*1400)

## 小结

这一讲介绍了gRPC怎样使用HTTP/2和Protobuf协议编码消息。

在定义好消息格式，以及service类中的RPC方法后，gRPC框架可以为编程语言生成Stub和Service类，而类中的方法就封装了网络调用，其中方法的参数是请求，而方法的返回值则是响应。

发起RPC调用后，我们可以这么分析抓取到的网络报文。首先，分析应用层最外层的HTTP/2帧，根据Stream ID找出一次RPC调用。客户端HTTP头部的path字段指明了service和RPC方法名，而content-type则指明了消息的编码格式。服务器端的HTTP头部被分成2次发送，其中DATA帧发送完毕后，才会发送grpc-status头部，这样可以明确最终的错误码。

其次，分析包体时，可以通过Stream中Length-Prefixed Message头部，确认DATA帧中含有多少个消息，因此可以确定这是一元模式还是流式调用。在Length-Prefixed Message头部后，则是Protobuf消息，按照上一讲的内容进行分析即可。

## 思考题

最后，留给你一道练习题。gRPC默认并不会压缩字符串，你可以通过在获取channel对象时加入grpc.default\_compression\_algorithm参数的形式，要求gRPC压缩消息，此时Length-Prefixed Message中1个字节的压缩位将会由0变为1。你可以观察下执行压缩后的gRPC消息有何不同，欢迎你在留言区与大家一起探讨。

感谢阅读，如果你觉得这节课对你有一些启发，也欢迎把它分享给你的朋友。