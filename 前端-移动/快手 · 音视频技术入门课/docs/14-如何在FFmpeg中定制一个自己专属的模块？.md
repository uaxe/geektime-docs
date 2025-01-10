你好，我是刘歧。

通过前面13节课的学习，我们对FFmpeg整体的使用和架构已经有了一定的了解。接下来，我们一起来探索一下FFmpeg社区的“玩法”，了解一下FFmpeg常用的交流工具、反馈bug和贡献代码的渠道，以及定制专属板块的方法。这个部分，我会分成两讲给你介绍。这节课我们先来学习一下如何在FFmpeg中定制一个专属于自己的模块。定制模块的作用有很多，比如可以通过定制自己的私有格式，防止别人播放自己的视频。

在FFmpeg中添加模块，需要深入了解源代码架构。但FFmpeg源代码太多，我们需要找到一个突破口深入进去。下面，我们一步一步来解决这些问题。

首先，我们下载官方的源代码库，基于5.0分支做一个新分支kwai，作为我们源码的基础。

```plain
$ git clone git://source.ffmpeg.org/ffmpeg.git     # 下载源代码
$ cd ffmpeg                                        # 进入源代码主目录
$ git checkout remotes/origin/release/5.0          # 切换到5.0分支
Note: switching to 'remotes/origin/release/5.0'.

$ git checkout -b kwai                             # 开一个新分支，起名叫kwai
Switched to a new branch 'kwai'

```

在源代码根目录中，执行命令ls \|grep lib，可以列出相应模块的源代码目录。

```plain
$ ls | grep lib
libavcodec/
libavdevice/
libavfilter/
libavformat/
libavutil/
libpostproc/
libswresample/
libswscale/

```

然后，可以用你喜欢的编辑器，打开整个源代码目录，浏览一下源代码的目录结构，找自己熟悉的内容看，比如你平时用H.264编码用得比较多，就可以在libavcodec目录下，找到很多h264开头的文件。

如果你写一个新的编解码模块的话，最简单的方式就是先找一个类似的模块，复制一个。不过，由于FFmpeg是一个庞大的项目，历史渊源也很深，里面会有各种代码判断，如if-else之类的，来应对实际使用环境中的问题，但这会干扰你的阅读。因此，这节课我们会通过最简单的例子，把问题讲清楚。

## 编译可用版本

我们先编译一个可用的版本。因为是自己实现模块，所以这里只需要最基本的编译就可以了，不需要编译大量的第三方模块。所以下面我们只使用了最简单的./configure，没有使用任何其它参数。

```plain
./configure
make -j4

```

编译完成后，执行./ffmpeg -h，如果运行正常，说明我们编译成功了。我是在MacBook上编译的，如果没有MacBook的话，你也可以考虑使用Linux。使用下面的命令统计输出结果如下：

```plain
./ffmpeg -formats | wc -l          # 输出 388
./ffmpeg -codecs | wc -l           # 输出 500
./ffmpeg -filters | wc -l          # 输出 428
./ffmpeg -protocols | wc -l        # 输出 58
./ffmpeg -devices | wc -l          # 输出 9

```

你也可以去掉其中的\| wc -l，查看完整的输出，从这些输出的结果大概可以看出相应模块的数量（行数）。

有了这个基础环境，下面我们就可以添加自己的模块了。如果你参考我在这节课里面贴的代码，同步做实验，可以在做完示例后，再次运行上面的命令，观察前后的差异。

## 为FFmpeg添加自己的 AVFormat模块

我们之前提到过很多次，AVForamt是各种音视频文件格式（包括网络文件格式）的封装模块，要添加一个自己专属的AVForamt模块，需要先“发明”一种自己的文件格式，然后用代码实现，这里为了简洁一点儿，我们使用固定的编解码格式。

### kwai文件格式

我们把新“发明”的文件格式命名为kwai，格式定义如下：

• 支持音视频，文件固定包含一个音频轨和一个视频轨。

• 音频固定为AAC，视频固定为H264。

• 音视频交错存储。

• 音视频数据块的长度，32位无符号整数，大端序，后面跟音视频数据。

• 长度字段最高位，音频为0，视频为1。

文件头定义如下：

