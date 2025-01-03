今天我带你用AdaBoost算法做一个实战项目。AdaBoost不仅可以用于分类问题，还可以用于回归分析。

我们先做个简单回忆，什么是分类，什么是回归呢？实际上分类和回归的本质是一样的，都是对未知事物做预测。不同之处在于输出结果的类型，分类输出的是一个离散值，因为物体的分类数有限的，而回归输出的是连续值，也就是在一个区间范围内任何取值都有可能。

这次我们的主要目标是使用AdaBoost预测房价，这是一个回归问题。除了对项目进行编码实战外，我希望你能掌握：

1. AdaBoost工具的使用，包括使用AdaBoost进行分类，以及回归分析。

2. 使用其他的回归工具，比如决策树回归，对比AdaBoost回归和决策树回归的结果。


## 如何使用AdaBoost工具

我们可以直接在sklearn中使用AdaBoost。如果我们要用AdaBoost进行分类，需要在使用前引用代码：

```
from sklearn.ensemble import AdaBoostClassifier

```

我们之前讲到过，如果你看到了Classifier这个类，一般都会对应着Regressor类。AdaBoost也不例外，回归工具包的引用代码如下：

```
from sklearn.ensemble import AdaBoostRegressor

```

我们先看下如何在sklearn中创建AdaBoost分类器。

我们需要使用AdaBoostClassifier(base\_estimator=None, n\_estimators=50, learning\_rate=1.0, algorithm=’SAMME.R’, random\_state=None)这个函数，其中有几个比较主要的参数，我分别来讲解下：

1. base\_estimator：代表的是弱分类器。在AdaBoost的分类器和回归器中都有这个参数，在AdaBoost中默认使用的是决策树，一般我们不需要修改这个参数，当然你也可以指定具体的分类器。

2. n\_estimators：算法的最大迭代次数，也是分类器的个数，每一次迭代都会引入一个新的弱分类器来增加原有的分类器的组合能力。默认是50。

3. learning\_rate：代表学习率，取值在0-1之间，默认是1.0。如果学习率较小，就需要比较多的迭代次数才能收敛，也就是说学习率和迭代次数是有相关性的。当你调整learning\_rate的时候，往往也需要调整n\_estimators这个参数。

4. algorithm：代表我们要采用哪种boosting算法，一共有两种选择：SAMME 和SAMME.R。默认是SAMME.R。这两者之间的区别在于对弱分类权重的计算方式不同。

5. random\_state：代表随机数种子的设置，默认是None。随机种子是用来控制随机模式的，当随机种子取了一个值，也就确定了一种随机规则，其他人取这个值可以得到同样的结果。如果不设置随机种子，每次得到的随机数也就不同。


那么如何创建AdaBoost回归呢？

我们可以使用AdaBoostRegressor(base\_estimator=None, n\_estimators=50, learning\_rate=1.0, loss=‘linear’, random\_state=None)这个函数。

你能看出来回归和分类的参数基本是一致的，不同点在于回归算法里没有algorithm这个参数，但多了一个loss参数。

loss代表损失函数的设置，一共有3种选择，分别为linear、square和exponential，它们的含义分别是线性、平方和指数。默认是线性。一般采用线性就可以得到不错的效果。

创建好AdaBoost分类器或回归器之后，我们就可以输入训练集对它进行训练。我们使用fit函数，传入训练集中的样本特征值train\_X和结果train\_y，模型会自动拟合。使用predict函数进行预测，传入测试集中的样本特征值test\_X，然后就可以得到预测结果。

## 如何用AdaBoost对房价进行预测

了解了AdaBoost工具包之后，我们看下sklearn中自带的波士顿房价数据集。

这个数据集一共包括了506条房屋信息数据，每一条数据都包括了13个指标，以及一个房屋价位。

13个指标的含义，可以参考下面的表格：

