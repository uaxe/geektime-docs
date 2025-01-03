你好，我是展晓凯。今天我们来一起学习iOS平台的音频采集。

iOS平台提供了多套API来采集音频，分别是AVAudioRecoder，AudioQueue以及AudioUnit。这三种方法各有优缺点，适用于不同的场景，我们一起看一下。

![图片](https://static001.geekbang.org/resource/image/76/5d/76f28e48a0bc736af8b03b26b3a0225d.png?wh=1920x587)

- AVAudioRecorder，类似于AVAudioPlayer，属于端到端的API，存在于AVFoundation框架中。当我们想指定一个路径将麦克风的声音录制下来的时候，就可以使用这一个API。优点是简单易用，缺点是无法操控中间的数据。
- AudioQueue，之前我们使用AudioQueue渲染过音频，其实AudioQueue也可以录制音频，也是对AudioUnit的封装，它允许开发者获取、操控中间的数据（按照配置的数据格式）。优点是灵活性较强，缺点是上手难度较高。
- AudioUnit，是音频最底层的API接口，之前我们使用AudioUnit渲染过音频，和AudioQueue一样，我们也可以使用它录制音频。当我们需要使用VPIO（VoiceProcessIO）等处理音频的AudioUnit、需要使用实时耳返或在低延迟场景下，必须使用这一层的API。优点是灵活性最强，缺点是上手难度更高。

这节课我会重点讲解如何使用AudioQueue与AudioUnit来采集音频，但在学习这两个接口之前，我们还需要先设置并激活一下录制场景下AVAudioSession。

## 设置AVAudioSession

要想使用iOS的麦克风录音，首先要为App声明使用麦克风的权限，在工程目录下找到info.plist，然后在里面新增麦克风权限的声明。

```plain
<key>NSMicrophoneUsageDescription</key>
<string>microphoneDesciption</string>

```

这样添加完之后，就让系统知道了App要访问系统的麦克风权限。

接下来需要判断一下麦克风的授权情况。如果已经询问过了，就根据实际授权的情况进行处理，如果未授权可以引导用户跳转设置页面重新打开，代码如下：

```plain
[[UIApplication sharedApplication] openURL:[NSURL URLWithString:UIApplicationOpenSettingsURLString] options:@{} completionHandler:^(BOOL success) {
}];

```

如果没有询问过用户是否授权，就调用询问接口。

```plain
[[AVAudioSession sharedInstance] requestRecordPermission:^(BOOL granted) {
  if (granted) {
    //获得授权
  } else {
    //未获得授权
  }
}];

```

根据实际获得授权的情况，来决定是否继续开启录音流程。

当获得授权之后，就要开启一个音频会话了，即设置对应的AVAudioSession，代码如下：

```plain
[[AVAudioSession sharedInstance] setPreferredIOBufferDuration:AUDIO_RECORD_BUFFER_DURATION error:&error];
[[AVAudioSession sharedInstance] setPreferredSampleRate:48000 error:nil];
[[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryPlayAndRecord  error:nil];
[[AVAudioSession sharedInstance] setActive:YES error:nil];

```

代码的第一行是设置缓冲区的大小，一般设置得越大延迟越高，但是性能越好。如果需要实时耳返的话，一般设置5～8ms；不需要实时耳返的场景，设置23ms左右即可。第二行是设置采样率，目前的主流设备可以都设置成48k的采样率，兼容性是最好的；第三行是设置Category，如果是不戴耳机或戴有线耳机的情况，根据上面的代码设置就可以，但是如果是蓝牙耳机想保留高音质采集，就需要这样设置：

```plain
[[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryPlayAndRecord withOptions:AVAudioSessionCategoryOptionAllowBluetoothA2DP error:nil];

```

这里的麦克风使用的是机身麦克风，如果想使用蓝牙本身的麦克风，设置代码如下：

```plain
[[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryPlayAndRecord  withOptions:AVAudioSessionCategoryOptionAllowBluetooth error:nil];

```

最后，激活AVAudioSession之后，就可以使用具体的录音框架了，下面就让我们先来学习一下用AudioQueue来采集音频。

## 如何使用AudioQueue采集音频？

还记得我们 [第1节课](https://time.geekbang.org/column/article/543649) 使用AudioQueue来渲染音频的方法吗？和渲染音频相比，采集音频就相当于是一个相反的过程，我们先来看一下AudioQueue采集音频的结构图。

![图片](https://static001.geekbang.org/resource/image/10/6f/10f88a7a26ef4b3bd0f691296c53f76f.png?wh=1920x782)

从结构图里，我们可以看到AudioQueue的输入是左侧的麦克风，输出是把BufferQueue里面填充好数据的buffer回调给业务层，让业务层自己处理或者执行IO操作。

下面我们再看一下AudioQueue录音的整个流程图。

![图片](https://static001.geekbang.org/resource/image/45/73/45a9cb9ac4bbb1d2ffd66b49b1cebd73.png?wh=1920x2035)

1. AudioQueue把采集进来的音频填充到第一个buffer里。
2. 填满了第一个buffer之后，会把第一个buffer返回给业务层处理，同时把采集进来的音频填充到第二个buffer里。
3. 业务层把接收到的第一个buffer写到磁盘里。
4. 业务层把第一个buffer再返还给AudioQueue，也就是重新让buffer入队。
5. AudioQueue填充好了第二个buffer回调给业务端，同时把麦克风采集到的数据写到第三个buffer里。
6. 业务层把第二个buffer写到磁盘上，同时把第二个buffer再返还给AudioQueue。

你可以再回顾一下 [AudioQueue渲染音频](https://time.geekbang.org/column/article/543649) 的数据流程，录制的数据运行流程恰恰是和音频渲染相反的一个过程： **渲染音频是需要业务端来填充数据，然后给AudioQueue进行播放；采集音频是需要业务端把采集到的数据消费掉，然后再返回给AudioQueue来填充音频。**

在学习AudioQueue音频渲染的时候，我们了解了AudioQueue内部是可以自动做解码操作的，其实在采集音频过程中也有一个逆过程的处理，就是AudioQueue内部会根据我们指定的数据格式来执行压缩编码，你可以看一下流程图。

![图片](https://static001.geekbang.org/resource/image/81/3f/81a4e7e86fe0d97ed67eb3yyf5556b3f.png?wh=1920x918)

在创建采集音频类型的AudioQueue的时候，要指定dataFormat（ASBD类型）参数，而这个DataFormat里有一个mFormatID属性，当这个属性被指定为kAudioFormatMPEG4AAC的时候，AudioQueue内部就会自动把采集到的PCM数据编码为AAC类型的数据返回给业务层。

在实际使用过程中，你可以根据自己的需要来制定dataFormat，如果你需要PCM数据，那么这里就不需要使用AudioQueue的编码能力，我们要根据自己的使用场景来做配置。

在充分理解了AudioQueue的整体数据流程之后，我们再来看一下它的核心使用方法。第一步是创建采集音频类型的AudioQueue。

```plain
AudioQueueNewInput(&dataformat, recoderCB, (__bridge void *)self, NULL, NULL, 0, &queueRef);

```

代码里的dataFormat代表期望AudioQueue采集音频之后返回给业务层的具体的音频格式，recoderCB代表AudioQueue填充好一个buffer之后回调给业务层的方法，这个方法的实现如下：

```plain
static void recoderCB(void *aqData, AudioQueueRef inAQ, AudioQueueBufferRef inBuffer, const AudioTimeStamp *timestamp, UInt32 inNumPackets, const AudioStreamPacketDescription *inPacketDesc) {
    //1 inBuffer->mAudioData 处理 & IO

    //2 重新入队
    AudioQueueEnqueueBuffer(inAQ, inBuffer, 0, NULL);
}

```

这个方法内部消费掉inBuffer里的音频数据，然后将这个buffer重新入队。

当创建好一个AudioQueue之后，一般要为这个AudioQueue分配3个buffer，然后依次入队。

```plain
for (int i = 0; i < kNumberBuffers; i++) {
  AudioQueueAllocateBuffer(queueRef, self.bufferBytesSize, &buffers[i]);
  AudioQueueEnqueueBuffer(queueRef, buffers[i], 0, NULL);
}

```

其中代码里的bufferBytesSize代表每个buffer的数据大小，这个可以根据dataFormat与期望的数据长度（比如50ms）来计算。

最后调用Start方法来启动AudioQueue。

```plain
AudioQueueStart(mQueue, NULL)

```

像Stop、Reset等方法这里我就不再赘述了。整体来看，AudioQueue的使用其实比较简单，核心就是配置好dataFormat，然后实现回调函数，再按照期望的dataFormat处理数据就可以了。

## 如何使用AudioUnit采集音频？

我们这个部分使用的AudioUnit接口，其实在专栏的 [第2节课](https://time.geekbang.org/column/article/543993) 已经详细地讲过了，所以这里我们就直接来看如何使用AudioUnit实现人声的采集，同时还会给耳机一个监听耳返。等完成这个功能之后，你就会感叹这在iOS平台上实现起来太简单了。

在激活AVAudioSession之后，我们就要构造一个AUGraph了，构造AUGraph的过程和第2节课渲染音频时构造的AUGraph几乎是一致的，这里就不再赘述了。由于这里我们要使用采集音频的能力，所以要启用RemoteIO这个AudioUnit的InputElement，代码如下：

```plain
static UInt32 kInputBus = 1;
UInt32 flag = 1;
AudioUnitSetProperty(ioUnit, kAudioOutputUnitProperty_EnableIO, kAudioUnitScope_Input, kInputBus, &flag, sizeof(flag));

```

RemoteIO这个AudioUnit其实是比较特别的，InputElement（kInputBus的值为1）代表的是麦克风，而OutputElement代表的是扬声器，上述这行代码就是启用RemoteIOUnit的InputElement。

为了支持开发的App可以在后续扩展出Mix一轨伴奏这个功能，我们需要额外在AUGraph中增加MultiChannelMixer这个AudioUnit。由于每个AudioUnit的输入输出格式并不相同，所以这里还要使用AudioConvert这个AudioUnit来把输入的AudioUnit连接到MixerUnit上。最终让MixerUnit连接上RemoteIO的OutputElement，将声音送到耳机或者扬声器中。

这里需要注意，如果没有插耳机的情况下需要Mute（消音）掉这一路，否则就会出现啸叫的现象。到这里我们就把AUGraph构建出来了，如下图所示。

![图片](https://static001.geekbang.org/resource/image/d9/36/d952faf11ee9b2c96b29b1b1a61ed736.png?wh=2145x803)

如何把采集的音频存储成为一个文件呢？

我们可以在RemoteIO这个节点的OutputElement增加一个回调，然后在回调方法中来拉取预期节点的数据，同时也可以去写文件，这种方式其实已经在音频渲染的时候使用过。首先给RemoteIO这个AudioUnit的OutputElement增加一个回调。

```plain
AURenderCallbackStruct finalRenderProc;
finalRenderProc.inputProc = &renderCallback;
finalRenderProc.inputProcRefCon = (__bridge void *)self;
status = AUGraphSetNodeInputCallback(_auGraph, _ioNode, 0, &finalRenderProc);

```

然后在上述的回调方法的实现中，把它的前一级MixerUnit的数据渲染出来，同时写文件。

```plain
static OSStatus renderCallback(void *inRefCon,
        AudioUnitRenderActionFlags *ioActionFlags, const AudioTimeStamp
        *inTimeStamp, UInt32 inBusNumber, UInt32 inNumberFrames, AudioBufferList
        *ioData){
    OSStatus result = noErr;
    __unsafe_unretained AudioRecorder *THIS = (__bridge AudioRecorder *)inRefCon;
    AudioUnitRender(THIS->_mixerUnit, ioActionFlags,
            inTimeStamp, 0, inNumberFrames, ioData);
    //Write To File
    return result;
}

```

关于写文件，我们会在第12节课使用AudioToolbox来给文件编码，但是这里我们使用一个更高级的API——ExtAudioFile 来写文件，其实这个ExtAudioFile内部封装了AudioToolbox里面的AudioConverterReference。iOS提供的这个API只需要我们设置好输入格式和输出格式以及输出文件路径和文件格式。

```plain
AudioStreamBasicDescription destinationFormat;
CFURLRef destinationURL;
result = ExtAudioFileCreateWithURL(destinationURL, kAudioFileCAFType,
        &destinationFormat, NULL, kAudioFileFlags_EraseFile, &audioFile);
result = ExtAudioFileSetProperty(audioFile,
        kExtAudioFileProperty_ClientDataFormat, sizeof(clientFormat),
        &clientFormat);
UInt32 codec = kAppleHardwareAudioCodecManufacturer;
result = ExtAudioFileSetProperty(audioFile,
        kExtAudioFileProperty_CodecManufacturer, sizeof(codec), &codec);

```

在需要给文件编码时，就直接写入数据。

```plain
ExtAudioFileWriteAsync(audioFile, inNumberFrames, ioData);

```

在停止写入的时候调用关闭方法即可。

```plain
ExtAudioFileDispose(audioFile);

```

注意，这里调用的是WriteAsync，就是异步的方式来写文件，这样它不会阻塞Remote IO这个线程。在停止写入的时候，我们关闭这个方法就可以了。

最终就可以得到我们想要的文件了，你可以从应用的沙盒中将保存的文件拿出来（在XCode中用Device或iExplorer取出文件），然后播放试听一下。

## 小结

最后，我们一起来回顾一下今天的内容。

在iOS平台采集音频数据，比较常用的就是AVAudioRecoder，AudioQueue以及AudioUnit三套接口。

- AVAudioRecorder使用起来比较简单，如果是简单的录音，使用AVAudioRecorder就可以。但因为无法操控中间的数据，它提供不了更高级的能力支持。
- 使用AudioQueue录制音频，灵活性比较强。如果只是获取内存中的录音数据，然后编码、输出，使用AudioQueue来采集音频会更适合。
- 使用AudioUnit录制音频灵活性最强，如果要使用更多的音效处理以及实时的监听功能，那么使用AudioUnit会更方便一些。

后续我们视频录制器项目中，使用的都是AudioUnit，因为实现的场景不单单需要耳返，也需要音效的实时处理等功能。

## 思考题

你可以使用一下回森这个App，这个App有一个特色的功能就是语音弹幕，它支持用户在观看音乐作品的同时演唱一段弹幕（启动音频采集），而从听到唱的过程中整个音乐作品播放是非常流畅的，这里我给你留两个问题：

1. 这个App是如何实现启动录音的时候音乐作品可以流畅地播放的呢？
2. 使用蓝牙耳机的情况下，在保证录制高音质音频的同时，音乐作品如何保持声音的流畅性呢？

欢迎在评论区留下你的思考，也欢迎你把这节课分享给更多对音视频感兴趣的朋友，我们一起交流、共同进步。下节课再见！