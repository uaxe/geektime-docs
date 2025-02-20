你好，我是DS Hunter。

上一讲，我们提到了高收益的后端为了保护自己，进行了大量的反爬支持。但是反爬的主战场，依然是前端。

众所周知，做反爬，对于前端来说是没什么收益的，因此动力会差很多。如何解决动力问题，我们会在进阶篇深入探讨。我们目前亟待明确的，是前端在帮助后端进行反爬的时候，具体能够做些什么。

在反爬虫工作里，前端主要的作用是key加密。除此之外，还有一些杂活，比如收集信息、埋点统计等等。最后我们会把这一切聚集到规则引擎中统一收口。今天我们就先来探讨**前端反爬虫的主力部分——key的加密**。至于其它的辅助以及收尾工作，我会在下节课跟你一起探讨。

在09讲中，我们已经明确过了，服务端的key是加密后下发的。那么客户端必然需要解密方法。不过，解密方法的基础框架是什么呢？除此之外，基础框架内有什么可以用到的代码保护方式呢？我们先从第一个问题开始分析。

## 放置方式：成对加解密

这里特意发明了一个新词，叫成对加解密，和“对称加解密”这种加密方式不是一件事。我们所熟知的对称加解密是一个加解密的方式，或者说过程，而**成对加解密是一个存储方式**。

加密这件事在服务端，也就是后端已经直接执行掉了，而解密操作是发到客户端让客户端去做的。通常来说，解密操作是如何进行的呢？
<div><strong>精选留言（3）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/12/98/2c/48770f8e.jpg" width="30px"><span>王雪</span> 👍（2） 💬（1）<div>便贴集赞：backend for frontend ，BFF</div>2022-02-18</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/ec/13/49e98289.jpg" width="30px"><span>neohope</span> 👍（0） 💬（1）<div>1、所有的加解密都是执行 js，那么如果对方使用浏览器直接运行 js，是否意味着所有的加解密都形同虚设？ 如果不是，那原因是什么？
如果直接调用JS，页面元素可以做一些验证。比如：鼠标与页面元素的相对位置可能有问题，在解密时，如果将屏幕区域划分为几个格子，不同格子触发的路径不一样，是否能做为间的的防护手段呢。调用时间间隔，可能也能做一些防护。

2、成对加解密本身就存在拦截概率了，因为对方可能匹配到熟悉的题目，也可能匹配不到。那么，我们如果有意放过爬虫，要计算条件概率吗？ 如何计算呢？
是否可以这样，将加密算法分成几个Bucket，根据加解密难度及系统埋点得知的爬虫方破解情况，将算法放入到不同Bucket中，不同Bucket评分不同。在roll算法的时候，做一个分值计算，对于要放过的爬虫，只Roll难度低的Bucket中的算法。

3、成对加解密 roll 出来之后要做一次洗牌，如果不做会有什么问题吗？
这个是防止伪随机数生成时，容易生成相同队列的问题吗？这样的话，多个加密方法，就可以被看作一个大加密方法了
</div>2022-03-11</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/10/25/87/f3a69d1b.jpg" width="30px"><span>peter</span> 👍（0） 💬（1）<div>Q1：key加解密是说服务端把加解密方法告诉前端，
       由前端进行加解密吗？
       key是用来做什么的？
Q2：代码处理，也是针对前端代码吗？</div>2022-02-18</li><br/>
</ul>