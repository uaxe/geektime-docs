## 写在前面

你好，我是吴咏炜。

今天我会介绍一些我觉得好并且值得推荐的书，但我不会提供任何购买或下载链接。前者没有必要，大家应该都知道怎么搜索；后者我个人认为违反道义。这些书没有哪本是程序员买不起的。如果书作者没有提供免费下载，而市面上又买不到某本书的话，那自己偷偷找个下载渠道也情有可原——但也请你不要分享出来、告诉我或者其他人。即使你认为以后别人复制你的作品是完全没有问题的（事实上我很怀疑这点，除非你是个硬核的自由软件贡献者），也不等于你有权利复制别人的作品。

## 入门介绍

Bjarne Stroustrup, _A Tour of C++_, 2nd ed. Addison-Wesley, 2018

中文版：王刚译，《C++ 语言导学》(第二版）。机械工业出版社，2019

推荐指数：★★★★★

（也有第一版的影印版，那就不推荐了。）

这是唯一一本较为浅显的全面介绍现代 C++ 的入门书。书虽然较薄，但 C++ 之父的功力在那里（这不是废话么😂），时有精妙之论。书的覆盖面很广，介绍了 C++ 的基本功能和惯用法。这本书的讲授方式，也体现了他的透过高层抽象来教授 C++ 的理念。

* * *

Michael Wong 和 IBM XL 编译器中国开发团队，《深入理解 C++11：C++11 新特性解析与应用》。机械工业出版社，2013

推荐指数：★★★☆

这本书我犹豫了好久是否应该推荐。Michael Wong 是 C++ 标准委员会委员，内容的权威性没有问题。但这本书，从电子书版本（Kindle 和微信读书上都有此书）看，排印错误不少——校对工作没有做好。我觉得，如果你已经熟悉 C++98，想很系统地检视一下 C++11 的新特性，这本书可能还比较适合。（我只讲了一些重点的现代 C++ 特性，完整性相差很远。）

## 最佳实践

Scott Meyers, _Effective C++: 55 Specific Ways to Improve Your Programs and Designs_, 3rd ed. Addison-Wesley, 2005

中文版：侯捷译《Effective C++ 中文版》（第三版）。电子工业出版社，2011

推荐指数：★★★★

* * *

Scott Meyers, _Effective STL: 50 Specific Ways to Improve Your Use of the Standard Template Library_. Addison-Wesley, 2001

中文版：潘爱民、陈铭、邹开红译《Effective STL 中文版》。清华大学出版社，2006

推荐指数：★★★★

* * *

Scott Meyers, _Effective Modern C++: 42 Specific Ways to Improve Your Use of C++11 and C++14_. O’Reilly, 2014

中文版：高博译《Effective Modern C++ 中文版》。中国电力出版社，2018

推荐指数：★★★★★

C++ 的大牛中有三人尤其让我觉得高山仰止，Scott Meyers 就是其中之一——Bjarne 让人感觉是睿智，而 Scott Meyers、Andrei Alexandrescu 和 Herb Sutter 则会让人感觉智商被碾压。Scott 对 C++ 语言的理解无疑是非常深入的，并以良好的文笔写出了好几代的 C++ 最佳实践。我读过他整个 Effective 系列四本书，每一本都是从头看到尾，收获巨大。（之所以不推荐第二本 _More Effective C++_，是因为那本没有出过新版，1996 年的内容有点太老了。）

这几本书讨论的都是最佳实践，因此，如果你没有实际做过 C++ 项目，感触可能不会那么深。做过实际项目的一定会看到，哦，原来我也犯了这个错误啊……如果你不想一下子看三本，至少最后一本属于必修课。

值得一提的是，这三本的译者在国内都是响当当的名家，翻译质量有保证。因此，这几本看看中文版就挺好。

## 深入学习

Herb Sutter, _Exceptional C++: 47 Engineering Puzzles, Programming Problems, and Solutions_. Addison-Wesley, 1999

中文版：卓小涛译《Exceptional C++ 中文版》。中国电力出版社，2003

推荐指数：★★★★

我已经说过，我认为 Herb Sutter 是 C++ 界最聪明的三人之一。在这本书里，Herb 用提问、回答的形式讨论了很多 C++ 里的难点问题。虽然这本书有点老了，但我认为你一定可以从中学到很多东西。

* * *

Herb Sutter and Andrei Alexandrescu, _C++ Coding Standards: 101 Rules, Guidelines, and Best Practices_. Addison-Wesley, 2004

中文版：刘基诚译《C++编程规范：101条规则准则与最佳实践》。人民邮电出版社，2006

推荐指数：★★★★

两个牛人制定的 C++ 编码规范。与其盲目追随网上的编码规范（比如，Google 的），不如仔细看看这两位大牛是怎么看待编码规范方面的问题的。

* * *

侯捷，《STL 源码剖析》。华中科技大学出版社，2002

推荐指数：★★★★☆

这本是我推荐的唯二的直接以中文出版的 C++ 技术书。侯捷以庖丁解牛的方式，仔细剖析了早期 STL 的源码——对于不熟悉 STL 代码的人来说，绝对可以学到许多。我当年从这本书中学到了不少知识。虽说那里面的 STL 有点老了，但同时也更简单些，比今天主流的 STL 容易学习。

同时仍需注意，这本书有点老，也有些错误（比如，有人提到它对 `std::copy` 和 `memmove` 的说明是错的，但我已经不再有这本书了，没法确认），阅读时需要自己鉴别。但瑕不掩瑜，我还是认为这是本好书。

## 高级专题

Alexander A. Stepanov and Daniel E. Rose, _From Mathematics to Generic Programming_. Addison-Wesley, 2014

中文版：爱飞翔译《数学与泛型编程：高效编程的奥秘》。机械工业出版社，2017

推荐指数：★★★★★

Alexander Stepanov 是 STL 之父，这本书写的却不是具体的编程技巧或某个库，而是把泛型编程和抽象代数放在一起讨论了。说来惭愧，我是读了这本书之后才对群论稍稍有了点理解：之前看到的介绍材料都过于抽象，没能理解。事实上，Alexander 之前还写了一本同一题材、但使用公理推导风格的 _Elements of Programming_（裘宗燕译《编程原本》），那本就比较抽象艰深，从受欢迎程度上看远远不及这一本。我也只是买了放在书架上没看多少页😝。​

回到这本书本身。这本书用的编程语言是 C++，并引入了“概念”——虽然作者写这本书时并没有真正的 C++ 概念可用。书中讨论了数学、编程，还介绍了很多大数学家的生平。相对来说（尤其跟《编程原本》比），通过这本书是可以比较轻松地学习到泛型的威力的。哦，对了，我之前提到使用高精度整数算 RSA 就是拿这本书里描述的内容做练习。计算 RSA，从抽象的角度，只不过就是求幂和最大公约数而已……

除非抽象代数和模板编程你都已经了然于胸，否则这本书绝对会让你对编程的理解再上一个层次。相信我！

* * *

Andrei Alexandrescu, _Modern C++ Design: Generic Programming and Design Patterns Applied_. Addison-Wesley, 2001

中文版：侯捷、於春景译《C++ 设计新思维》。华中科技大学出版社，2003

推荐指数：★★★★☆

这本书算是 Andrei 的成名作了，一出版就艳惊四座。书中讨论了大量模板相关的技巧，尤其是基于策略的设计。记得在这本书出版时，大量书中的代码是不能被编译器接受的。当然，错的基本上都是编译器，而不是 Andrei。

对了，注意到英文书名中的 Modern C++ 了吗？现代 C++ 这一提法就是从他开始的，虽然那是在 C++11 发布之前十年了。可以说他倡导了新的潮流。在今天，这本书的内容当然是略老了，但它仍然是不可替代的经典作品。书里的技巧有些已经过时了（我也不推荐大家今天去使用 Loki 库），但理念没有过时，对思维的训练也仍然有意义。

* * *

Anthony Williams, _C++ Concurrency in Action_, 2nd ed. Manning, 2019

中文译本只有第一版，且有人评论“机器翻译的都比这个好”。因而不推荐中文版。

推荐指数：★★★★☆

C++ 在并发上出名的书似乎只此一本。这也不算奇怪：作者是 Boost.Thread 的主要作者之一，并且也直接参与了 C++ 跟线程相关的很多标准化工作；同时，这本书也非常全面，内容覆盖并发编程相关的所有主要内容，甚至包括在 Concurrency TS 里讨论的，尚未进入 C++17 标准（但应当会进入 C++20）的若干重要特性：barrier、latch 和 continuation。

除非你为一些老式的嵌入式系统开发 C++ 程序，完全不需要接触并发，否则我推荐你阅读这本书。

* * *

Ivan Čukić, _Functional Programming in C++_. Manning, 2019

中文版：程继洪、孙玉梅、娄山佑译《C++ 函数式编程》。机械工业出版社，2020

推荐指数：★★★★

推荐这本书我是有点私心的，毕竟我为这本书作了点小贡献，你也能在这本书里找到我的名字。因为这个，也因为这本书太新、评价太少，我也很犹豫该不该推荐。不过，鉴于在这个领域这是唯一的一本，如果你想用 C++ 语言做函数式编程的话，也没有更好的书可选了。

如果你对函数式编程有兴趣，可以读一读这本书。如果你对函数式编程不感冒，可以跳过这一本。

## 参考书

Bjarne Stroustrup, _The C++ Programming Language_, 4th ed. Addison-Wesley, 2013

中文版：王刚、杨巨峰译《C++ 程序设计语言》。机械工业出版社， 2016

推荐指数：★★★★☆

没什么可多说的，C++ 之父亲自执笔写的 C++ 语言。主要遗憾是没有覆盖 C++14/17 的内容。中文版分为两卷出版，内容实在是有点多了。不过，如果你没有看过之前的版本，并且对 C++ 已经有一定经验的话，这个新版还是会让你觉得，姜还是老的辣！

* * *

Nicolai M. Josuttis, _The C++ Standard Library: A Tutorial and Reference_, 2nd ed. Addison-Wesley, 2012

中文版：侯捷译《C++ 标准库》。电子工业出版社，2015

推荐指数：★★★★☆

Nicolai 写的这本经典书被人称为既完备又通俗易懂，也是殊为不易。从 C++11 的角度，这本书堪称完美。当然，超过一千页的大部头，要看完也是颇为不容易了。如果你之前没有阅读过第一版，那我也会非常推荐这一本。

## C++ 的设计哲学

Bjarne Stroustrup, _The Design and Evolution of C++_. Addison-Wesley, 1994

中文版：裘宗燕译《C++ 语言的设计与演化》。科学出版社， 2002

推荐指数：★★★☆

这本书不是给所有的 C++ 开发者准备的。它讨论的是为什么 C++ 会成为今天（1994 年）这个样子。如果你对 C++ 的设计思想感兴趣，那这本书会比较有用些。如果你对历史不感兴趣，那这本书不看也不会有很大问题。

* * *

Bruce Eckel, _Thinking in C++, Vol. 1: Introduction to Standard C++_, 2nd ed. Prentice-Hall, 2000

Bruce Eckel and Chuck Allison, _Thinking in C++, Vol. 2: Practical Programming_. Pearson, 2003

中文版：刘宗田等译《C++ 编程思想》。机械工业出版社，2011

推荐指数：★★★

据说这套书翻译不怎么样，我没看过，不好评价。如果你英文没问题，还是看英文版吧——作者释出了英文的免费版本。这套书适合有一点编程经验的人，讲的是编程思想。推荐星级略低的原因是，书有点老，且据说存在一些错误。但 Bruce Eckel 对编程的理解非常深入，即使在 C++ 的细节上他有错误，通读此书肯定还是会对你大有益处的。

## 非 C++ 的经典书目

W. Richard Stevens, _TCP/IP Illustrated Volume 1: The Protocols_. Addison-Wesley, 1994

Gary R. Wright and W. Richard Stevens, _TCP/IP Illustrated Volume 2: The Implementation_. Addison-Wesley, 1995

W. Richard Stevens, _TCP/IP Illustrated Volume 3: TCP for Transactions, HTTP, NNTP and the Unix Domain Protocols_. Addison-Wesley 1996

中文版翻译不佳，不推荐。

推荐指数：★★★★☆

不是所有的书都是越新越好，《TCP/IP 详解》就是其中一例。W. Richard Stevens 写的卷一比后人补写的卷一第二版评价更高，就是其中一例。关于 TCP/IP 的编程，这恐怕是难以超越的经典了。不管你使用什么语言开发，如果你的工作牵涉到网络协议的话，这套书恐怕都值得一读——尤其是卷一。

* * *

W. Richard Stevens and Stephen A. Rago, _Advanced Programming in the UNIX Environment_, 3rd ed. Addison-Wesley, 2013

中文版： 戚正伟、张亚英、尤晋元译《UNIX环境高级编程》。人民邮电出版社，2014

推荐指数：★★★★

从事 C/C++ 编程应当对操作系统有深入的了解，而这本书就是讨论 Unix 环境下的编程的。鉴于 Windows 下都有了 Unix 的编程环境，Unix 恐怕是开发人员必学的一课了。这本书是经典，而它的第三版至少没有损坏前两版的名声。

* * *

Erich Gamma, Richard Helm, Ralph Johson, John Vlissides, and Grady Booch, _Design Patterns: Elements of Reusable Object-Oriented Software_. Addison-Wesley, 1994

中文版：李英军、马晓星、蔡敏、刘建中等译《设计模式》。机械工业出版社，2000

推荐指数：★★★★☆

经典就是经典，没什么可多说的。提示：如果你感觉这本书很枯燥、没用，那就等你有了更多的项目经验再回过头来看一下，也许就有了不同的体验。

* * *

Eric S. Raymond, _The Art of UNIX Programming_. Addison-Wesley, 2003

中文版：姜宏、何源、蔡晓骏译《UNIX 编程艺术》。电子工业出版社，2006

推荐指数：★★★★

抱歉，这仍然是一本 Unix 相关的经典。如果你对 Unix 设计哲学有兴趣的话，那这本书仍然无可替代。如果你愿意看英文的话，这本书的英文一直是有在线免费版本的。

* * *

Pete McBreen, _Software Craftsmanship: The New Imperative_. Addison-Wesley, 2001

中文版：熊节译《软件工艺》。人民邮电出版社，2004

推荐指数：★★★★

这本书讲的是软件开发的过程，强调的是软件开发中人的作用。相比其他的推荐书，这本要“软”不少。但不等于这本书不重要。如果你之前只关注纯技术问题的话，那现在是时间关注一下软件开发中人的问题了。

* * *

Paul Graham, _Hackers & Painters: Big Ideas From The Computer Age_. O’Reilly, 2008

中文版：阮一峰译《黑客与画家》。人民邮电出版社，2011

推荐指数：★★★★

这本讲的是一个更玄的问题：黑客是如何工作的。作者 Paul Graham 也是一名计算机界的大神了，用 Lisp 写出了被 Yahoo! 收购的网上商店，然后又从事风险投资，创办了著名的孵化器公司 Y Combinator。这本书是他的一本文集，讨论了黑客——即优秀程序员——的爱好、动机、工作方法等等。你可以从中学习一下，一个优秀的程序员是如何工作的，包括为什么脚本语言比静态类型语言受欢迎😁……

* * *

Robert C. Martin, _Clean Code: A Handbook of Agile Software Craftsmanship_. Prentice Hall, 2008

中文版：韩磊译《代码整洁之道》。人民邮电出版社，2010

推荐指数：★★★★☆

Bob 大叔的书如果你之前没看过的话，这本是必看的。这本也是语言无关的，讲述的是如何写出干净的代码。有些建议初看也许有点出乎意料，但细想之下又符合常理。推荐。

## 其他

别忘了下面这两个重要的免费网站：

C++ Reference. [https://en.cppreference.com](https://en.cppreference.com)

C++ Core Guidelines. [https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)

这两个网站绝对是优秀的免费资源。大力推荐！

希望今天的推荐能给你提供多一些的参考方向，从而进一步提升自己。