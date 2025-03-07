你好，我是独行。

上节课我们学习了如何构造提示，让AI大模型高效输出我们需要的内容，相信你已经迫不及待地体验过了，但是你有没有发现AI大模型在使用的过程中是有一些局限的，比如：

1. **数据的及时性**：大部分AI大模型都是预训练的，拿ChatGPT举例，3.5引擎数据更新时间截止到2022年1月份，4.0引擎数据更新时间截止到2023年12月份，也就是说如果我们问一些最新的信息，大模型是不知道的。
2. **复杂任务处理**：虽然AI大模型在问答方面表现出色，但它们并不总是能够处理复杂的任务，比如直接编辑或优化Word文档或PDF文件。这些任务通常需要特定的软件工具和用户界面，而大模型主要是基于文本的交互（多模态除外）。
3. **代码生成与下载**：我们希望大模型根据需求描述生成对应的代码，并提供下载链接，大模型也是不支持的。
4. **与企业应用场景的集成**：在和企业应用场景打通的时候，我们希望大模型读取关系型数据库里的数据，并根据提示进行任务处理，同样大模型也是不支持的。

这样的场景非常多，因为大模型的核心能力是**意图理解与文本生成**，而在我们实际应用过程中，输入数据和输出数据不仅仅是纯文本。很多时候我们需要解析用户的输入，比如把Word或PDF文件转化为纯文本，从一个关系型数据库读取数据转化为大模型的输入数据，将大模型的输出内容进行压缩打包并上传至网站供用户下载等等。那这一类任务由谁来做呢？那就是**AI 智能体**，也叫 **AI Agent**。

## AI Agent

AI Agent就是以大语言模型为核心控制器的一套代理系统。

举个形象的例子：如果把人的大脑比作大模型的话，眼睛、耳朵、鼻子、嘴巴、四肢等联合起来叫做Agent，眼睛、耳朵、鼻子感知外界信号作为大脑的输入；嘴巴、四肢等根据大脑处理结果形成反馈进行输出，形成以大脑为核心控制器的一套系统。

