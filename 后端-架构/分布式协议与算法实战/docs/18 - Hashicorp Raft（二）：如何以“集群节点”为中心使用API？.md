你好，我是韩健。

上一讲结束后，相信有的同学已经跃跃欲试，想把Hashicorp Raft使用起来了。不过，也有一些同学跟我反馈，说自己看到Hashicorp Raft的 [Godoc](https://godoc.org/github.com/hashicorp/raft)，阅读完接口文档后，感觉有些不知所措，无从下手，Hashicorp Raft支持了那么多的函数，自己却不知道如何将这些函数使用起来。

这似乎是一个共性的问题，在我看来，之所以出现这个问题，是因为文档里虽然提到了API的功能，但并没有提如何在实际场景中使用这些API，每个API都是孤立的点，缺乏一些场景化的线将它们串联起来。

所以，为了帮你更好地理解Hashicorp Raft的API接口，在实践中将它们用起来，我以“集群节点”为核心，通过创建、增加、移除集群节点，查看集群节点状态这4个典型的场景，具体聊一聊在Hashicorp Raft中，通过哪些API接口能创建、增加、移除集群节点，查看集群节点状态。这样一来，我们会一步一步，循序渐进地彻底吃透Hashicorp Raft的API接口用法。

我们知道，开发实现一个Raft集群的时候，首先要做的第一个事情就是创建Raft节点，那么在Hashicorp Raft中如何创建节点呢？

## 如何创建Raft节点

在Hashicorp Raft中，你可以通过NewRaft()函数，来创建Raft节点。我强调一下，NewRaft()是非常核心的函数，是Raft节点的抽象实现，NewRaft()函数的原型是这样的：

```
func NewRaft(
        conf *Config,
        fsm FSM,
        logs LogStore,
        stable StableStore,
        snaps SnapshotStore,
        trans Transport) (*Raft, error)

```

你可以从这段代码中看到，NewRaft()函数有这么几种类型的参数，它们分别是：

- Config（节点的配置信息）；
- FSM（有限状态机）；
- LogStore（用来存储Raft的日志）；
- StableStore（稳定存储，用来存储Raft集群的节点信息等）；
- SnapshotStore（快照存储，用来存储节点的快照信息）；
- Transport（Raft节点间的通信通道）。

这6种类型的参数决定了Raft节点的配置、通讯、存储、状态机操作等核心信息，所以我带你详细了解一下，在这个过程中，你要注意是如何创建这些参数信息的。

Config是节点的配置信息，可通过函数DefaultConfig()来创建默认配置信息，然后按需修改对应的配置项。一般情况下，使用默认配置项就可以了。不过，有时你可能还是需要根据实际场景，来调整配置项的，比如：

- 如果在生产环境中部署的时候，你可以将LogLevel从DEBUG调整为WARM或ERROR；
- 如果部署环境中网络拥堵，你可以适当地调大HeartbeatTimeout的值，比如，从1s调整为1.5s，避免频繁的领导者选举；

那么FSM又是什么呢？它是一个interface类型的数据结构，借助Golang Interface的泛型编程能力，应用程序可以实现自己的Apply(\*Log)、Snapshot()、Restore(io.ReadCloser) 3个函数，分别实现将日志应用到本地状态机、生成快照和根据快照恢复数据的功能。FSM是日志处理的核心实现，原理比较复杂，不过不是咱们本节课的重点，现在你只需要知道这3个函数就可以了。在20讲，我会结合实际代码具体讲解的。

第三个参数LogStore存储的是Raft日志，你可以用 [raft-boltdb](https://github.com/hashicorp/raft-boltdb) 来实现底层存储，持久化存储数据。在这里我想说的是，raft-boltdb是Hashicorp团队专门为Hashicorp Raft持久化存储而开发设计的，使用广泛，打磨充分。具体用法是这样的：

```
logStore, err := raftboltdb.NewBoltStore(filepath.Join(raftDir, "raft-log.db"))

```

NewBoltStore()函数只支持一个参数，也就是文件路径。

第四个参数StableStore存储的是节点的关键状态信息，比如，当前任期编号、最新投票时的任期编号等，同样，你也可以采用raft-boltdb来实现底层存储，持久化存储数据。

```
stableStore, err := raftboltdb.NewBoltStore(filepath.Join(raftDir, "raft-stable.db"))

```

第五个参数SnapshotStore存储的是快照信息，也就是压缩后的日志数据。在Hashicorp Raft中提供了3种快照存储方式，它们分别是：

- DiscardSnapshotStore（不存储，忽略快照，相当于/dev/null，一般来说用于测试）；
- FileSnapshotStore（文件持久化存储）；
- InmemSnapshotStore（内存存储，不持久化，重启程序后，数据会丢失）。

**这3种方式，在生产环境中，建议你采用FileSnapshotStore实现快照， 使用文件持久化存储，避免因程序重启，导致快照数据丢失。** 具体代码实现如下：

```
snapshots, err := raft.NewFileSnapshotStore(raftDir, retainSnapshotCount, os.Stderr)

```

NewFileSnapshotStore()函数支持3个参数。也就是说，除了指定存储路径（raftDir），还要指定需要保留的快照副本的数量(retainSnapshotCount)，以及日志输出的方式。 **一般而言，将日志输出到标准错误IO就可以了。**

最后一个Transport指的是Raft集群内部节点之间的通信机制，节点之间需要通过这个通道来进行日志同步、领导者选举等等。Hashicorp Raft支持两种方式：

- 一种是基于TCP协议的TCPTransport，可以跨机器跨网络通信的；
- 另一种是基于内存的InmemTransport，不走网络，在内存里面通过Channel来通信。

**在生产环境中，我建议你使用TCPTransport，** 使用TCP进行网络通讯，突破单机限制，提升集群的健壮性和容灾能力。具体代码实现如下：

```
addr, err := net.ResolveTCPAddr("tcp", raftBind)
transport, err := raft.NewTCPTransport(raftBind, addr, maxPool, timeout, os.Stderr)

```

NewTCPTransport()函数支持5个参数，也就是，指定创建连接需要的信息。比如，要绑定的地址信息（raftBind、addr）、连接池的大小（maxPool）、超时时间（timeout），以及日志输出的方式，一般而言，将日志输出到标准错误IO就可以了。

以上就是这6个参数的详细内容了，既然我们已经了解了这些基础信息，那么如何使用NewRaft()函数呢？其实，你可以在代码中直接调用NewRaft()函数，创建Raft节点对象，就像下面的样子：

```
raft, err := raft.NewRaft(config, (*storeFSM)(s), logStore, stableStore, snapshots, transport)

```

接口清晰，使用方便，你可以亲手试一试。

现在，我们已经创建了Raft节点，打好了基础，但是我们要实现的是一个多节点的集群，所以，创建一个节点是不够的，另外，创建了节点后，你还需要让节点启动，当一个节点启动后，你还需要创建新的节点，并将它加入到集群中，那么具体怎么操作呢？

## 如何增加集群节点

集群最开始的时候，只有一个节点，我们让第一个节点通过bootstrap的方式启动，它启动后成为领导者：

```
raftNode.BootstrapCluster(configuration)

```

BootstrapCluster()函数只支持一个参数，也就是Raft集群的配置信息，因为此时只有一个节点，所以配置信息为这个节点的地址信息。

后续的节点在启动的时候，可以通过向第一个节点发送加入集群的请求，然后加入到集群中。具体来说，先启动的节点（也就是第一个节点）收到请求后，获取对方的地址（指Raft集群内部通信的TCP地址），然后调用AddVoter()把新节点加入到集群就可以了。具体代码如下：

```
raftNode.AddVoter(id,
            addr, prevIndex, timeout)

```

AddVoter()函数支持4个参数，使用时，一般只需要设置服务器ID信息和地址信息 ，其他参数使用默认值0，就可以了：

- id（服务器ID信息）；
- addr（地址信息）；
- prevIndex（前一个集群配置的索引值，一般设置为0，使用默认值）；
- timeout（在完成集群配置的日志项添加前，最长等待多久，一般设置为0，使用默认值）。

当然了，也可以通过AddNonvoter()，将一个节点加入到集群中，但不赋予它投票权，让它只接收日志记录，这个函数平时用不到，你只需知道有这么函数，就可以了。

在这里，我想补充下，早期版本中的用于增加集群节点的函数，AddPeer()函数，已废弃，不再推荐使用。

你看，在创建集群或者扩容时，我们尝试着增加了集群节点，但一旦出现不可恢复性的机器故障或机器裁撤时，我们就需要移除节点，进行节点替换，那么具体怎么做呢？

## 如何移除集群节点

我们可以通过RemoveServer()函数来移除节点，具体代码如下：

```
raftNode.RemoveServer(id, prevIndex, timeout)

```

RemoveServer()函数支持3个参数，使用时，一般只需要设置服务器ID信息 ，其他参数使用默认值0，就可以了：

- id（服务器ID信息）；
- prevIndex（前一个集群配置的索引值，一般设置为0，使用默认值）；
- timeout（在完成集群配置的日志项添加前，最长等待多久，一般设置为0，使用默认值）。

我要强调一下，RemoveServer()函数必须在领导者节点上运行，否则就会报错。这一点，很多同学在实现移除节点功能时会遇到，所以需要注意一下。

最后，我想补充下，早期版本中的用于移除集群节点的函数，RemovePeer()函数也已经废弃了，不再推荐使用。

关于如何移除集群节点的代码实现，也比较简单易用，通过服务器ID信息，就可以将对应的节点移除了。除了增加和移除集群节点，在实际场景中，我们在运营分布式系统时，有时需要查看节点的状态。那么该如何查看节点状态呢？

## 如何查看集群节点状态

在分布式系统中，日常调试的时候，节点的状态信息是很重要的，比如在Raft分布式系统中，如果我们想抓包分析写请求，那么必须知道哪个节点是领导者节点，它的地址信息是多少，因为在Raft集群中，只有领导者能处理写请求。

那么在Hashicorp Raft中，如何查看节点状态信息呢？

我们可以通过Raft.Leader()函数，查看当前领导者的地址信息，也可以通过Raft.State()函数，查看当前节点的状态，是跟随者、候选人，还是领导者。不过你要注意，Raft.State()函数返回的是RaftState格式的信息，也就是32位无符号整数，适合在代码中使用。 **如果想在日志或命令行接口中查看节点状态信息，我建议你使用RaftState.String()函数，** 通过它，你可以查看字符串格式的当前节点状态。

为了便于你理解，我举个例子。比如，你可以通过下面的代码，判断当前节点是否是领导者节点：

```
func isLeader() bool {
       return raft.State() == raft.Leader
}

```

了解了节点状态，你就知道了当前集群节点之间的关系，以及功能和节点的对应关系，这样一来，你在遇到问题，需要调试跟踪时，就知道应该登录到哪台机器去调试分析了。

## 内容小结

本节课我主要以“集群节点”为核心，带你了解了Hashicorp Raft的常用API接口，我希望你明确的重点如下：

1. 除了提到的raft-boltdb做作为LogStore和StableStore，也可以调用NewInmemStore()创建内存型存储，在测试时比较方便，重新执行程序进行测试时，不需要手动清理数据存储。

2. 你还可以通过NewInmemTransport()函数，实现内存型通讯接口，在测试时比较方便，将集群通过内存进行通讯，运行在一台机器上。

3. 你可以通过Raft.Stats()函数，查看集群的内部统计信息，比如节点状态、任期编号、节点数等，这在调试或确认节点运行状况的时候很有用。


我以集群节点为核心，讲解了Hashicorp Raft常用的API接口，相信现在你已经掌握这些接口的用法了，对如何开发一个分布式系统，也有了一定的感觉。既然学习是为了使用，那么我们学完这些内容，也应该用起来才是，所以，为了帮你更好地掌握Raft分布式系统的开发实战技巧，我会用接下来两节课的时间，以分布式KV系统开发实战为例，带你了解Raft的开发实战技巧。

## 课堂思考

我提到了一些常用的API接口，比如创建Raft节点、增加集群节点、移除集群节点、查看集群节点状态等，你不妨思考一下，如何创建一个支持InmemTransport的Raft节点呢？欢迎在留言区分享你的看法，与我一同讨论。

最后，感谢你的阅读，如果这篇文章让你有所收获，也欢迎你将它分享给更多的朋友。