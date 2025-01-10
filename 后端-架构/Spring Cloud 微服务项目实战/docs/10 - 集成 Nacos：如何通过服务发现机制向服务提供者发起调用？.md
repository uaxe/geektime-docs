你好，我是姚秋辰。

在上一课里，我们对coupon-template-serv和coupon-calculation-serv这两个服务做了微服务化改造，通过服务注册流程将它们注册到了Nacos Server。这两个服务是以服务提供者的身份注册的，它们之间不会发生相互调用。为了发起一次完整的服务调用请求，我们还需要构建一个服务消费者去访问Nacos上的已注册服务。

coupon-customer-serv就扮演了服务消费者的角色，它需要调用coupon-template-serv和coupon-calculation-serv完成自己的业务流程。今天我们就来动手改造coupon-customer-serv服务，借助Nacos的服务发现功能从注册中心获取可供调用的服务列表，并发起一个远程服务调用。

通过今天的内容，你可以了解如何使用Webflux发起远程调用，并熟练掌握如何搭建一套基于Nacos的服务治理方案。

## 添加Nacos依赖项和配置信息

在开始写代码之前，你需要将以下依赖项添加到customer-customer-impl子模块的pom.xml文件中。

```
<!-- Nacos服务发现组件 -->
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>

<!-- 负载均衡组件 -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-loadbalancer</artifactId>
</dependency>

<!-- webflux服务调用 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>

```

第一个依赖项你一定很熟悉了，它是Nacos服务治理的组件，我们在上一节课程中也添加了同款依赖项到coupon-template-impl和coupon-calculation-impl两个模块。

后面两个依赖项你应该是第一回见到，我来向你简单介绍一下。

- **spring-cloud-starter-loadbalancer**：Spring Cloud御用负载均衡组件Loadbalancer，用来代替已经进入维护状态的Netflix Ribbon组件。我会在下一课带你深入了解Loadbalancer的功能，今天我们只需要简单了解下它的用法就可以了；
- **spring-boot-starter-webflux**：Webflux是Spring Boot提供的响应式编程框架，响应式编程是基于异步和事件驱动的非阻塞程序。Webflux实现了Reactive Streams规范，内置了丰富的响应式编程特性。今天我将用Webflux组件中一个叫做WebClient的小工具发起远程服务调用。

添加好这两个依赖之后，你还需要做一番清理门户的工作，让coupon-customer-serv和另外两个微服务之间划清界限。

1. **删除实现层依赖**：从coupon-customer-impl的依赖项中删除coupon-template-impl和coupon-calculation-impl；
2. **添加接口层依赖**：在coupon-customer-impl的依赖项中添加coupon-template-api和coupon-calculation-api。

这样做的目的是 **划清服务之间的依赖关系**，由于coupon-customer-serv是一个独立的微服务，它不需要将其他服务的“代码逻辑实现层”打包到自己的启动程序中一同启动。如果某个应用场景需要调用其它微服务，我们应该使用远程接口调用的方式对目标服务发起请求。因此，我们需要将对应接口的Impl实现层从coupon-customer-impl的依赖中删除，同时引入API层的依赖，以便构造请求参数和接收服务响应。

接下来，你还需要在coupon-customer-impl项目的application.yml文件中添加Nacos的配置项，我们直接从coupon-template-impl的配置项里抄作业就好了。将spring.cloud.nacos路径下的配置项copy到coupon-customer-impl项目中，如果你通过spring.cloud.nacos.discovery.service参数指定了服务名称，那你要 **记得在抄作业的时候把名字改掉**，改成coupon-customer-impl。

修改完依赖项和配置信息之后，你的代码一定冒出了不少编译错误。因为尽管我们已经将coupon-template-impl和coupon-calculation-impl依赖项删除，但coupon-customer-impl中的CouponCustomerServiceImpl仍然使用Autowire注入的方式调用本地服务。

所以接下来，我们就需要对调用层做一番改造，将Autowire注入本地服务的方式，替换为使用WebClient发起远程调用。

## 添加WebClient对象

