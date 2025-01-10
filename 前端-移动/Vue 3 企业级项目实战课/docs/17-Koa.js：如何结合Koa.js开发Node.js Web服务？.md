你好，我是杨文坚。

上节课我们分析了单页面应用的原理，并且使用了vue-router来实现Vue.js的单页面应用。这节课，我们就来做进一步的扩展，接入Koa.js，实现Node.js的Web服务，打造一个前后端分离的Node.js全栈项目。

可能你有疑问，为什么作为前端开发工程师，需要自己开发后端服务呢？

这其实跟工作分工有关。绝大多数企业，不管是“前端”“后端”，还是“测试”，程序员的核心工作都是帮企业解决实际的技术问题。如果你负责某个项目，遇到了技术问题，但是问题所属的技术领域不是自己职位的领域，也是需要自己想办法解决的。

也就是说，你作为前端程序员，负责实现一个全栈项目，无论怎么努力沟通，都没有后端程序员来支持开发，那就需要自己动手解决了。这种情况其实也是大厂的常态。在大厂里，前端程序员都会Node.js的Web服务开发，以备工作不时之需。

为什么大家要选择Node.js来开发Web服务，而不是其他语言呢？

## 为什么要用Node.js开发Web服务？

在大厂里，前端程序员用Node.js开发Web服务，核心原因是Node.js的主要开发语言也是JavaScript。所以，Node.js对于前端程序员来讲， **入门和学习成本较低，甚至可以说是无缝切换**。

因为Node.js同样用JavaScript语言，前端页面中用到的大部分JavaScript工具库，比如lodash.js之类的工具，也是能直接用在Node.js服务端中的，甚至我们课程中的Vue.js前端组件，也能稍作处理，放在Node.js服务端里运行。

总的来说，我们课程中运营搭建的全栈项目选择Node.js开发，有三个优势：

- 前后端统一用JavaScript，学习成本低；
- 代码可前后端复用，能提高开发效率；
- Vue.js组件可以用于前端和服务端渲染。

好，用Node.js开发Web服务已经确定了， **但Node.js只是个JavaScript运行环境，那该选择什么框架或者工具来开发Web服务呢？**

在Node.js中，市面上主流用来开发Web服务的框架有Express.js、Koa.js、Egg.js、Nest.js等。我们课程项目里选择Koa.js，有这几个原因：

- Koa.js框架精简，轻量简单，源码就几个JavaScript文件；
- Koa.js洋葱中间件模型的灵活优势；
- Koa.js的中间件生态丰富；
- 国内大厂广泛使用Koa.js，用于封装业务Web框架，例如阿里开源的Egg.js等。

其实Koa.js之外的其它Web服务框架，功能都很齐全，但是学习成本高，框架结构的复杂度也高。 **我们使用一个框架，最重要的，不是看它功能是否齐全，而是看自己能否弄清它的核心原理，出问题时知道怎么排查原因。** 所以，我们就选择了Koa.js作为项目的Web服务框架。

那么，如何使用Koa.js开发Node.js服务呢？

## 如何使用Koa.js开发Node.js服务?

首先，你要理解一点，所有Web服务框架都是处理HTTP请求和响应的，不管是Koa.js，还是Express.js、Egg.js等Node.js Web框架，最核心功能就是处理HTTP请求和响应， **框架之间的差异，主要是处理HTTP的流程操作或设计理念不一样**。

我们先看相同，再看差异。

### 核心要素http模块

演示一下在Node.js中最简单的一个HTTP服务，如下代码所示：

```javascript
// easy-server.cjs
const http = require('node:http');

const server = http.createServer((req, res) => {
  const url = req.url;
  const html = `
  <html>
    <head>
      <meta charset="utf-8" />
    </head>
    <body>
      <h1>当前页面链接: ${url}</h1>
    </body>
  </html>
  `;
  res.end(html);
});

server.listen(6001, () => {
  console.log('服务已经启动，浏览器打开 http://127.0.0.1:6001/');
});

```

这段代码是通过Node.js的“http”模块，快速实现一个HTTP服务， **所有的Node.js Web框架的最核心点就是利用这个Node.js原生能力**。

