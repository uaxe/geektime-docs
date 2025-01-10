你好，我是郭屹。今天我们继续手写MiniTomcat。

上一节课我们实现了Pipeline和Valve，这样我们在流程走通的前提下，可以在每一层Container之间增加权限校验、日志打印、错误输出等自定义的处理逻辑。此外我们引入了责任链这一设计模式，来依次调用这些处理逻辑。

这节课我们继续来完善MiniTomcat，我们计划引入两个组件——Filter（过滤器）以及Listener（监听器），并且还是使用经典的职责链模式。

过滤器可以检查请求对象以及返回对象，并通过请求对象和返回对象的包装类进行修改，而且多个过滤器之间可以串联，就像流水线一样一层层进行过滤，协同起来组装成最终的请求对象和响应对象。

而监听器的存在是为了配合我们目前已有的Container、Session等机制，通过监听这些机制的事件，比如启动、超时、结束等，更好地对服务器进行处理。

我们一起来动手实现。

## 项目结构

这节课我们主要新增了Filter相关处理方法类，还有Container、Instance与Session的事件和监听器，具体类的功能我们后面会详细介绍。你可以看一下现在的项目结构。

```plain
MiniTomcat
├─ src
│  ├─ main
│  │  ├─ java
│  │  │  ├─ com
│  │  │  │  ├─ minit
│  │  │  │  │  ├─ connector
│  │  │  │  │  │  ├─ http
│  │  │  │  │  │  │  ├─ DefaultHeaders.java
│  │  │  │  │  │  │  ├─ HttpConnector.java
│  │  │  │  │  │  │  ├─ HttpHeader.java
│  │  │  │  │  │  │  ├─ HttpProcessor.java
│  │  │  │  │  │  │  ├─ HttpRequestImpl.java
│  │  │  │  │  │  │  ├─ HttpRequestLine.java
│  │  │  │  │  │  │  ├─ HttpResponseImpl.java
│  │  │  │  │  │  │  ├─ ServletProcessor.java
│  │  │  │  │  │  │  ├─ SocketInputStream.java
│  │  │  │  │  │  │  ├─ StatisResourceProcessor.java
│  │  │  │  │  │  ├─ HttpRequestFacade.java
│  │  │  │  │  │  ├─ HttpResponseFacade.java
│  │  │  │  │  ├─ core
│  │  │  │  │  │  ├─ ApplicationFilterChain.java
│  │  │  │  │  │  ├─ ApplicationFilterConfig.java
│  │  │  │  │  │  ├─ ContainerBase.java
│  │  │  │  │  │  ├─ ContainerListenerDef.java
│  │  │  │  │  │  ├─ FilterDef.java
│  │  │  │  │  │  ├─ FilterMap.java
│  │  │  │  │  │  ├─ StandardContext.java
│  │  │  │  │  │  ├─ StandardContextValve.java
│  │  │  │  │  │  ├─ StandardPipeline.java
│  │  │  │  │  │  ├─ StandardWrapper.java
│  │  │  │  │  │  ├─ StandardWrapperValve.java
│  │  │  │  │  ├─ logger
│  │  │  │  │  │  ├─ Constants.java
│  │  │  │  │  │  ├─ FileLogger.java
│  │  │  │  │  │  ├─ LoggerBase.java
│  │  │  │  │  │  ├─ SystemErrLogger.java
│  │  │  │  │  │  ├─ SystemOutLogger.java
│  │  │  │  │  ├─ session
│  │  │  │  │  │  ├─ StandardSession.java
│  │  │  │  │  │  ├─ StandardSessionFacade.java
│  │  │  │  │  ├─ startup
│  │  │  │  │  │  ├─ BootStrap.java
│  │  │  │  │  ├─ util
│  │  │  │  │  │  ├─ CookieTools.java
│  │  │  │  │  │  ├─ StringManager.java
│  │  │  │  │  │  ├─ URLDecoder.java
│  │  │  │  │  ├─ valves
│  │  │  │  │  │  ├─ AccessLogValve.java
│  │  │  │  │  │  ├─ ValveBase.java
│  │  │  │  ├─ Connector.java
│  │  │  │  ├─ Container.java
│  │  │  │  ├─ ContainerEvent.java
│  │  │  │  ├─ ContainerListener.java
│  │  │  │  ├─ Context.java
│  │  │  │  ├─ InstanceEvent.java
│  │  │  │  ├─ InstanceListener.java
│  │  │  │  ├─ Logger.java
│  │  │  │  ├─ Pipeline.java
│  │  │  │  ├─ Request.java
│  │  │  │  ├─ Response.java
│  │  │  │  ├─ Session.java
│  │  │  │  ├─ SessionEvent.java
│  │  │  │  ├─ SessionListener.java
│  │  │  │  ├─ Valve.java
│  │  │  │  ├─ ValveContext.java
│  │  │  │  ├─ Wrapper.java
│  │  ├─ resources
│  ├─ test
│  │  ├─ java
│  │  │  ├─ test
│  │  │  │  ├─ HelloServlet.java
│  │  │  │  ├─ TestFilter.java
│  │  │  │  ├─ TestListener.java
│  │  │  │  ├─ TestServlet.java
│  │  ├─ resources
├─ webroot
│  ├─ test
│  │  ├─ HelloServlet.class
│  │  ├─ TestFilter.class
│  │  ├─ TestListener.class
│  │  ├─ TestServlet.class
│  ├─ hello.txt
├─ pom.xml

```

