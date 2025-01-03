你好，我是郭屹。今天我们继续手写MiniTomcat。

上节课我们从原理出发探讨了Java的NIO模式，以及Tomcat如何实现NIO的。我们知道把Socket设置为NIO模式，通过注册事件的方法来进行读写处理，就相当于有一排信号灯，来了请求就会亮灯，还可以用不同的颜色区分不同的请求，比如连接、读、写等等，然后有一个Poller程序轮询，对不同的信号进行不同的处理。

这节课我们继续聊这个话题，看一下在NIO模式下如何调用Servlet。我们最后再来探讨一下MiniTomcat如何支持NIO。同样的，这节课也是对思路和原理的讨论，并没有对应的源码。

## NIO与Servlet的协同

我们来探讨支持NIO的另一件事情：Servlet协同。我们得先描述一下，前面说了，改成NIO模式之后，网络连接这一部分现在是非阻塞的模式了，主线程不用阻塞等待网络返回，而是可以接着做别的工作了。反映在程序上，我们现在拿到的不再是一个普通的Java socket了，而是SocketChannel。

但是Servlet的行为呢？按照通常的理解，是要阻塞地对数据进行读取，也就是说Servlet程序员写程序的时候，头脑里总是想象数据同步读写完成。这样我们就了解到了，现在网络连接和Servlet调用之间存在一个模式的差别。你可以结合我给出的示意图来理解。

