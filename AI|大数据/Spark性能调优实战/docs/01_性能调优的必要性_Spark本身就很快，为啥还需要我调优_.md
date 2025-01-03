你好，我是吴磊。

在日常的开发工作中，我发现有个现象很普遍。很多开发者都认为Spark的执行性能已经非常强了，实际工作中只要按部就班地实现业务功能就可以了，没有必要进行性能调优。

你是不是也这么认为呢？确实，Spark的核心竞争力就是它的执行性能，这主要得益于Spark基于内存计算的运行模式和钨丝计划的锦上添花，以及Spark SQL上的专注与发力。

但是，真如大家所说， **开发者只要把业务逻辑实现了就万事大吉了吗**？这样，咱们先不急于得出结论，你先跟着我一起看两个日常开发中常见的例子，最后我们再来回答这个问题。

在数据应用场景中，ETL（Extract Transform Load）往往是打头阵的那个，毕竟源数据经过抽取和转换才能用于探索和分析，或者是供养给机器学习算法进行模型训练，从而挖掘出数据深层次的价值。我们今天要举的两个例子，都取自典型ETL端到端作业中常见的操作和计算任务。

## 开发案例1：数据抽取

第一个例子很简单：给定数据条目，从中抽取特定字段。这样的数据处理需求在平时的ETL作业中相当普遍。想要实现这个需求，我们需要定义一个函数extractFields：它的输入参数是Seq\[Row\]类型，也即数据条目序列；输出结果的返回类型是Seq\[(String, Int)\]，也就是（String, Int）对儿的序列；函数的计算逻辑是从数据条目中抽取索引为2的字符串和索引为4的整型。

应该说这个业务需求相当简单明了，实现起来简直是小菜一碟。在实际开发中，我观察到有不少同学一上来就迅速地用下面的方式去实现，干脆利落，代码写得挺快，功能也没问题，UT、功能测试都能过。

```
//实现方案1 —— 反例
val extractFields: Seq[Row] => Seq[(String, Int)] = {
  (rows: Seq[Row]) => {
    var fields = Seq[(String, Int)]()
    rows.map(row => {
        fields = fields :+ (row.getString(2), row.getInt(4))
    })
  fields
  }
}

```

在上面这个函数体中，是先定义一个类型是Seq\[(String, Int)\]的变量fields，变量类型和函数返回类型完全一致。然后，函数逐个遍历输入参数中的数据条目，抽取数据条目中索引是2和4的字段并且构建二元元组，紧接着把元组追加到最初定义的变量fields中。最后，函数返回类型是Seq\[(String, Int)\]的变量fields。

乍看上去，这个函数似乎没什么问题。特殊的地方在于，尽管这个数据抽取函数很小，在复杂的ETL应用里是非常微小的一环，但在整个ETL作业中，它会在不同地方被频繁地反复调用。如果我基于这份代码把整个ETL应用推上线，就会发现ETL作业端到端的执行效率非常差，在分布式环境下完成作业需要两个小时，这样的速度难免有点让人沮丧。

想要让ETL作业跑得更快，我们自然需要做性能调优。可问题是我们该从哪儿入手呢？既然extractFields这个小函数会被频繁地调用，不如我们从它下手好了，看看有没有可能给它“减个肥、瘦个身”。重新审视函数extractFields的类型之后，我们不难发现，这个函数从头到尾无非是从Seq\[Row\]到Seq\[(String, Int)\]的转换，函数体的核心逻辑就是字段提取，只要从Seq\[Row\]可以得到Seq\[(String, Int)\]，目的就达到了。

要达成这两种数据类型之间的转换，除了利用上面这种开发者信手拈来的过程式编程，我们还可以用函数式的编程范式。函数式编程的原则之一就是尽可能地在函数体中避免副作用（Side effect），副作用指的是函数对于状态的修改和变更，比如上例中extractFields函数对于fields变量不停地执行追加操作就属于副作用。

基于这个想法，我们就有了第二种实现方式，如下所示。与第一种实现相比，它最大的区别在于去掉了fields变量。之后，为了达到同样的效果，我们在输入参数Seq\[Row\]上直接调用map操作逐一地提取特定字段并构建元组，最后通过toSeq将映射转换为序列，干净利落，一气呵成。

