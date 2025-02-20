你好，我是邢云阳。

在上一章节，我带你深入实践了 AI + 云原生的第一个实战项目，用自然语言操控 K8s。该项目相比传统的 K8s 管理系统而言，最大的变化就是前端从命令行或网页页面按钮等变成了聊天界面。而带来的好处除了显而易见的无需记忆复杂命令行或者摒弃复杂的界面操作外，还有一点就是让内容的呈现变得智能化。

在传统的 K8s 管理系统中，呈现的数据内容与格式都是固定的，例如 Pod 资源有很多字段，但在前端上，通常会选取部分字段做展示。如果某一天需求变更，需要修改格式或者变更字段，则前后端代码都得修改。而自然语言前端就不一样了，用户想要什么字段，完全是看 prompt 如何编写，非常灵活。

OK，以上是对上一章节的一个简单回顾。这一章我们将会花两个课时的时间继续沿着这个主题进行实践，会把重点放在让 AI 辅助人类解决 K8s 运维问题上。第一节课，我们先简单一点，不写任何 API，而是用 kubectl 当工具来分析问题。而第二节课，我们将尝试进行日志和事件的分析。

首先，我们先来做个测试，看看通义千问大模型到底会不会使用 kubectl。你可以看一下设计的 prompt。

```plain
SYSTEM
你是一个K8s运维专家，请使用kubectl工具来一步步的思考帮我解决运维问题。

#Guidelines
- 每一步都列出对应的kubectl命令

HUMAN
The user's input is: 我在default命名空间下有一个叫foo-service的service不工作，应如何排查？
```
<div><strong>精选留言（1）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/0f/5c/88/222d946e.jpg" width="30px"><span>linxs</span> 👍（0） 💬（2）<div>有个小疑问， 对于文中提到的联网搜索的操作，看一些大模型也是可以进行联网搜索的，那么在这种场景下，能否可以使用大模型本身的能力，替代Tavily这类网络搜索工具呢？
</div>2025-01-06</li><br/>
</ul>