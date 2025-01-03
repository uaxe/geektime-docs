你好，我是展晓凯。今天我们来一起学习移动平台的音频编码。

上节课，我们提到过CD音质的数据每分钟需要的存储空间约为10.1MB，如果仅仅是要放在存储设备（光盘、硬盘）中，可能是可以接受的，但是一旦在线传输的话，这个数据量就太大了，所以我们必须对其进行压缩编码。

压缩编码的基本指标之一就是压缩比，压缩比通常小于1。压缩算法分为有损压缩和无损压缩。无损压缩就是解压后数据可以完全复原，比如我们常见的Zip压缩；在音视频领域我们用得比较多的是有损压缩，有损压缩指解压后的数据不能完全复原，会丢失一部分信息。压缩比越小，丢掉的信息越多，信号还原后失真越大。

根据不同的应用场景（从存储设备、传输网络环境、播放设备等角度综合考虑），我们可以选用不同的压缩编码算法，如WAV、MP3、AAC、OPUS等。压缩编码的原理实际上是压缩掉冗余信号。在音频中冗余信号指的是不容易被人耳感知到的信号，包含人耳听觉范围外的音频信号以及被掩蔽掉的音频信号等。

人耳听觉范围是20～20kHz，被掩蔽掉的音频信号指的是由于人耳的掩蔽效应不被察觉的信号，主要表现为频域掩蔽效应与时域掩蔽效应，无论在时域还是频域上，被掩蔽掉的声音信号都被认为是冗余信息，也不进行编码处理。

## 常见的音频编码格式

了解了音频编码的原理，下面我们来详细看一下几种常用的压缩编码格式。

- WAV编码

PCM 脉冲编码调制是Pulse Code Modulation的缩写。前面我们提到了PCM大致的工作流程，而WAV编码的一种实现（有多种实现，但是都不会进行压缩操作）就是在PCM数据格式的前面加上44个字节，分别用来描述PCM的采样率、声道数、数据格式等信息。

WAV编码的特点是音质非常好，几乎可以被所有软件播放，适用于多媒体开发的中间文件、保存音乐和音效素材。

- MP3编码

MP3具有不错的压缩比，使用LAME编码（最常使用的一种MP3编码器）的中高码率（320Kbps左右）的MP3，听感上非常接近WAV源文件，当然在不同的应用场景下，我们自己应该调整合适的参数来达到最好的效果。

MP3编码的特点是音质在128Kbps以上表现还不错，压缩比比较高，大量软件和硬件都支持，兼容性最好，适用于高比特率下对兼容性有要求的音乐欣赏。

- AAC编码

AAC是新一代的音频有损压缩技术，它通过一些附加的编码技术，如SBR、PS等，衍生出了LC-AAC、HE-AAC、HE-AACv2三种主要的编码规格（Profile）。LC-AAC就是比较传统的AAC，主要用在中高码率的场景编码（$\\geq80Kbps$）；HE-AAC，相当于AAC+SBR，主要用在中低码率场景编码（$\\leq80Kbps$）；而HE-AACv2，相当于AAC+SBR+PS，主要用于双声道、低码率场景下的编码（$\\leq48Kbps$）。

事实上，大部分AAC编码器的实现中，将码率设成小于等于48Kbps会自动启用PS技术，而大于48Kbps就不加PS，就相当于普通的HE-AAC。

AAC编码的特点是在小于128Kbps的码率下，表现优异，当下应用广泛，多用于 128Kbps以下的音频编码、视频中音频轨的编码以及音乐场景下的编码。

- Opus编码

Opus集成了以语音编码为导向的SILK和低延迟编码为导向的CELT，所以它同时具有这两者的优点，可以无缝调节高低码率。在较低码率时，使用线性预测编码，在高码率时使用变换编码。

Opus具有非常低的算法延迟，最低可以做到5ms的延迟，默认为22.5 ms，非常适合用在低延迟语音通话场景。与MP3、AAC等常见格式相比，在低码率（64Kbps及以下）场景下，Opus具有更好的音质表现，同时也有更低的延迟表现。WebRTC中采用的音频默认编码就是Opus编码，并且在Opus编码的协议中，开发者也可以加入自己的增强信息（类似于H264中的SEI）用于一些场景功能的扩展。

