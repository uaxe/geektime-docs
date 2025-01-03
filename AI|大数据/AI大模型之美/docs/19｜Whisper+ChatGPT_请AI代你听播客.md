你好，我是徐文浩。

今天，我们的课程开始进入一个新的主题了，那就是语音识别。过去几周我们介绍的ChatGPT虽然很强大，但是只能接受文本的输入。而在现实生活中，很多时候我们并不方便停下来打字。很多内容比如像播客也没有文字版，所以这个时候，我们就需要一个能够将语音内容转换成文本的能力。

作为目前AI界的领导者，OpenAI自然也不会放过这个需求。他们不仅发表了一个通用的语音识别模型 Whisper，还把对应的代码开源了。在今年的1月份，他们也在API里提供了对应的语音识别服务。那么今天，我们就一起来看看Whisper这个语音识别的模型可以怎么用。

## Whisper API 101

我自己经常会在差旅的过程中听播客。不过，筛选听什么播客的时候，有一个问题，就是光看标题和简介其实不是特别好判断里面的内容我是不是真的感兴趣。所以，在看到Whisper和ChatGPT这两个产品之后，我自然就想到了可以通过组合这两个API，让AI来代我听播客。 **我想通过Whisper把想要听的播客转录成文字稿，再通过ChatGPT做个小结，看看AI总结的小结内容是不是我想要听的。**

