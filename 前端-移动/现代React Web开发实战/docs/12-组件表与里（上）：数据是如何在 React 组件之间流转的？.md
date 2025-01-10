你好，我是宋一玮，欢迎回到React应用开发的学习。

上节课我们学习了React的事件处理，理解了React事件是标准化封装过的合成事件。在这基础之上，还学习了受控组件和事件冒泡/捕获的概念，并为 `oh-my-kanban` 项目加入了实用的卡片拖拽功能。其间我们也不忘与浏览器原生DOM事件作对比。

到目前为止，包括生命周期、Hooks、事件处理，你已经基本了解了可以在哪些位置编写组件逻辑代码。那么当你在React应用中写了多段逻辑代码后，代码之间是怎么串联起来的？反过来说，怎样才能把每段代码写在它合适的地方，让它们各司其职，支撑应用跑起来呢？

接下来我们会用两节课的时间，把视野从单个React组件中拓展开来，看看 **组件与组件之间的分工和交互，** 从而帮助你解决刚才提出的问题。

我把这两节课分别称为组件的“面子”和“里子”。这节课的重点，是React的 **单向数据流**。当你理解了在React的设计哲学中数据应该如何流转，就会对如何设计props和state了然于心。

在学习概念的基础上，也请你跟随我，从数据流的视角重新梳理早在第5节课就基本定型的 `oh-my-kanban` 各组件，进行一次 **大重构：对组件文件进行拆分，并根据需要调整各组件的props和state**。同时我们也会学习React另一个与数据流相关的概念——context。

顺带预告一下，在下节课，我们会参照 `oh-my-kanban` 重构前后的组件层次结构，进一步讲解如何用面向接口编程的思路来设计开发React组件和应用。

下面开始这节课的内容。

## 什么是数据流？

提到数据流，要先提一下 **函数响应式编程**（Functional Reactive Programming），顾名思义，函数响应式编程是一种利用函数式编程的部件进行响应式编程的编程范式。

**数据流**（Data Flow）则是其中响应式编程的重要概念，响应式编程将程序逻辑建模成为在 **运算（Operation）之间流动的数据及其变化**。

举个最简单的例子，对于 `b = a * 2` 这个赋值语句，如果把 `a * 2` 定义为一个运算，那么如果流动进来的 `a` 发生了改变，则 `b` 会自动响应前者的变化。

估计你看到这个例子，马上就会想到React的设计哲学 `UI = f(state)` ，比如一个函数组件 `({ a }) => (<div>{ a * 2 }</div>)` ，只要prop属性 `a` 发生变化，组件渲染的 `<div>` 包含的内容就会自动变化。

当然，一个程序往往会包含多个运算，当数据流经过多个运算时，每个运算只负责自己的部分，这样的数据处理过程有点像是工厂流水线。那类比到React应用呢？

我们知道React的开发单元是组件，多个组件在运行时会形成一颗组件树，根组件会沿着子组件树传递数据。对于任意一条从根组件到叶子节点组件的路径，都可以看作是一条工厂流水线。而每个组件都是流水线上的一道工序，对流过的数据各取所需，完成本职工作。

## React的数据流包含哪些数据？

React的数据流主要包含了三种数据： **属性props、状态state和上下文context**。这三个概念在React中算是专有名词，为避免歧义，我在本课程中将沿用它们的英文名称。我们先来系统地看一下props。

### Props

自定义React组件接受一组输入参数，用于改变组件运行时的行为，这组参数就是props。

在声明函数组件时，函数的第一个参数就是props。以下两种写法都很常见：

- 一个是在组件内部读取props对象的属性；
- 另一个是通过ES6的解构赋值语法（Destructuring Assignment）展开函数参数，直接在组件内部读取单个prop变量。

这两种写法本质上都是相同的：

