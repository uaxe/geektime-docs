这一讲是“破冰篇”的最后一讲，我会先简单地回顾一下之前的内容，然后在Windows系统上实际操作，用几个应用软件搭建出一个“最小化”的HTTP实验环境，方便后续的“基础篇”“进阶篇”“安全篇”的学习。

## “破冰篇”回顾

HTTP协议诞生于30年前，设计之初的目的是用来传输纯文本数据。但由于形式灵活，搭配URI、HTML等技术能够把互联网上的资源都联系起来，构成一个复杂的超文本系统，让人们自由地获取信息，所以得到了迅猛发展。

HTTP有多个版本，目前应用的最广泛的是HTTP/1.1，它几乎可以说是整个互联网的基石。但HTTP/1.1的性能难以满足如今的高流量网站，于是又出现了HTTP/2和HTTP/3。不过这两个新版本的协议还没有完全推广开。在可预见的将来，HTTP/1.1还会继续存在下去。

HTTP翻译成中文是“超文本传输协议”，是一个应用层的协议，通常基于TCP/IP，能够在网络的任意两点之间传输文字、图片、音频、视频等数据。

HTTP协议中的两个端点称为 **请求方** 和 **应答方**。请求方通常就是Web浏览器，也叫user agent，应答方是Web服务器，存储着网络上的大部分静态或动态的资源。

在浏览器和服务器之间还有一些“中间人”的角色，如CDN、网关、代理等，它们也同样遵守HTTP协议，可以帮助用户更快速、更安全地获取资源。

HTTP协议不是一个孤立的协议，需要下层很多其他协议的配合。最基本的是TCP/IP，实现寻址、路由和可靠的数据传输，还有DNS协议实现对互联网上主机的定位查找。

对HTTP更准确的称呼是“ **HTTP over TCP/IP**”，而另一个“ **HTTP over SSL/TLS**”就是增加了安全功能的HTTPS。

## 软件介绍

常言道“实践出真知”，又有俗语“光说不练是假把式”。要研究HTTP协议，最好有一个实际可操作、可验证的环境，通过实际的数据、现象来学习，肯定要比单纯的“动嘴皮子”效果要好的多。

现成的环境当然有，只要能用浏览器上网，就会有HTTP协议，就可以进行实验。但现实的网络环境又太复杂了，有很多无关的干扰因素，这些“噪音”会“淹没”真正有用的信息。

所以，我给你的建议是：搭建一个“ **最小化**”的环境，在这个环境里仅有HTTP协议的两个端点：请求方和应答方，去除一切多余的环节，从而可以抓住重点，快速掌握HTTP的本质。

