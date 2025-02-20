你好，我是 Tyler！

上一节课中，我们讨论了 Scaling Law 中的第一个重要因素 —— **参数的扩展**，了解到大规模参数量如何从根本上影响语言模型的表现。今天，我们将焦点转向“第二阶段：**数据的扩展**”，也就是在后训练阶段对数据进行的探索，以及这些探索如何影响语言模型的推理能力。

## 预训练：语言模型的基础

在谈数据之前，先回顾一下预训练阶段的关键：在预训练阶段，我们会一次性地向模型提供海量文本数据，让它充分学习语言的词义、语法结构以及基本推理能力。经过这样的过程，模型便具备了初步的语言理解和推理雏形。

有趣的是，研究者在实践中意外发现，某些“提示语”（Prompts）能够让模型产生更好的推理效果。例如“Let’s think step by step”这句话，在处理复杂问题时，能引导模型把问题拆解成更小、更易处理的部分，然后逐步推理得出答案。

但需要注意的是，这些提示语往往带有“偶然性”，是在大量试错中意外发现的。有时对某些特定任务效果立竿见影，却无法应对更精密、更复杂的推理需求。

于是，在预训练阶段获得的所有提示语，更像是一个“彩蛋”，它们虽然为模型提供了思路，但无法完整支持多样且高难度的场景。这就引出了我们今天的重点：后训练阶段的数据探索。