> 你好，我是于航。这一讲是一期大咖加餐，我们邀请到了海纳老师，来跟你聊聊与 C 程序编译相关的内容。C 语言是一门语法简单，且被广泛使用的编程语言，通过观察其代码的编译流程，你能够清楚地了解一个传统编译器的基本运作原理。海纳老师会用三到四讲的篇幅，来帮助你深刻理解 C 程序的编译全过程，这也是对我们专栏内容的很好补充。感谢海纳老师，也希望你能够有所收获，对 C 语言了解得更加透彻。

你好，我是海纳，是极客时间[《编程高手必学的内存知识》](https://time.geekbang.org/column/intro/100094901?tab=catalog)的专栏作者。

作为一名编译器开发工程师，在这里我想和你聊一下 C 语言的编译过程。对于 C 语言的开发者来说，深刻理解编译的过程是十分必要的。由于 C 语言非常接近底层，所以它是一门用于构建基础设施的语言。很多时候，C 语言的开发者要理解每一行代码在 CPU 上是如何执行的。所以，有经验的开发者在看到 C 的代码时，基本都能够判断它对应的汇编语句是什么。

在接下来的几篇加餐里，我会通过一个简单的例子，来说明一个 C 编译器有哪些基本步骤。在这个过程中，你也可以进一步通过操作 gcc 的相关工具，来掌握如何查看 C 编译过程的每一步的中间结果。

接下来，我们就先从对 C 编译器基本步骤的整体了解开始吧。

## 编译的基本步骤

一个 C 语言的源代码文件，一般要经过编译和链接两个大的步骤才能变成可执行程序。其中，编译的过程是将单个C源码文件翻译成中间文件。而链接器主要用于符号解析，它负责将中间文件中的符号进行跨文件解析，进而把中间文件组成一个二进制文件。关于链接的知识，于航老师已经在这个专栏的第 27~28 讲中深入地介绍过了，所以在这里我就不赘述了。
<div><strong>精选留言（1）</strong></div><ul>
<li><img src="https://thirdwx.qlogo.cn/mmopen/vi_32/MpF5Hia4Qwibdice7Qibk3iamUVZY3KglCymK67n5YEvZjX8GbFY1J2f1RGTbNibpnvicxYZGoJL7oicfbpBIfWTCe7Gbw/132" width="30px"><span>李慧文</span> 👍（4） 💬（0）<div>居然在这里见到了海纳老师，凡代码存在处，皆可学“海”课~太棒了~</div>2022-03-14</li><br/>
</ul>