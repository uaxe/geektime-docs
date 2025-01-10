你好，我是大圣。

在讲组件化的进阶开发篇之前，我想在全家桶实战篇的最后，用一讲的篇幅，来专门聊一下TypeScript。希望你在学完这一讲之后，能对TypeScript有一个全面的认识。

另外，今天我会设置很多实战练习，一边阅读一边敲代码的话，学习效果更好。而且，这次加餐中的全部代码都是可以在线完成的，建议你打开 [这个链接](https://www.typescriptlang.org/play?#code/FAehAJC+9Q66MA3lHnrQMhGGO5QgB6F+E9gnU0AByhZBKA)，把下面的每行代码都跟着敲一遍。

## TypeScript入门

对于TypeScript，你首先要了解的是，TypeScript 可以在JavaScript的基础上，对变量的数据类型加以限制。TypeScript 中最基本的数据类型包括布尔、数字、字符串、null、undefined，这些都很好理解。

在下面的代码中，我们分别定义了这几个数据类型的变量，你能看到，当我们把number类型的变量price赋值字符串时，就会报错，当我们把数组 me 的第一个元素 me\[0\] 的值修改为数字时，也会报错。

```typescript
let courseName:string = '玩转Vue 3全家桶'
let price:number = 129
price = '89' //类型报错
let isOnline:boolean = true
let courseSales:undefined
let timer:null = null
let me:[string,number] = ["大圣",18]
me[0] = 1 //类型报错

```

当你不确定某个变量是什么类型时，你可以使用any作为这个变量的类型。你可以用any标记任何属性，可以修改任何数据，访问任何方法也不会报错。也就是说，在TypeScript中，当你把变量的类型标记为any后，这个变量的使用就和JavaScript没啥区别了，错误只会在浏览器里运行的时候才会提示。

```typescript
let anyThing
let anyCourse :any = 1
anyCourse = 'xx'
console.log(anyCourse.a.b.c)

```

然后我们可以使用enum去定义枚举类型，这样可以把类型限制在指定的场景之内。下面的代码中我们可以把课程评分限制在好、非常好和嘎嘎好三个值之内。

```typescript
enum 课程评分 {好,非常好,嘎嘎好}
console.log(课程评分['好']===0)
console.log(课程评分[0]==='好')
let scores = [课程评分['好'], 课程评分['嘎嘎好'], 课程评分['非常好']]

```

然后我们可以通过学到的这些基础类型，通过组合的方式组合出新的类型，最常见的组合方式就是使用 \| 实现类型联合。下面的代码中我们定义course1变量的类型为字符串或者数字，赋值为这两个类型都不会报错，还可以用来限制变量只能赋值为几个字符串的一个，score的取值只能是代码中三个值之一。

```typescript
let course1 : string|number = '玩转vue 3'
course1 = 1
course1 = true // 报错

type courseScore = '好' | '非常好' | '嘎嘎好'
let score1 :courseScore = '好'
let score2 :courseScore = '一般好' // 报错

```

通过interface接口可以定义对象的类型限制。下面代码中我们定义了极客时间课程的类型，课程名是字符串，价格使用number\[\] 语法定义类型为数字组成的数组，讲师头像是string或者boolean，并且通过 ?设置为可选属性，课程地址使用readonly设置为只读属性，如果对课程地址进行修改就会报错。

```typescript
interface 极客时间课程 {
    课程名字:string,
    价格:number[],
    受众:string,
    讲师头像?:string|boolean,
    readonly 课程地址:string
}
let vueCourse: 极客时间课程 = {
    课程名字:'玩转Vue 3全家桶',
    价格:[59,'139'],
    讲师头像:false,
    课程地址:"time.geekbang.org"
}
vueCourse.课程地址 = 'e3.shengxinjing.cn' // 报错

```

然后我们学一下函数的类型限制。其实函数的定义，参数和返回值本质上也是变量的概念，都可以进行类型的定义。下面的代码中我们定义了参数x和y是数字，返回值也是数字的add函数，定义好参数和返回值类型，函数的类型自然也就确定了。

```typescript
function 函数名(参数:参数类型):返回值类型{} //大致语法
function add(x: number, y: number): number {
    return x + y;
}
add(1, 2);


```

我们也可以使用变量的方式去定义函数，直接使用(参数类型) =>返回值类型的语法去定义add1的变量类型，但是这样写出来的代码可读性稍差一些，我更建议你使用type或者interface关键字去定义函数的类型。下面代码中的addType和addType1都是很好的定义函数类型的方式：

```
let add1:(a:number,b:number)=>number = function(x: number, y: number): number {
    return x + y;
}
type addType = (a:number,b:number)=>number
let add2:addType  = function(x: number, y: number): number {
    return x + y;
}

interface addType1{
    (a:number,b:number):number
}
let add3:addType1  = function(x: number, y: number): number {
    return x + y;
}

```

如果你的函数本来就支持多个类型的参数，下面的代码中reverse函数既支持数字也支持字符串。 **我们的要求是如果参数是数字，返回值也要是数字，参数是字符串返回值也只能是字符串**，所以参数和返回值都用number\|string就没法精确地限制这个需求。我们需要使用函数重载的方式，定义多个函数的输入值和返回值类型，更精确地限制函数的类型。我们可以在 [Vue 3的源码](https://github.com/vuejs/vue-next/blob/master/packages/reactivity/src/ref.ts#L72) 看到Vue 3中ref函数的重载写法：

```typescript
function reverse(x: number): number
function reverse(x: string): string
function reverse(x: number | string): number | string | void {
    if (typeof x === 'number') {
        return Number(x.toString().split('').reverse().join(''));
    } else if (typeof x === 'string') {
        return x.split('').reverse().join('');
    }
}

```

这样TypeScript里如何限制一个变量和函数类型，我们就大致入门了。这时候你肯定还有个疑问， **日常开发中有很多浏览器上的变量和属性，这些怎么限制类型呢？**

关于宿主环境里的类型，TypeScript全部都给我们提供了，我们可以直接在代码中书写：Window是window的类型，HTMLElement是dom元素类型，NodeList是节点列表类型，MouseEvent是鼠标点击事件的类型……关于更多TypeScript的内置类型，你可以在 [TypeScript的源码](https://github.com/Microsoft/TypeScript/tree/main/src/lib) 中看到：

```typescript
let w:Window = window
let ele:HTMLElement = document.createElement('div')
let allDiv: NodeList = document.querySelectorAll('div')

ele.addEventListener('click',function(e:MouseEvent){
    const args:IArguments = arguments
    w.alert(1)
    console.log(args)
},false)

```

除了浏览器的API，我们还会用到很多第三方框架，比如Vue、Element3等等，这些框架现在都提供了完美的类型可以直接使用。在 [第18讲](https://time.geekbang.org/column/article/445880) 中我们使用下面的代码Vue导出的Ref来限定数据是ref包裹的响应式数据：

```typescript
 import { ref ,Ref} from 'vue'
 interface Todo{
     title:string,
      done:boolean
 }
 let todos:Ref = ref([{title:'学习Vue',done:false}])


```

## 泛型

那么聊完上面的内容，你就已经能使用TypeScript实现很多项目的开发，把所有变量和函数出现的地方都定义好类型，就可以在编译阶段提前规避出很多报错。然而TypeScript的能力可不止于此， **TypeScript可以进行类型编程，这会极大提高TypeScript在复杂场景下的应用场景。**

然后我们来看一下TypeScript中的泛型，这也是很多同学觉得TypeScript很难的最大原因。

首先我们看下面的代码，我们定一个idientity0函数，这个函数逻辑非常简单，就是直接返回参数，那么 **我们怎么确定返回值的类型呢？**

因为输入值可以是任意属性，所以我们只能写出identity0这个函数，参数和返回值类型都是any，但是明显不能满足我们的需求。我们需要返回值的类型和参数一致，所以我们在函数名之后使用<>定一个泛型T，你可以理解这个T的意思就是给函数参数定义了一个类型变量，会在后面使用，相当于【 **type T = arg的类型**】，返回值使用T这个类型就完成了这个需求。

```typescript
function identity0(arg: any): any {
    return arg
}
// 相当于type T = arg的类型
function identity<T>(arg: T): T {
    return arg
}
identity<string>('玩转vue 3全家桶') // 这个T就是string，所以返回值必须得是string
identity<number>(1)

```

有了泛型之后，我们就有了把函数参数定义成类型的功能，我们就可以实现类似高阶函数的类型函数。下面的代码中我们使用keyof语法获得已知类型VueCourse5的属性列表，相当于 ‘name’\|‘price’：

```typescript
interface VueCourse5 {
    name:string,
    price:number
}
type CourseProps = keyof VueCourse5 // 只能是name和price选一个
let k:CourseProps = 'name'
let k1:CourseProps = 'p' // 改成price

```

keyof可以帮助我们拆解已有类型，下一步我们需要使用extends来实现类型系统中的条件判断。我们定义类型函数ExtendsType，接受泛型参数T后，通过判断T是不是布尔值来返回不同的类型字符串，我们就可以通过ExtendsType传入不同的参数去返回不同的类型。

```typescript
// T extends U ? X : Y 类型三元表达式

type ExtendsType<T> = T extends boolean ? "重学前端" : "玩转Vue 3"
type ExtendsType1 = ExtendsType<boolean> // type ExtendsType1='重学前端'
type ExtendsType2 = ExtendsType<string> // type ExtendsType2='玩转Vue 3'

```

extends相当于TypeScript世界中的条件语句，然后in关键字可以理解为TypeScript世界中的遍历。下面的代码中我们通过 k in Courses语法，相当于遍历了Courses所有的类型作为CourseObj的属性，值的类型是number。

```typescript
type Courses = '玩转Vue 3'|'重学前端'
type CourseObj = {
    [k in Courses]:number // 遍历Courses类型作为key
}
// 上面的代码等于下面的定义
// type CourseObj = {
//     玩转Vue 3: number;
//     重学前端: number;
// }

```

学完上面的语法，你就能完全搞懂 [第18讲](https://time.geekbang.org/column/article/455487) 里的getProperty函数。限制函数第二个参数只能是第一个参数的属性，并且返回值的类型，最后我们传递不存在的属性时，TypeScript就会报错。

```typescript
// K extends keyof T限制K的类型必须是T的属性之一
// T[K]是值得类型
function getProperty<T, K extends keyof T>(o: T, name: K): T[K] {
    return o[name]
}
const coursePrice:CourseObj = {
    "玩转Vue 3":129,
    "重学前端":129
}
getProperty(coursePrice,'玩转Vue 3')
getProperty(coursePrice,'不学前端') // 报错

```

然后我再给你讲解最后一个关键字infer。<T>让我们拥有了给函数的参数定义类型变量的能力，infer则是可以在extends之后的变量设置类型变量，更加细致地控制类型。下面的代码中我们定义了ReturnType类型函数，目的是返回传入函数的返回值类型。infer P的意思就是泛型T是函数类型，并且这个函数类型的返回类型是P。

```typescript
type Foo = () => CourseObj

// 如果T是一个函数，并且函数返回类型是P就返回P
type ReturnType1<T> = T extends ()=>infer P ?P:never
type Foo1 = ReturnType1<Foo>

```

## 实战练习

有了上面的基础后，我们来几个实战的练习。以下所有的练习都可以在代码最后找到答案，我建议你一定要自己实现一遍才能有最多的收获。

代码地址： [https://www.typescriptlang.org/docs/handbook/utility-types.html](https://www.typescriptlang.org/docs/handbook/utility-types.html)

下面的代码中，我们首先定义类型Todo，有title、desc和done三个属性：

```typescript
interface Todo {
  title: string
  desc:string
  done: boolean
}

```

首先第一题是，我们需要实现类型函数Partial1，返回的类型是Todo所有的属性都变成可选项。

```typescript
type partTodo = Partial1<Todo>
// 和下面类型一致，鼠标移动到partTodo变量上也能看到
// type partTodo = {
//     title?: string | undefined;
//     desc?: string | undefined;
//     done?: boolean | undefined;
// }

```

这一题的答案见下面的代码，使用K in keyof T遍历所有T的属性后，使用 ?标记为可选属性。

```typescript
type Partial1<T> = {
    [K in keyof T]?:T[K]
}

```

TypeScript中还有很多类似的函数，包括Pick、Omit、Diff等函数，你都可以自行实现一遍，更多工具类型函数你可以移步 [TypeScript官方文档](https://www.typescriptlang.org/docs/handbook/utility-types.html)。你也可以结合下面的代码工具函数的实现，到留言区中讨论一下分别实现了什么功能。

```typescript
type Exclude1<T, K> = T extends K ? never : T
type Pick1<T, K extends keyof T> = {
    [P in K]: T[P]
}
type Concat1<T extends any[], U extends any[]> = [...T, ...U]

```

最后我们再来一个实战的练习，在实际项目开发中除了JavaScript、浏览器和第三方框架的类型，还有一个很重要的场景就是后端返回的数据类型。我们需要根据开发文档去定义好每个请求的类型，在下面的代码中，request作为发送请求的函数，可以传递url是字符串。 **那我们该如何定义Interface API，使其能够限制request只能有buy和comment两个请求地址，并且comment请求的参数中message是必传项呢？**

```typescript
import axios from 'axios'

function request(url:string,obj:any){
    return axios.post(url,obj)
}
interface Api{

}
request('/course/buy',{id:1})
request('/course/comment',{id:1,message:'嘎嘎好看'})
request('/course/comment',{id:1}) //如果message必传 怎么类型提醒缺少参数
request('/course/404',{id:1}) //接口不存在 类型怎么需要报错

```

记得要先尝试自己实现一下，答案就在下面的代码中。在API类型中，我们定义了buy和comment两个属性，分别设置了当前请求所需要的参数都是必选项。然后我们通过在request中使用泛型T限制url，通过Api\[T\] 限制传递的参数，这样我们就得到了下面的报错示意图，在编译阶段就能通知你缺少message属性，并且404请求不存在，这可以极大提高我们开发的体验和效率。

```typescript
import axios from 'axios'
interface Api{
    '/course/buy':{
        id:number
    },
    '/course/comment':{
        id:number,
        message:string
    }
}

function request<T extends keyof Api>(url:T,obj:Api[T]){
    return axios.post(url,obj)
}

request('/course/buy',{id:1})
request('/course/comment',{id:1,message:'嘎嘎好看'})
request('/course/comment',{id:1}) //如果message必传 怎么类型提醒缺少参数
request('/course/404',{id:1}) //接口不存在 类型怎么需要报错

```

![图片](https://static001.geekbang.org/resource/image/0c/8e/0c52cee36238831a10e4004d6536f18e.png?wh=1420x612)

更多类型的练习，你可以访问 [type-challenges](https://github.com/type-challenges/type-challenges) 这个项目自行尝试。现在你再去看项目或者框架源码中的TypeScript，是不是就没有那么晦涩了呢。

## 总结

今天想聊的TypeScript就结束啦，总结一下我们今天学到的内容吧。

首先我们学习了TypeScript的基本类型，包括数字字符串等等，然后我们可以通过这些基础类型组合出复杂的类型组合，并且可以通过type和interface关键字定义复杂对象的类型和函数的类型。

然后浏览器的相关变量和API类型TypeScript都已经内置了，包括HTMLElement、MouseEvent等等，第三方框架的类型我们可以直接导入使用，Vue中的Ref类型我们就会经常用来定义ref函数包裹的响应式数据。

接着我们学习了TypeScript进阶中最重要的概念：泛型。通过泛型我们可以在函数内部把类型变成变量使用，并且通过keyof、in、extends、infer等关键字组合出复杂的类型函数，可以更加精确地组合现有类型。

最后我们通过定义前后端的接口类型的案例，演示了在实战中我们如何通过类型系统提高联调和开发的体验。

有了这些TypeScript的知识储备，你才能更好地在Vue项目中使用TypeScript。由于JSX的本质就是JavaScript，所以TypeScript的诞生也给了JSX更好的类型推导，这是JSX相比于Template的另外一个优势。关于Vue和TypeScript开发组件的内容，我们下一讲开始全部使用TypeScript来实现。

## 思考题

最后，留一个思考题：我们实现的Partial1可以把类型的属性变成可选的，如果传递的类型是嵌套很多层的，如何实现Partial1的递归版本，才能把所有嵌套的属性都变成可选的呢？

欢迎你在评论区分享你的答案，也欢迎你把这一讲的内容分享给你的同事和朋友们，我们下一讲再见。