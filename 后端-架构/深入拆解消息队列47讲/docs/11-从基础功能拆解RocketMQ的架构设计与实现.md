你好，我是文强。

上节课我们分析了RabbitMQ在通信协议、网络模块、存储模块、生产者、消费者这五个模块的设计思路。这节课我们用同一个思路来讲讲 RocketMQ。

有一个蛮有意思的现象，从我们的统计数据来看，RabbitMQ的用户数是最多的。但是在程序员的口碑中，RocketMQ无论是从性能还是稳定性上都是优于RabbitMQ的。从我个人来看，RocketMQ 可以当作RabbitMQ的替代品，因为RocketMQ在功能、稳定性、性能层面都比RabbitMQ的表现更好。所以我们一起来看看为什么吧。

## **RocketMQ 系统架构**

在正式讲解之前，我们先来看一下RocketMQ的架构图。

如下图所示，RocketMQ由 **Producer**、 **NameServer**、 **Broker**、 **Consumer** 四大模块组成。其中，NameServer是RocketMQ的元数据存储组件。另外，在RocketMQ 5.0后，还增加了Proxy模块，用来支持gRPC协议，并为后续的计算存储分离架构做准备。

![](https://static001.geekbang.org/resource/image/6a/38/6af4ab5debc9535849ab7da3e5022f38.jpg?wh=10666x4161)

RocketMQ有Topic、MessageQueue、Group的概念，一个Topic可以包含一个或多个MessageQueue，一个Group 可以订阅一个或多个Topic。MessageQueue是具体消息数据的存储单元，订阅的时候通过Group来管理消费订阅关系。

从流程上看，Broker 在启动的时候会先连接NameServer，将各自的元数据信息上报给NameServer，NameServer会在内存中存储元数据信息。客户端在连接集群的时候，会配置对应的 NameServer 地址，通过连接NameServer来实现客户端寻址，从而连接上对应的Broker。

客户端在发送数据的时候，会指定Topic或MessageQueue。Broker收到数据后，将数据存储到对应的Topic中，消息存储在Topic的不同Queue中。在底层的文件存储中，所有Queue的数据是存储在同一个CommitLog文件中的。在订阅的时候会先创建对应的Group，消费消息后，再确认数据。

从客户端来看，在RocketMQ 5.0以后，我们也可以通过直连Proxy，将数据通过gRPC协议发送给Proxy。Proxy在当前阶段本质上只是一个代理（gRPC协议的代理），不负责真正的数据存储，当收到数据后，还是将数据转发到Broker进行保存。

好了，学习完RocketMQ的基本概念和架构，我们继续围绕上述的五个模块来分析一下RocketMQ，先来看一下协议和网络模块。

## 协议和网络模块

在协议方面，如下图所示，RocketMQ 5.0 之前支持自定义的Remoting协议，在5.0之后，增加了gRPC协议的支持。

这是在Proxy组件上完成了对gRPC协议的支持，用的是 [第03讲](https://time.geekbang.org/column/article/670596) 的代理（Proxy）模式。即Broker依旧只支持Remoting协议，如果需要支持gRPC协议，那么就需要单独部署Proxy组件。

![](https://static001.geekbang.org/resource/image/b1/c9/b1b45ffe1bf5e2870e53124815440dc9.jpg?wh=10666x4063)

在传输层协议方面，Remoting和gRPC都是基于TCP协议传输的。Remoting 直接基于四层的TCP协议通信，gRPC是基于七层的HTTP2协议通信，不过 HTTP2 底层也是基于TCP，它们本质上都是应用层的协议。

讲到这，不知道你是否会想： **Remoting** **不够用吗** **？** **为什么还需要** **gRPC** **呢？**

在我看来，Remoting 从功能、性能、灵活性来看没有太大的问题。它的主要缺点是私有协议客户端的重复开发成本，以及与第三方服务集成的不便捷。因为是私有协议，所以Remoting在多语言SDK开发时，基础网络模块的工作（如连接管理、网络模型设计、心跳管理等）都需要重新开发，工作量很高。另外，生态连接在 RocketMQ 是一个很重要的工作，gRPC作为公有协议，有很多天然的生态集成能力，比如Service Mesh、Kubernetes生态等等。

关于Remoting协议的细节，我们在 [第03讲](https://time.geekbang.org/column/article/670596) 介绍协议时已经详细讲述了，这里不再重复。下面我们来聊一下gRPC协议，先来看一下gRPC的架构图。

![图片](https://static001.geekbang.org/resource/image/b9/a3/b961c1a2a899610d7c0e0b5f24dcd0a3.png?wh=800x480)

如上图所示，gRPC 分为Client端和Server端，底层基于HTTP2通信，内置了编解码模块，也定义好了Client和Server之间的调用方式，同时支持TLS加密，是一个完整的RPC框架。所以我们可以看到它在底层已经实现了网络通信、协议的设计、编解码框架等所有基础的工作。从使用的角度来说，gRPC 提供了各个语言的开发库，只需要集成对应语言的开发库，即可完成网络模块的开发，很轻便。详情情况你可以参考 [gRPC 各语言官方文档](https://grpc.io/docs/languages/)。

因为我们在 [第04讲](https://time.geekbang.org/column/article/670965) 就分析了RocketMQ网络模块的详细实现，这里就不重复讲了。接下来我们看一下RocketMQ的存储层。

## 数据存储

RocketMQ 同 RabbitMQ 一样，数据存储模块也分为元数据存储和消息数据存储两部分。

### 元数据存储

先来看一下元数据存储。RocketMQ 的元数据信息实际是存储在Broker上的，Broker启动时将数据上报到NameServer模块中汇总缓存。NameServer是一个简单的TCP Server，专门用来接收、存储、分发 Broker 上报的元数据信息。这些元数据信息是存储在NameServer内存中的，NameServer不会持久化去存储这些数据。

![](https://static001.geekbang.org/resource/image/27/53/278f259567c197cb42b8134880d0cb53.jpg?wh=10666x5489)

如上图所示，Broker 启动或删除时，会调用NameServer的注册和退出接口，每个Broker都会存储自己节点所属的元数据信息（比如有哪些Topic、哪些Queue 在本节点上），在Broker启动时，会把全量的数据上报到 NameServer 中。

从部署形态上看，NameServer 是多节点部署的，是一个集群。 但是不同节点之间是没有相互通信的，所以本质上多个NameServer节点间数据没有一致性的概念，是各自维护自己的数据，由每台Broker上报元数据来维护每台 NameServer 节点上数据的准确性。

由于NameServer不负责具体消息数据的存储和分发，所以在请求频率、负载方面都不会很高。所以在大多数场景下，NameServer都是可以多集群共享的。从功能上看，它对RocketMQ的作用相当于RabbitMQ的Mnesia。

讲完了元数据，我们再来看消息数据。

### 消息数据

RocketMQ 消息数据的最小存储单元是MessageQueue，也就是我们常说的Queue或Partition。Topic可以包含一个或多个MessageQueue，数据写入到Topic后，最终消息会分发到对应的MessageQueue中存储。

![](https://static001.geekbang.org/resource/image/0d/79/0dc590cca3709d82e04d3561e9223879.jpg?wh=10666x4366)

在底层的文件存储方面，并不是一个MessageQueue对应一个文件存储的，而是一个节点对应一个总的存储文件，单个Broker 节点下所有的队列共用一个日志数据文件（CommitLog）来存储，和RabbitMQ采用的是同一种存储结构。存储结构如下图所示：

![图片](https://static001.geekbang.org/resource/image/e5/69/e54d8fb1dffecbc91b978728b48a5369.png?wh=1142x763)

图中主要包含 CommitLog、ConsumeQueue、IndexFile 三个跟消息存储相关的文件，下面我们来简单了解一下。

- **CommitLog** 是消息主体以及元数据存储主体，每个节点只有一个，客户端写入到所有MessageQueue的数据，最终都会存储到这一个文件中。

- **ConsumeQueue** 是逻辑消费队列，是消息消费的索引，不存储具体的消息数据。引入的目的主要是提高消息消费的性能。由于RocketMQ是基于主题Topic的订阅模式，消息消费是针对主题进行的，如果要遍历Commitlog文件，基于Topic检索消息是非常低效的。Consumer可根据ConsumeQueue来查找待消费的消息，ConsumeQueue文件可以看成是基于Topic的CommitLog索引文件。

- **IndexFile** 是索引文件，它在文件系统中是以HashMap结构存储的。在RocketMQ中，通过Key或时间区间来查询消息的功能就是由它实现的。


值得关注的是，因为消息数据会很多，CommitLog 会存储所有的消息内容。所以为了保证数据的读写性能，我们会对CommitLog进行分段存储。CommitLog底层默认单个文件大小为1G，消息是顺序写入到文件中，当文件满了，就会写入下一个文件。对于 ConsumeQueue 和 IndexFile，则不需要分段存储，因为它们存储的是索引数据，数据量一般很小。

在消息清理方面，RocketMQ 支持按照时间清理数据。这个时间是按照消息的生产时间计算的，和消息是否被消费无关，只要时间到了，那么数据就会被删除。

不过跟RabbitMQ不同的是，RocketMQ 不是按照主题或队列维度来清理数据的，而是按照节点的维度来清理的。原因和RocketMQ 的存储模型有关，上面说到RocketMQ所有Queue的日志都存储在一个文件中，如果要支持主题和队列单独管理，需要进行数据的合并、索引的重建，实现难度相对复杂，所以RocketMQ并没有选择主题和队列这两个维度的清理逻辑。

好了，协议、网络、数据存储我们就都讲完了，接下来看一下RocketMQ客户端的生产者和消费者的实现。

## 生产者和消费者

RocketMQ的客户端连接服务端是需要经过客户端寻址的。如下图所示，首先和NameServer 完成寻址，拿到Topic/MessageQueue和Broker的对应关系后，接下来才会和Broker进行交互。

![](https://static001.geekbang.org/resource/image/c3/c8/c37175b6ba7ec1fc369f561e849b4fc8.jpg?wh=10666x6000)

### 生产端

生产端的基础模块（如连接管理、心跳检测、协议构建、序列化等工作），则会以协议和网络层的设计为准，使用不同编程语言 SDK 完成对应的开发。例如，在Java中，我们可以使用Netty 来构建客户端，进行TCP通信，根据Remoting协议构建请求数据，序列化后向服务端发起请求，或者直接使用 gRPC 框架的客户端进行通信。

从生产端来看，生产者是将数据发送到Topic或者Queue里面的。如果是发送到Topic，则数据要经历生产数据分区分配的过程。 **即决定消息要发送到哪个目标分区。**

默认情况下，RocketMQ支持轮询算法和最小投递延迟算法两种策略。默认是轮询算法，该算法保证了每个Queue中可以均匀地获取到消息。最小投递延迟算法会统计每次消息投递的时间延迟，然后根据统计出的结果将消息投递到时间延迟最小的Queue。如果是直接发送到Queue，则无需经过分区选择，直接发送即可。

由于RocketMQ在协议层不支持批量发送消息的协议，所以在SDK底层是没有等待、聚合发送逻辑的。所以如果需要批量发送数据，就需要在生产的时候进行聚合，然后发送。

为了满足不同的发送场景， **RocketMQ** **支持单向发送、同步发送、异步发送三种发送形式**。单向发送（Oneway）指发送消息后立即返回，不处理响应，不关心是否发送成功。同步发送（Sync）指发送消息后等待响应。异步发送（Async）指发送消息后立即返回，在提供的回调方法中处理响应。

### 消费端

在RocketMQ消费端，为了满足不同场景的消费需要，RocketMQ同时支持Pull、Push、Pop三种消费模型。

默认的消费模型是Pull，Pull的底层是以客户端会不断地去服务端拉取数据的形式实现的。Push 模型底层是以伪Push的方式实现的，即在客户端底层用一个Pull线程不断地去服务端拉取数据，拉到数据后，触发客户端设置的回调函数。让客户端从感受上看，是服务端直接将数据Push过来的。

另外，当消费者和分区都很多的时候，因为消费重平衡会消耗很长时间，且重平衡期间的消费会暂停。而在客户端也需要感知到复杂的重平衡行为，各个语言的客户端需要较高的重复开发成本。所以，RocketMQ 推出了Pop模式，将消费分区、分区分配关系、重平衡都移到了服务端， **减少了重平衡机制给客户端带来的复杂性。**

RocketMQ 默认是通过消费分组机制来消费的。即在客户端消费数据的时候，会通过消费分组来管理消费关系和存储消费进度。从实现上看，同一条消息支持被多个消费分组订阅，每个消费者分组可以有多个消费者。

由于Topic和Queue模型的存在，在启动消费的时候，就需要先分配消费者和分区消费关系。这个过程就是 RocketMQ 消费端负载均衡。在实现中，消息按照哪种逻辑分配给哪个消费者，就是由消费者负载均衡策略所决定的。

根据消费者类型的不同，消费者负载均衡策略分为消息粒度负载均衡和队列粒度负载均衡两种模式。这里简单了解下。

**消息粒度负载均衡** 是指同一消费者分组内的多个消费者，将按照消息粒度平均分摊主题中的所有消息。即同一个队列中的消息，会被平均分配给多个消费者共同消费。

![](https://static001.geekbang.org/resource/image/bb/59/bb949f7cde7e5c710b7232b9978f3759.jpg?wh=10666x4626)

**队列粒度负载均衡** 是指同一消费者分组内的多个消费者，将按照队列粒度消费消息，即每个队列仅被一个消费者消费。

![](https://static001.geekbang.org/resource/image/27/be/278ceayydfbe148a7c7767497b5ccdbe.jpg?wh=10666x6000)

消息粒度负载均衡就是我们之前在 [第08讲](https://time.geekbang.org/column/article/673672) 讲到的共享消费模式，而队列粒度负载均衡就是独占消费模式。大部分情况下，我推荐你优先使用队列粒度负载均衡。

当消费端消费数据成功后，就需要保存消费进度信息。RocketMQ通过提交消费位点信息来保存消费进度。在服务端，RocketMQ会为每个消费分组维护一份消费位点信息，信息中会保存消费的 **最大位点、最小位点、当前消费位点** 等内容。

![](https://static001.geekbang.org/resource/image/db/42/db391cae3483d129fe5fc1d31eb2d242.jpg?wh=10666x4259)

从实现来看，客户端消费完数据后，就会调用Broker的消费位点更新接口，提交当前消费的位点信息。

在服务端，消息被某个消费者消费完成后，不会立即在队列中被删除，以便当消费者客户端停止又再次重新上线时，会严格按照服务端保存的消费进度继续处理消息。如果服务端保存的历史位点信息已过期被删除，此时消费位点向前移动至服务端存储的最小位点。

讲完了生产者和消费者，接下来我们来看看RocketMQ对HTTP协议的支持和集群管控操作的实现。

## HTTP 协议支持和管控操作

RocketMQ原生不支持HTTP协议的生产消费，但是在一些云厂商的商业化版本是支持的。从技术上来看，HTTP协议的支持和gRPC的支持可以是一个技术思路，即通过使用Proxy模式来实现。

同样的，RocketMQ的管控也是不支持HTTP协议的操作的。RocketMQ的管控操作都是通过Remoting协议支持的，在gRPC协议中也不支持管控操作。即在Broker中，通过Remoting协议暴露不同的接口或者在NameServer中暴露TCP的接口，来实现一些对应的管控操作。

客户端 SDK 会集成调用服务端这些接口的逻辑。命令行工具就是通过客户端SDK来完成管控操作，也可以在代码中通过SDK来执行管控操作。

![](https://static001.geekbang.org/resource/image/93/5e/9353b611ea01ff5b0a91fd6e6d510d5e.jpg?wh=10666x3716)

## 总结

现在我们来总结一下RocketMQ。

1. 协议层支持Remoting和gRPC两种协议。
2. 网络层是基于Java NIO框架Netty开发，底层也是通过多路复用、异步IO、Reactor模型等技术来提高网络模块的性能。
3. 存储层是基于多个MessageQueue的数据统一存储到一个文件的思路来设计的，同时也支持分段存储和基于时间的数据过期机制。
4. 元数据存储是使用 Broker + 自定义的NameServer之间的配合来实现的。
5. 客户端的访问需要经过客户端寻址机制，拿到元数据信息后，才直连Broker。
6. 生产端是将数据写入到Topic或分区，写入Topic时需要经过生产分区分配操作，确认最终写入的MessageQueue也支持多种写入方式。
7. 消费端有消费分组的概念，也需要在多个消费者和消费分组之间进行消费的负载均衡，最后通过提交消费位点的形式来保存消费进度。

## 思考题

请你按照基础篇的思路，描述一下 RocketMQ 从生产到消费的全过程，越详细越好。

期待你的思考，如果觉得有收获，也欢迎你把这节课分享给身边的朋友。我们下节课再见！

## 上节课思考闭环

请你按照基础篇的课程思路，完整描述一下RabbitMQ从生产到消费的全过程？

跟经典的消息队列一样，RabbitMQ的生产到消费总共经过生产者、Broker、消费者三个模块。大致的流程如下：

在生产端，客户端根据AMQP协议定义的命令字（如Connection.Start/Start-Ok、Connection.Tune/Tune-Ok），通过四层的TCP协议和Broker创建Connection、Channel 进行通信。客户端直连Broker服务，不需要经过寻址，然后客户端需要指定Exchange、route\_key发送消息。因为AMQP没有支持批量发送的协议，消息会立即发送给给服务端。通信协议的内容格式、序列化和反序列化遵循AMQP的标准。

Broker收到消息后，根据AMQP协议反序列化解析出请求内容。根据Exchange和route\_key的信息，结合路由模式，将数据分发到具体的Queue中。存储层收到消息后，底层会将这条数据的结构进行整合，添加一些额外信息，如写入时间等，然后将数据写入到同一个文件存储。Broker支持数据过期机制，当消息过期后，数据会被删除。

消费端直接指定Queue消费，不需要经过消费分组、分区分配的过程。消费端跟生产端一样，根据AMQP协议连接上Broker后，消费端直接从Queue中消费数据，消费完成后通过手动ACK或自动ACK的方式ACK消息。