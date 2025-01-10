你好，我是simsun，曾在微信从事Android开发，也是开源爱好者、Rust语言“铁粉”。应绍文邀请，很高兴可以在“高手课”里和你分享一些编译方面的底层知识。

当我们在调试Native崩溃或者在做profiling的时候是十分依赖backtrace的，高质量的backtrace可以大大减少我们修复崩溃的时间。但你是否了解系统是如何生成backtrace的呢？今天我们就来探索一下backtrace背后的故事。

下面是一个常见的Native崩溃。通常崩溃本身并没有任何backtrace信息，可以直接获得的就是当前寄存器的值，但显然backtrace才是能够帮助我们修复Bug的关键。

```
pid: 4637, tid: 4637, name: crasher  >>> crasher <<<
signal 6 (SIGABRT), code -6 (SI_TKILL), fault addr --------
Abort message: 'some_file.c:123: some_function: assertion "false" failed'
    r0  00000000  r1  0000121d  r2  00000006  r3  00000008
    r4  0000121d  r5  0000121d  r6  ffb44a1c  r7  0000010c
    r8  00000000  r9  00000000  r10 00000000  r11 00000000
    ip  ffb44c20  sp  ffb44a08  lr  eace2b0b  pc  eace2b16
backtrace:
    #00 pc 0001cb16  /system/lib/libc.so (abort+57)
    #01 pc 0001cd8f  /system/lib/libc.so (__assert2+22)
    #02 pc 00001531  /system/bin/crasher (do_action+764)
    #03 pc 00002301  /system/bin/crasher (main+68)
    #04 pc 0008a809  /system/lib/libc.so (__libc_init+48)
    #05 pc 00001097  /system/bin/crasher (_start_main+38)

```

在阅读后面的内容之前，你可以先给自己2分钟时间，思考一下系统是如何生成backtrace的呢？我们通常把生成backtrace的过程叫作unwind，unwind看似和我们平时开发并没有什么关系，但其实很多功能都是依赖unwind的。举个例子，比如你要绘制火焰图或者是在崩溃发生时得到backtrace，都需要依赖unwind。

## 书本中的unwind

**1\. 函数调用过程**

如果你在大学时期修过汇编原理这门课程，相信你会对下面的内容还有印象。下图就是一个非常标准的函数调用的过程。

