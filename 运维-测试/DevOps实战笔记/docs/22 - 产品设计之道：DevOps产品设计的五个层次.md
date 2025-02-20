你好，我是石雪峰。

在上一讲中，我们聊到了企业DevOps平台建设的三个阶段。那么，一个平台产品到底做到什么样，才算是好的呢？不知道你有没有想过这个问题，反正做产品的这些年来，我一直都在思考这个事儿。直到我听到了梁宁的专栏里面讲到的用户体验的五层要素，才发现，**无论什么产品，其实都是为了解决一群特定的人在特定场景的特定问题**。

那么，回到我们的DevOps产品，我们可以借鉴一下梁宁老师的思路，来看看DevOps产品设计体验的五个层次：**战略存在层、能力圈层、资源结构层、角色框架层和感知层**。

![](https://static001.geekbang.org/resource/image/fd/8c/fd05c31feebb1fd92c845a9347e5cd8c.png?wh=1330%2A907)

这么多专有名词一股脑地蹦出来，估计你头都大了吧？没关系，接下来我会逐一解释一下。

## 第一个层次：战略存在层

在决定开发一个DevOps产品的时候，我们首先要回答的根本问题就是，这个产品解决了什么样的痛点问题？换句话说，我们希望用户通过这个产品得到什么？显然，目标用户和痛点问题的不同，会从根本上导致两套DevOps产品之间相距甚远。

举个例子，业界很多大公司在内部深耕DevOps平台很多年，有非常多很好的实践。但是，当他们准备把这些内部平台对外开放，提供给C端用户使用的时候，会发现存在着严重的水土不服问题。

有些时候，内外部产品团队有独立的两套产品，对外提供的产品版本甚至比对内的版本要差上几年。这就是用户群体的不同造成的。C端用户相对轻量级，需要的功能大多在具体的点上，而企业内部因为多年的积累，有大量的固有流程、系统、规则需要兼顾。所以，整套产品很重，甚至是完全封闭的一套体系，难以跟用户现有的平台进行打通。
<div><strong>精选留言（5）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/14/34/df/64e3d533.jpg" width="30px"><span>leslie</span> 👍（9） 💬（2）<div>    一个好的或者成功的DevOps其实要有全栈的能力：超级全能。突然想起这些年自己的职业DBA&amp;&amp;OPS：产品和研发工作中吵架-自己中间协调完后大家没问题了，开发和运维工作中吵架-中间调节然后问题解决了。换个角度解释一下老师的课程：看看是否有理。
       1.DevOps要有全栈经历：整个项目的整体任何环节都大致明白，直接全栈经历过一次；【注：我自己就差不多属于这种；从DEV-&gt;DBA-&gt;OPS-机房运维】
      此处其实是同时需要具备3个视角：用户视角、产品视角、项目视角
        2.DevOps要有一些能力：产品设计能力、项目管理能力、研发能力。
      作为一个内部项目，各种视角的切换之间才能看见问题，可是很多人不会站在对方的角度去思考问题解决问题。记得苏杰老师的课程中有句话很经典“要想否认别人的创新，你先得证明你的创新”。
       学习到现在我觉得我已经不是在学习了：享受学习沟通中的快感。老师提及的不少我都学过了差不多的东西，算是把自己这一年在极客时间学习的一堆课程做了一个梳理。极厚薄发提前规划，等待合适的时候去实现。
      谢谢老师的分享：期待下堂课的学习。</div>2019-12-05</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/15/02/66f65388.jpg" width="30px"><span>雷霹雳的爸爸</span> 👍（6） 💬（1）<div>就记得那时候做paas采购选型，灵雀时速之类的，我问你们这流水线里有没有啥自选的审批功能，我们老板比较传统，不自己当看门狗心里不踏实，都告诉我还得定制开发，我想我估计是落伍了，然后偶尔看到好像是叫weaveworks把还是啥的，gitops这玩意儿一下子就惊了，心想我咋就没想到捏，PR一统世界不远了的感觉，算是有过眼前一亮的感觉吧

其他时候大都是眼前一暗，好比说我原来在一个公司用bitbucket，PR的approval可以强制，否则不能合代码，感觉挺好，后来到一个公司图便宜咱弄个 gitlab ce吧，这功能咋也找不到，最后弄半天这得企业版才支持，这里用的社区版，好吧，那commit测试不过总可以吧，发现gitlab社区版也没这个和jenkins结合的功能，还得付费版...这玩意儿看起来有些钱还必须得花...</div>2019-12-05</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/c1/60/f5439f04.jpg" width="30px"><span>Geek_dn82ci</span> 👍（1） 💬（1）<div>个人觉得在devops领域做商业化变现，很难脱离咨询服务去单独盈利，因为市场上都是一些IT大厂才有能力做出一些具有普适性的工具软件，但企业级客户往往需要从方法论开始逐步渗透（0到1），最终可能工具软件都是添头，反而超强的咨询服务才是大头</div>2019-12-18</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/16/17/df/9cc8eb4a.jpg" width="30px"><span>DevOps在路上</span> 👍（3） 💬（1）<div>azure devops是我目前问过最好的平台，国内coding很有它的风格。对于企业来说，光靠工具真的不能解决根本效率问题，有工具当然比没有好，但是规则制定，是否愿意遵守，不管测试开发是否都理解devops敏捷的价值</div>2021-03-28</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/75/be/24a7e668.jpg" width="30px"><span>程序猿爸爸</span> 👍（0） 💬（0）<div>博云Mufan DevOps</div>2022-11-21</li><br/>
</ul>