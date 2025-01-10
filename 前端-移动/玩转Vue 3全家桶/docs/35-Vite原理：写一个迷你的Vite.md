你好，我是大圣。

上一讲学完了Vue的编译原理后，我们就把Vue的整体流程梳理完毕了，但是我们在使用Vue的时候，还会用到很多Vue生态的库。所以从今天开始，我会带你了解几个Vue生态中重要成员的原理和源码，今天我先带你剖析一下我们项目中用的工程化工具Vite的原理。

## 现在工程化的痛点

现在前端开发项目的时候，工程化工具已经成为了标准配置，webpack是现在使用率最高的工程化框架，它可以很好地帮助我们完成从代码调试到打包的全过程，但是随着项目规模的爆炸式增长， **webpack也带来了一些痛点问题**。

最早webpack可以帮助我们在JavaScript文件中使用require导入其他JavaScript、CSS、image等文件，并且提供了dev-server启动测试服务器，极大地提高了我们开发项目的效率。

webpack的核心原理就是通过分析JavaScript中的require语句，分析出当前JavaScript文件所有的依赖文件，然后递归分析之后，就得到了整个项目的一个依赖图。对图中不同格式的文件执行不同的loader，比如会把CSS文件解析成加载CSS标签的JavaScript代码，最后基于这个依赖图获取所有的文件。

进行打包处理之后，放在内存中提供给浏览器使用，然后dev-server会启动一个测试服务器打开页面，并且在代码文件修改之后可以通过WebSocket通知前端自动更新页面， **也就是我们熟悉的热更新功能**。

由于webpack在项目调试之前，要把所有文件的依赖关系收集完，打包处理后才能启动测试，很多大项目我们执行调试命令后需要等1分钟以上才能开始调试。这对于开发者来说，这段时间除了摸鱼什么都干不了，而且热更新也需要等几秒钟才能生效，极大地影响了我们开发的效率。所以针对webpack这种打包bundle的思路，社区就诞生了bundless的框架，Vite就是其中的佼佼者。

前端的项目之所以需要webpack打包，是因为 **浏览器里的JavaScript没有很好的方式去引入其他文件**。webpack提供的打包功能可以帮助我们更好地组织开发代码，但是现在大部分浏览器都支持了ES6的module功能，我们在浏览器内使用type="module"标记一个script后，在src/main.js中就可以直接使用import语法去引入一个新的JavaScript文件。这样我们其实可以不依赖webpack的打包功能，利用浏览器的module功能就可以重新组织我们的代码。

```javascript
    <script type="module" src="/src/main.js"></script>

```

## Vite原理

了解了script的使用方式之后，我们来实现一个 **迷你的 Vite** 来讲解其大致的原理。

首先，浏览器的module功能有一些限制需要额外处理。浏览器识别出JavaScript中的import语句后，会发起一个新的网络请求去获取新的文件，所以只支持/、./和…/开头的路径。

而在下面的Vue项目启动代码中，首先浏览器并不知道Vue是从哪来，我们第一个要做的，就是分析文件中的import语句。如果路径不是一个相对路径或者绝对路径，那就说明这个模块是来自node\_modules，我们需要去node\_modules查找这个文件的入口文件后返回浏览器。然后 ./App.vue是相对路径，可以找到文件，但是浏览器不支持 .vue文件的解析，并且index.css也不是一个合法的JavaScript文件。

**我们需要解决以上三个问题，才能让Vue项目很好地在浏览器里跑起来。**

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import './index.css'

const app = createApp(App)
app.mount('#app')

```

怎么做呢？首先我们需要使用Koa搭建一个server，用来拦截浏览器发出的所有网络请求，才能实现上述功能。在下面代码中，我们使用Koa启动了一个服务器，并且访问首页内容读取index.html的内容。

```javascript
const fs = require('fs')
const path = require('path')
const Koa = require('koa')
const app = new Koa()

app.use(async ctx=>{
  const {request:{url,query} } = ctx
if(url=='/'){
    ctx.type="text/html"
    let content = fs.readFileSync('./index.html','utf-8')

    ctx.body = content
  }
})
app.listen(24678, ()=>{
  console.log('快来快来数一数，端口24678')
})

```

下面就是首页index.html的内容，一个div作为Vue启动的容器，并且通过script引入src.main.js。我们访问首页之后，就会看到浏览器内显示的geektime文本，并且发起了一个main.js的HTTP请求， **然后我们来解决页面中的报错问题**。

```javascript
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link rel="icon" href="/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vite App</title>
</head>
<body>
  <h1>geek time</h1>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>