![](https://static001.geekbang.org/resource/image/85/0b/85cadf90dc96cf413afaf8668689ef0b.png?wh=3000*1681)

简单说一下这个“最小化”环境用到的应用软件：

- Wireshark
- Chrome/Firefox
- Telnet
- OpenResty

**Wireshark** 是著名的网络抓包工具，能够截获在TCP/IP协议栈中传输的所有流量，并按协议类型、地址、端口等任意过滤，功能非常强大，是学习网络协议的必备工具。

它就像是网络世界里的一台“高速摄像机”，把只在一瞬间发生的网络传输过程如实地“拍摄”下来，事后再“慢速回放”，让我们能够静下心来仔细地分析那一瞬到底发生了什么。

**Chrome** 是Google开发的浏览器，是目前的主流浏览器之一。它不仅上网方便，也是一个很好的调试器，对HTTP/1.1、HTTPS、HTTP/2、QUIC等的协议都支持得非常好，用F12打开“开发者工具”还可以非常详细地观测HTTP传输全过程的各种数据。

如果你更习惯使用 **Firefox**，那也没问题，其实它和Chrome功能上都差不太多，选择自己喜欢的就好。

与Wireshark不同，Chrome和Firefox属于“事后诸葛亮”，不能观测HTTP传输的过程，只能看到结果。

**Telnet** 是一个经典的虚拟终端，基于TCP协议远程登录主机，我们可以使用它来模拟浏览器的行为，连接服务器后手动发送HTTP请求，把浏览器的干扰也彻底排除，能够从最原始的层面去研究HTTP协议。

**OpenResty** 你可能比较陌生，它是基于Nginx的一个“强化包”，里面除了Nginx还有一大堆有用的功能模块，不仅支持HTTP/HTTPS，还特别集成了脚本语言Lua简化Nginx二次开发，方便快速地搭建动态网关，更能够当成应用容器来编写业务逻辑。

选择OpenResty而不直接用Nginx的原因是它相当于Nginx的“超集”，功能更丰富，安装部署更方便。我也会用Lua编写一些服务端脚本，实现简单的Web服务器响应逻辑，方便实验。

## 安装过程

这个“最小化”环境的安装过程也比较简单，大约只需要你半个小时不到的时间就能搭建完成。

我在GitHub上为本专栏开了一个项目： [http\_study](https://github.com/chronolaw/http_study.git)，可以直接用“git clone”下载，或者去Release页面，下载打好的 [压缩包](https://github.com/chronolaw/http_study/releases)。

我使用的操作环境是Windows 10，如果你用的是Mac或者Linux，可以用VirtualBox等虚拟机软件安装一个Windows虚拟机，再在里面操作（或者可以到“答疑篇”的 [Linux/Mac实验环境搭建](https://time.geekbang.org/column/article/146833) 中查看搭建方法）。

首先你要获取 **最新** 的http\_study项目源码，假设clone或解压的目录是“D:\\http\_study”，操作完成后大概是下图这个样子。

![](https://static001.geekbang.org/resource/image/86/ee/862511b8ef87f78218631d832927bcee.png?wh=2000*1121)

Chrome和WireShark的安装比较简单，一路按“下一步”就可以了。版本方面使用最新的就好，我的版本可能不是最新的，Chrome是73，WireShark是3.0.0。

Windows 10自带Telnet，不需要安装，但默认是不启用的，需要你稍微设置一下。

打开Windows的设置窗口，搜索“Telnet”，就会找到“启用或关闭Windows功能”，在这个窗口里找到“Telnet客户端”，打上对钩就可以了，可以参考截图。

![](https://static001.geekbang.org/resource/image/1a/47/1af035861c4fd33cb42005eaa1f5f247.png?wh=2000*1121)

接下来我们要安装OpenResty，去它的 [官网](http://openresty.org)，点击左边栏的“Download”，进入下载页面，下载适合你系统的版本（这里我下载的是64位的1.15.8.1，包的名字是“openresty-1.15.8.1-win64.zip”）。

![](https://static001.geekbang.org/resource/image/ee/0a/ee7016fecd79919de550677af32f740a.png?wh=2000*760)

然后要注意，你必须把OpenResty的压缩包解压到刚才的“D:\\http\_study”目录里，并改名为“openresty”。

![](https://static001.geekbang.org/resource/image/5a/b5/5acb89c96041f91bbc747b7e909fd4b5.png?wh=2000*1121)

安装工作马上就要完成了，为了能够让浏览器能够使用DNS域名访问我们的实验环境，还要改一下本机的hosts文件，位置在“C:\\WINDOWS\\system32\\drivers\\etc”，在里面添加三行本机IP地址到测试域名的映射，你也可以参考GitHub项目里的hosts文件，这就相当于在一台物理实机上“托管”了三个虚拟主机。

```
127.0.0.1       www.chrono.com
127.0.0.1       www.metroid.net
127.0.0.1       origin.io

```

注意修改hosts文件需要管理员权限，直接用记事本编辑是不行的，可以切换管理员身份，或者改用其他高级编辑器，比如Notepad++，而且改之前最好做个备份。

到这里，我们的安装工作就完成了！之后你就可以用Wireshark、Chrome、Telnet在这个环境里随意“折腾”，弄坏了也不要紧，只要把目录删除，再来一遍操作就能复原。

## 测试验证

实验环境搭建完了，但还需要把它运行起来，做一个简单的测试验证，看是否运转正常。

首先我们要启动Web服务器，也就是OpenResty。

在http\_study的“www”目录下有四个批处理文件，分别是：

![](https://static001.geekbang.org/resource/image/e5/da/e5d35bb94c46bfaaf8ce5c143b2bb2da.png?wh=2000*1121)

- start：启动OpenResty服务器；
- stop：停止OpenResty服务器；
- reload：重启OpenResty服务器；
- list：列出已经启动的OpenResty服务器进程。

使用鼠标双击“start”批处理文件，就会启动OpenResty服务器在后台运行，这个过程可能会有Windows防火墙的警告，选择“允许”即可。

运行后，鼠标双击“list”可以查看OpenResty是否已经正常启动，应该会有两个nginx.exe的后台进程，大概是下图的样子。

![](https://static001.geekbang.org/resource/image/db/1d/dba34b8a38e98bef92289315db29ee1d.png?wh=2000*661)

有了Web服务器后，接下来我们要运行Wireshark，开始抓包。

因为我们的实验环境运行在本机的127.0.0.1上，也就是loopback“环回”地址。所以，在Wireshark里要选择“Npcap loopback Adapter”，过滤器选择“HTTP TCP port(80)”，即只抓取HTTP相关的数据包。鼠标双击开始界面里的“Npcap loopback Adapter”即可开始抓取本机上的网络数据。

![](https://static001.geekbang.org/resource/image/12/c4/128d8a5ed9cdd666dbfa4e17fd39afc4.png?wh=2000*728)

然后我们打开Chrome，在地址栏输入“ `http://localhost`”，访问刚才启动的OpenResty服务器，就会看到一个简单的欢迎界面，如下图所示。

![](https://static001.geekbang.org/resource/image/d7/88/d7f12d4d480d7100cd9804d2b16b8a88.png?wh=2000*672)

这时再回头去看Wireshark，应该会显示已经抓到了一些数据，就可以用鼠标点击工具栏里的“停止捕获”按钮告诉Wireshark“到此为止”，不再继续抓包。

![](https://static001.geekbang.org/resource/image/f7/79/f7d05a3939d81742f18d2da7a1883179.png?wh=2000*587)

至于这些数据是什么，表示什么含义，我会在下一讲再详细介绍。

如果你能够在自己的电脑上走到这一步，就说明“最小化”的实验环境已经搭建成功了，不要忘了实验结束后运行批处理“stop”停止OpenResty服务器。

## 小结

这次我们学习了如何在自己的电脑上搭建HTTP实验环境，在这里简单小结一下今天的内容。

1. 现实的网络环境太复杂，有很多干扰因素，搭建“最小化”的环境可以快速抓住重点，掌握HTTP的本质；
2. 我们选择Wireshark作为抓包工具，捕获在TCP/IP协议栈中传输的所有流量；
3. 我们选择Chrome或Firefox浏览器作为HTTP协议中的user agent；
4. 我们选择OpenResty作为Web服务器，它是一个Nginx的“强化包”，功能非常丰富；
5. Telnet是一个命令行工具，可用来登录主机模拟浏览器操作；
6. 在GitHub上可以下载到本专栏的专用项目源码，只要把OpenResty解压到里面即可完成实验环境的搭建。

## 课下作业

1.按照今天所学的，在你自己的电脑上搭建出这个HTTP实验环境并测试验证。

2.由于篇幅所限，我无法详细介绍Wireshark，你有时间可以再上网搜索Wireshark相关的资料，了解更多的用法。

欢迎你把自己的学习体会写在留言区，与我和其他同学一起讨论。如果你觉得有所收获，也欢迎把文章分享给你的朋友。

![unpreview](https://static001.geekbang.org/resource/image/03/dd/03727c2a64cbc628ec18cf39a6a526dd.png?wh=1769*3004)

![unpreview](https://static001.geekbang.org/resource/image/56/63/56d766fc04654a31536f554b8bde7b63.jpg?wh=1110*659)