你好，我是叶伟民。

开篇词里面我们提过，RAG是传统软件开发人员加入AI浪潮的最快之路，但是这条路里面又分三条小路。

第一条是最容易想到的，就是直接跳槽换一份RAG工作（比如做大模型应用开发），这条路成功率最小。第二条，就是在现有公司/团队里面开一个全新的RAG项目，这条路成功率高一点，但是还是有难度，这个方案我们下一章再探讨。

使用RAG改造自己所处的项目，这条路成功率最高，难度最小，因此我们安排在最前面讲解，也就是我们第一章要学习的实战案例——传统MIS系统的RAG改造。

今天这一讲，我们就先睹为快，看看传统MIS系统使用RAG改造前后的模样，同时搞定一些环境准备工作，方便我们把MIS系统乃至整个课程的配套代码运行起来。

## 用RAG改造传统MIS系统的收益

我们如果单纯出于自己想加入AI浪潮的私心，就想推进一个RAG改造项目，这样是很难获得上级或者客户等利益相关者同意的。我们必须要让他们看到改造系统所带来的收益，才可能让他们同意我们改造。

那么使用RAG改造传统MIS系统有什么收益呢？最直观的一个收益就是可以（大幅）减少用户的操作步骤和操作时间，提高用户的工作效率。

## 项目改造入手点

那么如何入手改造项目，才能减少用户的操作步骤和操作时间，提高用户的工作效率呢？我们先从日常最熟悉的查询操作说起。

### 查询数据

具体来说，原来的MIS系统想查询一条数据要经过以下步骤。

1. 找到数据查询界面入口，总计1个步骤。
2. 打开数据查询界面，总计1个步骤。
3. 输入N种查询条件，总计N个步骤。
4. 点击“查询”按钮。

总计是2+N+1个步骤，有没有更快更方便的方法呢？如果用户可以使用自然语言查询，理想状态下只需要1个步骤，总计可以减少N+2个步骤。N越多，用户的操作步骤和操作时间减少得越多。

另外如果可以结合准确率高的语音输入法，那么用户节省的时间更多。既然查询部分改成了自然语言，那么录入数据部分也可以相应地改为自然语言录入。

### 录入数据

查询数据提升效率的思路找到了，我们很容易想到录入数据也能做相似的改造。

传统MIS系统里，录入一条数据要经过以下步骤。

1. 找到数据管理界面入口，一般需要1个步骤。
2. 打开数据管理界面，总计1个步骤。
3. 点击“新建”按钮，总计1个步骤。
4. 录入数据，每个输入控件可能都要操作一遍，假设有N个输入控件，那么总计N个步骤。
5. 点击“保存”按钮。

总计3+N+1个步骤，如果用户可以使用自然语言录入数据，理想状态下只需要1个步骤，总计可以减少N+3个步骤。同样，N越多，用户的操作步骤和操作时间减少得越多。

### 语音输入

另外，结合准确率高的语音输入法，那么能为用户节省的时间就会更多。既然录入部分改成了自然语言，那么修改数据和删除数据部分也可以相应地改为自然语言。

不过语音输入法属于操作系统配置部分，不属于软件应用开发部分，这里提到这个，更多是为了启发你的思路。

接下来，我们看看这个实战案例所要改造的MIS系统。

## 传统的MIS系统

这里我们使用一个ERP系统来代表传统的MIS系统。我们以其中一个子模块：“销售管理”下面的“销售对账”为例。

### 录入数据

我们先看看录入数据部分，直观感受一下录入的操作流程。

第一步，我们需要点开左边的“销售管理”菜单。

