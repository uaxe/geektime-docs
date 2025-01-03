你好，我是winter。今天我们来聊聊CSS的正常流。

我想，在CSS中，大家最讨厌的大概就是排版部分了。因为早年的CSS设计上不能够很好地支持软件排版需求，导致大家需要使用很多黑科技，让很多新人望而却步。

现在CSS提供了很多种排版方式，我们有很多选项可以选择自己适合的那一种，然而，正常流却是我们绕不开的一种排版。

我们能够在网上看到关于正常流的各种资料，比如：块级格式化上下文、margin折叠等等……这一系列的概念光是听起来就令人非常头痛。

所以我相信很多同学一定会奇怪：正常流到底正常在哪里。事实上，我认为正常流本身是简单和符合直觉的东西。

我们之所以会觉得它奇怪，是因为如果我们从严苛的CSS标准角度去理解正常流，规定排版的算法，就需要引入上述那些复杂的概念。但是，如果我们单纯地从感性认知的层面去理解正常流，它其实是简单的。

下面，就让我们先抛弃掉所有的已知概念，从感性认知的角度出发，一起去理解一下正常流。

## 正常流的行为

首先，我们先从词源来讲一讲排版这件事。

在毕昇发明活字印刷之前，排版这项工作是不存在的，相应的操作叫做“雕版”。人们要想印刷书籍，就需要依靠雕版工人去手工雕刻印版。

活字印刷的出现，将排版这个词引入进来，排版是活字印刷的15道工序之一，不论是古代的木质活字印刷，还是近代的铅质活字印刷，排版的过程是由排版工人一个字一个字从字架捡出，再排入版框中。实际上，这个过程就是一个流式处理的过程。

从古代活字印刷开始，到现代的出版行业，再到今天的Web，排版过程其实并没有什么本质的变化，只不过，今天在我们的CSS中，排版需要处理的内容，不再是简单的大小相同的木字或者铅字，而是有着不同字体和字号的富文本，以及插入在富文本中大小不等的盒。

并且，在这些过程中，都会有一个正常流的存在。那么，正常流是什么样的呢？

**我们可以用一句话来描述正常流的排版行为，那就是：依次排列，排不下了换行。** 这个操作很简单吧，我想，任何一个不懂排版的人都会将其作为排版时的第一反应。

理解了正常流的基本概念，剩下的功能只需要在它的基础上延伸一下就好。

在正常流基础上，我们有float相关规则，使得一些盒占据了正常流需要的空间，我们可以把float理解为“文字环绕”。

