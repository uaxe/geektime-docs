你好，我是Barry。

从这节课开始，我们就进入到后端实战篇。这个章节重点培养的是我们从0到1做项目后端开发的能力。我们将经历从代码设计到具体功能的模块接口开发，深度体验独立平台搭建和后端开发的完整链路，学会灵活应用框架技术来应对多种类型的项目需求。

这节课，我们要拿下的就是后端部分的第一个核心知识点—— Flask 项目搭建。之所以选择基于Python的Flask框架，是因为它更合适用来完成视频直播平台的后端开发。

## 为什么选用Flask

为了让你知道选型的来龙去脉。我们先聊聊为什么要选用Flask框架，而不是选择使用Django这个应用也很广泛的框架呢？

这就要说到Flask和Django的区别了。首先，二者都是企业当中用的很多的Web的后端框架。接下来，我们一起来看一下二者的对比。

Flask主要有两大优点。第一个优点，它是轻量级Python开发框架。意思就是Flask核心就是几个文件，不用大量的配置文件，很快就能搭建起来一个小型的Web应用并快速启动运行，很适合搞微服务。

第二个优点就是灵活，其实这不光是Flask的优点，也是Python的优点，因为Flask是基于Python的Web应用框架。灵活的地方就在于这个框架用的人多，整体生态比较好。Flask有很多别人做好的扩展包，并且整体处在一个持续的维护和更新状态，我们可以灵活使用这些包和库做定制和扩展。它的API部分也不需要大量的配置文件和模板，几行代码就可以完成一个实现简单功能的应用。

我们可以结合后面这个例子来看看。通过这个例子，我们不难发现API开发在Flask中不复杂，几行代码就可以实现一个简单的功能。

```python
from flask import Flask, jsonify
app = Flask(__name__)
def get_weather(city):
  # 根据城市名称查询天气
  # 返回查询结果
  return {'city': city, 'weather': 'sunny'}
@app.route('/weather/<city>')
def weather(city):
  # 调用get_weather函数获取天气情况
  result = get_weather(city)
  # 将查询结果以json格式返回
  return jsonify(result)
if __name__ == '__main__':
  app.run()

```

上面这段代码里，我们定义了一个get\_weather函数，用来根据城市名称查询天气情况。我们使用了@app.route这个装饰器，把get\_weather函数绑定到 “/weather/” 的URL路径上。这样当用户去访问这个URL的时候，Flask就会自动调用get\_weather函数，并将查询结果以JSON格式返还给用户。

说完了Flask，我们再来聊一聊同样是基于Python的Web框架——Django。那么Django有什么优点呢？

首先，Django的库非常完整，就像一个工具箱一样，你想要的它都有。

其次，Django有着比较严密的架构设计，安全性也比较高，可以保护网站抵御像SQL注入这样的恶意操作。

最后，Django可以直接用Python语言对数据库进行操作，这一点也比较方便。

Django的库完整、架构设计严密这些优点，注定了它非常适用于大型的应用，比如电子商务网站。不过，Django的优点其实也算是它的缺点，因为Django架构严密，又非常完整的库，这就造成了一个问题——Django的学习成本比较高。

无论应用大小怎样，Django所需要的大量配置文件都少不了，而且占用的系统资源比较多，比如像机器性能、网路带宽等等这些资源。应用不需要的功能模块，Django也包括在内了，所以它不如Flask轻便。

我们总结下Django和Flask的区别。Django就像是一个工具箱，你要的它都有；而Flask是一把锤子，非常轻便，只要你善于使用它，就可以做出更多的、自由度更大的东西。

说到这里，我们已经明白了选用Falsk的原因。考虑到我们平台的特点，还有后端学习路径循序渐进的原则，Flask更合适一些。

## Flask知识点梳理

接下来我们就一起来看看，学习Flask都应该掌握哪些知识点。使用Flask去做项目的话，有几样技术知识需要去掌握： **Python语言、数据库和前端应用。**

想要掌握Flask，就需要我们对Python语言的应用非常熟悉。通过前面先导课的学习，对于Python语言你或多或少已经具备了一些基础。

其中需要重点掌握的就是 **Python语言应用。** 比如变量的应用、Python当中的一些控制结构语言（比如if的while、for循环等等简单的控制语句，还有像函数要怎么构造、类怎么构造，怎样使用类当中的操作等等，这些都是高频用到的知识。

第二类技术知识就是 **数据库**。从字面意思理解，数据库就是存储数据的一个仓库，能对项目中的数据进行管理和操作。因为我们的在线视频项目有很多数据，比如用户上传的视频、用户的个人信息预计日志等等，这些都需要存放的容器。而这个容器就是数据库，因此我们整个项目都不留离不开它。这里我也明确一下，数据库我们使用MySQL来实现。

第三就是 **前端应用**。前面我们刚刚完成前端语言和框架的学习，相信你已经能够使用Vue完成整个前端部分的实现了。等我们学完后端部分，就可以实现整个平台前后端的联动，完成平台整体功能的开发。

接下来就是实践环节，我们一起来完成整个Flask框架的搭建。

## 框架搭建

在开始之前，你需要先准备好项目所使用到的IDE。安装成功之后，我们再来实现Flask框架的搭建。

### 第一步：安装项目所使用的IDE

