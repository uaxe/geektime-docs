你好，我是展晓凯。

上节课我们学习了iOS平台的音频框架的第一部分，深入了解了AVAudioSession以及AudioQueue的使用方法，同时也学习了iOS音频格式的表示方法，就是ASBD。其中重点学习了AudioQueue渲染音频的方法。AudioQueue这个API其实是介于AVPlayer/AVAudioPlayer与Audio Unit之间的一个音频渲染框架。如果我们想对音频有更高层次的控制，而AudioQueue满足不了我们的开发需求的时候，我们应该使用哪个音频框架呢？

![图片](https://static001.geekbang.org/resource/image/53/9a/5398e87e2955052a62f9dc5accc1b89a.png?wh=1744x704)

没错，就是AudioUnit。作为iOS最底层的音频框架，AudioUnit是音视频开发者必须要掌握的内容。我们在开发音频相关产品的时候，如果对音频有更高程度的控制、性能以及灵活性需求，或者想使用一些特殊功能（比如回声消除、实时耳返）的时候，就可以直接使用AudioUnit这一层的API，这些接口是面向C语言的。

随着iOS的API不断升级，AudioUnit还逐渐演变出了AUGraph与AVAudioEngine框架，它们可以为你的App融入更强大的音频多媒体能力。

正如苹果官方文档中描述的，AudioUnit提供了快速的音频模块化处理功能，如果是在以下场景中，更适合使用AudioUnit，而不是高层次的音频框架。

- 在VOIP的应用场景下，想使用低延迟的音频I/O；
- 合成多路声音并且回放，比如游戏或者音乐合成器（弹唱、多轨乐器）的应用；
- 使用AudioUnit里特有的功能，比如：均衡器、压缩器、混响器等效果器，以及回声消除、Mix两轨音频等；
- 需要图状结构来处理音频时，可以使用iOS提供的AUGraph和AVAudioEngine的API接口，把音频处理模块组装到灵活的图状结构中。

既然AudioUnit这么强大，我们该怎么好好利用它呢？不要急，接下来我们就一起来看一下AudioUnit的使用方法。

## AudioUnit

这部分我会从分类、创建、参数设置、构建处理框架四个方面来讲解，我们先看AudioUnit分为哪几类。

### AudioUnit的分类

iOS根据AudioUnit的功能不同，将AudioUnit分成了5大类，了解AudioUnit的分类对于音频渲染和处理是非常重要的。这里我们会从全局视角来认识一下每个大类型（Type）以及大类型下面的子类型（SubType），并且还会介绍每个大类型下面子类型AudioUnit的用途，以及对应参数的意义。

1. **Effect Unit**

第一个大类型是kAudioUnitType\_Effect，主要提供声音特效处理的功能。子类型及用途如下：

- 均衡效果器：子类型是kAudioUnitSubType\_NBandEQ，主要作用是给声音的某一些频带增强或者减弱能量，这个效果器需要指定多个频带，然后为每个频带设置宽度以及增益，最终将改变声音在频域上的能量分布。
- 压缩效果器：子类型是kAudioUnitSubType\_DynamicsProcessor，主要作用是当声音较小的时候可以提高声音的能量，当声音能量超过了设置的阈值，可以降低声音的能量，当然我们要设置合适的作用时间和释放时间以及触发值，最终可以将声音在时域上的能量压缩到一定范围之内。
- 混响效果器：子类型是kAudioUnitSubType\_Reverb2，是对人声处理非常重要的效果器，可以想象我们在一个空房子中，有非常多的反射声和原始声音叠加在一起，可能从听感上会更有震撼力，但是同时也会使原始声音更加模糊，遮盖掉原始声音的一些细节，所以混响设置得大或小对不同的人来讲非常不一致，可以根据自己的喜好来设置。

Effect Unit下最常使用的就是这三种效果器，当然这个大类型下面还有很多种子类型的效果器，像高通（High Pass）、低通（Low Pass）、带通（Band Pass）、延迟（Delay）、压限（Limiter）等效果器，你可以自己使用一下，感受一下效果。

2. **Mixer Units**

第二个大类型是kAudioUnitType\_Mixer，主要提供Mix多路声音的功能。子类型及用途如下。

- 3D Mixer：这个效果器在移动设备上无法使用，只能在OS X上使用，所以这里不介绍了。
- MultiChannelMixer：子类型是kAudioUnitSubType\_MultiChannelMixer，这个效果器是我们重点介绍的对象， **它是多路声音混音的效果器，可以接收多路音频的输入，还可以分别调整每一路音频的增益与开关，并将多路音频合并成一路**，这个效果器在处理音频的图状结构中非常有用。

3. **I/O Units**

第三个大类型是kAudioUnitType\_Output，它的用途就像它分类的名字一样，主要提供的就是I/O功能。子类型及用途如下：

- RemoteIO：子类型是kAudioUnitSubType\_RemoteIO，从名字上也可以看出，这是用来采集音频与播放音频的，当开发者在应用场景中要使用麦克风及扬声器的时候，都会用到这个AudioUnit。
- Generic Output：子类型是kAudioUnitSubType\_GenericOutput，当开发者需要离线处理，或者说在AUGraph中不使用Speaker（扬声器）来驱动整个数据流，而是希望使用一个输出（可以放入内存队列或者进行磁盘I/O操作）来驱动数据流的话，就使用这个子类型。

4. **Format Converter Units**

第四个大类型是kAudioUnitType\_FormatConverter，提供格式转换的功能，比如：采样格式由Float到SInt16的转换、交错和平铺的格式转换、单双声道的转换等，子类型及用途说明如下。

- AUConverter：子类型是kAudioUnitSubType\_AUConverter，这是我们要重点介绍的格式转换效果器，某些效果器对输入的音频格式有明确要求，比如3D Mixer Unit就必须使用UInt16格式的sample，或者开发者将音频数据后续交给一些其他编码器处理，又或者开发者想使用SInt16格式的PCM裸数据进行其他CPU上音频算法计算等场景下，就需要用到这个ConverterNode。

比较典型的场景是我们自定义的一个音频播放器，由FFmpeg解码出来的PCM数据是SInt16格式表示的，我们不可以直接让RemoteIO Unit播放，而是需要构建一个ConvertNode，将SInt16格式表示的数据转换为Float32表示的数据，然后再给到RemoteIO Unit，最终才能正常播放出来。

- Time Pitch：子类型是kAudioUnitSubType\_NewTimePitch，即变速变调效果器，这是一个比较意思的效果器，可以对声音的音高、速度进行更改，像Tom猫这样的应用场景就可以使用这个效果器来实现。

5. **Generator Units**

第五个大类型是kAudioUnitType\_Generator，在开发中我们经常用它来提供播放器的功能。子类型及用途说明如下。

- AudioFilePlayer：子类型是kAudioUnitSubType\_AudioFilePlayer，在AudioUnit里面，如果我们的输入不是麦克风，而是一个媒体文件，要怎么办呢？当然也可以自己进行解码，通过转换之后给RemoteIO Unit播放出来。但其实还有一种更加简单、方便的方式，那就是使用AudioFilePlayer这个AudioUnit，其实数据源还是会调用AudioFile里面的解码功能，将媒体文件中的压缩数据解压成为PCM裸数据，最终再交给AudioFilePlayer Unit进行后续处理。

这里需要注意， **我们必须在AUGraph初始化了之后，再去配置AudioFilePlayer的数据源以及播放范围等属性，否则会出现错误。**

### 创建AudioUnit

构建AudioUnit时，需要指定类型（Type）、子类型（Subtype）以及厂商（Manufacture）。

类型就是刚刚我们讲到的几个大类型；而子类型是这个大类型下面的小类型，比如Effect这个大类型下面有EQ、Compressor、limiter等子类型；厂商一般情况下比较固定，直接写成kAudioUnitManufacturer\_Apple就好了。

利用以上这三个变量，开发者就可以完整描述出一个AudioUnit了，我们使用下面的代码创建一个RemoteIO类型的AudioUnit的描述。

```plain
AudioComponentDescription ioUnitDescription;
ioUnitDescription.componentType = kAudioUnitType_Output;
ioUnitDescription.componentSubType = kAudioUnitSubType_RemoteIO;
ioUnitDescription.componentManufacturer=kAudioUnitManufacturer_Apple;
ioUnitDescription.componentFlags = 0;
ioUnitDescription.componentFlagsMask = 0;

```

上述代码构造了RemoteIO这个AudioUnit描述的结构体，那如何再使用这个描述来构造真正的AudioUnit呢？有两种方式：第一种方式是直接使用AudioUnit裸的创建方式；第二种方式则是使用AUGraph和AUNode（其实一个AUNode就是对AudioUnit的封装，可以理解为一个AudioUnit的Wrapper）方式来构建。下面我来介绍一下这两种方式。

1. **裸创建方式**

首先根据AudioUnit描述，找出实际的AudioUnit类型：

```plain
AudioComponent ioUnitRef = AudioComponentFindNext(NULL, &ioUnitDescription);

```

然后声明一个AudioUnit引用：

```plain
AudioUnit ioUnitInstance;

```

最后根据类型创建出这个AudioUnit实例：

```plain
AudioComponentInstanceNew(ioUnitRef, &ioUnitInstance);

```

2. **AUGraph创建方式**

首先声明并且实例化一个AUGraph：

```plain
AUGraph processingGraph;
NewAUGraph(&processingGraph);

```

然后利用AudioUnit的描述在AUGraph中按照描述增加一个AUNode：

```plain
AUNode ioNode;
AUGraphAddNode(processingGraph, &ioUnitDescription, &ioNode);

```

接下来打开AUGraph，其实打开AUGraph的过程也是间接实例化AUGraph中所有的AUNode的过程。 **注意，必须在获取AudioUnit之前打开整个Graph**，否则我们不能从对应的AUNode里面获取到正确的AudioUnit。

```plain
AUGraphOpen(processingGraph);

```

最后在AUGraph中的某个Node里面获得AudioUnit的引用：

```plain
AudioUnit ioUnit;
AUGraphNodeInfo(processingGraph, ioNode, NULL, &ioUnit);

```

无论使用上面的哪一种方式，都可以创建出我们想要的AudioUnit，而具体应该使用哪一种方式，其实还是应该根据实际的应用场景来决定。结合我的实际工作经验，我认为 **使用AUGraph的结构可以在我们的应用中搭建出扩展性更高的系统**，所以我推荐你使用第二种方式，我们整个音频处理系统就是使用的第二种方式来搭建的。

### RemoteIO详解

AudioUnit创建好之后，就应该对其进行配置和使用了，因为我们后面的播放器项目会用到RemoteIO Unit，所以在这里我就以RemoteIO这个AudioUnit为例，详细讲解AudioUnit的使用。

RemoteIO这个AudioUnit是与硬件IO相关的一个Unit，它可以控制硬件设备的输入和输出（I代表Input，O代表Output）。输入端是麦克风（机身麦克风或者蓝牙耳机麦克风），输出端的话可能是扬声器（Speaker）或者耳机。如果要同时使用输入输出，即K歌应用中的耳返功能（用户在唱歌或者说话的同时，耳机中会将麦克风收录的声音播放出来，让用户自己能听到自己的声音），需要开发者将它们连接起来。

![图片](https://static001.geekbang.org/resource/image/16/1c/16287030b548e0600f7e5fcd4d611f1c.jpg?wh=1920x1063)

如图所示，RemoteIO Unit分为Element0和Element1，其中Element0控制输出端，Element1控制输入端，同时每个Element又分为Input Scope和Output Scope。如果开发者想要使用扬声器的播放声音功能，那么必须将这个Unit的Element0的OutputScope和Speaker进行连接。而如果开发者想要使用麦克风的录音功能，那么必须将这个Unit的Element1的InputScope和麦克风进行连接。使用扬声器的代码如下：

```plain
OSStatus status = noErr;
UInt32 oneFlag = 1;
UInt32 busZero = 0;//Element 0
status = AudioUnitSetProperty(remoteIOUnit,
        kAudioOutputUnitProperty_EnableIO,
        kAudioUnitScope_Output,
        busZero,
        &oneFlag,
        sizeof(oneFlag));
CheckStatus(status, @"Could not Connect To Speaker", YES);

```

上面这段代码就是把RemoteIO Unit中Element0的OutputScope连接到Speaker上，连接过程会返回一个OSStatus类型的值，可以使用自定义的CheckError函数来判断错误并且打印Could not Connect To Speaker提示。具体的CheckError函数如下：

```plain
static void CheckStatus(OSStatus status, NSString *message, BOOL fatal)
{
    if(status != noErr)
    {
        char fourCC[16];
        *(UInt32 *)fourCC = CFSwapInt32HostToBig(status);
        fourCC[4] = '\0';
        if(isprint(fourCC[0]) && isprint(fourCC[1]) && isprint(fourCC[2]) &&
isprint(fourCC[3]))
            NSLog(@"%@: %s", message, fourCC);
        else
            NSLog(@"%@: %d", message, (int)status);
        if(fatal)
            exit(-1);
    }

```

连接成功之后，就应该给AudioUnit设置数据格式（ASBD）了，ASBD我们在前面已经详细讲过了，这里不再赘述。构造好合适的ASBD结构体，最终设置给AudioUnit对应的Scope（Input/Output），代码如下：

```plain
AudioUnitSetProperty( remoteIOUnit,kAudioUnitProperty_StreamFormat,
kAudioUnitScope_Output, 1, &asbd, sizeof(asbd));

```

播放了解清楚了，那么接下来我们一起看下如何控制输入，我们通过一个实际的场景来学习这部分的内容。在K歌应用的场景中，会采集到用户的人声处理之后且立即给用户一个耳返（将声音在50ms之内输出到耳机中，让用户可以听到），那么如何让RemoteIO Unit利用麦克风采集出来的声音，经过中间效果器处理，最终输出到Speaker中播放给用户呢？

这里我来介绍一下，如何以AUGraph的方式将声音采集、处理以及声音输出的整个过程管理起来。

![图片](https://static001.geekbang.org/resource/image/f4/d9/f435eb739f6eec3039e6ebbe1180afd9.jpg?wh=1920x1096)

如上图所示，首先要知道数据可以从通道中传递是由最右端Speaker（RemoteIO Unit）来驱动的，它会向它的前一级AUNode去要数据（图中序号1），然后它的前一级会继续向上一级节点要数据（图中序号2），最终会从我们的RemoteIO Unit的Element1（即麦克风）中取得数据，这样就可以将数据按照相反的方向一级一级地传递下去（图中序号4、5），最终传递到RemoteIOUnit的Element0（即Speaker，图中序号6）就可以让用户听到了。

当然这时候你可能会想离线处理的时候是不能播放出来的，那么应该由谁来进行驱动呢？其实在离线处理的时候，应该使用Mixer Unit这个大类型下面的子类型为Generic Output的AudioUnit来做驱动端。那么这些AudioUnit或者说AUNode是如何进行连接的呢？有两种方式，第一种方式是直接将AUNode连接起来；第二种方式是通过回调把两个AUNode连接起来。下面我们分别来介绍下这两种方式。

1. **直接连接的方式**

```plain
AUGraphConnectNodeInput(mPlayerGraph, mPlayerNode, 0, mPlayerIONode, 0);

```

这段代码是把Audio File Player Unit和RemoteIO Unit连接起来了，当RemoteIO Unit需要播放的数据的时候，就会调用AudioFilePlayer Unit来获取数据，最终数据会传递到RemoteIO中播放出来。

2. **回调的方式**

```plain
AURenderCallbackStruct renderProc;
renderProc.inputProc = &inputAvailableCallback;
renderProc.inputProcRefCon = (__bridge void *)self;
AUGraphSetNodeInputCallback(mGraph, ioNode, 0, &finalRenderProc);

```

这段代码首先构造了一个AURenderCallback的结构体，结构体中需要指定一个回调函数，然后设置给RemoteIO Unit，当这个RemoteIO Unit需要数据输入的时候就会回调这个回调函数，而回调函数的实现如下：

```plain
static OSStatus renderCallback(void *inRefCon, AudioUnitRenderActionFlags
        *ioActionFlags, const AudioTimeStamp *inTimeStamp, UInt32
        inBusNumber, UInt32 inNumberFrames, AudioBufferList *ioData)
{
    OSStatus result = noErr;
    __unsafe_unretained AUGraphRecorder *THIS = (__bridge
            AUGraphRecorder *)inRefCon;
    AudioUnitRender(THIS->mixerUnit, ioActionFlags, inTimeStamp, 0,
            inNumberFrames, ioData);
    return result;
}

```

这个回调函数中主要做两件事情，第一件事情是去Mixer Unit里面要数据，通过调用AudioUnitRender的方式来驱动Mixer Unit获取数据，得到数据之后放入ioData中，这也就填充了回调方法中的数据，从而实现了Mixer Unit和RemoteIO Unit的连接。

如果要播放一个音频文件，就自己构造一套AUGraph是十分不方便的，但我们这样做实际有两个目的： **其一是为了让你体验在开发iOS平台的程序时，优先使用iOS平台自身提供的API的便捷性与重要性；其二是为了给后续的视频播放器项目打下基础。** 你可以好好学习一下这两个实例，充分感受iOS平台为开发者提供的强大的多媒体开发API。

## 小结

最后，我们可以一起来回顾一下。

这节课我们重点学习了使用AudioUnit来渲染音频的方法。其实在iOS开发中除了这些底层的音频框架，还有一些常用的上层框架，了解这些框架的特点与适用场景能够帮助我们做技术选型，接下来我们一起简单看下iOS为开发者提供的各个层次的音频播放框架，以便以后在你的应用中做技术选型：

- AVAudioPlayer：如果你要直接播放一个本地音频文件（无论是本地路径还是内存中的数据），使用AVAudioPlayer会是最佳选择；
- AVPlayer：如果是普通网络协议（HTTP、HLS）音频文件要直接播放，使用AVPlayer会是最佳选择；
- AudioQueue：但是如果你的输入是PCM（比如视频播放器场景、RTC等需要业务自己Mix或者处理PCM的场景），其实使用AudioQueue是适合的一种方式；
- AudioUnit：如果需要构造一个复杂的低延迟采集、播放、处理的音频系统，那么使用AudioUnit（实际实现可能是使用AUGraph或者AVAudioEngine框架）会是最佳选择。

**真正好的架构师应该像裁缝一样懂得量体裁衣**，要了解清楚当前应用场景的现状和未来，然后根据自己的经验做出合理的技术选型，让开发的App可以快速、高质量地上线并且还有一定的扩展性，所以接下来的挑战就看你的了。

## 思考题

如果你想要实现一个K歌录制的功能，场景描述如下：

1. 播放伴奏的同时，可以将人声进行录音；
2. 可以实时听到用户自己的人声耳返，并且要在耳返中加入混响效果器；
3. 可以调节伴奏与人声的音量；

请你思考一下，使用AUGraph如何构造出你的图状结构。欢迎在评论区分享你的思考，也欢迎把这节课分享给更多对音视频感兴趣的朋友，我们共同交流、共同进步。我们下节课再见！