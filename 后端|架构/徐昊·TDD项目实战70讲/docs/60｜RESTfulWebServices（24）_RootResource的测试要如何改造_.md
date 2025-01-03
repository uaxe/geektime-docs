你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

目前我们已经实现了ResourceRouter，和UriTemplate整体的架构愿景如下：

![](https://static001.geekbang.org/resource/image/6c/yy/6c626153c86cd68fec66b5ce9d9cb1yy.jpg?wh=2284x1285)

![](https://static001.geekbang.org/resource/image/0b/36/0be0e96754f217b36d12e1edeb9ba936.jpg?wh=2284x1285)

目前的任务列表：

- Resource/RootResource/ResourceMethod
  - 从Path标注中获取UriTemplate
    - 如不存在Path标注，则抛出异常
  - 在处理请求派分时，可以根据客户端提供的Http方法，选择对应的资源方法
    - 当请求与资源方法的Uri模版一致，且Http方法一致时，派分到该方法
    - 没有资源方法于请求的Uri和Http方法一致时，返回404
  - 在处理请求派分时，可以支持多级子资源
    - 当没有资源方法可以匹配请求时，选择最优匹配SubResourceLocater，通过它继续进行派分
    - 如果SubResourceLocator也无法找到满足的请求时，返回404

代码为：

```
class ResourceMethods {
    private Map<String, List<ResourceRouter.ResourceMethod>> resourceMethods;
    public ResourceMethods(Method[] methods) {
        this.resourceMethods = getResourceMethods(methods);
    }
    private static Map<String, List<ResourceRouter.ResourceMethod>> getResourceMethods(Method[] methods) {
        return Arrays.stream(methods).filter(m -> Arrays.stream(m.getAnnotations())
                        .anyMatch(a -> a.annotationType().isAnnotationPresent(HttpMethod.class)))
                .map(DefaultResourceMethod::new)
                .collect(Collectors.groupingBy(ResourceRouter.ResourceMethod::getHttpMethod));
    }
    public Optional<ResourceRouter.ResourceMethod> findResourceMethods(String path, String method) {
        return Optional.ofNullable(resourceMethods.get(method)).flatMap(methods -> methods.stream().map(m -> match(path, m)).filter(Result::isMatched).sorted()
                .findFirst().map(Result::resourceMethod));
    }
    private static Result match(String path, ResourceRouter.ResourceMethod method) {
        return new Result(method.getUriTemplate().match(path), method);
    }
    static record Result(Optional<UriTemplate.MatchResult> matched,
                         ResourceRouter.ResourceMethod resourceMethod) implements Comparable<Result> {
        public boolean isMatched() {
            return matched.map(r -> r.getRemaining() == null).orElse(false);
        }
        @Override
        public int compareTo(Result o) {
            return matched.flatMap(x -> o.matched.map(x::compareTo)).orElse(0);
        }
    }
}
class RootResourceClass implements ResourceRouter.RootResource {
    private PathTemplate uriTemplate;
    private Class<?> resourceClass;
    private ResourceMethods resourceMethods;
    public RootResourceClass(Class<?> resourceClass) {
        this.resourceClass = resourceClass;
        this.uriTemplate = new PathTemplate(resourceClass.getAnnotation(Path.class).value());
        this.resourceMethods = new ResourceMethods(resourceClass.getMethods());
    }
    @Override
    public Optional<ResourceRouter.ResourceMethod> match(UriTemplate.MatchResult result, String method, String[] mediaTypes, UriInfoBuilder builder) {
        String remaining = Optional.ofNullable(result.getRemaining()).orElse("");
        return resourceMethods.findResourceMethods(remaining, method);
    }
    @Override
    public UriTemplate getUriTemplate() {
        return uriTemplate;
    }
}
class SubResource implements ResourceRouter.Resource {
    private Object subResource;
    private ResourceMethods resourceMethods;
    public SubResource(Object subResource) {
        this.subResource = subResource;
        this.resourceMethods = new ResourceMethods(subResource.getClass().getMethods());
    }
    @Override
    public Optional<ResourceRouter.ResourceMethod> match(UriTemplate.MatchResult result, String method, String[] mediaTypes, UriInfoBuilder builder) {
        String remaining = Optional.ofNullable(result.getRemaining()).orElse("");
        return resourceMethods.findResourceMethods(remaining, method);
    }
}
class DefaultResourceMethod implements ResourceRouter.ResourceMethod {
    private String httpMethod;
    private UriTemplate uriTemplate;
    private Method method;
    public DefaultResourceMethod(Method method) {
        this.method = method;
        this.uriTemplate = new PathTemplate(Optional.ofNullable(method.getAnnotation(Path.class)).map(Path::value).orElse(""));
        this.httpMethod = Arrays.stream(method.getAnnotations()).filter(a -> a.annotationType().isAnnotationPresent(HttpMethod.class))
                .findFirst().get().annotationType().getAnnotation(HttpMethod.class).value();
    }
    @Override
    public String getHttpMethod() {
        return httpMethod;
    }
    @Override
    public UriTemplate getUriTemplate() {
        return uriTemplate;
    }
    @Override
    public GenericEntity<?> call(ResourceContext resourceContext, UriInfoBuilder builder) {
        return null;
    }
    @Override
    public String toString() {
        return method.getDeclaringClass().getSimpleName() + "." + method.getName();
    }
}

```

## 视频演示

进入今天的环节：

## 思考题

如何重构DefaultResourceRouter中的Result结构？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！