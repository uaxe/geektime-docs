你好，我是雪飞。

用了这么久的命令行，是不是很喜欢 kubectl 这个集群管理工具，我个人也是更喜欢使用命令行来管理集群。不过，这节课我给你介绍两款 K8s 集群的可视化管理工具：Dashboard 和 Kuboard，通过可视化管理工具可以更加直观地查看集群状态以及管理资源对象。

## Dashboard

K8s Dashboard 是一个官方支持的开源 Web 界面工具，它极大地简化了 K8s 集群的管理和监控。通过浏览器访问一个直观的用户界面，你可以执行资源的部署、更新、删除和查看操作，同时监控集群状态和资源对象的使用情况。Dashboard 支持故障排查工具，如日志查看和事件监控，以及与 K8s RBAC 的集成，提供了细粒度的访问控制。此外，它还允许用户设置资源配额和限制，帮助优化资源使用和成本控制。

总体而言，Dashboard 是一个功能全面的可视化工具，为 Kubernetes 集群管理者提供了一种直观、高效、安全的方式来管理和监控集群资源，无需复杂的命令行操作。下面我们就先来部署一下 Dashboard。

### 部署 Dashboard

Dashboard 需要部署到 K8s 集群中，使用 YAML 文件部署。

1. 下载 Dashboard 的 YAML 部署文件。

```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.0/aio/deploy/recommended.yaml

```

2. 默认部署的 Dashboard 只能集群内部访问，所以我们修改 recommended.yaml 部署文件，修改 Service 为 NodePort 类型，并给它指定一个固定的 30001 的节点端口号，从而把服务暴露到外部。

```yaml
# vi recommended.yaml，编辑 YAML 文件
......
spec:
  ports:
    - port: 443
      targetPort: 8443
      nodePort: 30001
  selector:
    k8s-app: kubernetes-dashboard
  type: NodePort
......

```

3. 执行 “kubectl apply” 命令部署 Dashboard 应用，之后查看 Pod 部署到了 kubernetes-dashboard 命名空间中。

```bash
[root@k8s-master ~]# kubectl apply -f recommended.yaml
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
secret/kubernetes-dashboard-certs created
secret/kubernetes-dashboard-csrf created
secret/kubernetes-dashboard-key-holder created
configmap/kubernetes-dashboard-settings created
role.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrole.rbac.authorization.k8s.io/kubernetes-dashboard created
rolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
service/dashboard-metrics-scraper created
deployment.apps/dashboard-metrics-scraper created

[root@k8s-master ~]# kubectl get pods -n kubernetes-dashboard
NAME                                     READY   STATUS    RESTARTS   AGE
kubernetes-dashboard-5ffb5cf944-98hdk    1/1     Running   0          22m

```

