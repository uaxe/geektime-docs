今天我来给你讲讲Python的可视化技术。

如果你想要用Python进行数据分析，就需要在项目初期开始进行探索性的数据分析，这样方便你对数据有一定的了解。其中最直观的就是采用数据可视化技术，这样，数据不仅一目了然，而且更容易被解读。同样在数据分析得到结果之后，我们还需要用到可视化技术，把最终的结果呈现出来。

## 可视化视图都有哪些？

按照数据之间的关系，我们可以把可视化视图划分为4类，它们分别是比较、联系、构成和分布。我来简单介绍下这四种关系的特点：

1. 比较：比较数据间各类别的关系，或者是它们随着时间的变化趋势，比如折线图；

2. 联系：查看两个或两个以上变量之间的关系，比如散点图；

3. 构成：每个部分占整体的百分比，或者是随着时间的百分比变化，比如饼图；

4. 分布：关注单个变量，或者多个变量的分布情况，比如直方图。


同样，按照变量的个数，我们可以把可视化视图划分为单变量分析和多变量分析。

单变量分析指的是一次只关注一个变量。比如我们只关注“身高”这个变量，来看身高的取值分布，而暂时忽略其他变量。

多变量分析可以让你在一张图上可以查看两个以上变量的关系。比如“身高”和“年龄”，你可以理解是同一个人的两个参数，这样在同一张图中可以看到每个人的“身高”和“年龄”的取值，从而分析出来这两个变量之间是否存在某种联系。

可视化的视图可以说是分门别类，多种多样，今天我主要介绍常用的10种视图，这些视图包括了散点图、折线图、直方图、条形图、箱线图、饼图、热力图、蜘蛛图、二元变量分布和成对关系。

