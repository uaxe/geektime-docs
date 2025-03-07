你好，我是三桥。

对于网页来说，用户行为是一种输入，那什么样的网页“输出”才会更好呢？想象一下，如果你在打开一个页面时，加载过程需要等待很久才出现画面，你还愿意等下去吗？你还会继续想用这样的产品吗？

我想表达的是，网页的反馈速度，对于用户体验至关重要，这也是我们在前端全链路监控中最核心的指标。这节课，我们就一起来学习通过网页指标衡量Web页面用户体验的方法。

我们先从前端最常用的分析方法开始。

## 使用 Performance 指标分析用户体验的局限性

对于大部分Web开发者来说，需要做Web性能分析时，第一时间肯定会想到用window.performance接口获取一个Web页面的性能基础数据，然后再分析，就完事了。

但是不是真的能解决问题呢？不能。

你可以看下下面这张图，Performance接口记录了一次网页加载全过程中每个生命周期的指标。这些指标，都是以时间戳来表达每个生命周期的时间位置的。

![图片](https://static001.geekbang.org/resource/image/5b/f7/5bb743e499e273e3183d786a0c8341f7.png?wh=1152x420 "图来源自W3C：https://www.w3.org/TR/navigation-timing-2/")

假设，即使我们获取到了这些时间戳，它们真的能帮助我们判断Web应用存在哪些性能问题吗？

首先，performance.timing获取每个周期阶段的时间戳，都只是网页加载过程中每个生命周期的时间节点，对于我们分析Web应用性能帮助还是有限的，毕竟我们还要通过这些时间戳去计算真正需要的指标值。

比如获取当前页面性能指标的代码。

```javascript
// 获取生命周期所有节点的时间戳对象
const timing = window.performance.timing 
// 获取首字节时间 
const ttfbTime = timing.responseStart - timing.requestStart 
// 首字节渲染时间 
const fptTime = timing.responseEnd - timing.fetchStart
// 页面完整加载时间 
const loadPageTime = timing.loadEventStart - timing.fetchStart 
// TCP连接时间 
const tcpTime = timing.connectEnd - timing.connectStart 
// dns连接时间 
const dnsTime = timing.domainLookupEnd - timing.domainLookupStart
```

实际上，即使我们获取到上述的这些时间，也无法判断我们的Web应用是否有问题，甚至有时候计算出来的数值是负数，或者超过5位数。

特别是在一些常见的开发模式里，例如Vue的SPA静态路由，基本上不可能套用这些公式的。

最后，你可能觉得还有官方推荐的PerformanceNavigationTiming对象呢，比如这样一串获取当前页面性能数据的代码：

```javascript
performance.getEntriesByType("navigation")
```

其实，虽然它用的是相对时间值，但我们还是没法用什么标准去衡量指标的性能情况。

总结一下，由于Performance标准是一套以网页加载生命周期为中心的网页指标，所以，我们无法通过它衡量真实的用户真实体验。而且，使用Performance对象分析Web页面性能，存在较多不可预估的问题。

1. 接口数据无法量化。通过接口获得的时间值，需要再进行二次计算才能得出有效数据，如果值很大或者很小，还要对数据进行三次筛选。
2. 难以标准量化。即使是通过后期计算出来的数据，也无法客观地衡量Web页面是否存在用户体验问题。
3. SPA单页面支持不够友好。SPA应用提供了更快的页面加载和更好的交互体验，但是使用Performance来追踪一个SPA页面加载的完整生命周期会缺失很多指标，而且获取的性能信息也不准确。

## 以用户为中心的核心网页指标

想要真正了解Web应用的性能，就应该使用以用户为中心的网页指标。Google推出了一套可以衡量页面状况的指标，希望通过这套指标，推动改善用户体验。

目前，网页指标分为两部分，一部分是核心网页指标，一部分是其它网页指标。

- 核心网页指标，是围绕用户体验的三个方面去衡量，包括加载响应速度（LCP）、互动交互（FID）以及视觉稳定性（CLS）。
- 其它网页指标，包括首次内容绘制（FCP）、互动延迟（INP）、可交互时间（TTI）、总阻塞时间（TBT）、首字节时间（TTFB）等等。

其中，加载响应速度是最核心的指标，Web页面出现的如打开慢、加载慢、白屏时间长等问题，都是参考这个指标去判断和衡量的。

接下来，我们就来学习一下这些指标，为我们后续的实战打下一个良好的基础。

### 网页指标

1. **网页加载速度指标（LCP）**

LCP对应其英语的三个词语Largest Contentful Paint。从这三个词语的组成来看，其含义就是最大内容渲染。

通俗来说，这个指标实际上是记录页面首屏可见区域中最大元素的呈现时间。而最大元素可能是一张图片，可能是一个视频，也可能是一段文本内容块。具体记录哪一种元素，与页面首屏所呈现的内容有关。

你想象一下，当你实现一个Web页面时，首屏内容区域中因为存在一张需要加载超过10M的图片，那得需要花费很多时间，特别是一些低速网络的用户，那必定会影响网页加载速度。

所以，在现实中，我们实现的Web页面，通常都很复杂，特别是业务不断迭代之后，影响页面加载速度的因素就变得很多。

2. **网页可交互指标（FID）**

我们都知道网页交互是一切和用户进行互动的重要手段，所以，第二个核心网页指标就是FID，全称为First Input Delay，其含义就是从用户首次和Web应用互动到浏览器实际开始处理事件或者处理脚本，响应用户互动的这段时间。

如果说，**LCP** **是衡量感受** **Web应用加载速度的第一印象的话，那么** **FID** **就是衡量你和** **Web** **应用互动的第一印象。**

一个侧重加载，一个侧重互动，也即响应能力。

既然是用户与Web互动，那互动就必定分为两部分，一部分是用户操作，另一部分是页面的响应。用计算机术语来描述的话，就叫做输入和输出。一般情况下，发生FID交互问题的场景，都是在页面响应阶段。

页面响应涉及的范围很大，其核心逻辑是当用户进行交互操作时，浏览器的主线程正忙于执行其他操作，例如解析或执行较大的Javascript文件。

特别是移动端Web应用，由于用户环境复杂，我们经常会遇到，当在手机上加载一个Web页面时，看到页面内容那一刻（此时可能页面还没完全渲染完成），就会很自觉地快速找到我们想要的操作位置（例如表单、按钮等），并尝试和页面进行互动（例如弹出键盘并输入、点击播放按钮等），但此时，页面仍然没有任何反应。

遇到这样的场景时，用户就无法快速体验Web应用，这时用户的心情一定会很沮丧，可能因为这样较差的体验，用户以后就不再来了。

3. **网页视觉稳定性指标（CLS）**

第三个核心指标就是视觉稳定性指标（CLS），英文全称Cumulative Layout Shift。这个指标更多的是判断用户的视觉上的体验，也就是在浏览器可视区内现有元素发生位置的改变，触发布局偏移，是否影响用户的使用体验。

换个思维，我们可以这样理解，CLS是衡量在一个Web应用的整个生命周期内，发生每次意外布局偏移的最大布局偏移分数。

是不是很虚？很难理解？

确实是很虚，因为这关系到用户在使用我们Web应用时，视觉上的感觉或感受。从心理学角度分析，这种视觉变化上的触动，会导致用户在思想和行为的生理和心理变化。

4. **首次内容绘制（FCP）**

首次内容绘制也是一个非常重要的指标。我认为如果三大核心网页指标作为排名前三重要的话，那排在第四位的就是FCP。

前面我们讨论的LCP是衡量最大内容渲染的时间，相反，FCP就是衡量第一次绘制内容的时间。

从这样的概念理解，FCP的时间必定小于LCP，在FCP和LCP之间的时间差里，就是浏览器持续性地渲染加载页面内容，又或者在执行脚本的过程。

为什么说这是一个非常重要的指标？

因为，FCP指标预示着用户从输入一个链接到真正看到第一个画面所花费的时间。立刻看到有内容渲染的时刻，能让用户清楚地知道Web应用是可访问的、可使用的、可以交互的。通过FCP，我们也能粗略评估出当前页面的白屏时间。

5. **互动响应速度（INP）**

INP指标英文全称叫Interaction to Next Paint。INP就是用来监听用户交互互动到页面响应的延迟时间。你有没有发现，INP和FID的指标定义很像，也就是说，如果用户在一个页面内的多次互动，那么INP会记录多个指标数据，并以最长延迟时间的那一次互动作为最终值。

这种场景非常多，例如增加商品到购物车的效果、风琴式折叠导航栏、多层级菜单、表单验证等。

需要说明的是，只有需出现交互场景才会监测和记录INP，所以，像是页面已经加载完毕，但用户没有点击或操作表单的时候，或者是在移动端，网页加载完毕，但用户的手势在互动操作里不涉及点击、点按或输入框输入等操作的时候，就不会有INP值的记录。

又例如搜索引擎收录页面、无头浏览器访问的时候，这种非实际用户访问的场景，基本上也不会存在INP值。

6. **可交互时间（TTI）**

可交互时间（TTI），顾名思义，就是衡量从网页开始加载到其主要子资源加载完成的时间。从定义上看，这个时间比FCP更靠前。

但由于TTI指标目前仍然是一个实验性指标，因此官方没有重点推广这个指标。但从FCP、LCP等指标中，一样可以分析出TTI是否存在性能问题。

7. **总阻塞时间（TBT）**

前面提到，首次内容绘制FCP之后还存在如LCP等其它指标。在基于FCP时间之后，页面会发生很多不同场景的事件，比如渲染内容、请求接口、主线程脚本执行等。

而在这个时间范围内，可以定义一个用于衡量事件或任务的总阻塞时间，我们称为TBT，它能帮助我们快速判断在这个时间范围内，哪些事件耗时较长、哪些接口请求时间长等等。

通常来说，经过很多次需求迭代之后，无论前期架构做得多么完善，后期的业务代码都会越来越臃肿，臃肿还不是最大的问题，最大的问题是功能逻辑上出了问题，最终导致性能问题，比如请求接口次数太多、组件不断重新渲染、重排重绘、页面加载卡顿等等。

这种性能问题，归根到底都是事件或任务运行时间很长，特别是在浏览器主线程上执行的代码。通常一个任务的执行时间建议不超过50ms，如果超过，会被主线程视为“阻塞”。这种任务，我们可以理解为长任务。

例如下面的任务队列处理顺序图。

![图片](https://static001.geekbang.org/resource/image/8d/d6/8df0dayy003829f62077b4aayye62cd6.png?wh=1081x180 "图来源于web.dev：https://web.dev/articles/tbt?hl=zh-cn")

上图一共有5个任务，其中第一个任务运行时间为250ms，如果按50ms的标准去衡量，这就是一个长任务，最终这个任务的阻塞时间就是200ms（阻塞时间=250ms-50ms）。最终的TBT时间是取5个任务减去50ms后的时间的总和。

通常我们都是在开发环境下的Google DevTool上进行总阻塞时间TBT的分析，又或者是在Lighthouse性能工具中分析。目前还没有一套可行的通过脚本去分析和计算出这样的指标的方案。

8. **首字节时间（TTFB）**

首字节时间TTFB，就是资源请求与响应的第一个字节开始到达之间的时间。TTFB就是衡量Performance.startTime和Performance.responseStart之间的间隔时间。

通常能影响到这个TTFB时间的因素有很多，比如多个页面的重定向时间，DNS查找时间，连接和TLS协商时间等等。

虽然TTFB并不是核心网页指标，但它是衡量Web应用可用性的 最重要的参考指标。它能帮助我们分析和评估在到达用户设备之前的网络状况。

### 一个真实的需求场景

下面，我们就以核心网页指标 LCP 为例，一起来看一个真实的需求场景。

需求是这样的，产品在第一轮需求是希望实现一个落地页，假设我们给它定义了“长连接”页面。

前端开发工程师很快就完成了这个落地页的开发，也上线了，而且有意识地通过Chrome DevTool分析Web性能，用LCP判断Web应用的指标值。假设这个值平均在600ms，最大值在1500ms。

很快，产品继续提出第二轮新需求，不希望使用这个Page地址，提出了短地址需求，因为营销推广时能给用户提供更好的体验。而点击短地址，就会自动跳转回“长连接”。

假设我们给这个短地址定义为“短连接”。

同样，技术上没什么难度，只要增加短链、增加缓存和302跳转即可满足需求。

我们还是通过Chrome DevTool获取LCP指标值。

此时我们发现，LCP平均值在1200ms，最大值在2200ms，LCP会把从“短连接”跳转到“长连接”过程中的耗时也算上。

第二轮需求满足后，过了一段时间，由于产品无法做到灰度，因此提出了第三轮需求，产品需要在营销落地页进行ABTest推广，希望实现“短连接”能根据AB场景跳转不同的“长连接”。

第三轮需求依然没难度，通过一定的机制，前后端实现了一套ABTest功能。好，现在，我们再通过Chrome DevTool获取LCP，突然发现平均值接近2000ms，最大值是3000ms。

在做到第三轮需求的时候，因为需求迭代快、需求多，而且每次都很简单，能快速上线，我们也就没有重点关注性能问题。

下图是三轮需求最终测试出来的LCP值的波动情况。

![图片](https://static001.geekbang.org/resource/image/46/49/46912ecyy354b6213f646f1dfd127349.png?wh=2238x722)

有没有发现，到了第三轮需求，研发开发出来的页面比起前两轮的需求，打开速度已经很慢了。

因为首屏内容区域中最大的一个元素所需呈现时间从均值600ms上升到2000ms，虽然感官上可能未必体验得到，但实际上页面越来越慢的事实是存在的。这就是通过LCP获取的数据。

## 如何衡量指标

从LCP这个案例，我们可以再延伸思考一下。在需求不断迭代之后，我们应该怎么看Web页面指标值有没有增长呢？怎么判断增长到一定的阈值后，处于一种怎样的状态呢？而这种状态，究竟是用户网络问题，还是Web性能问题，甚至是交互问题？

其实，每一个网页指标都代表着一种场景，我们可以通过一种标准参考值来衡量用户的体验效果。

### 标准的衡量

官方提供了一套标准，可以衡量每个指标数据当前所在的位置，方便我们有一个初步的判断。

> 好（Good）&gt; 需要改进（Needs Improvement）&gt; 体验较差（Poor）

每一个指标的衡量，既以时间作为参考单位，也以一个数值作为判断标准。毕竟，不是所有场景都可以用时间来衡量用户体验的真实感觉，例如视觉稳定性。

下面是每个指标所对应的衡量值。

![图片](https://static001.geekbang.org/resource/image/d4/d5/d4a0a694ff9ff59278f349aa5b8ee9d5.png?wh=2077x888)

为什么CLS使用的是数值比较呢？

理解CLS概念时有一个关键词：分数。也就是说，CLS是用一套公式计算出一个分数，基于这个分数来衡量好与差的。

官方基于布局偏移这个概念，定义了布局偏移分数的计算公式，用来衡量视觉上的用户体验值。

首先，我们先理解下面几个新名词。

1. 不稳定的元素。元素是指在浏览器可视视口内可见的内容对应DOM节点，不稳定是指这个可见元素在上一帧和当前帧产生的起始位置的变化。所以，不稳定的元素，一定是首屏内第一眼可见的页面内容对应的一个或多个元素。
2. 影响比例。它是衡量出现不稳定的元素对于前后变化，对可视视口区域的影响程度。
3. 距离分数。它是测量这个不稳定元素相对于可视视口区域内的移动距离。

这套公式，主要由影响比例和距离分数两个要素组成。每一个不稳定的元素，都有一个布局偏移分数。

整个公式就是：**布局偏移得分 =** **影响比例 x 距离分数**

前面也提到，不稳定的元素有可能不止一个，所以，也就存在多个布局偏移得分。

其中，分数最大的那个不稳定元素，肯定会对用户体验影响最大。

那么，一个CLS指标值，是由多个布局偏移分数组成并取最大值。计算公式如下：

> CLS = Max(布局偏移得分1, 布局偏移得分2, 布局偏移得分3, ……)

不过，公式得出的数据对我们Web开发者来说仍然只是一个参考，是用来快速判断问题的，至于最终是否存在用户视觉上的问题，还是需要拆解整个Web页面流程去分析才能得出结果。

### 第 75 百分位

除了衡量值，Google官方还提出了另一个建议。为了保证用户的良好体验，可以通过总记录量排序的第75百分位来衡量LCP。

**这个怎么理解呢?**

还是以LCP为例，如果一个页面的总访问量是1000PV，那么LCP一共会监测和收集到1000份指标数据。

我们基于这1000份指标数据重新整理顺序，按从低到高进行排序。

那么，第一条肯定是最少的时间，最后一条数据是最大值，假设我们的第一条数据是500ms。最后一条的时间是5000ms，也就是5秒。

按照第75百分位来衡量的话，那么排在750位置的指标数据，就是判断的基准。我们假设这个位置的时间是3.5s，按照我刚才说的判断性能好不好的方式，3.5s说明当前的页面可能存在性能问题，就需要优化和改进。

**那75** **百分位真的合适？**

移动端和桌面PC端是两个不同领域的场景，虽然官方推荐的是第75百分位，但我认为，因为桌面PC端的浏览器和网络环境更优，所以桌面PC端的百分位应该在98%以上。

而移动端相反，移动端用户通常会被网络环境限制，不同App之间打开的方式 也存在很大差异，所以很难用一个官方的标准来衡量网页指标，需要按实际情况来评估。前期的时候，我们可以基于75百分位来衡量，但如果对页面可访问性的要求更高，那么这个标准就需要提升到更高的百分位。

不管是桌面PC端还是移动端Web应用，页面性能问题的重要性不言而喻，这个75百分位的定义，我认为偏低了。

所以，我建议你根据实际情况去调整，如果一个Web应用里面有多个核心的页面，同时是和用户强交互关联的，这个百分位数的阈值应该要上升到95～99的百分位。

关于怎么实现网页指标、监控指标、优化页面的内容，我会在后面的课程详解。

## 总结

这节课，我们探讨了为什么Performance无法帮助我们去分析用户体验问题，以及如何利用以用户为中心的用户体验的方法衡量Web性能问题。

接着，我们探讨了由Chrome团队提出的以用户为中心的用户体验的多个网页指标的基本概念。

- 基于用户加载速度的体验，可以通过LCP、FCP等指标来衡量。
- 基于用户和网页之间的互动指标，可以使用FID或INP等来衡量。
- 基于用户使用Web应用的视觉稳定性，可以使用CLS指标来衡量。
- 基于判断用户网络状况，可以使用TTI、TTFB等指标来衡量。
- 基于判断Web应用脚本执行效率，可以用TBT等指标来衡量。

总之，基于用户实际使用过程中的不同Web网页指标来衡量一个Web应用的性能情况或者体验效果，总比只看一堆网页加载时不同生命周期的时间戳更靠谱，也更容易判断和解决问题。

## 思考题

虽然WebVitals是由Chome团队提出的一系列网页指标，但也没那么全面，所以这节课的最后，我也给你留一道思考题，在实际Web业务里，如果从用户体验的角度去考虑，是否还有其他方法来衡量Web页面的性能问题呢？

期待你的思考，如果今天的课程对你有帮助，也欢迎分享给有需要的朋友，我们下节课再见！
<div><strong>精选留言（5）</strong></div><ul>
<li><span>苏果果</span> 👍（0） 💬（0）<p>完整源码入口：
https:&#47;&#47;github.com&#47;sankyutang&#47;fontend-trace-geekbang-course</p>2024-07-18</li><br/><li><span>苏果果</span> 👍（1） 💬（1）<p>各位同学大家好～我是这门课程的编辑同学。

课程将于五一假期暂停更新，在5月6日（周一）00:00恢复更新。

假期归来之后欢迎继续追更～预祝大家五一假期快乐！</p>2024-04-30</li><br/><li><span>JuneRain</span> 👍（0） 💬（1）<p>利用 performance API获取到的生命周期时间戳，从而计算出来的TCP链接时间，DNS解析时间数值很大，是因为你没给要统计的资源的响应头加上 Timing-Allow-Origin 字段，导致 connectStart ，transferSize 等字段值一直为0

https:&#47;&#47;developer.mozilla.org&#47;en-US&#47;docs&#47;Web&#47;HTTP&#47;Headers&#47;Timing-Allow-Origin</p>2024-05-14</li><br/><li><span>北国风光</span> 👍（0） 💬（0）<p>请教个问题，页面上使用了大量的异步组件，根据条件渲染不同的异步组件，每次FCP的时间都不同，是不是针对异步加载组件的场景，FCP无法衡量加载性能？</p>2024-09-24</li><br/><li><span>Aaaaaaaaaaayou</span> 👍（0） 💬（0）<p>https:&#47;&#47;web.dev&#47;articles&#47;tti 从这里的定义来看 TTI 应该比 FCP 更靠后呀</p>2024-09-14</li><br/>
</ul>