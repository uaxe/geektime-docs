你好，我是郑建勋。

这节课，我们来看看容器化技术，并利用Docker将我们的程序打包为容器。

## 不可阻挡的容器化

大多数应用程序都是在服务器上运行的。过去，我们只能在一台服务器上运行一个应用程序，这带来了巨大的资源浪费，因为机器的资源通常不能被充分地利用。同时，由于程序依赖的资源很多，部署和迁移通常都比较困难。

解决这一问题的一种方法是使用虚拟机技术（VM，Virtual Machine）。虚拟机是对物理硬件的抽象。协调程序的Hypervisor允许多个虚拟机在一台机器上运行。但是，每个 VM 都包含操作系统、应用程序、必要的二进制文件和库的完整副本，这可能占用数十GB。此外，每个操作系统还会额外消耗 CPU、RAM和其他资源。VM 的启动也比较缓慢，难以进行灵活的迁移。

为了应对虚拟机带来的问题，容器化技术应运而生了。容器不需要单独的操作系统，它是应用层的抽象，它将代码和依赖项打包在了一起。多个容器可以在同一台机器上运行，并与其他容器共享操作系统内核。

容器可以共享主机的操作系统，比VM占用的空间更少。这减少了维护资源和操作系统的成本。同时，容器可以快速迁移，便于配置，将容器从本地迁移到云端是轻而易举的事情。
<div><strong>精选留言（3）</strong></div><ul>
<li><img src="" width="30px"><span>Geek_b11a14</span> 👍（1） 💬（1）<div>docker部署的go项目后，容器内生成的日志文件如何同步宿主机。目前添加docker run -v参数后启动容器异常</div>2023-02-08</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1f/b9/f8/c4697160.jpg" width="30px"><span>花酒锄作田</span> 👍（1） 💬（0）<div>思考题：docker可作为k8s的容器运行时。不过新版本的k8s不再直接支持docker，新版本k8s一般采用实现了cri的容器运行时</div>2024-09-04</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/10/7f/d3/b5896293.jpg" width="30px"><span>Realm</span> 👍（1） 💬（1）<div>思考题：docker是k8s的调度对象.</div>2023-02-07</li><br/>
</ul>