## 引入过滤器

首先我们看看如何引入过滤器。按照Servlet规范，我们定义了Filter、FilterConfig和FilterChain三个接口。我们先采用ApplicationFilterConfig类，对Filter进行包装。你可以看一下ApplicationFilterConfig类的定义。

```java
package com.minit.core;
final class ApplicationFilterConfig implements FilterConfig {
    public ApplicationFilterConfig(Context context, FilterDef filterDef)
            throws ClassCastException, ClassNotFoundException,
            IllegalAccessException, InstantiationException,
            ServletException {
        super();
        this.context = context;
        setFilterDef(filterDef);
    }
    private Context context = null;
    private Filter filter = null;
    private FilterDef filterDef = null;
    public String getFilterName() {
        return (filterDef.getFilterName());
    }
    public String getInitParameter(String name) {
        Map<String,String> map = filterDef.getParameterMap();
        if (map == null)
            return (null);
        else
            return ((String) map.get(name));
    }
    public Enumeration<String> getInitParameterNames() {
        Map<String,String> map = filterDef.getParameterMap();
        if (map == null)
            return Collections.enumeration(new ArrayList<String>());
        else
            return (Collections.enumeration(map.keySet()));
    }
    public ServletContext getServletContext() {
        return (this.context.getServletContext());
    }
    public String toString() {
        StringBuffer sb = new StringBuffer("ApplicationFilterConfig[");
        sb.append("name=");
        sb.append(filterDef.getFilterName());
        sb.append(", filterClass=");
        sb.append(filterDef.getFilterClass());
        sb.append("]");
        return (sb.toString());
    }
    Filter getFilter() throws ClassCastException, ClassNotFoundException,
            IllegalAccessException, InstantiationException, ServletException {
        // 返回现有的过滤器实例（如果有的话）
        if (this.filter != null)
            return (this.filter);
        // 确定我们将使用的类加载器
        String filterClass = filterDef.getFilterClass();
        ClassLoader classLoader = null;
        classLoader = context.getLoader();
        ClassLoader oldCtxClassLoader =
                Thread.currentThread().getContextClassLoader();
        // 实例化这个过滤器的新实例并返回
        Class clazz = classLoader.loadClass(filterClass);
        this.filter = (Filter) clazz.newInstance();
        filter.init(this);
        return (this.filter);
    }
    FilterDef getFilterDef() {
        return (this.filterDef);
    }
    void release() {
        if (this.filter != null)
            filter.destroy();
        this.filter = null;
    }
    void setFilterDef(FilterDef filterDef)
            throws ClassCastException, ClassNotFoundException,
            IllegalAccessException, InstantiationException,
            ServletException {
        this.filterDef = filterDef;
        if (filterDef == null) {
            // 释放之前分配的所有过滤器实例
            if (this.filter != null)
                this.filter.destroy();
            this.filter = null;
        } else {
            // 分配一个新的过滤器实例
            Filter filter = getFilter();
        }
    }
}

```

通过ApplicationFilterConfig类的实现我们可以看到，引入了Filter对象，这个Filter对象就是 `javax.servlet.Filter`，同时还定义了Context和FilterDef，FilterDef定义了Filter的部分参数信息，你可以看一下相关实现。

```java
package com.minit.core;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
public final class FilterDef {
    private String description = null;
    public String getDescription() {
        return (this.description);
    }
    public void setDescription(String description) {
        this.description = description;
    }
    private String displayName = null;
    public String getDisplayName() {
        return (this.displayName);
    }
    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }
    private String filterClass = null;
    public String getFilterClass() {
        return (this.filterClass);
    }
    public void setFilterClass(String filterClass) {
        this.filterClass = filterClass;
    }
    private String filterName = null;
    public String getFilterName() {
        return (this.filterName);
    }
    public void setFilterName(String filterName) {
        this.filterName = filterName;
    }
    private String largeIcon = null;
    public String getLargeIcon() {
        return (this.largeIcon);
    }
    public void setLargeIcon(String largeIcon) {
        this.largeIcon = largeIcon;
    }
    private Map<String,String> parameters = new ConcurrentHashMap<>();
    public Map<String,String> getParameterMap() {
        return (this.parameters);
    }
    private String smallIcon = null;
    public String getSmallIcon() {
        return (this.smallIcon);
    }
    public void setSmallIcon(String smallIcon) {
        this.smallIcon = smallIcon;
    }
    public void addInitParameter(String name, String value) {
        parameters.put(name, value);
    }
    public String toString() {
        StringBuffer sb = new StringBuffer("FilterDef[");
        sb.append("filterName=");
        sb.append(this.filterName);
        sb.append(", filterClass=");
        sb.append(this.filterClass);
        sb.append("]");
        return (sb.toString());
    }
}

```

