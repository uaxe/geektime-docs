你好，我是展晓凯。

前两节课我们一起学习了iOS平台的音频渲染技术，深入地了解了AudioQueue和AudioUnit两个底层的音频框架，了解这些音频框架便于我们做技术选型，可以给我们的应用融入更强大的功能。那除了iOS平台外，Android平台的音视频开发也有着相当大的需求，所以这节课我们一起来学习Android平台的音频渲染技术。

由于Android平台的厂商与定制Rom众多，碎片化特别严重，所以系统地学习音频渲染是非常重要的。这节课我会先从音频渲染的技术选型入手，向你介绍Android系统上渲染音频方法的所有可能性，然后依次讲解常用技术选型的内部原理与使用方法。

## 技术选型及其优缺点

Android系统为开发者在SDK以及NDK层提供了多种音频渲染的方法，每一种渲染方法其实也是为不同的场景而设计的，我们必须要了解每一种方法的最佳实践是什么，这样在开发工作中才能如鱼得水地使用它们。

### SDK层的音频渲染

Android系统在SDK层（Java层提供的API）为开发者提供了3套常用的音频渲染方法，分别是：MediaPlayer、SoundPool和AudioTrack。这三个API的推荐使用场景是不同的。

- MediaPlayer适合在后台长时间播放本地音乐文件或者在线的流式媒体文件，相当于是一个端到端的播放器，可以播放音频也可以播放视频，它的封装层次比较高，使用方式也比较简单。
- SoundPool也是一个端到端的音频播放器，优点是：延时较低，比较适合有交互反馈音的场景，适合播放比较短的音频片段，比如游戏声音、按键声、铃声片段等，它可以同时播放多个音频。
- AudioTrack是直接面向PCM数据的音频渲染API，所以也是一个更加底层的API，提供了非常强大的控制能力，适合低延迟的播放、流媒体的音频渲染等场景，由于是直接面向PCM的数据进行渲染，所以一般情况下需要结合解码器来使用。

### NDK层的音频渲染

Android系统在NDK层（Native层提供的API，即C或者C++层可以调用的API）提供了2套常用的音频渲染方法，分别是OpenSL ES和AAudio，它们都是为Android的低延时场景（实时耳返、RTC、实时反馈交互）而设计的，下面我们一起来看一下。

- OpenSL ES：是Khronos Group开发的 OpenSL ES™ API 规范的实现，专用于 Android低延迟高性能的音频场景，API接口设计会有一些晦涩、复杂，目前Google已经不推荐开发者把OpenSL ES用于新应用的开发了。但是在Android8.0系统以下以及一些碎片化的Android设备上它具有更好的兼容性，所以掌握这种音频渲染方法也是十分重要的。
- AAudio：专门为低延迟、高性能音频应用而设计的，API设计精简，是Google推荐的新应用构建音频的应用接口。掌握这种音频渲染方法，为现有应用中增加这种音频的渲染能力是十分有益的。但是它仅适合Android 8.0及以上版本，并且在一些品牌的特殊Rom版本中适配性不是特别好。

NDK层的这两套音频渲染方法适用于不同的Android版本，可以应用在不同的场景中，因此了解这两种音频渲染的方法对我们的开发工作来说是非常必要的，一会儿我们会再就这两种方法深入展开讨论。

通过上述讲解，想必你已经了解了Android平台上所有的音频渲染的方法，而这里面最通用的渲染PCM的方法就是AudioTrack，那么接下来我们首先从AudioTrack开始讲起。

## AudioTrack

由于AudioTrack是Android SDK层提供的最底层的音频播放API，因此只允许输入PCM裸数据。与MediaPlayer相比，对于一个压缩的音频文件（比如MP3、AAC等文件），它需要开发者自己来实现解码操作和缓冲区控制。由于这节课我们重点关注的是音频渲染的知识，所以这个部分我们只介绍如何使用AudioTrack来渲染音频PCM数据，对于缓冲区的控制机制会在播放器实战部分详细讲一下。

首先让我们一起来看一下AudioTrack的工作流程：

1. 根据音频参数信息，配置出一个AudioTrack的实例。
2. 调用play方法，将AudioTrack切换到播放状态。
3. 启动播放线程，循环向AudioTrack的缓冲区中写入音频数据。
4. 当数据写完或者停止播放的时候，停止播放线程，并且释放所有资源。

根据上述AudioTrack的工作流程，我会给你详细地讲解流程中的每个步骤。

### 第一步：配置AudioTrack

我们先来看一下AudioTrack的参数配置，要想构造出一个AudioTrack类型的实例，得先了解一下它的构造函数原型，如下所示：