```javascript
// 1
function MyComponent(props) {
  return (
    <ul>
      <li>{props.prop1}</li>
      <li>{props.prop2}</li>
    </ul>
  );
}

// 2
function MyComponent({ prop1, prop2 }) {
  return (
    <ul>
      <li>{prop1}</li>
      <li>{prop2}</li>
    </ul>
  );
}

```

第二种写法有些很方便的功能，比如为prop设置默认值：

```javascript
function MyComponent({ prop1, prop2, optionalProp = 'default' }) {

```

以及利用ES2018的Rest Properties语法，将解构剩余属性赋值给一个变量，便于透传给子元素：

```javascript
function MyComponent({ prop1, prop2, ...restProps }) {
  return (
    <ul {...restProps}>
      <li>{prop1}</li>
      <li>{prop2}</li>
    </ul>
  );
}

```

顺带一提，类组件的props可以通过 `this.props` 读取：

```javascript
class MyLegacyClassComponent extends React.Component {
  render() {
    return (
      <ul>
        <li>{this.props.prop1}</li>
        <li>{this.props.prop2}</li>
      </ul>
    );
  }
}

```

需要注意的是，无论是哪种写法，props都是 **不可变** 的，不能在组件内改写从外面传进来的props。

上面了解了如何声明props，再看看如何赋值。在其他组件中使用子组件时，可以通过JSX语法为子组件的props赋值：

```javascript
const ParentComponent = () => (
  <MyComponent prop1="文本" prop2={123} booleanProp={false}
    onClick={(evt) => {console.log('clicked')}} />
);

```

当prop值为布尔值的 `true` 时，JSX可以简写成 `<MyComponent booleanProp />` 。此外还有一个特殊的props：代表子元素的 `children`。

请回忆一下你在第5节课拆分 `oh-my-kanban` 项目组件时，在 `<KanbanBoard>` 组件的JSX闭合标签中加入子元素 `<KanbanColumn>` ，子元素会被赋值给该组件props里的 `children` 属性，在 `<KanbanBoard>` 组件的函数内部即可使用这个 `props.children`。 `<KanbanColumn>` 与 `<KanbanCard>` 之间也是类似的。

以及两个形式上像props，但并不是props的属性：

- 形成列表的子元素的 `key` ，我们在第6节课学习过。
- 引用DOM元素的 `ref` ，我们在第9节课学习过。

`key` 和 `ref` 的特殊之处还在于，当子元素是自定义组件时，在子组件内部是不能读取传给它的 `key` 或 `ref` 值的，如果尝试读取，React则会在控制台提示，也就是 `Warning: KanbanCard: ` key `is not a prop. Trying to access it will result in` undefined ` being returned`；如果确实需要在子组件中访问 `key` 或 `ref` 的值，就得用另一个额外的prop传进来。

说回数据流， **props的数据流向是单向的，只能从父组件流向子组件**，而不能从子组件流回父组件，也不能从当前组件流向平级组件。如下图所示：

