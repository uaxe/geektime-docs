你好，我是孙鹏飞。今天我们基于 [专栏第5期](http://time.geekbang.org/column/article/71982) 的练习Sample以及热点问题，我来给你做答疑。有关上一期答疑，你可以点击 [这里](http://time.geekbang.org/column/article/73068) 查看。

为了让同学们可以进行更多的实践，专栏第5期Sample采用了让你自己实现部分功能的形式，希望可以让你把专栏里讲的原理可以真正用起来。

前面几期已经有同学通过Pull request提交了练习作业，这里要给每位参与练习、提交作业的同学点个赞。

第5期的作业是根据系统源码来完成一个CPU数据的采集工具，并且在结尾我们提供了一个案例让你进行分析。我已经将例子的实现提交到了 [GitHub](http://github.com/AndroidAdvanceWithGeektime/Chapter05) 上，你可以参考一下。

在文中提到，“当发生ANR的时候，Android系统会打印CPU相关的信息到日志中，使用的是 [ProcessCpuTracker.java](http://androidxref.com/9.0.0_r3/xref/frameworks/base/core/java/com/android/internal/os/ProcessCpuTracker.java)”。ProcessCpuTracker的实现主要依赖于Linux里的/proc伪文件系统（in-memory pseudo-file system），主要使用到了/proc/stat、/proc/loadavg、/proc/\[pid\]/stat、/proc/\[pid\]/task相关的文件来读取数据。在Linux中有很多程序都依赖/proc下的数据，比如top、netstat、ifconfig等，Android里常用的procrank、librank、procmem等也都以此作为数据来源。关于/proc目录的结构在Linux Man Pages里有很详细的说明，在《Linux/Unix系统编程手册》这本书里，也有相关的中文说明。

关于proc有一些需要说明的地方，在不同的Linux内核中，该目录下的内容可能会有所不同，所以如果要使用该目录下的数据，可能需要做一些版本上的兼容处理。并且由于Linux内核更新速度较快，文档的更新可能还没有跟上，这就会导致一些数据和文档中说明的不一致，尤其是大量的以空格隔开的数字数据。这些文件其实并不是真正的文件，你用ls查看会发现它们的大小都是0，这些文件都是系统虚拟出来的，读取这些文件并不会涉及文件系统的一系列操作，只有很小的性能开销，而现阶段并没有类似文件系统监听文件修改的回调，所以需要采用轮询的方式来进行数据采集。

下面我们来看一下专栏文章结尾的案例分析。下面是这个示例的日志数据，我会通过分析数据来猜测一下是什么原因引起，并用代码还原这个情景。

```
usage: CPU usage 5000ms(from 23:23:33.000 to 23:23:38.000):
System TOTAL: 2.1% user + 16% kernel + 9.2% iowait + 0.2% irq + 0.1% softirq + 72% idle
CPU Core: 8
Load Average: 8.74 / 7.74 / 7.36

Process:com.sample.app
  50% 23468/com.sample.app(S): 11% user + 38% kernel faults:4965

Threads:
  43% 23493/singleThread(R): 6.5% user + 36% kernel faults：3094
  3.2% 23485/RenderThread(S): 2.1% user + 1% kernel faults：329
  0.3% 23468/.sample.app(S): 0.3% user + 0% kernel faults：6
  0.3% 23479/HeapTaskDaemon(S): 0.3% user + 0% kernel faults：982
  \.\.\.

```

上面的示例展示了一段在5秒时间内CPU的usage的情况。初看这个日志，你可以收集到几个重要信息。

1.在System Total部分user占用不多，CPU idle很高，消耗多在kernel和iowait。

2.CPU是8核的，Load Average大约也是8，表示CPU并不处于高负载情况。

3.在Process里展示了这段时间内sample app的CPU使用情况：user低，kernel高，并且有4965次page faults。

4.在Threads里展示了每个线程的usage情况，当前只有singleThread处于R状态，并且当前线程产生了3096次page faults，其他的线程包括主线程（Sample日志里可见的）都是处于S状态。

根据内核中的线程状态的 [宏的名字](http://elixir.bootlin.com/linux/v4.8/source/include/linux/sched.h#L207) 和缩写的对应，R值代表线程处于Running或者Runnable状态。Running状态说明线程当前被某个Core执行，Runnable状态说明线程当前正在处于等待队列中等待某个Core空闲下来去执行。从内核里看两个状态没有区别，线程都会持续执行。日志中的其他线程都处于S状态，S状态代表 [TASK\_INTERRUPTIBLE](http://elixir.bootlin.com/linux/v4.8/ident/TASK_INTERRUPTIBLE)，发生这种状态是线程主动让出了CPU，如果线程调用了sleep或者其他情况导致了自愿式的上下文切换（Voluntary Context Switches）就会处于S状态。常见的发生S状态的原因，可能是要等待一个相对较长时间的I/O操作或者一个IPC操作，如果一个I/O要获取的数据不在Buffer Cache或者Page Cache里，就需要从更慢的存储设备上读取，此时系统会把线程挂起，并放入一个等待I/O完成的队列里面，在I/O操作完成后产生中断，线程重新回到调度序列中。但只根据文中这个日志，并不能判定是何原因所引起的。

还有就是SingleThread的各项指标都相对处于一个很高的情况，而且产生了一些faults。page faluts分为三种：minor page fault、major page fault和invalid page fault，下面我们来具体分析。

minor page fault是内核在分配内存的时候采用一种Lazy的方式，申请内存的时候并不进行物理内存的分配，直到内存页被使用或者写入数据的时候，内核会收到一个MMU抛出的page fault，此时内核才进行物理内存分配操作，MMU会将虚拟地址和物理地址进行映射，这种情况产生的page fault就是minor page fault。

major page fault产生的原因是访问的内存不在虚拟地址空间，也不在物理内存中，需要从慢速设备载入，或者从Swap分区读取到物理内存中。需要注意的是，如果系统不支持 [zRAM](http://source.android.com/devices/tech/perf/low-ram) 来充当Swap分区，可以默认Android是没有Swap分区的，因为在Android里不会因为读取Swap而发生major page fault的情况。另一种情况是mmap一个文件后，虚拟内存区域、文件磁盘地址和物理内存做一个映射，在通过地址访问文件数据的时候发现内存中并没有文件数据，进而产生了major page fault的错误。

根据page fault发生的场景，虚拟页面可能有四种状态：

- 第一种，未分配；
- 第二种，已经分配但是未映射到物理内存；
- 第三种，已经分配并且已经映射到物理内存；
- 第四种，已经分配并映射到Swap分区（在Android中此种情况基本不存在）。

通过上面的讲解并结合page fault数据，你可以看到SingleThread你一共发生了3094次fault，根据每个页大小为4KB，可以知道在这个过程中SingleThread总共分配了大概12MB的空间。

下面我们来分析iowait数据。既然有iowait的占比，就说明在5秒内肯定进行了I/O操作，并且iowait占比还是比较大的，说明当时可能进行了大量的I/O操作，或者当时由于其他原因导致I/O操作缓慢。

从上面的分析可以猜测一下具体实现，并且在读和写的时候都有可能发生。由于我的手机写的性能要低一些，比较容易复现，所以下面的代码基于写操作实现。

```
File f = new File(getFilesDir(), "aee.txt");

FileOutputStream fos = new FileOutputStream(f);

byte[] data = new byte[1024 * 4 * 3000];//此处分配一个12mb 大小的 byte 数组

for (int i = 0; i < 30; i++) {//由于 IO cache 机制的原因所以此处写入多次cache，触发 dirty writeback 到磁盘中
    Arrays.fill(data, (byte) i);//当执行到此处的时候产生 minor fault，并且产生 User cpu useage
    fos.write(data);
}
fos.flush();
fos.close();

```

上面的代码抓取到的CPU数据如下。

```
E/ProcessCpuTracker: CPU usage from 5187ms to 121ms ago (2018-12-28 08:28:27.186 to 2018-12-28 08:28:32.252):
    40% 24155/com.sample.processtracker(R): 14% user + 26% kernel / faults: 5286 minor
    thread stats:
    35% 24184/SingleThread(S): 11% user + 24% kernel / faults: 3055 minor
    2.1% 24174/RenderThread(S): 1.3% user + 0.7% kernel / faults: 384 minor
    1.5% 24155/.processtracker(R): 1.1% user + 0.3% kernel / faults: 95 minor
    0.1% 24166/HeapTaskDaemon(S): 0.1% user + 0% kernel / faults: 1070 minor

    100% TOTAL(): 3.8% user + 7.8% kernel + 11% iowait + 0.1% irq + 0% softirq + 76% idle
    Load: 6.31 / 6.52 / 6.66

```

可以对比Sample中给出的数据，基本一致。

通过上面的说明，你可以如法炮制去分析ANR日志中相关的数据来查找性能瓶颈，比如，如果产生大量的major page fault其实是不太正常的，或者iowait过高就需要关注是否有很密集的I/O操作。

## 相关资料

- [低内存配置](http://source.android.com/devices/tech/perf/low-ram)
- [iowait的形成原因和内核分析](http://oenhan.com/iowait-wa-vmstat)
- [page fault带来的性能问题](http://yq.aliyun.com/articles/55820)
- [Linux工具快速教程](http://linuxtools-rst.readthedocs.io/zh_CN/latest/index.html)
- [Android: memory management insights, part I](http://fixbugfix.blogspot.com/2015/11/android-memory-management-insights-part.html)
- [Linux 2.6调度系统分析](http://www.ibm.com/developerworks/cn/linux/kernel/l-kn26sch/index.html?mhq=iowait&mhsrc=ibmsearch_a)
- 《性能之巅》

欢迎你点击“请朋友读”，把今天的内容分享给好友，邀请他一起学习。