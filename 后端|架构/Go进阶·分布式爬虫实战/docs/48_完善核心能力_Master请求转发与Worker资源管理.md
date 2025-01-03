你好，我是郑建勋。

这节课，让我们继续优化Master服务，实现Master请求转发和并发情况下的资源保护，同时实现Worker对分配资源的监听。

## 将Master请求转发到Leader

首先我们需要考虑一下，当Master是Follower状态，同时还接收到了请求的情形。在之前的设计中，为了避免并发处理时可能出现的异常情况，我们只打算让Leader来处理请求。所以，当Master节点接收到请求时，如果当前节点不是Leader，我们可以直接报错，由客户端选择正确的Leader节点。如下所示。

```plain
func (m *Master) AddResource(ctx context.Context, req *proto.ResourceSpec, resp *proto.NodeSpec) error {
	if !m.IsLeader() {
		return errors.New("no leader")
	}
}

```

我们还可以采用另外一种更常见的方式：将接收到的请求转发给Leader。要实现这一点，首先所有Master节点要在Leader发生变更时，将当前最新的Leader地址保存到leaderID中。

```plain
func (m *Master) Campaign() {
	select {
		case resp := <-leaderChange:
			m.logger.Info("watch leader change", zap.String("leader:", string(resp.Kvs[0].Value)))
			m.leaderID = string(resp.Kvs[0].Value)
		}
		for {
			select {
			case err := <-leaderCh:
					m.leaderID = m.ID
			case resp := <-leaderChange:
				if len(resp.Kvs) > 0 {
					m.logger.Info("watch leader change", zap.String("leader:", string(resp.Kvs[0].Value)))
					m.leaderID = string(resp.Kvs[0].Value)
				}
		}
}

```

在处理请求前，首先判断当前Master的状态，如果它不是Leader，就获取Leader的地址并完成请求的转发。注意，这里如果不指定Leader的地址，go-micro就会随机选择一个地址进行转发。

```plain
func (m *Master) AddResource(ctx context.Context, req *proto.ResourceSpec, resp *proto.NodeSpec) error {
	if !m.IsLeader() && m.leaderID != "" && m.leaderID != m.ID {
		addr := getLeaderAddress(m.leaderID)
		nodeSpec, err := m.forwardCli.AddResource(ctx, req, client.WithAddress(addr))
		resp.Id = nodeSpec.Id
		resp.Address = nodeSpec.Address
		return err
	}

	nodeSpec, err := m.addResources(&ResourceSpec{Name: req.Name})
	if nodeSpec != nil {
		resp.Id = nodeSpec.Node.Id
		resp.Address = nodeSpec.Node.Address
	}
	return err
}

```

在转发时，我们使用了micro生成的GRPC客户端，这是通过在初始化时导入 micro GRPC client的插件实现的。SetForwardCli方法将生成的GRPC client 注入到了Master结构体中。

```plain
import (
	grpccli "github.com/go-micro/plugins/v4/client/grpc"
)

func RunGRPCServer(m *master.Master, logger *zap.Logger, reg registry.Registry, cfg ServerConfig) {
	service := micro.NewService(
		...
		micro.Client(grpccli.NewClient()),
	)

	cl := proto.NewCrawlerMasterService(cfg.Name, service.Client())
	m.SetForwardCli(cl)
}

```

接下来，我们来验证一下服务是否能够正确地转发。

首先启动一个 Worker和一个Master服务，当前的 Leader会变成master2，IP地址为192.168.0.105:9091。

```plain
» go run main.go worker  --pprof=:9983
» go run main.go master --id=2 --http=:8081  --grpc=:9091

```

现在我们启动一个新的Master服务master3。

```plain
» go run main.go master --id=3 --http=:8082  --grpc=:9092 --pprof=:9982

```

接着访问master3服务暴露的HTTP接口。虽然master3并不是Leader，但是访问master3添加资源时，操作仍然能够成功。