![](https://static001.geekbang.org/resource/image/f8/2b/f8d1baf82178bff10de6b06cf46ee02b.jpg?wh=2010x514)

点开之后，进入第二步，点击“销售对账”子菜单。

![](https://static001.geekbang.org/resource/image/24/80/24129a307c80206f59f63ee9e9724180.jpg?wh=2010x495)

进入“销售对账”页面，继续第三步，点击页面主要部分左上角的“添加”按钮。

![](https://static001.geekbang.org/resource/image/80/a6/80639cd7ff8907820ab33d5139c83da6.jpg?wh=2010x499)

第四步，进入“添加数据”页面，操作N个输入控件。

![](https://static001.geekbang.org/resource/image/5b/14/5b4f55a594ac9e6be3f77569c77aef14.jpg?wh=2010x505)

然后点击“提交”按钮。

![](https://static001.geekbang.org/resource/image/27/56/27b593a92c3bc050083bcb19a98c3756.jpg?wh=2010x507)

经过3+N+1个步骤之后，我们终于录入完一条数据。

## 使用RAG改造之后

我们将以上模块使用RAG改造之后，理想状态下将只需要两个步骤：第一步，输入你的问题。第二步，点击“提交”按钮。然后系统会解析你输入的内容，将其转化为数据录入系统。

![](https://static001.geekbang.org/resource/image/7f/b3/7fe48c8ea61a26081eca12a73025bab3.jpg?wh=2010x509)

## 查询数据

我们再来看看查询数据的操作。第一步，我们需要点开左边的“销售管理”菜单。

![](https://static001.geekbang.org/resource/image/0a/37/0aeec869d9e5f039yy53c23f5007c037.jpg?wh=2010x514)

点开之后，进入第二步，点击“销售对账”子菜单。

![](https://static001.geekbang.org/resource/image/04/0b/045b8a965c40ef9413698381e88ed30b.jpg?wh=2010x1118)

第三步，进入“销售对账”页面后，在N个输入控件输入查询条件。

![](https://static001.geekbang.org/resource/image/92/e0/920c066yy10c5a8f59a68c1d38c907e0.jpg?wh=2010x499)

点击“搜索”按钮，系统将返回查询结果。

![](https://static001.geekbang.org/resource/image/1d/d1/1defecbce2ddf278bd72482fe3cb25d1.jpg?wh=2010x498)

经过2+N+1个步骤之后，我们终于可以查询出数据了。

## 使用RAG改造之后

我们使用RAG改造以上模块之后，理想状态下只需要两个步骤就能查询数据了。

第一步，输入你的问题。第二步，点击“提交”按钮。然后系统会解析你输入的内容，将其转化为具体的查询条件来查询出数据。

![](https://static001.geekbang.org/resource/image/7f/b3/7fe48c8ea61a26081eca12a73025bab3.jpg?wh=2010x509)

现在通过改造前后的比较，我们明显看出通过RAG改造传统MIS系统可以提升用户的工作效率。我们可以通过这点，说服用户等利益相关者同意使用RAG改造传统MIS系统。

细心的同学应该注意到了，即使使用RAG改造了传统MIS系统，我们也依旧保留了传统MIS系统的界面。是的，使用RAG将系统改造到可以替换的程度，并非短期可以完成的工作。即使完成了，根据经验，还是会有部分用户坚持使用传统界面，所以我们还需要保留传统界面，这样 **遇到RAG不能很好工作的时候，用户还能够通过传统界面完成任务**。

## 安装先决软件和配置环境

我们约定使用Windows 11这个操作系统，为了把这个MIS系统运行起来，我们先需要安装以下软件。

1. Python 3.9
2. Miniconda（或Anaconda）

Python相信各位同学都不陌生，这里就不做介绍了。这里我们着重了解一下Miniconda或Anaconda，因为我们整个课程里都将使用Miniconda或Anaconda。

### 为什么要使用Miniconda或Anaconda

Miniconda或Anaconda是两种常用的Python发行版，我们整个课程将使用它们来创建Python的虚拟环境。

任何软件开发项目都会遇到依赖冲突、全局环境混乱、升级难题等问题，那么如何解决这些问题呢？Java使用Maven，.NET使用NuGet，Python则使用虚拟环境。

## 虚拟环境概述

虚拟环境是一种用于创建隔离的Python环境的方法。每个虚拟环境都有自己的Python解释器和一套独立的Python库。使用虚拟环境可以带来以下好处。

1. **依赖管理：** 在虚拟环境中，你可以为不同的项目安装不同的库和库的版本，而不会相互冲突。
2. **版本控制：** 你可以为每个虚拟环境指定一个Python版本，这样即使全局环境中的Python版本更新了，你的项目仍然可以使用特定版本的Python。
3. **避免全局污染：** 在全局环境中安装太多包可能会导致依赖问题和版本冲突。虚拟环境可以避免这些问题，因为每个环境都是独立的。
4. **开发和生产一致性：** 你可以在本地开发环境中使用与生产环境相同的依赖和配置，从而确保代码在不同环境中的行为一致。
5. **安全性：** 虚拟环境可以限制对全局系统的更改，从而提高安全性。
6. **灵活性：** 你可以为不同的项目创建多个虚拟环境，每个环境都可以根据项目需求定制。

我们可以使用以下工具创建和管理虚拟环境。

- **venv**：Python标准库中包含的虚拟环境工具，从Python 3.3版本开始提供。
- **virtualenv**：一个第三方工具，用于创建隔离的Python环境，可以与Python 2.x版本一起使用。
- **Conda**：作为Anaconda的一部分，Conda也可以用来创建和管理虚拟环境，但它提供了更多的功能，如包管理和跨语言支持。

使用虚拟环境是Python开发中的最佳实践之一，它可以帮助开发者管理项目依赖，确保项目的可移植性和可重复性。

## 初识Conda

Conda也有分两个版本，一个是完整版本Anaconda，一个是精简版本Miniconda。

Anaconda是一个打包的集合，里面预装好了conda、某个版本的python、众多包、科学计算工具等等，就是把很多常用的、不常用的库都给你装好了。

而Miniconda是Anaconda的精简版。Miniconda只包含最基本的Conda包管理器和Python解释器。由于Miniconda体积较小，它适合于那些只需要Conda包管理功能的用户。用户可以根据自己的需要，通过Conda安装所需的包和库。Miniconda可以节省磁盘空间，并且启动速度更快。它提供了更多的灵活性来选择安装哪些包。

## 安装Miniconda

如果你没有安装Anaconda，就可以按照下面的操作完成Miniconda的安装。如果你之前安装过Anaconda，直接使用就可以了，可以跳过安装这一步。

首先，我们使用浏览器打开 [https://mirrors.tuna.tsinghua.edu.cn/](https://mirrors.tuna.tsinghua.edu.cn/)。

然后搜索anaconda，点击搜索到的anaconda链接。

![](https://static001.geekbang.org/resource/image/9b/48/9beb49c80606caf7a8142bac9d897748.jpg?wh=1990x321)

然后点击miniconda。

![](https://static001.geekbang.org/resource/image/64/3d/648e885d02246540ebb0a24e4755673d.jpg?wh=1940x521)

之后点击 [Miniconda3-py39\_23.5.2-0-Windows-x86\_64.exe](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_23.5.2-0-Windows-x86_64.exe) 下载。

![](https://static001.geekbang.org/resource/image/76/79/7603d89cb790db2e6811b819f9540e79.jpg?wh=1930x330)

下载之后，一路按默认安装即可。

### 确认Miniconda已经安装和配置正确

如果一切顺利，这时候我们点击开始菜单，输入conda，应该弹出以下界面。

![](https://static001.geekbang.org/resource/image/6d/1e/6db8b680d00f5943ea6c1f2c979b681e.jpg?wh=1916x412)

我们点击Anaconda Powershell Prompt，应该弹出以下界面。

![](https://static001.geekbang.org/resource/image/2b/0c/2ba0c6930f02199488638bd9bc99d30c.jpg?wh=1939x137)

然后我们输入conda --version，应该弹出以下界面，这时就说明安装成功了。

![](https://static001.geekbang.org/resource/image/4d/38/4df4b7098040126f0558eaa63934yy38.jpg?wh=1942x200)

## 虚拟环境搭建&系统运行

安装完Miniconda之后，我们最后还要搭建虚拟环境，并把MIS系统运行起来。

### 创建虚拟环境

首先我们来创建虚拟环境。继续使用我们刚才打开的 `Anaconda Powershell Prompt`，输入下面的命令：

```powershell
conda create -n rag1 python=3.9

```

这里的 `rag1` 是虚拟环境的名称。

![](https://static001.geekbang.org/resource/image/e0/35/e0a39b7b7151c5763b3d95902212d835.jpg?wh=1944x336)

当弹出以下提示时，输入 `y`。

![](https://static001.geekbang.org/resource/image/ec/y2/ec475a488984e50886a307f56c566yy2.jpg?wh=1931x193)

然后我们创建一个虚拟环境 `rag1`。如果一切顺利，将会出现以下界面。

![](https://static001.geekbang.org/resource/image/95/c1/95ffde79585bdbda6ee35c489a1cafc1.jpg?wh=1944x1041)

### 激活虚拟化境

环境创建好以后，需要激活才能使用。输入以下命令即可激活虚拟环境。

```powershell
conda activate rag1

```

如果一切顺利，命令行开头的 `base` 将会变成 `rag1`。

![](https://static001.geekbang.org/resource/image/70/88/70faf77fd5bc2yy7d19ca83b99b84f88.jpg?wh=1941x181)

### 下载源代码

激活了虚拟环境之后，我们到 [这里](https://github.com/weiminye/time-geekbang-org-rag) 下载这一章的配套源代码。

### 安装依赖

下载和解压完源代码之后，回到我们刚才打开的 `Anaconda Powershell Prompt`，输入cd命令进入源代码解压后的目录，然后再进入。

```python
cd 源代码解压后的目录
cd 实战案例1\改造前

```

然后再输入以下命令安装所有依赖。

```powershell
pip install -r requirements.txt

```

### 运行MIS系统

所有依赖安装完毕后，我们输入命令运行系统。

```powershell
python manage.py migrate
python manage.py runserver

```

如果一切顺利，将会显示如下界面。

![](https://static001.geekbang.org/resource/image/9a/81/9af6d454082c54db8cb27d1538f09281.jpg?wh=1940x458)

### 确认MIS系统可以正常运行

这时候我们打开浏览器，访问 [http://127.0.0.1:8000/，应该会出现以下页面。](http://127.0.0.1:8000/%EF%BC%8C%E5%BA%94%E8%AF%A5%E4%BC%9A%E5%87%BA%E7%8E%B0%E4%BB%A5%E4%B8%8B%E9%A1%B5%E9%9D%A2%E3%80%82)

![](https://static001.geekbang.org/resource/image/3a/32/3a7f5afcbba7e90e00c2f60b4b1e4c32.jpg?wh=1786x756)

至此，我们的MIS系统可以正常运行了。

## 小结

好了，今天这一讲到这里就结束了，最后我们来回顾一下今天的学习成果。

这一讲我们学会了三件事情。

第一件事，讨论了如何说服利益相关方，同意我们推动项目的RAG改造，并且分析了改造的切入点。

第二件事，展示了这个实战案例改造前后的模样，建立了感性、直观的认识。

第三件事，学习了如何把我们要改造的传统MIS系统运行起来，并且顺便搭建了整个课程所需要的环境。

好了，现在我们已经讲完改造前后的MIS系统，以及经改造后会有多方便，相信你的用户看了之后也会心动，愿意让你去改造。下一节我们开始讲这个实战案例的第一个基础概念：对话模式。

## 思考题

既然一个RAG应用无法一步到位，那么我们如何度过RAG应用不成熟的早期阶段呢？

欢迎你在留言区和我交流互动，如果这节课对你有启发，也推荐分享给身边更多朋友。