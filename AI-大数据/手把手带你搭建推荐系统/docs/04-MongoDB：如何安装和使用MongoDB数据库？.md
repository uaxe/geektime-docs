你好，我是黄鸿波。

上节课，我们主要了解了数据库的来源和形式，但凡是数据都离不开存储。说到数据库，我们最常用到的就是MongoDB和Redis。

推荐系统中的原始数据一般分成两大类，用户数据和内容数据。这两类数据服务于推荐算法，最终我们会得到用户特征与画像。对于用户画像这类的信息，最好使用字段可变的文档型数据库，比较常见的就是MongoDB数据库。

这节课我们就来详细地介绍一下MongoDB数据库。看看它是什么、有什么特点、应该如何安装。

## 什么是MongoDB数据库？

MongoDB是一个开源的基于分布式文件存储的数据库（C++语言编写），最初是为Web应用提供可扩展的高性能数据存储解决方案。MongoDB最大的优点是可扩展性强、高效的查询方式和非常出色的安全性。

![](https://static001.geekbang.org/resource/image/ec/52/ec37cf94b227833379c7152f71ce2d52.png?wh=2000x600)

### MongoDB数据库的特性

由于MongoDB开源且分布式，因此，它在可扩展性方面一直是所有NoSQL数据库中的佼佼者。MongoDB数据库可以通过分片数据来提高整个数据库的吞吐量，并且由于它以文档结构来存储数据，所以在编写和使用查询语句时非常容易。

我们这里所说的文档结构，是一种类似于JSON类型的BSON文档。在实际使用过程中，我们可以把它当作JSON的形式使用，因为这二者从使用和长相上来看基本没有区别，而我们在日常开发中也比较喜欢使用JSON对象作为传输格式，因此，MongoDB数据库与程序的对接就变得容易多了。

此外，BSON数据类型还使得安全性变得非常高。因为MongoDB在进行查询时使用的是BSON对象，不是像SQL一样可解析的字符串，这可以大幅度降低由SQL注入带来的风险。

### MongoDB数据库的基本概念

像MySQL或者Oracle数据库等关系型数据库一样，MongoDB也有一套完整的基本模型和概念，并且它在某些方面也与关系型数据库类似。我们可以对比一下这两类数据库，以此更好地了解MongoDB数据库。

首先在关系型数据库中比较常见的几个概念：数据库、数据库表、行（也叫记录）、列（也叫字段），在MongoDB数据库中也有几个类似的概念，我们一一来看看。

**Database**：数据库，这个概念和关系型数据库中的概念相同，它装载着所有的数据内容。

**Collection**：集合，可以将其理解为关系型数据库中的表。在关系型数据库中，我们将所有的数据按字段顺序逐行存到数据表中。在MongoDB中也是类似，我们可以将我们需要的数据以文档（Document）为单位存储在集合中。但与关系型数据库不同的是，MongoDB数据库不需要事先定义好列的名字，而是可以随时变化。也就是说，你可以在一个Collection中存储完全不一样的Document，只要这个Document符合BSON的格式要求即可。

**Document**：文档，可以将其理解为关系型数据库中的行。与关系型数据库不同的是，Document是由多个字段组成的，这个字段我们可以理解为JSON中的Key，而值则可以理解为JSON中的Value，因此，我们可以先粗略地理解为，Document就是一个JSON字符串。

**Field**：字段，可以将其理解为关系型数据库中的列。与关系型数据库不同的是，Field可以支持更多的数据类型，甚至还可以像JSON中嵌套JSON一样，在Document中嵌套Document等，因此，它的Field类型更加灵活。

这些是MongoDB数据库最主要的概念，我们也对应地讲解了它们和关系型数据库的差异，MongoDB数据库的概念并不止这些，其他的我们遇到再做讲解。

## 如何安装和使用MongoDB数据库？

在对MongoDB数据库有了一个初步的了解之后，接下来我们来看看如何安装和使用MongoDB数据库。

### MongoDB数据库的安装

**第一步，** 进入MongoDB的官网。

![](https://static001.geekbang.org/resource/image/4e/04/4e34e04aba09d964bbf75334yy46f904.png?wh=3814x1782)

**第二步，** 我们在最上面的菜单栏依次找到Product→Community Edition→Community Server。

![](https://static001.geekbang.org/resource/image/a1/d4/a1829768f2ea2aa1acc5ecceb9c2dfd4.png?wh=2032x1227)

**第三步，** 在弹出的页面中，选择自己需要的版本、平台和包。这里我使用的是4.0.28版本，平台使用Windows平台，用msi安装包的形式进行安装，点击download按钮开始下载。

![](https://static001.geekbang.org/resource/image/f2/a4/f2e606a4c7fc0de9a199328702b52aa4.png?wh=2164x1770)

**第四步，** 下载完成后，双击我们下载的安装包进行安装，然后可以看到下面这个界面。

![](https://static001.geekbang.org/resource/image/98/a5/986c894089f6ffb18784ca87844cc5a5.png?wh=764x597)

**第五步，** 在这个界面下，一路Next到选择安装方式界面，在这个界面中，上面是完全安装（Complete），下面是自定义安装（Custom），我建议使用自定义安装，因为这个时候你可以清楚地了解你都安装了什么，并且安装到了哪个目录。

![](https://static001.geekbang.org/resource/image/b0/45/b077bedf58eb1eaf88c47c07858e8145.png?wh=771x596)

**第六步，** 接下来会让你选择要安装的程序以及安装的位置。一般来讲，安装的程序我们默认就可以了，安装的位置我建议选择一个非C盘的磁盘，最好空间大一点，这里我把它安装到了I盘。在更改目录时，我也建议你只更改目录前面的盘符，不更改后面安装位置的具体目录，因为使用原目录结构在进行环境变量等信息配置的时候，更加方便。

![](https://static001.geekbang.org/resource/image/60/a6/60498c5cyyd1058028f81ef5c04eaaa6.png?wh=766x596)

**第七步，** 点击Next，这个时候安装程序让我们选择服务的配置，这里直接默认就好。然后我们一路Next到最后，安装完成之后会弹出完成界面。

![](https://static001.geekbang.org/resource/image/67/52/6700a2bbf0aa6fefe9763c11e999e052.png?wh=768x595)

与此同时还会弹出一个Compass的窗口，这个我们暂时用不上。

![](https://static001.geekbang.org/resource/image/6b/fe/6b190c48039fdb79f7b9d2efcc6c1ffe.png?wh=2126x1240)

不过，完成上面这些步骤之后，我们只能说完成了全流程的50%，这时候我们的MongoDB数据库还是不可用的。接下来我们要配置环境变量、配置相关目录并启动数据库。

首先，我们要把MongoDB相关的命令配置到环境变量中，方便我们后面的开发和操作。

具体做法是，先找到我们刚刚安装MongoDB的目录，比如我的目录是：I:\\Program Files\\MongoDB\\Server\\4.0。然后我们把它加入到系统的环境变量中，我们需要在系统的环境变量中新建一个Key为MONGO\_HOME，如下图所示。

![](https://static001.geekbang.org/resource/image/d7/1a/d70f3dd2d0eaeaa091fd0a54c114061a.png?wh=1029x264)

接下来，我们在Path中新建一个变量 `%MONGO_HOME%\bin`，这里包含了运行MongoDB的相关命令。

![](https://static001.geekbang.org/resource/image/b8/46/b8979c2a9b6701b808e0268c92729a46.png?wh=823x793)

点击确定，然后点击环境变量窗口的确定，此时，我们就可以在命令行中使用MongoDB的相关命令了。例如，我们可以在命令行中输入mongo，这时如果弹出下图这样的信息，就说明环境变量配置好了。

![](https://static001.geekbang.org/resource/image/4b/09/4bf81b460bbe2a0185bd15689616ea09.png?wh=1470x766)

到这里，实际上我们的MongoDB数据库就已经安装成功，也可以正常使用了。接下来，我们要把MongoDB添加成为一个系统服务，这样每次启动的时候，就不需要重新运行命令了。

首先，我们要在MongoDB的安装目录的data文件夹下创建两个目录，分别是db目录和log目录，如图所示。

![](https://static001.geekbang.org/resource/image/f7/2a/f7dbde34c2d2f5f08531c4936yy52c2a.png?wh=1684x880)

然后在log目录下，创建一个名为mongodb.log的文件。

接下来，在MongoDB的主目录下（我这里的主目录是I:\\Program Files\\MongoDB\\Server\\4.0）创建一个mongod.cfg文件，用记事本编辑文件，在文件中输入下面内容。

```
systemLog:
    destination: file
    path: I:\Program Files\MongoDB\Server\4.0\data\log\mongod.log
storage:
	dbPath: I:\Program Files\MongoDB\Server\4.0\data\db

```

接着，以管理员身份打开cmd命令，如下图所示。

![](https://static001.geekbang.org/resource/image/84/31/842aef1d31c9492d1f8c375dd249c231.png?wh=1125x747)

然后输入如下命令。

```
mongod --config"I:\Program Files\MongoDB\Server\4.0\mongod.cfg"--install

```

接下来输入下面这个命令。

```
net start MongoDB

```

如果出现下面的截图，说明服务已经启动了。

![](https://static001.geekbang.org/resource/image/b6/e7/b606aa0ceccff3f14bfea1932087e4e7.png?wh=1374x321)

我们在计算机上点击右键选择管理，然后在服务和应用程序中找到服务，并在服务选项中找到MongoDB Server。

![](https://static001.geekbang.org/resource/image/fd/54/fd6ca335f0146656bde5702188768154.png?wh=1187x821)

此时，我们的MongoDB数据库已经完全安装完成了。我们可以通过cmd控制台输入mongo命令，如果得到下面这个截图，说明安装成功了。

![](https://static001.geekbang.org/resource/image/fc/ed/fc0675bd8c36c231d6c643438ac168ed.png?wh=1440x748)

### MongoDB数据库的简单使用

接下来，我们写一个简单的demo来测试一下我们的数据库，需要完成下面几个操作。

1. 创建一个数据库DB。
2. 创建一个Collection。
3. 在Collection中插入一条数据。
4. 使用查询语句将这条数据查询出来。

在MongoDB中，创建数据库的命令是 `use + 数据库名`，这个时候，MongoDB会查询系统中是否有这个数据库，如果有，则直接使用，如果没有就会自动创建。为了验证我们的想法，我们先使用DB命令来查询一下目前使用的是哪个数据库。

```
db

```

得到下图。

![](https://static001.geekbang.org/resource/image/d2/e8/d269d727bf18b7ab2e39a099e61332e8.png?wh=669x52)

通过这张图我们可以看到，目前我们的MongoDB系统中只有一个test数据库。接下来，我们使用下面的命令创建一个 `recommendation_demo` 数据库。

```
use recommendation_demo

```

然后再使用DB命令进行查询，得到结果如图。

![](https://static001.geekbang.org/resource/image/e3/54/e3208314fe01a4bc07939435f1e72b54.png?wh=823x100)

我们可以随意往里面插入一条数据，比如我们插入一条Key为“name”，值为“welcome to recommendation system class”的数据，然后我们再使用find命令来查询数据是否存在。

```
db.recommendation_demo.insert({"name":"welcome to recommendation system class"})

```

![](https://static001.geekbang.org/resource/image/1b/e5/1b08ce29550e2bb2f03eae6b0ed21de5.png?wh=712x99)

如果能够看到上面的信息，说明我们的MongoDB数据库已经能够正常运行，并且你已经往里面插入了一条真实的数据。

到这里你可能还有一个疑问，我们这里只创建了DB并插入了数据，但是并没有特意创建Collection呀。实际上，在MongoDB中，如果没有指定创建Collection的话，就会默认创建一个与数据库同名的Collection，我们可以通过show tables命令来验证下。

![](https://static001.geekbang.org/resource/image/54/d4/54df29d8f7969461fc339e850118dbd4.png?wh=303x36)

到现在为止，我们MongoDB的安装和最基本的使用已经学习完成了。在后面的课程中，我们会利用MongoDB数据库来完成我们推荐系统中的部分数据存储工作。

## 总结

学完这节课，希望你记住下面这些知识点。

1. MongoDB是一个开源的基于分布式文件存储的数据库，它是使用C++语言编写的。
2. MongoDB最突出的优势是可扩展性强，同时它还具有高效的查询方式和很高的安全性。
3. MongoDB数据库在很多方面与结构化数据库有异曲同工之处，数据库、集合、文档、字段等概念都与关系型数据库有所对应，我们应该了解他们的区别和联系。
4. MongoDB数据库的安装方法，以及安装之后如何把它变成一个Windows自带的服务。
5. 使用 MongoDB 数据库创建一个 Collection 并插入数据。

## 课后题

学完这节课，给你留两道课后题。

1. 请你动手在自己的电脑上搭建一套MongoDB数据库的开发环境。
2. 请你尝试自学API的形式，创建一个数据库和集合，并在库中随意插入一条数据。

欢迎你把代码上传到GitHub并在评论区留下你的代码链接，我会选择有代表性的代码进行点评。我们下节课见！