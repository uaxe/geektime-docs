你好，我是黄佳。

开源模型的微调大家耳熟能详，但是很少有人了解OpenAI的GPT模型也可以微调。今天我们就来探讨如何微调OpenAI的闭源模型，以及使用Function Calling进行特定领域微调的流程和要点。

OpenAI的GPT系列模型经过海量数据的预训练，已经具备了强大的自然语言理解和生成能力。但面对特定领域的应用场景，预训练模型难免会有知识盲区和表现欠佳的情况。这时候，我们就需要用特定领域的数据对模型进行微调，让模型更加贴合具体的任务需求。

微调后的模型可以更好地理解特定领域的术语、口吻和逻辑，生成更加准确、专业的内容。比如在法律领域微调后，模型可以更好地分析案情，援引法条，给出有说服力的法律意见。因此，微调 GPT 家族的模型还是能进一步拓展 OpenAI 这一系列模型的应用场景和落地空间。

## OpenAI 的 Fine-Tuning 基本流程

OpenAI为GPT-3.5系列的模型提供了 Fine-Tuning API，我们可以用自己的数据对模型进行微调，至于GPT-4系列的模型，只有gpt-4-0613可以进行实验性质的微调。

主要步骤如下：

1. 准备符合要求的微调数据集。微调数据要采用 JSONL 格式，每行代表一个训练样本。每个样本是一个 JSON 对象，主要包含以下字段：

- messages：由角色（role）和内容（content）组成的对话数据。
- functions：可选。一个列表，其中列出了样本涉及的函数调用。

下面就是 JSONL 微调数据文件的示例，这是OpenAI给出的例子，这个微调数据的目标是创建一个偶尔给出讽刺性回应的聊天机器人。

```plain
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}

```

OpenAI建议准备 50~100 个高质量的数据样本，最少不能少于10个，具体数量取决于任务复杂度。

数据准备好之后，要检查 JSONL 文件的格式是否符合输入要求。通常我们还会把数据集拆分成训练集（training set）和验证集（validation set）两部分。

OpenAI 只对微调训练数据收费，而不对验证数据中的 Token 收费。要估算特定微调作业的成本，请使用以下公式：

$$每 1k 个Token 的基本成本 \* 输入文件中的Token 数量 \* 训练的Epoch 数量$$

对于一个包含 10000 个 Token 的文件，要训练10个Epoch，预计成本约为 1.60 美元。

2. 上传训练和验证数据。使用 Files API 把格式化好的 JSONL 文件分别上传到 OpenAI。上传完成后，会得到训练文件和验证文件各自的ID。有了文件 ID，我们就可以启动微调任务了。

3. 创建一个微调任务。这里需要指定要微调的基础模型、新模型的后缀名、轮次等参数。Job创建成功后，我们会得到一个微调任务的ID。

4. 查看微调进度。可以用微调任务的ID查询微调进度。从API返回的信息里，你可以了解到：

- 任务状态（排队中、进行中、完成、出错等）
- 经过的训练轮数（epochs）、批次（steps）
- 各种训练指标，如 loss、accuracy 的变化趋势
- 完成后得到的模型名称

这些信息可以帮你持续监控和评估微调过程。

5. 测试和使用微调后的模型。微调完成后，你就得到了一个定制化的模型。它的名称是由 **基础模型名+你预设的后缀** 构成。

你可以像使用普通 OpenAI 模型一样，通过 API 调用这个微调后的新模型进行测试和应用。测试时可以通过验证数据，来客观评估微调效果。如果效果不理想，则可能需要返回第1步，优化你的微调数据，然后尝试不同的微调参数。

## GPT 模型微调实战

上面的流程是比较清晰的，下面，我们就开始拿具体的示例来做一次实战。

### 利用 GPT 模型创建微调数据

微调模型的第一步当然是收集数据，如果你有足够的行业领域相关的数据，就可以把它整理成OpenAI 微调所需要的格式。

当然，如果想尝试微调，但是没有数据，也有办法。我在下面的代码中，利用OpenAI的GPT-4模型来生成金融领域的问答数据，用于后续的模型微调。 **用智能更高阶的模型来为更低阶的模型（也包括开源模型）制作微调数据或者评测数据，这是一个常见的操作**。

