你好，我是Mike, 今天我们来讲一讲如何用Axum框架进行Web服务器后端开发。

关于Rust是否适合做Web后端开发，很多人持怀疑态度。认为Web开发讲究的是敏捷，一种动态的、带运行时的、方便修改的语言可能更适合Web开发。

但有一些因素，其实决定了Rust非常适合Web开发。

1. 时代变化：芯片摩尔定律已失效，服务器成本逐渐占据相当大的比例，无脑堆服务器的时代已经过去。当前阶段，对于规模稍微大一些的公司来说，降本增效是一个很重要的任务。而Rust的高性能和稳定可靠的表现非常适合帮助公司节省服务器成本。
2. 随着业务的成型，一些核心业务会趋于稳定，模型和流程抽象已经基本不会有大的改动。这时，使用Rust重写或部分重写这些业务，会带来更强的性能和更可靠稳定的服务表现。
3. Rust非常适合用来做一些通用的中间件服务，目前开源社区已经出现了一些相当优秀的中间件产品。
4. Rust的表达能力其实非常强，其强大的类型系统可帮助开发者轻松地对问题进行建模。一个中等熟练的Rust开发者做原型的速度不会比Python慢多少，在复杂问题场景下，甚至更快。
5. Rust的语言层面的设计使它特别适合做重构。重构Rust工程特别快，重构完后，也不用担心出错的问题。相对于动态语言，对应的测试用例都可以少准备很多。

## Rust Web Backend 生态

