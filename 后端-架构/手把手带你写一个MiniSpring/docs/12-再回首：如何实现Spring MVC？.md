你好，我是郭屹。

恭喜你学完MiniSpring的第二部分——MVC了。你是不是跟着我的脚步自己也实现了一个MVC呢？如果已经完成了，欢迎你把你的实现代码放到评论区，我们一起交流讨论。

为了让你更好地掌握这部分内容，我们来对这一整章做一个重点回顾。

### MVC重点回顾

MVC是Spring框架的核心组成部分之一，负责实现一个Web应用程序的模型视图控制器模式。Spring框架提供了丰富的组件和工具，而MVC负责处理一个Web应用程序中的核心过程，例如请求处理、数据转换、模板渲染和视图管理等。而MVC和Spring的结合，就像是车与引擎的结合一样，给Web应用程序提供了强大而且可靠的性能和灵活性，让我们能够快速、方便地搭建高性能、可靠的Web应用程序。

因为Spring是Java实现的，也因为发明人Rod Johnson先生自己是Java团队Servlet规范的专家组成员，所以很自然，他的MVC的实现是基于Servlet的。利用Servlet的机制，把这种功效发挥到了极致，快速构造了完整的Web程序结构，让我们大开眼界。

### 那我们在课程中是怎么实现MVC的呢？

首先我们利用Servlet机制，用一个单一的Servlet拦截所有请求，由它来分派任务，这样实现了原始的MVC结构。然后呢，我们把MVC和IoC结合在一起，在Servlet容器启动的时候，给上下文环境里注入IoC容器，使得在Servlet里可以访问到IoC容器里的Bean。

之后我们进一步解耦MVC结构，独立出请求处理器，还用一个简洁统一的注解方式，把Web请求方便地定位到后台处理的类和方法里，实现Spring的RequestHandler。

在前后台打通的时候，实现数据参数的自动转换，也就是说先把Web请求的传入参数，自动地从文本转换成对象，实现数据绑定功能。对于返回数据，也自动根据用户需求进行格式化转换，这样实现了Spring里面的data binder和data conversion。最后回到前端View，如果有前端引擎，在Spring中引用，把数据自动渲染到前端。

我们可以利用Servlet机制、MVC结构、IoC容器、RequestHandler和数据绑定等功能，确保前后台的有效沟通和良好的交互体验，实现一个高效可靠的Web应用程序。你学会了吗？

最后，我们再来看一下这一章的几道思考题，我在文稿里都给出了参考答案。我建议你也可以把你的思考分享在留言区，看看自己的思路是不是对的。题目我也就不一道一道地说了，你在做完思考题之后，自己来对比。

### 07｜原始MVC：如何通过单一的Servlet拦截请求分派任务？

#### 思考题

我们在MVC中也使用了Bean这个概念，它跟我们以前章节中的Bean是什么关系？

#### 参考答案

MVC（Model-View-Controller）和IoC（Inversion of Control）是两个不同的设计模式，它们都使用“Bean”这个概念，但是在不同的层级和实现方式上有所不同。

- 在MVC中，“Bean”通常指代模型对象。模型对象是业务逻辑层的核心，用于实现数据访问和业务逻辑处理等功能。在MVC中，模型对象通常是由控制器（Controller）创建并向视图（View）传递的。
- 在IoC中，“Bean”指代由IoC容器管理的对象。IoC容器负责创建及管理应用程序中的所有Bean对象。通过IoC容器，应用程序能够实现“控制反转”，即由IoC容器统一管理和调度应用程序中的各个组件。在IoC中，Bean是由IoC容器创建、初始化、配置和装配的。

因此，尽管MVC和IoC都使用了“Bean”这个概念，但它们的含义及在系统中的作用是不同的。MVC中的Bean一般是Web相关的业务逻辑，IoC中的Bean可能是一些更加基础性的逻辑。从MVC中可以访问到IoC容器中的Bean。

### 08｜整合IoC和MVC：如何在Web环境中启动IoC容器？

#### 思考题

我们看到从Dispatcher里可以访问WebApplicationContext里管理的Bean，那通过 WebApplicationContext 可以访问Dispatcher内管理的Bean吗？

#### 参考答案

不可以。

Servlet容器启动的时候，按照时序，是先启动Listener，在Listener的初始化过程中创建IoC容器，放到ServletContext里，这就是WAC。这之后再初始化的Servlet。所以Dispatcher可以访问到WAC，但是WAC访问不到DispatcherServlet，这个是单向的。

### 09｜分解Dispatcher：如何把专门的事情交给专门的部件去做？

#### 思考题

目前，我们只支持了GET方法，你能不能尝试自己增加POST方法。想一想，需要改变现有的程序结构吗？

#### 参考答案

增加POST方法支持不需要改变现有程序结构。因为我们的DispatcherServlet现在统一用service()方法处理所有请求，之后调用doDispatch()方法，最后通过this.handlerMapping.getHandler()找到需要调用的方法。无论对于GET还是POST，都是同样的流程，统一由handlerMapping来区分不同的调用方法。

所以如果要区分GET和POST，则可以在RequestMapping注解上增加METHOD属性，表示GET还是POST，然后handlerMapping.getHandler()中根据GET和POST匹配实际的调用方法。

### 10｜数据绑定: 如何自动转换传入的参数？

#### 思考题

我们现在的实现是把request里面的参数值，按照内部的次序隐含地自动转成后台调用方法参数对象中的某个属性值，那么可不可以使用一个手段，让程序员手动指定某个调用方法的参数跟哪个request参数进行绑定呢？

#### 参考答案

参数绑定的处理，是在RequestMappingHandlerAdatper的invokeHandlerMethod()方法中处理的，它拿到调用方法的所有参数，一个参数一个参数进行绑定： `WebDataBinder wdb = binderFactory.createBinder(request, methodParamObj, methodParameter.getName());`。所以我们在这里可以考虑给参数增加一个注解@RequestParam。对于带有这个注解的参数，就不是隐含地按照参数名去匹配，而是按照指定的名字去request中匹配。

### 11｜ModelAndView ：如何将处理结果返回到前端？

现在返回的数据只支持Date、Number和String三种类型，如何扩展到更多的数据类型？现在也只支持JSP，如何扩展到别的前端？

#### 参考答案

返回数据的格式处理是通过ObjectMapper来实现的。我们有一个默认实现DefaultObjectMapper，只要在它的writeValuesAsString()里判断数据类型的时候，增加别的类型就可以了。

对于JSP之外的View，我们现在的结构是可扩展的。只要自己另外实现一个View和一个View resolver即可。