![](https://static001.geekbang.org/resource/image/09/2a/09cd560f823de783e22af03a5f837f2a.png?wh=3830*1370)

- 首先假设我们处于函数main()并准备调用函数foo()，调用方会按倒序压入参数。此时第一个参数会在调用栈栈顶。

- 调用invoke foo()伪指令，压入当前寄存器EIP的值到栈，然后载入函数foo()的地址到EIP。

- 此时，由于我们已经更改了EIP的值（为foo()的地址），相当于我们已经进入了函数foo()。在执行一个函数之前，编译器都会给每个函数写一段序言（prologue），这里会压入旧的EBP值，并赋予当前EBP和ESP新的值，从而形成新的一个函数栈。

- 下一步就行执行函数foo()本身的代码了。

- 结束执行函数foo() 并准备返回，这里编译器也会给每个函数插入一段尾声（epilogue）用于恢复调用方的ESP和EBP来重建之前函数的栈和恢复寄存器。

- 执行返回指令（ret），被调用函数的尾声（epilogue）已经恢复了EBP和ESP，然后我们可以从被恢复的栈中依次pop出EIP、所有的参数以及被暂存的寄存器的值。


读到这里，相信如果没有学过汇编原理的同学肯定会有一些懵，我来解释一下上面提到的寄存器缩写的具体含义，上述命名均使用了x86的命名方式。讲这些是希望你对函数调用有一个初步的理解，其中有很多细节在不同体系结构、不同编译器上的行为都有所区别，所以请你放松心情，跟我一起继续向后看。

> EBP：基址指针寄存器，指向栈帧的底部。
>
> 在ARM体系结构中，R11（ARM code）或者R7（Thumb code）起到了类似的作用。在ARM64中，此寄存器为X29。
>
> ESP：栈指针寄存器，指向栈帧的栈顶 ， 在ARM下寄存器为R13。
>
> EIP：指令寄存器，存储的是CPU下次要执行的指令的地址，ARM下为PC，寄存器为R15。

**2\. 恢复调用帧**

如果我们把上述过程缩小，站在更高一层视角去看，所有的函数调用栈都会形成调用帧（stack frame），每一个帧中都保存了足够的信息可以恢复调用函数的栈帧。

![](https://static001.geekbang.org/resource/image/01/45/017b900048f1be70ec870ea0750d2145.png?wh=1770*1016)

我们这里忽略掉其他不相关的细节，重点关注一下EBP、ESP和EIP。你可以看到EBP和ESP分别指向执行函数栈的栈底和栈顶。每次函数调用都会保存EBP和EIP用于在返回时恢复函数栈帧。这里所有被保存的EBP就像一个链表指针，不断地指向调用函数的EBP。 这样我们就可以此为线索，十分优雅地恢复整个调用栈。

![](https://static001.geekbang.org/resource/image/7a/f8/7ab1f6e1774731ec96b9c68843a73df8.png?wh=912*1070)

这里我们可以用下面的伪代码来恢复调用栈：

```
void debugger::print_backtrace() {
    auto curr_func = get_func_from_pc(get_pc());
    output_frame(curr_func);

    auto frame_pointer = get_register_value(m_pid, reg::rbp);
    auto return_address = read_mem(frame_pointer+8);

    while (dwarf::at_name(curr_func) != "main") {
        curr_func = get_func_from_pc(ret_addr);
        output_frame(curr_func);
        frame_pointer = read_mem(frame_pointer);
        return_address = read_mem(frame_pointer+8);
    }

```

但是在ARM体系结构中，出于性能的考虑，天才的开发者为了节约R7/R11寄存器，使其可以作为通用寄存器来使用，因此无法保证保存足够的信息来形成上述调用栈的（即使你向编译器传入了“-fno-omit-frame-pointer”）。比如下面两种情况，ARM就会不遵循一般意义上的序言（prologue），感兴趣的同学可以具体查看 [APCS Doc](https://www.cl.cam.ac.uk/~fms27/teaching/2001-02/arm-project/02-sort/apcs.txt#1018)。

- 函数为叶函数，即在函数体内再没有任何函数调用。

- 函数体非常小。


## Android中的unwind

我们知道大部分Android手机使用的都是ARM体系结构，那在Android中需要如何进行unwind呢？我们需要分两种情况分别讨论。

**1\. Debug版本unwind**

如果是Debug版本，我们可以通过“.debug\_frame”（有兴趣的同学可以了解一下 [DWARF](http://www.dwarfstd.org/doc/DWARF4.pdf)）来帮助我们进行unwind。这种方法十分高效也十分准确，但缺点是调试信息本身很大，甚至会比程序段（.TEXT段）更大，所以我们是无法在Release版本中包含这个信息的。

> DWARF 是一种标准调试信息格式。DWARF最早与ELF文件格式一起设计, 但DWARF本身是独立的一种对象文件格式。本身DAWRF和ELF的名字并没有任何意义（侏儒、精灵，是不是像魔兽世界的角色 :)），后续为了方便宣传，才命名为Debugging With Attributed Record Formats。引自 [wiki](https://en.wikipedia.org/wiki/DWARF#cite_note-eager-1)

**2\. Release版本unwind**

对于Release版本，系统使用了一种类似“.debug\_frame”的段落，是更加紧凑的方法，我们可以称之为unwind table，具体来说在x86和ARM64平台上是“.eh\_frame”和“.eh\_frame\_hdr”，在ARM32平台上为“.ARM.extab”和“.ARM.exidx”。

由于ARM32的标准早于DWARF的方法，所有ARM使用了自己的实现，不过它们的原理十分接近，后续我们只讨论“.eh\_frame”，如果你对ARM32的实现特别感兴趣，可以参考 [ARM-Unwinding-Tutorial](https://sourceware.org/binutils/docs/as/ARM-Unwinding-Tutorial.html)。

“.eh\_frame section”也是遵循DWARF的格式的，但DWARF本身十分琐碎也十分复杂，这里我们就不深入进去了，只涉及一些比较浅显的内容，你只需要了解DAWRF使用了一个被称为DI（Debugging Information Entry）的数据结构，去表示每个变量、变量类型和函数等在debug程序时需要用到的内容。

“.eh\_frame”使用了一种很聪明的方法构成了一个非常大的表，表中包含了每个程序段的地址对应的相应寄存器的值以及返回地址等相关信息，下面就是这张表的示例（你可以使用 `readelf --debug-dump=frames-interp` 去查看相应的信息，Release版中会精简一些信息，但所有帮助我们unwind的寄存器信息都会被保留）。

![](https://static001.geekbang.org/resource/image/03/70/03aa1ebfe910222910dee2b23c7a5770.png?wh=2178*462)

“.eh\_frame section”至少包含了一个CFI（Call Frame Information）。每个CFI都包含了两个条目：独立的CIE（Common Information Entry）和至少一个FDE（Frame Description Entry）。通常来讲CFI都对应一个对象文件，FDE则描述一个函数。

“ [.eh\_frame\_hdr](https://refspecs.linuxfoundation.org/LSB_1.3.0/gLSB/gLSB/ehframehdr.html) section”包含了一系列属性，除了一些基础的meta信息，还包含了一列有序信息（初始地址，指向“.eh\_frame”中FDE的指针），这些信息按照function排序，从而可以使用二分查找加速搜索。

![](https://static001.geekbang.org/resource/image/ba/d1/ba663ea69e7a64a716e37c7f6710f4d1.png?wh=1162*758)

## 总结

总的来说，unwind第一个栈帧是最难的，由于ARM无法保证会压基址指针寄存器（EBP）进栈，所以我们需要借助一些额外的信息（.eh\_frame）来帮助我们得到相应的基址指针寄存器的值。即使如此，生产环境还是会有各种栈破坏，所以还是有许多工作需要做，比如不同的调试器（GDB、LLDB）或者breakpad都实现了一些搜索算法去寻找潜在的栈帧，这里我们就不展开讨论了，感兴趣的同学可以查阅相关代码。

## 扩展阅读

下面给你一些外部链接，你可以阅读GCC中实现unwind的关键函数，有兴趣的同学可以在调试器中实现自己的unwinder。

- [\_Unwind\_Backtrace](https://gcc.gnu.org/git/gitweb.cgi?p=gcc.git;a=blob;f=libgcc/unwind.inc;h=12f62bca7335f3738fb723f00b1175493ef46345;hb=HEAD#l275)

- [uw\_frame\_state\_for](https://gcc.gnu.org/git/gitweb.cgi?p=gcc.git;a=blob;f=libgcc/unwind-dw2.c;h=b262fd9f5b92e2d0ea4f0e65152927de0290fcbd;hb=HEAD#l1222)

- [uw\_update\_context](https://gcc.gnu.org/git/gitweb.cgi?p=gcc.git;a=blob;f=libgcc/unwind-dw2.c;h=b262fd9f5b92e2d0ea4f0e65152927de0290fcbd;hb=HEAD#l1494)

- [uw\_update\_context\_1](https://gcc.gnu.org/git/gitweb.cgi?p=gcc.git;a=blob;f=libgcc/unwind-dw2.c;h=b262fd9f5b92e2d0ea4f0e65152927de0290fcbd;hb=HEAD#l1376)