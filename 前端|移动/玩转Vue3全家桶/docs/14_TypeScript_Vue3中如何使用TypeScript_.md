你好，我是大圣。

在上一讲中，我为你介绍了Vue中的JSX，以及template和JSX各自的优缺点。就像在上一讲中我提到的template牺牲灵活性换来了静态标记的收益，你能看到：有些时候，我们需要放弃一些灵活性去换取项目的整体收益。那么在这一讲中，我会给你介绍一个可以在语言层面上，提高代码可维护性和调试效率的强类型语言——TypeScript。

在整体上，我们的课程还是以使用JavaScript为主。对于TypeScript的内容，我会在这一讲中先带着你入门。下面，我会先讲一下TypeScript的入门知识 ；然后作为巩固，我会带你在Vue 3里再实战一下TypeScript；最后，我会对TypeScript和JavaScript这两者做一个对比分析，让你明白如何在这两者之间做一个更好的平衡。

## 什么是TypeScript

TypeScript是微软开发的JavaScript的超集，这里说的超集，意思就是TypeScript在语法上完全包含JavaScript。TypeScript的主要作用是给JavaScript赋予强类型的语言环境。现在大部分的开源项目都是用TypeScript构建的，并且Vue 3本身TS的覆盖率也超过了95%。

![图片](https://static001.geekbang.org/resource/image/77/78/77827e57090096f5d19a92d53f89ed78.png?wh=1920x1157)

下图展示了TypeScript和JavaScript的关系， **TypeScript相当于在JavaScript外面包裹了一层类型系统，这样可以帮助我们开发更健壮的前端应用**。

![](https://static001.geekbang.org/resource/image/6b/23/6b367c26a1be5a2190c686c0a55f9223.jpg?wh=320x320)

接下来，我们看一下TypeScript带来的新语法：首先，TypeScript可以在JavaScript的变量之上限定数据类型。你可以打开这个TypeScript官方的 [演示链接](https://www.typescriptlang.org/play?#code/FAGwpgLgBAxg9gVwE4GcwDkCGBbMAuFCJASwDsBzKAXigHJBK50Bt4gNQTAGZALRUDbtQNwtbQkKAAcSMfKQTYARmCTUoARgBMATkHRiKAPKkQZfNLhxwmUgqJtgwUcXELaACzAgQcKAHc4SEABMBQA)，在线体验一下TypeScript的这种新语法。

上面TypeScript的官方演示链接，我用截图的方式放到了下面。你可以看到TypeScript和JavaScript的区别在于：TypeScript的变量后面有一个冒号用来设置好变量的数据类型，courseName变量的值只能是字符串，price只能是数字。

在第六行代码中，我们给price赋值了字符串，页面右边解析出来的JavaScript代码是没有任何问题的。但是我们点击右边的Errors时，就会看到一个报错信息，明确告诉你string类型的变量不能赋值给数字类型。

![图片](https://static001.geekbang.org/resource/image/0e/b8/0e5d48ac1ca1ae8f027c34e437bfb7b8.png?wh=1920x707)

这段演示代码算是TypeScript中最简单的Demo了，你的脑子里肯定会提出一个问题：在TypeScript中，既然变量不能随便赋值，那这会带来什么好处吗？

我还是给你举个例子，在你去极客时间官网购买课程的时候，如果官网上对每个课程的类型都定义得非常详细，那么在课程列表页面，你就能知道《玩转Vue 3全家桶》这个课的受众、价格、难度等类型，所以你在购买之前就可以很轻松地过滤不需要的课程。用TypeScript来描述的话，就是下面的代码：

```typescript
interface 极客时间课程 {
    课程名字:string,
    价格:number[],
    受众:string,
    讲师头像?:string|boolean,
    获取口令():string
}

let vueCourse: 极客时间课程 = {
    课程名字:'玩转Vue 3全家桶',
    价格:[59,129],
    受众: '前端小老弟',
    讲师头像:false,
    获取口令(){
        return 88
    }
}

```

这就是TypeScript带来的好处，如果项目中的每个变量、每个接口都能在定义的时候定义好类型，那么很多错误在开发阶段就可以提前被TypeScript识别。在上面的代码中，我们使用interface去定义一个复杂的类型接口，也即极客时间课程。

这样，一个变量想要描述一个课程，就必须要按照这个格式去定义，也就是说：课程名必须是字符串、价格必须是一个数组，并且内部全部是数字、讲师头像可以是字符串或布尔这两个类型之一、获取口令必须是一个函数，并且返回一个字符串。

只要是不符合接口规定的类型的变量，就会直接在变量下方给出红色波浪线的报错提示。鼠标移到报错的变量那里，就会有提示信息弹出，直接通知你哪里出问题了。 **这也是为什么现在大部分前端开源项目都使用TypeScript构建的原因，因为每个函数的参数、返回值的类型和属性都清晰可见，这就可以极大地提高我们代码的可维护性和开发效率**。

![图片](https://static001.geekbang.org/resource/image/28/32/284fa7c40d13ee168c3abb2134307f32.png?wh=1920x859)

TypeScript能够智能地去报错和提示，也是Vue 3的代码阅读起来比较顺畅的主要原因。点击这里的Vue 3源码 [链接](https://github.com/vuejs/vue-next/blob/master/packages/runtime-core/src/apiCreateApp.ts#L28)，如下图所示，在这个源码文件内部的interface App中，定义好了Vue实例所需要的所有方法后，我们可以看到熟悉的use、component、mount等方法。并且每个方法的参数类型和返回值都已经定义好了，阅读和调试代码的难度也降低了很多。

![图片](https://static001.geekbang.org/resource/image/89/b3/896b64a3929a530c0eba6f557a3506b3.png?wh=1904x1644)

接下来，我来跟你聊一下TypeScript中的一些进阶用法。很多时候，你看不懂开源库TypeScript的原因，也是出在对这些进阶用法的生疏上。

首先要讲到的进阶用法是泛型，泛型就是指有些函数的参数，你在定义的时候是不确定的类型，而返回值类型需要根据参数来确定。在下面的代码中，我们想规定test函数的返回类型和参数传递类型保持一致，这个时候就没有办法用number或者string预先定义好参数args的类型，为了解决这一问题，泛型机制就派上了用场。

我们在函数名的后面用尖括号包裹一个类型占位符，常见的写法是，这里为了帮助你理解，我用<某种类型>替代这种写法。调用方式可以直接使用test(1), 也可以使用test <number> (1) 。泛型让我们拥有了根据输入的类型去实现函数的能力，这里你也能感受到TypeScript类型可以进行动态设置。

```typescript
function test<某种类型>(args:某种类型):某种类型{
    return args
}

```

接下来，我再给你介绍一下TypeScript中泛型的使用方法。在下面的代码中，我们实现一个函数getProperty，它能够动态地返回对象的属性。函数的逻辑是很好实现的，那怎么使用TypeScript限制getProperty的类型呢？

```javascript
getProperty(vueCourse， '课程名字') // 返回 ['玩转Vue3全家桶']

```

因为getProperty的返回值是由输入类型决定的，所以一定会用到泛型。但是返回值是vueCourse的一个value值，那如何定义返回值的类型呢？首先我们要学习的是keyof关键字，下面代码中我们使用 `type 课程属性列表 = keyof 极客时间课程` ，就可以根据获取到的极客时间课程这个对象的属性列表，使用extends来限制属性只能从极客时间的课程里获取。

```typescript
function getProperty<某种类型, 某种属性 extends keyof 某种类型>(o: 某种类型, name: 某种属性): 某种类型[某种属性] {
    return o[name]
}
function getProperty<T, K extends keyof T>(o: T, name: K): T[K] {
    return o[name]
}

```

对于上面给出的代码，你可以打开 [这个链接](https://www.typescriptlang.org/play?#code/FAGwpgLgBAxg9gVwE4GcwDkCGBbMAuFCJASwDsBzKAXigHJBK50Bt4gNQTAGZALRUDbtQNwtbQkKAAcSMfKQTYARmCTUoARgBMATkHRiKAPKkQZfNLhxwmUgqJtg14GQhyAZpnFRAgeaAi7UBvpoBfUwH-RgaC8oAG9gKDCoAMBYFUB1bQIiMnIAGlDwwHe5QB4LPEkZOQBtAF1k8KhAdeVAdHk4kgoi8MAm6MAIPUAWTUB5hQB+SoSAHyMTMDMasMB24MA15UBj5UATuQAKAEoOimAAX2twaAA3NgBhRFR8Ny8-QJoQ4qjYhhY2KC4+WgGoDLxcgFZVRJVVQpSw8rw6QFklQD3XoB4HUAgAGAfH1bl8oA0WngnCA0HcRhMZsdiuEkJBkOZaAATTAoAAWYAoAA5SQJikslg4EKQYBBiHBzORIAAFJBwYRyCAATwAPIAF80As56Abx9ANHqiSgIsAejqAcgMoGAAB72Ui4lBQADWYF5cAc0rF4oAfJM4L8RRKpaQcLtZXLZgaJbk7flglDMRBsVA4Llrbh8otrKyIByuTzeZN1mAtshEbQAoByv0A1Eq0abAYOh7lIPmRzbbOOnVNAA) 体验一下，如果传递的name不是极客时间课程类型中的属性，就会有报错提示。

![图片](https://static001.geekbang.org/resource/image/82/cc/824ceff75ccc74801764ac27d3cdc0cc.png?wh=1770x800)

上面只是TypeScript最简单的应用，关于TypeScript的更多类型的使用文档，你可以在 [官网文档](https://www.tslang.cn/docs/handbook/basic-types.html) 上找到很详细的教程和介绍。而且TypeScript的类型其实是可以编程的，可以根据类型去组合推导新的类型，甚至可以使用extends去实现递归类型。

在Vue源码中也有一些地方用到了递归类型，可以书写更复杂的类型组合，这一部分你可以自己去官网学习。到这里，相信你应该大致能理解TypeScript给我们带来的好处了，那如何在Vue 3中使用TypeScript呢，这就是我们接下来要解决的问题。

## Vue 3中的TypeScript

由于TypeScript中的每个变量都需要把类型定义好，因而对代码书写的要求也会提高。 **Vue 2中全部属性都挂载在this之上，而this可以说是一个黑盒子，我们完全没办法预先知道this上会有什么数据，这也是为什么Vue 2对TypeScript的支持一直不太好的原因**。

Vue 3全面拥抱Composition API之后，没有了this这个黑盒，对TypeScript的支持也比Vue2要好很多。在下面的代码中，首先我们需要在script 标签上加一个配置 lang=“ts”，来标记当前组件使用了TypeScript，然后代码内部使用defineComponent定义组件即可。

```xml
<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  // 已启用类型推断
})
</script>

```

在<script setup>的内部，需要调整写法的内容不多。下面的代码使用Composition API的过程中，可以针对ref或者reactive进行类型推导。如果ref包裹的是数字，那么在对count.value进行split函数操作的时候，TypeScript就可以预先判断count.value是一个数字，并且进行报错提示。

```javascript
    const count = ref(1)
    count.value.split('') // => Property 'split' does not exist on type 'number'

```

我们也可以显式地去规定ref、reactive和computed输入的属性，下面代码中我们分别演示了ref、reactive和computed限制类型的写法，每个函数都可以使用默认的参数推导，也可以显式地通过泛型去限制。

```xml
<script setup lang="ts">
import { computed, reactive, ref } from '@vue/runtime-core';
interface 极客时间课程 {
    name:string,
    price:number
}

const msg = ref('') //  根据输入参数推导字符串类型
const msg1 = ref<string>('') //  可以通过范型显示约束

const obj = reactive({})
const course = reactive<极客时间课程>({name: '玩转Vue3全家桶', price: 129})

const msg2 = computed(() => '') // 默认参数推导
const course2 = computed<极客时间课程>(() => {
  return {name: '玩转Vue3全家桶', price: 129}
})
</script>

```

在Vue中，除了组件内部数据的类型限制，还需要对传递的属性Props声明类型。而在<script setup>语法中，只需要在defineProps和defineEmits声明参数类型就可以了。下面的代码中，我们声明了title属性必须是string，而value的可选属性是number类型。

```typescript
const props = defineProps<{
  title: string
  value?: number
}>()
const emit = defineEmits<{
  (e: 'update', value: number): void
}>()

```

接下来，我们对清单应用做一个TypeScript代码的改造。首先清单本身就是一个类型，在下面的代码中，我们定义Todo这个接口，然后初始化todos的时候，Vue也暴露了Ref这个类型，todos是Ref包裹的数组。

```typescript
import {ref, Ref} from 'vue'
interface Todo{
  title:string,
  done:boolean
}
let todos:Ref<Todo[]> = ref([{title:'学习Vue',done:false}])

```

因为这里需要把todos的格式设置为Vue3的响应式类型，所以当你需要了解Composition API所有的类型设置的时候，你可以进入项目目录下面的node\_modules/@vue/reactivity/dist/reactivity.d.ts中查看。

完成了上面的操作后，我们再来了解一下和vue-router的优化相关的工作。vue-router提供了Router和RouteRecordRaw这两个路由的类型。在下面的代码中，用户路由的配置使用RouteRecordRaw来定义，返回的router实例使用类型Router来定义，这两个类型都是vue-router内置的。通过查看这两个类型的定义，我们也可以很方便地学习和了解vue-router路由的写法。

```typescript
import { createRouter, createWebHashHistory, Router, RouteRecordRaw } from 'vue-router'
const routes: Array<RouteRecordRaw> = [
  ...
]

const router: Router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

```

我们打开项目目录下的node\_modules/vue-router/dist/vue-router.d.ts文件，下面的代码中你可以看到vue-router是一个组合类型，在这个类型的限制下，你在注册路由的时候，如果参数有漏写或者格式不对的情况，那就会在调试窗口里直接看到报错信息。如果没有TypeScript的话，我们需要先启动dev，之后在浏览器的调试页面里看到错误页面，回来之后才能定位问题。

```typescript
export declare type RouteRecordRaw = RouteRecordSingleView | RouteRecordMultipleViews | RouteRecordRedirect;

declare interface RouteRecordSingleView extends _RouteRecordBase {
    /**
     * Component to display when the URL matches this route.
     */
    component: RawRouteComponent;
    components?: never;
    /**
     * Allow passing down params as props to the component rendered by `router-view`.
     */
    props?: _RouteRecordProps;
}

```

## TypeScript和JavaScript的平衡

TypeScript引入的强类型系统带来了可维护性较好、调试较为方便的好处。并且TypeScript在社区的热度也越来越高，也有人开始提问：“到底是学TypeScript还是JavaScript？”

但是，这个提问忽略了这一点： **TypeScript是JavaScript的一个超集，这两者并不是完全对立的关系** **。** 所以，学习TypeScript和学习JavaScript不是二选一的关系，你需要做的，是打好坚实的JavaScript的基础，在维护复杂项目和基础库的时候选择TypeScript。

TypeScript能发展至今，得益于微软，而JavaScript的语法则是由TC39协会制定的。由于JavaScript的发展速度问题，有一些语法的实现细节在TC39协会还在讨论的时候，TypeScript就已经实现了。比较典型的就是装饰器Decorator的语法，因为TC39在Decorator的实现思路上，和Typescript不同，未来TypeScript的Decorator可能会和JavaScript的Decorator发生冲突。

TypeScript最终还是要编译成为JavaScript，并在浏览器里执行。对于浏览器厂商来说，引入类型系统的收益并不太高，毕竟编译需要时间。而过多的编译时间，会影响运行时的性能，所以未来TypeScript很难成为浏览器的语言标准。

所以我们的核心还是要掌握JavaScript，在这个基础之上，无论是框架，还是TypeScript类型系统，我们都将其作为额外的工具使用，才是我们最佳的选择。

## 总结

这一讲的主要内容就结束了，我们来复习一下今天学到的内容。首先，我们介绍了TypeScript是什么，以及该如何使用TypeScript带来的类型系统。我们可以限制变量的类型，包括string、number、boolean等。如果把数字类型的变量赋值给了字符串类型的变量，TypeScript就会在编译阶段提示类型出错的信息。

我们可以从代码编辑器的智能提示中及时发现错误，这对我们代码的开发效率是一个很大的提升。基于数字、字符串这种简单的变量类型，我们可以组装出接口类型、数组类型等，也就可以更精确地控制项目中的数据结构。

然后，我们学习了在Vue 3中如何去使用TypeScript，在我们使用的<script setup>环境下，Vue已经把对TypeScript的支持封装得很好了，这样ref 和reactive可以很好地实现类型推导，我们只需要定义好项目中使用变量的格式即可。然后vue-router和Vuex也提供了自己TypeScript类型系统，比如我们可以引入vue-router的RouterViewRecord类型去限制我们书写路由的格式。

最后，我们讨论了一下TypeScript和JavaScript的关系，这个问题在社区热度也一直不减，我也给出了我的想法，那就是JavaScript是前端这个行业的语法标准，而TypeScript是在此之上的类型系统。主流的浏览器短期也不会直接支持TypeScript，所以我们学习的重点还是要放在JavaScript之上。不过，要是你对TypeScript非常感兴趣的话，也可以在留言区留言，如果呼声很高，我也会考虑新增专门的TypeScript的加餐。

## 思考题

最后给你留一个思考题：了解了TypeScript的使用后，你可以回想一下Vue 2里有哪些写法是对TypeScript不友好的，以及我们应该怎么在Vue 3优化呢？

欢迎你在评论区留言分享，也欢迎你把这一讲的内容分享给你的同事和朋友。