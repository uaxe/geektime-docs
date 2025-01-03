你好，我是刘歧。

我们日常看电视剧，录视频时，最常见的就是MP4格式了。你有没有想过，MP4格式为什么使用得这么广泛呢？

因为MP4标准非常灵活，可扩展性比较好，有很多常见的格式是基于MP4做了一些扩展，然后被应用到比较广的范围，比如CMAF、DASH、HLS。而且MP4的参考标准是一个开放的标准，我们通常以编号为ISO-14496-12来查找标准文档。因为MP4的使用范围比较广，我们在 [第3节课](https://time.geekbang.org/column/article/544986) 的时候，也着重讲了MP4封装容器格式，你可以回顾一下。

![图片](https://static001.geekbang.org/resource/image/68/6b/689b8f155c2ed9yy6dbb007fa474586b.png?wh=1920x1083)

基于MP4的重要地位，我这节课来给你讲一讲，如何用FFmpeg、GPAC等工具生成与解析MP4。

尽管FFmpeg的目标是自己不去创造标准，但是难免会有一些工具或者用户会根据自己的臆测做一些定制或者修改，导致与我们公认的标准出现一些偏差。为了让MP4的标准性更好地得到验证，我们通常会选择使用多种工具，所以这节课除了给你介绍FFmpeg对MP4的mux与demux（封装与解封装）之外，我还会介绍一些其他的MP4相关的工具，例如MP4Box、Shaka- Packager。

在我们使用FFmpeg做音视频处理的时候，经常会使用FFmpeg生成MP4文件，或者使用FFmpeg输入MP4文件然后转换成其他格式。这里我们就先来了解一下FFmpeg对MP4都有哪些能力支持。这就需要用到 [上节课](https://time.geekbang.org/column/article/548420) 的知识了，你可以停下来先想一下我们应该怎么在FFmpeg中查找自己想要的帮助信息。

### 用FFmpeg生成MP4文件

首先，查看MP4的muxer对应的参数，输入ffmpeg -h muxer=mp4，看一下输出的内容。

```plain
Muxer mp4 [MP4 (MPEG-4 Part 14)]:
    Common extensions: mp4.
    Mime type: video/mp4.
    Default video codec: h264.
    Default audio codec: aac.
mov/mp4/tgp/psp/tg2/ipod/ismv/f4v muxer AVOptions:
  -movflags          <flags>      E.......... MOV muxer flags (default 0)
     rtphint                      E.......... Add RTP hint tracks
     empty_moov                   E.......... Make the initial moov atom empty
     frag_keyframe                E.......... Fragment at video keyframes
     frag_every_frame              E.......... Fragment at every frame
     separate_moof                E.......... Write separate moof/mdat atoms for each track
     frag_custom                  E.......... Flush fragments on caller requests
     isml                         E.......... Create a live smooth streaming feed (for pushing to a publishing point)
     faststart                    E.......... Run a second pass to put the index (moov atom) at the beginning of the file
     omit_tfhd_offset              E.......... Omit the base data offset in tfhd atoms
     disable_chpl                 E.......... Disable Nero chapter atom
     default_base_moof              E.......... Set the default-base-is-moof flag in tfhd atoms
     dash                         E.......... Write DASH compatible fragmented MP4
     cmaf                         E.......... Write CMAF compatible fragmented MP4
     frag_discont                 E.......... Signal that the next fragment is discontinuous from earlier ones
     delay_moov                   E.......... Delay writing the initial moov until the first fragment is cut, or until the first fragment flush
     global_sidx                  E.......... Write a global sidx index at the start of the file
     skip_sidx                    E.......... Skip writing of sidx atom
     write_colr                   E.......... Write colr atom even if the color info is unspecified (Experimental, may be renamed or changed, do not use from scripts)
     prefer_icc                   E.......... If writing colr atom prioritise usage of ICC profile if it exists in stream packet side data
     write_gama                   E.......... Write deprecated gama atom
     use_metadata_tags              E.......... Use mdta atom for metadata.
     skip_trailer                 E.......... Skip writing the mfra/tfra/mfro trailer for fragmented files
     negative_cts_offsets              E.......... Use negative CTS offsets (reducing the need for edit lists)
  -moov_size         <int>        E.......... maximum moov size so it can be placed at the begin (from 0 to INT_MAX) (default 0)
  -rtpflags          <flags>      E.......... RTP muxer flags (default 0)
     latm                         E.......... Use MP4A-LATM packetization instead of MPEG4-GENERIC for AAC
     rfc2190                      E.......... Use RFC 2190 packetization instead of RFC 4629 for H.263
     skip_rtcp                    E.......... Don't send RTCP sender reports
     h264_mode0                   E.......... Use mode 0 for H.264 in RTP
     send_bye                     E.......... Send RTCP BYE packets when finishing
  -skip_iods         <boolean>    E.......... Skip writing iods atom. (default true)
  -iods_audio_profile <int>        E.......... iods audio profile atom. (from -1 to 255) (default -1)
  -iods_video_profile <int>        E.......... iods video profile atom. (from -1 to 255) (default -1)
  -frag_duration     <int>        E.......... Maximum fragment duration (from 0 to INT_MAX) (default 0)
  -min_frag_duration <int>        E.......... Minimum fragment duration (from 0 to INT_MAX) (default 0)
  -frag_size         <int>        E.......... Maximum fragment size (from 0 to INT_MAX) (default 0)
  -ism_lookahead     <int>        E.......... Number of lookahead entries for ISM files (from 0 to 255) (default 0)
  -video_track_timescale <int>        E.......... set timescale of all video tracks (from 0 to INT_MAX) (default 0)
  -brand             <string>     E.......... Override major brand
  -use_editlist      <boolean>    E.......... use edit list (default auto)
  -fragment_index    <int>        E.......... Fragment number of the next fragment (from 1 to INT_MAX) (default 1)
  -mov_gamma         <float>      E.......... gamma value for gama atom (from 0 to 10) (default 0)
  -frag_interleave   <int>        E.......... Interleave samples within fragments (max number of consecutive samples, lower is tighter interleaving, but with more overhead) (from 0 to INT_MAX) (default 0)
  -encryption_scheme <string>     E.......... Configures the encryption scheme, allowed values are none, cenc-aes-ctr
  -encryption_key    <binary>     E.......... The media encryption key (hex)
  -encryption_kid    <binary>     E.......... The media encryption key identifier (hex)
  -use_stream_ids_as_track_ids <boolean>    E.......... use stream ids as track ids (default false)
  -write_btrt        <boolean>    E.......... force or disable writing btrt (default auto)
  -write_tmcd        <boolean>    E.......... force or disable writing tmcd (default auto)
  -write_prft        <int>        E.......... Write producer reference time box with specified time source (from 0 to 2) (default 0)
     wallclock       1            E..........
     pts             2            E..........
  -empty_hdlr_name   <boolean>    E.......... write zero-length name string in hdlr atoms within mdia and minf atoms (default false)
  -movie_timescale   <int>        E.......... set movie timescale (from 1 to INT_MAX) (default 1000)

```

就像开头我说的那样，因为MP4的灵活性比较好，变种形态也比较多，为了方便使用，FFmpeg就增加了很多符合标准但又有可能用不到的参数，我们一会儿抽取一些例子来讲讲。

在讲例子之前，我们先看一下这个帮助信息里面的内容，帮助信息的头部给出了MP4的文件扩展名.mp4，视频默认用H.264编码，音频默认用AAC编码。

接下来我们来看一下FFmpeg封装MP4常用的参数有哪些。

![图片](https://static001.geekbang.org/resource/image/47/a2/4788f2d19294d9f4b036bf0ed8042aa2.png?wh=2069x2864)

从参数的列表中可以看到，MP4的muxer支持的参数比较复杂，例如支持在视频关键帧处切片、支持设置moov容器的最大大小、支持设置encrypt加密等。下面我们用常见的参数来举几个例子。

### faststart参数

正常情况下，FFmpeg生成moov是在mdat写完成之后，但我们可以通过参数faststart把moov容器移动到mdat前面，我们可以参考下面这个例子。

```plain
./ffmpeg -i input.flv -c copy -f mp4 output.mp4

```

使用mp4info查看output.mp4的容器出现顺序。

![图片](https://static001.geekbang.org/resource/image/59/bf/59b0386632994a0d4bba6yy7f7d958bf.png?wh=1728x1250)

可以看到图中moov容器是在mdat的下边，如果使用参数faststart，就会在生成上边的结构之后将moov移动到mdat前面。

```plain
./ffmpeg -i input.flv -c copy -f mp4 -movflags faststart output.mp4

```

然后我们再使用mp4info查看MP4的容器顺序，可以看到moov被移动到了mdat前面。

![图片](https://static001.geekbang.org/resource/image/c9/94/c9bcd9d90d3a4b2d41e6472d52a3de94.png?wh=1728x1250)

### DASH参数

当生成DASH格式的时候，里面有一种特殊的MP4格式，其实我们也可以把它理解成MP4切片，可以通过DASH参数生成。

```plain
./ffmpeg -i input.flv -c copy -f mp4 -movflags dash output.mp4

```

使用mp4info查看容器格式的信息，稍微有些特殊，我们来看一下图片。

![图片](https://static001.geekbang.org/resource/image/db/ed/db6ef849yya8855082932af6807e50ed.png?wh=1728x1254)

从图中可以看到，这个DASH格式的MP4文件存储的容器信息与常规的MP4格式有些差别，以sidx、moof与mdat这三种容器为主。

有些时候，我们在做MP4切片操作的时候，可能会出现一些问题，例如，editlist的时间戳相关计算变量与实际数据对应的时间戳有偏差，导致视频丢帧或音画略有不同步的现象。这个时候我们可以考虑把use\_edilist操作项设置成忽略。

**MP4切片很常用，当我们做HLS/DASH直播、生成点播内容，还有做MP4上传云端实时转码等操作时，MP4切片都是比较常见的操作。**

通过这些例子，相信你已经对MP4生成部分的能力有一些了解了，剩余的能力我们可以课后自己一点点挖掘。接下来我们看一下FFmpeg的MP4文件解析操作。

### 用FFmpeg解析MP4文件

首先FFmpeg在解析MP4文件格式的时候，可能会因为MP4的内容生成得不标准产生一些奇奇怪怪的问题，例如前面我们提到的音视频不同步或者视频抖动等问题。FFmpeg针对出现的这类问题也做了格式上的兼容，但用户可能需要自己手动设置一些参数，定制一下，才可以解决这些问题。

FFmpeg这么做的主要原因是之前大部分用户使用时是正常的，异常素材只有少部分用户才会遇到。为了尽量不改变原有用户的使用习惯，只能通过新用户自己设置参数的形式来避免出现异常情况。我们看一下操作选项。

```plain
Demuxer mov,mp4,m4a,3gp,3g2,mj2 [QuickTime / MOV]:
    Common extensions: mov,mp4,m4a,3gp,3g2,mj2,psp,m4b,ism,ismv,isma,f4v,avif.
mov,mp4,m4a,3gp,3g2,mj2 AVOptions:
  -use_absolute_path <boolean>    .D.V....... allow using absolute path when opening alias, this is a possible security issue (default false)
  -seek_streams_individually <boolean>    .D.V....... Seek each stream individually to the closest point (default true)
  -ignore_editlist   <boolean>    .D.V....... Ignore the edit list atom. (default false)
  -advanced_editlist <boolean>    .D.V....... Modify the AVIndex according to the editlists. Use this option to decode in the order specified by the edits. (default true)
  -ignore_chapters   <boolean>    .D.V.......  (default false)
  -use_mfra_for      <int>        .D.V....... use mfra for fragment timestamps (from -1 to 2) (default auto)
     auto            -1           .D.V....... auto
     dts             1            .D.V....... dts
     pts             2            .D.V....... pts
  -use_tfdt          <boolean>    .D.V....... use tfdt for fragment timestamps (default true)
  -export_all        <boolean>    .D.V....... Export unrecognized metadata entries (default false)
  -export_xmp        <boolean>    .D.V....... Export full XMP metadata (default false)
  -activation_bytes  <binary>     .D......... Secret bytes for Audible AAX files
  -audible_key       <binary>     .D......... AES-128 Key for Audible AAXC files
  -audible_iv        <binary>     .D......... AES-128 IV for Audible AAXC files
  -audible_fixed_key <binary>     .D......... Fixed key used for handling Audible AAX files
  -decryption_key    <binary>     .D......... The media decryption key (hex)
  -enable_drefs      <boolean>    .D.V....... Enable external track support. (default false)
  -max_stts_delta    <int>        .D......... treat offsets above this value as invalid (from 0 to UINT32_MAX) (default 4294487295)

```

从内容中可以看到，FFmpeg的MP4 demuxer里提供了editlist相关的一些操作，比如ignore\_editlist、-use\_tfdt等。MP4切片时，可能会遇到切片的时间戳与editlist参考计算出来的时间戳对不上的问题，用户就可以使用-use\_tfdt选项，来选择是否使用tfdt里面的时间戳。

FFmpeg为什么会给MP4的demuxer加这么多兼容性的参数呢？

因为可以生成和处理MP4文件的工具不止FFmpeg，还有其他的工具，例如GPAC、Shaka-Packager。工具多了，生成出来的MP4文件可能不统一，存在一定的差异，这个差异就可能引起兼容性问题。

## 如何用GPAC生成MP4？

其实要说生成MP4更接近参考标准的，就要数GPAC了，可能你之前并没有听说过GPAC，但是GPAC里的MP4Box工具你应该听说过。下面我们先来了解一下MP4Box。和使用FFmpeg类似，我们先看一下help信息。

```plain
MP4Box --help

```

这是输出的内容。

```plain
MP4Box [option] input [option]

General Options:

-h (string):                   print help
	* general: general options help
	* hint: hinting options help
	* dash: DASH segmenter help
	* import: import options help
	* encode: encode options help
	* meta: meta handling options help
	* extract: extraction options help
	* dump: dump options help
	* swf: Flash (SWF) options help
	* crypt: ISMA E&A options help
	* format: supported formats help
	* live: BIFS streamer help
	* core: libgpac core options
	* all: print all the above help screens
	* opts: print all options
	* VAL: search for option named VAL (without - or --) in MP4Box, libgpac core and all filters

-hx (string):                  look for given string in all possible options
-nodes:                        list supported MPEG4 nodes
-node (string):                get given MPEG4 node syntax and QP infolist
-xnodes:                       list supported X3D nodes
-xnode (string):               get given X3D node syntax
-snodes:                       list supported SVG nodes
-languages:                    list supported ISO 639 languages
-boxes:                        list all supported ISOBMF boxes and their syntax
-fstat:                        print filter session statistics (import/export/encrypt/decrypt/dashing)
-fgraph:                       print filter session graph (import/export/encrypt/decrypt/dashing)
-v:                            verbose mode
-version:                      get build version
---  INPUT:                    escape option if INPUT starts with - character

```

帮助信息里有更详细的参数帮助信息，使用-h加对应的参数就可以得到，例如MP4Box -h dash，就可以查看dash切片帮助信息了。

我们使用 MP4Box查看一下MP4文件信息。

```plain
# MP4Box -info ~/Movies/Test/ToS-4k-1920.mov

* Movie Info *
	Timescale 1000 - 2 tracks
	Computed Duration 00:12:14.167 - Indicated Duration 00:12:14.167
	Fragmented File: no
	File Brand qt   - version 512
		Compatible brands: qt
	Created: UNKNOWN DATE	Modified: UNKNOWN DATE
File has no MPEG4 IOD/OD
1 UDTA types: A9737772 (1)

Track # 1 Info - TrackID 1 - TimeScale 24
Media Duration 00:12:14.166 - Indicated Duration 00:12:14.166
Track has 1 edit lists: track duration is 00:12:14.167
Media Info: Language "Undetermined (und)" - Type "vide:avc1" - 17620 samples
Visual Sample Entry Info: width=1920 height=800 (depth=24 bits)
Visual Track layout: x=0 y=0 width=1920 height=800
MPEG-4 Config: Visual Stream - ObjectTypeIndication 0x21
AVC/H264 Video - Visual Size 1920 x 800
	AVC Info: 1 SPS - 1 PPS - Profile High @ Level 4
	NAL Unit length bits: 32
	Pixel Aspect Ratio 1:1 - Indicated track size 1920 x 800
	Chroma format YUV 4:2:0 - Luma bit depth 8 - chroma bit depth 8
	SPS#1 hash: DEC7C9D830854068543D5AE5BC84AA68081EC57C
	PPS#1 hash: 12874FF8439E10C45D6C9B519B94BDAADC9759BD
Self-synchronized
	RFC6381 Codec Parameters: avc1.640028
	Average GOP length: 17 samples
	Max sample duration: 1 / 24

Track # 2 Info - TrackID 2 - TimeScale 44100
Media Duration 00:12:14.122 - Indicated Duration 00:12:14.122
Track has 1 edit lists: track duration is 00:12:14.123
Media Info: Language "Undetermined (und)" - Type "soun:mp4a" - 31616 samples
MPEG-4 Config: Audio Stream - ObjectTypeIndication 0x40
MPEG-4 Audio AAC LC (AOT=2 implicit) - 2 Channel(s) - SampleRate 44100
Synchronized on stream 1
	RFC6381 Codec Parameters: mp4a.40.2
Alternate Group ID 1
	All samples are sync
	Max sample duration: 1024 / 44100

```

其实从帮助信息中我们可以看到，MP4Box也可以切DASH和HLS，除了MP4Box，我们还可以尝试使用Shaka-Packager来做对应的操作。

## Shaka-Packager的HLS与DASH

Shaka-Packager是Google的一个开源项目，除了用FFmpeg和GPAC做HLS、DASH之外，用Shaka-Packager其实也是个不错的选择，我们稍微了解一下。

例如，用Shaka-Packager做一个HLS视频流加密操作。

```plain
packager 'input=../in.mp4,stream=video,segment_template=output$Number$.m4s,playlist_name=video_playlist.m3u8,init_segment=init.mp4'
--hls_master_playlist_output="master_playlist.m3u8"
--hls_base_url="http://127.0.0.1/" --enable_raw_key_encryption
--protection_scheme cbcs --keys
key=61616161616161616161616161616161:key_id=61616161616161616161616161616161
--clear_lead 0

```

这样就可以通过Shaka-Packager生成一个DRM的HLS了，输入一个MP4文件，视频流输出m4s，列表名为video\_playlist.m3u8，mp4切片的初始文件名为init.mp4，master列表名为master\_playlist.m3u8，使用raw\_key方式加密内容，加密保护模式为cbcs模式，密钥是61616161616161616161616161616161，切片的init之后的第一个MP4切片文件不加密，从第二片开始加密。

Shaka-Packager也是一个很大的项目，更多的能力需要你自己慢慢去挖掘。 [Shaka-Packager官方文档](https://shaka-project.github.io/shaka-packager/html/) 的内容也比较全，你可以参考一下。

总的来说，Shaka-Packager和GPAC比FFmpeg要简单得多，使用的API操作也比较容易，所以如果不是多格式、多codec，对兼容性要求不高且音视频应用场景简单的话，Shaka-Packager和GPAC也是不错的选择。

## 小结

MP4格式因其开放性和灵活性，使用范围非常广泛，用MP4做切片后可以封装成HLS或者DASH做分发，日常的使用频率是比较高的。因此它是我们必须要掌握的一种格式。

![图片](https://static001.geekbang.org/resource/image/0a/fd/0a1f3cc5b0d97efaeyy3f97c69e08bfd.png?wh=1920x835)

能够生成和解析MP4的工具有很多，FFmpeg就是其中之一。考虑兼容性的问题，FFmpeg给出了很多参数，其中有一些比较常用的参数，如faststart（把moov容器移动到mdat前面）、DASH（兼容DASH格式的MP4分片）等参数是需要我们掌握的。除了FFmpeg之外，在简单场景下我们还可以用GPAC或者Shaka-Packager做MP4的流媒体处理。

学完今天的内容，你就可以使用FFmpeg做一些MP4的日常处理了，如果你想要获得更多的能力支持，需要再深入研究一下这三个工具的参数，并且动手去操作一下。

## 思考题

一个视频流转成MP4文件时，如何用FFmpeg对视频流内容做加密呢？加密之后如何用FFmpeg解密并顺利地播放出来呢？欢迎在评论区留下你的思考，也欢迎你把这节课分享给需要的朋友，我们下节课再见！