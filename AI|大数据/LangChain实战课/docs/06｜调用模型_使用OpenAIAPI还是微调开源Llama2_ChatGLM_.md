你好，我是黄佳，欢迎来到LangChain实战课！

之前，我们花了两节课的内容讲透了提示工程的原理以及LangChain中的具体使用方式。今天，我们来着重讨论Model I/O中的第二个子模块，LLM。

![](https://static001.geekbang.org/resource/image/cd/81/cd7e1506af5b6a8e382c2c9eab4d7481.jpg?wh=4000x1536)

让我们带着下面的问题来开始这一节课的学习。大语言模型，不止ChatGPT一种。调用OpenAI的API，当然方便且高效，不过，如果我就是想用其他的模型（比如说开源的Llama2或者ChatGLM），该怎么做？再进一步，如果我就是想在本机上从头训练出来一个新模型，然后在LangChain中使用自己的模型，又该怎么做？

关于大模型的微调（或称精调）、预训练、重新训练、乃至从头训练，这是一个相当大的话题，不仅仅需要足够的知识和经验，还需要大量的语料数据、GPU硬件和强大的工程能力。别说一节课了，我想两三个专栏也不一定能讲全讲透。不过，我可以提纲挈领地把大模型的训练流程和使用方法给你缕一缕。这样你就能体验到，在LangChain中使用自己微调的模型是完全没问题的。

## 大语言模型发展史

说到语言模型，我们不妨先从其发展史中去了解一些关键信息。

Google 2018 年的论文名篇Attention is all you need，提出了Transformer架构，也给这一次AI的腾飞点了火。Transformer是几乎所有预训练模型的核心底层架构。基于Transformer预训练所得的大规模语言模型也被叫做“基础模型”（Foundation Model 或Base Model）。

在这个过程中，模型学习了词汇、语法、句子结构以及上下文信息等丰富的语言知识。这种在大量数据上学到的知识，为后续的下游任务（如情感分析、文本分类、命名实体识别、问答系统等）提供了一个通用的、丰富的语言表示基础，为解决许多复杂的NLP问题提供了可能。

在预训练模型出现的早期，BERT毫无疑问是最具代表性的，也是影响力最大的模型。BERT通过同时学习文本的前向和后向上下文信息，实现对句子结构的深入理解。BERT之后，各种大型预训练模型如雨后春笋般地涌现，自然语言处理（NLP）领域进入了一个新时代。这些模型推动了NLP技术的快速发展，解决了许多以前难以应对的问题，比如翻译、文本总结、聊天对话等等，提供了强大的工具。

![](https://static001.geekbang.org/resource/image/7f/a6/7f1108deceaa4b5281ed431598f1b0a6.jpg?wh=10666x4300)

当然，现今的预训练模型的趋势是参数越来越多，模型也越来越大，训练一次的费用可达几百万美元。这样大的开销和资源的耗费，只有世界顶级大厂才能够负担得起，普通的学术组织和高等院校很难在这个领域继续引领科技突破，这种现象开始被普通研究人员所诟病。

![](https://static001.geekbang.org/resource/image/95/ef/95828d4e2234e7130bb2d500455092ef.jpg?wh=10666x6000)

## 预训练+微调的模式

不过，话虽如此，大型预训练模型的确是工程师的福音。因为，经过预训练的大模型中所习得的语义信息和所蕴含的语言知识，能够非常容易地向下游任务迁移。NLP应用人员可以对模型的头部或者部分参数根据自己的需要进行适应性的调整，这通常涉及在相对较小的有标注数据集上进行有监督学习，让模型适应特定任务的需求。

这就是对预训练模型的微调（Fine-tuning）。微调过程相比于从头训练一个模型要快得多，且需要的数据量也要少得多，这使得作为工程师的我们能够更高效地开发和部署各种NLP解决方案。

![](https://static001.geekbang.org/resource/image/75/af/75edd66d67ec8a20326b69514c9d9daf.jpg?wh=10666x5061)

图中的“具体任务”，其实也可以更换为“具体领域”。那么总结来说：

- **预训练**：在大规模无标注文本数据上进行模型的训练，目标是让模型学习自然语言的基础表达、上下文信息和语义知识，为后续任务提供一个通用的、丰富的语言表示基础。
- **微调**：在预训练模型的基础上，可以根据特定的下游任务对模型进行微调。现在你经常会听到各行各业的人说： _我们的优势就是领域知识嘛！我们比不过国内外大模型，我们可以拿开源模型做垂直领域嘛！做垂类模型！_—— 啥叫垂类？指的其实就是根据领域数据微调开源模型这件事儿。

这种预训练+微调的大模型应用模式优势明显。首先，预训练模型能够将大量的通用语言知识迁移到各种下游任务上，作为应用人员，我们不需要自己寻找语料库，从头开始训练大模型，这减少了训练时间和数据需求；其次，微调过程可以快速地根据特定任务进行优化，简化了模型部署的难度；最后，预训练+微调的架构具有很强的可扩展性，可以方便地应用于各种自然语言处理任务，大大提高了NLP技术在实际应用中的可用性和普及程度，给我们带来了巨大的便利。

好，下面咱们开始一步步地使用开源模型。今天我要带你玩的模型主要是Meta（Facebook）推出的Llama2。当然你可以去Llama的官网下载模型，然后通过Llama官方 [GitHub](https://github.com/facebookresearch/llama) 中提供的方法来调用它。但是，我还是会推荐你从HuggingFace下载并导入模型。因为啊，前天百川，昨天千问，今天流行Llama，明天不就流行别的了嘛。模型总在变，但是HuggingFace一直在那里，支持着各种开源模型。我们学东西，尽量选择学一次能够复用的知识。

## 用 HuggingFace 跑开源模型

### 注册并安装 HuggingFace

第一步，还是要登录 [HuggingFace](https://huggingface.co/) 网站，并拿到专属于你的Token。（如果你做了前面几节课的实战案例，那么你应该已经有这个API Token了）

第二步，用 `pip install transformers` 安装HuggingFace Library。详见 [这里](https://huggingface.co/docs/transformers/installation)。

第三步，在命令行中运行 `huggingface-cli login`，设置你的API Token。

![](https://static001.geekbang.org/resource/image/5f/e6/5fa0c088652c8776f5ec50a059b1b1e6.png?wh=1475x668)

当然，也可以在程序中设置你的API Token，但是这不如在命令行中设置来得安全。

```plain
# 导入HuggingFace API Token
import os
os.environ['HUGGINGFACEHUB_API_TOKEN'] = '你的HuggingFace API Token'

```

### 申请使用 Meta 的 Llama2 模型

在HuggingFace的Model中，找到 [meta-llama/Llama-2-7b](https://huggingface.co/meta-llama/Llama-2-7b)。注意，各种各样版本的Llama2模型多如牛毛，我们这里用的是最小的7B版。此外，还有13b\\70b\\chat版以及各种各样的非Meta官方版。

![](https://static001.geekbang.org/resource/image/88/17/88a4b8d60cc93e77c3573663aa096217.png?wh=3028x710)

选择meta-llama/Llama-2-7b这个模型后，你能够看到这个模型的基本信息。如果你是第一次用Llama，你需要申请Access，因为我已经申请过了，所以屏幕中间有句话：“You have been granted access to this model”。从申请到批准，大概是几分钟的事儿。

![](https://static001.geekbang.org/resource/image/46/ce/46c59c59545720ccff6d7c560792d4ce.png?wh=3029x1662)

### 通过 HuggingFace 调用 Llama

好，万事俱备，现在我们可以使用HuggingFace的Transformers库来调用Llama啦！

```plain
# 导入必要的库
from transformers import AutoTokenizer, AutoModelForCausalLM

# 加载预训练模型的分词器
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")

# 加载预训练的模型
# 使用 device_map 参数将模型自动加载到可用的硬件设备上，例如GPU
model = AutoModelForCausalLM.from_pretrained(
          "meta-llama/Llama-2-7b-chat-hf",
          device_map = 'auto')

# 定义一个提示，希望模型基于此提示生成故事
prompt = "请给我讲个玫瑰的爱情故事?"

# 使用分词器将提示转化为模型可以理解的格式，并将其移动到GPU上
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

# 使用模型生成文本，设置最大生成令牌数为2000
outputs = model.generate(inputs["input_ids"], max_new_tokens=2000)

# 将生成的令牌解码成文本，并跳过任何特殊的令牌，例如[CLS], [SEP]等
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

# 打印生成的响应
print(response)

```

这段程序是一个很典型的HuggingFace的Transformers库的用例，该库提供了大量预训练的模型和相关的工具。

- 导入AutoTokenizer：这是一个用于自动加载预训练模型的相关分词器的工具。分词器负责将文本转化为模型可以理解的数字格式。
- 导入AutoModelForCausalLM：这是用于加载因果语言模型（用于文本生成）的工具。
- 使用from\_pretrained方法来加载预训练的分词器和模型。其中， `device_map = 'auto'` 是为了自动地将模型加载到可用的设备上，例如GPU。
- 然后，给定一个提示（prompt）： `"请给我讲个玫瑰的爱情故事?"`，并使用分词器将该提示转换为模型可以接受的格式， `return_tensors="pt"` 表示返回PyTorch张量。语句中的 `.to("cuda")` 是GPU设备格式转换，因为我在GPU上跑程序，不用这个的话会报错，如果你使用CPU，可以试一下删掉它。
- 最后使用模型的 `.generate()` 方法生成响应。 `max_new_tokens=2000` 限制生成的文本的长度。使用分词器的 `.decode() ` 方法将输出的数字转化回文本，并且跳过任何特殊的标记。

因为是在本地进行推理，耗时时间比较久。在我的机器上，大概需要30s～2min产生结果。

![](https://static001.geekbang.org/resource/image/93/98/933b7b11512bd06a977027cbbfd8d198.png?wh=1653x651)

这样的回答肯定不能直接用做商业文案，而且，我的意思是玫瑰花相关的故事，它明显把玫瑰理解成一个女孩的名字了。所以，开源模型，尤其是7B的小模型和Open AI的ChatGPT还是有一定差距的。

## LangChain 和 HuggingFace 的接口

讲了半天，LangChain未出场。下面让我们看一看，如何把HuggingFace里面的模型接入LangChain。

### 通过 HuggingFace Hub

第一种集成方式，是通过HuggingFace Hub。HuggingFace Hub 是一个开源模型中心化存储库，主要用于分享、协作和存储预训练模型、数据集以及相关组件。

我们给出一个HuggingFace Hub 和LangChain集成的代码示例。

```plain
# 导入HuggingFace API Token
import os
os.environ['HUGGINGFACEHUB_API_TOKEN'] = '你的HuggingFace API Token'

# 导入必要的库
from langchain import PromptTemplate, HuggingFaceHub, LLMChain

# 初始化HF LLM
llm = HuggingFaceHub(
    repo_id="google/flan-t5-small",
    #repo_id="meta-llama/Llama-2-7b-chat-hf",
)

# 创建简单的question-answering提示模板
template = """Question: {question}
              Answer: """

# 创建Prompt
prompt = PromptTemplate(template=template, input_variables=["question"])

# 调用LLM Chain --- 我们以后会详细讲LLM Chain
llm_chain = LLMChain(
    prompt=prompt,
    llm=llm
)

# 准备问题
question = "Rose is which type of flower?"

# 调用模型并返回结果
print(llm_chain.run(question))

```

可以看出，这个集成过程非常简单，只需要在HuggingFaceHub类的repo\_id中指定模型名称，就可以直接下载并使用模型，模型会自动下载到HuggingFace的Cache目录，并不需要手工下载。

初始化LLM，创建提示模板，生成提示的过程，你已经很熟悉了。这段代码中有一个新内容是我通过llm\_chain来调用了LLM。这段代码也不难理解，有关Chain的概念我们以后还会详述。

不过，我尝试使用meta-llama/Llama-2-7b-chat-hf这个模型时，出现了错误，因此我只好用比较旧的模型做测试。我随便选择了google/flan-t5-small，问了它一个很简单的问题，想看看它是否知道玫瑰是哪一种花。

![](https://static001.geekbang.org/resource/image/5b/71/5bfc31eacb422fcd1d148bb1a2b3bf71.png?wh=547x149)

模型告诉我，玫瑰是花。对，答案只有一个字，flower。这…不得不说，2023年之前的模型，和2023年之后的模型，水平没得比。以前的模型能说话就不错了。

![](https://static001.geekbang.org/resource/image/yy/3e/yyc2177bc3c06f1d738f26985b9fbd3e.png?wh=578x92)

### 通过 HuggingFace Pipeline

既然HuggingFace Hub还不能完成Llama-2的测试，让我们来尝试另外一种方法，HuggingFace Pipeline。HuggingFace 的 Pipeline 是一种高级工具，它简化了多种常见自然语言处理（NLP）任务的使用流程，使得用户不需要深入了解模型细节，也能够很容易地利用预训练模型来做任务。

让我来看看下面的示例：

````plain
# 指定预训练模型的名称
model = "meta-llama/Llama-2-7b-chat-hf"

# 从预训练模型中加载词汇器
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(model)

# 创建一个文本生成的管道
import transformers
import torch
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
    max_length = 1000
)

# 创建HuggingFacePipeline实例
from langchain import HuggingFacePipeline
llm = HuggingFacePipeline(pipeline = pipeline,
                          model_kwargs = {'temperature':0})

# 定义输入模板，该模板用于生成花束的描述
template = """
              为以下的花束生成一个详细且吸引人的描述：
              花束的详细信息：
              ```{flower_details}```
           """

# 使用模板创建提示
from langchain import PromptTemplate,  LLMChain
prompt = PromptTemplate(template=template,
                     input_variables=["flower_details"])

# 创建LLMChain实例
from langchain import PromptTemplate
llm_chain = LLMChain(prompt=prompt, llm=llm)

# 需要生成描述的花束的详细信息
flower_details = "12支红玫瑰，搭配白色满天星和绿叶，包装在浪漫的红色纸中。"

# 打印生成的花束描述
print(llm_chain.run(flower_details))

````

这里简单介绍一下代码中使用到的transformers pipeline的配置参数。

![](https://static001.geekbang.org/resource/image/41/7e/41yyb05408bd6a16e349f89279548f7e.jpg?wh=2490x1034)

生成的结果之一如下：

![](https://static001.geekbang.org/resource/image/1b/3c/1bb303ec8bd8150d23bebc79035af13c.jpg?wh=6396x3569)

此结果不敢恭维。但是，后续的测试告诉我，这很有可能是7B这个模型太小，尽管有形成中文的相应能力，但是能力不够强大，也就导致了这样的结果。

至此，通过HuggingFace接口调用各种开源模型的尝试成功结束。下面，我们进行最后一个测试，看看LangChain到底能否直接调用本地模型。

## 用 LangChain 调用自定义语言模型

最后，我们来尝试回答这节课开头提出的问题，假设你就是想训练属于自己的模型。而且出于商业秘密的原因，不想开源它，不想上传到HuggingFace，就是要在本机运行模型。此时应该如何利用LangChain的功能？

我们可以创建一个LLM的衍生类，自己定义模型。而LLM这个基类，则位于langchain.llms.base中，通过from langchain.llms.base import LLM语句导入。

这个自定义的LLM类只需要实现一个方法：

- \_call方法：用于接收输入字符串并返回响应字符串。

以及一个可选方法：

- \_identifying\_params方法：用于帮助打印此类的属性。

下面，让我们先从HuggingFace的 [这里](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/tree/main)，下载一个llama-2-7b-chat.ggmlv3.q4\_K\_S.bin模型，并保存在本地。

![](https://static001.geekbang.org/resource/image/54/1c/54c0ec3cbe3c3cyy6988de10f619b51c.png?wh=3879x1976)

你可能会质疑我，不是说自己训练，自己微调，不再用HuggingFace了吗？

不好意思，容许我解释一下。自己训练一个能用的模型没那么容易。这个模型，它并不是原始的Llama模型，而是TheBloke这位老兄用他的手段为我们量化过的新模型，你也可以理解成，他已经为我们压缩或者说微调了Llama模型。

> 量化是AI模型大小和性能优化的常用技术，它将模型的权重简化到较少的位数，以减少模型的大小和计算需求，让大模型甚至能够在CPU上面运行。当你看到模型的后缀有GGML或者GPTQ，就说明模型已经被量化过，其中GPTQ 是一种仅适用于 GPU 的特定格式。GGML 专为 CPU 和 Apple M 系列设计，但也可以加速 GPU 上的某些层。llama-cpp-python这个包就是为了实现GGML而制作的。

所以，这里你就假设，咱们下载下来的llama-2-7b-chat.ggmlv3.q4\_K\_S.bin这个模型，就是你自己微调过的。将来你真的微调了Llama2、ChatGLM、百川或者千问的开源版，甚至是自己从头训练了一个mini-ChatGPT，你也可以保存为you\_own\_model.bin的格式，就按照下面的方式加载到LangChain之中。

然后，为了使用llama-2-7b-chat.ggmlv3.q4\_K\_S.bin这个模型，你需要安装 pip install llama-cpp-python 这个包。

```plain
# 导入需要的库
from llama_cpp import Llama
from typing import Optional, List, Mapping, Any
from langchain.llms.base import LLM

# 模型的名称和路径常量
MODEL_NAME = 'llama-2-7b-chat.ggmlv3.q4_K_S.bin'
MODEL_PATH = '/home/huangj/03_Llama/'

# 自定义的LLM类，继承自基础LLM类
class CustomLLM(LLM):
    model_name = MODEL_NAME

    # 该方法使用Llama库调用模型生成回复
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        prompt_length = len(prompt) + 5
        # 初始化Llama模型，指定模型路径和线程数
        llm = Llama(model_path=MODEL_PATH+MODEL_NAME, n_threads=4)
        # 使用Llama模型生成回复
        response = llm(f"Q: {prompt} A: ", max_tokens=256)

        # 从返回的回复中提取文本部分
        output = response['choices'][0]['text'].replace('A: ', '').strip()

        # 返回生成的回复，同时剔除了问题部分和额外字符
        return output[prompt_length:]

    # 返回模型的标识参数，这里只是返回模型的名称
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"name_of_model": self.model_name}

    # 返回模型的类型，这里是"custom"
    @property
    def _llm_type(self) -> str:
        return "custom"


# 初始化自定义LLM类
llm = CustomLLM()

# 使用自定义LLM生成一个回复
result = llm("昨天有一个客户抱怨他买了花给女朋友之后，两天花就枯了，你说作为客服我应该怎么解释？")

# 打印生成的回复
print(result)

```

代码中需要解释的内容不多，基本上就是CustomLLM类的构建和使用，类内部通过Llama类来实现大模型的推理功能，然后直接返回模型的回答。

![](https://static001.geekbang.org/resource/image/02/59/0275183b3863e602c59afb94707aca59.jpg?wh=6369x1322)

似乎Llama经过量化之后，虽然仍读得懂中文，但是不会讲中文了。

翻译成中文，他的回答是这样的。

_当客户抱怨他们为女朋友买的花在两天内就枯萎了，我会以礼貌和专业的方式这样解释：_

_“感谢您把这个问题告诉我们。对于给您带来的任何不便，我深感抱歉。有可能这些花没有被正确地存储或照料，这可能影响了它们的生命期。我们始终以提供高质量的产品为荣，但有时可能会出现意外的问题。请您知道，我们非常重视您的满意度并随时为您提供帮助。您希望我为您提供替换或退款吗？”_

看上去，除了中文能力不大灵光之外，Llama2的英文表现真的非常完美，和GPT3.5差距不是很大，要知道：

1. 这可是开源模型，而且是允许商业的免费模型。
2. 这是在本机 CPU 的环境下运行的，模型的推理速度还是可以接受的。
3. 这仅仅是Llama的最小版本，也就是7B的量化版，就达到了这么好的效果。

基于上述三点原因，我给Llama2打98.5分。

## 总结时刻

今天的课程到此就结束了，相信你学到了很多新东西吧。的确，进入大模型开发这个领域，就好像打开了通往新世界的一扇门，有太多的新知识，等待着你去探索。

现在，你已经知道大模型训练涉及在大量数据上使用深度学习算法，通常需要大量计算资源和时间。训练后，模型可能不完全适合特定任务，因此需要微调，即在特定数据集上继续训练，以使模型更适应该任务。为了减小部署模型的大小和加快推理速度，模型还会经过量化，即将模型参数从高精度格式减少到较低精度。

如果你想继续深入学习大模型，那么有几个工具你不得不接着研究。

- PyTorch是一个流行的深度学习框架，常用于模型的训练和微调。
- HuggingFace是一个开源社区，提供了大量预训练模型和微调工具，尤其是NLP任务。
- LangChain则擅长于利用大语言模型的推理功能，开发新的工具或应用，完成特定的任务。

这些工具和库在AI模型的全生命周期中起到关键作用，使研究者和开发者更容易开发和部署高效的AI系统。

## 思考题

1. 现在请你再回答一下，什么时候应该使用OpenAI的API？什么时候应该使用开源模型？或者自己开发/微调的模型？

   提示：的确，文中没有给出这个问题的答案。因为这个问题并没有标准答案。

2. 请你使用HuggingFace的Transformers库，下载新的模型进行推理，比较它们的性能。

3. 请你在LangChain中，使用HuggingFaceHub和HuggingFace Pipeline这两种接口，调用当前最流行的大语言模型。

   提示：HuggingFace Model 页面，有模型下载量的当月排序，当月下载最多的模型就是最流行的模型。

期待在留言区看到你的分享，我们一起交流探讨，共创一个良好的学习氛围。如果你觉得内容对你有帮助，也欢迎分享给有需要的朋友！最后如果你学有余力，可以进一步学习下面的延伸阅读。

## 延伸阅读

1. Llama2，开源的可商用类ChatGPT模型， [Facebook链接](https://ai.meta.com/research/publications/llama-2-open-foundation-and-fine-tuned-chat-models/)、 [GitHub链接](https://github.com/facebookresearch/llama)
2. HuggingFace [Transformer](https://huggingface.co/docs/transformers/index) 文档
3. PyTorch 官方 [教程](https://pytorch.org/tutorials/)、 [文档](https://pytorch.org/docs/stable/index.html)
4. [AutoGPTQ](https://github.com/PanQiWei/AutoGPTQ) 基于GPTQ算法的大模型量化工具包
5. [Llama CPP](https://github.com/ggerganov/llama.cpp) 支持 [GGML](https://github.com/ggerganov/ggml)，目标是在MacBook（或类似的非GPU的普通家用硬件环境）上使用4位整数量化运行Llama模型