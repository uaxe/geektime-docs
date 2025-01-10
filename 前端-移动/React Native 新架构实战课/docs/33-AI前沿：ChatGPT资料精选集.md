你好，我是蒋宏伟。

咱们的专栏一直是围绕着 React Native 展开的，但最近想必你也感受到 ChatGPT 的重要性了，这是我们所有人不得不关注的一件大事。所以，今天咱们也来聊聊 ChatGPT。

2022年11月30日，ChatGPT 正式发布。短短两个月，用户数量便突破了亿级大关，创造了史上最快达到亿级用户量的传奇。更为重要的是，它展示了大型 AI 模型所具有的巨大潜能，这或许将引领人类走向一个前所未有的新纪元。

为了让你更高效、更系统地了解和学习 ChatGPT，我整理了这篇关于 ChatGPT 的精选集。本精选集的目的在于提供一个便捷的参考资源，帮助你全面掌握 ChatGPT。精选的资料会尽可能来源于 AI 领域的权威和一线项目，分为以下 6 个部分：OpenAI、业界观点、实际应用、原理科普、开源模型以及学习材料。这些内容将助力你深入了解 ChatGPT 的方方面面。

## **OpenAI**

首先，咱们需要重点关注的是 OpenAI 的三位联合创始人：Sam Altman、Ilya Sutskever 和 Greg Brockman。

作为 ChatGPT 背后团队的核心领导成员，Sam Altman、Ilya Sutskever 和 Greg Brockman 将他们的天赋、使命感和领导力融会贯通。正是他们对通用人工智能的坚定信念，使得这三位领袖汇聚一堂，并于2015年共同创立了 OpenAI。从 GPT-1 到 GPT-3，再到 ChatGPT，他们不断取得辉煌成就。

我精选了 3 篇他们关于 ChatGPT 的谈话，以及 1 篇关于 OpenAI 首席科学家 Ilya Sutskever 的成长故事。

在这些谈话中，他们从技术和产品的角度深入阐述了 ChatGPT 的运作原理以及未来发展愿景。涉及的主题包括神经网络、基于人类反馈的强化学习（RLHF）、通用人工智能、AI 意识以及 OpenAI 开源组织等诸多领域。而在 Ilya Sutskever 成长故事中，你能从另一个维度去理解这群人对于人工智能执着的信仰。

