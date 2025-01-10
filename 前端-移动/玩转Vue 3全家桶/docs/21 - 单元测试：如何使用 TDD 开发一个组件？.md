你好，我是大圣。

上一讲我们学习了不少组件库里的经典组件，用TypeScript搭建起了TypeScript + Vite + Sass的组件库开发基础环境，并且实现了Container布局组件。

今天我们来聊另外一个大幅提升组件库代码可维护性的手段：单元测试。在理解单元测试来龙去脉的基础上，我还会给你演示，如何使用测试驱动开发的方式实现一个组件，也就是社区里很火的TDD开发模式。

## 单元测试

单元测试（Unit Testing），是指对软件中的最小可测试单元进行检查和验证，这是百度百科对单元测试的定义。而我的理解是，在我们日常代码开发中，会经常写Console来确认代码执行效果是否符合预期，这其实就算是测试的雏形了，我们把代码中的某个函数或者功能，传入参数后，校验输出是否符合预期。

下面的代码中我们实现了一个简单的add函数, 并且使用打印3和add(1,2)的结果来判断函数输出。

add函数虽然看起来很简单，但实际使用时可能会遇到很多情况。比如说x如果是字符串，或者对象等数据类型的时候，add结果是否还可以符合预期？而且add函数还有可能被你的同事不小心加了其他逻辑，这都会干扰add函数的行为。

```javascript
function add(x,y){
  return x+y
}

console.log(3 == add(1,2))

```

为了让add函数的行为符合预期，你希望能添加很多Console的判断逻辑，并且让这些代码自动化执行。

我们来到src目录下，新建一个add.js。下面的代码中，我们定义了函数test执行测试函数，可以给每个测试起个名字，方便调试的时候查找，expect可以判断传入的值和预期是否相符。

```javascript
function add(x,y){
  return x+y
}

function expect(ret){
  return {
    toBe(arg){
      if(ret!==arg){
        throw Error(`预计和实际不符,预期是${arg}，实际是${ret}`)
      }
    }
  }
}
function test(title, fn){
  try{
    fn()
    console.log(title,'测试通过')
  }catch(e){
    console.log(e)
    console.error(title,'测试失败')
  }
}
test('测试数字相加',()=>{
  expect(add(1,2)).toBe(3)
})

```

命令行执行node add.js以后，我们就可以看到下面的结果。如果每次Git提交代码之前，我们都能执行一遍add.js去检查add函数的逻辑，add函数相当于有了个自动检查员，这样就可以很好地提高add函数的可维护性。

```javascript
➜  ailemente git:(main) ✗ node add.js
测试数字相加 测试通过

```

下一步，我们如果想让add函数支持更多的数据类型，比如我们想支持数字字符串的相加，又要怎么处理呢？我们可以先写好测试代码，在下面的代码中，我们希望数字1和字符串2也能以数字的形式相加。

```javascript
test('测试数字和字符串数字相加',()=>{
  expect(add(1,'2')).toBe(3)
})

```

我们在命令行里执行node add.js之后，就会提示下面的报错信息，这说明现在代码还没有符合新的需求，我们需要进一步丰富add函数的逻辑。

