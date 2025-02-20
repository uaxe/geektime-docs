你好，我是微扰君。

HTTP 是当今最广为使用的互联网传输协议，我们都听说过HTTP/1.0、HTTP/2.0、SPDY、HTTP/3.0等概念，但是对这几者之间的区别能如数家珍的同学却不多，比如 HTTP/2.0 在编码方面做了什么样的改进，比HTTP/1.1 的传输更快呢？

我们今天就来学习一下HTTP/2.0 为了提高传输效率而引入的用于头部压缩的杀招：**HPACK**。

HPACK应用了静态表、动态表和哈夫曼编码三种技术，把冗余的HTTP头大大压缩，常常可以达到50%以上的压缩率。其中的哈夫曼编码，底层主要就依赖了我们今天会重点学习的哈夫曼树，这也是广泛运用在各大压缩场景里的算法。

在展开讲解HTTP/2.0中的HPACK到底是怎么工作的，我们首先要来思考一下为什么要压缩HTTP的头，或者说，压缩到底又是什么呢？

## 压缩技术

我们都知道压缩技术诞生已久，在各种文件尤其是多媒体文件里，应用非常广泛，能帮助节约信息的存储空间和网络传输时间。

**之所以能压缩，主要原因就是我们存储的信息往往是有模式和冗余的**。以文本为例，大量单词的重复或者大量的空格，都是我们可以压缩的空间。原文件大小与压缩后文件大小的比值，我们就叫做压缩比，是衡量压缩算法有效性非常直观的指标。
<div><strong>精选留言（3）</strong></div><ul>
<li><img src="" width="30px"><span>Paul Shan</span> 👍（2） 💬（1）<div>如果所有字母出现的概率都相等，哈夫曼编码压缩就失败了，好像也没有什么编码能够处理这种情况。</div>2022-01-08</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/1d/64/52a5863b.jpg" width="30px"><span>大土豆</span> 👍（5） 💬（0）<div>老师说错啦，大多数语言的char类型，是两个字节，应该就C&#47;C++是一个字节，原因是很简单的，asc2码没法表示中文，char a=&#39;中&#39;，这种必须得两个字节才能存，C&#47;C++中char就不行了，得w_char，其他语言为了避免这种情况，char都设计成两个字节，当然，现在两个字节也已经装不下完整的unicode编码了，比如U+a3e8b这种码点，Java底层还得做特殊处理，这也是面试的一个考点。</div>2022-01-30</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1f/05/63/dd59ad18.jpg" width="30px"><span>加油加油</span> 👍（0） 💬（0）<div>静态哈夫曼编码能保证绝对的准确性吗，是否依赖于采样数据的数量？</div>2022-10-14</li><br/>
</ul>