你好，我是陈天。

现在 Rust 基础篇已经学完了，相信你已经有足够的信心去应对一些简单的开发任务。今天我们就来个期中测试，实际考察一下你对 Rust 语言的理解以及对所学知识的应用情况。

我们要做的小工具是 rgrep，它是一个类似 grep 的工具。如果你是一个 \*nix 用户，那大概率使用过 grep 或者 ag 这样的文本查找工具。

grep 命令用于查找文件里符合条件的字符串。如果发现某个文件的内容符合所指定的字符串，grep 命令会把含有字符串的那一行显示出；若不指定任何文件名称，或是所给予的文件名为 **-**，grep 命令会从标准输入设备读取数据。

我们的 rgrep 要稍微简单一些，它可以支持以下三种使用场景：

首先是最简单的，给定一个字符串以及一个文件，打印出文件中所有包含该字符串的行：

```plain
$ rgrep Hello a.txt
55: Hello world. This is an exmaple text

```

然后放宽限制，允许用户提供一个正则表达式，来查找文件中所有包含该字符串的行：

```plain
$ rgrep Hel[^\\s]+ a.txt
55: Hello world. This is an exmaple text
89: Help me! I need assistant!

```

如果这个也可以实现，那进一步放宽限制，允许用户提供一个正则表达式，来查找满足文件通配符的所有文件（你可以使用 [globset](https://docs.rs/globset/0.4.8/globset/) 或者 [glob](https://docs.rs/glob/0.3.0/glob/) 来处理通配符），比如：

```plain
$ rgrep Hel[^\\s]+ a*.txt
a.txt
    55:1 Hello world. This is an exmaple text
    89:1 Help me! I need assistant!
    5:6  Use `Help` to get help.
abc.txt:
    100:1 Hello Tyr!

```

其中，冒号前面的数字是行号，后面的数字是字符在这一行的位置。

给你一点小提示。

- 对于命令行的部分，你可以使用 [clap3](https://docs.rs/clap/3.0.0-beta.4/clap/index.html) 或者 [structopt](https://docs.rs/structopt/0.3.23/structopt/)，也可以就用 env.args()。
- 对于正则表达式的支持，可以使用 [regex](https://github.com/rust-lang/regex)。
- 至于文件的读取，可以使用 [std::fs](https://doc.rust-lang.org/std/fs/index.html) 或者 [tokio::fs](https://docs.rs/tokio/1.12.0/tokio/fs/index.html)。你可以顺序对所有满足通配符的文件进行处理，也可以用 [rayon](https://docs.rs/rayon/1.5.1/rayon/) 或者 [tokio](https://docs.rs/tokio/1.12.0/tokio/) 来并行处理。
- 对于输出的结果，最好能把匹配的文字用不同颜色展示。

![](https://static001.geekbang.org/resource/image/95/1f/95d87be96953d3655daf9c3yy8b6bf1f.png?wh=2356x1318)

如果你有余力，可以看看 grep 的文档，尝试实现更多的功能。

祝你好运！

加油，我们下节课作业讲解见。