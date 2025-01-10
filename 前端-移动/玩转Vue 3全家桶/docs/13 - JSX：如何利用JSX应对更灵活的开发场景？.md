你好，我是大圣。

在上一讲中，我给你介绍了如何使用Chrome和Vue Devtools来调试项目，相信你已经拥有了调试复杂项目的能力。今天，我们来聊一个相对独立的话题，就是Vue中的JSX。你肯定会有这样的疑惑，JSX不是React的知识点吗？怎么Vue里也有？

实际上，Vue中不仅有JSX，而且Vue还借助JSX发挥了Javascript动态化的优势。此外，Vue中的JSX在组件库、路由库这类开发场景中，也发挥着重要的作用。对你来说，学习JSX，可以让你实现更灵活的开发需求，这一讲我们重点关注一下Vue中的JSX。

## h函数

在聊JSX之前，我需要先给你简单介绍一下h函数，因为理解了h函数之后，你才能更好地理解JSX是什么。下面，我会通过一个小圣要实现的需求作为引入，来给你讲一下h函数。

在Vue 3的项目开发中，template是Vue 3默认的写法。虽然template长得很像HTML，但Vue其实会把template解析为render函数，之后，组件运行的时候通过render函数去返回虚拟DOM，你可以在Vue Devtools中看到组件编译之后的结果。

