你好，我是宋一玮，欢迎回到React应用开发的学习。

上节课我们学习了不可变数据，了解了不可变数据对React的重要意义，然后学习了用 `React.memo` 创建具有更佳性能的纯组件。最后介绍了在JS中实现不可变数据的几种方式，除了我们在 `oh-my-kanban` 中的手工实现，还有Immutable.js和Immer这些开源框架。

接下来我们会用两节课的时间，学习React的应用状态管理。你也许已经胸有成竹了：“应用状态，不就是 `useState` 吗？已经很熟悉啦。”

很高兴你有这份自信，不过我们上面提到的应用状态管理的学习，是一个概念到框架再到具体案例的过程。首先应用状态管理是一个前端领域的概念，这节课我们会先来看看它是解决什么问题的，然后来学习目前仍然最流行的应用状态管理框架Redux，了解它的用法和设计思想。

这里也提前做个小预告，在下节课我们会进一步讨论什么情况下使用React的state，什么情况下使用Redux，并举一些实际的例子。

下面开始这节课的内容。

## 什么是应用状态管理？

我们先看 **应用状态（Application State）**。理论上，一个应用在运行的时候内存里所有跟它有关的数据都可以称作是应用状态，但实际上，这远远超出了应用开发者需要关注的范围。

我们姑且可以类比一下后端服务： **有状态服务（Stateful Service）和无状态服务（Stateless Service）** 常被一起提及。

比如一个购物车HTTP服务，在服务器端临时保存了当前登录用户的session信息，用户先后两次请求都会读写这个session，那这个HTTP服务就是 **有状态服务**；另一个商品列表HTTP服务，并不关心用户是否登录，仅凭用户发过来的HTTP请求里包含的参数就可以完成工作，把结果作为HTTP响应返回给用户，那么它就是 **无状态服务**。

这两个服务相减，得出“ _服务器端临时保存的登录用户的session信息_”就是我们需要关注的应用状态（至于session保存在内存里还是数据库里，我们这里暂时不讨论）。

**越是“富JS”的浏览器端应用，越是倾向于把服务器端的应用状态转移到浏览器端**。于是就有了“ _浏览器端临时保存的登录用户的session信息_”，这样提供给前端JS使用的应用状态。

