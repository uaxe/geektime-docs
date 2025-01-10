你好，我是Tony Bai。

通过上一节课的讲解，我们掌握了Go Module构建模式的基本概念和工作原理，也初步学会了如何通过go mod命令，将一个Go项目转变为一个Go Module，并通过Go Module构建模式进行构建。

但是，围绕一个Go Module，Go开发人员每天要执行很多Go命令对其进行维护。这些维护又是怎么进行的呢？

具体来说，维护Go Module 无非就是对Go Module 依赖包的管理。但在具体工作中还有很多情况，我们接下来会拆分成六个场景，层层深入给你分析。可以说，学好这些是每个Go开发人员成长的必经之路。

我们首先来看一下日常进行Go应用开发时遇到的最为频繁的一个场景： **为当前项目添加一个依赖包**。

## 为当前module添加一个依赖

在一个项目的初始阶段，我们会经常为项目引入第三方包，并借助这些包完成特定功能。即便是项目进入了稳定阶段，随着项目的演进，我们偶尔还需要在代码中引入新的第三方包。

那么我们如何为一个Go Module添加一个新的依赖包呢？

我们还是以上一节课中讲过的module-mode项目为例。如果我们要为这个项目增加一个新依赖：github.com/google/uuid，那需要怎么做呢？

我们首先会更新源码，就像下面代码中这样：

```plain
package main

import (
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

func main() {
	logrus.Println("hello, go module mode")
	logrus.Println(uuid.NewString())
}

```

新源码中，我们通过import语句导入了github.com/google/uuid，并在main函数中调用了uuid包的函数NewString。此时，如果我们直接构建这个module，我们会得到一个错误提示：

```plain
$go build
main.go:4:2: no required module provides package github.com/google/uuid; to add it:
	go get github.com/google/uuid

```

Go编译器提示我们，go.mod里的require段中，没有哪个module提供了github.com/google/uuid包，如果我们要增加这个依赖，可以手动执行go get命令。那我们就来按照提示手工执行一下这个命令：

```plain
$go get github.com/google/uuid
go: downloading github.com/google/uuid v1.3.0
go get: added github.com/google/uuid v1.3.0

```

你会发现，go get命令将我们新增的依赖包下载到了本地module缓存里，并在go.mod文件的require段中新增了一行内容：

```plain
require (
	github.com/google/uuid v1.3.0 //新增的依赖
	github.com/sirupsen/logrus v1.8.1
)

```

这新增的一行表明，我们当前项目依赖的是uuid的v1.3.0版本。我们也可以使用go mod tidy命令，在执行构建前自动分析源码中的依赖变化，识别新增依赖项并下载它们：

```plain
$go mod tidy
go: finding module for package github.com/google/uuid
go: found github.com/google/uuid in github.com/google/uuid v1.3.0

```

对于我们这个例子而言，手工执行go get新增依赖项，和执行go mod tidy自动分析和下载依赖项的最终效果，是等价的。但对于复杂的项目变更而言，逐一手工添加依赖项显然很没有效率，go mod tidy是更佳的选择。

到这里，我们已经了解了怎么为当前的module添加一个新的依赖。但是在日常开发场景中，我们需要对依赖的版本进行更改。那这又要怎么做呢？下面我们就来看看下面升、降级修改依赖版本的场景。

## 升级/降级依赖的版本

我们先以对依赖的版本进行降级为例，分析一下。

在实际开发工作中，如果我们认为Go命令自动帮我们确定的某个依赖的版本存在一些问题，比如，引入了不必要复杂性导致可靠性下降、性能回退等等，我们可以手工将它降级为之前发布的某个兼容版本。

那这个操作依赖于什么原理呢？

答案就是我们上一节课讲过“语义导入版本”机制。我们再来简单复习一下，Go Module的版本号采用了语义版本规范，也就是版本号使用vX.Y.Z的格式。其中X是主版本号，Y为次版本号（minor），Z为补丁版本号（patch）。主版本号相同的两个版本，较新的版本是兼容旧版本的。如果主版本号不同，那么两个版本是不兼容的。

