你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

目前我们已经实现了ResourceRouter，和UriTemplate整体的架构愿景如下：

![](https://static001.geekbang.org/resource/image/c1/bd/c1a8d4b80fcf2c009a448d996594b6bd.jpg?wh=2284x1264)

![](https://static001.geekbang.org/resource/image/fd/06/fd32fcbe73cb3d406f7473a0798a8d06.jpg?wh=2284x1285)

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
package geektime.tdd.rest;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.ws.rs.HttpMethod;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.container.ResourceContext;
import jakarta.ws.rs.core.GenericEntity;
import jakarta.ws.rs.core.HttpHeaders;
import jakarta.ws.rs.core.Response;
import java.lang.reflect.Method;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
interface ResourceRouter {
    OutboundResponse dispatch(HttpServletRequest request, ResourceContext resourceContext);
    interface Resource extends UriHandler {
        Optional<ResourceMethod> match(UriTemplate.MatchResult result, String httpMethod, String[] mediaTypes, ResourceContext resourceContext, UriInfoBuilder builder);
    }
    interface ResourceMethod extends UriHandler {
        String getHttpMethod();
        GenericEntity<?> call(ResourceContext resourceContext, UriInfoBuilder builder);
    }
}
class DefaultResourceRouter implements ResourceRouter {
    private Runtime runtime;
    private List<Resource> rootResources;
    public DefaultResourceRouter(Runtime runtime, List<Resource> rootResources) {
        this.runtime = runtime;
        this.rootResources = rootResources;
    }
    @Override
    public OutboundResponse dispatch(HttpServletRequest request, ResourceContext resourceContext) {
        String path = request.getServletPath();
        UriInfoBuilder uri = runtime.createUriInfoBuilder(request);
        Optional<ResourceMethod> method = UriHandlers.mapMatched(path, rootResources, (result, resource) -> findResourceMethod(request, resourceContext, uri, result, resource));
        if (method.isEmpty()) return (OutboundResponse) Response.status(Response.Status.NOT_FOUND).build();
        return (OutboundResponse) method.map(m -> m.call(resourceContext, uri)).map(entity -> Response.ok(entity).build())
                .orElseGet(() -> Response.noContent().build());
    }
    private Optional<ResourceMethod> findResourceMethod(HttpServletRequest request, ResourceContext resourceContext, UriInfoBuilder uri, Optional<UriTemplate.MatchResult> matched, Resource handler) {
        return handler.match(matched.get(), request.getMethod(),
                Collections.list(request.getHeaders(HttpHeaders.ACCEPT)).toArray(String[]::new), resourceContext, uri);
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
class   ResourceMethods {
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
        return Optional.ofNullable(resourceMethods.get(method)).flatMap(methods -> UriHandlers.match(path, methods, r -> r.getRemaining() == null));
    }
}
class SubResourceLocators {
    private final List<ResourceRouter.Resource> subResourceLocators;
    public SubResourceLocators(Method[] methods) {
        subResourceLocators = Arrays.stream(methods).filter(m -> m.isAnnotationPresent(Path.class) &&
                        Arrays.stream(m.getAnnotations()).noneMatch(a -> a.annotationType().isAnnotationPresent(HttpMethod.class)))
                .map((Function<Method, ResourceRouter.Resource>) SubResourceLocator::new).toList();
    }
    public Optional<ResourceRouter.ResourceMethod> findSubResourceMethods(String path, String method, String[] mediaTypes, ResourceContext resourceContext, UriInfoBuilder builder) {
        return UriHandlers.mapMatched(path, subResourceLocators, (result, locator) -> locator.match(result.get(), method, mediaTypes, resourceContext, builder));
    }
    static class SubResourceLocator implements ResourceRouter.Resource {
        private PathTemplate uriTemplate;
        private Method method;
        public SubResourceLocator(Method method) {
            this.method = method;
            this.uriTemplate = new PathTemplate(method.getAnnotation(Path.class).value());
        }
        @Override
        public UriTemplate getUriTemplate() {
            return uriTemplate;
        }
        @Override
        public String toString() {
            return method.getDeclaringClass().getSimpleName() + "." + method.getName();
        }
        @Override
        public Optional<ResourceRouter.ResourceMethod> match(UriTemplate.MatchResult result, String httpMethod, String[] mediaTypes, ResourceContext resourceContext, UriInfoBuilder builder) {
            Object resource = builder.getLastMatchedResource();
            try {
                Object subResource = method.invoke(resource);
                return new ResourceHandler(subResource, uriTemplate).match(result, httpMethod, mediaTypes, resourceContext, builder);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }
}
class ResourceHandler implements ResourceRouter.Resource {
    private UriTemplate uriTemplate;
    private ResourceMethods resourceMethods;
    private SubResourceLocators subResourceLocators;
    private Function<ResourceContext, Object> resource;

    public ResourceHandler(Class<?> resourceClass) {
        this(resourceClass, new PathTemplate(getTemplate(resourceClass)), rc -> rc.getResource(resourceClass));
    }
    private static String getTemplate(Class<?> resourceClass) {
        if (!resourceClass.isAnnotationPresent(Path.class)) throw new IllegalArgumentException();
        return resourceClass.getAnnotation(Path.class).value();
    }
    public ResourceHandler(Object resource, UriTemplate uriTemplate) {
        this(resource.getClass(), uriTemplate, rc -> resource);
    }
    private ResourceHandler(Class<?> resourceClass, UriTemplate uriTemplate, Function<ResourceContext, Object> resource) {
        this.uriTemplate = uriTemplate;
        this.resourceMethods = new ResourceMethods(resourceClass.getMethods());
        this.subResourceLocators = new SubResourceLocators(resourceClass.getMethods());
        this.resource = resource;
    }
    @Override
    public Optional<ResourceRouter.ResourceMethod> match(UriTemplate.MatchResult result, String httpMethod, String[] mediaTypes, ResourceContext resourceContext, UriInfoBuilder builder) {
        builder.addMatchedResource(resource.apply(resourceContext));
        String remaining = Optional.ofNullable(result.getRemaining()).orElse("");
        return resourceMethods.findResourceMethods(remaining, httpMethod)
                .or(() -> subResourceLocators.findSubResourceMethods(remaining, httpMethod, mediaTypes, resourceContext, builder));
    }
    @Override
    public UriTemplate getUriTemplate() {
        return uriTemplate;
    }
}

```

## 视频演示

进入今天的环节：

## 思考题

今天的思考题有两道，请选择你最有感触的一道来回答。

1. 学习到现在，你有向其他朋友或同事推荐过TDD吗？成功还是失败了？如果失败了，那么在你看来可能的原因是什么呢？
2. 如何实现head方法不去调用get的内容？

欢迎把你的思考或想法分享在留言区，咱们下节课再见！