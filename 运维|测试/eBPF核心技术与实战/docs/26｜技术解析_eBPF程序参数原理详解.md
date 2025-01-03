你好，我是倪朋飞。

在第 6 讲 [各类 eBPF 程序的触发机制及其应用场景](https://time.geekbang.org/column/article/483364) 中，我曾讲过 eBPF 程序的分类以及每种不同类型程序的使用场景。而在后续的实战进阶篇中，也通过多讲课程详细为你讲述了各种类型 eBPF 程序的开发方法。但是，无论在课程留言区还是微信讨论群中，依然有很多同学不清楚如何从零开发一个 eBPF 程序，特别是开发的第一步———到底该如何为要开发的 eBPF 程序设置参数。

今天，我就带你一起来深入探讨这个问题，看看不同类型 eBPF 程序的参数到底是如何设置的，它们的返回值又代表着什么含义。

## 再谈 eBPF 程序

我相信你一定已经开发了很多不同的 eBPF 程序了，也已经跟随我们课程学习了很多常用 eBPF 程序的使用方法。简单来说，eBPF 程序就是通过 C 语言开发并可被编译为 eBPF 字节码的程序，而这个程序中最核心的就是挂载到内核态或用户态事件的 eBPF 函数。

在开发 eBPF 程序过程中，我想你一定已经体会到 eBPF 中的函数远没有普通程序中的函数那么灵活，其编程模型与普通程序有着明显的不同。与普通程序相比，eBPF 程序不仅无法随意调用各种库函数，而且其函数功能相对受限。这些限制主要源于 eBPF 的设计理念和安全考虑。

eBPF 指令集定义了严格的函数调用约定，所有 eBPF 程序都必须遵循，以确保在内核环境中的安全和高效运行。这些约定包括：

- R0 寄存器用作返回值，除 void 函数之外，eBPF 函数在返回之前应该设置 R0 寄存器。
- R1-R5 寄存器用于函数参数，R1 用于第一个参数，R2 用于第二个，依此类推。
- R6-R9 寄存器用于保存临时变量，它们在函数调用之间保留。
- R10 寄存器用于帧指针，它是只读的。

这儿需要注意的是：

- 第一，所有 eBPF 程序中使用的函数都必须遵循这些调用约定，包括用户开发的 eBPF 程序和内核提供的各类辅助函数以及 eBPF 内核函数（BPF Kernel Functions，一般简称 kfunc）。

- 第二，与普通的函数调用不同，eBPF 函数的参数永远不会通过堆栈传递。因而，5 个参数是一个硬限制。想要传递更多参数，必须使用结构体来解决。


了解了 eBPF 函数的基本特性和调用约定后，接下来我再带你一起来看看 Linux 内核是如何为 eBPF 程序定义参数的。

## eBPF 程序参数和返回格式

在第 6 讲 [各类 eBPF 程序的触发机制及其应用场景](https://time.geekbang.org/column/article/483364) 中，我曾提到过，不同类型的 eBPF 程序其挂载点各不相同，自然这些程序可以处理的数据也是不同的，也就意味着它们的参数也是各不相同的。要查看这些参数的定义格式，我们还需要回到 Linux 内核对 eBPF 程序类型的定义上面来。

Linux 内核使用 [BPF\_PROG\_TYPE()](https://elixir.bootlin.com/linux/v6.8/source/include/linux/bpf.h#L2075-L2077) 宏来定义不同类型的 eBPF 程序，以下就是这个宏定义的源代码：

```cpp
#define BPF_PROG_TYPE(_id, _name, prog_ctx_type, kern_ctx_type) \
    extern const struct bpf_prog_ops _name ## _prog_ops; \
    extern const struct bpf_verifier_ops _name ## _verifier_ops;

```

根据定义，你可以发现 `BPF_PROG_TYPE` 宏支持四个参数，它们的含义分别是：

- `_id` 是 eBPF 程序的编号，即内核枚举类型 `bpf_prog_type` 中的枚举值，比如 `BPF_PROG_TYPE_XDP`、 `BPF_PROG_TYPE_KPROBE` 等；
- `_name` 是 eBPF 程序名的前缀，用来拼接形成全局符号名，比如 `xdp`、 `kprobe` 等；
- `prog_ctx_type` 是 eBPF 程序上下文数据结构，用于 eBPF 程序的参数；
- `kern_ctx_type` 是 eBPF 程序内核态上下文数据结构；

宏定义的后面两行会根据这些参数拼接形成 eBPF 程序和验证器类型声明。比如，对于 XDP 程序来说，这个宏定义会生成下面的两个类型声明：

```cpp
extern const struct bpf_prog_ops xdp_prog_ops;
extern const struct bpf_verifier_ops xdp_verifier_ops;

```

通过使用 `BPF_PROG_TYPE` 宏，内核代码实现了一种统一的、可扩展的机制来声明各种 eBPF 程序类型的关键操作与验证函数接口。这样，当需要新增一种 eBPF 程序类型时，开发者只需使用该宏在对应的 C 文件中声明相应的 `*_prog_ops` 和 `*_verifier_ops` 结构，然后在其他实现文件中定义这些 ops 结构的实际内容和函数指针指向。这样可以将声明与定义分离，增强代码组织的模块化和可维护性。

这些结构体的具体实现不是本次课程的重点，这儿就不再详细展开。如果你感兴趣的话，可以到内核源码中搜索宏定义展开后的结构体名称，进而找到对应的实现源码。比如，以 XDP 为例，搜索 [xdp\_prog\_ops](https://elixir.bootlin.com/linux/v6.8/A/ident/xdp_prog_ops)，就可以找到它的定义格式，即：

```cpp
const struct bpf_verifier_ops xdp_verifier_ops = {
 .get_func_proto  = xdp_func_proto,
 .is_valid_access = xdp_is_valid_access,
 .convert_ctx_access = xdp_convert_ctx_access,
 .gen_prologue  = bpf_noop_prologue,
 .btf_struct_access = xdp_btf_struct_access,
};
​
const struct bpf_prog_ops xdp_prog_ops = {
 .test_run  = bpf_prog_test_run_xdp,
};

```

理解了 eBPF 程序类型的宏定义格式之后，如何查找具体 eBPF 程序类型的参数格式自然也就很清晰了，即只要找到对应程序类型的定义，然后看它的 `prog_ctx_type` 即可。

以下就是 Linux 内核中 [各种 eBPF 程序类型的定义](https://elixir.bootlin.com/linux/v6.8/source/include/linux/bpf_types.h#L5-L84)，它们的第三个参数也就是我们想要查找的 eBPF 程序参数格式：

```cpp
BPF_PROG_TYPE(BPF_PROG_TYPE_SOCKET_FILTER, sk_filter,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_SCHED_CLS, tc_cls_act,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_SCHED_ACT, tc_cls_act,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_XDP, xdp,
       struct xdp_md, struct xdp_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_CGROUP_SKB, cg_skb,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_CGROUP_SOCK, cg_sock,
       struct bpf_sock, struct sock)
BPF_PROG_TYPE(BPF_PROG_TYPE_CGROUP_SOCK_ADDR, cg_sock_addr,
       struct bpf_sock_addr, struct bpf_sock_addr_kern)
BPF_PROG_TYPE(BPF_PROG_TYPE_LWT_IN, lwt_in,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_LWT_OUT, lwt_out,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_LWT_XMIT, lwt_xmit,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_LWT_SEG6LOCAL, lwt_seg6local,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_SOCK_OPS, sock_ops,
       struct bpf_sock_ops, struct bpf_sock_ops_kern)
BPF_PROG_TYPE(BPF_PROG_TYPE_SK_SKB, sk_skb,
       struct __sk_buff, struct sk_buff)
BPF_PROG_TYPE(BPF_PROG_TYPE_SK_MSG, sk_msg,
       struct sk_msg_md, struct sk_msg)
BPF_PROG_TYPE(BPF_PROG_TYPE_FLOW_DISSECTOR, flow_dissector,
       struct __sk_buff, struct bpf_flow_dissector)
BPF_PROG_TYPE(BPF_PROG_TYPE_KPROBE, kprobe,
       bpf_user_pt_regs_t, struct pt_regs)
BPF_PROG_TYPE(BPF_PROG_TYPE_TRACEPOINT, tracepoint,
       __u64, u64)
BPF_PROG_TYPE(BPF_PROG_TYPE_PERF_EVENT, perf_event,
       struct bpf_perf_event_data, struct bpf_perf_event_data_kern)
BPF_PROG_TYPE(BPF_PROG_TYPE_RAW_TRACEPOINT, raw_tracepoint,
       struct bpf_raw_tracepoint_args, u64)
BPF_PROG_TYPE(BPF_PROG_TYPE_RAW_TRACEPOINT_WRITABLE, raw_tracepoint_writable,
       struct bpf_raw_tracepoint_args, u64)
BPF_PROG_TYPE(BPF_PROG_TYPE_TRACING, tracing,
       void *, void *)
BPF_PROG_TYPE(BPF_PROG_TYPE_CGROUP_DEVICE, cg_dev,
       struct bpf_cgroup_dev_ctx, struct bpf_cgroup_dev_ctx)
BPF_PROG_TYPE(BPF_PROG_TYPE_CGROUP_SYSCTL, cg_sysctl,
       struct bpf_sysctl, struct bpf_sysctl_kern)
BPF_PROG_TYPE(BPF_PROG_TYPE_CGROUP_SOCKOPT, cg_sockopt,
       struct bpf_sockopt, struct bpf_sockopt_kern)
BPF_PROG_TYPE(BPF_PROG_TYPE_LIRC_MODE2, lirc_mode2,
       __u32, u32)
BPF_PROG_TYPE(BPF_PROG_TYPE_SK_REUSEPORT, sk_reuseport,
       struct sk_reuseport_md, struct sk_reuseport_kern)
BPF_PROG_TYPE(BPF_PROG_TYPE_SK_LOOKUP, sk_lookup,
       struct bpf_sk_lookup, struct bpf_sk_lookup_kern)
BPF_PROG_TYPE(BPF_PROG_TYPE_STRUCT_OPS, bpf_struct_ops,
       void *, void *)
BPF_PROG_TYPE(BPF_PROG_TYPE_EXT, bpf_extension,
       void *, void *)
BPF_PROG_TYPE(BPF_PROG_TYPE_LSM, lsm,
        void *, void *)
BPF_PROG_TYPE(BPF_PROG_TYPE_SYSCALL, bpf_syscall,
       void *, void *)
BPF_PROG_TYPE(BPF_PROG_TYPE_NETFILTER, netfilter,
       struct bpf_nf_ctx, struct bpf_nf_ctx)

```

有了参数格式，那么返回格式又该如何确定呢？从前面的 `BPF_PROG_TYPE` 的定义，你可以发现，它只定义了参数格式，而返回格式则另外定义在 [bpf\_ret\_code](https://elixir.bootlin.com/linux/v6.8/source/include/uapi/linux/bpf.h#L6193-L6213) 枚举中：

```cpp
/* 通用 BPF 返回代码，所有 BPF 程序类型可能支持（XDP 使用自定义返回码）*/
enum bpf_ret_code {
  BPF_OK = 0,
  /* 1 保留 */
  BPF_DROP = 2,
  /* 3-6 保留 */
  BPF_REDIRECT = 7,
  /* >127 保留 */
​
  // BPF_PROG_TYPE_LWT_IN/BPF_PROG_TYPE_LWT_XMIT 专用
  BPF_LWT_REROUTE = 128,
  // BPF_PROG_TYPE_FLOW_DISSECTOR 专用
  BPF_FLOW_DISSECTOR_CONTINUE = 129,
};

```

从这个枚举的定义你可以看到，这其中只有少数几个值（比如 `BPF_OK`、 `BPF_DROP`、 `BPF_REDIRECT` 等）是预定义好的，而其他大部分数值都是保留字段。这就意味着不同类型的 eBPF 程序可以根据自己的需要去定义它们的含义，故而还需要进一步查看这些 eBPF 程序的调用逻辑才能知道确切的返回值含义。

另外，XDP 程序的返回值格式是个例外，它通过 `xdp_action` 枚举定义了返回值格式，这些值我们在之前的 XDP 案例中其实已经使用过：

```cpp
/* User return codes for XDP prog type.
 * A valid XDP program must return one of these defined values. All other
 * return codes are reserved for future use. Unknown return codes will
 * result in packet drops and a warning via bpf_warn_invalid_xdp_action().
 */
enum xdp_action {
  XDP_ABORTED = 0,  // 错误
  XDP_DROP,         // 丢包
  XDP_PASS,         // 传递到内核协议
  XDP_TX,           // 转发数据包到同一网卡
  XDP_REDIRECT,     // 转发数据包到不同网卡
};

```

为了帮你更好地理解各类 eBPF 程序的参数和返回值格式，我已整理了一份常见 eBPF 程序类型的汇总。接下来，让我们按 eBPF 程序类型的不同，逐一看一下它们的参数定义方式和返回值含义。

### 跟踪类 eBPF 程序

首先来看第一类，也就是跟踪类 eBPF 程序。跟踪类 eBPF 程序主要用于从系统中提取跟踪信息，进而为监控、排错、性能优化等提供数据支撑，包括内核探针、跟踪点、性能事件等几种类型。

> 注意， `kprobe`、 `kretprobe`、 `uprobe` 以及 `uretprobe` 都属于内核探针，它们是内核探针的不同形式。

为了方便你查询，我把常见的跟踪类 eBPF 程序的参数格式和返回格式整理成了一个表格，你可以在需要时参考。

![](https://static001.geekbang.org/resource/image/c0/b8/c0d03e200002be44579cd02af434e6b8.jpg?wh=4000x1922)

这里，有四点需要特别提醒你。

第一，KPROBE 跟踪程序通常借助 Libbpf 宏 `PT_REGS_PARM1` … `PT_REGS_PARM5` 来访问 `pt_regs`，这些宏将根据当前 CPU 架构将其转换为正确的待跟踪内核函数参数格式。当然更简单的一种方式是借助 Libbpf 宏 `BPF_KPROBE(name, args...)` 用待跟踪内核函数相同的函数签名来定义 eBPF 程序参数。

第二，TRACEPOINT 跟踪程序的参数可以通过两种方式获取其定义。

- 第一种，直接使用 `vmlinux.h` 中的预定义类型，格式一般为 `trace_event_raw_<跟踪点名称>`。

- 第二种，通过 `/sys/kernel/tracing` 或者 bpftrace 查询具体的参数格式后，自己构造一个结构体。


第三，同 TRACEPOINT 跟踪程序相比，RAW\_TRACEPOINT 跟踪程序的参数不会自动进行格式转换，因而需要在 eBPF 程序内根据需要执行强制类型转换。

第四，跟踪类 eBPF 程序中的函数返回值通常没有任何作用，按照惯例，一般返回 0 表示执行成功，返回其他值表示失败。

## 网络类 eBPF 程序

看完跟踪类 eBPF 程序，我们再来看看网络类 eBPF 程序。网络类 eBPF 程序主要用于对网络数据包进行过滤和处理，进而实现网络的观测、过滤、流量控制以及性能优化等各种丰富的功能，包括 XDP、TC、套接字程序等几种类型。

为了方便你查询，我把常见的网络类 eBPF 程序的参数格式和返回格式整理成了一个表格，你可以在需要时参考。

![](https://static001.geekbang.org/resource/image/34/92/34fe0af77d87d1c3aef5c9aca1524492.jpg?wh=4122x2488)

这里，需要特别提醒你的是，与跟踪类 eBPF 程序不同，网络类 eBPF 程序的返回值都有明确的定义，在使用时注意根据期望的动作设置返回值。

### cGroup 程序

cGroup 程序用于对 cGroup 内所有进程的网络过滤、套接字选项以及转发等进行动态控制，它最典型的应用场景是对容器中运行的多个进程进行网络控制。

为了方便你查询，我把常见的 cGroup 类 eBPF 程序的参数格式和返回格式也整理成了一个表格，你可以在需要时参考。

![](https://static001.geekbang.org/resource/image/30/a3/305b9ab480da668d4eedec1e97b3d4a3.jpg?wh=4083x1840)

从这个表格里你可以发现，cGroup 程序的返回值跟网络类 eBPF 程序类似，其返回值都有明确的定义，一般返回 0 表示禁止操作或者丢包，而返回 1 表示允许操作或者允许接收数据包。

## 小结

今天，我带你深入探讨了各类 eBPF 程序的参数设置和返回值含义。为保障内核安全和效率，eBPF 程序有着函数参数数量和特定寄存器使用规则的严格限制，这些限制直接影响了 eBPF 程序的参数和返回格式。

接着，我们从 Linux 内核 eBPF 程序类型的设计源码出发，通过分析 `BPF_PROG_TYPE` 宏定义，了解了如何确定特定 eBPF 程序类型的参数格式。值得注意的是，不同类型 eBPF 程序的返回格式并无统一规范。

最后，根据 eBPF 程序类型的不同，我还为你总结了常见 eBPF 程序类型的参数格式和返回格式：

- 跟踪类 eBPF 程序参数格式灵活，可以通过 Libbpf 宏、vmlinux.h 预定义数据类型或者完全自定义数据类型等多种方式来构造 eBPF 程序参数，而返回值通常没有任何作用。按照惯例，一般返回 0 表示执行成功，返回其他值表示失败。

- 网络类和 cGroup 类 eBPF 程序的参数格式则有严格的定义格式，并且它们的返回值也都有明确的定义，通常代表对数据包的处理决定。


理解这些 eBPF 程序的参数设置和返回格式，将帮助你更好地开发和使用各种类型的 eBPF 程序，充分发挥 eBPF 技术的强大功能。

## 思考题

最后，我想邀请你也来深入到 Linux 内核源码中，来具体查一查 eBPF 程序的返回值是如何定义的。你可以选择一种特定类型的 eBPF 程序（如 XDP、TC 或者 KPROBE 等），在 Linux 内核源码中找到其返回值的定义。

期待你在留言区和我讨论，也欢迎把这节课分享给你的同事、朋友。让我们一起在实战中演练，在交流中进步。