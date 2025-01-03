你好，我是姚秋辰。

在上一讲中，我们已经将OpenFeign组件集成到了实战项目中。今天我们来进一步深入OpenFeign的功能特性，学习几个OpenFeign的进阶使用技巧：异常信息排查、超时判定和服务降级。

异常信息排查是我们开发人员每天都要面对的事情。如果你正在开发一个大型微服务应用，你经常需要集成一些由其他团队开发的API，这就免不了要参与各种联调和问题排查。如果你是一个经验丰富的老码农，那你一定经常说这样一句话：“你的Request参数是什么？”这句台词在我们平时的API联调和线上异常排查中出镜率很高，因为 **服务请求的入参和出参是分析和排查问题的重要线索**。

为了获得服务请求的参数和返回值，我们经常使用的一个做法就是 **打印日志**。你可以在程序中使用log.info或者log.debug方法将服务请求的入参和返回值一一打印出来。但是，对一些复杂的业务场景来说就没有那么轻松了。

假如你在开发的是一个下单服务，执行一次下单流程前前后后要调用十多个微服务。你需要在请求发送的前后分别打印Request和Response，不仅麻烦不说，我们还未必能把包括Header在内的完整请求信息打印出来。

那我们如何才能引入一个既简单又不需要硬编码的日志打印功能，让它自动打印所有远程方法的Request和Response，方便我们做异常信息排查呢？接下来，我就来给你介绍一个OpenFeign的小功能，轻松实现 **远程调用参数的日志打印**。

## 日志信息打印

为了让OpenFeign可以主动将请求参数打印到日志中，我们需要做两个代码层面的改动。

首先，你需要在配置文件中 **指定FeignClient接口的日志级别为Debug**。这样做是因为OpenFeign组件默认将日志信息以debug模式输出，而默认情况下Spring Boot的日志级别是Info，因此我们必须将应用日志的打印级别改为debug后才能看到OpenFeign的日志。

我们打开coupon-customer-impl模块的application.yml配置文件，在其中加上以下几行logging配置项。

```
logging:
  level:
    com.geekbang.coupon.customer.feign.TemplateService: debug
    com.geekbang.coupon.customer.feign.CalculationService: debug

```

在上面的配置项中，我指定了TemplateService和CalculationService的日志级别为debug，而其它类的日志级别不变，仍然是默认的Info级别。

接下来，你还需要在应用的上下文中使用代码的方式 **声明Feign组件的日志级别**。这里的日志级别并不是我们传统意义上的Log Level，它是OpenFeign组件自定义的一种日志级别，用来控制OpenFeign组件向日志中写入什么内容。你可以打开coupon-customer-impl模块的Configuration配置类，在其中添加这样一段代码。

```
@Bean
Logger.Level feignLogger() {
    return Logger.Level.FULL;
}

```

在上面这段代码中，我指定了OpenFeign的日志级别为Full，在这个级别下所输出的日志文件将会包含最详细的服务调用信息。OpenFeign总共有四种不同的日志级别，我来带你了解一下这四种级别下OpenFeign向日志中写入的内容。

- **NONE**：不记录任何信息，这是OpenFeign默认的日志级别；
- **BASIC**：只记录服务请求的URL、HTTP Method、响应状态码（如200、404等）和服务调用的执行时间；
- **HEADERS**：在BASIC的基础上，还记录了请求和响应中的HTTP Headers；
- **FULL**：在HEADERS级别的基础上，还记录了服务请求和服务响应中的Body和metadata，FULL级别记录了最完整的调用信息。

我们将Feign的日志级别指定为Full，并启动项目发起一个远程调用，你就可以在日志中看到整个调用请求的信息，包括请求路径、Header参数、Request Payload和Response Body。我拿了一个调用日志作为示例，你可以参考一下。

```
 ---> POST http://coupon-calculation-serv/calculator/simulate HTTP/1.1
 Content-Length: 458
 Content-Type: application/json

 {"products":[{"productId":null,"price":3000, xxxx省略请求参数
 ---> END HTTP (458-byte body)
 <--- HTTP/1.1 200 (29ms)
 connection: keep-alive
 content-type: application/json
 date: Sat, 27 Nov 2021 15:11:26 GMT
 keep-alive: timeout=60
 transfer-encoding: chunked

 {"bestCouponId":26,"couponToOrderPrice":{"26":15000}}
 <--- END HTTP (53-byte body)

```

有了这些详细的日志信息，你在开发联调阶段排查异常问题就易如反掌了。

到这里，我们就详细了解了OpenFeign的日志级别设置。接下来，我带你了解如何在OpenFeign中配置超时判定条件。

## OpenFeign超时判定

