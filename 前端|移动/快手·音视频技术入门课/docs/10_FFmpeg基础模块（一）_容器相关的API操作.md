你好，我是刘歧。

学到这里，相信你对音视频的基本工作原理和基本操作已经有了一定的认识，并且能够通过命令行、参考标准文档等工具独立完成一些音视频工作了。课程到现在开始渐入佳境，我们要从工具用户逐渐转变成API用户了。毕竟还有很多工作是FFmpeg命令行操作起来不太方便的，比如直播连麦的动态画面拼接、连麦PK结束后画面比例变化等。

从这节课开始，我们会逐步分析作为API用户我们需要了解的FFmpeg中的重要模块，比如AVFormat模块、AVcodec模块、AVfilter模块、swscale模块、swresample模块。

在具体讲解如何使用FFmpeg的API之前，为了方便你查看API对应的代码，首先我会介绍一下FFmpeg的代码结构目录，我建议你先从 [FFmpeg的官方代码库](https://ffmpeg.org/download.html) 下载一份代码。

```plain
git clone git://source.ffmpeg.org/ffmpeg.git

```

从目录中可以看到，FFmpeg目录中包含了FFmpeg库代码目录、构建工程目录、自测子系统目录等，具体内容如下：

![图片](https://static001.geekbang.org/resource/image/8a/bd/8af20d33c9b1d3144dddf25cbfafe5bd.png?wh=1626x1140)

现在你知道FFmpeg的源代码目录中都包含了哪些内容，在之后使用FFmpeg的API做开发遇到问题时，就可以通过查看源代码来了解更多、更详细的内部实现了。

## AVFormat模块

从FFmpeg的目录结构中可以看出， **libavformat主要是用来做封装格式处理的模块**，如果不做转码，只做切片或者封装格式转换的话，基本上用AVFormat模块就可以，下面我们来看一下AVFormat模块都有哪些常用接口提供给我们使用。

avformat\_version、avformat\_configuration、avformat\_license 这三个接口都是用来调试的，确定使用的FFmpeg版本、编译配置信息以及License。因为FFmpeg本身是LGPL的，但是FFmpeg可以引入其他第三方库，比如libfdkaac是nonfree的，就有可能存在专利收费的法律风险。

如果引入了libx264这样的编码器，FFmpeg会自动切换成GPL的License，这个时候如果你想要基于FFmpeg做定制或者开发，就需要注意GPL的License法律风险，相关情况最好还是咨询一下开源License法律援助律师，尽量避免给自己的项目和公司带来不必要的麻烦。

> GPL 是 GNU 公共许可证的缩写。它通常会具有 “传染性”，当某一项目使用了 GPL 下的软件部分的话，那么该项目将被 “感染”变成了 GPL 协议下产品，也就是你需要将其开源和免费。LGPL 是 GNU 宽松公共许可证的缩写，它是GPL的一个为主要为类库使用设计的开源协议。和GPL不同，LGPL 允许商业软件通过类库引用方式使用LGPL类库而不需要开源商业软件的代码。—— [关于开源许可 GPL 与 LGPL](https://my.oschina.net/u/4258525/blog/4542981)

### AVFormat前处理部分

当我们做音视频内容处理的时候，首先接触到的应该是AVFormatContext模块相关的操作，也就是我们这里说的AVFormat部分，但是操作AVFormat的时候，会有一个前处理部分，主要包含网络初始化、模块遍历、申请上下文空间、打开文件，还有分析音视频流等操作。下面我们逐个了解一下AVFormat前处理部分的接口与作用。

- avformat\_network\_init和avformat\_network\_deinit两个接口，是网络相关模块的初始化和撤销网络相关模块初始化。
- av\_muxer\_iterate和av\_demuxer\_iterate两个接口，是muxer和demuxer的遍历接口，如果你想查找自己需要的muxer或者demuxer是否在当前使用的FFmpeg库中，用这两个接口可以全面地查找。
- avformat\_alloc\_context和avformat\_free\_context 两个接口可以用来申请与释放AVFormatContext上下文结构。
- avformat\_new\_stream 接口用来创建新的AVStream。
- av\_stream\_add\_side\_data 接口用来向AVStream中添加新的side data信息，例如视频旋转信息，通常是可以存储在side data里面的。
- av\_stream\_new\_side\_data 接口用来申请新的side data。
- av\_stream\_get\_side\_data 接口用来获取side data。
- avformat\_alloc\_output\_context2 接口用来申请将要输出的文件的AVFormatContext，可以通过avformat\_free\_context释放申请的AVFormatContext。
- av\_find\_input\_format 接口可以根据传入的short\_name来获得对应的AVFormat模块，例如MP4。
- avformat\_open\_input 接口主要用处是打开一个AVInputFormat，并挂在AVFormatContext模块上，这个接口里面会调用avformat\_alloc\_context，可以通过接口avformat\_close\_input来关闭和释放avformat\_open\_input里对应的alloc操作。
- av\_find\_best\_stream 接口用来找到多个视频流或多个音频流中最优的那个流。
- avformat\_find\_stream\_info 接口主要用来建立AVStream的信息，获得的信息大多数情况下是比较准确的。使用avformat\_find\_stream\_info接口来获得AVStream信息的话，会比较消耗时间。因为里面需要通过try\_decode进行解码操作，来获得更精准的AVStream信息，所以有些固定场景不使用avformat\_find\_stream\_info，是为了节省时间方面的开销。

我们可以通过probesize、analyzeduration来设置读取的音视频数据的阈值，avformat\_find\_stream\_info里面也会遍历这个阈值，所以通过设置probesize和analyzeduration也可以节省一些时间。

如果有多个类似AAC或者H264这样的codec的话，avformat\_find\_stream\_info内部会使用最先遍历到的codec，其实我们可以在使用avformat\_find\_stream\_info之前指定解码器，预期的结果会更准确一些。

### AVFormat读写处理部分

看完AVFormat前处理部分的操作，接下来我们进入AVFormat读写处理的部分。

- av\_read\_frame 接口用来从AVFormatContext中读取AVPacket，AVPacket里面存储的内容在 [第6节课](https://time.geekbang.org/column/article/547562) 的时候已经有讲过，这里就不重复讲解了。
- 当拖动进度条的时候，我们可以调用avformat\_seek\_file（旧版是av\_seek\_frame）接口，seek到自己想要指定的位置，但前提是对应的封装格式得支持精确seek，seek支持以下四种模式：

```plain
AVSEEK_FLAG_BACKWARD //往回seek
AVSEEK_FLAG_BYTE //以字节数的方式seek
AVSEEK_FLAG_ANY //可seek到任意帧
AVSEEK_FLAG_FRAME //以帧数量的方式seek

```

- avformat\_flush 接口主要是用来清空当前AVFormatContext中的buffer。
- avformat\_write\_header 接口主要用在“写”操作的开头部分，通常指传输协议的开始，写封装格式头部。avformat\_write\_header里会调用到avformat\_init\_output，通常avformat\_write\_header函数的最后一个参数可以传入Option，Option可以控制容器模块中的Option，关于如何查看封装容器格式的Option参数，我们 [第7节课](https://time.geekbang.org/column/article/548420) 的时候讲过，你可以回顾一下。

> 写MP4文件有很多Option，可以通过ffmpeg -h muxer=mp4看到生成MP4的一些列参数，也就是Option。——第7节课内容回顾

- avformat\_init\_output 接口主要用来做容器格式初始化部分的操作，例如打开文件，或者有一些容器格式内部的信息需要初始化的时候。
- av\_interleaved\_write\_frame 接口支持在写入AVPacket的时候，根据dts时间戳交错写入数据。使用这个接口有一个需要注意的地方，就是数据会先写入到buffer里用来交错存储数据，这个buffer会不断变大，如果有必要的话，可以考虑自己调用avio\_flush或者写NULL把buffer写到磁盘。

> 我们在存储音视频数据的时候，如果是顺序读取音视频数据的话，音视频数据交错存储比较好，因为这样可以给内存、硬盘或者网络节省很多开销。——第3节课内容回顾

- av\_write\_frame 接口是不按照交错的形式存储AVPacket，不过在写入文件的时候是直接写入到磁盘，不会有buffer，所以可以考虑自己先做交错再用这个接口，不过我一般选择使用av\_interleaved\_write\_frame，因为比较方便，不需要自己做数据交错排列的操作。
- av\_write\_trailer 接口是写数据到封装容器的收尾部分。可以关闭和释放在此之前申请的内存，另外，MP4文件如果需要把moov移动到MP4文件头部，也是在这个接口里面完成的。

## 小结

FFmpeg中有很多重要的模块，比如AVFormat模块、AVcodec模块、AVfilter模块等。其中AVFormat是用来做封装格式处理的模块。这个模块的内部提供了很多常用的接口，比如前处理部分的avformat\_find\_stream\_info等接口，读写处理部分的avformat\_write\_header、av\_interleaved\_write\_frame等接口，了解这些接口的用途和可能出现的问题及解决办法，可以让我们在实践中更好地使用它们去做容器封装和解封装方面的操作。

![图片](https://static001.geekbang.org/resource/image/5c/73/5c6f88a5324bc15c6a5d3354c6c16a73.png?wh=1920x2045)

关于AVFormat模块中API接口更多的使用方式，比如说参数相关的内容，你还需要多看一看avformat.h头文件中的注释和参数说明。如果你还是掌握不住这些接口的使用方式的话，也可以根据我的建议，先把源代码下来，去看一下API里实现的过程来加深理解。

## 思考题

我们介绍最后一个接口av\_write\_trailer的时候，提到它支持把MP4的moov移动到文件的头部，在FFmpeg的命令行参数里面使用的是-movflags faststart，那么如果我用API的话，需要在哪个接口里面传递这个参数呢？

欢迎在评论区留下你的答案，也欢迎你把这节课分享给需要的朋友，我们下节课再见！