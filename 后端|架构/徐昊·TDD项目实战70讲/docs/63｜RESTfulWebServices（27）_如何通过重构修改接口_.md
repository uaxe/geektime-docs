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
    interface Resource {
        Optional<ResourceMethod> match(UriTemplate.MatchResult result, String method, String[] mediaTypes, UriInfoBuilder builder);
    }
    interface RootResource extends Resource, UriHandler {
    }
    interface ResourceMethod extends UriHandler {
        String getHttpMethod();
        GenericEntity<?> call(ResourceContext resourceContext, UriInfoBuilder builder);
    }
    interface SubResourceLocator extends UriHandler {
        Resource getSubResource(ResourceContext resourceContext, UriInfoBuilder uriInfoBuilder);
    }
}
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
        Optional<ResourceMethod> method = UriHandlers.mapMatched(path, rootResources, (result, resource) -> findResourceMethod(request, uri, result, resource));
        if (method.isEmpty()) return (OutboundResponse) Response.status(Response.Status.NOT_FOUND).build();
        return (OutboundResponse) method.map(m -> m.call(resourceContext, uri)).map(entity -> Response.ok(entity).build())
                .orElseGet(() -> Response.noContent().build());
    }
    private Optional<ResourceMethod> findResourceMethod(HttpServletRequest request, UriInfoBuilder uri, Optional<UriTemplate.MatchResult> matched, RootResource handler) {
        return handler.match(matched.get(), request.getMethod(),
                Collections.list(request.getHeaders(HttpHeaders.ACCEPT)).toArray(String[]::new), uri);
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
        return Optional.ofNullable(resourceMethods.get(method)).flatMap(methods -> UriHandlers.match(path, methods, r -> r.getRemaining() == null));
    }
}
class SubResourceLocators {
    private final List<ResourceRouter.SubResourceLocator> subResourceLocators;
    public SubResourceLocators(Method[] methods) {
        subResourceLocators = Arrays.stream(methods).filter(m -> m.isAnnotationPresent(Path.class) &&
                        Arrays.stream(m.getAnnotations()).noneMatch(a -> a.annotationType().isAnnotationPresent(HttpMethod.class)))
                .map((Function<Method, ResourceRouter.SubResourceLocator>) DefaultSubResourceLocator::new).toList();
    }
    public Optional<ResourceRouter.SubResourceLocator> findSubResource(String path) {
        return UriHandlers.match(path, subResourceLocators);
    }
    static class DefaultSubResourceLocator implements ResourceRouter.SubResourceLocator {
        private PathTemplate uriTemplate;
        private Method method;
        public DefaultSubResourceLocator(Method method) {
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
        public ResourceRouter.Resource getSubResource(ResourceContext resourceContext, UriInfoBuilder uriInfoBuilder) {
            Object resource = uriInfoBuilder.getLastMatchedResource();
            try {
                Object subResource = method.invoke(resource);
                uriInfoBuilder.addMatchedResource(subResource);
                return new SubResource(subResource);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }
}

```

## 视频演示

进入今天的环节：

## 思考题

如何重构Resource、SubResource等接口与实现？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！