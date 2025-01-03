你好，我是志东，欢迎和我一起从零打造秒杀系统。

经过前面课程的学习，我们知道Nginx和Tomcat都可以做网关服务，并且从理论出发做了分析比对，也从实践上做了相应服务的开发，那么今天我们将学习一款优秀的、可开发网关服务的技术，即Vertx。该技术的总体性能要优于Tomcat，但弱于Nginx。其在国内的普及度相对国外来说还是比较低的，但已经有些公司开始尝试使用了，比如京东的PC商详页服务、秒杀Web服务都是用它来开发的，并且线上实际效果也很不错。

接下来我们将对Vertx做个简单的介绍，并实际搭建一个Vertx项目，来替换demo-web的角色，重新构造秒杀Web系统的一环。

## **Vertx简介**

我们先了解一下Vertx可以用来干什么，这样我们才能在已知的技术栈中找出一个和其相对应的技术来帮助理解。

首先它可以开发Web服务，这点Nginx、Tomcat也能做。

其次它也有点像Spring，它提供了完整的生态，包括Vertx Web、Vertx Core、Vertx Unit等模块，但它和Spring也不是互斥关系，我们待会搭建的项目中就会使用Vertx+Spring，它们可以配合使用。

然后它还提供了很多其他的能力，比如EventBus的消息机制，实现服务间通信，同时它还可以支持多种语言的开发。

**所以我们很难直接给它做一个精确的定义，但其总体的设计思路就是异步非阻塞。** 这里不仅仅是针对我们熟悉的一些请求消息的读写，还包括下游服务的调用，甚至是数据库的读写都可以实现异步，支持你去编写全链路的非阻塞代码。这样可以使用有限的线程，来充分利用机器的CPU资源，当然这并不能缩短业务接口的执行时间，这点你得清楚。

那么从以上这几个方面来看的话，我们其实很难用一节课把Vertx技术介绍全面，所以这里我们定个更加好实现的小目标，那就是用Vertx+Spring来开发一个Web服务。你可以在这个过程中，和Nginx还有Tomcat做个简单的对比。

## **Vertx对比Nginx和Tomcat**

首先，Nginx由于多进程、单线程、多协程的模式，其占用资源更少，并发处理能力更强，再加上其事件驱动、异步非阻塞等特性，总体性能也是三者中最好的，并且比Vertx和Tomcat要强出很多。

Nginx还可以支持使用Lua、C等语言做业务开发，但大部分以Java为主的公司能够支持的SDK、中间件等相对较少，所以一般都是用它来做反向代理和负载均衡器。因为秒杀的特殊业务场景，故而我们启用了Nginx来做前置网关。

Tomcat的话，大部分公司都用它来部署服务，不管是HTTP服务还是RPC服务。虽然底层线程模型一直在迭代更新，新的NIO模式也大大提高了并发处理能力，但由于其历史更久、内部结构更重，所以整体性能也是三者中最差的，但好在普及度高，绝大部分的公司技术栈里都有它。所以在秒杀系统中我们暂时只用其来启动RPC服务，不再用它来部署Web服务了。

最后是Vertx，就像上面介绍的那样，其在诞生之初，就是以纯异步化的思想来设计的。其内部提供的几乎所有接口都支持异步，并且所有的操作都是基于事件来实现程序的非阻塞运行。再加上它的网络通信框架集成了Netty，其内部的零拷贝机制、基于内存池的缓冲区重用机制，还有高性能的序列化框架，以及它本身的Multi-Reactor模式，总结来看它的性能是要优于Tomcat的。但由于它仍使用线程池来处理业务请求，所以整体性能是弱于Nginx的。

**它的底层线程模型，大概是这样的，如下图所示：**

