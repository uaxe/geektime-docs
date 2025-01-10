你好，我是何辉。今天我们来聊一聊中小厂的Dubbo高频面试题。

中小厂，招你进来是要立马干活的，需要你面对快节奏的迭代需求，能根据架构师分配的任务，独立自主开发。

所以， **中小厂面试，一般重点考察面试者对基础知识的掌握程度，会比较偏实战**。如果你对基础知识掌握不牢，完成需求交付，本来就比较耗费时间，如果交付过程中还因为各种基础的技术问题研究老半天，就少不了加班加点来还技术债。

面试中问到 Dubbo，一般会问平常工作中常用的基础知识点，主要是考察你对基础知识点的掌握程度，对 Dubbo 是否拥有足够扎实的基础知识面，来评判 **面试者是否具备快速上手项目的能力**。

如果你被突如其来的未知问题难倒，不要慌，你可以说不知道，也可以在脑海中快速检索出相似的知识点聊聊自己的看法，还可以尝试用自己的所学谈谈对这个问题的专业理解。但 **千万别不懂装懂**，一旦被面试官戳穿，那你后面的面试大概率就是走走过场，最后来一个毫无音讯的“等通知”。

有些时候，面试官是职场多年的老江湖，可能不会太关注你回答的内容是否正确，但是他们会从你的手势、言语、表情等多方面，综合评判你回答问题的流畅度和自信度，即便面试者一本正经地胡说八道，只要你能自圆其说，也是一种能耐。

这里我整理了中小厂常见的 12 个 Dubbo 面试问题，你可以先尝试自己回答一下。

> 1.Dubbo的主要节点角色有哪些？分别是干什么用的？
>
> 2.Dubbo3.x 提供方注册有哪几种方式，怎么设置？消费方订阅又有哪几种方式，又怎么设置？
>
> 3.Dubbo有哪些容错策略，以及作用是什么？
>
> 4.Dubbo 通过 RpcContext 开启了异步之后，是怎么衔接父子线程的上下文信息的？
>
> 5.泛化调用编写代码的关键步骤是怎样的？
>
> 6.点点直连有该怎么设置？
>
> 7.Dubbo 的事件通知怎么设置？
>
> 8.Dubbo 的参数验证是怎么设置的？
>
> 9.Dubbo 怎么设置缓存？缓存有哪些类似可以设置？
>
> 10.配置的加载顺序是怎样的？
>
> 11.Dubbo 默认使用的是什么通信框架？
>
> 12.Dubbo 的 <dubbo:application>、<dubbo:reference> 等标签，是怎么被加载到 Spring 中的呢？

接下来我们具体分析每个问题，看看你的掌握程度。

### 问题一

1. Dubbo的主要节点角色有哪些？分别是干什么用的？

这个问题是想看你对 Dubbo 总体架构的了解，Dubbo 的构成角色一般能说出 Provider 提供方、Consumer 消费方就及格了，如果能说出五个角色以及每个角色的作用就更好，这样基本上可以说明你对 Dubbo 的整体架构是有过一定了解的，至少在排查异常问题时，能知道是哪个角色出了问题，而不至于看到异常，不知所措。