有了语义版本号作为基础和前提，我们就可以从容地手工对依赖的版本进行升降级了，Go命令也可以根据版本兼容性，自动选择出合适的依赖版本了。

我们还是以上面提到过的logrus为例，logrus现在就存在着多个发布版本，我们可以通过下面命令来进行查询：

```plain
$go list -m -versions github.com/sirupsen/logrus
github.com/sirupsen/logrus v0.1.0 v0.1.1 v0.2.0 v0.3.0 v0.4.0 v0.4.1 v0.5.0 v0.5.1 v0.6.0 v0.6.1 v0.6.2 v0.6.3 v0.6.4 v0.6.5 v0.6.6 v0.7.0 v0.7.1 v0.7.2 v0.7.3 v0.8.0 v0.8.1 v0.8.2 v0.8.3 v0.8.4 v0.8.5 v0.8.6 v0.8.7 v0.9.0 v0.10.0 v0.11.0 v0.11.1 v0.11.2 v0.11.3 v0.11.4 v0.11.5 v1.0.0 v1.0.1 v1.0.3 v1.0.4 v1.0.5 v1.0.6 v1.1.0 v1.1.1 v1.2.0 v1.3.0 v1.4.0 v1.4.1 v1.4.2 v1.5.0 v1.6.0 v1.7.0 v1.7.1 v1.8.0 v1.8.1

```

在这个例子中，基于初始状态执行的go mod tidy命令，帮我们选择了logrus的最新发布版本v1.8.1。如果你觉得这个版本存在某些问题，想将logrus版本降至某个之前发布的兼容版本，比如v1.7.0， **那么我们可以在项目的module根目录下，执行带有版本号的go get命令：**

```plain
$go get github.com/sirupsen/logrus@v1.7.0
go: downloading github.com/sirupsen/logrus v1.7.0
go get: downgraded github.com/sirupsen/logrus v1.8.1 => v1.7.0

```

从这个执行输出的结果，我们可以看到，go get命令下载了logrus v1.7.0版本，并将go.mod中对logrus的依赖版本从v1.8.1降至v1.7.0。

当然我们也可以使用万能命令go mod tidy来帮助我们降级，但前提是首先要用go mod edit命令，明确告知我们要依赖v1.7.0版本，而不是v1.8.1，这个执行步骤是这样的：

```plain
$go mod edit -require=github.com/sirupsen/logrus@v1.7.0
$go mod tidy
go: downloading github.com/sirupsen/logrus v1.7.0

```

降级后，我们再假设logrus v1.7.1版本是一个安全补丁升级，修复了一个严重的安全漏洞，而且我们必须使用这个安全补丁版本，这就意味着我们需要将logrus依赖从v1.7.0升级到v1.7.1。

我们可以使用与降级同样的步骤来完成升级，这里我只列出了使用go get实现依赖版本升级的命令和输出结果，你自己动手试一下。

```plain
$go get github.com/sirupsen/logrus@v1.7.1
go: downloading github.com/sirupsen/logrus v1.7.1
go get: upgraded github.com/sirupsen/logrus v1.7.0 => v1.7.1

```

好了，到这里你就学会了如何对项目依赖包的版本进行升降级了。

但是你可能会发现一个问题，在前面的例子中，Go Module的依赖的主版本号都是1。根据我们上节课中学习的语义导入版本的规范，在Go Module构建模式下，当依赖的主版本号为0或1的时候，我们在Go源码中导入依赖包，不需要在包的导入路径上增加版本号，也就是：

```plain
import github.com/user/repo/v0 等价于 import github.com/user/repo
import github.com/user/repo/v1 等价于 import github.com/user/repo

```

