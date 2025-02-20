你好，我是大明。我们今天接着学习消息队列的新主题——有序消息。

在消息队列的相关的面试里面，有序消息和消息不丢失、消息重复消费是三个并列的面试热点，同时在实践中也很容易遇到要求使用有序消息的场景。但是大部分人在面试的时候，无法深入透彻地讨论这个问题。大多数时候，只能说出 topic 只能有一个分区这种最简单的方案。当面试官追问这种方案有什么缺陷的时候就开始答不上来了。

所以今天我就带你深入了解有序消息的方方面面，深挖解决方案的缺陷以及对应的改进策略。

## 消息在分区上的组织方式

在 Kafka 中，消息是以分区为单位进行存储的。分区是逻辑上的概念，用于对消息进行水平划分和并行处理。每个 topic 都可以被划分为一个或多个分区，每个分区都是一个**有序、不可变**的消息日志。

Kafka 使用 WAL （write-ahead-log）日志来存储消息。每个分区都有一个对应的日志文件，新的消息会被追加到文件的末尾，而已经加入日志里的消息，就不会再被修改了。

![图片](https://static001.geekbang.org/resource/image/73/70/73ef185e2011f444026cff4d140caf70.png?wh=1920x806)

每个消息在分区日志里都有一个唯一的偏移量（offset），用来标识消息在分区里的位置。**Kafka 保证同一分区内的消息顺序，但不保证不同分区之间的顺序**。

而 Kafka 本身暴露了对应的接口，也就是说你可以显式地指定消息要发送到哪个分区，也可以显式地指定消费哪个分区的数据。
<div><strong>精选留言（18）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/28/44/cf/791d0f5e.jpg" width="30px"><span>ZhiguoXue_IT</span> 👍（8） 💬（1）<div>在订单的业务场景下，有下单消息，退单退款消息，按照订单号进行分区，保证同一个订单的数据一致性，如果是分布式环境下，退单的消息比下单的消息先到，业务一般如何处理呢</div>2023-08-24</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/20/2b/22/79d183db.jpg" width="30px"><span>H·H</span> 👍（3） 💬（2）<div>消息重试这个怎么保证有序？</div>2023-09-11</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/2a/44/e6/2c97171c.jpg" width="30px"><span>sheep</span> 👍（1） 💬（1）<div>ZhiguoXue_IT的留言中，老师这里回复了“你只需要检测有没有这个订单，或者状态是否符合，不符合你就丢回去原本的 topic 里面”，这里是丢回到原来的分区尾部？还是说创建一个生产者往对应topic发送原来的消息呢？</div>2023-12-15</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/b6/0f/e3550f48.jpg" width="30px"><span>LargeOrange</span> 👍（1） 💬（1）<div>老师你好，引入hash槽可以解决数据量平衡的问题，顺序消费的场景下，当某个槽被重新映射到新的partition下，怎么保证消息的顺序消费呢</div>2023-12-04</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/15/a3/f2/ab8c5183.jpg" width="30px"><span>Sampson</span> 👍（1） 💬（2）<div>老师这里有在使用kafka的多分区方案的时候有一个点，如果某个分区挂了，或者出发了rebalance，那消息岂不是无序了，而且对于其他业务来说也是不友好的。我之前会经常遇到这个问题，请教下这里改怎么弄呢</div>2023-08-28</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/17/ec/4c/93a84658.jpg" width="30px"><span>Zwh</span> 👍（1） 💬（2）<div>对于多分区下可能会出现的消息失序问题，新增一个乱序队列，消费者判断业务前置条件是否达成，若否就放入乱序队列，考虑增加延时和重试次数控制，乱序队列消费者收到消息后根据业务状态判断是否进行处理还是继续乱序，请问老师这个方案可行吗</div>2023-08-21</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/9f/80/2ead2573.jpg" width="30px"><span>利见大人</span> 👍（1） 💬（1）<div>老师您好，您好像忘更了关于解决消息堆积的章节哈！
这章我有两个疑问？
异步消费方案中的队列和多分区方案中的分区有什么分别？
异步消息方案中的队列不会出现数据不均匀的问题吗？</div>2023-08-11</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/17/ef/4d/83a56dad.jpg" width="30px"><span>Z.</span> 👍（0） 💬（1）<div>我有一个疑问，在新增分区失序的问题中，让新分区消费者等待一段时间在消费，这个时间是积压消息来决定的，那么等待的这段时间会产生新的消息，那要怎么界定积压消息</div>2024-05-04</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/17/96/a10524f5.jpg" width="30px"><span>蓬蒿</span> 👍（0） 💬（1）<div>我有两点疑问：
1. 使用一致性哈希解决数据倾斜问题，但无法解决单个用户的热点，比如同一个用户，使用用户ID来选择分区，短时间内这个用户的qps激增一样会出现热点以及数据倾斜
2. 增加分区导致消息失序的解决方案怎么看都不靠谱，因为消息积压了才要增加分区，说明积压消息的分区一直处于满载且缓慢流动的状态，等待3分钟可能解决了msg2和msg1的顺序问题，但会增加msg15和msg16失序的问题，本质上没有解决问题。

以上是个人浅见。</div>2024-02-26</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/19/4f/52/791d0f5e.jpg" width="30px"><span>Qualifor</span> 👍（0） 💬（1）<div>你好，请问下老师，如何做到新增的分区不让消费者消费呢？kafka 有对应的功能吗？</div>2024-01-04</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/2a/44/e6/2c97171c.jpg" width="30px"><span>sheep</span> 👍（0） 💬（1）<div>“手工调整槽的映射关系或者哈希环上节点的分布”，
1. 这里使用一致性哈希算法时候，采用插入几个分区节点来分散数据较多的分区
 1.1 这里多几个分区后，是不是一致性哈希算法的计算方法也要调整，否则只会定位在之前的分区所组成的哈希环上？
 1.2 那这里我可以不插入几个分区，转为调整发布者的一致性哈希算法，让指定分区的哈希范围变长或变短来分散数据。这样子的话，除了每个发布者都要调整算法之外，还会有其他什么问题？
2. 手工调整槽的映射关系
  2.1 会出现被调整的槽上有数据的情况吗(比如: 槽5属于分区2，然后上有槽上5个数据，这时候要调整到分区1)，这时候是否需要等待数据消费完，再进行调整呢?
  2.2 调整槽所属的分区，也会出现消息失序的情况吧？</div>2023-12-14</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/37/3f/a9127a73.jpg" width="30px"><span>KK</span> 👍（0） 💬（1）<div>在【异步消费】中，消费者线程，从kafka中取出消息之后，通过根据业务把hash放到对应的队列中，在队列中的消息一定是有序的吗？</div>2023-11-01</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/37/3f/a9127a73.jpg" width="30px"><span>KK</span> 👍（0） 💬（1）<div>“对于消费端来说，只有一个分区，那么就只能有一个消费者消费”，与前文&quot;可以显式地指定消费哪个分区的数据&quot;,是否矛盾呀？只有一个分区，就只能有一个消费者消费吗？</div>2023-11-01</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/17/2f/bb/f663ac5a.jpg" width="30px"><span>itschenxiang</span> 👍（0） 💬（2）<div>多分区，哈希槽方案我有点不太理解，通过crc16(key) &amp; 1024是能够比较均匀地分配到每个槽中吗？</div>2023-08-29</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/dc/08/64f5ab52.jpg" width="30px"><span>陈斌</span> 👍（0） 💬（2）<div>
老师你好~
1、如果某个分区消息积压了就启用异步消费，我认为思路整体方向肯定可行的，这个解决方案也会引入更多的思考点。
例如：这个解决思路就是使用线程池去异步处理消息，这就有会引出一个问题：线程池的核心线程数的问题（需要根据处理消息是CPU密集型还是IO密集型来设置核心线程个数）。还有如果要求业务内消息有序，需要考虑到同一个业务的消息应该被同一个线程执行，这个时候是否还能使用线程池去异步处理消息，线程池没有指定那个消息被那个线程消费的能力。只能手动给线程编号，然后根据业务ID去分配消息被那个线程处理，同样如果消息又被积压，一样会有增加线程数而引起消息失序的问题。还有一个问题就是如果该分区处理了10个业务的消息，其中只有2个业务消息特别多，我需要怎么把其他8个不怎么忙的业务通过异步消费的方式隔离出来，怎么做到业务之间相互解耦。  （说的有点乱）

2、数据分布不均匀：例如分库分表怎么使得分片后的数据均匀分布。流量分布不均匀：初步想到是Nginx的负载均衡算法会用到这个。</div>2023-08-13</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/10/25/87/f3a69d1b.jpg" width="30px"><span>peter</span> 👍（0） 💬（2）<div>请教老师两个问题：
Q1：借用Redis槽的思想来解决数据分布不均匀的问题，那么，同一个业务的消息会被分配到不同的分区上吗？如果同一个业务的消息被分配到不同的分区上，那么，会产生消息失序的问题吗？
Q2：有个说法是：kafka是专门用于大数据处理的消息队列，是专为大数据而生的。这个说法成立吗？（这个问题在第22课提问过了，当时打错了几个关键字，导致老师不理解，抱歉）</div>2023-08-12</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/2d/90/3b/791d0f5e.jpg" width="30px"><span>进击的和和</span> 👍（0） 💬（1）<div>老师你好
(1)如果 msg2 先到了，但是 msg1 还没出来，那么这个协调者要有办法让 msg2 的消费者 B 停下来，暂时不消费 msg1。这里好像想表达的是描述的写反了。
(2)如果想保证一个topic在多个分区有序还有什么别的思路和方法吗?
(3)关于多分区数据不均匀。因为发送方要按照业务特征来选择分区,可能造成数据不均匀,如果使用了redis的哈希槽,只是槽多了,但是这个特征还是会分配到某些槽上,这些槽对应的映射还是数据较多的那几个分区,这里还要用方式或方法来计算下呢
(4)增加分区引起消息失序。假设分区里的数据很少,等三分钟这个只是概率上会降低失序的可能,还可以监控发现问题,手动修复一下就好了。这里能不能用某种方式监控分区了没有数据才加入分区,或者说才开始给新的分区分配数据。但是就是因为消息积压严重,才需要立刻增加分区减轻消极积压分区的负担,所以不应该等消息积压分区消费完成才进行分配。这里可以在业务msg2的业务中增加逻辑,某个topic下最近一次的分区数,如发现某个topic下分区数发生变化,这个消息还是发给之前那个分区,然后修改最近一次的分区数,不知道这样行不行,并且业务逻辑太麻烦了,还有什么好的方式吗</div>2023-08-11</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/25/67/6e/ec7299ec.jpg" width="30px"><span>达芬奇</span> 👍（0） 💬（0）<div>文章写得非常好，点赞</div>2024-05-08</li><br/>
</ul>