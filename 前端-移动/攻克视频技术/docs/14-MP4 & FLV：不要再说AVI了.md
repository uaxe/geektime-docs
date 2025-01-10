你好，我是李江。

前面我们花了很长的时间学习了视频编码和视频传输弱网对抗的知识点。从今天开始我们来学习几个视频封装和播放的知识点。我们先来学习一下什么是音视频封装。之后我们再学习如何做音视频同步。

其实相比视频编码和传输，音视频封装应该是非常简单的知识点了。而且我们前面还学习过RTP打包，RTP打包音视频数据其实一定程度上也可以算是一种封装。我们今天再介绍两种常用的封装，一种是FLV，一种是MP4，相信你对这两种文件一点儿也不陌生。

音视频封装其实就是将一帧帧视频和音频数据按照对应封装的标准有组织地存放在一个文件里面，并且再存放一些额外的基础信息，比如说分辨率、采样率等信息。那到底怎么组织这些基础信息还有音视频数据呢？我们接下来先看看FLV是怎么做的。

## FLV

FLV是一种非常常见的音视频封装，尤其是在流媒体场景中经常用到。FLV封装也是比较简单的封装格式，它是由一个个Tag组成的。Tag又分为视频Tag、音频Tag和Script Tag，分别用来存放视频数据、音频数据和MetaData数据。

下图就是FLV的总体结构图：

