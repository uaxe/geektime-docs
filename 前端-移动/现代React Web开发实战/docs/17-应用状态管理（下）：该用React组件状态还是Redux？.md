你好，我是宋一玮，欢迎回到React应用开发的学习。

上节课我们学习了应用状态对于JS前端应用的重要意义，也学习了以Redux为代表的应用状态管理框架，介绍了Redux的核心概念 `action` 、 `reducer` 、 `store` ，以及它单向数据流的本质。从使用角度，我们介绍了Redux封装库Redux Toolkit的用法，强调了它对Redux开发的简化。

不知你发现没有，上节课除了作为扩展内容的MobX和XState，我们完全没有用到React。请你放心，当然不是我忘了这个专栏的主题，而是我希望你能以更纯粹的视角，去了解应用状态管理这个领域知识，不会因为React的概念导致先入为主。

这节课，我们会把Redux与React结合起来使用，看看它能为React的状态管理带来什么好处，同时也要探讨什么时候该用Redux，什么时候用React内建的state，更或者，是否可以混用两种状态管理。

## React应用中有哪些状态？

我们在开发React应用时，会用到各种状态，大致可以分类成三种：业务状态、交互状态以及外部状态。

**业务状态是指与业务直接相关的状态，这些状态理论上剥离UI也可以使用**，比如在单元测试中、Node.js环境中等等。

举个具体的例子：oh-my-kanban中的todoList、ongoingList、doneList，用于保存看板卡片的列表，都可以增删，这些都是oh-my-kanban的核心业务，那么它们就属于业务状态。

假设我们非要为oh-my-kanban提供一套命令行下的管理工具，那么这些状态和它们相关的逻辑是可以复用的，比如下面这几行命令：

```javascript
ohmykanban list --column=ongoing
ohmykanban add --column=todo '开发任务-5'
ohmykanban remove --column=done '测试任务-2'

```

另外，在大中型React项目中的用户权限信息，也经常被存入前端状态中，方便前端逻辑判断某个功能模块是否可以对当前用户开放，或是可见但只读，再或者，直接隐藏起来。

当然，考虑到系统整体安全性，当服务器端接收到用户从浏览器端发起的请求时，仍然要验证用户权限，这类用户权限状态也属于业务状态。

**交互状态**（也称作UI状态）， **是与用户交互相关的状态，主要控制着用户与应用的交互过程，用于提升用户体验**。

比如oh-my-kanban中的isLoading、showAdd，分别控制着是否显示“读取中”占位提示，和是否显示“创建新卡片”的卡片，它们就属于交互状态。

还有，当大中型React项目中功能比较多时，常用到的Tab标签页，也常用诸如currentTab这样的交互状态来记录哪个是当前Tab。

为什么说交互状态用于提升用户体验呢？请你想象一个极端的设计，从一个React应用中删除所有交互状态，包括：

- isLoading不要了，列表拿到数据时会跳一下，还好吧；
- showAdd不要了，那“添加新卡片”默认就一直展示吧，也不是不能用；
- currentTab不要了，所有Tab下的页面内容都一次性展示出来，那……这还能称作是现代前端应用吗？

作为一个 **优秀的前端工程师，开发出优秀的用户体验是你的职责，也是你的骄傲**，我由衷希望你在这一点上不要妥协。

