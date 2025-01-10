你好，我是鸟窝。

在这节课正式开始之前，我想先带你看一个工作中的场景。

假设有一天你进入办公室，突然同事们都围住你，然后大喊“小王小王你最帅”，此时你可能一头雾水，只能尴尬地笑笑。为啥呢？因为你缺少上下文的信息，不知道之前发生了什么。

但是，如果同事告诉你，由于你业绩突出，一天之内就把云服务化的主要架构写好了，因此被评为9月份的工作之星，总经理还特意给你发1万元的奖金，那么，你心里就很清楚了，原来同事恭喜你，是因为你的工作被表扬了，还获得了奖金。同事告诉你的这些前因后果，就是上下文信息，他把上下文传递给你，你接收后，就可以获取之前不了解的信息。

你看，上下文（Context）就是这么重要。在我们的开发场景中，上下文也是不可或缺的，缺少了它，我们就不能获取完整的程序信息。那到底啥是上下文呢？其实，这就是指，在API之间或者方法调用之间，所传递的除了业务参数之外的额外信息。

比如，服务端接收到客户端的HTTP请求之后，可以把客户端的IP地址和端口、客户端的身份信息、请求接收的时间、Trace ID等信息放入到上下文中，这个上下文可以在后端的方法调用中传递，后端的业务方法除了利用正常的参数做一些业务处理（如订单处理）之外，还可以从上下文读取到消息请求的时间、Trace ID等信息，把服务处理的时间推送到Trace服务中。Trace服务可以把同一Trace ID的不同方法的调用顺序和调用时间展示成流程图，方便跟踪。

不过，Go标准库中的Context功能还不止于此，它还提供了超时（Timeout）和取消（Cancel）的机制，下面就让我一一道来。

# Context的来历

在学习Context的功能之前呢，我先带你了解下它的来历。毕竟，知道了它的来龙去脉，我们才能应用得更加得心应手一些。

Go在1.7的版本中才正式把Context加入到标准库中。在这之前，很多Web框架在定义自己的handler时，都会传递一个自定义的Context，把客户端的信息和客户端的请求信息放入到Context中。Go最初提供了golang.org/x/net/context库用来提供上下文信息，最终还是在Go1.7中把此库提升到标准库context包中。

为啥呢？这是因为，在Go1.7之前，有很多库都依赖golang.org/x/net/context中的Context实现，这就导致Go 1.7发布之后，出现了标准库Context和golang.org/x/net/context并存的状况。新的代码使用标准库Context的时候，没有办法使用这个标准库的Context去调用旧有的使用x/net/context实现的方法。

所以，在Go1.9中，还专门实现了一个叫做type alias的新特性，然后把x/net/context中的Context定义成标准库Context的别名，以解决新旧Context类型冲突问题，你可以看一下下面这段代码：

```
    // +build go1.9
	package context

	import "context"

	type Context = context.Context
	type CancelFunc = context.CancelFunc

```

Go标准库的Context不仅提供了上下文传递的信息，还提供了cancel、timeout等其它信息，这些信息貌似和context这个包名没关系，但是还是得到了广泛的应用。所以，你看，context包中的Context不仅仅传递上下文信息，还有timeout等其它功能，是不是“名不副实”呢？

