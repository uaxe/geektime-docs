> 你好，我是张绍文。俊杰目前负责微信的音视频开发工作，无论是我们平常经常使用到的小视频，还是最新推出的即刻视频，都是出自他手。俊杰在音视频方面有非常丰富的经验，今天有幸请到他来给我们分享他个人对Android音视频开发的心得和体会。

> 在日常生活中，视频类应用占据了我们越来越多的时间，各大公司也纷纷杀入这个战场，不管是抖音、快手等短视频类型，虎牙、斗鱼等直播类型，腾讯视频、爱奇艺、优酷等长视频类型，还是Vue、美拍等视频编辑美颜类型，总有一款适合你。

> 未来随着5G普及以及网络资费的下降，音视频的前景是非常广阔的。但是另一方面，无论是音视频的编解码和播放器、视频编辑和美颜的各种算法，还是视频与人工智能的结合（ [AI剪片](https://mp.weixin.qq.com/s/ZtsqF7bBODFymEaYFG6KAg)、视频修复、超清化等），它们都涉及了方方面面的底层知识，学习曲线比较陡峭，门槛相对比较高，所以也造成了目前各大公司音视频相关人才的紧缺。如果你对音视频开发感兴趣，我也非常建议你去往这个方向尝试，我个人是非常看好音视频开发这个领域的。

> 当然音视频开发的经验是靠着一次又一次的“填坑”成长起来的，下面我们一起来看看俊杰同学关于音视频的认识和思考。

大家好，我是周俊杰，现在在微信从事Android多媒体开发。应绍文的邀请，分享一些我关于Android音视频开发的心得和体会。

不管作为开发者还是用户，现在我们每天都会接触到各种各样的短视频、直播类的App，与之相关的音视频方向的开发也变得越来越重要。但是对于大多数Android开发者来说，从事Android音视频相关的开发可能目前还算是个小众领域，虽然可能目前深入这个领域的开发者还不是太多，但这个方向涉及的知识点可一点都不少。

## 音视频的基础知识

**1\. 音视频相关的概念**

说到音视频，先从我们熟悉也陌生的视频格式说起。

对于我们来说，最常见的视频格式就是 [MP4](https://zh.wikipedia.org/zh-cn/MP4) 格式，这是一个通用的容器格式。所谓容器格式，就意味内部要有对应的数据流用来承载内容。而且既然是一个视频，那必然有音轨和视轨，而音轨、视轨本身也有对应的格式。常见的音轨、视轨格式包括：

- 视轨： [H.265(HEVC)](https://zh.wikipedia.org/wiki/%E9%AB%98%E6%95%88%E7%8E%87%E8%A7%86%E9%A2%91%E7%BC%96%E7%A0%81)、 [H.264](https://zh.wikipedia.org/wiki/H.264/MPEG-4_AVC)。其中，目前大部分Android手机都支持H.264格式的直接硬件编码和解码；对于H.265来说，Android 5.0以上的机器就支持直接硬件解码了，但是对于硬件编码，目前只有一部分高端芯片可以支持，例如高通的8xx系列、华为的98x系列。对于视轨编码来说，分辨率越大性能消耗也就越大，编码所需的时间就越长。

- 音轨： [AAC](https://zh.wikipedia.org/wiki/%E9%80%B2%E9%9A%8E%E9%9F%B3%E8%A8%8A%E7%B7%A8%E7%A2%BC)。这是一种历史悠久音频编码格式，Android手机基本可以直接硬件编解码，几乎很少遇到兼容性问题。可以说作为视频的音轨格式，AAC已经非常成熟了。


对于编码本身，上面提到的这些格式都是 [有损编码](https://zh.wikipedia.org/zh-hans/%E6%9C%89%E6%8D%9F%E6%95%B0%E6%8D%AE%E5%8E%8B%E7%BC%A9)，因此压缩编码本身还需要一个衡量压缩之后，数据量多少的指标，这个标准就是 [码率](https://zh.wikipedia.org/wiki/%E6%AF%94%E7%89%B9%E7%8E%87#%E5%A4%9A%E5%AA%92%E4%BD%93%E7%9A%84%E6%AF%94%E7%89%B9%E7%8E%87)。同一个压缩格式下，码率越高质量也就越好。更多Android本身支持的编解码格式，你可以参考 [官方文档](https://developer.android.com/guide/topics/media/media-formats)。

小结一下，要拍摄一个MP4视频，我们需要将视轨 + 音轨分别编码，然后作为MP4的数据流，再合成出一个MP4文件。

**2\. 音视频编码的流程**

接下来，我们再来看看一个视频是怎么拍摄出来的。首先，既然是拍摄，少不了跟摄像头、麦克风打交道。从流程来说，以H.264/AAC编码为例，录制视频的总体流程是：

![](https://static001.geekbang.org/resource/image/40/73/406204beab2de273ecdb436d4bf66773.png?wh=1920*424)

我们分别从摄像头/录音设备采集数据，将数据送入编码器，分别编码出视轨/音轨之后，再送入合成器（MediaRemuxer或者类似mp4v2、FFmpeg之类的处理库），最终输出MP4文件。接下来，我主要以视轨为例，来介绍下编码的流程。

首先，直接使用系统的 [MediaRecorder](https://developer.android.com/reference/android/media/MediaRecorder) 录制整个视频，这是最简单的方法，直接就能输出MP4文件。但是这个接口可定制化很差，比如我们想录制一个正方形的视频，除非摄像头本身支持宽高一致的分辨率，否则只能后期处理或者各种Hack。另外，在实际App中，除非对视频要求不是特别高，一般也不会直接使用MediaRecorder。

视轨的处理是录制视频中相对比较复杂的部分，输入源头是Camera的数据，最终输出是编码的H.264/H.265数据。下面我来介绍两种处理模型。

![](https://static001.geekbang.org/resource/image/fb/82/fb9fe38693f3a86af745b97fc8d22882.png?wh=1698*200)

第一种方法是利用Camera获取摄像头输出的原始数据接口（例如onPreviewFrame），经过预处理，例如缩放、裁剪之后，送入编码器，输出H.264/H.265。

摄像头输出的原始数据格式为NV21，这是 [YUV](https://zh.wikipedia.org/wiki/YUV) 颜色格式的一种。区别于RGB颜色，YUV数据格式占用空间更少，在视频编码领域使用十分广泛。

一般来说，因为摄像头直接输出的NV21格式大小跟最终视频不一定匹配，而且编码器往往也要求输入另外一种YUV格式（一般来说是YUV420P），因此在获取到NV21颜色格式之后，还需要进行各种缩放、裁剪之类的操作，一般会使用 [FFmpeg](https://www.ffmpeg.org/)、 [libyuv](https://chromium.googlesource.com/libyuv/libyuv/) 这样的库处理YUV数据。

最后会将数据送入到编码器。在视频编码器的选择上，我们可以直接选择系统的MediaCodec，利用手机本身的硬件编码能力。但如果对最终输出的视频大小要求比较严格的话，使用的码率会偏低，这种情况下大部分手机的硬件编码器输出的画质可能会比较差。另外一种常见的选择是利用 [x264](https://www.videolan.org/developers/x264.html) 来进行编码，画质表现相对较好，但是比起硬件编码器，速度会慢很多，因此在实际使用时最好根据场景进行选择。

除了直接处理摄像头原始数据以外，还有一种常见的处理模型，利用Surface作为编码器的输入源。

![](https://static001.geekbang.org/resource/image/50/06/5003363cbda442463e50b7c6a245b306.png?wh=1692*198)

对于Android摄像头的预览，需要设置一张Surface/SurfaceTexture来作为摄像头预览数据的输出，而MediaCodec在API 18+之后，可以通过 [createInputSurface](https://developer.android.com/reference/android/media/MediaCodec#createInputSurface) 来创建一张Surface作为编码器的输入。这里所说的另外一种方式就是，将摄像头预览Surface的内容，输出到MediaCodec的InputSurface上。

而在编码器的选择上，虽然InputSurface是通过MediaCodec来创建的，乍看之下似乎只能通过MediaCodec来进行编码，无法使用x264来编码，但利用PreviewSurface，我们可以创建一个OpenGL的上下文，这样所有绘制的内容，都可以通过glReadPixel来获取，然后再讲读取数据转换成YUV再输入到x264即可（另外，如果是在GLES 3.0的环境，我们还可以利用 [PBO](http://www.songho.ca/opengl/gl_pbo.html) 来加速glReadPixles的速度）。

![](https://static001.geekbang.org/resource/image/98/cb/98ae4dbac4cac80639d7dfe4682414cb.png?wh=1534*560)

由于这里我们创建了一个OpenGL的上下文，对于目前的视频类App来说，还有各种各样的滤镜和美颜效果，实际上都可以基于OpenGL来实现。

而至于这种方式录制视频具体实现代码，你可以参考下grafika中 [示例](https://github.com/google/grafika/blob/master/app/src/main/java/com/android/grafika/CameraCaptureActivity.java)。

## 视频处理

**1\. 视频编辑**

在当下视频类App中，你可以见到各种视频裁剪、视频编辑的功能，例如：

- 裁剪视频的一部分。

- 多个视频进行拼接。


对于视频裁剪、拼接来说，Android直接提供了 [MediaExtractor](https://developer.android.com/reference/android/media/MediaExtractor) 的接口，结合seek以及对应读取帧数据readSampleData的接口，我们可以直接获取对应时间戳的帧的内容，这样读取出来的是已经编码好的数据，因此无需重新编码，直接可以输入合成器再次合成为MP4。

![](https://static001.geekbang.org/resource/image/61/ad/61b18d372ba93905b547d60da313a1ad.png?wh=1920*189)

我们只需要seek到需要裁剪原视频的时间戳，然后一直读取sampleData，送入MediaMuxer即可，这是视频裁剪最简单的实现方式。

但在实践时会发现， [seekTo](https://developer.android.com/reference/android/media/MediaExtractor#seekTo) 并不会对所有时间戳都生效。比如说，一个 **4min** 左右的视频，我们想要seek到大概 **2min** 左右的位置，然后从这个位置读取数据，但实际调用seekTo到2min这个位置之后，再从MediaExtractor读取数据，你会发现实际获取的数据上可能是从2min这里前面一点或者后面一点位置的内容。这是因为MediaExtractor这个接口只能seek到视频 [关键帧](https://zh.wikipedia.org/wiki/%E9%97%9C%E9%8D%B5%E6%A0%BC#%E8%A6%96%E8%A8%8A%E7%B7%A8%E8%BC%AF%E7%9A%84%E9%97%9C%E9%8D%B5%E6%A0%BC) 的位置，而我们想要的位置并不一定有关键帧。这个问题还是要回到视频编码，在视频编码时两个关键帧之间是有一定间隔距离的。

![](https://static001.geekbang.org/resource/image/9a/7b/9a59d62bc13f09d9ccf971ce6d8d5b7b.jpg?wh=1248*532)

如上图所示，关键帧被成为 **I帧**，可以被认为是一帧没有被压缩的画面，解码的时候无需要依赖其他视频帧。但是在两个关键帧之间，还存在这 **B帧**、 **P帧** 这样的压缩帧，需要依赖其他帧才能完整解码出一个画面。至于两个关键帧之间的间隔，被称为一个 [GOP](https://zh.wikipedia.org/wiki/%E5%9C%96%E5%83%8F%E7%BE%A4%E7%B5%84) ，在GOP内的帧，MediaExtractor是无法直接seek到的，因为这个类不负责解码，只能seek到前后的关键帧。但如果GOP过大，就会导致视频编辑非常不精准了（实际上部分手机的ROM有改动，实现的MediaExtractor也能精确seek）。

既然如此，那要实现精确裁剪也就只能去依赖解码器了。解码器本身能够解出所有帧的内容，在引入解帧之后，整个裁剪的流程就变成了下面的样子。

![](https://static001.geekbang.org/resource/image/89/53/89f6cf7d68677a1a6225905117877853.png?wh=1920*211)

我们需要先seek到需要位置的前一I帧上，然后送入解码器，解码器解除一帧之后，判断当前帧的 [PTS](https://en.wikipedia.org/wiki/Presentation_timestamp) 是否在需要的时间戳范围内，如果是的话，再将数据送入编码器，重新编码再次得到H.264视轨数据，然后合成MP4文件。

上面是基础的视频裁剪流程，对于视频拼接，也是类似得到多段H.264数据之后，才一同送入合成器。

另外，在实际视频编辑中，我们还会添加不少视频特效和滤镜。前面在视频拍摄的场景下，我们利用Surface作为MediaCodec的输入源，并且利用Surface创建了OpenGL的上下文。而MediaCodec作为解码器的时候，也可以在 [configure](https://developer.android.com/reference/android/media/MediaCodec#configure) 的时候，指定一张Surface作为其解码的输出。大部分视频特效都是可以通过OpenGL来实现的，因此要实现视频特效，一般的流程是下面这样的。

![](https://static001.geekbang.org/resource/image/0f/5d/0f4a26fd743155b102887758056ba85d.png?wh=1920*207)

我们将解码之后的渲染交给OpenGL，然后输出到编码器的InputSurface上，来实现整套编码流程。

**2\. 视频播放**

任何视频类App都会涉及视频播放，从录制、剪辑再到播放，构成完整的视频体验。对于要播放一个MP4文件，最简单的方式莫过于直接使用系统的 [MediaPlayer](https://developer.android.com/reference/android/media/MediaPlayer)，只需要简单几行代码，就能直接播放视频。对于本地视频播放来说，这是最简单的实现方式，但实际上我们可能会有更复杂的需求：

- 需要播放的视频可能本身并不在本地，很多可能都是网络视频，有边下边播的需求。

- 播放的视频可能是作为视频编辑的一部分，在剪辑时需要实时预览视频特效。


对于第二种场景，我们可以简单配置播放视频的View为一个GLSurfaceView，有了OpenGL的环境，我们就可以在这上实现各种特效、滤镜的效果了。而对于视频编辑常见的快进、倒放之类的播放配置，MediaPlayer也有直接的接口可以设置。

更为常见的是第一种场景，例如一个视频流界面，大部分视频都是在线视频，虽然MediaPlayer也能实现在线视频播放，但实际使用下来，会有两个问题：

- 通过设置MediaPlayer视频URL方式下载下来的视频，被放到了一个私有的位置，App不容易直接访问，这样会导致我们没法做视频预加载，而且之前已经播放完、缓冲完的视频，也不能重复利用原有缓冲内容。

- 同视频剪辑直接使用MediaExtractor返回的数据问题一样，MediaPlayer同样无法精确seek，只能seek到有关键帧的地方。


对于第一个问题，我们可以通过视频URL代理下载的方式来解决，通过本地使用Local HTTP Server的方式代理下载到一个指定的地方。现在开源社区已经有很成熟的项目实现，例如 [AndroidVideoCache](http://AndroidVideoCache)。

而对于第二个问题来说，没法精确seek的问题在有些App上是致命的，产品可能无法接受这样的体验。那同视频编辑一样，我们只能直接基于MediaCodec来自行实现播放器，这部分内容就比较复杂了。当然你也可以直接使用Google开源的 [ExoPlayer](https://github.com/google/ExoPlayer)，简单又快捷，而且也能支持设置在线视频URL。

看似所有问题都有了解决方案，是不是就万事大吉了呢？

常见的网络边下边播视频的格式都是MP4，但有些视频直接上传到服务器上的时候，我们会发现无论是使用MediaPlayer还是ExoPlayer，似乎都只能等待到整个视频都下载完才能开始播放，没有达到边下边播的体验。这个问题的原因实际上是因为MP4的格式导致的，具体来看，是跟MP4 [格式](http://l.web.umkc.edu/lizhu/teaching/2016sp.video-communication/ref/mp4.pdf) 中的moov有关。

![](https://static001.geekbang.org/resource/image/64/42/6439de8111b1ad7173291c0723071142.png?wh=1172*330)

MP4格式中有一个叫作moov的地方存储这当前MP4文件的元信息，包括当前MP4文件的音轨视轨格式、视频长度、播放速率、视轨关键帧位置偏移量等重要信息，MP4文件在线播放的时候，需要moov中的信息才能解码音轨视轨。

而上述问题发生的原因在于，当moov在MP4文件尾部的时候，播放器没有足够的信息来进行解码，因此视频变得需要直接下载完之后才能解码播放。因此，要实现MP4文件的边下边播，则需要将moov放到文件头部。目前来说，业界已经有非常成熟的工具， [FFmpeg](https://ffmpeg.org/ffmpeg-formats.html#Options-8) 跟 [mp4v2](https://code.google.com/archive/p/mp4v2/) 都可以将一个MP4文件的moov提前放到文件头部。例如使用FFmpeg，则是如下命令：

```
ffmpeg -i input.mp4 -movflags faststart -acodec copy -vcodec copy output.mp4

```

使用 `-movflags faststart`，我们就可以把视频文件中的moov提前了。

另外，如果想要检测一个MP4的moov是否在前面，可以使用类似 [AtomicParsley](http://atomicparsley.sourceforge.net/) 的工具来检测。

在视频播放的实践中，除了MP4格式来作为边下边播的格式以外，还有更多的场景需要使用其他格式，例如m3u8、FLV之类，业界在客户端中常见的实现包括 [ijkplayer](https://github.com/bilibili/ijkplayer)、 [ExoPlayer](https://github.com/google/ExoPlayer)，有兴趣的同学可以参考下它们的实现。

## 音视频开发的学习之路

音视频相关开发涉及面很广，今天我也只是简单介绍一下其中基本的架构，如果想继续深入这个领域发展，从我个人学习的经历来看，想要成为一名合格的开发者，除了基础的Android开发知识以外，还要深入学习，我认为还需要掌握下面的技术栈。

**语言**

- C/C++：音视频开发经常需要跟底层代码打交道，掌握C/C++是必须的技能。这方面资料很多，相信我们都能找到。

- ARM NEON汇编：这是一项进阶技能，在视频编解码、各种帧处理低下时很多都是利用NEON汇编加速，例如FFmpeg/libyuv底层都大量利用了NEON汇编来加速处理过程。虽说它不是必备技能，但有兴趣也可以多多了解，具体资料可以参考ARM社区的 [教程](https://community.arm.com/processors/b/blog/posts/coding-for-neon---part-1-load-and-stores)。


**框架**

- [FFmpeg](https://ffmpeg.org/)：可以说是业界最出名的音视频处理框架了，几乎囊括音视频开发的所有流程，可以说是必备技能。

- [libyuv](https://chromium.googlesource.com/libyuv/libyuv/)：Google开源的YUV帧处理库，因为摄像头输出、编解码输入输出也是基于YUV格式，所以也经常需要这个库来操作数据（FFmpeg也有提供了这个库里面所有的功能，在 [libswscale](https://www.ffmpeg.org/doxygen/2.7/swscale_8h.html) 都可以找到类似的实现。不过这个库性能更好，也是基于NEON汇编加速）。

- [libx264](https://www.videolan.org/developers/x264.html)/ [libx265](http://x265.org/)：目前业界最为广泛使用的H.264/H.265软编解码库。移动平台上虽然可以使用硬编码，但很多时候出于兼容性或画质的考虑，因为不少低端的Android机器，在低码率的场景下还是软编码的画质会更好，最终可能还是得考虑使用软编解码。

- [OpenGL ES](https://www.khronos.org/opengles/)：当今，大部分视频特效、美颜算法的处理，最终渲染都是基于GLES来实现的，因此想要深入音视频的开发，GLES是必备的知识。另外，除了GLES以外， [Vulkan](https://www.khronos.org/vulkan/) 也是近几年开始发展起来的一个更高性能的图形API，但目前来看，使用还不是特别广泛。

- [ExoPlayer](https://github.com/google/ExoPlayer)/ [ijkplayer](https://github.com/bilibili/ijkplayer)：一个完整的视频类App肯定会涉及视频播放的体验，这两个库可以说是当下业界最为常用的视频播放器了，支持众多格式、协议，如果你想要深入学习视频播放处理，它们几乎也算是必备技能。


从实际需求出发，基于上述技术栈，我们可以从下面两条路径来深入学习。

**1\. 视频相关特效开发**

直播、小视频相关App目前越来越多，几乎每个App相关的特效，往往都是利用OpenGL本身来实现。对于一些简单的特效，可以使用类似 [Color Look Up Table](https://en.wikipedia.org/wiki/3D_lookup_table) 的技术，通过修改素材配合Shader来查找颜色替换就能实现。如果要继续学习更加复杂的滤镜，推荐你可以去 [shadertoy](https://www.shadertoy.com/) 学习参考，上面有非常多Shader的例子。

而美颜、美型相关的效果，特别是美型，需要利用人脸识别获取到关键点，对人脸纹理进行三角划分，然后再通过Shader中放大、偏移对应关键点纹理坐标来实现。如果想要深入视频特效类的开发，我推荐可以多学习OpenGL相关的知识，这里会涉及很多优化点。

**2\. 视频编码压缩算法**

H.264/H.265都是非常成熟的视频编码标准，如何利用这些视频编码标准，在保证视频质量的前提下，将视频大小最小化，从而节省带宽，这就需要对视频编码标准本身要有非常深刻的理解。这可能是一个门槛相对较高的方向，我也尚处学习阶段，有兴趣的同学可以阅读相关编码标准的文档。

欢迎你点击“请朋友读”，把今天的内容分享给好友，邀请他一起学习。我也为认真思考、积极分享的同学准备了丰厚的“学习加油礼包”，期待与你一起切磋进步哦。