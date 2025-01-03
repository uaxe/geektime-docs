你好，我是杨文坚。

前两节课，我们已经入门了Vue.js 3.x自研组件库的开发和组件库的主题方案设计，还了解了按钮组件这一基础组件的开发流程及其主题化实现。

组件库，核心是将不同类型的功能组件聚合起来，提供给业务前端开发者按需选择，用到实际前端页面上。接下来的几节课，我们主要会一步步开发不同类型的Vue.js 3.x的组件，打造属于自己的Vue.js 3.x企业级自研组件库。

今天，我们先学习组件库里常见的一种组件类型， **动态渲染组件**。

## 什么是动态渲染组件？

在平时工作中用Ant Design或者Element Plus等前端组件库时，相信你经常会用到对话框、消息提醒和侧边抽屉等组件，来做一些信息的动态显示和动态操作，这类组件都可以通过函数式的方式直接调用。

这类组件从功能上分类，一般被称为“反馈类型组件”。如果从技术实现方式上归类，就可以归纳为“动态渲染组件”。 **那我们如何从技术实现的角度，理解动态渲染组件呢？**

从字面意义可以看出来，动态渲染组件就是通过“动态”的方式来“渲染”组件，不需要像常规 Vue.js 3.x组件那样，把组件注册到模板里使用。

所以，动态渲染组件的两个技术特点就是：

- 以直接函数式地使用来执行渲染，使用者不需要写代码来挂载组件；
- 组件内部实现了动态挂载和卸载节点的操作。

如果我们把这2个技术特点放在Vue.js 3.x的框架体系内来理解，你会发现： **Vue.js 3.x 动态渲染组件在页面上是独立于“Vue.js 主应用”之外的渲染。**

因为，动态渲染组件，在项目应用里，只是调用组件的函数（或者方法），然后创建一个独立于“Vue.js 主应用”外的一个“Vue.js 副应用”，动态挂载（mount）在HTML动态创建的DOM上。如果要关闭动态渲染组件，就需要再次触发一个关闭函数（或者方法），把这个“Vue.js 的副应用”卸载（unmount），最后把动态创建的DOM也一并销毁回收。这样，就完成动态渲染组件从挂载到卸载的一个完整的生命周期。

那么，动态渲染组件一般可以实现组件库里的哪些功能组件？或者说，组件库的建设一般需要哪些动态渲染组件呢？

工作开发中高频用到的动态渲染组件有 **消息提醒组件（Message）和对话框组件(Dialog)**。所以，接下来我们会围绕这两个组件动态渲染的技术实现方案展开。

不过，在实现Message和Dialog这两个动态渲染组件之前，我们首要的工作是知道实现动态组件前要准备什么。

## 实现动态渲染组件需要做什么技术准备？

组件库是提供给开发者使用的，除了功能，开发者最关心的当然就是组件的API（接口）使用方式，所以 **动态渲染组件API设计尤为重要**。

我们前面说过，动态渲染组件是直接通过函数方法触发调用，所以我们首先要准备的就是对这个函数方法的API的设计。

需要关注的是，这里不仅仅要考虑技术层面的API设计，我们还需要考虑到组件库使用者的开发使用体验。我建议在设计函数方法的API的时候，以组件库的使用者视角作为出发点，换位思考一下，如果你作为组件库的使用者，使用一个函数方法来触发一个动态渲染组件时，是不是使用方式越简单越好，学习成本越低越好？

所以，我们在设计动态渲染组件的API时， **使用步骤尽量少，使用代码尽量精简**。

而动态渲染组件整个生命周期，最核心的就是“动态挂载”和“动态卸载”两个步骤，所以API的设计，可以直接围绕着“挂载”和“卸载”两个来设计，最简单的可以设计成如下代码：

```typescript
import { Module } from 'xxxx'

// 动态组件挂载
Module.open({  /* 组件参数 */ });

// 动态组件卸载
Module.close();

```

如果考虑到组件不是单例的，而是多实例共存的，可以这么设计API：

