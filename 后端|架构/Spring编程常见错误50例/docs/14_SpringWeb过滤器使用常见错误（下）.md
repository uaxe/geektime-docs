你好，我是傅健。

通过上节课的两个案例，我们了解了容器运行时过滤器的工作原理，那么这节课我们还是通过两个错误案例，来学习下容器启动时过滤器初始化以及排序注册等相关逻辑。了解了它们，你会对如何使用好过滤器更有信心。下面，我们具体来看一下。

## 案例1：@WebFilter过滤器使用@Order无效

假设我们还是基于Spring Boot去开发上节课的学籍管理系统，这里我们简单复习下上节课用到的代码。

首先，创建启动程序的代码如下：

```
@SpringBootApplication
@ServletComponentScan
@Slf4j
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
        log.info("启动成功");
    }
}

```

实现的Controller代码如下：

```
@Controller
@Slf4j
public class StudentController {
    @PostMapping("/regStudent/{name)}")
    @ResponseBody
    public String saveUser(String name) throws Exception {
        System.out.println("......用户注册成功");
        return "success";
    }
}

```

上述代码提供了一个 Restful 接口 "/regStudent"。该接口只有一个参数 name，注册成功会返回"success"。

现在，我们来实现两个新的过滤器，代码如下：

AuthFilter：例如，限制特定IP地址段（例如校园网内）的用户方可注册为新用户，当然这里我们仅仅Sleep 1秒来模拟这个过程。

```
@WebFilter
@Slf4j
@Order(2)
public class AuthFilter implements Filter {
    @SneakyThrows
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        if(isPassAuth()){
            System.out.println("通过授权");
            chain.doFilter(request, response);
        }else{
            System.out.println("未通过授权");
            ((HttpServletResponse)response).sendError(401);
        }
    }
    private boolean isPassAuth() throws InterruptedException {
        System.out.println("执行检查权限");
        Thread.sleep(1000);
        return true;
    }
}

```

TimeCostFilter：计算注册学生的执行耗时，需要包括授权过程。

```
@WebFilter
@Slf4j
@Order(1)
public class TimeCostFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        System.out.println("#开始计算接口耗时");
        long start = System.currentTimeMillis();
        chain.doFilter(request, response);
        long end = System.currentTimeMillis();
        long time = end - start;
        System.out.println("#执行时间(ms)：" + time);
    }
}

```

在上述代码中，我们使用了@Order，期望TimeCostFilter先被执行，因为TimeCostFilter设计的初衷是统计这个接口的性能，所以是需要统计AuthFilter执行的授权过程的。

全部代码实现完毕，执行结果如下：

```
执行检查权限
通过授权
#开始计算接口耗时
......用户注册成功
#执行时间(ms)：33

```

从结果来看，执行时间并不包含授权过程，所以这并不符合我们的预期，毕竟我们是加了@Order的。但是如果我们交换Order指定的值，你会发现也不见效果，为什么会如此？难道Order不能用来排序WebFilter么？下面我们来具体解析下这个问题及其背后的原理。

### 案例解析

通过上节课的学习，我们得知：当一个请求来临时，会执行到 StandardWrapperValve 的 invoke()，这个方法会创建 ApplicationFilterChain，并通过ApplicationFilterChain#doFilter() 触发过滤器执行，并最终执行到内部私有方法internalDoFilter()， 我们可以尝试在internalDoFilter()中寻找一些启示：

```
private void internalDoFilter(ServletRequest request,
                              ServletResponse response)
    throws IOException, ServletException {

    // Call the next filter if there is one
    if (pos < n) {
        ApplicationFilterConfig filterConfig = filters[pos++];
        try {
            Filter filter = filterConfig.getFilter();

```

从上述代码我们得知：过滤器的执行顺序是由类成员变量Filters决定的，而Filters变量则是createFilterChain()在容器启动时顺序遍历StandardContext中的成员变量FilterMaps获得的：

