你好，我是展晓凯。今天我们一起学习使用移动平台的硬件编码器编码AAC。

上一节课，我们学习了AAC编码格式，还用FFmpeg书写了一个AAC编码工具类，这节课我们一起学习一下如何使用平台自身提供的硬件编码方法来给音频编码。因为两个平台的硬件编码器编码出来的是裸的ES流，如果要保存为可播放的AAC，还需要自己加上ADTS的头。

## Android平台的硬件编码器MediaCodec

我们先来看如何使用Android平台提供的MediaCodec来编码AAC。MediaCodec是Android系统提供的硬件编码器，它可以利用设备的硬件来完成编码，大大提升了编码的效率，并且可以节省CPU，让你的App运行起来更加流畅。

但使用MediaCodec编码对Android系统是有要求的，必须是4.1以上的系统，Android的版本代号在Jelly\_Bean以上。而且因为Android设备的碎片化太严重，所以兼容性方面不如软件编码好，你可以根据自己的实际情况决定是否使用Android平台的硬件编码能力。

下面我们来看MediaCodec使用方法。类似于软件编码提供的三个接口方法，这里也提供三个接口方法，分别完成初始化、编码数据和销毁编码器操作。

### 初始化

在初始化方法的实现中要构造一个MediaCodec实例出来，通过这个类的静态方法来构建。如果要构造一个AAC的Codec，代码如下：

```plain
MediaCodec mediaCodec = MediaCodec.createEncoderByType("audio/mp4a-latm");

```

上面这个方法，类似于前面讲到的FFmpeg中根据Codec的name来找出编码器，在构造出这个实例之后，就需要配置这个编码器了。配置编码器最重要的是传递一个MediaFormat类型的对象，这个对象里配置的是比特率、采样率、声道数以及编码AAC的Profile，此外，还要配置输入Buffer的最大值，代码如下：

```plain
MediaFormat encodeFormat = MediaFormat.createAudioFormat(MINE_TYPE, sampleRate, channels);
encodeFormat.setInteger(MediaFormat.KEY_BIT_RATE, bitRate);
encodeFormat.setInteger(MediaFormat.KEY_AAC_PROFILE, MediaCodecInfo.CodecProfileLevel.AACObjectLC);
encodeFormat.setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, 10 * 1024);

```

然后将这个对象配置到编码器中。

```plain
mediaCodec.configure(encodeFormat, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE);

```

最后一个参数代表了我们要配置一个编码器，而非解码器（如果是解码器则传递为0）。然后调用start方法就可以开启这个编码器了。

那接下来如何将PCM数据送给MediaCodec进行编码呢？我们先来看一下MediaCodec的工作原理图，如图所示。