FilterDef定义不难理解，主要包括Filter的描述、名称等信息，定义了众多Getter和Setter方法。在FilterDef类定义完毕后，我们就通过Config拿到了Filter，并进行初始化工作。

由于支持多个FilterConfig，所以我们使用链路模式进行管理，定义ApplicationFilterChain类。

```java
package com.minit.core;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.Servlet;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import com.minit.connector.HttpRequestFacade;
import com.minit.connector.HttpResponseFacade;
import com.minit.connector.http.HttpRequestImpl;
import com.minit.connector.http.HttpResponseImpl;
final class ApplicationFilterChain implements FilterChain {
    public ApplicationFilterChain() {
        super();
    }
    private ArrayList<ApplicationFilterConfig> filters = new ArrayList<>();
    private Iterator<ApplicationFilterConfig> iterator = null;
    private Servlet servlet = null;

    //核心方法，启动过滤
    public void doFilter(ServletRequest request, ServletResponse response)
            throws IOException, ServletException {
        System.out.println("FilterChain doFilter()");
        internalDoFilter(request,response);
    }
    private void internalDoFilter(ServletRequest request, ServletResponse response)
            throws IOException, ServletException {
        if (this.iterator == null)
            this.iterator = filters.iterator();
        if (this.iterator.hasNext()) {
            //拿到下一个filter
            ApplicationFilterConfig filterConfig =
                    (ApplicationFilterConfig) iterator.next();
            Filter filter = null;
            try {
                //进行过滤，这是职责链模式，一个一个往下传
                filter = filterConfig.getFilter();
                System.out.println("Filter doFilter()");
                //调用filter的过滤逻辑，根据规范，filter中要再次调用filterChain.doFilter
                //这样又会回到internalDoFilter()方法，就会再拿到下一个filter，
                //如此实现一个一个往下传
                filter.doFilter(request, response, this);
            } catch (IOException e) {
                throw e;
            } catch (ServletException e) {
                throw e;
            } catch (RuntimeException e) {
                throw e;
            } catch (Throwable e) {
                throw new ServletException("filterChain.filter", e);
            }
            return;
        }
        try {
            //最后调用servlet
            HttpServletRequest requestFacade = new HttpRequestFacade((HttpRequestImpl) request);
            HttpServletResponse responseFacade = new HttpResponseFacade((HttpResponseImpl) response);
            servlet.service(requestFacade, responseFacade);
        } catch (IOException e) {
            throw e;
        } catch (ServletException e) {
            throw e;
        } catch (RuntimeException e) {
            throw e;
        } catch (Throwable e) {
            throw new ServletException("filterChain.servlet", e);
        }
    }
    void addFilter(ApplicationFilterConfig filterConfig) {
        this.filters.add(filterConfig);
    }
    void release() {
        this.filters.clear();
        this.iterator = iterator;
        this.servlet = null;
    }
    void setServlet(Servlet servlet) {
        this.servlet = servlet;
    }
}

```

我们使用ArrayList存放所有的filter，而最重要的实现方法就是 **doFilter**，这也是FilterChain接口本身所定义的，我们在这进行了实现。doFilter方法内又调用了internalDoFilter方法来实现。我们使用了iterator迭代器指向filters，通过 `filterConfig.getFilter()` 方法获取第一个filter后调用 `filter.doFilter(request, response, this)`。

需要注意的是，这个地方调用了第一个 `Filter.doFilter()`，而不是在ApplicationFilterChain中迭代遍历。之后的filter还是采用职责链设计模式，由第一个Filter调用下一个，一个一个地继续。

当所有Filter过滤完之后，执行 `servlet.service(requestFacade, responseFacade)` 方法，这也是Filter Chain自动完成的， `service()` 成了Chain之后的一个环节，所以Processor和Container不再需要显式地调用 `service()`。

有了这些准备后，我们接下来可以把Filter加入到Container里，每一层都可以加，我们只在StandardContext这一层保存，重新启动的时候在BootStrap里加上，调用的程序写在StandardWrapperValve里。

接下来我们看看如何实现，首先定义FilterMap类以及URLDecoder工具类。

URLDecoder工具类：

```java
package com.minit.util;
public class URLDecoder {
    public static String URLDecode(String str) {
        return URLDecode(str, null);
    }
    public static String URLDecode(String str, String enc) {
        if (str == null)
            return (null);
        int len = str.length();
        byte[] bytes = new byte[len];
        bytes = str.getBytes();
        return URLDecode(bytes, enc);
    }
    public static String URLDecode(byte[] bytes) {
        return URLDecode(bytes, null);
    }
    public static String URLDecode(byte[] bytes, String enc) {
        if (bytes == null)
            return (null);
        int len = bytes.length;
        int ix = 0;
        int ox = 0;
        while (ix < len) {
            byte b = bytes[ix++];     // 获取要测试的字节
            if (b == '+') {
                b = (byte)' ';
            } else if (b == '%') {
                b = (byte) ((convertHexDigit(bytes[ix++]) << 4)
                        + convertHexDigit(bytes[ix++]));
            }
            bytes[ox++] = b;
        }
        if (enc != null) {
            try {
                return new String(bytes, 0, ox, enc);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return new String(bytes, 0, ox);
    }
    private static byte convertHexDigit( byte b ) {
        if ((b >= '0') && (b <= '9')) return (byte)(b - '0');
        if ((b >= 'a') && (b <= 'f')) return (byte)(b - 'a' + 10);
        if ((b >= 'A') && (b <= 'F')) return (byte)(b - 'A' + 10);
        return 0;
    }
}

```