![图片](https://static001.geekbang.org/resource/image/75/af/75e3242df6e45538a6d43c5f0d39a1af.png?wh=1920x1140)

在上面的示意图中，调试窗口右侧代码中的\_sfc\_render\_函数就是清单应用的template解析成JavaScript之后的结果。所以除了template之外，在某些场景下，我们可以直接写render函数来实现组件。

先举个小例子，我给小圣模拟了这样一个需求：我们需要通过一个值的范围在数字1到6之间的变量，去渲染标题组件 h1~h6，并根据传递的props去渲染标签名。对于这个需求，小圣有点拿不准了，不知道怎么实现会更合适，于是小圣按照之前学习的template语法，写了很多的v-if：

```xml
  <h1 v-if="num==1">{{title}}</h1>
  <h2 v-if="num==2">{{title}}</h2>
  <h3 v-if="num==3">{{title}}</h3>
  <h4 v-if="num==4">{{title}}</h4>
  <h5 v-if="num==5">{{title}}</h5>
  <h6 v-if="num==6">{{title}}</h6>

```

从上面的代码中，你应该能感觉到，小圣这样的实现看起来太冗余。所以这里我教你一个新的实现方法，那就是Vue 3中的 [h函数](https://v3.cn.vuejs.org/api/global-api.html#h)。

由于render函数可以直接返回虚拟DOM，因而我们就不再需要template。我们在src/components目录下新建一个文件Heading.jsx ，要注意的是，这里Heading的结尾从.vue变成了jsx。

在下面的代码中, 我们使用defineComponent定义一个组件，组件内部配置了props和setup。这里的setup函数返回值是一个函数，就是我们所说的render函数。render函数返回h函数的执行结果，h函数的第一个参数就是标签名，我们可以很方便地使用字符串拼接的方式，实现和上面代码一样的需求。像这种连标签名都需要动态处理的场景，就需要通过手写h函数来实现 **。**

```javascript
import { defineComponent, h } from 'vue'

export default defineComponent({
  props: {
    level: {
      type: Number,
      required: true
    }
  },
  setup(props, { slots }) {
    return () => h(
      'h' + props.level, // 标签名
      {}, // prop 或 attribute
      slots.default() // 子节点
    )
  }
})

```

然后，在文件src/About.vue中，我们使用下面代码中的import语法来引入Heading，之后使用level传递标签的级别。这样，之后在浏览器里访问 [http://localhost:9094/#/about](http://localhost:9094/#/about) 时，就可以直接看到Heading组件渲染到浏览器之后的结果。

```xml
 <template>
  <Heading :level="3">hello geekbang</Heading>
</template>

<script setup>
import Heading from './components/Head.jsx'
</script>

```

上面的代码经过渲染后的结果如下：

## ![图片](https://static001.geekbang.org/resource/image/7a/e8/7a4d4901c4cc483977d6a423aa4e29e8.png?wh=1120x440)

手写的h函数，可以处理动态性更高的场景。 **但是如果是复杂的场景，h函数写起来就显得非常繁琐，需要自己把所有的属性都转变成对象**。并且组件嵌套的时候，对象也会变得非常复杂。不过，因为h函数也是返回虚拟DOM的，所以有没有更方便的方式去写h函数呢？答案是肯定的，这个方式就是JSX。

## JSX是什么

我们先来了解一下JSX是什么，JSX来源自React框架，下面这段代码就是JSX的语法，我们给变量title赋值了一个h1标签。

```javascript
const element = <h1 id="app">Hello, Geekbang!</h1>

```

**这种在JavaScript里面写HTML的语法，就叫做JSX**，算是对JavaScript语法的一个扩展。上面的代码直接在JavaScript环境中运行时，会报错。JSX的本质就是下面代码的语法糖，h函数内部也是调用createVnode来返回虚拟DOM。在之后的课程中，对于那些创建虚拟DOM的函数，我们统一称为h函数。

```javascript
const element = createVnode('h1',{id:"app"}, 'hello Geekbakg')

```

在从JSX到createVNode函数的转化过程中，我们需要安装一个JSX插件。在项目的根目录下，打开命令行，执行下面的代码来安装插件：

```bash
npm install @vitejs/plugin-vue-jsx -D

```

插件安装完成后，我们进入根目录下，打开vite.config.js文件去修改vite配置。在vite.config.js文件中，我们加入下面的代码。这样，在加载JSX插件后 ，现在的页面中就可以支持JSX插件了。

```javascript
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx';

export default defineConfig({
  plugins: [vue(),vueJsx()]
})

```

然后，我们进入src/componentns/Heading.jsx中，把setup函数的返回函数改成下面代码中所示的内容，这里我们使用变量tag计算出标签类型，直接使用渲染，使用一个大括号把默认插槽包起来就可以了。

```javascript
  setup(props, { slots }) {
    const tag = 'h'+props.level
    return () => <tag>{slots.default()}</tag>
  }

```

我们再来聊一下JSX的语法在实战中的要点，详细的要点其实在 [GitHub文档](https://github.com/vuejs/jsx-next/blob/dev/packages/babel-plugin-jsx/README-zh_CN.md) 中也有全面的介绍，我在这里主要针对之前的清单应用讲解一下。

我们进入到src/components下面新建文件Todo.jsx，在下面的代码中，我们使用JSX实现了一个简单版本的清单应用。我们首先使用defineComponent的方式来定义组件，在setup返回的JSX中，使用vModel取代v-model，并且使用单个大括号包裹的形式传入变量title.value ，然后使用onClick取代@click。循环渲染清单的时候，使用.map映射取代v-for，使用三元表达式取代v-if。

```javascript
import { defineComponent, ref } from 'vue'

export default defineComponent({
  setup(props) {
    let title = ref('')
    let todos = ref([{ title: "学习 Vue 3", done: true },{ title: "睡觉", done: false }]);
    function addTodo(){
        todos.value.push({
            title:title.value
        })
        title.value = ''
    }
    return () => <div>
        <input type="text" vModel={title.value} />
        <button onClick={addTodo}>click</button>
        <ul>
            {
                todos.value.length ? todos.value.map(todo=>{
                    return <li>{todo.title}</li>
                }): <li>no data</li>
            }
        </ul>
    </div>
  }
})

```

通过这个例子，你应该能够认识到， **使用JSX的本质，还是在写JavaScript**。在Element3组件库设计中，我们也有很多组件需要用到JSX，比如时间轴Timeline、分页Pagination、表格Table等等。

就像在TimeLine组件的 [源码](https://github.com/hug-sun/element3/blob/master/packages/element3/packages/timeline/Timeline.vue#L35) 中，有一个reverse的属性来决定是否倒序渲染，我们在下面写出了类似的代码。代码中的Timeline是一个数组，数组中的两个元素都是JSX，我们可以通过数组的reverse方法直接进行数组反转，实现逆序渲染。类似这种动态性要求很高的场景，template是较难实现的。

```javascript
export const Timeline = (props)=>{
    const timeline = [
        <div class="start">8.21 开始自由职业</div>,
        <div class="online">10.18 专栏上线</div>
    ]
    if(props.reverse){
        timeline.reverse()
    }
    return <div>{timeline}</div>
}

```

## JSX和Template

看到这里，你一定会有一个疑惑：我们该怎么选择JSX和template呢？接下来，我就和你聊聊template和JSX的区别，这样你在加深对template的理解的同时，也能让你逐步了解到JSX的重要性。

先举个例子，我们在极客时间官网购买课程的时候，就如下图所示的样子，页面顶部有搜索框、页面左侧有课程的一些类别。我们按照极客时间对课程的分类，比如前端、后端、AI、运维等分类，可以很轻松地筛选出我们所需类别的课程。

试想一下，如果没有这些条件限制，而是直接显示课程列表，那你就需要自己在几百门的课程列表里搜索到自己需要的内容。也就是说，接受了固定分类的限制，就能降低选择课程的成本。 **这就告诉我们一个朴实无华的道理：我们接受一些操作上的限制，但同时也会获得一些系统优化的收益。**

![图片](https://static001.geekbang.org/resource/image/44/a4/4470104541451a1084dd5f17d5fc7ca4.png?wh=1920x918)

在Vue的世界中也是如此，template的语法是固定的，只有v-if、v-for等等语法。 [Vue的官网中](https://v3.cn.vuejs.org/api/directives.html) 也列举得很详细，也就是说，template遇见条件渲染就是要固定的选择用v-if。这就像极客时间官网上课程的分类是有限的，我们需要在某一个类别中选择课程一样。我们按照这种固定格式的语法书写，这样Vue在编译层面就可以很方便地去做静态标记的优化。

而JSX只是h函数的一个语法糖，本质就是JavaScript，想实现条件渲染可以用if else，也可以用三元表达式，还可以用任意合法的JavaScript语法。也就是说， **JSX可以支持更动态的需求。而template则因为语法限制原因，不能够像JSX那样可以支持更动态的需求**。这是JSX相比于template的一个优势。

**JSX相比于template还有一个优势，是可以在一个文件内返回多个组件**，我们可以像下面的代码一样，在一个文件内返回Button、Input、Timeline等多个组件。

```javascript
export const Button = (props,{slots})=><button {...props}>slots.default()</button>
export const Input = (props)=><input {...props} />
export const Timeline = (props)=>{
  ...
}

```

在上面，我们谈到了JSX相比于template的优势，那么template有什么优势呢？你可以先看下面的截图，这是使用Vue官方的template解析的 [一个demo](https://vue-next-template-explorer.netlify.app/#%7B%22src%22%3A%22%3Cdiv%20id%3D%5C%22app%5C%22%3E%5Cn%20%20%20%20%3Cdiv%20%40click%3D%5C%22()%3D%3Econsole.log(xx)%5C%22%20%20name%3D%5C%22hello%5C%22%3E%7B%7Bname%7D%7D%3C%2Fdiv%3E%5Cn%20%20%20%20%3Ch1%20%3E%E6%8A%80%E6%9C%AF%E6%91%B8%E9%B1%BC%3C%2Fh1%3E%5Cn%20%20%20%20%3Cp%20%3Aid%3D%5C%22name%5C%22%20class%3D%5C%22app%5C%22%3E%E6%9E%81%E5%AE%A2%E6%97%B6%E9%97%B4%3C%2Fp%3E%5Cn%3C%2Fdiv%3E%5Cn%22%2C%22ssr%22%3Afalse%2C%22options%22%3A%7B%22mode%22%3A%22module%22%2C%22filename%22%3A%22Foo.vue%22%2C%22prefixIdentifiers%22%3Afalse%2C%22hoistStatic%22%3Atrue%2C%22cacheHandlers%22%3Atrue%2C%22scopeId%22%3Anull%2C%22inline%22%3Afalse%2C%22ssrCssVars%22%3A%22%7B%20color%20%7D%22%2C%22compatConfig%22%3A%7B%22MODE%22%3A3%7D%2C%22whitespace%22%3A%22condense%22%2C%22bindingMetadata%22%3A%7B%22TestComponent%22%3A%22setup-const%22%2C%22setupRef%22%3A%22setup-ref%22%2C%22setupConst%22%3A%22setup-const%22%2C%22setupLet%22%3A%22setup-let%22%2C%22setupMaybeRef%22%3A%22setup-maybe-ref%22%2C%22setupProp%22%3A%22props%22%2C%22vMySetupDir%22%3A%22setup-const%22%7D%2C%22optimizeBindings%22%3Afalse%7D%7D)。

![图片](https://static001.geekbang.org/resource/image/d5/c4/d57a43f06d47e740b17ba996df051ec4.png?wh=1920x769)

在demo页面左侧的template代码中，你可以看到代码中的三个标签。页面右侧是template代码编译的结果，我们可以看到，相比于我们自己去写h函数，在template解析的结果中，有以下几个性能优化的方面。

首先，静态的标签和属性会放在\_hoisted变量中，并且放在render函数之外。这样，重复执行render的时候，代码里的h1这个纯静态的标签，就不需要进行额外地计算，并且静态标签在虚拟DOM计算的时候，会直接越过Diff过程。

然后是@click函数增加了一个cache缓存层，这样实现出来的效果也是和静态提升类似，尽可能高效地利用缓存。最后是，由于在下面代码中的属性里，那些带冒号的属性是动态属性，因而存在使用一个数字去标记标签的动态情况。

比如在p标签上，使用8这个数字标记当前标签时，只有props是动态的。而在虚拟DOM计算Diff的过程中，可以忽略掉class和文本的计算，这也是Vue 3的虚拟DOM能够比Vue 2快的一个重要原因。

```javascript
import { toDisplayString as _toDisplayString, createElementVNode as _createElementVNode, openBlock as _openBlock, createElementBlock as _createElementBlock } from "vue"

const _hoisted_1 = { id: "app" }
const _hoisted_2 = /*#__PURE__*/_createElementVNode("h1", null, "技术摸鱼", -1 /* HOISTED */)
const _hoisted_3 = ["id"]

export function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", {
      onClick: _cache[0] || (_cache[0] = ()=>_ctx.console.log(_ctx.xx)),
      name: "hello"
    }, _toDisplayString(_ctx.name), 1 /* TEXT */),
    _hoisted_2,
    _createElementVNode("p", {
      id: _ctx.name,
      class: "app"
    }, "极客时间", 8 /* PROPS */, _hoisted_3)
  ]))
}

// Check the console for the AST

```

在template和JSX这两者的选择问题上，只是选择框架时角度不同而已。 **我们实现业务需求的时候，也是优先使用template，动态性要求较高的组件使用JSX实现**，尽可能地利用Vue本身的性能优化。

在课程最后的生态源码篇中，我们还会聊到框架的设计思路，那时你就会发现除了template和JSX之外，一个框架的诞生还需要很多维度的考量，比如是重编译还是重运行时等等，学到那里的时候，你会对Vue有一个更加深刻的理解。

## 总结

好，今天这一讲的主要内容就讲完了，我们来简单总结一下今天学到了什么吧。今天我主要带你学习了Vue 3中的JSX。首先我们学习了h函数，简单来说，h函数内部执行createVNode，并返回虚拟DOM，而JSX最终也是解析为createVnode执行。而在一些动态性要求很高的场景下，很难用template优雅地实现，所以我们需要JSX实现。

因为render函数内部都是JavaScript代码，所以render函数相比于template会更加灵活，但是h函数手写起来非常的痛苦，有太多的配置，所以我们就需要JSX去方便快捷地书写render函数。

JSX的语法来源于React，在Vue 3中会直接解析成h函数执行，所以JSX就拥有了JS全部的动态性。

最后，我们对比了JSX和template的优缺点，template由于语法固定，可以在编译层面做的优化较多，比如静态标记就真正做到了按需更新；而JSX由于动态性太强，只能在有限的场景下做优化，虽然性能不如template好，但在某些动态性要求较高的场景下，JSX成了标配，这也是诸多组件库会使用JSX的主要原因。

## 思考题

在你现在实现的需求里，有哪些是需要JSX的呢？

欢迎在留言区分享你的看法，也欢迎你把这一讲推荐给你的同事和朋友们，我们下一讲再见。