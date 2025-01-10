你好，我是姚秋辰。

上节课我们对Nacos功能体系有了全面的认识。今天我们就来动手搭建Nacos服务注册中心。通过这节课，你可以知道如何搭建一个高可用的Nacos服务集群，以及如何使用MySQL作为Nacos的底层数据存储方案。这些内容可以帮助你理解什么是“高可用架构”。

我们在做系统架构的时候，首要目标就是保障系统的高可用性。不管你的系统架构多么精妙，用的技术多么先进，如果系统的可用性无法得到保障，那么你做什么都是白忙活。

这就像我们的人生一样，事业、家庭、地位都是0，健康才是一串0前面的那个1，没有1则一切皆无。所以，系统的高可用性，就是系统架构层面的那个1。

保障系统的高可用性有两个大道至简的方向。

- **避免单点故障**：在做系统架构的时候，你应该假设任何服务器都有可能挂掉。如果某项任务依赖单一服务资源，那么这就会成为一个“单点”，一旦这个服务资源挂掉就表示整个功能变为不可用。所以你要尽可能消灭一切“单点”；

- **故障机器状态恢复**：尽快将故障机器返回到故障前的状态。对于像Nacos这类中心化注册中心来说，因故障而下线的机器在重新上线后，应该有能力从某个地方获取故障发生前的服务注册列表。


那Nacos是如何解决上面这两个问题，来保证自己的高可用性的呢？很简单，就是构建服务集群。集群环境不仅可以有效规避单点故障引发的问题，同时对于故障恢复的场景来说，重新上线的机器也可以从集群中的其他节点同步数据信息，恢复到故障前的状态。

那么，接下来我就带你手把手搭建Nacos Server的集群环境。

## 下载Nacos Server