![](https://static001.geekbang.org/resource/image/42/b7/426dec532f34d7f458e36ee59a6617b7.png?wh=468*447)

这些指标分析得还是挺细的，但实际上，我们不用关心具体的含义，要做的就是如何通过这13个指标推导出最终的房价结果。

如果你学习了之前的算法实战，这个数据集的预测并不复杂。

首先加载数据，将数据分割成训练集和测试集，然后创建AdaBoost回归模型，传入训练集数据进行拟合，再传入测试集数据进行预测，就可以得到预测结果。最后将预测的结果与实际结果进行对比，得到两者之间的误差。具体代码如下：

```
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.datasets import load_boston
from sklearn.ensemble import AdaBoostRegressor
# 加载数据
data=load_boston()
# 分割数据
train_x, test_x, train_y, test_y = train_test_split(data.data, data.target, test_size=0.25, random_state=33)
# 使用AdaBoost回归模型
regressor=AdaBoostRegressor()
regressor.fit(train_x,train_y)
pred_y = regressor.predict(test_x)
mse = mean_squared_error(test_y, pred_y)
print("房价预测结果 ", pred_y)
print("均方误差 = ",round(mse,2))

```

运行结果：

```
房价预测结果  [20.2        10.4137931  14.63820225 17.80322581 24.58931298 21.25076923
 27.52222222 17.8372093  31.79642857 20.86428571 27.87431694 31.09142857
 12.81666667 24.13131313 12.81666667 24.58931298 17.80322581 17.66333333
 27.83       24.58931298 17.66333333 20.90823529 20.10555556 20.90823529
 28.20877193 20.10555556 21.16882129 24.58931298 13.27619048 31.09142857
 17.08095238 26.19217391  9.975      21.03404255 26.74583333 31.09142857
 25.83960396 11.859375   13.38235294 24.58931298 14.97931034 14.46699029
 30.12777778 17.66333333 26.19217391 20.10206186 17.70540541 18.45909091
 26.19217391 20.10555556 17.66333333 33.31025641 14.97931034 17.70540541
 24.64421053 20.90823529 25.83960396 17.08095238 24.58931298 21.43571429
 19.31617647 16.33733333 46.04888889 21.25076923 17.08095238 25.83960396
 24.64421053 11.81470588 17.80322581 27.63636364 23.59731183 17.94444444
 17.66333333 27.7253886  20.21465517 46.04888889 14.97931034  9.975
 17.08095238 24.13131313 21.03404255 13.4        11.859375   26.19214286
 21.25076923 21.03404255 47.11395349 16.33733333 43.21111111 31.65730337
 30.12777778 20.10555556 17.8372093  18.40833333 14.97931034 33.31025641
 24.58931298 22.88813559 18.27179487 17.80322581 14.63820225 21.16882129
 26.91538462 24.64421053 13.05       14.97931034  9.975      26.19217391
 12.81666667 26.19214286 49.46511628 13.27619048 17.70540541 25.83960396
 31.09142857 24.13131313 21.25076923 21.03404255 26.91538462 21.03404255
 21.16882129 17.8372093  12.81666667 21.03404255 21.03404255 17.08095238
 45.16666667]
均方误差 =  18.05

```

这个数据集是比较规范的，我们并不需要在数据清洗，数据规范化上花太多精力，代码编写起来比较简单。

同样，我们可以使用不同的回归分析模型分析这个数据集，比如使用决策树回归和KNN回归。

编写代码如下：

```
# 使用决策树回归模型
dec_regressor=DecisionTreeRegressor()
dec_regressor.fit(train_x,train_y)
pred_y = dec_regressor.predict(test_x)
mse = mean_squared_error(test_y, pred_y)
print("决策树均方误差 = ",round(mse,2))
# 使用KNN回归模型
knn_regressor=KNeighborsRegressor()
knn_regressor.fit(train_x,train_y)
pred_y = knn_regressor.predict(test_x)
mse = mean_squared_error(test_y, pred_y)
print("KNN均方误差 = ",round(mse,2))

```

运行结果：

```
决策树均方误差 =  23.84
KNN均方误差 =  27.87

```

你能看到相比之下，AdaBoost的均方误差更小，也就是结果更优。虽然AdaBoost使用了弱分类器，但是通过50个甚至更多的弱分类器组合起来而形成的强分类器，在很多情况下结果都优于其他算法。因此AdaBoost也是常用的分类和回归算法之一。

## AdaBoost与决策树模型的比较

在sklearn中AdaBoost默认采用的是决策树模型，我们可以随机生成一些数据，然后对比下AdaBoost中的弱分类器（也就是决策树弱分类器）、决策树分类器和AdaBoost模型在分类准确率上的表现。

如果想要随机生成数据，我们可以使用sklearn中的make\_hastie\_10\_2函数生成二分类数据。假设我们生成12000个数据，取前2000个作为测试集，其余作为训练集。

有了数据和训练模型后，我们就可以编写代码。我设置了AdaBoost的迭代次数为200，代表AdaBoost由200个弱分类器组成。针对训练集，我们用三种模型分别进行训练，然后用测试集进行预测，并将三个分类器的错误率进行可视化对比，可以看到这三者之间的区别：

```
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.metrics import zero_one_loss
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import  AdaBoostClassifier
# 设置AdaBoost迭代次数
n_estimators=200
# 使用
X,y=datasets.make_hastie_10_2(n_samples=12000,random_state=1)
# 从12000个数据中取前2000行作为测试集，其余作为训练集
train_x, train_y = X[2000:],y[2000:]
test_x, test_y = X[:2000],y[:2000]
# 弱分类器
dt_stump = DecisionTreeClassifier(max_depth=1,min_samples_leaf=1)
dt_stump.fit(train_x, train_y)
dt_stump_err = 1.0-dt_stump.score(test_x, test_y)
# 决策树分类器
dt = DecisionTreeClassifier()
dt.fit(train_x,  train_y)
dt_err = 1.0-dt.score(test_x, test_y)
# AdaBoost分类器
ada = AdaBoostClassifier(base_estimator=dt_stump,n_estimators=n_estimators)
ada.fit(train_x,  train_y)
# 三个分类器的错误率可视化
fig = plt.figure()
# 设置plt正确显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']
ax = fig.add_subplot(111)
ax.plot([1,n_estimators],[dt_stump_err]*2, 'k-', label=u'决策树弱分类器 错误率')
ax.plot([1,n_estimators],[dt_err]*2,'k--', label=u'决策树模型 错误率')
ada_err = np.zeros((n_estimators,))
# 遍历每次迭代的结果 i为迭代次数, pred_y为预测结果
for i,pred_y in enumerate(ada.staged_predict(test_x)):
     # 统计错误率
    ada_err[i]=zero_one_loss(pred_y, test_y)
# 绘制每次迭代的AdaBoost错误率
ax.plot(np.arange(n_estimators)+1, ada_err, label='AdaBoost Test 错误率', color='orange')
ax.set_xlabel('迭代次数')
ax.set_ylabel('错误率')
leg=ax.legend(loc='upper right',fancybox=True)
plt.show()

```

运行结果：

![](https://static001.geekbang.org/resource/image/8a/35/8ad4bb6a8c6848f2061ff6f442568735.png?wh=865*659)

从图中你能看出来，弱分类器的错误率最高，只比随机分类结果略好，准确率稍微大于50%。决策树模型的错误率明显要低很多。而AdaBoost模型在迭代次数超过25次之后，错误率有了明显下降，经过125次迭代之后错误率的变化形势趋于平缓。

因此我们能看出，虽然单独的一个决策树弱分类器效果不好，但是多个决策树弱分类器组合起来形成的AdaBoost分类器，分类效果要好于决策树模型。

## 总结

今天我带你用AdaBoost回归分析对波士顿房价进行了预测。因为这是个回归分析的问题，我们直接使用sklearn中的AdaBoostRegressor即可。如果是分类，我们使用AdaBoostClassifier。

另外我们将AdaBoost分类器、弱分类器和决策树分类器做了对比，可以看出经过多个弱分类器组合形成的AdaBoost强分类器，准确率要明显高于决策树算法。所以AdaBoost的优势在于框架本身，它通过一种迭代机制让原本性能不强的分类器组合起来，形成一个强分类器。

其实在现实工作中，我们也能找到类似的案例。IBM服务器追求的是单个服务器性能的强大，比如打造超级服务器。而Google在创建集群的时候，利用了很多PC级的服务器，将它们组成集群，整体性能远比一个超级服务器的性能强大。

再比如我们讲的“三个臭皮匠，顶个诸葛亮”，也就是AdaBoost的价值所在。

![](https://static001.geekbang.org/resource/image/6c/17/6c4fcd75a65dc354bc65590c18e77d17.png?wh=1638*822)

今天我们用AdaBoost分类器与决策树分类做对比的时候，使用到了sklearn中的make\_hastie\_10\_2函数生成数据。实际上在 [第19篇](http://time.geekbang.org/column/article/79072)，我们对泰坦尼克号的乘客做生存预测的时候，也讲到了决策树工具的使用。你能不能编写代码，使用AdaBoost算法对泰坦尼克号乘客的生存做预测，看看它和决策树模型，谁的准确率更高？

你也可以把这篇文章分享给你的朋友或者同事，一起切磋一下。