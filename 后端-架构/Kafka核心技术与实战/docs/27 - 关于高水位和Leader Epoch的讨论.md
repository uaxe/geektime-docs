你好，我是胡夕。今天我要和你分享的主题是：Kafka中的高水位和Leader Epoch机制。

你可能听说过高水位（High Watermark），但不一定耳闻过Leader Epoch。前者是Kafka中非常重要的概念，而后者是社区在0.11版本中新推出的，主要是为了弥补高水位机制的一些缺陷。鉴于高水位机制在Kafka中举足轻重，而且深受各路面试官的喜爱，今天我们就来重点说说高水位。当然，我们也会花一部分时间来讨论Leader Epoch以及它的角色定位。

## 什么是高水位？

首先，我们要明确一下基本的定义：什么是高水位？或者说什么是水位？水位一词多用于流式处理领域，比如，Spark Streaming或Flink框架中都有水位的概念。教科书中关于水位的经典定义通常是这样的：

> 在时刻T，任意创建时间（Event Time）为T’，且T’≤T的所有事件都已经到达或被观测到，那么T就被定义为水位。

“Streaming System”一书则是这样表述水位的：

> 水位是一个单调增加且表征最早未完成工作（oldest work not yet completed）的时间戳。

为了帮助你更好地理解水位，我借助这本书里的一张图来说明一下。

