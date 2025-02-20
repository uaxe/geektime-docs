你好，我是蒋宏伟。从今天起，我们进入了一个新的篇章，新架构原理篇。

在此之前，我们所学的核心基础篇、社区生态篇、基础设施建设篇都是贴近应用层面的知识，而在新架构原理篇中，我们会重点学习偏底层的纯技术类知识。

看到这儿你可能会问了：“我们在日常工作中很难用得到框架原理呀，学习这个到底有什么意义呢？”

这个问题问得非常好，其实我们换个角度来看就豁然开朗了：“如果只学那些日常会用到的、别人也会知识点，我的职业竞争力在哪里？”

掌握那些大家都会的应用层面的知识只是及格，要想更进一步，我们就要有更高的技术追求。我认为学习底层框架的意义不在于“内卷”，也不在于为了面试去背八股文，**为的是解决别人解决不了的问题，为的是“创新”**。

“人无我有，人有我优”，才是你的核心竞争力。

不过，在深入学习 React Native 新架构的原理细节之前，我想先带你对比下小程序、Flutter、React Native之间的架构，让你先从宏观上理解各大框架的架构差异，为后续深入原理打下基础。

## 小程序

我们先来看小程序。

**从技术上说，小程序是在一个应用程序中再嵌入另一个应用程序，**也就是说微信本身就是一个应用程序，而小程序就是微信应用程序之上的程序，这在国内独有现象，国外是没有的。
<div><strong>精选留言（5）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/25/29/28/b6b73f57.jpg" width="30px"><span>大龙龙龙</span> 👍（6） 💬（2）<div>1. Flutter 双端一致性以及跨端性能最好的，缺点是不支持热更新。 
2. RN性能介于hybrid和flutter之间，但是支持热更新， 缺点是兼容性比较差，一致性以及性能都没有flutter好。
3. 小程序的缺点应该是受到的限制比较多，且只能嵌在微信之中，优点是无需安装，更加轻量级，维护开发成本更低。</div>2022-08-29</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/ec/38/409b35f0.jpg" width="30px"><span>魑魅魍魉👽</span> 👍（0） 💬（1）<div>老师，您好，请问ios 使用hermes，会影响热更新吗？</div>2022-10-28</li><br/><li><img src="" width="30px"><span>app_html_center</span> 👍（3） 💬（0）<div>关于 三种跨端思路 对比结论的疑问：

&gt; 问题一：为什么测试环境不保持一致？
&gt; 问题二：为什么没有 Flutter 和 RN-like 方案直接对比的结果？
&gt; 问题三，来自灵魂的拷问：是不是作者水平有限，才得出这种的结论？</div>2022-07-24</li><br/><li><img src="" width="30px"><span>app_html_center</span> 👍（1） 💬（0）<div>关于简版的架构对比，有一个疑问：

这种简版的模型，可以用在任何 UI 平台上，包括 Android&#47;iOS&#47;Windows，怎么可以得出 &quot;Flutter 和浏览器的架构非常相似&quot; 这种结论呢？</div>2022-07-24</li><br/><li><img src="" width="30px"><span>app_html_center</span> 👍（0） 💬（2）<div>666，很客观、很宏观、很全面、很中肯、很前瞻、很有价值</div>2022-07-24</li><br/>
</ul>