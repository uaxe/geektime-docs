你好，我是徐昊，今天我们来继续学习AI时代的软件工程。

上节课我们介绍了在不同的认知行为模式下与大语言模型（Large Language Model，LLM）不同的交互模式。我们可以通过提示词模版建立任务和流程，来应用显式知识和充分学习的不可言说知识；通过已经提取完成的思维链，指导知识生成、产生任务列表，以消费不可言说知识。

那么通过LLM辅助的不同认知模式，真的会带来效率的提升吗？这是我们今天讨论的问题。

## 通过自动化带来的效率提升

通过LLM辅助不同的认知模式，一个显而易见的效率提升是由于**知识外化带来的复用**。比如，[上节课](https://time.geekbang.org/column/article/758937?utm_campaign=guanwang&utm_content=0511&utm_medium=geektime&utm_source=pinpaizhuanqu&utm_term=guanwang)我们提到的**清晰认知模式**中的任务模板：

```plain
需求背景
=======
{requirements}

API要求
=====
API返回的结果是json格式；
当查找的SKU不存在时，返回404；
按关键搜索功能使用POST而不是GET；

任务
===
按照API要求为需求设计RESTful API接口。使用RAML描述。
```

可以看到，在这个模板中**API要求**的部分与需求背景部分是**正交**的。也就是说，无论针对何种需求背景，都可以依照同样的API要求，进行任务的操作。那么，对于API要求这部分的知识提取，就是可复用的知识。
<div><strong>精选留言（7）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/11/7a/56/29877cb9.jpg" width="30px"><span>临风</span> 👍（15） 💬（2）<div>    之前老师给我的留言回复LLM对复杂模式的帮助比庞杂模式大，还不是很理解，今天算是揭晓答案了。庞杂模式是对不可言说知识的提炼和拆分，直接自己写和让LLM帮忙效率是差不多的。但复杂模式不同，复杂模式之前的困难是在于探测-感知-响应的循环过慢，导致知识提取的效率过慢，而LLM因为已经掌握了大量知识，可以作为个人的一对一指导老师，效率自然就提高了不少。
    不知道大家注意到了没有，我觉得今天这篇文章的核心词是“复用”。过去我经常感慨，上个世纪的程序员为什么这么厉害，一个人就能完成一个软件的开发，而现在的人就只会调接口，已经丧失了从零编写一个软件的能力 。除了这些大神本身天赋异禀之外，可能更大的原因就在于复用，我们这代人，必须要基于现有的框架体系内去拓展，现实已经证明重复造轮子是低效且缺乏价值的。但为了复用已有的框架，我们要学大量个人品味的东西，而不需要接触代码底层的更核心的东西，诸如为什么是用注解定义而不是xml定义，为什么这个地方实现用组合而不是继承，为什么用双引号而不是单引号，为什么是用Java而不是go等等。
    复用本来是为了解决多人协作重复造轮子的低效，反而又增加了新的学习负担。但LLM可能会重新改变这一局面，当LLM可以通过更高效的方式对不可言说知识进行复用，我们就不用去学习每个人框架开发者的品味，不用去在意开发语言或框架，而这正是未来软件发展的方向。</div>2024-03-20</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/16/e8/c9/59bcd490.jpg" width="30px"><span>听水的湖</span> 👍（0） 💬（0）<div>第一章课程学习反馈收集链接，看完第一章内容的同学记得填写哦！https:&#47;&#47;jinshuju.net&#47;f&#47;YzTEQa</div>2024-03-20</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/51/6e/efb76357.jpg" width="30px"><span>一只豆</span> 👍（7） 💬（0）<div>二刷课程时又读到这里：清晰模式下的任务自动化；庞杂模式下的认知对齐；复杂模式下可以快速探索。。。忽然觉得这三条几乎已经是整个技术史和文明史的高度概括！工业革命是从自动纺纱机开始，现代组织的巨大能量是从战略共识启动的，整个互联网经济的核心就是建立更有效率的创新体系。。。
感觉课程聚焦在软件开发好像委屈了老师和 大模型与知识工程之间的化学反应～～</div>2024-03-22</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1c/f6/27/c27599ae.jpg" width="30px"><span>术子米德</span> 👍（1） 💬（0）<div>🤔☕️🤔☕️🤔
【Q】根据不同的测试策略，如何引入LLM？
【A】测试策略，Test Strategy，在开发周期内，确定何时何地怎么测试的策略。
如果，我的开发周期里，存在发布这个节点，那么，至少存在端到端测试，所谓End-to-End Testing，或者叫接受测试，所谓Acceptance Testing或System Testing；如果，我的开发在代码提交前，进行模块级别独立验证，那么，大概率存在单元测试，所谓Unit Testing；如果，我们的开发体系庞大，模块会被集成到不同组件或产品，那么，大概率存在集成测试，所谓Integrated Testing。这么好，那么现在就假设，ST、IT、UT，它们都好好在那里。
最接近客户的是ST，最接近组织的是IT，最接近开发的是UT。
客户的想法，不容易全懂，要摸着石头过河；组织的战略，关注新机会，要多种选项组合；开发的交付，明确和具体，要清晰不要糊涂。
LLM跟ST在一起，大概率是复杂（Complex）认知模式；LLM跟IT在一起，大概率是庞杂（Complicated）认知模式；LLM跟UT在一起，大概率是清晰（Clear）认知模式。
— by 术子米德@2024年3月23日</div>2024-03-23</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1c/f6/27/c27599ae.jpg" width="30px"><span>术子米德</span> 👍（1） 💬（0）<div>🤔☕️🤔☕️🤔
【R】效率提升 = 知识外化带来的复用
团队效率的根源 = 知识传递的及时准确性
【.I.】原来，这些知识在我的肌肉记忆里，跟着我的手势，靠你的天赋和悟性，才能习得。如今，提炼为模板的提示词工程，可以拿来反复跟LLM聊天，肌肉记忆变成聊法。我是肌肉记忆的主角，我是提示词的提取者，我是反复跟LLM聊天人，我把自己的不可言说知识，以提示链或任务列表的形式，变成我的日常稳定可用显式知识，让自己从复杂降到庞杂、再进入清晰，我自己的收益显然无疑。
【Q】你拿到我的提示词，跟LLM聊出的东西，真的也会复杂到庞杂、再进入清晰嘛？你和我的哪些不同方面，会影响到这个过程的发生？
— by 术子米德@2024年3月20日</div>2024-03-23</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/1d/de/62bfa83f.jpg" width="30px"><span>aoe</span> 👍（1） 💬（0）<div>在学习 Android Jetpack Compose 时借助 Copilot AI 插件确实提升了知识传递的及时性、准确性
两周周学习过程：
1. 「无 AI 介入」在官网阅读入门文档、观看入门视频解了 Jetpack Compose 的基本概念：如何创建一个页面、页面布局有哪些主要控件、控件在页面的位置如何调整
2. 「无 AI 介入」运行了最先发现的示例代码
3. 「无 AI 介入」按自己的想法开始了一个项目：点击按钮随机生成卦象、数字、十二星座、十二生肖
4. 「AI 介入」通过和 AI 对话进行开发功能：添加一个 Jetpack Compose Button；选中 Button 代码后，要求将 Button 变成圆形、改个颜色；画一条线；添加一个 Drawer 控件等
5. 「AI 介入」通过和 AI 对话添加了一个 codecov 插件在 Github Workflows 中上报测试覆盖率
6. 「无 AI 介入」开发到一周时，发现因严重缺乏 Android 基础知识，导致开发进度缓慢，买了一本《Head First Android 开发（第三版）》准备学习，此时还没看，硬和 AI 聊天完成了第一版功能
7. 「AI 介入」和 AI 聊天也没能解决的问题：测试 Compose 布局，运行时需要借助 Android 模拟器，自己写的测试代码，运行后的报错信息 AI 也不能帮助解决
8. v1.0.0 版本已发布，源码地址 https:&#47;&#47;github.com&#47;aoeai&#47;aoeai-qigua-android</div>2024-03-20</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/94/1c/97aa234c.jpg" width="30px"><span>止😊</span> 👍（1） 💬（0）<div>精彩</div>2024-03-20</li><br/>
</ul>