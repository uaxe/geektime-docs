在今天这一讲中，我来分析一下并发包内部的组成，一起来看看各种同步结构、线程池等，是基于什么原理来设计和实现的。

今天我要问你的问题是，AtomicInteger底层实现原理是什么？如何在自己的产品代码中应用CAS操作？

## 典型回答

AtomicIntger是对int类型的一个封装，提供原子性的访问和更新操作，其原子性操作的实现是基于CAS（ [compare-and-swap](https://en.wikipedia.org/wiki/Compare-and-swap)）技术。

所谓CAS，表征的是一系列操作的集合，获取当前数值，进行一些运算，利用CAS指令试图进行更新。如果当前数值未变，代表没有其他线程进行并发修改，则成功更新。否则，可能出现不同的选择，要么进行重试，要么就返回一个成功或者失败的结果。

从AtomicInteger的内部属性可以看出，它依赖于Unsafe提供的一些底层能力，进行底层操作；以volatile的value字段，记录数值，以保证可见性。

```
private static final jdk.internal.misc.Unsafe U = jdk.internal.misc.Unsafe.getUnsafe();
private static final long VALUE = U.objectFieldOffset(AtomicInteger.class, "value");
private volatile int value;

```

具体的原子操作细节，可以参考任意一个原子更新方法，比如下面的getAndIncrement。

Unsafe会利用value字段的内存地址偏移，直接完成操作。

```
public final int getAndIncrement() {
    return U.getAndAddInt(this, VALUE, 1);
}

```

因为getAndIncrement需要返归数值，所以需要添加失败重试逻辑。

```
public final int getAndAddInt(Object o, long offset, int delta) {
    int v;
    do {
        v = getIntVolatile(o, offset);
    } while (!weakCompareAndSetInt(o, offset, v, v + delta));
    return v;
}

```

而类似compareAndSet这种返回boolean类型的函数，因为其返回值表现的就是成功与否，所以不需要重试。

```
public final boolean compareAndSet(int expectedValue, int newValue)

```

CAS是Java并发中所谓lock-free机制的基础。

## 考点分析

今天的问题有点偏向于Java并发机制的底层了，虽然我们在开发中未必会涉及CAS的实现层面，但是理解其机制，掌握如何在Java中运用该技术，还是十分有必要的，尤其是这也是个并发编程的面试热点。

有的同学反馈面试官会问CAS更加底层是如何实现的，这依赖于CPU提供的特定指令，具体根据体系结构的不同还存在着明显区别。比如，x86 CPU提供cmpxchg指令；而在精简指令集的体系架构中，则通常是靠一对儿指令（如“load and reserve”和“store conditional”）实现的，在大多数处理器上CAS都是个非常轻量级的操作，这也是其优势所在。

大部分情况下，掌握到这个程度也就够用了，我认为没有必要让每个Java工程师都去了解到指令级别，我们进行抽象、分工就是为了让不同层面的开发者在开发中，可以尽量屏蔽不相关的细节。

如果我作为面试官，很有可能深入考察这些方向：

- 在什么场景下，可以采用CAS技术，调用Unsafe毕竟不是大多数场景的最好选择，有没有更加推荐的方式呢？毕竟我们掌握一个技术，cool不是目的，更不是为了应付面试，我们还是希望能在实际产品中有价值。

- 对ReentrantLock、CyclicBarrier等并发结构底层的实现技术的理解。


## 知识扩展

关于CAS的使用，你可以设想这样一个场景：在数据库产品中，为保证索引的一致性，一个常见的选择是，保证只有一个线程能够排他性地修改一个索引分区，如何在数据库抽象层面实现呢？

可以考虑为索引分区对象添加一个逻辑上的锁，例如，以当前独占的线程ID作为锁的数值，然后通过原子操作设置lock数值，来实现加锁和释放锁，伪代码如下：

```
public class AtomicBTreePartition {
private volatile long lock;
public void acquireLock(){}
public void releaseeLock(){}
}

```

那么在Java代码中，我们怎么实现锁操作呢？Unsafe似乎不是个好的选择，例如，我就注意到类似Cassandra等产品，因为Java 9中移除了Unsafe.moniterEnter()/moniterExit()，导致无法平滑升级到新的JDK版本。目前Java提供了两种公共API，可以实现这种CAS操作，比如使用java.util.concurrent.atomic.AtomicLongFieldUpdater，它是基于反射机制创建，我们需要保证类型和字段名称正确。

```
private static final AtomicLongFieldUpdater<AtomicBTreePartition> lockFieldUpdater =
        AtomicLongFieldUpdater.newUpdater(AtomicBTreePartition.class, "lock");

private void acquireLock(){
    long t = Thread.currentThread().getId();
    while (!lockFieldUpdater.compareAndSet(this, 0L, t)){
        // 等待一会儿，数据库操作可能比较慢
         …
    }
}

```

[Atomic包](https://docs.oracle.com/javase/9/docs/api/java/util/concurrent/atomic/package-summary.html) 提供了最常用的原子性数据类型，甚至是引用、数组等相关原子类型和更新操作工具，是很多线程安全程序的首选。

我在专栏第七讲中曾介绍使用原子数据类型和Atomic\*FieldUpdater，创建更加紧凑的计数器实现，以替代AtomicLong。优化永远是针对特定需求、特定目的，我这里的侧重点是介绍可能的思路，具体还是要看需求。如果仅仅创建一两个对象，其实完全没有必要进行前面的优化，但是如果对象成千上万或者更多，就要考虑紧凑性的影响了。而atomic包提供的 [LongAdder](https://docs.oracle.com/javase/9/docs/api/java/util/concurrent/atomic/LongAdder.html)，在高度竞争环境下，可能就是比AtomicLong更佳的选择，尽管它的本质是空间换时间。

回归正题，如果是Java 9以后，我们完全可以采用另外一种方式实现，也就是Variable Handle API，这是源自于 [JEP 193](http://openjdk.java.net/jeps/193)，提供了各种粒度的原子或者有序性的操作等。我将前面的代码修改为如下实现：

```
private static final VarHandle HANDLE = MethodHandles.lookup().findStaticVarHandle
        (AtomicBTreePartition.class, "lock");

private void acquireLock(){
    long t = Thread.currentThread().getId();
    while (!HANDLE.compareAndSet(this, 0L, t)){
        // 等待一会儿，数据库操作可能比较慢
        …
    }
}

```

过程非常直观，首先，获取相应的变量句柄，然后直接调用其提供的CAS方法。

一般来说，我们进行的类似CAS操作，可以并且推荐使用Variable Handle API去实现，其提供了精细粒度的公共底层API。我这里强调公共，是因为其API不会像内部API那样，发生不可预测的修改，这一点提供了对于未来产品维护和升级的基础保障，坦白说，很多额外工作量，都是源于我们使用了Hack而非Solution的方式解决问题。

CAS也并不是没有副作用，试想，其常用的失败重试机制，隐含着一个假设，即竞争情况是短暂的。大多数应用场景中，确实大部分重试只会发生一次就获得了成功，但是总是有意外情况，所以在有需要的时候，还是要考虑限制自旋的次数，以免过度消耗CPU。

另外一个就是著名的 [ABA](https://en.wikipedia.org/wiki/ABA_problem) 问题，这是通常只在lock-free算法下暴露的问题。我前面说过CAS是在更新时比较前值，如果对方只是恰好相同，例如期间发生了 A -> B -> A的更新，仅仅判断数值是A，可能导致不合理的修改操作。针对这种情况，Java提供了AtomicStampedReference工具类，通过为引用建立类似版本号（stamp）的方式，来保证CAS的正确性，具体用法请参考这里的 [介绍](http://tutorials.jenkov.com/java-util-concurrent/atomicstampedreference.html)。

前面介绍了CAS的场景与实现，幸运的是，大多数情况下，Java开发者并不需要直接利用CAS代码去实现线程安全容器等，更多是通过并发包等间接享受到lock-free机制在扩展性上的好处。

下面我来介绍一下AbstractQueuedSynchronizer（AQS），其是Java并发包中，实现各种同步结构和部分其他组成单元（如线程池中的Worker）的基础。

学习AQS，如果上来就去看它的一系列方法（下图所示），很有可能把自己看晕，这种似懂非懂的状态也没有太大的实践意义。

![](https://static001.geekbang.org/resource/image/e3/36/e3b4b7fe5a94a88ca2feb04d734b9c36.png?wh=1062*424)

我建议的思路是，尽量简化一下，理解为什么需要AQS，如何使用AQS， **至少** 要做什么，再进一步结合JDK源代码中的实践，理解AQS的原理与应用。

[Doug Lea](https://en.wikipedia.org/wiki/Doug_Lea) 曾经介绍过AQS的设计初衷。从原理上，一种同步结构往往是可以利用其他的结构实现的，例如我在专栏第19讲中提到过可以使用Semaphore实现互斥锁。但是，对某种同步结构的倾向，会导致复杂、晦涩的实现逻辑，所以，他选择了将基础的同步相关操作抽象在AbstractQueuedSynchronizer中，利用AQS为我们构建同步结构提供了范本。

AQS内部数据和方法，可以简单拆分为：

- 一个volatile的整数成员表征状态，同时提供了setState和getState方法

```
private volatile int state;

```

- 一个先入先出（FIFO）的等待线程队列，以实现多线程间竞争和等待，这是AQS机制的核心之一。

- 各种基于CAS的基础操作方法，以及各种期望具体同步结构去实现的acquire/release方法。


利用AQS实现一个同步结构，至少要实现两个基本类型的方法，分别是acquire操作，获取资源的独占权；还有就是release操作，释放对某个资源的独占。

以ReentrantLock为例，它内部通过扩展AQS实现了Sync类型，以AQS的state来反映锁的持有情况。

```
private final Sync sync;
abstract static class Sync extends AbstractQueuedSynchronizer { …}

```

下面是ReentrantLock对应acquire和release操作，如果是CountDownLatch则可以看作是await()/countDown()，具体实现也有区别。

```
public void lock() {
    sync.acquire(1);
}
public void unlock() {
    sync.release(1);
}

```

排除掉一些细节，整体地分析acquire方法逻辑，其直接实现是在AQS内部，调用了tryAcquire和acquireQueued，这是两个需要搞清楚的基本部分。

```
public final void acquire(int arg) {
    if (!tryAcquire(arg) &&
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
        selfInterrupt();
}

```

首先，我们来看看tryAcquire。在ReentrantLock中，tryAcquire逻辑实现在NonfairSync和FairSync中，分别提供了进一步的非公平或公平性方法，而AQS内部tryAcquire仅仅是个接近未实现的方法（直接抛异常），这是留个实现者自己定义的操作。

我们可以看到公平性在ReentrantLock构建时如何指定的，具体如下：

```
public ReentrantLock() {
        sync = new NonfairSync(); // 默认是非公平的
    }
    public ReentrantLock(boolean fair) {
        sync = fair ? new FairSync() : new NonfairSync();
    }

```

以非公平的tryAcquire为例，其内部实现了如何配合状态与CAS获取锁，注意，对比公平版本的tryAcquire，它在锁无人占有时，并不检查是否有其他等待者，这里体现了非公平的语义。

```
final boolean nonfairTryAcquire(int acquires) {
    final Thread current = Thread.currentThread();
    int c = getState();// 获取当前AQS内部状态量
    if (c == 0) { // 0表示无人占有，则直接用CAS修改状态位，
    	if (compareAndSetState(0, acquires)) {// 不检查排队情况，直接争抢
        	setExclusiveOwnerThread(current);  //并设置当前线程独占锁
        	return true;
    	}
    } else if (current == getExclusiveOwnerThread()) { //即使状态不是0，也可能当前线程是锁持有者，因为这是再入锁
    	int nextc = c + acquires;
    	if (nextc < 0) // overflow
        	throw new Error("Maximum lock count exceeded");
    	setState(nextc);
    	return true;
	}
	return false;
}

```

接下来我再来分析acquireQueued，如果前面的tryAcquire失败，代表着锁争抢失败，进入排队竞争阶段。这里就是我们所说的，利用FIFO队列，实现线程间对锁的竞争的部分，算是是AQS的核心逻辑。

当前线程会被包装成为一个排他模式的节点（EXCLUSIVE），通过addWaiter方法添加到队列中。acquireQueued的逻辑，简要来说，就是如果当前节点的前面是头节点，则试图获取锁，一切顺利则成为新的头节点；否则，有必要则等待，具体处理逻辑请参考我添加的注释。

```
final boolean acquireQueued(final Node node, int arg) {
      boolean interrupted = false;
      try {
    	for (;;) {// 循环
        	final Node p = node.predecessor();// 获取前一个节点
        	if (p == head && tryAcquire(arg)) { // 如果前一个节点是头结点，表示当前节点合适去tryAcquire
            	setHead(node); // acquire成功，则设置新的头节点
            	p.next = null; // 将前面节点对当前节点的引用清空
            	return interrupted;
        	}
        	if (shouldParkAfterFailedAcquire(p, node)) // 检查是否失败后需要park
            	interrupted |= parkAndCheckInterrupt();
    	}
       } catch (Throwable t) {
    	cancelAcquire(node);// 出现异常，取消
    	if (interrupted)
        	    selfInterrupt();
    	throw t;
      }
}

```

到这里线程试图获取锁的过程基本展现出来了，tryAcquire是按照特定场景需要开发者去实现的部分，而线程间竞争则是AQS通过Waiter队列与acquireQueued提供的，在release方法中，同样会对队列进行对应操作。

今天我介绍了Atomic数据类型的底层技术CAS，并通过实例演示了如何在产品代码中利用CAS，最后介绍了并发包的基础技术AQS，希望对你有所帮助。

## 一课一练

关于今天我们讨论的题目你做到心中有数了吗？今天布置一个源码阅读作业，AQS中Node的waitStatus有什么作用？

请你在留言区写写你对这个问题的思考，我会选出经过认真思考的留言，送给你一份学习奖励礼券，欢迎你与我一起讨论。

你的朋友是不是也在准备面试呢？你可以“请朋友读”，把今天的题目分享给好友，或许你能帮到他。