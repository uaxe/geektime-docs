你好，我是吴磊。

上一讲我们说到，在数据关联场景中，广播变量是克制Shuffle的杀手锏，用Broadcast Joins取代Shuffle Joins可以大幅提升执行性能。但是，很多同学只会使用默认的广播变量，不会去调优。那么，我们该怎么保证Spark在运行时优先选择Broadcast Joins策略呢？

今天这一讲，我就围绕着数据关联场景，从配置项和开发API两个方面，帮你梳理出两类调优手段，让你能够游刃有余地运用广播变量。

## 利用配置项强制广播

我们先来从配置项的角度说一说，有哪些办法可以让Spark优先选择Broadcast Joins。在Spark SQL配置项那一讲，我们提到过spark.sql.autoBroadcastJoinThreshold这个配置项。它的设置值是存储大小，默认是10MB。它的含义是， **对于参与Join的两张表来说，任意一张表的尺寸小于10MB，Spark就在运行时采用Broadcast Joins的实现方式去做数据关联。** 另外，AQE在运行时尝试动态调整Join策略时，也是基于这个参数来判定过滤后的数据表是否足够小，从而把原本的Shuffle Joins调整为Broadcast Joins。

![](https://static001.geekbang.org/resource/image/69/89/697cccb272fc8863f40bb7c465f53c89.jpeg?wh=1785*348)

为了方便你理解，我来举个例子。在数据仓库中，我们经常会看到两张表：一张是订单事实表，为了方便，我们把它记成Fact；另一张是用户维度表，记成Dim。事实表体量很大在100GB量级，维度表很小在1GB左右。两张表的Schema如下所示：

```
//订单事实表Schema
orderID: Int
userID: Int
trxDate: Timestamp
productId: Int
price: Float
volume: Int

//用户维度表Schema
userID: Int
name: String
age: Int
gender: String

```

当Fact表和Dim表基于userID做关联的时候，由于两张表的尺寸大小都远超spark.sql.autoBroadcastJoinThreshold参数的默认值10MB，因此Spark不得不选择Shuffle Joins的实现方式。但如果我们把这个参数的值调整为2GB，因为Dim表的尺寸比2GB小，所以，Spark在运行时会选择把Dim表封装到广播变量里，并采用Broadcast Join的方式来完成两张表的数据关联。

显然，对于绝大多数的Join场景来说，autoBroadcastJoinThreshold参数的默认值10MB太低了，因为现在企业的数据体量都在TB，甚至PB级别。因此，想要有效地利用Broadcast Joins，我们需要把参数值调大，一般来说，2GB左右是个不错的选择。

现在我们已经知道了， **使用广播阈值配置项让Spark优先选择Broadcast Joins的关键，就是要确保至少有一张表的存储尺寸小于广播阈值**。

但是，在设置广播阈值的时候，不少同学都跟我抱怨：“我的数据量明明小于autoBroadcastJoinThreshold参数设定的广播阈值，为什么Spark SQL在运行时并没有选择Broadcast Joins呢？”

详细了解后我才知道，这些同学所说的数据量， **其实指的是数据表在磁盘上的存储大小**，比如用 `ls` 或是 `du -sh` 等系统命令查看文件得到的结果。要知道，同一份数据在内存中的存储大小往往会比磁盘中的存储大小膨胀数倍，甚至十数倍。这主要有两方面原因。

一方面，为了提升存储和访问效率，开发者一般采用Parquet或是ORC等压缩格式把数据落盘。这些高压缩比的磁盘数据展开到内存之后，数据量往往会翻上数倍。

另一方面，受限于对象管理机制，在堆内内存中，JVM往往需要比数据原始尺寸更大的内存空间来存储对象。

我们来举个例子，字符串“abcd”按理说只需要消耗4个字节，但是，JVM在堆内存储这4个字符串总共需要消耗48个字节！那在运行时，一份看上去不大的磁盘数据展开到内存，翻上个4、5倍并不稀奇。因此，如果你按照磁盘上的存储大小去配置autoBroadcastJoinThreshold广播阈值，大概率也会遇到同样的窘境。

**那么问题来了，有什么办法能准确地预估一张表在内存中的存储大小呢？**

首先，我们要避开一个坑。我发现，有很多资料推荐用Spark内置的SizeEstimator去预估分布式数据集的存储大小。结合多次实战和踩坑经验，咱们必须要指出， **SizeEstimator的估算结果不准确**。因此，你可以直接跳过这种方法，这也能节省你调优的时间和精力。

我认为比较靠谱的办法是： **第一步，把要预估大小的数据表缓存到内存，比如直接在DataFrame或是Dataset上调用cache方法；第二步，读取Spark SQL执行计划的统计数据**。这是因为，Spark SQL在运行时，就是靠这些统计数据来制定和调整执行策略的。

```
val df: DataFrame = _
df.cache.count

val plan = df.queryExecution.logical
val estimated: BigInt = spark
.sessionState
.executePlan(plan)
.optimizedPlan
.stats
.sizeInBytes

```

你可能会说：“这种办法虽然精确，但是这么做，实际上已经是在运行时进行调优了。把数据先缓存到内存，再去计算它的存储尺寸，当然更准确了。”没错，采用这种计算方式，调优所需花费的时间和精力确实更多，但在很多情况下，尤其是Shuffle Joins的执行效率让你痛不欲生的时候，这样的付出是值得的。

## 利用API强制广播

既然数据量的预估这么麻烦，有没有什么办法，不需要配置广播阈值，就可以让Spark SQL选择Broadcast Joins？还真有，而且办法还不止一种。

开发者可以通过Join Hints或是SQL functions中的broadcast函数，来强制Spark SQL在运行时采用Broadcast Joins的方式做数据关联。下面我就来分别讲一讲它们的含义和作用，以及该如何使用。必须要说明的是，这两种方式是等价的，并无优劣之分，只不过有了多样化的选择之后，你就可以根据自己的偏好和习惯来灵活地进行开发。

### 用Join Hints强制广播

Join Hints中的Hints表示“提示”，它指的是在开发过程中使用特殊的语法，明确告知Spark SQL在运行时采用哪种Join策略。一旦你启用了Join Hints，不管你的数据表是不是满足广播阈值，Spark SQL都会尽可能地尊重你的意愿和选择，使用Broadcast Joins去完成数据关联。

我们来举个例子，假设有两张表，一张表的内存大小在100GB量级，另一张小一些，2GB左右。在广播阈值被设置为2GB的情况下，并没有触发Broadcast Joins，但我们又不想花费时间和精力去精确计算小表的内存占用到底是多大。在这种情况下，我们就可以用Join Hints来帮我们做优化，仅仅几句提示就可以帮我们达到目的。

```
val table1: DataFrame = spark.read.parquet(path1)
val table2: DataFrame = spark.read.parquet(path2)
table1.createOrReplaceTempView("t1")
table2.createOrReplaceTempView("t2")

val query: String = “select /*+ broadcast(t2) */ * from t1 inner join t2 on t1.key = t2.key”
val queryResutls: DataFrame = spark.sql(query)

```

你看，在上面的代码示例中，只要在SQL结构化查询语句里面加上一句 `/*+ broadcast(t2) */` 提示，我们就可以强制Spark SQL对小表t2进行广播，在运行时选择Broadcast Joins的实现方式。提示语句中的关键字，除了使用broadcast外，我们还可以用broadcastjoin或者mapjoin，它们实现的效果都一样。

如果你不喜欢用SQL结构化查询语句，尤其不想频繁地在Spark SQL上下文中注册数据表，你也可以在DataFrame的DSL语法中使用Join Hints。

```
table1.join(table2.hint(“broadcast”), Seq(“key”), “inner”)

```

在上面的DSL语句中，我们只要在table2上调用hint方法，然后指定broadcast关键字，就可以同样达到强制广播表2的效果。

总之，Join Hints让开发者可以灵活地选择运行时的Join策略，对于熟悉业务、了解数据的同学来说，Join Hints允许开发者把专家经验凌驾于Spark SQL的优化引擎之上，更好地服务业务。

不过，Join Hints也有个小缺陷。如果关键字拼写错误，Spark SQL在运行时并不会显示地抛出异常，而是默默地忽略掉拼写错误的hints，假装它压根不存在。因此，在使用Join Hints的时候，需要我们在编译时自行确认Debug和纠错。

### 用broadcast函数强制广播

如果你不想等到运行时才发现问题，想让编译器帮你检查类似的拼写错误，那么你可以使用强制广播的第二种方式：broadcast函数。这个函数是类库org.apache.spark.sql.functions中的broadcast函数。调用方式非常简单，比Join Hints还要方便，只需要用broadcast函数封装需要广播的数据表即可，如下所示。

```
import org.apache.spark.sql.functions.broadcast
table1.join(broadcast(table2), Seq(“key”), “inner”)

```

你可能会问：“既然开发者可以通过Join Hints和broadcast函数强制Spark SQL选择Broadcast Joins，那我是不是就可以不用理会广播阈值的配置项了？”其实还真不是。我认为， **以广播阈值配置为主，以强制广播为辅**，往往是不错的选择。

**广播阈值的设置，更多的是把选择权交给Spark SQL，尤其是在AQE的机制下，动态Join策略调整需要这样的设置在运行时做出选择。强制广播更多的是开发者以专家经验去指导Spark SQL该如何选择运行时策略。** 二者相辅相成，并不冲突，开发者灵活地运用就能平衡Spark SQL优化策略与专家经验在应用中的比例。

## 广播变量不是银弹

不过，虽然我们一直在强调，数据关联场景中广播变量是克制Shuffle的杀手锏，但广播变量并不是银弹。

就像有的同学会说：“开发者有这么多选项，甚至可以强制Spark选择Broadcast Joins，那我们是不是可以把所有Join操作都用Broadcast Joins来实现？”答案当然是否定的，广播变量不能解决所有的数据关联问题。

**首先，从性能上来讲，Driver在创建广播变量的过程中，需要拉取分布式数据集所有的数据分片。** 在这个过程中，网络开销和Driver内存会成为性能隐患。广播变量尺寸越大，额外引入的性能开销就会越多。更何况，如果广播变量大小超过8GB，Spark会直接抛异常中断任务执行。

**其次，从功能上来讲，并不是所有的Joins类型都可以转换为Broadcast Joins。** 一来，Broadcast Joins不支持全连接（Full Outer Joins）；二来，在所有的数据关联中，我们不能广播基表。或者说，即便开发者强制广播基表，也无济于事。比如说，在左连接（Left Outer Join）中，我们只能广播右表；在右连接（Right Outer Join）中，我们只能广播左表。在下面的代码中，即便我们强制用broadcast函数进行广播，Spark SQL在运行时还是会选择Shuffle Joins。

```
import org.apache.spark.sql.functions.broadcast
broadcast (table1).join(table2, Seq(“key”), “left”)
table1.join(broadcast(table2), Seq(“key”), “right”)

```

## 小结

这一讲，我们总结了2种方法，让Spark SQL在运行时能够选择Broadcast Joins策略，分别是设置配置项和用API强制广播。

**首先，设置配置项主要是设置autoBroadcastJoinThreshold配置项。** 开发者通过这个配置项指示Spark SQL优化器。只要参与Join的两张表中，有一张表的尺寸小于这个参数值，就在运行时采用Broadcast Joins的实现方式。

为了让Spark SQL采用Broadcast Joins，开发者要做的，就是让数据表在内存中的尺寸小于autoBroadcastJoinThreshold参数的设定值。

除此之外，在设置广播阈值的时候，因为磁盘数据展开到内存的时候，存储大小会成倍增加，往往导致Spark SQL无法采用Broadcast Joins的策略。因此，我们在做数据关联的时候，还要先预估一张表在内存中的存储大小。一种精确的预估方法是先把DataFrame缓存，然后读取执行计划的统计数据。

**其次，用API强制广播有两种方法，分别是设置Join Hints和用broadcast函数。** 设置Join Hints的方法就是在SQL结构化查询语句里面加上一句“/\*+ broadcast(某表) \*/”的提示就可以了，这里的broadcast关键字也可以换成broadcastjoin或者mapjoin。另外，你也可以在DataFrame的DSL语法中使用调用hint方法，指定broadcast关键字，来达到同样的效果。设置broadcast函数的方法非常简单，只要用broadcast函数封装需要广播的数据表就可以了。

总的来说，不管是设置配置项还是用API强制广播都有各自的优缺点，所以， **以广播阈值配置为主、强制广播为辅**，往往是一个不错的选择。

最后，不过，我们也要注意，广播变量不是银弹，它并不能解决所有的数据关联问题，所以在日常的开发工作中，你要注意避免滥用广播。

## 每日一练

1. 除了broadcast关键字外，在Spark 3.0版本中，Join Hints还支持哪些关联类型和关键字？
2. DataFrame可以用sparkContext.broadcast函数来广播吗？它和org.apache.spark.sql.functions.broadcast函数之间的区别是什么？

期待在留言区看到你的思考和答案，我们下一讲见！