```plain
public AudioTrack(int streamType, int sampleRateInHz, int channelConfig,
        int audioFormat, int bufferSizeInBytes, int mode);

```

其中构造函数中的参数说明如下：

- streamType，在Android手机上有多重音频管理策略，比如你按一下手机侧边的按键或者在系统设置中，可以看到有多个类型的音量管理，这其实就是不同音频策略的音量控制展示。当系统有多个进程需要播放音频的时候，管理策略会决定最终的呈现效果，该参数的可选值以常量的形式定义在类AudioManager中，主要包括：

```plain
STREAM_VOCIE_CALL：电话声音
STREAM_SYSTEM：系统声音
STREAM_RING：铃声
STREAM_MUSCI：音乐声
STREAM_ALARM：警告声
STREAM_NOTIFICATION：通知声

```

- sampleRateInHz，采样率，即播放的音频每秒钟会有多少次采样，可选用的采样频率列表为：8000、16000、22050、24000、32000、44100、48000等。采样率越高声音的还原度就越高，普通的语音通话可能16k的采样频率就够了，但是如果高保真的场景，比如：K歌、音乐、短视频、ASMR等，就需要44.1k以上的采样频率，你可以根据自己的应用场景进行合理的选择。
- channelConfig，声道数（通道数）的配置，可选值以常量的形式配置在类AudioFormat中，常用的是CHANNEL\_IN\_MONO（单声道）、CHANNEL\_IN\_STEREO（双声道）。因为现在大多数手机的麦克风都是伪立体声采集，考虑到性能，我建议你使用单声道进行采集，然后在声音处理阶段（比如混响、HRTF等效果器）转变为立体声的效果。
- audioFormat，这个参数是用来配置“数据位宽”的，即采样格式，可选值以常量的形式定义在类AudioFormat中，分别为ENCODING\_PCM\_16BIT（16bit）、ENCODING\_PCM\_8BIT（8bit）。注意，前者是可以保证兼容所有Android手机的，所以我建议你尽量选择前者。
- bufferSizeInBytes，它配置的是 AudioTrack 内部的音频缓冲区的大小，AudioTrack 类提供了一个帮助开发者确定这个 bufferSizeInBytes 的函数，原型如下：

```plain
int getMinBufferSize(int sampleRateInHz, int channelConfig, int audioFormat);

```

在实际开发中，我建议你使用该函数计算出需要传入的bufferSizeInBytes，而不是自己手动计算。

- mode，AudioTrack提供了两种播放模式，可选值以常量的形式定义在类AudioTrack中，一个是 MODE\_STATIC，需要一次性将所有的数据都写入播放缓冲区，简单高效，通常用于播放铃声、系统提醒的音频片段；另一个是 MODE\_STREAM，需要按照一定的时间间隔不间断地写入音频数据，理论上它可用于任何音频播放的场景。在实际开发中，我建议你采用MODE\_STREAM这种播放模式。

讲到这里，我相信你可以根据自己的场景构造出一个AudioTrack实例来了，我们根据上面的工作流程继续进行下一步，接下来就是将AudioTrack切换到播放状态。

### 第二步：将AudioTrack切换到播放状态

其实切换到播放状态是非常简单的，需要先判断AudioTrack实例是否初始化成功，如果当前状态是初始化成功的话，那么就调用它的play方法，切换到播放状态，代码如下：

```plain
if (null != audioTrack && audioTrack.getState() != AudioTrack.STATE_UNINITIALIZED)
{
    audioTrack.play();
}

```

但是在切换为播放状态之后，需要开发者自己启动一个线程，用于向AudioTrack里面送入PCM数据，接下来我们一起来看如何开启播放线程。

### 第三步：开启播放线程

首先创建出一个播放线程，代码如下：

```plain
playerThread = new Thread(new PlayerThread(), "playerThread");
playerThread.start();

```

接着我们来看这个线程中执行的任务，代码如下：

```plain
class PlayerThread implements Runnable {
    private short[] samples;
    public void run() {
        samples = new short[minBufferSize];
        while(!isStop) {
            int actualSize = decoder.readSamples(samples);
            audioTrack.write(samples, actualSize);
        }
    }
}

```

线程中的minBufferSize的计算方式如下：

1. 在初始化AudioTrack的时候获得的缓冲区大小为bufferSizeInBytes；
2. 换算为2个字节表示一个采样的大小，也就是除以2得到这个minBufferSize。

然后代码中的decoder是一个解码器实例，构建这个解码器实例比较简单，在这里我就不详细介绍了。现在我们假设已经构建成功，然后从解码器中拿到PCM采样数据，最后调用write方法写入AudioTrack的缓冲区中。循环往复地不断送入PCM数据，音频就能够持续地播放了。

