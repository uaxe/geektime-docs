你好，我是倪朋飞。

在上一讲中，我带你学习了如何利用 ChatGPT 学习 eBPF 技术并解决碰到的各种疑惑。ChatGPT 不仅可以帮助我们制定学习和实践计划，还能方便地解答疑惑、生成代码。此外，结合丰富的插件和文档语义搜索功能，你还可以让 ChatGPT 学习并了解最新信息，以帮助你解决 ChatGPT 不曾了解的问题。

在利用 ChatGPT 强大能力的同时，我还得提醒你，ChatGPT 仍处于实验阶段，它所生成的代码可能存在很多问题。因此，你需要对 ChatGPT 生成的代码进行检查，以确保代码的正确性。特别是在 eBPF 等技术领域，扎实的基础知识还是必不可少的。

在前面的课程中，你可能已经注意到，eBPF 的主要应用都在 Linux 平台上。但是，随着 eBPF 技术的发展以及云原生、容器等技术在多平台上的大量实践，越来越多的人希望能够把 eBPF 技术带到 Windows 等其他平台上，以便利用 eBPF 技术扩展这些平台的操作系统内核，应对故障诊断、网络优化、安全控制、性能监控等各类挑战。

今天，我就带你一起探索 eBPF 在 Windows 系统中的实现以及如何开发 Windows eBPF 程序。

## eBPF 居然也可以在 Windows 上运行？

我们知道，在 Linux 系统中，eBPF 技术已经广泛应用于网络、观测、安全和性能优化等各种场景。随着这些实践的发展，围绕 eBPF 已经形成了一个横跨 Linux 内核、开发工具、开发库以及各类产品的生态系统。尽管最初 eBPF 技术是在 Linux 内核中实现的，但 **eBPF 在 Linux 系统中解决的这些问题在 Windows 等其他操作系统中也同样存在**。所以，很多人也希望同样的技术可以移植到 Windows 等其他操作系统中。

