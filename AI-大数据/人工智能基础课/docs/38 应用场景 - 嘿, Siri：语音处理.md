Siri是由苹果公司开发的智能语音助手。2011年10月，Siri以系统内置应用的方式随iPhone 4s一起发布，并被逐步集成到苹果的全线产品之中。Siri支持自然语言的输入与输出，可以通过与用户的语言交互实现朗读短信、介绍餐厅、询问天气、设置闹钟等简单功能，它还能不断学习新的声音和语调，并提供对话式的应答。今天，我就结合苹果公司关于Siri的介绍简单谈谈人工智能中的语音处理。

Siri的语音处理包括**语音识别**和**语音合成**两部分。语音识别（speech recognition）的作用是听懂用户的话，语音合成（speech synthesis）的作用则是生成Siri自己的回答。目前在苹果公司公开的技术博客Apple Machine Learning Journal上，主要给出的是语音合成的技术方案，但这些方案对语音识别也有启发。

在很多游戏和软件中，语音提示都是由声优提前录制而成，但以Siri为代表的实时语音助手们必须采用语音合成技术。**业界主流的语音合成方法有两种：单元选择和参数合成**。

当具备足够数量的高品质录音时，单元选择方法能够合成出自然的高质量语音。相比之下，参数合成方法得到的结果虽然更加流利且容易识别，其整体质量却有所不及，因而适用于语料库较小的情景。

将两者结合起来就得到了**混合单元选择模式**：其基本思路仍然是单元选择的思路，在预测需要选择的单元时则采用参数方法，Siri正是采用了这种模式。

要实现高质量的语音合成，足够的录音语料是必备的基础。但这些语料不可能覆盖所有的表达，因而需要将其划分为音素和半音素等更微小的基本单元，再根据由输入语音转换成的文本将基本单元重组，合成全新的语音。

当然，这样的重组绝非易事：在自然语言中，每个音素的选择既依赖于相邻音素，也取决于整体语句的音韵。单元选择方法完成的正是基本单元重组的任务：既要与输入的文本对应，又要生成符合语句内容的音调与音韵，同时还不能出现明显的打喯儿与中断。

**Siri的语音合成系统包括文本分析、音韵生成、单元选择、波形串联四个模块，前两个环节对应前端的文本处理，后两个环节则对应后端的信号处理**。
<div><strong>精选留言（4）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/11/41/8d/f14a278d.jpg" width="30px"><span>风的轨迹</span> 👍（0） 💬（2）<div>1.包含两种语言单词混合的语音识别效果不好，越专业的词汇效果越不好
2. 合成语音读小说得效果不好，必须集中精力听才能听懂，其实还是多了一层人工翻译的过程</div>2018-06-08</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/c1/a7/5e66d331.jpg" width="30px"><span>林彦</span> 👍（3） 💬（0）<div>没怎么用过。如果有个语音助手能协助我听懂和说出别人听不出来的中国各地方言，我肯定会用 😊</div>2018-03-09</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/26/eb/d7/90391376.jpg" width="30px"><span>ifelse</span> 👍（1） 💬（0）<div>学习打卡</div>2023-05-18</li><br/><li><img src="http://thirdwx.qlogo.cn/mmopen/vi_32/g1icQRbcv1QvJ5U8Cqk0ZqMH5PcMTXcZ8TpS5utE4SUzHcnJA3FYGelHykpzTfDh55ehE8JO9Zg9VGSJW7Wxibxw/132" width="30px"><span>杨家荣</span> 👍（0） 💬（0）<div>极客时间
21天打卡行动 36&#47;21
&lt;&lt;人工智能基础课38&gt;&gt;嘿, Siri：语音处理
回答老师问题:
语音处理的最终目的不是简单地分析或者合成声音，而是为了更好地和人交互，从而以更简捷的方式解决问题。从交互的角度来看，你认为目前的语音助手还存在着哪些不足呢？
前后语意不能交互;如果加上长短期记忆网络或许会好些!
今日所学 :
1,语音处理包括语音识别和语音合成两部分;
2,业界主流的语音合成方法有两种：单元选择和参数合成;
3,Siri 的语音合成系统包括文本分析、音韵生成、单元选择、波形串联四个模块，前两个环节对应前端的文本处理，后两个环节则对应后端的信号处理;
4,对于每个目标半音素，维特比算法都可以搜索出一个最优单元序列来合成它，评价最优性的指标包括两条：目标成本和拼接成本。
5,Siri 的独特之处在于将深度学习应用在了混合单元选择模式中：用基于深度学习的一体化模型代替传统的隐马尔可夫模型指导最优单元序列的搜索，以自动并准确地预测数据库中单元的目标损失和拼接损失;
6,Siri 使用的技术是深度混合密度网络（Mixture Density Network），这是传统的深度神经网络和高斯混合模型（Gaussian Mixture Model）的组合。
7,语音识别能够将语音信号转换成对应的文本信息，其系统通常包含预处理、特征提取、声学模型，语言模型和字典解码等几个模块。
8,与隐马尔可夫模型相比，神经网络的优点在于不依赖对特征统计特性的任何假设，但其缺点则是对时间上的依赖关系的建模能力较差，因而缺乏处理连续识别任务的能力。
9,不同语言、不同带宽语音数据的神经网络训练可以在同样的框架下进行，其基础是神经网络中特征变换的泛化特性，这使得特征变换的方法不依赖于具体的语言。
重点:
1,语音处理可以分为语音识别和语音合成两类任务；
2,语音合成过程包括文本分析、音韵生成、单元选择、波形串联等步骤；
3,语音识别过程包括预处理、特征提取、声学模型，语言模型和字典解码等步骤；
4,深度学习和迁移学习等技术都已经被应用在语音处理之中。</div>2020-01-23</li><br/>
</ul>