> 本门课程为精品小课，不标配音频

你好，我是常扬。

本节课将深入探讨RAG索引（Indexing）流程中的 **分块（Chunking）策略和嵌入（Embedding）技术。**

文档数据（Documents）经过解析后，通过分块技术将信息内容划分为适当大小的文档片段（chunks），从而使RAG系统能够高效处理和精准检索这些片段信息。分块的本质在于依据一定逻辑或语义原则，将较长文本拆解为更小的单元。分块策略有多种，各有侧重， **选择适合特定场景的分块策略** 是提升RAG系统召回率的关键。

嵌入模型（Embedding Model）负责将文本数据映射到高维向量空间中，将输入的文档片段转换为对应的嵌入向量（embedding vectors）。这些向量捕捉了文本的语义信息，并被存储在向量库（VectorStore）中，以便后续检索使用。用户查询（Query）同样通过嵌入模型的处理生成查询嵌入向量，这些向量用于在向量数据库中通过向量检索（Vector Retrieval）匹配最相似的文档片段。根据不同的场景需求， **评估并选择最优的嵌入模型**，以确保RAG的检索性能符合要求。

![图片](https://static001.geekbang.org/resource/image/c2/d0/c2eea144d5e3ffd46fb18fe11fb069d0.jpg?wh=1920x1603)

## 为什么说分块很重要？

文档通常包含丰富的上下文信息和复杂的语义结构，通过将文档分块，模型可以更有效地提取关键信息，并减少不相关内容的干扰。分块的目标在于确保每个片段在 **保留核心语义** 的同时，具备 **相对独立的语义完整性**，从而使模型在处理时不必依赖广泛的上下文信息， **增强检索召回的准确性**。

分块的重要性在于它直接影响RAG系统的生成质量。首先，合理的分块能够确保检索到的片段与用户查询 **信息高度匹配**，避免信息冗余或丢失。其次，分块有助于提升 **生成内容的连贯性**，精心设计的独立语义片段可以降低模型对上下文的依赖，从而增强生成的逻辑性与一致性。最后，分块策略的选择还会影响系统的 **响应速度与效率**，模型能够更快、更准确地处理和生成内容。

分块策略最大的挑战在于 **确定分块的大小**。如果片段过大，可能导致向量无法精确捕捉内容的特定细节并且计算成本增加；若片段过小，则可能丢失上下文信息，导致句子碎片化和语义不连贯。较小的块适用于需要细粒度分析的任务，例如情感分析，能够精确捕捉特定短语或句子的细节。更大的块则更为合适需要保留更广泛上下文的场景，例如文档摘要或主题检测。因此，块大小的确定必须在计算效率和上下文信息之间取得平衡。

![图片](https://static001.geekbang.org/resource/image/12/88/12ab6af24cc2eb16185e127e90440a88.jpg?wh=1920x1019)

## 分块策略

最佳的分块策略取决于具体的应用场景，而非行业内的统一标准。 **根据场景中文档内容的特点和查询问题的需求，选择最合适该场景的分块策略，以确保RAG系统中大模型能够更精确地处理和检索数据**。

多种分块策略从本质上来看，由以下三个关键组成部分构成：

1. **大小**：每个文档块所允许的最大字符数。
2. **重叠**：在相邻数据块之间，重叠字符的数量。
3. **拆分**：通过段落边界、分隔符、标记，或语义边界来确定块边界的位置。

上述三个组成部分共同决定了分块策略的特性及其适用场景。基于这些组成部分，常见的分块策略包括： **固定大小分块（Fixed Size Chunking）**、 **重叠分块（Overlap Chunking）**、 **递归分块（Recursive Chunking）**、 **文档特定分块（Document Specific Chunking）**、 **语义分块（Semantic Chunking）**、 **混合分块（Mix Chunking）**。下面我将对这些策略逐一进行介绍。

![图片](https://static001.geekbang.org/resource/image/63/ef/63b052c1b1639bfa66c23342cf28d9ef.jpg?wh=1920x1206)

### **固定大小分块（Fixed Size Chunking）**

最基本的方法是将文档按固定大小进行分块，通常作为 **分块策略的基准线** 使用。

Chunk Size 100字符（每种颜色为一个文本块，Chunk切分可视化呈现链接： [https://chunkviz.up.railway.app/](https://chunkviz.up.railway.app/)）

![图片](https://static001.geekbang.org/resource/image/6y/bb/6yy324332a63ab8cf344d9f350fc27bb.png?wh=1315x725)

Chunk Size 50字符

![图片](https://static001.geekbang.org/resource/image/3f/df/3f02a46f4e84ac280d1525749d3b48df.png?wh=1278x475)

**适用场景**

1. 作为分块策略的基准线；
2. 对大型数据集进行初步分析；
3. 实现简单且可预测性高，分块便于管理；
4. 适用于格式和大小相似的同质数据集，如新闻文章或博客文章。

**问题**

1. 不考虑内容上下文，可能在句子或段落中断内容，导致无意义的文本块，例如上面图示中的“大模/型”“边际成/本”等词组被中断；
2. 缺乏灵活性，无法适应文本的自然结构。

### **重叠分块（Overlap Chunking）**

通过滑动窗口技术切分文本块，使新文本块与前一个块的内容部分重叠，从而保留块边界处的重要上下文信息，增强系统的语义相关性。虽然这种方法增加了存储需求和冗余信息，但它有效避免了在块之间丢失关键语义或句法结构。

Chunk Size 100字符，Chunk overlap 20字符（绿色）

![图片](https://static001.geekbang.org/resource/image/47/74/47081fa325055a09af84b373408b7b74.png?wh=1326x474)

**适用场景**

1. 需要深入理解语义并保持上下文完整性的文档，如法律文档、技术手册或科研论文；
2. 提升分块内容的连贯性，以提高分析质量。

**问题**

1. 计算复杂度增加，处理效率降低；
2. 冗余信息的存储和管理成为负担。

### **递归分块（Recursive Chunking）**

通过预定义的文本分隔符（如换行符\\n\\n、\\n ，句号、逗号、感叹号、空格等）迭代地将文本分解为更小的块，以实现段大小的均匀性和语义完整性。此过程中，文本首先按较大的逻辑单元分割（如段落 \\n\\n），然后逐步递归到较小单元（如句子 \\n 和单词），确保在分块大小限制内保留最强的语义片段。

Chunk Size 100字符

![图片](https://static001.geekbang.org/resource/image/7d/12/7d544182c5a87899d214096f46a87912.png?wh=1278x472)

这种方法适用于需要逐层分析的文本文档或需要分解成长片段、长段落的长文档，如研究报告、法律文档等。不过仍有可能在块边界处模糊语义，容易将完整的语义单元切分开。

### **文档特定分块（Document Specific Chunking）**

根据文档的格式（如Markdown、Latex、或编程语言如Python等）进行定制化分割的技术。此方法依据文档的特定格式和结构规则，例如Markdown的标题、列表项，或Python代码中的函数和类定义等，来确定分块边界。通过这种方式，确保分块能够准确反映文档的格式特点，优化保留这些语义完整的单元，提升后续的处理和分析效果。

Chunk Size 100字符，Markdown特定分块

![图片](https://static001.geekbang.org/resource/image/4b/e3/4bb487bea5e25511d71cc2e7cd8e1de3.png?wh=1291x416)

Chunk Size 100字符，Python特定分块

![图片](https://static001.geekbang.org/resource/image/b0/2a/b0e4135a497a5cf06b9e986b68b2132a.png?wh=1281x508)

这种方法可以根据特定的文档结构，进行准确的语义内容切分，在编程语言、Markdown、Latex等结构文档中表现出色。但文档特定分块的方式格式依赖性强，不同格式之间的分块策略不通用，并且无法处理格式不规范及混合多种格式的情况。

### **语义分块（Semantic Chunking）**

基于文本的自然语言边界（如句子、段落或主题中断）进行分段的技术，需要使用NLP技术根据语义分词分句，旨在确保每个分块都包含语义连贯的信息单元。语义分块保留了较高的上下文保留，并确保每个块都包含连贯的信息，但需要更多的计算资源。常用的分块策略有spaCy 和 NLTK 的NLP库，spaCy 适用于需要高效、精准语义切分的大规模文本处理，NLTK更适合教学、研究和需要灵活自定义的语义切分任务。

spaCy语义分块

![图片](https://static001.geekbang.org/resource/image/95/cf/95687f417dyy2f92ab7c9ca374619acf.png?wh=1909x325)

**适用场景**

1. 确保每个文档块的信息完整且语义连贯；
2. 提高检索结果的相关性和准确性；
3. 适用于复杂文档和上下文敏感的精细化分析。

**问题**

1. 需要额外的高计算资源，特别是在处理大型或动态变化的文档数据时；
2. 处理效率降低。

### **混合分块（Mix Chunking）**

混合分块是一种结合多种分块方法的技术，通过综合利用不同分块技术的优势，提高分块的精准性和效率。例如，在初始阶段使用固定长度分块快速整理大量文档，而在后续阶段使用语义分块进行更精细的分类和主题提取。根据实际业务场景，设计多种分块策略的混合，能够灵活适应各种需求，提供更强大的分块方案。

**适用场景**

1. 适用于多层次的精细化分块场景；
2. 数据集动态变化，包含多种文档格式与结构；
3. 平衡处理速度与准确性的场景。

**问题**

1. 实现复杂度高；
2. 策略调优难度高；
3. 资源消耗增加。

## 分块策略实战

LangChain 提供了多种文档分块方法（Text Splitters），帮助开发者轻松集成使用。上述分块策略在 **langchain\_text\_splitters** 库中对应的具体方法类如下：

![图片](https://static001.geekbang.org/resource/image/72/6f/72fb7d398cf2e1d5d50024d0c0e8386f.png?wh=1836x1396)

除了上述方法类外，LangChain 还提供了更多的 Text Splitter，参考 [LangChain 官网](https://python.langchain.com/v0.2/api_reference/text_splitters/index.html)。

关于开发环境以及 `langchain` 和 `langchain_community` 等库的安装和配置，已在第 02 课中详细说明。下面实战的代码更新在Gitee托管项目的 **rag\_app\_lesson4.py** 代码文件中，rag\_app\_lesson4.py 代码基于第03讲中的 rag\_app\_lesson3.py 进行迭代更新。

SpacyTextSplitter 和 NLTKTextSplitter 需要额外安装 Python 依赖库，其中 SpacyTextSplitter 还需要按照文档的语言对应安装额外的语言模型。

**命令行中执行以下安装命令：**

```plain
source rag_env/bin/activate  # 激活虚拟环境
pip install spacy nltk -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m spacy download zh_core_web_sm # 如果需要进行中文分块，安装spacy中文语言模型
python -m spacy download en_core_web_sm # 如果需要进行英文分块，安装spacy英文语言模型

```

**导入langchain.text\_splitter中各种文档分块类代码：**

```plain
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter,
    LatexTextSplitter,
    SpacyTextSplitter,
    NLTKTextSplitter
) # 从 langchain.text_splitter 模块中导入各种文档分块类

```

CharacterTextSplitter、RecursiveCharacterTextSplitter、MarkdownTextSplitter、PythonCodeTextSplitter、LatexTextSplitter、NLTKTextSplitter替换原有text\_splitter参数的赋值类即可。需要额外处理的是SpacyTextSplitter，需要参数pipeline指定具体的语言模型才可以运行。

**indexing\_process方法中切分文本块库代码：**

```plain
# 配置SpacyTextSplitter分割文本块库
#text_splitter = SpacyTextSplitter(
#    chunk_size=512, chunk_overlap=128, pipeline="zh_core_web_sm")

# 配置RecursiveCharacterTextSplitter分割文本块
# 可以更换为CharacterTextSplitter、MarkdownTextSplitter、PythonCodeTextSplitter、LatexTextSplitter、NLTKTextSplitter等
text_splitter = RecursiveCharacterTextSplitter(
chunk_size=512, chunk_overlap=128)

```

其中，SpacyTextSplitter 的文本分块逻辑已被注释。如果需要使用，只需取消注释，并将下方使用其他文本分块库的代码注释即可。

## 什么是Embedding嵌入？

**Embedding 嵌入** 是指将文本、图像、音频、视频等形式的信息映射为高维空间中的密集向量表示。这些向量在语义空间中起到坐标的作用，捕捉对象之间的语义关系和隐含的意义。通过在向量空间中进行计算（例如余弦相似度），可以量化和衡量这些对象之间的 **语义相似性**。

在具体实现中，嵌入的每个维度通常对应文本的某种特征，例如性别、类别、数量等。通过多维度的数值表示，计算机能够理解并解析文本的复杂语义结构。例如，“man”和“woman”在描述性别维度上具有相似性，而“king”和“queen”则在性别和王室身份等维度上表现出相似的语义特征。

向量是一组在高维空间中定义点的数值数组，而嵌入则是将信息（如文本）转化为这种向量表示的过程。这些向量能够捕捉数据的语义及其他重要特征，使得语义相近的对象在向量空间中彼此邻近，而语义相异的对象则相距较远。 **向量检索（Vector Retrieval）** 是一种基于向量表示的搜索技术，通过计算查询向量与已知文本向量的相似度来识别最相关的文本数据。向量检索的高效性在于，它能在大规模数据集中快速、准确地找到与查询最相关的内容，这得益于向量表示中蕴含的丰富语义信息。

![图片](https://static001.geekbang.org/resource/image/60/09/60d4d55a2c7d16d42e255e19038eb409.jpg?wh=1920x1080)

## Embedding Model 嵌入模型

自 2013 年以来，word2vec、GloVe、fastText 等嵌入模型通过分析大量文本数据，学习得出单词的嵌入向量。近年来，随着 transformer 模型的突破，嵌入技术以惊人的速度发展。BERT、RoBERTa、ELECTRA 等模型将词嵌入推进到上下文敏感的阶段。这些模型在为文本中的每个单词生成嵌入时，会充分考虑其上下文环境，因此同一个单词在不同语境下的嵌入向量可以有所不同，从而大大提升了模型理解复杂语言结构的能力。

在 RAG 系统中， **Embedding Model 嵌入模型** 扮演着关键角色，负责将文本数据映射到高维向量空间，以便高效检索和处理。具体而言，Embedding Model 将输入的 **文档片段（Chunks）和查询文本（Query）转换为嵌入向量（Vectors）**，这些向量捕捉了文本的语义信息，并可在向量空间中与其他嵌入向量进行比较。

在 RAG 流程中，文档首先被分割成多个片段，每个片段随后通过 Embedding Model 进行嵌入处理。生成的文档嵌入向量被存储在 VectorStore 中，供后续检索使用。用户查询会通过 Embedding Model 转换为查询嵌入向量，这些向量用于在向量数据库中匹配最相似的文档片段，最终组合生成 **指令（Prompt）**，大模型生成回答。

![图片](https://static001.geekbang.org/resource/image/77/4c/7714f94f54d754cc6d45dd4a63b8494c.jpg?wh=1920x1080)

正如图中所示，嵌入模型是 RAG 流程的核心。既然如此重要，市面上有非常多的嵌入模型，我们该如何为我们的业务场景选择最合适的嵌入模型呢？

## **Embedding Model 嵌入模型评估**

在选择适合的嵌入模型时，需要综合考虑多个因素，包括 **特定领域的适用性**、 **检索精度**、 **支持的语言**、 **文本块长度**、 **模型大小** 以及 **检索效率** 等因素。同时以广泛受到认可的 **MTEB**（Massive Text Embedding Benchmark）和 **C-MTEB**（Chinese Massive Text Embedding Benchmark）榜单作为参考，通过涵盖分类、聚类、语义文本相似性、重排序和检索等多个数据集的评测，开发者可以根据不同任务的需求，评估并选择最优的向量模型，以确保在特定应用场景中的最佳性能。

![图片](https://static001.geekbang.org/resource/image/f6/d4/f670a0df1b78f0891bd8fb63f17f9dd4.jpg?wh=1920x1122)

[MTEB & C-MTEB榜单](https://huggingface.co/spaces/mteb/leaderboard)

![图片](https://static001.geekbang.org/resource/image/6a/f8/6a330f2f96a08d147523fbc91d3e0ef8.png?wh=1920x1140)

榜单每日更新，上图展示的是2024年8月28日的榜单。点击“Overall”，切换语言为Chinese，可以看到中文嵌入模型的排名。由于 RAG 是一项检索任务，我们需要按“ **Retrieval Average**”（检索平均值）列对排行榜进行排序，图中显示的就是检索任务效果排序后的结果。在检索任务中，我们需要在榜单顶部看到最佳的检索模型，并且专注于以下几个关键列：

- **Retrieval Average 检索平均值：** 较高的检索平均值表示模型更擅长在检索结果列表中将相关项目排在较高的位置，检索效果更好。
- **Model Size 模型大小：** 模型的大小（以 GB 为单位）。虽然检索性能随模型大小而变化，但要注意，模型大小也会对延迟产生直接影响。因此，在选择模型时，建议筛选掉那些在硬件资源有限的情况下不可行的过大模型。在生产环境中，性能与效率之间的权衡尤为重要。
- **Max Tokens 最大Token数：** 可压缩到单个文本块中的最大Token数。因为文档块我们希望不要过大而降低目标信息块的精准度，因此，即使最大 tokens 数为 512 的模型在大部分场景下也足够使用。
- **Embedding Dimensions：** 嵌入向量的维度。越少的嵌入维度提供更快的推理速度，存储效率更高，而更多的维度可以捕获数据中的细微特征。我们需要在模型的性能和效率之间取得良好的权衡。
- **实验至关重要**，在排行榜上表现良好的模型不一定在你的任务上表现良好，试验各种高得分的模型至关重要。我们参考 MTEB 排行榜，选择多个适合我们场景的嵌入模型作为备选，并在我们的业务场景数据集上进行评估测试，以选出最适合我们 RAG 系统的嵌入模型。

## Embedding Model 技术实战

我们使用 **SentenceTransformers** 作为加载嵌入模型的 Python 模块。

SentenceTransformers（又名 SBERT）是一个用于训练和推理文本嵌入模型的 Python 模块，可以在 RAG 系统中计算嵌入向量。使用 SentenceTransformers 进行文本嵌入转换非常简单：只需导入模块库、加载模型，并调用 encode 方法即可。执行时，SentenceTransformers 会自动下载相应的模型库，当然也可以手动下载并指定模型库的路径。所有可用的模型都可以在 [SentenceTransformers 模型库](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html) 查看，超过8000个发布在 Hugging Face 上的嵌入模型库可以被使用。

在中文领域，智源研究院的 [BGE 系列模型](https://huggingface.co/collections/BAAI/bge-66797a74476eb1f085c7446d) 是较为知名的开源嵌入模型，在 C-MTEB 上表现出色。BGE 系列目前包含23个嵌入模型，涵盖多种维度、多种最大 Token 数和模型大小，用户可以根据需求进行测试和使用。

**load\_embedding\_model 方法中使用SentenceTransformer加载嵌入模型代码：**

```plain
# 绝对路径：SentenceTransformer读取绝对路径下的bge-small-zh-v1.5模型，如需使用其他模型，下载其他模型，并且更换绝对路径即可
embedding_model = SentenceTransformer(os.path.abspath('rag_app/bge-small-zh-v1.5'))

# 自动下载：SentenceTransformer库自动下载BAAI/bge-large-zh-v1.5模型，如需下载其他模型，输入其他模型名称即可
# embedding_model = SentenceTransformer('BAAI/bge-large-zh-v1.5')

```

**indexing\_process 方法中将文本转化为嵌入向量代码：**

```plain
# 文本块转化为嵌入向量列表，normalize_embeddings表示对嵌入向量进行归一化，用于后续流程准确计算向量相似度
embeddings = []
for chunk in all_chunks:
      embedding = embedding_model.encode(chunk, normalize_embeddings=True)
      embeddings.append(embedding)

```

## 总结

这节课我们深入探讨了RAG索引流程中的分块策略和嵌入技术。

**分块策略** 通过将文档拆分为更小的片段，使模型能更高效地处理和检索信息，确保每个片段在保留核心语义的同时，具备相对独立的语义完整性。常见的分块策略包括 **固定大小分块**、 **重叠分块**、 **递归分块**、 **文档特定分块**、 **语义分块**、 **混合分块**。分块的关键在于选择 **适合的分块大小** 与 **特定场景的策略**，以优化系统的检索精度和生成内容的连贯性。

**嵌入技术** 将文本数据映射到高维向量空间中，捕捉其语义信息，支持 **向量检索**，从而在大规模数据中快速识别与查询最相关的文档片段。在选择嵌入模型时，需要综合考虑 **特定领域的适用性**、 **检索精度**、 **支持的语言**、 **文本块长度**、 **模型大小** 以及 **检索效率** 等因素。

通过参考 **MTEB** 和 **C-MTEB** 的评测榜单，可以评估多个高得分的模型，并在具体的业务场景中进行测试，最终选择最适合该场景的嵌入模型。同时，使用 SentenceTransformers Python 模块可以简化嵌入模型的加载和嵌入计算，进而高效率集成测试。

相关代码已公开在 [Gitee 代码仓库](https://gitee.com/techleadcy/rag_app) 中了，代码文件为 **rag\_app\_lesson4.py**。

## 思考题

本节课程涵盖了分块策略和嵌入技术两个关键知识点。对应这两个知识点，我给你留两道思考题。

1. 在你的业务场景中，是否曾遇到过因分块策略选择不当而导致检索精度下降的问题？如果有，请分析这个问题，并思考如何通过调整分块策略来优化系统的性能。
2. 在选择嵌入模型时，你如何在模型大小与延迟、精度与效率之间做出权衡？分享你在实际项目中平衡这些因素的经验，或探讨在不同业务场景下的最佳平衡点。

欢迎你把你的经验和思考分享到留言区，和我一起讨论，也欢迎你把这节课的内容分享给需要的朋友，我们下节课再见！