你好，我是郑雨迪。

Java 线程是 Java 程序执行的基本单位，相信大家对此并不陌生。JVM 允许应用程序同时运行多个线程，从而实现并发执行。

传统的 Java 线程依赖操作系统的原生线程，由操作系统负责调度和管理。这类线程的内存开销较大，单个线程的栈空间通常超过 1MB（可通过 -Xss 或 -XX:ThreadStackSize 进行调整，最小值为 1MB）。

例如，在 Web 服务器中，如果为每个请求创建一个 Java 线程，处理百万级别的请求将消耗超过 1TB 的内存用于栈空间，这在实际应用中难以承受。

因此，JVM 能够创建的线程数量受限，难以满足高并发场景的需求，与主流的异步编程模型存在一定冲突。

## 虚拟线程

**JDK 21 的 Loom 项目 [\[1\]](https://openjdk.org/jeps/444) 将传统的 Java 线程划分为虚拟线程（virtual thread）和平台线程（platform thread）。**

平台线程本质上仍是原来的 Java 线程，同样与操作系统的原生线程一一映射，并且需要固定的大容量栈空间，因此 JVM 能够创建的平台线程数量十分有限。

相比之下，虚拟线程采用了可变栈空间的设计。**对于调用层级较浅的简单任务，其栈空间占用极小。**这一特性使得 JVM 能够同时创建大量的虚拟线程，从而支持 “一个任务一个线程” 的编程模型，提高并发能力。