其实啊，这也是这个Context的一个问题，比较容易误导人，Go布道师Dave Cheney还专门写了一篇文章讲述这个问题： [Context isn’t for cancellation](https://dave.cheney.net/2017/08/20/context-isnt-for-cancellation)。

同时，也有一些批评者针对Context提出了批评： [Context should go away for Go 2](https://faiface.github.io/post/context-should-go-away-go2/)，这篇文章把Context比作病毒，病毒会传染，结果把所有的方法都传染上了病毒（加上Context参数），绝对是视觉污染。

Go的开发者也注意到了“关于Context，存在一些争议”这件事儿，所以，Go核心开发者Ian Lance Taylor专门开了一个 [issue 28342](https://github.com/golang/go/issues/28342)，用来记录当前的Context的问题：

- Context包名导致使用的时候重复ctx context.Context；
- Context.WithValue可以接受任何类型的值，非类型安全；
- Context包名容易误导人，实际上，Context最主要的功能是取消goroutine的执行；
- Context漫天飞，函数污染。

尽管有很多的争议，但是，在很多场景下，使用Context其实会很方便，所以现在它已经在Go生态圈中传播开来了，包括很多的Web应用框架，都切换成了标准库的Context。标准库中的database/sql、os/exec、net、net/http等包中都使用到了Context。而且，如果我们遇到了下面的一些场景，也可以考虑使用Context：

- 上下文信息传递 （request-scoped），比如处理http请求、在请求处理链路上传递信息；
- 控制子goroutine的运行；
- 超时控制的方法调用；
- 可以取消的方法调用。

所以，我们需要掌握Context的具体用法，这样才能在不影响主要业务流程实现的时候，实现一些通用的信息传递，或者是能够和其它goroutine协同工作，提供timeout、cancel等机制。

# Context基本使用方法

首先，我们来学习一下Context接口包含哪些方法，这些方法都是干什么用的。

包context定义了Context接口，Context的具体实现包括4个方法，分别是Deadline、Done、Err和Value，如下所示：

```
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key interface{}) interface{}
}

```

下面我来具体解释下这4个方法。

**Deadline** 方法会返回这个Context被取消的截止日期。如果没有设置截止日期，ok的值是false。后续每次调用这个对象的Deadline方法时，都会返回和第一次调用相同的结果。

**Done** 方法返回一个Channel对象。在Context被取消时，此Channel会被close，如果没被取消，可能会返回nil。后续的Done调用总是返回相同的结果。当Done被close的时候，你可以通过ctx.Err获取错误信息。Done这个方法名其实起得并不好，因为名字太过笼统，不能明确反映Done被close的原因，因为cancel、timeout、deadline都可能导致Done被close，不过，目前还没有一个更合适的方法名称。

关于Done方法，你必须要记住的知识点就是：如果Done没有被close，Err方法返回nil；如果Done被close，Err方法会返回Done被close的原因。

**Value** 返回此ctx中和指定的key相关联的value。

Context中实现了2个常用的生成顶层Context的方法。

- context.Background()：返回一个非nil的、空的Context，没有任何值，不会被cancel，不会超时，没有截止日期。一般用在主函数、初始化、测试以及创建根Context的时候。
- context.TODO()：返回一个非nil的、空的Context，没有任何值，不会被cancel，不会超时，没有截止日期。当你不清楚是否该用Context，或者目前还不知道要传递一些什么上下文信息的时候，就可以使用这个方法。

官方文档是这么讲的，你可能会觉得像没说一样，因为界限并不是很明显。其实，你根本不用费脑子去考虑，可以直接使用context.Background。事实上，它们两个底层的实现是一模一样的：

```
var (
    background = new(emptyCtx)
    todo       = new(emptyCtx)
)

func Background() Context {
    return background
}

func TODO() Context {
    return todo
}

```

在使用Context的时候，有一些约定俗成的规则。

1. 一般函数使用Context的时候，会把这个参数放在第一个参数的位置。
2. 从来不把nil当做Context类型的参数值，可以使用context.Background()创建一个空的上下文对象，也不要使用nil。
3. Context只用来临时做函数之间的上下文透传，不能持久化Context或者把Context长久保存。把Context持久化到数据库、本地文件或者全局变量、缓存中都是错误的用法。
4. key的类型不应该是字符串类型或者其它内建类型，否则容易在包之间使用Context时候产生冲突。使用WithValue时，key的类型应该是自己定义的类型。
5. 常常使用struct{}作为底层类型定义key的类型。对于exported key的静态类型，常常是接口或者指针。这样可以尽量减少内存分配。

其实官方的文档也是比较搞笑的，文档中强调key的类型不要使用string，结果接下来的例子中就是用string类型作为key的类型。你自己把握住这个要点就好，如果你能保证别人使用你的Context时不会和你定义的key冲突，那么key的类型就比较随意，因为你自己保证了不同包的key不会冲突，否则建议你尽量采用保守的unexported的类型。

# 创建特殊用途Context的方法

接下来，我会介绍标准库中几种创建特殊用途Context的方法：WithValue、WithCancel、WithTimeout和WithDeadline，包括它们的功能以及实现方式。

## WithValue

WithValue基于parent Context生成一个新的Context，保存了一个key-value键值对。它常常用来传递上下文。

WithValue方法其实是创建了一个类型为valueCtx的Context，它的类型定义如下：

```
type valueCtx struct {
    Context
    key, val interface{}
}

```

它持有一个key-value键值对，还持有parent的Context。它覆盖了Value方法，优先从自己的存储中检查这个key，不存在的话会从parent中继续检查。

Go标准库实现的Context还实现了链式查找。如果不存在，还会向parent Context去查找，如果parent还是valueCtx的话，还是遵循相同的原则：valueCtx会嵌入parent，所以还是会查找parent的Value方法的。

```
ctx = context.TODO()
ctx = context.WithValue(ctx, "key1", "0001")
ctx = context.WithValue(ctx, "key2", "0001")
ctx = context.WithValue(ctx, "key3", "0001")
ctx = context.WithValue(ctx, "key4", "0004")

fmt.Println(ctx.Value("key1"))

```

![](https://static001.geekbang.org/resource/image/03/fe/035a1b8e090184c1feba1ef194ec53fe.jpg?wh=4000*557)

## WithCancel

WithCancel 方法返回parent的副本，只是副本中的Done Channel是新建的对象，它的类型是cancelCtx。

我们常常在一些需要主动取消长时间的任务时，创建这种类型的Context，然后把这个Context传给长时间执行任务的goroutine。当需要中止任务时，我们就可以cancel这个Context，这样长时间执行任务的goroutine，就可以通过检查这个Context，知道Context已经被取消了。

WithCancel返回值中的第二个值是一个cancel函数。其实，这个返回值的名称（cancel）和类型（Cancel）也非常迷惑人。

记住，不是只有你想中途放弃，才去调用cancel，只要你的任务正常完成了，就需要调用cancel，这样，这个Context才能释放它的资源（通知它的children 处理cancel，从它的parent中把自己移除，甚至释放相关的goroutine）。很多同学在使用这个方法的时候，都会忘记调用cancel，切记切记，而且一定尽早释放。

我们来看下WithCancel方法的实现代码：

```
func WithCancel(parent Context) (ctx Context, cancel CancelFunc) {
    c := newCancelCtx(parent)
    propagateCancel(parent, &c)// 把c朝上传播
    return &c, func() { c.cancel(true, Canceled) }
}

// newCancelCtx returns an initialized cancelCtx.
func newCancelCtx(parent Context) cancelCtx {
    return cancelCtx{Context: parent}
}

```

代码中调用的propagateCancel方法会顺着parent路径往上找，直到找到一个cancelCtx，或者为nil。如果不为空，就把自己加入到这个cancelCtx的child，以便这个cancelCtx被取消的时候通知自己。如果为空，会新起一个goroutine，由它来监听parent的Done是否已关闭。

当这个cancelCtx的cancel函数被调用的时候，或者parent的Done被close的时候，这个cancelCtx的Done才会被close。

cancel是向下传递的，如果一个WithCancel生成的Context被cancel时，如果它的子Context（也有可能是孙，或者更低，依赖子的类型）也是cancelCtx类型的，就会被cancel，但是不会向上传递。parent Context不会因为子Context被cancel而cancel。

cancelCtx被取消时，它的Err字段就是下面这个Canceled错误：

```
var Canceled = errors.New("context canceled")

```

## WithTimeout

WithTimeout其实是和WithDeadline一样，只不过一个参数是超时时间，一个参数是截止时间。超时时间加上当前时间，其实就是截止时间，因此，WithTimeout的实现是：

```
func WithTimeout(parent Context, timeout time.Duration) (Context, CancelFunc) {
    // 当前时间+timeout就是deadline
    return WithDeadline(parent, time.Now().Add(timeout))
}

```

## WithDeadline

WithDeadline会返回一个parent的副本，并且设置了一个不晚于参数d的截止时间，类型为timerCtx（或者是cancelCtx）。

如果它的截止时间晚于parent的截止时间，那么就以parent的截止时间为准，并返回一个类型为cancelCtx的Context，因为parent的截止时间到了，就会取消这个cancelCtx。

如果当前时间已经超过了截止时间，就直接返回一个已经被cancel的timerCtx。否则就会启动一个定时器，到截止时间取消这个timerCtx。

综合起来，timerCtx的Done被Close掉，主要是由下面的某个事件触发的：

- 截止时间到了；
- cancel函数被调用；
- parent的Done被close。

下面的代码是WithDeadline方法的实现：

```
func WithDeadline(parent Context, d time.Time) (Context, CancelFunc) {
    // 如果parent的截止时间更早，直接返回一个cancelCtx即可
    if cur, ok := parent.Deadline(); ok && cur.Before(d) {
        return WithCancel(parent)
    }
    c := &timerCtx{
        cancelCtx: newCancelCtx(parent),
        deadline:  d,
    }
    propagateCancel(parent, c) // 同cancelCtx的处理逻辑
    dur := time.Until(d)
    if dur <= 0 { //当前时间已经超过了截止时间，直接cancel
        c.cancel(true, DeadlineExceeded)
        return c, func() { c.cancel(false, Canceled) }
    }
    c.mu.Lock()
    defer c.mu.Unlock()
    if c.err == nil {
        // 设置一个定时器，到截止时间后取消
        c.timer = time.AfterFunc(dur, func() {
            c.cancel(true, DeadlineExceeded)
        })
    }
    return c, func() { c.cancel(true, Canceled) }
}

```

和cancelCtx一样，WithDeadline（WithTimeout）返回的cancel一定要调用，并且要尽可能早地被调用，这样才能尽早释放资源，不要单纯地依赖截止时间被动取消。正确的使用姿势是啥呢？我们来看一个例子。

```
func slowOperationWithTimeout(ctx context.Context) (Result, error) {
	ctx, cancel := context.WithTimeout(ctx, 100*time.Millisecond)
	defer cancel() // 一旦慢操作完成就立马调用cancel
	return slowOperation(ctx)
}

```

# 总结

我们经常使用Context来取消一个goroutine的运行，这是Context最常用的场景之一，Context也被称为goroutine生命周期范围（goroutine-scoped）的Context，把Context传递给goroutine。但是，goroutine需要尝试检查Context的Done是否关闭了：

```
func main() {
    ctx, cancel := context.WithCancel(context.Background())

    go func() {
        defer func() {
            fmt.Println("goroutine exit")
        }()

        for {
            select {
            case <-ctx.Done():
                return
            default:
                time.Sleep(time.Second)
            }
        }
    }()

    time.Sleep(time.Second)
    cancel()
    time.Sleep(2 * time.Second)
}

```

如果你要为Context实现一个带超时功能的调用，比如访问远程的一个微服务，超时并不意味着你会通知远程微服务已经取消了这次调用，大概率的实现只是避免客户端的长时间等待，远程的服务器依然还执行着你的请求。

所以，有时候，Context并不会减少对服务器的请求负担。如果在Context被cancel的时候，你能关闭和服务器的连接，中断和数据库服务器的通讯、停止对本地文件的读写，那么，这样的超时处理，同时能减少对服务调用的压力，但是这依赖于你对超时的底层处理机制。

![](https://static001.geekbang.org/resource/image/2d/2b/2dcbb1ca54c31b4f3e987b602a38e82b.jpg?wh=2250*2441)

# 思考题

使用WithCancel和WithValue写一个级联的使用Context的例子，验证一下parent Context被cancel后，子conext是否也立刻被cancel了。

欢迎在留言区写下你的思考和答案，我们一起交流讨论。如果你觉得有所收获，也欢迎你把今天的内容分享给你的朋友或同事。