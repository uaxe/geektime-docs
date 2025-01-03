> 本课程为精品小课，不标配音频

你好，我是文强。

这节课开始，我们就正式来写消息队列架构中的元数据集群部分。首先我们需要初始化一个项目，接下来我会详细讲解如何组织项目结构，以及如何编译打包 Rust 项目。

## Rust 的 bin、lib 和 mod

在初始化项目之前，我们先来学习 3 个基础概念，cargo 中的 bin、lib、mod。

在 Rust 中，项目代码是通过 bin、lib、mod 这三种形式来组织的，先介绍下它们的功能。

**1\. bin**

用来存放主入口 main 函数的目录。如下所示，它是通过 cargo.toml 中的 \[\[bin\]\] 语法指定的。name 表示编译生成的二进制文件的名称，path 表示主入口 main 函数所在的文件。当然，你可以在 cargo 文件中指定多个 \[\[bin\]\] ，生成多个目标二进制文件。

```plain
[[bin]]
name = "placement-center"
path = "src/placement-center/server.rs"

[[bin]]
name = "placement-center1"
path = "src/placement-center/server1.rs"

```

**2\. lib**

这是 Library 的简写，表示功能库的集合。比如我们有一批通用的功能，就可以通过 lib 来组织，封装成一个独立的 lib，给其他项目调用。在 [https://crates.io/](https://crates.io/) 上的各种基础功能库都是lib 的形式。从功能来看，Rust 中 lib 的概念相当于 Java Maven 中的 module。

lib 的特征是在 src 的目录下必须有一个 lib.rs 文件。比如我们在 common 目录下定义一个 base 的 Library，则它的结构如下：

```plain
├── common
│   └── base
│       ├── Cargo.toml
│       ├── src
│       │   └── lib.rs
│       └── tests
│           └── test.rs

```

**3\. mod**

这是 Module 的缩写，从功能上来看，它相当于 Java 中的 package，它用来在 lib 中组织独立的代码功能。所以可以简单理解，mod 是包含在 lib 中的。比如我们在 common 中定义一个config 的 mod，此时目录结构如下：

```plain
├── common
│   └── base
│       ├── Cargo.toml
│       ├── src
│       │   ├── config
│       │   │   └──  mod.rs
│       │   └── lib.rs
│       └── tests
│           └── test.rs

```

一般情况下，从功能上来看： **一个 lib 会包含多个 mod，一个 bin 需要调用多个 lib**。

接下来我们来看一下如何组织我们的代码结构。

## 如何组织代码结构

如果你对我之前推荐的资料看得比较仔细，可能会关注到有这一章节 [《标准的 Package 目录结构》](https://course.rs/cargo/guide/package-layout.html)。这里推荐了一个项目目录结构：

```plain
├── Cargo.lock
├── Cargo.toml
├── src/
│   ├── lib.rs
│   ├── main.rs
│   └── bin/
│       ├── named-executable.rs
│       ├── another-executable.rs
│       └── multi-file-executable/
│           ├── main.rs
│           └── some_module.rs
├── benches/
│   ├── large-input.rs
│   └── multi-file-bench/
│       ├── main.rs
│       └── bench_module.rs
├── examples/
│   ├── simple.rs
│   └── multi-file-example/
│       ├── main.rs
│       └── ex_module.rs
└── tests/
    ├── some-integration-tests.rs
    └── multi-file-test/
        ├── main.rs
        └── test_module.rs

```

从编码的角度来看，推荐的这个项目结构适合单体项目，比如微服务架构中某个服务的项目结构，它不适合复杂的项目。这是因为， **在这个项目结构中，只有一个 lib 和 bin，当项目中需要多个 lib 和多个 bin 的时候，这个目录结构就不够用了**。而大部分项目，都是需要多个 lib 和多个 bin 的。

在 cargo 的定义中， **在业务逻辑比较复杂的项目中，一般需要通过 workspace 来组织多个 lib 和 bin**。

那项目结构应该是什么样子呢？我们来看一下项目初始化后的目录结构，如下所示：

```plain
├── Cargo.toml # Cargo 的定义文件
├── LICENSE # 项目 的LICENSE 文件，比如Apache2.0
├── README.md # 项目说明 README文件
├── benches # 压测代码所在目录
├── bin # 项目启动命令存放的目录
├── build.rs # cargo中的构建脚本 build.rs。可参考这个文档:https://course.rs/cargo/reference/build-script/intro.html
├── config # 存放配置文件的目录
├── docs # 存放技术文档的目录
├── example # 存放项目调用 Demo 的项目
├── makefile # 用于编译打包项目的makefile文件
├── src  # 源代码目录
│   ├── cmd
│   │   ├── Cargo.toml
│   │   ├── src
│   │   │   └── placement-center
│   │   │       └── server.rs
│   │   └── tests
│   │       └── test.rs
│   ├── placement-center
│   │   ├── Cargo.toml
│   │   ├── src
│   │   │   └── lib.rs
│   │   └── tests
│   │       └── test.rs
│   └── protocol
│       ├── Cargo.toml
│       ├── src
│       │   └── lib.rs
│       └── tests
│           └── test.rs
├── tests # 存放测试用例代码的文件
└── version.ini  # 记录版本信息的文件

```

各个文件和目录的说明已经有标注，就不再赘述了。我们重点来看 src 目录的组织结构。这个目录结构得配合根目录的 cargo.toml 和子目录的 cargo 文件来解释，下面分别是根目录和子目录的 cargo 文件。

- 根目录 cargo.toml

```plain
[workspace]
members = [
    "src/common/base",
    "src/placement-center",
    "src/cmd",
    "src/protocol",
]

resolver = "2"

[workspace.package]
version = "0.0.1"
edition = "2021"
license = "Apache-2.0"

[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

## workspaces members
placement-center = { path = "src/placement-center" }
cmd = { path = "src/cmd" }
protocol = { path = "src/protocol" }
common-base = { path = "src/common/base" }

```

- 子目录 cargo.toml

```plain
[package]
name = "cmd"
version.workspace = true
edition.workspace = true
license.workspace = true

[dependencies]
[[bin]]
name = "placement-center"
path = "src/placement-center/server.rs"

```

这个项目结构的核心是：在项目的根目录通过 workspace 来组织管理 cmd、protocol、placement-center、common-base 等 4 个子项目。从定义上看，protocol、placement-center、common-base 是 lib 类型，分别完成相关业务逻辑，cmd 是 bin 类型。也就是说主入口 main 函数是写在 cmd/src/placement-center/server.rs 中的。

当然，在 cmd 中可以支持多个主入口 main 函数，来支持启动多个不同类型的服务。比如在最开始的架构图中有一个 Broker Server，我们就可以在 cmd 中的 toml 加一个 bin，如下所示：

```plain
[package]
name = "cmd"
version.workspace = true
edition.workspace = true
license.workspace = true

[dependencies]
[[bin]]
name = "placement-center"
path = "src/placement-center/server.rs"

[[bin]]
name = "mqtt-broker"
path = "src/mqtt-broker/server.rs"

```

从实践的角度看， **对于大多数项目** **，这个** **项目结构基本是通用的，可以直接复制**。接下来，我们来看一下如何打包项目。

## 通过 Cargo build 编译打包

在 Rust 中，打包项目是一件很简单的事情，就是在项目根目录直接执行 **cargo build** 即可。基于上面的 cargo 文件，执行完会在 target/debug目录下生成一个 placement-center 文件，效果如下：

![图片](https://static001.geekbang.org/resource/image/c6/05/c6a3731f2dyy2700d77b899c20d4f605.png?wh=1908x260)

此时，你可以执行 ./placement-center 命令，它会调用 cmd/src/placement-center/server.rs 中的主入口 main 函数，从而启动服务。如下图所示，会输出：

```plain
 Get Started

```

因为我们在 cmd/src/placement-center/server.rs 中的内容是：

```plain
fn main() {
    println!("Get Started");
}

```

这里有一点需要注意的是： **你必须先了解** **Cargo 中 Profile 的含义**。

Profile 是 Cargo 的一个功能，详细内容你可以参考这个文档 [《发布配置 Profile》](https://course.rs/cargo/reference/profiles.html)。Profile 默认包含 dev、 release、 test 和 bench 4 种配置项。正常情况下，我们无需去指定，Cargo 会根据我们使用的命令来自动进行选择。例如：

1. cargo build 自动选择 dev profile

2. cargo test 则是 test profile

3. cargo build --release 自动选择 release profile

4. cargo bench 则是 bench profile


从运行的角度，编译器会根据这 4 种不同的配置提供不同的优化机制，比如优化编译速度、优化运行速度等等。例如在开发时，我们需要更快的构建速度来验证代码。此时，我们可以牺牲运行性能来换取编译性能，所以应该选择 dev 模式。而在线上环境，我们希望代码运行得更快，可以接受编译速度降低，则需要选择 release 模式。

因为默认情况下是 dev 模式，所以我们在开发测试时，编译时可以直接使用：

```plain
cargo build

```

而发布线上包，则需要使用:

```plain
cargo build -- release

```

编译生成可执行的二进制文件后，不清楚你会不会有疑问。我们平时下载的开源软件包，一般是 .tar.gz 的形式，而且下载解压完成后的目录结构一般是下面这种形式：

```plain
.
├── bin
├── config
└── libs

```

在这种结构中，bin 目录一般放启动脚本，config 目录一般放配置文件，libs 一般放一些依赖的可执行文件。启动时通过 bin 中的启动脚本来启动服务。

那能通过 Cargo 打出这种形式的 tar.gz 的包吗？ 答案是不行的。那应该怎样打出这种包呢？

从实践来看，如果要实现类似的效果，一般需要依赖 make 和 makefile 来完成打包。

## 通过 make 和 makefile 来编译打包

可以说， **是否掌握 make 和 makefile，某种程度上意味着你是否掌握了构建大型项目的能力**。所以建议你要去了解一下 make 命令和 makefile 的语法。这块语法，网上教程很多，你直接搜一下即可，我就不推荐了。

从功能上看，make 是一个编译命令，makefile 是 make 命令的语法文件。当执行 make 命令的时候，会默认在当前目录下寻找名称为 makefile 的文件，解析文件内容，并执行完成编译。

接下来，来看我们项目的 makefile 文件，通过这个文件看一下应该如何写 makefile。

```plain
TARGET = robustmq-geek
BUILD_FOLD = ./build
VERSION:=$(shell cat version.ini)
PACKAGE_FOLD_NAME = ${TARGET}-$(VERSION)

release:
    # 创建对应目录
    mkdir -p ${BUILD_FOLD}
    mkdir -p $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}
    mkdir -p $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}/bin
    mkdir -p $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}/libs
    mkdir -p $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}/config
    # 编译 release 包
    cargo build --release

    # 拷贝 bin目录下的脚本、config中的配置文件、编译成功的可执行文件
    cp -rf target/release/placement-center $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}/libs
    cp -rf bin/* $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}/bin
    cp -rf config/* $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}/config
    chmod -R 777 $(BUILD_FOLD)/${PACKAGE_FOLD_NAME}/bin/*

    # 将目录打包成.tar.gz 文件
    cd $(BUILD_FOLD) && tar zcvf ${PACKAGE_FOLD_NAME}.tar.gz ${PACKAGE_FOLD_NAME} && rm -rf ${PACKAGE_FOLD_NAME}
    echo "build release package success. ${PACKAGE_FOLD_NAME}.tar.gz "

test:
    sh ./scripts/integration-testing.sh
clean:
    cargo clean
    rm -rf build

```

在上面的 makefile 中，我们定义了 release、test、clean 等 3 个 target，即我们的 make 支持下面三个命令：

```plain
make release # 编译项目并打包成名称为robustmq-geek-{***}-beta.tar.gz的安装包
make test # 通过脚本./scripts/integration-testing.sh 运行测试用例，
make clean # 清理编译文件

```

接下来我们用 release target 来讲一下 makefile 的语法。

1. 首先，定义了 TARGET、BUILD\_FOLD、VERSION、PACKAGE\_FOLD\_NAME 4 个变量，分别表示项目的名称、构建完成后的包的存放目录、包的版本、项目名称+版本号组成的安装包的名称。

2. release target 里面是一段 shell 代码，拆解开来主要有下面四部分逻辑：
   1. 创建对应目录

   2. 编译 release 包

   3. 拷贝 bin 目录下的脚本、config 中的配置文件、编译成功的可执行文件

   4. 将目录打包成 .tar.gz 文件

当我们写完 makefile 后，接下来就可以执行 make release 命令打包即可，打包过程如下：

![图片](https://static001.geekbang.org/resource/image/c4/ee/c47bb802149bb28bd57dd56010ff0bee.png?wh=1920x726)

打包完成后，会在 build 目录下生成一个 robustmq-geek-0.0.1-beta.tar.gz 安装包，解压后效果如下：

![图片](https://static001.geekbang.org/resource/image/b5/f9/b54de78aae17d4ae6186f14d2095e3f9.png?wh=1310x584)

到这里，我们就完成了项目的初始化、编译、打包的整个流程了。

## 总结

> tips：从本节课开始，每节课的代码都能在项目 [https://github.com/robustmq/robustmq-geek](https://github.com/robustmq/robustmq-geek) 中找到源码，有兴趣的同学可以下载源码来看。

这节课的核心，我们完成了 **如何组织项目结构** 和 **如何编译打包项目** 两个工作。如果你要初始化一个项目，你直接按照这节课的思路去组织项目就可以了。

在组织复杂的 Rust 项目时，workspace 是需要重点关注的一个功能。另外在项目组织这块，你需要多去了解 Cargo 的各种语法。在 Cargo 中提供了很多好用的命令，比如 cargo bench 可以帮你压测代码的性能，cargo test 可以运行测试用例等等。

值得一提的是，Rust 在语言基础设施这块做得非常好，所以，当你熟悉了它的各种语法后，实际的工作量是很低的。

## 思考题

从这节课开始，我们的思考题换个方式。

我会在 [https://github.com/robustmq/robustmq](https://github.com/robustmq/robustmq) 项目中发布一些 good first issue 的任务，让你来完成，目的是让你有真正动手的机会，你可以选择自己感兴趣的任务来执行。当然如果你基础更好，也可以完成一些复杂的任务。当你完成自己认领的任务后，在评论区回复即可，我会找时间 check 一下大家的完成情况。

这里是本节课推荐的相关 issue 的任务列表，请点击查看 [《Good First Issue》](http://www.robustmq.com/docs/robustmq-tutorial-cn/%e8%b4%a1%e7%8c%ae%e6%8c%87%e5%8d%97/good-first-issue/)。 欢迎给我的项目 [https://github.com/robustmq/robustmq](https://github.com/robustmq/robustmq) 点个 Star 啊！