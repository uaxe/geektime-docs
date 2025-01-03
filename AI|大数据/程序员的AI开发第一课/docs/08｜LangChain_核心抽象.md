你好，我是郑晔！

上一讲，我们知道了 LangChain 是一个 AI 应用开发的生态，包括了开发框架、社区生态和扩展生态。其中， **最重要的，也是构成整个生态基础的就是开发框架**。

开发框架为我们提供了构建大模型应用的基础抽象和 LangChain 表达式语言，其中，LangChain 表达式语言是为了提高代码的表达性，要想理解 LangChain，关键点就是理解其中的基础抽象。这一讲，我们就来讨论一下 LangChain 的基础抽象。

## ChatModel

既然 LangChain 是为了构建大模型应用而生的，其最核心的基础抽象一定就是聊天模型（ChatModel）。如果你去查看 LangChain 的文档，估计第一个让人困惑的问题一定就是为什么 LangChain 中既有 LLM，也有 ChatModel？

它俩的关系其实类似于之前我们说的补全接口和聊天补全接口的关系，LLM 对应的是文本到文本的生成，而 ChatModel 则是对应着由 ChatGPT 带来的聊天模式。大部分情况下，推荐使用 ChatModel，即便对于非聊天应用也是如此，如同聊天补全接口几乎可以替代补全接口，ChatModel 几乎可以完全替代 LLM。所以，我们后面的讨论也集中在 ChatModel 上。

我们来看一个例子，它的主要作用就是把一段文字由英文翻译成中文：

```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "你的 API Key"
os.environ["OPENAI_API_BASE"] = "你的 API Base"

messages = [
    SystemMessage(content="Translate the following from English into Chinese:"),
    HumanMessage(content="Welcome to LLM application development!"),
]

model = ChatOpenAI(model="gpt-4o-mini")
result = model.invoke(messages)
print(result)

```

在这段代码里，我们创建了一个 ChatModel，也就是这里的 ChatOpenAI，它负责集成 OpenAI 的模型。在创建这个 ChatModel 的同时，我们指定了使用的具体模型，这里我们用到的是 GPT-4o-mini。

正如我们上一讲所说，具体的实现是由社区生态提供的，所以，我们要想使用 ChatOpenAI 模型，需要安装 `langchain-openai` 这个包。有许多服务提供商会提供多个基础抽象的实现，比如，OpenAI 除了 ChatModel 之外，还提供了 Embedding 模型，所有与 OpenAI 相关的内容都会统一放到 `langchain-openai` 这个包里，LangChain 社区将它们统一称为 **供应商（Provider）**，这里的 OpenAI 就是一个供应商。

接下来，就是把消息传给模型。还记得我们在 OpenAI API 提到的消息吗？每条消息都包含角色和内容两个部分，SystemMessage 表示消息的角色是系统，HumanMessage 表示消息的角色是人，对应到 OpenAI API 的底层实现，角色就是用户。然后，我们通过 `model.invoke` 把消息传给了模型，接下来只需等待返回结果。

下面是一次执行的结果，我们前面讲过 OpenAI API 的应答，在这里都可以对应上，我就不过多解释了。

```python
content='欢迎来到大型语言模型应用开发！' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 8, 'prompt_tokens': 26, 'total_tokens': 34, 'completion_tokens_details': {'reasoning_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_483d39d857', 'finish_reason': 'stop', 'logprobs': None} id='run-12d4417e-811b-467a-a92f-3deec9106db6-0' usage_metadata={'input_tokens': 26, 'output_tokens': 8, 'total_tokens': 34}

```

尝试运行这段代码，你会发现，“等待”是执行中最让人难熬的部分，因为我们采用的同步方式执行代码，所以，必须等到所有的内容完全产生之后，我们才能得到响应。你可能想到我要说什么了，没错，我们需要流式响应。我们调整一下代码：

```python
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

messages = [
    SystemMessage(content="Translate the following from English into Chinese:"),
    HumanMessage(content="Welcome to LLM application development!"),
]

model = ChatOpenAI(model="gpt-4o-mini")
stream = model.stream(messages)
for response in stream:
    print(response.content, end="|")

```

