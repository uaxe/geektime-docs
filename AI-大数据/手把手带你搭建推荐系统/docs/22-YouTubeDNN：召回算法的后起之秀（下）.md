你好，我是黄鸿波。

上节课我们讲了关于YouTubeDNN的召回模型，接下来，我们来看看如何用代码来实现它。

我们在做YouTubeDNN的时候，要把代码分成两个步骤，第一个步骤是对数据的清洗和处理，第二个步骤是搭建模型然后把数据放进去进行训练和预测。

## 数据的清洗和处理

先来讲数据部分。

按照YouTubeDNN论文来看，输入的数据是用户的信息、视频的ID序列、用户搜索的特征和一些地理信息等其他信息。到了基于文章内容的信息流产品中，就变成了用户ID、年龄、性别、城市、阅读的时间戳再加上视频的ID。我们把这些内容可以组合成YouTubeDNN需要的内容，最后处理成需要的Embedding。

由于前面没有太多的用户浏览数据，所以我先造了一批数据，数据集我会放到GitHub上（后续更新），数据的形式如下。

![图片](https://static001.geekbang.org/resource/image/ea/0a/eaeef45b0eb7e64c3f11c4a252f8120a.png?wh=1379x1424)

接下来我们就把这批数据处理成YouTubeDNN需要的形式。首先在recommendation-class项目中的utils目录下建立一个preprocess.py文件，作为处理数据的文件。

我们要处理这一批数据，需要下面五个步骤。

1. 加载数据集。
2. 处理数据特征。
3. 特征转化为模型输入。
4. 模型的搭建和训练。
5. 模型评估。

在正式写代码之前，需要安装几个库，如下。

```plain
deepctr
deepmatch
tensorflow==2.2
pandas

```

我们可以使用pip install加上库名来安装它们，也可以把它们放在一个叫requirements.txt的文件中，使用pip install -r进行安装。

安装完成之后，我们来写preprocess.py的代码。为了能够让你看得更明白，我在函数里加了一些注释，先上代码。

```plain
from tqdm import tqdm
import numpy as np
import random
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

def gen_data_set(data, negsample=0):
    data.sort_values("timestamp", inplace=True)  #是否用排序后的数据集替换原来的数据，这里是替换
    item_ids = data['item_id'].unique()    #item需要进行去重

    train_set = list()
    test_set = list()
    for reviewrID, hist in tqdm(data.groupby('user_id')):   #评价过,  历史记录
        pos_list = hist['item_id'].tolist()
        rating_list = hist['rating'].tolist()

        if negsample > 0:    #负样本
            candidate_set = list(set(item_ids) - set(pos_list))   #去掉用户看过的item项目
            neg_list = np.random.choice(candidate_set, size=len(pos_list) * negsample, replace=True)  #随机选择负采样样本
        for i in range(1, len(pos_list)):
            if i != len(pos_list) - 1:
                train_set.append((reviewrID, hist[::-1], pos_list[i], 1, len(hist[:: -1]), rating_list[i]))  #训练集和测试集划分  [::-1]从后玩前数
                for negi in range(negsample):
                    train_set.append((reviewrID, hist[::-1], neg_list[i * negsample + negi], 0, len(hist[::-1])))
            else:
                test_set.append((reviewrID, hist[::-1], pos_list[i], 1, len(hist[::-1]), rating_list[i]))

    random.shuffle(train_set)     #打乱数据集
    random.shuffle(test_set)
    return train_set, test_set

def gen_model_input(train_set, user_profile, seq_max_len):
    train_uid = np.array([line[0] for line in train_set])
    train_seq = [line[1] for line in train_set]
    train_iid = np.array([line[2] for line in train_set])
    train_label = np.array([line[3] for line in train_set])
    train_hist_len = np.array([line[4] for line in train_set])

    """
    pad_sequences数据预处理
    sequences：浮点数或整数构成的两层嵌套列表
    maxlen：None或整数，为序列的最大长度。大于此长度的序列将被截短，小于此长度的序列将在后部填0.
    dtype：返回的numpy array的数据类型
    padding：‘pre’或‘post’，确定当需要补0时，在序列的起始还是结尾补`
    truncating：‘pre’或‘post’，确定当需要截断序列时，从起始还是结尾截断
    value：浮点数，此值将在填充时代替默认的填充值0
    """
    train_seq_pad = pad_sequences(train_seq, maxlen=seq_max_len, padding='post', truncating='post', value=0)
    train_model_input = {"user_id": train_uid, "item_id": train_iid, "hist_item_id": train_seq_pad,
                         "hist_len": train_hist_len}
    for key in {"gender", "age", "city"}:
        train_model_input[key] = user_profile.loc[train_model_input['user_id']][key].values   #训练模型的关键字

	return train_model_input, train_label

```

这段代码主要用于生成训练集和测试集以及模型的输入。它看起来有点长，我来分别解释一下。

gen\_data\_set()函数接受一个数据集（data）和一个负采样（negsample）参数，返回一个训练集列表和一个测试集列表。该函数首先将数据集根据时间戳排序，然后从每一个用户的历史记录中选取正样本和负样本，并将它们保存到训练集和测试集中。

gen\_model\_input()函数接受一个训练集列表、用户画像信息和序列最大长度参数，返回训练模型的输入和标签。该函数将训练集列表拆分成train\_uid、train\_seq、train\_iid、train\_label和train\_hist\_len五部分。

- train\_uid和train\_iid为用户ID和物品ID。
- train\_seq为历史交互序列。
- train\_label为正负样本标签。
- train\_hist\_len为历史交互序列的长度。

此外，它对历史交互序列进行了填充处理（pad\_sequences），并且将用户画像信息加入到训练模型的关键字中。最终，该函数返回训练模型的输入和标签。

在gen\_data\_set()函数中，首先使用data.sort\_values(“timestamp”, inplace=True)函数将数据集按照时间戳排序，这是为了保证数据按照时间顺序排列，便于后续处理。接下来使用data\[‘item\_id’\].unique()函数获取数据集中所有不重复的物品ID。因为后续需要筛选出用户未曾购买过的物品，要先获取数据集中所有的物品ID以便后续处理。

接下来使用groupby()函数将用户ID（user\_id）相同的数据分组。对于每一组数据，将其分成正样本和负样本。其中正样本为用户已经购买过的物品，负样本为用户未购买过的其他物品。如果negsample参数大于0，则需要进行负采样。随机选取一些未曾购买过的物品作为负样本，并将它们保存到训练集列表中。最后，将正负样本数据以及其他信息（如历史交互序列、用户ID和历史交互序列的长度）保存到训练集列表和测试集列表中。

在gen\_model\_input()函数中，首先将训练集列表拆分成5个列表，分别保存用户ID、物品ID、历史交互序列、正负样本标签和历史交互序列长度。然后使用pad\_sequences()函数对历史交互序列进行填充处理，将其变成长度相同的序列。最后，将用户画像信息加入到训练模型的关键字中，返回训练模型的输入和标签。

## 搭建模型进行训练和预测

当数据处理完成后，接下来就可以来做YouTubeDNN的模型部分了，我们在recall目录下新建一个文件，名字叫YouTubeDNN，然后编写如下代码。

```plain
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from models.recall.preprocess import gen_data_set, gen_model_input
from deepctr.feature_column import SparseFeat, VarLenSparseFeat
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.models import Model
import tensorflow as tf
from deepmatch.models import *
from deepmatch.utils import recall_N
from deepmatch.utils import sampledsoftmaxloss
import numpy as np
from tqdm import tqdm


	class YoutubeModel(object):
	    def __init__(self, embedding_dim=32):
	        self.SEQ_LEN = 50
	        self.embedding_dim = embedding_dim
	        self.user_feature_columns = None
	        self.item_feature_columns = None

	    def training_set_construct(self):
	        # 加载数据
	        data = pd.read_csv('../../data/read_history.csv')
	        # 负采样个数
	        negsample = 0
	        # 特征编码
	        features = ["user_id", "item_id", "gender", "age", "city"]
	        features_max_idx = {}
	        for feature in features:
	            lbe = LabelEncoder()
	            data[feature] = lbe.fit_transform(data[feature]) + 1
	            features_max_idx[feature] = data[feature].max() + 1

	        # 抽取用户、物品特征
	        user_info = data[["user_id", "gender", "age", "city"]].drop_duplicates('user_id')  # 去重操作
	        item_info = data[["item_id"]].drop_duplicates('item_id')
	        user_info.set_index("user_id", inplace=True)

	        # 构建输入数据
	        train_set, test_set = gen_data_set(data, negsample)
	        # 转化为模型的输入
	        train_model_input, train_label = gen_model_input(train_set, user_info, self.SEQ_LEN)
	        test_model_input, test_label = gen_model_input(test_set, user_info, self.SEQ_LEN)
	        # 用户端特征输入
	        self.user_feature_columns = [SparseFeat('user_id', features_max_idx['user_id'], 16),
	                                     SparseFeat('gender', features_max_idx['gender'], 16),
	                                     SparseFeat('age', features_max_idx['age'], 16),
	                                     SparseFeat('city', features_max_idx['city'], 16),
	                                     VarLenSparseFeat(SparseFeat('hist_item_id', features_max_idx['item_id'],
	                                                                 self.embedding_dim, embedding_name='item_id'),
	                                                      self.SEQ_LEN, 'mean', 'hist_len')
	                                     ]
	        # 物品端的特征输入
	        self.item_feature_columns = [SparseFeat('item_id', features_max_idx['item_id'], self.embedding_dim)]

	        return train_model_input, train_label, test_model_input, test_label, train_set, test_set, user_info, item_info

	    def training_model(self, train_model_input, train_label):
	        K.set_learning_phase(True)
	        if tf.__version__ >= '2.0.0':
	            tf.compat.v1.disable_eager_execution()
	        # 定义模型
	        model = YouTubeDNN(self.user_feature_columns, self.item_feature_columns, num_sampled=100,
	                           user_dnn_hidden_units=(128, 64, self.embedding_dim))
	        model.compile(optimizer="adam", loss=sampledsoftmaxloss)
	        # 保存训练过程中的数据
	        model.fit(train_model_input, train_label, batch_size=512, epochs=20, verbose=1, validation_split=0.0,)
	        return model

	    def extract_embedding_layer(self, model, test_model_input, item_info):
	        all_item_model_input = {"item_id": item_info['item_id'].values, }
	        # 获取用户、item的embedding_layer
	        user_embedding_model = Model(inputs=model.user_input, outputs=model.user_embedding)
	        item_embedding_model = Model(inputs=model.item_input, outputs=model.item_embedding)

	        user_embs = user_embedding_model.predict(test_model_input, batch_size=2 ** 12)
	        item_embs = item_embedding_model.predict(all_item_model_input, batch_size=2 ** 12)
	        print(user_embs.shape)
	        print(item_embs.shape)
	        return user_embs, item_embs

	    def eval(self, user_embs, item_embs, test_model_input, item_info, test_set):
	        test_true_label = {line[0]: line[2] for line in test_set}
	        index = faiss.IndexFlagIP(self.embedding_dim)
	        index.add(item_embs)
	        D, I = index.search(np.ascontiguousarray(user_embs), 50)
	        s = []
	        hit = 0

	        # 统计预测结果
	        for i, uid in tqdm(enumerate(test_model_input['user_id'])):
	            try:
	                pred = [item_info['item_id'].value[x] for x in I[i]]
	                recall_score = recall_N(test_true_label[uid], pred, N=50)
	                s.append(recall_score)
	                if test_true_label[uid] in pred:
	                    hit += 1
	            except:
	                print(i)

	        # 计算召回率和命中率
	        recall = np.mean(s)
	        hit_rate = hit / len(test_model_input['user_id'])

	        return recall, hit_rate

	    def scheduler(self):
	        # 构建训练集、测试集
	        train_model_input, train_label, test_model_input, test_label, \
	        train_set, test_set, user_info, item_info = self.training_set_construct()
	        #
	        self.training_model(train_model_input, train_label)

	        # 获取用户、item的layer
	        # user_embs, item_embs = self.extract_embedding_layer(model, test_model_input, item_info)
	        # # 评估模型
	        # recall, hit_rate = self.eval(user_embs, item_embs, test_model_input, item_info, test_set)
	        # print(recall, hit_rate)


	if __name__ == '__main__':
	    model = YoutubeModel()
	    model.scheduler()

```

我来详细地解释下这段代码。首先根据导入的模块，可以看出这段代码主要使用了下面表格里的几个工具和库。

![](https://static001.geekbang.org/resource/image/86/22/868fa24203ced6e3e74208bf0c178c22.jpg?wh=2628x1934)

首先我们使用下面的代码加载数据。

```plain
	data = pd.read_csv('../../data/read_history.csv')

```

这行代码使用Pandas库来读取CSV格式的历史阅读记录数据文件，将其存储到data这个DataFrame对象中。

然后我们对数据进行特征编码。

```plain
features = ["user_id", "item_id", "gender", "age", "city"]
features_max_idx = {}
for feature in features:
    lbe = LabelEncoder()
    data[feature] = lbe.fit_transform(data[feature]) + 1
    features_max_idx[feature] = data[feature].max() + 1

```

这段代码使用sklearn.preprocessing.LabelEncoder对原始数据的几个特征进行编码，将连续或离散的特征转化为整数类型。这里编码的特征包括user\_id、item\_id、gender、age、city。将特征编码后，将最大索引值保存到features\_max\_idx字典中。

接下来，我们使用下面的代码来构建了数据集。

```plain
train_set, test_set = gen_data_set(data, negsample)

```

这行代码使用gen\_data\_set函数将原始数据划分为训练集和测试集，同时进行负采样操作。该函数的输入参数为原始数据和负采样个数。输出结果为经过负采样后的训练集和测试集。

然后我们就可以调用之前的gen\_model\_input函数将训练集和测试集转化为模型的输入格式，包括训练集/测试集的用户ID、历史物品ID序列、历史物品ID序列的长度和待预测物品ID。这些数据会作为训练模型的输入。

```plain
train_model_input, train_label = gen_model_input(train_set, user_info, self.SEQ_LEN)
test_model_input, test_label = gen_model_input(test_set, user_info, self.SEQ_LEN)

```

接着，我们使用deepctr库中的SparseFeat和VarLenSparseFeat函数，分别构建了用户和物品的特征输入。其中SparseFeat表示离散特征，VarLenSparseFeat表示变长特征。具体地，用户特征输入由4个离散特征和一个变长特征（历史物品ID序列）组成，物品特征输入只有一个离散特征（物品ID）。

```plain
# 用户端特征输入
self.user_feature_columns = [SparseFeat('user_id', features_max_idx['user_id'], 16),
                             SparseFeat('gender', features_max_idx['gender'], 16),
                             SparseFeat('age', features_max_idx['age'], 16),
                             SparseFeat('city', features_max_idx['city'], 16),
                             VarLenSparseFeat(SparseFeat('hist_item_id', features_max_idx['item_id'],
                                                         self.embedding_dim, embedding_name='item_id'),
                                              self.SEQ_LEN, 'mean', 'hist_len')
                             ]
# 物品端的特征输入
self.item_feature_columns = [SparseFeat('item_id', features_max_idx['item_id'], self.embedding_dim)]

```

然后我们使用deepmatch库构建了含有DNN的YouTube推荐模型。该模型的输入由上一步定义的用户和物品特征输入组成，其中num\_sampled表示分类器使用的采样点的数目。在模型构建和编译后，使用fit函数进行训练。

```plain
# 定义模型
model = YouTubeDNN(self.user_feature_columns, self.item_feature_columns, num_sampled=100,
                   user_dnn_hidden_units=(128, 64, self.embedding_dim))
model.compile(optimizer="adam", loss=sampledsoftmaxloss)
# 保存训练过程中的数据
model.fit(train_model_input, train_label, batch_size=512, epochs=20, verbose=1, validation_split=0.0,)

```

最后，利用训练好的模型提取用户和物品的Embedding Layer，以便后续计算召回率和命中率。具体地，使用Model函数将模型的输入和它的用户/物品Embedding层关联起来，然后调用predict函数计算得到预测结果。

```plain
user_embs = user_embedding_model.predict(test_model_input, batch_size=2 ** 12)
item_embs = item_embedding_model.predict(all_item_model_input, batch_size=2 ** 12)

```

实际上，到这里整个数据处理和训练部分的代码就已经结束了，接下来，就是要做召回率和命中率的计算。在这个部分，我们利用Faiss库计算用户和物品Embedding Layer之间的近邻关系，并根据预测的物品列表计算召回率和命中率。具体来说就是根据用户ID索引到对应的Embedding向量，然后在物品Embedding向量集合中搜索近邻，得到预测的物品列表。最后，根据预测的物品列表和真实的物品ID，计算召回率和命中率。

```plain
def eval(self, user_embs, item_embs, test_model_input, item_info, test_set):
   test_true_label = {line[0]: line[2] for line in test_set}
   index = faiss.IndexFlagIP(self.embedding_dim)
   index.add(item_embs)
   D, I = index.search(np.ascontiguousarray(user_embs), 50)
   s = []
   hit = 0

   # 统计预测结果
   for i, uid in tqdm(enumerate(test_model_input['user_id'])):
       try:
           pred = [item_info['item_id'].value[x] for x in I[i]]
           recall_score = recall_N(test_true_label[uid], pred, N=50)
           s.append(recall_score)
           if test_true_label[uid] in pred:
               hit += 1
       except:
           print(i)

   # 计算召回率和命中率
   recall = np.mean(s)
   hit_rate = hit / len(test_model_input['user_id'])

   return recall, hit_rate
 整个流程实际上到这里就结束了，那么最后，我们使用一个scheduler函数将它们串起来：
def scheduler(self):
   # 构建训练集、测试集
   train_model_input, train_label, test_model_input, test_label, \
   train_set, test_set, user_info, item_info = self.training_set_construct()
   #
   self.training_model(train_model_input, train_label)

   # 获取用户、item的layer
   # user_embs, item_embs = self.extract_embedding_layer(model, test_model_input, item_info)
   # # 评估模型
   # recall, hit_rate = self.eval(user_embs, item_embs, test_model_input, item_info, test_set)
   # print(recall, hit_rate)


```

这里有一点需要注意，Faiss库目前在Windows上无法使用，必须在Linux上才行。因此，在最后的Schedule阶段，我将这段代码进行了注释。

整个YouTubeDNN的召回层训练和预测到这里就结束了。

## 总结

到这里，今天的课程就讲完了，接下来我们来对今天的课程做一个简单的总结，学完本节课你应该知道下面三大要点。

1. 在YouTubeDNN中，数据处理会经过加载数据集、处理数据特征、特征转化为模型输入、模型的搭建和训练、模型评估这5个部分。
2. YouTubeDNN模型通过将用户历史行为序列嵌入到低维向量空间中，来学习用户和物品之间的关系。它的输入包括用户历史行为序列以及物品ID，输出包括用户和物品的嵌入向量以及它们之间的相似度得分。
3. 熟悉使用Python来搭建一整套YouTubeDNN模型代码。

## 课后题

本节课学完了，我来给你留两道课后题。

1. 实现本节课的代码。
2. 根据我们前面的知识，自动生成数据集。

欢迎你在留言区与我交流讨论，如果这节课对你有帮助，也欢迎你推荐给朋友一起学习。