你好，我是独行。

上一节课我们讲解了编码器各层的数据处理逻辑，这节课我们进入解码器。先来看一个更加细化的架构图，解码器多了一层：编码-解码注意力层（Encoder-Decoder Attention），我们依次来看一下。

![图片](https://static001.geekbang.org/resource/image/4d/84/4d6c6cbaa5a9754c6976ae4a6af62e84.png?wh=1415x804)

## Transformer架构原理

### 自注意力层处理（解码器）

解码器的自注意力层设计得比较特别，与编码器的自注意力层不同，解码器的自注意力层需要处理额外的约束，即保证在生成序列的每一步仅依赖于之前的输出，而不是未来的输出。这是通过一个特定的掩蔽（masking）技术来实现的。接下来我详细解释一下解码器自注意力层的几个关键点。

1. **处理序列依赖关系**，解码器的自注意力层使每个输出位置可以依赖于到目前为止在目标序列中的所有先前位置。这允许模型在生成每个新词时，综合考虑已生成的序列的上下文信息。
2. **掩蔽未来信息**，为了确保在生成第 $t$ 个词的时候不会使用到第 $t+1$ 及之后的词的信息，自注意力层使用一个上三角掩蔽矩阵，在实现中通常填充为负无穷或非常大的负数。这保证了在计算Softmax时未来位置的贡献被归零，从而模型无法“看到”未来的输出。
3. **动态调整注意力焦点**，通过学习的注意力权重，模型可以动态地决定在生成每个词时应更多地关注目标序列中的哪些部分。

```python
import torch
import torch.nn.functional as F

def decoder_self_attention(query, key, value, mask):
    """
    解码器自注意力层，带掩蔽功能。

    参数:
    - query, key, value: 形状为 (batch_size, seq_len, embed_size) 的张量
    - mask: 形状为 (seq_len, seq_len) 的张量，用于防止未来标记的注意力

    返回:
    - attention output: 形状为 (batch_size, seq_len, embed_size) 的张量
    - attention weights: 形状为 (batch_size, seq_len, seq_len) 的张量
    """
    # 计算缩放点积注意力分数
    d_k = query.size(-1)  # 键向量的维度
    scores = torch.matmul(query, key.transpose(-2, -1)) / torch.sqrt(torch.tensor(d_k, dtype=torch.float32))

    # 应用掩蔽（将未来的标记设置为极大的负数以排除它们）
    scores = scores.masked_fill(mask == 0, float('-inf'))

    # 应用softmax获取注意力权重
    attention_weights = F.softmax(scores, dim=-1)

    # 使用注意力权重和值向量乘积得到输出
    attention_output = torch.matmul(attention_weights, value)

    return attention_output, attention_weights

# 示例用法
batch_size = 1
seq_len = 5
embed_size = 64
query = torch.rand(batch_size, seq_len, embed_size)
key = torch.rand(batch_size, seq_len, embed_size)
value = torch.rand(batch_size, seq_len, embed_size)

# 生成掩蔽矩阵以阻止对未来标记的注意（使用上三角矩阵掩蔽）
mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()

# 调用函数
output, weights = decoder_self_attention(query, key, value, mask)
print("输出形状:", output.shape)
print("注意力权重形状:", weights.shape)

```

mast的值：

```python
tensor([[False,  True,  True,  True,  True],
        [False, False,  True,  True,  True],
        [False, False, False,  True,  True],
        [False, False, False, False,  True],
        [False, False, False, False, False]])

```

![图片](https://static001.geekbang.org/resource/image/98/a1/984b96816c309a711ce0e0359e1605a1.png?wh=1252x366)

解码器中的自注意力层至关重要，因为它不仅提供了处理序列内依赖关系的能力，还确保了生成过程的自回归性质，即在生成当前词的时候，只依赖于之前已经生成的词。这种机制使Transformer模型非常适合各种序列生成任务，如机器翻译、文本摘要等。

之所以有这种机制，是因为自注意力机制允许当前位置的输出与未来位置的输入产生关联，从而导致数据泄露和信息泄露的问题。而推理阶段，是不可能读到未来信息的，这样可能会导致模型在训练和推断阶段表现不一致，以及模型预测结果的不稳定性。

### 编码-解码注意力层（解码器）

编码-解码注意力层（Encoder-Decoder Attention Layer）是一种特殊的注意力机制，用于在解码器中对输入序列（编码器的输出）进行注意力计算。这个注意力层有助于解码器在生成输出序列时对输入序列的信息进行有效整合和利用，注意，这个注意力层关注的是全局的注意力计算，包括编码器输出的信息序列和解码器内部的自注意力计算。

那它与上面讲的解码器自注意力层有什么区别呢？

1. **信息来源不同**：编码-解码注意力层用在解码器（Decoder）中，将解码器当前位置的查询向量与编码器（Encoder）的输出进行注意力计算，而解码自注意力层用于解码器自身内部，将解码器当前位置的查询向量与解码器之前生成的位置的输出进行注意力计算。

2. **计算方式不同**：编码-解码注意层计算当前解码器位置与编码器输出序列中所有位置的注意力分数。这意味着解码器在生成每个输出位置时，都可以综合考虑整个输入序列的信息。解码自注意力层计算当前解码器位置与之前所有解码器位置的输出的注意力分数。这使得解码器可以自我关注并利用先前生成的信息来生成当前位置的输出。


用一句话总结就是：编码-解码注意层关注整个编码器输出序列，将编码器的信息传递给解码器，用于帮助解码器生成目标序列，解码自注意力层关注解码器自身先前生成的位置的信息，用于帮助解码器维护上下文并生成连贯的输出序列。

#### 前馈层处理（解码器）

前馈处理和编码器中的前馈处理类似，通过两次线性映射和一个中间的ReLU激活函数，生成解码器最终的输出，原理可以看我们上一节课介绍的内容。

#### Linear

在Transformer架构中，Linear层就是线性层的意思，通常被用于多个子模块中，包括编码器和解码器中的不同部分。Linear层的作用是对输入数据进行线性变换，将输入张量映射到另一个张量空间中，并且通过学习参数来实现数据的线性组合和特征变换。可以说，Linear无处不在，也很容易理解。我简单讲解下解码器后面的Linear的作用。

解码器后面的Linear层通常用于将经过前馈层处理的特征表示，映射到最终的输出空间，即模型的输出词汇表的维度。这个Linear层的作用是将解码器前馈层的输出映射为模型最终的预测结果，例如生成下一个单词或标记的概率分布，实际上是进行降维，将前馈层的高维输出转换为词汇表的维度。你可以参考下面的示例代码：

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class Decoder(nn.Module):
    def __init__(self, d_model, vocab_size):
        super(Decoder, self).__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size

        # 前馈网络（Feed Forward Network）
        self.feedforward = nn.Sequential(
            nn.Linear(d_model, 2048),
            nn.ReLU(),
            nn.Linear(2048, vocab_size)
        )

    def forward(self, x):
        # x: 解码器前馈网络的输出，形状为 [batch_size, seq_len, d_model]

        # 将解码器前馈网络的输出通过线性层进行映射
        output_logits = self.feedforward(x)  # 输出形状为 [batch_size, seq_len, vocab_size]

        # 对输出 logits 进行 softmax 操作，得到预测概率
        output_probs = F.softmax(output_logits, dim=-1)  # 输出形状为 [batch_size, seq_len, vocab_size]

        return output_probs

# 示例用法
d_model = 512  # 解码器特征维度
vocab_size = 10000  # 词汇表大小

# 创建解码器实例
decoder = Decoder(d_model, vocab_size)

# 输入数据，假设解码器前馈网络的输出
input_tensor = torch.randn(2, 10, d_model)  # 示例输入，batch_size=2，序列长度=10

# 解码器前向传播
output_probs = decoder(input_tensor)

# 输出预测概率，形状为 [2, 10, 10000]
print(output_probs.shape)

```

示例中，我们定义了一个简单的解码器（Decoder），其中包含一个前馈网络。前馈网络由两个线性层和一个ReLU激活函数组成，用于将解码器的特征表示 $x$ 映射到词汇表大小的维度上。最后，对输出进行Softmax操作，得到预测概率。我们再看看Softmax函数的作用。

#### Softmax函数

Softmax函数作用非常大，其核心就是一句话：将一组任意实数转换成一个概率分布。在Transformer模型中有多处用到，比如注意力机制和多头注意力机制，通过Softmax函数计算注意力分数，以及在解码器最后一层，会将上面讲的Linear线性层输出的数据，应用Softmax函数进行处理。这里有两个问题需要注意。

1. 为什么需要通过Softmax函数进行计算？意义在哪里？
2. 将任意实数转化为概率分布，数据的意义将会发生变化，会不会对效果产生影响？

我们看一下关于问题1的解释。

- 将得分转换成概率后，模型能够更加明确地选择哪些输入的部分是最相关的。
- 在神经网络中，直接处理非常大或非常小的数值可能会导致数值不稳定，出现梯度消失或爆炸等问题。通过Softmax函数处理后，数据将被规范化到一个固定的范围，从0到1之间，可以缓解这些问题。
- Softmax函数的输出是概率分布，这使得模型的行为更加透明，可以直接解释为“有多少比例的注意力被分配到特定的输入上”。这有助于调试和优化模型，以及理解模型的决策过程。

我们再看一下关于问题2的解释。

- 原始的得分只表达了相对大小关系，即一个得分比另一个高，但不清楚这种差异有多大。而通过Softmax转换后，得到的概率值不仅反映出哪些得分较高，还具体表达了它们相对于其他选项的重要性。这种转换让模型可以做出更精确的决策。
- 原始得分可能因范围广泛或分布不均而难以直接操作，而概率形式的输出更标准化、更规则，适合进一步的处理和决策，如分类决策、风险评估等。

我们看一个简单的示例代码。

```python
import numpy as np
import torch
import torch.nn.functional as F

# 假设有一个简单的查询 (Query) 和键 (Key) 矩阵，这里使用随机数生成
np.random.seed(0)  # 设置随机种子以确保结果的可复现性
query = np.random.rand(1, 64)  # 查询向量，维度为1x64
key = np.random.rand(64, 10)   # 键矩阵，维度为64x10

# 将numpy数组转换为torch张量
query = torch.tensor(query, dtype=torch.float32)
key = torch.tensor(key, dtype=torch.float32)

# 计算点积注意力得分
attention_scores = torch.matmul(query, key)  # 结果维度为1x10

# 应用Softmax函数，规范化注意力权重
attention_weights = F.softmax(attention_scores, dim=-1)

print("注意力得分（未规范化）:", attention_scores)
print("注意力权重（Softmax规范化后）:", attention_weights)

```

程序输出结果：

```python
注意力得分（未规范化）: tensor([[17.9834, 15.4092, 15.5016, 15.2171, 18.3008, 17.4539, 15.6339, 16.3575,
         14.5159, 15.4736]])
注意力权重（Softmax规范化后）: tensor([[0.2786, 0.0212, 0.0233, 0.0175, 0.3826, 0.1640, 0.0266, 0.0548, 0.0087,
         0.0226]])

```

Softmax函数的具体实现：

$$Softmax(x\_i)=\\frac{e^{x\_i}}{\\sum\_{j}^{}{e^{x\_j}}}$$

1. **指数化**：对输入向量的每个元素应用指数函数。这意味着每个输入值 $x\_i$ 被转换为 $e^{x\_i}$，其中 $e$ 是自然对数的底。这一步的作用是将所有输入转化为正数，并放大了输入值之间的差异。
2. **归一化**：计算所有指数化值的总和 ${\\sum\_{j}^{}{e^{x\_j}}}$，然后，将每个指数化后的值除以这个总和。这一步的结果是一组和为1的概率值，其中每个概率值都表示原始输入值相对于其他值的重要性或贡献度。

代码实现如下：

```python
import numpy as np

def softmax(x):
    exp_x = np.exp(x - np.max(x))  # 防止数值溢出
    return exp_x / exp_x.sum()

# 示例输入
x = np.array([1.0, 2.0, 3.0])
print("Softmax输出:", softmax(x))

```

到这里，Transformer的基本原理就介绍得差不多了，下面我们看看这么设计有什么好处。

## Transformer的优势

### 并行处理能力

与传统的循环神经网络（RNN）和长短期记忆网络（LSTM）不同，Transformer完全依赖于自注意力机制，消除了序列处理中的递归结构，允许模型在处理输入数据时实现高效的并行计算。这使得训练过程大大加速，特别是在使用现代GPU和TPU等硬件时。你可以回顾一下Position Encoding的作用，就是为序列添加位置编码，以便在并行处理完以后，进行合并。

### 捕捉长距离依赖

Transformer通过自注意力机制能够捕捉序列中的长距离依赖关系。在自然语言处理中，这意味着模型可以有效地关联文本中相隔很远的词汇，提高对上下文的理解。

### 灵活的注意力分布

多头注意力机制允许Transformer在同一个模型中同时学习数据的不同表示。每个头可以专注于序列的不同方面，例如一个头关注语法结构，另一个头关注语义内容。

### 可扩展性

Transformer模型可以很容易地扩展到非常大的数据集和非常深的网络结构。这一特性是通过模型的简单可堆叠的架构实现的，使其在训练非常大的模型时表现出色。

当然还有其他特性，比如适用性、通用性等，总的来说，Transformer通过其独特的架构设计在效率、效果和灵活性方面提供了显著的优势，使其成为处理复杂序列数据任务的强大工具。

## 小结

Transformer架构还是比较复杂的，涉及很多概念，对于初学者来说有点难，而且机器学习里的很多概念甚至代码和我们做软件开发相比，完全不一样。不过你不用着急，看不懂没关系，一点一点来，从下一节课开始，我们从0到1写一个基于Transformer架构的模型，相信你会更有感觉。

![图片](https://static001.geekbang.org/resource/image/91/f8/91ebf8992293781f0f30e288404b24f8.png?wh=2310x1398)

## 思考题

假设你正在使用一个基于Transformer的模型来自动总结新闻文章。你注意到模型在处理某些文章时，重要的信息并没有被有效地捕捉和反映在摘要中，请思考一下，Transformer模型中的哪一个部分最可能对抓取关键信息并生成准确摘要起到决定性作用？如何简单调整模型，来确保关键信息被捕捉？

欢迎你把你思考后的结果分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！