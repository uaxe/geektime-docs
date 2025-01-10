我们先来看一个反常识的例子。

```
int a=0, b=0;

public void method1() {
  int r2 = a;
  b = 1;
}

public void method2() {
  int r1 = b;
  a = 2;
}

```

这里我定义了两个共享变量a和b，以及两个方法。第一个方法将局部变量r2赋值为a，然后将共享变量b赋值为1。第二个方法将局部变量r1赋值为b，然后将共享变量a赋值为2。请问（r1，r2）的可能值都有哪些？

在单线程环境下，我们可以先调用第一个方法，最终（r1，r2）为（1，0）；也可以先调用第二个方法，最终为（0，2）。

在多线程环境下，假设这两个方法分别跑在两个不同的线程之上，如果Java虚拟机在执行了任一方法的第一条赋值语句之后便切换线程，那么最终结果将可能出现（0，0）的情况。

除上述三种情况之外，Java语言规范第17.4小节\[1\]还介绍了一种看似不可能的情况（1，2）。

造成这一情况的原因有三个，分别为即时编译器的重排序，处理器的乱序执行，以及内存系统的重排序。由于后两种原因涉及具体的体系架构，我们暂且放到一边。下面我先来讲一下编译器优化的重排序是怎么一回事。

首先需要说明一点，即时编译器（和处理器）需要保证程序能够遵守as-if-serial属性。通俗地说，就是在单线程情况下，要给程序一个顺序执行的假象。即经过重排序的执行结果要与顺序执行的结果保持一致。

另外，如果两个操作之间存在数据依赖，那么即时编译器（和处理器）不能调整它们的顺序，否则将会造成程序语义的改变。

```
int a=0, b=0;

public void method1() {
  int r2 = a;
  b = 1;
  .. // Code uses b
  if (r2 == 2) {
    ..
  }
}

```

在上面这段代码中，我扩展了先前例子中的第一个方法。新增的代码会先使用共享变量b的值，然后再使用局部变量r2的值。

此时，即时编译器有两种选择。

第一，在一开始便将a加载至某一寄存器中，并且在接下来b的赋值操作以及使用b的代码中避免使用该寄存器。第二，在真正使用r2时才将a加载至寄存器中。这么一来，在执行使用b的代码时，我们不再霸占一个通用寄存器，从而减少需要借助栈空间的情况。

```
int a=0, b=0;

public void method1() {
  for (..) {
    int r2 = a;
    b = 1;
    .. // Code uses r2 and rewrites a
  }
}

```

另一个例子则是将第一个方法的代码放入一个循环中。除了原本的两条赋值语句之外，我只在循环中添加了使用r2，并且更新a的代码。由于对b的赋值是循环无关的，即时编译器很有可能将其移出循环之前，而对r2的赋值语句还停留在循环之中。

如果想要复现这两个场景，你可能需要添加大量有意义的局部变量，来给寄存器分配算法施加压力。

可以看到，即时编译器的优化可能将原本字段访问的执行顺序打乱。在单线程环境下，由于as-if-serial的保证，我们无须担心顺序执行不可能发生的情况，如（r1，r2）=（1，2）。

然而，在多线程情况下，这种数据竞争（data race）的情况是有可能发生的。而且，Java语言规范将其归咎于应用程序没有作出恰当的同步操作。

## Java内存模型与happens-before关系

为了让应用程序能够免于数据竞争的干扰，Java 5引入了明确定义的Java内存模型。其中最为重要的一个概念便是happens-before关系。happens-before关系是用来描述两个操作的内存可见性的。如果操作X happens-before操作Y，那么X的结果对于Y可见。

在同一个线程中，字节码的先后顺序（program order）也暗含了happens-before关系：在程序控制流路径中靠前的字节码happens-before靠后的字节码。然而，这并不意味着前者一定在后者之前执行。实际上，如果后者没有观测前者的运行结果，即后者没有数据依赖于前者，那么它们可能会被重排序。

除了线程内的happens-before关系之外，Java内存模型还定义了下述线程间的happens-before关系。

1. 解锁操作 happens-before 之后（这里指时钟顺序先后）对同一把锁的加锁操作。
2. volatile字段的写操作 happens-before 之后（这里指时钟顺序先后）对同一字段的读操作。
3. 线程的启动操作（即Thread.starts()） happens-before 该线程的第一个操作。
4. 线程的最后一个操作 happens-before 它的终止事件（即其他线程通过Thread.isAlive()或Thread.join()判断该线程是否中止）。
5. 线程对其他线程的中断操作 happens-before 被中断线程所收到的中断事件（即被中断线程的InterruptedException异常，或者第三个线程针对被中断线程的Thread.interrupted或者Thread.isInterrupted调用）。
6. 构造器中的最后一个操作 happens-before 析构器的第一个操作。