```typescript
import { Module } from 'xxxx'

// 创建动态组件 mod1
const mod1 = Module.create({  /* 组件参数 */ });
// 挂载渲染 mod1
mod1.open();
// 卸载动态组件 mod1
mod1.close();

// 创建动态组件 mod2
const mod2 = Module.create({  /* 组件参数 */ });
// 挂载渲染 mod2
mod2.open();
// 卸载动态组件 mod2
mod2.close();

```

如果动态组件在其生命周期还需要添加一些节点，可以这么来设计：

```typescript
import { Module } from 'xxxx'

// 创建动态组件 mod1
const mod1 = Module.create({  /* 组件参数 */ });
// 挂载渲染 mod1
mod1.open();
// 更新组 mod1 件内容
mod1.update({ /* 更新内容参数 */ })
// 卸载动态组件 mod1
mod1.close();

```

完成了动态组件的函数方法API设计，接下来，我们学习Vue.js 3.x实现组件的动态挂载和卸载操作。

前面说了，Vue.js 3.x 动态渲染组件本质就是渲染一个独立的Vue.js 3.x的应用，只是独立于本身页面主应用存在，那么，组件渲染挂载的时候，就需要一个动态的挂载节点DOM，用Vue.js 3.x创建一个App挂载到这个动态节点DOM上面。

后续到组件生命周期结束时，也就是卸载动态渲染组件时，再用Vue.js 3.x卸载App的方法，把组件从DOM上卸载掉，同时把动态创建的DOM给销毁掉。

整个过程，我们可以用最简单的Vue.js 3.x代码实现：

```typescript
import { defineComponent, createApp, h } from 'vue';

// 用 JSX 语法实现一个Vue.js 3.x的组件
const ModuleComponent = defineComponent({
  setup(props, context) {
    return () => {
      return (
        <div>这是一个动态渲染的组件</div>
      );
    };
  }
});

// 实现动态渲染组件的过程

export const createModule = () => {
  // 创建动态节点DOM
	const dom = document.createElement('div');
  // 把 DOM 追加到页面 body标签里
  const body = document.querySelector('body') as HTMLBodyElement;
  const app = createApp({
    render() {
      return h(DialogComponent, {});
    }
  });


  // 返回当前组件的操作实例
  // 其中封装了挂载和卸载组件的方法
  return {
    open(): () => {
      // 把组件 ModuleComponent 作为一个独立应用挂载在 DOM 节点上
      app.mount(dom);
    },
    close: () => {
      // 卸载组件
      app.unmount();
      // 销毁动态节点
      dom.remove();
    }
  }
}

```

上面封装的一个最简单的动态渲染组件，可以这么使用：

```typescript
import { createModule } from './xxxx';

// 创建和渲染组件
const mod = createModule();

// 挂载渲染组件
mod.open();

// 卸载关闭组件
mod.close();

```

通过这些代码演示和注释，相信你可以一目了然地看到动态渲染组件一个完整的开发实现过程。

在这个例子里，我们通过一个 JSX语法实现的动态渲染组件，而JSX的语法比较灵活，在动态渲染组件的实现上有很大的发挥空间，我们还可以用JSX语法，把一个Vue.js 3.x的动态组件实现在一个独立的JS文件中，不需要额外新建Vue文件来书写组件实体。

那么问题来了，我们能不能用不同于JSX语法的另一种语法，也就是模板语法，来实现动态渲染组件呢？

答案是可以的。

## 如何实现一个动态Message组件？

实现动态Message组件前，你可以先看一下最终的功能效果：

