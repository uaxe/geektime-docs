你好，我是胡夕。今天我要和你分享的主题是：Kafka的Java消费者是如何管理TCP连接的。

在专栏 [第13讲](https://time.geekbang.org/column/article/103844) 中，我们专门聊过“Java **生产者** 是如何管理TCP连接资源的”这个话题，你应该还有印象吧？今天算是它的姊妹篇，我们一起来研究下Kafka的Java **消费者** 管理TCP或Socket资源的机制。只有完成了今天的讨论，我们才算是对Kafka客户端的TCP连接管理机制有了全面的了解。

和之前一样，我今天会无差别地混用TCP和Socket两个术语。毕竟，在Kafka的世界中，无论是ServerSocket，还是SocketChannel，它们实现的都是TCP协议。或者这么说，Kafka的网络传输是基于TCP协议的，而不是基于UDP协议，因此，当我今天说到TCP连接或Socket资源时，我指的是同一个东西。

## 何时创建TCP连接？

我们先从消费者创建TCP连接开始讨论。消费者端主要的程序入口是KafkaConsumer类。 **和生产者不同的是，构建KafkaConsumer实例时是不会创建任何TCP连接的**，也就是说，当你执行完new KafkaConsumer(properties)语句后，你会发现，没有Socket连接被创建出来。这一点和Java生产者是有区别的，主要原因就是生产者入口类KafkaProducer在构建实例的时候，会在后台默默地启动一个Sender线程，这个Sender线程负责Socket连接的创建。

从这一点上来看，我个人认为KafkaConsumer的设计比KafkaProducer要好。就像我在第13讲中所说的，在Java构造函数中启动线程，会造成this指针的逃逸，这始终是一个隐患。

如果Socket不是在构造函数中创建的，那么是在KafkaConsumer.subscribe或KafkaConsumer.assign方法中创建的吗？严格来说也不是。我还是直接给出答案吧： **TCP连接是在调用KafkaConsumer.poll方法时被创建的**。再细粒度地说，在poll方法内部有3个时机可以创建TCP连接。

1. **发起FindCoordinator请求时**。

还记得消费者端有个组件叫协调者（Coordinator）吗？它驻留在Broker端的内存中，负责消费者组的组成员管理和各个消费者的位移提交管理。当消费者程序首次启动调用poll方法时，它需要向Kafka集群发送一个名为FindCoordinator的请求，希望Kafka集群告诉它哪个Broker是管理它的协调者。

不过，消费者应该向哪个Broker发送这类请求呢？理论上任何一个Broker都能回答这个问题，也就是说消费者可以发送FindCoordinator请求给集群中的任意服务器。在这个问题上，社区做了一点点优化：消费者程序会向集群中当前负载最小的那台Broker发送请求。负载是如何评估的呢？其实很简单，就是看消费者连接的所有Broker中，谁的待发送请求最少。当然了，这种评估显然是消费者端的单向评估，并非是站在全局角度，因此有的时候也不一定是最优解。不过这不并影响我们的讨论。总之，在这一步，消费者会创建一个Socket连接。

2. **连接协调者时。**

Broker处理完上一步发送的FindCoordinator请求之后，会返还对应的响应结果（Response），显式地告诉消费者哪个Broker是真正的协调者，因此在这一步，消费者知晓了真正的协调者后，会创建连向该Broker的Socket连接。只有成功连入协调者，协调者才能开启正常的组协调操作，比如加入组、等待组分配方案、心跳请求处理、位移获取、位移提交等。

3. **消费数据时。**

消费者会为每个要消费的分区创建与该分区领导者副本所在Broker连接的TCP。举个例子，假设消费者要消费5个分区的数据，这5个分区各自的领导者副本分布在4台Broker上，那么该消费者在消费时会创建与这4台Broker的Socket连接。

## 创建多少个TCP连接？

下面我们来说说消费者创建TCP连接的数量。你可以先思考一下大致需要的连接数量，然后我们结合具体的Kafka日志，来验证下结果是否和你想的一致。

我们来看看这段日志。

> _\[2019-05-27 10:00:54,142\] DEBUG \[Consumer clientId=consumer-1, groupId=test\] Initiating connection to node localhost:9092 (id: -1 rack: null) using address localhost/127.0.0.1 (org.apache.kafka.clients.NetworkClient:944)_

> _......_

> _\[2019-05-27 10:00:54,188\] DEBUG \[Consumer clientId=consumer-1, groupId=test\] Sending metadata request MetadataRequestData(topics=\[MetadataRequestTopic(name='t4')\], allowAutoTopicCreation=true, includeClusterAuthorizedOperations=false, includeTopicAuthorizedOperations=false) to node localhost:9092 (id: -1 rack: null) (org.apache.kafka.clients.NetworkClient:1097)_

> _......_

> _\[2019-05-27 10:00:54,188\] TRACE \[Consumer clientId=consumer-1, groupId=test\] Sending FIND\_COORDINATOR {key=test,key\_type=0} with correlation id 0 to node -1 (org.apache.kafka.clients.NetworkClient:496)_

> _\[2019-05-27 10:00:54,203\] TRACE \[Consumer clientId=consumer-1, groupId=test\] Completed receive from node -1 for FIND\_COORDINATOR with correlation id 0, received {throttle\_time\_ms=0,error\_code=0,error\_message=null, node\_id=2,host=localhost,port=9094} (org.apache.kafka.clients.NetworkClient:837)_

> _......_

> _\[2019-05-27 10:00:54,204\] DEBUG \[Consumer clientId=consumer-1, groupId=test\] Initiating connection to node localhost:9094 (id: 2147483645 rack: null) using address localhost/127.0.0.1 (org.apache.kafka.clients.NetworkClient:944)_

> _......_

> _\[2019-05-27 10:00:54,237\] DEBUG \[Consumer clientId=consumer-1, groupId=test\] Initiating connection to node localhost:9094 (id: 2 rack: null) using address localhost/127.0.0.1 (org.apache.kafka.clients.NetworkClient:944)_

> _\[2019-05-27 10:00:54,237\] DEBUG \[Consumer clientId=consumer-1, groupId=test\] Initiating connection to node localhost:9092 (id: 0 rack: null) using address localhost/127.0.0.1 (org.apache.kafka.clients.NetworkClient:944)_

> _\[2019-05-27 10:00:54,238\] DEBUG \[Consumer clientId=consumer-1, groupId=test\] Initiating connection to node localhost:9093 (id: 1 rack: null) using address localhost/127.0.0.1 (org.apache.kafka.clients.NetworkClient:944)_

这里我稍微解释一下，日志的第一行是消费者程序创建的第一个TCP连接，就像我们前面说的，这个Socket用于发送FindCoordinator请求。由于这是消费者程序创建的第一个连接，此时消费者对于要连接的Kafka集群一无所知，因此它连接的Broker节点的ID是-1，表示消费者根本不知道要连接的Kafka Broker的任何信息。

值得注意的是日志的第二行，消费者复用了刚才创建的那个Socket连接，向Kafka集群发送元数据请求以获取整个集群的信息。

日志的第三行表明，消费者程序开始发送FindCoordinator请求给第一步中连接的Broker，即localhost:9092，也就是nodeId等于-1的那个。在十几毫秒之后，消费者程序成功地获悉协调者所在的Broker信息，也就是第四行标为橙色的“node\_id = 2”。

完成这些之后，消费者就已经知道协调者Broker的连接信息了，因此在日志的第五行发起了第二个Socket连接，创建了连向localhost:9094的TCP。只有连接了协调者，消费者进程才能正常地开启消费者组的各种功能以及后续的消息消费。

在日志的最后三行中，消费者又分别创建了新的TCP连接，主要用于实际的消息获取。还记得我刚才说的吗？要消费的分区的领导者副本在哪台Broker上，消费者就要创建连向哪台Broker的TCP。在我举的这个例子中，localhost:9092，localhost:9093和localhost:9094这3台Broker上都有要消费的分区，因此消费者创建了3个TCP连接。

看完这段日志，你应该会发现日志中的这些Broker节点的ID在不断变化。有时候是-1，有时候是2147483645，只有在最后的时候才回归正常值0、1和2。这又是怎么回事呢？

前面我们说过了-1的来由，即消费者程序（其实也不光是消费者，生产者也是这样的机制）首次启动时，对Kafka集群一无所知，因此用-1来表示尚未获取到Broker数据。

那么2147483645是怎么来的呢？它是 **由Integer.MAX\_VALUE减去协调者所在Broker的真实ID计算得来的**。看第四行标为橙色的内容，我们可以知道协调者ID是2，因此这个Socket连接的节点ID就是Integer.MAX\_VALUE减去2，即2147483647减去2，也就是2147483645。这种节点ID的标记方式是Kafka社区特意为之的结果，目的就是要让组协调请求和真正的数据获取请求使用不同的Socket连接。

至于后面的0、1、2，那就很好解释了。它们表征了真实的Broker ID，也就是我们在server.properties中配置的broker.id值。

我们来简单总结一下上面的内容。通常来说，消费者程序会创建3类TCP连接：

1. 确定协调者和获取集群元数据。
2. 连接协调者，令其执行组成员管理操作。
3. 执行实际的消息获取。

那么，这三类TCP请求的生命周期都是相同的吗？换句话说，这些TCP连接是何时被关闭的呢？

## 何时关闭TCP连接？

和生产者类似，消费者关闭Socket也分为主动关闭和Kafka自动关闭。主动关闭是指你显式地调用消费者API的方法去关闭消费者，具体方式就是 **手动调用KafkaConsumer.close()方法，或者是执行Kill命令**，不论是Kill -2还是Kill -9；而Kafka自动关闭是由 **消费者端参数connection.max.idle.ms** 控制的，该参数现在的默认值是9分钟，即如果某个Socket连接上连续9分钟都没有任何请求“过境”的话，那么消费者会强行“杀掉”这个Socket连接。

不过，和生产者有些不同的是，如果在编写消费者程序时，你使用了循环的方式来调用poll方法消费消息，那么上面提到的所有请求都会被定期发送到Broker，因此这些Socket连接上总是能保证有请求在发送，从而也就实现了“长连接”的效果。

针对上面提到的三类TCP连接，你需要注意的是， **当第三类TCP连接成功创建后，消费者程序就会废弃第一类TCP连接**，之后在定期请求元数据时，它会改为使用第三类TCP连接。也就是说，最终你会发现，第一类TCP连接会在后台被默默地关闭掉。对一个运行了一段时间的消费者程序来说，只会有后面两类TCP连接存在。

## 可能的问题

从理论上说，Kafka Java消费者管理TCP资源的机制我已经说清楚了，但如果仔细推敲这里面的设计原理，还是会发现一些问题。

我们刚刚讲过，第一类TCP连接仅仅是为了首次获取元数据而创建的，后面就会被废弃掉。最根本的原因是，消费者在启动时还不知道Kafka集群的信息，只能使用一个“假”的ID去注册，即使消费者获取了真实的Broker ID，它依旧无法区分这个“假”ID对应的是哪台Broker，因此也就无法重用这个Socket连接，只能再重新创建一个新的连接。

为什么会出现这种情况呢？主要是因为目前Kafka仅仅使用ID这一个维度的数据来表征Socket连接信息。这点信息明显不足以确定连接的是哪台Broker，也许在未来，社区应该考虑使用 **<主机名、端口、ID>** 三元组的方式来定位Socket资源，这样或许能够让消费者程序少创建一些TCP连接。

也许你会问，反正Kafka有定时关闭机制，这算多大点事呢？其实，在实际场景中，我见过很多将connection.max.idle.ms设置成-1，即禁用定时关闭的案例，如果是这样的话，这些TCP连接将不会被定期清除，只会成为永久的“僵尸”连接。基于这个原因，社区应该考虑更好的解决方案。

## 小结

好了，今天我们补齐了Kafka Java客户端管理TCP连接的“拼图”。我们不仅详细描述了Java消费者是怎么创建和关闭TCP连接的，还对目前的设计方案提出了一些自己的思考。希望今后你能将这些知识应用到自己的业务场景中，并对实际生产环境中的Socket管理做到心中有数。

![](https://static001.geekbang.org/resource/image/f1/04/f13d7008d7b251df0e6e6a89077d7604.jpg?wh=2069*2535)

## 开放讨论

假设有个Kafka集群由2台Broker组成，有个主题有5个分区，当一个消费该主题的消费者程序启动时，你认为该程序会创建多少个Socket连接？为什么？

欢迎写下你的思考和答案，我们一起讨论。如果你觉得有所收获，也欢迎把文章分享给你的朋友。