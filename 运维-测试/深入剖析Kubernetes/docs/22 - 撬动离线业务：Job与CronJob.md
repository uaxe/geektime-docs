你好，我是张磊。今天我和你分享的主题是：撬动离线业务之Job与CronJob。

在前面的几篇文章中，我和你详细分享了Deployment、StatefulSet，以及DaemonSet这三个编排概念。你有没有发现它们的共同之处呢？

实际上，它们主要编排的对象，都是“在线业务”，即：Long Running Task（长作业）。比如，我在前面举例时常用的Nginx、Tomcat，以及MySQL等等。这些应用一旦运行起来，除非出错或者停止，它的容器进程会一直保持在Running状态。

但是，有一类作业显然不满足这样的条件，这就是“离线业务”，或者叫作Batch Job（计算业务）。这种业务在计算完成后就直接退出了，而此时如果你依然用Deployment来管理这种业务的话，就会发现Pod会在计算结束后退出，然后被Deployment Controller不断地重启；而像“滚动更新”这样的编排功能，更无从谈起了。

所以，早在Borg项目中，Google就已经对作业进行了分类处理，提出了LRS（Long Running Service）和Batch Jobs两种作业形态，对它们进行“分别管理”和“混合调度”。

不过，在2015年Borg论文刚刚发布的时候，Kubernetes项目并不支持对Batch Job的管理。直到v1.4版本之后，社区才逐步设计出了一个用来描述离线业务的API对象，它的名字就是：Job。

Job API对象的定义非常简单，我来举个例子，如下所示：

```
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  template:
    spec:
      containers:
      - name: pi
        image: resouer/ubuntu-bc
        command: ["sh", "-c", "echo 'scale=10000; 4*a(1)' | bc -l "]
      restartPolicy: Never
  backoffLimit: 4

```

此时，相信你对Kubernetes的API对象已经不再陌生了。在这个Job的YAML文件里，你肯定一眼就会看到一位“老熟人”：Pod模板，即spec.template字段。

在这个Pod模板中，我定义了一个Ubuntu镜像的容器（准确地说，是一个安装了bc命令的Ubuntu镜像），它运行的程序是：

```
echo "scale=10000; 4*a(1)" | bc -l

```

其中，bc命令是Linux里的“计算器”；-l表示，我现在要使用标准数学库；而a(1)，则是调用数学库中的arctangent函数，计算atan(1)。这是什么意思呢？

中学知识告诉我们： `tan(π/4) = 1`。所以， `4*atan(1)` 正好就是π，也就是3.1415926…。

> 备注：如果你不熟悉这个知识也不必担心，我也是在查阅资料后才知道的。

所以，这其实就是一个计算π值的容器。而通过scale=10000，我指定了输出的小数点后的位数是10000。在我的计算机上，这个计算大概用时1分54秒。

但是，跟其他控制器不同的是，Job对象并不要求你定义一个spec.selector来描述要控制哪些Pod。具体原因，我马上会讲解到。

现在，我们就可以创建这个Job了：

```
$ kubectl create -f job.yaml

```

在成功创建后，我们来查看一下这个Job对象，如下所示：

```
$ kubectl describe jobs/pi
Name:             pi
Namespace:        default
Selector:         controller-uid=c2db599a-2c9d-11e6-b324-0209dc45a495
Labels:           controller-uid=c2db599a-2c9d-11e6-b324-0209dc45a495
                  job-name=pi
Annotations:      <none>
Parallelism:      1
Completions:      1
..
Pods Statuses:    0 Running / 1 Succeeded / 0 Failed
Pod Template:
  Labels:       controller-uid=c2db599a-2c9d-11e6-b324-0209dc45a495
                job-name=pi
  Containers:
   ...
  Volumes:              <none>
Events:
  FirstSeen    LastSeen    Count    From            SubobjectPath    Type        Reason            Message
  ---------    --------    -----    ----            -------------    --------    ------            -------
  1m           1m          1        {job-controller }                Normal      SuccessfulCreate  Created pod: pi-rq5rl

```

