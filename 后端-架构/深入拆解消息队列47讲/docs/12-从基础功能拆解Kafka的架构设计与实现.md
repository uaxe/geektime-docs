你好，我是文强。

上节课我们分析了RocketMQ在通信协议、网络模块、存储模块、生产者、消费者这五个模块的设计思路。这节课同样还是分析 Kafka 在这五个模块的设计实现。

在学习的过程中，你会发现Kafka和RocketMQ的架构是非常像的，那为什么今天我们还要单独拿出一节课来分析 Kafka 呢？因为它们俩面对的场景是不一样的，一个是消息场景、一个是流场景，所以它们在底层的协议设计、存储模型、消费方式的实现上也是不一样的。而实现的不同，又导致了它们在功能和性能上的表现不一样。

接下来我们就从底层原理的角度来看一下，它们都有哪些异同点。

## Kafka 系统架构

首先来看一下Kafka的架构图。

![](https://static001.geekbang.org/resource/image/39/5a/39d54678ca944b19d2470521dfbec15a.jpg?wh=10666x5048)

如上图所示，Kafka 由 Producer、Broker、ZooKeeper、Consumer 四个模块组成。其中，ZooKeeper 用来存储元数据信息，集群中所有元数据都持久化存储在ZooKeeper 当中。

Kafka有Topic和分区的概念，分区就相当于RocketMQ的MessageQueue。一个Topic可以包含一个或多个分区。消费方面通过Group来组织消费者和分区的关系。

到这你是不是发现了？ **Kafka架构和RocketMQ非常像。** 从社区信息来看，RocketMQ最初的设计应该参考过Kafka，所以它们的架构和概念非常像，只是在具体实现方式上不太一样。比如概念上分区和MessageQueue的作用是一样的，元数据存储ZooKeeper和NameServer 的作用也是一样的。

前面我们讲过，使用 ZooKeeper 作为元数据存储服务会带来额外的维护成本、数据一致性和集群规模限制（主要是分区数）等问题。所以RocketMQ 使用NameServer替代ZooKeeper，Kafka 3.0 使用内置的Raft机制替代 ZooKeeper，就是为了解决这几个问题。

从消息的生命周期来看，生产者也需要通过客户端寻址拿到元数据信息。客户端通过生产分区分配机制，选择消息发送到哪个分区，然后根据元数据信息拿到分区Leader所在的节点，最后将数据发送到Broker。Broker收到消息并持久化存储。消费端使用消费分组或直连分区的机制去消费数据，如果使用消费分组，就会经过消费者和分区的分配流程，消费到消息后，最后向服务端提交Offset记录消费进度，用来避免重复消费。

讲完基本概念和架构，我们继续围绕着基础篇的五个模块来分析一下Kafka，先来看一下协议和网络模块。

## 协议和网络模块

Kafka 是自定义的私有协议，经过多年发展目前有V0、V1、V2三个版本，稳定在V2版本。官方没有支持其他的协议，比如HTTP，但是商业化的 Kafka 一般都会支持HTTP协议，原因还是 HTTP 协议使用的便捷性。

Kafka 协议从结构上来看包含协议头和协议体两部分， **协议头包含基础通用的信息，协议体由于每个接口的功能参数不一样，内容结构上差异很大。**

Kafka 协议的细节在 [第03讲](https://time.geekbang.org/column/article/670596) 已经详细讲过了，这里就不再重复。关于协议的更多详细信息你还可以参考 [官方的协议文档](https://kafka.apache.org/protocol.html#:~:text=Kafka%20uses%20a%20binary%20protocol,of%20the%20following%20primitive%20types.)。

Kafka 服务端的网络层是基于 Java NIO和Reactor 来开发的，通过多级的线程调度来提高性能。Kafka 网络层细节在 [第04讲](https://time.geekbang.org/column/article/670965) 我们也讲过，遗忘的话可以去复习。

## 数据存储

下面我们继续来看Kafka的存储层，Kafka 同样分为元数据存储和消息数据存储两部分。

### 元数据存储

上面我们说过，Kafka的元数据是存储在ZooKeeper里面的。元数据信息包括Topic、分区、Broker节点、配置等信息。ZooKeeper 会持久化存储全量元数据信息，Broker 本身不存储任何集群相关的元数据信息。在Broker启动的时候，需要连接ZooKeeper读取全量元数据信息。

ZooKeeper是一个单独的开源项目，它自带了集群组网、数据一致性、持久化存储、监听机制等等完整的能力。它的底层是基于Zab协议组件集群，有Leader节点和Slave节点的概念，数据写入全部在Leader节点完成，Slave负责数据的读取工作。

![](https://static001.geekbang.org/resource/image/5e/78/5ed6a93804949915ebf406e7d76a7e78.jpg?wh=10666x6000)

从ZooKeeper的角度来看， **Kafka只是它的一个使用者**，Kafka用ZooKeeper的标准使用方式向ZooKeeper集群上写入、删除、更新数据，以完成Kafka的元数据管理、集群构建等工作。所以每台Broker启动时，都会在ZooKeeper注册、监听一些节点信息，从而感知集群的变化。

另外，Kakfa 集群中的一些如消费进度信息、事务信息，分层存储元数据，以及3.0后的Raft架构相关的元数据信息，都是基于内置Topic来完成存储的。把数据存储在内置Topic中，算是一个比较巧妙的思路了，也是一个值得借鉴的技巧。Kafka 中存储不同功能的元数据信息的Topic列表如下所示：

![](https://static001.geekbang.org/resource/image/62/46/6260ced9bbb35d3c9fc9185314df2d46.jpg?wh=10666x3829)

### 消息数据

在消息数据存储方面，Kafka的数据是以分区为维度单独存储的。即写入数据到Topic后，根据生产分区分配关系，会将数据分发到 Topic 中不同的分区。此时底层不同分区的数据是存储在不同的“文件”中的，即一个分区一个数据存储“文件”。这里提到的“文件”也是一个虚指，在系统底层的表现是一个目录，里面的文件会分段存储。

如下图所示，当Broker收到数据后，是直接将数据写入到不同的分区文件中的。所以在消费的时候，消费者也是直接从每个分区读取数据。这个存储模型和RocketMQ、RabbitMQ都不像，这里的选择考虑和优劣势可以回顾 [第05讲](https://time.geekbang.org/column/article/671725)。

![](https://static001.geekbang.org/resource/image/ff/82/ffd5d608f6ffc0a2f506d098ba7f7782.jpg?wh=10666x3689)

在底层数据存储中，Kafka的存储结构是以Topic和分区维度来组织的。一个分区一个目录，目录名称是TopicName + 分区号，结构如下图所示：

```plain
/data/kafka/data#ll
drwxr-xr-x 2 root root 4096 2月  15 2020 __consumer_offsets-0
drwxr-xr-x 2 root root 4096 2月  15 2020 __consumer_offsets-1
drwxr-xr-x 2 root root 4096 2月  15 2020 __consumer_offsets-2
drwxr-xr-x 2 root root 4096 2月  15 2020 __transaction_state-0
drwxr-xr-x 2 root root 4096 2月  15 2020 __transaction_state-1
drwxr-xr-x 2 root root 4096 2月  15 2020 __transaction_state-2

```

每个分区的目录下，都会有 .index、.log、.timeindex 三类文件。其中，.log 是消息数据的存储文件，.index 是偏移量（offset）索引文件，.timeindex 是时间戳索引文件。两个索引文件分别根据 Offset 和时间来检索数据。

```plain
/data/data/data#ll __consumer_offsets-0
总用量 0
-rw-r--r-- 1 root root 10485760 11月 19 2020 00000000000000000000.index
-rw-r--r-- 1 root root        0 2月  15 2020 00000000000000000000.log
-rw-r--r-- 1 root root 10485756 11月 19 2020 00000000000000000000.timeindex
-rw-r--r-- 1 root root        0 2月  15 2020 leader-epoch-checkpoint

```

在节点维度，也会持久存储当前节点的数据信息（如 BrokerID）和一些异常恢复用的Checkpoint 等数据。

由于每个分区存储的数据量会很大，分区数据也会进行分段存储。分段是在.log进行的，文件分段的默认数据大小也是1G，可以通过配置项来修改。

**Kafka提供了根据过期时间和数据大小清理的机制，清理机制是在Topic维度生效的。** 当数据超过配置的过期时间或者超过大小的限制之后，就会进行清理。清理的机制也是延时清理的机制，它是根据每个段文件进行清理的，即整个文件的数据都过期后，才会清理数据。

特别说明的是，根据大小清理的机制是在分区维度生效的，不是Topic。即当分区的数据大小超过设置的大小，就会触发清理逻辑。这个机制和RocketMQ的清理机制是一致的，但RocketMQ只提供了按节点维度配置的消息过期机制，所以相比之下，根据分区维度存储能带来一定的便捷。

在存储性能上，Kafka的写入大量依赖顺序写、写缓存、批量写来提高性能。消费方面依赖批量读、顺序读、读缓存的热数据、零拷贝来提高性能。在这些技巧中，每个分区的顺序读写是高性能的核心。

接下来我们看一下客户端，看看Kafka的生产者和消费者的实现。

## 生产者和消费者

Kafka 客户端在连接 Broker 之前需要经过客户端寻址，找到目标Broker的信息。在早期，Kafka 客户端是通过链接 ZooKeeper 完成寻址操作的，但是因为ZooKeeper的性能不够，如果大量的客户端都访问ZooKeeper，那么就会导致ZooKeeper超载，从而导致集群异常。

所以在新版本的Kafka中，客户端是通过直连Broker完成寻址操作的，不会跟ZooKeeper交互。即Broker跟ZooKeeper交互，在本地缓存全量的元数据信息，然后客户端通过连接Broker拿到元数据信息，从而避免对ZooKeeper造成太大负载。

![](https://static001.geekbang.org/resource/image/49/49/49ca389c31ccd15cb11e3yyb31b3d449.jpg?wh=10666x4859)

我们知道 RocketMQ 一直是通过 NameServer 完成寻址操作的，这就是我们说的虽然RocketMQ和Kafka架构很像，但是实际的实现相差很大。

### 生产者

生产者完成寻址后，在发送的时候可以将数据发送到Topic或者直接发送到分区。发送到Topic时会经过生产分区分配的流程，即根据一定的策略将数据发送到不同的分区。

**Kafka提供了轮询和KeyHash两种策略。**

轮询策略是指按消息维度轮询，将数据平均分配到多个分区。Key Hash是指根据消息的Key生成一个Hash值，然后和分区数量进行取余操作，得到的结果可以确定要将数据发送到哪个分区。生产消息分配的过程是在客户端完成的。

Kafka 协议提供了批量（Batch）发送的语义。所以生产端会在本地先缓存数据，根据不同的分区聚合数据后，再根据一定的策略批量将数据写入到Broker。因为这个Batch机制的存在，客户端和服务端的吞吐性能会提高很多。

![](https://static001.geekbang.org/resource/image/92/2b/92ce44f04a794c072c74de7dc2e48a2b.jpg?wh=10666x6000)

这里多讲一点，客户端批量往服务端写有两种形式： **一种是协议和内核就提供了Batch语义，一种是在业务层将一批数据聚合成一次数据发送。** 这两种虽然都是批量发送，但是它们的区别在于：

1. 第一种批量消息中的每条消息都会有一个Offset，每条消息在Broker看来就是一条消息。第二种批量消息是这批消息就是一条消息，只有一个Offset。
2. 在消费端看来，第一种对客户端是无感的，一条消息就是一条消息。第二种需要消费者感知生产的批量消息，然后解析批量，逐条处理。

### 消费者

Kafka 的消费端只提供了Pull（拉）模式的消费。即客户端是主动不断地去服务端轮询数据、获取数据，消费则是直接从分区拉取数据的。Kafka提供了消费分组消费和直连分区消费两种模式，这两者的区别在于，是否需要进行消费者和分区的分配，以及消费进度谁来保存。

**大部分情况下，都是基于消费分组消费。** 消费分组创建、消费者或分区变动的时候会进行重平衡，重新分配消费关系。Kafka 默认提供了RangeAssignor（范围）、RoundRobinAssignor（轮询）、 StickyAssignor（粘性）三种策略，也可以自定义策略。消费分组模式下，一个分区只能给一个消费者消费，消费是顺序的。

当客户端成功消费数据后，会往服务端提交消费进度信息，此时服务端也不会删除具体的消息数据，只会保存消费位点信息。位点数据保存在内部的一个 Topic（\_\_consumer\_offset）中。消费端同样提供了自动提交和手动提交两种模式。当消费者重新启动时，会根据上一次保存的位点去消费数据，用来避免重复消费。

最后我们还是来看一下 Kafka 对HTTP协议和管控操作的支持。

## HTTP 协议支持和管控操作

Kafka内核是不支持HTTP协议的，如果需要支持，则需要在Broker前面挂一层代理。如Confluent开源的 [Kafka Rest](https://github.com/confluentinc/kafka-rest)。

管控的大部分操作是通过Kafka Protocol暴露的，基于四层的TCP进行通信。还有部分可以通过直连ZooKeeper完成管控操作。

在早期很多管控操作都是通过操作ZooKeeper完成的。后来为了避免对ZooKeeper造成压力，所有的管控操作都会通过 Broker 再封装一次，即客户端SDK 通过Kafka Protocol调用Broker，Broker再去和ZooKeeper 交互。

![](https://static001.geekbang.org/resource/image/87/69/87e542e15283f885e1ebb58dca636369.jpg?wh=10666x4478)

Kafka 命令行提供了管控、生产、消费、压测等功能，其底层就是通过客户端SDK和Broker进行交互的。我们在代码里面也可以通过客户端SDK完成相应的操作， **不用必须通过命令行**。

因为历史的演进，在一些命令行里面，还残留着直连ZooKeeper的操作。而我们也可以通过直接操作ZooKeeper中的数据完成一些操作，比如更改配置、创建Topic等等。

## 总结

最后，我们再来总结一下Kafka。

1. 协议层只支持私有的 Kafka Protocol协议。
2. 网络层是基于原生的Java NIO开发，底层也是通过多路复用、异步IO、Reactor模型等技术来提高网络模块的性能。
3. 存储层是每个分区对应一份具体的存储文件，分区文件在底层会分段存储，同时支持基于时间和大小的数据过期机制。
4. 元数据存储是通过ZooKeeper来实现的，所有的元数据都存储在ZooKeeper中。
5. 客户端的访问同样也需要经过客户端寻址机制。老版本可以通过ZooKeeper获取元数据信息，新版本只能通过Broker拿到元数据信息。拿到所有元数据信息后，才会直连Broker。
6. 生产端支持将数据写入到Topic或指定写入某个分区，写入Topic时需要经过生产分区分配操作，选择出最终需要写入的分区，同时支持批量写入的语义。
7. 消费端也有消费分组的概念，消费时需要在多个消费者和消费分组之间进行消费的负载均衡，同时也支持指定分区消费的模式。

## 思考题

请你按照基础篇的思路，描述一下Kafka从生产到消费的全过程？

欢迎在留言区分享你的答案，如果觉得有收获，也欢迎你把这节课分享给身边的朋友。我们下节课再见！

## 上节课思考闭环

请你按照基础篇的思路，描述一下 RocketMQ 从生产到消费的全过程，越详细越好。

跟经典的消息队列一样，RocketMQ 生产到消费也经过了生产者、Broker、消费者三个模块。我们通过Remoting协议来讲解一下大致的流程，具体如下：

在生产端，客户端通过四层的TCP协议和NameServer建立连接，通过Remoting协议从 NameServer 获取到集群的元数据信息。根据元数据信息，和对应的Broker的建立TCP连接。如果客户端指定了目标Topic，消息则先经过消息分区分配，然后才将数据发送到Broker中。因为Remoting也没有支持Batch的协议，所以数据会直接发送到对应的Broker，可以使用单向发送、同步发送、异步发送三种发送形式。

Broker 接收到数据后，会先使用Remoting反序列化数据。然后解析处理数据，将数据整合后，在底层会写入到同一个文件中，存储数据的时候会进行分段存储。如果是集群部署并设置了副本，则数据会分发到其他Broker的副本中。当数据过期后，Broker会自动清理节点上的数据。

在消费端，可以先选择Pull、Push、Pop其中的一种消费模型。客户端同样需要先和NameServer完成寻址操作。消费端有消费分组的概念，所以会先进行消费者和分区的消费关系分配的流程，然后消费者会和自己消费的分区的Leader所在的Broker建立连接。接着，客户端会使用 Remoting 协议从Broker消费数据。数据消费成功后，最后会提交消费进度。