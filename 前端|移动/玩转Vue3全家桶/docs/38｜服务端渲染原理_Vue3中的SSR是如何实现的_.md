你好，我是大圣，上一讲我们学完vue-router源码，Vue全家桶的生态就基本介绍完了，包括Vue的响应式、运行时、编译器，以及全家桶的vuex和vue-router。

今天我来给你介绍Vue中优化的一个进阶知识点：SSR（Server Side Rendering），也就是服务端渲染。

## SSR是什么

要想搞清楚SSR是什么？我们需要先理解这个方案是为解决什么问题而产生的。

在现在MVVM盛行的时代，无论是Vue还是React的全家桶，都有路由框架的身影，所以，页面的渲染流程也全部都是浏览器加载完JavaScript文件后，由JavaScript获取当前的路由地址，再决定渲染哪个页面。

这种架构下， **所有的路由和页面都是在客户端进行解析和渲染的，我们称之为Client Side Rendering，简写为CSR，也就是客户端渲染**。

交互体验确实提升了，但同时也带来了两个小问题。

首先，如果采用CSR，我们在ailemente项目中执行 `npm run build` 命令后，可以在项目根目录下看到多了一个dist文件夹，打开其中的index.html文件，看到下面的代码：

```xml
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite App</title>
    <script type="module" crossorigin src="/assets/index.c305634d.js"></script>
    <link rel="modulepreload" href="/assets/vendor.9419ee42.js">
    <link rel="stylesheet" href="/assets/index.1826a359.css">
  </head>
  <body>
    <div id="app"></div>

  </body>
</html>

```

这就是项目部署上线之后的入口文件，body内部就是一个空的div标签，用户访问这个页面后，页面的首屏需要等待JavaScript加载和执行完毕才能看到，这样白屏时间肯定比body内部写页面标签的要长一些，尤其在客户端网络环境差的情况下，等待JavaScript下载和执行的白屏时间是很伤害用户体验的。

其次，搜索引擎的爬虫抓取到你的页面数据后，发现body是空的，也会认为你这个页面是空的，这对于SEO是很不利的。即使现在基于Google的搜索引擎爬虫已经能够支持JavaScript的执行，但是爬虫不会等待页面的网络数据请求，何况国内主要的搜索引擎还是百度。

所以如果你的项目对白屏时间和搜索引擎有要求， **我们就需要在用户访问页面的时候，能够把首屏渲染的HTML内容写入到body内部，也就是说我们需要在服务器端实现组件的渲染**，这就是SSR的用武之地。

## 怎么做SSR

那怎么在服务器端实现组件渲染呢？Vue提供了@vue/server-renderer这个专门做服务端解析的库，我们来尝试使用一下。

首先创建一个新的文件夹vue-ssr，执行下面命令来安装server-renderer、vue和express：

```xml
npm init -y
npm install @vue/server-renderer vue@next express --save

```

然后新建server.js，核心就是要实现在服务器端解析Vue的组件，直接把渲染结果返回给浏览器。

下面的代码中我们使用express启动了一个服务器，监听9093端口，在用户访问首页的时候，通过createSSRApp创建一个Vue的实例，并且通过@vue/compiler-ssr对模板的template进行编译，返回的函数配置在vueapp的ssrRender属性上，最后通过@vue/server-renderer的renderToString方法渲染Vue的实例，把renderToString返回的字符串通过res.send返回给客户端。

```javascript
// 引入express
const express = require('express')
const app = express()
const Vue = require('vue') // vue@next
const renderer3 = require('@vue/server-renderer')
const vue3Compile= require('@vue/compiler-ssr')

// 一个vue的组件
const vueapp = {
  template: `<div>
    <h1 @click="add">{{num}}</h1>
    <ul >
      <li v-for="(todo,n) in todos" >{{n+1}}--{{todo}}</li>
    </ul>
  </div>`,
  data(){
    return {
      num:1,
      todos:['吃饭','睡觉','学习Vue']
    }
  },
  methods:{
    add(){
      this.num++
    }
  }
}
// 使用@vue/compiler-ssr解析template
vueapp.ssrRender = new Function('require',vue3Compile.compile(vueapp.template).code)(require)
// 路由首页返回结果
app.get('/',async function(req,res){
    let vapp = Vue.createSSRApp(vueapp)
    let html = await renderer3.renderToString(vapp)
    const title = "Vue SSR"
    let ret = `
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${title}</title>
  </head>
  <body>
    <div id="app">
      ${html}
    </div>
  </body>