因此，微软在 2021 年 5 月宣布了一个新的开源项目，也就是 [eBPF for Windows](https://github.com/microsoft/ebpf-for-windows)，将 Linux 生态系统中的 eBPF 工具链和应用程序编程接口（API）引入到 Windows，从而允许在 Windows 之上使用现有的 eBPF 工具链。并在随后的 2021 年 8 月，同 Google、Isovalent、Facebook 和 Netflix 联合宣布成立了 eBPF 基金会，共同推动 eBPF 技术的发展和应用。

虽然名字同 Linux 上一样，但 Windows eBPF 并不是 Linux eBPF 的一个分支，而只是利用了 eBPF 开源社区现有的工具链为 eBPF 程序添加了 Windows 运行时的支持。那么，这到底是如何实现的呢？看一下下面这个架构组件图你就明白了。

![](https://static001.geekbang.org/resource/image/14/d5/14920827da476b693dcc749242486dd5.png?wh=1051x809)

从这个架构组件图中你可以发现，现有的 eBPF 编译工具（比如 clang）可以用来把 eBPF 程序编译成 eBPF 字节码。然后，应用程序或者 Windows netsh 工具可以通过 [Libbpf API](https://microsoft.github.io/ebpf-for-windows/libbpf_8h.html) 来加载这些字节码到内核中运行。

接着，这些字节码会被发送到托管在用户模式安全环境的静态验证器（ [PREVAIL 验证器](https://github.com/vbpf/ebpf-verifier)）进行校验。如果字节码通过了验证器的所有安全检查，那么这些字节码可以通过下面两种方式的任何一种来执行。

- 第一种方式，字节码可以加载到在 Windows 内核模式执行上下文中运行的 [uBPF](https://github.com/iovisor/ubpf) 解释器中解释执行。
- 第二种方式，由 uBPF 即时编译器（JIT）编译，再将编译后的本机代码加载到内核模式上下文执行。

加载到内核上下文的 eBPF 程序可以挂载到各种内核事件上，并通过 eBPF shim 暴露的帮助函数来处理这些事件。同 Linux 中的 BPF 帮助函数类似， **Windows 系统中的 eBPF shim 封装了可供 eBPF 程序调用的 Windows 内核接口，方便 eBPF 程序与内核进行交互**。

除了以上两种运行模式之外，由于开启虚拟机监控程序保护代码完整性（Hypervisor-protected Code Integrity，HVCI）的系统中运行程序需要签名验证，导致即时编译器生成的代码无法注入内核。因此，Windows eBPF 还提供了一种特殊的运行模式，即把 eBPF 程序编译成原生的 Windows 驱动程序（.sys 文件），再以驱动的方式执行。

## 如何在 Windows 系统中安装 eBPF？

了解了 eBPF 程序在 Windows 中的运行原理之后，接下来我再带你一起来看看如何在 Windows 系统中安装 eBPF 运行时。

在安装之前需要提醒你的是，由于 Windows 系统要求在内核模式运行的所有软件都必须进行数字签名，而 Windows eBPF 暂时还在测试阶段，还没有发布已签名的稳定版本，因而只能在打开测试签名或者连接并运行内核调试器的系统上工作。所以，在安装之前，你需要先打开测试签名模式并重启系统。

### 第一步，打开测试签名并重启系统

以管理员模式打开 Powershell，并运行下面的命令打开测试签名，然后重启系统。

```powershell
bcdedit.exe -set TESTSIGNING ON

```

在执行命令时，请注意：

- 如果你的系统开启了安全启动，会碰到“该值受安全引导策略保护，无法进行修改或删除”的错误。这时候需要先到 BIOS 关闭安全启动，然后再执行上面的命令。
- 打开测试签名后，必须要先重启系统才会生效（重启后桌面右下角会有“测试模式”字样），以下的所有命令都需要在重启之后执行。

### 第二步，安装 Windows eBPF 运行时

以管理员模式打开 Powershell，执行下面的命令，下载并安装 eBPF 运行时。

```powershell
# 安装 Visual C++ 可再发行程序包
Start-BitsTransfer https://aka.ms/vs/17/release/vc_redist.x64.exe
Start-Process -FilePath .\vc_redist.x64.exe

# 安装 eBPF 运行时
Start-BitsTransfer https://github.com/microsoft/ebpf-for-windows/releases/download/v0.12.0/ebpf-for-windows.0.12.0.msi
# 安装时请选择安装 Runtime Components 和 Development Components
msiexec.exe /I ebpf-for-windows.0.12.0.msi

```

注意，在安装时请把默认目录修改到 `C:\ebpf-for-windows` 或者其他不带空格的目录中（以下的内容都以 `C:\ebpf-for-windows` 为例讲解）。

接着，执行 `Get-Service eBPFSvc` 确认 eBPF 程序已经正常启动。如果一切正常，你将看到如下输出：

```powershell
PS C:\> Get-Service eBPFSvc
Status   Name               DisplayName
------   ----               -----------
Running  eBPFSvc            eBPFSvc

```

### 第三步，安装 Windows eBPF 开发工具

Windows eBPF 运行时安装完成后，接下来还有最后一步，就是安装 eBPF 开发工具。这里，我推荐你使用社区提供的安装脚本，它可以帮你自动安装所有依赖的工具。

以管理员模式打开一个新的 Powershell 终端，执行下面的命令。

```powershell
# 安装 Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 安装 eBPF 开发工具
Invoke-WebRequest 'https://raw.githubusercontent.com/microsoft/ebpf-for-windows/main/scripts/Setup-DevEnv.ps1' -OutFile $env:TEMP\Setup-DeveEnv.ps1
&"$env:TEMP\Setup-DeveEnv.ps1"

```

> 小提示：如果上面的命令执行碰到 “Wrong file hash for Chocolatey installer” 的错误，可以执行 `notepad $env:TEMP\Setup-DeveEnv.ps1` 打开这个文件，把第 5 行检查哈希的步骤删除之后重新运行 `&"$env:TEMP\Setup-DeveEnv.ps1"`。这个错误是由安装脚本哈希值检查过程的问题导致的，后续开源社区会修复。

由于 Chocolatey 暂时还不支持安装 WDK for Windows 11，所以你还需要执行下面的命令，手动安装 WDK for Windows 11。

```powershell
Start-BitsTransfer "https://go.microsoft.com/fwlink/?linkid=2196230" -Destination wdksetup.exe
Start-Process -FilePath .\wdksetup.exe

```

注意，在安装完成时，需要注意勾选 “Install Windows Driver Kit Visual Studio Extension” 选项，这样才能在 Visual Studio 中使用 WDK。

恭喜你，经过漫长的下载和安装步骤之后，到这里所有 Windows eBPF 需要的运行时和开发工具就安装成功了。接下来，我们就可以开始正式的 Windows eBPF 程序开发了。

## 开发一个 Hello World 程序

我们还是以最经典的 Hello World 为例，看一下如何开发 Windows eBPF 程序。在 [第 03 讲](https://time.geekbang.org/column/article/481090) 中，我已经带你学习了如何借助 BCC 库开发一个 Linux eBPF 的 Hello World 程序。由于 BCC 库在 Windows 中不可用，我们需要借助 Libbpf API 和 clang 工具来开发 Windows eBPF 程序。

首先，创建一个名为 bpf.c 的文件，内容如下所示：

```c++
#include "bpf_helpers.h"

SEC("bind")
int hello(bind_md_t *ctx)
{
    // 显示 Hello, world! 日志
    bpf_printk("Hello, world!");
    return 0;
}

```

接着，调用 clang 工具将其编译为字节码。

```powershell
clang -I 'C:\ebpf-for-windows\include' -target bpf -Werror -O2 -g -c bpf.c -o bpf.o

```

注意，这儿的 `-I 'C:\ebpf-for-windows\include'` 是为了把上一节安装的 Libbpf API 头文件包含进来。

编译成功后，你可以利用 netsh ebpf 命令把字节码加载到内核中运行，即执行下面的命令。

```powershell
netsh ebpf add program bpf.o

```

netsh ebpf 提供了很多管理 eBPF 程序的命令，它们的功能同 Linux 中的 bpftool 类似，可以用来方便地调试 eBPF 程序。比如，你可以执行 `netsh ebpf show programs` 命令查询系统中的 eBPF 程序列表，输出如下所示：

```powershell
PS C:\> netsh ebpf show programs

    ID  Pins  Links  Mode       Type           Name
======  ====  =====  =========  =============  ====================
 65538     1      1  JIT        bind           func

```

从结果中可以看到，刚刚加载的 eBPF 程序已经以 JIT 模式运行起来了，其 ID 是 65538（这个 ID 还会在卸载 eBPF 程序的时候用到）。

不过， **它的日志从哪儿可以看到呢？** 在 Linux 系统中，eBPF 的调试日志可以通过读取调试文件系统 `/sys/kernel/debug/tracing/trace_pipe` 得到，而 Windows eBPF 则利用 Windows 事件跟踪（Windows Event Tracing，简称 ETW）来跟踪事件和日志。上面我们安装的 WDK 就包含了跟踪和查看 ETW 事件的工具，它支持把事件重定向到文件，也支持实时查看。

对于第一种方法，可以使用 `wpr` 工具（Windows Performance Recorder，简称 WPR）把 eBPF 事件抓取到文件中，具体方法如下所示：

```powershell
# 引入 WDK 环境变量，后面就不需要输入长长的文件路径了
$env:Path += ';C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64'

# 开始抓取
wpr.exe -start  'C:\ebpf-for-windows\ebpfforwindows.wprp' -filemode

# 运行 eBPF 程序一段时间后停止抓取
wpr.exe -stop ebpfforwindows.etl

# 抓取的事件存在 ebpfforwindows.etl 中，还需要转换一下才好读取
netsh trace convert ebpfforwindows.etl overwrite=yes

```

转换完成后，打开 `ebpfforwindows.txt` 就看到熟悉的日志文件了。

而第二种方法，则可以使用 `tracelog` 工具，实时查看系统中的 eBPF 事件。具体方法如下所示：

```powershell
# 引入 WDK 环境变量，后面就不需要输入长长的文件路径了
$env:Path += ';C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64'

# 开始跟踪 eBPF printk 事件
tracelog -start EbpfLog -guid 'C:\ebpf-for-windows\ebpf-printk.guid' -rt

# 查看 eBPF 事件，按 Ctrl-C 结束
tracefmt -rt EbpfLog -displayonly -jsonMeta 0

# 当不需要查看实时事件时，不要忘记停止 eBPF printk 跟踪事件
tracelog -stop EbpfLog

```

稍等一会就会看到类似如下的日志：

```plain
[1]0D14.1D90::10/28/2023-11:55:08.381 [EbpfForWindowsProvider]{"Message":"Hello, world!"}
[0]0D14.0434::10/28/2023-11:55:08.386 [EbpfForWindowsProvider]{"Message":"Hello, world!"}

```

在这个日志中，\[1\] 表示 CPU ID； `0D14.1D90` 分别表示十六进制格式的进程 ID 和线程 ID；再后面就是时间和具体的日志了。

在不需要 eBPF 程序的时候，可以执行 `netsh ebpf delete program` 命令将其从系统中卸载掉。

```powershell
# ID 来自于 netsh ebpf show programs 命令
netsh ebpf delete program Id=65538

```

到这里，你可以发现，Windows eBPF 程序的开发和加载过程同 Linux 是类似的，也都提供了 Libbpf API 方便 eBPF 程序的开发。 **它们的主要区别在于 Windows 内核和 Linux 内核的差别以及开发工具链的不同。** 那么，Windows eBPF 程序的完整开发流程是什么样的呢？下面，我就以另外一个复杂点的网络跟踪示例带你一起来看一下。

## 如何开发 Windows eBPF 程序？

在正式开发之前，我需要提醒你，Windows eBPF 还处于比较早期的测试阶段，其功能特性同 Linux eBPF 相比还有很多不足。根据 Windows eBPF 的 [最新官方文档](https://microsoft.github.io/ebpf-for-windows/ebpf__structs_8h.html#a0f8242763b15ec665eaa47c6add861a0)，当前只有 XDP、BIND、CGROUP\_SOCK\_ADDR 以及 SOCK\_OPS 等少数几种程序类型是支持的。如果你的 eBPF 程序需要使用到 Linux eBPF 中的一些高级功能，那么就需要等待 Windows eBPF 的功能完善之后再进行开发。

在 [第 08 讲](https://time.geekbang.org/column/article/483364) 中，我曾经带你学习了利用 Libbpf 库开发 eBPF 程序的整个流程，而 Windows eBPF 程序的开发过程也是类似的，只是在具体的步骤上稍微不同，这个过程可以通过以下几个步骤完成：

1. 开发 eBPF 内核程序，包括数据结构定义、BPF 映射创建和更新、内核挂载事件的处理等。
2. 编译 eBPF 程序为字节码，即调用 clang 将 eBPF 代码编译为字节码。
3. 开发 eBPF 用户态程序，包括 eBPF 程序加载、挂载到内核跟踪点，以及通过 eBPF 映射获取和打印执行结果等。

下面，我就以一个 TCP/UDP 连接跟踪的示例带你一起来看一下。

### **第一步，开发 eBPF 内核程序**

eBPF 内核程序的开发包括数据结构定义、BPF 映射创建和更新、内核挂载事件的处理等。同 Linux 类似，数据结构的定义一般放在一个公共的头文件中，方便后续在 eBPF 内核程序和用户态程序中复用。

创建一个 `conn_tracker.h`，内容如下所示：

```c++
#include "net/ip.h"

// IP 地址数据结构
typedef struct _ip_address
{
    union
    {
        uint32_t ipv4;
        ipv6_address_t ipv6;
    };
} ip_address_t;

// 连接信息数据结构
typedef struct _connection_tuple
{
    ip_address_t src_ip;
    uint16_t src_port;
    ip_address_t dst_ip;
    uint16_t dst_port;
    uint32_t protocol;
    uint32_t compartment_id;
    uint64_t interface_luid;
} connection_tuple_t;

// 连接历史信息数据结构
typedef struct _connection_history
{
    connection_tuple_t tuple;
    bool is_ipv4;
    uint64_t start_time;
    uint64_t end_time;
} connection_history_t;

```

有了数据结构之后，接下来就可以用这些数据结构定义我们需要的 eBPF 映射了。创建一个 `conn_track.c`，内容如下所示：

```c++
// 网络连接映射，KEY: 连接信息，VALUE：连接开始时间
SEC("maps")
struct bpf_map_def connection_map = {
    .type = BPF_MAP_TYPE_LRU_HASH,
    .key_size = sizeof(connection_tuple_t),
    .value_size = sizeof(uint64_t),
    .max_entries = 1024};

// 网络连接历史映射，用于用户态程序获取连接历史信息
SEC("maps")
struct bpf_map_def history_map = {
    .type = BPF_MAP_TYPE_RINGBUF,
    .max_entries = 256 * 1024};

```

再接着就是对 eBPF 内核事件的处理了，这里我们选择 `sock_ops` 事件，即在网络套接字操作时触发的事件。由于代码比较多，这里只列出主要的内容，完整的代码可以在 [GitHub](https://github.com/feiskyer/ebpf-apps/blob/main/windows/connection_tracker/bpf/conn_track.c) 找到。

```c++
// eBPF 内核事件处理程序入口，段名字必须为 sockops
SEC("sockops")
int connection_tracker(bpf_sock_ops_t* ctx)
{
    int result = 0;
    bool connected;
    switch (ctx->op) {
    case BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB:
        connected = true;
        break;
    case BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB:
        connected = true;
        break;
    case BPF_SOCK_OPS_CONNECTION_DELETED_CB:
        connected = false;
        break;
    default:
        result = -1;
    }
    if (result == 0)
        handle_connection(ctx, (ctx->family == AF_INET), connected);

    return 0;
}

// 处理网络连接信息的主函数，将新的网络连接信息写入 history_map 中。
__attribute__((always_inline)) void
handle_connection(bpf_sock_ops_t* ctx, bool is_ipv4, bool connected)
{
    connection_tuple_t key = {0};
    sock_ops_to_connection_tuple(ctx, is_ipv4, &key);
    uint64_t now = bpf_ktime_get_ns();

    if (connected) {
        // 将连接信息写入 connection_map 中
        bpf_map_update_elem(&connection_map, &key, &now, 0);
    } else {
        // 从 connection_map 中删除后，将连接信息写入 history_map 中
        uint64_t* start_time = (uint64_t*)bpf_map_lookup_and_delete_elem(&connection_map, &key);
        if (start_time) {
            log_tuple(&key, is_ipv4, false);
            connection_history_t history;
            // Memset is required due to padding within this struct.
            __builtin_memset(&history, 0, sizeof(history));
            history.tuple = key;
            history.is_ipv4 = is_ipv4;
            history.start_time = *start_time;
            history.end_time = now;
            bpf_ringbuf_output(&history_map, &history, sizeof(history), 0);
        }
    }
}

// 数据结构转换函数，从 bpf_sock_ops_t 提取需要的连接信息
__attribute__((always_inline)) void
sock_ops_to_connection_tuple(bpf_sock_ops_t* ctx, bool is_ipv4, connection_tuple_t* tuple)
{
    tuple->compartment_id = ctx->compartment_id;
    tuple->interface_luid = ctx->interface_luid;
    tuple->src_port = ctx->local_port;
    tuple->dst_port = ctx->remote_port;
    tuple->protocol = ctx->protocol;

    if (is_ipv4) {
        tuple->src_ip.ipv4 = ctx->local_ip4;
        tuple->dst_ip.ipv4 = ctx->remote_ip4;
    } else {
        void* ip6 = NULL;
        ip6 = ctx->local_ip6;
        __builtin_memcpy(tuple->src_ip.ipv6, ip6, sizeof(tuple->src_ip.ipv6));
        ip6 = ctx->remote_ip6;
        __builtin_memcpy(tuple->dst_ip.ipv6, ip6, sizeof(tuple->dst_ip.ipv6));
    }
}

```

### **第二步，编译 eBPF 程序为字节码**

eBPF 内核程序开发完成后，接着就可以调用 clang 命令，将其编译为字节码了。这一步比较简单，打开 Powershell 终端，执行下面的命令即可。

```powershell
clang -I 'C:\ebpf-for-windows\include' -target bpf -Werror -O2 -g -c conn_track.c -o conn_track.o

```

### **第三步，开发 eBPF 用户态程序**

最后，就是开发 eBPF 用户态程序了。这一步包括 eBPF 字节码加载、挂载到内核跟踪点，以及通过 eBPF 映射获取和打印执行结果等。

创建一个新的 `conn_tracker.cpp` 文件，省略一些错误处理逻辑，主要内容如下所示：

```c++
// 引用头文件，注意 <windows.h> 需要放在最前面
#include <windows.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <ebpf_api.h>

int main(int argc, char** argv)
{
    // 加载 eBPF 字节码
    struct bpf_object* object = bpf_object__open("conn_track.o");
    if (!object) {
        std::cerr << "bpf_object__open for conn_track.o failed:" << errno << std::endl;
        return 1;
    }
    if (bpf_object__load(object) < 0) {
        std::cerr << "bpf_object__load for conn_track.o failed:" << errno << std::endl;
        return 1;
    }

    // 挂载到 sock_ops
    auto program = bpf_object__find_program_by_name(object, "connection_tracker");
    if (!program) {
        std::cerr << "bpf_object__find_program_by_name for \"connection_tracker\"failed:" << errno << std::endl;
        return 1;
    }
    auto link = bpf_program__attach(program);
    if (!link) {
        std::cerr << "BPF program conn_track.o failed to attach:" << errno << std::endl;
        return 1;
    }

    // 挂载 BPF 映射处理函数
    bpf_map* map = bpf_object__find_map_by_name(object, "history_map");
    if (!map) {
        std::cerr << "Unable to locate history map:" << errno << std::endl;
        return 1;
    }
    auto ring = ring_buffer__new(bpf_map__fd(map), conn_track_history_callback, nullptr, nullptr);
    if (!ring) {
        std::cerr << "Unable to create ring buffer:" << errno << std::endl;
        return 1;
    }

    // 等待 Ctrl-C 结束程序
    ...
}

// 读取 history_map 事件并打印连接信息到终端
int conn_track_history_callback(void* ctx, void* data, size_t size)
{
    if (size == sizeof(connection_history_t)) {
        auto history = reinterpret_cast<connection_history_t*>(data);
        auto source = ip_address_to_string(history->is_ipv4, history->tuple.src_ip, history->tuple.interface_luid) + ":" +
                      std::to_string(htons(history->tuple.src_port));
        auto dest = ip_address_to_string(history->is_ipv4, history->tuple.dst_ip, history->tuple.interface_luid) + ":" +
                    std::to_string(htons(history->tuple.dst_port));
        double duration = static_cast<double>(history->end_time);
        duration -= static_cast<double>(history->start_time);
        duration /= 1e9;
        std::cout <<source << "==>" << dest << "\t" << _protocol[history->tuple.protocol] << "\t" << duration
                  << std::endl;
    }
    return 0;
}

// 转换 IP 地址和网卡 UID 到字符串格式
std::string ip_address_to_string(bool ipv4, const ip_address_t& ip_address, const uint64_t interface_luid)
{
    std::string buffer;
    if (ipv4) {
        buffer.resize(MAX_IPV4_ADDRESS_LENGTH);
        in_addr addr;
        addr.S_un.S_addr = ip_address.ipv4;
        auto end = RtlIpv4AddressToStringA(&addr, buffer.data());
        buffer.resize(end - buffer.data());
    } else {
        buffer.resize(MAX_IPV6_ADDRESS_LENGTH);
        in_addr6 addr;
        memcpy(addr.u.Byte, ip_address.ipv6, sizeof(ip_address.ipv6));
        auto end = RtlIpv6AddressToStringA(&addr, buffer.data());
        buffer.resize(end - buffer.data());

    }
    buffer += "%" + interface_luid_to_name(interface_luid);

    return "[" + trim(buffer) + "]";
}

```

从这段代码中你会发现有很多陌生的函数，这是由于 Windows 库函数与 Linux 不同导致的。比如，Windows 使用 `RtlIpv4AddressToStringA()` 把 IPv4 地址转换为可读的字符串格式，而 Linux 则使用 `inet_ntop()` 函数。

代码开发完成后，还需要最后编译为二进制可执行文件才可运行。在 Windows 系统上，我们通常使用 Visual Studio 来开发、编译和调试程序。我已经帮你创建好了整个项目，源码放在 [GitHub](https://github.com/feiskyer/ebpf-apps/tree/main/windows/connection_tracker)。你可以下载源码后，使用 Visual Studio 打开 `conn_track.sln` 选择 x64/Release 之后构建项目。

构建成功后，打开一个新的 Powershell 终端，执行下面的命令运行 eBPF 程序。

```powershell
# 切换到项目的 Release 目录中
cd .\x64\Release

# 执行跟踪程序
.\conn_tracker.exe

```

接着，打开另一个 Powershell 终端，随机访问几个网络服务，比如解析 baidu.com 的 IP 地址并访问它。

```powershell
nslookup.exe baidu.com 114.114.114.114
curl.exe baidu.com

```

再回到第一个终端，你可以看到如下输出：

```plain
# 格式为源 IP、网卡、源端口 => 目的 IP、网卡、端口 协议 连接延迟
[192.168.0.3%ethernet_32769]:49853==>[114.114.114.114%ethernet_32769]:53   UDP     0.195494
[192.168.0.3%ethernet_32769]:49854==>[114.114.114.114%ethernet_32769]:53   UDP     0.199999
[192.168.0.3%ethernet_32769]:49855==>[114.114.114.114%ethernet_32769]:53   UDP     0.195471
[192.168.0.3%ethernet_32769]:54537==>[110.242.68.66%ethernet_32769]:80     TCP     0.212876

```

到这里，一个完整的网络跟踪 eBPF 程序就开发完成了。你可以看到，Windows eBPF 程序的开发流程同 Linux 非常类似，主要也是开发 eBPF 内核程序、编译 eBPF 程序为字节码，最后再到用户态程序中加载和挂载 eBPF 字节码，并通过 eBPF 映射同内核态 eBPF 程序进行交互。

同 Linux 类似，你还可以使用 bpftool 来读取 eBPF 映射的内容（bpftool 会随着 ebpf-for-windows.msi 一起安装）。比如，对于刚才连接百度的请求，你会看到如下的映射内容：

```powershell
PS C:\> C:\ebpf-for-windows\bpftool.exe map dump name connection_map -p

[{
        "key": ["0x0a","0x00","0x00","0x04","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0xd8","0x0a","0x00","0x00","0x6e","0xf2","0x44","0x42","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x50","0x00","0x00","0x06","0x00","0x00","0x00","0x01","0x00","0x00","0x00","0x00","0x00","0x00","0x01","0x80","0x00","0x06","0x00"
        ],
        "value": ["0x9c","0x72","0x03","0x52","0xc1","0x0c","0x00","0x00"
        ]
    },
    ...
]

```

这段 16 进制的数字该如何解读呢？这将是今天留给你的思考题，也顺便帮你重温一下之前课程中关于 bpftool 和 eBPF 映射的内容。

## 小结

在今天的课程中，我带你学习了 eBPF for Windows 的主要原理以及如何在 Windows 系统上开发 eBPF 程序。eBPF for Windows 把开源社区的 eBPF 工具链带到了 Linux，让 Windows 开发者也可以利用 eBPF 技术来解决网络、观测、性能优化等各类问题。

由于复用了相同的工具链，Windows eBPF 程序的开发流程同 Linux 非常相似，主要也是开发 eBPF 内核程序、编译 eBPF 程序为字节码，最后再到用户态程序中加载和挂载 eBPF 字节码，并通过 BPF 映射同内核态 eBPF 程序进行交互。

在开发和使用 Windows eBPF 程序的时候，你需要注意 Windows 平台与 Linux 平台的不同，特别是内核库函数有非常大的差别。另外，由于 Windows eBPF 还处于早期测试阶段，其功能特性同 Linux eBPF 相比还有很多不足，很多 Linux eBPF 中的一些高级功能暂时还没法在 Windows 平台中使用。不过我相信，随着 eBPF 技术的发展，Windows eBPF 也会越来越强大，未来的 Windows eBPF 一定会支持更多的功能，让 Windows 开发者也能享受到 eBPF 带来的便利。

今天的这一讲就到这里了。我将继续关注 eBPF 的发展，并为你带来更多与 eBPF 相关的内容。预计下次的更新将于 12 月份推出。如果你对我们未来课程内容有任何建议，请在评论区留言，期待你与我共同完善和构建一个贴近实践的 eBPF 知识体系。

## 思考题

在这一讲的最后，我想邀请你来聊一聊如何解读课程中最后一个案例的 eBPF 映射内容。如下所示，这是我们在访问百度网站之后查询到的 eBPF 映射。它们都是 16 进制的格式，到底代表什么意思呢？请你回顾一下之前课程中关于 bpftool 和 BPF 映射的内容，然后在留言区告诉我你的答案。

```powershell
PS C:\> C:\ebpf-for-windows\bpftool.exe map dump name connection_map -p

[{
        "key": ["0x0a","0x00","0x00","0x04","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0xd8","0x0a","0x00","0x00","0x6e","0xf2","0x44","0x42","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x00","0x50","0x00","0x00","0x06","0x00","0x00","0x00","0x01","0x00","0x00","0x00","0x00","0x00","0x00","0x01","0x80","0x00","0x06","0x00"
        ],
        "value": ["0x9c","0x72","0x03","0x52","0xc1","0x0c","0x00","0x00"
        ]
    },
    ...
]

```

欢迎在留言区和我讨论你在实践 eBPF 技术过程中碰到的问题和心得，也欢迎把这节课分享给你的同事、朋友。让我们一起在实战中演练，在交流中进步。