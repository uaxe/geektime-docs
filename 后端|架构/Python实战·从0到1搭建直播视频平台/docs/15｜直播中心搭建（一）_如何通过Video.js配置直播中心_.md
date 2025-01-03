你好，我是Barry。

在前面的几节课，我们完成了视频平台整体功能前端的搭建与开发，实现了平台大部分的功能。

从这节课起，我们更上一层楼，一起来学习实践直播中心的搭建与配置。直播中心是视频平台中较为核心的功能模块，近几年，随着直播的大火，很多的公司开始进军直播行业，对相关人才的需求也在与日俱增。

直播中心应该具备哪些功能？界面设计该怎么做？业务逻辑又该如何编排？接下来，我们一起来揭秘，从0到1一步步设计和实现一个直播中心模块。

## 直播中心功能梳理

直播中心的核心功能就是视频直播，让用户在平台内通过直播形式把自己期望展示的内容呈现出来。直播的种类一定是非常多元的，比方说营销带货、直播上课、生活日常、游戏直播等等形式。丰富的直播种类可以覆盖到更多用户的偏好，让用户对视频平台更加喜爱。

我们这就一起来梳理一下，用户在直播中心的操作动线以及中心内整体的功能设计。我用思维框架图的方式整理了整个直播中心的大框架，你可以先看一下。

