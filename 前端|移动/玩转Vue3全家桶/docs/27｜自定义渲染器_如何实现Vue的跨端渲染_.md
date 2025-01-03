你好，我是大圣。

上一讲我们讲完了组件库的核心知识点，这一讲我们来学习一个叫Vue 3的进阶知识点：自定义渲染器，这个功能可以自定义Vue渲染的逻辑。

在给你讲清楚原理之后，我还会带你一起实现一个Canvas的渲染器实际上手体验一下。

## 什么是渲染器

我们都知道，Vue内部的组件是以虚拟dom形式存在的。下面的代码就是一个很常见的虚拟Dom，用对象的方式去描述一个项目。相比dom标签相比，这种形式可以让整个Vue项目脱离浏览器的限制，更方便地实现Vuejs的跨端。

```javascript
{
  tag: 'div',
  props: {
    id: 'app'
  },
  chidren: [
    {
      tag: Container,
      props: {
        className: 'el-container'
      },
      chidren: [
        '哈喽小老弟!!!'
      ]
    }
  ]
}

```

渲染器是围绕虚拟Dom存在的。在浏览器中，我们把虚拟Dom渲染成真实的Dom对象，Vue源码内部把一个框架里所有和平台相关的操作，抽离成了独立的方法。所以，我们只需要实现下面这些方法，就可以实现Vue 3在一个平台的渲染。

首先用createElement创建标签，还有用createText创建文本。创建之后就需要用insert新增元素，通过remove删除元素，通过setText更新文本和patchProps修改属性。然后再实现parentNode、nextSibling等方法实现节点的查找关系。完成这些工作，理论上就可以在一个平台内实现一个应用了。

在Vue 3中的runtime-core模块，就对外暴露了这些接口，runtime-core内部基于这些函数实现了整个Vue内部的所有操作，然后在runtime-dom中传入以上所有方法。

下面的代码就是Vue代码提供浏览器端操作的函数，这些DOM编程接口完成了浏览器端增加、添加和删除操作，这些API都是浏览器端独有的，如果一个框架强依赖于这些函数，那就只能在浏览器端运行。

```javascript
export const nodeOps: Omit<RendererOptions<Node, Element>, 'patchProp'> = {
  //插入元素
  insert: (child, parent, anchor) => {
    parent.insertBefore(child, anchor || null)
  },
  // 删除元素
  remove: child => {
    const parent = child.parentNode
    if (parent) {
      parent.removeChild(child)
    }
  },
  // 创建元素
  createElement: (tag, isSVG, is, props): Element => {
    const el = isSVG
      ? doc.createElementNS(svgNS, tag)
      : doc.createElement(tag, is ? { is } : undefined)

    if (tag === 'select' && props && props.multiple != null) {
      ;(el as HTMLSelectElement).setAttribute('multiple', props.multiple)
    }

    return el
  }
  //...其他操作函数
}

```

如果一个框架想要实现实现跨端的功能，那么渲染器本身不能依赖任何平台下特有的接口。

在后面的代码中，我们通过createRenderer函数区创建了一个渲染器。通过参数options获取增删改查所有的函数以后，在内部的render、mount、patch等函数中，需要去渲染一个元素的时候，就可以通过option.createElement和option.insert来实现。

