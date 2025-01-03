你好，我是文强。

这节课我们来看一下如何在消息队列内核中支持 WebSocket。如果你以前了解过 WebSocket，就知道 WebSocket 是一个协议。我们在 [第03讲](https://time.geekbang.org/column/article/670596) 中讲过，消息队列在自身私有协议的基础上，还会支持像HTTP这样的公有协议。

那为什么需要支持WebSocket协议呢？又是如何支持的？带着这两个问题，我们开始今天的课程。

## WebSocket 是什么

首先，我们来了解一下 WebSocket 是什么。

WebSocket 是一种基于 TCP 传输协议的应用层协议，它设计的初衷是解决Web应用程序中的实时双向通信问题。它跟 HTTP 协议一样，也是一种标准的公有协议。所以它也有协议头、协议体、数据帧格式、建立连接、维持连接、数据交换等等各个细节。

这里网上的资料有很多，就不展开细讲了。你只要记住一个重点： **WebSocket 是一个可以在浏览器中使用的支持双向通信的应用层协议**，就可以了。

那什么是双向通信呢？

### 双工（双向）通信

回答这个问题之前，我们来回顾一下计算机网络基础中的单工通信和双通通信。

1. **单工通信** 指的是数据只能在一个方向上传输，而不能在另一个方向上传输。例如，广播电台只能向接收者发送信息，接收者无法向电台发送信息，这是单工通信的一种。
2. **双工通信** 指的是数据可以在两个方向上传输。例如，电话通信就是双工通信的一种，通话双方可以同时说话和倾听对方的声音。

如下图所示，在计算机网络中，HTTP是一种单向通信协议，即浏览器请求服务器上的信息并从服务器接收响应，但服务器不能主动向浏览器发送信息。而TCP/IP协议则是一种双向通信协议，数据可以在客户端和服务器之间相互传输，即客户端可以发数据给服务端，服务端也可以发数据给客户端。

![](https://static001.geekbang.org/resource/image/14/8f/14e013b76f154df04a99c8dc3130298f.jpg?wh=10666x3392)

接下来，我们来了解一下 WebSocket 的协议特点和主要的应用场景。

### 特点和应用场景

从某种角度讲，WebSocket 协议可以理解为 HTTP 协议的升级版本，它主要有这样五个特点。

1. **持久化连接**：WebSocket 建立了一个持久化的 TCP 和 TLS 连接，从而减少了握手过程中的延迟并提高性能。
2. **全双工通信**：WebSocket 允许客户端和服务器在同一时刻发送和接收消息，实现了全双工通信。
3. **低带宽开销**：WebSocket 在数据分帧处理方面采用了紧凑的二进制格式，并对附加元数据进行了优化，以实现低带宽开销。
4. **与** **HTTP** **兼容**：WebSocket 协议兼容 HTTP 协议，使用与 HTTP 相同的默认端口（80 和 443），能够通过现有的网络基础设施进行传输，并得到大多数现代浏览器的支持。
5. **跨域通信**：WebSocket 协议允许跨域通信（在配置允许的情况下），使得客户端可以与不同域名上的服务器建立连接。

因为协议具备这些特点，在需要高度实时性和低延迟的场景中，WebSocket 是一种理想的解决方案。所以 WebSocket 在 Web 即时通讯、在线游戏、实时股票和金融信息流、物联网通信和在线协作工具等场景中会被大量使用。

为了让你对 WebSocket 有一个更直观的理解，我们来看一个 WebSocket 客户端代码示例。

### 客户端使用示例

下面是一个用 JavaScript 写的 WebSocket 客户端发送数据的代码示例，包括初始化连接、发送数据、发送成功和失败处理、关闭连接等操作。

```plain
// 初始化连接
let socket = new WebSocket("wss://javascript.info/article/websocket/demo/hello");

// 发送数据
socket.onopen = function(e) {
  socket.send("My name is John");
};

// 发送成功
socket.onmessage = function(event) {
  alert(`[message] Data received from server: ${event.data}`);
};

//关闭连接
socket.onclose = function(event) {
    alert('close Connection');

};

// 返回错误
socket.onerror = function(error) {
  alert(`[error] ${error.message}`);
};

```

这个示例比较简单，就不细讲了。接下来我们来了解一下WebSocket 协议和消息队列的关系，来回答一下“为什么消息队列需要支持 WebSocket 协议”。

## WebSocket 协议和消息队列

从应用场景来看，消息队列需要的是 WebSocket 协议支持的双工通信的特性。

我们在 [第08讲](https://time.geekbang.org/column/article/673672) 讲消费模型的时候讲过，Push 模型可以实现当服务端有数据时主动将数据推送给消费者，从而降低消费延时。而客户端要接收数据，一般要启动端口。

从技术上看，消费者其实就是一个Server，而在客户端维护这个Server是有成本的。

![](https://static001.geekbang.org/resource/image/4a/99/4a898532502ff7a2605be9680f920799.jpg?wh=10666x4147)

如果引入 WebSocket 协议，消费者通过 WebSocket 协议和 Broker 建立连接。因为WebSocket 协议是双向通信的，所以 Broker 就可以直接将数据推送给消费者，而不需要在客户端实现一个Server。因此开发工作量就降低特别多。

![](https://static001.geekbang.org/resource/image/d3/3a/d32b659c52e23b7772eb4f6be5be8d3a.jpg?wh=10666x6000)

所以说， **长连接和双向通信是 WebSocket 实现高度实时性和低延迟的技术核心**，也是消息队列需要支持WebSocket协议的重要原因。

接下来，我们用 WebSocket 和 MQTT Broker 结合的一个案例，让你更直观感受一下它们组合起来使用的优势。

![](https://static001.geekbang.org/resource/image/6c/60/6cf2082d6cc3406368a1266dfde49060.jpg?wh=10666x3728)

参考图示，这里想要展现的的场景是：物联网传感器（例如气体传感器）收集数据后，将数据通过 MQTT 协议发送到 MQTT Broker。收到数据的同时，Broker 可以通过 WebSocket 将数据推送到浏览器或客户端，从而及时更新监控面板或者触发告警。

因为 MQTT 和 WebSocket 都是双向通信的，我们也可以在浏览器中通过 WebSocket 协议将消息发送到 MQTT Broker，然后 MQTT Broker 再将消息发送给 IoT 终端。

在上面的场景中，核心就是双向通信提升了消息传递的及时性。当你把 MQTT Broker 换作其他的消息队列，就可以应用在类似的场景中。

我们知道，支持多协议一般有内核支持和Proxy模式两种形态。因为实现方式基本差不多，下面我们就重点看一下如何在消息队列的内核中支持WebSocket协议。

## 内核中支持 WebSocket 协议

从技术拆解来看，在内核中支持 WebSocket 协议，主要分为以下四部分工作：

1. 确定在 WebSocket 上支持哪些功能，比如生产、消费。
2. 设计生产、消费等功能的请求和返回协议。
3. 在内核中支持 WebSocket Server。
4. Broker 通过 WebSocket 协议推送数据。

### 支持功能

从实际业务场景来看，WebSocket 主要用在消息队列的数据流上。因为消息队列数据流的操作主要是生产和消费，所以在 WebSocket 协议上主要也是支持生产、消费等操作。

接下来我们看一下 WebSocket 协议的生产和消费如何设计。

### 生产消费协议设计

从技术上看，WebSocket 兼容HTTP。可以简单理解成，WebSocket是基于HTTP的。所以从使用的角度，如下所示，WebSocket 协议包含 URI 和 Body 两个部分。

```plain

URI: wss://javascript.info/article/websocket/demo/hello

Body: { "payload": "SGVsbG8gV29ybGQ=" }

```

URI 表示 WebSocket Server 的地址，Body 是请求内容，可以发现跟 HTTP 协议很像。所以，生产、消费协议跟设计普通的HTTP API区别不大，就是定义URI、定义访问参数和返回参数。请求 Body 一般也是使用 JSON 格式来传递。

接下来，我们来看一下生产请求的协议设计，示例如下：

```plain
URI:
    wss://mqserver.com/send/ns1/tp1
body：
{
  "key"："k1"，
  "value": "v1",
  "properties":"{"p1":1,"p2":2}"
}

```

在上面的示例中，/send/ns1/tp1 表示发送数据到租户ns1中的 Topic tp1，body 是JSON格式的数据，包含 key、value、properties 三个字段，分别表示消息的key、消息的value、消息的属性。

接下来看一下返回值，示例如下：

```plain
// 请求成功
{
   "result": "ok",
   "messageID": "CAAQAw=="
 }

// 请求失败
 {
   "result": "send-error:3",
   "errorMsg": "Failed to de-serialize from JSON"
 }

```

这个返回值就是一个普通的JSON格式的返回值。result表示请求结果，messageID 表示这条消息的ID，errorMsg 表示错误信息。

协议设计整体看下来，其实就是普通的 HTTP API 的设计，没有太多的新东西。 其他的比如消费、位点提交等接口，设计思路是类似的，就不展开了。

设计好了协议，我们来看一下如何在内核中支持WebSocket Server。

### 支持 WebSocket Server

从技术上来看，在内核中支持 WebSocket Server 并不复杂，因为各个语言都有对应的库来实现。

下面我们通过 Netty 来实现一个WebSocket Server，举例说明一下如何在Broker内支持WebSocket，代码示例如下：

```plain
public static void StartWebServer() throws InterruptedException {
    EventLoopGroup bossGroup = new NioEventLoopGroup();
    EventLoopGroup workerGroup = new NioEventLoopGroup();
    try {
        ServerBootstrap b = new ServerBootstrap();
        b.group(bossGroup, workerGroup)
                .channel(NioServerSocketChannel.class)
                .childHandler(new ChannelInitializer<SocketChannel>() {
                    @Override
                    public void initChannel(SocketChannel ch) throws Exception {
                        ChannelPipeline pipeline = ch.pipeline();
                        pipeline.addLast(new HttpServerCodec()); // HTTP 协议解析，用于握手阶段
                        pipeline.addLast(new HttpObjectAggregator(65536)); // HTTP 协议解析，用于握手阶段
                        pipeline.addLast(new WebSocketServerCompressionHandler()); // WebSocket 数据压缩扩展
3
                    }
                });
        ChannelFuture f = b.bind(80).sync();
        f.channel().closeFuture().sync();
    } finally {
        workerGroup.shutdownGracefully();
        bossGroup.shutdownGracefully();
    }
}

class MyWebSocketServerHandler extends SimpleChannelInboundHandler<WebSocketFrame> {
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, WebSocketFrame frame) throws Exception {
        if (frame instanceof TextWebSocketFrame) {
            String request = ((TextWebSocketFrame) frame).text();
            ctx.channel().writeAndFlush(new TextWebSocketFrame("receive: " + request));
        }
    }
}

```

在上面的代码中，主要需要关注的是 pipeline.addLast 和 writeAndFlush 两部分代码。addLast 主要用来做协议相关的解析，writeAndFlush 是给客户端返回数据的，它是双工通信的重要环节。只要往 Channel 回写数据，此时客户端就可以收到数据，从而实现主动推送消息给客户端。

因为数据推送给客户端是 WebSocket 的一个重要功能，所以我们接下来讲一下 Broker 如何基于 WebSocket 协议实现主动消息推送。

### 主动消息推送

先来看一下下面这张图，这是一个消息主动推送的场景。

![](https://static001.geekbang.org/resource/image/c3/9b/c3e433aa7b67f96059f49f6b1724759b.jpg?wh=10666x3621)

参考图示，当数据写入到Broker中的Topic tp1 时，因为WebSocket是双向通信的，所以 Broker 收到消息后，可以直接将消息推送给客户端。这个推送的逻辑一般是在内核中维护异步线程去回写数据到客户端实现的。你可以去回看 [第08讲](https://time.geekbang.org/column/article/673672) 的内容，回顾一下Push模型的实现，结合起来看，理解会更深入一点。

目前业界主流消息队列只有 Pulsar 和 RabbitMQ 支持了 WebSocket 协议。从技术上看，两者的实现思路基本一致。所以接下来我们就挑 Puslar 来分析一下它是如何支持 WebSocket 协议的。

## Pulsar 如何支持 WebSocket 协议

如下图所示，Pulsar 内核支持两种 WebSocket 部署形式。一种是在内核中启动，一种是作为单独组件部署。从代码实现来看，两者的区别不大，对于 WebSocket Server 的支持是同一份代码，只是启动的地方不一样而已。

![](https://static001.geekbang.org/resource/image/65/f9/65de0ac91d2f074628efa0044dcbc8f9.jpg?wh=10666x3679)

从代码实现上看，Pulsar 是基于 Jetty 的 WebSocket 包来实现 WebSocket Server的，属于很标准的用法。有兴趣的同学可以参考 [GitHub 的仓库源码](https://github.com/apache/pulsar/tree/master/pulsar-websocket)。

Pulsar 支持 **生产**、 **消费**、 **读取消费位点** 3 个功能。下面我们简单看一下生产操作的请求URI、Body、返回值。

```plain
// 请求URI
ws://broker-service-url:8080/ws/v2/producer/persistent/:tenant/:namespace/:topic

// 请求体Body
{
  "payload": "SGVsbG8gV29ybGQ=",
  "properties": {"key1": "value1", "key2": "value2"}
}

// 处理成功的返回值：
{
   "result": "ok",
   "messageID": "CAAQAw==",
   "context": "1"
 }
// 处理失败的返回值
 {
   "result": "send-error:3",
   "errorMsg": "Failed to de-serialize from JSON",
   "context": "1"
 }

```

可以看到在 URI 的定义上，Pulsar 定义了 **请求的版本** **、** **生产接口**、 **租户**、 **命名空间**、 **Topic** 等信息，用来标识数据发给谁。请求体里面的 payload、properties分别表示消息内容和消息属性。

返回值里面则包含了result、messageID、errorMsg、context等信息，分别表示请求返回结果、消息ID、错误信息和上下文信息。

当然生产的参数和返回值不止这几个，想了解更多你可以参考 [官方文档](https://pulsar.apache.org/docs/3.1.x/client-libraries-websocket/)。同样的，消费和读取消费位点的接口定义也可以参考这个官方文档。

我们最后来看一下 Python 客户端的代码示例。

```plain
import websocket, base64, json

# If set enableTLS to true, your have to set tlsEnabled to true in conf/websocket.conf.
enable_TLS = False
scheme = 'ws'
if enable_TLS:
    scheme = 'wss'

TOPIC = scheme + '://localhost:8080/ws/v2/producer/persistent/public/default/my-topic'

ws = websocket.create_connection(TOPIC)

# encode message
s = "Hello World"
firstEncoded = s.encode("UTF-8")
binaryEncoded = base64.b64encode(firstEncoded)
payloadString = binaryEncoded.decode('UTF-8')

# Send one message as JSON
ws.send(json.dumps({
    'payload' : payloadString,
    'properties': {
        'key1' : 'value1',
        'key2' : 'value2'
    },
    'context' : 5
}))

response =  json.loads(ws.recv())
if response['result'] == 'ok':
    print( 'Message published successfully')
else:
    print('Failed to publish message:', response)
ws.close()

```

客户端的代码逻辑很清晰，分为构建URI、初始化连接、组装参数、发送生产请求、处理返回、关闭连接六个流程。

因此，可以看出 Pulsar 对 WebSocket 的支持也不复杂，主要是协议的兼容和适配。

## 总结

WebSocket 是一种实时协议，它在单个 TCP 连接上提供持久的全双工通信，即双向通信。双向通信非常适合需要实时更新的系统，简单说就是允许服务端主动推送数据给客户端的场景。比如金融行情、实时多人游戏、聊天应用程序和实时地理位置更新等等。

消息队列支持 WebSocket 协议的核心诉求就是WebSocket的双向通信的特性。因为基于这个特性，Broker可以很方便地将数据推送给各个客户端，从而提高数据传递的及时性。

消息队列支持 WebSocket 协议主要有内核支持和Proxy模式两种形态。从实现机制上看，这两种方案差别不大。主要就是确定需要支持的功能点、各个功能点的协议设计、内核支持WebSocket Server、实现主动推送逻辑四个部分。

从业界来看，支持 WebSocket 协议的消息队列并不多。虽然 WebSocket 结合消息队列有一定的使用场景，但是用户也可以自定义实现一个 WebSocket Server，然后消费消息队列的数据，再将数据推送到客户端，实现类似的功能，并且整体开发成本并不高。所以严格来讲，WebSocket 协议不是消息队列的核心功能，但因为有场景需求，所以我们还是花了一节课的时间来梳理它，希望能完善你的知识体系。

## 思考题

为什么在讲生产消费协议时我们说“简单理解成 WebSocket 是基于HTTP的”，请你从 WebSocket 建立连接、数据交互的角度来尝试回答一下这个问题。

提示：可以去对比一下 WebSocket 协议和 HTTP 协议建立连接、数据交互的过程。

欢迎分享你的思考，如果觉得有收获，也欢迎你把这节课分享给身边的朋友。我们下节课再见！

## 上节课思考闭环

1\. 既然Schema Register都是独立部署的，业界的RocketMQ、Kafka、Pulsar 都分别实现了独立的Schema Register，那么实现一个统一通用的Schema Register有意义吗？有什么好处或者难点？

从功能和需求的角度来看，是一定有意义的。有一个通用的Schema Register可以减少重复开发的工作量，统一标准，降低用户的部署、运维、学习成本。因为本质上Schema Register的功能是比较固定的，都是持久化存储，并提供管理Schema信息的接口。

但是难点在于，不同的消息队列的Schema 需求有一定的差异，目前还没有形成一个统一的标准。此时需要协调各个社区的工作，沟通工作量比较大，推进困难。这也是各个社区各自推进的原因。

就跟我们在 [第03讲](https://time.geekbang.org/column/article/670596) 讲到的一样，大家有统一的诉求，但是实际落地就会遇到需求不一致、统一标准的制定周期长、沟通成本高、不够灵活等问题。

2\. Pulsar 的社区版本也支持Schema特性，Kakfa 的商业化公司Confluent的商业化版本Kafka也支持了Schema，请你去官网学习一下它们的实现，然后对比一下这节课的所学。

Pulsar Schema 官网文档地址： [https://pulsar.apache.org/docs/3.0.x/schema-overview/](https://pulsar.apache.org/docs/3.0.x/schema-overview/%5Breference_end%5D)

Kafka Schema 官网文档地址： [https://www.confluent.io/blog/how-i-learned-to-stop-worrying-and-love-the-schema-part-1/](https://www.confluent.io/blog/how-i-learned-to-stop-worrying-and-love-the-schema-part-1/%5Breference_end%5D)