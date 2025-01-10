你好，我是大圣。

跟随我的脚步，通过对前面数讲内容的学习，相信你现在对Vue+Vuex+vue-router都已经比较熟悉了。在开启课程后续的复杂项目之前，学会如何调试项目也是我们必须要掌握的一个技能。

在项目开发中，我们会碰到各种各样的问题，有样式错误、有不符合预期的代码报错、有前后端联调失败等问题。也因此，一个能全盘帮我们监控项目的方方面面，甚至在监控时，能精确到源码每一行的运行状态的调试工具，就显得非常有必要了。

而Chrome的开发者工具Devtools，就是Vue的调试工具中最好的选择。由于Chrome也公开了Devtools开发的规范，因而各大框架比如Vue和React，都会在Chrome Devtools的基础之上，开发自己框架的调试插件，这样就可以更方便地调试框架内部的代码。Vue Devtools就是Vue官方开发的一个基于Chrome浏览器的插件，作为调试工具，它可以帮助我们更好地调试Vuejs代码。

这节课，我会先为你讲解如何借助Chrome和VS Code搭建高效的开发环境，然后再教你使用Vue 的官方调试插件 Vue Devtools 来进行项目调试工作。

## Chrome调试工具

首先，我们来了解一下Chrome的调试工具，也就是Chrome的开发者工具Chrome DevTools。在Chrome浏览器中，我们打开任意一个页面，点击鼠标右键，再点击审查元素（检查），或者直接点击F12就可以看到调试窗口了。

