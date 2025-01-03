你好，我是丁威。

上一节课，我们介绍了中间件领域最经典的网络编程模型NIO，我也在文稿的最后给你提供了用NIO模拟Reactor线程模型的示例代码。如果你真正上手了，你会明显感知到，如果代码处理得过于粗糙，只关注正常逻辑却对一些异常逻辑考虑不足，就不能成为一个生产级的产品。

这是因为要直接基于NIO编写网络通讯层代码，需要开发者拥有很强的代码功底和丰富的网络通信理论知识。所以，为了降低网络编程的门槛，Netty框架就出现了，它能够对NIO进行更高层级的封装。

从这之后，开发人员只需要关注业务逻辑的开发就好了，网络通信的底层可以放心交给Netty，大大降低了网络编程的开发难度。

这节课，我们就来好好谈谈Netty。

我会先从网络编程中通信协议、线程模型这些网络编程框架的共性问题入手，然后重点分析Netty NIO的读写流程，最后通过一个Netty编程实战，教会你怎么使用Netty解决具体问题，让你彻底掌握Netty。

## 通信协议

如果你不从事中间件开发工作，那估计网络编程对你来说会非常陌生，为了让你对它有一个直观的认知，我给你举一个例子。

假如我们在使用Dubbo构建微服务应用，Dubbo客户端在向服务提供者发起远程调用的过程中，需要告诉服务提供者服务名、方法名和参数。但这些参数是怎么在网络中传递的呢？服务提供者又怎么识别出客户端的意图呢？

你可以先看看我画的这张图：