Rust Web后端开发生态目前处于一种欣欣向荣的局面。就Web开发框架来说，能叫得上名字的就有十几种，其中按 [crates.io](https://crates.io) 最新下载量排名，排列靠前的是这几位。

1. Axum
2. Actix-web
3. Rocket
4. Poem
5. Rouille
6. Salvo

从最近下载的绝对数量来说，Axum 的下载量是第二名 Actix-web 的 3 倍多。因此，我们选择了下载量最多的框架——Axum。

### Tokio技术栈介绍

Axum有这么强劲的表现，得益于其本身优秀的设计，还有它无缝依赖的 Tokio 技术栈。Tokio从 2017 年发布 0.1 版本开始到现在，已经形成一套强大的技术栈。

![](https://static001.geekbang.org/resource/image/e1/40/e1e84b20997c3a99540c7559e6dc5b40.jpg?wh=1414x1594)

这些可靠的工具链，为Rust在服务器端的发展打下了坚实的基础，越来越多的项目开始采用这一套技术栈。

## Axum框架

> Axum是一个专注于人体工程学和模块化的Web开发框架。——官方文档的Slogan

从上层视角来看，Axum具有以下特性：

1. 写Router和Handler的时候，不需要使用宏（非标注风格）。
2. 使用解包器进行声明式的请求解析。
3. 简单和可预测的错误处理模型。
4. 生成响应时只需用到最小的样板代码。
5. 充分利用 tower 和 tower-http 的中间件、服务和工具的生态系统。

特别是最后一点，让Axum显著不同于其他框架。Axum自己不带中间件系统，而是使用 tower 系的中间件。这样就能和生态里的其他项目，如 hyper 或 tonic 共享中间件系统。 这种设计太棒了。

### Tower中间层服务

Tower是一个模块化、可重用的组件系统，用于构建稳健的网络服务端和客户端应用。它对 **请求/响应模型** 做了一个统一的服务抽象，和具体的实现协议无关。你可以看一下Service的定义。

```plain
async fn(Request) -> Result<Response, Error>

```

Tower包含 Service 和 Layer 两个抽象。一个Service是一个接受请求，做出响应的异步函数；而一个 Layer 接受一个Service，处理并返回另一个Service。Service和Layer一起，就可以方便地构建中间件服务。而完全基于流（stream）的服务，并不适合使用Tower。

### Tower-http介绍

[Tower-http](https://docs.rs/tower-http/latest/tower_http/) 是一个专门用于提供HTTP相关的中间件和设施的库，里面罗列了二十多个中间件。

在Axum中，最常用的中间件是下面这几个。

- TracyLayer 中间件，用于提供高层日志或跟踪。
- CorsLayer 中间件，用于处理CORS。
- CompressionLayer 中间件，用于自动压缩响应。
- RequestIdLayer 和 PropagateRequestIdLayer 中间件，用于设置和传播请求ID。
- TimeoutLayer 中间件，用于设置超时。
- HandleErrorLayer 中间件，用于转换各种错误类型到响应。

而每个中间件都可以用在全局Router、模块Router和Handler三个层次。

### Router

Router用来定义URL到handler的映射，并用来构建模块化URL的层级，既能支持全局性路由，也能支持模块层级的路由。比如：

```rust
let user_routes = Router::new().route("/:id", get(|| async {}));
let team_routes = Router::new().route("/", post(|| async {}));
let api_routes = Router::new()
    .nest("/users", user_routes)
    .nest("/teams", team_routes);
let app = Router::new().nest("/api", api_routes);

```

### Handler

在Axum里，Handler是一个异步函数，这个异步函数接受一个或多个解包器作为参数，返回一个可以转换为响应（impl IntoResponse）的类型。

最简单的 handler 类似下面这个样子：

```plain
async fn string_handler() -> String {
    "Hello, World!".to_string()
}

```

## 使用Axum进行Web后端开发

现在话不多说，让我们开始Axum实战环节吧！

注：目前（2023年12月）Axum的最新版本是 v0.7 版，我们下面会基于这个版本来编写代码。

### 第一步：Hello world

我们先来看看Axum的Hello World是什么样子。

```plain
use axum::{response::Html, routing::get, Router};

#[tokio::main]
async fn main() {
    // build our application with a route
    let app = Router::new().route("/", get(handler));

    // run it
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .unwrap();
    println!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}

async fn handler() -> Html<&'static str> {
    Html("<h1>Hello, World!</h1>")
}

```

这里我给出这个步骤的 [原始代码地址](https://github.com/miketang84/jikeshijian/tree/master/2122-axumapp_stepbystep/axumapp01_helloworld)，你可以直接下载到本地运行。

从这个例子里，我们可以一窥Axum应用的基本结构。首先，一个Axum应用其实就是一个Tokio应用，以标志性的tokio::main属性宏开头。

```plain
#[tokio::main]
async fn main() {

```

然后，创建一个Router实例，代表App。在Router中，绑定URL与handler。

然后使用 `tokio::net::TcpListener::bind()` 监听服务器地址，并将生成的 listener 传入 `axum::serve()` 中使用，启动axum服务。而这个应用的 handler 参数里没有解包器（extractor），是因为我们暂时不解析请求参数，所以参数部分留空。

```plain
async fn handler() -> Html<&'static str> {
    Html("<h1>Hello, World!</h1>")
}

```

然后，这个handler的返回值是 `Html<&'static str>` 类型，它已经实现了 IntoResponse，所以可以作为 Response 返回类型。下面我们来测试，打开终端在代码目录下执行 `cargo run`。终端下输出 `listening on 127.0.0.1:3000`。

打开浏览器，输入 `127.0.0.1:3000`，可以看到下面这样的页面效果。

![图片](https://static001.geekbang.org/resource/image/d7/cb/d757695525f1fd973f4532bf7475fdcb.png?wh=1920x499)

### 第二步：实现静态文件服务

静态文件服务非常有用，用于对服务器上的静态资源如图片、HTML、JS、CSS等文件提供服务。下面我们来看看如何使用Axum实现一个简单的静态文件服务。我们只需要引入ServeDir服务，然后在Router实例上使用 nest\_service 挂载这个服务就可以了。

```rust
    Router::new().nest_service("/assets", ServeDir::new("assets"))

```

`ServeDir::new()` 的参数是资源目录的路径，上面一句表示把 `/assets/*` 的URL映射到 assets 目录下的哪些文件。

而如果需要配置获取默认文件，可以按照下面这样，在ServeDir里配置not\_found\_service，传一个ServeFile实例进去，这个ServeFile实例就是默认获取的那个文件。然后在Router实例配置时，添加一个 fallback\_service 挂载 serve\_dir。

```rust
let serve_dir =
    ServeDir::new("assets2")
    .not_found_service(ServeFile::new("assets2/index.html"));
let app = Router::new()
    .route("/foo", get(handler))
    .nest_service("/assets", ServeDir::new("assets"))
    .nest_service("/assets2", serve_dir.clone())
    .fallback_service(serve_dir);

```

上述示例里，即使我们访问一些不存在的URL地址，服务器也会返回assets2目录下的index.html文件。这通常正是我们想要的。你可以根据 [示例源码](https://github.com/miketang84/jikeshijian/tree/master/2122-axumapp_stepbystep/axumapp02_staticfile) 自行测试，查看效果。

你可以尝试如下URL地址：

```
http://127.0.0.1:3000/
http://127.0.0.1:3000/foo
http://127.0.0.1:3000/bar
http://127.0.0.1:3000/assets/index.html
http://127.0.0.1:3000/assets/ferris.png
http://127.0.0.1:3000/assets/script.js
http://127.0.0.1:3000/assets2/index.html
http://127.0.0.1:3000/assets2/ferris2.png
http://127.0.0.1:3000/assets2/script.js
...

```

### 第三步：加入日志记录

日志系统是一个服务必不可少的组件，我们一起来看看如何为Axum应用添加日志。在Axum中添加日志很简单。第一步，我们需要添加 tracing 和 tracing-subscriber 两个crates。

```rust
cargo add tracing
cargo add tracing-subscriber

```

然后引入TraceLayer。

```rust
use tower_http::trace::TraceLayer;

```

在main函数的开头添加代码：

```rust
    tracing_subscriber::fmt::init();

```

再在Router配置的时候，添加下面这行代码配置日志中间件服务就可以了。

```rust
let app = Router::new()
    .route("/foo", get(handler))
    .nest_service("/assets", serve_dir.clone())
    .fallback_service(serve_dir)
    .layer(TraceLayer::new_for_http());  // 添加这行

```

使用时，需要按照下面这个方式来使用。

```rust
tracing::debug!("listening on {}", addr);

```

我们用上面一句替代了之前的 `println!`，在一个正经一点的应用中，我们都不会使用 `println!` 去打印日志的。

这里需要补充一点知识：Rust中的日志标准。Rust标准的log协议在 [链接](https://docs.rs/log/latest/log/) 里。这个crate中定义了5个级别的日志打印语句。

- `error!`
- `warn!`
- `info!`
- `debug!`
- `trace!`

这5个级别从上到下警示程度为由高到低。也就是说，越往下会越详细。

但是这只是一套协议的定义，而不是具体实现。具体使用的时候，需要用另外的crate来实现。我们常用的 env\_logger 就是其中一种实现，它把日志输出到标准终端里，用环境变量来控制打印的级别开关。而这里我们使用的 tracing 库也是这样一种实现。它是为tokio异步运行时专门设计的，适合在异步并发代码中使用。

你可以使用RUST\_LOG来打开日志开关。比如：

```rust
RUST_LOG=trace cargo run

```

访问 [http://127.0.0.1:3000/foo](http://127.0.0.1:3000/foo) ，可以看到，TRACE级别的和DEBUG级别的日志都打印出来了。

```rust
2023-12-11T05:36:39.240674Z TRACE mio::poll: registering event source with poller: token=Token(0), interests=READABLE | WRITABLE
2023-12-11T05:36:39.240718Z DEBUG axumapp03: listening on 127.0.0.1:3000
2023-12-11T05:36:50.029388Z TRACE mio::poll: registering event source with poller: token=Token(1), interests=READABLE | WRITABLE
2023-12-11T05:36:50.029678Z TRACE mio::poll: registering event source with poller: token=Token(2), interests=READABLE | WRITABLE
2023-12-11T05:36:50.030011Z DEBUG request{method=GET uri=/foo version=HTTP/1.1}: tower_http::trace::on_request: started processing request
2023-12-11T05:36:50.030127Z DEBUG request{method=GET uri=/foo version=HTTP/1.1}: tower_http::trace::on_response: finished processing request
 latency=0 ms status=200

```

用debug模式日志会少一些。

```rust
RUST_LOG=debug cargo run

```

访问 [http://127.0.0.1:3000/foo](http://127.0.0.1:3000/foo) ， 输出：

```rust
2023-12-11T05:43:45.223551Z DEBUG axumapp03: listening on 127.0.0.1:3000
2023-12-11T05:43:50.558174Z DEBUG request{method=GET uri=/foo version=HTTP/1.1}: tower_http::trace::on_request: started processing request
2023-12-11T05:43:50.558303Z DEBUG request{method=GET uri=/foo version=HTTP/1.1}: tower_http::trace::on_response: finished processing request
 latency=0 ms status=200

```

我们还可以指定只打印某些crate里的日志。

```rust
RUST_LOG=tower_http=debug,axumapp03=debug cargo run

```

访问 [http://127.0.0.1:3000/foo](http://127.0.0.1:3000/foo) ，输出：

```rust
2023-12-11T05:45:03.578294Z DEBUG axumapp03: listening on 127.0.0.1:3000
2023-12-11T05:45:08.036568Z DEBUG request{method=GET uri=/foo version=HTTP/1.1}: tower_http::trace::on_request: started processing request
2023-12-11T05:45:08.036696Z DEBUG request{method=GET uri=/foo version=HTTP/1.1}: tower_http::trace::on_response: finished processing request
 latency=0 ms status=200

```

你可以下载 [源码](https://github.com/miketang84/jikeshijian/tree/master/2122-axumapp_stepbystep/axumapp03_addlog) 自行测试查看效果。

### 第四步：解析 Get 请求参数

一般一个URL是这样的：

```
https://rustcc.cn/article?id=8ba98036-e2fb-41cf-9dad-7cd874c397c4

```

最后面一段是 query，query 的格式为键值对列表，比如 `x1=yyy&x2=zzz` ，键值对之间使用 & 符号隔开。

Axum采用一种解包器（extractor）的方式，直接从HTTP Request里提取出开发者关心的参数信息。这种设计有一些好处：

1. 减少样板重复代码，可以让代码更紧凑易读。
2. 类型化，充分利用Rust强大的类型能力。
3. 配置式开发，轻松惬意。

下面我们先来看如何从GET请求的URL中，取出Query参数。

在 Axum中，我们只需要在Handler中这样配置解包器就可以。

```plain
#[derive(Debug, Deserialize)]
struct InputParams {
    foo: i32,
    bar: String,
    third: Option<i32>,
}

async fn query(Query(params): Query<InputParams>) -> impl IntoResponse {
    tracing::debug!("query params {:?}", params);
    Html("<h3>Test query</h3>")
}

```

这里这个 params 参数就是我们想要的query请求参数。可以看到，Axum框架自动帮我们处理了解析工作，让我们直接得到了Rust 结构体对象。减轻了我们处理具体协议的繁琐度，不易出错。请注意示例第8行的参数中使用了模式匹配，你可以回顾一下 [第 6 讲](https://time.geekbang.org/column/article/720999) 的模式匹配相关知识点。

我们可以继续折腾一下，InputParams里定义了一个third字段，它是 `Option<i32>` 类型，请你尝试在浏览器URL地址栏或插件中变换请求参数，查看及日志输出返回情况。可能的参数组合有下面这几种。

```
http://127.0.0.1:3000/query?foo=1&bar=2&third=3
http://127.0.0.1:3000/query?foo=1&bar=2
http://127.0.0.1:3000/query?foo=1
http://127.0.0.1:3000/query?bar=2
http://127.0.0.1:3000/query?foo=1&bar=2&third=3&another=4

```

本示例完整代码在 [这里](https://github.com/miketang84/jikeshijian/tree/master/2122-axumapp_stepbystep/axumapp04_query)。

## 小结

通过这节课的展示，你有没有体会到使用Rust进行Web开发的感觉？其实跟那些动态语言如Python、JavaScript等开发Web没太大区别，Axum的代码也是比较精练的。请你一定要参考我给出的代码示例，对照源代码在你的本地跑起来。Web开发一个非常方便的地方就是方便测试，易于看到渐进的效果正反馈，所以动手是非常重要而且高效的。

相比于动态语言来讲，Rust的强类型更加能够保证Web后端服务的正确性和可靠性。性能自不用说，你选择了Rust，就是选择了高起点。

同时你可以看到，这节课出现的Axum示例代码，一点都不复杂，甚至都没有用到Rust的所谓各种高级特性。其实就是这样，你用Rust做日常开发，特别是业务开发，根本不难，不要被那些所谓的高级特性吓到，先用现成的框架，快速捣鼓出自己的东西，后面再慢慢上难度就好了。

## 思考题

请你说一说Request/Response 模型是什么，Axum框架和其他gRPC框架（比如Tonic）有什么区别。欢迎你把自己的思考分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！