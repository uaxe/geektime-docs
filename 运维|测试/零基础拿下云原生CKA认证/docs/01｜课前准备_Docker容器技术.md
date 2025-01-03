你好，我是雪飞。

要介绍 Kubernetes 技术，我们要从容器技术开始讲起。因为容器技术在云原生技术体系中具有革命性的意义，它可以将应用与底层运行环境进行解耦，让应用能以敏捷的、可扩展的、可复制的方式发布在云上，发挥出云原生的最大能力。

目前，容器技术已经成为云原生应用分发和部署的标准技术，它可以帮我们大大简化繁琐的发布部署环节，提升5~10倍的交付效率。同时，通过 Kubernetes 容器编排来部署大规模微服务应用，已经是互联网和传统行业数字化系统的标配。所以，容器技术是我们学习 Kubernetes 需要打好的第一块基石。

今天这节课，我会带你了解容器技术的相关概念，以及如何使用容器。我希望你学完这节课后能自己动手试一试，亲身体验一下容器技术带来的便捷和高效。

## **为什么要使用容器技术？**

首先问你一个问题，你有没有遇到过这种情况：在测试环境正常运行的程序，却在生产环境中出现一些意想不到的问题。产品、测试人员都找你抱怨，但你也很无奈，明明都是一样的代码、一样的环境，为什么表现出来的不一样呢？

然而定位这种问题有时需要花费大量的时间，到头来可能发现只是两个环境的硬件配置、操作系统、环境变量、依赖软件版本等存在一些细小偏差导致的。如果你对此深有感触，那么恭喜你，你已经能够理解为什么要使用容器技术了。

容器可以帮我们轻松避免这类问题，它把运行应用所需的全部东西，包括依赖项、配置、脚本、二进制文件等，都打包到了镜像中。在容器中运行镜像，就不用再依赖宿主机（应用部署的物理服务器或云服务）上的操作系统和环境配置了，这样我们就不必担心应用在不同环境下运行不一致的问题。

容器在本质上是一个特殊的进程，它通过 Linux 内核的命名空间（Namespaces）、控制组（Cgroups）、切根（chroot）技术，把硬件资源、文件系统、环境配置都划分到了一个独立的空间中，就像是一个集装箱，应用程序和依赖配置就装在这个集装箱里。

部署人员把这个集装箱放在任何宿主机上都能正常运行。当然，这些宿主机上需要有运行容器的容器引擎。目前行业内主流的容器引擎就是 Docker，在后面的课程中，我会以 Docker 为主给你讲解相关的容器知识。

#### 安装 Docker

