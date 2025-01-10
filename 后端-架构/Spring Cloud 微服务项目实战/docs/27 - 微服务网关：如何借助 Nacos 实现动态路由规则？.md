你好，我是姚秋辰。

在上节课中，我们通过一系列谓词和过滤器的组合为三个微服务模块配置了路由规则，这套方案足以应对大部分线上业务的需求，但在可扩展性方面还不够完美。为什么这么说呢？因为这些路由规则是以yml文件或者Java代码配置在项目中的静态规则。随着项目启动，这些路由规则会被加载到应用上下文并生效。但在程序运行期，如果我们想要改变这些预定义的路由规则，或者创建新的路由规则，似乎只有提交改动到Gateway组件->编译项目->重新部署这一条路子。

那么，如果我们希望不重新部署网关，就能更改路由规则，可以有哪些途径呢？

有一种“临时性”的方案，是借助Gateway网关的actuator endpoiont进行CRUD。Gateway组件内定义了一套内置的actuator endpoints，当满足下面两个条件时，我们就可以借助actuator提供的能力对路由表进行修改了。

- 项目中存在spring-boot-starter-actuator依赖项；
- Gateway组件的actuator endpoint已对外开放。


  为了满足上面这两个条件，我已经将配置项添加到了Gateway模块中，并且在application.yml文件中的management节点下，对外开放了所有actuator端点。

接下来，你就可以借助Gateway组件的actuator endpoiont完成一系列CRUD操作了。以实战项目的源码为例，actuator endpoint地址是localhost:30000/actuator/gateway/routes。这套接口遵循了标准的RESTful规范，你可以对这个路径发起GET请求，获取一段JSON格式的路由规则全集，也可以使用POST请求添加一个新的路由规则，或者使用PUT/DELETE请求修改/删除指定路由规则。

好了，Gateway的actuator动态路由功能我就点到即止了，actuator方案尽管实现了动态路由管理，但这些动态路由只保存在了应用的上下文中，一重启就没了。接下来我要给你介绍个更牛的方案，它不仅能动态管理路由表，而且还能让这些规则实现持久化，无论怎么重启都不会丢失路由规则。

下面，我们就来了解一下，如何借助Nacos Config实现动态路由规则的持久化。

## 使用Nacos Config添加动态路由表

**但凡有动态配置相关的需求，使用Nacos Config就对了**。上节课里我已经将Nacos Config的依赖项添加到了Gateway模块，接下来我们直奔主题，看一下Gateway和Nacos是如何来集成的吧。

首先，我们需要定义一个底层的网关路由规则编辑类，它的作用是将变化后的路由信息添加到网关上下文中。我把这个类命名为GatewayService，放置在com.geekbang.gateway.dynamic包路径下。

```java
@Slf4j
@Service
public class GatewayService {

    @Autowired
    private RouteDefinitionWriter routeDefinitionWriter;

    @Autowired
    private ApplicationEventPublisher publisher;

    public void updateRoutes(List<RouteDefinition> routes) {
        if (CollectionUtils.isEmpty(routes)) {
            log.info("No routes found");
            return;
        }

        routes.forEach(r -> {
            try {
                routeDefinitionWriter.save(Mono.just(r)).subscribe();
                publisher.publishEvent(new RefreshRoutesEvent(this));
            } catch (Exception e) {
                log.error("cannot update route, id={}", r.getId());
            }
        });
    }
}

```

这段代码接收了一个RouteDefinition List对象作为入参，它是Gateway网关组件用来封装路由规则的标准类，在里面包含了谓词、过滤器和metadata等一系列构造路由规则所需要的元素。在主体逻辑部分，我调用了Gateway内置的路由编辑类RouteDefinitionWriter，将路由规则写入上下文，再调用ApplicationEventPublisher类发布一个路由刷新事件。

接下来，我们要去做一个中间层转换层来对接Nacos和GatewayService，这个中间层主要完成两个任务，一是动态接收Nacos Config的参数，二是将配置文件的内容转换为GatewayService的入参。

这里我不打算使用@RefreshScope来获取Nacos动态参数了，我另辟蹊径使用了一种更为灵活的监听机制，通过注册一个“监听器”来获取Nacos Config的配置变化通知。我把这段逻辑封装在了DynamicRoutesListener类中，它位于GatewayService同级目录下，你可以参考下面的代码实现。

```java
@Slf4j
@Component
public class DynamicRoutesListener implements Listener {

    @Autowired
    private GatewayService gatewayService;

    @Override
    public Executor getExecutor() {
        log.info("getExecutor");
        return null;
    }

    // 使用JSON转换，将plain text变为RouteDefinition
    @Override
    public void receiveConfigInfo(String configInfo) {
        log.info("received routes changes {}", configInfo);

        List<RouteDefinition> definitionList = JSON.parseArray(configInfo, RouteDefinition.class);
        gatewayService.updateRoutes(definitionList);
    }
}

```

DynamicRoutesListener实现了Listener接口，后者是Nacos Config提供的标准监听器接口，当被监听的Nacos配置文件发生变化的时候，框架会自动调用receiveConfigInfo方法执行自定义逻辑。在这段方法里，我将接收到的文本对象configInfo转换成了List类，并调用GatewayService完成路由表的更新。

这里需要你注意的一点是，你需要按照RouteDefinition的JSON格式来编写Nacos Config中的配置项，如果两者格式不匹配，那么这一步格式转换就会抛出异常。

