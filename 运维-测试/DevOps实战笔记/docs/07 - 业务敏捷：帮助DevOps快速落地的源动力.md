你好，我是石雪峰，今天我要跟你分享的主题是业务敏捷，那么，我们先来聊一聊，什么是业务敏捷，为什么需要业务敏捷呢？

先试想这样一个场景：你们公司内部成立了专项小组，计划用三个月时间验证DevOps落地项目的可行性。当要跟大老板汇报这个事情的时候，作为团队的负责人，你开始发愁，怎么才能将DevOps的价值和业务价值关联起来，以表明DevOps对业务价值的拉动和贡献呢？

如果朝着这个方向思考，就很容易钻进死胡同。因为，从来没有一种客观的证据表明，软件交付效率的提升，和公司的股价提升有什么对应关系。换句话说，软件交付效率的提升，并不能直接影响业务的价值。

实际上，软件交付团队一直在努力通过各种途径改善交付效率，但如果你的前提是需求都是靠谱的、有效的，那你恐怕就要失望了。因为，实际情况是，业务都是在不断的试错中摸着石头过河，抱着“宁可错杀一千，也不放过一个”的理念，各种天马行空的需求一起上阵，搞得软件交付团队疲于奔命，宝贵的研发资源都消耗在了业务的汪洋大海中。但是，这些业务究竟带来了多少价值，却很少有人能说得清楚。

在企业中推行DevOps的时间越长，就越会发现，开发、测试和运维团队之间的沟通障碍固然存在，但实际上，业务部门和IT部门之间的鸿沟，有时候会更加严重。试问有多少公司的业务方能够满意IT部门的交付效率，又有多少IT团队不会把矛头指向业务方呢？说白了，就一句话：**如果业务不够敏捷，IT再怎么努力也没用啊！**所以，我觉得很有必要跟你聊一聊有关需求的话题。
<div><strong>精选留言（12）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/13/17/27/ec30d30a.jpg" width="30px"><span>Jxin</span> 👍（20） 💬（3）<div>1.卡洛模型我们的产品团队也有在用，但很遗憾的是，收效甚微差距巨大，但我深知不怪我们的产品团队。因为作为2b的业务，产品的价值都是业务方提出或者评定的。然后这个价值评定就是笑话，风风火火搞一两个月的大项目，原本业务提出能接入xxx客户，带来xxx价值，结果接入廖廖无几。当站在最前面的一波人都是来搞笑的，你后面再怎么折腾也翻不起浪。深刻觉得业务方都停留在我觉得，而没真真走出公司站在市场，用客观的数据和长期经验来评定需求价值。

2.mvp前面还有个mvp，在最小可行产品出来前，应该要筛选最小价值产品（v=valuable）。挖掘追小价值产品方案，排优先级，然后再制定最小可行产品，去试验反馈改进升级。业务驱动往上再看一点是价值驱动。但这种模式偏爱短期价值，势必会导致长期价值的产品难以推行。但就当下而言还是比较适用的，因为变化太快，长期价值的风险系数太高，贴现率太低了，远不如短期价值来得靠谱。</div>2019-11-08</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/34/df/64e3d533.jpg" width="30px"><span>leslie</span> 👍（6） 💬（2）<div>     其实老师的课程提到一点：核心需求；经历过一些企业，和一些同行沟通过，如何梳理出真实的核心需求似乎是个典型问题或者说通病。
     最核心最有价值的东西展现或挖潜出来才可能绕着去做：其实之前有学习极客时间里关于产品的课程，今天的课程中所提及的MVP的概念以及需求的价值，就像为什么DevOps是提升效率；当我们结合产品就会发现其中的核心理念是有所相通的。
      进一步举例说明：产品经理为何很多时候和技术对立；可是如果是真正懂技术或技术转产品的会更加明白其中的方式方法。其实DevOps同样是一个产品：技术团队本身的产品。</div>2019-10-26</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/19/d4/fc/c92a0623.jpg" width="30px"><span>Eric Yi</span> 👍（5） 💬（1）<div>关于用户需求故事的拆分，再进入每一个迭代，能否举一个具体例子？这样会更好理解一点。</div>2019-10-27</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/13/37/3b/495e2ce6.jpg" width="30px"><span>陈斯佳</span> 👍（4） 💬（1）<div>一切技术还是要围绕业务的需求来展开，作为后端的技术支持团队其实也可以主动影响业务需求的定义，从而适配之后整个开发流程。也许一个好的DevOps工程师就是一个业务和技术的翻译官吧</div>2019-10-31</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/a8/e8/bc84c47d.jpg" width="30px"><span>熊斌</span> 👍（2） 💬（1）<div>记得2015年我们公司负责推行敏捷开发的领导来培训敏捷，培训完毕后采用的是“自顶向下”的路径推行敏捷开发。
