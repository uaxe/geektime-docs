你好，我是郑建勋。

上一节课，我们搭建起了Master的基本框架。这一节课，让我们接着实现分布式Master的核心功能：选主。

## etcd选主API

我们在讲解架构设计时提到过，可以开启多个Master来实现分布式服务的故障容错。其中，只有一个Master能够成为Leader，只有Leader能够完成任务的分配，只有Leader能够处理外部访问。当Leader崩溃时，其他的Master将竞争上岗成为Leader。

实现分布式的选主并没有想象中那样复杂，在我们的项目中，只需要借助分布式协调服务etcd就能实现。 [etcd clientv3](https://pkg.go.dev/go.etcd.io/etcd/clientv3/concurrency) 已经为我们封装了对分布式选主的实现，核心的API如下。

```plain
// client/v3/concurrency
func NewSession(client *v3.Client, opts ...SessionOption) (*Session, error)
func NewElection(s *Session, pfx string) *Election
func (e *Election) Campaign(ctx context.Context, val string) error
func (e *Election) Leader(ctx context.Context) (*v3.GetResponse, error)
func (e *Election) Observe(ctx context.Context) <-chan v3.GetResponse
func (e *Election) Resign(ctx context.Context) (err error)

```

我来解释一下这些API的含义。

- NewSession函数：创建一个与etcd服务端带租约的会话。
- NewElection函数：创建一个选举对象Election，Election有许多方法。
- Election.Leader方法可以查询当前集群中的Leader信息。
- Election.Observe 可以接收到当前Leader的变化
- Election.Campaign方法：开启选举，该方法会阻塞住协程，直到调用者成为Leader。

## 实现Master选主与故障容错

现在让我们在项目中实现分布式选主算法，核心逻辑位于Master.Campaign方法中，完整的代码位于 [v0.3.5分支](https://github.com/dreamerjackson/crawler)。

```plain
func (m *Master) Campaign() {
	endpoints := []string{m.registryURL}
	cli, err := clientv3.New(clientv3.Config{Endpoints: endpoints})
	if err != nil {
		panic(err)
	}

	s, err := concurrency.NewSession(cli, concurrency.WithTTL(5))
	if err != nil {
		fmt.Println("NewSession", "error", "err", err)
	}
	defer s.Close()

	// 创建一个新的etcd选举election
	e := concurrency.NewElection(s, "/resources/election")
	leaderCh := make(chan error)
	go m.elect(e, leaderCh)
	leaderChange := e.Observe(context.Background())
	select {
	case resp := <-leaderChange:
		m.logger.Info("watch leader change", zap.String("leader:", string(resp.Kvs[0].Value)))
	}

	for {
		select {
		case err := <-leaderCh:
			if err != nil {
				m.logger.Error("leader elect failed", zap.Error(err))
				go m.elect(e, leaderCh)
			} else {
				m.logger.Info("master change to leader")
				m.leaderID = m.ID
				if !m.IsLeader() {
					m.BecomeLeader()
				}
			}
		case resp := <-leaderChange:
			if len(resp.Kvs) > 0 {
				m.logger.Info("watch leader change", zap.String("leader:", string(resp.Kvs[0].Value)))
			}
		}
	}
}

```

我们一步步来解析这段分布式选主的代码。

1. 第3行调用clientv3.New函数创建一个etcd clientv3的客户端。
2. 第15行， `concurrency.NewElection(s, "/resources/election")` 意为创建一个新的etcd选举对象。其中的第二个参数就是所有Master都在抢占的Key，抢占到该Key的Master将变为Leader。

在etcd中，一般都会选择这种目录形式的结构作为Key，这种方式可以方便我们进行前缀查找。例如，Kubernetes 资源在 etcd 中的存储格式为 `prefix/资源类型/namespace/资源名称` 。

```plain
/registry/clusterrolebindings/system:coredns
/registry/clusterroles/system:coredns
/registry/configmaps/kube-system/coredns
/registry/deployments/kube-system/coredns
/registry/replicasets/kube-system/coredns-7fdd6d65dc
/registry/secrets/kube-system/coredns-token-hpqbt
/registry/serviceaccounts/kube-system/coredns

```

3. 第17行 `go m.elect(e, leaderCh)` 代表开启一个新的协程，让当前的Master进行Leader的选举。如果集群中已经有了其他的Leader，当前协程将陷入到堵塞状态。如果当前Master选举成功，成为了Leader，e.Campaign方法会被唤醒，我们将其返回的消息传递到ch通道中。

```plain
func (m *Master) elect(e *concurrency.Election, ch chan error) {
	// 堵塞直到选取成功
	err := e.Campaign(context.Background(), m.ID)
	ch <- err
}

```

e.Campaign方法的第二个参数为Master成为Leader后，设置到Key中的Value值。在这里，我们将Master ID作为Value值。 Master的ID是初始化时设置的，它当前包含了Master的序号、Master的IP地址和监听的GRPC地址。

其实，Master的ID就足够标识唯一的Master了，但这里还存储了 Master IP，是为了方便后续其他的Master拿到Leader的IP地址，从而对Leader进行访问。

```plain
// master/master.go
func New(id string, opts ...Option) (*Master, error) {
	m := &Master{}

	options := defaultOptions
	for _, opt := range opts {
		opt(&options)
	}
	m.options = options

	ipv4, err := getLocalIP()
	if err != nil {
		return nil, err
	}
	m.ID = genMasterID(id, ipv4, m.GRPCAddress)
	m.logger.Sugar().Debugln("master_id:", m.ID)
	go m.Campaign()

	return &Master{}, nil
}

type Master struct {
	ID        string
	ready     int32
	leaderID  string
	workNodes map[string]*registry.Node
	options
}

func genMasterID(id string, ipv4 string, GRPCAddress string) string {
	return "master" + id + "-" + ipv4 + GRPCAddress
}

```

获取本机的IP地址有一个很简单的方式，那就是遍历所有网卡，找到第一个IPv4地址，代码如下所示。

```plain
func getLocalIP() (string, error) {
	var (
		addrs []net.Addr
		err   error
	)
	// 获取所有网卡
	if addrs, err = net.InterfaceAddrs(); err != nil {
		return "", err
	}
	// 取第一个非lo的网卡IP
	for _, addr := range addrs {
		if ipNet, isIpNet := addr.(*net.IPNet); isIpNet && !ipNet.IP.IsLoopback() {
			if ipNet.IP.To4() != nil {
				return ipNet.IP.String(), nil
			}
		}
	}

	return "", errors.New("no local ip")
}

```

4. 当Master并行进行选举的同时（第18行），调用e.Observe监听Leader的变化。e.Observe函数会返回一个通道，当Leader状态发生变化时，会将当前Leader的信息发送到通道中。在这里我们初始化时首先堵塞读取了一次e.Observe返回的通道信息。因为只有成功收到e.Observe返回的消息，才意味着集群中已经存在Leader，表示集群完成了选举。

5. 第24行，我们在for循环中使用select监听了多个通道的变化，其中通道leaderCh负责监听当前Master是否当上了Leader，而leaderChange负责监听当前集群中Leader是否发生了变化。


书写好Master的选主逻辑之后，接下来让我们执行Master程序，完整的代码位于 [v0.3.5分支](https://github.com/dreamerjackson/crawler)。

```plain
» go run main.go master --id=2 --http=:8081  --grpc=:9091

```

由于当前只有一个Master，因此当前Master一定会成为Leader。我们可以看到打印出的当前Leader的信息：master2-192.168.0.107:9091。

```plain
{"level":"INFO","ts":"2022-12-07T18:23:28.494+0800","logger":"master","caller":"master/master.go:65","msg":"watch leader change","leader:":"master2-192.168.0.107:9091"}
{"level":"INFO","ts":"2022-12-07T18:23:28.494+0800","logger":"master","caller":"master/master.go:65","msg":"watch leader change","leader:":"master2-192.168.0.107:9091"}
{"level":"INFO","ts":"2022-12-07T18:23:28.494+0800","logger":"master","caller":"master/master.go:75","msg":"master change to leader"}
{"level":"DEBUG","ts":"2022-12-07T18:23:38.500+0800","logger":"master","caller":"master/master.go:87","msg":"get Leader","Value":"master2-192.168.0.107:9091"}

```

如果这时我们查看etcd的信息，会看到自动生成了 `/resources/election/xxx` 的Key，并且它的Value是我们设置的 `master2-192.168.0.107:9091`。

```plain
» docker exec etcd-gcr-v3.5.6 /bin/sh -c "/usr/local/bin/etcdctl get --prefix /"                                                                           jackson@bogon

/micro/registry/go.micro.server.master/go.micro.server.master-2
{"name":"go.micro.server.master","version":"latest","metadata":null,"endpoints":[{"name":"Greeter.Hello","request":{"name":"Request","type":"Request","values":[{"name":"name","type":"string","values":null}]},"response":{"name":"Response","type":"Response","values":[{"name":"greeting","type":"string","values":null}]},"metadata":{"endpoint":"Greeter.Hello","handler":"rpc","method":"POST","path":"/greeter/hello"}}],"nodes":[{"id":"go.micro.server.master-2","address":"192.168.0.107:9091","metadata":{"broker":"http","protocol":"grpc","registry":"etcd","server":"grpc","transport":"grpc"}}]}

/resources/election/3f3584fc571ae898
master2-192.168.0.107:9091

```

如果我们再启动一个新的Master程序，会发现当前获取到的Leader仍然是 `master2-192.168.0.107:9091`。

```plain
» go run main.go master --id=3 --http=:8082  --grpc=:9092
{"level":"DEBUG","ts":"2022-12-07T18:23:52.371+0800","logger":"master","caller":"master/master.go:33","msg":"master_id: master3-192.168.0.107:9092"}
{"level":"INFO","ts":"2022-12-07T18:23:52.387+0800","logger":"master","caller":"master/master.go:65","msg":"watch leader change","leader:":"master2-192.168.0.107:9091"}
{"level":"DEBUG","ts":"2022-12-07T18:24:02.393+0800","logger":"master","caller":"master/master.go:87","msg":"get Leader","value":"master2-192.168.0.107:9091"}

```

再次查看etcd的信息，会发现 `go.micro.server.master-3` 也成功注册到etcd中了，并且c在/resources/election 下方注册了自己的Key，但是该Key比master-2要大。

```plain
/micro/registry/go.micro.server.master/go.micro.server.master-2
{"name":"go.micro.server.master","version":"latest","metadata":null,"endpoints":[{"name":"Greeter.Hello","request":{"name":"Request","type":"Request","values":[{"name":"name","type":"string","values":null}]},"response":{"name":"Response","type":"Response","values":[{"name":"greeting","type":"string","values":null}]},"metadata":{"endpoint":"Greeter.Hello","handler":"rpc","method":"POST","path":"/greeter/hello"}}],"nodes":[{"id":"go.micro.server.master-2","address":"192.168.0.107:9091","metadata":{"broker":"http","protocol":"grpc","registry":"etcd","server":"grpc","transport":"grpc"}}]}
/micro/registry/go.micro.server.master/go.micro.server.master-3
{"name":"go.micro.server.master","version":"latest","metadata":null,"endpoints":[{"name":"Greeter.Hello","request":{"name":"Request","type":"Request","values":[{"name":"name","type":"string","values":null}]},"response":{"name":"Response","type":"Response","values":[{"name":"greeting","type":"string","values":null}]},"metadata":{"endpoint":"Greeter.Hello","handler":"rpc","method":"POST","path":"/greeter/hello"}}],"nodes":[{"id":"go.micro.server.master-3","address":"192.168.0.107:9092","metadata":{"broker":"http","protocol":"grpc","registry":"etcd","server":"grpc","transport":"grpc"}}]}
/resources/election/3f3584fc571ae898
master2-192.168.0.107:9091
/resources/election/3f3584fc571ae8a9
master3-192.168.0.107:9092

```

到这里，我们就实现了Master的选主操作，所有的Master都只认定一个Leader。当我们终止master-2程序，在master-3程序中会立即看到如下日志，说明当前的Leader已经顺利完成了切换，master-3当选为了新的Leader。

```plain
{"level":"INFO","ts":"2022-12-12T00:46:58.288+0800","logger":"master","caller":"master/master.go:93","msg":"watch leader change","leader:":"master3-192.168.0.107:9092"}
{"level":"INFO","ts":"2022-12-12T00:46:58.289+0800","logger":"master","caller":"master/master.go:85","msg":"master change to leader"}
{"level":"DEBUG","ts":"2022-12-12T00:47:18.296+0800","logger":"master","caller":"master/master.go:107","msg":"get Leader","value":"master3-192.168.0.107:9092"}

```

当我们再次查看etcd，发现/resources/election/路径下只剩下master-3程序的注册信息了，证明Master的选举成功。

```plain
» docker exec etcd-gcr-v3.5.6 /bin/sh -c "/usr/local/bin/etcdctl get --prefix /"                                                                           jackson@bogon
/micro/registry/go.micro.server.master/go.micro.server.master-3
{"name":"go.micro.server.master","version":"latest","metadata":null,"endpoints":[{"name":"Greeter.Hello","request":{"name":"Request","type":"Request","values":[{"name":"name","type":"string","values":null}]},"response":{"name":"Response","type":"Response","values":[{"name":"greeting","type":"string","values":null}]},"metadata":{"endpoint":"Greeter.Hello","handler":"rpc","method":"POST","path":"/greeter/hello"}}],"nodes":[{"id":"go.micro.server.master-3","address":"192.168.0.107:9092","metadata":{"broker":"http","protocol":"grpc","registry":"etcd","server":"grpc","transport":"grpc"}}]}
/resources/election/3f3584fc571ae8a9
master3-192.168.0.107:9092

```

## etcd选主原理

经过上面的实践，我们可以看到，借助etcd，分布式选主变得非常容易了，现在我们来看一看etcd实现分布式选主的原理。它的核心代码位于Election.Campaign方法中，如下所示，下面代码做了简化，省略了对异常情况的处理。

```plain
func (e *Election) Campaign(ctx context.Context, val string) error {
	s := e.session
	client := e.session.Client()

	k := fmt.Sprintf("%s%x", e.keyPrefix, s.Lease())
	txn := client.Txn(ctx).If(v3.Compare(v3.CreateRevision(k), "=", 0))
	txn = txn.Then(v3.OpPut(k, val, v3.WithLease(s.Lease())))
	txn = txn.Else(v3.OpGet(k))
	resp, err := txn.Commit()
	if err != nil {
		return err
	}
	e.leaderKey, e.leaderRev, e.leaderSession = k, resp.Header.Revision, s
	_, err = waitDeletes(ctx, client, e.keyPrefix, e.leaderRev-1)
	if err != nil {
		// clean up in case of context cancel
		select {
		case <-ctx.Done():
			e.Resign(client.Ctx())
		default:
			e.leaderSession = nil
		}
		return err
	}
	e.hdr = resp.Header

	return nil
}

```

Campaign首先用了一个事务操作在要抢占的e.keyPrefix路径下维护一个Key。其中，e.keyPrefix是Master要抢占的etcd路径，在我们的项目中为/resources/election/。这段事务操作会首选判断当前生成的Key（例如/resources/election/3f3584fc571ae8a9）是否已经在etcd中了。如果不存在，才会创建该Key。这样，每一个Master都会在/resources/election/下维护一个Key，并且当前的Key是带租约的。

Campaign第二步会调用waitDeletes函数堵塞等待，直到自己成为Leader为止。那什么时候当前Master会成为Leader呢？

waitDeletes函数会调用client.Get获取到当前争抢的/resources/election/路径下具有最大版本号的Key，并调用waitDelete函数等待该Key被删除。而waitDelete会调用client.Watch来完成对特定版本Key的监听。

当前Master需要监听这个最大版本号Key的删除事件。当这个特定的Key被删除，就意味着已经没有比当前Master创建的Key更早的Key了，因此当前的Master理所当然就排队成为了Leader。

```plain
func waitDeletes(ctx context.Context, client *v3.Client, pfx string, maxCreateRev int64) (*pb.ResponseHeader, error) {
	getOpts := append(v3.WithLastCreate(), v3.WithMaxCreateRev(maxCreateRev))
	for {
		resp, err := client.Get(ctx, pfx, getOpts...)
		if err != nil {
			return nil, err
		}
		if len(resp.Kvs) == 0 {
			return resp.Header, nil
		}
		lastKey := string(resp.Kvs[0].Key)
		if err = waitDelete(ctx, client, lastKey, resp.Header.Revision); err != nil {
			return nil, err
		}
	}
}

func waitDelete(ctx context.Context, client *v3.Client, key string, rev int64) error {
	cctx, cancel := context.WithCancel(ctx)
	defer cancel()

	var wr v3.WatchResponse
	wch := client.Watch(cctx, key, v3.WithRev(rev))
	for wr = range wch {
		for _, ev := range wr.Events {
			if ev.Type == mvccpb.DELETE {
				return nil
			}
		}
	}
	if err := wr.Err(); err != nil {
		return err
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	return fmt.Errorf("lost watcher waiting for delete")
}

```

这种监听方式还避免了惊群效应，因为当Leader崩溃后，并不会唤醒所有在选举中的Master。只有当队列中的前一个Master创建的Key被删除，当前的Master才会被唤醒。也就是说，每一个Master都在排队等待着前一个Master退出，这样Master就以最小的代价实现了对Key的争抢。

## 总结

这节课，我们借助etcd实现了分布式Master的选主，确保了在同一时刻只能存在一个Leader。此外，我们还实现了Master的故障容错能力。

etcd clientv3为我们封装了选主的实现，它的实现方式也很简单，通过监听最近的Key的DELETE事件，我们实现了所有的节点对同一个Key的抢占，同时还避免了集群可能出现的惊群效应。在实践中，我们也可以使用其他的分布式协调组件（例如ZooKeeper、Consul）帮助我们实现选主，它们的实现原理都和etcd类似。

## 课后题

最后，给你留一道思考题吧。

其实，利用MySQL也可以实现分布式的选主，你知道如何实现吗？（参考： [http://code.openark.org/blog/mysql/leader-election-using-mysql](http://code.openark.org/blog/mysql/leader-election-using-mysql)）

欢迎你给我留言交流讨论，我们下节课见！