你好，我是张磊。今天我和你分享的主题是：谈谈Service与Ingress。

在上一篇文章中，我为你详细讲解了将Service暴露给外界的三种方法。其中有一个叫作LoadBalancer类型的Service，它会为你在Cloud Provider（比如：Google Cloud或者OpenStack）里创建一个与该Service对应的负载均衡服务。

但是，相信你也应该能感受到，由于每个 Service 都要有一个负载均衡服务，所以这个做法实际上既浪费成本又高。作为用户，我其实更希望看到Kubernetes为我内置一个全局的负载均衡器。然后，通过我访问的URL，把请求转发给不同的后端Service。

**这种全局的、为了代理不同后端Service而设置的负载均衡服务，就是Kubernetes里的Ingress服务。**

所以，Ingress的功能其实很容易理解： **所谓Ingress，就是Service的“Service”。**

举个例子，假如我现在有这样一个站点： `https://cafe.example.com`。其中， `https://cafe.example.com/coffee`，对应的是“咖啡点餐系统”。而， `https://cafe.example.com/tea`，对应的则是“茶水点餐系统”。这两个系统，分别由名叫coffee和tea这样两个Deployment来提供服务。

那么现在，我如何能使用Kubernetes的Ingress来创建一个统一的负载均衡器，从而实现当用户访问不同的域名时，能够访问到不同的Deployment呢？

上述功能，在Kubernetes里就需要通过Ingress对象来描述，如下所示：

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: cafe-ingress
spec:
  tls:
  - hosts:
    - cafe.example.com
    secretName: cafe-secret
  rules:
  - host: cafe.example.com
    http:
      paths:
      - path: /tea
        backend:
          serviceName: tea-svc
          servicePort: 80
      - path: /coffee
        backend:
          serviceName: coffee-svc
          servicePort: 80

```

在上面这个名叫cafe-ingress.yaml文件中，最值得我们关注的，是rules字段。在Kubernetes里，这个字段叫作： **IngressRule**。

IngressRule的Key，就叫做：host。它必须是一个标准的域名格式（Fully Qualified Domain Name）的字符串，而不能是IP地址。

> 备注：Fully Qualified Domain Name的具体格式，可以参考 [RFC 3986](https://tools.ietf.org/html/rfc3986) 标准。

而host字段定义的值，就是这个Ingress的入口。这也就意味着，当用户访问cafe.example.com的时候，实际上访问到的是这个Ingress对象。这样，Kubernetes就能使用IngressRule来对你的请求进行下一步转发。

而接下来IngressRule规则的定义，则依赖于path字段。你可以简单地理解为，这里的每一个path都对应一个后端Service。所以在我们的例子里，我定义了两个path，它们分别对应coffee和tea这两个Deployment的Service（即：coffee-svc和tea-svc）。

**通过上面的讲解，不难看到，所谓Ingress对象，其实就是Kubernetes项目对“反向代理”的一种抽象。**

一个Ingress对象的主要内容，实际上就是一个“反向代理”服务（比如：Nginx）的配置文件的描述。而这个代理服务对应的转发规则，就是IngressRule。

这就是为什么在每条IngressRule里，需要有一个host字段来作为这条IngressRule的入口，然后还需要有一系列path字段来声明具体的转发策略。这其实跟Nginx、HAproxy等项目的配置文件的写法是一致的。

而有了Ingress这样一个统一的抽象，Kubernetes的用户就无需关心Ingress的具体细节了。

在实际的使用中，你只需要从社区里选择一个具体的Ingress Controller，把它部署在Kubernetes集群里即可。

然后，这个Ingress Controller会根据你定义的Ingress对象，提供对应的代理能力。目前，业界常用的各种反向代理项目，比如Nginx、HAProxy、Envoy、Traefik等，都已经为Kubernetes专门维护了对应的Ingress Controller。

接下来，我就以最常用的Nginx Ingress Controller为例，在我们前面用kubeadm部署的Bare-metal环境中，和你实践一下Ingress机制的使用过程。

部署Nginx Ingress Controller的方法非常简单，如下所示：

```
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml

```

其中，在 [mandatory.yaml](https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/mandatory.yaml) 这个文件里，正是Nginx官方为你维护的Ingress Controller的定义。我们来看一下它的内容：

```
kind: ConfigMap
apiVersion: v1
metadata:
  name: nginx-configuration
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: nginx-ingress-controller
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
      app.kubernetes.io/part-of: ingress-nginx
  template:
    metadata:
      labels:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/part-of: ingress-nginx
      annotations:
        ...
    spec:
      serviceAccountName: nginx-ingress-serviceaccount
      containers:
        - name: nginx-ingress-controller
          image: quay.io/kubernetes-ingress-controller/nginx-ingress-controller:0.20.0
          args:
            - /nginx-ingress-controller
            - --configmap=$(POD_NAMESPACE)/nginx-configuration
            - --publish-service=$(POD_NAMESPACE)/ingress-nginx
            - --annotations-prefix=nginx.ingress.kubernetes.io
          securityContext:
            capabilities:
              drop:
                - ALL
              add:
                - NET_BIND_SERVICE
            # www-data -> 33
            runAsUser: 33
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
            - name: http
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          ports:
            - name: http
              containerPort: 80
            - name: https
              containerPort: 443

