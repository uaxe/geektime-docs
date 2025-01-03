有了开放的营商环境，咱们外包公司的创业之旅就要开始了。

上一节我们说，x86作为一个开放的营商环境，有两种模式，一种模式是实模式，只能寻址1M，每个段最多64K。这个太小了，相当于咱们创业的个体户模式。有了项目只能老板自己上，本小利微，万事开头难。另一种是保护模式，对于32位系统，能够寻址4G。这就是大买卖了，老板要雇佣很多人接项目。

几乎所有成功的公司，都是从个体户模式发展壮大的，因此，这一节咱们就从系统刚刚启动的个体户模式开始说起。

## BIOS时期

当你轻轻按下计算机的启动按钮时，你的主板就加上电了。

按照我们之前说的，这时候你的CPU应该开始执行指令了。你作为老板，同时也作为员工，要开始干活了。可是你发现，这个时候还没有项目执行计划书，所以你没啥可干的。

也就是说，这个时候没有操作系统，内存也是空的，一穷二白。CPU该怎么办呢？

你作为这个创业公司的老板，由于原来没开过公司，对于公司的运营当然是一脸懵的。但是我们有一个良好的营商环境，其中的创业指导中心早就考虑到这种情况了。于是，创业指导中心就给了你一套创业公司启动指导手册。你只要按着指导手册来干就行了。

