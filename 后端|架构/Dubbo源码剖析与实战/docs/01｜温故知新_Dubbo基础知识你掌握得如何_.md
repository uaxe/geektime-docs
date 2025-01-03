你好，我是何辉。

任何一门学科都有它基本的知识结构，而Dubbo作为一款优秀的微服务框架，自然也有着其领域的基础知识。所谓万丈高楼平地起，想把Dubbo用得游刃有余，对基础知识的深刻理解就尤为重要了。

举一个最基础的问题：Dubbo的总体架构是什么样？一定有初学者或者面试官问过你吧，但常年忙着写业务代码逻辑，对于这样的提问，想必你是既熟悉又陌生，有种欲言又止的感觉，心里清楚却又无法一气呵成地向他人讲清楚。

没关系，今天，我们就一起来回顾Dubbo的基础知识体系，温故知新，之后我们碰到的一些异常或者问题时，就能快速定位问题归属于Dubbo的哪个角色，找准方向力求解决。

## 总体架构

我们知道，Dubbo的主要节点角色有五个：

- Container：服务运行容器，为服务的稳定运行提供运行环境。
- Provider：提供方，暴露接口提供服务。
- Consumer：消费方，调用已暴露的接口。
- Registry：注册中心，管理注册的服务与接口。
- Monitor：监控中心，统计服务调用次数和调用时间。

我们画一张Dubbo的总体架构示意图，你可以清楚地看到每个角色大致的交互方式：

