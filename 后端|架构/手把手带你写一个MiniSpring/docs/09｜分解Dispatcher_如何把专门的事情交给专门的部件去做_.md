你好，我是郭屹。今天我们继续手写MiniSpring。

经过上节课的工作，我们已经实现了IoC与MVC的结合，还定义了Dispatcher与WebApplicationContext两个相对独立又互相关联的结构。

这节课我们计划在已有的ApplicationConfigWebApplicationContext 和DispatcherServlet基础上，把功能做进一步地分解，让Dispatcher只负责解析request请求，用Context 专门用来管理各个Bean。

## 两级ApplicationContext

按照通行的Web分层体系，一个程序它在结构上会有Controller和Service 两层。在我们的程序中，Controller由DispatcherServlet负责启动，Service由Listener负责启动。我们计划把这两部分所对应的容器进行进一步地切割，拆分为XmlWebApplicationContext和AnnotationConfigWebApplicationContext。

首先在 DispatcherServlet 这个类里，增加一个对WebApplicationContext 的引用，命名为parentApplicationContext。这样，当前这个类里就有了两个对WebApplicationContext 的引用。

```java
private WebApplicationContext webApplicationContext;
private WebApplicationContext parentApplicationContext;

```

新增parentApplicationContext 的目的是，把Listener启动的上下文和DispatcherServlet启动的上下文两者区分开来。按照时序关系，Listener启动在前，对应的上下文我们把它叫作parentApplicationContext。

我们调整一下init() 方法。

```java
public void init(ServletConfig config) throws ServletException {
    super.init(config);
    this.parentApplicationContext = (WebApplicationContext)
this.getServletContext().getAttribute(WebApplicationContext.ROOT_WEB_APPLICATION
_CONTEXT_ATTRIBUTE);
    sContextConfigLocation =
config.getInitParameter("contextConfigLocation");

    URL xmlPath = null;
	try {
		xmlPath = this.getServletContext().getResource(sContextConfigLocation);
	} catch (MalformedURLException e) {
		e.printStackTrace();
	}
    this.packageNames = XmlScanComponentHelper.getNodeValue(xmlPath);
    this.webApplicationContext = new
AnnotationConfigWebApplicationContext(sContextConfigLocation,
this.parentApplicationContext);
    Refresh();
}

```

初始化的时候先从ServletContext里拿属性WebApplicationContext.ROOT\_WEB\_APPLICATION\_CONTEXT\_ATTRIBUTE，得到的是前一步Listener存放在这里的那个parentApplicationContext。然后通过contextConfigLocation配置文件，创建一个新的WebApplicationContext。

从上述代码，我们可以发现，里面构建了一个AnnotationConfigWebApplicationContext对象，这个对象的构造函数需要两个参数，一个是配置文件路径，另一个是父上下文。但以前AnnotationConfigWebApplicationContext只有一个参数为String的构造函数。所以这里我们需要扩展改造一下，把DispatcherServlet里一部分和扫描包相关的代码移到AnnotationConfigWebApplicationContext里。你可以看一下修改后的AnnotationConfigWebApplicationContext代码。

