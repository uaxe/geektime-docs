你好，我是winter，今天我们继续来聊聊HTML模块的语义类标签。

在上一篇文章中，我花了大量的篇幅和你解释了正确使用语义类标签的好处和一些场景。那么，哪些场景适合用到语义类标签呢，又如何运用语义类标签呢？

不知道你还记不记得在大学时代，你被导师逼着改毕业论文格式的情景，如果你回想一下，你在论文中使用的那些格式，你会发现其实它们都是可以用HTML里的语义标签来表示的。

这正是因为HTML最初的设计场景就是“超文本”，早期HTML工作组的专家都是出版界书籍排版的专家。

所以，在这一部分，我们找了个跟论文很像的案例：Wikipedia文章，这种跟论文相似的网站比较适合用来学习语义类标签。通过分析一篇Wiki的文章用到的语义类标签，来进一步帮你理解语义的概念。

你可以在电脑上，打开这个页面：

- [https://en.wikipedia.org/wiki/World\_Wide\_Web](https://en.wikipedia.org/wiki/World_Wide_Web)

为了防止这个页面被修改，我们保存了一个副本：

- [http://static001.geekbang.org/static/time/quote/World\_Wide\_Web-Wikipedia.html](http://static001.geekbang.org/static/time/quote/World_Wide_Web-Wikipedia.html)

这是一篇我们选择的Wiki文章，虽然在原本的Wikipedia网站中，也是大量使用了div和span来完成功能。在这里，我们来尝试分析一下，应该如何用语义类标签来呈现这样的一个页面/文章。

我们看一下这个页面。

## aside

![](https://static001.geekbang.org/resource/image/b6/da/b692ade1e78d295de52ffe01edaa11da.png?wh=1435*684)

首先我们来看下，左侧侧边栏，根据上一篇文章中提到的语义定义，这里属于aside内容。是导航性质的工具内容。

## article

![](https://static001.geekbang.org/resource/image/cf/aa/cfc9a6542e0fc973e6e871043e7e42aa.jpeg?wh=1435*690)

我们来到文章主体部分，因为主体部分具有明确的独立性，所以可以用article来包裹。

## hgroup, h1, h2

![](https://static001.geekbang.org/resource/image/7d/48/7ddad196e7734fd32bfc577b3a459c48.jpeg?wh=1433*687)

在语义的上一篇文章中，我们介绍过hgroup和h1-h6的作用，hgroup是标题组，h1是一级标题，h2是二级标题。这里，World Wide Web 是文章的大标题，适合h1元素。

接下来出现了一个副标题。From Wikipedia, the free encyclopedia。这个地方适合使用h2，跟h1组成一个hgroup，所以代码可能是类似这样的:

```html
<hgroup>
<h1>World Wide Web </h1>
<h2>From Wikipedia, the free encyclopedia</h2>
</hgroup>

```

## abbr

![](https://static001.geekbang.org/resource/image/13/72/139b1603d3851b11e9ee4ed955aec972.png?wh=1424*690)

abbr标签表示缩写。考虑到WWW是World Wide Web的缩写，所以文中所有出现的WWW，都应该使用abbr标签。

```html
<abbr title="World Wide Web">WWW</abbr>.

```

## hr

![](https://static001.geekbang.org/resource/image/3e/1e/3e3fca7df41dd824da47efca4aa2731e.jpeg?wh=1426*688)

细心的同学会发现，在Wiki的界面中，出现了一条很长的横线，大家都知道hr标签表示横向分隔线，那么这个地方是不是应该用hr呢？

答案是不用。我们读一下标准的定义就知道了，hr表示故事走向的转变或者话题的转变，显然此处两个标题并非这种关系，所以我们应该使用CSS的border来把它当作纯视觉效果来实现，所以这里是不需要用hr的。

## p

![](https://static001.geekbang.org/resource/image/a5/d4/a5c22955f87e2861cadfa3fdb15565d4.jpeg?wh=1434*691)

接下来一段，我们看到了三段“note”，也就是注记。它在文章中用作额外注释。

> “WWW” and “The Web” redirect here. For other uses of WWW, see WWW (disambiguation). For other uses of web, see Web (disambiguation).
>
> For the first web software, see WorldWideWeb.
>
> Not to be confused with the Internet.

HTML中并没有note相关的语义，所以，我们用普通的p标签，加上 `class="note"` 来实现。后面的多数自然段都是普通的段落，我们用p标签来实现。

## strong

![](https://static001.geekbang.org/resource/image/d7/a1/d7f8b1f98df1488813c3fc2d6b06d5a1.jpeg?wh=1422*702)

注意，这里 “World Wide Web (WWW)” 和 “the Web” 使用了黑体呈现，从上下文来看，这里表示这个词很重要，所以我们使用strong标签。

```
<p>
A global map of the web index for countries in 2014
<strong>The World Wide Web (WWW)</strong>, also called <strong>the Web</strong>,
......

```

## blockquote, q, cite

![](https://static001.geekbang.org/resource/image/e5/1a/e516e5e00ecc5b6b0b743dd2a8d65d1a.png?wh=1227*358)

接下来我们看到了一个论文中很常见的用法“引述”。

> interlinked by hypertext links, and accessible via the Internet.\[1\]

注意看这里的\[1\]，当我们把鼠标放上去的时候，出现了引述的相关信息：

> “What is the difference between the Web and the Internet?”. W3C Help and FAQ. W3C. 2009. Archived from the original on 9 July 2015. Retrieved 16 July 2015.

在HTML中，有三个跟引述相关的标签blockquote表示段落级引述内容，q表示行内的引述内容，cite表示引述的作品名。

这里的作品名称 “What is the difference between the Web and the Internet?”，应当使用cite标签。

```
<cite>"What is the difference between the Web and the Internet?"</cite>. W3C Help and FAQ. W3C. 2009. Archived from the original on 9 July 2015. Retrieved 16 July 2015.

```

在文章的结尾处，有对应的 References 一节，这一节中所有的作品名称也应该加入cite标签。

![](https://static001.geekbang.org/resource/image/31/45/31246e3ebf6426bfd6b1373a0644b245.png?wh=1271*509)

这里我们看看引用的原文就可以知道，Wiki文章中的信息并非直接引用，如果是直接引用的内容，那么，我们还应该加上blockquote或者q标签。

## time

![](https://static001.geekbang.org/resource/image/95/b6/9573647112ae3812013b37c29aa7d2b6.png?wh=1227*358)

这里除了引用的文章外，还出现了日期，为了让机器阅读更加方便，可以加上time标签：

```
<cite>"What is the difference between the Web and the Internet?"</cite>. W3C Help and FAQ. W3C. 2009. Archived from the original on <time datetime="2015-07-09">9 July 2015</time>. Retrieved <time datetime="2015-07-16">16 July 2015</time>.

```

## figure, figcaption

![](https://static001.geekbang.org/resource/image/6d/72/6d473b6fb734ea85a8cc209bc1716b72.png?wh=1431*685)

我们注意一下文章的右侧，出现了几张图片，这种出现在文中的图片，不仅仅是一个img标签，它和下面的文字组成了一个figure的语法现象，figure也是我们的一种标签（用于表示与主文章相关的图像、照片等流内容）。

```
<figure>
 <img src="https://.....440px-NeXTcube_first_webserver.JPG"/>
 <figcaption>The NeXT Computer used by Tim Berners-Lee at CERN.</figcaption>
</figure>

```

这种插入文章中的内容，不仅限图片，代码、表格等，只要是具有一定自包含性（类似独立句子）的内容，都可以用figure。这里面，我们用figcaption表示内容的标题，当然，也可以没有标题。

## dfn

![](https://static001.geekbang.org/resource/image/b7/19/b7ae53127450b496729edd459cbc0619.png?wh=1418*616)

然后我们继续往下看，来注意这一句：

> The terms Internet and World Wide Web are often used without much distinction. However, the two are not the same. The Internet is a global system of interconnected computer networks. In contrast, the World Wide Web is a global collection of documents and other resources, linked by hyperlinks and URIs.

这里分别定义了Internet和World Wide Web，我们应该使用dfn标签。

```

The terms Internet and World Wide Web are often used without much distinction. However, the two are not the same.
The <dfn>Internet</dfn> is a global system of interconnected computer networks.
In contrast, the <dfn>World Wide Web</dfn> is a global collection of documents and other resources, linked by hyperlinks and URIs.

```

代码中你可以看见，你需要在你要定义的词前后放上dfn标签，所以我们知道了，dfn标签是用来包裹被定义的名词。

## nav, ol, ul

![](https://static001.geekbang.org/resource/image/c1/f6/c12c129af98f6aa99b7dcdbdef1f62f6.png?wh=1420*675)

接下来，几个普通的段落之后，我们看到了文章的目录。这里的目录链接到文章的各个章节，我们可以使用nav标签。因为这里的目录顺序不可随意变化，所以我们这里使用多级的ol结构。

```
<nav>
  <h2>Contents</h2>
  <ol>
    <li><a href="...">History</a></li>
    <li><a href="...">Function</a>
      <ol>
        <li><a href="...">Linking</a></li>
        <li><a href="...">Dynamic updates of web pages</a></li>
        ...
      </ol>
    </li>
    ...
  </ol>
</nav>

```

我们这里必须要指出，ol和ul的区分是内容是否有顺序关系，每一项的前面不论是数字还是点，都不会影响语义的判断。所以，你可以注意一下这里，不要因为视觉表现效果，而改变语义的使用。

## pre, samp, code

![](https://static001.geekbang.org/resource/image/ab/ed/ab5be608e3b4d2bd15b79c5b8885a2ed.png?wh=1365*647)

继续往下，我们来到了这里，我们看见这篇文章有一个很重要的特色，文章中嵌入了一些代码和一些预先编写好的段落。我们看到在“Function”小节中有一段背景色是灰色的文字。

```
GET /home.html HTTP/1.1
Host: www.example.org

```

这是一段HTTP协议的内容描述，因为这段内容的换行是非常严格的，所以我们不需要浏览器帮我们做自动换行，因此我们使用了pre标签，表示这部分内容是预先排版过的，不需要浏览器进行排版。

又因为这是一段计算机程序的示例输出，所以我们可以使用samp标签：

```
<pre><samp>
GET /home.html HTTP/1.1
Host: www.example.org
</samp></pre>

```

接下来Wiki中的内容出现了一段HTML代码，我们同样不希望浏览器做自动换行。

```
<html>
  <head>
    <title>Example.org – The World Wide Web</title>
  </head>
  <body>
    <p>The World Wide Web, abbreviated as WWW and commonly known ...</p>
  </body>
</html>

```

因为同时是代码，我们还需要加上code标签。最后的代码是pre标签包裹了code标签，code标签包裹了HTML代码。

```
<pre><code>
&lt;html&gt;
  &lt;head&gt;
    &lt;title&gt;Example.org – The World Wide Web&lt;/title&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;p&gt;The World Wide Web, abbreviated as WWW and commonly known ...&lt;/p&gt;
  &lt;/body&gt;
&lt;/html&gt;
</code></pre>

```

在后面的代码中，还有一些在行内的code，比如 title和 p括起来的内容，这些也都应该使用code标签。

### 总结

在这一篇Wiki文章中，已经涉及了大部分语义标签，可见HTML工作组对语义标签的增加是非常谨慎和保守的。

当然了，我们选择的案例不可能刚巧覆盖所有的标签，还有些没讲到的标签，我们这里稍微做一下简要的补充说明。

![](https://static001.geekbang.org/resource/image/96/9e/9684130e423b6734b23652f4f0b6359e.jpg?wh=624*628)

（长按点击大图查看）

实际上，HTML这种语言，并不像严谨的编程语言一样，有一条非此即彼的线。一些语义的使用其实会带来争议，所以我的建议是：你可以尽量只用自己熟悉的语义标签，并且只在有把握的场景引入语义标签。这样，我们才能保证语义标签不被滥用，造成更多的问题。

你最擅长使用哪些语义标签，会把它们用在哪些场景里呢？欢迎留言告诉我，我们一起讨论。

# 猜你喜欢

[![unpreview](https://static001.geekbang.org/resource/image/1a/08/1a49758821bdbdf6f0a8a1dc5bf39f08.jpg?wh=1032*330)](https://time.geekbang.org/course/intro/163?utm_term=zeusMTA7L&utm_source=app&utm_medium=chongxueqianduan&utm_campaign=163-presell)