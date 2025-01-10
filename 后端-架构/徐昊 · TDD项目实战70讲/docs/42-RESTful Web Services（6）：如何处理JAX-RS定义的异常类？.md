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
    - 如果找不到对应的MessageBody，则返回500族错误
  - 当资源方法抛出异常时，根据异常影响Http请求
    - 如果抛出WebApplicationException，且response不为null，则使用response响应Http
    - 如果抛出WebApplicationException，而response为null，则通过异常的具体类型查找ExceptionMapper，生产response响应Http请求
    - 如果抛出的不是WebApplicationException，则通过异常的具体类型查找ExceptionMapper，生产response响应Http请求
- RuntimeDelegate
  - 为MediaType提供HeaderDelegate
  - 为CacheControl提供HeaderDelegate
  - 为Cookie提供HeaderDelegates
  - 为EntityTag提供HeaderDelegate
  - 为Link提供HeaderDelegate
  - 为NewCookie提供HeaderDelegate
  - 为Date提供HeaderDelegate

代码为：

```
package geektime.tdd.rest;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.ws.rs.core.GenericEntity;
import jakarta.ws.rs.core.MultivaluedMap;
import jakarta.ws.rs.ext.MessageBodyWriter;
import jakarta.ws.rs.ext.Providers;
import jakarta.ws.rs.ext.RuntimeDelegate;
import java.io.IOException;

public class ResourceServlet extends HttpServlet {

    private Runtime runtime;

    public ResourceServlet(Runtime runtime) {
        this.runtime = runtime;
    }

    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        ResourceRouter router = runtime.getResourceRouter();
        Providers providers = runtime.getProviders();

        OutboundResponse response = router.dispatch(req, runtime.createResourceContext(req, resp));

        resp.setStatus(response.getStatus());

        MultivaluedMap<String, Object> headers = response.getHeaders();
        for (String name : headers.keySet())
            for (Object value : headers.get(name)) {
                RuntimeDelegate.HeaderDelegate headerDelegate = RuntimeDelegate.getInstance().createHeaderDelegate(value.getClass());
                resp.addHeader(name, headerDelegate.toString(value));
            }

        GenericEntity entity = response.getGenericEntity();
        MessageBodyWriter writer = providers.getMessageBodyWriter(entity.getRawType(), entity.getType(), response.getAnnotations(), response.getMediaType());
        writer.writeTo(entity.getEntity(), entity.getRawType(), entity.getType(), response.getAnnotations(), response.getMediaType(),
                response.getHeaders(), resp.getOutputStream());
    }
}

```

## 视频演示

下面让我们继续：

## 思考题

在进入下节课之前，希望你能认真思考如下两个问题。

1. 目前的Sad Path任务是否足够？还有哪些Sad Path的情况？
2. 在这节课的学习中，你最大的收获是什么？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！