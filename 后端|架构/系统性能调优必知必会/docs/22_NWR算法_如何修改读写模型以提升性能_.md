你好，我是陶辉。

前两讲我们介绍数据库的扩展时，写请求仍然在操作中心化的Master单点，这在很多业务场景下都是不可接受的。这一讲我将介绍对于无单点的去中心化系统非常有用的NWR算法，它可以灵活地平衡一致性与性能。

最初我们仅在单机上部署数据库，一旦性能到达瓶颈，我们可以基于AKF Y轴将读写分离，这样多个Slave从库将读操作分流后，写操作就可以独享Master主库的全部性能。然而主库作为中心化的单点，一旦宕机，未及时同步到从库的数据就有可能丢失。而且，这一架构下，主库的故障还会导致整个系统瘫痪。

去中心化系统中没有“Master主库”这一概念，数据存放在多个Replication冗余节点上，且这些节点间地位均等，所以没有单点问题。为了保持强一致性，系统可以要求修改数据时，必须同时写入所有冗余节点，才能向客户端返回成功。但这样系统的可用性一定很成问题，毕竟大规模分布式系统中，出现故障是常态，写入全部节点的操作根本无法容错，任何1个节点宕机都会造成写操作失败。而且，同步节点过多也会导致写操作性能低下。

NWR算法提供了一个很棒的读写模型，可以解决上述问题。这里的“NWR”，是指在去中心化系统中将1份数据存放在N个节点上，每次操作时，写W个节点、读R个节点，只要调整W、R与N的关系，就能动态地平衡一致性与性能。NWR在NoSQL数据库中有很广泛的应用，比如Amazon的Dynamo和开源的Cassandra，这些数据库往往跨越多个IDC数据中心，包含成千上万个物理机节点，适用于海量数据的存储与处理。

这一讲，我们将介绍NWR算法的原理，包括它是怎样调整读写模型来提升性能的，以及Cassandra数据库是如何使用NWR算法的。

## 从鸽巢原理到NWR算法

NWR算法是由鸽巢原理得来的：如果10只鸽子放入9个鸽巢，那么有1个鸽巢内至少有2只鸽子，这就是鸽巢原理，如下图所示：

