我前面介绍的大数据技术主要是处理、计算存储介质上的大规模数据，这类计算也叫大数据批处理计算。顾名思义，数据是以批为单位进行计算，比如一天的访问日志、历史上所有的订单数据等。这些数据通常通过HDFS存储在磁盘上，使用MapReduce或者Spark这样的批处理大数据计算框架进行计算，一般完成一次计算需要花费几分钟到几小时的时间。

此外，还有一种大数据技术，针对实时产生的大规模数据进行即时计算处理，我们比较熟悉的有摄像头采集的实时视频数据、淘宝实时产生的订单数据等。像上海这样的一线城市，公共场所的摄像头规模在数百万级，即使只有重要场所的视频数据需要即时处理，可能也会涉及几十万个摄像头，如果想实时发现视频中出现的通缉犯或者违章车辆，就需要对这些摄像头产生的数据进行实时处理。实时处理最大的不同就是这类数据跟存储在HDFS上的数据不同，是实时传输过来的，或者形象地说是流过来的，所以针对这类大数据的实时处理系统也叫大数据流计算系统。

目前业内比较知名的大数据流计算框架有Storm、Spark Streaming、Flink，接下来，我们逐一看看它们的架构原理与使用方法。

## Storm

其实大数据实时处理的需求早已有之，最早的时候，我们用消息队列实现大数据实时处理，如果处理起来比较复杂，那么就需要很多个消息队列，将实现不同业务逻辑的生产者和消费者串起来。这个处理过程类似下面图里的样子。

