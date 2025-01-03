你好，我是郭屹。今天我们继续手写MiniTomcat。

上节课我们把Request和Response从无状态变成了有状态，实现了Session和Cookie的管理，还实现了同一页面的资源请求复用Socket，减少了性能消耗。

到目前为止，我们已经基本将浏览器与服务器之间的通信处理完毕。接下来我们再看后端服务器，现在我们还是使用ServletProcessor简单地调用Servlet的service方法，接下来我们考虑将其扩展，对Servlet进行管理，这就引入了Container容器的概念。 **我们计划让Container和Connector配合在一起工作，前者负责后端Servlet管理，而后者则负责通信管理。**

![图片](https://static001.geekbang.org/resource/image/6e/42/6e0069a19d16f6ddf482820a06b8d242.png?wh=1920x998)

初步构建容器后，我们还会考虑使用Wrapper进行包装，用于维护Servlet的生命周期：初始化、提供服务、销毁这个全过程，把Servlet完全纳入程序自动管理之中，让应用程序员更少地感知到底层的配置，更专注于业务逻辑本身。

接下来我们一起来动手实现。

## 项目结构

这节课我们新增ServletContainer与ServletWrapper两个类，分别定义Container与Wrapper，你可以看一下现在的程序结构。

```plain
MiniTomcat
├─ src
│  ├─ main
│  │  ├─ java
│  │  │  ├─ server
│  │  │  │  ├─ CookieTools.java
│  │  │  │  ├─ DefaultHeaders.java
│  │  │  │  ├─ HttpConnector.java
│  │  │  │  ├─ HttpHeader.java
│  │  │  │  ├─ HttpProcessor.java
│  │  │  │  ├─ HttpRequest.java
│  │  │  │  ├─ HttpRequestFacade.java
│  │  │  │  ├─ HttpRequestLine.java
│  │  │  │  ├─ HttpResponse.java
│  │  │  │  ├─ HttpResponseFacade.java
│  │  │  │  ├─ HttpServer.java
│  │  │  │  ├─ Request.java
│  │  │  │  ├─ ServletContainer.java
│  │  │  │  ├─ Response.java
│  │  │  │  ├─ ServletProcessor.java
│  │  │  │  ├─ ServletWrapper.java
│  │  │  │  ├─ Session.java
│  │  │  │  ├─ SessionFacade.java
│  │  │  │  ├─ SocketInputStream.java
│  │  │  │  ├─ StatisResourceProcessor.java
│  │  ├─ resources
│  ├─ test
│  │  ├─ java
│  │  │  ├─ test
│  │  │  │  ├─ HelloServlet.java
│  │  │  │  ├─ TestServlet.java
│  │  ├─ resources
├─ webroot
│  ├─ test
│  │  ├─ HelloServlet.class
│  │  ├─ TestServlet.class
│  ├─ hello.txt
├─ pom.xml

```

## Container——Servlet管理容器

在改造之前，我们先关注一下整个Server的启动类——HttpServer。目前，我们的启动类是比较简单的，main函数内只有两行。

```java
package server;
public class HttpServer {
    public static void main(String[] args) {
        HttpConnector connector = new HttpConnector();
        connector.start();
    }
}

```

通过代码可以知道，我们Server的起点就是HttpConnector，所以之前对Servlet的管理也全是交由Connector进行处理，不过这并不好，角色混合了。所以接下来我们要做的，就是引入Container容器这个概念，将Servlet管理和网络通信功能一分为二。

首先是定义ServletContainer类。

```java
package server;
//Servlet容器
public class ServletContainer {
    HttpConnector connector = null;
    ClassLoader loader = null;
    //包含servlet类和实例的map
    Map<String,String> servletClsMap = new ConcurrentHashMap<>(); //servletName - ServletClassName
    Map<String,Servlet> servletInstanceMap = new ConcurrentHashMap<>();//servletName - servlet
    public ServletContainer() {
        try {
            // create a URLClassLoader
            URL[] urls = new URL[1];
            URLStreamHandler streamHandler = null;
            File classPath = new File(HttpServer.WEB_ROOT);
            String repository = (new URL("file", null, classPath.getCanonicalPath() + File.separator)).toString() ;
            urls[0] = new URL(null, repository, streamHandler);
            loader = new URLClassLoader(urls);
        } catch (IOException e) {
            System.out.println(e.toString() );
        }
    }
    public String getInfo() {
        return null;
    }
    public ClassLoader getLoader(){
        return this.loader;
    }
    public void setLoader(ClassLoader loader) {
        this.loader = loader;
    }
    public HttpConnector getConnector() {
        return connector;
    }
    public void setConnector(HttpConnector connector) {
        this.connector = connector;
    }
    public String getName() {
        return null;
    }
    public void setName(String name) {
    }
    //invoke方法用于从map中找到相关的servlet，然后调用
    public void invoke(HttpRequest request, HttpResponse response)
            throws IOException, ServletException {
        Servlet servlet = null;
        ClassLoader loader = getLoader();
        String uri = request.getUri();
        String servletName = uri.substring(uri.lastIndexOf("/") + 1);
        String servletClassName = servletName;
        servlet = servletInstanceMap.get(servletName);
        //如果容器内没有这个servlet，先要load类，创建新实例
        if (servlet == null) {
            Class<?> servletClass = null;
            try {
                servletClass = loader.loadClass(servletClassName);
            } catch (ClassNotFoundException e) {
                System.out.println(e.toString());
            }
            try {
                servlet = (Servlet) servletClass.newInstance();
            } catch (InstantiationException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
            servletClsMap.put(servletName, servletClassName);
            servletInstanceMap.put(servletName, servlet);
            //按照规范，创建新实例的时候需要调用init()
            servlet.init(null);
        }
        //然后调用service()
        try {
            HttpRequestFacade requestFacade = new HttpRequestFacade(request);
            HttpResponseFacade responseFacade = new HttpResponseFacade(response);
            System.out.println("Call service()");
            servlet.service(requestFacade, responseFacade);
        }
        catch (Exception e) {
            System.out.println(e.toString());
        }
        catch (Throwable e) {
            System.out.println(e.toString());
        }
    }
}

```

从ServletContainer的代码里，我们又看到了熟悉的面孔——ClassLoader，此前将ClassLoader直接交由HttpConnector管理，定义了域。

```java
public static URLClassLoader loader = null;

```

现在进行改造，用新创建的ServletContainer类管理ClassLoader，并提供对应的 `getLoader()` 和 `setLoader()` 方法，同时也将原来在ServletProcessor内调用Servlet的代码挪到ServletContainer的 `invoke()` 方法中。

之前在调用 `invoke()` 方法时，每次都是加载Servlet的类进行实例化，并调用service方法，在这里我们进一步把Servlet放到Map中存起来，包含多Servlet实例，其中servletClsMap用于存储Servlet名称与Servlet类名的映射关系，而servletInstanceMap用于存储Servlet名称与具体Servlet对象的映射关系。

这样改造后，当 `invoke()` 方法被调用时，如果有Servlet实例，就直接调用 `service()`，如果没有实例，就加载并创建实例，并调用 `init()` 进行初始化工作。

现在ServletProcessor可以尽可能地简化了，你可以看一下简化后的代码。

```java
package server;
public class ServletProcessor {
    private HttpConnector connector;
    public ServletProcessor(HttpConnector connector) {
        this.connector = connector;
    }
    public void process(HttpRequest request, HttpResponse response) throws IOException, ServletException {
        this.connector.getContainer().invoke(request, response);
    }
}

```

在ServletProcessor中我们定义了传入Connector的构造函数，所以在Processor代码中，需要调整初始化Processor的代码。

```java
if (request.getUri().startsWith("/servlet/")) {
    ServletProcessor processor = new ServletProcessor(this.connector);
    processor.process(request, response);
}

```

接下来，我们再转向HttpConnector。在定义了Container之后，自然地，要把Container和Connector结合起来，我们在HttpConnector中改一下代码。

```java
package server;
public class HttpConnector implements Runnable {
    int minProcessors = 3;
    int maxProcessors = 10;
    int curProcessors = 0;
    Deque<HttpProcessor> processors = new ArrayDeque<>();
    public static Map<String, HttpSession> sessions = new ConcurrentHashMap<>();
    //这是与connector相关联的container
    ServletContainer container = null;
    public void run() {
        ServerSocket serverSocket = null;
        int port = 8080;
        try {
            serverSocket = new ServerSocket(port, 1, InetAddress.getByName("127.0.0.1"));
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
        // initialize processors pool
        for (int i = 0; i < minProcessors; i++) {
            HttpProcessor initprocessor = new HttpProcessor(this);
            initprocessor.start();
            processors.push(initprocessor);
        }
        curProcessors = minProcessors;
        while (true) {
            Socket socket = null;
            try {
                socket = serverSocket.accept();
                HttpProcessor processor = createProcessor();
                if (processor == null) {
                    socket.close();
                    continue;
                }
                processor.assign(socket);
                // Close the socket
//                socket.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    public void start() {
        Thread thread = new Thread(this);
        thread.start();
    }
    public ServletContainer getContainer() {
        return container;
    }
    public void setContainer(ServletContainer container) {
        this.container = container;
    }
}

```

上述代码中，新增了ServletContainer类型的container属性，添加了对应 `getContainer()` 与 `setContainer()` 方法，移除了原本处理Classloader的相关代码。

这个时候，我们就可以调整HttpServer里的代码，拆分功能了。

```java
package server;
public class HttpServer {
    public static final String WEB_ROOT =
            System.getProperty("user.dir") + File.separator + "webroot";
    public static void main(String[] args) {
        //创建connector和container
        HttpConnector connector = new HttpConnector();
        ServletContainer container = new ServletContainer();
        //connector和container互相指引
        connector.setContainer(container);
        container.setConnector(connector);
        connector.start();
    }
}

```

这里我们进一步拆分了HttpConnector，做到了ServletContainer管理Servlet，HttpConnector负责通信管理，各司其职。

到这里，我想多说几句。软件结构应该怎么进行拆分？我们可以直观地将一个软件当成一个公司或者一个团体，里面有很多岗位和人，如果在公司里需要将某一个工作专门交由专人负责，就可以设置一个岗位，类比软件结构，就是在软件中新添加一个类，一个类就是一个岗位。这种拟人化的思考方式对我们分析软件结构很有帮助。

## Wrapper——增强Servlet管理

刚刚我们已经使用Container实现了Servlet的管理，我们继续关注这一部分， **采用Wrapper包装，用来维护Servlet的生命周期**。

为什么需要这么一个Wrapper呢？从功能角度，不引入它也是没有问题的。但是如果没有Wrapper，我们就得在Container这个容器里直接管理Servlet，这相当于在一个大的纸盒子中直接放上很多小玩具，比较繁琐。

所以超市给了我们一个方案：每个小玩具外面套一个包装，比如小盒子或者是塑料袋子，再将这些小盒子或者袋子放在大纸盒中，方便人们拿取。这个Wrapper也是同样的思路。

首先我们来定义ServletWrapper类。

```java
package server;
public class ServletWrapper {
    private Servlet instance = null;
    private String servletClass;
    private ClassLoader loader;
    private String name;
    protected ServletContainer parent = null;
    public ServletWrapper(String servletClass, ServletContainer parent) {
        this.parent = parent;
        this.servletClass = servletClass;
        try {
            loadServlet();
        } catch (ServletException e) {
            e.printStackTrace();
        }
    }
    public ClassLoader getLoader() {
        if (loader != null)
            return loader;
        return parent.getLoader();
    }
    public String getServletClass() {
        return servletClass;
    }
    public void setServletClass(String servletClass) {
        this.servletClass = servletClass;
    }
    public ServletContainer getParent() {
        return parent;
    }
    public void setParent(ServletContainer container) {
        parent = container;
    }
    public Servlet getServlet(){
        return this.instance;
    }
    public Servlet loadServlet() throws ServletException {
        if (instance!=null)
            return instance;
        Servlet servlet = null;
        String actualClass = servletClass;
        if (actualClass == null) {
            throw new ServletException("servlet class has not been specified");
        }
        ClassLoader classLoader = getLoader();
        Class classClass = null;
        try {
            if (classLoader!=null) {
                classClass = classLoader.loadClass(actualClass);
            }
        }
        catch (ClassNotFoundException e) {
            throw new ServletException("Servlet class not found");
        }
        try {
            servlet = (Servlet) classClass.newInstance();
        }
        catch (Throwable e) {
            throw new ServletException("Failed to instantiate servlet");
        }
        try {
            servlet.init(null);
        }
        catch (Throwable f) {
            throw new ServletException("Failed initialize servlet.");
        }
        instance =servlet;
        return servlet;
    }
    public void invoke(HttpServletRequest request, HttpServletResponse response)
            throws IOException, ServletException {
        if (instance != null) {
            instance.service(request, response);
        }
    }
}

```

在ServletWrapper类中，核心在于 `loadServlet()` 方法，主要是通过一个Classloader加载并实例化Servlet，然后调用 `init()` 方法进行初始化工作，其实也是刚刚我们在ServletContainer中的处理。所以在ServletContainer类里，我们可以进一步改造，将一些对Servlet的处理交给ServletWrapper进行。

首先是servletInstanceMap，Value类型可设置成更高层次的ServletWrapper，你可以看一下修改后的样子。

```java
Map<String,ServletWrapper> servletInstanceMap = new ConcurrentHashMap<>();

```

其次是调整invoke方法，你可以看一下调整后的invoke方法。

```java
public void invoke(HttpRequest request, HttpResponse response)
        throws IOException, ServletException {
    ServletWrapper servletWrapper = null;
    String uri = request.getUri();
    String servletName = uri.substring(uri.lastIndexOf("/") + 1);
    String servletClassName = servletName;
    servletWrapper = servletInstanceMap.get(servletName);
    if ( servletWrapper == null) {
        servletWrapper = new ServletWrapper(servletClassName,this);
        //servletWrapper.setParent(this);
        this.servletClsMap.put(servletName, servletClassName);
        this.servletInstanceMap.put(servletName, servletWrapper);
    }
    try {
        HttpServletRequest requestFacade = new HttpRequestFacade(request);
        HttpServletResponse responseFacade = new HttpResponseFacade(response);
        System.out.println("Call service()");
        servletWrapper.invoke(requestFacade, responseFacade);
    }
    catch (Exception e) {
        System.out.println(e.toString());
    }
    catch (Throwable e) {
        System.out.println(e.toString());
    }
}

```

这样在ServletContainer中，只是获取到ServletWrapper的实例，调用ServletWrapper内的 `invoke()` 方法，进一步进行了解耦。

## 测试

这节课并没有功能性的变化，所以没有新增测试类，还是和之前的测试方式保持一致。这里就不重复说了。

## 小结

这节课我们实现了ServletContainer管理全部的Servlet，将原本的管理功能从Connector内抽离，让Connector专注服务器通信管理。这个Container就是我们MiniTomcat初始容器，它里面有一个map，包含了管理的Servlet实例。有了这个Container，Processor就变得简单了，它里面的新方法 `process()` 只需要调用Container的 `invoke()` 就可以了。

同时，我们引入ServletWrapper，对ServletContainer做了更进一步的拆分，更加方便对Servlet进行管理。今后，我们会把Container进一步拆成多层。

本节课代码参见： [https://gitee.com/yaleguo1/minit-learning-demo/tree/geek\_chapter10](https://gitee.com/yaleguo1/minit-learning-demo/tree/geek_chapter10)

## 思考题

学完了这节课的内容，我们来思考一个问题：现在这个HttpServer仅仅只是创建Connector和Container，只是一个壳子了，按照拟人化的思路，HttpServer应该是一个公司，那么这个类从道理上还应该分工负责做些什么？

欢迎你把你思考后的结果分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！