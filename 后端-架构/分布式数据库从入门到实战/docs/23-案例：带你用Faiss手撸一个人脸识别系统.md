你好，我是彭旭。

通过前面两节课的学习，你应该已经学会了如何使用Faiss来实现向量化检索，这节课，我们就用Faiss来搭建一个人脸识别系统。

## 需求场景分析

在日常生活中，我们会碰到各种各样的人脸识别场景，比如门禁系统、人脸门店客流系统、人脸支付等。

其实这些场景，可以归纳为两种类型的人脸识别，第一种是1对1的人脸对比，比如手机的人脸解锁、支付等。第二种是1对N的人脸搜索，比如人脸门禁、人脸客流系统等。这里我们以人脸门店客流系统为例，来搭建一个人脸搜索系统。

我来简单介绍下这个人脸门店客流系统。它能利用人脸识别技术，实时统计和分析门店的客流量。

我们可以在店门口安装一个摄像头，摄像头会捕捉人脸，然后保存为图片。

图片通过人脸识别系统后，会生成一个唯一的FaceId。后续，相同人脸的图片会通过人脸识别系统关联到同一个FaceId，这样就能用来分析门店客流的PV、UV等数据。

这个FaceId也可以跟会员的资料绑定，一旦这个用户进入到门店，系统就能用摄像头拍摄到的图片，进行人脸识别，就知道是哪个会员进店了，然后在收银台显示会员的信息，如果搭建了CDP客户画像系统，收银员还可以根据会员的标签、画像等，了解客户的喜好，更好地为会员做推荐与服务。

好了，接下来我们先看一下如何搭建一个人脸识别服务。

## 人脸识别服务搭建

我们仍然使用Python来搭建一个人脸识别的服务，这个服务要提供一个HTTP接口，用来识别人脸，返回对应的FaceId或者会员ID，简单分析下来，服务处理流程分为两步。

1. 初始化：从文件夹读取图片，识别图片中的人脸，将人脸向量化后，构建Faiss索引。
2. 人脸识别：从HTTP接口读取图片文件，识别图片中的人脸，将人脸向量化后，检索Faiss索引。

### 依赖库安装

首先，图片中的人脸定位与人脸向量化，我们要用到一个叫做face\_recognition的Python库。你可以使用pip install face\_recognition来安装这个库，不过这个库依赖cmake和dlib，比如在我的Mac上，可以使用如下命令安装。

```shell
brew install cmake

pip install dlib  -i https://mirrors.aliyun.com/pypi/simple/

pip install face_recognition -i https://mirrors.aliyun.com/pypi/simple/

```

### 数据准备

