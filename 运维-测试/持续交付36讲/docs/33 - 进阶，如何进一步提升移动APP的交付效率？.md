你好，我是王潇俊。今天我和你分享的主题是：进阶，如何进一步提升移动App的交付效率？

通过我在前面分享的《了解移动App的持续交付生命周期》和《细谈移动App的交付流水线（pipeline）》两个主题，你应该已经比较全面和细致地理解了移动客户端持续交付的整个过程。

当然，搭建持续交付体系的最终目的是，提升研发效率。所以，仅仅能把整个流水线跑起来，肯定满足不了你的胃口。那么，今天我就再和你聊聊，如何进一步提升移动App的交付效率。

## 提升交付效率的基本思路

同其他很多问题的解决方式一样，提升移动App持续交付的效率，也是要先有一个整体思路，再具体落实。

理解了移动App的交付流水线后，你很容易就能发现，它其实与后端服务的交付流水线十分相似。

后端持续交付流水线包括了：代码管理、环境管理、集成和编译管理、测试管理，以及发布管理这五个核心过程。而与之相比，移动App的运行形势决定了其在环境管理方面没有特别多的要求。

所以，我们可以从代码管理、集成和编译管理、测试管理，以及发布管理这四个方面来考虑问题。而将这四个方面直接对应到研发流程的话，就是标准的开发、构建、测试、发布过程。因此，移动App持续交付流水线的优化，我们只要从这四个过程中寻找优化点即可。
<div><strong>精选留言（3）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/10/1c/4b/2e5df06f.jpg" width="30px"><span>三件事</span> 👍（1） 💬（1）<div>老师我想请问下版本分发是怎么做的？是通过 TestFlight 吗？还是把一些测试用户加入到企业证书里？</div>2019-10-15</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/14/99/5b1ed92b.jpg" width="30px"><span>戴斌</span> 👍（0） 💬（1）<div>PC客户端持续交付的场景能否介绍一些经验，如.NET的Windows客户端</div>2020-03-25</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/0f/48/9e/99cb0a7a.jpg" width="30px"><span>心在飞</span> 👍（0） 💬（0）<div>王老师，我们正在尝试用Conan做C++的包管理，包括第三方及自研发的算法库等。我们还会用Artifactory做二进制包的存档。</div>2019-03-07</li><br/>
</ul>