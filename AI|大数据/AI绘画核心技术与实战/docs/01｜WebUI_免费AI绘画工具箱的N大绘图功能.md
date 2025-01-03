你好，我是南柯。

欢迎和我一起探索AI绘画的魅力。热身篇这一章相当于整个学习过程里的“新手村”，我会带你一起熟悉各种各样免费开源的AI绘画工具和模型，帮助你全面掌握AI绘画的无限潜能。

今天是课程的第一讲，我们先从Stable Diffusion和WebUI说起。学完今天的内容，你不但能够知道Stable Diffusion的来龙去脉，还能解锁WebUI里的特色功能，来实现各种富有想象力的视觉创意。

## 初识WebUI

想必你一定听说过Stable Diffusion，其背后的技术便是人们常说的扩散模型。扩散模型这个概念源自热力学，在图像生成问题中得以应用。

简言之，Stable Diffusion是这样一个过程：你不妨想象一下，任何一张图像都可以通过不断添加噪声变成一张完全被噪声覆盖的图像；反过来，任何一张噪声图像通过逐步合理地去除噪声，变得清晰可辨。

Stable Diffusion（以下简称SD）在AI绘画领域中闪耀着耀眼的光芒，SD背后的方法在学术界被称为Latent Diffusion，论文发表于2022年计算机顶会CVPR，相关知识在后面的课程中我们会涉及，这里先按下不表。此时你只需要知道，SD模型可以输入文本，生成图像。这里提到的文本，就是我们常说的prompt。比如下面这张图，就是由SD模型生成的。