![图片](https://static001.geekbang.org/resource/image/3c/80/3ce4ae4685e533094598a4608aa6dd80.jpg?wh=1920x1136)

对于一个Dubbo项目来说，我们首先会从提供方进行工程创建（第 ① 步），并启动工程（第 ② 步）来进行服务注册（第 ③ 步），接着会进行消费方的工程创建（第 ④ 步）并启动订阅服务（第 ⑤ 步）来发起调用（第 ⑥ 步），到这里，消费方就能顺利调用提供方了。

消费方在运行的过程中，会感知注册中心的服务节点变更（第 ⑦ 步），最后消费方和提供方将调用的结果指标同步至监控中心（第 ⑧⑨ 步）。

在这样的完整流程中， **每个角色在Dubbo架构体系中具体起到了什么样的作用？每一步我们有哪些操作注意点呢？** 带着问题，我们通过实操来仔细分析。

### 1\. Container 服务运行容器

首先，提供方、消费方的正常运转，离不开一个大前提——运行的环境。

我们需要一个容器来承载应用的运行，可以是 Tomcat 容器，也可以是 Jetty 容器，还可以是 Undertow 容器等等，只要能负责启动、加载，并运行服务提供者来提供服务就可以了。

### 2\. Provider 提供方

有了Container为服务的稳定运行提供环境后，我们就可以开始新建工程了。

**第 ① 步**，先自己新建一个提供方的工程，引用一个 facade.jar 包来对外暴露服务，编写的关键代码如下：

```java
///////////////////////////////////////////////////
// 提供方应用工程的启动类
///////////////////////////////////////////////////
// 导入启动提供方所需要的Dubbo XML配置文件
@ImportResource("classpath:dubbo-04-xml-boot-provider.xml")
// SpringBoot应用的一键式启动注解
@SpringBootApplication
public class Dubbo04XmlBootProviderApplication {
    public static void main(String[] args) {
        // 调用最为普通常见的应用启动API
        SpringApplication.run(Dubbo04XmlBootProviderApplication.class, args);
        // 启动成功后打印一条日志
        System.out.println("【【【【【【 Dubbo04XmlBootProviderApplication 】】】】】】已启动.");
    }
}

///////////////////////////////////////////////////
// 提供方应用工程的Dubbo XML配置文件内容：dubbo-04-xml-boot-provider.xml
///////////////////////////////////////////////////
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:dubbo="http://dubbo.apache.org/schema/dubbo"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans-4.3.xsd
       http://dubbo.apache.org/schema/dubbo
       http://dubbo.apache.org/schema/dubbo/dubbo.xsd">
    <!-- 注册中心的地址，通过 address 填写的地址提供方就可以联系上 zk 服务 -->
    <dubbo:registry address="zookeeper://127.0.0.1:2181"></dubbo:registry>
    <!-- 提供者的应用服务名称 -->
    <dubbo:application name="dubbo-04-xml-boot-provider"></dubbo:application>
    <!-- 提供者需要暴露服务的协议，提供者需要暴露服务的端口 -->
    <dubbo:protocol name="dubbo" port="28040"></dubbo:protocol>
    <!-- 提供者暴露服务的全路径为 interface 里面的内容 -->
    <dubbo:service interface="com.hmilyylimh.cloud.facade.demo.DemoFacade"
                   ref="demoFacade"></dubbo:service>
    <!-- 提供者暴露服务的业务实现逻辑的承载体 -->
    <bean id="demoFacade" class="com.hmilyylimh.cloud.xml.demo.DemoFacadeImpl"></bean>
</beans>

```

将提供方应用启动的代码、Dubbo配置文件内容编写好后，就准备 **第 ② 步** 启动了。

如果你现在运行 Dubbo04XmlBootProviderApplication 启动类，会直接遇到非法状态异常：

```xml
java.lang.IllegalStateException: java.lang.IllegalStateException: zookeeper not connected
	at org.apache.dubbo.config.deploy.DefaultApplicationDeployer.prepareEnvironment(DefaultApplicationDeployer.java:678) ~[dubbo-3.0.7.jar:3.0.7]
	at org.apache.dubbo.config.deploy.DefaultApplicationDeployer.startConfigCenter(DefaultApplicationDeployer.java:261) ~[dubbo-3.0.7.jar:3.0.7]
	at org.apache.dubbo.config.deploy.DefaultApplicationDeployer.initialize(DefaultApplicationDeployer.java:185) ~[dubbo-3.0.7.jar:3.0.7]

```

这是因为不做任何超时时间设置时，ConfigCenterConfig#checkDefault 方法中会默认超时时间为 **30秒**，然后将“30秒”传给 CuratorFramework 让它在有限的时间内连接上注册中心，若30秒还没有连接上的话，就抛出了这里你看到的非法状态异常，提示 `zookeeper not connected`，表示注册中心没有连接上。

所以接下来我们需要做的就是，自己启动一个 ZooKeeper 注册中心，然后再次运行启动类，就能看到启动成功的打印信息：

```markdown
2022-11-11 23:57:27.261  INFO 12208 --- [           main] .h.c.x.Dubbo04XmlBootProviderApplication : Started Dubbo04XmlBootProviderApplication in 5.137 seconds (JVM running for 6.358)
2022-11-11 23:57:27.267  INFO 12208 --- [pool-1-thread-1] .b.c.e.AwaitingNonWebApplicationListener :  [Dubbo] Current Spring Boot Application is await...
【【【【【【 Dubbo04XmlBootProviderApplication 】】】】】】已启动.

```

接下来的 **第 ③ 步** 是在提供方启动的过程中进行的。启动成功后，你可以通过 ZooKeeper 中自带的 zkCli.cmd 或 zkCli.sh 连上注册中心，查看提供方在注册中心留下了哪些痕迹，如图：

![图片](https://static001.geekbang.org/resource/image/66/94/669e2bdb93b579498fc5547168698194.png?wh=1920x1038)

通过 `ls /` 查看根目录，我们发现 Dubbo 注册了两个目录，/dubbo 和 /services 目录：

![图片](https://static001.geekbang.org/resource/image/03/10/03e12e64bb379302175e35dfae696310.jpg?wh=1920x1053)

这是 Dubbo 3.x 推崇的一个应用级注册新特性，在不改变任何 Dubbo 配置的情况下，可以兼容一个应用从 2.x 版本平滑升级到 3.x 版本，这个新特性主要是为了将来能支持十万甚至百万的集群实例地址发现，并且可以与不同的微服务体系实现地址发现互联互通。

但这里有个小问题了，控制提供方应用到底应该接口级注册，还是应用级注册，还是两个都注册呢？

你可以通过在提供方设置 **dubbo.application.register-mode** 属性来自由控制，设置的值有3 种：

- interface：只接口级注册。
- instance：只应用级注册。
- all：接口级注册、应用级注册都会存在，同时也是默认值。

### 3\. Consumer 消费方

提供方启动完成后，我们就可以接着新建消费方的工程了。

**第 ④ 步**，在新建的消费方工程中，同样需要引用 facade.jar 来进行后续的远程调用，你可以参考要编写的关键代码：

```java
///////////////////////////////////////////////////
// 消费方应用工程的启动类
///////////////////////////////////////////////////
// 导入启动消费方所需要的Dubbo XML配置文件
@ImportResource("classpath:dubbo-04-xml-boot-consumer.xml")
// SpringBoot应用的一键式启动注解
@SpringBootApplication
public class Dubbo04XmlBootConsumerApplication {
    public static void main(String[] args) {
        // 调用最为普通常见的应用启动API
        ConfigurableApplicationContext ctx =
                SpringApplication.run(Dubbo04XmlBootConsumerApplication.class, args);
        // 启动成功后打印一条日志
        System.out.println("【【【【【【 Dubbo04XmlBootConsumerApplication 】】】】】】已启动.");
        // 然后向提供方暴露的 DemoFacade 服务进行远程RPC调用
        DemoFacade demoFacade = ctx.getBean(DemoFacade.class);
        // 将远程调用返回的结果进行打印输出
        System.out.println(demoFacade.sayHello("Geek"));
    }
}

///////////////////////////////////////////////////
// 消费方应用工程的Dubbo XML配置文件内容：dubbo-04-xml-boot-consumer.xml
///////////////////////////////////////////////////
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:dubbo="http://dubbo.apache.org/schema/dubbo"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans-4.3.xsd
       http://dubbo.apache.org/schema/dubbo
       http://dubbo.apache.org/schema/dubbo/dubbo.xsd">
    <!-- 消费者的应用服务名称，最好是大家当前应用归属的系统名称 -->
    <dubbo:application name="dubbo-04-xml-boot-consumer"></dubbo:application>
    <!-- 注册中心的地址，通过 address 填写的地址提供方就可以联系上 zk 服务 -->
    <dubbo:registry address="zookeeper://127.0.0.1:2181"></dubbo:registry>
    <!-- 引用远程服务 -->
    <dubbo:reference id="demoFacade"
            interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
    </dubbo:reference>
</beans>

```

把消费方应用启动的代码、Dubbo配置文件内容编写好后，我们就准备启动了。

不过在启动之前，如果提供方还没有启动，也就是说提供方还没有发布 DemoFacade 服务，这个时候，我们启动消费方会看到这样的报错信息：

```markdown
java.lang.IllegalStateException: Failed to check the status of the service com.hmilyylimh.cloud.facade.demo.DemoFacade. No provider available for the service com.hmilyylimh.cloud.facade.demo.DemoFacade from the url consumer://192.168.100.183/com.hmilyylimh.cloud.facade.demo.DemoFacade?application=dubbo-04-xml-boot-consumer&background=false&dubbo=2.0.2&interface=com.hmilyylimh.cloud.facade.demo.DemoFacade&methods=sayHello,say&pid=11876&qos.enable=false&register.ip=192.168.100.183&release=3.0.7&side=consumer&sticky=false&timestamp=1668219196431 to the consumer 192.168.100.183 use dubbo version 3.0.7
	at org.apache.dubbo.config.ReferenceConfig.checkInvokerAvailable(ReferenceConfig.java:545) ~[dubbo-3.0.7.jar:3.0.7]
	at org.apache.dubbo.config.ReferenceConfig.init(ReferenceConfig.java:293) ~[dubbo-3.0.7.jar:3.0.7]
	at org.apache.dubbo.config.ReferenceConfig.get(ReferenceConfig.java:219) ~[dubbo-3.0.7.jar:3.0.7]

```

又看到了非法状态异常的类，告诉我们检查 DemoFacade 的状态失败了，并提示 `No provider available` 说明还暂时没有提供者，导致消费方无法启动成功。

怎么解决这个问题呢？我们可以考虑 3 种方案：

- 方案1：将提供方应用正常启动起来即可。
- 方案2：可以考虑在消费方的Dubbo XML配置文件中，为 DemoFacade 服务添加 `check="false"` 的属性，来达到启动不检查服务的目的，即：

```markdown
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" check="false"
        interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>

```

- 方案3：也可以考虑在消费方的Dubbo XML配置文件中，为整个消费方添加 `check="false"` 的属性，来达到启动不检查服务的目的，即：

```markdown
<!-- 为整个消费方添加启动不检查提供方服务是否正常 -->
<dubbo:consumer check="false"></dubbo:consumer>

```

这 3 种方法，我们结合实际日常开发过程分析一下。

方案1，耦合性太强，因为提供方没有发布服务而导致消费方无法启动，有点说不过去。

方案2，需要针对指定的服务级别设置“启动不检查”，但一个消费方工程，会有几十上百甚至上千个提供方服务配置，一个个设置起来特别麻烦，而且一般我们也很少会逐个设置。

方案3，是我们比较常用的一种设置方式，保证不论提供方的服务处于何种状态，都不能影响消费方的启动，而且只需要一条配置，没有方案2需要给很多个提供方服务挨个配置的困扰。

不过这里为了正常演示，我们还是按照方案1中规中矩的方式来，先把提供方应用启动起来，再启动消费方，接下来你就能看到消费方启动成功的日志打印信息，并且也成功调用了提供方的服务，日志信息就是这样：

```markdown
2022-11-12 10:38:18.758  INFO 11132 --- [pool-1-thread-1] .b.c.e.AwaitingNonWebApplicationListener :  [Dubbo] Current Spring Boot Application is await...
【【【【【【 Dubbo04XmlBootConsumerApplication 】】】】】】已启动.
Hello Geek, I'm in 'dubbo-04-xml-boot-provider' project.

```

现在，消费方能成功启动了，接下来就要去注册中心订阅服务了，也就是 **第 ⑤ 步**，这一步也是在消费方启动的过程中进行的。启动成功后，你可以通过 ZooKeeper 中自带的 zkCli.cmd 或 zkCli.sh 连上注册中心，查看消费方在注册中心留下了哪些痕迹：

![图片](https://static001.geekbang.org/resource/image/85/b3/85e9d1b4d506c3379250c0cf1420c4b3.png?wh=1920x1043)

我们发现消费方也会向注册中心写数据，通过 `ls /dubbo/metadata/com.hmilyylimh.cloud.facade.demo.DemoFacade` 可以看到，有 consumer 目录，还有对应的消费方 URL 注册信息， **所以通过一个 interface，我们就能从注册中心查看有哪些提供方应用节点、哪些消费方应用节点**。

而前面提到 Dubbo 3.x 推崇的一个应用级注册新特性，在消费方侧也存在如何抉择的问题，到底是订阅接口级注册信息，还是订阅应用级注册信息呢，还是说有兼容方案？

![图片](https://static001.geekbang.org/resource/image/22/b0/2215cc5288f326853f77c3aabc9c23b0.jpg?wh=1920x1053)

其实Dubbo也为我们提供了过渡的兼容方案，你可以通过在消费方设置 **dubbo.application.service-discovery.migration** 属性来兼容新老订阅方案，设置的值同样有 3 种：

- FORCE\_INTERFACE：只订阅消费接口级信息。
- APPLICATION\_FIRST：注册中心有应用级注册信息则订阅应用级信息，否则订阅接口级信息，起到了智能决策来兼容过渡方案。
- FORCE\_APPLICATION：只订阅应用级信息。

到现在提供方完成了启动和注册，消费方完成了启动和订阅，接下来消费方就可以向提供方发起调用了，也就是 **第 ⑥ 步**。

消费方向提供方发起远程调用的环节，调用的代码也非常简单：

```java
// 然后向提供方暴露的 DemoFacade 服务进行远程RPC调用
DemoFacade demoFacade = ctx.getBean(DemoFacade.class);
// 将远程调用返回的结果进行打印输出
System.out.println(demoFacade.sayHello("Geek"));

```

区区两行代码，就跨越了网络从提供方那边拿到了结果，非常方便简单。

不过总有调用不顺畅的时候，尤其是在提供方服务有点耗时的情况下，你可能会遇到这样的异常信息：

```java
Exception in thread "main" org.apache.dubbo.rpc.RpcException: Failed to invoke the method sayHello in the service com.hmilyylimh.cloud.facade.demo.DemoFacade. Tried 3 times of the providers [192.168.100.183:28040] (1/1) from the registry 127.0.0.1:2181 on the consumer 192.168.100.183 using the dubbo version 3.0.7. Last error is: Invoke remote method timeout. method: sayHello, provider: DefaultServiceInstance{serviceName='dubbo-04-xml-boot-provider', host='192.168.100.183', port=28040, enabled=true, healthy=true, metadata={dubbo.endpoints=[{"port":28040,"protocol":"dubbo"}], dubbo.metadata-service.url-params={"connections":"1","version":"1.0.0","dubbo":"2.0.2","release":"3.0.7","side":"provider","port":"28040","protocol":"dubbo"}, dubbo.metadata.revision=7c65b86f6f680876cbb333cb7c92c6f6, dubbo.metadata.storage-type=local}}, service{name='com.hmilyylimh.cloud.facade.demo.DemoFacade',group='null',version='null',protocol='dubbo',params={side=provider, application=dubbo-04-xml-boot-provider, release=3.0.7, methods=sayHello,say, background=false, deprecated=false, dubbo=2.0.2, dynamic=true, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, service-name-mapping=true, generic=false, anyhost=true},}, cause: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-11-12 13:50:44.215, end time: 2022-11-12 13:50:45.229, client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms, request: Request [id=3, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-xml-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=1000}]], channel: /192.168.100.183:57977 -> /192.168.100.183:28040
	at org.apache.dubbo.rpc.cluster.support.FailoverClusterInvoker.doInvoke(FailoverClusterInvoker.java:114)
	at org.apache.dubbo.rpc.cluster.support.AbstractClusterInvoker.invoke(AbstractClusterInvoker.java:340)
	... 36 more
Caused by: java.util.concurrent.ExecutionException: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-11-12 13:50:44.215, end time: 2022-11-12 13:50:45.229, client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms, request: Request [id=3, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-xml-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=1000}]], channel: /192.168.100.183:57977 -> /192.168.100.183:28040
	at java.base/java.util.concurrent.CompletableFuture.reportGet(CompletableFuture.java:395)
	at java.base/java.util.concurrent.CompletableFuture.get(CompletableFuture.java:2093)
	... 24 more
Caused by: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-11-12 13:50:44.215, end time: 2022-11-12 13:50:45.229, client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms, request: Request [id=3, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-xml-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=1000}]], channel: /192.168.100.183:57977 -> /192.168.100.183:28040
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture.doReceived(DefaultFuture.java:212)
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture.received(DefaultFuture.java:176)
	... 29 more

```

首先是 RpcException 远程调用异常，发现 `Tried 3 times` 尝试了 3 次调用仍然拿不到结果。再看 TimeoutException 异常类， `client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms`，提示消费方在有限的 1000ms 时间内未拿到提供方的响应而超时了。

源码中默认的超时时间，可以从这段代码中查看，是 1000ms：

```java
private DefaultFuture(Channel channel, Request request, int timeout) {
    // 省略了其他逻辑代码
    // 源码中 int DEFAULT_TIMEOUT = 1000 是这样的默认值
    // 重点看这里，这里当任何超时时间未设置时，就采用源码中默认的 1000ms 为超时时效
    this.timeout = timeout > 0 ? timeout : channel.getUrl().getPositiveParameter(TIMEOUT_KEY, DEFAULT_TIMEOUT);
    // 省略了其他逻辑代码
}

```

对于这种情况，如果你预估可以稍微把超时时间设置长一点，可以在消费方的Dubbo XML配置文件中，为 DemoFacade 服务添加 `timeout="5000"` 的属性，来达到设置超时时间为5000ms 的目的，即：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" timeout="5000"
        interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>

```

正常情况下5000ms足够了，但有些时候网络抖动延时增大，需要稍微重试几次，你可以继续设置 `retries="3"` 来多重试3次，即：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" timeout="5100" retries="3"
        interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>

```

除了网络抖动影响调用，更多时候可能因为有些服务器故障了，比如消费方调着调着，提供方突然就挂了，消费方如果换台提供方，继续重试调用一下也许就正常了，所以你可以继续设置 `cluster="failover"` 来进行故障转移，比如：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" cluster="failover" timeout="5000" retries="3"
        interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>

```

当然故障转移只是一种手段，目的是当调用环节遇到一些不可预估的故障时，尽可能保证服务的正常运行，就好比这样的调用形式：

![图片](https://static001.geekbang.org/resource/image/79/8f/793b5bc7f73ebf15682ef13c3a98e08f.png?wh=1920x1085)

Dubbo 框架为了尽可能保障运行，除了有 failover 故障转移策略，还有许多的容错策略，我们常用的比如：

![图片](https://static001.geekbang.org/resource/image/ae/4c/ae256185d0af78127a45eda3b0279d4c.jpg?wh=1920x1469)

容错设置帮我们尽可能保障服务稳定调用，但调用也有流量高低之分，流量低的时候可能你发现不了什么特殊情况，一旦流量比较高，你可能会发现提供方总是有那么几台服务器流量特别高，另外几个服务器流量特别低。

这是因为Dubbo默认使用的是 `loadbalance="random"` 随机类型的负载均衡策略，为了尽可能雨露均沾调用到提供方各个节点，你可以继续设置 `loadbalance="roundrobin"` 来进行轮询调用，比如：

```xml
<!-- 引用远程服务 -->
<dubbo:reference id="demoFacade" loadbalance="roundrobin"
        interface="com.hmilyylimh.cloud.facade.demo.DemoFacade">
</dubbo:reference>

```

你发现了吗，一个简单的远程RPC调用，我们在梳理的过程中联想到了各式各样的考量因素。感兴趣的话，你可以研究 <dubbo:reference/>、<dubbo:method/> 这 2 个标签，能发现很多让你意想不到的有趣属性。

到这里调用就完成了，很多人会认为，当消费方能调用提供方就没其他角色什么事了。如果这样想，可就大错特错。我们继续看最后两个关键节点：Registry 注册中心、Monitor 监控中心。

### 4\. Registry 注册中心

前面我们只是新增并注册了一个提供方，当我们逐渐增加节点的时候：

![图片](https://static001.geekbang.org/resource/image/cd/b0/cd66e36fdb6e3196bcd581c400c59bb0.png?wh=1920x842)

提供方节点在增加，/dubbo 和 /services 目录的信息也会随之增多，那消费方怎么知道提供方有新节点增加了呢？

这就需要注册中心出场了。注册中心之所以成为一个注册的集中地带，有着它不可或缺的责任。当服务新增或减少，其实，Dubbo默认的注册中心ZooKeeper有另外一层通知机制，也就是 **第 ⑦ 步。**

比如 DemoFacade 有新的提供方节点启动了，那么 `/dubbo/com.hmilyylimh.cloud.facade.demo.DemoFacade/providers` 目录下会留下新节点的 URL 痕迹，也就相当于 `/dubbo/com.hmilyylimh.cloud.facade.demo.DemoFacade` 目录节点有变更。

ZooKeeper 会将目录节点变更的事件通知给到消费方，然后消费方去 ZooKeeper 中拉取 DemoFacade 最新的所有提供方的节点信息放到消费方的本地，这样消费方就能自动感知新的提供方节点的存在了。

### 5\. Monitor 监控中心

服务调用失败不可避免，当服务的调用成功或者失败时，机器本身或者使用功能的用户是能感知到的，那我们怎么在第一时间察觉某些服务是否出了问题了呢？

![](https://static001.geekbang.org/resource/image/49/fa/4960177e503aaa4f434a0fdf182d7bfa.png?wh=2872x1263)

不管是提供方服务，还是消费方服务，如果在处理调用过程中发生了异常，可以将服务的调用成功数、失败数、服务调用的耗时时间上送给监控中心，也就是 **第 ⑧⑨ 步**。

这样一来，我们通过在监控中心设置不同的告警策略，就能在第一时间感知到一些异常问题的存在，争取在用户上报问题之前尽可能最快解决异常现象。

## 总结

我们通过新建一个Dubbo项目回顾了Dubbo的总体架构，主要有五个角色，Provider 暴露接口提供服务，Consumer 调用已暴露的接口，Registry 管理注册的服务与接口，Monitor 统计服务调用次数和调用时间，Container 为服务的稳定运行提供运行环境。

今天只是把各个环节涉及的基础知识点粗略过了一遍，如果你对每个环节的细节存有疑问，也不用担心，后面我们会深入学习。

![](https://static001.geekbang.org/resource/image/3c/80/3ce4ae4685e533094598a4608aa6dd80.jpg?wh=1920x1136)

这里也总结一下今天涉及的基础知识点，你可以边看边回顾：

![](https://static001.geekbang.org/resource/image/02/01/021e0ae73b79665719fb1419410ef501.jpg?wh=4000x4379)

### 思考题

现在再有人问你Dubbo的总体架构是怎样的，相信你一定能从容回答。还记得今天有一段调用超时的异常信息吗？

```java
Exception in thread "main" org.apache.dubbo.rpc.RpcException: Failed to invoke the method sayHello in the service com.hmilyylimh.cloud.facade.demo.DemoFacade. Tried 3 times of the providers [192.168.100.183:28040] (1/1) from the registry 127.0.0.1:2181 on the consumer 192.168.100.183 using the dubbo version 3.0.7. Last error is: Invoke remote method timeout. method: sayHello, provider: DefaultServiceInstance{serviceName='dubbo-04-xml-boot-provider', host='192.168.100.183', port=28040, enabled=true, healthy=true, metadata={dubbo.endpoints=[{"port":28040,"protocol":"dubbo"}], dubbo.metadata-service.url-params={"connections":"1","version":"1.0.0","dubbo":"2.0.2","release":"3.0.7","side":"provider","port":"28040","protocol":"dubbo"}, dubbo.metadata.revision=7c65b86f6f680876cbb333cb7c92c6f6, dubbo.metadata.storage-type=local}}, service{name='com.hmilyylimh.cloud.facade.demo.DemoFacade',group='null',version='null',protocol='dubbo',params={side=provider, application=dubbo-04-xml-boot-provider, release=3.0.7, methods=sayHello,say, background=false, deprecated=false, dubbo=2.0.2, dynamic=true, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, service-name-mapping=true, generic=false, anyhost=true},}, cause: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-11-12 13:50:44.215, end time: 2022-11-12 13:50:45.229, client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms, request: Request [id=3, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-xml-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=1000}]], channel: /192.168.100.183:57977 -> /192.168.100.183:28040
	at org.apache.dubbo.rpc.cluster.support.FailoverClusterInvoker.doInvoke(FailoverClusterInvoker.java:114)
	at org.apache.dubbo.rpc.cluster.support.AbstractClusterInvoker.invoke(AbstractClusterInvoker.java:340)
	... 36 more
Caused by: java.util.concurrent.ExecutionException: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-11-12 13:50:44.215, end time: 2022-11-12 13:50:45.229, client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms, request: Request [id=3, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-xml-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=1000}]], channel: /192.168.100.183:57977 -> /192.168.100.183:28040
	at java.base/java.util.concurrent.CompletableFuture.reportGet(CompletableFuture.java:395)
	at java.base/java.util.concurrent.CompletableFuture.get(CompletableFuture.java:2093)
	... 24 more
Caused by: org.apache.dubbo.remoting.TimeoutException: Waiting server-side response timeout by scan timer. start time: 2022-11-12 13:50:44.215, end time: 2022-11-12 13:50:45.229, client elapsed: 1 ms, server elapsed: 1013 ms, timeout: 1000 ms, request: Request [id=3, version=2.0.2, twoway=true, event=false, broken=false, data=RpcInvocation [methodName=sayHello, parameterTypes=[class java.lang.String], arguments=[Geek], attachments={path=com.hmilyylimh.cloud.facade.demo.DemoFacade, remote.application=dubbo-04-xml-boot-consumer, interface=com.hmilyylimh.cloud.facade.demo.DemoFacade, version=0.0.0, timeout=1000}]], channel: /192.168.100.183:57977 -> /192.168.100.183:28040
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture.doReceived(DefaultFuture.java:212)
	at org.apache.dubbo.remoting.exchange.support.DefaultFuture.received(DefaultFuture.java:176)
	... 29 more

```

你能从异常信息中搜集出哪些有用的信息？

期待在留言区见到你，02讲文末我会给出今天思考题的参考。如果觉得今天的内容对你有帮助，也欢迎分享给身边的朋友一起讨论。我们下一讲见。

课程的代码仓库 [https://gitee.com/ylimhhmily/GeekDubbo3Tutorial](https://gitee.com/ylimhhmily/GeekDubbo3Tutorial) 。