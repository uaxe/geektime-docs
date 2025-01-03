你好，我是黄鸿波。

上一节课我们讲解了什么是爬虫以及爬虫的基本原理，从这节课开始，我们就要实际地去爬取一些网络上的内容，为后续推荐系统的使用做准备。

这节课我们来深入了解一下Python中的常见爬虫框架：Scrapy框架。我们将学习什么是Scrapy框架、它的特点是什么以及如何安装和使用它。

## Scrapy框架概览

Scrapy是一个适用于Python的快速、高层次的屏幕抓取和Web抓取框架，用于抓取Web站点并从页面中提取结构化的数据。它也提供了多种类型爬虫的基类，如BaseSpider、Sitemap爬虫等。我们可以很方便地通过 Scrapy 框架实现一个爬虫程序，抓取指定网站的内容或图片。

![](https://static001.geekbang.org/resource/image/67/87/67220e129b726a764fa62f28fb46e587.png?wh=1200x482)

下面是Scrapy框架的架构图。

![](https://static001.geekbang.org/resource/image/02/b8/02ce18db3937d494e05ddcbdd60ee1b8.png?wh=1766x1039)

通过这张图我们可以看到，Scrapy框架总共分成了下面七个部分。

1. Scrapy Engine（Scrapy引擎）。
2. Scheduler（调度器）。
3. Downloader（下载器）。
4. Spiders（爬虫）。
5. Item Pipline（管道）。
6. Downloader Middlewares（下载中间件）。
7. Spider Middlewares（Spider中间件）。

接下来，我们来看看这七个部分的具体含义，以及它们是如何协作的。

**Scrapy Engine** **：** Scrapy引擎是整个Scrapy框架的核心，负责所有子模块间的调度、通信和数据传递等，我们可以把它看作整个Scrapy框架的总指挥。

**Spider**：它负责处理所有的responses。也就是说，当爬虫程序获取到服务器端的response响应之后，接下来就会交由Spider去处理，它会根据需求提取数据和相应的URL信息，并交给引擎。值得注意的是，Spider模块虽然是Scrapy框架自带的模块，但是它仍然需要开发者自己手写代码实现。

**Scheduler**：调度器负责接收引擎发送过来的requests请求，并将它们放入到队列当中，在后续引擎有需要的时候再将请求返回给引擎。我们可以理解为下一步要抓取的网址由它决定，同时，在调度器里还会自动去掉重复的网址。

**Downloader**：下载器主要负责下载Scrapy Engine发送过来的所有requests请求，并将获取到的responses信息经 Scrapy Engine 返回给Spider处理。

**Item Pipeline**：管道，主要负责处理Spider中获取到的item并进行后期处理，比如对数据进行分析、过滤、存储等。

**Downloader Middlewares**：下载中间件，开发者可以在这里自定义扩展下载功能的组件。

**Spider Middlewares**：Spider中间件，可以自定义request请求和进行response过滤的组件。

了解了这七个组件的功能之后，我们来看看各组件的工作流程。在上面这张图中，我们可以看到核心的位置是引擎。也就是说基本所有的流程都和引擎相关，借助Scrapy框架爬取信息大致可以分为下面六步。

1. 爬虫程序工作的时候会经由引擎向Spider提出申请，索要第一个待爬取的URL。待引擎拿到URL之后，就将这个URL传入调度程序Scheduler。
2. Scheduler会将需要下载的URL加入到队列中，形成一个URL队列。当Scheduler完成请求后，会取出队列中的第一个URL，将其返回给引擎。
3. 引擎拿到URL之后，会将这个URL经由Downloader Middlewares交给Downloader。完成下载后，我们会得到服务端返回来的response对象。
4. 当Downloader拿到了response对象之后，接下来要做的就是把它交给引擎，然后引擎再经由Spider Middlewares将response结果交给Spider文件。
5. Spider文件处理和分析response的结果，在此基础上拿到我们想要的数据，这里一般要做的就是标签解析、内容提取等工作。
6. 解析完数据之后，我们要把这些数据经由Item Pipeline存储起来。无论是存文件还是存数据库，理论上都是由这一个组件来完成。

完成上面六个步骤之后，我们的第一个链接爬虫工作就结束了。紧接着，我们会循环这个操作，直至拿到我们要爬取的所有文件为止（也就是直到URL列表空了），这时我们就完成了一整套爬虫工作。

## Scrapy框架的安装和使用

了解了Scrapy框架的工作原理，我们就可以更好地安装和使用 Scrapy 。

Scrapy在Python中被当作一个库来使用，要想在Python中使用Scrapy，首先我们要安装Scrapy。而要在Python中安装各种各样的库，我推荐使用Anaconda来进行Python环境的管理。

### 安装Anaconda环境

Anaconda是一个开源的Python发行版本，它包括Conda、Python以及一大堆安装好的工具包，比如：Numpy、Pandas等。我们可以把Anaconda看作是一个常用的扩展库的集合，我们可以使用Anaconda很轻松地管理我们的扩展库，还可以使用Anaconda创建多个虚拟环境。每个虚拟环境都是独立的，我们可以在各个环境上分别安装独立的包。

Anaconda安装包的获取方式有很多，我们首先想到的肯定是从官网下载。不过，我个人建议从清华源下载，因为在国内访问清华源速度相对较快，下载起来比较容易。我们直接百度搜索Anaconda清华源，或者输入以下网址即可。

```
https://mirrors.bfsu.edu.cn/anaconda/archive/

```

在这里，我们下载的版本为2022.05-Windows-x86\_64。

![](https://static001.geekbang.org/resource/image/15/72/150fd5bd54d78894bbd59d2f4595be72.png?wh=1364x1792)

下载完成之后，我们双击安装包进行安装。

![](https://static001.geekbang.org/resource/image/d9/8f/d958fcc27c37788b7dbbb892d3yyc08f.png?wh=738x574)

然后一路点击Next，直到选择目录那一步，你可以根据习惯选择目录，然后点击Next，出现下面的界面。

![](https://static001.geekbang.org/resource/image/49/9e/49acd833a68a154ae9b0114150d0099e.png?wh=741x575)

这里我建议把两个复选框都选中，上面的复选框是说要把Anaconda3加入到系统的环境变量中，下面的选项大意是使用Anaconda3作为默认的Python3.9，然后点击Install。安装完成后，我们在命令控制台输入conda，如果出现以下界面，说明安装完成了。

![](https://static001.geekbang.org/resource/image/aa/4d/aa63fe3372dyycefb7d292baa989254d.png?wh=2129x1229)

接下来，我们要创建一个虚拟环境。因为我们这个虚拟环境主要是用来做爬虫的，所以我们可以创建一个名为scrapy\_recommendation的虚拟环境，并指定我们使用的Python版本为3.7版本。具体做法是输入如下命令。

```
conda create -n scrapy_recommendation python==3.7

```

稍等片刻，会出现下面的界面。

![](https://static001.geekbang.org/resource/image/98/ef/98c8df3a921312398d94f8259e7yyaef.png?wh=2556x1089)

我们输入Y，开始安装，安装结束后，会弹出如下提示。

![](https://static001.geekbang.org/resource/image/cb/f3/cb437de0752bb31b4e8697e860db0cf3.png?wh=719x342)

但是这里要注意的是，它会告诉你如果要激活你的环境，需要输入conda activate scrapy\_recommendation，但是实际上在Windows中，这样输入会产生报错。

![](https://static001.geekbang.org/resource/image/4e/8e/4e1e4108589e70726387e53bc33cd48e.png?wh=825x415)

这个应该属于Anaconda的一个小Bug，因为这实际上是在Linux和Mac环境下的命令，在Windows环境下，我们直接输入activate scrapy\_recommendation即可。这个时候会有如下显示。

![](https://static001.geekbang.org/resource/image/9f/ce/9f582124d1ecd5241d460fd9799139ce.png?wh=583x110)

### 安装Scrapy环境

现在，我们的 Anaconda 环境就已经安装好了，下一步是安装Scrapy环境。实际上要在Anaconda环境中安装Scrapy很简单，只需要执行pip install scrapy即可。

等到出现如下界面时，安装就完成了。

![](https://static001.geekbang.org/resource/image/7c/d9/7c67a8c7cf0c5b04244e5cf68cb618d9.png?wh=2615x988)

我们可以通过 conda list 来查看我们已有的包。

![](https://static001.geekbang.org/resource/image/b1/fa/b102327567450a48c5d7da442eec6cfa.png?wh=830x1082)

### 使用Scrapy创建爬虫开发环境

接下来，我们就尝试使用Scrapy创建一个爬虫开发环境。

首先，我们要确定好一个我们要搭建环境的目录，我选择了I盘的geekbang作为我要搭建环境的根目录。所以我首先要做的就是切换到这个目录下。具体做法是输入如下指令。

```
cd I:\geekbang

```

切换到指定目录下之后，我们就可以创建我们的Scrapy工程了。要注意的是，我们可以直接通过Scrapy的相关命令来创建爬虫工程。因为我们准备爬取新浪新闻里的新闻数据，把它作为我们后面推荐系统的原始数据。所以我们可以创建一个工程名为sina的爬虫项目，输入如下命令。

```
scrapy startproject sina

```

创建完成项目之后，会是下图的样子。

![](https://static001.geekbang.org/resource/image/0b/80/0b47ca678b7d19155c3135f5b8dfeb80.png?wh=2088x333)

这个时候，我们进入到I:\\geekbang目录下，会发现Scrapy帮我们创建了一个名为“sina”的目录。

![](https://static001.geekbang.org/resource/image/20/60/20fba8d54353019e6e40bec938875960.png?wh=830x151)

我们进入到这个目录之后会发现，这个目录里，已经帮我们创建好了一个基础的Scrapy工程，如图所示。

![](https://static001.geekbang.org/resource/image/cb/52/cb827d02fa8ayy277a8c894d2ba9b652.png?wh=830x279)

接下来我们将项目导入到IDE环境中，然后在IDE环境里查看整体的目录结构。这里我选择了PyCharm作为我们后续所有开发的IDE。我们在PyCharm中依次点击File->open，弹出一个文件目录选择框，我们选择I:\\geekbang\\sina作为我们的项目根目录，如下图所示。

![](https://static001.geekbang.org/resource/image/a3/b7/a3563e93a571658b7f1d40b49ac6aeb7.png?wh=633x726)

然后点击OK，导入我们的项目。

需要注意的是，这个时候，我们PyCharm的开发环境是默认的，我们需要将其切换到我们所创建的Anaconda的“scrapy\_recommendation”环境下。

因此，我们要依次点击：

File->Settings->Project:sina->Python Interpreter，然后将Python Interpreter的目录选择为我们的Anaconda创建的scrapy\_recommendation环境下的python.exe文件。然后点击OK，切换环境成功。

![](https://static001.geekbang.org/resource/image/a2/cb/a267bf5e85317874459e191a8297c8cb.png?wh=1193x1006)

接下来，我们在主界面的左侧把所有的目录展开，我们来分别看一下Scrapy的各个目录以及它们的功能。

![](https://static001.geekbang.org/resource/image/ef/39/efee48abeea350eb5db293679ec07839.png?wh=334x514)

我们首先可以看到，在sina工程下面有一个同名的目录“sina”，和这个目录同一级的还有一个叫做scrapy.cfg的文件。你可以对照下面这个表格，看看这些文件的作用。

![](https://static001.geekbang.org/resource/image/c3/8f/c313c6199779a2e3ba77ed57486e628f.jpg?wh=3210x2072)

现在我们的 Scrapy 工程就创建完了。接下来我们再来创建一个爬虫程序，爬虫主要功能是爬取网站的数据。我们可以在I:\\geekbang\\sina目录下创建它，我们还是在cmd中切换到这个目录下，然后使用如下命令创建一个名为sina\_spider的爬虫程序。

```
scrapy genspider sina_spider sina.com.cn

```

这时候命令行中显示如下。

![](https://static001.geekbang.org/resource/image/10/a3/10ab2b58534e9d179041cfd37d05f6a3.png?wh=826x130)

然后我们切换到IDE中，会发现在sina\\sina\\spiders下面出现了一个名为sina\_spider.py的文件，如图所示。

![](https://static001.geekbang.org/resource/image/23/dc/2313f111c2b9347550f67bf6369291dc.png?wh=519x531)

我们打开这个文件，如果出现如下代码，说明我们这个爬虫文件创建成功了。

```
import scrapy


class SinaSpiderSpider(scrapy.Spider):
    name = 'sina_spider'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://sina.com.cn/']

    def parse(self, response):
        pass

```

进行到这里，一个基本的爬虫程序就创建完成了。但是现在离可以爬取数据还差一步，我们需要让我们的爬虫程序可以模拟人的操作来浏览网页。也就是说，我们要装一个插件来连接我们的Scrapy框架和浏览器界面，这里我推荐使用Chrome浏览器，我们需要下载的插件名称就是ChromeDriver，ChromeDriver插件的下载地址如下。

```
http://chromedriver.storage.googleapis.com/index.html

```

这个插件有很多版本，那我们是不是随便下载一个版本就可以了呢？当然不是，我们下载的版本一定要和Chrome浏览器的版本对应上。我们可以在Chrome浏览器中输入下面的命令进入设置界面。

```
chrome://settings/help

```

这时候会弹出一个关于Chrome的界面，在这个界面里可以看到我们浏览器的版本。

![](https://static001.geekbang.org/resource/image/5e/b2/5e962a6d2d9b9524e4f99c45b7304eb2.png?wh=1895x1194)

可以看到，我的版本为111.0.5563.149，所以我们回到ChromeDriver的下载界面找到110.0.5563版本进行下载，如果小版本找不到的话，就找前一个级别的版本中最后一个版本即可。

![](https://static001.geekbang.org/resource/image/6b/35/6b0cf59b49783fe832d4968952282235.png?wh=1485x1093)

这里要注意的是，我们可能找不到完全一样的版本。如果遇到这种情况，找到上一级版本号一样的插件中的最后一个版本即可。我这里对应的是110.0.5563.64，点击下载。这里适配Windows的插件只有32位的版本，但它其实没什么影响，我们即使是64位的操作系统也可以使用，正常下载即可。

![](https://static001.geekbang.org/resource/image/4e/67/4e6b1d34c8d6755a1317dbyy94cdc367.png?wh=1304x509)

下载完成之后，解压会得到一个chromedriver.exe 的文件，要把这个文件分别复制到我们的Anaconda的scrapy\_recommendation环境和Rhrome的浏览器中，如图所示。

![](https://static001.geekbang.org/resource/image/97/76/97f5639b86c2c8cb821e766a3db2b276.png?wh=831x489)

![](https://static001.geekbang.org/resource/image/3e/fe/3eyy124739f8e57301e3a8e9b0ce3bfe.png?wh=830x399)

到这里，我们的ChromDriver插件就安装好了，只有安装好这个插件，我们在爬取数据的时候才能连接上浏览器。

我们知道，要运行一个程序就要写一个主文件。一般来说这个主文件是main.py文件，所以我们在项目的根目录下创建一个名为main.py的文件，然后输入如下代码。

```
from scrapy import cmdline

cmdline.execute('scrapy crawl sina_spider'.split())

```

简单解释一下这段程序。在这段程序里，我们首先从Scrapy的包里导入了cmdline这个库，然后使用cmdline.execute执行了scrapy crawl sina\_spider。这里scrapy crawl是一个Scrapy的基础命令，表示启动爬虫程序，后面跟的是爬虫的名字。所以上面代码合起来的意思就是使用cmd命令启动名为“sina\_spider”的爬虫程序。

如果出现如下界面，说明Scrapy的基础程序是正确的。

![](https://static001.geekbang.org/resource/image/69/f3/69a87bf9d64bef8852321b9b38ac79f3.png?wh=3840x2098)

到这一步，虽然程序已经知道了要爬取的网站是sina.com.cn，现在运行也没有报错，但是似乎并没有什么结果，而且马上就关闭了。这是因为我们目前只是启动了这个爬虫程序，并没有写具体的爬虫代码，所以程序只是对sina.com.cn做了个链接，并返回了响应码200。接下来，我们就要开始正式踏上爬虫程序的编写之路了。

## 总结

我们来回顾一下本节课的主要知识点。

1. Scrapy是一个适用于Python的快速、高层次的屏幕抓取和Web抓取框架，它可以抓取Web站点并从页面中提取结构化的数据。
2. 你还应该知道Scrapy框架的原理和主要模块（Scrapy引擎、调度器、下载器、爬虫、管道、下载中间件、Spider中间件），以及它们是如何协作的。
3. 最后，我们应该有能力在Anaconda环境中创建一个Scrapy环境，搭建一个最简单的Scrapy框架并把它跑起来。

## 课后题

学完这节课，给你留两道思考题。

1. 请你自己尝试搭建一个Anaconda环境，并安装Scrapy框架相关的库。
2. 请你创建一个Scrapy的框架程序并运行它。

欢迎你在留言区与我交流讨论，我们下节课再见。