![](https://static001.geekbang.org/resource/image/f8/cb/f8b7d1beea87115537ed104b8031a3cb.jpg?wh=1300x873)

这里我并非打算讨论其学术价值，而是想和你说说SD模型的高昂成本。你知道吗，训练一个Stable Diffusion模型的代价相当可观。SD模型有几个备受关注的版本，比如SD 1.4、SD 1.5和SD 2.0。

为了训练这些模型，需要使用巨大的数据集，包含20亿至50亿个图像文本对。这一庞大任务需要依赖数百块A100显卡，每块A100的价格大约在十万元左右。以SD 1.5为例，训练过程需要使用256块A100显卡，并持续耗时30天。这样一算，你可能会感叹，这投入都够买好几套海淀区的学区房了，真不是普通人能玩得起的！

然而，令人惊喜和惊叹的是，这些令人炫目的成果竟然被开源了！这一开源举措在整个社区中引发了热烈反响，掀起了一股热潮。开源的SD模型让我们真切感受到了文生图的强大魅力和言出法随的创作能力。

然而，复杂的代码逻辑也让普通用户望而却步。我们今天要用到的WebUI便应运而生。2022年10月，开源社区AUTOMATIC1111推出了名为 “stable-diffusion-webui” 的图形化界面，为普通用户提供了方便快捷的构建SD模型图像UI界面的工具。

通过这个界面，用户可以体验到SD模型一系列的功能，包括文生图、图生图、inpainting和 outpainting等等，甚至还能自定义训练具有指定风格的全新模型。由于开源、易于上手和功能全面等诸多优势，SD WebUI迅速成为SD模型系列中最出色、使用最广泛的图形化程序之一。

为了让你在上手实操前有个基本认识，这里我先贴了个WebUI的界面图。

你可以看到，在这个界面最上面的部分，你可以选择各种不同的AI绘画模型和不同的AI绘画功能；右侧可以展示出AI绘画的效果，供我们根据喜好决定是否保存到本地；至于左侧的参数信息怎么用，稍后我再详细讲解。

![](https://static001.geekbang.org/resource/image/63/4f/63c72f749a6aa9aa3ab2348519a6824f.png?wh=2900x2267)

与其他AI绘画类模型如Midjoruney、DALL-E 2相比，SD WebUI可以免费在个人电脑或服务器上运行，并根据用户意愿进行改造和扩展。随着社区力量的涌入，SD WebUI还拥有了丰富的插件，如LoRA、ControlNet等，它们让原生SD模型的能力和表现更加出色。

目前，SD WebUI已经支持多平台运行，包括Windows、MacOS和Linux系统，支持英伟达、AMD和苹果M系列等多种GPU架构。对于追求高自由度的AI绘画艺术家而言，SD WebUI几乎已经成为该领域的首选工具。

## WebUI的安装和部署

一提到安装WebUI，你可能会担心GPU的问题。我事先说明，先把心放在肚子里。因为WebUI既可以使用自己的本地GPU，也可以使用第三方提供的GPU资源。

如果你拥有个人显卡或GPU服务器，并且希望按照官方的安装方式进行操作，那么首先需要下载SD WebUI的代码。你可以使用Git命令将整个仓库克隆到本地。如果你的网络速度比较慢，也可以在GitHub主页中找到并下载已打包好的zip压缩包。

```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git

```

对于Windows用户，可以像后面这样操作。

```bash
1. 安装Python 3.10.6，勾选 "Add Python to PATH"。
2. 从Windows资源管理器(CMD终端)中以非管理员的用户身份运行webui-user.bat。

```

![](https://static001.geekbang.org/resource/image/63/91/63536b62b12b75532f5302c63e08f891.jpg?wh=2900x2215)

对于Linux用户，打开终端命令行。

```bash
# Debian-based:
sudo apt install wget git python3 python3-venv
# Red Hat-based:
sudo dnf install wget git python3
# Arch-based:
sudo pacman -S wget git python3

bash <(wget -qO- https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui/master/webui.sh)

```

![](https://static001.geekbang.org/resource/image/c5/b0/c551b86a767759be04c3b94bb956bcb0.png?wh=2900x1351)

对于苹果M系列芯片的电脑用户，打开电脑的term命令行工具，根据这个 [教程链接](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Installation-on-Apple-Silicon) 来安装WebUI。

```bash
# 首先cd到你希望安装WebUI的位置

brew install cmake protobuf rust python@3.10 git wget

git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui

cd stable-diffusion-webui

export no_proxy="localhost, 127.0.0.1, ::1"

./webui.sh

```

在你的浏览器输入以下链接 [http://127.0.0.1:7860](http://127.0.0.1:7860/)，便可以进入WebUI。在丐版M2处理器的MacBook Air上，20步生成512分辨率的单张图像，大概需要25秒。即使没有英伟达的高端显卡，也可以在本地进行AI绘画。

更详细的安装方案和问题，你可以参考 [官方指南](https://github.com/AUTOMATIC1111/stable-diffusion-webui)。

如果你本地没有英伟达显卡，而且不希望等太久，可以使用各种第三方平台提供的GPU资源进行操作。这需要发挥下你的聪明才智，也欢迎小伙伴们在评论区留下你的方法。启动WebUI后的界面可以看下面的图示。

![](https://static001.geekbang.org/resource/image/fd/f4/fd137cc1a21f32211fc3f27f1b340cf4.png?wh=2900x1331)

此外，如果你希望进行汉化或者探索更多功能，可以在Extensions（扩展）中进一步探索。Extensions提供了一系列额外的功能和工具，里面包括很多功能和定制选项，这让我们的WebUI体验更加个性化和定制化。

到这里，我们就完成了WebUI的安装和部署。搞定了环境问题，我们便可以玩转WebUI了！

## WebUI基本能力之文生图

现在让我们开始创作吧！首先我们需要熟悉一下后面这些参数信息。

![](https://static001.geekbang.org/resource/image/b5/29/b596e8080731898080e307581a70e829.jpg?wh=4409x2480)

- Stable Diffusion checkpoint：这里可以选择已经下载的模型。目前许多平台支持开源的SD模型下载，例如Civitai、Hugging Face等。
- txt2img：这个选项表示启用文生图（text-to-image）功能。类似地，img2img等选项则代表其他功能。
- prompt：用于生成图像的文字输入，需要使用英文输入，但你也可以通过探索Extensions来实现中文输入。
- negative prompt：这是生成图像的反向提示词，用于指定你不希望模型生成的内容。例如，如果你不想图像中出现红色，可以在这里输入“red”。
- Sampling method：不同的采样算法，这里深入了Diffusion算法领域，稍后我们会更详细地讲解。简单来说，通过这些采样算法，噪声图像可以逐渐变得更清晰。
- Sampling steps：与采样算法配合使用，表示生成图像的步数。步数越大，需要等待的时间越长。通常20-30步就足够了。
- Width & Height：生成图像的宽度和高度。
- Batch size：每次生成的图像数。如果显存不够大，建议调小这个数值。
- CFG scale：这里表示prompt的影响程度。值越大，prompt的影响就越大。
- Seed：生成图像的随机种子，类似于抽奖的幸运种子，会影响生成的图像结果。

这些参数的变化会对最终的生成效果产生千般变化。每一个参数都扮演着重要的角色，影响着生成图像的质量、多样性和风格。理解和熟悉这些参数的作用是使用WebUI进行图像生成和编辑的关键。

但你不用着急，在后续的课程中，我们将会详细拆解这些参数的作用，逐一介绍它们对生成效果的影响。通过学习这些参数的作用，你将能够更加准确地控制生成图像的特征和风格，实现自己所需的创作效果。

OK，开启AI绘画！我们在WebUI界面中使用如下参数，让SD模型帮我们生成一只可爱的小猫。这里我们使用的是一个名为RealisticVision的模型，你可以点开 [这个链接](https://civitai.com/models/4201?modelVersionId=6987) 进行模型下载，然后将模型放置在WebUI安装路径下的模型文件夹中。

```python
# 模型文件夹地址：./stable-diffusion-webui/models/Stable-diffusion
model：realisticVisionV13_v13.safetensors[c35782bad8]
prompt：a photo of a cute cat
Sampling method：Euler A
Sampling steps：20
Width & Height: 512
Batch size: 4
CFG scale: 7
seed: 10

```

结果是后面这样。

![](https://static001.geekbang.org/resource/image/2c/35/2cce40c243bff208855dbb31659fb935.jpg?wh=4409x2480)

通过SD模型，几只可爱的小猫瞬间诞生了！然而，这些小猫似乎带着一丝悲伤。不过，我们可以保持相同的参数，把prompt语句稍作修改，在cute和happy cat之间多写一个单词 “and”。

```bash
prompt：a photo of a cute and happy cat

```

![](https://static001.geekbang.org/resource/image/dd/ca/dd714e39ee5da4d4b8b5b6a21daf80ca.jpg?wh=4409x2480)

魔法再次生效！现在这些可爱的小猫展现出了微笑的表情。接下来，你可以放飞想象力，将所有的生成和创作交给SD模型完成了！AI绘图的文生图模式已经为你打开大门，更加广阔的创作空间就在眼前！

## WebUI的其它有趣功能

除了基本的文生图能力外，WebUI在图像生成和编辑方面几乎无所不能。我们继续探索WebUI的其他玩法。

**img2img：图生图，不同风格**

我先大致给你梳理一下img2img的原理。首先，输入图像经过添加噪声的处理，变成了一个“不清晰的噪声图”。然后，通过结合不同的prompt语句，图像逐渐变得清晰，并呈现出与prompt语句相关的风格。

以一张男士的头像为例，通过使用不同的prompt语句，就能将其转变成多种不同的风格，如艺术风格、卡通风格、油画风格等。每一步都会逐渐减少噪声的影响，使得图像细节逐渐清晰，并呈现出与prompt语句相匹配的风格特征。

请注意，具体的实现方式可能会因为我们使用的模型和算法而有所不同。这只是一个大致的描述，实际操作需要考虑到具体的模型和算法选择。

![](https://static001.geekbang.org/resource/image/93/b3/932dd1d545fc151aa4ea149b99eb3bb3.jpg?wh=4409x2480)

**Outpainting：延展图像**

我们还可以生成图像之外的区域，这个功能可以帮我们扩展图像的边界或填充缺失的区域，使整体图像更完整。它的基本原理是将原始图像中的图像之外的区域看作“不清晰的噪声图”，但会保持原本区域不变，并参考原始图像的信息来生成原图之外的内容。

![](https://static001.geekbang.org/resource/image/7c/5e/7c877119f3067167031a07c314655c5e.jpg?wh=4409x2480)

**Inpainting：局部重绘**

同样的思路，我们可以在图像内部绘制一个遮罩（mask），这个功能使用WebUI自带的画笔功能便可以实现。

当我们对要重画的区域进行遮罩后，使用不同的prompt语句，就可以为该遮罩重新绘制新的内容。这样做可以根据所选择的风格和要表达的意图，在图像的特定区域上添加或修改内容，从而实现更具创意和个性化的图像效果。

通过与不同的prompt语句结合，我们可以为图像内部的遮罩部分赋予各种风格和特征。

![](https://static001.geekbang.org/resource/image/ff/00/ff0109ce0bc174108b1974bb17f81100.jpg?wh=4409x2480)

**强调prompt的关键词**

在WebUI中，有时我们希望强调prompt语句中的特定词汇。为了实现这一目的，我们可以使用圆括号 ( ) 来突出显示这些词汇。举个例子，如果我们想强调少年头发的卷曲特征，即curly hair，只需在该词汇外添加多个 ( )，以突出显示该词汇，从而引导生成模型更加关注这一特定要素。

![](https://static001.geekbang.org/resource/image/94/c1/94cyye0f49de4c43f736ac3749bb8dc1.jpg?wh=4409x2480)

**Negative prompt：反向提示词**

通过在negative prompt区域添加不想出现的信息，比如在此处添加 “smile（微笑）”，就可以去掉笑容。生成模型会参考这些负面prompt信息，尽量避免生成带有笑容的图像。这样的处理可以帮助控制图像生成的特定要素，使其符合特定需求或风格。

请注意，生成模型的效果可能会受到多种因素的影响，包括数据集、模型架构等。

![](https://static001.geekbang.org/resource/image/71/47/717538c1b9a30279af211836a5857e47.jpg?wh=4409x2480)

**Face restoration：面部修复**

对于SD模型来说，实现高质量而且精确的人脸生成确实是一个挑战。为了解决这个问题，WebUI可以结合以往针对人脸修复的工作，例如GFPGAN、CodeFormer等，对生成图像中的人脸区域进行修复，从而提高人脸的生成质量。

通过对生成的人脸进行修复，可以改善细节、纠正不准确的特征，让生成的人脸显得更加自然和美观。这种修复过程可以针对人脸区域做精细调整，提升生成结果的真实感和质量。

![](https://static001.geekbang.org/resource/image/b7/5e/b7b43e22e7a191bb12ef585ec243bd5e.jpg?wh=4409x2480)

## WebUI的功能拓展插件

WebUI的功能，不光是前面我们提到的这几种。通过探索WebUI的Extensions，你会发现更多让人惊喜的功能和工具，实现更多个性化的需求。例如，你可以探索中文输入的扩展，方便你在中文模式下生成和编辑图像。

此外，用户也可以通过自定义训练模型，实现更加个性化和定制化的图像生成。通过指定特定的风格和样本图像，用户可以训练出符合自己需求的模型，进一步发挥创造力。

总之，WebUI的功能远远超出我们展示的范围，它为用户提供了一个广阔的创作空间。期待你能充分发挥想象力，探索出更多新颖和创造性的玩法，将WebUI的潜力发挥到极致。无论是专业人士还是爱好者，都能在WebUI中找到满足自己创作需求的工具和功能。让我们一起期待更多精彩的创作和探索！

## 总结时刻

这一讲，我们学习了Stable Diffusion模型，了解了它在创意图像生成和编辑中的应用。

Stable Diffusion模型是一种基于噪声图像逐步演化的生成模型。通过对图像进行多次采样和演化，我们可以逐渐生成高质量、多样性的图像。

为了满足普通人使用SD模型的需求，WebUI这个强大的图形化界面工具应运而生，它为我们提供了便捷的使用接口和丰富的功能。

通过WebUI，我们可以轻松选择和加载已训练好的Stable Diffusion模型，使用文生图等功能生成具有创意和多样性的图像。我们还介绍了WebUI中的一些关键参数，如 **prompt、negative prompt** 等，它们对图片生成效果起着重要的影响。

此外，我们还探索了WebUI的其他功能，如图像编辑、样式迁移等，这些功能使得我们可以在图像生成和编辑过程中实现更多的创作可能性。WebUI的易用性和灵活性使得它成为广大创意艺术家和AI爱好者的首选工具之一。

希望这一讲能够激发你对WebUI工具和Stable Diffusion模型的兴趣和热情，并尝试开启广阔的创作空间。

![](https://static001.geekbang.org/resource/image/c9/d8/c98af7f4b7941048e2bd76eb1e3d72d8.jpg?wh=2600x1852)

## 思考题

你的工作与图像和创意创作有关吗？WebUI在这方面扮演怎样的角色呢？

欢迎你在留言区与我交流讨论，并把今天的内容分享给身边的同事和朋友，和他一同探索AI绘画的无限可能！