你好，我是王喆。

刚刚结束的2020年双11活动，让技术圈出现了一个非常劲爆的新闻，就是阿里基于Flink，实现了数据的批流一体处理，每秒能够处理40亿条的巨量数据。这也是业界首次在这么大规模的数据洪峰之上，实现数据流的实时处理。

也正是因为实时数据流处理功能的实现，让阿里的推荐系统引擎能够在双11期间做出更快速的反应，实时抓住用户的兴趣，给出更准确的推荐。

这节课，我就带你揭开阿里使用流处理平台Flink的面纱，来重点解决这3个问题：

- 为什么说实时性是影响推荐系统效果的关键因素？
- 到底什么是批流一体的数据处理体系？
- 业界流行的Flink到底是怎么实现数据流处理的？

## 为什么实时性是影响推荐系统效果的关键因素？

周星驰的电影《功夫》里有一句著名的台词“天下武功，无坚不摧，唯快不破”。如果说推荐模型的架构是那把“无坚不摧”的“玄铁重剑”，那么推荐系统的实时性就是“唯快不破”的“柳叶飞刀”。那这把柳叶飞刀到底是怎么发挥作用的呢？我说个切身的场景你就明白了。

假设，你正在手机上刷抖音，你刚刚看了一个精彩的足球进球视频，感觉意犹未尽，还想看更多这样的视频。这个时候，抖音的推荐系统肯定不会让你失望，它很快会接收到“你观看了精彩进球视频”的信号，快速地抓到你的兴趣点，然后，它会迅速做出反馈，给你推送更多类似的视频。
<div><strong>精选留言（8）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/20/46/f4/93b1275b.jpg" width="30px"><span>Alan</span> 👍（50） 💬（1）<div>答：1、短视频应用的实时性要求更高！因为相同时间内，短视频用户的单视频停留周期短、场景更换频繁，用户兴趣反馈信息更多；
2、我们常说的推荐实时=7特征实时+3模型实时，都很重要！特征实时推荐是加强当前用户关注话题（现在、个别），模型训练实时推荐加强的用户未来关注的话题（下次、整体）。业界常见的做法，基于用户特征实时变化的推荐（热周期-用户活跃期），至于模型训练（或强化学习）放在冷周期（用户睡眠期）。
</div>2021-04-10</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/72/1d/abb7bfe3.jpg" width="30px"><span>顾小平</span> 👍（8） 💬（1）<div>老师你好，这篇文章说的是不是特征的实时性呢，就可以可以构建最新的用户特征去在线推断，但是在线推断跑的模型还是基于离线数据（批处理计算出来的）训练出来的模型，所以模型也需要做到准实时的更新，比如一天更新一次模型？</div>2021-01-23</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/8f/cf/890f82d6.jpg" width="30px"><span>那时刻</span> 👍（7） 💬（1）<div>相对于长视频应用，短视频应用的实时性要求更高些，因为短视频用户切换到下一个视频的时间短，需要推荐系统快速推荐短视频。

我觉得模型实时性也蛮重要的，可以让模型及时迭代。模型的实时性是模型本身快速及时的通过数据迭代模型，加强模型推荐能力。而特征实时性，可以快速而准确依据用户特征推荐内容。

想问一下老师，Apache Beam也是批流一体的模型，在业界有应用么？</div>2020-12-23</li><br/><li><img src="" width="30px"><span>Geek_91c50b</span> 👍（4） 💬（4）<div>老师，我有个疑问：文中“Spark 平台的特点是，它处理的数据都是已经落盘的数据。”，spark 不是也能直接消费kafka里的数据而不落盘，是不是spark与flink的区别其实也没这么大</div>2020-12-24</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/5a/c1/6df65e0a.jpg" width="30px"><span>190coder</span> 👍（2） 💬（1）<div>请教下老师一个短期画像架构问题。短期画像是用flink实时更新所有流的偏好，（如点击，下单，浏览等不同流）。还是只计算属于自己流内的计数,然后短期画像做统一汇总计算。</div>2021-04-25</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/23/cf/6a/42ee61a1.jpg" width="30px"><span>找大夫吗</span> 👍（1） 💬（3）<div>想请教王老师一个问题：
问题场景：短视频推荐场景下采用DSSM双塔模型召回，离线训练完之后把模型 serving上线，然后把用户和item的embedding存入redis, 想根据flink获取的实时特征（过去一小时的行为）去更新用户embedding
问题：对于像 ‘用户历史平均分均值’ 这样的input特征，可能flink都获取不到用户实时的评分数据，这种情况下该怎么做到实时特征构建呢？</div>2021-01-18</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/25/7f/db/c22a5af1.jpg" width="30px"><span>赵炯</span> 👍（4） 💬（0）<div>语音助手？？</div>2021-03-17</li><br/><li><img src="" width="30px"><span>Geek_8a732a</span> 👍（0） 💬（0）<div>1、实时性对短视频比长视频更重要，因为用户在看短视频的工程中不断产生新的点击，用户的喜好都在实时变化
2、模型的实时性也是重要的，模型的实时性可以提升模型的推荐能力，特征实时性可以根据用户的特征来更快速准确的推荐内容</div>2021-08-23</li><br/>
</ul>