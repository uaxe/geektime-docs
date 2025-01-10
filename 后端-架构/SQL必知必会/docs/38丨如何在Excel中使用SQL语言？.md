在进阶篇中，我们对设计范式、索引、页结构、事务以及查询优化器的原理进行了学习，了解这些可以让我们更好地使用SQL来操作RDBMS。实际上SQL的影响力远不止于此，在数据的世界里，SQL更像是一门通用的语言，虽然每种工具都会有一些自己的“方言”，但是掌握SQL可以让我们接触其它以数据为核心的工具时，更加游刃有余。

比如Excel。

你一定使用过Excel，事实上，Excel的某些部分同样支持我们使用SQL语言，那么具体该如何操作呢？

今天的课程主要包括以下几方面的内容：

1. 如何在Excel中获取外部数据源？
2. 数据透视表和数据透视图是Excel的两个重要功能，如何通过SQL查询在Excel中完成数据透视表和透视图？
3. 如何让Excel与MySQL进行数据交互？

## 如何在Excel中获取外部数据源？

使用SQL查询数据，首先需要数据源。如果我们用Excel来呈现这些数据的话，就需要先从外部导入数据源。这里介绍两种直接导入的方式：

1. 通过OLE DB接口获取外部数据源；
2. 通过Microsoft Query导入外部数据源。

