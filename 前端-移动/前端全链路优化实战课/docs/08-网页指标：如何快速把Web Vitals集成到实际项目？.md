你好，我是三桥。

这节课，我将为你介绍实现前端全链路指标数据的第一步，把Web Vitals集成到你的项目。

我们先了解一下前端项目的现状。

近年来，前端开发者从0到1开发新项目，技术选型这方面基本上会将Vue和React作为前端开发首选框架之一，因为它们的模块化开发模式能让我们方便、快速地引入第三方框架或库，为开发更复杂的功能提供强大的后盾。

实际上，前端工程师需要负责的项目并不仅仅局限于Vue和React这两种框架，有些公司还在维护着最传统的旧前端系统，他们仍然使用着古老的技术栈，例如JSP、ASP、PHP以及jQuery等。

那在这种环境下，前端同学应该如何把Web Vital的网页指标应用到不同架构的前端项目上，并实现全链路的分析和体验优化呢？这是一个很有趣的题目。

## 使用Web Vitals的第一步

Web Vitals网页指标是由Google提出的。Google还开发了一套前端SDK，方便前端同学直接通过函数获取网页指标数据。

通常，想要前端项目中使用第三方库可以通过NPM安装依赖或者script链接引入的方式实现。而Web Vitals库正好可以支持这两种方式。

如果前端项目是通过NPM安装依赖，比如Vue或React项目，就可以直接使用npm、yarn或pnpm安装命令来安装Web Vitals。

```shell
// 使用npm
npm install web-vitals
// 使用yarn
yarn add web-vitals
// 使用pnpm
pnpm add web-vitals

```

第二种使用第三方库的方法是通过传统的 `script` 标签引入一个JS文件。对于不支持NPM安装依赖的前端项目来说，这就是最佳的引入方式。

然而，通过 `script` 标签引入的Web Vitals不能实现组件化中的import导入，只能通过window.webVitals对象来读取网页指标数据。

下面是引入外部链接web-vitals.iife.js的代码。

```xml
<script>
  (function () {
    var script = document.createElement('script');
    script.src = 'https://unpkg.com/web-vitals@3/dist/web-vitals.iife.js';
    script.onload = function () {
      window.webVitals.onCLS(console.log);
      window.webVitals.onFID(console.log);
      window.webVitals.onLCP(console.log);
    };
    document.head.appendChild(script);
  })();
</script>

```

上面的代码里有一点需要注意，就是例子中使用的是unpkg.com站点的链接。由于这个站点归属于海外服务商，所以如果你的业务只有国内用户，那还是不建议你直接拿来使用。

通常的做法是把这个链接的JS文件下载本地，然后放到国内已备案的站点上。目前有两种方法可以让你把它托管到任意地方。

1. 存放在你公司业务的服务器上，通过Web服务器提供可访问的链接。
2. 托管在公网提供的静态资源服务上，例如阿里云OSS，腾讯云的COS。

无论用哪一种方法部署Javascript文件，我们的目的都是确保前端页面能稳定地加载JS文件，从而保证全链路监控数据的完整性。

## 如何获取网页指标

现在，我们来学习下如何在项目中使用Web Vitals库以及怎么获取网页指标。

我们以NPM导入作为例子，看下怎么在Vue项目里使用它。下面是简单的代码示例。

```xml
<!-- Vue Project -->
<!-- web-vitals.vue -->
<template>
<!-- 在这里不展示内容 -->
</template>

<script>
import { onLCP } from "web-vitals";
export default {
  mounted(){
    onLCP(console.log);
  }
};
</script>
<style>
</style>

```

这里我们用的是通过import引入onLCP的方法，并在mounted生命周期内调用。由于onLCP是一个异步函数，是通过参数回调的，所以运行过程中不会阻塞mounted事件。

同理，React项目也可以通过import引入Web Vitals，你可以参考下面的代码。

```javascript
// React Project
// app.js
import { useEffect } from 'react';
import { onFCP } from "web-vitals";

function App() {

  const onVital = (vital) => {
    console.log(vital);
  }

  useEffect(() => {
    onFCP(onVital);
  }, [])

  return (
    <div className="App">
    </div>
  );
}

export default App;

```

这里非常简单，只需通过import导出onLCP方法，然后调用它，就可以获取到LCP网页指标数据了。

