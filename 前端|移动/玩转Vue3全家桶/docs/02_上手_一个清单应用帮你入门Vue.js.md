你好，我是大圣，欢迎进入课程导读篇的第二讲。

在上一讲中，我带你了解了前端框架的基本发展历史。在为什么要学Vue框架这个问题上，相信你现在已经有了自己的答案。那么从今天开始，我们正式进入上手学Vue 的阶段。

我们的专栏课程会通过故事的形式展开。故事的主角小圣是一名刚入行的前端工程师，在校期间学了点HTML、CSS和JavaScript，但是不太懂框架。我是他的经理，会手把手教他在Vue.js这个框架里打怪升级。

小圣在学习Vue的过程中碰到的各种问题，同样也可能是你会碰到的问题。所以，在我带着你一起解决小圣面临的问题的同时，你的很多问题也会迎刃而解。

今天是小圣第一天入职，他只知道团队的项目是用Vue.js开发的，但并不熟悉Vue的具体技术细节，所以我决定带他先做一个清单应用，先在整体上熟悉这个框架。当然了，我在这里带小圣做的清单应用，更多的是一种模拟的场景，并不需要对号入座到真实的工作场景下。毕竟在真实的工作场景下，可能小圣一进公司就上实际的项目了。

如果你已经很熟悉Vue开发了，可以直接粗略地把本讲过一遍，直奔下一讲。在那里，我会带你梳理Vue 3的新特性，相信这些新特性会让你对Vue 3产生新的期待。

## 环境准备

小圣领完电脑后，首先要做的是安装编辑器和浏览器，这个不用多介绍，你也能轻松地搞定。我推荐给小圣写代码的编辑器是VS Code，调试页面的浏览器是Chrome。有了VS Code和Chrome，我们就可以开始后面的工作了。

## 任务分解

如下图所示，小圣要上手开发的应用大概长这个样子：它有一个输入框，供我们输入数据；下方有一个列表，显示着所有我们要做的事情。

在输入框输入内容后，敲下回车，下面就会新增一条数据。对于每个要做的事情，你还可以用复选框标记，标记后文字就会变灰，并带有一个删除的效果，表示这件事情已经做完了。