![](https://static001.geekbang.org/resource/image/af/65/aff7250eac6064158021aea86dd4ac65.png?wh=808*424)

我们还有vertical-align相关规则规定了如何在垂直方向对齐盒。vertical-align相关规则看起来复杂，但是实际上，基线、文字顶/底、行顶/底都是我们正常书写文字时需要用到的概念，只是我们平时不一定会总结它们。

下图展示了在不同的vertical-align设置时，盒与文字是如何混合排版的。为了方便你理解，我们用代码给大家标注了基线、文字顶/底、行顶/底等概念。

![](https://static001.geekbang.org/resource/image/aa/e3/aa6611b00f71f606493f165294410ee3.png?wh=1405*164)

（点击大图查看）

除此之外，margin折叠是很多人非常不理解的一种设计，但是实际上我们可以把margin理解为“一个元素规定了自身周围至少需要的空间”，这样，我们就非常容易理解为什么margin需要折叠了。

## 正常流的原理

我们前面描述了正常流的行为，接下来我们要切换一下模式，用比较严谨的姿势来理解一下正常流。

在CSS标准中，规定了如何排布每一个文字或者盒的算法，这个算法依赖一个排版的“当前状态”，CSS把这个当前状态称为“格式化上下文（formatting context）”。

我们可以认为排版过程是这样的：

> 格式化上下文 \+ 盒/文字 = 位置

> formatting context + boxes/charater = positions

我们需要排版的盒，是分为块级盒和行内级盒的，所以排版需要分别为它们规定了块级格式化上下文和行内级格式化上下文。

与正常流一样，如果我们单纯地看格式化上下文，规则其实是非常简单的。

块级格式化上下文顺次排列元素：

![](https://static001.geekbang.org/resource/image/a5/e7/a5e1b9a77d9745499f96d25cf0a0dbe7.png?wh=948*519)

行内级格式化上下文顺次排列元素：

![](https://static001.geekbang.org/resource/image/1c/cf/1ced4fa809b30343df45e559cf0c08cf.png?wh=1027*291)

注意，块级和行内级元素的排版，受文字书写方向的影响，这里我们讲上下左右只是为了方便你直观理解。

当我们要把正常流中的一个盒或者文字排版，需要分成三种情况处理。

- **当遇到块级盒**：排入块级格式化上下文。
- **当遇到行内级盒或者文字**：首先尝试排入行内级格式化上下文，如果排不下，那么创建一个行盒，先将行盒排版（行盒是块级，所以到第一种情况），行盒会创建一个行内级格式化上下文。
- **遇到float盒**：把盒的顶部跟当前行内级上下文上边缘对齐，然后根据float的方向把盒的对应边缘对到块级格式化上下文的边缘，之后重排当前行盒。

我们以上讲的都是一个块级格式化上下文中的排版规则，实际上，页面中的布局没有那么简单，一些元素会在其内部创建新的块级格式化上下文，这些元素有：

1. 浮动元素；
2. 绝对定位元素；
3. 非块级但仍能包含块级元素的容器（如inline-blocks, table-cells, table-captions）；
4. 块级的能包含块级元素的容器，且属性overflow不为visible。

这里的最后一条比较绕，实际上，我个人喜欢用另一种思路去理解它：

自身为块级，且overflow为visible的块级元素容器，它的块级格式化上下文和外部的块级格式化上下文发生了融合，也就是说，如果不考虑盒模型相关的属性，这样的元素从排版的角度就好像根本不存在。

好了，到这里我们已经讲完了正常流的排版详细规则，但是理解规则仅仅是基础，我们还需要掌握一些技巧。

## 正常流的使用技巧

现在，我们就一起来动手用实际的例子来研究一下。我们今天来看看等分布局和自适应宽，从这两种经典布局问题入手，一起来探索一下正常流的使用技巧。

### 等分布局问题

横向等分布局是一个很常见的需求，按照一般的思路，我们可以使用百分比宽度来解决，我们参考以下代码：

```
<div class="outer">
    <div class="inner"></div>
    <div class="inner"></div>
    <div class="inner"></div>
</div>
.inner {
    width:33.33%;
    height:300px;
    display:inline-block;
    outline:solid 1px blue;
}

```

在这段HTML代码中，我们放了三个div，用CSS给它们指定了百分比宽度，并且指定为inline-block。

但是这段代码执行之后，效果跟我们预期不同，我们可以发现，每个div并非紧挨，中间有空白，这是因为我们为了代码格式加入的换行和空格被HTML当作空格文本，跟inline盒混排了的缘故。

解决方案是修改HTML代码，去掉空格和换行：

```
<div class="outer"><div class="inner"></div><div class="inner"></div><div class="inner"></div></div>

```

但是这样做影响了源代码的可读性，一个变通的方案是，改变outer中的字号为0。

```
.inner {
    width:33.33%;
    height:300px;
    display:inline-block;
    outline:solid 1px blue;
    font-size:30px;
}
.outer {
    font-size:0;
}

```

在某些浏览器中，因为像素计算精度问题，还是会出现换行，我们给outer添加一个特定宽度：

```
.inner {
    width:33.33%;
    height:300px;
    display:inline-block;
    outline:solid 1px blue;
}
.outer {
    width:101px
}

```

这个代码在某些旧版本浏览器中会出现换行。为了保险起见，我们给最后一个div加上一个负的右margin：

```
.outer {
    width:101px
}

.inner {
    width:33.33%;
    height:300px;
    display:inline-block;
    outline:solid 1px blue;
}

.inner:last-child {
    margin-right:-5px;
}

```

这样就可以解决旧版本浏览器的问题了。

除了使用inline-block，float也可以实现类似的效果，但是float元素只能做顶对齐，不如inline-block灵活。

### 自适应宽

我们再来说说自适应宽。在IE6统治浏览器市场的旧时代，自适应宽（一个元素固定宽度，另一个元素填满父容器剩余宽度）是个经典的布局问题，我们现在就看一下如何使用正常流来解决。

我们首先来看一下问题。

```
<div class="outer">
    <div class="fixed"></div>
    <div class="auto"></div>
</div>
.fixed {
    width:200px;
}
.fixed, .auto {
    height:300px;
    outline:solid 1px blue;
}

```

这里fixed这个div宽度已经被指定好，我们需要添加css代码尝试让.auto填满剩余宽度。

使用正常流解决这个问题的思路是，利用负margin：

```
.fixed {
    display:inline-block;
    vertical-align:top;
}
.auto {
    margin-left:-200px;
    width:100%;
    display:inline-block;
    vertical-align:top;
}

```

但是，这样做会导致auto中的内容位置不对，所以我们还需要使用padding把内容挤出来，最终完整代码如下：

```
.fixed {
    display:inline-block;
    vertical-align:top;
}
.auto {
    margin-left:-200px;
    padding-left:200px;
    box-sizing:border-box;
    width:100%;
    display:inline-block;
    vertical-align:top;
}

```

这样就给auto添加了padding-left和box-sizing两个属性。

总的来说，正常流布局主要是使用inline-block来作为内容的容器，利用块级格式化上下文的纵向排布和行内级格式化上下文的横向排布来完成布局的，我们需要根据需求的横向和纵向排布要求，来选择元素的display属性。

## 结语

这次的文章中，我们一起学习了正常流，我们可以用一句话来描述正常流的排版行为，那就是：依次排列，排不下了换行。这也是理解它最简单最源头的方式。

我们将正常流的知识分成了三个部分。

- 正常流的行为部分，我们从一些感性认知出发，帮助你从思路和源头上理解正常流的行为。

- 正常流的原理部分，我用更严格的描述方式，给你讲解了CSS标准中规定的正常流排版逻辑。

- 最后的正常流应用部分，我以两个经典布局问题等分布局和自适应宽为例，为你讲解了正常流实际使用的一些技巧。


最后，留给你一个思考题：用JavaScript写一个仅包含inline-block的正常流布局算法。你写好的话，可以留言给我，我们一起讨论。

# 猜你喜欢

[![unpreview](https://static001.geekbang.org/resource/image/1a/08/1a49758821bdbdf6f0a8a1dc5bf39f08.jpg?wh=1032*330)](https://time.geekbang.org/course/intro/163?utm_term=zeusMTA7L&utm_source=app&utm_medium=chongxueqianduan&utm_campaign=163-presell)