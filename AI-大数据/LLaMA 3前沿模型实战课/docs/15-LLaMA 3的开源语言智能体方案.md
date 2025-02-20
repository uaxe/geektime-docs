你好，我是Tyler。

今天，我们将正式开始语言智能体的学习之旅，进一步探索LLaMA3的能力边界。在第二章探索多轮对话能力的过程中，我们深入研究了如何利用“反馈增强”技术扩展 LLaMA3 的能力。尽管这种方法在很多场景下取得了不错的效果，但它仍然存在一个关键问题：**智能体无法根据持续的运行进行自我进化，不能从历史经验中不断优化决策。**

比如，我们曾经使用过反馈增强方法（如ReAct），在多次重复处理同一问题时，得到的答案几乎没有任何变化。这表明，传统的反馈增强方法未能促使模型实现真正的自我进化，缺乏持续学习和适应的能力。

为了让模型实现真正的自我进化，我们需要采用全新的方法。你还记得我们是如何在多步推理中不断提升大模型处理复杂任务的能力的吗？正是通过引入行动-观察闭环和思考闭环，我们增强了智能体的工具使用能力和稳定性，进而构建了ReAct的复杂闭环结构。

这次，我们将引入全新的闭环反馈机制，**加入“自我反思”功能和“外部记忆”模块**。通过这种方式，模型不仅能在每次执行任务时反思自己的决策，还能存储历史经验，在后续任务中不断优化表现。

## 自我反思（Reflexion）进化增强

自我反思是一种通过语言反馈来强化智能体行为的机制，旨在让智能体从过去的决策和行为中持续学习，提升其在复杂任务中的表现。具体来说，自我反思机制将环境反馈——无论是自由形式的语言反馈，还是标量形式的奖励（如评分）——转化为“自我反思”反馈，为下一轮决策提供必要的上下文信息。这一过程使得智能体能够从过去的错误中迅速吸取教训，避免重复相同的失误。
<div><strong>精选留言（2）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/2b/63/57/b8eef585.jpg" width="30px"><span>小虎子11🐯</span> 👍（0） 💬（0）<div>课程代码地址：https:&#47;&#47;github.com&#47;tylerelyt&#47;LLaMa-in-Action</div>2024-11-25</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/17/df/aa/07d99f59.jpg" width="30px"><span>小歪歪的狗子</span> 👍（0） 💬（1）<div>很好，很期待老师给出具体的代码实现</div>2024-11-15</li><br/>
</ul>