为了可以用WebClient发起远程调用，你还需要在Spring上下文中构造一个WebClient对象。标准的做法是创建一个Configuration类，并在这个类中通过@Bean注解创建需要的对象。

所以我们在coupon-customer-impl子模块下创建了com.geekbang.coupon.customer.Configuration类，并声明WebClient的Builder对象。

```
// Configuration注解声明配置类
@org.springframework.context.annotation.Configuration
public class Configuration {

    // 注册Bean并添加负载均衡功能
    @Bean
    @LoadBalanced
    public WebClient.Builder register() {
        return WebClient.builder();
    }

}

```

虽然上面的代码没几行，但我足足用了三个注解，这些注解各有用途。

- @ **Configuration注解**：定义一个配置类。在Configuration类中定义的@Bean注解方法会被AnnotationConfigApplicationContext或者AnnotationConfigWebApplicationContext扫描并在上下文中进行构建；
- @ **Bean注解**：声明一个受Spring容器托管的Bean；
- @ **LoadBalanced注解**：为WebClient.Build构造器注入特殊的Filter，实现负载均衡功能，我在下一课会详细解释负载均衡的知识点。今天咱就好读书不求甚解就可以了，只需要知道这个注解的作用是在远程调用发起之前选定目标服务器地址。

WebClient创建好了之后，你就可以在业务类中注入WebClient对象，并发起服务调用了。接下来，我就手把手带你将CouponCustomerServiceImpl里的本地方法调用替换成WebClient远程调用。

## 使用WebClient发起远程方法调用

首先，我们将Configuration类中声明的WebClient的Builder对象注入到CouponCustomerServiceImpl类中，两行代码简单搞定：

```
@Autowired
private WebClient.Builder webClientBuilder;

```

接下来，我们开始改造第一个接口requestCoupon。你需要将requestCoupon接口实现的第一行代码中的CouponTemplateService本地调用替换为WebClient远程调用。下面是改造之前的代码。

```
CouponTemplateInfo templateInfo = templateService.loadTemplateInfo(request.getCouponTemplateId());

```

远程接口调用的代码改造可以通过WebClient提供的“链式编程”轻松实现，下面是代码的完整实现。

```
CouponTemplateInfo templateInfo = webClientBuilder.build()
        .get()
        .uri("http://coupon-template-serv/template/getTemplate?id=" + request.getCouponTemplateId())
        .retrieve()
        .bodyToMono(CouponTemplateInfo.class)
        .block();

```

在这段代码中，我们应用了几个关键方法发起远程调用。

- get：指明了Http Method是GET，如果是其他请求类型则使用对应的post、put、patch、delete等方法；
- uri：指定了访问的请求地址；
- retrieve + bodyToMono：指定了Response的返回格式；
- block：发起一个阻塞调用，在远程服务没有响应之前，当前线程处于阻塞状态。

在使用uri指定调用服务的地址时，你并不需要提供目标服务的IP地址和端口号，只需要将目标服务的服务名称coupon-template-serv告诉WebClient就好了。Nacos在背后会通过服务发现机制，帮你获取到目标服务的所有可用节点列表。然后，WebClient会通过负载均衡过滤器，从列表中选取一个节点进行调用，整个流程对开发人员都是 **透明的**、 **无感知的**。

你可以看到，在代码中我使用了retrieve + bodyToMono的方式接收Response响应，并将其转换为CouponTemplateInfo对象。在这个过程中，我只接收了Response返回的Body内容，并没有对Response中包含的其它字段进行处理。

如果你需要获取完整的Response，包括Http status、headers等额外数据，就可以使用retrieve + toEntity的方式，获取包含完整Response信息的ResponseEntity对象。示例如下，你可以自己在项目中尝试这种调用方式，体验下toEntity和bodyToMono的不同之处。

```
Mono<ResponseEntity<CouponTemplateInfo>> entityMono = client.get()
	.uri("http://coupon-template-serv/template/xxxx")
	.accept(MediaType.APPLICATION_JSON)
	.retrieve()
	.toEntity(CouponTemplateInfo.class);

```