```plain
» curl  --request POST 'http://localhost:8082/crawler/resource' --header 'Content-Type: application/json' --data '{"id":"zjx","name": "task-forward"}'
{"id":"go.micro.server.worker-1","Address":"192.168.0.105:9090"}

```

同时，我们在Leader服务的日志中能够看到请求信息，验证成功。

```plain
{"level":"INFO","ts":"2022-12-29T17:23:55.792+0800","caller":"master/master.go:198","msg":"receive request","method":"CrawlerMaster.AddResource","Service":"go.micro.server.master","request param:":{"id":"zjx","name":"task-forward"}}

```

## 资源保护

由于Worker节点与Resource资源一直在动态变化当中，因此如果不考虑数据的并发安全，在复杂线上场景下，就可能出现很多难以解释的现象。

为了避免数据的并发安全问题，我们之前利用了通道来进行协程间的通信，但 **如果我们现在希望保护Worker节点与Resource资源，** **其实当前场景下更好的方式是使用原生的互斥锁。** 这是因为我们只希望在关键位置加锁，其他的逻辑仍然是并行的。如果我们在读取一个变量时还要用通道来通信，代码会变得不优雅。

我们来看下使用原生互斥锁的操作是怎样的。如下，在Master中添加sync.Mutex互斥锁，用于资源的并发安全。

```plain
type Master struct {
	...
	ID         string
	rlock      sync.Mutex

	options
}

```

我们可以在资源更新（资源加载与增删查改）、Worker节点更新、资源分配的阶段都加入互斥锁如下所示。

```plain
func (m *Master) DeleteResource(ctx context.Context, spec *proto.ResourceSpec, empty *empty.Empty) error {
	m.rlock.Lock()
	defer m.rlock.Unlock()

	r, ok := m.resources[spec.Name]
	...
}

func (m *Master) AddResource(ctx context.Context, req *proto.ResourceSpec, resp *proto.NodeSpec) error {
	...
	m.rlock.Lock()
	defer m.rlock.Lock()
	nodeSpec, err := m.addResources(&ResourceSpec{Name: req.Name})
	if nodeSpec != nil {
		resp.Id = nodeSpec.Node.Id
		resp.Address = nodeSpec.Node.Address
	}
	return err
}

func (m *Master) updateWorkNodes() {
	services, err := m.registry.GetService(worker.ServiceName)
	if err != nil {
		m.logger.Error("get service", zap.Error(err))
	}

	m.rlock.Lock()
	defer m.rlock.Unlock()
	...
	m.workNodes = nodes
}

func (m *Master) loadResource() error {
	resp, err := m.etcdCli.Get(context.Background(), RESOURCEPATH, clientv3.WithPrefix(), clientv3.WithSerializable())
	...
	resources := make(map[string]*ResourceSpec)
	m.rlock.Lock()
	defer m.rlock.Unlock()
	m.resources = resources
}

func (m *Master) reAssign() {
	rs := make([]*ResourceSpec, 0, len(m.resources))

	m.rlock.Lock()
	defer m.rlock.Unlock()

	for _, r := range m.resources {...}

	for _, r := range rs {
		m.addResources(r)
	}
}

```

当外部访问Leader的HTTP接口时，实际上服务端会开辟一个协程并发处理请求。通过使用互斥锁，我们消除了并发访问同一资源可能出现的问题。在实践中，需要合理地使用互斥锁，尽量让锁定的范围足够小，锁定的资源足够少，减少锁等待的时间。

## Worker单机模式

接下来我们回到Worker。Worker可以有两种模式，集群模式与单机模式。我们可以在Worker中加一个flag来切换Worker运行的模式。

对于少量的任务，可以直接用单机版的Worker来处理，种子节点来自于配置文件。而对于集群版的Worker，任务将来自Master的分配。

要切换Worker模式只要判断一个flag值cluster即可做到。如下所示，在启动Worker时，如果cluster为false，代表为单机模式。如果cluster为true，代表是集群模式。

