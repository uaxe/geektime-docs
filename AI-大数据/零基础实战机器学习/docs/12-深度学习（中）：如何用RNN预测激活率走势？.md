你好，我是黄佳。

欢迎来到零基础实战机器学习。在上一讲中，我们通过给鲜花图片分类，学习了CNN在图像识别方面的应用。这一讲呢，我们就来学习另外一种深度学习模型——循环神经网络RNN（Recurrent Neural Network）。那么进入正题之前，我先给你讲个段子，让你直观理解一下，循环神经网络和其它神经网络模型有啥不同。

假如我和你开车去商场，然后我说“嘿！你知道吗，昨天老王的夫人生二胎了！”你说：“是吗？这么大年纪，真不容易。对了，上次你说他的项目没上线，对吧，后来那个项目到底怎么样了呢？”我回答说：“嗨，那个项目啊，别提了，把他整惨了，三次上线都失败了，现在公司在考虑放弃老王负责的这个项目。嗯，到了，你等我一会儿，我去给老王买个\_\_\_\_\_（此处为填空，选项1：项目；选项2：玩具）慰问一下他。”

若是这个选择题给循环神经网络之外的其它神经网络做，我们得到的答案可能是“项目”，因为在输入的文本（特征）中，一直是在谈项目，可正确答案显然是“玩具”。也就是说，如果让神经网络实现类似于人脑的语义判别能力，有一个很重要的前提是，**必须从所有过去的句子中保留一些信息，以便能理解整个故事的上下文**。而循环神经网络中的记忆功能恰恰解决了这个“对前文的记忆”功能。
<div><strong>精选留言（5）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/15/66/8f/02be926d.jpg" width="30px"><span>在路上</span> 👍（5） 💬（3）<div>佳哥好，测试了下SimpleRNN和GRU算法，SimpleRNN算法的损失值会达到0.2，GRU算法的损失值只有0.04，所以GRU算法的预测结果非常漂亮，几乎和实际值重叠。像请教下老师，后面的课程会解释神经网络的中间层的参数含义吗？我会换不同的算法，为什么要又三层，每一次参数为什么这么设置，其实并不清楚。</div>2021-09-27</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/26/ef/0e/bbc35830.jpg" width="30px"><span>一杯绿绿</span> 👍（3） 💬（2）<div>老师好，有个疑问，不太理解本讲案例中的“根据前60天的历史激活数数值预测未来激活数”与前面第7讲提到的“根据前三个月的RFM值预测一年的总消费额”这两个案例的不同，看着感觉都是根据历史信息预测未来，那么第7讲的案例也可以用 RNN来解决吗？</div>2022-03-19</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/93/18/8cd87764.jpg" width="30px"><span>纯新手求轻喷</span> 👍（0） 💬（1）<div>请问老师，如果我的业务受到时间影响非常大（如电商促销节点、气候变化），能否考虑把时间数据加到模型里呢。

如果我有过去n年的历史数据，想预测本年度4季度的数据，如何能将同期的数据，在一个整年度上利用起来。</div>2021-10-09</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/93/18/8cd87764.jpg" width="30px"><span>纯新手求轻喷</span> 👍（0） 💬（3）<div>请问老师，如何对未知数据预测呢。上述案例中，预测输入的数据，是测试集数据呀</div>2021-10-08</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/12/93/18/8cd87764.jpg" width="30px"><span>纯新手求轻喷</span> 👍（0） 💬（1）<div>老师，请问下，最后预测的时候，预测的时候，输入的数据是x_test，x_test 里面是包含了已知的真实数据的，这是怎么理解的呢？</div>2021-10-08</li><br/>
</ul>