FilterMap类：

```java
package com.minit.core;
import com.minit.util.URLDecoder;
public final class FilterMap {
    private String filterName = null;
    public String getFilterName() {
        return (this.filterName);
    }
    public void setFilterName(String filterName) {
        this.filterName = filterName;
    }
    private String servletName = null;
    public String getServletName() {
        return (this.servletName);
    }
    public void setServletName(String servletName) {
        this.servletName = servletName;
    }
    private String urlPattern = null;
    public String getURLPattern() {
        return (this.urlPattern);
    }
    public void setURLPattern(String urlPattern) {
        this.urlPattern = URLDecoder.URLDecode(urlPattern);
    }
    public String toString() {
        StringBuffer sb = new StringBuffer("FilterMap[");
        sb.append("filterName=");
        sb.append(this.filterName);
        if (servletName != null) {
            sb.append(", servletName=");
            sb.append(servletName);
        }
        if (urlPattern != null) {
            sb.append(", urlPattern=");
            sb.append(urlPattern);
        }
        sb.append("]");
        return (sb.toString());
    }
}

```

紧接着调整StandardContext，新增下面这些代码。这些代码进行了过滤器的配置和处理。

```java
package com.minit.core;
public class StandardContext extends ContainerBase implements Context{
    //下面的属性记录了filter的配置
    private Map<String,ApplicationFilterConfig> filterConfigs = new ConcurrentHashMap<>();
    private Map<String,FilterDef> filterDefs = new ConcurrentHashMap<>();
    private FilterMap filterMaps[] = new FilterMap[0];

    public void addFilterDef(FilterDef filterDef) {
        filterDefs.put(filterDef.getFilterName(), filterDef);
    }
    public void addFilterMap(FilterMap filterMap) {
        // 验证所建议的过滤器映射
        String filterName = filterMap.getFilterName();
        String servletName = filterMap.getServletName();
        String urlPattern = filterMap.getURLPattern();
        if (findFilterDef(filterName) == null)
            throw new IllegalArgumentException("standardContext.filterMap.name"+filterName);
        if ((servletName == null) && (urlPattern == null))
            throw new IllegalArgumentException("standardContext.filterMap.either");
        if ((servletName != null) && (urlPattern != null))
            throw new IllegalArgumentException("standardContext.filterMap.either");
        // 因为过滤器模式是2.3中的新功能，所以不需要调整
        // 对于2.2版本的向后兼容性
        if ((urlPattern != null) && !validateURLPattern(urlPattern))
            throw new IllegalArgumentException("standardContext.filterMap.pattern"+urlPattern);
        // 将这个过滤器映射添加到我们已注册的集合中
        synchronized (filterMaps) {
            FilterMap results[] =new FilterMap[filterMaps.length + 1];
            System.arraycopy(filterMaps, 0, results, 0, filterMaps.length);
            results[filterMaps.length] = filterMap;
            filterMaps = results;
        }
    }
    public FilterDef findFilterDef(String filterName) {
        return ((FilterDef) filterDefs.get(filterName));
    }
    public FilterDef[] findFilterDefs() {
        synchronized (filterDefs) {
            FilterDef results[] = new FilterDef[filterDefs.size()];
            return ((FilterDef[]) filterDefs.values().toArray(results));
        }
    }
    public FilterMap[] findFilterMaps() {
        return (filterMaps);
    }
    public void removeFilterDef(FilterDef filterDef) {
        filterDefs.remove(filterDef.getFilterName());
    }

    public void removeFilterMap(FilterMap filterMap) {
        synchronized (filterMaps) {
            // 确保当前存在这个过滤器映射
            int n = -1;
            for (int i = 0; i < filterMaps.length; i++) {
                if (filterMaps[i] == filterMap) {
                    n = i;
                    break;
                }
            }
            if (n < 0)
                return;
            // 删除指定的过滤器映射
            FilterMap results[] = new FilterMap[filterMaps.length - 1];
            System.arraycopy(filterMaps, 0, results, 0, n);
            System.arraycopy(filterMaps, n + 1, results, n,
                    (filterMaps.length - 1) - n);
            filterMaps = results;
        }
    }
    //对配置好的所有filter名字，创建实例，存储在filterConfigs中，可以生效了
    public boolean filterStart() {
        System.out.println("Filter Start..........");
        // 为每个定义的过滤器实例化并记录一个FilterConfig
        boolean ok = true;
        synchronized (filterConfigs) {
            filterConfigs.clear();
            Iterator<String> names = filterDefs.keySet().iterator();
            while (names.hasNext()) {
                String name = names.next();
                ApplicationFilterConfig filterConfig = null;
                try {
                    filterConfig = new ApplicationFilterConfig
                            (this, (FilterDef) filterDefs.get(name));
                    filterConfigs.put(name, filterConfig);
                } catch (Throwable t) {
                    ok = false;
                }
            }
        }
        return (ok);
    }
    public FilterConfig findFilterConfig(String name) {
        return (filterConfigs.get(name));
    }
    private boolean validateURLPattern(String urlPattern) {
        if (urlPattern == null)
            return (false);
        if (urlPattern.startsWith("*.")) {
            if (urlPattern.indexOf('/') < 0)
                return (true);
            else
                return (false);
        }
        if (urlPattern.startsWith("/"))
            return (true);
        else
            return (false);
    }
}

```