```

首先import {createApp} from Vue这一步由于浏览器无法识别Vue的路径，就会直接抛出错误，所以我们要在Koa中把Vue的路径重写。为了方便演示，我们可以直接使用replace语句，把Vue改成/@modules/vue，使用@module开头的地址来告诉Koa这是一个需要去node\_modules查询的模块。

在下面的代码中，我们判断如果请求地址是js结尾，就去读取对应的文件内容，使用rewriteImport函数处理后再返回文件内容。在rewriteImport中我们实现了路径的替换，把Vue变成了 @modules/vue， 现在浏览器就会发起一个 [http://localhost:24678/@modules/vue](http://localhost:24678/@modules/vue) 的请求，下一步我们要在Koa中拦截这个请求，并且返回Vue的代码内容。

```javascript
const fs = require('fs')
const path = require('path')
const Koa = require('koa')
const app = new Koa()

function rewriteImport(content){
  return content.replace(/ from ['|"]([^'"]+)['|"]/g, function(s0,s1){
    // . ../ /开头的，都是相对路径
    if(s1[0]!=='.'&& s1[1]!=='/'){
      return ` from '/@modules/${s1}'`
    }else{
      return s0
    }
  })
}

app.use(async ctx=>{
  const {request:{url,query} } = ctx
  if(url=='/'){
      ctx.type="text/html"
      let content = fs.readFileSync('./index.html','utf-8')

      ctx.body = content
  }else if(url.endsWith('.js')){
    // js文件
    const p = path.resolve(__dirname,url.slice(1))
    ctx.type = 'application/javascript'
    const content = fs.readFileSync(p,'utf-8')
    ctx.body = rewriteImport(content)
  }
})
app.listen(24678, ()=>{
  console.log('快来快来说一书，端口24678')
})

```

![图片](https://static001.geekbang.org/resource/image/c3/62/c39f700e37b638345ae4cbd0228fd762.png?wh=1125x387)

然后我们在Koa中判断请求地址，如果是@module的地址，就把后面的Vue解析出来，去node\_modules中查询。然后拼接出目标路径 ./node\_modules/vue/package.json去读取Vue项目中package.json的module字段，这个字段的地址就是 ES6 规范的入口文件。在我们读取到文件后，再使用rewriteImport处理后返回即可。

这里还要使用rewriteImport的原因是，Vue文件内部也会使用import的语法去加载其他模块。然后我们就可以看到浏览器网络请求列表中多了好几个Vue的请求。

```javascript
else if(url.startsWith('/@modules/')){
    // 这是一个node_module里的东西
    const prefix = path.resolve(__dirname,'node_modules',url.replace('/@modules/',''))
    const module = require(prefix+'/package.json').module
    const p = path.resolve(prefix,module)
    const ret = fs.readFileSync(p,'utf-8')
    ctx.type = 'application/javascript'
    ctx.body = rewriteImport(ret)
}

```

![图片](https://static001.geekbang.org/resource/image/7f/fb/7fb5564ac59ffba085d9c7fd24f8f9fb.png?wh=1681x512)

**这样我们就实现了node\_modules模块的解析，然后我们来处理浏览器无法识别 .vue文件的错误。**

.vue文件是Vue中特有的文件格式，我们上一节课提过Vue内部通过@vue/compiler-sfc来解析单文件组件，把组件分成template、style、script三个部分，我们要做的就是在Node环境下，把template的内容解析成render函数，并且和script的内容组成组件对象，再返回即可。

其中，compiler-dom解析template的流程我们学习过，今天我们来看下如何使用。

在下面的代码中，我们判断 .vue的文件请求后，通过compilerSFC.parse方法解析Vue组件，通过返回的descriptor.script获取JavaScript代码，并且发起一个type=template的方法去获取render函数。在query.type是template的时候，调用compilerDom.compile解析template内容，直接返回render函数。

```javascript
const compilerSfc = require('@vue/compiler-sfc') // .vue
const compilerDom = require('@vue/compiler-dom') // 模板