可以看到，这个Job对象在创建后，它的Pod模板，被自动加上了一个controller-uid=<一个随机字符串>这样的Label。而这个Job对象本身，则被自动加上了这个Label对应的Selector，从而 保证了Job与它所管理的Pod之间的匹配关系。

而Job Controller之所以要使用这种携带了UID的Label，就是为了避免不同Job对象所管理的Pod发生重合。需要注意的是， **这种自动生成的Label对用户来说并不友好，所以不太适合推广到Deployment等长作业编排对象上。**

接下来，我们可以看到这个Job创建的Pod进入了Running状态，这意味着它正在计算Pi的值。

```
$ kubectl get pods
NAME                                READY     STATUS    RESTARTS   AGE
pi-rq5rl                            1/1       Running   0          10s

```

而几分钟后计算结束，这个Pod就会进入Completed状态：

```
$ kubectl get pods
NAME                                READY     STATUS      RESTARTS   AGE
pi-rq5rl                            0/1       Completed   0          4m

```

这也是我们需要在Pod模板中定义restartPolicy=Never的原因：离线计算的Pod永远都不应该被重启，否则它们会再重新计算一遍。

> 事实上，restartPolicy在Job对象里只允许被设置为Never和OnFailure；而在Deployment对象里，restartPolicy则只允许被设置为Always。

此时，我们通过kubectl logs查看一下这个Pod的日志，就可以看到计算得到的Pi值已经被打印了出来：

```
$ kubectl logs pi-rq5rl
3.141592653589793238462643383279...

```

这时候，你一定会想到这样一个问题， **如果这个离线作业失败了要怎么办？**

比如，我们在这个例子中 **定义了restartPolicy=Never，那么离线作业失败后Job Controller就会不断地尝试创建一个新Pod**，如下所示：

```
$ kubectl get pods
NAME                                READY     STATUS              RESTARTS   AGE
pi-55h89                            0/1       ContainerCreating   0          2s
pi-tqbcz                            0/1       Error               0          5s

```

可以看到，这时候会不断地有新Pod被创建出来。

当然，这个尝试肯定不能无限进行下去。所以，我们就在Job对象的spec.backoffLimit字段里定义了重试次数为4（即，backoffLimit=4），而这个字段的默认值是6。

需要注意的是，Job Controller重新创建Pod的间隔是呈指数增加的，即下一次重新创建Pod的动作会分别发生在10 s、20 s、40 s …后。

