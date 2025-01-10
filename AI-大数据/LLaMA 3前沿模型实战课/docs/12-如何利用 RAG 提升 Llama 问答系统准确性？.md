你好，我是Tyler！

在上一讲中，我们学习了如何通过 LLaMa 3 来高效构建索引，提升 RAG 系统的输入质量。在这一讲中，我们将探讨如何优化 RAG 系统的在线检索效果，以确保生成内容的准确性和时效性。

## 知识冲突时的默认行为

在预训练过程中，LLaMA 3 积累了大量知识，主要分为两类。第一类是来自原始语料的历史实时信息，反映特定时间点的事实、事件或观点，但这些信息随着时间推移可能失去时效性。第二类则是模型通过学习原始数据模式所总结出的知识，这类知识通常不是直接的事实，而是对语言或概念的统计关联和推断。这两类知识都有一个共同的问题：随着时间的推移，原始数据中的事实信息可能失效，导致模型生成的内容不再准确反映当前情况。

在前面的课程中我们学到过，为了解决时效性的问题，使用上下文学习是一种有效策略。上下文学习通常通过提供提示词来引导模型，使其能够获取与当前任务或目标场景相关的事实信息。这些提示词为模型提供了最新的语境，从而确保生成的内容更加准确且紧贴现实需求。例如，在应对最新的新闻事件或动态变化时，提示词可以为模型提供最新的数据和信息，增强生成结果的时效性和相关性。

因此，在上下文学习的设计背景下，当模型在预训练过程中学到的历史知识与RAG提供的实时信息发生冲突时，模型默认会优先参考提示词中的事实信息。这种默认优先机制的初衷是为了让提示词引入当前的上下文，使得模型能够生成与实际情况更吻合的回答。

然而，尽管这一点在理论上看似良好，但实际上却给我们带来了很大的压力。这是因为我们需要确保注入模型的新的事实信息是准确的，避免错误信息的传播。这就需要一些关键策略来帮助我们解决这个问题。

## 信息来源的透明性

首先，RAG 系统应透明地向用户展示所使用的信息来源。在生成内容的同时，附上信息来源的链接或简短说明，确保用户了解这些信息的出处和可靠性。例如，系统可以为每条生成结果提供引用的文献、网页或数据库，增强内容的可信度并便于用户验证。

为了实现这一功能，可以利用向量数据库的元数据功能，具体步骤如下：

- **索引和存储信息源**：在向量数据库中，为每个信息源（如文献、网页、数据库等）创建条目，记录其元数据（标题、作者、出版日期、URL等），并将这些元数据作为向量的附加信息存储。

- **信息检索**：当用户发起查询时，RAG 系统会根据查询内容从向量数据库中检索相关信息源，提取与文本关联的元数据，以便在生成内容时使用。

- **生成内容时附带引用**： 在生成内容的过程中，系统可以将检索到的信息源的元数据附加到生成的文本中。例如，可以在生成的段落末尾添加一句话：“信息来源：标题（作者，出版日期），链接”，以便用户快速查看信息的出处。

- **增强用户体验**： 在界面上提供“信息来源”或“引用”标签，用户点击后可查看生成内容所依据的所有信息源的详细列表，方便验证信息的可靠性。

- **动态更新和维护**： 确保元数据的定期更新和维护，检查链接的有效性和信息的准确性，以始终提供可靠的信息来源。


下面是一个基于 **Milvus** 向量数据库的代码示例，展示了如何存储和检索信息源，并在生成内容时附加引用。

```python
from pymilvus import (
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    connections
)

# 连接到 Milvus 数据库
connections.connect("default", host='localhost', port='19530')

# 定义集合的字段
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),  # 向量维度
    FieldSchema(name="title", dtype=DataType.STRING),
    FieldSchema(name="author", dtype=DataType.STRING),
    FieldSchema(name="pub_date", dtype=DataType.STRING),
    FieldSchema(name="url", dtype=DataType.STRING)
]

# 创建集合
schema = CollectionSchema(fields, description="Document Collection with Metadata")
collection = Collection(name="documents", schema=schema)

# 插入数据
def insert_data(vectors, titles, authors, pub_dates, urls):
    entities = [
        {"name": "vector", "values": vectors},
        {"name": "title", "values": titles},
        {"name": "author", "values": authors},
        {"name": "pub_date", "values": pub_dates},
        {"name": "url", "values": urls}
    ]
    ids = collection.insert(entities)
    print(f"Inserted {len(ids)} documents.")

# 示例数据
vectors = [[0.1] * 128]  # 示例向量
titles = ["Sample Document"]
authors = ["Author Name"]
pub_dates = ["2024-10-16"]
urls = ["http://example.com"]

insert_data(vectors, titles, authors, pub_dates, urls)

# 检索数据
def retrieve_data(vector, top_k=5):
    results = collection.search(data=[vector], anns_field="vector", limit=top_k)
    for result in results:
        for hit in result.hits:
            print(f"Document: {hit.id}, Title: {hit.entity.get('title')}, "
                  f"Author: {hit.entity.get('author')}, "
                  f"Published Date: {hit.entity.get('pub_date')}, "
                  f"URL: {hit.entity.get('url')}")

# 示例检索
query_vector = [0.1] * 128  # 与插入的示例向量相同
retrieve_data(query_vector)

# 在生成内容时附带引用
generated_content = "This is the generated content."
for result in results:
    for hit in result.hits:
        citation = f"信息来源：{hit.entity.get('title')}（{hit.entity.get('author')}, {hit.entity.get('pub_date')}），[链接]({hit.entity.get('url')})"
        generated_content += f"\n{citation}"

print(generated_content)

```