![111](https://static001.geekbang.org/resource/image/06/67/06101abf0d29981582489e1cbdce5767.png?wh=2590x870)

这个差别根本上来自于哪里呢？在发布的Servlet规范中有要求同步阻塞读写吗？并没有，没有任何一段文本表明这一点。但是我们看API，输入输出是用的InputStream和OutputStream，这就表明了在实际的实现中，Servlet的行为是同步阻塞的。

所以为了将NIO模式与Servlet的阻塞读写行为协调起来，我们需要模拟同步阻塞：在一个非阻塞的网络连接上，数据读取的行为看起来又得是同步阻塞的。

我们编程的时候，碰到这类同步异步结合的问题，常用一个编程“技巧”：死循环等待。一方通过一个死循环不停地尝试从另一方获取数据，直到取得全部数据。这个死循环就是在模拟同步过程，我们是可以考虑这个办法的，比较简单，所以后面你会看到我们的MiniTomcat借鉴了这个办法。

## Tomcat如何模拟阻塞式读写?

Tomcat一样要考虑这个事情，所以我们要学习Tomcat自身是怎么处理这个问题的，它的办法也就是我们的办法。以前我就说过，MiniTomcat不是创造新东西，而是为了学习Tomcat而抽取出来的简化版的Tomcat。

你可以看一下我从Tomcat的主页里截取的一张图。

![222](https://static001.geekbang.org/resource/image/2f/4b/2fd7af33bfcc476f876d1546af2bb34b.png?wh=1833x401)

可以看出，对Request和Response的body进行读写，Tomcat一律采用的阻塞模式。那么Tomcat是如何做到的呢？它也是用的模拟方式。我们一点一点来看。

Servlet永远在使用HttpServletRequest，而对于Tomcat来说，在这里用的是RequestFacade。程序要从这里面获得Inputstream，如果我们直接使用JDK的ServletInputStream，肯定是不行的，那还是默认的blocking通道，所以这里要偷梁换柱一下，我们看到Tomcat使用了CoyoteInputStream，这个类它继承了ServletInputStream。这个CoyoteInputStream重新实现了read()。具体来讲，就是用里面的InputBuffer来读的，而最后一步步追下去，就会落在一个NIOSocketWrapper的读操作上。

我们通过主体代码来看看Tomcat怎么用NIO来读数据的。

NioSocketWrapper类：

```plain
volatile boolean readBlocking = false;

fillReadBuffer():
        do {
            n = socketChannel.read(buffer);
            if (n == 0) {
                if (!readBlocking) {
                    readBlocking = true;
                    registerReadInterest();
                }
                synchronized (readLock) {
                    if (readBlocking) {
                        readLock.wait();
                    }
                }
            }
        } while (n == 0);

```

上面的代码是由工作线程执行的，实际通过SocketChannel读取数据。关键是后面的代码，没有读到数据的时候把readBlocking的值设为true。这段程序是如何进行阻塞的呢？首先是一个 do{} 循环，你可以理解为死等，然后这里用了一个锁 readLock，通过wait()操作进行等待，并且在此之前向Poller注册了读事件。死循环 + wait()，这个思路其实很简单。

这个工作线程的等待由Poller来唤醒，你可以看一下主体代码。

Poller类：

```plain
    processkey():
        unreg(sk, socketWrapper, sk.readyOps());
	    if (sk.isReadable()) {
            if (socketWrapper.readBlocking) {
                synchronized (socketWrapper.readLock) {
                    socketWrapper.readBlocking = false;
                    socketWrapper.readLock.notify();
                }
            }
        }

```

通过上面这段代码可以知道，Poller中处理key的时候，在读就绪的情况下，如果判断是readBlocking标志，就使用工作线程里的同一把锁，唤醒工作线程，工作线程继续去读。

NIOSocketWrapper和Poller两者互相配合，就保证了工作线程一直等待直到读取到数据，客观上就是阻塞方式了。这就是Tomcat在NIO通道上模拟阻塞式的实现方案。

而处理写数据的时候也是同样的办法。

NioSocketWrapper类：

```plain
	volatile boolean writeBlocking = false;

	doWrite():
		do {
	        n = socketChannel.write(buffer);
	        if (n == 0 && (buffer.hasRemaining())) {
	            writeBlocking = true;
	            registerWriteInterest();
	            synchronized (writeLock) {
	                if (writeBlocking) {
                        writeLock.wait();
	                    writeBlocking = false;
	                }
	            }
	        }
	    } while (buffer.hasRemaining());

```

Poller类：

```plain
    processkey():
        unreg(sk, socketWrapper, sk.readyOps());
	    if (sk.isWritable()) {
            if (socketWrapper.writeBlocking) {
                synchronized (socketWrapper.writeLock) {
                    socketWrapper.writeBlocking = false;
                    socketWrapper.writeLock.notify();
                }
		    }
        }

```

那这个NIOSocketWrapper是怎么来的呢？回到上一节课我们讲的，当接收到一个网络连接的时候就产生了一个SocketChannel，然后它被包装成了NIOChannel和NIOSocketWrapper，最后给到Servlet的InputStream和OutputStream内部的就是这个NIOSocketWrapper。

这里的关键是NIOSocketWrapper这个类，它包装了SocketChannel，通过模拟的方式将非阻塞式的读写变成了阻塞式的读写。

## MiniTomcat如何支持NIO？

探讨到现在，我们已经了解了NIO原理以及Tomcat是如何支持NIO的。可以感觉到，NIO是一个比较复杂的话题，编写程序的难度比较高，规模也比较大。这也是我们这门课程只讲到这里的原因，真正的NIO和异步处理的实现，需要单开一门课程来讲述。

正好说到这里，我还想多说几句。在Java体系中，非阻塞和异步等特性，整个社区一直支持得不简洁，这些从根本上来说是Java内核带来的，应该在JDK这个层级简洁而有效地解决问题。当然我不是怪发明和推动Java的那些大师们，我这是事后诸葛亮。我们要明白，产品要考虑历史，一个体系的核心一旦确定下来，是不能轻易修改的，发展到最后都可以看到最原始的一段段代码作为整个体系的基因永远流传。好消息是Java 21这个版本引入虚拟线程Virtual Thread为我们带来了希望，让程序员能够简洁地处理异步编程。

根据这些知识和参考，我们自己在将MiniTomcat改造为NIO模式的时候，可以这么考虑：我们现在的程序结构是比较简单的，就是Bootstrap启动服务器，而服务器由Connector + Processor + Container组成。为了整体支持NIO，我们需要把Connector改成NIO模式进行连接，传给Processor的Socket是需要在NIO之上模拟Servlet阻塞式数据读写的。

按照这个思路，我们可以设计一个大概的修改方案。

1. Bootstrap依然是启动器。
2. 将Connector分拆成三块：NIOEndpoint、Acceptor和Poller。NIOEndpoint将实现一个NIO服务端，绑定 IP 地址及端口。NIOEndpoint还需要启动Acceptor线程和Poller线程，分别负责接收连接和轮询。之前的processor连接池结构可以不变，但是要把ServletProcessor类修改成支持SocketChannel的SocketProcessor。
3. Acceptor的accept() 接收新连接，这个连接是SocketChannel，把接收到的连接通道设置为非阻塞的NIO模式。
4. 用上面的SocketChannel构造一个包装对象NIOSocketWrapper，上层程序用这个包装类，而不是直接使用SocketChannel（因为我们需要在这里模拟阻塞式读写），注册到轮询线程，生成事件添加到事件队列。我们后面的数据读写都是在这个NIOSocketWrapper上进行的，因此这里也要加上无限循环等待数据读写，注册读写事件，用readLock和writeLock进行等待wait。通过这种方式，SocketChannel上的非阻塞读写到了NIOSocketWrapper层面就是模拟阻塞式读写了。
5. Poller进行轮询，先取出队列里新增的 PollerEvent 并注册到 Selector，然后调用 Selector.select() 方法来等待就绪的事件，再根据选择的Key 构造 SocketProcessor 提交到请求处理线程。最后Poller还需要唤醒工作线程在readLock/writeLock上的等待，这样来配合模拟Servlet的同步阻塞式读写。
6. SocketProcessor要支持SocketChannel，它带上了NIOSocketWrapper参数，以它为基础构造我们自己的MinitNIOInputStream，所以以前的RequestFacade里面，getInputStream 要返回新的MinitNIOInputStream。这样，网络连接这一块和Servlet这一块底下就是用的同一个SocketChannel。
7. Servlet的读写是基于MiniTomcat实现的stream的，最后落实在NIOSocketWrapper上，所以数据的读写是模拟的同步阻塞方式。

经过这样的修改，原则上就能让MiniTomcat支持NIO模式了。

## 小结

我们这节课了解了Tomcat如何在NIO模式下模拟Servlet的阻塞式读写，基本的做法就是给SocketChannel包装一下变成一个NIOSocketWrapper，在这个Wrapper里，用 **死循环 \+ 读写锁的 wait 方式** 进行模拟阻塞式读写，锁的唤醒则是在Poller里面进行的，达到了轮询器和处理器两者之间的协调。

然后我们结合上节课的知识，探讨了怎么把MiniTomcat修改成支持NIO模式的方案。总的来讲也是两大块内容， **第一部分是网络连接**，通过一个NIOEndpoint把网络连接变成NIO模式，获取到 SocketChannel，并基于它包装出NIOSocketWrapper， **第二部分就是构造自己的 InputStream**，内部使用NIOSocketWrapper，这个stream会被RequestFacade包含并传递给Servlet。

不过我们要注意，这个还只是大致的设计，原理上行得通，而参照Tomcat实际的代码，你会发现还有大量的细节要处理，程序规模也是很大的。

## 思考题

学完了这节课的内容，你来思考一个问题：我们现在的MiniTomcat是只支持HTTP协议的，如果要支持别的协议，需要怎么改造？

欢迎你把你思考后的结果分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！