```
public static ApplicationFilterChain createFilterChain(ServletRequest request,
        Wrapper wrapper, Servlet servlet) {

    // 省略非关键代码
    // Acquire the filter mappings for this Context
    StandardContext context = (StandardContext) wrapper.getParent();
    FilterMap filterMaps[] = context.findFilterMaps();
    // 省略非关键代码
    // Add the relevant path-mapped filters to this filter chain
    for (int i = 0; i < filterMaps.length; i++) {
        if (!matchDispatcher(filterMaps[i] ,dispatcher)) {
            continue;
        }
        if (!matchFiltersURL(filterMaps[i], requestPath))
            continue;
        ApplicationFilterConfig filterConfig = (ApplicationFilterConfig)
            context.findFilterConfig(filterMaps[i].getFilterName());
        if (filterConfig == null) {
            continue;
        }
        filterChain.addFilter(filterConfig);
    }
    // 省略非关键代码
    // Return the completed filter chain
    return filterChain;
}

```

下面继续查找对StandardContext成员变量FilterMaps的写入引用，我们找到了addFilterMapBefore()：

```
public void addFilterMapBefore(FilterMap filterMap) {
    validateFilterMap(filterMap);
    // Add this filter mapping to our registered set
    filterMaps.addBefore(filterMap);
    fireContainerEvent("addFilterMap", filterMap);
}

```

到这，我们已经知道过滤器的执行顺序是由StandardContext类成员变量FilterMaps的顺序决定，而FilterMaps则是一个包装过的数组，所以我们只要进一步弄清楚 **FilterMaps中各元素的排列顺序** 即可。

我们继续在addFilterMapBefore()中加入断点，尝试从调用栈中找到一些线索：

```
addFilterMapBefore:2992, StandardContext
addMappingForUrlPatterns:107, ApplicationFilterRegistration
configure:229, AbstractFilterRegistrationBean
configure:44, AbstractFilterRegistrationBean
register:113, DynamicRegistrationBean
onStartup:53, RegistrationBean
selfInitialize:228, ServletWebServerApplicationContext
// 省略非关键代码

```

可知，Spring从selfInitialize()一直依次调用到addFilterMapBefore()，稍微分析下selfInitialize()，我们可以了解到，这里是通过调用getServletContextInitializerBeans()，获取所有的ServletContextInitializer类型的Bean，并调用该Bean的onStartup()，从而一步步以调用栈显示的顺序，最终调用到 addFilterMapBefore()。

```
private void selfInitialize(ServletContext servletContext) throws ServletException {
   prepareWebApplicationContext(servletContext);
   registerApplicationScope(servletContext);
   WebApplicationContextUtils.registerEnvironmentBeans(getBeanFactory(), servletContext);
   for (ServletContextInitializer beans : getServletContextInitializerBeans()) {
      beans.onStartup(servletContext);
   }
}

```

那么上述的selfInitialize()又从何处调用过来呢？这里你可以先想想，我会在思考题中给你做进一步解释。

现在我们继续查看selfInitialize()的细节。

首先，查看上述代码中的getServletContextInitializerBeans()，因为此方法返回的ServletContextInitializer类型的Bean集合顺序决定了addFilterMapBefore()调用的顺序，从而决定了FilterMaps内元素的顺序，最终决定了过滤器的执行顺序。

getServletContextInitializerBeans()的实现非常简单，只是返回了ServletContextInitializerBeans类的一个实例，参考代码如下：

```
protected Collection<ServletContextInitializer> getServletContextInitializerBeans() {
   return new ServletContextInitializerBeans(getBeanFactory());
}

```

上述方法的返回值是个Collection，可见ServletContextInitializerBeans类是一个集合类，它继承了AbstractCollection抽象类。也因为如此，上述selfInitialize()才可以遍历 ServletContextInitializerBeans的实例对象。

既然ServletContextInitializerBeans是集合类，那么我们就可以先查看其iterator()，看看它遍历的是什么。

```
@Override
public Iterator<ServletContextInitializer> iterator() {
   return this.sortedList.iterator();
}

```

此集合类对外暴露的集合遍历元素为sortedList成员变量，也就是说，上述selfInitialize()最终遍历的即为sortedList成员变量。

到这，我们可以进一步确定下结论：selfInitialize()中是通过getServletContextInitializerBeans()获取到的ServletContextInitializer类型的Beans集合，即为ServletContextInitializerBeans的类型成员变量sortedList。反过来说， **sortedList中的过滤器Bean元素顺序，决定了最终过滤器的执行顺序**。

现在我们继续查看ServletContextInitializerBeans的构造方法如下：

