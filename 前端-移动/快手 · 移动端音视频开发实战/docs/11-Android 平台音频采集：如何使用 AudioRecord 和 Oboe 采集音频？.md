你好，我是展晓凯。今天我们来一起学习Android平台的音频采集。

视频播放器是将一个视频文件通过解封装、解码、渲染等工作，让用户可以听到声音、看到画面，而视频录制器恰恰是一个逆向的过程，是将麦克风采集到的声音、摄像头采集到的画面通过编码、封装，最终得到一个视频文件。所以整个项目的前置知识包括音视频的采集、编码还有音视频同步等，上一节课我们一起学习了iOS平台的音频采集方法，这节课我们就一起来看Android平台给我们提供了哪些音频采集的方法吧。

## Android平台的音频采集技术选型

![图片](https://static001.geekbang.org/resource/image/f0/eb/f02ac0c612eyyeceebbc56898fc894eb.png?wh=1920x670)

### SDK层提供的采集方法

Android SDK 提供了两套音频采集的API接口，分别是MediaRecorder 和 AudioRecord。前者是一个端到端的API，它可以直接把手机麦克风录入的音频数据进行编码压缩（如AMR、MP3等）并存储成文件；而后者则更底层一些，可以让开发者更加灵活地控制麦克风采集到的PCM数据。

如果想简单地做一个录音机，并且录制出一个音频文件，首选肯定是MediaRecorder，而如果需要对音频做进一步的算法处理，或者需要采用第三方的编码库进行编码压缩，那么就需要使用AudioRecord了。我们的视频录制器场景显然更适合选用第二种方式，使用AudioRecord来采集音频。

### NDK层提供的采集方法

Android NDK也提供了两套音频采集的API接口，就是OpenSL ES和AAudio，其中AAudio是在Android 8.0系统以上才可以使用的。这两个API接口也都属于底层接口，可以获取实时采集到的PCM数据。相比于AudioRecord，Native层提供的采集方法具有更低的延迟与更高的性能，但是由于Android设备与系统厂商碎片化的问题，兼容性比不上AudioRecord，比如某些品牌的手机上会有声音采集音量过小，采集的音频有杂音等问题。

如果在一些需要低延迟音频采集的场景比较适合使用这两个音频采集的方法，比如实时耳返场景、更低延迟的VOIP场景等。如果想为自己的工程构建音频采集框架，是需要同时支持SDK层AudioRecord采集和Native层采集的。而在Native层直接使用Google开源的Oboe框架是一个比较好的选择，因为它屏蔽掉了OpenSL ES与AAudio的内部实现细节，提供了统一的API接口。所以在这节课的最后一部分，我会以Oboe为例给你讲解Native层录制音频的方法。

### 录音权限

其实无论是SDK层还是NDK层的音频采集，Android平台都要求，在采集之前应用必须要向用户显示申请权限，所以这里我们还需要了解一下，应用如何在Android平台获取录音权限。

首先，需要在AndroidManifest.xml这个应用的配置文件中，增加权限的声明。

```plain
<uses-permission android:name="android.permission.RECORD_AUDIO" />

```

如果我们在获取到PCM数据之后，还要把数据写入SDCard中，就需要额外申请系统的文件权限。声明好了之后，就需要检查当前的授权状态。如果已经授权了，可以直接开启录音器采集音频。如果没有授权的话，就需要去申请授权。

```plain
if(ContextCompat.checkSelfPermission(this, android.Manifest.permission.RECORD_AUDIO)
                        != PackageManager.PERMISSION_GRANTED){
  //未授权，则进行申请权限
  ActivityCompat.requestPermissions(this,new String[]{android.Manifest.permission.RECORD_AUDIO},1);
}else {
  //已经授权，可以开启录音器
}

```

申请授权的代码中，第一个参数传递的是一个Activity类型的对象，申请授权一般是用系统的弹窗来提示用户，应用索取录音权限，是否同意授权，用户的授权状态会回调给这个对象的方法onRequestPermissionsResult。

```plain
public static void requestPermission(@NonNull Activity activity, int requestCode, @NonNull String[] permissions,
    @Nullable PermissionGrantCallback callback) {
    //判断是否授权了
}

```

如果已获得授权一般requestCode是1，permissions里面包含了用户赋予应用的所有权限，可以在这里再判断一下用户是否给予了录音权限，如果确认授权了就可以执行录音操作，如果没有获得权限就可以给用户提示。

当我们取得内存中的PCM数据之后该如何处理呢？

其实在多媒体App中一般会进行声音特效处理，然后把它编码成一个AAC或者MP3文件。至于音频的处理部分这节课我们暂不涉及，音频的编码我们下节课会进行讲解，这里我们就简单地写到一个PCM文件中。在录制结束之后，可以从SD卡中拿出这个PCM文件，然后使用ffplay进行播放来试听效果。接下来我们就先看一下SDK层的AudioRecord采集音频吧。

## AudioRecord采集音频

AudioRecord是Android平台兼容性最好的音频采集方法，熟练地使用它可以为你的App带来最稳定的音频采集能力。使用方法分为四个步骤。

![图片](https://static001.geekbang.org/resource/image/22/a3/229f75c715e3c7e3064d15b9337c0fa3.png?wh=1920x2418)

1. 配置参数，初始化内部的音频缓冲区

我们先来看一下AudioRecord的参数配置，AudioRecord是通过构造函数来进行配置的，构造函数原型如下：

```plain
public AudioRecord(int audioSource, int sampleRateInHz, int channelConfig, int
        audioFormat, int bufferSizeInBytes).

```

我们来看下构造函数中参数代表的含义，以及在各种场景下应该传递的值具体说明。

audioSource参数指定的是音频采集的输入源，可选值以常量的形式定义在类AudioSource（MediaRecorder的一个内部类）中，常用的可选值如下：

- DEFAULT，代表使用默认的麦克风采集。
- CAMCORDER，使用和摄像头同方向的麦克风采集。
- VOICE\_RECOGNITION，一般用于语音识别场景。
- MIC，代表使用手机的主麦克风作为采集的输入源。
- VOICE\_COMMUNICATION，在VOIP场景下如果使用硬件AEC的话，可以设置这个参数。

sampleRateInHz，用来指定采用多大的采样频率来采集音频，现在用得最多的就是44100或者48000的采样频率。因为根据奈奎斯特采样定律，只有这两个采样频率在做AD/DA转换的时候才能还原出20K以上的音频。如果使用这个采样率初始化录音器失败的话，则可以使用16000的采样频率（就是我们经常说的16k的采样率）来兜一下底。

channelConfig，这个参数用来指定录音器采集几个声道的声音，可选值以常量的形式定义在 AudioFormat 类中，常用的值包括：CHANNEL\_IN\_MONO单声道采集和CHANNEL\_IN\_STEREO立体声采集。

由于现在的移动设备都是伪立体声的采集，所以考虑到性能，一般按照单声道进行采集，然后在音频处理阶段转换为立体声效果。当然在某些需要立体声输入的场景（外接声卡输入/USB麦克风），可以设置为立体声。

audioFormat，就是基础概念里我们介绍过的采样表示格式，可选值以常量的形式定义在 AudioFormat 类中，常用的值包括：ENCODING\_PCM\_16BIT，使用16位或者2个字节来表示一个采样点，还有ENCODING\_PCM\_8BIT，代表使用8位或者1个字节来表示一个采样点。前者可以保证兼容大部分的Android手机，一般都采用16BIT。

bufferSizeInBytes，这是最难理解但又很重要的一个参数，用来指定AudioRecord内部音频缓冲区的大小。而具体的大小，不同厂商会有不同的实现，这个音频缓冲区越小，录音的延时就会越小。

AudioRecord 类提供了一个静态方法，帮助开发者来确定这个 bufferSizeInBytes 的函数，原型如下：

```plain
int getMinBufferSize(int sampleRateInHz, int channelConfig, int audioFormat);

```

在实际开发中，一定要通过这个函数计算需要传入的 bufferSizeInBytes。

配置好AudioRecord之后，要检查一下当前AudioRecord的状态，因为有可能会因为权限或者参数的问题，使构造的AudioRecord状态异常。那如何检查录音的状态呢？我们可以通过AudioRecord的方法getState来获取当前状态，然后和AudioRecord.STATE\_INITAILIZED进行比较。如果相等，才可以开启采集，否则应该提示给用户。

2. 开始采集

走到这一阶段，说明已经创建好AudioRecord的实例了，并且状态也是正确的，接下来我们调用startRecording()方法来采集音频。

```plain
audioRecord.startRecording();

```

3. 提取数据

与AudioTrack的使用方法类似，读取音频录音器采集到的音频，需要开发者自己启动一个线程，不断地从 AudioRecord 的缓冲区将音频数据读出来。注意，这个过程一定要及时，否则控制台会打印“overrun”的错误，这个错误在音频开发中比较常见，意味着应用层没有及时地“取走”音频数据，导致内部的音频缓冲区溢出。读取录音器采集到的PCM数据的方法原型如下：

```plain
public int read(byte[] audioData, int offsetInBytes, int sizeInBytes)

```

当然，也可以读取short数组类型的数据，因为这更符合音频采样点的表示，毕竟我们设置的是每个sample都是由两个字节来表示，方法原型如下：

```plain
public int read(short[] audioData, int offsetInShorts, int sizeInShorts)

```

拿到数据之后，就可以通过Java层提供的FileOutputStream直接将数组写到文件中。

4. 停止采集，释放资源

当我们想停止音频采集的时候，需要调用AudioRecord实例的stop方法，并且最终要对这个AudioRecord的实例调用release，来释放这个录音器，以便设备的其他应用可以正常使用录音器。一般通用的写法是通过调用个布尔型变量控制读取数据的线程结束，然后再停止和释放AudioRecord实例。最后还要关闭写入数据的文件，否则会有文件写出不完全的问题。

当拿到一个写出的PCM文件，我们应该如何播放呢？因为PCM文件就是一个二进制文件，如果不知道这个PCM文件的表示格式，是无法播放的。而我们这个PCM文件的表示格式是44100的采样率、单声道、16位表示一个采样点，那么使用ffplay来播放这个PCM文件的命令如下：

```plain
ffplay -f s16le  -sample_rate 44100  -channels 1 -i vocal.pcm

```

而我们常见的WAV文件就是将PCM文件的表示格式放到WAV协议定义的一个头里面，我们也可以利用FFmpeg将PCM文件转换为WAV文件，然后使用PC上的系统播放器进行播放，转换命令行如下：

```plain
ffmpeg -f s16le -sample_rate 44100 -channels 1 -i vocal.pcm -acodec pcm_s16le vocal.wav

```

## Oboe采集音频

关于Oboe的介绍，以及如何集成Oboe到我们的工程中，我们 [第3节课](https://time.geekbang.org/column/article/545000) 使用Oboe来做音频渲染的时候已经讲过，你可以先回顾一下，这里我们就不再重复了。接下来，我们直接看如何使用Oboe采集音频。

![图片](https://static001.geekbang.org/resource/image/50/fa/50e04720a4474104027f198648c5cafa.png?wh=1035x747)

1. 创建AudioStream

和音频的渲染一样，我们通过AudioStreamBuilder来创建Stream，不同点是Direction这里我们要设置成Input，代表我们要创建录音器。

```plain
oboe::AudioStreamBuilder builder;
builder.setPerformanceMode(oboe::PerformanceMode::LowLatency)
  ->setDirection(oboe::Direction::Input)//录制的设置
  ->setSharingMode(oboe::SharingMode::Shared)
  ->setChannelCount(oboe::ChannelCount::Mono)//单声道采集
  ->setFormat(oboe::AudioFormat::I16);//格式采用I16，范围为[-32768, 32767]

```

最终调用openStream来打开Stream，和音频渲染一样，也是根据返回值来判断是否创建成功，如果创建失败了，可以使用convertToText来查看错误码。

```plain
oboe::Result result = builder.openStream(mStream);
if (result != oboe::Result::OK) {
  LOGE("Failed to create stream. Error: %s", convertToText(result));
}

```

2. 录制音频

调用了requestStart方法，当采集到音频之后就会回调设置的Callback函数。

```plain
mStream->requestStart();

```

3. 启动一个线程来读取音频

```plain
oboe::ResultWithValue<int32_t> result = mInputStream->read(mInputBuffer.get(), numFrames, 0);
if (!result) {
    //结束
} else {
    int32_t framesRead = result.value();
    //TODO 写入文件
}

```

在这里读取出一部分数据就可以写入文件了。

4. 当停止录音的时候需要关闭AudioStream

```plain
mStream->requestStop();
mStream->close();

```

到这里，Oboe录制音频的方法我们也就讲完了，最终得到的PCM文件也可以使用ffplay进行播放，使用这个方法来检查一下你录音器是否录制成功了吧。

当然，在一些低性能手机上，写文件还是要在异步线程中去写，否则就会阻碍录制器的录制线程。

## 小结

最后，我们可以一起来回顾一下。

![图片](https://static001.geekbang.org/resource/image/66/77/66b65110b92012b25779f571063fa177.png?wh=1920x1796)

Android平台音频采集的技术选型，在SDK层和NDK层各有两套音频采集方法，考虑到我们的视频录制器的场景，我们选取了SDK层的AudioRecord和Native层的Oboe采集音频的方法。

- AudioRecord采集音频主要分为配置参数，初始化内部音频缓冲区、采集、提取数据，以及停止采集，释放资源四步。
- 使用Oboe录制音频也分为四步，分别是创建Audio Stream、录制、启动线程读取音频、停止录音时关闭Audio Stream。

每一步我都给出了相应的代码示例，相信你跟着我做，也能成功录制音频。通过音频的录制我们已经得到设备采集到的PCM声音了。但是PCM数据是非常大的，比如CD音质的PCM数据一般表示格式为：44100采样率、双声道、每个采样点用16位来表示，那1分钟CD音质的PCM数据大小就是10.09MB。

$$44100\\times16\\times2\\times60\\div8\\div1024=10.09MB$$

这么大的数据要想进行存储及网络传输是不现实的，需要对音频进行压缩编码，下节课我会带着你学习音频编码方面的内容。

## 思考题

在一些K歌的App，比如回森中有一个功能是实时耳返功能，它可以让带有线耳机的用户在演唱歌曲的同时，在耳机中听到自己的声音，要想实现这个功能肯定需要将采集到的音频立马播放出来。而这里面的难点就是低延迟，因为如果延迟高了用户跟着伴奏演唱是非常糟糕的体验。那如果让你来实现这个功能，应该怎么实现呢？欢迎在评论区分享你的思考，也欢迎你把这节课分享给更多对音视频感兴趣的朋友，我们一起交流、共同进步。下节课再见！