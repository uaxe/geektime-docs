你好，我是黄鸿波。

在上节课中，我们已经了解了推荐系统的运作方式，知道了它能够为企业带来什么。本节课我们就用一个实际的案例，讲解一下推荐系统具体是怎么工作的。

我们选取Netflix开放出来的推荐系统架构作为这节课的案例，一起来看看什么是Netflix系统、Netflix系统的整体架构是怎样的。另外我还会为你讲解在线层、近似在线层和离线层之间的关系。

相信你学习完今天的内容，会对推荐系统的整体架构有更加深入的认识。

## 什么是Netflix系统？

Netflix是一家在全球多个国家提供网络视频点播的平台，用户可以付费在Netflix上观看自己喜欢的节目，这个平台的网络电影营收曾排在全美国第一名。Netflix这么高的收入，其中很大一部分原因要归功于它的推荐系统。下面这张图就是[Netflix的推荐系统架构](http://techblog.netflix.com/2013/03/system-architectures-for.html)。

![](https://static001.geekbang.org/resource/image/c6/4e/c6340108d40659623820bab2366cb34e.jpg?wh=1998x2000)

从上面这张图中我们可以发现，Netflix的推荐系统主要分为了三个大的部分，从下到上分别为在线层（Online）、近似在线层（Nearline）和离线层（Offline）。下面我们来详细地解读这三大部分所做的工作。

## 离线层、在线层和近似在线层

我们先来简单地了解一下这三层的概念。

**一般来讲，离线层包含的是需要离线工作的内容。**比如说对数据库的内容的查询、特征工程、数据处理以及数据存储相关的内容，这些都是在离线层做的。也就是说离线层指的是不需要实时给到用户反馈的内容。在推荐系统中，最基础的召回一般就是在离线层里做的。
<div><strong>精选留言（5）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/1e/14/f0/53e3ab4b.jpg" width="30px"><span>一五一十</span> 👍（3） 💬（1）<div>1. 在线层对响应时间要求较高，因此用 redis 这种内存数据结构较好；近似在线层可以用 Mysql 这种存储非海量的数据；离线曾用 hadoop hive 这些存储海量数据。
2. 后端会对召回数据做一些精细的筛选和重排后返回给用户 topN，然后将用户的操作行为再收集给到离线层。
自己理解，如果不对还请老师和同学们批评指正哈。</div>2023-04-27</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/10/25/87/f3a69d1b.jpg" width="30px"><span>peter</span> 👍（3） 💬（1）<div>请教老师几个问题：
Q1：Netflix推荐系统“开放”具体指什么？是指开源吗？或者是类似工具一类的可以拿来直接用？或者SDK？或者只是提供架构图一类的原理性解释？
Q2：近似在线层，既然是“粗排序”，怎么会是“精召回”呢？应该是“粗召回”才更合理啊。
Q3：在线层依赖近似在线层的话，怎么保证在线层的实时性？
文中提到“等到近似在线层处理完成后，会将结果输入到在线层。而在线层更多地是做了一个排序工作，它把离线特征数据和从近似在线层得到的待推荐列表组合起来”，从这句话看，在线层是依赖近似在线层。如果有依赖，近似在线层是分钟级，而在线层是50毫秒，就无法保证实时性了啊。
Q4：NetFlix的三层架构是通用的吗？
Q5：推荐系统对大数据依赖大吗？大数据框架出现之前有推荐系统吗？</div>2023-04-12</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/15/23/bb/a1a61f7c.jpg" width="30px"><span>GAC·DU</span> 👍（0） 💬（1）<div>在线层存储用户实时轨迹数据，近似在线层存储业务逻辑数据，离线层存储用户历史轨迹数据。离线数据存储在Hadoop的分布式文件系统中，其余两者存储在Kafka消息队列中。后端服务系统接收数据后，做进一步的关联查询，把最终结果推给前端服务。不知道思考的对不对？思考的过程中觉得虽然做了分层，对执行性能上做了优化，但是耦合度太高，尤其是近似实时层，承上启下，重要程度不言自明，能否可以做一个降级的方案，做到即使某一层挂了也能做到最小程度的推荐？</div>2023-04-12</li><br/><li><img src="" width="30px"><span>杜凯</span> 👍（0） 💬（0）<div>老师，我有一个问题。就是使用模型那段时的&quot;一种是直接使用用户的 ID 进行预测&quot;。如果只根据ID进行预测的话，那对于新注册用户要怎么处理呢？</div>2024-12-31</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/18/dc/b6/74cc764f.jpg" width="30px"><span>Lennyzhang</span> 👍（0） 💬（0）<div>后端服务可能会经过以下阶段：
数据验证：确保传入的数据符合预期的格式和规范。
业务逻辑处理：根据业务需求，对数据进行进一步处理，如过滤、转换、聚合等。
结果存储：将处理后的结果存储到数据库或缓存中，以便后续使用。
推荐算法：根据用户的历史行为、偏好等信息，结合计算出的结果，生成个性化的推荐列表。
结果展示：将推荐结果以合适的方式展示给用户，如网页、APP界面等。
用户反馈收集：收集用户对推荐结果的反馈，如点击、评分等，以便后续优化推荐算法。</div>2024-05-13</li><br/>
</ul>