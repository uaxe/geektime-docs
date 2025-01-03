你好，我是倪朋飞。

上一节我们详细学习了 Linux 内存回收，特别是 Swap 的原理，先简单回顾一下。

在内存资源紧张时，Linux通过直接内存回收和定期扫描的方式，来释放文件页和匿名页，以便把内存分配给更需要的进程使用。

- 文件页的回收比较容易理解，直接清空缓存，或者把脏数据写回磁盘后，再释放缓存就可以了。

- 而对不常访问的匿名页，则需要通过Swap换出到磁盘中，这样在下次访问的时候，再次从磁盘换入到内存中就可以了。


开启 Swap 后，你可以设置 /proc/sys/vm/min\_free\_kbytes ，来调整系统定期回收内存的阈值，也可以设置 /proc/sys/vm/swappiness ，来调整文件页和匿名页的回收倾向。

那么，当 Swap 使用升高时，要如何定位和分析呢？下面，我们就来看一个磁盘I/O的案例，实战分析和演练。

## 案例

下面案例基于 Ubuntu 18.04，同样适用于其他的 Linux 系统。

- 机器配置：2 CPU，8GB 内存

- 你需要预先安装 sysstat 等工具，如 apt install sysstat


首先，我们打开两个终端，分别 SSH 登录到两台机器上，并安装上面提到的这些工具。

同以前的案例一样，接下来的所有命令都默认以 root 用户运行，如果你是用普通用户身份登陆系统，请运行 sudo su root 命令切换到 root 用户。

如果安装过程中有什么问题，同样鼓励你先自己搜索解决，解决不了的，可以在留言区向我提问。

然后，在终端中运行free命令，查看Swap的使用情况。比如，在我的机器中，输出如下：

```
$ free
             total        used        free      shared  buff/cache   available
Mem:        8169348      331668     6715972         696     1121708     7522896
Swap:             0           0           0

```

从这个free输出你可以看到，Swap的大小是0，这说明我的机器没有配置Swap。

为了继续Swap的案例， 就需要先配置、开启Swap。如果你的环境中已经开启了Swap，那你可以略过下面的开启步骤，继续往后走。

要开启Swap，我们首先要清楚，Linux本身支持两种类型的Swap，即Swap分区和Swap文件。以Swap文件为例，在第一个终端中运行下面的命令开启Swap，我这里配置Swap文件的大小为8GB：

```
# 创建Swap文件
$ fallocate -l 8G /mnt/swapfile
# 修改权限只有根用户可以访问
$ chmod 600 /mnt/swapfile
# 配置Swap文件
$ mkswap /mnt/swapfile
# 开启Swap
$ swapon /mnt/swapfile

```

然后，再执行free命令，确认Swap配置成功：

```
$ free
             total        used        free      shared  buff/cache   available
Mem:        8169348      331668     6715972         696     1121708     7522896
Swap:       8388604           0     8388604

```

现在，free 输出中，Swap 空间以及剩余空间都从 0 变成了8GB，说明Swap已经 **正常开启**。

接下来，我们在第一个终端中，运行下面的 dd 命令，模拟大文件的读取：

```
# 写入空设备，实际上只有磁盘的读请求
$ dd if=/dev/sda1 of=/dev/null bs=1G count=2048

```

接着，在第二个终端中运行 sar 命令，查看内存各个指标的变化情况。你可以多观察一会儿，查看这些指标的变化情况。

```
# 间隔1秒输出一组数据
# -r表示显示内存使用情况，-S表示显示Swap使用情况
$ sar -r -S 1
04:39:56    kbmemfree   kbavail kbmemused  %memused kbbuffers  kbcached  kbcommit   %commit  kbactive   kbinact   kbdirty
04:39:57      6249676   6839824   1919632     23.50    740512     67316   1691736     10.22    815156    841868         4

04:39:56    kbswpfree kbswpused  %swpused  kbswpcad   %swpcad
04:39:57      8388604         0      0.00         0      0.00

04:39:57    kbmemfree   kbavail kbmemused  %memused kbbuffers  kbcached  kbcommit   %commit  kbactive   kbinact   kbdirty
04:39:58      6184472   6807064   1984836     24.30    772768     67380   1691736     10.22    847932    874224        20

04:39:57    kbswpfree kbswpused  %swpused  kbswpcad   %swpcad
04:39:58      8388604         0      0.00         0      0.00

…

04:44:06    kbmemfree   kbavail kbmemused  %memused kbbuffers  kbcached  kbcommit   %commit  kbactive   kbinact   kbdirty
04:44:07       152780   6525716   8016528     98.13   6530440     51316   1691736     10.22    867124   6869332         0

04:44:06    kbswpfree kbswpused  %swpused  kbswpcad   %swpcad
04:44:07      8384508      4096      0.05        52      1.27

```

