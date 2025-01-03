你好，我是郑建勋。

这节课，我们一起来学习如何使用 Docker Compose 来部署多个容器。

## 什么是 Docker Compose？

那什么是 Docker Compose 呢？

一句话解释，Docker Compose 一般用于开发环境，负责部署和管理多个容器。

现代的应用程序通常由众多微服务组成，就拿我们的爬虫服务来说，它包含了Master、Worker、etcd、MySQL，未来还可能包含前端服务、日志采集服务、鉴权服务等等。部署和管理许多像这样的微服务可能很困难，而 Docker Compose 就可以解决这一问题。

Docker Compose 并不是简单地将多个容器脚本和 Docker 命令排列在一起，它会让你在单个声明式配置文件（例如 docker-compose.yaml）中描述整个应用程序，并使用简单的命令进行部署。部署应用程序之后，你可以用一组简单的命令来管理应用程序的整个生命周期。

Docker Compose的前身是 Fig。Fig 由 Orchard 公司创建，它是管理多容器的最佳方式。Fig是一个位于 Docker 之上的 Python 工具，它可以让你在单个 YAML 文件中定义整个容器服务。然后，使用 fig 命令行工具就可以部署和管理应用程序的生命周期。Fig 通过读取 YAML 文件和 Docker API 来部署和管理应用程序。

后来，Docker Inc 公司收购了 Orchard 并将 Fig 重新命名为 Docker Compose，而命令行工具也从 fig 重命名为了 docker-compose。Docker Compose仍然是在 Docker 之上的外部工具，它从未完全集成到 Docker 引擎中，但却一直很受欢迎并被广泛使用。