```
//实现方案2 —— 正例
val extractFields: Seq[Row] => Seq[(String, Int)] = {
  (rows: Seq[Row]) =>
    rows.map(row => (row.getString(2), row.getInt(4))).toSeq
}

```

你可能会问：“两份代码实现无非是差了个中间变量而已，能有多大差别呢？看上去不过是代码更简洁了而已。”事实上，我基于第二份代码把ETL作业推上线后，就惊奇地发现端到端执行性能提升了一倍！从原来的两个小时缩短到一个小时。 **两份功能完全一样的代码，在分布式环境中的执行性能竟然有着成倍的差别。因此你看，在日常的开发工作中，仅仅专注于业务功能实现还是不够的，任何一个可以进行调优的小环节咱们都不能放过。**

## 开发案例2：数据过滤与数据聚合

你也许会说：“你这个例子只是个例吧？更何况，这个例子里的优化，仅仅是编程范式的调整，看上去和Spark似乎也没什么关系啊！”不要紧，我们再来看第二个例子。第二个例子会稍微复杂一些，我们先来把业务需求和数据关系交代清楚。

```
/**
(startDate, endDate)
e.g. ("2021-01-01", "2021-01-31")
*/
val pairDF: DataFrame = _

/**
(dim1, dim2, dim3, eventDate, value)
e.g. ("X", "Y", "Z", "2021-01-15", 12)
*/
val factDF: DataFrame = _

// Storage root path
val rootPath: String = _

```

在这个案例中，我们有两份数据，分别是pairDF和factDF，数据类型都是DataFrame。第一份数据pairDF的Schema包含两个字段，分别是开始日期和结束日期。第二份数据的字段较多，不过最主要的字段就两个，一个是Event date事件日期，另一个是业务关心的统计量，取名为Value。其他维度如dim1、dim2、dim3主要用于数据分组，具体含义并不重要。从数据量来看，pairDF的数据量很小，大概几百条记录，factDF数据量很大，有上千万行。

对于这两份数据来说，具体的业务需求可以拆成3步：

1. 对于pairDF中的每一组时间对，从factDF中过滤出Event date落在其间的数据条目；
2. 从dim1、dim2、dim3和Event date 4个维度对factDF分组，再对业务统计量Value进行汇总；
3. 将最终的统计结果落盘到Amazon S3。

针对这样的业务需求，不少同学按照上面的步骤按部就班地进行了如下的实现。接下来，我就结合具体的代码来和你说说其中的计算逻辑。

```
//实现方案1 —— 反例
def createInstance(factDF: DataFrame, startDate: String, endDate: String): DataFrame = {
val instanceDF = factDF
.filter(col("eventDate") > lit(startDate) && col("eventDate") <= lit(endDate))
.groupBy("dim1", "dim2", "dim3", "event_date")
.agg(sum("value") as "sum_value")
instanceDF
}

pairDF.collect.foreach{
case (startDate: String, endDate: String) =>
val instance = createInstance(factDF, startDate, endDate)
val outPath = s"${rootPath}/endDate=${endDate}/startDate=${startDate}"
instance.write.parquet(outPath)
}

```

首先，他们是以factDF、开始时间和结束时间为形参定义createInstance函数。在函数体中，先根据Event date对factDF进行过滤，然后从4个维度分组汇总统计量，最后将汇总结果返回。定义完createInstance函数之后，收集pairDF到Driver端并逐条遍历每一个时间对，然后以factDF、开始时间、结束时间为实参调用createInstance函数，来获取满足过滤要求的汇总结果。最后，以Parquet的形式将结果落盘。

同样地，这段代码从功能的角度来说没有任何问题，而且从线上的结果来看，数据的处理逻辑也完全符合预期。不过，端到端的执行性能可以说是惨不忍睹，在16台机型为C5.4xlarge AWS EC2的分布式运行环境中，基于上面这份代码的ETL作业花费了半个小时才执行完毕。

没有对比就没有伤害，在同一份数据集之上，采用下面的第二种实现方式，仅用2台同样机型的EC2就能让ETL作业在15分钟以内完成端到端的计算任务。 **两份代码的业务功能和计算逻辑完全一致，执行性能却差了十万八千里**。

