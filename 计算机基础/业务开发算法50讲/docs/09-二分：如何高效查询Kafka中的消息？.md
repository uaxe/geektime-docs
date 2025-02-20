你好，我是微扰君。

今天我们来学习另一个常用的算法思想，二分法。这个算法思想相信即使你没有什么开发经验也不会感到陌生，而且之前讲红黑树的时候我们也简单聊过。

不知道你有没有玩过“猜数字”的游戏。大家规定一个范围，一个人在心里想一个这个范围内的具体数字，比如一个1-100的自然数，然后另几个人来猜数字；每次猜错，这个人都会提示他们的猜测是大了还是小了，看谁最快猜到数字。

如果你做这个游戏会怎么猜呢？从1开始顺次猜吗？我反正不会这么猜，出于一个很简单的直觉，如果1猜错了，那么出题的同学给你的提示对可选范围的缩小非常有限，也就是从1-100变成了2-100。

我想很多人第一反应也都会是从比较中间的位置，比如50，开始猜起。毕竟如果50猜错了，因为要提示是大了还是小了，范围就要么缩小到1-49，要么缩小到51-100，这样猜测范围就可以成倍的缩小。

所以，**如果每一次我们都猜测可能范围内的中间值，那么即使猜错了也能成倍的缩小范围，这样的策略其实就是二分查找算法**。

有了二分查找算法，即使更大的范围内进行游戏，比如在1-1,000,000的范围内，我们按照二分的策略，最多也只需要20次即可完成任意数字的猜测，这是遍历数字猜测所远远做不到的。可以看下图有一个直观的认知。  
![](https://static001.geekbang.org/resource/image/d1/cf/d1f036f97b3e08f446b70071f4a474cf.jpg?wh=2312x1379)
<div><strong>精选留言（9）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/17/06/7e/735968e2.jpg" width="30px"><span>西门吹牛</span> 👍（4） 💬（1）<div>B+ 树就是为了磁盘存储而生，可以减少磁盘的访问次数，同时也可提供顺序访问，Kafka 采用顺序稀疏索引文件，同一分区的 log 都是顺序写的，采用稀疏索引，一方面节省空间，只要找个开始的位置，顺序遍历即可，这也和场景有关，消息是按分区顺序写入，消费端是按分区顺序成批拉取，二分找到起始位置，顺序读取即可，读写磁盘都是分区内顺序读写</div>2022-01-22</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/13/50/2b/2344cdaa.jpg" width="30px"><span>第一装甲集群司令克莱斯特</span> 👍（2） 💬（1）<div>应该整理一下常用中间件的索引类型
MySQL innodb: B+ Tree
Oracle&#47;Mongodb:B Tree
ES:倒排索引
Kafka:稀疏索引
这节还学到了热区，冷区，还有缺页中断。</div>2022-01-03</li><br/><li><img src="" width="30px"><span>Paul Shan</span> 👍（1） 💬（1）<div>索引文件和红黑树查询量级是一样的，都是log n，索引文件实现简单，红黑树实现复杂，红黑树可以插入删除，合并起来可以对一个节点Key做任意变化，索引文件对于频繁的插入删除，效率会退化，最后往往需要O(n)的复杂度去重建索引，代价比较大。</div>2021-12-30</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/60/5a/3b2cdae0.jpg" width="30px"><span>宋照磊</span> 👍（0） 💬（1）<div>我的理解稀疏索引对应的场景是因为经常要顺序批量查询，而MySQL常用于随机查询，所以用树结构</div>2022-01-04</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/fe/a2/5252a278.jpg" width="30px"><span>对方正在输入。。。</span> 👍（0） 💬（2）<div>老师我是这样理解的：稀疏索引的方式和b➕树比起来最大的不同是稀疏索引把所有索引都放到一层，b➕树有m层，所以这样看起来洗漱索引优点是实现简单，但是不利于大数据量的存储，如果量很大，导致这一层的索引文件太多，会严重影响这一层的二分查找的效率。消息队列的消息存活一般都有一定时间限制的，kafka就是默认7天有效，单个partition的数据量一般都不会太大，就算如果量太大也可以采用横向扩展分片树的方式来控制每个partition的数据量上限。消息队列的这一特性保证了单个partition的数据量上限，所以选择了实现简单的稀疏索引</div>2022-01-02</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/25/78/dc/bcdb3287.jpg" width="30px"><span>丶</span> 👍（0） 💬（1）<div>get： 冷热分区 + 二分查找。 感觉自己还得再补补计算机基础了。</div>2021-12-30</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/ff/e9/276b9753.jpg" width="30px"><span>SevenHe</span> 👍（4） 💬（0）<div>二分查找其实除了用于算法和工程实战以外，解决实际问题的时候也可以考虑采用二分查找的思想，比如快速定位Bug的位置</div>2022-03-24</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/17/95/af/b7f8dc43.jpg" width="30px"><span>拓山</span> 👍（1） 💬（0）<div>1、B+树支持范围查、顺序查等能力，且由于索引层级少，很适合磁盘文件读的场景，但数据库的写能力没有kafka要求那么高。
2、kafka的特性是快！因此它不能严格按照B+那种严格的存储顺序去写入。它采用的稀疏hash、追加文件方式都是突出写入快读取快的性能，但它就不能做范围查询、索引查询了。</div>2023-08-09</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/19/6b/e9/7620ae7e.jpg" width="30px"><span>雨落～紫竹</span> 👍（0） 💬（0）<div>第一 修改 第二 只有叶子结点存储数据 </div>2022-07-11</li><br/>
</ul>