![](https://static001.geekbang.org/resource/image/a4/6a/a4009d3de2dbae10340256af2737c26a.jpeg?wh=2113*1162)

计算机系统也早有计划。在主板上，有一个东西叫 **ROM**（Read Only Memory，只读存储器）。这和咱们平常说的内存 **RAM**（Random Access Memory，随机存取存储器）不同。

咱们平时买的内存条是可读可写的，这样才能保存计算结果。而ROM是只读的，上面早就固化了一些初始化的程序，也就是 **BIOS**（Basic Input and Output System，基本输入输出系统）。

如果你自己安装过操作系统，刚启动的时候，按某个组合键，显示器会弹出一个蓝色的界面。能够调整启动顺序的系统，就是我说的BIOS，然后我们就可以先执行它。

![](https://static001.geekbang.org/resource/image/13/b7/13187b1ffe878bc406da53967e8cddb7.png?wh=640*453)

创业初期，你的办公室肯定很小。假如现在你有1M的内存地址空间。这个空间非常有限，你需要好好利用才行。

![](https://static001.geekbang.org/resource/image/5f/fc/5f364ef5c9d1a3b1d9bb7153bd166bfc.jpeg?wh=1796*1148)

在x86系统中，将1M空间最上面的0xF0000到0xFFFFF这64K映射给ROM，也就是说，到这部分地址访问的时候，会访问ROM。

当电脑刚加电的时候，会做一些重置的工作，将CS设置为0xFFFF，将IP设置为0x0000，所以第一条指令就会指向0xFFFF0，正是在ROM的范围内。在这里，有一个JMP命令会跳到ROM中做初始化工作的代码，于是，BIOS开始进行初始化的工作。

创业指导手册第一条，BIOS要检查一下系统的硬件是不是都好着呢。

创业指导手册第二条，要有个办事大厅，只不过自己就是办事员。这个时期你能提供的服务很简单，但也会有零星的客户来提要求。

这个时候，要建立一个中断向量表和中断服务程序，因为现在你还要用键盘和鼠标，这些都要通过中断进行的。

这个时期也要给客户输出一些结果，因为需要你自己来，所以你还要充当客户对接人。你做了什么工作，做到了什么程度，都要主动显示给客户，也就是在内存空间映射显存的空间，在显示器上显示一些字符。

![](https://static001.geekbang.org/resource/image/29/63/2900bed28c7345e6c90437da8a5cd563.jpeg?wh=1949*1316)

最后，政府领进门，创业靠个人。接下来就是你发挥聪明才智的时候了。

## bootloader时期

政府给的创业指导手册只能保证你把公司成立起来，但是公司如何做大做强，需要你自己有一套经营方法。你可以试着从档案库里面翻翻，看哪里能够找到《企业经营宝典》。通过这个宝典，可以帮你建立一套完整的档案库管理体系，使得任何项目的档案查询都十分方便。

现在，什么线索都没有的BIOS，做完自己的事情，只能从档案库门卫开始，慢慢打听操作系统的下落。

操作系统在哪儿呢？一般都会在安装在硬盘上，在BIOS的界面上。你会看到一个启动盘的选项。启动盘有什么特点呢？它一般在第一个扇区，占512字节，而且以0xAA55结束。这是一个约定，当满足这个条件的时候，就说明这是一个启动盘，在512字节以内会启动相关的代码。

这些代码是谁放在这里的呢？在Linux里面有一个工具，叫 **Grub2**，全称Grand Unified Bootloader Version 2。顾名思义，就是搞系统启动的。

你可以通过grub2-mkconfig -o /boot/grub2/grub.cfg来配置系统启动的选项。你可以看到里面有类似这样的配置。

```
menuentry 'CentOS Linux (3.10.0-862.el7.x86_64) 7 (Core)' --class centos --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option 'gnulinux-3.10.0-862.el7.x86_64-advanced-b1aceb95-6b9e-464a-a589-bed66220ebee' {
	load_video
	set gfxpayload=keep
	insmod gzio
	insmod part_msdos
	insmod ext2
	set root='hd0,msdos1'
	if [ x$feature_platform_search_hint = xy ]; then
	  search --no-floppy --fs-uuid --set=root --hint='hd0,msdos1'  b1aceb95-6b9e-464a-a589-bed66220ebee
	else
	  search --no-floppy --fs-uuid --set=root b1aceb95-6b9e-464a-a589-bed66220ebee
	fi
	linux16 /boot/vmlinuz-3.10.0-862.el7.x86_64 root=UUID=b1aceb95-6b9e-464a-a589-bed66220ebee ro console=tty0 console=ttyS0,115200 crashkernel=auto net.ifnames=0 biosdevname=0 rhgb quiet
	initrd16 /boot/initramfs-3.10.0-862.el7.x86_64.img
}

```

这里面的选项会在系统启动的时候，成为一个列表，让你选择从哪个系统启动。最终显示出来的结果就是下面这张图。至于上面选项的具体意思，我们后面再说。

![](https://static001.geekbang.org/resource/image/88/97/883f3f5d4227a593228e1bcb93f67297.png?wh=716*245)

使用grub2-install /dev/sda，可以将启动程序安装到相应的位置。

grub2第一个要安装的就是boot.img。它由boot.S编译而成，一共512字节，正式安装到启动盘的第一个扇区。这个扇区通常称为 **MBR**（Master Boot Record，主引导记录/扇区）。

BIOS完成任务后，会将boot.img从硬盘加载到内存中的0x7c00来运行。

由于512个字节实在有限，boot.img做不了太多的事情。它能做的最重要的一个事情就是加载grub2的另一个镜像core.img。

引导扇区就是你找到的门卫，虽然他看着档案库的大门，但是知道的事情很少。他不知道你的宝典在哪里，但是，他知道应该问谁。门卫说，档案库入口处有个管理处，然后把你领到门口。

core.img就是管理处，它们知道的和能做的事情就多了一些。core.img由lzma\_decompress.img、diskboot.img、kernel.img和一系列的模块组成，功能比较丰富，能做很多事情。

![](https://static001.geekbang.org/resource/image/2b/6a/2b8573bbbf31fc0cb0420e32d07b196a.jpeg?wh=2489*1520)

boot.img先加载的是core.img的第一个扇区。如果从硬盘启动的话，这个扇区里面是diskboot.img，对应的代码是diskboot.S。

boot.img将控制权交给diskboot.img后，diskboot.img的任务就是将core.img的其他部分加载进来，先是解压缩程序lzma\_decompress.img，再往下是kernel.img，最后是各个模块module对应的映像。这里需要注意，它不是Linux的内核，而是grub的内核。

lzma\_decompress.img对应的代码是startup\_raw.S，本来kernel.img是压缩过的，现在执行的时候，需要解压缩。

在这之前，我们所有遇到过的程序都非常非常小，完全可以在实模式下运行，但是随着我们加载的东西越来越大，实模式这1M的地址空间实在放不下了，所以在真正的解压缩之前，lzma\_decompress.img做了一个重要的决定，就是调用real\_to\_prot，切换到保护模式，这样就能在更大的寻址空间里面，加载更多的东西。

## 从实模式切换到保护模式

好了，管理处听说你要找宝典，知道你将来是要做老板的人。既然是老板，早晚都要雇人干活的。这不是个体户小打小闹，所以，你需要切换到老板角色，进入保护模式了，把哪些是你的权限，哪些是你可以授权给别人的，都分得清清楚楚。

切换到保护模式要干很多工作，大部分工作都与内存的访问方式有关。

第一项是 **启用分段**，就是在内存里面建立段描述符表，将寄存器里面的段寄存器变成段选择子，指向某个段描述符，这样就能实现不同进程的切换了。第二项是 **启动分页**。能够管理的内存变大了，就需要将内存分成相等大小的块，这些我们放到内存那一节详细再讲。

切换到了老板角色，也是为了招聘很多人，同时接多个项目，这时候就需要划清界限，懂得集权与授权。

当了老板，眼界要宽多了，同理保护模式需要做一项工作，那就是打开Gate A20，也就是第21根地址线的控制线。在实模式8086下面，一共就20个地址线，可访问1M的地址空间。如果超过了这个限度怎么办呢？当然是绕回来了。在保护模式下，第21根要起作用了，于是我们就需要打开Gate A20。

切换保护模式的函数DATA32 call real\_to\_prot会打开Gate A20，也就是第21根地址线的控制线。

现在好了，有的是空间了。接下来我们要对压缩过的kernel.img进行解压缩，然后跳转到kernel.img开始运行。

切换到了老板角色，你可以正大光明地进入档案馆，寻找你的那本宝典。

kernel.img对应的代码是startup.S以及一堆c文件，在startup.S中会调用grub\_main，这是grub kernel的主函数。

在这个函数里面，grub\_load\_config()开始解析，我们上面写的那个grub.conf文件里的配置信息。

如果是正常启动，grub\_main最后会调用grub\_command\_execute (“normal”, 0, 0)，最终会调用grub\_normal\_execute()函数。在这个函数里面，grub\_show\_menu()会显示出让你选择的那个操作系统的列表。

同理，作为老板，你发现这类的宝典不止一本，经营企业的方式也有很多种，到底是人性化的，还是强纪律的，这个时候你要做一个选择。

一旦，你选定了某个宝典，启动某个操作系统，就要开始调用 grub\_menu\_execute\_entry() ，开始解析并执行你选择的那一项。接下来你的经营企业之路就此打开了。

例如里面的linux16命令，表示装载指定的内核文件，并传递内核启动参数。于是grub\_cmd\_linux()函数会被调用，它会首先读取Linux内核镜像头部的一些数据结构，放到内存中的数据结构来，进行检查。如果检查通过，则会读取整个Linux内核镜像到内存。

如果配置文件里面还有initrd命令，用于为即将启动的内核传递init ramdisk路径。于是grub\_cmd\_initrd()函数会被调用，将initramfs加载到内存中来。

当这些事情做完之后，grub\_command\_execute (“boot”, 0, 0)才开始真正地启动内核。

## 总结时刻

启动的过程比较复杂，我这里画一个图，让你比较形象地理解这个过程。你可以根据我讲的，自己来梳理一遍这个过程，做到不管是从流程还是细节上，都能心中有数。

![](https://static001.geekbang.org/resource/image/0a/6b/0a29c1d3e1a53b2523d2dcab3a59886b.jpeg?wh=1819*4309)

## 课堂练习

grub2是一个非常牛的Linux启动管理器，请你研究一下grub2的命令和配置，并试试通过它启动Ubuntu和centOS两个操作系统。

欢迎留言和我分享你的疑惑和见解，也欢迎你收藏本节内容，反复研读。你也可以把今天的内容分享给你的朋友，和他一起学习、进步。

![](https://static001.geekbang.org/resource/image/8c/37/8c0a95fa07a8b9a1abfd394479bdd637.jpg?wh=1110*659)