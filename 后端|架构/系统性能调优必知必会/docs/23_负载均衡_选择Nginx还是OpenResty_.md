你好，我是陶辉。

在 [\[第21讲\]](https://time.geekbang.org/column/article/252741) 介绍AKF立方体时，我们讲过只有在下游添加负载均衡后，才能沿着X、Y、Z三个轴提升性能。这一讲，我们将介绍最流行的负载均衡Nginx、OpenResty，看看它们是如何支持AKF扩展体系的。

负载均衡通过将流量分发给新增的服务器，提升了系统的性能。因此，我们对负载均衡最基本的要求，就是它的吞吐量要远大于上游的应用服务器，否则扩展能力会极为有限。因此，目前性能最好的Nginx，以及在Nginx之上构建的OpenResty，通常是第一选择。

系统接入层的负载均衡，常通过Waf防火墙承担着网络安全职责，系统内部的负载均衡则通过权限、流量控制等功能承担着API网关的职责，CDN等边缘节点上的负载均衡还会承担边缘计算的任务。如果负载均衡不具备高度开放的设计，或者推出时间短、社区不活跃， **我们就无法像搭积木一样，从整个生态中低成本地构建出符合需求的负载均衡。**

很幸运的是，Nginx完全符合上述要求，它性能一流而且非常稳定。从2004年诞生之初，Nginx的模块化设计就未改变过，这样16年来累积下的各种Nginx模块都可以复用。它的 [2-clause BSD-like license](https://opensource.org/licenses/BSD-2-Clause) 源码许可协议极其开放，即使修改源码后仍然可作商业用途，因此Nginx之上延伸出了TEngine、OpenResty、Kong等生态，这大大扩展了Nginx的能力边界。

接下来，我们就以Nginx以及建立了Lua语言生态的OpenResty为例，看看负载均衡是怎样扩展系统的，以及Nginx和同源的OpenResty有何不同。

## 负载均衡是如何扩展系统提升性能的？

通过AKF立方体X轴扩展系统时，负载均衡只需要能够透传协议，并选择负载最低的上游应用作为流量分发对象即可。这样，三层（网络层）、四层（传输层）负载均衡都可用于扩展系统，甚至在单个局域网内你还可以使用二层（数据链路层）负载均衡。其中，分发流量的路由算法既可以使用RoundRobin轮转算法，也可以基于TCP连接或者UDP Session使用最少连接数算法，如下图所示：

![](https://static001.geekbang.org/resource/image/a6/yd/a614d25af06a6439874a12d7748afyyd.jpg?wh=807*604)

然而，基于AKF Y轴扩展系统时，负载均衡必须根据功能来分发请求，也就是说它必须解析完应用层协议，才能明白这是什么请求。因此，如LVS这样工作在三层和四层的负载均衡就无法满足需求了，我们需要Nginx这样的七层（应用层）负载均衡，它能够从请求中获取到描述功能的关键信息，并以此为依据路由请求。比如当HTTP请求中的URL描述功能时，Nginx就可以用location匹配URL，再基于location来路由请求，如下图所示：

![](https://static001.geekbang.org/resource/image/19/73/198619be633e7db39e6c8c817078b673.jpg?wh=971*643)

基于AKF Z轴扩展时，如果只是使用了网络报文中的源IP地址，那么三层、四层负载均衡都能胜任。然而如果需要帐号、访问对象等用户信息扩展系统，仍然只能使用七层负载均衡从请求中获得。比如，Nginx可以通过$变量获取到URL参数或者HEADER头部的值，再以此作为路由算法的输入参数。

因此， **七层负载均衡是分布式系统提升性能的必备工具。** 除了基于各种路由策略分发流量，提高性能及可用性（如宕机迁移）外，负载均衡还需要完成上、下游协议间的适配、转换。例如考虑到信息安全，跑在公网上的外部协议常基于TLS/SSL协议，而在效率优先的企业内网中，一般不会使用大幅降低性能的TLS协议，因此负载均衡需要拥有卸载或者装载TLS层的能力。

再比如，下游客户端多样且难以保持一致（比如IE6这个古董浏览器仍然存在于当下的互联网中），因此常使用HTTP协议与服务器通讯，而上游组件则依据开发团队或者系统架构的特点，会选择CGI、uWSGI、gRPC等协议，这样负载均衡还得拥有转换各种协议的功能。Nginx可以通过反向代理模块，轻松适配各类协议，如下所示（通过stream模块，Nginx也支持四层负载均衡）：

![](https://static001.geekbang.org/resource/image/ey/93/eyy0dfeeb4783de585789f1c5b768393.jpg?wh=554*406)

从性能角度，Nginx支持C10M级别的并发连接，其原因你可以参考本专栏第1、2部分的内容。从功能角度，良好的模块化设计，使得Nginx可以完成各类协议的适配，不只包括第3部分课程介绍过的通用协议，甚至支持Redis、MySQL等专有协议。因此，Nginx是目前最好用的负载均衡。

## Nginx上为什么可以执行Lua代码？

OpenResty也非常流行，其实它就是Nginx，只是通过扩展的C模块支持在Nginx中嵌入Lua语言，这样Lua模块构建出的生态就可以与C模块协作使用，大幅度提升了开发效率。我们先来看下OpenResty与Nginx之间的关系。

OpenResty源代码由 **官方Nginx、第三方C模块、Lua语言模块以及一些工具脚本** 构成。编译Nginx时，OpenResty将自己的第三方C模块按照Nginx的规则添加到可执行文件中，包括ngx\_http\_lua\_module和ngx\_stream\_lua\_module这两个C模块，它们允许Lua语言运行在Nginx进程中，如下图所示：

![](https://static001.geekbang.org/resource/image/a7/8e/a73f1f14bec13dddd497aeb4a5393b8e.jpg?wh=7313*2567)

**Lua模块既能够享受Nginx的高性能，又通过“协程”**（参见 [\[第5讲\]](https://time.geekbang.org/column/article/233629)） **、Lua脚本语言提高了开发效率**，这也是OpenResty最大的优点。我们先来看看Lua语言是怎么嵌入到Nginx中的。

**Nginx在进程启动、处理请求时提供了许多钩子函数，允许第三方C模块将其代码放在这些钩子函数中执行。同时，Nginx还允许C模块自行解析nginx.conf中出现的配置项。** 这种架构允许OpenResty将Lua代码写进nginx.conf文件，再基于 [LuaJIT](https://luajit.org/) 即时编译到Nginx中执行。

ngx\_http\_lua\_module模块也正是通过OpenResty提供的以下11个指令嵌入Lua代码的：

- 在Nginx启动时嵌入Lua代码，包括master进程启动时执行的 **init\_by\_lua** 指令，以及每个worker进程启动时执行的 **init\_worker\_by\_lua** 指令。
- 在重写URL、访问权限控制等预处理阶段嵌入Lua代码，包括解析TLS协议后的 **ssl\_certificate\_by\_lua** 指令（基于openssl的回调函数实现），设置动态变量的 **set\_by\_lua** 指令，重写URL阶段的 **rewrite\_by\_lua** 指令，以及控制访问权限的 **access\_by\_lua** 指令。
- 生成HTTP响应时嵌入Lua代码，包括直接生成响应的 **content\_by\_lua** 指令，连接上游服务前的 **balancer\_by\_lua** 指令，处理响应头部的 **header\_filter\_by\_lua** 指令，以及处理响应包体的 **body\_filter\_by\_lua** 指令。
- 记录access.log日志时嵌入Lua代码，通过 **log\_by\_lua** 指令实现。

如下图所示：

![](https://static001.geekbang.org/resource/image/97/c3/9747cc2830cb65513ea0f4e5603b9fc3.jpg?wh=1504*1368)

ngx\_stream\_lua\_module模块与之类似，这里不再赘述。

当然，如果Lua代码只是可以在Nginx进程中执行，它是无法处理用户请求的。我们还需要让Lua代码与Nginx中的C代码互相调用，去获取、改变HTTP请求、响应的内容。因此，ngx\_http\_lua\_module和ngx\_stream\_lua\_module这两个模块通过 [FFI](https://luajit.org/ext_ffi.html) 技术，将C函数通过Ngx库中的Lua API，暴露给纯Lua代码，如下图所示：

![](https://static001.geekbang.org/resource/image/b3/58/b30b937e7866b9e588ce3e0427b1b758.jpg?wh=7052*3186)

这样，通过nginx.conf文件中的11个指令，以及FFI技术提供的SDK，Lua代码才真正可以处理请求，Lua生态从这里开始延伸，因此，OpenResty上还提供了进一步提高开发效率的Lua模块库（参见/usr/local/openresty/lualib/目录）。关于FFI技术及OpenResty提供的HTTP SDK，你可以参考 [《Nginx核心知识100讲》中的第147-154课](https://time.geekbang.org/course/intro/100020301)。

## Nginx与OpenResty的差别在哪里？

清楚了OpenResty与Nginx间的相同之处，我们再来看，二者默认编译出的Nginx可执行程序有何不同之处。

首先看版本差异。当你在 [官网](http://nginx.org/en/download.html) 下载Nginx时，会发现有3类版本：Mainline、Stable和Legacy。其中，Mainline是单号版本， **它是含有最新功能的主线版本，迭代速度最快。Stable是mainline版本稳定运行一段时间后，将单号大版本转换为双号的稳定版本**，比如1.18.0就是由1.17.10转换而来。Legacy则是曾经的稳定版本，如下图所示：

![](https://static001.geekbang.org/resource/image/63/59/63yy17990a31578a4e3ba00af7b67859.jpg?wh=1344*1046)

你可以通过源代码中的CHANGES文件，通过4种不同类型的变更查看版本间的差异，包括：

- 表示新功能的 **Feature**，比如下图中HTTP服务新增的auth\_delay指令。
- 表示已修复问题的 **Bugfix**。
- 表示已知特性变更的 **Change**，比如Nginx曾经允许HTTP请求头部中出现多个Host头部，但在1.17.9这个Change之后，这类HTTP请求将作为非法请求处理。
- 表示安全升级的 **Security**，比如1.15.6版本就修复了CVE-2018-16843等3个安全问题。

![](https://static001.geekbang.org/resource/image/c3/7e/c366e0f928dfc149da5a4df8cb15c27e.jpg?wh=1944*1074)

当你安装好了OpenResty或者Nginx后，你可以通过nginx -v命令查看它们的版本。你会发现， **2014年以后发布的OpenResty都是运行在单号Mainline版本上的：**

```
# /usr/local/nginx/sbin/nginx -v
nginx version: nginx/1.18.0
# /usr/local/openresty/nginx/sbin/nginx -v
nginx version: openresty/1.15.8.3

```

通常我们会选择稳定的Stable版本，OpenResty为什么会选择单号的Mainline版本呢？这是因为， **Nginx与OpenResty的版本发布频率完全不同**，2012年后Nginx每年大约发布10多个版本，如下图所示（versions统计了每年发布的版本数，图中其他3条拆线统计了每年feature、bugfix、change的变更次数）：

![](https://static001.geekbang.org/resource/image/bd/68/bd39d1fd2abbcf1787a34aeb008fa368.jpg?wh=1225*899)

OpenResty每年的版本更新频率是个位数，特别是从2018年到现在，OpenResty只发布了4个版本。所以 **为了使用尽量运行在最新版本上，OpenResty选择了Mainline单号版本。**

你可能会想，OpenResty并没有修改Nginx的源代码，为什么不能由用户在官方Nginx上自行添加C模块，实现OpenResty的安装呢？这源于部分OpenResty C模块，没有按照Nginx架构指定的顺序添加到模块列表中，而且它们的编译环境也过于复杂。因此，OpenResty放弃了Nginx官方的configure文件，用户需要使用OpenResty改造过的configure脚本编译Nginx。

再来看模块间的差异。如果你留意OpenResty与Nginx间二进制文件的体积，会发现使用默认配置时， **OpenResty的可执行文件大了5倍，** 如下所示：

```
# ls -s --block-size=1 /usr/local/openresty/nginx/sbin/nginx
16437248 /usr/local/openresty/nginx/sbin/nginx
# ls -s --block-size=1 /usr/local/nginx/sbin/nginx
3851568 /usr/local/openresty/nginx/sbin/nginx

```

这由2个原因所致。

首先，官方Nginx提供的四层负载均衡功能（由18个STREAM模块实现）、TLS协议处理功能，默认都是不添加到Nginx中的，而OpenResty的configure脚本将其改为了默认模块。当然，如果你在编译官方Nginx时，加入以下选项：

```
./configure --with-stream --with-stream_ssl_module --with-stream_ssl_preread_module --with-http_ssl_module

```

那么从官方模块上，Nginx就与OpenResty完全一致了，此时再观察二进制文件的体积，会发现它翻了一倍：

```
# ls -s --block-size=1 /usr/local/openresty/nginx/sbin/nginx
6999144 /usr/local/openresty/nginx/sbin/nginx

```

其次，OpenResty添加了近20个第三方C模块，除了前文介绍过支持Lua语言的2个模块外，还有支持Redis、Memcached、MySQL等服务的模块。这些模块编译时，还需要链接依赖的软件库，因此它们又将Nginx可执行文件的体积增加了1倍多。

除版本、模块外，OpenResty与Nginx间还有一些小的差异，比如Nginx使用了GCC编译器的-O1优化参数，而OpenResty则使用了-O2优化参数。再比如，官方Nginx最新版本的Makefile支持upgrade参数，简化了热升级操作。当然，这些小改动并不重要，只要修改configure脚本就能做到。

我们到底该如何在二者中选择呢？我认为，如果不使用Lua语言，那么我建议使用Nginx。官方Nginx的Stable版本更稳定，可执行文件的体积也更小。 **如果你需要使用OpenResty、TEngine中的部分C模块，可以通过–add-module选项将其加入到官方Nginx中。**

如果所有C模块都无法满足业务需求，你就应该选择OpenResty。注意，Lua语言给你带来极大灵活性的同时，也会引入许多不确定性。比如，如果你调用了会导致进程休眠的Lua阻塞函数（比如封装了系统调用的原生Lua库，或者第三方服务提供的同步SDK），将会导致Nginx正在处理数万并发请求的C模块同时进入休眠，从而让服务的性能大幅度下降。

## 小结

这一讲，我们介绍了负载均衡的工作方式，以及Nginx、OpenResty这两个最流行的负载均衡之间的异同。

任何负载均衡都能从AKF X轴水平扩展系统，但只有能够解析应用层协议，获取到请求的功能、用户身份、访问对象等信息，才能够沿AKF Y轴、Z轴全方位扩展系统。因此，七层负载均衡是分布式系统提升性能的利器。

Nginx的开放式架构允许第三方模块通过10多个钩子函数，在不同的生命周期中处理请求。同时，还允许C模块自行解析nginx.conf配置文件。这样，OpenResty就通过2个C模块，将Lua代码用LuaJIT编译到Nginx中执行，并通过FFI技术将C函数暴露给Lua代码。这就是OpenResty允许Lua语言与C模块协同处理请求的原因。

OpenResty虽然就是Nginx，但由于版本发布频率低于官方Nginx，因此使用了单号的Mainline版本以获得Nginx的最新特性。由于OpenResty默认加入了四层负载均衡和TLS协议处理功能，还新增了近20个第三方C模块，这造成它编译出的Nginx体积大了5倍。如果无须使用Lua语言就能够满足业务需求，我推荐你使用Nginx。

## 思考题

最后，留给你一道思考题。Nginx、OpenResty都有着丰富、活跃的生态，这也是我们选择开源软件的一个前提。这节课我们提到开放的设计是形成生态的一个必要因素，然而这二者都有许多没有形成生态的竞争对手，你认为开源软件构建出庞大的生态，还需要哪些充分条件呢？欢迎你在留言区与大家一起探讨。

感谢阅读，如果你觉得这节课让你对负载均衡有了更深的了解，搞清楚了OpenResty与Nginx间的差别，也欢迎把它分享给你的朋友。