你好，我是文强。

从这节课开始，我们将用两节课的内容来梳理一下 Serverless 、Event（事件）、消息队列三者之间的关系和应用价值。这节课我们就聚焦如何基于 Serverless 架构实现流式处理，下节课会详细分析如何基于消息队列和 Serverless 设计事件驱动架构。

为什么要搞明白上述问题？我们从一张架构图讲起。

![](https://static001.geekbang.org/resource/image/7b/26/7b49facf1a4e7f93ab1edc15656d9d26.jpg?wh=10666x5239)

这是一张消息队列上下游生态的架构图，分为数据源、总线管道、数据目标三部分。可以看到消息队列在架构中处于缓存层，起到的是削峰填谷的缓冲作用。

从技术上看，构建以消息队列为中心的数据流架构，有很多现成的技术方案和开源框架。比如分布式流计算框架 Spark/Flink，开源体系内自带的Kafka Stream、SeaTunnel/DataX 等数据集成产品，或者ELK体系下的采集和数据处理的组件Logstash，都具有处理数据的能力。

然而在上面的架构中，存在一个问题：**每种技术方案所适用的场景不一样，业务一般需要同时使用多种方案，而使用和运维多种方案的成本很高**。

为了解决使用和运维成本问题，接下来我们来学习一种非常实用的方案，那就是基于 Serverless Funciton 实现流式的数据处理。而为了让你对数据流场景有一个更深刻的理解，我们先来看几个业务中常见且典型的数据流场景。