```plain

WorkerCmd.Flags().BoolVar(
		&cluster, "cluster", true, "run mode")
var cluster bool

func (c *Crawler) Run(cluster bool) {
	if !cluster {
		c.handleSeeds()
	}

	go c.Schedule()
	for i := 0; i < c.WorkCount; i++ {
		go c.CreateWork()
	}
	c.HandleResult()
}

```

## Worker集群模式

在集群模式下，我们还需要书写Worker加载和监听etcd资源这一重要的功能。首先来看看初始化时的资源加载，在初始时，我们生成了etcd client，并注入到Crawler结构中。

```plain
endpoints := []string{e.registryURL}
cli, err := clientv3.New(clientv3.Config{Endpoints: endpoints})
if err != nil {
	return nil, err
}
e.etcdCli = cli

```

### 资源加载

Crawler.loadResource方法用于从etcd中加载资源。我们调用etcd Get方法，获取前缀为 `/resources` 的全量资源列表。解析这些资源，查看当前资源分配的节点是否为当前节点。如果分配的节点和当前节点匹配，意味着当前资源是分配给当前节点的，不是当前节点的资源将会被直接忽略。

```plain
func (c *Crawler) loadResource() error {
	resp, err := c.etcdCli.Get(context.Background(), master.RESOURCEPATH, clientv3.WithPrefix(), clientv3.WithSerializable())
	if err != nil {
		return fmt.Errorf("etcd get failed")
	}

	resources := make(map[string]*master.ResourceSpec)
	for _, kv := range resp.Kvs {
		r, err := master.Decode(kv.Value)
		if err == nil && r != nil {
			id := getID(r.AssignedNode)
			if len(id) > 0 && c.id == id {
				resources[r.Name] = r
			}
		}
	}
	c.Logger.Info("leader init load resource", zap.Int("lenth", len(resources)))
	c.rlock.Lock()
	defer c.rlock.Unlock()
	c.resources = resources
	for _, r := range c.resources {
		c.runTasks(r.Name)
	}

	return nil
}

```

资源加载完毕后，分配给当前节点的任务会执行runTask方法，通过任务名从全局任务池中获取爬虫任务，调用t.Rule.Root()获取种子请求，并放入到调度器中执行。

```plain
func (c *Crawler) runTasks(taskName string) {
	t, ok := Store.Hash[taskName]
	if !ok {
		c.Logger.Error("can not find preset tasks", zap.String("task name", taskName))
		return
	}
	res, err := t.Rule.Root()

	if err != nil {
		c.Logger.Error("get root failed",
			zap.Error(err),
		)
		return
	}

	for _, req := range res {
		req.Task = t
	}
	c.scheduler.Push(res...)
}

```

### 资源监听

除了加载资源，在初始化时我们还需要开辟一个新的协程c.watchResource来监听资源的变化。

```plain
func (c *Crawler) Run(id string, cluster bool) {
	c.id = id
	if !cluster {
		c.handleSeeds()
	}
	go c.loadResource()
	go c.watchResource()
	go c.Schedule()
	for i := 0; i < c.WorkCount; i++ {
		go c.CreateWork()
	}
	c.HandleResult()
}

```

如下所示，我在watchResource函数中书写了一个监听新增资源的功能。watchResource借助etcd client 的Watch方法监听资源的变化。Watch返回值是一个通道，当etcd client监听到etcd中前缀为 `/resources` 的资源发生变化时，就会将信息写入到通道Watch中。通过通道返回的信息，不仅能够得到当前有变动的资源最新的值，还可以得知当前资源变动的事件是新增、更新还是删除。如果是新增事件，那就调用runTasks启动该资源对应的爬虫任务。