Opus编码的特点是支持众多的帧长范围、码率范围、频率范围，内部有机制，来处理防止丢包策略，在低码率下依然能保持优异的音质。它主要适用于VOIP场景下的语音编码。

![图片](https://static001.geekbang.org/resource/image/b5/bd/b590b60d01377b1d6b63088759ee11bd.png?wh=1920x708)

在移动平台上，无论是单独的音频编码，还是视频编码中的音频流的编码，用得最广泛的就是AAC这一编码格式。所以我们这节课来重点学习一下音频的AAC编码。

AAC编码的方式有两种，一种是使用软件编码，另一种是使用Android与iOS平台的硬件编码。软件编码的实现方式我们会基于FFmpeg来讲解，后期无论你想用什么格式，都可以自己配置编码库来实现，编码部分的代码是可以复用的。这节课的输入是我们前两节课用录音器采集下来的PCM文件，最终编码成一个AAC编码格式的M4A文件。

在学习使用软件编码器编码AAC之前，让我们先来系统了解AAC这种编码格式，底层编码原理与算法我们就不介绍了，但是站在应用层角度我们要学习一下它的编码规格和封装格式，让我们一起来看一下吧。

## AAC编码格式详解

对于音视频应用层的开发者来讲，还是要掌握编码器本身的一些高级特性的，在AAC这个编码中，我们需要重点掌握的就是它的编码规格和封装格式。

### AAC的编码规格

AAC编码器常用的编码规格有三种，分别是LC-AAC、HE-AAC、HE-AACv2，这三种编码规格以及使用的消除冗余的技术手段如下图所示。

![](https://static001.geekbang.org/resource/image/ff/50/ffb29fce82cd718d7c2b9eda9c52b050.png?wh=1356x746)

其中LC-AAC的Profile是最基础的AAC的编码规格，它的复杂度最低，兼容性也是最好的，双声道音乐在128Kbps的码率下可以达到全频带（44.1kHz）的覆盖。

在LC-AAC的基础上添加SBR技术，形成HE-AAC的编码规格，SBR全称是Spectral Band Replication，其实就是消除频域上的冗余信息，可以在降低码率的情况下保持音质。内部实现原理就是把频谱切割开，低频单独编码保存，来保留主要的频谱部分，高频单独放大编码保存以保留音质，这样就保证在降低码率的情况下，更大程度地保留了音质。

在HE-AAC的基础上添加PS技术，就形成了HE-AACv2的编码规格，PS全称是Parametric Stereo，其实就是消除立体声中左右声道之间的冗余信息，所以使用这个编码规格编码的源文件必须是 **双声道** 的。内部实现原理就是存储了一个声道的全量信息，然后再花很少的字节用参数描述另一个声道和全量信息声道有差异的地方，这样就达到了在HE-AAC基础上进一步提高压缩比的效果。

我们使用FFmpeg命令行，用不同的编码规格，来把同一个输入文件编码成为三个文件，然后使用可视化的音频分析软件Praat看一下它们的质量，我们先来看一下原始文件source.wav（双声道、采样率为44.1kHz）导入到Praat中的频谱分布。

![图片](https://static001.geekbang.org/resource/image/10/4c/1066fdffa2b4c0034c993af5244cf04c.png?wh=1265x616)

可以看到图片中高频的部分到了22050，根据奈奎斯特采样定律，编码之后频带分布到22050就是全频带分布（原始格式44.1kHz），使用下面命令来编码文件。

```plain
ffmpeg -i source.wav -acodec libfdk_aac -b:a 48K lc_aac.m4a
ffmpeg -i source.wav -acodec libfdk_aac -profile:a aac_he -b:a 48K he_aac.m4a
ffmpeg -i source.wav -acodec libfdk_aac -profile:a aac_he_v2 -b:a 48K he_v2_aac.m4a

```

这三行命令使用的都是libfdk\_aac编码器，但是用了不同编码器规格，编码出了三个M4A文件。接下来我们把三个文件放到Praat中，如下图。

![图片](https://static001.geekbang.org/resource/image/7e/d5/7e42c6dbe9c0f650865913a73d6b39d5.png?wh=1260x1744)

可以看到lc\_aac.m4a的频带分布到了10KHz就被截断了，对高频部分影响比较大；而he\_aac这个文件的截止频率大约到16KHz以上，明显要比第一个好很多；再看第三个文件几乎达到了全频带覆盖，结合之前介绍的原理你就知道为什么这种编码规格可以达到全频带覆盖了。

AAC编码器的这三种编码规格之间的差异我们了解清楚之后，就可以根据自己的应用场景选择不同的编码规格和码率。

### AAC的封装格式

我们日常生活中常见的AAC编码的封装格式有两种，一种是ADTS封装格式，可以简单理解为以AAC为后缀名的文件，另外一种是ADIF封装格式，可以简单地理解为以M4A为后缀名的文件。

ADIF全称是Audio Data Interchange Format，是AAC定义在MPEG4里面的格式，字面意思是交换格式，是将整个流的Meta信息（包括AAC流的声道、采样率、规格、时长）写到头部，解码器只有解析了头部信息之后才可以解码具体的音频帧，像M4A封装格式、FLV封装格式、MP4封装格式都是这样的。

ADTS全称是Audio Data Transport Stream，是AAC定义在MPEG2里面的格式，含义就是传输流格式，特点就是从流中的任意帧位置都可以直接进行解码。这种格式实现的原理是在每一帧AAC原始数据块的前面都会加上一个头信息（ADTS+ES），形成一个音频帧，然后不断地写入文件中形成一个完整可播放的AAC文件。

![图片](https://static001.geekbang.org/resource/image/e5/f6/e599901899e61a372e59d642f8c403f6.png?wh=1920x1027)

如图所示，ADTS头分为固定头和可变头两部分，各自需要28位来表示，要构造一个ADTS头其实就是分配好这7个字节，下面我们来分配一下这七个字节。

```plain
int adtsLength = 7;
char *packet = malloc(sizeof(char) * adtsLength);
packet[0] = (char)0xFF;
packet[1] = (char)0xF9;

```

前12位表示同步字，固定为全1，表示为\[11111111\], \[1111\]；接下来的4位表示的是ID，我们这里是ADTS的封装格式ID，也就是1；Layer一般固定是00，protection\_absent代表是否进行误码校验，这里我们填1，所以前2个字节就是 \[11111111\] \[11111001\]，也就是代码上的两个Char类型的数字了。

下面我们不再一一分析每一位是怎么构造的了，直接以字节来讲解。后边的字节是编码规格、采样率下标（注意是下标，而不是采样率）、声道配置（注意是声道配置，而不是声道数）、数据长度的组合（注意packetLen是原始数据长度加上ADTS头的长度），最后一个字节一般也是固定的代码，如下：

```plain
int profile = 2; // AAC LC
int freqIdx = 4; // 44.1KHz
int chanCfg = 2; // CPE
packet[2] = (byte) (((profile - 1) << 6) + (freqIdx << 2) + (chanCfg >> 2));
packet[3] = (byte) (((chanCfg & 3) << 6) + (packetLen >> 11));
packet[4] = (byte) ((packetLen & 0x7FF) >> 3);
packet[5] = (byte) (((packetLen & 7) << 5) + 0x1F);
packet[6] = (char) 0xFC;

```

这里具体的编码Profile、采样率的下标以及声道数配置，可以点击 [链接](https://wiki.multimedia.cx/index.php?title=MPEG-4_Audio#Channel_Configurations) 查看相关的所有表示。一般编码器（Android的MediaCodec或者iOS的AudioToolbox）编码出来的AAC原始数据块我们称为ES流，需要在前面加上ADTS的头，才可以形成可播放的AAC文件，下节课我们就会用到。对于这种ADTS的压缩音频帧，也可以直接使用FFmpeg封装成M4A格式的文件。

在FFmpeg中，有一个类型的Filter叫做bit stream filter，主要是应用在一些编码格式的转封装行为中。对于AAC编码上述的两种封装格式，FFmpeg提供了aac\_adtstoasc类型的bit stream filter，用来把ADTS格式的压缩包（AVPacket）转换成ADIF格式的压缩包（Packet）。使用这个Filter可以很方便地完成AAC到M4A封装格式的转换，不用重新进行解码编码的操作，FFmpeg帮助开发者隐藏掉了实现细节，并且提供了更好的代码可读性。

了解了AAC的封装格式之后，我们就来学习如何使用FFmpeg来将PCM编码成AAC格式。

## 使用软件编码器编码AAC

我们用FFmpeg的API来编写的主要原因是，如果我们以后想使用别的编码格式，只需要调整相应的编码器ID或者编码器Name就可以了。原理就是FFmpeg帮我们透明掉了内部的细节，做了和各家编码器API对接的工作，给开发者暴露出了统一的面向FFmpeg API的接口。这里使用的编码器是libfdk\_aac，既然要使用第三方库libfdk\_aac，那么就必须在做交叉编译的时候，将libfdk\_aac这个库编译到FFmpeg中去。

由于我们想书写一个同时运行在Andorid平台和iOS平台上编码器工具类，所以构造一个C++的类，叫做audio\_encoder，向外暴露三个接口，分别是初始化、编码以及销毁方法。下面我会向你详细讲解每一个接口定义、职责描述以及内部实现（实现会根据FFmpeg版本不同稍有不同，FFmpeg5.0以上改动较大）。

### 初始化

初始化接口定义如下：

```plain
int init(int bitRate, int channels, int sampleRate, int bitsPerSample,
      const char* aacFilePath, const char * codec_name);

```

第一个参数是比特率，也就是最终编码出来的文件的码率，码率越高音质也就越好，对于双声道的音频，一般我们设置128Kb就可以了；接下来的参数是声道数、采样率和位深度；然后是最终编码的文件路径；最后是编码器的名字。注意，最后两个参数是有关联的，比如M4A文件要填入一个AAC的编码器（libfdk\_aac）名称、MP3文件要传入一个MP3编码器（lame）的名称。

这个接口内部会拿着这些信息把编码器初始化，如果编码器初始化成功，则返回0，失败则返回小于0的值。接口内部的核心实现如下：

![图片](https://static001.geekbang.org/resource/image/6b/ae/6b3d1722b702e3yy9a25b7244a4648ae.png?wh=1920x1202)

调用avformat\_alloc\_context方法分配出封装格式，然后调用avformat\_alloc\_output\_context2 传入输出文件格式，分配出上下文，即分配出封装格。之后调用avio\_open2方法将AAC的编码路径传入，相当于打开文件连接通道。这样就可以确定Muxer与Protocol了。

有了容器之后，就应该向容器中添加音频轨了，调用avformat\_new\_stream传入刚才的FormatContext构建出一个音频流（AVStream），接着要为这个Stream分配一个编码器，编码器是一个AVCodecContext类型的结构体，先调用avcodec\_find\_encoder\_by\_name函数，根据编码器名称找出对应的编码器，接着根据编码器分配出编码器上下文，然后给编码器上下文填充以下几个属性。

- 首先是codec\_type，赋值为AVMEDIA\_TYPE\_AUDIO，代表音频类型；
- 其次是bit\_rate、sample\_rate、channels等基本属性；
- 然后是channel\_layout，可选值是两个常量AV\_CH\_LAYOUT\_MONO代表单声道、AV\_CH\_LAYOUT\_STEREO代表立体声；
- 最后也是最重要的sample\_fmt，代表采样格式，使用的是AV\_SAMPLE\_FMT\_S16，即用2个字节来表示一个采样点。

这样，我们就把AVCodecContext这个结构体构造完成了，然后还可以设置profile，这里可以设置FF\_PROFILE\_AAC\_LOW。最后调用avcodec\_open2来打开这个编码器上下文，接下来为编码器指定frame\_size的大小，一般指定1024作为一帧的大小，现在我们就把音频轨以及这个音频轨里面编码器部分给打开了。

这里需要注意一下，某些编码器只允许特定格式的PCM作为输入源，比如对声道数、采样率、表示格式（比如lame编码器就不允许SInt16的表示格式）是有要求的。这时候就需要构造一个重采样器，来将PCM数据转换为可适配编码器输入的PCM数据，就是前面讲过的需要将输入的声道、采样率、表示格式和输出的声道、采样率、表示格式，传递给初始化方法，然后分配出重采样上下文SwrContext。

接下来还要分配一个AVFrame类型的inputFrame，作为客户端代码输入的PCM数据存放的地方，这里需要知道inputFrame分配的buffer的大小，默认一帧大小是1024，所以对应的buffer（按照uint8\_t类型作为一个元素来分配）大小就应该是：

```plain
bufferSize = frame_size * sizeof(SInt16) * channels;

```

也可以调用FFmpeg提供的方法av\_samples\_get\_buffer\_size，来帮助开发者计算，其实这个方法内部的计算公式就是上面所列的公式。如果需要重采样的处理的话，也需要额外分配一个重采样之后的AVFrame类型的swrFrame，作为最终得到结果的AVFrame。

在初始化方法的最后，需要调用FFmpeg提供的方法avformat\_write\_header将这个音频文件的Header部分写进去，然后记录一个标志isWriteHeaderSuccess，使其为true，因为后续在销毁资源的阶段，需要根据这个标志来判断是否调用write trailer方法写入文件尾部。

### 编码方法

编码接口定义如下：

```plain
void encode(byte* buffer, int size);

```

传入的参数是uint8\_t类型数组和它的长度，这个接口的职责就是将传递进来的PCM数据编码并写到文件中。接口内部实现就是将这个buffer填充入inputFrame，因为前面我们已经知道每一帧buffer需要填充的大小是多少了，所以这里可以利用一个while循环来做数据的缓冲，一次性填充到AVFrame中去。

调用avcodec\_send\_frame，当返回值大于0的时候，再调用avcodec\_receive\_packet来得到编码后的数据AVPacket，然后调用av\_interleaved\_write\_frame方法，就可以将这个packet写到最终的文件中去。

### 销毁方法

接口定义如下：

```plain
void destroy();

```

这个方法需要销毁前面分配的资源以及打开的连接通道。如果初始化了重采样器，那么就销毁重采样的数据缓冲区以及重采样上下文；然后销毁为输入PCM数据分配的AVFrame类型的inputFrame，再判断标志isWriteHeaderSuccess变量，决定是否需要填充duration以及调用方法av\_write\_trailer，然后关闭编码器和连接通道，最终释放FormatContext。

这个类写完之后，就可以集成到Android和iOS平台了，外界控制层需要初始化这个类，然后负责读写文件调用encode方法，最终调用销毁资源方法。

这节课涉及的代码比较多，后续我会把代码实例上传到GitHub上，你可以对着代码再进行练习一下。

## 小结

最后，我们可以一起来回顾一下。

![图片](https://static001.geekbang.org/resource/image/41/ce/41fb68f986803e354e81ae68fb50b0ce.png?wh=1136x1192)

一般我们采集得到的原始数据都会比较大，需要我们后期进行压缩编码。目前常用的编码格式有AAC、MP3、WAV、Opus几种，其中WAV格式编码是最常见的，MP3格式是兼容性最好的，而AAC在低码率（128Kb以下）场景下，音质大大超过MP3。目前在音视频开发领域，用得最广泛的就是AAC编码格式。

这节课，我们用FFmpeg实现了一个编码AAC文件的工具类，并且这个音频编码的工具类不单单可以用到编码AAC格式中，同时支持后续的其他编码，比如WAV编码和MP3编码等。在Android和iOS平台上都提供了各自的硬件编码器用于音频编码，下节课我会给你讲一讲怎么使用这两个平台的硬件编码器来给音频编码，一起期待一下吧！

## 思考题

这节课我们一起学习了AAC的编码格式，并且一起书写了一个用FFmpeg来编码AAC的工具类，上节课我们也掌握了音频采集的方法，那如何将它们结合起来，做一个系统录音机呢？思考一下，描述出你的架构设计。

欢迎在评论区分享你的思考，也欢迎你把这节课分享给更多对音视频感兴趣的朋友，我们一起交流、共同进步。下节课再见！