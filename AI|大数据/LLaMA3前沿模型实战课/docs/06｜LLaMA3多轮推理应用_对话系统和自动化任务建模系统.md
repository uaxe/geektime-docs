你好，我是Tyler。

今天，我们将深入探讨多轮对话的应用场景，并重点了解LLaMA 3在这一领域的能力。LLaMA 3作为当前最强大的语言模型之一，特别适合应用于复杂的对话系统和自动化任务流程中。我们将通过两个典型案例——对话系统和自动化任务建模系统，来展示Llama-3如何在这些复杂场景中表现出色。

## 多轮对话的核心能力

多轮对话系统的核心包括两个重要功能： **与人的互动和自动化推理**。LLaMA 3作为当前最强大的语言模型之一，凭借其深度学习能力，可以不断地理解对话上下文、记住对话历史，并基于这些信息生成符合逻辑和语境的回应。这使得它不仅能够处理简单的问答任务，还能在复杂的对话场景和任务流程自动化中表现出色。

## 对话系统：ChatGPT

### 对话状态应用设计

多轮对话是AIGC（人工智能生成内容）产品的主要形式，它显著提升了人机交互的效率和自然度。在对话系统中，LLaMA 3的典型应用之一就是像ChatGPT这样的智能助手。设计和维护对话状态是系统面临的核心挑战。对话状态指的是模型在多轮对话中对用户输入的理解和记忆。一个设计良好的对话状态管理系统对于保持对话的连贯性和逻辑性至关重要。

在一个典型的购票对话中，用户可能会先询问航班信息，然后选择航班并完成支付。在这个过程中，模型需要维护用户的需求、偏好和上下文信息，以便在后续对话中做出合适的回应。LLaMA 3凭借其强大的自然语言理解能力，能够准确捕捉并记住这些信息，从而生成符合上下文的回应。

### 示例 1：ChatGPT 客服对话

以下是一个示例代码，展示如何使用Llama-3模型进行多轮对话，以模拟客服对话系统。

```python
import ollama

def customer_service_chat(history: str, user_input: str, max_turns: int = 3) -> tuple[str, str]:
    """
    与客服进行对话，并维护对话历史。

    参数:
    history (str): 先前的对话历史。
    user_input (str): 用户当前的输入。
    max_turns (int): 需要保留的最大对话轮数。

    返回:
    tuple[str, str]: 更新后的对话历史和客服的回复。
    """
    # 分割历史对话成列表，保留最近 max_turns 轮对话
    history_lines = history.split("\n")
    recent_history = "\n".join(history_lines[-max_turns * 2:])  # 每轮对话包含用户和客服两句

    # 更新历史记录，拼接对话
    recent_history += f"\n用户: {user_input}\n客服:"

    # 使用 Ollama 进行对话，要求用中文回答，并明确指示上下文
    messages = [
        {'role': 'system', 'content': '请根据以下对话历史，用中文回答问题。'},
        {'role': 'user', 'content': recent_history}
    ]

    response = ollama.chat(model='llama3', messages=messages)

    # 提取并清理模型的回复
    reply = response['message']['content'].strip()

    # 更新历史，保留全量历史记录
    history += f"\n用户: {user_input}\n客服: {reply}"

    return history, reply

# 示例对话
history = "客服: 欢迎使用在线客服系统！请问有什么可以帮您？"
user_input = "我想预订一张飞往纽约的机票。"
history, reply = customer_service_chat(history, user_input)
print(f"用户: {user_input}\n客服: {reply}")

user_input = "有哪些航班可以选择？"
history, reply = customer_service_chat(history, user_input)
print(f"用户: {user_input}\n客服: {reply}")

```

这个代码模拟了一个用户与客服系统的对话。初始对话历史包含助手的欢迎消息，用户请求预订机票，模型生成的回复被添加到对话历史中，接着用户询问航班选择，模型再生成新的回复。代码展示了如何初始化Llama-3模型、处理对话历史和生成响应。

### 对话状态的维护

在多轮对话中，如何高效地维护对话状态至关重要。对于长时间对话，历史对话记录可能变得冗长且不必要。将整个历史记录传递给模型不仅会增加计算开销，还可能导致模型在大量无关信息中“迷失方向”，从而降低提示语的工作效率。因此，必须针对性地选择历史记录中的关键部分。

LLaMA 3在对话状态维护过程中，主要考虑了 **近时性和相关性**。近时性指的是优先选择最近的对话记录，因为它们通常与当前上下文更为相关。相关性要求模型筛选出与当前任务密切相关的信息，避免被无关内容干扰。如果希望获得兼顾这两个特性的历史记录，需要结合检索增强生成的方法，这部分内容将在后续章节进行详细展开。