![图片](https://static001.geekbang.org/resource/image/b6/36/b6651abc9df589fe238fe79e33677a36.png?wh=1065x727 "图片来源于网络")

控制端处于核心地位，承担记忆、思考以及决策制定等基础工作，感知模块则负责接收和处理来自外部环境的多样化信息，如声音、文字、图像、位置等，最后行动模块通过生成文本、API调用、使用工具等方式来执行任务以及改变环境。

相信通过这样的介绍，你就明白智能体的概念和结构了，接下来我给你介绍一些常见的智能体技术，下面我们统称为Agent。目前比较流行的Agent技术有AutoGen、LangChain等，因为LangChain既是开源的，又提供了一整套围绕大模型的Agent工具，可以说使用起来非常方便，而且从设计到构建、部署、运维等多方面都提供支持，所以下面我们主要介绍一下LangChain的应用场景。

## LangChain介绍

起初，LangChain只是一个技术框架，使用这个框架可以快速开发AI应用程序。这可能是软件开发工程师最容易和AI接触的一个点，因为我们不需要储备太多算法层面的知识，只需要知道如何和模型进行交互，也就是熟练掌握模型暴露的API接口和参数，就可以利用LangChain进行应用开发了。

LangChain发展到今天，已经不再是一个纯粹的AI应用开发框架，而是成为了一个AI应用程序开发平台，它包含4大组件。

- LangChain：大模型应用开发框架。
- LangSmith：统一的DevOps平台，用于开发、协作、测试、部署和监控大模型应用程序，同时，LangSmith是一套Agent DevOps规范，不仅可以用于LangChain应用程序，还可以用在其他框架下的应用程序中。
- LangServe：部署LangChain应用程序，并提供API管理能力，包含版本回退、升级、数据处理等。
- LangGraph：一个用于使用大模型构建有状态、多参与者应用程序的库，是2024年1月份推出的。

放到我们传统软件开发场景中，我认为LangChain就类似于SpringCloud；LangSmith类似于Jenkins + Docker + K8s + Prometheus；LangServe类似于API网关；LangGraph类似于Nacos；当然只是简单比拟。

LangChain可以说是当前最火的AI Agent技术框架，GitHub上拥有超过80k stars，另外使用MIT开源协议，非常友好，自己研究或公司拿来商用都没有问题。

不过一切还在快速发展中，相信很快就会有更多的技术出来。为什么这么说呢？就拿软件开发举例，现在的开发流程是：开发工程师在IDE（IDEA/Eclipse/VSCode）里编写代码，然后打包部署，测试工程师进行测试，然后发布上线。

目前看，大模型已经具备代码编写的能力，理想场景不太可能是由大模型把代码写好，我们下载到本地，用IDE打开，然后打包部署、测试，这说白了只是替换了目前代码编写的场景。我觉得如果AI颠覆软件开发行业，一定是从编码到测试，再到部署一整套流程的颠覆。到那个时候，我们的开发流程可能就变成我上节课讲的那样了。

![](https://static001.geekbang.org/resource/image/fa/ba/faefa1f183c3789f6abc11fb43416bba.png?wh=2516x1086)

当然，也必须要配套相关的技术框架、管理工具来支撑，比如Prompt管理是否还会用Git？会不会有另一套类似于Git用来管理Prompt的工具？代码还会不会存在？大模型可否直接生成可执行程序？还会有Jenkins吗？

你可以畅想一下，未来一整套的技术架构都有可能会被颠覆。

## LangChain技术架构

接下来我们看一下目前LangChain整个平台技术体系，不包含LangGraph，LangChain框架本身包含三大模块。

- LangChain-Core：基础抽象和LangChain表达式语言。
- LangChain-Community：第三方集成。
- LangChain：构成应用程序认知架构的链、代理和检索策略。

![图片](https://static001.geekbang.org/resource/image/12/a4/1280f740f0cd3e71b15bd7e9c0042da4.png?wh=1246x1273 "图片来源于官方网站")

下面我们介绍一下其中的重要模块。

#### 模型I/O（Model I/O）

模型I/O模块主要由三部分组成：格式化（Format）、预测（Predict）、解析（Parse）。顾名思议，模型I/O主要是和大模型打交道，前面我们提到过，大模型其实可以理解为只接受**文本输入**和**文本输出的模型**。

此处注意⚠️：目前LangChain里的大模型是纯文本补全模型，不包含多模态模型。

在把数据输入到AI大模型之前，不论它来源于搜索引擎、向量数据库还是第三方系统接口，都必须先对数据进行格式化，转化成大模型能理解的格式。这就是格式化部分做的事情。

![图片](https://static001.geekbang.org/resource/image/cf/26/cf91ecc5f16e56781ca47aee521a1626.png?wh=4000x1536 "图片来源于官方网站")

预测是指LangChain原生支持的丰富的API，可以实现对各个大模型的调用。

解析主要是指对大模型返回的文本内容的解析，随着多模态模型的日益成熟，相信很快就会实现对多模态模型输出结果的解析。

#### Retrieval

Retrieval可以翻译成检索、抽取，就是从各种数据源中将数据抓取过来，进行词向量化Embedding（Word Embedding）、向量数据存储、向量数据检索的过程。你可以结合图片来理解整个过程。

![图片](https://static001.geekbang.org/resource/image/7b/dc/7bff32c53995cd56850d7ae23ca838dc.png?wh=4256x1472 "图片来源于官方网站")

我会在后面的实战过程中，通过代码来演示各个阶段的含义。

#### Agents

Agents（代理）就是指实现具体任务的模块，比如从某个第三方接口获取数据，用来作为大模型的输入，那么获取数据这个模块就可以称为XXX代理，LangChain本身支持多个类型的代理，当然也可以根据实际需要进行自定义。

#### Chains

链条就是各种各样的顺序调用，类似于Linux命令里的管道。可以是文件处理链条、SQL查询链条、搜索链条等等。LangChain技术体系里链条主要通过LCEL（LangChain表达式）实现。既然是主要使用LCEL实现，那说明还有一部分不是使用LCEL实现的链条，也就是LegacyChain，一些底层的链条，没有通过LCEL实现。

#### Memory

内存是指模型的一些输入和输出，包含历史对话信息，可以放入缓存，提升性能，使用流程和我们软件开发里缓存的使用一样，在执行核心逻辑之前先查询缓存，如果查询到就可以直接使用，在执行完核心逻辑，返回给用户前，将内容写入缓存，方便后面使用。

![图片](https://static001.geekbang.org/resource/image/2a/2e/2ab8dyybe6e271b02ceec0c785d9fc2e.png?wh=2880x1472)

#### Callbacks

LangChain针对各个组件提供回调机制，包括链、模型、代理、工具等。回调的原理和普通开发语言里的回调差不多，就是在某些事件执行后唤起提前设定好的调用。LangChain回调有两种：构造函数回调和请求回调。构造函数回调只适用于对象本身，而请求回调适用于对象本身及其所有子对象。

#### LCEL

LangChain表达式，前面我们介绍Chains（链）的时候讲过，LCEL是用来构建Chains的，我们看官方的一个例子。

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("tell me a short joke about {topic}")
model = ChatOpenAI(model="gpt-4")
output_parser = StrOutputParser()

chain = prompt | model | output_parser

chain.invoke({"topic": "ice cream"})
```

就像我前面讲到的一样，这里的链和Linux里的管道很像，通过特殊字符 `|` 来连接不同组件，构成复杂链条，以实现特定的功能。

```python
chain = prompt | model | output_parser
```

每个组件的输出会作为下一个组件的输入，直到最后一个组件执行完。当然，我们也可以通过LCEL将多个链关联在一起。

```python
chain1 = prompt1 | model | StrOutputParser()
chain2 = (
    {"city": chain1, "language": itemgetter("language")}
    | prompt2
    | model
    | StrOutputParser()
)
chain2.invoke({"person": "obama", "language": "spanish"})
```

以上就是LangChain技术体系里比较重要的几个核心概念，整个设计思想还是比较简单的，你只要记住两个核心思想。

1. 大模型是核心控制器，所有的操作都是围绕大模型的输入和输出在进行。
2. 链的概念，可以将一系列组件串起来进行功能叠加，这对于逻辑的抽象和组件复用是非常关键的。

理解这两个思想，玩转LangChain就不难了，下面我举一个RAG的例子来说明Agent的使用流程。

## Agent使用案例——RAG

就像前面讲的，大模型是基于预训练的，一般大模型训练周期1～3个月，因为成本过高，所以大模型注定不可能频繁更新知识。正是这个训练周期的问题，导致大模型掌握的知识基本上都是滞后的，GPT-4的知识更新时间是2023年12月份，如果我们想要大模型能够理解实时数据，或者把企业内部数据喂给大模型进行推理，我们必须进行检索增强，也就是常说的**RAG，检索增强生成**。

就拿下面这个案例来说吧，我们可以通过RAG技术让大模型支持最新的知识索引。我们先来看一下技术流程图。

![](https://static001.geekbang.org/resource/image/4f/e8/4fe9d7acd1782e033927c46c5c1a48e8.png?wh=2452x1038)

任务一：先通过网络爬虫，爬取大量的信息，这个和搜索引擎数据爬取过程一样，当然这里不涉及PR（Page Rank），只是纯粹的知识爬取，并向量化存储，为了保障我们有最新的数据。

任务二：用户提问时，先把问题向量化，然后在向量库里检索，将检索到的信息构建成提示，喂给大模型，大模型处理完进行输出。

整个过程涉及两个新的概念，一个叫**向量化**，一个叫**向量存储**，你先简单理解下，向量化就是将语言通过数学的方式进行表达，比如男人这个词，通过某种模型向量化后就变成了类似于下面这样的向量数据：

```plain
[0.5,−1.2,0.3,−0.4,0.1,−0.8,1.7,0.6,−1.1,0.9]
```

注意：此处只是举例，实际使用过程中男人这个词生成的向量数据取决于我们使用的 Embedding模型，这个知识我们会在后面的内容中讲解。

向量存储就是将向量化后的数据存储在向量数据库里，常见的向量数据库有Faiss、Milvus，我们会在后面的实战部分用到Faiss。

通过任务一、二的结合，大模型就可以使用最新的知识进行推理了。当然不一定只有这一种思路，比如我们不采取预先爬取最新的数据的方式，而是实时调用搜索引擎的接口，获取最新数据，然后向量化后喂给大模型，同样也可以获取结果。在实际的项目中，要综合成本、性能等多方面因素去选择最合适的技术方案。

## 小结

这节课我们详细学习了智能体以及LangChain技术体系。目前看来，智能体很有可能在未来一段时间内成为AI发展的一个重要方向。因为大模型实际上是大厂商的游戏（除非未来开发出能够低成本训练和推理的大模型），而智能体不一样，普通玩家一样可以入局，而且现在基本上是一片蓝海。

![图片](https://static001.geekbang.org/resource/image/88/7f/889665dc93eb55689bfb5b88c54e3a7f.png?wh=2268x1370)

## 思考题

从软件开发及架构的思路去看，LangChain未来还有可能增加什么组件？你可以对比Java技术体系来思考一下。欢迎你把你思考后的结果分享到评论区，也欢迎你把这节课的内容分享给需要的朋友，我们下节课再见。

[戳此加入课程交流群](https://jinshuju.net/f/D8y8pw)
<div><strong>精选留言（13）</strong></div><ul>
<li><span>zMansi</span> 👍（11） 💬（2）<p>老师langchain和dify的在团队实践中如何选择，dify似乎有比较友好的操作界面，langchain似乎对嵌入企业原有流程更加灵活，那么这两个老师有什么看法</p>2024-06-08</li><br/><li><span>风轻扬</span> 👍（6） 💬（1）<p>抱着了解的想法看了免费的前4节，现在看收获很大，了解到了一个很重要的概念，AI Agent。一直以来，我对AI都是持观望的态度，感觉自己只是一个普通的业务开发，没有能力参与到AI行业。感觉老师为普通开发者打开了一条新的发展道路，普通开发者也是有机会的。打算深入了解一下langchain和dify，这可能是未来5年甚至10年的工作机会</p>2024-06-11</li><br/><li><span>光锥1066</span> 👍（3） 💬（3）<p>老师想问一下RAG的那个流程，模型没有被这些最新数据或者企业内部数据训练过，怎么能保证模型的输出一定符合预期呢</p>2024-06-17</li><br/><li><span>hudy_coco</span> 👍（2） 💬（3）<p>老师，现在市场上应用最多的是langchain吗，后面课程会不会讲一点实战案例</p>2024-06-08</li><br/><li><span>Geek_5203b4</span> 👍（1） 💬（1）<p>RAG ，文心一言似乎就是这么做的。每次键入问题，首先先去网络上查询数据，再转换成向量喂给大模型作为提示，现在理解了。</p>2024-10-28</li><br/><li><span>Geek_frank</span> 👍（1） 💬（1）<p>打卡第三课。
个人思考，我觉得langchain已经把组件的大框框给框定的差不多了，核心开发框架，运维部署监控框架，以及服务治理框架。要说可能缺少的可以单独拎出来一套自动化测试框架。而且目前的组件是一个大集成，以后可能会把组件细分。 比如retrieval模块可以单独抽出来，方便以后扩展支持多模态的内容录入以及检索。 因为每个模块发展到后来可能都会变得越来越复杂。这也正是以前传统软件框架发展的规律</p>2024-06-29</li><br/><li><span>文敦复</span> 👍（1） 💬（1）<p>新手提问：在使用RAG模型处理特定问题时，如果我整合的知识与模型预先训练的知识发生冲突，应该如何处理？更具体地说，我们应该依赖模型原有的知识还是优先使用自建的知识库？</p>2024-06-28</li><br/><li><span>一点点就好</span> 👍（1） 💬（2）<p>对划分哪些是Agent 指责，哪些是大模型职责，可以用一个案例讲解一下，一个现有业务系统怎么改变成自己的Agent 吗</p>2024-06-23</li><br/><li><span>张申傲</span> 👍（1） 💬（1）<p>第3讲打卡~
个人思考：未来LangChain是否有可能扩展数据存储模块，例如LangStore，统一封装对于不同存储引擎的存储、索引和查询相关功能，如搜索场景的ES或者向量数据库Milvus。</p>2024-06-12</li><br/><li><span>mmm</span> 👍（1） 💬（1）<p>老师，请问模型通过理解指令并决策后输出的结果是什么形式的，比如在自动驾驶或机器人场景，路径规划，方向盘或电机转角，力矩这些action是模型直接生成的，还是agent对模型输出进行加工处理后得到的，另外这方面的知识有什么途径可以获取和学习吗？</p>2024-06-11</li><br/><li><span>like life</span> 👍（0） 💬（1）<p>LangChain 未来还有可能增加分布式大模型调度组件、支持集群部署、负载均衡😂</p>2024-11-07</li><br/><li><span>mmm</span> 👍（0） 💬（1）<p>目前这些ai agent的工具在多模态和端侧嵌入式场景适用吗</p>2024-06-11</li><br/><li><span>Karen</span> 👍（0） 💬（0）<p>老师有个问题咨询下，文中提到Embedding 模型，在一个RAG流程中使用不同大模型例如qwen,llama时，这个Embedding 模型是需要特定匹配qwen或llama的才行么？如果需要那如何选择Embedding 模型呢？</p>2025-02-08</li><br/>
</ul>