</html>`
    res.send(ret)
})

app.listen(9093,()=>{
    console.log('listen 9093')
})

```

现在我们访问页面后，点击右键查看网页源代码，会出现下图所示的页面：

![图片](https://static001.geekbang.org/resource/image/7a/d2/7a345e1b518259e0b2fd7bb0d6c7f6d2.png?wh=1920x582)

可以看到，首屏的body标签内部就出现了vue组件中v-for渲染后的标签结果，我们的第一步就完成了。

但具体SSR是怎么实现的呢？我们一起来看源码。

## Vue SSR源码剖析

在CSR环境下，template解析的render函数用来返回组件的虚拟DOM，而SSR环境下template解析的ssrRender函数，函数内部是通过\_push对字符串进行拼接，最终生成组件渲染的结果的。你可以在官方的 [模板渲染演示页面](https://vue-next-template-explorer.netlify.app/#%7B%22src%22%3A%22%3Cdiv%3E%5Cn%20%20%20%20%3Cul%20%3E%5Cn%20%20%20%20%20%20%3Cli%20v-for%3D%5C%22(todo%2Cn)%20in%20todos%5C%22%20%3E%7B%7Bn%2B1%7D%7D--%7B%7Btodo%7D%7D%3C%2Fli%3E%5Cn%20%20%20%20%3C%2Ful%3E%5Cn%20%20%3C%2Fdiv%3E%22%2C%22ssr%22%3Atrue%2C%22options%22%3A%7B%22mode%22%3A%22function%22%2C%22filename%22%3A%22Foo.vue%22%2C%22prefixIdentifiers%22%3Afalse%2C%22hoistStatic%22%3Atrue%2C%22cacheHandlers%22%3Atrue%2C%22scopeId%22%3Anull%2C%22inline%22%3Afalse%2C%22ssrCssVars%22%3A%22%7B%20color%20%7D%22%2C%22compatConfig%22%3A%7B%22MODE%22%3A3%7D%2C%22whitespace%22%3A%22condense%22%2C%22bindingMetadata%22%3A%7B%22TestComponent%22%3A%22setup-const%22%2C%22setupRef%22%3A%22setup-ref%22%2C%22setupConst%22%3A%22setup-const%22%2C%22setupLet%22%3A%22setup-let%22%2C%22setupMaybeRef%22%3A%22setup-maybe-ref%22%2C%22setupProp%22%3A%22props%22%2C%22vMySetupDir%22%3A%22setup-const%22%7D%2C%22optimizeBindings%22%3Afalse%7D%7D) 选择ssr设置后，看到渲染的结果：

```javascript
const { mergeProps: _mergeProps } = require("vue")
const { ssrRenderAttrs: _ssrRenderAttrs, ssrInterpolate: _ssrInterpolate, ssrRenderList: _ssrRenderList } = require("vue/server-renderer")

return function ssrRender(_ctx, _push, _parent, _attrs, $props, $setup, $data, $options) {
  const _cssVars = { style: { color: _ctx.color }}
  _push(`<div${_ssrRenderAttrs(_mergeProps(_attrs, _cssVars))}><ul><!--[-->`)
  _ssrRenderList(_ctx.todos, (todo, n) => {
    _push(`<li>${
      _ssrInterpolate(n+1)
    }--${
      _ssrInterpolate(todo)
    }</li>`)
  })
  _push(`<!--]--></ul></div>`)
}

```

可以看到ssrRender函数内部通过传递的\_push函数拼接组件渲染的结果后，直接返回renderToString函数的执行结果。

那renderToString是如何工作的呢？

现在你已经拥有了源码阅读的技巧，我们进入到vue-next/packages/server-renderer文件中，打开 **renderToString文件**：

```javascript
export async function renderToString(
  input: App | VNode,
  context: SSRContext = {}
): Promise<string> {
  if (isVNode(input)) {
    // raw vnode, wrap with app (for context)
    return renderToString(createApp({ render: () => input }), context)
  }
  const vnode = createVNode(input._component, input._props)
  vnode.appContext = input._context
  // provide the ssr context to the tree
  input.provide(ssrContextKey, context)
  const buffer = await renderComponentVNode(vnode)

  await resolveTeleports(context)

  return unrollBuffer(buffer as SSRBuffer)
}

```

这段代码可以看到，我们通过renderComponentVNode函数对创建的Vnode进行渲染，生成一个buffer变量，最后通过unrollBuffer返回字符串。

我们先继续看 **renderComponentVNode函数**，它内部通过renderComponentSubTree进行虚拟DOM的子树渲染，而renderComponentSubTree内部调用组件内部的ssrRender函数，这个函数就是我们代码中通过@vue/compiler-ssr解析之后的ssrRender函数，传递的push参数是通过createBuffer传递的：

```javascript
export function renderComponentVNode(
  vnode: VNode,
  parentComponent: ComponentInternalInstance | null = null,
  slotScopeId?: string
): SSRBuffer | Promise<SSRBuffer> {
  const instance = createComponentInstance(vnode, parentComponent, null)
  const res = setupComponent(instance, true /* isSSR */)
  if (hasAsyncSetup || prefetches) {
    ....
    return p.then(() => renderComponentSubTree(instance, slotScopeId))
  } else {
    return renderComponentSubTree(instance, slotScopeId)
  }
}
function renderComponentSubTree(instance,slotScopeId){
  const { getBuffer, push } = createBuffer()
  const ssrRender = instance.ssrRender || comp.ssrRender
  if (ssrRender) {
      ssrRender(
        instance.proxy,
        push,
        instance,
        attrs,
        // compiler-optimized bindings
        instance.props,
        instance.setupState,
        instance.data,
        instance.ctx
      )
  }
}

```

**createBuffer的实现** 也很简单，buffer是一个数组，push函数就是不停地在数组最后新增数据，如果item是字符串，就在数组最后一个数据上直接拼接字符串，否则就在数组尾部新增一个元素，这种提前合并字符串的做法，也算是一个小优化。

```javascript
export function createBuffer() {
  let appendable = false
  const buffer: SSRBuffer = []
  return {
    getBuffer(): SSRBuffer {
      // Return static buffer and await on items during unroll stage
      return buffer
    },
    push(item: SSRBufferItem) {
      const isStringItem = isString(item)
      if (appendable && isStringItem) {
        buffer[buffer.length - 1] += item as string
      } else {
        buffer.push(item)
      }
      appendable = isStringItem
      if (isPromise(item) || (isArray(item) && item.hasAsync)) {
        // promise, or child buffer with async, mark as async.
        // this allows skipping unnecessary await ticks during unroll stage
        buffer.hasAsync = true
      }
    }
  }
}

```

最后我们看下返回字符串的 **unrollBuffer函数**，由于buffer数组中可能会有异步的组件，服务器返回渲染内容之前，我们要把组件依赖的异步任务使用await，等待执行完毕后，进行字符串的拼接，最后返回给浏览器。

```javascript
async function unrollBuffer(buffer: SSRBuffer): Promise<string> {
  if (buffer.hasAsync) {
    let ret = ''
    for (let i = 0; i < buffer.length; i++) {
      let item = buffer[i]
      if (isPromise(item)) {
        item = await item
      }
      if (isString(item)) {
        ret += item
      } else {
        ret += await unrollBuffer(item)
      }
    }
    return ret
  } else {
    // sync buffer can be more efficiently unrolled without unnecessary await
    // ticks
    return unrollBufferSync(buffer)
  }
}

```

至此我们就把Vue中SSR的渲染流程梳理完毕了，通过compiler-ssr模块把template解析成ssrRender函数后，整个组件通过renderToString把组件渲染成字符串返回给浏览器。

SSR最终实现了通过服务器端解析Vue组件的方式，提高首屏的响应时间和页面的SEO友好度。

## 同构应用和其他渲染方式

现在服务器渲染SSR的逻辑我们已经掌握了，但是现在页面中没有JavaScript的加入，我们既需要提供服务器渲染的首屏内容，又需要CSR带来的优秀交互体验，这个时候我们就需要使用同构的方式来构建Vue的应用。

什么是同构应用呢？看来自于Vue官网的同构应用的经典架构图：

![图片](https://static001.geekbang.org/resource/image/13/6b/13ba7725eb1e2aaf07920ae5cbb9d26b.png?wh=1920x880)

左边是我们的源码，无论项目有多么复杂，都可以拆分为component + store + router三大模块。这一部分的源码，设置了两个入口，分别是客户端入口 client entry 和服务器端入口 server entry。打包的过程中也有两个打包的配置文件，分别客户端的配置和服务器端的配置。

最终在服务端实现用户首次访问页面的时候通过服务器端入口进入，显示服务器渲染的结果，然后用户在后续的操作中由客户端接管，通过vue-router来提高页面跳转的交互体验，这就是 **同构应用** 的概念。

### SSR+同构的问题

当然，没有任何一个技术架构是完美的，SSR和同构带来了很好的首屏速度和SEO友好度，但是也让我们的项目多了一个Node服务器模块。

首先，我们部署的难度会提高。之前的静态资源直接上传到服务器的Nginx目录下，做好版本管理即可，现在还需要在服务器上部署一个Node环境，额外带来了部署和监控的成本，工作量提升了。

其次，SSR和同构的架构，实际上，是把客户端渲染组件的计算逻辑移到了服务器端执行，在并发量大的场景中，会加大服务器的负载。所以，所有的同构应用下还需要有降级渲染的逻辑，在服务器负载过高或者服务器有异常报错的情况下，让页面恢复为客户端渲染。

总的来说，同构解决问题的同时，也带来了额外的系统复杂度。 **每个技术架构的出现都是为了解决一些特定的问题，但是它们的出现也必然会带来新的问题**。

针对同构出现的问题目前也有一些解决方案来应对。

### 解决方案

针对SSR架构的问题，我们也可以使用 **静态网站生成（Static Site Generation，SSG）** 的方式来解决，针对页面中变动频率不高的页面，直接渲染成静态页面来展示。

比如极客时间的首页变化频率比较高，每次我们都需要对每个课程的销量和评分进行排序，这部分的每次访问都需要从后端读取数据；但是每个课程内部的页面，比如文章详情页，变化频率其实是很低的，虽然课程的文本是存储在数据库里，但是每次上线前，我们可以把课程详情页生成静态的HTML页面再上线。

Vue的SSR框架nuxt就提供了很好的SSG功能，由于这一部分页面变化频率低，我们静态化之后还可以通过部署到CDN来进行页面加速，每次新文章发布或者修改的时候，重新生成一遍即可。

当然SSG也不是完全没有问题，比如极客时间如果有一万门课了，每门课几十篇文章，每次部署都全量静态生成一遍，耗时是非常惊人的，所以也不断有新的解决方案出现。

如果你的页面是内嵌在客户端内部的，可以借助客户端的运算能力，把SSR的逻辑移动到客户端进行，使用 **客户端渲染（Native Side Rendering，NSR）** 的方式降低服务端的负载，同时也能提高首屏的响应时间。

针对SSG全量生成的性能问题，我们可以采用 **增量渲染（Incremental Site Rendering，ISR）** 的方式，每次只生成核心重点的页面，比如每个课程的开篇词，其他的页面访问的时候先通过CSR的方式渲染，然后把渲染结果存储在CDN中。

现在还有解决方案 **边缘渲染（Edge Side Rendering，ESR）**，把静态内容和动态的内容都以流的方式返回给用户，在CDN节点上返回给用户缓存静态资源，同时在CDN上负责发起动态内容的请求。

今年还出现了在浏览器里跑node的 [webcontainer](https://blog.stackblitz.com/posts/introducing-webcontainers) 技术，如果这个技术成熟后，我们甚至可以把Express、Egg.js等后端应用也部署到CDN节点上，在浏览器端实现服务器应用的ESR，一起期待webcontainer技术的发展。

## 总结

我们要聊的内容就讲完了，来回顾一下。

今天我们学习了Vue中服务器渲染的原理，Vue通过@vue/compiler-ssr库把template解析成ssrRender函数，并且用@vue/server-renderer库提供了在服务器端渲染组件的能力，让用户访问首屏页面的时候，能够有更快的首屏渲染结果，并且对SEO也是友好的，server-renderer通过提供renderToString函数，内部通过管理buffer数组实现组件的渲染。

然后我们学习了SSR之后的同构、静态网站生成SSG、增量渲染ISR和边缘渲染ESR等内容，Vue中的最成熟的SSR框架就是nuxt了，最新的nuxt3还没有正式发版，内部对于SSG和ESR都支持，等nuxt3发版后你可以自行学习。

每一个技术选型都是为了解决问题存在的，无论学习什么技术，我们都不要单纯地把它当做八股文，这样才能真正掌握好一个技术。

## 思考题

最后留个思考题，你现在负责的项目，是出于什么目的考虑使用SSR的呢？欢迎在评论区分享你的思考，我们下一讲再见。