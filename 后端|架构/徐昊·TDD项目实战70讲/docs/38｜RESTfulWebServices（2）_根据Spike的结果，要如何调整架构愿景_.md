你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

在上节课，我们通过Spike实现了一个非常简略的版本，可以通过Root Resource以及对应的方法处理请求，并使用MessageBodyWriter扩展点，将内容写入Http响应中。代码如下：

```
static class ResourceServlet extends HttpServlet {

    private Application application;

    private Providers providers;

    public ResourceServlet(Application application, Providers providers) {
        this.application = application;
        this.providers = providers;
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        Stream<Class<?>> rootResources = application.getClasses().stream().filter(c -> c.isAnnotationPresent(Path.class));
        Object result = dispatch(req, rootResources);
        MessageBodyWriter<Object> writer = (MessageBodyWriter<Object>) providers.getMessageBodyWriter(result.getClass(), null, null, null);
        writer.writeTo(result, null, null, null, null, null, resp.getOutputStream());
    }

    Object dispatch(HttpServletRequest req, Stream<Class<?>> rootResources) {
        try {
            Class<?> rootClass = rootResources.findFirst().get();
            Object rootResource = rootClass.getConstructor().newInstance();
            Method method = Arrays.stream(rootClass.getMethods()).filter(m -> m.isAnnotationPresent(GET.class)).findFirst().get();
            return method.invoke(rootResource);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}

```

在这个Spike的基础上，我们可以进一步细化架构的愿景：

![](https://static001.geekbang.org/resource/image/16/e1/165d9ce2d5223bf6498b9c1ceffa71e1.jpg?wh=8000x4500)

通过结合JAX-RS的Application和Providers，我们大致清楚了ResourceServlet如何使用Application和Providers，以及大致在什么地方需要使用依赖注入容器。

说到依赖注入，在JAX-RS中存在两种依赖注入：对于Application Scope的Inject注入，以及对于Request Scope的Context注入。这仍然是不太清晰的部分，我们需要进一步Spike：

## 思考题

根据Spike的结果，接下来要如何进一步调整架构愿景？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！