```
public ServletContextInitializerBeans(ListableBeanFactory beanFactory,
      Class<? extends ServletContextInitializer>... initializerTypes) {
   this.initializers = new LinkedMultiValueMap<>();
   this.initializerTypes = (initializerTypes.length != 0) ? Arrays.asList(initializerTypes)
         : Collections.singletonList(ServletContextInitializer.class);
   addServletContextInitializerBeans(beanFactory);
   addAdaptableBeans(beanFactory);
   List<ServletContextInitializer> sortedInitializers = this.initializers.values().stream()
         .flatMap((value) -> value.stream().sorted(AnnotationAwareOrderComparator.INSTANCE))
         .collect(Collectors.toList());
   this.sortedList = Collections.unmodifiableList(sortedInitializers);
   logMappings(this.initializers);
}

```

通过第8行，可以得知：我们关心的类成员变量this.sortedList，其元素顺序是由类成员变量this.initializers的values通过比较器AnnotationAwareOrderComparator进行排序的。

继续查看AnnotationAwareOrderComparator比较器，忽略比较器调用的细节过程，其最终是通过两种方式获取比较器需要的order值，来决定sortedInitializers的排列顺序：

- 待排序的对象元素自身实现了Order接口，则直接通过getOrder()获取order值；
- 否则执行OrderUtils.findOrder()获取该对象类@Order的属性。

这里多解释一句，因为this.initializers的values类型为ServletContextInitializer，其实现了Ordered接口，所以这里的比较器显然是使用了getOrder()获取比较器所需的order值，对应的类成员变量即为order。

继续查看this.initializers中的元素在何处被添加，我们最终得知，addServletContextInitializerBeans()以及addAdaptableBeans()这两个方法均构建了ServletContextInitializer子类的实例，并添加到了this.initializers成员变量中。在这里，我们只研究addServletContextInitializerBeans，毕竟我们使用的添加过滤器方式（使用@WebFilter标记）最终只会通过这个方法生效。

在这个方法中，Spring通过getOrderedBeansOfType()实例化了所有ServletContextInitializer的子类：

```
private void addServletContextInitializerBeans(ListableBeanFactory beanFactory) {
   for (Class<? extends ServletContextInitializer> initializerType : this.initializerTypes) {
      for (Entry<String, ? extends ServletContextInitializer> initializerBean : getOrderedBeansOfType(beanFactory,
            initializerType)) {
         addServletContextInitializerBean(initializerBean.getKey(), initializerBean.getValue(), beanFactory);
      }
   }
}

```

根据其不同类型，调用addServletContextInitializerBean()，我们可以看出ServletContextInitializer的子类包括了ServletRegistrationBean、FilterRegistrationBean以及ServletListenerRegistrationBean，正好对应了Servlet的三大要素。

而这里我们只需要关心对应于Filter的FilterRegistrationBean，显然，FilterRegistrationBean是ServletContextInitializer的子类（实现了Ordered接口），同样由 **成员变量order的值决定其执行的优先级。**

```
private void addServletContextInitializerBean(String beanName, ServletContextInitializer initializer,
      ListableBeanFactory beanFactory) {
   if (initializer instanceof ServletRegistrationBean) {
      Servlet source = ((ServletRegistrationBean<?>) initializer).getServlet();
      addServletContextInitializerBean(Servlet.class, beanName, initializer, beanFactory, source);
   }
   else if (initializer instanceof FilterRegistrationBean) {
      Filter source = ((FilterRegistrationBean<?>) initializer).getFilter();
      addServletContextInitializerBean(Filter.class, beanName, initializer, beanFactory, source);
   }
   else if (initializer instanceof DelegatingFilterProxyRegistrationBean) {
      String source = ((DelegatingFilterProxyRegistrationBean) initializer).getTargetBeanName();
      addServletContextInitializerBean(Filter.class, beanName, initializer, beanFactory, source);
   }
   else if (initializer instanceof ServletListenerRegistrationBean) {
      EventListener source = ((ServletListenerRegistrationBean<?>) initializer).getListener();
      addServletContextInitializerBean(EventListener.class, beanName, initializer, beanFactory, source);
   }
   else {
      addServletContextInitializerBean(ServletContextInitializer.class, beanName, initializer, beanFactory,
            initializer);
   }
}

```

