你好，我是陈皓，网名左耳朵耗子。

这节课，我们来重点讨论一下，Kubernetes 的 `kubectl` 命令中的使用到的一个编程模式：Visitor（其实， `kubectl` 主要使用到了两个，一个是Builder，另一个是Visitor）。

本来，Visitor 是面向对象设计模式中一个很重要的设计模式（可以看下Wikipedia [Visitor Pattern词条](https://en.wikipedia.org/wiki/Visitor_pattern)），这个模式是将算法与操作对象的结构分离的一种方法。这种分离的实际结果是能够在不修改结构的情况下向现有对象结构添加新操作，是遵循开放/封闭原则的一种方法。这节课，我们重点学习一下 `kubelet` 中是怎么使用函数式的方法来实现这个模式的。

## 一个简单示例

首先，我们来看一个简单设计模式的Visitor的示例。

- 我们的代码中有一个 `Visitor` 的函数定义，还有一个 `Shape` 接口，这需要使用 `Visitor` 函数作为参数。
- 我们的实例的对象 `Circle` 和 `Rectangle` 实现了 `Shape` 接口的 `accept()` 方法，这个方法就是等外面给我们传递一个Visitor。

```
package main

import (
    "encoding/json"
    "encoding/xml"
    "fmt"
)

type Visitor func(shape Shape)

type Shape interface {
    accept(Visitor)
}

type Circle struct {
    Radius int
}

func (c Circle) accept(v Visitor) {
    v(c)
}

type Rectangle struct {
    Width, Heigh int
}

func (r Rectangle) accept(v Visitor) {
    v(r)
}

```

然后，我们实现两个Visitor：一个是用来做JSON序列化的；另一个是用来做XML序列化的。

```
func JsonVisitor(shape Shape) {
    bytes, err := json.Marshal(shape)
    if err != nil {
        panic(err)
    }
    fmt.Println(string(bytes))
}

func XmlVisitor(shape Shape) {
    bytes, err := xml.Marshal(shape)
    if err != nil {
        panic(err)
    }
    fmt.Println(string(bytes))
}

```

下面是使用Visitor这个模式的代码：

```
func main() {
  c := Circle{10}
  r :=  Rectangle{100, 200}
  shapes := []Shape{c, r}

  for _, s := range shapes {
    s.accept(JsonVisitor)
    s.accept(XmlVisitor)
  }

}

```

其实，这段代码的目的就是想解耦数据结构和算法。虽然使用 Strategy 模式也是可以完成的，而且会比较干净， **但是在有些情况下，多个Visitor是来访问一个数据结构的不同部分，这种情况下，数据结构有点像一个数据库，而各个Visitor会成为一个个的小应用。** `kubectl` 就是这种情况。

## Kubernetes相关背景

接下来，我们再来了解一下相关的知识背景。

- Kubernetes抽象了很多种的Resource，比如Pod、ReplicaSet、ConfigMap、Volumes、Namespace、Roles……种类非常繁多，这些东西构成了Kubernetes的数据模型（你可以看看 [Kubernetes Resources 地图](https://github.com/kubernauts/practical-kubernetes-problems/blob/master/images/k8s-resources-map.png) ，了解下有多复杂）。
- `kubectl` 是Kubernetes中的一个客户端命令，操作人员用这个命令来操作Kubernetes。 `kubectl` 会联系到 Kubernetes 的API Server，API Server会联系每个节点上的 `kubelet` ，从而控制每个节点。
- `kubectl` 的主要工作是处理用户提交的东西（包括命令行参数、YAML文件等），接着会把用户提交的这些东西组织成一个数据结构体，发送给 API Server。
- 相关的源代码在 `src/k8s.io/cli-runtime/pkg/resource/visitor.go` 中（ [源码链接](https://github.com/kubernetes/kubernetes/blob/cea1d4e20b4a7886d8ff65f34c6d4f95efcb4742/staging/src/k8s.io/cli-runtime/pkg/resource/visitor.go)）。

`kubectl` 的代码比较复杂，不过，简单来说，基本原理就是 **它从命令行和YAML文件中获取信息，通过Builder模式并把其转成一系列的资源，最后用 Visitor 模式来迭代处理这些Reources**。

下面我们来看看 `kubectl` 的实现。为了简化，我不直接分析复杂的源码，而是用一个小的示例来表明 。

## kubectl的实现方法

### Visitor模式定义

首先， `kubectl` 主要是用来处理 `Info` 结构体，下面是相关的定义：

```
type VisitorFunc func(*Info, error) error

type Visitor interface {
    Visit(VisitorFunc) error
}

type Info struct {
    Namespace   string
    Name        string
    OtherThings string
}
func (info *Info) Visit(fn VisitorFunc) error {
  return fn(info, nil)
}

```

可以看到，

- 有一个 `VisitorFunc` 的函数类型的定义；
- 一个 `Visitor` 的接口，其中需要 `Visit(VisitorFunc) error` 的方法（这就像是我们上面那个例子的 `Shape` ）；
- 最后，为 `Info` 实现 `Visitor` 接口中的 `Visit()` 方法，实现就是直接调用传进来的方法（与前面的例子相仿）。

我们再来定义几种不同类型的 Visitor。

### Name Visitor

这个Visitor 主要是用来访问 `Info` 结构中的 `Name` 和 `NameSpace` 成员：

```
type NameVisitor struct {
  visitor Visitor
}

func (v NameVisitor) Visit(fn VisitorFunc) error {
  return v.visitor.Visit(func(info *Info, err error) error {
    fmt.Println("NameVisitor() before call function")
    err = fn(info, err)
    if err == nil {
      fmt.Printf("==> Name=%s, NameSpace=%s\n", info.Name, info.Namespace)
    }
    fmt.Println("NameVisitor() after call function")
    return err
  })
}

```

可以看到，在这段代码中：

- 声明了一个 `NameVisitor` 的结构体，这个结构体里有一个 `Visitor` 接口成员，这里意味着多态；
- 在实现 `Visit()` 方法时，调用了自己结构体内的那个 `Visitor` 的 `Visitor()` 方法，这其实是一种修饰器的模式，用另一个Visitor修饰了自己（关于修饰器模式，可以复习下 [第113讲](https://time.geekbang.org/column/article/332608)）。

### Other Visitor

这个Visitor主要用来访问 `Info` 结构中的 `OtherThings` 成员：

```
type OtherThingsVisitor struct {
  visitor Visitor
}

func (v OtherThingsVisitor) Visit(fn VisitorFunc) error {
  return v.visitor.Visit(func(info *Info, err error) error {
    fmt.Println("OtherThingsVisitor() before call function")
    err = fn(info, err)
    if err == nil {
      fmt.Printf("==> OtherThings=%s\n", info.OtherThings)
    }
    fmt.Println("OtherThingsVisitor() after call function")
    return err
  })
}

```

实现逻辑同上，我就不再重新讲了。

### Log Visitor

```
type LogVisitor struct {
  visitor Visitor
}

func (v LogVisitor) Visit(fn VisitorFunc) error {
  return v.visitor.Visit(func(info *Info, err error) error {
    fmt.Println("LogVisitor() before call function")
    err = fn(info, err)
    fmt.Println("LogVisitor() after call function")
    return err
  })
}

```

### 使用方代码

现在，我们看看使用上面的代码：

```
func main() {
  info := Info{}
  var v Visitor = &info
  v = LogVisitor{v}
  v = NameVisitor{v}
  v = OtherThingsVisitor{v}

  loadFile := func(info *Info, err error) error {
    info.Name = "Hao Chen"
    info.Namespace = "MegaEase"
    info.OtherThings = "We are running as remote team."
    return nil
  }
  v.Visit(loadFile)
}

```

可以看到，

- Visitor们一层套一层；
- 我用 `loadFile` 假装从文件中读取数据；
- 最后执行 `v.Visit(loadfile)` ，这样，我们上面的代码就全部开始激活工作了。

这段代码输出如下的信息，你可以看到代码是怎么执行起来的：

```
LogVisitor() before call function
NameVisitor() before call function
OtherThingsVisitor() before call function
==> OtherThings=We are running as remote team.
OtherThingsVisitor() after call function
==> Name=Hao Chen, NameSpace=MegaEase
NameVisitor() after call function
LogVisitor() after call function

```

上面的代码有以下几种功效：

- 解耦了数据和程序；
- 使用了修饰器模式；
- 还做出了Pipeline的模式。

所以，其实我们可以重构一下上面的代码。

### Visitor修饰器

我们用 [修饰器模式](https://coolshell.cn/articles/17929.html) 来重构一下上面的代码。

```
type DecoratedVisitor struct {
  visitor    Visitor
  decorators []VisitorFunc
}

func NewDecoratedVisitor(v Visitor, fn ...VisitorFunc) Visitor {
  if len(fn) == 0 {
    return v
  }
  return DecoratedVisitor{v, fn}
}

// Visit implements Visitor
func (v DecoratedVisitor) Visit(fn VisitorFunc) error {
  return v.visitor.Visit(func(info *Info, err error) error {
    if err != nil {
      return err
    }
    if err := fn(info, nil); err != nil {
      return err
    }
    for i := range v.decorators {
      if err := v.decorators[i](info, nil); err != nil {
        return err
      }
    }
    return nil
  })
}

```

这段代码并不复杂，我来解释下。

- 用一个 `DecoratedVisitor` 的结构来存放所有的 `VistorFunc` 函数；
- `NewDecoratedVisitor` 可以把所有的 `VisitorFunc` 转给它，构造 `DecoratedVisitor` 对象；
- `DecoratedVisitor` 实现了 `Visit()` 方法，里面就是来做一个for-loop，顺着调用所有的 `VisitorFunc`。

这样，我们的代码就可以这样运作了：

```
info := Info{}
var v Visitor = &info
v = NewDecoratedVisitor(v, NameVisitor, OtherVisitor)

v.Visit(LoadFile)

```

是不是比之前的那个简单？需要注意的是，这个 `DecoratedVisitor` 同样可以成为一个Visitor来使用。上面的这些代码全部存在于 `kubectl` 的代码中，只要你看懂了这里面的代码逻辑，就一定能看懂 `kubectl` 的代码。

好了，这节课就到这里。如果你觉得今天的内容对你有所帮助，欢迎你帮我分享给更多人。