我前一阵刚听过一个 [关于 ChatGPT 的播客](https://www.listennotes.com/podcasts/onboard/ep-26-10pmK95wovN/)，我们不妨就从这个开始。我们可以通过 [listennotes](https://www.listennotes.com/) 这个网站来搜索播客，还能够下载到播客的源文件。而且，这个网站还有一个很有用的功能，就是可以直接切出播客中的一段内容，创建出一个切片（clip）。

我们先拿一个小的切片来试试Whisper的API，对应的切片的 [链接](https://www.listennotes.com/podcast-clips/ep-26-chatgpt%E4%B8%8E%E7%94%9F%E6%88%90%E5%BC%8Fai%E7%9A%84%E6%8A%80%E6%9C%AF%E6%BC%94%E8%BF%9B%E4%B8%8E%E5%95%86%E4%B8%9A%E6%9C%AA%E6%9D%A5%E5%AF%B9%E8%AF%9Dgoogle-P9dfstDKIV6/) 我也放在这里了。课程Github的data目录里也有已经下载好的MP3文件。

OpenAI提供的Whisper的API非常简单，你只要调用一下transcribe函数，就能将音频文件转录成文字。

```python
import openai, os

openai.api_key = os.getenv("OPENAI_API_KEY")

audio_file= open("./data/podcast_clip.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript['text'])

```

输出结果：

```python
欢迎来到 Onboard 真实的一线经验 走新的投资思考 我是 Monica 我是高宁 我们一起聊聊软件如何改变世界 大家好 欢迎来到 Onboard 我是 Monica 自从OpenAI发布的ChatGBT 掀起了席卷世界的AI热潮 不到三个月就积累了 超过一亿的越货用户 超过1300万的日货用户 真的是展现了AI让人惊讶的 也让很多人直呼 这就是下一个互联网的未来 有不少观众都说 希望我们再做一期AI的讨论 于是这次硬核讨论就来了 这次我们请来了 Google Brain的研究员雪芝 她是Google大语言模型PALM Pathway Language Model的作者之一 要知道这个模型的参数量 是GPT-3的三倍还多 另外还有两位AI产品大牛 一位来自著名的StableDM 背后的商业公司Stability AI 另一位来自某硅谷科技大厂 也曾在吴恩达教授的Landing AI中 担任产品负责人 此外 莫妮凯还邀请到一位 一直关注AI的投资人朋友Bill 当做我的特邀共同主持嘉宾 我们主要讨论几个话题 一方面从研究的视角 最前沿的研究者在关注什么 现在技术的天花板 和未来大的变量可能会在哪里 第二个问题是 未来大的变量可能会在哪里 从产品和商业的角度 什么是一个好的AI产品 整个生态可能随着技术 有怎样的演变 更重要的 我们又能从上一波 AI的创业热潮中学到什么 最后 莫妮凯和Bill还会从投资人的视角 做一个回顾 总结和畅想 这里还有一个小的update 在本集发布的时候 Google也对爆发式增长的 Chad GPT做出了回应 正在测试一个基于Lambda 模型的聊天机器人 ApprenticeBot 正式发布后会有怎样的惊喜 我们都拭目以待 AI无疑是未来几年 最令人兴奋的变量之一 莫妮凯也希望未来能邀请到更多 一线从业者 从不同角度讨论这个话题 不论是想要做创业 研究 产品 还是投资的同学 希望这些对话 对于大家了解这些技术演进 商业的可能 甚至未来对于我们每个人 每个社会意味着什么 都能引发一些思考 提供一些启发 这次的讨论有些技术硬核 需要各位对生成式AI 大模型都有一些基础了解 讨论中涉及到的论文和重要概念 也会总结在本集的简介中 供大家复习参考 几位嘉宾在北美工作生活多年 夹杂英文在所难免 也请大家体谅了 欢迎来到未来 希望大家enjoy

```

从转录的结果来看，有一个好消息和一个坏消息。好消息是，语音识别的转录效果非常好。我们看到尽管播客里面混杂着中英文，但是Whisper还是很好地识别出来了。坏消息是，转录出来的内容只有空格的分隔符，没有标点符号。

不过，这个问题也并不难解决。我们只要在前面的代码里面，增加一个Prompt参数就好了。

```python
audio_file= open("./data/podcast_clip.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                     prompt="这是一段中文播客内容。")
print(transcript['text'])

```

输出结果：

```python
欢迎来到 Onboard,真实的一线经验,走新的投资思考。 我是 Monica。 我是高宁。我们一起聊聊软件如何改变世界。 大家好,欢迎来到 Onboard,我是 Monica。 自从 OpenAI 发布的 ChatGBT 掀起了席卷世界的 AI 热潮, 不到三个月就积累了超过一亿的越活用户,超过一千三百万的日活用户。 真的是展现了 AI 让人惊叹的能力, 也让很多人直呼这就是下一个互联网的未来。 有不少观众都说希望我们再做一期 AI 的讨论, 于是这次硬核讨论就来了。 这次我们请来了 Google Brain 的研究员雪芝, 她是 Google 大语言模型 PAMP,Pathway Language Model 的作者之一。 要知道,这个模型的参数量是 GPT-3 的三倍还多。 另外还有两位 AI 产品大牛,一位来自著名的 Stable Diffusion 背后的商业公司 Stability AI, 另一位来自某硅谷科技大厂,也曾在吴恩达教授的 Landing AI 中担任产品负责人。 此外,Monica 还邀请到一位一直关注 AI 的投资人朋友 Bill 当作我的特邀共同主持嘉宾。 我们主要讨论几个话题,一方面从研究的视角,最前沿的研究者在关注什么? 现在技术的天花板和未来大的变量可能会在哪里? 从产品和商业的角度,什么是一个好的 AI 产品? 整个生态可能随着技术有怎样的演变? 更重要的,我们又能从上一波 AI 的创业热潮中学到什么? 最后,Monica 和 Bill 还会从投资人的视角做一个回顾、总结和畅想。 这里还有一个小的 update,在本集发布的时候, Google 也对爆发式增长的ChatGPT 做出了回应, 正在测试一个基于 Lambda 模型的聊天机器人 ApprenticeBot。 正式发布后会有怎样的惊喜?我们都拭目以待。 AI 无疑是未来几年最令人兴奋的变量之一, Monica 也希望未来能邀请到更多一线从业者从不同角度讨论这个话题。 不论是想要做创业、研究、产品还是投资的同学, 希望这些对话对于大家了解这些技术演进、商业的可能, 甚至未来对于我们每个人、每个社会意味着什么, 都能引发一些思考,提供一些启发。 这次的讨论有些技术硬核,需要各位对生成式 AI 大模型都有一些基础了解。 讨论中涉及到的论文和重要概念,也会总结在本集的简介中,供大家复习参考。 几位嘉宾在北美工作生活多年,夹杂英文在所难免,也请大家体谅了。 欢迎来到未来,大家 enjoy!

```

我们在transcribe函数被调用的时候，传入了一个Prompt参数。里面是一句引导Whisper模型的提示语。在这里，我们的Prompt里用了一句中文介绍，并且带上了标点符号。你就会发现，transcribe函数转录出来的内容也就带上了正确的标点符号。

不过，转录出来的内容还有一点小小的瑕疵。那就是中英文混排的内容里面，英文前后会多出一些空格。那我们就再修改一下Prompt，在提示语里面也使用中英文混排并且不留空格。

```python
audio_file= open("./data/podcast_clip.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                     prompt="这是一段Onboard播客的内容。")
print(transcript['text'])

```

输出结果：

```python
欢迎来到Onboard,真实的一线经验,走新的投资思考。 我是Monica,我是高宁,我们一起聊聊软件如何改变世界。 大家好,欢迎来到Onboard,我是Monica。 自从OpenAI发布的ChatGBT掀起了席卷世界的AI热潮, 不到三个月就积累了超过一亿的越活用户,超过1300万的日活用户。 真的是展现了AI让人惊叹的能力,也让很多人直呼这就是下一个互联网的未来。 有不少观众都说希望我们再做一期AI的讨论,于是这次硬核讨论就来了。 这次我们请来了Google Brain的研究员雪芝, 她是Google大语言模型POM,Pathway Language Model的作者之一。 要知道这个模型的参数量是GPT-3的三倍还多。 另外还有两位AI产品大牛,一位来自著名的Stable Diffusion背后的商业公司Stability AI, 另一位来自某硅谷科技大厂,也曾在吴恩达教授的Landing AI中担任产品负责人。 此外,Monica还邀请到一位一直关注AI的投资人朋友Bill,当做我的特邀共同主持嘉宾。 我们主要讨论几个话题,一方面从研究的视角,最前沿的研究者在关注什么? 现在的技术的天花板和未来大的变量可能会在哪里? 从产品和商业的角度,什么是一个好的AI产品? 整个生态可能随着技术有怎样的演变? 更重要的,我们又能从上一波AI的创业热潮中学到什么? 最后,Monica和Bill还会从投资人的视角做一个回顾、总结和畅想。 这里还有一个小的update,在本集发布的时候, Google也对爆发式增长的ChatGPT做出了回应, 正在测试一个基于Lambda模型的聊天机器人ApprenticeBot。 正式发布后会有怎样的惊喜?我们都拭目以待。 AI无疑是未来几年最令人兴奋的变量之一, Monica也希望未来能邀请到更多一线从业者从不同角度讨论这个话题。 不论是想要做创业、研究、产品还是投资的同学, 希望这些对话对于大家了解这些技术演进、商业的可能, 甚至未来对于我们每个人、每个社会意味着什么, 都能引发一些思考,提供一些启发。 这次的讨论有些技术硬核,需要各位对生成式AI、大模型都有一些基础了解。 讨论中涉及到的论文和重要概念,也会总结在本集的简介中,供大家复习参考。 几位嘉宾在北美工作生活多年,夹杂英文在所难免,也请大家体谅了。 欢迎来到未来,大家enjoy!

```

可以看到，输出结果的英文前后也就没有空格了。 **能够在音频内容的转录之前提供一段Prompt，来引导模型更好地做语音识别，是Whisper模型的一大亮点。** 如果你觉得音频里面会有很多专有名词，模型容易识别错，你就可以在Prompt里加上对应的专有名词。比如，在上面的内容转录里面，模型就把ChatGPT也听错了，变成了ChatGBT。Google的PALM模型也给听错了，听成了POM。对应的全称Pathways Language Model也少了一个s。而针对这些错漏，我们只要再修改一下Prompt，它就能够转录正确了。

```python
audio_file= open("./data/podcast_clip.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                     prompt="这是一段Onboard播客，里面会聊到ChatGPT以及PALM这个大语言模型。这个模型也叫做Pathways Language Model。")
print(transcript['text'])

```

输出结果：

```python
欢迎来到Onboard,真实的一线经验,走新的投资思考。我是Monica。 我是高宁。我们一起聊聊软件如何改变世界。 大家好,欢迎来到Onboard,我是Monica。 自从OpenAI发布的ChatGPT掀起了席卷世界的AI热潮,不到三个月就积累了超过一亿的越活用户,超过1300万的日活用户。 真的是展现了AI让人惊叹的能力,也让很多人直呼这就是下一个互联网的未来。 有不少观众都说希望我们再做一期AI的讨论,于是这次硬核讨论就来了。 这次我们请来了Google Brain的研究员雪芝,她是Google大语言模型PALM Pathways Language Model的作者之一。 要知道,这个模型的参数量是GPT-3的三倍还多。 另外还有两位AI产品大牛,一位来自著名的Stable Diffusion背后的商业公司Stability AI, 另一位来自某硅谷科技大厂,也曾在吴恩达教授的Landing AI中担任产品负责人。 此外,Monica还邀请到一位一直关注AI的投资人朋友Bill当作我的特邀共同主持嘉宾。 我们主要讨论几个话题,一方面从研究的视角,最前沿的研究者在关注什么? 现在的技术的天花板和未来大的变量可能会在哪里? 从产品和商业的角度,什么是一个好的AI产品? 整个生态可能随着技术有怎样的演变? 更重要的,我们又能从上一波AI的创业热潮中学到什么? 最后,Monica和Bill还会从投资人的视角做一个回顾、总结和畅想。 这里还有一个小的update,在本集发布的时候,Google也对爆发式增长的Chat GPT做出了回应。 正在测试一个基于Lambda模型的聊天机器人ApprenticeBot。 证实发布后会有怎样的惊喜,我们都拭目以待。 AI无疑是未来几年最令人兴奋的变量之一。 Monica也希望未来能邀请到更多一线从业者从不同角度讨论这个话题。 不论是想要做创业、研究、产品还是投资的同学, 希望这些对话对于大家了解这些技术演进、商业的可能,甚至未来对于我们每个人、每个社会意味着什么都能引发一些思考,提供一些启发。 这次的讨论有些技术硬核,需要各位对生成式AI大模型都有一些基础了解。 讨论中涉及到的论文和重要概念也会总结在本集的简介中,供大家复习参考。 几位嘉宾在北美工作生活多年,夹杂英文在所难免,也请大家体谅了。 欢迎来到未来,大家enjoy!

```

出现这个现象的原因，主要和Whisper的模型原理相关，它也是一个和GPT类似的模型，会用前面转录出来的文本去预测下一帧音频的内容。通过在最前面加上文本Prompt，就会影响后面识别出来的内容的概率，也就是能够起到给专有名词“纠错”的作用。

除了模型名称、音频文件和Prompt之外，transcribe接口还支持这样三个参数。

1. response\_format，也就是返回的文件格式，我们这里是默认值，也就是JSON。实际你还可以选择TEXT这样的纯文本，或者SRT和VTT这样的音频字幕格式。这两个格式里面，除了文本内容，还会有对应的时间信息，方便你给视频和音频做字幕。你可以直接试着运行一下看看效果。
2. temperature，这个和我们之前在ChatGPT类型模型里的参数含义类似，就是采样下一帧的时候，如何调整概率分布。这里的参数范围是0-1之间。
3. language，就是音频的语言。提前给模型指定音频的语言，有助于提升模型识别的准确率和速度。

这些参数你都可以自己试着改一下，看看效果。

```python
audio_file= open("./data/podcast_clip.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file, response_format="srt",
                                     prompt="这是一段Onboard播客，里面会聊到PALM这个大语言模型。这个模型也叫做Pathways Language Model。")
print(transcript)

```

输出结果：

```python
1
00:00:01,000 --> 00:00:07,000
欢迎来到Onboard,真实的一线经验,走新的投资思考。我是Monica。
2
00:00:07,000 --> 00:00:11,000
我是高宁。我们一起聊聊软件如何改变世界。
3
00:00:15,000 --> 00:00:17,000
大家好,欢迎来到Onboard,我是Monica。
4
00:00:17,000 --> 00:00:28,000
自从OpenAI发布的ChatGBT掀起了席卷世界的AI热潮,不到三个月就积累了超过一亿的越活用户,超过1300万的日活用户。
5
00:00:28,000 --> 00:00:34,000
真的是展现了AI让人惊叹的能力,也让很多人直呼这就是下一个互联网的未来。
6
00:00:34,000 --> 00:00:41,000
有不少观众都说希望我们再做一期AI的讨论,于是这次硬核讨论就来了。
7
...
欢迎来到未来,大家enjoy!

```

## 转录的时候顺便翻译一下

除了基本的音频转录功能，Whisper的API还额外提供了一个叫做translation的接口。这个接口可以在转录音频的时候直接把语音翻译成英文，我们不妨来试一下。

```python
audio_file= open("./data/podcast_clip.mp3", "rb")
translated_prompt="""This is a podcast discussing ChatGPT and PaLM model.
The full name of PaLM is Pathways Language Model."""
transcript = openai.Audio.translate("whisper-1", audio_file,
                                    prompt=translated_prompt)
print(transcript['text'])

```

输出结果：

```python
Welcome to Onboard. Real first-line experience. New investment thinking. I am Monica. I am Gao Ning. Let's talk about how software can change the world. Hello everyone, welcome to Onboard. I am Monica. Since the release of ChatGPT by OpenAI, the world's AI has been in a frenzy. In less than three months, it has accumulated more than 100 million active users, and more than 13 million active users. It really shows the amazing ability of AI. It also makes many people say that this is the future of the next Internet. Many viewers said that they wanted us to do another AI discussion. So this discussion came. This time we invited a researcher from Google Brain, Xue Zhi. He is one of the authors of Google's large-scale model PaLM, Pathways Language Model. You should know that the number of parameters of this model is three times more than ChatGPT-3. In addition, there are two AI product big cows. One is from the famous company behind Stable Diffusion, Stability AI. The other is from a Silicon Valley technology factory. He was also the product manager in Professor Wu Wenda's Landing AI. In addition, Monica also invited a friend of AI who has been paying attention to AI, Bill, as my special guest host. We mainly discuss several topics. On the one hand, from the perspective of research, what are the most cutting-edge researchers paying attention to? Where are the cutting-edge technologies and the large variables of the future? From the perspective of products and business, what is a good AI product? What kind of evolution may the whole state follow? More importantly, what can we learn from the previous wave of AI entrepreneurship? Finally, Monica and Bill will also make a review, summary and reflection from the perspective of investors. Here is a small update. When this issue was released, Google also responded to the explosive growth of ChatGPT. We are testing an Apprentice Bot based on Lambda model. What kind of surprises will be released? We are looking forward to it. AI is undoubtedly one of the most exciting variables in the coming years. Monica also hopes to invite more first-line entrepreneurs to discuss this topic from different angles. Whether you want to do entrepreneurship, research, product or investment, I hope these conversations will help you understand the possibilities of these technical horizons and business. Even in the future, it can cause some thoughts and inspire us to think about what it means to each person and each society. This discussion is a bit technical, and requires you to have some basic understanding of the biometric AI model. The papers and important concepts involved in the discussion will also be summarized in this episode's summary, which is for your reference. You have worked in North America for many years, and you may have some English mistakes. Please understand. Welcome to the future. Enjoy. Let me give you a brief introduction. Some of your past experiences. A fun fact. Using an AI to represent the world is now palped.

```

这个接口只能把内容翻译成英文，不能变成其他语言。所以对应的，Prompt也必须换成英文。只能翻译成英文对我们来说稍微有些可惜了。如果能够指定翻译的语言，很多英文播客，我们就可以直接转录成中文来读了。现在我们要做到这一点，就不得不再花一份钱，让ChatGPT来帮我们翻译。

## 通过分割音频来处理大文件

刚才我们只是尝试转录了一个3分钟的音频片段，那接下来我们就来转录一下整个音频。不过，我们没法把整个150分钟的播客一次性转录出来，因为OpenAI限制Whisper一次只能转录25MB大小的文件。所以我们要先把大的播客文件分割成一个个小的片段，转录完之后再把它们拼起来。我们可以选用OpenAI在官方文档里面提供的 [PyDub 的库](https://platform.openai.com/docs/guides/speech-to-text/longer-inputs) 来分割文件。

不过，在分割之前，我们先要通过FFmpeg把从listennotes下载的MP4文件转换成MP3格式。你不了解FFmpeg或者没有安装也没有关系，对应的命令我是让ChatGPT写的。转换后的文件我也放到了 [课程 Github 库](https://github.com/xuwenhao/geektime-ai-course) 里的网盘地址了。

```python
ffmpeg -i ./data/podcast_long.mp4 -vn -c:a libmp3lame -q:a 4 ./data/podcast_long.mp3

```

分割MP3文件的代码也很简单，我们按照15分钟一个片段的方式，把音频切分一下就好了。通过PyDub的AudioSegment包，我们可以把整个长的MP3文件加载到内存里面来变成一个数组。里面每1毫秒的音频数据就是数组里的一个元素，我们可以很容易地将数组按照时间切分成每15分钟一个片段的新的MP3文件。

先确保我们安装了PyDub包。

```python
%pip install -U pydub

```

代码：

```python
from pydub import AudioSegment

podcast = AudioSegment.from_mp3("./data/podcast_long.mp3")

# PyDub handles time in milliseconds
ten_minutes = 15 * 60 * 1000

total_length = len(podcast)

start = 0
index = 0
while start < total_length:
    end = start + ten_minutes
    if end < total_length:
        chunk = podcast[start:end]
    else:
        chunk = podcast[start:]
    with open(f"./data/podcast_clip_{index}.mp3", "wb") as f:
        chunk.export(f, format="mp3")
    start = end
    index += 1

```

在切分完成之后，我们就一个个地来转录对应的音频文件，对应的代码就在下面。

```python
prompt = "这是一段Onboard播客，里面会聊到ChatGPT以及PALM这个大语言模型。这个模型也叫做Pathways Language Model。"
for i in range(index):
    clip = f"./data/podcast_clip_{i}.mp3"
    audio_file= open(clip, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                     prompt=prompt)
    # mkdir ./data/transcripts if not exists
    if not os.path.exists("./data/transcripts"):
        os.makedirs("./data/transcripts")
    # write to file
    with open(f"./data/transcripts/podcast_clip_{i}.txt", "w") as f:
        f.write(transcript['text'])
    # get last sentence of the transcript
    sentences = transcript['text'].split("。")
    prompt = sentences[-1]

```

在这里，我们对每次进行转录的Prompt做了一个小小的特殊处理。我们把前一个片段转录结果的最后一句话，变成了下一个转录片段的提示语。这样，我们可以让后面的片段在进行语音识别的时候，知道前面最后说了什么。这样做，可以减少错别字的出现。

## 通过开源模型直接在本地转录

通过OpenAI的Whisper API来转录音频是有成本的，目前的定价是 0.006 美元/分钟。比如我们上面的150分钟的音频文件，只需要不到1美元，其实已经很便宜了。不过，如果你不想把对应的数据发送给OpenAI，避免任何数据泄露的风险，你还有另外一个选择，那就是直接使用OpenAI开源出来的模型就好了。

不过使用开源模型你还是需要一块GPU，如果没有的话，你仍然可以使用免费的Colab的Notebook环境。

先安装openai-whisper的相关的依赖包。

```python
%pip install openai-whisper
%pip install setuptools-rust

```

代码本身很简单，我们只是把原先调用OpenAI的API的地方，换成了加载Whisper的模型，然后在transcribe的参数上，有一些小小的差异。其他部分的代码和前面我们调用OpenAI的Whisper API的代码基本上是一致的。

```python
import whisper

model = whisper.load_model("large")
index = 11 # number of fi

def transcript(clip, prompt, output):
    result = model.transcribe(clip, initial_prompt=prompt)
    with open(output, "w") as f:
        f.write(result['text'])
    print("Transcripted: ", clip)

original_prompt = "这是一段Onboard播客，里面会聊到ChatGPT以及PALM这个大语言模型。这个模型也叫做Pathways Language Model。\n\n"
prompt = original_prompt
for i in range(index):
    clip = f"./drive/MyDrive/colab_data/podcast/podcast_clip_{i}.mp3"
    output = f"./drive/MyDrive/colab_data/podcast/transcripts/local_podcast_clip_{i}.txt"
    transcript(clip, prompt, output)
    # get last sentence of the transcript
    with open(output, "r") as f:
        transcript = f.read()
    sentences = transcript.split("。")
    prompt = original_prompt + sentences[-1]

```

有一个点你可以注意一下，Whisper的模型和我们之前看过的其他开源模型一样，有好几种不同尺寸。你可以通过 load\_model 里面的参数来决定加载什么模型。这里我们选用的是最大的 large 模型，它大约需要10GB的显存。因为Colab提供的GPU是英伟达的T4，有16G显存，所以是完全够用的。

如果你是使用自己电脑上的显卡，显存没有那么大，你可以选用小一些的模型，比如small或者base。如果你要转录的内容都是英语的，还可以直接使用small.en这样仅限于英语的模型。这种小的或者限制语言的模型，速度还更快。不过，如果是像我们这样转录中文为主，混杂了英文的内容，那么尽可能选取大一些的模型，转录的准确率才会比较高。

![](https://static001.geekbang.org/resource/image/7a/3d/7a36faf9bb3f023714dea7e24a86653d.png?wh=1928x1076)

Whisper项目： [https://github.com/openai/whisper](https://github.com/openai/whisper)

## 结合ChatGPT做内容小结

无论是使用API还是通过本地的GPU进行文本转录，我们都会获得转录之后的文本。要给这些文本做个小结，其实我们在 [第 10 讲](https://time.geekbang.org/column/article/645305) 讲解llama-index的时候就给过示例了。我们把那个代码稍微改写一下，就能得到对应播客的小结。

```python
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import SpacyTextSplitter
from llama_index import GPTListIndex, LLMPredictor, ServiceContext, SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser

# define LLM
llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=1024))

text_splitter = SpacyTextSplitter(pipeline="zh_core_web_sm", chunk_size = 2048)
parser = SimpleNodeParser(text_splitter=text_splitter)
documents = SimpleDirectoryReader('./data/transcripts').load_data()
nodes = parser.get_nodes_from_documents(documents)

service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

list_index = GPTListIndex(nodes=nodes, service_context=service_context)
response = list_index.query("请你用中文总结一下我们的播客内容:", response_mode="tree_summarize")
print(response)

```

输出结果：

```python
这个播客讨论了人工智能和深度学习领域的高级技术和最新发展，包括稳定性人工智能、语言模型的预训练方法、图像生成模型的训练和优化，以及各种机器学习模型的比较和应用场景。同时，我们探讨了开源社区的作用和趋势，以及开源商业化的优缺点及如何应对。我们还讨论了人工智能在各个领域的应用和未来发展趋势，并强调了找到实际应用场景和解决实际问题的重要性。最后，我们提醒说，未来值得期待的AI应用将是能够真正跟人交互的产品，对于创业公司来说，需要从用户实际的痛点出发去考虑如何更好地应用AI技术。

```

基于这里的代码，你完全可以开发一个自动抓取并小结你订阅的播客内容的小应用。一般的播客也就是40-50分钟一期，转录并小结一期的成本也就在5块人民币上下。

## 小结

好了，这一讲到这里也就结束了。

OpenAI的Whisper模型，使用起来非常简单方便。无论是通过API还是使用开源的模型，只要一行代码调用一个transcribe函数，就能把一个音频文件转录成对应的文本。而且即使对于多语言混杂的内容，它也能转录得很好。而通过传入一个Prompt，它不仅能够在整个文本里，加上合适的标点符号，还能够根据Prompt里面的专有名词，减少转录中这些内容的错漏。虽然OpenAI的API接口限制了单个转录文件的大小，但是我们可以很方便地通过PyDub这样的Python包，把音频文件切分成多个小的片段来解决问题。

对于转录后的结果，我们可以很容易地使用之前学习过的ChatGPT和llama-index来进行相应的文本小结。通过组合Whisper和ChatGPT，我们就可以快速地让机器自动帮助我们将播客、Youtube访谈，变成一段文本小结，能够让我们快速浏览并判定是否有必要深入去听一下原始的内容。

## 思考题

我们在将长音频分片进行转录的过程里，是完全按照精确的时间去切割音频文件的。但是实际上音频的断句其实并不在那一毫秒。所以转录的时候，效果也不一定好，特别是在录音的开头和结尾部分，很有可能不是一个完整的句子，也容易出现一些错漏的情况。你能想想有什么好办法可以解决这个问题吗？我们是否可以利用SRT或VTT文件里面文本对应的时间标注信息？

欢迎你把你思考的结果分享到留言区，也欢迎你把这一讲分享给需要的朋友，我们下一讲再见！

## 推荐阅读

李沐老师在他的论文精读系列视频里面，有专门讲解过 [OpenAI Whisper 的相关论文](https://www.bilibili.com/video/BV1VG4y1t74x/)。他还专门基于Whisper的开源代码做了一个用来剪辑视频的小工具 [AutoCut](https://www.bilibili.com/video/BV1Pe4y1t7de/?spm_id_from=333.788.recommend_more_video.2&vd_source=dd7dfb298255b22a34220853aab4f816)。你有兴趣的话，可以去看一看。