![](https://static001.geekbang.org/resource/image/7b/b0/7babcd38e678fa204a0afb9b423a91b0.jpg?wh=1142x687)

### State

在props之外，组件也可以拥有自己的数据。对于一个函数而言，“自己的数据”一般是指函数内声明的变量。

而对一个函数组件来说，因为每次渲染函数体都会重新执行，函数体内变量也会被重新声明，如果需要组件在它的生命周期期间拥有一个“稳定存在”的数据，那就需要为组件引入一个专有的概念，即state。

在函数组件中使用state，需要调用 `useState` / `useReducer` Hooks。这两个Hooks在第9节课刚学习过，在此只放一段例子代码，不再赘述。

```javascript
function MyComponent() {
  const [state1, setState1] = useState('文本');
  const [state2, setState2] = useState(123);
  const handleClick = () => {
    setState1('更新文本');
    setState2(456);
  };
  return (
    <ul>
      <li>{state1}</li>
      <li>{state2}</li>
      <li><button onClick={handleClick}>更新state</button></li>
    </ul>
  );
}

```

姑且提一下类组件的state，在类组件内可以通过 `this.state` 读取state，通过 `this.setState` 修改state，唯一例外是在类组件构造函数里，可以通过赋值 `this.state` 的方式设置初始值，与Hooks的state不同，类组件的state总是以对象形式存在：

```javascript
class MyLegacyClassComponent extends React.Component {
  constructor() {
    this.state = { state1: '文本', state2: 123 };
  }

  handleClick = () => {
    this.setState({ state1: '更新文本', state2: 456 })
  }

  render() {
    return (
      <ul>
        <li>{this.state.state1}</li>
        <li>{this.state.state2}</li>
        <li><button onClick={this.handleClick}>更新state</button></li>
      </ul>
    );
  }
}

```

不过需要反复强调的是，state与props一样，也是 **不可变** 的。需要修改state时，不能直接给state变量赋值，而是必须调用state更新函数，即 `setXxx` / `dispatch` 或 `this.setState` 。

当组件的state发生改变时，组件将重新渲染。那什么才算是改变呢？从底层实现来看，React框架是用 [Object.is()](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Object/is) 来判断两个值是否不同的。尤其注意，当新旧值都是对象、数组、函数时，判断依据是它们的值引用是否不同。

对同一个对象属性的修改不会改变对象的值引用，对同一个数组成员的修改也不会改变数组的值引用，在React中都不认为是变化。所以在更新这类state时，需要新建对象、数组：

```javascript
function MyComponent() {
  const [obj, setObj] = useState({ a: '文本', b: true });
  const [arr, setArr] = useState([1, 2, 3]);
  const handleClick = () => {
    setObj({...obj, a: '更新文本'}); // ...对象展开语法
    setArr([...arr, 4, 5, 6]); // ...数组展开语法
  };
  return (
    <ul>
      <li>{obj.a}</li>
      <li>{arr.join(',')}</li>
      <li><button onClick={handleClick}>更新state</button></li>
    </ul>
  );
}

```

还有要注意的就是state更新的 **异步性** 和 **自动批处理**。如果印象有些模糊了，那请你务必复习一下第9节课的内容。

再来看看state的数据流向，当读取和更改state都发生在同一组件中时，state的流动仅限于当前组件之内。

如果希望由子组件或后代组件来更改state，需要将对应的state更新函数包在另一个函数，比如事件处理函数中，然后将函数以props或context的方式传给子组件或后代组件，由它们来决定调用的时机和参数。当这个函数被调用，state被更新，当前组件则会重新传染。

如下图所示，可以帮助你理解：

![](https://static001.geekbang.org/resource/image/75/0b/7595dddd7a3164b7b6ce859b8bcc800b.jpg?wh=1142x759)

### Context

“终于”，你也许会感叹，“终于讲到context了”。React很早就引入了context这个概念，它的API也经历过新老版本的更迭，用于组件跨越多个组件层次结构，向后代组件传递和共享“全局”数据。

使用context分三个步骤：

1. 调用 `React.createContext` 方法创建 `Context` 对象，如 `MyContext` ：

```javascript
const MyContext = React.createContext('没路用的初始值');

```

2. 在组件JSX中使用 `<MyContext.Provider>` 组件，定义 `value` 值，并将子组件声明在前者的闭合标签里：

```javascript
function MyComponent() {
  const [state1, setState1] = useState('文本');
  const handleClick = () => {
    setState1('更新文本');
  };
  return (
    <MyContext.Provider value={state1}>
      <ul>
        <MyChildComponent />
        <li><button onClick={handleClick}>更新state</button></li>
      </ul>
    </MyContext.Provider>
  );
}

```

3. 在子组件或后代组件中使用 `useContext` Hook获取 `MyContext` 的值，这个组件就成为MyContext的消费者（Consumer）：

```javascript
function MyChildComponent() {
  return (
    <MyGrandchildComponent />
  );
}

function MyGrandchildComponent() {
  const value = useContext(MyContext);
  return (
    <li>{value}</li>
  );
}

```

其中 `MyContext.Provider` 是可以嵌套使用的。 `MyGrandchildComponent` 组件会去到组件树，从它的祖先节点中找到离它最近的 `MyContext.Provider` 即 `MyComponent` ，读取后者的 `value` 值；当 `MyComponent` 的 `state1` ，也就是 `MyContext.Provider` 的 `value` 值发生更改时，会通知到它后代组件中所有消费者组件重新渲染。

Context.Provider的value值也可以传一个对象进去，但要注意写法，避免在组件重新渲染时反复创建新的对象，比如利用state或 `useMemo` ：

```javascript
// 不要这样写
function MyComponent() {
  const [state1, setState1] = useState('文本');
  // ...
  return (
    <MyContext.Provider value={{ key1: state1 }}>
      <MyChildComponent />
    </MyContext.Provider>
  );
}

// 可以利用state
function MyComponent() {
  const [obj, setObj] = useState({ key1: '文本' })
  // ...
  return (
    <MyContext.Provider value={obj}>
      <MyChildComponent />
    </MyContext.Provider>
  );
}

// 也可以利用useMemo
function MyComponent() {
  const [state1, setState1] = useState('文本');
  const obj = useMemo(() => ({ key1: state1 }), [state1]);
  // ...
  return (
    <MyContext.Provider value={obj}>
      <MyChildComponent />
    </MyContext.Provider>
  );
}

```

从数据流的角度看， **context的数据流向也是单向的，只能从声明了** `Context.Provider` **的当前组件传递给它的子组件树**，即子组件和后代组件。而不能向父组件或祖先组件传递，也不能向当前子组件树之外的其他分支组件树传递。正如下图所示：

![](https://static001.geekbang.org/resource/image/1f/cc/1fec023c27077010ef7e61dd1960e6cc.jpg?wh=1000x563)

至此，我们介绍完了props、state和context这三个概念。其中props和state，我们已经在 `oh-my-kanban` 中做了丰富的实践，至于context，我们下节课会利用它为看板加入管理员功能。接下来，仍然让我们将注意力集中在数据流上。

## React单向数据流

刚才介绍的props、state和context三种数据，共同组成了React组件的数据流。早在第5节课我们就已经学习过，React是一种声明式的前端框架，在React的数据流上也体现了这一点。在典型场景下，你可以通过 **声明这三种数据来设计React应用的数据流，进而控制应用的交互和逻辑**。

只有这三种数据的变更会自动通知到React框架，触发组件必要的重新渲染。当你的数据流中混入了不属于它们其中任意一种的数据，就要小心，这种 **跳出“三界之外”的数据很有可能带来Bug**，比如数据改变了但组件并不重新渲染。

这种Bug其实并不难定位，但当项目代码比较多，逻辑变得复杂时，你还是有可能会搞混数据的来源，花不少时间去Debug。顺便提一下，“三界之外”这个说法来自于我的一位同事，当时她正是遇到了这类Bug，我们一起调试了好久才恍然大悟。

虽然说props、state和context是不同的概念，但从一棵组件树的多个组件来看，同一条数据在引用不变的前提下，在传递过程中却可以具有多重身份。

比如，一条数据最初来自于组件A的state，通过props传递给子组件B后就成为了组件B的prop。再比如，另一条数据来自于组件A的state，通过在A中声明context传给了子组件树，子组件B的子组件C消费了这个context值。

从三者分别的流向可知，React整体的数据流也是单向的，如下图所示：

![](https://static001.geekbang.org/resource/image/02/e1/0221e1ce4ae5e2afc0650eb419ac27e1.jpg?wh=1142x642)

## 基于数据流再做一次组件拆分

好了，讲完了React数据流的概念，我们来到了约定好的 `oh-my-kanban` “ **大重构**”。

首先强调一点，大部分时候我们 **不应该为了重构而重构，除非我们很清楚重构的目标范围、预期收益、成本和存在的风险**。

这次的重构当然在一定程度上是为了教学目的，不过我还是会列（xiā）举（biān）一些重构 `oh-my-kanban` 的动机和目标：

1. 目前300多行源代码集中在 `src/App.js` 中，希望重构后能 **分散** 到多个源文件中；
2. 目前主要业务逻辑都集中在 `App` 组件上，希望重构后能 **分摊** 到其他组件；
3. 将CSS-in-JS样式代码直接写在JSX标签上有点喧宾夺主，希望重构后能 **独立** 些。

针对第二个目标，在重构过程中我们会遇到一系列与数据流相关的决策。这些重构步骤和决策思路我们会留到下节课，而这节课我们会先完成第一个和第三个重构目标，为下节课的重构工作做好充分准备。

好的，我们开始重构。车速会比较快，希望你能跟紧。

## 重构第一步：抽取组件到独立文件

我们将利用VSCode的重构功能来减少重构的工作量。在 `src/App.js` 中，光标选中 `KanbanBoard` 组件的全部代码：

![图片](https://static001.geekbang.org/resource/image/d1/yy/d1b7639a24f6cd8f549d069f614c57yy.png?wh=1300x800)

接着，按快捷键 `⌃⇧R` 或右键打开重构菜单，选择“移动到新文件”：

![图片](https://static001.geekbang.org/resource/image/8c/08/8c9c465faa88069eec252e8e80397808.png?wh=1300x960)

此时，VSCode会自动创建一个新文件 `src/KanbanBoard.js` ，将这段代码移过去，并在 `src/App.js` 中加入一行 `import` 语句导入 `KanbanBoard` 组件：

![图片](https://static001.geekbang.org/resource/image/09/1e/0992a59f59c75b87c8020cffa73bd81e.png?wh=1920x1004)

根据社区常见的代码约定（Convention），我们希望与文件名同名的组件是这个文件的默认导出项。让我们再做两个重构操作。首先选中 `KanbanBoard` 变量名，打开重构菜单，选择“转换为命名函数”，这样可以保证组件在React开发者工具中有显示名称：

![图片](https://static001.geekbang.org/resource/image/48/8e/483deba71864a263b4b8fae16ff2448e.png?wh=1300x900)

然后马上对这个命名函数再做一次重构，“将命名导出项转换为默认导出项”：

![图片](https://static001.geekbang.org/resource/image/58/eb/586bdd3830780aa713edce1739ea4beb.png?wh=1300x800)

可以回头看一下 `src/App.js` ，导入语句也自动更新了。继续选中css属性内的所有内容，打开重构菜单，选择“抽取为模块范围的常量”，取个好听的变量名（关于如何起好变量名，建议参考Martin Fowler大神的《重构》）：

![图片](https://static001.geekbang.org/resource/image/06/af/0606f908e2e4c307af7ce8aec3afe4af.png?wh=1300x800)

稍微修正一下代码缩进， `src/KanbanBoard.js` 目前的代码如下：

```javascript
import React from 'react';
import { css } from '@emotion/react';

const kanbanBoardStyles = css`
  flex: 10;
  display: flex;
  flex-direction: row;
  gap: 1rem;
  margin: 0 1rem 1rem;
`;

export default function KanbanBoard({ children }) {
  return (
    <main css={kanbanBoardStyles}>{children}</main>
  );
}

```

恭喜你成功拆分出来第一个独立组件JS，代码看着很清爽！跑 `npm start` 验证一下：

![图片](https://static001.geekbang.org/resource/image/db/83/db1906cc8912681b0e5ef1f06f55c383.png?wh=1920x1030)

诶？样式没生效？不要惊慌，还记得我们第7节课引入 `emotion` 框架时，为组件加入的 `JSX Pragma` （编译指示）吗？这里也需要：

```diff
+/** @jsxImportSource @emotion/react */
 import React from 'react';
 import { css } from '@emotion/react';

```

保存文件，样式恢复正常了。

以此类推，请你继续抽取 `KanbanColumn` 、 `KanbanCard` 、 `KanbanNewCard` 。下面是一些关键代码的提示：

![图片](https://static001.geekbang.org/resource/image/5e/e5/5e8b133f370bd99943dc35625815a4e5.png?wh=1920x1487)

`src/KanbanCard.js` 的关键代码的提示如下：

```javascript
/** @jsxImportSource @emotion/react */
import React, { useEffect, useState } from 'react';
import { css } from '@emotion/react';

export const kanbanCardStyles = css`
  margin-bottom: 1rem;
  /*...省略*/
`;
export const kanbanCardTitleStyles = css`
  min-height: 3rem;
`;

const MINUTE = 60 * 1000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;
const UPDATE_INTERVAL = MINUTE;

export default function KanbanCard({ title, status, onDragStart }) {
  const [displayTime, setDisplayTime] = useState(status);
  useEffect(() => {
    const updateDisplayTime = () => {/*...省略*/};
    const intervalId = setInterval(updateDisplayTime, UPDATE_INTERVAL);
    // ...省略
  }, [status]);
  // ...省略

  return (
    <li css={kanbanCardStyles} draggable onDragStart={handleDragStart}>
      {/*...省略*/}
    </li>
  );
}

```

`src/KanbanNewCard.js` 的关键代码的提示如下：

```javascript
/** @jsxImportSource @emotion/react */
import React, { useEffect, useRef, useState } from 'react';
import { css } from '@emotion/react';
import { kanbanCardStyles, kanbanCardTitleStyles } from './KanbanCard';

export default function KanbanNewCard({ onSubmit }) {

```

`src/KanbanColumn.js` 的关键代码的提示如下：

```javascript
/** @jsxImportSource @emotion/react */
import React from 'react';
import { css } from '@emotion/react';

const kanbanColumnStyles = css`
  flex: 1 1;
  display: flex;
  flex-direction: column;
  border: 1px solid gray;
  border-radius: 1rem;

  & > h2 {
    /*...省略*/
  }
`;

export default function KanbanColumn({
  children, bgColor, title /*...省略*/
}) {
  return (
    <section
      {/*...省略*/}
      css={css`
        ${kanbanColumnStyles}
        background-color: ${bgColor};
      `}
    >

```

好的， `src/App.js` 还剩150余行代码，重构的第一个目标达成了。同时我们把 `css` 属性抽取成了模块内的变量，重构的第三个目标也达成了。请务必记得把你的重构成果提交到代码仓库，也欢迎分享到留言区。

## 小结

这节课我们先是借助FRP函数响应式编程理解了什么是数据流，然后较为系统地学习了React数据流的三大组成部分，分别是props、state和context。

除了它们的定义和用法外，还介绍了它们在组件中分别的流向，进而推断出整个React数据流是单向的。在这节课后半部分，我们为 `oh-my-kanban` 项目提出了重构目标，并完成了抽取组件到独立文件，作为下节课继续重构的基础。

下节课我们会聊聊如何用面向接口编程思想帮助React应用的设计开发，并结合单向数据流和面向接口思想，继续重构 `oh-my-kanban` 项目。在下节课结束时，你会发现 `oh-my-kanban` 项目已经是一个“可用”的React Web应用了！

最后，附上本节课所涉及的项目源代码： [https://gitee.com/evisong/geektime-column-oh-my-kanban/releases/tag/v0.12.0](https://gitee.com/evisong/geektime-column-oh-my-kanban/releases/tag/v0.12.0)

## 思考题

1. React的数据流为什么要设计成单向的？如果设计成双向的甚至多向的，会导致什么后果吗？
2. 我们（终于）要重构 `oh-my-kanban` 项目了，你对重构的理解是怎样的？你经历过其他哪些软件项目的重构吗？

欢迎把你的思考和想法分享在留言区，咱们下节课再见！