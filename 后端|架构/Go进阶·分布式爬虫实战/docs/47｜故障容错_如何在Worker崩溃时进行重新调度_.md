你好，我是郑建勋。

上一节课，我们用随机的方式为资源分配了它所属的Worker。这一节课，让我们更进一步优化资源的分配。

对资源进行分配不仅发生在正常的事件内，也可能发生在Worker节点崩溃等特殊时期。这时，我们需要将崩溃的Worker节点中的任务转移到其他节点。

## Master调度的时机

具体来说，分配资源的时机可能有下面三种情况。

- 当Master成为Leader时。
- 当客户端调用Master API进行资源的增删查改时。
- 当Master监听到Worker节点发生变化时。

其中，第二点“调用Master API进行资源的增删查改”我们会在这节课的最后完成，下面让我们实战一下剩下两点是如何实现资源的调度的。

### Master成为Leader时的资源调度

在日常实践中，Leader的频繁切换并不常见。不管是Master在初始化时选举成为了Leader，还是在中途由于其他Master异常退出导致Leader发生了切换，我们都要全量地更新一下当前Worker的节点状态以及资源的状态。

在Master成为Leader节点时，我们首先要利用m.updateWorkNodes 方法全量加载当前的Worker节点，同时利用m.loadResource 方法全量加载当前的爬虫资源。

```plain
func (m *Master) BecomeLeader() error {
	m.updateWorkNodes()
	if err := m.loadResource(); err != nil {
		return fmt.Errorf("loadResource failed:%w", err)
	}

	m.reAssign()

	atomic.StoreInt32(&m.ready, 1)
	return nil
}

```

接下来，调用reAssign方法完成一次资源的分配。m.reAssign会遍历资源，当发现有资源还没有分配节点时，将再次尝试将资源分配到Worker中。如果发现资源都已经分配给了对应的Worker，它就会查看当前节点是否存活。如果当前节点已经不存在了，就将该资源分配给其他的节点。

```plain
func (m *Master) reAssign() {
	rs := make([]*ResourceSpec, 0, len(m.resources))

	for _, r := range m.resources {
		if r.AssignedNode == "" {
			rs = append(rs, r)
			continue
		}

		id, err := getNodeID(r.AssignedNode)

		if err != nil {
			m.logger.Error("get nodeid failed", zap.Error(err))
		}

		if _, ok := m.workNodes[id]; !ok {
			rs = append(rs, r)
		}
	}
	m.AddResources(rs)
}

func (m *Master) AddResources(rs []*ResourceSpec) {
	for _, r := range rs {
		m.addResources(r)
	}
}

```

之前我们已经维护了资源的ID、事件以及分配的Worker节点等信息。 在这里让我们更进一步，当资源分配到节点上时，更新节点的状态。

为此我抽象出了一个新的结构NodeSpec，我们用它来描述Worker节点的状态。NodeSpec封装了Worker注册到etcd中的节点信息registry.Node。同时，我们额外增加了一个Payload字段，用于标识当前Worker节点的负载。当资源分配到对应的Worker节点上时，则更新Worker节点的状态，让Payload负载加1。

```plain
type NodeSpec struct {
	Node    *registry.Node
	Payload int
}

func (m *Master) addResources(r *ResourceSpec) (*NodeSpec, error) {
	ns, err := m.Assign(r)
	...
	r.AssignedNode = ns.Node.Id + "|" + ns.Node.Address
	_, err = m.etcdCli.Put(context.Background(), getResourcePath(r.Name), encode(r))
	m.resources[r.Name] = r
	ns.Payload++
	return ns, nil
}

```

### Worker节点发生变化时的资源更新

当我们发现Worker节点发生变化时，也需要全量完成一次更新。这是为了及时发现当前已经崩溃的Worker节点，并将这些崩溃的Worker节点下的任务转移给其他Worker节点运行。

如下所示，当Master监听workerNodeChange通道，发现Worker节点产生了变化之后，就会像成为Leader一样，更新当前节点与资源的状态，然后调用m.reAssign方法重新调度资源。

```plain
func (m *Master) Campaign() {
	...
	for {
		select {
		case resp := <-workerNodeChange:
			m.logger.Info("watch worker change", zap.Any("worker:", resp))
			m.updateWorkNodes()
			if err := m.loadResource(); err != nil {
				m.logger.Error("loadResource failed:%w", zap.Error(err))
			}
			m.reAssign()
		}
	}
}

```