![](https://static001.geekbang.org/resource/image/46/75/4673a17085302cfe9177f8ee687ac675.png?wh=574*441)

下面我给你一一进行介绍。

**散点图**

散点图的英文叫做scatter plot，它将两个变量的值显示在二维坐标中，非常适合展示两个变量之间的关系。当然，除了二维的散点图，我们还有三维的散点图。

我在上一讲中给你简单介绍了下Matplotlib这个工具，在Matplotlib中，我们经常会用到pyplot这个工具包，它包括了很多绘图函数，类似Matlab的绘图框架。在使用前你需要进行引用：

```
import matplotlib.pyplot as plt

```

在工具包引用后，画散点图，需要使用plt.scatter(x, y, marker=None)函数。x、y 是坐标，marker代表了标记的符号。比如“x”、“>”或者“o”。选择不同的marker，呈现出来的符号样式也会不同，你可以自己试一下。

下面三张图分别对应“x”“>”和“o”。

![](https://static001.geekbang.org/resource/image/7a/f9/7a3e19e006a354eacc230fe87f623cf9.png?wh=603*154)

除了Matplotlib外，你也可以使用Seaborn进行散点图的绘制。在使用Seaborn前，也需要进行包引用：

```
import seaborn as sns

```

在引用seaborn工具包之后，就可以使用seaborn工具包的函数了。如果想要做散点图，可以直接使用sns.jointplot(x, y, data=None, kind='scatter')函数。其中x、y是data中的下标。data就是我们要传入的数据，一般是DataFrame类型。kind这类我们取scatter，代表散点的意思。当然kind还可以取其他值，这个我在后面的视图中会讲到，不同的kind代表不同的视图绘制方式。

好了，让我们来模拟下，假设我们的数据是随机的1000个点。

```
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# 数据准备
N = 1000
x = np.random.randn(N)
y = np.random.randn(N)
# 用Matplotlib画散点图
plt.scatter(x, y,marker='x')
plt.show()
# 用Seaborn画散点图
df = pd.DataFrame({'x': x, 'y': y})
sns.jointplot(x="x", y="y", data=df, kind='scatter');
plt.show()

```

我们运行一下这个代码，就可以看到下面的视图（第一张图为Matplotlib绘制的，第二张图为Seaborn绘制的）。其实你能看到Matplotlib和Seaborn的视图呈现还是有差别的。Matplotlib默认情况下呈现出来的是个长方形。而Seaborn呈现的是个正方形，而且不仅显示出了散点图，还给了这两个变量的分布情况。

Matplotlib绘制：

![](https://static001.geekbang.org/resource/image/28/03/2823ea9c7c2d988c1fdb3e7c8fb1e603.png?wh=393*301)

Seaborn绘制：

![](https://static001.geekbang.org/resource/image/5f/b9/5f06e23188cb31bc549cfd60696e75b9.png?wh=392*397)

**折线图**

折线图可以用来表示数据随着时间变化的趋势。

在Matplotlib中，我们可以直接使用plt.plot()函数，当然需要提前把数据按照x轴的大小进行排序，要不画出来的折线图就无法按照x轴递增的顺序展示。

在Seaborn中，我们使用sns.lineplot (x, y, data=None)函数。其中x、y是data中的下标。data就是我们要传入的数据，一般是DataFrame类型。

这里我们设置了x、y的数组。x数组代表时间（年），y数组我们随便设置几个取值。下面是详细的代码。

```
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# 数据准备
x = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
y = [5, 3, 6, 20, 17, 16, 19, 30, 32, 35]
# 使用Matplotlib画折线图
plt.plot(x, y)
plt.show()
# 使用Seaborn画折线图
df = pd.DataFrame({'x': x, 'y': y})
sns.lineplot(x="x", y="y", data=df)
plt.show()

```

然后我们分别用Matplotlib和Seaborn进行画图，可以得到下面的图示。你可以看出这两个图示的结果是完全一样的，只是在seaborn中标记了x和y轴的含义。

![](https://static001.geekbang.org/resource/image/25/88/258c6a2fbd7786ed7bd86a5f50c49b88.png?wh=423*322)

![](https://static001.geekbang.org/resource/image/77/60/77d619cc2a4131e97478df490cc43d60.png?wh=417*316)

**直方图**

直方图是比较常见的视图，它是把横坐标等分成了一定数量的小区间，这个小区间也叫作“箱子”，然后在每个“箱子”内用矩形条（bars）展示该箱子的箱子数（也就是y值），这样就完成了对数据集的直方图分布的可视化。

在Matplotlib中，我们使用plt.hist(x, bins=10)函数，其中参数x是一维数组，bins代表直方图中的箱子数量，默认是10。

在Seaborn中，我们使用sns.distplot(x, bins=10, kde=True)函数。其中参数x是一维数组，bins代表直方图中的箱子数量，kde代表显示核密度估计，默认是True，我们也可以把kde设置为False，不进行显示。核密度估计是通过核函数帮我们来估计概率密度的方法。

这是一段绘制直方图的代码。

```
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# 数据准备
a = np.random.randn(100)
s = pd.Series(a)
# 用Matplotlib画直方图
plt.hist(s)
plt.show()
# 用Seaborn画直方图
sns.distplot(s, kde=False)
plt.show()
sns.distplot(s, kde=True)
plt.show()

```

我们创建一个随机的一维数组，然后分别用Matplotlib和Seaborn进行直方图的显示，结果如下，你可以看出，没有任何差别，其中最后一张图就是kde默认为Ture时的显示情况。

![](https://static001.geekbang.org/resource/image/fc/0d/fccd31462e7de6f56b4aca262b46650d.png?wh=549*403)

![](https://static001.geekbang.org/resource/image/fb/af/fb7a2db332dcd5c7c18a4961794923af.png?wh=536*401)

![](https://static001.geekbang.org/resource/image/9c/19/9cded19e1c877f98f55d4c6726ff2f19.png?wh=547*400)

**条形图**

如果说通过直方图可以看到变量的数值分布，那么条形图可以帮我们查看类别的特征。在条形图中，长条形的长度表示类别的频数，宽度表示类别。

在Matplotlib中，我们使用plt.bar(x, height)函数，其中参数x代表x轴的位置序列，height是y轴的数值序列，也就是柱子的高度。

在Seaborn中，我们使用sns.barplot( _x=None, y=None, data=None_)函数。其中参数data为DataFrame类型，x、y是data中的变量。

```
import matplotlib.pyplot as plt
import seaborn as sns
# 数据准备
x = ['Cat1', 'Cat2', 'Cat3', 'Cat4', 'Cat5']
y = [5, 4, 8, 12, 7]
# 用Matplotlib画条形图
plt.bar(x, y)
plt.show()
# 用Seaborn画条形图
sns.barplot(x, y)
plt.show()

```

我们创建了x、y两个数组，分别代表类别和类别的频数，然后用Matplotlib和Seaborn进行条形图的显示，结果如下：

![](https://static001.geekbang.org/resource/image/d9/3a/d9a247a6fbee488cc8eb62f96947173a.png?wh=380*284)

![](https://static001.geekbang.org/resource/image/75/31/7553f2fa08e3962ed9902d4cef796c31.png?wh=379*288)

**箱线图**

箱线图，又称盒式图，它是在1977年提出的，由五个数值点组成：最大值(max)、最小值(min)、中位数(median)和上下四分位数(Q3, Q1)。它可以帮我们分析出数据的差异性、离散程度和异常值等。

在Matplotlib中，我们使用plt.boxplot(x, labels=None)函数，其中参数x代表要绘制箱线图的数据，labels是缺省值，可以为箱线图添加标签。

在Seaborn中，我们使用sns.boxplot( _x=None, y=None, data=None_)函数。其中参数data为DataFrame类型，x、y是data中的变量。

```
# 数据准备
# 生成10*4维度数据
data=np.random.normal(size=(10,4))
labels = ['A','B','C','D']
# 用Matplotlib画箱线图
plt.boxplot(data,labels=labels)
plt.show()
# 用Seaborn画箱线图
df = pd.DataFrame(data, columns=labels)
sns.boxplot(data=df)
plt.show()

```

这段代码中，我生成0-1之间的10\*4维度数据，然后分别用Matplotlib和Seaborn进行箱线图的展示，结果如下。

Matplotlib绘制：

![](https://static001.geekbang.org/resource/image/60/e0/6083f7fc15028eae5e3f49e60fad90e0.png?wh=399*309)

Seaborn绘制：

![](https://static001.geekbang.org/resource/image/42/e0/42fe2a9864bbc2bc0034a0973673d1e0.png?wh=409*309)

**饼图**

饼图是常用的统计学模块，可以显示每个部分大小与总和之间的比例。在Python数据可视化中，它用的不算多。我们主要采用Matplotlib的pie函数实现它。

在Matplotlib中，我们使用plt.pie(x, labels=None)函数，其中参数x代表要绘制饼图的数据，labels是缺省值，可以为饼图添加标签。

这里我设置了labels数组，分别代表高中、本科、硕士、博士和其他几种学历的分类标签。nums代表这些学历对应的人数。

```
import matplotlib.pyplot as plt
# 数据准备
nums = [25, 37, 33, 37, 6]
labels = ['High-school','Bachelor','Master','Ph.d', 'Others']
# 用Matplotlib画饼图
plt.pie(x = nums, labels=labels)
plt.show()

```

通过Matplotlib的pie函数，我们可以得出下面的饼图：

![](https://static001.geekbang.org/resource/image/45/f7/45c38de6563d528f610bfcef5c8874f7.png?wh=435*341)

**热力图**

热力图，英文叫heat map，是一种矩阵表示方法，其中矩阵中的元素值用颜色来代表，不同的颜色代表不同大小的值。通过颜色就能直观地知道某个位置上数值的大小。另外你也可以将这个位置上的颜色，与数据集中的其他位置颜色进行比较。

热力图是一种非常直观的多元变量分析方法。

我们一般使用Seaborn中的sns.heatmap(data)函数，其中data代表需要绘制的热力图数据。

这里我们使用Seaborn中自带的数据集flights，该数据集记录了1949年到1960年期间，每个月的航班乘客的数量。

```
import matplotlib.pyplot as plt
import seaborn as sns
# 数据准备
flights = sns.load_dataset("flights")
data=flights.pivot('year','month','passengers')
# 用Seaborn画热力图
sns.heatmap(data)
plt.show()

```

通过seaborn的heatmap函数，我们可以观察到不同年份，不同月份的乘客数量变化情况，其中颜色越浅的代表乘客数量越多，如下图所示：

![](https://static001.geekbang.org/resource/image/57/93/57e1bc17d943620620fb087d6190df93.png?wh=542*440)

**蜘蛛图**

蜘蛛图是一种显示一对多关系的方法。在蜘蛛图中，一个变量相对于另一个变量的显著性是清晰可见的。

假设我们想要给王者荣耀的玩家做一个战力图，指标一共包括推进、KDA、生存、团战、发育和输出。那该如何做呢？

这里我们需要使用Matplotlib来进行画图，首先设置两个数组：labels和stats。他们分别保存了这些属性的名称和属性值。

因为蜘蛛图是一个圆形，你需要计算每个坐标的角度，然后对这些数值进行设置。当画完最后一个点后，需要与第一个点进行连线。

因为需要计算角度，所以我们要准备angles数组；又因为需要设定统计结果的数值，所以我们要设定stats数组。并且需要在原有angles和stats数组上增加一位，也就是添加数组的第一个元素。

```
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties
# 数据准备
labels=np.array([u"推进","KDA",u"生存",u"团战",u"发育",u"输出"])
stats=[83, 61, 95, 67, 76, 88]
# 画图数据准备，角度、状态值
angles=np.linspace(0, 2*np.pi, len(labels), endpoint=False)
stats=np.concatenate((stats,[stats[0]]))
angles=np.concatenate((angles,[angles[0]]))
# 用Matplotlib画蜘蛛图
fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.plot(angles, stats, 'o-', linewidth=2)
ax.fill(angles, stats, alpha=0.25)
# 设置中文字体
font = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf", size=14)
ax.set_thetagrids(angles * 180/np.pi, labels, FontProperties=font)
plt.show()

```

代码中flt.figure是创建一个空白的figure对象，这样做的目的相当于画画前先准备一个空白的画板。然后add\_subplot(111)可以把画板划分成1行1列。再用ax.plot和ax.fill进行连线以及给图形上色。最后我们在相应的位置上显示出属性名。这里需要用到中文，Matplotlib对中文的显示不是很友好，因此我设置了中文的字体font，这个需要在调用前进行定义。最后我们可以得到下面的蜘蛛图，看起来是不是很酷？

![](https://static001.geekbang.org/resource/image/19/7d/1924d3cbf035053fa3d5043794624c7d.png?wh=405*395)

**二元变量分布**

如果我们想要看两个变量之间的关系，就需要用到二元变量分布。当然二元变量分布有多种呈现方式，开头给你介绍的散点图就是一种二元变量分布。

在Seaborn里，使用二元变量分布是非常方便的，直接使用sns.jointplot(x, y, data=None, kind)函数即可。其中用kind表示不同的视图类型：“kind='scatter'”代表散点图，“kind='kde'”代表核密度图，“kind='hex' ”代表Hexbin图，它代表的是直方图的二维模拟。

这里我们使用Seaborn中自带的数据集tips，这个数据集记录了不同顾客在餐厅的消费账单及小费情况。代码中total\_bill保存了客户的账单金额，tip是该客户给出的小费金额。我们可以用Seaborn中的jointplot来探索这两个变量之间的关系。

```
import matplotlib.pyplot as plt
import seaborn as sns
# 数据准备
tips = sns.load_dataset("tips")
print(tips.head(10))
# 用Seaborn画二元变量分布图（散点图，核密度图，Hexbin图）
sns.jointplot(x="total_bill", y="tip", data=tips, kind='scatter')
sns.jointplot(x="total_bill", y="tip", data=tips, kind='kde')
sns.jointplot(x="total_bill", y="tip", data=tips, kind='hex')
plt.show()

```

代码中我用kind分别显示了他们的散点图、核密度图和Hexbin图，如下图所示。

散点图：

![](https://static001.geekbang.org/resource/image/a3/54/a3efa7acabdb7ab7976c826ca5a76754.png?wh=283*275)

核密度图：

![](https://static001.geekbang.org/resource/image/6b/f7/6bd77fa07d150546c0f23e5a0d12b1f7.png?wh=272*263)

Hexbin图：

![](https://static001.geekbang.org/resource/image/7c/aa/7cbdbb115e7d984c3086acb689b661aa.png?wh=287*276)

**成对关系**

如果想要探索数据集中的多个成对双变量的分布，可以直接采用sns.pairplot()函数。它会同时展示出DataFrame中每对变量的关系，另外在对角线上，你能看到每个变量自身作为单变量的分布情况。它可以说是探索性分析中的常用函数，可以很快帮我们理解变量对之间的关系。

pairplot函数的使用，就像在DataFrame中使用describe()函数一样方便，是数据探索中的常用函数。

这里我们使用Seaborn中自带的iris数据集，这个数据集也叫鸢尾花数据集。鸢尾花可以分成Setosa、Versicolour和Virginica三个品种，在这个数据集中，针对每一个品种，都有50个数据，每个数据中包括了4个属性，分别是花萼长度、花萼宽度、花瓣长度和花瓣宽度。通过这些数据，需要你来预测鸢尾花卉属于三个品种中的哪一种。

```
import matplotlib.pyplot as plt
import seaborn as sns
# 数据准备
iris = sns.load_dataset('iris')
# 用Seaborn画成对关系
sns.pairplot(iris)
plt.show()

```

这里我们用Seaborn中的pairplot函数来对数据集中的多个双变量的关系进行探索，如下图所示。从图上你能看出，一共有sepal\_length、sepal\_width、petal\_length和petal\_width4个变量，它们分别是花萼长度、花萼宽度、花瓣长度和花瓣宽度。

下面这张图相当于这4个变量两两之间的关系。比如矩阵中的第一张图代表的就是花萼长度自身的分布图，它右侧的这张图代表的是花萼长度与花萼宽度这两个变量之间的关系。

![](https://static001.geekbang.org/resource/image/88/0d/885450d23f468b9cbcabd90ff9a3480d.png?wh=676*681)

## 总结

我今天给你讲了Python可视化工具包Matplotlib和Seaborn工具包的使用。他们两者之间的关系就相当于NumPy和Pandas的关系。Seaborn是基于Matplotlib更加高级的可视化库。

另外针对我讲到的这10种可视化视图，可以按照变量之间的关系对它们进行分类，这些关系分别是比较、联系、构成和分布。当然我们也可以按照随机变量的个数来进行划分，比如单变量分析和多变量分析。在数据探索中，成对关系pairplot()的使用，相好比Pandas中的describe()使用一样方便，常用于项目初期的数据可视化探索。

在Matplotlib和Seaborn的函数中，我只列了最基础的使用，也方便你快速上手。当然如果你也可以设置修改颜色、宽度等视图属性。你可以自己查看相关的函数帮助文档。这些留给你来进行探索。

关于本次Python可视化的学习，我希望你能掌握：

1. 视图的分类，以及可以从哪些维度对它们进行分类；

2. 十种常见视图的概念，以及如何在Python中进行使用，都需要用到哪些函数；

3. 需要自己动手跑一遍案例中的代码，体验下Python数据可视化的过程。


![](https://static001.geekbang.org/resource/image/8e/d2/8ed2addb00a4329dd63bba669f427fd2.png?wh=865*1073)

最后，我给你留两道思考题吧，Seaborn数据集中自带了car\_crashes数据集，这是一个国外车祸的数据集，你要如何对这个数据集进行成对关系的探索呢？第二个问题就是，请你用Seaborn画二元变量分布图，如果想要画散点图，核密度图，Hexbin图，函数该怎样写？

欢迎你在评论区与我分享你的答案，也欢迎点击“请朋友读”，把这篇文章分享给你的朋友或者同事，一起来动手练习一下。