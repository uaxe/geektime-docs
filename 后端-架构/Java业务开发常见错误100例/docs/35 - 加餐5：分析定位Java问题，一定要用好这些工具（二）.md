你好，我是朱晔。

在 [上一篇加餐](https://time.geekbang.org/column/article/224816) 中，我们介绍了使用JDK内置的一些工具、网络抓包工具Wireshark去分析、定位Java程序的问题。很多同学看完这一讲，留言反馈说是“打开了一片新天地，之前没有关注过JVM”“利用JVM工具发现了生产OOM的原因”。

其实，工具正是帮助我们深入到框架和组件内部，了解其运作方式和原理的重要抓手。所以，我们一定要用好它们。

今天，我继续和你介绍如何使用JVM堆转储的工具MAT来分析OOM问题，以及如何使用全能的故障诊断工具Arthas来分析、定位高CPU问题。

## 使用MAT分析OOM问题

对于排查OOM问题、分析程序堆内存使用情况，最好的方式就是分析堆转储。

堆转储，包含了堆现场全貌和线程栈信息（Java 6 Update 14开始包含）。我们在上一篇加餐中看到，使用jstat等工具虽然可以观察堆内存使用情况的变化，但是对程序内到底有多少对象、哪些是大对象还一无所知，也就是说只能看到问题但无法定位问题。而堆转储，就好似得到了病人在某个瞬间的全景核磁影像，可以拿着慢慢分析。

Java的OutOfMemoryError是比较严重的问题，需要分析出根因，所以对生产应用一般都会这样设置JVM参数，方便发生OOM时进行堆转储：

```
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=.

```

上一篇加餐中我们提到的jvisualvm工具，同样可以进行一键堆转储后，直接打开这个dump查看。但是，jvisualvm的堆转储分析功能并不是很强大，只能查看类使用内存的直方图，无法有效跟踪内存使用的引用关系，所以我更推荐使用Eclipse的Memory Analyzer（也叫做MAT）做堆转储的分析。你可以点击 [这个链接](https://www.eclipse.org/mat/)，下载MAT。

使用MAT分析OOM问题，一般可以按照以下思路进行：

1. 通过支配树功能或直方图功能查看消耗内存最大的类型，来分析内存泄露的大概原因；
2. 查看那些消耗内存最大的类型、详细的对象明细列表，以及它们的引用链，来定位内存泄露的具体点；
3. 配合查看对象属性的功能，可以脱离源码看到对象的各种属性的值和依赖关系，帮助我们理清程序逻辑和参数；
4. 辅助使用查看线程栈来看OOM问题是否和过多线程有关，甚至可以在线程栈看到OOM最后一刻出现异常的线程。

比如，我手头有一个OOM后得到的转储文件java\_pid29569.hprof，现在要使用MAT的直方图、支配树、线程栈、OQL等功能来分析此次OOM的原因。

首先，用MAT打开后先进入的是概览信息界面，可以看到整个堆是437.6MB：

![](https://static001.geekbang.org/resource/image/63/61/63ecdaf5ff7ac431f0d05661855b2e61.png?wh=2384*1500)

那么，这437.6MB都是什么对象呢？

如图所示，工具栏的第二个按钮可以打开直方图，直方图按照类型进行分组，列出了每个类有多少个实例，以及占用的内存。可以看到，char\[\]字节数组占用内存最多，对象数量也很多，结合第二位的String类型对象数量也很多，大概可以猜出（String使用char\[\]作为实际数据存储）程序可能是被字符串占满了内存，导致OOM。

![](https://static001.geekbang.org/resource/image/0b/b9/0b3ca076b31a2d571a47c64d622b0db9.png?wh=1610*1440)

我们继续分析下，到底是不是这样呢。

在char\[\]上点击右键，选择List objects->with incoming references，就可以列出所有的char\[\]实例，以及每个char\[\]的整个引用关系链：

![](https://static001.geekbang.org/resource/image/f1/a3/f162fb9c6505dc9a8f1ea9900437ada3.png?wh=1600*186)

随机展开一个char\[\]，如下图所示：

![](https://static001.geekbang.org/resource/image/dd/ac/dd4cb44ad54edee3a51f56a646c5f2ac.png?wh=3079*858)

接下来，我们按照红色框中的引用链来查看，尝试找到这些大char\[\]的来源：

- 在①处看到，这些char\[\]几乎都是10000个字符、占用20000字节左右（char是UTF-16，每一个字符占用2字节）；
- 在②处看到，char\[\]被String的value字段引用，说明char\[\]来自字符串；
- 在③处看到，String被ArrayList的elementData字段引用，说明这些字符串加入了一个ArrayList中；
- 在④处看到，ArrayList又被FooService的data字段引用，这个ArrayList整个RetainedHeap列的值是431MB。

Retained Heap（深堆）代表对象本身和对象关联的对象占用的内存，Shallow Heap（浅堆）代表对象本身占用的内存。比如，我们的FooService中的data这个ArrayList对象本身只有16字节，但是其所有关联的对象占用了431MB内存。这些就可以说明，肯定有哪里在不断向这个List中添加String数据，导致了OOM。

左侧的蓝色框可以查看每一个实例的内部属性，图中显示FooService有一个data属性，类型是ArrayList。

如果我们希望看到字符串完整内容的话，可以右键选择Copy->Value，把值复制到剪贴板或保存到文件中：

![](https://static001.geekbang.org/resource/image/cc/8f/cc1d53eb9570582da415c1aec5cc228f.png?wh=1844*688)

这里，我们复制出的是10000个字符a（下图红色部分可以看到）。对于真实案例，查看大字符串、大数据的实际内容对于识别数据来源，有很大意义：

![](https://static001.geekbang.org/resource/image/7b/a0/7b3198574113fecdd2a7de8cde8994a0.png?wh=2466*1594)

看到这些，我们已经基本可以还原出真实的代码是怎样的了。

其实，我们之前使用直方图定位FooService，已经走了些弯路。你可以点击工具栏中第三个按钮（下图左上角的红框所示）进入支配树界面（有关支配树的具体概念参考 [这里](https://help.eclipse.org/2020-03/index.jsp?topic=%2Forg.eclipse.mat.ui.help%2Fconcepts%2Fdominatortree.html&resultof%3D%2522%2564%256f%256d%2569%256e%2561%2574%256f%2572%2522%2520%2522%2564%256f%256d%2569%256e%2522%2520%2522%2574%2572%2565%2565%2522%2520)）。这个界面会按照对象保留的Retained Heap倒序直接列出占用内存最大的对象。

可以看到，第一位就是FooService，整个路径是FooSerice->ArrayList->Object\[\]->String->char\[\]（蓝色框部分），一共有21523个字符串（绿色方框部分）：

![](https://static001.geekbang.org/resource/image/7a/57/7adafa4178a4c72f8621b7eb49ee2757.png?wh=3226*1362)

这样，我们就从内存角度定位到FooService是根源了。那么，OOM的时候，FooService是在执行什么逻辑呢？

为解决这个问题，我们可以点击工具栏的第五个按钮（下图红色框所示）。打开线程视图，首先看到的就是一个名为main的线程（Name列），展开后果然发现了FooService：

![](https://static001.geekbang.org/resource/image/3a/ce/3a2c3d159e1599d906cc428d812cccce.png?wh=3140*1382)

先执行的方法先入栈，所以线程栈最上面是线程当前执行的方法，逐一往下看能看到整个调用路径。因为我们希望了解FooService.oom()方法，看看是谁在调用它，它的内部又调用了谁，所以选择以FooService.oom()方法（蓝色框）为起点来分析这个调用栈。

往下看整个绿色框部分，oom()方法被OOMApplication的run方法调用，而这个run方法又被SpringAppliction.callRunner方法调用。看到参数中的CommandLineRunner你应该能想到，OOMApplication其实是实现了CommandLineRunner接口，所以是SpringBoot应用程序启动后执行的。

以FooService为起点往上看，从紫色框中的Collectors和IntPipeline，你大概也可以猜出，这些字符串是由Stream操作产生的。再往上看，可以发现在StringBuilder的append操作的时候，出现了OutOfMemoryError异常（黑色框部分），说明这这个线程抛出了OOM异常。

我们看到，整个程序是Spring Boot应用程序，那么FooService是不是Spring的Bean呢，又是不是单例呢？如果能分析出这点的话，就更能确认是因为反复调用同一个FooService的oom方法，然后导致其内部的ArrayList不断增加数据的。

点击工具栏的第四个按钮（如下图红框所示），来到OQL界面。在这个界面，我们可以使用类似SQL的语法，在dump中搜索数据（你可以直接在MAT帮助菜单搜索OQL Syntax，来查看OQL的详细语法）。

比如，输入如下语句搜索FooService的实例：

```
SELECT * FROM org.geekbang.time.commonmistakes.troubleshootingtools.oom.FooService

```

可以看到只有一个实例，然后我们通过List objects功能搜索引用FooService的对象：

![](https://static001.geekbang.org/resource/image/19/43/1973846815bd9d78f85bef05b499e843.png?wh=3206*1284)

得到以下结果：

![](https://static001.geekbang.org/resource/image/07/a8/07e1216a6cc93bd146535b5809649ea8.png?wh=2074*704)

可以看到，一共两处引用：

- 第一处是，OOMApplication使用了FooService，这个我们已经知道了。
- 第二处是一个ConcurrentHashMap。可以看到，这个HashMap是DefaultListableBeanFactory的singletonObjects字段，可以证实FooService是Spring容器管理的单例的Bean。

你甚至可以在这个HashMap上点击右键，选择Java Collections->Hash Entries功能，来查看其内容：

![](https://static001.geekbang.org/resource/image/ce/5f/ce4020b8f63db060a94fd039314b2d5f.png?wh=3126*1112)

这样就列出了所有的Bean，可以在Value上的Regex进一步过滤。输入FooService后可以看到，类型为FooService的Bean只有一个，其名字是fooService：

![](https://static001.geekbang.org/resource/image/02/1a/023141fb717704cde9a57c5be6118d1a.png?wh=2678*206)

到现在为止，我们虽然没看程序代码，但是已经大概知道程序出现OOM的原因和大概的调用栈了。我们再贴出程序来对比一下，果然和我们看到得一模一样：

```
@SpringBootApplication
public class OOMApplication implements CommandLineRunner {
    @Autowired
    FooService fooService;
    public static void main(String[] args) {
        SpringApplication.run(OOMApplication.class, args);
    }
    @Override
    public void run(String... args) throws Exception {
        //程序启动后，不断调用Fooservice.oom()方法
        while (true) {
            fooService.oom();
        }
    }
}
@Component
public class FooService {
    List<String> data = new ArrayList<>();
    public void oom() {
        //往同一个ArrayList中不断加入大小为10KB的字符串
        data.add(IntStream.rangeClosed(1, 10_000)
                .mapToObj(__ -> "a")
                .collect(Collectors.joining("")));
    }
}

```

到这里，我们使用MAT工具从对象清单、大对象、线程栈等视角，分析了一个OOM程序的堆转储。可以发现，有了堆转储，几乎相当于拿到了应用程序的源码+当时那一刻的快照，OOM的问题无从遁形。

## 使用Arthas分析高CPU问题

[Arthas](https://alibaba.github.io/arthas/) 是阿里开源的Java诊断工具，相比JDK内置的诊断工具，要更人性化，并且功能强大，可以实现许多问题的一键定位，而且可以一键反编译类查看源码，甚至是直接进行生产代码热修复，实现在一个工具内快速定位和修复问题的一站式服务。今天，我就带你使用Arthas定位一个CPU使用高的问题，系统学习下这个工具的使用。

首先，下载并启动Arthas：

```
curl -O https://alibaba.github.io/arthas/arthas-boot.jar
java -jar arthas-boot.jar

```

启动后，直接找到我们要排查的JVM进程，然后可以看到Arthas附加进程成功：

```
[INFO] arthas-boot version: 3.1.7
[INFO] Found existing java process, please choose one and hit RETURN.
* [1]: 12707
  [2]: 30724 org.jetbrains.jps.cmdline.Launcher
  [3]: 30725 org.geekbang.time.commonmistakes.troubleshootingtools.highcpu.HighCPUApplication
  [4]: 24312 sun.tools.jconsole.JConsole
  [5]: 26328 org.jetbrains.jps.cmdline.Launcher
  [6]: 24106 org.netbeans.lib.profiler.server.ProfilerServer
3
[INFO] arthas home: /Users/zhuye/.arthas/lib/3.1.7/arthas
[INFO] Try to attach process 30725
[INFO] Attach process 30725 success.
[INFO] arthas-client connect 127.0.0.1 3658
  ,---.  ,------. ,--------.,--.  ,--.  ,---.   ,---.
 /  O  \ |  .--. ''--.  .--'|  '--'  | /  O  \ '   .-'
|  .-.  ||  '--'.'   |  |   |  .--.  ||  .-.  |`.  `-.
|  | |  ||  |\  \    |  |   |  |  |  ||  | |  |.-'    |
`--' `--'`--' '--'   `--'   `--'  `--'`--' `--'`-----'

wiki      https://alibaba.github.io/arthas
tutorials https://alibaba.github.io/arthas/arthas-tutorials
version   3.1.7
pid       30725
time      2020-01-30 15:48:33

```

输出help命令，可以看到所有支持的命令列表。今天，我们会用到dashboard、thread、jad、watch、ognl命令，来定位这个HighCPUApplication进程。你可以通过 [官方文档](https://alibaba.github.io/arthas/commands.html)，查看这些命令的完整介绍：

![](https://static001.geekbang.org/resource/image/47/73/47b2abc1c3a8c0670a60c6ed74761873.png?wh=2156*1496)

dashboard命令用于整体展示进程所有线程、内存、GC等情况，其输出如下：

![](https://static001.geekbang.org/resource/image/ce/4c/ce59c22389ba95104531e46edd9afa4c.png?wh=2772*1840)

可以看到，CPU高并不是GC引起的，占用CPU较多的线程有8个，其中7个是ForkJoinPool.commonPool。学习过 [加餐1](https://time.geekbang.org/column/article/212374) 的话，你应该就知道了，ForkJoinPool.commonPool是并行流默认使用的线程池。所以，此次CPU高的问题，应该出现在某段并行流的代码上。

接下来，要查看最繁忙的线程在执行的线程栈，可以使用thread -n命令。这里，我们查看下最忙的8个线程：

```
thread -n 8

```

输出如下：

![](https://static001.geekbang.org/resource/image/96/00/96cca0708e211ea7f7de413d40c72c00.png?wh=2964*1916)

可以看到，由于这些线程都在处理MD5的操作，所以占用了大量CPU资源。我们希望分析出代码中哪些逻辑可能会执行这个操作，所以需要从方法栈上找出我们自己写的类，并重点关注。

由于主线程也参与了ForkJoinPool的任务处理，因此我们可以通过主线程的栈看到需要重点关注org.geekbang.time.commonmistakes.troubleshootingtools.highcpu.HighCPUApplication类的doTask方法。

接下来，使用jad命令直接对HighCPUApplication类反编译：

```
jad org.geekbang.time.commonmistakes.troubleshootingtools.highcpu.HighCPUApplication

```

可以看到，调用路径是main->task()->doTask()，当doTask方法接收到的int参数等于某个常量的时候，会进行1万次的MD5操作，这就是耗费CPU的来源。那么，这个魔法值到底是多少呢？

![](https://static001.geekbang.org/resource/image/45/e5/4594c58363316d8ff69178d7a341d5e5.png?wh=2964*1916)

你可能想到了，通过jad命令继续查看User类即可。这里因为是Demo，所以我没有给出很复杂的逻辑。在业务逻辑很复杂的代码中，判断逻辑不可能这么直白，我们可能还需要分析出doTask的“慢”会慢在什么入参上。

这时，我们可以使用watch命令来观察方法入参。如下命令，表示需要监控耗时超过100毫秒的doTask方法的入参，并且输出入参，展开2层入参参数：

```
watch org.geekbang.time.commonmistakes.troubleshootingtools.highcpu.HighCPUApplication doTask '{params}' '#cost>100' -x 2

```

可以看到，所有耗时较久的doTask方法的入参都是0，意味着User.ADMN\_ID常量应该是0。

![](https://static001.geekbang.org/resource/image/04/3a/04e7a4e54c09052ab937f184ab31e03a.png?wh=2262*1066)

最后，我们使用ognl命令来运行一个表达式，直接查询User类的ADMIN\_ID静态字段来验证是不是这样，得到的结果果然是0：

```
[arthas@31126]$ ognl '@org.geekbang.time.commonmistakes.troubleshootingtools.highcpu.User@ADMIN_ID'
@Integer[0]

```

需要额外说明的是，由于monitor、trace、watch等命令是通过字节码增强技术来实现的，会在指定类的方法中插入一些切面来实现数据统计和观测，因此诊断结束要执行shutdown来还原类或方法字节码，然后退出Arthas。

在这个案例中，我们通过Arthas工具排查了高CPU的问题：

- 首先，通过dashboard + thread命令，基本可以在几秒钟内一键定位问题，找出消耗CPU最多的线程和方法栈；
- 然后，直接jad反编译相关代码，来确认根因；
- 此外，如果调用入参不明确的话，可以使用watch观察方法入参，并根据方法执行时间来过滤慢请求的入参。

可见，使用Arthas来定位生产问题根本用不着原始代码，也用不着通过增加日志来帮助我们分析入参，一个工具即可完成定位问题、分析问题的全套流程。

对于应用故障分析，除了阿里Arthas之外，还可以关注去哪儿的 [Bistoury工具](https://github.com/qunarcorp/bistoury)，其提供了可视化界面，并且可以针对多台机器进行管理，甚至提供了在线断点调试等功能，模拟IDE的调试体验。

## 重点回顾

最后，我再和你分享一个案例吧。

有一次开发同学遇到一个OOM问题，通过查监控、查日志、查调用链路排查了数小时也无法定位问题，但我拿到堆转储文件后，直接打开支配树图一眼就看到了可疑点。Mybatis每次查询都查询出了几百万条数据，通过查看线程栈马上可以定位到出现Bug的方法名，然后来到代码果然发现因为参数条件为null导致了全表查询，整个定位过程不足5分钟。

从这个案例我们看到，使用正确的工具、正确的方法来分析问题，几乎可以在几分钟内定位到问题根因。今天，我和你介绍的MAT正是分析Java堆内存问题的利器，而Arthas是快速定位分析Java程序生产Bug的利器。利用好这两个工具，就可以帮助我们在分钟级定位生产故障。

## 思考与讨论

1. 在介绍 [线程池](https://time.geekbang.org/column/article/210337) 的时候，我们模拟了两种可能的OOM情况，一种是使用Executors.newFixedThreadPool，一种是使用Executors.newCachedThreadPool，你能回忆起OOM的原因吗？假设并不知道OOM的原因，拿到了这两种OOM后的堆转储，你能否尝试使用MAT分析堆转储来定位问题呢？
2. Arthas还有一个强大的热修复功能。比如，遇到高CPU问题时，我们定位出是管理员用户会执行很多次MD5，消耗大量CPU资源。这时，我们可以直接在服务器上进行热修复，步骤是：jad命令反编译代码->使用文本编辑器（比如Vim）直接修改代码->使用sc命令查找代码所在类的ClassLoader->使用redefine命令热更新代码。你可以尝试使用这个流程，直接修复程序（注释doTask方法中的相关代码）吗？

在平时工作中，你还会使用什么工具来分析排查Java应用程序的问题呢？我是朱晔，欢迎在评论区与我留言分享你的想法，也欢迎你把今天的内容分享给你的朋友或同事，一起交流。