当时团队领导拿到需求后先拆分，将拆分后的需求写在纸条上面，贴在看板上让大家去领任务。

刚开始大家的积极性很高，每天有任务进度汇报，早上还有“站立会”。可是久而久之大家就疲惫了，没有人去关注看板上面的东西，也不再开站立会，又回到了原来的状态。

由此可见，知道容易，做到是很难的，尤其是在一个庞大的协作体系内。</div>2019-10-28</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/13/08/5f/b8dc0e5b.jpg" width="30px"><span>iiiqueena</span> 👍（0） 💬（1）<div>感觉又把ACP的课上了一遍，不过老师你讲的挺好。</div>2019-10-28</li><br/><li><img src="https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJl5efMibfHzgs3aOYJAUxZ4vpak1mXfe4eVHibIfwbjS7zswNgvN95icn7WarUy98TRWV8YOO9drJTg/132" width="30px"><span>Geek_62e3e7</span> 👍（2） 💬（0）<div>老师你好，关于需求拆分的粒度，之前阿里内部确实这么拆分过，然后对需求交付时间考核，大家就很聪明的把需求越拆越小，反而失去了度量的意义，这种情况你们内部有吗？如何解决这种问题</div>2023-01-31</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1d/3f/0d/1e8dbb2c.jpg" width="30px"><span>怀揣梦想的学渣</span> 👍（0） 💬（0）<div>文中讲到了用户价值，我理解的是，满足用户需求，提升用户满意度，就是用户价值的具体体现。我做过3年的面向通信公司的产品交付，做过2年面向制造业的产品交付，我的感受是，用户的心声需要一线人员收集，愿意主动分享需求的比较少，稍有阻力就不会反馈问题或者提需求，只会让乙方去猜测推测。
常见方法是留一个便捷的渠道让客户反馈需求。
我的方法是主动融入客户的群体，让客户把我这里当作树洞，对产品的不满随时可以骂过来，我去掉情绪话，总结梳理后，反馈给公司内部，并且将公司内部的进展同步给客户，让客户感受到被重视，让公司内部可以看到客户需求优先级。让客户看到自己扔来的石头有溅起水花，而非进入无底洞。
一些沟通中发掘的需求，需要和客户多一些细致的交流分辨优先级，分辨重要程度。并非客户经理喝酒可以搞定，也并非产品经理用复杂公式和先进流程可以分析出结果。
我印象比较深的一次产品交付，有国内主流厂家都去竞标，试用阶段，一家厂商因为曾经对客户的需求无回应，直接在试用阶段出局，我要交付的产品虽然是客户期望度比较高的产品，但我一直是抱着怀疑的态度先去探查客户真实的需求。和客户闲聊是发现，客户对A功能十分需要，并且每天都要用。但客户认为A功能是主流厂商产品默认有的，不需要单独提。但做从技术实现角度看，A功能必须额外准备其他资源才可以实现，在特定业务场景并不会标配A功能，只有在低端普通场景才会标配A功能。如果没有这些探查，整个产品团队会一致认为我们的产品是最符合客户需求的，并且会吐槽客户需求变化真多。客户也会一致认为这乙方真脑子冒泡，基础需求都不能理解，还要我们多轮去讲解，难道不能一次交流清楚。</div>2023-06-01</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/2d/90/b7/b19aafac.jpg" width="30px"><span>Mr_Sun</span> 👍（0） 💬（0）<div>老师您好 关于您讲到的bizdevops 我有几点疑问 。1、如果让开发参与到业务过程影响开发效率问题怎么解决，如何平衡2、在用户使用产品过程中遇到的问题，是否需要开发一起协助解决，用户提出的工单解决流程具体如何优化更有效果，具体应该如何分配3、在实践中，运维人员在业务和敏捷中的比例应该怎么分配</div>2022-04-24</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/67/63/abb7bfe3.jpg" width="30px"><span>atom992</span> 👍（0） 💬（0）<div>谈需求拆分的时候，是否可以结合DDD呢？如何结合？</div>2020-12-18</li><br/><li><img src="https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJp4KDwoPkxZGo9yAKUiaI2uaHy87QuW1l0gV5LbJekbffsKJodWtI61V4kNXbOHep1DTGjABxoHhg/132" width="30px"><span>Leiting</span> 👍（0） 💬（1）<div>我们单位的工作都是基于是否能直接产生效益？能直接产生效益的，才是好工作。这个观点，怎么才能有限推进DevOps呢</div>2020-05-26</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/18/22/97/7a1c4031.jpg" width="30px"><span>Raymond吕</span> 👍（0） 💬（0）<div>这个时候就需要一个教练，天天盯着，答疑解惑。</div>2020-02-27</li><br/>
</ul>