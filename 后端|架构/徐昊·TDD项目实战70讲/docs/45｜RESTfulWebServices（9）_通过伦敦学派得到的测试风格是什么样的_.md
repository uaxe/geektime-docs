你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

目前我们的架构愿景如下：

![](https://static001.geekbang.org/resource/image/ed/2e/ed95e0629105b3fe661590be6ab4af2e.jpg?wh=2284x1285)

![](https://static001.geekbang.org/resource/image/aa/56/aacdc2230e337d593308c0184b799956.jpg?wh=2284x1285)

任务列表为：

- ResourceServlet
  - 将请求派分给对应的资源（Resource），并根据返回的状态、超媒体类型、内容，响应Http请求
    - 使用OutboundResponse的status作为Http Response的状态
    - 使用OutboundResponse的headers作为Http Response的Http Headers
    - 通过MessageBodyWriter将OutboundResponse的GenericEntity写回为Body
    - 如果找不到对应的MessageBodyWriter，则返回500族错误
    - 如果找不到对应的HeaderDelegate，则返回500族错误
    - 如果找不到对应的ExceptionMapper，则返回500族错误
    - 如果entity为空，则忽略body
  - 当资源方法抛出异常时，根据异常响应Http请求
    - 如果抛出WebApplicationException，且response不为null，则使用response响应Http
    - 如果抛出的不是WebApplicationException，则通过异常的具体类型查找ExceptionMapper，生产response响应Http请求
  - 当其他组件抛出异常时，根据异常响应Http请求
    - 调用ExceptionMapper时
    - 调用HeaderDelegate时
    - 调用MessageBodyWriter时
    - 通过Providers查找ExceptionMapper时
    - 通过Providers查找MessageBodyWriter时
    - 通过RuntimeDelegate查找HeaderDelegate时
- RuntimeDelegate
  - 为MediaType提供HeaderDelegate
  - 为CacheControl提供HeaderDelegate
  - 为Cookie提供HeaderDelegates
  - 为EntityTag提供HeaderDelegate
  - 为Link提供HeaderDelegate
  - 为NewCookie提供HeaderDelegate
  - 为Date提供HeaderDelegate
  - 提供OutboundResponseBuilder
- OutboundResponseBuilder

- OutboundResponse


代码为：

```
package geektime.tdd.rest;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.ws.rs.WebApplicationException;
import jakarta.ws.rs.core.GenericEntity;
import jakarta.ws.rs.core.MultivaluedMap;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.MessageBodyWriter;
import jakarta.ws.rs.ext.Providers;
import jakarta.ws.rs.ext.RuntimeDelegate;
import java.io.IOException;
import java.util.function.Supplier;

public class ResourceServlet extends HttpServlet {
    private Runtime runtime;
    private Providers providers;

    public ResourceServlet(Runtime runtime) {
        this.runtime = runtime;
        this.providers = runtime.getProviders();
    }

    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        ResourceRouter router = runtime.getResourceRouter();
        respond(resp, () -> router.dispatch(req, runtime.createResourceContext(req, resp)));
    }

    private void respond(HttpServletResponse resp, Supplier<OutboundResponse> supplier) {
        try {
            respond(resp, supplier.get());
        } catch (WebApplicationException exception) {
            respond(resp, () -> (OutboundResponse) exception.getResponse());
        } catch (Throwable throwable) {
            respond(resp, () -> from(throwable));
        }
    }

    private void respond(HttpServletResponse resp, OutboundResponse response) throws IOException {
        resp.setStatus(response.getStatus());
        MultivaluedMap<String, Object> headers = response.getHeaders();
        for (String name : headers.keySet())
            for (Object value : headers.get(name)) {
                RuntimeDelegate.HeaderDelegate headerDelegate = RuntimeDelegate.getInstance().createHeaderDelegate(value.getClass());
                resp.addHeader(name, headerDelegate.toString(value));
            }
        GenericEntity entity = response.getGenericEntity();
        if (entity != null) {
            MessageBodyWriter writer = providers.getMessageBodyWriter(entity.getRawType(), entity.getType(), response.getAnnotations(), response.getMediaType());
            writer.writeTo(entity.getEntity(), entity.getRawType(), entity.getType(), response.getAnnotations(), response.getMediaType(),
                    response.getHeaders(), resp.getOutputStream());
        }
    }

    private OutboundResponse from(Throwable throwable) {
        ExceptionMapper mapper = providers.getExceptionMapper(throwable.getClass());
        return (OutboundResponse) mapper.toResponse(throwable);
    }
}

```

测试为：

```
package geektime.tdd.rest;
import jakarta.servlet.Servlet;
import jakarta.ws.rs.WebApplicationException;
import jakarta.ws.rs.container.ResourceContext;
import jakarta.ws.rs.core.*;
import jakarta.ws.rs.ext.MessageBodyWriter;
import jakarta.ws.rs.ext.Providers;
import jakarta.ws.rs.ext.RuntimeDelegate;
import org.junit.jupiter.api.*;
import org.mockito.Mockito;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.lang.annotation.Annotation;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.reflect.Method;
import java.lang.reflect.Type;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.function.Consumer;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;
public class ResourceServletTest extends ServletTest {
    private Runtime runtime;
    private ResourceRouter router;
    private ResourceContext resourceContext;
    private Providers providers;
    private RuntimeDelegate delegate;
    @Override
    protected Servlet getServlet() {
        runtime = Mockito.mock(Runtime.class);
        router = Mockito.mock(ResourceRouter.class);
        resourceContext = Mockito.mock(ResourceContext.class);
        providers = Mockito.mock(Providers.class);
        when(runtime.getResourceRouter()).thenReturn(router);
        when(runtime.createResourceContext(any(), any())).thenReturn(resourceContext);
        when(runtime.getProviders()).thenReturn(providers);
        return new ResourceServlet(runtime);
    }
    @BeforeEach
    public void before() {
        delegate = Mockito.mock(RuntimeDelegate.class);
        RuntimeDelegate.setInstance(delegate);
        when(delegate.createHeaderDelegate(eq(NewCookie.class))).thenReturn(new RuntimeDelegate.HeaderDelegate<>() {
            @Override
            public NewCookie fromString(String value) {
                return null;
            }
            @Override
            public String toString(NewCookie value) {
                return value.getName() + "=" + value.getValue();
            }
        });
    }
    @Nested
    class RespondForOutboundResponse {
        @Test
        public void should_use_http_headers_from_response() throws Exception {
            response().headers("Set-Cookie", new NewCookie.Builder("SESSION_ID").value("session").build(),
                    new NewCookie.Builder("USER_ID").value("user").build()).returnFrom(router);
            HttpResponse<String> httpResponse = get("/test");
            assertArrayEquals(new String[]{"SESSION_ID=session", "USER_ID=user"}, httpResponse.headers().allValues("Set-Cookie").toArray(String[]::new));
        }
        @Test
        public void should_write_entity_to_http_response_using_message_body_writer() throws Exception {
            response().entity(new GenericEntity<>("entity", String.class), new Annotation[0]).returnFrom(router);
            HttpResponse<String> httpResponse = get("/test");
            assertEquals("entity", httpResponse.body());
        }

        @Test
        public void should_not_call_message_body_writer_if_entity_is_null() throws Exception {
            response().entity(null, new Annotation[0]).returnFrom(router);
            HttpResponse<String> httpResponse = get("/test");
            assertEquals(Response.Status.OK.getStatusCode(), httpResponse.statusCode());
            assertEquals("", httpResponse.body());
        }
        @Test
        public void should_use_status_from_response() throws Exception {
            response().status(Response.Status.NOT_MODIFIED).returnFrom(router);
            HttpResponse<String> httpResponse = get("/test");
            assertEquals(Response.Status.NOT_MODIFIED.getStatusCode(), httpResponse.statusCode());
        }
    }
    @TestFactory
    public List<DynamicTest> RespondWhenExtensionMissing() {
        List<DynamicTest> tests = new ArrayList<>();
        Map<String, org.junit.jupiter.api.function.Executable> extensions =
                Map.of("MessageBodyWriter", () -> response().entity(new GenericEntity<>(1, Integer.class), new Annotation[0]).returnFrom(router),
                        "HeaderDelegate", () -> response().headers(HttpHeaders.DATE, new Date()).returnFrom(router),
                        "ExceptionMapper", () -> when(router.dispatch(any(), eq(resourceContext))).thenThrow(IllegalStateException.class));
        for (String name : extensions.keySet())
            tests.add(DynamicTest.dynamicTest(name + " not found", () -> {
                extensions.get(name).execute();
                when(providers.getExceptionMapper(eq(NullPointerException.class))).thenReturn(e -> response().status(Response.Status.INTERNAL_SERVER_ERROR).build());
                HttpResponse<String> httpResponse = get("/test");
                assertEquals(Response.Status.INTERNAL_SERVER_ERROR.getStatusCode(), httpResponse.statusCode());
            }));
        return tests;
    }
    @TestFactory
    public List<DynamicTest> RespondForException() {
        List<DynamicTest> tests = new ArrayList<>();
        Map<String, Consumer<Consumer<RuntimeException>>> exceptions = Map.of("Other Exception", this::otherExceptionThrownFrom,
                "WebApplicationException", this::webApplicationExceptionThrownFrom);
        for (Map.Entry<String, Consumer<RuntimeException>> caller : getCallers().entrySet())
            for (Map.Entry<String, Consumer<Consumer<RuntimeException>>> exceptionThrownFrom : exceptions.entrySet())
                tests.add(DynamicTest.dynamicTest(caller.getKey() + " throws " + exceptionThrownFrom.getKey(),
                        () -> exceptionThrownFrom.getValue().accept(caller.getValue())));
        return tests;
    }
    private void webApplicationExceptionThrownFrom(Consumer<RuntimeException> caller) {
        RuntimeException exception = new WebApplicationException(response().status(Response.Status.FORBIDDEN).build());
        caller.accept(exception);
        HttpResponse<String> httpResponse = get("/test");
        assertEquals(Response.Status.FORBIDDEN.getStatusCode(), httpResponse.statusCode());
    }
    private void otherExceptionThrownFrom(Consumer<RuntimeException> caller) {
        RuntimeException exception = new IllegalArgumentException();
        caller.accept(exception);
        when(providers.getExceptionMapper(eq(IllegalArgumentException.class))).thenReturn(e -> response().status(Response.Status.FORBIDDEN).build());
        HttpResponse<String> httpResponse = get("/test");
        assertEquals(Response.Status.FORBIDDEN.getStatusCode(), httpResponse.statusCode());
    }
    @Retention(RetentionPolicy.RUNTIME)
    @interface ExceptionThrownFrom {
    }
    @ExceptionThrownFrom
    private void providers_getExceptionMapper(RuntimeException exception) {
        when(router.dispatch(any(), eq(resourceContext))).thenThrow(RuntimeException.class);
        when(providers.getExceptionMapper(eq(RuntimeException.class))).thenThrow(exception);
    }
    @ExceptionThrownFrom
    private void runtimeDelegate_createHeaderDelegate(RuntimeException exception) {
        response().headers(HttpHeaders.CONTENT_TYPE, MediaType.TEXT_PLAIN_TYPE).returnFrom(router);
        when(delegate.createHeaderDelegate(eq(MediaType.class))).thenThrow(exception);
    }
    @ExceptionThrownFrom
    private void exceptionMapper_toResponse(RuntimeException exception) {
        when(router.dispatch(any(), eq(resourceContext))).thenThrow(RuntimeException.class);
        when(providers.getExceptionMapper(eq(RuntimeException.class))).thenThrow(exception);
    }
    @ExceptionThrownFrom
    private void headerDelegate_toString(RuntimeException exception) {
        response().headers(HttpHeaders.CONTENT_TYPE, MediaType.TEXT_PLAIN_TYPE).returnFrom(router);
        when(delegate.createHeaderDelegate(eq(MediaType.class))).thenReturn(new RuntimeDelegate.HeaderDelegate<MediaType>() {
            @Override
            public MediaType fromString(String value) {
                return null;
            }
            @Override
            public String toString(MediaType value) {
                throw exception;
            }
        });
    }
    @ExceptionThrownFrom
    private void providers_getMessageBodyWriter(RuntimeException exception) {
        response().entity(new GenericEntity<>(2.5, Double.class), new Annotation[0]).returnFrom(router);
        when(providers.getMessageBodyWriter(eq(Double.class), eq(Double.class), eq(new Annotation[0]), eq(MediaType.TEXT_PLAIN_TYPE)))
                .thenThrow(exception);
    }
    @ExceptionThrownFrom
    private void messageBodyWriter_writeTo(RuntimeException exception) {
        response().entity(new GenericEntity<>(2.5, Double.class), new Annotation[0]).returnFrom(router);
        when(providers.getMessageBodyWriter(eq(Double.class), eq(Double.class), eq(new Annotation[0]), eq(MediaType.TEXT_PLAIN_TYPE)))
                .thenReturn(new MessageBodyWriter<Double>() {
                    @Override
                    public boolean isWriteable(Class<?> type, Type genericType, Annotation[] annotations, MediaType mediaType) {
                        return false;
                    }
                    @Override
                    public void writeTo(Double aDouble, Class<?> type, Type genericType, Annotation[] annotations, MediaType mediaType, MultivaluedMap<String, Object> httpHeaders, OutputStream entityStream) throws IOException, WebApplicationException {
                        throw exception;
                    }
                });
    }
    @ExceptionThrownFrom
    public void resourceRouter_dispatch(RuntimeException exception) {
        when(router.dispatch(any(), eq(resourceContext))).thenThrow(exception);
    }
    private Map<String, Consumer<RuntimeException>> getCallers() {
        Map<String, Consumer<RuntimeException>> callers = new HashMap<>();
        for (Method method : Arrays.stream(this.getClass().getDeclaredMethods()).filter(m -> m.isAnnotationPresent(ExceptionThrownFrom.class)).toList()) {
            String name = method.getName();
            String callerName = name.substring(0, 1).toUpperCase() + name.substring(1).replace('_', '.');
            callers.put(callerName, e -> {
                try {
                    method.invoke(this, e);
                } catch (Exception ex) {
                    throw new RuntimeException(ex);
                }
            });
        }
        return callers;
    }
    private OutboundResponseBuilder response() {
        return new OutboundResponseBuilder();
    }
    class OutboundResponseBuilder {
        Response.Status status = Response.Status.OK;
        MultivaluedMap<String, Object> headers = new MultivaluedHashMap<>();
        GenericEntity<Object> entity = new GenericEntity<>("entity", String.class);
        Annotation[] annotations = new Annotation[0];
        MediaType mediaType = MediaType.TEXT_PLAIN_TYPE;
        public OutboundResponseBuilder status(Response.Status status) {
            this.status = status;
            return this;
        }
        public OutboundResponseBuilder headers(String name, Object... values) {
            headers.addAll(name, values);
            return this;
        }
        public OutboundResponseBuilder entity(GenericEntity<Object> entity, Annotation[] annotations) {
            this.entity = entity;
            this.annotations = annotations;
            return this;
        }
        void returnFrom(ResourceRouter router) {
            build(response -> when(router.dispatch(any(), eq(resourceContext))).thenReturn(response));
        }
        void build(Consumer<OutboundResponse> consumer) {
            consumer.accept(build());
        }
        OutboundResponse build() {
            OutboundResponse response = Mockito.mock(OutboundResponse.class);
            when(response.getStatus()).thenReturn(status.getStatusCode());
            when(response.getStatusInfo()).thenReturn(status);
            when(response.getHeaders()).thenReturn(headers);
            when(response.getGenericEntity()).thenReturn(entity);
            when(response.getAnnotations()).thenReturn(annotations);
            when(response.getMediaType()).thenReturn(mediaType);
            stubMessageBodyWriter();
            return response;
        }
        private void stubMessageBodyWriter() {
            when(providers.getMessageBodyWriter(eq(String.class), eq(String.class), same(annotations), eq(mediaType)))
                    .thenReturn(new MessageBodyWriter<>() {
                        @Override
                        public boolean isWriteable(Class<?> type, Type genericType, Annotation[] annotations, MediaType mediaType) {
                            return false;
                        }
                        @Override
                        public void writeTo(String s, Class<?> type, Type genericType, Annotation[] annotations, MediaType mediaType, MultivaluedMap<String, Object> httpHeaders, OutputStream entityStream) throws IOException, WebApplicationException {
                            PrintWriter writer = new PrintWriter(entityStream);
                            writer.write(s);
                            writer.flush();
                        }
                    });
        }
    }
}

```

## 目前的代码与测试

下面让我们回顾一下目前的代码与测试：

## 思考题

在进入下节课之前，希望你能认真思考如下两个问题。

1. 伦敦学派与经典学派的差异是什么？
2. 伦敦学派与经典学派的这些差异，在编码过程中，对我们的思考方法带来了什么影响？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！