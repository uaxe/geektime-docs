你好，我是独行。

前面第16课，我们从0～1手敲了Transformer，并且进行了一次完整的训练，当时我用的A10-24G显卡，准备了500M的训练文本，结果预估需要1个月时间才能跑完，可见训练对机器的要求有多么高，我们使用的数据集大小才500M，一般训练一个大模型，绝对不止这么点数据，而且参数规模也会更大。

据我所知，GPT-3和GLM-130B这种千亿规模的大模型，训练周期基本在3个月左右，所以按照我们目前的这种做法，肯定是不行的。那在实际的训练过程中，如何才能提高训练速度呢？

答案是使用分布式训练，目前比较流行的训练框架有微软的DeepSpeed和NVIDIA的NCCL等，这节课我们就主要聊聊微软的DeepSpeed。

## DeepSpeed

DeepSpeed是由微软开发的一个非常优秀的分布式训练库，专为大规模和高效的深度学习训练设计，在分布式训练领域提供了多项创新的技术，比如并行训练、并行推理、模型压缩等。你可以看一下官方说明的4个创新点。

![图片](https://static001.geekbang.org/resource/image/87/7c/879fbdb6b8ac6ef8d1f4c163ceeyye7c.png?wh=2048x475)

简单整理下：

![图片](https://static001.geekbang.org/resource/image/25/ea/25aa98226da8a14c2094941ed23e09ea.jpg?wh=1422x1230)

下面我就向你依次介绍DeepSpeed在这几方面的能力。

## 训练

对于复杂的深度学习模型，除了模型设计具有挑战性之外，使用先进的训练技术也尤为重要，比如分布式训练、混合精度、梯度累积和检查点等。DeepSpeed在这些方面比较擅长，可灵活组合三种并行方法：数据并行性、管道并行性和模型并行性，简称3D并行性，可适应不同工作负载的需求。目前已经支持超过一万亿超大参数的模型，实现了近乎完美的内存扩展和吞吐量扩展效率。
<div><strong>精选留言（1）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/0f/a0/c3/c5db35df.jpg" width="30px"><span>石云升</span> 👍（4） 💬（0）<div>结合 DeepSpeed 和 LoRA，可以显著优化微调过程，尤其是在资源受限的环境下。
1.减少计算资源需求：LoRA 本身已经减少了微调的计算需求，再加上 DeepSpeed 的内存和计算优化，可以进一步降低显存占用和计算时间。例如，在微调 GPT-3 这样的大型模型时，DeepSpeed+LoRA 的组合可以让单个 GPU 处理更多的微调数据，从而提高效率。
2.提升微调速度：由于 LoRA 只需要对模型的部分参数进行调整，而不是对整个模型进行完整的更新，因此微调过程中的计算量大幅减少。DeepSpeed 的混合精度训练和 ZeRO 优化技术进一步加快了这个过程，从而可以在更短的时间内完成微调。
3.提高模型性能：DeepSpeed 的优化方法能够确保在微调过程中，计算资源的利用率达到最大化。同时，LoRA 只在模型的特定部分进行更新，减少了过拟合的风险。因此，两者结合可以在较短时间内实现更好的性能，同时保持模型的泛化能力。</div>2024-09-05</li><br/>
</ul>