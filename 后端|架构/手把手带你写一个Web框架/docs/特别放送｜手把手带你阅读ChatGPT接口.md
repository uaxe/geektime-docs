你好，我是轩脉刃。

好久不见，经过四、五月份GPT的信息轰炸，想必有些同学已经尝试调用过ChatGPT的接口了，今天我们也来聊聊这个话题。

我们大多数人使用ChatGPT，一般是直接使用网页版本的GPT对话框。但是实际上，OpenAI提供了ChatGPT开放平台的调用方式，这个方式，反而是我们目前碰到的各种应用中最常用的方式。

我们可以使用HTTP API的方式来调用ChatGPT。这节课我们就来详细解析一下，如何通过API来调用OpenAI的开放平台，并且通过理解API来解构下目前最火的AutoGPT的实现原理。

## 接口地址

首先我们明确下范围，OpenAI提供了非常多的模型，不同模型在开放平台可能有不同的调用方式，而OpenAI目前最流行的模型就是ChatGPT，专注于聊天对话的大模型。我们这里研究的接口，就是 **ChatGPT 提供的开放平台的接口**。

ChatGPT的接口是一个标准的HTTP请求，请求的URL为： `POST https://api.openai.com/v1/chat/completions`

官方的接口文档地址为： [https://platform.openai.com/docs/api-reference/chat/create](https://platform.openai.com/docs/api-reference/chat/create)

我们可以在这个文档中看到所有的参数说明和示例，不过官方文档虽然很权威，但却是非常简陋的。要将里面的每个参数理解透，并不是那么容易。这里我结合最近的研究，来手把手带你理解下ChatGPT的API接口的每个参数含义。

## 请求

### model

model参数代表请求接口要使用什么模型。这个模型仅限于GPT模型，目前OpenAI的GPT模型开放的只有GPT-4 和GPT-3.5。

在这里，model参数我们可以选择的有：

- gpt-4
- gpt-4-0314
- gpt-4-32k
- gpt-4-32k-0314
- gpt-3.5-turbo
- gpt-3.5-turbo-0301

首先我们理解下为什么有这么多种模型的分类呢？为什么不能只有GPT-4和GPT-3.5呢？

**每个模型分类代表了不同的AI算法和训练方法。** 这里的各种分类我们可以理解为Git的不同分支，OpenAI的工程师在不同时期尝试使用不同的方法和数据集来训练模型，以达到解决不同问题的目的。

- gpt-4 是 OpenAI 最新的大型多模态模型，可以接受图像和文本输入，输出文本。它在各种专业和学术的基准测试中表现出了人类水平的性能，例如在模拟律师考试中得分位于前 10%。
- 而gpt-4-0314 是 gpt-4 模型的一个快照，它是在 2023 年 3 月 14 日发布的。它与最新的 gpt-4 模型相比，可能存在一些差异和缺陷。
- gpt-4-32k 是 gpt-4 模型的一个扩展版本，它提供了 32,000 个 Token 的上下文长度，而标准的 gpt-4 模型只提供了 8,000 个 Token 的上下文长度。这意味着 gpt-4-32k 可以处理更长的输入和输出，适用于一些需要更多细节和信息的任务。
- gpt-3.5-turbo 是 OpenAI 在 2022 年发布的一个大型单模态模型，只接受文本输入，输出文本。它是在 GPT-3.5 的基础上进行了一些优化和改进，提高了性能和稳定性。

简要来说， **不同模型在相同问题上，会有不同表现，这种表现不仅仅是回答问题的不同，也包括反应速度、准确度等。** 由于不同的人会有不同的使用场景，所以OpenAI就干脆把所有模型分类都提供给大家，让大家按需选择。

这里再深入思考一个扩展知识点：Token是什么？Token上下文长度和大小有什么区别呢？

我们需要知道，每个文本都是由不同的单词组成，不同单词组合起来，就代表一个句子。而GPT模型在进行句子分析计算的时候，是以Token为最小单元，也就是计算机的“单词”。比如一句话“我是中国人”在计算机中是会被分成几个Token：我、是、中国、人。

而自然而然在一个对话中，我们的Token长度允许越长，我们就能传输越多的内容，提供越多的能力。且理论上回答一个问题需要的时间就会越长。

比如现在比较流行直接将一个PDF文件传输给GPT，让GPT总结PDF的内容。那么一个PDF的Token数就非常多，如果使用普通的gpt-4，可能就没有办法理解一个完整的PDF文件内容。这时候模型就需要选择gpt-4-32k。

理解了Token之后，我们再继续深入理解下另外一个问题： **OpenAI 的 GPT 中 Token 计算方式是什么样的？**

所谓计算Token，前面说了，就是计算机理解一个句子的最小单元。而这个最小单元，是根据某种编码存储在计算机中的。由于GPT是支持多语言模型的，而最好的多语言编码就是Unicode。所以这里的编码都是基于Unicode的。但是并不是简单的一个Unicode字符就是一个Token，而是OpenAI有一个自己定义的编码表，这个编码表对于不同模型是不一样的。但是对于ChatGPT，gpt4 和 gpt3.5-turbo 使用的都是一个叫 cl100k\_base 的编码表。

Token和我们实际支付给OpenAI的模型是息息相关的，我们在实际应用中，会非常关心 Token的使用数量和计算方式。关于ChatGPT实际的计算Token，有这样几种办法。

1. 官方提供的计算Token的 [网页](https://platform.openai.com/tokenizer)

输入任何语言的文字，网页都会解析出有哪些Token、有多少Token。我们可以通过这个网页很好地理解OpenAI是怎么分Token的。

2. 官方提供的计算Token的Python库： [TikToken](https://github.com/openai/tiktoken)

这个库是OpenAI官方发布的计算Token的方式。是的，虽然我们的编码表是一样的，但是如何将一个文章按照编码表拆分为一个个Token，是有不同的算法支持的，而TikToken，就是OpenAI官方披露的拆分Token的算法。

3 第三方开源库。官方的TikToken算法是Python支持的，而Golang的开源库也是有人自愿开源支持的。

- [https://github.com/tiktoken-go/tokenizer](https://github.com/tiktoken-go/tokenizer)
- [https://github.com/pkoukk/tiktoken-go](https://github.com/pkoukk/tiktoken-go)

从一个model参数我们就引申了模型分类、Token定义、Token计算等含义，我想强调的是，有这些概念，在实际应用中是非常非常重要的，选择哪个model参数其实就选择了model参数后面所包含的逻辑。

### message

message参数传递的是这个对话的内容。

这个message并不只是一个简单的文本，而描述的是一段对话。而且这个对话是分角色的。目前有三种角色：system、user、assistant。

- system表示其中的内容是系统设置，就是用于提示GPT的行为。比如，system：“你是一个作家”，就是对GPT模型的一种提示。
- user表示对话中用户的提问，是用户通过应用程序或者其他方式提出的一些问题或者要求。
- assistant表示ChatGPT的回答，它是GPT模型根据用户和系统的输入生成的一些回答或者反馈。

这里引申的一个思考点，你不妨想一想： **为什么 message 要定义这么复杂呢？我只是问一个问题而已。**

这里就有一个和我们平时认知不一样的点，ChatGPT的API接口和我们平时用的ChatGPT的网页是不一样的。在网页中，我们只需要在对话框中输入我们的问题。而我们在使用API调用的时候，必须在一个请求中把整个对话流程和内容都给到GPT。

我们提问的问题是需要有上下文才能更准确推理出回答的，ChatGPT的网页是帮我们存储了我们的上下文对话的，而ChatGPT的接口是不会帮我们保存上下文信息的。

那我们要让模型根据上下文信息回答我的最后一个问题怎么办呢？API每次请求都是一次完全独立的请求，我们只能把上下文的对话在message请求参数中全部传递过去。这个上下文对话自然就包括了用户提问的内容（user）以及机器人回答的内容（assistant）。

这样就能很好地理解user和assistant角色了吧。而system角色，其实用处更大，它是一种对模型的暗示和设置（prompt）。它的更多应用我们在后面的AutoGPT部分会做更详细的说明。

### temperature

temperature参数是用来控制返回答案的随机性的。它的值从0-2不等， **temperature 值越高表示回答的随机性越高，越低则表示回答越固定。**

理解起来很简单，但我们细细思考，其实这里也能引申出一个问题：为什么我们能调整ChatGPT回答的随机性呢？ChatGPT不是将最正确的答案返回回来么？

这里其实要从ChatGPT的回答机制说起，ChatGPT基于的GPT模型可以抽象为“单词接龙”，就是根据你说的上半句话（你的提问）GPT模型猜测下个单词（Token）是什么。再根据选择出来的下个单词，猜出下下个单词。最终组成你的下半句话。

比如我的问题是“我是一名诗人，我在写”，它去推测下一个单词是“诗”、还是“词”、还是“信”。

**这里的推辞实际上就是为可能的下个单词打上一个概率。** 但是每次GPT并不是将概率最高的返回给你，因为并不是每次选择概率最高的词，就能组成最正确的句子。

所以GPT模型是在一个概率范围内，随机地将可能的下个单词返回给你。

这也是为什么，在实际使用中，面对同样的问题，ChatGPT每次返回的回答都不一样。

回到这个temperature参数，实际上就是控制这个概率范围的，temperature 值越高，那么随机范围越大，回答的随机性就越高了。

### top\_p

这个top\_p也是用来控制最终答案的概率范围的。只是它的逻辑是按照最终答案的概率由高到低排列，选择概率大于p的词汇集合。这个参数的值在0和1之间。

举个例子，如果top\_p为0.9，则表示模型最终只在总概率为90%的词汇中间选择下一个词。

这里要注意，top\_p和temperature都是控制返回结果的概率范围。所以这两个一起调整的效果实际上是不可控的，官网强烈建议这两个参数只调整一个就好。

我们在实际项目中，一般调整的是 temperature 值。

### n

n代表的是对于问题，你希望返回多少个回答。比如n为5的时候，模型会针对你的问题生成5个独立的回答，这些回答互相没有关联，独立生成。

如果这个默认值是1，那就是默认ChatGPT只返回1个回答。

这里n设置大于1的场景其实不多，我们既然知道了GPT的单词接龙的原理，那么其实就不难知道，即使返回多于1个的回答，我们也很难判断哪个回答更好。

### stream

我们平时用的ChatGPT网页，都是打字机的效果，就是一个回答是一个字一个字往外面蹦的。这种返回就是设置stream为true的返回模型，即 **流式返回**。

当stream为true的时候，模型的回答是按照一个个chunk的方式返回的，每个chunk都是一个JSON结构，是这里的ChatCompletionStreamResponse数据结构。

```

type ChatCompletionStreamChoiceDelta struct {

	Content string `json:"content"`

}

type ChatCompletionStreamChoice struct {

	Index        int                             `json:"index"`

	Delta        ChatCompletionStreamChoiceDelta `json:"delta"`

	FinishReason string                          `json:"finish_reason"`

}

type ChatCompletionStreamResponse struct {

	ID      string                       `json:"id"`

	Object  string                       `json:"object"`

	Created int64                        `json:"created"`

	Model   string                       `json:"model"`

	Choices []ChatCompletionStreamChoice `json:"choices"`

}

```

里面最主要是一个String结构，Content。表示模型返回的内容。当这个Content为字符串 \[DONE\] 的时候，就代表当前的流式返回结构结束了。

这个流式返回很多人应该很陌生。我们一般用到的HTTP都是一个Request对应一个Response的请求结构，为什么会有HTTP是能流式返回呢？ **这里我们需要引申一下HTTP的 SSE 原理才能理解好 stream 这个参数。**

OpenAI API在流模式（stream）下使用了HTTP协议的一项特性“服务器发送事件”（Server-Sent Events，SSE）。在SSE中，客户端请求一次Request之后，服务器就可以发送一系列的消息到客户端，而后续无需客户端每次都去重新请求。在OpenAI的流模式下，服务器将逐个发送生成的文本块称之为chunks。

SSE技术是浏览器除了WebSocket之外的另外一项能使得服务端向客户端连续发送数据的方式。这种方式中，服务端和客户端都需要做少量额外支持。比如浏览器端需要使用EventSource的API来接收服务器发送的事件；服务端也需要能够保持长时间的HTTP连接，并能发送特定格式的数据。

但相较于WebSocket来说，SSE是更轻量级的选择。基本上所有的Web服务器都能支持，并且是沿用HTTP协议的，并不是像WebSocket一样有一个自己的独立协议，浏览器端和服务端都需要额外的很重的库才能解析。

**它一般会用于像实时聊天、监控系统、在线游戏等场景。** 而OpenAI这里选择使用SSE技术应该也是希望使用者使用ChatGPT的时候最简化。

比如，我们用curl就能实现这种SSE功能。

```

~ curl -X POST \

        -H "Accept: text/event-stream"  \

  -H "Authorization: Bearer  [api-key]" \

  -H "Content-Type: application/json" \

 -d '{

    "model": "gpt-3.5-turbo",

    "messages": [{"role": "user", "content": "你好，请问你是什么模型"}],

    "stream": true

  }' \

  [https://api.openai.com/v1/chat/completions](https://api.openai.com/v1/chat/completions)

```

可以看到上面的curl命令，主要是发送的header头中需要带一个Accept: text/event-stream的头。

它返回的结果就是：

```

data: {"id":"chatcmpl-7Ic9sSjdqv7JtEQrlXr9zx6UOL8Fl","object":"chat.completion.chunk","created":1684670940,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"role":"assistant"},"index":0,"finish_reason":null}]}

data: {"id":"chatcmpl-7Ic9sSjdqv7JtEQrlXr9zx6UOL8Fl","object":"chat.completion.chunk","created":1684670940,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"我"},"index":0,"finish_reason":null}]}

data: {"id":"chatcmpl-7Ic9sSjdqv7JtEQrlXr9zx6UOL8Fl","object":"chat.completion.chunk","created":1684670940,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"是"},"index":0,"finish_reason":null}]}

...

data: {"id":"chatcmpl-7Ic9sSjdqv7JtEQrlXr9zx6UOL8Fl","object":"chat.completion.chunk","created":1684670940,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"。"},"index":0,"finish_reason":null}]}

data: {"id":"chatcmpl-7Ic9sSjdqv7JtEQrlXr9zx6UOL8Fl","object":"chat.completion.chunk","created":1684670940,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}

data: [DONE]

```

我们提问的句子是：你好，请问你是什么模型？

返回的句子是：我是OpenAI GPT-3 自然语言生成模型。一个基于人工智能的语言生成技术。

只是这个句子是一个（或者几个）字（Token）一个字往外面蹦出来的。

### stop

stop参数是可选的，它表示在生成文本时用于指示模型停止生成的符号或字符串。比如我们设置stop为中文句号“。”，上面的对话语句就会变成这样。

我们提问的句子是：你好，请问你是什么模型？

返回的句子是：我是OpenAI GPT-3 自然语言生成模型。

这个stop参数可以帮助你得到更符合你预期的输出。

那什么是更符合你预期的输出呢？stop参数在哪些场景会有作用呢？

比如你在生成一个对话过程中，使用stop为Bye 或者GoodBye。这样会让整个对话一定在Bye这个词语结束，会更口语化。

### max\_tokens

这个字段的意思就是字面意思，限制Token的长度。前面已经说了，Token的使用量代表费用，所以我们使用OpenAI的API的优化目标就是用最小的Token能获取到最正确的回复。

我们的问题是有请求和返回两个方面的。这个max\_tokens限制的是 **模型返回的回复的长度**。

这个参数的使用场景也非常重要。比如你是要使用OpenAI来回复某个评论，那么平台的评论一般有字数限制，所以你需要设置这个max\_tokens以保证回复的字数满足平台限制。

max\_tokens的最大限制一定不能超过模型本身的限制。GPT-3.5的限制是4096个tokens，GPT-4的最大tokens数为32768，即2^15，这相当于大约64000个单词或50页的文字。所以对于不同的model参数，我们这里设置的max\_token最大值也是有不同的，这点需要注意下。

### presence\_penalty

presence\_penalty参数用来影响模型生成文本的方式。具体来说，它影响了模型生成新话题或概念的倾向性。这对于控制模型生成的文本的连贯性和主题一致性来说是重要的。

presence\_penalty的值可以是从-2到2的任意数值。较高的值会鼓励模型避免引入新的话题或概念，而较低的值则会让模型更有可能引入新的话题或概念。也就是说，如果你希望模型生成的文本尽可能地聚焦在一种或者少数几种主题上，你可能会设置较高的presence\_penalty值。反之，如果你希望模型能够广泛地涉及多种主题，你可能会设置较低的presence\_penalty值。

这个值默认值为0。中立值，表示没有做任何限制，会适当地引入新主题。

**这个参数有什么具体的使用场景呢？**

比如你是使用ChatGPT来创作一篇文章，你自身的问题并没有多少确定性，比如“如何赚取100万”这种发散性问题，那么你就需要适当调低这个参数，让模型有更多的发挥和发散能力。最终让你生成的文章有更多的创造性。

### frequency\_penalty

frequency\_penalty参数是用于控制模型在生成文本时对常见词汇的偏好程度。值是-2到2的任意数值。

如果设置为高的值，模型会更倾向于避免选择常见的词汇，这就代表模型的回答在网络上的重复度就越低，感觉就会有更高的原创性。

### logit\_bias

logit\_bias参数允许你为模型输出的特定令牌（Token）应用一个偏差。这可以帮助你引导或限制模型的行为。

这个参数接受一个字典作为输入，字典的键是令牌的ID（在英语中，一个令牌可能是一个字、一个单词或一个字符），字典的值是应用到该令牌的偏差值。 **正值增加了该令牌被选中的可能性，负值减少了它的可能性。**

例如，如果你不希望模型生成某个特定的单词，你可以对该单词的令牌ID应用一个大的负偏差。相反，如果你希望鼓励模型生成某个单词，你可以对该单词的令牌ID应用一个正偏差。

这个参数其实在安全方面是很有用的，比如我们可以使用logit\_bias为不适当的单词设置一个大的负偏差，从而减少模型生成这个单词的可能性。我们的回答就会安全很多。

### user

OpenAI API中的user参数用于识别发出请求的最终用户。这在需要追踪或将生成的内容与特定用户关联的应用程序中经常被使用。

因为我们的API-KEY是一个应用，而一个应用一般都服务于很多用户，那么这个user就是将某个特定用户的用户名指定上，这样能提供给 ChatGPT “哪个用户问了哪些问题”的线索。

这使得OpenAI在检测到应用程序有任何违反政策的行为时，可以向你的团队提供更多可操作的反馈。

## 返回

ChatGPT的API返回值在官方文档中描述得非常少。

它返回一般有以下两种形式。

### 非stream形式返回

```

{

    "id": "chatcmpl-7IdPv75cxkG3BG1TroGtabUAi0eDx",

    "object": "chat.completion",

    "created": 1684675779,

    "model": "gpt-3.5-turbo-0301",

    "usage": {

        "prompt_tokens": 19,

        "completion_tokens": 22,

        "total_tokens": 41

    },

    "choices": [

        {

            "message": {

                "role": "assistant",

                "content": "我是一个AI语言模型，被称为GPT（Generative Pretrained Transformer）。"

            },

            "finish_reason": "stop",

            "index": 0

        }

    ]

}

```

这个是非stream形式返回的结构，里面的choices就代表一个返回值。它由message结构组成。

这里其实我们是需要关注下usage这个结构的。因为我们很有可能要自己记录下Token的使用量，最后对账使用。

这里的usage将我们请求的Token、返回的Token、总共使用的Token都返回给我们了。

### stream形式返回

stream形式的返回如下：

```

data: {"id":"chatcmpl-7IcH13bsFJrjkhBcCJiczZ2523bZ3","object":"chat.completion.chunk","created":1684671383,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"role":"assistant"},"index":0,"finish_reason":null}]}

data: {"id":"chatcmpl-7IcH13bsFJrjkhBcCJiczZ2523bZ3","object":"chat.completion.chunk","created":1684671383,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"我"},"index":0,"finish_reason":null}]}

data: {"id":"chatcmpl-7IcH13bsFJrjkhBcCJiczZ2523bZ3","object":"chat.completion.chunk","created":1684671383,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}

data: [DONE]

```

**以上四条我们可以看下，都是 stream 模式返回的，但却有一些不同。**

首先我们观察到，和非stream模式不一样的是，stream模式返回的choices里面带内容的字段叫做delta，而非message。这也是OpenAI区分stream和非stream模式，避免用户使用相同字段解析的意义。

其次我们看到，第一条，返回的delta中是指定 `role：“assistant”` 表示后面的内容都是AI回复的，第一条并没有返回任何实际的内容数据。

而第二条，delta中的内容是放在content中，这个就是正常的内容返回。

而第三条，delta中是没有内容的，而finish\_reason中有个 “stop” 字段，表示这是一个结束的标记位。

最后一条，data中只返回了 \[DONE\] 字样，这个是告诉调用，这个请求结束了。

这里有同学可能就会问了， **finish\_reason 中的 stop 字段和 \[DONE\] 字段功能不是重复了么？**

其实不是的，这里我们回头思考下请求参数中的n这个属性，它代表需要模型返回几个回答。

如果n=2，那么这个模型就会返回2个回答，并且他们的index字段分别是0和1，这个时候就有在stream模式下这两个回答并不是同时结束的问题。

OpenAI的回复中，index=0且finish\_reason=stop就代表第1个回答结束，index=1且finish\_reason=stop就代表第二个回答结束。而 \[DONE\] 则是代表整个问题的回答都结束了。所以finish\_reason的stop字段和 \[DONE\] 字段并不重复，各自有各自的用途。

这个返回值，特别是stream还是有点复杂的。对于理解这个返回值，并且正确解析其实也是有一定工作量的。

所幸开源界其实都有了现成的解决方案。这里介绍一个： [https://github.com/sashabaranov/go-openai](https://github.com/sashabaranov/go-openai)

这个就是Golang的一个用得最广的ChatGPT的调用API的封装包。

它已经将请求和返回结构都封装得非常易用了，我们只需要简单引入并且调用即可。

```

package main

import (

	"context"

	"errors"

	"fmt"

	"io"

	openai "github.com/sashabaranov/go-openai"

)

func main() {

	c := openai.NewClient("your token")

	ctx := context.Background()

	req := openai.ChatCompletionRequest{

		Model:     openai.GPT3Dot5Turbo,

		MaxTokens: 20,

		Messages: []openai.ChatCompletionMessage{

			{

				Role:    openai.ChatMessageRoleUser,

				Content: "Lorem ipsum",

			},

		},

		Stream: true,

	}

	stream, err := c.CreateChatCompletionStream(ctx, req)

	if err != nil {

		fmt.Printf("ChatCompletionStream error: %v\n", err)

		return

	}

	defer stream.Close()

	fmt.Printf("Stream response: ")

	for {

		response, err := stream.Recv()

		if errors.Is(err, io.EOF) {

			fmt.Println("\nStream finished")

			return

		}

		if err != nil {

			fmt.Printf("\nStream error: %v\n", err)

			return

		}

		fmt.Printf(response.Choices[0].Delta.Content)

	}

}

```

上面就是这个库官网调用的例子，这里如果你理解了这节课描述的所有参数的含义，那么自然就能理解到代码的含义。

- 使用openai.ChatCompletionRequest封装了请求参数。
- 请求参数中的Stream: true表示是流式调用，且c.CreateChatCompletionStream函数也是流式调用的函数方法。
- 使用stream.Recv()来回收一个个的流式返回数据。
- 使用errors.Is(err, io.EOF) 来代表流式调用结束。
- 使用response.Choices\[0\].Delta.Content来代表流式调用的返回内容。

## AutoGPT的实现思路

现在，我们已经理解了ChatGPT API的每个细节，其实这就是我们和ChatGPT模型交互的全部内容了。但是即使我们知道了如何与模型进行交互，每个人使用模型的能力却还是天差地别，为什么呢？原因就在于我们请求参数的设置能力不同，这里给你展示一下使用请求参数最极致的用法——AutoGPT。

前面我们说到，请求参数中的messages参数有三个角色：system、user、assistant。

其中说到system这个角色，就是为机器人预设一些设置项，引导ChatGPT模型按照这些设置项进行回答。这个预设的设置项，就是叫prompt。

这个prompt可以有哪些内容呢？

- 可以让GPT模型有一些预设身份，比如是程序员，比如名字叫做Nick，比如是在大数据模型中有专业的推理能力。
- 可以让GPT模型有一个目标，比如这个模型的目标是帮助用户提升英语知识。
- 可以让GPT模型有一些约束条件，比如不需要依赖用户的反复输入做帮助，不允许反问用户。
- 可以让GPT模型预设一些命令（Command），这个命令比如说“打开文件”命令为read\_file，命令参数为file。
- 可以让GPT模型限定返回的内容长度。
- 可以让GPT模型限定依赖一些外部资源，比如MySQL数据库、互联网资源。
- 可以让GPT模型返回JSON结构而不是纯文本。
- 可以让GPT模型返回的JSON结构具有某些特定结构，比如带有thoughts字段、带有command字段。
- 可以让GPT模型有更好的工作调优能力，即可以自检查。

是不是强大到匪夷所思。实际上，目前最火的AutoGPT项目就是在prompt上设置了以上的内容，来完成AI的自主化（autonomous）。并且AutoGPT把以上的每个prompt的内容全部都工程化，就是每个内容都有一段工程代码根据用户输入来输出。

我们来看一个具体的AutoGPT的prompt例子：

```

You are Story-GPT, an AI designed to autonomously write stories.

Your decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies with no legal complications.

GOALS:

1. write a short story about flowers

Constraints:

1. 4000 word limit for short term memory. Your short term memory is short, so immediately save important information to files.

2. If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.

3. No user assistance

4. Exclusively use the commands listed in double quotes e.g. "command name"

Commands:

1. Google Search: "google", args: "input": "<search>"

2. Browse Website: "browse_website", args: "url": "<url>", "question": "<what_you_want_to_find_on_website>"

3. Start GPT Agent: "start_agent", args: "name": "<name>", "task": "<short_task_desc>", "prompt": "<prompt>"

4. Message GPT Agent: "message_agent", args: "key": "<key>", "message": "<message>"

5. List GPT Agents: "list_agents", args:

6. Delete GPT Agent: "delete_agent", args: "key": "<key>"

7. Clone Repository: "clone_repository", args: "repository_url": "<url>", "clone_path": "<directory>"

8. Write to file: "write_to_file", args: "file": "<file>", "text": "<text>"

9. Read file: "read_file", args: "file": "<file>"

10. Append to file: "append_to_file", args: "file": "<file>", "text": "<text>"

11. Delete file: "delete_file", args: "file": "<file>"

12. Search Files: "search_files", args: "directory": "<directory>"

13. Evaluate Code: "evaluate_code", args: "code": "<full_code_string>"

14. Get Improved Code: "improve_code", args: "suggestions": "<list_of_suggestions>", "code": "<full_code_string>"

15. Write Tests: "write_tests", args: "code": "<full_code_string>", "focus": "<list_of_focus_areas>"

16. Execute Python File: "execute_python_file", args: "file": "<file>"

17. Generate Image: "generate_image", args: "prompt": "<prompt>"

18. Send Tweet: "send_tweet", args: "text": "<text>"

19. Do Nothing: "do_nothing", args:

20. Task Complete (Shutdown): "task_complete", args: "reason": "<reason>"

Resources:

1. Internet access for searches and information gathering.

2. Long Term memory management.

3. GPT-3.5 powered Agents for delegation of simple tasks.

4. File output.

Performance Evaluation:

1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.

2. Constructively self-criticize your big-picture behavior constantly.

3. Reflect on past decisions and strategies to refine your approach.

4. Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.

You should only respond in JSON format as described below

Response Format:

{

    "thoughts": {

        "text": "thought",

        "reasoning": "reasoning",

        "plan": "- short bulleted\n- list that conveys\n- long-term plan",

        "criticism": "constructive self-criticism",

        "speak": "thoughts summary to say to user",

    },

    "command": {"name": "command name", "args": {"arg name": "value"}},

}

Ensure the response can be parsed by Python json.loads

```

由于ChatGPT模型是英文的，所以在实际设置中最好使用英文设置prompt，另外英文作为prompt也会比中文少很多Token数。

但是在这里为了易于理解，我们还是将prompt翻译为中文。

```

你是Story-GPT，一个被设计用来自主编写故事的人工智能。

你的决定必须始终是独立作出的，不需要寻求用户的帮助。发挥你作为法律硕士的优势，追求简单的策略，没有法律上的复杂问题。

目标：

1.写一个关于花的小故事

制约因素：

1.短期记忆的4000字限制。你的短时记忆很短，所以要立即将重要信息保存到文件中。

2.如果你不确定你以前是怎么做的，或者想回忆过去的事件，思考类似的事件会帮助你记忆。

3.没有用户协助。

4.只使用双引号中列出的命令，例如“命令名称”。

命令：

1.谷歌搜索："google", args: "input"："<搜索>"

2.浏览网站："browse_website", args: "url"："<url>", "问题"："<what_you_want_to_find_on_website>"

3.启动GPT代理："start_agent", args: "name"："<名称>", "任务"："<short_task_desc>", "提示"："<prompt>"

4.消息GPT代理："message_agent", args: "key"："<key>", "message"："<message>"

5.列出GPT代理："list_agents", args：

6.删除GPT代理："delete_agent", args: "key"："<key>"

7.Clone Repository："clone_repository", args: "repository_url"："<url>", "clone_path"："<directory>"

8.写入文件："write_to_file", args: "file"："<文件>", "文本"："<文本>"

9.读取文件："read_file", args: "file"："<文件>"

10.追加到文件："append_to_file", args: "file"："<文件>", "文本"："<文本>"

11.删除文件："delete_file", args: "file"："<文件>"

12.搜索文件："search_files", args: "directory"："<目录>"

13.评估代码："evaluate_code", args: "code"："<full_code_string>"

14.获得改进的代码："improve_code", args: "建议"："<list_of_suggestions>", "code"："<full_code_string>"

15.写测试："write_tests", args: "code"："<full_code_string>", "focus"："<list_of_focus_areas>"

16.执行Python文件："execute_python_file", args: "file"："<文件>"

17.生成图像："generate_image", args: "prompt"："<prompt>"

18.发送Twitter："send_tweet", args: "text"："<文本>"

19.什么都不做: "do_nothing", args：

20.任务完成（关闭）："task_complete", args: "reason"："<原因>"

资源：

1.用于搜索和收集信息的互联网接入。

2.长期记忆管理。

3.GPT-3.5驱动的代理，用于委托简单任务。

4.文件输出。

性能评估：

1.不断审查和分析你的行动，以确保你的表现是最好的。

2.不断对自己的大局观进行建设性的自我批评。

3.对过去的决定和策略进行反思，以完善你的方法。

4.每个命令都有成本，所以要聪明和高效。争取用最少的步骤完成任务。

你应该只以JSON格式响应，如下所述。

响应格式：

{

"想法"：{

"文本"："思想"、

"推理"："推理"、

"计划"："--简短的bulleted/n- list that conveys/n- long plan"、

"批评"："建设性的自我批评"、

"说话"："对用户说的思想总结"、

},

"命令"：{"名称"："命令名称", "参数"：{"参数名"："值"}、

}

```

我们解析下这个prompt到底提示了模型什么内容？

- 提示模型是一个Story-GPT，专门写故事的GPT。
- 提示模型写出来的故事没有法律风险，能避开一些违法行为和提示。
- 提示模型的目标是写一个关于花的故事。
- 提示模型不需要用户协助，就是强调模型是可以自己处理问题，不要有反问等行为。
- 提示模型单次内容为4000字限制，并且将单次内容保存为文本。
- 定义了一些模型可以使用的命令和参数。
- 定义了模型可以使用的资源。
- 暗示了模型能自我优化，并且用最少的步骤完成任务。
- 定义了模型返回的结构。

这就是AutoGPT交互的某次prompt，包含的内容是有非常多的。而这次交互返回的结果是一个JSON，这个JSON中定义了我要实现这个目标、要完成的步骤以及可能要依赖的命令。

如下：

```

{

    "thoughts": {

        "text": "I need to write a short story about flowers.",

        "reasoning": "This is the task I was given by the user. I assume they want a creative and original story that is engaging and coherent.",

        "plan": "- Research different types of flowers and their meanings\n- Generate some possible story ideas based on flowers\n- Choose the best one and outline the plot, characters, and setting\n- Write the first draft of the story and save it to a file\n- Review and edit the story for grammar, style, and logic\n- Generate an image for the story cover and save it to a file\n- Send the story and the image to the user via tweet",

        "criticism": "I should be careful not to plagiarize or copy any existing stories about flowers. I should also avoid clichés and stereotypes. I should try to make the story interesting and original, but not too complex or confusing.",

        "speak": "I am going to write a short story about flowers. I will research, generate, write, and edit the story, and then send it to you."

    },

    "command": {"name": "google", "args": {"input": "types of flowers and their meanings"}}

}

```

同样为了方便理解，我们翻译一下。

```

{

"思想"：{

"文本"："我需要写一个关于花的小故事。"、

"推理"："这是用户给我的任务。我假设他们想要一个有创意的、原创的、吸引人的、连贯的故事。"、

"计划"："- 研究不同类型的花和它们的含义/n

		- 根据花产生一些可能的故事想法/n

		- 选择最好的一个并概述情节、人物和设置/n

		- 写出故事的初稿并保存到一个文件/n

		- 审查和编辑故事的语法、风格和逻辑/n

		- 为故事封面产生一个图像并保存到一个文件/n

		- 通过推特将故事和图像发给用户"、

"批评"："我应该注意不要剽窃或抄袭任何关于花的现有故事。我还应该避免陈词滥调和定型观念。我应该尽量使故事有趣和新颖，但不要太复杂或令人困惑。"、

"讲"："我将写一个关于花的短篇故事。我将研究、生成、撰写和编辑这个故事，然后将其发送给你。"

},

"命令"：{"name"："google", "args"：{"输入"："花的类型和它们的含义"}}

}

```

这里主要看到返回的“计划”，要写一个花的故事，返回了以下7个计划步骤：

- 研究不同类型的花和它们的含义。
- 根据花产生一些可能的故事想法。
- 选择最好的一个并概述情节、人物和设置。
- 写出故事的初稿并保存到一个文件。
- 审查和编辑故事的语法、风格和逻辑。
- 为故事封面产生一个图像并保存到一个文件。
- 通过推特将故事和图像发给用户。

并且给出了第一个步骤的命令，Google搜索“花的类型和他们的含义”。

那么接下来，AutoGPT会执行预设的Google搜索命令。然后再将后续的步骤作为prompt输入来进一步解析，进行命令迭代。

而我们这里应该非常明确，所谓的命令迭代prompt推理，本质上就是一次ChatGPT的API接口调用。

如此循环调用ChatGPT的API接口，并且结合项目自带的命令，最终我们就能写出这篇关于花的故事了。

而这，就是AutoGPT的原理： **prompt 的工程化 + GPT 自迭代**。

当然，AutoGPT的细节是非常多的，我们这里只是粗略地描述了下它的原理。更多的细节是需要看AutoGPT的源码的，你可以去研究研究。

## 总结

这节课我们详细阅读了OpenAI提供的ChatGPT的API接口，对请求的每个参数的作用、使用场景都做了分析和解释，并且对API接口的返回也做了解读和分析。

最后我们基于对API的理解，分析了目前最火的AutoGPT的基本原理。希望能让你体会到AutoGPT其实并没有那么神秘，只是对ChatGPT的API的一种极致应用而已。

AI的浪潮已经到来，每个人都需要有AI的相关技能，并且能熟练使用这个技能来改变自己的工作和生活，否则就会被这个浪潮所淘汰。希望这个分享对于处于浪潮之中的你，能有所帮助。

## 参考资料

- [https://zhuanlan.zhihu.com/p/617746745](https://zhuanlan.zhihu.com/p/617746745)
- [https://github.com/openai/openai-cookbook/blob/main/examples/How\_to\_count\_tokens\_with\_tiktoken.ipynb](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- [https://zhuanlan.zhihu.com/p/592399697](https://zhuanlan.zhihu.com/p/592399697)
- [https://github.com/easychen/openai-gpt-dev-notes-for-cn-developer](https://github.com/easychen/openai-gpt-dev-notes-for-cn-developer)
- [https://www.ruanyifeng.com/blog/2017/05/server-sent\_events.html](https://www.ruanyifeng.com/blog/2017/05/server-sent_events.html)
- [https://juejin.cn/post/7231362257337368631](https://juejin.cn/post/7231362257337368631)
- [https://community.openai.com/t/dissecting-auto-gpts-prompt/163892](https://community.openai.com/t/dissecting-auto-gpts-prompt/163892)