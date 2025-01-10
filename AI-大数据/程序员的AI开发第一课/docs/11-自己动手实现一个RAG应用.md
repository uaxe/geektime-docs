你好，我是郑晔！

上一讲，我们用了一讲的篇幅介绍了一下 RAG。你现在已经对 RAG 有了一个初步的了解，这一讲，我们就要动手实现一个 RAG 应用了。

我们知道 RAG 有两个核心的过程，一个是把信息存放起来的索引过程，一个是利用找到相关信息生成内容的检索生成过程。所以，我们这个 RAG 应用也要分成两个部分： **索引和检索生成**。

RAG 是为了让大模型知道更多的东西，所以，接下来要实现的 RAG 应用，用来增强的信息就是我们这门课程的内容，我会把开篇词做成一个文件，这样，我们就可以和大模型讨论我们的课程了。LangChain 已经提供了一些基础设施，我们可以利用这些基础设施构建我们的应用。

我们先从索引的过程开始！

## 索引

我们 [上一讲](https://time.geekbang.org/column/article/827289) 已经讲过了索引的基本过程，你可以先回顾一下，这样结合代码看起来就比较容易理解了：

![](https://static001.geekbang.org/resource/image/bd/a2/bdba19e4bbcd2d5bc548cd23372a86a2.jpg?wh=2202x471)

下面是实现这个索引过程的代码：

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("introduction.txt")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma(
    collection_name="ai_learning",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="vectordb"
)
vectorstore.add_documents(splits)

```

出于简化的目的，我这里直接从文本内容中加载信息源，而且选择了 Chroma 作为向量数据库，它对开发很友好，可以把向量数据存储在本地的指定目录下。

我们结合代码来看一下。首先是 TextLoader，它负责加载文本信息。

```python
loader = TextLoader("introduction.txt")
docs = loader.load()

```

这里的 TextLoader 属于 DocumentLoader。在 LangChain 中，有一个很重要的概念叫文档（Document），它包括文档的内容（page\_content）以及相关的元数据（metadata）。所有原始信息都是文档，索引信息的第一步就是把这些文档加载进来，这就是 DocumentLoader 的作用。

除了这里用到的 TextLoader，LangChain 社区里已经实现了大量的 DocumentLoader，比如，从数据库里加载数据的 SQLDatabaseLoader，从亚马逊 S3 加载文件的 S3FileLoader。基本上，大部分我们需要的文档加载器都可以找到直接的实现。

拆分加载进来的文档是 TextSplitter 的主要职责。

```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

```

虽然都是文本，但怎样拆分还是有讲究的，拆分源代码和拆分普通文本，处理方法就是不一样的。LangChain 社区里同样实现了大量的 TextSplitter，我们可以根据自己的业务特点进行选择。我们这里使用了 RecursiveCharacterTextSplitter，它会根据常见的分隔符（比如换行符）递归地分割文档，直到把每个块拆分成适当的大小。

做好基础的准备之后，就要把拆分的文档存放到向量数据库里了：

```python
vectorstore = Chroma(
    collection_name="ai_learning",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="vectordb"
)
vectorstore.add_documents(splits)

```

LangChain 支持了很多的向量数据库，它们都有一个统一的接口：VectorStore，在这个接口中包含了向量数据库的统一操作，比如添加、查询之类的。这个接口屏蔽了向量数据库的差异，在向量数据库并不为所有程序员熟知的情况下，给尝试不同的向量数据库留下了空间。各个具体实现负责实现这些接口，我们这里采用的实现是 Chroma。

在 Chroma 初始化的过程中，我们指定了 Embedding 函数，它负责把文本变成向量。这里我们采用了 OpenAI 的 Embeddings 实现，你完全可以根据自己的需要选择相应的实现，LangChain 社区同样提供了大量的实现，比如，你可以指定 Hugging Face 这个模型社区中的特定模型来做 Embedding。

到这里，我们就完成了索引的过程，看上去还是比较简单的。为了验证我们索引的结果，我们可以调用 similarity\_search 检索向量数据库的数据：

```python
vectorstore = Chroma(
    collection_name="ai_learning",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="vectordb"
)
documents = vectorstore.similarity_search("专栏的作者是谁？")
print(documents)

```

我们这里用的 similarity\_search 表示的是根据相似度进行搜索，还可以使用 max\_marginal\_relevance\_search，它会采用 MMR（Maximal Marginal Relevance，最大边际相关性）算法。这个算法可以在保持结果相关性的同时，尽量选择与已选结果不相似的内容，以增加结果的多样性。

## 检索生成

现在，我们已经为我们 RAG 应用准备好了数据。接下来，就该正式地构建我们的 RAG 应用了。我在之前的聊天机器上做了一些修改，让它能够支持 RAG，代码如下：

```python
from operator import itemgetter
from typing import List
import tiktoken
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage, trim_messages
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_chroma import Chroma

vectorstore = Chroma(
    collection_name="ai_learning",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="vectordb"
)

retriever = vectorstore.as_retriever(search_type="similarity")

def str_token_counter(text: str) -> int:
    enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(text))

def tiktoken_counter(messages: List[BaseMessage]) -> int:
    num_tokens = 3
    tokens_per_message = 3
    tokens_per_name = 1
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, ToolMessage):
            role = "tool"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"Unsupported messages type {msg.__class__}")
        num_tokens += (
                tokens_per_message
                + str_token_counter(role)
                + str_token_counter(msg.content)
        )
        if msg.name:
            num_tokens += tokens_per_name + str_token_counter(msg.name)
    return num_tokens

trimmer = trim_messages(
    max_tokens=4096,
    strategy="last",
    token_counter=tiktoken_counter,
    include_system=True,
)

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

