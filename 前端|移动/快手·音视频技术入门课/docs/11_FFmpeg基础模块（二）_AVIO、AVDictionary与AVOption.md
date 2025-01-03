你好，我是刘歧。

[上一节课](https://time.geekbang.org/column/article/551256) 我们了解了AVFormat中的API接口的功能，从实际操作经验看，这些接口是可以满足大多数音视频的mux与demux，或者说remux场景的。但是除此之外，在日常使用API开发应用的时候，我们还会遇到需要从自己定义的内存或文件中读写数据，然后套用在AVFormat中的场景。遇到这种场景的时候我们应该怎么办呢？使用AVIO就可以做到。

## AVIO

我们先来认识一下AVIO。AVIO部分常见的接口看上去比较多，主要是为了方便读、写内容时做一些字节对齐与大小端定义的操作，了解了它内在的结构之后，你就会觉得清晰多了。下面我们来一一讲解一下。

当你想知道一个URL字符串是什么协议的时候，通过 **avio\_find\_protocol\_name接口** 就能得到协议的名称，例如http、rtmp、rtsp等。

```plain
const char *avio_find_protocol_name(const char *url);

```

**avio\_alloc\_context接口** 主要用来申请AVIOContext句柄，并且可以在申请的时候注册read\_packet、write\_packet与seek回调，然后可以将AVIOContext句柄挂载到AVFormatContext的pb上面。挂载完成后，在操作AVFormatContext的read\_packet、write\_packet、seek的时候，会调用这里注册过的回调接口，注册的时候如果把回调接口设置成NULL（空），就会使用AVIOContext子模块默认的流程。这里申请的AVIOContext可以通过 **avio\_context\_free** 来释放。

```plain
AVIOContext *avio_alloc_context(
                  unsigned char *buffer,
                  int buffer_size,
                  int write_flag,
                  void *opaque,
                  int (*read_packet)(void *opaque, uint8_t *buf, int buf_size),
                  int (*write_packet)(void *opaque, uint8_t *buf, int buf_size),
                  int64_t (*seek)(void *opaque, int64_t offset, int whence));

void avio_context_free(AVIOContext **s);

```

下面这一系列的读写接口，从名字就可以看出来，其中w是写，r是读，l或者le代表小端方式读写，b或者be代表大端读写，8代表8位，16代表16位，24、32、64分别代表24位、32位和64位。至于是大端读写还是小端读写，你可以根据实际的参考标准的要求进行操作。然后是字符串操作，这个部分也可以区分大小端的读写。

```plain
void avio_w8(AVIOContext *s, int b);
void avio_write(AVIOContext *s, const unsigned char *buf, int size);
void avio_wl64(AVIOContext *s, uint64_t val);
void avio_wb64(AVIOContext *s, uint64_t val);
void avio_wl32(AVIOContext *s, unsigned int val);
void avio_wb32(AVIOContext *s, unsigned int val);
void avio_wl24(AVIOContext *s, unsigned int val);
void avio_wb24(AVIOContext *s, unsigned int val);
void avio_wl16(AVIOContext *s, unsigned int val);
void avio_wb16(AVIOContext *s, unsigned int val);
int avio_put_str(AVIOContext *s, const char *str);
int avio_put_str16le(AVIOContext *s, const char *str);
int avio_put_str16be(AVIOContext *s, const char *str);

int avio_read(AVIOContext *s, unsigned char *buf, int size);
int avio_read_partial(AVIOContext *s, unsigned char *buf, int size);
int          avio_r8  (AVIOContext *s);
unsigned int avio_rl16(AVIOContext *s);
unsigned int avio_rl24(AVIOContext *s);
unsigned int avio_rl32(AVIOContext *s);
uint64_t     avio_rl64(AVIOContext *s);
unsigned int avio_rb16(AVIOContext *s);
unsigned int avio_rb24(AVIOContext *s);
unsigned int avio_rb32(AVIOContext *s);
uint64_t     avio_rb64(AVIOContext *s);
int avio_get_str(AVIOContext *pb, int maxlen, char *buf, int buflen);
int avio_get_str16le(AVIOContext *pb, int maxlen, char *buf, int buflen);
int avio_get_str16be(AVIOContext *pb, int maxlen, char *buf, int buflen);

```

当解析部分封装格式的时候，有一些字段暂时不用或者不需要解析，就可以使用 **avio\_skip、avio\_seek** 来跳过对应的字节，或者通过avio\_seek定位到想去的字节处，如果想要知道文件读写之后当前的文件位置，可以通过 **avio\_tell** 来获得。

```plain
int64_t avio_seek(AVIOContext *s, int64_t offset, int whence);
int64_t avio_skip(AVIOContext *s, int64_t offset);
static av_always_inline int64_t avio_tell(AVIOContext *s)

```

AVIOContext句柄文件当前已经写入的内容的大小，可以通过 **avio\_size** 来获得。

```plain
int64_t avio_size(AVIOContext *s);

```

通过 **avio\_feof** 可以判断当前位置是否是AVIOContext的EOF（文件末尾）。

```plain
int avio_feof(AVIOContext *s);

```

如果在操作AVIOContext写内容的时候内存不断增长，可以尝试用 **avio\_flush** 把内容刷到目标文件中去。

```plain
void avio_flush(AVIOContext *s);

```

当写入文件需要先临时放在内存中，最后按照自己的计划将内容刷到文件中的话，可以考虑使用 **avio\_open\_dyn\_buf、avio\_get\_dyn\_buf、avio\_close\_dyn\_buf** 来操作。

```plain
int avio_open_dyn_buf(AVIOContext **s);
int avio_get_dyn_buf(AVIOContext *s, uint8_t **pbuffer);
int avio_close_dyn_buf(AVIOContext *s, uint8_t **pbuffer);

```

比如操作HLS直播流的时候，考虑到fragment mp4文件的特殊性，我希望先把文件内容写入到内存中，确保写入的数据拿到音视频包完整的流信息数据，然后生成HLS列表时能够写入准确的流信息内容，我会调用avio\_open\_dyn\_buf、avio\_get\_dyn\_buf、avio\_close\_dyn\_buf来解决问题。

再比如生成fragment mp4的HLS时，需要有一个fragment mp4的init头内容，这个init头部内容，通常可以用avio\_open\_dyn\_buf、avio\_get\_dyn\_buf、avio\_close\_dyn\_buf来做临时缓存，并且定时刷新到init头中。

**avio\_close与avio\_closep** 几乎相同，用来释放申请的资源，但是在avio\_closep里会调用avio\_close，并清空AVIOContext句柄内容，然后置空。这样可以确保AVIOContext的操作安全，不会出现use-after-free的问题，所以有时候用avio\_closep会更安全一些。

```plain
int avio_close(AVIOContext *s);
int avio_closep(AVIOContext **s);

```

**avio\_open和avio\_open2** 都是用来打开FFmpeg的输入输出文件的，它们之间的差别是avio\_open2可以注册一个AVIOInterruptCB的callback做超时中断处理，而且可以在open的时候设置AVDictionary来操作AVIO目标对象的options。

```plain
int avio_open(AVIOContext **s, const char *url, int flags);
int avio_open2(AVIOContext **s, const char *url, int flags, const AVIOInterruptCB *int_cb, AVDictionary **options);

```

![图片](https://static001.geekbang.org/resource/image/77/47/773dc943233541714b0113c114118147.png?wh=1920x2084)

学完AVIO部分接口的用途和操作方式，就补齐了封装格式操作API方面的拼图。这是我们成为FFmpeg API用户的第一步。但你不要因此觉得成为API用户就可以不用FFmpeg的命令行了。

其实无论是FFmpeg的命令行还是各种API接口，都可以为我们所用，它们之间并不是割裂的。FFmpeg提供的命令行支持很多参数，这些参数不单单是提供给命令行用户的，API用户也可以使用。那具体API用户应该怎么去使用这些参数呢？

我们可以通过AVDictionary或者AVOption来设置参数，这两个API系列主要用来设置操作目标的format、codec、protocol的参数，最终达到与命令行使用参数一样的效果。因为AVDictionary和AVOption都是基础操作接口，之后我们学习的操作接口都会涉及参数设置，所以今天我们也详细地了解一下opt和dict的操作方法。

## AVDictionary 与 AVOption

在使用 FFmpeg 命令行做封装、解封装、编解码、网络传输的时候，都会用到一些参数，比如我们录制MP4的时候，希望在录制完成之后把moov移动到文件头部，就需要添加一个参数‐movflags faststart。那么在使用FFmpeg的SDK时，就需要使用dict或opt的操作方式，来将参数传给 FFmpeg内部MP4的muxer模块。

同样是把moov移动到文件头部，使用dict和使用opt有什么区别呢？下面我用两个例子来说明这个问题。

1. 通过opt操作设置参数

```plain
AVFormatContext *oc;
avformat_alloc_output_context2(&oc, NULL, NULL, "out.mp4");
av_opt_set(oc‐>priv_data, "movflags", "faststart", 0); /* 直接设置容器对象的参数 */
avformat_write_header(oc, NULL);
av_interleaved_write_frame(oc, pkt);
av_write_trailer(oc);

```

2. 通过dict操作设置参数。

```plain
AVFormatContext *oc;
AVDictionary *opt = NULL; /* 先定义一个AVDictionary变量 */
avformat_alloc_output_context2(&oc, NULL, NULL, "out.mp4");
av_dict_set(&opt, "movflags", "faststart", 0); /* 将参数设置到AVDictionary变量中 */
avformat_write_header(oc, &opt); /* 打开文件时传AVDictionary参数 */
av_dict_free(&opt); /* 使用完AVDictionary参数后立即释放以防止内存泄露 */
av_interleaved_write_frame(oc, pkt);
av_write_trailer(oc);

```

这两种操作方式都可以将moov容器移动到MP4文件的头部，我们从操作的代码中看到， av\_opt\_set可以直接设置对应对象的参数，这样使用的话能够直接让设置的参数生效。而 av\_dict\_set可以把参数设置到AVDictionary变量中，放到AVDictionary里之后，可以复用到多个对象里，但是设置起来会稍微麻烦一些。二者各有优势，你可以通过个人的使用习惯而定。

除了av\_opt\_set与av\_dict\_set之外，opt与dict还有很多的操作接口可以使用，我们可以通过列表来了解一下。

1. opt接口列表

```plain
av_opt_set_int 只接受整数
av_opt_set_double 只接受浮点数
av_opt_set_q 只接受分子与分母，例如{1, 25}这样
av_opt_set_bin 只接受二进制数据
av_opt_set_image_size 只接受图像宽与高，例如1920，1080这样
av_opt_set_video_rate 只接受分子与分母，例如{1, 25}这样
av_opt_set_pixel_fmt 只接受枚举类型，例如AV_PIX_FMT_YUV420P
av_opt_set_sample_fmt 只接受采样数据格式枚举类型，例如AV_SAMPLE_FMT_S16
av_opt_set_channel_layout 只接受音频通道布局枚举类型，例如AV_CHANNEL_LAYOUT_5POINT0
av_opt_set_dict_val 接受AVDictionary类型，例如设置metadata时候可以使用
av_opt_set_chlayout 只接受音频通道布局枚举类型，例如AV_CHANNEL_LAYOUT_5POINT0
av_opt_set_defaults 设置对象的默认值，例如hlsenc有自己对应的操作选项的默认值，全部设置对应的默认值
av_opt_set_defaults2 设置对象的默认值，例如hlsenc有自己对应的操作选项的默认值，全部设置对应的默认值
av_opt_set_from_string 解析key=value格式的字符串并设置对应的参数与值

av_opt_next 获得opt操作的对象的下一个参数
av_opt_get_int 获得对象参数的值为整数
av_opt_get_double 获得对象参数的值为双精度浮点数
av_opt_get_q 获得对象参数为分子分母数，例如{1, 25}这样
av_opt_get_image_size 获得图像的宽和高，例如1920，1080这样
av_opt_get_video_rate 获得视频的帧率，例如{1, 25}这样
av_opt_get_pixel_fmt 获得视频的像素点格式枚举类型，例如AV_PIX_FMT_YUV420P
av_opt_get_sample_fmt 获得音频的采样格式枚举类型，例如AV_SAMPLE_FMT_S16
av_opt_get_channel_layout 获得音频的采样布局枚举类型，例如AV_CHANNEL_LAYOUT_5POINT0
av_opt_get_dict_val 获得AVDictionary类型，通常是key-value方式
av_opt_get_key_value 获得key=value类型

```

使用opt中的这些接口进行操作时，可以精确地设置到参数值的类型，直接操作对象，比如某个封装格式模块、某个编解码模块，非常方便。

2. dirt接口列表

```plain
av_dict_count 获得dict参数的数量整数
av_dict_parse_string 一次性解析多组key=value格式的字符串为dict
av_dict_free 释放因设置dict申请的内存空间
av_dict_copy 复制dict参数与值
av_dict_get_string 获得dict的参数值为字符串，用key=value格式字符串获得到value
av_dict_set_int 设置dict参数的值为整数

```

和opt相比，dict的操作接口比较少，给人感觉比较简单。但是注意，使用dict这些接口操作对象后，通常只是设置了AVDictionary，并没有真正地设置具体对象。如果想让设置的参数生效，还需要在做封装格式open或编解码器open的时候，设置AVDictionary，并且需要仔细斟酌内存使用情况，通常需要自己调用av\_dict\_free做内存释放。

在日常使用API进行开发的时候，你可以使用opt与dict相关的接口，高效地设置对应的参数。当然想要获得这项能力，还需要你勤加练习。

## 小结

![图片](https://static001.geekbang.org/resource/image/2d/77/2debcce3ce9a8360bdd31cf90a0dcd77.png?wh=1920x1348)

关于封装格式的API，除了 [上节课](https://time.geekbang.org/column/article/551256) 我们学习的AVFormat模块之外，还有AVIO，它主要应用于在内存中直接操作数据的场景中。

AVIO中包含很多常用的接口，比如用来查看协议名称的avio\_find\_protocol\_name接口、用来申请AVIOContext句柄的avio\_alloc\_context接口，还有一系列的读写接口等。AVIO操作接口和我们标准文件的操作接口基本相似，可以在申请之后与FFmpeg的AVFormatContext的pb挂载，这样方便进入FFmpeg的AVFormat操作的内部流程。

除此之外，我们也应该合理利用FFmpeg命令行支持的参数，学会使用opt与dict相关的API操作，灵活调用FFmpeg命令行支持的参数，为我们使用API开发应用提供更强大的能力。

## 思考题

最后，我们来思考一个问题，在AVFormat模块中可以看到频繁出现的一个参数AVPacket，这个AVPacket属于AVFormat还是AVCodec呢？ 欢迎你在评论区留下你的答案，也欢迎你把这节课分享给感兴趣的朋友，我们下节课再见！