![图片](https://static001.geekbang.org/resource/image/a3/c8/a38e2f1a60daa1c57be8101dd393f4c8.gif?wh=599x316)

可以看出，Message组件主要功能是显示消息提示，在挂载渲染后的一段时间内自动关闭，所以，这个组件除了能实现API控制的挂载渲染和卸载关闭，也需要支持默认的自动关闭。

想实现的效果我们知道了，动态渲染组件的技术准备前面也都掌握了，接下来，我们就实现这个Message动态渲染组件。

主要分四步：

- 第一步，先用Vue.js 3.x模板语法实现Message的模板组件；
- 第二步，封装open函数来控制挂载渲染这个模板语法的Message组件；
- 第三步，封装close函数来控制卸载关闭这个组件；
- 第四步，扩展open函数，内置一个定时器来控制延时自动关闭组件。

在进入正式开发前，我们先定义以下参数的TypeScript类型，如下所示：

```typescript
// ./types.ts
export type MessageType = 'info' | 'success' | 'warn' | 'error';

export interface MessageParams {
  text: string;
  type?: MessageType;
  duration?: number;
}

```

进入第一步，也就是用Vue.js 3.x模板语法先实现Message的模板组件，实现代码如下所示：

```xml
<template>
  <div v-if="show" :class="{ [baseClassName]: true, [typeClassName]: true }">
    <div>{{ props.text }}</div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { prefixName } from '../theme/index';
import type { MessageType } from './types';

const show = ref<boolean>(false);

onMounted(() => {
  show.value = true;
});

const props = withDefaults(
  defineProps<{
    text?: string;
    type?: MessageType;
  }>(),
  {
    type: 'info'
  }
);

const closeMessage = () => {
  show.value = false;
};

defineExpose<{
  closeMessage: () => void;
}>({ closeMessage: closeMessage });

const baseClassName = `${prefixName}-message`;
const typeClassName = `${baseClassName}-${props.type}`;
</script>

```

在上述代码中，我把Message组件的消息提醒划分成几种类型，用几种不同颜色来显示区别，具体实现方式是基于Less和CSS Variable，如果你有什么不懂，可以翻看上一节课的内容。

进入第二步来封装open函数，代码片段如下所示：

```javascript
import { createApp, h } from 'vue';
import MessageComponent from './message.vue';
import type { MessageParams } from './types';

const Message = {
  // 封装open函数
  open(params: MessageParams) {
    const dom = document.createElement('div');
    const body = document.querySelector('body') as HTMLBodyElement;
    let duration: number | undefined = params.duration;
    if (duration === undefined) {
      duration = 3000;
    }
    body.appendChild(dom);
    const msg = h(MessageComponent, {
      text: params.text,
      type: params.type
    });
    const app = createApp({
      render() {
        return msg;
      }
    });
    // 挂载和渲染Message组件
    app.mount(dom);

    // 后续等待返回 close 函数
  }
};

export default Message;

```

到了第三步，就是基于已有open函数来返回close函数，代码如下所示：

```typescript
import { createApp, h } from 'vue';
import MessageComponent from './message.vue';
import type { MessageParams } from './types';

const Message = {
  open(params: MessageParams) {
    // 这里省略open函数渲染Message组件的代码

    // 封装内部关闭函数
    const internalClose = () => {
      msg.component?.exposed?.['closeMessage']?.();
      app.unmount();
      dom.remove();
    };

    let timer: number | null = null;
    if (duration > 0) {
      timer = setTimeout(() => {
        internalClose();
      }, duration);
    }

    // 最后返回可控制Message关闭的close函数
    return {
      close: () => {
        if (timer) {
          clearTimeout(timer);
          timer = null;
        }
        internalClose();
      }
    };
  }
};

export default Message;

```

最后，第四步封装定时器到open函数中来控制挂载渲染这个模板语法的Message组件，最终实现代码所示：

```typescript
import { createApp, h } from 'vue';
import MessageComponent from './message.vue';
import type { MessageParams } from './types';

const Message = {
  open(params: MessageParams) {
    const dom = document.createElement('div');
    const body = document.querySelector('body') as HTMLBodyElement;
    let duration: number | undefined = params.duration;
    if (duration === undefined) {
      duration = 3000;
    }
    body.appendChild(dom);
    const msg = h(MessageComponent, {
      text: params.text,
      type: params.type
    });
    const app = createApp({
      render() {
        return msg;
      }
    });
    app.mount(dom);

    const internalClose = () => {
      msg.component?.exposed?.['closeMessage']?.();
      app.unmount();
      dom.remove();
    };

    let timer: number | null = null;
    if (duration > 0) {
      timer = setTimeout(() => {
        internalClose();
      }, duration);
    }

    return {
      close: () => {
        if (timer) {
          clearTimeout(timer);
          timer = null;
        }
        internalClose();
      }
    };
  }
};

export default Message;

```

最终可以这么来使用：

```typescript
import Message from './message';

// 自动关闭
Message.open({
  text: '这是一个success类型的消息提醒组件，5秒后自动关闭',
  type: 'success',
  duration: 5000
})

const msg = Message.open({
  text: '这是一个success类型的消息提醒组件，不会自动关闭',
  type: 'success',
  duration: 0
})
// 如果要关闭，就执行 msg.close() 来关闭这个组件

```

至此，我们就已经学会了用动态渲染组件开发思路，来实现一个消息提示的功能组件Message。

不过到这儿，还没有大功告成。我们要做一个企业级项目，当然要按照企业级的用户体验来要求技术实现。不知道你有没有发现，我实现的这个Message组件，在显示消息和关闭消息过程中很突兀， **消息突然显示和消失，组件变化中间没有过渡，给人一种不友好的用户体验**。

这时候我们就需要用到动画过渡的效果，来消除组件显示和消失的突兀感觉，那在Vue.js 3.x组件开发中，如何来实现组件的动画效果呢？

## 动态渲染组件的动画效果实现？

Vue.js 3.x官方对组件动画过渡效果实现提供了一个内置的组件<transition>，这个组件使用起来比较简单，有JavaScript和CSS3两种控制动画的方式，我们就选择CSS3这个比较简单的动画过渡方式来实现。

你可以先看一下最终的功能效果，如下动图所示：

![图片](https://static001.geekbang.org/resource/image/26/9e/263e3d6d1ed11ab7668c54bd2bcb779e.gif?wh=599x316)

基于上述的Message组件，我们可以加入<transition>内置组件来控制动画过渡。Vue相关代码调整为：

```xml
<template>
  <Transition :name="fadeClassName">
    <div v-if="show" :class="{ [baseClassName]: true, [typeClassName]: true }">
      <div>{{ props.text }}</div>
    </div>
  </Transition>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { prefixName } from '../theme/index';
import type { MessageType } from './types';

const show = ref<boolean>(false);

onMounted(() => {
  show.value = true;
});

const props = withDefaults(
  defineProps<{
    text?: string;
    type?: MessageType;
  }>(),
  {
    type: 'info'
  }
);

const closeMessage = () => {
  show.value = false;
};

defineExpose<{
  closeMessage: () => void;
}>({ closeMessage: closeMessage });

const baseClassName = `${prefixName}-message`;
const typeClassName = `${baseClassName}-${props.type}`;
const fadeClassName = `${baseClassName}-fade`;
</script>

```

针对<transition>组件的CSS3动画过渡样式，在Less文件中补充样式代码如下：

```less
.@{message-name}-fade-enter-active,
.@{message-name}-fade-leave-active {
  transition: opacity 0.5s ease;
}

.@{message-name}-fade-enter-from,
.@{message-name}-fade-leave-to {
  opacity: 0;
}

```

Vue.js 3.x 内置动画效果组件<transition>，结合CSS3实现动画过渡， **核心原理就是在运行过程中，自动检查目标组件是否使用了CSS的过渡动画样式**。如果使用了，会在适当的组件变化过程中添加或者删除对应的样式的className。

在<transition>基于CSS3动画样式实现的动画过渡效果中，真正实现过渡的动画效果是CSS3动画样式，内置的<transition>组件只是帮助开发者更加方便和合理地把握动画的执行时机（如果你还想了解更多Vue.js 3.x 动画效果的实现，可以参阅 [官方文档](https://cn.vuejs.org/guide/extras/animation.html)）。

## 如何实现一个动态Dialog组件？

现在，看我们实现的 Message组件，你会发现只是显示消息提醒，没有任何交互操作。那么，动态渲染组件实现的功能组件，有哪些是既可以显示消息，又可以交互操作的呢？

我们最经常遇到的就是Dialog组件，也就是对话框组件。接下来我们就用动态渲染组件的开发思路来开发一个对话框组件。

实现动态Dialog组件前，我还是先给你看一下最终的功能效果，如下动图所示：

![图片](https://static001.geekbang.org/resource/image/9b/9d/9ba06fe485a85cafea2958f9eb423e9d.gif?wh=600x381)

看了这个动图，是不是觉得很眼熟？没错，就是我们在第4节课中，用JSX语法实现的那个对话框组件。

上次我们是从JSX语法角度来分析实现过程，这节课我们再从动态渲染组件的角度来讲解这个实现过程，具体步骤如下：

- 第一步，实现Dialog的实体组件，用JSX语法或模板语法都可以。这里，Dialog组件要用Emit方式注册好回调事件；
- 第二步，封装createDialog函数来创建一个Dialog的实例。这个过程要注意配置好Dialog的回调函数等操作；
- 第三步，封装close函数来控制卸载关闭这个组件。

具体实现代码也跟第4课实现的代码一致，我把它再贴出来了，你可以再看看。这个是JSX实现的Dialog实体组件：

```typescript
// ./dialog.tsx
import { defineComponent } from 'vue';
import { prefixName } from '../theme/index';

export const DialogComponent = defineComponent({
  props: {
    text: String
  },
  emits: ['onOk'],
  setup(props, context) {
    const { emit } = context;
    const onOk = () => {
      emit('onOk');
    };
    return () => {
      return (
        <div class={`${prefixName}-dialog-mask`}>
          <div class={`${prefixName}-dialog`}>
            <div class={`${prefixName}-dialog-text`}>{props.text}</div>
            <div class={`${prefixName}-dialog-footer`}>
              <button class={`${prefixName}-dialog-btn`} onClick={onOk}>
                确定
              </button>
            </div>
          </div>
        </div>
      );
    };
  }
});

```

以下是封装了函数方法调用的动态渲染组件的方式：

```typescript
import { createApp, h } from 'vue';
import { DialogComponent } from './dialog';

function createDialog(params: { text: string; onOk: () => void }) {
  const dom = document.createElement('div');
  const body = document.querySelector('body') as HTMLBodyElement;
  body.appendChild(dom);
  const app = createApp({
    render() {
      return h(DialogComponent, {
        text: params.text,
        onOnOk: params.onOk
      });
    }
  });
  app.mount(dom);

  return {
    close: () => {
      app.unmount();
      dom.remove();
    }
  };
}

const Dialog: { createDialog: typeof createDialog } = {
  createDialog
};

export default Dialog;

```

最后你会发现，Dialog动态渲染组件和Message动态渲染组件，实现流程是类似的，核心是要用函数方法来控制组件的“动态挂载”和“动态卸载”。

## 总结

这节课核心内容就是Vue.js 3.x 动态渲染组件的实现思路，我再总结一下具体的实现步骤：

- 第一步：设计动态渲染组件的使用函数方法的API，API越简洁越好，核心是要控制组件渲染的挂载和卸载的生命周期；
- 第二步：基于Vue.js 3.x 实现动态渲染组件的原理，核心是要在页面上动态创建DOM，再用Vue.js 3.x创建一个独立应用来“承载”这个组件，挂载在这个动态DOM上面；
- 第三步：关闭动态组件时，要卸载这个Vue.js 3.x的“独立应用”，卸载完再销毁这个动态DOM。

在实现Vue.js 3.x 动态渲染组件的时候，还有几点需要你多加注意：

- 在组件的挂载和卸载过程中，尽量用Vue.js 3.x的内置<transition>组件来实现动画过渡效果，提升用户体验，减少组件动态显示和消失的突兀感觉。
- 动态组件在关闭后，注意要记得销毁组件挂载的动态DOM，释放没必要的内存占用，减少内存泄漏的风险。

## 思考题

Vue.js 3.x 动态渲染组件是通过创建一个新的Vue.js应用来渲染组件的，跟页面原有的Vue.js应用是互相独立的，那么如何实现这两个Vue.js 应用的数据通信呢？

欢迎在留言区分享你的想法，参与讨论，如果对今天的内容有疑问，也欢迎留言，下节课见。

### [完整的代码在这里](https://github.com/FE-star/vue3-course/tree/main/chapter/10)