if(url.indexOf('.vue')>-1){
    // vue单文件组件
    const p = path.resolve(__dirname, url.split('?')[0].slice(1))
    const {descriptor} = compilerSfc.parse(fs.readFileSync(p,'utf-8'))

    if(!query.type){
      ctx.type = 'application/javascript'
      // 借用vue自导的compile框架 解析单文件组件，其实相当于vue-loader做的事情
      ctx.body = `
  ${rewriteImport(descriptor.script.content.replace('export default ','const __script = '))}
  import { render as __render } from "${url}?type=template"
  __script.render = __render
  export default __script
      `
    }else if(query.type==='template'){
      // 模板内容
      const template = descriptor.template
      // 要在server端吧compiler做了
      const render = compilerDom.compile(template.content, {mode:"module"}).code
      ctx.type = 'application/javascript'

      ctx.body = rewriteImport(render)
    }


```

上面的代码实现之后，我们就可以在浏览器中看到App.vue组件解析的结果。App.vue会额外发起一个App.vue?type=template的请求，最终完成了整个App组件的解析。

![图片](https://static001.geekbang.org/resource/image/f9/90/f986571970188eac47bb4fac1af37d90.png?wh=1920x552)![图片](https://static001.geekbang.org/resource/image/cc/46/cc696c23a2a6d4e9eacf401375320146.png?wh=1920x384)

**接下来我们再来实现对CSS文件的支持。** 下面的代码中，如果url是CSS结尾，我们就返回一段JavaScript代码。这段JavaScript代码会在浏览器里创建一个style标签，标签内部放入我们读取的CSS文件代码。这种对CSS文件的处理方式，让CSS以JavaScript的形式返回，这样我们就实现了在Node中对Vue组件的渲染。

```javascript
if(url.endsWith('.css')){
    const p = path.resolve(__dirname,url.slice(1))
    const file = fs.readFileSync(p,'utf-8')
    const content = `
    const css = "${file.replace(/\n/g,'')}"
    let link = document.createElement('style')
    link.setAttribute('type', 'text/css')
    document.head.appendChild(link)
    link.innerHTML = css
    export default css
    `
    ctx.type = 'application/javascript'
    ctx.body = content
  }

```

![图片](https://static001.geekbang.org/resource/image/9f/f7/9f50c5ca0d9b74b680e41963055c99f7.png?wh=1920x628)

## Vite的热更新

最后我们再来看一下热更新如何实现。热更新的目的就是在我们修改代码之后， **浏览器能够自动渲染更新的内容**，所以我们要在客户端注入一个额外的JavaScript文件，这个文件用来和后端实现WebSocket通信。然后后端启动WebSocket服务，通过chokidar库监听文件夹的变化后，再通过WebSocket去通知浏览器即可。

下面的代码中，我们通过chokidar.watch实现了文件夹变更的监听，并且通过handleHMRUpdate通知客户端文件更新的类型。

```javascript

export function watch() {
  const watcher = chokidar.watch(appRoot, {
    ignored: ['**/node_modules/**', '**/.git/**'],
    ignoreInitial: true,
    ignorePermissionErrors: true,
    disableGlobbing: true,
  });
  watcher;

  return watcher;
}
export function handleHMRUpdate(opts: { file: string; ws: any }) {
  const { file, ws } = opts;
  const shortFile = getShortName(file, appRoot);
  const timestamp = Date.now();

  console.log(`[file change] ${chalk.dim(shortFile)}`);
  let updates;
  if (shortFile.endsWith('.css')) {
    updates = [
      {
        type: 'js-update',
        timestamp,
        path: `/${shortFile}`,
        acceptedPath: `/${shortFile}`,
      },
    ];
  }

  ws.send({
    type: 'update',
    updates,
  });
}

```

然后客户端注入一段额外的JavaScript代码，判断后端传递的类型是js-update还是css-update去执行不同的函数即可。

```javascript
async function handleMessage(payload: any) {
  switch (payload.type) {
    case 'connected':
      console.log(`[vite] connected.`);

      setInterval(() => socket.send('ping'), 30000);
      break;

    case 'update':
      payload.updates.forEach((update: Update) => {
        if (update.type === 'js-update') {
          fetchUpdate(update);
        }
      });
      break;
  }
}

```

## 总结

以上就是今天的主要内容，我们来总结一下吧！

首先，我们通过了解webpack的大致原理，知道了现在webpack在开发体验上的痛点。除了用户体验UX之外，开发者的体验DX也是项目质量的重要因素。

webpack启动服务器之前需要进行项目的打包，而Vite则是可以直接启动服务，通过浏览器运行时的请求拦截，实现首页文件的按需加载，这样开发服务器启动的时间就和整个项目的复杂度解耦。任何时候我们启动Vite的调试服务器，基本都可以在一秒以内响应，这极大地提升了开发者的体验，这也是Vite的使用率越来越高的原因。

并且我们可以看到，Vite的主要目的就是提供一个调试服务器。Vite也可以和Vue解耦，实现对任何框架的支持，如果使用Vite支持React，只需要解析React中的JSX就可以实现。这也是Vite项目的现状，我们只需要使用框架对应的Vite插件就可以支持任意框架。

Vite能够做到这么快的原因，还有一部分是因为使用了esbuild去解析JavaScript文件。esbuild是一个用Go语言实现的JavaScript打包器，支持JavaScript和TypeScript语法，现在前端工程化领域的工具也越来越多地使用Go和Rust等更高效的语言书写，这也是性能优化的一个方向。

## 思考题

最后留一个思考题吧。如果一个模块文件是分散的，导致Vite首页一下子要加载1000个JavaScript文件造成卡顿，我们该如何处理这种情况呢？

欢迎在评论区分享你的答案，我们下一讲再见！