![图片](https://static001.geekbang.org/resource/image/a5/8f/a525b96dd2cfd7cdc0e59f464fef988f.jpg?wh=1091x753)

简单来说，Vertx在启动时，可以部署多个Verticle实例，每个Verticle实例都是Actor模型的一种具体实现（其内部定义好了整个流程的处理顺序，当然我们可以针对可扩展项做自定义开发）。

它接受请求，然后将其封装成事件，并交给EventLoop线程来处理。当然在EventLoop线程中，我们也可以决定是否将后续事件交给Worker线程来处理，比如像调用外部RPC接口等IO操作。

这里有个黄金原则，即在EventLoop线程里运行的程序一定不能阻塞该线程，否则这将直接影响其处理后续请求的效率。正是因为其有着不错的性能表现，所以在秒杀系统中，我们使用它代替了demo-web，来开发新的Web服务。

那在了解了Vertx的一些基本概念之后，咱们来实际搭建一个Vertx Web项目，使其具备demo-web的能力，同时上下游系统demo-nginx和demo-support不用做任何的改动。下面咱们就正式开始吧！

## **Vertx项目搭建**

**第一步：** 新建一个项目demo-vertx-web，并包含两个module，整体项目结构和demo-web类似，如下图所示：

![图片](https://static001.geekbang.org/resource/image/3c/cc/3cfbc9eaa68e8b8c0bc5be5acc85c9cc.png?wh=764x598)

其中demo-vertx-gateway模块用来做一些文件的配置，并且也是用来打包部署的，demo-vertx-service主要用来做业务聚合，这块的代码到时候可以直接将demo-web中的service模块代码拷过来即可。所以我们主要的改动点也都是在demo-vertx-gateway这一块。

**第二步**：由于没了Tomcat来启动服务，所以我们需要自己写个main方法，来加载对应的配置，完成项目的启动，由于我们仍然使用Spring来管理类，所以这里也通过Spring提供的机制来完成对应配置的加载。如下图所示：

![图片](https://static001.geekbang.org/resource/image/42/16/4254467264d63ebc102187208d884e16.png?wh=1920x823)

那我们继续看下InitialModule类都配置了些什么：

![图片](https://static001.geekbang.org/resource/image/5f/b9/5f4c6a996b938b90a5de67eacd6f70b9.png?wh=1920x1064)

这里首先是导入Spring的配置文件spring-config，同时配置Spring的包扫描路径，其次是初始化Vertx，然后开始部署Verticle实例，这里Vertx的初始化配置和部署实例的配置如下：

![图片](https://static001.geekbang.org/resource/image/c6/8a/c63a5950d369238b7bc8c11148b8568a.png?wh=1920x893)

vertxOptions主要配置了两个属性，即EventLoop线程池大小和Worker线程池大小，而deploymentOptions主要配置了部署的实例数。

这里要注意一下，一个Verticle实例会被指定到一个EventLoop线程处理，一个EventLoop线程可以处理多个Verticle实例，所以这里的EventLoop线程数最好和CPU核数相等，而部署的实例数，最好小于等于EventLoop线程数，这样可以确保一个线程只对应处理一个Verticle实例。比如你是8核机器，那就配置8个EventLoop线程和8个Verticle实例。

**第三步：** 从上面可以看到，我们部署的实例是MainVerticle，在这里我们可以编排请求的处理流程，先看下代码，如下图所示：

![图片](https://static001.geekbang.org/resource/image/52/39/5220cb6cdff8c2f0a7d3fc38fd59ca39.png?wh=1740x1668)

这里我们首先是创建了一个Router，即路由，这个类主要是用来设置请求的处理逻辑，包括哪个URL请求由哪个类的方法来处理，是让EventLoop线程来执行，还是让Worker线程来执行，处理的过程是什么样的等等。

其次我们就按上面说的对Router进行配置了。这里分了两种情况，一种是处理动态请求的，一种是处理静态资源请求的。动态请求的配置咱们先放一下，等会细说，这里先说下配置静态资源请求的情况。

这里统一都是由StaticHandler来处理，同时设置了启用静态资源的缓存，这样就不用每次都读文件了，大大地提高了响应的速度。

StaticHandler处理静态资源的逻辑是直接根据你请求的URL，然后加上配置的WebRoot，来读取文件。所以比如我们想获取结算页H5，我们的请求URL是/settlement/page，这个时候需要我们reroute一下，重新路由到对应要返回的HTML文件路径，这块也会在下面说到。

设置好路由Router之后，我们就可以配置HTTP服务的启动配置了，包括各种HTTP相关的设置，如连接超时配置、端口号设置等。

**第四步：** 这块再详细说下动态路由的配置，我们是通过RouterHelper来做相应配置的。这块的主要功能是将请求URL与对应的处理方法做绑定，并注册到Router，这样请求进来后，就知道该执行哪段业务逻辑了。

![图片](https://static001.geekbang.org/resource/image/d0/0d/d0fd1ab2byy795abccd9035710531b0d.png?wh=1920x968)

这里首先是从Spring管理的Bean中，找出添加了我们自定义注解RequestMapping的类，然后遍历，将请求URL与对应的类和方法注册到Router中，具体的注册方法如下：

![图片](https://static001.geekbang.org/resource/image/c1/69/c151ef7027ac0e2ebb1fd427fc3eb369.png?wh=1920x1204)

这里我们指定了业务逻辑由Worker线程来执行，那是怎么指定的呢？

我们是通过Router的blockingHandler()方法来指定的。如果想在EventLoop线程里执行，则使用route.handler()方法。关于如何合理分配任务，我们有个简单的基本原则，比如你想每秒处理1000个请求，那么理论上每个请求的处理时间不能超过1ms，如果超过了1ms，那就不应该放到EventLoop线程里执行，否则会影响后续请求的处理，所以一般为了简单起见，我们都是将业务逻辑直接分配给Worker线程来处理。

另外在blockingHandler中，我们可以在执行目标方法之前，增加像监控、限流之类的公共逻辑，有点像拦截器的概念。然后执行目标方法的的调用，这里是通过Java的反射来做的。

![图片](https://static001.geekbang.org/resource/image/ca/c7/ca76e89abd8aaee1df8f7c9b07f7cfc7.png?wh=1920x787)

这里目标方法的入参，暂时只适配了2种，一个是RoutingContext，另一个是HttpServerRequest。

这是Vertx的一个弊端，它没有提供直接的功能，无法像SpringMVC一样方便，能够支持在Controller的方法入参里直接定义我们想要的变量来接受入参的值，得需要我们自己去扩展。所以这里为了简便，我们直接先将原始的RoutingContext或HttpServerRequest往下传，其中RoutingContext是一次请求的上下文，HttpServerRequest是将HTTP请求的相关信息都封装进去了，包括入参、Header等。

另外这里要重点关注一下，blockingHandler()方法的第二个入参，可以设置Hander是顺序执行还是并发执行。这个是指同一个Verticle实例下，同一个适配URL，默认是true，但在高并发场景下，需要设置成false，否则吞吐量上不去。

最后，在执行完目标方法之后，需要将响应结果返回。我们根据响应类型，也做了区分处理，目前支持两种，一个是JSON返回，另一个是HTML返回。对于HTML的返回，我们reroute到了真实的静态文件路径，如下图所示：

![图片](https://static001.geekbang.org/resource/image/35/53/359807dyyb6a64d6136179592cff5153.png?wh=1920x986)

并且在异常时，也做同样的区分处理。

**第五步：** 到这里，一些核心逻辑的编写就完成了。下面再看一个业务Handler的示例，为了让你适应SpringMVC的使用习惯，所以这里的写法风格上也是类似的：

![图片](https://static001.geekbang.org/resource/image/b4/38/b41d3e40600ec4409451c772bc9af038.png?wh=1920x732)

这里要记得加上Spring的@Component注解，这样Spring才能将其管理起来。同时也要加上自定义的@RequestMapping注解，这样才能被我们自己的逻辑扫到。

那下面再展示下两种响应类型的写法，如下图所示：

![图片](https://static001.geekbang.org/resource/image/2c/00/2c1f6e5bb3e45a6f8b40444ff64e9100.png?wh=1920x943)

一个是默认返回JSON，另一个是返回HTML（真实的HTML文件路径），HTML的返回需要指定RT的类型。

其他的如Dubbo相关配置，都是和demo-web一样的，剩下的我们只需要将demo-web中的业务代码拷过来即可。唯一有个变动的点，就是在活动查询接口有个请求跨域问题，需要在Nginx中设置响应结果的Header，其他的都没有变化。

那这样，咱们的demo-vertx-web项目就算搭建完成了，之后可以按照以前的测试方式，从商详页进入到结算页然后完成下单，测试整个秒杀流程，这里就不再复述了。

## 总结

这节课我们初步认识了Vertx，这是一种以异步化思想来设计的技术。其内部提供的几乎所有接口都是异步的，并且像传统的RPC调用、数据库读写等阻塞操作，Vertx也都提供了异步化、非阻塞的解决方案。

这和我们传统的开发方式有所不同，你可以借助Vertx习惯这种新的开发思想。当然异步化编程势必会增加代码的复杂度，这也是其弊端。而对于开发Web服务这块，我们横向对比分析了Vertx与Nginx、Tomcat的优劣势，其性能介于Tomcat与Nginx之间，而这三种技术都有其自身的优缺点，并且我们在秒杀系统中都有使用到。

像Nginx，性能最优，我们用其来做前置网关，直面大流量的冲击；Vertx性能次之，所以我们用其来开发业务Web服务；Tomcat使用起来最方便也最普及，可以用来发布RPC服务，或者是像ERP这种小流量的Web服务。

同时在今天这节课中，我们也用了较多的篇幅，来讲解Vertx开发Web服务的详细过程，帮助你更直观地学习Vertx，并投入到实际的使用中。

虽然如此，但今天介绍的也仅仅是Vertx的冰山一角，这里只是起到抛砖引玉的作用，Vertx所具备的能力绝对不止这些。如果你感兴趣，可以自己做进一步的学习，当然更多的相关开发使用，也可以关注我的GitHub，我们一起交流学习。

## **思考题**

这节课我们实际开发的Vertx项目，处理业务逻辑这块，仍然使用的是Worker线程池，这块和Tomcat没有太大区别。如果我们使用Vertx提供的异步化API，该如何改造现有代码呢？又会带来怎样的影响？

期待你的思考，欢迎你来评论区和我讨论问题，交流经验！我们下节课再见。