再来讨论一个复杂的问题， [第11节课](https://time.geekbang.org/column/article/568107?) 我们学习过受控组件和表单，那么表单状态算是业务状态还是交互状态呢？我认为需要分情况讨论，我们一起来看看。

**表单状态属于交互状态：**

- 表单状态由若干受控组件状态组成，用户在使用这些受控组件输入文本、选取下拉框时，产生的状态变更主要还是交互行为，暂时还不具有业务意义；
- 在用户录入表单过程中，如果有针对表单项的验证逻辑，比如“标题不能为空”“密码至少需要包含一个数字”，验证过程会使用表单状态，验证结果也会更新到表单状态中。这个时候验证结果已经具有业务意义了，但整体还是可以看作是交互状态。

**表单状态属于业务状态：**

- 如果表单提供了一个自动提示的下拉框，根据输入的文本内容去服务器端获取下拉框的列表，这个列表就很难说它不是业务状态了；
- 提交表单时会使用其中各个受控组件的最终状态，这时可以认为它们是业务状态；
- 如果这个表单并不是在新建一条记录，而是在修改一条已有记录，那么来自服务器端，为各个表单项提供的初始值也应该算作业务状态。

还有一个场景，比如一个名为num的状态数据，在某个组件上需要做一系列比较重的计算才能使用，比如fibonacci(num)，有些开发者为了避免反复计算影响性能，把计算结果保存在了另一个名为result的state里。

先不用讨论这个计算结果result是哪种状态，首先我们需要认识到，这是一个计算值，也可以说是派生值。无论是否使用Redux，我们都值得用单一事实来源原则来审视这个计算值：当原值num和计算值result都放在状态里，单从状态层面看，是看不出它们的因果关系的。

更合适的做法是，在状态里只保留原值num，组件里从始至终都基于num做计算。那性能怎么保证呢？我们在 [第10节课](https://time.geekbang.org/column/article/566856) 学习过的useMemo就是干这事的：

```javascript
const memoizedResult = useMemo(() => fibonacci(num), [num]);

```

上面讨论了业务状态和交互状态，那 **外部状态** 是怎么回事？在外部不就意味着与React无关了吗？我举个例子你可能就理解了：window.location。

在React生态中，最常用的前端路由框架就是React-Router了。React-Router在前端做路由时，会读取window.location的信息，也会通过浏览器History API，修改location的URL。这从实际上来看，就成为了React应用状态的一部分。

其实不仅React，业务状态、交互状态、外部状态的分类对很多其他前端框架也适用。

你这时可能就会有疑问了：“给状态分类是很好，但有什么用？”别急，接下来会用到。

## 全局状态与局部状态

单看API，state对单个React组件是私有的，但从单向数据流的角度看，一个组件的state还可以覆盖到它的所有后代组件。你可以花一分钟研究一下下面这张图，我们再继续往下分析。

![图片](https://static001.geekbang.org/resource/image/d8/yy/d8ec523a9b830d2401ea3ee99ca8c9yy.png?wh=1920x1129)

`ParentComponent` 的state `A` ：

- 可以自用；
- 可以通过props传给直接子组件 `MyComponent` ；
- 也可以通过props向下钻取，传给第二层和第三层的后代组件 `MyChildComponent` 、 `MyGrandchildComponent` ；
- 更可以通过context，传给所有的后代组件。

而 `MyChildComponent` 的state `B` 的范围虽然要小很多，但跟state `A` 会有一定重合，即 `MyChildComponent` 、 `MyGrandchildComponent` 可以同时使用 state `A` 和 `B` 的值。

如果 `ParentComponent` 已经是应用的根组件，那么可以认为state `A` 就是全局状态，而state `B` 就是局部状态。

当然，全局状态和局部状态是相对而言的。如果你的根组件并未提供状态，而它的唯一子组件提供了状态，那么这个状态也是全局状态。

局部状态也可以通过 [第13节课](https://time.geekbang.org/column/article/574161) 讲到的 **状态提升** 这样的开发技巧，根据需要改写为全局状态。

这个时候你可能会有新的疑问：“区分全局与局部状态是很好，但有什么用？”我们接着往下讲。

## 什么时候使用Redux？

一般情况下，当你的React项目足够小，引入Redux的成本要大于收益。只有你 **预期项目规模会逐渐增大，或者项目已经是大中型的体量了**，这时可以考虑引入Redux。Redux鼓励全局只有单一store，所以比较适合管理全局状态。

尤其有一种情况，当你发现，你不得不把项目中大部分组件的state都提升到根组件上时，全局状态会不断膨胀，那你就有可能亟需引入Redux了。

虽然与事实不符，但这里姑且可以认为Redux是React单向数据流的一层 **抽象**。Redux可以独立于React存在，在开发React应用时编写的Redux代码，与React的耦合度比较低，可以独立开发、测试。

给你爆个料，在上节课，Redux和Redux Toolkit的两段样例代码，我就是用Node直接跑的：

```bash
npm install redux # 或 npm install @reduxjs/toolkit
node index.js

```

将这部分数据流抽象出来后，会降低根组件state的复杂度，在编写Redux数据流逻辑时，也可以做到与React组件的 **关注点分离（Separation Of Concerns）**。

另外， **Redux对状态的变更和读取也是解耦的**。比如用createSlice接口创建了2个slice，共同组成store，reducer分别更改对应的state节点，同时开发者也可以跨slice创建selector来组合使用多个state节点里的数据。

其中createSelector API其实就是reselect库（ [官网](https://github.com/reduxjs/reselect)），用于创建记忆化的选择器函数：

```javascript
import { createSelector } from "@reduxjs/toolkit";
// ...
const selectBooks = (state) => state.books.allBooks;
const selectFavIds = (state) => state.user.favIds;

export const selectFavBooks = createSelector(
  selectBooks,
  selectFavIds,
  (books, ids) => {
    return books.filter(book => ids.includes(book.id));
  },
);

```

下面看看如何在React中使用Redux。

### React Redux

我们在React中使用Redux，一般会借助Redux官方的 **React连接器React Redux：**

```javascript
npm install @reduxjs/toolkit react-redux

```

用Provider组件包住整个应用，传入上节课Redux Toolkit样例代码中创建的store对象：

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
// ...
import { Provider } from 'react-redux';
import store from './store';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <Provider store={store}>
    <App />
  </Provider>
);

```

然后在组件中就可以使用这个store了：

```javascript
import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addCard, removeCard } from './cardListSlice';

export function CardList() {
  const cardList = useSelector(state => state);
  const dispatch = useDispatch();

  return (
    <div>
      <button onClick={() => {
        const payload = { newCard: { title: '开发任务-1' } };
        dispatch(addCard(payload));
      }}>添加</button>
      <ul>
        {
          cardList.map(card => (
            <li key={card.title}>
              {card.title}
              <button onClick={() => {
                dispatch(removeCard({ title: '开发任务-1' }));
              }}>删除</button>
            </li>
          ))
        }
      </ul>
    </div>
  );
}

```

相信你用CRA很快就能实现这个小Demo：

![图片](https://static001.geekbang.org/resource/image/40/49/401ef797d75c6db9972c3e329bf27f49.png?wh=1920x1030)

这里只是一段临时的例子代码，并不代表我们需要用Redux来改写oh-my-kanban项目或者你的yeah-my-kanban项目。根据前面的什么时候用Redux的条件，这两个项目目前还不适合引入Redux。

感谢“学习前端-react”同学在 [第12节课](https://time.geekbang.org/column/article/571276) 留言区的提问，我在这里也稍微提一下React Redux的原理。

这个库把Redux的 `store` 放到了context里，但并 **没有借助React的context更新机制** 来响应store内部的更新。在早期版本中，React Redux提供的高阶组件订阅store变化，当有变化时调用组件的 `forceUpdate()` 方法。

而在新版（v8.0）中，高阶组件使用了React的新Hooks API： `useSyncExternalStore` ，用这个Hook返回的props来更新被修饰的组件。如果你感兴趣，也可以读一读React Redux的 [发展史](https://blog.isquaredsoftware.com/2018/11/react-redux-history-implementation/)。

### Redux DevTools浏览器扩展

经过多年的积累，Redux开发的生态圈非常丰富，其中我首先推荐的是Redux官方推出的Redux DevTools浏览器扩展（ [Chrome扩展链接](https://chrome.google.com/webstore/detail/redux-devtools/lmhkpmbekcpmknklioeibfkpmmfibljd?hl=en)、 [Firefox扩展链接](https://addons.mozilla.org/en-US/firefox/addon/reduxdevtools/)），可以用来跟踪调试state和action包含的数据，还提供了一个很酷的 **时间旅行功能**。

![图片](https://static001.geekbang.org/resource/image/76/a7/766a704b7b1e35a18ce733c7130529a7.gif?wh=1200x580)

上面的介绍可能引起了你对Redux的一些兴趣，但学习归学习，实际项目中还是要认真考虑是否该引入Redux。

了解了什么时候使用Redux，那么什么时候使用React内建state呢？如果你本来就不打算引入Redux，任何时候都可以使用React内建state。

## 可否混用React内建state和Redux？

我们进入今天这节课的最后一个问题：“可否混用React内建state和Redux？”当然可以。当你决定了为项目引入Redux，并不意味着你就与useState说再见了。它们 **可以共存，而且可以配合得很好**。

一般情况下可以这样分工：

- 全局状态倾向于放到Redux store里；
- 局部状态倾向于放到React state里；
- 业务状态倾向于放到Redux store里；
- 交互状态倾向于放到React state里；
- 必要时，可以把外部状态同步到Redux store里。

这里我插一个经济学和社会学概念： **路径依赖（Path Dependence），说的是人们在当前做的决策选择往往受制于他过去的决策，哪怕所处环境已经发生变化**。最著名的例子是QWERTY键盘的历史，感兴趣的话你可以上网搜一下，这个概念本来不具有贬义或者褒义。

我曾见过不少开发者，在React中引入Redux后，无论大大小小的状态都习惯性地往Redux store里放，这就是一种路径依赖了。这样做的后果也很容易想象得到： **Redux store不堪重负，React反而头重脚轻**。

## 小结

这节课我们继续上节课应用状态管理的内容，介绍了React应用中的三种状态：业务状态、交互状态和外部状态，并且学习了从数据流层面区分的全局状态和局部状态。

紧接着我们学习了什么时候为React项目引入Redux、如何用React Redux连接器，最后总结了混用React内建state和Redux store的一些分工建议。

这节课讲了这么多应用状态，那么应用状态算不算是React应用的数据模型呢？如果是的话，该如何保证模型的schema（模式）呢？下节课我们会学习如何活用PropTypes和TypeScript，在React应用中加入数据类型验证。

## 思考题

这节课虽然写了一个很小的React Redux Demo，但并不打算用Redux来改写oh-my-kanban或者yeah-my-kanban项目。

你愿意接受这个挑战吗？如果愿意的话，请建一个fork或者分支，把最新的代码用Redux改写一遍，然后在留言区留下你的代码仓库链接与大家分享，或者留一个“M”字样代表你很满意自己的成果。

你将遇到的具体挑战包括：

1. 在课程中并没有把Redux Toolkit和React Redux的所有API都展示出来，你需要参考官方文档；
2. 三个看板列状态数据结构和操作都相同，你会怎么设计slice、reducer？当然，直接创建三个相似的slice也是完全ok的；
3. 哪些状态会放在Redux store中，哪些会放在React state中。

这节课内容就到这里。我们下节课再见。