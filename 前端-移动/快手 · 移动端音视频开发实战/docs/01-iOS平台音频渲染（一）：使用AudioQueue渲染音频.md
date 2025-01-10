你好，我是展晓凯。

记得在开篇的时候我说过，我们最后的目标之一就是要实现一个视频播放器项目。而想要实现这个项目，需要我们先掌握音频渲染、视频渲染以及音视频同步等知识。所以今天我们就来迈出第一步——音频的渲染。

音频渲染相关的技术框架比较多，平台不同，需要用到的技术框架也不同。这节课我们就先来看一下iOS平台都有哪些音频框架可供我们选择，以及怎么在iOS平台做音频渲染。

我们先看一下图1，iOS平台的音频框架，里面比较高层次的音频框架有Media Player、AV Foundation、OpenAL和Audio Toolbox（AudioQueue），这些框架都封装了AudioUnit，然后提供了更高层次的、功能更精简、职责更加单一的API接口。这里你先简单地了解一下这些音频框架之间的关系，以及AudioUnit在整个音频体系中的作用，下节课我会给你详细地讲解AudioUnit框架。

![](https://static001.geekbang.org/resource/image/42/7f/429c932f1b5fed302fa262bff76yy87f.png?wh=1744x704)

如果我们想要低开销地实现录制或播放音频的功能，就需要用到iOS音频框架中一个非常重要的接口—— **AudioQueue**， **它是实现录制与播放功能最简单的API接口**，作为开发者的我们无需知道太多内部细节，就可以简单地完成播放PCM数据的功能，可以说是非常方便了。

在实际学习AudioQueue框架之前，我会先把AudioSession给你讲清楚，因为AudioSession是我们与系统对话的重要窗口，它能够向系统描述应用需要的音频能力，所以需要在学会使用AudioSession基础上，再去学习具体的框架。

## AVAudioSession

在iOS的音视频开发中，使用具体API之前都会先创建一个会话，而音频这里的会话就是AVAudioSession， **它以单例的形式存在，用于管理与获取iOS设备音频的硬件信息**。我们可以使用以下代码来获取AudioSession的实例：

```plain
AVAudioSession *audioSession = [AVAudioSession sharedInstance];

```

### 基本设置

获得AudioSession实例之后，就可以设置以何种方式使用音频硬件做哪些处理了，基本的设置如下所示：

1. 根据我们需要硬件设备提供的能力来设置类别：

```plain
[audioSession setCategory:AVAudioSessionCategoryPlayback error:&error];

```

2. 设置I/O的Buffer，Buffer越小说明延迟越低：

```plain
NSTimeInterval bufferDuration = 0.002;
[audioSession setPreferredIOBufferDuration:bufferDuration error:&error];

```

3. 设置采样频率，让硬件设备按照设置的采样率来采集或者播放音频：

```plain
double hwSampleRate = 44100.0;
[audioSession setPreferredSampleRate:hwSampleRate error:&error];

```

4. 当设置完毕所有参数之后就可以激活AudioSession了，代码如下：

```plain
[audioSession setActive:YES error:&error];

```

经过上述几个简单的调用，我们就完成了对AVAudioSession的设置。当我们使用具体API的时候，系统就会按照上述设置的参数进行播放或者回调给开发者进行处理。

### 深入理解AudioSession

除了上述基本的设置之外，我们再从以下几个层面深入理解一下AudioSession，在AVAudioSession设置Category的时候是有很多细节的，分别是Category和CategoryOptions，在某些场景下，它可能会产生奇效。

1. Category是向系统描述应用需要的能力，常用的分类如下：

- AVAudioSessionCategoryPlayback：用于播放录制音乐或者其它声音的类别，如要在应用程序转换到后台时继续播放（锁屏情况下），在xcode中设置 UIBackgroundModes 即可。默认情况下，使用此类别意味着，应用的音频不可混合，激活音频会话将中断其它不可混合的音频会话。如要使用混音，则使用AVAudioSessionCategoryOptionMixWithOthers。
- AVAudioSessionCategoryPlayAndRecord : 同时需要录音（输入）和播放（输出）音频的类别，例如K歌、RTC场景。注意：用户必须打开音频录制权限（iPhone 麦克风权限）。

2. CategoryOptions是向系统设置类别的可选项，具体分类如下：

- AVAudioSessionCategoryOptionDefaultToSpeaker：此选项只能在使用PlayAndRecord类别时设置。它用于保证在没有使用其他配件（如耳机）的情况下，音频始终会路由至扬声器而不是听筒。而如果类别设置的是Playback，系统会自动使用Speaker进行输出，无需进行此项设置。
- AVAudioSessionCategoryOptionAllowBluetooth：此选项代表音频录入和输出全部走蓝牙设备，仅可以为PlayAndRecord还有Record这两个类别设置这个选项，注意此时播放和录制的声音音质均为通话音质（16kHz），适用于RTC的通话场景，但不适用于K歌等需要高音质采集与播放的场景。
- AVAudioSessionCategoryOptionAllowBluetoothA2DP：此选项代表音频可以输出到高音质（立体声、仅支持音频输出不支持音频录入）的蓝牙设备中。如果使用Playback类别，系统将自动使用这个A2DP选项，如果使用PlayAndRecord类别，需要开发者自己手动设置这个选项，音频采集将使用机身内置麦克风（在需要高音质输出和输入的场景下可以设置成这种）。

3. 监听音频焦点抢占，一般在检测到音频被打断的时候处理一些自己业务上的操作，比如暂停播放音频等，代码如下：

```plain
[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(audioSessionInterruptionNoti:) name:AVAudioSessionInterruptionNotification object:[AVAudioSession sharedInstance]];

- (void)audioSessionInterruptionNoti:(NSNotification *)noti {
AVAudioSessionInterruptionType type = [noti.userInfo[AVAudioSessionInterruptionTypeKey] intValue];
if (type == AVAudioSessionInterruptionTypeBegan) {
//Do Something
}
}

```

4. 监听声音硬件路由变化，当检测到插拔耳机或者接入蓝牙设备的时候，业务需要做一些自己的操作，代码如下：

```plain
[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(audioRouteChangeListenerCallback:) name:AVAudioSessionRouteChangeNotification object:nil];

- (void)audioRouteChangeListenerCallback:(NSNotification*)notification {
NSDictionary *interuptionDict = notification.userInfo;
NSInteger routeChangeReason = [[interuptionDict valueForKey:AVAudioSessionRouteChangeReasonKey] integerValue];
if (routeChangeReason==AVAudioSessionRouteChangeReasonNewDeviceAvailable || routeChangeReason == AVAudioSessionRouteChangeReasonOldDeviceUnavailable || routeChangeReason == AVAudioSessionRouteChangeReasonWakeFromSleep ) {
//Do Something
} else if (
routeChangeReason == AVAudioSessionRouteChangeReasonCategoryChange ||
routeChangeReason == AVAudioSessionRouteChangeReasonOverride) {
//Do Something
}
}

```

5. 申请录音权限，首先判断授权状态，如果没有询问过，就询问用户授权，如果拒绝了就引导用户进入设置页面手动打开，代码如下：

```plain
AVAuthorizationStatus status = [AVCaptureDevice authorizationStatusForMediaType:AVMediaTypeAudio];
    if (status == AVAuthorizationStatusNotDetermined) {
        [[AVAudioSession sharedInstance] requestRecordPermission:^(BOOL granted) {
            //granted代表是否授权
        }];
    } else if (status == AVAuthorizationStatusRestricted || status == AVAuthorizationStatusDenied) {// 未授权
        //引导用户跳入设置页面
    } else {
        // 已授权
    }

```

**注意：从iOS 10开始，所有访问任何设备麦克风的应用都必须静态声明其意图。** 为此，应用程序现在必须在其Info.plist文件中包含NSMicrophoneUsageDescription键，并为此密钥提供目的字符串。当系统提示用户允许访问时，这个字符串将显示为警报的一部分。如果应用程序尝试访问任何设备的麦克风而没有此键和值，则应用程序将终止。

现在，音频渲染第一步——会话创建就完成了，接下来就可以进入音频渲染框架的学习了，我们就先来看AudioQueue渲染音频的部分。

## AudioQueue详解

iOS为开发者在AudioToolbox这个framework中提供了一个名为AudioQueueRef的类，AudioQueue内部会完成以下职责：

- 连接音频的硬件进行录音或者播放；
- 管理内存；
- 根据开发者配置的格式，调用编解码器进行音频格式转换。

接下来让我们一起看一下AudioQueue播放音频的结构图：

![图片](https://static001.geekbang.org/resource/image/5a/cd/5a73413d808694e8db31c6109681d2cd.jpg?wh=1920x645)

AudioQueue暴露给开发者的接口如下：

- 使用正确的音频格式、回调方法等参数，创建出AudioQueueRef对象；
- 为AudioQueueRef分配Buffer，并将Buffer入队，启动AudioQueue；
- 在AudioQueueRef的回调中填充指定格式的音频数据，并且重新入队；
- 暂停、恢复等常规接口。

了解了AudioQueue的内部职责和暴露给开发者的接口之后，就让我们一起看一下AudioQueue的运行流程吧！

### AudioQueue运行流程

AudioQueue的整体运行流程分为启动和运行阶段，启动阶段主要是应用程序配置和启动AudioQueue；运行阶段主要是AudioQueue开始播放之后回调给应用程序填充buffer，并重新入队，3个buffer周而复始地运行起来；直到应用程序调用AudioQueue的Pause或者Stop等接口。下图是一个详细的运行流程：

![图片](https://static001.geekbang.org/resource/image/8d/c1/8d23534dddf478fc7b89ce8e2d2023c1.jpg?wh=1920x2543)

#### 启动阶段

1. 配置AudioQueue：

```plain
AudioQueueNewInput(&dataformat, playCallback, (__bridge void *)self, NULL, NULL, 0, &queueRef);

```

dataformat就是音频格式，后面我们会重点讲解，playCallback是当AudioQueue需要我们填充数据时的回调方法，函数返回值为OSStatus类型，如果为noErr则说明配置成功。

2. 分配3个Buffer，并且依次灌到AudioQueue中：

```plain
for (int i = 0; i < kNumberBuffers; i++) {
  AudioQueueAllocateBuffer(queueRef, bufferBytesSize, &buffers[i]);
  AudioQueueEnqueueBuffer(queueRef, buffers[i], 0, NULL);
}

```

Buffer类型为AudioQueueBufferRef，是AudioQueue对外提供的数据封装，具体每个Buffer的大小是如何决定的，我会在后面与dataformat一起讲解。

3. 调用Play方法进行播放：

```plain
AudioQueueStart(queueRef, NULL)

```

#### 运行阶段

启动完毕后，接下来就到运行阶段了，运行阶段主要分为4步：

1. AudioQueue启动之后会播放第一个buffer；
2. 当播放完第一个buffer之后，会继续播放第二个buffer，但是与此同时将第一个buffer回调给业务层由开发者进行填充，填充完毕重新入队；
3. 第二个buffer播放完毕后，会继续播放第三个buffer，与此同时会将第二个buffer回调给业务层由开发者进行填充，填充完毕重新入队；
4. 第三个buffer播放完毕后，会继续循环播放队列中的第一个buffer，也会将第三个buffer回调给业务层由开发者进行填充，填充完毕重新入队。

```plain
static void playCallback(void *aqData, AudioQueueRef inAQ, AudioQueueBufferRef inBuffer) {
  KSAudioPlayer *player = (__bridge KSAudioPlayer *)aqData;
  //TODO: Fill Data
  AudioQueueEnqueueBuffer(player->queueRef, inBuffer, numPackets, player.mPacketDescs);
}

```

这样一来，整个AudioQueue的运行流程就讲解完了，还记得我们在前面说过AudioQueue内部会进行调用编解码器进行音频格式转换吗？接下来我们就详细介绍一下AudioQueue中的Codec运行流程。

### AudioQueue中Codec运行流程

值得一提的是，AudioQueue的强大之处在于 **开发者可以不用关心播放的数据的编解码格式，它内部会帮助开发者将Codec的事情做好**，所以这部分的流程我们是有必要单拎出来看一下的。

![图片](https://static001.geekbang.org/resource/image/58/23/58bb49c9c742bd6955fb5a21aafe6e23.jpg?wh=1920x967)

如图所示，主要分为3个步骤：

1. 开发者配置AudioQueue的时候告诉AudioQueue具体编码格式；
2. 开发者在回调函数中按照原始格式填充buffer；
3. AudioQueue会自己采用合适的Codec将压缩数据解码成PCM进行播放。

介绍完Codec相关的流程，你可能还有一个疑问，就是数据格式以及音频数据到底应该如何设置以及填充呢？这个其实就是之前我们说要重点讲解的音频格式（dataformat），接下来我们就一起来学习一下吧！

### iOS平台的音频格式

iOS平台的音频格式是ASBD（AudioStreamBasicDescription），用来描述音频数据的表示方式，结构体如下：

```plain
struct AudioStreamBasicDescription
{
    AudioFormatID       mFormatID;
    Float64             mSampleRate;
    UInt32              mChannelsPerFrame;
    UInt32              mFramesPerPacket;
    AudioFormatFlags    mFormatFlags;
    UInt32              mBytesPerPacket;
    UInt32              mBytesPerFrame;
    UInt32              mBitsPerChannel;
    UInt32              mReserved;
};
typedef struct AudioStreamBasicDescription  AudioStreamBasicDescription;

```

针对结构体中每个字段，我们需要配上一个实际的案例来逐个讲解一下，先看下面这个格式的配置：

```plain
UInt32 bytesPerSample = sizeof(Float32);
AudioStreamBasicDescription asbd;
bzero(&asbd, sizeof(asbd));
asbd.mFormatID = kAudioFormatLinearPCM;
asbd.mSampleRate = _sampleRate;
asbd.mChannelsPerFrame = channels;
asbd.mFramesPerPacket = 1;
asbd.mFormatFlags = kAudioFormatFlagsNativeFloatPacked | kAudioFormatFlagIsNonInterleaved;
asbd.mBitsPerChannel = 8 * bytesPerSample;
asbd.mBytesPerFrame = bytesPerSample;
asbd.mBytesPerPacket = bytesPerSample;

```

- mFormatID这个参数是用来指定音频的编码格式，此处音频编码格式指定为PCM格式；
- 接下来设置声音的采样率、声道数以及每个Packet有几个Frame这三个参数；
- mFormatFlags是用来描述声音表示格式的参数，代码中的第一个参数指定每个sample的表示格式是Float格式。这个类似于我们之前讲解的每个sample使用两个字节（SInt16）来表示；然后是后面的参数NonInterleaved，表面理解这个单词的意思是非交错的，其实对音频来说，就是左右声道是非交错存放的，实际的音频数据会存储在一个AudioBufferList结构中的变量mBuffers中。 **如果mFormatFlags指定的是NonInterleaved，那么左声道就会在mBuffers\[0\]里面，右声道就会在mBuffers\[1\]里面，而如果mFormatFlags指定的是Interleaved的话，那么左右声道就会交错排列在mBuffers\[0\]里面，** 理解这一点对后续的开发是十分重要的；
- 接下来的mBitsPerChannel表示的是一个声道的音频数据用多少位来表示，前面我们已经知道每个采样使用Float来表示，所以这里就使用8乘以每个采样的字节数来赋值；
- 最后是参数mBytesPerFrame和mBytesPerPacket的赋值，这里需要根据mFormatFlags的值来分配。如果在NonInterleaved的情况下，就赋值为bytesPerSample（因为左右声道是分开存放的）；但如果是Interleaved的话，那么就应该是bytesPerSample \* channels（因为左右声道是交错存放的），这样才能表示一个Frame里面到底有多少个byte。

如果要播放的是一个MP3或者M4A的文件，这个ASBD应该如何确定呢？请看下面这个代码：

```plain
// 打开文件
NSURL *fileURL = [NSURL URLWithString:filePath];
OSStatus status = AudioFileOpenURL((__bridge CFURLRef)fileURL, kAudioFileReadPermission, kAudioFileCAFType, &_mAudioFile);
if (status != noErr) {
  NSLog(@"open file error");
}
// 获取文件格式
UInt32 dataFromatSize = sizeof(dataFormat);
AudioFileGetProperty(_mAudioFile, kAudioFilePropertyDataFormat, &dataFromatSize, &dataFormat);

```

第一步是用AudioFile打开文件，如果打开成功的话，直接获取出这个AudioFile的DataFormat就好了，是不是很简单呢？对于填充数据也比较简单，直接从AudioFile中读取原始数据就可以了。

学到这里可能你会有疑问，绕了一大圈，用AudioQueue就直接播放了一个音频文件，那我直接使用AVAudioPlayer或者AVPlayer来播放这个音频文件不更简单吗？的确是的，但我更想通过这个例子来告诉你： **这就是iOS给开发者提供的强大的多媒体处理能力，而AudioQueue更适合开发者在一些更底层的数据处理的场景下使用。**

## 小结

最后，我们可以一起来回顾一下。

![](https://static001.geekbang.org/resource/image/bd/40/bd314e0090edf7c1636a5cd6d8a9cd40.png?wh=1725x751)

这节课我们对iOS的音频框架有了一个大致的了解。其中最重要的两个就是AudioQueue和AudioUnit。AudioQueue使用起来非常方便，它是实现录制与播放功能最简单的API接口，就算你不知道内部的细节，也可以简单地完成播放PCM数据的功能。所以如果你的输入是PCM，比如视频播放器场景、RTC等需要业务自己Mix或者处理PCM的场景，那么使用AudioQueue是非常适合的一种方式。

AudioUnit是iOS中最底层的音频框架，对音频能够实现更高程度的控制，所以也是我们的必学内容之一，下节课我会详细地讲一讲怎么使用AudioUnit实现音频的渲染，期待一下吧！

今天我通过代码带你创建并设置了AVAudioSession，还带你详细了解了AudioQueue的运行流程以及iOS平台的音频格式ASBD，希望你学完之后可以自己动手练一练，把今天学习的内容内化到自己的知识网络中。

## 思考题

学而不思则罔，最后我给你留一道思考题：你思考一下AudioQueue相比于AVPlayer或者AVAudioPlayer，它的灵活性或者说好处在哪儿呢？欢迎在评论区分享你的思考，也欢迎你把这节课分享给更多对音视频感兴趣的朋友，我们一起交流、共同进步。下节课再见！