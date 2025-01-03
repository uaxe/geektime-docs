你好，我是雪飞。

上节课我和你一起学习了 CKA 真题的上半部分，这节课，我们继续真题串讲的下半部分。

## 第十题 PV

#### 题目

创建名为 “app-config” 的 Persistent Volume，容量为 1Gi，访问模式为 ReadWriteMany。Volume 类型为 hostPath，位于 /srv/app-config。

#### 答题要点

这道题主要考 hostPath 类型的 PV，知识点参考专栏 [第 11 课](https://time.geekbang.org/column/article/795256)，下面我给出参考答案。

#### 参考答案

1. 按照题目要求，编写 PV 的 YAML 文件（pv.yaml）。

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: app-config
spec:
  capacity:
    storage: 1Gi  # 题目要求 1Gi
  accessModes:
    - ReadWriteMany  # 题目要求 ReadWriteMany
  hostPath:
    path: "/srv/app-config"   # 注意有引号

```

2. 部署 PV。

```bash
kubectl apply -f pv.yaml

```

#### 验证

查看 PV 状态，检查是否符合题目要求。

```bash
kubectl get pv app-config

```

## 第十一题 PVC

#### 题目

创建一个新的 PersistentVolumeClaim：

- 名称：pv-volume
- Class：csi-hostpath-sc
- 容量：10Mi

创建一个新的 Pod，来将 PersistentVolumeClaim 作为 volume 进行挂载：

- 名称：web-server
- Image：nginx:1.16
- 挂载路径：/usr/share/nginx/html

配置新的 Pod，以对 volume 具有 ReadWriteOnce 权限。

最后，使用 kubectl edit 或 kubectl patch 将 PersistentVolumeClaim 的容量扩展为 70Mi，并记录此更改。

#### 答题要点

这道题主要考 PVC 的创建和挂载使用，知识点参考专栏 [第 11 课](https://time.geekbang.org/column/article/795256)。最后使用 “kubectl edit” 命令扩容时要加上 “–record” 参数记录此次更改。这道题相对复杂，要编写 PVC 和 Pod 两个 YAML 文件，做的时候一定要细心，YAML 文件的写法还是可以参考题目中给出的参考文档。

#### 参考答案

1. 按照题目要求，编写 PVC 的 YAML 文件（pvc.yaml）。

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pv-volume
spec:
  storageClassName: csi-hostpath-sc
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Mi

```

2. 部署并查看 PVC。

```bash
kubectl apply -f pvc.yaml
kubectl get pvc  # 查看 STATUS 是否为 "Bound"

```

3. 按照题目要求，编写 Pod 的 YAML 文件（pod-pvc.yaml）。

```yaml
# pod-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
spec:
  containers:
  - image: nginx:1.16
    name: web-server
    volumeMounts:    # 挂载 PVC
      - mountPath: "/usr/share/nginx/html"
        name: pvc-volume
  volumes:    # 注意 volumes 层级
    - name: pvc-volume
      persistentVolumeClaim:
        claimName: pv-volume

```

4. 部署并查看 Pod。

```bash
kubectl apply -f pod-pvc.yaml
kubectl get pod web-server  # 查看 READY 是否为 1/1

```

5. 使用 “kubectl edit” 命令实时编辑 PVC 的 YAML 文件，然后找到 spec 属性中的 storage 属性，修改为 70Mi，保存后立刻生效。

```bash
kubectl edit pvc pv-volume --record

```

### ![图片](https://static001.geekbang.org/resource/image/d2/52/d2650dc405e8ba8bae755a3c100ba552.png?wh=1208x692)

#### 验证

查看 PVC 状态，检查状态为 Bound，同时查看 Pod 状态，检查 READY 状态为 1/1。

```bash
kubectl get pv app-config
kubectl get pod web-server

```

## 第十二题 Pod 日志

#### 题目

监控 pod “foo” 的日志并：

- 提取与错误 RLIMIT\_NOFILE 相对应的日志行
- 将这些日志行写入 /opt/KUTR00101/foo

#### 答题要点

这道题主要考查看 Pod 日志，使用一条命令就可以完成题目要求。知识点参考专栏 [第 16 课](https://time.geekbang.org/column/article/797497)，下面我给出参考答案。

#### 参考答案

```bash
kubectl logs foo | grep "RLIMIT_NOFILE" > /opt/KUTR00101/foo

```

#### 验证

查看文件中是否有满足条件的日志。

```bash
cat /opt/KUTR00101/foo

```

## 第十三题 边车容器

#### 题目

将一个现有的 Pod 集成到 Kubernetes 的内置日志记录体系结构中（例如 kubectl logs）。添加 streaming sidecar 容器是实现此要求的一种好方法。

使用 busybox Image 来将名为 “sidecar” 的 sidecar 容器添加到现有的 Pod “11-factor-app” 中。新的 sidecar 容器必须运行以下命令：

```bash
/bin/sh -c tail -n+1 -f /var/log/11-factor-app.log

```

使用挂载在 “/var/log” 的 Volume，使日志文件 11-factor-app.log 可用于 sidecar 容器。

除了添加所需要的 volume mount 以外，请勿更改现有容器的规格。

#### 答题要点

这道题主要考查看 Pod 的多容器及共享存储。知识点参考专栏 [第 5 课](https://time.geekbang.org/column/article/793385)。

由于 Pod 不能通过 “kubectl edit” 在线增加容器，所以解题思路如下：

1. 先导出现有的 Pod “11-factor-app” 的 YAML 文件。
2. 修改 Pod 的 YAML 文件，增加边车容器以及挂载 Volume。
3. 删除旧的 Pod，然后再部署新的 Pod。

#### 参考答案

1. 导出现有 Pod 的 YAML 文件（tmp-pod.yaml）。

```bash
kubectl get pod 11-factor-app -o yaml > tmp-pod.yaml

```

2. 编辑 tmp-pod.yaml 文件，注意看备注新增的部分。

```yaml
vi tmp-pod.yaml  # 通过 vi 编辑器编辑 YAML 文件

# tmp-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: 11-factor-app
spec:
  containers:
  - args:
    - /bin/sh
    - -c
    - |
      i=0; while true; do
        echo "$(date) INFO $i" >> /var/log/11-factor-app.log;
        i=$((i+1));
        sleep 1;
      done
    name: count
    image: busybox:1.35
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: auditlog
      mountPath: /var/log
  - name: sidecar           #新增
    image: busybox:1.35     #新增
    args: [/bin/sh, -c, 'tail -n+1 -f /var/log/11-factor-app.log']  #新增
    volumeMounts:           #新增
    - name: auditlog        #新增
      mountPath: /var/log   #新增
  volumes:
  - name: auditlog
    emptyDir: {}

```

3. 删除旧的 Pod，然后等待删除完成后，部署新的 Pod。

```yaml
kubectl delete pod 11-factor-app
kubectl apply -f tmp-pod.yaml

```

#### 验证

查看边车容器日志。

```bash
kubectl logs 11-factor-app -c sidecar

```

## 第十四题 集群升级

#### 题目

现有的 Kubernetes 集群正在运行版本 1.29.5。仅将 master 节点上的所有 Kubernetes 控制平面和节点组件升级到版本 1.29.6。确保在升级之前 drain master 节点，并在升级后 uncordon master 节点。

可以使用以下命令，通过 ssh 连接到 master 节点。

```plain
ssh master01

```

可以使用以下命令，在该 master 节点上获取更高权限。

```plain
sudo -i

```

另外，在主节点上升级 kubelet 和 kubectl。请不要升级工作节点、etcd、container 管理器、CNI 插件、DNS 服务或任何其他插件。

#### 答题要点

这道题主要考 K8s 版本升级，知识点参考专栏 [第 17 课](https://time.geekbang.org/column/article/797799)，由于 Master 节点的升级步骤已经在前面的课程中详细介绍过，下面我直接给出参考答案。

#### 参考答案

```bash
# 1、停止调度，将 node 调为 SchedulingDisabled
kubectl cordon master01

# 2、驱逐节点
kubectl drain master01 --ignore-daemonsets

# 3、ssh 到 master01 节点，并切换到 root 下
ssh master01
sudo -i

# 4、由于操作系统是 Ubuntu，所以安装管理软件使用 apt-get 而不是 yum
# 更新软件库
apt-get update

# 5、获取具体的版本号，会返回 Version: 1.29.6-1.1
apt-cache show kubeadm | grep 1.29.6

# 6、升级 kubeadm
apt-get install kubeadm=1.29.6-1.1 –y

# 7、验证升级计划
kubeadm upgrade plan

# 8、执行升级，大约等5分钟
# 题目要求不升级 etcd，使用"--etcd-upgrade=false" 参数
kubeadm upgrade apply v1.29.6 --etcd-upgrade=false

# 9、升级 kubelet 和 kubectl
apt-get install kubelet=1.29.6-1.1 kubectl=1.29.6-1.1 -y

# 10、重启 kubelet
systemctl restart kubelet

# 11、返回到初始节点
exit

# 12、设置 Master 节点为可调度
kubectl uncordon master01

```

#### 验证

检查 master01 节点是否为 Ready，并且为题目要求升级到的版本。

```bash
kubectl get node

```

## 第十五题 etcd 备份与恢复

#### 题目

你必须从 master01 主机执行所需的 etcdctl 命令。

首先，为运行在 [https://127.0.0.1:2379](https://127.0.0.1:2379) 上的现有 etcd 实例创建快照并将快照保存到 “/var/lib/backup/etcd-snapshot.db”。提供了以下 TLS 证书和密钥，以通过 etcdctl 连接到服务器。

- CA 证书: /opt/KUIN00601/ca.crt
- 客户端证书: /opt/KUIN00601/etcd-client.crt
- 客户端密钥: /opt/KUIN00601/etcd-client.key

为给定实例创建快照预计能在几秒钟内完成。如果该操作似乎挂起，则命令可能有问题。用 CTRL + C 来取消操作，然后重试。

然后通过位于 “/data/backup/etcd-snapshot-previous.db” 的先前备份的快照进行还原。

#### 答题要点

这道题主要考 etcd 的备份与恢复，知识点参考专栏 [第 17 课](https://time.geekbang.org/column/article/797799)，下面我给出参考答案。

#### 参考答案

1. 备份快照。

```bash
ETCDCTL_API=3 etcdctl snapshot save /var/lib/backup/etcd-snapshot.db \
--endpoints=https://127.0.0.1:2379 \
--cacert="/opt/KUIN00601/ca.crt" \
--cert="/opt/KUIN00601/etcd-client.crt" \
--key="/opt/KUIN00601/etcd-client.key"

```

2. 恢复快照。

```bash
# 1、暂停系统组件
mv /etc/kubernetes/manifests /etc/kubernetes/manifests.bak

# 2、备份当前 Etcd 的数据目录
systemctl cat etcd  # 查看数据目录，--data-dir 值，通常是 /var/lib/etcd/
mv /var/lib/etcd/ /var/lib/etcd.bak

# 3、恢复数据
ETCDCTL_API=3 etcdctl snapshot restore /data/backup/etcd-snapshot-previous.db --data-dir=/var/lib/etcd

# 4、修改目录权限
chown -R etcd:etcd /var/lib/etcd

# 5、恢复系统组件
mv /etc/kubernetes/manifests.bak /etc/kubernetes/manifests

# 6、重启kubelet，集群重启需要时间3分钟左右
systemctl restart kubelet

```

#### 验证

查看集群中 Pod 状态，如果正常表示恢复成功。

```bash
kubectl get pod

```

## 第十六题 重启 kubelet

#### 题目

名为 “node02” 的 Kubernetes worker node 处于 NotReady 状态。调查发生这种情况的原因，并采取相应的措施将 node 恢复为 Ready 状态，确保所做的任何更改永久生效。

可以使用以下命令，通过 ssh 连接到 node02 节点。

```bash
ssh node02

```

可以使用以下命令，在该节点上获取更高权限。

```bash
sudo -i

```

#### 答题要点

这道题主要考在节点上重启 kubelet 组件以及设置开机启动。知识点参考专栏 [第 16 课](https://time.geekbang.org/column/article/797497)，下面我给出参考答案。

#### 参考答案

```bash
# 1、ssh 到 node02 节点，并切换到 root 下
ssh node02
sudo -i

# 2、启动 kubelet 组件
systemctl start kubelet

# 3、设置为开机启动
systemctl enable kubelet

# 4、查看 kubelet 状态，如果返回 Active: active 则表示成功运行组件
systemctl status kubelet

# 5、退回到初始节点
exit

```

#### 验证

检查节点状态，查看 node02 是否恢复 Ready 状态。

```bash
kubectl get node

```

## 第十七题 排空节点

#### 题目

将名为 node02 的 node 设置为不可用，并重新调度该 node 上所有运行的 pods。

#### 答题要点

这道题主要考排空节点。知识点参考专栏 [第 6 课](https://time.geekbang.org/column/article/793925)，下面我给出参考答案。

#### 参考答案

```bash
# 标记节点不可调度
kubectl cordon node02

# 驱逐节点上的所有 Pod，这些 Pod 会自动重新调度到别的节点
# 如果命令有报错，则按照提示需要加上 --delete-emptydir-data --force 参数
kubectl drain node02 --ignore-daemonsets

```

#### 验证

查看节点状态，node02 节点状态为 SchedulingDisabled。

```bash
kubectl get node

```

## **小结**

今天我给你讲了真题的下半部分，你会发现这些真题中有些题目简单，只需要一两行命令就可以完成，有些题目复杂，需要你写大量的 YAML 文件，或者要记住很多命令。在考试的过程中你可以有选择的先把自己熟悉并且简单的题目做好答对，然后再来做复杂有难度的题目。

考试时间是很充足的，如果碰到拿不准的题目也不要着急，放到最后慢慢想。相信你多熟悉几遍真题，一定能顺利通过 CKA 考试。