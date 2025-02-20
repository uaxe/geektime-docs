你好，我是俊达。

数据复制技术是构建MySQL高可用环境的基础，但无论是异步复制，还是半同步复制，在理论上都无法保证极端情况下数据完全一致。MySQL 8.0中的组复制技术（MGR，MySQL Group Replication），使用了基于Paxos 协议的分布式一致性算法，能保证事务在集群中的一致性复制。

这一讲，我们来聊一聊怎么搭建一个MySQL组复制集群，以及组复制中一些常见问题的处理方法。

## MySQL数据复制回顾

我们先来回顾下几种复制架构，这里使用了官方文档中的几个架构图。

- 异步复制

使用默认的异步复制时，主库上的事务提交时，Binlog会异步发送到备库上。由于是异步发送Binlog，因此在主库故障切换时，无法保证备库的数据和主库是完全一致的。

![图片](https://static001.geekbang.org/resource/image/b4/29/b4199759dce8e0846a542aa7c487e529.png?wh=1516x646)

- 半同步复制

使用半同步复制时，主库提交事务时，会先等待Binlog发送给备库。但是这里等待可能会超时，半同步复制会退化成异步复制。

![图片](https://static001.geekbang.org/resource/image/ce/0a/ce8dfd4fa8eeee43a3c3c883793c8b0a.png?wh=1532x652)

- 组复制（Group Replication）

使用组复制时，主库的事务在提交之前，要先将Binlog发送到集群中的每个成员。由于使用了Paxos 协议，各个成员节点看到的事务提交消息的顺序是一致的。MGR支持多主，每个成员都可以独立提交事务。不同节点发起的事务可能会有冲突（比如修改了同一行数据），节点成员需要对事务消息进行冲突检测（certification），没有冲突的事务才能提交，如果事务有冲突，会回滚后执行的事务。