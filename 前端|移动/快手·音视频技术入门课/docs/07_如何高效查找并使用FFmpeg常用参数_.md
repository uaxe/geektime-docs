你好，我是刘歧。

我们讲述直播推流的时候曾简单介绍过 [FFmpeg推直播流](https://time.geekbang.org/column/article/546485) 的操作，但是并不是特别全面，遇到一些问题的时候我们还是无法很好地解决。有时候，我们想要使用FFmpeg的某个功能，但不知道怎么查找，甚至可能不知道FFmpeg是否包含我们需要的能力。那么这节课我们会更全面地介绍FFmpeg中常用的参数，还有遇到问题的时候如何确认FFmpeg是否可以达到我们预期的目的。

如果你是第一次使用FFmpeg，肯定会有很多疑惑，尤其是看到命令行的一堆参数之后。所以这节课我会一步一步引导你先学会使用FFmpeg，最后让你拥有自己深度挖掘FFmpeg里面各种黑科技的能力。先吃到“鱼”，然后学会“钓鱼”，之后你就可以自己慢慢收获各种“鱼”了。

## FFmpeg 输入输出组成

FFmpeg的工作原理比较简单，它没有指定输出文件的参数。一般的工具都会带一个-o来指定输出文件，但FFmpeg不是，它不用-o指定输出，FFmpeg自己会分析命令行然后确定输出。例如我们输入这么一段命令：

```plain
ffmpeg -i i.mp4 a.mp4 -vcodec mpeg4 b.mp4

```

这段命令会输出两个文件，分别是a.mp4和b.mp4。

```plain
(base) liuqi05:xx liuqi$ ls
a.mp4 b.mp4
(base) liuqi05:xx liuqi$

```

因为b.mp4的输出参数部分我指定了vcodec为mpeg4，所以b.mp4的视频编码采用的是mpeg4。而a.mp4的输出部分我没有指定任何信息，所以a.mp4使用的是mp4格式默认的视频编码，也就是H.264编码。我们一起来看一下命令行执行的输出信息。

```plain
Output #0, mp4, to 'a.mp4':
  Metadata:
    major_brand     : mp42
    minor_version   : 512
    compatible_brands: mp42iso2avc1mp41
    encoder         : Lavf59.25.100
  Stream #0:0(und): Video: h264 (avc1 / 0x31637661), yuv420p(tv, bt709, progressive), 1920x800 [SAR 1:1 DAR 12:5], q=2-31, 24 fps, 12288 tbn (default)
    Metadata:
      creation_time   : 2022-04-01T09:59:10.000000Z
      handler_name    : VideoHandler
      vendor_id       : [0][0][0][0]
      encoder         : Lavc59.33.100 libx264
    Side data:
      cpb: bitrate max/min/avg: 0/0/0 buffer size: 0 vbv_delay: N/A
  Stream #0:1(eng): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 128 kb/s (default)
    Metadata:
      creation_time   : 2022-04-01T09:59:10.000000Z
      handler_name    : Stereo
      vendor_id       : [0][0][0][0]
      encoder         : Lavc59.33.100 aac
Output #1, mp4, to 'b.mp4':
  Metadata:
    major_brand     : mp42
    minor_version   : 512
    compatible_brands: mp42iso2avc1mp41
    encoder         : Lavf59.25.100
  Stream #1:0(und): Video: mpeg4 (mp4v / 0x7634706D), yuv420p(tv, bt709, progressive), 1920x800 [SAR 1:1 DAR 12:5], q=2-31, 200 kb/s, 24 fps, 12288 tbn (default)
    Metadata:
      creation_time   : 2022-04-01T09:59:10.000000Z
      handler_name    : VideoHandler
      vendor_id       : [0][0][0][0]
      encoder         : Lavc59.33.100 mpeg4
    Side data:
      cpb: bitrate max/min/avg: 0/0/200000 buffer size: 0 vbv_delay: N/A
  Stream #1:1(eng): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 128 kb/s (default)
    Metadata:
      creation_time   : 2022-04-01T09:59:10.000000Z
      handler_name    : Stereo
      vendor_id       : [0][0][0][0]
      encoder         : Lavc59.33.100 aac
frame=  116 fps= 73 q=28.0 q=2.0 size=       0kB time=00:00:05.22 bitrate=   0.1kbits/s speed=3.28x

```

可以看到，FFmpeg的输入可以是多个，输出也可以是多个，但是每一个输出都会根据输入的信息做一个参数复制。遇到不用于输出封装格式的默认codec，FFmpeg会转成默认的封装格式对应的编码。

如果想要指定编码，每个输出格式都需要输出对应的编码，如果不想重新编码，可以使用-vcodec copy，-acodec copy、-scodec copy这样的参数，来进行只转封装不转码（做解码后再编码）的操作。不做视频转码操作的话，会节省CPU的计算资源，CPU占用率会降低很多，但是如果输入的视频码率特别高的话，文件也会特别大，这种情况做一下转码还是有必要的。

FFmpeg的命令行参数分布通常是这样：

```plain
ffmpeg [第一个输入文件对应的解析参数] -i 第一个输入文件名 [第二个输入文件对应的解析参数 ] -i 第二个输入文件名 [如果有第三个文件输入] [-i] [如果有第三个文件] [第一个输出文件对应的参数] [第一个输出文件名] [第二个输出文件对应的参数] [第二个输出文件名] [第三个输出文件对应的参数] [第三个输出文件名]

```

FFmpeg的输入输出组成看上去比较简单，但是参数和官方文档的使用说明还是太多，怎么办呢？没关系，多数的畏难情绪是因为不了解。接下来，我们看一下FFmpeg的参数组成，了解清楚它的参数内容，相信你的疑虑就会打消大半了。

## 如何查找各个模块参数的帮助信息？

当我们查看FFmpeg的帮助信息和官方的文档的时候，第一感觉是文档和参数太多了，一时间根本无从下手。其实FFmpeg官方文档和帮助信息中的内容并不多，主要取决于你怎么看、怎么用。比如，我们使用命令行的时候，能够看到FFmpeg参数的情况。

```plain
ffmpeg --help

```

如果认真看帮助信息的话，你就会发现开头还有一部分关于查看帮助的方法。

```plain
Getting help:
    -h      -- print basic options
    -h long -- print more options
    -h full -- print all options (including all format and codec specific options, very long)
    -h type=name -- print all options for the named decoder/encoder/demuxer/muxer/filter/bsf/protocol
    See man ffmpeg for detailed description of the options.

```

查看帮助，我们可以看到基础版本，也就是–help，而–help还有两个常用参数，long和full。long这个参数，除了可以查看基础帮助信息之外，还能查看更多高级操作的帮助内容；full可以输出所有的帮助信息，可以全部打印出来查看。

下面还有个type=name的方式查看帮助信息，正如前面几节课我们讲到的FFmpeg一样，FFmpeg是包含了封装与解封装、编码与解码、滤镜以及传输协议模块的，所以我们可以通过type=name来过滤掉我们不需要的信息，只查看我们会用到的模块。例如我想查看FLV的封装，那就可以输入帮助操作。

```plain
ffmpeg -h muxer=flv

Muxer flv [FLV (Flash Video)]:
    Common extensions: flv.
    Mime type: video/x-flv.
    Default video codec: flv1.
    Default audio codec: adpcm_swf.
flv muxer AVOptions:
  -flvflags          <flags>      E.......... FLV muxer flags (default 0)
     aac_seq_header_detect              E.......... Put AAC sequence header based on stream data
     no_sequence_end              E.......... disable sequence end for FLV
     no_metadata                  E.......... disable metadata for FLV
     no_duration_filesize              E.......... disable duration and filesize zero value metadata for FLV
     add_keyframe_index              E.......... Add keyframe index metadata

```

这样的话，我们得到的参数就比直接用ffmpeg --help full要简洁多了，只看到了我们想看到的部分。如果想要看编码对应的帮助信息，也可以用同样的方法，把muxer换成encoder就可以了。

```plain
ffmpeg -h encoder=libx264

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

比全部输出简洁多了，但是我们怎么确认我们使用的type名称是真实存在的呢？如果我直接输入ffmpeg -h encoder=helloworld，肯定是拿不到任何信息的，而且会返回错误。这个时候我们就需要从头部看FFmpeg的help信息了。

```plain
Print help / information / capabilities:
-L                  show license
-h topic            show help
-? topic            show help
-help topic         show help
--help topic        show help
-version            show version
-buildconf          show build configuration
-formats            show available formats
-muxers             show available muxers
-demuxers           show available demuxers
-devices            show available devices
-codecs             show available codecs
-decoders           show available decoders
-encoders           show available encoders
-bsfs               show available bit stream filters
-protocols          show available protocols
-filters            show available filters
-pix_fmts           show available pixel formats
-layouts            show standard channel layouts
-sample_fmts        show available audio sample formats
-dispositions       show available stream dispositions
-colors             show available color names
-sources device     list sources of the input device
-sinks device       list sinks of the output device
-hwaccels           show available HW acceleration methods

```

FFmpeg帮助信息中提供了一些查看各个模块的全部列表，例如我们如果想查看我们机器上的FFmpeg是否支持nvidia的H.264编码器的话，就可以通过参数ffmpeg -encoders来确认机器上当前安装的FFmpeg中是否涵盖了nvidia的H.264编码器。

```plain
ffmpeg -encoders|grep H.264

```

我把所有输出信息通过管道用grep过滤了一遍，得到的输出信息是这样的。

```plain
 V....D libx264              libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (codec h264)
 V....D libx264rgb           libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 RGB (codec h264)
 V....D h264_videotoolbox    VideoToolbox H.264 Encoder (codec h264)

```

从输出的内容中可以看到，我的机器上没有安装nvidia的H.264编码器，但是我机器上安装了lib264和h264\_videotoolbox的编码器，所以可以直接查看libx264或者h264\_videotoolbox的帮助信息。

**只要有针对性地查找帮助信息，就可以过滤掉很多我们不想看到的内容。** 另外，还有一小部分是常用的参数，接下来我们通过一些实际场景来学习一下。

## FFmpeg 公共基础参数

当我们使用FFmpeg时，有一些贯穿FFmpeg各个组件的核心参数，在我们查看帮助信息时就可以看到，help不带参数的话就会输出基础帮助信息。

基础帮助信息中包含了这几部分：

1. 公共操作部分

公共操作部分的参数主要包括把日志输出到日志文件的参数 -report，输出日志文件名的格式是ffmpeg-20220703-170736.log，也就是ffmpeg-年月日-时分秒.log的文件名格式。你可以使用命令行ffmpeg -report试验一下。

还可以将FFmpeg的日志输出到终端，通过-v参数来设置日志的级别，主要分为quiet、panic、fatal、error、warning、info、verbose、debug、trace9个级别，按先后顺序输出的内容越来越多。如果我们想看到全部的处理信息，用trace就可以。如果不特意设置的话，默认是info级别，所以我们看到的通常是info、warning、error以及更严重的错误信息。如果我们什么信息都不想看到，用quiet就能做到。

2. 每个文件主要操作部分

文件主要操作部分的参数除了我们前面课程提到的-codec、-c、-f之外，还可以使用-ss来定位文件的开始时间，通过-t来规定输出文件时间长度。

如果我们想做分片转码的话，就可以使用-ss和-t两个参数分隔视频文件。另外，要注意-ss指定的位置最好是关键帧位置。比如说，我们可以通过ffprobe -show\_packet input.mp4找到视频关键帧对应的pts位置，然后通过-ss定位到关键帧位置，-t设置为下一个关键帧减去当前关键帧位置的时间长度，这样就能完成切片了。

需要注意的是，-ss放在-i参数左侧来定位开始的位置会比放在右侧要快很多，但是放在-i左侧的话，定位通常不准确，但如果我们把-ss的时间点位设置为关键帧对应的点位，那定位就是准确的。另外，我们还可以使用-codec:v copy -an去掉音频，从而达到分离音视频的目的。

如果想给视频添加metadata信息的话，例如指定文件的标题等信息，可以通过-metadata参数来设置metadata。

我们通过命令行测一下效果。

```plain
ffmpeg -f lavfi -i testsrc=s=176x144 -metadata title="This Is A Test" -t 2 out.mp4

```

我们先确认一下输出的out.mp4文件是否包含了我们设定的Title“This Is A Test.”。

```plain
ffmpeg -i out.mp4

Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'out.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    title           : This Is A Test
    encoder         : Lavf58.77.100
  Duration: 00:00:02.00, start: 0.000000, bitrate: 49 kb/s
  Stream #0:0(und): Video: h264 (High 4:4:4 Predictive) (avc1 / 0x31637661), yuv444p, 176x144 [SAR 1:1 DAR 11:9], 44 kb/s, 25 fps, 25 tbr, 12800 tbn, 50 tbc (default)
    Metadata:
      handler_name    : VideoHandler
      vendor_id       : [0][0][0][0]

```

从输出的信息中可以看到文件里带有我们设定的title信息。

3. 视频操作部分

既然是做音视频处理，FFmpeg除了文件公共部分，还有视频操作公共部分的参数。比如说：

- -r:v设置视频的帧率；
- -vb设置视频码率；
- -vframes设置视频输出的帧数；
- -aspect设置视频的宽高比；
- -vn关闭视频流处理操作，也就是屏蔽视频流；
- -vf给视频做简单滤镜处理，简单滤镜处理一般不支持多图层、多输入、多输出的滤镜。

4. 音频操作部分

同样的，除了视频操作部分的参数，FFmpeg还有音频操作公共部分的参数，比如说：

- -ar设置音频采样率；
- -ab设置音频码率；
- -aframes设置音频输出的帧数；
- -ac设置音频的声道数量
- -an关闭音频流处理操作，也就是屏蔽音频流
- -af给音频做简单滤镜处理，简单滤镜处理一般不支持多图层、多输入、多输出的滤镜；
- -vol设置音频的音量。

![](https://static001.geekbang.org/resource/image/bf/c8/bfe09d7f10e2a5401b4e12ce849686c8.png?wh=1132x1921)

## FFmpeg 公共高级参数

前面我们讲到了一些基础操作部分，也提到了通过help long还可以查看到高级操作部分。高级操作部分是基于基础部分做的一些更高级的内容延伸。

-filter\_complex参数可以将音视频混合在一条参数字符串里进行操作，也可以输入、输出多个视频流和音频流。如果滤镜字符串太长的话，一条命令行可能会遇到很多麻烦，例如命令行支持的输入内容长度有最长限制，从而导致无法输入完整的FFmpeg命令参数，这时我们可以考虑使用外挂filter脚本来处理，使用参数-filter\_script能够解决这些问题。

-copytb参数设定timebase与输入的相同，确保时间戳不会跳变，当然这么做会有一定的风险，毕竟视频的MPEGTS封装格式与MP4的封装格式对应的timebase还是有差别的，如果强制使用相同的timebase则会引起时间戳间隔相关问题，严重的话甚至会引起丢帧。-force\_key\_frames在做编码的时候可以根据这个参数做强制关键帧设定，-force\_key\_frames支持表达式方式处理。FFmpeg的表达式处理可以参考 [FFmpeg官方文档](https://ffmpeg.org/ffmpeg-utils.html#Expression-Evaluation)。

## 小结

最后，我们来对这节课的内容做一个回顾吧！

FFmpeg常用的参数主要分为输入输出组成、公共基础参数、高级参数几方面内容，这节课学习这些参数的用法除了让你了解FFmpeg常用的参数混个脸熟之外，更深层次的目的是消除你的畏难情绪。

FFmpeg作为一个必备的音视频开发工具，确实参数比较多，但入门之后你就会发现，里面的参数是分模块的，非常好记也非常好用，尤其是FFmpeg公共基础参数部分，我们把这部分内容分成了公共操作参数、每个文件主要的操作参数、音频和视频操作参数四部分，每个部分的参数功能都非常明确清晰。

除此之外，学会查看各个模块参数的帮助手册，就算是掌握了“钓鱼”的方法。我希望你可以好好地利用这些方法，真正地用起来，让这些参数知识、查找方法真正成为你趁手的工具。

## **思考题**

最后，我给你留道思考题。使用FFmpeg的filter\_complex和表达式，实现这个场景：前景是一个小图（也可以是logo），背景是一个视频；logo位置与视频的进度同步，在视频下方游动，也就是视频开始的时候logo在视频的最左下角，视频结束的时候在视频的最右下角，视频播放的时候按照视频进度比例从左下角向右下角移动。

我们应该怎么去实现这个场景呢？欢迎你把自己的想法写在评论区和我交流，也欢迎你把这节课分享给需要的朋友，我们下节课再见！