而如果你 **定义的restartPolicy=OnFailure，那么离线作业失败后，Job Controller就不会去尝试创建新的Pod。但是，它会不断地尝试重启Pod里的容器**。这也正好对应了restartPolicy的含义（你也可以借此机会再回顾一下第15篇文章 [《深入解析Pod对象（二）：使用进阶》](https://time.geekbang.org/column/article/40466) 中的相关内容）。

如前所述，当一个Job的Pod运行结束后，它会进入Completed状态。但是，如果这个Pod因为某种原因一直不肯结束呢？

在Job的API对象里，有一个spec.activeDeadlineSeconds字段可以设置最长运行时间，比如：

```
spec:
 backoffLimit: 5
 activeDeadlineSeconds: 100

```

一旦运行超过了100 s，这个Job的所有Pod都会被终止。并且，你可以在Pod的状态里看到终止的原因是reason: DeadlineExceeded。

以上，就是一个Job API对象最主要的概念和用法了。不过，离线业务之所以被称为Batch Job，当然是因为它们可以以“Batch”，也就是并行的方式去运行。

接下来，我就来为你讲解一下Job Controller对并行作业的控制方法。

在Job对象中，负责并行控制的参数有两个：

1. spec.parallelism，它定义的是一个Job在任意时间最多可以启动多少个Pod同时运行；

2. spec.completions，它定义的是Job至少要完成的Pod数目，即Job的最小完成数。


这两个参数听起来有点儿抽象，所以我准备了一个例子来帮助你理解。

现在，我在之前计算Pi值的Job里，添加这两个参数：

```
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  parallelism: 2
  completions: 4
  template:
    spec:
      containers:
      - name: pi
        image: resouer/ubuntu-bc
        command: ["sh", "-c", "echo 'scale=5000; 4*a(1)' | bc -l "]
      restartPolicy: Never
  backoffLimit: 4

```

这样，我们就指定了这个Job最大的并行数是2，而最小的完成数是4。

接下来，我们来创建这个Job对象：

```
$ kubectl create -f job.yaml

```

可以看到，这个Job其实也维护了两个状态字段，即DESIRED和SUCCESSFUL，如下所示：

```
$ kubectl get job
NAME      DESIRED   SUCCESSFUL   AGE
pi        4         0            3s

```

其中，DESIRED的值，正是completions定义的最小完成数。

然后，我们可以看到，这个Job首先创建了两个并行运行的Pod来计算Pi：

```
$ kubectl get pods
NAME       READY     STATUS    RESTARTS   AGE
pi-5mt88   1/1       Running   0          6s
pi-gmcq5   1/1       Running   0          6s

```

而在40 s后，这两个Pod相继完成计算。

这时我们可以看到，每当有一个Pod完成计算进入Completed状态时，就会有一个新的Pod被自动创建出来，并且快速地从Pending状态进入到ContainerCreating状态：

```
$ kubectl get pods
NAME       READY     STATUS    RESTARTS   AGE
pi-gmcq5   0/1       Completed   0         40s
pi-84ww8   0/1       Pending   0         0s
pi-5mt88   0/1       Completed   0         41s
pi-62rbt   0/1       Pending   0         0s

$ kubectl get pods
NAME       READY     STATUS    RESTARTS   AGE
pi-gmcq5   0/1       Completed   0         40s
pi-84ww8   0/1       ContainerCreating   0         0s
pi-5mt88   0/1       Completed   0         41s
pi-62rbt   0/1       ContainerCreating   0         0s

```

紧接着，Job Controller第二次创建出来的两个并行的Pod也进入了Running状态：

```
$ kubectl get pods
NAME       READY     STATUS      RESTARTS   AGE
pi-5mt88   0/1       Completed   0          54s
pi-62rbt   1/1       Running     0          13s
pi-84ww8   1/1       Running     0          14s
pi-gmcq5   0/1       Completed   0          54s

```

最终，后面创建的这两个Pod也完成了计算，进入了Completed状态。

这时，由于所有的Pod均已经成功退出，这个Job也就执行完了，所以你会看到它的SUCCESSFUL字段的值变成了4：

```
$ kubectl get pods
NAME       READY     STATUS      RESTARTS   AGE
pi-5mt88   0/1       Completed   0          5m
pi-62rbt   0/1       Completed   0          4m
pi-84ww8   0/1       Completed   0          4m
pi-gmcq5   0/1       Completed   0          5m

$ kubectl get job
NAME      DESIRED   SUCCESSFUL   AGE
pi        4         4            5m

```

通过上述Job的DESIRED和SUCCESSFUL字段的关系，我们就可以很容易地理解Job Controller的工作原理了。

首先，Job Controller控制的对象，直接就是Pod。

其次，Job Controller在控制循环中进行的调谐（Reconcile）操作，是根据实际在Running状态Pod的数目、已经成功退出的Pod的数目，以及parallelism、completions参数的值共同计算出在这个周期里，应该创建或者删除的Pod数目，然后调用Kubernetes API来执行这个操作。

以创建Pod为例。在上面计算Pi值的这个例子中，当Job一开始创建出来时，实际处于Running状态的Pod数目=0，已经成功退出的Pod数目=0，而用户定义的completions，也就是最终用户需要的Pod数目=4。

所以，在这个时刻，需要创建的Pod数目 = 最终需要的Pod数目 - 实际在Running状态Pod数目 - 已经成功退出的Pod数目 = 4 - 0 - 0= 4。也就是说，Job Controller需要创建4个Pod来纠正这个不一致状态。

可是，我们又定义了这个Job的parallelism=2。也就是说，我们规定了每次并发创建的Pod个数不能超过2个。所以，Job Controller会对前面的计算结果做一个修正，修正后的期望创建的Pod数目应该是：2个。

这时候，Job Controller就会并发地向kube-apiserver发起两个创建Pod的请求。

类似地，如果在这次调谐周期里，Job Controller发现实际在Running状态的Pod数目，比parallelism还大，那么它就会删除一些Pod，使两者相等。

综上所述，Job Controller实际上控制了，作业执行的 **并行度**，以及总共需要完成的 **任务数** 这两个重要参数。而在实际使用时，你需要根据作业的特性，来决定并行度（parallelism）和任务数（completions）的合理取值。

接下来，我再和你分享三种常用的、使用Job对象的方法。

**第一种用法，也是最简单粗暴的用法：外部管理器+Job模板。**

这种模式的特定用法是：把Job的YAML文件定义为一个“模板”，然后用一个外部工具控制这些“模板”来生成Job。这时，Job的定义方式如下所示：

```
apiVersion: batch/v1
kind: Job
metadata:
  name: process-item-$ITEM
  labels:
    jobgroup: jobexample
spec:
  template:
    metadata:
      name: jobexample
      labels:
        jobgroup: jobexample
    spec:
      containers:
      - name: c
        image: busybox
        command: ["sh", "-c", "echo Processing item $ITEM && sleep 5"]
      restartPolicy: Never

```

可以看到，我们在这个Job的YAML里，定义了$ITEM这样的“变量”。

所以，在控制这种Job时，我们只要注意如下两个方面即可：

1. 创建Job时，替换掉$ITEM这样的变量；

2. 所有来自于同一个模板的Job，都有一个jobgroup: jobexample标签，也就是说这一组Job使用这样一个相同的标识。


而做到第一点非常简单。比如，你可以通过这样一句shell把$ITEM替换掉：

```
$ mkdir ./jobs
$ for i in apple banana cherry
do
  cat job-tmpl.yaml | sed "s/\$ITEM/$i/" > ./jobs/job-$i.yaml
done

```

这样，一组来自于同一个模板的不同Job的yaml就生成了。接下来，你就可以通过一句kubectl create指令创建这些Job了：

```
$ kubectl create -f ./jobs
$ kubectl get pods -l jobgroup=jobexample
NAME                        READY     STATUS      RESTARTS   AGE
process-item-apple-kixwv    0/1       Completed   0          4m
process-item-banana-wrsf7   0/1       Completed   0          4m
process-item-cherry-dnfu9   0/1       Completed   0          4m

```

这个模式看起来虽然很“傻”，但却是Kubernetes社区里使用Job的一个很普遍的模式。

原因很简单：大多数用户在需要管理Batch Job的时候，都已经有了一套自己的方案，需要做的往往就是集成工作。这时候，Kubernetes项目对这些方案来说最有价值的，就是Job这个API对象。所以，你只需要编写一个外部工具（等同于我们这里的for循环）来管理这些Job即可。

这种模式最典型的应用，就是TensorFlow社区的KubeFlow项目。

很容易理解，在这种模式下使用Job对象，completions和parallelism这两个字段都应该使用默认值1，而不应该由我们自行设置。而作业Pod的并行控制，应该完全交由外部工具来进行管理（比如，KubeFlow）。

**第二种用法：拥有固定任务数目的并行Job**。

这种模式下，我只关心最后是否有指定数目（spec.completions）个任务成功退出。至于执行时的并行度是多少，我并不关心。

比如，我们这个计算Pi值的例子，就是这样一个典型的、拥有固定任务数目（completions=4）的应用场景。 它的parallelism值是2；或者，你可以干脆不指定parallelism，直接使用默认的并行度（即：1）。

此外，你还可以使用一个工作队列（Work Queue）进行任务分发。这时，Job的YAML文件定义如下所示：

```
apiVersion: batch/v1
kind: Job
metadata:
  name: job-wq-1
spec:
  completions: 8
  parallelism: 2
  template:
    metadata:
      name: job-wq-1
    spec:
      containers:
      - name: c
        image: myrepo/job-wq-1
        env:
        - name: BROKER_URL
          value: amqp://guest:guest@rabbitmq-service:5672
        - name: QUEUE
          value: job1
      restartPolicy: OnFailure

```

我们可以看到，它的completions的值是：8，这意味着我们总共要处理的任务数目是8个。也就是说，总共会有8个任务会被逐一放入工作队列里（你可以运行一个外部小程序作为生产者，来提交任务）。

在这个实例中，我选择充当工作队列的是一个运行在Kubernetes里的RabbitMQ。所以，我们需要在Pod模板里定义BROKER\_URL，来作为消费者。

所以，一旦你用kubectl create创建了这个Job，它就会以并发度为2的方式，每两个Pod一组，创建出8个Pod。每个Pod都会去连接BROKER\_URL，从RabbitMQ里读取任务，然后各自进行处理。这个Pod里的执行逻辑，我们可以用这样一段伪代码来表示：

```
/* job-wq-1的伪代码 */
queue := newQueue($BROKER_URL, $QUEUE)
task := queue.Pop()
process(task)
exit

```

可以看到，每个Pod只需要将任务信息读取出来，处理完成，然后退出即可。而作为用户，我只关心最终一共有8个计算任务启动并且退出，只要这个目标达到，我就认为整个Job处理完成了。所以说，这种用法，对应的就是“任务总数固定”的场景。

**第三种用法，也是很常用的一个用法：指定并行度（parallelism），但不设置固定的completions的值。**

此时，你就必须自己想办法，来决定什么时候启动新Pod，什么时候Job才算执行完成。在这种情况下，任务的总数是未知的，所以你不仅需要一个工作队列来负责任务分发，还需要能够判断工作队列已经为空（即：所有的工作已经结束了）。

这时候，Job的定义基本上没变化，只不过是不再需要定义completions的值了而已：

```
apiVersion: batch/v1
kind: Job
metadata:
  name: job-wq-2
spec:
  parallelism: 2
  template:
    metadata:
      name: job-wq-2
    spec:
      containers:
      - name: c
        image: gcr.io/myproject/job-wq-2
        env:
        - name: BROKER_URL
          value: amqp://guest:guest@rabbitmq-service:5672
        - name: QUEUE
          value: job2
      restartPolicy: OnFailure

```

而对应的Pod的逻辑会稍微复杂一些，我可以用这样一段伪代码来描述：

```
/* job-wq-2的伪代码 */
for !queue.IsEmpty($BROKER_URL, $QUEUE) {
  task := queue.Pop()
  process(task)
}
print("Queue empty, exiting")
exit

```

由于任务数目的总数不固定，所以每一个Pod必须能够知道，自己什么时候可以退出。比如，在这个例子中，我简单地以“队列为空”，作为任务全部完成的标志。所以说，这种用法，对应的是“任务总数不固定”的场景。

不过，在实际的应用中，你需要处理的条件往往会非常复杂。比如，任务完成后的输出、每个任务Pod之间是不是有资源的竞争和协同等等。

所以，在今天这篇文章中，我就不再展开Job的用法了。因为，在实际场景里，要么干脆就用第一种用法来自己管理作业；要么，这些任务Pod之间的关系就不那么“单纯”，甚至还是“有状态应用”（比如，任务的输入/输出是在持久化数据卷里）。在这种情况下，我在后面要重点讲解的Operator，加上Job对象一起，可能才能更好地满足实际离线任务的编排需求。

最后，我再来和你分享一个非常有用的Job对象，叫作：CronJob。

顾名思义，CronJob描述的，正是定时任务。它的API对象，如下所示：

```
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            args:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure

```

在这个YAML文件中，最重要的关键词就是 **jobTemplate**。看到它，你一定恍然大悟，原来CronJob是一个Job对象的控制器（Controller）！

没错，CronJob与Job的关系，正如同Deployment与ReplicaSet的关系一样。CronJob是一个专门用来管理Job对象的控制器。只不过，它创建和删除Job的依据，是schedule字段定义的、一个标准的 [Unix Cron](https://en.wikipedia.org/wiki/Cron) 格式的表达式。

比如，"\*/1 \* \* \* \*"。

这个Cron表达式里\*/1中的\*表示从0开始，/表示“每”，1表示偏移量。所以，它的意思就是：从0开始，每1个时间单位执行一次。

那么，时间单位又是什么呢？

Cron表达式中的五个部分分别代表：分钟、小时、日、月、星期。

所以，上面这句Cron表达式的意思是：从当前开始，每分钟执行一次。

而这里要执行的内容，就是jobTemplate定义的Job了。

所以，这个CronJob对象在创建1分钟后，就会有一个Job产生了，如下所示：

```
$ kubectl create -f ./cronjob.yaml
cronjob "hello" created

# 一分钟后
$ kubectl get jobs
NAME               DESIRED   SUCCESSFUL   AGE
hello-4111706356   1         1         2s

```

此时，CronJob对象会记录下这次Job执行的时间：

```
$ kubectl get cronjob hello
NAME      SCHEDULE      SUSPEND   ACTIVE    LAST-SCHEDULE
hello     */1 * * * *   False     0         Thu, 6 Sep 2018 14:34:00 -070

```

需要注意的是，由于定时任务的特殊性，很可能某个Job还没有执行完，另外一个新Job就产生了。这时候，你可以通过spec.concurrencyPolicy字段来定义具体的处理策略。比如：

1. concurrencyPolicy=Allow，这也是默认情况，这意味着这些Job可以同时存在；

2. concurrencyPolicy=Forbid，这意味着不会创建新的Pod，该创建周期被跳过；

3. concurrencyPolicy=Replace，这意味着新产生的Job会替换旧的、没有执行完的Job。


而如果某一次Job创建失败，这次创建就会被标记为“miss”。当在指定的时间窗口内，miss的数目达到100时，那么CronJob会停止再创建这个Job。

这个时间窗口，可以由spec.startingDeadlineSeconds字段指定。比如startingDeadlineSeconds=200，意味着在过去200 s里，如果miss的数目达到了100次，那么这个Job就不会被创建执行了。

## 总结

在今天这篇文章中，我主要和你分享了Job这个离线业务的编排方法，讲解了completions和parallelism字段的含义，以及Job Controller的执行原理。

紧接着，我通过实例和你分享了Job对象三种常见的使用方法。但是，根据我在社区和生产环境中的经验，大多数情况下用户还是更倾向于自己控制Job对象。所以，相比于这些固定的“模式”，掌握Job的API对象，和它各个字段的准确含义会更加重要。

最后，我还介绍了一种Job的控制器，叫作：CronJob。这也印证了我在前面的分享中所说的：用一个对象控制另一个对象，是Kubernetes编排的精髓所在。

## 思考题

根据Job控制器的工作原理，如果你定义的parallelism比completions还大的话，比如：

```
 parallelism: 4
 completions: 2

```

那么，这个Job最开始创建的时候，会同时启动几个Pod呢？原因是什么？

感谢你的收听，欢迎你给我留言，也欢迎分享给更多的朋友一起阅读。