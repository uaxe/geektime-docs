作为专栏最后一个模块的答疑文章，我想是时候总结一下Tomcat和Jetty的区别了。专栏里也有同学给我留言，询问有关Tomcat和Jetty在系统选型时需要考虑的地方，今天我也会通过一个实战案例来比较一下Tomcat和Jetty在实际场景下的表现，帮你在做选型时有更深的理解。

我先来概括一下Tomcat和Jetty两者最大的区别。大体来说，Tomcat的核心竞争力是 **成熟稳定**，因为它经过了多年的市场考验，应用也相当广泛，对于比较复杂的企业级应用支持得更加全面。也因为如此，Tomcat在整体结构上比Jetty更加复杂，功能扩展方面可能不如Jetty那么方便。

而Jetty比较年轻，设计上更加 **简洁小巧**，配置也比较简单，功能也支持方便地扩展和裁剪，比如我们可以把Jetty的SessionHandler去掉，以节省内存资源，因此Jetty还可以运行在小型的嵌入式设备中，比如手机和机顶盒。当然，我们也可以自己开发一个Handler，加入Handler链中用来扩展Jetty的功能。值得一提的是，Hadoop和Solr都嵌入了Jetty作为Web服务器。

从设计的角度来看，Tomcat的架构基于一种多级容器的模式，这些容器组件具有父子关系，所有组件依附于这个骨架，而且这个骨架是不变的，我们在扩展Tomcat的功能时也需要基于这个骨架，因此Tomcat在设计上相对来说比较复杂。当然Tomcat也提供了较好的扩展机制，比如我们可以自定义一个Valve，但相对来说学习成本还是比较大的。而Jetty采用Handler责任链模式。由于Handler之间的关系比较松散，Jetty提供HandlerCollection可以帮助开发者方便地构建一个Handler链，同时也提供了ScopeHandler帮助开发者控制Handler链的访问顺序。关于这部分内容，你可以回忆一下专栏里讲的回溯方式的责任链模式。

说了一堆理论，你可能觉得还是有点抽象，接下来我们通过一个实例，来压测一下Tomcat和Jetty，看看在同等流量压力下，Tomcat和Jetty分别表现如何。需要说明的是，通常我们从吞吐量、延迟和错误率这三个方面来比较结果。

测试的计划是这样的，我们还是用 [专栏第36期](http://time.geekbang.org/column/article/112271) 中的Spring Boot应用程序。首先用Spring Boot默认的Tomcat作为内嵌式Web容器，经过一轮压测后，将内嵌式的Web容器换成Jetty，再做一轮测试，然后比较结果。为了方便观察各种指标，我在本地开发机器上做这个实验。

我们会在每个请求的处理过程中休眠1秒，适当地模拟Web应用的I/O等待时间。JMeter客户端的线程数为100，压测持续10分钟。在JMeter中创建一个Summary Report，在这个页面上，可以看到各种统计指标。

![](https://static001.geekbang.org/resource/image/88/b6/888ff5dc207d7bc746663c2be2d3dbb6.png?wh=1911*235)

第一步，压测Tomcat。启动Spring Boot程序和JMeter，持续10分钟，以下是测试结果，结果分为两部分：

**吞吐量、延迟和错误率**

![](https://static001.geekbang.org/resource/image/eb/c9/eb8f119a6106da2ada200a86436df8c9.png?wh=1455*224)

**资源使用情况**

![](https://static001.geekbang.org/resource/image/8a/c6/8ad606fd374a375ccedae71c5eaadcc6.png?wh=1149*650)

第二步，我们将Spring Boot的Web容器替换成Jetty，具体步骤是在pom.xml文件中的spring-boot-starter-web依赖修改下面这样：

```
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>

```

编译打包，启动Spring Boot，再启动JMeter压测，以下是测试结果：

**吞吐量、延迟和错误率**

![](https://static001.geekbang.org/resource/image/16/c6/1613eca65656b08e467eae63238252c6.png?wh=1474*242)

**资源使用情况**

![](https://static001.geekbang.org/resource/image/60/9f/6039f999094dd390bb7a60ec63c5b19f.png?wh=1148*647)

下面我们通过一个表格来对比Tomcat和Jetty：

![](https://static001.geekbang.org/resource/image/82/4f/824b67dbdb1cd7205427ab67a3ab864f.jpg?wh=1248*272)

从表格中的数据我们可以看到：

- **Jetty在吞吐量和响应速度方面稍有优势，并且Jetty消耗的线程和内存资源明显比Tomcat要少，这也恰好说明了Jetty在设计上更加小巧和轻量级的特点。**
- **但是Jetty有2.45%的错误率，而Tomcat没有任何错误，并且我经过多次测试都是这个结果。因此我们可以认为Tomcat比Jetty更加成熟和稳定。**

当然由于测试场景的限制，以上数据并不能完全反映Tomcat和Jetty的真实能力。但是它可以在我们做选型的时候提供一些参考：如果系统的目标是资源消耗尽量少，并且对稳定性要求没有那么高，可以选择轻量级的Jetty；如果你的系统是比较关键的企业级应用，建议还是选择Tomcat比较稳妥。

最后用一句话总结Tomcat和Jetty的区别： **Tomcat好比是一位工作多年比较成熟的工程师，轻易不会出错、不会掉链子，但是他有自己的想法，不会轻易做出改变。而Jetty更像是一位年轻的后起之秀，脑子转得很快，可塑性也很强，但有时候也会犯一点小错误。**

不知道今天的内容你消化得如何？如果还有疑问，请大胆的在留言区提问，也欢迎你把你的课后思考和心得记录下来，与我和其他同学一起讨论。如果你觉得今天有所收获，欢迎你把它分享给你的朋友。