通过这样的设计，RAG 系统不仅能够生成内容，还能提供透明的信息来源，从而增强用户的信任度和内容的可信度。在检索和生成过程中附带的引用，确保用户方便地访问信息出处，提升整体用户体验。例如，在生成关于“机器学习的基本概念”的内容时，系统会附上相应的参考链接，指向相关的学术论文或权威网站。

## 反馈机制的优化

此外，系统需要设计一个有效的反馈机制，允许用户对生成的内容进行正面或负面的评价。这一机制使用户能够帮助系统识别内容中的优缺点。具体而言，正面反馈将提升相关信息的优先级，增加其在未来查询中的出现概率；而负面反馈则有助于减少低质量内容的重复使用。

例如，用户可以对某个回答进行“赞”或“踩”，每天晚上（时机自己选择），系统会自动处理这些反馈，将获得多个“踩”的文档标记为负向内容，而获得多个“赞”的文档则设置为正向内容，从而动态调整内容的权重。

```python
# 示例：反馈机制实现
# 假设 feedback_list 是用户的反馈记录
feedback_list = [
    {"content_id": 1, "feedback_type": "positive"},
    {"content_id": 2, "feedback_type": "negative"},
    {"content_id": 3, "feedback_type": "negative"},
]

# 在处理反馈时，系统可以更新文档的标记
for feedback in feedback_list:
    if feedback["feedback_type"] == "negative":
        # 更新该文档的标签为负向
        print(f"Document ID {feedback['content_id']} updated to negative.")
    elif feedback["feedback_type"] == "positive":
        # 更新该文档的标签为正向
        print(f"Document ID {feedback['content_id']} updated to positive.")

```

通过这一用户反馈机制，RAG 系统能够在动态场景中自我调整。例如，当用户提供负面反馈时，系统可以将该内容标记为低质量，并在后续生成中避免重复出现。此外，我们可以为不同质量的内容准备三个向量数据库集合，分别存储高质量、普通质量和低质量的内容。这样，系统在检索时可以优先选择高质量集合中的信息。

最后，我们将用户的反馈纳入 RAG 检索内容的召回机制。具体而言，RAG 系统在进行检索时，不仅从原始索引中提取内容，还能根据用户的反馈记录寻找高质量的历史问答（query，answer）作为召回路径。例如，如果用户曾对某个关于“深度学习”的回答给予正面反馈，这对问答结果也会进入 RAG 的索引当中，并作为单独的一路 RAG 索引输入，确保用户获取高质量的信息。这一过程将用户的问答结果纳入 RAG 的闭环，不仅提高了内容的相关性，也使得系统逐步适应用户的需求。

这一机制还体现了 **少量示例学习**（few-shot learning）的核心能力，即通过少量的反馈样本，逐步优化系统的输出。由于 RAG 系统无需大量反馈数据即可调整模型行为，即使在初期反馈有限的情况下，系统也能迅速根据用户偏好作出调整。例如，若用户只提供了几条关于特定主题的反馈，系统依然能够利用这些信息调整相关内容的生成策略。

这样的结构确保了系统在检索和生成内容时优先展示来自高质量集合的信息，从而提升用户满意度和系统整体效能。同时，普通和低质量的内容可在后续阶段审查，以决定是否需要改进或从系统中移除。通过动态反馈与调整机制，RAG 系统能够不断优化性能，提供更加贴合用户需求的输出。

## 未获得明确反馈情况的优化

这里我们再来讨论最后一个问题，也是 LLaMA 3 最关键的一个能力。那就是在用户不主动点击“赞”或“踩”的情况下，系统仍然需要收集反馈数据，以便不断优化内容生成。这时，LLaMA 3 就可以发挥作用。我们可以将用户和系统的历史对话输入 LLaMA 3，让其通过分析对话的语境和用户的反应，判断用户对回答的满意度。

- **判断满意度**：LLaMA 3 可以通过自然语言处理技术，分析用户的表达方式、询问的语气以及其他潜在的情感线索，来推断用户是否对生成的内容感到满意。

- **补全反馈数据**：根据 LLaMA 3 的判断，系统可以自动补全反馈数据，标记用户可能的“赞”或“踩”。例如，如果用户在后续对话中表现出困惑或提问的意图，系统可能会将该回答标记为负向反馈；反之，如果用户表示满意或继续深入讨论，系统可以将其标记为正向反馈。


通过这一机制，RAG 系统能够在动态场景中自我调整，增强对用户满意度的敏感性。例如，当用户未提供明确反馈时，系统依然能利用 LLaMA 3 的分析结果补全反馈数据，从而提升整体用户体验。

## 小结

学到这里，我们来做个总结吧。在这一讲中，我们讨论了当模型的历史知识与检索增强生成（RAG）提供的实时信息发生冲突时，模型通常会优先参考提示词中的内容。这一优先机制虽然能提升生成内容的相关性，但也带来了确保信息准确性的挑战。

为了解决这一问题，RAG 系统应明确展示信息来源，以增强内容的可信度。此外，允许用户对生成内容提供反馈，可以帮助系统动态调整生成策略，确保高质量信息的优先出现。通过少量示例学习，系统能够利用用户反馈来优化输出，进一步提高内容的相关性。

最后，我们学习了如何通过 LLaMA 3 分析历史对话，自动推断用户的满意度，从而补全反馈数据，确保内容生成的持续优化。通过这些策略，优化RAG系统的在线检索效果，以确保生成内容的准确性和时效性。

## 思考题

1. 当模型预训练所习得的知识和 RAG 注入的新知识冲突时，模型会优先使用哪个知识？

2. 如何判断模型预训练学习的知识和后期注入的知识有冲突？


欢迎你把思考后的结果分享到留言区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！