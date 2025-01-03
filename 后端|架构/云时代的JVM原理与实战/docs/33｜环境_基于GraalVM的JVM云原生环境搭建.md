你好，我是康杨。

在这个时代，云计算正如早晨的太阳一般，照耀着每个现代企业。而今天，我们要探讨的GraalVM，则是伴随云原生概念而生的新星。它不仅仅是能高效执行Java程序的JVM，更是一种多语言平台，能帮助我们在构建云原生应用时，实现更快启动、更小的内存占用，甚至是跨语言的即时编译能力。今天就让我们基于GraalVM来搭建一个JVM云原生环境搭建，从头开始探索这一技术的奥秘。

## 云原生与GraalVM

GraalVM是一个非常酷的技术，也是Java界的一个明星产品。每一个使用Java编写代码的人都希望它跑得跟闪电一样快。而这就是GraalVM正在做的事情，让Java代码运行得更快、更高效。而且，不只是Java，其他语言也可以享受这种高速体验。下面，我们先来认识下GraalVM的三个核心组件。

### GraalVM核心组件

#### 超级编译器：Graal编译器

首先来说说Graal编译器。你写的Java代码在运行前需要被编译成字节码，JVM再把字节码转换成机器能懂的语言，也就是本地代码。这个过程有点像翻译，你的代码是英文书，而机器需要的是中文版。想象一下如果你问个问题，Graal编译器可以边听边给出答案，而不是等你说完所有话才开始翻译。而这就是Graal编译器动态编译的能力。

