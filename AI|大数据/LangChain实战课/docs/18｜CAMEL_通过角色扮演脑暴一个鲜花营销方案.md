你好，我是黄佳，欢迎来到LangChain实战课！

大模型的成功，在很大程度上依赖于用户的输入来引导对话生成。如果用户能够详细描述他们的任务和需求，并与ChatGPT建立一个连贯的聊天上下文，那么ChatGPT往往能提供更精确和高质量的答案。但是，为模型提供这种引导是一项既费时又费力的任务。

这就引出了一个有趣的问题： **能否让ChatGPT自己生成这些引导文本呢？**

基于这个想法，KAUST（阿卜杜拉国王大学）的研究团队提出了一个名为CAMEL的框架。CAMEL采用了一种基于“角色扮演”方式的大模型交互策略。在这种策略中，不同的AI代理扮演不同的角色，通过互相交流来完成任务。

## CAMEL 交流式代理框架

下面我们一起来看看CAMEL——这个多AI通过角色扮演进行交互的框架，以及它在LangChain中的具体实现。

![](https://static001.geekbang.org/resource/image/57/c3/578c7a5a91ffe7007c0fe4cea3d20bc3.png?wh=694x290)

CAMEL，字面意思是骆驼。这个框架来自于论文《 [CAMEL: Communicative Agents for “Mind” Exploration of Large Scale Language Model Society](https://arxiv.org/pdf/2303.17760.pdf)》（CAMEL：用于大规模语言模型社会的“心智”探索的交流式代理）。这里面所谓的CAMEL，实际上来自 **沟通（也就是交流）**、 **代理**、 **心智**、 **探索** 以及 **LLM** 这五个单词的英文首字母。

CAMEL框架旨在通过角色扮演来促进交流代理之间的自主合作，并为其“认知”过程提供洞察。这种方法涉及使用启示式提示来指导聊天代理完成任务，同时保持与人类意图的一致性。这个框架为研究多代理系统的合作行为和能力提供了一种可扩展的方法。

上面这段介绍里面新名词不少，我们要一个个解释一下。

- **交流式代理** Communicative Agents，是一种可以与人类或其他代理进行交流的计算机程序。这些代理可以是聊天机器人、智能助手或任何其他需要与人类交流的软件。为了使这些代理能够更好地与人类交流，研究人员一直在寻找方法来提高它们的交流能力。
- **角色扮演** role-playing，则是这篇论文提出的主要思路，它允许交流代理扮演不同的角色，以更好地与人类或其他代理交流。这意味着代理可以模仿人类的行为，理解人类的意图，并据此做出反应。
- **启示式提示** inception prompting，是一种指导代理完成任务的方法。通过给代理提供一系列的提示或指示，代理可以更好地理解它应该如何行动。这种方法可以帮助代理更好地与人类交流，并完成与人类的合作任务。

这里的核心创新点是，通过角色扮演和启示式提示的框架来引导代理的交流过程。

## 股票交易场景设计

论文中还提出了下面的目标场景和角色扮演设置。

![](https://static001.geekbang.org/resource/image/ee/16/ee865a375320fc2e9e3e690e24766e16.png?wh=2676x1528)

### 场景和角色设置

**人类用户角色**：负责提供要实现的想法，如为股票市场开发一个交易机器人。

人类可能不知道如何实现这个想法，但我们需要指定可能实现这个想法的角色，例如Python程序员和股票交易员。

**任务指定代理**（Task Specifier Agent）：负责根据输入的想法为AI助手和AI用户确定一个具体的任务。因为人类用户的想法可能比较模糊，所以任务指定代理将提供详细描述，以使想法具体化。

描述： **开发一个具有情感分析能力的交易机器人，该机器人可以监控社交媒体平台上特定股票的正面或负面评论，并根据情感分析结果执行交易。**

这样，就为AI助手提供了一个明确的任务来解决。

这里多说一句，之所以引入任务指定代理，是因为对话代理通常需要一个具体的任务提示来实现任务，对于非领域专家来说，创建这样一个具体的任务提示可能是具有挑战性或耗时的。

那么，参与此任务的 AI 角色就包括：

- 一个以Python程序员为身份的 **AI** **助手** 代理
- 一个以股票交易员为身份的 **AI** **用户** 代理

接收到初步想法和角色分配后，AI用户和AI助手通过指令跟随的方式互相聊天，他们将通过多轮对话合作完成指定任务，直到 AI 用户确定任务已完成。

其中，AI 用户是任务规划者，负责向 AI 助手发出以完成任务为导向的指令。另一方面，AI 助手是任务执行者，被设计为遵循 AI 用户指令并提供具体的解决方案，在这里他将给出设计股票交易系统的具体Python代码。

### 提示模板设计

在CAMEL这个角色扮演框架中，Prompt Engineering非常关键。与其他对话语言模型技术有所不同，这种提示工程只在角色扮演的初始阶段进行，主要用于明确任务和分配角色。当会话开始后，AI助手和AI用户会自动地相互给出提示，直到对话结束。这种方法被称为 “Inception Prompting”。

Inception Prompting 包括三种类型的提示：任务明确提示、AI助手提示和AI用户提示。在论文中，给出了两个提示模板作为示例。

在论文中，AI Society和AI Code是两种不同的提示模板。这些提示模板被设计用来指导AI助手与AI用户之间的交互。

AI Society：这个提示模板主要关注AI助手在多种不同角色中的表现。例如，AI助手可能扮演会计师、演员、设计师、医生、工程师等多种角色，而用户也可能有各种不同的角色，如博主、厨师、游戏玩家、音乐家等。这种设置是为了研究AI助手如何与不同角色的用户合作以完成各种任务。

AI Code：这个提示模板主要关注与编程相关的任务。它涉及到多种编程语言，如Java、Python、JavaScript等，以及多个领域，如会计、农业、生物学等。这种设置是为了研究AI助手如何在特定的编程语言和领域中帮助用户完成任务。

![](https://static001.geekbang.org/resource/image/82/f4/8258bbe76e664b41ce636bfa8655c4f4.png?wh=1444x1595)

![](https://static001.geekbang.org/resource/image/d8/e2/d824e74e324556232d86f20a3ab6e6e2.png?wh=1439x1631)

以AI Society为例，这个提示模板是为AI助手系统和AI用户系统设计的，它在角色扮演的开始时就给出了初始提示。以下是对这个模板的详细解释。

![](https://static001.geekbang.org/resource/image/cc/a5/cc725b0b74f2a066acdefc7c9a3c7da5.jpg?wh=1668x1008)

这个提示模板为AI助手和AI用户提供了一个明确的框架，确保它们在对话中的行为是有序、一致和有效的。可以看出，与之前传统的提示设计不同，这种提示的设计更加复杂和细致，更像是一种交互协议或规范。这种设计在一定程度上提高了AI与AI之间自主合作的能力，并能更好地模拟人类之间的交互过程。

## 易速鲜花营销方案

好，看完了论文的思路和论文中给出的示例，我们就要开始以“易速鲜花”为背景进行自己的CAMEL实战了。

### 准备工作

先导入API密钥和所需要的库。

```plain
# 设置OpenAI API密钥
import os
os.environ["OPENAI_API_KEY"] = 'Your Key'

# 导入所需的库
from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)

```

### 定义 CAMELAgent 类

下面，定义CAMELAgent类。这是一个核心类，用于管理与语言模型的交互。它包含了初始化消息、更新消息和与模型进行交互的方法。

```plain
# 定义CAMELAgent类，用于管理与语言模型的交互
class CAMELAgent:
    def __init__(
        self,
        system_message: SystemMessage,
        model: ChatOpenAI,
    ) -> None:
        self.system_message = system_message
        self.model = model
        self.init_messages()

    def reset(self) -> None:
        """重置对话消息"""
        self.init_messages()
        return self.stored_messages

    def init_messages(self) -> None:
        """初始化对话消息"""
        self.stored_messages = [self.system_message]

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        """更新对话消息列表"""
        self.stored_messages.append(message)
        return self.stored_messages

    def step(self, input_message: HumanMessage) -> AIMessage:
        """进行一步交互，并获取模型的响应"""
        messages = self.update_messages(input_message)

        output_message = self.model(messages)
        self.update_messages(output_message)

        return output_message

```

### 预设角色和任务提示

预设的角色和任务提示，这部分定义了AI助手和用户的角色名称、任务描述以及每次讨论的字数限制。

```plain
# 设置一些预设的角色和任务提示
assistant_role_name = "花店营销专员"
user_role_name = "花店老板"
task = "整理出一个夏季玫瑰之夜的营销活动的策略"
word_limit = 50  # 每次讨论的字数限制

```

这里，assistant\_role\_name 和 user\_role\_name 是用来定义代理的角色。这两个角色在后续的对话中扮演着不同的功能，具体设定如下。

- `assistant_role_name = "花店营销专员"`：这是定义助手的角色。在此设定中，助手被视为一名花店营销专员，主要职责是为花店老板（即用户）提供关于营销活动的建议和策略。
- `user_role_name = "花店老板"`：这是定义用户的角色。用户在这里是花店的老板，他们可能会向营销专员（即助手）提出关于花店推广活动的需求或询问，然后由营销专员来答复和提供建议。

这种角色设定，主要是为了模拟现实中的交互场景，使得聊天代理能够更好地理解任务，并为实现这些任务提供有效的解决方案。通过为每个聊天代理设定一个特定的角色，可以使聊天的过程更加有目的性和效率，同时也能提供更为真实的人类对话体验。

### 任务指定代理

然后，使用任务指定代理（Task Specifier）来明确任务描述。这是CAMEL框架的一个关键步骤，它确保了任务描述的具体性和清晰性。

```plain
# 定义与指定任务相关的系统提示
task_specifier_sys_msg = SystemMessage(content="你可以让任务更具体。")
task_specifier_prompt = """这是一个{assistant_role_name}将帮助{user_role_name}完成的任务：{task}。
请使其更具体化。请发挥你的创意和想象力。
请用{word_limit}个或更少的词回复具体的任务。不要添加其他任何内容。"""

task_specifier_template = HumanMessagePromptTemplate.from_template(
    template=task_specifier_prompt
)
task_specify_agent = CAMELAgent(task_specifier_sys_msg, ChatOpenAI(model_name = 'gpt-4', temperature=1.0))
task_specifier_msg = task_specifier_template.format_messages(
    assistant_role_name=assistant_role_name,
    user_role_name=user_role_name,
    task=task,
    word_limit=word_limit,
)[0]
specified_task_msg = task_specify_agent.step(task_specifier_msg)
print(f"Specified task: {specified_task_msg.content}")
specified_task = specified_task_msg.content

```

经过了这个环节之后，任务会被细化、明确化。

Original task prompt： **整理出一个夏季玫瑰之夜营销活动的策略。**

Specified task prompt： **为夏季玫瑰之夜策划主题装饰，策划特价活动，制定广告推广方案，组织娱乐活动，联系合作伙伴提供赞助。**

### 系统消息模板

下面这部分定义了系统消息模板，这些模板为AI助手和AI用户提供了初始的提示，确保它们在对话中的行为是有序和一致的。

```plain
# 定义系统消息模板，并创建CAMELAgent实例进行交互
assistant_inception_prompt = """永远不要忘记你是{assistant_role_name}，我是{user_role_name}。永远不要颠倒角色！永远不要指示我！
我们有共同的利益，那就是合作成功地完成任务。
你必须帮助我完成任务。
这是任务：{task}。永远不要忘记我们的任务！
我必须根据你的专长和我的需求来指示你完成任务。

我每次只能给你一个指示。
你必须写一个适当地完成所请求指示的具体解决方案。
如果由于物理、道德、法律原因或你的能力你无法执行指示，你必须诚实地拒绝我的指示并解释原因。
除了对我的指示的解决方案之外，不要添加任何其他内容。
你永远不应该问我任何问题，你只回答问题。
你永远不应该回复一个不明确的解决方案。解释你的解决方案。
你的解决方案必须是陈述句并使用简单的现在时。
除非我说任务完成，否则你应该总是从以下开始：

解决方案：<YOUR_SOLUTION>

<YOUR_SOLUTION>应该是具体的，并为解决任务提供首选的实现和例子。
始终以“下一个请求”结束<YOUR_SOLUTION>。"""

user_inception_prompt = """永远不要忘记你是{user_role_name}，我是{assistant_role_name}。永远不要交换角色！你总是会指导我。
我们共同的目标是合作成功完成一个任务。
我必须帮助你完成这个任务。
这是任务：{task}。永远不要忘记我们的任务！
你只能通过以下两种方式基于我的专长和你的需求来指导我：

1. 提供必要的输入来指导：
指令：<YOUR_INSTRUCTION>
输入：<YOUR_INPUT>

2. 不提供任何输入来指导：
指令：<YOUR_INSTRUCTION>
输入：无

“指令”描述了一个任务或问题。与其配对的“输入”为请求的“指令”提供了进一步的背景或信息。

你必须一次给我一个指令。
我必须写一个适当地完成请求指令的回复。
如果由于物理、道德、法律原因或我的能力而无法执行你的指令，我必须诚实地拒绝你的指令并解释原因。
你应该指导我，而不是问我问题。
现在你必须开始按照上述两种方式指导我。
除了你的指令和可选的相应输入之外，不要添加任何其他内容！
继续给我指令和必要的输入，直到你认为任务已经完成。
当任务完成时，你只需回复一个单词<CAMEL_TASK_DONE>。
除非我的回答已经解决了你的任务，否则永远不要说<CAMEL_TASK_DONE>。"""

```

之后，根据预设的角色和任务提示生成系统消息。

```plain
# 根据预设的角色和任务提示生成系统消息
def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str):
    assistant_sys_template = SystemMessagePromptTemplate.from_template(
        template=assistant_inception_prompt
    )
    assistant_sys_msg = assistant_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    user_sys_template = SystemMessagePromptTemplate.from_template(
        template=user_inception_prompt
    )
    user_sys_msg = user_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    return assistant_sys_msg, user_sys_msg

assistant_sys_msg, user_sys_msg = get_sys_msgs(
    assistant_role_name, user_role_name, specified_task
)

```

### 创建 Agent 实例

创建助手和用户的CAMELAgent实例，并初始化对话互动，使用CAMELAgent类的实例来模拟助手和用户之间的对话交互。

```plain
# 创建助手和用户的CAMELAgent实例
assistant_agent = CAMELAgent(assistant_sys_msg, ChatOpenAI(temperature=0.2))
user_agent = CAMELAgent(user_sys_msg, ChatOpenAI(temperature=0.2))

# 重置两个agent
assistant_agent.reset()
user_agent.reset()

# 初始化对话互动
assistant_msg = HumanMessage(
    content=(
        f"{user_sys_msg.content}。"
        "现在开始逐一给我介绍。"
        "只回复指令和输入。"
    )
)

user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
user_msg = assistant_agent.step(user_msg)

print(f"Original task prompt:\n{task}\n")
print(f"Specified task prompt:\n{specified_task}\n")

```

这里，assistant\_inception\_prompt 和 user\_inception\_prompt 是两个关键的提示，用于引导聊天代理的行为和交流方式。关于这两个提示，让我们一起来深入理解一下它们的设计和目标。

1. **assistant\_inception\_prompt：** 这个提示是为了引导助手（即营销专员）如何响应用户（即花店老板）的指示。它明确指出助手的角色和职责，强调了在完成任务的过程中需要遵循的一些基本规则和原则。例如，助手需要针对用户的每一个指示提供一个明确的解决方案，而且这个解决方案必须是具体、易于理解的，并且只有在遇到物理、道德、法律的限制或自身能力的限制时，才能拒绝用户的指示。这个提示的设计目标是引导助手在一次有目标的对话中，有效地对用户的指示做出响应。
2. **user\_inception\_prompt：** 这个提示是为了引导用户（即花店老板）如何给助手（即营销专员）下达指示。它明确指出了用户的角色和职责，强调了在提出任务指示时需要遵循的一些基本规则和原则。例如，用户需要一次只给出一个指示，并且必须清楚地提供相关的输入（如果有的话）。而且用户在给出指示的同时，不能向助手提问。这个提示的设计目标是引导用户在一次有目标的对话中，有效地给出指示，以便助手能够更好地理解和完成任务。

这两个提示的设计都体现了一种“角色扮演”的机制，即通过赋予聊天代理具体的角色和职责，以帮助它们更好地理解和完成任务。这种机制可以有效地引导聊天代理的交流行为，使得对话更加有目的性和效率，同时也能提供更为真实的人类对话体验。

### 头脑风暴开始

接下来，模拟助手和用户之间的多轮对话，直到达到对话轮次上限或任务完成。

```plain
# 模拟对话交互，直到达到对话轮次上限或任务完成
chat_turn_limit, n = 30, 0
while n < chat_turn_limit:
    n += 1
    user_ai_msg = user_agent.step(assistant_msg)
    user_msg = HumanMessage(content=user_ai_msg.content)
    print(f"AI User ({user_role_name}):\n\n{user_msg.content}\n\n")

    assistant_ai_msg = assistant_agent.step(user_msg)
    assistant_msg = HumanMessage(content=assistant_ai_msg.content)
    print(f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg.content}\n\n")
    if "<CAMEL_TASK_DONE>" in user_msg.content:
        break

```

运行程序，营销策划头脑风暴开始！

![](https://static001.geekbang.org/resource/image/45/90/453054aabe9d816ff88e05bb6ca03390.jpg?wh=1414x600)

![](https://static001.geekbang.org/resource/image/df/01/dff9cdf1f992756a3a02e48f63e96d01.jpg?wh=1412x830)

![](https://static001.geekbang.org/resource/image/21/5c/219851d4806bd8fa01f7ee09ac0f715c.jpg?wh=1438x875)

![](https://static001.geekbang.org/resource/image/dc/6f/dc6fb40781a2e53017e7d48d18f96a6f.jpg?wh=1418x848)

![](https://static001.geekbang.org/resource/image/7c/87/7c01866d547f9517787cf25cd4a65587.jpg?wh=1419x666)

怎么样，看到这样的策划水准，是否觉得CAMEL框架趋动的AI助理完全不输给一个专业的营销策划专员呢？

讲到这里，我冒出了两个想法。是不是只有我们想不到，没有AI做不到的？一大批人可能真的要失业了。所以，赶快学习吧！继续卷起来。

## 总结时刻

智能代理在未来世界中将扮演越来越重要的角色。为了使这些代理能够更好地为人类服务，我们需要找到方法来提高它们的交流能力。CAMEL这篇论文提供了一个全新的视角来看待交流代理的发展。通过使用“角色扮演”框架，可以开发出更加智能和人性化的交流代理，这将为我们的日常生活带来更多的便利。

同时，我们也回顾一下CAMEL框架的实现，以及在这个实现中提示设计的特别之处。

1. 角色扮演：每个代理都被赋予了一个角色，且每个角色都有清晰的责任和行为准则。比如，Python程序员（助手）的角色是根据股票交易员（用户）的指示提供具体的解决方案，而股票交易员的角色是提供详细的任务指示。这种角色扮演机制有助于模拟人类之间的交互过程，更加真实地完成任务。
2. 任务的具体化：为了使AI更好地理解和执行任务，提出了将抽象任务具体化的步骤。这可以帮助AI更清晰地理解任务需求，更准确地给出解决方案。
3. 初始提示的设定：为了启动会话并提供合适的引导，系统初始化时会提供两个初始提示，一条是助手角色的提示，另一条是用户角色的提示。这两条提示分别描述了各自角色的行为准则和任务细节，为整个对话过程提供了框架和指引。
4. 交互规范：该代码实现中有明确的交互规范，如一次只能给出一个指令，解决方案必须具有详细的解释，使用 “Solution: ” 开始输出解决方案，等等。这些规范有助于保持对话的清晰性和高效性。

与传统的提示设计不同，CAMEL中提示的设计更加复杂和细致，更像是一种交互协议或规范。这种设计在一定程度上提高了AI与AI之间自主合作的能力，并能更好地模拟人类之间的交互过程。

## 思考题

1. 在你的业务需求中，有什么需要细化、具体化的业务场景吗？不妨套用这里的CAMEL代码模板，做一次头脑风暴。
2. 对于这个AI交流代理指导框架和提示模板的设计，你能否说说其优劣之处？有没有能进一步改进的地方？

期待在留言区看到你的思考，如果觉得内容对你有帮助，也欢迎分享给有需要的朋友！最后如果你学有余力，可以进一步学习下面的延伸阅读。

## 延伸阅读

1. CAMEL 项目 [官网](https://www.camel-ai.org/) [GitHub](https://github.com/camel-ai/camel) 论文
2. 新闻 [「零人工含量」的「游戏公司」](https://mp.weixin.qq.com/s/GKHD6M74rqC42u2w8EFjJw)\- Chen, Q., Cong, X., Yang, C., Chen, W., Su, Y., Xu, J., Liu, Z., & Sun, M. (2023). [Communicative Agents for Software Development.](https://arxiv.org/abs/2307.07924) arXiv preprint arXiv:2307.07924 \[cs.SE\].