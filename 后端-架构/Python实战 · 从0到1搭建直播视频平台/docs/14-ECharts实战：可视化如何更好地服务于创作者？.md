你好，我是Barry。

上节课我们一起学习了数据中心的数据业务需求、数据采集逻辑和数据呈现效果。在数据分析呈现的时候，我们用到了很多数据可视化的组件，有了这些组件，就能让我们轻松地实现数据可视化，直观展示出我们想要的分析结果，而且能帮用户清晰地看到数据间的关系。

其实在我们实际项目开发中，数据可视化的应用是非常多的。因此，如何熟练应用数据可视化组件，也是我们在日常开发中的一项必备技能，这样会让我们技术栈更加完善。这节课，我们就一起来认识学习应用一款轻量级数据可视化组件库——ECharts。

## 认识ECharts

我们先来认识一下ECharts，ECharts是一款基于JavaScript的数据可视化图表库。ECharts由百度团队开源，在2018年初捐赠给Apache基金会，成为ASF孵化级项目。

2021年1月，Apache基金会宣布 ECharts项目正式成为Apache顶级项目。同样在2021年1月，ECharts 5正式发布上线，在这个过程中ECharts不断地更新迭代，满足用户对数据可视化的各类需求。

提到前端可视化图表库，热度最高、也最常用的两个库就是D3.js和ECharts了，我们在课程中使用的也是ECharts。那为什么不选D3.js呢？这里我们简单分析一下，也让你有一个全面的了解。

D3.js的全称是Data-Driven Documents，是一个数据驱动的JS图表库，不难看出，它是用一种偏函数式编程的方式来实现图表可视化的，整体使用起来非常灵活。可是，这样的优势对于初学者来说不太友好，学习成本较高，并且D3.js配置门槛也比较高（使用了SVG绘制图形，只能兼容IE9及以上浏览器）。

ECharts则有所不同，ECharts使用Canvas来绘制图形，兼容IE6及以上浏览器。因为ECharts是直接封装好的，所以我们只需根据自己的需求，更改相关配置项就可以轻松实现数据可视化。这对新手非常友好，而且ECharts整个生态建设得非常完整，组件库资源相当丰富。

分析完D3.js和ECharts的优缺点，为了让你更容易上手，并且能够契合更多的可视化场景，我们视频平台里的可视化部分都会采用ECharts来实现。

