你好，我是宋一玮。上节课我们利用Create React App（CRA）脚手架工具创建了一个React项目，并在项目中部分实现了一个简单的看板应用。在接下来的课程里，我们会把看板应用抽丝剥茧，逐一认识学习项目里涉及到的React概念和API。很自然地，我们这节课会讲到JSX语法和React组件。

有不少初学者对React的第一印象就是JSX语法，以至于会有这样的误解：

- JSX就是React？
- JSX就是React组件？
- JSX就是另一种HTML？
- JSX既能声明视图，又能混入JS表达式，那是不是可以把所有逻辑都写在JSX里？

这些误解常会导致开发时遇到各种问题：

- 写出连续超百行、甚至近千行的JSX代码，既冗长又难维护；
- 在JSX的标签上添加了HTML属性却不生效；
- JSX混入JS表达式后，页面一直报错。

其实只要 **理清了JSX和React组件的关系**，这些问题自然不在话下。

总的来说，React是一套声明式的、组件化的前端框架。顾名思义， **声明（动词）组件** 是React前端开发工作最重要的组成部分。在声明组件的代码中使用了JSX语法，JSX不是HTML，也不是组件的全部。

接下来，我们就详细展开介绍JSX和React组件。

## JSX是语法糖

Web应用日益复杂，其视图中往往包含很多的控制逻辑，比如条件、循环等。以声明式开发视图，就需要把控制逻辑代码也加入到声明语句中去。而这样的代码，就对可读性、可维护性提出了挑战。

在JSX之前，前端领域有各种视图模版技术，JSP、Struts、Handlebars、Pug等，都在用各自的方法满足这些需求。那么JSX语法与其他声明式模版语法有什么异同？不用JSX可以写React吗？

我们在这节课开始时提到了React组件，组件是React开发的基本单位。在组件中，需要被渲染的内容是用 `React.createElement(component, props, ...children)` 声明的，而JSX正是 `createElement` 函数的语法糖。浏览器本身不支持JSX，所以在应用发布上线前， **JSX源码需要工具编译成由若干** `createElement` **函数组成的JS代码，然后才能在浏览器中正常执行**。至于编译工具，我们在后面的课程会有所涉及。

例如，上节课看板组件的部分JSX：

```
<header className="App-header">
  <h1>我的看板</h1>
</header>

```

编译成JS就会变成：

```
React.createElement("header", {className: "App-header"},
  React.createElement("h1", null, "我的看板")
);

```

当然你也可以选择不用JSX，而是自己手写这些JS代码。这样做最显著的好处就是，这部分代码不需要针对JSX做编译，直接可以作用于浏览器。但当元素或者元素的嵌套层级比较多时，JS代码的右括号会越来越多。当你看到成篇的 `))))))));` 时，你的代码和内心会有一个先崩溃。就算IDE帮忙自动格式化，对应层级缩进，也没法减少括号嵌套的数量。

也许是因为先入为主，在Web领域，类HTML语法天生就更受欢迎。 **JSX提供的类HTML/XML的语法会让声明代码更加直观**，在IDE的支持下，语法高亮更醒目， **比起纯JS也更容易维护**。相比JSX带来的开发效率的提升，编译JSX的成本基本可以忽略不计。

如果光看JSX中“X”的部分，还不足以让它和其他HTML/XML模版技术区别开来，这里还要强调一下JSX中“JS”的部分。请你回忆一下我们在上节课写的JSX代码，以里面的条件渲染为例：

```
  { showAdd && <KanbanNewCard onSubmit={handleSubmit} /> }

```

我们来对比一下Java SSH（Spring+Struts2+Hibernate）技术栈里Struts2模版的写法：

```
  <s:if test="showAdd">
        <div>KanbanNewCard ...</div>
    </s:if>

```

可以发现两者判断条件的语义是相同的，区别是Struts2用XML定义了一套名为标签库的DSL（Domain-Specific Language，领域特定语言），由标签库提供的 `<s:if></s:if>` 做条件渲染；而 **JSX则直接利用了JS语句。很明显，JS表达式能做的，JSX都能做，不需要开发者再去学习一套新的DSL**。

也正是因为JSX作为语法糖足够“甜”，我们才能得到这样的结论：JSX是前端视图领域“最JS”的声明式语法，它为React的推广和流行起了至关重要的作用。

## 前端开发中的声明式与命令式

既然刚才提到了声明式（Declarative），就一定要提一下命令式（Imperative）。这两种编程范式的PK存在于软件开发的各个领域。下面的表格呢，从（非）现实世界用例、各领域代表性技术、具体JS语句三个方面，将声明式和命令式做了一个对比。

