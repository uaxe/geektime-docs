你好，我是大明。今天我们来学习一个面试中热度极高的话题——分布式锁。

分布式锁和分布式事务，可以说是分布式系统里面两个又热又难的话题。从理论上来说，分布式锁和分布式事务都涉及到了很多分布式系统里面的基本概念，所以我们不愁找不到切入点。从实践上来说，分布式锁和分布式事务都是属于一不小心就会出错的技术手段。

在面试分布式锁的过程中，我发现大部分人只知道很基础的几个点，比如说只能回答出使用 SETNX 命令，又或者能答出要设置超时时间。当进一步追问的时候，就不知道了。

那么今天我就带你全方位学习分布式锁的知识点，确保你在这个话题之下能够赢得竞争优势。

## 能用于实现分布式锁的中间件

这一节课的主题是用 Redis 来实现一个分布式锁，但是并不意味着分布式锁只能使用 Redis 来实现。

简单来说，**支持排他性操作**的中间件都可以作为实现分布式锁的中间件，例如 ZooKeeper、Nacos 等，甚至关系型数据库也可以，比如说利用 MySQL 的 SELECT FOR UPDATE 语法是可以实现分布式锁的。

## 面试准备

你在公司里面要收集一些信息。

- 你们公司有没有使用分布式锁的场景？不用分布式锁行不行？
- 你们使用的分布式锁是怎么实现的？性能怎么样？
- 你使用的分布式锁有没有做什么性能优化？
- 你使用的分布式锁是如何加锁、释放锁的？有没有续约机制？
- 在使用分布式锁的时候，各个环节收到超时响应，你会怎么办？
<div><strong>精选留言（10）</strong></div><ul>
<li><img src="" width="30px"><span>Geek_84f004</span> 👍（3） 💬（1）<div>老师您好，Singleflight模式多次提到了，但如何实现这个模式，老师有比较好的建议吗?比较害怕的是在这个模式下可能有太多的线程处于等待状态？是否有隐患</div>2023-09-13</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/17/8a/7a/54003392.jpg" width="30px"><span>Geek_27a248</span> 👍（0） 💬（1）<div>老师，在工作中，哪些场景可以用到分布式锁呢，尤其是锁的可重入特性</div>2024-04-22</li><br/><li><img src="" width="30px"><span>刘洁</span> 👍（0） 💬（1）<div>老师您好，提到：“如果重试一直都超时，这个时候也不需要额外处理。因为如果之前加锁已经成功了，那么无非就是过期时间到了，锁自然失效。如果之前没有加锁成功，就更没事了，别的线程需要的时候就可以拿到锁。” 这里一直超时，是有网络问题了，锁失效或没有锁情况下，其他线程怎么会在有网络问题下拿到锁？</div>2024-04-07</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/28/d6/6a/1d844a27.jpg" width="30px"><span>冲冲冲</span> 👍（0） 💬（1）<div>redLock 加锁多数原则 ，5台机器为啥加锁4个成功，有一个超时失败要把其他四个解锁尼，不是已经超过半数了吗</div>2023-10-23</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/3c/fa/e2990931.jpg" width="30px"><span>文敦复</span> 👍（0） 💬（1）<div>Singleflight 模式 来优化竞争，感觉需要处理很多复杂问题：选择哪个线程去竞争？获取锁过程中，如果这个线程奔溃，如何通知其他线程？获取锁过程中，其他线程如何自处（直接失败？等待失败? 等待成为竞争者？）
感觉不玩这个奇技淫巧，大开大合，以力破巧更实在，要不然被面试官绕进去，那就尴尬啦...</div>2023-10-11</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/3c/fa/e2990931.jpg" width="30px"><span>文敦复</span> 👍（0） 💬（1）<div>请教下：“如果 key1 存在，检查值是不是 value1。如果是 value1，那么说明我上一次加锁成功了。考虑到距离重试的时候已经过去了一段时间，所以需要重置一下过期时间。” 如果 key1 都存在了，不就代表上资源被占用了吗，这次加锁应该算失败吧，还继续操作干嘛?</div>2023-10-11</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/10/25/87/f3a69d1b.jpg" width="30px"><span>peter</span> 👍（0） 💬（1）<div>请教老师几个问题：
Q1：线程1设置key1=value1，线程2设置key1=value2能成功吗？
键相同，都是key1，但值不同，可以设置吗？
Q2：订阅键值对，是Redis已经具备的功能吗？还是需要进一步开发？
Q3：释放锁的时候，线程1为什么能把线程2的锁释放掉？两个锁应该是不同的锁啊。
Q4：释放锁的时候，比较value，是谁比较？Redis比较吗？</div>2023-09-13</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/2b/03/03/d610f362.jpg" width="30px"><span>@</span> 👍（0） 💬（0）<div>老师，虽然通过hash同一个key只会路由到同一个节点。         要保证不出现并发问题，节点上的服务也是不能用多线程的web框架吧</div>2024-06-04</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/36/f3/d4/86a99ae0.jpg" width="30px"><span>哆啦a喵</span> 👍（0） 💬（0）<div>这里redis实现的分布式锁是不是获取和释放锁的操作，都需要用lua脚本来实现，保证原子性？</div>2024-05-13</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/2a/44/e6/2c97171c.jpg" width="30px"><span>sheep</span> 👍（0） 💬（0）<div>课后问题：
1. 重试时候，要考虑重试次数还有重试间隔
2. 有一个分布式锁无效的情况，就是异地部署情况下，两个服务使用的都是自己的redis，这时候使用redis分布式锁无效（因为两个服务没有连到同一个redis中间件么），
但存在只允许一个服务进行执行指定业务的场景。这里有两个服务，B服务（备用业务服）连的数据库是作为A服务（主业务服）连的数据库的备用数据库，数据库MySQL主备数据之间是有进行同步。因此这里做了一个比较简易的方案，就是A服务和B服务定时执行一个业务时，A服务往一个业务执行表（tbl_lock_record）插入一条数据，B服务要执行时，延迟1~2s（考虑到主备数据库延时问题），然后先判断tbl_lock_record表内指定时间范围有没有执行过的数据（ 当前时间-定时时长-延迟时长&lt; time &lt;= 当前时间），若有则B服务不进行执行定时任务。
同样，这种方法也存在挺多问题：
（1）时间判断不准确情况下，可能两个服务都会执行
（2）若主备数据同步失败（例如延迟时长内数据还未同步），B服务也会进行执行</div>2024-02-19</li><br/>
</ul>