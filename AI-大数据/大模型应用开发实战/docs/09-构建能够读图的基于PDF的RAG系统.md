你好，我是黄佳。

在前两节课中，我们探讨了如何利用ChatGPT等大语言模型，通过精心设计的多步骤提示流程，自动生成Python单元测试代码以及SQL查询语句。这些示例生动地展示了提示工程的威力，以及语言模型在软件开发领域的广阔应用前景。

现在，我们将目光转向另一个更具挑战性的任务：构建一个能够读出PDF文档中的“图”的高级RAG（Retrieval-Augmented Generation）系统。RAG是一种将知识检索与语言生成相结合的系统，它先从外部知识库中检索出相关信息，然后将这些信息作为额外的输入，辅助模型生成更加准确和与问题相关的输出。因为 RAG 可以不断更新其所检索的数据源，适应新的信息和趋势，从而保持其回答的相关性和准确性。

![图片](https://static001.geekbang.org/resource/image/d9/89/d95aa69e33afb412da79a5197e106b89.jpg?wh=1324x640 "RAG 基本流程")

RAG这个概念今年非常火爆，被很多人誉为是大模型技术落地第一站，而结合我平时的项目情况来看，事实也的确如此。这种技术之所以备受关注并被视为大模型落地的重要方向，主要有这样几个原因。

1. 知识增强：RAG系统通过在生成过程中融入从外部知识库检索到的相关信息，使得模型能够利用更广泛、更准确的知识来完成任务。这大大提升了模型应对知识密集型任务的能力，如问答、对话、文档生成等。
2. 可解释性：传统的端到端生成模型通常被视为一个黑盒子，难以解释其输出结果的依据。而RAG系统可以明确指出输出结果所引用的外部知识来源，增强了模型的可解释性和可信度，这对于许多需要结果可追溯、可验证的应用场景非常重要。
3. 可扩展性：RAG系统的知识库是独立于模型训练的，这意味着我们可以灵活地扩充和更新知识，而无需重新训练模型。这种解耦设计使得RAG系统可以较容易地适应不同领域、不同规模的应用需求。
4. 数据效率：与从零开始训练大模型相比，RAG系统可以更有效地利用外部知识，在较小的数据规模下取得不错的效果。这在实际应用中意味着更低的数据收集和标注成本。
5. 技术成熟度：RAG系统所涉及的信息检索、语义匹配、语言生成等技术在近年来都取得了长足进展。一些开源的RAG实现方案，如LangChain、LlamaIndex，以及OpenAI的Assistants中提供的功能，都已经使得构建RAG系统的门槛大大降低，推动了其在业界的应用落地。
<div><strong>精选留言（1）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/19/70/67/0c1359c2.jpg" width="30px"><span>qinsi</span> 👍（0） 💬（1）<div>对非文本数据做RAG就需要多模态了</div>2024-06-07</li><br/>
</ul>