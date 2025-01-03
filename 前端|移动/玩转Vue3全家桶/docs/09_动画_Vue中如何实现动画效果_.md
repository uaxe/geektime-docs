你好，我是大圣。

在上一讲中，我给你讲解了组件化设计的思路，有了组件，我们就可以积木式地搭建网页了。领会组件设计的思路后，小圣继续丰富了清单组件的功能，在组件的功能实现完毕后，我给他提出了一个新的要求，希望能有一些动画效果的加入，让这个应用显得不再这么生硬。

小圣自己琢磨以后，又找过来咨询我Vue 3中实现动画的方式，所以今天我就来跟你聊一下Vue中应该如何实现常见的过渡和动效。在讲解过程中，我们会继续给之前那个清单应用添砖加瓦，给它添加更多酷炫的玩法，让我们正式开始今天的学习吧。

## 前端过渡和动效

在讲Vue中的动效和过渡之前，我想先跟你聊一下前端的过渡和动效的实现方式。举个例子，假设我现在有这样一个需求：在页面上要有一个div标签，以及一个按钮，点击页面的按钮后，能够让div标签的宽度得到增加。

在下面的代码中，我们可以实现上面所说的这个效果。这段代码里，首先是一个div标签，我们使用width控制宽度。我们想要的前端效果是，每次点击按钮的时候，div标签的宽度都增加100px。

```xml
<template>

  <div class="box" :style="{width:width+'px'}"></div>
  <button @click="change">click</button>
</template>

<script setup>
import {ref} from 'vue'
let width= ref(100)
function change(){
  width.value += 100
}
</script>

<style>
.box{
  background:red;
  height:100px;
}
</style>

```

这个功能实现的效果图如下，小圣虽然实现了需求中提到的功能，但是现在的显示效果很生硬，这点你从下面的动态效果图中也能看出来。