• 4字节文件魔数，固定为kwai。

• 4字节版号，32位无符号整数，大端序。

• 4字节采样率，32位无符号整数，大端序。

• 1字节填充字符，无任何意义，固定为0。

• 1字节音频声道数。

• 2字节视频宽度，32位整数，大端序。

• 2字节视频高度，32位整数，大端序。

• 2字节帧率分子，16位整数，大端序。

• 2字节帧率分母，16位整数，大端序。

• 26字节其它文本信息，最后一字节为0，即NULL字符，主要是为了方便字符串处理。

这样定制内容，主要是为了演示不同长度整数的处理，外加一个额外的填充字符，同时也是为了数据对齐，人眼看起来比较直观，后面我们会在文件头的16进制数据表示时感受到这种效果。

### 添加文件

首先，我们在libavformat目录下创建两个文件：kwaienc.c和kwaidec.c，其中kwaienc.c对应文件编码，enc是encoding的缩写，也叫封装/mux。kwaidec.c对应文件解码，dec是decoding缩写，也叫解封装/demux。文件的具体内容我们后面再讲。

接下来在libavformat/Makefile中增加下面这段内容。

```plain
OBJS-$(CONFIG_kwai_DEMUXER)              += kwaidec.o
OBJS-$(CONFIG_kwai_MUXER)                += kwaienc.o

```

在libavformat/allformats.c中增加下面这段内容。

```plain
extern const AVOutputFormat ff_kwai_muxer;
extern const AVInputFormat  ff_kwai_demuxer;

```

执行命令./configure --list-muxers和./configure --list-demuxers可以列出所有的格式，如果能从输出结果中找到kwai，就说明添加成功了。

```plain
./configure --list-muxers
./configure --list-demuxers

```

然后重新执行configure。

```plain
./configure --enable-muxer=kwai --enable-demuxer=kwai

```

到这里，我们的源文件和编译环境都准备好了。接下来，我们添加文件的封装格式。

### 添加文件封装格式

文件封装（就是AVOutputFormat）是一个输出格式，它的输入端也是一个AVFormat（也就是AVInputFormat）。下面，我们先注册我们的kwai封装文件格式，内容在kwaienc.c中。一般来说，分为这几步：

1. 定义文件格式结构体
2. 准备参数
3. 定义一个类
4. 向FFmpeg注册文件格式
5. 实现回调函数

下面我们逐步讲解一下。

#### 定义文件格式结构体

我们先来定义一个结构体，用来描述和存储文件的各种参数。其中，这个结构体的第一个成员必须是一个AVClass类型的指针，不需要特别处理，FFmpeg内部会用到。其它参数，你可以参考代码内的注释。

```plain
typedef struct kwaiMuxContext {
    AVClass *class;         // AVClass指针
    uint32_t magic;         // 文件魔数，用于标志文件的类型，很多文件类型如PNG和MP3都这么做
    uint32_t version;       // 版本号，目前固定为1
    uint32_t sample_rate;   // 音频采样率，常用的AAC格式采样率为44100
    uint8_t channels;       // 声道数，一般为1或2
    uint32_t width;         // 视频宽度
    uint32_t height;        // 视频高度
    AVRational fps;         // 帧率，这里用分数表示
    char *info;             // 文件的其它描述信息，字符串
} kwaiMuxContext;

```

#### 准备参数

准备一个AVOption结构体数组，用来存放kwai文件格式的相关参数。比如，我们下面定义了一个字符串格式的info参数和一个整数格式的version参数，最后用了一个空（NULL）结构体元素结尾。这两个参数都可以在命令行上使用，后面我们会看到具体的用法。

FFmpeg会自动为这些参数申请存储空间。从下面的代码里我们可以看到，这些参数其实指向了我们上面定义的结构体，当在命令行上指定参数的时候，会修改相应的结构体指针。

```plain
static const AVOption options[] = {
    { "info", "kwai info", offsetof(kwaiMuxContext, info), AV_OPT_TYPE_STRING,
        {.str = NULL}, INT_MIN, INT_MAX, AV_OPT_FLAG_ENCODING_PARAM, "kwaiflags" },
    { "version", "kwai version", offsetof(kwaiMuxContext, version), AV_OPT_TYPE_INT,
        {.i64 = 1}, 0, 9, AV_OPT_FLAG_ENCODING_PARAM, "kwaiflags" },
    { NULL },
};

```

