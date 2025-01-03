上一章中，我们讲了Python的一个重要的第三方库NumPy，今天我来给你介绍Python的另一个工具Pandas。

在数据分析工作中，Pandas的使用频率是很高的，一方面是因为Pandas提供的基础数据结构DataFrame与json的契合度很高，转换起来就很方便。另一方面，如果我们日常的数据清理工作不是很复杂的话，你通常用几句Pandas代码就可以对数据进行规整。

Pandas可以说是基于 NumPy 构建的含有更高级数据结构和分析能力的工具包。在NumPy中数据结构是围绕ndarray展开的，那么在Pandas中的核心数据结构是什么呢？

下面主要给你讲下 **Series和 DataFrame这两个核心数据结构**，他们分别代表着一维的序列和二维的表结构。基于这两种数据结构，Pandas可以对数据进行导入、清洗、处理、统计和输出。

## 数据结构：Series和DataFrame

**Series是个定长的字典序列**。说是定长是因为在存储的时候，相当于两个ndarray，这也是和字典结构最大的不同。因为在字典的结构里，元素的个数是不固定的。

**Series** 有两个基本属性：index 和 values。在Series结构中，index默认是0,1,2,……递增的整数序列，当然我们也可以自己来指定索引，比如index=\[‘a’, ‘b’, ‘c’, ‘d’\]。

```
import pandas as pd
from pandas import Series, DataFrame
x1 = Series([1,2,3,4])
x2 = Series(data=[1,2,3,4], index=['a', 'b', 'c', 'd'])
print x1
print x2

```

运行结果：

```
0    1
1    2
2    3
3    4
dtype: int64
a    1
b    2
c    3
d    4
dtype: int64

```

这个例子中，x1中的index采用的是默认值，x2中index进行了指定。我们也可以采用字典的方式来创建Series，比如：

```
d = {'a':1, 'b':2, 'c':3, 'd':4}
x3 = Series(d)
print x3

```

运行结果：

```
a    1
b    2
c    3
d    4
dtype: int64

```

**DataFrame类型数据结构类似数据库表。**

它包括了行索引和列索引，我们可以将DataFrame 看成是由相同索引的Series组成的字典类型。

我们虚构一个王者荣耀考试的场景，想要输出几位英雄的考试成绩：

```
import pandas as pd
from pandas import Series, DataFrame
data = {'Chinese': [66, 95, 93, 90,80],'English': [65, 85, 92, 88, 90],'Math': [30, 98, 96, 77, 90]}
df1= DataFrame(data)
df2 = DataFrame(data, index=['ZhangFei', 'GuanYu', 'ZhaoYun', 'HuangZhong', 'DianWei'], columns=['English', 'Math', 'Chinese'])
print df1
print df2

```

在后面的案例中，我一般会用df, df1, df2这些作为DataFrame数据类型的变量名，我们以例子中的df2为例，列索引是\[‘English’, ‘Math’, ‘Chinese’\]，行索引是\[‘ZhangFei’, ‘GuanYu’, ‘ZhaoYun’, ‘HuangZhong’, ‘DianWei’\]，所以df2的输出是：

```
            English  Math  Chinese
ZhangFei         65    30       66
GuanYu           85    98       95
ZhaoYun          92    96       93
HuangZhong       88    77       90
DianWei          90    90       80

```

在了解了Series和 DataFrame这两个数据结构后，我们就从数据处理的流程角度，来看下他们的使用方法。

## 数据导入和输出

Pandas允许直接从xlsx，csv等文件中导入数据，也可以输出到xlsx, csv等文件，非常方便。

```
import pandas as pd
from pandas import Series, DataFrame
score = DataFrame(pd.read_excel('data.xlsx'))
score.to_excel('data1.xlsx')
print score

```

需要说明的是，在运行的过程可能会存在缺少xlrd和openpyxl包的情况，到时候如果缺少了，可以在命令行模式下使用“pip install”命令来进行安装。

## 数据清洗

数据清洗是数据准备过程中必不可少的环节，Pandas也为我们提供了数据清洗的工具，在后面数据清洗的章节中会给你做详细的介绍，这里简单介绍下Pandas在数据清洗中的使用方法。

我还是以上面这个王者荣耀的数据为例。

```
data = {'Chinese': [66, 95, 93, 90,80],'English': [65, 85, 92, 88, 90],'Math': [30, 98, 96, 77, 90]}
df2 = DataFrame(data, index=['ZhangFei', 'GuanYu', 'ZhaoYun', 'HuangZhong', 'DianWei'], columns=['English', 'Math', 'Chinese'])

```

**在数据清洗过程中，一般都会遇到以下这几种情况，下面我来简单介绍一下。**

**1\. 删除 DataFrame 中的不必要的列或行**

Pandas提供了一个便捷的方法 drop() 函数来删除我们不想要的列或行。比如我们想把“语文”这列删掉。

```
df2 = df2.drop(columns=['Chinese'])

```

想把“张飞”这行删掉。

```
df2 = df2.drop(index=['ZhangFei'])

```

**2\. 重命名列名columns，让列表名更容易识别**