我们在“ [温故知新](https://time.geekbang.org/column/article/611355)”中学过，如果不太记得，可以复习巩固一下。

Dubbo的主要节点角色有五个。

- Container：服务运行容器，为服务的稳定运行提供运行环境。
- Provider：提供方，暴露接口提供服务。
- Consumer：消费方，调用已暴露的接口。
- Registry：注册中心，管理注册的服务与接口。
- Monitor：监控中心，统计服务调用次数和调用时间。

这五个角色构成了 Dubbo 的总体架构。

![](https://static001.geekbang.org/resource/image/bd/8d/bd909dd97b113920b3f70fe97c4ab98d.jpg?wh=3377x1998)

### 问题二

2. Dubbo3.x 提供方注册有哪几种方式，怎么设置？消费方订阅又有哪几种方式，又怎么设置？

这个问题是想看你对 Dubbo 新版本特性的掌握程度，一般老项目升级至 Dubbo 新版本会用到这个，一般答出提供方有注册模式和消费方有订阅模式就及格了，如果能说出每种模式下的枚举值就更好。

我们在“ [温故知新](https://time.geekbang.org/column/article/611355)”中在介绍提供方和消费方的时候有学过。

提供方注册有 3 种方式，在程序上可以通过设置 **dubbo.application.register-mode** 属性来控制不同的注册模式，设置的值有3 种：

- interface：只接口级注册。
- instance：只应用级注册。
- all：接口级注册、应用级注册都会存在，同时也是默认值。

消费方订阅其实也有 3 种方式，在程序上是通过设置 **dubbo.application.service-discovery.migration** 属性来兼容新老订阅方案的，设置的值同样有 3 种：

- FORCE\_INTERFACE：只订阅消费接口级信息。
- APPLICATION\_FIRST：注册中心有应用级注册信息则订阅应用级信息，否则订阅接口级信息，起到了智能决策来兼容过渡方案。
- FORCE\_APPLICATION：只订阅应用级信息。

### 问题三

3. Dubbo有哪些容错策略以及作用是什么？

这个问题是想看你对调用异常时的容错设置的掌握程度，每种容错设置都有对应的适用场景，一般能说出 failover、failfast、broadcast 这几个名字和功效就基本及格了，如果能说出更多的名字，以及说明每种容错设置具有什么样的效果，可以说明你对消费方调用异常时该怎么应对，是有过一定研究的。

我们在“ [温故知新](https://time.geekbang.org/column/article/611355)”中，消费方调用时发生故障异常时讲过十种容错设置。具体明细是：

![](https://static001.geekbang.org/resource/image/2f/e6/2f44d50b8947f14589865ccf167e8ce6.jpg?wh=4000x3060)

### 问题四

4. Dubbo 通过 RpcContext 开启了异步之后，是怎么衔接父子线程的上下文信息的？

这个问题是想看你对多线程之间数据如何衔接传递的掌握程度，一般说出使用具体的 API 就及格了，如果能再说出上下文的本质属性就更好，毕竟会使用 API 基本上是标配，能了解背后的底层原理就更值得称赞了。

我们在“ [异步化实践](https://time.geekbang.org/column/article/611392)”中在分析 Dubbo 异步实现原理时学过过，如果不太记得，可以复习巩固一下。

RpcContext 通过调用 startAsync 方法开启异步模式之后，然后在另外的线程中采用 asyncContext.signalContextSwitch 方法来同步父线程的上下文信息，本质还是进行了 ThreadLocal 传递。

因为 asyncContext 富含上下文信息， **只需要把这个所谓的 asyncContext 对象传入到子线程中，然后将 asyncContext 中的上下文信息充分拷贝到子线程的 ThreadLocal 中**，这样，子线程处理所需要的任何信息就不会因为开启了异步化处理而缺失。

### 问题五

5. 泛化调用编写代码的关键步骤是怎样的？

这个问题是想看你对 Dubbo 的高级特性——泛化调用的掌握程度，因为泛化调用所提供的特性，非常适合把某些功能抽象成通用的调用框架，一般提到 ReferenceConfig、GenericService 两个关键类就基本及格了，如果能讲清楚需要哪些关键参数，同时比划一下调用的关键类、关键方法就更好。

我们在“ [泛化调用](https://time.geekbang.org/column/article/613308)”中编码实现部分详细学习过。

- 首先，要明确 4 个维度的参数，分别是：接口类名、接口方法名、接口方法参数类名、业务请求参数。
- 然后，根据接口类名创建 ReferenceConfig 对象，设置 generic = true 属性，调用 referenceConfig.get 拿到 genericService 泛化对象。
- 最后，将接口方法名、接口方法参数类名、业务请求参数，传入 genericService.$invoke 方法中，即可拿到响应对象。

一个简单的泛化调用案例代码，仅供参考。

```java
@RestController
public class CommonController {
    // 响应码为成功时的值
    public static final String SUCC = "000000";

    // 定义URL地址
    @PostMapping("/gateway/{className}/{mtdName}/{parameterTypeName}/request")
    public String commonRequest(@PathVariable String className,
                                @PathVariable String mtdName,
                                @PathVariable String parameterTypeName,
                                @RequestBody String reqBody){
        // 将入参的req转为下游方法的入参对象，并发起远程调用
        return commonInvoke(className, parameterTypeName, mtdName, reqBody);
    }

    /**
     * <h2>模拟公共的远程调用方法.</h2>
     *
     * @param className：下游的接口归属方法的全类名。
     * @param mtdName：下游接口的方法名。
     * @param parameterTypeName：下游接口的方法入参的全类名。
     * @param reqParamsStr：需要请求到下游的数据。
     * @return 直接返回下游的整个对象。
     * @throws InvocationTargetException
     * @throws IllegalAccessException
     */
    public static String commonInvoke(String className,
                                      String mtdName,
                                      String parameterTypeName,
                                      String reqParamsStr) {
        // 然后试图通过类信息对象想办法获取到该类对应的实例对象
        ReferenceConfig<GenericService> referenceConfig = createReferenceConfig(className);

        // 远程调用
        GenericService genericService = referenceConfig.get();
        // 泛化调用
        Object resp = genericService.$invoke(
                mtdName,
                new String[]{parameterTypeName},
                new Object[]{JSON.parseObject(reqParamsStr, Map.class)});

        // 判断响应对象的响应码，不是成功的话，则组装失败响应
        if(!SUCC.equals(OgnlUtils.getValue(resp, "respCode"))){
            return RespUtils.fail(resp);
        }

        // 如果响应码为成功的话，则组装成功响应
        return RespUtils.ok(resp);
    }

    private static ReferenceConfig<GenericService> createReferenceConfig(String className) {
        DubboBootstrap dubboBootstrap = DubboBootstrap.getInstance();

        // 设置应用服务名称
        ApplicationConfig applicationConfig = new ApplicationConfig();
        applicationConfig.setName(dubboBootstrap.getApplicationModel().getApplicationName());

        // 设置注册中心的地址
        String address = dubboBootstrap.getConfigManager().getRegistries().iterator().next().getAddress();
        RegistryConfig registryConfig = new RegistryConfig(address);
        ReferenceConfig<GenericService> referenceConfig = new ReferenceConfig<>();
        referenceConfig.setApplication(applicationConfig);
        referenceConfig.setRegistry(registryConfig);
        referenceConfig.setInterface(className);

        // 设置泛化调用形式
        referenceConfig.setGeneric("true");
        // 设置默认超时时间5秒
        referenceConfig.setTimeout(5 * 1000);
        return referenceConfig;
    }
}

```

### 问题六

6. 点点直连有该怎么设置？

这个问题是想看你对单点直连调用的掌握程度，因为测试环境的快速联调，或者产线问题的快速修复，都会需要这种特殊的请求连接方式。一般提到可以通过设置 url 属性来进行点点直连就及格了，如果能说出通过多种方式来设置 url 属性的话就更好，更能说明你平常对 url 属性配置这块研究得非常透彻。

在“ [点点直连](https://time.geekbang.org/column/article/613319)”中的万能管控部分，我们详细学习过。

- 可以设置在 <dubbo:reference> 标签中，比如：

```java
<dubbo:reference url="dubbo://192.168.0.6:20884" />

```

- 也可以设置在 @DubboReference 注解中，比如：

```java
@DubboReference(url = "dubbo://192.168.0.6:20884")

```

- 还可以通过 -D 参数设置在 JVM 启动命名中，比如：

```java
-Ddubbo.reference.com.hmily.dubbo.api.UserQueryFacade.url=dubbo://192.168.0.6:20884

```

- 还在设置在外部配置文件中，比如设置在外部的 dubbo.properties 配置文件中，比如：

```java
dubbo.reference.com.hmily.dubbo.api.UserQueryFacade.url=dubbo://192.168.0.6:20884

```

### 问题七

7. Dubbo 的事件通知怎么设置？

这个问题考察新增的技术属性如何通过事件通知的方式进行解耦，一般说到通过在 @DubboReference 注解或 <dubbo:reference/> 标签中设置属性，来实现事件通知机制，基本上就及格了，如果能说出事件通知机制的底层实现原理就更好，说明你平时对事件通知的背后原理机制是有过细心研究的。

我们在“ [事件通知](https://time.geekbang.org/column/article/613332)”中也学过，如果不太记得，可以复习巩固一下。

- 首先，创建一个服务类，在该类中添加 onInvoke、onReturn、onThrow 三个方法。
- 其次，在三个方法中按照源码 FutureFilter 的规则定义好方法入参。
- 最后，@DubboReference 注解中或者 <dubbo:reference/> 标签中给需要关注事件的Dubbo接口添加配置即可。

而事件通知的底层实现原理，是借助于 FutureFilter 过滤器来实现的，底层实现的原理主要有 3 个重要环节。

- 在 invoker.invoke(invocation) 方法之前，利用 fireInvokeCallback 方法反射调用了接口配置中指定服务中的 onInvoke 方法。
- 然后在 onResponse 响应时，处理了正常返回和异常返回的逻辑，分别调用了接口配置中指定服务中的 onReturn、onThrow 方法。
- 最后在 onError 框架异常后，调用了接口配置中指定服务中的 onThrow 方法。

一个简单的事件通知在消费方简单设置的案例代码。

```java
@DubboService
@Component
public class PayFacadeImpl implements PayFacade {
    @Autowired
    @DubboReference(
            /** 为 DemoRemoteFacade 的 sayHello 方法设置事件通知机制 **/
            methods = {@Method(
                    name = "sayHello",
                    oninvoke = "eventNotifyService.onInvoke",
                    onreturn = "eventNotifyService.onReturn",
                    onthrow = "eventNotifyService.onThrow")}
    )
    private DemoRemoteFacade demoRemoteFacade;
}

// 专门为 demoRemoteFacade.sayHello 该Dubbo接口准备的事件通知处理类
@Component("eventNotifyService")
public class EventNotifyServiceImpl implements EventNotifyService {
    // 调用之前
    @Override
    public void onInvoke(String name) {
        System.out.println("[事件通知][调用之前] onInvoke 执行.");
    }
    // 调用之后
    @Override
    public void onReturn(String result, String name) {
        System.out.println("[事件通知][调用之后] onReturn 执行.");
        // 埋点已支付的商品信息
        method2();
        // 发送支付成功短信给用户
        method3();
        // 通知物流派件
        method4();
    }
    // 调用异常
    @Override
    public void onThrow(Throwable ex, String name) {
        System.out.println("[事件通知][调用异常] onThrow 执行.");
    }
}

```

### 问题八

8. Dubbo 的参数验证是怎么设置的？

这个问题是想看你对使用注解方式进行参数验证的掌握程度，一般答到会使用 jvalidation 进行参数验证就及格了，能说出自定义校验器来进行定制化的参数校验就更好，因为普通的属性只能满足普通的诉求，特殊的定制化诉求，还得靠定制化校验器来承载。

我们在“ [参数验证](https://time.geekbang.org/column/article/613339)”的统一验证环节有学过。

Dubbo 源码中使用参数校验有两种方式。

- 一般方式，设置 validation 为 jvalidation、jvalidationNew 两种框架提供的值。
- 特殊方式，设置 validation 为自定义校验器的类路径，并将自定义的类路径添加到 META-INF 文件夹下面的 org.apache.dubbo.validation.Validation 文件中。

参数验证的简单案例代码我也写在了下面。

```java
@Component
public class InvokeDemoFacade {

    // 注意，@DubboReference 这里添加了 validation 属性
    @DubboReference(validation ＝ "jvalidation")
    private ValidationFacade validationFacade;

    // 一个简单的触发调用下游 ValidationFacade.validateUser 的方法
    public String invokeValidate(String id, String name, String sex) {
        return validationFacade.validateUser(new ValidateUserInfo(id, name, sex));
    }
}

```

### 问题九

9. Dubbo 怎么设置缓存？缓存有哪些类似可以设置？

这个问题是考察面对接口高频大量调用时，如何针对接口优雅添加缓存特性。一般说可以通过使用注解来简单添加缓存就基本及格了，如果能说出可以在哪些地方为接口调用添加缓存，以及有哪些缓存方式的设置，并且说明每种缓存方式的本质原理就更好。

在“ [缓存操作](https://time.geekbang.org/column/article/613346)”中我们详细学过。

缓存设置，有好些地方可以设置，比如可以在 <dubbo:service/>、<dubbo:method/>、<dubbo:provider/>、<dubbo:consumer/>、@DubboReference、@DubboService 这些标签或注解的地方，都是可以设置缓存的。

缓存的类型，有 4 种选择方式，比如有 lru、threadlocal、jcache、expiring 四种缓存策略。

- lru，使用的是 LruCacheFactory 工厂类，类注释上有提到使用 LruCache 缓存类来进行处理，实则背后使用的是 JVM 内存。
- threadlocal，使用的是 ThreadLocalCacheFactory 工厂类，类名中 ThreadLocal 是本地线程的意思，而 ThreadLocal 最终还是使用的是 JVM 内存。
- jcache，使用的是 JCacheFactory 工厂类，是提供 javax-spi 缓存实例的工厂类，既然是一种 spi 机制，可以接入很多自制的开源框架。
- expiring，使用的是 ExpiringCacheFactory 工厂类，内部的 ExpiringCache 中还是使用的 Map 数据结构来存储数据，仍然使用的是 JVM 内存。

### 问题十

10. 配置的加载顺序是怎样的？

这个问题是想看你对属性配置后生效的优先级掌握程度，一般答到 API / XML / 注解、Local File 这两个层级就及格了，如果能继续把另外 2 种更高级的说出来，以及每种层级关系适合放哪些配置属性，就更好了。

我们在“ [配置加载顺序](https://time.geekbang.org/column/article/615345)”中也学过，如果不记得，可以复习一下。

在 [官网覆盖关系图](https://dubbo.apache.org/imgs/blog/configuration.jpg) 的基础之上，这里配备了常用的配置写法。

![](https://static001.geekbang.org/resource/image/e4/1c/e47919148139eb4c4c17925yy808721c.png?wh=4716x2134)

主要有四个层级关系。

- System Properties，最高优先级，我们一般会在启动命令中通过 JVM 的 -D 参数进行指定，图中通过 -D 参数从指定的磁盘路径加载配置，也可以从公共的 NAS 路径加载配置。
- Externalized Configuration，优先级次之，外部化配置，我们可以直接从统一的配置中心加载配置，图中就是从 Nacos 配置中心加载配置。
- API / XML / 注解，优先级再次降低，这三种应该是我们开发人员最熟悉不过的配置方式了。
- Local File，优先级最低，一般是项目中默认的一份基础配置，当什么都不配置的时候会读取。

### 问题十一

11. Dubbo 默认使用的是什么通信框架？

这个问题考察远程调用时，数据收发到底是采用哪种通信框架，主要是想看你平常写业务代码或者调用出现异常时，有没有研究过 Dubbo 是怎么进行数据收发的，一般答到使用 Netty 通信框架就及格了，如果还能说出除 Netty 在整个 Dubbo 框架位于的层次，那就更好了。

我在“ [源码框架](https://time.geekbang.org/column/article/615369)”的思考题参考答案中放了一段消费方调用异常时的堆栈日志，你可以详细看下。

默认使用 Netty 作为 Dubbo 的网络通信框架。同时，Netty 也位于 Dubbo 十层模块中的第 9 层，Transport 层。

### 问题十二

12. Dubbo 的 <dubbo:application>、<dubbo:reference> 等标签，是怎么被加载到 Spring 中的？

这个问题想看你是否掌握日常开发经常使用的标签背后的原理，一般能说出生成 bean 对象就及格了，如果能稍微描述一下底层读取解析的简要流程就更好，充分说明你对平常使用的东西有较深入的研究，是值得加入候选人的。

针对流程的关键节点，我梳理了下。

主要关注这个 DubboNamespaceHandler 命名空间处理类，Spring 在启动的时候，不但会读取 Spring 默认的一些 schema，还会读取第三方（比如 Dubbo）自定义的 schema。

Spring 的底层会回调 NamespaceHandler 接口的所有实现类，调用每个实现类的 parse 方法，然而 DubboNamespaceHandler 也就是在这个 parse 方法中完成了配置的解析，并转为 Spring 的 bean 对象。

## 面试小技巧

这 12 个中小厂常见的面试问题，总的来说，都是一些日常开发经常用到的知识点，一般在研发过程中，你稍微研究一下用到的技术知识点，回答这些基础面试题应该都不是什么难事。

而且面试时，面试官并不会面面俱到问完所有的基础知识点，只会蜻蜓点水问几个常用，如果你能自信地回答，在面试官心目中就留下基础知识扎实的好印象了，技术层面上说，起码招进来实战开发问题不大。当然还有很多其他因素需要综合考虑，因不同公司而异。

**你要注意的是，基础面试，表面看似基础，实际是最能看出面试者的一些能力水平的，这种基础知识点，怎么回答，你可以尝试用 START 法则。**

- “S”—— situation，背景或环境。
- “T”—— task，制定任务。
- “A”—— action，实施步骤。
- “R”—— result，结果反响。
- “T”—— think，思考改进。

比如针对这个面试问题，你当时遇到了一个怎么样的背景问题，在分析问题的过程中，你给自己制定了怎样的任务目标或者期望，然后采取了怎样的实施步骤，得到了什么结果，效果如何，最后针对已知的结果，思考未来可以怎样改进，来得到更好的效果。

中小厂面试题和面试技巧的解读就告一段落了。当你走上了技术这条路，将来一定会遇到各色各样的奇葩问题，夯实基础知识，就像打地基，地基越牢，楼层就能建得越高，你透过现象看穿问题本质，也就会越快。

下一讲，我们讨论大厂面试。下一讲见。

### 27 思考题参考

第27讲留了个作业，研究下 DubboProtocol 是怎么根据接收的入参，找到对应的 Invoker 对象来处理业务逻辑的。

要想解答这个问题，避免不了查看源码。既然提到了 DubboProtocol 是如何处理调用的，那就有必要深入到 DubboProtocol 中接收数据的地方看看，一打开该类，就看到了 reply 响应数据的方法。

```java
///////////////////////////////////////////////////
// org.apache.dubbo.remoting.exchange.support.ExchangeHandlerAdapter#reply
// 接收请求，处理请求，响应数据
///////////////////////////////////////////////////
@Override
public CompletableFuture<Object> reply(ExchangeChannel channel, Object message) throws RemotingException {

    // 省略其他部分代码...

    Invocation inv = (Invocation) message;

    // 找到了最核心的获取 invoker 代码的地方
    Invoker<?> invoker = getInvoker(channel, inv);

    // 省略其他部分代码...

    RpcContext.getServiceContext().setRemoteAddress(channel.getRemoteAddress());
    // 拿着找到的 invoker 就开始一路 invoke 调用了，最终得到的是一个 result 对象
    Result result = invoker.invoke(inv);
    // 返回最终的数据
    return result.thenApply(Function.identity());
}
                  ↓
///////////////////////////////////////////////////
// org.apache.dubbo.rpc.protocol.dubbo.DubboProtocol#getInvoker
// 根据一系列
///////////////////////////////////////////////////
Invoker<?> getInvoker(Channel channel, Invocation inv) throws RemotingException {
    boolean isCallBackServiceInvoke;
    boolean isStubServiceInvoke;
    int port = channel.getLocalAddress().getPort();
    String path = (String) inv.getObjectAttachments().get(PATH_KEY);
    // if it's callback service on client side
    isStubServiceInvoke = Boolean.TRUE.toString().equals(inv.getObjectAttachments().get(STUB_EVENT_KEY));
    // 获取重要 port 参数
    // port = 28270
    if (isStubServiceInvoke) {
        port = channel.getRemoteAddress().getPort();
    }

    //callback
    // 获取重要 path 参数
    // path = com.hmilyylimh.cloud.facade.demo.DemoFacade
    isCallBackServiceInvoke = isClientSide(channel) && !isStubServiceInvoke;
    if (isCallBackServiceInvoke) {
        path += "." + inv.getObjectAttachments().get(CALLBACK_SERVICE_KEY);
        inv.getObjectAttachments().put(IS_CALLBACK_SERVICE_INVOKE, Boolean.TRUE.toString());
    }

    // 拼接一个唯一字符串值
    // serviceKey = com.hmilyylimh.cloud.facade.demo.DemoFacade:28270
    String serviceKey = serviceKey(
            port,
            path,
            (String) inv.getObjectAttachments().get(VERSION_KEY),
            (String) inv.getObjectAttachments().get(GROUP_KEY)
    );

    // 通过拼接出来的唯一字符串，直接从 exporterMap 中找到对应的 invoker 对象
    DubboExporter<?> exporter = (DubboExporter<?>) exporterMap.get(serviceKey);
    if (exporter == null) {
        throw new RemotingException(channel, "Not found exported service: " + serviceKey + " in " + exporterMap.keySet() + ", may be version or group mismatch " +
                ", channel: consumer: " + channel.getRemoteAddress() + " --> provider: " + channel.getLocalAddress() + ", message:" + getInvocationWithoutData(inv));
    }
    return exporter.getInvoker();
}

```

看完这段代码，invoker 对象的寻找， **居然是根据 port + path + version + group 四个参数组合起来，从 exporterMap 中直接取出对应的 invoker 而已**。

这也就和当初在“ [发布流程](https://time.geekbang.org/column/article/620988)”中了解到的衔接起来了，提供方在导出服务时，导出的对象会存储在 exporterMap 中，当初的服务导出把对象存储在 exporterMap 中，等到有请求过来的时候，就直接从 exporterMap 取出对应的 invoker 进行处理业务逻辑，设计非常巧妙。