要使用 Docker 容器引擎，需要先在宿主机上安装 Docker。如果你是个人 PC，可以从 [Docker 官网](https://www.docker.com/get-started/) 下载 Docker 桌面客户端的安装包进行安装，我使用的是 Mac 电脑，安装完成后，软件界面如下图：

![图片](https://static001.geekbang.org/resource/image/cb/ff/cb5d97414515d1cf95eaa3553dd0efff.png?wh=2540x1440)

Docker 安装完成之后，默认使用 Docker Hub 的官方镜像仓库，对于国内下载镜像会很慢，所以我们需要在 Docker 的配置项中增加如下配置，从而使用阿里云提供的镜像库来加速镜像下载。

```bash
 "registry-mirrors": ["https://b9pmyelo.mirror.aliyuncs.com"],

```

![图片](https://static001.geekbang.org/resource/image/61/8f/615a12721ae4deef5a6107f7a7a4768f.png?wh=2540x1440)

这样你就可以通过桌面客户端来使用 Docker，你也可以在 Shell 终端窗口里通过执行 “docker” 相关命令来使用 Docker。我在课程中都是通过命令方式来讲解 Docker 的使用。

#### Docker VS 虚拟机

说到这，其实我们不难看出， **容器主要解决的是跨平台、跨服务器运行环境的问题**，那它和虚拟机技术有什么差别呢？我们来看看下面这张图。

![图片](https://static001.geekbang.org/resource/image/bb/76/bbac7ed12080eab427c6aee3a2383876.jpg?wh=634x364)

可以看到，虚拟机是基于宿主机的操作系统之上，虚拟出一个或多个具备操作系统的虚拟环境。在这种虚拟机上运行应用进程会比较重，因为光是启动虚拟机通常就要花费几分钟的时间。

而使用容器就轻量多了。容器之间共用宿主机操作系统，同一个宿主机上可以同时运行多个容器，每个容器之间相互隔离，互不影响。此外，容器还具备开机秒级、易于移植、易于弹性伸缩等优势。不过，随着容器数量的增多，容器管理的复杂性也会加大，这时候我们就需要用容器编排工具来管理大量容器。

## **什么是容器镜像？**

介绍完容器，我们再来说一下容器镜像。容器镜像（Image）是一个应用打包规范，包含了运行容器所需要的文件集合，我们就是基于镜像来运行容器的。容器与镜像的关系，就如同面向对象编程中对象与类的关系，容器是通过镜像来创建的。

实际上，容器镜像是一种基于联合文件系统的层式结构，由一系列指令一步步构建而来。通常制作镜像并非都要从零开始，我们可以使用别人制作好的镜像文件或者基于别人的镜像文件进行加工。

那具体怎么构建镜像呢？这里要分两种情况。

- 如果你要对正在运行的容器制作镜像，通过 “docker commit” 命令就可以将一个容器打包为镜像。
- 如果你要对自己写好的应用制作镜像，那么就在文件夹里创建 Dockerfile 文件，然后在 Dockerfile 中按步骤编写构建镜像指令，最后通过 “docker build” 命令就能构建出一个镜像。

这里我 **推荐你使用 Dockerfile 文件和 “docker build” 命令构建镜像**。

### **Dockerfile 文件**

我们刚才说，制作镜像需要先有一个 Dockerfile 文件，这个文件就像是一个构建镜像的指令执行脚本。在构建镜像的时候，Docker 程序会自动按照文件中的指令一步步去执行，最终生成一个可以在容器中运行的镜像。那么接下来，我就给你讲一讲如何编写一个 Dockerfile 文件。

Dockerfile 是文本文件，没有后缀名，你可以在项目目录下手动创建一个 Dockerfile 文件。下面是一个前端 VUE 项目的 Dockerfile 文件示例。啰嗦两句，如果你对 VUE 项目及编译运行过程不了解也没关系，这里只是为了展示 Dockerfile 文件的内容和一些常用指令，每行语句我都加了注释，就不再一一解释了。

```bash
# FROM 指令 获取基础镜像，在基础镜像(Base Image)上继续构建，这里的基础镜像是nodejs 12.17版本
FROM node:12.17

# MAINTAINER 指令 指定作者为 myname
MAINTAINER myname

# WORKDIR指令 指定应用工作目录为/app
WORKDIR /app

# COPY指令 将当前根目录的 vue 项目所有文件，都复制到 /app 目录下
COPY . .

# RUN 指令 在构建时执行命令(npm install)，这里 npm install 是安装 vue 项目相关依赖的命令
RUN npm install

# RUN 指令在构建时执行命令(npm build)，这里 npm build 是编译 vue 项目的命令
RUN npm run build

# EXPOSE 指令容器运行时会暴露该端口
EXPOSE 8000

# ENTRYPOINT 指令在容器启动时执行命令(npm run dev)，这里npm run dev是启动运行vue项目的命令
ENTRYPOINT ["npm","run","dev"]

```

通过上面的示例可以发现，Dockerfile 很像是计算机执行指令的脚本文件，只要你按照构建步骤编写指令语句，就能构建出你想要的镜像文件。

当 Dockerfile 文件编写好后，我们在当前目录下执行下面这个命令，就能构建出一个名称为 myvue 、标签为 v1 的应用镜像。

```plain
docker build -t myvue:v1 .

```

这个镜像打包构建完成后就存放在你的本地。然后我们使用这个镜像去运行容器，就可以通过容器访问该 VUE 前端项目了。如果需要其他人也能获取这个镜像，就可以推送到远程的镜像仓库。

### **使用镜像运行容器**

打包构建完成的镜像需要在容器中运行，运行容器镜像有三个步骤：首先，使用 “docker pull” 命令从镜像仓库拉取镜像保存到本地；然后，使用 “docker images” 命令查看本地镜像列表，找到要运行的镜像名称；最后，选择相应的镜像并使用 “docker run” 命令运行容器，命令为：

```bash
docker run [-d] --name=<容器名称>  <镜像名称>

```

其中，-d 表示在后台运行；-name 表示指定一个将要启动的容器的名称；最后是需要运行的镜像名称，镜像名称是在执行构建镜像命令的时候指定的一个名称。

**注意：** 在命令中，<> 表示要填写的参数含义，<\> 及其内部文字都需要替换成你的实际参数。\[\] 表示这个参数不是必须的，根据实际情况决定是否需要这个参数。

为了帮助你更好地理解容器的运行过程，我在这里举一个使用 Nginx 镜像运行容器的例子。Nginx 是一个常用的 HTTP 反向代理 Web 服务器，我们直接使用 Nginx 官方发布的镜像。

**第一步：查找镜像**

我们已经安装好了 Docker，现在从公共镜像库中查找 Ngnix 的镜像。镜像库是一个用来存放构建好的镜像的仓库，我们使用镜像库可以方便地推送和拉取镜像，关于镜像库的详细知识我稍后会讲到。

现在，我们通过 “docker search” 命令搜索镜像，命令使用方式如下：

```bash
[root@localhost ~]# docker search nginx
NAME                                              DESCRIPTION                                     STARS     OFFICIAL   AUTOMATED
nginx                                             Official build of Nginx.                        17244     [OK]
linuxserver/nginx                                 An Nginx container, brought to you by LinuxS…   173
bitnami/nginx                                     Bitnami nginx Docker Image                      139                  [OK]
ubuntu/nginx                                      Nginx, a high-performance reverse proxy & we…   56
bitnami/nginx-ingress-controller                  Bitnami Docker Image for NGINX Ingress Contr…   19                   [OK]
...

```

**第二步：拉取镜像**

通过 “docker pull” 命令拉取镜像到本地。

```bash
[root@localhost ~]# docker pull nginx

```

这时候我们可以用 “docker images” 命令查看一下镜像是否拉取到本地。

```bash
[root@localhost ~]# docker images
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
nginx        latest    f493a2ff2935   12 days ago   135MB

```

有时你会遇到公共镜像库中的镜像无法拉取的情况，这个时候可以使用离线镜像包，我给你提供了一些课程中用到的离线镜像包（ [下载地址](https://pan.baidu.com/s/1LOSuxBjXxC-RY3HA49O3YQ?pwd=nysi)），你下载之后可以使用 “docker load” 命令把 “.tar” 后缀的离线镜像包导入到本地。

```bash
docker load -i <离线镜像文件.tar>

```

**第三步：执行镜像**

如果镜像已被拉取到本地，我们就通过 “docker run” 命令使用指定镜像运行容器，命令使用方式如下：

```bash
[root@localhost ~]# docker run -d -p 80:80 --name myNginx nginx

```

为了便于你理解，其中有几个参数的含义我给你说明一下：

- **-p**：将容器的 80 端口映射到宿主机的 80 端口，这样通过宿主机的 80 端口可以访问到容器的 80 端口。
- **–name**：指定容器的名称为 myNginx。

执行命令后，我们通过 “docker ps” 命令再来查看容器的运行情况。

```bash
[root@localhost ~]# docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                NAMES
28aed831efca   nginx     "/docker-entrypoint.…"   2 minutes ago   Up 2 minutes   0.0.0.0:80->80/tcp   myNginx

```

对于上述显示的结果，我稍微做个解释。

- **CONTAINER ID**：每个容器运行时都会有一个唯一的容器 ID，这个例子中的容器 ID 为28aed831efca，容器 ID 会在管理容器的其他命令中用到。
- **IMAGE**：容器中运行的镜像名称，在这个例子中，容器里运行的是 Nginx 镜像。
- **COMMAND**：容器启动后执行的命令。

**第四步：验证容器运行结果**

最后，我们在浏览器上通过访问本地 IP 和 80 端口（或者直接使用 [http://localhost:80](http://localhost:80)），就能访问到容器中运行的 Nginx 服务。

![图片](https://static001.geekbang.org/resource/image/f7/fd/f7bb3afae2117cba6f40308c9d04d8fd.png?wh=1652x286)

在容器创建成功之后，我们可能还需要对容器或者镜像进行一些停止、删除、查看、进入容器等管理操作，我这里列出了 Docker 的常用命令，你也不需要现在都记下来，我习惯把命令做成这种清单小卡片，用到的时候可以随时查找。

```bash
查看容器详细信息：docker inspect <容器ID> | more
停止容器：docker stop <容器ID>
删除容器：docker rm <容器ID>
删除镜像：docker rmi <镜像名称>

从宿主机复制⽂件到容器⾥：docker cp <源文件> <容器ID:目标目录>
进⼊容器中使用容器的bash：docker exec -it <容器ID> /bin/bash
查看容器⽇志：docker logs -f <容器ID>

```

## **什么是镜像仓库？**

上面在讲 Nginx 例子的时候提到了镜像仓库，现在我们详细了解一下。

镜像仓库（Image Repository）用来集中保存所有创建好的镜像。与之相关联的还有一个概念，叫镜像仓库服务（Docker Registry），它类似于 Git 代码库服务，可以包含多个镜像仓库，主要提供对镜像的管理功能。我们平时都通过镜像仓库服务来推送、拉取和管理仓库中的镜像。

镜像仓库分为两种：私有仓库和公共仓库。私有仓库需要登录验证身份后才可以拉取（pull）和推送（push）镜像；公共仓库则可以无需登录直接拉取（pull）和推送（push）镜像，Docker 默认的官方公共仓库是 [Docker Hub](https://hub.docker.com/)，你可以在这个官方仓库里搜索到想要的镜像。

![图片](https://static001.geekbang.org/resource/image/45/55/45b8048e1516baa693caf88c1d1dbd55.png?wh=1349x985)

你可以使用开源软件例如 Harbor 来搭建私有镜像仓库，也可以使用云厂商提供的镜像仓库。通常，我们会将公有仓库和私有仓库结合起来部署业务应用的容器镜像，具体流程是这样的：先从公共镜像仓库拉取（pull）基础镜像；然后在本地开发环境中，构建好包含业务应用的容器镜像，再推送（push）到自己搭建的私有镜像仓库；接着，我们在测试或正式环境中，从私有镜像仓库中拉取业务应用的容器镜像到测试或正式环境的服务器；最后就可以在服务器上运行容器执行镜像了。

![图片](https://static001.geekbang.org/resource/image/67/54/67202c1f8a5c826e5c929da84628c654.jpg?wh=1158x648)

以上我们介绍了镜像仓库的使用，一般来说，搭建一个私有镜像仓库的步骤比较繁琐，需要考虑镜像仓库的高性能和高可用性，因为一旦镜像仓库发生故障，会直接影响到我们应用的部署和发布流程。

## **小结**

今天我给你讲了容器、镜像和镜像仓库的相关概念，我们再来总结一下。

容器是一种轻量级的虚拟化技术，它将应用及其所有依赖和配置都打包起来与外界隔离，可以快速、可靠、方便地运行在其他宿主机；而容器镜像是一个应用打包规范，包含了运行容器所需要的所有文件集合。容器与镜像的关系，就如同面向对象编程中对象与类之间的关系，需要先有镜像才能创建容器。

这里我推荐使用 Dockerfile 和 “docker build” 命令构建镜像，具体来讲就是在项目中使用特定指令编写 Dockerfile 文件，然后使用 “docker build” 命令来构建容器镜像，最后再用 “docker run” 命令运行容器。

我们创建好的镜像都会保存在镜像仓库中。通过镜像仓库服务，我们可以推送、拉取和管理仓库中的镜像。

在这节课中，我还带你完成了通过容器快速部署 Nginx 镜像的小案例，相信你已经体会到了容器技术的方便快捷。

## 思考题

这就是今天的全部内容，最后留一道练习题给你吧！

在本地安装好 Docker，然后拉取 Apache 的镜像，Apache 应用也是一个 HTTP 的 Web 服务器，它的镜像名称为 httpd，服务端口号也是80端口。最后通过 Docker 运行镜像，看看你是否成功。

欢迎你把过程写到留言区。相信经过练习，会让你对知识的理解更加深刻。