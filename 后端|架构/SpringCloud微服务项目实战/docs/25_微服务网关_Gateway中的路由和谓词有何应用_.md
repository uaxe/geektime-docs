你好，我是姚秋辰。

在上节课中，我们了解了Spring Cloud Gateway网关在微服务架构中的定位，我还介绍了Gateway的三大核心组件路由、谓词和过滤器的基本概念。今天，我们就来进一步认识Gateway的内置功能，了解在Gateway中如何声明一个路由，以及路由中的谓词判断逻辑有什么作用。

Spring Cloud Gateway（以下简称Gateway）提供了非常丰富的内置谓词，你可以通过内置谓词来构建复杂的路由条件，甚至连“整点秒杀”这个场景都能在网关层做控制。这些内置谓词就像乐高积木一样，你可以随意组合在自己的业务逻辑中，构建五花八门的网关层判断逻辑。如果这还不够，那么Gateway还提供了自定义的谓词工厂扩展点，让你构建自定义谓词。

由于这些个谓词都要附着于一个路由之上，所以在介绍谓词之前，我得先和你聊一下怎么声明一个路由。这一节不涉及微服务项目改造，只是让你能够用最直观的方式体验Gateway的功能特点。

## 声明路由的几种方式

在上一节中我们讲到，路由是Gateway中的一条基本转发规则。网关在启动的时候，必须将这些路由规则加载到上下文中，它才能正确处理服务转发请求。那么网关可以从哪些地方加载路由呢？

Gateway提供了三种方式来加载路由规则，分别是Java代码、yaml文件和动态路由。让我们先来一睹为快，近距离感受一下这三种风格迥异的加载方式。

第一种加载方式是Java代码声明路由，它是可读性和可维护性最好的方式，也是我比较喜欢使用的方式。你可以使用一种链式编程的Builder风格来构造一个route对象，比如在下面的例子里，相信就算我不解释，你也能看明白这段代码做的事情。它声明了两个路由，根据path的匹配规则将请求转发到不同的地址。

```plain
@Bean
public RouteLocator declare(RouteLocatorBuilder builder) {
    return builder.routes()
            .route("id-001", route -> route
                    .path("/geekbang/**")
                    .uri("http://time.geekbang.org")
            ).route(route -> route
                    .path("/test/**")
                    .uri("http://www.test.com")
            ).build();
}

```

第二种方式是通过配置文件来声明路由，你可以在application.yml文件中组装路由规则。我把前面定义的Java路由规则改写成了yml版，你可以参考一下。

```plain
spring:
  cloud:
    gateway:
      routes:
        - id: id-001
          uri: http://time.geekbang.org
          predicates:
            - Path=/geekbang2/**
        - uri: http://www.test.com
          predicates:
            - Path=/test2/**

```

不管是Java版还是yml版，它们都是通过“hardcode”的方式声明的静态路由规则，这些Route只会在项目启动后被加载一次。如果你想要在Gateway运行期更改路由逻辑，那么就要使用第三种方式：动态路由加载。

动态路由也有不同的实现方式。如果你在项目中集成了actuator服务，那么就可以通过Gateway对外开放的actuator端点在运行期对路由规则做增删改查。但这种修改只是临时性的，项目重新启动后就会被打回原形，因为这些动态规则并没有持久化到任何地方。

动态路由还有另一种实现方式，是我比较推荐的，那就是借助Nacos配置中心来存储路由规则。Gateway通过监听Nacos Config中的文件变动，就可以动态获取Nacos中配置的规则，并在本地生效了。我将在后面的课程中带你落地一套Nacos+Gateway的动态路由。

了解了如何加载路由规则之后，我们再来看一看，有哪些构建在路由之上的、功能丰富的内置谓词吧。

## Gateway的内置谓词都有哪些

Gateway的内置谓词可真不少，我这里捡一些比较常用的谓词，为你介绍下它们的用法。我把这些谓词大致分为三个类型：寻址谓词、请求参数谓词和时间谓词。我将使用基于Java代码的声明方式，带你挨个来看下如何在路由中配置谓词。

**寻址谓词**，顾名思义，就是针对请求地址和类型做判断的谓词条件。比如这里我们用到的path，其实就是一个路径匹配条件，当请求的URL和Path谓词中指定的模式相匹配的时候，这个谓词就会返回一个True的判断。而method谓词则是根据请求的Http Method做为判断条件，比如我这里就限定了只有GET和POST请求才能访问当前Route。

```plain
.route("id-001", route -> route
      .path("/geekbang/**")
      .and().method(HttpMethod.GET, HttpMethod.POST)
      .uri("http://time.geekbang.org")

```

在上面这段代码中，我添加了不止一个谓词。在谓词与谓词之间，你可以使用and、or、negate这类“与或非”逻辑连词进行组合，构造一个复杂判断条件。

接下来是 **请求参数谓词**，这类谓词主要对服务请求所附带的参数进行判断。这里的参数不单单是Query参数，还可以是Cookie和Header中包含的参数。比如下面这段代码，如果请求中没有包含指定参数，或者指定参数的值和我指定的regex表达式不匹配，那么请求就无法满足当前路由的谓词判断条件。

