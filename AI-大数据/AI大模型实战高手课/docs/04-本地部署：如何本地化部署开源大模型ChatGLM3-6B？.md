你好，我是独行。

前面听我讲了这么多，相信你也很想上手试一试了。从这节课开始，我们进入一个新的章节，这部分我们会学习如何部署开源大模型ChatGLM3-6B，本地搭建向量库并结合LangChain做检索增强（RAG），并且我会带你做一次微调，从头学习 **大模型的部署、微调、推理** 等过程。

这节课我们就来讲一下如何本地化部署ChatGLM3-6B（后面我们简称为6B）。讲6B之前我们先整体看一下目前国内外大模型的发展状况，以便我们进行技术选型。

## 大模型的选择

当前环境下，大模型百花齐放。我筛选出了一些核心玩家，你可以看一下表格。非核心的其实还有很多，这里我就不一一列举了。厂商虽然很多，但真正在研究技术的没多少，毕竟前面我们讲过，玩大模型投入非常大，光看得见的成本，包括人才、训练和硬件费用，一年就得投入几个亿，不是一般玩家能玩得起的。

![图片](https://static001.geekbang.org/resource/image/a4/a0/a4e540e0b41d3d58e2cec92ae15d38a0.png?wh=2532x1340)

当然，也有不少厂商是基于LLaMA爆改的，或者叫套壳，不是真正意义上的自研大模型。

ChatGLM-6B和LLaMA2是目前开源项目比较热的两个，早在2023年年初，国内刚兴起大模型热潮时，智谱AI就开源了ChatGLM-6B，当然130B也可以拿过来跑，只不过模型太大，需要比较多的显卡，所以很多人就部署6B试玩。

从长远看，信创大潮下，国产大模型肯定是首选，企业布局AI大模型，要么选择MaaS服务，调用大厂大模型API，要么选择开源大模型，自己微调、部署，为上层应用提供服务。使用MaaS服务会面临数据安全问题，所以一般企业会选择私有化部署+公有云MaaS混合的方式来架构。在国产厂商里面，光从技术角度讲，我认为智谱AI是国内大模型研发水平最高的厂商，这也是我选择ChatGLM-6B的原因。

还有一点需要考虑，就是6B参数规模为62亿，单张3090显卡就可以进行微调（P-Turing）和推理，对于中小企业而言，简直就是福音。

![图片](https://static001.geekbang.org/resource/image/af/8b/af978014b18d697cd68257e62975ec8b.png?wh=2540x1054)

当然，如果企业预算充足（百万以上），可以尝试6B的老大哥GLM-130B，简称130B，千亿参数规模，推理能力更强，使用130B的话除了GPU资源费用，还需要进行商业授权，这个要注意。

![图片](https://static001.geekbang.org/resource/image/a5/9a/a53215243f9b534bdbyy5dd038d0779a.png?wh=2438x580)

下面我们讲讲预算不足的情况下，怎么搞定显卡资源？

## 如何搞定显卡资源？

玩儿大模型第一步就是要想办法解决计算资源问题，要么CPU要么GPU，当然还有TPU，不过TPU太小众，这里我就不介绍了。我建议你想办法申请GPU，因为适合CPU计算的大模型不多，有些大模型可以在CPU上进行推理，但是需要使用低精度轻量化模型，而低精度下模型会失真，效果肯定不行，只适合简单把玩。如果要真正体验并应用到实际项目，必须上GPU。那我们可以从哪些渠道去购买GPU呢？

1. **购买二手显卡**：无论是个人使用还是企业使用，都可以考虑在网上购买二手RTX3090显卡，单卡24G显存，8000块左右，可以用于本地微调、推理。如果想用在产品上，也可以通过云服务做映射，提供简单的推理服务，但是不适合为大规模客户提供服务。
2. **淘宝租赁显卡资源**：适合个人学习使用，可以按天/周/月/年购买服务，比较灵活，成本也不高。
3. **在线GPU租赁**：比如autodl、RTX3090-24G，每月大概不到900块钱，也很划算。不仅仅可以用来本地测试，还可以用于生产环境推理，如果用在生产环境的话，最好按照实际推理需求，评估每秒推理量（具体方法我会在大模型应用架构部分讲解），搭建高可用推理环境。
4. **各个平台免费资源**：比如阿里云PAI平台、智谱AI的开放平台等，对于新人都有一定的免费GPU额度，这个方式省钱，但是不推荐，因为有时需要为平台推广拉人，也挺耗时间的。

## ChatGLM3-6B部署

ChatGLM-6B目前已经发展到第3代ChatGLM3-6B，除了中英文推理，还增强了数学、代码等推理能力，我记得一年前的6B在代码或者数学方面是比较弱的。根据目前的官方信息，在语义、数学、推理、代码、知识等不同角度的数据集上测评显示，ChatGLM3-6B-Base在10B以下的基础模型中性能是最强的，除此之外，还具有8K、32K、128K等多个长文理解能力版本。下面我们就一步一步来安装部署ChatGLM3-6B，你也可以在 [官方文档](https://github.com/THUDM/ChatGLM3) 里找到安装教程。

#### 准备环境

操作系统推荐Linux环境，如Ubuntu或者CentOS。

![图片](https://static001.geekbang.org/resource/image/0c/eb/0c3defe2984a1f29721b5920016104eb.png?wh=2314x606)

- Python推荐3.10～3.11版本。
- Transformers库推荐4.36.2版本。
- Torch 推荐使用 2.0 及以上的版本，以获得最佳的推理性能。

#### 克隆代码

```python
git clone https://github.com/THUDM/ChatGLM3

```

![图片](https://static001.geekbang.org/resource/image/e5/bc/e53bcfdc761101b5a5e55b4f58dd6dbc.png?wh=1022x223)

#### 安装依赖

注意：要切换成国内pip源，比如阿里云，下载会快很多。

```python
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
cd ChatGLM3
pip install -r requirements.txt

```

显示以下内容表明依赖安装成功。

![图片](https://static001.geekbang.org/resource/image/e8/4b/e8b4f77dff6dd93ab9554e2853cc564b.png?wh=1914x594)

#### 下载模型

```python
git clone https://huggingface.co/THUDM/chatglm3-6b

```

如果Huggingface下载比较慢的话，也可以选择ModelScope进行下载。下载完将chatglm3-6b文件夹重新命名成model并放在ChatGLM3文件夹下，这一步非必需，只要放在一个路径下，在下一步提示的文件里，指定好模型文件路径即可。

#### 命令行模式启动

打开文件 `basic_demo/cli_demo.py`，修改模型加载路径。

```python
MODEL_PATH = os.environ.get('MODEL_PATH', '../model')

```

执行 `python cli_demo.py`。

![图片](https://static001.geekbang.org/resource/image/b9/1b/b9c920372yy65521df248f8efb66b01b.png?wh=1906x537)

#### Web控制台模式启动

打开文件 `basic_demo/web_demo_gradio.py`，修改模型加载路径。

```python
MODEL_PATH = os.environ.get('MODEL_PATH', '../model')

```

同时修改最后一行：

```python
demo.launch(server_name="127.0.0.1", server_port=7870, inbrowser=True, share=False)

```

server\_name修改为本地IP，并指定端口server\_port即可。也可以设置share=True，使用gradio提供的链接进行访问。

执行 `python web_demo_gradio.py`。

![图片](https://static001.geekbang.org/resource/image/70/fa/70cbbe44362d1548094f77a959e7c1fa.png?wh=2452x1436)

默认情况下，模型以FP16精度加载，大概需要13GB显存。如果你的电脑没有GPU，只能通过CPU启动，6B也是支持的，需要大概32G的内存。我们修改一下模型加载脚本。

```python
model = AutoModel.from_pretrained(MODEL_PATH trust_remote_code=True).float()

```

如果你的电脑有GPU，但是显存不够，也可以通过修改模型加载脚本，在4-bit量化下运行，只需要6GB左右的显存就可以进行流程推理。

```python
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, ).quantize(4).cuda()

```

同时，官方也提供了一个全新的web demo，支持Chat、Tool、Code Interpreter，就在我们克隆下来的代码里，在文件夹composite\_demo下。

```python
cd composite_demo
pip install -r requirements.txt
export MODEL_PATH=../model
streamlit run main.py 或者 python -m streamlit run main.py

```

页面确实上了一个档次。

![图片](https://static001.geekbang.org/resource/image/28/06/284f2c42be5dd945ee495163602aff06.png?wh=2804x1432)

接下来我简单总结一下部署过程：

1. 安装Python环境，包含pip；
2. 下载代码；
3. 下载模型；
4. 安装依赖；
5. 修改示例代码，指定模型路径、精度等参数；
6. 命令行启动。

整体来说，如果Python版本在3.10～3.11之间，网络环境也没问题的话，安装还是很快的，如果有GPU的话，推理效果也是很好的。在我们部署好模型之后，就可以进行推理了。推理之前，6B有几个参数可以进行设置，就是 **超参数**，用来控制模型的推理准确度，我们知道大模型推理每次给的回答可能都和之前不一样，这也是为什么大模型不能用来处理精确度要求很高的任务的原因，比如让大模型算个税、算工资等等。

## 超参数介绍

ChatGLM3-6B有3个参数可以设置。

1. max\_length：模型的总token限制，包括输入和输出的tokens。
2. temperature：模型的温度。温度只是调整单词的概率分布。它最终的宏观效果是，在较低的温度下，我们的模型更具确定性，而在较高的温度下，则不那么确定。数字越小，给出的答案越精确。
3. top\_p：模型采样策略参数。每一步只从累积概率超过某个阈值 p 的最小单词集合中进行随机采样，而不考虑其他低概率的词。只关注概率分布的核心部分，忽略了尾部。

对于以下场景，官方推荐使用这样的参数进行设置：

![图片](https://static001.geekbang.org/resource/image/fa/58/faf0a74ffb6d1766d3d309442a6f5358.png?wh=2544x1346)

系统设置好，我们基本就可以开始进行问答了，ChatGLM3-6B采用了一种新的Prompt格式，看上去应该是模仿的ChatGPT。下面我们介绍下这种提问格式。

## 新的Prompt格式

新的提示格式，主要是增加了几个角色，在对话场景中，有且仅有以下三种角色。

- system：系统信息，出现在消息的最前面，可以指定回答问题的角色。
- user：我们提的问题。
- assistant：大模型给出的回复。

在代码场景中，有且仅有user、assistant、system、observation四种角色。observation是外部返回的结果，比如调用外部API，代码执行逻辑等返回的结果，都通过observation返回。observation必须放在assistant之后。

下面这个是官方提供的例子，基本把以上4种角色都解释清楚了。

````python
<|system|>
Answer the following questions as best as you can. You have access to the following tools:
[
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string"},
            },
            "required": ["location"],
        },
    }
]
<|user|>
今天北京的天气怎么样？
<|assistant|>
好的，让我们来查看今天的天气
<|assistant|>get_current_weather

```python
tool_call(location="beijing", unit="celsius")

<|observation|>
{"temperature": 22}
<|assistant|>
根据查询结果，今天北京的气温为 22 摄氏度。

````

为什么会这么设计呢？

首先，当前阶段的大模型经过训练后，都可以遵守系统消息，而系统消息不算用户对话的一部分，与用户是隔离的，但是可以控制模型与用户交互的范围，比如我们在system角色里指定模型充当Java技术专家，那么就可以指导模型的输出偏向于Java技术范围。

还有一个原因就是 **防止用户进行输入注入攻击**。在进行多轮对话的时候，每次新的对话都会把历史对话都带进去。如果我们在前面的对话中，告诉模型错误的提示，那么这些错误的提示会在后续的对话中被当作正确的上下文带进去。我们知道基于自回归的模型，会根据上下文进行内容推理，这样就可能生成错误的内容。角色可以使内容更加容易区分，增加注入攻击的复杂度。这种方式不一定能处理所有的攻击类型，类似于我们日常开发中的XSS注入，只能尽可能减少，完全避免有点难。

## 小结

这节课我们学习了如何部署6B。从模型的选择到环境配置再到模型启动、推理，整体来说已经比较全面了，如果你在实际操作的过程中遇到环境问题，可以自己Google一下尝试去解决。毕竟每个人的环境不一样，可能会遇到各种各样的问题，主要还是Python相关的多一些。如果这一节课有些内容你没有看懂也不用急，先把模型部署及推理这一块熟悉一下，后面我们会逐渐深入地讲解。

![图片](https://static001.geekbang.org/resource/image/e1/6e/e18c5ee37836cd26025a2b2ed60f546e.png?wh=2484x1390)

## 思考题

我们知道ChatGLM3-6B是一个具有62亿参数规模的大语言模型，那你知道大模型的参数是什么意思吗？62亿表示什么？欢迎你把你的观点分享到评论区，我们一起讨论，如果你觉得这节课的内容对你有帮助的话，也欢迎你分享给其他朋友，我们下节课再见！

[戳此加入课程交流群](https://jinshuju.net/f/D8y8pw)