如果你想对DataFrame中的columns进行重命名，可以直接使用rename(columns=new\_names, inplace=True) 函数，比如我把列名Chinese改成YuWen，English改成YingYu。

```
df2.rename(columns={'Chinese': 'YuWen', 'English': 'Yingyu'}, inplace = True)

```

**3\. 去重复的值**

数据采集可能存在重复的行，这时只要使用drop\_duplicates()就会自动把重复的行去掉。

```
df = df.drop_duplicates() #去除重复行

```

**4\. 格式问题**

**更改数据格式**

这是个比较常用的操作，因为很多时候数据格式不规范，我们可以使用astype函数来规范数据格式，比如我们把Chinese字段的值改成str类型，或者int64可以这么写：

```
df2['Chinese'].astype('str')
df2['Chinese'].astype(np.int64)

```

**数据间的空格**

有时候我们先把格式转成了str类型，是为了方便对数据进行操作，这时想要删除数据间的空格，我们就可以使用strip函数：

```
#删除左右两边空格
df2['Chinese']=df2['Chinese'].map(str.strip)
#删除左边空格
df2['Chinese']=df2['Chinese'].map(str.lstrip)
#删除右边空格
df2['Chinese']=df2['Chinese'].map(str.rstrip)

```

如果数据里有某个特殊的符号，我们想要删除怎么办？同样可以使用strip函数，比如Chinese字段里有美元符号，我们想把这个删掉，可以这么写：

```
df2['Chinese']=df2['Chinese'].str.strip('$')

```

**大小写转换**

大小写是个比较常见的操作，比如人名、城市名等的统一都可能用到大小写的转换，在Python里直接使用upper(), lower(), title()函数，方法如下：

```
#全部大写
df2.columns = df2.columns.str.upper()
#全部小写
df2.columns = df2.columns.str.lower()
#首字母大写
df2.columns = df2.columns.str.title()

```

**查找空值**

数据量大的情况下，有些字段存在空值NaN的可能，这时就需要使用Pandas中的isnull函数进行查找。比如，我们输入一个数据表如下：

