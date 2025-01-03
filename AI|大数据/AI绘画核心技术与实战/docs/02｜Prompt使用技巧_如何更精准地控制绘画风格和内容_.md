你好，我是南柯。

之前我们解锁了Web UI的七大特色功能，如果拿烹饪来做比喻，前一讲的内容大概只是把菜做熟的程度，还无法产出“色香味”俱全的图像作品。实际应用的时候，你很可能遇到后面这些困扰。

- 图生图如何优化，如何生成具有特定特征或内容的图像？
- 输入了提示词，但AI模型不太“听话”，要怎么做参数调优？
- 怎样生成多样风格的图像作品？

这一讲我们就来解决这些问题，学习影响图像风格、内容和质量的重要参数。熟练掌握应用和优化这些参数的技巧以后，你就可以随心所欲地控制AI绘画的构图、内容和风格，制作出更符合自己心意的专属内容了。

## WebUI咒语指南：prompt入门

想要控制 **Stable Diffusion** 创作我们喜好的图像，熟练运用 **prompt**（提示词）至关重要。在开源社区中，prompt甚至因为对AI绘画的神秘影响，被赋予了“咒语”或“魔法”的称号。

不过prompt其实并没那么玄乎，学完它的使用方法和实用技巧以后，你也能成为AI绘画界的杰出“魔法师”。

### 初阶咒语：直接描述

prompt最简单且常见的用法，就是直接在prompt区域描述我们想要创作的图像，例如输入 `a happy dog and a cute girl`。通过这样的描述，我们可以生成后面这样的图像。