最终添加到this.initializers成员变量中：

```
private void addServletContextInitializerBean(Class<?> type, String beanName, ServletContextInitializer initializer,
      ListableBeanFactory beanFactory, Object source) {
   this.initializers.add(type, initializer);
// 省略非关键代码
}

```

通过上述代码，我们再次看到了FilterRegistrationBean。但问题来了，我们没有定义FilterRegistrationBean，那么这里的FilterRegistrationBean是在哪里被定义的呢？其order类成员变量是否有特定的取值逻辑？

不妨回想下上节课的案例1，它是在WebFilterHandler类的doHandle()动态构建了FilterRegistrationBean的BeanDefinition：

```
class WebFilterHandler extends ServletComponentHandler {

   WebFilterHandler() {
      super(WebFilter.class);
   }

   @Override
   public void doHandle(Map<String, Object> attributes, AnnotatedBeanDefinition beanDefinition,
         BeanDefinitionRegistry registry) {
      BeanDefinitionBuilder builder = BeanDefinitionBuilder.rootBeanDefinition(FilterRegistrationBean.class);
      builder.addPropertyValue("asyncSupported", attributes.get("asyncSupported"));
      builder.addPropertyValue("dispatcherTypes", extractDispatcherTypes(attributes));
      builder.addPropertyValue("filter", beanDefinition);
      builder.addPropertyValue("initParameters", extractInitParameters(attributes));
      String name = determineName(attributes, beanDefinition);
      builder.addPropertyValue("name", name);
      builder.addPropertyValue("servletNames", attributes.get("servletNames"));
      builder.addPropertyValue("urlPatterns", extractUrlPatterns(attributes));
      registry.registerBeanDefinition(name, builder.getBeanDefinition());
   }
   // 省略非关键代码

```

这里我再次贴出了WebFilterHandler中doHandle()的逻辑（即通过 BeanDefinitionBuilder动态构建了FilterRegistrationBean类型的BeanDefinition）。然而遗憾的是， **此处并没有设置order的值，更没有根据@Order指定的值去设置。**

到这里我们终于看清楚了问题的本质，所有被@WebFilter注解的类，最终都会在此处被包装为FilterRegistrationBean类的BeanDefinition。虽然FilterRegistrationBean也拥有Ordered接口，但此处却并没有填充值，因为这里所有的属性都是从@WebFilter对应的属性获取的，而@WebFilter本身没有指定可以辅助排序的属性。

现在我们来总结下，过滤器的执行顺序是由下面这个串联决定的：

> RegistrationBean中order属性的值->
>
> ServletContextInitializerBeans类成员变量sortedList中元素的顺序->
>
> ServletWebServerApplicationContext 中selfInitialize()遍历FilterRegistrationBean的顺序->
>
> addFilterMapBefore()调用的顺序->
>
> filterMaps内元素的顺序->
>
> 过滤器的执行顺序

可见，RegistrationBean中order属性的值最终可以决定过滤器的执行顺序。但是可惜的是：当使用@WebFilter时，构建的FilterRegistrationBean并没有依据@Order的值去设置order属性，所以@Order失效了。

### 问题修正

现在，我们理清了Spring启动Web服务之前的一些必要类的初始化流程，同时也弄清楚了@Order和@WebFilter同时使用失效的原因，但这个问题想要解决却并非那么简单。

这里我先提供给你一个常见的做法，即实现自己的FilterRegistrationBean来配置添加过滤器，不再使用@WebFilter。具体代码如下：

```
@Configuration
public class FilterConfiguration {
    @Bean
    public FilterRegistrationBean authFilter() {
        FilterRegistrationBean registration = new FilterRegistrationBean();
        registration.setFilter(new AuthFilter());
        registration.addUrlPatterns("/*");
        registration.setOrder(2);
        return registration;
    }

    @Bean
    public FilterRegistrationBean timeCostFilter() {
        FilterRegistrationBean registration = new FilterRegistrationBean();
        registration.setFilter(new TimeCostFilter());
        registration.addUrlPatterns("/*");
        registration.setOrder(1);
        return registration;
    }
}

```

按照我们查看的源码中的逻辑，虽然WebFilterHandler中doHandle()构建了FilterRegistrationBean类型的BeanDefinition，但 **没有设置order的值**。

