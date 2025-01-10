你好，我是刘歧。

前面两节课我们学习了AVFormat、AVIO、dict和opt操作接口，做容器格式封装与解封装问题不大，但是如果要涉及音视频的编解码的话，就需要用到AVCodec部分的接口了。

AVCodec是存储编解码器信息的结构体，当我们使用编解码器的时候会用到AVCodec，而FFmpeg除了AVCodec结构体之外，还有一个AVCodecContext，是FFmpeg内部流程中处理编解码时，用来记录和存储上下文的结构体。关于AVCodecContext这个结构体的参数，如果你学习 [第7节课FFmpeg常用参数](https://time.geekbang.org/column/article/548420) 的时候，仔细阅读过帮助信息的话，那AVCodecContext这个结构体对你来说应该很好理解。

## AVCodec 接口

在使用FFmpeg的编解码器之前，首先需要找到编解码器。

```plain
const AVCodec *avcodec_find_decoder(enum AVCodecID id);
const AVCodec *avcodec_find_decoder_by_name(const char *name);
const AVCodec *avcodec_find_encoder(enum AVCodecID id);
const AVCodec *avcodec_find_encoder_by_name(const char *name);

```

如代码所示，找到编码器和解码器有两种方式，一种是通过AVCodecID来查找，一种是通过字符串来查找，字符串就是编码器或解码器的名称，例如libx264。

这里需要注意的是，如果编码器和解码器的find接口使用得没有问题，用avcodec\_find\_decoder查找编码器的话，在这里可能能找到AVCodec，但是在后续用来做编码的时候会报错。

通常我们也可以在做编码操作之前，调用接口av\_codec\_is\_encoder来确认当前拿到的AVCodec是不是编码器，或者通过av\_codec\_is\_decoder来确认是不是解码器。

找到AVCodec之后，最好不要直接使用，推荐的做法是与FFmpeg内部流程中的AVCodecContext建立关联。

```plain
AVCodecContext *avcodec_alloc_context3(const AVCodec *codec);
void avcodec_free_context(AVCodecContext **avctx);

```

从示例代码中可以看到，AVCodec与AVCodecContext可以通过avcodec\_alloc\_context3接口来申请并建立关联，因为涉及内存申请操作，所以用完之后需要使用avcodec\_free\_context释放资源。

申请完AVCodecContext上下文之后，接下来可以打开编码器或者解码器了。

```plain
int avcodec_open2(AVCodecContext *avctx, const AVCodec *codec, AVDictionary **options);

```

你应该已经发现了，这个avcodec\_open2有三个参数，第一个是AVCodecContext，它是处理编解码时，用来记录和存储上下文的结构体，第三个参数是AVDictionary，这个参数用来设置AVCodec编码器或者解码器内部的参数，可以使用ffmpeg -h encoder=libx264查看libx264的内部可设置的参数，AVDictionary和AVOption的设置方式，我们在上一节课已经讲过了，这里就不过多介绍了。

好了，我们该说道说道这第二个参数了，前面我们不是已经在avcodec\_alloc\_context3将AVCodec与AVCodecContext建立过关联了吗，这里怎么还需要传递一个AVCodec呢？你想得没错，这里可以不传递了，设置为NULL就可以了。如果想要关闭编码器，推荐你使用avcodec\_free\_context来做一次释放，这样比较干净，因为avcodec\_free\_context里面已经有avcodec\_close操作了。

### 编码和解码的操作接口

好了，说完编解码的前置操作，接下来进入正题，我们看一看编码和解码的操作接口。

```plain
int avcodec_send_packet(AVCodecContext *avctx, const AVPacket *avpkt);
int avcodec_receive_frame(AVCodecContext *avctx, AVFrame *frame);
int avcodec_send_frame(AVCodecContext *avctx, const AVFrame *frame);
int avcodec_receive_packet(AVCodecContext *avctx, AVPacket *avpkt);

```

这是两组接口，avcodec\_send\_packet与avcodec\_receive\_frame是用来做解码的组合，avcodec\_send\_frame与avcodec\_receive\_packet是用来做编码的组合。

大多数场景下，可以调用一次avcodec\_send\_packet，将AVPacket送到解码器里，然后avcodec\_receive\_frame读取一次AVFrame，但是稳妥起见，avcodec\_receive\_frame有时候会返回EAGAIN，所以我们还需要确认读全了AVframe，再做avcodec\_receive\_frame操作。

FFmpeg旧版本其实是用avcodec\_decode\_video2和avcodec\_decode\_audio4来做的音视频的解码，从2016年04月21日开始，FFmpeg新增了avcodec\_send\_packet和avcodec\_receive\_frame这样的组合解码与组合编码接口，主要是为了解决一个AVPacket中包含多个视频帧或者音频包的情况。

如果解码结束，给avcodec\_send\_packet写一个NULL的AVPacket包就可以了。编码的话，给avcodec\_send\_frame设置AVFrame为NULL就表示编码结束了。

## 关键参数AVPacket

在AVFormat和AVCodec之间有一个关键的参数，就是我们这几节课频繁见到的AVPacket。AVPacket的内容构建也有一系列的接口需要我们了解，构造AVPacket内容的时候用这些接口会非常方便，下面我来介绍一下。

如果你想使用AVPacket的话，可以通过av\_packet\_alloc来申请一个AVPacket。

```plain
AVPacket *av_packet_alloc(void);

```

但这次申请的只是一个AVPacket的内存空间，里面的buf和data的内存空间不会被申请。如果想要申请buf和data的空间的话，可以考虑在av\_packet\_alloc之后使用av\_new\_packet来解决。

```plain
int av_new_packet(AVPacket *pkt, int size)

```

当使用av\_new\_packet申请带buf和data的AVPacket的时候，需要给av\_new\_packet传递一个要申请的buf空间大小的值。

通过av\_packet\_alloc申请的AVPacket需要用av\_packet\_free来释放申请的内存空间。当然，av\_new\_packet申请的buf在av\_packet\_free里也会一并释放。

这个时候你可能会有个疑问。诶？不对啊，我如果按照AVIOContext的操作方式，自己从内存中读到一段数据，想挂到AVPacket做解码，这个时候如果用av\_new\_packet申请内存是不是不太对？你想的是对的，这个时候可以不用av\_new\_packet来申请buf或者data的内存空间，但是前面av\_packet\_alloc还是需要的，只是这里的buf或者data如果想要指向第三方data内存区域的话，最好还是使用av\_packet\_from\_data。

```plain
int av_packet_from_data(AVPacket *pkt, uint8_t *data, int size);

```

为什么推荐使用av\_packet\_from\_data做data挂载，而不是直接把AVPacket的data、buf指到我们自己读到的data内存空间呢？

其实主要是因为你在使用FFmpeg的API，所以最好还是用FFmpeg提供的接口走FFmpeg自己内部的流程。并不是说不能自己手动处理，而是为了避免很多不必要的问题不这样做，比如你把data指向你自己申请的内存空间，那么很有可能会缺少data指向buf，然后那个buf是有PADDING空间预留的。

```plain
    pkt->buf = av_buffer_create(data, size + AV_INPUT_BUFFER_PADDING_SIZE,
                                av_buffer_default_free, NULL, 0);

```

这个AV\_INPUT\_BUFFER\_PADDING\_SIZE能解决很重要的问题，尤其是在后续做packet里面的data分析的时候，可能会出现crash。因为FFmpeg内部的parser在解析data的时候做了一些优化，但是会有一些额外的开销，FFmpeg的codec模块会预读一段数据，这个时候可能会因为内存越界出现crash错误。

```plain
/**
 * @ingroup lavc_decoding
 * Required number of additionally allocated bytes at the end of the input bitstream for decoding.
 * This is mainly needed because some optimized bitstream readers read
 * 32 or 64 bit at once and could read over the end.<br>
 * Note: If the first 23 bits of the additional bytes are not 0, then damaged
 * MPEG bitstreams could cause overread and segfault.
 */
#define AV_INPUT_BUFFER_PADDING_SIZE 64

```

说到对音视频流做parser，我们可以大概了解一下。

```plain
AVCodecParserContext *av_parser_init(int codec_id);
int av_parser_parse2(AVCodecParserContext *s,
                     AVCodecContext *avctx,
                     uint8_t **poutbuf, int *poutbuf_size,
                     const uint8_t *buf, int buf_size,
                     int64_t pts, int64_t dts,
                     int64_t pos);

void av_parser_close(AVCodecParserContext *s);

```

有些音视频的编码数据，是会把一部分数据相关的头信息存储在AVPacket的data中的，这个时候可以使用parser来做解析，获得相关的codec信息。如果你想要知道哪些codec有parser的话，可以在编译FFmpeg代码那一步就通过./configure --list-parsers来查看。

比如说H.264的数据，可以通过parser来得到编码数据的NALUnit信息，我们在 [第6节课](https://time.geekbang.org/column/article/547562) 的时候讲过ffprobe -show\_frames可以看到音视频流的frames信息，parser解析出来有一些信息是在这个frames里面展示出来的。这些信息也主要用来传给解码器作为解码处理的一个参考。

## 小结

我们来回顾一下这节课我们都学到了哪些内容。

- AVCodec中编解码相关的API接口：avcodec\_send\_packet与avcodec\_receive\_frame、avcodec\_send\_frame与avcodec\_receive\_packet，两组用来做编解码的组合接口。
- 关键参数AVPacket，贯穿Codec与Format模块的始终，无论是处理已有的内存数据，还是按照FFmpeg内部框架流程建立的数据，都可以应对自如。

Codec和Format之间还有更多的可操作系统的方法，你可以参考FFmpeg提供的例子加深理解。还记得 [第10节课](https://time.geekbang.org/column/article/551256) 我推荐你下载FFmpeg的源代码吗？下载源代码以后，你可以在源代码目录的doc/examples目录下看到更全面的FFmpeg的API用例。

## 思考题

如果解码以后我想给视频添加一些特效，在AVCodec操作以后应该使用哪个结构体里面的内容呢？欢迎你在评论区分享你的想法，也欢迎你把这节课分享给对音视频感兴趣的朋友，我们下节课再见！