![图片](https://static001.geekbang.org/resource/image/10/d4/10701bd6e882b52cb33d10101138d3d4.png?wh=1440x694)

左右两边的Client代表我们应用层书写代码的地方，左边Client元素代表需要应用层将PCM放到inputBuffers里某一个具体的buffer里去，右边的Client元素代表将编码之后的原始AAC数据从outputBuffers里一个具体的buffer中取出来。

开发者可以从MediaCodec实例中取出两个buffer来，一个是inputBuffers，用来存放输入的PCM数据（类似于FFmpeg编码的AVFrame）；另外一个是outputBuffers，用来存放编码之后的原始AAC的数据（类似于FFmpeg编码的AVPacket）。

```plain
ByteBuffer[] inputBuffers = mediaCodec.getInputBuffers();
ByteBuffer[] outputBuffers = mediaCodec.getOutputBuffers();

```

初始化方法的核心实现完成了，接下来我们看一下编码方法的实现。

### 编码

首先，从MediaCodec里拿出一个空闲的InputBuffer，其实这里获取的不是一个buffer，而是一个buffer Index，然后从我们上面取出来的这个InputBuffers里面拿出buffer Index所代表的这个buffer，然后填充数据，并且把填充好的buffer送给Codec，就是调用Codec的codec.queueInputBuffer。

```plain
int bufferIndex = codec.dequeueInputBuffer(-1);
if (inputBufferIndex >= 0) {
    ByteBuffer inputBuffer = inputBuffers[bufferIndex];
    inputBuffer.clear();
    inputBuffer.put(data);
    long time = System.nanoTime();
    codec.queueInputBuffer(bufferIndex, 0, len, time, 0);
}

```

将PCM数据送给MediaCodec之后，那如何获取出编码之后的数据呢？我们只需要从Codec里面拿出一个编码好的buffer的Index，通过Index取出对应的outputBuffer，然后将数据读取出来就可以了。读取出来数据是裸的AAC的ES流，需要我们自己添加上ADTS头部，然后写文件，最后把这个outputBuffer放回待编码填充队列里面去。

```plain
BufferInfo info = new BufferInfo();
int index = codec.dequeueOutputBuffer(info, 0);
while (index >= 0) {
    ByteBuffer outputBuffer = outputBuffers[index];
    if (outputAACDelegate != null) {
        int outPacketSize = info.size + 7;
        outputBuffer.position(info.offset);
        outputBuffer.limit(info.offset + info.size);
        byte[] outData = new byte[outPacketSize];
        //添加ADTS 代码后面会贴上
        addADTStoPacket(outData, outPacketSize);
        //将编码得到的AAC数据 取出到byte[]中 偏移量offset=7
        outputBuffer.get(outData, 7, info.size);
        outputBuffer.position(info.offset);
        outputAACDelegate.outputAACPacket(outData);
    }
    codec.releaseOutputBuffer(index, false);
    index = mediaCodec.dequeueOutputBuffer(bufferInfo, 0);
}

```

上述代码中构造出了BufferInfo类型的对象，当从Codec的输出缓冲区拿取一个buffer的时候，Codec会把这个buffer的描述信息放到这个对象中，接下来我们读取数据以及确定数据大小都要根据这个对象的信息来处理。

这样周而复始地调用这个方法，就可以将PCM数据编码成AAC，并且交给Delegate把数据输出到文件中。在编码工作完成之后需要调用销毁方法，接下来我们就来看一下销毁方法。

### 销毁

使用完MediaCodec编码器之后，就需要停止运行并释放编码器。

```plain
if (null != mediaCodec) {
    mediaCodec.stop();
    mediaCodec.release();
}

```

这样整个类的核心实现我们就讲完了，外界调用端需要做的事情是先初始化这个类，然后读取PCM文件并调用这个类的编码方法，实现这个类的Delegate接口，在重写的方法中将输出带有ADTS头的AAC码流直接写文件，最终编码结束之后，调用这个类的停止编码方法。

## iOS平台的硬件编码器AudioToolbox

在iOS平台上可使用AudioToolbox下面的Audio Converter Services来完成硬件编码，iOS平台提供的这个服务，看名字就知道它是一个转换服务，那么它能够提供哪几方面的转换呢？

- PCM到PCM：可以转换位深度、采样率以及表示格式，也包括交错存储和平铺存储之间的转换，这与FFmpeg里的重采样器非常类似。
- PCM到压缩格式的转换：相当于一个编解码器，当然可以应用在编解码场景。

iOS平台在多媒体方面提供的API是非常强大的，并且兼容性也非常好。随着学习的深入，你会逐渐了解更多更好用的API，而这节课，我们利用的就是它所提供的编码服务，将PCM数据编码为AAC格式的数据。

AudioToolbox里编码出来的AAC数据也是裸数据，在写入文件之前也需要手动添加上ADTS头信息，最终写出的文件才可以被系统播放器播放，具体添加头信息的操作和Android平台的操作是一样的，这里就不重复了。类似于软件编码提供的三个接口方法，这里也提供三个接口方法，分别完成初始化、编码数据和销毁编码器操作。

在介绍这三个方法的实现之前，我们先定义一个Protocol，名称定为FillDataDelegate，需要调用端来实现这个Delegate，这里面定义了三个方法：

我们先看第一个方法的方法原型。

```plain
- (UInt32) fillAudioData:(uint8_t*) sampleBuffer bufferSize:(UInt32) bufferSize;

```

当编码器（转换器）需要编码一段PCM数据的时候，就通过调用这个方法来让实现这个Delegate的调用端来填充PCM数据。

再看第二个方法的方法原型。

```plain
- (void) outputAACPakcet:(NSData*) data presentationTimeMills:(int64_t)presentationTimeMills error:(NSError*) error;

```

待编码器成功编码出一帧AAC的Packet之后，我们先给这段数据添加ADTS头，然后通过调用上面这个方法来让调用端输出编码后的数据。

最后一个方法的方法原型是onCompletion。

```plain
- (void) onCompletion;

```

待编码（转换）结束之后，调用上面这个方法来让调用端做资源销毁和关闭IO等操作。

接下来我们来看一下这三个接口的核心实现。

### 初始化

还记得之前我们讲过，在iOS平台提供的音视频API中，如果需要用到硬件Device相关的API，就需要配置各种Session。而如果要用到与配置相关API，一般就需要配置各种的Description来描述配置的信息。而在这里需要配置的Description就是我们 [第一节课iOS平台的音频格式](http://time.geekbang.org/column/article/543649) 里讲过的。这里需要分别配置一个input和一个output部分的Description，用来描述编码前后的音频格式。

首先是输入部分的Description的配置。

```plain
//构建InputABSD
AudioStreamBasicDescription inASBD = {0};
UInt32 bytesPerSample = sizeof (SInt16);
inASBD.mFormatID = kAudioFormatLinearPCM;
inASBD.mFormatFlags = kAudioFormatFlagIsSignedInteger | kAudioFormatFlagIsPacked;
inASBD.mBytesPerPacket = bytesPerSample * channels;
inASBD.mBytesPerFrame = bytesPerSample * channels;
inASBD.mChannelsPerFrame = channels;
inASBD.mFramesPerPacket = 1;
inASBD.mBitsPerChannel = 8 * channels;
inASBD.mSampleRate = inputSampleRate;
inASBD.mReserved = 0;

```

可以看到，这里输入的是PCM格式，表示格式是有符号整型并且是交错存储的，这一点十分关键，因为要按照设置的格式填充PCM数据，或者反过来说，客户端代码填充的PCM数据是什么格式的，就应该在这里配置给input，描述的mFormatFlags是什么。存储格式是指交错存储或非交错存储，输出或者输入数据都存储于AudioBufferList中的属性ioData中。假设声道是双声道的，对于交错存储（IsPacked）来讲，对应的数据格式分布如下：

```plain
	ioData->mBuffers[0]: LRLRLRLRLRLR…

```

而对于非交错的存储（NonInterleaved）来讲，数据格式分布如下：

```plain
	ioData->mBuffers[0]: LLLLLLLLLLLL…
	ioData->mBuffers[1]: RRRRRRRRRRRR…

```

这也就要求客户端代码，要按照配置的格式描述进行填充或者获取数据，否则就会出现不可预知的问题。由于我们提供的数据就是交错存储的，所以Description后续几个关键值都得乘以channels。这样输入的配置就已经书写好了，我们再来看一下输出部分的Description的配置。

```plain
//构造OutputABSD
AudioStreamBasicDescription outASBD = {0};
outASBD.mSampleRate = inASBD.mSampleRate;
outASBD.mFormatID = kAudioFormatMPEG4AAC;
outASBD.mFormatFlags = kMPEG4Object_AAC_LC;
outASBD.mBytesPerPacket = 0;
outASBD.mFramesPerPacket = 1024;
outASBD.mBytesPerFrame = 0;
outASBD.mChannelsPerFrame = inASBD.mChannelsPerFrame;
outASBD.mBitsPerChannel = 0;
outASBD.mReserved = 0;

```

上面需要注意的是，mFormatID需要配置成AAC的编码格式， Profile配置为低运算复杂度的规格（LC），因为这样兼容性最好。另外，配置一帧数据的地方需要填写1024，这是AAC编码格式要求的帧大小。

到这里，输入和输出的Description就配置好了，接下来就需要构造一个编码器实例了，但是构造编码器实例也得从配置一个编码器描述开始。编码器的描述指定编码器类型是kAudioFormatMPEG4AAC，编码的实现方式使用兼容性更好的软件编码方式kAppleSoftwareAudioCodecManufacturer。通过这两个输入构造出一个编码器类的描述，它可以告诉iOS系统开发者到底想使用哪个编码器。

![图片](https://static001.geekbang.org/resource/image/f0/05/f0f4dc77bc1a6d0cfc1d5592e382c805.png?wh=1920x900)

有了上述的三个Description（输入和输出数据的描述、编码器的描述），就可以构造出一个AudioConverterRef实例了，代码如下：

```plain
OSStatus status = AudioConverterNewSpecific(&inABSD, &outABSD, 1, codecDescription, &_audioConverter);

```

第三个参数1是指明要创建编码器的个数，最后一个参数就是我们想要构造的转码器实例对象，返回值是OSStatus类型的变量，如果返回的不是0，则表示出错了，成功的话返回常量noErr。

接下来就可以对这个转码实例设置比特率了。

```plain
AudioConverterSetProperty(_audioConverter, kAudioConverterEncodeBitRate, sizeof(bitRate), &bitRate);

```

要获取编码之后输出的AAC的Packet size最大值是多少，因为我们需要按照这个值来分配编码后数据的存储空间，从而让编码器输出到这个存储区域里面来，代码如下：

```plain
UInt32 size = sizeof(_aacBufferSize);
AudioConverterGetProperty(_audioConverter, kAudioConverterPropertyMaximumOutputPacketSize, &size, &_aacBufferSize);
_aacBuffer = malloc(_aacBufferSize * sizeof(uint8_t));
memset(_aacBuffer, 0, _aacBufferSize);

```

到这里，初始化方法就结束了，这里面除了分配出编码器还有给编码器设置比特率之外，还根据输出的AAC的Packet大小分配了存储AAC的Packet的空间。接下来我们看编码方法的实现。

### 编码

第一步要用前面初始化好的\_aacBuffer构造出一个AudioBufferList的结构体，作为编码器输出AAC数据的存储容器，代码如下：

```plain
AudioBufferList outAudioBufferList = {0};
outAudioBufferList.mNumberBuffers = 1;
outAudioBufferList.mBuffers[0].mNumberChannels = _channels;
outAudioBufferList.mBuffers[0].mDataByteSize = _aacBufferSize;
outAudioBufferList.mBuffers[0].mData = _aacBuffer;

```

构造出了这个结构体之后，就可以去调用编码器的编码函数了。但是你可能会问，我们还没有拿到PCM数据，怎么调用编码器编码呢，数据源从哪里来呢？

AudioToolbox这里的设计是按照回调函数的方式获取数据源，而这个回调函数就设置在编码函数调用中，编码函数调用如下：

```plain
UInt32 ioOutputDataPacketSize = 1;
OSStatus status = AudioConverterFillComplexBuffer(
        _audioConverter, inInputDataProc, (__bridge void *)(self),
        &ioOutputDataPacketSize, &outAudioBufferList, NULL);

```

函数中，第一个参数是编码器；第二个参数就是用来填充PCM数据的回调函数，第三个参数就是对象本身，一般回调函数都会传一个Context进去，便于调用本对象的方法；接下来的参数就是输出的AAC Packet的大小，还有编码之后的AAC Packet存放的容器；最后一个参数是输出AAC Packet的Description，一般填充为NULL。

接下来我们看一下这个回调函数的原型，以及在回调函数中我们如何填充PCM数据。回调函数的原型如下：

```plain
OSStatus inInputDataProc(AudioConverterRef inAudioConverter, UInt32
        *ioNumberDataPackets, AudioBufferList *ioData,
        AudioStreamPacketDescription **outDataPacketDescription,
        void *inUserData)

```

这个回调函数中的第一个参数是编码器的实例；第二个参数是需要填充多少个PCM数据的数量；第三个参数就是应用层要填充PCM数据的容器；第四个参数是填充输出Packet的Description，但是在这里不使用；最后一个参数就是上下文，即在调用编码函数（转换函数）的时候传入的对象本身。这里我们直接将inUserData强制转换成这个类型的一个实例对象，就可以调用这个对象的方法了，代码如下：

```plain
AudioToolboxEncoder *encoder = (__bridge AudioToolboxEncoder *)(inUserData);
[encoder fillAudioRawData:ioData ioNumberDataPackets:ioNumberDataPackets];

```

在这个静态的回调函数里，通过上下文对象的强制类型转换，就可以得到对象本身，进而可以调用fillAudioRawData这个方法。

接下来我们看下这个方法的具体实现，首先根据需要填充的帧的数目、当前声道数以及表示格式，计算出需要填充的uint8\_t类型的buffer大小。

```plain
int bufferLength = ioNumberDataPackets * channels * sizeof(short);

```

根据公式算出来的bufferLength来分配出pcmBuffer，然后调用Delegate里面的fillAudioData:bufferSize:方法来填充数据，最后将Delegate中填充好的pcmBuffer放入ioData容器中并返回，这样就完成了给编码器提供PCM数据的回调函数。

编码函数执行结束之后，如果status是noErr，那编码好的AAC数据就存放在前面定义好的outAudioBufferList这个结构体里了。

从这个结构体的属性mBuffers\[0\].mData中，拿出AAC的原始Packet，添加上ADTS头信息，然后调用Delegate的方法outputAACPakcet，由Delegate输出AAC数据，这时候的AAC数据就是编码之后带有ADTS头信息的数据。最终如果输入数据为空，则代表结束，我们就可以调用Delegate的方法onCompletion，让调用端做一些资源关闭以及销毁操作了。

### 销毁

最后来看销毁接口的实现，我们先把分配的填充PCM数据的pcmBuffer释放掉，然后把分配的接收编码器输出的aacBuffer释放掉，最后释放掉编码器，代码如下：

```plain
if(_pcmBuffer) {
    free(_pcmBuffer);
    _pcmBuffer = NULL;
}
if(_aacBuffer) {
    free(_aacBuffer);
    _aacBuffer = NULL;
}
AudioConverterDispose(_audioConverter);

```

到这里，这三个接口方法就全部实现了。

最后我们看集成阶段。首先，调用端需要实现这个类中定义的FillDataDelegate类型的Protocol，并且要重写里面的fillAudioData方法，以便给这个编码器类提供PCM数据。接着重写outputAACPacket方法来输出AAC的码流数据，重写onCompletion方法来关闭自己读写文件等操作；然后实例化我们的编码器，开启一个线程（使用GCD）来调用编码方法；最终编码结束之后，在dealloc方法中调用结束编码的方法。

## 小结

最后，我们可以一起来回顾一下。

这节课我们使用Android平台的硬件编码器MediaCodec和iOS平台的硬件编码器AudioToolbox来编码AAC，最终得到AAC编码格式的数据。相比于上节课我们用软件编码器编码AAC，使用硬件编码器可以有效提升我们的编码效率，节约CPU资源。

在iOS平台，你可以尝试使用硬件编码来实现速度的优化，当然也可以使用ExtAudioFile等API接口来操作。Android平台碎片化比较严重，可能会存在兼容性问题，所以我更推荐你直接使用软件编码，因为音频编码对于CPU的消耗或者计算性能要求并不会太高。

## 思考题

这两节课我们重点讲解了音频的AAC编码，那么我来考考你，AAC常用的编码规格中，HE-AAC和LC-AAC两种编码的每一帧音频帧的时长是多少呢？做一个实验来看看吧，欢迎在评论区分享你的答案，也欢迎你把这节课分享给更多对音视频感兴趣的朋友，我们一起交流、共同进步。下节课再见！