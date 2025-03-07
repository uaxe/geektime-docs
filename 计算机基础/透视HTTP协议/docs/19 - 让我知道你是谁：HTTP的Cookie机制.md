在之前的[第13讲](https://time.geekbang.org/column/article/103270)、[第14讲](https://time.geekbang.org/column/article/103746)中，我曾经说过，HTTP是“无状态”的，这既是优点也是缺点。优点是服务器没有状态差异，可以很容易地组成集群，而缺点就是无法支持需要记录状态的事务操作。

好在HTTP协议是可扩展的，后来发明的Cookie技术，给HTTP增加了“记忆能力”。

## 什么是Cookie？

不知道你有没有看过克里斯托弗·诺兰导演的一部经典电影《记忆碎片》（Memento），里面的主角患有短期失忆症，记不住最近发生的事情。

比如，电影里有个场景，某人刚跟主角说完话，大闹了一通，过了几分钟再回来，主角却是一脸茫然，完全不记得这个人是谁，刚才又做了什么，只能任人摆布。

这种情况就很像HTTP里“无状态”的Web服务器，只不过服务器的“失忆症”比他还要严重，连一分钟的记忆也保存不了，请求处理完立刻就忘得一干二净。即使这个请求会让服务器发生500的严重错误，下次来也会依旧“热情招待”。

如果Web服务器只是用来管理静态文件还好说，对方是谁并不重要，把文件从磁盘读出来发走就可以了。但随着HTTP应用领域的不断扩大，对“记忆能力”的需求也越来越强烈。比如网上论坛、电商购物，都需要“看客下菜”，只有记住用户的身份才能执行发帖子、下订单等一系列会话事务。

那该怎么样让原本无“记忆能力”的服务器拥有“记忆能力”呢？

看看电影里的主角是怎么做的吧。他通过纹身、贴纸条、立拍得等手段，在外界留下了各种记录，一旦失忆，只要看到这些提示信息，就能够在头脑中快速重建起之前的记忆，从而把因失忆而耽误的事情继续做下去。

HTTP的Cookie机制也是一样的道理，既然服务器记不住，那就在外部想办法记住。相当于是服务器给每个客户端都贴上一张小纸条，上面写了一些只有服务器才能理解的数据，需要的时候客户端把这些信息发给服务器，服务器看到Cookie，就能够认出对方是谁了。

## Cookie的工作过程

那么，Cookie这张小纸条是怎么传递的呢？

这要用到两个字段：响应头字段**Set-Cookie**和请求头字段**Cookie**。

当用户通过浏览器第一次访问服务器的时候，服务器肯定是不知道他的身份的。所以，就要创建一个独特的身份标识数据，格式是“**key=value**”，然后放进Set-Cookie字段里，随着响应报文一同发给浏览器。

浏览器收到响应报文，看到里面有Set-Cookie，知道这是服务器给的身份标识，于是就保存起来，下次再请求的时候就自动把这个值放进Cookie字段里发给服务器。

因为第二次请求里面有了Cookie字段，服务器就知道这个用户不是新人，之前来过，就可以拿出Cookie里的值，识别出用户的身份，然后提供个性化的服务。

不过因为服务器的“记忆能力”实在是太差，一张小纸条经常不够用。所以，服务器有时会在响应头里添加多个Set-Cookie，存储多个“key=value”。但浏览器这边发送时不需要用多个Cookie字段，只要在一行里用“;”隔开就行。

我画了一张图来描述这个过程，你看过就能理解了。

![](https://static001.geekbang.org/resource/image/9f/a4/9f6cca61802d65d063e24aa9ca7c38a4.png?wh=2100%2A921)

从这张图中我们也能够看到，Cookie是由浏览器负责存储的，而不是操作系统。所以，它是“浏览器绑定”的，只能在本浏览器内生效。

如果你换个浏览器或者换台电脑，新的浏览器里没有服务器对应的Cookie，就好像是脱掉了贴着纸条的衣服，“健忘”的服务器也就认不出来了，只能再走一遍Set-Cookie流程。

在实验环境里，你可以用Chrome访问URI“/19-1”，实地看一下Cookie工作过程。

首次访问时服务器会设置两个Cookie。

![](https://static001.geekbang.org/resource/image/97/87/974063541e5f9b43893db45ac4ce3687.png?wh=1893%2A821)

然后刷新这个页面，浏览器就会在请求头里自动送出Cookie，服务器就能认出你了。

![](https://static001.geekbang.org/resource/image/da/9f/da9b39d88ddd717a6e3feb6637dc3f9f.png?wh=1598%2A1244)

如果换成Firefox等其他浏览器，因为Cookie是存在Chrome里的，所以服务器就又“蒙圈”了，不知道你是谁，就会给Firefox再贴上小纸条。

## Cookie的属性

说到这里，你应该知道了，Cookie就是服务器委托浏览器存储在客户端里的一些数据，而这些数据通常都会记录用户的关键识别信息。所以，就需要在“key=value”外再用一些手段来保护，防止外泄或窃取，这些手段就是Cookie的属性。

下面这个截图是实验环境“/19-2”的响应头，我来对着这个实际案例讲一下都有哪些常见的Cookie属性。

![](https://static001.geekbang.org/resource/image/9d/5d/9dbb8b490714360475911ca04134df5d.png?wh=2091%2A762)

首先，我们应该**设置Cookie的生存周期**，也就是它的有效期，让它只能在一段时间内可用，就像是食品的“保鲜期”，一旦超过这个期限浏览器就认为是Cookie失效，在存储里删除，也不会发送给服务器。

Cookie的有效期可以使用Expires和Max-Age两个属性来设置。

“**Expires**”俗称“过期时间”，用的是绝对时间点，可以理解为“截止日期”（deadline）。“**Max-Age**”用的是相对时间，单位是秒，浏览器用收到报文的时间点再加上Max-Age，就可以得到失效的绝对时间。

Expires和Max-Age可以同时出现，两者的失效时间可以一致，也可以不一致，但浏览器会优先采用Max-Age计算失效期。

比如在这个例子里，Expires标记的过期时间是“GMT 2019年6月7号8点19分”，而Max-Age则只有10秒，如果现在是6月6号零点，那么Cookie的实际有效期就是“6月6号零点过10秒”。

其次，我们需要**设置Cookie的作用域**，让浏览器仅发送给特定的服务器和URI，避免被其他网站盗用。

作用域的设置比较简单，“**Domain**”和“**Path**”指定了Cookie所属的域名和路径，浏览器在发送Cookie前会从URI中提取出host和path部分，对比Cookie的属性。如果不满足条件，就不会在请求头里发送Cookie。

使用这两个属性可以为不同的域名和路径分别设置各自的Cookie，比如“/19-1”用一个Cookie，“/19-2”再用另外一个Cookie，两者互不干扰。不过现实中为了省事，通常Path就用一个“/”或者直接省略，表示域名下的任意路径都允许使用Cookie，让服务器自己去挑。

最后要考虑的就是**Cookie的安全性**了，尽量不要让服务器以外的人看到。

写过前端的同学一定知道，在JS脚本里可以用document.cookie来读写Cookie数据，这就带来了安全隐患，有可能会导致“跨站脚本”（XSS）攻击窃取数据。

属性“**HttpOnly**”会告诉浏览器，此Cookie只能通过浏览器HTTP协议传输，禁止其他方式访问，浏览器的JS引擎就会禁用document.cookie等一切相关的API，脚本攻击也就无从谈起了。

另一个属性“**SameSite**”可以防范“跨站请求伪造”（XSRF）攻击，设置成“SameSite=Strict”可以严格限定Cookie不能随着跳转链接跨站发送，而“SameSite=Lax”则略宽松一点，允许GET/HEAD等安全方法，但禁止POST跨站发送。

还有一个属性叫“**Secure**”，表示这个Cookie仅能用HTTPS协议加密传输，明文的HTTP协议会禁止发送。但Cookie本身不是加密的，浏览器里还是以明文的形式存在。

Chrome开发者工具是查看Cookie的有力工具，在“Network-Cookies”里可以看到单个页面Cookie的各种属性，另一个“Application”面板里则能够方便地看到全站的所有Cookie。

![](https://static001.geekbang.org/resource/image/a8/9d/a8accc7e1836fa348c2fbd29f494069d.png?wh=3683%2A985)

![](https://static001.geekbang.org/resource/image/37/6e/37fbfef0490a20179c0ee274dccf5e6e.png?wh=2097%2A795)

## Cookie的应用

现在回到我们最开始的话题，有了Cookie，服务器就有了“记忆能力”，能够保存“状态”，那么应该如何使用Cookie呢？

Cookie最基本的一个用途就是**身份识别**，保存用户的登录信息，实现会话事务。

比如，你用账号和密码登录某电商，登录成功后网站服务器就会发给浏览器一个Cookie，内容大概是“name=yourid”，这样就成功地把身份标签贴在了你身上。

之后你在网站里随便访问哪件商品的页面，浏览器都会自动把身份Cookie发给服务器，所以服务器总会知道你的身份，一方面免去了重复登录的麻烦，另一方面也能够自动记录你的浏览记录和购物下单（在后台数据库或者也用Cookie），实现了“状态保持”。

Cookie的另一个常见用途是**广告跟踪**。

你上网的时候肯定看过很多的广告图片，这些图片背后都是广告商网站（例如Google），它会“偷偷地”给你贴上Cookie小纸条，这样你上其他的网站，别的广告就能用Cookie读出你的身份，然后做行为分析，再推给你广告。

这种Cookie不是由访问的主站存储的，所以又叫“第三方Cookie”（third-party cookie）。如果广告商势力很大，广告到处都是，那么就比较“恐怖”了，无论你走到哪里它都会通过Cookie认出你来，实现广告“精准打击”。

为了防止滥用Cookie搜集用户隐私，互联网组织相继提出了DNT（Do Not Track）和P3P（Platform for Privacy Preferences Project），但实际作用不大。

## 小结

今天我们学习了HTTP里的Cookie知识。虽然现在已经出现了多种Local Web Storage技术，能够比Cookie存储更多的数据，但Cookie仍然是最通用、兼容性最强的客户端数据存储手段。

简单小结一下今天的内容：

1. Cookie是服务器委托浏览器存储的一些数据，让服务器有了“记忆能力”；
2. 响应报文使用Set-Cookie字段发送“key=value”形式的Cookie值；
3. 请求报文里用Cookie字段发送多个Cookie值；
4. 为了保护Cookie，还要给它设置有效期、作用域等属性，常用的有Max-Age、Expires、Domain、HttpOnly等；
5. Cookie最基本的用途是身份识别，实现有状态的会话事务。

还要提醒你一点，因为Cookie并不属于HTTP标准（RFC6265，而不是RFC2616/7230），所以语法上与其他字段不太一致，使用的分隔符是“;”，与Accept等字段的“,”不同，小心不要弄错了。

## 课下作业

1. 如果Cookie的Max-Age属性设置为0，会有什么效果呢？
2. Cookie的好处已经很清楚了，你觉得它有什么缺点呢？

欢迎你把自己的学习体会写在留言区，与我和其他同学一起讨论。如果你觉得有所收获，也欢迎把文章分享给你的朋友。

![unpreview](https://static001.geekbang.org/resource/image/f0/97/f03db082760cfa8920b266ce44f52597.png?wh=1769%2A2877)

![unpreview](https://static001.geekbang.org/resource/image/56/63/56d766fc04654a31536f554b8bde7b63.jpg?wh=1110%2A659)
<div><strong>精选留言（15）</strong></div><ul>
<li><span>徐海浪</span> 👍（48） 💬（4）<p>1. 如果 Cookie 的 Max-Age 属性设置为 0，会有什么效果呢？
设置为0，服务器0秒就让Cookie失效，即立即失效，服务器不存Cookie。
2. Cookie 的好处已经很清楚了，你觉得它有什么缺点呢？
好处：方便了市民
缺点：方便了黑客:)</p>2019-07-10</li><br/><li><span>放开那个猴子</span> 👍（37） 💬（15）<p>广告追踪没看明白呀，能否详细讲讲</p>2019-07-10</li><br/><li><span>Geek_66666</span> 👍（28） 💬（2）<p>既然max-age=0会立即失效，那不就等于无记忆了？那干嘛还用cookie？</p>2019-08-15</li><br/><li><span>前端西瓜哥</span> 👍（25） 💬（1）<p>1. （我修改 Lua 文件测试了一下）如果 Max-Age 设置为0，浏览器中该 Cookie 失效，即便这个 Cookie 已存在于浏览器中，且尚未过期。另外 Web 应用开发中，可以通过这种方式消除掉用户的登陆状态，此外记得在服务器的 session 中移除该 cookie 和其对应的用户信息。
2. Cookie 的缺点：
（1） 不安全。如果被中间人获取到 Cookie，完全将它作为用户凭证冒充用户。解决方案是使用 https 进行加密。
（2）有数量和大小限制。另外 Cookie 太大也不好，传输的数据会变大。
（3）客户端可能不会保存 Cookie。比如用 telnet 收发数据，用户禁用浏览器 Cookie 保存功能的情况。</p>2019-07-11</li><br/><li><span>饭饭</span> 👍（18） 💬（1）<p>Max-age：-1 的时候会永久有效吧 ？</p>2019-07-10</li><br/><li><span>WL</span> 👍（16） 💬（3）<p>对于XSS和XSRF一直不是很理解希望老师帮忙解答一下：
1. XSS攻击是指第三方的JS代码读取到浏览器A网站的Cookie然后冒充我去访问A网站吗？
2.XSRF是指浏览器从A网站跳转到B网站是会带上A网站的Cookie吗？这个不是由Domain和Path已经限定了吗？</p>2019-07-10</li><br/><li><span>rongyefeng</span> 👍（13） 💬（1）<p>还有一个属性叫“Secure”，表示这个 Cookie 仅能用 HTTPS 协议加密传输，明文的 HTTP 协议会禁止发送。
但 Cookie 本身不是加密的，浏览器里还是以明文的形式存在。
这里的“ Cookie 本身”怎么理解？</p>2020-05-28</li><br/><li><span>业余草</span> 👍（11） 💬（2）<p>属性“HttpOnly”、“Secure”、“SameSite”很少见，老师可以给几个配套例子，后面答疑篇，可以来个攻防实战！</p>2019-07-10</li><br/><li><span>cp3yqng</span> 👍（6） 💬（1）<p>域名+路径的方式存储cookie，感觉像只有一台业务服务器，那后台如何过分布式系统呢，用户中心是一个系统，核心业务是其他的系统，这里cookie肯定要共享，应该有一级域名和二级域名等等的概念吧，麻烦老师在解释解释。我本人是做移动端开发的，都是自己把token写在网络底层的请求头中，其实核心思想是一样的，但是缺点就是所有的域名里面都带token，这样也不好，好像还有优化的空间。</p>2019-07-10</li><br/><li><span>大小兵</span> 👍（6） 💬（2）<p>要是能把session和token也说一下就好了</p>2019-07-10</li><br/><li><span>业余爱好者</span> 👍（5） 💬（1）<p>1.Max-Age: 是永久有效的意思。 
2.cookie在浏览器端禁用，还有就是安全性，因为在本地是明文存储的</p>2019-07-10</li><br/><li><span>Maske</span> 👍（4） 💬（1）<p>samesite的加入是为了在一定程度上防范CSRF，比如a.com页面中有个恶意表单，提交url为b.com的域名为开头且为银行转账接口地址，且为post请求，用户误操作后会将本地cookie（domain为b.com）发送，导致账户损失，设置samesite为Lax后可避免该cookie的发送，防止该情况出现。</p>2020-06-14</li><br/><li><span>quaeast</span> 👍（4） 💬（2）<p>老师您好，我一只搞不懂cookie和session的区别</p>2020-02-15</li><br/><li><span>許敲敲</span> 👍（4） 💬（1）<p>还有个名词，session 这个适合cookie放在一起的，这个老师能简单解释下嘛？</p>2019-12-26</li><br/><li><span>kissingers</span> 👍（4） 💬（1）<p>哈哈，就是九品芝麻官里的半个烧饼：你后人凭这个来找我</p>2019-12-10</li><br/>
</ul>