![图片](https://static001.geekbang.org/resource/image/0c/01/0c58c5219ecb61394110ccb848829c01.png?wh=1526x884)

清单应用虽然看起来简单，不过麻雀虽小，五脏俱全。其实不管入门哪个框架，你都可以写一个清单，来上手体验一下。

不过，由于小圣只有简单的jQuery开发经验，他在学习Vue的时候，首先要做的就是思想的转变。为什么要这么说呢？下面我们来对比看看jQuery的开发思路和Vue.js的开发思路有什么不同，看完你就会明白，我为什么说小圣在学习Vue时，首先要做的是转变思路。

比如，我们想做一个输入框，里面输入的任何数据都会在页面上同步显示。

对于这样一个前端的功能，jQuery开发的思路是：

1. 先找到输入框，给输入框绑定输入事件；
2. 输入的同时，我们获取输入的值；
3. 再找到对应的html标签，更新标签的内容。

对应代码大概是这样的：

```plain
<div>
    <h2 id="app"></h2>
    <input type="text" id="todo-input">
</div>
<script src="jquery.min.js"></script>
<script>
    // 找到输入框，监听输入
    $('#todo-input').on('input',function(){
        let val = $(this).val() // 获取值
        $('#app').html(val) // 找到标签，修改内容
    })
</script>

```

在实现我们想要的输入框的功能时，上述jQuery代码需要先找到输入框，然后持续监听输入，之后一直等待到输入值被获取，最后找到标签所在的前端页面位置，进行内容的修改。

上述的jQuery代码，其实是jQuery时代的开发逻辑的一个缩影。 **而jQuery时代的开发逻辑，就是我们先要找到目标元素，然后再进行对应的修改**。

学习Vue.js，首先就要进行思想的升级，也就是说， **不要再思考页面的元素怎么操作，而是要思考数据是怎么变化的**。这就意味着，我们只需要操作数据，至于数据和页面的同步问题，Vue会帮我们处理。实际上，Vue让前端开发者能够专注数据本身的操作，而数据和页面的同步问题，则交由Vue来负责。这种机制正是Vue当初受到开发者青睐的一个重要原因。

对于同样的输入框需求，Vue的开发思路是：我们需要一个数据，在输入框的代码和h2标签的代码内使用。我们只需要操作数据，然后交给Vue去管理数据和页面的同步就可以了。

在Vue框架下，如果你想要页面显示一个数据，就要先在代码的data里声明数据；在输入框的代码里，使用v-model来标记输入框和数据的同步；在HTML模板里，使用两个花括号标记，来显示数据，例如{{title}}。对应代码大概是这个样子：

```xml
<div id="app">
  <h2>{{title}}</h2>
  <input type="text" v-model="title">
</div>

<script src="https://unpkg.com/vue@next"></script>
<script>
const App = {
  data() {
    return {
      title: "" // 定义一个数据
    }
  }
}
// 启动应用
Vue.createApp(App).mount('#app')
</script>

```

从这个例子中，你就可以看到Vue在开发思路上和jQuery的不同。而我们要做的，就是逐渐习惯Vue的这种开发模式。

## 清单页面的渲染

在前端页面，我们在输入框输入数据，然后输入框下方要有一个列表，显示我们所有输入的值。按照Vue的思考方式，如果我们想实现这个功能，那么我们需要一个数组，然后使用v-for这个语法来循环渲染。

先看代码：

```xml
<div id="app">
  <h2>{{title}}</h2>
  <input type="text" v-model="title">
  <ul>
    <li v-for="todo in todos">{{todo}}</li>
  </ul>
</div>

<script src="https://unpkg.com/vue@next"></script>
<script>
const App = {
  data() {
    return {
      title: "", // 定义一个数据
      todos:['吃饭','睡觉']
    }
  }
}
// 启动应用
Vue.createApp(App).mount('#app')
</script>

```

看上述代码，在data中，我们再定义一个数据todos，输入一个数组。为了方便调试，我们先放两个假数据，如果我们在标签里直接写{{todos}}，就会看到显示的是一个数组，但这个不是我们想要的，我们需要的是显示一个列表。

在Vue中，只要是渲染列表，我们都是用v-for这个语法，而具体到上述代码对v-for语法的使用，也即：

```xml
<li v-for="todo in todos">{{todo}}</li>

```

上面这行单独抽出来的代码的意思就是：我们循环遍历todos这个数据， 每一条遍历的结果叫todo，然后把这个数据渲染出来，这样页面就能显示一个列表了。

![图片](https://static001.geekbang.org/resource/image/b2/28/b2436fe52fec4a2e0b4a13dba97f1728.png?wh=874x436)

## 处理用户交互

在上一步中，我们主要考虑的是：实现前端页面的一个输入框，以及能显示输入值的一个列表的功能。下一步，就是让用户敲回车的时候，能够让列表新增一条。采用Vue的思维，我们需要完成以下这几个步骤：

1. 监听用户的输入。在监听中，如果判断到用户的输入是回车的时候，那就执行一个函数。
2. 在执行的这个函数内部把title追加到todos最后面的位置，并且清空title。

那么Vue如何实现这一功能呢？我们先看实现这一功能后的完整代码：

```xml
<div id="app">
  <input type="text" v-model="title" @keydown.enter="addTodo">
  <ul>
    <li v-for="todo in todos">{{todo}}</li>
  </ul>
</div>

<script src="https://unpkg.com/vue@next"></script>
<script>
const App = {
  data() {
    return {
      title: "", // 定义一个数据
      todos:['吃饭','睡觉']
    }
  },
  methods:{
    addTodo(){
      this.todos.push(this.title)
      this.title = ""
    }
  }
}
// 启动应用
Vue.createApp(App).mount('#app')
</script>

```

对照上述代码，我们来看一下在Vue中，监听用户交互的方法。在Vue中，我们使用@来标记用户的交互，@click是点击，@keydown是键盘敲下，所以就像上述代码展示的那样，如果只监听回车键，那么我们就用@keydown.enter=“addTodo” 。

监听到用户的输入后，对于要执行的函数，我们新增一个methods配置。在函数内部，我们可以在this上直接读到data里的的数据，所以我们不需要考虑怎么找到标签，只需要进行如下这行潇洒的代码，就能让列表自动新增了一条， 这就是数据驱动页面的魅力。

```xml
this.todos.push(this.title)

```

## 额外信息的显示

好了，我们现在既实现了一个输入框，以及输入数据后能够新增一条数据的列表的功能，也实现了用户在输入后的交互功能。

下一步，我们想实现标记清单中某一项是否完成的功能。但这却难住了小圣同学，因为从目前的代码设计上来看，我们的输入只能是字符串格式的内容。而我们想要实现的标记功能，却是把列表中的某一项，用灰色的字体背景和中划线来标记，以此表示这一条内容是已经完成的内容。

如果我们想实现这个功能，就需要对数据结构进行一下改造，把内容的数据类型，从简单的字符串类型改为对象。

那么数据结构要怎么改造呢？我们先直接看改造数据结构后的完整代码：

```xml
  <ul>
    <li v-for="todo in todos">
      <input type="checkbox" v-model="todo.done">
      <span :class="{done:todo.done}"> {{todo.title}}</span>
    </li>
  </ul>

<script>
const App = {
  data() {
    return {
      title: "", // 定义一个数据
      todos:[
        {title:'吃饭',done:false},
        {title:'睡觉',done:true}
      ]
    }
  },
  methods:{
    addTodo(){
      this.todos.push({
        title:this.title,
        done:false
      })
      this.title = ""
    }
  }
}
</script>

<style>
  .done{
    color:gray;
    text-decoration: line-through;
  }
</style>

```

结合代码，我给你理理整个的改造思路。首先，对于todos数组，除了title，还要加上一个done字段，来标记列表中的某一项内容是否完成，并且渲染的时候使用todo.title。

在前面的步骤中，对于列表中每一项，我们是用无序列来表示的。但如果我们想要在列表中实现对某些选项的同时多选，那么就需要用到复选框。对于每条信息，我们都要加一个复选框，所以我们依然使用v-model来绑定这个done字段，从而实现数据里能记录用户操作的状态。

我们还需要根据done字段来显示某一行的样式。在Vue中，冒号":" 开头的属性是用来传递数据的，这里的写法的意思就是根据todo.done来决定是否有done这个class。最后，当加上".done"的样式后，下面的左图就是我们想要的效果，而下面的右图则是涉及到".done"的相关代码：

![图片](https://static001.geekbang.org/resource/image/7f/b7/7f73769e14d67yy4104404b7442809b7.png?wh=1884x910)

## 进一步优化

完成前面的步骤以后，现在看起来一个清单应用最基本的功能模块、用户交互、复选框功能都已经实现了。但是为了进一步提升交互，小圣还想要增加两个功能，第一个功能是：在前端页面显示的列表的最下面，显示一下列表项目中没完成的项目的比例；第二个功能是：新增一个清理的按钮，用来删掉已经标记为完成的列表中的一条或多条数据。

那么，对于要增加的第一个功能，也即如何实现在前端页面的列表的最下方，显示一下列表项目中没有完成的项目的比例呢？小圣按照学到的知识，写出了下面的代码：

```xml
  <div>
    {{todos.filter(v=>!v.done).length}}
    /
    {{todos.length}}
  </div>

```

把这段代码增加到上一步最后的完整代码中，运行代码，从下图所示的前端页面运行时状态中，我们能看到，其中显示的未完成比例的数据也没问题。

![图片](https://static001.geekbang.org/resource/image/d0/97/d02a1fc75d79063f48660f4yy13dd197.png?wh=988x416)

不过，从上述代码实现的方式上看，代码看起来很丑且性能不好，而且需要二次计算的数据，这在我们开发的需求中很常见。此外，在模板里面写JS，看起来代码也很乱。Vue针对这种情况，设计了一个功能，也就是 **计算属性**。

我们看一下采用Vue的计算属性实现的，能够支持二次计算的上述功能的实现代码：

```xml
  <div>
    {{active}}  / {{all}}
  </div>

<script>
  computed:{
    active(){
      return this.todos.filter(v=>!v.done).length
    },
    all(){
      return this.todos.length
    }
  }
</script>

```

从上面的代码中能看到，和之前采用往模板里写JS的办法相比，我们新增了一个属性computed。computed属性的配置，也即active和all，都是函数。这两个函数返回的计算后的值，在模板里可以直接当做数据来用，这样把JavaScript的计算逻辑依然放在了JavaScript里，避免了过于臃肿的模板。

而且computed计算属性还内置了缓存功能，如果依赖数据没变化，多次使用计算属性会直接返回缓存结果，同我们直接写在模板里相比，性能也有了提升。

计算属性不仅可以用来返回数据，有些时候我们也需要修改计算属性，比如我让小圣新增一个全选的复选框，要求如下：

1. 全选框在勾选与取消勾选两个状态之间的切换，会把所有清单内的数据都同步勾选。
2. 清单内的项目如果全部选中或者取消，也会修改全选框的状态。

对于新增全选框的功能，需要满足上面的两个要求，所以全选框这个计算属性就有了修改的需求。这时候computed的配置就不能是函数了，要变成一个对象，分别实现get和set函数，get就是之前的返回值，set就是修改计算属性要执行的函数。

我们来看一下computed修改后的代码：

```xml
<div>
  全选<input type="checkbox" v-model="allDone">
  <span> {{active}}  / {{all}} </span>
</div>

<script>
computed:{
  active(){
    return this.todos.filter(v=>!v.done).length
  },
  all(){
    return this.todos.length
  },
  allDone: {
      get: function () {
        return this.active === 0
      },
      set: function (val) {
        this.todos.forEach(todo=>{
          todo.done = val
        });
      }
  }
}
</script>

```

和没有全选框时的computed属性的配置代码相比，上面的代码新增了一个allDone的计算属性，页面中直接使用checbox绑定。在allDone的get函数里，对于allDone会返回什么值，我们只需要判断计算属性active是不是0就可以。

而set函数做到的就是，我们在修改allDone，也就是前端页面切换全选框的时候，直接遍历todos，把里面的done字段直接和allDone同步即可。

实现新增一个全选的复选框后的效果是什么样呢？我们一起来看一下：

![图片](https://static001.geekbang.org/resource/image/27/cf/273d37ca7e59a40ac0d5a537203f41cf.gif?wh=542x325)

## 条件渲染

在上面一部分，我们增加了在前端页面的底部显示未完成比例，和增加全选框这两个功能。除此之外，我们还需要新增一个“清理”的按钮，点击之后把已完成的数据删除，功能需求很简单，但是有一个额外的要求，就是列表中没有标记为完成的某一项列表数据时，这个按钮是不显示的。

这种在特定条件下才显示，或者隐藏的需求也很常见，我们称之为条件渲染。在Vue中，我们使用v-if 来实现条件渲染。

老规矩，我们还是先看代码：

```xml
<button v-if="active<all" @click="clear">清理</button>
<script>
  methods:{
    clear(){
      this.todos = this.todos.filter(v=>!v.done)
    }
  }
</script>

```

通过上述代码，我们实现了增加一个清理按钮的功能。当active小于all的时候，我们显示清理按钮，也就是说，v-if后面的值是true的时候，显示清理按钮，false的时候不显示。“@”符号的作用，我们在前面讲到监听用户交互时，已经拿@keydown为例说明过了，这里代码中的@click的作用是绑定点击事件。

我们还可以用v-else配合v-if，当todos是空的时候，显示一条“暂无数据”的信息，具体的实现代码如下：

```xml
  <ul v-if="todos.length">
    <li v-for="todo in todos">
      <input type="checkbox" v-model="todo.done">
      <span :class="{done:todo.done}"> {{todo.title}}</span>
    </li>
  </ul>
  <div v-else>
    暂无数据
  </div>

```

当我们实现了清理按钮的功能，并且也实现了列表为空时，能够显示“暂无数据”的信息后，我们看下清单应用的最终效果。

![图片](https://static001.geekbang.org/resource/image/3c/72/3c8ddf81d6b478069d6b1dec7b605572.gif?wh=542x325)

这个需求并没有考虑美观性，小圣没写太多CSS，主要专注在JS的交互逻辑上。小圣这个需求做完，晚上下班的时候跟我分享了一下学习Vue的心得，你也可以在评论区分享一下你对Vue的开发的心得，我们一起交流。

## 总结

我们来总结一下小圣今天都学到了什么吧。入职第一天，小圣首先扭转了之前使用jQuery时的开发思路，并且弄明白了jQuery和Vue开发思路的区别。从寻找DOM到数据驱动，这是前端开发的一次巨大的变革，也是小圣同学的第一个挑战。

其次就是对Vue的入门使用，我带你回顾一下今天做的这个清单应用：对于这个应用，首先我们要有输入框能输入文本，并且在输入框下方循环显示清单，我们用到了v-model，v-for这些功能。这些v-开头的属性都是Vue自带写法，我们通过{{}}包裹的形式显示数据。

然后我们想在用户输入完成后敲击回车新增一条数据，这就用到@开头的几个属性，@keyup和@click都是绑定对应的交互事件。最后，通过computed，我们能对页面数据的显示进行优化。我们所需要关心的，就是数据的变化，这种思维方式会贯穿小圣的整个打怪升级之路。

## 思考题

下班前我给小圣布置一个作业，现在所有的操作状态一刷新就都没了，这个问题怎么解决呢？

欢迎在评论区一起讨论，也欢迎你把这篇文章分享给其他人，我们下一讲见。