但是，如果我们要依赖的module的主版本号大于1，这又要怎么办呢？接着我们就来看看这个场景下该如何去做。

## 添加一个主版本号大于1的依赖

这里，我们还是先来回顾一下，上节课我们讲的语义版本规则中对主版本号大于1情况有没有相应的说明。

有的。语义导入版本机制有一个原则： **如果新旧版本的包使用相同的导入路径，那么新包与旧包是兼容的**。也就是说，如果新旧两个包不兼容，那么我们就应该采用不同的导入路径。

按照语义版本规范，如果我们要为项目引入主版本号大于1的依赖，比如v2.0.0，那么由于这个版本与v1、v0开头的包版本都不兼容，我们在导入v2.0.0包时，不能再直接使用github.com/user/repo，而要使用像下面代码中那样不同的包导入路径：

```plain
import github.com/user/repo/v2/xxx

```

也就是说，如果我们要为Go项目添加主版本号大于1的依赖，我们就需要使用“语义导入版本”机制， **在声明它的导入路径的基础上，加上版本号信息**。我们以“向module-mode项目添加github.com/go-redis/redis依赖包的v7版本”为例，看看添加步骤。

首先，我们在源码中，以空导入的方式导入v7版本的github.com/go-redis/redis包：

```plain
package main

import (
	_ "github.com/go-redis/redis/v7" // “_”为空导入
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

func main() {
	logrus.Println("hello, go module mode")
	logrus.Println(uuid.NewString())
}

```

接下来的步骤就与添加兼容依赖一样，我们通过go get获取redis的v7版本：

```plain
$go get github.com/go-redis/redis/v7
go: downloading github.com/go-redis/redis/v7 v7.4.1
go: downloading github.com/go-redis/redis v6.15.9+incompatible
go get: added github.com/go-redis/redis/v7 v7.4.1

```

我们可以看到，go get为我们选择了go-redis v7版本下当前的最新版本v7.4.1。

不过呢，这里说的是为项目添加一个主版本号大于1的依赖的步骤。有些时候，出于要使用依赖包最新功能特性等原因，我们可能需要将某个依赖的版本升级为其不兼容版本，也就是主版本号不同的版本，这又该怎么做呢？

我们还以go-redis/redis这个依赖为例，将这个依赖从v7版本升级到最新的v8版本看看。

## 升级依赖版本到一个不兼容版本

我们前面说了，按照语义导入版本的原则，不同主版本的包的导入路径是不同的。所以，同样地，我们这里也需要先将代码中redis包导入路径中的版本号改为v8：

```plain
import (
	_ "github.com/go-redis/redis/v8"
	"github.com/google/uuid"
	"github.com/sirupsen/logrus"
)

```

接下来，我们再通过go get来获取v8版本的依赖包：

```plain
$go get github.com/go-redis/redis/v8
go: downloading github.com/go-redis/redis/v8 v8.11.1
go: downloading github.com/dgryski/go-rendezvous v0.0.0-20200823014737-9f7001d12a5f
go: downloading github.com/cespare/xxhash/v2 v2.1.1
go get: added github.com/go-redis/redis/v8 v8.11.1

```

这样，我们就完成了向一个不兼容依赖版本的升级。是不是很简单啊！

但是项目继续演化到一个阶段的时候，我们可能还需要移除对之前某个包的依赖。

## 移除一个依赖

我们还是看前面go-redis/redis示例，如果我们这个时候不需要再依赖go-redis/redis了，你会怎么做呢？

你可能会删除掉代码中对redis的空导入这一行，之后再利用go build命令成功地构建这个项目。

但你会发现，与添加一个依赖时Go命令给出友好提示不同，这次go build没有给出任何关于项目已经将go-redis/redis删除的提示，并且go.mod里require段中的go-redis/redis/v8的依赖依旧存在着。

我们再通过go list命令列出当前module的所有依赖，你也会发现go-redis/redis/v8仍出现在结果中：

