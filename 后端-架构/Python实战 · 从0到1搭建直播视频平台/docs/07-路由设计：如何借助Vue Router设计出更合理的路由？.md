你好，我是Barry。

上节课我留过一个思考题，如果在我们平台中有一些公共的展示的内容，例如平台的Icon，我们希望在每一个页面都可以看到它，并且点击可以跳回首页，要怎么实现呢？

比较常见的一个做法就是通过路由来管理。实际开发中，一个企业级项目的页面众多，每一个页面都需要有对应的路由地址，为了保证所有链接可用，自然需要统一管理起来。

路由的配置管理在Vue框架开发中非常重要，是我们完成后续各功能模块开发的前提。因为我们需要提前配置好路由，才能控制网址和现实页面的对应关系。

这节课，我们就一起动手实践，最后给我们的视频平台配置路由。在动手之前，我们先简单了解一下 Vue 的官方路由。

## 初识 Vue Router

Vue 的官方路由是Vue Router ，在 [第4节课](https://time.geekbang.org/column/article/653986)，我们也了解到过它能帮我们在Vue框架中轻松快捷地配置路由。

我们先来认识一下Vue Router中两个至关重要的标签。

1.router-link：路由的链接标签，to属性是将要跳转的路由地址（即我们预先配置好的路由地址），它的用法似于HTML的<a>标签。

2.router-view：路由组件出口，相当于用来显示路由地址对应组件的HTML<div>标签。

当我们在页面要点击链接跳转到项目中的页面时，链接就要用到router-link标签。

```javascript
<router-link to="/">Go to Home</router-link>

```

当我们在页面上要显示路由对应的组件时，就要用到router-view标签。

```javascript
<router-view/>

```

下面我们进入实操练习，体会一下在Vue项目中如何使用Vue Router配置路由配置。

## Vue Router实操练习

为了直观看到路由的效果，我们先来定义一个简单的路由，把它配置到Vue上。

这个流程一共4步走。第一步，我们要安装Vue Router的依赖包到当前项目中，需要运行后面这条命令。

```javascript
npm install vue-router@4

```

第二步，我们要定义一个路由配置的文件。比如在项目src文件夹下建一个router文件夹，然后进入router文件夹，在里面创建一个index.js文件。

```javascript
import Vue from 'vue'
//引入Vue Router组件
import Router from 'vue-router'
//让Vue使用Router
Vue.use(Router)
const routes = [
  { path: '/', component: Home },    //路由地址和组件一一对应，注意需要换成自己的页面
  { path: '/about', component: About }
]

const router = new Router({
  routes: routes
})

export default router;

```

第三步，打开main.js，将刚刚在文件中定义好的路由绑定到Vue实例上。

```javascript
import Vue from 'vue'
//引入刚刚定义好的Vue Router 配置文件
import router from './router/index.js'
import App from './App'

new Vue({
  el: '#app',
  router,    //将路由绑定在Vue实例上
  components: {
    App
  },
  template: '<App/>'
})

```

第四步，在App.vue中加上router-view标签。

```javascript
<template>
  <div id="app">
    <!-- 路由出口 -->
    <!-- 路由匹配到的组件将渲染在这里 -->
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

```

这样一个最简单的路由就配置好啦！我们运行后面的命令，启动Vue来看一下效果。

```javascript
npm run dev

```

这时候我们通过浏览器直接看一下页面的效果。

我们在浏览器地址栏输入localhost:8080，显示的就是Home组件。你也可以尝试更换路由地址，例如输入localhost:8080/about ，显示的就会是About组件。

### 带参数的动态路由匹配

刚才通过简单的几个步骤，我们学会了简单的路由配置，也把路由绑定在了Vue实例上。接下来，我们再了解一些路由配置的其他常见功能，这些也是在我们后边项目开发中会用到的知识点，用好这些功能，后面项目开发才会更加高效。

很多时候，我们需要将给定匹配模式的路由映射到同一个组件。

例如，我们有一个商品详情组件，用来显示所有商品的详细信息，但商品 ID 不同，我们需要通过ID来查询商品的详细信息，并进行展示。所以每一次的点击，都需要带上商品的ID进行查询。在 Vue Router 中，我们可以在路径中使用一个动态字段来实现，我们称之为 **路径参数** 。

```javascript
const routes = [
  // 动态字段以冒号开始
  { path: '/product/detail/:id', component: ProductDetail },
]

```

这样，带路径参数的路由就配好了。

这时我们打开http://localhost:8080/product/detail/1，显示的应该是id为1的商品。打开http://localhost:8080/product/detail/2，显示的就应该是id为2的商品。

在商品详情页面中可以通过route的params方式来获取当前的ID，params是路由传值的方式，后面是代码实现。

```javascript
this.$route.params.id

```

### 重定向

当我们在开发过程中，如果遇到路由重定向的需求，需要跳转到路由配置的地址时，想转到其他地址，就可以使用重定向， **redirect是重定向到的地址**。

```javascript
const routes = [{ path: '/home', redirect: '/' }]

```

或者你可以采用下面的实现方式。

```javascript
const routes = [{ path: '/home', redirect: { name: 'homepage' } }]

```

### 别名

有时想通过更多的地址访问同一个组件，就可以给路由添加别名，alias的值就是对应其他地址的名称，后面具体的代码实现。

```javascript
const routes = [{ path: '/', component: Homepage, alias: '/home' }]

```

当我们需要更多地址时，alias可以是数组。

```javascript
const routes = [{
path: '/', component: Homepage,
alias: ['/addr1','/addr2','/addr3']
}]

```

### 嵌套路由

有时组件内要根据地址栏的地址嵌套不同的其他组件，我们就要用到嵌套路由。

例如几个页面要使用相同的布局，或者相同的组件，为了减少重复的工作，我们就会把公共的部分定义为父组件，中间可切换的部分用标签根据地址栏的路由地址渲染。

我们还是结合例子来理解，用户详情页需要显示不同的信息，这时候就需要嵌套不同的组件。

接下来我们通过两个案例一起认识一下嵌套路由。

```plain
/user/:id/userMes  //显示用户个人信息
/user/:id/photos  // 现实用户个人相册

//接下来我们看一下使用时的具体写法
/user/1/profile  显示id为1的用户的个人信息
/user/1/posts 显示id为1的用户的相册
/user/2/profile  显示id为2的用户的个人信息
/user/2/posts 显示id为2的用户的相册

```

那么在Router中该怎么配置呢？具体代码是后面这样。

```javascript
const routes = [
  {
    path: '/user/:id',
    component: User,
    children: [
      {
        // 当 /user/:id/profile 匹配成功
        // UserProfile 将被渲染到 User 的 <router-view> 内部
        path: '/profile',
        component: UserProfile
      },
      {
        // 当 /user/:id/posts 匹配成功
        // UserPosts 将被渲染到 User 的 <router-view> 内部
        path: '/posts',
        component: UserPosts
      },
    ],
  },
]

```

这样当 /user/:id/profile 匹配成功时，UserProfile 组件将被渲染到 User 的  内部，当 /user/:id/posts 匹配成功时，UserPosts 组件将被渲染到 User 的  内部。

### 懒加载

因为路由配置时引入了很多组件，当打包构建应用时，JavaScript 包会变得非常大，影响页面加载，这样不仅会造成资源的消耗，还会影响用户的体验。如果我们能当路由被访问的时候才加载对应组件，就会更加高效。

具体的实现方式我写在了后面。

```javascript
const ComponentA = （）=>import('需要加载的模块地址')

```

后面这种语法也是正确的。

```javascript
ComponentA：resolve=>(['需要加载的路由的地址'，resolve])

```

我们再结合Vue Router配置文件看一下懒加载的实现。

```javascript
// 将
// import UserDetails from './views/UserDetails.vue'
// 替换成
const UserDetails = () => import('./views/UserDetails.vue')

const router = new Router({
  // ...
  routes: [{
   path: '/users/:id',
  component: UserDetails
})

```

到这里，如何配置路由的核心知识我们就已经学习完了。

### API

为了让你对Vue Router的功能和属性更加熟悉，今后可以灵活地使用它。我们再来熟悉一些常见的常见Router API，它们能让我们在组件中实现路由的跳转、回退等功能。

1.跳转到其他路由页面

在代码中我们使用this.$router.push来控制路由页面的跳转，比如跳转到About组件页面。

```javascript
this.$router.push('/about')

```

这个跳转等同于点击页面上的router-link链接。

```javascript
<router-link :to="/about">跳转到About</router-link>

```

有时跳转到下一个页面需要带上一些信息，比如搜索关键词等，就需要跳转时链接带上参数，就像后面这样。

```javascript
this.$router.push({ path: '/about', query: { keyword: '二次元美少女' } })

```

在HTML代码中我们想要实现参数的传值，就直接通过标签来实现，后面是具体的实现代码。

```javascript
<router-link :to="{ name: 'About', query: { keyword: '二次元美少女' }}">
  跳转到About
</router-link>

```

这样，跳转到About组件时链接上就会带上参数 “keyword=二次元美少女”。也就是说，地址本来是 “localhost:8080/about”，带上参数后是 “localhost:8080/about?keyword=二次元美少女”。那么在About组件页，我们可以通过route.query来获得当前页面链接上的参数。

```javascript
this.$route.query.keyword  //-->'二次元美少女'

```

有一些隐秘的信息不想在链接上展示，那么可以跳转时给组件传参数。

```javascript
// 命名的路由，并加上参数，让路由建立 url
this.$router.push({ name: 'user', params: { username: 'eduardo' } })

```

那我们就可以在HTML代码块中直接用后面这种方式来实现。

```javascript
<router-link :to="{ name: 'user', params: { username: 'eduardo' }}">
  User
</router-link>

```

name是组件的名字，params是要给组件传的参数对。这两种方式是同样的效果，跳转到user组件页，并且带着参数username=‘eduardo’。

在user组件页，我们可以使用router.params来取到路由带来的参数，这样当我们需要通过一些字段做数据处理或接口请求时，就可以直接使用传递的值。

```javascript
this.$router.params.username  //-->eduardo

```

2.回到上一页

对于回到上一页的应用，在项目中也经常用到，比如这样的场景：提交完表单，我们需要回到列表页或者首页。

那么这个功能在代码中应该如何控制呢？你可以通过下面的代码来实现，这样就实现回到上一页的功能。

```javascript
this.$router.go(-1)

```

以此类推，如果想要回到上一页的上一页的代码就是后面这样。

```javascript
this.$router.go(-2)

```

3.组件的路由钩子函数

第四节课我们学习过Vue组件在生命周期中的钩子函数，现在我们再来学习跟路由相关的两个常用钩子函数。

如果我们在进入页面前，有一些要处理的操作（比如重置缓存），就要用到beforeRouteEnter函数。需要注意此时组件实例还没被创建，不能通过this访问组件实例。后面是具体代码示例。

```javascript
<template>
<div id="MyComponent"></div>
</template>
<script>
export default {
    name: 'MyComponent',
    data(){
    //这里定义数据
      return{
        ......
      }
  },
  methods:{
    //这里定义方法
    ......
  },
  beforeRouteEnter(to, from) {
    // 在渲染该组件的对应路由被验证前调用
    // 不能获取组件实例 `this`
    // 因为当守卫执行时，组件实例还没被创建
  }
}
</script>

```

相应地，在离开页面前，有一些要处理的操作，比如我们希望用户在离开页面之前收到一个“确定要离开么”的弹窗。这种情况就会用到beforeRouteLeave函数。

此时组件实例已经被创建，可以通过this访问组件实例。代码是后面这样。

```javascript
beforeRouteLeave(to, from) {
    // 在导航离开渲染该组件的对应路由时调用
    // 可以访问组件实例 `this`
 }

```

4.全局路由钩子函数

除了进入页面和离开页面的钩子函数，还有一个比较重要的钩子函数——全局函数。它定义在Vue Router的配置文件里，也就是刚刚我们建的src/router/index.js ，对所有路由页面都生效。

比如跳转页面之前需要查看当前用户是否已经登陆，如果没有登陆要重定向到登陆页。这时就会用到router.beforeEach。

```javascript
router.beforeEach(async (to, from) => {
   if (
     // 检查用户是否已登陆
     !isAuthenticated &&
     // 避免无限重定向
     to.name !== 'Login'
   ) {
     // 将用户重定向到登陆页面
     return { name: 'Login' }
   }
 })

```

而当我们想要统计页面访问数量时，就可以使用router.afterEach钩子函数。显然，这个函数要在路由跳转之后调用。

```javascript
router.afterEach((to, from) => {
  //do something
})

```

到这里，Vue Router的核心知识我们就梳理好了。但纸上得来终觉浅，绝知此事要躬行。接下来我们在真正的项目中，体会一下它们都是如何应用的。

## 视频平台中如何使用Vue Router

首先我们来梳理一下，视频平台中都有哪些页面。

- 首页
- 登陆
- 注册
- 视频列表
- 视频详情
- 视频发布
- 个人中心
- 创作中心
- 数据中心
- 我的资料

在这里我们需要考虑一个问题：因为我们大部分的页面都使用相同的Header，为了减少重复工作。我们需要将Header和Footer写成公共组件。展示效果是后面这样。

![](https://static001.geekbang.org/resource/image/09/51/09969fa83abdbb1c3c0bd8e7d93f4f51.jpg?wh=2619x1003)

![](https://static001.geekbang.org/resource/image/a5/52/a5f3b10466b5605eaea7b090a29a1752.jpg?wh=2923x989)

接下来，我们把Header和Footer定义成组件，然后定义一个模版，让其他内容根据路由地址展示在中间。

这时候我们就需要使用标签来实现，后面是对应的实现代码。

```javascript
<template>
  <div class="layout">
    <my-header ref="myheader"></my-header>
    <div class="content">
      <router-view ref="child"></router-view>
    </div>
    <my-footer></my-footer>
  </div>
</template>

<script>
import MyHeader from '@/components/PC/MyHeader';
import MyFooter from '@/components/PC/MyFooter';
export default {
  name: 'Layout',
  components: { MyHeader, MyFooter },
  data() {
    return {};
  },
  mounted(){}
};
</script>

<style lang="less" scoped>
.content {
  min-height: calc(100vh - 140px);
  background: #fff;
}
</style>

```

接下来，我们需要打开src/router/index.js配置路由。

大部分组件都要用到公用的Header和Footer，并显示在Layout组件下，所以我们把Layout组件配置在router中，也就是头部第一个组件。之后我们把其他页面的路由统一写在Layout的children里。

具体的代码形式是后面这样，你可以清晰地看到它们的层级关系。到这里，我们就实现了项目的路由配置管理代码。

```javascript
import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
() => import('./views/UserDetails.vue')
const router = new Router({
  routes: [{
    path: '/',
    name: 'Layout',
    component: resolve => require([`@/pages/Layout/Layout`], resolve),
    children: [
      //首页
      {
        path: '/',
        name: 'Index',
        component: resolve => require([`@/pages/Index/Index`], resolve)
      }, {
        path: '/login',
        alias: '/register',
        name: 'Wrapper',
        component: resolve => require([`@/pages/Login/Wrapper`], resolve),
        //登陆页
        children: [{
            path: '/login',
            name: 'Login',
            component: resolve => require([`@/pages/Login/Login`], resolve)
          },
          //注册页
          {
            path: '/register',
            name: 'Register',
            component: resolve => require([`@/pages/Login/Register`], resolve)
          }
        ]
      },
      //视频列表页
      {
        path: '/video/list/:tag',
        name: 'VideoList',
        component: resolve => require([`@/pages/Video/VideoList`], resolve)
      },
      //视频搜索页
      {
        path: '/video/search/:keyword',
        name: 'VideoList',
        component: resolve => require([`@/pages/Video/VideoList`], resolve)
      },
      //视频详情页
      {
        path: '/video/detail/:id',
        name: 'VideoDetail',
        component: resolve => require([`@/pages/Video/VideoDetail`], resolve)
      },
      //视频发布页
      {
        path: '/video/publish',
        name: 'VideoPublish',
        component: resolve => require([`@/pages/Video/VideoPublish`], resolve)
      },
      //视频编辑页
      {
        path: '/video/edit/:id',
        name: 'VideoPublish',
        component: resolve => require([`@/pages/Video/VideoPublish`], resolve)
      },
      //作品列表页
      {
        path: '/home/admin',
        name: 'Admin',
        component: resolve => require([`@/pages/Home/Admin`], resolve)
      },
      //个人资料页
      {
        path: '/home/info',
        name: 'Info',
        component: resolve => require([`@/pages/Home/Info`], resolve)
      },
      //数据中心页
      {
        path: '/home/data',
        name: 'Data',
        component: resolve => require([`@/pages/Home/Data`], resolve)
      },
      //消息通知页
      {
        path: '/home/message/:id',
        name: 'Message',
        component: resolve => require([`@/pages/Home/Message`], resolve)
      },
      //个人中心页
      {
        path: '/home/:id',
        name: 'Home',
        component: resolve => require([`@/pages/Home/Home`], resolve)
      }
    ]
  }]
})

export default router;

```

到这里，我们就完成了路由配置。怎么验证配置成功了呢？你可以跟着后面的操作来直观感受下。

我们首先启动项目，打开localhost:8080会显示首页。

![](https://static001.geekbang.org/resource/image/e1/b5/e1539d1bd4098059c5e5b8b59af552b5.jpg?wh=3183x1211)

然后点击右上角的登陆，就会跳转到登陆页。这里我们使用标签直接来实现，点击登陆，标签中的to属性表示目标路由的链接，有了它用户就会直接通过路由跳转进入login页面，标签里的“/login”就是对应的登陆页面的路由。

```javascript
<router-link to="/login">登陆</routerlink>

```

![](https://static001.geekbang.org/resource/image/30/58/301988fa2fe8cac0d41afd0a48159858.jpg?wh=3183x1431)

我们再来说说平台的登陆功能设计，在用户登陆成功之后，需要再次回到平台的首页，也就是我们刚访问过的路由，我们直接通过router.go(-1)的方法回到上一页。

```javascript
this.$router.go(-1)

```

![](https://static001.geekbang.org/resource/image/9a/a3/9a68b186f2a682419246485548cafda3.jpg?wh=3043x1820)

我们继续思考后面这个问题。在平台的首页，用户点击某一个视频，想要查看详情，应该如何来实现呢？

这时候我们只需要在用户点击视频的方法内调用router.push()，括号内放上对应的路由地址和需要传递的参数，就可以实现跳转了。具体的代码实现我放在下面。

```javascript
this.$router.push("/video/detail/" + video.id);

```

到这里，我们就实现了平台视频页到视频详情页的跳转，同时路由里也会携带上视频的id（方便我们通过id查询相关信息）。这时，对应的路由呈现就会变成“localhost:8080/#/video/detail/10001”，具体呈现方式你可以参考后面的截图。

![](https://static001.geekbang.org/resource/image/1e/4b/1e5b9585511192a27d154d0117956f4b.jpg?wh=2834x1820)

点击Header右上角的用户头像，这里我们如果提前放置了与用户相关的菜单，点击头像就可以直接显示菜单详情。

这里的路由跳转非常多，那这一部分我们该如何实现呢？具体的界面效果我也放在了下面。

![](https://static001.geekbang.org/resource/image/5c/c8/5c28a55007ddd40abce35c9cbe16e9c8.jpg?wh=2834x1678)

不难发现，这里每一个菜单都有点击事件，例如我们想要跳转到个人中心页面，这时候点击个人中心就需要调用router.push()方法实现页面跳转，代码如下。

```javascript
this.$router.push("/home/" + user.userId);

```

以此类推，都可以通过上面的代码实现路由的跳转和参数的传递，当然，如果我们想要获取用户的资料，我们就必须要先知道用户id是什么，通过id我们才能进行数据的查询，这时候对于传递值的获取，我们可以通过router.params获取当前页面组件的参数id（用户的id）。

```javascript
this.$router.params.id

```

掌握了以上的方法，你想要实现路由的跳转，还有值的传递就非常简单了，在项目中你都可以通过这样的方式来实现，可以看到我们通过路由管理，实现了项目中一系列页面的地址和展示组件的配置和页面之间的相互跳转，这样我们在后面的项目开发就能更加快捷。

## 总结

课程到了这里又即将进入尾声了，让我们回顾一下这节课的学习重点。

首先我们初识Vue Router组件，了解了Vue Router是什么和两个核心标签。这里重点要理解这两个标签的应用场景：点击页面标签跳转就用<router-link>；页面上有某一部分要根据地址栏地址变化而变化，此时就用<router-view>。

然后我们学习了如何把Vue Router整合到Vue框架里。这里课后同学们可以新建Vue项目加强练习，按照这四个步骤给Vue项目配置路由。

接下来，我们学习了Vue Router的核心知识和API。这里重点是我们能够根据不一样的场景、需求来配置路由，并且能在组件中运用API来控制路由。

最后的环节是平台路由的管理配置实战，路由跳转有多种方式，路由传值与值的获取也经常用到。只要完全理解了文化社区平台这个项目的路由配置，换成其他项目也是一样的，相信你可以举一反三。

通过今天的学习，我们已经可以自己为Vue项目做路由配置了，是不是收获满满呢？学无止境，课后一定要多学多练，可以自己建几个Vue简单的页面，用路由管理起来，在浏览器分别访问它们。另外，你也可以查看 [Vue Router 官网](https://router.vuejs.org/zh/) 文档，学习更多Router的相关知识。

## 思考题

这节课我们在Vue框架中整合了Vue Router，整合其他依赖也是同样的道理。你可以尝试整合一下Vue常用的UI组件库Element-UI。

提示： [Element-UI官网](https://element.eleme.io/#/)

欢迎你在留言区和我交流互动，也推荐你把这节课分享给更多的朋友。