同前面的代码相比，这段代码仅有的变化就是用流处理代替了同步调用，这里调用的函数是 `stream`，这个函数的返回值是迭代器（Iterator），我们可以用 `for` 循环来一个一个处理返回的内容。这里我只处理返回的内容部分，为了让结果看得更清楚，我给结果加上了一个分割符，这就是 `end="|"` 处理的效果。

下面就是这段代码一次执行的结果，分割线之间的内容就是一个消息块中的内容：

```python
|欢迎|来到|大型|语言|模型|应用|开发|！||

```

之前我们说过，所有的 LangChain 应用代码核心就是构建一条链。在这里，单独的一个模型也是一条链，只不过这条链上只有一个组件，它就是 ChatModel。前面的两个例子演示的调用方法其实也是链的调用方法。在后面的例子里，我会把重点放在链的组装上，返回结果如何处理在这两个例子里已经做了相应的演示。

除了同步调用和流式处理，链还提供了其它的调用方式，比如，批处理和异步调用等。这些调用方式都是在同步调用和流式处理的基础上做了封装，简化代码的编写，你可以在需要时查看相关的文档。

一旦你了解了 ChatModel，也就了解了构建大模型应用的最核心部分。除此之外的抽象可以说都是 LangChain 提供的抽象。接下来，我们再来了解几个重要的抽象。

## PromptTemplate

想用好大模型，提示词是非常关键的，许多大模型应用本质上就是开发者预置好提示词，把它和用户的提示词结合在一起发给大模型，以便达到更好的效果。

LangChain 把这种预置提示词的方法提炼了出来，引入了一个叫提示词模板（PromptTemplate）的概念。下面是一个例子，这段代码的功效和前面的例子完全一样，只是我用了提示词模板：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "Translate the following from English into Chinese:"),
        ("user", "{text}")
    ]
)

model = ChatOpenAI(model="gpt-4o-mini")

chain = prompt_template | model
result = chain.invoke({"text":"Welcome to LLM application development!"})
print(result)

```

除了使用 ChatPromptTemplate 这个类型之外，提示词模板的部分你会觉得非常眼熟，这和前面例子里面的消息内容几乎一模一样，仅有的差别是在用户消息里面，我们没有采用一个固定的输入，而是引入了一个占位符 `text`。熟悉各种模板语言的话，通过 `{}` 定义占位符的方式你一定不陌生，这个位置就是留给用户填写的内容。

现在我们有了两个组件（PromptTemplate 和 ChatModel），我们可以通过 LCEL 把它们组成一条链：

```python
chain = prompt_template | model

```

**在 LCEL 中，组件声明的先后顺序就是处理逻辑的先后顺序**。在这个处理过程中，先是提示词模板把输入参数处理成发给模型的消息，所以，这里把提示词模板写在前面，模型写在后面。

有了链之后，就可以调用这条链了。相比于直接传递消息，这次我们在调用传递的是一个变量名及其对应的值。PromptTemplate 内部会先做一个替换，用这里的值替换掉模板中的占位符。如果你想知道替换出来的消息到底长什么样，可以像下面这样查看一下：

```python
messages = prompt_template.invoke({"text":"Welcome to LLM application development!"})
print(messages)

```

引入了 PromptTemplate 之后，开发者写的提示词和用户的消息就完全分开了。开发者可以不断地调整提示词以便达到更好的效果，而这一切对用户完全屏蔽掉了。此外，还有一个好处，就是好的提示词模板是可以共享出来的，我们甚至可以把别人写好的提示词用在自己的代码里。我们在上一讲说过的 [提示词社区](https://smith.langchain.com/hub/) 就是这样诞生的。

## OutputParser

PromptTemplate 处理的是输入，与之对应的是 OutputParser，从名字就可以看出，它是负责处理输出的。在前面的例子里，我们看到的输出都是一个对象，在正常情况下，我们还需要编写代码从这个输出对象中解析出自己所需的信息，比如，想要获得大模型生成的内容，我们要这么写：

```python
content = result.content

```

OutputParser 就是把输出结果的解析过程单独拿了出来。LangChain 里提供了一些常用的解析器，比如，把输出结果拿出来就对应着 StrOutputParser。下面是一个例子：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "Translate the following from English into Chinese:"),
        ("user", "{text}")
    ]
)

model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = prompt_template | model | parser
result = chain.invoke({"text":"Welcome to LLM application development!"})
print(result)

```