```plain
from openai import OpenAI
from tqdm import tqdm
import json

client = OpenAI()

# 配置OpenAI API密钥
# openai.api_key = "your_api_key"

# 定义问题生成函数
def generate_question(topic):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个善于提问的助手,会根据给定的话题生成问题。"},
            {"role": "user", "content": f"请问一个关于{topic}的问题,用于训练金融领域的聊天机器人。直接生成问题就好，不需要回复“好的”"}
        ],
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# 定义回答生成函数
def generate_answer(question):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个金融领域的智能助理,能够专业地回答用户的金融问题。"},
            {"role": "user", "content": f"Q: {question}\nA: "}
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# 定义要生成问答数据的金融主题
topics = [
    "股票投资",
    "银行理财",
    "基金定投",
    "资产配置",
    "风险管理"
]

# 生成问答数据
qa_data = []
total_qa_pairs = len(topics) * 3
with tqdm(total=total_qa_pairs, desc="生成问答数据", unit="组") as pbar:
    for topic in topics:
        for i in range(3):  # 每个主题生成3组问答
            question = generate_question(topic)
            print(f"生成问题: {question}")

            answer = generate_answer(question)
            print(f"生成回答: {answer}\n")

            qa_data.append({
                "messages": [
                    {"role": "system", "content": "你是一个金融领域的智能助理,能够专业地回答用户的金融问题。"},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            })

            pbar.update(1)  # 更新进度条

# 将生成的数据保存到JSONL文件
with open("finance_qa_data.jsonl", "w", encoding="utf-8") as f:
    for data in qa_data:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

print(f"\n成功生成并保存{len(qa_data)}组金融问答数据到finance_qa_data.jsonl文件。")

```

程序中，首先定义了问题生成函数generate\_question和回答生成函数generate\_answer，分别根据给定的话题生成问题和对应的回答。然后设置要生成数据的金融主题，并使用这些主题生成问答数据对，将生成的数据保存为JSONL格式的文件。

