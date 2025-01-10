你好，我是展晓凯。今天我们来一起学习Android平台视频画面的采集。

[上一节课](https://time.geekbang.org/column/article/556012) 我们一起学习了iOS平台的视频画面采集，Android平台的采集相对来讲会更复杂一些，因为我们整个系统的核心部分都是在Native层构建的，所以这就会涉及JNI层的一些转换操作。不过不用担心，我会带着你一步步构建起整个系统。

## 权限配置

要想使用Android平台提供的摄像头，必须在配置文件里添加权限要求。

```plain
<uses-permission android:name="android.permission.CAMERA" />

```

Android 6.0及以上的系统，需要动态申请权限。

```plain
if (ContextCompat.checkSelfPermission(MainActivity.this, android.Manifest.permission.CAMERA)!= PackageManager.PERMISSION_GRANTED){
  //没有权限就在这里申请
  ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.CAMERA}, CAMERA_OK);
}else {
  //说明已经获取到摄像头权限了
}

```

随着Android系统的发展，摄像头API也有了非常多的变化，这里我们使用的是给Camera设置预览纹理的方式，而不是使用给Camera设置接收YUV数据回调的方式。这是因为得到纹理ID之后，进入我们的OpenGL ES渲染链路会更方便，同时视频滤镜处理、View的渲染也会方便一些。

## 配置摄像头

使用Android的摄像头采集数据，需要打开摄像头并进行一些配置，我们先来看打开摄像头的操作。

### 打开摄像头

Android平台提供的打开摄像头的接口如下：

```plain
public static Camera open(int cameraId)

```

需要传入的参数就是摄像头的ID。我们知道，是先有的后置摄像头，后有的前置摄像头，甚至目前部分手机已经有了更多的辅助摄像头，所以摄像头的ID也是按先后顺序排列的，后置摄像头是0，前置摄像头是1，然后才是其他的摄像头，需要使用CameraInfo这个类里面的两个常量，CAMERA\_FACING\_BACK后置摄像头和CAMERA\_FACING\_FRONT前置摄像头

这个函数返回的就是一个摄像头的实例，如果返回的是NULL，或者抛出异常（因为不同厂商所给出的返回不一致），代表用户没有给这个应用授权，就不可以访问摄像头。拿到这个摄像头实例之后，要为这个摄像头实例做一些配置，参数的配置主要就是预览格式和预览的尺寸。先来看预览格式的设置。

### 预览格式

预览格式一般设置为NV21格式，实际上就是YUV420SP格式，即UV是交错（interleaved）存放的，设置代码如下：

```plain
List<Integer> supportedPreviewFormats = parameters.getSupportedPreviewFormats();
if (supportedPreviewFormats.contains(ImageFormat.NV21)) {
    parameters.setPreviewFormat(ImageFormat.NV21);
} else {
    throw new CameraParamSettingException("视频参数设置错误:设置预览图像格式异常");
}

```

代码显示，先取出摄像头支持的所有的预览格式，然后判断一下有没有我们要设定的格式，如果有，就设置进去；如果没有，就抛出异常，留给业务层处理。

### 预览尺寸

接下来是预览尺寸的设置，一般设置成1280 _720，当然在某些特殊场景，也可以设置成640_ 480的分辨率，设置代码如下：

```plain
List<Size> supportedPreviewSizes = parameters.getSupportedPreviewSizes();
int previewWidth = 640;//1280
int previewHeight = 480;//720
boolean isSupportPreviewSize = isSupportPreviewSize(
        supportedPreviewSizes, previewWidth, previewHeight);
if (isSupportPreviewSize) {
    parameters.setPreviewSize(previewWidth, previewHeight);
} else {
    throw new CameraParamSettingException("视频参数设置错误:设置预览的尺寸异常");
}

```

执行代码就会获取摄像头支持的所有分辨率列表，然后判断要设置的分辨率是否在支持的列表中，如果在的话就设置进去，否则抛出异常，留给业务层去处理。

配置完上面的参数之后，就要把这个参数设置给Camera这个实例了，代码如下：

```plain
try {
    mCamera.setParameters(parameters);
} catch (Exception e) {
    throw new CameraParamSettingException("视频参数设置错误");
}

```

在宽高的设置中，要注意宽是1280（或者640），高是720（或者480），这是因为摄像头默认采集出来的视频画面是横版的。在显示的时候，需要获取当前摄像头采集出来的画面的旋转角度，我们可以通过下面这段代码来获取旋转角度。

```plain
int degrees = 0;
CameraInfo info = new CameraInfo();
Camera.getCameraInfo(cameraId, info);
if (info.facing == Camera.CameraInfo.CAMERA_FACING_FRONT) {
    degrees = (info.orientation) % 360;
} else { // back-facing
    degrees = (info.orientation + 360) % 360;
}

```

根据不同的摄像头取出对应的CameraInfo，这个CameraInfo里的orientation属性表示的就是画面的旋转角度，不过要想正确地旋转还要再处理一下。如果是前置摄像头，就直接对360进行取模；如果是后置摄像头，要加上360度再取模360，从而得到要旋转的角度。这个角度对于将视频帧正确地显示到屏幕上是至关重要的，所以我们带着这个角度进入摄像头预览部分的学习吧。

## 摄像头的预览

摄像头的基础参数配置好之后，就可以接收摄像头采集的图像，然后将图像渲染到屏幕上了。OpenGL ES渲染图像的基本流程是，先把图像解码成RGBA格式，然后将RGBA格式的字节数组上传到一个纹理上，最终将纹理渲染到屏幕View上，而这里的渲染也会使用OpenGL ES实现。

### 渲染链路

整体渲染架构我们在Java层构造一个Surface(Texture)View，来显示渲染的结果，然后在Native层用EGL和OpenGL ES给这个SurfaceView做渲染。核心的连接点如下：

- 在Native层的OpenGL线程中，生成一个纹理ID并传递到Java层，Java层利用这个纹理ID构造出一个SurfaceTexture。
- 把这个SurfaceTexture设置给Camera的预览纹理，然后调用Camera的开始预览方法。

![图片](https://static001.geekbang.org/resource/image/9a/37/9a85b7aa0208536735bb39b2cbe5f237.png?wh=1920x1001)

但是我们怎么能够知道摄像头捕捉到了一张新的图片呢？答案就是给这个SurfaceTexture设置视频帧可用监听者。当Camera设备采集到一帧内容的时候，就会回调这个Listener，你可以看一下代码。

```plain
mCameraSurfaceTexture = new SurfaceTexture(textureId);
try {
    mCamera.setPreviewTexture(mCameraSurfaceTexture);
    mCameraSurfaceTexture.setOnFrameAvailableListener(frameAvailableListener);
    mCamera.startPreview();
} catch (Exception e) {
    throw new CameraParamSettingException("设置预览纹理错误");
}

```

代码里的frameAvailableListener是继承自OnFrameAvailableListener的内部类的一个实例，这个内部类里需要重写onFrameAvailable方法。当摄像头采集到一帧图像后，就会调用这个方法，在方法中我们调用Native层的方法来渲染出摄像头刚刚捕捉的图像。

Native层的这个方法会转换到渲染线程中调用SurfaceTexture的updateTexImage方法（因为必须在OpenGL ES线程才可以调用这个方法，所以绕了一大圈）。这个方法调用完毕之后，摄像头采集的视频帧就放到了Native层生成的纹理上去了，渲染线程就可以继续把这个纹理渲染到界面上去了。当摄像头再一次采集到一帧新图像的时候，就周而复始地执行上述过程，这样在设备屏幕上就可以流畅地预览摄像头采集的内容了。

![图片](https://static001.geekbang.org/resource/image/74/d0/744eyy84604f78a1bc065652fb6357d0.png?wh=1920x673)

### 渲染过程与OES纹理

上面我们在Native层的OpenGL线程中生成一个纹理ID，然后传递到Java层，由Java层构造成一个SurfaceTexture类型的对象，并将Camera的PreviewCallback设置为这个SurfaceTexture对象。

还记得在摄像头配置阶段，我们给摄像头配置的视频频帧格式是NV21吗？也就是YUV420SP格式的，这个格式中width \* height个像素点需要占用width \* height \* 3 / 2个字节数，即每一个像素点都会有一个Y放到数据存储的前width \* height个数据中，每四个像素点共享一个UV放到后半部分进行交错存储。

而在OpenGL中使用的绝大部分纹理对象都是RGBA的格式，另外之前在讲播放器的时候，我们也讲过Luminance格式，但是那里面是开辟3个纹理来表示一张YUV的图片，而这里必须使用一个纹理ID来给Camera更新数据，那应该怎么把3个Luminance的纹理合并成一个纹理对象呢？

幸好OpenGL ES提供了一个扩展类型：GL\_TEXTURE\_EXTERNAL\_OES，这种纹理在使用上会有一些特殊，比如，纹理需要绑定到类型GL\_TEXTURE\_EXTERNAL\_OES上，而不是类型GL\_TEXTURE\_2D上，给纹理设置参数的时候也要使用GL\_TEXTURE\_EXTERNAL\_OES类型，生成这种类型的纹理与设置参数的代码如下：

```plain
glGenTextures(1, &texId);
glBindTexture(GL_TEXTURE_EXTERNAL_OES, texId);
glTexParameteri(GL_TEXTURE_EXTERNAL_OES, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_EXTERNAL_OES, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
glTexParameteri(GL_TEXTURE_EXTERNAL_OES, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_EXTERNAL_OES, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

```

在实际的渲染过程中绑定纹理的代码如下：

```plain
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_EXTERNAL_OES, texId);
glUniform1i(uniformSamplers, 0);

```

在OpenGL ES的shader中需要声明对此扩展的使用，指令如下：

```plain
#extension GL_OES_EGL_image_external : require

```

在shader里也必须使用samplerExternalOES采样方式来声明纹理，FragmentShader中的代码如下：

```plain
static char* GPU_FRAME_FRAGMENT_SHADER =
"#extension GL_OES_EGL_image_external : require                   \n"
"precision mediump float;                                           \n"
"uniform samplerExternalOES yuvTexSampler;                          \n"
"varying vec2 yuvTexCoords;                                                                              \n"
"                                                                     \n"
"void main() {                                                       \n"
"    gl_FragColor = texture2D(yuvTexSampler, yuvTexCoords);\n"
"}                                                                                                                                             \n";

```

从生成纹理到设置参数，再到真正渲染这一整个流程下来，我们就弄清楚了这种特殊格式的纹理的使用方法，接下来我们再看一下摄像头采集图像旋转角度的问题。

### 纹理旋转角度

在使用摄像头的时候，很容易在这个地方踩坑，比如手机摄像头预览的时候会出现倒立、镜像等问题，下面我就带你彻底地搞定它。

由于摄像头采集出来的视频都是横向的，比如摄像头的预览大小是640 \* 480，其实摄像头采集出来的视频帧宽是640，高是480，并且图片也是横向采集的。如果要能正确地预览出来需要旋转一个90度或270度，具体旋转多少度需要在当前这个摄像头的CameraInfo里面获取。

不同的手机甚至是不同的系统都会不一样，并且如果是前置摄像头的话，还需要再做一个VFlip（垂直镜像）用来修复镜像的问题。假设图像是横向采集出来的，就做竖直翻转，如果已经旋转过了，就做横向翻转。下面我们用实际的图片，来分别看一下前置摄像头和后置摄像头具体的渲染流程。先看一张实际摄像头要采集的物体。

![图片](https://static001.geekbang.org/resource/image/54/dc/5483e188bef86567c2f1f3aeeed100dc.png?wh=1696x578)

在使用 **前置摄像头** 去采集这个物体的时候，得到最左边的图片，这个时候在摄像头的CameraInfo里取出来的角度一般是270度。按照旋转角度，我们把图片顺时针旋转270度，得到中间的图片，再进行镜像处理，得到最右边的图片。最后我们在手机屏幕上看到的才是预期的图像。

![图片](https://static001.geekbang.org/resource/image/af/c0/af629d66a6dcbe8592b5d82ba34730c0.png?wh=1916x560)

如果是 **后置摄像头**，一般在摄像头的CameraInfo里取出来的角度是90度，当然这是ROM厂商定的，比如LG厂商的Nexus5X这个设备取出来的角度就是270度。不过无论是多少度，摄像头采集出来的图像，根据这个角度在旋转过后，就能得到一个正常的图像了，你可以看一下它的旋转流程。

![图片](https://static001.geekbang.org/resource/image/f4/7f/f488a98ffyy778f2535dc4768620907f.png?wh=1692x580)

如果是LG厂商的Nexus5X或者HUAWEI厂商的Nexus6P这两款设备，图像的后置摄像头需要顺时针旋转270度，得到正常显示的图像。

![图片](https://static001.geekbang.org/resource/image/f8/13/f88385f2591a1b34d2e03c606eb02813.png?wh=1680x584)

### 确定物体坐标与纹理坐标

上述图像的旋转和镜像，在OpenGL ES中需要通过物体坐标和纹理坐标变换来实现。我们可以再回看一下之前物体坐标系和纹理坐标系的图。

![图片](https://static001.geekbang.org/resource/image/45/4b/451583e39a93e7b42ef62e38e7c9964b.png?wh=1920x865)

而我们这里的物体坐标也是一个通用的坐标。

```plain
GLfloat squareVertices[8] = {
    -1.0, -1.0, //物体左下角
    1.0，-1.0，  //物体右下角
    -1.0，1.0，  //物体左上角
    1.0，1.0     //物体右上角
};

```

下面是不做任何旋转与镜像的OpenGL纹理坐标。

```plain
GLfloat textureCoordNoRotation[8] = {
    0.0，0.0，//图像的左下角
    1.0，0.0，//图像的右下角
    0.0，1.0，//图像的左上角
    1.0，1.0  //图像的右上角
};

```

然后，给出顺时针旋转90度的纹理坐标，你可以想象一下，把OpenGL的纹理坐标系的图顺时针旋转90度，然后再把对应的左下、右下、左上、右上的坐标点写下来。

```plain
GLfloat textureCoords[8] = {
    1.0，0.0，//图像的右下角
    1.0，1.0，//图像的右上角
    0.0，0.0，//图像的左下角
    0.0，1.0  //图像的左上角
};

```

给出顺时针旋转180度的纹理坐标。

```plain
GLfloat textureCoords[8] = {
    1.0，1.0，//图像的右上角
    0.0，1.0，//图像的左上角
    1.0，0.0，//图像的右下角
    0.0，0.0  //图像的左下角
};

```

然后，给出顺时针旋转270度的纹理坐标。

```plain
GLfloat textureCoords[8] = {
    0.0，1.0，//图像的左上角
    0.0，0.0，//图像的左下角
    1.0，1.0，//图像的右上角
    1.0，0.0  //图像的右下角
};

```

还记得前面我们讲过计算机图像的坐标系与OpenGL的坐标系不同吗？它们的Y恰好是相反的，所以这里要把每一个纹理坐标做一个VFlip的变换（垂直镜像，即把每一个顶点的y值由0变为1或者由1变为0），这样就可以得到一个正确的图像旋转了。而我们的前置摄像头存在镜像的问题，这时候需要对每一个纹理坐标做一个HFlip变换（水平镜像，即把每一个顶点的x值由0变为1或者由1变为0），从而让图片在预览界面中看起来和在镜子中一样。

### 自适应渲染

上面的步骤其实就是一个特殊格式（OES）的纹理经过旋转和渲染，变成了正常格式（RGBA）的一个纹理，那接下来就可以把这个正常格式的纹理渲染到屏幕上去了。

但这里需要补充一句，由于这个纹理的宽和高实际上是摄像头捕捉过来的图像的高和宽（做了一个90度或者270度的旋转），而我们的目标是要渲染到SurfaceView上面去，但是如果Java层提供的SurfaceView的宽高和处理过后的这个纹理ID的宽高不一致，那么这一帧图像就会出现被压缩或者拉伸的问题，所以在渲染到屏幕上的时候，我们要做一个自适配，让纹理按照屏幕View的比例自动填充。

先来看纹理坐标，x从0.0到1.0就说明要把纹理的x轴方向全部都绘制到物体表面（整个SurfaceView）上去，而如果我们只想绘制一部分，比如中间的一半，那么就可以将x轴的坐标写成0.25到0.75，类似的适配也可以应用到y轴上。但这个0.25和0.75是如何得出来的呢？

答案很简单，如果不想被拉伸，SurfaceView的宽高比例和纹理的宽高比例就应该是相同的。假设这一张纹理的宽为texWidth，高为texHeight，而物体表面的宽为screenWidth，高为screenHeight，就可以利用下面的公式来完成自动填充的坐标计算。

```plain
float textureAspectRatio = texHeight / texWidth;
float viewAspectRatio = screenHeight / screenWidth;
float xOffset = 0.0f;
float yOffset = 0.0f;
if(textureAspectRatio > viewAspectRatio){
    //Update Y Offset
    int expectedHeight = texHeight*screenWidth/texWidth+0.5f;
    yOffset = (expectedHeight - screenHeight) / (2 * expectedHeight);
} else if(textureAspectRatio < viewAspectRatio){
    //Update X Offset
    int expectedWidth = texHeight * screenWidth / screenHeight + 0.5);
    xOffset = (texWidth - expectedWidth)/(2*texWidth);
}

```

计算得到的xOffset和yOffset在纹理坐标中分别替换掉0.0的位置，利用1.0-xOffset以及1.0-yOffset替换掉1.0的位置，最终得到一个纹理坐标矩阵。

```plain
GLfloat textureCoordNoRotation[8] = {
    xOffset，           yOffset，
    1.0 - xOffset，     yOffset，
    xOffset，           1.0 - yOffset，
    1.0 - yOffset，     1.0 - yOffset
};

```

到这里，摄像头预览流程就可以随着摄像头所采集的图像一帧一帧地绘制下去了，也就实现了整个预览过程。

### 切换摄像头与关闭预览

当用户切换摄像头的时候，就可以给Native层发一个指令，Native层会在OpenGL线程中关闭当前摄像头，然后重新打开另外一个摄像头，并配置参数，然后设置预览的SurfaceTexture，最后调用开始预览方法，这样就可以切换成功了，用户看到的就是切换摄像头之后的预览画面。

最终关闭预览时，要先停掉整个渲染线程，然后关闭Camera，当然还要释放之前建立的SurfaceTexture，把摄像头的PreviewCallback设置为null，最终释放掉摄像头。

![图片](https://static001.geekbang.org/resource/image/99/ec/994dd896159418becf7e6536395b20ec.png?wh=1920x524)

到这里，摄像头预览相关的操作就全都讲完了，这个部分的内容是十分重要的，对后面搭建整个录制视频的项目来说，是最基础的部分，所以一定要掌握。

## 小结

最后，我们可以一起来回顾一下这节课的主要内容。这节课我们从权限配置开始，然后讲解了摄像头的配置与打开摄像头的操作，接着详细讲解了如何将摄像头采集到的图像一步步渲染到屏幕View上，整体流程如下：

- 在Native层创建一个OpenGL线程，并且构建出一个OES类型的纹理ID传递给Java层构造成一个SurfaceTexture，然后配置给摄像头。
- 当摄像头采集到一帧图像之后，就会通过回调的方式告诉我们，我们将在OpenGL线程中调用update方法将这一帧图像更新到纹理ID上。
- 接着按照旋转角度确定纹理矩阵，将OES的纹理渲染成为一个标准的RGBA的纹理。
- 最后将RGBA类型的纹理在渲染到屏幕上。

如果你了解清楚整个过程，那么后面学习编码也会更加顺畅。

![图片](https://static001.geekbang.org/resource/image/e3/be/e3306e85566c35d565032124fde097be.png?wh=1898x1384)

## 思考题

这节课我们学习了摄像头预览的流程，那我来考考你，摄像头采集的出来的纹理类型是什么类型，它又是怎么被绘制到屏幕View上去的呢？欢迎你把这节课分享给更多对音视频感兴趣的朋友，我们一起交流、共同进步。下节课再见！