我们可以看到，sar的输出结果是两个表格，第一个表格表示内存的使用情况，第二个表格表示Swap的使用情况。其中，各个指标名称前面的kb前缀，表示这些指标的单位是KB。

去掉前缀后，你会发现，大部分指标我们都已经见过了，剩下的几个新出现的指标，我来简单介绍一下。

- kbcommit，表示当前系统负载需要的内存。它实际上是为了保证系统内存不溢出，对需要内存的估计值。%commit，就是这个值相对总内存的百分比。

- kbactive，表示活跃内存，也就是最近使用过的内存，一般不会被系统回收。

- kbinact，表示非活跃内存，也就是不常访问的内存，有可能会被系统回收。


清楚了界面指标的含义后，我们再结合具体数值，来分析相关的现象。你可以清楚地看到，总的内存使用率（%memused）在不断增长，从开始的23%一直长到了 98%，并且主要内存都被缓冲区（kbbuffers）占用。具体来说：

- 刚开始，剩余内存（kbmemfree）不断减少，而缓冲区（kbbuffers）则不断增大，由此可知，剩余内存不断分配给了缓冲区。

- 一段时间后，剩余内存已经很小，而缓冲区占用了大部分内存。这时候，Swap的使用开始逐渐增大，缓冲区和剩余内存则只在小范围内波动。


你可能困惑了，为什么缓冲区在不停增大？这又是哪些进程导致的呢？

显然，我们还得看看进程缓存的情况。在前面缓存的案例中我们学过， cachetop 正好能满足这一点。那我们就来 cachetop 一下。

在第二个终端中，按下Ctrl+C停止sar命令，然后运行下面的cachetop命令，观察缓存的使用情况：

```
$ cachetop 5
12:28:28 Buffers MB: 6349 / Cached MB: 87 / Sort: HITS / Order: ascending
PID      UID      CMD              HITS     MISSES   DIRTIES  READ_HIT%  WRITE_HIT%
   18280 root     python                 22        0        0     100.0%       0.0%
   18279 root     dd                  41088    41022        0      50.0%      50.0%

```

通过cachetop的输出，我们看到，dd进程的读写请求只有50%的命中率，并且未命中的缓存页数（MISSES）为41022（单位是页）。这说明，正是案例开始时运行的dd，导致了缓冲区使用升高。

你可能接着会问，为什么Swap也跟着升高了呢？直观来说，缓冲区占了系统绝大部分内存，还属于可回收内存，内存不够用时，不应该先回收缓冲区吗？

这种情况，我们还得进一步通过 /proc/zoneinfo ，观察剩余内存、内存阈值以及匿名页和文件页的活跃情况。

你可以在第二个终端中，按下Ctrl+C，停止cachetop命令。然后运行下面的命令，观察 /proc/zoneinfo 中这几个指标的变化情况：

```
# -d 表示高亮变化的字段
# -A 表示仅显示Normal行以及之后的15行输出
$ watch -d grep -A 15 'Normal' /proc/zoneinfo
Node 0, zone   Normal
  pages free     21328
        min      14896
        low      18620
        high     22344
        spanned  1835008
        present  1835008
        managed  1796710
        protection: (0, 0, 0, 0, 0)
      nr_free_pages 21328
      nr_zone_inactive_anon 79776
      nr_zone_active_anon 206854
      nr_zone_inactive_file 918561
      nr_zone_active_file 496695
      nr_zone_unevictable 2251
      nr_zone_write_pending 0

```

你可以发现，剩余内存（pages\_free）在一个小范围内不停地波动。当它小于页低阈值（pages\_low) 时，又会突然增大到一个大于页高阈值（pages\_high）的值。

再结合刚刚用 sar 看到的剩余内存和缓冲区的变化情况，我们可以推导出，剩余内存和缓冲区的波动变化，正是由于内存回收和缓存再次分配的循环往复。

- 当剩余内存小于页低阈值时，系统会回收一些缓存和匿名内存，使剩余内存增大。其中，缓存的回收导致sar中的缓冲区减小，而匿名内存的回收导致了Swap的使用增大。

