你好，我是鸟窝。

这一讲我来讲一个简单的并发原语：Once。为什么要学习Once呢？我先给你答案： **Once可以用来执行且仅仅执行一次动作，常常用于单例对象的初始化场景。**

那这节课，我们就从对单例对象进行初始化这件事儿说起。

初始化单例资源有很多方法，比如定义package级别的变量，这样程序在启动的时候就可以初始化：

```
package abc

import time

var startTime = time.Now()

```

或者在init函数中进行初始化：

```
package abc

var startTime time.Time

func init() {
  startTime = time.Now()
}

```

又或者在main函数开始执行的时候，执行一个初始化的函数：

```
package abc

var startTime time.Tim

func initApp() {
    startTime = time.Now()
}
func main() {
  initApp()
}

```

这三种方法都是线程安全的，并且后两种方法还可以根据传入的参数实现定制化的初始化操作。

但是很多时候我们是要延迟进行初始化的，所以有时候单例资源的初始化，我们会使用下面的方法：

```
package main

import (
    "net"
    "sync"
    "time"
)

// 使用互斥锁保证线程(goroutine)安全
var connMu sync.Mutex
var conn net.Conn

func getConn() net.Conn {
    connMu.Lock()
    defer connMu.Unlock()

    // 返回已创建好的连接
    if conn != nil {
        return conn
    }

    // 创建连接
    conn, _ = net.DialTimeout("tcp", "baidu.com:80", 10*time.Second)
    return conn
}

// 使用连接
func main() {
    conn := getConn()
    if conn == nil {
        panic("conn is nil")
    }
}

```

这种方式虽然实现起来简单，但是有性能问题。一旦连接创建好，每次请求的时候还是得竞争锁才能读取到这个连接，这是比较浪费资源的，因为连接如果创建好之后，其实就不需要锁的保护了。怎么办呢？

这个时候就可以使用这一讲要介绍的Once并发原语了。接下来我会详细介绍Once的使用、实现和易错场景。

# Once的使用场景

**sync.Once只暴露了一个方法Do，你可以多次调用Do方法，但是只有第一次调用Do方法时f参数才会执行，这里的f是一个无参数无返回值的函数。**

```
func (o *Once) Do(f func())

```

因为当且仅当第一次调用Do方法的时候参数f才会执行，即使第二次、第三次、第n次调用时f参数的值不一样，也不会被执行，比如下面的例子，虽然f1和f2是不同的函数，但是第二个函数f2就不会执行。

```
package main

import (
    "fmt"
    "sync"
)

func main() {
    var once sync.Once

    // 第一个初始化函数
    f1 := func() {
        fmt.Println("in f1")
    }
    once.Do(f1) // 打印出 in f1

    // 第二个初始化函数
    f2 := func() {
        fmt.Println("in f2")
    }
    once.Do(f2) // 无输出
}

```

因为这里的f参数是一个无参数无返回的函数，所以你可能会通过闭包的方式引用外面的参数，比如：

```
    var addr = "baidu.com"

    var conn net.Conn
    var err error

    once.Do(func() {
        conn, err = net.Dial("tcp", addr)
    })

```

而且在实际的使用中，绝大多数情况下，你会使用闭包的方式去初始化外部的一个资源。

你看，Once的使用场景很明确，所以，在标准库内部实现中也常常能看到Once的身影。

