你好，我是鸟窝。

Go是一个自动垃圾回收的编程语言，采用 [三色并发标记算法](https://go.dev/blog/ismmkeynote) 标记对象并回收。和其它没有自动垃圾回收的编程语言不同，使用Go语言创建对象的时候，我们没有回收/释放的心理负担，想用就用，想创建就创建。

但是， **如果你想使用Go开发一个高性能的应用程序的话，就必须考虑垃圾回收给性能带来的影响**，毕竟，Go的自动垃圾回收机制还是有一个STW（stop-the-world，程序暂停）的时间，而且，大量地创建在堆上的对象，也会影响垃圾回收标记的时间。

所以，一般我们做性能优化的时候，会采用对象池的方式，把不用的对象回收起来，避免被垃圾回收掉，这样使用的时候就不必在堆上重新创建了。

不止如此，像数据库连接、TCP的长连接，这些连接在创建的时候是一个非常耗时的操作。如果每次都创建一个新的连接对象，耗时较长，很可能整个业务的大部分耗时都花在了创建连接上。

所以，如果我们能把这些连接保存下来，避免每次使用的时候都重新创建，不仅可以大大减少业务的耗时，还能提高应用程序的整体性能。

Go标准库中提供了一个通用的Pool数据结构，也就是sync.Pool，我们使用它可以创建池化的对象。这节课我会详细给你介绍一下sync.Pool的使用方法、实现原理以及常见的坑，帮助你全方位地掌握标准库的Pool。

不过，这个类型也有一些使用起来不太方便的地方，就是 **它池化的对象可能会被垃圾回收掉**，这对于数据库长连接等场景是不合适的。所以在这一讲中，我会专门介绍其它的一些Pool，包括TCP连接池、数据库连接池等等。

除此之外，我还会专门介绍一个池的应用场景： Worker Pool，或者叫做goroutine pool，这也是常用的一种并发模式，可以使用有限的goroutine资源去处理大量的业务数据。

# sync.Pool

首先，我们来学习下标准库提供的sync.Pool数据类型。

sync.Pool数据类型用来保存一组可独立访问的 **临时** 对象。请注意这里加粗的“临时”这两个字，它说明了sync.Pool这个数据类型的特点，也就是说，它池化的对象会在未来的某个时候被毫无预兆地移除掉。而且，如果没有别的对象引用这个被移除的对象的话，这个被移除的对象就会被垃圾回收掉。

因为Pool可以有效地减少新对象的申请，从而提高程序性能，所以Go内部库也用到了sync.Pool，比如fmt包，它会使用一个动态大小的buffer池做输出缓存，当大量的goroutine并发输出的时候，就会创建比较多的buffer，并且在不需要的时候回收掉。

有两个知识点你需要记住：

1. sync.Pool本身就是线程安全的，多个goroutine可以并发地调用它的方法存取对象；
2. sync.Pool不可在使用之后再复制使用。

## sync.Pool的使用方法

知道了sync.Pool这个数据类型的特点，接下来，我们来学习下它的使用方法。其实，这个数据类型不难，它只提供了三个对外的方法：New、Get和Put。

**1.New**

Pool struct包含一个New字段，这个字段的类型是函数 func() interface{}。当调用Pool的Get方法从池中获取元素，没有更多的空闲元素可返回时，就会调用这个New方法来创建新的元素。如果你没有设置New字段，没有更多的空闲元素可返回时，Get方法将返回nil，表明当前没有可用的元素。

有趣的是，New是可变的字段。这就意味着，你可以在程序运行的时候改变创建元素的方法。当然，很少有人会这么做，因为一般我们创建元素的逻辑都是一致的，要创建的也是同一类的元素，所以你在使用Pool的时候也没必要玩一些“花活”，在程序运行时更改New的值。

**2.Get**

如果调用这个方法，就会从Pool **取走** 一个元素，这也就意味着，这个元素会从Pool中移除，返回给调用者。不过，除了返回值是正常实例化的元素，Get方法的返回值还可能会是一个nil（Pool.New字段没有设置，又没有空闲元素可以返回），所以你在使用的时候，可能需要判断。

**3.Put**

这个方法用于将一个元素返还给Pool，Pool会把这个元素保存到池中，并且可以复用。但如果Put一个nil值，Pool就会忽略这个值。

好了，了解了这几个方法，下面我们看看sync.Pool最常用的一个场景：buffer池（缓冲池）。

因为byte slice是经常被创建销毁的一类对象，使用buffer池可以缓存已经创建的byte slice，比如，著名的静态网站生成工具Hugo中，就包含这样的实现 [bufpool](https://github.com/gohugoio/hugo/blob/master/bufferpool/bufpool.go)，你可以看一下下面这段代码：

```
var buffers = sync.Pool{
	New: func() interface{} {
		return new(bytes.Buffer)
	},
}

func GetBuffer() *bytes.Buffer {
	return buffers.Get().(*bytes.Buffer)
}

func PutBuffer(buf *bytes.Buffer) {
	buf.Reset()
	buffers.Put(buf)
}

```

除了Hugo，这段buffer池的代码非常常用。很可能你在阅读其它项目的代码的时候就碰到过，或者是你自己实现buffer池的时候也会这么去实现，但是请你注意了，这段代码是有问题的，你一定不要将上面的代码应用到实际的产品中。它可能会有内存泄漏的问题，下面我会重点讲这个问题。

## 实现原理

了解了sync.Pool的基本使用方法，下面我们就来重点学习下它的实现。

Go 1.13之前的sync.Pool的实现有2大问题：

**1.每次GC都会回收创建的对象。**

如果缓存元素数量太多，就会导致STW耗时变长；缓存元素都被回收后，会导致Get命中率下降，Get方法不得不新创建很多对象。

**2.底层实现使用了Mutex，对这个锁并发请求竞争激烈的时候，会导致性能的下降。**

在Go 1.13中，sync.Pool做了大量的优化。前几讲中我提到过，提高并发程序性能的优化点是尽量不要使用锁，如果不得已使用了锁，就把锁Go的粒度降到最低。 **Go对Pool的优化就是避免使用锁，同时将加锁的queue改成lock-free的queue的实现，给即将移除的元素再多一次“复活”的机会。**

当前，sync.Pool的数据结构如下图所示：

![](https://static001.geekbang.org/resource/image/f4/96/f4003704663ea081230760098f8af696.jpg?wh=3659*2186)

Pool最重要的两个字段是 local和victim，因为它们两个主要用来存储空闲的元素。弄清楚这两个字段的处理逻辑，你就能完全掌握sync.Pool的实现了。下面我们来看看这两个字段的关系。

每次垃圾回收的时候，Pool会把victim中的对象移除，然后把local的数据给victim，这样的话，local就会被清空，而victim就像一个垃圾分拣站，里面的东西可能会被当做垃圾丢弃了，但是里面有用的东西也可能被捡回来重新使用。

victim中的元素如果被Get取走，那么这个元素就很幸运，因为它又“活”过来了。但是，如果这个时候Get的并发不是很大，元素没有被Get取走，那么就会被移除掉，因为没有别人引用它的话，就会被垃圾回收掉。

下面的代码是垃圾回收时sync.Pool的处理逻辑：

```
func poolCleanup() {
    // 丢弃当前victim, STW所以不用加锁
    for _, p := range oldPools {
        p.victim = nil
        p.victimSize = 0
    }

    // 将local复制给victim, 并将原local置为nil
    for _, p := range allPools {
        p.victim = p.local
        p.victimSize = p.localSize
        p.local = nil
        p.localSize = 0
    }

    oldPools, allPools = allPools, nil
}

```

在这段代码中，你需要关注一下local字段，因为所有当前主要的空闲可用的元素都存放在local字段中，请求元素时也是优先从local字段中查找可用的元素。local字段包含一个poolLocalInternal字段，并提供CPU缓存对齐，从而避免false sharing。

而poolLocalInternal也包含两个字段：private和shared。

- private，代表一个缓存的元素，而且只能由相应的一个P存取。因为一个P同时只能执行一个goroutine，所以不会有并发的问题。
- shared，可以由任意的P访问，但是只有本地的P才能pushHead/popHead，其它P可以popTail，相当于只有一个本地的P作为生产者（Producer），多个P作为消费者（Consumer），它是使用一个local-free的queue列表实现的。

### Get方法

我们来看看Get方法的具体实现原理。

```
func (p *Pool) Get() interface{} {
    // 把当前goroutine固定在当前的P上
    l, pid := p.pin()
    x := l.private // 优先从local的private字段取，快速
    l.private = nil
    if x == nil {
        // 从当前的local.shared弹出一个，注意是从head读取并移除
        x, _ = l.shared.popHead()
        if x == nil { // 如果没有，则去偷一个
            x = p.getSlow(pid)
        }
    }
    runtime_procUnpin()
    // 如果没有获取到，尝试使用New函数生成一个新的
    if x == nil && p.New != nil {
        x = p.New()
    }
    return x
}

```

我来给你解释下这段代码。首先，从本地的private字段中获取可用元素，因为没有锁，获取元素的过程会非常快，如果没有获取到，就尝试从本地的shared获取一个，如果还没有，会使用getSlow方法去其它的shared中“偷”一个。最后，如果没有获取到，就尝试使用New函数创建一个新的。

这里的重点是getSlow方法，我们来分析下。看名字也就知道了，它的耗时可能比较长。它首先要遍历所有的local，尝试从它们的shared弹出一个元素。如果还没找到一个，那么，就开始对victim下手了。

在vintim中查询可用元素的逻辑还是一样的，先从对应的victim的private查找，如果查不到，就再从其它victim的shared中查找。

下面的代码是getSlow方法的主要逻辑：

```
func (p *Pool) getSlow(pid int) interface{} {

    size := atomic.LoadUintptr(&p.localSize)
    locals := p.local
    // 从其它proc中尝试偷取一个元素
    for i := 0; i < int(size); i++ {
        l := indexLocal(locals, (pid+i+1)%int(size))
        if x, _ := l.shared.popTail(); x != nil {
            return x
        }
    }

    // 如果其它proc也没有可用元素，那么尝试从vintim中获取
    size = atomic.LoadUintptr(&p.victimSize)
    if uintptr(pid) >= size {
        return nil
    }
    locals = p.victim
    l := indexLocal(locals, pid)
    if x := l.private; x != nil { // 同样的逻辑，先从vintim中的local private获取
        l.private = nil
        return x
    }
    for i := 0; i < int(size); i++ { // 从vintim其它proc尝试偷取
        l := indexLocal(locals, (pid+i)%int(size))
        if x, _ := l.shared.popTail(); x != nil {
            return x
        }
    }

    // 如果victim中都没有，则把这个victim标记为空，以后的查找可以快速跳过了
    atomic.StoreUintptr(&p.victimSize, 0)

    return nil
}

```

这里我没列出pin代码的实现，你只需要知道，pin方法会将此goroutine固定在当前的P上，避免查找元素期间被其它的P执行。固定的好处就是查找元素期间直接得到跟这个P相关的local。有一点需要注意的是，pin方法在执行的时候，如果跟这个P相关的local还没有创建，或者运行时P的数量被修改了的话，就会新创建local。

### Put方法

我们来看看Put方法的具体实现原理。

```
func (p *Pool) Put(x interface{}) {
    if x == nil { // nil值直接丢弃
        return
    }
    l, _ := p.pin()
    if l.private == nil { // 如果本地private没有值，直接设置这个值即可
        l.private = x
        x = nil
    }
    if x != nil { // 否则加入到本地队列中
        l.shared.pushHead(x)
    }
    runtime_procUnpin()
}

```

Put的逻辑相对简单，优先设置本地private，如果private字段已经有值了，那么就把此元素push到本地队列中。

## sync.Pool的坑

到这里，我们就掌握了sync.Pool的使用方法和实现原理，接下来，我要再和你聊聊容易踩的两个坑，分别是内存泄漏和内存浪费。

### 内存泄漏

这节课刚开始的时候，我讲到，可以使用sync.Pool做buffer池，但是，如果用刚刚的那种方式做buffer池的话，可能会有内存泄漏的风险。为啥这么说呢？我们来分析一下。

取出来的bytes.Buffer在使用的时候，我们可以往这个元素中增加大量的byte数据，这会导致底层的byte slice的容量可能会变得很大。这个时候，即使Reset再放回到池子中，这些byte slice的容量不会改变，所占的空间依然很大。而且，因为Pool回收的机制，这些大的Buffer可能不被回收，而是会一直占用很大的空间，这属于内存泄漏的问题。

即使是Go的标准库，在内存泄漏这个问题上也栽了几次坑，比如 [issue 23199](https://github.com/golang/go/issues/23199)、 [@dsnet](https://github.com/dsnet) 提供了一个简单的可重现的例子，演示了内存泄漏的问题。再比如encoding、json中类似的问题：将容量已经变得很大的Buffer再放回Pool中，导致内存泄漏。后来在元素放回时，增加了检查逻辑，改成放回的超过一定大小的buffer，就直接丢弃掉，不再放到池子中，如下所示：

![](https://static001.geekbang.org/resource/image/e3/9f/e3e23d2f2ab55b64741e14856a58389f.png?wh=1098*319)

package fmt中也有这个问题，修改方法是一样的，超过一定大小的buffer，就直接丢弃了：

![](https://static001.geekbang.org/resource/image/06/62/06c68476cac13a860c470b006718c462.png?wh=1012*392)

在使用sync.Pool回收buffer的时候， **一定要检查回收的对象的大小。** 如果buffer太大，就不要回收了，否则就太浪费了。

### 内存浪费

除了内存泄漏以外，还有一种浪费的情况，就是池子中的buffer都比较大，但在实际使用的时候，很多时候只需要一个小的buffer，这也是一种浪费现象。接下来，我就讲解一下这种情况的处理方法。

要做到物尽其用，尽可能不浪费的话，我们可以将buffer池分成几层。首先，小于512 byte的元素的buffer占一个池子；其次，小于1K byte大小的元素占一个池子；再次，小于4K byte大小的元素占一个池子。这样分成几个池子以后，就可以根据需要，到所需大小的池子中获取buffer了。

在标准库 [net/http/server.go](https://github.com/golang/go/blob/617f2c3e35cdc8483b950aa3ef18d92965d63197/src/net/http/server.go) 中的代码中，就提供了2K和4K两个writer的池子。你可以看看下面这段代码：

![](https://static001.geekbang.org/resource/image/55/35/55086ccba91975a0f65bd35d1192e335.png?wh=628*611)

YouTube开源的知名项目vitess中提供了 [bucketpool](https://github.com/vitessio/vitess/blob/master/go/bucketpool/bucketpool.go) 的实现，它提供了更加通用的多层buffer池。你在使用的时候，只需要指定池子的最大和最小尺寸，vitess就会自动计算出合适的池子数。而且，当你调用Get方法的时候，只需要传入你要获取的buffer的大小，就可以了。下面这段代码就描述了这个过程，你可以看看：

![](https://static001.geekbang.org/resource/image/c5/08/c5cd474aa53fe57e0722d840a6c7f308.png?wh=591*146)

# 第三方库

除了这种分层的为了节省空间的buffer设计外，还有其它的一些第三方的库也会提供buffer池的功能。接下来我带你熟悉几个常用的第三方的库。

1. [bytebufferpool](https://github.com/valyala/bytebufferpool)

这是fasthttp作者valyala提供的一个buffer池，基本功能和sync.Pool相同。它的底层也是使用sync.Pool实现的，包括会检测最大的buffer，超过最大尺寸的buffer，就会被丢弃。

valyala一向很擅长挖掘系统的性能，这个库也不例外。它提供了校准（calibrate，用来动态调整创建元素的权重）的机制，可以“智能”地调整Pool的defaultSize和maxSize。一般来说，我们使用buffer size的场景比较固定，所用buffer的大小会集中在某个范围里。有了校准的特性，bytebufferpool就能够偏重于创建这个范围大小的buffer，从而节省空间。

2. [oxtoacart/bpool](https://github.com/oxtoacart/bpool)

这也是比较常用的buffer池，它提供了以下几种类型的buffer。

- bpool.BufferPool： 提供一个固定元素数量的buffer 池，元素类型是bytes.Buffer，如果超过这个数量，Put的时候就丢弃，如果池中的元素都被取光了，会新建一个返回。Put回去的时候，不会检测buffer的大小。
- bpool.BytesPool：提供一个固定元素数量的byte slice池，元素类型是byte slice。Put回去的时候不检测slice的大小。
- bpool.SizedBufferPool： 提供一个固定元素数量的buffer池，如果超过这个数量，Put的时候就丢弃，如果池中的元素都被取光了，会新建一个返回。Put回去的时候，会检测buffer的大小，超过指定的大小的话，就会创建一个新的满足条件的buffer放回去。

bpool最大的特色就是能够保持池子中元素的数量，一旦Put的数量多于它的阈值，就会自动丢弃，而sync.Pool是一个没有限制的池子，只要Put就会收进去。

bpool是基于Channel实现的，不像sync.Pool为了提高性能而做了很多优化，所以，在性能上比不过sync.Pool。不过，它提供了限制Pool容量的功能，所以，如果你想控制Pool的容量的话，可以考虑这个库。

# 连接池

Pool的另一个很常用的一个场景就是保持TCP的连接。一个TCP的连接创建，需要三次握手等过程，如果是TLS的，还会需要更多的步骤，如果加上身份认证等逻辑的话，耗时会更长。所以，为了避免每次通讯的时候都新创建连接，我们一般会建立一个连接的池子，预先把连接创建好，或者是逐步把连接放在池子中，减少连接创建的耗时，从而提高系统的性能。

事实上，我们很少会使用sync.Pool去池化连接对象，原因就在于，sync.Pool会无通知地在某个时候就把连接移除垃圾回收掉了，而我们的场景是需要长久保持这个连接，所以，我们一般会使用其它方法来池化连接，比如接下来我要讲到的几种需要保持长连接的Pool。

## 标准库中的http client池

标准库的http.Client是一个http client的库，可以用它来访问web服务器。为了提高性能，这个Client的实现也是通过池的方法来缓存一定数量的连接，以便后续重用这些连接。

http.Client实现连接池的代码是在Transport类型中，它使用idleConn保存持久化的可重用的长连接：

![](https://static001.geekbang.org/resource/image/14/ec/141ced98a81466b793b0f90b9652afec.png?wh=1192*430)

## TCP连接池

最常用的一个TCP连接池是fatih开发的 [fatih/pool](https://github.com/fatih/pool)，虽然这个项目已经被fatih归档（Archived），不再维护了，但是因为它相当稳定了，我们可以开箱即用。即使你有一些特殊的需求，也可以fork它，然后自己再做修改。

它的使用套路如下：

```
// 工厂模式，提供创建连接的工厂方法
factory    := func() (net.Conn, error) { return net.Dial("tcp", "127.0.0.1:4000") }

// 创建一个tcp池，提供初始容量和最大容量以及工厂方法
p, err := pool.NewChannelPool(5, 30, factory)

// 获取一个连接
conn, err := p.Get()

// Close并不会真正关闭这个连接，而是把它放回池子，所以你不必显式地Put这个对象到池子中
conn.Close()

// 通过调用MarkUnusable, Close的时候就会真正关闭底层的tcp的连接了
if pc, ok := conn.(*pool.PoolConn); ok {
  pc.MarkUnusable()
  pc.Close()
}

// 关闭池子就会关闭=池子中的所有的tcp连接
p.Close()

// 当前池子中的连接的数量
current := p.Len()

```

虽然我一直在说TCP，但是它管理的是更通用的net.Conn，不局限于TCP连接。

它通过把net.Conn包装成PoolConn，实现了拦截net.Conn的Close方法，避免了真正地关闭底层连接，而是把这个连接放回到池中：

```
    type PoolConn struct {
		net.Conn
		mu       sync.RWMutex
		c        *channelPool
		unusable bool
	}

    //拦截Close
	func (p *PoolConn) Close() error {
		p.mu.RLock()
		defer p.mu.RUnlock()

		if p.unusable {
			if p.Conn != nil {
				return p.Conn.Close()
			}
			return nil
		}
		return p.c.put(p.Conn)
	}

```

它的Pool是通过Channel实现的，空闲的连接放入到Channel中，这也是Channel的一个应用场景：

```
    type channelPool struct {
		// 存储连接池的channel
		mu    sync.RWMutex
		conns chan net.Conn


		// net.Conn 的产生器
		factory Factory
	}

```

## 数据库连接池

标准库sql.DB还提供了一个通用的数据库的连接池，通过MaxOpenConns和MaxIdleConns控制最大的连接数和最大的idle的连接数。默认的MaxIdleConns是2，这个数对于数据库相关的应用来说太小了，我们一般都会调整它。

![](https://static001.geekbang.org/resource/image/49/15/49c14b5bccb6d6ac7a159eece17a2215.png?wh=552*106)

DB的freeConn保存了idle的连接，这样，当我们获取数据库连接的时候，它就会优先尝试从freeConn获取已有的连接（ [conn](https://github.com/golang/go/blob/4fc3896e7933e31822caa50e024d4e139befc75f/src/database/sql/sql.go#L1196)）。

![](https://static001.geekbang.org/resource/image/d0/b5/d043yyd649a216fe37885yy4e03af3b5.png?wh=789*345)

## Memcached Client连接池

Brad Fitzpatrick是知名缓存库Memcached的原作者，前Go团队成员。 [gomemcache](https://github.com/bradfitz/gomemcache) 是他使用Go开发的Memchaced的客户端，其中也用了连接池的方式池化Memcached的连接。接下来让我们看看它的连接池的实现。

gomemcache Client有一个freeconn的字段，用来保存空闲的连接。当一个请求使用完之后，它会调用putFreeConn放回到池子中，请求的时候，调用getFreeConn优先查询freeConn中是否有可用的连接。它采用Mutex+Slice实现Pool：

```
   // 放回一个待重用的连接
   func (c *Client) putFreeConn(addr net.Addr, cn *conn) {
		c.lk.Lock()
		defer c.lk.Unlock()
		if c.freeconn == nil { // 如果对象为空，创建一个map对象
			c.freeconn = make(map[string][]*conn)
		}
		freelist := c.freeconn[addr.String()] //得到此地址的连接列表
		if len(freelist) >= c.maxIdleConns() {//如果连接已满,关闭，不再放入
			cn.nc.Close()
			return
		}
		c.freeconn[addr.String()] = append(freelist, cn) // 加入到空闲列表中
	}

    // 得到一个空闲连接
	func (c *Client) getFreeConn(addr net.Addr) (cn *conn, ok bool) {
		c.lk.Lock()
		defer c.lk.Unlock()
		if c.freeconn == nil {
			return nil, false
		}
		freelist, ok := c.freeconn[addr.String()]
		if !ok || len(freelist) == 0 { // 没有此地址的空闲列表，或者列表为空
			return nil, false
		}
		cn = freelist[len(freelist)-1] // 取出尾部的空闲连接
		c.freeconn[addr.String()] = freelist[:len(freelist)-1]
		return cn, true
	}

```

# Worker Pool

最后，我再讲一个Pool应用得非常广泛的场景。

你已经知道，goroutine是一个很轻量级的“纤程”，在一个服务器上可以创建十几万甚至几十万的goroutine。但是“可以”和“合适”之间还是有区别的，你会在应用中让几十万的goroutine一直跑吗？基本上是不会的。

一个goroutine初始的栈大小是2048个字节，并且在需要的时候可以扩展到1GB（具体的内容你可以课下看看代码中的配置： [不同的架构最大数会不同](https://github.com/golang/go/blob/f296b7a6f045325a230f77e9bda1470b1270f817/src/runtime/proc.go#L120)），所以，大量的goroutine还是很耗资源的。同时，大量的goroutine对于调度和垃圾回收的耗时还是会有影响的，因此，goroutine并不是越多越好。

有的时候，我们就会创建一个Worker Pool来减少goroutine的使用。比如，我们实现一个TCP服务器，如果每一个连接都要由一个独立的goroutine去处理的话，在大量连接的情况下，就会创建大量的goroutine，这个时候，我们就可以创建一个固定数量的goroutine（Worker），由这一组Worker去处理连接，比如fasthttp中的 [Worker Pool](https://github.com/valyala/fasthttp/blob/9f11af296864153ee45341d3f2fe0f5178fd6210/workerpool.go#L16)。

Worker的实现也是五花八门的：

- 有些是在后台默默执行的，不需要等待返回结果；
- 有些需要等待一批任务执行完；
- 有些Worker Pool的生命周期和程序一样长；
- 有些只是临时使用，执行完毕后，Pool就销毁了。

大部分的Worker Pool都是通过Channel来缓存任务的，因为Channel能够比较方便地实现并发的保护，有的是多个Worker共享同一个任务Channel，有些是每个Worker都有一个独立的Channel。

综合下来，精挑细选，我给你推荐三款易用的Worker Pool，这三个Worker Pool 的API设计简单，也比较相似，易于和项目集成，而且提供的功能也是我们常用的功能。

- [gammazero/workerpool](https://godoc.org/github.com/gammazero/workerpool)：gammazero/workerpool可以无限制地提交任务，提供了更便利的Submit和SubmitWait方法提交任务，还可以提供当前的worker数和任务数以及关闭Pool的功能。
- [ivpusic/grpool](https://godoc.org/github.com/ivpusic/grpool)：grpool创建Pool的时候需要提供Worker的数量和等待执行的任务的最大数量，任务的提交是直接往Channel放入任务。
- [dpaks/goworkers](https://godoc.org/github.com/dpaks/goworkers)：dpaks/goworkers提供了更便利的Submit方法提交任务以及Worker数、任务数等查询方法、关闭Pool的方法。它的任务的执行结果需要在ResultChan和ErrChan中去获取，没有提供阻塞的方法，但是它可以在初始化的时候设置Worker的数量和任务数。

类似的Worker Pool的实现非常多，比如还有 [panjf2000/ants](https://github.com/panjf2000/ants)、 [Jeffail/tunny](https://github.com/Jeffail/tunny) 、 [benmanns/goworker](https://github.com/benmanns/goworker)、 [go-playground/pool](https://github.com/go-playground/pool)、 [Sherifabdlnaby/gpool](https://github.com/Sherifabdlnaby/gpool) 等第三方库。 [pond](https://github.com/alitto/pond) 也是一个非常不错的Worker Pool，关注度目前不是很高，但是功能非常齐全。

其实，你也可以自己去开发自己的Worker Pool，但是，对于我这种“懒惰”的人来说，只要满足我的实际需求，我还是倾向于从这个几个常用的库中选择一个来使用。所以，我建议你也从常用的库中进行选择。

# 总结

Pool是一个通用的概念，也是解决对象重用和预先分配的一个常用的优化手段。即使你自己没在项目中直接使用过，但肯定在使用其它库的时候，就享受到应用Pool的好处了，比如数据库的访问、http API的请求等等。

我们一般不会在程序一开始的时候就开始考虑优化，而是等项目开发到一个阶段，或者快结束的时候，才全面地考虑程序中的优化点，而Pool就是常用的一个优化手段。如果你发现程序中有一种GC耗时特别高，有大量的相同类型的临时对象，不断地被创建销毁，这时，你就可以考虑看看，是不是可以通过池化的手段重用这些对象。

另外，在分布式系统或者微服务框架中，可能会有大量的并发Client请求，如果Client的耗时占比很大，你也可以考虑池化Client，以便重用。

如果你发现系统中的goroutine数量非常多，程序的内存资源占用比较大，而且整体系统的耗时和GC也比较高，我建议你看看，是否能够通过Worker Pool解决大量goroutine的问题，从而降低这些指标。

![](https://static001.geekbang.org/resource/image/58/aa/58358f16bcee0281b55299f0386e17aa.jpg?wh=2250*2404)

# 思考题

在标准库net/rpc包中，Server端需要解析大量客户端的请求（ [Request](https://github.com/golang/go/blob/master/src/net/rpc/server.go#L171)），这些短暂使用的Request是可以重用的。请你检查相关的代码，看看Go开发者都使用了什么样的方式来重用这些对象。

欢迎在留言区写下你的思考和答案，我们一起交流讨论。如果你觉得有所收获，也欢迎你把今天的内容分享给你的朋友或同事。