如果 Dashboard 的镜像下载太慢或者无法下载，可以使用我提供的离线镜像包（dashboard-image.zip， [下载地址](https://pan.baidu.com/s/1LOSuxBjXxC-RY3HA49O3YQ?pwd=nysi)），解压后在每个节点上执行导入命令，将所有离线镜像导入到节点本地，最后再执行 YAML 文件部署。

```bash
ls *.tar |xargs -i docker load -i {}

```

4. 部署完成后，可以通过 “https://<节点公网 IP>:<端口号30001>” 访问 Dashboard。可以看到登录界面。 **注意：** Dashboard 要求使用 HTTPS 来访问，但是我们没有使用证书，所以这里会提示不安全，你可以继续访问，就可以看到登录页，但是生产环境还是建议通过 Ingress 加载 HTTPS 证书来访问。

![图片](https://static001.geekbang.org/resource/image/9c/70/9c15ab25faaa2851ec98ace5a8c64970.png?wh=2364x754)

### 访问 Dashboard

新部署的 Dashboard 需要登录，有两种方式登录，一种是 Token，另一种是 Kubeconfig，在课程中我们讲过这两种方式，这里我们使用 Token 登录方式。所以你需要创建一个 ServiceAccount 账号（dashboard-admin），并绑定默认 cluster-admin 管理员角色，然后用这个账号生成 Token 来登录 Dashboard，命令如下：

```bash
# 创建服务账号
kubectl create serviceaccount dashboard-admin -n kubernetes-dashboard
# 用户授权
kubectl create clusterrolebinding dashboard-admin --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:dashboard-admin
# 创建sa的Token
kubectl create token dashboard-admin -n kubernetes-dashboard

```

使用输出的 Token 登录 Dashboard，你就可以通过 Dashboard 来管理 K8s 集群了。

![图片](https://static001.geekbang.org/resource/image/4a/af/4a35db637d861a4a12188ea20d2a78af.png?wh=1913x967)

![图片](https://static001.geekbang.org/resource/image/a1/32/a1b0da75b238424fcf4b3f10b8e38932.png?wh=3002x1526)

![图片](https://static001.geekbang.org/resource/image/2a/7b/2af6c9e55e7157c68f1314498ea87e7b.png?wh=2984x1402)

在生产环境中，你可以根据我们的课程内容，给 Dashboard 部署 Ingress 资源，并且配置 HTTPS 证书，通过 HTTPS 域名来访问 Dashboard。

## Kuboard

Kuboard 是一个为 K8s 集群提供直观管理的可视化工具，它通过图形用户界面简化了日常的运维任务。这个工具的核心优势在于支持多集群管理，让用户能够在不同集群间轻松切换和操作。

Kuboard 还允许用户通过图形化的方式部署应用程序，管理配置映射和密钥，同时集成了Prometheus 和 Grafana 等监控工具，提供了强大的性能监控功能。此外，它还具备插件系统，为用户提供了高度的自定义能力，以适应特定的使用需求。我们团队实际在生产集群中使用 Kuboard 作为可视化管理工具，可以查看它的 [官方文档](https://www.kuboard.cn/)。

### 部署 Kuboard

Kuboard 可以管理多个 K8s 集群，所以它不是通过 YAML 文件部署到某个集群中，而是通过 Docker 容器方式运行在单个 Linux 服务器上，这个服务器需要可以通过内网访问到集群。

1. 在服务器本地目录创建 “kuboard-v4”。

```bash
[root@k8s-worker1 kuboard-v4]# mkdir kuboard-v4

```

2. 在该目录下创建文件 docker-compose.yaml，这是一个 Docker Compose 文件，文件中包含两个步骤：创建 MySQL 数据库，然后运行 kuboard 镜像。

> Docker Compose 是一个用于简化多容器 Docker 应用程序部署和编排的工具。它通过一个 YAML 格式的配置文件来统一定义应用程序中所有服务的配置信息，包括容器的镜像、环境变量、端口映射等。用户可以通过一个简单的命令来启动或停止整个应用程序的所有服务，同时 Docker Compose 还支持网络配置、数据卷管理和服务扩展等功能。

```yaml
configs:
  create_db_sql:
    content: |
      CREATE DATABASE kuboard DEFAULT CHARACTER SET = 'utf8mb4' DEFAULT COLLATE = 'utf8mb4_unicode_ci';
      create user 'kuboard'@'%' identified by 'kuboardpwd';
      grant all privileges on kuboard.* to 'kuboard'@'%';
      FLUSH PRIVILEGES;

services:
  db:
    image: swr.cn-east-2.myhuaweicloud.com/kuboard/mariadb:11.3.2-jammy
    # image: mariadb:11.3.2-jammy
    # swr.cn-east-2.myhuaweicloud.com/kuboard/mariadb:11.3.2-jammy 与 mariadb:11.3.2-jammy 镜像完全一致
    environment:
      MARIADB_ROOT_PASSWORD: kuboardpwd
      MYSQL_ROOT_PASSWORD: kuboardpwd
      TZ: Asia/Shanghai
    volumes:
      - ./kuboard-mariadb-data:/var/lib/mysql:Z
    configs:
      - source: create_db_sql
        target: /docker-entrypoint-initdb.d/create_db.sql
        mode: 0777
    networks:
      kuboard_v4_dev:
        aliases:
          - db
  kuboard:
    image: swr.cn-east-2.myhuaweicloud.com/kuboard/kuboard:v4
    # image: eipwork/kuboard:v4
    environment:
      - DB_DRIVER=org.mariadb.jdbc.Driver
      - DB_URL=jdbc:mariadb://db:3306/kuboard?serverTimezone=Asia/Shanghai
      - DB_USERNAME=kuboard
      - DB_PASSWORD=kuboardpwd
    ports:
      - '8000:80'
    depends_on:
      - db
    networks:
      kuboard_v4_dev:
        aliases:
          - kuboard

networks:
  kuboard_v4_dev:
    driver: bridge

```

3. 在 kuboard-v4 目录下执行命令，自动运行上面的 docker-compose 文件，成功之后就可以通过浏览器访问 Kuboard。

```yaml
[root@k8s-worker1 kuboard-v4]# docker compose up -d
[+] Running 2/2
 ✔ Container kuboard-v4-db-1       Started                                                                                       0.3s
 ✔ Container kuboard-v4-kuboard-1  Started

```

### 访问 Kuboard

在浏览器输入 “http://<服务器公网 IP>:8000” 即可访问 Kuboard 的界面。

![图片](https://static001.geekbang.org/resource/image/e0/82/e0417b63db1848511e82d1e352d6c182.png?wh=3112x1334)

> 登录方式：
>
> 用户名：admin
>
> 密 码：Kuboard123

进入 Kuboard 之后需要导入集群，有两种方式：kubeconfig 文件导入和 Secret Token 导入，你可以选择合适的方式导入要管理的 K8s 集群。

![图片](https://static001.geekbang.org/resource/image/42/9a/42c8ea342c7db405fyy242ee50eed69a.png?wh=3826x1914)

导入后就可以查看你要管理的 K8s 集群，并可以对集群进行可视化操作了。

![图片](https://static001.geekbang.org/resource/image/2e/90/2e1395e8a960bdcbf00337af2ac02c90.png?wh=3828x1920)

![图片](https://static001.geekbang.org/resource/image/8e/72/8e90a13fda9826bb8573708f2f31fe72.png?wh=3818x1920)

![图片](https://static001.geekbang.org/resource/image/1e/30/1e61c1ca4027e067d1373d869a79dc30.png?wh=3824x1916)

## 小结

Dashboard 和 Kuboard 作为可视化管理工具，都提供了一种直观的方式来管理和监控 K8s 集群。

Dashboard 是官方支持的工具，拥有广泛的社区支持，特别适合寻求官方解决方案和严格安全控制的用户。它通过 Web 界面支持资源的部署、管理和故障排查，并提供了用户认证和基于角色的访问控制。

与此相比，Kuboard 作为一个第三方工具，以其易用性和多集群管理功能脱颖而出。它允许用户通过图形化界面轻松管理和部署应用程序，并且支持插件系统，可以根据用户的特定需求进行扩展和自定义。对于那些需要统一视图来管理多个集群的用户来说，Kuboard 提供了极大的便利。