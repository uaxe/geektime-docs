你好，我是文强。上节课我们讲了生产端，这节课我们来讲讲消费端。

从技术上看，消费端SDK和生产端SDK一样，主要包括客户端基础功能和消费相关功能两部分。客户端基础功能在上一节讲过，我们就不再重复。

从实现来看，消费相关功能包括**消费模型**、**分区消费模式**、**消费分组（订阅）**、**消费确认**、**消费失败处理**五个部分。内容比较多，所以本节课我们将会聚焦消费模型的选择和分区消费模式设计这两个部分，下节课会继续完成剩下三个部分的讲解。

## 消费模型的选择

为了满足不同场景的业务需求，从实现机制上来看，主流消息队列一般支持 Pull、Push、Pop 三种消费模型。

### Pull 模型

Pull（拉）模型是指客户端通过不断轮询的方式向服务端拉取数据。它是消息队列中使用最广泛和最基本的模型，主流的消息队列都支持这个模型。

![](https://static001.geekbang.org/resource/image/f8/b9/f8cb7308f06113f96b53bbc1f986d2b9.jpg?wh=10666x3070)

它的好处是客户端根据自身的处理速度去拉取数据，不会对客户端和服务端造成额外的风险和负载压力。缺点是可能会出现大量无效返回的Pull调用，另外消费及时性不够，无法满足一些需要全链路低耗时的场景。

为了提高消费性能，Pull模型都会支持批量读，即**在客户端指定需要拉取多少条数据或者拉取多大的数据**，然后传递给服务端。客户端拉取到数据并处理完成后，再重复拉取数据处理。如前面讲的，这种拉取模式的缺点是可能会出现长时间轮询到空数据的情况，从而浪费通信资源，提高服务端的负载。

来看下图的场景，当Topic1数据已经被消费完，此时如果消费者频繁来拉取数据并立即返回结果，客户端就会不停地重复请求服务端。当空数据请求特别多的时候，就会造成资源损耗，不利于提高吞吐，也有可能导致负载问题。

![](https://static001.geekbang.org/resource/image/d1/d8/d13569ac0196a12bbd9d05e812c987d8.jpg?wh=10666x6000)

为了解决这个问题，正常的思路是在客户端根据一定策略进行等待和回避。这样做的话，就会出现如何设置等待时间的问题，客户端等待时间设置不合理就会出现消费不及时的情况。

所以为了解决空请求带来的问题，一般服务端会协助处理，有如下两个思路。

**1. 服务端hold住请求**

当客户端根据策略拉取数据时，如果没有足够的数据，就先在服务端等一段时间，等有数据后一起返回给客户端。这种方案的好处是，可以尽量提高吞吐能力，不会有太多的空交互请求。缺点是如果长时间不给客户端回包，会导致客户端请求超时，另外当数据不够时，hold住请求的时间太长就会提高消费延时。

**2. 服务端有数据的时候通知客户端**

当服务端不hold住请求，立刻返回空数据，客户端收到空数据时则不再发起请求，会等待服务端的通知。当服务端有数据的时候，再主动通知客户端来拉取。这种方案的好处是可以及时通知客户端来拉取数据，从而降低消费延时。缺点是因为客户端和服务端一般是半双工的通信，此时服务端是不能主动向客户端发送消息的。

所以在 Pull 模型中，比较合适的方案是客户端告诉服务端：**最多需要多少数据、最少需要多少数据、未达到最小数据时可以等多久**三个信息。然后服务端首先判断是否有足够的数据，有的话就立即返回，否则就根据客户端设置的等待时长hold住请求，如果超时，无论是否有数据，都会直接给客户端返回当前的结果。

这种策略可以解决频繁不可控的空轮询请求。即使全是空轮询，对单个消费者来说，其TPS也是可以预估的，即总时间/等待时长 = 总轮询次数。而如果需要降低消费延时，可以通过降低最小获取的数据大小和最大等待时长来提高获取的频率，从而尽量降低延时。通过这种方案，我们可以把理想的消费延迟时间降低到两次Pull请求之间的时间间隔。

在一些业务消息的场景中，因为应对的场景规模有限，可以将最大等待时长设置为0，此时消费模型就变成了请求-返回的模式，当没数据的时候就会立即返回数据，其余逻辑交给客户端自己处理。

### Push 模型

Push（推）模型是为了解决消费及时性而提出来的。这个模型的本意是指当服务端有数据时会主动推给客户端，让数据的消费更加及时。理想中的思路如下图所示，即当服务端有数据以后，会主动推动给各个消费者。这个思路是非常好的，随着事件模型的发展，为了解决消费的及时性，很多消息队列都希望支持Push模型。

![](https://static001.geekbang.org/resource/image/d2/12/d287737b178a9a6fd61c27a24b0db512.jpg?wh=10666x6000)

在实际的Push模型的实现上，一般有 Broker 内置 Push 功能、Broker 外独立实现 Push 功能的组件、在客户端实现伪 Push 功能三种思路。

**第一种，Broker** **内置** **Push** **功能是指在Broker中内置标准的** **Push** **的能力，由服务端向客户端主动推送数据。**

![](https://static001.geekbang.org/resource/image/22/05/2220e23cba67a3e392b48c02c3462505.jpg?wh=10666x6000)

这种方案的好处是Broker自带Push能力，无需重复开发和部署。Broker 内部可以感知到数据堆积情况，可以保证消息被及时消费。缺点是当消费者很多时，内核需要主动维护很多与第三方的长连接，并且需要处理各种客户端异常，比如客户端卡住、接收慢、处理慢等情况。这些推送数据、异常处理、连接维护等工作需要消耗很多的系统资源，在性能上容易对Broker形成反压，导致Broker本身的性能和稳定性出现问题。

所以这种方案在主流消息队列中用得较少，比如RabbitMQ和某些金融证券领域的消息队列，为了保证消息投递的高效及时（比如全链路的毫秒级耗时），才会采用这种方案。

**第二种，Broker外独立实现Push功能的组件是指独立于Broker提供一个专门实现推模型的组件。**通过先 Pull 数据，再将数据 Push 给客户端，从而简化客户端的使用，提高数据消费的及时性。

![](https://static001.geekbang.org/resource/image/6d/3b/6db5181a1714e327c375de7eae4a293b.jpg?wh=10666x6000)

这种方案的好处是将Push组件独立部署，解决了 Broker 的性能和稳定性问题，也能实现Push的效果。缺点是虽然实现了Push的模型，但其本质还是先Pull再Push，从全链路来看，还是会存在延时较高的问题，并且需要单独开发独立的 Push 组件，开发和运维成本较高。

从实际业务上来讲，这种模型的使用场景较为有限，主要用在回调、事件触发的场景，在实际的流消费场景中用得较少。主要是因为通过第三方组件的Push灵活性不够，性能会比Pull低。

**第三种，在客户端实现伪Push功能是指在客户端内部维护内存队列，SDK 底层通过Pull模型从服务端拉取数据存储到客户端的内存队列中。**然后通过回调的方式，触发用户设置的回调函数，将数据推送给应用程序，在使用体验上看就是 Push 的效果。

![](https://static001.geekbang.org/resource/image/06/b1/06ed827d2681386d9cef461d7a5ee7b1.jpg?wh=10666x6000)

这种方案的好处在于通过客户端底层的封装，从用户体验看是Push模型的效果，解决用户代码层面的不断轮询问题，降低了用户的使用复杂度。缺点是底层依旧是Pull模型，还是得通过不断轮询的方式去服务端拉取数据，就会遇到 Pull 模型遇到的问题。

在客户端实现伪Push，是目前消息队列在实现Push模型上常用的实现方案，因为它解决了客户体验上的主动回调触发消费问题。虽然底层会有不断轮询和消费延时的缺点，但是可以通过编码技巧来降低这两个问题的影响。

因为Push模型需要先分配分区和消费者的关系，客户端就需要感知分区分配、分区均衡等操作，从而在客户端就需要实现比较重的逻辑。并且当客户端和订阅的分区数较多时，容易出现需要很长的重平衡时间的情况。此时为了解决这个问题，业界提出了Pop模型。

### Pop模型

Pop模型想解决的是客户端实现较重，重平衡会暂停消费并且可能时间较长，从而出现消费倾斜的问题。

它的思路是客户端不需要感知到分区，直接通过Pop模型提供的get接口去获取到数据，消费成功后ACK数据。就跟我们发起HTTP请求去服务端拉取数据一样，不感知服务端的数据分布情况，只需要拉到数据。这种方案的好处是简化了消费模型，同时服务端可以感知到消费的堆积情况，可以根据堆积情况返回那些分区的数据给客户端，这样也简化了消息数据的分配策略。

从实现上来看，它将分区分配的工作移到了服务端，在服务端完成了消费者的分区分配、进度管理，然后暴露出了新的Pop和ACK接口。客户端调用Pop接口去拿取数据，消费成功后调用ACK去确认数据。这和 HTTP 的 Request 和 Response 的使用模型一致。

![](https://static001.geekbang.org/resource/image/7f/45/7f6f8e8603b1c9af0c594ec3b954c845.jpg?wh=10666x6000)

## 分区消费模式的设计

我们知道，消息队列的数据是在Partition/Queue维度承载的。所以消费过程中一个重要的工作就是消费者和分区的消费模式问题，即分区的数据能不能被多个消费者并发消费，一条数据能不能被所有消费者消费到，分区的数据能不能被顺序消费等等。

从技术上看，在数据的消费模式上主要有独占消费、共享消费、广播消费、灾备消费四个思路。

**独占消费是指一个分区在同一个时间只能被一个消费者消费。**在消费者启动时，会分配消费者和分区之间的消费关系。当消费者数量和分区数量都没有变化的情况下，两者之间的分配关系不会变动。当分配关系变动时，一个分组也只能被一个消费者消费，这个消费者可能是当前的，也可能是新的。如果消费者数量大于分区数量，则会有消费者被空置；反之，如果分区数量大于消费者数量，一个消费者则可以同时消费多个分区。

![](https://static001.geekbang.org/resource/image/e1/8d/e1996c88f34fe02a23c65ce487e89b8d.jpg?wh=10666x6000)

独占消费的好处是可以保证分区维度的消费是有序的。缺点是当数据出现倾斜、单个消费者出现性能问题或hang住时，会导致有些分区堆积严重。现在大部分消息队列默认支持的就是独占消费的类型，比如Kafka、RocketMQ、Pulsar等。

**共享消费是指单个分区的数据可以同时被多个消费者消费。**即分区的数据会依次投递给不同的消费者，一条数据只会投递给一个消费者。

![](https://static001.geekbang.org/resource/image/2b/5b/2b565d4a50802225d74c0b7f4304ef5b.jpg?wh=10666x6000)

这种方式的好处是，可以避免单个消费者的性能和稳定性问题导致分区的数据堆积。缺点是无法保证数据的顺序消费。这种模式一般用在对数据的有序性无要求的场景，比如日志。

**广播消费是指一条数据要能够被多个消费者消费到。**即分区中的一条数据可以投递给所有的消费者，这种方式是需要广播消费的场景。

![](https://static001.geekbang.org/resource/image/bb/cb/bb2b39c0762baaa2283438b280caa2cb.jpg?wh=10666x6000)

实现广播消费一般有内核实现广播消费的模型、使用不同的消费分组消费和指定分区消费三种技术思路。

1. 内核实现广播消费的模型，指在Broker内核中的消息投递流程实现广播消费模式，即 Broker 投递消息时，可以将一条消息吐给不同的消费者，从而实现广播消费。
2. 使用不同的消费分组对数据进行消费，指通过创建不同的消费者组消费同一个Topic或分区，不同的消费分组管理自己的消费进度，消费到同一条消息，从而实现广播消费的效果。
3. 指定分区消费，是指每个消费者指定分区进行消费，在本地记录消费位点，从而实现不同消费者消费同一条数据，达到广播消费的效果。

三种方案的优劣对比如下：![](https://static001.geekbang.org/resource/image/f5/92/f59f74ff20f77192c9f6b50abc5d6c92.jpg?wh=1484x458)在常见的消息队列产品中，Pulsar支持的Share消费模型就是第一种实现思路。Kafka和RocketMQ主要支持第二和第三种实现思路。

**灾备消费是独占消费的升级版，在保持独占消费可以支持顺序消费的基础上，同时加入灾备的消费者。**当消费者出现问题的时候，灾备消费者加入工作，继续保持独占顺序消费。

好处是既能保持独占顺序消费，又能保证容灾能力。缺点是无法解决消费倾斜的性能问题，另外还需要准备一个消费者来做灾备，使用成本较高。

![](https://static001.geekbang.org/resource/image/24/88/24c795441bd156a1b6bd1a99d312c388.jpg?wh=10666x6000)

业界还有一些其他用得比较少的消费模式，如果你有兴趣，可以去研究一下各个主流消息队列（如 Kafka、RocketMQ、Pulsar等）的实现。

## 总结

在消费端，为了提高消费速度和消息投递的及时性，需要选择合适的消费模型，目前主流有Pull、Push、Pop三种模型。

这三种模型的应用场景都不一样。目前业界主流消息队列使用的都是Pull模型。但为了满足业务需求，很多消息队列也会支持Push模型和Pop模型。其中，Push模型的及时性更高，实现较为复杂，限制较多。Pop模型本质上是Pull模型的一种，只是在实现和功能层面上，与Pull的实现思路和适用场景不一样。所以在模型的选择上来看，因为场景复杂，三种模型都是需要的。

常用的消费模式一般有独占消费、共享消费、广播消费、灾备消费四种**。**为了避免堆积，保证消息消费顺序，一般需要选择分区独占的消费模式。从单分区的维度，共享消费的性能是最高的。广播消费主要是通过创建多个消费分组、指定分区消费来实现的。灾备消费的场景用得相对较少。

## 思考题

当Topic的消息写入存在倾斜，某些分区消息堆积很多，此时选择哪种分区消费模式可以解决问题？

欢迎分享你的思考，如果觉得有收获，也欢迎你把这节课分享给身边的朋友。我们下节课再见！

## 上节课思考闭环

假设让你从头开始写一个消息队列的某个语言的SDK，思考步骤是怎样的？

1\. 思考客户端的模块组成，比如我们总结部分说到的三层结构。

2\. 参考服务端网络模块的实现，进行客户端网络模块的选型开发，比如使用Netty Client或者Java Socket Client，然后完成连接管理、心跳检测等网路模块的开发工作。

3\. 了解这个消息队列的协议设计的内容，各个接口的请求和返回的协议是什么样子的。

4\. 思考如何构建请求，实现构建各个请求相关的逻辑代码实现。

5\. 思考序列化模块怎么实现。

6\. 完成第一个接口的请求和返回的处理。

7\. 根据各个接口的调用参数进行开发。

8\. 如果需要支持SSL，就去参考这个语言官方的SSL CLient配置，然后编码实现，其他比如压缩的支持也是类似。
<div><strong>精选留言（15）</strong></div><ul>
<li><span>文敦复</span> 👍（3） 💬（1）<p>文中的“因为 Push 模型需要先分配分区和消费者的关系，客户端就需要感知分区分配、分区均衡等操作，从而在客户端就需要实现比较重的逻辑。” 这里的Push模型指的提到的第三种“伪Push模式”吧？</p>2023-07-07</li><br/><li><span>文敦复</span> 👍（2） 💬（2）<p>文中提到“实现广播消费一般有内核实现广播消费的模型、使用不同的消费分组消费和指定分区消费三种技术思路。”关于最后一种广播消息指定分区进行消费没搞清楚：为什么指定分区消费可以做到广播消费的效果？1个Topic会分成多个分区，所有分区合起来才的整体才是的所有消息？如果客户端指定分区消费不就只能消费其中一部分吗？</p>2023-07-07</li><br/><li><span>张申傲</span> 👍（1） 💬（1）<p>思考题：当 Topic 的消息写入存在倾斜，某些分区消息堆积很多，此时可以选择【共享消费】模式，给该 Partition 下挂多个 Consumer 来提升消费吞吐量，快速处理掉积压的消息。
小建议：这里【共享消费】这个说法个人感觉有点歧义，容易和【广播消费】产生混淆，是不是叫做【负载均衡消费】更直观一点？</p>2023-07-07</li><br/><li><span>cykuo</span> 👍（1） 💬（1）<p>先回答问题：pop模型却可以根据积压情况动态调整消费分区，一定程度上可以解决写入倾斜问题。</p>2023-07-07</li><br/><li><span>虚竹</span> 👍（0） 💬（2）<p>老师好，关于共享消费模型，或者叫消息粒度负载均衡，假设一个消费者组有 a b c 共3个具体消费者，假设b未返回消费状态，a c是不受影响可以继续往后消费吗？ 这样的话，该消费者组到底消费到队列的哪个位置了是不是就有点乱了？这个问题是怎么解决的呢？</p>2023-10-10</li><br/><li><span>Geek4329</span> 👍（0） 💬（1）<p>“Pop 模型本质上是 Pull 模型的一种，只是在实现和功能层面上，与 Push 的实现思路和适用场景不一样。”这句话怎么理解呢？前半句讲pop跟pull的关系，后半句又讲pop跟push的关系</p>2023-10-09</li><br/><li><span>jackfan</span> 👍（0） 💬（1）<p>独占是一个分区只能给一个消费者，共享是一个分区的消息给多个消费者，并且一条消息不会给多个消费者，广播是一个消费会被多个消费者消费，灾备也是独占消费。所以这里需要选择共享消费</p>2023-07-13</li><br/><li><span>Johar</span> 👍（0） 💬（1）<p>共享消费模型可以解决分区消息堆积问题</p>2023-07-07</li><br/><li><span>Geek_f6zh7v</span> 👍（1） 💬（0）<p>pulsar 的 Key_Shared模式。多个消费者，可以保证单个key发送给同一个消费者，保证局部有序。</p>2023-07-11</li><br/><li><span>Geek_4386bc</span> 👍（0） 💬（0）<p>独占消费那个图是不是画错了，怎么全是partition1</p>2024-08-25</li><br/><li><span>shan</span> 👍（0） 💬（1）<p>1. Pull模型
客户端不断轮询的方式向服务端拉取消息。优点是客户端可以根据自身处理速度区拉取数据，缺点没有消息消费时，可能会出现大量无效的调用。

2. Push模型
指服务端有数据时会主动推送给客户端，一般有Broker内置Push功能、Broker独立实现Push组件、客户端实现伪Push功能。
（1）内置Push功能
在Broker中内置标准的Push功能，服务端想客户端主动推送数据。优点是自带推送功能，不需要重复开发和部署，缺点是消费者很多时，维护较多长链接，引起Broker性能和稳定性。

（2）独立实现Push组件
独立于Broker提供一个专门实现推送功能的组件。优点是独立部署，解决了Broker的性能问题，缺点是本质还是需要从服务端Pull数据再Push给客户端，并且独立部署开发运维成本高。

（3）客户端实现伪Push
客户端内部，底层通过Pull模型先从服务端拉取数据，在通过回调的方式触发回调函数推送消息进行消费，这种方案依旧是Pull模型，需要不断轮询向服务器请求数据。

RocketMQ在5.0之前有Pull和Push两种方式（客户端实现伪Push），对于Pull模式，消费者需要不断向Broker发送拉取消息的请求，拉取消息后会将消息放入一个阻塞队列中，主线程开启循环不断从这个阻塞队列中获取拉取到的消息进行消费。
对于Push模式，本质依旧就是通过Pull的方式拉取数据，只不过不需要开启循环不断从队列中读取数据，而且拉取到消息之后，会触发回调函数进行消息消费，从表面上看就像是Broker主动推送给消费者一样，所以是伪Push。
不管Push模式还是Pull模式，RocketMQ都需要在消费者端进行负载均衡，为消费者分配对应的消息队列，之后才可以向Broker发送请求从队列中拉取消息。

3. Pop模型
Push模型需要在消费者端做负载均衡分配分区&#47;消息队列，如果负载均衡时间过长会影响消费者消费，为了解决这个问题，推出了Pop模型，不再将分区&#47;消息队列与消费者绑定，消费者只需按Pop模型提供的接口去获取消息内容即可，不再感知数据的分布情况。

RocketMQ 5.0的Pop模型，消费者不需要再进行负载均衡，MessageQueue也不与消费者绑定，消费者只需调用服务端提供的接口获取消息进行消费并确认即可，并且Pop模型可以实现消息粒度的分配，在5.0之前只能基于消息队列进行分配。</p>2023-09-23</li><br/><li><span>TKF</span> 👍（0） 💬（0）<p>老师，文中的广播消费的实现思路部分，“在常见的消息队列产品中，Pulsar 支持的 Share 消费模型就是第一种实现思路。Kafka 和 RocketMQ 主要支持第二和第三种实现思路。”，RocketMQ是第一种思路，Pulsar和Kafka都是第二种思路吧？</p>2023-08-15</li><br/><li><span>张洋</span> 👍（0） 💬（0）<p>共享消费、灾备消费都有可能解决：
消费者本身并无问题的情况，使用共享消费，针对于堆积比较严重的分区，增加多个消费者加速消费
如果仅仅是该分区对应的消费者本身出现问题，使用灾备消费，出现问题，及时切换备用消费者去处理。</p>2023-07-19</li><br/><li><span>贝氏倭狐猴</span> 👍（0） 💬（0）<p>老师您好，关于pop模型能否深入讲解下，不太明白具体实现方法</p>2023-07-08</li><br/><li><span>cykuo</span> 👍（0） 💬（0）<p>Pop 模型本质上是 Pull 模型的一种，只是在实现和功能层面上，与 Push 的实现思路和适用场景不一样。所以在模型的选择上来看，因为场景复杂，三种模型都是需要的。这句话不是特别的通顺…不知是不是自己理解的有问题</p>2023-07-07</li><br/>
</ul>