#### 定义一个类

定义一个AVClass结构体，指定kwai文件格式的名称，关联上面定义的参数等。

```plain
static const AVClass kwai_muxer_class = {
    .class_name = "kwai muxer",
    .item_name  = av_default_item_name,
    .option     = options,
    .version    = LIBAVUTIL_VERSION_INT,
};

```

#### 向FFmpeg注册文件格式

有了上述内容，我们就可以向FFmpeg注册我们的kwai文件格式了。其中ff\_kwai\_muxer这个名字对应我们上面在allformats.c文件中添加的名字，这样FFmpeg在编译器中就可以找到我们定义的文件格式了。

```plain
const AVOutputFormat ff_kwai_muxer = {
    .name              = "kwai",                 // 格式名称
    .long_name         = NULL_IF_CONFIG_SMALL("kwai / kwai"), // 长名称
    .extensions        = "kwai",                 // 文件扩展名
    .priv_data_size    = sizeof(kwaiMuxContext), // 私有数据内存大小
    .audio_codec       = AV_CODEC_ID_AAC,        // 音频编码
    .video_codec       = AV_CODEC_ID_H264,       // 视频编码
    .init              = kwai_init,              // 初始化回调函数
    .write_header      = kwai_write_header,      // 写文件头回调
    .write_packet      = kwai_write_packet,      // 写文件内容回调
    .write_trailer     = kwai_write_trailer,     // 写文件尾回调
    .deinit            = kwai_free,              // 写文件结束后，释放内存回调
    .flags             = 0,                      // 其它标志（略）
    .priv_class        = &kwai_muxer_class,      // 私有的文件结构体，指向我们上一步定义的内容
};

```

#### 实现回调函数