这里有一点是需要额外注意的，就是这个write方法是阻塞的，比如：一般写入200ms的音频数据需要执行接近200ms的时间，所以这要求在这个线程中不应该做更多额外耗时的操作，比如IO、等锁。

### 第四步：销毁资源

当要停止播放（自动完成或者用户手动停止）的时候，就需要停止播放同时销毁资源，那么就需要首先停掉AudioTrack，代码如下：

```plain
if (null != audioTrack && audioTrack.getState() != AudioTrack.STATE_UNINITIALIZED)
{
    audioTrack.stop();
}

```

然后要停掉我们自己的播放线程：

```plain
isStop = true;
if (null != playerThread) {
    playerThread.join();
    playerThread = null;
}

```

只有当线程停掉之后，才不会再有AudioTrack的使用，最后一步就是释放AudioTrack：

```plain
audioTrack.release();

```

看完了SDK层的音频渲染方法，接下来我们继续看NDK层音频渲染的两种方法，先来介绍OpenSL ES吧！

## OpenSL ES

OpenSL ES全称是Open Sound Library for Embedded Systems，即嵌入式音频加速标准。OpenSL ES是无授权费、跨平台、针对嵌入式系统精心优化的硬件音频加速的框架。它为嵌入式移动多媒体设备上的本地应用程序开发者提供了标准化、高性能、低响应时间的音频功能实现方法，并实现了软/硬件音频性能的直接跨平台部署，降低了执行难度，促进了高级音频市场的发展。