```plain
func (c *Crawler) watchResource() {
	watch := c.etcdCli.Watch(context.Background(), master.RESOURCEPATH, clientv3.WithPrefix())
	for w := range watch {
		if w.Err() != nil {
			c.Logger.Error("watch resource failed", zap.Error(w.Err()))
			continue
		}
		if w.Canceled {
			c.Logger.Error("watch resource canceled")
			return
		}
		for _, ev := range w.Events {
			spec, err := master.Decode(ev.Kv.Value)
			if err != nil {
				c.Logger.Error("decode etcd value failed", zap.Error(err))
			}

			switch ev.Type {
			case clientv3.EventTypePut:
				if ev.IsCreate() {
					c.Logger.Info("receive create resource", zap.Any("spec", spec))

				} else if ev.IsModify() {
					c.Logger.Info("receive update resource", zap.Any("spec", spec))
				}
				c.runTasks(spec.Name)
			case clientv3.EventTypeDelete:
				c.Logger.Info("receive delete resource", zap.Any("spec", spec))
			}
		}
	}
}

```

现在让我们来验证一下新增资源的功能，启动Master与Worker节点。

```plain
» go run main.go master --id=3 --http=:8082  --grpc=:9092 --pprof=:9982
» go run main.go worker  --pprof=:9983

```

紧接着调用Master的添加资源接口。

```plain
» curl -H "content-type: application/json" -d '{"id":"zjx","name": "douban_book_list"}' <http://localhost:8082/crawler/resource>         jackson@localhost
{"id":"go.micro.server.worker-1", "Address":"192.168.0.105:9090"}

```