```plain
.route("id-001", route -> route
    // 验证cookie
    .cookie("myCookie", "regex")
    // 验证header
    .and().header("myHeaderA")
    .and().header("myHeaderB", "regex")
    // 验证param
    .and().query("paramA")
    .and().query("paramB", "regex")
    .and().remoteAddr("远程服务地址")
    .and().host("pattern1", "pattern2")

```

如果你要对原始服务请求的远程地址或Header中的Host参数做些文章，那么你也可以通过remoteAddr和host谓词进行判断。

在实际项目中，非必要情况下，我并不推荐把过多的参数谓词条件定义在网关层，因为这些参数往往携带了业务层的逻辑。如果这些业务参数被大量引入到网关层，从职责分离的角度来讲，并不合适。网关层的逻辑一般来说比较“轻薄”，主要只是一个请求转发，最多再夹带一些简单的鉴权和登录态检查就够了。

最后一组是时间谓词。你可以借助before、after、between这三个时间谓词来控制当前路由的生效时间段。

```plain
.route("id-001", route -> route
   // 在指定时间之前
   .before(ZonedDateTime.parse("2022-12-25T14:33:47.789+08:00"))
   // 在指定时间之后
   .or().after(ZonedDateTime.parse("2022-12-25T14:33:47.789+08:00"))
   // 或者在某个时间段以内
   .or().between(
        ZonedDateTime.parse("起始时间"),
        ZonedDateTime.parse("结束时间"))

```

拿一项秒杀活动来说，如果开发团队做了一个新的秒杀下单入口，我要限定该入口的生效时间在秒杀时间点之后，那么我就可以使用after谓词。对于固定时间窗口的秒杀活动来说，你还可以使用between来限定生效时间窗口。再结合前面我们讲到的请求参数谓词，你还可以实现更加复杂的路由判断逻辑，比如通过query谓词针对特定商品开放不同的秒杀时段。

如果Gateway的内置谓词还差那么点意思，你想要实现自定义的谓词逻辑，那么你可以通过Gateway的可扩展谓词工厂来实现自定义谓词。Gateway组件提供了一个统一的抽象类AbstractRoutePredicateFactory作为谓词工厂，你可以通过继承这个类来添加新的谓词逻辑。

我把实现一个自定义谓词的代码框架放到了这里，你可以参考一下。

```plain
// 继承自通用扩展抽象类AbstractRoutePredicateFactory
public class MyPredicateFactory extends
    AbstractRoutePredicateFactory<MyPredicateFactory.Config> {

   public MyPredicateFactory() {
      super(Config.class);
   }

   // 定义当前谓词所需要用到的参数
   @Validated
   public static class Config {
       private String myField;
   }

   @Override
   public List<String> shortcutFieldOrder() {
      // 声明当前谓词参数的传入顺序
      // 参数名要和Config中的参数名称一致
      return Arrays.asList("myField");
   }

   // 实现谓词判断的核心方法
   // Gateway会将外部传入的参数封装为Config对象
   @Override
   public Predicate<ServerWebExchange> apply(Config config) {
      return new GatewayPredicate() {

         // 在这个方法里编写自定义谓词逻辑
         @Override
         public boolean test(ServerWebExchange exchange) {
            return true;
         }

         @Override
         public String toString() {
            return String.format("myField: %s", config.myField);
         }
      };
   }
}

```

这个实现的过程非常简单，相信看了上面的源码就能明白。这里面的关键步骤就两步，一是定义Config结构来接收外部传入的谓词参数，二是实现apply方法编写谓词判断逻辑。我将会留一道课后作业让你自己动手实现一个专属谓词。

到这里，我们就了解了Gateway的路由和谓词是如何完成请求转发的。接下来我来带你回顾一下这一节的重点内容吧。

## 总结

今天我们了解了Gateway中声明路由的三种不同方式。对于静态路由来说，我推荐你使用可读性更强的Java代码方式来配置路由；至于动态路由呢，就等到后面的课程，我再教你如何使用Nacos定义JSON格式动态路由吧。

但是这里要注意的是，一般来讲，路由规则是不受开发团队控制的。暴露什么URL给到外部网关，那可是涉及到安全性的一个决策，在大厂中，所有的对外接口都要经过严格的漏扫和渗透测试，然后再经由相关团队审批才能上线路由规则。

在实际工作中，最最常用的谓词当属path，其它大部分内置谓词都用不太上，如果你想要使用这些谓词在网关层判断登录状态或者做权限验证，那么我更推荐你使用Gateway的Filter机制，也就是过滤器。我在下节课将基于Gateway限流的场景，跟你讲一下如何在路由规则中添加Filter。

## 思考题

结合这节课的内容，你能自己写一个自定义谓词实现某个简单逻辑吗？比如说恶搞的“春节炸弹”，在春节这一天将所有请求转发到一个特定的URL（不要使用between谓词来实现）。这里你需要思考一个问题，如果某个请求同时满足两个路由的判断条件，如何设置其中一个路由先行生效。

好啦，这节课就结束啦。欢迎你把这节课分享给更多对Spring Cloud感兴趣的朋友。我是姚秋辰，我们下节课再见！