WebClient使用了一种 **链式编程** 的风格来构造请求对象，链式编程就是我们熟悉的Builder建造者模式。仔细观察你会发现，大部分开源应用都在使用这种设计模式简化对象的构建。如果你需要在自己的项目中使用Builder模式，你可以借助Lombok组件的@Builder注解来实现。如果你对此感兴趣，可以自行了解Lombok组件的相关用法。

到这里，我们已经完成了requestCoupon方法的改造，接下来我们趁热打铁，动手去替换findCoupon和placeOrder方法中的本地调用。有了之前的基础，这次替换对你来说已经是小菜一碟了。

在findCoupon方法中，我们需要调用coupon-template-serv的服务批量查询CouponTemplate。这里的方式和前面一样，我使用WebClient对本地调用进行了替换，你可以参考下面的源码。

```
Map<Long, CouponTemplateInfo> templateMap = webClientBuilder.build().get()
        .uri("http://coupon-template-serv/template/getBatch?ids=" + templateIds)
        .retrieve()
        .bodyToMono(new ParameterizedTypeReference<Map<Long, CouponTemplateInfo>>() {})
        .block();

```

由于方法的返回值不是一个标准的Json对象，而是Map<Long, CouponTemplateInfo>类型，因此你需要构造一个ParameterizedTypeReference实例丢给WebClient，告诉它应该将Response转化成什么类型。

现在，我们还剩下一个关键方法没有改造，那就是placeOrder，它调用了coupon-calculation-serv计算最终的订单价格，你可以参考以下源码。

```
ShoppingCart checkoutInfo = webClientBuilder.build()
        .post()
        .uri("http://coupon-calculation-serv/calculator/checkout")
        .bodyValue(order)
        .retrieve()
        .bodyToMono(ShoppingCart.class)
        .block();

```

和前面几处改造不同的是，这是一个POST请求，因此在使用webClient构造器的时候我调用了post方法；除此之外，它还需要接收订单的完整信息作为请求参数，因此我这里调用了bodyValue方法，将封装好的Order对象塞了进去。在coupon-customer-impl中剩下的一些远程调用方法，就留给你来施展拳脚做改造了。

到这里，我们整个Nacos服务改造就已经完成了。你可以在本地依次启动coupon-template-serv、coupon-calculation-serv和coupon-customer-serv。启动成功后，再到Nacos控制台查看这三个服务是否已经全部注册到了Nacos。

如果你是以集群模式启动了多台Nacos服务器，那么即便你在实战项目中只配置了一个Nacos URL，并没有使用虚拟IP搭建单独的集群地址，注册信息也会传播到Nacos集群中的所有节点。