```

可以看到，在上述YAML文件中，我们定义了一个使用nginx-ingress-controller镜像的Pod。需要注意的是，这个Pod的启动命令需要使用该Pod所在的Namespace作为参数。而这个信息，当然是通过Downward API拿到的，即：Pod的env字段里的定义（env.valueFrom.fieldRef.fieldPath）。

而这个Pod本身，就是一个监听Ingress对象以及它所代理的后端Service变化的控制器。

当一个新的Ingress对象由用户创建后，nginx-ingress-controller就会根据Ingress对象里定义的内容，生成一份对应的Nginx配置文件（/etc/nginx/nginx.conf），并使用这个配置文件启动一个 Nginx 服务。

而一旦Ingress对象被更新，nginx-ingress-controller就会更新这个配置文件。需要注意的是，如果这里只是被代理的 Service 对象被更新，nginx-ingress-controller所管理的 Nginx 服务是不需要重新加载（reload）的。这当然是因为nginx-ingress-controller通过 [Nginx Lua](https://github.com/openresty/lua-nginx-module) 方案实现了Nginx Upstream的动态配置。

此外，nginx-ingress-controller还允许你通过Kubernetes的ConfigMap对象来对上述 Nginx 配置文件进行定制。这个ConfigMap的名字，需要以参数的方式传递给nginx-ingress-controller。而你在这个 ConfigMap 里添加的字段，将会被合并到最后生成的 Nginx 配置文件当中。

**可以看到，一个Nginx Ingress Controller为你提供的服务，其实是一个可以根据Ingress对象和被代理后端 Service 的变化，来自动进行更新的Nginx负载均衡器。**

当然，为了让用户能够用到这个Nginx，我们就需要创建一个Service来把Nginx Ingress Controller管理的 Nginx 服务暴露出去，如下所示：

```
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/provider/baremetal/service-nodeport.yaml

```

由于我们使用的是Bare-metal环境，所以service-nodeport.yaml文件里的内容，就是一个NodePort类型的Service，如下所示：

```
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
spec:
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: 80
      protocol: TCP
    - name: https
      port: 443
      targetPort: 443
      protocol: TCP
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx

```

可以看到，这个Service的唯一工作，就是将所有携带ingress-nginx标签的Pod的80和433端口暴露出去。

> 而如果你是公有云上的环境，你需要创建的就是LoadBalancer类型的Service了。

**上述操作完成后，你一定要记录下这个Service的访问入口，即：宿主机的地址和NodePort的端口**，如下所示：

```
$ kubectl get svc -n ingress-nginx
NAME            TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx   NodePort   10.105.72.96   <none>        80:30044/TCP,443:31453/TCP   3h

```

为了后面方便使用，我会把上述访问入口设置为环境变量：

```
$ IC_IP=10.168.0.2 # 任意一台宿主机的地址
$ IC_HTTPS_PORT=31453 # NodePort端口

```

在Ingress Controller和它所需要的Service部署完成后，我们就可以使用它了。

> 备注：这个“咖啡厅”Ingress的所有示例文件，都在 [这里](https://github.com/resouer/kubernetes-ingress/tree/master/examples/complete-example)。

首先，我们要在集群里部署我们的应用Pod和它们对应的Service，如下所示：

```
$ kubectl create -f cafe.yaml

```

然后，我们需要创建Ingress所需的SSL证书（tls.crt）和密钥（tls.key），这些信息都是通过Secret对象定义好的，如下所示：

```
$ kubectl create -f cafe-secret.yaml

```

这一步完成后，我们就可以创建在本篇文章一开始定义的Ingress对象了，如下所示：

```
$ kubectl create -f cafe-ingress.yaml

```

这时候，我们就可以查看一下这个Ingress对象的信息，如下所示：

```
$ kubectl get ingress
NAME           HOSTS              ADDRESS   PORTS     AGE
cafe-ingress   cafe.example.com             80, 443   2h

$ kubectl describe ingress cafe-ingress
Name:             cafe-ingress
Namespace:        default
Address:
Default backend:  default-http-backend:80 (<none>)
TLS:
  cafe-secret terminates cafe.example.com