![图片](https://static001.geekbang.org/resource/image/e2/25/e2d00f93dcbb2c960720b41c45479125.png?wh=1714x210)

我们看下截图中的调试窗口，里面有几个页面是我们经常用到的：Elements页面可以帮助我们调试页面的HTML和CSS；Console页面是我们用得最多的页面，它可以帮助我们调试JavaScript；Source页面可以帮助我们调试开发中的源码；Application页面可以帮助我们调试本地存储和一些浏览器服务，比如Cookie、Localstorage、通知等等。

Network页面在我们开发前后端交互接口的时候，可以让我们看到每个网络请求的状态和参数；Performance页面则用来调试网页性能。Lighthouse是Google官方开发的插件，用来获取网页性能报告，今天我也会教你用lighthouse评测一下极客时间官网首页的性能。

以上说的这些调试窗口中的页面，都是Chrome的开发者工具中自带的选项，而调试窗口最后面的Vue页面就是需要额外安装的Vue Devtools，也就是调试Vue必备的工具。

![图片](https://static001.geekbang.org/resource/image/e7/54/e756015dc2eb7a87d8825585115d4f54.png?wh=1920x1237)

上图所示的是项目开发中用到最多的页面，而在调试窗口右侧的工具栏中，你还可以选中More tools来开启更多自带的插件。如下图所示，More tools中的Animations用于调试动画，Security用于调试安全特性等等。

![图片](https://static001.geekbang.org/resource/image/bf/93/bfc45abbf1e20fb639bd712463ef7893.png?wh=1822x1082)

**下面，我们重点介绍一下调试窗口中的Elements页面和Console页面。这两个页面用来调试页面中的HTML+CSS+JavaScript，是使用频率最高的两个页面。**

在Elements页面中，首先映入眼帘的是开发的Vue项目在浏览器里的状态。调试窗口的左侧是正在调试的前端页面的HTML结构，当我们把鼠标放到HTML代码的任何元素上时，在调试的前端页面上，对应元素在前端页面中所在的位置都会高亮起来。

当我们点击一个元素之后，调试窗口右侧就会显示出当前元素所有的CSS样式，这对于我们开发的页面布局和样式调整非常有帮助。并且，我们还可以在Elements页面左侧的代码中，任意修改页面的HTML和CSS代码。

比如，以我在这里给出的调试页面为例，我们可以选中调试页面（清单应用）的div标签，再点击调试页面右侧的element.style，这样就可以直接新增background和padding属性，也即会得到下图的效果。此外，有一些页面布局上的bug可以用这种方式，在网页里实时调整后，再去更新代码。

![图片](https://static001.geekbang.org/resource/image/f6/0a/f6a378b2d723e92aaa1cea6cd0bc230a.png?wh=1920x1319)

然后，我们再来看一下在调试中用得最多的Console页面。在这个页面内，我们可以直接调试JavaScript，并且页面中也会显示JavaScript出现的报错信息。

举个小例子，我们来到项目里的src/main.js文件内，把createApp修改成createApp1，然后回到浏览器的Console调试页面，就会看到以下的报错内容，红色报错信息清晰地告诉我们代码执行出现错误的原因。

## ![图片](https://static001.geekbang.org/resource/image/d9/06/d91f1daa22cb0ac8063bccbbabb07606.png?wh=1920x298)

我们点击报错信息的最右侧，还能精确地定位到项目中的文件以及代码的行数。尤其是对于新手程序员来说，精确的报错定位可以极大地提高我们的开发效率。国外甚至有程序员还直接在报错信息里加上stackoverflow搜索地址，也算是把Console玩出花样了。

![图片](https://static001.geekbang.org/resource/image/36/0d/36fb0aed8ab2d3fe06f8f0ffac04b40d.png?wh=1208x1002)

参考我们提到的国外程序员的做法，我们在src/main.js里加入下面这段代码 ，这样就可以在日志信息中直接复制报错内容中的链接，去Stack Overflow中寻找答案。

```javascript
window.onerror = function(e){
    console.log(['https://stackoverflow.com/search?q=[js]+'+e])
}

```

其实Console页面的用法非常多，当我们在代码里使用cosole.log打印信息时，console页面里就会显示log传递的参数，这也是程序员用得最多的调试方法。

除了console.log，还有console.info、console.error等方法可以显示不同级别的报错信息。而在log之外，我们还可以使用console.table更便捷地打印数组消息。在MDN的 [Console页面](https://developer.mozilla.org/zh-CN/docs/Web/API/Console) 中，有对Console的全部API的介绍，你也可以去参考一下。

关于Console，后续的课程中还会持续地用到，我在这里还可以分享一个我喜欢用的前端面试题，题目来自贺老的面试题。那就是我会把电脑给面试者，让他在Console页面里写代码，统计极客时间官网一共有多少种HTML标签。

你也可以上手体验一下，打开极客时间的官网，再打开调试窗口，在Console页面输入下面的代码，你就可以看到答案。这其实是一个比较考验应试者前端基础的一道题，你可以自己试一试。

```javascript
new Set([...document.querySelectorAll('*')].map(n=>n.nodeName)).size

```

## Vue Devtools

然后，我们再来介绍一下调试窗口里最后面的Vue页面，这个页面其实就是我们在Chrome浏览器中安装的第三方的插件Vue Devtools。

首先我们要做的是安装一下Vue Devtools。Vue Devtools的官网上有详细的 [安装教程](https://devtools.vuejs.org/)，这里就不过多讲解了。安装完毕后，如果调试的前端页面中有Vue相关的代码，就会激活这个tab。进入到Vue这个调试页面后，你就会看到下面的示意图。

![图片](https://static001.geekbang.org/resource/image/9f/74/9fa65477f34ae77d75732629e22da274.png?wh=1920x1328)

从上面的图中你可以看到，Vue Devtools可以算是一个Elements页面的Vue定制版本，调试页面左侧的显示内容并不是HTML，而是Vue的组件嵌套关系。我们可以从中清晰地看到整个项目中最外层的App组件，也能看到App组件内部的RouterView下面的Todo组件。

并且，在调试页面的左侧中，当我们点击组件的时候，我们所调试的前端页面中也会高亮清单组件的覆盖范围。调试页面的右侧则显示着todo组件内部所有的数据和方法。我们可以清晰地看到setup配置下，有todos、animate、active等诸多变量，并且这些变量也是和页面实时同步的数据，我们在页面中输入新的清单后，可以看到active和all的数据也随之发生了变化。

同时，我们也可以直接修改调试窗口里面的数据，这样，正在调试的前端页面也会同步数据的显示效果。有了Vue的调试页面，当我们碰到页面中的数据和标签不同步的情况时，就可以很轻松地定位出是哪里出现了问题。

然后在Component的下拉框那里，我们还可以选择Vuex和Router页面，分别用来调试Vuex和vue-router。

![图片](https://static001.geekbang.org/resource/image/1f/f6/1f0d59f12fe3833148f92d4bee65cbf6.png?wh=1920x1024)

我们先来点击Vuex页面试一下， **这个页面里的操作可以帮助我们把Vuex的执行过程从黑盒变成一个白盒**。简单来说，我们可以在调试窗口的右侧看到Vuex内部所有的数据变化，包括state、getters等。

![图片](https://static001.geekbang.org/resource/image/66/1b/66e771b822ffa8bf9a3549e88060c71b.png?wh=1920x988)

我们点击Vuex下拉框里的Routes页面，这个页面里显示了整个应用路由的配置、匹配状态、参数等，这里就不做过多的解释了。相信有了Vue Devtools后，你能够更快地调试Vue项目的内部运行状态，从而极大地提高开发效率。

![图片](https://static001.geekbang.org/resource/image/fe/e6/fe8624dc482abff1257191c8a2a4e6e6.png?wh=1920x736)

这里还有一个小技巧，你可以了解一下：在Components页面下，你选中一个组件后，调试窗口的右侧就会出现4个小工具。

如下图所示，在我用红框标记的四个工具中，最右边的那个工具可以让你直接在编辑器里打开这个代码。这样，调试组件的时候就不用根据路径再去VS Code里搜索代码文件了，这算是一个非常好用的小功能。

![图片](https://static001.geekbang.org/resource/image/53/46/53b82ec4499c08b0b8403a8471070946.png?wh=1920x807)

## 断点调试

正常情况下，我们用好Elements、Console和Vue这三个页面就可以处理大部分的调试结果了。不过太多的Console信息会让页面显得非常臃肿，所以还出现过专门去掉Console代码的webpack插件。

如果代码逻辑比较复杂，过多的Console信息也会让我们难以调试。这种情况就需要使用断点调试的功能，Chrome的调试窗口会识别代码中的debugger关键字，并中断代码的执行。

还是通过小例子直观感受一下。我们打开src/components目录下的todo.vue文件，下面是清单应用的代码，我们在addTodo函数内的第一行写上debugger。然后到前端的清单应用的页面中，我们输入任意一条信息，点击回车，你就会发现页面暂停了，并且调试窗口跳转到了source页面。

```javascript
  function addTodo() {
    debugger
    if(!title.value){
      showModal.value = true
      setTimeout(()=>{
        showModal.value = false
      },1500)
      return
    }
    todos.value.push({
      title: title.value,
      done: false,
    });
    title.value = "";
}

```

上面的代码在调试窗口中的效果如下图所示，点击图中用红框圈出的按钮，你就可以在debugger暂停的地方，逐行执行代码。并且鼠标放在任意变量上，都可以看到这个变量在代码执行的结果。对于复杂代码逻辑的调试来说，使用断点调试，可以让整个代码执行过程清晰可见。 **debugger也是高级程序员必备的断点调试法，你一定要掌握**。

![图片](https://static001.geekbang.org/resource/image/3f/74/3f3e7fb01d09468cbd48d4f6de27d174.png?wh=1920x993)

## 性能相关的调试

了解了页面代码的调试方法后，我们再来分享一下页面的性能调试方法。比如，在你遇到页面交互略有卡顿的时候，你可以在调试窗口中点击Performance页面中的录制按钮，然后重复你卡顿的操作后，点击结束，就可以清晰看到你在和页面进行交互操作时，浏览器中性能的变化。

以极客时间的官网页面作为具体的例子，我们在调试窗口中点击Performance页面中的录制按钮，然后进行刷新页面的操作，并点击首页轮播图，之后我们可以看到如下的效果：

![图片](https://static001.geekbang.org/resource/image/34/6b/348d056766eaa0feba5ec5205f5e7e6b.png?wh=1920x1199)

我们可以滑动鼠标，这样就能很清晰地看到极客时间页面加载的过程。然后，我们重点看下首屏加载中的性能指标，通过下方的饼图，你可以看到整个刷新过程中耗时的比例，其中JS代码391ms，整体624ms。

![图片](https://static001.geekbang.org/resource/image/1c/ba/1c2892c22c3d9bde8f28559e0d0d6cba.png?wh=1262x598)

在Performace页面中，我们还可以详细地看到每个函数的执行时间。我们录制一下清单应用新增清单的操作之后，就会显示下面的示意图，从中可以清晰地看到键盘keydown事件之后执行的函数，在图中可以找到我们写的addTodo方法，以及mountElement等Vue源码里的函数。关于Chrome性能页面更多的使用方法 ，你可以到 [Chrome官方文档](https://developer.chrome.com/docs/devtools/evaluate-performance) 上去查看。

![图片](https://static001.geekbang.org/resource/image/cd/cf/cd14d601a7801de54b8a88ef754c38cf.png?wh=1920x943)

如果你觉得上面手动录制页面的性能报告的方法过于繁琐，还可以直接使用lighthouse插件。我们进入到lighthouse页面，选择desktop桌面版后，点击生成报告。lighthouse在浏览器上模拟刷新的操作后，给出一个网页评分。这里我们可以看到，极客时间网站首页的评分是72分，在合格的标准线上。

![图片](https://static001.geekbang.org/resource/image/3a/19/3ae311638a352a8e884764d6d3603e19.png?wh=1920x833)

此外，根据性能、可访问性、最佳实践、SEO和PWA五个维度的评分，我们可以看出，在前面四个维度中，极客时间都是及格的，第五个指标置灰，说明极客时间首页还没有支持PWA。

我们先看下性能指标，下图中详细地给出了FCP、TTI、LCP等常见性能指标，并且还很贴心地给出了建议，包括字体、图标宽高、DOM操作等等，其实我们按照这些建议依次修改，就可以实现对网页的性能优化了。并且网页优化后，性能分数的提升还可以很好地量化优化的结果。

![图片](https://static001.geekbang.org/resource/image/5e/01/5ec97d6bff48ab8ed6e9549d71506a01.png?wh=1920x1668)

关于极客时间首页lighthouse其余几个指标，你可以点开 [这个链接](https://pandafe.gitee.io/clock/time.geekbang.org.html) 查看结果，相信结合这个实例演示，你一定会对性能优化手段有所体会。

## 总结

好，今天这一讲的主要内容，也即调试Vue应用的方法，就讲完了，我们一起来回顾一下吧。

首先，我给你讲解了在Chrome浏览器中，进行项目调试的方法。除了最基本的Console，我们还可以借助Chrome提供的其他调试工具提高效率，例如元素面板、源码面板等等。每个面板都带来了透视Vue应用的方式，从样式到性能都是我们提高效率最高的工具。

Elements和Console页面可以完成页面的布局和JavaScript的调试工作，并且调试窗口还会识别代码中的debugger语句，可以让我们在Chrome中进行断点调试。Performance和lighthouse页面则提供了对页面做性能测试的方法，从而能帮助我们更好地查看页面中性能的指标。

然后，我们介绍了Vue团队开发的插件Vue Devtools，你可以把Vue Devtools理解为是对Chrome调试工具的一个扩展。 **在Vue Devtools中，我们可以很方便地调试Vue的应用，比如查看Vue的组件嵌套、查看Vue组件内部的data等属性**。

此外，当我们遇见页面中的数据和渲染结果不一致的bug时，我们可以很方便地使用Vue Devtools精确地定位问题，从而极大地提高了开发效率。并且Vue Devtools还支持了Vue和vue-router的调试页面，这让整个页面的Vuex数据和路由都清晰可见。

相信今天这一讲结束后，当你在开发应用时再遇到了bug，你就能通过调试工具快速地定位问题，并借助今天我们讲到的内容，顺利地解决掉bug。

## 思考题

Vue的Devtools操作比较简单，进阶的知识并不算多。在讲Console页面时，我分享了一个与Vue Devtools相关的常见的手写面试题，而今天的思考题就是这个面试题的升级版：如何在Console页面写一段代码，来统计极客时间首页出现次数最多的3种HTML标签呢？

欢迎在留言区分享你的答案，我们可以一起探讨高效调试Vue的新方法。也欢迎你把这一讲的内容分享给你周围的朋友、同事，我们下一讲见！