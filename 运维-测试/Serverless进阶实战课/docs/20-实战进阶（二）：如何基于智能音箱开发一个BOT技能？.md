你好，我是静远。

上节课，我们一起感受了FaaS 作为Serverless “连接器”的强大，但也仅限于云厂商单个云平台上的体验。

今天，我将带你体验跨平台的开发，通过智能音箱、IOT 开发平台、云函数计算平台三者之间的联动，一起完成一个不同年龄段宝宝食谱推荐BOT技能的开发。

你也可以通过这样的方式，完成**智能客服、智能问答等对话式应用**的开发。通过这个实战，相信你能进一步感受到Serverless的无限可能。

## 如何实现

我们本次的目标是通过语音对话的方式来完成宝宝食谱的推荐。这个功能符合Serverless的特性：事件触发、轻量应用、按需调用、流量不固定。同时，该功能需要有语音转文字的处理能力以及一个物理载体。

因此，我们以[百度智能云函数计算平台](https://cloud.baidu.com/product/cfc.html)、[百度DuerOS开放平台](https://dueros.baidu.com/dbp/main/console)来进行本次的案例开发，并选择一个小度X8作为载体。当然，你也可以直接用DuerOS平台上的[模拟测试工具](https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-quickstart/skills-test-sample_markdown)达到一样的效果。

正所谓磨刀不误砍柴工，在开始实战之前，我们先了解一下今天涉及到的各类概念以及整体的实现思路。

### **什么是技能（BOT）？**

我们通常将**在DuerOS平台上开发的对话式服务**称为“技能”，它还有一个英文名，“BOT”。一般来说，平台有内置技能和开发者提交发布的两种技能。前者可以直接拿来用，后者分为免费和收费两种，收费的技能和你在小度音箱上看到的一样，是需要支付购买才能使用的。