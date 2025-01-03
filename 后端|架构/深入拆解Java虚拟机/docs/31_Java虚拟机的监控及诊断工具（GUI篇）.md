今天我们来继续了解Java虚拟机的监控及诊断工具。

## eclipse MAT

在上一篇中，我介绍了 `jmap` 工具，它支持导出Java虚拟机堆的二进制快照。eclipse的 [MAT工具](https://www.eclipse.org/mat/) 便是其中一个能够解析这类二进制快照的工具。

MAT本身也能够获取堆的二进制快照。该功能将借助 `jps` 列出当前正在运行的Java进程，以供选择并获取快照。由于 `jps` 会将自己列入其中，因此你会在列表中发现一个已经结束运行的 `jps` 进程。

![](https://static001.geekbang.org/resource/image/c9/7e/c9072149fb112312cbc217acc2660c7e.png?wh=1280*894)

MAT获取二进制快照的方式有三种，一是使用Attach API，二是新建一个Java虚拟机来运行Attach API，三是使用 `jmap` 工具。

这三种本质上都是在使用Attach API。不过，在目标进程启用了 `DisableAttachMechanism` 参数时，前两者将不在选取列表中显示，后者将在运行时报错。

当加载完堆快照之后，MAT的主界面将展示一张饼状图，其中列举占据的Retained heap最多的几个对象。

![](https://static001.geekbang.org/resource/image/da/bf/da2e5894d0be535b6daa5084beb33ebf.png?wh=1920*1116)

这里讲一下MAT计算对象占据内存的 [两种方式](https://help.eclipse.org/mars/topic/org.eclipse.mat.ui.help/concepts/shallowretainedheap.html?cp=46_2_1)。第一种是Shallow heap，指的是对象自身所占据的内存。第二种是Retained heap，指的是当对象不再被引用时，垃圾回收器所能回收的总内存，包括对象自身所占据的内存，以及仅能够通过该对象引用到的其他对象所占据的内存。上面的饼状图便是基于Retained heap的。

MAT包括了两个比较重要的视图，分别是直方图（histogram）和支配树（dominator tree）。

![](https://static001.geekbang.org/resource/image/bb/05/bbb59ca4d86c227dac23f30c360c9405.png?wh=1510*1394)

MAT的直方图和 `jmap` 的 `-histo` 子命令一样，都能够展示各个类的实例数目以及这些实例的Shallow heap总和。但是，MAT的直方图还能够计算Retained heap，并支持基于实例数目或Retained heap的排序方式（默认为Shallow heap）。此外，MAT还可以将直方图中的类按照超类、类加载器或者包名分组。

当选中某个类时，MAT界面左上角的Inspector窗口将展示该类的Class实例的相关信息，如类加载器等。（下图中的 `ClassLoader @ 0x0` 指的便是启动类加载器。）

![](https://static001.geekbang.org/resource/image/dd/ab/dde7022060fad3945944fb7e4c9926ab.png?wh=1550*648)

支配树的概念源自图论。在一则流图（flow diagram）中，如果从入口节点到b节点的所有路径都要经过a节点，那么a支配（dominate）b。

在a支配b，且a不同于b的情况下（即a严格支配b），如果从a节点到b节点的所有路径中不存在支配b的其他节点，那么a直接支配（immediate dominate）b。这里的支配树指的便是由节点的直接支配节点所组成的树状结构。

我们可以将堆中所有的对象看成一张对象图，每个对象是一个图节点，而GC Roots则是对象图的入口，对象之间的引用关系则构成了对象图中的有向边。这样一来，我们便能够构造出该对象图所对应的支配树。

MAT将按照每个对象Retained heap的大小排列该支配树。如下图所示：

![](https://static001.geekbang.org/resource/image/0d/a6/0d4ea7f00d500db8a978ff0183a840a6.png?wh=1920*1045)

根据Retained heap的定义，只要能够回收上图右侧的表中的第一个对象，那么垃圾回收器便能够释放出13.6MB内存。

需要注意的是，对象的引用型字段未必对应支配树中的父子节点关系。假设对象a拥有两个引用型字段，分别指向b和c。而b和c各自拥有一个引用型字段，但都指向d。如果没有其他引用指向b、c或d，那么a直接支配b、c和d，而b（或c）和d之间不存在支配关系。

当在支配树视图中选中某一对象时，我们还可以通过Path To GC Roots功能，反向列出该对象到GC Roots的引用路径。如下图所示：

![](https://static001.geekbang.org/resource/image/e0/e7/e04d55d955832bf681aba16dcffc2ee7.png?wh=1388*816)

MAT还将自动匹配内存泄漏中的常见模式，并汇报潜在的内存泄漏问题。具体可参考该 [帮助文档](https://help.eclipse.org/mars/topic/org.eclipse.mat.ui.help/tasks/runningleaksuspectreport.html?cp=46_3_1) 以及 [这篇博客](http://memoryanalyzer.blogspot.com/2008/05/automated-heap-dump-analysis-finding.html)。

## Java Mission Control

> 注意：自Java 11开始，本节介绍的JFR已经开源。但在之前的Java版本，JFR属于Commercial Feature，需要通过Java虚拟机参数 `-XX:+UnlockCommercialFeatures` 开启。
>
> 我个人不清楚也不能回答关于Java 11之前的版本是否仍需要商务许可（Commercial License）的问题。请另行咨询后再使用，或者直接使用Java 11。
>
> [Java Mission Control](http://jdk.java.net/jmc/)（JMC）是Java虚拟机平台上的性能监控工具。它包含一个GUI客户端，以及众多用来收集Java虚拟机性能数据的插件，如JMX Console（能够访问用来存放虚拟机各个子系统运行数据的 [MXBeans](https://en.wikipedia.org/wiki/Java_Management_Extensions#Managed_beans)），以及虚拟机内置的高效profiling工具Java Flight Recorder（JFR）。

JFR的性能开销很小，在默认配置下平均低于1%。与其他工具相比，JFR能够直接访问虚拟机内的数据，并且不会影响虚拟机的优化。因此，它非常适用于生产环境下满负荷运行的Java程序。

当启用时，JFR将记录运行过程中发生的一系列事件。其中包括Java层面的事件，如线程事件、锁事件，以及Java虚拟机内部的事件，如新建对象、垃圾回收和即时编译事件。

按照发生时机以及持续时间来划分，JFR的事件共有四种类型，它们分别为以下四种。

1. 瞬时事件（Instant Event），用户关心的是它们发生与否，例如异常、线程启动事件。
2. 持续事件（Duration Event），用户关心的是它们的持续时间，例如垃圾回收事件。
3. 计时事件（Timed Event），是时长超出指定阈值的持续事件。
4. 取样事件（Sample Event），是周期性取样的事件。


   取样事件的其中一个常见例子便是方法抽样（Method Sampling），即每隔一段时间统计各个线程的栈轨迹。如果在这些抽样取得的栈轨迹中存在一个反复出现的方法，那么我们可以推测该方法是热点方法。

JFR的取样事件要比其他工具更加精确。以方法抽样为例，其他工具通常基于JVMTI（ [Java Virtual Machine Tool Interface](https://docs.oracle.com/en/java/javase/11/docs/specs/jvmti.html)）的 `GetAllStackTraces` API。该API依赖于安全点机制，其获得的栈轨迹总是在安全点上，由此得出的结论未必精确。JFR则不然，它不依赖于安全点机制，因此其结果相对来说更加精确。

JFR的启用方式主要有三种。

第一种是在运行目标Java程序时添加 `-XX:StartFlightRecording=` 参数。关于该参数的配置详情，你可以参考 [该帮助文档](https://docs.oracle.com/en/java/javase/11/tools/java.html)（请在页面中搜索 `StartFlightRecording`）。

下面我列举三种常见的配置方式。

- 在下面这条命令中，JFR将会在Java虚拟机启动5s后（对应 `delay=5s`）收集数据，持续20s（对应 `duration=20s`）。当收集完毕后，JFR会将收集得到的数据保存至指定的文件中（对应 `filename=myrecording.jfr`）。

```
# Time fixed
$ java -XX:StartFlightRecording=delay=5s,duration=20s,filename=myrecording.jfr,settings=profile MyApp

```

> `settings=profile` 指定了JFR所收集的事件类型。默认情况下，JFR将加载配置文件 `$JDK/lib/jfr/default.jfc`，并识别其中所包含的事件类型。当使用了 `settings=profile` 配置时，JFR将加载配置文件 `$JDK/lib/jfr/profile.jfc`。该配置文件所包含的事件类型要多于默认的 `default.jfc`，因此性能开销也要大一些（约为2%）。
>
> `default.jfc` 以及 `profile.jfc` 均为XML文件。后面我会介绍如何利用JMC来进行修改。

- 在下面这条命令中，JFR将在Java虚拟机启动之后持续收集数据，直至进程退出。在进程退出时（对应 `dumponexit=true`），JFR会将收集得到的数据保存至指定的文件中。

```
# Continuous, dump on exit
$ java -XX:StartFlightRecording=dumponexit=true,filename=myrecording.jfr MyApp

```

- 在下面这条命令中，JFR将在Java虚拟机启动之后持续收集数据，直至进程退出。该命令不会主动保存JFR收集得到的数据。

```
# Continuous, dump on demand
$ java -XX:StartFlightRecording=maxage=10m,maxsize=100m,name=SomeLabel MyApp
Started recording 1.

Use jcmd 38502 JFR.dump name=SomeLabel filename=FILEPATH to copy recording data to file.
...

```

由于JFR将持续收集数据，如果不加以限制，那么JFR可能会填满硬盘的所有空间。因此，我们有必要对这种模式下所收集的数据进行限制。

在这条命令中， `maxage=10m` 指的是仅保留10分钟以内的事件， `maxsize=100m` 指的是仅保留100MB以内的事件。一旦所收集的事件达到其中任意一个限制，JFR便会开始清除不合规格的事件。

然而，为了保持较小的性能开销，JFR并不会频繁地校验这两个限制。因此，在实践过程中你往往会发现指定文件的大小超出限制，或者文件中所存储事件的时间超出限制。具体解释请参考 [这篇帖子](https://community.oracle.com/thread/3514679)。

前面提到，该命令不会主动保存JFR收集得到的数据。用户需要运行 `jcmd <PID> JFR.dump` 命令方能保存。

这便是JFR的第二种启用方式，即通过 `jcmd` 来让JFR开始收集数据、停止收集数据，或者保存所收集的数据，对应的子命令分别为 `JFR.start`， `JFR.stop`，以及 `JFR.dump`。

`JFR.start` 子命令所接收的配置及格式和 `-XX:StartFlightRecording=` 参数的类似。这些配置包括 `delay`、 `duration`、 `settings`、 `maxage`、 `maxsize` 以及 `name`。前几个参数我们都已经介绍过了，最后一个参数 `name` 就是一个标签，当同一进程中存在多个JFR数据收集操作时，我们可以通过该标签来辨别。

在启动目标进程时，我们不再添加 `-XX:StartFlightRecording=` 参数。在目标进程运行过程中，我们可以运行 `JFR.start` 子命令远程启用目标进程的JFR功能。具体用法如下所示：

```
$ jcmd <PID> JFR.start settings=profile maxage=10m maxsize=150m name=SomeLabel

```

上述命令运行过后，目标进程中的JFR已经开始收集数据。此时，我们可以通过下述命令来导出已经收集到的数据：

```
$ jcmd <PID> JFR.dump name=SomeLabel filename=myrecording.jfr

```

最后，我们可以通过下述命令关闭目标进程中的JFR：

```
$ jcmd <PID> JFR.stop name=SomeLabel

```

关于 `JFR.start`、 `JFR.dump` 和 `JFR.stop` 的其他用法，你可以参考 [该帮助文档](https://docs.oracle.com/javacomponents/jmc-5-5/jfr-runtime-guide/comline.htm#JFRRT185)。

第三种启用JFR的方式则是JMC中的JFR插件。

![](https://static001.geekbang.org/resource/image/39/16/395900f606fd93570196a6dcbac75e16.png?wh=752*458)

在JMC GUI客户端左侧的JVM浏览器中，我们可以看到所有正在运行的Java程序。当点击右键弹出菜单中的 `Start Flight Recording...` 时，JMC便会弹出另一个窗口，用来配置JFR的启动参数，如下图所示：

![](https://static001.geekbang.org/resource/image/31/6a/31f86bc1cafc569f51e0364d716cab6a.png?wh=1330*1020)

这里的配置参数与前两种启动JFR的方式并无二致，同样也包括标签名、收集数据的持续时间、缓存事件的时间及空间限制，以及配置所要监控事件的 `Event settings`。

（这里对应前两种启动方式的 `settings=default|profile`）

> JMC提供了两个选择：Continuous和Profiling，分别对应 `$JDK/lib/jfr/` 里的 `default.jfc` 和 `profile.jfc`。

我们可以通过JMC的 `Flight Recording Template Manager` 导入这些jfc文件，并在GUI界面上进行更改。更改完毕后，我们可以导出为新的jfc文件，以便在服务器端使用。

当收集完成时，JMC会自动打开所生成的jfr文件，并在主界面中列举目标进程在收集数据的这段时间内的潜在问题。例如， `Parallel Threads` 一节，便汇报了没有完整利用CPU资源的问题。

![](https://static001.geekbang.org/resource/image/5a/7c/5a4302c29947518250e2b697aecc8d7c.png?wh=1920*1062)

客户端的左边则罗列了Java虚拟机的各个子系统。JMC将根据JFR所收集到的每个子系统的事件来进行可视化，转换成图或者表。

![](https://static001.geekbang.org/resource/image/db/ff/dbc36a8713af058c79df2878379276ff.png?wh=732*1272)

这里我简单地介绍其中两个。

垃圾回收子系统所对应的选项卡展示了JFR所收集到的GC事件，以及基于这些GC事件的数据生成的堆已用空间的分布图，Metaspace大小的分布图，最长暂停以及总暂停的直方分布图。

![](https://static001.geekbang.org/resource/image/56/0c/56f9fb2932ffb63ffa29e95dc779100c.png?wh=1920*1074)

即时编译子系统所对应的选项卡则展示了方法编译时间的直方图，以及按编译时间排序的编译任务表。

后者可能出现同方法名同方法描述符的编译任务。其原因主要有两个，一是不同编译层次的即时编译，如3层的C1编译以及4层的C2编译。二是去优化后的重新编译。

![](https://static001.geekbang.org/resource/image/6e/c8/6e7e41a6f8945a2b65d67c18ea5293c8.png?wh=1920*1070)

JMC的图表总体而言都不难理解。你可以逐个探索，我在这里便不详细展开了。

## 总结与实践

今天我介绍了两个GUI工具：eclipse MAT以及JMC。

eclipse MAT可用于分析由 `jmap` 命令导出的Java堆快照。它包括两个相对比较重要的视图，分别为直方图和支配树。直方图展示了各个类的实例数目以及这些实例的Shallow heap或Retained heap的总和。支配树则展示了快照中每个对象所直接支配的对象。

Java Mission Control是Java虚拟机平台上的性能监控工具。Java Flight Recorder是JMC的其中一个组件，能够以极低的性能开销收集Java虚拟机的性能数据。

JFR的启用方式有三种，分别为在命令行中使用 `-XX:StartFlightRecording=` 参数，使用 `jcmd` 的 `JFR.*` 子命令，以及JMC的JFR插件。JMC能够加载JFR的输出结果，并且生成各种信息丰富的图表。

* * *

今天的实践环节，请你试用JMC中的MBean Server功能，并通过JMC的帮助文档（ `Help->Java Mission Control Help`），以及 [该教程](https://docs.oracle.com/javase/tutorial/jmx/mbeans/index.html) 来了解该功能的具体含义。

![](https://static001.geekbang.org/resource/image/2a/7f/2a68f0f2b5de35f29b045fe82923ac7f.png?wh=1920*1072)

由于篇幅的限制，我就不再介绍 [VisualVM](https://visualvm.github.io/index.html) 以及 [JITWatch](https://github.com/AdoptOpenJDK/jitwatch) 了。感兴趣的同学可自行下载研究。