超时判定是一种保障可用性的手段。如果你要调用的目标服务的RT（Response Time）值非常高，那么你的调用请求也会处于一个长时间挂起的状态，这是造成服务雪崩的一个重要因素。为了隔离下游接口调用超时所带来的的影响，我们可以在程序中设置一个 **超时判定的阈值**，一旦下游接口的响应时间超过了这个阈值，那么程序会自动取消此次调用并返回一个异常。

我们以coupon-customer-serv为例，customer服务依赖template服务来读取优惠券模板的信息，如果你想要对template的远程服务调用添加超时判定配置，那么我们可以在coupon-customer-impl模块下的application.yml文件中添加下面的配置项。

```
feign:
  client:
    config:
      # 全局超时配置
      default:
        # 网络连接阶段1秒超时
        connectTimeout: 1000
        # 服务请求响应阶段5秒超时
        readTimeout: 5000
      # 针对某个特定服务的超时配置
      coupon-template-serv:
        connectTimeout: 1000
        readTimeout: 2000

```

从上面这段代码中可以看出，所有超时配置都放在feign.client.config路径之下，我在这个路径下面声明了两个节点：default和coupon-template-serv。

default节点配置了全局层面的超时判定规则，它的生效范围是所有OpenFeign发起的远程调用。

coupon-template-serv下面配置的超时规则只针对向template服务发起的远程调用。如果你想要对某个特定服务配置单独的超时判定规则，那么可以用同样的方法，在feign.client.config下添加目标服务名称和超时判定规则。

这里需要你注意的一点是，如果你同时配置了全局超时规则和针对某个特定服务的超时规则，那么后者的配置会覆盖全局配置，并且优先生效。

在超时判定的规则中我定义了两个属性：connectTimeout和readTimeout。其中，connectTimeout的超时判定作用于“建立网络连接”的阶段；而readTimeout的超时判定则作用于“服务请求响应”的阶段（在网络连接建立之后）。我们常说的RT（即服务响应时间）受后者影响比较大。另外，这两个属性对应的超时 **时间单位都是毫秒**。

配置好超时规则之后，我们可以验证一下。你可以在template服务中使用Thread.sleep方法强行让线程挂起几秒钟，制造一个超时场景。这时如果你通过customer服务调用了template服务，那么在日志中可以看到下面的报错信息，提示你服务请求超时。

```
[TemplateService#getTemplate] <--- ERROR SocketTimeoutException: Read timed out (2077ms)
[TemplateService#getTemplate] java.net.SocketTimeoutException: Read timed out

```

到这里，相信你已经清楚如何通过OpenFeign的配置项来设置超时判定规则了。接下来，我带你了解一下OpenFeign是如何通过降级来处理服务异常的。

## OpenFeign降级

降级逻辑是在远程服务调用发生超时或者异常（比如400、500 Error Code）的时候，自动执行的一段业务逻辑。你可以根据具体的业务需要编写降级逻辑，比如执行一段兜底逻辑将服务请求从失败状态中恢复，或者发送一个失败通知到相关团队提醒它们来线上排查问题。

在后面课程中，我将会使用Spring Cloud Alibaba的组件Sentinel跟你讲解如何搭建中心化的服务容错控制逻辑，这是一种重量级的服务容错手段。

但在这节课中，我采用了一种完全不同的服务容错手段，那就是借助OpenFeign实现Client端的服务降级。尽管它的功能远不如Sentinel强大，但它相比于Sentinel而言 **更加轻量级且容易实现，** 足以满足一些简单的服务降级业务需求。

OpenFeign对服务降级的支持是借助Hystrix组件实现的，由于Hystrix已经从Spring Cloud组件库中被移除，所以我们需要在coupon-customer-impl子模块的pom文件中手动添加hystrix项目的依赖。

```
<!-- hystrix组件，专门用来演示OpenFeign降级 -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-hystrix</artifactId>
    <version>2.2.10.RELEASE</version>
    <exclusions>
        <!-- 移除Ribbon负载均衡器，避免冲突 -->
        <exclusion>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-netflix-ribbon</artifactId>
        </exclusion>
    </exclusions>
</dependency>

```

添加好依赖项之后，我们就可以编写OpenFeign的降级类了。OpenFeign支持两种不同的方式来指定降级逻辑，一种是定义fallback类，另一种是定义fallback工厂。

通过fallback类实现降级是最为简单的一种途径，如果你想要为TemplateService这个FeignClient接口指定一段降级流程，那么我们可以定义一个降级类并实现TemplateService接口。我写了一个TemplateServiceFallback类，你可以参考一下。

```
@Slf4j
@Component
public class TemplateServiceFallback implements TemplateService {

    @Override
    public CouponTemplateInfo getTemplate(Long id) {
        log.info("fallback getTemplate");
        return null;
    }

    @Override
    public Map<Long, CouponTemplateInfo> getTemplateInBatch(Collection<Long> ids) {
        log.info("fallback getTemplateInBatch");
        return null;
    }
}

```