![图片](https://static001.geekbang.org/resource/image/86/0c/866bf76715b9c9577da3b52c655ddb0c.png?wh=1081x314)

下面是几个数据例子。

> {“messages”: \[{“role”: “system”, “content”: “你是一个金融领域的智能助理,能够专业地回答用户的金融问题。”}, {“role”: “user”, “content”: “好的，这里有一个关于股票投资的问题：\\n\\n"在进行股票投资时，如何评估一只股票的内在价值？有哪些关键指标和方法可以用来进行这种评估？”“}, {“role”: “assistant”, “content”: “评估一只股票的内在价值是股票投资中的关键步骤，通常涉及多种方法和指标。以下是一些常见的评估方法和关键指标：\\n\\n### 1. **基本面分析**\\n\\n **1.1. 市盈率（P/E Ratio）**\\n- **公式**: 市盈率 = 股票价格 / 每股收益（EPS）\\n- **解释**: 反映投资者愿意为每一单位的当前收益支付多少倍的价格。一般来说，较低的市盈率可能表示股票被低估，但也需要结合行业平均水平和公司的增长前景来判断。\\n\\n **1.2. 市净率（P/B Ratio）**\\n- **公式**: 市净率 = 股票价格 / 每股净资产\\n- **解释**: 表明投资者愿意为每一单位的净资产支付多少价格。较低的市净率可能表明股票被低估，但”}\]}
>
> {“messages”: \[{“role”: “system”, “content”: “你是一个金融领域的智能助理,能够专业地回答用户的金融问题。”}, {“role”: “user”, “content”: “当然可以! 这里有一个关于股票投资的问题:\\n\\n"在选择股票进行投资时，投资者应该考虑哪些关键因素来评估一只股票的潜在收益和风险?””}, {“role”: “assistant”, “content”: “在选择股票进行投资时，投资者需要全面评估多方面的因素，以判断一只股票的潜在收益和风险。以下是一些关键因素：\\n\\n1. **基本面分析**：\\n   - **公司财务状况**：查看公司的财务报表，包括资产负债表、利润表和现金流量表。关注收入增长、净利润、资产负债率和现金流状况。\\n   - **盈利能力**：评估公司的盈利能力，如净利润率、毛利率和运营利润率。\\n   - **市盈率（P/E Ratio）**：这个比率可以帮助你了解股票的估值水平，与同行业的其他公司进行比较。\\n   - **股息收益率**：如果你关注股息，查看公司的股息支付历史和收益率。\\n\\n2. **行业和市场前景**：\\n   - **行业趋势**：研究公司所在行业的整体发展趋势和”}\]}
>
> {“messages”: \[{“role”: “system”, “content”: “你是一个金融领域的智能助理,能够专业地回答用户的金融问题。”}, {“role”: “user”, “content”: “好的，这里有一个关于股票投资的问题：\\n\\n"在评估一只股票的投资价值时，应该重点关注哪些财务指标？请解释这些指标的意义及其在投资决策中的作用。”"}, {“role”: “assistant”, “content”: “在评估一只股票的投资价值时，投资者通常会关注多个财务指标，以全面了解公司的财务健康状况和未来增长潜力。以下是一些关键的财务指标及其意义：\\n\\n1. **每股收益（EPS, Earnings Per Share）**：\\n   - **意义**：每股收益是公司净利润除以流通在外的普通股股数所得的值。它反映了公司盈利能力，是衡量公司为股东创造价值的重要指标。\\n   - **作用**：EPS越高，通常表明公司的盈利能力越强，投资者可能会对其未来前景更有信心。\\n\\n2. **市盈率（P/E Ratio, Price to Earnings Ratio）**：\\n   - **意义**：市盈率是股票价格除以每股收益（EPS）。它反映了投资者为每一美元的收益愿意支付的价格。\\n   -”}\]}

### 上传数据文件

接下来，我们将生成的问答数据文件上传到OpenAI平台，为微调做准备。

在上传文件之前，我们先按照OpenAI所要求的数据结构，对微调文件进行一个检查。

```plain
import json
from collections import defaultdict

# 数据路径
data_path = "07_Finetune/Finetune_GPT3.5/finance_qa_data.jsonl"

# 加载数据集
with open(data_path, 'r', encoding='utf-8') as f:
    dataset = [json.loads(line) for line in f]

# 初始数据集统计
print("样本数量:", len(dataset))
print("第一个样本:")
for message in dataset[0]["messages"]:
    print(message)

# 格式错误检查
format_errors = defaultdict(int)

for ex in dataset:
    if not isinstance(ex, dict):
        format_errors["data_type"] += 1
        continue

    messages = ex.get("messages", None)
    if not messages:
        format_errors["missing_messages_list"] += 1
        continue

    for message in messages:
        if "role" not in message or "content" not in message:
            format_errors["message_missing_key"] += 1

        if any(k not in ("role", "content", "name", "function_call", "weight") for k in message):
            format_errors["message_unrecognized_key"] += 1

        if message.get("role", None) not in ("system", "user", "assistant", "function"):
            format_errors["unrecognized_role"] += 1

        content = message.get("content", None)
        function_call = message.get("function_call", None)

        if (not content and not function_call) or not isinstance(content, str):
            format_errors["missing_content"] += 1

    if not any(message.get("role", None) == "assistant" for message in messages):
        format_errors["example_missing_assistant_message"] += 1

if format_errors:
    print("发现错误:")
    for k, v in format_errors.items():
        print(f"{k}: {v}")
else:
    print("未发现错误")

```

格式检查结果表示，文件无误。

```plain
样本数量: 25
第一个样本:
{'role': 'system', 'content': '你是一个金融领域的智能助理,能够专业地回答用户的金融问题。'}
{'role': 'user', 'content': '好的，这里有一个关于股票投资的问题：\n\n"在进行股票投资时，如何评估一只股票的内在价值？有哪些关键指标和方法可以用 来进行这种评估？"'}
{'role': 'assistant', 'content': '评估一只股票的内在价值是股票投资中的关键步骤，通常涉及多种方法和指标。以下是一些常见的评估方法和关键指标：\n\n### 1. **基本面分析**\n\n**1.1. 市盈率（P/E Ratio）**\n- **公式**: 市盈率 = 股票价格 / 每股收益（EPS）\n- **解释**: 反映投资者愿意为每一单位的当前收益支付多少倍的价格。一般来说，较低的市盈率可能表示股票被低估，但也需要结合行业平均水平和公司的增长前景来判断。\n\n**1.2. 市净率（P/B Ratio）**\n- **公式**: 市净率 = 股票价格 / 每股净资产\n- **解释**: 表明投资者愿意为每一单位的净资产支付多少价格。较低的市净率可能表明股票被低估，但'}
未发现错误

```

然后使用 OpenAI 库提供的 files.create 方法，指定要上传的文件路径和用途（purpose=“fine-tune”），即可完成文件上传。

```plain
from openai import OpenAI
client = OpenAI()

# 如果没有错误,上传文件进行微调
if not format_errors:

    file = client.files.create(
        file=open(data_path, "rb"),
        purpose="fine-tune"
    )

    print(file)

```

上传成功后，会返回一个FileObject对象，包含文件的各种元数据信息。

```plain
FileObject(id='file-ID8oHTZDz5jp4VdzOnJyvgfs', bytes=30946, created_at=1717608254, filename='finance_qa_data.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)

```

### 提交微调作业

在上传完训练数据后，就可以提交微调作业了。通过调用 OpenAI 库的 fine\_tuning.jobs.create 方法，指定训练文件 ID、基础模型（这里使用gpt-3.5-turbo）以及超参数（如训练轮数n\_epochs），即可创建一个微调作业。

```plain
from openai import OpenAI
client = OpenAI()

n_epochs = 20

job = client.fine_tuning.jobs.create(
   training_file="file-ID8oHTZDz5jp4VdzOnJyvgfs",
   model="gpt-3.5-turbo",
   hyperparameters={"n_epochs": n_epochs}
)

print(job)

```

提交成功后，会返回一个FineTuningJob对象，包含作业的ID、状态等信息。

```plain
FineTuningJob(id='ftjob-b9S1AK4BHhBCYJv0I4LBZauM', created_at=1717608923, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs=2, batch_size='auto', learning_rate_multiplier='auto'), model='gpt-3.5-turbo-0125', object='fine_tuning.job', organization_id='org-2MRF2ZhOMmubKIrnf84j3uGi', result_files=[], seed=1597839268, status='validating_files', trained_tokens=None, training_file='file-ID8oHTZDz5jp4VdzOnJyvgfs', validation_file=None, estimated_finish=None, integrations=[], user_provided_suffix=None)
微调作业已创建,作业ID: ftjob-b9S1AK4BHhBCYJv0I4LBZauM

```

### 轮询作业，直至结束

由于微调作业需要一定的时间才能完成，我们需要定期查询作业状态，直到其状态变为 “succeeded”、“failed” 或 “cancelled”。通过一个while循环，不断地调用fine\_tuning.jobs.retrieve方法获取作业状态，并在每次查询之间等待10秒。

```plain
# 根据id重新获取微调作业
job = client.fine_tuning.jobs.retrieve('ftjob-b9S1AK4BHhBCYJv0I4LBZauM')

job_id = job.id
status = job.status

print(f"微调作业已创建,作业ID: {job_id}")

# 轮询作业状态,直至完成
import time
while status not in ["succeeded", "failed", "cancelled"]:
    print(f"作业状态: {status}, 等待 10 秒...")
    time.sleep(10)

    job = client.fine_tuning.jobs.retrieve(job_id)
    status = job.status

print(f"微调作业已完成,最终状态: {status}")

if status == "succeeded":
    print(f"微调后的模型名称: {job.fine_tuned_model}")
else:
    print("微调作业未成功完成,请检查错误信息。")

```

当作业成功完成时，我们可以获取到微调后的模型名称，并且可以打印出微调过程中的损失信息；如果作业未成功，则需要检查错误信息。

```plain
微调作业已创建,作业ID: ftjob-b9S1AK4BHhBCYJv0I4LBZauM
作业状态: running, 等待 10 秒...
作业状态: running, 等待 10 秒...
作业状态: running, 等待 10 秒...
微调作业已完成,最终状态: succeeded
微调后的模型名称: ft:gpt-3.5-turbo-0125:personal::9Wou7j8z
... ...
Step 34/50: training loss=0.56
Step 35/50: training loss=0.38
Step 36/50: training loss=0.43
Step 37/50: training loss=0.43
Step 38/50: training loss=0.42
Step 39/50: training loss=0.56
Step 40/50: training loss=0.47
Step 41/50: training loss=0.43
Step 42/50: training loss=0.34
Step 43/50: training loss=0.59
Step 44/50: training loss=0.59
Step 45/50: training loss=0.56
Step 46/50: training loss=0.45
Step 47/50: training loss=0.51
Step 48/50: training loss=0.40
Step 49/50: training loss=0.44
Step 50/50: training loss=0.43
Checkpoint created at step 25 with Snapshot ID: ft:gpt-3.5-turbo-0125:personal::9Wou7Qnq:ckpt-step-25
New fine-tuned model created: ft:gpt-3.5-turbo-0125:personal::9Wou7j8z
The job has successfully completed

```

日志显示，微调已经成功，并且给出了每轮的Training Loss。我在这次的微调过程中，并没有拆分训练数据集和测试数据集，如果你进行拆分，那么在训练的过程中，会同时显示validation loss。

### 运行微调后的模型

这样，我们就拥有了一个专属于自己的、懂财务的GPT模型了！我的这个模型的ID是ft:gpt-3.5-turbo-0125:personal::9Wou7j8z，下面测一测它。

```plain
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="ft:gpt-3.5-turbo-0125:personal::9Wou7j8z",
  messages=[
    {"role": "system", "content": "你是我的财务小助理"},
    {"role": "user", "content": "如何分析一支股票的基本面？"}
  ]
)
print(completion.choices[0].message)

```

输出如下：

```plain
ChatCompletionMessage(content='分析一支股票的基本面是评估该股票是否值得投资的重要步骤。以下是一些常用的方法和指标：\n\n1. **盈利能力**：\n   - **盈利状况**：查看公司近几年的盈利情况，包括净利润、营业利润、每股收益等指标。\n   - **增长情况**：关注盈利增长的趋势，逐年增长或稳定成长是正面的信号。\n   - **毛利率和净利率**：这两个指标反映了公司经营的盈利能力，通常越高越好。\n\n2. **财务状况**：\n   - **负债情况**：查看公司资产负债表，了解公司的负债结构，确保不会出现债务过高导致的财务困境。\n   - **流动比率和速动比率**：这两个比率可以衡量公司的偿债能力，流动比率应在1.5以
上，速动比率应该在1以上。\n\n3. **成长前景**：\n   - **行业前景**：了解公司所在行业的未来发展趋势，行业前景对公司成长至关重要。\n   - **收入来
源**：如果公司有新的产品、技术或服务计划，会推动未来的收入增长。\n\n4. **市场地位**：\n   - **市场份额**：了解公司在相关市场上的地位，市占率大
的公司通常有更稳定和高质量的盈利。\n   - **品牌资产**：具有强大品牌影响力的公司往往在市场上更具竞争力。\n\n5. **管理团队**：\n   - **领导能力**：评估公司高层管理团队的素质、经验和领导风格。\n   - **激励机制**：看看公司是否采取有效的激励措施来激励员工，并与股东利益保持一致。\n\n6. **行
业比较**：\n   - **对比分析**：比较目标公司与同行业的其他公司，了解其在市场上的竞争优势和劣势。\n\n7. **风险因素**：\n   - **宏观经济环境**：了解整体经济和政治环境的稳定性，它们可能对公司盈利产生影响。\n   - **公司内部风险**：例如高管变动、公司不当行为等。\n\n**结合技术分析**：\n   -
技术分析可以帮助了解股票的走势，并配合基本面分析进行决策。', role='assistant', function_call=None, tool_calls=None)

```

以上，就是微调GPT模型的整个流程。

## Function Calling 微调

除了常规的Fine-Tuning方式，OpenAI还支持一种特殊的微调模式，叫Function Calling微调。这种方式允许我们在微调时定义一些“函数”，让模型学会理解并调用函数。

Function Calling 我们在启程篇已经重点讲过了（在新版API中已经把它更名为Tool Call，但是目前在微调API中，仍然叫做 Function Calling）。

当Function Calling按预期运行时，它是一种非常强大的工具。然而，随着函数数量的增加和手头任务的复杂性增加，函数调用变得不那么准确。那么，此时Function Calling微调的好处是，让你的微调模型拥有预定义的函数知识，否则，在每次调用API时都要包含一长串函数定义会消耗大量Token，有时模型会产生幻觉或无法提供有效的 JSON 输出。

因此，使用Function Calling微调模型可以让你在即使没有完整的函数定义时，也可以获得符合格式的响应，同时获得更准确、更一致的输出。

Function Calling的微调数据样本格式和普通的Fine-Tuning样本略有不同。除了messages字段外，每个样本还可以包含一个functions字段，用于列举和定义相关函数。大概是这个样子。

```plain
{
    "messages": [
        {"role": "user", "content": "给我写一封请假信,用公司的正式格式"},
        {
            "role": "assistant",
            "function_call": {
                "name": "write_leave_letter",
                "arguments": "{\"name\": \"张三\", \"dept\": \"市场部\", \"position\": \"销售经理\", \"reason\": \"发烧感冒\", \"days\": 2}"
            }
        }
    ],
    "functions": [
        {
            "name": "write_leave_letter",
            "description": "写一封请假信",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string",  "description": "员工姓名"},
                    "dept": {"type": "string", "description": "所在部门"},
                    "position": {"type":  "string", "description": "职位"},
                    "reason": {"type":  "string", "description": "请假原因"},
                    "days": {"type":  "integer", "description":  "请假天数"}
                },
                "required": ["name", "dept", "position", "reason", "days"]
            }
        }
    ]
}

```

可以看到，这里在messages中引入了一个function\_call角色，表示助手要调用名为write\_leave\_letter的函数，并传入员工姓名、部门等参数。而在functions中则详细定义了这个函数的名称、描述、参数列表、参数类型等信息。

微调时模型会学习这种function\_call的模式，之后再遇到类似的场景时，就能更准确地自动抽取出关键信息，组织成结构化的函数调用，而不是简单地生成一段文本。

## 总结时刻

这节课我们重点学习了用OpenAI的Fine-Tuning API进行微调的基本流程。我们首先使用GPT-4生成高质量的领域特定问答数据，然后将数据上传到OpenAI平台。接着提交微调作业，并通过轮询的方式监控作业状态。当作业成功完成后，我们就得到了一个针对特定领域（如金融）进行过微调的模型，可以用于后续的应用开发和部署。

当然，在具体实践中你可能还会遇到一些问题，比如：

- 如何设计高质量的微调数据？
- 如何根据任务特点选择最佳的基础模型和微调参数？
- 如何权衡微调效果和成本开销？

这些都是微调大模型所不得不面对的没有标准答案的问题，这就需要在实践中不断摸索和优化。如果你在微调过程中有任何心得，也请你分享你的宝贵经验。

## 思考题

1. 针对你的业务场景，思考如何准备一套高质量的微调数据集？另外，在我用GPT-4构建数据集时，数据里面总是出现“好的”“没问题”“当然可以！”这样不该出现在金融数据集里面的词语。这是为什么？你怎样通过优化提示词来解决这个问题？
2. 针对金融微调数据集，请你尝试使用不同的微调参数来实现更好的微调效果。
3. Function Calling微调我只是给出了步骤和解释，没有给出具体实战代码，你能否自己完成一次Function Calling微调实战？

期待你的分享，欢迎与我交流。如果今天的内容让你有所收获，也欢迎你把这节课转发给有需要的朋友！我们下节课再见！