可以看到StandardContext里主要定义了filter的启动方法，用来在BootStrap启动类中启动过滤器。

接下来再调整StandardContextValve类里的invoke方法的实现，增加了filter的支持，不是直接调用Servlet，而是放在filterChain中进行调用，即先进行过滤，然后再到Servlet。

```java
package com.minit.core;
public class StandardWrapperValve extends ValveBase {
    private FilterDef filterDef = null;
    @Override
    public void invoke(Request request, Response response, ValveContext context) throws IOException, ServletException {
        //创建filter Chain，再调用filter，然后调用servlet
        System.out.println("StandardWrapperValve invoke()");
        Servlet instance = ((StandardWrapper)getContainer()).getServlet();
        ApplicationFilterChain filterChain = createFilterChain(request, instance);
        if ((instance != null) && (filterChain != null)) {
            filterChain.doFilter((ServletRequest)request, (ServletResponse)response);
        }
        filterChain.release();
    }
    //根据context中的filter map信息挑选出符合模式的filter，创建filterChain
    private ApplicationFilterChain createFilterChain(Request request, Servlet servlet) {
        System.out.println("createFilterChain()");
        if (servlet == null)
            return (null);
        ApplicationFilterChain filterChain = new ApplicationFilterChain();
        filterChain.setServlet(servlet);
        StandardWrapper wrapper = (StandardWrapper) getContainer();
        StandardContext context = (StandardContext) wrapper.getParent();
        //从context中拿到filter的信息
        FilterMap filterMaps[] = context.findFilterMaps();
        if ((filterMaps == null) || (filterMaps.length == 0))
            return (filterChain);
        //要匹配的路径
        String requestPath = null;
        if (request instanceof HttpServletRequest) {
            String contextPath = "";
            String requestURI = ((HttpRequestImpl)request).getUri(); //((HttpServletRequest) request).getRequestURI();
            if (requestURI.length() >= contextPath.length())
                requestPath = requestURI.substring(contextPath.length());
        }
        //要匹配的servlet名
        String servletName = wrapper.getName();

        //下面遍历filter Map，找到匹配URL模式的filter，加入到filterChain中
        int n = 0;
        for (int i = 0; i < filterMaps.length; i++) {
            if (!matchFiltersURL(filterMaps[i], requestPath))
                continue;
            ApplicationFilterConfig filterConfig = (ApplicationFilterConfig)
                    context.findFilterConfig(filterMaps[i].getFilterName());
            if (filterConfig == null) {
                continue;
            }
            filterChain.addFilter(filterConfig);
            n++;
        }
        //下面遍历filter Map，找到匹配servlet的filter，加入到filterChain中
        for (int i = 0; i < filterMaps.length; i++) {
            if (!matchFiltersServlet(filterMaps[i], servletName))
                continue;
            ApplicationFilterConfig filterConfig = (ApplicationFilterConfig)
                    context.findFilterConfig(filterMaps[i].getFilterName());
            if (filterConfig == null) {
                continue;
            }
            filterChain.addFilter(filterConfig);
            n++;
        }
        return (filterChain);
    }
    //字符串模式匹配filter的过滤路径
    private boolean matchFiltersURL(FilterMap filterMap, String requestPath) {
        if (requestPath == null)
            return (false);
        String testPath = filterMap.getURLPattern();
        if (testPath == null)
            return (false);
        if (testPath.equals(requestPath))
            return (true);
        if (testPath.equals("/*"))
            return (true);
        if (testPath.endsWith("/*")) { //路径符合/前缀，通配成功
            String comparePath = requestPath;
            while (true) {  //以/截取前段字符串，循环匹配
                if (testPath.equals(comparePath + "/*"))
                    return (true);
                int slash = comparePath.lastIndexOf('/');
                if (slash < 0)
                    break;
                comparePath = comparePath.substring(0, slash);
            }
            return (false);
        }
        if (testPath.startsWith("*.")) {
            int slash = requestPath.lastIndexOf('/');
            int period = requestPath.lastIndexOf('.');
            if ((slash >= 0) && (period > slash))
                return (testPath.equals("*." + requestPath.substring(period + 1)));
        }
        return (false); // NOTE - Not relevant for selecting filters
    }
    private boolean matchFiltersServlet(FilterMap filterMap, String servletName) {
        if (servletName == null)
            return (false);
        else
            return (servletName.equals(filterMap.getServletName()));
    }
}

```