```plain
$go list -m all
github.com/bigwhite/module-mode
github.com/cespare/xxhash/v2 v2.1.1
github.com/davecgh/go-spew v1.1.1
... ...
github.com/go-redis/redis/v8 v8.11.1
... ...
gopkg.in/yaml.v2 v2.3.0

```

这是怎么回事呢？

其实，要想彻底从项目中移除go.mod中的依赖项，仅从源码中删除对依赖项的导入语句还不够。这是因为如果源码满足成功构建的条件，go build命令是不会“多管闲事”地清理go.mod中多余的依赖项的。

那正确的做法是怎样的呢？我们还得用go mod tidy命令，将这个依赖项彻底从Go Module构建上下文中清除掉。go mod tidy会自动分析源码依赖，而且将不再使用的依赖从go.mod和go.sum中移除。

到这里，其实我们已经分析了Go Module依赖包管理的5个常见情况了，但其实还有一种特殊情况，需要我们借用vendor机制。

## 特殊情况：使用vendor

你可能会感到有点奇怪，为什么Go Module的维护，还有要用vendor的情况？

其实，vendor机制虽然诞生于GOPATH构建模式主导的年代，但在Go Module构建模式下，它依旧被保留了下来，并且成为了Go Module构建机制的一个很好的补充。特别是在一些不方便访问外部网络，并且对Go应用构建性能敏感的环境，比如在一些内部的持续集成或持续交付环境（CI/CD）中，使用vendor机制可以实现与Go Module等价的构建。

和GOPATH构建模式不同，Go Module构建模式下，我们再也无需手动维护vendor目录下的依赖包了，Go提供了可以快速建立和更新vendor的命令，我们还是以前面的module-mode项目为例，通过下面命令为该项目建立vendor：

```plain
$go mod vendor
$tree -LF 2 vendor
vendor
├── github.com/
│   ├── google/
│   ├── magefile/
│   └── sirupsen/
├── golang.org/
│   └── x/
└── modules.txt

```

我们看到，go mod vendor命令在vendor目录下，创建了一份这个项目的依赖包的副本，并且通过vendor/modules.txt记录了vendor下的module以及版本。

如果我们要基于vendor构建，而不是基于本地缓存的Go Module构建，我们需要在go build后面加上-mod=vendor参数。

在Go 1.14及以后版本中，如果Go项目的顶层目录下存在vendor目录，那么go build默认也会优先基于vendor构建，除非你给go build传入-mod=mod的参数。

## 小结

好了，到这里，我们就完成了维护Go Module的全部常见场景的学习了，现在我们一起来回顾一下吧。

在通过go mod init为当前Go项目创建一个新的module后，随着项目的演进，我们在日常开发过程中，会遇到多种常见的维护Go Module的场景。

其中最常见的就是为项目添加一个依赖包，我们可以通过go get命令手工获取该依赖包的特定版本，更好的方法是通过go mod tidy命令让Go命令自动去分析新依赖并决定使用新依赖的哪个版本。

另外，还有几个场景需要你记住：

- 通过go get我们可以升级或降级某依赖的版本，如果升级或降级前后的版本不兼容，这里千万注意别忘了变化包导入路径中的版本号，这是Go语义导入版本机制的要求；
- 通过go mod tidy，我们可以自动分析Go源码的依赖变更，包括依赖的新增、版本变更以及删除，并更新go.mod中的依赖信息。
- 通过go mod vendor，我们依旧可以支持vendor机制，并且可以对vendor目录下缓存的依赖包进行自动管理。

在了解了如何应对Go Modules维护的日常工作场景后，你是不是有一种再也不担心Go源码构建问题的感觉了呢？

## 思考题

如果你是一个公共Go包的作者，在发布你的Go包时，有哪些需要注意的地方？

感谢你和我一起学习，也欢迎你把这节课分享给更多对Go构建模式感兴趣的朋友。我是Tony Bai，我们下节课见。