你好，我是Barry。

上节课我们根据游客的操作动线，完成了直播中心游客需求功能的设计和开发工作,相信你对直播中心的整体功能已经有了新的认识。

作为一个视频平台，直播功能是平台的刚需，用户通过直播可以进行授课、个人展示、带货等等，这也是当下非常主流的媒体宣传方式。

这节课我们继续推进直播模块的功能开发，把焦点放在直播功能和页面的开发实现上。这次我们先从主播的视角出发，从需求分析开始，一步步设计开发平台的直播功能。

## 直播功能的需求有哪些

先来梳理一下直播模块的功能需求。

我们需要从两个维度综合分析。从平台的维度来看，平台需要保证直播内容是健康、绿色、安全的，所以一定要对主播进行实名认证，这就需要我们实现认证功能；另外，从主播的维度来看，在完成实名认证之后，这时候需要提交直播相关信息并发起直播。

以上我们对功能需求就梳理完了，接下来我们就要实现每个模块的功能。

## 页面设计

根据前面的需求分析，我们把直播模块整体切割成两个模块。

一个模块是申请中心，用户可以在该模块完成个人信息的实名认证。你可以参考后面这张表格，来了解用户需要提交的信息具体涉及的主要字段。当然，你也可以灵活添加调整，但是一定保证数据库中新增了字段。

