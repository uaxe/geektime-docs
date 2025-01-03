你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

![](https://static001.geekbang.org/resource/image/c1/bd/c1a8d4b80fcf2c009a448d996594b6bd.jpg?wh=2284x1264)

![](https://static001.geekbang.org/resource/image/fd/06/fd32fcbe73cb3d406f7473a0798a8d06.jpg?wh=2284x1285)

目前的任务列表：

- Resource/RootResource/ResourceMethods
  - 当HEAD方法映射到GET方法时，忽略GET的返回值
  - 当没有OPTIONS方法时，提供默认实现

代码为：

```
package geektime.tdd.rest;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.ws.rs.HttpMethod;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.container.ResourceContext;
import jakarta.ws.rs.core.GenericEntity;
import jakarta.ws.rs.core.HttpHeaders;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.UriInfo;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Parameter;
import java.lang.reflect.Type;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import static geektime.tdd.rest.DefaultResourceMethod.ValueConverter.singeValued;
import static java.util.Arrays.stream;
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
        return (OutboundResponse) method.map(m -> m.call(resourceContext, uri))
                .map(entity -> (entity.getEntity() instanceof OutboundResponse) ? (OutboundResponse) entity.getEntity() : Response.ok(entity).build())
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
        this.httpMethod = stream(method.getAnnotations()).filter(a -> a.annotationType().isAnnotationPresent(HttpMethod.class))
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
        try {
            UriInfo uriInfo = builder.createUriInfo();
            Object result = method.invoke(builder.getLastMatchedResource(),
                    stream(method.getParameters()).map(parameter ->
                            injectParameter(parameter, uriInfo)
                                    .or(() -> injectContext(parameter, resourceContext, uriInfo))
                                    .orElse(null)).toArray(Object[]::new));
            return result != null ? new GenericEntity<>(result, method.getGenericReturnType()) : null;
        } catch (IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }
    }
    private Optional<Object> injectParameter(Parameter parameter, UriInfo uriInfo) {
        return providers.stream().map(provider -> provider.provide(parameter, uriInfo)).filter(Optional::isPresent)
                .findFirst()
                .flatMap(values -> values.flatMap(v -> convert(parameter, v)));
    }
    private Optional<Object> injectContext(Parameter parameter, ResourceContext resourceContext, UriInfo uriInfo) {
        if (parameter.getType().equals(ResourceContext.class)) return Optional.of(resourceContext);
        if (parameter.getType().equals(UriInfo.class)) return Optional.of(uriInfo);
        return Optional.of(resourceContext.getResource(parameter.getType()));
    }
    private Optional<Object> convert(Parameter parameter, List<String> values) {
        return PrimitiveConverter.convert(parameter, values)
                .or(() -> ConverterConstructor.convert(parameter.getType(), values.get(0)))
                .or(() -> ConverterFactory.convert(parameter.getType(), values.get(0)));
    }
    private static ValueProvider pathParam = (parameter, uriInfo) ->
            Optional.ofNullable(parameter.getAnnotation(PathParam.class))
                    .map(annotation -> uriInfo.getPathParameters().get(annotation.value()));
    private static ValueProvider queryParam = (parameter, uriInfo) ->
            Optional.ofNullable(parameter.getAnnotation(QueryParam.class))
                    .map(annotation -> uriInfo.getQueryParameters().get(annotation.value()));
    private static List<ValueProvider> providers = List.of(pathParam, queryParam);
    interface ValueProvider {
        Optional<List<String>> provide(Parameter parameter, UriInfo uriInfo);
    }
    interface ValueConverter<T> {
        T fromString(List<String> values);
        static <T> ValueConverter<T> singeValued(Function<String, T> converter) {
            return values -> converter.apply(values.get(0));
        }
    }

    @Override
    public String toString() {
        return method.getDeclaringClass().getSimpleName() + "." + method.getName();
    }
}
class PrimitiveConverter {
    private static Map<Type, DefaultResourceMethod.ValueConverter<Object>> primitives = Map.of(
            int.class, singeValued(Integer::parseInt),
            double.class, singeValued(Double::parseDouble),
            short.class, singeValued(Short::parseShort),
            float.class, singeValued(Float::parseFloat),
            byte.class, singeValued(Byte::parseByte),
            boolean.class, singeValued(Boolean::parseBoolean),
            String.class, singeValued(s -> s));
    public static Optional<Object> convert(Parameter parameter, List<String> values) {
        return Optional.ofNullable(primitives.get(parameter.getType()))
                .map(c -> c.fromString(values));
    }
}
class ConverterConstructor {
    public static Optional<Object> convert(Class<?> converter, String value) {
        try {
            return Optional.of(converter.getConstructor(String.class).newInstance(value));
        } catch (InstantiationException | IllegalAccessException | InvocationTargetException |
                 NoSuchMethodException e) {
            return Optional.empty();
        }
    }
}
class ConverterFactory {
    public static Optional<Object> convert(Class<?> converter, String value) {
        try {
            return Optional.of(converter.getMethod("valueOf", String.class).invoke(null, value));
        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
            return Optional.empty();
        }
    }
}
class ResourceMethods {
    private Map<String, List<ResourceRouter.ResourceMethod>> resourceMethods;
    public ResourceMethods(Method[] methods) {
        this.resourceMethods = getResourceMethods(methods);
    }
    private static Map<String, List<ResourceRouter.ResourceMethod>> getResourceMethods(Method[] methods) {
        return stream(methods).filter(m -> stream(m.getAnnotations())
                        .anyMatch(a -> a.annotationType().isAnnotationPresent(HttpMethod.class)))
                .map(DefaultResourceMethod::new)
                .collect(Collectors.groupingBy(ResourceRouter.ResourceMethod::getHttpMethod));
    }
    public Optional<ResourceRouter.ResourceMethod> findResourceMethods(String path, String method) {
        return findMethod(path, method).or(() -> findAlternative(path, method));
    }
    private Optional<ResourceRouter.ResourceMethod> findAlternative(String path, String method) {
        if (HttpMethod.HEAD.equals(method)) return findMethod(path, HttpMethod.GET).map(HeadResourceMethod::new);
        if (HttpMethod.OPTIONS.equals(method)) return Optional.of(new OptionResourceMethod(path));
        return Optional.empty();
    }
    private Optional<ResourceRouter.ResourceMethod> findMethod(String path, String method) {
        return Optional.ofNullable(resourceMethods.get(method)).flatMap(methods -> UriHandlers.match(path, methods, r -> r.getRemaining() == null));
    }
    class OptionResourceMethod implements ResourceRouter.ResourceMethod {
        private String path;
        public OptionResourceMethod(String path) {
            this.path = path;
        }
        @Override
        public String getHttpMethod() {
            return HttpMethod.OPTIONS;
        }
        @Override
        public GenericEntity<?> call(ResourceContext resourceContext, UriInfoBuilder builder) {
            return new GenericEntity<>(Response.noContent().allow(findAllowedMethods()).build(), Response.class);
        }
        private Set<String> findAllowedMethods() {
            Set<String> allowed = List.of(HttpMethod.GET, HttpMethod.HEAD, HttpMethod.OPTIONS, HttpMethod.PUT,
                            HttpMethod.POST, HttpMethod.DELETE, HttpMethod.PATCH).stream()
                    .filter(method -> findMethod(path, method).isPresent()).collect(Collectors.toSet());
            allowed.add(HttpMethod.OPTIONS);
            if (allowed.contains(HttpMethod.GET)) allowed.add(HttpMethod.HEAD);
            return allowed;
        }
        @Override
        public UriTemplate getUriTemplate() {
            return new PathTemplate(path);
        }
    }
}
class HeadResourceMethod implements ResourceRouter.ResourceMethod {
    ResourceRouter.ResourceMethod method;
    public HeadResourceMethod(ResourceRouter.ResourceMethod method) {
        this.method = method;
    }
    @Override
    public String getHttpMethod() {
        return HttpMethod.HEAD;
    }
    @Override
    public GenericEntity<?> call(ResourceContext resourceContext, UriInfoBuilder builder) {
        method.call(resourceContext, builder);
        return null;
    }
    @Override
    public UriTemplate getUriTemplate() {
        return method.getUriTemplate();
    }
}
class SubResourceLocators {
    private final List<ResourceRouter.Resource> subResourceLocators;
    public SubResourceLocators(Method[] methods) {
        subResourceLocators = stream(methods).filter(m -> m.isAnnotationPresent(Path.class) &&
                        stream(m.getAnnotations()).noneMatch(a -> a.annotationType().isAnnotationPresent(HttpMethod.class)))
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

如何重构并复用测试？

欢迎把你的思考和想法分享在留言区，咱们下节课再见！