## 负载均衡的资源分配算法

接下来，我们再重新看看资源的分配。上节课我们都是将资源随机分配到某一个Worker上的，但是在实践中很可能会有多个Worker，而为了对资源进行合理的分配，需要实现负载均衡，让Worker节点分摊工作量。

负载均衡分配资源的算法有很多，例如轮询法、加权轮询法、随机法、最小负载法等等，而根据实际场景，还可能需要有特殊的调度逻辑。这里我们实现一种简单的调度算法：最小负载法。在我们当前的场景中，最小负载法能够比较均衡地将爬虫任务分摊到Worker节点中。它每一次都将资源分配给具有最低负载的Worker节点，这依赖于我们维护的节点的状态。

如下所示，第一步我们遍历所有的Worker节点，找到合适的Worker节点。其实这一步可以完成一些简单的筛选，过滤掉一些不匹配的Worker。举一个例子，有些任务比较特殊，在计算时需要使用到GPU，那么我们就只能将它调度到有GPU的Worker节点中。这里我们没有实现更复杂的筛选逻辑，把当前全量的Worker节点都作为候选节点，放入到了candidates队列中。

```plain
func (m *Master) Assign(r *ResourceSpec) (*NodeSpec, error) {
	candidates := make([]*NodeSpec, 0, len(m.workNodes))

	for _, node := range m.workNodes {
		candidates = append(candidates, node)
	}

	//  找到最低的负载
	sort.Slice(candidates, func(i, j int) bool {
		return candidates[i].Payload < candidates[j].Payload
	})

	if len(candidates) > 0 {
		return candidates[0], nil
	}

	return nil, errors.New("no worker nodes")
}

```

第二步，根据负载对Worker队列进行排序。这里我使用了标准库sort中的Slice函数。Slice函数的第一个参数为candidates队列；第二个参数是一个函数，它可以指定排序的优先级条件，这里我们指定负载越小的Worker节点优先级越高。所以在排序之后，负载最小的Worker节点会排在前面。

第三步，取排序之后的第一个节点作为目标Worker节点。

现在，让我们来验证一下资源分配是否成功实现了负载均衡。首先，启动两个Worker节点。

```plain
» go run main.go worker --id=1 --http=:8080  --grpc=:9090
» go run main.go worker --id=2 --http=:8079  --grpc=:9089

```

接着，我们在配置文件中加入5个任务，并启动一个Master节点。

```plain
» go run main.go master --id=2 --http=:8081  --grpc=:9091

```

Master在初始化时就会完成任务的分配，我们可以在etcd中查看资源的分配情况，结果如下所示。

```plain
» docker exec etcd-gcr-v3.5.6 /bin/sh -c "/usr/local/bin/etcdctl get --prefix /resources"                                                                  jackson@bogon
/resources/douban_book_list
{"ID":"1604065810010083328","Name":"douban_book_list","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671274065865783000}
/resources/task-test-1
{"ID":"1604066677018857472","Name":"task-test-1","AssignedNode":"go.micro.server.worker-1|192.168.0.107:9090","CreationTime":1671274272579882000}
/resources/task-test-2
{"ID":"1604066699756179456","Name":"task-test-2","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671274278001122000}
/resources/task-test-3
{"ID":"1604066716206239744","Name":"task-test-3","AssignedNode":"go.micro.server.worker-1|192.168.0.107:9090","CreationTime":1671274281922539000}
/resources/xxx
{"ID":"1604065810026860544","Name":"xxx","AssignedNode":"go.micro.server.worker-1|192.168.0.107:9090","CreationTime":1671274065869756000}

```

观察资源分配的Worker节点，会发现当前有3个任务分配到了go.micro.server.worker-2，有2个节点分配到了go.micro.server.worker-1，说明我们现在的负载均衡策略符合预期。

接下来，让我们删除worker-1节点，验证一下worker-1中的资源是否会自动迁移到worker-2中。输入 `Ctrl+C` 退出worker-1节点，然后回到etcd中查看资源分配的情况，发现所有的资源都已经迁移到了worker-2中。这说明当Worker节点崩溃后，重新调度任务的策略是符合预期的。

