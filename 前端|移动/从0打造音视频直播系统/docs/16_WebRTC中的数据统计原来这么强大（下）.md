在 [上一篇文章](https://time.geekbang.org/column/article/118885) 中我向你介绍了 WebRTC 可以获得哪些统计信息，以及如何使用 RTCPeerConntction 对象的 getStats 方法获取想要的统计信息。

那本文我们在 [上一篇文章](https://time.geekbang.org/column/article/118885) 的基础之上，继续对 WebRTC 中的统计信息做进一步的讨论，了解它更为详细的内容。

## 再论 getStats

现在你已经非常清楚，通过 RTCPeerConnection 对象的 getStats 方法可以很轻松地获取到各种统计信息，比如发了多少包、收了多少包、丢了多少包，等等。但实际上对于收发包这块儿的统计还可以从其他方法获取到，即通过 **RTCRtpSender 的 getStats 方法和 RTCRtpReceiver 的 getStats 方法也能获取收发包的统计信息**。

也就是说，除了 RTCPeerConnection 对象有 getStats 方法外，RTCRtpSender 和 RTCRtpReceiver 对象也有 getStats 方法，只不过它们只能获取到与传输相关的统计信息，而RTCPeerConnection还可以获取到其他更多的统计信息。

下面我们就来看一下它们三者之间的区别：

- RTCPeerConnection 对象的 getStats 方法获取的是 **所有的统计信息**，除了收发包的统计信息外，还有候选者、证书、编解码器等其他类型的统计信息。
- RTCRtpSender对象的 getStats 方法只统计 **与发送相关** 的统计信息。
- RTCRtpReceiver对象的 getStats 方法则只统计 **与接收相关** 的统计信息。

通过上面的描述，我想你已经非常清楚 RTCPeerConnection 中的 getStats 方法是获取到所有的统计信息，而 RTCRtpSender 和 RTCRtpReceiver 对象中的 getStats 方法则分别统计的是发包、收包的统计信息。所以RTCPeerConnection 对象中的统计信息与 RTCRtpSender 和 RTCRtpReceiver 对象中的统计信息是 **整体与局部** 的关系。

下面咱们通过一段示例代码来详细看看它们之间的不同：

```
...
var pc = new RTCPeerConnection(null);
...

pc.getStats()
  .then( reports => { //得到相关的报告
    reports.forEach( report => { //遍历每个报告
      console.log(report);
    });
  }).catch( err=>{
    console.error(err);
  });

//从 PC 上获得 sender 对象
var sender = pc.getSenders()[0];

...

//调用sender的 getStats 方法
sender.getStats()
    .then(reports => { //得到相关的报告
        reports.forEach(report =>{ //遍历每个报告
            if(report.type === 'outbound-rtp'){ //如果是rtp输出流
            ....
            }
        }
     );
 ...

```

在上面的代码中生成了两段统计信息，一段是通过 RTCPeerConnection 对象的 getStats 方法获取到的，其结果如下：

![](https://static001.geekbang.org/resource/image/5c/61/5c6cdea557a8a3ec0208a2915d6a5461.png?wh=1142*567)

另一段是通过 RTCRtpSender 对象的 getStats 方法获取到的，其结果如下：

![](https://static001.geekbang.org/resource/image/21/24/212a2a9124f8b643755ee63a5bafca24.png?wh=1142*569)

通过对上面两幅图的对比你可以发现，RTCPeerConnection 对象的 getStats 方法获取到的统计信息明显要比 RTCRtpSender 对象的 getStats 方法获取到的信息多得多。这也证明了我们上面的结论，即 RTCPeerConnection 对象的 getStas 方法获取到的信息与 RTCRtpSender 对象的 getStats 方法获取的信息之间是 **整体与局部** 的关系。

## RTCStatsReport

我们通过 getStats API 可以获取到WebRTC各个层面的统计信息，它的返回值的类型是RTCStatsReport。

RTCStatsReport的结构如下：

```
interface RTCStatsReport {
  readonly maplike<DOMString, object>;
};

```

即 RTCStatsReport 中有一个Map，Map中的key是一个字符串，object是 RTCStats 的继承类。

RTCStats作为基类，它包括以下三个字段。

- id：对象的唯一标识，是一个字符串。
- timestamp：时间戳，用来标识该条Report是什么时间产生的。
- type：类型，是 RTCStatsType 类型，它是各种类型Report的基类。

而继承自 RTCStats 的子类就特别多了，下面我挑选其中的一些子类向你做下介绍。

**第一种，编解码器相关** 的统计信息，即RTCCodecStats。其类型定义如下：

```
dictionary RTCCodecStats : RTCStats {
             unsigned long payloadType; //数据负载类型
             RTCCodecType  codecType;   //编解码类型
             DOMString     transportId; //传输ID
             DOMString     mimeType;
             unsigned long clockRate;   //采样时钟频率
             unsigned long channels;    //声道数，主要用于音频
             DOMString     sdpFmtpLine;
             DOMString     implementation;
};

```

通过 RTCCodecStats 类型的统计信息，你就可以知道现在直播过程中都支持哪些类型的编解码器，如 AAC、OPUS、H264、VP8/VP9等等。

**第二种，输入RTP流相关** 的统计信息，即 RTCInboundRtpStreamStats。其类型定义如下：

```
dictionary RTCInboundRtpStreamStats : RTCReceivedRtpStreamStats {
            ...
             unsigned long        frameWidth;     //帧宽度
             unsigned long        frameHeight;    //帧高度
             double               framesPerSecond;//每秒帧数
             ...
             unsigned long long   bytesReceived;  //接收到的字节数
             ....
             unsigned long        packetsDuplicated; //重复的包数
             ...
             unsigned long        nackCount;         //丢包数
             ....
             double               jitterBufferDelay; //缓冲区延迟
             ....
             unsigned long        framesReceived;    //接收的帧数
             unsigned long        framesDropped;     //丢掉的帧数
             ...
            };

```

通过 RTCInboundRtpStreamStats 类型的统计信息，你就可以从中取出接收到字节数、包数、丢包数等信息了。

**第三种，输出RTP流相关** 的统计信息，即 RTCOutboundRtpStreamStats。其类型定义如下：

```
dictionary RTCOutboundRtpStreamStats : RTCSentRtpStreamStats {
             ...
             unsigned long long   retransmittedPacketsSent; //重传包数
             unsigned long long   retransmittedBytesSent; //重传字节数
             double               targetBitrate;  //目标码率
             ...
.
             unsigned long        frameWidth;  //帧的宽度
             unsigned long        frameHeight; //帧的高度
             double               framesPerSecond; //每秒帧数
             unsigned long        framesSent; //发送的总帧数
             ...
             unsigned long        nackCount; //丢包数
             ....
};

```

通过 RTCOutboundRtpStreamStats 类型的统计信息，你就可以从中得到目标码率、每秒发送的帧数、发送的总帧数等内容了。

在 WebRTC 1.0 规范中，一共定义了 17 种 RTCStats 类型的子类，这里我们就不一一进行说明了。关于这 17 种子类型，你可以到文末的参考中去查看。实际上，这个表格在 [上一篇文章](https://time.geekbang.org/column/article/118885) 中我已经向你做过介绍了，这里再重新温习一下。

若你对具体细节很感兴趣的话，可以通过《WebRTC1.0规范》去查看每个 RTCStats 的详细定义， [相关链接在这里](https://w3c.github.io/webrtc-stats/#rtctatstype-*)。

## RTCP 交换统计信息

在 [上一篇文章](https://time.geekbang.org/column/article/118885) 中，我给你留了一道思考题，不知你是否已经找到答案了？实际上在WebRTC中，上面介绍的输入/输出RTP流报告中的统计数据都是通过 RTCP 协议中的 SR、RR 消息计算而来的。

关于 RTCP 以及 RTCP 中的 SR、 RR 等相关协议内容记不清的同学可以再重新回顾一下 [《 06 \| WebRTC中的RTP及RTCP详解》](https://time.geekbang.org/column/article/109999) 一文的内容。

在RTCP协议中，SR 是发送方发的，记录的是RTP流从发送到现在一共发了多少包、发送了多少字节数据，以及丢包率是多少。RR是接收方发的，记录的是RTP流从接收到现在一共收了多少包、多少字节的数据等。

通过 SR、RR 的不断交换，在通讯的双方就很容易计算出每秒钟的传输速率、丢包率等统计信息了。

**在使用 RTCP 交换信息时有一个主要原则，就是 RTCP 信息包在整个数据流的传输中占带宽的百分比不应超过 5%**。也就是说你的媒体包发送得越多，RTCP信息包发送得也就越多。你的媒体包发得少，RTCP包也会相应减少，它们是一个联动关系。

## 绘制图形

通过 getStats 方法我们现在可以获取到各种类型的统计数据了，而且在上面的 **RTCP交换统计信息** 中，我们也知道了 WebRTC 底层是如何获取到传输相关的统计数据的了，那么接下来我们再来看一下如何利用 RTCStatsReport 中的信息来绘制出各种分析图形，从而使监控的数据更加直观地展示出来。

在本文的例子中，我们以绘制每秒钟发送的比特率和每秒钟发送的包数为例，向你展示如何将 RTCStats 信息转化为图形。

要将 Report 转化为图形大体上分为以下几个步骤：

- 引入第三方库 graph.js；
- 启动一个定时器，每秒钟绘制一次图形；
- 在定时器的回调函数中，读取 RTCStats 统计信息，转化为可量化参数，并将其传给 graph.js进行绘制。

了解了上面的步骤后，下来我们就来实操一下吧！

第三方库 graph.js 是由 WebRTC 项目组开发的，是专门用于绘制各种图形的，它底层是通过 Canvas 来实现的。这个库非常短小，只有 600 多行代码，使用起来也非常方便，在下面的代码中会对它的使用做详细的介绍。

另外，该库的代码链接我已经放到了文章的末尾，供你参考。

### 1\. 引入第三方库

在 JavaScript 中引入第三方库也非常简单，只要使用 `<script>` 就可以将第三方库引入进来了。具体代码如下：

```
<html>
  ...
  <body>
  ...
  <script src="js/client.js"></script>

  //引入第三方库 graph.js
  <script src="js/third_party/graph.js"></script>
  ...
  </body>
</html>

```

### 2\. client.js 代码的实现

client.js是绘制图形的核心代码，具体代码如下所示：

```
...

var pc = null;

//定义绘制比特率图形相关的变量
var bitrateGraph;
var bitrateSeries;

//定义绘制发送包图形相关的变理
var packetGraph;
var packetSeries;
...

pc = new RTCPeerConnection(null);

...

//bitrateSeries用于绘制点
bitrateSeries = new TimelineDataSeries();
//bitrateGraph用于将bitrateSeries绘制的点展示出来
bitrateGraph = new TimelineGraphView('bitrateGraph', 'bitrateCanvas');
bitrateGraph.updateEndDate(); //绘制时间轴

//与上面一样，只不是用于绘制包相关的图
packetSeries = new TimelineDataSeries();
packetGraph = new TimelineGraphView('packetGraph', 'packetCanvas');
packetGraph.updateEndDate();

...

//每秒钟获取一次 Report，并更新图形
window.setInterval(() => {

  if (!pc) { //如果 pc 没有创建直接返回
    return;
  }

  //从 pc 中获取发送者对象
  const sender = pc.getSenders()[0];
  if (!sender) {
    return;
  }

  sender.getStats().then(res => { //获取到所有的 Report
    res.forEach(report => { //遍历每个 Report
      let bytes;
      let packets;

      //我们只对 outbound-rtp 型的 Report 做处理
      if (report.type === 'outbound-rtp') {
        if (report.isRemote) { //只对本地的做处理
          return;
        }

        const now = report.timestamp;
        bytes = report.bytesSent; //获取到发送的字节
        packets = report.packetsSent; //获取到发送的包数

        //因为计算的是每秒与上一秒的数据的对比，所以这里要做个判断
        //如果是第一次就不进行绘制
        if (lastResult && lastResult.has(report.id)) {

          //计算这一秒与上一秒之间发送数据的差值
          var mybytes= (bytes - lastResult.get(report.id).bytesSent);
          //计算走过的时间，因为定时器是秒级的，而时间戳是豪秒级的
          var mytime = (now - lastResult.get(report.id).timestamp);
          const bitrate = 8 * mybytes / mytime * 1000; //将数据转成比特位

          //绘制点
          bitrateSeries.addPoint(now, bitrate);
          //将会制的数据显示出来
          bitrateGraph.setDataSeries([bitrateSeries]);
          bitrateGraph.updateEndDate();//更新时间

          //下面是与包相关的绘制
          packetSeries.addPoint(now, packets -
                               lastResult.get(report.id).packetsSent);
          packetGraph.setDataSeries([packetSeries]);
          packetGraph.updateEndDate();
        }
      }
    });

    //记录上一次的报告
    lastResult = res;

  });

}, 1000); //每秒钟触发一次

...

```

在该代码中，最重要的是32～89行的代码，因为这其中实现了一个定时器——每秒钟执行一次。每次定时器被触发时，都会调用sender 的 getStats 方法获取与传输相关的统计信息。

然后对获取到的 RTCStats 类型做判断，只取 RTCStats 类型为 outbound-rtp 的统计信息。最后将本次统计信息的数据与上一次信息的数据做差值，从而得到它们之间的增量，并将增量绘制出来。

### 3\. 最终的结果

当运行上面的代码时，会绘制出下面的结果，这样看起来就一目了然了。通过这张图你可以看到，当时发送端的码率为 1.5Mbps的带宽，每秒差不多发送小200个数据包。

![](https://static001.geekbang.org/resource/image/47/ca/4766d46db9b8c3aaece83a403f0e07ca.png?wh=1142*336)

## 小结

在本文中，我首先向你介绍了除了可以通过 RTCPeerConnection 对象的 getStats 方法获取到各种统计信息之外，还可以通过 RTCRtpSender 或 RTCRtpReceiver 的 getStats 方法获得与传输相关的统计信息。WebRTC对这些统计信息做了非常细致的分类，按类型可细分为 17 种，关于这 17 种类型你可以查看文末参考中的表格。

在文中我还向你重点介绍了 **编解码器、输入RTP流** 以及 **输出RTP流** 相关的统计信息。

除此之外，在文中我还向你介绍了 **网络传输** 相关的统计信息是如何获得的，即通过 RTCP 协议中的 SR 和 RR 消息进行交换而来的。实际上，对于 RTCP 的知识我在前面 [《06 \| WebRTC中的RTP及RTCP详解》](https://time.geekbang.org/column/article/109999) 一文中已经向你讲解过了，而本文所讲的内容则是 RTCP 协议的具体应用。

最后，我们通过使用第三方库 graph.js 与 getStats 方法结合，就可以将统计信息以图形的方式绘制出来，使你可以清晰地看出这些报告真正表达的意思。

## 思考时间

今天你要思考的问题是：当使用 RTCP 交换 SR/RR 信息时，如果 SR/RR包丢失了，会不会影响数据的准确性呢？为什么呢？

欢迎在留言区与我分享你的想法，也欢迎你在留言区记录你的思考过程。感谢阅读，如果你觉得这篇文章对你有帮助的话，也欢迎把它分享给更多的朋友。

## 参考

![](https://static001.geekbang.org/resource/image/72/93/72b638952a9e9d0440e9efdb4e2f4493.png?wh=1142*1158)

[例子代码地址，戳这里](https://github.com/avdance/webrtc_web/tree/master/16_getstat/getstats)

[第三方库地址，戳这里](https://github.com/avdance/webrtc_web/tree/master/16_getstat/getstats/js/third_party)