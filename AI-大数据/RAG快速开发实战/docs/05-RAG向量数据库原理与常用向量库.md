> 本课程为精品小课，不标配音频。

你好，我是常扬。

在前面的课程中，我们已经学习了RAG检索流程中如何将文档数据解析、分块并转换为嵌入向量的操作。本节课将进一步掌握如何存储这些向量及其文档元数据，并高效地进行相似度检索。

![图片](https://static001.geekbang.org/resource/image/91/19/9110ece16990bf06ed1ddb60c9989a19.jpg?wh=1920x572)

在人工智能（AI）主导的时代，文字、图像、语音、视频等多模态数据的复杂性显著增加。由于这些数据具有非结构化和多维特征，向量表示能够有效表示语义和捕捉其潜在的语义关系，促使向量数据库成为存储、检索和分析高维数据向量的关键工具。

下图展示了向量数据库的分类，依据是否开源与是否为专用向量数据库，将其分为四类。

1. 第一类是 **开源的专用向量数据库**，如 Chroma、Vespa、LanceDB、Marqo、Qdrant 和 Milvus，这些数据库专门设计用于处理向量数据。
2. 第二类是 **支持向量搜索的开源数据库**，如 OpenSearch、PostgreSQL、ClickHouse 和 Cassandra，它们是常规数据库，但支持向量搜索功能。
3. 第三类是 **商用的专用向量数据库**，如Weaviate和Pinecone，它们专门用于处理向量数据，但属于商业产品或通过商业许可获得源码。
4. 第四类是 **支持向量搜索的商用数据库**，如Elasticsearch、Redis、Rockset和SingleStore，这些常规数据库支持向量搜索功能，同时属于商业产品或可通过商业许可获得源码。

![图片](https://static001.geekbang.org/resource/image/21/90/21ef69a6c3fcd37d4154a206c774f890.jpg?wh=1920x1207)

## 为什么需要向量数据库？

![图片](https://static001.geekbang.org/resource/image/19/0c/19b0e3823b4b9158de7eb11cebac630c.jpg?wh=1920x758)

传统数据库通常分为关系型（SQL）数据库和非关系型（NoSQL）数据库，其中存储复杂、非结构化或半结构化信息的需求主要依赖于非关系型数据库的能力。图中展示了三种非关系型数据库类型与向量数据库：

1. **键值数据库（Key-Value）**：通常用于简单的数据存储，通过键来快速访问数据。
2. **文档数据库（Document）**：用于存储文档结构的数据，如JSON格式。
3. **图数据库（Graph）**：用于表示和存储复杂的关系数据，常用于社交网络、推荐等场景。
4. **向量数据库（Vector）**：用于存储和检索基于向量表示的数据，用于AI模型的高维度和复杂的嵌入向量。

那在什么场景下该选择什么样的数据库呢？举个例子，如果你想要找到一本特定的书，只需通过书名来 **精准定位信息**，键值数据库是最理想的选择。而如果你需要查询一本书的详细章节内容、作者简介等 **复杂的结构化信息**，文档数据库则更为适用。

如果你的目标是了解书籍之间的推荐关系，或者探索作者之间的合作网络，图数据库可以高效存储和查询这些 **复杂的关系数据**。最后，如果你希望找到与某本书内容相似的书籍，比如基于主题、风格等特征进行相似性搜索，向量数据库则能够通过计算书籍内容语义在向量空间中的距离，为你提供 **语义最相关的数据信息**。

**向量数据库的核心在于其能够基于向量之间的相似性，快速、精确地定位和检索数据**。这类数据库不仅为向量嵌入提供了优化的存储和查询功能，同时也继承了传统数据库的诸多优势，如 **性能、可扩展性和灵活性**，满足了充分利用大规模数据的需求。相比之下，传统的基于标量的数据库由于无法应对数据复杂性和规模化处理的挑战，难以有效提取洞察并实现实时分析。

向量数据库的主要优势体现在以下几个方面：

1. **数据管理**：向量数据库提供了易于使用的数据存储功能，如插入、删除和更新操作。与独立的向量索引工具（如 Faiss）相比，这使得向量数据的管理和维护更加简便，因为 Faiss 需要额外的工作才能与存储解决方案集成。
2. **元数据存储和筛选**：向量数据库能够存储与每个向量条目关联的元数据，用户可以基于这些元数据进行更细粒度的查询，从而提升查询的精确度和灵活性。
3. **可扩展性**：向量数据库设计旨在应对不断增长的数据量和用户需求，支持分布式和并行处理，并通过无服务器架构优化大规模场景下的成本。
4. **实时更新**：向量数据库通常支持实时数据更新，允许动态修改数据以确保检索结果的时效性和准确性。
5. **备份与恢复**：向量数据库具备完善的备份机制，能够处理数据库中所有数据的例行备份操作，确保数据的安全性与持久性。
6. **生态系统集成**：向量数据库能够与数据处理生态系统中的其他组件（如 ETL 管道中的 Spark、分析工具如 Tableau 和 Segment、可视化平台如 Grafana）轻松集成，从而简化数据管理工作流程。此外，它还能够无缝集成AI相关工具，如 LangChain、LlamaIndex 和 Cohere，进一步增强其应用潜力。
7. **数据安全与访问控制**：向量数据库通常提供内置的数据安全功能和访问控制机制，以保护敏感信息。通过命名空间实现的多租户管理，允许用户对索引进行完全分区，甚至可以在各自的索引中创建完全隔离的分区，确保数据的安全性和访问的灵活性。

由于其上述特性，向量数据库可以广泛应用于LLM RAG系统、推荐系统、异常检测、计算机视觉、自然语言处理等多种AI产品生产场景中。

综上所述， **向量数据库是一类专门为生产场景下的向量嵌入管理而构建的数据库**。与传统的基于标量的数据库及独立的向量索引相比，向量数据库在性能、可扩展性、安全性和生态系统集成等方面展现了显著的优势，为现代数据管理提供了强有力的支持。

## 向量数据库是如何工作的？

向量数据库是一种专门用于 **存储和检索多维向量的数据库类型**，与传统的基于行列结构的数据库不同，它主要处理高维空间中的数据点。传统数据库通常处理字符串、数字等标量数据，并通过精确匹配来查询数据。然而，向量数据库的操作逻辑则是基于相似性搜索，即在查询时，应用特定的相似性度量（如余弦相似度、欧几里得距离等）来查找与查询向量最相似的向量。

向量数据库的核心在于其 **高效的索引和搜索机制**。为了优化查询性能，它采用了如哈希、量化和基于图形的多种算法。这些算法通过构建如层次化可导航小世界（HNSW）图、产品量化（PQ）和位置敏感哈希（LSH）等索引结构，显著提升了查询速度。这种搜索过程并非追求绝对精确，而是通过近似最近邻（ANN）算法在速度与准确性之间进行权衡，从而实现快速响应。

向量数据库的索引结构可以理解为一种预处理步骤，类似于为图书馆中的书籍编制索引，方便快速找到所需内容。HNSW图通过在多层结构中将相似向量连接在一起，快速缩小搜索范围。PQ则通过压缩高维向量，减少内存占用并加速检索，而LSH则通过哈希函数将相似向量聚集在一起，便于快速定位。

向量数据库的搜索机制不是追求精确匹配，而是通过近似最近邻（ANN）算法在速度与准确性之间找到最佳平衡。ANN算法通过允许一定程度的误差，在显著提高搜索速度的同时，依然能够找到与查询相似度较高的向量。这种策略对于需要实时、高精度响应的应用场景尤为重要。

**向量数据库的工作流程涵盖了从数据处理、向量化、向量存储、向量索引到最终检索的全链条操作**，确保在复杂的数据环境中实现高效的存储、索引和相似性搜索。具体流程如下：

![图片](https://static001.geekbang.org/resource/image/01/09/01af1033b844ce52d46878a263ef2209.jpg?wh=1920x498)

1. **数据处理与向量化** 原始数据首先被处理并转化为向量嵌入。这一步通过嵌入模型实现，模型利用深度学习算法提取数据的语义特征，生成适合后续处理的高维向量表示。
2. **向量存储** 转化后的向量嵌入存储在数据库中。这一环节确保数据在高效检索的同时，能够以优化的方式管理和维护存储资源，以适应不同规模和复杂度的应用需求。
3. **向量索引** 存储的向量嵌入需要经过索引处理，以便在后续查询中快速定位相关数据。索引过程通过构建特定的结构，使得数据库能够在大规模数据集上实现高效的查询响应。
4. **向量搜索** 在接收到查询后，数据库通过已建立的索引结构执行相似性搜索，找出与查询向量最为接近的数据点。这一阶段的重点在于平衡搜索的速度与准确性，确保在大数据环境下提供快速且相关的查询结果。常见的向量搜索方法包括余弦相似度、欧几里得距离和曼哈顿距离。其中， **余弦相似度主要用于文本处理和信息检索**，关注向量之间的角度，以捕捉语义相似性；欧几里得距离则测量向量之间的实际距离，适用于密集特征集的聚类或分类；而曼哈顿距离则通过计算笛卡尔坐标中的绝对差值之和，适用于稀疏数据的处理。
5. **数据检索** 最后，数据库从匹配的向量中检索出对应的原始数据，并根据特定的需求进行必要的后处理。这一步骤确保最终结果能够准确反映用户的查询意图，并提供有意义的输出。

在RAG系统中，向量数据库起着重要的作用。其主要功能在于索引过程中，建立 **高效的向量索引结构**，以便快速定位与查询相关的向量数据。在查询阶段，系统将输入的提示转化为向量表示形式，并从数据库中 **检索出与之最相关的向量及其对应的分块数据**。通过这种索引和检索机制，检索到的向量为生成模型提供了必要的上下文信息，使模型能够依据当前的语义上下文生成更加精准和相关的响应。

![图片](https://static001.geekbang.org/resource/image/90/d6/90a727190bb09d4910d769396f141bd6.jpg?wh=1920x821)

## 常用向量数据库

下面列出十个目前主流的向量数据库，展示其数据库链接、介绍、优点与缺点。根据开发者具体的使用场景和技术需求，选择最适合的向量数据库解决方案是关键。

![图片](https://static001.geekbang.org/resource/image/c2/cc/c27b4yy6748a414dae0c679835a1eccc.jpg?wh=1920x1197)

根据上面所示特点，对于需要快速开发和轻量化部署的项目，Chroma、Qdrant 是不错的选择。而对于追求高性能和可扩展性的企业级应用，可以考虑 Milvus/Zilliz。FAISS 是适合对性能有极致要求、不要求持久化和数据管理的场景。Weaviate、LanceDB 在处理多模态数据方面表现突出，适用于需要管理多种数据类型（如图像、文本、音频等）的 AI 应用。如果需要无缝集成现有数据库并进行向量搜索，PGVector、Elasticsearch、Redis 是理想的方案。而不希望管理基础设施的用户则可以选择 Pinecone 这样的全托管服务。

## 向量数据库实战

在实战中，我们使用 **Chroma** 作为 RAG 项目的向量库，以替代原先无法持久化的 Faiss 库。

Chroma 是一种简单且易于持久化的向量数据库，它以 **轻量级、开箱即用** 的特性著称。Chroma 支持内存中操作和磁盘持久化，能够高效地管理和查询向量数据，非常适合快速集成和开发。其设计简洁且不需要复杂的配置，使开发者能够专注于核心功能的实现而无需担心底层存储的复杂性。

随着我们课程的深入，代码量和注释量逐渐增加。为了更加专注于当前课程，从这节课起，将不再保留前几课中的代码注释和扩展。代码中的注释将仅标注与这节课需要学习和掌握的内容。同时，开发环境将完整地展示在这节课的实战内容中，无需依赖之前课程的内容来追溯配置，实现单课时中即可运行的依赖库安装和代码。本课程的代码文件为 **rag\_app\_lesson5.py**。

下载本课程对应的 Gitee 上托管项目，若已下载，则需进入 rag\_app 文件夹中执行 git pull 命令，拉取最新代码：

```plain
git clone https://gitee.com/techleadcy/rag_app.git

```

创建并激活虚拟环境，若已创建则无需重复执行：

```plain
python3 -m venv rag_env

```

命令行中拉取仓库的最新代码，执行依赖库安装命令，本课时对应的是 ChromaDB 库：

```plain
source rag_env/bin/activate
pip install -U pip chromadb langchain langchain_community sentence-transformers dashscope unstructured pdfplumber python-docx python-pptx markdown openpyxl pandas -i https://pypi.tuna.tsinghua.edu.cn/simple

```

代码中设置大模型qwen\_model，qwen\_api\_key参数，访问 [阿里云百炼大模型服务平台](https://www.aliyun.com/product/bailian) 获得。

执行课程代码：

```plain
python rag_app/rag_app_lesson5.py

```

课程涉及的代码改动均已在 **rag\_app\_lesson5.py** 文件中添加详细注释，主要包括以下内容：

1. 引入 Chroma 向量数据库 **chromadb**，引入 uuid 模块用于为每个文本块生成唯一的 ID。
2. 在 main 方法中，创建了 Chroma 本地存储实例 client 和存储集合 collection，实例数据库存储在相对路径 **rag\_app/chroma\_db** 下，数据存储在 **documents** 集合中。
3. 在 indexing\_process 方法中，将文档切块后的文本块的 ID、嵌入向量和原始文本块内容存储到 ChromaDB 的 documents 集合中。
4. 在 retrieval\_process 方法中，使用 Chroma 向量数据库检索与查询（query）最相似的 top\_k 个文本块。

具体代码改动如下：

引入依赖库：

```plain
import chromadb # 引入 Chroma 向量数据库
import uuid # 生成唯一ID
import shutil # 文件操作模块，为了避免既往数据的干扰，在每次启动时清空 ChromaDB 存储目录中的文件

```

main方法：

```plain
def main():
    print("RAG过程开始.")

    # 为了避免既往数据的干扰，在每次启动时清空 ChromaDB 存储目录中的文件
    chroma_db_path = os.path.abspath("rag_app/chroma_db")
    if os.path.exists(chroma_db_path):
        shutil.rmtree(chroma_db_path)

    # 创建ChromaDB本地存储实例和collection
    client = chromadb.PersistentClient(chroma_db_path)
    collection = client.get_or_create_collection(name="documents")
    embedding_model = load_embedding_model()

    indexing_process('rag_app/data_lesson3', embedding_model, collection)
    query = "下面报告中涉及了哪几个行业的案例以及总结各自面临的挑战？"
    retrieval_chunks = retrieval_process(query, collection, embedding_model)
    generate_process(query, retrieval_chunks)
    print("RAG过程结束.")

```

indexing\_process方法：

```plain
def indexing_process(folder_path, embedding_model, collection):
    all_chunks = []
    all_ids = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            document_text = load_document(file_path)
            if document_text:
                print(f"文档 {filename} 的总字符数: {len(document_text)}")

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
                chunks = text_splitter.split_text(document_text)
                print(f"文档 {filename} 分割的文本Chunk数量: {len(chunks)}")

                all_chunks.extend(chunks)
                # 生成每个文本块对应的唯一ID
                all_ids.extend([str(uuid.uuid4()) for _ in range(len(chunks))])

    embeddings = [embedding_model.encode(chunk, normalize_embeddings=True).tolist() for chunk in all_chunks]

    # 将文本块的ID、嵌入向量和原始文本块内容添加到ChromaDB的collection中
    collection.add(ids=all_ids, embeddings=embeddings, documents=all_chunks)
    print("嵌入生成完成，向量数据库存储完成.")
    print("索引过程完成.")
    print("********************************************************")

```

retrieval\_process方法：

```plain
def retrieval_process(query, collection, embedding_model=None, top_k=6):
    query_embedding = embedding_model.encode(query, normalize_embeddings=True).tolist()

    # 使用向量数据库检索与query最相似的top_k个文本块
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    print(f"查询语句: {query}")
    print(f"最相似的前{top_k}个文本块:")

    retrieved_chunks = []
    # 打印检索到的文本块ID、相似度和文本块信息
    for doc_id, doc, score in zip(results['ids'][0], results['documents'][0], results['distances'][0]):
        print(f"文本块ID: {doc_id}")
        print(f"相似度: {score}")
        print(f"文本块信息:\n{doc}\n")
        retrieved_chunks.append(doc)

    print("检索过程完成.")
    print("********************************************************")
    return retrieved_chunks

```

## 总结

本节课讲解了RAG流程中的关键技术组件—— **向量数据库**。内容涵盖了向量数据库的必要性及其工作原理，并列举了常见的数据库选型，最后通过代码实战巩固所学知识。本课程代码已公开在Gitee代码仓库中，链接地址为： [https://gitee.com/techleadcy/rag\_app](https://gitee.com/techleadcy/rag_app)。

1. **向量数据库的必要性**

向量数据库支持基于语义相似性的高效向量检索，同时具备传统数据库的管理、扩展、备份和集成功能，以满足生产环境的需求。

2. **向量数据库的工作原理**

向量数据库通过高效的索引和搜索机制，覆盖数据处理、存储、索引和检索的全流程，在RAG的索引和检索流程中发挥关键作用，实现复杂环境下的快速索引构建与相似搜索。

3. **常用向量数据库**

列举了十种常用的向量数据库，并对其特点进行了分析。Chroma、Qdrant 适合快速开发和轻量化部署，Milvus/Zilliz 适用于高性能和可扩展性需求，FAISS 适合不要求持久化且对性能有极致要求，Weaviate 和LanceDB 在多模态数据处理中表现出色，PGVector、Elasticsearch 和 Redis 则在现有数据库的高效集成中占优势，而 Pinecone 是云托管场景的理想选择。

4. **向量数据库实战**

课程实战部分使用 Chroma 作为 RAG 项目的向量数据库。代码中详细讲解了如何创建 Chroma 实例，如何将文档切块后的文本块存储到 Chroma 数据库中，并通过Chroma 执行相似度检索。

## 思考题

本课程介绍了多种开源和商用的向量数据库。结合你的开发经验，思考一下，在选择技术组件时，你如何看待开源与闭源的选择？在哪些场景下，开源组件可能更为合适，而在什么情况下商用组件更具优势？有哪些关键因素会影响你的决策？期待你把你的想法分享到留言区，如果你觉得这节课的内容对你有帮助的话，也欢迎你分享给其他朋友，我们下节课再见！