```plain
» docker exec etcd-gcr-v3.5.6 /bin/sh -c "/usr/local/bin/etcdctl get --prefix /resources"                                                                  jackson@bogon
/resources/douban_book_list
{"ID":"1604065810010083328","Name":"douban_book_list","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671274065865783000}
/resources/task-test-1
{"ID":"1604069265235775488","Name":"task-test-1","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671274889679244000}
/resources/task-test-2
{"ID":"1604066699756179456","Name":"task-test-2","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671274278001122000}
/resources/task-test-3
{"ID":"1604069265252552704","Name":"task-test-3","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671274889683174000}
/resources/xxx
{"ID":"1604069265269329920","Name":"xxx","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671274889687807000}

```

最后我们来看看Master Leader切换时的情况。我们新建一个Master，它的ID为3。输入Ctrl+C中断之前的Master节点。

```plain
» go run main.go master --id=3 --http=:8082  --grpc=:9092

```

这时再次查看etcd中的资源分配情况，会发现资源的信息没有任何变化。这是符合预期的，因为当前的资源在之前都已经分配给了Worker，不需要再重新分配了。

## 实战Master资源处理API

接下来，让我们为Master实现对外暴露的API，方便外部客户端进行访问，实现资源的增删查改。按照惯例，我们仍然会为API实现GRPC协议和HTTP协议。

**首先，我们要在crawler.proto中书写Master服务的Protocol Buffer协议。**

我们先为Master加入两个RPC接口。其中，AddResource接口用于增加资源，参数为结构体ResourceSpec，表示添加资源的信息。其中最重要的参数是name，它标识了具体启动哪一个爬虫任务。返回值为结构体NodeSpec，NodeSpec描述了资源分配到Worker节点的信息。 DeleteResource接口用于删除资源，请求参数为资源信息，而不需要有任务返回值信息，因此这里定义为空结构体Empty。为了引用Empty，在这里我们导入了google/protobuf/empty.proto库。

```plain
syntax = "proto3";
option go_package = "proto/crawler";
import "google/api/annotations.proto";
import "google/protobuf/empty.proto";

service CrawlerMaster {
	rpc AddResource(ResourceSpec) returns (NodeSpec) {
	    option (google.api.http) = {
            post: "/crawler/resource"
            body: "*"
        };
	}
	rpc DeleteResource(ResourceSpec) returns (google.protobuf.Empty){
	    option (google.api.http) = {
            delete: "/crawler/resource"
            body: "*"
        };
	}
}

message ResourceSpec {
      string id = 1;
	  string name = 2;
	  string assigned_node = 3;
	  int64 creation_time = 4;
}

message NodeSpec {
    string id = 1;
    string Address = 2;
}

```

