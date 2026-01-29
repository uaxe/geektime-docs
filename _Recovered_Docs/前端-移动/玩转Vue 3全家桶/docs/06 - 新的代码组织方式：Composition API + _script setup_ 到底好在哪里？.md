你好，我是大圣，欢迎进入课程的第六讲。

在上一讲中，我带你搭建了项目的雏形，这是后面项目开发的起点。从今天开始，我就带你在这个骨架结构的基础之上，开始项目的实战开发。首先我们要掌握的，就是 Vue 3 的Composition API + &lt;script setup&gt;这种最新的代码组织方式。

![](https://static001.geekbang.org/resource/image/6f/0a/6fd86f3d33a0200d64c7423bc88e890a.png?wh=1222x432)

我们在前面的第三讲中，有详细地讲到过 Composition API ，相信你对这个API 的语法细节已经有所掌握了。那你肯定会很好奇，这个&lt;script setup&gt;又是什么？为什么尤雨溪要在微博上强推&lt;script setup&gt;呢？

别急，今天我就带你使用Composition API 和 &lt;script setup&gt; 去重构第二讲的清单应用。在重构的过程中，你能逐渐明白，**Composition API 可以让我们更好地组织代码结构**，而让你感到好奇的 &lt;script setup&gt;本质上是以一种更精简的方式来书写Composition API 。

## Composition API 和 &lt;script setup&gt; 上手

首先我想提醒你，我们在这一讲中写代码的方式，就和前面的第二讲有很大的区别。

在第二讲中，我们开发清单应用时，是直接在浏览器里使用 Options API 的方式写代码；但在接下来的开发中，我们会直接用单文件组件——也就是 `.vue` 文件，的开发方式。这种文件格式允许我们把 Vue 组件的HTML、CSS和JavaScript写在单个文件内容中。下面我带你用单文件组件的方式，去重构第二讲做的清单应用。

我们现在已经搭建好了项目的骨架，以后在这个骨架之内会有很多页面和组件。从这里开始，我们就要逐步适应组件化的开发思路，新的功能会以组件的方式来组织。

按照上一讲制定的规范，首先，我们打开项目文件夹下面的src下的components目录，新建一个Todolist.vue ，并在这个文件里写出下面的代码：

```xml
<template>
  <div>
    <h1 @click="add">{{count}}</h1>
  </div>
</template>

<script setup>
import { ref } from "vue";
let count = ref(1)
function add(){
    count.value++
}
</script>

<style>
h1 {
  color: red;
}
</style>
```

在上述代码中，我们使用template标签放置模板、script 标签放置逻辑代码，并且用setup标记我们使用&lt;script setup&gt;的语法，style标签放置CSS样式。

从具体效果上看，这段代码实现了一个累加器。在 &lt;script setup&gt; 语法中，我们使用引入的ref函数包裹数字，返回的count变量就是响应式的数据，使用add函数实现数字的修改。需要注意的是，对于ref返回的响应式数据，我们需要修改 `.value` 才能生效，而在 &lt;script setup&gt; 标签内定义的变量和函数，都可以在模板中直接使用。

实现累加器以后，我们再回到src/pages/Home.vue 组件中，使用如下代码显示清单应用。在这段代码里，我们直接import TodoList.vue组件，然后&lt;script setup&gt;会自动把组件注册到当前组件，这样我们就可以直接在template中使用 来显示清单的功能。

```xml
<template>
    <h1>这是首页</h1>
    <TodoList />    
</template>

<script setup>
import TodoList from '../components/TodoList.vue'
</script>
```

这个时候我们就把清单功能独立出来了，可以在任意你需要的地方复用。在课程的后续内容中，我会详细给你介绍基于组件去搭建应用的方式。**通过这种方式，你可以实现对业务逻辑的复用。这样做的好处就是，如果有其他页面也需要用到这个功能，可以直接复用过去。**

然后，我们就可以基于新的语法实现之前的清单应用。下面的代码就是把之前的代码移植过来后，使用ref包裹的响应式数据。在你修改title和todos的时候，注意要修改响应式数据的value属性。

```xml
<template>
  <div>
    <input type="text" v-model="title" @keydown.enter="addTodo" />
    <ul v-if="todos.length">
      <li v-for="todo in todos">
        <input type="checkbox" v-model="todo.done" />
        <span :class="{ done: todo.done }"> {{ todo.title }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from "vue";
let title = ref("");
let todos = ref([{title:'学习Vue',done:false}])

function addTodo() {
  todos.value.push({
    title: title.value,
    done: false,
  });
  title.value = "";
}
</script>
```

## 计算属性

在第二讲开发的清单应用中，我们也用到了计算属性，在Composition API的语法中，计算属性和生命周期等功能，都可以脱离Vue的组件机制单独使用 。我们向TodoList.vue代码块中加入下面的代码：

```xml
<template>
  <div>
    <input type="text" v-model="title" @keydown.enter="addTodo" />
    <button v-if="active < all" @click="clear">清理</button>
    <ul v-if="todos.length">
      <li v-for="todo in todos">
        <input type="checkbox" v-model="todo.done" />
        <span :class="{ done: todo.done }"> {{ todo.title }}</span>
      </li>
    </ul>
    <div v-else>暂无数据</div>
    <div>
      全选<input type="checkbox" v-model="allDone" />
      <span> {{ active }} / {{ all }} </span>
    </div>
  </div>
</template>

<script setup>
import { ref,computed } from "vue";
let title = ref("");
let todos = ref([{title:'学习Vue',done:false}])

function addTodo() {
...
}
function clear() {
  todos.value = todos.value.filter((v) => !v.done);
}
let active = computed(() => {
  return todos.value.filter((v) => !v.done).length;
});
let all = computed(() => todos.value.length);
let allDone = computed({
  get: function () {
    return active.value === 0;
  },
  set: function (value) {
    todos.value.forEach((todo) => {
      todo.done = value;
    });
  },
});
</script>
```

在这这段代码中，具体的计算属性的逻辑和第二讲一样，区别仅在于computed的用法上。你能看到，第二讲的computed是组件的一个配置项，而这里的computed的用法是单独引入使用。

## Composition API 拆分代码

讲到这里，可能你就会意识到，之前的累加器和清单，虽然功能都很简单，但也属于两个功能模块。如果在一个页面里有这两个功能，那就需要在data和methods里分别进行配置。但这样的话，数据和方法相关的代码会写在一起，在组件代码行数多了以后就不好维护。**所以，我们需要使用Composition API 的逻辑来拆分代码，把一个功能相关的数据和方法都维护在一起。**

但是，所有功能代码都写在一起的话，也会带来一些问题：随着功能越来越复杂，script 内部的代码也会越来越多。因此，我们可以进一步对代码进行拆分，把功能独立的模块封装成一个独立的函数，真正做到按需拆分。

在下面，我们新建了一个函数 useTodos：

```xml
function useTodos() {
  let title = ref("");
  let todos = ref([{ title: "学习Vue", done: false }]);
  function addTodo() {
    todos.value.push({
      title: title.value,
      done: false,
    });
    title.value = "";
  }
  function clear() {
    todos.value = todos.value.filter((v) => !v.done);
  }
  let active = computed(() => {
    return todos.value.filter((v) => !v.done).length;
  });
  let all = computed(() => todos.value.length);
  let allDone = computed({
    get: function () {
      return active.value === 0;
    },
    set: function (value) {
      todos.value.forEach((todo) => {
        todo.done = value;
      });
    },
  });
  return { title, todos, addTodo, clear, active, all, allDone };
}
```

这个函数就是把那些和清单相关的所有数据和方法，都放在函数内部定义并且返回，这样这个函数就可以放在任意的地方来维护。

而我们的组件入口，也就是&lt;script setup&gt;中的代码，就可以变得非常简单和清爽了。在下面的代码中，我们只需要调用useTodos，并且获取所需要的变量即可，具体的实现逻辑可以去useTodos内部维护，代码可维护性大大增强。

```xml
<script setup>
import { ref, computed } from "vue";

let count = ref(1)
function add(){
    count.value++
}

let { title, todos, addTodo, clear, active, all, allDone } = useTodos();
</script>
```

我们在使用Composition API 拆分功能时，也就是执行useTodos的时候，ref、computed等功能都是从 Vue 中单独引入，而不是依赖this上下文。其实你可以把组件内部的任何一段代码，从组件文件里抽离出一个独立的文件进行维护。

现在，我们引入追踪鼠标位置的需求进行讲解，比如我们项目中可能有很多地方需要显示鼠标的坐标位置，那我们就可以在项目的src/utils文件夹下面新建一个mouse.js。我们先从 Vue 中引入所需要的ref函数，然后暴露一个函数，函数内部和上面封装的useTodos类似，不过这次独立成了文件，放在utils文件下独立维护，提供给项目的所有组件使用。

```xml
import {ref} from 'vue'

export function useMouse(){

    const x = ref(0)
    const y = ref(0)

    return {x, y}

}
```

想获取鼠标的位置，我们就需要监听mousemove事件。这需要在组件加载完毕后执行，在Composition API中，我们可以直接引入onMounted和onUnmounted来实现生命周期的功能。

看下面的代码，组件加载的时候，会触发onMounted生命周期，我们执行监听mousemove事件，从而去更新鼠标位置的x和y的值；组件卸载的时候，会触发onUnmounted生命周期，解除mousemove事件。

```xml


import {ref, onMounted,onUnmounted} from 'vue'

export function useMouse(){
    const x = ref(0)
    const y = ref(0)
    function update(e) {
      x.value = e.pageX
      y.value = e.pageY
    }
    onMounted(() => {
      window.addEventListener('mousemove', update)
    })
  
    onUnmounted(() => {
      window.removeEventListener('mousemove', update)
    })
    return { x, y }
}
```

完成了上面的鼠标事件封装这一步之后，我们在组件的入口就可以和普通函数一样使用useMouse函数。在下面的代码中，上面的代码返回的x和y的值可以在模板任意地方使用，也会随着鼠标的移动而改变数值。

```xml
import {useMouse} from '../utils/mouse'

let {x,y} = useMouse()
```

相信到这里，你一定能体会到 Composition API 对代码组织方式的好处。简单来看，**因为ref和computed等功能都可以从 Vue 中全局引入，所以我们就可以把组件进行任意颗粒度的拆分和组合**，这样就大大提高了代码的可维护性和复用性。

## &lt;script setup&gt; 好用的功能

Composition API 带来的好处你已经掌握了，而&lt;script setup&gt;是为了提高我们使用Composition API 的效率而存在的。我们还用累加器来举例，如果没有&lt;script setup&gt;，那么我们需要写出下面这样的代码来实现累加器。

```xml
<script >
import { ref } from "vue";
export default {
  setup() {
    let count = ref(1)
    function add() {
      count.value++
    }
    return {
      count,
      add
    }
  }
}
</script>
```

在上面的代码中，我们要在&lt;script&gt;中导出一个对象。我们在setup配置函数中写代码时，和Options的写法比，也多了两层嵌套。并且，我们还要在setup函数中，返回所有需要在模板中使用的变量和方法。上面的代码中，setup函数就返回了count和add。

**使用 &lt;script setup&gt; 可以让代码变得更加精简，这也是现在开发 Vue 3 项目必备的写法**。除了我们上面介绍的功能，&lt;script setup&gt;还有其它一些很好用的功能，比如能够使用顶层的await去请求后端的数据等等，我们会在后面的项目中看到这种使用方法。

## style样式的特性

除了script相关的配置，我也有必要给你介绍一下style样式的配置。比如，在style标签上，当我们加上scoped这个属性的时候，我们定义的CSS就只会应用到当前组件的元素上，这样就很好地避免了一些样式冲突的问题。

我们项目中的样式也可以加上如下标签：

```xml
<style scoped>
h1 {
  color: red;
}
</style>>
```

这样，组件就会解析成下面代码的样子。标签和样式的属性上，新增了data-的前缀，确保只在当前组件生效。

```xml
<h1 data-v-3de47834="">1</h1>
<style scoped>
h1[data-v-3de47834] {
    color: red;
}
</style>
```

如果在scoped内部，你还想写全局的样式，那么你可以用:global来标记，这样能确保你可以很灵活地组合你的样式代码（后面项目中用到的话，我还会结合实战进行讲解）。而且我们甚至可以通过v-bind函数，直接在CSS中使用JavaScript中的变量。

在下面这段代码中, 我在script里定义了一个响应式的color变量，并且在累加的时候，将变量随机修改为红或者蓝。在style内部，我们使用v-bind函数绑定color的值，就可以动态地通过JavaScript的变量实现CSS的样式修改，点击累加器的时候文本颜色会随机切换为红或者蓝。

```xml
<template>
  <div>
    <h1 @click="add">{{ count }}</h1>
  </div>
</template>

<script setup>
import { ref } from "vue";
let count = ref(1)
let color = ref('red')
function add() {
  count.value++
  color.value = Math.random()>0.5? "blue":"red"
}
</script>

<style scoped>
h1 {
  color:v-bind(color);
}
</style>>
```

点击累加器时文本颜色的切换效果，如下图所示：

![图片](https://static001.geekbang.org/resource/image/59/18/5974c0d7dbce32306bd2a207a6a37f18.gif?wh=343x105)

## 总结

我们来总结一下今天都学到了什么吧。今天的主要任务就是使用Composition API +&lt;script setup&gt;的语法复现第二讲的清单应用，我们首先通过累加器的例子介绍了ref这个函数的使用；之后我们讲到，在Composition API的语法中，所有的功能都是通过全局引入的方式使用的，并且通过&lt;script setup&gt;的功能，我们定义的变量、函数和引入的组件，都不需要额外的生命周期，就可以直接在模板中使用。

然后，我们通过把功能拆分成函数和文件的方式，掌握到Composition API组织代码的方式，我们可以任意拆分组件的功能，抽离出独立的工具函数，大大提高了代码的可维护性。

最后我们还学习了style标签的特殊属性，通过标记scoped可以让样式只在当前的组件内部生效，还可以通过v-bind函数来使用JavaScript中的变量去渲染样式，如果这个变量是响应式数据，就可以很方便地实现样式的切换。

相信学完今天这一讲，你一定会对我们为什么需要Composition API有更进一步的认识，而对于&lt;script setup&gt;来说，则可以帮助我们更好且更简洁的写Compostion的语法。在后面，我们的项目会全部使用Composition API + &lt;script setup&gt;来进行书写。

## 思考题

最后给你留一个思考题，Composition API 和 &lt;script setup&gt; 虽然能提高开发效率，但是带来的一些新的语法，比如ref返回的数据就需要修改 value属性；响应式和生命周期也需要import后才能使用等等，很多人也在社区批评这是 Vue 造的“方言” ，那你怎么看呢？

欢迎你在留言区分享你的想法，当然也推荐你把这一讲推荐给你自己的朋友、同事。我们下一讲见！
<div><strong>精选留言（15）</strong></div><ul>
<li><span>奇奇</span> 👍（15） 💬（3）<p>大圣，能不能搞一个 git 仓库来放每一讲的课程代码内容呢</p>2021-10-29</li><br/><li><span>ll</span> 👍（137） 💬（5）<p> 每节课都有很多收获！
  ✿ Options API vs Composition API
        字面上, 选项 API 与 组合 API，细品, 这反映了设计面向的改变：
        1. 选项，谁的选项，关键在“谁”。谁？组件。也是 Vue2.x 的设计基础。组件有什么，
           有状态，有改变状态的方法，有生命周期，还有组件和组件之间的关系。这种情况
           下，“数据”要接受一定的“规矩”，“什么时候能做什么事”，“什么时候有什么表现”；
           这个状态下，开发模式像是“被动接受”。

        2. 组合，什么组合，关键在“什么”。什么？数据。数据的组合。Vue3.x 设计重点变了，数
           据变绝对的C了，现在去组件里串门，不用“守规矩”了，只需要说“我在 onMounted 的时
           候要这样这样，你看着办”，真只能的以“数据”为中心，没人能管得了了，想去哪就去哪，
           自然就灵活了

        至于这些是怎么做到由“被动接受”到“主动告知”的，实现这部分内容，我很期待。

  ✿ 模板语法更好用
        &lt;script setup&gt; 像是“语法糖”，很甜；&lt;style&gt;里能用 v-bind，以后开发可以
        少用“黑科技”了，双手点赞。

  ✿ 至于思考题
        Vue 本来就属于 DSL，语法方面各有偏好，见仁见智；响应式和生命周期需要 import，个
        人认为就代表了从之前的“被动主动”转向“主动告知”，这样设计更加灵活。从此一条主线在
        ”数据&quot;，以后查 bug 顺着这条 &quot;线&quot; 应该更加容易了。</p>2021-10-29</li><br/><li><span>琼斯基亚</span> 👍（39） 💬（2）<p>对于value，官方是这样解释的：
将值封装在一个对象中，看似没有必要，但为了保持 JavaScript 中不同数据类型的行为统一，这是必须的。这是因为在 JavaScript 中，Number 或 String 等基本类型是通过值而非引用传递的：在任何值周围都有一个封装对象，这样我们就可以在整个应用中安全地传递它，而不必担心在某个地方失去它的响应性</p>2021-11-10</li><br/><li><span>ch3cknull</span> 👍（15） 💬（2）<p>关于导入问题，antfu大神有一个插件unplugin-auto-import，可以自动注入依赖项，不用import

https:&#47;&#47;github.com&#47;antfu&#47;unplugin-auto-import

.value问题貌似最新的ref语法糖可以算是一个解决方案，但是目前褒贬不一，我不推荐现在就用</p>2021-10-29</li><br/><li><span>王俊</span> 👍（15） 💬（6）<p>建议增加代码库，实时拉取更新，现在的代码片段看着比较麻烦</p>2021-10-29</li><br/><li><span>cwang</span> 👍（12） 💬（9）<p>谢谢大圣老师的讲解。其中清单应用中，独立出来的useTodos函数，放在了哪里进行维护？并且，在使用这个函数时：let { title, ……} = useTodos() ，是不是还要对它进行一个引用？谢谢。</p>2021-10-29</li><br/><li><span>Geek_fcdf7b</span> 👍（9） 💬（1）<p>大圣老师，请教一下，3.2版本之后，是不是定义响应式数据都可以用ref一把梭？我看有的文章是这样说的，ref在3.2之后性能进行了大幅度提升，所以建议使用ref，不管简单数据还是复杂数据都可以用ref，没必要用reactive</p>2021-12-08</li><br/><li><span>凌旭</span> 👍（9） 💬（2）<p>1，Composition API +setup的写法，看起来是把vue2中属于单个组件的js代码和组件解耦了，这样可以高效复用到其他组件中，但随着业务代码的增对，这样抽离出来的js也会越来越多，到时的维护管理难度又会加大，虽然这样做杜绝了在template,script间的反复横跳，但是无法避免地需要在各个js文件中跳转呀。</p>2021-10-31</li><br/><li><span>超</span> 👍（7） 💬（6）<p>请问大圣，如果把useTodos单独抽成一个js文件，改js里的文件，浏览器界面不会自动热重载，有啥解决方法没？是改webpack的配置吗？</p>2021-10-29</li><br/><li><span>1⃣️</span> 👍（6） 💬（1）<p>ref的副作用也可以用$ref解决是什么意思？哪里能找到这个语法介绍吗？</p>2022-01-07</li><br/><li><span>特供版</span> 👍（5） 💬（2）<p>强烈建议听课前
过一遍vue3的文档先！
过一遍vue3的文档先！
过一遍vue3的文档先！
https:&#47;&#47;v3.cn.vuejs.org&#47;api&#47;
对老师的建议：稍微提一下setup(),再提&lt;script setup&gt;。要不然直接跳到语法糖，简直是一头雾水。
还有类似style的v-bind，如果是vue2没有的特性的话，希望也顺带提一嘴。

另外mac也有热更新的问题，最后把文件引用全部补全了（例如文件路径没有.js后缀等），莫名的就好使了。</p>2021-12-28</li><br/><li><span>月落梅影</span> 👍（4） 💬（1）<p>以前在极客时间上买了李兵老师浏览器相关的课程，现在再来看大圣老师的课，觉得差别还是挺大的，大圣老师的课程中，经常出现相信你一定怎样怎样，觉得缺乏一根主线。</p>2022-01-10</li><br/><li><span>流星的泪痕</span> 👍（3） 💬（1）<p>useTodos() 放到哪里去？上面的代码也没看到引用useTodos js相关文件。去查看了 https:&#47;&#47;github.com&#47;shengxinjing&#47;geektime-vue-course 代码里面好像也没有看到useTodos()这个函数</p>2021-12-13</li><br/><li><span>嘻哈</span> 👍（3） 💬（2）<p>感觉会 react学本节内容成本不高的</p>2021-10-29</li><br/><li><span>SjmBreadrain</span> 👍（2） 💬（1）<p>现在是setup 被 script setup 替代了？</p>2022-01-08</li><br/>
</ul>