你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

目前我们的架构愿景如下：

![](https://static001.geekbang.org/resource/image/ed/2e/ed95e0629105b3fe661590be6ab4af2e.jpg?wh=2284x1285)  
![](https://static001.geekbang.org/resource/image/aa/56/aacdc2230e337d593308c0184b799956.jpg?wh=2284x1285)

在继续拆分不同模块的任务之前，我们先回顾一下伦敦学派的做法：

- 按照功能需求与架构愿景，划分对象的角色和职责；
- 根据角色与职责，明确对象之间的交互；
- 按照调用栈（Call Stack）的顺序，自外向内依次实现不同的对象；
- 在实现的过程中，依照交互关系，使用测试替身替换所有与被实现对象直接关联的对象；
- 直到所有对象全部实现完成。

到目前为止，我们完成了第一层调用栈的测试。也就是以ResourceServlet为核心，测试驱动地实现了它与其他组件之间的交互。因为大量地使用测试替身（主要是Stub），我们实际上围绕着ResourceServlet构建了一个抽象层。

如果我们继续沿着调用栈向内测试驱动，那么实际上就是**为之前构建的抽象层提供了具体实现**。因而，伦敦学派的过程就是**一个从抽象到具体的测试驱动的过程**。这也是为什么伦敦学派不惮于大量使用测试替身（甚至是Mock）：**具体实现是易变的，抽象是稳定的，因为它提炼了核心而忽略了细节**。

如果抽象层构建合理，那么它就是稳定且不易改变的。重构和代码改写通常发生在实现层，合理的抽象可以屏蔽这些改变对于外界的影响。那么使用行为验证、mock、单元测试，也不会阻碍重构的进行。而随着调用栈向内，逐渐从抽象层走到具体实现的时候，具体的模块就不会再依赖额外的组件，那么**单元测试自然变成状态验证的单元级别功能测试**。
<div><strong>精选留言（4）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/20/a8/66/e2781d4a.jpg" width="30px"><span>忘川</span> 👍（2） 💬（0）<div>伦敦学派的抽象层划分难点 是依赖 现成的规约或者框架 也就是必须有一个被验证的约定在前 才能降低难点带来的影响 
伦敦学派的深入调用栈 是依赖 后续对于测试用例的 不断整理重构 保证其结构不会随着太多而散乱</div>2023-01-07</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/bd/6a/abe84a16.jpg" width="30px"><span>范特西</span> 👍（0） 💬（0）<div>经典学派难点：需求理解能力、重构能力
伦敦学派难点在经典学派之上还有：识别抽象能力
个人理解伦敦学派更适合于构建复杂度高的软件</div>2024-07-28</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/ac/87/8ed5880a.jpg" width="30px"><span>大碗</span> 👍（0） 💬（0）<div>越外层的越像门面，主要负责编排，所以也更加抽象</div>2022-09-08</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/7d/b6/abdebdeb.jpg" width="30px"><span>Michael</span> 👍（0） 💬（0）<div>我怎么觉得对于这种编排类型的组件的测试来说好像建立在抽象上的测试才是一个比较正确的做法呢？因为如果测试要测试的是意图而不是实现，那么我的理解就是你的编排型的组件必须得非常抽象，你才能做到测试意图呢？比如说，我要测试下单流程，可能下单的流程里还要支付，那现在我的下单依赖了支付组件，那也只能依赖抽象而不是具体的实现，这样我的单元测试可能就直接mock 抽象出来的interface PaymentProvider 而不用取关心具体的实现，这样以后即便我再怎么改我的下单的流程，只要业务上还需要支付我都可以不需要修改我的测试，这样不是挺好的么？当然了，你越接近具体实现，你的代码修改，你确实是要改的，但是你起码控制了你的修改面，不至于你实现细节的修改还要去修改上层的模块的测试。</div>2022-06-21</li><br/>
</ul>