![图片](https://static001.geekbang.org/resource/image/38/c0/38cc18a2a824e2001ae4d38818e691c0.jpeg?wh=1920x1080)

其总体格式图如下：

![](https://static001.geekbang.org/resource/image/d9/00/d9e526be063eb8382535caa585d9f600.jpeg?wh=1552x1190)

### FLV Header

其中，FLV Header占用9个字节。前3个字节是文件的标识，固定是FLV。之后的1个字节表示版本。在之后的1个字节中的第6位表示是否存在音频数据，第8位表示是否存在视频数据，其他位都为0。最后的4个字节表示从文件开头到FLV Body开始的长度，一般就是等于9。

### FLV Body

在FLV Header之后就是FLV Body了，这就是存放主要数据的地方，放置着一个个Tag。在每一个Tag前面都有一个4字节的Previous Tag Size，表示前一个Tag的大小，方便往回倒。再之后就是具体的Tag了。Tag又是由Tag Header和Tag Data组成，其中Tag Header占用11个字节，格式如上图。

**其中最重要的是时间戳，因为播放的速度还有音视频同步都需要依赖这个时间戳的值。** 时间戳占用3～4字节，如果3字节不够的话，则需要使用1字节的扩展时间戳作为时间戳的高8位。还需要注意的一个点就是，时间戳的单位是ms。RTP的时间戳单位是1/90000秒，MP4的时间戳是可以自定义的。这个时间戳的单位也是至关重要的，不要弄错了。

接下来就是Tag Data数据了。Tag Data有Script、音频和视频。首先来看一下Script Tag的Data。这个Tag存放的是MetaData数据，主要包括宽、高、时长、采样率等基础信息。

Script Data使用2个AMF包来存放信息。第一个AMF包是onMetaData包。第1个字节表示的是AMF包的类型，一般是字符串类型，值是0x02，之后是2字节的长度，一般长度总是10，值是0x000A。之后就是10字节长度字符串了，值是onMetaData。

第二个AMF包的第一个字节是数组类型，值是0x08，紧接着4个字节为数组元素的个数。后面即为各数组元素的封装，数组元素为元素名称和值组成的对。常见的数组元素如下表所示：

![图片](https://static001.geekbang.org/resource/image/da/30/da922577ddc53bcac52b1bcccd433130.jpeg?wh=1340x1172)

音频Tag Data的第一个字节表示音频的编码方式、采样率和位宽等信息，如下图所示。之后就是音频数据了。

![图片](https://static001.geekbang.org/resource/image/4a/5a/4a226cc369df7fd8ee7f469694e47f5a.jpeg?wh=1328x688)

视频Tag的第1个字节包含了这个Tag的视频帧类型和视频编码方式，格式如下图：

![图片](https://static001.geekbang.org/resource/image/1f/51/1fd4c7db11320f1f163b969f2d411451.jpeg?wh=1342x350)

对于H264数据，紧接着会有4字节的AVC Packet Type格式，如下图所示：

![图片](https://static001.geekbang.org/resource/image/a8/a1/a86a39594d3295f431763959d53487a1.jpeg?wh=1336x452)

**其中最重要的就是CTS。** 这个是什么意思呢？这是因为H264有B帧这种类型，涉及到显示时间戳PTS和解码时间戳DTS。前面Tag Header里的时间戳就是DTS，PTS等于DTS + CTS，这个需要注意一下。接下来就是存放具体的视频数据。

如果AVC包类型是0，则数据格式如下图所示：

![图片](https://static001.geekbang.org/resource/image/12/bb/12d630497d4f0e540a764e62dd7f34bb.jpeg?wh=1336x1246)

如果AVC包类型为1，则数据格式如下图所示：

![图片](https://static001.geekbang.org/resource/image/be/81/be79ca64a849568c1e19ce3399750e81.png?wh=1206x324)

这就是FLV封装。

## MP4

了解了FLV封装之后，我们再来看一下MP4封装。MP4封装相比FLV更常见，但是也更复杂一些。其实它们的基本的思想还是一样的，就是用一个规定的格式组织存放音视频数据和一些基础信息。跟FLV由一个个Tag组成有点类似，MP4由一个个box组成，每一个box存放了不同的数据，而且box里面还可以嵌套着box。

MP4最外层的box主要有三个，分别是File Type box（ftyp box）、Movie box（moov box）和Media Data box（mdat box）。其中最重要、最复杂的就是moov box了，它里面存放了音视频的基本信息和每一个音视频数据的具体位置。

还有一点需要说明的就是：在MP4文件中，视频的一帧和音频的一段编码数据称为一个sample。连续的几个sample称之为chunk，而视频的所有sample称为一个视频track，同样音频的所有sample也称为一个音频track。

因此一般MP4文件是由音频track和视频track组成，而track由sample组成，其中若干个sample组成一个chunk。

**好了，下面我们就来看看比较重要的box吧。** 因为，MP4的box特别多，我们不会一个个都介绍，我们只介绍一下比较重要的box。

每一个box都是由Box Header和Box Data组成。Box Header的结构如下图所示：

![图片](https://static001.geekbang.org/resource/image/e8/90/e888133ea73c584a711098869f6f6790.jpeg?wh=1198x572)

根据Box Header中的type我们将box分为不同类型的box，每一种不同的box对应的Box Data都是不一样。Box Data里面又可以嵌套box。MP4的总体box分布图如下图所示：

![图片](https://static001.geekbang.org/resource/image/7f/d1/7f22c603689c17b42098b32eyyf034d1.jpeg?wh=1920x1333)

首先，ftyp box放在MP4文件的开始，用来表示文件类型，该box的Box Data包含了4字节的主版本（major brand）、4字节的版本号（minor version）和若干个4字节数组组成的兼容版本（compatible\_brands）。

**mdat box是MP4的音视频数据存放的地方**。mdat box 基本由头部和数据两部分组成，box type是 “mdat” 的ASCII码值。对于H264来说，是一个个NALU，码流格式使用的是 [第05讲](https://time.geekbang.org/column/article/461658) 里面的MP4格式。这里的NLAU不再包含SPS和PPS，这些数据已经放到moov box里面了，此处NALU类型是图像数据或者SEI数据。

**另一个box就是最重要的moov box，用来存放Metadata信息。** 这个box可以放在ftyp的后面也可以放置在文件的最后面。moov box里面会一层层嵌套很多层box。总体嵌套逻辑就是movie里面是track，track里面是sample，多个sample又组成了一个个chunk。

moov box首先有一个mvhd box（movie header box）主要存放文件的基本信息，比如说MP4文件的创建时间、时间单位、总时长等信息。

moov box中的另外一个重要的box就是trak box，这个box音频和视频各有一个。具体是音频trak还是视频trak，会在trak box中的mdia box里面的hdlr box中表示出来。

trak box内部有一个tkhd box（track header box）主要是表示track的一些基本信息，比如说视频的宽高信息和音频的音量信息等。

trak box还有一个mdia box，它是媒体信息box。它包含了3个子box，一个是mdhd box，一个是刚才提到的hdlr box，一个是最重要的minf box，这个box里面包含了sample的很多信息，这些信息是找到并正确使用音频和视频数据的关键。

mdhd box里面最重要的一个值就是时间单位time scale，这个时间单位是sample的时间戳的单位，控制播放速度和音视频同步都需要使用到这个值。

hdlr box主要包含了track的类型信息，表明是音频还是视频track。

minf box里面包含了一个stbl box（sample table box），里面存放着可以计算得到每一个chunk的偏移地址、每一个sample在文件中的地址信息和大小、每一个sample的时间戳和每一个视频IDR帧的地址信息。下面我们来详细介绍一下这些box。

其中，stts box中放置的是每一个sample的时长，这个值是DTS。

![图片](https://static001.geekbang.org/resource/image/6a/75/6a94cf7fcee63b81bd1375f42a206275.jpeg?wh=1342x1250)

ctts box放置着CTS，也就是每一个sample的PTS和DTS的差值。

![图片](https://static001.geekbang.org/resource/image/58/8d/58b59fc37129abcb6e7398f98cb6ea8d.jpeg?wh=1348x1254)

stss box中放置的是哪些sample是关键帧。

![图片](https://static001.geekbang.org/resource/image/94/8a/94347b1d78b04a9995yyea1110yy338a.jpeg?wh=1332x1068)

stsc box中放置的是sample到chunk的映射表，也就是哪些sample属于哪个chunk。

![图片](https://static001.geekbang.org/resource/image/03/a5/034ec8ab5228e2c65240c7fdb2f190a5.jpeg?wh=1338x1446)

stco box或co64 box中放置着每个chunk在文件中的偏移地址。

![图片](https://static001.geekbang.org/resource/image/5c/ca/5ca7437ed49766cfc827fa75891680ca.jpeg?wh=1332x1104)

stsz box中放置着每一个sample的大小。

![图片](https://static001.geekbang.org/resource/image/aa/99/aa0b8bef4d0c23da67c1468e92682599.jpeg?wh=1336x1214)

好了，跟sample相关的box就是这些。

### 工程实践

接下来我们结合一个工程问题来实践一下。我们如何计算每一个sample在文件中的具体位置，判断它是不是关键帧，并计算它的具体时间。

计算sample的具体位置需要使用stco（或co64）、stsc和stsz。我们首先通过stsc将每一个sample属于哪一个chunk计算出来。这样每一个chunk的第一个sample就知道是哪个了。然后我们通过stco和co64就可以知道对应序号的chunk的第一个sample在文件中的地址了。我们再通过stsz查询每个sample的大小，从chunk的第一个sample的地址将中间的sample的大小一个个地加上去就可以得到每一个sample的地址了。

![图片](https://static001.geekbang.org/resource/image/aa/7c/aaac0910d536a50191854cae468b307c.jpeg?wh=1904x852)

而sample是不是关键帧，我们只需要通过stss对应每一个sample序号查询就可以得到。

![图片](https://static001.geekbang.org/resource/image/54/c5/54fa75cc33d0690c8c206f6bac6b82c5.jpeg?wh=1904x841)

计算sample的时间我们需要用到stts和ctts。我们先通过stts得到每一个sample的时长，第n个sample的结束时间就是第n-1个sample的结束时间加上第n个sample的时长。但是需要注意一下，这个是DTS，我们还需要通过ctts box得到每一个sample的PTS和DTS的差值。最后每一个sample的PTS就是等于DTS加上CTS。

![图片](https://static001.geekbang.org/resource/image/02/7b/02d684c8ea5e8405fb8f2ce341b90d7b.jpeg?wh=1913x896)

好了，以上就是MP4封装的主要内容。

## 总结

今天，我们主要介绍了一下两种音视频封装格式，分别是FLV和MP4。这两种封装格式是我们工作和生活中经常需要用到的。

- FLV在流媒体场景经常会用到，其实直播RTMP协议和HTTP-FLV协议里面也是用的FLV封装，所以还是很重要的。
- MP4封装就是平时视频文件最常用的封装了，它主要由一个个box组成，其中最重要的就是跟sample有关的box，你需要重点掌握。当然你也不需要背下来，了解主要思想即可，等真正用到的时候查询一下就可以了。

## 思考题

好了，今天的课程到这里就结束了。在课程的最后，我给你留一道思考题。请你想一想：为什么FLV相比MP4更适合流媒体？

你可以在留言区留下你的答案，或者你有任何问题都可以在留言区和我交流，我们下节课再见。