[![](https://static001.geekbang.org/resource/image/83/17/835a454f1ecb8d6edb5a1c2059082d17.jpg?wh=1246*1010)](https://zh.wikipedia.org/wiki/%E9%B4%BF%E5%B7%A2%E5%8E%9F%E7%90%86)

你可以用反证法证明它。鸽巢原理虽然简单，但它有许多很有用的推论。比如 [\[第3课\]](https://time.geekbang.org/column/article/232351) 介绍了很多解决哈希表冲突的方案，那么，哈希表有没有可能完全不出现冲突呢？ **鸽巢原理告诉我们，只要哈希函数输入主键的值范围大于输出索引，出现冲突的概率就一定大于0；只要存放元素的数量超过哈希桶的数量，就必然会发生冲突。**

基于鸽巢原理，David K. Gifford在1979年首次提出了 [Quorum](https://en.wikipedia.org/wiki/Quorum_(distributed_computing)) 算法（参见《 [Weighted Voting for Replicated Data](https://dl.acm.org/doi/epdf/10.1145/800215.806583)》论文），解决去中心化系统冗余数据的一致性问题。而Quorum算法提出，如果冗余数据存放在N个节点上，且每次写操作成功写入W个节点（其他N - W个节点将异步地同步数据），而读操作则从R个节点中选择并读出正确的数据，只要确保W + R > N，同1条数据的读、写操作就不能并发执行，这样客户端就总能读到最新写入的数据。特别是当W > N/2时，同1条数据的修改必然是顺序执行的。这样，分布式系统就具备了强一致性，这也是NWR算法的由来。

比如，若N为3，那么设置W和R为2时，在保障系统强一致性的同时，还允许3个节点中1个节点宕机后，系统仍然可以提供读、写服务，这样的系统具备了很高的可用性。当然，R和W的数值并不需要一致，如何调整它们，取决于读、写请求数量的比例。比如当N为5时，如果系统读多写少时，可以将W设为4，而R设为2，这样读操作的性能会更好。

NWR算法最早应用在Amazon推出的 [Dynamo](https://en.wikipedia.org/wiki/Dynamo_(storage_system)) 数据库中，你可以参见2007年Amazon发表的 [《Dynamo: Amazon’s Highly Available Key-value Store》](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) 论文。2008年Dynamo的作者Avinash Lakshman跳槽到FaceBook，开发了Dynamo的开源版数据库 [Cassandra](https://zh.wikipedia.org/wiki/Cassandra)，它是目前最流行的NoSQL数据库之一，在Apple、Netflix、360等公司得到了广泛的应用。想必你对NWR算法的很多细节并不清楚，那么接下来我们以Cassandra为例，看看NWR是如何应用在实际工程中的。

## Cassandra数据库是如何使用NWR算法的？

1个Cassandra分布式系统可以由多个IDC数据中心、数万个服务器节点构成，这些节点间使用RPC框架通信，由于Cassandra推出时gRPC（参见 [\[第18课\]](https://time.geekbang.org/column/article/247812)）还没有诞生，因此它使用的是性能相对较低的Thrift RPC框架（Thrift的优点是支持的开发语言更多）。同时，Cassandra虽然使用宽列存储模型（每行最多可以包含 [20亿列](https://docs.datastax.com/en/cql-oss/3.x/cql/cql_reference/refLimits.html) 数据），但 **数据的分布是基于行Key进行的**，它和Dynamo一样使用了一致性哈希算法，将Key对应的数据存储在多个节点中。关于一致性哈希算法，我们会在 \[第24课\] 再详细介绍。

Cassandra对客户端提供一种类SQL的 [CQL](https://cassandra.apache.org/doc/latest/cql/index.html) 语言，你可以使用下面这行CQL语句设定数据存储的冗余节点个数，也就是NWR算法中的N（也称为Replication Factor）：

```
CREATE KEYSPACE excalibur
  WITH REPLICATION = {'class' : 'NetworkTopologyStrategy', 'dc1' : 3};

```

上面这行CQL语句设置了每行数据在数据中心DC1中存储3份冗余，即N = 3，接下来我们通过下面的CQL语句，将读R、写W的节点数都设置为1：

```
cqlsh> CONSISTENCY ONE
Consistency level set to ONE.
cqlsh> CONSISTENCY
Current consistency level is ONE.

```

**此时，Cassandra的性能最高，但达成最终一致性的耗时最长，丢数据风险也最大。** 如果业务上对丢失少量数据不太在意，可以采用这种模型。此时修改数据时，客户端会并发地向3个存储节点写入数据，但只要1个节点返回成功，Cassandra就会向客户端返回写入成功，如下图所示：

[![](https://static001.geekbang.org/resource/image/74/1d/742a430b92bb3b235294805b7073991d.png?wh=606*415)](https://docs.datastax.com/en/cassandra-oss/3.x/cassandra/dml)

上图中的系统由12个主机节点构成，由于数据采用一致性哈希算法分片，故构成了一个节点环。其中，本次写入的数据被分布到1、3、6这3个节点中存储。客户端可以随机连接到系统中的任何一个节点访问Cassandra，此时该节点被称为Coordinator Node，由它根据NWR的值来选择一致性模型，访问存储节点。

再来看读取数据的流程。下图中，作为Coordinator Node的节点10首先试图读取节点1中的数据，但发现节点1已经宕机，于是改选节点6并获取到数据，由于R = 1于是立刻向客户端返回成功。

![](https://static001.geekbang.org/resource/image/50/d6/5038a63ce8a5cd23fcb6ba2e14b59cd6.jpg?wh=609*443)

如果我们将R、W都设置成2，这就满足了R + W > N(3)的场景，此时系统具备了强一致性。客户端读写数据时，必须有2个节点返回，才算操作成功。比如下图中读取数据时，只有接收到节点1、节点6的返回，操作才算成功。

![](https://static001.geekbang.org/resource/image/8d/0f/8dc00f0a82676cb54d21880e7b60c20f.jpg?wh=610*457)

上图中的蓝色线叫做Read repair，如果节点3上的数据不一致，那么本次读操作可以将它修复为正确的数据。说完正常场景，我们再来看当一个节点出现异常时，NWR是如何保持强一致性的。

下图中，客户端1在第2步，同时向3个存储节点写入了数据，由于节点1、3返回成功，所以写入操作实际已经完成了，但是节点6由于网络故障，却一直没有收到Coordinator Node发来的写入操作。在强一致性的约束下，客户端2在第5步发起的读请求，必须能获取到第2步写入的数据。然而，客户端2连接的Coordinator Node与客户端1不同，它选择了节点3和节点6，这两个节点上的数据并不一致。 **根据不同的timestamp时间戳，Coordinator Node发现节点3上的数据才是最后写入的数据，因此选择其上的数据返回客户端。这也叫Last-Write-Win策略。**

[![](https://static001.geekbang.org/resource/image/4b/fa/4bc3308298395b7a57d9d540a79aa7fa.jpg?wh=7306*3486)](https://blog.scottlogic.com/2017/10/06/cassandra-eventual-consistency.html)

Cassandra提供了一个简单的方法，用于设置读写节点数量都过半，满足强一致性的要求，如下所示：

```
cqlsh> CONSISTENCY QUORUM
Consistency level set to QUORUM.
cqlsh> CONSISTENCY
Current consistency level is QUORUM.

```

最后我们再来看看多数据中心的部署方式。下图中2个数据中心各设置N = 3，其中R、W则采用QUORUM一致性模型。当客户端发起写请求到达节点10这个Coordinator Node后，它选择本IDC Alpha的1、3、6节点存储数据，其中节点3、6返回成功后，IDC Alpha便更新成功。同时找到另一IDC Beta的节点11存储数据，并由节点11将数据同步给节点4和节点8。其中，只要节点4返回成功，IDC Beta也就成功更新了数据，此时Coordinator Node会向客户端返回写入成功。

![](https://static001.geekbang.org/resource/image/5f/00/5fe2fa80bb20e04d25c41ed5986c0c00.jpg?wh=618*811)

读取数据时，这2个IDC内必须由4个存储节点返回数据，才满足QUORUM一致性的要求。下图中，Coordinator Node获取到了IDC Alpha中节点1、3、6的返回，以及IDC Beta中节点11的返回，就可以基于timestamp时间戳选择最新的数据返回客户端。而且Coordinator Node会并发地发起Read repair，试图修复IDC Beta中可能存在不一致的节点4和8。

![](https://static001.geekbang.org/resource/image/59/19/59564438445fb26d2e8993a50a23df19.jpg?wh=614*892)

Cassandra还有许多一致性模型，比如LOCAL\_QUORUM只要求本地IDC内有多数节点响应即可，而EACH\_QUORUM则要求每个IDC内都必须有多数节点返回成功（注意，这与上图中IDC Alpha中有3个节点返回，而IDC Beta则只有1个节点返回的QUORUM是不同的）。你可以从 [这个页面](https://docs.datastax.com/en/cassandra-oss/3.x/cassandra/dml/dmlConfigConsistency.html) 找到Cassandra支持的所有一致性模型，但无论如何变化，都只是在引入数据中心、机架等概念后，局部性地调节NWR而已。

## 小结

这一讲我们介绍了鸽巢原理，以及由此推导出的NWR算法，并以流行的NoSQL数据库Cassandra为例，介绍了NWR在分布式系统中的实践。

当鸽子的数量超过了鸽巢后，就要注定某一个鸽巢内一定含有两只以上的鸽子，同样的道理，只要读、写操作涉及的节点超过半数，就注定读写操作总包含一个含有正确数据的节点。NWR算法将这一原理一般化为：只要读节点数R + 写节点数W > 存储节点数N，特别是W > N/2时，就能使去中心的分布式系统获得强一致性。

支持上万节点的Cassandra数据库，就使用了NWR算法来保持一致性。当然，Cassandra支持多种一致性模型，当你需要更强劲的性能时，你可以令R + W < N，当业务变化导致需要增强系统的一致性时，你可以实时地修改R、W。Cassandra也支持跨数据中心部署，此时的一致性模型更为复杂，但仍然将NWR算法作为实现基础。

## 思考题

最后给你留一道讨论题。你还知道哪些有状态服务使用了NWR算法吗？它与NWR在Cassandra中的应用有何不同？欢迎你在留言区中分享，也期待你能从大家的留言中总结出更一般化的规律。

感谢你的阅读，如果你觉得这节课对你有一些启发，也欢迎把它分享给你的朋友。