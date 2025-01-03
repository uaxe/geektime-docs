你好，我是展晓凯。今天我们来继续学习移动平台的视频渲染。

在 [第4讲](https://time.geekbang.org/column/article/545953) 中，我们学习了OpenGL ES的基础概念，并且用OpenGL ES提供给我们的接口构建出了一个GLProgram； [第5讲](https://time.geekbang.org/column/article/546501)，我们学习了如何在移动平台搭建OpenGL ES的上下文环境。有了之前的准备，我们终于迎来了收获成果的时刻——让GLProgram在上下文环境中跑起来。

## GLSL语法与内建函数

在让GLProgram跑起来之前，我们还需要学习一下GLSL的语法和内建函数，这样才能够学会用GLSL书写着色器。

> GLSL是OpenGL的着色器语言，开发者自己能够编写着色器来完成渲染管线的顶点变换阶段和片元处理阶段。——第4讲内容回顾

我们这个部分的目标就是实现一组着色器来完成增强对比度的功能，但是这组着色器还不能直接看到效果，因为着色器是需要运行到显卡中的，要想看到效果还得等这节课学完之后，所以不要着急，我们慢慢来。

前面我们已经粗略地介绍过GLSL是什么了，但是一直没有准确地给它下过定义，其实就是担心你看到它的定义之后，觉得难以理解，而学到这里我们已经了解了 [渲染管线以及着色器的职责](https://time.geekbang.org/column/article/545953)，GLSL理解起来也就容易多了。

GLSL（OpenGL Shading Language）就是OpenGL为了实现着色器给开发人员提供的一种开发语言。接触一门新的编程语言，一般要先看一下它的数据类型和修饰符，然后再学习这种语言的内嵌函数，最终再构建一个完整的程序，让它跑起来。我们先来看一下基本的数据类型。

### GLSL的修饰符与数据类型

![图片](https://static001.geekbang.org/resource/image/43/3c/43605e35dc22794f5db5db21af9d743c.png?wh=1588x1326)

其实GLSL的语法跟C语言非常类似，所以我们学起来也会比较轻松。我们先来看一下 **GLSL中变量的修饰符**，具体如下：

![图片](https://static001.geekbang.org/resource/image/17/1e/1703e04fd6c27993cbb8d9e94bfa9a1e.png?wh=1920x645)

接着我们看一下 **GLSL的基本数据类型：** int、float、bool，这些都是和C语言一致的，有一点需要强调的就是，GLSL中的float是可以再加一个修饰符的，这个修饰符用来指定精度。修饰符的可选项有三种：

![图片](https://static001.geekbang.org/resource/image/34/y7/349c929770ff5f73aa312edf86216yy7.png?wh=1920x485)

一般基础数据类型讲完之后，就应该讲数组了，在 **GLSL中就是向量类型**（vec），向量类型是Shader中最常用的一个数据类型，因为在做数据传递的时候经常要传递多个参数，相较于写多个基本数据类型，使用向量类型更加简单。比如，通过OpenGL接口把物体坐标和纹理坐标传递到顶点着色器中，用的就是向量类型。每个顶点都是一个四维向量，在顶点着色器中利用这两个四维向量就能去做自己的运算，你可以看下它的声明方式。

```plain
attribute vec4 position;

```

接下来是 **矩阵类型**（matrix），矩阵类型在GLSL中同样也是一个非常重要的数据类型，在某些效果器的开发中，需要开发者自己传入一些矩阵类型的数据，用于像素计算。比如GPUImage中的怀旧效果器，就需要传入一个矩阵来改变原始的像素数据，你可以看一下它的声明方式。

```plain
uniform lowp mat4 colorMatrix;

```

上面的代码表示的是一个4 _4的浮点矩阵，如果是mat2的声明，代表的就是2_ 2的浮点矩阵，而mat3代表的就是3\*3的浮点矩阵。OpenGL为开发者提供了以下接口，把内存中的数据（mColorMatrixLocation）传递给着色器。

```plain
glUniformMatrix4fv(mColorMatrixLocation, 1, false, mColorMatrix);

```

其中，mColorMatrix是这个变量在接口程序中的句柄。这里一定要注意，上边的这个函数不属于GLSL部分，而是属于客户端代码，也就是说，我们调用这个函数来和着色器进行交互。

接下来就是 **纹理类型**，在这节课的最后我们会介绍纹理应该如何加载以及渲染，这里我们先把关注点放在如何声明这个类型上，这个类型一般只在片元着色器中使用，下面GLSL代码是二维纹理类型的声明方式。

```plain
uniform sampler2D texSampler；

```

那客户端如何写代码来把图像传递进来呢？首先我们需要拿到这个变量的句柄，定义为mGLUniformTexture，然后就可以给它绑定一个纹理，接口程序的代码如下：

```plain
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, texId);
glUniform1i(mGLUniformTexture, 0);

```

注意， **上述接口程序中的第一行代码激活的是哪个纹理句柄，在第三行代码中的第二个参数就需要传递对应的Index**，就比如说代码中激活的纹理句柄是GL\_TEXTURE0，对应的第三行代码中的第二个参数Index就是0，如果激活的纹理句柄是GL\_TEXTURE1，那对应的Index就是1，句柄的个数在不同的平台不一样，但是一般都会在32个以上。

最后，我们来看一个比较特殊的 **传递类型**，在GLSL中有一个特殊的修饰符就是varying，这个修饰符修饰的变量都是用来在顶点着色器和片元着色器之间传递参数的。最常见的使用场景就是在顶点着色器中修饰纹理坐标，顶点着色器会改变这个纹理坐标，然后把这个坐标传递到片元着色器，代码如下：

```plain
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main(void)
{
    //计算顶点坐标
    v_texcoord = texcoord;
}

```

接着在片元着色器中也要声明同名的变量，然后使用texture2D方法来取出二维纹理中这个纹理坐标点上的纹理像素值，代码如下：

```plain
varying vec2 v_texcoord;
vec4 texel = texture2D(texSampler, v_texcoord);

```

取出了这个坐标点上的像素值，就可以进行像素变化操作了，比如说去提高对比度，最终将改变的像素值赋值给gl\_FragColor。

### GLSL的内置变量与内嵌函数

接下来我们看一下GLSL内置变量。常见的是两个Shader的输出变量，一个是顶点着色器的内置变量gl\_position，它用来设置顶点转换到屏幕坐标的位置。

```plain
vec4 gl_posotion;

```

另外一个内置变量用来设置每一个粒子矩形大小，一般是在粒子效果的场景下，需要为粒子设置绘制的半径大小时使用。

```plain
float gl_pointSize;

```

其次是片元着色器的内置变量gl\_FragColor，用来指定当前纹理坐标所代表的像素点的最终颜色值。

```plain
vec4 gl_FragColor;

```

然后是GLSL内嵌函数部分，我们在这里只介绍常用的几个常用函数。

![图片](https://static001.geekbang.org/resource/image/e9/29/e93a58f8c956ed8f0bf0805db008bd29.png?wh=1866x1094)

其他函数，比如角度函数、指数函数、几何函数，这里我就不再赘述了，用到的时候你可以去 [官方文档](https://www.khronos.org/opengles/sdk/docs/manglsl/docbook4/) 中进行查询。

对于一种语言的语法来讲，剩下的就是控制流的部分了。GLSL的控制流与C语言非常类似，既可以使用for、while以及do-while实现循环，也可以使用if和if-else进行条件分支的操作，在后面的实践过程中，GLSL代码中都会用到这些控制流，这里我们就不再讲解了。

到这里， GLSL的语法部分已经讲完了，相信你已经可以书写出着色器了。现在我们再来思考一个问题：GLProgram是对什么进行绘制或者渲染呢？

没错，就是纹理，接下来让我们一起来学习一下。

## OpenGL ES的纹理

OpenGL中的纹理用GLUint类型来表示，通常我们称之为Texture或者TextureID，可以用来表示图像、视频画面等数据。在我们这个专栏里，只需要处理二维的纹理，每个二维纹理都由许多小的片元组成，每一个片元我们可以理解为一个像素点。大多数的渲染过程，都是基于纹理进行操作的，最简单的一种方式就是从一个图像文件加载数据，然后上传到显存中构造成一个纹理，具体的方式后续我们会介绍。

### 纹理坐标系

为了访问到纹理中的每一个片元（像素点），OpenGL ES构造了纹理坐标空间，坐标空间的定义是从左下角的（0，0）到右上角的（1，1）。横轴维度称为S轴，左边是0，右边是1，纵轴维度称为T轴，下面是0，上面是1。按照这个规则就构成了左图所示的坐标系，可以看到上下左右四个顶点的坐标位置，而中间的位置就是（0.5，0.5）。

另外在这里不得不提的是计算机系统里的坐标空间，通常X轴称之为横轴，从左到右是0～1，Y轴称之为纵轴，是从上到下是0～1，如图所示：

![图片](https://static001.geekbang.org/resource/image/bd/60/bd8038285123c7da28150b7d41bfb360.png?wh=1920x1064)

无论是计算机还是手机的屏幕坐标，X轴是从左到右是0～1，Y轴是从上到下是0～1，这种存储方式是和图片的存储是一致的。我们这里假设图片（Bitmap）的存储是把所有像素点存储到一个大数组中，数组的第一个像素点表示的就是图片左上角的像素点（即第一排第一列的像素点），数组中的第二个元素表示的是第一排第二列的第二个像素点，依此类推。

这样你会发现 **这种坐标其实是和OpenGL中的纹理坐标做了一个旋转180度**，理解这一点是非常重要的，因为接下来我们学习如何从本地图片中加载一张纹理并且渲染到界面上的时候，就会用到纹理坐标和计算机系统的坐标的转换。

### 纹理创建与绑定

下面我们来看看如何加载一张图片作为OpenGL中的纹理。首先要在显卡中创建一个纹理对象，OpenGL ES提供了方法原型如下：

```plain
void glGenTextures (GLsizei n, GLuint* textures)

```

这个方法中的第一个参数是需要创建几个纹理对象，第二个参数是一个数组（指针）的形式，函数执行之后会将创建好的纹理句柄放入到这个数组中。如果仅仅需要创建一个纹理对象的话，只需要声明一个GLuint类型的texId，然后将这个纹理ID取地址作为第二个参数，就可以创建出这个纹理对象，代码如下：

```plain
glGenTextures(1, &texId);

```

执行完上面这个指令之后，OpenGL引擎就会在显卡中创建出一个纹理对象，并且把这个纹理对象的句柄存储到texId这个变量中。

那接下来我们要对这个纹理对象进行操作，具体应该怎么做呢？OpenGL ES提供的都是类似于状态机的调用方式，也就是说在对某个OpenGL ES对象操作之前，先进行绑定操作，然后接下来所有操作的目标都是针对这个绑定的对象进行的。对于纹理ID的绑定调用代码如下：

```plain
glBindTexture(GL_TEXTURE_2D, texId);

```

执行完上面这个指令之后，OpenGL ES引擎认为这个纹理对象已经处于绑定状态，那么接下来所有对于纹理的操作都是针对这个纹理对象的了，当我们操作完毕之后可以调用如下代码进行解绑：

```plain
glBindTexture(GL_TEXTURE_2D, 0);

```

上面这行指令执行完毕之后，就代表我们不会对texId这个纹理对象做任何操作了，所以上面这行代码一般在一个GLProgram执行完成之后调用。

那一般对纹理的操作或者设置有哪些呢？

首先就是纹理的过滤方式，当纹理对象被渲染到物体表面上的时候，纹理的过滤方式指定纹理的放大和缩小规则。实际上，是OpenGL ES的绘制管线中将纹理的元素映射到片元这一过程中的映射规则，因为纹理（可以理解为一张图片）大小和物体（可以理解为手机屏幕的渲染区域）大小不太可能一致，所以要指定放大和缩小的时候应该具体确定每个片元（像素）是如何被填充的。

放大（magnification）规则的设置：

```plain
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

```

缩小（minification）规则的设置：

```plain
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);

```

上述两个指令设置的过滤方式都是GL\_LINEAR，这种过滤方式叫做双线性过滤，底层使用双线性插值算法来平滑像素之间的过渡部分，OpenGL的具体实现会使用四个邻接的纹理元素，并在它们之间用一个线性插值算法做插值，这种过滤方式是最常用的。

OpenGL还提供了GL\_NEAREST的过滤方式，GL\_NEAREST被称为最邻近过滤，底层为每个片段选择最近的纹理元素进行填充，缺点就是当放大的时候会丢失掉一些细节，会有很严重的锯齿效果。因为是原始的直接放大，相当于降采样。而当缩小的时候，因为没有足够的片段来绘制所有的纹理单元，也会丢失很多细节，是真正的降采样。

其实OpenGL还提供了另外一种技术，叫做MIP贴图，但是这种技术会占用更多的内存，优点是渲染也会更快。当缩小和放大到一定程度之后效果也比双线性过滤的方式更好，但是它对纹理的尺寸以及内存的占用是有一定限制的。不过，在处理以及渲染视频的时候不需要放大或者缩小这么多倍，所以在这种场景下MIP贴图并不适用。

综合对比这几种过滤方式，在使用纹理的过滤方式时我们一般都会选用双线性过滤的过滤方式（GL\_LINEAR）。

接下来，我们看纹理对象的另外一个设置，也就是在纹理坐标系中的s轴和t轴超出范围的纹理处理规则，常见的代码设置如下：

```plain
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

```

上述代码表示的含义就是，给这个纹理的s轴和t轴的坐标设置为GL\_CLAMP\_TO\_EDGE类型，代表所有大于1的像素值都按照1这个点的像素值来绘制，所有小于0的值都按照0这个点的像素值来绘制。除此之外，OpenGL ES还提供了GL\_REPEAT和GL\_MIRRORED\_REPEAT的处理规则，从名字也可以看得出来，GL\_REPEAT代表超过1的会从0再重复一遍，也就是再平铺一遍，而GL\_MIRRORED\_REPEAT就是完全镜像地平铺一遍。

现在，我们创建出了一个纹理对象，并对这个纹理对象进行了一系列的设置，接下来就到关键的地方了，就是将内存中的一个图片数据上传到这个纹理对象中去。

### 纹理的上传与下载

假设我们有一张PNG类型的图片，我们需要将它解码为内存中RGBA裸数据，所以首先我们需要解码。可以采用跨平台（C++层）的方式，引用libpng这个库来进行解码操作，当然也可以采用各自平台的API进行解码。无论哪一种方式，最终都可以得到RGBA的数据。等拿到RGBA的数据之后，记为uint8\_t数组类型的pixels。

接下来，就是要将PNG素材的内容放到这个纹理对象上面去了，如何上传到纹理上面去呢？代码如下：

```plain
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
        GL_UNSIGNED_BYTE, pixels);

```

执行上述指令的前提是我们已经绑定了某个纹理，OpenGL的大部分纹理一般只接受RGBA类型的数据。当然在视频场景下，考虑性能问题也会使用到GL\_LUMINANCE类型，不过需要在片元着色器中，把YUV420P格式转换成RGBA格式。上述指令正确执行之后，RGBA的数组表示的像素内容会上传到显卡里面texId所代表的纹理对象中，以后要使用这个图片，直接使用这个纹理ID就可以了。

既然有内存数据上传到显存的操作，那么一定也会有显存的数据回传回内存的操作，这个应该如何实现呢？代码如下：

```plain
glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels);

```

执行上述指令的前提是我们已经绑定了某个纹理，然后将绑定的这个纹理对象代表的内容拷贝回pixels这个数组中，这个拷贝会比较耗时，并且拷贝时间会和分辨率（width\\height）大小成正比。一般在实际的开发工作中要尽量避免这种内存和显存之间的数据拷贝与传输，而是使用各个平台提供的快速映射API去完成内存与显存的拷贝工作。

## 物体坐标与纹理绘制

通过刚刚的操作，我们已经准备好了一个纹理，那么如何把这张图片（纹理）绘制到屏幕上呢？在实际绘制之前，我们还需要了解一下一下OpenGL中的物体坐标系。

### 物体坐标系

如图所示，OpenGL规定物体坐标系中X轴从左到右是从-1到1变化的，Y轴从下到上是从-1到1变化的，物体的中心点是(0, 0)的位置。

![图片](https://static001.geekbang.org/resource/image/97/5f/97e9ecff3314d71ffbb429d301b60a5f.png?wh=1920x1063)

接下来的任务就是将这个纹理绘制到物体（屏幕）上，首先要搭建好各自平台的OpenGL ES的环境，包括上下文与窗口管理，然后创建显卡可执行程序，最终让程序跑起来。

### 纹理的绘制

先来看一个最简单的顶点着色器（Vertex Shader），代码如下：

```plain
static char* COMMON_VERTEX_SHADER =
      "attribute vec4 position;                   \n"
      "attribute vec2 texcoord;                   \n"
      "varying vec2 v_texcoord;                   \n"
      "                                            \n"
      "void main(void)                              \n"
      "{                                              \n"
      "   gl_Position = position;                 \n"
      "   v_texcoord = texcoord;                  \n"
      "}                                              \n";

```

片元着色器（Fragment Shader），代码如下：

```plain
static char* COMMON_FRAG_SHADER =
      "precision highp float;                                       \n"
      "varying highp vec2 v_texcoord;                               \n"
      "uniform sampler2D texSampler;                                \n"
      "                                                               \n"
      "void main() {                                                 \n"
      "    gl_FragColor = texture2D(texSampler, v_texcoord);      \n"
      "}                                                                                                                                       \n";

```

利用上面两个Shader创建好的这个Program，我们记为mGLProgId。接下来我们需要将这个Program中的重点属性以及常量的句柄寻找出来，以备后续渲染过程中向顶点着色器和片元着色器传递数据。

```plain
mGLVertexCoords = glGetAttribLocation(mGLProgId, "position");
mGLTextureCoords = glGetAttribLocation(mGLProgId, "texcoord");
mGLUniformTexture = glGetUniformLocation(mGLProgId, "texSampler");

```

在这个例子里，我们要从Program的顶点着色器中读取两个attribute，并放置到全局变量的mGLVertexCoords与mGLTextureCoords中，从Program的片元着色器中读取出来的uniform会放置到mGLUniformTexture这个变量里。

所有准备工作都做好了之后，接下来进行真正的绘制操作。

首先，规定窗口大小：

```plain
glViewport(0, 0, screenWidth, screenHeight);

```

函数中的参数screenWidth表示绘制View或者目标FBO的宽度，screenHeight表示绘制View或者目标FBO的高度。

然后使用显卡绘制程序：

```plain
glUseProgram(mGLProgId);

```

设置物体坐标与纹理坐标：

```plain
GLfloat vertices[] = { -1.0f, -1.0f, 1.0f, -1.0f, -1.0f, 1.0f, 1.0f, 1.0f };
glVertexAttribPointer(mGLVertexCoords, 2, GL_FLOAT, 0, 0, vertices);
glEnableVertexAttribArray(mGLVertexCoords);

```

设置纹理坐标：

```plain
GLfloat texCoords1[] = { 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 1.0f, 1.0f, 1.0f };
GLfloat texCoords2[] = { 0.0f, 1.0f, 1.0f, 1.0f, 0.0f, 0.0f, 1.0f, 0.0f };
glVertexAttribPointer(mGLTextureCoords, 2, GL_FLOAT, 0, 0,  texCoords2);
glEnableVertexAttribArray(mGLTextureCoords);

```

代码中有两个纹理坐标数组，分别是texCoords1与texCoords2，最终我们使用的是texCoords2这个纹理坐标。因为我们的纹理对象是将一个RGBA格式的PNG图片上传到显卡上，其实上传上来本身就需要转换坐标系，这两个纹理坐标恰好就是做了一个上下的翻转，从而将计算机坐标系和OpenGL坐标系进行转换。对于第一次上传内存数据的场景纹理坐标一般都会选用texCoords2。但是如果这个纹理对象是OpenGL中的一个普通纹理对象的话，则需要使用texCoords1。

接下来，指定我们要绘制的纹理对象，并且将纹理句柄传递给片元着色器中的uniform常量：

```plain
glActiveTexture(GL_TEXTURE0);
glBindTexture(GL_TEXTURE_2D, texId);
glUniform1i(mGLUniformTexture, 0);

```

执行绘制操作：

```plain
glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

```

上述这行指令执行成功之后，就相当于将最初内存中的PNG图片绘制到默认的FBO上去了，最终再通过各平台的窗口管理操作（Android平台的swapBuffer、iOS平台的renderBuffer），就可以让用户在屏幕上看到了。

当确定这个纹理对象不再使用了，则需要删掉它，执行代码是：

```plain
glDeleteTextures(1, &texId);

```

如果不调用这个方法，就会造成显存的泄露。同时调用删除纹理对象的时候，也必须要在OpenGL线程中进行操作。

除此之外，关于纹理的绘制我们还要额外注意一点： **我们提交给OpenGL的绘图指令并不会马上送给图形硬件执行，而是会放到一个指令缓冲区中。** 考虑性能的问题，等缓冲区满了以后，这些指令会被一次性地送给图形硬件执行，指令比较少或比较简单的时候，是没办法填满缓冲区的，所以这些指令不能马上执行，也就达不到我们想要的效果。因此每次写完绘图代码，想让它立即完成效果的时候，就需要我们自己手动调用glFlush()或gLFinish()函数。

- glFlush：将缓冲区中的指令（无论是否为满）立刻送给图形硬件执行，发送完立即返回；
- glFinish：将缓冲区中的指令（无论是否为满）立刻送给图形硬件执行，但是要等待图形硬件执行完后这些指令才返回。

在遇到绘图指令不能马上执行时，手动调用这两个函数可能会解决我们的问题。

## 小结

![图片](https://static001.geekbang.org/resource/image/d6/b7/d604739781322a99ac3c76da398467b7.png?wh=1920x933)

到这里，我们整个移动平台视频渲染部分的内容就学完了。最后，我们一起来回顾一下吧！

我们从视频渲染的技术选型开始，给你介绍了几种视频渲染的技术手段并且分析了各自的优缺点，最终选择OpenGL ES作为我们这个部分的学习重点，但是要想完全弄懂OpenGL ES并实际上手操作，确实比较难。

所以这个部分我带着你从它的概念、用途开始，然后逐步了解它内部的运行机制和GLSL语法，并且创建出了一个GLProgram，继而在各个平台上搭建出OpenGL ES的上下文环境，最后让这个GLProgram运行到了搭建的上下文环境中。你可以结合这个思维导图来回顾一下我们这部分的重点内容。

![图片](https://static001.geekbang.org/resource/image/0c/b9/0c494e8fcf68eec795266f84f5b831b9.png?wh=1920x1546)

## 思考题

打开 [GPUImage](https://github.com/BradLarson/GPUImage) 这个项目，阅读一下GPUImage这个框架，然后描述出这个框架的整体设计思路，你可以带着以下几个问题去思考。

1. GPUImage是如何构建上下文的？
2. GPUImage中对于和OpenGL ES相关的API是如何抽象的？
3. GPUImage核心的架构是如何设计的？
4. GPUImage中的共享上下文是如何实现的？
5. GPUImage中的TextureCache存在的意义是什么？

欢迎你在评论区留下自己的见解，也欢迎你把这节课分享给需要的朋友，我们下节课再见！