model = ChatOpenAI()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Context: {context}""",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

context = itemgetter("question") | retriever | format_docs
first_step = RunnablePassthrough.assign(context=context)
chain = first_step | prompt | trimmer | model

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "dreamhead"}}

while True:
    user_input = input("You:> ")
    if user_input.lower() == 'exit':
        break

    if user_input.strip() == "":
        continue

    stream = with_message_history.stream(
        {"question": user_input},
        config=config
    )
    for chunk in stream:
        print(chunk.content, end='', flush=True)
    print()

```

为了进行检索，我们需要指定数据源，这里就是我们的向量数据库，其中存放着我们前面已经索引过的数据：

```python
vectorstore = Chroma(
    collection_name="ai_learning",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="vectordb"
)

retriever = vectorstore.as_retriever(search_type="similarity")

```

这段代码引入了一个新的概念： **Retriever**。从名字不难看出，它就是充当 RAG 中的 R。Retriever 的核心能力就是根据文本查询出对应的文档（Document）。

为什么不直接使用向量数据库呢？因为 Retriever 并不只有向量数据库一种实现，比如，WikipediaRetriever 可以从 Wikipedia 上进行搜索。所以，一个 Retriever 接口就把具体的实现隔离开来。

回到向量数据库上，当我们调用 `as_retriever` 创建 Retriever 时，还传入了搜索类型（ `search_type`），这里的搜索类型和前面讲到向量数据库的检索方式是一致的，这里我们传入的是 similarity，当然也可以传入 mmr。

文档检索出来，并不能直接就和我们的问题拼装到一起。这时，就轮到提示词登场了。下面是我们在代码里用到的提示词（改造自 [https://smith.langchain.com/hub/rlm/rag-prompt](https://smith.langchain.com/hub/rlm/rag-prompt)）

```plain
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Context: {context}

```

在这段提示词里，我们告诉大模型，根据提供的上下文回答问题，不知道就说不知道。这是一个提示词模板，在提示词的最后是我们给出的上下文（Context）。这里上下文是根据问题检索出来的内容。

有了这个提示词，再加上聊天历史和我们的问题，就构成了一个完整的提示词模板：

```plain
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            Context: {context}""",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

```

好，我们已经理解了这一讲的新内容，接下来，就是把各个组件组装到一起，构成一条完整的链：

```plain
context = itemgetter("question") | retriever | format_docs
first_step = RunnablePassthrough.assign(context=context)
chain = first_step | prompt | trimmer | model

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

```

在这段代码里，我们首先构建了一个 context 变量，它也一条链。第一步是从传入参数中获取到 question 属性，也就是我们的问题，然后把它传给 retriever。retriever 会根据问题去做检索，对应到我们这里的实现，就是到向量数据库中检索，检索的结果是一个文档列表。

文档是 LangChain 应用内部的表示，要传给大模型，我们需要把它转成文本，这就是 format\_docs 做的事情，它主要是把文档内容取出来拼接到一起：

```python
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

```

这里补充几句实现细节。在 LangChain 代码里， `|` 运算符被用作不同组件之间的连接，其实现的关键就是大部分组件都实现了 Runnable 接口，在这个接口里实现了 `__or__` 和 `__ror__`。 `__or__` 表示这个对象出现在 `|` 左边时的处理，相应的 `__ror__` 表示这个对象出现在右边时的处理。

Python 在处理 `a | b` 这个表达式时，它会先尝试找 `a` 的 `__or__`，如果找不到，它会尝试找 `b` 的 `__ror__`。所以，在 context 的处理中， 来自标准库的 `itemgetter` 虽然没有实现

`__or__`，但 retriever 因为实现了 Runnable 接口，所以，它也实现了 `__ror__`。所以，这段代码才能组装出我们所需的链。

有了 context 变量，我们可以用它构建了另一个变量 first\_step：

```plain
first_step = RunnablePassthrough.assign(context=context)

```

还记得我们的提示词模板里有一个 context 变量吗？它就是从这里来的。

RunnablePassthrough.assign 这个函数就是在不改变链当前状态值的前提下，添加新的状态值。前面我们说了，这里赋给 context 变量的值是一个链，我们可以把它理解成一个函数，它会在运行期执行，其参数就是我们当前的状态值。现在你可以理解 itemgetter(“question”) 的参数是从哪来的了。这个函数的返回值会用来在当前的状态里添加一个叫 context 的变量，以便在后续使用。

其余的代码我们之前已经讲解过了，这里就不再赘述了。至此，我们拥有了一个可以运行的 RAG 应用，我们可以运行一下看看效果：

```bash
You:> 专栏的作者是谁？
专栏的作者是郑晔。
You:> 作者还写过哪些专栏？
作者郑晔还写过《10x程序员工作法》、《软件设计之美》、《代码之丑》和《程序员的测试课》这四个专栏。

```

## 总结时刻

这一讲，我们自己动手实现了一个 RAG 应用，主要包括了索引和检索生成两个部分。

在 LangChain 中，有一些支持 RAG 应用的概念：

- 文档（Document），表示各种信息。

- DocumentLoader，将文档加载进来。

- 向量数据库（VectorStore），提供向量数据库的基础操作。

- Embedding，负责将文本向量化。

- TextSplitter，负责切分加载进来的文档。

- Retriever，负责检索文档，供生成使用。


有了基础的概念支持，在实现 RAG 应用过程中，还需要写好提示词。在样例中，我提供了一个提示词，你也可以根据自己的需要调整提示词，以便更好地支持你的业务。

如果今天的内容你只能记住一件事，那请记住， **LangChain 为 RAG 应用提供了基础的支持**。

## 练习题

这一讲我们实现的 RAG 应用采用了我的开篇词作为原始信息，你可以尝试改造一下，把你的业务资料索引到向量数据库里。欢迎在留言区分享你的改造心得。