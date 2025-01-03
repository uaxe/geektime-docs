你好，我是Barry。

今天是一节答疑课。课程更新到现在，很开心你的一路支持。很多同学也在留言区记录了自己的学习收获和自己对于思考题的解答。

其实设置思考题，就是为了帮助同学们检验和巩固自己的学习成果。这次我把前面十几节课的参考答案公布出来，供你作为参考。这里我要提醒一下，建议你先自己思考和练习后，再来对答案，这样的学习效果会更好一些。每节课我都准备了超链接，方便你跳转回顾。

## [第一节课](https://time.geekbang.org/column/article/652102)

你知道Python内置函数split和replace有什么区别吗？

Python replace() 方法起到了替换功能，把字符串中的 old（旧字符串）替换成 new（新字符串），如果指定第三个参数max，则替换不超过 max 次。具体使用方法如下。

```plain
str.replace(old, new[, max])

```

Python **split()** 通过指定分隔符对字符串进行切片，如果参数 num 有指定值，则分隔 num+1 个子字符串。

```plain
str.split(str="", num=string.count(str)).

```

- str：分隔符，默认为所有的空字符，包括空格、换行(\\n)、制表符(\\t)等。
- num：分割次数。默认为 -1，即分隔所有。

replace主要用于解决替换需求，split主要用于字符串切片，而且两者在参数含义上也存在很大的区别。

## [第二节课](https://time.geekbang.org/column/article/652736?)

请你使用Matploylib画一个饼状图，巩固一下对Matploylib的认识。

你可以参考后面这个例子，我们用饼状图呈现出了一个班级的学生对不同球类运动兴趣偏好的分布情况。

```python
import matplotlib.pyplot as plt
import numpy as np
#添加图形对象
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
#使得X/Y轴的间距相等
ax.axis('equal')
#准备数据
langs = ['football', 'tennis', 'basketball', 'ping-pong', 'volleyball']
students = [20,18,35,22,5]
#绘制饼状图
ax.pie(students, labels = langs,autopct='%1.2f%%')
plt.show()

```