![图片](https://static001.geekbang.org/resource/image/0a/ef/0a52318a2a136bebbe711a70e5b2f0ef.gif?wh=991x310)

为了优化显示的效果，首先我们可以通过一个CSS的属性transition来实现过渡，实现方式非常简单，直接在div的样式里加上一个transition配置就可以了。下面是具体的实现，其中我们给transition配置了三个参数，简单解释呢，就是div的width属性需要过渡，过渡时间是1秒，并且过渡方式是线性过渡。

```xml
<style>
.box{
  background:#d88986;
  height:100px;
  transition: width 1s linear;
}
</style>

```

添加上述transition配置后，前端页面会显示如下的过渡效果，是不是流畅了一些呢？实际上，日常项目开发中类似的过渡效果是很常见的。

![图片](https://static001.geekbang.org/resource/image/dd/e4/dd5bcf6e3dbcb4bd84f97093bc0a08e4.gif?wh=991x310)

现在你能看到， **我们可以通过transition来控制一个元素的属性的值，缓慢地变成另外一个值，这种操作就称之为过渡**。除了transition，我们还可以通过animation和keyframe的组合实现动画。

在下面的代码中，我们指定标签的antimation配置，给标签设置move动画，持续时间为两秒，线性变化并且无限循环。然后使用@keyframes 定制move动画，内部定义了动画0%、50%和100%的位置，最终实现了一个方块循环移动的效果。

```xml
.box1{
  width:30px;
  height:30px;
  position: relative;
  background:#d88986;
  animation: move 2s linear infinite;
}
@keyframes move {
  0% {left:0px}
  50% {left:200px}
  100% {left:0}
}

```

上面代码的实现效果如下：

![图片](https://static001.geekbang.org/resource/image/8c/20/8c070a460f13cb979cc393b55ac6a420.gif?wh=991x310)

这就是实现前端动画最简单的方式了，在网页应用开发的场景下，或多或少都会有过渡动画的使用需求。从最基本的颜色和位置的渐变，到页面切换都是动画的应用场景，这些动画在视觉和心理的体验上更加友好，比如等待时间的Loading加载提示，弹窗出现的显示动画等。

## Vue 3动画入门

通常我们实现的动画，会给Web应用带来额外的价值。动画和过渡可以增加用户体验的舒适度，让变化更加自然，并且可以吸引用户的注意力，突出重点。transition和animation让我们可以用非常简单的方式实现动画。那么在Vue 3中，我们到底该如何使用动画呢？

Vue 3中提供了一些动画的封装，使用内置的transition组件来控制组件的动画。为了让你先有一个感性的认识，这里我们先来举一个最简单的例子：我们可以使用一个按钮控制标题文字的显示和隐藏，具体的代码如下，通过点击按钮，就可以控制h1标签的显示和隐藏。

```xml
<template>

  <button @click="toggle">click</button>
  <h1 v-if="showTitle">你好 Vue 3</h1>
</template>

<script setup>
import {ref} from 'vue'
let showTitle = ref(true)
function toggle(){
  showTitle.value = !showTitle.value
}
</script>

```

在Vue中，如果我们想要在显示和隐藏标题文字的时候，加入动效进行过渡，那么我们直接使用transition组件包裹住需要动画的元素就可以了。

在下面代码中，我们使用transition包裹h1标签，并且设置了name为fade，Vue会在h1标签显示和隐藏的过程中去设置标签的class，我们可以根据这些class去实现想要的动效。

```xml
  <transition name="fade">
    <h1 v-if="showTitle">你好 Vue 3</h1>
  </transition>

```

具体class的名字，Vue 的官网有一个图给出了很好的解释，图里的v-enter-from中的v，就是我们设置的name属性。所以在我们现在这个案例中，标签在进入和离开的时候，会有fade-enter-active和fade-leave-active的class，进入的开始和结束会有fade-enter-from和face-enter-to两个class。

![图片](https://static001.geekbang.org/resource/image/71/92/718a6019316ed75f6d040e4983957692.png?wh=1920x866)

根据上图所示的原理，我们在style标签中新增如下代码，通过fade-enter-active和fade-leave-active两个class，去控制动画全程的过渡属性。设置opacity有0.5秒的过渡时间，并且在元素进入前和离开后设置opacity为0。

```xml
<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s linear;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

```

通过对元素进入和离开的过渡设置，我们可以实现如下动画：

![图片](https://static001.geekbang.org/resource/image/af/e0/afeed23b2f92cac24de8b83fe3df80e0.gif?wh=460x290)

## 清单应用优化

现在，我们通过学到的动画原理，去优化一下第二讲的清单应用。我们先来了解一下操作的场景，在原先清单应用已有的交互下，有一个交互的优化，我们想对交互再增加一个优化项。具体来说，就是当输入框为空的时候，敲击回车需要弹出一个错误的提示。

小圣同学对Composition API已经非常熟悉了，很快速地写下了下面的代码。小圣在代码的template中新增了一个显示错误消息的div，设置为绝对定位，通过showModal变量控制显示和隐藏。并且在addTodo函数中，如果title.value为空，也就是用户输入为空的时候，就设置showModal为true。这时，如果用户敲击回车，就会显示弹窗，并且定时关闭。

```xml
<template>
...清单代码
  <div class="info-wrapper" v-if="showModal">
    <div class="info">
      哥，你啥也没输入！
    </div>
  </div>
</template>

<script setup>
...清单功能代码
  let showModal = ref(false)

  function addTodo() {
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
</script>
<style>
.info-wrapper {
  position: fixed;
  top: 20px;
  width:200px;
}
.info {
  padding: 20px;
  color: white;
  background: #d88986;
}
</style>

```

新增交互后的前端显示效果如下，敲击回车后，如果输入为空，就会显示错误信息的弹窗。

![图片](https://static001.geekbang.org/resource/image/60/47/60aea2a58ccb29ca0676189dfd3b9d47.gif?wh=646x463)

功能虽然实现了，但是我们想进一步提高弹窗的交互效果，也就是弹窗的显示需要新增动画。对于这个需求，我们在直接使用transition包裹弹窗之后，设置对应进入和离开的CSS样式就可以了。首先，我们给transition动画设置name为modal，在style中通过对model对应的CSS设置过渡效果后，就给弹窗增加了弹窗的效果。

```xml
<transition name="modal">
  <div class="info-wrapper" v-if="showModal">
    <div class="info">
      哥，你啥也没输入！
    </div>
   </div>
</transition>

<style>
  .modal-enter-from {
    opacity: 0;
    transform: translateY(-60px);
  }
  .modal-enter-active {
    transition: all 0.3s ease;
  }
  .modal-leave-to {
    opacity: 0;
    transform: translateY(-60px);
  }
  .modal-leave-active {
    transition: all 0.3s ease;
  }
</style>

```

通过上面的代码，我们可以进行过渡效果的优化。优化后，前端页面的显示效果如下，可以看到弹窗有一个明显的滑入和划出的过渡效果。

![图片](https://static001.geekbang.org/resource/image/1d/b4/1ddf1492ebddce584eac161e65d49bb4.gif?wh=646x463)

## 列表动画

学了transition组件后，小圣兴致勃勃地把清单应用的列表也做了动画显示，但是现在清单列表并不是一个单独的标签，而是v-for渲染的列表元素，所以小圣就来找我求助，问我怎么实现列表项依次动画出现的效果。

在Vue中，我们把这种需求称之为列表过渡。因为transition组件会把子元素作为一个整体同时去过渡，所以我们需要一个新的内置组件transition-group。在v-for渲染列表的场景之下，我们使用transition-group组件去包裹元素，通过tag属性去指定渲染一个元素。

此外，transition-group组件还有一个特殊之处，就是不仅可以进入和离开动画，还可以改变定位。就和之前的类名一样，这个功能新增了v-move类，在下面的代码中，使用transition-group包裹渲染的li元素，并且设置动画的name属性为flip-list。然后我们根据v-move的命名规范，设置 `.flip-list-move` 的过渡属性，就实现了列表依次出现的效果了。

```xml
    <ul v-if="todos.length">
      <transition-group name="flip-list" tag="ul">
        <li v-for="todo in todos" :key="todo.title">
          <input type="checkbox" v-model="todo.done" />
          <span :class="{ done: todo.done }"> {{ todo.title }}</span>
        </li>
      </transition-group>

    </ul>
<style>
.flip-list-move {
  transition: transform 0.8s ease;
}
.flip-list-enter-active,
.flip-list-leave-active {
  transition: all 1s ease;
}
.flip-list-enter-from,
.flip-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>

```

通过上面的代码，我们就可以得到如下的实现效果。你可以看到，在新增列表和显示错误信息的弹窗上，都设置了过渡和动画。

## ![图片](https://static001.geekbang.org/resource/image/0b/a7/0b68e2ec1b617461f198094bd643aea7.gif?wh=646x463)

## 页面切换动画

对于一般的前端页面应用来说，还有一个常见的动画切换的场景，就是在页面切换这个场景时的动画。 **这个动画切换场景的核心原理和弹窗动画是一样的，都是通过transition标签控制页面进入和离开的class**。

现在默认是在vue-router的模式下，我们使用router-view组件进行动态的组件渲染。在路由发生变化的时候，我们计算出对应匹配的组件去填充router-view。

如果要在路由组件上使用转场，并且对导航进行动画处理，你就需要使用v-slot API。我们来到src/App.vue组件中，因为之前router-view没有子元素，所以我们要对代码进行修改。

在下面的代码中，router-view通过v-slot获取渲染的组件并且赋值给Component，然后使用transition 包裹需要渲染的组件，并且通过内置组件component的is属性动态渲染组件。这里vue-router的动画切换效果算是抛砖引玉，关于vue-router进阶的适用内容，全家桶实战篇后面的几讲还会继续深入剖析。

```xml
<router-view v-slot="{ Component }">
  <transition  name="route" mode="out-in">
    <component :is="Component" />
  </transition>
</router-view>

```

## JavaScript动画

在前端的大部分交互场景中，动画的主要目的是提高交互体验，CSS动画足以应对大部分场景。但如果碰见比较复杂的动画场景，就需要用JavaScript来实现，比如购物车、地图等场景。

在下面的代码中，我们首先在清单应用中加上一个删除事项的功能，当点击删除图标来删除清单的时候，可以直接删除一行。

```xml
<template>

    ...清单应用其他代码

      <transition-group name="flip-list" tag="ul">
        <li v-for="(todo,i) in todos" :key="todo.title">
          <input type="checkbox" v-model="todo.done" />
          <span :class="{ done: todo.done }"> {{ todo.title }}</span>
          <span class="remove-btn" @click="removeTodo($event,i)">
            ❌
          </span>
        </li>
      </transition-group>
</template>
<script>
  function removeTodo(e,i){
    todos.value.splice(i,1)
  }
</script>

```

通过上面的代码，我们能实现下面所示的效果：

![图片](https://static001.geekbang.org/resource/image/5a/b2/5afba5a388f940995c39de50d04f7fb2.gif?wh=661x381)

如果我们想在删除的时候，实现一个图标飞到废纸篓的动画，那么在这个场景下，使用单纯的CSS动画就不好实现了，我们需要引入JavaScript来实现动画。实现的思路也很简单，我们放一个单独存在的动画元素并且藏起来，当点击删除图标的时候，我们把这个动画元素移动到鼠标的位置，再飞到废纸篓里藏起来就可以了。

具体怎么做呢？ 在Vue的transition组件里，我们可以分别设置before-enter，enter和after-enter三个函数来更精确地控制动画。

在下面的代码中，我们首先定义了animate响应式对象来控制动画元素的显示和隐藏，并且用transition标签包裹动画元素。在beforeEnter函数中，通过getBoundingClientRect函数获取鼠标的点击位置，让动画元素通过translate属性移动到鼠标所在位置；并且在enter钩子中，把动画元素移动到初始位置，在afterEnter中，也就是动画结束后，把动画元素再隐藏起来，这样就实现了类似购物车的飞入效果。

```xml
<template>
    <span class="dustbin">
      🗑
    </span>
<div class="animate-wrap">
    <transition @before-enter="beforeEnter" @enter="enter" @after-enter="afterEnter">
        <div class="animate" v-show="animate.show">
            📋
        </div>
    </transition>
</div>
</template>

<script setup>

let animate = reactive({
  show:false,
  el:null
})
function beforeEnter(el){
      let dom = animate.el
      let rect = dom.getBoundingClientRect()
      let x = window.innerWidth - rect.left - 60
      let y = rect.top - 10
      el.style.transform = `translate(-${x}px, ${y}px)`
}
function enter(el,done){
      document.body.offsetHeight
      el.style.transform = `translate(0,0)`
      el.addEventListener('transitionend', done)
}
function afterEnter(el){
      animate.show = false
      el.style.display = 'none'
}
function removeTodo(e,i){
  animate.el = e.target
  animate.show = true
  todos.value.splice(i,1)
}
</script>
<style>
.animate-wrap .animate{
    position :fixed;
    right :10px;
    top :10px;
    z-index: 100;
    transition: all 0.5s linear;
}
</style>

```

上面代码的显示效果如下，我们点击删除后，除了列表本身的动画移出效果，还多了一个飞入废纸篓的效果。你能看到，在引入JavaScript后，我们可以实现更多定制的动画效果。

## ![图片](https://static001.geekbang.org/resource/image/0d/00/0da30b53ee409874259965d0a86d4400.gif?wh=661x381)

## 总结

今天这一讲的主要内容讲完了，我们来简单复习一下今天学到的知识点。

首先我们学习了前端使用CSS实现简单动画的transition和animation两个配置；然后，我们了解到了通过Vue 3提供的transition组件，我们可以控制在Vue中动画元素进入和离开页面时候的class；通过制定的命名规范，在CSS中设置过渡和动画效果，从而很方便地实现过渡效果，并且丰富了清单应用的弹窗功能；在这之后，我们使用transition-group实现列表元素的动画；最后，我还带你了解了vue-router中页面切换动画的实现方式。

相信学完今天这一讲，你会对Vue 3中实现简单动画的方式有所领会。今天我们实现的动画功能其实是Vue中动画的入门实战，所以我特意带你体验了全套玩法。不过你需要注意的是，实际开发中动画也不是越多越好，动画的设计也需要设计师去系统地设计效果，不要用动画做出眼花缭乱的网页。

而且，实际开发中如果想实现更复杂的动画，比如常见电商中商品飞入购物车的效果，管理系统中丰富的动画效果等，只借助transition组件是很难实现的。你需要借助JavaScript和第三方库的支持，在beforeEnter、enter、afterEnter等函数中实现动画。

## 思考题

关于今天设计的弹窗动画，如果想实现一个振动的效果，该如何实现呢？

欢迎在留言区留言讨论，也欢迎你把这一讲推荐给你的朋友、同事。我们下一讲见！