![图片](https://static001.geekbang.org/resource/image/8f/14/8f3a58623d5dbb8a819912c5ab667e14.png?wh=1920x529)

一切准备就绪，下面就是实现具体的回调函数了。

1. 初始化函数

初始化函数在最初打开文件时调用，这个函数的输入参数是一个AVFormatContext结构体指针，由FFmpeg在打开文件时传入。这个结构体指针包含了文件的类型、流的数量（nb\_streams）和各种参数。根据这些参数，我们就可以完成kwai封装器的初始化工作了。

```plain
static int kwai_init(AVFormatContext *s)
{
    AVStream *st; // 音视频流，每一个stream代表一种类型，如音频流，视频流等
    kwaiMuxContext *kwai = s->priv_data; // 指向私有的结构体，已初始化为默认值
    printf("init nb_streams: %d\n", s->nb_streams);
    if (s->nb_streams < 2) { // 音视频流数量，我们只接受一个音频流和一个视频流的输入
        return AVERROR_INVALIDDATA; // 简单出错处理
    }
    st = find_stream(s, AVMEDIA_TYPE_AUDIO); // 查找音频流，该函数后面解释
    if (!st) return AVERROR_INVALIDDATA;     // 简单出错处理，如果找不到音频流则返回错误
    kwai->sample_rate = st->codecpar->sample_rate; // 记住输入音频流的采样率
    kwai->channels = st->codecpar->channels;       // 记住声道数
    st = find_stream(s, AVMEDIA_TYPE_VIDEO); // 查找视频流
    if (!st) return AVERROR_INVALIDDATA;     // 简单出错处理
    kwai->width = st->codecpar->width;       // 记住视频宽度
    kwai->height = st->codecpar->height;     // 记住视频高度
    // kwai->fps = st->codecpar->fps;
    kwai->fps = (AVRational){15, 1};         // 记住帧率
    return 0;                                // 初始化正常返回0
}

```

在上面的代码中，我们用到了一个find\_stream函数，它可以从kwai格式的输入参数中查找音视频流。

```plain
static AVStream *find_stream(AVFormatContext *s, enum AVMediaType type)
{
    int i = 0;
    for (i = 0; i < s->nb_streams; i++) { // 遍历所有输入流
        AVStream *stream = s->streams[i];
        if (stream->codecpar->codec_type == type) { // 找到第一个对应的类型（音频或视频），即返回对应的流
            return stream;
        }
    }
    return NULL;
}

```

2. 写文件头

初始化完成后，下一步就是写文件头，其实写文件头函数也是一个回调函数，都是由FFmpeg的核心逻辑回调的，所以我们只需要照着输入输出格式定义好头文件就可以了。

```plain
static int kwai_write_header(AVFormatContext *s)
{
    kwaiMuxContext *kwai = s->priv_data;        // 获取我们的私有结构体
    kwai->magic = MKTAG('K', 'W', 'A', 'I');    // 初始化魔数
    // avio_wb32(s->pb, kwai->magic);
    avio_write(s->pb, (uint8_t *)&kwai->magic, 4); // 将该魔数写入文件，此时文件有4字节，内容为kwai
    avio_wb32(s->pb, kwai->version);            // 以大端序写入版本号，占4字节
    avio_wb32(s->pb, kwai->sample_rate);        // 以大端序写入采样率
    avio_w8(s->pb, 0);                          // 写入一个字节占位符，无任何意义
    avio_w8(s->pb, kwai->channels);             // 写入一个字节声道数
    avio_wb16(s->pb, kwai->width);              // 写入宽度，2字节
    avio_wb16(s->pb, kwai->height);             // 写入高度，2字节
    avio_wb16(s->pb, kwai->fps.num);            // 写入帧率分子部分，2字节
    avio_wb16(s->pb, kwai->fps.den);            // 字入帧率分母部分，2字节
    char info[26] = {0};
    if (kwai->info) {                           // 如果命令行上有info参数，则将其内容读到临时内在
        strncpy(info, kwai->info, sizeof(info) - 1);
    }
    avio_write(s->pb, info, sizeof(info));       // 写入info字符串内容
    return 0;
}

```

在上述代码中，info字符串占26个字节（包含结尾的NULL字符），这主要是为了使文件头部分正好是48个字节，对人眼比较友好。

3. 写音视频数据

如果初始化和写文件头正常，FFmpeg就开始写音视频数据了。其中，输入参数除了AVFormatContext结构体指针外，还有一个AVPacket结构体指针，里面存放了具体要求的音视频数据。音视频会交错存储，首先写入当前数据的时间戳（64位的pts值），然后是以32位无符号整数表示的长度（其中视频的长度最高位置1），接着写入实际的音视频数据。

```plain
static int kwai_write_packet(AVFormatContext *s, AVPacket *pkt)
{
    // kwaiMuxContext *mov = s->priv_data;
    if (!pkt) {
        return 1;
    }
 uint32_t size = pkt->size;               // 获取数据大小

    AVStream *st = s->streams[pkt->stream_index];  // 通过stream_index可以找到对应的流，是音频还是视频

    if (st->codecpar->codec_type == AVMEDIA_TYPE_AUDIO) {
        printf("Audio: %04d pts: %lld\n", size, pkt->pts); // 打印音频字节数和pts
    } else if (st->codecpar->codec_type == AVMEDIA_TYPE_VIDEO) {
        printf("Video: %04d pts: %lld\n", size, pkt->pts); // 打印视频字节数和pts
        size |= (1 << 31); // 如果是视频，将长度的最高位置1
    } else {
        return 0; // ignore any other types
    }

    avio_wb64(s->pb, pkt->pts);              // 写入8字节pts，大端序
    avio_wb32(s->pb, size);                  // 写入4字节视频长度，大端序
    avio_write(s->pb, pkt->data, pkt->size); // 写入实际的音视频数据

    return 0;
}

```

4. 文件结束处理

文件结束时，调用write\_trailer回调写尾部数据，并调用deinit回调释放相应的内存。这里我们的封装器实现得比较简单，所以简单放两个空函数即可。

```plain
static int kwai_write_trailer(AVFormatContext *s)
{
    return 0;
}

static void kwai_free(AVFormatContext *s)
{
}

```

到这里，我们的文件格式封装器就做好了。

5. 编译运行

最后，直接执行make就可以编译了。不过，这时候由于我们没有实现解封装器，会提示ff\_kwai\_demuxer不存在。为了能“骗过”编译器，我们可以先在kwaidec.c里定义一下，临时代码如下所示：

```plain
#include "avformat.h"
const AVInputFormat  ff_kwai_demuxer;

```

编译通过后，我们就可以使用熟悉的命令行来生成一个kwai类型的文件了。先找一个标准的MP4文件（如input.mp4）作为输入，命令行如下：

```plain
./ffmpeg -i input.mp4 -bsf:v h264_mp4toannexb -info 'a simple test' out.kwai

```

在上述命令中，我们使用了h264\_mp4toannexb这个filter，它的主要作用是将MP4中的H264视频容器数据封装转换为传统的使用startcode分割的annexb比特流格式。因为大多数解码器只支持这种格式。此外，我们还使用-info参数增加了一些文本信息，输出文件名为out.kwai。

现在，地球上还没有任何一个播放器能播放我们生成的文件。下面，我们先来分析一下文件格式是否符合我们的预期。Windows平台可以使用一些16进制编辑器打开文件查看，Linux或macOS可以使用xxd命令来查看（这个命令一般会随vim编辑器一起安装）。具体命令如下：

```plain
$ xxd out.kwai | head -n 4

```

注：head -n 4表示只查看输出的前4行。

输出结果是下面这段内容。

```plain
00000000: 6b77 6169 0000 0001 0000 ac44 0002 0280  kwai.......D....
00000010: 01e0 000f 0001 6120 7369 6d70 6c65 2074  ......a simple t
00000020: 6573 7400 0000 0000 0000 0000 0000 0000  est.............
00000030: 0000 0000 0000 0000 0000 0017 de02 004c  ...............L

```

其中，输出结果在横向上分为三部分，左侧是文件字节偏移量，以16进制表示；中间是实际的数据，每行有16个字节，两个16进制数字表示一个字节（取值范围为00~ff），两个字节为一组（即一个字）；最后是文件内容可读的形式，如果是可读的字符，就会显示出来，否则以“.”表示。

对照着我们前面对kwai类型文件的定义以及代码实现，可以看到，上面的输出是符合预期的。从第一行看，最开始4个字节6b77 6169，对应的ASCII码是kwai，这是我们规定的文件头，也就是魔数。接下来4个字节0000 0001是版本号（此处为1）；后面4个字节0000 ac44换成10进制是44100，即采样率；再后面一个字节的00是占位符，没有任何作用；占位符后的一个字节02表示声道数；两个字节0280表示视频宽度，转换成10进制是640。

第二行，前两个字节01e0是视频高度，即480；后面是帧率：000f和0001，即15/1。接下来就是我们命令行上用-info参数设置的字符串，此处是“a simple test”；后面全部以0填充，直到第三行行尾。我们精心设计了48个字节的文件头，就是为了让它在输出时正好占满3行。

从第四行开始，前8个字节的0是时间戳，它是一个64位整数，此处时间戳是从0开始的。接下来0000 0017表示后面音视频的长度，因为这个数的最高位是0（二进制最高位也是0），所以它后面应该是音频数据，占23（0x17换成10进制是23）个字节。往后跳过23个字节就应该是下一组数据了，以此类推。

你可以在前面的命令行上加上-version 2，并修改相应的info看一下有什么变化，完整的命令行参考如下：

```plain
./ffmpeg -i input.mp4 -bsf:v h264_mp4toannexb -info 'another simple test' -version 2 out.kwai

```

## 小结

这节课我们在FFmpeg中添加了一个自己专属的封装模块，如果你想只有你的播放器能够播放你自己的私有化音视频数据的话，这种操作是比较常见的。其实操作比较简单，主要是添加AVOutputFormat、AVIntputFormat、AVCodec这样的结构体，给结构体填充自己指定的内容即可。学习完这节课以后，你可以自己分析FFmpeg的各模块代码，跟着我的操作步骤添加一个自己的专属模块。

## 思考题

这节课我们学习的是添加一个muxer，那么你能否为muxer添加一个demuxer呢？ 欢迎你在评论区留言和我讨论，也欢迎你把这节课分享给需要的朋友，我们下节课再见！