这个例子接续了上一个例子的代码，唯一的差别是这里创建了 StrOutputParser，因为它处理的是模型的输出结果，所以，它的声明应该是在模型之后的。正如 StrOutputParser 名字所示，它把输出结果解析成了一个字符串， `chain.invoke` 在之前的例子里是直接返回一个对象，而因为有了 StrOutputParser，它返回的结果就成了一个字符串：

```python
欢迎来到大语言模型应用开发！

```

当然，输出解析远不止把内容提取出来。LangChain 还提供了许多不同的输出格式解析器，比如：JSON、CSV、分割符、枚举等等。但你可能会有一个疑问，我该怎么让大模型返回这些格式呢？LangChain 已经为我们做好了准备。

下面我们来看一个例子，我们让大模型帮我们列出一些著名作者的作品，用 JSON 格式返回：

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class Work(BaseModel):
    title: str = Field(description="Title of the work")
    description: str = Field(description="Description of the work")

parser = JsonOutputParser(pydantic_object=Work)

prompt = PromptTemplate(
    template="列举3部{author}的作品。\n{format_instructions}",
    input_variables=["author"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

model = ChatOpenAI(model="gpt-4o-mini")

chain = prompt | model | parser
result = chain.invoke({"author": "老舍"})
print(result)

```

在这个例子里，我们首先声明了返回的格式，也就是这里的作品（Work），其中包含了标题（title）和描述（description）两个字段。然后，声明了一个 JsonOutputParser，告诉它根据 Work 这个对象解析结果。

关键的部分来了，在声明提示词模板时，除了正常的提示词部分，我们还额外加上了 **格式指令（format\_instructions）**，它就是对大模型回复内容的约束。然后，我们在 `partial_variables` 里初始化了格式指令这个变量，给它赋值为 `parser.get_format_instructions()`。

是的，LangChain 已经替我们写好了提示词。许多输出解析器都提供了格式指令，我们只要在配置提示词的时候，把它们添加到其中就可以了。当然，如果你愿意深究，完全也可以调用一下模板的 `invoke` 看看生成的提示词到底是什么样。

顺便说一下，这里的 `partial_variables` 相当于初始化一次的变量，我们可以理解为，它把模板里的一部分内容填写好，生成了一个新的模板，后面使用的就是这个新的模板。相应地， `input_variables` 是来自用户的输入，所以，每次都有不同的内容。

下面是执行这段代码的一次输出，我让它回答了老舍有哪些作品：

```python
[{'title': '骆驼祥子', 'description': '讲述了一个人力车夫的悲惨生活和梦想，反映了旧社会的残酷和人性的复杂。'}, {'title': '四世同堂', 'description': '描绘了一个大家族在抗日战争时期的生活和挣扎，展现了中国传统文化与现代冲突的深刻主题。'}, {'title': '茶馆', 'description': '通过一个茶馆的兴衰反映了社会变迁，揭示了人性、社会和历史的多重层面。'}]

```

到这里，我们讨论了 LangChain 中最核心的三个抽象：ChatModel、PromptTemplate 和 OutputParser。经过这一讲的讲解，你已经可以编写一些简单的大模型应用了，只要把提示词模板的内容替换成你要完成的工作。当然，LangChain 提供的抽象远不止这些。在接下来的内容中，我会结合具体的应用，给你讲解遇到的各种抽象。

## 总结时刻

我们在这一讲中讨论了 LangChain 提供的最核心的三个抽象：

- ChatModel：整个框架的核心，根据输入的内容生成输出。

- PromptTemplate：负责处理输入，有效拆分了开发者提示词和用户提示词。

- OutputParser：负责处理输出，许多输出解析器里包含了格式指令。


如果今天的内容你只能记住一件事，那请记住： **ChatModel 是核心，PromptTemplate 处理输入，OutputParser 处理输出。**

## 练习题

这三个抽象是最核心的，也是最容易理解。我建议你花些时间，尝试着写些代码，增进对于它们的熟悉。欢迎你在留言区分享你在练习中的心得体会。