- 紧接着，由于dd还在继续，剩余内存又会重新分配给缓存，导致剩余内存减少，缓冲区增大。


其实还有一个有趣的现象，如果多次运行dd和sar，你可能会发现，在多次的循环重复中，有时候是Swap用得比较多，有时候Swap很少，反而缓冲区的波动更大。

换句话说，系统回收内存时，有时候会回收更多的文件页，有时候又回收了更多的匿名页。

显然，系统回收不同类型内存的倾向，似乎不那么明显。你应该想到了上节课提到的swappiness，正是调整不同类型内存回收的配置选项。

还是在第二个终端中，按下Ctrl+C停止watch命令，然后运行下面的命令，查看swappiness的配置：

```
$ cat /proc/sys/vm/swappiness
60

```

swappiness显示的是默认值60，这是一个相对中和的配置，所以系统会根据实际运行情况，选择合适的回收类型，比如回收不活跃的匿名页，或者不活跃的文件页。

到这里，我们已经找出了Swap发生的根源。另一个问题就是，刚才的Swap到底影响了哪些应用程序呢？换句话说，Swap换出的是哪些进程的内存？

这里我还是推荐 proc文件系统，用来查看进程Swap换出的虚拟内存大小，它保存在 /proc/pid/status中的VmSwap中（推荐你执行man proc来查询其他字段的含义）。

在第二个终端中运行下面的命令，就可以查看使用Swap最多的进程。注意for、awk、sort都是最常用的Linux命令，如果你还不熟悉，可以用man来查询它们的手册，或上网搜索教程来学习。

```
# 按VmSwap使用量对进程排序，输出进程名称、进程ID以及SWAP用量
$ for file in /proc/*/status ; do awk '/VmSwap|Name|^Pid/{printf $2 " " $3}END{ print ""}' $file; done | sort -k 3 -n -r | head
dockerd 2226 10728 kB
docker-containe 2251 8516 kB
snapd 936 4020 kB
networkd-dispat 911 836 kB
polkitd 1004 44 kB

```

从这里你可以看到，使用Swap比较多的是dockerd 和 docker-containe 进程，所以，当dockerd再次访问这些换出到磁盘的内存时，也会比较慢。

这也说明了一点，虽然缓存属于可回收内存，但在类似大文件拷贝这类场景下，系统还是会用Swap机制来回收匿名内存，而不仅仅是回收占用绝大部分内存的文件页。

最后，如果你在一开始配置了 Swap，不要忘记在案例结束后关闭。你可以运行下面的命令，关闭Swap：

```
$ swapoff -a

```

实际上，关闭Swap后再重新打开，也是一种常用的Swap空间清理方法，比如：

```
$ swapoff -a && swapon -a

```

## 小结

在内存资源紧张时，Linux 会通过 Swap ，把不常访问的匿名页换出到磁盘中，下次访问的时候再从磁盘换入到内存中来。你可以设置/proc/sys/vm/min\_free\_kbytes，来调整系统定期回收内存的阈值；也可以设置/proc/sys/vm/swappiness，来调整文件页和匿名页的回收倾向。

当Swap变高时，你可以用 sar、/proc/zoneinfo、/proc/pid/status等方法，查看系统和进程的内存使用情况，进而找出Swap升高的根源和受影响的进程。

反过来说，通常，降低Swap的使用，可以提高系统的整体性能。要怎么做呢？这里，我也总结了几种常见的降低方法。

- 禁止Swap，现在服务器的内存足够大，所以除非有必要，禁用Swap就可以了。随着云计算的普及，大部分云平台中的虚拟机都默认禁止Swap。

- 如果实在需要用到Swap，可以尝试降低swappiness的值，减少内存回收时Swap的使用倾向。

- 响应延迟敏感的应用，如果它们可能在开启Swap的服务器中运行，你还可以用库函数 mlock() 或者 mlockall()锁定内存，阻止它们的内存换出。


## 思考

最后，给你留一个思考题。

今天的案例中，swappiness使用的是默认配置的60。如果把它配置成0的话，还会发生Swap吗？这又是为什么呢？

希望你可以实际操作一下，重点观察sar的输出，并结合今天的内容来记录、总结。

欢迎留言和我讨论，也欢迎把这篇文章分享给你的同事、朋友。我们一起在实战中演练，在交流中进步。