最后调整BootStrap类，你可以看一下当前main函数的实现。主要的变化就是配置了filter信息、名称、类名、过滤路径等等。

```java
package com.minit.startup;
public class BootStrap {
    public static void main(String[] args) {
        if (debug >= 1)
            log(".... startup ....");
        HttpConnector connector = new HttpConnector();
        StandardContext container = new StandardContext();
        connector.setContainer(container);
        container.setConnector(connector);
        Logger logger = new FileLogger();
        container.setLogger(logger);
        FilterDef filterDef = new FilterDef();
        filterDef.setFilterName("TestFilter");
        filterDef.setFilterClass("test.TestFilter");
        container.addFilterDef(filterDef);
        FilterMap filterMap = new FilterMap();
        filterMap.setFilterName("TestFilter");
        filterMap.setURLPattern("/*");
        container.addFilterMap(filterMap);
        container.filterStart();
        connector.start();
    }
}

```

这样Filter就定义好了，我们可以在测试文件夹里定义TestFIlter类来测试一下。

```java
package test;
public class TestFilter implements Filter{
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        System.out.println("The very first Filter");
        chain.doFilter(request, response);
    }
}

```

测试类比较简单，实现Servlet的标准Filter规范，实现doFilter方法。

完成过滤器的定义与实现后，我们再来看监听器的实现。

## 引入监听器

监听器一般和事件共同存在，也就是先有事件定义，后面对这个事件进行监听。在MiniTomcat里，我们定义InstanceListener、ContainerListener、SessionListener三种监听器以及对应的事件，分别作用于整个对象实例、容器Container和Session处理。这样我们MiniTomcat内部主要对象的各种行为都能够被监听了。

我们先来看看事件和监听器的代码定义。

ContainerEvent是一个基础的容器事件对象。

```java
package com.minit;
public final class ContainerEvent extends EventObject {
    private Container container = null;
    private Object data = null;
    private String type = null;
    public ContainerEvent(Container container, String type, Object data) {
        super(container);
        this.container = container;
        this.type = type;
        this.data = data;
    }
    public Object getData() {
        return (this.data);
    }
    public Container getContainer() {
        return (this.container);
    }
    public String getType() {
        return (this.type);
    }
    public String toString() {
        return ("ContainerEvent['" + getContainer() + "','" +
                getType() + "','" + getData() + "']");
    }
}

```

ContainerListener用于监听容器事件。

```java
package com.minit;
public interface ContainerListener {
    public void containerEvent(ContainerEvent event);
}

```

InstanceEvent是Servlet的事件。

```java
package com.minit;
public final class InstanceEvent extends EventObject {
    public static final String BEFORE_INIT_EVENT = "beforeInit";
    public static final String AFTER_INIT_EVENT = "afterInit";
    public static final String BEFORE_SERVICE_EVENT = "beforeService";
    public static final String AFTER_SERVICE_EVENT = "afterService";
    public static final String BEFORE_DESTROY_EVENT = "beforeDestroy";
    public static final String AFTER_DESTROY_EVENT = "afterDestroy";
    public static final String BEFORE_DISPATCH_EVENT = "beforeDispatch";
    public static final String AFTER_DISPATCH_EVENT = "afterDispatch";
    public static final String BEFORE_FILTER_EVENT = "beforeFilter";
    public static final String AFTER_FILTER_EVENT = "afterFilter";
    public InstanceEvent(Wrapper wrapper, Filter filter, String type) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = filter;
        this.servlet = null;
        this.type = type;
    }
    public InstanceEvent(Wrapper wrapper, Filter filter, String type,
                         Throwable exception) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = filter;
        this.servlet = null;
        this.type = type;
        this.exception = exception;
    }
    public InstanceEvent(Wrapper wrapper, Filter filter, String type,
                         ServletRequest request, ServletResponse response) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = filter;
        this.servlet = null;
        this.type = type;
        this.request = request;
        this.response = response;
    }
    public InstanceEvent(Wrapper wrapper, Filter filter, String type,
                         ServletRequest request, ServletResponse response,
                         Throwable exception) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = filter;
        this.servlet = null;
        this.type = type;
        this.request = request;
        this.response = response;
        this.exception = exception;
    }
    public InstanceEvent(Wrapper wrapper, Servlet servlet, String type) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = null;
        this.servlet = servlet;
        this.type = type;
    }
    public InstanceEvent(Wrapper wrapper, Servlet servlet, String type,
                         Throwable exception) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = null;
        this.servlet = servlet;
        this.type = type;
        this.exception = exception;
    }
    public InstanceEvent(Wrapper wrapper, Servlet servlet, String type,
                         ServletRequest request, ServletResponse response) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = null;
        this.servlet = servlet;
        this.type = type;
        this.request = request;
        this.response = response;
    }
    public InstanceEvent(Wrapper wrapper, Servlet servlet, String type,
                         ServletRequest request, ServletResponse response,
                         Throwable exception) {
        super(wrapper);
        this.wrapper = wrapper;
        this.filter = null;
        this.servlet = servlet;
        this.type = type;
        this.request = request;
        this.response = response;
        this.exception = exception;
    }
    private Throwable exception = null;
    private Filter filter = null;
    private ServletRequest request = null;
    private ServletResponse response = null;
    private Servlet servlet = null;
    private String type = null;
    private Wrapper wrapper = null;
    public Throwable getException() {
        return (this.exception);
    }
    public Filter getFilter() {
        return (this.filter);
    }
    public ServletRequest getRequest() {
        return (this.request);
    }
    public ServletResponse getResponse() {
        return (this.response);
    }
    public Servlet getServlet() {
        return (this.servlet);
    }
    public String getType() {
        return (this.type);
    }
    public Wrapper getWrapper() {
        return (this.wrapper);
    }
}

```

