> 本课程为精品小课，不标配音频

你好，我是文强。

这节课我们继续完善基于 Raft 协议开发的分布式集群，我们会完成存储层和网络层这两部分的开发。接上节课的内容，我们首先来看一下 RaftMachineStorage 的实现逻辑。

## Raft 存储层：RaftMachineStorage

从代码上看，RaftMachineStorage 的作用是 **使用 RocksDB 来持久化存储 Raft 运行数据**。由于 RaftMachineStorage 的代码较多，这里我就不把全部代码贴出来了，建议你先去看一下文件 [《RaftMachineStorage》](https://github.com/robustmq/robustmq-geek/blob/main/src/placement-center/src/storage/raft.rs) 中的代码。

下面这张图是 RaftMachineStorage 的功能列表。

![图片](https://static001.geekbang.org/resource/image/fe/4a/fe0d4abcfdecb8d609b444e96aa2484a.png?wh=1084x1364)

从函数名称中可以知道，RaftMachineStorage 的功能就是对 Entry、HardState、ConfState、First Index、Last Idnex、Uncommit Index、Snapshot 等数据进行读写。

因为 RocksDB 是 KV 存储模型，因此我们需要先定义保存数据的 Key。来看下面这段代码：

```plain
// 存储未过期的第一个Entry的Index
pub fn key_name_by_first_index() -> String {
    return "/raft/first_index".to_string();
}

// 存储最新的一个 Entry 的Index
pub fn key_name_by_last_index() -> String {
    return "/raft/last_index".to_string();
}

// 保存 Raft 元数据 HardState
pub fn key_name_by_hard_state() -> String {
    return "/raft/hard_state".to_string();
}

// 保存 Raft 元数据 ConfState
pub fn key_name_by_conf_state() -> String {
    return "/raft/conf_state".to_string();
}

// 根据Entry的 Index 保存Entry 信息
pub fn key_name_by_entry(idx: u64) -> String {
    return format!("/raft/entry/{}", idx);
}

// 保存未正常 commit 的index列表
pub fn key_name_uncommit() -> String {
    return "/raft/uncommit_index".to_string();
}

// 保存快照信息
pub fn key_name_snapshot() -> String {
    return "/raft/snapshot".to_string();
}

```

在这段代码中，我们分别为保存 First Index、Last Index、HardState、ConfState、Entry、Uncommit、Snapshot 设计了保存的 Key。 因此你也就需要了解 Raft 运行过程中需要保存的这些数据。

从逻辑上来看，这些数据可以分为 **Entry**、 **Raft 运行状态**、 **快照** 三个类型。接下来我们来看这些数据的写入实现，因为读取类操作比较简单，就不展开了。先来看Entry。

```plain
  pub fn append(&mut self, entrys: &Vec<Entry>) -> RaftResult<()> {

        // 如果 Entry 为空，则不保存
        if entrys.len() == 0 {
            return Ok(());
        }

        // 判断 Entry 列表中的 index 是否符合规范
        let entry_first_index = entrys[0].index;

        let first_index = self.first_index();
        if first_index > entry_first_index {
            panic!(
                "overwrite compacted raft logs, compacted: {}, append: {}",
                first_index - 1,
                entry_first_index,
            );
        }

        let last_index = self.last_index();
        if last_index + 1 < entry_first_index {
            panic!(
                "raft logs should be continuous, last index: {}, new appended: {}",
                last_index, entry_first_index,
            );
        }

        // 循环保存 Entry
        for entry in entrys {
            debug!(">> save entry index:{}, value:{:?}", entry.index, entry);
            // 将 Entry 转化为 Vec 类型
            let data: Vec<u8> = Entry::encode_to_vec(&entry);
            // 将 Entry 保存在名为  /raft/entry/{index} 的 key 中
            let key = key_name_by_entry(entry.index);
            self.rocksdb_engine_handler
                .write(self.rocksdb_engine_handler.cf_cluster(), &key, &data)
                .unwrap();
            // 更新未 commit 的 index信息
            self.uncommit_index.insert(entry.index, 1);
            // 更新 last index
            self.save_last_index(entry.index).unwrap();
        }

        // 持久化存储未 commit 的 index
        self.save_uncommit_index();
        return Ok(());
    }

```

上面这段代码的功能是： **接收 Entry 列表并保存**。主要代码都加了注释，我们总结下核心逻辑：

1. 首先进行数据校验，判断 Entry 列表是否为空，以及 Entry 对应的 index 是否可用。

2. 循环以 /raft/entry/{index} 为 Key，在 RocksDB 中持久化保存 Entry，同时更新 last index 信息。

3. 因为 Entry 保存后，属于 uncommit 的数据，所以需要将 Entry 对应的 index 暂存到 uncomit 列表。


完成了这三步就完成了 Entry 和 Uncommit Index 的存储，同时也更新了最新的 Last Index。因为 Entry 是会过期的，所以当 Entry 过期时，First Index 也会被更新。

再来看 Raft 运行状态的写入实现。在上节课我们知道，Raft 运行状态主要是 HardfState 和 ConfState 两个数据，来看它的代码实现。

```plain

pub fn save_hard_state(&self, hs: HardState) -> Result<(), String> {
   let key = key_name_by_hard_state();
   let val = HardState::encode_to_vec(&hs);
   self.rocksdb_engine_handler
            .write(self.rocksdb_engine_handler.cf_cluster(), &key, &val)
}

pub fn save_conf_state(&self, cs: ConfState) -> Result<(), String> {
        let key = key_name_by_conf_state();
        let value = ConfState::encode_to_vec(&cs);
        self.rocksdb_engine_handler
            .write(self.rocksdb_engine_handler.cf_cluster(), &key, &value)
}

```

从上面代码可以看到，它的逻辑很简单，就是拿到数据写入到对应的 Key。但是关键问题是： **HardState 和 ConfState 是哪里来的（哪里生成的）？**

从技术上看，这两个数据的来源是 Raft 状态机，也就是 raft-rs 这个库的内部。raft-rs 实现了 Raft 的共识算法，在内部完成了发起选举、选举过程、心跳保持、用户数据保存等主要逻辑。也就说当 Raft 状态机向前驱动时，就会产生这两个数据，我们拿到这两个数据持久化存储即可。

最后来看 snapshot（快照）数据的写入。

当前快照数据的实现逻辑是：将所有未过期的 Entry 读取出来，整理成一份数据，再保存到 RocksDB 中，以便 Follower 拉取快照时更快。代码实现如下：

```plain
    pub fn create_snapshot(&mut self) {
        let mut sns = Snapshot::default();

        // 获取快照的元数据
        let meta = self.create_snapshot_metadata();
        sns.set_metadata(meta.clone());

        // 获取所有的 Entry，整理成一份数据
        let all_data = self.rocksdb_engine_handler.read_all();
        sns.set_data(serialize(&all_data).unwrap());

        // 将快照数据再持久化保存的一个固定的快照 Key 中。
        self.save_snapshot_data(sns);
        self.snapshot_metadata = meta.clone();
    }

    // 读取 HardState 和ConfState，构建快照的元数据
    pub fn create_snapshot_metadata(&self) -> SnapshotMetadata {
        let hard_state = self.hard_state();
        let conf_state = self.conf_state();

        let mut meta: SnapshotMetadata = SnapshotMetadata::default();
        meta.set_conf_state(conf_state);
        meta.set_index(hard_state.commit);
        meta.set_term(hard_state.term);
        return meta;
    }

```

代码注释比较清晰，这里就不展开了。需要注意的是，上面的实现会把快照数据再存储到 RocksDB，会导致重复存储两份数据。因此从实现来看是有优化空间的。

到这里，存储层的实现逻辑基本就讲完了。接下来我们看看网络层的实现。

为了帮助你更好地理解网络层的作用，我们需要先来理解一下 Raft 节点之间是如何通信的。

## Raft 节点间的通信流程

在我看到 raft-rs 这个库时，就有一个很大的疑问： **它既然只实现了共识算法，那么多个 Raft 节点之间的投票和选举、心跳保持、心跳超时 / Leader 宕机触发重新选举等等这些流程是怎么实现的呢？**

这里核心的是：多个节点间要如何交换信息？

回答这个问题之前，我们先来看下面这张 Raft 节点间交互的原理图。

![图片](https://static001.geekbang.org/resource/image/41/2b/418c3ed88byy0d399f4fyy80e391fe2b.jpeg?wh=1920x1080)

如上图所示，每个 Raft 节点上都会运行一个 Raft Machine（状态机）。每个状态机内部有定时驱动机制，用于定时驱动 Raft 状态向前运行。比如定时检测心跳是否过期，是否需要发起选举等等。

从代码实现的角度，也就是说，节点会根据自身的角色（比如 Leader 和 Follower）触发不同的行为，从而产生不同的 Message（消息），再将这些 Message 发送给其他 Raft 节点。那生成的都是哪些消息呢？ raft-rs 库定义了多种 MessageType 来标识不同类型的消息，代码如下所示：

```plain
#[derive(Clone,PartialEq,Eq,Debug,Hash)]
pub enum MessageType {
    MsgHup = 0,
    MsgBeat = 1,
    MsgPropose = 2,
    MsgAppend = 3,
    MsgAppendResponse = 4,
    MsgRequestVote = 5,
    MsgRequestVoteResponse = 6,
    MsgSnapshot = 7,
    MsgHeartbeat = 8,
    MsgHeartbeatResponse = 9,
    MsgUnreachable = 10,
    MsgSnapStatus = 11,
    MsgCheckQuorum = 12,
    MsgTransferLeader = 13,
    MsgTimeoutNow = 14,
    MsgReadIndex = 15,
    MsgReadIndexResp = 16,
    MsgRequestPreVote = 17,
    MsgRequestPreVoteResponse = 18,
}

```

从上面的消息类型可以看到，有投票、心跳、快照、Leader 切换等等不同类型的消息。举个例子，当用户往 Leader 节点写入数据，这条数据就需要发送给 Follwer 节点。因此 Leader 节点上的状态机就会生成一条类型为 MsgPropose 的Message，然后通过网络层将这个 Message 发送给 Follower 节点。Follower 节点遇到心跳超时时，本节点上的 Raft 状态机也会生成 MsgRequestVote 类型的消息，并将这条消息发送给其他节点。

了解完了 Raft 节点间的通信流程，接下来我们来看一下 Raft Node 网络层的代码实现。

## 基于 gRPC 的网络层实现

在上节课我们讲到，在网络层我们选择了 gRPC 来做通信协议。所以从代码实现的角度，整体就分为两步：

1. 定义 gRPC proto 文件
2. 实现 gRPC Service

先来看 gRPC proto 文件的定义。

```plain
// 定义名为SendRaftMessage的 rpc 方法，用于在两个Raft节点间的传递消息
rpc SendRaftMessage(SendRaftMessageRequest) returns(SendRaftMessageReply) {}

message SendRaftMessageRequest{
    // 需要传递的消息内容，是一个 bytes 类型
    bytes message = 1;
}

// 返回参数为空即可，即成功不需要返回值
message SendRaftMessageReply{
}

```

在上面的 proto 中，定义了一个名为 SendRaftMessage 的 RPC 方法，以及方法对应的请求和返回参数。

参数很简单，需要重点关注是 message 字段，它是 bytes 类型的数据，是由 raft-rs 中名为 Message 的结构体 encode 得到的。 **raft-rs 中的 Message 结构体，就是前面提到的 Raft 状态机驱动时生成的需要发给其他 Raft Node 的消息**。它的定义如下：

```plain
message Message {
    MessageType msg_type = 1;
    uint64 to = 2;
    uint64 from = 3;
    uint64 term = 4;
    uint64 log_term = 5;
    uint64 index = 6;
    repeated Entry entries = 7;
    uint64 commit = 8;
    uint64 commit_term = 15;
    Snapshot snapshot = 9;
    uint64 request_snapshot = 13;
    bool reject = 10;
    uint64 reject_hint = 11;
    bytes context = 12;
    uint64 deprecated_priority = 14;
    int64 priority = 16;
}

```

可以看到 Message 中有一个前面提到的 MessageType 字段，Message 用这个字段来区分不同类型的消息。结构体内容就不细讲了，大部分比较好理解，想了解更多可以去看这个 [《raft-rs eraftpb.proto》](https://github.com/tikv/raft-rs/blob/master/proto/proto/eraftpb.proto) 文件。

所以在网络层，我们只要将 Message encode 成 Vec，传递给其他节点即可，代码如下：

```plain
// 将 Message 转化为Vec<u8>类型
let data: Vec<u8> = Message::encode_to_vec(&msg);
// 初始化请求结构
let request = SendRaftMessageRequest { message: data };
// 将消息发送给其他节点
match send_raft_message(self.client_poll.clone(), vec![addr.clone()], request).await
    {
      Ok(_) => debug!("Send Raft message to node {} Successful.", addr),
      Err(e) => error!(
                 "Failed to send data to {}, error message: {}",
                  addr,
                  e.to_string()
                 ),
      }

```

接着来看 gRPC Service 的实现，代码如下：

```plain
  async fn send_raft_message(
        &self,
        request: Request<SendRaftMessageRequest>,
    ) -> Result<Response<SendRaftMessageReply>, Status> {

        // 将 SendRaftMessageRequest 中的 message 字段 decode 为 Message 结构体
       let message = raftPreludeMessage::decode(request.into_inner().message.as_ref())
            .map_err(|e| Status::invalid_argument(e.to_string()))?;

        // 将Message 传递给 Raft 状态机去执行 Raft 协议算法的逻辑
        // 这部分在第十章会细讲，可以暂时忽略
        match self
            .placement_center_storage
            .apply_raft_message(message, "send_raft_message".to_string())
            .await
        {
            Ok(_) => return Ok(Response::new(SendRaftMessageReply::default())),
            Err(e) => {
                return Err(Status::cancelled(
                    PlacementCenterError::RaftLogCommitTimeout(e.to_string()).to_string(),
                ));
            }
        }
    }

```

上面这段代码的核心逻辑是：接收参数、decode Message、将得到的 Message 传递给 Raft 状态机执行，完成比如投票、选举、保存用户数据等等行为。所以说，网络层本身是不做业务逻辑处理的，当 Raft Node 拿到消息后，需要将数据传递给 Raft 状态机进行处理。

至于 Raft 状态机的实现，我们下节课会完整讲解，敬请期待！

## 总结

> tips：每节课的代码都能在项目 [https://github.com/robustmq/robustmq-geek](https://github.com/robustmq/robustmq-geek) 中找到源码，有兴趣的同学可以下载源码来看。

这两节课我们基于 RocksDB 完成了存储层的开发，基于 gRPC 完成了网络层的开发。

从存储层的视角，我们主要是对 First Index、Last Index、HardState、ConfState、Entry、Uncommit、Snapshot 这 7 个数据进行读写。

从网络层的视角，核心是在多个 RaftNode 之间传递 Raft 状态机生成的消息，从而完成比如投票、选举等核心流程。

Raft Node 是指一个唯一的 Raft 投票者，需要通过唯一的 ID 来标识，不能重复。

## 思考题

这里是本节课推荐的相关 issue 的任务列表，请点击查看 [《Good First Issue》](http://www.robustmq.com/docs/robustmq-tutorial-cn/%e8%b4%a1%e7%8c%ae%e6%8c%87%e5%8d%97/good-first-issue/)。 另外欢迎给我的项目 [https://github.com/robustmq/robustmq](https://github.com/robustmq/robustmq) 点个 Star 啊！