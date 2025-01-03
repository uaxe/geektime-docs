你好，我是Barry。

前端实战篇即将步入尾声。之前的课程中，整体的前端项目开发已经告一段落，在本地即可访问项目的完整功能，但是，如果想让更多的人在浏览器直接访问我们的平台，又该如何实现呢？

为了让更多的用户访问视频平台界面。这节课我们就一起来学习一下，如何将我们的前端代码打包上线。

想要高效地打包代码，我们需要用到模块管理工具Webpack。这款工具你应该不陌生，因为我们在最初构建项目的时候就用过它。

只有全面了解Webpack，你才能在后续项目部署的时候轻车熟路，快速实现项目管理和项目打包。而且，Webpack也是在技术面试中也是个高频考点，难度系数也比较高。不过不要有心理负担，耐心学完这节课，你就能找到掌握Webpack的诀窍了。

## Webpack初识

Webpack 是一种模块打包工具，它可以将多个 JavaScript 模块打包成一个或多个 JavaScript 文件，从而减少网页加载时的体积。Webpack 主要用于构建大型的、复杂的应用程序，比如游戏、后端服务等。

Webpack 的工作原理是将源代码分割成一个个模块，然后使用 loader 将这些模块打包成一个或多个 JavaScript 文件。每个模块都可以看作一个独立的文件，它们之间通过依赖关系相互联系。

在 Webpack 当中，常用的模块打包器有 Babel、Parcel、Compression等。除去模块打包，它们还可以对代码进行压缩、优化等处理。

另外，Webpack 还支持多种插件，这些插件可以扩展其功能，比如支持多种 loaders、支持代码分割、支持自动化测试等。

分析了这么多，不难看出Webpack 是一种非常强大的模块打包工具，它可以帮助开发者快速构建高质量的网页应用程序。

## Webpack详解