![](https://static001.geekbang.org/resource/image/16/11/16c853b325fcyy73db0d4c7cd9d4e511.jpg?wh=1990x1158)

### 中心入口

整个直播中心作为一个功能模块，我们首先要关注的就是用户操作动线。用户操作的起点自然是直播的入口，我们在哪里呈现入口呢？

这里我们要考虑到，这一模块的使用包括两种角色。

一种角色是作为 **直播的观众**。用户在平台首页可以看到直播中心入口，点击进入直播列表，直播列表主要呈现的就是当前正在直播的所有视频，并且要分类别展示。用户可以点击任意视频，进入到直播的详情页。

另一种角色就是 **主播**。主播需要在平台内直接发起直播。因为发起直播属于常用功能，我们把它归类为与用户维度紧密相关的功能模块，所以把该入口放在用户个人下拉列表中，用户可以直接操作，发起直播功能。

两个入口的位置如下图。

![](https://static001.geekbang.org/resource/image/a6/cd/a62be2402e0a348317e5eb7efd2f71cd.jpg?wh=1641x545)

### 直播列表

直播列表是直播中心的必备功能，你也可以把它理解为平台的直播视频区。它的作用是呈现正在直播的视频，便于用户根据自己的喜好查看选择。

在这里我们需要做两个功能模块。第一区块用于展示热门直播，向用户推荐一些优质高粉丝量的直播视频，供用户选择观看。

第二区块是直播分类展区，我们需要分类展示直播视频，大致分区可以和视频首页的分区保持一致。这是因为，全部视频放在一起呈现显得非常冗杂，而分类展示更容易让用户清晰地锁定自己喜欢的类别。

### 直播详情

当用户点击查看自己喜欢的直播视频后，就会从列表页面跳转到直播详情页面，这个功能逻辑与视频列表到视频详情列表的功能逻辑相似，但是呈现的效果和功能是完全不同的。

在视频直播详情页，我们主要展示的就是直播介绍、主播的相关信息和直播内容，并设置相关的互动功能（例如弹幕、点赞），这样我们就能满足用户对直播的功能需求。当然，还有一些能提升用户使用体验的特色功能，比方说在这里放一些同类型热度较高的直播视频列表，方便用户可在详情页里实现直播内容的切换，而不用回退到首页再进入其他直播视频。

好，我们已经从用户视角对整个直播中心模块做了功能梳理，现在整个功能动线就非常清晰了，接下来我们一起来看看具体功能的实现。

## 直播相关页面布局实现

这里我给准备了一张直播界面的样例图作为参考，接下来我们一起看看怎样实现相应的功能开发吧。

![](https://static001.geekbang.org/resource/image/69/13/69fd9434780bcaa16a32743cb47e0913.jpg?wh=1949x661)

### 直播视频列表页的实现

我们把整个页面切割成上下两个部分。上半部分用来展示在游客访问列表时热度比较高的直播。因此，这一部分我们需要设定一个窗口位，而且我们还要考虑到整个页面动态适配的问题，这样才能保证播放器可以根据不同尺寸大小进行适配，具体可以采用Element的Layout组件来实现，

Layout组件主要用于做页面布局，可以按我们设定好的参数对页面进行切割分块。

整体页面的块数一共是24份，你可以随意切割，只要相加起来的和为24就可以。Layout组件相比传统的CSS设定尺寸的模式会更加便捷。

为了让你明白它的实现方法，我们直接来看后面的官方案例。

```plain
//这个是整体一块
<el-row>
  <el-col :span="24"><div class="grid-content bg-purple-dark"></div></el-col>
</el-row>
//分割成两块，各占12
<el-row>
  <el-col :span="12"><div class="grid-content bg-purple"></div></el-col>
  <el-col :span="12"><div class="grid-content bg-purple-light"></div></el-col>
</el-row>
//分割成三块，各占8
<el-row>
  <el-col :span="8"><div class="grid-content bg-purple"></div></el-col>
  <el-col :span="8"><div class="grid-content bg-purple-light"></div></el-col>
  <el-col :span="8"><div class="grid-content bg-purple"></div></el-col>
</el-row>
//分割成四块，各占6
<el-row>
  <el-col :span="6"><div class="grid-content bg-purple"></div></el-col>
  <el-col :span="6"><div class="grid-content bg-purple-light"></div></el-col>
  <el-col :span="6"><div class="grid-content bg-purple"></div></el-col>
  <el-col :span="6"><div class="grid-content bg-purple-light"></div></el-col>
</el-row>
//分割成六块，各占4
<el-row>
  <el-col :span="4"><div class="grid-content bg-purple"></div></el-col>
  <el-col :span="4"><div class="grid-content bg-purple-light"></div></el-col>
  <el-col :span="4"><div class="grid-content bg-purple"></div></el-col>
  <el-col :span="4"><div class="grid-content bg-purple-light"></div></el-col>
  <el-col :span="4"><div class="grid-content bg-purple"></div></el-col>
  <el-col :span="4"><div class="grid-content bg-purple-light"></div></el-col>
</el-row>

```

具体的参数说明你可以直接参考 [Layout官网API](https://element.eleme.cn/#/zh-CN/component/layout)，这里我们重点需要关注的就是利用Layout去实现自适应，这部分需要用到后面的参数设置来实现。

![](https://static001.geekbang.org/resource/image/92/e1/9223f5e80a40a2226f679b11e2328ae1.jpg?wh=3377x1614)

具体实现代码是后面这样。

- xs表示页面在手机展示，屏幕宽度小于768px
- sm表示页面在平板展示，屏幕宽度等于或者大于768px
- md表示页面在PC桌面展示，屏幕宽度大于或者等于768px
- lg表示页面在大桌面展示，屏幕宽度大于或者等于992px
- xl表示页面在超大屏幕展示，屏幕宽度大于等于1200px

```plain
<el-row :gutter="10">
  <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="1"><div class="grid-content bg-purple"></div></el-col>
  <el-col :xs="4" :sm="6" :md="8" :lg="9" :xl="11"><div class="grid-content bg-purple-light"></div></el-col>
  <el-col :xs="4" :sm="6" :md="8" :lg="9" :xl="11"><div class="grid-content bg-purple"></div></el-col>
  <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="1"><div class="grid-content bg-purple-light"></div></el-col>
</el-row>

```

观察前面的代码，相信你可以看出每一行设置的值分别代表了在不同屏幕大小下显示的宽度。同时我们再次验证了在每一种尺寸下， **页面横向块数总和加起来总是等于24**，这一点我们在编写的过程中一定要注意。

借鉴前面的思路，我们继续思考——如果想让播放器能够适应不同屏幕尺寸应该如何实现。具体代码实现是后面这样。

```plain
<div class="player">
      <!-- gutter用于间隔列距 -->
    <el-row :gutter="10">
      //这里我们应对各类大小，统一设置大小为4个单位
      <el-col :xs="4" :sm="4" :md="4" :lg="4" :xl="6">这里可以为空，用来占位</el-col>
      <el-col :xs="16" :sm="16" :md="16" :lg="16" :xl="12">
        <div class="wenzi">
          //当用户鼠标悬浮到页面中央，显示"进入直播间"的字样
          <p @click="goOnline">进入直播间</p>
        </div>
        <!-- 播放的实现采用组件 -videojs -->
        <video-player
          class="video-player vjs-custom-skin"
          ref="videoPlayer"
          :playsinline="true"
          :options="playerOptions"
          @play="onPlayerPlay($event)"
          @pause="onPlayerPause($event)"
          style="height:100%"
        ></video-player>
      </el-col>
      <el-col :xs="4" :sm="4" :md="4" :lg="4" :xl="6">
        这里我们可以放一些推荐视频，或空着占位
      </el-col>
    </el-row>
  </div>

```

后面是对应的CSS代码，其中的重点属性我都做了注释，结合注释你就能明白代码的含义和作用了。

```plain
<style>
.player {
  //这是背景图
  background: url("../../../assets/image/onlineB.png") no-repeat;
  background-size: 100% 100%; //让图片全部展开 铺满整个区域 图片不满的情况
  .wenzi {
    width: 200px;
    height: 300px;
    position: absolute; //绝对定位属性
    left: 48%; //通过距左侧和上侧的距离
    top: 48%;
    p {
      color: #298ce9;
      font-size: 19px;
      position: absolute;
      z-index: 9999;
      font-weight: bolder;
      opacity: 0; //透明度
      cursor: pointer;
    }
  }
  //当鼠标悬浮在文字上时，改变层叠级别和透明度
  .wenzi:hover p {
    z-index: 9999; //值越高，图层越位于上层
    opacity: 1; //值越大，透明度越低，以此组合最终把字样展示出来
  }
}
</style>

```

到这里，我们已经完成了热度直播推荐模块内容呈现的代码设计和实现。你也可以自己发挥想象，对展示的内容进行设计。

直播分类列表页和首页展示的布局样式一致，我们只需要根据类别来区分就可以了。如果你希望巩固一下自己的CSS和Element组件库应用能力，课后可以自己试着设计实现一下。

### 直播详情页的实现

接下来就是直播详情页的实现。我们同样要提前设计好这一部分都需要展示哪些内容。

结合详情页面的展示需求，在整个页面最为核心的是两部分：第一部分用来展示主播信息；第二部分就是视频播放器。当然，这个页面里我们也可以展示主播的介绍、个人动态等信息。

后面是直播详情页的效果预览图。

![](https://static001.geekbang.org/resource/image/8f/60/8f8c49bb6e8e94348dbdf4cb78c5e260.jpg?wh=1963x948)

页面的适配我们依旧使用Layout组件来实现。

为了展示主播的基本信息，我们还会应用到一些Element的组件，例如头像组件avatar、标签组件tag、标签页组件Tabs，还有大量的Element图标icon。至于样式修饰还是应用CSS相关属性来实现。你可以参考后面的具体代码实现和详细注释。

```plain
 <div class="player">
      <el-row :gutter="10">
        <el-col :xs="3" :sm="4" :md="4" :lg="4" :xl="4">
          <div class="left">这里可以放你想展示的内容，考虑到界面的整洁，这一部分非必需</div>
        </el-col>
        // 下面的模块用于展示直播内容，依旧用Layout做适配
        <el-col :xs="18" :sm="16" :md="16" :lg="16" :xl="16">
          <el-card class="card" shadow="hover">
            <div class="onlineT">
              //这里应用的是Element的头像组件，直接对应src放上对应的图片地址即可
              <el-avatar src=""></el-avatar>
               //以下所有的展示信息都可自定义，只需改变图标和文字描述，当然对应展示的内容是动态获取的
              <el-tag class="online-tag" size="mini" type="warning">直播中</el-tag>
              <p>一起来体验游戏的魅力</p>
              <i class="el-icon-share">分享</i>
              <i class="el-icon-warning">举报</i>
              <i class="el-icon-s-custom">粉丝 {{fansNum}}万</i>
            </div>
            <div class="line-two">
              <el-tag class="online-lv" effect="dark" size="mini" type="danger">LV 89</el-tag>
              <p>Barry</p>
              <i class="el-icon-present">{{presentNum}}</i>
              <i class="el-icon-star-on">收藏</i>
              <i class="el-icon-video-camera-solid">回放</i>
              <i class="el-icon-s-flag">粉丝群</i>
              <i class="el-icon-s-data">数据</i>
            </div>
          </el-card>
          <div style="height:80%">
          //这是播放器，后面我们会详细讲解
            <video-player
              class="video-player vjs-custom-skin"
              ref="videoPlayer"
              :playsinline="false"
              :options="playerOptions"
              @play="onPlayerPlay($event)"
              @pause="onPlayerPause($event)"
            ></video-player>
          </div>
        </el-col>
        <el-col :xs="3" :sm="4" :md="4" :lg="4" :xl="4">
          <div>这里可放置内容，也可占空位</div>
        </el-col>
      </el-row>
    </div>
    <div style="margin-top:40px">
      <el-row :gutter="20">
        <el-col :span="16" :offset="4">
          <el-card shadow="always">
          //这里用到tabs组件，分别展示主播简介和生活动态
          //组件使用较为简单，具体详情也可直接了解element官网
            <el-tabs type="border-card">
              <el-tab-pane>
                <span slot="label">
                  <i class="el-icon-user-solid">主播简介</i>
                </span>
                这里是主播的的介绍，
                <br />吃鸡、王者、战地、CS样样精通
                <br />个人获得各个赛区的冠军
                <br />每晚8：00准时开播
              </el-tab-pane>
              <el-tab-pane>
                <span slot="label">
                  <i class="el-icon-trophy-1">个人动态</i>
                </span>
                <ul>
                  <li>
                  //可用于类似朋友圈信息展示
                    <p style="font-size:16px;color:red;padding-bottom:10px">今天天气真不错</p>
                    <img src="图片地址" alt="动态图片">
                  </li>
                  <hr>
                  <li>
                    <p style="font-size:16px;color:red;padding-bottom:10px">努力登顶</p>
                    <img src="图片地址" alt="登顶">
                  </li>
                </ul>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>

```

对应的CSS样式是后面这样，你可以和前面代码的class值一一对应。具体的代码用途和属性相信你通过注释就能弄明白。

这里我提供的代码只是参考，掌握了思路以后，你可以灵活应用，还可以自己尝试来实现。

```plain
.player {
  //背景图展示
  background: url("../../../assets/image/onlineB.png") no-repeat;
  background-size: 100% 100%; //让图片全部展开 铺满整个区域 图片不满的情况
}
.card {
  background-color: transparent;
  border-radius: 20px; //设置card圆角
}
.onlineT {
  width: 100%;
  color: #f2f2f2;
  padding-left: 10px;
  img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }
  .online-tag {
    margin-left: 40px;
    size: 5px;
  }
  .el-icon-share {
    font-size: 14px;
    float: right;
  }
  .el-icon-warning {
    font-size: 14px;
    float: right;
    padding-right: 10px;
  }
  .el-icon-s-custom {
    font-size: 14px;
    float: right;
    padding-right: 10px;
  }
  .el-icon-video-play {
    content: "\E7C0"; //Emoji表情符
    font-size: 30px;
    color: aqua;
    margin-left: 40px;
  }
  p {
    font-size: 18px;
    font-weight: bold;
    padding: 0 0 0 20px;
    color: rgb(231, 157, 18);
    display: inline-block;
  }
}
//以下就是基础应用，你可以完成理解
.line-two {
  width: 500px;
  color: #f2f2f2;
  padding: 10px 10px 0 100px;

  p {
    display: inline-block;
    font-size: 10px;
    margin-left: 6%;
  }
  i {
    font-size: 17px;
    font-weight: bolder;
    margin-left: 10px;
  }
  .el-icon-present {
    font-size: 17px;
    font-weight: bolder;
    margin-left: 10px;
    color: #f56c6c;
  }
  .el-icon-star-on {
    color: greenyellow;
  }
  .el-icon-video-camera-solid {
    color: cadetblue;
  }
  .el-icon-s-flag {
    color: #f56c6c;
  }
  .el-icon-s-data {
    color: blue;
  }
}

```

进行到这里，我们把用户从点击直播中心到观看直播的全部流程都顺下来了。经过这个完整的链路，我们已经实现了游客维度的直播间页面呈现。

## 总结

好，我们一起来总结回顾一下这节课的重点内容。

设计直播模块的时候，我们一定要对用户的整个操作动线非常清晰。关键是 **入口设置、直播列表以及直播详情** 这三部分，每一个页面都扮演着不同的角色。在这个过程中，我们一定要考虑得非常全面，除了实现基础功能，还要尽量提升用户使用直播功能的体验。

在页面的实现过程中，你会发现我们应用到了很多Element组件来实现布局，例如通过Layout组件来完成页面适配，这能帮助我们告别冗杂的CSS编写，你也可以将其应用在其他任何页面上。

另外，我们又一次用到Element的其他组件来完成互动或展示的需求，加深了对这些组件的熟悉程度。善用组件不但能提高实现效率，还会让页面更美观。以后你遇到相关的样式呈现，就完全可以借助成熟的组件来实现。

最后我再提醒一下，这节课里我准备了大量代码，但直播模块的呈现方法并不唯一，你也可以发挥自己的想象做一些探索，毕竟自己动手能更快地提高你应用前端语言的能力。

完成了游客端的页面开发，我们又该如何实现直播的功能，下节课起我们就来探索这个问题，敬请期待。

## 思考题

在Layout组件中，如果我们不想使用<el-col>来实现空的内容占位，还有什么好的方式？

欢迎你在留言区和我交流互动，如果这节课对你有帮助，别忘了分享给身边的朋友。