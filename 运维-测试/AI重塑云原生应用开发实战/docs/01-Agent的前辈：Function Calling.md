你好，我是邢云阳。

自2023年3月 ChatGPT 在中国爆火以来，大模型已经悄然改变了许多人的提问方式，尤其是在互联网圈子里。从以前的“有问题，Google 一下”，到现在的“先问问大模型”，这种转变反映了技术对日常生活的深远影响，比如图中这位女士就将 ChatGPT 使用的淋漓尽致。

![](https://static001.geekbang.org/resource/image/d6/23/d608212c2ebb73c43ee94353f6021923.jpg?wh=968x961)

但是在使用过程中，我们会发现，有时大模型并不是万能的，它会一本正经的给出错误答案，业界把这种现象称之为“幻觉”。比如我问 ChatGPT-4o 一个它肯定不会的问题。

![图片](https://static001.geekbang.org/resource/image/12/ce/126d324784yy8bfb4d2ff9fc66475fce.png?wh=1221x505)

我们会发现，大模型给出了看似正确实则“废话”的答案。

再比如，我问一道小学一二年级的数学题：

![图片](https://static001.geekbang.org/resource/image/34/6e/342d4b45a41122d6868b5686d546586e.png?wh=1183x264)

我们很容易知道1+2+3+4-5-6=-1，但大模型给我们的答案是0。

“幻觉”出现的原因其实很简单。我们知道作为人类来说，即使是才高八斗，学富五车，也不可能什么都懂，于是就有这样一种人，为了面子，在遇到不会的问题时，也要强行给出一个模模糊糊的答案，我们称之为不懂装懂。

同样，作为大模型，训练数据是有限的，特别是对于一些垂直领域以及实时性的问题，例如附近哪有加油站？今天的茅台股票多少钱一股？大模型是无法给出正确的回答的。那大模型为什么也处理不了小学数学题呢？这是因为大模型的训练方法是通过学习语言的结构和模式，使得其能够生成与人类语言相似的文本，而不是针对数学问题这种精确逻辑做的训练，因此它的数学能力很弱。

我们应如何解决这类问题呢？OpenAI 公司为了能让大模型与外界进行交互，发明了 Function Calling 机制，即可以在向大模型提问时，给大模型提供一些工具（函数），由大模型根据需要，自行选择合适的工具，从而解决问题。

接下来，我将使用Go语言，为你演示一下 Function Calling 功能，我们就以加法减法工具为例，让大模型通过工具来进行数学运算。

## 代码实战前置工作

### 环境准备

- 运行环境：Windows/Linux
- Go版本：1.19
- LLM：阿里云 qwen-turbo
- SDK：go-openai v1.32.0

考虑到使用 OpenAI 的模型，需要科学上网，且购买 API 的调用额度，需要美国信用卡支付。因此我们选择国内模型作为替代演示。如果有同学想了解如何使用 OpenAI API ，可留言区留言评论，我们不在课程中展示。

### 通义千问大模型开通

阿里云通义千问提供了比较丰富的大模型产品供用户使用，且其请求方式是兼容 OpenAI SDK 的。本小节实战所使用的模型是通义千问中最便宜的 qwen-turbo 模型。如何开通服务，可参考官网教程 [开通DashScope并创建API-KEY\_模型服务灵积(DashScope)-阿里云帮助中心 (aliyun.com)](https://help.aliyun.com/zh/dashscope/opening-service?spm=a2c22.12281978.0.0.4d59588ebiflN0) 。

## 代码实战演示

### 模型环境变量配置

当我们获取了通义千问大模型的 api\_key 之后，为了保密和调用方便，可以将其配置到环境变量。

以 Windows 系统为例，我的电脑->右键属性->高级系统设置->环境变量，在系统变量中点击新建。

![图片](https://static001.geekbang.org/resource/image/94/89/94c2859904708be8205faba30011bc89.png?wh=1030x472)

输入变量名和 api\_key 的值即可。

接下来我们开始写初始化 OpenAI 客户端的代码。

首先将 go-openai sdk 下载下来。

```plain
go get github.com/sashabaranov/go-openai

```

之后，开始初始化一个 OpenAI 客户端，需要填充 token 和 baseurl 两项，用于客户端与大模型服务器的连接。

```go
func NewOpenAiClient() *openai.Client {
    token := os.Getenv("DashScope")
    dashscope_url := "https://dashscope.aliyuncs.com/compatible-mode/v1"
    config := openai.DefaultConfig(token)
    config.BaseURL = dashscope_url

    return openai.NewClientWithConfig(config)
}

```

由于通义千问大模型是兼容 OpenAI 的，因此可以使用 OpenAI SDK 初始化大模型客户端。使用 os 包从环境变量中获取 api\_key。

### Chat Completions

我们在演示工具选择之前，首先需要把和大模型对话的基础代码写好。这就要用到 Chat Completions。Chat Completions 是 OpenAI SDK 提供的一次性对话的方法，我们使用它可以完成和大模型的对话。

在与大模型的对话过程中，会有三种基础角色，用来让大模型清楚某句话是谁说的。

- system：系统角色，可以理解为全局变量或前置条件，设置上这个角色之后，就会规定大模型的聊天范围，业界通常称之为“人设”。

- user：人类角色，代表这句话是人类说的。在包括 LangChain 在内的很多框架和场景下，user 角色也会被写成 human。

- assistant：AI角色，代表这句话是大模型给我们的返回。在包括 LangChain 在内的很多框架和场景下，assistant 角色也会被写成 AI。


我举一个例子，演示一下使用以上三种角色完成一次 Chat Completions。

```plain
system: 你是一个足球领域的专家，请尽可能地帮我回答与足球相关的问题。
user: C罗是哪个国家的足球运动员？
assistant: 葡萄牙

```

如果想要实现多轮对话效果，则需要每一次都带着历史对话提问，例如：

```plain
system: 你是一个足球领域的专家，请尽可能地帮我回答与足球相关的问题。
user: C罗是哪个国家的足球运动员？
assistant: 葡萄牙
user: 内马尔呢？

```

虽然最后一次人类的提问“内马尔呢”是一个模糊提问，但由于存在历史对话，因此大模型可以理解用户的提问的意思是“内马尔是哪个国家的足球运动员？”

理解了三种角色后，我们开始写代码。

```go
func Chat(message []openai.ChatCompletionMessage) openai.ChatCompletionMessage {
    c := NewOpenAiClient()
    rsp, err := c.CreateChatCompletion(context.TODO(), openai.ChatCompletionRequest{
        Model:    "qwen-plus",
        Messages: message,
    })
    if err != nil {
        log.Println(err)
        return openai.ChatCompletionMessage{}
    }

    return rsp.Choices[0].Message
}

```

在这个函数中，首先我获取了 OpenAI 客户端，之后通过客户端调用了 CreateChatCompletion 方法。该方式是完成一次与大模型的 Chat。该方法的返回值 rsp，便是大模型的回复。

在这次 Chat Compleetion 中，我使用的模型是 qwen-plus，message 即向大模型发送的消息。message 的类型是一个 openai.ChatCompletionMessage 切片。

openai.ChatCompletionMessage包含了多个字段，其中有两个基础字段为：

```go
Role         string `json:"role"`
Content      string `json:"content"`

```

role 代表角色，content 代表对话内容。

openai.ChatCompletionMessage为切片类型，是因为考虑到会有历史消息，因此我们需要构建一个历史消息存储器来存储历史对话。核心代码如下：

```go
var MessageStore ChatMessages
type ChatMessages []openai.ChatCompletionMessage

func (cm *ChatMessages) AddFor(role string, msg string) {
    *cm = append(*cm, openai.ChatCompletionMessage{
        Role:    role,
        Content: msg,
    })
}

func (cm *ChatMessages) ToMessage() []openai.ChatCompletionMessage {
    ret := make([]openai.ChatCompletionMessage, len(*cm))
    for index, c := range *cm {
        ret[index] = c
    }
    return ret
}

```

在上述代码中，我们定义了历史消息存储器MessageStore，其本质是一个用于存放各类角色对话内容的 openai.ChatCompletionMessage 切片。并编写了 AddFor 方法，用于添加各类角色的对话内容，最后编写了 ToMessage 方法，用于取出存储器中的所有消息。

完成了以上编码后，我们可以测试一下和大模型对话的效果了。

```go
func main() {
    ai.MessageStore.AddFor(ai.RoleSystem, "你是一个足球领域的专家，请尽可能地帮我回答与足球相关的问题。")
    ai.MessageStore.AddFor(ai.RoleUser, "C罗是哪个国家的足球运动员？")
    ai.MessageStore.AddFor(ai.RoleAssistant, "C罗是葡萄牙足球运动员。")
    ai.MessageStore.AddFor(ai.RoleUser, "内马尔呢？")

    response := ai.Chat(ai.MessageStore.ToMessage())
    fmt.Println(response.Content)
}

```

输出：

```go
内马尔是巴西足球运动员。

```

在上面的例子中，大模型成功的根据对话历史，理解了“内马尔呢？”表达的真正含义。

### Function Calling

由于 Function Calling 功能是 OpenAI 公司发明的，因此我们定义工具需要遵循 OpenAI SDK 的规范。规范如下：

```go
const (
    ToolTypeFunction ToolType = "function"
)

type Tool struct {
    Type     ToolType            `json:"type"`
    Function *FunctionDefinition `json:"function,omitempty"`
}

type FunctionDefinition struct {
    Name        string `json:"name"`
    Description string `json:"description,omitempty"`
    Parameters any `json:"parameters"`
}

```

规范还是很简单的，包含了工具类型 Type 和工具定义 Function 两个部分，其实工具类型是写死的 “fuction”。工具定义包含名称 Name、描述 Description 以及参数 Parameters 三个部分。

接下来我来定义一个加法工具，给你做一下演示。

```go
var AddToolDefine = openai.Tool{
    Type: "function",
    Function: &openai.FunctionDefinition{
        Name: "AddTool",
        Description: `
        Use this tool for addition calculations.
            example:
                1+2 =?
            then Action Input is: 1,2
        `,
        Parameters: `{"type":"object","properties":{"numbers":{"type":"array","items":{"type":"integer"}}}}`,
    },
}

```

在我的工具定义的 Description 部分，我不仅写清楚了 AddTool 工具的作用，还举了一个例子，这样可以让大模型更好地理解。在Parameters部分，我使用了标准的 json schema 方式编写了参数名称、类型等，这样也有助于大模型准确理解。

在定义好工具后，我们需要在向大模型提问时，带上工具，因此 Chat Completions 增加了两个参数，一个是 Tools，用于接收 \[\]openai.tool 列表；另一个参数是ToolChoice，用于设置让大模型使用工具还是不使用工具，一般设置为 “auto”，意思是让大模型自己根据实际情况选择是否调用工具。修改后的 chat 函数代码如下：

```go
func ToolsChat(message []openai.ChatCompletionMessage, tools []openai.Tool) openai.ChatCompletionMessage {
    c := NewOpenAiClient()
    rsp, err := c.CreateChatCompletion(context.TODO(), openai.ChatCompletionRequest{
        Model:      "qwen-turbo",
        Messages:   message,
        Tools:      tools,
        ToolChoice: "auto",
    })
    if err != nil {
        log.Println(err)
        return openai.ChatCompletionMessage{}
    }

    return rsp.Choices[0].Message
}

```

有了这些基础，我们就可以向大模型提问，测试工具选择了。我们让大模型计算一下"1+2=?"

```go
func main() {
    toolsList := make([]openai.Tool, 0)
    toolsList = append(toolsList, tools.AddToolDefine, tools.SubToolDefine
)

    prompt := "1+2=? Just give me a number result"
    ai.MessageStore.AddFor(ai.RoleUser, prompt)

    response := ai.ToolsChat(ai.MessageStore.ToMessage(), toolsList)
    toolCall := response.ToolCalls

    fmt.Println("大模型的回复是: ", response.Content)
    fmt.Println("大模型选择的工具是: ", toolCalls)
}

```

输出：

```go
大模型的回复是:
大模型选择的工具是:  [{0xc000284520 call_f31f9091de504216a3a84d function {AddTool {"numbers": [1, 2]}}}]

```

可以看到大模型选择了工具 AddTool，并将参数按照我们的要求拆解成了 \[1, 2\] 这样一个切片。只要大模型选择了工具，则其回复就会是空字符串。

测试到这里，我们可以初步理解所谓大模型“调用”工具的机制。其实就是将工具用文字描述清楚，并和问题一起发送给大模型，由大模型判断选择哪个工具能解决问题。因此其实 Function Calling 这个表述我个人感觉并不准确，或许叫 Function Selecting 会更加没有歧义。

**这里我们可以得出两个结论：**

1. **工具的定义也是 prompt，也就是要消耗** **token** **的。**

2. **大模型只能选择使用工具！而不能调用工具！真正调用工具的仍然是人类！**


最后我们看一下，人类如何调用工具，并将结果反馈给大模型，从而辅助大模型完成任务。

OpenAI 的 SDK 文档给出了说明，经过我简化后，方法如下：

```json
#1. 将提问存储到MessageStore
{"role": "user", "content": "1+2=? Just give me a number result"}

#开始进行第一轮提问....
#得到大模型返回

#2. 将大模型的返回，存储到MessageStore
{"role": "assistant", "content": "", "tool_calls": [{0xc000284520 call_f31f9091de504216a3a84d function {AddTool {"numbers": [1, 2]}}}]
}

#3. 将工具调用信息，存储到MessageStore
{"role": "tool", "content": "3", "name": "AddTool", "tool_call_id": "call_f31f9091de504216a3a84d"}

#4. 开始进行第二轮提问，将上述所有Mesage，发送给大模型
#得到大模型返回

```

可以看到，相比正常的 user assistant 的多轮对话模式，Function Calling 的对话模式，只是略有不同，不同点在于第一要将大模型选择的工具添加到 assistant 对话中，第二是要在assistant 之后添加 tool 角色的消息，用于存储工具调用结果、工具名称以及 id。

理解了原理后，我们来看代码：

```go
if toolCalls != nil {
    var result int
    var args tools.InputArgs
    err := json.Unmarshal([]byte(toolCalls[0].Function.Arguments), &args)
    if err != nil {
        log.Fatalln("json unmarshal err: ", err.Error())
    }

    if toolCalls[0].Function.Name == tools.AddToolDefine.Function.Name {
        result = tools.AddTool(args.Numbers)
    } else if toolCalls[0].Function.Name == tools.SubToolDefine.Function.Name {
        result = tools.SubTool(args.Numbers)
    }

    fmt.Println("函数计算结果: ", result)
    ai.MessageStore.AddFor(ai.RoleAssistant, response.Content, toolCalls)
    ai.MessageStore.AddForTool(string(result), toolCalls[0].Function.Name, toolCalls[0].ID)

    response := ai.ToolsChat(ai.MessageStore.ToMessage(), toolsList)

    fmt.Println("大模型的最终回复: ", response.Content)
}

```

首先判断一下大模型有没有调用工具，如果调用了，则从 toolCalls\[0\].Function.Arguments 中解析出函数入参。之后根据工具名称，调用相应的工具函数。最后按照上文中 OpenAI 规定的格式，将对应的 assistant 以及 tool 消息填好，反馈给大模型。

输出：

```json
函数计算结果:  3
大模型的最终回复:  1 + 2 = 3

```

## 总结

本节课我在开篇用了两个小例子为你展示了大模型不是万能的，大模型也有自身的弱点以及无法解决的问题，让你体验了一下什么是业界常说的“幻觉”。

OpenAI 公司为了解决这些问题，想到了让大模型与外界环境交互的破解之法，因此提出了 Function Calling 机制，并在 SDK 中进行了支持，在迅速成为了行业标杆做法后，其他公司包括国内公司的大模型，也对该机制进行了兼容，因此我们可以使用 OpenAI SDK 配合阿里云的通义千问大模型体验该机制。

最后我用一个加法小例子，为你展示了 Function Calling 的代码应如何写，并介绍了其前置基础 Chat Completion。本节课的代码已公开在 GitHub 上，链接为： [Geek/function-calling at main · xingyunyang01/Geek (github.com)](https://github.com/xingyunyang01/Geek/tree/main/function-calling)

## 思考题

我在课程中的代码，为你演示了 “1+2=？” 这个小例子，如果是计算 “1+2+3+4-5-6=?” 呢？代码该如何编写？大模型能否给出正确的回答？

欢迎你在留言区展示你的思考过程，我们一起探讨。如果你觉得这节课的内容对你有帮助的话，也欢迎你分享给其他朋友，我们下节课再见！