代码中的 option 是 [GRPC-gateway](https://github.com/grpc-ecosystem/grpc-gateway) 使用的信息，用于生成与GRPC方法对应的HTTP代理请求。在option中，AddResource对应的HTTP方法为POST，URL为/crawler/resource。

DeleteResource对应的URL仍然为/crawler/resource，不过HTTP方法为DELETE。 `body: "*"` 表示GRPC-gateway将接受HTTP Body中的信息，并会将其解析为对应的请求。

**下一步，执行protoc命令，生成对应的micro GRPC文件和HTTP代理文件。**

```plain
» protoc -I $GOPATH/src  -I .  --micro_out=. --go_out=.  --go-grpc_out=.  --grpc-gateway_out=logtostderr=true,allow_delete_body=true,register_func_suffix=Gw:. crawler.proto

```

这里的allow\_delete\_body表示对于HTTP DELETE方法，HTTP代理服务也可以解析Body中的信息，并将其转换为请求参数。

**接下来，我们需要为Master书写对应的方法，让Master实现micro生成的CrawlerMasterHandler接口。**

```plain
type CrawlerMasterHandler interface {
	AddResource(context.Context, *ResourceSpec, *NodeSpec) error
	DeleteResource(context.Context, *ResourceSpec, *empty.Empty) error
}

```

实现 DeleteResource 和 AddResource 这两个方法比较简单。其中，DeleteResource负责判断当前的任务名是否存在，如果存在则调用etcd delete方法删除资源Key，并更新节点的负载。而AddResource方法可以调用我们之前就写好的 m.addResources 方法来添加资源，返回资源分配的节点信息。

```plain
func (m *Master) DeleteResource(ctx context.Context, spec *proto.ResourceSpec, empty *empty.Empty) error {
	r, ok := m.resources[spec.Name]

	if !ok {
		return errors.New("no such task")
	}

	if _, err := m.etcdCli.Delete(context.Background(), getResourcePath(spec.Name)); err != nil {
		return err
	}

	if r.AssignedNode != "" {
		nodeID, err := getNodeID(r.AssignedNode)
		if err != nil {
			return err
		}

		if ns, ok := m.workNodes[nodeID]; ok {
			ns.Payload -= 1
		}
	}
	return nil
}

func (m *Master) AddResource(ctx context.Context, req *proto.ResourceSpec, resp *proto.NodeSpec) error {
	nodeSpec, err := m.addResources(&ResourceSpec{Name: req.Name})
	if nodeSpec != nil {
		resp.Id = nodeSpec.Node.Id
		resp.Address = nodeSpec.Node.Address
	}
	return err
}

```

**最后，我们还要调用micro生成的crawler.RegisterCrawlerMasterHandler函数，将Master注册为GRPC服务。** 这之后就可以正常处理客户端的访问了。

```plain
func RunGRPCServer(MasterService *master.Master, logger *zap.Logger, reg registry.Registry, cfg ServerConfig) {
	...
	if err := crawler.RegisterCrawlerMasterHandler(service.Server(), MasterService); err != nil {
		logger.Fatal("register handler failed", zap.Error(err))
	}

	if err := service.Run(); err != nil {
		logger.Fatal("grpc server stop", zap.Error(err))
	}
}

```

让我们来验证一下Master是否正在正常对外提供服务。

首先，启动Master。接着，通过HTTP访问Master提供的添加资源的接口。如下所示，添加资源“task-test-4”。

```plain
» go run main.go master --id=2 --http=:8081  --grpc=:9091
» curl -H "content-type: application/json" -d '{"id":"zjx","name": "task-test-4"}' http://localhost:8081/crawler/resource
{"id":"go.micro.server.worker-2", "Address":"192.168.0.107:9089"}

```

通过返回值可以看到，当前资源分配到了worker-2，worker-2的IP地址为"192.168.0.107:9089"。

查看etcd中的资源，发现资源已经成功写入了etcd，而且其中分配的Worker节点信息与HTTP接口返回的信息相同。

```plain
» docker exec etcd-gcr-v3.5.6 /bin/sh -c "/usr/local/bin/etcdctl get /resources/task-test-4"
/resources/task-test-4
{"ID":"1604109125694787584","Name":"task-test-4","AssignedNode":"go.micro.server.worker-2|192.168.0.107:9089","CreationTime":1671284393144648000}

```

接着，我们尝试调用Master服务的删除资源接口，删除我们刚刚生成添加的资源。

```plain
» curl -X DELETE  -H "content-type: application/json" -d '{"name": "task-test-4"}' http://localhost:8081/crawler/resource

```

再次查看etcd中的资源"task-test-4"，发现资源已经被删除了。Master API提供的添加和删除功能验证成功。

## 总结

这节课，我们对资源分配的时机和资源分配的算法进行了优化。我们模拟了Master和Worker节点崩溃的情况，并用简单的方式实现了节点的重新分配，让当前系统在分布式下具备了故障容错的特性。

在Master调度的时机上，当Master成为Leader，Worker节点崩溃，或者外部调用资源增删查改接口时，Leader 需要对资源进行重新调度。对于调度算法，为了实现负载的均衡，我选择了当前负载最低的Worker的节点作为了优先级最高的节点。在实践中，我们需要结合对应的业务场景设计出最合适的调度逻辑。

最后，我们还为Master实现了GRPC与HTTP API，让Masrer具备了添加资源和删除资源的能力。

## 课后题

这节课，我们用简单的方式实现了负载均衡的调度算法，但在生产实践中，调度器可能会更复杂。例如有些资源的负载会更大，有些资源只能在某一个Worker上执行，有些资源需要具有亲和性等等。你认为应该如何处理这些情况呢？

如何让我们的程序轻松地切换到另一个调度算法上？

（提示：可以参考 Kubernetes 对资源的复杂调度。）

欢迎你在留言区与我交流讨论，我们下节课见。