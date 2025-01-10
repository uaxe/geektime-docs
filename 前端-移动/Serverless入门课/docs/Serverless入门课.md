Serverless 兴起于 2017 年，近年伴随着云原生概念的推广愈发火爆。在这波浪潮里，以阿里巴巴、腾讯这样的一线大厂为首，越来越多的互联网公司开始关注甚至推进Serverless的应用。

Serverless的大热，表面上看好像是一件技术的事情，其实背后与钱有关。

拿你部署一套博客来说，常见的Node.js MVC架构，需要购买云服务商的Linux虚拟机、RDS关系型数据库，做得好的话还要购买Redis缓存、负载均衡、CDN等等。再专业一点，可能还会考虑容灾和备份。这么算下来一年最小开销都在1万元左右。但如果你用Serverless的话，这个成本可以直接降到1000元以下。

就像iPhone当年颠覆诺基亚一样，Serverless对运维体系的极端抽象，给应用开发和部署提供了一个极简模型。这种高度抽象的模型，可以让一个零运维经验的人，几分钟就部署一个Web应用上线，并对外提供服务。这是在省钱的基础上，又为你省了力。

所以有人就说，Serverless就是让前端拓宽边界，去做一些后端的事情。可事实上，它对于前后端程序员的机遇和挑战又是什么？Serverless又该如何与现有业务结合去谈实践？

本专栏将结合蒲松洋近年的研究成果，从Serverless的概念、运行原理入手，到应用实践，带你系统化地深入学习Serverless。为了让你学以致用，本专栏会设置有录屏演示、项目Demo、动手作业等等教学活动。

具体内容上，专栏共分为三大部分，基础篇、进阶篇和实战篇。

**基础篇：** 带你理解Serverless要解决什么问题，以及Serverless的边界和定义。搞清楚了来龙去脉后会进入动手环节，通过一个例子给你讲解Serverless引擎盖下的工作原理，以及FaaS的一些应用场景。

**进阶篇：** 专注FaaS的后端解决方案BaaS，以及现有的后端应用如何BaaS化。为了更好地展现Serverless的发展历程和背后的思考，这部分还设有一个基于Node.js的待办任务的Web应用，帮助你动手实践。点击获取 [GitHub地址](https://github.com/pusongyang/todolist-backend)。

**实战篇：** 通过Google开源的Kubernetes向你演示本地化Serverless环境如何搭建，并结合作者的经验，带你了解Serverless架构应该如何选型，以及目前Serverless开发的最佳实践。

# 学习路径图

![](https://static001.geekbang.org/resource/image/62/10/62bb60b638c2cde5efd95ae94789bf10.jpg)