![图片](https://static001.geekbang.org/resource/image/63/f9/632ed2fdc46e4bf58083b0dc50cbaaf9.png?wh=1780x802)

我们把add函数改成下面的代码，再执行add.js后，就会提示你两个测试都通过了，这样我们就确保新增逻辑的时候，也没有影响到之前的代码逻辑。

```javascript
function add(x,y){
  if(Number(x)==x && Number(y)==y){
    return Number(x) + Number(y)
  }
  return x+y
}

```

这是一个非常简单的场景演示，但这个例子能够帮助你快速了解什么是单元测试。下一步，我们要在Vue中给我们的组件加上测试。

## 组件库引入Jest

我们选择Facebook出品的Jest作为我们组件库的测试代码，Jest是现在做测试的最佳选择了，因为它内置了断言、测试覆盖率等功能。

不过，因为我们组件库使用TypeScript开发，所以需要安装一些插件，通过命令行执行下面的命令，vue-jest和@vue/test-utils是测试Vue组件必备的库，然后安装babel相关的库，最后安装Jest适配TypeScript的库。代码如下：

```javascript
npm install -D jest@26 vue-jest@next @vue/test-utils@next
npm install -D babel-jest@26 @babel/core @babel/preset-env
npm install -D ts-jest@26 @babel/preset-typescript @types/jest

```

安装完毕后，我们要在根目录下新建.babel.config.js。下面的配置目的是让babel解析到Node和TypeScript环境下。

```javascript
module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    '@babel/preset-typescript',
  ],
}

```

然后，我们还需要新建jest.config.js，用来配置jest的测试行为。不同格式的文件需要使用不同命令来配置，对于.vue文件我们使用vue-jest，对于.js或者.jsx结果的文件，我们就要使用babel-jest，而对于.ts结尾的文件我们使用ts-jest，然后匹配文件名是xx.spect.js。这里请注意， **Jest只会执行.spec.js结尾的文件**。

```javascript
module.exports = {
  transform: {
    // .vue文件用 vue-jest 处理
    '^.+\\.vue$': 'vue-jest',
    // .js或者.jsx用 babel-jest处理
    '^.+\\.jsx?$': 'babel-jest',
    //.ts文件用ts-jest处理
    '^.+\\.ts$': 'ts-jest'
  },
  testMatch: ['**/?(*.)+(spec).[jt]s?(x)']
}

```

然后配置package.json，在scrips配置下面新增test命令，即可启动Jest。

```javascript
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "serve": "vite preview",
    "lint": "eslint --fix --ext .js,vue src/",
    "test": "jest",
}

```

完成上面的操作之后，配置工作就告一段落了，可以开始输入代码做测试了。

我们可以在src目录下新增test.spec.js，再输入下面代码来进行测试。在这段代码中，我们使用expect().toBe()来判断值是否相等，使用toHavaBeenCalled来判断函数是否执行。更多的断言函数你可以去 [官网](https://www.jestjs.cn/docs/expect) 查看，这些函数可以覆盖我们测试场景的方方面面。

```javascript

function sayHello(name,fn){
  if(name=='大圣'){
    fn()
  }
}
test('测试加法',()=>{
  expect(1+2).toBe(3)
})
test('测试函数',()=>{
  const fn = jest.fn()
  sayHello('大圣',fn)
  expect(fn).toHaveBeenCalled()
})


```

## TDD开发组件

好，通过之前的讲解，我们已经学会如何使用Jest去测试函数。下一步我们来测试Vue3的组件，其实，Vue的组件核心逻辑也是函数。

这里我们借助Vue官方推荐的 [@vue/test-utils](https://next.vue-test-utils.vuejs.org) 库来测试组件的渲染，我们新建src/components/button文件夹，新建Button.spec.ts。

参考 [Element3的button组件](https://e3.shengxinjing.cn/#/component/button)，el-button组件可以通过传递size来配置按钮的大小。现在我们先根据需求去写测试代码，因为现在Button.vue还不存在，所以我们可以先根据Button的行为去书写测试案例。

```javascript
import Button from './Button.vue'
import { mount } from '@vue/test-utils'
describe('按钮测试', () => {
  it('按钮能够显示文本', () => {
    const content = '大圣小老弟'
    const wrapper = mount(Button, {
      slots: {
        default: content
      }
    })
    expect(wrapper.text()).toBe(content)
  })
  it('通过size属性控制大小', () => {
    const size = 'small'
    const wrapper = mount(Button, {
      props: {
        size
      }
    })
    // size内部通过class控制
    expect(wrapper.classes()).toContain('el-button--small')
  })

})

```

我们首先要从@vue/test-utils库中导入mount函数，这个函数可以在命令行里模拟Vue的组件渲染。在Button的slot传递了文本之后，wrapper.text()就能获取到文本内容，然后对Button渲染结果进行判断。之后，我们利用size参数，即可通过渲染不同的class来实现按钮的大小，这部分内容我们很熟悉了，在 [第20讲](https://time.geekbang.org/column/article/464098) 里的Container组件中就已经实现过了。

然后我们在命令行执行npm run test来执行所有的测试代码。命令行终端上提示，我们期望button上含有el-button-small class，但是实际上button上并没有这个class，所以就会报错。具体报错信息你可以参考下图。

![图片](https://static001.geekbang.org/resource/image/ac/43/acb02590c5a4390c89bc76a8e1769043.png?wh=1442x652)

之后，我们再通过实现Button组件的逻辑，去处理这个错误信息，这就是TDD测试驱动开发的方法。我们实现功能的过程就像小时候写作业，而测试代码就像批改作业的老师。

TDD的优势就相当于有一位老师，在我们旁边不停做批改，哪怕一开始所有题都做错了，只要我们不断写代码，把所有题都回答正确，也能最后确保全部功能的正确。

我们通过接收size去渲染button的class，我们来到button.vue中，通过下面的代码可以接收size参数，并且成功渲染出对应的class。

```xml
<template>
  <button
    class="el-button"
    :class="[size ? `el-button--${size}` : '',]"
  >
    <slot />
  </button>
</template>
<script setup lang="ts">

import {computed, withDefaults} from 'vue'
interface Props {
  size?:""|'small'|'medium'|'large'
}
const props = withDefaults(defineProps<Props>(),{
  size:""
})
</script>

```

进行到这里还没有结束，class还要通过Sass去修改浏览器页面内的大小。

为了让你抓住重点，这里的Sass代码我放几个核心逻辑，完整代码你可以在项目的 [GitHub](https://github.com/shengxinjing/ailemente/blob/main/src/components/button/Button.vue#L40) 里看到。

```scss
@include b(button){
  display: inline-block;
  cursor: pointer;
  background: $--button-default-background-color;
  color: $--button-default-font-color;
  @include button-size(
    $--button-padding-vertical,
    $--button-padding-horizontal,
    $--button-font-size,
    $--button-border-radius
  );
  @include m(small) {
    @include button-size(
      $--button-medium-padding-vertical,
      $--button-medium-padding-horizontal,
      $--button-medium-font-size,
      $--button-medium-border-radius
    );
  }
  @include m(large) {
    @include button-size(
      $--button-large-padding-vertical,
      $--button-large-padding-horizontal,
      $--button-large-font-size,
      $--button-large-border-radius
    );
  }
}

```

前面的代码中通过b(button)渲染el-button的样式，内部使用变量都可以在mixin中找到。通过b和button-size的嵌套，就能实现按钮大小的控制。button渲染的结果，你可以参考下方的截图。

![图片](https://static001.geekbang.org/resource/image/86/c2/86ee8a8f3fd337014857329324f4b1c2.png?wh=1920x557)

然后我们接着往下进行，想要设置按钮的大小，除了通过props传递，还可以通过全局配置的方式设置默认大小。我们进入到代码文件src/main.ts中，设置全局变量$AILEMENTE中的size为large，并且还可以通过type="primary"或者type="success"的方式，设置按钮的主体颜色，代码如下：

```typescript
const app = createApp(App)
app.config.globalProperties.$AILEMENTE = {
  size:'large'
}
app.use(ElContainer)
  .use(ElButton)
  .mount('#app')

```

首先我们要支持全局的size配置，在src目录下新建util.ts，写入下面的代码。我们通过vue提供的getCurrentInstance获取当前的实例，然后返回全局配置的$AILEMENTE。这里请注意，由于很多组件都需要读取全局配置，所以我们封装了useGlobalConfig函数。

```typescript
import { getCurrentInstance,ComponentInternalInstance } from 'vue'

export function useGlobalConfig(){
  const instance:ComponentInternalInstance|null =getCurrentInstance()
  if(!instance){
    console.log('useGlobalConfig 必须得在setup里面整')
    return
  }
  return instance.appContext.config.globalProperties.$AILEMENTE || {}

}

```

这时我们再回到Button.vue中，通过computed返回计算后的按钮的size。如果props.size没传值，就使用全局的globalConfig.size；如果全局设置中也没有size配置，按钮就使用Sass中的默认大小。

```xml
<template>
  <button
    class="el-button"
    :class="[
      buttonSize ? `el-button--${buttonSize}` : '',
      type ? `el-button--${type}` : ''
    ]"
  >
    <slot />
  </button>
</template>

<script lang="ts">
export default{
  name:'ElButton'
}
</script>

<script setup lang="ts">

import {computed, withDefaults} from 'vue'
import { useGlobalConfig } from '../../util';

interface Props {
  size?:""|'small'|'medium'|'large',
  type?:""|'primary'|'success'|'danger'
}
const props = withDefaults(defineProps<Props>(),{
  size:"",
  type:""
})
const globalConfig = useGlobalConfig()
const buttonSize = computed(()=>{
  return props.size||globalConfig.size
})
</script>

```

我们来到src/App.vue中，就可以直接使用el-button来显示不同样式的按钮了。

```xml
  <el-button type="primary">
    按钮
  </el-button>
  <el-button type="success">
    按钮
  </el-button>
  <el-button>按钮</el-button>
  <el-button size="small">
    按钮
  </el-button>


```

不同按钮的显示效果如下所示：

![图片](https://static001.geekbang.org/resource/image/e1/20/e1bc7b41f95640cafaf4619f9df96720.jpg?wh=1920x508)

然后我们进入jest.config.js中，新增下面的配置，collectCoverage标记的意思是我们需要收集代码测试覆盖率。

```typescript
module.exports = {
  transform: {
    //  用 `vue-jest` 处理 `*.vue` 文件
    '^.+\\.vue$': 'vue-jest', //vuejest 处理.vue
    '^.+\\.jsx?$': 'babel-jest',  // babel jest处理js or jsx
    '^.+\\.tsx?$': 'ts-jest', // ts-jest 处理.ts .tsx
  },
  testMatch: ['**/?(*.)+(spec).[jt]s?(x)'],
  collectCoverage: true,
  coverageReporters: ["json", "html"],
}

```

然后在执行npm run test后，项目的根目录下就会出现一个coverage目录。

我们打开下面的index.html后，就可以在浏览器中看到测试覆盖率的报告。对照下图我们可以看到，button组件的测试覆盖率100%，util下面有两行代码飘红，也就是没有测试的逻辑。

在一定程度上，测试覆盖率也能够体现出代码的可维护性，希望你可以用好这个指标。

![图片](https://static001.geekbang.org/resource/image/b3/d0/b38eec8c9b286c4316cecfe39e3a67d0.png?wh=1868x288)

![图片](https://static001.geekbang.org/resource/image/6b/be/6b4027a05761d323224df5b09c4beebe.png?wh=1568x690)

![图片](https://static001.geekbang.org/resource/image/62/02/621bf3871a7b345bb6a08c451e0b3d02.png?wh=1870x506)

最后，我们进入.husky/pre-commit文件，新增npm run test命令，这么做的目的是，确保测试通过的代码才能进入git管理代码，这会进一步提高代码的规范和可维护性。

```typescript
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npm run lint
npm run test

```

## 总结

今天的内容就到此结束了，我们来回顾一下今天学到的东西吧。

首先，我们学习了什么是自动化测试，我们实现了test和expect函数，通过它们来测试add函数。

然后，我们通过jest框架配置了Vue的自动化测试环境。通过安装babel、@vue/test-utils、babel-vue、ts-babel等插件，我们配置了TypeScript环境下的Jest+Vue 3的单测环境，并且匹配项目中.spect结束的js和vue文件执行测试。

在Jest中，我们通过describe函数给测试分组，通过it执行测试，再利用expect语法去执行断言。我们还发现，借助@vue/test-utils库可以很方便地对Vue组件进行测试。

最后，我们一起体验了TDD测试驱动开发的开发模式。我们先根据功能需求，去写出测试案例，这个时候测试窗口就会报错，然后我们才开始实现功能，最终让测试代码全部通过，用这样的方式来检验开发的结果。 **TDD的优势就在于可以随时检验代码的逻辑，能极大提高代码的可维护性**。

现在我们有了TypeScript，有了Jest，下一讲我们将实现一个比较复杂的表单组件，它会包含组件的通信、方法传递等难点，敬请期待。

## 思考题

最后留个思考题，我们的Button组件怎么通过传递circle属性来显示圆角按钮呢？

欢迎你在评论区留下你的答案，也欢迎你把这一讲分享给你的同事和朋友们，我们下一讲再见！