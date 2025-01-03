你好，我是海纳。

我们前面几节课主要是以Java为例，介绍了JVM中垃圾回收算法的演进过程。实际上，除了JVM之外，用于运行JavaScript的V8虚拟机、Lua虚拟机、Python虚拟机和Go的虚拟机都采用了自动内存管理技术。这节课，我们就一起来分析一下它们的实现。

通过这节课，你将会看到垃圾回收算法的设计是十分灵活而且多种多样的，这会为你以后改进应用中自动或半自动的内存管理，提供很好的参考。你要注意的是，学习自动内存管理，一定要抓住核心原理，不要陷入到细节里去。另外，你可以通过查看虚拟机源代码来验证自己的猜想，但不要把源代码教条化。

接下来，我先解释一下为什么选择Python和GO这两种语言做为例子。

## 静态语言和动态语言

我先介绍两个基本概念： **动态语言和静态语言**。动态语言的特征是可以在运行时，为对象甚至是类添加新的属性和方法，而静态语言不能在运行期间做这样的修改。

动态语言的代表是Python和JavaScript，静态语言的代表是C++。Java本质上是一门静态语言，但它又提供了反射（reflection）的能力为动态性开了一个小口子。

从实现的层面讲，静态语言往往在编译时就能确定各个属性的偏移值，所以编译器能确定某一种类型的对象，它的大小是多少。这就方便了在分配和运行时快速定位对象属性。关于静态语言的对象内存布局，我们在 [导学（三）](https://time.geekbang.org/column/article/431373) 和 [第19节课](https://time.geekbang.org/column/article/465516) 都做了介绍，你可以去看看。

而动态语言往往会将对象组织成一个字典结构，例如下面这个Python的例子：

```
>>> class A(object):
...  pass
...
>>> a = A()
>>> a.b = 1
>>> b = A()
>>> b.c = 2
>>> b.__dict__
{'c': 2}
>>> a.__dict__
{'b': 1}

```

你可以看到，类A的两个对象a和b，它们的属性是不相同的。这在Java语言中是很难想象的，但是在Python或者JavaScript中，却是司空见惯的操作。

**如果把上述代码中的a对象和b对象想象成一个字典的话，这段代码就不难理解了。第5行和第6行的操作不过是相当于在字典中添加了新的一个键值对而已。**

在了解了动态语言和静态语言的区别以后，我们就从动态语言中选择Python语言，从静态语言中选择Go语言，来对两种语言的实现加以解释。其中，Python语言的分配过程与 [第9节课](https://time.geekbang.org/column/article/440452) 所讲的malloc的实现非常相似，所以我们重点看它的垃圾回收过程。Go语言的垃圾回收过程就是简单的CMS，所以我们重点分析它的分配过程。下面，我们先从Python语言开始吧。

## Python 的内存管理机制

我们先从Python的对象布局讲起，以最简单的浮点数为例，在Include/floatobject.h中，python中的浮点数是这么定义的：

```
typedef struct {
    PyObject_HEAD
    double ob_fval;
} PyFloatObject;

```

我们继续查看PyObject\_HEAD的定义：

```
/* PyObject_HEAD defines the initial segment of every PyObject. */
#define PyObject_HEAD                   \
    _PyObject_HEAD_EXTRA                \
    Py_ssize_t ob_refcnt;               \
    struct _typeobject *ob_type;

```

这是一个宏定义，而其中的EXTRA在正常编译时是空的。所以，我们直接展开所有宏，那么PyFloatObject的定义就是这样子的：

```
typedef struct {
    Py_ssize_t ob_refcnt;
    struct _typeobject *ob_type;
    double ob_fval;
} PyFloatObject;

```

这样就很清楚了，ob\_refcnt就是引用计数，而ob\_fval是真正的值。例如我写一段这样的代码：

```
a = 1000.0
a = 2000.0

```

在执行第1句时，Python虚拟机真正执行的逻辑是创建一个PyFloatObject对象，然后使它的ob\_fval为1000.0，同时，它的引用计数为1；当执行到第2句时，创建一个值为2000.0的PyFloatObject对象，并且使这个对象的引用计数为1，而前一个对象的引用计数就要减1，从而变成0。那么前一个对象就会被回收。

在Python中，引用计数的维护是通过这两个宏来实现的：

```
#define Py_INCREF(op) (                         \
    _Py_INC_REFTOTAL  _Py_REF_DEBUG_COMMA       \
    ((PyObject*)(op))->ob_refcnt++)
#define Py_DECREF(op)                                   \
    do {                                                \
        if (_Py_DEC_REFTOTAL  _Py_REF_DEBUG_COMMA       \
        --((PyObject*)(op))->ob_refcnt != 0)            \
            _Py_CHECK_REFCNT(op)                        \
        else                                            \
        _Py_Dealloc((PyObject *)(op));                  \
    } while (0)

```

这两个宏位于Include/object.h中。这段代码里最重要的地方在于ob\_refcnt增一和减一的操作。这段代码与 [第19节课](https://time.geekbang.org/column/article/465516) 所讲的引用计数法的伪代码十分相似，我就不重复分析了。

使用了引用计数的地方，就会存在循环引用。例如下图中的四个对象，A是根对象，它与B之间有循环引用，那么它们都不是垃圾对象。C和D之间也有循环引用，但因为没有外界的引用指向它们了，所以它们就是垃圾对象，但是循环引用导致他们都不能释放。

![](https://static001.geekbang.org/resource/image/97/5f/97cc143f4d4216ba56ace93f1b8f7f5f.jpg?wh=2284x946)

Python为了解决这个问题，在虚拟机中引入了一个双向链表，把所有对象都放到这个链表里。Python的每个对象头上都有一个名为PyGC\_Head的结构：

```
/* GC information is stored BEFORE the object structure. */
typedef union _gc_head {
    struct {
        union _gc_head *gc_next;
        union _gc_head *gc_prev;
        Py_ssize_t gc_refs;
    } gc;
    long double dummy;  /* force worst-case alignment */
} PyGC_Head;

```

在这个结构里，gc\_next和gc\_prev的作用就是把对象关联到链表里。而gc\_refs则是用于消除循环引用的。当链表中的对象达到一定数目时，Python的GC模块就会执行一次标记清除。具体来讲，一共有四步。

第一步， **将ob\_refcnt的值复制到gc\_refs中**。对于上面的例子，它们的gc\_refs的值就如下图所示：

![](https://static001.geekbang.org/resource/image/52/49/524145acfebb39dc369c22fb3c36f649.jpg?wh=2284x896)

第二步是 **遍历整个链表，对每个对象，将它直接引用的对象的gc\_refs的值减一**。比如遍历到A对象时，只把B对象的gc\_refs值减一；遍历到B对象时，再把它直接引用的A对象的gc\_refs值减一。经过这一步骤后，四个对象的gc\_refs的值如下图所示：

![](https://static001.geekbang.org/resource/image/7d/c9/7d29ee40420ff42a0c6a77455e2f0cc9.jpg?wh=2284x896)

第三步， **将gc\_refs值为0的对象，从对象链表中摘下来，放入一个名为“临时不可达”的链表中**。之所以使用“临时”，是因为有循环引用的垃圾对象的gc\_refs在此时一定为0，比如C和D。但gc\_refs值为0的对象不一定是垃圾对象，比如B对象。此时，B、C和D对象就被放入临时不可达链表中了，示意图如下所示：

![](https://static001.geekbang.org/resource/image/38/69/3823754c6a23a3874f45547066fbd869.jpg?wh=2284x863)

最后一步， **以可达对象链表中的对象为根开始深度优先搜索**， **将所有访问到gc\_refs为0的对象，再从临时不可达链表中移回可达链表中**。最后留在临时不可达链表中的对象，就是真正的垃圾对象了。

接下来就可以使用\_Py\_Dealloc逐个释放链表中的对象了，对于上面的例子，就是把B对象重新加回到可达对象链表中，然后将C和D分别释放。

到这里，Python内存管理的核心知识我们就介绍完了，接下来，我们来看Go语言的例子。它的特点是分配算法复杂，但清除算法简单。

## Go语言的内存管理机制

Go语言采用的垃圾回收算法是 **并发标记清理**（Concurrent Mark Sweep，CMS）算法。CMS算法是Tracing GC算法中非常经典且朴素的例子，我们在前边的课程中讲了基于复制的GC算法和基于分区的GC算法，它们都在不同方面比CMS GC有优势，那为什么Go语言还是选择了CMS作为其GC算法呢？这里原因主要有两点：

**第一点是，Go语言通过内存分配策略缓解了CMS容易产生内存碎片的缺陷。**

相对于CMS GC，基于压缩的GC算法和基于复制的GC算法最大的优势是，能够降低内存的碎片率。这一点我们在前边的课程里已经充分讨论了。Go的GC算法采用TCMalloc分配器的内存分配思路，虽然不能像基于copy的GC算法那样消除掉内存碎片化的问题，但也极大地降低了碎片率。

另外，基于Thread Cache的分配机制可以使得Go在分配的大部分场景下避免加锁，这使得Go在高并发场景下能够发挥巨大的性能优势。

**第二点是，Go语言是有值类型数据的，即struct类型**。有了值类型的介入，编译器只需要关注函数内部的逃逸分析（intraprocedural escape analysis），而不用关注函数间的逃逸分析（interprocedural analysis），由此可以将生命周期很短的对象安排在栈上分配。

在前面的课程里，我们介绍了分代GC可以区分长生命周期和短生命周期对象，它的优势是能够快速回收生命周期短的对象。但由于逃逸分析的优势，Go语言中的短生命周期对象并没有那么多，所以分代GC在Go语言中收益较低。另外，由于分代GC需要额外的write barrier来维护老年代对年轻代的引用关系，也加重了GC引入的开销。

基于这两个主要原因，Go语言目前采用的GC算法是CMS算法。当然，Go语言在演进的过程中也曾采用过ROC和分代GC的算法，但后来也都放弃了。如果你对Go GC的演进过程感兴趣，可以看下 [《Getting to Go: The Journey of Go’s Garbage Collector》](https://go.dev/blog/ismmkeynote) 这篇文章。

在上面讲的第一点原因中，我们提到Go在CMS算法中，为了提高分配效率并且保障堆空间较低的碎片率，采用了TCMalloc的分配思想。所以，我们先来看一下TCMalloc的分配思想是怎样的，把握住TCMalloc的思想，你就能容易理解Go的分配机制了。

## TCMalloc的分配思想

在TCMalloc中，“TC”是Thread Cache的意思，其核心思想是： **TCMalloc会给每个线程分配一个Thread-Local Cache，对于每个线程的分配请求，就可以从自己的Thread-Local Cache区间来进行分配。此时因为不会涉及多线程操作，所以并不需要进行加锁，从而减少了因为锁竞争而引起的性能损耗。**

而当Thread-Local Cache空间不足的时候，才向下一级的内存管理器请求新的空间。TCMalloc引入了Thread cache、Central cache以及Page heap三个级别的管理器来管理内存，可以充分利用不同级别下的性能优势。这个时候你会发现，TCMalloc的多级管理机制非常类似计算机系统结构的内存多级缓存机制。

![](https://static001.geekbang.org/resource/image/45/a8/45883b243e08fb71fd6453f63d489da8.jpg?wh=2284x1310)

围绕着这个核心思想，我们具体看下Go的分配器是怎么实现的。在Go的内存管理机制中，有几个重要的数据结构需要关注，分别是 **mspan、heapArena、mcache、mcentral以及mheap**。其中，mspan和heapArena维护了Go的虚拟内存布局，而mcache、mcentral以及mheap则构成了Go的三层内存管理器。

### 虚拟内存布局

Go的内存管理基本单元是mspan，每个mspan中会维护着一块连续的虚拟内存空间，内存的起始地址由startAddr来记录。每个mspan存储的内存空间大小都是内存页的整数倍，由npages来保存。不过你需要注意的是，这里内存页并非是操作系统的物理页大小，Go的内存页大小设置的是8KB。mspan结构的部分定义如下：

```
type mspan struct {
    next *mspan     // next span in list, or nil if none
    prev *mspan     // previous span in list, or nil if none

    startAddr uintptr // address of first byte of span aka s.base()
    npages    uintptr // number of pages in span
    ...
    spanclass   spanClass     // size class and noscan (uint8)
    ...
}

```

![](https://static001.geekbang.org/resource/image/32/eb/323bc82131d5ba1675a8bd9d9ef53ceb.jpg?wh=2284x1290)

heapArena的结构相当于Go的一个内存块，在x86-64架构下的Linux系统上，一个heapArena维护的内存空间大小是64MB。该结构中存放了ArenaSize/PageSize 长度的mspan数组，heapArena结构的spans变量，用来精确管理每一个内存页。而整个arena内存空间的基址则存放在zeroedBase中。heapArena结构的部分定义如下：

```
type heapArena struct {
    ...
    spans [pagesPerArena]*mspan
    zeroedBase uintptr
}

```

有了这两个结构，我们就可以整体看下Go的虚拟内存布局了。Go整体的虚拟内存布局是存放在mheap中的一个heapArena的二维数组。定义如下：

```
arenas [1 << arenaL1Bits]*[1 << arenaL2Bits]*heapArena

```

这里二维数组的大小在不同架构跟操作系统上有所不同，对于x86-64架构下的Linux系统，第一维数组长度是1，而第二维数组长度是4194304。这样每个heapArena管理的内存大小是64MB，由此可以算出Go的整个堆空间最多可以管理256TB的大小。

![](https://static001.geekbang.org/resource/image/61/d6/6100a108e58e380b6635c7bb705a70d6.jpg?wh=2284x1110)

这里我们又会发现，Go通过heapArena来对虚拟内存进行管理的方式其实跟操作系统通过页表来管理物理内存是一样的。了解了Go的虚拟内存布局之后，我们再来看下Go的三级内存管理器。

### 三级内存管理

在Go的三级内存管理器中，维护的对象都是小于32KB的小对象。对于这些小对象，Go又将其按照大小分成了67个类别，称为spanClass。每一个spanClass都用来存储固定大小的对象。这67个spanClass的信息在runtime.sizeclasses.go中可以看到详细的说明。我选取了一部分注释放在了下面，你可以看看。

```
// class  bytes/obj  bytes/span  objects  tail waste  max waste  min align
//     1          8        8192     1024           0     87.50%          8
//     2         16        8192      512           0     43.75%         16
//     3         24        8192      341           8     29.24%          8
//     4         32        8192      256           0     21.88%         32
//    ...
//    67      32768       32768        1           0     12.50%       8192

```

对于上面的注释，我以class 3为例做个介绍。class 3是说在spanClass为3的span结构中，存储的对象的大小是24字节，整个span的大小是8192字节，也就是一个内存页的大小，可以存放的对象数目最多是341。

tail waste这里是8字节，这个8是通过8192 mod 24计算得到，意思是，当这个span填满了对象后，会有8字节大小的外部碎片。而max waste的计算方式则是$\\left\[ \\left( 24-17 \\right)\\times341+8\\right\]\\div8192$得到，意思是极端场景下，该span上分配的所有对象大小都是17字节，此时的内存浪费率为29.24%。

以上67个存储小对象的spanClass级别，再加上class为0时用来管理大于32KB对象的spanClass，共总是68个spanClass。这些数据都是通过在runtime.mksizeclasses.go中计算得到的。我们从上边的注释可以看出，Go在分配的时候，是通过控制每个spanClass场景下的最大浪费率，来保障堆内存在GC时的碎片率的。

![](https://static001.geekbang.org/resource/image/a2/26/a2466f262yy6886a4813f99b587cee26.jpg?wh=2284x1338)

另外，spanClass的ID中还会通过最后一位来存放noscan的属性。这个标志位是用来告诉Collector该span中是否需要扫描。如果当前span中并不存放任何堆上的指针，就意味着 **Collector不需要扫描这段span区间**。

```
func makeSpanClass(sizeclass uint8, noscan bool) spanClass {
    return spanClass(sizeclass<<1) | spanClass(bool2int(noscan))
}

func (sc spanClass) sizeclass() int8 {
    return int8(sc >> 1)
}

func (sc spanClass) noscan() bool {
    return sc&1 != 0
}

```

好了，接下来我们继续看下mcache的结构。mcache是Go的线程缓存，对应于TCMalloc中的Thread cache结构。mcache会与线程绑定，每个goroutine在向mcache申请内存时，都不会与其他goroutine发生竞争。mcache中会维护上述$68\\times2$种spanClass的mspan数组，存放在mcache的alloc中，包括scan以及noscan两个队列。mcache的主要结构如下，其中tiny相关的三个field涉及到tiny对象的分配，我们稍后在对象分配机制中再进行介绍。

```
type mcache struct {
    ...
    tiny       uintptr
    tinyoffset uintptr
    tinyAllocs uintptr

    alloc [numSpanClasses]*mspan // spans to allocate from, indexed by spanClass
    ...
}

```

![](https://static001.geekbang.org/resource/image/98/87/98a5961841b744615161dde97cbbf787.jpg?wh=2284x1279)

当mcache中的内存不够需要扩容时，需要向mcentral请求，mcentral对应于TCMalloc中的Central cache结构。mcentral的主要结构如下：

```
type mcentral struct {
    spanclass spanClass
    partial [2]spanSet // list of spans with a free object
    full    [2]spanSet // list of spans with no free objects
}

```

可以看到，mcentral中也存有spanClass的ID标识符，这表示说每个mcentral维护着固定一种spanClass的mspan。spanClass下面是两个spanSet，它们是mcentral维护的mspan集合。partial里存放的是包含着空闲空间的mspan集合，full里存放的是不包含空闲空间的span集合。这里每种集合都存放两个元素，用来 **区分集合中mspan是否被清理过**。

mcentral不同于mcache，每次请求mcentral中的mspan时，都可能发生不同线程直接的竞争。因此，在使用mcentral时需要进行加锁访问，具体来讲，就是spanSet的结构中会有一个mutex的锁的字段。

![](https://static001.geekbang.org/resource/image/4a/e0/4a1633500dba8f4923d3bbba9e6b97e0.jpg?wh=2284x1333)

我们最后看下mheap的结构。mheap在Go的运行时里边是只有一个实例的全局变量。上面我们讲到，维护Go的整个虚拟内存布局的heapArena的二维数组，就存放在mheap中。mheap结构对应于TCMalloc中的Page heap结构。mheap的主要结构如下：

```
type mheap struct {
    lock  mutex

    arenas [1 << arenaL1Bits]*[1 << arenaL2Bits]*heapArena
    central [numSpanClasses]struct {
        mcentral mcentral
        pad      [cpu.CacheLinePadSize - unsafe.Sizeof(mcentral{})%cpu.CacheLinePadSize]byte
    }
}

var mheap_ mheap

```

mheap中存放了$68\\times2$个不同spanClass的mcentral数组，分别区分了scan队列以及noscan队列。

到目前为止，我们就对Go的三级内存管理器有了一个整体的认识，下面这张图展示了这几个结构的关系。

![](https://static001.geekbang.org/resource/image/e4/75/e4e35deaffa0504a8aa9cd7955eec375.jpg?wh=2284x1402)

学习了Go的三级内存管理机制，那么Go的对象分配逻辑也就很清晰了。

### 对象分配机制

我们在这里需要注意的一点是：Go根据对象大小分成了三个级别，分别是微小对象、小对象和大对象。 **微小对象**，也就是指大小在0 ~ 16字节的非指针类型对象； **小对象**，指的是大小在16 ~ 32KB的对象以及小于16字节的指针对象； **大对象**，也就是上文提到的spanClass为0的类型。

对于这三种类型对象，Go的分配策略也不相同，对象分配的主要逻辑如下：

```
if size <= maxSmallSize {
    if noscan && size < maxTinySize {
      // 微小对象分配
    } else {
      // 小对象分配
    }
} else {
  // 大对象分配
}

```

微小对象会被放到spanClass为2的mspan中，由于每个对象最大是16字节，在分配时会尽量将多个小对象放到同一个内存块内（16字节），这样可以更进一步的降低这种微小对象带来的碎片化。

我们在mcache中提到的三个字段：tiny、tinyoffset和tinyAllocs就是用来维护微小对象分配器的。tiny是指向当前在使用的16字节内存块的地址，tinyoffset则是指新分配微小对象需要的起始偏移，tinyAllocs则存放了目前这个mcache中共存放了多少微小对象。

![](https://static001.geekbang.org/resource/image/4b/c3/4b04b0918e4963e1065f6913f73737c3.jpg?wh=2284x1387)

对于小对象的分配，整体逻辑跟TCMalloc是保持一致的，就是依次向三级内存管理器请求内存，一旦内存请求成功则返回，这里我就不详细展开了。

对于大对象的分配，Go并不会走上述的三次内存管理器，而是直接通过调用mcache.allocLarge来分配大内存。allocLarge会以内存页的倍数大小来通过mheap\_.alloc申请对应大小内存，并构建起spanClass为0的mspan对象返回。

好，接下来我们具体看下Go的内存回收器是怎么实现的。

## 内存回收机制

前面我们讲到，Go的GC算法采用的是经典的CMS算法，在并发标记的时候使用的是三色标记清除算法。而在write barrier上则采用了 **Dijkstra的插入barrier**，以及汤浅太一提出的删除 **barrier混合的barrier算法**。

另外，为了降低GC在回收时STW的最长时间，Go在内存回收时并不是一次性回收完全部的垃圾，而是采用增量回收的策略，将整个垃圾回收的过程切分成多个小的回收cycle。具体来讲，Go的内存回收主要分为这几个阶段：

1. **清除终止阶段；**

这个阶段会进行STW，让所有的线程都进入安全点。如果此次GC是被强制触发的话，那么这个阶段还需要清除上次GC尚未清除的mspan。

2. **标记阶段；**

在进行标记阶段之前，需要先做一些准备工作，也就是将gcphase状态从\_GCoff切换到\_GCmark，并打开write barrier和mutator assists，然后将根对象压入扫描队列中。此时，所有的mutator还处于STW状态。

准备就绪后重启mutator的运行，此时后台中的标记线程和mutator assists可以共同帮助GC进行标记。在标记过程中，write barrier会把所有被覆盖的指针以及新指针都标记为灰色，而新分配的对象指针则直接标记为黑色。

标记线程开始进行根对象扫描，包括所有的栈对象、全局变量的对象，还有所有堆外的运行时数据结构。这里你要注意的是，当对栈进行扫描的时候需要暂停当前的线程。扫描完根对象后，标记线程会继续扫描灰色队列中的对象，将对象标记为黑色并依次将其引用的对象标灰入队。

由于Go中每个线程都有一个Thread Local的cache，GC采用的是分布式终止算法来检查各个mcache中是否标记完成。

3. **标记终止阶段；**

在标记终止阶段会进行STW，暂停所有的线程。STW之后将gcphase的状态切换到\_GCmarktermination，并关闭标记进程和mutator assists。此外还会进行一些清理工作，刷新mcache。

4. **清除阶段。**

在开始清除阶段之前，GC会先将gcphase状态切换到\_GCoff，并关闭write barrier。接着再恢复用户线程执行，此时新分配的对象只会是白色状态。并且清除工作是增量是进行的，所以在分配时，也会在必要的情况下先进行内存的清理。这个阶段的内存清理工作会在后台并发完成。

## 总结

这节课做为自动内存管理的最后一节，同样也是我们专栏的最后一篇文章，我们通过两个具体的例子来展示了，实际场景中语言虚拟机是如何进行内存管理的。

首先，我们介绍了动态语言和静态语言的区别，并在动态语言中选择Python做为实例，在静态语言中选择Go做为实例进行介绍。

它们的数据结构和算法设计其实并没有超出我们之前课程所介绍的理论。只是在代码实现上，在细节上做了一些调整。

我们讲解了动态类型语言的内存布局，接着又分析了Python中的内存回收的具体实现。Python主要使用引用计数法进行内存管理。为了解决循环引用的问题，又引入了一种特殊的标记算法来释放垃圾对象。

在Go语言的内存管理机制中，我们详细学习了Go中内存分配的实现。Go语言通过采用TCMalloc的分配器思路，以及对内存对象类别大小的精确控制，保障了程序在运行过程中能够有高速的分配效率，以及维持较低的碎片率，这样回收器就可以采用相对简单的CMS算法。

到这里，我们就把自动内存管理的核心内容全部介绍完了。

## 思考题

如果你对Go语言比较熟悉的话，可以思考一下，Go语言中保留了值类型，有哪些优点和缺点呢？欢迎在留言区分享你的想法，我在留言区等你。

![](https://static001.geekbang.org/resource/image/f6/cb/f6c74dc0fcf052f32d46d8c952f939cb.jpg?wh=2284x1386)

好啦，这节课到这就结束啦。欢迎你把这节课分享给更多对计算机内存感兴趣的朋友。我是海纳，我们下节课再见！