这里先带你学习另一项高效的提示语工程技巧，那就是 **对话压缩**，我们可以将历史对话在特定的触发条件下（如完成10轮对话后）进行历史对话摘要压缩，比如将前十轮的对话内容传输给大模型，让它生成这段对话的摘要。

```python
import ollama

def summarize_dialogue(dialogue_history):
    # 历史对话压缩，提取关键信息
    relevant_dialogue = "\n".join(line for line in dialogue_history.split("\n") if "用户:" in line or "客服:" in line)

    # 生成对话摘要的提示词，强调保留数字和地点等关键信息
    prompt = (
        f"请提取以下对话的关键信息，并生成摘要，保留数字和地点等重要信息，去除不必要的细节:\n\n{relevant_dialogue}"
    )

    # 使用 Ollama 进行对话摘要生成，并指定用中文回答
    messages = [
        {'role': 'user', 'content': prompt},
        {'role': 'system', 'content': '请用中文回答'}
    ]

    response = ollama.chat(model='llama3', messages=messages)

    # 提取并清理模型的回复
    summary = response['message']['content'].strip()

    return summary

# 示例对话记录
dialogue_history = (
    "用户: 你好，你怎么样？\n"
    "客服: 我很好，谢谢！请问今天有什么可以帮助您的？\n"
    "用户: 我需要帮助处理我的账户。您能查看我的余额吗？\n"
    "客服: 当然可以！请提供您的账户号码。\n"
    "用户: 我的账户号码是123456。\n"
    "客服: 让我为您查一下...\n"
    "客服: 您的当前余额是$500。\n"
    "用户: 谢谢！您能告诉我最近的交易吗？\n"
    "客服: 我需要验证您的身份才能提供交易详细信息。\n"
    "用户: 好的，这里是我有的详细信息。\n"
)

# 生成摘要
summary = summarize_dialogue(dialogue_history)
print("对话摘要:", summary)

# 压缩历史对话信息
dialogue_history = summary

```

这样不仅可以有效地压缩模型的输入长度，也可以让模型更集中在关键的历史信息上。

这一切都表明LLaMA 3具备在复杂对话场景中有效管理对话状态的能力，使得它能够在多轮对话中保持一致性并生成高质量的回应。

## 有限状态机：FSM

任务流程建模是流程自动化的关键技术之一。在 FSM 系统中，任务流程被建模为多个状态的转换，这些状态之间的转换通常需要复杂的条件判断和搜索算法的支持。LLaMA 3凭借其强大的自然语言处理（NLP）能力，能够为这些任务流程提供智能化的支持。

### 任务流程建模

在复杂任务流程中，LLaMA 3不仅能够理解自然语言指令，还能够将这些指令转化为可执行的任务操作。例如，在一个文件处理系统中，用户可能会要求系统根据文件类型、内容和需求进行不同的处理。LLaMA 3可以自动理解这些要求，并选择合适的处理方式，最终实现整个流程的自动化执行。

任务流程建模的核心在于如何将一个复杂的任务拆分为多个状态，并定义这些状态之间的转换规则。LLaMA 3通过自然语言理解（NLU）和自然语言生成（NLG）技术，可以在理解用户意图的基础上，自动构建有限状态机，并在不同状态之间智能地进行转换。比如，在一个多步骤的流程中，LLaMA 3能够根据当前的状态，自动决定下一步操作，并在需要时调整流程路径。

### 示例 2：有限状态机（FSM）任务流程建模

这个代码示例展示了如何使用有限状态机（FSM）来建模一个任务流程系统，该系统用于根据用户的输入推荐金融产品。