![](https://static001.geekbang.org/resource/image/2b/81/2bfe7d987d2a8cb4aca0a61ed294ee81.jpg?wh=1186x789)

## [第三节课](https://time.geekbang.org/column/article/653426)

后面是一段HTML代码，呈现的内容就是有p标签的“变化前- 1”，还有一个按钮写着“文本变换”，点击网页上的按钮，让p标签里的文字变成“变化后-2”，这里就是让你再次应用一下JS动效，快来试试吧！

```css
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>动效小测试</title>
</head>
<body>
<p>变化前-1</p>
<button>文本变换</button>
</body>
</html>

```

这道题目属于代码实操类题目。参考代码如下。很多同学留言的实现我也看到了，做得也非常不错。

```css
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>动效小测试</title>
</head>
<body>
<p>变换前-1</p>
<button onclick="changetext(this)">文本变换</button>

</body>
<script>
function changetext(id){
	id.innerHTML="变换后-2";
}
</script>
</html>

```

## [第四节课](https://time.geekbang.org/column/article/653986)

Vue采用了MVVM架构思想的框架，你知道什么是MVVM吗？

MVVM 是 Vue 实现数据驱动视图和双向数据绑定的核心原理。MVVM指的是 Model、 View 和 ViewModel，它把每个 HTML 页面都拆分成了三个部分。

![](https://static001.geekbang.org/resource/image/37/51/372151b69ec407ca3cdb6fe117413751.jpg?wh=1361x925)

- Model 表示当前页面渲染时所依赖的数据源。
- View 表示当前页面所渲染的 DOM 结构。
- ViewModel 表示 Vue 的实例，它是 MVVM 的核心。

MVVM采用双向数据绑定，View中的数据变化将自动反映到ViewModel上。反之，Dodel中的数据变化也会自动展示在页面上。把Model和View关联起来的就是ViewModel。ViewModel负责把Model的数据同步到View并显示出来，还负责把View的修改同步回Model。

MVVM的核心思想是关注Model的变化，让MVVM框架利用自己的机制自动更新DOM，也就是所谓的数据-视图分离，数据不会影响视图。

## [第六节课](https://time.geekbang.org/column/article/654616)

如果在我们平台中有一些公共的展示内容，例如平台的Icon，在每一个页面都可以看到它，并且点击可以跳回首页，你有什么好的想法呢？

我们可以直接把它放在App.vue文件（这是一个公共文件）中，另一种方法是可以通过路由跳转来控制。

## [第七节课](https://time.geekbang.org/column/article/655607)

这节课我们在Vue框架中整合了Vue Router，整合其他依赖也是同样的道理。你可以尝试整合一下Vue常用的UI组件库Element-UI。

提示： [Element-UI官网](https://element.eleme.io/#/)

main.js代码如下。

```javascript
import Vue from 'vue';
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import App from './App.vue';
Vue.use(ElementUI);
new Vue({
  el: '#app',
  render: h => h(App)
});

```

## [第八节课](https://time.geekbang.org/column/article/656369)

我们在处理菜单权限控制的时候，选择的方法是根据 access 权限参数来控制对应的展示内容。如果想应对更复杂的角色情况，还有什么更好的解决方法呢？

我们可以通过对menuList中特殊的菜单栏绑定新的参数，可以针对不同的情况实现，例如下面的代码。为了应对更多复杂情况，我们给对应的菜单级加入新的标识参数hidden，通过access+hidden的组合参数来形成权限判定。

```plain
{
        path: '/course',
        icon: 'funnel',
        title: '课程管理',
        name: 'course',
        header: 0,
        access: 1, //权限参数
        hidden：2, // 加入多个唯一标识从而解决复杂条件的情况,以此类推
        component: Main,
        children: [
            {
                path: 'course',
                icon: 'battery-charging',
                name: 'course',
                title: '课程列表',
                component: resolve => { require(['@/views/myView/course/courselist.vue'], resolve); }
            }
        ]
    }

```

## [第九节课](https://time.geekbang.org/column/article/656997)

尝试用 Element-UI 来实现一个 tab 可以切换的标签页，效果是点击不同的标签能够显示不同的内容。

参考代码如下。

```css
<template>
  <el-tabs v-model="activeName" @tab-click="handleClick">
    <el-tab-pane label="用户管理" name="first">用户管理</el-tab-pane>
    <el-tab-pane label="配置管理" name="second">配置管理</el-tab-pane>
    <el-tab-pane label="角色管理" name="third">角色管理</el-tab-pane>
    <el-tab-pane label="定时任务补偿" name="fourth">定时任务补偿</el-tab-pane>
  </el-tabs>
</template>
<script>
  export default {
    data() {
      return {
        activeName: 'second'
      };
    },
    methods: {
      handleClick(tab, event) {
        console.log(tab, event);
      }
    }
  };
</script>

```

## [第十节课](https://time.geekbang.org/column/article/658229)

我们一起来讨论一下，关于用户个人中心的“我的点赞”和“我的收藏”视频列表，是否有必要做分页？

这个可以分情况讨论，如果不太大的话，比如50以内的数量其实没必要分页展示，反而整个页面呈现出来对用户的体验更好，不需要来回切换。

但是如果量级特别大，例如快到100了，那这个需要滑非常久，这个体验就不太好，所以建议通过分页的方式来进行内容呈现管理，体验更佳。

## [第十一节课](https://time.geekbang.org/column/article/658963)

如果我们想要在用户点击视频暂停的时候，弹出一个弹窗，你有什么好的实现方法？

我们可以通过视频播放器的暂停钩子函数来触发Element-ui的弹窗组件，这个题目的核心是你会应用播放器的内置方法来实现。

## [第十二节课](https://time.geekbang.org/column/article/659854)

如果想在表单中el-input组件中实现输入数字的验证功能，你有什么好办法？

在表单验证rules中，对应的prop值加上后面的内容。

```plain
{ type: 'number', message: '输入内容必须为数字值'}

```

## [第十三节课](https://time.geekbang.org/column/article/660706)

除了课程里提到的四个维度的数据，你觉得数据中心里还有必要新增哪些维度的数据？

这个是一个活命题，没有固定答案，只要是有助于用户数据检测的维度、最终服务于优化用户视频质量的思路都是可取的。比如后面这几个维度。

1. 稿件播放完成率对比
2. 粉丝的兴趣分布
3. 粉丝地区分布等等

## [第十四节课](https://time.geekbang.org/column/article/661435)

如何实现一个图表在多个页面中使用？这里不建议每一个页面都写一次代码，这样会有大量的代码量。

可以采用组件封装的形式来实现，我们把共用的这个图表作为一个子组件，对于不同页面的实现需求，我们分别传入不同的data值，实现数据效果的展示就可以，这样只需要写一次代码，就可以实现多处复用。

## [第十五节课](https://time.geekbang.org/column/article/662105?)

在Layout组件中，如果我们不想使用来实现空的内容占位，还有什么好的方式？

可以直接利用Layout的offset属性来实现占位，它的作用是实现栅格左侧的间隔格数，直接完成占位。

## [第十六节课](https://time.geekbang.org/column/article/662742)

直播中心应用中我们一起实现了申请中心，你可以尝试模拟实现一下直播间信息的配置。请你思考一下需要用户提交哪些信息呢？页面又该怎样实现呢？

这是一道开放题，通常包含频道名称、频道类型、频道描述或直播描述、上传直播间的封面。通过表单的形式提交即可。

## [第十七节课](https://time.geekbang.org/column/article/663146)

在 Webpack 中，loader 中 test 选项用于匹配需要被处理的文件。你知道它是通过什么样的方式进行文件类型匹配的吗？

test主要应用的是正则进行文件类型的匹配。例如后面这个表达式。

```plain
test: /\.vue$/

```

$符号表示匹配字符串的末尾，即以.vue结尾的字符串。因此，该正则表达式会匹配所有以.vue结尾的文件。

好，这次的答疑加餐就到这里。如果有什么疑问，也欢迎你继续通过留言区和我交流。