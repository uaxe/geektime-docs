你好，我是徐文浩。这节课，我们继续来解读Megastore的论文。

在上一讲里，我们了解了Megastore的设计目标和整体架构。Megastore虽然定了一个雄心勃勃的设计目标，但是当我们深入它的整体架构的时候，发现它还是根据实际的应用场景做了种种的妥协。

Megastore把数据按照分区划分成了很多“小数据库”，来解决Paxos算法的单节点性能瓶颈问题。而针对数据库事务，Megastore支持的是 **单个实体组内的一阶段事务**。一旦要跨实体组，要么就要选择两阶段事务，要么就要采用并非事务性的异步消息机制。所以，Megastore虽然支持了SQL形式的接口，但是实际在应用中，仍然需要我们针对自己的数据模型进行精心的设计。

那么，这一讲，我们就看看Megastore的数据模型是怎么样的，它在底层又是如何使用Bigtable来存储数据的，它实现的实体组层面的事务又是怎么一回事儿。

在学完这一讲之后，希望你能够发现，其实Megastore并不神秘。通过有效利用Bigtable本身的各个特性，Megastore就已经能够实现很多，原先我们觉得在分布式环境下相对复杂的特性了。当然，这些特性也作出了种种妥协，使得Megastore并不能成为分布式数据库的终极方案。

事实上，与其说Megastore是一个独立的分布式数据库方案，不如说它更像一个Bigtable上的应用层的封装。那么在深入了解了Megastore的数据模型之后，相信你能够学会善用现有的系统，利用好现有系统的各种特性，就能有效组合出各类原先觉得难以做到的数据库高级特性。

## 实体组到底是什么？

实体组这个名字，我们在上一讲里，就已经反复提过很多次了。我们给出了一个抽象的概念，说它是一系列会经常共同访问的数据，也给出了一些像是用户和他的订单这样的例子。那么这一讲，我们就深入来看看，实体组到底是个什么东西。

```scala
CREATE SCHEMA PhotoApp

CREATE TABLE User {
  required int64 user_id;
  required string name;
} PRIMARY KEY(user_id), ENTITY GROUP ROOT;

CREATE TABLE Photo {
  required int64 user_id;
  required int32 photo_id;
  required int64 time;
  required string full_url;
  optional string thumbnail_url;
  repeated string tag;
} PRIMARY KEY(user_id, photo_id),
  IN TABLE user,
  ENTITY GROUP KEY(user_id) REFERENCES User;

CREATE LOCAL INDEX PhotosByTime
  ON Photo(user_id, time);

CREATE GLOBAL INDEX PhotosByTag
  ON Photo(tag) STORING (thumbnail_url);

```

> 论文中的图3，一个照片分享服务的示例Schema。

我在这里列出了论文中的图3，里面是一个最简单的实体组的示例Schema。其中包含了这些信息。

首先是定义了一个叫做PhotoApp的Schema，你可以认为是定义了数据库里的一个库（database）。

然后定义了一张叫做User的表，并且定义其中的user\_id是主键，并且定义了这个表是 **实体组（Entity Group）的一个根（Root）**。一条User表的记录，就代表了一个用户。

接着，定义了一张叫做Photo的表，其中的主键是user\_id和photo\_id两个字段的组合。并且， **这张表是关联到前面的User表这个根上的。这个挂载，是通过user\_id这个字段关联起来的。** 这个关联关系，就是我们上一讲所说的“挂载”。

实际上，我们可以有多个表，都关联到User表这个根上。而所谓的实体组，在逻辑上就是一张根表A，并且其他表可以通过外键，关联到根表A的主键上。并且，这个关联是可以层层深入的。比如我们还可以再定义一个表，叫做PhotoMeta，里面可以再通过user\_id和photo\_id，再关联到Photo表上。

最后，Schema里分别建立了两个索引：

- 一个是叫做PhotosByTime的 **本地索引（Local Index）**，索引的是Photo表里user\_id和time字段的组合；
- 另一个，是叫做PhotosByTag的 **全局索引（Global Index）**，索引的是Photo表里的Tag这个字段，并且它专门设置了一个特定的STORING参数，指向了Photo表里的thumbnaill这个字段。