![](https://static001.geekbang.org/resource/image/84/77/8426888d04e1e9917619829b7e3de877.png?wh=1950%2A624)

图中标注“Completed”的蓝色部分代表已完成的工作，标注“In-Flight”的红色部分代表正在进行中的工作，两者的边界就是水位线。

在Kafka的世界中，水位的概念有一点不同。Kafka的水位不是时间戳，更与时间无关。它是和位置信息绑定的，具体来说，它是用消息位移来表征的。另外，Kafka源码使用的表述是高水位，因此，今天我也会统一使用“高水位”或它的缩写HW来进行讨论。值得注意的是，Kafka中也有低水位（Low Watermark），它是与Kafka删除消息相关联的概念，与今天我们要讨论的内容没有太多联系，我就不展开讲了。

## 高水位的作用

在Kafka中，高水位的作用主要有2个。

1. 定义消息可见性，即用来标识分区下的哪些消息是可以被消费者消费的。
2. 帮助Kafka完成副本同步。

下面这张图展示了多个与高水位相关的Kafka术语。我来详细解释一下图中的内容，同时澄清一些常见的误区。

![](https://static001.geekbang.org/resource/image/45/db/453ff803a31aa030feedba27aed17ddb.jpg?wh=4000%2A1583)

我们假设这是某个分区Leader副本的高水位图。首先，请你注意图中的“已提交消息”和“未提交消息”。我们之前在专栏[第11讲](https://time.geekbang.org/column/article/102931)谈到Kafka持久性保障的时候，特意对两者进行了区分。现在，我借用高水位再次强调一下。在分区高水位以下的消息被认为是已提交消息，反之就是未提交消息。消费者只能消费已提交消息，即图中位移小于8的所有消息。注意，这里我们不讨论Kafka事务，因为事务机制会影响消费者所能看到的消息的范围，它不只是简单依赖高水位来判断。它依靠一个名为LSO（Log Stable Offset）的位移值来判断事务型消费者的可见性。

另外，需要关注的是，**位移值等于高水位的消息也属于未提交消息。也就是说，高水位上的消息是不能被消费者消费的**。

图中还有一个日志末端位移的概念，即Log End Offset，简写是LEO。它表示副本写入下一条消息的位移值。注意，数字15所在的方框是虚线，这就说明，这个副本当前只有15条消息，位移值是从0到14，下一条新消息的位移是15。显然，介于高水位和LEO之间的消息就属于未提交消息。这也从侧面告诉了我们一个重要的事实，那就是：**同一个副本对象，其高水位值不会大于LEO值**。

**高水位和LEO是副本对象的两个重要属性**。Kafka所有副本都有对应的高水位和LEO值，而不仅仅是Leader副本。只不过Leader副本比较特殊，Kafka使用Leader副本的高水位来定义所在分区的高水位。换句话说，**分区的高水位就是其Leader副本的高水位**。

## 高水位更新机制

现在，我们知道了每个副本对象都保存了一组高水位值和LEO值，但实际上，在Leader副本所在的Broker上，还保存了其他Follower副本的LEO值。我们一起来看看下面这张图。

![](https://static001.geekbang.org/resource/image/8b/de/8b1b8474a568e2ae40bf36bb03ca81de.jpg?wh=2347%2A1648)

在这张图中，我们可以看到，Broker 0上保存了某分区的Leader副本和所有Follower副本的LEO值，而Broker 1上仅仅保存了该分区的某个Follower副本。Kafka把Broker 0上保存的这些Follower副本又称为**远程副本**（Remote Replica）。Kafka副本机制在运行过程中，会更新Broker 1上Follower副本的高水位和LEO值，同时也会更新Broker 0上Leader副本的高水位和LEO以及所有远程副本的LEO，但它不会更新远程副本的高水位值，也就是我在图中标记为灰色的部分。

为什么要在Broker 0上保存这些远程副本呢？其实，它们的主要作用是，**帮助Leader副本确定其高水位，也就是分区高水位**。

为了帮助你更好地记忆这些值被更新的时机，我做了一张表格。只有搞清楚了更新机制，我们才能开始讨论Kafka副本机制的原理，以及它是如何使用高水位来执行副本消息同步的。

![](https://static001.geekbang.org/resource/image/d6/41/d6d2f98c611e06ffb85f01031ca79b41.jpg?wh=3894%2A2216)

在这里，我稍微解释一下，什么叫与Leader副本保持同步。判断的条件有两个。

1. 该远程Follower副本在ISR中。
2. 该远程Follower副本LEO值落后于Leader副本LEO值的时间，不超过Broker端参数replica.lag.time.max.ms的值。如果使用默认值的话，就是不超过10秒。

乍一看，这两个条件好像是一回事，因为目前某个副本能否进入ISR就是靠第2个条件判断的。但有些时候，会发生这样的情况：即Follower副本已经“追上”了Leader的进度，却不在ISR中，比如某个刚刚重启回来的副本。如果Kafka只判断第1个条件的话，就可能出现某些副本具备了“进入ISR”的资格，但却尚未进入到ISR中的情况。此时，分区高水位值就可能超过ISR中副本LEO，而高水位 &gt; LEO的情形是不被允许的。

下面，我们分别从Leader副本和Follower副本两个维度，来总结一下高水位和LEO的更新机制。

**Leader副本**

处理生产者请求的逻辑如下：

1. 写入消息到本地磁盘。
2. 更新分区高水位值。  
   i. 获取Leader副本所在Broker端保存的所有远程副本LEO值（LEO-1，LEO-2，……，LEO-n）。  
   ii. 获取Leader副本高水位值：currentHW。  
   iii. 更新 currentHW = max{currentHW, min（LEO-1, LEO-2, ……，LEO-n）}。

处理Follower副本拉取消息的逻辑如下：

1. 读取磁盘（或页缓存）中的消息数据。
2. 使用Follower副本发送请求中的位移值更新远程副本LEO值。
3. 更新分区高水位值（具体步骤与处理生产者请求的步骤相同）。

**Follower副本**

从Leader拉取消息的处理逻辑如下：

1. 写入消息到本地磁盘。
2. 更新LEO值。
3. 更新高水位值。  
   i. 获取Leader发送的高水位值：currentHW。  
   ii. 获取步骤2中更新过的LEO值：currentLEO。  
   iii. 更新高水位为min(currentHW, currentLEO)。

## 副本同步机制解析

搞清楚了这些值的更新机制之后，我来举一个实际的例子，说明一下Kafka副本同步的全流程。该例子使用一个单分区且有两个副本的主题。

当生产者发送一条消息时，Leader和Follower副本对应的高水位是怎么被更新的呢？我给出了一些图片，我们一一来看。

首先是初始状态。下面这张图中的remote LEO就是刚才的远程副本的LEO值。在初始状态时，所有值都是0。

![](https://static001.geekbang.org/resource/image/1e/36/1ee643ce819a503f72df3d9b4ab04536.jpg?wh=3173%2A691)

当生产者给主题分区发送一条消息后，状态变更为：

![](https://static001.geekbang.org/resource/image/73/0b/7317242d7068dbf618866d5974a2d80b.jpg?wh=3147%2A1271)

此时，Leader副本成功将消息写入了本地磁盘，故LEO值被更新为1。

Follower再次尝试从Leader拉取消息。和之前不同的是，这次有消息可以拉取了，因此状态进一步变更为：

![](https://static001.geekbang.org/resource/image/91/0d/910e114abe40f1f9e4a13f6e6083320d.jpg?wh=3167%2A1013)

这时，Follower副本也成功地更新LEO为1。此时，Leader和Follower副本的LEO都是1，但各自的高水位依然是0，还没有被更新。**它们需要在下一轮的拉取中被更新**，如下图所示：

![](https://static001.geekbang.org/resource/image/80/cb/8066e72733f14d2732a054ed56e373cb.jpg?wh=3081%2A1560)

在新一轮的拉取请求中，由于位移值是0的消息已经拉取成功，因此Follower副本这次请求拉取的是位移值=1的消息。Leader副本接收到此请求后，更新远程副本LEO为1，然后更新Leader高水位为1。做完这些之后，它会将当前已更新过的高水位值1发送给Follower副本。Follower副本接收到以后，也将自己的高水位值更新成1。至此，一次完整的消息同步周期就结束了。事实上，Kafka就是利用这样的机制，实现了Leader和Follower副本之间的同步。

## Leader Epoch登场

故事讲到这里似乎很完美，依托于高水位，Kafka既界定了消息的对外可见性，又实现了异步的副本同步机制。不过，我们还是要思考一下这里面存在的问题。

从刚才的分析中，我们知道，Follower副本的高水位更新需要一轮额外的拉取请求才能实现。如果把上面那个例子扩展到多个Follower副本，情况可能更糟，也许需要多轮拉取请求。也就是说，Leader副本高水位更新和Follower副本高水位更新在时间上是存在错配的。这种错配是很多“数据丢失”或“数据不一致”问题的根源。基于此，社区在0.11版本正式引入了Leader Epoch概念，来规避因高水位更新错配导致的各种不一致问题。

所谓Leader Epoch，我们大致可以认为是Leader版本。它由两部分数据组成。

1. Epoch。一个单调增加的版本号。每当副本领导权发生变更时，都会增加该版本号。小版本号的Leader被认为是过期Leader，不能再行使Leader权力。
2. 起始位移（Start Offset）。Leader副本在该Epoch值上写入的首条消息的位移。

我举个例子来说明一下Leader Epoch。假设现在有两个Leader Epoch&lt;0, 0&gt;和&lt;1, 120&gt;，那么，第一个Leader Epoch表示版本号是0，这个版本的Leader从位移0开始保存消息，一共保存了120条消息。之后，Leader发生了变更，版本号增加到1，新版本的起始位移是120。

Kafka Broker会在内存中为每个分区都缓存Leader Epoch数据，同时它还会定期地将这些信息持久化到一个checkpoint文件中。当Leader副本写入消息到磁盘时，Broker会尝试更新这部分缓存。如果该Leader是首次写入消息，那么Broker会向缓存中增加一个Leader Epoch条目，否则就不做更新。这样，每次有Leader变更时，新的Leader副本会查询这部分缓存，取出对应的Leader Epoch的起始位移，以避免数据丢失和不一致的情况。

接下来，我们来看一个实际的例子，它展示的是Leader Epoch是如何防止数据丢失的。请先看下图。

![](https://static001.geekbang.org/resource/image/4d/f5/4d97a873fc1bfaf89b5cc8259838f0f5.jpg?wh=2254%2A2036)

我稍微解释一下，单纯依赖高水位是怎么造成数据丢失的。开始时，副本A和副本B都处于正常状态，A是Leader副本。某个使用了默认acks设置的生产者程序向A发送了两条消息，A全部写入成功，此时Kafka会通知生产者说两条消息全部发送成功。

现在我们假设Leader和Follower都写入了这两条消息，而且Leader副本的高水位也已经更新了，但Follower副本高水位还未更新——这是可能出现的。还记得吧，Follower端高水位的更新与Leader端有时间错配。倘若此时副本B所在的Broker宕机，当它重启回来后，副本B会执行日志截断操作，将LEO值调整为之前的高水位值，也就是1。这就是说，位移值为1的那条消息被副本B从磁盘中删除，此时副本B的底层磁盘文件中只保存有1条消息，即位移值为0的那条消息。

当执行完截断操作后，副本B开始从A拉取消息，执行正常的消息同步。如果就在这个节骨眼上，副本A所在的Broker宕机了，那么Kafka就别无选择，只能让副本B成为新的Leader，此时，当A回来后，需要执行相同的日志截断操作，即将高水位调整为与B相同的值，也就是1。这样操作之后，位移值为1的那条消息就从这两个副本中被永远地抹掉了。这就是这张图要展示的数据丢失场景。

严格来说，这个场景发生的前提是**Broker端参数min.insync.replicas设置为1**。此时一旦消息被写入到Leader副本的磁盘，就会被认为是“已提交状态”，但现有的时间错配问题导致Follower端的高水位更新是有滞后的。如果在这个短暂的滞后时间窗口内，接连发生Broker宕机，那么这类数据的丢失就是不可避免的。

现在，我们来看下如何利用Leader Epoch机制来规避这种数据丢失。我依然用图的方式来说明。

![](https://static001.geekbang.org/resource/image/3a/8c/3a2e1131e8244233c076de906c174f8c.jpg?wh=2975%2A1992)

场景和之前大致是类似的，只不过引用Leader Epoch机制后，Follower副本B重启回来后，需要向A发送一个特殊的请求去获取Leader的LEO值。在这个例子中，该值为2。当获知到Leader LEO=2后，B发现该LEO值不比它自己的LEO值小，而且缓存中也没有保存任何起始位移值 &gt; 2的Epoch条目，因此B无需执行任何日志截断操作。这是对高水位机制的一个明显改进，即副本是否执行日志截断不再依赖于高水位进行判断。

现在，副本A宕机了，B成为Leader。同样地，当A重启回来后，执行与B相同的逻辑判断，发现也不用执行日志截断，至此位移值为1的那条消息在两个副本中均得到保留。后面当生产者程序向B写入新消息时，副本B所在的Broker缓存中，会生成新的Leader Epoch条目：\[Epoch=1, Offset=2]。之后，副本B会使用这个条目帮助判断后续是否执行日志截断操作。这样，通过Leader Epoch机制，Kafka完美地规避了这种数据丢失场景。

## 小结

今天，我向你详细地介绍了Kafka的高水位机制以及Leader Epoch机制。高水位在界定Kafka消息对外可见性以及实现副本机制等方面起到了非常重要的作用，但其设计上的缺陷给Kafka留下了很多数据丢失或数据不一致的潜在风险。为此，社区引入了Leader Epoch机制，尝试规避掉这类风险。事实证明，它的效果不错，在0.11版本之后，关于副本数据不一致性方面的Bug的确减少了很多。如果你想深入学习Kafka的内部原理，今天的这些内容是非常值得你好好琢磨并熟练掌握的。

![](https://static001.geekbang.org/resource/image/98/3f/989d13e4bc4f44618a10b5b7bd6f523f.jpg?wh=2069%2A2580)

## 开放讨论

在讲述高水位时，我是拿2个副本举的例子。不过，你应该很容易地扩展到多个副本。现在，请你尝试用3个副本来说明一下副本同步全流程，以及分区高水位被更新的过程。

欢迎写下你的思考和答案，我们一起讨论。如果你觉得有所收获，也欢迎把文章分享给你的朋友。
<div><strong>精选留言（15）</strong></div><ul>
<li><span>朱东旭</span> 👍（17） 💬（5）<p>胡老师您好，在您讲的leader epoch机制案例中，在我看来最关键的操作是broker重启后先向leader确认leo,而不是直接基于自己的高水位截断数据，来防止数据不一致。。可是有无leader epoch都可以做这个操作呀，我看不出leader epoch必要性在哪。。
</p>2019-11-02</li><br/><li><span>李先生</span> 👍（13） 💬（3）<p>胡哥，有两个问题：
1:为什么broker重启要进行日志截断，触发日志截断的前提是什么？目的是什么？
2:acks=all,是代表同步到所有isr中broker的pagecache中还是磁盘？min.insync.replicas是配合acks=all来使用的，是一个保证消息可靠性的配置，比如设置为2，是代表在isr中至少两个broker上写入消息，这个写入是写入pagecache中还是磁盘中？如果都是写入pagecache中，kafka是有异步线程来定时从pagecache中拉消息写入磁盘吗？</p>2020-04-14</li><br/><li><span>td901105</span> 👍（9） 💬（6）<p>老师您好,我怎么感觉只需要在副本拉取Leader的LOG就不会产生日志截断的问题了,感觉不需要Leader Epoch?</p>2020-01-19</li><br/><li><span>Johnson</span> 👍（8） 💬（2）<p>老师您好，有个疑问，leader epoch怎么做到像hw里的数据可见性的，比如hw可以保证消费端只能消费hw之前提交的消息，leader epoch如何保证这点，谢谢！</p>2020-04-13</li><br/><li><span>faunjoe</span> 👍（7） 💬（1）<p>多个broker 中的leader epoch 他们是版本号是怎么保持累加的</p>2020-05-10</li><br/><li><span>thomas</span> 👍（7） 💬（2）<p>倘若此时副本 B 所在的 Broker 宕机，当它重启回来后，副本 B 会执行日志截断操作，将 LEO 值调整为之前的高水位值，也就是 1。
-------------------------------------------------------------&gt;
老师，请问为什么要将LE0的值设置为HW的值。LEO的值是消息写入磁盘后才被更新的，也就是数据已经落地。重启后继续用LEO的值会有什么问题吗</p>2020-04-26</li><br/><li><span>😈😈😈😈😈</span> 👍（7） 💬（2）<p>这个是我理解的HW和LEO更新的机制步骤，有错误的话请大神指明下，非常感谢
更新对象 更新时机
Broker1上Follower副本 Follwer会从Leader副本不停的拉取数据，但是Leader副本现在的没有数据。所以Leader副本和Follower副本的高水位值和LEO值都是0
Broker0上的Leader副本 生产者向Leader副本中写入一条数据，此时LEO值是1,HW值是0。也就是说位移为0的位置上已经有数据了
Broker1上Follower副本 由于Leader副本有了数据，所以Follower可以获取到数据写入到自己的日志中，且标记LEO值为1，此时在Followe位移值为0的位置上也有了数据，所以此时Follower的HW=0，LEO=1
Broker1上Follower副本 获取到数据之后，再次向Leader副本拉数据，这次请求拉取的数据是位移值1上的数据
Broker0上的远程副本 Leader收到Follower的拉取请求后，发现Follower要拉取的数据是在位移值为1的位置上的数据，此时会更新远程副本的LEO值为1。所以所有的远程副本的LEO等于各自对应的Follower副本的LEO值
Brober0上的Leader副本 Broker0上的远程副本的LEO已经更新为1了。所以开始更新Leader副本的HW值。HW=max{HW,min(LEO1,LEO2,LEO3......LEON)},更新HW值为1，之后会发送Follower副本请求的数据（如果有数据的话，没有数据的话只发送HW值）并一起发送HW值
Broker1上Follower副本 Follwer副本收到Leader返回的数据和HW值（如果Leader返回了数据那么LEO就是2，没有数据的话LEO还是1），用HW值和自己的LEO值比较选择较小作为自己的HW值并更新HW值为1（如果俩个值相等的话HW=LEO）
一次副本间的同步过程完成 </p>2019-10-22</li><br/><li><span>Geek_0819</span> 👍（6） 💬（4）<p>胡老师有个疑问：生产者同步发送消息时指定同步到所有副本，生产者是等待所有副本的LEO都写入成功才返回吗？如果是这样Follower副本从Leader上拉取LEO是有时间间隔的，这样生产者都在这里等待很久吗？还是其他方式的交互？</p>2020-01-21</li><br/><li><span>常超</span> 👍（6） 💬（3）<p>请问老师，与 Leader 副本保持同步的两个判断条件，是OR还是AND的关系？</p>2019-08-07</li><br/><li><span>lmtoo</span> 👍（5） 💬（3）<p>“当获知到 Leader LEO=2 后，B 发现该 LEO值不比它自己的 LEO 值小，而且缓存中也没有保存任何起始位移值 &gt; 2 的 Epoch 条目”是什么意思？
如果follower B重启回来之后去取Leader A的LEO，但是此时Leader A已经挂了，这套机制不就玩不转了吗？</p>2019-08-03</li><br/><li><span>我来也</span> 👍（4） 💬（4）<p>1.该远程 Follower 副本在 ISR 中。

如果 Kafka 只判断第 1 个条件的话，就可能出现某些副本具备了“进入 ISR”的资格，但却尚未进入到 ISR 中的情况。

————————
这里是不是把条件的编号写反了？
</p>2019-08-03</li><br/><li><span>山里小龙</span> 👍（3） 💬（1）<p>”当它重启回来后，副本 B 会执行日志截断操作，将 LEO 值调整为之前的高水位值，也就是 1。这就是说，位移值为 1 的那条消息被副本 B 从磁盘中删除，此时副本 B 的底层磁盘文件中只保存有 1 条消息，即位移值为 0 的那条消息。”
这里有点不明白，主从的高水位都是1了，说明数据1已经成功同步了，为什么要把1给截断删除呢？follower重启只需要把leo值设置为1就行了，hw不用动了吧！</p>2021-02-02</li><br/><li><span>店小二#2</span> 👍（3） 💬（1）<p>引用一下@thomas与老师交流。

thomas
iii. 更新 currentHW = max{currentHW, min（LEO-1, LEO-2, ……，LEO-n）}
-------------------------------------------------------------------------------&lt;
老师， LEO-1,LEO-2...LEO-n 都是在ISR集合中的，我认为 currentHW= min（LEO-1, LEO-2, ……，LEO-n就可以，请问在什么场景下currentHW 会大于 min(LEO-1, LEO-2, ……，LEO-n）
作者回复: 有些落后很多的follower可能出现这种情况

====================================================
老师的解答的场景我理解了。但是不明白的是，该场景下，恢复过来的follower副本replica.lag.time.max.ms &lt; 10s，且还未到ISR中时，此时的分区高水位不是也大于LEO了么？
</p>2020-07-09</li><br/><li><span>亚洲舞王.尼古拉斯赵四</span> 👍（3） 💬（3）<p>我还奇怪为什么老师讲的和Apache kafka实战这部分内容差不多，还以为是抄袭，后来一看，原来老师就是我看的这本书的作者，😂</p>2019-11-06</li><br/><li><span>信信</span> 👍（3） 💬（2）<p>原文中“如果 Kafka 只判断第 1 个条件的话”--这里应该是：第2个条件？评论区其他人也有提到
对这块的个人理解：
两个条件之间的关系是与不是或
这里想表达的应该是--这个即将进入isr的副本的LEO值比分区高水位小，但满足条件2；
文中对条件2的描述好像有点歧义，以下是网上找的一段：
假设replica.lag.max.messages设置为4，表明只要follower落后leader不超过3，就不会从同步副本列表中移除。replica.lag.time.max设置为500 ms，表明只要follower向leader发送请求时间间隔不超过500 ms，就不会被标记为死亡,也不会从同步副本列中移除。 </p>2019-08-04</li><br/>
</ul>