![](https://static001.geekbang.org/resource/image/19/31/199c65da1a9dfae48f42c32f6a82c831.png?wh=1236%2A312)

图中的消息队列负责完成数据的流转；处理逻辑既是消费者也是生产者，也就是既消费前面消息队列的数据，也为下个消息队列产生数据。这样的系统只能是根据不同需求开发出来，并且每次新的需求都需要重新开发类似的系统。因为不同应用的生产者、消费者的处理逻辑不同，所以处理流程也不同，因此这个系统也就无法复用。

之后我们很自然地就会想到，能不能开发一个流处理计算系统，我们只要定义好处理流程和每一个节点的处理逻辑，代码部署到流处理系统后，就能按照预定义的处理流程和处理逻辑执行呢？Storm就是在这种背景下产生的，它也算是一个比较早期的大数据流计算框架。上面的例子如果用Storm来实现，过程就变得简单一些了。

![](https://static001.geekbang.org/resource/image/78/5b/780899b3fda0ea39acbdfb9545fbc55b.png?wh=664%2A314)

有了Storm后，开发者无需再关注数据的流转、消息的处理和消费，只要编程开发好数据处理的逻辑bolt和数据源的逻辑spout，以及它们之间的拓扑逻辑关系toplogy，提交到Storm上运行就可以了。

在了解了Storm的运行机制后，我们来看一下它的架构。Storm跟Hadoop一样，也是主从架构。

![](https://static001.geekbang.org/resource/image/d3/8a/d33aa8765ad381824fd9818f93074a8a.png?wh=1198%2A762)

nimbus是集群的Master，负责集群管理、任务分配等。supervisor是Slave，是真正完成计算的地方，每个supervisor启动多个worker进程，每个worker上运行多个task，而task就是spout或者bolt。supervisor和nimbus通过ZooKeeper完成任务分配、心跳检测等操作。

Hadoop、Storm的设计理念，其实是一样的，就是把和具体业务逻辑无关的东西抽离出来，形成一个框架，比如大数据的分片处理、数据的流转、任务的部署与执行等，开发者只需要按照框架的约束，开发业务逻辑代码，提交给框架执行就可以了。

而这也正是所有框架的开发理念，就是将业务逻辑和处理过程分离开来，使开发者只需关注业务开发即可，比如Java开发者都很熟悉的Tomcat、Spring等框架，全部都是基于这种理念开发出来的。

## Spark Streaming

我们知道Spark是一个批处理大数据计算引擎，主要针对大批量历史数据进行计算。前面我在讲Spark架构原理时介绍过，Spark是一个快速计算的大数据引擎，它将原始数据分片后装载到集群中计算，对于数据量不是很大、过程不是很复杂的计算，可以在秒级甚至毫秒级完成处理。

Spark Streaming巧妙地利用了Spark的**分片**和**快速计算**的特性，将实时传输进来的数据按照时间进行分段，把一段时间传输进来的数据合并在一起，当作一批数据，再去交给Spark去处理。下图这张图描述了Spark Streaming将数据分段、分批的过程。

![](https://static001.geekbang.org/resource/image/fb/c3/fb535e9dc1813dbacfa03c7cb65d17c3.png?wh=1078%2A206)

如果时间段分得足够小，每一段的数据量就会比较小，再加上Spark引擎的处理速度又足够快，这样看起来好像数据是被实时处理的一样，这就是Spark Streaming实时流计算的奥妙。

这里要注意的是，在初始化Spark Streaming实例的时候，需要指定分段的时间间隔。下面代码示例中间隔是1秒。

```
val ssc = new StreamingContext(conf, Seconds(1))
```

当然你也可以指定更小的时间间隔，比如500ms，这样处理的速度就会更快。时间间隔的设定通常要考虑业务场景，比如你希望统计每分钟高速公路的车流量，那么时间间隔可以设为1分钟。

Spark Streaming主要负责将流数据转换成小的批数据，剩下的就可以交给Spark去做了。

## Flink

前面说Spark Streaming是将实时数据流按时间分段后，当作小的批处理数据去计算。那么Flink则相反，一开始就是按照流处理计算去设计的。当把从文件系统（HDFS）中读入的数据也当做数据流看待，他就变成批处理系统了。

为什么Flink既可以流处理又可以批处理呢？

如果要进行流计算，Flink会初始化一个流执行环境StreamExecutionEnvironment，然后利用这个执行环境构建数据流DataStream。

```
StreamExecutionEnvironment see = StreamExecutionEnvironment.getExecutionEnvironment();

DataStream<WikipediaEditEvent> edits = see.addSource(new WikipediaEditsSource());
```

如果要进行批处理计算，Flink会初始化一个批处理执行环境ExecutionEnvironment，然后利用这个环境构建数据集DataSet。

```
ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();

DataSet<String> text = env.readTextFile("/path/to/file");
```

然后在DataStream或者DataSet上执行各种数据转换操作（transformation），这点很像Spark。不管是流处理还是批处理，Flink运行时的执行引擎是相同的，只是数据源不同而已。

Flink处理实时数据流的方式跟Spark Streaming也很相似，也是将流数据分段后，一小批一小批地处理。流处理算是Flink里的“一等公民”，Flink对流处理的支持也更加完善，它可以对数据流执行window操作，将数据流切分到一个一个的window里，进而进行计算。

在数据流上执行

```
.timeWindow(Time.seconds(10))
```

可以将数据切分到一个10秒的时间窗口，进一步对这个窗口里的一批数据进行统计汇总。

Flink的架构和Hadoop 1或者Yarn看起来也很像，JobManager是Flink集群的管理者，Flink程序提交给JobManager后，JobManager检查集群中所有TaskManager的资源利用状况，如果有空闲TaskSlot（任务槽），就将计算任务分配给它执行。

![](https://static001.geekbang.org/resource/image/92/9f/92584744442b15d541a355eb7997029f.png?wh=645%2A480)

## 小结

大数据技术最开始出现的时候，仅仅针对批处理计算，也就是离线计算。相对说来，大数据实时计算可以复用互联网实时在线业务的处理技术方案，毕竟对于Google而言，每天几十亿的用户搜索访问请求也是大数据，而互联网应用处理实时高并发请求已经有一套完整的解决方案了（详见我写的《大型网站技术架构：核心原理与案例分析》一书），大数据流计算的需求当时并不强烈。

但是我们纵观计算机软件发展史，发现这部历史堪称一部**技术和业务不断分离**的历史。人们不断将业务逻辑从技术实现上分离出来，各种技术和架构方案的出现，也基本都是为这一目标服务。

最早的时候我们用机器语言和汇编语言编程，直接将业务逻辑用CPU指令实现，计算机软件就是CPU指令的集合，此时技术和业务完全耦合，软件编程就是面向机器编程，用机器指令完成业务逻辑，当时我们在编程的时候思维方式是面向机器的，需要熟记机器指令。

后来我们有了操作系统和高级编程语言，将软件和CPU指令分离开来，我们使用Pascal、Cobal这样的高级编程语言进行编程，并将程序运行在操作系统上。这时我们不再面向机器编程，而是面向业务逻辑和过程编程，这是业务逻辑与计算机技术的一次重要分离。

再后来出现了面向对象的编程语言，这是人类编程史上的里程碑。我们编程的时候关注的重心，从机器、业务过程转移到业务对象本身，分析客观世界业务对象的关系和协作是怎样的，如何通过编程映射到软件上，这是编程思维的一次革命，业务和技术实现从思想上分离了。

再后来出现各种编程框架，一方面使业务和技术分离得更加彻底，想象一下，如果不用这些框架，你自己编程监听80通信端口，从获取HTTP二进制流开始，到开发一个Web应用会是什么感觉。另一方面，这些框架也把复杂的业务流程本身解耦合，视图、业务、服务、存储各个层次模块独立开发、部署，通过框架整合成一个系统。

回到流计算，固然我们可以用各种分布式技术实现大规模数据的实时流处理，但是我们更希望只要针对小数据量进行业务开发，然后丢到一个大规模服务器集群上，就可以对大规模实时数据进行流计算处理。也就是业务实现和大数据流处理技术分离，业务不需要关注技术，于是各种大数据流计算技术应运而生。

其实，我们再看看互联网应用开发，也是逐渐向业务和技术分离的方向发展。比如，云计算以云服务的方式将各种分布式解决方案提供给开发者，使开发者无需关注分布式基础设施的部署和维护。目前比较热门的微服务、容器、服务编排、Serverless等技术方案，它们则更进一步，使开发者只关注业务开发，将业务流程、资源调度和服务管理等技术方案分离开来。而物联网领域时髦的FaaS，意思是函数即服务，就是开发者只要开发好函数，提交后就可以自动部署到整个物联网集群运行起来。

总之，流计算就是将大规模实时计算的资源管理和数据流转都统一管理起来，开发者只要开发针对小数据量的数据处理逻辑，然后部署到流计算平台上，就可以对大规模数据进行流式计算了。

## 思考题

流计算架构方案也逐渐对互联网在线业务开发产生影响，目前流行的微服务架构虽然将业务逻辑拆分得很细，但是服务之间的调用还是依赖接口，这依然是一种比较强的耦合关系。淘宝等互联网企业已经在尝试一种类似流计算的、异步的、基于消息的服务调用与依赖架构，据说淘宝的部分核心业务功能已经使用这种架构方案进行系统重构，并应用到今年的“双十一”大促，利用这种架构特有的回压设计对高并发系统进行自动限流与降级，取得很好的效果。

我也邀请了淘宝负责这次架构重构的高级技术专家李鼎，请他在留言区分享一下这次架构重构的心得体会。

你对这种架构方案有什么想法，是否认为这样的架构方案代表了未来的互联网应用开发的方向？

欢迎你写下自己的思考或疑问，与我和其他同学一起讨论。
<div><strong>精选留言（15）</strong></div><ul>
<li><span>李鼎(哲良)</span> 👍（163） 💬（5）<p>数据流是久经考验的典型思路，在网络协议（如TCP）、数据平台这样场景，早就应用多年习以为常了。淘宝业务的应用架构升级可以认为是把这样思路应用到了业务系统开发中，把『流』作为业务表达上的一等概念和手段，并在业务架构&#47;系统能力优化提升。

简单地说，因为业务面向数据流来编写，一方面业务逻辑表达可以自然接近业务流程；另一方面逻辑运行可以是全异步有很好的性能提升，一核心后端应用在双11线上，单机QPS提升30%，RT下降40%。流程的表达与异步&#47;同步执行方式是分离的（如果了解过像RxJava，这句会容易理解：）。

另外，『流』也为业务系统的保护提供新的一些方法，在思路上其实和流计算平台是一样的，这对业务大型系统的稳定性来非常重要。

当然，业务的流式架构，在业务编写上有些FP风格（简单地说比如充分使用了Lambda），平时我们大家业务上主要是用命令式顺序平铺方式来表达，会有要个熟悉过程，虽然不见得有多难 :)</p>2018-12-06</li><br/><li><span>Jowin</span> 👍（12） 💬（1）<p>智慧老师，我是从事金融实时数据处理的，有一类典型需求是从原始实时数据计算出各种衍生数据，但是有状态积累。比如，当前状态是S0，收到数据A0，此时要根据(S0,A0)生成数据A1，同时要更新当前状态S1，后续的新数据再基于S1处理。团队考虑过使用Stream作为计算平台，有两个问题没想清楚怎么处理：
1）如果计算任务故障挂掉，会不会导致这期间的数据丢失？
2）另外，由于数据量也不小，差不多在每秒4~5万条消息，状态S的更新特别频繁，常规的存储在性能上没有办法满足，所以我们是采用内存+日志文件保存。如果重启的任务被分配套新的服务节点上，我们是否就还得考虑这部分数据也要迁移过去？
盼复，谢谢。</p>2018-12-01</li><br/><li><span>星凡</span> 👍（11） 💬（1）<p>文中有这么一段话：“回到流计算，固然我们可以用各种分布式技术实现大规模数据的实时流处理，但是我们更希望只针对小数据量进行业务开发，然后丢到一个大规模服务器集群上，就可以对大规模实时数据进行流计算处理。”，在下愚昧，没有get到，不用分布式技术实现大规模数据实时流处理的真正原因是？</p>2019-10-06</li><br/><li><span>zhj</span> 👍（7） 💬（1）<p>1面向数据流的编程在java里逐渐展露头角，之前rxjava更多的是用于android，直到hystrix才算是后端一个大规模应用的案例(也和场景有关吧，后端的大多业务都是短事物处理去构建一条数据流水线反倒显得累赘)，reactor是响应式编程的另一个实现，直到spring5全面拥抱以后，才完全进入人们视野(所以技术落地离不开大厂的支持)，单纯的业务层处理构造一条很短的数据流意义不大(因为数据源可能还是需要返回所有数据),spring webflux结合springdata从持久层到业务层构建了自下而上的数据流(前提是持久层驱动是非阻塞的),并利用reactor-netty(支持网络背压)，理想情况下将构建一个全链路的按需处理数据流
2 数据流编程，有点类似当年面向函数-&gt;面向对象，更多的是思考方式的改变，异步和数据流都是为了正确的构建数据流间的关系而存在，不过目前貌似不支持对数据流分片并行处理</p>2019-01-08</li><br/><li><span>🐱您的好友William🐱</span> 👍（5） 💬（1）<p>主攻人工智能，机器学习和算法实现的应该学习哪种呢？Storm，Spark还是Flink呢？</p>2018-12-04</li><br/><li><span>李二木</span> 👍（3） 💬（1）<p>和老师探讨一个问题，对于架构设计，目前流行的是微服务，我个人觉得微服务还是有好些缺点。架构从开始的合走到现在的分，未来会不会从分又到和呢？</p>2018-12-01</li><br/><li><span>Geek_ea2bf8</span> 👍（0） 💬（1）<p>智慧老师，通常的场景是，已经有大量的存量数据，在离线的Hadoop中，又有实时需求，依赖于历史存量数据，和当日的实时数据。这种典型场景，架构应该如何设计啊？</p>2023-07-25</li><br/><li><span>Geek_8593e5</span> 👍（0） 💬（1）<p>Flink 处理实时数据流的方式跟 Spark Streaming 也很相似，也是将流数据分段后，一小批一小批地处理。（？这没听懂）   Flink是分批的吗？</p>2022-03-08</li><br/><li><span>万～～</span> 👍（27） 💬（2）<p>你好 storm spark flink 都是优秀的框架 那我们应该学习哪个呢？ 都学肯定精力不够 而且难以精通</p>2018-12-01</li><br/><li><span>laurencezl</span> 👍（18） 💬（3）<p>智慧老师你好，这节对storm.spark.flink的介绍感觉过于概述了！后面是否会有详细的文章介绍，比如分析对比一下他们三者各自优缺点在哪里？各自试用与不适用的业务场景有哪些之类的呢？</p>2018-12-04</li><br/><li><span>纯洁的憎恶</span> 👍（13） 💬（0）<p>批计算是对历史数据的一次性处理，流计算是对实时流入的数据实时响应。

storm模仿消息队列（什么是消息队列？卡夫卡？），把消息队列中与业务逻辑无关的过程部分抽象出来形成标准框架，实现复用。开发者不用纠结四面八方涌入的实时数据如何流转，消息如何处理和消费，只用考虑业务流程、数据源、处理逻辑。 

spark streaming以spark为基础，将同一时间段的数据分片聚合在一起做为一批数据处理（以批模拟流）。

flink则是以流模拟批，它的底层计算逻辑只有流，通过时间窗口把流入数据按时间间隔分为若干批（与spark streaming类似），通过数据源的不同，完成在流与批的切换。

计算机软件的发展史就是一部业务与技术分离的历史，通过把业务不相关部分高度抽象并标准化，开发者能够越来越多的专注于业务流程，而越来越少的考虑机器、程序等技术细节的因素。

不知这么理解对不对。

需要进一步明确的知识点：消息队列。</p>2018-12-01</li><br/><li><span>常平</span> 👍（9） 💬（0）<p>流式架构本质上是事件驱动（event-Driven）架构，流由段（segment）组成，段由事件（event）组成，事件由字节（bytes）组成，事件大小有限，而字节流大小无限</p>2018-12-11</li><br/><li><span>尼糯米</span> 👍（4） 💬（0）<p>问题一
Strom算是比较早期的大数据流计算框架
	》》定义处理流程
	》》流程的每个环节上的处理逻辑
数据流转是计算框架按处理流程进行流转吗？
从作者的陈述，实在看不出这和实时数据有啥关系，把它的计算框架套在批数据上也不伪和，
至少文中不指明是为了流计算，实在看不出来

问题二
Spark Streaming实现的流计算
是通过把流数据切分迷你批数据且每个迷你批数据的处理非常迅速，
而这个迷你批数据是怎么做容错呢，切分出来的数据总要做容错吧

问题三
Flink不管是批数据还是实时数据流，对它只是数据源不同，这点从源码上切实看出来了，
它确实要构建一个数据源出来，在数据源上做各种数据处理。
但是我从作者描述中理解到的东西：数据处理终究还是避免不了对数据的分段，
所以，不管是怎样的流计算框架，把数据处理总是以数据分片的基础上进行呢

如果是这样，流计算喊出来还是响当当，蛮吓人的
希望看到的各位老师批评下

PS，该篇小结太多了，小结之上倒是不多</p>2019-01-10</li><br/><li><span>qiaoer</span> 👍（3） 💬（0）<p>老师讲了Storm，Flink，Spark Streaming，感觉他们几个很相似，都是Master&#47;slave 结构，一个Master节点进行 任务划分管理，然后下发到Slave节点，Slave负责具体的执行。 但是他们的区别是什么？还有Flink和Spark Streaming他们都是Micro Streaming的思路？那么适用的场景又是什么呢？</p>2019-10-30</li><br/><li><span>杰之7</span> 👍（3） 💬（0）<p>通过本小节的学习，了解了常用的流计算及它们的计算框架，其中Spark Streaming巧妙了运用Spark计算速度的优势，将Spark批计算通过时间间隔装置成流计算。在我们的生活中，股票交易的价格传输应该就是运用了流计算，要求在极短的时间内完成对价格的改变。当然，淘宝，一线城市的摄像头在后台处理上也应用了流计算技术。相比批计算技术，流计算在重要的数据上会用的越来越广。</p>2018-12-01</li><br/>
</ul>