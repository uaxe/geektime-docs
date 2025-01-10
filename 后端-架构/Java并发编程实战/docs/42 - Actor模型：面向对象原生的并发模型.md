上学的时候，有门计算机专业课叫做面向对象编程，学这门课的时候有个问题困扰了我很久，按照面向对象编程的理论，对象之间通信需要依靠 **消息**，而实际上，像C++、Java这些面向对象的语言，对象之间通信，依靠的是 **对象方法**。对象方法和过程语言里的函数本质上没有区别，有入参、有出参，思维方式很相似，使用起来都很简单。那面向对象理论里的消息是否就等价于面向对象语言里的对象方法呢？很长一段时间里，我都以为对象方法是面向对象理论中消息的一种实现，直到接触到Actor模型，才明白消息压根不是这个实现法。

## Hello Actor模型

Actor模型本质上是一种计算模型，基本的计算单元称为Actor，换言之， **在Actor模型中，所有的计算都是在Actor中执行的**。在面向对象编程里面，一切都是对象；在Actor模型里，一切都是Actor，并且Actor之间是完全隔离的，不会共享任何变量。

当看到“不共享任何变量”的时候，相信你一定会眼前一亮，并发问题的根源就在于共享变量，而Actor模型中Actor之间不共享变量，那用Actor模型解决并发问题，一定是相当顺手。的确是这样，所以很多人就把Actor模型定义为一种 **并发计算模型**。其实Actor模型早在1973年就被提出来了，只是直到最近几年才被广泛关注，一个主要原因就在于它是解决并发问题的利器，而最近几年随着多核处理器的发展，并发问题被推到了风口浪尖上。

但是Java语言本身并不支持Actor模型，所以如果你想在Java语言里使用Actor模型，就需要借助第三方类库，目前能完备地支持Actor模型而且比较成熟的类库就是 **Akka** 了。在详细介绍Actor模型之前，我们就先基于Akka写一个Hello World程序，让你对Actor模型先有个感官的印象。

在下面的示例代码中，我们首先创建了一个ActorSystem（Actor不能脱离ActorSystem存在）；之后创建了一个HelloActor，Akka中创建Actor并不是new一个对象出来，而是通过调用system.actorOf()方法创建的，该方法返回的是ActorRef，而不是HelloActor；最后通过调用ActorRef的tell()方法给HelloActor发送了一条消息 “Actor” 。

```
//该Actor当收到消息message后，
//会打印Hello message
static class HelloActor
    extends UntypedActor {
  @Override
  public void onReceive(Object message) {
    System.out.println("Hello " + message);
  }
}

public static void main(String[] args) {
  //创建Actor系统
  ActorSystem system = ActorSystem.create("HelloSystem");
  //创建HelloActor
  ActorRef helloActor =
    system.actorOf(Props.create(HelloActor.class));
  //发送消息给HelloActor
  helloActor.tell("Actor", ActorRef.noSender());
}

```

通过这个例子，你会发现Actor模型和面向对象编程契合度非常高，完全可以用Actor类比面向对象编程里面的对象，而且Actor之间的通信方式完美地遵守了消息机制，而不是通过对象方法来实现对象之间的通信。那Actor中的消息机制和面向对象语言里的对象方法有什么区别呢？

## 消息和对象方法的区别

在没有计算机的时代，异地的朋友往往是通过写信来交流感情的，但信件发出去之后，也许会在寄送过程中弄丢了，也有可能寄到后，对方一直没有时间写回信……这个时候都可以让邮局“背个锅”，不过无论如何，也不过是重写一封，生活继续。

Actor中的消息机制，就可以类比这现实世界里的写信。Actor内部有一个邮箱（Mailbox），接收到的消息都是先放到邮箱里，如果邮箱里有积压的消息，那么新收到的消息就不会马上得到处理，也正是因为Actor使用单线程处理消息，所以不会出现并发问题。你可以把Actor内部的工作模式想象成只有一个消费者线程的生产者-消费者模式。

所以，在Actor模型里，发送消息仅仅是把消息发出去而已，接收消息的Actor在接收到消息后，也不一定会立即处理，也就是说 **Actor中的消息机制完全是异步的**。而 **调用对象方法**，实际上是 **同步** 的，对象方法return之前，调用方会一直等待。

除此之外， **调用对象方法**，需要持有对象的引用， **所有的对象必须在同一个进程中**。而在Actor中发送消息，类似于现实中的写信，只需要知道对方的地址就可以， **发送消息和接收消息的Actor可以不在一个进程中，也可以不在同一台机器上**。因此，Actor模型不但适用于并发计算，还适用于分布式计算。