如果你仔细看一下这个Schema，你会发现其实这个Schema的定义，更像是我们前面见过的Thrift或者Protobuf的定义文件。每个字段不仅有类型，还有是否是required以及optional，并且我们可以定义repeated的字段，也就是有某一个字段在某一条记录里面是List。

这个其实是我们在大数据系统中常见的一种技术方案。 **为了减少数据需要跨越特定的服务器进行Join，不如直接支持嵌套的List类型的字段。** 而Megastore也直接使用了Protobuf的Schema，使得跨语言跨团队使用Megastore变得更加容易了。

### 实体组的数据布局

抛开这些题外话，我们一起看看为什么在一个实体组内，我们可以让数据经常共同访问，而跨越实体组就不合适呢？

其实只要观察一下上面的这个示例Schema，在Bigtable内是如何存储的，你自己就能得出答案。

![图片](https://static001.geekbang.org/resource/image/40/5b/40d23c0b8a626a9c19d8a363d779a15b.jpg?wh=1920x750)

我把论文里面的图5，也就是前面的PhotoApp表在Bigtable里是怎么存储的放在了这里，并把示例数据分别标成了绿色和蓝色。对于PhotoApp里的User和Photo这两张表，是存放在同一张Bigtable的表里的，其中，绿色部分的数据是来自User表的，而蓝色部分的数据来自Photo表。

可以看到，我们是直接拿User表的主键user\_id，作为了Bigtable里的行键。而对于Photo表，我们是拿user\_id和photo\_id组合作为行键，存放在同一张表里。因为Bigtable里面的数据，是按照行键连续排列的。所以，同一个User下的Photo的数据记录，会连续存储在对应的User记录后面。

在前面的 [第9讲](https://time.geekbang.org/column/article/423602) 解读Bigtable这篇论文的时候，我们说过在Bigtable里，数据是按照行键分区的，实际的数据存储，也是按照行键连续存储的。并且，当我们用一个行键去Bigtable里面查询数据的话，Bigtable会有Block Cache，也就是把底层的SSTable的整个Block都获取回来。而这个里面，其实就会包含当前行键前后连续行键所包含的数据。

所以，当我们去查询某一条User记录的时候，会有非常高的概率，直接把User记录下的Photo记录一并获取到，而不需要再次访问对应的硬盘。自然读写的性能，就会比随机布局的数据要好上很多。在Megastore的论文里，这样的数据布局是被称之为 **对Key进行预Join**（Pre-Joining with Keys）。

除此之外，为了避免热点问题，Megastore支持你对数据表添加一个SCATTER参数，添加了这个参数之后，所有的行键都会带上Root实体记录的Key的哈希值。这样，虽然同一个实体组里的数据还是连续排列的，但是同一张表的两个连续实体组的Root记录的Key，就不一定存储在一个服务器上了。

而数据库里的每一个列也非常简单，我们就直接使用Bigtable的Column就好了。而且Megastore这样混合一个实体组里的多个表的结构，其实是非常适合Bigtable的。因为Bigtable的列是稀疏的，对于不存在的列，并不需要存储，当然也不会占用存储空间。这样，虽然一个Bigtable里的表，实际存放了一套实体组的Schema下的很多张表，但是并不会存在存储上浪费的情况。

### Megastore的索引

了解了Megastore的实际数据是怎么存储在Bigtable里的，我们再来看看它的索引是怎么回事儿。

Megastore的索引，分成了两种类型，一个是本地索引，另一种叫做全局索引。 **本地索引的数据，是直接存储在实体组“内部”的**，它是我们已经确定是哪一个实体组的情况下，去寻找具体的记录位置。这个，你可以看看我在上一讲里，放过的论文图2里面索引的位置。

![图片](https://static001.geekbang.org/resource/image/14/a4/14e7e9d6be877ffaac50a290b87beda4.jpg?wh=1920x1080)

而我们通过看前面的Schema的例子也会非常清楚，PhotosByTime这个本地索引，需要通过user\_id和time这样两个字段才能查询到。其实，也就是我们先通过user\_id，知道是哪一个User实体组，再在这个实体组里查询数据。

```scala
CREATE LOCAL INDEX PhotosByTime
  ON Photo(user_id, time);

```

> 本地索引，索引中需要包含实体组的根的主键信息。

而另一种全局索引，就不需要预先知道是哪一个实体组了，但是它的更新就不是实时的了。最新的数据更新，不一定会在全局索引里反映出来，这也是为什么论文里说， **全局索引是弱一致的**。我们也不难猜到，全局索引应该是异步更新的。

#### 索引优化

除了把索引区分成本地索引和全局索引之外，Megastore在索引上，还花了更多的功夫做了三点改造，让Megastore支持了更加复杂的索引功能。

**第一点，是Megastore支持在索引中存储数据。**

传统的数据库索引里，往往只存储指向具体数据记录的主键。这就意味着，当我们查询数据的时候，需要两次请求：第一次请求是查询索引，拿到对应数据记录的主键；第二次请求是再通过主键，去查询对应的整条数据，然后拿到我们需要的字段的值。

而在Megastore里，你可以通过一个STORING语句，指定索引里存储下对应的数据记录的某一个字段的值。这样，我们的查询只需要检索索引，就能拿到需要字段的值。

这个优化听起来微不足道，但是在分布式数据库里其实作用很大。在一般的单机数据库里，索引和数据都是在同一台服务器上，所以索引里不存储数据，只是多了硬盘随机访问的压力。 **但是在分布式数据库里，如果我们的索引和数据不存储在一个节点上，就意味着还会多一次网络往返，进一步会拉低整个集群的性能。** 

![图片](https://static001.geekbang.org/resource/image/36/ec/365ab4771ec9dd7e4770b24b47d6a3ec.jpg?wh=1920x1805)

不过，需要显示指定索引里存放哪一个字段，也意味着开发人员需要预先判定，业务中未来特定的查询会使用到的字段值，其实这也给开发人员带来了很多挑战。

**第二点，是Megastore支持为repeated类型的字段建立索引（Repeated Indexes）。**

这里对应的例子，仍然是前面的PhotosByTag索引，它对应的索引字段，是Photo这个实体里的tag这个字段。tag这个字段，在Photos表里是申明为repeated的，也就是一张Photo表里面可以有多个Tag。

而Megastore会为里面的每一个tag都记录一条索引。这样，我们就可以通过索引， **反向查询** 到某一个tag关联到的所有的Photo记录。Megastore这种支持repeated字段的索引，使得我们不需要为这样的单个repeated字段，去单独建立一张子表。无论这张子表是一张独立的表，还是像Megastore的实体组一样挂载在Root表上，都很浪费存储空间，也让这个数据表结构变得过于复杂，不容易理解。

```scala
CREATE TABLE Photo {
  required int64 user_id;
  required int32 photo_id;
  required int64 time;
  required string full_url;
  optional string thumbnail_url;
  repeated string tag;
} PRIMARY KEY(user_id, photo_id),
  IN TABLE user,
  ENTITY GROUP KEY(user_id) REFERENCES User;

CREATE GLOBAL INDEX PhotosByTag
  ON Photo(tag) STORING (thumbnail_url);

```

> 为repeated字段建立索引，就是为里面的每一个值都建立了一条索引记录。

**最后一点，是Megastore提供了对于内联索引（Inline Indexes）的支持。**

这个索引类型，是为了帮助父实体（Parent Entity）能够快速访问子实体（Child Entity）的某些字段。

还是回到论文中的例子，我们可以把Schema中定义的本地索引，PhotosByTime这个原本索引Photo实体的索引，变成User实体的内联索引。这样，User表实际上会相当于多了一个repeated的虚拟字段（virtual）。而既然是repeated字段，那它其实就是一个List。List里的每一个结构体，都存放了两个信息，一个是PhotosByTime里面的time信息，另一个是对应的这个time，对应的是Photos里的哪一条记录。

这样，通过在父实体里添加了一个虚拟字段，我们对于子实体里的数据查询，直接在父实体里就能够完成了，而不需要再去查询具体的索引数据。因为在应用开发的时候，比如在Instagram里，我们看一个用户最近的照片，都是先取到User这样的父实体，再根据user\_id和索引去查询它的照片信息。当有了内联索引之后，我们在第二步查询子实体数据的时候，就可以少一次索引的访问了。

![图片](https://static001.geekbang.org/resource/image/a2/85/a2a60497c47cf8e276ca35b0b9ec6585.jpg?wh=1920x821)

#### 索引实现

其实，Megastore的索引实现也并不复杂。 **每一条索引，都是作为一行数据，存储在Bigtable里的。** 这条记录的行键，就是建立索引的字段，和索引到的数据的主键的组合。我们还是回到论文里的例子来看：

```scala
CREATE LOCAL INDEX PhotosByTime
  ON Photo(user_id, time);

```

- PhotosByTime这个索引由user\_id和time这两个字段组成；
- 并且它索引的是Photo这个表，对应的Photo表的主键就是user\_id和photo\_id；
- 那么，索引这一行的行键，就是 ((user\_id, time), (user\_id, photo\_id)) 这样的一个组合；
- 而如果我们的索引，指向的是一个repeated的字段，比如tags，那么每一个tag都会有一行数据。比如有三个tag，分别是 \[tag1, tag2, tag3\]，我们的索引，就会有三条记录，分别是 (tag1, (user\_id, time)), (tag2, (user\_id, time)) 和 (tag3, (user\_id, time))。

![图片](https://static001.geekbang.org/resource/image/08/a3/08f8dfb669dbf911bc0af9574a4c46a3.jpg?wh=1920x501)

![图片](https://static001.geekbang.org/resource/image/79/66/79b273c49e69cb24794cba849ea94866.jpg?wh=1920x850)

而这样的索引，其实是充分利用了Bigtable的特性。因为Bigtable的行数据，是按照行键范围分区，连续的数据会存储在一起。所以，无论是根据索引值进行范围内查询一段数据，还是随机查询某一条数据，都会很容易。

可以看到，这个索引的实现，也和前面的实体组的数据布局一样，是充分利用了Bigtable的特性的一个很好的应用。

## Megastore的事务与隔离性

在聊完了Megastore的索引之后，我们最后来看看Megastore的事务和隔离性是怎么做的。因为Megastore只支持同一个实体组下的一阶段事务，那我们就 **可以把同一个实体组下的所有数据行，看成是一个抽象的“迷你数据库”**。在这个迷你数据库上，Megastore也支持了“可串行化”的ACID语义。

我们先来回顾一下数据库的隔离性。

在课程的 [第13讲](https://time.geekbang.org/column/article/428116)，我们深入讲解了数据库的ACID里的隔离性I（Isolation），其实其他三个ACD都不复杂，可以说大部分我们面临的复杂性，都在隔离性这个I上。而为了让数据库对应用层来说尽量简单易用，我们希望数据库的隔离性能够做到“可串行化”，也就是在外部应用看起来，每个事务是一个一个在数据库里面提交的。这样的隔离性，会使得我们的数据库事务不会遇到脏读、不可重复读、幻读等各种异常情况。

那么，要实现“可串行化”的隔离性，当然不只有真的把所有的事务排一个队，一个个来执行这样一种办法。这样的方式，就彻底丧失了数据库事务的并发性，会大大拖累数据库的性能。现代的关系型数据库，都是采用一种叫做 **MVCC**（Multiversion Concurrency Control）的机制来实现，中文名称叫做多版本并发控制。

这个机制，通俗来讲，就是数据库中的数据会有多个历史版本。你的每一次事务请求，都会拿到当前最新已经提交的那个版本的快照， **在整个事务提交的时候，会检查当前数据库里数据的最新版本，是否和你拿到的快照版本一致**。

如果一致的话，数据提交会成功，并且数据库里的版本会更新。而当有两个并发的数据库事务都会去读或者写同一份数据的时候，先尝试提交的A事务的会成功。后尝试提交的B事务，因为数据的最新版本已经变了，就会失败。而当你有一个事务正在提交，或者数据写入到一半，另一个读取事务的请求并不会读到你写到一半的数据，而是读取上一个完成提交的事务的一个快照。

![图片](https://static001.geekbang.org/resource/image/59/6d/592524068b954a387ef1a4d0d2yyd66d.jpg?wh=1920x1080)

看完这个对于MVCC机制的描述，不知道你是不是和我一样，发现Bigtable的底层数据读写机制，和它非常匹配。因为Bigtable天然会存储数据的多个版本，每一次的数据写入，都是追加了一个新版本，而不是把原来的数据覆盖掉。这样我们就可以把每一个事务提交时的时间戳，用作MVCC机制里面的版本。

Megastore的一个实体组，可能包含多行的数据。而你就要问了：可是Bigtable本身只支持单行数据的事务呀？别着急，我们完全可以使用时间戳这个版本信息，来实现基于MVCC的事务性和隔离性。

我们在 **提交事务的时候，需要指定一个时间戳**，而不是让每一行的数据更新都使用当前的时间戳。然后我们在读取数据的时候，只需要找到最后成功提交的事务的时间戳，我们读取这个时间戳版本的数据，就是最新的版本。

而如果这个时候，有一个事务提交到一半，一个实体组里的一部分数据更新了，另一部分数据还没有来得及更新，也不要紧，我们的读请求并不会读到这个数据。

![图片](https://static001.geekbang.org/resource/image/5e/c8/5e5634dfb01c151ffbee2d4bb5c9a3c8.jpg?wh=1920x980)

正是因为这个时间戳机制的存在，Megastore对于读取数据提供了current，snapshot以及 inconsistent三种模式。这三种模式其实看名字就很明白了：

- **current** 就是读取最新版本的数据。在读数据之前，Megastore的事务系统，会先确认已经提交的事务都已经应用成功。然后，事务系统会读取最新事务对应的时间戳的数据版本。
- **snapshot**，则不会等待当前是否有已经提交的事务应用完成，而是直接返回上一个完全应用的事务对应的数据版本。
- **inconsistent**，则是完全忽视事务系统的日志信息，直接获取到Bigtable里面最新的数据就好了。自然，在这个机制下，我们就会读到“不一致”的数据，因为我们可能在事务提交到一半的时候，读取到不同行的不同版本的数据。

看到这里相信你也猜到了，Megastore在Bigtable本身的存储系统之外，添加了一个独立的事务系统。而这个事务系统，其实就是我们在Chubby里面所说的，是一个 [复制日志的状态机](https://time.geekbang.org/column/article/428116)。而我们的事务提交，是通过下面这样5个步骤来进行的：

1. **读**（Read）：我们先要获取到时间戳，以及最后一次提交的事务的日志的位置。
2. **应用层的逻辑**（Application Logic）：我们要从Bigtable读取数据，并且把所有需要的写操作，收集到一条日志记录（log entry）中。
3. **提交事务**（Commit）：通过Paxos算法，我们要和其他数据中心对应的副本，达成一致，把这个日志记录追加到日志的最后。
4. **应用事务**（Apply）：也就是把实际对于实体和索引的修改，写入到Bigtable里。
5. **清理工作**（Clean UP）：也就是把不需要的数据删除掉。

你可以看到，其中的第3步和第4步，其实就是在Bigtable之外，又包装了一层Bigtable的单行事务机制。第3步相当于是一个预写日志（Write-Ahead-Log），而第4步，像是Bigtable里的MemTable+SSTable，我们的变更需要再更新到对应的内存和存储系统里去。

而第3、4步之间的这个 **时间差**，也是为什么我们的数据需要区分是读取current版本，还是读取snapshot版本。current版本，就是预写日志已经完成，但是数据还没有更新到Bigtable里，那我们就等待数据更新完到Bigtable里，再获取这个最新的数据。snapshot版本，则不会等待预写日志已经完成，但是数据还没有更新到Bigtable里的数据，而是直接获取上一个已经更新到Bigtable的数据版本。

所以，如果我们所有的数据读，都是用current读，我们就能保障“可线性化”，但是它在有些情况下的延时，会比snapshot读长一些，性能会差一些。

**那么，当我们出现并发写的时候怎么办呢？** 请你回头去看一下前面的第1步，其中会获取到最新的日志位置。两个并发写入，会在第3步，去竞争写入同一个日志位置，但是只有一个会成功。而失败的那个，就会从头来过，重新拿到新的最新日志位置，来发起事务。

看到这里，相信你就弄明白，Megastore是如何通过一个只支持单行事务的Bigtable，来实现实体组内的事务机制的了。

至于消息机制、两阶段提交，我们已经在上一讲以及更之前的Chubby论文讲解中深入剖析过了，在这里我们就不再一一重复了。

## 小结

好了，这一讲，我们一起深入了解了Megastore的数据模型是怎么样的。我们发现，无论是Megastore的实体组的设计，还是它的索引的实现，都是在充分利用Bigtable这个底层存储系统。

**实体组的设计**，其实是把多张数据表存放在一个Bigtable的表的方式，来让根据一个主键能够关联起来的数据，在物理上连续排布在一起。这样无论是读写数据，都有很强的局部性，数据读写的性能都会大大增强。而对应的 **索引**，其实也是Bigtable里一行行的记录，同样是根据Bigtable行键连续分布的特性，使得根据索引的范围查找和随机查找都变得很容易。

Megastore在数据库事务层面的实现，同样是这样。和其他数据库一样，Megastore采用了 **MVCC** 这样的机制，来实现事务中对于冲突资源的处理。而Bigtable又天然地通过每个数据版本都有的TimeStamp（时间戳），很好地支持了这样的机制。

可以看到， **Megastore与其说是一个数据库系统，不如说是对Bigtable的特性进行了合理封装后的一个数据应用层。** 固然，这些特性的使用，使得Megastore支持了很多有用的特性，比如特定实体组内的事务、数据库Schema、本地和全局的索引。

但是我们同时也要看到，这些特性也使得Megastore **更像一个专有系统**，而不是一个我们熟悉的标准的关系型数据库。我们必须熟悉Megastore的这一系列底层设计，才能设计出一个合理的数据模型。而且这个数据模型，往往和我们熟悉的关系模型也会有差异。这些不足之处也限制了Megastore的推广和应用，最终Megastore也只能算是分布式数据库发展史上的一个“过渡品”，而不是最终的解决方案。

最后，也请你做好准备进入下一讲。在下一讲里，我会讲解Megastore是如何优化Paxos算法，使得在一个跨数据中心的远距离传输的场景下，Paxos算法仍然尽可能有还算不错的性能的。

## 推荐阅读

可以看到，Megastore在数据模型和数据存储上，是重度使用了Bigtable。所以如果你对这一讲的一些内容觉得还不够清晰的话，我推荐你回头去复习一下我们对于Bigtable的讲解。

此外，对于Megastore的数据库事务部分，我为你介绍了通过MVCC的方式，来实现数据库的隔离性。如果你想对数据库的隔离性有更深入的了解，我推荐你阅读一下《数据密集型应用系统设计》的第7章的事务部分，这个对你理解事务的隔离性，特别是“MVCC是如何在数据库内部实现的”会非常有帮助。

## 思考题

这一讲里，我们讲解了Megastore的实体组数据、索引以及事务机制。在了解完了Megastore的事务机制之后，你觉得这个事务日志的数据应该存放在哪里呢？应该采用什么样的结构来存储呢？请结合你过去那么多讲课程学习的知识，给出你的想法和设计，和周围的朋友、同学、老师共同探讨、相互学习，一起进步。