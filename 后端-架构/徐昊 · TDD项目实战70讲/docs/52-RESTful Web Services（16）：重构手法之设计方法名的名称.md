你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

目前我们的架构愿景如下：

![](https://static001.geekbang.org/resource/image/59/24/59ee2d534a4ae87623a736157e848924.jpg?wh=2284x1285)

![](https://static001.geekbang.org/resource/image/2e/a4/2ef7e84ba450b36d1df67cfce9e61da4.jpg?wh=2284x1285)

任务列表如下：

- ResourceRouter
  - 将Resource Method的返回值包装为Response对象
    - 根据与Path匹配结果，降序排列RootResource，选择第一个的RootResource
    - 如果没有匹配的RootResource，则构造404的Response
    - 如果返回的RootResource中无法匹配剩余Path，则构造404的Response
    - 如果ResourceMethod返回null，则构造204的Response

代码目前是：

```
class DefaultResourceRouter implements ResourceRouter {
    private Runtime runtime;
    private List<RootResource> rootResources;
    public DefaultResourceRouter(Runtime runtime, List<RootResource> rootResources) {
        this.runtime = runtime;
        this.rootResources = rootResources;
    }
    @Override
    public OutboundResponse dispatch(HttpServletRequest request, ResourceContext resourceContext) {
        String path = request.getServletPath();
        UriInfoBuilder uri = runtime.createUriInfoBuilder(request);
        Optional<Result> matched = rootResources.stream().map(resource -> new Result(resource.getUriTemplate().match(path), resource))
                .filter(result -> result.matched.isPresent()).sorted((x, y) -> x.matched.get().compareTo(y.matched.get())).findFirst();
        Optional<ResourceMethod> method = matched.flatMap(result -> result.resource.match(result.matched.get().getRemaining(),
                request.getMethod(), Collections.list(request.getHeaders(HttpHeaders.ACCEPT)).toArray(String[]::new), uri));
        GenericEntity<?> entity = method.map(m -> m.call(resourceContext, uri)).get();
        return (OutboundResponse) Response.ok(entity).build();
    }
    record Result(Optional<UriTemplate.MatchResult> matched, RootResource resource) {
    }
}

```

## 视频演示

下面进入今日的开发：

## 思考题

在进入下节课之前，希望你能认真思考如下两个问题。

1. 接下来是否还需要进行Spike的架构愿景细化？
2. 你有没有什么比较好的学习TDD的方法？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！