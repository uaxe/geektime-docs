你好，我是倪朋飞。

在上一讲中，我带你学习了 eBPF for Windows 的主要原理以及如何在 Windows 系统上开发 eBPF 程序。eBPF for Windows 把开源社区的 eBPF 工具链带到了 Linux，让 Windows 开发者也可以利用 eBPF 技术来解决网络、观测、性能优化等各类问题。由于复用了相同的工具链，Windows eBPF 程序的开发流程同 Linux 非常相似，主要也是利用 libbpf 开发 eBPF 内核程序、利用 LLVM 编译 eBPF 程序为字节码、最后再到用户态程序中加载和挂载 eBPF 字节码，并通过 BPF 映射同内核态 eBPF 程序进行交互。

今天这一讲我将带你换一种编程语言，也就是通过在容器和云原生应用中最流行的 Go 语言来开发 eBPF 程序。

## eBPF Go 语言开发库

在 [阶段总结｜实用eBPF工具及最新开源项目总结](https://time.geekbang.org/column/article/487227) 中我曾经讲到，BCC、libbpf 以及内核源码，都主要使用 C 语言开发 eBPF 程序，而实际的应用程序可能会以多种多样的编程语言进行开发。所以，开源社区开发和维护了很多不同语言的接口，方便这些高级语言跟 eBPF 系统进行交互。比如，我们课程多次使用的 BCC 就提供了 Python、C++ 等多种语言的接口，而使用 BCC 的 Python 接口去加载 eBPF 程序，要比 libbpf 和内核源码的方法简单得多。

对于 Go 语言来说，跟 Python 接口也是类似的，目的也是方便熟悉 Go 语言的开发者更容易地把 eBPF 集成到现有的项目中去。下面的表格列出了常见的 Go 语言开发库，以及它们的使用场景。

![](https://static001.geekbang.org/resource/image/eb/a8/eb3e2b02c352498f9a4yy93d86fa82a8.jpg?wh=1772x1284)

在使用这些 Go 语言开发库时需要注意， **Go 开发库只适用于用户态程序中**，可以完成 eBPF 程序编译、加载、事件挂载，以及 BPF 映射交互等用户态的功能，而内核态的 eBPF 程序还是需要使用 C 语言来开发的。

了解了这些 Go 语言的 eBPF 开发库之后，你肯定在想该如何使用 Go 语言来开发 eBPF 程序了。接下来，我就通过一个具体的例子带你一起看一下。

> 注意：以下课程内容需要你在 Linux 机器中安装 Go 语言。如果你还没有安装，可以点击 [这里](https://go.dev/dl/) 下载并安装。或者，你也可以执行下面的命令，安装最新版本的 Go 并配置 Go 环境。
>
> GOVERSION=$(curl -sL ‘ [https://golang.org/VERSION?m=text](https://golang.org/VERSION?m=text)’ \| head -n 1)
>
> curl -sL “ [https://go.dev/dl/$GOVERSION.linux-amd64.tar.gz](https://go.dev/dl/$GOVERSION.linux-amd64.tar.gz)” \| sudo tar -C /usr/local -zxf -
>
> mkdir /go
>
> export GOPATH=/go
>
> export PATH=$PATH:/usr/local/go/bin/:$GOPATH/bin

## 如何用 Go 开发 eBPF 程序

在正式开始我们的例子之前，我先带你简单看一下 [cilium/ebpf](https://github.com/cilium/ebpf) 这个库的主要组件，方便你以后在使用时查阅。

根据 cilium/ebpf 的 [GitHub](https://github.com/cilium/ebpf) 页面，你可以发现，它主要由 asm、cmd/bpf2go、link、perf、ringbuf、features、rlimit 以及 btf 等 8 个子包组成，这些子包的功能分别是：

- [asm](https://pkg.go.dev/github.com/cilium/ebpf/asm) 包含一个基本的汇编器，允许你直接在 Go 代码中编写 eBPF 汇编指令（如果你更喜欢用 C 语言编写 eBPF 程序的话，则不需要使用这个功能）。
- [cmd/bpf2go](https://pkg.go.dev/github.com/cilium/ebpf/cmd/bpf2go) 用于把 C 语言编写的 eBPF 程序进行编译并嵌入到 Go 代码中。除了代码编译外，它还自动生成加载和操作 eBPF 程序和映射对象的 Go 语言脚手架代码。
- [link](https://pkg.go.dev/github.com/cilium/ebpf/link) 用于将 eBPF 程序挂载到各种钩子上。
- [perf](https://pkg.go.dev/github.com/cilium/ebpf/perf) 用于从 `PERF_EVENT_ARRAY` 映射中读取数据。
- [ringbuf](https://pkg.go.dev/github.com/cilium/ebpf/ringbuf) 用于从 `BPF_MAP_TYPE_RINGBUF` 映射中读取数据。
- [features](https://pkg.go.dev/github.com/cilium/ebpf/features) 使用原生 Go 实现了类似于 `bpftool feature probe` 的功能，用于发现与 BPF 相关的内核特性。
- [rlimit](https://pkg.go.dev/github.com/cilium/ebpf/rlimit) 提供了一个方便的 API 来解除 5.11 版本之前内核上对 `RLIMIT_MEMLOCK` 的限制。
- [btf](https://pkg.go.dev/github.com/cilium/ebpf/btf) 允许读取 BTF（BPF 类型格式）。


  其中， `cmd/bpf2go` 是一个可执行文件，其功能类似于 `bpftool gen skeleton`，用于编译 eBPF 代码并生成 Go 语言的脚手架代码；而其他的子包则是类似于 libbpf，用于 Go 代码同 eBPF 程序进行交互。

还记得 [第 8 讲](https://time.geekbang.org/column/article/484372?utm_campaign=geektime_search&utm_content=geektime_search&utm_medium=geektime_search&utm_source=geektime_search&utm_term=geektime_search) 讲到的使用 libbpf 开发 eBPF 程序的步骤吗？如果你不记得，可以点击 [libbpf 方法](https://time.geekbang.org/column/article/484372) 再去回顾一下。其实，使用 cilium/ebpf 开发 eBPF 程序的步骤也是类似的，可以通过以下三个步骤完成：

1. 第一步，使用 C 语言开发内核态 eBPF 程序，这一步跟 libbpf 方法是完全相同的。
2. 第二步，借助 `go generate` 命令，使用 [cmd/bpf2go](https://pkg.go.dev/github.com/cilium/ebpf/cmd/bpf2go) 编译 eBPF 程序，并生成 Go 语言脚手架代码。
3. 第三步，使用 cilium/ebpf 库配合上一步生成的脚手架代码开发用户态程序，包括 eBPF 程序加载、挂载到内核函数和跟踪点，以及通过 BPF 映射获取和打印执行结果等。

接下来，我就用一个最简单的 XDP 网络包计数程序来带你一起详细看看这几个步骤。

**第一步，使用 C 语言开发内核态 eBPF 程序。**

第一步跟我们之前学习的 libbpf 方法是一样的，新建一个 hello.bpf.c 文件，然后写入内核态 eBPF 程序即可。主要的代码如下所示，关键的地方我都加了注释方便你理解。

```go
/* 由于我们并不需要cgo，这儿需要通过Go构建标签来排除C源文件，否则Go编译会报错 */
//go:build ignore

#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

/* 定义BPF映射，用于存储网络包计数*/
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __type(key, __u32);
    __type(value, __u64);
    __uint(max_entries, 1);
} pkt_count SEC(".maps");

/* XDP程序入口，统计网络包数量并存入BPF映射 */
SEC("xdp")
int count_packets() {
    __u32 key    = 0;
    __u64 *count = bpf_map_lookup_elem(&pkt_count, &key);
    if (count) {
        __sync_fetch_and_add(count, 1);
    }

    return XDP_PASS;
}

char __license[] SEC("license") = "Dual MIT/GPL";

```

这其中，

- `//go:build ignore` 表示 Go 编译时忽略 C 文件；
- `pkt_count` 定义了一个用于存储网络包计数的 BPF 映射；
- `SEC("xdp")` 定义了 XDP 程序的入口函数 `count_packets`。

从这段代码你可以发现，这儿的代码跟 libbpf 方法是一样的。只有一点需要注意的是 `// go:build ignore` 这一行是必不可少的，它的意思是让 Go 编译时忽略 C 源码文件。由于我们只是用 C 语言开发 eBPF 程序，并不需要通过 cgo 去直接调用内核态 eBPF 程序代码，所以在编译 Go 代码时应该忽略 C 源码文件。

**第二步，编译并生成 Go 语言脚手架代码。**

有了 eBPF 程序代码之后，接下来就是利用 `cmd/bpf2go` 来编译并生成 Go 脚手架代码了。创建一个 main.go 文件，并写入如下的代码。

```go
package main

//go:generate go run github.com/cilium/ebpf/cmd/bpf2go hello hello.bpf.c

```

这段代码最关键的是第二句 `go:generate` 注解，用于在执行 `go generate` 时自动执行 `cmd/bpf2go` 命令。 `cmd/bpf2go` 命令需要两个参数，第一个 `hello` 是生成文件名的前缀，而第二个参数 `hello.bpf.c` 就是我们第一步开发的 eBPF 程序。

在执行 `go generate` 命令之前，你还需要执行下面的命令，初始化一个 Go 模块，并添加对 `github.com/cilium/ebpf/cmd/bpf2go` 的依赖（如果你对 Go 模块不熟悉，可以点击 [这里](https://go.dev/ref/mod)，查看官方文档）。

```shell
go mod init hello
go mod tidy
go get github.com/cilium/ebpf/cmd/bpf2go

```

接下来，你就可以执行 `go generate` 命令，编译并生成 Go 语言脚手架代码。如果一切顺利，你将看到如下输出：

```shell
$ go generate
Compiled /ebpf-apps/go/hello/hello_bpfel.o
Stripped /ebpf-apps/go/hello/hello_bpfel.o
Wrote /ebpf-apps/go/hello/hello_bpfel.go
Compiled /ebpf-apps/go/hello/hello_bpfeb.o
Stripped /ebpf-apps/go/hello/hello_bpfeb.o
Wrote /ebpf-apps/go/hello/hello_bpfeb.go

```

这其中， `.o` 文件就是编译目标文件， `.go` 文件就是对应的脚手架代码，而后缀 `bpfel` 和 `bpfeb` 则分别表示该文件用于小端系统和大端系统。

**第三步，开发用户态程序。**

有了脚手架代码之后，接下来的最后一步就是开发用户态程序了。你可以在 main.go 里面继续添加 `main()` 函数，添加 eBPF 程序加载、挂载到XDP，以及通过 BPF 映射获取和打印执行结果等执行逻辑。完整的代码如下所示，关键的步骤我加了注释方便你理解。

```go
// 1. 引入必要的依赖库
import (
 "log"
 "net"
 "os"
 "os/signal"
 "time"

 "github.com/cilium/ebpf/link"
 "github.com/cilium/ebpf/rlimit"
)

func main() {
 // 2. 移除内核<5.11的资源限制
 if err := rlimit.RemoveMemlock(); err != nil {
  log.Fatal("Removing memlock:", err)
 }

 // 3. 调用脚手架函数，加载编译后的 eBPF 字节码
 var objs helloObjects
 if err := loadHelloObjects(&objs, nil); err != nil {
  log.Fatal("Loading eBPF objects failure:", err)
 }
 defer objs.Close()

  // 4. 挂载 XDP 程序到网卡上
 ifname := "eth0"
 iface, err := net.InterfaceByName(ifname)
 if err != nil {
  log.Fatalf("Getting interface %s failure: %s", ifname, err)
 }
 link, err := link.AttachXDP(link.XDPOptions{
  Program:   objs.CountPackets,
  Interface: iface.Index,
 })
 if err != nil {
  log.Fatal("Attaching XDP failure:", err)
 }
 defer link.Close()

 log.Printf("Counting incoming packets on %s..", ifname)

 // 5. 定期查询并打印数据包计数（Ctrl+C退出）
 tick := time.Tick(time.Second)
 stop := make(chan os.Signal, 5)
 signal.Notify(stop, os.Interrupt)
 for {
  select {
  case <-tick:
   var count uint64
   err := objs.PktCount.Lookup(uint32(0), &count)
   if err != nil {
    log.Fatal("Map lookup failure:", err)
   }
   log.Printf("Received %d packets", count)
  case <-stop:
   log.Print("Received stop signal, exiting..")
   return
  }
 }
}

```

你可以发现，这段代码的主要逻辑跟 libbpf 方法也是类似的，所不同的只是编程语言和库函数的不同。另外，这段 Go 代码里面的 eBPF 程序名 `CountPackets` 和 BPF 映射名 `PktCount` 分别对应第一步 eBPF C 代码里面的 `count_packets` 和 `pkt_count`，这是 `cmd/bpf2go` 自动将 C 命名格式转换为 Go 的驼峰命名法导致的（即不使用下划线且单词首字母大写）。

代码开发完成后，你就可以编译并执行用户态的程序了。执行 `go build` 命令编译 Go 程序后并执行 `./hello` 运行它，如果一切正常，你将看到如下的输出：

```shell
$ go build
$ ./hello
2023/12/30 14:19:49 Counting incoming packets on eth0..
2023/12/30 14:19:50 Received 9 packets
2023/12/30 14:19:51 Received 16 packets
2023/12/30 14:19:52 Received 20 packets

```

恭喜你，你已经使用 Go 语言成功开发并运行了第一个 eBPF 程序。

## eBPF 程序分发

同 libbpf 一样，你除了可以在本地运行刚刚开发的 eBPF 程序之外，你还可以直接把编译生成的二进制文件复制到其他相同体系结构的机器上运行。如果目标机器的体系结构不同，你还可以借助 Go 的交叉编译，生成对应体系结构的二进制文件。比如，你可以执行下面的命令为 ARM 机器编译。

```shell
# CGO_ENABLED=0 指定不依赖libc
# GOARCH=arm64 指定编译目标为64位ARM
CGO_ENABLED=0 GOARCH=arm64 go build

```

那么，cilium/ebpf 是怎么实现同一份代码可以跨平台编译，并且只通过一个二进制文件就可以分发的呢？其实秘密就藏在 `cmd/bpf2go` 生成的脚手架文件中。

对于第一个跨平台的问题，由于大小端系统的不同， `cmd/bpf2go` 分别为小端系统和大端系统生成了后缀为 `bpfel` 和 `bpfeb` 的脚手架文件。执行下面的命令，查看这两个文件的开头你可以发现，它们通过 `go:build` 指定了只在特定平台才会执行编译。

```shell
$ head -n3 hello_bpfel.go
// Code generated by bpf2go; DO NOT EDIT.
//go:build 386 || amd64 || amd64p32 || arm || arm64 || loong64 || mips64le || mips64p32le || mipsle || ppc64le || riscv64

$ head -n3 hello_bpfeb.go
// Code generated by bpf2go; DO NOT EDIT.
//go:build arm64be || armbe || mips || mips64 || mips64p32 || ppc64 || s390 || s390x || sparc || sparc64

```

再仔细查看 hello\_bpfel.go 和 hello\_bpfeb.go 的区别，你可以进一步发现，除了刚才的 `go:build` 标签不同之外，这两个文件的主要区别在于 `go:embed` 对应的 ELF 文件不同。执行下面的命令，你可以发现它们分别嵌入了小端和大端系统对应的 `.o` 文件，并放到了 Go 变量 `_HelloBytes` 中。

```shell
$ tail -n5 hello_bpfeb.go

// Do not access this directly.
//
//go:embed hello_bpfeb.o
var _HelloBytes []byte

$ tail -n5 hello_bpfel.go

// Do not access this directly.
//
//go:embed hello_bpfel.o
var _HelloBytes []byte

```

而这也回答了刚才的第二个问题，即通过 Go 嵌入 `.o` 的方法，让编译生成的二进制文件可以独立分发，而不需要在目标机器上安装开发编译工具。

当然了，在分发 eBPF 程序到异构环境时，不同内核版本导致的 eBPF 兼容性问题还是需要你自己去解决的。比如，你可以通过 `features` 包来检查目标机器的内核版本是否支持某个 eBPF 特性，然后再决定是否加载 eBPF 程序；也可以通过 BTF 来解决不同内核版本中数据结构不同的问题，从而实现一次编译到处执行。

## **小结**

今天，我带你一起学习了如何使用 Go 语言开发 eBPF 程序。通过一个最简单的 XDP 网络包计数程序，我带你一起学习了使用 Go 语言开发 eBPF 程序的三个步骤，即使用 C 语言开发内核态 eBPF 程序，使用 `cmd/bpf2go` 编译 eBPF 程序并生成 Go 语言脚手架代码，以及使用 cilium/ebpf 库开发用户态程序。得益于 Go 语言的高效和简洁，使用 Go 语言开发的 eBPF 程序可以在交叉编译后直接分发到其他平台上运行，而不需要在目标机器上再去安装开发工具。

在这一讲的最后，我想提醒你，尽管 Go 语言已经提供了完善的交叉编译机制，但是在分发 eBPF 程序时你还需注意目标机器的内核版本是否支持你所使用的特性。如果有必要的话，你还需要使用 `features` 包和 BTF 来确保 eBPF 程序能够正常运行在目标机器上。

## **思考题**

最后，我想邀请你来聊一聊：

1. 今天的主要内容是如何使用 Go 开发 eBPF 程序，那么为什么要使用 Go 语言开发 eBPF 程序呢？你觉得 Go 语言开发 eBPF 程序有什么优势和劣势？
2. 除了 Go 语言，你还知道有哪些语言可以用来开发 eBPF 程序吗？它们各自有什么优势和劣势？

期待你在留言区和我讨论，也欢迎把这节课分享给你的同事、朋友。让我们一起在实战中演练，在交流中进步。