不过，在上面的示例代码里，我们只介绍了如何使用onFCP函数。Web Vitals库一共支持获取6种网页指标的方法，其余5种方法分别是onCLS、onFID、onINP、onLCP和onTTFB。Web Vitals库在设计时考虑到自己提供的功能，为每个指标分别提供了一个方法，通过调用这些方法就可以计算出每个指标的数据了。

我们再讨论下这个onXXX方法。它提供了两个参数，一个是回调函数，另一个是指标报告参数。参考下面代码的类型结构定义。

```typescript
// onCls Function Type
type onCLS = (callback: CLSReportCallback, opts?: ReportOpts) => void;

// onFCP Function Type
type onFCP = (callback: FCPReportCallback, opts?: ReportOpts) => void;

// onFID Function Type
type onFID = (callback: FIDReportCallback, opts?: ReportOpts) => void;

// onINP Function Type
type onINP = (callback: INPReportCallback, opts?: ReportOpts) => void;

// onLCP Function Type
type onLCP = (callback: LCPReportCallback, opts?: ReportOpts) => void;

// onTTFB Function Type
type onTTFB = (callback: TTFBReportCallback, opts?: ReportOpts) => void;

```

由于第一个参数是一个回调函数，所以我们可以传入console.log，也可以传入自定义的函数。而onXXX函数在计算出网页指标值后，会把数据传入这个回调函数，提供给外层业务使用。

至于第二个参数，它是可选的，参数类型是ReportOpts。它提供了两个参数属性。

- `reportAllChanges`：这是一个布尔值类型参数，用于设置当初始值或页面生命周期内发生变更时，判断是否会调用回调函数。
- `durationThreshold`：这个参数的作用是调整指标报告的阈值。默认情况下，它有一个默认阈值，当然，你也可以通过修改这个参数来调整指标阈值。

## 如何集成到公共全链路数据指标？

现在我们已经学会了使用Web Vitals获取网页指标的方法，但这需要通过编写代码来实现页面指标的计算和读取。那有没有更好的方法可以自动收集并存储到我们设计的数据指标里呢？

还记得我们在前面的课程中学习设计数据指标时，专门设计了一个性能字段perf来存储网页指标吗？

最少字段原则是全链路数据指标的设计原则，设计perf字段的主要目的就是通过网页指标值来提前发现性能问题。

因此，我们只需记录每个网页指标的两个数据，就是指标值和指标衡量值，这样就可以知道页面的性能状况了。

那么我们应该如何实现Web Vitals和全链路指标的整合呢？

首先，我们先来实现onXXX的回调函数，通过回调函数获取到指标值，代码参考如下。

```typescript
// src/typings/typing.d.ts
type TracePerfRating = 'good' | 'needs improvement' | 'poor'

type TracePerf = {
    id: string
    LCP?: number
    LCPRating?: TracePerfRating
    FID?: number
    FIDRating?: TracePerfRating
    FCP?: number
    FCPRating?: TracePerfRating
    TTFB?: number
    TTFBRating?: TracePerfRating
    CLS?: number
    CLSRating?: TracePerfRating
    INP?: number
    INPRating?: TracePerfRating
}

// src/baseTrace.ts
export class BaseTrace implements BaseTraceInterface {

	// 性能日志数据
  public perfData: TracePerf = {
    id: ''
  }

	createPerfReport() {
	  const report = (metric) => {
	    this.perfData = { ...this.perfData, ...mapMetric(metric) };
	  };
	  return report
	}
}

```

在上述代码中，我们在BaseTrace类中定义了perfData公共属性，用于存储当前页面的网页指标数据。

此外，BaseTrace类新增了createPerfReport函数，并返回了一个名为report的内部函数。report函数是提供给onXXX的回调函数，用来获取指标值的。

我们还看到了mapMetric函数，它的主要作用是通过获取到的指标数据，重新构造出我们想要的数据，同时返回给perfData。

以下是mapMetric函数的实现代码参考。

```typescript
// src/core/webvitals.ts

export function mapMetric(metric) {
  const isWebVital = ['FCP', 'TTFB', 'LCP', 'CLS', 'FID'].indexOf(metric.name) !== -1;
  return {
    [metric.name]: isWebVital ? round(metric.value, metric.name === 'CLS' ? 4 : 0) : metric.value,
    [`${metric.name}Rating`]: metric.rating
  }
};

```

一切准备就绪后，我们就可以在初始化时自动监听网页指标的计算结果了。

具体的实现方法分为两部分。第一部分是实现新函数onVitals，并调用6个指标方法，第二部分是在初始化SDK时，执行onVitals函数。