传统的JVM在编译时效率有点慢，而Graal编译器像是一位翻译高手，能够在你的程序运行时边翻译边交流，大幅提升速度，它支持AOT和JIT两种编译方式，前面 [第 4 讲](https://time.geekbang.org/column/article/690327) 我们详细讲解过这两种编译方式，你可以回顾一下。

Graal编译器非常聪明，能在各种不同的电脑和操作系统上工作。无论你在Windows上，还是Mac甚至是别的平台，Graal编译器都能确保你的程序以最优秀的状态运行。

#### 语言的搭档：Truffle框架

接下来是Truffle框架。Truffle框架让JVM能够理解和优化多种编程语言。它使用AST（Abstract Syntax Tree，抽象语法树）来表示程序的语法结构，并将其转化为中间表示。在运行时，Truffle根据实际情况动态优化和编译代码，以提高执行性能。这就意味着你可以用不同的语言如Scala、Kotlin来写在JVM上运行的程序，因为Truffle框架能够将它们转化为JVM能够理解和优化的形式。它的灵活性和性能优化可以让你轻松地使用不同的编程语言与JVM进行交互。

Truffle像是一个翻译器的翻译器，让JVM懂得怎么去运行这些不同的语言。如果你擅长某种语言，不必非得跳槽到Java才能写出高效代码。用你自己擅长的语言编写，让Truffle来做后面的转换工作就可以。

#### 构建大师：SubstrateVM

SubstrateVM是构建GraalVM剧场的幕后英雄，提供了一个稳固的基础，让整个GraalVM能在不同的硬件和操作系统上运行。你可以把 SubstrateVM看作是一个特殊的Java运行时，它首先会启动并加载你的应用程序，接着通过调用Graal编译器把这个应用程序和它依赖的所有类库都编译成机器代码。这个过程会生成一个包含了应用程序和所有类库的静态链接的本地执行体，并且这个执行体可以在不需要Java运行时环境的情况下直接运行。

在编译过程中，SubstrateVM会移除应用程序不会用到的代码和数据，包括未使用的类、方法和字段等，这被叫做“死代码消除”，这样可以让生成的代码更加高效，占用的内存更小。

在运行时，SubstrateVM会创建一个轻量级的运行时环境，它包含了Java线程管理、垃圾收集器和一些基本的Java类库。这个轻量级运行时让你可以在没有JVM的情况下运行Java代码，因此可以把SubstrateVM生成的程序运行在任何支持的硬件和操作系统上。

SubstrateVM就像乐高积木，让你可以根据需要组装自己的GraalVM，不管是小玩具项目，还是大型企业级应用，SubstrateVM都能让它稳扎稳打，运行无忧。

这就是GraalVM的神奇之处：一个高速、灵活、多才多艺的Java虚拟机。通过Graal编译器、Truffle框架和SubstrateVM这三个超能力组件的组合，让开发者像运用自己的母语一样编程，打造出更快、更高效的应用程序。而且，这种速度和灵活性不仅限于Java，其他编程语言也同样可以享受。

### 云原生和GraalVM的结合

GraalVM可以优化云原生应用程序的性能和资源使用，它主要通过3种方式实现。

- 通过 **动态编译技术**，GraalVM可以在运行时将字节码编译成本地代码，从而提高程序的执行速度。
- **GraalVM支持多种编程语言**，包括Java、Scala、Kotlin等，这样开发人员就可以选择最适合他们项目的编程语言。
- GraalVM还提供了一个 **用于实现JVM语言的框架Truffle**，这使开发人员可以更轻松地编写云原生应用程序。

## 搭建GraalVM云原生环境

### GraalVM 安装

要在云原生环境中使用GraalVM，我们需要搭建一个GraalVM环境。下面让我们从零开始搭建。

#### 下载并安装GraalVM

首先，我们需要从 [GraalVM 的官方网站](https://www.graalvm.org/) 下载GraalVM的二进制文件。根据你的操作系统选择相应的版本进行下载。下载完成后，解压缩下载的文件，然后将其移动到合适的位置。

#### 配置环境变量

为了能在命令行中使用GraalVM，我们需要将其添加到环境变量中。你可以看一下具体操作。

对于macOS系统，在终端中执行以下命令：

```plain
export PATH=$PATH:/path/to/graalvm/bin

```

对于Windows系统，在命令提示符中执行以下命令：

```plain
set PATH=%PATH%;C:\path\to\graalvm\bin

```

#### 验证安装

为了验证GraalVM是否安装成功，我们可以执行以下命令：

```plain
graalvm-version

```

如果安装成功，你将看到GraalVM的版本信息。

在搭建好GraalVM环境后，我们需要搭建一个云原生环境。下面是一个基于GraalVM的云原生环境搭建步骤，我们一起来看一下。

### 安装Docker

Docker是一个容器化技术，它能够让应用程序在不同的环境中运行，不需要重新配置环境。首先，我们需要在GraalVM环境中安装Docker。根据你的操作系统选择相应的版本进行安装。下面我分别整理了在 Windows、macOS上安装 Docker 的方法，我们一起看一下。

#### Windows 系统

1. 前往 [Docker 官方网站](https://www.docker.com/products/docker-desktop) 下载适用于 Windows 系统的 Docker Desktop 安装程序。
2. 下载完成后，双击运行安装程序，按照安装向导的提示进行操作。
3. 安装过程中，Docker 会要求你登录。如果你没有 Docker 账户，就注册一个。如果你已有 Docker 账户，就使用你的账户登录。
4. 安装完成后，启动 Docker Desktop。
5. 在 Docker Desktop 的主界面中，单击“设置”按钮，然后选择“Docker 守护程序”选项卡。
6. 在“Docker 守护程序”选项卡中，确保“Docker 守护程序”和“Docker 注册表”的地址设置为你的主机 IP 地址。
7. 保存设置并关闭 Docker Desktop。

#### macOS 系统

1. 前往 [Docker 官方网站](https://www.docker.com/products/docker) 下载适用于 macOS 系统的 Docker 安装程序。
2. 下载完成后，双击运行安装程序，按照安装向导的提示进行操作。
3. 安装完成后，启动 Docker。
4. 在 Docker 命令行中，输入以下命令来验证 Docker 是否正常工作。

```plain
docker run hello-world

```

如果 Docker 工作正常，你会看到一条来自 Docker 的欢迎消息。

### 安装Kubernetes

首先，需要确保你的电脑满足安装Kubernetes的环境要求。Kubernetes支持多种操作系统，包括Windows和Mac。但是，你需要确保你的系统版本满足Kubernetes的要求。

#### Windows系统

请确保你的Windows版本是Windows 10 Pro或Enterprise，并且系统上安装了最新的安全补丁。

1. 下载Kubernetes安装文件。你可以从 [Kubernetes 官方网站](https://kubernetes.io/%EF%BC%89%E4%B8%8B%E8%BD%BD%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E7%9A%84%E5%AE%89%E8%A3%85%E6%96%87%E4%BB%B6%E3%80%82) 下载最新版本的安装文件。
2. 解压安装文件。
3. 以管理员身份运行命令提示符。
4. 切换到解压后的目录。
5. 运行 `.\kubernetes-install.ps1` 命令来安装Kubernetes组件。
6. 根据提示完成安装过程。
7. 配置Kubernetes环境变量，将Kubernetes的安装目录添加到系统环境变量中。

```java
export PATH=$PATH:C:\path\to\your\kubernetes\installation\bin
source %USERPROFILE%\AppData\Roaming\npm\etc\profile.d\kube.sh

```

8. 配置Kubernetes命令行工具，将Kubernetes命令行工具的路径添加到系统环境变量中。

#### Mac系统

先确保你的Mac版本是macOS 10.12或更高版本。

1. 安装Homebrew，这是一个用于管理软件包的命令行工具。你可以通过运行以下命令来安装Homebrew：

```java
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```

2. 安装Kubernetes组件。你可以通过运行以下命令来安装Kubernetes组件：

```java
brew install kubernetes-cli

```

3. 安装Kubernetes命令行工具。你可以通过运行以下命令来安装Kubernetes命令行工具：

```java
brew install kubectl

```

4. 安装Kubernetes Dashboard。你可以通过运行以下命令来安装Kubernetes Dashboard：

```java
brew install kubernetes-dashboard

```

5. 配置Kubernetes命令行工具，将Kubernetes命令行工具的路径添加到系统环境变量中。
6. 配置Kubernetes Dashboard，将Kubernetes Dashboard的路径添加到系统环境变量中。

## 创建GraalVM应用

在完成上述步骤后 ，我们可以创建一个基于GraalVM的云原生应用。我们一步一步操作。先创建一个名为“my-graalvm-app”的命名空间。

```java
kubectl create namespace my-graalvm-app

```

然后创建一个名为“my-graalvm-pod”的Pod，其中包含一个GraalVM运行时和一个应用程序容器。你使用下面的命令创建Pod配置文件：

```plain
apiVersion: v1
kind: Pod
metadata:
  name: my-graalvm-pod
  namespace: my-graalvm-app
spec:
  containers:
   - name: graalvm-runtime
     image: graalvm/graalvm-ce:latest
     ports:
     - containerPort: 8080
   - name: my-app
     image: my-app-image
     ports:
     - containerPort: 8081

```

使用下面这行命令应用Pod配置文件：

```plain
kubectl apply -f my-graalvm-pod.yaml

```

现在，你的GraalVM云原生环境已经搭建完成。

```java
>> kubectl get pods  -n my-graalvm-app

```

![图片](https://static001.geekbang.org/resource/image/f7/23/f7fb500b594e7df475b041039f6dd223.png?wh=1116x54)

### 使用GraalVM运行应用程序

在成功创建并部署了基于GraalVM的应用程序后，我们可以使用GraalVM运行这个应用程序。我们看下具体操作。

使用kubectl命令获取Pod的IP地址。

```plain
kubectl get pods -n my-graalvm-app

```

获取Pod的IP地址后，我们可以使用JDK自带的 `jps` 命令查看GraalVM运行时和应用程序容器中的进程。

如果你看到GraalVM运行时和应用程序容器的进程，说明你的应用程序已经在GraalVM环境中成功运行了。

## 重点回顾

GraalVM为云原生应用的时代带来了一种高性能的多语言平台，让你编写的代码像丝绸一样顺滑地在各种硬件和操作系统上运转。这款革命性的JVM在提升启动速度、节省内存使用方面做得非常出色，它不仅支持Java，还有Scala、Kotlin等语言，非常适合现代企业在构建弹性和自动管理能力极强的云原生应用时使用。而且，通过Graal编译器、Truffle框架和SubstrateVM，GraalVM能够让开发变得更灵活、高效，真正做到让你用最喜欢的语言来表达逻辑，同时又能享受极致的性能。

通过今天的介绍，我们成功搭建了一个基于GraalVM的云原生环境，并运行了一个简单的应用程序。在实际生产环境中，你可能需要根据具体需求对GraalVM进行更复杂的配置，例如，配置资源限制、设置安全性等。

## 思考题

学而不思则罔，学完这节课之后，你也来说一说GraalVM的核心组件有哪些？此外你可以自己动手搭建一个GraalVM的云原生应用，然后把自己的代码分享到评论区，如果有收获的话，也欢迎你把这节课的内容分享给需要的朋友，我们下节课再见！