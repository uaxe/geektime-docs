你好，我是刘歧。

学到这里，不知道你有没有发现一个事情：从开始到现在，我们讲得最多的就是FFmpeg的命令行工具和参数，很少讲到界面操作。其实在做视频转码时，大多数人除了经常用FFmpeg之外，还会用一些免费的带界面的转码工具，这节课我除了会教你如何使用FFmpeg转码之外，还会给你介绍一个非常好用的本地化转码工具Handbrake。

## 如何使用FFmpeg转码？

在我们专栏开篇的基础部分，我给你讲过音视频相关的图像色彩、编解码、封装（Mux）与解封装（Demux）的基本原理。 [第7节课](https://time.geekbang.org/column/article/548420)，我又给你讲了如何高效地使用FFmpeg帮助信息和文档。在前面这些内容的基础上，我们来学以致用，讲一讲怎么用FFmpeg转码。

首先我们需要确定我们在转码的时候输出文件的应用场景。假如你是希望传到快手这样的内容发布平台，那么我们是需要转换成平台要求的转码规格的。既然要转码，就需要先看一下自己电脑系统的环境是否支持这一操作，比如使用CPU做转码，电脑会不会变得很慢，如果电脑上有GPU，使用GPU转码的话，CPU理所当然地会空出来，这样就不会影响我们继续使用电脑做其他的事情了。

我们先来了解一下怎么使用CPU做转码。

### 用 CPU 转码

使用CPU转码的话，通常是用CPU解码，然后用libx264、libx265、librav1e之类的编码器编码，也叫软编码。当然也有人用OpenH264或者其他自己定制的编码器，因为编码参数大多数是与编码的参考标准对应的，通用的或者常见的编码参数在libx264、libx265、librav1e里面相差无几，所以这里为了简洁一点，我使用FFmpeg与libx264来做软编码。我们先来回顾一下转码的基本操作流程。

![图片](https://static001.geekbang.org/resource/image/54/f3/54a1e6a1264b0c1a54f84c743b8a2ff3.png?wh=1142x492)

首先是读取文件后解析文件，然后对文件进行解封装，也就是demux。将解封装后的音视频流数据进行解码，得到原始数据，也就是我们 [第1节课](https://time.geekbang.org/column/article/541546) 讲的YUV数据或者PCM数据，然后用我们设置的目标编码对应的编码器进行编码，编码后的数据写入音频流或者视频流里，封装音频流或者视频流，写入文件里。

回顾完流程之后，我们用 [第7节课](https://time.geekbang.org/column/article/548420) 学到的知识查看一下我们能如何使用libx264。首先看一下libx264在FFmpeg里面支持的参数。

使用命令行ffmpeg -h encoder=libx264查看一下参数内容。

```plain
Encoder libx264 [libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10]:
    General capabilities: dr1 delay threads
    Threading capabilities: other
    Supported pixel formats: yuv420p yuvj420p yuv422p yuvj422p yuv444p yuvj444p nv12 nv16 nv21 yuv420p10le yuv422p10le yuv444p10le nv20le gray gray10le
libx264 AVOptions:
  -preset            <string>     E..V....... Set the encoding preset (cf. x264 --fullhelp) (default "medium")
  -tune              <string>     E..V....... Tune the encoding params (cf. x264 --fullhelp)
  -profile           <string>     E..V....... Set profile restrictions (cf. x264 --fullhelp)
  -fastfirstpass     <boolean>    E..V....... Use fast settings when encoding first pass (default true)
  -level             <string>     E..V....... Specify level (as defined by Annex A)
  -passlogfile       <string>     E..V....... Filename for 2 pass stats
  -wpredp            <string>     E..V....... Weighted prediction for P-frames
  -a53cc             <boolean>    E..V....... Use A53 Closed Captions (if available) (default true)
  -x264opts          <string>     E..V....... x264 options
  -crf               <float>      E..V....... Select the quality for constant quality mode (from -1 to FLT_MAX) (default -1)
  -crf_max           <float>      E..V....... In CRF mode, prevents VBV from lowering quality beyond this point. (from -1 to FLT_MAX) (default -1)
  -qp                <int>        E..V....... Constant quantization parameter rate control method (from -1 to INT_MAX) (default -1)
  -aq-mode           <int>        E..V....... AQ method (from -1 to INT_MAX) (default -1)
     none            0            E..V.......
     variance        1            E..V....... Variance AQ (complexity mask)
     autovariance    2            E..V....... Auto-variance AQ
     autovariance-biased 3            E..V....... Auto-variance AQ with bias to dark scenes
  -aq-strength       <float>      E..V....... AQ strength. Reduces blocking and blurring in flat and textured areas. (from -1 to FLT_MAX) (default -1)
  -psy               <boolean>    E..V....... Use psychovisual optimizations. (default auto)
  -psy-rd            <string>     E..V....... Strength of psychovisual optimization, in <psy-rd>:<psy-trellis> format.
  -rc-lookahead      <int>        E..V....... Number of frames to look ahead for frametype and ratecontrol (from -1 to INT_MAX) (default -1)
  -weightb           <boolean>    E..V....... Weighted prediction for B-frames. (default auto)
  -weightp           <int>        E..V....... Weighted prediction analysis method. (from -1 to INT_MAX) (default -1)
     none            0            E..V.......
     simple          1            E..V.......
     smart           2            E..V.......
  -ssim              <boolean>    E..V....... Calculate and print SSIM stats. (default auto)
  -intra-refresh     <boolean>    E..V....... Use Periodic Intra Refresh instead of IDR frames. (default auto)
  -bluray-compat     <boolean>    E..V....... Bluray compatibility workarounds. (default auto)
  -b-bias            <int>        E..V....... Influences how often B-frames are used (from INT_MIN to INT_MAX) (default INT_MIN)
  -b-pyramid         <int>        E..V....... Keep some B-frames as references. (from -1 to INT_MAX) (default -1)
     none            0            E..V.......
     strict          1            E..V....... Strictly hierarchical pyramid
     normal          2            E..V....... Non-strict (not Blu-ray compatible)
  -mixed-refs        <boolean>    E..V....... One reference per partition, as opposed to one reference per macroblock (default auto)
  -8x8dct            <boolean>    E..V....... High profile 8x8 transform. (default auto)
  -fast-pskip        <boolean>    E..V....... (default auto)
  -aud               <boolean>    E..V....... Use access unit delimiters. (default auto)
  -mbtree            <boolean>    E..V....... Use macroblock tree ratecontrol. (default auto)
  -deblock           <string>     E..V....... Loop filter parameters, in <alpha:beta> form.
  -cplxblur          <float>      E..V....... Reduce fluctuations in QP (before curve compression) (from -1 to FLT_MAX) (default -1)
  -partitions        <string>     E..V....... A comma-separated list of partitions to consider. Possible values: p8x8, p4x4, b8x8, i8x8, i4x4, none, all
  -direct-pred       <int>        E..V....... Direct MV prediction mode (from -1 to INT_MAX) (default -1)
     none            0            E..V.......
     spatial         1            E..V.......
     temporal        2            E..V.......
     auto            3            E..V.......
  -slice-max-size    <int>        E..V....... Limit the size of each slice in bytes (from -1 to INT_MAX) (default -1)
  -stats             <string>     E..V....... Filename for 2 pass stats
  -nal-hrd           <int>        E..V....... Signal HRD information (requires vbv-bufsize; cbr not allowed in .mp4) (from -1 to INT_MAX) (default -1)
     none            0            E..V.......
     vbr             1            E..V.......
     cbr             2            E..V.......
  -avcintra-class    <int>        E..V....... AVC-Intra class 50/100/200/300/480 (from -1 to 480) (default -1)
  -me_method         <int>        E..V....... Set motion estimation method (from -1 to 4) (default -1)
     dia             0            E..V.......
     hex             1            E..V.......
     umh             2            E..V.......
     esa             3            E..V.......
     tesa            4            E..V.......
  -motion-est        <int>        E..V....... Set motion estimation method (from -1 to 4) (default -1)
     dia             0            E..V.......
     hex             1            E..V.......
     umh             2            E..V.......
     esa             3            E..V.......
     tesa            4            E..V.......
  -forced-idr        <boolean>    E..V....... If forcing keyframes, force them as IDR frames. (default false)
  -coder             <int>        E..V....... Coder type (from -1 to 1) (default default)
     default         -1           E..V.......
     cavlc           0            E..V.......
     cabac           1            E..V.......
     vlc             0            E..V.......
     ac              1            E..V.......
  -b_strategy        <int>        E..V....... Strategy to choose between I/P/B-frames (from -1 to 2) (default -1)
  -chromaoffset      <int>        E..V....... QP difference between chroma and luma (from INT_MIN to INT_MAX) (default 0)
  -sc_threshold      <int>        E..V....... Scene change threshold (from INT_MIN to INT_MAX) (default -1)
  -noise_reduction   <int>        E..V....... Noise reduction (from INT_MIN to INT_MAX) (default -1)
  -udu_sei           <boolean>    E..V....... Use user data unregistered SEI if available (default false)
  -x264-params       <dictionary> E..V....... Override the x264 configuration using a :-separated list of key=value parameters

```

从帮助信息中可以看到，libx264编码支持的图像色彩格式主要包括yuv420p、yuvj420p、yuv422p、yuvj422p、yuv444p、yuvj444p、nv12、nv16、nv21、yuv420p10le、yuv422p10le、yuv444p10le、nv20le、gray、gray10le，我们通常统一编码成yuv420p即可。如果确定播放器可以支持HDR的话，也可以考虑用yuv420p10le。但是如果想要在Web浏览器上正常播放出来的话，yuv420p是最稳定的格式。

为了解决设置编码参数时参数太多、太琐碎的问题，libx264提供了预置模板preset，在FFmpeg里默认用的是medium模板，也就是平衡画质与编码速度的最优选择。除了medium，还可以按照帮助信息里面的提示，通过使用x264 --fullhelp查看x264的其他preset，例如还有ultrafast、superfast、veryfast、faster、fast、slow、slower、veryslow、placebo。

除了preset模板，还有调优类型的模板tune，包括film、animation、grain、stillimage、psnr、ssim、fastdecode、zerolatency等不同的模版。

![图片](https://static001.geekbang.org/resource/image/ee/09/ee8dd86b8e2c941a3b937acae374eb09.png?wh=1560x888)

不同的模板支持的参数也略有差别，比如视频编码想做画面延迟低的直播流的话，可以考虑设置tune为zerolatency。因为zerolatency模板里已经包含了低延迟编码的参数。

![图片](https://static001.geekbang.org/resource/image/41/a2/414dd247876e469c13b6440d197374a2.png?wh=1856x806)

其中宏块树是一种视频编码结构，在编码时它可以增加slice处理的层数，降低视频编码的码率，但是复杂度会略有提升，所以耗时也会增加一些。你可以结合极客时间上 [视频编码](https://time.geekbang.org/column/article/468091) 及 [帧内预测](https://time.geekbang.org/column/article/463775) 相关的课程来理解，这里我就不展开说了。

slice的的意思是将一帧图像切成多个切片，然后将多个片放到多个线程里处理，从而达到并发处理的的目的。因为lookahead是0，不需要提前预存多个帧做缓存，也没有双向参考帧B帧，不需要预读多个帧做缓存，所以最大限度地降低了帧缓存引起的画面延迟。

除了以上两类模板，在给视频转码做转码的时候，有时也会被要求转成恒定码率的视频流，也就是我们常说的CBR，这个CBR可以通过参数nal-hrd cbr来设置，但是实际的码率不一定能够控制得很好，所以通常会搭配FFmpeg的maxrate、minrate与bufsize来精确地控制码率，一般bufsize控制比maxrate小大概1/3 ~ 1/2即可，达到的效果如图所示：

![图片](https://static001.geekbang.org/resource/image/9c/ba/9ca113092d51469d046ef3115d846aba.png?wh=1920x990)

如果使用当前FFmpeg里面的libx264参数无法达到要求，但用x264没问题的话，我们就可以通过FFmpeg预留的x264opts来设置更多x264的参数，例如设置x264为OpenGOP模式，就需要使用参数-x264opts “open-gop=1”，来达到使用OpenGOP的编码模式的目的。

在同画质下，使用OpenGOP比CloseGOP码率更低一些，但是也可能会引入一些不稳定因素，例如视频切片的时候找不到关键帧，这一点需要我们注意。

说了这么多，接下来我们实际操练一下，使用FFmpeg命令行来做转码。

你先下载一个《大雄兔》或者《钢铁之泪》的电影，这两部电影是开放版权的，在互联网上能够搜到对应的视频文件，自己测试的时候可以随便用。先输入命令行：

```plain
ffmpeg -i ~/Movies/Test/ToS-4k-1920.mov -pix_fmt yuv420p -vcodec libx264 -nal-hrd cbr -tune zerolatency -preset superfast -maxrate 900k -minrate 890k -bufsize 300k -x264opts "open-gop=1" output.ts

```

命令行执行后，输出的内容是这样的：

```plain
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from '/Users/liuqi/Movies/Test/ToS-4k-1920.mov':
  Metadata:
    major_brand     : qt
    minor_version   : 512
    compatible_brands: qt
    encoder         : Lavf54.29.104
  Duration: 00:12:14.17, start: 0.000000, bitrate: 8051 kb/s
  Stream #0:0[0x1](eng): Video: h264 (High) (avc1 / 0x31637661), yuv420p(progressive), 1920x800 [SAR 1:1 DAR 12:5], 7862 kb/s, 24 fps, 24 tbr, 24 tbn (default)
    Metadata:
      handler_name    : VideoHandler
      vendor_id       : FFMP
      encoder         : libx264
  Stream #0:1[0x2](eng): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 182 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
      vendor_id       : [0][0][0][0]
Stream mapping:
  Stream #0:0 -> #0:0 (h264 (native) -> h264 (libx264))
  Stream #0:1 -> #0:1 (aac (native) -> mp2 (native))
Press [q] to stop, [?] for help
[libx264 @ 0x619000006480] CBR HRD requires constant bitrate
[libx264 @ 0x619000006480] using SAR=1/1
[libx264 @ 0x619000006480] using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX FMA3 BMI2 AVX2
[libx264 @ 0x619000006480] profile High, level 4.0, 4:2:0, 8-bit
Output #0, mpegts, to 'output.ts':
  Metadata:
    major_brand     : qt
    minor_version   : 512
    compatible_brands: qt
    encoder         : Lavf59.25.100
  Stream #0:0(eng): Video: h264, yuv420p(progressive), 1920x800 [SAR 1:1 DAR 12:5], q=2-31, 24 fps, 90k tbn (default)
    Metadata:
      handler_name    : VideoHandler
      vendor_id       : FFMP
      encoder         : Lavc59.33.100 libx264
    Side data:
      cpb: bitrate max/min/avg: 900000/0/0 buffer size: 300000 vbv_delay: N/A
  Stream #0:1(eng): Audio: mp2, 44100 Hz, stereo, s16, 384 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
      vendor_id       : [0][0][0][0]
      encoder         : Lavc59.33.100 mp2
frame=  240 fps=0.0 q=39.0 Lsize=     778kB time=00:00:09.99 bitrate= 637.3kbits/s speed=11.5x
video:218kB audio:469kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 13.097445%
[libx264 @ 0x619000006480] frame I:3     Avg QP:16.91  size: 16651
[libx264 @ 0x619000006480] frame P:237   Avg QP: 6.68  size:   733
[libx264 @ 0x619000006480] mb I  I16..4: 71.5% 23.2%  5.3%
[libx264 @ 0x619000006480] mb P  I16..4:  0.3%  0.7%  0.0%  P16..4:  2.3%  0.0%  0.0%  0.0%  0.0%    skip:96.7%
[libx264 @ 0x619000006480] 8x8 transform intra:43.0% inter:46.2%
[libx264 @ 0x619000006480] coded y,uvDC,uvAC intra: 19.4% 18.2% 3.9% inter: 0.1% 0.3% 0.0%
[libx264 @ 0x619000006480] i16 v,h,dc,p: 60%  9% 24%  7%
[libx264 @ 0x619000006480] i8 v,h,dc,ddl,ddr,vr,hd,vl,hu: 12% 15% 27%  9%  6%  7%  9%  6%  8%
[libx264 @ 0x619000006480] i4 v,h,dc,ddl,ddr,vr,hd,vl,hu: 20% 19% 29%  5%  5%  6%  8%  3%  5%
[libx264 @ 0x619000006480] i8c dc,h,v,p: 78% 10% 10%  2%
[libx264 @ 0x619000006480] Weighted P-Frames: Y:1.3% UV:0.0%
[libx264 @ 0x619000006480] kb/s:178.99

```

从输出的内容中可以看到，编码的帧类型里只有I帧和P帧，设置的CBR模式已经生效，你也可以尝试把输入文件改成直播推流。

但是需要注意的是，设置视频编码流为CloseGOP，关键帧间隔的-g设置成fps的一半即可，fps需要使用参数-r:v来设置，例如设置-r:v 为 30，就是 30 fps，那么-g可以设置为15，也就是每隔15帧会有一个关键帧，这样可以达到0.5秒钟一个关键帧。当然，实际上这么做会很浪费带宽，常规的秀场直播设置2~5秒钟一个关键帧就可以了。

如果我们平时用CPU转码的话，对CPU的消耗会比较高，转码的时候电脑做其他事情会比较慢，一般电脑上有GPU的话直接选择用GPU转码，这样可以节省一些CPU计算资源。

### 用GPU转码

用GPU转码之前，你需要先确认一下自己当前电脑里的GPU是否可以做转码，然后安装对应的音视频编解码环境（GPU相关的驱动、软件、开发库等）。

FFmpeg支持的硬件加速方案，按照各OS厂商、Chip厂商特定方案，还有行业联盟定义的标准来分的话，大致可以分成3类：

- 操作系统：包括Windows、Linux、macOS /iOS、Android等。
- Chip厂商的特定方案：包括Intel、AMD、Nvidia等。
- 行业标准或事实标准：包括OpenMAX和OpenCL、Vulkan、OpenGL还有cuda等。

这只是一个粗略的分类，很多时候，这几者之间纵横交错，联系密切，之间的关系并非像列出的这般泾渭分明。

下面就是Windows环境下，在AMD、Intel、Nvidia 的GPU上用dxva2和d3d11va来解码，再使用厂商提供的编码器编码的例子。

1. AMD AMF

```plain
ffmpeg -hwaccel dxva2 -hwaccel_output_format dxva2_vld -i <video> -c:v h264_amf -b:v 2M -y out.mp4
ffmpeg -hwaccel d3d11va -hwaccel_output_format d3d11 -i <video> -c:v h264_amf -b:v 2M -y out.mp4

```

2. Intel QSV

```plain
ffmpeg -hwaccel dxva2 -hwaccel_output_format dxva2_vld -i <video> -c:v h264_qsv -vf hwmap=derive_device=qsv,format=qsv -b:v 2M -y out.mp4
ffmpeg -hwaccel d3d11va -hwaccel_output_format d3d11 -i <video> -c:v h264_qsv -vf hwmap=derive_device=qsv,format=qsv -b:v 2M -y out.mp4

```

3. Nvidia NVENC

```plain
ffmpeg -hwaccel d3d11va -hwaccel_output_format d3d11 -i <video> -c:v h264_nvenc -b:v 2M -y out.mp4

```

比如我自己本机是苹果电脑，那么我使用videotoolbox做转码就可以。

```plain
./ffmpeg -vcodec h264_vda -i input.mp4 -vcodec h264_videotoolbox -b:v 2000k output.mp4

```

更多GPU转码或音视频滤镜处理相关的操作，你可以通过GPU对应的开发者官方网站了解，当然，FFmpeg也提供了一些快速上手的 [操作手册](https://trac.ffmpeg.org/wiki/HWAccelIntro)，你也可以作为参考。

讲到这里，我们一直在用命令做转码，还要记好多参数，有没有一种更简单的方式来实现转码呢？当然有，接下来我们看一下带界面的转码工具——Handbrake。

## 使用Handbrake转码

我们打开Handbrake之后，先选择一个我们想要转码的视频文件，然后就会顺利打开Handbrake的界面。

![图片](https://static001.geekbang.org/resource/image/2c/8d/2ccf112d0afdb95b3083810eaf0f958d.png?wh=1920x1251)

设置基础能力部分有很多预置模板，点“预设”的话，我们可以把参数调整为适配最终输出的格式。

![图片](https://static001.geekbang.org/resource/image/88/1d/88861174a525dcd9e38305c73a57161d.png?wh=1640x1486)

不用预设的参数也可以自己定义，例如自己定制输出尺寸、滤镜以及视频编码参数，也有对应的使用FFmpeg做转码时相关参数的设置项。

![图片](https://static001.geekbang.org/resource/image/81/65/817de4be011d0d613bd1df7fab7f8065.png?wh=1920x868)

如果选择使用x264编码的话，也有预设模板和调优模板。

![图片](https://static001.geekbang.org/resource/image/14/e6/148dc8951fe92bd78f4f0c0c24124ee6.png?wh=1920x651)

由于是界面操作并且已经汉化，所以比较容易上手，你可以自己下载一个试试看，Handbrake设置还有更多黑科技，你可以在使用过程中慢慢挖掘。

## 小结

最后，我们总结一下这节课的内容吧！

![图片](https://static001.geekbang.org/resource/image/88/35/88ac9e954ecf616315429756344e9535.png?wh=1920x1429)

给视频做转码时，我们最常用的工具就是FFmpeg，使用FFmpeg转码的时候，我们既可以选择使用软编码做转码，也可以使用硬编码做转码。

具体使用哪一种需要你根据自己的使用场景来决定， **如果是CPU特别富裕的话，使用软编码是一个不错的选择。** 因为软编码对画质相关调优的参数自主可控性更高一些，硬编码因硬件设计比较固定，所以有些时候画质调优方面比较受限，例如对不同视频应用场景的高清低码率相关的调优，使用硬转码效果会比软转码差一些。同时因可控性受限，硬转码的码率普遍会比软转码的视频码率高。

除了使用FFmpeg来做软硬转码之外，我们还可以 **借助Handbrake这个界面工具**，里面的参数设置我们可以使用它给出的模版，也可以自己根据需要去定义。

## 思考题

结合前面讲过的知识，你可以自己分析一下x264的编码参数，按照这样的参数输出视频编码。

1. 每秒钟30fps的720p的视频。
2. 2秒钟一个关键帧（GOP）。
3. 每两个P帧（包括I帧）之间两个B帧。

欢迎在评论区留下你的答案，也欢迎你把这节课分享给需要的朋友。我们下节课再见！