```typescript
// src/core/webvitals.ts
export const onVitals = (saveMetric) => {
  onLCP(saveMetric)
  onFID(saveMetric)
  onCLS(saveMetric)
  onTTFB(saveMetric)
  onINP(saveMetric)
  onFCP(saveMetric)
}

```

第二部分是增加链路SDK的初始化以及执行onVitals，代码如下。

```typescript
// src/baseTrace.ts
import { onVitals } from './core/webvitals';

export class BaseTrace implements BaseTraceInterface {
	// 初始化实例
  public static init(options: TraceOptions): BaseTrace {
    const traceSdk = new BaseTrace(options)

    // 监听页面性能
    onVitals(traceSdk.createPerfReport())

    window.traceSdk = traceSdk
    return traceSdk
  }
}

```

每次页面加载后，只需执行BaseTrace.init方法，就能够初始化监听6个网页指标情况了，然后根据计算出来的指标值回调给BaseTrace的内部函数，并将需要记录的指标值存储起来就好了。

通过以上的实现，我们成功把Web Vitals库整合到了前端全链路SDK的实现逻辑里。虽然这里的实现只是介绍了存储网页指标的方法，但并没有提到何时报告数据以及怎么上报。关于这部分的内容，我们将在后面的课程中详细学习。

## **Web Vitals库的局限性**

最后，我们来谈谈Web Vitals官方JS库的局限性。它的版本目前还在不断更新迭代。因此，无论是指标的计算公式、还是指标的衡量标准，在未来都有可能变化。

另外，由于市场上浏览器的差异性，例如Google、微软、Apple都有各自不同的浏览器内核，对于Web Vitals的支持也存在较大差异。所以，Web Vitals库提供的所有指标，并不是在每个浏览器环境下都支持的。

基于Chromuim（Google的开源内核）内核的浏览器，例如谷歌Chrome，它对Web Vitals的支持更加完善。其余类似Firefox或Safari，则要根据用户使用的版本才能判断是否支持Web Vitals。对于这一点的差异，前端开发者需要关注浏览器的兼容问题。

而基于移动端应用的前端网页，大部分都是安卓系统，而且它的浏览器内核也是基于Chromuim的架构。所以，在业务上对于我们使用Web Vitals库来说，收集用户体验指标数据的影响不大。

我认为，不管浏览器的差异性如何，我们的用户通常都是来自不同设备上的浏览器，肯定至少有一款浏览器能支持Web Vitals的特性。对于前端同学来说，只要能捕获到这些数据，无论收集数据的比例如何，只要能发现问题、解决问题，这些都不是问题。

分享一个很有趣的研发沟通话术，研发接收到一些用户反馈问题的时候，都会抛出这类话术：这个用户的问题是怎么重现的？麻烦提供一下重现路径？我在后台看下数据是否可以找到Bug？

因此，只要有数据，有重现路径，解决问题无需1天或3天，半分钟就能重现问题，5分钟内解决。

## 总结

这节课我们学习了把Web Vitals集成到前端全链路的方法。

我选用的是Vue和React这两个技术栈，通过NPM的方式引入Web Vitals的函数。另外，如果我们遇到使用旧技术栈的前端项目，也可以采用script引入链接的方式使用Web Vitals。

引入Web Vitals后，我们有6种onXXX方法获取到网页指标值，例如获取FCP指标值的onFCP方法，还有onCLS、onFID等等。

我们还完成了将Web Vitals库和全链路指标整合的实现方案。首先，我们要定义一个存储当前页面网页指标数据的属性perfData，接着，实现一个回调函数report，用来获取指标值。同时，还需要设计一个函数mapMetric来处理获取到的指标数据，并返回给需要记录的指标值。

最后，我们也讨论了Web Vitals的局限性，包括未来可能发生的变化以及浏览器的兼容性问题。尽管Web Vitals在计算公式、衡量标准、浏览器兼容问题以及未来的变化都存在不确定性，但是这些并不妨碍我们通过它发现网页性能问题。

## 思考题

今天我介绍了将Web Vitals库整合到前端全链路的全过程，但并没有提及何时报告数据以及怎么上报。现在，我给你一个小小的思考题，你觉得有了网页指标后，应该在什么时机上报这些数据呢？

关于在使用Web Vitals过程中遇到的问题和建议，非常欢迎和我交流，一起共同进步和成长。欢迎你在留言区和我交流。如果觉得有所收获，也可以把课程分享给更多的朋友一起学习。我们下节课见！