![](https://static001.geekbang.org/resource/image/28/a3/28f8db9ab79c74ba11b50d32866bd5a3.jpg?wh=2574x845)

明确了需要哪些用户信息之后，接下来就是设计实现界面样式，这一部分我们通过折叠菜单的形式来展示。

结合界面效果截图我们可以看到，这里有两个选择项，分别是申请中心和直播间。点击不同的菜单，用户就可以看到对应的功能区，用户无需跳转界面，这样反而能更高效地解决问题。

![](https://static001.geekbang.org/resource/image/19/bf/192f24eecf1cb401551dbbf756cd28bf.jpg?wh=2830x1370)

## 页面代码实战

菜单组件我们依然使用Element的组件，应用组件的方法和我们前面讲过的一样，相信经过前面的练习现在你已经可以应对自如了。你需要重点关注的是组件的API以及组件本身的一些属性方法。如果想全面学习了解菜单组件，你还可以直接查看 [menu组件的官网链接](https://element.eleme.cn/#/zh-CN/component/menu)。

好，我们继续来看直播功能里页面菜单怎么实现。我们先用栅格把菜单组件做一个定位，然后开始做菜单组件的开发，具体实现代码是后面这样。

```plain
<el-col :span="4">
  <el-menu
    default-active="1-1"
    class="el-menu-vertical-demo"
    @open="handleOpen"
    @close="handleClose"
    :unique-opened="true"
    text-color="black"
    active-text-color="#ffd04b"
    menu-trigger="click"
    @select="handleSelect"
  >
    <el-submenu index="1">
      <template slot="title">
        <i class="el-icon-location"></i>
        <span>直播操作台</span>
      </template>
      <el-menu-item-group>
        <el-menu-item index="1-1">申请中心</el-menu-item>
        <el-menu-item index="1-2">直播间</el-menu-item>
      </el-menu-item-group>
    </el-submenu>
  </el-menu>
</el-col>

```

这段代码的重点是 <el-menu>的 **select 方法**，每一级菜单都有一个index值用来表示对应的层级，因此在用户点击菜单选项的时候，我们需要通过index值的判断来更换右侧展示的内容。

接下来就到了申请中心的页面实现，我们还是边看代码边分析。

```plain
<el-card v-if="status === '1-1'" class="card">
  <p class="data-title">申请信息</p>
  <p v-show="!applyStatus" class="applyTitle">您已认证成功，赶快去直播吧!</p>
  <p v-show="applyStatus" class="applyTitle">实名认证成功后,可以享受开通直播间等服务!</p>
  <el-form
    ref="form"
    :model="form"
    :rules="formRule"
    label-position="left"
    label-width="80px"
    v-show="applyStatus"
  >
    <el-form-item label="真实姓名" prop="name">
      <el-input v-model="form.name"></el-input>
    </el-form-item>
    <el-form-item label="证件类型" prop="type">
      <el-select v-model="form.type" placeholder="请选择证件类型">
        <el-option label="身份证" value="1"></el-option>
        <el-option label="护照（中国签发）" value="2"></el-option>
        <el-option label="其他国家或地区证明" value="3"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item label="证件号码" prop="number">
      <el-input v-model.number="form.number"></el-input>
    </el-form-item>
    <el-form-item label="证件上传">
      <el-upload
        class="avatar-uploader"
        :action="存储文件的服务器地址"
        :show-file-list="false"
        :on-success="handleAvatarSuccess"
        :before-upload="beforeAvatarUpload"
      >
        <img v-if="imageUrl" :src="imageUrl" class="avatar" />
        <i v-else class="el-icon-plus avatar-uploader-icon"></i>
      </el-upload>
    </el-form-item>
    <el-form-item>
      <el-button
        class="buttonC"
        type="primary"
        @click="submitForm('form')"
      >提交认证</el-button>
    </el-form-item>
  </el-form>
</el-card>

```

这里就是简单的表单应用，让用户能够填写和提交相关的信息即可。唯一需要注意的就是v-if的应用，我们通过对status的值判断最终呈现申请信息内容。其实这个status就是我在上面提到的每一个菜单的index值。

紧接着我们看看如何呈现页面，具体的实现代码是后面这样。

```plain
handleSelect(index, indexPath) {
  console.log(indexPath); //['1', '1-2']
  console.log(index); //1-2
  this.status = index;
},

```

可以看到，这里我们用到了@select方法handleSelect，它主要包含两个参数——key和keypath，分别代表选中菜单的index和选中菜单的indexPath。在点击触发handleSelect方法的时候，就会给status值进行赋值，这样展示的页面内容就可以根据status来判断了。

在status值改变之后，对应的页面card内容也会随之变化，这样我们就实现了申请中心的功能。菜单中的“直播间”主要是用来配置直播相关的信息，整体的实现方式与申请中心一致，区别就是申请中心是以主播信息为核心，而直播间配置更加关注的则是给更多用户展示每一场直播的相关信息。

到这里，信息配置模块的页面开发告一段落。直播前的准备已经就绪，我们下一步就来搞定直播里的视频播放器，这是我们直播中最关键的功能。

## 认识一下Video-Player

平台的直播应用方面，我们选取Video-Player充当视频播放器。

选择Video-Player有两个原因：第一个就是除了前面学过的DPlayer播放器以外，我想带你多接触一些不同的播放器，丰富一下你个人的技术库。第二是因为相比DPlayer，Video-Player更适合做平台的直播。为什么说它更适合呢？我们接着往下看。

Video-Player是由俄罗斯的开发团队 2007 年开始开发的。它最初是在俄罗斯的一个社交网站上开始流行的，之后在2010年被翻译成英语并在全球范围内推广。在经历了一些版本的更新和改进之后，Video-Player在 2014 年被开源，并成为了广受欢迎的知名开源项目。

接下来，我们从应用场景和相关技术支持的角度比较一下DPlayer与video-player，你就明白我们为什么选择后者了。

Video-Player适合在各种平台上播放多种格式的视频，包括网络视频平台、本地播放器、移动设备等。它支持的编解码器和流媒体格式非常丰富，可以轻松地支持各种主流的流媒体服务，如YouTube、Facebook Live等。

另外，Video-Player采用了先进的H.265视频编码技术，可以提供更加清晰、流畅和低延迟的视频播放体验。它还支持多种音频格式，可以为用户带来更加逼真的音频和视频体验，这个是它非常大的一个优势。

Dplayer则更加注重原始素材的加工和处理，提供的素材管理和调度工具更为丰富，支持多种视频编辑和转换工具，用户制作原生视频内容会更加方便。此外，Dplayer还支持实时流媒体服务，可以实时转码并推流到不同的平台上。

综合来看，如果你需要在网络直播平台上使用视频播放器，Video-Player更适合。但如果你只需要在本地或移动设备上播放视频，Dplayer更适合。

如果你有兴趣，课后可以看看Video-Player的 [官网链接](https://videojs.com/)，进入官网你会发现是Video.js官网，不过不用疑惑，Video.js是一个流行的JavaScript视频播放器库，而Video-Player是Video.js的一个分支。两者在功能和支持的编解码器方面有一定的重叠，但Video-Player对流行视频平台和格式的原生支持更多一些，自定义选项也更加丰富。

## 播放器Video-Player实战

全面了解了Video-Player之后，我们进入实战环节。在Vue中使用第三方应用的流程，相信你已经非常熟练了，下面请跟上我的节奏，先从安装环节入手。

我们先要安装Video-Player，在对应的项目路径下执行下面的命令即可。

```plain
cnpm install vue-video-player --save

```

然后我们需要在main.js中引入VideoPlayer。

```plain
import VideoPlayer from 'vue-video-player'
Vue.use(VideoPlayer)

```

与此同时，我们还要引入播放器需要的CSS内容，代码是后面这样。

```plain
require('video.js/dist/video-js.css')
require('vue-video-player/src/custom-theme.css')

```

因为我们的直播流采用的是m3u8文件，所以我们下一步需要导入HLS。HLS是什么呢？HLS是一种流媒体传输协议，它允许流媒体服务器向客户端推送实时流媒体流，Video.js可以通过JavaScript来处理HLS流媒体传输。

Video.js提供了一个简单易用的API，可以轻松地处理HLS流媒体传输，并支持多种流行的视频平台和格式。

接下来我们就在项目中安装一下HLS，执行命令我写在了后面。

```plain
cnpm install videojs-contrib-hls --save

```

同样的道理，我们依旧需要在main.js文件中引入，具体代码如下。

```plain
在main.js中引入
import videojsC from 'videojs-contrib-hls'
Vue.use(videojsC)

```

这样我们就完成了整个安装的过程。

那么如何在页面中使用Video-Player呢？第一步，我们需要在直播的页面中引入Video-Player，这样在页面中才可以使用它。

```plain
import { videoPlayer } from "vue-video-player";

```

第二步就是实现Video-Player组件。你可以对照后面的具体代码听我讲解。

```plain
<video-player
  class="video-player vjs-custom-skin"
  ref="videoPlayer"
  :playsinline="false"
  :options="playerOptions"
  @play="onPlayerPlay($event)"
  @pause="onPlayerPause($event)"
></video-player>

```

对照代码可以看到，这里面放了两种方法，分别是 **play()播放方法** 和 **pause()暂停方法**。当然video-player API有很多方法，这个我稍后再给你梳理。

接下来我们需要重点关注的是 **options的参数playerOptions**。对照后面的代码和详细的代码注释，你很容易就能明白每个参数的含义和作用。

```plain
playerOptions: {
  playbackRates: [0.7, 1.0, 1.5, 2.0], //播放速度
  autoplay: false, //如果true,浏览器准备好时开始回放。
  muted: false, // 默认情况下将会消除任何音频。
  loop: false, // 导致视频一结束就重新开始。
  preload: "auto", // 建议浏览器在<video>加载元素后是否应该开始下载视频数据。auto浏览器选择最佳行为,立即开始加载视频（如果浏览器支持）
  language: "zh-CN",
  aspectRatio: "16:9", // 将播放器置于流畅模式，并在计算播放器的动态大小时使用该值。值应该代表一个比例 - 用冒号分隔的两个数字（例如"16:9"或"4:3"）
  fluid: true, // 当true时，播放器将按比例缩放以适应其容器。
  sources: [
    {
      type: "application/x-mpegURL",
      src:"你的直播m3u8地址（必填），当然在开发工程中，这里需要设置为动态值"
    }
  ],
  poster: "poster.jpg", //你的封面地址
  width: document.documentElement.clientWidth,
  notSupportedMessage: "此视频暂无法播放，请稍后再试", //允许覆盖Video.js无法播放媒体源时显示的默认信息。
  controlBar: {
    timeDivider: true, //当前时间和持续时间的分隔符
    durationDisplay: true, //表示当前时间和持续时间的显示格式
    remainingTimeDisplay: true,//表示当前时间还剩余的时间的显示格式
    fullscreenToggle: true //全屏按钮
  }
}

```

前面我们提到的两个方法——播放和暂停的方法。我们在方法里可以放置要执行的相关代码逻辑，你可以结合后面的例子体会一下用法。

```plain
methods: {
    onPlayerPlay(player) {
      console.log("play");
      //TODO:开始播放需要执行的相关业务操作
      this.$refs.videoPlayer.player.play();
    },
    onPlayerPause(player) {
      //TODO：暂停需要执行的相关业务操作
      console.log("pause");
    }
}

```

我还帮你整理了Video-Player相关操作的常用方法，在之后的开发中你可以直接应用这些方法，解决你在播放器功能上的需求。

```plain
//整体的写法@后为固定方法名 =后自定义，和播放、暂停的写法一致
@play="onPlayerPlay($event)"
@pause="onPlayerPause($event)"
@ended="onPlayerEnded($event)"
@waiting="onPlayerWaiting($event)"
@playing="onPlayerPlaying($event)"
@loadeddata="onPlayerLoadeddata($event)"
@timeupdate="onPlayerTimeupdate($event)"

//具体的用法和含义写在下面

// 播放回调
onPlayerPlay(player) {
console.log('player play!', player)
},

// 暂停回调
onPlayerPause(player) {
console.log('player pause!', player)
},

// 视频播完回调
onPlayerEnded($event) {
console.log(player)
},

// 当视频播放时出现暂停、停止或重新加载等状态变化时，调用该方法
onPlayerWaiting($event) {
console.log(player)
},

// 当用户开始播放视频时，调用该方法
onPlayerPlaying($event) {
console.log(player)
},

// 当播放器在当前播放位置下载数据时触发
onPlayerLoadeddata($event) {
console.log(player)
},

// 当视频播放时出现时间更新时，调用该方法
onPlayerTimeupdate($event) {
console.log(player)
}

```

完成前面的步骤，我们还要通过后端接口请求获取到sources中的src地址，这样就能使用Video-Player在平台里实现直播的功能了。因为整体实现过程的步骤比较多，建议课后你再自己把整个流程回顾一下。

## 总结

不知不觉又到了课程尾声，我们一起来回顾总结一下。

这节课我们主要实现了用户在平台的直播功能。在此之前我们要先设计好用户的直播申请功能，这一部分，你需要重点关注两点：一是 **新组件<el-menu>的应用**，二是如何通过v-show的指令控制实现菜单切换的功能。

在直播功能的开发实践环节，我们使用了Video-Player播放器，它有强大的综合功能，我们发现Video-Player更适合应用在平台类的直播。当然如果你只需要在本地或移动设备上播放视频，Dplayer更适合，你可以灵活选择。

Video-Player整个安装配置的过程是这节课的重点，也是我建议你多花心思的部分，只要你细心，按部就班跟着课程讲解来实现，一定可以拿下。完成安装之后，你就可以参照我提供的实践代码，自己先把播放器应用起来，通过现成的第三方直播链接测试一下效果。当然，在学完课程的后端直播模块之后，你就可以打通前后端，在平台内实现自己的直播应用了。

## 思考题

直播中心应用中我们一起实现了申请中心，你可以尝试模拟实现一下直播间信息的配置。请你思考一下需要用户提交哪些信息呢？页面又该怎样实现呢？

期待你在留言区和我交流互动。如果这节课的内容让你感觉实用有趣的话，别忘了推荐给你的伙伴，让我们一起学习进步。