可以看到，Worker日志中任务开始正常地执行了，验证成功。完整代码你可以查看 [v0.4.1分支](https://github.com/dreamerjackson/crawler)。

```plain
{"level":"DEBUG","ts":"2022-12-30T21:06:56.743+0800","caller":"doubanbook/book.go:77","msg":"parse book tag,count: 47"}
{"level":"DEBUG","ts":"2022-12-30T21:07:00.532+0800","caller":"doubanbook/book.go:108","msg":"parse book list,count: 20 url: <https://book.douban.com/tag/随笔>"}
{"level":"DEBUG","ts":"2022-12-30T21:07:04.240+0800","caller":"doubanbook/book.go:108","msg":"parse book list,count: 20 url: <https://book.douban.com/tag/散文>"}

```

### 资源删除

接下来让我们继续看看如何删除一个爬虫任务。

我们需要在Watch的选项中设置 `clientv3.WithPrevKV()`，这样，当监听到资源的删除时，就能够获取当前删除的资源信息，接着就可以调用 `c.deleteTasks` 来删除任务了。

```plain
func (c *Crawler) watchResource() {
	watch := c.etcdCli.Watch(context.Background(), master.RESOURCEPATH, clientv3.WithPrefix(), clientv3.WithPrevKV())
	for w := range watch {
		for _, ev := range w.Events {
			switch ev.Type {
			...
			case clientv3.EventTypeDelete:
				spec, err := master.Decode(ev.PrevKv.Value)
				c.Logger.Info("receive delete resource", zap.Any("spec", spec))
				if err != nil {
					c.Logger.Error("decode etcd value failed", zap.Error(err))
				}
				c.rlock.Lock()
				c.deleteTasks(spec.Name)
				c.rlock.Unlock()
			}
		}
	}
}

```

deleteTasks 会删除 `c.resources` 中存储的当前Task，并且将Task的Closed变量设置为true。

```plain
func (c *Crawler) deleteTasks(taskName string) {
	t, ok := Store.Hash[taskName]
	if !ok {
		c.Logger.Error("can not find preset tasks", zap.String("task name", taskName))
		return
	}
	t.Closed = true
	delete(c.resources, taskName)
}

```

我们在Task中设计了一个新的变量Closed用于标识当前的任务是否已经被删除了。这是因为被删除的任务可能现在还在运行当中，我们通过该变量确认它已经不再运行了。

在一些场景中，我们也可以将标识任务是否已经结束的变量设计为通道类型或者context.Context，然后与select语句结合起来实现多路复用。我们在HTTP标准库中也经常看到这种用法，它可以判断通道的事件与其他事件哪一个先发生。

```plain
type Task struct {
	Visited     map[string]bool
	VisitedLock sync.Mutex

	//
	Closed bool

	Rule RuleTree
	Options
}

```

不过我们这里使用一个标识任务是否关闭的bool类型就足够了。在任务流程的核心位置，我们都需要检测该变量。检测到任务关闭时，就不再执行后续的流程。

具体操作是在request.Check方法中，加入对任务是否关闭的判断。

```plain
func (r *Request) Check() error {
	if r.Depth > r.Task.MaxDepth {
		return errors.New("max depth limit reached")
	}

	if r.Task.Closed {
		return errors.New("task has Closed")
	}

	return nil
}

```

接着，在任务的采集和调度的两个核心位置检测任务的有效性。一旦发现任务已经被关闭，它所有的请求将不再被调度和采集。

```plain
func (c *Crawler) CreateWork() {
	for {
		req := c.scheduler.Pull()
		if err := req.Check(); err != nil {
			c.Logger.Debug("check failed",
				zap.Error(err),
			)

			continue
		}
}

func (s *Schedule) Schedule() {
	var ch chan *spider.Request

	var req *spider.Request

	for {
		...
		// 请求校验
		if req != nil {
			if err := req.Check(); err != nil {
				zap.S().Debug("check failed",
					zap.Error(err),
				)
				req = nil
				ch = nil
				continue
			}
		}
}

```

下面让我们来验证一下任务的删除功能是否正常，首先启动一个Master和一个Worker服务。

```plain
» go run main.go master --id=3 --http=:8082  --grpc=:9092 --pprof=:9982
» go run main.go worker  --pprof=:9983

```

紧接着，调用Master的添加资源接口，可以看到爬虫任务是正常执行的。

```plain
» curl -H "content-type: application/json" -d '{"id":"zjx","name": "douban_book_list"}' <http://localhost:8082/crawler/resource>         jackson@localhost
{"id":"go.micro.server.worker-1", "Address":"192.168.0.105:9090"}

```

然后，我们调用Master的删除资源接口，从Worker中的日志可以看到，Worker监听到了删除资源的事件。在日志打印出 `"task has Closed"` 的错误信息之后，删除的爬虫任务将不再运行。

```plain
{"level":"INFO","ts":"2022-12-31T14:06:33.528+0800","caller":"engine/schedule.go:479","msg":"receive delete resource","spec":{"ID":"1609068436011356160","Name":"douban_book_list","AssignedNode":"go.micro.server.worker-1|192.168.0.105:9090","CreationTime":1672466784878532000}
{"level":"DEBUG","ts":"2022-12-31T14:06:33.845+0800","caller":"engine/schedule.go:336","msg":"check failed","error":"task has Closed"}
{"level":"DEBUG","ts":"2022-12-31T14:06:33.845+0800","caller":"engine/schedule.go:269","msg":"check failed","error":"task has Closed"}

```

此后，当我们再次调用Master的添加资源接口时，爬虫任务又将恢复如初。删除功能验证成功。

## 总结

好了，这节课，我们设计了将Master请求转发到Leader的功能，让所有的Master都具备了接收请求的能力。此外，我们还使用了原生的互斥锁解决了并发安全问题。因为通道并不总是解决并发安全问题的最佳方式，在这里如果我们使用通道会减慢程序的并发性，使代码变得不优雅。

最后，我们还实现了在Worker集群模式下任务的加载与监听。在初始化时，我们通过加载etcd中属于当前节点的资源获取了全量的爬虫任务。我们还启动了对etcd资源的监听，实现了资源的动态添加和删除。至此，Master与Worker的核心功能与交互都已经能够正常工作了。

## 课后题

最后，还是给你留一道思考题。

在我们的设计中，默认一个爬虫任务是不能够被添加多次的。那有没有一种场景，可以让同一个爬虫任务添加多次，也就是让多个Worker可以同时执行同一个爬虫任务呢? 如果有这样的场景，我们应该如何修改设计？

欢迎你在留言区与我交流讨论，我们下节课再见！