所以在这里，我们直接手工实例化了FilterRegistrationBean实例，而且设置了其setOrder()。同时不要忘记去掉AuthFilter和TimeCostFilter类中的@WebFilter，这样问题就得以解决了。

## 案例2：过滤器被多次执行

我们继续沿用上面的案例代码，要解决排序问题，可能有人就想了是不是有其他的解决方案呢？比如我们能否在两个过滤器中增加@Component，从而让@Order生效呢？代码如下。

AuthFilter：

```
@WebFilter
@Slf4j
@Order(2)
@Component
public class AuthFilter implements Filter {
    @SneakyThrows
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain){
        if(isPassAuth()){
            System.out.println("通过授权");
            chain.doFilter(request, response);
        }else{
            System.out.println("未通过授权");
            ((HttpServletResponse)response).sendError(401);
        }
    }
    private boolean isPassAuth() throws InterruptedException {
        System.out.println("执行检查权限");
        Thread.sleep(1000);
        return true;
    }
}

```

TimeCostFilter类如下：

```
@WebFilter
@Slf4j
@Order(1)
@Component
public class TimeCostFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        System.out.println("#开始计算接口耗时");
        long start = System.currentTimeMillis();
        chain.doFilter(request, response);
        long end = System.currentTimeMillis();
        long time = end - start;
        System.out.println("#执行时间(ms)：" + time);
    }
}

```

最终执行结果如下：

```
#开始计算接口耗时
执行检查权限
通过授权
执行检查权限
通过授权
#开始计算接口耗时
......用户注册成功
#执行时间(ms)：73
#执行时间(ms)：2075

```

更改 AuthFilter 类中的Order值为0，继续测试，得到结果如下：

```
执行检查权限
通过授权
#开始计算接口耗时
执行检查权限
通过授权
#开始计算接口耗时
......用户注册成功
#执行时间(ms)：96
#执行时间(ms)：1100

```

显然，通过Order的值，我们已经可以随意调整Filter的执行顺序，但是我们会惊奇地发现，过滤器本身被执行了2次，这明显不符合我们的预期！那么如何理解这个现象呢？

### 案例解析

从案例1中我们已经得知被@WebFilter的过滤器，会在WebServletHandler类中被重新包装为FilterRegistrationBean类的BeanDefinition，而并非是Filter类型。

而当我们在自定义过滤器中增加@Component时，我们可以大胆猜测下：理论上Spring会根据当前类再次包装一个新的过滤器，因而doFIlter()被执行两次。因此看似奇怪的测试结果，也在情理之中了。

我们继续从源码中寻找真相，继续查阅ServletContextInitializerBeans的构造方法如下：

```
public ServletContextInitializerBeans(ListableBeanFactory beanFactory,
      Class<? extends ServletContextInitializer>... initializerTypes) {
   this.initializers = new LinkedMultiValueMap<>();
   this.initializerTypes = (initializerTypes.length != 0) ? Arrays.asList(initializerTypes)
         : Collections.singletonList(ServletContextInitializer.class);
   addServletContextInitializerBeans(beanFactory);
   addAdaptableBeans(beanFactory);
   List<ServletContextInitializer> sortedInitializers = this.initializers.values().stream()
         .flatMap((value) -> value.stream().sorted(AnnotationAwareOrderComparator.INSTANCE))
         .collect(Collectors.toList());
   this.sortedList = Collections.unmodifiableList(sortedInitializers);
   logMappings(this.initializers);
}

```

上一个案例中，我们关注了addServletContextInitializerBeans()，了解了它的作用是实例化并注册了所有FilterRegistrationBean类型的过滤器（严格说，是实例化并注册了所有的ServletRegistrationBean、FilterRegistrationBean以及ServletListenerRegistrationBean，但这里我们只关注FilterRegistrationBean）。

而第7行的addAdaptableBeans()，其作用则是实例化所有实现Filter接口的类（严格说，是实例化并注册了所有实现Servlet、Filter以及EventListener接口的类），然后再逐一包装为FilterRegistrationBean。

之所以Spring能够直接实例化FilterRegistrationBean类型的过滤器，这是因为：

