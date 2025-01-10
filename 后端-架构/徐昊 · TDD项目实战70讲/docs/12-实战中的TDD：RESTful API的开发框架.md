你好，我是徐昊。从今天开始，让我们进入实战中的TDD环节。也就是使用TDD的方式，去实现我们工作中常用的技术框架。

之所以选择常用的技术框架，而不虚构某个业务系统，主要是因为TDD的难点首先在于理解需求，并将需求分解为功能点。虚构的业务系统，难以详尽描述所有的业务假设（功能上、组织上、运营方式上等），不利于你跟随题目自行练习。而使用常用的技术框架，由于你对于大体的功能及其所解决的问题，已经有所了解。我也可以避免无谓的啰嗦。

## RESTful API的开发框架

第一个场景是支撑RESTful API的开发框架，你可以将它想象成mini版本的Dropwizard或者Spring MVC。功能范围包含一个依赖注入容器（Dependency Injection Container/IoC Container）和一个支持RESTful API构建的Web框架。

我们会以Jakarta EE中的Jakarta Dependency Injection和Jakarta RESTful Web Services 为主要功能参考，并对其适当简化，以完成我们的目标。

当我们完成全部功能之后，可以通过类似以下的代码实现RESTful API：

```
package geektime.tdd.resources;

import geektime.tdd.model.Student;
import geektime.tdd.model.StudentRepository;
import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.List;

@Path("/students")
public class StudentsResource {

    private StudentRepository repository;

    @Inject
    public StudentsResource(StudentRepository repository) {
        this.repository = repository;
    }

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Student> all() {
        return repository.all();
    }

    @GET
    @Path("{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response findById(@PathParam("id") long id) {
        return repository.findById(id).map(Response::ok)
                .orElse(Response.status(Response.Status.NOT_FOUND)).build();
    }
}

```

## 依赖注入容器的大致功能

首先让我们从依赖注入容器开始。关于依赖注入的来龙去脉可以参看Martin Fowler在2004年写的文章 [《](https://martinfowler.com/articles/injection.html) [IoC容器与依赖注入模式](https://martinfowler.com/articles/injection.html) [》](https://martinfowler.com/articles/injection.html)。

Jakarta Dependency Injection的功能主要分为三部分：组件的构造、依赖的选择以及生命周期控制。详细说明如视频中所示：

Jakarta Dependency Injection中没有规定而又常用的部分有：配置容器如何配置、容器层级结构以及生命周期回调。详细说明如视频中所示：

## 思考题

那么以此为基础，要如何分解功能点呢？请你自行练习。下节课，我会给出我做的分解列表。

欢迎把你的思考和想法分享在留言区，也欢迎你扫描详情页的二维码加入读者交流群。我们下节课再见！