我们在后端开发中使用Pycharm这个工具，你可以直接到 [Pycharm的官网](https://www.jetbrains.com/zh-cn/pycharm/)。它的安装比较简单，你根据教程一步步操作就能搞定。这里我们需要选择community，也就是社区版本。

![图片](https://static001.geekbang.org/resource/image/f7/fd/f7699c319aaf1f36e63f47e97f7af9fd.png?wh=1920x712)

## 第二步：配置Pycharm的编译环境

下一步我们需要创建一个新的项目。在PyCharm中，一个项目对应一个文件夹。我们需要在PyCharm的欢迎界面，点击 “ **Create New Project**” 按钮，然后输入项目的名称和存放路径。

这里我给项目起的名字是 “First\_Flask”，你可以自己创建命名。点击New environment using，选择 “Virtualenv”，然后在Base interpreter中选择Python版本。这里我使用的是软件anaconda自带的Python解释器，你使用先导课中下载过的Python解释器即可。若系统未自动检测到，还需要点击右边省略号图标，找到并选中python.exe文件路径。

### 第三步：安装Flask

接下来就是安装环节。在Pycharm下方，有一个Terminal按钮，点击之后，就会弹出后面截图里的对话框。

![](https://static001.geekbang.org/resource/image/54/58/549b74760c5cd1f1e8e8768649533658.jpg?wh=2000x524)

我们使用pip命令来安装，在下方的终端——Terminal输入命令行即可。

```python
pip install flask

```

这里的pip其实是一个Python语言的包管理器，用来安装和管理Python包和依赖。

### 第四步：框架文件的搭建

由于项目会有许多的程序，我们提前设置好整个项目目录结构。后端开发中，我们需要创建文件夹来存放不同功能的代码块。

接下来，我们看看这个项目需要的Python Package。我们先把基础的几个文件夹建好。每个文件夹的作用你可以参考后面的表格，之后我们有其他需要再创建即可。我画了一张表，帮你梳理了整个api文件下的项目目录。

![](https://static001.geekbang.org/resource/image/3f/72/3f58f4678cd2a186f5dc1957fb4a9772.jpg?wh=3030x2030)

后面是对应的项目目录图，你可以对照图片来了解文件之间的层级关系。

![](https://static001.geekbang.org/resource/image/f5/83/f58737d7d40b99029811fb70d0221183.jpg?wh=2600x509)![](https://static001.geekbang.org/resource/image/43/55/43a12e9e0642f2e4f1dc0f43b18d3255.jpg?wh=2000x487)

对于model文件夹中的内容，主要存放的是admin，video，message等项目文件。

![](https://static001.geekbang.org/resource/image/f0/6f/f06617057f4de15279f1dbe8f31ca86f.jpg?wh=2463x678)

下面进入实战环节，我们通过简单的案例尝试在浏览器中输出打印hello word，借此感受一下Flask的魅力。

我们先来新建一个hello\_word的Python文件。只需要在项目文件下面直接创建即可，对应的代码参考如下。

```python
from flask import Flask    # 导入Flask模块
app = Flask(__name__)      # 创建Flask实例，并指定模块名
@app.route('/')                 # 定义路由，即当访问 根目录 时返回下面的函数结果
def hello_world():
    return 'Hello, World!'   # 返回字符串Hello, World!
if __name__ == '__main__':
    app.run()                       # 运行Flask应用程序

```

请注意，写在最后的if **name** == ‘ **main**’ 方法中 **name** 表示当前模块名，如果是直接运行的Python脚本，则为 **main**，所以该判断语句整体的作用是判断当前模块是否为主模块，如果是则执行下面的语句。

接着，我们一起来看看运行结果，运行完前面那段代码，在Pycharm的终端就会显示后面截图这样的运行结果，生成一个URL。

![](https://static001.geekbang.org/resource/image/da/32/da4f8b0a32262d0d15361c26cf956632.jpg?wh=2000x487)

紧接着，你需要在浏览器中输入该地址，然后就可以看到对应的效果了。

![](https://static001.geekbang.org/resource/image/70/bb/70c246ea391547380e0418b999db79bb.jpg?wh=1623x554)

到这里，我们就完成了Flask框架的搭建，并且完成了一个简单的案例测试。建议你在课后用配套代码亲自动手练习一下，这样学习效果会更好。

## 总结

课程接近尾声了，我来带你对今天学到的内容做一个回顾总结。

我们先是比较了Flask和Django两种框架的特点。结合我们平台的需要和学习路径的合理性，我们最终选择了更合适做视频直播平台后端开发的Flask框架。

之后，我带你梳理了掌握Flask必备的技术知识，包括Python基础应用和数据库操作等，虽然这一部分我们已经在先导课学过了，但如果想更熟练地应用框架，还是建议你课后继续强化练习。

最后，通过Flask框架的搭建实操，我们一起演练了Flask安装到项目搭建的整个过程。至于hello word这个简单案例，其实也是为后续我们使用Flask开发后端做一个预热，后续课程里我们还会让Flask发挥更大的价值。

## 思考题

你可以尝试设置两个路由，实现——用户输入不同URL，页面显示不同内容。

期待你在留言区和我交流互动。如果觉得这节课的内容实用有趣，不妨推荐给你的伙伴，和他一起学习进步。