- WebFilterHandler相关类通过扫描@WebFilter，动态构建了FilterRegistrationBean类型的BeanDefinition，并注册到Spring；
- 或者我们自己使用@Bean来显式实例化FilterRegistrationBean并注册到Spring，如案例1中的解决方案。

但Filter类型的过滤器如何才能被Spring直接实例化呢？相信你已经有答案了： **任何通过@Component修饰的的类，都可以自动注册到Spring，且能被Spring直接实例化。**

现在我们直接查看addAdaptableBeans()，其调用了addAsRegistrationBean()，其beanType为Filter.class：

```
protected void addAdaptableBeans(ListableBeanFactory beanFactory) {
   // 省略非关键代码
   addAsRegistrationBean(beanFactory, Filter.class, new FilterRegistrationBeanAdapter());
   // 省略非关键代码
}

```

继续查看最终调用到的方法addAsRegistrationBean()：

```
private <T, B extends T> void addAsRegistrationBean(ListableBeanFactory beanFactory, Class<T> type,
      Class<B> beanType, RegistrationBeanAdapter<T> adapter) {
   List<Map.Entry<String, B>> entries = getOrderedBeansOfType(beanFactory, beanType, this.seen);
   for (Entry<String, B> entry : entries) {
      String beanName = entry.getKey();
      B bean = entry.getValue();
      if (this.seen.add(bean)) {
         // One that we haven't already seen
         RegistrationBean registration = adapter.createRegistrationBean(beanName, bean, entries.size());
         int order = getOrder(bean);
         registration.setOrder(order);
         this.initializers.add(type, registration);
         if (logger.isTraceEnabled()) {
            logger.trace("Created " + type.getSimpleName() + " initializer for bean '" + beanName + "'; order="
                  + order + ", resource=" + getResourceDescription(beanName, beanFactory));
         }
      }
   }
}

```

主要逻辑如下：

- 通过getOrderedBeansOfType()创建了所有 Filter 子类的实例，即所有实现Filter接口且被@Component修饰的类；
- 依次遍历这些Filter类实例，并通过RegistrationBeanAdapter将这些类包装为RegistrationBean；
- 获取Filter类实例的Order值，并设置到包装类 RegistrationBean中；
- 将RegistrationBean添加到this.initializers。

到这，我们了解到，当过滤器同时被@WebFilter和@Component修饰时，会导致两个FilterRegistrationBean实例的产生。addServletContextInitializerBeans()和addAdaptableBeans()最终都会创建FilterRegistrationBean的实例，但不同的是：

- @WebFilter会让addServletContextInitializerBeans()实例化，并注册所有动态生成的FilterRegistrationBean类型的过滤器；
- @Component会让addAdaptableBeans()实例化所有实现Filter接口的类，然后再逐一包装为FilterRegistrationBean类型的过滤器。

### 问题修正

解决这个问题提及的顺序问题，自然可以继续参考案例1的问题修正部分。另外我们也可以去掉@WebFilter保留@Component的方式进行修改，修改后的Filter示例如下：

```
//@WebFilter
@Slf4j
@Order(1)
@Component
public class TimeCostFilter implements Filter {
   //省略非关键代码
}

```

## 重点回顾

这节课我们分析了过滤器在Spring框架中注册、包装以及实例化的整个流程，最后我们再次回顾下重点。

@WebFilter和@Component的相同点是：

- 它们最终都被包装并实例化成为了FilterRegistrationBean；
- 它们最终都是在 ServletContextInitializerBeans的构造器中开始被实例化。

@WebFilter和@Component的不同点是：

- 被@WebFilter修饰的过滤器会被提前在BeanFactoryPostProcessors扩展点包装成FilterRegistrationBean类型的BeanDefinition，然后在ServletContextInitializerBeans.addServletContextInitializerBeans() 进行实例化；而使用@Component修饰的过滤器类，是在ServletContextInitializerBeans.addAdaptableBeans() 中被实例化成Filter类型后，再包装为RegistrationBean类型。
- 被@WebFilter修饰的过滤器不会注入Order属性，但被@Component修饰的过滤器会在ServletContextInitializerBeans.addAdaptableBeans() 中注入Order属性。

## 思考题

这节课的两个案例，它们都是在Tomcat容器启动时发生的，但你了解Spring是如何整合Tomcat，使其在启动时注册这些过滤器吗？

期待你的思考，我们留言区见！