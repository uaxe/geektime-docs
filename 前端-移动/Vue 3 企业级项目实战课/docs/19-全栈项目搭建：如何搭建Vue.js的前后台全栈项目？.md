你好，我是杨文坚。

前几节课中，我们基于Node.js的Koa.js搭建了Web服务，设计了Node.js项目的前后端分离，学习了如何基于Node.js在服务端渲染Vue.js页面，以及前后端项目如何联动实现Vue.js的同构渲染。数一数你掌握的项目能力，Web服务开发、Node.js服务端分层，Vue.js前端渲染和服务端渲染，看起来前后端能力都有了，应该就是全栈项目吧？

如果从广义上理解，确实已经算是全栈项目了，但是从实际项目角度上分析，还不满足我们课程中运营搭建平台的“全栈”功能需要，比如，还缺少数据存储层的设计、前台和后台的服务隔离设计（这里的前台指的是面向客户的Web服务，后台指的是面向管理员的Web服务）。

这么多新概念，不知道你有没有觉得有点云里雾里的？不用困惑，今天我们会逐一分析，最终搭建出自己的全栈项目。

首先老规矩，先分析一下我们的课程项目，完整的全栈系统设计需要做什么准备？

## 全栈系统设计需要准备什么？

我们最终的项目是实现一个运营搭建平台，需要考虑项目的用户人群。运营搭建平台是给企业员工用的，快速搭建网页，然后把网页输出给客户使用。

那就要考虑两个用户维度：员工、客户。在大厂的项目中，这类场景**需要把平台拆分成两个独立的服务**。拆分主要从“安全”、“稳定”和“便于维护”三个因素考虑的。
<div><strong>精选留言（3）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/15/2f/95/db8dedde.jpg" width="30px"><span>Akili</span> 👍（0） 💬（1）<div>静态文件适合做些配置文件，如果使用静态文件存储动态的数据，需要进行读写文件，效率不高，还有读写静态文件会缺失数据库有的事物、约束、索引等等。</div>2023-02-17</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/26/eb/d7/90391376.jpg" width="30px"><span>ifelse</span> 👍（0） 💬（0）<div>学习打卡</div>2024-09-20</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/14/55/73/7431e82e.jpg" width="30px"><span>冰糖爱白开水</span> 👍（0） 💬（0）<div>运营搭建平台分为前后台，是普遍的实现方案吗？</div>2024-03-12</li><br/>
</ul>