这段代码给你展现的是核心逻辑，完整版本你可以看一下 [Vue 3的源码](https://github.com/vuejs/vue-next/blob/master/packages/runtime-core/src/renderer.ts#L334)。

```javascript
export default function createRenderer(options) {
  const {
	    insert: hostInsert,
	    remove: hostRemove,
	    patchProp: hostPatchProp,
	    createElement: hostCreateElement,
	    createText: hostCreateText,
	    createComment: hostCreateComment,
	    setText: hostSetText,
	    setElementText: hostSetElementText,
	    parentNode: hostParentNode,
	    nextSibling: hostNextSibling,
	    setScopeId: hostSetScopeId = NOOP,
	    cloneNode: hostCloneNode,
	    insertStaticContent: hostInsertStaticContent
   } = options

  function render(vnode, container) {  }

  function mount(vnode, container, isSVG, refNode) {  }

  function mountElement(vnode, container, isSVG, refNode) {  }

  function mountText(vnode, container) {  }

  function patch(prevVNode, nextVNode, container) {  }

  function replaceVNode(prevVNode, nextVNode, container) {  }
  function patchElement(prevVNode, nextVNode, container) {  }
  function patchChildren(
    prevChildFlags,
    nextChildFlags,
    prevChildren,
    nextChildren,
    container
  ) {  }

  function patchText(prevVNode, nextVNode) {  }
  function patchComponent(prevVNode, nextVNode, container) {  }

  return { render }
}

```

在每个函数实现的内部，比如mountElemnt，我们之前的实现方式是调用浏览器的API创建。

```javascript
function mountElement(vnode, container, isSVG, refNode) {
  const el = isSVG
    ? document.createElementNS(....)
    : document.createElement(vnode.tag)
}

```

对比一下，经过渲染器抽离之后，内部的mountElmenet就会把所有document的操作全部换成options传递进来的hostCreate函数。

```javascript
function mountElement(vnode, container, isSVG, refNode) {
  const el = hostCreateElement(vnode.tag, isSVG)
}

```

然后，我们使用后面的代码创建一个具体平台的渲染器，这也是Vue 3中的runtime-dom包主要做的事。了解了Vue中自定义渲染器的实现方式后，我们还可以基于Vue 3的runtime-core包封装其他平台的渲染器，让其他平台也能使用Vue内部的响应式和组件化等优秀的特性。

```javascript
const { render } = createRenderer({
  nodeOps: {
    createElement() {   },
    createText() {   }
    // more...
  },
  patchData
})

```

## 自定义渲染

说完了渲染器创建，我们再来看看自定义渲染。

自定义渲染器让Vue脱离了浏览器的限制，我们只需要实现平台内部的增删改查函数后，就可以直接对接Vue 3。比方说，我们可以把Vue渲染到小程序平台，实现Vue 3-miniapp；也可以渲染到Canvas，实现vue 3-canvas，把虚拟dom渲染成Canvas；甚至还可以尝试把Vue 3渲染到threee.js中，在3D世界使用响应式开发。

接下来，我们一起尝试实现一个Canvas的渲染器。具体操作是这样的，我们在项目的src目录下新建renderer.js，通过这个文件实现一个简易的Canvas渲染逻辑。Canvas平台中操作的方式相对简单，没有太多节点的概念，我们可以把整个Canvas维护成一个对象，每次操作的时候直接把Canvas重绘一下就可以了。

```javascript
import { createRenderer } from '@vue/runtime-core'
const { createApp: originCa } = createRenderer({
  insert: (child, parent, anchor) => {
  },
  createElement(type, isSVG, isCustom) {
  },
  setElementText(node, text) {
  },
  patchProp(el, key, prev, next) {
  },
});

```

下面的代码中我们实现了draw函数，这里我们就使用了Canvas的操作方法， **递归** 地把Canvas对象渲染到了Canvas标签内部。

```javascript
let ctx
function draw(ele, isChild) {
  if (!isChild) {
    ctx.clearRect(0, 0, 500, 500)
  }

  ctx.fillStyle = ele.fill || 'white'
  ctx.fillRect(...ele.pos)
  if (ele.text) {
    ctx.fillStyle = ele.color || 'white'
    ele.fontSize = ele.type == "h1" ? 20 : 12
    ctx.font = (ele.fontSize || 18) + 'px serif'
    ctx.fillText(ele.text, ele.pos[0] + 10, ele.pos[1] + ele.fontSize)
  }
  ele.child && ele.child.forEach(c => {
    console.log('child:::', c)
    draw(c, true)
  })

}

```

由于我们主体需要维护的逻辑就是对于对象的操作，所以创建和更新操作直接去操作对象即可。新增insert需要维护parent和child元素。另外，插入的时候也需要调用draw函数，并且需要监听onclick事件。

```javascript
const { createApp: originCa } = createRenderer({
  insert: (child, parent, anchor) => {
    if (typeof child == 'string') {
      parent.text = child
    } else {
      child.parent = parent
      if (!parent.child) {
        parent.child = [child]
      } else {
        parent.child.push(child)
      }
    }
    if (parent.nodeName) {
      draw(child)
      if (child.onClick) {
        ctx.canvas.addEventListener('click', () => {
          child.onClick()
          setTimeout(() => {
            draw(child)
          })
        }, false)
      }
    }
  },
  createElement(type, isSVG, isCustom) {
    return {
      type
    }
  },
  setElementText(node, text) {
    node.text = text
  },
  patchProp(el, key, prev, next) {
    el[key] = next
  },

});

```

现在我们来到src/main.js中，这时候就不能直接从vue中引入createApp了，而是需要从runtime-core中导入createRenderer。

接下来，通过createRenderer用我们自己定义的renderer去创建createApp，并且重写mount函数。在Canvas的mount中，我们需要创建Canvas标签并且挂载到App上。

```javascript
import { createRenderer } from '@vue/runtime-core'
const { createApp: originCa } = createRenderer({

}）
function createApp(...args) {
  const app = originCa(...args)
  return {
    mount(selector) {
      const canvas = document.createElement('canvas')
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      document.querySelector(selector).appendChild(canvas)
      ctx = canvas.getContext('2d')
      app.mount(canvas)
    }
  }
}

```

下一步进入src/App.vue中，我们就可以在Vue组件中使用ref等响应式的写法了。我们实现了通过ref返回的响应式对象，渲染Canvas内部的文字和高度，并且点击的时候还可以修改文字。完成上面的操作，我们就实现了Canvas平台的基本渲染。

```xml
<template>
<div @click="setName('vue3真棒')" :pos="[10,10,300,300]" fill="#eee">
    <h1 :pos="[20,20,200,100]" fill="red" color="#000">累加器{{count}}</h1>
    <span :pos="pos" fill="black" >哈喽{{name}}</span>
</div>

</template>

<script setup>

import {ref} from 'vue'
const name = ref('vue3入门')
const pos = ref([20,120,200,100])
const count = ref(1)
const setName = (n)=>{
  name.value = n
  pos.value[1]+=20
  count.value+=2
}
</script>

```

上面的代码在浏览器里就会有下图的显示效果。我们点击Canvas后，文案就会显示为“哈喽vue3真棒”，并且黑色方块和红色方块的距离也会变大。

![图片](https://static001.geekbang.org/resource/image/b4/7b/b466ca102ef94ebce2d05c865ca4637b.png?wh=1920x992)

基于这个原理，我们其实可以做很多有意思的尝试。社区也有越来越多开源的Vue 3的自定义渲染器，比如小程序跨端框架uni-app，Vugel可以使用Vue渲染Webgl等，你也可以动手多多体验。

比如下面的代码中，我们对three.js进行一个渲染的尝试。它的实现逻辑和Canvas比较类似，通过对于对象的维护和draw函数实现最终的绘制。在draw函数内部，我们调用three.js的操作方法去创建camera，sence，geometry等概念，最后对外暴露three.js的createApp函数。

```xml
import { createRenderer } from '@vue/runtime-core'
import * as THREE from 'three'
import {nextTick} from '@vue/runtime-core'

let renderer

function draw(obj) {
    const {camera,cameraPos, scene, geometry,geometryArg,material,mesh,meshY,meshX} = obj
    if([camera,cameraPos, scene, geometry,geometryArg,material,mesh,meshY,meshX].filter(v=>v).length<9){
        return
    }
    let cameraObj = new THREE[camera]( 40, window.innerWidth / window.innerHeight, 0.1, 10 )
    Object.assign(cameraObj.position,cameraPos)

    let sceneObj = new THREE[scene]()

    let geometryObj = new THREE[geometry]( ...geometryArg)
    let materialObj = new THREE[material]()

    let meshObj = new THREE[mesh]( geometryObj, materialObj )
    meshObj.rotation.x = meshX
    meshObj.rotation.y = meshY
    sceneObj.add( meshObj )
    renderer.render( sceneObj, cameraObj );

}

const { createApp: originCa } = createRenderer({
  insert: (child, parent, anchor) => {
    if(parent.domElement){
        draw(child)
    }
  },
  createElement(type, isSVG, isCustom) {
    return {
      type
    }
  },
  setElementText(node, text) {
  },
  patchProp(el, key, prev, next) {
    el[key] = next
    draw(el)
  },
  parentNode: node => node,
  nextSibling: node => node,
  createText: text => text,
  remove:node=>node

});
function createApp(...args) {
  const app = originCa(...args)
  return {
    mount(selector) {
        renderer = new THREE.WebGLRenderer( { antialias: true } );
        renderer.setSize( window.innerWidth, window.innerHeight );
        document.body.appendChild( renderer.domElement );
        app.mount(renderer)
    }
  }
}
export { createApp }

```

然后我们在App.vue中，使用下面的代码渲染出一个立方体，并且通过ref响应式对象控制立方体偏移的角度，再通过setInterval实现立方体的动画，实现下图的翻转效果。

```xml
<template>
    <div
        camera="PerspectiveCamera"
        :cameraPos={z:1}
        scene="Scene"
        geometry="BoxGeometry"
        :geometryArg="[0.2,0.2,0.2]"
        material="MeshNormalMaterial"
        mesh="Mesh"
        :meshY="y"
        :meshX="x"
    >
    </div>

</template>

<script>
import {ref} from 'vue'
export default {
    setup(){
        const y = ref(0.3)
        const x = ref(0.3)
        setInterval(()=>{
            y.value+=0.3
            x.value+=0.5
        },100)
        return {y,x}
    }
}
</script>

```

反转效果演示如下：

![图片](https://static001.geekbang.org/resource/image/b0/4f/b0b20b2a314bcf650b8b56256bdf804f.gif?wh=1182x761)

我们还可以在Canvas的封装上更进一步，并且实现对一些Canvas已有框架Pixi.js的封装，这样就可以通过Vue 3的响应式的开发方式，快速开发一个小游戏。

下面的代码中就是针对Pixi.js实现的封装函数，你可以看一下。

```xml
 import {Graphics} from "PIXI.js";

export const getNodeOps = (app) => {
  return {
    insert: (child, parent, anchor) => {
      parent.addChild(child);
    },

    remove: (child) => {
      const parent = child.parentNode;
      if (parent) {
        parent.removeChild(child);
      }
    },

    createElement: (tag, isSVG, is) => {
      let element;
      if (tag === "Rectangle") {
        // 创建一个矩形
        element = new window.PIXI.Graphics();
        element.lineStyle(4, 0xff3300, 1);
        element.beginFill(0x66ccff);
        element.drawRect(0, 0, 64, 64);
        element.endFill();
        element.x = 0;
        element.y = 0;
        // Opt-in to interactivity
        element.interactive = true;

        // Shows hand cursor
        element.buttonMode = true;
      } else if (tag === "Sprite") {
        element = new window.PIXI.Sprite();
        element.x = 0;
        element.y = 0;
      } else if (tag === "Container") {
        element = new window.PIXI.Container();
        element.x = 0;
        element.y = 0;
      }

      return element;
    },

    createText: (text) => doc.createTextNode(text),

    createComment: (text) => {
    //   console.log(text);
    },

    setText: (node, text) => {
      node.nodeValue = text;
    },

    setElementText: (el, text) => {
      el.textContent = text;
    },

    parentNode: (node) => node.parentNode,

    nextSibling: (node) => node.nextSibling,

    querySelector: (selector) => doc.querySelector(selector),

    setScopeId(el, id) {
      el.setAttribute(id, "");
    },

    cloneNode(el) {
      return el.cloneNode(true);
    },
  };
};

```

Pixi中的属性修改可以使用下面的代码，判断x、y、width和on属性不同的操作，就是用响应式包裹了Pixi的对象。关于Vue 3和Pixi实现的代码效果，你可以在 [GitHub](https://github.dev/shengxinjing/vue3-vs-vue2/blob/0911af848941c2eeb2783c32c1907fd286134be1/vue3-runtime-canvas/index.js) 看到全部的源码。

```xml
export const patchProp = (
  el,
  key,
  prevValue,
  nextValue,
见  isSVG = false,
) => {
  switch (key) {
    case "x":
    case "y":
    case "width":
    case "height":
        el[key] = nextValue;
        break;
    case "on":
      Object.keys(nextValue).forEach((eventName) => {
        const callback = nextValue[eventName];
        el.on(eventName, callback);
      });
      break;
    case "texture":
        let texture = PIXI.Texture.from(nextValue);
        el.texture = texture;
        break;
  }
};

```

## 总结

今天聊的内容到此就结束了，我们来总结一下今天学到的知识点。

首先我们了解了自定义渲染器的原理，就是 **把所有的增删改查操作暴露出去，使用的时候不需要知道内部的实现细节，我们只需要针对每个平台使用不同的API即可**。

你可以这样理解，就像武侠小说中高手可以通过给你传输内力的方式控制你进行比武。我们打出去的每招每式都是来源于背后的高手，只不过自己做了简单的适配。在Vue渲染器的设计中就把document所有的操作都抽离成了nodeOps，并且通过调用Vue的createRenderer函数创建平台的渲染器。

这样一来，只要我们实现了Canvas平台的增删改查，就可以在Canvas的世界中使用Vue的响应式语法控制绘图和做游戏，Vue生态中对小程序和原生app的支持原理也是基于自定义渲染器实现的。

其实，自定义渲染器也代表着适配器设计模式的一个实践。除了自定义渲染器 API 的学习，我们也要反思一下自己现在负责的项目中，有哪些地方为了不同的接口或者平台写了太多的判断代码，是否也可以使用类似自定义渲染器的逻辑和模式，把多个组件、平台、接口之间不同的操作方式封装成一个核心模块，去进行单独函数的扩展。

## 思考题

最后留个思考题给你，Vue如何在node环境中渲染呢？欢迎在评论区分享你的答案，我们下一讲再见！