![](https://static001.geekbang.org/resource/image/34/ab/3440abb73e91e9f7a41dc2fbfeea44ab.png?wh=423*202)

如果我们想看下哪个地方存在空值NaN，可以针对数据表df进行df.isnull()，结果如下：

![](https://static001.geekbang.org/resource/image/5b/fe/5b52bca4eb6f00d51f72dcc5c6ce2afe.png?wh=391*161)

如果我想知道哪列存在空值，可以使用df.isnull().any()，结果如下：

![](https://static001.geekbang.org/resource/image/89/03/89cb71afc4f54a11ce1d4d05cd46bb03.png?wh=179*116)

## 使用apply函数对数据进行清洗

apply函数是Pandas中 **自由度非常高的函数**，使用频率也非常高。

比如我们想对name列的数值都进行大写转化可以用：

```
df['name'] = df['name'].apply(str.upper)

```

我们也可以定义个函数，在apply中进行使用。比如定义double\_df函数是将原来的数值\*2进行返回。然后对df1中的“语文”列的数值进行\*2处理，可以写成：

```
def double_df(x):
           return 2*x
df1[u'语文'] = df1[u'语文'].apply(double_df)

```

我们也可以定义更复杂的函数，比如对于DataFrame，我们新增两列，其中’new1’列是“语文”和“英语”成绩之和的m倍，'new2’列是“语文”和“英语”成绩之和的n倍，我们可以这样写：

```
def plus(df,n,m):
    df['new1'] = (df[u'语文']+df[u'英语']) * m
    df['new2'] = (df[u'语文']+df[u'英语']) * n
    return df
df1 = df1.apply(plus,axis=1,args=(2,3,))

```

其中axis=1代表按照列为轴进行操作，axis=0代表按照行为轴进行操作，args是传递的两个参数，即n=2, m=3，在plus函数中使用到了n和m，从而生成新的df。

## 数据统计

在数据清洗后，我们就要对数据进行统计了。

Pandas和NumPy一样，都有常用的统计函数，如果遇到空值NaN，会自动排除。

常用的统计函数包括：

![](https://static001.geekbang.org/resource/image/34/00/343ba98c1322dc0c013e07c87b157a00.jpg?wh=1800*3200)

表格中有一个describe()函数，统计函数千千万，describe()函数最简便。它是个统计大礼包，可以快速让我们对数据有个全面的了解。下面我直接使用df1.descirbe()输出结果为：

```
df1 = DataFrame({'name':['ZhangFei', 'GuanYu', 'a', 'b', 'c'], 'data1':range(5)})
print df1.describe()

```

![](https://static001.geekbang.org/resource/image/e4/83/e4a7a208a11d60dbcda6f3dbaff9a583.png?wh=205*250)

## 数据表合并

有时候我们需要将多个渠道源的多个数据表进行合并，一个DataFrame相当于一个数据库的数据表，那么多个DataFrame数据表的合并就相当于多个数据库的表合并。

比如我要创建两个DataFrame：

```
df1 = DataFrame({'name':['ZhangFei', 'GuanYu', 'a', 'b', 'c'], 'data1':range(5)})
df2 = DataFrame({'name':['ZhangFei', 'GuanYu', 'A', 'B', 'C'], 'data2':range(5)})

```

两个DataFrame数据表的合并使用的是merge()函数，有下面5种形式：

**1\. 基于指定列进行连接**

比如我们可以基于name这列进行连接。

```
df3 = pd.merge(df1, df2, on='name')

```

![](https://static001.geekbang.org/resource/image/22/2f/220ce1ea19c8f6f2668d3a8122989c2f.png?wh=862*227?wh=862*227)

**2\. inner内连接**

inner内链接是merge合并的默认情况，inner内连接其实也就是键的交集，在这里df1, df2相同的键是name，所以是基于name字段做的连接：

```
df3 = pd.merge(df1, df2, how='inner')

```

![](https://static001.geekbang.org/resource/image/22/2f/220ce1ea19c8f6f2668d3a8122989c2f.png?wh=862*227?wh=862*227)

**3\. left左连接**

左连接是以第一个DataFrame为主进行的连接，第二个DataFrame作为补充。

```
df3 = pd.merge(df1, df2, how='left')

```

![](https://static001.geekbang.org/resource/image/90/ac/9091a7406d5aa7a2980328d587fb42ac.png?wh=863*234)

**4\. right右连接**

右连接是以第二个DataFrame为主进行的连接，第一个DataFrame作为补充。

```
df3 = pd.merge(df1, df2, how='right')

```

![](https://static001.geekbang.org/resource/image/10/af/10f9f22f66f3745381d85d760f857baf.png?wh=863*245)

**5\. outer外连接**

外连接相当于求两个DataFrame的并集。

```
df3 = pd.merge(df1, df2, how='outer')

```

![](https://static001.geekbang.org/resource/image/67/8c/6737f6d4d66af0d75734cd140b5d198c.png?wh=864*346)

## 如何用SQL方式打开Pandas

Pandas的DataFrame数据类型可以让我们像处理数据表一样进行操作，比如数据表的增删改查，都可以用Pandas工具来完成。不过也会有很多人记不住这些Pandas的命令，相比之下还是用SQL语句更熟练，用SQL对数据表进行操作是最方便的，它的语句描述形式更接近我们的自然语言。

事实上，在Python里可以直接使用SQL语句来操作Pandas。

这里给你介绍个工具：pandasql。

pandasql 中的主要函数是 sqldf，它接收两个参数：一个SQL 查询语句，还有一组环境变量globals()或locals()。这样我们就可以在Python里，直接用SQL语句中对DataFrame进行操作，举个例子：

```
import pandas as pd
from pandas import DataFrame
from pandasql import sqldf, load_meat, load_births
df1 = DataFrame({'name':['ZhangFei', 'GuanYu', 'a', 'b', 'c'], 'data1':range(5)})
pysqldf = lambda sql: sqldf(sql, globals())
sql = "select * from df1 where name ='ZhangFei'"
print pysqldf(sql)

```

运行结果：

```
   data1      name
0      0  ZhangFei

```

上面这个例子中，我们是对“name='ZhangFei”“的行进行了输出。当然你会看到我们用到了lambda，lambda在python中算是使用频率很高的，那lambda是用来做什么的呢？它实际上是用来定义一个匿名函数的，具体的使用形式为：

```
 lambda argument_list: expression

```

这里argument\_list是参数列表，expression是关于参数的表达式，会根据expression表达式计算结果进行输出返回。

在上面的代码中，我们定义了：

```
pysqldf = lambda sql: sqldf(sql, globals())

```

在这个例子里，输入的参数是sql，返回的结果是sqldf对sql的运行结果，当然sqldf中也输入了globals全局参数，因为在sql中有对全局参数df1的使用。

## 总结

和NumPy一样，Pandas有两个非常重要的数据结构：Series和DataFrame。使用Pandas可以直接从csv或xlsx等文件中导入数据，以及最终输出到excel表中。

我重点介绍了数据清洗中的操作，当然Pandas中同样提供了多种数据统计的函数。

最后我们介绍了如何将数据表进行合并，以及在Pandas中使用SQL对数据表更方便地进行操作。

Pandas包与NumPy工具库配合使用可以发挥巨大的威力，正是有了Pandas工具，Python做数据挖掘才具有优势。

![](https://static001.geekbang.org/resource/image/74/cd/74884960677548b08acdc919c13460cd.jpg?wh=3200*1800)

我们来回顾一下今天的内容，在Pandas中，最主要的数据结构是什么？它都提供了哪些函数，可以帮我们做数据清洗？你可以自己描述一下吗？

## 练习题

对于下表的数据，请使用Pandas中的DataFrame进行创建，并对数据进行清洗。同时新增一列“总和”计算每个人的三科成绩之和。

![](https://static001.geekbang.org/resource/image/25/80/25b34b3f6227a945500074e05ea49e80.png?wh=423*241)

欢迎在评论区与我分享你的答案。

如果你觉着这篇文章有价值，欢迎点击“请朋友读”，把这篇文章分享给你的朋友或者同事。