Rules:
  Host              Path  Backends
  ----              ----  --------
  cafe.example.com
                    /tea      tea-svc:80 (<none>)
                    /coffee   coffee-svc:80 (<none>)
Annotations:
Events:
  Type    Reason  Age   From                      Message
  ----    ------  ----  ----                      -------
  Normal  CREATE  4m    nginx-ingress-controller  Ingress default/cafe-ingress

```

可以看到，这个Ingress对象最核心的部分，正是Rules字段。其中，我们定义的Host是 `cafe.example.com`，它有两条转发规则（Path），分别转发给tea-svc和coffee-svc。

> 当然，在Ingress的YAML文件里，你还可以定义多个Host，比如 `restaurant.example.com`、 `movie.example.com` 等等，来为更多的域名提供负载均衡服务。

接下来，我们就可以通过访问这个Ingress的地址和端口，访问到我们前面部署的应用了，比如，当我们访问 `https://cafe.example.com:443/coffee` 时，应该是coffee这个Deployment负责响应我的请求。我们可以来尝试一下：

```
$ curl --resolve cafe.example.com:$IC_HTTPS_PORT:$IC_IP https://cafe.example.com:$IC_HTTPS_PORT/coffee --insecureServer address: 10.244.1.56:80
Server name: coffee-7dbb5795f6-vglbv
Date: 03/Nov/2018:03:55:32 +0000
URI: /coffee
Request ID: e487e672673195c573147134167cf898

```

我们可以看到，访问这个URL 得到的返回信息是：Server name: coffee-7dbb5795f6-vglbv。这正是 coffee 这个 Deployment 的名字。

而当我访问 `https://cafe.example.com:433/tea` 的时候，则应该是tea这个Deployment负责响应我的请求（Server name: tea-7d57856c44-lwbnp），如下所示：

```
$ curl --resolve cafe.example.com:$IC_HTTPS_PORT:$IC_IP https://cafe.example.com:$IC_HTTPS_PORT/tea --insecure
Server address: 10.244.1.58:80
Server name: tea-7d57856c44-lwbnp
Date: 03/Nov/2018:03:55:52 +0000
URI: /tea
Request ID: 32191f7ea07cb6bb44a1f43b8299415c

```

可以看到，Nginx Ingress Controller为我们创建的Nginx负载均衡器，已经成功地将请求转发给了对应的后端Service。

以上，就是Kubernetes里Ingress的设计思想和使用方法了。

不过，你可能会有一个疑问， **如果我的请求没有匹配到任何一条IngressRule，那么会发生什么呢？**

首先，既然Nginx Ingress Controller是用Nginx实现的，那么它当然会为你返回一个 Nginx 的404页面。

不过，Ingress Controller也允许你通过Pod启动命令里的–default-backend-service参数，设置一条默认规则，比如：–default-backend-service=nginx-default-backend。

这样，任何匹配失败的请求，就都会被转发到这个名叫nginx-default-backend的Service。所以，你就可以通过部署一个专门的Pod，来为用户返回自定义的404页面了。

## 总结

在这篇文章里，我为你详细讲解了Ingress这个概念在Kubernetes里到底是怎么一回事儿。正如我在文章里所描述的，Ingress实际上就是Kubernetes对“反向代理”的抽象。

目前，Ingress只能工作在七层，而Service只能工作在四层。所以当你想要在Kubernetes里为应用进行TLS配置等HTTP相关的操作时，都必须通过Ingress来进行。

当然，正如同很多负载均衡项目可以同时提供七层和四层代理一样，将来Ingress的进化中，也会加入四层代理的能力。这样，一个比较完善的“反向代理”机制就比较成熟了。

而Kubernetes提出Ingress概念的原因其实也非常容易理解，有了Ingress这个抽象，用户就可以根据自己的需求来自由选择Ingress Controller。比如，如果你的应用对代理服务的中断非常敏感，那么你就应该考虑选择类似于Traefik这样支持“热加载”的Ingress Controller实现。

更重要的是，一旦你对社区里现有的Ingress方案感到不满意，或者你已经有了自己的负载均衡方案时，你只需要做很少的编程工作，就可以实现一个自己的Ingress Controller。

在实际的生产环境中，Ingress带来的灵活度和自由度，对于使用容器的用户来说，其实是非常有意义的。要知道，当年在Cloud Foundry项目里，不知道有多少人为了给Gorouter组件配置一个TLS而伤透了脑筋。

## 思考题

如果我的需求是，当访问 `www.mysite.com` 和 `forums.mysite.com` 时，分别访问到不同的Service（比如：site-svc和forums-svc）。那么，这个Ingress该如何定义呢？请你描述出YAML文件中的rules字段。

感谢你的收听，欢迎你给我留言，也欢迎分享给更多的朋友一起阅读。