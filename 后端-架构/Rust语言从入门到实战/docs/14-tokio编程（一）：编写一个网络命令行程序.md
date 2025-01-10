你好，我是Mike，上一节课我们了解了Rust异步编程和tokio的基础知识，今天我们就来一起用tokio做一个小应用。

## 准备阶段

我们常常需要知道远程服务器上的一些信息，这有一些现成的工具可以做到。我们来试一下如何使用tokio实现这一功能。

**目标：** 编写一个获取服务器时间的命令行程序。

**任务分解：**

1. 命令行：这个工具取名为 getinfo, 参数格式是 `getinfo {ip}`，就是在 getinfo 后接IP地址，获取服务器时间。
2. tcp server：监听 8888 端口，获取从客户端来的请求，然后获取服务器本地时间，返回。
3. tcp client：连接服务端地址 `ip:port`，向服务端发送获取服务器时间指令。
4. 测试。

## 实现

下面我们开始实现。

### 创建项目

我们打开终端或者IDE中的Terminal，执行：

```plain
cargo new --bin getinfo

```

### 命令行雏形

Rust标准库中实际已经有获取命令行参数的功能， `std::env` 提供了一种获取命令行参数的方法 [std](https://doc.rust-lang.org/std/index.html):: [env](https://doc.rust-lang.org/std/env/index.html):: [args](https://doc.rust-lang.org/std/env/fn.args.html#)()，可以将命令行参数转换成一个迭代器，通过 for 循环就可以遍历所有命令行参数，当然也可以使用迭代器上的 `.nth()` 直接定位到某一个参数。比如：

```plain
let addr = env::args()
    .nth(1)
    .unwrap_or_else(|| "127.0.0.1:8888".to_string());

```

有了这个功能，我们就可以得到命令行的初始版本。

```plain
use std::env;

fn main() {
  let addr = env::args()
    .nth(1)
    .unwrap_or("127.0.0.1:8888".to_string());

  println!("{}", addr);
}

```

检查一下Cargo.toml中的配置，我们的应用名字应该叫 getinfo。

```plain
[package]
name = "getinfo"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]

```

执行 cargo build 编译，会出现 target 目录。

```plain
Cargo.lock  Cargo.toml  src/  target/

```

执行 `cargo run` 或 `./target/debug/getinfo`。可以得到输出 `127.0.0.1:8888`。

而执行 `cargo run -- 127.0.0.1:8000` 或 `./target/debug/getinfo 127.0.0.1:8000`，可以得到输出 `127.0.0.1:8000`。

这里我们来分析一下这个命令行的形式。

```plain
./target/debug/getinfo ip_address

```

命令行参数从左到右按序号从0开始计数，上面命令中， `./target/debug/getinfo` 序号为 0， `ip_address` 部分序号就是 1，如果后面还有其他参数，那么序号依次递增。所以你就可以理解为什么我们上面的代码中，使用 `.nth(1)` 取IP地址的信息。

标准库中命令行相关的功能虽然比较初级，但是对于我们的例子来说，已经够用了。Rust生态中有个非常好用的写命令行的库： [clap](https://crates.io/crates/clap)，如果你想写一个功能丰富的命令行程序，可以去尝试一下这个 clap。

下面我们就要开始 tokio tcp server 的创建。

### 添加依赖

先加入tokio的依赖，在项目目录下执行命令。

```plain
cargo add tokio --features full
cargo add tokio-util --features full
cargo add futures
cargo add bytes

```

执行完这几个添加依赖的命令后，Cargo.toml文件现在看起来是类似下面这个样子：

```plain
mike@LAPTOP-04V0EV33:~/works/jikeshijian/getinfo$ cat Cargo.toml
[package]
name = "getinfo"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
bytes = "1.5.0"
futures = "0.3.29"
tokio = { version = "1.33.0", features = ["full"] }
tokio-util = { version = "0.7.10", features = ["full"] }

```

`cargo add` 工具为我们准确配置了具体依赖库的版本号和特性。

### 基于tokio实现tcp server

我们的tcp server实际要干下面几件事儿。

1. 接收tcp client的连接，每一个新连接创建一个新的task。
2. 读取tcp client发过来的指令数据。
3. 根据指令，获取服务器本地的时间信息。
4. 将得到的信息字符串写入socket，返回给客户端。

```plain
use std::env;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use tokio::process::Command;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = env::args()
        .nth(1)
        .unwrap_or_else(|| "127.0.0.1:8888".to_string());
    println!("Listening on: {}", addr);
    let listener = TcpListener::bind(&addr).await?;

    // 注意这里是一个无条件循环，表明始终处于服务状态
    loop {
        // 等待客户端请求连上来
        let (mut socket, _) = listener.accept().await?;

        // 来一个客户端连接，创建一个对应的新任务
        tokio::spawn(async move {
            // 分配一个缓冲存
            let mut buf = [0; 1024];
            let mut offset = 0;
            // 循环读，因为不能确保一次能从网络线路上读完数据
            loop {
                // 读操作，返回的n表示读了多少个字节
                // 正常情况下，读到数据才会返回，如果没有读到，就会等待
                let n = socket
                    .read(&mut buf[offset..])
                    .await
                    .expect("failed to read data from socket");

                // n返回0的情况，是碰到了EOF，表明远端的写操作已断开，这个一定要判断
                if n == 0 {
                    // 碰到了EOF就直接返回结束此任务，因为后面的操作没了意义
                    return;
                }

                println!("offset: {offset}, n: {n}");
                let end = offset + n;
                // 转换指令为字符串
                if let Ok(directive) = std::str::from_utf8(&buf[..end]) {
                    println!("{directive}");
                    // 执行指令对应的工作
                    let output = process(directive).await;
                    println!("{output}");
                    // 向客户端返回处理结果
                    socket
                        .write_all(&output.as_bytes())
                        .await
                        .expect("failed to write data to socket");
                } else {
                    // 判断是否转换失败，如果失败，就有可能是网络上的数据还没读完
                    // 要继续loop读下一波数据
                    offset = end;
                }
            }
        });
    }
}

async fn process(directive: &str) -> String {
    if directive == "gettime" {
        // 这里我们用了unwrap()是因为我们一般确信执行date命令不会失败
        // 更可靠的做法是对返回的Result作处理
        let output = Command::new("date").output().await.unwrap();
        String::from_utf8(output.stdout).unwrap()
    } else {
        // 如果是其他指令，我们目前返回 无效指令
        "invalid command".to_owned()
    }
}

```

代码中有详细解释，这里我也补充说明一下。

首先，我们给main函数指定了返回类型： `Result<(), Box<dyn std::error::Error>>`。错误类型部分是一个用 `Box<T>` 装盒的trait object，这个trait object是针对标准库中的Error trait的。在这里的意思是，凡是实现了Error trait的类型都可以作为错误类型从main函数中返回。

第12行 `let listener = TcpListener::bind(&addr).await?;` 行末有一个问号，这是Rust里的问号操作符，意思是.await 得到数据后是一个 `Result<>`，如果这个 `Result<>` 是Ok值，那就解开它，返回里面的内容，这个例子里是一个TcpListener实例；而如果这个 `Result<>` 是Err值，那就直接从函数中返回，不再往下执行。问号操作符在这里起一个防御式编程的作用，能够让流程代码显得更简洁。

注意第15行是一个loop无条件循环，也就是死循环。为什么呢？因为这是个服务端程序，是需要一直跑着的，退出就意味着出问题了。

第17行，监听客户端来的连接，来一个就产生一个 socket 实例。我们看到，在let后面用了模式匹配写法，直接把元组析构了。如果来了多个连接，就会产生多个task，它们之间互不干扰，是并发处理的。

第20行，针对每一个连上的客户端连接，创建一个新的tokio轻量级线程task，来处理对应的任务。继续往下，第22行，可以看到，这个服务端程序为每个连接创建了一个缓冲区，大小是1024字节。从网络上读到的数据会放在这个缓冲区里面。

第25行，再次用了一个循环。因为网络上的数据是呈流的形式过来的，在一次CPU读取它之前，这些数据有可能还没完全到达服务器上面。因此可能需要多次读。读没读够，可以尝试把已经读到数据转换成字符串，看是否能成功来判断（这个判断方式并不严谨，这里主要用于说明流程）。如果成功了，就调用 `process()` 业务函数来计算。

process()异步函数中使用了 `tokio::process::Command` 类型来调用系统中的 `date` 命令，这是一个Linux下的查看系统日期时间的命令，会输出下面这种格式：

```plain
Tue Oct 31 14:56:27 CST 2023

```

注：如果你使用Windows的话，可以找找Windows里的替代命令。

`process()` 函数会返回这个字符串。

然后，通过同一个 socket，将数据返回给客户端连接： `socket.write_all`。

在多次读的过程中，要注意偏移量offset的处理。可以看到，代码量虽然不多，但是充满了细节，请你仔细品味一下。

### 基于tokio实现tcp client

下面我们来看对应的tcp客户端应该怎么实现。

因为我们要马上再创建一个可执行程序，所以默认的 `cargo run` 命令就不能满足这个需求，它默认只能启动一个二进制文件。我们需要改一下Cargo.toml的配置，在文件中加入一些内容。

```plain
[[bin]]
name = "server"
path = "src/server.rs"

[[bin]]
name = "client"
path = "src/client.rs"

```

然后把src目录下的 main.rs 改成 server.rs，并创建一个新文件 client.rs，代码如下：

```plain
use std::env;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = env::args()
        .nth(1)
        .unwrap_or_else(|| "127.0.0.1:8888".to_string());
    // 连接到服务端
    let mut stream = TcpStream::connect(&addr).await?;

    // 写入指令数据，这是一种最简单的协议.
    stream.write_all(b"gettime").await?;

    // 等待tcp server的回复，读取内容
    // 这里用动态数组来存储从服务端返回的内容
    let mut buf: Vec<u8> = Vec::with_capacity(8128);
    // 读取的缓冲区
    let mut resp = [0u8; 2048];
    loop {
        // 尝试一次读，返回读到的字节数
        let n = stream.read(&mut resp).await?;
        // 将读到的字节合并到buf中去
        buf.extend_from_slice(&resp[0..n]);
        if n == 0 {
            // 流断掉了
            panic!("Unexpected EOF");
        } else if buf.len() >= 28 {
            // like: "Tue Oct 31 14:56:27 CST 2023"
            // buf 已经填充了足够的内容
            break;
        } else {
            // buf 中还没有足够多的内容，继续填充...
            continue;
        }
    }

    // 转换并打印返回的信息
    let timeinfo = String::from_utf8(buf)?;
    println!("{}", timeinfo);

    Ok(())
}

```

代码中有详细解释，这里我也做一下补充说明。

第11行，我们使用 `TcpStream::connect()` 连到服务端上去，注意这点和服务端的监听是不同的。然后第14行，向tcp连接中写入协议指令，这里就是简单的字节串： `b"gettime"`。

然后第17行到25行，我们采用了另外一种方式来存储读回来的数据，这里用到了动态数组Vec的 `API extend_from_slice()`，这个的好处是不需要由自己来维护每次读到的偏移量。第21行，我们再次使用了loop，还是同样的原因，网络上的数据流，我们有可能一次读取不完，需要多次读才行。

第29行是跳出此循环的判断条件，这里是因为我们知道会返回 date 命令的输出结果，它是固定的28个字节的长度。这个条件相当死板，这里也只是起演示作用。

最后就把这个从服务端程序得到的内容打印出来。下面我们开始测试。

### 测试

编译运行服务端：

```plain
cargo run --bin server 或 cargo run --bin server -- 127.0.0.1:8888

```

编译执行客户端：

```plain
cargo run --bin client 或 cargo run --bin client -- 127.0.0.1:8888

```

查看执行效果。

服务端打印：

```plain
Listening on: 127.0.0.1:8888
offset: 0, n: 7
gettime
Tue Oct 31 15:04:08 CST 2023

```

客户端打印：

```plain
Tue Oct 31 15:07:48 CST 2023

```

这样，我们就成功实现了我们的第一个命令行应用，并完整体验了tokio网络编程。

## Frame 层

前面我们的实现，完成了这个应用初步的功能。但是实际上对于我们初学者来说，难度还是比较大，主要体现在4个方面。

1. 什么时候要加loop，什么时候不加？
2. 两个端的合法性判定条件是什么？能否推广到适用面更广的方式？
3. 多次读取的偏移量或缓冲区如何准确维护？
4. tcp网络协议的背景知识，服务端与客户端的基本概念，EOF在什么条件下触发等等。

其中前面三条都属于实现层面的细节，我们可以来了解一下产生这些复杂性的原因。

### 复杂性的来源

我们知道，一个tcp连接就像一个管道一样，里面流过的是一个个的字节，也就是说，它传输的是一个字节流。然而，由于网络本身的复杂性，比如如果服务器在很远的地方，数据有可能要经历过很多次路由器/交换机才能到达，有可能一个字节和下一个字节之间会间隔一段时间才能传过来。这时候，直接在 socket 上做的一次 read，并不能保证就一定读完整了我们想要的内容，有可能只读到了一个片段而已。

这个问题其实属于传输层的问题，不应该让上层业务开发人员来担忧。如果在考虑业务的同时，还要考虑这种底层问题的话，总会感觉施展不开，各种细节会缠得你寸步难行。

比如有两个人A和B，A给B发送两条消息msg\_a和msg\_b，B 接收消息的时候，一般会希望编程接口每次拿到一个完整的消息，第一次取是msg\_a，不多也不少；第二次取是 msg\_b，不多也不少。不会担心每次取的时候，消息可能取不完整，需要用一个循环重复取，并且还得把每次取到的片段拼接成一个大的完整的消息内容。

当消息体小的时候，可能问题不明显，当消息体大的时候，比如一次有几兆内容的时候，这个问题其实就无法忽略了。

好在tokio框架已经为我们考虑了这个问题。tokio生态引入了Frame的概念，Frame就是一个帧/框，一个Frame里可以包含一段完整的可预期的信息。相当于它在tcp这一层之上又抽象了一层，封装了具体怎么读取和切分原始的字节序列这个问题。Frame让我们读到的总是业务关心的一批批数据：msg。Frame机制将网络流的原始字节序列转换成Frame序列，并且会自动帮我们确定Frame的边界在哪里。

### Frame编解码

既然是Frame，就涉及到采用何种编码的问题。Frame本身只是一个框的概念，这个框里面具体填什么格式的内容，是由编码决定的，写入的时候编码，取出的时候需要解码。

与 tokio 配套的 tokio\_util crate 里，提供了四种最简单的编解码类型：BytesCodec、LinesCodec、AnyDelimiterCodec、LengthDelimitedCodec。我们分别介绍一下。

- BytesCodec

Frame长度为1的编解码。一个字节一个Frame。适用于文本和二进制的任何网络协议。如果你的应用就想一个字节一个字节地处理数据流，这个就是合适的选择。

- LinesCodec

行编解码协议，它使用 `\n` 作为Frame之间的分隔。这个协议用得很多，特别适合文本网络协议。

- AnyDelimiterCodec

指定间隔符的编解码协议，这个相当于LinesCodec的扩展版本。用这个协议，你可以自定义任何Frame分隔符，比如 ; , # 等等。它也比较适用于文本网络协议。

- LengthDelimitedCodec

长度分隔编解码协议。这个协议的思路是，每一个msg发送的时候，在它前面，都加上一个固定位数的长度表示前缀。这样，每次读到这个前缀数字的时候，就知道接下来要读多少个字节，才会形成一个完整的Frame。比如编码后的一个Frame类似下面这个样子：

```plain
+----------+--------------------------------+
| len: u32 |          frame payload         |
+----------+--------------------------------+

```

这个方法是协议设计的典型方法，具有非常强的通用性，适用于文本或二进制的网络协议。

tokio不仅提供了这些默认的简单的编解码方案，它还允许你自定义Codec。如果上面4种都不能满足你的需求，你完全可以按它的规范自定义一个。

此处，我们可以用LengthDelimitedCodec，只需要在基本的 TcpStream 上套一下就可以了。接着往下看。

### 使用Frame改造代码

使用Framed + LengthDelimitedCodec 类型改造后的服务端和客户端代码如下：

服务端代码：

```plain
use bytes::Bytes;
use futures::{SinkExt, StreamExt};
use std::env;
use tokio::net::TcpListener;
use tokio::process::Command;
use tokio_util::codec::{Framed, LengthDelimitedCodec};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = env::args()
        .nth(1)
        .unwrap_or_else(|| "127.0.0.1:8888".to_string());
    println!("Listening on: {}", addr);
    let listener = TcpListener::bind(&addr).await?;

    // 注意这里是一个无条件循环，表明始终处于服务状态
    loop {
        // 等待客户端请求连上来
        let (stream, _) = listener.accept().await?;
        // 包裹成一个Frame stream
        let mut framed_stream = Framed::new(stream, LengthDelimitedCodec::new());

        // 创建子task执行任务
        tokio::spawn(async move {
            // 等待读取一个一个msg，如果返回None，会退出这个循环
            while let Some(msg) = framed_stream.next().await {
                match msg {
                    Ok(msg) => {
                        // 解析指令，执行任务
                        let directive = String::from_utf8(msg.to_vec())
                            .expect("error when converting to string directive.");
                        println!("{directive}");
                        let output = process(&directive).await;
                        println!("{output}");

                        // 返回执行结果
                        _ = framed_stream.send(Bytes::from(output)).await;
                    }
                    Err(e) => {
                        println!("{e:?}");
                    }
                }
            }
        });
    }
}

async fn process(directive: &str) -> String {
    if directive == "gettime" {
        // 这里我们用了unwrap()是因为我们一般确信执行date命令不会失败
        // 更可靠的做法是对返回的Result作处理
        let output = Command::new("date").output().await.unwrap();
        String::from_utf8(output.stdout).unwrap()
    } else {
        // 如果是其他指令，我们目前返回 无效指令
        "invalid command".to_owned()
    }
}

```

这里我简单解释一下上面的示例。

在监听到连接stream（第19行）后，把它包裹成Frame stream（第21行），然后使用 `while let` 配合 `framed_stream.next()` 对这个流进行迭代，就读出了里面一帧一帧的数据msg。需要返回结果的时候，使用 `framed_stream.send()` 就可以了。

客户端代码：

```plain
use bytes::Bytes;
use futures::{SinkExt, StreamExt};
use std::env;
use tokio::net::TcpStream;
use tokio_util::codec::{Framed, LengthDelimitedCodec};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = env::args()
        .nth(1)
        .unwrap_or_else(|| "127.0.0.1:8888".to_string());
    // 连接到服务端
    let stream = TcpStream::connect(&addr).await?;
    // 包裹成 Frame stream
    let mut framed_stream = Framed::new(stream, LengthDelimitedCodec::new());

    // 发送指令
    framed_stream.send(Bytes::from("gettime")).await?;

    // 读取返回数据，这里只读一次
    if let Some(msg) = framed_stream.next().await {
        match msg {
            Ok(msg) => {
                let timeinfo = String::from_utf8(msg.to_vec())?;
                println!("{}", timeinfo);
            }
            Err(e) => return Err(e.into()),
        }
    }

    Ok(())
}

```

在连接到服务器，得到连接stream（第13行）后，把它包裹成Frame stream（第15行） ，然后使用 `framed_stream.send()` 发送一条指令，在后面用迭代器方法等待指令执行后返回的内容msg。对msg的处理方式和服务端代码一致。

可以看到，经过Frame层抽象后，大大精简了代码逻辑，整体变得非常清爽。最关键的是，改造后的代码实际 **完全重塑了程序员的心智模型**：我们不再需要关注底层传输的大量细节了，真正实现了面向业务编码，可以按时下班了，非常开心。

注：这节课的完整代码点击 [这里](https://github.com/miketang84/jikeshijian/tree/master/14-getinfo) 可以获取。

## 小结

这节课我们一起学习了如何循序渐进地基于tokio开发一个服务端和客户端tcp网络应用命令行程序。知识点很多，我们一起来回顾一下。

- Rust中命令行参数的获取方式；
- 在Cargo.toml 配置文件中添加依赖；
- 在服务端建立 tcp lisener；
- 根据新的连接创建新的task；
- 读取tcp数据输入，以及写入返回内容；
- 建立 tcp client 连接；
- 编译测试Rust命令行程序；
- tokio的Frame概念和编解码；
- 使用Frame简化网络编程。

网络编程有其复杂性在里面，所以这节课我们应该重点掌握使用Frame的编程模型，同时了解原始字节流的处理原理。

## 思考题

最后请你来思考2个问题。

1. EOF是什么，什么时候会碰到EOF？
2. 请问 stream.read\_to\_end() 接口能读完网络连接中的数据吗？

欢迎你把思考后的结果分享到评论区和我一起讨论，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！