```python
import json
from ollama import chat

class FinancialProductFSM:
    def __init__(self):
        self.states = {
            'START': 'START',
            'YOUNG': 'YOUNG',
            'OLD': 'OLD',
            'LOW_RISK': 'LOW_RISK',
            'HIGH_RISK': 'HIGH_RISK',
            'HIGH_INCOME': 'HIGH_INCOME',
            'LOW_INCOME': 'LOW_INCOME'
        }
        self.current_state = self.states['START']

        self.transitions = {
            (self.states['START'], 'young'): self.states['YOUNG'],
            (self.states['START'], 'old'): self.states['OLD'],
            (self.states['YOUNG'], 'low_risk'): self.states['LOW_RISK'],
            (self.states['YOUNG'], 'high_risk'): self.states['HIGH_RISK'],
            (self.states['OLD'], 'low_risk'): self.states['LOW_RISK'],
            (self.states['OLD'], 'high_risk'): self.states['HIGH_RISK'],
        }

        self.product_recommendations = {
            (self.states['LOW_RISK'], self.states['HIGH_INCOME']): '高收益储蓄账户',
            (self.states['HIGH_RISK'], self.states['HIGH_INCOME']): '股票和共同基金',
            (self.states['LOW_RISK'], self.states['LOW_INCOME']): '定期存款（CD）',
            (self.states['HIGH_RISK'], self.states['LOW_INCOME']): '高风险投资基金',
        }

    def process_input(self, user_info):
        age = user_info.get('age')
        risk = user_info.get('risk')
        income = user_info.get('income')

        new_state = self.update_state(age, risk)
        if new_state is None:
            return '输入无效'

        self.current_state = new_state
        return self.get_recommendation(income)

    def update_state(self, age, risk):
        if age in ['young', 'old']:
            state_after_age = self.transitions.get((self.states['START'], age))
            return self.transitions.get((state_after_age, risk)) if state_after_age else None
        return None

    def get_recommendation(self, income):
        for (risk_state, income_state), product in self.product_recommendations.items():
            if self.current_state == risk_state:
                return product if income_state == (self.states['HIGH_INCOME'] if income == 'high_income' else self.states['LOW_INCOME']) else None
        return '没有合适的产品推荐'

def get_user_info_from_ollama(dialogue):
    """
    与 Ollama 模型对话，要求返回用户的关键信息，以 JSON 格式返回。
    指定 age、risk、income 的可能枚举值。
    """
    prompt = f"""
    请从以下对话中提取用户的年龄、风险偏好和收入水平，并以 JSON 格式返回。只输出 JSON，不要附加任何其他文字。
    格式如下：
    {{
        "age": "young" 或 "old",
        "risk": "low_risk" 或 "high_risk",
        "income": "high_income" 或 "low_income"
    }}

    对话内容如下：
    {dialogue}
    """

    # 调用 Ollama API 进行对话，返回结构化的 JSON 响应
    response = chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])

    # 获取 Ollama 返回的响应
    ollama_response = response['message']['content'].strip()

    # 将响应字符串转换为 Python 字典
    try:
        user_info = json.loads(ollama_response)  # 使用 json.loads 安全解析 JSON
    except json.JSONDecodeError:
        return None

    return user_info

def main():
    fsm = FinancialProductFSM()
    print("欢迎来到金融产品推荐系统！")

    # 假设对话记录来自 Ollama 的自然语言对话
    dialogue_history = """
    用户: 我年轻，喜欢高风险投资，而且收入挺高的。
    """

    # 使用 Ollama 提取用户信息（年龄、风险偏好、收入水平）
    user_info = get_user_info_from_ollama(dialogue_history)

    if user_info:
        # 显示提取的用户信息
        print(f"提取的用户信息: {json.dumps(user_info, ensure_ascii=False)}")

        # 处理提取的信息并推荐金融产品
        recommendation = fsm.process_input(user_info)
        print(f"推荐的产品: {recommendation}")
    else:
        print("无法根据用户输入生成推荐。")

if __name__ == "__main__":
    main()

```

这个示例展示了如何定义一个有限状态机来推荐金融产品。代码通过状态转换和条件判断，根据用户的输入动态更新状态并提供推荐。这个示例有助于理解复杂状态流转的过程，后续章节我会介绍如何用LangGraph完成更高效的任务建模和状态管理。

这一能力使LLaMA 3在流程自动化的广泛应用中大展身手，不仅可以处理复杂的任务，还能够灵活应对各种突发情况。

### 任务状态的维护

在流程自动化中，任务状态的维护与对话状态有着相似之处，但更为复杂。任务状态指的是系统在执行自动化流程时，各个环节的执行情况和当前状态。随着流程的推进，Llama-3需要实时更新这些状态，并根据最新的状态做出决策。这种状态维护能力确保了整个自动化流程的连续性和准确性。

例如，在一个多步骤的文件处理流程中，每一步操作之后，LLaMA 3都需要更新当前的任务状态，如文件的处理进度、操作成功与否以及下一步可能的选择。通过对任务状态的精准维护，LLaMA 3能够在整个流程中保持高度一致性，避免因状态信息错误或遗漏而导致的流程中断或错误决策。

此外，LLaMA 3还能够在任务状态维护中融入更复杂的逻辑和判断条件。例如，某些流程步骤可能依赖于前一步操作的成功与否，或者需要根据外部数据源的实时更新来调整任务状态。在这些场景中，LLaMA 3的能力可以进一步扩展，涵盖更广泛的自动化工作流。

## 总结

这节课我们深入探讨了LLaMA 3在多轮对话中的能力边界，并通过ChatGPT和LangGraph两个典型案例，展示了其在复杂人机交互和任务流程自动化中的强大应用。通过对话状态和任务状态的有效管理，LLaMA 3能够在广泛的应用场景中提供高质量的智能服务。

## 思考题

1. 为什么说多步推理过程的本质是一台状态机？
2. 你是否能想到有哪些多步推理不能解决的问题？

欢迎你把思考后的结果分享到留言区，也欢迎你把这节课分享给需要的朋友，我们下节课再见！