```
//实现方案2 —— 正例
val instances = factDF
.join(pairDF, factDF("eventDate") > pairDF("startDate") && factDF("eventDate") <= pairDF("endDate"))
.groupBy("dim1", "dim2", "dim3", "eventDate", "startDate", "endDate")
.agg(sum("value") as "sum_value")

instances.write.partitionBy("endDate", "startDate").parquet(rootPath)

```

那么问题来了，这两份代码到底差在哪里，是什么导致它们的执行性能差别如此之大。我们不妨先来回顾第一种实现方式，嗅一嗅这里面有哪些不好的代码味道。

我们都知道，触发Spark延迟计算的Actions算子主要有两类：一类是将分布式计算结果直接落盘的操作，如DataFrame的write、RDD的saveAsTextFile等；另一类是将分布式结果收集到Driver端的操作，如first、take、collect。

显然，对于第二类算子来说，Driver有可能形成单点瓶颈，尤其是用collect算子去全量收集较大的结果集时，更容易出现性能问题。因此，在第一种实现方式中，我们很容易就能嗅到collect这里的调用，味道很差。

尽管collect这里味道不好，但在我们的场景里，pairDF毕竟是一份很小的数据集，才几百条数据记录而已，全量搜集到Driver端也不是什么大问题。

最要命的是collect后面的foreach。要知道，factDF是一份庞大的分布式数据集，尽管createInstance的逻辑仅仅是对factDF进行过滤、汇总并落盘，但是createInstance函数在foreach中会被调用几百次，pairDF中有多少个时间对，createInstance就会被调用多少次。对于Spark中的DAG来说，在没有缓存的情况下，每一次Action的触发都会导致整条DAG从头到尾重新执行。

明白了这一点之后，我们再来仔细观察这份代码，你品、你细品，目不转睛地盯着foreach和createInstance中的factDF，你会惊讶地发现：有着上千万行数据的factDF被反复扫描了几百次！而且，是全量扫描哟！吓不吓人？可不可怕？这么分析下来，ETL作业端到端执行效率低下的始作俑者，是不是就暴露无遗了？

反观第二份代码，factDF和pairDF用pairDF.startDate < factDF.eventDate <= pairDF.endDate的不等式条件进行数据关联。在Spark中，不等式Join的实现方式是Nested Loop Join。尽管Nested Loop Join是所有Join实现方式（Merge Join，Hash Join，Broadcast Join等）中性能最差的一种，而且这种Join方式没有任何优化空间，但factDF与pairDF的数据关联只需要扫描一次全量数据，仅这一项优势在执行效率上就可以吊打第一份代码实现。

## 小结

今天，我们分析了两个案例，这两个案例都来自数据应用的ETL场景。第一个案例讲的是，在函数被频繁调用的情况下，函数里面一个简单变量所引入的性能开销被成倍地放大。第二个例子讲的是，不恰当的实现方式导致海量数据被反复地扫描成百上千次。

通过对这两个案例进行分析和探讨，我们发现，对于Spark的应用开发，绝不仅仅是完成业务功能实现就高枕无忧了。 **Spark天生的执行效率再高，也需要你针对具体的应用场景和运行环境进行性能调优**。

而性能调优的收益显而易见：一来可以节约成本，尤其是按需付费的云上成本，更短的执行时间意味着更少的花销；二来可以提升开发的迭代效率，尤其是对于从事数据分析、数据科学、机器学习的同学来说，更高的执行效率可以更快地获取数据洞察，更快地找到模型收敛的最优解。因此你看，性能调优不是一件锦上添花的事情，而是开发者必须要掌握的一项傍身技能。

那么，对于Spark的性能调优，你准备好了吗？生活不止眼前的苟且，让我们来一场说走就走的性能调优之旅吧。来吧！快上车！扶稳坐好，系好安全带，咱们准备发车了！

## 每日一练

1. 日常工作中，你还遇到过哪些功能实现一致、但性能大相径庭的案例吗？
2. 我们今天讲的第二个案例中的正例代码，你觉得还有可能进一步优化吗？

期待在留言区看到你分享，也欢迎把你对开发案例的思考写下来，我们下节课见！