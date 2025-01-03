你好，我是Tyler。

在上一节课中，我们学习了提示语工程的核心概念和设计理念，相信你现在已经对提示语工程有了全新的认识，不再认为它是一个“试错游戏”，而是一整套基于上下文学习的科学方法。

之前，我们虽然知道了如何对上下文学习，也就是ICL施加影响，但并没有涉及到具体技术的解读。这节课，我们将深入了解 ICL 的技术本质以及在大模型系统中的具体使用。学完今天的内容后，你将有能力为下节课中人工智能小镇的角色们增加各种“技能”。

## 大模型哺乳（吃奶粉）

首先，我们来看看模型热身（Warmup）技术，它是一种在训练阶段优化 ICL 能力的方法。举个例子，锻刀大赛中，一把刚刚锻造出的刀，如果不“开刃”，在后面一定会很难用。模型热身也是类似的作用，它可以帮助模型更好地适应目标场景，就像锻刀师给刀“开刃”一样，让刀锋更加锋利。

模型热身技术可以通过修改模型参数或添加额外的参数，来针对目标场景进行调整。模型热身和微调都是针对模型进行调整的方法，但它们的侧重点不同。模型热身是针对大语言模型上下文学习的整体能力进行调整，而微调是针对特定任务进行调整。

今天的重点，是推理阶段的优化方法，因为这才是提示语引擎的主要工作。模型热身的内容我们会在模型工程的部分详细介绍。

## 大模型投喂（吃食物）

上节课我们学习了提示语工程中组织示例样本的方法，主要分为示例选择和示例排序两个步骤。我们这就分别展开聊一聊。

### Selecting

我们先来说示例选择。上节课中我们提到，你可以用 AIRC 系统来完成外部记忆的优选。因此，你的提示语引擎是重度依赖 AIRC 系统的。但是当时还有一个细节没有提到，那就是在获得了优质的外部记忆后，提示语引擎还会进行一个“优中选优”的过程。

你可能会问，为什么不把这个过程直接加入到 AIRC 系统中？

这是一个很好的问题。其实，在最早期构建 AI 大模型系统时，工业级大模型系统的专家也都是这么做的。但是后来在系统不断迭代的过程中，我们发现，AIRC 面向的客户是“人”，所以它所检索出的内容，会更符合人的需求。

但是大语言模型系统中，提示语工程面向的客户是 LLM，所以我们必须考虑它的感受。因此，这个“优中选优”的过程，是为了在 AIRC 的结果中，选择更符合 LLM 胃口的示例。

接下来，我将针对这个需求，介绍几种经典的提示语工程方法。

#### KATE（就近法则）

第一类方法是，以论文 “What Makes Good In-Context Examples for GPT-3?” 为代表的无监督方法。这篇文章提出了 KATE 方法，这个方法是受到了提示语工程中检索增强能力的启发。

简单来说，他们进行了一组实验来验证一件事，那就是跟提问内容语义（高维空间距离）更相近的示例，是否能够帮助大语言模型得到更好的结果。实验结果显示，这个方法在文本理解和文本生成任务上，都明显优于随机选择示例的做法。