```java
package com.minis.web;

import java.io.File;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import javax.servlet.ServletContext;
import com.minis.beans.BeansException;
import com.minis.beans.factory.annotation.AutowiredAnnotationBeanPostProcessor;
import com.minis.beans.factory.config.BeanDefinition;
import com.minis.beans.factory.config.BeanFactoryPostProcessor;
import com.minis.beans.factory.config.ConfigurableListableBeanFactory;
import com.minis.beans.factory.support.DefaultListableBeanFactory;
import com.minis.context.AbstractApplicationContext;
import com.minis.context.ApplicationEvent;
import com.minis.context.ApplicationEventPublisher;
import com.minis.context.ApplicationListener;
import com.minis.context.SimpleApplicationEventPublisher;

public class AnnotationConfigWebApplicationContext
					extends AbstractApplicationContext implements WebApplicationContext{
	private WebApplicationContext parentApplicationContext;
	private ServletContext servletContext;
	DefaultListableBeanFactory beanFactory;
	private final List<BeanFactoryPostProcessor> beanFactoryPostProcessors =
			new ArrayList<BeanFactoryPostProcessor>();

	public AnnotationConfigWebApplicationContext(String fileName) {
		this(fileName, null);
	}
	public AnnotationConfigWebApplicationContext(String fileName, WebApplicationContext parentApplicationContext) {
		this.parentApplicationContext = parentApplicationContext;
		this.servletContext = this.parentApplicationContext.getServletContext();
        URL xmlPath = null;
		try {
			xmlPath = this.getServletContext().getResource(fileName);
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}

        List<String> packageNames = XmlScanComponentHelper.getNodeValue(xmlPath);
        List<String> controllerNames = scanPackages(packageNames);
    	DefaultListableBeanFactory bf = new DefaultListableBeanFactory();
        this.beanFactory = bf;
        this.beanFactory.setParent(this.parentApplicationContext.getBeanFactory());
        loadBeanDefinitions(controllerNames);

        if (true) {
            try {
				refresh();
			} catch (Exception e) {
				e.printStackTrace();
			}
        }
	}
	public void loadBeanDefinitions(List<String> controllerNames) {
        for (String controller : controllerNames) {
            String beanID=controller;
            String beanClassName=controller;
            BeanDefinition beanDefinition=new BeanDefinition(beanID,beanClassName);
            this.beanFactory.registerBeanDefinition(beanID,beanDefinition);
        }
	}
    private List<String> scanPackages(List<String> packages) {
    	List<String> tempControllerNames = new ArrayList<>();
    	for (String packageName : packages) {
    		tempControllerNames.addAll(scanPackage(packageName));
    	}
    	return tempControllerNames;
    }
    private List<String> scanPackage(String packageName) {
    	List<String> tempControllerNames = new ArrayList<>();
        URL url  =this.getClass().getClassLoader().getResource("/"+packageName.replaceAll("\\.", "/"));
        File dir = new File(url.getFile());
        for (File file : dir.listFiles()) {
            if(file.isDirectory()){
            	scanPackage(packageName+"."+file.getName());
            }else{
                String controllerName = packageName +"." +file.getName().replace(".class", "");
                tempControllerNames.add(controllerName);
            }
        }
        return tempControllerNames;
    }
	public void setParent(WebApplicationContext parentApplicationContext) {
		this.parentApplicationContext = parentApplicationContext;
		this.beanFactory.setParent(this.parentApplicationContext.getBeanFactory());
	}
	public ServletContext getServletContext() {
		return this.servletContext;
	}
	public void setServletContext(ServletContext servletContext) {
		this.servletContext = servletContext;
	}
	public void publishEvent(ApplicationEvent event) {
		this.getApplicationEventPublisher().publishEvent(event);
	}
	public void addApplicationListener(ApplicationListener listener) {
		this.getApplicationEventPublisher().addApplicationListener(listener);
	}
	public void registerListeners() {
		ApplicationListener listener = new ApplicationListener();
		this.getApplicationEventPublisher().addApplicationListener(listener);
	}
	public void initApplicationEventPublisher() {
		ApplicationEventPublisher aep = new SimpleApplicationEventPublisher();
		this.setApplicationEventPublisher(aep);
	}
	public void postProcessBeanFactory(ConfigurableListableBeanFactory bf) {
	}
	public void registerBeanPostProcessors(ConfigurableListableBeanFactory bf) {
		this.beanFactory.addBeanPostProcessor(new AutowiredAnnotationBeanPostProcessor());
	}
	public void onRefresh() {
		this.beanFactory.refresh();
	}
	public void finishRefresh() {
	}
	public ConfigurableListableBeanFactory getBeanFactory() throws IllegalStateException {
		return this.beanFactory;
	}
}

```

这段代码的核心是扩充原有的构造方法。通过下面两行代码得到parentApplicationContext和servletContext的引用。

```plain
 this.parentApplicationContext = parentApplicationContext;
 this.servletContext = this.parentApplicationContext.getServletContext();

```

为了兼容原有构造方法，在只有1个参数的时候，给WebApplicationContext传入了一个null。可以看到，修改后的AnnotationConfigWebApplicationContext继承自抽象类AbstractApplicationContext，所以也具备了上下文的通用功能，例如注册监听器、发布事件等。

其次是改造 DefaultListableBeanFactory，因为AnnotationConfigWebApplicationContext里调用了DefaultListableBeanFactory的setParent方法，所以我们需要提供相应的实现方法，你可以看一下相关代码。

