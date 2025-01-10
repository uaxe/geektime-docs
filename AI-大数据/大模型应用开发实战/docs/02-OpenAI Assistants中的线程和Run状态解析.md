你好，我是黄佳，欢迎来到启程篇的第二节课。

在上节课中，我们介绍了如何使用OpenAI的Playground创建一个Assistant，并通过Python程序检索并调用它完成一个简单的订单总价计算任务。今天，我们将继续深入探讨OpenAI Assistant中两个重要的概念：Thread（线程）和Run（运行），以及它们的生命周期和各种状态。

OpenAI Assistants的技术架构中总共有4个值得一提的对象，分别是：Assistant、Thread、Run和Message，其基本操作步骤如下：

![](https://static001.geekbang.org/resource/image/28/bf/2801d4e3c087093fe6da67a0b12ba3bf.jpg?wh=1417x927)

这些对象中，Assisant和Message不言自明，无须解释。那么，如何理解Thread和Run呢？

## 究竟什么是 Thread 和 Run?

在OpenAI Assistant的设计中，Thread代表了Assistant和用户之间的一次完整对话会话。它存储了Assistant和用户之间来回的Messages（消息），并自动处理上下文截断，以适应模型的上下文长度限制。

其实这就像是你在网页上和ChatGPT等任何语言模型的一个 **聊天页面**，这个会话过程中，背后的Thread帮你记住之前的聊天上下文，并且在你输入的信息过长时会提醒你。

而Run则表示在一个Thread上调用Assistant的过程。Assistant会根据其配置以及Thread中的Messages，通过调用模型和工具来执行任务。在Run的过程中，Assistant也会向Thread中添加新的Messages。

其实这就像是你在网页上和ChatGPT等任何语言模型的一次 **互动过程**。

### Assistant、Thread 和 Run 的交互过程

Assistant、Thread和Run这三个核心概念之间的关系和交互过程如下图所示。

![](https://static001.geekbang.org/resource/image/1d/fa/1db9eb555b2665a4d6ab8141ae254efa.jpg?wh=1360x453)

在这个示例中，一个名为 “Personal finance bot” 的Assistant被配置用于提供退休规划方面的建议。当用户向这个Assistant发送一条消息 “How much should I contribute to my retirement plan?” 时，就会创建一个新的Thread，用于处理这个关于退休规划的对话。

为了回答用户的问题，系统会在这个Thread上启动一个新的Run。在Run的执行过程中，Assistant分两步生成回复：

- 首先，使用代码解释器（code interpreter）工具计算出一个建议的缴费金额。
- 然后，基于计算结果生成一条回复消息，例如 “You should contribute $478 per year…”。

最后，Assistant生成的回复消息会添加到Thread中，发送给用户。

这样，Assistant、Thread和Run，以及Message协同工作，共同完成一次 **人机对话**。

此外，请你注意，在上一课中，我们创建线程的时候并没有指明助手的ID，因此，可以认为OpenAI 的线程和助手是彼此独立的。在OpenAI 的 API 设计中，创建和管理线程来维持一个连贯的对话流程，而助手则是在这些线程中提供回答和交互的实体。助手负责处理具体的请求，而线程则更多关注于对话的组织和管理。

也就是说，一个线程中可以有多个助手；同时，一个助手可以有多个线程。 **这种设计增加了系统的灵活性和应用场景的广度。** 比如在一个复杂的对话系统中，不同的助手可能专注于处理不同类型的任务或问题。例如，一个助手可能专门处理与天气相关的查询，而另一个助手则处理旅游建议。在同一个对话线程中，根据用户的不同问题，系统可以将请求路由到不同的助手进行处理。

### Thread 的上下文和生命周期管理

创建Thread时，可以指定一组初始的Messages。之后我们可以不断地向Thread中添加新的Messages，这代表用户与Assistant的持续对话。

值得注意的是，Thread会自动管理上下文窗口，以确保它不超过模型的上下文长度限制。当Thread中Messages的总长度超过模型的上下文窗口时，Thread会在其内部用GPT模型对上下文做总结，并尝试尽可能多地包含最新的Messages，而丢弃最早的Messages。

线程创建之后，就会一直在那里等待你的消息，并和你对话。你此时可能会有疑问，如果我们创建了一系列重复的空的新线程，如何删除它呢？线程什么时候停止呢? 它会一直等着我来访问么？它过一段时间之后会不会自动消亡呢？

其实，旧的线程可以通过 API client.beta.threads.delete(thread\_id) 来清理，不过，前提是你必须要知道线程的ID。

对于 assistants、run和message，你都可以通过list API来获取你所创建的所有对象的列表。

- client.beta.assistants.list
- client.beta.threads.runs.list
- client.beta.threads.messages.list

但是你会发现，OpenAI目前并 **没有** 为我们提供线程的列表API。因此，当你没有记录下之前创建的线程，你就没有办法删除它。

我发现有人在论坛上提出了是否可以通过API列出当前的线程，以便管理。

![图片](https://static001.geekbang.org/resource/image/2f/21/2fe97dafe6445ab2cc58ffbbf6e1de21.png?wh=944x416)

OpenAI的开发团队表示他们了解这一需求，说Playground中最初是有这个功能的，但是由于担心线程会对组织内的任何人开放（考虑到大型企业对OpenAI访问权限设置较为宽松），所以他们移除了这一功能。这个问题已经被记录为一个待处理事项，团队希望在未来几周内能够分享更多信息。同时，他们建议不要使用尚未公开的端点（endpoints，也就是提问者提到的获取线程列表的API功能）。

当我发现自己重复创建了很多线程的时候，也在OpenAI的论坛中发了一个帖子，询问当我删除自己创建的助手时（可以在Playground或者用API删除Assistants），这些线程会不会跟着被清理掉。很快就得到了论坛leader的回复。但是他也不是100%肯定（其实现在想想，我觉得答案是No，因为Thread和Assistant是彼此独立存在的）。根据他的回答，60天后没有动静的线程，会被系统自动清理掉。

![图片](https://static001.geekbang.org/resource/image/41/99/415b8a82eb75c32c8fa4f376c1349999.png?wh=944x535)

虽然创建了线程，但是没有Token的传输，应该不会产生费用的。所以，要删光你的活动线程似乎并不容易，暂时就这样吧，不要强迫症了。我想，开着的线程应该不会浪费过多资源吧，只要你没有循环地频繁在线程中发送和接收消息就好。

## Run 的生命周期和状态

当我们在一个Thread上创建一个新的Run时，Assistant就开始根据Thread中的上下文Messages来执行任务。在这个过程中，Run会经历下图所示的多个状态。

![](https://static001.geekbang.org/resource/image/a4/59/a4f3734bdf5fa2acbdbc3909472c1659.jpg?wh=1360x453)

对于这些状态，我列表解释如下。

![](https://static001.geekbang.org/resource/image/a6/ea/a6671862c0b39a58185f192006d91eea.jpg?wh=1675x1954)

在Run创建后，也就是Thread开始运行对话交互之后，为了及时获取Run的最新状态，我们需要定期检索Run对象，以观察Run的状态变化。每次检索时，可以通过查看Run的status字段来确定应用程序接下来应该执行的操作。

## 通过实战分析 Run 的状态流转

好了，有了上面的理论做基础，我们现在就可以开始分析上一讲中，我们的Run究竟经历了那些状态，从出生到消亡，它的状态是怎样流转的。

### 最简单的状态流转

我们先来看一个最简单的状态变化的情况。此处的示例仍然调用上一节课中创建的同一个Assistant，但是，问题比较简单，Assistant能够智能的发现，不需要进行Function Call，因此会直接回答。

简单调用Assistant的程序代码如下：

```plain
# 导入OpenAI库,并创建OpenAI客户端
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

client = OpenAI()

# 检索您之前创建的Assistant
assistant_id = "asst_aT4hurwd35eSave7qrt2t6eJ"  # 你自己的助手ID
assistant = client.beta.assistants.retrieve(assistant_id)
print(assistant)

# 创建一个新的Thread
thread = client.beta.threads.create()
print(thread)

# 向Thread添加用户的消息
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="你好,请问你能做什么。"
)
print(message)

# 运行Assistant来处理Thread
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)
print("读取Run的状态", run)

import time
# 定义一个轮询的函数
def poll_run_status(client, thread_id, run_id, interval=10):
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Run的轮询信息:\n{run}\n")
        if run.status in ['requires_action', 'completed']:
            return run
        time.sleep(interval)  # 等待后再次检查

# 轮询以检查Run的状态
run = poll_run_status(client, thread.id, run.id)

# 获取Assistant在Thread中的回应
messages = client.beta.threads.messages.list(
    thread_id=thread.id
)
print("全部的message", messages)

# 输出Assistant的最终回应
print('下面打印最终的Assistant回应:')
for message in messages.data:
    if message.role == "assistant":
        print(f"{message.content}\n")

```

在这里，我们定义了poll\_run\_status 函数，用来轮询检查 Assistant 在处理 Thread 过程中的状态，并定期输出当前Run的状态。这个函数的主要作用是在调用 Assistant 处理 Thread 后，持续检查 Assistant 处理的状态，直到处理完成或需要采取进一步行动为止。

这个程序的输出如下：

```plain
Assistant(id='asst_aT4hurwd35eSave7qrt2t6eJ', created_at=1711126020, description=None, file_ids=[], instructions='可以帮助客户计算当前购物车的商品总价', metadata={}, model='gpt-4-1106-preview', name='订单价格计算器', object='assistant', tools=[ToolFunction(function=FunctionDefinition(name='calculate_order_total', description='根据多个商品类型和数量计算订单总价', parameters={'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'item_type': {'type': 'string', 'description': '商品类型,例如:书籍,文具,电子产品'}, 'quantity': {'type': 'integer', 'description': '商品数量'}}, 'required': ['item_type', 'quantity']}}}, 'required': ['items']}), type='function')])
Thread(id='thread_1709dA8z7mQxnXP3U3QSnQiW', created_at=1712030293, metadata={}, object='thread')
ThreadMessage(id='msg_nPRj7cttfIEoXgmmAuGaJMdV', assistant_id=None, content=[MessageContentText(text=Text(annotations=[], value='你好,请问你能做什么。'), type='text')], created_at=1712030293, file_ids=[], metadata={}, object='thread.message', role='user', run_id=None, thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW')
读取Run的状态 Run(id='run_8XqQ2w5cO5H3te3GdeQxSrfB', assistant_id='asst_aT4hurwd35eSave7qrt2t6eJ', cancelled_at=None, completed_at=None, created_at=1712030293, expires_at=1712030893, failed_at=None, file_ids=[], instructions='可以帮助客户计算当前购物车的商品总价', last_error=None, metadata={}, model='gpt-4-1106-preview', object='thread.run', required_action=None, started_at=None, status='queued', thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW', tools=[ToolAssistantToolsFunction(function=FunctionDefinition(name='calculate_order_total', description='根据多个商品类型和数量计算订单总价', parameters={'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'item_type': {'type': 'string', 'description': '商品类型,例如:书籍,文具,电子产品'}, 'quantity': {'type': 'integer', 'description': '商品数量'}}, 'required': ['item_type', 'quantity']}}}, 'required': ['items']}), type='function')], usage=None, temperature=1.0)
Run的轮询信息:
Run(id='run_8XqQ2w5cO5H3te3GdeQxSrfB', assistant_id='asst_aT4hurwd35eSave7qrt2t6eJ', cancelled_at=None, completed_at=None, created_at=1712030293, expires_at=1712030893, failed_at=None, file_ids=[], instructions='可以帮助客户计算当前购物车的商品总价', last_error=None, metadata={}, model='gpt-4-1106-preview', object='thread.run', required_action=None, started_at=1712030294, status='in_progress', thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW', tools=[ToolAssistantToolsFunction(function=FunctionDefinition(name='calculate_order_total', description='根据多个商品类型和数量 计算订单总价', parameters={'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'item_type': {'type': 'string', 'description': '商品类型,例如:书籍,文具,电子产品'}, 'quantity': {'type': 'integer', 'description': '商品数量'}}, 'required': ['item_type', 'quantity']}}}, 'required': ['items']}), type='function')], usage=None, temperature=1.0)

Run的轮询信息:
Run(id='run_8XqQ2w5cO5H3te3GdeQxSrfB', assistant_id='asst_aT4hurwd35eSave7qrt2t6eJ', cancelled_at=None, completed_at=None, created_at=1712030293, expires_at=1712030893, failed_at=None, file_ids=[], instructions='可以帮助客户计算当前购物车的商品总价', last_error=None, metadata={}, model='gpt-4-1106-preview', object='thread.run', required_action=None, started_at=1712030294, status='in_progress', thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW', tools=[ToolAssistantToolsFunction(function=FunctionDefinition(name='calculate_order_total', description='根据多个商品类型和数量
计算订单总价', parameters={'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'item_type': {'type': 'string', 'description': '商品类型,例如:书籍,文具,电子产品'}, 'quantity': {'type': 'integer', 'description': '商品数量'}}, 'required': ['item_type', 'quantity']}}}, 'required': ['items']}), type='function')], usage=None, temperature=1.0)

Run的轮询信息:
Run(id='run_8XqQ2w5cO5H3te3GdeQxSrfB', assistant_id='asst_aT4hurwd35eSave7qrt2t6eJ', cancelled_at=None, completed_at=None, created_at=1712030293, expires_at=1712030893, failed_at=None, file_ids=[], instructions='可以帮助客户计算当前购物车的商品总价', last_error=None, metadata={}, model='gpt-4-1106-preview', object='thread.run', required_action=None, started_at=1712030294, status='in_progress', thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW', tools=[ToolAssistantToolsFunction(function=FunctionDefinition(name='calculate_order_total', description='根据多个商品类型和数量 计算订单总价', parameters={'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'item_type': {'type': 'string', 'description': '商品类型,例如:书籍,文具,电子产品'}, 'quantity': {'type': 'integer', 'description': '商品数量'}}, 'required': ['item_type', 'quantity']}}}, 'required': ['items']}), type='function')], usage=None, temperature=1.0)

Run的轮询信息:
Run(id='run_8XqQ2w5cO5H3te3GdeQxSrfB', assistant_id='asst_aT4hurwd35eSave7qrt2t6eJ', cancelled_at=None, completed_at=1712030317, created_at=1712030293, expires_at=None, failed_at=None, file_ids=[], instructions='可以帮助客户计算当前购物车的商品总价', last_error=None, metadata={}, model='gpt-4-1106-preview', object='thread.run', required_action=None, started_at=1712030294, status='completed', thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW', tools=[ToolAssistantToolsFunction(function=FunctionDefinition(name='calculate_order_total', description='根据多个商品类型和数量计 算订单总价', parameters={'type': 'object', 'properties': {'items': {'type': 'array', 'items': {'type': 'object', 'properties': {'item_type': {'type': 'string', 'description': '商品类型,例如:书籍,文具,电子产品'}, 'quantity': {'type': 'integer', 'description': '商品数量'}}, 'required': ['item_type', 'quantity']}}}, 'required': ['items']}), type='function')], usage=Usage(completion_tokens=340, prompt_tokens=327, total_tokens=667), temperature=1.0)

全部的message SyncCursorPage[ThreadMessage](data=[ThreadMessage(id='msg_1x5L8QTIhw2drlG6gCJhytIh', assistant_id='asst_aT4hurwd35eSave7qrt2t6eJ', content=[MessageContentText(text=Text(annotations=[], value='你好！我是一个人工智能助手，可以帮你完成许多任务。以下是我可以提供帮助的一些范例：\n\n1. 回答问题：我能提供关于各种主题的信息，从简单的 事实问题到更复杂的解释和建议。\n2. 解决问题：我可以帮助你解决数学问题、提供编程指导或帮你理解复杂的概念。\n3. 数据分析：我可以帮你分析数据，提供统计信息或进行预测分析。\n4. 文字处理：我可以帮你校对文本、生成内容或翻译成不同的语 言。\n5. 计算与转换：我可以执行各种类型的计算，比如货币转换、单位转换、日期计算等。\n6. 生活帮助：我能帮你规划日程、设置提醒或者提供生活小贴士。\n7. 购物助手：我可以帮你计算购物车的商品总价、比较产品价格或提供购物建议。\n\n还有 很多其他的功能和服务。如果你有具体的需求或问题，随时告诉我，我会尽力协助你。'), type='text')], created_at=1712030296, file_ids=[], metadata={}, object='thread.message', role='assistant', run_id='run_8XqQ2w5cO5H3te3GdeQxSrfB', thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW'), ThreadMessage(id='msg_nPRj7cttfIEoXgmmAuGaJMdV', assistant_id=None, content=[MessageContentText(text=Text(annotations=[], value='你好,请问你能做什么。'), type='text')], created_at=1712030293, file_ids=[], metadata={}, object='thread.message', role='user', run_id=None, thread_id='thread_1709dA8z7mQxnXP3U3QSnQiW')], object='list', first_id='msg_1x5L8QTIhw2drlG6gCJhytIh', last_id='msg_nPRj7cttfIEoXgmmAuGaJMdV', has_more=False)
下面打印最终的Assistant回应:
[MessageContentText(text=Text(annotations=[], value='你好！我是一个人工智能助手，可以帮你完成许多任务。以下是我可 以提供帮助的一些范例：\n\n1. 回答问题：我能提供关于各种主题的信息，从简单的事实问题到更复杂的解释和建议。\n2. 解决问题：我可以帮助你解决数学问题、提供编程指导或帮你理解复杂的概念。\n3. 数据分析：我可以帮你分析数据，提供统计信息 或进行预测分析。\n4. 文字处理：我可以帮你校对文本、生成内容或翻译成不同的语言。\n5. 计算与转换：我可以执行各种类型的计算，比如货币转换、单位转换、日期计算等。\n6. 生活帮助：我能帮你规划日程、设置提醒或者提供生活小贴士。\n7. 购物助手：我可以帮你计算购物车的商品总价、比较产品价格或提供购物建议。\n\n还有很多其他的功能和服务。如果你有具体的需求或问题，随时告诉我，我会尽力协助你。'), type='text')]

```

这个输出内容很多，又有点不好理解，所以我给你总结成了下面的列表。

![图片](https://static001.geekbang.org/resource/image/4d/83/4d4a478284b2af88e4b64d65c3709f83.jpg?wh=1816x1134)

通过这个表格，我们可以清晰地看到整个对话过程中，Assistant、Thread、Message和Run这几个关键对象的状态变化。其中，Run的状态变化最为关键，体现了Assistant处理用户请求的完整生命周期，从 “queued” 到 “in\_progress”，最后到 “completed”。整体流程正如下图所示。

![](https://static001.geekbang.org/resource/image/01/54/017b829869fd3eb7e1ea2ecd31fece54.jpg?wh=1788x754)

这就是不调用Function时，Run状态变化的最简示例。

### 加入了 Function Call 之后的状态流转

以上，是最简单的流程。你可能已经意识到了，上一讲中，我们的示例中Run的状态比上面复杂多了。这是因为，我们当时的对话“你好，我购买了一本书和一个电子产品，请帮我计算一下订单总价”，成功地激活了Assistant的功能调用服务（Function Tool），从而进一步 **触发了Run的requires\_action状态**。

此时，如果你使用自定义的poll\_run\_status函数来取代上一讲中的create\_and\_poll API，你就会发现，Run经过了queue和in\_progress两个状态之后，是进入了requires\_action这个新状态，等待函数的本地调用，当然本地调用结束之后，必须 **再通过submit\_tool\_outputs提交给Assistant，Run状态才变为 “completed”，Assistant 处理过程才结束**。

如果你持续地把Run的status打印出来，总结成列表的形式，就会如下表所示。

![图片](https://static001.geekbang.org/resource/image/85/11/85e7eff68fd8424100d8e0a522c06d11.jpg?wh=1404x1368)

通过这个表格，我们可以清晰地看到整个对话过程中，Assistant、Thread、Message和Run这几个关键对象的状态变化。其中，Run的状态变化最为关键，体现了Assistant处理用户请求的完整生命周期。正如下图所示。

![](https://static001.geekbang.org/resource/image/d3/2b/d358ccdcda13b3b18ce7f00ce11d602b.jpg?wh=1695x745)

与上一个例子相比，这个例子中Run的状态出现了 “requires\_action”（需要操作），表明Assistant在处理过程中需要调用外部函数。我们可以看到，在读取函数元数据信息、动态调用函数并获得结果后，Run的状态才变为 “completed”（已完成）。这展示了函数调用在Assistant处理过程中的重要作用。

## 总结时刻

这节课，我带着你深入探讨了OpenAI Assistant中Thread和Run的概念，以及它们的生命周期管理和状态转换。了解这些内容可以帮助我们更好地使用OpenAI的Assistants API构建强大的AI应用。

这几个重要概念列表如下：

![图片](https://static001.geekbang.org/resource/image/ed/f1/ed60d6e017fa13d24c978be1ab5c58f1.jpg?wh=1668x808)

在下节课中，我们将继续学习Assistant的其他重要功能，如代码解释器（Code interpreter）和文件检索（File search）等工具的使用。敬请期待！

## 思考题

1. 我们自定义的函数 poll\_run\_status() 和 client.beta.threads.runs.create\_and\_poll() 这个API有何异同？为何这一课中，我们选择使用自定义的函数poll\_run\_status()？
2. 观察程序中每一个Run的输出，说一说，Run的生命周期大概有多长？在本课的两个示例中，Run在什么情况下可能会进入Expired状态？
3. 调整程序代码，尝试通过client.beta.threads.runs.cancel这个API来取消正在进行的Run，使Run进入cancelled状态。

期待你的思考，欢迎在评论区与我交流。如果今天的内容让你有所收获，也欢迎你把这节课转发给有需要的朋友！我们下节课再见！