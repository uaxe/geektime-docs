RTCPeerConnection 类是在浏览器下使用 WebRTC 实现1对1实时互动音视频系统最核心的类。你可以认为它是一个总的接口类或者称它为聚合类，而该类中实现的很多功能都是由其他类具体实现的。

像我前面讲的很多文章，都是 RTCPeerConnection 类的一部分功能，如 ：

- [《06 \| WebRTC中的RTP及RTCP详解》](https://time.geekbang.org/column/article/109999) 讲的是底层网络数据传输协议与其控制协议。
- [《07 \| 你竟然不知道SDP？它可是WebRTC的驱动核心！》](https://time.geekbang.org/column/article/111337) 和 [《08 \| 有话好商量，论媒体协商》](https://time.geekbang.org/column/article/111675) 讲的是 SDP 协议及使用SDP协议进行媒体协商的过程等。
- [《09 \| 让我们揭开WebRTC建立连接的神秘面纱》](https://time.geekbang.org/column/article/112325) 讲的是 WebRTC 底层是如何建立连接的。
- [《10 \| WebRTC NAT穿越原理》](https://time.geekbang.org/column/article/113560) 介绍了在 WebRTC 底层进行 NAT 穿越的过程。

以上这些内容都是 RTCPeerConnection 类的功能。除了上述讲的这些内容之外，RTCPeerConnection类还有许多其他的功能，我在后面的文章中还会向你逐一介绍。

RTPPeerConnection 这个知识点是你掌握 WebRTC 开发的重中之重，抓住它你就抓住了学习 WebRTC 的钥匙（这里你一定要清楚， **SDP 是掌握WebRTC运行机制的钥匙，而RTCPeerConnection是使用 WebRTC 的钥匙**），这样可以让你很快学会 WebRTC 的使用。

## 在WebRTC处理过程中的位置

还是老规矩，我们先来看一下本文在整个 WebRTC处理过程中的位置。

![](https://static001.geekbang.org/resource/image/0b/c5/0b56e03ae1ba9bf71da6511e8ffe9bc5.png?wh=1142*481)

WebRTC处理过程图

通过上面这张图，你可以看到本文所要讲述的内容就是两个端点之间是如何通过 RTCPeerConnection 创建连接的。

## 传输要做哪些事儿

可以想像一下，如果你自己要实现一套1对1的通话系统，你会怎么做呢？如果你有一些socket开发经验的话，我想你首先会想到在每一端创建一个 socket，然后通过该 socket 与对端相连。

当 socket 连接成功之后，你就可以通过 socket 向对端发送数据或者接收对端的数据了。这个过程是不是看起来还是蛮简单的呢？实际上， **RTCPeerConnection 类的工作原理与socket 基本是一样的**，不过它的功能更强大，实现也更为复杂。因为它有很多细节需要处理，这里我们从“提问题”的角度出发，反向分析，你就知道 RTCPeerConnection 要处理哪些细节了。

- 端与端之间要建立连接，但它们是如何知道彼此的外网地址呢？
- 如果两台主机都是在 NAT 之后，它们又是如何穿越 NAT 进行连接的呢？
- 如果 NAT 穿越不成功，又该如何保证双方之间的连通性呢？
- 好不容易双方连通了，如果突然丢包了，该怎么办？
- 如果传输过程中，传输的数据量过大，超过了网络带宽能够承受的负载，又该如何保障音视频的服务质量呢？
- 传输的音视频要时刻保持同步，这又该如何做到呢？
- 数据在传输之前要进行音视频编码，而在接收之后又要做音视频解码，但WebRTC支持那么多编解码器，如 H264､ H265､ VP8､ VP9等，它是如何选择的呢？
- ……

如果不是篇幅有限，我可以一直问下去哈，从中你也可以看出RTCPeerConnection要处理多少事情了。通过这些描述，我想你也清楚，这就是原理与真正的实际工作之间还差着十万八千里的距离呢。不过原理的好处是可以帮你简化问题，方便发现问题的本质。

## 什么是RTCPeerConnection

了解了传输都要做哪些事之后，你再理解什么是 RTCPeerConnection 就比较容易了。实际上，RTCPeerConnection 就与普通的 socket 一样，在通话的每一端都至少有一个 RTCPeerConnection 对象。在 WebRTC 中它负责与各端建立连接，接收、发送音视频数据，并保障音视频的服务质量。

在操作时，你完全可以把它当作一个 socket 来用，而且还是一个具有超强能力的“ **SOCKET**”。至于它是如何保障端与端之间的连通性，如何保证音视频的服务质量，又如何确定使用的是哪个编解码器等问题，作为应用者的你可以不必关心，因为所有的这些问题都已经在 RTCPeerConnection 对象的底层实现好了。

因此，如果有人问你什么是 RTCPeerConnection？你可以简要地回答说: “ **它就是一个功能超强的 socket**！”这一下就点出了 RTCPeerConnection 的本质。

## 实现通话

今天我们要实现的例子是在同一个页面中，使两个RTCPeerConnection对象之间建立连接。它没有什么实际价值，但却能很好地证明RTCPeerConnection是如何工作的。

这里需要特别强调一点，在音视频通话中，每一方只需要有一个 RTCPeerConnection对象，用它来接收或发送音视频数据。然而在真实的场景中，为了实现端与端之间的通话，还需要利用信令服务器交换一些信息，比如交换双方的 IP 和 port 地址，这样通信的双方才能彼此建立连接（信令服务器的实现可以参考 [上一篇文章](https://time.geekbang.org/column/article/114179)）。

而在本文的例子中，为了最大化地减少额外的工作量，所以我们选择在同一个页面中进行音视频的互通，这样就不需要开发、安装信令服务器了。不过这样也增加了一些理解的难度，所以在阅读下面的内容时，你一定要在脑子中想象： **每一个 RTCPeerConnection 就是一个客户端**，这样就比较容易理解后面的内容了。

接下来我们就实操起来，一步一步实现通话吧！

### 1\. 添加视频元素和控制按钮

我们首先开发一个简单的显示界面，在该页面中有两个 `<video>` 标签，一个用于显示本地捕获的视频，另一个用于显示“远端”的视频。

除此之外，在该页面上还有三个 `<button>` 按钮：

- start 按钮，用于打开本地视频；
- call 按钮，用于与对方建立连接；
- hangup 按钮，用于断开与对方的连接。

具体代码如下：

```
<video id="localVideo" autoplay playsinline></video>
<video id="remoteVideo" autoplay playsinline></video>

<div>
  <button id="startButton">start</button>
  <button id="callButton">call</button>
  <button id="hangupButton">hang up</button>
</div>

```

### 2\. 适配各种浏览器

一般情况下，我都还会在显示页面中添加一个叫做 **adapter.js** 的脚本，它的作用是为各种浏览器都提供统一的、最新的 WebRTC API 接口。

在 WebRTC 1.0 规范没有发布之前，虽然各大浏览器厂商都在各自的浏览器上移植了 WebRTC，但你会发现它们最终实现的接口各不相同。这一问题直到 WebRTC 规范正式推出之后才有所改善，但很多用户依然使用老版本的浏览器，这就为使用 WebRTC 开发音视频应用增添了不少麻烦。

由于浏览器版本众多，而且用户基数大，可以预见各浏览器访问 WebRTC API 接口不统一的问题，在未来很长一段时间内会一直存在。但幸运的是，Google 很早之前就已经注意到了这个问题，因此开发了adapter.js 这个适配器脚本，以弥补各浏览器API 不统一的问题。

当然，你也可以自己做这件事儿，只不过适配各种浏览器版本真的是一件令人头疼的事儿，这会是一个不小的挑战。而 adapter.js 正好解决了这个痛点。随着adapter.js的发展，它为了解决各种各样复杂的问题，也从一小段很简单的JavaScript代码逐渐变得越来越庞大、复杂。但对于adapter.js这种即稳定、又成熟，且性能不错的库我一向是奉行“拿来主义”哈！

在页面中引入 adapter.js 的方法如下：

```
...
<script src="https://webrtc.github.io/adapter/adapter-latest.js </script>
...

```

修改后的 index.html 代码如下：

```
<!DOCTYPE html>
<html>

<head>
  <title>Realtime communication with WebRTC</title>
  <link rel="stylesheet" href="css/main.css" />
</head>

<body>
  <h1>Realtime communication with WebRTC</h1>

  <video id="localVideo" autoplay playsinline></video>
  <video id="remoteVideo" autoplay playsinline></video>

  <div>
    <button id="startButton">Start</button>
    <button id="callButton">Call</button>
    <button id="hangupButton">Hang Up</button>
  </div>

  <script src="https://webrtc.github.io/adapter/adapter-latest.js"></script>
  <script src="js/client.js"></script>
</body>
</html>

```

通过上面的操作，界面显示及各浏览器之间适配的问题就全部完成了。接下来我们来看一下 RTCPeerConnection是如何工作的。

### 3\. RTCPeerConnection如何工作

为了讲清楚RTCPeerConnection是如何工作的，我们还是看一个具体的例子吧。

假设 A 与 B 进行通信，那么对于每个端都要创建一个 RTCPeerConnection 对象，这样双方才可以通信，这个应该很好理解。但由于我们的例子中，通信双方是在同一个页面中（也就是说一个页面同时扮演 A 和 B 两个角色），所以在我们的JavaScript代码中会同时存在两个 RTCPeerConnection 对象，我们称它们为 pc1 和 pc2好啦！这里你一定要注意，虽然pc1 和 pc2 是在同一个页面中，但你一定要把 pc1 和 pc2 想像成两个端的连接对象，这样才便于对后面代码的理解。

在 WebRTC 端与端之间建立连接，包括三个任务：

- 为连接的每个端创建一个RTCPeerConnection对象，并且给 RTCPeerConnection 对象添加一个本地流，该流是从getUserMedia()获取的；
- 获取本地媒体描述信息，即 SDP 信息，并与对端进行交换；
- 获得网络信息，即 Candidate（IP地址和端口），并与远端进行交换。

下面我们就来详细看看代码是如何实现的。

**（1）获取本地音视频流**

你需要调用 getUserMedia() 获取到本地流，然后将它添加到对应的 RTCPeerConnecton对象中，代码如下：

```
...
//创建 RTCPeerConnection 对象
let localPeerConnection = new RTCPeerConnection(servers);
...

//调用 getUserMedia API 获取音视频流
navigator.mediaDevices.getUserMedia(mediaStreamConstraints).
  then(gotLocalMediaStream).
  catch(handleLocalMediaStreamError);

//如果 getUserMedia 获得流，则会回调该函数
//在该函数中一方面要将获取的音视频流展示出来
//另一方面是保存到 localSteam
function gotLocalMediaStream(mediaStream) {
  ...
  localVideo.srcObject = mediaStream;
  localStream = mediaStream;
  ...

}

...

//将音视频流添加到 RTCPeerConnection 对象中
localPeerConnection.addStream(localStream);

...

```

**（2）交换媒体描述信息**

当 RTCPeerConnection 对象获得音视频流后，就可以开始与对端进行媒协体协商了。整个媒体协商的过程我已经在 [《08 \| 有话好商量，论媒体协商》](https://time.geekbang.org/column/article/111675) 一文中做了详细介绍，若记不清了，可以回看下，我们下面的实践中要用到。

并且前面我们也说了，在真实的应用场景中，各端获取的 SDP 信息都要通过信令服务器进行交换，但在我们这个例子中为了减少代码的复杂度，直接在一个页面中实现了两个端，所以也就不需通过信令服务器交换信息了，只需要直接将一端获取的 offer 设置到另一端就好了，具体步骤可以大致描述为如下。

我们首先创建 offer 类型的 SDP信息。A 调用 RTCPeerConnection 的 createOffer() 方法，得到 A 的本地会话描述，即 offer 类型的 SDP 信息：

```
...
localPeerConnection.createOffer(offerOptions)
  .then(createdOffer).catch(setSessionDescriptionError);
...

```

如果 createOffer 函数调用成功，会回调 createdOffer 方法，并在 createdOffer 方法中做以下几件事儿。

- A 使用setLocalDescription()设置本地描述，然后将此会话描述发送给B。B 使用setRemoteDescription() 设置 A 给它的描述作为远端描述。
- 之后，B 调用 RTCPeerConnection 的 createAnswer() 方法获得它本地的媒体描述。然后，再调用 setLocalDescription 方法设置本地描述并将该媒体信息描述发给A。
- A得到 B 的应答描述后，就调用 setRemoteDescription()设置远程描述。

整个媒体信息交换和协商至此就完成了。具体代码如下：

```
//当创建 offer 成功后，会调用该函数
function createdOffer(description) {
  ...
  //将 offer 保存到本地
  localPeerConnection.setLocalDescription(description)
    .then(() => {
      setLocalDescriptionSuccess(localPeerConnection);
    }).catch(setSessionDescriptionError);

  ...
  //远端 pc 将 offer 保存起来
  remotePeerConnection.setRemoteDescription(description)
    .then(() => {
      setRemoteDescriptionSuccess(remotePeerConnection);
    }).catch(setSessionDescriptionError);

  ...
  //远端 pc 创建 answer
  remotePeerConnection.createAnswer()
    .then(createdAnswer)
    .catch(setSessionDescriptionError);
}

//当 answer 创建成功后，会回调该函数
function createdAnswer(description) {
  ...
  //远端保存 answer
  remotePeerConnection.setLocalDescription(description)
    .then(() => {
      setLocalDescriptionSuccess(remotePeerConnection);
    }).catch(setSessionDescriptionError);

  //本端pc保存 answer
  localPeerConnection.setRemoteDescription(description)
    .then(() => {
      setRemoteDescriptionSuccess(localPeerConnection);
    }).catch(setSessionDescriptionError);
}

```

**（3）端与端建立连接**

在本地，当 A 调用 setLocalDescription 函数成功后，就开始收到网络信息了，即开始收集 ICE Candidate。

当 Candidate 被收集上来后，会触发 pc 的 **icecandidate** 事件，所以在代码中我们需要编写 icecandidate 事件的处理函数，即onicecandidate，以便对收集到的 Candidate 进行处理。

为 RTCPeerConnection 对象添加 icecandidate 事件的方法如下：

```
...
localPeerConnection.onicecandidate= handleConnection(event);
...

```

上面这段代码为 localPeerConnection 对象的 icecandidate 事件添加了一个处理函数，即 handleConnection。

当Candidate变为有效时，handleConnection 函数将被调用，具体代码如下：

```
...
function handleConnection(event) {

  //获取到触发 icecandidate 事件的 RTCPeerConnection 对象
  //获取到具体的Candidate
  const peerConnection = event.target;
  const iceCandidate = event.candidate;

  if (iceCandidate) {
  	 //创建 RTCIceCandidate 对象
    const newIceCandidate = new RTCIceCandidate(iceCandidate);
    //得到对端的RTCPeerConnection
    const otherPeer = getOtherPeer(peerConnection);

	//将本地获到的 Candidate 添加到远端的 RTCPeerConnection对象中
    otherPeer.addIceCandidate(newIceCandidate)
      .then(() => {
        handleConnectionSuccess(peerConnection);
      }).catch((error) => {
        handleConnectionFailure(peerConnection, error);
      });

    ...
  }

}
...

```

每次 handleConnection 函数被调用时，就说明 WebRTC 又收集到了一个新的 Candidate。在真实的场景中，每当获得一个新的 Candidate 后，就会通过信令服务器交换给对端，对端再调用 RTCPeerConnection 对象的 addIceCandidate()方法将收到的 Candidate 保存起来，然后按照Candidate的优先级进行连通性检测。

如果 Candidate 连通性检测完成，那么端与端之间就建立了物理连接，这时媒体数据就可能通这个物理连接源源不断地传输了。

## 显示远端媒体流

通过 RTCPeerConnection 对象A与B双方建立连接后，本地的多媒体数据就被源源不断地传送到了远端。不过，远端虽然接收到了媒体数据，但音视频并不会显示或播放出来。以视频为例，不显示视频的原因是 `<video>` 标签还没有与 RTCPeerConnection 对象进行绑定，也就是说数据虽然到了，但播放器还没有拿到它。

下面我们就来看一下如何让RTCPeerConnection对象获得的媒体数据与 H5 的 `<video>` 标签绑定到一起。具体代码如下所示：

```
...

localPeerConnection.onaddstream = handleRemoteStreamAdded;
...

function handleRemoteStreamAdded(event) {
  console.log('Remote stream added.');
  remoteStream = event.stream;
  remoteVideo.srcObject = remoteStream;
}

...

```

上面代码的关键点是 **addstream** 事件。 在创建好 RTCPeerConnection 对象后，我们需要给 RTCPeerConnection 的 addstream 事件添加回调处理函数，即onaddstream 函数。也就是说，当有数据流到来的时候，浏览器会回调它，在我们的代码中设置的回调处理函数就是 **handleRemoteStreamAdded** 。

当远端有数据到达时，WebRTC 底层就会调用 addstream 事件的回调函数，即handleRemoteStreamAdded。在 handleRemoteStreamAdded 函数的输入参数event中，包括了远端的音视频流，即 MediaStream 对象，此时将该对象赋值给 video 标签的 srcObject 字段，这样 video 就与 RTCPeerConnection 进行了绑定。

至此，video 就能从 RTCPeerConnection 获取到视频数据，并最终将其显示出来了。

## 小结

在文中我向你详细介绍了RTCPeerConnection类，当你从不同的角度去观察它时，你会对它有不同的认知：如果你从使用的角度看，会觉得RTCPeerConnection是一个接口类；如果你从功能的角度看，它又是一个功能聚合类。这就是真实的 RTCPeerConnection类。

在使用 RTCPeerConnection时，你可以把它当作一个功能超强的 socket 使用。在它的底层，它做了很多很细致的工作，而在应用层，你不必关心这些细节，只要学会如何使用它，就可以在浏览器上轻松实现你对音视频处理的想法。

在本文的后半段，我还通过一个具体的例子向你讲解了如何使用 RTCPeerConnection 对象。通过这个例子你就知道如何在一个页面内实现音视频流的发送与接收了。

## 思考时间

在 [上一篇文章](https://time.geekbang.org/column/article/114179) 中我向你讲解了如何通过 Node.js搭建一套信令服务器，今天我又向你讲解了如何使用 RTCPeerConnection 对象，那你是否可以将二者结合起来实现一个简单的 1对1 系统了呢？

欢迎在留言区与我分享你的想法，也欢迎你在留言区记录你的思考过程。感谢阅读，如果你觉得这篇文章对你有帮助的话，也欢迎把它分享给更多的朋友。

[所做Demo的GitHub链接（有需要可以点这里）](https://github.com/avdance/webrtc_web/tree/master/12_peerconnection)