![](https://static001.geekbang.org/resource/image/1f/f9/1f469cbc2bbb50690c02fc4b151640f9.jpg?wh=3900x2194)

#### EPR（因材施教）

第二类方法是以论文 “Learning To Retrieve Prompts for In-Context Learning” 为代表的监督学习方法。其实监督学习的方法更符合我们对提示语工程的期望，因为它可以让大语言模型自身来判断示例样本的好坏。

这个方法名叫 EPR，它借鉴了 Learning to Rank 中 Pairwise 的对比学习方法。相信你还记得我们在 GPT 系列课程里面学过这类方法。这类方法只需要给出优秀示例和劣质示例的对比关系，就可以训练出一个打分模型，用来评价示例样本的质量。

所以这里唯一的问题，就是 **如何定义提示语中示例样本的“质量”高低。** 文章中提出了一种方法，这种方法可以利用大语言模型本身来为打分模型提供输入。

首先，我们需要从示例样本集中选择一个示例样本。然后，基于这个示例样本和训练集中的题目进行组合作为提示语，通过大语言模型为这个提示语生成的输出结果打分。接着，将平均得分高的示例样本选为正样本，平均得分低的示例样本选为负样本。最后，基于正负样本进行对比学习训练，得到一个对示例样本打分的模型。

这样，我们就可以在多个示例样本中，根据分数排序来优选样本。

![](https://static001.geekbang.org/resource/image/b6/69/b6dc8100017b0eb17c77c24c8cb5d769.jpg?wh=3900x2194)

### Ordering

现在我们继续学习第二步的工作，也就是 Ordering 排序。在上节课中，我们学习了常用的基于“就近示例”的排序方法。这节课，我们来学习另一个主流的排序策略，那就是基于熵的排序策略。

#### GlobalE&LocalE（投其所好）

我们可以根据 ACL 22 的这篇杰出论文 “Fantastically Ordered Prompts and Where to Find Them: Overcoming Few-Shot Prompt Order Sensitivity” 提出的方法，使用熵来决定示例的排序。简单来说，我们可以对一个示例样本的序列，计算它概率的熵值。熵值越大，就表示该序列的质量越高。

研究人员发现，使用他们提出的全局熵（Global Entropy: GlobalE）和局部熵（Local Entropy: LocalE），跟随机排序的方法相比，可以分别平均提高13%和9.6%的性能。这种方法相较于“就近示例”方法更加复杂，但在理论上具有更强的可解释性，更适用于对稳定性要求较高的工业级系统。

在确定了示例的选择和排序之后，我们接下来需要考虑的问题则是：如何使用提示语模板来组合你的示例和提问，才能让大语言模型更好地理解。

## 大模型反刍（吃自己）

一般而言，用户在给某个任务设计提示语的时候，往往会用一些习惯的表达方式，比如会对模型说：“根据我给你的示例，帮我解决某某问题”。

这些表达方式可能符合用户的习惯，但不一定会符合大语言模型的需求。

因此，工业级大模型系统的解决思路是，根据用户要完成任务的具体内容，使用自动提示词工程技术也就是 APE（Automatic Prompt Engineering）自动地生成一个更适合大语言模型的提示词模板。

### Automatic Prompt Engineer（自问自答）

APE 方法的主要思想是，根据用户要完成任务的具体内容，自动生成一个更适合大语言模型的提示词模板，主要包含以下几个步骤：

首先，你需要提供示例，包括任务描述和任务示例，一般来说任务示例是一组输入输出对。大语言模型会根据提供的示例，生成一些备选的“提示语模板”。

之后，你需要使用大语言模型作为打分模型，给每个提示语模板打分，选出分数最高的提示语模板作为这个任务的模板。

最后，是改进模板，这里要使用迭代蒙特卡洛搜索的方法，针对刚刚生成好的提示语模板，生成语义相似的指令变体，改进最佳模板。

这个改进的模板，就是我们用来完成最终任务的提示语模板了。APE方法可以提高模型的回答质量，将提示语工程的工作自动化掉，提高用户产品体验。这样用户在和大语言模型对话的时候，只要给出自己要完成的任务，APE 就会自动帮他选择更合适的沟通方式来与大语言模型对话了。

![](https://static001.geekbang.org/resource/image/f1/99/f1b4b50323f5773e4a7cf0ed98ca5099.jpg?wh=3900x2194)

在学习了如何给大语言模型选择和排序合适的示例，以及自动生成提示词模版之后的下一步，我们来学习如何通过提示语控制大语言模型的“思考方式”。

### Self-Consistency Sampling（一题多解）

大语言模型通常会在解码器的每个时间步，选择概率最高的词汇作为输出。这种策略在只有一次回答机会的情况下是非常有效的。但是，如果我们希望模型在回答某个问题时，充分考虑他所学过的所有知识，这种方法就不太适用了。为了优化这种方法，Google提出了自一致采样（Self-Consistency Sampling）的方法。

自一致采样方法包括以下三个步骤。

- 第一步，使用思维链（CoT）提示语言模型，分步骤地解决给定问题。
- 第二步，从语言模型的解码器中随机采样，生成一组不同的推理路径。
- 第三步， 在众多最终答案中，选择最一致的答案，作为最终的推理结果。

这个思想，和我们在数学考试中，通过“一题多解”来验证答案的正确性，其实是一样的。它通过让 LLM 从多个不同的推理路径中生成答案，并根据答案的自洽性来选择最优的结果。

是不是觉得这是一个非常直观有效的方法？

确实，自一致采样是目前最广泛使用的提示语工程方法。这个方法既可以提高模型的回答质量，又可以提高模型的鲁棒性。

![](https://static001.geekbang.org/resource/image/dd/fc/ddc1702e694a1717709f1a2f5a7beafc.jpg?wh=3900x1924)

### Generated Knowledge Prompting（反刍知识）

刚刚我们学习了，怎样通过综合使用大语言模型 **输出的多样性**，来增强模型生成内容的质量。而接下来要讲的这种方法，是通过增强大语言模型 **输入的质量**，来提升生成内容质量。这种方法可以与之前的方法结合使用，进一步地提高模型的性能。

我们知道，在大语言模型回答复杂问题的时候，往往需要用到涌现能力，而涌现能力呢，对模型的参数量有很大的需求，这会花费大量的算力成本。

所以，为了不滥用模型的“涌现”能力，在一些情况下，我们可以先帮助模型，去唤醒一些它的“深度记忆”，让它知道该用这些学过的知识来，回答问题。

需要注意的是，这里的“记忆”是指模型在训练过程中获得的记忆，而不是提示词提供的外部记忆。这个方法的具体步骤是先让大语言模型生成一些，跟问题内容相关的“知识”，然后再把这个知识做为输入示例样本反哺给大语言模型，辅助回答目标问题。

![](https://static001.geekbang.org/resource/image/7f/86/7f88b1b9606accddb9b4c2d04f532086.jpg?wh=3900x2194)

这里举个例子，比如你问大语言模型以下问题时，它很可能给你一个错误的答案。

> Prompt：Part of golf is trying to get a higher point total than others. Yes or No?

> Output：Yes.

接下来，我们让 LLM 提供一些问题相关的知识。

> Prompt：Generate some knowledge about golf.

> Knowledge 1: The objective of golf is to play a set of holes in the least number of strokes. A round of golf typically consists of 18 holes. Each hole is played once in the round on a standard golf course. Each stroke is counted as one point, and the total number of strokes is used to determine the winner of the game.

> Knowledge 2: Golf is a precision club-and-ball sport in which competing players (or golfers) use many types of clubs to hit balls into a series of holes on a course using the fewest number of strokes. The goal is to complete the course with the lowest score, which is calculated by adding up the total number of strokes taken on each hole. The player with the lowest score wins the game.

随后基于这些知识，我们继续提出相同的问题。

> Prompt: Part of golf is trying to get a higher point total than others. Yes or No?

> Knowledge: The objective of golf is to play a set of holes in the least number of strokes. A round of golf typically consists of 18 holes. Each hole is played once in the round on a standard golf course. Each stroke is counted as one point, and the total number of strokes is used to determine the winner of the game.

> Output: No, the objective of golf is not to get a higher point total than others. Rather, the objective is to play a set of holes in the least number of strokes. The total number of strokes is used to determine the winner of the game, not the total number of points.

这时你会发现，模型已经可以给出正确答案了。其实这有点像人类把自己想到的和问题相关的所有知识写在纸上，再盯着这张纸去思考问题答案的过程。

## 大模型觅食（吃别人）

前面我们分别用吃奶粉、吃食物来比喻大语言模型的交互过程，这里为什么叫吃别人呢？因为我们后面课程的重点，是让大语言模型自己学会如何获取自己所需要的“食物”，这个食物泛指一切大语言模型可以获取的外部记忆和外部工具，甚至它还可以寻求其他智能体的帮助。

### Self-Ask（自抛自抢）

在具身智能和多智能体博弈的场景下，大语言模型要学会判断当前获取的知识是否够用。我们在 [第2节课](https://time.geekbang.org/column/article/686408) 具身智能的时候就提过 Self-Ask 的方法，不过那时我们还没学习 LLM 的相关知识和 ICL 的概念，所以没有展开。所以，请一定确保你已经掌握了上下文学习的概念，这样才能真正理解Self-Ask的技术。

Self-Ask 本质上是通过给大语言模型几个的示例样本（Few-Shot），帮助模型理解在什么情况下，它需要向外界索要更多的外部知识。

具体的做法类似于后面图里这样。

![](https://static001.geekbang.org/resource/image/c7/b0/c7faf03c0c68ea7b34a4b53fcd0e85b0.jpg?wh=3912x2250)

我们可以看到，在左边的图中，我们直接给大语言模型提出问题或者使用思维链的方式提示它回答问题，但都没有给出正确的答案。然而右侧的Self-Ask方法却给出了正确的结果，为什么会这样呢？下面我为你详细解释一下， Self-Ask 在这个过程中做了什么。

首先，我们会给出一个红框中的示例样本，其中包含了一个例子，内容是在条件不足的情况下，通过索要更多信息，补全条件后问题得以解决的例子。这个例子可以帮助大语言模型理解在什么场景下，它应该提出需求，来索要更多的信息辅助它回答蓝框中给定的问题。

绿色部分则是模型的输出内容，这些输出内容会告诉我们它是否需要更多的额外信息（Follow up）。如果需要，提示引擎则会调用外部记忆或工具去获取更多的信息。

![](https://static001.geekbang.org/resource/image/9e/4a/9ebdcb1a83a637562476b7fee79c1a4a.jpg?wh=2268x2250)

这种通过大语言模型自我判断的，多轮思考方法的步数不是特别可控，所以该方法在聊天对话类大模型应用中不太常见。不过，在具身智能和多智能体博弈的场景则经常会用 Self-Ask 和它的各类变种来实现智能体的自治，希望你可以牢牢掌握。

## 总结

好的，到这里我们先做一个总结吧。

今天的课程里，我们学习了如何在大语言模型投入线上工作之前的各种工作。

在模型的角度，你需要先对模型进行热身。在提示语工程的角度，你需要一个强大的提示引擎来支持大语言模型。具体而言，我们学习了如何优选示例样本、排序示例样本和帮助大模型反刍所学知识。

之后我们还进一步学习了怎么让大模型学会打猎觅食，自主地使用外部记忆和工具，解决它所遇到的各种现实问题。你可以参考后面这张图回顾今天的重点内容。

![](https://static001.geekbang.org/resource/image/d5/8b/d55906073389dec3d822552ca874fb8b.jpg?wh=4000x2016)

在下节课中，我将带你进一步学习。怎么让大模型学会打猎觅食，自主地使用外部记忆和工具，解决它所遇到的各种现实问题，敬请期待。

## 思考题

如果只允许你为自己的大模型系统，添加一个这节课学到的提示语工程能力，你会选择哪个，为什么呢？

恭喜完成我们第 20 次打卡学习，期待你在留言区和我交流互动。如果你觉得有收获，也欢迎你分享给你身边的朋友，邀 TA 一起讨论。