![](https://static001.geekbang.org/resource/image/e5/87/e542c7f24b8510a9bc829afed3e1fb87.jpg?wh=2935x1207)

![](https://static001.geekbang.org/resource/image/c8/c8/c887acb346b312d25fcec77d31aa58c8.jpg?wh=3594x2480)

如果你想生成和我相同的图像，请记得将SD基础模型选择为realv1.3，固定随机种子设为10。采样方法选择Euler a，步数选择20，CFG Scale为7。目前你可能还不熟悉这些参数的含义，不必担心，我们将逐步了解它们。

紧接着，我们可以通过修改prompt来赋予创作图像不同的风格化效果。例如，我们可以使用以下修改后的prompt： `a happy dog and a cute girl, watercolor style`。这样生成的图像会呈现水彩风格的效果。

![](https://static001.geekbang.org/resource/image/6b/78/6b3ef7eb2c2c4ffc946633b8abdae478.jpg?wh=3535x2480)

通过添加两个描述单词，我们可以看到整个画面发生了巨大的变化，图像的风格都变成了水彩风，这正是prompt的魅力所在！

### 二阶咒语：巧用标签

当然，我相信同学们对美的追求是无止境的。现在让我们进一步提升这幅画的质量，方法就是使用标签（tag）继续优化。

例如，在我们之前的prompt语句中添加 “best quality” 和 “masterpiece”，最终的句子会变成： `best quality, masterpiece, a happy dog and a cute girl, watercolor style`。这样的修改将进一步提升生成画面的质量。

![](https://static001.geekbang.org/resource/image/8d/8c/8dfc58c4bf9513f3947c73aeea7d4f8c.jpg?wh=3638x2480)

可以看到，画面变得更美了！SD模型的绘画技巧真是令人惊叹！不过别光顾着开心，我们仔细看一下生成的图片，似乎出现了一些问题。左下角只有小狗，可爱的小女孩似乎不见了。这正是当前SD模型的局限性，它对于prompt语句的表达能力还不够充分。

### 三阶咒语：负面提示词

为了获得更好的创作效果，我们通常需要生成多张样本，然后反复修改我们的prompt语句。社区的朋友们也称这个过程为“抽卡”，我们只能依靠运气来获取满意的图像。但作为专业的魔法师，我们还是有办法挽救这个图像的。这时，我们可以进一步结合 **负向提示词（negative prompt）** 进行创作。

具体做法就是，在negative prompt区域填入“lowres, bad anatomy, extra digits, low quality”。所谓negative prompt，代表的是我们不想拥有的特性。

![](https://static001.geekbang.org/resource/image/d6/c3/d6f3db7c7f404d81da48fa2ddb3c5fc3.jpg?wh=1452x618)

![](https://static001.geekbang.org/resource/image/9b/12/9bbe81658cdbfe3c079dfe42a6195712.jpg?wh=3642x2480)

上面这个例子可以说明，控制SD模型的确是一项挑战，但也正是这种挑战性赋予了它独特的魅力。正因为SD模型做出来的图像难以预测，才让每一次创作都充满了惊喜和探索的乐趣。

不过很多情况下，我们还是希望SD模型不要太过自由发挥。这时候就需要用到ControlNet模型。它能够更精确地控制生成的图像，让我们能够更好地实现自己的创作愿景。关于ControlNet的原理和使用技巧，我们后面的课程还会详细展开讲解，这里你先留一个大致印象就行。

### 四阶咒语：文本权重调整

好，言归正传，我们先继续探索prompt的神奇魅力。在没有ControINet的情况下，我们实际上可以通过一些巧妙的语法，让SD模型知道在prompt中要关注的重点。

这里我们需要用上一种叫做 `()` 的特殊语法来增强提示词的权重。

我们还是结合例子来体会这个语法。比方说，我们把prompt语句修改为： `best quality, masterpiece, a happy (dog) and a cute girl, watercolor style`，那么它将产生后面这样的图像。

![](https://static001.geekbang.org/resource/image/72/04/7261b4ee2b6ce6b9529bb5aac8afa304.jpg?wh=3579x2480)

对比一下前面的作品，是不是挺惊喜的？终于，欢快的小狗和可爱的女孩再次同框了，新咒语生效！

现在我们总结一下“施法”技巧：在prompt中添加 `()` ，默认情况下会让对应的单词产生1.1倍的强度。双括号 `(())` ，则表示1.1 x 1.1 倍的加强。当然，我们也可以直接将数字写上去，例如 `(dog:1.2)` 。

正确地运用这种技巧，可以帮助我们更好地控制创作的效果。不过通常情况下，我不建议该权重超过1.3，否则对画面的影响很大，甚至不能产生正常的图像。

### 中型法阵：引入LoRA

除了添加文本和文本强度的变化，我们还可以通过在prompt区域中引入LoRA来实现风格的二次变化。如果前面的还是入门程度的咒语，那LoRA就相当于让作品脱胎换骨的进阶法阵。

LoRA模型可以看作是原始模型的新特效，你可以这样理解：LoRA相当于给原有模型穿上了“新服饰”一样，能让图像呈现出不同的表现。我们这就来体会一下，在prompt区域中使用LoRA的咒语是什么效果。

我们需要先了解规范的“念咒”动作，标准写法是  <lora:模型文件名:权重>。

通常权重的范围是0到1，其中0表示LoRA模型完全不起作用。WebUI会自动加载相应的LoRA模型，并根据权重的大小进行应用。这些LoRA文件可以是自己训练的，你也可以从开源社区获取。关于LoRA的神奇之处和制作方法，我们后面的课程里会逐步介绍，敬请期待。

现在，假设我们已经获取了一个风格化的LoRA模型，例如在Civitai开源社区的 “大概是盲盒” 这个LoRA模型。

![](https://static001.geekbang.org/resource/image/25/5d/2586e3c91e0905da041844cfa745705d.jpg?wh=2406x1276)

我们将其下载并放入 stable-diffusion-webui/models/Lora文件夹，然后就可以在WebUI中看到这个模型了。

![](https://static001.geekbang.org/resource/image/46/0d/46eaab0b8b5545e6e3afcb1cd20c040d.jpg?wh=2830x1318)

现在，我们将前面学到的技巧融为一体，输入后面这样的指令。

- **prompt**： `(masterpiece),(best quality),(ultra-detailed), (full body:1.2), 1girl,chibi,cute, smile, flower, outdoors, playing guitar, jacket, blush, shirt, short hair, cherry blossoms, green headwear, blurry, brown hair, blush stickers, long sleeves, bangs, headphones, black hair, pink flower, (beautiful detailed face), (beautiful detailed eyes), <lora:blindbox_v1_mix:1>`
- **negative prompt**： `(low quality:1.3), (worst quality:1.3)`

这时，我们的新图像也将会变成后面的样式。

![](https://static001.geekbang.org/resource/image/f9/19/f98d4709d44459c43619690b409ece19.jpg?wh=3650x2480)

你看，可爱的、盲盒版本的、爱音乐的小女孩就创作出来了。想必你也发现了，相同的模型，在LoRA的加持下，生成的图像会呈现出完全不同的风格。所以，如果能成为prompt的使用高手，你就离成为WebUI的AI绘画大师更近了！

另外，开源社区还整理了许多相关的 [魔法法典](https://docs.qq.com/doc/DWHl3am5Zb05QbGVs) 供我们参考。你可以借助这些资料，寻找更多指导和灵感，进一步提升自己的技能，在AI绘画的旅程中更上一层楼。

## 文生图的引导：CFG Scale 提示词相关性

讲完最基础的prompt语句，下面让我们探讨一些配合prompt起作用的重要参数。

首先是CFG Scale，也就是我们常说的 “提示词相关性”。CFG Scale在有的教程中也叫Guidance Scale，二者是一回事。我们这就来看看这个参数又会让AI绘画作品出现怎样的奇妙反应。

在WebUI中，CFG Scale的范围是1-30，默认值为7。我们可以通过调整不同的Scale值来观察图像的变化。以输入prompt语句 “a dog, cartoon style” 为例。如下表所示，不同的Scale值会产生不同的效果。

![](https://static001.geekbang.org/resource/image/11/b8/11998c126d622b6f4f317dc1e660bbb8.jpg?wh=4409x2480)

从下一讲开始，我们便会引入一些具体的代码实操，很多代码运行需要用到GPU资源。对于没有GPU或服务器的同学来说，我们仍然可以充分利用一些免费的服务器资源，其中Google Colab便是一个不错的选择！

Google Colab是一款强大而便利的云端编程环境，具备许多优势。首先，它无需安装和配置，用户只需拥有浏览器和可靠的网络连接，即可立即开始编写和运行代码，省去了繁琐的安装步骤。其次，Google Colab是免费使用的，为学生、研究人员和开发者提供了免费的实验和学习环境。

特别提示一下，Google Colab需要用到Google账号！解决这个问题就要发挥你的聪明才智了。

![](https://static001.geekbang.org/resource/image/42/d5/42207797107b024fcb69280f9b243ed5.jpg?wh=1526x1102)

## 总结时刻

这一讲我们学习了AI绘画的很多“施法咒语（prompt技巧）”和重要参数，现在我们来做个总结。

我们今天重点学习了如何设计巧妙的prompt咒语，比如标签用法、负面提示词、文本权重控制、LoRA用法等。同时，还探索了围绕prompt的关键参数CFG Scale对于最终AI绘画成图效果的影响。

在使用SD模型进行AI绘画时，正确使用和设计prompt至关重要。prompt可以用来引导模型生成特定风格、内容或特征的图像。通过精心构思和设计prompt，你可以激发模型创造出符合你意愿的艺术作品。

CFG Scale是文生成图模型中的一个重要参数，它表示输入文本对生成图像的影响程度。较高的CFG Scale值可以使生成图像更贴近prompt的信息，但并非越高越好。通过调整CFG Scale值，你可以控制生成图像与提示之间的相似度，从而获得期望的结果。

![](https://static001.geekbang.org/resource/image/ca/27/ca88d7e916e476c607a25a003b4e7427.jpg?wh=3366x1215)

## 思考题

如果你想绘制一幅精细化的人物肖像，AI绘画生成的图像在手部和脸部细节存在瑕疵。这种情况下，有哪些方法可以改善这些问题？

期待你在留言区和我交流讨论，也推荐你把今天学到的内容分享给更多朋友，我们一起探索AI绘画的无限潜力！