```java
    ConfigurableListableBeanFactory parentBeanFactory;

    public void setParent(ConfigurableListableBeanFactory beanFactory) {
        this.parentBeanFactory = beanFactory;
    }

```

接下来我们还要改造XmlWebApplicationContext，在继承ClassPathXmlApplicationContext的基础上实现WebApplicationContext接口，基本上我们可以参考AnnotationConfigWebApplicationContext来实现。

```java
package com.minis.web;

import javax.servlet.ServletContext;
import com.minis.context.ClassPathXmlApplicationContext;

public class XmlWebApplicationContext
					extends ClassPathXmlApplicationContext implements WebApplicationContext{
	private ServletContext servletContext;

	public XmlWebApplicationContext(String fileName) {
		super(fileName);
	}

	public ServletContext getServletContext() {
		return this.servletContext;
	}
	public void setServletContext(ServletContext servletContext) {
		this.servletContext = servletContext;
	}
}

```

到这里，我们就进一步拆解了DispatcherServlet，拆分出两级ApplicationContext，当然启动过程还是由Listener来负责。所以最后ContextLoaderListener初始化时是创建XmlWebApplicationContext对象。

```java
WebApplicationContext wac = new XmlWebApplicationContext(sContextLocation);

```

到这里，Web环境下的两个ApplicationContext都构建完毕了，WebApplicationContext持有对parentApplicationContext的单向引用。当调用getBean()获取Bean时，先从WebApplicationContext中获取，若为空则通过parentApplicationContext获取，你可以看一下代码。

```java
    public Object getBean(String beanName) throws BeansException {
        Object result = super.getBean(beanName);
        if (result == null) {
            result = this.parentBeanFactory.getBean(beanName);
        }
        return result;
    }

```

## 抽取调用方法

拆解的工作还要继续进行，基本的思路是将专业事情交给不同的专业部件来做，我们来看看还有哪些工作是可以分出来的。从代码可以看到现在doGet()方法是这样实现的。

```plain
	Method method = this.mappingMethods.get(sPath);
	obj = this.mappingObjs.get(sPath);
	objResult = method.invoke(obj);
	response.getWriter().append(objResult.toString());

```

这个程序就是简单地根据URL找到对应的方法和对象，然后通过反射调用方法，最后把方法执行的返回值写到response里。我们考虑把通过URL映射到某个实例方法的过程抽取出来，还要考虑把对方法的调用也单独抽取出来。仿照Spring框架，我们新增RequestMappingHandlerMapping与RequestMappingHandlerAdapter，分别对应这两个独立的部件。

首先将HandlerMapping与HandlerAdapter抽象出来，定义接口，然后基于接口来编程。

```java
package com.minis.web.servlet;

import javax.servlet.http.HttpServletRequest;

public interface HandlerMapping {
	HandlerMethod getHandler(HttpServletRequest request) throws Exception;
}

package com.minis.web.servlet;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public interface HandlerAdapter {
	void handle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception;
}

```

其中可以看到，HandlerMapping中定义的getHandler方法参数是http request，返回一个HandlerMethod对象，这个地方就是封装的这种映射关系。你可以看一下HandlerMethod对象的定义。

```java
package com.minis.web.servlet;

import java.lang.reflect.Method;

public class HandlerMethod {
	private  Object bean;
	private  Class<?> beanType;
	private  Method method;
	private  MethodParameter[] parameters;
	private  Class<?> returnType;
	private  String description;
	private  String className;
	private  String methodName;

	public HandlerMethod(Method method, Object obj) {
		this.setMethod(method);
		this.setBean(obj);
	}
	public Method getMethod() {
		return method;
	}
	public void setMethod(Method method) {
		this.method = method;
	}
	public Object getBean() {
		return bean;
	}
	public void setBean(Object bean) {
		this.bean = bean;
	}
}

```

接下来增加一个MappingRegistry类，这个类有三个属性：urlMappingNames、mappingObjs和mappingMethods，用来存储访问的URL名称与对应调用方法及Bean实例的关系。你可以看一下相关定义。