我从网上找了一个CASIA-FaceV5亚洲人脸数据集，截取了100个人的数据，每个人有5张左右的人脸图片，你可以从 [这里](https://pan.baidu.com/s/18kAZInUofiei2Zpt2JHR3A?pwd=5n6b) 下载（提取码: 5n6b）。

构建Faiss索引的时候，每个人只会加载一张图片到索引，所以我又从数据集里，为每个人挑选了一张照片，形成一个Faiss的底库照片集，你可以从 [这里](https://pan.baidu.com/s/1oERVM7-msFIqsHhcxPDhCw?pwd=m4nx) 下载（提取码: m4nx）。

当然，你也可以把每个人的照片向量化之后，加载到Faiss索引。这样可以提升匹配的准确度，但是对内存占用与检索时间都会带来负面影响。

### 图片人脸定位与识别

face\_recognition能够从图片文件中定位人脸，然后提取人脸特征。提取人脸特征其实就是向量化的过程，它会将人脸转化为128维的向量。

下面的代码演示了从读取图片文件，到将人脸转化为128维向量的过程。

```shell
import face_recognition

image_path = os.path.join(face_dir, filename)
image = face_recognition.load_image_file(image_path)
#从图片中定位人脸
face_locations = face_recognition.face_locations(image) # (top, right, bottom, left)
# 提取人脸特征
face_encodings = face_recognition.face_encodings(image, face_locations)

```

### 使用Faiss加载人脸向量构建索引

得到人脸向量化数组后，我们将其加载到Faiss索引中。在这个场景中，我们对搜索精确度的要求较高，所以我们构建一个Flat类型的索引，使用L2的度量方式。

这里我们假设加载的图片文件的名字就是FaceId。因为我们检索匹配到人脸后，需要返回FaceId或者会员ID，所以我们需要用到Faiss的一个IndexIDMap类，用来映射向量索引和FaceId。也就是当我们检索匹配到相同的人脸后，检索结果可以返回这个FaceId。

然后将人脸向量添加到Faiss索引的时候，我们也会过滤掉没有人脸，或者有多个人脸的图片，下面就是构建Faiss人脸索引的代码。

```shell
import faiss

# 向量128维度
d = 128
# 创建faiss索引
index = faiss.IndexIDMap(faiss.IndexFlatL2(d))

# 读取不到人脸或者超过1个人脸的都过滤掉
if len(face_encodings) == 1:
    index.add_with_ids(np.array(face_encodings), np.array(file_name.split("_")[0]))


```

### 人脸检索

最后，我们构建一个HTTP接口，接收一个图片类型文件，同样使用face\_recognition定位图片中的人脸，将人脸向量化后检索Faiss，返回对应的FaceId。代码如下：

```shell
app = Flask("face_recognition")

@app.route('/recognize', methods=['POST'])
def recognize_face_file():
    # 从请求中获取上传的图片文件
    image_file = request.files['image']
    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)  # (top, right, bottom, left)
    # 提取人脸特征
    face_encodings = face_recognition.face_encodings(image, face_locations)
    # 将人脸特征转换为 numpy 数组
    face_encodings_np = np.array(face_encodings)
    D, I = index.search(face_encodings_np, k=1)
    # 获取最相似人脸的 ID
    similar_face_id = I[0][0]
    # 返回结果
    return jsonify({'result': str(similar_face_id)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

```

你可以看到我们使用Flask搭建了一个HTTP服务，并在5000端口监听人脸识别的请求。

到这里，我们就搭建完成了一个简易的人脸识别服务，你可以在 [这里](https://github.com/ZHAMoonlight/referencebook/blob/master/python/ls23/ls22_face_recoginize.py) 找到完整的代码。

### 测试

你还可以用数据集里面的图片作为测试图片，看到返回的结果，就是测试图片名的id前缀。

```shell
curl -X POST -F "image=@/Users/xupeng/Downloads/CASIA-FaceV5 (000-099)/095/095_0.bmp" http://127.0.0.1:5000/recognize_file

```

![图片](https://static001.geekbang.org/resource/image/4e/6e/4eea562a6749ba688a9b1468d9f41c6e.png?wh=1536x79)

在数据量不大的情况下，我们的人脸服务，检索速度、内存占用等，都没什么问题。

但是总有一天，数据量会增大到一个服务器的内存无法存储，或者检索时间无法满足业务需求，这时候有什么解决办法呢？

## 使用多服务：数据分片

第一个方法是做服务分片。

首先，将需要检索的、包含人脸的图片分片。比如按图片归属的地区或者门店分片。以按门店将图片分片为例，假设有3台服务器，那么流程就是这样的。

1. 每台服务器上可以启动一个或者多个人脸检索的HTTP服务。
2. 维护一个门店到HTTP服务的映射关系，比如 {“门店A”:“127.0.0.1:5000”,“门店B”:“127.0.0.2:5000”}。
3. 基于这个映射关系，HTTP服务加载图片构建Faiss索引时，只加载对应门店的图片，这样就减少了单台机器需要加载图片的数量，减少了内存占用，也就是利用集群的能力，来提升内存配额。
4. 图片检索时，同样是某个门店拍摄到的图片，根据门店从第2步维护的映射关系中找到对应的HTTP服务地址，只需要调用该HTTP服务，检索对应门店的Faiss索引即可，这样需要检索的图片也变少了，检索性能也提升了。

为了实现高可用，同一个门店，还可以部署多个HTTP服务，使用Nginx做负载均衡。

当然，数据分片会带来的一个问题就是跨门店会员的识别，比如会员张三之前一直在门店A消费，突然某一天出差到了门店B所在区域，这时候张三去门店B消费，门店B部署的人脸检索HTTP服务由于没有加载张三的人脸图片，所以无法识别出张三，而认为这是一个新客户。

在这种场景下，如果业务上需要保障识别的成功率，我们也可以再检索一遍其他门店的人脸检索HTTP服务，解决跨门店消费的问题。不过带来的影响就是资源占用稍多以及检索时长增加。

前面我们也提到过，一台16G以上的服务器，也基本都能承载百万级向量数据的索引与检索。如果我们需要检索的人脸图片数量，能够由单台服务器支撑，只是可能检索时间较长。

不过没关系，Faiss还提供了另外一种索引分片的解决方案。

## 使用Faiss索引分片

![图片](https://static001.geekbang.org/resource/image/de/f9/de8d9fe51b47db7b80f9e96117a036f9.png?wh=2044x1110)

Faiss索引分片的逻辑，其实是先将图片向量化，聚簇归类，那么比较相近的向量会被归类到同一个Voronoi Cell，也就是分区，类似将一个平面划分为多个不规则的多边形，每个多边形有一个“形心”。检索的时候，我们先用检索向量，找到与他最近的“形心”，然后只需要在“形心”对应的多边形内检索，找到最近的向量即可。

你应该也发现了，这个其实是用牺牲一定准确度的方式来提升整体的检索效率。使用Faiss分片也很简单，我们前面介绍的IndexIVFFlat就是一种分片索引，我们只需要像下面代码片段一样，调整一下Faiss构建索引的方式。

```shell
#创建索引
index_need_train = faiss.IndexIVFFlat(quantizer, d, nlist)
index = faiss.IndexIDMap(index_need_train)
#训练索引，也就是归类，构建形心
index.train(np.array(face_encodings_list))
#将数据添加到索引
index.add_with_ids(np.array(face_encodings_list), face_id_list)

```

你可以从 [这里](https://github.com/ZHAMoonlight/referencebook/blob/master/python/ls23/ls23_faiss_index_partition.py) 找到完整的代码，注意，在将数据添加到索引之前，需要先对索引进行训练，其实训练一般也都用真实的需要添加到索引的数据，这样能够更好地归类数据。

同样，你也可以使用我们之前的curl命令对索引进行检索测试，测试之后可以发现，检索的准确度与之前Flat类型索引的测试结果相差不大。

## 小结

人脸识别中的准确度主要取决于三个关键步骤，人脸检测、特征提取和向量检索的精准度。

首先，人脸检测模型用来确定图像中是否存在人脸，并标定其位置。然后，特征提取模型将人脸转换为一个特征向量，这个向量捕捉了人脸的关键信息。最后，我们通过Faiss相似度检索，将这个特征向量与数据库中的其他向量进行比较，计算它们之间的相似度，从而确定最相似的人脸身份。

一旦将人脸转换为特征向量，向量数据库的作用就是度量这些向量之间的距离，即它们之间的相似程度。通过计算特征向量之间的距离，我们可以找到与输入特征向量最接近的向量，从而确定人脸的身份。

当人脸向量所需内存增加到单台服务器无法支撑，或者检索时间过长，可以对数据或者索引进行分片来“分而治之”。这节课我介绍了两个分片方案，部署多服务和使用Faiss自带的索引分片能力。不过分片对检索的准确性会有一定的影响。

## 思考题

你觉得还有哪些办法，可以提升人脸识别的准确性与性能？

欢迎你在留言区和我交流。如果觉得有所收获，也可以把课程分享给更多的朋友一起学习。欢迎你加入我们的 [读者交流群](http://jinshuju.net/f/QX5mGO)，我们下节课见！