InstanceListener是Servlet事件的监听器。

```java
package com.minit;
public interface InstanceListener {
    public void instanceEvent(InstanceEvent event);
}

```

SessionEvent是session事件。

```java
package com.minit;
public final class SessionEvent extends EventObject {
    private Object data = null;
    private Session session = null;
    private String type = null;
    public SessionEvent(Session session, String type, Object data) {
        super(session);
        this.session = session;
        this.type = type;
        this.data = data;
    }
    public Object getData() {
        return (this.data);
    }
    public Session getSession() {
        return (this.session);
    }
    public String getType() {
        return (this.type);
    }
    public String toString() {
        return ("SessionEvent['" + getSession() + "','" +
                getType() + "']");
    }
}

```

SessionListener是session事件监听器。

```java
package com.minit;
public interface SessionListener {
    public void sessionEvent(SessionEvent event);
}

```

有了这些事件和监听器的定义后，在响应的类里面加上 `addlistener()`、 `removelistener()` 方法以及 `fireEvent()` 就可以了。所以在StandardContext类和StandardSession类中，我们可以添加这三个方法，你可以看一下相关实现。

首先是StandardContext类，我们在代码里新增方法实现。这些新代码处理了容器监听器。

```java
package com.minit.core;
public class StandardContext extends ContainerBase implements Context{
    private ArrayList<ContainerListenerDef> listenerDefs = new ArrayList<>();
    private ArrayList<ContainerListener> listeners = new ArrayList<>();

    public void start(){
        // 触发一个容器启动事件
        fireContainerEvent("Container Started",this);
    }
    public void addContainerListener(ContainerListener listener) {
        // 添加一个新的容器监听器到监听器列表，并确保线程安全
        synchronized (listeners) {
            listeners.add(listener);
        }
    }
    public void removeContainerListener(ContainerListener listener) {
        // 移除指定的容器监听器，并确保线程安全
        synchronized (listeners) {
            listeners.remove(listener);
        }
    }
    public void fireContainerEvent(String type, Object data) {
        // 检查是否已经有监听器，如果没有则直接返回
        if (listeners.size() < 1)
            return;
        ContainerEvent event = new ContainerEvent(this, type, data);
        ContainerListener list[] = new ContainerListener[0];
        synchronized (listeners) {
            list = (ContainerListener[]) listeners.toArray(list);
        }
        // 遍历所有监听器并触发事件
        for (int i = 0; i < list.length; i++)
            ((ContainerListener) list[i]).containerEvent(event);
    }
    public void addListenerDef(ContainerListenerDef listenererDef) {
        synchronized (listenerDefs) {
            listenerDefs.add(listenererDef);
        }
    }

    public boolean listenerStart() {
        System.out.println("Listener Start..........");
        boolean ok = true;
        synchronized (listeners) {
            listeners.clear();
            Iterator<ContainerListenerDef> defs = listenerDefs.iterator();
            while (defs.hasNext()) {
                ContainerListenerDef def = defs.next();
                ContainerListener listener = null;
                try {
                    // 确定我们将要使用的类加载器
                    String listenerClass = def.getListenerClass();
                    ClassLoader classLoader = null;
                    classLoader = this.getLoader();
                    ClassLoader oldCtxClassLoader =
                            Thread.currentThread().getContextClassLoader();
                    // 创建这个过滤器的新实例并返回它
                    Class<?> clazz = classLoader.loadClass(listenerClass);
                    listener = (ContainerListener) clazz.newInstance();
                    addContainerListener(listener);
                } catch (Throwable t) {
                    t.printStackTrace();
                    ok = false;
                }
            }
        }
        return (ok);
    }
}

```

和前面说的一样，我们在这儿新增了addContainerListener、removeContainerListener以及fireContainerEvent三个方法，使方法名称更加具体化了。有一些不同的是我们还引入了addListenerDef方法，接受ContainerListenerDef类型的传参数。其实ContainerListenerDef和上一部分的FilterDef类似，也只是对Container监听器的属性进行定义，我们看看具体定义内容。

