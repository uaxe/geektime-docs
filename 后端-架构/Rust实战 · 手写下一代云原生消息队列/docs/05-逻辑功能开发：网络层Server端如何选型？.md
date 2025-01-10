> 本课程为精品小课，不标配音频

你好，我是文强。

前面我们完成了项目初始化和基础模块的开发，这节课我们正式进入逻辑功能部分的开发。我们第一个要做的就是网络 Server 模块。

开发网络 Server 模块的核心是： **从业务需求视角出发，分析 Server 应该具备哪些能力，从而根据这些信息选型出技术层面网络层和应用层的协议**。

前面我们讲到，第一阶段我们会完成消息队列中的 **“元数据服务”** **，** 那么接下来我们就来看一下这个元数据存储服务的网络 Server 怎么选型。

## 网络 Server 模块选型

先来看一下元数据服务（Placement Center）的架构图。

![图片](https://static001.geekbang.org/resource/image/5c/f9/5c5dd56a4d0f8673618a46d563f82ff9.png?wh=1139x641)

在前面的定义中，我们的元数据服务有两个功能：

1. **分布式的 KV 存储能力**：需要给 Broker 集群提供分布式的 KV 存储能力，从性能来看，需要支持较高并发的读写。

2. **集群管控和调度能力**: 根据运行信息对 Broker 集群进行管控、调度，比如元数据更新、Leader 切换等等。


所以从网络模块的角度来看，就需要能支持： **较高的吞吐和并发能力**。那协议怎么选择呢？

从技术上来看，很多开源组件会选择 **TCP + 自定义协议** 来完成网络 Server 的开发。我们最终选择的是 **基于 gRPC 协议来实现我们的 Server**。考虑如下：

1. gRPC 是标准的网络通讯框架，具备现成的 Server 端库和多语言 SDK。基于 gRPC 框架实现网络 Server 会极大地降低开发成本。

2. gRPC 协议底层是基于 HTTP2 和 Protobuf 来实现数据通信的，具备较高的吞吐性能。

3. 元数据服务是用来给 Broker 集群提供服务的，所以从业务特点上不会有非常高的数据量的吞吐。

4. 元数据服务是集群化部署，允许多节点快速横向部署扩容，不需要单机具备极高的性能。


另外作为一个元数据存储服务，它一般 **需要提供 HTTP 协议的接口来给管控页面或者用户做一些管理操作**。比如增删改查集群、用户、权限信息，查看集群运行的监控数据等等。所以我们还需要提供 HTTP 协议的 Server 来支持这类场景。

总结来看，我们的元数据服务需要提供 **基于 gRPC 协议的数据面 Server** 和 **基于 HTTP 协议的管控面 Server**。

接下来我们来看看如何基于 Axum 来实现 HTTP Server。

## 基于 Axum 支持 HTTP Server

在 Rust 中，Axum 是实践中选择最多的框架。教程很齐全，就不展开细讲各个技术细节了，需要的话你可以看 [《官方文档》](https://crates.io/crates/axum) 和 [《Demo 示例》](https://github.com/tokio-rs/axum/tree/main/examples)。 在 Demo 里面你几乎可以找到所有需要的用法。

从元数据服务的管控功能来看，我们需要提供 HTTP 协议的对资源的增删改查接口。所以我们的 HTTP Server 需要具备以下四个功能：

- 支持 Restful 规范的 HTTP 接口。

- 支持多版本接口的管理。

- 返回 JSON 格式的请求和返回。

- 支持在接口中处理各种业务逻辑，比如数据读写、缓存读取等。


这四个功能基本包含了我们对一个 HTTP Server 的基本诉求，接下来我们从主要代码来讲解一下实现的逻辑。

首先通过函数 start\_http\_server 来启动 HTTP Server。

```plain
pub async fn start_http_server(state: HttpServerState, stop_sx: broadcast::Sender<bool>) {
    # 读取配置
    let config = placement_center_conf();

    # 组装监听地址和端口
    let ip: SocketAddr = match format!("0.0.0.0:{}", config.http_port).parse() {
        Ok(data) => data,
        Err(e) => {
            panic!("{}", e);
        }
    };

    // 构建路由信息
    let app = routes(state);

    let mut stop_rx = stop_sx.subscribe();
        // 绑定端口，如果端口绑定失败，直接退出程序
        let listener = match tokio::net::TcpListener::bind(ip).await {
            Ok(data) => data,
            Err(e) => {
                panic!("{}", e);
            }
        };
        // 通过 select 来同时监听进程停止信号和 Server 运行
        select! {
            val = stop_rx.recv() =>{
                match val{
                    Ok(flag) => {
                        if flag {
                            info!("HTTP Server stopped successfully");
                            break;
                        }
                    }
                    Err(_) => {}
                }
            },
            // 监听服务
            val = axum::serve(listener, app.clone())=>{
                match val{
                    Ok(()) => {
                        // info!("HTTP Server started successfully, listening on port {}",config.http_port)
                    },
                    Err(e) => {
                        // HTTP 服务监听失败，直接退出程序
                        panic!("{}",e);
                    }
                }
            }
        }

}

```

上面的代码主要逻辑都在注释中，不再展开。我们主要关注select和panic这两个语法。

- 在 Rust 中 select 的功能是等待多个并发分支，如果有一个分支返回，则取消剩余分支。在上面的代码中，如果接收到停止进程的信号或者 HTTP Server 停止，则 select 就会返回。因此， **用 select 语法从功能上是为了能够正确处理进程停止信号**。select 相关详细资料可以参考 [《Tokio Select》](https://docs.rs/tokio/latest/tokio/macro.select.html)。

- panic 是退出进程的信号，当出现不可逆异常时，可以通过这个语法退出进程。


接下来，来看看定义路由的代码，这块属于 Axum Router 的官方语法的使用，细节可以参考这个文档 [《Axum Router》](https://docs.rs/axum/0.7.5/axum/struct.Router.html)。

```plain
#[derive(Clone)]
pub struct HttpServerState {
  mysql:DB
}

impl HttpServerState {
    pub fn new(mysql:DB) -> Self {
        return Self {mysql};
    }
}

fn routes(state: HttpServerState) -> Router {
    // 定义不同的http path 路径被哪个服务处理
    let common = Router::new()
        .route(&v1_path(&path_list(ROUTE_ROOT)), get(index))
        .route(&v1_path(&path_create(ROUTE_ROOT)), post(index))
        .route(&v1_path(&path_update(ROUTE_ROOT)), put(index))
        .route(&v1_path(&path_delete(ROUTE_ROOT)), delete(index));

    // 构建路由信息并返回，Axum的 merge 和 with_state 语法
    let app = Router::new().merge(common);
    return app.with_state(state);
}

// 业务处理逻辑 index 函数
pub async fn index(State(state): State<HttpServerState>) -> String {
    state.mysql.query("select * .....");
    return success_response("{}");
}

// 通过 serde_json 返回json 格式的数据。
pub fn success_response<T: Serialize>(data: T) -> String {
    let resp = Response {
        code: 0,
        data: data,
    };
    return serde_json::to_string(&resp).unwrap();
}

```

在上面的代码中，需要关注的有 HttpServerState、Route merge、success\_response 三个语法。

- HttpServerState **是一个我们自定义的数据结构，它是和 app.with\_state 结合起来用的，允许我们将自定义变量通过HttpServerState 传递给真正的业务逻辑**。比如 HttpServerState 包含了一个变量 MySQL，它是 MySQL driver。所以我们在上面的 index 函数中，就可以通过 state.mysql 来获取到 MySQL driver，执行 SQL 进行数据查询。因此如果有其他的全局变量都可以通过这个 state 来传递给各个 HTTP Server 处理。

- Route merge 是一个官方语法，主要功能是方便你管理多个 route，直接参考 [《Axum Router》](https://docs.rs/axum/0.7.5/axum/struct.Router.html) 即可。

- 在success\_response方法中，使用 serde\_json 将数据编码成 json 格式进行返回。


细心的同学会关注到类似 v1\_path 和 path\_get 两个函数。它是我们自定义的一个函数，用来实现 API 版本管理的。逻辑很简单，贴个代码你就懂了。

```plain
pub(crate) fn v1_path(path: &str) -> String {
    return format!("/v1{}", path);
}

pub(crate) fn path_get(path: &str) -> String {
    return format!("{}/get", path);
}

```

当完成上面的代码后，最后访问地址 [http://127.0.0.1:8971/v1/index/list](http://127.0.0.1:8971/v1/index/list)，效果如下：

![图片](https://static001.geekbang.org/resource/image/06/95/06c86fe3065407f4a174274e380dd895.png?wh=1543x458)

到了这里，我们就完成了满足上述 4 个需求的 HTTP Server 了，更多细节就需要你自己去扩展了。

接下来我们来实现基于 gRPC 协议的数据面 Server。

## 基于 Tonic 实现 gRPC Server

从技术上来看，Rust 中 gRPC 的实现是比较成熟的，有现成的框架可以用。从实践来看，我建议使用 [《Tonic 库》](https://github.com/hyperium/tonic) 来实现。我推荐两个 gRPC 代码示例库 [《Example1》](https://github.com/hyperium/tonic/tree/master/examples) 和 [《Example2》](https://github.com/hyperium/tonic/tree/master/interop)，这里面有各种场景的 gRPC 示例。

从编码角度来看，基于 Tonic 库实现 gRPC Server 主要包含五步：

1. 编写 protobuf 文件，即通过 protobuf 语法定义 RPC 的方法和参数

2. 编译 protobuf 文件

3. 在服务端，实现 RPC Service

4. 启动 gRPC Server

5. 运行测试用例


首先来编写元数据服务的 gRPC Server 的 protobuf 文件。我们知道它的一个重要功能就是 KV 型数据的存储，所以 gRPC Server 就得支持 KV 中 set/delete/get/exists 四个功能。

所以 Server 的 Protobuf 文件 placement\_center.proto，内容如下：

```plain
syntax = "proto3";
package kv;
import "common.proto";

service KvService {
  rpc set(SetRequest) returns(common.CommonReply){}
  rpc delete(DeleteRequest) returns(common.CommonReply){}
  rpc get(GetRequest) returns(GetReply){}
  rpc exists(ExistsRequest) returns(ExistsReply){}
}

message SetRequest{
    string key = 1;
    string value = 2;
}

message GetRequest{
    string key = 1;
}

message GetReply{
    string value = 1;
}

message DeleteRequest{
    string key = 1;
}

message ExistsRequest{
    string key = 1;
}

message ExistsReply{
    bool flag = 1;
}

```

上面的语法很简单，定义了 set、delete、get、exists 四个 RPC 方法，以及对应的request/reply 参数。我们使用的是 protobuf 3 的语法，关于 protobuf 3 的语法，你可以去看 [《protobuf 3 指南》](https://protobuf.dev/programming-guides/proto3/)。

接下来这一步是需要重点关注的： **proto 文件只是定义 RPC 的调用信息，如果要在Rust 使用这个 proto 文件，则需要将其编译成 .rs 文件。**

在 Rust 使用 protobuf，有两种方式。

1. 第一种方法：使用 tonic 库中的宏 tonic::include\_proto!，使用姿势如下：

```plain
pub mod placement_center_grpc {
    tonic::include_proto!("placement_center");
}

```

Rust 中宏的作用直观理解就是： **翻译/填充代码**。在上面的示例中，就是把placement\_center.rs 文件编译成 Rust 的代码，然后把生成的代码填充到 placement\_center\_grpc 的模块中。 **为了代码简洁，基于宏是主流推荐的用法**。

2. 第二种用法：手动使用 [《tonic\_build》](https://crates.io/search?q=tonic_build) 库将protobuf 代码编译成 Rust 代码。然后再正常 通过 use 使用编译完成的代码。为了让你能更加理解这个流程，我们的课程使用这种用法，下面是编译 protobuf 文件到 Rust 代码的代码示例。

```plain
fn build_pb() {
        tonic_build::configure()
            .build_server(true)
            // 指定生成的rust 存放的目录
            .out_dir("src/") // you can change the generated code's location
            .compile(
                &[
                  // 指定需要编译的 proto 文件
                  "src/kv.proto",
                  ],
                   // 指定在哪个目录寻找 .proto 文件
                &["src/"], // specify the root location to search proto dependencies
            )
            .unwrap();
    }

```

当执行完这个代码，就会自动在 src 目录下生成 kv.rs 的文件。如下所示：

![图片](https://static001.geekbang.org/resource/image/d4/d0/d47102f6ae5a4e084e619dc6d1512fd0.png?wh=530x262)

第二种方法相比第一种方法麻烦了许多，每次修改 proto 文件后都得手动编译一次。其实从底层来看，tonic::include\_proto 宏本质上也是使用 tonic\_build 编译的 proto 文件。只是通过 Rust 宏的特性，自动执行了这一步而已。这里需要注意的是，topic\_build 底层是调用 [《prost 库》](https://crates.io/crates/prost) 实现Protocol Buffers编译的。

接下来我们来实现 gRPC Server 端的 KV Server，也就是 RPC 中的方法。代码如下：

```plain
use protocol::kv::{
    kv_service_server::KvService, CommonReply, DeleteRequest, ExistsReply, ExistsRequest, GetReply,
    GetRequest, SetRequest,
};
use tonic::{Request, Response, Status};

// 定义GrpcBrokerServices结构体
pub struct GrpcBrokerServices {
    // 初始化一个基于 DashMap 库的 HashMap
    data: DashMap<String, String>,
}

impl GrpcBrokerServices {
    pub fn new() -> Self {
        return GrpcBrokerServices {
            data: DashMap::with_capacity(8),
        };
    }
}

// 在GrpcBrokerServices中实现 set/get/delete/exists 四个方法
// 当前实现是将数据保存在内存中的
#[tonic::async_trait]
impl KvService for GrpcBrokerServices {
    async fn set(&self, request: Request<SetRequest>) -> Result<Response<CommonReply>, Status> {
        let req = request.into_inner();
        self.data.insert(req.key, req.value);
        return Ok(Response::new(CommonReply::default()));
    }

    async fn get(&self, request: Request<GetRequest>) -> Result<Response<GetReply>, Status> {
        let req = request.into_inner();
        if let Some(data) = self.data.get(&req.key) {
            return Ok(Response::new(GetReply {
                value: data.value().clone(),
            }));
        }
        return Ok(Response::new(GetReply::default()));
    }

    async fn delete(
        &self,
        request: Request<DeleteRequest>,
    ) -> Result<Response<CommonReply>, Status> {
        let req = request.into_inner();
        self.data.remove(&req.key);
        return Ok(Response::new(CommonReply::default()));
    }

    async fn exists(
        &self,
        request: Request<ExistsRequest>,
    ) -> Result<Response<ExistsReply>, Status> {
        let req = request.into_inner();
        return Ok(Response::new(ExistsReply {
            flag: self.data.contains_key(&req.key),
        }));
    }
}

```

上面的代码比较简单，基于 Tonic 的规范，实现了我们在 proto 文件中定义的 set/get/delete/exists 方法。细节比较简单，就不赘述了。

接着来启动 gRPC Server。

```plain
pub async fn start_grpc_server(stop_sx: broadcast::Sender<bool>) {
    let config = placement_center_conf();
    let server = GrpcServer::new(config.grpc_port);
    server.start(stop_sx).await;
}

pub struct GrpcServer {
    port: usize,
}

impl GrpcServer {
    pub fn new(port: usize) -> Self {
        return Self { port };
    }
    pub async fn start(&self, stop_sx: broadcast::Sender<bool>) {
        let addr = format!("0.0.0.0:{}", self.port).parse().unwrap();
        info!("Broker Grpc Server start. port:{}", self.port);
        let service_handler = GrpcBrokerServices::new();
        let mut stop_rx = stop_sx.subscribe();
        select! {
            val = stop_rx.recv() =>{
                match val{
                    Ok(flag) => {
                        if flag {
                            info!("HTTP Server stopped successfully");

                        }
                    }
                    Err(_) => {}
                }
            },
            val =  Server::builder().add_service(KvServiceServer::new(service_handler)).serve(addr)=>{
                match val{
                    Ok(()) => {
                    },
                    Err(e) => {
                        panic!("{}",e);
                    }
                }
            }
        }
    }
}

```

启动 Server 和上面启动 HTTP Server 差不多，核心是这行代码：

> Server::builder().add\_service(KvServiceServer::new(service\_handler)).serve(addr)

即通过 Tonic 启动 gRPC Server，并增加 GrpcBrokerServices 处理逻辑。最后我们可以来写一个测试用例来测试 KV Server 是否运行正常。

```plain
 #[tokio::test]
    async fn kv_test() {
        let mut client = KvServiceClient::connect("http://127.0.0.1:8871")
            .await
            .unwrap();
        let key = "mq".to_string();
        let value = "robustmq".to_string();
        let request = tonic::Request::new(SetRequest {
            key: key.clone(),
            value: value.clone(),
        });

        let _ = client.set(request).await.unwrap();

        let request = tonic::Request::new(ExistsRequest { key: key.clone() });
        let exist_reply = client.exists(request).await.unwrap().into_inner();
        assert!(exist_reply.flag);

        let request = tonic::Request::new(GetRequest { key: key.clone() });
        let get_reply = client.get(request).await.unwrap().into_inner();
        assert_eq!(get_reply.value, value);

        let request = tonic::Request::new(DeleteRequest { key: key.clone() });
        let _ = client.delete(request).await.unwrap().into_inner();

        let request = tonic::Request::new(ExistsRequest { key: key.clone() });
        let exist_reply = client.exists(request).await.unwrap().into_inner();
        assert!(!exist_reply.flag);
    }

```

至此，我们的 gRPC Server 的框架就基本搭建完成了。接下来就是按照上面的流程去添加自己的服务就可以了。

需要注意的是，上面的代码只是最基本的 gRPC Server 的实现，在Rust gRPC Server 中，还有比如 **负载均衡、TLS、鉴权、拦截器、压缩** 等高级功能。这块就不展开讲了，直接看官网文档 [《Tonic 库》](https://github.com/hyperium/tonic) 即可。

细心的同学可能会关注到上面的代码有变量 stop\_sx: broadcast::Sender，那它是起什么作用的呢？

broadcast::Sender 是 Tokio 提供的 Channel，用于在多个Task之间通信，详细资料可以看 [《Tokio Channel》](https://rust-book.junmajinlong.com/ch100/05_task_communication.html)。可以看到 stop\_sx 是 Tokio 中的 broadcast 类型，broadcast 是一种广播通道，可以有多个Sender端以及多个Receiver端，任何一个Sender发送的每一条数据都能被所有的Receiver端看到。所以我们通过 broadcast Channel 来接收进程停止信号，并分发给所有的broadcast Receiver，从而达到优雅停止所有线程的目的。

## Tokio 并行运行多个服务

先来看一段代码，你能从下面这段代码中看出什么问题吗？

```plain
pub async fn start_server(stop_sx: broadcast::Sender<bool>) {
    let state = HttpServerState::new();
    start_http_server(state, stop_sx.clone()).await;
    start_grpc_server(stop_sx.clone()).await;
}

```

上面代码的问题是： **运行到** **start\_http\_server** **函数会卡** **住，** **start\_grpc\_server** **是运行不到的**。因为启动 HTTP Server 的代码和启动 gRPC Server 的代码都是卡住的。

那怎么处理呢? 来看下面的代码。

```plain
pub async fn start_server(stop_sx: broadcast::Sender<bool>) {

    // 将 grpc server 运行在一个独立的 tokio task 中。
    let raw_stop_sx = stop_sx.clone();
    tokio::spawn(async move {
        start_grpc_server(raw_stop_sx).await;
    });

    // 将 http server 运行在一个独立的 tokio task 中。
    let raw_stop_sx = stop_sx.clone();
    tokio::spawn(async move {
        let state = HttpServerState::new();
        start_http_server(state, raw_stop_sx).await;
    });

    // 等待进程信号
    awaiting_stop(stop_sx.clone()).await;
}

pub async fn awaiting_stop(stop_send: broadcast::Sender<bool>) {
    // 等待接收 ctrl c 停止线程的信号。
    signal::ctrl_c().await.expect("failed to listen for event");
    // 当接手到 ctrl c 信号时，给http server 和 grpc server 线程发送停止信号
    match stop_send.send(true) {
        Ok(_) => {
            info!(
                "{}",
                "When ctrl + c is received, the service starts to stop"
            );
            // 在这里允许执行相关回收逻辑。
        }
        Err(e) => {
            panic!("{}", e);
        }
    }
}

```

这里有两个重点：

1. 将 HTTP Server 和 gRPC Server 通过 tokio::spawn 异步运行在一个独立的 tokio task 中，让它不阻塞主进程。

2. 依赖 signal::ctrl\_c() 来阻塞主进程，让主进程不退出，并且等待接收 ctrl + c 信号，当接收到信号时，就执行相关回收逻辑。


服务成功启动后，当我们按 ctrl+c，服务接收到信号，发送停止信号给多个运行线程，停止HTTP 和 gRPC 服务。效果如下：

![图片](https://static001.geekbang.org/resource/image/7b/eb/7b64b92853fc1ed60dc39ec5f246bceb.png?wh=1920x350)

## 总结

> tips：每节课的代码都能在项目 [https://github.com/robustmq/robustmq-geek](https://github.com/robustmq/robustmq-geek) 中找到源码，有兴趣的同学可以下载源码来看。

这节课我们首先讲了我们的元数据服务需要什么类型的 Server，这一步是很重要的， **要根据我们的需求和场景选择合适的 Server**。可以参考我们前面的选择思考逻辑。

接下来我们讲了HTTP Server 和 gRPC Server 的实现要点以及主体框架的开发。这里总结下主要依赖的库：

- Tokio：Rust 异步运行的标准库。

- Axum：Rust 语言的 HTTP Web 框架。

- Tonic：Rust 语言的 gRPC 框架的实现。

- Prost：Protocol Buffers 的 Rust 语言的实现，Tonic 及其相关库（tonic\_build）关于 Proto 部分都是用这个库。


最后我们讲了基于 tokio spawn、tokio signal、tokioc broadcast channel 来实现 **并行运行多个服务** 和 **程序平滑退出** 的能力。

另外，这节课我们只是讲了上面几个库的基本主体功能，课下还需要你深入去研究这几个库的文档，才能在实战中更好地使用它们。

## 思考题

这里是本节课推荐的相关 issue 的任务列表，请点击查看 [《Good First Issue》](http://www.robustmq.com/docs/robustmq-tutorial-cn/%e8%b4%a1%e7%8c%ae%e6%8c%87%e5%8d%97/good-first-issue/)，任务列表会不间断地更新。欢迎给我的项目 [https://github.com/robustmq/robustmq](https://github.com/robustmq/robustmq) 点个 Star 啊！