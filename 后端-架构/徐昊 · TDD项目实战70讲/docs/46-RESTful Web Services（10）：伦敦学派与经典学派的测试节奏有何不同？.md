你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

目前我们的架构愿景如下：

![](https://static001.geekbang.org/resource/image/ed/2e/ed95e0629105b3fe661590be6ab4af2e.jpg?wh=2284x1285)

![](https://static001.geekbang.org/resource/image/aa/56/aacdc2230e337d593308c0184b799956.jpg?wh=2284x1285)

在继续拆分不同模块的任务之前，我们先回顾一下伦敦学派的做法：

- 按照功能需求与架构愿景，划分对象的角色和职责；
- 根据角色与职责，明确对象之间的交互；
- 按照调用栈（Call Stack）的顺序，自外向内依次实现不同的对象；
- 在实现的过程中，依照交互关系，使用测试替身替换所有与被实现对象直接关联的对象；
- 直到所有对象全部实现完成。

到目前为止，我们完成了第一层调用栈的测试。也就是以ResourceServlet为核心，测试驱动地实现了它与其他组件之间的交互。因为大量地使用测试替身（主要是Stub），我们实际上围绕着ResourceServlet构建了一个抽象层。

如果我们继续沿着调用栈向内测试驱动，那么实际上就是 **为之前构建的抽象层提供了具体实现**。因而，伦敦学派的过程就是 **一个从抽象到具体的测试驱动的过程**。这也是为什么伦敦学派不惮于大量使用测试替身（甚至是Mock）： **具体实现是易变的，抽象是稳定的，因为它提炼了核心而忽略了细节**。

如果抽象层构建合理，那么它就是稳定且不易改变的。重构和代码改写通常发生在实现层，合理的抽象可以屏蔽这些改变对于外界的影响。那么使用行为验证、mock、单元测试，也不会阻碍重构的进行。而随着调用栈向内，逐渐从抽象层走到具体实现的时候，具体的模块就不会再依赖额外的组件，那么 **单元测试自然变成状态验证的单元级别功能测试**。

伦敦学派与经典学派具有完全不同的测试节奏。经典学派是从功能入手，完成功能之后，再通过重构做抽象与提炼。而伦敦学派则是从抽象入手，先构建一个 **抽象的机制**（Abstraction Mechanism），再逐步具化抽象机制中的组件。

因而，伦敦学派的难点有两个：在调用栈外层的时候，如何构建足够好的抽象层，以屏蔽具体实现变化带来的影响；逐步深入调用栈时，如何选择恰当的抽象层级。过多的抽象会 **不断加深调用栈**，让代码变得细碎且难理解。

在前面的课程中，我们展示了如何构建外层的抽象：通过Spike消除不确定性，从中提取架构愿景，并转化为抽象的接口。换句话说，我们使用了 **不严格的经典学派（没有大量的测试，架构愿景提取代替了测试）**，构建了伦敦学派的起点。

## 继续分解任务

正如我在上节课中讲解过的，目前的代码具有相当抽象的程度：

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

接下来，就要看我们如何继续分解任务了。目前的任务列表为：

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

我们需要把抽象层中其他使用到的组件也加入到任务列表当中，以及目前已知的任务列表中：

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
  - 可按照不同的Status生成Resposne
- OutboundResponse

- ResourceDispatcher
  - 将Resource Method的返回值包装为Response对象
- Providers
  - 可获取MessageBodyWriter
  - 可获取ExceptionMapper
- Runtimes
  - 可获取ResourceDispatcher
  - 可获取Providers
- MessageBodyWriter

- ExceptionMapper
  - 需要提供默认的ExceptionMapper

可以看到，列表中包含了抽象层中所有的组件，以及在最外层交互和测试的过程中识别的功能上下文，比如ResourceDispatcher按照Resource Method返回值来包装Response对象。这个时候，将要如何继续分解任务呢？

一个简单的考量是，能不能直接进入 **经典模式** 继续开发。如果可以，比如Runtimes、Providers、OutboundResponseBuilder等，就直接分解任务。如果不能，比如Resource Dispatcher，那么可以继续通过Spike消除不确定性，再一层抽象。

## 思考题

在进入下节课之前，希望你能完成这个作业：请根据你的理解，继续拆分任务，并将拆分好的任务分享在留言区。

相信经过你的思考与实操，学习效果会更好！我们下节课再见！