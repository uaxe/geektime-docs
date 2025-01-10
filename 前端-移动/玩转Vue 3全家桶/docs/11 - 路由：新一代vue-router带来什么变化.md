你好，我是大圣。

在上一讲中，我带你了解了Vuex这个数据管理框架的使用方法，以及Vue 3中数据管理框架的来源、实战细节和相关的原理。

其实项目中除了数据管理，路由系统也是非常核心的模块。所以在这一讲中，我会先带你了解一下前端开发方式的演变，让你明白前端路由因何而来，之后再讲解前端路由的实现原理。最后，我会再带你手写一个vue-router，并在这个过程中为你补充相关的实战要点，让你对如何用好vue-router有一个直观体验。

## 前后端开发模式的演变

在jQuery时代，对于大部分Web项目而言，前端都是不能控制路由的，而是需要依赖后端项目的路由系统。通常，前端项目也会部署在后端项目的模板里，整个项目执行的示意图如下：

![图片](https://static001.geekbang.org/resource/image/26/2b/26ddd952f1f7d6dc3193af5be57e202b.jpg?wh=1569x462)

jQuery那个时代的前端工程师，都要学会在后端的模板，比如JSP，Smatry等里面写一些代码。但是在这个时代，前端工程师并不需要了解路由的概念。对于每次的页面跳转，都由后端开发人员来负责重新渲染模板。

前端依赖后端，并且前端不需要负责路由的这种开发方式，有很多的优点，比如开发速度会很快、后端也可以承担部分前端任务等，所以到现在还有很多公司的内部管理系统是这样的架构。当然，这种开发方式也有很多缺点，比如前后端项目无法分离、页面跳转由于需要重新刷新整个页面、等待时间较长等等，所以也会让交互体验下降。

为了提高页面的交互体验，很多前端工程师做了不同的尝试。在这个过程中，前端的开发模式发生了变化，项目的结构也发生了变化。下图所示的，是在目前的前端开发中，用户访问页面后代码执行的过程。

![图片](https://static001.geekbang.org/resource/image/26/ec/2657d4eb129568d3c5b766e40eef60ec.jpg?wh=1920x435)

从上面的示意图中，我们可以看到：用户访问路由后，无论是什么URL地址，都直接渲染一个前端的入口文件index.html，然后就会在index.html文件中加载JS和CSS。之后，JavaScript获取当前的页面地址，以及当前路由匹配的组件，再去动态渲染当前页面即可。用户在页面上进行点击操作时，也不需要刷新页面，而是直接通过JS重新计算出匹配的路由渲染即可。

在前后两个示意图中，绿色的部分表示的就是前端负责的内容。而在后面这个架构下，前端获得了路由的控制权，在JavaScript中控制路由系统。也因此，页面跳转的时候就不需要刷新页面，网页的浏览体验也得到了提高。 **这种所有路由都渲染一个前端入口文件的方式，是单页面应用程序（SPA，single page application）应用的雏形。**

通过JavaScript动态控制数据去提高用户体验的方式并不新奇，Ajax让数据的获取不需要刷新页面，SPA应用让路由跳转也不需要刷新页面。这种开发的模式在jQuery时代就出来了，浏览器路由的变化可以通过pushState来操作，这种纯前端开发应用的方式，以前称之为Pjax （pushState+ Ajax）。之后，这种开发模式在MVVM框架的时代大放异彩，现在大部分使用Vue/React/Angular的应用都是这种架构。

SPA应用相比于模板的开发方式，对前端更加友好，比如：前端对项目的控制权更大了、交互体验也更加丝滑，更重要的是，前端项目终于可以独立出来单独部署了。

## 前端路由的实现原理

在讲完前端路由的执行逻辑之后，我们深入探索一下前端控制路由的实现原理。

现在，通过URL区分路由的机制上，有两种实现方式，一种是hash模式，通过URL中#后面的内容做区分，我们称之为hash-router；另外一个方式就是history模式，在这种方式下，路由看起来和正常的URL完全一致。

这两个不同的原理，在vue-router中对应两个函数，分别是createWebHashHistory和createWebHistory。

![图片](https://static001.geekbang.org/resource/image/d0/d3/d07894f8b9df7c1afed10b730f8276d3.jpg?wh=1546x561)

### hash 模式

单页应用在页面交互、页面跳转上都是无刷新的，这极大地提高了用户访问网页的体验。 **为了实现单页应用，前端路由的需求也变得重要了起来。**

类似于服务端路由，前端路由实现起来其实也很简单，就是匹配不同的 URL 路径，进行解析，然后动态地渲染出区域 HTML 内容。但是这样存在一个问题，就是 URL 每次变化的时候，都会造成页面的刷新。解决这一问题的思路便是在改变 URL 的情况下，保证页面的不刷新。

在 2014 年之前，大家是通过 hash 来实现前端路由，URL hash 中的 # 就是类似于下面代码中的这种 # ：

```plain
http://www.xxx.com/#/login

```

之后，在进行页面跳转的操作时，hash 值的变化并不会导致浏览器页面的刷新，只是会触发hashchange事件。在下面的代码中，通过对hashchange事件的监听，我们就可以在fn函数内部进行动态地页面切换。

```javascript
window.addEventListener('hashchange',fn)

```

### history 模式

2014年之后，因为HTML5标准发布，浏览器多了两个API：pushState 和 replaceState。通过这两个 API ，我们可以改变 URL 地址，并且浏览器不会向后端发送请求，我们就能用另外一种方式实现前端路由\*\*。

在下面的代码中，我们监听了popstate事件，可以监听到通过pushState修改路由的变化。并且在fn函数中，我们实现了页面的更新操作。

```plain
window.addEventListener('popstate', fn)

```

## 手写迷你vue-router

明白了前端路由实现原理还不够，接下来我们一起写代码直观感受一下。这里我们准备设计一个使用hash模式的迷你vue-router。

现在，我们在src/router目录下新建一个grouter文件夹，并且在grouter文件夹内部新建index.js。有了 [上一讲](https://time.geekbang.org/column/article/439588) 手写Vuex的基础，我们就可以在index.js中写入下面的代码。

在代码中，我们首先实现了用Router类去管理路由，并且，我们使用createWebHashHistory来返回hash模式相关的监听代码，以及返回当前URL和监听hashchange事件的方法；然后，我们通过Router类的install方法注册了Router的实例，并对外暴露createRouter方法去创建Router实例；最后，我们还暴露了useRouter方法，去获取路由实例。

```javascript
import {ref,inject} from 'vue'
const ROUTER_KEY = '__router__'

function createRouter(options){
    return new Router(options)
}

function useRouter(){
    return inject(ROUTER_KEY)
}
function createWebHashHistory(){
    function bindEvents(fn){
        window.addEventListener('hashchange',fn)
    }
    return {
        bindEvents,
        url:window.location.hash.slice(1) || '/'
    }
}
class Router{
    constructor(options){
        this.history = options.history
        this.routes = options.routes
        this.current = ref(this.history.url)

        this.history.bindEvents(()=>{
            this.current.value = window.location.hash.slice(1)
        })
    }
    install(app){
        app.provide(ROUTER_KEY,this)
    }
}

export {createRouter,createWebHashHistory,useRouter}

```

有了上面这段代码，我们回到src/router/index.js中，可以看到下面代码的使用方式，我们使用createWebHashHistory作为history参数，使用routes作为页面的参数传递给createRouter函数。

```javascript
import {
    createRouter,
    createWebHashHistory,
} from './grouter/index'
const router = createRouter({
  history: createWebHashHistory(),
  routes
})

```

下一步，我们需要注册两个内置组件router-view和router-link。在createRouter创建的Router实例上，current返回当前的路由地址，并且使用ref包裹成响应式的数据。router-view组件的功能，就是current发生变化的时候，去匹配current地址对应的组件，然后动态渲染到router-view就可以了。

我们在src/router/grouter下新建RouterView.vue，写出下面的代码。在代码中，我们首先使用useRouter获取当前路由的实例；然后通过当前的路由，也就是router.current.value的值，在用户路由配置route中计算出匹配的组件；最后通过计算属性返回comp变量，在template内部使用component组件动态渲染。

```xml
<template>
    <component :is="comp"></component>
</template>
<script setup>

import {computed } from 'vue'
import { useRouter } from '../grouter/index'

let router = useRouter()

const comp = computed(()=>{
    const route = router.routes.find(
        (route) => route.path === router.current.value
    )
    return route?route.component : null
})
</script>

```

在上面的代码中，我们的目的是介绍vue-router的大致原理。之后，在课程的源码篇中，我们会在《前端路由原理：vue-router 源码剖析》这一讲完善这个函数的路由匹配逻辑，并让这个函数支持正则匹配。

有了RouterView组件后，我们再来实现router-link组件。我们在grouter下面新建文件RouterILink.vue，并写入下面的代码。代码中的template依然是渲染一个a标签，只是把a标签的href属性前面加了个一个#， 就实现了hash的修改。

```xml
<template>
    <a :href="'#'+props.to">
        <slot />
    </a>
</template>

<script setup>
import {defineProps} from 'vue'
let props = defineProps({
    to:{type:String,required:true}
})

</script>

```

然后，回到grouter/index.js中，我们注册router-link和router-view这两个组件, 这样hash模式的迷你vue-router就算实现了。这里我演示了支持hash模式迷你vue-router，那你不妨进一步思考一下，history模式又该如何实现。

```javascript
import {ref,inject} from 'vue'
import RouterLink from './RouterLink.vue'
import RouterView from './RouterView.vue'
class Router{
    ....
    install(app){
        app.provide(ROUTER_KEY,this)
        app.component("router-link",RouterLink)
        app.component("router-view",RouterView)
    }
}

```

**实际上，vue-router还需要处理很多额外的任务，比如路由懒加载、路由的正则匹配等等**。在今天了解了vue-router原理之后，等到课程最后一部分剖析vue-router源码的那一讲时，你就可以真正感受到“玩具版”的router和实战开发中的router的区别。

## vue-router实战要点

了解了vue-router的原理后，我们再来介绍一下vue-router在实战中的几个常见功能。

首先是在 **路由匹配的语法** 上，vue-router支持动态路由。例如我们有一个用户页面，这个页面使用的是User组件，但是每个用户的信息都不一样，需要给每一个用户配置单独的路由入口，这时就可以按下面代码中的样式来配置路由。

在下面的代码中，冒号开头的id就是路由的动态部分，会同时匹配/user/dasheng和/user/geektime， 这一部分的详细内容你可以参考 [官方文档的路由匹配语法部分](https://next.router.vuejs.org/zh/guide/essentials/route-matching-syntax.html)。

```javascript
const routes = [
  { path: '/users/:id', component: User },
]

```

然后是在实战中，对于有些页面来说，只有管理员才可以访问，普通用户访问时，会提示没有权限。这时就需要用到vue-router的 **导航守卫功能** 了，也就是在访问路由页面之前进行权限认证，这样可以做到对页面的控制，也就是只允许某些用户可以访问。

此外，在项目庞大之后，如果首屏加载文件太大，那么就可能会影响到性能。这个时候，我们可以使用vue-router的 **动态导入功能**，把不常用的路由组件单独打包，当访问到这个路由的时候再进行加载，这也是vue项目中常见的优化方式。

关于vue-router实战中的种种优化和注意点，在课程后续的15-19讲，也就是实战痛点中，我会借助实战场景，挨个给你讲解。

## 总结

好，这一讲的主要内容就讲完了，我们来总结一下今天学到的内容。首先，我们回顾了前后端开发模式的演变，也即前端项目经历的从最初的嵌入到后端内部发布，再到现在的前后端分离的过程，而这一过程也见证了前端SPA应用的发展。

然后，我们讲到了前端路由实现的两种方式，也即通过监听不同的浏览器事件，来实现hash模式和history模式。之后，根据这个原理，我们手写了一个迷你的vue-router，通过createRouter创建路由实例，并在app.use函数内部执行router-link和router-view组件的注册，最后在router-view组件内部动态的渲染组件。

在这一讲的最后，我还给你简单说明了一下vue-router实战中常见的一些痛点。vue-router进一步实战的内容，比如权限认证、页面懒加载等功能，在课程后面的15-19讲中还会详细展开。相信今天这一讲结束后，你一定对vue-router有了更加新的理解。

## 思考题

最后给你留个思考题，今天我们只用了大概60行代码，就实现了hash模式的迷你vue-router，那你还可以思考一下，支持history模式的迷你vue-router又该如何实现呢？

欢迎在留言区分享你的答案，也欢迎你把这一讲分享给你的朋友们，我们下一讲见！