你好，我是宋一玮，欢迎回到React应用开发的学习。

这是专栏的第一次加餐。我和专栏编辑从已上线课程的留言区中，选择了一些具有代表性的问题。这次加餐我们先来讲讲“真·子组件”，以及JSX这一语法糖在React 17版本以后发生的变化。在心愿单里呼声同样比较高的，还有Fiber协调引擎，会放到下节加餐中。

好的，接下来开始我们的加餐内容。

## 真·子组件

在第5节课中，我曾提到过：

> React还流行过一波真·子组件（Sub-components）的设计模式，代表性的组件库有 [Semantic UI React](https://react.semantic-ui.com/#sub-components)、 [Recharts](https://recharts.org/zh-CN/guide/getting-started)……如果你感兴趣的话，在靠后面的课程中我会讲解一下这种模式的具体实现。

在React领域，一般提到中文“子组件”，指的是Child Component，用于描述在React运行时（Runtime）构建的组件树（元素树）中，组件与组件之间的父子关系。

而这里提到的Sub-components，主要还是在 **描述设计时**（Design-time） **组件与组件间的强包含关系**（Containment），而在运行时这些组件之间却不一定是父子关系。所以，把Sub-components直译成“子组件”就不太合适，我就改用了“真·子组件”这种中二的翻译，意在与Child Component区别开。事实上，“附属组件”、“次级组件”、“副组件”也都是可行的名字。

如果用真·子组件模式设计 `KanbanColumn` 组件，那么它的 `title` 属性可能是这样的：

```javascript
<KanbanColumn className="column-todo">
  <KanbanColumn.Title>
    待处理<button onClick={handleAdd}
      disabled={showAdd}>&#8853; 添加新卡片</button>
  </KanbanColumn.Title>
  {/* ...省略 */}
</KanbanColumn>

```

你也许会吐槽，这跟在 `title={}` 里直接写JSX区别不大啊。那我们再来看一个props比较复杂的组件：

```javascript
<Dialog
  modal
  onClose={() => {}}
  title="这是标题"
  titleClass="dialog-title"
  titleStyle={{ color: 'blue' }}
  content="这是正文。"
  contentClass="dialog-content"
  contentStyle={{ color: 'red' }}
  showConfirmButton={true}
  confirmButtonText="确认"
  onConfirmButtonClick={() => {}}
  showCancelButton={false}
  cancelButtonText=""
  onCancelButtonClick={() => {}}
  {/* ...还有很多props */}
/>

```

也许这个组件的设计者对加入这么多props不以为然，但这个组件的使用者们，看着茫茫props会觉得无从下手。这种情况下，双方就组件接口设计会提出如下需求：

1. 组件的props需要更加结构化、语义化；
2. 降低组件props结构与组件内部实现的耦合。

这就轮到真·子组件上场了，通过简单的梳理，我们为 `Dialog` 设计了如下几个真·子组件：

```javascript
const Dialog = (props) => {/* 待实现 */};
Dialog.Title = () => null;
Dialog.Content = () => null;
Dialog.Action = () => null;

```

期待的使用方式如下：

```javascript
<Dialog modal onClose={() => {}}>
  <Dialog.Title className="dialog-title" style={{ color: 'blue' }}>
    这是标题
  </Dialog.Title>
  <Dialog.Content>
    <p>这是正文。</p>
    <p>这是正文第二段。</p>
  </Dialog.Content>
  <Dialog.Action type="confirm" onClick={() => {}}>确认</Dialog.Action>
  <Dialog.Action type="cancel" onClick={() => {}}>取消</Dialog.Action>
</Dialog>

```

这样设计对于 `Dialog` 组件的使用者来说，还是很好用的，但对于 `Dialog` 组件的开发者就有一定挑战了。

具体来说，在渲染时，这些真·子组件与其他自定义组件一样，会创建对应的React元素出来，但它们会导致元素树变得冗长。我们并不希望这样，而只想把它们当作是 `Dialog` 组件的一种扩展属性。这就需要在 `Dialog` 的 `children` 属性上做文章。

首先基于 `React.Children` API，定义两个工具函数 `findByType` 和 `findAllByType`，用于选取 `children` 中特定类型的React元素：

```javascript
function findByType(children, type) {
  return React.Children.toArray(children).find(c => c.type === type);
}

function findAllByType(children, type) {
  return React.Children.toArray(children).filter(c => c.type === type);
}

```

然后在 `Dialog` 组件函数体中，定义渲染标题、正文和动作按钮的函数，并在返回的JSX中调用它们：

```javascript
const Dialog = ({ modal, onClose, children }) => {
  const renderTitle = () => {
    const subElement = findByType(children, Dialog.Title);
    if (subElement) {
      const { className, style, children } = subElement.props;
      return (<h1 {...{ className, style }}>{children}</h1>);
    }
    return null;
  };
  const renderContent = () => {
    const subElement = findByType(children, Dialog.Content);
    return subElement?.props?.children;
  };
  const renderButtons = () => {
    const subElements = findAllByType(children, Dialog.Action);
    return subElements.map(({ props: { onClick, children } }) => (
      <button onClick={onClick} key={children}>{children}</button>
    ));
  };
  return (
    <dialog open>
      <header>{renderTitle()}</header>
      <main>{renderContent()}</main>
      <footer>{renderButtons()}</footer>
    </dialog>
  );
};
Dialog.Title = () => null;
Dialog.Content = () => null;
Dialog.Action = () => null;

```

可以看到，三个渲染函数行为都稍有不同， `renderTitle` 是从 `<Dialog.Title>` 中获取 `className` 、 `children` 等props，然后用在 `<h1>` 上； `renderContent` 是直接返回 `<Dialog.Content>` 的 `children` 子元素；而 `renderButtons` 则是从多个 `<Dialog.Action>` 中获取多组 `onClick` 、 `children` 属性，然后分别渲染成 `<button>`。

在浏览器中可以观察到渲染结果：

![图片](https://static001.geekbang.org/resource/image/b7/9c/b7607fef52dd3357eccb67ed61b92a9c.png?wh=774x643)

还有一种情况，如果是用真·子组件定义类似模版的元素，在组件中有可能需要调用 `React.cloneElement` API来克隆这个模版元素。

更详细的例子请参考 [Github上Semantic-UI-React的v3版本](https://github.com/Semantic-Org/Semantic-UI-React/tree/next-v3)。之所以推荐v3版本，是因为这个版本大量使用了组件函数+Hooks，而目前主干版本的v2.x，主要还是基于类组件实现的。

除了真·子组件，你仍然有其他选择可以实现上述目标：

- 使用类似JSON这样的DSL（Domain Specific Language）作为props，让组件内部逻辑解析DSL来决定如何渲染；
- 组件的组合（Composition），这方面的知识和最佳实践，我们在后面第18节课代码复用会讲到。

## React 17/18中的react/jsx-runtime

在第4节课我们提到过JSX是 `React.createElement` 的语法糖。如果你对React底层实现感兴趣，那你也需要了解这个语法糖在React新版中的变化：React从17版本开始已经启用全新的JSX运行时来替代 `React.createElement` 。这要感谢留言区“ _Geek\_fcdf7b_ ”同学的提醒。

在启用新JSX运行时的状态下，用代码编译器编译JSX：

- 在生产模式下被编译成了 `react/jsx-runtime` 下的 `jsx` 或 `jsxs` （目前同 `jsx` ）；
- 在开发模式下JSX被编译成了 `react/jsx-dev-runtime` 下的 `jsxDEV` 。

作为编译输入，JSX的语法没有改变，编译输出无论是 `jsx-runtime` 还是 `React.createElement` 函数，它们的返回值也同样都是React元素。可见，代码编译器为开发者隐藏了新旧API的差异。这个变化并不影响已有的对JSX的理解。

另外，如果是开发者手工创建React元素，依旧应该调用 `React.createElement` 。这个API并不会被移除。而 `jsx-runtime` 代码只应由编译器生成，开发者不应直接调用这个函数。

在React 17版本，新JSX运行时的具体更新日志可参考：  [https://zh-hans.reactjs.org/blog/2020/09/22/introducing-the-new-jsx-transform.html](https://zh-hans.reactjs.org/blog/2020/09/22/introducing-the-new-jsx-transform.html) ；

引入新JSX运行时的动机主要是因为原有的 `React.createElement` 是为了类组件设计的，而目前函数组件已然成为主流，老接口限制了进一步的优化，具体可以参考官方的征求意见贴： [https://github.com/reactjs/rfcs/pull/107](https://github.com/reactjs/rfcs/pull/107) 。里面提及React v0.12版本以来JSX的实现，在性能优化方面存在一些痛点，包括：

- 每次创建元素时都需要动态检查组件是否用 `.defaultProps` 定义了props默认值；
- 在 `React.lazy` 懒加载中，更是需要在渲染阶段解析props默认值；
- 子元素 `children` 需要被动态合并到props中，导致调用方无法更早获知元素props的完整结构；
- 从JSX编译出来的 `React.createElement` 是React对象的属性，而不是更容易优化的模块范围常量；
- 无法确定传入的props是否是一个用户创建的可变对象，所以每次都必须克隆对象；
- 必须从props中取出 `key` 和 `ref` ；
- 同样是 `key` 和 `ref` ，也有可能以属性展开的方式传进来，如 `<div {...props} />` ，我们需要动态检查其中是否有这两个属性；
- 要想让JSX编译出来的 `React.createElement` 生效，需要模块显式导入 `React`。

为了解决上面这些痛点，以及在远期能对React框架的部分概念做简化，React官方将陆续引入三个步骤：

1. 新的JSX编译目标；
2. 对部分功能标注即将弃用；
3. 语义层面的破坏性更新。

React 17版本加入的新JSX运行时就是这第一步。与 `React.createElement` 相比的变化包括：

- 自动导入；
- 在props之外传递 `key` 属性；
- 将 `children` 直接作为props的一部分；
- 分离生产模式和开发模式的JSX运行时。

我在 `oh-my-kanban` 项目里验证了一下，确实。

```javascript
var KanbanCard = function KanbanCard(_ref) {
  var title = _ref.title,
    status = _ref.status;
  return /*#__PURE__*/ (0, jsx_runtime.jsxs)("li", {
    className: "kanban-card",
    children: [
      /*#__PURE__*/ (0, jsx_runtime.jsx)("div", {
        className: "card-title",
        children: title,
      }),
      /*#__PURE__*/ (0, jsx_runtime.jsx)("div", {
        className: "card-status",
        children: status,
      }),
    ],
  });
};

```

从编译结果看，与 `React.createElement` 在 `children` 的处理上是不同， `jsx_runtime.jsx` 的 `children` 直接就是props的一部分。

在本专栏选用的React 18.2.0版本和与它配套的CRA中，新JSX运行时也是被默认启用的。

好了，这节加餐就到这里。如果你还有其他想听的话题，或者在课程学习中有什么疑问，欢迎在留言区告诉我。下节课再见！