happens-before关系还具备传递性。如果操作X happens-before操作Y，而操作Y happens-before操作Z，那么操作X happens-before操作Z。

在文章开头的例子中，程序没有定义任何happens-before关系，仅拥有默认的线程内happens-before关系。也就是r2的赋值操作happens-before b的赋值操作，r1的赋值操作happens-before a的赋值操作。

```
Thread1      Thread2
  |            |
 b=1           |
  |          r1=b
  |           a=2
r2=a           |

```

拥有happens-before关系的两对赋值操作之间没有数据依赖，因此即时编译器、处理器都可能对其进行重排序。举例来说，只要将b的赋值操作排在r2的赋值操作之前，那么便可以按照赋值b，赋值r1，赋值a，赋值r2的顺序得到（1，2）的结果。

那么如何解决这个问题呢？答案是，将a或者b设置为volatile字段。

比如说将b设置为volatile字段。假设r1能够观测到b的赋值结果1。显然，这需要b的赋值操作在时钟顺序上先于r1的赋值操作。根据volatile字段的happens-before关系，我们知道b的赋值操作happens-before r1的赋值操作。

```
int a=0;
volatile int b=0;

public void method1() {
  int r2 = a;
  b = 1;
}

public void method2() {
  int r1 = b;
  a = 2;
}

```

根据同一个线程中，字节码顺序所暗含的happens-before关系，以及happens-before关系的传递性，我们可以轻易得出r2的赋值操作happens-before a的赋值操作。

这也就意味着，当对a进行赋值时，对r2的赋值操作已经完成了。因此，在b为volatile字段的情况下，程序不可能出现（r1，r2）为（1，2）的情况。

由此可以看出，解决这种数据竞争问题的关键在于构造一个跨线程的happens-before关系 ：操作X happens-before 操作Y，使得操作X之前的字节码的结果对操作Y之后的字节码可见。

## Java内存模型的底层实现

在理解了Java内存模型的概念之后，我们现在来看看它的底层实现。Java内存模型是通过内存屏障（memory barrier）来禁止重排序的。

对于即时编译器来说，它会针对前面提到的每一个happens-before关系，向正在编译的目标方法中插入相应的读读、读写、写读以及写写内存屏障。

这些内存屏障会限制即时编译器的重排序操作。以volatile字段访问为例，所插入的内存屏障将不允许volatile字段写操作之前的内存访问被重排序至其之后；也将不允许volatile字段读操作之后的内存访问被重排序至其之前。

然后，即时编译器将根据具体的底层体系架构，将这些内存屏障替换成具体的CPU指令。以我们日常接触的X86\_64架构来说，读读、读写以及写写内存屏障是空操作（no-op），只有写读内存屏障会被替换成具体指令\[2\]。

在文章开头的例子中，method1和method2之中的代码均属于先读后写（假设r1和r2被存储在寄存器之中）。X86\_64架构的处理器并不能将读操作重排序至写操作之后，具体可参考Intel Software Developer Manual Volumn 3，8.2.3.3小节。因此，我认为例子中的重排序必然是即时编译器造成的。

举例来说，对于volatile字段，即时编译器将在volatile字段的读写操作前后各插入一些内存屏障。

然而，在X86\_64架构上，只有volatile字段写操作之后的写读内存屏障需要用具体指令来替代。（HotSpot所选取的具体指令是lock add DWORD PTR \[rsp\],0x0，而非mfence\[3\]。）

该具体指令的效果，可以简单理解为强制刷新处理器的写缓存。写缓存是处理器用来加速内存存储效率的一项技术。

在碰到内存写操作时，处理器并不会等待该指令结束，而是直接开始下一指令，并且依赖于写缓存将更改的数据同步至主内存（main memory）之中。

强制刷新写缓存，将使得当前线程写入volatile字段的值（以及写缓存中已有的其他内存修改），同步至主内存之中。

由于内存写操作同时会无效化其他处理器所持有的、指向同一内存地址的缓存行，因此可以认为其他处理器能够立即见到该volatile字段的最新值。

## 锁，volatile字段，final字段与安全发布

下面我来讲讲Java内存模型涉及的几个关键词。

前面提到，锁操作同样具备happens-before关系。具体来说，解锁操作 happens-before 之后对同一把锁的加锁操作。实际上，在解锁时，Java虚拟机同样需要强制刷新缓存，使得当前线程所修改的内存对其他线程可见。

需要注意的是，锁操作的happens-before规则的关键字是同一把锁。也就意味着，如果编译器能够（通过逃逸分析）证明某把锁仅被同一线程持有，那么它可以移除相应的加锁解锁操作。

因此也就不再强制刷新缓存。举个例子，即时编译后的synchronized (new Object()) {}，可能等同于空操作，而不会强制刷新缓存。