执行启动这个简单的Node.js服务“node ./easy-server.cjs”，然后用浏览器访问，效果如下图所示：

![图片](https://static001.geekbang.org/resource/image/49/c7/49c9917c41870de0e20d263a925bc2c7.png?wh=606x411)

上述的代码也可以直接用TypeScript来编写，代码可以改成这样：

```typescript
// easy-server.ts
import http from 'node:http';

const server = http.createServer(
  (
    req: http.IncomingMessage,
    res: http.ServerResponse<http.IncomingMessage>
  ) => {
    const url = req.url;
    const html = `
  <html>
    <head>
      <meta charset="utf-8" />
    </head>
    <body>
      <h1>当前页面链接: ${url}</h1>
    </body>
  </html>
  `;
    res.end(html);
  }
);

server.listen(6001, () => {
  console.log('服务已经启动，浏览器打开 http://127.0.0.1:6001/');
});

```

这个时候，我们可以使用 vite-node 这个npm模块，在本地计算机全局安装这个命令，直接启动TypeScript文件，如执行这个命令 “vite-node ./easy-server.ts”。

我们了解了Node.js Web框架的核心要素http模块之后，剩下需要掌握的就是 **不同框架对HTTP操作的设计理念**。

### 不同设计理念

我们主要用到Web框架是Koa.js，那么它核心的分析服务设计理念，就是处理HTTP请求的中间件流程设计，也就是“ **洋葱模型**”。这我先给你展示一段代码：

```typescript
/* eslint-disable no-console */
import Koa from 'koa';
import type { Context, Next } from 'koa';

const app = new Koa();

app.use(async (ctx: Context, next: Next) => {
  console.log(`[${ctx.path}] 打印 001`);
  await next();
  console.log(`[${ctx.path}] 打印 004`);
});

app.use(async (ctx: Context, next: Next) => {
  console.log(`[${ctx.path}] 处理HTTP响应之前`);
  ctx.body = `<html>
  <head>
    <meta charset="utf-8" />
  </head>
  <body>
    <h1>当前页面链接: ${ctx.path}</h1>
  </body>
</html>`;
  await next();
  console.log(`[${ctx.path}] 处理HTTP响应之后`);
});

app.use(async (ctx: Context, next: Next) => {
  console.log(`[${ctx.path}] 打印 002`);
  await next();
  console.log(`[${ctx.path}] 打印 003`);
});

app.listen(6001, () => {
  console.log('Koa.js 服务已经启动，浏览器打开 http://127.0.0.1:6001/');
});

```

这段代码执行后，可以访问 [http://127.0.0.1:6001/hello](http://127.0.0.1:6001/hello) 连接，得到控制台这样的打印顺序：

![图片](https://static001.geekbang.org/resource/image/b3/d8/b3082666c44213b87c138c0da33f18d8.png?wh=783x469)

这种打印结果就是洋葱模型的效果，每个异步函数，都是一个中间件，执行时候“先进后出”。其实，每个中间件，都等于一个Promise。我把上述的代码拆解成简单的JavaScript代码，你就能理解中间件模型了，代码如下所示：

```typescript
// middleware-demo.ts
const context = {};

async function middleware1(ctx: any, next: any) {
  console.log('打印 001');
  await next();
  console.log('打印 004');
}

async function middleware2(ctx: any, next: any) {
  console.log('处理HTTP响应之前');
  await next();
  console.log('处理HTTP响应之后');
}

async function middleware3(ctx: any, next: any) {
  console.log('打印 002');
  await next();
  console.log('打印 003');
}

Promise.resolve(
  middleware1(context, async () => {
    return Promise.resolve(
      middleware2(context, async () => {
        return Promise.resolve(
          middleware3(context, async () => {
            return Promise.resolve();
          })
        );
      })
    );
  })
).then(() => {
  console.log('执行结束');
});

```

执行后的打印效果如下：

![图片](https://static001.geekbang.org/resource/image/66/33/66562247cf579d56ba84b88ab2678033.png?wh=761x294)

你看，所谓的洋葱模型中间件，就是Promise嵌套。“先进后出”的效果就是Promise嵌套中resolve前后控制。

Koa.js的中间件洋葱模型，核心是用koa-compose这个npm模块来实现的，代码就100行左右，原理就是实现类似的Promise嵌套能力。结合上面的Promise嵌套代码，我们可以整理出其完整的模型，如下图所示：

![图片](https://static001.geekbang.org/resource/image/9d/bd/9d70yyf2ca465862aea95ef1af818ebd.jpg?wh=1920x1197)

Koa.js本身框架极其简单，虽然只提供了HTTP请求和相应的处理能力，但是由于中间件模型灵活度高，可以控制整个HTTP的请求和相应过程，提供了很强的扩展能力，经过近七八年的沉淀，积累了很多功能中间件。开发者可以基于Koa.js选择对应功能的中间件，来实现Web服务所需要的功能。

我们课程里涉及到的Node.js Web服务，都是基于Koa.js来选择需要功能中间件，组装成需要的功能服务。具体怎么选择和组装，我们详细看一下。

一般Web服务基础功能有四点：

- 服务端路由控制；
- 静态资源加载；
- HTML页面渲染；
- 提供API接口（Ajax/JSONP接口）。

这时候，Koa.js可以通过找对应的中间件，来实现对应功能：

- 中间件koa-router处理路由；
- 中间件koa-static处理静态资源，同时，用koa-mount来辅助处理静态资源的URL前缀；
- Koa.js自带的Context控制渲染HTML和处理API。

那么接下来，我们课程Web服务架构的具体目录，可以设计成这样：

```shell
# packages/work-server/src
.
├── controller/*
├── public/*
├── service/*
├── template/*
├── util/*
├── router.ts
└── index.ts

```

我们来分析一下主要的目录和文件设计：

- 文件router.ts，是路由层 ，定义Web服务的URL内容；
- 目录controller，是控制层，控制页面内容和API内容的HTTP响应；
- 目录service，是业务层，提供一些业务逻辑的操作；
- 目录public，是静态资源目录，存放JavaScript、CSS和图片等静态资源。

![图片](https://static001.geekbang.org/resource/image/86/80/86c15768d31b41eaf344763977628580.jpg?wh=1920x1080)

具体的技术结构可以结合下图理解：

![图片](https://static001.geekbang.org/resource/image/5f/fd/5f2dece9f2b4c96a36c4071f9bc69efd.jpg?wh=1920x1080)

我们基于TypeScript实现路由层的代码，如下所示：

```typescript
// packages/work-server/src/router.ts

import Router from '@koa/router';
import { renderPage } from './controller/page';
import { getData } from './controller/api';

const router = new Router();
router.get('/page/:pageName', renderPage);
router.get('/page/:pageName/:subPageName', renderPage);
router.get('/api/getData', getData);
const routers = router.routes();

export default routers;

```

控制层，我们实现了两个控制内容。

一个是页面渲染控制：

```typescript
// packages/work-server/src/controller/page.ts
import type { Context, Next } from 'koa';
import { getPageHTML } from '../util/file';

export const renderPage = async (ctx: Context, next: Next) => {
  ctx.body = getPageHTML(ctx.params.pageName);
  await next();
};

```

另一个控制层内容是API请求控制，就是Ajax或者HTTPXMLRequest的请求操作：

```typescript
// packages/work-server/src/controller/api.ts
import type { Context, Next } from 'koa';

export const getData = async (ctx: Context, next: Next) => {
  const data = [
    { id: 'A001', name: '001' },
    { id: 'A002', name: '002' },
    { id: 'A003', name: '003' },
    { id: 'A004', name: '004' },
    { id: 'A005', name: '005' }
  ];
  ctx.body = data;
  await next();
};

```

最后启动代码为如下所示：

```typescript
// packages/work-server/src/index.ts
import path from 'node:path';
import Koa from 'koa';
import koaStatic from 'koa-static';
import koaMount from 'koa-mount';
import routers from './router';
import { getServerDir } from './util/file';

const app = new Koa();

const publicDirPath = path.join(getServerDir(), 'public');
app.use(koaMount('/public', koaStatic(publicDirPath)));
app.use(routers);

const port = 8001;

app.listen(port, () => {
  console.log('服务启动: http://127.0.0.1:' + port);
});

```

最后你就可以用vite-node启动TypeScript的服务代码，访问服务页面。

现在，我们已经成功实现了一个基于Koa.js的Web服务，接下来，就要集合上节课的前端代码，整合前后端分离的全栈项目。这里你估计会有疑问，为什么需要做项目的前后端分离呢？

## 为什么需要前后端项目分离？

考虑三个视角，分别是技术视角、管理视角和行情视角。

从 **技术视角** 上看，前后端分离能让前端代码和服务端代码解耦，不会杂糅混合在一起，代码的目录和职责都很分明。反之，如果前后端代码耦合在一起，类似PHP、JSP等技术，一些前后端的功能代码都写在一起，虽然开发方便，但是不好区分功能职责。

从 **管理视角** 上看，项目的开发不是一次性的，会随着业务需求的变化不停迭代。如果我们不做前后端代码的解耦，耦合的代码在后续的频繁修改下，容易埋下代码混乱的隐患，直到陷入难以修改维护的困境。

前后端分离在项目管理视角中，还有另一个要素，就是“ **迁移成本**”。项目到一定体量要做升级优化，前端代码要独立部署到CDN里，后端代码要“上云”部署到云服务上。前后端分离的项目可以用很低的成本完成升级改造，甚至后续项目重构，比如后端代码要替换开发语言，从Node.js换成Java，或者前端代码替换框架，从Vue.js换成React.js，前后端分离的项目在重构过程中，也能保证不会带来太大的干扰成本。

第三个就是 **行情视角**，目前国内大部分企业的Web项目基本都是前后端分离，只有极少数陈年老项目是前后端代码耦合在一起的。但国外的项目很多还是前后端耦合在一起的项目，例如很多国外网站是基于PHP开发的项目，或者基于PHP框架WordPress，前端代码很多是写在PHP文件里的。

所以，基于以上三个视角的考虑，我选择了前后端分离的项目管理形式。那么，接下来，我们要如何设计Vue.js和Koa.js的前后端分离项目呢？

## 如何设计Vue.js和Koa.js前后端分离项目？

首先我们做一下整体的前后端的关系设计，看流程图：

![图片](https://static001.geekbang.org/resource/image/fd/2b/fd90911a9e8be0e4ca1aea517a221c2b.jpg?wh=1920x1080)

这里，前端项目和后端项目是两个独立子项目，前端跟后端项目的联动主要是提供静态资源。前端项目将JavaScript和CSS等静态资源给后端，让后端能在渲染HTML页面时加载前端的静态资源，进而渲染页面。

从项目实现的架构中，我们不难看出，实际项目可以拆分成monorepo里的两个子项目：

- 前端子项目，主要是管理浏览器运行的JS/CSS代码；
- 后端子项目，主要是管理Node.js环境运行的代码。

现在区分出了两个子项目的项目实现，接下来就是两个子项目如何在生产模式和开发模式下实现前后端联动的问题了。

### **开发模式**

**现在我们先来设计前后端分离项目的“开发模式”**：

![图片](https://static001.geekbang.org/resource/image/97/d6/97c52b5543da5d5bd20f4f5d743967d6.jpg?wh=1920x1080)

这里可以看出，前端子项目的开发模式是用Vite启动开发服务来编译Vue.js代码的，而且提供了一个8002端口的服务。开发过程中，我们基本都用TypeScript语法开发，基于Vite的开发服务来实现ES Modules模块的编译和热更新。

前端子项目Vite只提供热更新的JavaScript代码和CSS代码，剩下的所有HTML和API的HTTP请求，都要通过Vite代理转发到后端子项目服务。

后端子项目用Koa.js直接搭建服务，也是用TypeScript语法开发，并基于nodemon和ts-node实现开发过程中的热更新。nodemon模块主要用于Node.js服务代码的热更新，ts-node模块主要是编译TypeScript代码。

当Koa.js通过nodemon和ts-node启动开发模式的Web服务后，就可以提供渲染HTML和数据API的HTTP请求，并提供给前端的Vite服务。

在开发模式中，我们要启动两个开发服务：一个是前端Vite服务，主要做前端代码热更新；另一个是Koa.js的Web服务，包括其代码的热更新。但开发过程中主要是访问Vite服务，也就是图中的8002端口的服务，因为Vite服务已经代理了Koa.js的服务。

这时候，你可能有疑问，为什么Koa.js服务开发模式用的是ts-node，而不是用vite-node呢？这是因为目前ts-node比较成熟，同时nodemon也提供了ts-node启动TypeScript热更新代码的配置支持。而vite-node主要是面向Vite的能力扩展，能直接运行ES Module的TypeScript代码。

### 生产模式

**接下来我们再来看看前后端分离项目“生产模式”的分离设计**，同样我也画了相关的结构图，如下所示：

![图片](https://static001.geekbang.org/resource/image/27/91/272721374ab1yy22ebeec9c6f0933891.jpg?wh=1920x1080)

从图中可知，前端通过Webpack编译，将前端子项目的TypeScript和Less代码，分别编译成JS和CSS文件。这里用Webpack，我们主要考虑的是生产环境用Webpack这个老牌框架，会更稳定些，构建出来的结果比较放心。

后端子项目基于Rollup编译成CommonJS模块，主要是用Rollup将TypeScript代码文件一一对应编译成JavaScript代码，可以直接在Node.js环境运行。同时将前端子项目编译结果一同打包出交付产物。具体交付构建流程，如下图所示：

![图片](https://static001.geekbang.org/resource/image/1d/a4/1d0e7a13651cfbeaff194045fdc1d7a4.jpg?wh=1920x1080)

这个时候你可能会问，既然开发模式下能直接运行代码，为什么不直接用于生产模式呢？这是因为，开发模式下前后端所有代码还是处于TypeScript的“中间状态”。

开发模式下，前端项目是通过Vite做热更新编译和调试TypeScript代码，要实时监听文件变化和编译，十分耗性能。同样的，后端是用nodemon和ts-node实时监听和编译TypeScript代码，也是十分费性能。

所以，生产模式要把源代码的“中间状态”转成“最终状态”，直接变成最终的运行代码的状态。

这个“变化的过程”就是将前端TypeScript和Less代码编译成JavaScript和CSS代码，能在浏览器里直接运行；将后端TypeScript代码编译成CommonJS格式JavaScript代码，能在Node.js环境里直接运行。

具体完整代码，请看文稿最后的源码链接。

## 总结

通过本节课的学习，相信你已经知道了Node.js搭建全栈Web项目的原理和实现方式。这节课的实现跨度有点大，我们从Node.js服务端开发入门，跳跃到Koa.js的原理了解和使用，又从前后端项目分离设计，跳跃到全栈项目的生产和开发模式的构建落地实现。

我们按知识点逐个总结：

- Node.js Web服务开发的核心原理是处理HTTP请求和响应，也就是Node.js原生http模块的使用；
- Koa.js的核心原理是洋葱模型的中间件体系，基于这个中间件模型，我们可以构造出处理各种HTTP服务操作的中间件；
- 前后端项目分离的理念要从具体的需求场景来分析，要从“技术”“管理”和“行情”这三个视角看待，不能脱离实际环境，一昧讨论技术理念的利弊优劣；
- 构建Node.js的Web全栈项目，需要做好开发模式和生产模式的联动处理。特别是在生产模式下，要保证最终产物能直接在对应环境中运行，不能是开发代码的“原始代码”或者开发模式的“中间产物”。

希望你能通过这节课的学习，进入一个更新的技术台阶，脱离前端“只会写页面代码”的桎梏，成长为一个能解决全栈问题的工程师。

## 思考题

Koa.js和Express.js的中间件模型有什么区别吗？

欢迎在留言区参与讨论，我们下节课见。

### [完整的代码在这里](https://github.com/FE-star/vue3-course/tree/main/chapter/17)