![图片](https://static001.geekbang.org/resource/image/01/6a/01b6a0efdecf1807f165c7a89d6d766a.png?wh=1503x1224)

如果不这样做呢？这里我们再举个反例。

比如对一个简单的对话框来说，决定它是否显示的是一个布尔值状态。如果把这个状态保存在服务器端，意味着每次弹出和关闭对话框都要去调用后端服务，这比在浏览器端保存状态要重得多。

从用户体验看，用户开关对话框都要等服务器响应，体验是比较差的。从前端开发角度看，开关对话框本来可以是一个同步的本地逻辑，却非要实现成异步的服务器请求，增加了复杂性。你可能会有疑惑：“真有框架会这样做吗？”有啊，当年的JSF就是。

React这样由数据驱动的前端框架，更是依赖浏览器本地的应用状态。

当开发本地状态越来越复杂，复杂到需要一层专门的抽象时，就出现了 **应用状态管理** 框架，来管理这些应用状态。

## 应用状态管理框架Redux

在React技术社区中，提到应用状态管理框架，一定会先提到Redux。Redux是一个用于JS应用的、可预测的状态容器。它并不是React专用，你也可以在Vue或Svelte应用中使用Redux。

你可以在任何一个JS项目中安装Redux：

```bash
npm install redux

```

我们先看一段为 `cardList` 写的样例代码：

```javascript
import { createStore } from 'redux';

function cardListReducer(state = [], action) {
  switch (action.type) {
    case 'card/add':
      return [action.newCard, ...state];
    case 'card/remove':
      return state.filter(card => card.title !== action.title);
    default:
      return state;
  }
}

const store = createStore(cardListReducer);
store.subscribe(() => console.log(store.getState()));

store.dispatch({ type: 'card/add', newCard: { title: '开发任务-1' } });
// [{ title: '开发任务-1' }]
store.dispatch({ type: 'card/add', newCard: { title: '测试任务-2' } });
// [{ title: '测试任务-2' }, { title: '开发任务-1' }]
store.dispatch({ type: 'card/remove', title: '开发任务-1' });
// [{ title: '测试任务-2' }]

```

你一下子看到了有点熟悉的名称： `reducer` 、 `action` 、 `dispatch` ，好嘛，这不就是 [第9节课](https://time.geekbang.org/column/article/566338?) 讲到的，状态Hooks之一的 `useReducer` 吗？是的，你没看错，之所以这么像，原因之一是Redux的两位原作者，都加入了React核心团队。

上面这段代码的核心概念是 `store` 即存储。在用Redux的 `createStore` API 创建 `store` 时指定 `reducer` 归约器函数，然后调用 `store.subscribe()` 方法订阅 `store` 的变化， `store.getState()` 可以取得最新的状态数据。然后调用 `store.dispatch()` 方法派发 `action` 动作， `reducer` 会根据 `action` 中的 `type` 字段决定动作的类型，然后返回新的状态用于更新 `store` 。

### Redux的核心概念和设计思想

刚才已经提到了Redux几个重要概念，这里再稍作介绍：

- 动作 `action` ：一个具有type属性的简单JS对象，用于表达一种意图或是事件；
- 归约器 `reducer` ：一个纯函数，接收当前状态和 `action` 作为参数，根据 `action` 不同，返回与不同变更过程相当的新状态；
- 存储 `store` ：应用状态的容器，通过 `reducer` 返回的初始值创建，可以通过 `store.getState()` 返回最新的状态，也可以通过 `store.dispatch()` 方法派发 `action` ，接受外部使用者订阅状态的变化。

Redux用上面这些概念，实现了一套 **单向数据流（Unidirectional Data Flow）**。

![图片](https://static001.geekbang.org/resource/image/4d/48/4d85838ae4cb4901a26d258c4d74b548.png?wh=1541x1159)

这里也有必要强调Redux的三个基本原则：

- **单一事实来源（Single Source Of Truth）**。Redux全局只有一个store，里面包含了唯一的状态对象树；
- **状态只读**。这就是在强调状态的不可变性，只有通过派发action的方式才能触发reducer，返回一个包含变更的新状态；
- **状态变更不应有副作用**。在store中使用的reducer，都必须是不会产生副作用的纯函数（Pure Function）。

这三个基本原则保证了Redux管理的应用状态是可预测的。

### Redux Toolkit

也许你听到过这样的评价：“使用Redux框架会导致代码冗长、啰嗦（verbose）。”我的建议是，不用纠结，只要想清楚你想从Redux中得到什么收益，也许这个收益足以抵消掉啰嗦带来的痛点。

一个好消息是，Redux官方已经推出了一套更易于使用的 **封装库Redux Toolkit，来简化Redux开发**：

- 降低了配置Redux store的复杂度；
- 减少了Redux所需的样板代码；
- 内置了Redux必备的扩展库。

依旧在任何JS项目中都可以安装Redux Toolkit，Redux Toolkit里已经内置了Redux，不用重复安装：

```bash
npm uninstall redux
npm install @reduxjs/toolkit

```

以下是用Redux Toolkit改写的前面Redux的代码：

```javascript
import { createSlice, configureStore } from '@reduxjs/toolkit';

const cardListSlice = createSlice({
  name: 'cardList',
  initialState: [],
  reducers: {
    addCard(state, action) {
      state.unshift(action.payload.newCard);
    },
    removeCard(state, action) {
      const index = state.findIndex(card => card.title === action.payload.title);
      if (index !== -1) {
        state.splice(index, 1);
      }
    },
  },
});
export const { addCard, removeCard } = cardListSlice.actions;

const store = configureStore({
  reducer: cardListSlice.reducer
});
store.subscribe(() => console.log(store.getState()));

store.dispatch(addCard({ newCard: { title: '开发任务-1' } }));
// [{ title: '开发任务-1' }]
store.dispatch(addCard({ newCard: { title: '测试任务-2' } }));
// [{ title: '测试任务-2' }, { title: '开发任务-1' }]
store.dispatch(removeCard({ title: '开发任务-1' }));
// [{ title: '测试任务-2' }]

```

我猜你会过来吐槽：“前面Redux的样例代码是745B，这个Redux Toolkit的样例代码是953B，代码怎么反而变多了？”

虽然场面有点尴尬，但请放心，从我实际开发经验来看， **在项目规模增大时，后者比前者减少的代码量非常可观**。顺便提一下，在写Redux代码时，为成堆的action.type起名字很容易导致决策疲劳，而用Redux Toolkit来写会好很多。

Redux Toolkit新引入了一个概念 `slice` ，即切片。切片是一组相关的state默认值、 `action` 、 `reducer` 的集合。

首先用Redux Toolkit的 `createSlice` API创建 `slice` ，然后从这个 `slice` 中拿到生成的 `actionCreator` 和 `reducer` ，用 `configureStore` API消费这个 `reducer` 创建 `store` 。接下来的步骤就与前面Redux的例子类似了，有一点区别是这边用于派发的 `action` 都是调用 `actionCreator` 创建的。

如果你的眼睛够尖，也许你已经发现了：“ `reducer` 函数的写法怎么不一样了？之前是返回新state，现在又退回了最早的 `Array.unshift()` ？”

这只是表象，其实Redux Toolkit的 `reducer` 中默认启用了Immer，也就是上节课刚学习使用的不可变数据框架。

> 它可以让JS开发者使用原生的JS数据结构，和本来不具有不可变性的JS API，创建和操作不可变数据。

这就是说，我们在Redux Toolkit中创建的 `reducer` ，可以直接用熟悉的JS API来修改状态，框架会帮我们加入state的不可变性。

除此之外，Redux Toolkit还有不少重要的功能，尤其是包括获取远程数据相关的状态管理，我们会在下节课和后面的课程中陆续涉及。

## 其他应用状态管理框架

当然，Redux也不是应用状态管理领域的唯一玩家，同样被广泛使用的还有MobX、XState等框架，下面我们来简要介绍一下。

### MobX

MobX是以透明的 **函数式响应编程（Transparent Functional Reactive Programming，TFRP）** 的方式，实现状态管理。以下是来自MobX官方文档的样例代码：

```javascript
import React from "react"
import ReactDOM from "react-dom"
import { makeAutoObservable } from "mobx"
import { observer } from "mobx-react"

// 对应用状态进行建模。
class Timer {
    secondsPassed = 0
    constructor() {
        makeAutoObservable(this)
    }
    increase() {
        this.secondsPassed += 1
    }
    reset() {
        this.secondsPassed = 0
    }
}

const myTimer = new Timer()
// 构建一个使用 observable 状态的“用户界面”。
const TimerView = observer(({ timer }) => (
    <button onClick={() => timer.reset()}>已过秒数：{timer.secondsPassed}</button>
))
ReactDOM.render(<TimerView timer={myTimer} />, document.body)

// 每秒更新一次‘已过秒数：X’中的文本。
setInterval(() => {
    myTimer.increase()
}, 1000)

```

如果你是先上手Immer，之后才接触MobX的话，会发现它们的思路很像，都鼓励你用熟悉的JS类型和方法修改数据，由框架来界定前后的变更。这并不意外，因为MobX（ [官网](https://zh.mobx.js.org/)）跟前面用到的Immer框架是同一个作者，MobX比Immer还早面世3年。

### XState

这个XState框架比起Redux和MobX来说更加硬核一些。它本身就是一个 **有限状态机**（ [维基百科](https://zh.wikipedia.org/wiki/%E6%9C%89%E9%99%90%E7%8A%B6%E6%80%81%E6%9C%BA)）的JS/TS实现，且遵守了 [W3C的XCXML规范](https://www.w3.org/TR/scxml/)。以下是来自XState官方Github，在React中使用XState的样例代码：

```javascript
import { useMachine } from '@xstate/react';
import { createMachine } from 'xstate';

const toggleMachine = createMachine({
  id: 'toggle',
  initial: 'inactive',
  states: {
    inactive: {
      on: { TOGGLE: 'active' }
    },
    active: {
      on: { TOGGLE: 'inactive' }
    }
  }
});

export const Toggler = () => {
  const [state, send] = useMachine(toggleMachine);
  return (
    <button onClick={() => send('TOGGLE')}>
      {state.value === 'inactive'
        ? 'Click to activate'
        : 'Active! Click to deactivate'}
    </button>
  );
};

```

XState还有一个强项，就是它可视化的 **状态图**：

![图片](https://static001.geekbang.org/resource/image/31/1e/3195f78ef95587edb21f5a500d50081e.png?wh=1920x1030)

可惜我自己还没有机会在生产项目中使用XState，如果你曾经用过，欢迎你在留言区分享你的经验。

## 小结

这节课我们学习了应用状态对于JS前端应用的重要意义，也学习了以Redux为代表的应用状态管理框架，介绍了Redux的核心概念 `action` 、 `reducer` 、 `store` ，以及它单向数据流的本质。

从使用角度，我们介绍了Redux封装库Redux Toolkit的用法，强调了它对Redux开发中 `action` 、 `reducer` 和不可变数据的简化。最后我们也简要介绍了另外两个应用状态管理框架MobX和XState，希望能帮到你拓宽思路。

下节课，我们会把Redux与React结合起来使用，看看它能为React的状态管理带来什么好处，同时会要探讨什么时候该用Redux，什么时候用React内建的state就好。

## 思考题

1. 这节课我们提到过Redux的 `action` 、 `reducer` 、 `dispatch` 概念，与前面第9节课学过的 `useReducer` 很类似。那么单就这节课学到的内容，可以请你把Redux和 `useReducer` 做个对比吗？
2. Redux一直在强调自己管理的状态是可预测的，那么可预测这件事本身，对我们的应用开发有什么好处吗？

好的，这节课就到这里，我们下节课再见。