你好，我是Tyler！

从这节课开始，我们正式讨论RAG（检索增强生成）相关的知识，这是当前大模型应用优化中最频繁使用的技术之一。

首先我们来区分一下搜索增强和检索增强，我们前面学习的搜索增强是在模型的推理过程中对不同可能的生成路径进行搜索，以达到最优的生成效果。而 **检索增强则是通过外部知识辅助大语言模型回答复杂问题。**

在检索增强的过程中有一个常见误区，那就是很多人常常对向量数据库过于重视，认为仅依靠“老三样”：文章分割、向量模型和向量数据库，就能够解决检索问题。然而，这种思路虽然有其价值，但如果通过充分利用LLaMA 3的能力，我们能够将索引、检索和内容生成的过程变得更加智能化。在深入探讨之前，首先让我们了解朴素RAG的基本流程。

## 朴素RAG的基本流程

由于我们的课程没有设置RAG的前序知识要求，所以我们首先来看朴素 RAG 的构建过程。朴素RAG（Retrieval-Augmented Generation）的基本流程分为五个主要步骤，分别是文档分割、嵌入生成、向量存储、检索过程和内容生成。以下是相关的代码逻辑分解介绍，文末提供了更紧凑的完整代码示例。

![图片](https://static001.geekbang.org/resource/image/1d/52/1d1c476be5d5d3fd9700a9d26aac0552.png?wh=1342x650)

### 文档分割

文档分割是RAG流程的起点，其目标是将大块的文档拆分成可管理的小片段。分割方式通常基于文本长度、段落、句子结构或者逻辑结构。例如：

- **固定长度分割**：将文档按照字符或词汇数量分割成固定大小的块。

- **逻辑分割**：基于语义或文档的段落、章节等自然分界线，保持片段的逻辑连贯性。


分割文档主要是为了便于后续的嵌入生成和检索。过大或者过小的片段都会影响嵌入质量和检索效果。因此，文档分割时需平衡精度和效率。

```python
from llama_index.core.node_parser import SentenceSplitter

# 使用SentenceSplitter进行文档分割
splitter = SentenceSplitter(chunk_size=256, chunk_overlap=10)
documents = splitter.split(original_document)

```

### 嵌入生成

分割后的文档片段会被输入到预训练的语言模型中（如BERT、RoBERTa等），生成相应的向量表示。此步骤的关键点在于选择适合的嵌入模型，以及优化嵌入质量。

具体过程如下：

- **模型选择**：可以使用各种预训练的Transformer模型，常用的是BERT、DistilBERT、Sentence-BERT等，这些模型能够将文本片段转化为高维稠密向量，捕捉文本的语义信息。

- **嵌入优化**：生成的向量应能很好地表达片段的语义，并与查询向量计算相似度。通常使用对比学习、微调等技术来优化嵌入模型，确保嵌入向量对特定任务有更好的性能。


```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 嵌入模型设置
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
embeddings = embed_model.embed(documents)

```

### 向量存储

生成的嵌入向量会被存储到向量数据库中，这类数据库通常经过优化，可以高效执行向量相似度搜索。

- **向量数据库**：常用的向量数据库有Faiss、Milvus、Pinecone等，它们能够快速执行向量检索。存储时会附带原始的文本片段信息，以便后续结合检索结果生成响应。

- **向量索引**：为了提高检索效率，数据库通常会对向量建立索引。常见的索引方法有倒排索引（Inverted Index）和HNSW（Hierarchical Navigable Small World）等，它们能够在大规模数据中进行高效的向量匹配。


```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

# 向量存储设置
chroma_client = chromadb.EphemeralClient()
chroma_collection = chroma_client.create_collection("ollama")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
vector_store.add_embeddings(embeddings)

```

### 检索过程

当用户提出查询时，系统会将查询转化为查询向量，通过与数据库中的向量进行相似度计算，找到最相关的文档片段。

- **查询嵌入生成**：查询同样会被转化为嵌入向量，使用与文档片段相同的模型，确保向量空间一致。

- **相似度计算**：系统通常使用余弦相似度或欧氏距离等度量方式来计算查询向量与文档片段向量之间的相似性，返回最相似的片段集合。为了减少计算量，向量数据库中的索引机制能有效缩短搜索时间。


```python
# 查询嵌入生成
query_embedding = embed_model.embed(query)

# 相似度计算
results = vector_store.query(query_embedding, top_k=3)

```

### 内容生成

检索到的相关文档片段会与用户的查询一起输入到生成模型中，生成最终的响应内容。

- **生成模型**：生成模型（如GPT、T5等）结合用户查询和相关的文档片段，利用检索到的知识进行回答。这一步有助于生成内容更加丰富且符合上下文语境的响应。

- **输出优化**：为了提高生成的准确性，系统可以采用多轮检索和生成，或者引入重写、总结等技术，使最终输出更加自然流畅。


在掌握了朴素RAG的基本流程后，我们接下来要探讨的是如何通过LLaMA 3提升各个环节的效率和效果，这将是我们本章后续学习的主要内容。

```python
from llama_index.llms.ollama import Ollama
from llama_index.core import PromptTemplate

# 设置生成模型
llm = Ollama(model="llama3")

# 生成响应
qa_template = PromptTemplate(
    "基于提供的上下文：\n"
    "{context_str}\n"
    "请回答以下问题：\n"
    "问题：{query_str}\n\n"
    "答案："
)

response = llm.generate(qa_template.format(context_str=results, query_str=query))
print(response)

```

通过上述流程，朴素 RAG 能够高效地处理信息并生成相应的内容。

## 如何为LLaMA 3构建更强大的RAG系统？

在传统的信息检索中，文档通常只是简单地按长度切分，然后将这些部分转化为向量存入数据库。这种做法虽然简单，却往往会漏掉重要的语义信息，导致用户在查找信息时遇到困难。引入 LLaMA 3 后，这个过程得到了显著改进，特别是通过 **GraphRAG** 和 **提示词压缩** 等技术，进一步提升了系统的性能。

1. 智能索引构建

传统的索引构建方法一般是按照固定的字数来切分内容，缺乏对文档结构和主题的理解。而 LLaMA 3 不仅按字数分段，还能识别文章的基本逻辑。通过 **GraphRAG** 技术，LLaMA 3 能够生成文档的结构化图谱，捕捉文档中各个主题之间的关系。例如，在处理关于 Kubernetes 的技术文档时，LLaMA 3 能够自动将“集群管理”和“容器调度”等主题整理在一起，并生成相应的向量。

这样的智能索引方式提高了信息检索的效率，使用户在查找信息时能够更快定位到所需内容。LLaMA 3 生成的向量不仅包含文本的基本特征，还蕴含丰富的语义信息。

2. 高效的检索系统设计

在设计检索系统时，LLaMA 3 的语义理解能力显得尤为重要。与传统的关键字匹配不同，LLaMA 3 能够理解用户的复杂查询，并根据需求动态调整返回的内容。通过结合 **提示词压缩** 技术，LLaMA 3 能有效减少输入长度，同时保留关键上下文信息，从而提升整个检索过程的流畅性。

例如，当用户询问“如何优化 Kubernetes 集群的性能”时，LLaMA 3 可以进一步询问是想了解资源分配还是负载均衡。这种互动方式不仅增强了信息的相关性，还提升了用户在检索过程中的参与感。

3. 高效的内容生成

在内容生成方面，LLaMA 3 同样表现出色。用户在面对长篇文档时，通常需要花费大量时间提取关键信息。而 LLaMA 3 能够迅速生成简洁的摘要，帮助用户快速抓住重点。结合 **GraphRAG** 的知识图谱特性，LLaMA 3 能够在生成摘要时综合多篇文档的内容，确保信息的全面性和准确性。

如果检索到的内容有些缺失，LLaMA 3 还能智能补全这些部分。比如，当用户询问“容器调度的最佳实践”时，LLaMA 3 能从不同文档中提取相关信息并整合，生成一篇连贯的综述。

总的来说，在使用 LLaMA 3 后，RAG 系统在索引构建、检索和内容生成方面都有了显著提升。通过智能的索引方式和强大的语义理解能力，用户在复杂查询中能够快速找到准确的信息。同时，LLaMA 3 在内容生成上的灵活性，也为用户提供了更加丰富的知识体验。这不仅提升了信息检索的效率，也使 RAG 系统在实际应用中变得更加灵活和实用。结合 **GraphRAG** 和 **提示词压缩** 技术的应用，LLaMA 3 让信息检索系统在处理复杂数据时表现得更加出色。

## 总结

学到这里，我们做个总结吧。我们深入探讨了 RAG在大模型应用中的重要性，尤其是在信息检索和内容生成的过程中。我们认为，依赖传统的向量数据库和文档分割技术已不够充分，而应当充分利用 LLaMA 3 的强大功能，以提升索引、检索和内容生成的智能化程度。

朴素 RAG 的基本流程涵盖几个关键步骤：文档分割、嵌入生成、向量存储、检索和内容生成。在这一过程中，通过合理分割文档、生成高质量的嵌入向量，并将其存储在优化的向量数据库中，可以显著提高检索效率。当用户发出查询时，系统将查询转化为向量，通过计算相似度找到最相关的文档片段，最终生成符合上下文的回复。这些步骤构成了 RAG 的基础框架，帮助用户更有效地获取信息。

引入 LLaMA 3 后，RAG 系统在多个方面有了显著提升。LLaMA 3 不仅能够理解文档结构和用户复杂查询，还能根据上下文动态调整返回的内容。例如，它能够生成简洁的摘要或补全缺失的信息。这种智能化的优化使 RAG 系统在实际应用中变得更加灵活和高效，大幅提升了用户的信息检索体验。

我们可以看到，结合 LLaMA 3 的强大能力，RAG 系统能够在索引、检索和内容生成中实现更高的智能化水平，从而更好地满足用户需求，提升信息获取的便捷性和准确性。在本章的后续内容中，我们将详细展开这些技术的方法和实现。

## 思考题

1. 你了解的RAG方法都有哪些？

2. 你在RAG的处理过程中都遇到过哪些问题？


欢迎你把你的经验分享到留言区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！

## 完整示例

```python
# 导入所需的包
import chromadb
from llama_index.core import PromptTemplate, Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

# 定义文件目录
file_directory = "path/to/your/documents"  # 更新为你的文件路径

# 嵌入模型
llm = Ollama(model="llama3", request_timeout=300.0)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = llm
Settings.embed_model = embed_model

# 从目标文档中设置上下文
documents = SimpleDirectoryReader(input_files=[file_directory]).load_data()
chroma_client = chromadb.EphemeralClient()
chroma_collection = chroma_client.create_collection("ollama")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model,
    transformations=[SentenceSplitter(chunk_size=256, chunk_overlap=10)]
)

# 设置通用的 RAG 提示词模板（中文）
qa_template = PromptTemplate(
    "基于提供的上下文：\n"
    "-----------------------------------------\n"
    "{context_str}\n"
    "-----------------------------------------\n"
    "请回答以下问题：\n"
    "问题：{query_str}\n\n"
    "答案："
)

query_engine = index.as_query_engine(text_qa_template=qa_template, similarity_top_k=3)

# 示例查询
query = "文档的主要发现是什么？"
response = query_engine.query(query)
print(response.response)

```