```java
package com.minis.web.servlet;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MappingRegistry {
    private List<String> urlMappingNames = new ArrayList<>();
    private Map<String,Object> mappingObjs = new HashMap<>();
    private Map<String,Method> mappingMethods = new HashMap<>();

	public List<String> getUrlMappingNames() {
		return urlMappingNames;
	}
	public void setUrlMappingNames(List<String> urlMappingNames) {
		this.urlMappingNames = urlMappingNames;
	}
	public Map<String,Object> getMappingObjs() {
		return mappingObjs;
	}
	public void setMappingObjs(Map<String,Object> mappingObjs) {
		this.mappingObjs = mappingObjs;
	}
	public Map<String,Method> getMappingMethods() {
		return mappingMethods;
	}
	public void setMappingMethods(Map<String,Method> mappingMethods) {
		this.mappingMethods = mappingMethods;
	}
}

```

通过上面的代码可以看出，这三个属性以前其实都已经存在了，是定义在DispatcherServlet里的，现在换一个位置，通过MappingRegistry这个单独的部件来存放和管理这个映射关系。

好了，有了这些准备之后，我们来看RequestMappingHandlerMapping的实现，它要实现HandlerMapping 接口，初始化过程就是遍历WAC中已经注册的所有的Bean，并处理带有@RequestMapping注解的类，使用mappingRegistry存储URL地址与方法和实例的映射关系。对外它要实现getHandler()方法，通过URL拿到method的调用。

相关源代码如下：

```java
package com.minis.web.servlet;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import javax.servlet.http.HttpServletRequest;
import com.minis.beans.BeansException;
import com.minis.web.RequestMapping;
import com.minis.web.WebApplicationContext;

public class RequestMappingHandlerMapping implements HandlerMapping{
    WebApplicationContext wac;
    private final MappingRegistry mappingRegistry = new MappingRegistry();
    public RequestMappingHandlerMapping(WebApplicationContext wac) {
        this.wac = wac;
        initMapping();
    }
    //建立URL与调用方法和实例的映射关系，存储在mappingRegistry中
    protected void initMapping() {
        Class<?> clz = null;
        Object obj = null;
        String[] controllerNames = this.wac.getBeanDefinitionNames();
        //扫描WAC中存放的所有bean
        for (String controllerName : controllerNames) {
            try {
                clz = Class.forName(controllerName);
                obj = this.wac.getBean(controllerName);
            } catch (Exception e) {
				e.printStackTrace();
			}
            Method[] methods = clz.getDeclaredMethods();
            if (methods != null) {
                //检查每一个方法声明
                for (Method method : methods) {
                    boolean isRequestMapping =
method.isAnnotationPresent(RequestMapping.class);
                    //如果该方法带有@RequestMapping注解,则建立映射关系
                    if (isRequestMapping) {
                        String methodName = method.getName();
                        String urlmapping =
method.getAnnotation(RequestMapping.class).value();

                        this.mappingRegistry.getUrlMappingNames().add(urlmapping);
                        this.mappingRegistry.getMappingObjs().put(urlmapping,
obj);
                        this.mappingRegistry.getMappingMethods().put(urlmapping,
method);
                    }
                }
            }
        }
    }

    //根据访问URL查找对应的调用方法
    public HandlerMethod getHandler(HttpServletRequest request) throws Exception
{
        String sPath = request.getServletPath();
		if (!this.mappingRegistry.getUrlMappingNames().contains(sPath)) {
			return null;
		}
        Method method = this.mappingRegistry.getMappingMethods().get(sPath);
        Object obj = this.mappingRegistry.getMappingObjs().get(sPath);
        HandlerMethod handlerMethod = new HandlerMethod(method, obj);
        return handlerMethod;
    }
}

```

这样我们就得到了独立的RequestMappingHandlerMapping部件，把以前写在DispatcherServlet里的代码移到这里来了。

接下来就轮到RequestMappingHandlerAdapter的实现了，它要实现HandlerAdapter接口，主要就是实现handle()方法，基本过程是接受前端传request、 response与handler，通过反射中的invoke调用方法并处理返回数据。

相关源代码如下：

```java
package com.minis.web.servlet;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import com.minis.web.WebApplicationContext;

public class RequestMappingHandlerAdapter implements HandlerAdapter {
	WebApplicationContext wac;

	public RequestMappingHandlerAdapter(WebApplicationContext wac) {
		this.wac = wac;
	}

	public void handle(HttpServletRequest request, HttpServletResponse response, Object handler)
			throws Exception {
		handleInternal(request, response, (HandlerMethod) handler);
	}
	private void handleInternal(HttpServletRequest request, HttpServletResponse response,
			HandlerMethod handler) {
		Method method = handler.getMethod();
		Object obj = handler.getBean();
		Object objResult = null;
		try {
			objResult = method.invoke(obj);
		} catch (Exception e) {
			e.printStackTrace();
		}
		try {
			response.getWriter().append(objResult.toString());
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}

```