了解了Webpack的作用之后呢，我们还需要深入了解Webpack的核心内容，为后续在项目中应用它打好基础。当然如果你想更全面地了解这个工具，也可以在课后直接访问 [Webpack的中文官网](https://www.webpackjs.com/concepts/)。

![](https://static001.geekbang.org/resource/image/b2/b1/b23208380aae146dc73bf2725c8d8eb1.jpg?wh=2896x1238)

首先我们需要详细了解Webpack的 **核心概念。** 这些概念对应的官网链接我也为你做了整理，方便你课后拓展学习。

- [入口](https://www.webpackjs.com/concepts/entry-points/)
- [输出](https://www.webpackjs.com/concepts/output/)
- [loader](https://www.webpackjs.com/concepts/loaders/)
- [插件](https://www.webpackjs.com/concepts/plugins/)
- [模式](https://www.webpackjs.com/concepts/#mode)
- [浏览器兼容性](https://www.webpackjs.com/concepts/#browser-compatibility)
- [环境](https://www.webpackjs.com/concepts/#environment)

接下来我们就依次来学习前面列出的每一种属性，了解其核心作用和使用技巧。

### 入口（entry）

Webpack 的入口起点是指 Webpack 在开始打包之前所加载的第一个模块或文件。在 Webpack 中，入口起点通常是 entry（或 module）属性。Webpack 会从入口起点开始打包，直到遇到第一个不允许打包的模块或文件为止。

**入口起点的设置非常重要，因为它会影响 Webpack 打包的策略**。通常情况下，Webpack 会使用入口起点来决定哪些模块需要打包、哪些模块应该被忽略。如果入口起点设置得不合理，可能会导致打包结果不符合预期，甚至导致项目无法正常运行。

在项目当中我们默认的入口是main.js，具体的配置路径在项目的build文件夹下面的webpack.base.conf.js文件内。你可以结合后面的具体代码案例来加深理解。

```plain
module.exports = {
  context: path.resolve(__dirname, '../'),
  entry: {
    app: './src/main.js'
  }
   //其中还有其他的一些应用
 }

```

因为我们本身使用的是Vue-cli脚手架，所以这些代码不需要你单独再写一遍，搭建过程就自动配置好了。不过你一定要对它的实现原理非常熟悉，这样需要根据项目需求调整Webpack配置的时候，你才能够快速上手。

了解了入口配置之后，我们紧接着来看一下输出的配置，这是我们最终生成打包文件的核心配置。

### 输出（output）

Webpack的输出（output）是指打包后生成的可执行文件或资源文件的位置和文件名等相关信息。

在Webpack的配置当中，我们可以通过output属性来指定输出位置，配置打包后的文件输出路径、文件名和文件描述等，output可以接受一个对象，这个对象包含后面这些属性。

- filename: 指定打包后生成的文件名，可以包含占位符，如\[name\].\[hash\].js，其中\[name\]表示模块名称，\[hash\]表示文件哈希值。
- path: 指定打包后生成的文件存放路径，一般设置为项目的静态资源目录。
- publicPath: 指定打包后的文件生成的路径，可以避免在构建时对资源文件进行绝对路径解析，例如项目中图片、样式等静态资源文件的访问路径。

我也把在项目中具体的配置写在了后面，供你参考。

```plain
module.exports = {
  context: path.resolve(__dirname, '../'),
  entry: {
    app: './src/main.js'
  },
  output: {
    path: config.build.assetsRoot,
    filename: '[name].js',
    publicPath: process.env.NODE_ENV === 'production' ?
      config.build.assetsPublicPath :
      config.dev.assetsPublicPath
  }
}

```

和入口部分一样，output部分也是在项目构建的时候创建好的，通常来说也不需要我们做更改，但是你要明白它的作用。

### loader

接下来要学习的是处理模块的插件loader。Webpack loader是一个用来处理模块的插件，loader的主要作用是对模块进行转换和处理，它可以将各种类型的文件转换成Webpack可以处理的模块。

具体来说，它可以接受一个输入文件，然后对其进行解析、压缩、混淆、编译等操作，最终输出一个可以供Webpack打包的模块。常见的loader包括babel-loader、css-loader、file-loader、url-loader等，你可以参考后面这张表格来了解它们的用途。

![](https://static001.geekbang.org/resource/image/3a/b5/3a518fea34634d796c3e6ea9420e38b5.jpg?wh=2452x1283)

通过loader的支持，Webpack能够更好地处理和转换不同的模块类型，从而提升开发效率和构建质量。

只看原理有点抽象，我们通过一个简单的案例来直观感受一下，在项目中我们该如何使用loader。

```plain
module: {
    rules: [{
      test: /\.vue$/,
      loader: 'vue-loader',
      options: vueLoaderConfig
    }, {
      test: /\.less$/,
      loader: "style-loader!css-loader!less-loader",
    },{
      test: /\.js$/,
      loader: 'babel-loader',
      include: [resolve('src'), resolve('test'), resolve('node_modules/webpack-dev-server/client')]
    }, {
      test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
      loader: 'url-loader',
      options: {
        limit: 10000,
        name: utils.assetsPath('img/[name].[hash:7].[ext]')
      }
    }, {
      test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
      loader: 'url-loader',
      options: {
        limit: 10000,
        name: utils.assetsPath('media/[name].[hash:7].[ext]')
      }
    }, {
      test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
      loader: 'url-loader',
      options: {
        limit: 10000,
        name: utils.assetsPath('fonts/[name].[hash:7].[ext]')
      }
    }]
  }

```

通过这个案例，loader的用法就一目了然了。可以看到，loader的配置内容也是放在webpack.base.conf.js文件里的。

- 对于.vue、.less、.js文件，我们使用babel-loader转换。
- .vue文件需要使用vue-loader处理。
- .less文件需要使用style-loader、css-loader处理。
- .css文件需要使用css-losder处理。

通过配置loader，我们可以轻松地支持各种类型的模块，提升开发效率。

### 插件（plugin）

如果我们想要扩展 Webpack 功能的模块，想要修改 Webpack 的打包过程和处理逻辑，那么我们该如何实现呢？这时候就需要用到Webpack 插件了。

Webpack中的插件是一种用于扩展Webpack功能的模块，它可以用来执行各种任务，例如打包优化、代码分割、资源管理等。在Webpack的配置中，插件可以通过plugins属性来指定。

Webpack提供了许多内置的插件，例如html-webpack-plugin、CopyWebpackPlugin等。同时，Webpack还支持自定义插件，开发者可以编写自己的插件来实现特定的功能。

接下来，对于如何使用html-webpack-plugin，我们还是结合案例来体会。

```plain
plugins: [
    new webpack.DefinePlugin({
      'process.env': require('../config/dev.env')
    }),
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: 'index.html',
      inject: true
    }),
    new CopyWebpackPlugin([
      {
        from: path.resolve(__dirname, '../static'),
        to: config.dev.assetsSubDirectory,
        ignore: ['.*']
      }
    ])
  ]

```

这段代码配置了HtmlWebpackPlugin插件，目的是生成一个名为"index.html"的HTML文件，并使用名为"index.html"的文件作为模板，将Webpack打包生成的脚本和样式标签直接注入到生成的HTML文件中。

具体的参数用途我也给你列在了下面，你大致了解就可以。

![](https://static001.geekbang.org/resource/image/4f/b8/4f169b4dcd013881fcb9206ea74167b8.jpg?wh=3408x1228)

### 模式（mode）

最后，我们一起来了解一下Webpack是如何适应不同的构造环境的。也许你会有疑问，为什么要使用不同的构造环境呢？

这是因为不同的构造环境会提供不同的编译选项和优化策略，这样可以满足更多开发者的需求。

Webpack中的mode是一个配置选项，主要用于指定 Webpack 的工作模式。它有三种取值：none、development 和 production。三种模式具体的应用场景是后面这样。

![](https://static001.geekbang.org/resource/image/07/a9/07521dc673b054235bc03329e8204da9.jpg?wh=2963x1284)

在 Webpack 的配置中，我们可以根据需求去选择不同模式去构建应用程序，具体可以通过设置 mode 属性来实现。你可以参考后面这个例子。

```plain
module.exports = {
  mode: 'development'
};

```

到这里，我们就理清了Webpack里最核心的部分。

这里我想带你系统梳理一下，Webpack在Vue项目里各阶段发挥了哪些作用。看完以后，你就会明白，为什么我们在项目的脚手架构建环节就已经设置好了对应的Webpack配置项，仍然需要专门学习了解这些配置项的作用和用法。

Webpack在Vue项目的构建和打包阶段发挥着不可或缺的作用。

在开发阶段，Webpack可以通过各种插件和工具提供开发环境，可以让你能够更加高效地开发和调试项目。同时，在生产环境中，Webpack还可以帮助开发人员将Vue项目中的代码和资源打包成一个或多个静态文件，从而在浏览器中加载和运行。

通过Webpack的代码分割和优化等功能，可以提高Vue项目的性能和加载速度，同时也可以更好地管理和组织Vue项目中的代码和依赖项。

## 项目实践

下面我们进入项目实践环节，演练一下如何使用Webpack实现项目打包上线，这里我们需要重点关注Webpack打包的命令操作。

首先，你要把你本地的项目服务停掉。然后在项目根目录下，运行“npm run build”命令。

```plain
npm run build

```

这时候就能生成生产环境下的打包文件。这个命令会编译、压缩Vue项目，并将所有的代码和资源打包成一个或多个静态文件，用于在生产环境中运行。后面的截图展示的就是对应的执行过程。

![](https://static001.geekbang.org/resource/image/72/43/726cyy84decf4bf11eb90edd91aba843.jpg?wh=1585x733)

如果你看到这张图，就代表打包成功了。这时候，你会在你的项目目录下看到一个dist访问文件，其中包含了 Vue 项目的所有静态资源，如 HTML、CSS、JS、图片等。进行到这里，我们就成功完成了项目打包。

![](https://static001.geekbang.org/resource/image/bb/c0/bbb8a405b022d0a56a0ae28099e811c0.jpg?wh=1602x353)

接下来，我们需要将生成的打包文件dist上传到Web服务器，这里你可以使用FTP等工具。我推荐你使用 **FileZilla** 来完成这一步 **，** 它支持直接的拖拽式操作，对初学者比较友好。详细的下载说明，你可以直接参考 [FileZilla中文官网](https://www.filezilla.cn/)。

与此同时，我们还要在Web服务器上配置Nginx或Apache等服务器，这样才能将打包文件提供给用户访问。你可以根据自己的需求，配置Web服务器的虚拟主机、域名解析、SSL证书等，这个是非常灵活的，你自己选择就可以。

好，项目的打包上线工作大功告成，我们的视频平台可以支持更多的用户访问和使用了，恭喜你坚持到这里。

## 总结

今天的学习告一段落，我们一起来总结回顾一下本节课的内容。

善于使用Webpack能让Vue项目的开发更加便捷、高效。作为模块管理工具，它不但可以通过整合各种资源（如CSS、图片等），减少网页加载时的体积，还能将分散的代码打包成一个或多个模块从而减少网页加载时间。

Webpack的学习重点就是了解每一个配置项的作用，这样才能逐步强化我们的Webpack应用能力，更好地管理项目，也可应对一些项目优化问题。

在项目打包和配置发布上线环节，通过打包命令生成dist文件之后，你可以尝试放到自己的服务器上部署访问一下，看看效果。这个过程你一定要在课后实践一下，相信在完成之后你会收获满满。

到这里，我们完成了前端开发的全部内容。从下节课开始，我们的后端开发之旅即将开启，实现前后端联调的目标就在眼前，相信你已经迫不及待了，让我们继续前进。

## 思考题

在Webpack中，loader中test选项用于匹配需要被处理的文件。你知道它是通过什么样的方式进行文件类型匹配的吗？

欢迎你在留言区和我交流互动，如果这节课对你有帮助，也推荐你分享给身边的朋友。