![](https://static001.geekbang.org/resource/image/f7/2b/f7ab64d2526106b7734c2608ae01c02b.jpg?wh=2000x903)

现在，动手搭建一套基于Nacos的服务治理方案对你而言一定不是难事儿了。动手能力是有了，但我们也不能仅仅满足于学会使用一套技术， **你必须要深入到技术的具体实现方案，才能从中汲取到养分，为你将来的技术方案设计提供参考**。

那么接下来，就让我带你去了解一下Nacos服务发现的底层实现，学习一下Client端是通过什么途径从Nacos Server获取服务注册表的。

## Nacos服务发现底层实现

Nacos Client通过一种 **主动轮询** 的机制从Nacos Server获取服务注册信息，包括地址列表、group分组、cluster名称等一系列数据。简单来说，Nacos Client会开启一个本地的定时任务，每间隔一段时间，就尝试从Nacos Server查询服务注册表，并将最新的注册信息更新到本地。这种方式也被称之为“Pull”模式，即客户端主动从服务端拉取的模式。

负责拉取服务的任务是UpdateTask类，它实现了Runnable接口。Nacos以开启线程的方式调用UpdateTask类中的run方法，触发本地的服务发现查询请求。

UpdateTask这个类隐藏得非常深，它是HostReactor

的一个内部类，我带你看一下经过详细注释的代码走读：

```
public class UpdateTask implements Runnable {

    // ....省略部分代码

    // 获取服务列表
    @Override
    public void run() {
        long delayTime = DEFAULT_DELAY;

        try {
            // 根据service name获取到当前服务的信息，包括服务器地址列表
            ServiceInfo serviceObj = serviceInfoMap
                .get(ServiceInfo.getKey(serviceName, clusters));

            // 如果为空，则重新拉取最新的服务列表
            if (serviceObj == null) {
                updateService(serviceName, clusters);
                return;
            }

            // 如果时间戳<=上次更新的时间，则进行更新操作
            if (serviceObj.getLastRefTime() <= lastRefTime) {
                updateService(serviceName, clusters);
                serviceObj = serviceInfoMap.get(ServiceInfo.getKey(serviceName, clusters));
            } else {
                // 如果serviceObj的refTime更晚，
                // 则表示服务通过主动push机制已被更新，这时我们只进行刷新操作
                refreshOnly(serviceName, clusters);
            }
            // 刷新服务的更新时间
            lastRefTime = serviceObj.getLastRefTime();

            // 如果订阅被取消，则停止更新任务
            if (!notifier.isSubscribed(serviceName, clusters) && !futureMap
                    .containsKey(ServiceInfo.getKey(serviceName, clusters))) {
                // abort the update task
                NAMING_LOGGER.info("update task is stopped, service:" + serviceName + ", clusters:" + clusters);
                return;
            }
            // 如果没有可供调用的服务列表，则统计失败次数+1
            if (CollectionUtils.isEmpty(serviceObj.getHosts())) {
                incFailCount();
                return;
            }
            // 设置延迟一段时间后进行查询
            delayTime = serviceObj.getCacheMillis();
            // 将失败查询次数重置为0
            resetFailCount();
        } catch (Throwable e) {
            incFailCount();
            NAMING_LOGGER.warn("[NA] failed to update serviceName: " + serviceName, e);
        } finally {
            // 设置下一次查询任务的触发时间
            executor.schedule(this, Math.min(delayTime << failCount, DEFAULT_DELAY * 60), TimeUnit.MILLISECONDS);
        }
    }
}

```

在UpdateTask的源码中，它通过调用updateService方法实现了服务查询和本地注册表更新，在每次任务执行结束的时候，在结尾处它通过finally代码块设置了下一次executor查询的时间，周而复始循环往复。

以上，就是Nacos通过UpdateTask来查询服务端注册表的底层原理了。

那么现在我就要考考你了，你知道UpdateTask是在什么阶段由哪一个类首次触发的吗？我已经把这个藤交到你手上了，希望你能顺藤摸瓜，顺着UpdateTask类，从源码层面找到它的上游调用方，理清整个服务发现链路的流程。

## 总结

到这里，我们就完成了geekbang-coupon-center的Nacos服务治理改造。通过这两节课，你完整搭建了整个Nacos服务治理链路。在这条链路中，你通过 **服务注册** 流程实现了服务提供者的注册，又通过 **服务发现** 机制让服务消费者获取服务注册信息，还能通过WebClient发起 **远程调用**。

在这段学习过程中，学会如何使用技术是一件很容易的事儿，而学会它背后的原理却需要花上数倍的功夫。在每节实战课里我都会加上一些源码分析，不仅授之以鱼，更要授之以渔，让你学会如何通过深入源码去学习一个框架。

为什么学习源码这么重要呢？我这么说吧，这就像你学习写作一样，小学刚开始练习写作的时候，我们是从“模仿”开始的。随着阅历、知识和阅读量的增多，你逐渐有了自己的思考和想法，建立了属于你的写作风格。学习技术也是类似的，好的开源框架就像一本佳作，Spring社区孵化的框架更是如此，你从中可以汲取很多营养，进而完善自己的架构理念和技术细节。若干年后当你成为独当一面的架构师，这些平日里的积累终会为你所用。

## 思考题

如果某个服务节点碰到了某些异常状况，比如网络故障或者磁盘空间已满，导致无法响应服务请求。你知道Nacos通过什么途径来识别故障服务，并从Nacos Server的服务注册表中将故障服务剔除的吗？

好啦，这节课就结束啦。欢迎你把这节课分享给更多对Spring Cloud感兴趣的朋友。我是姚秋辰，我们下节课再见！