![](https://static001.geekbang.org/resource/image/cd/e5/cd6ff2aa2617b42097eef7b6706f1de5.jpg?wh=2866x1620)

接下来我们看看ECharts有哪些特性吧！以下内容参考 [ECharts官网](https://echarts.apache.org/zh/index.html)。这里我帮你提炼了核心内容，方便你快速抓住重点。

![](https://static001.geekbang.org/resource/image/61/3d/612d37fc9b468ca5346c15d5d7ec253d.jpg?wh=3628x2260)

通过前面这张表，我们全面了解了ECharts的特性，也看到了它能够呈现的图表样式，能够满足非常多的数据可视化场景。接下来，我们就通过官网这个最直接的学习渠道来学习应用ECharts。

## ECharts学习应用指南

虽然官网上ECharts整体内容比较多，但是我帮你梳理过后，你就会知道怎样学习才会更加系统高效了。

![](https://static001.geekbang.org/resource/image/3d/de/3dd13d2f29cc1bb62b5d81a9c96464de.jpg?wh=2784x1118)

最重要的就是使用手册、API、配置项手册这三项，建议你课后再仔细阅读一下。其中使用频率比较高的就是配置项手册，因为在ECharts实现的过程中，配置项设置这一步必不可少，所以我们必须要对常见配置的作用心中有数。

不过，你不必把这么多配置项全部记清楚，可以在实操过程中把配置手册当字典库来使用。

比方说，我们想实现一个简单的折线图，这时候我们在示例中找一个案例，就可以直接拿过来使用。

我们来看看具体的应用流程。首先一进入示例库，我们就能看到非常多的案例，我们只需点击想要的案例，进入编辑页面，就可以直接去修改相关的数据和配置项，并且看到相应的展示效果。

![图片](https://static001.geekbang.org/resource/image/fe/2e/fe60d723386aba938db34c7b53a2412e.png?wh=1920x982)

这里我们选取第一个折线图的案例，进入编辑页面。在界面的左侧是具体的实现代码，参考代码我们很容易分析出xAxis和yAxis的意思，它们分别代表了X轴和Y轴。

那么 type: ‘category’ 是什么用途呢？

![](https://static001.geekbang.org/resource/image/73/ae/73016c4491c856080f29fb9fbd7355ae.jpg?wh=2834x1548)

这时候配置项手册就能派上用场了。我们找到手册搜索 “category”，就能明确它的功能和含义了，就像后面截图展示的这样。

![](https://static001.geekbang.org/resource/image/5e/56/5ebe2be37b739dbaa9bbaae3e6facc56.jpg?wh=2554x1398)

当然这只是开胃菜，重点是你在应用时养成良好的学习方式，在不断发现问题和解决问题的过程中熟悉ECharts的基础用法。如果你追求更酷炫的效果，即便你前期对ECharts还不太熟练，也不妨多看看各类案例，比较一下它们的功能和呈现样式，上手多感受一下，这样你的学习效果会更好。

接下来我们来做一个简单的案例来看一下，在HTML中，我们该如何使用ECharts完成一个可视化呈现案例。

我们先来看一下最终呈现的效果，然后再一起完成从0到1的实现过程。

![](https://static001.geekbang.org/resource/image/1a/43/1a9d12bdfb8c2b1b1e4013bfbeed5043.jpg?wh=2862x1534)

我帮你系统梳理了日常使用率非常高的配置项，你可以参考后面的表格。

![](https://static001.geekbang.org/resource/image/bf/bd/bf49a9df2e0yy949b6db1867793537bd.jpg?wh=3878x3535)

当然，就像前面我说的那样，表里的内容你没必要全部记住，这些属性你可以直接在配置项手册里找到详细介绍。

好，让我们继续来看看如何在HTML里，把这段代码实现出来。我们先来看看整体的代码。

```plain
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>小试牛刀</title>
    <!-- 引入 echarts.js，这一部分必须要引入才可以使用 -->
    <script src="https://cdn.staticfile.org/echarts/4.3.0/echarts.min.js"></script>
</head>
<body>
    <!-- 为ECharts准备一个Dom，这一个也是必须的，同时需要声明ID -->
    <div id="first"></div>
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var firstChart = echarts.init(document.getElementById('first'));

        // 指定图表的配置项和数据
        var option = {
            title: {
                text: '一起来测试一个案例'
              },
              tooltip: {
                trigger: 'axis'
              },
              legend: {
                data: ['第一组', '第二组', '第三组', '第四组', '第五组']
              },
            grid: {
              left: '3%',
              right: '4%',
              bottom: '3%',
              containLabel: true
            },
            toolbox: {
              feature: {
                saveAsImage: {}
              }
            },
            xAxis: {
              type: 'category',
              boundaryGap: false,
              data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            yAxis: {
              type: 'value'
            },
            series: [
            {
              name: '第一组',
              type: 'line',
              stack: 'Total',
              data: [120, 132, 101, 134, 90, 230, 210]
            },
            {
              name: '第二组',
              type: 'line',
              stack: 'Total',
              data: [220, 182, 191, 234, 290, 330, 310]
            },
            {
              name: '第三组',
              type: 'line',
              stack: 'Total',
              data: [150, 232, 201, 154, 190, 330, 410]
            },
            {
              name: '第四组',
              type: 'line',
              stack: 'Total',
              data: [320, 332, 301, 334, 390, 330, 320]
            },
            {
              name: '第五组',
              type: 'line',
              stack: 'Total',
              data: [820, 932, 901, 934, 1290, 1330, 1320]
            }
          ]
        };

        // 使用刚指定的配置项和数据显示图表。
        firstChart.setOption(option);
    </script>
</body>
</html>

```

配合代码里的详细注释，相信你有能力看懂这个过程。我们首先需要有一个<div>标签来做图表的占位。而JS中的option是图表的相关配置项，通过配置手册我们就能明确它的含义。其中series里放的是图表最终呈现的数据，通过它我们就完成了图表的填充渲染。

配置项和图表类型还可以灵活切换，建议你上手尝试一下，掌握了应用方法以后，我相信在HTML中实现ECharts就是一件非常轻松的事情了。

## ECharts+Vue项目实战

接下来我们进一步升级，应用ECharts来实现数据中心里的数据可视化工作。我们一起来看看，如何在项目中使用ECharts，如何把ECharts与Vue结合起来，最终实现可视化效果。

首先，我们需要在项目文件目录下使用命令行安装ECharts，具体执行命令如下。

```plain
npm install echarts --save

```

完成安装之后，我们还要 **在main.js文件下进行注册和实例挂载**，这是因为所有全局要使用的组件都需要 **在Vue中全局引用**。

```plain
//main.js
import echarts from 'echarts'
Vue.prototype.$echarts = echarts //挂载在Vue原型上

```

注册挂载之后，我们就可以在项目内的各个页面组件中使用ECharts了。

这里还是结合案例来体验，比方说我们期望展示一个直播数据，要怎么实现呢？

我们需要在HTML的代码中先定义好，这里的id是ECharts块级容器id，在渲染的过程中需要根据id来加载和渲染dom。具体的代码编写是后面这样。

```plain
 <div class="chart_wrapper" id="video_sum"></div>

```

这里我想请你暂停思考一下，整个的ECharts的渲染应该放在Created阶段，还是放在Mounted阶段呢？

其实放哪个阶段区别都不大。但我想提醒你注意的是，因为ECharts渲染的过程中需要数据的填充，所以我们一定要在渲染前就请求获取到数据，这样才能顺利展示图表。为了避免一些展示上的错误，我推荐的做法是—— **把ECharts的数据请求放在Created方法内，然后把渲染放在Mounted钩子函数里。**

我们这就来模拟一下具体的实现。

```plain
created() {
  this.getLineData() //获取数据的接口
}
mounted(){
  this.showLine() //ECharts渲染的方法
}

methods: {
  //请求数据的方法
  getLineData() {
    this.$axios({
      method: "请求方法",
      url: "接口地址",
      params: {传递参数}
    }).then(res => {
      // res是接口请求返回的JSON数据，其中包括code值，代表接口的状态
      //200 代表请求成功
     if (res.code === 200) {
        this.x_data = res.data.counts_x_data;
        this.y_data = res.data.counts_y_data;
      } else {
        //这个是消息组件
        //type表示消息类型，warning错误警告
        //message是展示信息。
        this.$message({
          message: "获取数据失败",
          type: "warning"
        });
      }
    });

    //渲染ECharts视图的方法
    showLine() {
      //以下就是就是ECharts的配置项
      let option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow"
          },
          formatter: "{b} : 在线{c}人"
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "10%",
          containLabel: true
        },
        //X轴的值
        xAxis: {
          type: "category",
          data: this.x_data
        },
        //Y轴的值
        yAxis: {
          type: "value",
          axisLabel: {
            formatter: "{value} 人"
          }
        },
        series: [
          {
            data: this.y_data,
            type: "bar"
          }
        ]
      };
      //ECharts渲染的过程
      let myChart = this.$echarts.init(document.getElementById("video_sum"));
      myChart.setOption(option);
      //ECharts 多图表自适应窗口大小，ECharts随页面大小变化而变化,用到resize()方法
      window.addEventListener("resize", function() {
        myChart.resize();
      });
    },

}

```

后面这张图就是绘制视图的效果。

![](https://static001.geekbang.org/resource/image/b7/ae/b7c372277094e330c1a6b43fd8a305ae.jpg?wh=1990x1568)

这样我们就轻松完成了视图的呈现，是不是非常简单呢？

当然还有一种方法，我们把获取数据的方法直接写在Mounted中，然后在数据获取成功之后再来渲染视图，这么做也没有问题，后面是代码实例。

```plain
mounted(){
  this.getLineData() //数据请求方法
}
methods: {
  //请求数据的方法
  getLineData() {
    this.$axios({
      method: "请求方法",
      url: "接口地址",
      params: {传递参数}
    }).then(res => {
      // res是接口请求返回的JSON数据，其中包括code值，代表接口的状态
      //200 代表请求成功
     if (res.code === 200) {
        this.x_data = res.data.counts_x_data;
        this.y_data = res.data.counts_y_data;
        //这里直接放视图渲染的方法
        this.showLine()
      } else {
        //这个是消息组件
        //type表示消息类型，warning错误警告
        //message是展示信息。
        this.$message({
          message: "获取数据失败",
          type: "warning"
        });
      }
    });

    //渲染ECharts视图的方法
    showLine() {
      //以下就是就是ECharts的配置项
      let option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow"
          },
          formatter: "{b} : 在线{c}人"
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "10%",
          containLabel: true
        },
        //X轴的值
        xAxis: {
          type: "category",
          data: this.x_data
        },
        //Y轴的值
        yAxis: {
          type: "value",
          axisLabel: {
            formatter: "{value} 人"
          }
        },
        series: [
          {
            data: this.y_data,
            type: "bar"
          }
        ]
      };
      //ECharts渲染的过程
      let myChart = this.$echarts.init(document.getElementById("video_sum"));
      myChart.setOption(option);
      //ECharts 多图表自适应窗口大小，ECharts随页面大小变化而变化,用到resize()方法
      window.addEventListener("resize", function() {
        myChart.resize();
      });
    }

}

```

代码实战环节，我建议你亲自上手感受一下。相信你在掌握了ECharts的各类配置项属性和应用方法以后，就可以轻松应用ECharts来实现各类的可视化图像呈现需求。

## 总结

今天的内容告一段落，我们一起来回顾一下这节课的核心知识点。

ECharts是一款对新手非常友好的数据可视化组件库。我帮你梳理了高效学习ECharts的方法以及官方文档里我们要重点关注的内容，并且带你通过案例应用加深了体会。

我们还一起练习了在HTML中如何使用ECharts。重点需要关注的就是JS的引入、元素的定义，以及具体配置项的使用。

之后我们进一步升级，结合项目演练了ECharts从安装到项目里的全局引入、再到实际案例的应用。你可以借鉴课程里的方式探索不同的可视化案例，来实现各种各样的功能开发。在数据中心开发实现上，后期你只需通过后端接口请求获取到对应的图表数据，图表就自然而然地实现了。希望你可以在持续练习中逐渐熟悉ECharts，灵活应对更多项目可视化的需求。

## 思考题

如何实现一个图表在多个页面中使用？这里不建议每一个页面都写一次代码，这样会有大量的代码量。

欢迎你在留言区和我交流互动，也推荐你把这节课分享给更多有需要的朋友。