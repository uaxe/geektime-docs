你好，我是吴磊。

在Spark的应用开发中，有效利用Cache往往能大幅提升执行性能。

但某一天，有位同学却和我说，自己加了Cache之后，执行性能反而变差了。仔细看了这位同学的代码之后，我吓了一跳。代码中充斥着大量的 `.cache`，无论是RDD，还是DataFrame，但凡有分布式数据集的地方，后面几乎都跟着个 `.cache`。显然，Cache滥用是执行性能变差的始作俑者。

实际上，在有些场景中，Cache是灵丹妙药，而在另一些场合，大肆使用Cache却成了饮鸩止渴。那Cache到底该在什么时候用、怎么用，都有哪些注意事项呢？今天这一讲，我们先一起回顾Cache的工作原理，再来回答这些问题。

## Cache的工作原理

在 [存储系统](https://time.geekbang.org/column/article/355081) 那一讲，我们其实介绍过RDD的缓存过程，只不过当时的视角是以MemoryStore为中心，目的在于理解存储系统的工作原理，今天咱们把重点重新聚焦到缓存上来。

Spark的Cache机制主要有3个方面需要我们掌握，它们分别是：

- 缓存的存储级别：它限定了数据缓存的存储介质，如内存、磁盘等
- 缓存的计算过程：从RDD展开到分片以Block的形式，存储于内存或磁盘的过程
- 缓存的销毁过程：缓存数据以主动或是被动的方式，被驱逐出内存或是磁盘的过程

下面，我们一一来看。

### 存储级别

Spark中的Cache支持很多种存储级别，比如MEMORY\_AND\_DISK\_SER\_2、MEMORY\_ONLY等等。这些长得差不多的字符串我们该怎么记忆和区分呢？其实， **每一种存储级别都包含3个基本要素**。

- 存储介质：内存还是磁盘，或是两者都有。
- 存储形式：对象值还是序列化的字节数组，带SER字样的表示以序列化方式存储，不带SER则表示采用对象值。
- 副本数量：存储级别名字最后的数字代表拷贝数量，没有数字默认为1份副本。

![](https://static001.geekbang.org/resource/image/4e/e2/4ecdfd4b62b1c6e151d029c38088yye2.jpeg?wh=1920*1000)

当我们对五花八门的存储级别拆解之后就会发现，它们不过是存储介质、存储形式和副本数量这3类不同基本元素的排列组合而已。我在上表中列出了目前Spark支持的所有存储级别，你可以通过它加深理解。

尽管缓存级别多得让人眼花缭乱，但实际上 **最常用的只有两个：MEMORY\_ONLY和MEMORY\_AND\_DISK，它们分别是RDD缓存和DataFrame缓存的默认存储级别**。在日常的开发工作中，当你在RDD和DataFrame之上调用 `.cache` 函数时，Spark默认采用的就是MEMORY\_ONLY和MEMORY\_AND\_DISK。

### 缓存的计算过程

在MEMORY\_AND\_DISK模式下，Spark会优先尝试把数据集全部缓存到内存，内存不足的情况下，再把剩余的数据落盘到本地。MEMORY\_ONLY则不管内存是否充足，而是一股脑地把数据往内存里塞，即便内存不够也不会落盘。不难发现， **这两种存储级别都是先尝试把数据缓存到内存**。数据在内存中的存储过程我们在 [第6讲](https://time.geekbang.org/column/article/355081) 中讲过了，这里我们再一起回顾一下。

![](https://static001.geekbang.org/resource/image/8f/e2/8fc350146a7yyb0448303d7f1f094be2.jpg?wh=3936*1818)

无论是RDD还是DataFrame，它们的数据分片都是以迭代器Iterator的形式存储的。因此，要把数据缓存下来，我们先得把迭代器展开成实实在在的数据值，这一步叫做Unroll，如步骤1所示。展开的对象值暂时存储在一个叫做ValuesHolder的数据结构里，然后转换为MemoryEntry。转换的实现方式是toArray，因此它不产生额外的内存开销，这一步转换叫做Transfer，如步骤2所示。最终，MemoryEntry和与之对应的BlockID，以Key、Value的形式存储到哈希字典（LinkedHashMap）中，如图中的步骤3所示。

当分布式数据集所有的数据分片都从Unroll到Transfer，再到注册哈希字典之后，数据在内存中的缓存过程就宣告完毕。

### 缓存的销毁过程

但是很多情况下，应用中数据缓存的需求会超过Storage Memory区域的空间供给。虽然缓存任务可以抢占Execution Memory区域的空间，但“出来混，迟早是要还的”，随着执行任务的推进，缓存任务抢占的内存空间还是要“吐”出来。这个时候，Spark就要执行缓存的销毁过程。

你不妨把Storage Memory想象成一家火爆的网红餐厅，待缓存的数据分片是一位又一位等待就餐的顾客。当需求大于供给，顾客数量远超餐位数量的时候，Spark自然要制定一些规则，来合理地“驱逐”那些尸位素餐的顾客，把位置腾出来及时服务那些排队等餐的人。

那么问题来了，Spark基于什么规则“驱逐”顾客呢？接下来，我就以同时缓存多个分布式数据集的情况为例，带你去分析一下在内存受限的情况下会发生什么。

我们用一张图来演示这个过程，假设MemoryStore中存有4个RDD/Data Frame的缓存数据，这4个分布式数据集各自缓存了一些数据分片之后，Storage Memory区域就被占满了。当RDD1尝试把第6个分片缓存到MemoryStore时，却发现内存不足，塞不进去了。

这种情况下， **Spark就会逐一清除一些“尸位素餐”的MemoryEntry来释放内存，从而获取更多的可用空间来存储新的数据分片**。这个过程叫做Eviction，它的中文翻译还是蛮形象的，就叫做驱逐，也就是把MemoryStore中那些倒霉的MemoryEntry驱逐出内存。

![](https://static001.geekbang.org/resource/image/b7/14/b73308328ef549579d02c72afb2ab114.jpg?wh=5828*1798)

回到刚才的问题，Spark是根据什么规则选中的这些倒霉蛋呢？这个规则叫作LRU（Least Recently Used），基于这个算法，最近访问频率最低的那个家伙就是倒霉蛋。因为 [LRU](https://baike.baidu.com/item/LRU/1269842?fr=aladdin) 是比较基础的数据结构算法，笔试、面试的时候经常会考，所以它的概念我就不多说了。

我们要知道的是，Spark是如何实现LRU的。这里， **Spark使用了一个巧妙的数据结构：LinkedHashMap，这种数据结构天然地支持LRU算法**。

LinkedHashMap使用两个数据结构来维护数据，一个是传统的HashMap，另一个是双向链表。HashMap的用途在于快速访问，根据指定的BlockId，HashMap以O(1)的效率返回MemoryEntry。双向链表则不同，它主要用于维护元素（也就是BlockId和MemoryEntry键值对）的访问顺序。凡是被访问过的元素，无论是插入、读取还是更新都会被放置到链表的尾部。因此，链表头部保存的刚好都是“最近最少访问”的元素。

如此一来，当内存不足需要驱逐缓存的数据块时，Spark只利用LinkedHashMap就可以做到按照“最近最少访问”的原则，去依次驱逐缓存中的数据分片了。

除此之外，在存储系统那一讲，有同学问MemoryStore为什么使用LinkedHashMap，而不用普通的Map来存储BlockId和MemoryEntry的键值对。我刚才说的就是答案了。

回到图中的例子，当RDD1试图缓存第6个数据分片，但可用内存空间不足时，Spark 会对LinkedHashMap从头至尾扫描，边扫描边记录MemoryEntry大小，当倒霉蛋的总大小超过第6个数据分片时，Spark停止扫描。

有意思的是， **倒霉蛋的选取规则遵循“兔子不吃窝边草”，同属一个RDD的MemoryEntry不会被选中**。就像图中的步骤4展示的一样，第一个蓝色的MemoryEntry会被跳过，紧随其后打叉的两个MemoryEntry被选中。

因此，总结下来，在清除缓存的过程中，Spark遵循两个基本原则：

- LRU：按照元素的访问顺序，优先清除那些“最近最少访问”的BlockId、MemoryEntry键值对
- 兔子不吃窝边草：在清除的过程中，同属一个RDD的MemoryEntry拥有“赦免权”

### 退化为MapReduce

尽管有缓存销毁这个环节的存在，Storage Memory内存空间也总会耗尽，MemoryStore也总会“驱无可驱”。这个时候，MEMORY\_ONLY模式就会放弃剩余的数据分片。比如，在Spark UI上，你时常会看到Storage Tab中的缓存比例低于100%。而我们从Storage Tab也可以观察到，在MEMORY\_AND\_DISK模式下，数据集在内存和磁盘中各占一部分比例。

这是因为对于MEMORY\_AND\_DISK存储级别来说，当内存不足以容纳所有的RDD数据分片的时候，Spark会把尚未展开的RDD分片通过DiskStore缓存到磁盘中。DiskStore的工作原理，我们在存储系统那一讲有过详细介绍，你可以回去看一看，我建议你结合DiskStore的知识把RDD分片在磁盘上的缓存过程推导出来。

因此， **相比MEMORY\_ONLY，MEMORY\_AND\_DISK模式能够保证数据集100%地物化到存储介质**。对于计算链条较长的RDD或是DataFrame来说，把数据物化到磁盘也是值得的。但是，我们也不能逢RDD、DataFrame就调用 `.cache`，因为在最差的情况下，Spark的内存计算就会退化为Hadoop MapReduce根据磁盘的计算模式。

比如说，你用DataFrame API开发应用，计算过程涉及10次DataFrame之间的转换，每个DataFrame都调用 `.cache` 进行缓存。由于Storage Memory内存空间受限，MemoryStore最多只能容纳两个DataFrame的数据量。因此，MemoryStore会有8次以DataFrame为粒度的换进换出。最终，MemoryStore存储的是访问频次最高的DataFrame数据分片，其他的数据分片全部被驱逐到了磁盘上。也就是说，平均下来，至少有8次DataFrame的转换都会将计算结果落盘，这不就是Hadoop的MapReduce计算模式吗？

当然，咱们考虑的是最差的情况，但这也能让我们体会到滥用Cache可能带来的隐患和危害了。

## Cache的用武之地

既然滥用Cache危害无穷，那在什么情况下适合使用Cache呢？我建议你在做决策的时候遵循以下2条基本原则：

- 如果RDD/DataFrame/Dataset在应用中的引用次数为1，就坚决不使用Cache
- 如果引用次数大于1，且运行成本占比超过30%，应当考虑启用Cache

第一条很好理解，我们详细说说第二条。这里咱们定义了一个新概念： **运行成本占比。它指的是计算某个分布式数据集所消耗的总时间与作业执行时间的比值**。我们来举个例子，假设我们有个数据分析的应用，端到端的执行时间为1小时。应用中有个DataFrame被引用了2次，从读取数据源，经过一系列计算，到生成这个DataFrame需要花费12分钟，那么这个DataFrame的运行成本占比应该算作：12 \* 2 / 60 = 40%。

你可能会说：“作业执行时间好算，直接查看Spark UI就好了，DataFrame的运行时间怎么算呢？”这里涉及一个小技巧，我们可以从现有应用中 把DataFrame的计算逻辑单拎出来，然后利用Spark 3.0提供的Noop来精确地得到DataFrame的运行时间。假设df是那个被引用2次的DataFrame，我们就可以把df依赖的所有代码拷贝成一个新的作业，然后在df上调用Noop去触发计算。Noop的作用很巧妙，它只触发计算，而不涉及落盘与数据存储，因此，新作业的执行时间刚好就是DataFrame的运行时间。

```
//利用noop精确计算DataFrame运行时间
df.write
.format(“noop”)
.save()

```

你可能会觉得每次计算占比会很麻烦，但只要你对数据源足够了解、对计算DataFrame的中间过程心中有数了之后，其实不必每次都去精确地计算运行成本占比，尝试几次，你就能对分布式数据集的运行成本占比估摸得八九不离十了。

## Cache的注意事项

弄清楚了应该什么时候使用Cache之后，我们再来说说Cache的注意事项。

首先，我们都知道， `.cache` 是惰性操作，因此在调用 `.cache` 之后，需要先用Action算子触发缓存的物化过程。但是，我发现很多同学在选择Action算子的时候很随意，first、take、show、count中哪个顺手就用哪个。

这肯定是不对的， **这4个算子中只有count才会触发缓存的完全物化，而first、take和show这3个算子只会把涉及的数据物化**。举个例子，show默认只产生20条结果，如果我们在.cache之后调用show算子，它只会缓存数据集中这20条记录。

选择好了算子之后，我们再来讨论一下怎么Cache这个问题。你可能会说：“这还用说吗？在RDD、DataFrame后面调用 `.cache` 不就得了”。还真没这么简单，我出一道选择题来考考你，如果给定包含数十列的DataFrame df和后续的数据分析，你应该采用下表中的哪种Cache方式？

```
val filePath: String = _
val df: DataFrame = spark.read.parquet(filePath)

//Cache方式一
val cachedDF = df.cache
//数据分析
cachedDF.filter(col2 > 0).select(col1, col2)
cachedDF.select(col1, col2).filter(col2 > 100)

//Cache方式二
df.select(col1, col2).filter(col2 > 0).cache
//数据分析
df.filter(col2 > 0).select(col1, col2)
df.select(col1, col2).filter(col2 > 100)

//Cache方式三
val cachedDF = df.select(col1, col2).cache
//数据分析
cachedDF.filter(col2 > 0).select(col1, col2)
cachedDF.select(col1, col2).filter(col2 > 100)

```

我们都知道，由于Storage Memory内存空间受限，因此Cache应该遵循 **最小公共子集原则**，也就是说，开发者应该仅仅缓存后续操作必需的那些数据列。按照这个原则，实现方式1应当排除在外，毕竟df是一张包含数十列的宽表。

我们再来看第二种Cache方式，方式2缓存的数据列是 `col1` 和 `col2`，且 `col2` 数值大于0。第一条分析语句只是把 `filter` 和 `select` 调换了顺序；第二条语句 `filter` 条件限制 `col2` 数值要大于100，那么，这个语句的结果就是缓存数据的子集。因此，乍看上去，两条数据分析语句在逻辑上刚好都能利用缓存的数据内容。

但遗憾的是，这两条分析语句都会跳过缓存数据，分别去磁盘上读取Parquet源文件，然后从头计算投影和过滤的逻辑。这是为什么呢？究其缘由是， **Cache Manager要求两个查询的Analyzed Logical Plan必须完全一致，才能对DataFrame的缓存进行复用**。

Analyzed Logical Plan是比较初级的逻辑计划，主要负责AST查询语法树的语义检查，确保查询中引用的表、列等元信息的有效性。像谓词下推、列剪枝这些比较智能的推理，要等到制定Optimized Logical Plan才会生效。因此，即使是同一个查询语句，仅仅是调换了 `select` 和 `filter` 的顺序，在Analyzed Logical Plan阶段也会被判定为不同的逻辑计划。

因此，为了避免因为Analyzed Logical Plan不一致造成的Cache miss，我们应该采用第三种实现方式，把我们想要缓存的数据赋值给一个变量，凡是在这个变量之上的分析操作，都会完全复用缓存数据。你看，缓存的使用可不仅仅是调用 `.cache` 那么简单。

除此之外，我们也应当及时清理用过的Cache，尽早腾出内存空间供其他数据集消费，从而尽量避免Eviction的发生。一般来说，我们会用.unpersist来清理弃用的缓存数据，它是.cache的逆操作。unpersist操作支持同步、异步两种模式：

- 异步模式：调用unpersist()或是unpersist(False)
- 同步模式：调用unpersist(True)

在异步模式下，Driver把清理缓存的请求发送给各个Executors之后，会立即返回，并且继续执行用户代码，比如后续的任务调度、广播变量创建等等。在同步模式下，Driver发送完请求之后，会一直等待所有Executors给出明确的结果（缓存清除成功还是失败）。各个Executors清除缓存的效率、进度各不相同，Driver要等到最后一个Executor返回结果，才会继续执行Driver侧的代码。显然，同步模式会影响Driver的工作效率。因此，通常来说，在需要主动清除Cache的时候，我们往往采用异步的调用方式，也就是调用unpersist()或是unpersist(False)。

## 小结

想要有效避免Cache的滥用，我们必须从Cache的工作原理出发，先掌握Cache的3个重要机制，分别是存储级别、缓存计算和缓存的销毁过程。

对于存储级别来说，实际开发中最常用到的有两个，MEMORY\_ONLY和MEMORY\_AND\_DISK，它们分别是RDD缓存和DataFrame缓存的默认存储级别。

对于缓存计算来说，它分为3个步骤，第一步是Unroll，把RDD数据分片的Iterator物化为对象值，第二步是Transfer，把对象值封装为MemoryEntry，第三步是把BlockId、MemoryEntry价值对注册到LinkedHashMap数据结构。

另外，当数据缓存需求远大于Storage Memory区域的空间供给时，Spark利用LinkedHashMap数据结构提供的特性，会遵循LRU和兔子不吃窝边草这两个基本原则来清除内存空间：

- LRU：按照元素的访问顺序，优先清除那些“最近最少访问”的BlockId、MemoryEntry键值对
- 兔子不吃窝边草：在清除的过程中，同属一个RDD的MemoryEntry拥有“赦免权”

其次，我们要掌握使用Cache的一般性原则和注意事项，我把它们总结为3条：

- 如果RDD/DataFrame/Dataset在应用中的引用次数为1，我们就坚决不使用Cache
- 如果引用次数大于1，且运行成本占比超过30%，我们就考虑启用Cache（其中，运行成本占比的计算，可以利用Spark 3.0推出的noop功能）
- Action算子要选择count才能完全物化缓存数据，以及在调用Cache的时候，我们要把待缓存数据赋值给一个变量。这样一来，只要是在这个变量之上的分析操作都会完全复用缓存数据。

## 每日一练

1. 你能结合DiskStore的知识，推导出MEMORY\_AND\_DISK模式下RDD分片缓存到磁盘的过程吗？
2. 你觉得，为什么Eviction规则要遵循“兔子不吃窝边草”呢？如果允许同一个RDD的MemoryEntry被驱逐，有什么危害吗？
3. 对于DataFrame的缓存复用，Cache Manager为什么没有采用根据Optimized Logical Plan的方式，你觉得难点在哪里？如果让你实现Cache Manager的话，你会怎么做？

期待在留言区看到你的思考和答案，如果你的朋友也正在为怎么使用Cache而困扰，也欢迎你把这一讲转发给他。我们下一讲见！