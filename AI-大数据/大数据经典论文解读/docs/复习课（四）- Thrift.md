你好，我是黄金。这次我们要复习的论文内容，是Facebook在2007年发表的这篇Thrift的论文。

## Thrift介绍

2007年前后，随着Facebook的业务发展，流量激增，服务之间的关系变得越来越复杂，他们的工程师开始尝试使用多种编程语言，来提升服务组合的性能、开发的简易性和速度，以及现有库的可用性，他们试图寻找一种透明的、高效的，并且能够沟通不同编程语言的协议框架。不过最后，Facebook并没有找到适合自己口味的开源软件，同时期的Protobuf还处于闭源状态，所以工程师们就开发了Thrift这个项目。

论文中提到，在Facebook内部，Thrift作为搜索服务的协议层和传输层，它允许服务端团队使用高效的C++语言、前端团队使用PHP语言访问搜索服务，允许运维团队使用Python语言获取服务状态信息。另外，Thrift还能用于记录日志、追踪请求的处理。

那么接下来，我们就一起来具体复习下Thrift这个框架。

## 跨语言

首先，作为一种跨语言的序列化协议框架，Thrift需要定义好支持的数据类型，以透明地适配不同语言的类型系统。

在论文中提到，Thrift支持的类型包括了基础类型bool、byte、i16、i32、i64、double、string，容器类型list、set、map，以及结构体类型。一个结构体是由基础类型、容器类型和子结构体组合而成的。一个这样的通用类型系统，让使用者可以灵活地定义协议字段，而不用关心如何适配到不同的语言，以及在对应的语言中如何解析该字段。