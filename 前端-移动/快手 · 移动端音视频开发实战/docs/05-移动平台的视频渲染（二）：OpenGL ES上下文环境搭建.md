你好，我是展晓凯。今天我们来继续学习移动平台的视频渲染。

[上一节课](https://time.geekbang.org/column/article/545953)，我们使用OpenGL ES提供给开发者的接口，创建出了一个GLProgram，但是如果让这个GLProgram运行起来还需要有一个上下文环境来支撑。由于OpenGL ES一开始就是为跨平台设计的，所以它本身并不承担窗口管理以及上下文环境构建的职责，这个职责需要由各自的平台来承担。

Android平台使用的是EGL，EGL是Khronos创建的一个框架，用来给OpenGL的输出与设备的屏幕搭建起一个桥梁。EGL的工作机制是双缓冲模式，也就是有一个Back Frame Buffer和一个Front Frame Buffer，正常绘制操作的目标都是Back Frame Buffer，渲染完毕之后，调用eglSwapBuffer这个API，会将绘制完毕的Back Frame Buffer与当前的Front Frame Buffer进行交换，然后显示出来。EGL承担了为OpenGL提供上下文环境以及窗口管理的职责。

iOS平台使用的是EAGL，与EGL的双缓冲机制比较类似，iOS平台也不允许我们直接渲染到屏幕上，而是渲染到一个叫renderBuffer的对象上。这个对象你可以理解为一个特殊的FrameBuffer，最终再调用EAGLContext的presentRenderBuffer方法，就可以将渲染结果输出到屏幕上去了。

下面我会分别对这两个平台的环境搭建进行详细地介绍。

## Android平台的环境搭建

要在Android平台上使用OpenGL ES，最简单的方式是使用GLSurfaceView，因为不需要开发者搭建OpenGL ES的上下文环境以及创建OpenGL ES的显示设备，只需要遵循GLSurfaceView定义的接口，实现对应的逻辑即可。就像硬币有正反面一样，使用GLSurfaceView的缺点也比较明显，就是不够灵活，OpenGL ES很多核心用法，比如共享上下文，使用起来就会比较麻烦。

我们这个专栏的OpenGL ES上下文环境，会直接使用EGL提供的API，在Native层基于C++环境进行搭建。原因是在Java层进行搭建的话，对于普通的应用也许可以，但是对于要进行解码或使用第三方库的场景，比如人脸识别，又需要到Native层来实施。考虑到效率和性能，我们这里就直接使用Native层的EGL来搭建一个OpenGL ES的开发环境。

### 引入头文件与so库

那么如何在Native层使用EGL呢？我们必须要在CMake构建脚本（CMakeLists.txt）中加入EGL这个库，并在使用这个库的C++文件中引入EGL对应的头文件。

需要引用的头文件如下：

```plain
#include <EGL/egl.h>
#include <EGL/eglext.h>

```

需要引入的so库：

```plain
target_link_libraries(videoengine
        # 引入系统的动态库
        EGL
        )

```

这样我们就可以在Android的Native层中使用EGL了，不过要使用OpenGL ES给开发者提供的接口，还需要引入OpenGL ES对应的头文件与库。

需要包含的头文件：

```plain
#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>

```

需要引入的so库，注意这里使用的是OpenGL ES 2.0版本。

```plain
target_link_libraries(videoengine
        # 引入系统的动态库
        GLESv2
        )

```

至此，OpenGL ES的开发需要用到的头文件以及库文件就引入完毕了，下面我们来看一下如何使用EGL搭建出OpenGL的上下文环境以及实现窗口的管理。

### EGLDisplay作为绘制的目标

EGL首先要解决的问题是，要告诉OpenGL ES绘制的目标在哪里，而EGLDisplay就是一个封装系统物理屏幕的数据类型，也就是绘制目标的一个抽象。开发者要调用eglGetDisplay这个方法来创建出EGLDisplay的对象，在调用这个方法的传参中，常量EGL\_DEFAULT\_DISPLAY会被传进这个方法中，每个厂商在自己的实现中都会返回默认的显示设备，代码如下：

```plain
EGLDisplay display;
if ((display = eglGetDisplay(EGL_DEFAULT_DISPLAY)) == EGL_NO_DISPLAY) {
    LOGE("eglGetDisplay() returned error %d", eglGetError());
    return false;
}

```

在获得了EGLDisplay的对象之后，就需要对这个对象做初始化工作，开发者需要调用EGL提供的eglInitialize方法来初始化这个对象，这个方法会返回一个bool值来代表函数运行结果。函数的第一个参数就是EGLDisplay对象，后面两个参数是这个函数为了返回EGL版本号而设计的，两个参数分别是Major和Minor的Version，比如EGL的版本号是1.0，那么Major返回1，Minor则返回0，如果我们不关心版本号，可以都传入0或者NULL，代码如下：

```plain
if (!eglInitialize(display, 0, 0)) {
    LOGE("eglInitialize() returned error %d", eglGetError());
    return false;
}

```

一旦EGLDisplay初始化成功之后，它就可以将OpenGL ES的输出和设备的屏幕桥接起来，但是需要我们指定一些配置项，比如色彩格式、像素格式、OpenGL版本以及SurfaceType等，不同的系统以及平台使用的EGL标准是不同的，在Android平台下一般配置的代码如下所示：

```plain
EGLConfig config;
const EGLint attribs[] = {EGL_BUFFER_SIZE, 32,
        EGL_ALPHA_SIZE, 8,
        EGL_BLUE_SIZE, 8,
        EGL_GREEN_SIZE, 8,
        EGL_RED_SIZE, 8,
        EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,
        EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
        EGL_NONE };
if (!eglChooseConfig(display, attribs, &config, 1, &numConfigs)) {
    LOGE("eglChooseConfig() returned error %d", eglGetError());
    return false;
}

```

配置选项这个函数也是返回一个bool值来代表配置状态，如果配置成功，则代表config会被正确初始化。

**EGLDisplay这个对象是EGL给开发者提供的最重要的入口**，接下来我们要基于这个EGLDisplay对象还有EGLConfig配置来创建上下文了。

### EGLContext提供线程的上下文

由于任何一条OpenGL ES指令（OpenGL ES提供给开发者的接口）都必须运行在自己的OpenGL上下文环境中，EGL提供EGLContext来封装上下文，可以按照如下代码构建出OpenGL ES的上下文环境。

```plain
EGLContext context;
EGLint attributes[] = { EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE };
if (!(context = eglCreateContext(display, config, NULL,
        eglContextAttributes))) {
    LOGE("eglCreateContext() returned error %d", eglGetError());
    return false;
}

```

函数eglCreateContext的前两个参数就是我们刚刚创建的两个对象，第三个参数类型也是EGLContext类型的，一般会有两种用法。

- 如果想和已经存在的某个上下文共享OpenGL资源（包括纹理ID、frameBuffer以及其他的Buffer），则传入对应的那个上下文变量。
- 如果目标仅仅是创建一个独立的上下文，不需要和其他OpenGL ES的上下文共享任何资源，则设置为NULL。

在一些场景下其实需要多个线程共同执行OpenGL ES的渲染操作，这种情况下就需要用到共享上下文，共享上下文的关键点就在这里，一定要记住。

成功创建出OpenGL ES的上下文，说明我们已经把OpenGL ES的绘制目标搞定了，但是这个绘制目标并没有渲染到我们某个View上，那如何将这个输出渲染到业务指定的View上呢？答案就在EGLSurface。

### EGLSurface将EGLDisplay与系统屏幕桥接起来

EGLSurface实际上是一个FrameBuffer，开发者可以调用EGL提供的eglCreateWindowSurface创建一个可实际显示的Surface，调用eglCreatePbufferSuface可以创建一个OffScreen（离屏渲染，一般用户后台保存场景）的Surface，创建可实际显示的Surface代码如下：

```plain
EGLSurface surface = NULL;
EGLint format;
if (!eglGetConfigAttrib(display, config, EGL_NATIVE_VISUAL_ID,
        &format)) {
    LOGE("eglGetConfigAttrib() returned error %d", eglGetError());
    return surface;
}
ANativeWindow_setBuffersGeometry(_window, 0, 0, format);
if (!(surface = eglCreateWindowSurface(display, config, _window, 0))) {
    LOGE("eglCreateWindowSurface() returned error %d", eglGetError());
}

```

上述代码中不得不提的就是\_window这个参数，这里我需要重点向你解释一下，这个\_window是ANativeWindow类型的对象，代表了本地业务层想要绘制到的目标View。在Android里面可以通过Surface（通过SurfaceView或TextureView来得到或者构建出Surface对象）去构建出ANativeWindow。但构建之前需要我们在使用的时候引用头文件。

```plain
#include <android/native_window.h>
#include <android/native_window_jni.h>

```

调用ANAtiveWindow的API接口如下：

```plain
ANativeWindow* window = ANativeWindow_fromSurface(env, surface);

```

里面的env是JNI层的JNIEnv指针类型的变量，surface就是jobject类型的变量，是由Java层的Surface类型对象传递而来的。到这里我们就把EGLSurface和Java层的View（即设备的屏幕）连接起来了。

这里我们再补充一点，如果想做离屏渲染，也就是在后台使用OpenGL处理一些图像，就需要用到处理图像的Surface了，创建离屏Surface如下：

```plain
EGLSurface surface;
EGLint PbufferAttributes[] = { EGL_WIDTH, width, EGL_HEIGHT, height, EGL_NONE,
        EGL_NONE };
if (!(surface = eglCreatePbufferSurface(display, config, PbufferAttributes))) {
    LOGE("eglCreatePbufferSurface() returned error %d", eglGetError());
}

```

可以看到这个Surface并不会和任何一个业务View进行关联，进行离屏渲染的时候，就可以把这个Surface当作目标进行绘制。

![图片](https://static001.geekbang.org/resource/image/7b/f3/7bbf36207fbb200f7de3636f88ea1bf3.png?wh=1920x860)

现在我们已经用EGL准备好了上下文环境与窗口管理，如上图所示，左侧我们为OpenGL ES准备好上下文环境，并且用EGLDisplay用来接收绘制的内容，右边通过EGLSurface连接好了设备的屏幕（Java层提供的SurfaceView或者TextureView）。那么接下来我们就具体看一下如何使用创建好的EGL环境进行工作。

### 为绘制线程绑定上下文

OpenGL ES需要开发者自己开辟一个新的线程，来执行OpenGL ES的渲染操作，还要求开发者在执行渲染操作前要为这个线程绑定上下文环境。EGL为绑定上下文环境提供了eglMakeCurrent这个接口。

```plain
eglMakeCurrent(display, eglSurface, eglSurface, context);

```

在绑定了上下文环境以及窗口之后就可以执行RenderLoop循环了，每一次循环都是去调用OpenGL ES指令绘制图像。

还记得我们之前提到的EGL的双缓冲模式吗？EGL内部有两个帧缓冲区（frameBuffer），我们执行的渲染目标都是后台的frameBuffer。当渲染操作完成之后，要调用函数eglSwapBuffers进行前台frameBuffer和后台frameBuffer的交换。

```plain
eglSwapBuffers(display, eglSurface)

```

执行上述函数之后，用户就可以在屏幕上看到刚刚渲染的图像了。

### 销毁资源

最后执行完所有的绘制操作之后，需要销毁资源。注意销毁资源也必须在这个独立的线程中，销毁显示设备（EGLSurface）的代码如下：

```plain
eglDestroySurface(display, eglSurface);

```

销毁上下文（Context）代码如下：

```plain
eglDestroyContext(display, context);

```

到这儿，在Android平台的Native层中，我们就使用EGL成功地把OpenGL ES的上下文环境搭建出来了，后面我们会用到这些知识。

## iOS平台的环境搭建

iOS平台不允许开发者使用OpenGL ES直接渲染输出到屏幕上，而是使用Frame Buffer与Render Buffer相结合的方式来进行渲染。EAGL提供的方式是必须创建一个render Buffer，然后让OpenGL ES渲染到这个Render Buffer上面去。那这个Renderbuffer又是如何关联到业务层View上去的呢？

答案是RenderBuffer需要绑定一个CAEAGLLayer，而这个Layer实际上就可以一对一地关联到我们自定义的一个UIView。也就是开发者最后调用EAGLContext的presentRenderBuffer方法，这样就可以将渲染结果输出到屏幕上去了。实际上，在这个方法的内部实现中，EAGL也会执行类似于前面EGL中的swapBuffer的过程。具体使用步骤如下：

### 自定义一个EAGLView

我们先自定义一个继承自UIView的View，然后重写父类UIView的layerClass方法，并且一定要返回CAEAGLLayer 这个类型。

```plain
+ (Class) layerClass
{
    return [CAEAGLLayer class];
}

```

接下来在这个View的初始化方法中，我们拿到layer并强制把类型转换为CAEAGLLayer类型的变量，然后给这个layer设置对应的参数。

```plain
- (id) initWithFrame:(CGRect)frame{
    if ((self = [super initWithFrame:frame])){
        CAEAGLLayer *eaglLayer = (CAEAGLLayer *)[self layer];
        NSDictionary *dict = [NSDictionary dictionaryWithObjectsAndKeys:
                [NSNumber numberWithBool:NO],
                kEAGLDrawablePropertyRetainedBacking,
                kEAGLColorFormatRGB565,
                kEAGLDrawablePropertyColorFormat,
                nil];
         [eaglLayer setOpaque:YES];
         [eaglLayer setDrawableProperties:dict];
    }
    return self;
}

```

### 构建EAGLContext

像之前提到的，我们必须为每一个线程绑定OpenGL ES上下文，所以要开辟一个线程，开发者在iOS中开辟一个新线程的方法有很多，可以使用GCD，也可以使用NSOperationQueue，甚至裸用pthread也可以，反正必须在一个线程中执行创建上下文的操作。创建OpenGL ES的上下文代码如下：

```plain
EAGLContext* _context;
_context = [[EAGLContext alloc]initWithAPI:kEAGLRenderingAPIOpenGLES2];

```

创建成功以后就来绑定上下文。

```plain
[EAGLContext setCurrentContext:_context];

```

执行成功之后就代表我们为这个线程绑定了刚刚创建好的上下文环境，也就是说我们已经建立好了EAGL与OpenGL ES的连接，接下来我们来建立另一端的连接。

### 窗口管理

这时，我们需要创建RenderBuffer并且把它绑定到前面自定义EAGLView的Layer上。首先是创建帧缓冲区。

```plain
glGenFramebuffers(1, &_framebuffer);

```

然后创建绘制缓冲区。

```plain
glGenRenderbuffers(1, &renderbuffer);

```

绑定帧缓冲区到渲染管线。

```plain
glBindFramebuffer(GL_FRAMEBUFFER, _framebuffer);

```

绑定绘制缓存区到渲染管线。

```plain
glBindRenderbuffer(GL_RENDERBUFFER, _renderbuffer);

```

为绘制缓冲区分配存储区，这里我们把CAEAGLLayer的绘制存储区作为绘制缓冲区的存储区。

```plain
[_context renderbufferStorage:GL_RENDERBUFFER fromDrawable:(CAEAGLLayer*)
        self.layer]

```

获取绘制缓冲区的像素宽度。

```plain
glGetRenderBufferParameteriv(GL_RENDER_BUFFER, GL_RENDER_BUFFER_WIDTH,
        &_backingWidth);

```

获取绘制缓冲区的像素高度。

```plain
glGetRenderBufferParameteriv(GL_RENDER_BUFFER, GL_RENDER_BUFFER_HEIGHT,
      &_backingHeight);

```

绑定绘制缓冲区到帧缓冲区。

```plain
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER,
      _renderbuffer);

```

检查Framebuffer的status。

```plain
GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
if(status != GL_FRAMEBUFFER_COMPLETE){
    //failed to make complete frame buffer object
}

```

完成以上操作，我们就把EAGL和我们的Layer（设备的屏幕）连接起来了，当我们绘制了一帧之后（当然绘制过程也必须在这个线程中），调用以下代码就可以将绘制的结果显示到屏幕上了。

```plain
[_context presentRenderbuffer:GL_RENDERBUFFER];

```

这样我们就搭建好了iOS平台的OpenGL ES的上下文环境。这给我们之后要学的内容打好了基础。

这里Open GL上下文环境搭建的重点已经讲完了，但是学到这里你可能会有一些疑问，我们需要为每一个平台搭建自己的OpenGL ES上下文环境，感觉好复杂呀，并且整个搭建过程也都涉及平台相关的API接口，那有没有一个开源框架可以将上下文环境透明掉呢？这样开发者不就可以专注在自己的业务和重点算法攻坚上了吗？

答案是有的，就是我们接下来要学习的一个库——SDL。

## SDL的介绍与使用

SDL可以给开发者提供面向libSDL的API编程，它的内部能解决多个平台的OpenGL上下文环境和窗口管理的问题。开发者只需要交叉编译这个库到各自的平台上，就可以达到一份代码运行到多个平台的目的了。FFmpeg中的ffplay工具就是基于libSDL开发的，SDL不单单可以渲染视频画面，也可以渲染音频。

但是对于移动开发者来讲，它也有一些缺点，比如使用SDL会牺牲一些更加灵活的控制，甚至某些场景下的功能实现不了。所以到底用不用SDL，你可以根据实际需求去考量，但了解这个库是十分有必要的。

我们这个部分的讲解是基于Mac + CLion的C++工程，最后学习怎么去使用sdl2这个库来构建OpenGL ES的上下文环境。

首先是安装sdl2库，我们可以通过命令行来安装。

```plain
brew install sdl2

```

安装后，可以使用命令来查看安装列表和安装路径。

```plain
brew list 查看安装列表
brew list sdl2 查看sdl2安装路径

```

如果安装路径是：/usr/local/Cellar/sdl2/2.0.14\_1，需要在工程的CMakeLists.txt文件里，加入配置。

```plain
include_directories(/usr/local/Cellar/sdl2/2.0.14_1/include/)
link_directories(/usr/local/Cellar/sdl2/2.0.14_1/lib )

```

在工程里加入SDL库和OpenGL库链接配置。

```plain
target_link_libraries(
  SDL_OpenGL
  SDL2
  "-framework OpenGL"
)

```

加入头文件。

```plain
//SDL API
#include "SDL2/SDL.h"
//OpenGL API
#include "OpenGL/gl3.h"

```

接下来就是整个使用SDL渲染的整体流程，在讲解过程中我们参考这个流程结构图。

![图片](https://static001.geekbang.org/resource/image/6e/4b/6ed519cb2dc8cced3ee7396513fc4e4b.png?wh=1920x1074)

结合上图，我们来详细地讲解一下其中的关键流程。首先，我们需要创建窗口和OpenGL上下文。

```plain
SDL_Window *window = SDL_CreateWindow("hello OpenGL", 0, 0, 300, 300, SDL_WINDOW_OPENGL);
SDL_GLContext context = SDL_GL_CreateContext(window);

```

进行循环渲染和更新窗口操作，然后退出。

```plain
while(true) {
  drawFromOpenGL(); //执行要做的渲染
  SDL_GL_SwapWindow(window); //相当于执行了eglSwapBuffers操作
  if (SDL_PollEvent(&event) && event.type == SDL_QUIT) {
    //在点击窗口close时退出循环
    break;
  }
  SDL_Delay(30); //单位ms,设置刷新频率
}

```

最后，释放资源。

```plain
SDL_GL_DeleteContext(context);
SDL_DestroyWindow(window);
SDL_Quit();

```

按照上述的整个流程，我们就使用SDL构建起OpenGL ES的上下文环境了，其实这也回答了刚才我们提出的问题。如果你选择使用SDL来构建，那么你写的代码就是跨平台的，实际上是SDL内部将平台的差异性屏蔽掉了，让我们可以更方便地去书写自己的业务，这也是面向对象思想的一个重要特征，你也可以思考一下，把它用到平时的系统与架构设计中。

## 总结

这节课我们分别为Android和iOS平台构建出了OpenGL ES的上下文环境，也给你讲解了使用SDL的方法以及优势。

![图片](https://static001.geekbang.org/resource/image/10/6c/1072af5f016e12b10874703310ac1a6c.png?wh=1920x895)

还记得在上一节课我们创建出来的显卡执行程序吗？接下来就是见证奇迹的时刻：让我们创建的显卡执行程序运行在构建出来的上下文环境上，最终我们可以通过OpenGL ES将YUV（或者RGBA）数据绘制到系统屏幕上。那么如何将显卡执行程序运行到平台的上下文环境中呢？我们下节课接着聊。

## 思考题

在今天学习中，我们知道了OpenGL ES的渲染需要在一个绑定了上下文的独立线程中进行，但是在实际的一些场景中，OpenGL ES的渲染需要分布在多个线程中，并且多个线程还需要共享这个上下文环境，那这个时候我们应该如何处理呢？欢迎在评论区留下你的思考，也欢迎你把这节课分享给需要的朋友，我们下节课再见！