![](https://static001.geekbang.org/resource/image/25/2f/250e1722bde8db58da7b49c38b4e902f.jpg?wh=4000x2250)

React是声明式的前端技术，这一点首先就体现在创建组件的视图上，无论是使用JSX语法还是直接利用 `React.createElement()` 函数，都是在 **描述开发者期待的视图状态**。开发者只需关心渲染结果，而React框架内部会实现具体的渲染过程，最终调用浏览器DOM API。

你可能会感兴趣：“除了jQuery，还有其他的前端框架是命令式的吗？”肯定是有的，但很明显，声明式才是主流。目前的三大主流前端框架，React、Vue、Angular都是声明式的。包括Flutter这样的新兴跨端框架也类似，都采用了典型的声明式API，以下是Flutter的官方例子：

```
Widget titleSection = Container(
  padding: const EdgeInsets.all(32),
  child: Row(
    children: [
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.only(bottom: 8),
              child: const Text('Oeschinen Lake Campground'),
            ),
            Text('Kandersteg, Switzerland'),
          ],
        ),
      ),
      Icon(
        Icons.star,
        color: Colors.red[500],
      ),
      const Text('41'),
    ],
  ),
);

```

多少有点眼熟吧。很有意思的是，从2017年开始，每年都有Flutter用户在社区中呼吁引入JSX语法（ [#11609](https://github.com/flutter/flutter/issues/11609)、 [#15922](https://github.com/flutter/flutter/issues/15922)、 [#70928](https://github.com/flutter/flutter/issues/70928)），但这一愿望都没有实现。这又一次彰显了JSX这种语法糖的吸引力。

理解了JSX是语法糖，其真实身份是声明式的 `React.createElement()` 函数，接下来我们来看看它的具体写法。

## JSX的写法和常见坑

先回到一个简单的问题上，JSX是哪几个单词的缩写？是的， **J** ava **S** cript **X** ML，即在JS语言里加入类XML的语法扩展。这样我们就可以把JSX一分为二：先介绍 **X** 的部分，即标签的命名规则，支持的元素类型、子元素类型；然后是 **JS** 的部分，即JSX中都有哪里可以加入JS表达式、规则是什么，进一步回顾上节课的条件渲染和循环渲染表达式。

### JSX的基本写法

请你回顾一下上节课 `src/App.js` 的内容，我们将以 `App` 组件为例，串讲一下JSX的常规写法和写JSX时常踩的坑。为了方便参考，我会在这里贴一部分 `App` 组件的源码。

```
function App() {
  const [showAdd, setShowAdd] = useState(false);
  const [todoList, setTodoList] = useState([]);
  const handleAdd = (evt) => {
    setShowAdd(true);
  };
  const handleSubmit = (title) => {
    setTodoList(currentTodoList => [
      { title, status: new Date().toDateString() },
      ...currentTodoList
    ]);
    setShowAdd(false);
  };

 return (
    <div className="App">
      <header className="App-header">
        <h1>我的看板</h1>
        <img src={logo} className="App-logo" alt="logo" />
      </header>
      <main className="kanban-board">
        <section className="kanban-column column-todo">
          <h2>待处理<button onClick={handleAdd}
            disabled={showAdd}>&#8853; 添加新卡片</button></h2>
          <ul>
            { showAdd && <KanbanNewCard onSubmit={handleSubmit} /> }
            { todoList.map(props => <KanbanCard {...props} />) }
          </ul>
        </section>
        {/* ...省略 */}
      </main>
    </div>
  );
}

```

虽然在写JSX时并不需要时时惦记着编译出来的 `React.createElement()` 语句，但在学习时还是很有帮助的。我们来看一下JSX各个组成部分与 `React.createElement()` 函数各参数的对应关系，代码如下：

```
React.createElement(type)
React.createElement(type, props)
React.createElement(type, props, ...children)

```

其中 `type` 参数是必须的，props可选，当参数数量大于等于3时，可以有一个或多个children。

以下是一个具体例子：

```
   <li className="kanban-card">
<!-- ^^ ^^^^^^^^^ ^^^^^^^^^^^^^
  type  props-key  props-value                                  -->
      <div className="card-title">{title}</div>   <!-- children -->
      <div className="card-status">{status}</div> <!-- ____|    -->
    </li>

```

把children中的一个成员单独来看，也是对应一条 `createElement()` 语句的：

```
   <div className="card-title">{title}</div>
<!-- ^^^ ^^^^^^^^^ ^^^^^^^^^^^^ ^^^^^^^
   type  props-key props-value   children -->

```

你可以在这个 [在线Babel编译器](https://babeljs.io/repl/#?browsers=defaults%2C%20not%20ie%2011%2C%20not%20ie_mob%2011&build=&builtIns=false&corejs=3.21&spec=false&loose=false&code_lz=GYVwdgxgLglg9mABACwKYBt1wBQEpEDeAUIogE6pQhlIA8AJjAG4B8AEhlogO5xnr0AhLQD0jVgG4iAXyJA&debug=false&forceAllTransforms=false&shippedProposals=false&circleciRepo=&evaluate=false&fileSize=false&timeTravel=false&sourceType=module&lineWrap=true&presets=react&prettier=false&targets=&version=7.18.4&externalPlugins=&assumptions=%7B%7D) 中做各种实验。

这里额外说一个大坑。当 `App` 代码 `return` 语句返回JSX时，将JSX包在了一对括号 `( )` 里，这是为了避免踏入JS自动加分号的陷阱。例如：

```
function Component() {
  return
    <div>{/*假设这行JSX语句很长，为了提升一些代码可读性才特地换行*/}</div>;
}

```

放到编译器里会生成：

```
function Component() {
  return;
  React.createElement("div", null);
}

```

整个函数短路了！根本不会执行到 `React.createElement()` 语句。为了修正这个问题，我们需要为JSX加上括号：

```
function Component() {
  return (
    <div>{/*假设这行JSX语句很长，为了提升一些代码可读性，特地换行*/}</div>
  );
}

```

再次编译：

```
function Component() {
  return React.createElement("div", null);
}

```

终于对了。

你能想象当年我和同事找Bug找了一整天，最后发现只是 `(` `)` 两个字符的问题吗？ “一朝被蛇咬，十年怕井绳。”自此，我养成了为JSX最外层加括号的习惯，甚至连单行return都会加上括号。毕竟在改老代码时，单行return有可能会改成多行，留下忘加括号的隐患。

### 命名规则

俗话说“无规矩不以成方圆”，学习JSX，就让我们从命名规则开始。

自定义React组件时，组件本身采用的变量名或者函数名，需要以大写字母开头。

```
function MyApp() {
//_______^
  return (<div></div>);
}
const KanbanCard = () => (
//____^
  <div></div>
);

```

在JSX中编写标签时，HTML元素名称均为小写字母，自定义组件首字母务必大写。

```
   <h1>我的看板</h1>
<!-- ^________全小写 -->
    <img src={logo} className="App-logo" alt="logo" />
<!-- ^^^______全小写 -->
    <button onClick={handleAdd} disabled={showAdd}>添加新卡片</button>
<!-- ^^^^^^___全小写 -->

    <KanbanCard />
<!-- ^_____首字母大写 -->

```

如果你很坚持自定义组件也要全小写，那我鼓励你亲手试一下，比如 `<camelCaseComponent />`。在浏览器开发者工具中定位到这个元素，你会发现React把它当成了一个不规范的HTML标签直接丢给了浏览器，而浏览器也不认识它，直接解析成 `<camelcasecomponent></camelcasecomponent>`。这也算是React的一种约定大于配置（Convention Over Configuration）了。

至于 `props` 属性名称，在React中使用驼峰命名（camelCase），且区分大小写，比如在 `<FileCard filename="文件名" fileName="另一个文件名" />` 中，你可以同时传两个字母相同但大小写不同的属性 ，这与传统的HTML属性不同。

### JSX元素类型

从前面的源码来看，我们在代表组件的函数里，返回了一整段JSX。JSX产生的每个节点都称作React元素，它是React应用的最小单元。React元素有三种基本类型：

1. React封装的DOM元素，如 `<div></div>`、 `<img />` ，这部分元素会最终被渲染为真实的DOM；
2. React组件渲染的元素，如 `<KanbanCard />` ，这部分元素会调用对应组件的渲染方法；
3. React Fragment元素， `<React.Fragment></React.Fragment>` 或者简写成 `<></>`，这一元素没有业务意义，也不会产生额外的DOM，主要用来将多个子元素分组。

其他还有Portal、Suspense等类型，这节课我们先不展开。

我们会为JSX元素加入props，不同类型元素的props有所区别。

React封装的DOM元素将浏览器DOM整体做了一次面向React的标准化，比如在HTML中很容易引起混淆的 `readonly="true"` ，它的W3C标准应该是 `readonly="readonly"` ，而常被误用的 `readonly="false"` 其实是无用的（谐音梗），在React JSX中就统一为 `readOnly={true}` 或 `readOnly={false}` ，更贴近JS的开发习惯。

至于前面反复出现的 `className="kanban-card"` ，更多是因为 HTML标签里的 `class` 是JS里的保留字，需要避开。

React组件渲染的元素，JSX中的props应该与自定义组件定义中的props对应起来；如果没有特别处理，没有对应的props会被忽略掉。这也是开发JSX时偶尔会犯的错误，在组件定义中改了props的属性名，但忘了改对应的JSX元素中的props，导致子组件拿不到属性值。

至于Fragment元素，没有props。

### JSX子元素类型

JSX元素可以指定子元素。在之后的课程里你会看到很多子组件的概念，这里先留一个印象： **子元素不一定是子组件，子组件一定是子元素**。

子元素的类型包括：

1. 字符串，最终会被渲染成HTML标签里的字符串；
2. 另一段JSX，会嵌套渲染；
3. JS表达式，会在渲染过程中执行，并让返回值参与到渲染过程中；
4. 布尔值、null值、undefined值，不会被渲染出来；
5. 以上各种类型组成的数组。

### JSX中的JS表达式

在JSX中可以插入JS表达式，特征是用大括号 `{ }` 包起来，主要有两个地方：

1. 作为props值，如 `<button disabled={showAdd}>添加新卡片</button>`；
2. 作为JSX元素的子元素，如 `<div className="card-title">{title}</div>`。

这些表达式可以简单到原始数据类型 `{true}` 、 `{123}` ，也可以复杂到一大串Lambda组成的函数表达式 `{ todoList.filter(card => card.title.startsWith('TODO:')).map(props => <KanbanCard {...props} />) }` ，只要确保最终的返回值符合props值或者JSX子元素的要求，就是有效的表达式。

前面也讲到， **JSX是声明式的，所以它的内部不应该出现命令式的语句**，如 `if ... else ...`。当你拿不准自己写到JSX `{ }` 里的代码到底是不是表达式，可以试着把这部分代码直接赋值给一个JS变量。如果这个赋值能成功，说明它确实是表达式；如果赋值不成功，可以从如下四个方面进行检查：

- 是否有语法错误；
- 是否使用了 `for...of` 的声明式变体 `array.forEach` ，这个中招几率比较高；
- 是否没有返回值；
- 是否有返回值，但不符合props或者子元素的要求。

另外有个props表达式的特殊用法：属性展开， `<KanbanCard {...props} />` 利用JS `...` 语法把 `props` 这个对象中的所有属性都传给 `KanbanCard` 组件。

对了，如果你想在JSX里加注释，会发现HTML注释 `<!-- -->` 根本没法通过编译，这时需要改用 `{/* */}` 来加注释，编译时它会被识别成JS注释然后抛弃掉。

### 回顾条件渲染和循环渲染

有了上面的知识，我请你再回顾一下上节课中的条件渲染和循环渲染：

```
{ showAdd && <KanbanNewCard onSubmit={handleSubmit} /> }

```

上面是一个典型的条件表达式，如果 `showAdd` 为 `true` 时，会返回后面的JSX，渲染《新建看板卡片》组件；否则会返回 `showAdd` 的值，即 `false` 。根据子元素类型中描述的， `false` 值并不会被渲染出来，《新建看板卡片》组件就不会被渲染了。

```
{ todoList.map(props => <KanbanCard {...props} />) }

```

上面是一个典型的数组转换表达式。当 `todoList` 为空数组时，表达式返回一个新的空数组，不会渲染出来；而当 `todoList` 包含1个或更多个项目时，会返回一个JSX的数组，相当于：

```
{[
  <KanbanCard title="开发任务-1" status="22-05-22 18:15" />,
  <KanbanCard title="开发任务-2" status="22-05-22 18:15" />
]}

```

## JSX与React组件的关系

你终于忍不住问出这个问题：“前面课里反复提到React组件，为啥一个普普通通的 `function App() {}` 函数就成组件了？”

这是个好问题！

鲁迅笔下的名人孔乙己曾说过“回字有四样写法”，巧了，React组件也是。React组件最初不是这么精简的。目前React的版本是v18，7年前的2015年React发布了两个大版本v0.13和v0.14（你可以理解成v13和v14），当时React组件的主流写法是：

```
const KanbanCard = React.createClass({
  render: function() {
    return (<div>KanbanCard ...</div>);
  }
});

```

FB官方在v0.13中开始推广 [ES6 class](https://zh-hans.reactjs.org/blog/2015/01/27/react-v0.13.0-beta-1.html#plain-javascript-classes) 的写法：

```
class KanbanCard extends React.Component {
  render() {
    return (<div>KanbanCard {this.props.title}</div>);
  }
}

```

用这两种方式 **定义组件时，最核心的就是实现** `render()` **方法。** `render()` 方法的 **返回值可以是一段JSX（或对应的React元素）、原始数据类型**（注：该方法在React v18以前的版本不可以返回 `undefined`，否则会报错） 、 **其他React数据类型或者是这几种类型的数组**。

除了 `render()` 方法，这两种写法还能加入其他属性和方法，完整实现React组件具有的状态管理、生命周期、事件处理等功能，这些功能我们放在后续的课程里，在这里暂时不展开。所以说JSX只是React组件的一部分，这就澄清了“JSX就是React组件”这个误解。

除了前面两种写法，在v0.14，React新加入了一种更为简化的 **无状态函数组件**（ [Stateless Function Component](https://zh-hans.reactjs.org/blog/2015/10/07/react-v0.14.html#stateless-function-components)）：

```
// ES6箭头函数
const KanbanCard = (props) => {
  var title = props.title;
  return (<div>KanbanCard {title}</div>);
};

// 更简单的箭头函数+参数解构
const KanbanCard = ({title}) => (
  <div>KanbanCard {title}</div>
);

```

函数的参数就是props， **函数的返回值与前面两种写法中** `render()` **方法的返回值相同**。这种函数组件在React Hooks尚未发布时，还不能自己处理state状态，需要在它的父组件提供状态，并通过props传递给它。虽然函数组件功能受限，但它贵在简单，受到了开发者的广泛欢迎。以至于开源社区开发了各种支持库，用诸如高阶组件的方式补足函数组件缺失的功能。

当时最出名的库莫过于 [recompose](https://github.com/acdlite/recompose)，举个简单的例子：

```
import { withState } from 'recompose';

const enhance = withState('showAdd', 'setShowAdd', false);
const KanbanColumn = enhance(({ showAdd, setShowAdd }) => (
  <section className="kanban-column column-todo">
    <h2>
      待处理
      <button onClick={() => setShowAdd(true)}>添加新卡片</button>
    </h2>
    <ul>
      { showAdd && <KanbanNewCard /> }
    </ul>
  </section>
));

```

其中可以看到 `KanbanColumn` 组件的主体是 `enhance` 参数的箭头函数组件。前面 `recompose` 的 `withState(stateName, stateUpdaterName, initialState)` 函数会创建一个单一功能的高阶组件（高阶组件后面课程会讲到），它会创建名为 `showAdd` 的state，并通过props传递给作为子组件的函数组件，父子组件结合在一起，形成一个功能完整的React组件。顺便一提，后来recompose的作者还加入了React官方开发组。

到了React v16.8，Hooks正式发布，函数组件取代类组件成为了React组件的C位。题外话，对于React函数组件的流行，我在当年是有点意外的。我本人是ES6 class的死忠粉，但后来先后上手了recompose和官方的Hooks，真香。

当然，介绍这段历史并不是为了吃瓜，最重要的还是回答你刚才的问题“为啥一个普普通通的函数就成组件了” 。

简单总结一下，函数组件上位的原因包括：

- React的哲学 `UI=f(state)` ；
- 更彻底的关注点分离（Separation Of Concerns）；
- 函数式编程的影响；
- React内部实现的不断优化；
- 开源社区的反哺。

## 小结

这节课我们学习了JSX的概念和写法，同时也引出了React声明式的特性，也初步聊了一下React组件。

这时我相信你已经不会再有这节课开头的误解了：

- JSX就是React？
  - 不是。JSX只是React其中一个API， `createElement` 函数的语法糖。
- JSX就是React组件？
  - 不是。JSX是React组件渲染方法返回值的一部分，React组件还有其他的功能。
- JSX就是另一种HTML？
  - 不是。JSX本质还是JS，只是在最终渲染时才创建修改DOM。
- JSX既能声明视图，又能混入JS表达式，那是不是可以把所有逻辑都写在JSX里？
  - 可以是可以，但毕竟不能在JSX里使用命令式语句，能做的事情很有限。

运用好JSX，可以很大程度提高你的React开发效率和效果。

下一讲，我们将趁热打铁，继续探讨React组件，从比React元素颗粒度更大的层面，认识React渲染的机制。同时也学习如何从业务和技术两方面入手，将一份原始的需求拆解为若干React组件。

## 思考题

这一讲中间举过一个Flutter的例子，提到用户希望将JSX语法引入Flutter。想请你按这个思路思考如下两个问题：

1. JSX一定得是React吗？React以外的技术能不能使用JSX？
2. JSX一定得生成HTML吗？可以用JSX生成其他模版吗？

欢迎把你的想法分享在留言区，我会和你交流。相信经过你的深度思考，学习效果会更好！我们下节课再见！