![图片](https://static001.geekbang.org/resource/image/4e/f0/4ec5c84yy26af476210e1e653c01aff0.jpg?wh=1920x553)

客户端在发送内容之前需要先将待发送的内容序列化为二进制流。例如，上图发送了两个包，第一个包的二进制流是0110，第二个包的二进制流是00110011。这时，服务端读取数据的情形可能有两种。

1. **经过多次读取**：在上面这张图中，服务端调用了3次read方法才把数据全部读取出来，分别读取到的包是011、000、110011。
2. **调用一次read就读取到所有数据**：例如011000110011。

这里我插播一个小知识，一次read方法能读取到的数据量，要取决于网卡中可读数据和接收缓冲区的大小。

那服务端是如何正确识别出0110就是第一个请求包，00110011是第二个请求包的呢？它为什么不会将011当成第一个请求包，000当成第二个请求包，110011当成第三个包，或者直接将011000110011当成一个请求包呢？其实这种现象叫做 **粘包。**

常用的解决方案是客户端与服务端共同制定一个通信规范（也称通信协议），用它来定义请求包/响应包的具体格式。这样，客户端发送请求之前，需要先将内容按照通信规范序列化成二进制流，这个过程称之为编码；同样，服务端会按照通信规范将收到的二进制流进行反序列化，这个过程称之为解码。

从这里你也可以看出，网络编程中通常涉及编码、往网络中写数据（Write）、从网络中读取数据（Read）、解码、业务逻辑处理、发送响应结果和接受响应结果等步骤，你可以看下下面这张图，加深理解：

![图片](https://static001.geekbang.org/resource/image/48/4f/487acd1670a4b7578e1bf50cfaa0334f.jpg?wh=1920x652)

那如何制订通信协议呢？

通信协议的制订方法有很多，有的是采用特殊符号来标记一个请求的结束，但如果请求体中也包含这个分隔符就会使协议破坏，还有一种方法是使用固定长度来表述一个请求包，定义一个请求包固定包含多少字节，如果请求体内存不足，就使用填充符合进行填充，但这种方式会造成空间的浪费。

业界最为经典的协议设计方法是 **协议头+Body的设计理念**，如图所示：

![图片](https://static001.geekbang.org/resource/image/f7/a8/f7df1794aac442388868b51d24948da8.jpg?wh=1804x551)

这里有几个关键点，你需要注意一下：

- **协议头的长度是固定的**，通常为识别出一个业务的最小长度；
- 协议头中会包含一个长度字段，用来标识一个完整包的长度，用来表示长度字段的字节位数直接决定了一个包的最大长度；
- 消息体中存储业务数据。

为了更直观地给你展示，我直接以一个简单的 RPC 通信场景为例，实现类似Dubbo服务远程服务调用，通信协议设计如下图所示：

![图片](https://static001.geekbang.org/resource/image/eb/6a/eb61c11e8675a604585f56b7f020436a.jpg?wh=1920x703)

这里我们演示的是基于Header+Body的设计模式，接受端从网络中读取到字节后解码的流程。接受端将读取到的数据存储在一个接收缓冲区，在Netty中称为累积缓冲区。

首先我们要判断累积缓存区中是否包含一个完整的Head，例如上述示例中，一个包的Header 的长度为 6 个字节，那首先判断累积缓存中可读字节数是否大于等于 6， **如果不足 6 个字节，跳过本次处理，等待更多数据到达累积缓存区。**

如果累积缓存区中包含一个完整的Header，就解析头部，并且提取长度字段中存储的数值，即包长度，然后判断累积缓存区中可读字节数是否大于或等于整个包的长度。 **如果累积缓存区不包含一个完整的数据包，则跳过本次处理，等待更多数据到达累积缓存区。** 如果累积缓存区包含一个完整的包，则按照通信协议的格式按顺序读取相关的内容。

通过上面这种方式，我们就可以完美解决粘包问题了。

我们前面也说了，网络编程中包含编码、解码、网络读取、业务逻辑等多个步骤，所以如何使用多线程提升并发度，合理处理多线程之间的高效协作就显得尤为重要，接下来我们来看一下Netty的线程模型是怎么做的。

Netty的线程模型采取的是业界的主流线程模型，也就是主从多Reactor模型：

![图片](https://static001.geekbang.org/resource/image/b1/yy/b117c06b91c299ca835d7613d351a2yy.jpg?wh=1920x1090)

它的设计重点主要包括下面这几个方面。

- **Netty Boss Group线程组**

主要处理OP\_ACCEPT事件，用于处理客户端链接，默认为1个线程。当Netty Boss Group线程组接收到一个客户端链接时，会创建NioSocketChannel对象，并封装成Channel对象，在Channel对象内部会创建一个缓冲区。这个缓冲区可以接收需要通过这个通道写入到对端的数据，然后从Netty Work Group线程组中选择一个线程并注册读事件。

- **Nettty Work Group线程组**

主要处理OP\_READ、OP\_WRITE事件，处理网络的读与写，所以也称为IO线程组，线程组中线程个数默认为CPU的核数。由于注册了读事件，所以当客户端发送请求时，读事件就会触发，从网络中读取请求，进入请求处理流程。

- **扩展机制采用责任链设计模式**

编码、解码等功能对应一个独立的Handler，这些Handler默认在IO线程中执行，但Netty支持将Handler的执行放在额外的线程中执行，实现与IO线程的解耦合，避免IO线程阻塞。

- **Business Thread Group**

经过解码后得到一个完整的请求包，根据请求包执行业务逻辑，通常会额外引入一个独立线程池，执行业务逻辑后会将结果再通过IO线程写入到网络中。

业务线程在处理完业务逻辑后，通过调用通道将数据发送到目标端。但它并不能当下直接发送，而是要将数据放入到Channel中的写缓存区，并向IO线程提交一个写入任务。这里涉及到线程切换，因为所有的读写操作都需要在IO线程中执行（即一个通道的IO操作都是同一个线程触发的），避免了多线程编程的复杂性。

**说到这里，我建议你停下来，尝试用NIO实现Netty的线程模型，检验一下自己对NIO的掌握程度。**

理解了Netty的线程模型，接下来我们继续学习Netty是怎样处理读写流程的。在进入下面的学习之前，我有几个问题希望你先思考一下：

1. 如何处理连接半关闭？
2. 什么时候应该注册读事件？
3. 写数据之前一定要先注册写事件吗？

## Netty如何处理网络读写事件？

Netty IO 读事件由 AbstractNioByteChannel 内部类 AbstractNioUnsafe 的 read 方法实现，接下来我们就来重点剖析一下这个方法，从中窥探 Netty 是如何实现 IO 读事件的。

由于AbstractNioUnsafe的read方法代码很长，我们分步进行解读。

**第一步**，如果没有开启自动注册读事件，在每一次读时间处理过后会取消读事件，代码片段如下：

```plain
  final ChannelConfig config = config();
  if (!config.isAutoRead() && !isReadPending()) {
       // ChannelConfig.setAutoRead(false) was called in the meantime
       removeReadOp();
       return;
  }

```

这段代码背后蕴含的知识点是，事件注册是一次性的。例如，为通道注册了读事件，然后经事件选择器选择触发后，选择器不再监听读事件，再出来完成一次读事件后需要 **再次注册读事件**。Netty中默认每次读取处理后会自动注册读事件， **如果通道没有注册读事件，则无法从网络中读取数据。**

**第二步**，为本次读取创建接收缓冲区，临时存储从网络中读取到的字节，代码片段如下：

```plain
  final ByteBufAllocator allocator = config.getAllocator();
  final int maxMessagesPerRead = config.getMaxMessagesPerRead();
  RecvByteBufAllocator.Handle allocHandle = this.allocHandle;
  if (allocHandle == null) {
    this.allocHandle = allocHandle = config.getRecvByteBufAllocator().newHandle();
  }

```

创建接收缓存区需要考虑的问题是，该创建多大的缓存区呢？如果缓存区创建大了，就容易造成内存浪费；如果分配少了，在使用过程中就可能需要进行扩容，性能就会受到影响。

Netty在这里提供了扩展机制，允许用户自定义创建策略，只需实现RecvByteBufAllocator接口就可以了。它又包括两种实现方式：

- 分配固定大小，待内存不够时扩容；
- 动态变化，根据历史的分配大小，动态调整接收缓冲区的大小。

**第三步，** 循环从网络中读取数据，代码片段如下：

```plain
  do {
    byteBuf = allocHandle.allocate(allocator);
    int writable = byteBuf.writableBytes();
    int localReadAmount = doReadBytes(byteBuf);
    // 省略代码
  } while (++ messages < maxMessagesPerRead);

```

为什么要循环读取呢？为什么不一次性把通道中需要读取到的数据全部读完再继续下一个通道呢？

其实，这主要是为了避免单个通道占用太多时间，导致其他链接没有机会去读取数据。所以Netty会限制在一次读事件处理过程中调用底层读取API的次数，这个次数默认为16次。

接下来我们进行第四步。这里要提醒一下，第四步和第五步都是位于第三步的循环之中的。

**第四步，** 调用底层SokcetChannel的read方法从网络中读取数据，代码片段如下：

```plain
 byteBuf = allocHandle.allocate(allocator);
 int writable = byteBuf.writableBytes();
 int localReadAmount = doReadBytes(byteBuf);
 if (localReadAmount <= 0) {
    // not was read release the buffer
    byteBuf.release();
    byteBuf = null;
    close = localReadAmount < 0;
    break;
 }
pipeline.fireChannelRead(byteBuf);

```

解释一下，首先用writable存储接收缓存区可写字节数，然后通过调用底层NioSocketChannel从网络中读取数据，并返回本次读取的字节数。

那在什么情况下读取的字节数小于0呢？原来，TCP是全双工通信模型，任意一端都可以关闭接收或者写入，如果对端连接调用了 **关闭（半关闭）**，那么我们尝试从网络中读取字节时就会返回-1，跳出循环。

然后，我们要将读取到的内容传播到事件链中，事件链中各个事件处理器会依次对这些数据进行处理。

**如果你也在使用Netty进行应用代码开发，请特别注意byteBuf的释放问题。自定义的事件处理器中要尽量继续调用fireChannelRead方法，Netty内置了一个HeadContext，它在实现时会主动释放ByteBuf。但如果自定义的事件处理器阻断了事件传播，请记得一定要释放ByteBuf，否则会造成内存泄露。**

**第五步，** 判断是否要跳出读取：

```plain
  if (totalReadAmount >= Integer.MAX_VALUE - localReadAmount) {
    // Avoid overflow.
    totalReadAmount = Integer.MAX_VALUE;
    break;
  }
  totalReadAmount += localReadAmount;
  // stop reading
  if (!config.isAutoRead()) {
    break;
  }
  if (localReadAmount < writable) {
    // Read less than what the buffer can hold,
    // which might mean we drained the recv buffer completely.
    break;
  }

```

这里需要关注的一个点是， **本次读取到的字节数如果小于接收缓冲区的可写大小**，说明通道中 **已经没有数据可读了**，结束本次读取事件的处理。

**第六步，** 完成网络IO读取后，进行善后操作。具体代码片段如下：

```plain
  pipeline.fireChannelReadComplete();
  allocHandle.record(totalReadAmount);
  if (close) {
    closeOnRead(pipeline);
    close = false;
  }

```

操作结束后，会触发一次读完成事件，并向整个事件链传播。这时候如果对端已经关闭了，则主动关闭链接。

就像我们在上节课提到的，事件机制触发后将失效，需要再次注册，所以Netty支持自动注册读事件。在每一次读事件完成后会主动调用下面这段代码实现读事件的自动注册，具体实现在HeadContext的fireChannelReadComplete方法中，代码片段如下：

```plain
public void channelReadComplete(ChannelHandlerContext ctx) throws Exception {
  ctx.fireChannelReadComplete();
  readIfIsAutoRead();//该方法最终会调用Channel的read方法，注册读事件
}

```

这里还涉及另一问题，那就是Netty的channelRead、channelReadComplete等事件是怎么传播的呢？我建议你查看我的另一篇文章 [《Netty4 事件处理传播机制》](https://mp.weixin.qq.com/s/5dlUN0bzW3aKfcg1PSR5Ow)。

Netty网络读流程就讲到这里了，我们用一张流程图结束网络读取部分的讲解：

![图片](https://static001.geekbang.org/resource/image/96/87/963f0b7a9b44b16c2d36e0c859110f87.jpg?wh=1920x921)

接下来，我们一起看看Netty的网络写入流程。

基于Netty网络模型，通常会使用一个业务线程池来执行业务操作，业务执行完成后，需要通过网络将响应结果提交给对应的IO线程，再通过IO线程将数据返回给客户端，其过程大致如下：

![图片](https://static001.geekbang.org/resource/image/4d/f8/4d23a22e05fe908b9e31cdecde8bfbf8.jpg?wh=1920x761)

那在代码实现层面，业务线程与IO线程是怎么协作的呢？我们带着这个问题，继续深入研究Netty的网络写入流程。

在Netty中，一眼就能看到写事件的处理入口，也就是NioEventLoop（IO线程）的processSelectedKey方法，代码片段如下所示：

```plain
// Process OP_WRITE first as we may be able to write some queued buffers and so free memory.
if ((readyOps & SelectionKey.OP_WRITE) != 0) {
    // Call forceFlush which will also take care of clear the OP_WRITE once there is nothing left to write
    ch.unsafe().forceFlush();
}

```

查看processSelectedKey方法的调用链，我们看到这个方法最终会调用AbstractUnsafe的flush0方法，代码片段如下所示：

```plain
protected void flush0() {
		if (inFlush0) {
    	return;
    }
    final ChannelOutboundBuffer outboundBuffer = this.outboundBuffer; // @1
    if (outboundBuffer == null || outboundBuffer.isEmpty()) {
    		return;
    }
    inFlush0 = true;
    // Mark all pending write requests as failure if the channel is inactive.
    if (!isActive()) { // @2
        try {
             if (isOpen()) {
                outboundBuffer.failFlushed(FLUSH0_NOT_YET_CONNECTED_EXCEPTION, true);
             } else {
                outboundBuffer.failFlushed(FLUSH0_CLOSED_CHANNEL_EXCEPTION, false);
             }
        } finally {
             inFlush0 = false;
        }
        return;
     }
     try {
         doWrite(outboundBuffer);  // @3
     } catch (Throwable t) {
         if (t instanceof IOException && config().isAutoClose()) {
              close(voidPromise(), t, FLUSH0_CLOSED_CHANNEL_EXCEPTION, false);
         } else {
              outboundBuffer.failFlushed(t, true);
         }
     } finally {
         inFlush0 = false;
     }
}

```

flush0方法的核心要点主要包括下面三点。

- 获取写缓存队列。如果写缓存队列为空，则跳过本次写事件。每一个通道Channel内部维护一个写缓存区，其他线程调用Channel向网络中写数据时，首先会写入到写缓存区，等到写事件被触发时，再将写缓存区中的数据写入到网络中。
- 如果通道处于未激活状态，需要清理写缓存区，避免数据污染。
- 通过调用 doWrite 方法将写缓存中的数据写入网络通道中。

这里的doWrite方法比较重要，我们重点介绍一下。

doWrite方法主要使用NIO完成数据的写入，具体由NioSocketChannel的doWrite实现，由于这一方法代码较长，我们还是分段来进行讲解。

**第一步，** 如果通道的写缓存区中没有可写数据，需要取消写事件，也就是说，这时候不必关注写事件。具体代码如下：

```plain
int size = in.size();
if (size == 0) {
		// All written so clear OP_WRITE
    clearOpWrite();
    break;
}

```

这背后的逻辑是，如果注册写事件，每次进行事件就绪选择时，只要底层TCP连接的写缓存区不为空，写就会就绪，它会继续通知上层应用程序可以往通道中就绪了。但这种情况下，如果上层应用无数据可写，写事件就绪就变得没有意义了。所以，为了避免出现这种情况，如果没有数据可写，建议直接取消写事件。

**第二步，** 尝试将缓存区数据写入到网络中：

```plain
switch (nioBufferCnt) {
		case 0:
      	super.doWrite(in);
        return;
    case 1:
        ByteBuffer nioBuffer = nioBuffers[0];
        for (int i = config().getWriteSpinCount() - 1; i >= 0; i --) {
           final int localWrittenBytes = ch.write(nioBuffer);
           if (localWrittenBytes == 0) {
               setOpWrite = true;
                break;
           }
           expectedWrittenBytes -= localWrittenBytes;
           writtenBytes += localWrittenBytes;
           if (expectedWrittenBytes == 0) {
               done = true;
               break;
           }
        }
        break;
     default:
        for (int i = config().getWriteSpinCount() - 1; i >= 0; i --) {
             final long localWrittenBytes = ch.write(nioBuffers, 0, nioBufferCnt);
             if (localWrittenBytes == 0) {
                   setOpWrite = true;
                   break;
             }
             expectedWrittenBytes -= localWrittenBytes;
             writtenBytes += localWrittenBytes;
             if (expectedWrittenBytes == 0) {
                  done = true;
                  break;
             }
         }
        break;
 }

```

也就是说，这一步要根据缓存区中的数据进行区分写入，各个分支的情况有所不同：

- 如果缓存区nioBufferCnt的个数为0，说明待写入数据为FileRegion（Netty零拷贝实现关键点），需要调用父类NIO相关方法完成数据写入。
- 如果数据是Buffer类型，且只有1个，则直接调用父类的doWrite方法，它的底层逻辑是基于NIO通道写入数据。
- 如果数据是Buffer类型而且有多个，那就要使用NIO Gather机制了，这可以避免数据复制。

写入端的处理逻辑也是差不多的。 **我们可以通过底层NIO SocketChannel的write方法将数据写入到Socket缓存区，** 有三种情况需要分别考虑。

- 如果返回值为０，表示Socket底层的缓存区已满，需要暂停写入。具体做法是，注册写事件，等Socket底层写缓存区空闲后再继续写入。
- 如果写缓存区的数据写入到了网络，那就需要取消注册写事件，避免毫无意义的写事件就绪。
- 如果写缓存区中的数据很大，为了避免单个通道对其他通道的影响，默认设置单次写事件最多调用底层 NIO SocketChannel的write方法的次数为16。

**第三步，** 如果底层缓存区已写满，重新注册写事件；如果需要写入的数据太多，则需要创建一个Task放入到IO线程中，待就绪事件处理完毕后继续处理。代码片段如下：

```plain
if (!done) {
    // Did not write all buffers completely.
    incompleteWrite(setOpWrite);
    break;
}
protected final void incompleteWrite(boolean setOpWrite) {
        // Did not write completely.
        if (setOpWrite) {
            setOpWrite();
        } else {
            // Schedule flush again later so other tasks can be picked up in the meantime
            Runnable flushTask = this.flushTask;
            if (flushTask == null) {
                flushTask = this.flushTask = new Runnable() {
                    @Override
                    public void run() {
                        flush();
                    }
                };
            }
            eventLoop().execute(flushTask);
        }
    }

```

**注意，这里是处理写入的第二个触发点。将写入请求添加到IO线程的任务列表中，就可以继续执行数据写入。也就是说，并不一定要注册写事件才能进行写入。**

Task的触发点在NioEventLoop的run方法，代码片段如下：

```plain
if (ioRatio == 100) {
   try {
     processSelectedKeys();
   } finally {
     // Ensure we always run tasks.
     runAllTasks();
  }
} else {
  final long ioStartTime = System.nanoTime();
  try {
     processSelectedKeys();
  } finally {
     // Ensure we always run tasks.
     final long ioTime = System.nanoTime() - ioStartTime;
     runAllTasks(ioTime * (100 - ioRatio) / ioRatio);
  }
}

```

其中，processSelectedKeys就是NIO事件的就绪执行入口。IO线程在执行完事件就绪选择后，会继续执行任务列表中的任务。

在实际开发中，通常是在完成业务逻辑后，往网络中写入数据，调用Channel的writeAndFlush方法。在Channel内部会分别调用write和flush方法。write方法是将数据写入到通道（Channel）对象的写缓存区，而调用flush方法是将通道缓存中的数据写入到网络（Socket 的写缓存区），继而通过网络传输到接收端。

Netty为了避免IO线程与多个业务线程之间的并发问题，业务线程不能直接调用IO线程的数据写入方法，只能是向IO线程提交写入任务，具体代码定义在AbstractChannelHandlerContext的write方法中。

```plain
private void write(Object msg, boolean flush, ChannelPromise promise) {
        AbstractChannelHandlerContext next = findContextOutbound();
        EventExecutor executor = next.executor();
        if (executor.inEventLoop()) {
            if (flush) {
                next.invokeWriteAndFlush(msg, promise);
            } else {
                next.invokeWrite(msg, promise);
            }
        } else {
            AbstractWriteTask task;
            if (flush) {
                task = WriteAndFlushTask.newInstance(next, msg, promise);
            }  else {
                task = WriteTask.newInstance(next, msg, promise);
            }
            safeExecute(executor, task, promise, msg);
        }
    }

```

为了方便你深入阅读Netty相关源码，我还给你整理了Netty写入的流程图：

## ![图片](https://static001.geekbang.org/resource/image/a2/57/a24e94e0078c9cdf1ace4e0541300b57.jpg?wh=1920x1780)

## Netty编程实战

好了，关于Netty网络读写的理解就介绍到这里了，但是只有理论是不行的，在这节课的最后，我们来看一个Netty的实战案例。

Netty通常会用在中间件开发、即时通信（IM）、游戏服务器、高性能网关服务器等领域，阿里巴巴的高性能消息中间件RocketMQ就是用Netty进行网络层开发的。

为了方便你学习，我将RocketMQ网络层代码单独抽取成了一个网络编程框架，并上传到了 [GitHub](https://github.com/dingwpmz/netty-learning/tree/main/netty-framework)，你可以拷贝下来跟我一起操作。

在深入RocketMQ网络层具体实践之前，我们先来看一下RocketMQ的网络交互流程：

![图片](https://static001.geekbang.org/resource/image/c3/b3/c340d40bd519295b10bf6f678d338db3.jpg?wh=1449x634)

**基于Netty进行网络编程，我们通常需要编写客户端代码、服务端代码和通信协议。**

我们先来看Netty客户端编程的通用示例：

![图片](https://static001.geekbang.org/resource/image/7c/d6/7cf85b0fb4cbc0d918d831e454488fd6.png?wh=1026x536)

这里我们需要注意五个关键点。

1. 需要创建Handler执行线程池，让IO线程只负责网络读写，而且创建线程池一定要使用线程工厂，同时要记得为线程命名。
2. 使用Bootstrap的Group方法指定Work线程组。
3. 通过Option方法设置网络参数。
4. 通过Handler方法创建事件调用链。
5. 将编码、解码、业务逻辑处理相关的事件处理器加入到事件执行链条。

再来看一下客户端如何创建连接，其代码片段如下：

![图片](https://static001.geekbang.org/resource/image/a5/ce/a5c5894e50c6a7e338d30ca6f93749ce.png?wh=1920x765)

客户端通过调用Bootstrap的connect方法尝试与服务端建立连接，该方法会立即返回一个Future而无须等待连接建立，所以该方法调用结束后并不一定成功创建了连接。但是连接只有在创建成功之后才能被用来发送和读取数据，所以这里我们需要再调用Future对象的awaitUninterruptibly方法等待连接成功建立。

客户端与服务端建立连接后，就可以通过连接向服务端发送请求了：

![图片](https://static001.geekbang.org/resource/image/0b/4a/0be5fc1365b53ec04434b392b549yy4a.png?wh=1920x1283)

这里主要有四个实现要点。

1. 为每一个请求创建一个唯一的请求序号。也就是为每一个请求创建一个响应结果Future，并建立RequestId到响应结果的映射Map，这样在收到服务端响应结果时，就可以准确地知道具体是哪一个请求的结果了。这是多线程共同使用单一连接发送请求的核心要点。为了更进一步理解，你可以再看一下这张示意图：

![图片](https://static001.geekbang.org/resource/image/74/52/74f03de29817d3cda8ce983dbb953552.jpg?wh=1920x571)

2. 通过调用Channel的writeAndFlush方法， **将数据写入到网络中。也就是说，不需要在发送数据之前先注册写事件。** 然后基于Future模式添加事件监听器，在收到返回结构后，ResponseFuture中的状态会被更新。
3. 同步发送的实现模板，通过调用ResponseFuture获取等待结果，如果使用异步发送模式，就在第三步执行用户定义的回调函数。
4. 处理完一个请求后，删除requestId-ResponseFuture的映射关系。

介绍完客户端编程范例后，接下来我们看一下如何使用Netty编写服务端程序。

首先，创建相关线程组，代码片段如下：

![图片](https://static001.geekbang.org/resource/image/db/ab/db5c63a641afab60fdb56185225546ab.png?wh=1233x737)

这里分别创建了3个线程组。

- eventLoopGroupBoss线程组，默认使用1个线程，对应Netty线程模型中的主Reactor。
- eventLoopGroupSelector线程组，对应Netty线程模型中的从Reactor组，俗称IO线程池。
- defaultEventExecutorGroup线程组，在Netty中，可以为编解码等事件处理器单独指定一个线程池，从而使IO线程只负责数据的读取与写入。

下一步，使用Netty提供的ServerBootstrap对象创建Netty服务端，示例代码如下所示：

![图片](https://static001.geekbang.org/resource/image/a0/43/a01ca20a4ff9bb8ea901d64225ef8043.png?wh=1253x509)

上面的代码基本都是模版代码，少数不同点就是需要自己实现编码器、解码器和业务处理Handler。其中，编码器、解码器其实就是实现通信协议，而ServerHandler就是服务端业务处理器。

再下一步，服务端在指定接口建立监听，等待客户端连接：

![图片](https://static001.geekbang.org/resource/image/6a/f7/6a9a5763e671c9512ea80dbbcab77df7.png?wh=944x193)

ServerBootstrap的bind方法是一个非阻塞方法，调用sync()方法会变成阻塞方法，它需要等待服务端启动完成。

最后一步就是编写服务端业务处理Handler了：

![图片](https://static001.geekbang.org/resource/image/73/2c/73a4383e93717b0813c62e490624b12c.png?wh=966x465)

服务端处理器需要接收客户端请求，所以通常需要实现channelRead事件。通常业务Handler是在解码器之后执行，所以业务Handler中channelRead方法接收到的参数已经是通信协议中定义的具体模型，也就是请求对象了。后面就是根据该请求对象中的内容，执行对应的业务逻辑了。业务Handler会在defaultEventExecutorGroup线程组中执行，为了提高解码的性能，避免业务逻辑与IO操作相互影响，通常会将业务执行派发到业务线程池。

## 总结

好了，这节课就讲到这里。

这节课，我们从一个简单的RPC请求-响应模式说起，串起了网络编程中编码、网络写、网络传输、网络读取、解码、业务逻辑执行等步骤，并引出了网络粘包问题，最终通过制定通信协议解决了粘包问题。

通信协议看似是一个非常高大上的名词，它其实是一种发送端和接收端共同制定的通信格式。我在这里介绍了一种通用的设计方法：Header(请求头) + Body（消息体）的经典设计方法。

接下来，我们还讲解了Netty的线程模型，也是主从多Reactor模型。但我们要知道业务Handler默认是在IO线程池中执行的，我们改变这种行为，让Handler在一个独立的线程池中执行，主要是为了提升IO线程的执行效率。

在讲解Netty读写流程之前，我给你提了下面几个问题。只有真正理解了这些问题，才能算是真正理解了NIO编程。在这里，我也给出我的答案，你可以对照思考一下。

- **如何处理连接半关闭？**


  在调用SocketChannel方法的read方法时，如果其返回值为-1，则表示对端已经关闭了连接，接受端也需要同样关闭连接，释放相关资源。
- **什么时候应该注册读事件？**


  接受端通常在创建好NioSocketChannel后就应该注册读事件。这样才能接受发送端的数据，如果服务端感觉到有压力时，可以暂时取消关注读事件，达到限流的效果。
- **写数据之前一定要先注册写事件吗？**


  写数据之前不需要注册写事件，写事件一般是底层NioSocketChannel的底层缓存区满了，无法再往网络中写入数据时，再注册通道的写事件，等待缓冲区空闲时通知应用程序继续将剩余数据写入到网络中。

在课程的最后，我们以消息中间件RocketMQ是如何使用Netty开发网络通信模块，进行Netty网络编程实战，做到理论与实践相结合。

Netty是一个庞大的体系，如果你想进一步提升高并发编程能力，我建议你体系化地学习一下它，我也非常推荐这本 [《Netty 源码分析与实战-网络通道篇》](https://www.aliyundrive.com/s/6CbWzmpFxbE)，希望可以让你在学习Netty的过程中少走一些弯路。

## 课后题

学完这节课，你应该已经掌握了NIO的读写处理过程，那我也给你留一道课后题。

请你尝试重构 [上节课](https://time.geekbang.org/column/article/532729) 的代码：实现一个简易的RPC Request-Response模型，确保这个模型支持同步请求、异步请求两种请求发送模式。

如果你想要分享你的代码想听听我的意见，可以提交一个 [GitHub](https://github.com/dingwpmz/infoq_question) 的push请求或issues，并把对应地址贴到留言里。我们下节课见！