```java
package com.minit.core;
public final class ContainerListenerDef {
    private String description = null;
    public String getDescription() {
        return (this.description);
    }
    public void setDescription(String description) {
        this.description = description;
    }
    private String displayName = null;
    public String getDisplayName() {
        return (this.displayName);
    }
    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }
    private String listenerClass = null;
    public String getListenerClass() {
        return (this.listenerClass);
    }
    public void setListenerClass(String listenerClass) {
        this.listenerClass = listenerClass;
    }
    private String listenerName = null;
    public String getListenerName() {
        return (this.listenerName);
    }
    public void setListenerName(String listenerName) {
        this.listenerName = listenerName;
    }
    private Map<String,String> parameters = new ConcurrentHashMap<>();
    public Map<String,String> getParameterMap() {
        return (this.parameters);
    }
    public void addInitParameter(String name, String value) {
        parameters.put(name, value);
    }
    public String toString() {
        StringBuffer sb = new StringBuffer("ListenerDef[");
        sb.append("listenerName=");
        sb.append(this.listenerName);
        sb.append(", listenerClass=");
        sb.append(this.listenerClass);
        sb.append("]");
        return (sb.toString());
    }
}

```

接下来我们看看StandardSession类如何进行改造，你可以看一下新增的代码实现。代码里面增加了session监听器的处理。

```java
package com.minit.session;
public class StandardSession implements HttpSession, Session {
    private transient ArrayList<SessionListener> listeners = new ArrayList<>();
    public void addSessionListener(SessionListener listener) {
        synchronized (listeners) {
            listeners.add(listener);
        }
    }
    public void removeSessionListener(SessionListener listener) {
        synchronized (listeners) {
            listeners.remove(listener);
        }
    }
    public void fireSessionEvent(String type, Object data) {
        if (listeners.size() < 1)
            return;
        SessionEvent event = new SessionEvent(this, type, data);
        SessionListener list[] = new SessionListener[0];
        synchronized (listeners) {
            list = (SessionListener[]) listeners.toArray(list);
        }
        for (int i = 0; i < list.length; i++)
            ((SessionListener) list[i]).sessionEvent(event);
    }

    public void setId(String sessionId) {
        this.sessionid = sessionId;
        fireSessionEvent(Session.SESSION_CREATED_EVENT, null);
    }
}

```

其实也基本上类似于StandardContext。和过滤器一样，最后我们在启动类BootStrap的main函数里启动监听器就可以了，这样在服务器运行过程中则会持续监听指定事件。你可以看一下改造后BootStrap类中的main方法。

```java
package com.minit.startup;
public class BootStrap {
    public static final String WEB_ROOT =
            System.getProperty("user.dir") + File.separator + "webroot";
    private static int debug = 0;
    public static void main(String[] args) {
        if (debug >= 1)
            log(".... startup ....");
        HttpConnector connector = new HttpConnector();
        StandardContext container = new StandardContext();
        connector.setContainer(container);
        container.setConnector(connector);
        Logger logger = new FileLogger();
        container.setLogger(logger);
        FilterDef filterDef = new FilterDef();
        filterDef.setFilterName("TestFilter");
        filterDef.setFilterClass("test.TestFilter");
        container.addFilterDef(filterDef);
        FilterMap filterMap = new FilterMap();
        filterMap.setFilterName("TestFilter");
        filterMap.setURLPattern("/*");
        container.addFilterMap(filterMap);
        container.filterStart();
        ContainerListenerDef listenerDef = new ContainerListenerDef();
        listenerDef.setListenerName("TestListener");
        listenerDef.setListenerClass("test.TestListener");
        container.addListenerDef(listenerDef);
        container.listenerStart();
        container.start();
        connector.start();
    }
}

```

到这里监听器部分的改造就先告一段落，现在我们可以监听Session和Container的动态了。

同样地，在测试目录中新增TestListener，可以测试我们的功能，测试方法的实现比较简单，直接输出事件对象，能够在控制台中看到输出就可以了。

```java
package test;
import com.minit.ContainerEvent;
import com.minit.ContainerListener;
public class TestListener implements ContainerListener{
    @Override
    public void containerEvent(ContainerEvent event) {
        System.out.println(event);
    }
}

```

我们需要将 `TestFilter.java` 与 `TestListener.java` 进行编译，生成的 `.class` 文件放入webroot目录下。

## 小结

这节课我们进一步完善了MiniTomcat，新增了过滤器和事件监听器。过滤器可以在Container互相调用的时候发挥作用，对请求对象与响应对象进一步封装改造，而且通过FilterChain可以让过滤器跟链条一样串联使用。而事件监听器则可以对服务器运行过程中的Container与Session等进行持续监听，捕获它们的状态，可以对启动、超时、响应等过程进行处理。

这两种机制使我们的MiniTomcat更加易于维护和扩展，能够更好地适应各种业务需求和变化。同时，过滤器和监听器也提高了系统的灵活性和可追溯性，帮助我们更好地管理和监控服务器的运行状况。

这节课代码参见： [https://gitee.com/yaleguo1/minit-learning-demo/tree/geek\_chapter13](https://gitee.com/yaleguo1/minit-learning-demo/tree/geek_chapter13)

## 思考题

学完了这节课的内容，我们来思考一个问题：几个filter按照职责链串在一起，具体哪几段代码是用来实现链条依次调用的呢？

欢迎你把你的答案分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！