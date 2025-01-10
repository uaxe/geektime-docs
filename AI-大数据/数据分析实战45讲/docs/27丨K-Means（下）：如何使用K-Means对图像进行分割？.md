上节课，我讲解了K-Means的原理，并且用K-Means对20支亚洲球队进行了聚类，分成3个梯队。今天我们继续用K-Means进行聚类的实战。聚类的一个常用场景就是对图像进行分割。

图像分割就是利用图像自身的信息，比如颜色、纹理、形状等特征进行划分，将图像分割成不同的区域，划分出来的每个区域就相当于是对图像中的像素进行了聚类。单个区域内的像素之间的相似度大，不同区域间的像素差异性大。这个特性正好符合聚类的特性，所以你可以把图像分割看成是将图像中的信息进行聚类。当然聚类只是分割图像的一种方式，除了聚类，我们还可以基于图像颜色的阈值进行分割，或者基于图像边缘的信息进行分割等。

## 将微信开屏封面进行分割

上节课，我讲了sklearn工具包中的K-Means算法使用，我们现在用K-Means算法对微信页面进行分割。微信开屏图如下所示：

![](https://static001.geekbang.org/resource/image/50/a2/50457e4e1fbd288c125364a6904774a2.png?wh=762*1355)

我们先设定下聚类的流程，聚类的流程和分类差不多，如图所示：

![](https://static001.geekbang.org/resource/image/8a/78/8af94562f6bd3ac42036ec47f5ad2578.jpg?wh=2373*1087)

在准备阶段里，我们需要对数据进行加载。因为处理的是图像信息，我们除了要获取图像数据以外，还需要获取图像的尺寸和通道数，然后基于图像中每个通道的数值进行数据规范化。这里我们需要定义个函数load\_data，来帮我们进行图像加载和数据规范化。代码如下：

```
# 加载图像，并对数据进行规范化
def load_data(filePath):
    # 读文件
    f = open(filePath,'rb')
    data = []
    # 得到图像的像素值
    img = image.open(f)
    # 得到图像尺寸
    width, height = img.size
    for x in range(width):
        for y in range(height):
            # 得到点(x,y)的三个通道值
            c1, c2, c3 = img.getpixel((x, y))
            data.append([c1, c2, c3])
    f.close()
    # 采用Min-Max规范化
    mm = preprocessing.MinMaxScaler()
    data = mm.fit_transform(data)
    return np.mat(data), width, height

```

因为jpg格式的图像是三个通道(R,G,B)，也就是一个像素点具有3个特征值。这里我们用c1、c2、c3来获取平面坐标点(x,y)的三个特征值，特征值是在0-255之间。

为了加快聚类的收敛，我们需要采用Min-Max规范化对数据进行规范化。我们定义的load\_data函数返回的结果包括了针对(R,G,B)三个通道规范化的数据，以及图像的尺寸信息。在定义好load\_data函数后，我们直接调用就可以得到相关信息，代码如下：

```
# 加载图像，得到规范化的结果img，以及图像尺寸
img, width, height = load_data('./weixin.jpg')

```

假设我们想要对图像分割成2部分，在聚类阶段，我们可以将聚类数设置为2，这样图像就自动聚成2类。代码如下：

```
# 用K-Means对图像进行2聚类
kmeans =KMeans(n_clusters=2)
kmeans.fit(img)
label = kmeans.predict(img)
# 将图像聚类结果，转化成图像尺寸的矩阵
label = label.reshape([width, height])
# 创建个新图像pic_mark，用来保存图像聚类的结果，并设置不同的灰度值
pic_mark = image.new("L", (width, height))
for x in range(width):
    for y in range(height):
        # 根据类别设置图像灰度, 类别0 灰度值为255， 类别1 灰度值为127
        pic_mark.putpixel((x, y), int(256/(label[x][y]+1))-1)
pic_mark.save("weixin_mark.jpg", "JPEG")

```

代码中有一些参数，我来给你讲解一下这些参数的作用和设置方法。

我们使用了fit和predict这两个函数来做数据的训练拟合和预测，因为传入的参数是一样的，我们可以同时进行fit和predict操作，这样我们可以直接使用fit\_predict(data)得到聚类的结果。得到聚类的结果label后，实际上是一个一维的向量，我们需要把它转化成图像尺寸的矩阵。label的聚类结果是从0开始统计的，当聚类数为2的时候，聚类的标识label=0或者1。

如果你想对图像聚类的结果进行可视化，直接看0和1是看不出来的，还需要将0和1转化为灰度值。灰度值一般是在0-255的范围内，我们可以将label=0设定为灰度值255，label=1设定为灰度值127。具体方法是用int(256/(label\[x\]\[y\]+1))-1。可视化的时候，主要是通过设置图像的灰度值进行显示。所以我们把聚类label=0的像素点都统一设置灰度值为255，把聚类label=1的像素点都统一设置灰度值为127。原来图像的灰度值是在0-255之间，现在就只有2种颜色（也就是灰度为255，和灰度127）。

有了这些灰度信息，我们就可以用image.new创建一个新的图像，用putpixel函数对新图像的点进行灰度值的设置，最后用save函数保存聚类的灰度图像。这样你就可以看到聚类的可视化结果了，如下图所示：

![](https://static001.geekbang.org/resource/image/94/6b/9420b9bedf2e3514b0624543a69fb06b.png?wh=762*1355)

上面是分割成2个部分的分割可视化，完整代码见 [这里](https://github.com/cystanford/kmeans/blob/master/kmeans1.py)。

[https://github.com/cystanford/kmeans/blob/master/kmeans1.py](https://github.com/cystanford/kmeans/blob/master/kmeans1.py)

如果我们想要分割成16个部分，该如何对不同分类设置不同的颜色值呢？这里需要用到skimage工具包，它是图像处理工具包。你需要使用pip install scikit-image来进行安装。

这段代码可以将聚类标识矩阵转化为不同颜色的矩阵：

```
from skimage import color
# 将聚类标识矩阵转化为不同颜色的矩阵
label_color = (color.label2rgb(label)*255).astype(np.uint8)
label_color = label_color.transpose(1,0,2)
images = image.fromarray(label_color)
images.save('weixin_mark_color.jpg')

```

代码中，我使用skimage中的label2rgb函数来将label分类标识转化为颜色数值，因为我们的颜色值范围是\[0,255\]，所以还需要乘以255进行转化，最后再转化为np.uint8类型。unit8类型代表无符号整数，范围是0-255之间。

得到颜色矩阵后，你可以把它输出出来，这时你发现输出的图像是颠倒的，原因可能是图像源拍摄的时候本身是倒置的。我们需要设置三维矩阵的转置，让第一维和第二维颠倒过来，也就是使用transpose(1,0,2)，将原来的(0,1,2）顺序转化为(1,0,2)顺序，即第一维和第二维互换。

最后我们使用fromarray函数，它可以通过矩阵来生成图片，并使用save进行保存。

最后得到的分类标识颜色化图像是这样的：

![](https://static001.geekbang.org/resource/image/d2/b7/d26df5f1ed26cca53118a99aa04484b7.png?wh=541*959)

完整的代码见 [这里](https://github.com/cystanford/kmeans/blob/master/kmeans2.py)。

[https://github.com/cystanford/kmeans/blob/master/kmeans2.py](https://github.com/cystanford/kmeans/blob/master/kmeans2.py)

刚才我们做的是聚类的可视化。如果我们想要看到对应的原图，可以将每个簇（即每个类别）的点的RGB值设置为该簇质心点的RGB值，也就是簇内的点的特征均为质心点的特征。

我给出了完整的代码，代码中，我可以把范围为0-255的数值投射到1-256数值之间，方法是对每个数值进行加1，你可以自己来运行下：

```
# -*- coding: utf-8 -*-
# 使用K-means对图像进行聚类，并显示聚类压缩后的图像
import numpy as np
import PIL.Image as image
from sklearn.cluster import KMeans
from sklearn import preprocessing
import matplotlib.image as mpimg
# 加载图像，并对数据进行规范化
def load_data(filePath):
    # 读文件
    f = open(filePath,'rb')
    data = []
    # 得到图像的像素值
    img = image.open(f)
    # 得到图像尺寸
    width, height = img.size
    for x in range(width):
        for y in range(height):
            # 得到点(x,y)的三个通道值
            c1, c2, c3 = img.getpixel((x, y))
            data.append([(c1+1)/256.0, (c2+1)/256.0, (c3+1)/256.0])
    f.close()
    return np.mat(data), width, height
# 加载图像，得到规范化的结果imgData，以及图像尺寸
img, width, height = load_data('./weixin.jpg')
# 用K-Means对图像进行16聚类
kmeans =KMeans(n_clusters=16)
label = kmeans.fit_predict(img)
# 将图像聚类结果，转化成图像尺寸的矩阵
label = label.reshape([width, height])
# 创建个新图像img，用来保存图像聚类压缩后的结果
img=image.new('RGB', (width, height))
for x in range(width):
    for y in range(height):
        c1 = kmeans.cluster_centers_[label[x, y], 0]
        c2 = kmeans.cluster_centers_[label[x, y], 1]
        c3 = kmeans.cluster_centers_[label[x, y], 2]
        img.putpixel((x, y), (int(c1*256)-1, int(c2*256)-1, int(c3*256)-1))
img.save('weixin_new.jpg')

```

完整代码见 [这里](https://github.com/cystanford/kmeans/blob/master/kmeans3.py)。

[https://github.com/cystanford/kmeans/blob/master/kmeans3.py](https://github.com/cystanford/kmeans/blob/master/kmeans3.py)

你可以看到我没有用到sklearn自带的MinMaxScaler，而是自己写了Min-Max规范化的公式。这样做的原因是我们知道RGB每个通道的数值在\[0,255\]之间，所以我们可以用每个通道的数值+1/256，这样数值就会在\[0,1\]之间。

对图像做了Min-Max空间变换之后，还可以对其进行反变换，还原出对应原图的通道值。

对于点(x,y)，我们找到它们所属的簇label\[x,y\]，然后得到这个簇的质心特征，用c1,c2,c3表示：

```
c1 = kmeans.cluster_centers_[label[x, y], 0]
c2 = kmeans.cluster_centers_[label[x, y], 1]
c3 = kmeans.cluster_centers_[label[x, y], 2]

```

因为c1, c2, c3对应的是数据规范化的数值，因此我们还需要进行反变换，即：

```
c1=int(c1*256)-1
c2=int(c2*256)-1
c3=int(c3*256)-1

```

然后用img.putpixel设置点(x,y)反变换后得到的特征值。最后用img.save保存图像。

## 总结

今天我们用K-Means做了图像的分割，其实不难发现K-Means聚类有个缺陷：聚类个数K值需要事先指定。如果你不知道该聚成几类，那么最好会给K值多设置几个，然后选择聚类结果最好的那个值。

通过今天的图像分割，你发现用K-Means计算的过程在sklearn中就是几行代码，大部分的工作还是在预处理和后处理上。预处理是将图像进行加载，数据规范化。后处理是对聚类后的结果进行反变换。

如果涉及到后处理，你可以自己来设定数据规范化的函数，这样反变换的函数比较容易编写。

另外我们还学习了如何在Python中如何对图像进行读写，具体的代码如下，上文中也有相应代码，你也可以自己对应下：

```
import PIL.Image as image
# 得到图像的像素值
img = image.open(f)
# 得到图像尺寸
width, height = img.size

```

这里会使用PIL这个工具包，它的英文全称叫Python Imaging Library，顾名思义，它是Python图像处理标准库。同时我们也使用到了skimage工具包（scikit-image），它也是图像处理工具包。用过Matlab的同学知道，Matlab处理起图像来非常方便。skimage可以和它相媲美，集成了很多图像处理函数，其中对不同分类标识显示不同的颜色。在Python中图像处理工具包，我们用的是skimage工具包。

这节课没有太多的理论概念，主要讲了K-Means聚类工具，数据规范化工具，以及图像处理工具的使用，并在图像分割中进行运用。其中涉及到的工具包比较多，你需要在练习的时候多加体会。当然不同尺寸的图像，K-Means运行的时间也是不同的。如果图像尺寸比较大，你可以事先进行压缩，长宽在200像素内运行速度会比较快，如果超过了1000像素，速度会很慢。

![](https://static001.geekbang.org/resource/image/5a/99/5a3f0dfaf5e6aaca1e96f488f8a10999.png?wh=1574*842)

今天我讲了如何使用K-Means聚类做图像分割，谈谈你使用的体会吧。另外我在 [GitHub](https://github.com/cystanford/kmeans/blob/master/baby.jpg) 上上传了一张baby.jpg的图片，请你编写代码用K-Means聚类方法将它分割成16个部分。

链接： [https://github.com/cystanford/kmeans/blob/master/baby.jpg](https://github.com/cystanford/kmeans/blob/master/baby.jpg)

欢迎在评论区与我分享你的答案，也欢迎点击“请朋友读”，把这篇文章分享给你的朋友或者同事。