- 《Sam Altman：OpenAI CEO 谈论 GPT-4、ChatGPT 以及 AI 的未来》 [英文视频](https://www.youtube.com/watch?v=L_Guz73e6fw) [中文](https://www.yuque.com/3dinternet/gpt/gpt3)
- 《Ilya Sutskever: ChatGPT 背后的大脑》 [英文](https://journeymatters.ai/ilya-the-brain-behind-chatgpt/) [中文](https://zhuanlan.zhihu.com/p/614092393)
- 《Ilya Sutskever：模型规模见顶，下个突破点在用好 AI 涌现特质》 [英文视频](https://www.youtube.com/watch?v=Wmo2vR7U9ck) [中文](https://mp.weixin.qq.com/s/WushU5NtU4futwjnVyQAiw)
- 《Greg Brockman：ChatGPT 惊人潜能的内幕故事》 [英文视频](https://www.ted.com/talks/greg_brockman_the_inside_story_of_chatgpt_s_astonishing_potential/c) [中文视频](https://www.bilibili.com/video/BV1514y1f74G/?spm_id_from=333.337.search-card.all.click&vd_source=8823013f26231a35736e61615f279c06)

## **业界观点**

比尔·盖茨和陆奇，可能是和 OpenAI 走得最近的社会名人之一，他们的观点同样引人关注。

比尔·盖茨在他的文章中开篇便提到，在他的一生中，他亲眼见证了两次具有变革性的技术革命。一个是图形界面，它成为了包括 Windows 系统在内的所有现代操作系统的基石，另一个便是 ChatGPT。盖茨对 ChatGPT 展示出的批判性思维赞叹不已，这不仅仅是模仿，而是具备了基于给定事实进行推理、分析并作出判断的能力。盖茨预测，ChatGPT 将给人们在工作、教育、医疗等方面带来巨大的变革。

陆奇认为，当前大部分数字化产品和公司，如谷歌、微软、阿里、字节等，其本质都是信息传递公司。而 ChatGPT 带来的大模型时代，能对信息进行更深入的推理和规划，从而取代部分人类的脑力劳动，除非你具备独到的见解。大模型将创造平台型的机会，尽管大多数淘金者可能会失败，但平台本身可以持续盈利。

然而，另一方面，ChatGPT 的能力也引起了各界人士的担忧。

图灵奖获得者、前谷歌大脑负责人 Geoffrey Hinton（同时也是 Ilya Sutskever 的老师）表示担忧：一个更聪明的存在不太可能被一个不那么聪明的存在控制。AI 可能会绕过我们的限制，让人们按照它的意愿行事。此外，竞争将逐步升级，包括 OpenAI 和谷歌公司之间的竞争，以及中美两国在该领域的竞争。但因为包括创造者在内，没有人能完全理解、预测或可靠地控制它们，AI 领域的“军备竞赛”可能会给人类带来危机。

同样，一封 27565 人的联名公开信也在呼吁 AI 实验室暂停训练比 GPT-4 更强大的 AI 系统，至少暂停 6 个月。

- 《比尔盖茨：AI时代已经开始》 [英文](https://www.gatesnotes.com/The-Age-of-AI-Has-Begun) [中文](https://36kr.com/p/2184264733720713)
- 《陆奇：我的大模型世界观》 [中文](https://mp.weixin.qq.com/s/_ZvyxRpgIA4L4pqfcQtPTQ)
- 《Geoffrey Hinton：要阻止AI控制人类》 [英文视频](https://www.youtube.com/watch?v=XolpDENpYgg) [中文](https://github.com/JimLiu/subtitles/tree/main/Geoffrey%20Hinton%20talks%20about%20the%20%E2%80%9Cexistential%20threat%E2%80%9D%20of%20AI)
- 《公开信：暂停训练比 GPT-4 更强大的 AI》 [英文](https://futureoflife.org/open-letter/pause-giant-ai-experiments/) [中文](https://36kr.com/p/2192266008313984)

## **业界应用**

ChatGPT、BingChat 和 Copilot X 对于程序员来说都是实用且高效的工具。

目前，ChatGPT 的搜索功能（with browsing）、编码解释器（Code Interpret）已处于灰度测试阶段，微软基于 GPT-4 的 BingChat 已全面开放，同样基于 GPT-4 的 Copilot X 也开始支持内测申请。

以 ChatGPT 编码解释器为例，它支持将编码转换为文字或可视化内容。编码包括文件、数据、视频、音频等，最大支持上传 100MB 的编码内容。此外，它还具备多模态功能，不仅能将编码内容提炼成人类可理解的文字或图片，还能根据命令自动生成代码分析上传的编码内容，支持 GIF 转视频、音频切割等。这些功能可应用于科研、金融分析或影音处理等领域。

在其他领域，如游戏和教育，GPT 的影响力也逐渐显现。

你可以尝试一款名为《病娇 AI 女友》的 GPT 游戏。在游戏中，你会感觉真的在与一个深爱你的虚拟女友聊天，她会说 “We can stay together forever, just you and me”。然而，你需要在她强烈、病态的占有欲中与她斗智斗勇，说服她让你离开房间。这种类真人互动的游戏体验可能会成为未来游戏的常态。

在教育领域，Khan 学院是这个方向的先驱。尽管有些学校因学生利用 ChatGPT “抄作业”而全面禁用，但 Khan 学院认为，一对一教育能够显著提高教学成绩，而 AI 老师让一对一教育成为可能。Khan 学院已在数学、编程、写作等方面展开了 AI 老师辅导教学的探索。

进一步思考，我们这一代人，绝大部分人都坚信 AI 是工具。然而，我们下一代是 AI 时代的“原住居民”，他们从小和 AI 一起玩耍和学习，他们还会认为 AI 是工具吗？还是会认为 AI 是和人类一样平等的硅基物种？

- ChatGPT 编码解释器（Code Interpret） [英文](https://twitter.com/heyBarsee/status/1654252233628819456) [中文](https://zhuanlan.zhihu.com/p/618306445)
- BingChat（需要美国IP，进不去时清除缓存） [官网](https://bing.com/) [中文](https://36kr.com/p/2244045320138626)
- Copilot X [官网](https://github.com/features/preview/copilot-x) [中文](https://mp.weixin.qq.com/s/BAzOuxjUongX0U3H4gYvYQ)
- 游戏：病娇AI女友 [官网](https://helixngc7293.itch.io/yandere-ai-girlfriend-simulator) [类真人游戏可行性论文](https://arxiv.org/pdf/2304.03442.pdf)
- Khan 学院的超级AI导师 [英文](https://www.ted.com/talks/sal_khan_the_amazing_ai_super_tutor_for_students_and_teachers/c) [中文](https://zhuanlan.zhihu.com/p/626331568) [一对一教育提高2个标准差成绩的论文](http://web.mit.edu/5.95/readings/bloom-two-sigma.pdf)

## **原理科普**

ChatGPT 中的 Chat 代表产品形态，而 GPT 是其背后的技术。GPT 也就是我们通常所说的大模型。

大模型的基础是数学和计算机科学。最早的深度学习研究者在 20 世纪 40 年代提出了一个大胆的假设：计算机人工神经元与生物神经元有相似之处。

因此，计算机神经网络的专家开始用计算机模拟生物神经元，其中人工神经元的参数对应于生物神经元。当参数达到一定量级时，就会出现一些原本不存在的能力。例如，在 GPT-3 中，它拥有约 1750 亿个参数，而人类大脑大约包含 1000 亿个神经元，当二者处于同一个数量级时，GPT-3 就涌现出了类似人类的推理能力。这种涌现出来的推理能力是一种偶然，还是一种必然？

为了让你更深入地了解大模型，我推荐给你 3 个视频，作者分别是伊利诺伊大学计算机科学系的副教授 Stephen Wolfram、Waymo（前身是谷歌自动驾驶汽车项目）的研究科学家 Ari Seff 和西安电子科技大学博士后于建国。这些视频将为你详细科普大模型的原理。

- 《ChatGPT在做什么…以及为什么它能发挥作用？》 [英文视频](https://www.youtube.com/watch?v=flXrLGPY3SU&t=2335s) [中文](https://mp.weixin.qq.com/s/p9xbzeFzI9OQ_JBEOweO2g)
- 《ChatGPT 是如何训练的？》 [英文视频](https://www.youtube.com/watch?v=VPRSBzXzavo) [中文视频](https://www.bilibili.com/video/BV1Xs4y1h7YP/?spm_id_from=333.337.search-card.all.click&vd_source=8823013f26231a35736e61615f279c06)
- 《渐构社群：万字科普GPT4为何会颠覆现有工作流？》 [中文视频](https://www.bilibili.com/video/BV1MY4y1R7EN/?spm_id_from=333.337.search-card.all.click&vd_source=8823013f26231a35736e61615f279c06)

## **开源模型**

数据就是“石油”，基于隐私考虑，任何的平台型的公司都不想让自己的数据跑在别人的模型上面。因此，未来这些平台型的公司，必然会选择私有部署大模型。这时候，开源模型就至关重要了，无论是参考借鉴，还是直接二次优化，都是很好的选择。

开源模型中的开源有三层含义，开源代码（Code）、开源训练数据（Dataset）、开源大模型本身（Model）。

OpenAI 在 GitHub 上开源了的 GPT-2、GPT-3，只开源了部分代码和部分训练数据。尽管代码和训练数据很重要，但最关键的是大模型本身。据国盛证券报告的估算，GPT-3 训练一次的成本约为 140 万美元。因此，无论是基于商业竞争角度考虑，还是基于 AI 安全角度考虑，开源成熟商业模型并不是一个好主意。因此，OpenAI 开源的 GPT-2、GPT-3 实际只具有学术研究价值，不能直接部署。

但也有一些可用的开源模型，它们开源了大模型本身。在这里，我主要介绍一下清华大学的 ChatGLM 和 Databricks 的 Dolly 大模型。清华的 ChatGLM 针对中文问答和对话进行了优化，其最大模型参数量为 100 亿。Databricks 是一家估值达到 380 亿美元的人工智能企业，它开源的 Dolly 大模型最大参数量为 120 亿。虽然，他们和 GPT-3 的 1750 亿个参数，差了一个量级，但却是能直接部署使用的。

ChatGLM-6B 模型的最低硬件要求是拥有 13GB 显存的 GPU，对应的显卡大约是 RTX A4000。Dolly-v2-12B 的最低要求是 A10 GPU，对应显存大小为 24GB。这些显卡的价格至少在数千元以上。如果你只是想部署并尝试一下，可以考虑其他替代方案。例如，可以使用 [GPU 云](https://www.runpod.io/console/gpu-secure-cloud)，按小时购买，只需花费十几元即可体验。或者，你还可以尝试一些非官方的优化后的部署方案，如 JittorLLMs 提供的 2GB 内存就能运行大模型的解决方案。

值得思考的是，什么能力是需要“内置”到模型中的，什么能力让模型借助工具完成即可。

- [GPT-2 开源了部分代码](https://github.com/openai/gpt-2)
- [GPT-3 开源了部分训练集](https://github.com/openai/gpt-3)
- [ChatGLM 开源了 100M～12B 的大模型](https://github.com/THUDM/ChatGLM-6B)
- [Dolly 开源了 3B～12B 的大模型](https://github.com/databrickslabs/dolly)
- [JittorLLMs 提供的笔记本没有显卡也能跑大模型方案](https://github.com/Jittor/JittorLLMs)

## **学习材料**

前面我们讲了，模型类似于人类大脑，但光有一个能推理的“大脑”是不够的，也并非所有能力都要内置到“大脑”中。

实际上，模型肯定还需要借助外部工具来接收来自真实世界的信息，并借助各种 API 和这个世界交互。这就涉及到如何使用 Prompt 来给模型下命令，以及如何将模型与现有工具进行整合的工程化的事情了。

如果你想学习如何搭建一个基于 GPT 的项目，模仿业内成熟项目是一个很好的方法。目前业内最受欢迎的两个基于 GPT 的开源项目分别是 Auto-GPT 和 gpt\_academic，它们的代码具有很高的参考价值。

如果你想进一步学习 GPT 相关知识，可以查看 OpenAI 官方提供的 Cookbook，以及与吴恩达合作的 Prompt 编程课。此外，极客时间的《AI大模型之美》课程也值得一学，我自己也在学习这门课程，非常推荐。通过这些资源，你可以系统地学习 GPT 技术，并运用在自己的项目中。

- [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT)
- [gpt\_acdemic](https://github.com/binary-husky/gpt_academic)
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)
- [吴恩达：开发者的 ChatGPT Prompt 编程课](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/)
- [《AI大模型之美》](https://time.geekbang.org/column/intro/100541001)

好了，今天的分享就到这里，在 ChatGPT 领域我也在努力学习，咱们共同进步。下节课咱们会继续聊 RN 的最新进展，下节课再见。