定义好了监听器之后，接下来你就要考虑如何来加载Nacos路由配置项了。我们需要在两个场景下加载配置文件，一个是项目首次启动的时候，从Nacos读取文件用来初始化路由表；另一个场景是当Nacos的配置项发生变化的时候，动态获取配置项。

为了能够一石二鸟简化开发，我决定使用一个类来搞定这两个场景。我定义了一个叫做DynamicRoutesLoader的类，它实现了InitializingBean接口，后者是Spring框架提供的标准接口。它的作用是在当前类所有的属性加载完成后，执行一段定义在afterPropertiesSet方法中的自定义逻辑。

在afterPropertiesSet方法中我执行了两项任务，第一项任务是调用Nacos提供的NacosConfigManager类加载指定的路由配置文件，配置文件名是routes-config.json；第二项任务是将前面我们定义的DynamicRoutesListener注册到routes-config.json文件的监听列表中，这样一来，每次这个文件发生变动，监听器都能够获取到通知。

```java
@Slf4j
@Configuration
public class DynamicRoutesLoader implements InitializingBean {

    @Autowired
    private NacosConfigManager configService;

    @Autowired
    private NacosConfigProperties configProps;

    @Autowired
    private DynamicRoutesListener dynamicRoutesListener;

    private static final String ROUTES_CONFIG = "routes-config.json";

    @Override
    public void afterPropertiesSet() throws Exception {
        // 首次加载配置
        String routes = configService.getConfigService().getConfig(
                ROUTES_CONFIG, configProps.getGroup(), 10000);
        dynamicRoutesListener.receiveConfigInfo(routes);

        // 注册监听器
        configService.getConfigService().addListener(ROUTES_CONFIG,
                configProps.getGroup(),
                dynamicRoutesListener);
    }

}

```

到这里，我们的代码任务就完成了，你只需要往项目的bootstrap.yml文件中添加Nacos Config的配置项就可以了。按照惯例，我仍然使用dev作为存放配置文件的namespace。

```plain
spring:
  application:
    name: coupon-gateway
  cloud:
    nacos:
      config:
        server-addr: localhost:8848
        file-extension: yml
        namespace: dev
        timeout: 5000
        config-long-poll-timeout: 1000
        config-retry-time: 100000
        max-retry: 3
        refresh-enabled: true
        enable-remote-sync-config: true

```

完成了以上步骤之后，Gateway组件的改造任务就算搞定了，接下来我再带你去Nacos里创建一个路由规则配置文件。

## 添加Nacos配置文件

在Nacos配置列表页中，你需要在“开发环境”的命名空间下创建一个JSON格式的文件，文件名要和Gateway代码中的名称一致，叫做“routes-config.json”，它的Group是默认分组，也就是DEFAULT\_GROUP。

创建好之后，你需要根据RoutesDefinition这个类的格式定义配置文件的内容。以coupon-customer-serv为例，我编写了下面的路由规则。

```json
[{
    "id": "customer-dynamic-router",
    "order": 0,
    "predicates": [{
        "args": {
            "pattern": "/dynamic-routes/**"
        },
        "name": "Path"
    }],
    "filters": [{
        "name": "StripPrefix",
        "args": {
            "parts": 1
        }
    }
    ],
    "uri": "lb://coupon-customer-serv"
}]

```

在这段配置文件中，我指定当前路由的ID是customer-dynamic-router，并且优先级为0。除此之外，我还定义了一段Path谓词作为路径匹配规则，还通过StripPrefix过滤器将Path中第一个前置路径删除。

创建完成后，你可以在本地启动项目，并尝试访问localhost:30000/dynamic-routes/coupon-customer/requestCoupon，发起一个用户领券请求到Gateway组件来领取优惠券。在配置正确无误的情况下，这个请求就会被转发到Customer服务啦。

到这里，我们就完整搭建了一套可被持久化的动态路由方案。下面让我来带你回顾下本节重点吧。

## 总结

在今天的课程里，我们借助Nacos Config作为路由规则的数据源，完成了路由表的动态加载和持久化。我这里讲的解决方案只是一种思路，在代码中我还留了一个坑给你来填，希望你可以顺着这节课学到的技术方案向下继续探索，把这个坑填上。

我所指的坑是什么呢？我在Nacos Config里定义的路由表中有一个ID，它是这个路由的全局唯一ID，借助这个ID呢我们就可以完成路由的UPDATE操作。但是，如果我想要删除某个路由，应该怎么办呢？

我可以给你提示几个解决方案，你挑其中一种来实现就好。比如说，你可以对Nacos配置项做一层额外封装，添加几个新字段用来表示“删除路由”这个语义，并创建一个自定义POJO类接收参数；还有，你可以在路由的metadata里为Nacos的动态路由做一个特殊标记，每次当Nacos刷新路由表的时候，就删除上下文当中的所有Nacos路由表，再重新创建；又或者你可以通过metadata做一个逻辑删除的标记，每次更新路由表的时候只要见到这个标记就删除当前路由，否则就更新或新建路由。

## 思考题

我在上面提示了几种路由删除的方案，希望可以抛砖引玉，接下来就轮到你来设计并实现一个优雅方案了，欢迎在留言区分享你自己的思路。

好啦，这节课就结束啦。欢迎你把这节课分享给更多对Spring Cloud感兴趣的朋友。我是姚秋辰，我们下节课再见！