下面我们通过导入数据源heros.xlsx体验一下这两种方式，你可以从 [这里](https://github.com/cystanford/SQL-Excel) 下载数据源。

### 通过OLE DB接口获取外部数据源

OLE的英文是Object Link and Embedding，中文意思是对象连接与嵌入，它是一种面向对象的技术。DB代表的就是数据库。OLE DB的作用就是通向不同的数据源的程序接口，方便获取外部数据，这里不仅包括ODBC，也包括其他非SQL数据类型的通路，你可以把OLE DB的作用理解成通过统一的接口来访问不同的数据源。

如果你想要在Excel中通过OLE DB接口导入数据，需要执行下面的步骤：

第一步，选择指定的文件。方法是通过“数据” → “现有连接”按钮选择连接。这里选择“浏览更多”，然后选择指定的xls文件。

![](https://static001.geekbang.org/resource/image/b5/81/b53c4acda1cf19a1943cf0123f5a2481.png?wh=865*867)

第二步，选择指定的表格，勾选数据首行包含列标题，目的是将第一行的列名也加载进来。

![](https://static001.geekbang.org/resource/image/85/f9/8594b603410c1b7872de9d7ef38e7df9.png?wh=848*418)

第三步，通过“属性” → “定义”中的命令文本来使用SQL查询，选择我们想要的数据，也可以将整张表直接导入到指定的位置。

![](https://static001.geekbang.org/resource/image/1d/f2/1df9b6d9ab9d4a854ab532f1f98ed1f2.png?wh=721*820)

如果我们显示方式为“表”，导入全部的数据到指定的$A$1（代表A1单元格），那么在Excel中就可以导入整个数据表，如下图所示：

![](https://static001.geekbang.org/resource/image/ba/ab/baeb41a95f49eb1fb76d6afe48122aab.png?wh=1730*601?wh=1730*601)

### 通过Microsoft Query获取外部数据源

第二种方式是利用Microsoft Query功能导入外部数据源，具体步骤如下：

第一步，选择指定的文件。方法是通过“数据” → “获取外部数据”按钮选择数据库，这里我选择了“Excel Files”，然后选择我们想要导入的xls文件。

![](https://static001.geekbang.org/resource/image/c7/84/c7cb9168c77b11c0d7f90a86316c3b84.png?wh=1093*567)

第二步。选择可用的表和列，在左侧面板中勾选我们想要导入的数据表及相应的列，点击 （>） 按钮导入到右侧的面板中，然后点击下一步。

![](https://static001.geekbang.org/resource/image/1c/40/1ca1f6f8d11e2f0c70c0b81ff8647440.png?wh=1128*648)

最后我们可以选择“将数据返回Microsoft Excel”还是“在Microsoft Query中查看数据或编辑查询”。这里我们选择第一个选项。

![](https://static001.geekbang.org/resource/image/75/46/753b382fa6246c4dd1d7634d703dc646.png?wh=1116*640)

当我们选择“将数据返回到Microsoft Excel”后，接下来的操作和使用OLE DB接口方式导入数据一样，可以对显示方式以及属性进行调整：

![](https://static001.geekbang.org/resource/image/24/65/24c70f964bb4dbdaf388af45bc57d865.png?wh=831*1000)

这里，我们同样选择显示方式为“表”，导入全部的数据到指定的$A$1(代表A1单元格），同样会看到如下的结果：

![](https://static001.geekbang.org/resource/image/ba/ab/baeb41a95f49eb1fb76d6afe48122aab.png?wh=1730*601?wh=1730*601)

## 使用数据透视表和数据透视图做分析

通过上面的操作你也能看出来，从外部导入数据并不难，关键在于通过SQL控制想要的结果集，这里我们需要使用到Excel的数据透视表以及数据透视图的功能。

我简单介绍下数据透视表和数据透视图：

数据透视表可以快速汇总大量数据，帮助我们统计和分析数据，比如求和，计数，查看数据中的对比情况和趋势等。数据透视图则可以对数据透视表中的汇总数据进行可视化，方便我们直观地查看数据的对比与趋势等。

假设我想对主要角色（role\_main）的英雄数据进行统计，分析他们平均的最大生命值（hp\_max），平均的最大法力值(mp\_max)，平均的最大攻击值(attack\_max)，那么对应的SQL查询为：

```
SELECT role_main, avg(hp_max) AS `平均最大生命`, avg(mp_max) AS `平均最大法力`, avg(attack_max) AS `平均最大攻击力`, count(*) AS num FROM heros GROUP BY role_main

```

### 使用SQL+数据透视表

现在我们使用SQL查询，通过OLE DB的方式来完成数据透视表。我们在第三步的时候选择“属性”，并且在命令文本中输入相应的SQL语句，注意这里的数据表是\[heros$\]，对应的命令文本为：

```
SELECT role_main, avg(hp_max) AS `平均最大生命`, avg(mp_max) AS `平均最大法力`, avg(attack_max) AS `平均最大攻击力`, count(*) AS num FROM [heros$] GROUP BY role_main

```

![](https://static001.geekbang.org/resource/image/5f/0d/5ff31b9bc54a6d0c02e23775273ada0d.png?wh=842*1161)

然后我们在右侧面板中选择“数据透视表字段”，以便对数据透视表中的字段进行管理，比如我们勾选num，role\_main，平均最大生命，平均最大法力，平均最大攻击力。

![](https://static001.geekbang.org/resource/image/cf/9d/cf3e3da9ddedb2d886806ac4b490059d.png?wh=592*479)

最后会在Excel中呈现如下的数据透视表：

![](https://static001.geekbang.org/resource/image/c4/08/c41bd917642147b103ec3524d7a9f408.png?wh=1729*350)

操作视频如下：

### 使用SQL+数据透视图

数据透视图可以呈现可视化的形式，方便我们直观地了解数据的特征。这里我们使用SQL查询，通过Microsoft Query的方式来完成数据透视图。我们在第三步的时候选择在Microsoft Query中查看数据或编辑查询，来看下Microsoft Query的界面：

![](https://static001.geekbang.org/resource/image/c7/20/c7d10db98c4e2226b663bbb7baefba20.png?wh=1729*1106)

然后我们点击“SQL”按钮，可以对SQL语句进行编辑，筛选我们想要的结果集，可以得到：

![](https://static001.geekbang.org/resource/image/2b/7d/2b9b5f3495013b62b7ba6e3186cf257d.png?wh=1730*850)

然后选择“将数据返回Microsoft Excel”，在返回时选择“数据透视图”，然后在右侧选择数据透视图的字段，就可以得到下面这张图：

![](https://static001.geekbang.org/resource/image/46/02/46829993666745ecc578b22ffcde4802.png?wh=1045*630)

你可以看到使用起来还是很方便。

具体操作视频如下：

## 让Excel与MySQL进行数据交互

刚才我们讲解的是如何从Excel中导入外部的xls文件数据，并在Excel实现数据透视表和数据透视图的呈现。实际上，Excel也可以与MySQL进行数据交互，这里我们需要使用到MySQL for Excel插件：

下载mysql-for-excel并安装，地址： [https://dev.mysql.com/downloads/windows/excel/](https://dev.mysql.com/downloads/windows/excel/)

下载mysql-connector-odbc并安装，地址： [https://dev.mysql.com/downloads/connector/odbc/](https://dev.mysql.com/downloads/connector/odbc/)

这次我们的任务是给数据表增加一个last\_name字段，并且使用Excel的自动填充功能来填充好英雄的姓氏。

第一步，连接MySQL。打开一个新的Excel文件的时候，会在“数据”面板中看到MySQL for Excel的插件，点击后可以打开MySQL的连接界面，如下：

![](https://static001.geekbang.org/resource/image/ec/3c/ec96481d8517bc7b08728630d3b1aa3c.png?wh=1092*631)

第二步，导入heros数据表。输入密码后，我们在右侧选择想要的数据表heros，然后选择Import MySQL Data导入数据表的导入，结果如下：

![](https://static001.geekbang.org/resource/image/33/15/333b8dc9913bcdf19d74e685f6751015.png?wh=1587*555)

第三步，创建last\_name字段，使用Excel的自动填充功能来进行姓氏的填写（Excel自带的“自动填充”可以帮我们智能填充一些数据），完成之后如下图所示：

![](https://static001.geekbang.org/resource/image/80/b7/801e1ec489d650a7df244b3737346cb7.png?wh=1729*639)

第四步，将修改好的Excel表导入到MySQL中，创建一个新表heros\_xls。选中整个数据表（包括数据行及列名），然后在右侧选择“Export Excel Data to New Table”。这时在MySQL中你就能看到相应的数据表heros\_xls了，我们在MySQL中使用SQL进行查询：

```
mysql > SELECT * FROM heros_xls

```

运行结果（69条记录）：

![](https://static001.geekbang.org/resource/image/86/56/868182e27c6a4a80db0f0f7decbc7956.png?wh=1201*352)

需要说明的是，有时候自动填充功能并不完全准确，我们还需要对某些数据行的last\_name进行修改，比如“夏侯惇”的姓氏应该改成“夏侯”，“百里守约”改成“百里”等。

## 总结

我们今天讲解了如何在Excel中使用SQL进行查询，在这个过程中你应该对”SQL定义了查询的标准“更有体会。SQL使得各种工具可以遵守SQL语言的标准（当然也有各自的方言）。

如果你已经是个SQL高手，你会发现原来SQL和Excel还可以如此“亲密”。Excel作为使用人数非常多的办公软件，提供了SQL查询会让我们操作起来非常方便。如果你还没有使用过Excel的这些功能，那么就赶快来用一下吧。

SQL作为一门结构化查询语言，具有很好的通用性，你还在其他工具中使用过SQL语言吗？如果有的话可以分享一下你的体会。

最后留一道动手题吧。你可以创建一个新的xls文件，导入heros.xlsx数据表，用数据透视图的方式对英雄主要定位为刺客、法师、射手的英雄数值进行可视化，数据查询方式请使用SQL查询，统计的英雄数值为平均生命成长hp\_growth，平均法力成长mp\_growth，平均攻击力成长attack\_growth。

欢迎你在评论区写下你的体会与思考，也欢迎把这篇文章分享给你的朋友或者同事，一起来交流。