Docker Compose 目前仍然是通过Python开发的工具。借助Docker Compose，你可以在 YAML 文件中定义多个服务，并由 docker-compose 对文件完成解析，然后借助 Docker API 部署容器。2020 年 4 月， [Compose 规范](https://github.com/compose-spec/compose-spec/blob/master/spec.md) 正式发布，它的目的是定义一个多容器，平台无关应用程序的标准。Docker Compose就是基于该规范实现的。

## **Compose的安装**

下面我们来看看如何安装Docker Compose。

安装 Docker Compose 最简单的方法是安装 Docker Desktop。之前，我们已经看到了如何通过简单的界面化的方式安装 Docker Desktop。Docker Desktop中包括 Docker Compose、 Docker Engine 以及 Docker CLI。要想通过其他方式安装，你也可以查看 [官方安装文档](https://docker-docs.netlify.app/compose/install/)。

接下来，我们执行以下命令可以验证是否拥有了 Docker Compose。

```plain
» docker-compose --version                                                                                                             jackson@localhost
Docker Compose version v2.13.0

```

## **Compose配置文件的编写**

Compose 使用 YAML 和JSON 格式的配置文件来定义多服务应用程序。其中默认的配置文件名称是 docker-compose.yml。但是，你也可以使用 -f 标志来指定自定义的配置文件。

下面我们为爬虫项目书写第一个简单的docker-compose.yml文件，如下所示。

```plain
version: "3.9"
services:
  worker:
    build: .
    command: ./crawler worker
    ports:
      - "8080:8080"
    networks:
      - counter-net
    volumes:
      - /tmp/app:/app
    depends_on:
      mysql:
          condition: service_healthy
  mysql:
    image: mysql:5.7
    #    restart: always
    environment:
      MYSQL_DATABASE: 'crawler'
      MYSQL_USER: 'myuser'
      MYSQL_PASSWORD: 'mypassword'
      # Password for root access
      MYSQL_ROOT_PASSWORD: '123456'
      #      docker-compose默认时区UTC
      TZ: 'Asia/Shanghai'
    ports:
      - '3326:3306'
    expose:
      # Opens port 3306 on the container
      - '3306'
      # Where our data will be persisted
    volumes:
      -  /tmp/data:/var/lib/mysql
    networks:
      counter-net:
    healthcheck:
      test: ["CMD", "mysqladmin" ,"ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 55
networks:
  counter-net:

```

在这个例子中，docker-compose.yml文件的根级别有 3 个指令。

- version


  version指令是Compose配置文件中必须要有的，它始终位于文件的第一行。version定义了 Compose 文件格式的版本，我们这里使用的是最新的3.9版本。注意，version并未定义 Docker Compose 和 Docker 的版本。

- services


  services指令用于定义应用程序需要部署的不同服务。这个例子中定义了两个服务，一个是我们爬虫项目的Worker，另一个是Worker依赖的MySQL数据库。

- networks


  networks 的作用是告诉 Docker 创建一个新网络。默认情况下，Compose 将创建桥接网络。但是，你可以使用driver属性来指定不同的网络类型。


除此之外，根级别配置中还可以设置其他指令，例如volumes、secrets、configs。其中，volumes 用于将数据挂载到容器，这是持久化容器数据的最佳方式。secrets主要用于swarm模式，可以管理敏感数据，安全传输数据（这些敏感数据不能直接存储在镜像或源码中，但在运行时又需要）。configs也用于swarm模式，它可以管理非敏感数据，例如配置文件等。

更进一步地，让我们来看看services中定义的服务。 **在services中我们定义了两个服务Worker 和MySQL 。** Compose 会将每一个服务部署为一个容器，并且容器的名字会分别包含 Worker 与 MySQL。

在对 Worker 服务的配置中，各个配置的含义如下所示。

- build用于构建镜像，其中 build: . 告诉 Docker 使用当前目录中的 Dockerfile 构建一个新镜像，新构建的镜像将用于创建容器。
- command，它是容器启动后运行的应用程序命令，该命令可以覆盖 Dockerfile 中设置的 CMD 指令。
- ports，表示端口映射。在这里， `"SRC:DST"` 表示将宿主机的SRC端口映射到容器中的DST端口，访问宿主机SRC端口的请求将会被转发到容器对应的DST端口中。
- networks，它可以告诉 Docker 要将服务的容器附加到哪个网络中。
- volumes，它可以告诉 Docker 要将宿主机的目录挂载到容器内的哪个目录。
- depends\_on，表示启动服务前需要首先启动的依赖服务。在本例中，启动Worker容器前必须先确保MySQL可正常提供服务。

而在对MySQL服务的定义中，各个配置的含义如下所示。

- image，用于指定当前容器启动的镜像版本，当前版本为mysql:5.7。如果在本地查找不到镜像，就从 Docker Hub 中拉取。
- environment，它可以设置容器的环境变量。环境变量可用于指定当前MySQL容器的时区，并配置初始数据库名，根用户的密码等。
- expose，描述性信息，表明当前容器暴露的端口号。
- networks，用于指定容器的命名空间。MySQL服务的networks应设置为和Worker服务相同的counter-net，这样两个容器共用同一个网络命名空间，可以使用回环地址进行通信。
- healthcheck，用于检测服务的健康状况，在这里它和depends\_on配合在一起可以确保MySQL服务状态健康后再启动Worker服务。

要使用 Docker Compose 启动应用程序，可以使用 docker-compose up指令，它是启动 Compose 应用程序最常见的方式。docker-compose up指令可以构建或拉取所有需要的镜像，创建所有需要的网络和存储卷，并启动所有的容器。

如下所示，我们输入 docker-compose up，程序启动后可能会打印冗长的启动日志，等待几秒钟之后，服务就启动好了。根据我们的配置，将首先启动MySQL服务，接着启动Worker服务。

```plain
» docker-compose up
[+] Running 2/0
 ⠿ Container crawler-mysql-1           Created                                                                                                                                 0.0s
 ⠿ Container crawler-crawler-worker-1  Created                                                                                                                                 0.0s
Attaching to crawler-crawler-worker-1, crawler-mysql-1

```

默认情况下，docker-compose up 将查找名称为 docker-compose.yml的配置文件，如果你有自定义的配置文件，需要使用 -f 标志指定它。另外，使用 -d 标志可以在后台启动应用程序。

现在，应用程序已构建好并开始运行了，我们可以使用普通的 docker 命令来查看 Compose 创建的镜像、容器、网络。

如下所示，docker images 指令可以查看到我们最新构建好的Worker镜像。

```plain
» docker images
REPOSITORY                  TAG      IMAGE ID       CREATED         SIZE
crawler-crawler-worker      latest   1fec0f6fc04e   23 hours ago    41.3MB

```

docker ps 可以查看当前正在运行的容器，可以看到Worker与MySQL都已经正常启动了。

```plain
» docker ps
CONTAINER ID   IMAGE                    COMMAND                  CREATED          STATUS                   PORTS                               NAMES
a43f4ed671fc   crawler-crawler-worker   "./crawler worker"       2 minutes ago    Up 2 minutes             0.0.0.0:8080->8080/tcp              crawler-crawler-worker-1
2bd879656049   mysql:5.7                "docker-entrypoint.s…"   38 minutes ago   Up 2 minutes (healthy)   33060/tcp, 0.0.0.0:3326->3306/tcp   crawler-mysql-1

```

接着，我们执行docker network ls，可以看到dokcek创建了一个新的网络crawler\_counter-net，它为桥接模式。

```plain
» docker network ls                                                                                                                        jackson@localhost
NETWORK ID     NAME                  DRIVER    SCOPE
ef63428fb70e   bridge                bridge    local
71d238bd7e46   crawler_counter-net   bridge    local
1fa0c4c53670   host                  host      local
04d433213cca   localnet              bridge    local
25c4683eb897   none                  null      local

```

## Compose生命周期管理

接下来，我们看看如何使用Docker Compose启动、停止和删除应用程序，实现对于多容器应用程序的管理。

当应用程序启动后，使用 docker-compose ps 命令可以查看当前应用程序的状态。和docker ps类似，你可以看到两个容器、容器正在运行的命令、当前运行的状态以及监听的网络端口。

```plain
» docker-compose ps                                                                                            jackson@jacksondeMacBook-Pro
NAME                COMMAND                  SERVICE             STATUS              PORTS
crawler-mysql-1     "docker-entrypoint.s…"   mysql               running (healthy)   33060/tcp, 0.0.0.0:3326->3306/tcp
crawler-worker-1    "./crawler worker"       worker              running             0.0.0.0:8080->8080/tcp

```

使用 docker-compose top 可以列出每个服务（容器）内运行的进程，返回的 PID 号是从宿主机看到的 PID 号。

```plain
» docker-compose top                                                                                           jackson@jacksondeMacBook-Pro
crawler-mysql-1
UID   PID     PPID    C    STIME   TTY   TIME       CMD
999   71494   71468   0    14:58   ?     00:00:00   mysqld

crawler-worker-1
UID    PID     PPID    C    STIME   TTY   TIME       CMD
root   71773   71746   0    14:58   ?     00:00:00   ./crawler worker

```

如果想要关闭应用程序，可以执行docker-compose down，如下所示。

```plain
» docker-compose down                                                                                          jackson@jacksondeMacBook-Pro
[+] Running 3/3
 ⠿ Container crawler-worker-1   Removed                                                                                                                                        5.2s
 ⠿ Container crawler-mysql-1    Removed                                                                                                                                        2.1s
 ⠿ Network crawler_counter-net  Removed

```

要注意的是，docker-compose up 构建或拉取的任何镜像都不会被删除，它们仍然存在于系统中，这意味着下次启动应用程序时会更快。同时我们还可以看到，当前挂载到宿主机的存储目录并不会随着docker-compose down 而销毁。

同样，使用 docker-compose stop 命令可以让应用程序暂停，但不会删除它。再次执行 docker-compose ps，可以看到应用程序的状态为exited。

```plain
» docker-compose ps                                                                                            jackson@jacksondeMacBook-Pro
NAME                COMMAND                  SERVICE             STATUS              PORTS
crawler-mysql-1     "docker-entrypoint.s…"   mysql               exited (0)
crawler-worker-1    "./crawler worker"       worker              exited (0)

```

因为docker-compose stop而暂停的容器，之后再执行 docker-compose restart 就可以重新启动。

```plain
» docker-compose restart                                                                                       jackson@jacksondeMacBook-Pro
[+] Running 2/2
 ⠿ Container crawler-mysql-1   Started                                                                                                                                         2.3s
 ⠿ Container crawler-worker-1  Started

```

最后，整合了Master，Worker，MySQL 和 etcd服务的 Compose 配置文件如下所示。具体的你可以查看项目最新分支的docker-compose.yml文件。

```plain
version: "3.9"
services:
  worker:
    build: .
    command: ./crawler worker --id=2 --http=:8080  --grpc=:9090
    ports:
      - "8080:8080"
      - "9090:9090"
    networks:
      - counter-net
    volumes:
      - /tmp/app:/app
    depends_on:
      mysql:
          condition: service_healthy
      etcd:
        condition: service_healthy
  master:
    build: .
    command: ./crawler master --id=3 --http=:8082  --grpc=:9092
    ports:
      - "8082:8082"
      - "9092:9092"
    networks:
      - counter-net
    volumes:
      - /tmp/app:/app
    depends_on:
      mysql:
        condition: service_healthy
      etcd:
        condition: service_healthy
  mysql:
    image: mysql:5.7
    #    restart: always
    environment:
      MYSQL_DATABASE: 'crawler'
      MYSQL_USER: 'myuser'
      MYSQL_PASSWORD: 'mypassword'
      # Password for root access
      MYSQL_ROOT_PASSWORD: '123456'
      #      docker-compose默认时区UTC
      TZ: 'Asia/Shanghai'
    ports:
      - '3326:3306'
    expose:
      # Opens port 3306 on the container
      - '3306'
      # Where our data will be persisted
    volumes:
      -  /tmp/data:/var/lib/mysql
    networks:
      counter-net:
    healthcheck:
      test: ["CMD", "mysqladmin" ,"ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 55
  etcd:
    image: gcr.io/etcd-development/etcd:v3.5.6
    volumes:
      - /tmp/etcd:/etcd-data
    ports:
      - '2379:2379'
      - '2380:2380'
    expose:
      - 2379
      - 2380
    networks:
      counter-net:
    environment:
      - ETCDCTL_API=3
    command:
      - /usr/local/bin/etcd
      - --data-dir=/etcd-data
      - --name
      - etcd
      - --initial-advertise-peer-urls
      - http://0.0.0.0:2380
      - --listen-peer-urls
      - http://0.0.0.0:2380
      - --advertise-client-urls
      - http://0.0.0.0:2379
      - --listen-client-urls
      - http://0.0.0.0:2379
      - --initial-cluster
      - etcd=http://0.0.0.0:2380
      - --initial-cluster-state
      - new
      - --initial-cluster-token
      - tkn
    healthcheck:
      test: ["CMD", "/usr/local/bin/etcdctl" ,"get", "--prefix", "/"]
      interval: 5s
      timeout: 5s
      retries: 55

networks:
  counter-net:

```

在这之后，我们就可以方便地测试最新的代码了。如下所示，调用Master添加资源接口之后，Worker将能够正常地爬取网站。

```plain
» curl -H "content-type: application/json" -d '{"id":"zjx","name": "douban_book_list"}' <http://localhost:8082/crawler/resource>
{"id":"go.micro.server.worker-2", "Address":"172.22.0.5:9090"}

```

## 总结

这节课，我们学习了如何使用 Docker Compose 部署和管理多容器应用程序。Docker Compose 是一个运行在 Docker 之上的 Python 应用程序。它允许你在单个声明式配置文件中描述多容器应用程序，并使用简单的命令进行管理。

Docker Compose 默认的配置文件为当前目录下的docker-compose.yml文件。配置文件中可以书写丰富的自定义配置，以此控制容器的行为。这节课我们了解了其中最常用的一些，其他的参数你可以查阅参考文档。

要注意的是，编写配置参数时候需要配置参数的缩进。例如，描述服务的networks参数和根级别的networks参数的含义是截然不同的。在实践中我们一般会复制一个模版文件，并在此基础上将其改造为当前项目的配置。

Docker Compose 多是用在单主机的开发环境中。在更大规模的生产集群中，我们一般会使用 Kubernetes 等容器编排技术，这部分内容我们后续会介绍。

## 课后题

这节课的思考题如下。

你认为，执行docker-compose down关闭容器时，挂载到容器中的volume会被销毁吗？为什么要这样设计呢？

欢迎你在留言区与我交流讨论，我们下节课再见！