volatile字段可以看成一种轻量级的、不保证原子性的同步，其性能往往优于（至少不亚于）锁操作。然而，频繁地访问volatile字段也会因为不断地强制刷新缓存而严重影响程序的性能。

在X86\_64平台上，只有volatile字段的写操作会强制刷新缓存。因此，理想情况下对volatile字段的使用应当多读少写，并且应当只有一个线程进行写操作。

volatile字段的另一个特性是即时编译器无法将其分配到寄存器里。换句话说，volatile字段的每次访问均需要直接从内存中读写。

final实例字段则涉及新建对象的发布问题。当一个对象包含final实例字段时，我们希望其他线程只能看到已初始化的final实例字段。

因此，即时编译器会在final字段的写操作后插入一个写写屏障，以防某些优化将新建对象的发布（即将实例对象写入一个共享引用中）重排序至final字段的写操作之前。在X86\_64平台上，写写屏障是空操作。

新建对象的安全发布（safe publication）问题不仅仅包括final实例字段的可见性，还包括其他实例字段的可见性。

当发布一个已初始化的对象时，我们希望所有已初始化的实例字段对其他线程可见。否则，其他线程可能见到一个仅部分初始化的新建对象，从而造成程序错误。这里我就不展开了。如果你感兴趣的话，可以参考这篇博客\[4\]。

## 总结与实践

今天我主要介绍了Java的内存模型。

Java内存模型通过定义了一系列的happens-before操作，让应用程序开发者能够轻易地表达不同线程的操作之间的内存可见性。

在遵守Java内存模型的前提下，即时编译器以及底层体系架构能够调整内存访问操作，以达到性能优化的效果。如果开发者没有正确地利用happens-before规则，那么将可能导致数据竞争。

Java内存模型是通过内存屏障来禁止重排序的。对于即时编译器来说，内存屏障将限制它所能做的重排序优化。对于处理器来说，内存屏障会导致缓存的刷新操作。

今天的实践环节，我们来复现文章初始的例子。由于复现需要大量的线程切换事件，因此我借助了OpenJDK CodeTools项目的jcstress工具\[5\]，来对该例子进行并发情况下的压力测试。具体的命令如下所示：

```
$ mvn archetype:generate -DinteractiveMode=false -DarchetypeGroupId=org.openjdk.jcstress -DarchetypeArtifactId=jcstress-java-test-archetype -DarchetypeVersion=0.1.1 -DgroupId=org.sample -DartifactId=test -Dversion=1.0
$ cd test
$ echo 'package org.sample;
import org.openjdk.jcstress.annotations.*;
import org.openjdk.jcstress.infra.results.IntResult2;
@JCStressTest
@Outcome(id = {"0, 0", "0, 2", "1, 0"}, expect = Expect.ACCEPTABLE, desc = "Normal outcome")
@Outcome(id = {"1, 2"}, expect = Expect.ACCEPTABLE_INTERESTING, desc = "Abnormal outcome")
@State
public class ConcurrencyTest {
  int a=0;
  int b=0; //改成volatile试试？
  @Actor
  public void method1(IntResult2 r) {
    r.r2 = a;
    b = 1;
  }
  @Actor
  public void method2(IntResult2 r) {
    r.r1 = b;
    a = 2;
  }
}' > src/main/java/org/sample/ConcurrencyTest.java
$ mvn package
$ java -jar target/jcstress.jar

```

如果你想要复现非安全发布的情形，那么你可以试试这一测试用例\[6\]。

\[1\] [https://docs.oracle.com/javase/specs/jls/se10/html/jls-17.html#jls-17.4](https://docs.oracle.com/javase/specs/jls/se10/html/jls-17.html#jls-17.4)

\[2\] [http://gee.cs.oswego.edu/dl/jmm/cookbook.html](http://gee.cs.oswego.edu/dl/jmm/cookbook.html)

\[3\] [https://blogs.oracle.com/dave/instruction-selection-for-volatile-fences-:-mfence-vs-lock:add](https://blogs.oracle.com/dave/instruction-selection-for-volatile-fences-:-mfence-vs-lock:add)

\[4\] [http://vlkan.com/blog/post/2014/02/14/java-safe-publication/](http://vlkan.com/blog/post/2014/02/14/java-safe-publication/)

\[5\] [https://wiki.openjdk.java.net/display/CodeTools/jcstress](https://wiki.openjdk.java.net/display/CodeTools/jcstress)

\[6\] [http://hg.openjdk.java.net/code-tools/jcstress/file/64f2cf32fa0a/tests-custom/src/main/java/org/openjdk/jcstress/tests/unsafe/UnsafePublication.java](http://hg.openjdk.java.net/code-tools/jcstress/file/64f2cf32fa0a/tests-custom/src/main/java/org/openjdk/jcstress/tests/unsafe/UnsafePublication.java)