## Actor的规范化定义

通过上面的介绍，相信你应该已经对Actor有一个感官印象了，下面我们再来看看Actor规范化的定义是什么样的。Actor是一种基础的计算单元，具体来讲包括三部分能力，分别是：

1. 处理能力，处理接收到的消息。
2. 存储能力，Actor可以存储自己的内部状态，并且内部状态在不同Actor之间是绝对隔离的。
3. 通信能力，Actor可以和其他Actor之间通信。

当一个Actor接收的一条消息之后，这个Actor可以做以下三件事：

1. 创建更多的Actor；
2. 发消息给其他Actor；
3. 确定如何处理下一条消息。

其中前两条还是很好理解的，就是最后一条，该如何去理解呢？前面我们说过Actor具备存储能力，它有自己的内部状态，所以你也可以把Actor看作一个状态机，把Actor处理消息看作是触发状态机的状态变化；而状态机的变化往往要基于上一个状态，触发状态机发生变化的时刻，上一个状态必须是确定的，所以确定如何处理下一条消息，本质上不过是改变内部状态。

在多线程里面，由于可能存在竞态条件，所以根据当前状态确定如何处理下一条消息还是有难度的，需要使用各种同步工具，但在Actor模型里，由于是单线程处理，所以就不存在竞态条件问题了。

## 用Actor实现累加器

支持并发的累加器可能是最简单并且有代表性的并发问题了，可以基于互斥锁方案实现，也可以基于原子类实现，但今天我们要尝试用Actor来实现。

在下面的示例代码中，CounterActor内部持有累计值counter，当CounterActor接收到一个数值型的消息message时，就将累计值counter += message；但如果是其他类型的消息，则打印当前累计值counter。在main()方法中，我们启动了4个线程来执行累加操作。整个程序没有锁，也没有CAS，但是程序是线程安全的。

```
//累加器
static class CounterActor extends UntypedActor {
  private int counter = 0;
  @Override
  public void onReceive(Object message){
    //如果接收到的消息是数字类型，执行累加操作，
    //否则打印counter的值
    if (message instanceof Number) {
      counter += ((Number) message).intValue();
    } else {
      System.out.println(counter);
    }
  }
}
public static void main(String[] args) throws InterruptedException {
  //创建Actor系统
  ActorSystem system = ActorSystem.create("HelloSystem");
  //4个线程生产消息
  ExecutorService es = Executors.newFixedThreadPool(4);
  //创建CounterActor
  ActorRef counterActor =
    system.actorOf(Props.create(CounterActor.class));
  //生产4*100000个消息
  for (int i=0; i<4; i++) {
    es.execute(()->{
      for (int j=0; j<100000; j++) {
        counterActor.tell(1, ActorRef.noSender());
      }
    });
  }
  //关闭线程池
  es.shutdown();
  //等待CounterActor处理完所有消息
  Thread.sleep(1000);
  //打印结果
  counterActor.tell("", ActorRef.noSender());
  //关闭Actor系统
  system.shutdown();
}

```

## 总结

Actor模型是一种非常简单的计算模型，其中Actor是最基本的计算单元，Actor之间是通过消息进行通信。Actor与面向对象编程（OOP）中的对象匹配度非常高，在面向对象编程里，系统由类似于生物细胞那样的对象构成，对象之间也是通过消息进行通信，所以在面向对象语言里使用Actor模型基本上不会有违和感。

在Java领域，除了可以使用Akka来支持Actor模型外，还可以使用Vert.x，不过相对来说Vert.x更像是Actor模型的隐式实现，对应关系不像Akka那样明显，不过本质上也是一种Actor模型。

Actor可以创建新的Actor，这些Actor最终会呈现出一个树状结构，非常像现实世界里的组织结构，所以利用Actor模型来对程序进行建模，和现实世界的匹配度非常高。Actor模型和现实世界一样都是异步模型，理论上不保证消息百分百送达，也不保证消息送达的顺序和发送的顺序是一致的，甚至无法保证消息会被百分百处理。虽然实现Actor模型的厂商都在试图解决这些问题，但遗憾的是解决得并不完美，所以使用Actor模型也是有成本的。

欢迎在留言区与我分享你的想法，也欢迎你在留言区记录你的思考过程。感谢阅读，如果你觉得这篇文章对你有帮助的话，也欢迎把它分享给更多的朋友。