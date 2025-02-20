上一篇文章我们讲了雅虎的广告预估模型。雅虎早期的模型主要集中在如何利用两轮架构来对点击率进行精确建模，后期的模型回归到了比较传统的利用线性模型外加特性哈希来进行大规模点击率预估的模式。

今天，我们继续来做公司的案例分析，结合论文《LASER：在线广告的可扩展响应预测平台》（LASER: a scalable response prediction platform for online advertising）\[1]，来了解LinkedIn这家公司是怎么来做最基本的广告预估的。

## LinkedIn广告预估模型

我们首先来看一看LinkedIn的广告预估模型。这个模型的一大“卖点”就是直接充分考虑了“冷启动”和“热启动”两种模式。

那么，什么是“冷启动”，什么又是“热启动”呢？

从我们之前的分享中可以看出，很多点击率预估的模型，都强烈依赖于对用户过去信息以及对广告过去表现的建模。比如刚刚讲过的雅虎预估模型，在它早期的模式中就已经见到了这种信息的作用。

然而，当我们出现新用户或者新广告时，就会有“冷启动”的问题。也就是说，“冷启动”主要是针对新用户或者新广告而言的。这时候基于历史信息的特性都无法起作用了，一般来说需要有专门的处理。
<div><strong>精选留言（2）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/10/30/b6/fedb6472.jpg" width="30px"><span>艾熊</span> 👍（12） 💬（0）<div>洪博士，通过一篇论文的简单导读来探讨业界应用的话，希望能够听到更深层次更多角度的东西。毕竟，这篇论文所是pr还是内部真的在应用了，应用效果是什么，现在是否还在用，真正应用中卡主的可能是一些没有在论文里写出来的东西…这些都不得而知。论文表层的东西确实给了题目大家去一看也就是这样，那么希望洪博士多提供一些发散的和批判性的分析，甚至遗留的问题也是比较好的点。感觉每一次留下来思考的点几乎没有反馈和交互…就比如小时候留了作业不需要检查和上交，那大家也就失去了互动的动力了。</div>2018-06-20</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/10/0f/0e/e85fb4f9.jpg" width="30px"><span>Ad</span> 👍（5） 💬（0）<div>請問如何達成個人化的係數，在實作上有點無法想像</div>2018-06-18</li><br/>
</ul>