重点看一下handleInternal()方法就知道了，这里就是简单地通过反射调用某个方法，然后把返回值写到response里。这些程序代码以前就有，只不过现在移到单独的这个部件中了。

最后需要修改DispatcherServlet中的实现，相关代码移走，放到了上面的两个部件中。所以在DispatcherServlet类中需要增加对HandlerMapping与HandlerAdapter的引用，在初始化方法refresh()中增加initHandlerMapping 与initHandlerAdapter两个方法，为引用的HandlerMapping与HandlerAdapter赋值。

你可以看下DispatcherServlet的refresh()的改造结果。

```plain
refresh()	{
    	initController();

		initHandlerMappings(this.webApplicationContext);
		initHandlerAdapters(this.webApplicationContext);
}

```

初始化这两个部件的代码如下：

```plain
    protected void initHandlerMappings(WebApplicationContext wac) {
    	this.handlerMapping = new RequestMappingHandlerMapping(wac);
    }
    protected void initHandlerAdapters(WebApplicationContext wac) {
    	this.handlerAdapter = new RequestMappingHandlerAdapter(wac);
    }

```

DispatcherServlet的分发过程也要改造一下，不再通过doGet()方法了，而是通过重写的service方法来实现的，而service方法则调用了doDispatch方法，这个方法内部通过handlerMapping获取到对应handlerMethod，随后通过HandlerAdapter进行处理，你可以看一下这个类修改后的源代码。

```java
protected void service(HttpServletRequest request, HttpServletResponse
response) {
    request.setAttribute(WEB_APPLICATION_CONTEXT_ATTRIBUTE,
this.webApplicationContext);
	try {
		doDispatch(request, response);
	} catch (Exception e) {
		e.printStackTrace();
	}
	finally {
	}
}
protected void doDispatch(HttpServletRequest request, HttpServletResponse
response) throws Exception{
    HttpServletRequest processedRequest = request;
    HandlerMethod handlerMethod = null;
    handlerMethod = this.handlerMapping.getHandler(processedRequest);
    if (handlerMethod == null) {
		return;
	}
    HandlerAdapter ha = this.handlerAdapter;
    ha.handle(processedRequest, response, handlerMethod);
}

```

可以看到，经过这么一改造，相比之前DispatcherServlet的代码简化了很多，并且当前业务程序不用再固定写死在doGet()方法里面，可以按照自身的业务需求随意使用任何方法名，也为今后提供多种请求方式，例如POST、PUT、DELETE等提供了便利。

以前，用原始的Servlet规范，我们的业务逻辑全部写在doGet()、doPost()等方法中，每一个业务逻辑程序都是一个独立的Servlet。现在经过我们这几节课的操作，整个系统用一个唯一的DispatcherServlet来拦截请求，并根据注解，定位需要调用的方法，我们就能够更加专注于本身业务代码的实现。这种我们称之为Dispatcher的设计模式也是要用心学习的。

## 小结

这节课我们的主要工作就是拆解Dispatcher。首先拆解的是ApplicationContext，现在我们有了两级上下文，一级用于IoC容器，我们叫parent上下文，一级用于Web上下文，WebApplicationContext持有对parent上下文的引用。方便起见，我们还增加了@RequestMapping注解来声明URL映射，然后新增RequestMappingHandlerMapping 与RequestMappingHandlerAdapter，分别包装URL映射关系和映射后的处理过程。

通过这些拆解工作，我们就把DispatcherServlet的功能进行了分治，把专门的事情交给专门的部件去完成，有利于今后的扩展。

完整源代码参见 [https://github.com/YaleGuo/minis](https://github.com/YaleGuo/minis)

## 课后题

学完这节课，我也给你留一道思考题。目前，我们只支持了GET方法，你能不能尝试自己增加POST方法。想一想，需要改变现有的程序结构吗？欢迎你在留言区和我交流讨论，也欢迎你把这节课分享给需要的朋友。我们下节课见！