比如标准库内部 [cache](https://github.com/golang/go/blob/f0e97546962736fe4aa73b7c7ed590f0134515e1/src/cmd/go/internal/cache/default.go) 的实现上，就使用了Once初始化Cache资源，包括defaultDir值的获取：

```
    func Default() *Cache { // 获取默认的Cache
		defaultOnce.Do(initDefaultCache) // 初始化cache
		return defaultCache
	}

    // 定义一个全局的cache变量，使用Once初始化，所以也定义了一个Once变量
	var (
		defaultOnce  sync.Once
		defaultCache *Cache
	)

    func initDefaultCache() { //初始化cache,也就是Once.Do使用的f函数
		......
		defaultCache = c
	}

    // 其它一些Once初始化的变量，比如defaultDir
    var (
		defaultDirOnce sync.Once
		defaultDir     string
		defaultDirErr  error
	)

```

还有一些测试的时候初始化测试的资源（ [export\_windows\_test](https://github.com/golang/go/blob/50bd1c4d4eb4fac8ddeb5f063c099daccfb71b26/src/time/export_windows_test.go)）：

```
    // 测试window系统调用时区相关函数
    func ForceAusFromTZIForTesting() {
		ResetLocalOnceForTest()
        // 使用Once执行一次初始化
		localOnce.Do(func() { initLocalFromTZI(&aus) })
	}

```

除此之外，还有保证只调用一次copyenv的envOnce，strings包下的Replacer，time包中的 [测试](https://github.com/golang/go/blob/b71eafbcece175db33acfb205e9090ca99a8f984/src/time/export_test.go#L12)，Go拉取库时的 [proxy](https://github.com/golang/go/blob/8535008765b4fcd5c7dc3fb2b73a856af4d51f9b/src/cmd/go/internal/modfetch/proxy.go#L103)，net.pipe，crc64，Regexp，……，数不胜数。我给你重点介绍一下很值得我们学习的 math/big/sqrt.go中实现的一个数据结构，它通过Once封装了一个只初始化一次的值：

```
   // 值是3.0或者0.0的一个数据结构
   var threeOnce struct {
		sync.Once
		v *Float
	}

    // 返回此数据结构的值，如果还没有初始化为3.0，则初始化
	func three() *Float {
		threeOnce.Do(func() { // 使用Once初始化
			threeOnce.v = NewFloat(3.0)
		})
		return threeOnce.v
	}

```

它将sync.Once和\*Float封装成一个对象，提供了只初始化一次的值v。 你看它的three方法的实现，虽然每次都调用threeOnce.Do方法，但是参数只会被调用一次。

当你使用Once的时候，你也可以尝试采用这种结构，将值和Once封装成一个新的数据结构，提供只初始化一次的值。

总结一下Once并发原语解决的问题和使用场景： **Once常常用来初始化单例资源，或者并发访问只需初始化一次的共享资源，或者在测试的时候初始化一次测试资源**。

了解了Once的使用场景，那应该怎样实现一个Once呢？

# 如何实现一个Once？

很多人认为实现一个Once一样的并发原语很简单，只需使用一个flag标记是否初始化过即可，最多是用atomic原子操作这个flag，比如下面的实现：

```
type Once struct {
    done uint32
}

func (o *Once) Do(f func()) {
    if !atomic.CompareAndSwapUint32(&o.done, 0, 1) {
        return
    }
    f()
}

```

这确实是一种实现方式，但是，这个实现有一个很大的问题，就是如果参数f执行很慢的话，后续调用Do方法的goroutine虽然看到done已经设置为执行过了，但是获取某些初始化资源的时候可能会得到空的资源，因为f还没有执行完。

所以， **一个正确的Once实现要使用一个互斥锁，这样初始化的时候如果有并发的goroutine，就会进入doSlow方法**。互斥锁的机制保证只有一个goroutine进行初始化，同时利用 **双检查的机制**（double-checking），再次判断o.done是否为0，如果为0，则是第一次执行，执行完毕后，就将o.done设置为1，然后释放锁。

即使此时有多个goroutine同时进入了doSlow方法，因为双检查的机制，后续的goroutine会看到o.done的值为1，也不会再次执行f。

这样既保证了并发的goroutine会等待f完成，而且还不会多次执行f。

```
type Once struct {
    done uint32
    m    Mutex
}

func (o *Once) Do(f func()) {
    if atomic.LoadUint32(&o.done) == 0 {
        o.doSlow(f)
    }
}

func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    // 双检查
    if o.done == 0 {
        defer atomic.StoreUint32(&o.done, 1)
        f()
    }
}

```

好了，到这里我们就了解了Once的使用场景，很明确，同时呢，也感受到Once的实现也是相对简单的。在实践中，其实很少会出现错误使用Once的情况，但是就像墨菲定律说的，凡是可能出错的事就一定会出错。使用Once也有可能出现两种错误场景，尽管非常罕见。我这里提前讲给你，咱打个预防针。

# 使用Once可能出现的2种错误

## 第一种错误：死锁

你已经知道了Do方法会执行一次f，但是如果f中再次调用这个Once的Do方法的话，就会导致死锁的情况出现。这还不是无限递归的情况，而是的的确确的Lock的递归调用导致的死锁。

```
func main() {
    var once sync.Once
    once.Do(func() {
        once.Do(func() {
            fmt.Println("初始化")
        })
    })
}

```

当然，想要避免这种情况的出现，就不要在f参数中调用当前的这个Once，不管是直接的还是间接的。

## 第二种错误：未初始化

如果f方法执行的时候panic，或者f执行初始化资源的时候失败了，这个时候，Once还是会认为初次执行已经成功了，即使再次调用Do方法，也不会再次执行f。

比如下面的例子，由于一些防火墙的原因，googleConn并没有被正确的初始化，后面如果想当然认为既然执行了Do方法googleConn就已经初始化的话，会抛出空指针的错误：

```
func main() {
    var once sync.Once
    var googleConn net.Conn // 到Google网站的一个连接

    once.Do(func() {
        // 建立到google.com的连接，有可能因为网络的原因，googleConn并没有建立成功，此时它的值为nil
        googleConn, _ = net.Dial("tcp", "google.com:80")
    })
    // 发送http请求
    googleConn.Write([]byte("GET / HTTP/1.1\r\nHost: google.com\r\n Accept: */*\r\n\r\n"))
    io.Copy(os.Stdout, googleConn)
}

```

既然执行过Once.Do方法也可能因为函数执行失败的原因未初始化资源，并且以后也没机会再次初始化资源，那么这种初始化未完成的问题该怎么解决呢？

这里我来告诉你一招独家秘笈，我们可以 **自己实现一个类似Once的并发原语**，既可以返回当前调用Do方法是否正确完成，还可以在初始化失败后调用Do方法再次尝试初始化，直到初始化成功才不再初始化了。

```
// 一个功能更加强大的Once
type Once struct {
    m    sync.Mutex
    done uint32
}
// 传入的函数f有返回值error，如果初始化失败，需要返回失败的error
// Do方法会把这个error返回给调用者
func (o *Once) Do(f func() error) error {
    if atomic.LoadUint32(&o.done) == 1 { //fast path
        return nil
    }
    return o.slowDo(f)
}
// 如果还没有初始化
func (o *Once) slowDo(f func() error) error {
    o.m.Lock()
    defer o.m.Unlock()
    var err error
    if o.done == 0 { // 双检查，还没有初始化
        err = f()
        if err == nil { // 初始化成功才将标记置为已初始化
            atomic.StoreUint32(&o.done, 1)
        }
    }
    return err
}

```

我们所做的改变就是Do方法和参数f函数都会返回error，如果f执行失败，会把这个错误信息返回。

对slowDo方法也做了调整，如果f调用失败，我们不会更改done字段的值，这样后续的goroutine还会继续调用f。如果f执行成功，才会修改done的值为1。

可以说，真是一顿操作猛如虎，我们使用Once有点得心应手的感觉了。等等，还有个问题，我们怎么查询是否初始化过呢？

目前的Once实现可以保证你调用任意次数的once.Do方法，它只会执行这个方法一次。但是，有时候我们需要打一个标记。如果初始化后我们就去执行其它的操作，标准库的Once并不会告诉你是否初始化完成了，只是让你放心大胆地去执行Do方法，所以， **你还需要一个辅助变量，自己去检查是否初始化过了**，比如通过下面的代码中的inited字段：

```
type AnimalStore struct {once   sync.Once;inited uint32}
func (a *AnimalStore) Init() // 可以被并发调用
	a.once.Do(func() {
		longOperationSetupDbOpenFilesQueuesEtc()
		atomic.StoreUint32(&a.inited, 1)
	})
}
func (a *AnimalStore) CountOfCats() (int, error) { // 另外一个goroutine
	if atomic.LoadUint32(&a.inited) == 0 { // 初始化后才会执行真正的业务逻辑
		return 0, NotYetInitedError
	}
        //Real operation
}

```

当然，通过这段代码，我们可以解决这类问题，但是，如果官方的Once类型有Done这样一个方法的话，我们就可以直接使用了。这是有人在Go代码库中提出的一个issue( [#41690](https://github.com/golang/go/issues/41690))。对于这类问题，一般都会被建议采用其它类型，或者自己去扩展。我们可以尝试扩展这个并发原语：

```
// Once 是一个扩展的sync.Once类型，提供了一个Done方法
type Once struct {
    sync.Once
}

// Done 返回此Once是否执行过
// 如果执行过则返回true
// 如果没有执行过或者正在执行，返回false
func (o *Once) Done() bool {
    return atomic.LoadUint32((*uint32)(unsafe.Pointer(&o.Once))) == 1
}

func main() {
    var flag Once
    fmt.Println(flag.Done()) //false

    flag.Do(func() {
        time.Sleep(time.Second)
    })

    fmt.Println(flag.Done()) //true
}

```

好了，到这里关于并发原语Once的内容我讲得就差不多了。最后呢，和你分享一个Once的踩坑案例。

其实啊，使用Once真的不容易犯错，想犯错都很困难，因为很少有人会傻傻地在初始化函数f中递归调用f，这种死锁的现象几乎不会发生。另外如果函数初始化不成功，我们一般会panic，或者在使用的时候做检查，会及早发现这个问题，在初始化函数中加强代码。

所以查看大部分的Go项目，几乎找不到Once的错误使用场景，不过我还是发现了一个。这个issue先从另外一个需求( [go#25955](https://github.com/golang/go/issues/25955))谈起。

# Once的踩坑案例

go#25955有网友提出一个需求，希望Once提供一个Reset方法，能够将Once重置为初始化的状态。比如下面的例子，St通过两个Once控制它的Open/Close状态。但是在Close之后再调用Open的话，不会再执行init函数，因为Once只会执行一次初始化函数。

```
type St struct {
    openOnce *sync.Once
    closeOnce *sync.Once
}

func(st *St) Open(){
    st.openOnce.Do(func() { ... }) // init
    ...
}

func(st *St) Close(){
    st.closeOnce.Do(func() { ... }) // deinit
    ...
}

```

所以提交这个Issue的开发者希望Once增加一个Reset方法，Reset之后再调用once.Do就又可以初始化了。

Go的核心开发者Ian Lance Taylor给他了一个简单的解决方案。在这个例子中，只使用一个ponce \*sync.Once 做初始化，Reset的时候给ponce这个变量赋值一个新的Once实例即可(ponce = new(sync.Once))。Once的本意就是执行一次，所以Reset破坏了这个并发原语的本意。

这个解决方案一点都没问题，可以很好地解决这位开发者的需求。Docker较早的版本（1.11.2）中使用了它们的一个网络库libnetwork，这个网络库在使用Once的时候就使用Ian Lance Taylor介绍的方法，但是不幸的是，它的Reset方法中又改变了Once指针的值，导致程序panic了。原始逻辑比较复杂，一个简化版可重现的 [代码](https://play.golang.org/p/xPULnrVKiY) 如下：

```
package main

import (
	"fmt"
	"sync"
	"time"
)

// 一个组合的并发原语
type MuOnce struct {
	sync.RWMutex
	sync.Once
	mtime time.Time
	vals  []string
}

// 相当于reset方法，会将m.Once重新复制一个Once
func (m *MuOnce) refresh() {
	m.Lock()
	defer m.Unlock()
	m.Once = sync.Once{}
	m.mtime = time.Now()
	m.vals = []string{m.mtime.String()}
}

// 获取某个初始化的值，如果超过某个时间，会reset Once
func (m *MuOnce) strings() []string {
	now := time.Now()
	m.RLock()
	if now.After(m.mtime) {
		defer m.Do(m.refresh) // 使用refresh函数重新初始化
	}
	vals := m.vals
	m.RUnlock()
	return vals
}

func main() {
	fmt.Println("Hello, playground")
	m := new(MuOnce)
	fmt.Println(m.strings())
	fmt.Println(m.strings())
}

```

如果你执行这段代码就会panic:

![](https://static001.geekbang.org/resource/image/f3/af/f3401f75a86e1d0c3b257f52696228af.png?wh=1323*482)

原因在于第31行执行m.Once.Do方法的时候，使用的是m.Once的指针，然后调用m.refresh，在执行m.refresh的时候Once内部的Mutex首先会加锁（可以再翻看一下这一讲的Once的实现原理）， 但是，在refresh中更改了Once指针的值之后，结果在执行完refresh释放锁的时候，释放的是一个刚初始化未加锁的Mutex，所以就panic了。

如果你还不太明白，我再给你简化成一个更简单的例子：

```
package main

import (
    "sync"
)

type Once struct {
    m sync.Mutex
}

func (o *Once) doSlow() {
    o.m.Lock()
    defer o.m.Unlock()

    // 这里更新的o指针的值!!!!!!!, 会导致上一行Unlock出错
    *o = Once{}
}

func main() {
    var once Once
    once.doSlow()
}

```

doSlow方法就演示了这个错误。Ian Lance Taylor介绍的Reset方法没有错误，但是你在使用的时候千万别再初始化函数中Reset这个Once，否则势必会导致Unlock一个未加锁的Mutex的错误。

总的来说，这还是对Once的实现机制不熟悉，又进行复杂使用导致的错误。不过最新版的libnetwork相关的地方已经去掉了Once的使用了。所以，我带你一起来看这个案例，主要目的还是想巩固一下我们对Once的理解。

# 总结

今天我们一起学习了Once，我们常常使用它来实现单例模式。

单例是23种设计模式之一，也是常常引起争议的设计模式之一，甚至有人把它归为反模式。为什么说它是反模式呢，我拿标准库中的单例模式给你介绍下。

因为Go没有immutable类型，导致我们声明的全局变量都是可变的，别的地方或者第三方库可以随意更改这些变量。比如package io中定义了几个全局变量，比如io.EOF：

```
var EOF = errors.New("EOF")

```

因为它是一个package级别的变量，我们可以在程序中偷偷把它改了，这会导致一些依赖io.EOF这个变量做判断的代码出错。

```
io.EOF = errors.New("我们自己定义的EOF")

```

从我个人的角度来说，一些单例（全局变量）的确很方便，比如Buffer池或者连接池，所以有时候我们也不要谈虎色变。虽然有人把单例模式称之为反模式，但毕竟只能代表一部分开发者的观点，否则也不会把它列在23种设计模式中了。

如果你真的担心这个package级别的变量被人修改，你可以不把它们暴露出来，而是提供一个只读的GetXXX的方法，这样别人就不会进行修改了。

而且，Once不只应用于单例模式，一些变量在也需要在使用的时候做延迟初始化，所以也是可以使用Once处理这些场景的。

总而言之，Once的应用场景还是很广泛的。 **一旦你遇到只需要初始化一次的场景，首先想到的就应该是Once并发原语。**

![](https://static001.geekbang.org/resource/image/4b/ba/4b1721a63d7bd3f3995eb18cee418fba.jpg?wh=2250*880)

# 思考题

1. 我已经分析了几个并发原语的实现，你可能注意到总是有些slowXXXX的方法，从XXXX方法中单独抽取出来，你明白为什么要这么做吗，有什么好处？

2. Once在第一次使用之后，还能复制给其它变量使用吗？


欢迎在留言区写下你的思考和答案，我们一起交流讨论。如果你觉得有所收获，也欢迎你把今天的内容分享给你的朋友或同事。