你好，我是Barry。

在上节课我们学习了如何使用Nginx来搭建服务器，并完成了防火墙的配置。这节课我们继续来完成直播系统的开发，学习如何通过NRM简单迅速地搭建流媒体服务器，并使用NRM来支持HLS协议直播。

在动手实操之前，我会先带你认识一下NRM，之后再为你讲解RTMP协议和HLS直播协议的工作原理。有了这些理论基础，后面搭建流媒体服务器的时候，你的思路也会更清晰。

## NRM的功能特性

NRM实际是Nginx-rtmp-module的缩写。这是一个用于Nginx的RTMP模块，它允许Nginx作为RTMP协议的服务器，主要用来处理基于RTMP协议的音频和视频流传输。

NRM是Nginx的第三方模块，它的开发由第三方开发者研发维护。NRM模块一直在不断更新和发展，目前已经有大量的开发者为其贡献代码。这是NRM的 [GitHub地址](https://github.com/arut/nginx-rtmp-module)，你可以课后再花点时间详细了解一下。

在直播领域里NRM应用很广泛。它可以作为直播服务器的后端，接收和处理来自客户端的直播请求，并将直播流传输到其他服务器或客户端上。同时，它还可以与其他直播相关的服务（如CDN服务、推流服务器等）集成，提供完整的直播解决方案。

为了帮你熟练地应用NRM，我们还需要了解它的功能特点，我们可以从直播流管理、直播流分发、负载均衡、安全性和可定制性这五个方面来把握。具体你可以参考后面的表格。

![](https://static001.geekbang.org/resource/image/ce/5a/ced044133f017d02f563a862daba835a.jpg?wh=3504x1721)

## NRM的优势

在了解了功能特性之后，我们再进一步了解一下NRM的优势，这样你会更加明确我们为什么选择它来搭建流媒体服务器。

在直播和点播支持方面，Nginx-rtmp-module可以作为RTMP协议的服务器，接收和处理RTMP直播请求，并将直播流传输到其他服务器或客户端上。同时，它还支持HLS点播，可以将直播流转换为HLS流，这样我们就能实现在支持HLS协议的客户端上直播。

另外，Nginx-rtmp-module还支持将一次 **直播流分为多个视频文件存储**，以便后续的处理和分析。这可以用于实现直播内容的分段存储、录制和回放等功能，也有助于我们分析直播数据，优化产品。

在音视频解码方面，Nginx-rtmp-module可以支持H.264视频编解码器和AAC音频编解码器。这能保障直播过程中的音视频质量，并提供 **高效的编解码处理。** Nginx-rtmp-module还支持回调HTTP，作用是完成直播里的HTTP请求和响应操作。这个功能可以帮我们实现直播模块和后端系统的通信、请求和响应等功能。

在直播系统中，我们可以使用HTTP控制直播。通过发送HTTP请求到Nginx-rtmp-module，我们能给用户提供更完善的直播管理功能，比如直播的开启、停止、删除、录播保存等等。

同时，Nginx-rtmp-module具备更优秀的缓存技术，可以在效率和解码之间达到平衡，获得更好的缓存效果。这样模块在处理大量直播流时，仍然可以保持高性能状态，实现低延迟且稳定的流传输。

## RTMP协议

前面我们说过NRM是处理基于RTMP协议的音频和视频流传输，那RTMP协议在直播里又起到了什么作用呢？我们这就来看看。

RTMP（Real-Time Messaging Protocol）是一种实时消息传输协议。它是一种基于网络的应用层协议，用来在客户端和服务器之间传输实时音频、视频和数据。

2005年，当时Adobe Systems为了实现Flash播放器与服务器之间的实时通信而推出了RTMP协议。随着Flash播放器越来越普及，RTMP协议得到了广泛应用。后来，HTML5技术逐渐发展起来，Adobe Systems也在2011年推出了支持HTML5的RTMP协议实现，即RTMP协议的变形版本——RTMP-c。

RTMP-c的实时性较强，延迟在1-2s内。RTMP适用于多种应用场景，如直播、视频播放、数据传输、实时通信等，你可以参考我整理的表格。

![](https://static001.geekbang.org/resource/image/9d/0c/9db9bf754a814181cbbd683b1d39510c.jpg?wh=3401x1539)

接下来，我带你梳理一下RTMP协议的客户端和服务端建立连接流程，也就是RTMP协议握手的过程。

在RTMP协议中，握手过程由三个固定大小的chunk组成，而不是像其他协议一样由可变大小的带有头文件的chunk组成。这三个chunk分别是C0、S0和C1。

- C0：客户端发送的RTMP协议连接请求
- S0：服务器发送的RTMP协议连接响应
- C1：客户端发送的确认消息

在RTMP协议中，这三个chunk的大小是固定的，而且不包含头文件。这种握手方式相对简单，但是可以确保握手过程稳定可靠。

整个握手过程可以拆解为三步，我们分别来看看每一步具体执行了什么动作。

![](https://static001.geekbang.org/resource/image/d1/ef/d1cdb5731e699ceb36e096237b4986ef.jpg?wh=4942x5260)

第一步，客户端发送一个RTMP请求连接消息（C0/C1）给服务器，其中包含用于建立连接的参数，如IP地址、端口号和协议版本等。

第二步，服务器收到请求后，发送一个确认连接消息（S0/S1）给客户端，表示服务器已经接受连接请求。

第三步，客户端再发送一个确认消息（C2）给服务器，表示客户端已经接受服务器的确认，连接建立成功。等服务器收到（C2）消息之后，会发送一个（S2）消息给客户端，确认连接已经建立，并通知客户端可以开始传输数据。

以上每一步的执行，服务器和客户端都需要等到确切的反馈结果，才会执行下一次的交互发送，比如客户端要在等收到S1之后，才能向服务端发送C2。在整个握手过程中，为了保证客户端和服务器成功建立链接，提升链接的安全性和可靠性，RTMP协议还进行了一些安全验证和加密操作。

搭建直播系统时，我们需要根据具体的应用场景和需求来选择适合的协议，或者将多个协议进行整合使用，以满足不同的需求。

## HLS直播协议

除了RTMP协议，还有一个协议在直播领域应用也很广泛，它就是HLS直播协议。

HLS（HTTP Live Streaming）是一种基于HTTP协议的流媒体传输协议，适用于直播、视频播放和实时通信等场景。在2009年，苹果公司推出了HLS协议，主要用于 **在移动设备上** 实现流媒体传输。

HLS协议能够将直播流分割为多个小的HTTP文件，通过TCP协议进行传输。这种传输方式可以适应不同的网络状况，实现更加稳定和可靠的流媒体传输。另外，为满足不同应用场景的需求，HLS协议还支持多种音视频编码格式（如AAC、H.264等）。HLS协议的适用场景，你同样可以参考后面的表格。

![](https://static001.geekbang.org/resource/image/67/2c/67caa938aea14f183c66aea511f7302c.jpg?wh=3408x1559)

不难发现，HLS直播协议的优势在于强大的低延迟、多编码格式、分布式直播等能力，还有它可以支持移动端直播。

提到HLS直播协议，就不得不说一说M3U8文件。在HLS直播协议的应用中，需要使用M3U8文件来描述直播流的元数据信息。

M3U8文件是一个文本文件，它包含多个媒体文件的URL地址，以及一些其他的元数据信息，如编码格式、分辨率等。

在HLS直播中，服务器会定期发送M3U8文件给客户端，客户端通过解析M3U8文件，可以获取到当前直播流的元数据信息，以及最新的媒体文件列表。这样，播放器就可以根据这些信息选择合适的媒体文件进行播放，直播也会更加流畅稳定。

## 项目实战

接下来，我们结合前面所学，一起完成NRM的搭建，并通过配置实现支持HLS协议直播。

### Nginx-rtmp-module配置安装

首先，我们需要先下载Nginx-rtmp-module。从官方的Git地址把NRM克隆下来，拉取并下载到Linux中。具体的执行命令如下。

```plain
git clone https://github.com/arut/nginx-rtmp-module.git

```

当然你还可以选择另一种下载方式：在GitHub中打开Nginx-rtmp-module的首页，点击“code”，在下拉菜单选择 “Download.zip” 下载压缩包，即可直接完成下载，然后把它放到我们自己的服务器里。后面是操作截图，你可以参考一下。

![](https://static001.geekbang.org/resource/image/97/17/975b1d26c4d1637eff27b2ee9e2a2d17.jpg?wh=2876x1626)

当然，你也可以使用wget命令下载并解压。

```plain
wget https://github.com/arut/nginx-rtmp-module/archive/master.zip

unzip  master.zip

```

第1行命令的含义是使用wget工具，从GitHub上下载nginx-rtmp-module的master分支代码，并将其保存为master.zip文件。紧接着我们通过unzip工具将master.zip文件解压缩到当前目录下。

接下来，就到了编译安装Nginx-rtmp-module的环节，我们就要进入Nginx解压目录，执行configure。

```plain
./configure --add-module=../nginx-rtmp-module-master
make
make install

```

第1行命令.configure用于配置nginx的编译环境，其中–add-module参数指定了要添加的Nginx-rtmp-module的路径，命令中的…/nginx-rtmp-module-master就是指添加到nginx的编译环境中，这个地址你可以自己选择。

第2行命令make的作用是编译nginx，它会根据配置文件和源代码文件自动生成可执行文件 。再看第三行命令，make install用于将编译好的可执行文件复制到指定的安装目录中，并将相关的配置文件和模块文件也复制到相应的位置。

因为Nginx默认是不支持rtmp，所以我们还需要修改配置文件。你只需要进入bin/conf目录，找到 nginx.conf 文件，然后在配置文件中添加后面的配置。

```plain
rtmp {
    server {
        listen 1935;
        #应用程序块
        application mylive {
            live on;
            hls on;
            hls_path /usr/local/m3u8File;
        }
    }
}

```

因为配置文件涉及到的配置项比较多，为了方便你学习，我直接整理成了表格。

![](https://static001.geekbang.org/resource/image/e1/6f/e12e6aaae3c4bfe7235baf5b34yy426f.jpg?wh=3733x2260)

因为HLS协议是基于HTTP协议的，所以无法通过RTMP协议头访问HLS的M3U8文件。为了配置对HLS的访问操作，我们还要完成一个关键操作——修改http中的server模块。

你需要加入的就是location的部分，具体的配置项是后面这样。

```plain
server {
    listen 80;
    location /mylive_hls {
        types {
            application/vnd.apple.mpegurl m3u8;
            video/mp2t ts;
        }
        alias /usr/local/m3u8File;
    }
}

```

你可以看看配置内容，核心配置项的解释如下表。

![](https://static001.geekbang.org/resource/image/0d/11/0dde68f592d882dc7c3f78629d693d11.jpg?wh=3656x1211)

完成前面的配置后，我们就可以启动Nginx了，别忘了指定Nginx服务器的可执行文件路径，这样才能让对应的配置生效。具体的命令如下所示。

```plain
/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf

```

然后我们查看Nginx的进程，如果出现后面截图里的执行效果，这就代表服务启动成功了。

![](https://static001.geekbang.org/resource/image/99/3a/991825c4885e98b7c90eacf1b2a43a3a.jpg?wh=2600x437)

到这里，我们就安装搭建好了Nginx-rtmp-module，还用它支持了HLS协议直播。下节课我们继续学习如何实现推拉流，让直播动起来，敬请期待。

## 总结

又到了课程的尾声，我们一起回顾总结一下这节课的内容。

Nginx-rtmp-module是一个用于Nginx的RTMP模块，它允许Nginx作为RTMP协议的服务器。综合来看，Nginx-rtmp-module可以满足不同应用场景的需求，并提供高效、稳定的RTMP和HLS直播服务，非常适合应用在我们的直播系统中。

RTMP协议是一种用于实时音视频和数据传输的协议，适用于多种应用场景，如直播、视频播放、数据传输、实时通信等。而HLS协议是一种基于HTTP协议的流媒体传输协议，适用于移动设备上的直播应用，可以适应不同的网络状况，实现稳定可靠的流媒体传输。

在项目实战部分，我们一起完成了Nginx-rtmp-module的安装配置，这一部分的操作步骤我写得比较详细。另外，因为HLS协议是基于HTTP协议的， **无法通过RTMP协议头访问HLS的M3U8文件，所以我们需要修改http中的server模块。**

实战部分还有配置文件中的参数，建议你课后多花一些时间理解和掌握，这样才能真正把这些知识化为己用。

## 思考题

在直播系统中，直播传输除了M3U8类型文件外，你还知道哪几种常见的文件类型？

欢迎你在留言区和我交流互动，也推荐你把这节课分享给身边更多朋友。