![图片](https://static001.geekbang.org/resource/image/1b/43/1ba3480ff88d7d509782e1bc501fed43.png?wh=1920x1043)

图1描述了OpenSL ES的架构，在Android中，High Level Audio Libs是音频Java层API 输入输出，属于高级API。相对来说，OpenSL ES则是比较低级别的API，属于C语言API。在开发中，一般使用高级API就能完成，除非遇到性能瓶颈，比如低延迟耳返、低延迟声音交互反馈、语音实时聊天等场景，开发者可以直接通过C/C++开发。

### 编译与链接

我们这个专栏里使用的是OpenSL ES 1.0.1版本，因为这个版本是目前比较成熟并且通用的，Android系统2.3版本以上才支持这个版本，并且有一些高级功能，比如解码AAC，是在Andorid系统版本4.0以上才支持的。

在使用OpenSL ES的API之前，我们需要引入OpenSL ES的头文件，如下：

```plain
#include <SLES/OpenSLES.h>
#include <SLES/OpenSLES_Android.h>

```

由于是在Native层使用这个特性，所以要在编译脚本中引入对应的so库：

1. Android.mk这个Makefile文件中增加链接选项，以便在链接阶段使用系统提供的OpenSL ES的so库：

```plain
LOCAL_LDLIBS += -lOpenSLES

```

2. Cmake的情况下，需要在CMakeLists.txt中增加链接选项，以便在链接阶段使用系统提供的OpenSL ES的so库：

```plain
target_link_libraries(audioengine
        OpenSLES
        )

```

### OpenSL ES的对象和接口

我们前面也提到了OpenSL ES提供的是基于C语言的API，设计者为了让开发更简单，所以以面向对象的方式为开发者提供接口，那基于C语言的API是如何设计面向对象的接口的呢？

OpenSL ES提供的是基于对象和接口的方式，采用面向对象的方法提供API接口，所以，我们先来看一下OpenSL ES里面对象和接口的概念。

- 对象：对象是对一组资源及其状态的抽象，每个对象都有一个在其创建时指定的类型，类型决定了对象可以执行的任务集，它类似于C++中类的概念。
- 接口：接口是对象提供的一组特征的抽象，这些抽象会暴露给开发者一组方法和每个接口的类型功能，在代码中，接口的类型由接口ID标识。

我们需要理解的重点是， **一个对象在代码中其实是没有实际的表示形式的，可通过接口来改变对象的状态以及使用对象提供的功能**。对象可以有一个或者多个接口的实例，但是对于接口实例，肯定只属于一个对象。理解了OpenSL ES中对象和接口的概念，我们继续来看代码实例中是如何使用它们的吧！

### OpenSL ES的使用方法

刚刚我们提到，对象是没有实际的代码表示形式的，对象的创建也是通过接口来完成的。通过相应的方法来获取对象，进而可以访问对象的其他接口方法或者改变对象的状态，具体的执行步骤如下：

![](https://static001.geekbang.org/resource/image/f4/2f/f407f66fb5d5cf6e94c2c1811a65a52f.png?wh=2011x236)

1. 创建一个引擎对象接口。引擎对象是OpenSL ES提供API的唯一入口，开发者需要调用全局函数slCreateEngine来获取SLObjectItf类型的引擎对象接口。

```plain
SLObjectItf engineObject;
SLEngineOption engineOptions[] = { { (SLuint32) SL_ENGINEOPTION_THREADSAFE,  (SLuint32) SL_BOOLEAN_TRUE } };
slCreateEngine(&engineObject, ARRAY_LEN(engineOptions), engineOptions, 0, 0, 0);

```

2. 实例化引擎对象，需要通过在上一步得到的引擎对象接口来实例化引擎对象，否则无法使用这个对象，其实在OpenSL ES的使用中，任何对象都需要使用接口来进行实例化，所以我们也封装出一个实例化对象的方法，代码如下：

```plain
RealizeObject(engineObject);
SLresult RealizeObject(SLObjectItf object) {
    return (*object)->Realize(object, SL_BOOLEAN_FALSE);
};

```

3. 获取这个引擎对象的方法接口，通过GetInterface方法，使用上一步已经实例化好的对象，获取对应的SLEngineItf类型的对象接口，这个接口将会是开发者使用所有其他API的入口。

```plain
SLEngineItf engineEngine;
(*engineObject)->GetInterface(engineObject, SL_IID_ENGINE, &engineEngine);

```

4. 创建需要的对象接口，通过调用SLEngineItf类型的对象接口的CreateXXX方法，来返回新的对象的接口，比如调用CreateOutputMix这个方法来获取出一个outputMixObject接口，或者调用CreateAudioPlayer这个方法来获取出一个audioPlayerObject接口，这里我们仅列出创建outputMixObject的接口代码，播放器接口的获取可以参考代码仓库中的代码：

```plain
SLObjectItf outputMixObject;
(*engineEngine)->CreateOutputMix(engineEngine, &outputMixObject, 0, 0, 0);

```

5. 实例化新的对象，任何对象接口获取出来之后，都必须要实例化，其实是和第二步（实例化引擎对象）一样的操作。

```plain
realizeObject(outputMixObject);
realizeObject(audioPlayerObject);

```

6. 对于某一些比较复杂的对象，需要获取新的接口来访问对象的状态或者维护对象的状态，比如在播放器audioPlayer或录音器audioRecorder中注册一些回调方法等，代码如下：

```plain
SLPlayItf audioPlayerPlay;
(*audioPlayerObject)->GetInterface(audioPlayerObject, SL_IID_PLAY,
&audioPlayerPlay);
//设置播放状态
(*audioPlayerPlay)->SetPlayState(audioPlayerPlay, SL_PLAYSTATE_PLAYING);
//设置暂停状态
(*audioPlayerPlay)->SetPlayState(audioPlayerPlay, SL_PLAYSTATE_PAUSED);

```

7. 待使用完毕这个对象之后，要记得调用Destroy方法来销毁对象以及相关的资源。

```plain
destroyObject(audioPlayerObject);
destroyObject(outputMixObject);
void AudioOutput::destroyObject(SLObjectItf& object) {
    if (0 != object)
        (*object)->Destroy(object);
    object = 0;
}

```

相较于其他音频接口（AudioTrack、AAudio），OpenSL ES的使用确实比较麻烦，但是如果你的面向对象思维比较好的话，按照它的套路写起来也会比较快。在后面课程中我们播放器实战的音频渲染部分也会使用OpenSL ES来构造，到时候你可以参考代码实例进行更深入的理解。

## Oboe

学到这里，你是否会有一个疑问呢？就是如果要在NDK层构建一套适配性好同时面向未来的音频渲染框架，势必要将上面介绍的两种方法结合起来，同时也要有一定的策略来选择使用哪一种实现，而从零搭建一套这样的框架会比较复杂，那有没有一些开源的实现来完成这件事情呢？

有，那就是Oboe。

### Oboe介绍

由于AAudio仅适用于Android 8.0系统以上，而OpenSL ES在某些设备上又没有Google给开发者提供的低延迟、高性能的能力，所以Google推出了自己的Oboe框架。Oboe使用和AAudio近乎一致的API接口为开发者封装了底层的实现，自动地根据当前Android系统来选择OpenSL ES还是AAudio，当然也给开发者提供了接口，开发者可以自由地选择底层的实现。由于Oboe的整体API接口以及设计思想与AAudio一致，所以我们这节课直接以Oboe为例来给你详细地讲解一下。

### 集成Oboe到工程里

1. 在gradle文件中增添对Oboe的依赖：

```plain
dependencies {
    implementation 'com.google.oboe:oboe:1.6.1'
}

```

2. 在CMake中增加头文件引用与库的链接：

```plain
# Find the Oboe package
find_package (oboe REQUIRED CONFIG)
# Specify the libraries which our native library is dependent on, including Oboe
target_link_libraries(native-lib log oboe::oboe)

```

3. 业务代码中引入必要的头文件：

```plain
#include <oboe/Oboe.h>

```

至此Oboe就已经集成到工程里了，那我们如何在工程中使用它呢？

### 在工程里使用Oboe

1. 创建AudioStream

- 首先，我们通过AudioStreamBuilder来创建Stream，AudioStreamBuilder是按照Builder设计模式设计的类，可以接连地设置多个参数。在下面的代码块中，我对参数进行了解释：

```plain
oboe::AudioStreamBuilder builder;
builder.setPerformanceMode(oboe::PerformanceMode::LowLatency)
  ->setDirection(oboe::Direction::Output)//播放的设置
  ->setSharingMode(oboe::SharingMode::Exclusive)//独占设备，对应的是Shared
  ->setChannelCount(oboe::ChannelCount::Mono)//单声道
  ->setFormat(oboe::AudioFormat::Float);//格式采用Float，范围为[-1.0，1.0]，还有一种是I16，范围为[-32768, 32767]

```

- 然后设置Callback，定义一个AudioStreamDataCallback的子类，重写onAudioReady方法来实现自己填充数据的逻辑，但这个方法不可以太耗时，否则会出现卡顿，最后基于这个类构建对象设置给Builder。

```plain
class MyCallback : public oboe::AudioStreamDataCallback {
public:
    oboe::DataCallbackResult
    onAudioReady(oboe::AudioStream *audioStream, void *audioData, int32_t numFrames) {
        auto *outputData = static_cast<float *>(audioData);
        const float amplitude = 0.2f;
        for (int i = 0; i < numFrames; ++i){
            outputData[i] = ((float)drand48() - 0.5f) * 2 * amplitude;
        }
        return oboe::DataCallbackResult::Continue;
    }
};

MyCallback myCallback;
builder.setDataCallback(&myCallback);

```

- 最终调用openStream来打开Stream，根据返回值来判断是否创建成功，如果创建失败了，可以使用convertToText来查看错误码。

```plain
oboe::Result result = builder.openStream(mStream);
if (result != oboe::Result::OK) {
  LOGE("Failed to create stream. Error: %s", convertToText(result));
}

```

2. 播放音频

调用了requestStart方法之后，就要在回调函数中填充数据。

```plain
mStream->requestStart();

```

3. 关闭AudioStream

```plain
mStream->close();

```

至此Oboe渲染音频的方法我们就学完了，其实Oboe（AAudio）的接口设计是非常优雅的，开发者在使用的时候也都很得心应手，希望通过这节课的学习你可以在你的应用中加入Oboe的能力，给你的应用赋予Google最新的低延迟、高性能的能力。

## 小结

最后，我们可以一起来回顾一下。

![](https://static001.geekbang.org/resource/image/a9/73/a9c7b54a5bfc724c2fd8bdfyyb8f2473.png?wh=3437x2473)

这节课我们重点学习了使用Java层的AudioTrack和Native层的OpenSL ES以及Oboe来渲染音频的方法。AudioTrack是最通用的渲染PCM的方法，今天我们详细地介绍了它的工作流程；然后我们又聚焦了Native层的OpenSL ES，它在高级音频市场占有非常重要的地位，今天通过代码实例，我们展示了OpenSL ES对象和接口的使用方法，希望你能通过今天的实战，掌握它的使用方法；最后我们学习了Oboe渲染音频的方法，Oboe可以根据当前Android系统选择合适的框架，在整个音频渲染体系中也是十分重要的存在。

其实在Android开发中除了这些底层的音频框架，还有其他的一些常用的上层框架，比如MediaPlayer、SoudPool，我们也做了简单的介绍。在系统地学习这些渲染音频的方法之后，相信你能够根据具体的开发场景，调用合适的音频框架去处理问题了。

## 思考题

如果你想要实现一个音频播放器功能，场景描述如下：

1. 自己构建解码器来解码本地的MP3或者M4A文件；
2. 使用AudioTrack或者Oboe来渲染音频；
3. 可以随时暂停、停止这个播放器的播放。

请你设计出这个案例的整体架构图，同时标记清楚你设计的各个类的职责。欢迎在评论区分享你的思考，也欢迎把这节课分享给更多对音视频感兴趣的朋友，我们一起交流、共同进步。下节课再见！