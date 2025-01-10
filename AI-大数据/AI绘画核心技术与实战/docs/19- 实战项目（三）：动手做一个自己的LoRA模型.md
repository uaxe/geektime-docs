你好，我是南柯。

上一讲我们已经学习了LoRA的算法原理，搞懂了引入LoRA技术减少可学习参数的技巧。

如今LoRA几乎家喻户晓，我们在Civitai或者Hugging Face上，也能找到各种各样的LoRA模型。这些LoRA模型既可以代表人物形象、动物形象或者某个特定物体，也可以代表水彩风、油画风这种特定的风格。

这一讲我们不妨自己动手，从零开始训练自己的LoRA模型。我们会以宝可梦生成和彩铅风格生成为例，完成两个模型的训练，借此探索LoRA模型表达内容和表达风格的能力如何实现。

## 如何训练一个LoRA

在我们动手训练LoRA前，我先为你预告一下整个流程。

对于LoRA的训练，我们首先需要考虑两个问题：数据集获取和基础模型选择。幸运的是，我们已经熟悉了 [Hugging Face](https://huggingface.co/models) 和 [Civitai](https://civitai.com/) 这两个强大的开源社区，可以免费获取到海量数据集和基础模型。

### 数据准备

我们可以使用 [Hugging Face](https://huggingface.co/datasets/lambdalabs/pokemon-blip-captions) 上现有的数据集，完成宝可梦的生成任务。这个数据集中包含800多张训练图片。从后面的数据集说明中你可以看到，每一张图，我们都可以获取到它对应的prompt。

![](https://static001.geekbang.org/resource/image/85/f3/857851382cf9e59969c4dd85a8ab55f3.png?wh=1568x774)

首先，我们可以通过后面这两行代码下载并加载数据集。

```python
from datasets import load_dataset

dataset = load_dataset("lambdalabs/pokemon-blip-captions", split="train")

```

接着，我们便可以通过后面这几行代码，可视化数据集中的图片和对应prompt。

```python
from PIL import Image

width, height = 360, 360
new_image = Image.new('RGB', (2*width, 2*height))

new_image.paste(dataset[0]["image"].resize((width, height)), (0, 0))
new_image.paste(dataset[1]["image"].resize((width, height)), (width, 0))
new_image.paste(dataset[2]["image"].resize((width, height)), (0, height))
new_image.paste(dataset[3]["image"].resize((width, height)), (width, height))

for idx in range(4):
  print(dataset[idx]["text"])

display(new_image)

```

![](https://static001.geekbang.org/resource/image/a5/39/a55e4011d73560e40fe87d9c743b3c39.png?wh=1102x1012)

当然，你也可以使用自己手中的图片做一个原创LoRA。如果你是一个插画师，那么你可以用自己曾经的作品，来训练一个贴近你自己风格的专属LoRA模型，帮助你进行创作。

SD模型的微调需要同时使用图片和prompt。 **如果我们手中的图片没有prompt，那么还需要使用一些方法为图片生成prompt**，这里我们选择使用名为 [BLIP](https://huggingface.co/docs/transformers/model_doc/blip) 的模型完成这个任务。

提到BLIP这个名字，你难免会联想到我们已经学过的CLIP。虽然名字差不多，但它们还是不一样的。你可以这样来区分记忆，CLIP模型提取图像和文本表征，用于跨模态理解任务。而BLIP从图像生成prompt，用于跨模态生成任务。

我以Hugging Face上的 [彩铅风格数据](https://huggingface.co/datasets/litmonster0521/pencildrawing) 为例，说明一下怎么用BLIP为每一张彩铅图片生成prompt。后面的图展示的就是这批彩铅图像的样例。

![](https://static001.geekbang.org/resource/image/84/c1/847yy9251b9597355bb1fb5a33eb97c1.jpg?wh=4409x2480)

我们要在彩铅模型训练的Colab中，运行make\_captions.py这个脚本，并指定原始图片的路径。这样脚本就会自动下载好BLIP模型，并针对提供的每张图依次进行模型推理生成prompt。你可以点开图像查看prompt的生成效果。

![](https://static001.geekbang.org/resource/image/61/57/618abbae5b55cca44b99d45f0074f857.png?wh=1587x549)

到此为止，我们已经完成了本次实战课两个数据集的准备工作。你可以根据自己想要完成的LoRA训练任务，参考上面的过程准备训练数据。

### 基础模型选择

搞定了训练数据，我们再来看怎么选基础模型。想要训练出理想的LoRA效果， **选择一个与训练目标风格接近的基础模型，会大大降低训练难度**。

比如说我们要训练某个二次元形象的LoRA模型，选择擅长动漫生成的Anything系列模型，相比于选择擅长写实人像风格生成的Chilloutmix模型而言，就是更好的选择。

这一讲我们的目标是宝可梦和彩铅风格这两个任务，我们可以选择 [Anything V5模型](https://civitai.com/models/9409) 作为基础模型。你可以在 [Civitai](https://civitai.com/models/9409) 中找到这个模型的权重，按照下面图中展示的方法把模型下载到本地，或者右键复制链接地址。

![](https://static001.geekbang.org/resource/image/a6/f8/a6829343f7fc27bcbd19bbd0e297e6f8.jpeg?wh=2245x1075)

我们运行后面这条指令便可以完成基础模型的下载。

```bash
# -O 用于制定文件的存储路径
!wget -c https://civitai.com/api/download/models/90854 -O anything_v5.safetensors

```

你也可以在Civitai或者Hugging Face中找到其他模型的下载路径，替换上面脚本中的下载链接即可完成基础模型下载的任务。比如，如果你想下载 [ChilloutMix模型](https://huggingface.co/Linaqruf/stolen/tree/main/pruned-models)，就可以使用后面这行指令。

```bash
# -O 用于制定文件的存储路径
!wget -c https://huggingface.co/Linaqruf/stolen/resolve/main/pruned-models/chillout_mix-pruned.safetensors -O chillout_mix-pruned.safetensors

```

### LoRA训练过程

准备好数据和基础模型之后，我们再来看一下训练LoRA模型的核心代码逻辑。我们在 [第12讲](https://time.geekbang.org/column/article/685751) 已经学过如何微调一个Stable Diffusion模型，这里我们来回顾一下SD训练的核心代码。

```python
 for epoch in range(num_train_epochs):
     for step, batch in enumerate(train_dataloader):

         # VAE模块将图像编码到潜在空间
         latents = vae.encode(batch["pixel_values"].to(weight_dtype)).latent_dist.sample()

         # 随机噪声 & 加噪到第t步
         noise = torch.randn_like(latents)
         timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps)
         noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

         # 使用CLIP将文本描述作为输入
         encoder_hidden_states = text_encoder(batch["input_ids"])[0]
         target = noise

         # 预测噪声并计算loss
         model_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample
         loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")
         optimizer.step()

```

其实这也正是训练一个LoRA模型的核心代码。这里该怎么理解呢？

我带你回顾一下SD模型的几个关键模块：VAE、CLIP文本编码器、UNet，通常只有UNet的权重是需要更新的。在使用LoRA微调SD的过程中，LoRA模型影响的是UNet中注意力模块的投影层权重，也就是后面示例代码中的W\_Q、W\_K和W\_V。

```python
# 从同一个输入序列产生Q、K和V向量。
Q = X * W_Q
K = X * W_K
V = X * W_V

# 计算Q和K向量之间的点积，得到注意力分数。
Scaled_Dot_Product = (Q * K^T) / sqrt(d_k)

# 应用Softmax函数对注意力分数进行归一化处理，获得注意力权重。
Attention_Weights = Softmax(Scaled_Dot_Product)

# 将注意力权重与V向量相乘，得到输出向量。
Output = Attention_Weights * V

```

我们以UNet模型中某一层的某一个交叉注意力模块投影矩阵为例来看看。我们已经知道，prompt的文本表征通过交叉注意力模块完成信息注入，用于计算得到对应的K、V向量，而Q向量源自带噪声的图像潜在表示。

下面图片展示的就是这个过程，红框中的部分就是我们要训练的LoRA模型权重。

![](https://static001.geekbang.org/resource/image/46/b2/46194ef5e13f9533e320c7fd88306fb2.jpg?wh=4409x2480)

W原始投影矩阵的权重，维度是dxd。根据我们预先设置矩阵的秩r，我们可以得到随机初始化的权重矩阵A和权重矩阵B，把它们作为要训练的LoRA模型，维度分别是dxr和rxd。

在训练过程中，W保持固定，要优化的部分是矩阵A和矩阵B。如果X作为输入，Y作为模型输出，使用LoRA的情况下，计算过程大致是后面这个公式。

$$Y = （W + A\\cdot B）\\cdot X$$

在UNet模型中，有几十处这样的注意力模块投影矩阵，我们需要逐一优化对应数量的权重矩阵A和权重矩阵B。当LoRA模型训练完成后，我们只需要保存这里的几十处LoRA权重即可，这些权重参数一般只占用几十M的存储空间。

如果前面的公式推理你暂时没法理解也不要紧，你只需要记住： **训练LoRA的过程仍旧是更新UNet模块，只不过代码中注意力模块的投影层权重会保持不变，更新的是对应的LoRA模型权重**。

### LoRA权重作用

了解了LoRA的训练，我们再来看看LoRA模型使用时候的技巧。你也许还记得，在WebUI中，我们会给LoRA模型设置一个权重值，比如0.7。这个权重值会直接决定LoRA模型发挥作用的强弱，你可以参考后面截图，红框里就是这个参数的位置。

![](https://static001.geekbang.org/resource/image/6e/9a/6ec86c8d7e8d68f38d4d534946yye09a.png?wh=1134x449)

那么，这个参数是如何起作用的呢？我们来看下面的公式。公式中的weight就是LoRA与基础模型组合时的权重（比如前面WebUI截图红框中的1），A和B代表的是LoRA模型的权重参数。

$$Y = （W + weight \* A\\cdot B）\\cdot X$$

如果我们同时使用多个模型，本质上就是下面这种计算方式。

$$Y = （W + weight\_{1} \* A\_{1}\\cdot B\_{1} + weight\_{2} \* A\_{2}\\cdot B\_{2} + weight\_{n} \* A\_{n}\\cdot B\_{n}）\\cdot X$$

这样一来，你是否就了解了多个LoRA组合的算法原理了呢？比方说，三个LoRA同时用，就相当于模型要听“三个上司”的话，每个上司都会影响输出结果Y，很可能这些影响会相互干扰。

没错，我们实际操作时，如果发现多个LoRA混用生成的图像效果并不好，其实是因为各个LoRA模型的权重值都被加到了基础模型上，导致最终AI绘画模型参数有点“四不像”。

## 代码实战

搞懂了上面的知识，我们这就来来实战演练一下，开始LoRA训练任务。GitHub上有不少LoRA训练的代码仓，比如 [diffusers 的 LoRA 训练](https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py) 代码量较少，阅读起来压力小，适合初学者作为参考。

### 一次完整的训练

使用这个代码仓的训练也非常简单，但需要你拥有独立的GPU环境。没有独立GPU的同学也不用担心，我后面会讲解怎么用Colab完成训练。

首先，你需要先在你的命令行环境下，登录Hugging Face账号，保证你的代码能够访问到Hugging Face服务器上的数据和基础模型。

```bash
huggingface-cli login
# 密码在你的Hugging Face账号Setting页面获取

```

然后你只需要将上面的 [训练代码](https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py) 拷贝到你的机器上，然后创建一个run.sh文件，写下后面的启动指令。

```bash
export MODEL_NAME="CompVis/stable-diffusion-v1-4"
export DATASET_NAME="lambdalabs/pokemon-blip-captions"

accelerate launch --mixed_precision="fp16" train_text_to_image_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --dataset_name=$DATASET_NAME --caption_column="text" \
  --resolution=512 --random_flip \
  --train_batch_size=1 \
  --num_train_epochs=10 --checkpointing_steps=5000 \
  --learning_rate=1e-04 --lr_scheduler="constant" --lr_warmup_steps=0 \
  --seed=42 \
  --output_dir="sd-pokemon-model-lora" \
  --validation_prompt="cute dragon creature"

```

然后我们运行这个启动脚本，便可以完成宝可梦的LoRA模型训练。

```bash
sh run.sh

```

需要注意，上面启动脚本中的基础模型是SD1.4，你可以在Hugging Face中获取其他基础模型的model\_id进行替换。比如可以通过一行代码，把基础模型替换为Anything V5模型。

```bash
export MODEL_NAME= "stablediffusionapi/anything-v5"

```

耐心等待20分钟（这里使用的是A100资源+预先下载的模型，不同GPU会有差异），我们就完成了LoRA模型的训练。

接着，我们不妨使用我们训练好LoRA生成图片，看看效果如何。你可以参考后面的代码完成这一步。第七行代码的prompt你可以按自己的想法灵活更换。

```python
from diffusers import StableDiffusionPipeline
import torch
model_path = "你的LoRA路径/sd-model-finetuned-lora-t4"
pipe = StableDiffusionPipeline.from_pretrained("stablediffusionapi/anything-v5", torch_dtype=torch.float16)
pipe.unet.load_attn_procs(model_path)
pipe.to("cuda")
prompt = "A pokemon with green eyes and red legs."
# prompt = "Girl with a pearl earring"
image = pipe(prompt, num_inference_steps=30, guidance_scale=7.5).images[0]
image.save("pokemon.png")

```

现在，你可以点开图片查看我们LoRA模型的生成效果，可以看到，我们的LoRA模型学到了宝可梦风格的“精髓之处”，图片的配色和线条都和宝可梦风格相似。

![](https://static001.geekbang.org/resource/image/37/b5/374d8835203aee394ecb3b1fab3a6eb5.jpg?wh=4409x2480)

### 推荐一个Colab

除了diffusers官方的LoRA实现，GitHub上有一些效果更好的LoRA实现。这里我推荐一个可调参数更多的 [Colab链接](https://colab.research.google.com/github/Linaqruf/kohya-trainer/blob/main/kohya-LoRA-finetuner.ipynb)。根据我们这一讲要完成的LoRA任务，我对原始的Colab进行了一些定制化的改造。

宝可梦风格的LoRA训练任务，你可以点开这个 [Colab链接](https://colab.research.google.com/github/NightWalker888/ai_painting_journey/blob/main/lesson19/LoRA_train_pokemon.ipynb) 做练习。

而彩铅风格的LoRA训练任务，你可以点开这个 [Colab链接](https://colab.research.google.com/github/NightWalker888/ai_painting_journey/blob/main/lesson19/LoRA_train_pencil_drawing.ipynb) 来练习。在彩铅风格的Colab代码中，我们会使用BLIP模型给每一张图片生成prompt。

为了方便你体验效果，在配置好Colab的GPU环境后，你可以直接点击全部运行，这样就能“一键”完成LoRA的训练。

![](https://static001.geekbang.org/resource/image/1d/02/1d3b6f340f6e8283412f70d03e571202.png?wh=1885x816)

耐心等待LoRA训练完成后，我们便可以看到LoRA模型的生成效果。以宝可梦的效果为例，能直观的感受到，在相同的测试prompt下，我们Colab的生成效果要优于使用diffusers代码仓的训练效果。

![](https://static001.geekbang.org/resource/image/3f/d4/3f0ebdbbd66a924421705c8fbd9d6fd4.jpg?wh=4409x2480)

这里我们用到的prompt信息如下。

```plain
Prompt：A pokemon with green eyes and red legs
Prompt：Girl with a pearl earring
Negative Prompt：lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry
采样器：Eular a
随机种子：1025
采样步数：20
分辨率：512x512
CFG Scale: 7
LoRA：pokemon.safetensors [使用Colab训练]
LoRA weight：1.0

```

我们可以再感受下彩铅LoRA的效果。从后面两张的图片可以看出，我们的LoRA模型学到了一种 “2D感” 的铅笔画风格。

![](https://static001.geekbang.org/resource/image/f3/60/f3131b2dc6a6b1c3c7b3134f3991e260.jpg?wh=4409x2480)

这里这里我们用到的prompt信息如下。

```plain
Prompt：A drawing of a beautiful girl
Prompt：Girl with a pearl earring
Negative Prompt：lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry
采样器：Eular a
随机种子：1025
采样步数：20
分辨率：512x512
CFG Scale: 7
LoRA：pencil.safetensors [使用Colab训练]
LoRA weight：1.0

```

以彩铅风格为例，我在Colab代码中为你增加了一些注释，来辅助你理解每个模块都负责做哪些事情，建议你课后阅读一下。如果你需要更换自己的训练数据，只需要替换掉代码中的训练图像拷贝部分即可。

```python
# 将我们的训练数据拷贝到训练路径下
# 如果你需要使用自己准备的图片，需要将你的数据拷贝到
# /content/LoRA/train_data/custom_data路径下
os.system("cp -r /content/caiqian_style/* /content/LoRA/train_data/custom_data")

```

## 配合WebUI使用

搞定了LoRA模型的训练，咱们再把它加入到WebUI上试试效果。

我们可以将训练得到的LoRA模型下载到本地，放在WebUI的LoRA文件夹中，然后就可以在WebUI直接使用我们刚刚训练的LoRA模型了。

```bash
# LoRA模型放置路径为：
/你的WebUI安装路径/extensions/sd-webui-additional-networks/models/lora

```

把模型放到相应位置后，别忘了刷新WebUI的LoRA模型库，加载我们刚刚放置的LoRA模型。

![](https://static001.geekbang.org/resource/image/c9/c3/c9c9c9b8d82f633ac54c2fabdd9097c3.png?wh=1143x569)

一切准备完毕，我们这就来测试下WebUI的使用效果，可以使用下面这组prompt来测试宝可梦模型。

```plain
Prompt：A pokemon with red eyes, big ears
Negative Prompt：lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry
采样器：Eular a
随机种子：1025
采样步数：20
分辨率：512x512
CFG Scale: 7
LoRA：pokemon.safetensors [使用Colab训练]
LoRA weight：1.0

```

后面的图片就是对应的生成结果，一只有点模糊的“宝可梦”呈现在我们眼前。

![](https://static001.geekbang.org/resource/image/f7/9f/f7c79f2cb07e53a251c04fda7444979f.png?wh=512x512)

效果还可以，但清晰度不够。这时我们可以利用WebUI的超分模块，得到更高清的图片。你可以点开图片查看超分后的宝可梦精灵效果。

![](https://static001.geekbang.org/resource/image/bf/7c/bfa48fa38c01dd11b05b508d74185d7c.png?wh=1142x716)

![](https://static001.geekbang.org/resource/image/8b/d6/8b3d5ee4f8735e49b94d1e6c5ce090d6.png?wh=1024x1024)

到此为止，我们已经走通了准备训练数据、图像prompt生成、基础模型选择、LoRA训练、LoRA本地使用、超分功能修复生成效果的完整流程。

关于LoRA模型，我们还可以做两个有意思的效果测试。第一个测试是将我们得到的两个LoRA模型组合使用。你可以在WebUI中按照图中的方式进行操作。

![](https://static001.geekbang.org/resource/image/f8/a6/f861677398de0ae32ea4082a045684a6.png?wh=1125x557)

我们使用后面的prompt信息进行测试。

```plain
prompt: A pokemon with red eyes, big ears
prompt: a drawing of a beautiful girl
Negative Prompt：lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry
采样器：Eular a
随机种子：1025
采样步数：20
分辨率：512x512
CFG Scale: 7

```

得到的效果是下面这个样子。可以看到，左面的宝可梦同时带上了彩铅的风格，右面的女孩子带上了宝可梦的“画风”。通过不同的LoRA权重配比，我们就能“调制出”我们心仪的风格。

![](https://static001.geekbang.org/resource/image/ee/fe/eebcf4019d52b49491fec5e8e19a2afe.jpg?wh=4409x2480)

第二个测试是将LoRA与其他基础模型搭配使用。比如我们训练宝可梦LoRA和彩铅风格LoRA的基础模型是Anything V5，我们可以试试将这两个LoRA与Realistic V3.0模型搭配使用。你可以点开图片查看结果，可以看到，生成效果并不符合我们预期的风格。这个测试说明， **LoRA模型与其他基础模型搭配使用时需要谨慎处理**。

![](https://static001.geekbang.org/resource/image/0a/87/0a8f12a8805821165327030c94894887.jpg?wh=4409x2480)

其实我们常用的各种基础模型，通常都是基于各种SD模型微调来的，有的模型甚至是基于微调后的模型再次微调。因此，我们可以将这些基础模型想象成一个大家族，不同模型之间存在一定的亲缘关系。也正是因为这个原因，我们训练得到的LoRA模型，和亲缘关系近的基础模型组合往往更容易实现预期的效果。

## 总结时刻

今天我们通过实战的形式加深了对LoRA模型的认识。我们从零到一，完成了宝可梦LoRA和彩铅LoRA两个模型的训练。

训练LoRA有两个基本前提：图文数据和基础模型。对于图文数据，我们可以从Hugging Face上直接获取，也可以用BLIP模型对我们自己的数据进行prompt打标。而基础模型，我们可以从Hugging Face或者Civitai上按需选择。

之后我们分析了在SD模型中LoRA权重的作用位置，也就是UNet模型的注意力模块，并进一步了解了LoRA权重的作用机理。然后，我们分别使用diffusers官方LoRA代码仓和一个改造后的Colab，完成了我们的LoRA训练任务。这部分的重点是理解Colab中的LoRA代码实现。

最后，我们将训练得到的LoRA模型导入WebUI，完成了图像生成、图像超分、多LoRA组合、更换基础模型测试等任务。建议你课后自己多练习，也可以将自己训练的LoRA模型发布到开源社区，供其他朋友体验和分享，这样学习效果会更好。

这一讲的重点，你可以点开下面的导图复习回顾。

![](https://static001.geekbang.org/resource/image/56/37/566185db89f38848d1a04945d26e8637.jpg?wh=3900x1720)

## 思考题

选择你一个你喜欢的物体或者一种你喜欢的风格，使用diffusers代码仓或者我们的Colab链接，完成你自己的LoRA模型训练。

期待你在留言区和我交流讨论，也推荐你把今天的内容分享给身边更多朋友，和他一起尝试训练LoRA模型。