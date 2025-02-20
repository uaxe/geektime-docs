你好，我是何为舟。“Linux系统和应用安全”模块讲完了，今天我通过一篇串讲，带你复习巩固一下这一模块的内容。

在这一模块中，我们重点讲解了，在开发过程中经常要接触或使用的平台、工具的安全功能。这些平台和工具包括：Linux系统、网络、容器、数据库和分布式平台。

那通过对这些平台和工具的安全功能分析，相信你已经知道了，应该如何正确配置和使用这些工具，来避免底层应用出现安全隐患，以防影响整个应用的安全性。

公司中有很多研发和运维人员，他们都在使用和维护自己的系统和应用，那要怎么保证他们都能够去采用最安全的配置呢？

## 重点知识回顾

在解决这个问题之前，我们先来回顾一下，Linux系统、网络、容器、数据库和分布式平台这些平台、工具的安全功能有哪些。

专栏一开始，我说过：安全的本质是数据的CIA，而保护数据CIA的办法就是黄金法则和密码学。因此，在讲解各个平台和工具的安全功能时，我都是以黄金法则和密码学为线索来探讨的。

所以，今天我还是以黄金法则和密码学为线索，带你系统梳理一下本模块的重点内容。希望通过今天的讲解，你能在此基础上总结出自己的学习经验和知识框架。

在之前的课程中，我都详细讲过这些安全功能了，你可以根据我梳理的知识脑图进一步复习巩固。在这里，我就挑一些重点内容着重强调一下。
<div><strong>精选留言（6）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/11/47/31/f35367c8.jpg" width="30px"><span>小晏子</span> 👍（4） 💬（5）<div>看到这个问题先想到了阿里云平台, 已经是非常成熟的平台了，就想它在安全性方面提供了哪些功能呢？
账号的认证授权功能：
阿里云访问控制服务（RAM）为客户提供集中式用户身份管理, 认证以及授权管理功能，使用RAM可以实现账号对应到人，职责分离，最小权限，三权分立等安全管理要求。
审计：这一块功能目前还没有，但是即将提供，叫云操作审计服务，可以将用户阿里云上调用的API操作记录记录下来，并存储在客户指定的OSS Bucket里
加密：用户可以使用云加密服务实现对加密密钥的完全控制和进行加解密操作。
有个问题请教下老师，使用这种公有云平台如何防止提供公有云服务的平台商盗取用户数据的情况，我们的数据基本上都是直接存在rds或者其他一些存储中，理论上平台服务提供商是有后门能进去的，那是不是只能靠商业法律保证了？</div>2020-01-22</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/34/df/64e3d533.jpg" width="30px"><span>leslie</span> 👍（2） 💬（1）<div>我们常用的堡垒机就是一种我们最常见的方式：其中的不少策略就已经被设置好了；私有云其实很早就出现在我们的工作和生活中。私有云中我们经常会用到的策略，在公有云中其实我们都看到了。
今天课程中提到的：认证、加密、审计、授权；我觉得少了一个核心的点-监控，“权限切换这个事情是否能发生，能在什么时候发生？”这个问题如果去研究就能找到一些方式去防范，不过这个环节很难做到合理策略，这块可能就要一定程度后续结合人工智能。</div>2020-02-07</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/8e/b9/740b3563.jpg" width="30px"><span>陈优雅</span> 👍（1） 💬（1）<div>概念明白了，具体的实操来一节课讲下？安全课总想动手实践一下</div>2020-01-22</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1c/f4/f7/871ff71d.jpg" width="30px"><span>Geek_David</span> 👍（1） 💬（0）<div>安全从业者，目前仅仅涉及嵌入式产品的安全，想要扩充一下，感觉这个课挺好</div>2020-03-21</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/92/6d/becd841a.jpg" width="30px"><span>escray</span> 👍（0） 💬（0）<div>从认证、授权、审计、加密这样的框架来分析平台和工具的安全功能，感觉很有条理。

提高平台安全性：

1. 培训

2. 定义安全基线 CIS Benchmarks ，Docker Bench for Security

3. 配置安全镜像

在一开始就分配给开发人员一个符合安全基线的系统

去看了一下 CIS Benchmarks，发现是按照 Cloud Providers, Desktop Software, DevSecOps Tools, Mobile Devices 等类别细分的，能看到 Alibaba Cloud 和 Aliyun Linux，但是没有看到华为。</div>2023-03-09</li><br/><li><img src="https://thirdwx.qlogo.cn/mmopen/vi_32/fFyUqodsJqwevjvtT2DIxiaa9xxDDomYz6Uf2V1GG2Wt5YIzhtiaibHTHoekWOu7ibcRRR0ySVsVFFdqia59iacDXMwQ/132" width="30px"><span>心灵梦幻sky</span> 👍（0） 💬（0）<div>我们公司的linux系统都不用密码的，统一用证书+跳板机结合使用，服务器上的证书只有跳板机自身的，跳板机通过对接ldap来实现用户认证，员工离职直接清除ldap账户就行了</div>2022-08-17</li><br/>
</ul>