Nacos Server的安装包可以从Alibaba官方GitHub中的 [Release页面](https://github.com/alibaba/nacos/releases) 下载。当前最新的稳定版本是2.0.3，我们课程的实战项目也使用该版本的Nacos做为注册中心和配置中心。

在选择Nacos版本的时候你要注意，一定要选择 **稳定版** 使用，不要选择版本号中带有BETA字样的版本（比如2.0.0-BETA）。后者通常是重大版本更新前预发布的试用版，往往会有很多潜在的Bug或者兼容性问题。

Nacos 2.0.3 Release note下方的Assets面板中包含了该版本的下载链接，你可以在nacos-server-2.0.3.tar.gz和nacos-server-2.0.3.zip这两个压缩包中任选一个下载。如果你对Nacos的源码比较感兴趣，也可以下载Source code源码包来学习。

![](https://static001.geekbang.org/resource/image/12/be/12b9e8acf953d20f30c0053yyc0f07be.jpg?wh=2000x807)

下载完成后，你可以在本地将Nacos Server压缩包解压，并将解压后的目录名改为“nacos-cluster1”，再复制一份同样的文件到nacos-cluster2，我们以此来模拟一个由两台Nacos Server组成的集群。

![](https://static001.geekbang.org/resource/image/52/a6/52a819b63e3f0d5281e08de6f99cdca6.jpg?wh=2000x807)

到这里，我们就完成了Nacos服务器的下载安装，接下来，我带你去修改Nacos Server的启动项参数。

## 修改启动项参数

Nacos Server的启动项位于conf目录下的application.properties文件里，别看这个文件里的配置项密密麻麻一大串，但大部分都不用你操心，直接使用默认值就好。你只需要修改这里面的服务启动端口和数据库连接串就好了。

因为你需要在一台机器上同时启动两台Nacos Server来模拟一个集群环境，所以这两台Nacos Server需要使用不同的端口，否则在启动阶段会报出端口冲突的异常信息。

Nacos Server的启动端口由server.port属性指定，默认端口是8848。我们在nacos-cluster1中仍然使用8848作为默认端口，你只需要把nacos-cluster2中的端口号改掉就可以了，这里我把它改为8948。

![](https://static001.geekbang.org/resource/image/ab/4f/abb1736f537681d270bd5a9557ea6b4f.jpg?wh=2000x516)

接下来，你需要对Nacos Server的DB连接串做一些修改。在默认情况下，Nacos Server会使用Derby作为数据源，用于保存配置管理数据。Derby是Apache基金会旗下的一款非常小巧的嵌入式数据库，可以随Nacos Server在本地启动。但从系统的可用性角度考虑，我们需要将Nacos Server的数据源迁移到更加稳定的 **MySQL数据库** 中。

你需要修改三处Nacos Server的数据库配置。

1. **指定数据源**：spring.datasource.platform=mysql这行配置默认情况下被注释掉了，它用来指定数据源为mysql，你需要将这行注释放开；
2. **指定DB实例数**：放开db.num=1这一行的注释；
3. **修改JDBC连接串**：db.url.0指定了数据库连接字符串，我指向了localhost 3306端口的nacos数据库，稍后我将带你对这个数据库做初始化工作；db.user.0和db.password.0分别指定了连接数据库的用户名和密码，我使用了默认的无密码root账户。

下面的图是完整的数据库配置项。

![](https://static001.geekbang.org/resource/image/74/93/7492a76dbc53de8aea7573c620675e93.jpg?wh=2000x1143)

修改完数据库配置项之后，接下来我带你去MySQL中创建Nacos Server所需要用到的数据库Schema和数据库表。

## 创建DB Schema和Table

Nacos Server的数据库用来保存配置信息、Nacos Portal登录用户、用户权限等数据，下面我们分两步来创建数据库。

**第一步，创建Schema**。你可以通过数据库控制台或者DataGrip之类的可视化操作工具，执行下面这行SQL命令，创建一个名为nacos的schema。

```
create schema nacos;

```

**第二步，创建数据库表**。Nacos已经把建表语句准备好了，就放在你解压后的Nacos Server安装目录中。打开Nacos Server安装路径下的conf文件夹，找到里面的nacos-mysql.sql文件，你所需要的数据库建表语句都在这了。你也可以直接到源码仓库的 [资源文件](https://gitee.com/banxian-yao/geekbang-coupon-center/tree/master/%E8%B5%84%E6%BA%90%E6%96%87%E4%BB%B6) 中获取Nacos建表语句的SQL文件。

将文件中的SQL命令复制下来，在第一步中创建的schema下执行这些SQL命令。执行完之后，你就可以在在数据库中看到这些tables了，总共有12张数据库表。

![](https://static001.geekbang.org/resource/image/e7/87/e75b4cd0yye902048406305feabbcf87.jpg?wh=2000x1047)

数据库准备妥当之后，我们还剩最后一项任务：添加集群机器列表。添加成功后就可以完成集群搭建了。

## 添加集群机器列表

Nacos Server可以从一个本地配置文件中获取所有的Server地址信息，从而实现服务器之间的数据同步。

所以现在我们要在Nacos Server的conf目录下创建cluster.conf文件，并将nacos-cluster1和nacos-cluster2这两台服务器的IP地址+端口号添加到文件中。下面是我本地的cluster.conf文件的内容。

```
## 注意，这里的IP不能是localhost或者127.0.0.1
192.168.1.100:8848
192.168.1.100:8948

```

这里需要注意的是，你不能在cluster.conf文件中使用localhost或者127.0.0.1作为服务器IP，否则各个服务器无法在集群环境下同步服务注册信息。这里的IP应该使用你本机分配到的内网IP地址。

如果你使用的是mac或者linux系统，可以在命令行使用 ifconfig \| grep “inet” 命令来获取本机IP地址，下图中红框标出的这行inet地址192.168.1.100就是本机的IP地址。

![](https://static001.geekbang.org/resource/image/c8/65/c87c972be62d4328a8ae5f595a7ff565.jpg?wh=2000x807)

到这里，我们已经完成了所有集群环境的准备工作，接下来我带你去启动Nacos Server验证一下效果。

## 启动Nacos Server

Nacos的启动脚本位于安装目录下的bin文件夹，下图是bin目录下的启动脚本。其中Windows操作系统对应的启动脚本和关闭脚本分别是startup.cmd和shutdown.cmd，Mac和Linux系统对应的启动和关闭脚本是startup.sh和shutdown.sh。

![](https://static001.geekbang.org/resource/image/37/76/375f132670e5a956bf93d0a8aa780776.jpg?wh=2000x1047)

以Mac操作系统为例，如果你希望以单机模式（非集群模式）启动一台Nacos服务器，可以在bin目录下通过命令行执行下面这行命令：

```
 sh startup.sh -m standalone

```

通过-m standalone参数，我指定了服务器以单机模式启动。Nacos Server在单机模式下不会主动向其它服务器同步数据，因此这个模式只能用于开发和测试阶段，对于生产环境来说，我们必须以Cluster模式启动。

如果希望将Nacos Server以集群模式启动，只需要在命令行直接执行sh startup.sh命令就可以了。这时控制台会打印以下两行启动日志。

```
nacos is starting with cluster
nacos is starting，you can check the /Users/banxian/workspace/dev/middleware/nacos-cluster1/logs/start.out

```

这两行启动日志没有告诉你Nacos Server最终是启动成功还是失败，不过你可以在第二行日志中找到一些蛛丝马迹。这行日志告诉了我们启动日志所在的位置是nacos-cluster1/logs/start.out，在启动日志中你可以查看到一行成功消息“Nacos started successfully in cluster mode”。当然了，如果启动失败，你也可以在这里看到具体的Error Log。

![](https://static001.geekbang.org/resource/image/63/6f/631aef2a8a6f741b24bc9430c960666f.jpg?wh=2000x1500)

我们用同样的方式先后启动nacos-cluster1和nacos-cluster2，如上图所示，在启动日志中显示了成功消息“started successfully in cluster mode”，这代表服务器已经成功启动了，接下来你就可以登录Nacos控制台了。

## 登录Nacos控制台

在Nacos的控制台中，我们可以看到服务注册列表、配置项管理、集群服务列表等信息。在浏览器中打开 [nacos-cluster1](http://127.0.0.1:8848/nacos) 或者 [nacos-cluster2](http://127.0.0.1:8948/nacos) 的地址，注意这两台服务器的端口分别是8848和8948。你可以看到下面的Nacos的登录页面。

![](https://static001.geekbang.org/resource/image/e8/56/e8337b81f3d9f59bc3f47fed7c090356.jpg?wh=2000x1296)

你可以使用Nacos默认创建好的用户nacos登录系统，用户名和密码都是nacos。当然了，你也可以在登录后的权限控制->用户列表页面新增系统用户。成功登录后，你就可以看到Nacos控制台首页了。

为了验证集群环境处于正常状态，你可以在左侧导航栏中打开“集群管理”下的“节点列表”页面，在这个页面上显示了集群环境中所有的Nacos Server节点以及对应的状态，在下面的图中我们可以看到192.168.1.100:8848和192.168.1.100:8948两台服务器，并且它们的节点状态都是绿色的“UP”，这表示你搭建的集群环境一切正常。

![](https://static001.geekbang.org/resource/image/59/64/595e5e94382f54c382ae6a7598c63a64.jpg?wh=2000x1008)

好，到这里，我们的Nacos集群环境搭建就完成了。如果你在搭建环境的过程中发现Nacos无法启动，只需要到启动日志/logs/start.out中就能找到具体的报错信息。如果你碰到了启动失败的问题，不妨先去检查以下两个地方：

1. **端口占用**：即server.port所指定的端口已经被使用，你需要更换一个端口重新启动服务；
2. **MySQL连不上**：你需要检查application.properties里配置的MySQL连接信息是否正确，并确认MySQL服务处于运行状态。

如果是其它的异常报错，欢迎发表到评论区，我和热心的同学们都会帮替你诊断的。

## 总结

现在，我们来回顾一下这节课的重点内容。今天我们了解了如何搭建高可用的Nacos集群，在这个过程中，我将底层存储切换成了MySQL数据源，实现了配置项的持久化。

在实际的项目中，如果某个微服务Client要连接到Nacos集群做服务注册，我们并不会把Nacos集群中的所有服务器都配置在Client中，否则每次Nacos集群增加或删除了节点，我都要对所有Client做一次代码变更并重新发布。那么正确的做法是什么呢？

常见的一个做法是提供一个VIP URL给到Client，VIP URL是一个虚拟IP地址，我们可以把真实的Nacos服务器地址列表“隐藏”在虚拟IP后面，客户端只需要连接到虚IP即可，由提供虚IP的组件负责将请求转发给背后的服务器列表。这样一来，即便Nacos集群机器数量发生了变动，也不会对客户端造成任何感知。

提供虚IP的技术手段有很多，比如通过搭建Nginx+LVS或者keepalived技术实现高可用集群。如果你对这些技术感兴趣，我鼓励你尝试自己搭建一个虚IP的环境，锻炼一下技术调研能力。

## 思考题

在开始接下来的实战课之前，我们来做一些课前预习作业。请你从Nacos的 [官方文档](https://nacos.io/zh-cn/docs/what-is-nacos.html) 中了解Nacos的功能特性以及集成方案，欢迎在评论区留下你的自学笔记。

好啦，这节课就结束啦。欢迎你把这节课分享给更多对Spring Cloud感兴趣的朋友。我是姚秋辰，我们下节课再见！