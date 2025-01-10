你好，我是Chrono。

在上一节课，我讲了JSON、MessagePack和ProtoBuffer这三种数据交换格式。现在，我们手里有了这些跨语言、跨平台的通用数据，该怎么与外部通信交换呢？

你肯定首先想到的就是Socket网络编程，使用TCP/IP协议栈收发数据，这样不仅可以在本地的进程间通信，也可以在主机、机房之间异地通信。

大方向上这是没错的，但你也肯定知道，原生的Socket API非常底层，要考虑很多细节，比如TIME\_WAIT、CLOSE\_WAIT、REUSEADDR等，如果再加上异步就更复杂了。

虽然你可能看过、学过不少这方面的资料，对如何处理这些问题“胸有成竹”，但无论如何，像Socket建连/断连、协议格式解析、网络参数调整等，都要自己动手做，想要“凭空”写出一个健壮可靠的网络应用程序还是相当麻烦的。

所以，今天我就来谈谈C++里的几个好用的网络通信库：libcurl、cpr和ZMQ，让你摆脱使用原生Socket编程的烦恼。

## libcurl：高可移植、功能丰富的通信库

第一个要说的库是libcurl，它来源于著名的 [curl项目](https://curl.haxx.se/)，也是curl的底层核心。

libcurl经过了多年的开发和实际项目的验证，非常稳定可靠，拥有上百万的用户，其中不乏Apple、Facebook、Google、Netflix等大公司。

它最早只支持HTTP协议，但现在已经扩展到支持所有的应用层协议，比如HTTPS、FTP、LDAP、SMTP等，功能强大。

libcurl使用纯C语言开发，兼容性、可移植性非常好，基于C接口可以很容易写出各种语言的封装，所以Python、PHP等语言都有libcurl相关的库。

因为C++兼容C，所以我们也可以在C++程序里直接调用libcurl来收发数据。

在使用libcurl之前，你需要用apt-get或者yum等工具安装开发库：

```
apt-get install libcurl4-openssl-dev

```

虽然libcurl支持很多协议，但最常用的还是HTTP。所以接下来，我也主要介绍libcurl的HTTP使用方法，这样对其他的协议你也可以做到“触类旁通”。

libcurl的接口可以粗略地分成两大类：easy系列和multi系列。其中，easy系列是同步调用，比较简单；multi系列是异步的多线程调用，比较复杂。通常情况下，我们用easy系列就足够了。

使用libcurl收发HTTP数据的基本步骤有4个：

1. 使用curl\_easy\_init()创建一个句柄，类型是CURL\*。但我们完全没有必要关心句柄的类型，直接用auto推导就行。
2. 使用curl\_easy\_setopt()设置请求的各种参数，比如请求方法、URL、header/body数据、超时、回调函数等。这是最关键的操作。
3. 使用curl\_easy\_perform()发送数据，返回的数据会由回调函数处理。
4. 使用curl\_easy\_cleanup()清理句柄相关的资源，结束会话。

下面我用个简短的例子来示范一下这4步：

```
#include <curl/curl.h>               // 包含头文件

auto curl = curl_easy_init();        // 创建CURL句柄
assert(curl);

curl_easy_setopt(curl, CURLOPT_URL, "http://nginx.org"); // 设置请求URI

auto res = curl_easy_perform(curl);   // 发送数据
if (res != CURLE_OK) {                // 检查是否执行成功
    cout << curl_easy_strerror(res) << endl;
}

curl_easy_cleanup(curl);             // 清理句柄相关的资源

```

这段代码非常简单，重点是调用curl\_easy\_setopt()设置了URL，请求Nginx官网的首页，其他的都使用默认值即可。

由于没有设置你自己的回调函数，所以libcurl会使用内部的默认回调，把得到的HTTP响应数据输出到标准流，也就是直接打印到屏幕上。

这个处理结果显然不是我们所期待的，所以如果想要自己处理返回的HTTP报文，就得写一个回调函数，在里面实现业务逻辑。

因为libcurl是C语言实现的，所以回调函数必须是函数指针。不过，C++11允许你写lambda表达式，这利用了一个特别规定： **无捕获的lambda表达式可以显式转换成一个函数指针**。注意一定要是“无捕获”，也就是说lambda引出符“\[\]”必须是空的，不能捕获任何外部变量。

所以，只要多做一个简单的转型动作，你就可以用lambda表达式直接写libcurl的回调，还是熟悉的函数式编程风格：

```
// 回调函数的原型
size_t write_callback(char* , size_t , size_t , void* );

curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION,        // 设置回调函数
  (decltype(&write_callback))      // decltype获取函数指针类型，显式转换
  [](char *ptr, size_t size, size_t nmemb, void *userdata)// lambda
  {
      cout << "size = " << size * nmemb << endl;   // 简单的处理
      return size * nmemb;                // 返回接收的字节数
  }
);

```

libcurl的用法大概就是这个样子了，开头的准备和结尾的清理工作都很简单，关键的就是curl\_easy\_setopt()这一步的参数设置。我们必须通过查文档知道该用哪些标志宏，写一些单调重复的代码。

你可能想到了，可以自己用C++包装出一个类，就能够少敲点键盘。但不要着急，因为我们有一个更好的选择，就是cpr。

## cpr：更现代、更易用的通信库

cpr是对libcurl的一个C++11封装，使用了很多现代C++的高级特性，对外的接口模仿了Python的requests库，非常简单易用。

你可以从 [GitHub](https://github.com/whoshuu/cpr) 上获取cpr的源码，再用cmake编译安装：

```
git clone git@github.com:whoshuu/cpr.git
cmake . -DUSE_SYSTEM_CURL=ON -DBUILD_CPR_TESTS=OFF
make && make install

```

和libcurl相比，cpr用起来真的是太轻松了，不需要考虑什么初始化、设置参数、清理等杂事，一句话就能发送HTTP请求：

```
#include <cpr/cpr.h>                            // 包含头文件

auto res = cpr::Get(                           // GET请求
           cpr::Url{"http://openresty.org"}   // 传递URL
);

```

你也不用写回调函数，HTTP响应就是函数的返回值，用成员变量url、header、status\_code、text就能够得到报文的各个组成部分：

```
cout << res.elapsed << endl;            // 请求耗费的时间

cout << res.url << endl;               // 请求的URL
cout << res.status_code << endl;       // 响应的状态码
cout << res.text.length() << endl;     // 响应的body数据

for(auto& x : res.header) {            // 响应的头字段
    cout << x.first << "=>"            // 类似map的结构
         << x.second << endl;
}

```

在cpr里，HTTP协议的概念都被实现为相应的函数或者类，内部再转化为libcurl操作，主要的有：

- GET/HEAD/POST等请求方法，使用同名的Get/Head/Post函数；
- URL使用Url类，它其实是string的别名；
- URL参数使用Parameters类，KV结构，近似map；
- 请求头字段使用Header类，它其实是map的别名，使用定制的函数实现了大小写无关比较；
- Cookie使用Cookies类，也是KV结构，近似map；
- 请求体使用Body类；
- 超时设置使用Timeout类。

这些函数和类的用法都非常自然、符合思维习惯，而且因为可以使用C++11的花括号“{}”初始化语法，如果你以前用过Python reqeusts库的话一定会感到很亲切：

```
const auto url = "http://openresty.org"s;  // 访问的URL

auto res1 = cpr::Head(                    // 发送HEAD请求
            cpr::Url{url}                 // 传递URL
);

auto res2 = cpr::Get(                     // 发送GET请求
            cpr::Url{url},               // 传递URL
            cpr::Parameters{             // 传递URL参数
                {"a", "1"}, {"b", "2"}}
);

auto res3 = cpr::Post(                  // 发送POST请求
            cpr::Url{url},             // 传递URL
            cpr::Header{                // 定制请求头字段
              {"x", "xxx"},{"expect",""}},
            cpr::Body{"post data"},    // 传递body数据
            cpr::Timeout{200ms}       // 超时时间
);

```

cpr也支持异步处理，但它内部没有使用libcurl的multi接口，而是使用了标准库里的future和async（参见 [第14讲](https://time.geekbang.org/column/article/245259)），和libcurl的实现相比，既简单又好理解。

异步接口与同步接口的调用方式基本一样，只是名字多了个“Async”的后缀，返回的是一个future对象。你可以调用wait()或者get()来获取响应结果：

```
auto f = cpr::GetAsync(                    // 异步发送GET请求
            cpr::Url{"http://openresty.org"}
);

auto res = f.get();                       // 等待响应结果
cout << res.elapsed << endl;              // 请求耗费的时间

```

看了上面这些介绍，你是不是有些心动了。说实话，我原来在C++里也是一直用libcurl，也写过自己的包装类，直到发现了cpr这个“大杀器”，就立即“弃暗投明”了。

相信有了cpr，你今后在C++里写HTTP应用就不再是痛苦，而是一种享受了。

## ZMQ：高效、快速、多功能的通信库

libcurl和cpr处理的都是HTTP协议，虽然用起来很方便，但协议自身也有一些限制，比如必须要一来一回，必须点对点直连，在超大数据量通信的时候就不是太合适。

还有一点，libcurl和cpr只能充当HTTP的客户端，如果你想写服务器端程序，这两个工具就完全派不上用场。

所以，我们就需要一个更底层、更灵活的网络通信工具，它应该能够弥补libcurl和cpr的不足，不仅快速高效，还能同时支持客户端和服务器端编程。

这就是我要说的第三个库： [ZMQ](https://zeromq.org/)。

其实，ZMQ不仅是一个单纯的网络通信库，更像是一个高级的异步并发框架。

从名字上就可以看出来，Zero Message Queue——零延迟的消息队列，意味着它除了可以收发数据外，还可以用作消息中间件，解耦多个应用服务之间的强依赖关系，搭建高效、有弹性的分布式系统，从而超越原生的Socket。

作为消息队列，ZMQ的另一大特点是零配置零维护零成本，不需要搭建额外的代理服务器，只要安装了开发库就能够直接使用，相当于把消息队列功能直接嵌入到你的应用程序里：

```
apt-get install libzmq3-dev

```

ZMQ是用C++开发的，但出于兼容的考虑，对外提供的是纯C接口。不过它也有很多C++封装，这里我选择的是自带的 [cppzmq](https://github.com/zeromq/cppzmq)，虽然比较简单，但也基本够用了。

由于ZMQ把自身定位于更高层次的“异步消息队列”，所以它的用法就不像Socket、HTTP那么简单直白，而是定义了5种不同的工作模式，来适应实际中常见的网络通信场景。

我来大概说一下这5种模式：

- 原生模式（RAW），没有消息队列功能，相当于底层Socket的简单封装；
- 结对模式（PAIR），两个端点一对一通信；
- 请求响应模式（REQ-REP），也是两个端点一对一通信，但请求必须有响应；
- 发布订阅模式（PUB-SUB），一对多通信，一个端点发布消息，多个端点接收处理；
- 管道模式（PUSH-PULL），或者叫流水线，可以一对多，也可以多对一。

前四种模式类似HTTP协议、Client-Server架构，很简单，就不多说了。我拿我在工作中比较常用的管道模式来给你示范一下ZMQ的用法，它非常适合进程间无阻塞传送海量数据，也有点map-reduce的意思。

![](https://static001.geekbang.org/resource/image/8b/2d/8b868214b032aebfcee1e0e97a8a1e2d.png?wh=360*480)

在ZMQ里有两个基本的类。

- 第一个是context\_t，它是ZMQ的运行环境。使用ZMQ的任何功能前，必须要先创建它。
- 第二个是socket\_t，表示ZMQ的套接字，需要指定刚才说的那5种工作模式。注意它与原生Socket没有任何关系，只是借用了名字来方便理解。

下面的代码声明了一个全局的ZMQ环境变量，并定义了一个lambda表达式，生产ZMQ套接字：

```
const auto thread_num = 1;              // 并发线程数

zmq::context_t context(thread_num);     // ZMQ环境变量

auto make_sock = [&](auto mode)        // 定义一个lambda表达式
{
    return zmq::socket_t(context, mode); // 创建ZMQ套接字
};

```

和原生Socket一样，ZMQ套接字也必须关联到一个确定的地址才能收发数据，但它不仅支持TCP/IP，还支持进程内和进程间通信，这在本机交换数据时会更高效：

- TCP通信地址的形式是“tcp://…”，指定IP地址和端口号；
- 进程内通信地址的形式是“inproc://…”，指定一个本地可访问的路径；
- 进程间通信地址的形式是“ipc://…”，也是一个本地可访问的路径。

用bind()/connect()这两个函数把ZMQ套接字连接起来之后，就可以用send()/recv()来收发数据了，看一下示例代码吧：

```
const auto addr = "ipc:///dev/shm/zmq.sock"s;  // 通信地址

auto receiver = [=]()                     // lambda表达式接收数据
{
    auto sock = make_sock(ZMQ_PULL);      // 创建ZMQ套接字，拉数据

    sock.bind(addr);                     // 绑定套接字
    assert(sock.connected());

    zmq::message_t msg;
    sock.recv(&msg);                      // 接收消息

    string s = {msg.data<char>(), msg.size()};
    cout << s << endl;
};

auto sender = [=]()                     // lambda表达式发送数据
{
    auto sock = make_sock(ZMQ_PUSH);     // 创建ZMQ套接字，推数据

    sock.connect(addr);                  // 连接到对端
    assert(sock.connected());

    string s = "hello zmq";
    sock.send(s.data(), s.size());       // 发送消息
};

```

这段代码实现了两个最基本的客户端和服务器，看起来好像没什么特别的。但你应该注意到，使用ZMQ完全不需要考虑底层的TCP/IP通信细节，它会保证消息异步、安全、完整地到达服务器，让你关注网络通信之上更有价值的业务逻辑。

ZMQ的用法就是这么简单，但想要进一步发掘它的潜力，处理大流量的数据还是要去看 [它的文档](http://wiki.zeromq.org/)，选择合适的工作模式，再仔细调节各种参数。

接下来，我再给你分享两个实际工作中会比较有用的细节吧。

一个是 **ZMQ环境的线程数**。它的默认值是1，太小了，适当增大一些就可以提高ZMQ的并发处理能力。我一般用的是4~6，具体设置为多少最好还是通过性能测试来验证下。

另一个是 **收发消息时的本地缓存数量**，ZMQ的术语叫High Water Mark。如果收发的数据过多，数量超过HWM，ZMQ要么阻塞，要么丢弃消息。

HWM需要调用套接字的成员函数setsockopt()来设置，注意收发使用的是两个不同的标志：

```
sock.setsockopt(ZMQ_RCVHWM, 1000);     // 接收消息最多缓存1000条
sock.setsockopt(ZMQ_SNDHWM, 100);      // 发送消息最多缓存100条

```

我们把HWM设置成多大都可以，比如我就曾经在一个高并发系统里用过100万以上的值，不用担心，ZMQ会把一切都处理得很好。

关于ZMQ就暂时说到这里，它还有很多强大的功能，你可以阅读 [官网](http://zguide.zeromq.org/page:all) 上的教程和指南，里面非常详细地讨论了ZMQ的各种模式和要点。

## 小结

好了，我来给今天的内容做一个小结：

1. libcurl是一个功能完善、稳定可靠的应用层通信库，最常用的就是HTTP协议；
2. cpr是对libcurl的C++封装，接口简单易用；
3. libcurl和cpr都只能作为客户端来使用，不能编写服务器端应用；
4. ZMQ是一个高级的网络通信库，支持多种通信模式，可以把消息队列功能直接嵌入应用程序，搭建出高效、灵活、免管理的分布式系统。

最后，再说说即将到来的C++20，原本预计会加入期待已久的networking库，但现在已经被推迟到了下一个版本（C++23）。

networking库基于已有多年实践的boost.asio，采用前摄器模式（Proactor）统一封装了操作系统的各种异步机制（epoll、kqueue、IOCP），而且支持协程。有了它，我们的网络通信工作就会更加轻松。

## 课下作业

最后是课下作业时间，给你留两个思考题：

1. 你在网络编程的时候都遇到过哪些“坑”，今天说的这几个库能否解决你的问题？
2. 你觉得ZMQ能够在多大程度上代替原生Socket？

欢迎你在留言区写下你的思考和答案，如果觉得今天的内容对你有所帮助，也欢迎分享给你的朋友。我们下节课见。

![](https://static001.geekbang.org/resource/image/3e/dd/3e07516e87c61172f9b2ddc317c74add.jpg?wh=2000*2536)