你好，我是文强。

上节课讲完了RocketMQ，这节课我们再来看一下流消息领域的消息队列Kafka。

因为我们之前在 [第16讲](https://time.geekbang.org/column/article/680879) 已经详细描述了，基于ZooKeeper和KRaft来构建集群的两种方式，在这里就不再重复。这节课我们会详细分析 Kafka 副本之间的数据一致性、数据同步机制、Leader 切换、数据截断。

## 数据可靠性

我们知道，Kafka 集群维度的数据可靠性也是通过副本来实现的，而副本间数据一致性是通过Kafka ISR 协议来保证的。ISR 协议是现有一致性协议的变种，它是参考业界主流的一致性协议，设计出来的符合流消息场景的一致性协议。

**ISR协议的核心思想是：** 通过副本拉取Leader数据、动态维护可用副本集合、控制Leader切换和数据截断3个方面，来提高性能和可用性。

![](https://static001.geekbang.org/resource/image/7e/ed/7e4cf5f54694b1624f91b31f2a2c7ced.jpg?wh=10666x6000)

参考图示，这是一个包含1个Leader、2个Follower的分区。如果是基于Raft协议或者多数原则实现的一致性算法，那么当Leader接收到数据后，就会直接分发给部分或全部副本。我们在前面两节课说到的 RabbitMQ的镜像队列、仲裁队列和 RocketMQ 的 Master/Slave、Dledger 都是这么实现的。

这种机制在流消息队列的大吞吐场景中主要有两个缺点：

1. 收到数据立即分发给多个副本，在请求量很大时，和副本之间的频繁交互会导致数据分发的性能不高。
2. 计算一致性的总副本数是固定的，当某个副本异常时，如果还往这个副本分发数据，此时会影响集群性能。

### **副本拉取Leader数据**

为了提高数据分发性能，主要的解决思路就是 **数据批量分发**。所以在实现上看，Kakfa 是通过Follower 批量从Leader拉取数据来完成主从副本间的数据同步，并提高性能的。

![](https://static001.geekbang.org/resource/image/68/fe/6818b32b368215f3451402b1ff7d79fe.jpg?wh=10666x6000)

如上图所示，Follower 会维护一批线程来从 Leader 拉取数据。此时，比如当 Leader 接收到1000 次数据，在 Leader 主动分发的场景中，就需要往两个 Follower 分别发起1000次请求。而在 ISR 模型下，假设 Follower 每批次拉取50条数据，此时每个Follower 和 Leader间的网络交互次数就减少到了20次，从而极大地提高了一致性的性能。

这里你可能就会有一个疑问： **如果是 Follower 来服务端拉取数据，那么当数据写入 Leader 后是直接告诉客户端写入成功吗？** 回答这个问题之前，我们先来看一张图。

![](https://static001.geekbang.org/resource/image/d0/f5/d0408914e4fa9961ea544b297ef5f7f5.jpg?wh=10666x6000)

从实现的角度看，当配置最终一致（ACK=1）或者强一致（ACK=-1）时，Leader接收到数据后不会立即告诉客户端写入成功。而是请求会进入一个本地的队列进行等待，等待 Follower 完成数据同步。当数据被副本同步后，Leader 才会告诉客户端写入成功。

等待这个行为的技术实现的核心思想是Leader维护的定时器， **时间轮**。简单理解就是时间轮会定时检查数据是否被同步，是的话就返回成功，否的话就判断是否超时，超时就返回超时错误，否则就继续等待。时间轮的具体实现，我们后面会详细分析，敬请期待。

### **动态维护可用副本集合**

在具体实现方面，ISR 会维护一个可用的副本集合。上节课我们讲过，RocketMQ的Controller 会维护可用副本集合SyncStateSet，这两者的思路是一样的。

即有一个三副本的分区，当服务都正常时，可用副本集合就有3个元素，比如 \[A、B、C\]。当某个副本异常时，比如副本宕机或副本性能有问题无法跟上Leader时，就会自动把这个副本剔出可用副本的集合，如下所示：

```plain
[A、B、C] => [A、B]

```

基于这个设计，此时总的可用副本为2。强一致计算的总副本数量也为2，则只要这两个副本写入成功即可。从而解决有问题节点不影响强一致可用性的问题。

**那怎么判断副本有异常呢？** 从技术实现来看，一般通过两种策略来判断。

1. 副本所在节点是否宕机，如果副本的节点挂了，就认为这个副本是不可用的。那如何判断副本的节点挂了呢？那就是我们在前面讲到的节点的心跳的探活机制。
2. 副本的数据拉取进度是否跟不上 Leader，即副本来Leader Pull数据的速度跟不上数据写入Leader数据的速度。此时如果Follower一直追不上Leader，这个Follower就会被踢出ISR集合。

在Kafka的实现中，最开始支持按数据条数去判断Follower是否跟得上Leader。但是因为不同Topic的流量不一样，根据数据条数很难准确判断落后情况。后来支持按照时间来判断落后情况，比如Follower 落后 Leader 多久，则表示 Follower 跟不上 Leader。当然，这是一个配置，可以调整。

### **控制** **Leader** **切换和数据截断**

我们知道，Leader切换的触发条件一般是节点的心跳探活失败后，由Controller或者元数据存储服务来触发的。

当出现Leader切换，如果所有节点的数据是强一致的，则直接进行Leader切换，不需要任何其他的处理，也不会有数据丢失的问题。这种方式实现是最简单的，开发成本也最低，但是性能较差。比如RabbitMQ的镜像队列和RocketMQ的Master/Slave的同步双写就是这种方案。

因为 Kafka ISR 协议是最终一致的，所以在某些极端的场景中会出现数据丢失和截断，所以我们需要在实现上做特殊的处理。

那什么情况下会出现数据丢失和截断呢？

![](https://static001.geekbang.org/resource/image/e5/dc/e5198a7def400ba3486d8365ebcf72dc.jpg?wh=10666x6000)

如上图所示，按照最终一致和多数原则，如果有2个副本A和B写入成功后，就会告诉客户端数据写入成功。此时，如果这两台节点同时挂掉， **就会有C节点成为Leader和C节点不成为 Leader两种场景。**

如果是C节点不能成为Leader，此时就不会有丢数据或截断问题。开发实现也简单，只是问题发生时，服务就不可用。

如果C节点可以成为Leader，此时就可能会出现数据截断。比如A、B有100条数据，C只有90条数据，此时A、B挂了，C 成为Leader 后重新接收数据。当 A 和 B 启动后，因为C这里也会有90～100之间的数据，如果要合并数据就会冲突。所以一般遇到这种情况，就会丢弃数据，然后就会有数据丢失。

在Kafka的实现中，这两种情况都是支持的，支持在 Topic 维度调整配置来选择这两个操作。所以Kafka的ISR协议的很大一部分工作，就是在代码层面处理Leader切换、数据阶段的操作。

接下来我们从传输安全、认证、鉴权3个方面，来分析一下 Kafka 的安全控制机制。

## 安全控制

Kafka 支持 TLS/SSL 进行数据加密传输。从代码实现层面看，服务端和客户端支持这部分能力，和RocketMQ 是一样的，都是 Java 代码的标准用法，这里就不再赘述了。

讲安全时我们讲过，SASL是一个身份验证和安全的框架。 **Kafka在这个框架下实现了GSSAPI、PLAIN、SCRAM、OAUTHBEARER、Delegation Token 5 种认证方式。**

[GSSAPI](https://docs.oracle.com/cd/E19253-01/819-7056/6n91eac3u/index.html) 全称是通用安全服务应用编程接口（Generic Security Service Application Programming Interface, GSS-API）的简称，它的目的是为应用程序提供一种用于保护发送数据的方法。它主要用在和 Kerberos 认证对接的过程。在Java Server 支持 GSSAPI 可以看这个 [教程](https://www.baeldung.com/java-gss)。

这里多说一句，Kerberos 是安全的、单点登录的、可信的第三方相互身份验证服务。

PLAIN 就是明文的用户名、密码认证机制，通过服务端提供的用户名密码来完成校验。PLAIN是Kafka 早期提供的明文认证机制，它的用户名和密码是写在 Broker 的配置文件中的，不支持动态修改。

为了解决这个问题，Kakfa 支持了 SCRAM 机制，SCRAM也是明文的认证机制。它跟PLAIN 最大的区别是，它的用户名和密码是存储在ZooKeeper中的，并支持 **动态修改**。

OAUTHBEARER 是 Kafka 为了支持 OAuth 认证机制而引入的。OAuth是我们常用的认证机制，它本质是一个安全的、开放而又简易的第三方认证机制。和其他的授权方式不同的是，OAuth授权不会使第三方触及到用户的帐号信息，即第三方无需使用用户的用户名与密码就可以申请获得该用户资源的授权，从而更加安全。在Java Server 支持OAuth可以看这个 [项目](https://github.com/authlete/java-oauth-server)。

Delegation Token是一种轻量级的Token认证机制，从实现原理来看，就是服务端签发保存Token，客户端携带Token来完成认证。Token信息也是保存在ZooKeeper上的。

在实现上，Kafka 的认证是一个独立的模块，通过接口形式实现了多种常见的认证机制。接下来我们来看看Kafka的鉴权。

Kakfa 对资源的管控粒度是比较细的，主要支持对Topic、Group、Cluster、TransactionalId、DelegationToken、User等 6 种资源进行控制，并给这些资源提供了Read、Write、Create、Delete、Alter、Describe、ClusterAction、DescribeConfigs、AlterConfigs、IdempotentWrite、CreateTokens、DescribeTokens、All 等 13 种权限，分别对应数据的读写、资源的增删改查、集群管控、配置修改、Token配置、全部权限等类型。 **同样的，Kafka也支持对来源IP的限制。**

从实现来看，用户的全新信息是保存在 ZooKeeper 的 /kafka-acl 目录中的。目录结构和权限如下所示：

```plain
/kafka-acl
  - Cluster
  - DelegationToken
  - Group
  - Topic
  - TransactionalId

权限配置详情：
{
    "version": 1,
    "acls": [
        {
            "host": "*",
            "operation": "Write",
            "permissionType": "Allow",
            "principal": "User:*"
        },
        {
            "host": "*",
            "operation": "Read",
            "permissionType": "Allow",
            "principal": "User:*"
        }
    ]
}

```

从运行的角度来看，在Broker启动时，会加载全部权限信息到内存中。当客户端访问某个功能时，会率先进行权限比对。当ZooKeeper节点的内容更新时，会下发通知，通知Broker重新读取 ZooKeeper 节点中的数据更新内存的内容。如果你想对Kafka权限配置有更加细致的了解，可以参考这个 [文档](https://kafka.apache.org/documentation/#security) 或者安装包自带的工具kafka-acls.sh。

从这么多细分权限可以知道，Kakfa在权限管控这里是做得非常细致。在现网运营过程中，基本是够用了的。

接下来我们从指标、日志、消息轨迹来看一下Kafka的可观测性。

## 可观测性

Kafka的指标定义是基于Yammer Metrics 库来实现的。Yammer Metrics 是Java中一个常用的指标库，它提供了Histogram、Meters、Gauges等类型来统计数据。对于Kafka的作用就是，使用这个库可以完成各种类型指标的统计和记录，代码使用方式如下：

```plain
val batchProcessingTimeHist = KafkaYammerMetrics.defaultRegistry().newHistogram(metricName(name, tags), biased)

batchProcessingTimeHist.update(1)

```

这个库的使用并不复杂，只需要引入包直接使用即可。如果你想在自己项目中使用这个库，可以参考 [这个教程](https://www.javacodegeeks.com/2012/12/yammer-metrics-a-new-way-to-monitor-your-application.html)。不过，如果是希望在自己的系统内注册统计指标，建议你使用OpenTelemetry Metrics或者Prometheus Metrics，这两种是近期在指标方面更常用的方案。

**在指标暴露方面，Kakfa 只支持JMX方式的指标获取。** 即如果需要从 Kafka 进程采集指标，就需要先在 Broker 上开启JMX Server。然后客户端通过JMX Client 去 Broker 采集对应的指标。

在实际运营中，主要有3种通过指标监控 Broker 的方式。

![](https://static001.geekbang.org/resource/image/be/70/beb3yy6f1cd58e453b8f5c7a6df99a70.jpg?wh=10666x4377)

如上图所示，可以通过代码使用 JMX Client 直接去采集Broker中的指标数据，然后自定义处理。也可以通过 JMX Export 采集指标，然后和 Prometheus 集成展示。从实现来看，JMX Export 底层也是通过JMX Client 去Broker采集数据的。另外社区提供了Kafka Export 通过Kafka Protocol 去获取消费进度、Topic信息等相关信息，然后再和 Prometheus 集成展示。

在日志方面，Kafka 也是基于 Log4j 库去打印日志，依赖 Log4j 库的强大，支持常见的日志功能，这里就不再细数。同时通过配置支持，将不同模块的日志打印到不同文件，如Controller、Coordinator、GC 等等，以便在运营过程中提高问题排查的效率。

在消息轨迹方面，Kafka 并没有提供对消息轨迹功能的支持。如果需要支持，得改造内核。从技术上来看，即在客户端SDK 实现轨迹上报的功能，在服务端记录生产时收到的数据信息和消费时发送的数据信息。

这里简单解释一下： **为什么 Kakfa 没有提供消息轨迹的功能？**

在我看来，主要是因为 Kakfa 定位的是流场景、大吞吐的消息队列。一般用在日志场景中，这些场景消息数量是非常大的。如果支持消息轨迹，那么一条消息至少需要生产者、Broker、消费者3条轨迹信息，此时轨迹数据的量就非常恐怖，从成本角度来看收益很低。

当然，也可以支持轨迹数据采样，但是采样的话，对消息场景来讲，如果是重要消息，就需要每一条消息都有轨迹。对于不重要的消息，也没必要采样。所以基于这些考虑，Kafka 社区对消息轨迹的支持就比较弱。

当然，有一些公司会通过改动内核来支持消息轨迹，这也是可行的。因为这可以满足把 Kafka 当作业务消息管道来用的场景。从技术实现来看，并不复杂。

## 总结

在集群构建方面，Kafka 支持依赖 ZooKeeper 和 KRaft 两种形态来存储元数据并完成集群构建，依赖Controller来完成集群的管理、Leader切换等等。

在数据可靠性方面，Kafka 依赖 ISR 协议来保证数据的高可靠。

Kafka 的支持通过 SSL 来完成数据的加密传输。同时支持GSSAPI、PLAIN、SCRAM、OAUTHBEARER、Delegation Token 等 5 种认证方式，并支持对Topic、Group、Cluster、TransactionalId、DelegationToken、User 等 6 种资源进行鉴权，提供了Read、Write、Create、Delete、Alter、Describe、ClusterAction、DescribeConfigs、AlterConfigs、IdempotentWrite、CreateTokens、DescribeTokens、All 等 13 种权限。从安全管控来说，Kafka做得非常细致。

在可观测性方面，Kafka 基于Yammer Metrics 库完成了指标的定义，基于JMX 完成了指标的暴露。在现网运营过程中，可以通过 Kafka Export + JMX Export + JMX 来完成集群监控体系的搭建。Kafka 对消息轨迹的需求不高，内核不支持轨迹相关功能，不过可以通过内核改造和SDK改造来支持消息轨迹，开发难度并不高。

## 思考题

为保证副本一致性，在 Leader 收到数据主动分发给副本的实现中，当某个节点出问题时，如何设计退避方案，以避免出现一些频繁的无效的调用？

欢迎分享你的思考，如果觉得有收获，也欢迎你把这节课分享给身边的朋友。我们下节课再见！

## 上节课思考闭环

为什么RocketMQ 会支持这么多种部署模式，出于什么考虑呢？

在我看来，这不是一个单纯的技术问题。我认为RocketMQ的多种部署模式就是演进出来的。从部署模式的演进，可以看到国内互联网架构演进的影子，如从Master/Slave（类MySQL）到Dledger（Raft实现数据一致性）再到Controller（选主、复制、Leader切换）。

经历了多种架构的演进，可能有最初的设计的问题，但是我认为它的演进受它的历史和业务背景因素所影响，比如开发周期、人力投入、业务需要等因素都会影响技术决策。

从RocketMQ架构来看，可以看到目前中国互联圈经常提到的一个说法：架构是演进出来的，不是设计出来的。对于这个观点，当然见仁见智，大家看法都不一样。但我觉得，我们应该尊重每个系统的架构设计，不要直接用好坏的标准来评价，我们可以抱着理解、拥抱的角度来理解它的设计。