在上面的代码中，我们可以看出TemplateServiceFallback实现了TemplateService中的所有方法。

我们以其中的getTemplate方法为例，如果在实际的方法调用过程中，OpenFeign接口的getTemplate远程调用发生了异常或者超时的情况，那么OpenFeign会主动执行对应的降级方法，也就是TemplateServiceFallback类中的getTemplate方法。

你可以根据具体的业务场景，编写合适的降级逻辑。

降级类定义好之后，你还需要在TemplateService接口中将TemplateServiceFallback类指定为降级类，这里你可以借助FeignClient接口的fallback属性来配置，你可以参考下面的代码。

```
@FeignClient(value = "coupon-template-serv", path = "/template",
       // 通过fallback指定降级逻辑
       fallback = TemplateServiceFallback.class)
public interface TemplateService {
      // ... 省略方法定义
}

```

如果你想要在降级方法中获取到 **异常的具体原因**，那么你就要借助 **fallback工厂** 的方式来指定降级逻辑了。按照OpenFeign的规范，自定义的fallback工厂需要实现FallbackFactory接口，我写了一个TemplateServiceFallbackFactory类，你可以参考一下。

```
@Slf4j
@Component
public class TemplateServiceFallbackFactory implements FallbackFactory<TemplateService> {

    @Override
    public TemplateService create(Throwable cause) {
        // 使用这种方法你可以捕捉到具体的异常cause
        return new TemplateService() {

            @Override
            public CouponTemplateInfo getTemplate(Long id) {
                log.info("fallback factory method test");
                return null;
            }

            @Override
            public Map<Long, CouponTemplateInfo> getTemplateInBatch(Collection<Long> ids) {
                log.info("fallback factory method test");
                return Maps.newHashMap();
            }
        };
    }
}

```

从上面的代码中，你可以看出，抽象工厂create方法的入参是一个Throwable对象。这样一来，我们在降级方法中就可以获取到原始请求的具体报错异常信息了。

当然了，你还需要将这个工厂类添加到TemplateService注解中，这个过程和指定fallback类的过程有一点不一样，你需要借助FeignClient注解的fallbackFactory属性来完成。你可以参考下面的代码。

```
@FeignClient(value = "coupon-template-serv", path = "/template",
        // 通过抽象工厂来定义降级逻辑
        fallbackFactory = TemplateServiceFallbackFactory.class)
public interface TemplateService {
        // ... 省略方法定义
}

```

到这里，我们就完成了OpenFeign进阶功能的学习。针对这里面的某些功能，我想从日志打印和超时判定这两个方面给你一些实践层面的建议。

**在日志打印方面**，OpenFeign的日志信息是测试开发联调过程中的好帮手，但是在生产环境中你是用不上的，因为几乎所有公司的生产环境都不会使用Debug级别的日志，最多是Info级别。

**在超时判定方面**，有时候我们在线上会使用多维度的超时判定，比如OpenFeign + 网关层超时判定 + Sentinel等等判定。它们可以互相作为兜底方案，一旦某个环节突然发生故障，另一个可以顶上去。但这就形成了一个木桶理论，也就是几种判定规则中最严格的那个规则会优先生效。

## 总结

今天我们了解了OpenFeign的三个进阶小技巧。首先，你使用OpenFeign的日志模块打印了完整的远程服务调用信息，我们可以利用这个功能大幅提高线下联调测试的效率。然后，我带你了解了OpenFeign组件如何设置超时判定规则，通过全局配置+局部配置的方式对远程接口进行超时判定，这是一种有效的防止服务雪崩的可用性保障手段。最后，我们动手搭建了OpenFeign的降级业务，通过fallback类和fallback工厂两种方式实现了服务降级。

关于 **服务降级的方案选型**，我想分享一些自己的见解。很多开发人员过于追求功能强大的新技术，但我们 **做技术选型的时候也要考虑开发成本和维护成本**。

比如像Sentinel这类中心化的服务容错控制台，它的功能固然强大，各种花式玩法它都考虑到了。但相对应地，如果你要在项目中引入Sentinel，在运维层面你要多维护一个Sentinel服务集群，并且在代码中接入Sentinel也是一个成本项。如果你只需要一些简单的降级功能，那OpenFeign+Hystrix的Client端降级方案就完全可以满足你的要求，我认为没必要拿大炮打苍蝇，过于追求一步到位的高大上方案。

到这里，我们OpenFeign组件的课程就结束了，下一节课程我将带你学习如何使用Nacos实现配置管理。

## 思考题

结合这节课的OpenFeign超时判定功能，你知道有哪些超时判定的算法吗？它们的底层原理是什么？欢迎在留言区写下自己的思考，与我一起讨论。

好啦，这节课就结束啦。欢迎你把这节课分享给更多对Spring Cloud感兴趣的朋友。我是姚秋辰，我们下节课再见！