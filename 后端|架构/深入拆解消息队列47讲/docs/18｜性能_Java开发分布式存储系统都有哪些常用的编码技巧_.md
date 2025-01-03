你好，我是文强。

到了这节课，我们的课程已经讲完三分之一了。前面我们讲了消息队列各个模块的设计、权衡、思考、选型，基本覆盖了基础核心架构中的所有细节了。

我一直认为，架构设计选型和编码是两个事情，魔鬼在细节，不管多牛逼的架构，都需要细致的工程化实现，才能达到我们预期的效果。这节课我们将用很零散的方式讲一下用 Java 来开发存储系统时会用到的一些技巧及其背后的原理。其中的每个知识点都是独立的，你可以挑自己感兴趣的部分学习。

## PageCache 调优和 Direct IO

我们一直会听到PageCache，简单理解它就是内存。写内存性能肯定是最高的。但是PageCache 并不是万能的，在某些情况下会存在命中率低，导致读写性能不高的情况。遇到这种情况，就需要在业务上进行处理。我们先来看下面这张图：

![](https://static001.geekbang.org/resource/image/58/80/586ac52baff5c8c9e6644da62d962f80.jpg?wh=10666x4844)

如上图所示，应用程序读取文件，会经过应用缓存、PageCache、DISK（硬盘）三层。即应用程序读取文件时，Linux 内核会把从硬盘中读取的文件页面缓存在内存一段时间，这个文件缓存被称为 PageCache。

**缓存的核心逻辑是：** 比如应用层要读1KB文件，那么内核的预读算法则会以它认为更合适的大小进行预读 I/O，比如 16-128KB。当应用程序下次读数据的时候，会先尝试读PageCache，如果数据在PageCache中，就会直接返回；如果数据不在PageCache中，就会触发从硬盘读取数据，效率就会变低。

这种预读机制，在顺序读的时候，性能会很高，因为已经预先加载了。但是有以下三种情况，PageCache无法起作用。

1. 使用 FIleChannel 读写时，底层可能走 Direct IO，不走页缓存。
2. 在内存有限或者不够用的时候，频繁换页，导致缓存命中率低。
3. 大量随机读的场景，导致页缓存的数据无法命中。

为了解决上面这类PageCache无法起作用的场景，有一种解决思路是： **通过使用** **Direct IO 来模拟实现** **PageCahce** **的效果。** 原先内核提供的 PageCache 的底层实现（比如数据加载、缓存命中、换页、刷盘等）是由操作系统来控制的，我们无法灵活控制，因此导致在一些场景中无法满足要求。

那么新的思路是：可以绕过操作系统，直接使用通过自定义Cache + Direct IO来实现更细致、自定义的管理内存、命中和换页等操作，从而针对我们的业务场景来优化缓存策略，从而实现比PageCache更好的效果。从技术实现上看，它和我们使用C++ 管理内存编程是一样的效果。

解决思路来看下图：

![](https://static001.geekbang.org/resource/image/d8/19/d86190bb6cfe6f3c0ba882335b71b219.jpg?wh=10666x6000)

通过前面所学我们知道，NIO 中的 FileChannel 主要和ByteBuffer打交道，mmap直接和缓存打交道，而 Direct IO直接和硬盘打交道。即Direct IO是直接操作硬盘中的数据的，不经过应用缓存和页缓存。

那么这个思路的核心实现就是： **通过自定义 Cache 管理、缓存加载、换页等行为，让这些策略可以满足当前业务和场景的需求** **。** 比如在随机读或者内存不够的场景下，提高页缓存的命中率。

在Java 中，Direct IO 可以通过 JNA/JNI 调用 Native 方法实来实现。GitHub上有封装好了Java JNA 库，实现了 Java 的 Direct IO，直接就可以使用。有兴趣的话，你可以去研究一下这个GitHub项目： [https://github.com/smacke/jaydio](https://github.com/smacke/jaydio)。

## FileChannel 和 mmap

Java 原生的 IO 主要可以分为普通 IO、FileChannel（文件通道）、mmap（内存映射）三种。

其中，java.io 包中的 FileWriter 和 FileReader 属于普通 IO；java.nio 包中的 FileChannel 属于 NIO 的一种；mmap 是调用 FileChannel.map() 实例出来的一种特殊读写文件的方式，被称为内存映射。基于字节传输的传统 IO 基本很少用了，当前主要使用 FileChannel 和 mmap。

先来看一下FileChannel，它的基本使用方式如下：

```plain
FileChannel fileChannel = new RandomAccessFile(new File("test.data"), "rw").getChannel();

// 写数据
byte[] data = new byte[1024];
long position = 10L;
fileChannel.write(ByteBuffer.wrap(data)); //当前位置写入数据
fileChannel.write(ByteBuffer.wrap(data), position); //指定位置写入数据

// 读数据
ByteBuffer buffer = ByteBuffer.allocate(1024);
long position = 10L;
fileChannel.read(buffer); // 当前位置读取1024byte的数据
fileChannel.read(buffer,position)； // 指定位置读取 1024byte 的数据

```

从技术上看， **FileChannel 大多数时候是和 ByteBuffer 打交道的**，你可以将ByteBuffer理解为一个 byte\[\] 的封装类。ByteBuffer 是在应用内存中的，它和硬盘之间还隔着一层 PageCache。

如下图所示，即FileChannel 写的时候经历了应用内存 -> PageCache -> 磁盘三个步骤。

![](https://static001.geekbang.org/resource/image/2e/b6/2e4c7986069cb2f423bd02ce2ef640b6.jpg?wh=10666x6000)

从使用上看，我们通过 filechannel.write 写入数据时，会将数据从应用内存写入到PageCache，此时便认为完成了落盘操作。但实际上，操作系统最终帮我们将 PageCache 的数据自动刷到了硬盘。这也是 FileChannel 提供了一个 force() 方法来通知操作系统进行及时刷盘的原因。

接着我们来看一下 mmap，先看一下它的基本使用方式：

```plain
MappedByteBuffer mappedByteBuffer = fileChannel.map(FileChannel.MapMode.READ_WRITE, 0, filechannel.size();

byte[] data = new byte[1024];
int position = 10;

// 从当前位置写入1kb的数据
mappedByteBuffer.put(data);

// 从指定位置写入1kb的数据
MappedByteBuffer subBuffer = mappedByteBuffer.slice();
subBuffer.position(position);
subBuffer.put(data);

```

mmap 是一个把文件映射到内存的操作，因此可以像读写内存一样读写文件。它省去了用户空间到内核空间的数据复制过程，从而提高了读写性能。

如下图所示，mmap的写入也是先把数据写入到PageCache，不是直接把数据写到硬盘中。它的底层借助了内存来加速，即 MappedByteBuffer 的 put 实际是对内存进行操作。具体刷盘依赖操作系统定时刷盘或者手动调用 mappedByteBuffer.force() 刷盘。

![](https://static001.geekbang.org/resource/image/f4/c0/f4e05ebbfc34a7d38b0a9c4b332f39c0.jpg?wh=10666x6000)

从经验来看，mmap 在内存充足、数据文件较小且相对固定的场景下，性能比 FileChannel 高。 **但它有这样几个缺点：**

1. 使用时必须先指定好内存映射的大小，并且一次 Map 的大小限制在 1.5G 左右。
2. 是由操作系统来刷盘的，手动刷盘时间不好掌握。
3. 回收非常复杂，需要手动释放，并且代码和实现很复杂。

实际使用中，在消息队列数据文件分段的场景下，因为每个段文件的大小是固定的，且大小还是可配置的，所以是可以使用 mmap 来提高性能的。在 RocketMQ 的源码中，我们可以看到 NIO 和 mmap 都有在使用，但是主要的写是通过 mmap 来完成的。

不过在大部分情况下，我认为FileChannel 完全可以胜任 IO 工作。所以在写文件中，我推荐你优先考虑FileChannel。在一些数据量小、内存充足的场景下，再换成 mmap 来实现。

## 预分配文件、预初始化、池化

在提高文件写入性能的时候，预分配文件是一个简单实用的优化技巧。比如前面讲过，消息队列的数据文件都是需要分段的，所以在创建分段文件的时候，可以预先写入空数据（比如0）将文件预分配好。此时当我们真正写入业务数据的时候，速度就会快很多。

下面是一个预分配文件的代码示例：

```plain
public void allocate(FileChannel fileChannel,
long preFileSize) throw IOException{
    int bufferSize = 1024;
    ByteBuffer byteBuffer = ByteBuffer.allocateDirect(bufferSize);
    for (int i = 0; i < bufferSize; i++) {
        byteBuffer.put((byte)0);
    }
    byteBuffer.flip();
    long loop = preFileSize / bufferSize;
    for (long i = 0; i < loop; i++) {
        fileChannel.write(byteBuffer);
        byteBuffer.flip();
    }
    fileChannel.force(true);
    fileChannel.position(0);
}

```

另外，对一些需要重复用到的对象或者实例化成本较高的对象 **进行预初始化**，可以降低核心流程的资源开销。

还一点就是对象池化，对象池化是指只要是需要反复 new 出来的东西都可以池化，以避免内存分配后再回收，造成额外的开销。Netty 中的 Recycler、RingBuffer 中预先分配的对象都是按照这个池化的思路来实现的。

## 直接内存（堆外）和堆内内存

想必这个概念你已经很熟悉了。如下图所示，堆内和堆外的堆是指 JVM 堆，堆内内存就是指JVM堆内部的内存空间，堆外就是指除了JVM堆以外的内存空间。堆内内存加上堆外内存等于总内存。

![](https://static001.geekbang.org/resource/image/4a/8f/4a3c99e3f26992da898eac1788b9a88f.jpg?wh=10666x6000)

虽然概念熟悉，但你知道什么时候使用堆内内存，什么时候使用堆外内存吗?

**关于堆内内存和堆外内存的选择，我有下面五点建议：**

1. 当需要申请大块的内存时，堆内内存会受到限制，可以尝试分配堆外内存。
2. 堆外内存适用于生命周期中等或较长的对象。
3. 堆内内存刷盘的过程中，还需要复制一份到堆外内存，多了一步，会降低性能。
4. 创建堆外内存的消耗要大于创建堆内内存的消耗，所以当分配了堆外内存之后，要尽可能复用它。
5. 可以使用池化+堆外内存的组合方式。比如代码中如果需要频繁new byte\[\]，就可以研究一下ThreadLocal<ByteBuffer>和ThreadLocal<byte\[\]>的使用机制。

如果用 Java 写存储系统（比如消息队列），我会建议你尽量优先考虑是否可以用堆外内存。

## 同步刷盘

不管是在使用NIO还是mmap，都是需要先操作缓存，然后依赖操作系统去刷盘或者手动刷盘。如果依赖操作系统刷盘，在一些极端场景可能会出现数据丢失。而如果每次写入都强制刷盘，就会导致性能下降厉害。

所以我们在之前的课程中讲过，多数消息队列会提供同步刷盘和异步刷盘两种机制给用户选择，用户可以根据不同场景来选择不同的策略。这种方案是把数据的可靠性选择交给用户，如果为了更高的性能，那就选择异步刷盘，如果选择可靠性，就同步刷盘，接受性能下降。

那有办法提高同步刷盘的性能吗？你的直觉是不是只能通过更高性能的硬盘，比如SSD、NVMe，或者AEP这种性能更高的存储介质了。除了存储介质外，有没有其他的解法呢？

从应用程序的角度来看，可以通过批量同步刷盘的操作来提高性能。批量同步刷盘的核心思路是： **每次刷盘尽量刷更多的数据到硬盘上**。技术上是指通过收集多线程写过来的数据，汇总起来批量同步刷到硬盘中，从而提高数据同步刷盘的性能。

我们来看一下具体的实现思路，来看下图：

![](https://static001.geekbang.org/resource/image/f2/b7/f22cf752b7a1876f42813dc5b58902b7.jpg?wh=10666x6000)

业务线程 T1 到 T6 的数据通过内存将数据发送给IO 线程。然后业务线程进入await 状态，当 IO Thread 收集到一定的数据后，再一起将数据同步刷到硬盘中。最后唤醒T1到T6线程，返回写入成功。

**这个方案和** **PageCache** **写入的最大区别在于：** fileChannel.write() 只要写 PageCache 成功就会直接返回，后续的刷盘动作交给操作系统去执行，在客户端看来数据已经写入成功了，但是底层却没有写入成功。而新方案中写入线程是可以感知到刷盘的结果的，当同步刷盘失败，则 IO 线程会通知业务线程写入失败，业务线程就会进行重试或给客户端返回失败。

我们在基础篇的网络模块中讲过，在消息队列系统中，客户端都是由多个生产者写入的，服务端会通过React模型配合后端 Process 线程池来处理请求。此时 Broker 接收到数据后，会分发给多个Process线程处理，当Process线程处理完数据后，如果需要同步刷盘，就可以使用上面这种优化方案来提高性能。

另外，在主流的消息队列中，为了避免同步刷盘，常用的方案是 **通过多副本机制来实现数据的高可靠**。如下图所示，数据会写入到多个副本中，每个副本只写入到本节点的PageCache，然后就返回成功。因为多台节点同时挂掉的概率很低，所以消息丢失的概率也就很低了。

![](https://static001.geekbang.org/resource/image/27/ba/270e2464868e6cb0a10cacdf2d1820ba.jpg?wh=10666x6000)

## 新的存储 AEP

我们来看看什么是AEP，这部分相当于一个科普吧。我们在选用硬盘的时候，经常会听到SSD、SATA、NVMe 等存储介质。因为在传统存储系统中，我们通常采用机械盘或SSD作为后端存储系统的缓存。

随着存储技术的发展，Intel 推出了基于 3D Xpoint 技术的新型存储介质傲腾内存（AEP）。相比普通内存，AEP 拥有有大容量、非易失的特点，相当于大容量的持久化的内存。

从使用上看，由于它的使用方式和普通内存不一样，并且成本较高，导致它没有被大规模应用。但是作为一个存储介质，它的优点就是快， **速度比** **SSD 快出 1~n 个数量级**。

所以在一些追求极限性能的场景中，比如某些金融级的消息队列，此时应用程序已经无法再提升性能了，就得依靠更好的硬件来提高性能，这时候我们就可以选择AEP作为存储介质。

## 线程绑核

在消息队列的进程中，负责各种功能的线程很多，比如处理请求、处理IO、清理数据等等，此时就会有CPU争用和线程切换的情况。频繁的线程切换会导致性能下降，而 IO 线程占用的资源和时间较多，切换成本较高。

所以在一些追求性能和隔离性的场景中，我们可以通过线程绑核的操作来实现更好的性能。比如在一些重IO的操作中，留几个核心专门给 IO 线程使用，这样就可以完全避免 IO 线程的时间片争用。

在 Java 中实现绑核操作，可以通过这个项目来实现： [https://github.com/OpenHFT/Java-Thread-Affinity](https://github.com/OpenHFT/Java-Thread-Affinity)。

使用的代码 demo 如下所示：

```plain
// lock one of the last CPUs
try (AffinityLock lock = AffinityLock.acquireLockLastMinus(n)) {

}

```

## SSD 的 4KB 对齐

SSD 4KB 对齐指的将 SSD 盘的物理扇区和逻辑扇区对齐，从而提高 SSD 盘读写性能的一种技巧，是 SSD 盘经典的优化技巧。

**底层大致的原理是** **：** 如果读取一次数据，要跨多个物理扇区，那么性能就会下降；如果每次读取刚刚好是读一个物理扇区的数据，那么性能就会很高。我在网上找了两张图来说明一下效果。

![图片](https://static001.geekbang.org/resource/image/9b/f4/9b7c49bb5527974b4733c93c9e65e4f4.png?wh=667x90)![](https://static001.geekbang.org/resource/image/30/5f/30cf525c0acae5c8fcb14f496635705f.png?wh=668x98)

可以看到，如果读取的刚好是一个物理扇区，那么就不需要跨物理扇区读，读取性能就会更高。当然，这块的细节很多，你如果有兴趣的话可以深入去研究下，这里只是点一下，让你知道有这么个东西。

基于这个理论，我们在使用SSD的时候，如果追求性能，并且场景合适，可以使用这个技巧来提高性能。但是在实际系统中，特别是在消息系统，因为用户的消息的大小是动态变化的，消息基本不可能是4KB的整数倍。所以如果强制要求4KB对齐，就需要进行空数据填充，当消息量多的时候，填充行为可能会导致额外的硬盘空间浪费。

## 其他一些优化手段

接下来我继续分享几个常用的优化手段。

### JVM 调优

从结果来看，JVM 调优是提高性能的一个重要操作。在消息系统中，我们需要尽量降低GC的次数，避免Full GC 和 STW 等。实际操作中，可以通过调整年轻代堆的大小、比例以及选择合适的垃圾回收算法等方式来优化。这里就不展开了，这块的资料非常丰富。

### 减少线程切换

我们经常听到进程、线程、协程这几个概念。从切换成本来看，进程最高，协程最低。目前主流Java 版本不支持协程，最新的JDK 19 才开始支持协程。所以当前用得最多的就是线程。

在一些追求高性能的场景中，线程切换也会影响性能。所以在实际的开发中，需要关注线程切换的次数。为了减少线程切换的次数，一般有这样几个建议：

1. 减少锁的持有时间。
2. 降低锁的粒度，锁分离、锁分段。
3. 乐观锁代替竞争锁，CAS 代替 Synchronized。
4. Condition await 替换 Object wait，Condition signal 替换 Object notify，Condition signalAll 替换 Object notifyAll，整体上解决提前唤醒和无法做到区分唤醒的问题。
5. 合理地设置线程池中的线程数。

### Unsafe

sun.misc.Unsafe 是 JDK 提供的原生工具类，它可以在Java 中实现内存分配与回收、CAS、类实例化、内存屏障等等操作。跟C/C++一样，它可以在Java中直接操作内存，执行底层系统调用。

它的好处就是灵活，像 C++ 一样使用Java。缺点就是 Unsafe 是一个不安全的操作，在JDK 8中可以使用，但是从 JDK 9 开始非标准库的模块都无法访问到它了。

在存储系统开发中，在某些场景下，如果需要更细致地操作内存，就可以考虑它。

### 其他知识点

1. 顺序读比随机读快，顺序写比随机写快。
2. 合并写入比单独写入快。
3. 在某些场景下，比如数据的集合长度是固定的时候，可以考虑数组替代或者重写 Map，用来降低 HashMap 的 overheap。
4. 文件分段。

## 总结

这节课我们总结了一些用Java 开发存储系统时经常会用到的技巧。在我的经验中，我认为在大的设计框架差别不大的情况下，性能差异很多就是因为这些不起眼的细节。这节课我们主要讲的是IO相关的优化操作，主要是因为消息队列本身就是一个重IO的存储系统，IO模块的性能提升是整个系统性能提升的关键。

Java IO 性能核心还是缓存、批量写和异步刷盘。从使用的角度，基本只要关注FileChannel、mmap 即可。在一些极限场景下，可以关注一下Direct IO的使用。同步刷盘并不是噩梦，可以通过一些代码上的优化，来提高同步刷盘的能力。

在某些场景，预分配文件和初始化一些资源可以带来意料之外的性能提升。在内存的使用上，建议多关注一下对外内存的使用。新的硬盘介质、线程绑核、4KB对齐、减少线程切换、Unsafe的使用等等这些技巧，最好也都了解下，有一个全局的视角，在某些场景下都会用到。

另外，编码技巧还有很重要的一部分是计算逻辑层面的优化技巧，如果有兴趣，你可以自行去研究下，也可以留言与我讨论。

## 思考题

你还知道有哪些提高性能的编码技巧吗？比如在 Java 逻辑处理方面。

欢迎分享你的思考，如果觉得有收获，也欢迎你把这节课分享给身边的朋友。我们下节课再见！

## 上节课思考闭环

RabbitMQ 的 Queue 在镜像模式下的一致性模型和可靠性是怎样的？

RabbitMQ 是通过配置镜像队列的机制来实现多副本的，数据可靠性的核心是多副本和一致性复制策略。多副本之间的数据同步，是通过同步复制、Leader推送模型来实现的。

从实现上来看，RabbitMQ的镜像模式基于主从架构的模型。镜像队列是在 Queue 的维度配置的，共有 All、Exactly、Node 三种策略。其中，All 是指强一致；Exactly 是允许指定同步的副本数，这和多数策略很像，属于最终一致；Node 可以指定数据需要固定同步的节点列表，严格意义来说也是强一致，因为被选中的节点都需要写入数据才算数据保存成功。从实现上看，在RabbitMQ的镜像模式中，不支持弱一致的一致性策略。