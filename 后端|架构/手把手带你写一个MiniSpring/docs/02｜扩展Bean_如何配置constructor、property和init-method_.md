你好，我是郭屹。

上节课，我们初步实现了一个MiniSpring框架，它很原始也很简单。我们实现了一个BeanFactory，作为一个容器对Bean进行管理，我们还定义了数据源接口Resource，可以将多种数据源注入Bean。

这节课，我们继续增强IoC容器，我们要做的主要有3点。

1. 增加单例Bean的接口定义，然后把所有的Bean默认为单例模式。
2. 预留事件监听的接口，方便后续进一步解耦代码逻辑。
3. 扩展BeanDefinition，添加一些属性，现在它只有id和class两个属性，我们要进一步地丰富它。

## 构建单例的Bean

首先我们来看看如何构建单例的Bean，并对该Bean进行管理。

单例（Singleton）是指某个类在整个系统内只有唯一的对象实例。只要能达到这个目的，采用什么技术手段都是可以的。常用的实现单例的方式有不下五种，因为我们构建单例的目的是深入理解Spring框架，所以我们会按照Spring的实现方式来做。

为了和Spring框架内的方法名保持一致，我们把BeanFactory接口中定义的registryBeanDefinition方法修改为registryBean，参数修改为beanName与obj。其中，obj为Object类，指代与beanName对应的Bean的信息。你可以看下修改后的BeanFactory。

```java
public interface BeanFactory {
    Object getBean(String beanName) throws BeansException;
    Boolean containsBean(String name);
    void registerBean(String beanName, Object obj);
}

```

既然要管理单例Bean，接下来我们就定义一下SingletonBeanRegistry，将管理单例Bean的方法规范好。

```java
public interface SingletonBeanRegistry {
    void registerSingleton(String beanName, Object singletonObject);
    Object getSingleton(String beanName);
    boolean containsSingleton(String beanName);
    String[] getSingletonNames();
}

```

你看这个类的名称上带有Registry字样，所以让人一眼就能知道这里面存储的就是Bean。从代码可以看到里面的方法 名称简单直接，分别对应单例的注册、获取、判断是否存在，以及获取所有的单例Bean等操作。

接口已经定义好了，接下来我们定义一个默认的实现类。这也是从Spring里学的方法，它作为一个框架并不会把代码写死，所以这里面的很多实现类都是默认的，默认是什么意思呢？就是我们可以去替换，不用这些默认的类也是可以的。我们就按照同样的方法，来为我们的默认实现类取个名字DefaultSingletonBeanRegistry。

```java
public class DefaultSingletonBeanRegistry implements SingletonBeanRegistry {
    //容器中存放所有bean的名称的列表
    protected List<String> beanNames = new ArrayList<>();
    //容器中存放所有bean实例的map
    protected Map<String, Object> singletons = new ConcurrentHashMap<>(256);

    public void registerSingleton(String beanName, Object singletonObject) {
        synchronized (this.singletons) {
            this.singletons.put(beanName, singletonObject);
            this.beanNames.add(beanName);
        }
    }
    public Object getSingleton(String beanName) {
        return this.singletons.get(beanName);
    }
    public boolean containsSingleton(String beanName) {
        return this.singletons.containsKey(beanName);
    }
    public String[] getSingletonNames() {
        return (String[]) this.beanNames.toArray();
    }
    protected void removeSingleton(String beanName) {
        synchronized (this.singletons) {
            this.beanNames.remove(beanName);
            this.singletons.remove(beanName);
        }
    }
}

```

我们在默认的这个类中，定义了beanNames列表和singletons的映射关系，beanNames用于存储所有单例Bean的别名，singletons则存储Bean名称和实现类的映射关系。

这段代码中要留意的是，我们将 singletons 定义为了一个ConcurrentHashMap，而且在实现 registrySingleton 时前面加了一个关键字synchronized。这一切都是为了确保在多线程并发的情况下，我们仍然能安全地实现对单例Bean的管理，无论是单线程还是多线程，我们整个系统里面这个Bean总是唯一的、单例的。

还记得我们有SimpleBeanFactory这样一个简单的BeanFactory实现类吗？接下来我们修改这个类，让它继承上一步创建的DefaultSingletonBeanRegistry，确保我们通过SimpleBeanFactory创建的Bean默认就是单例的，这也和Spring本身的处理方式一致。

```java
public class SimpleBeanFactory extends DefaultSingletonBeanRegistry implements BeanFactory{
    private Map<String, BeanDefinition> beanDefinitions = new ConcurrentHashMap<>(256);
    public SimpleBeanFactory() {
    }

    //getBean，容器的核心方法
    public Object getBean(String beanName) throws BeansException {
        //先尝试直接拿bean实例
        Object singleton = this.getSingleton(beanName);
        //如果此时还没有这个bean的实例，则获取它的定义来创建实例
        if (singleton == null) {
            //获取bean的定义
            BeanDefinition beanDefinition = beanDefinitions.get(beanName);
            if (beanDefinition == null) {
                throw new BeansException("No bean.");
            }
            try {
                singleton = Class.forName(beanDefinition.getClassName()).newInstance();
            }
            //新注册这个bean实例
            this.registerSingleton(beanName, singleton);
        }
        return singleton;
    }
    public void registerBeanDefinition(BeanDefinition beanDefinition) {
        this.beanDefinitions.put(beanDefinition.getId(), beanDefinition);
    }
    public Boolean containsBean(String name) {
        return containsSingleton(name);
    }
    public void registerBean(String beanName, Object obj) {
        this.registerSingleton(beanName, obj);
    }
}

```

我们对 SimpleBeanFactory 的主要改动是增加了对containsBean和registerBean的实现。通过代码可以看出，这两处实现都是对单例Bean的操作。

这部分还有两个类需要调整：ClassPathXmlApplicationContext和XmlBeanDefinitionReader。其中ClassPathXmlApplicationContext里增加了对containsBean和registerBean的实现。

```java
public Boolean containsBean(String name) {
    return this.beanFactory.containsBean(name);
}
public void registerBean(String beanName, Object obj) {
    this.beanFactory.registerBean(beanName, obj);
}

```

XmlBeanDefinitionReader调整后如下：

```java
public class XmlBeanDefinitionReader {
    SimpleBeanFactory simpleBeanFactory;
    public XmlBeanDefinitionReader(SimpleBeanFactory simpleBeanFactory) {
        this.simpleBeanFactory = simpleBeanFactory;
    }
    public void loadBeanDefinitions(Resource resource) {
        while (resource.hasNext()) {
            Element element = (Element) resource.next();
            String beanID = element.attributeValue("id");
            String beanClassName = element.attributeValue("class");
            BeanDefinition beanDefinition = new BeanDefinition(beanID, beanClassName);
            this.simpleBeanFactory.registerBeanDefinition(beanDefinition);
        }
    }
}

```

## 增加事件监听

构建好单例Bean之后，为了监控容器的启动状态，我们要增加事件监听。

我们先定义一下ApplicationEvent和ApplicationEventPublisher。通过名字可以看出，一个是用于监听应用的事件，另一个则是发布事件。

- ApplicationEventPublisher的实现

```java
public interface ApplicationEventPublisher {
    void publishEvent(ApplicationEvent event);
}

```

- ApplicationEvent的实现

```java
public class ApplicationEvent  extends EventObject {
    private static final long serialVersionUID = 1L;
    public ApplicationEvent(Object arg0) {
        super(arg0);
    }
}

```

可以看出，ApplicationEvent继承了Java工具包内的EventObject，我们是在Java的事件监听的基础上进行了简单的封装。虽然目前还没有任何实现，但这为我们后续使用观察者模式解耦代码提供了入口。

到此为止，我们进一步增强了IoC容器，还引入了两个新概念： **单例Bean和事件监听。** 其中，事件监听这部分目前只预留了入口，方便我们后续扩展。而单例Bean则是Spring框架默认的实现，我们提供了相关实现方法，并考虑到多线程高并发的场景，引入了ConcurrentHashMap来存储Bean信息。

到这一步，我们容器就变成了管理单例Bean的容器了。下面我们做一点准备工作，为后面对这些Bean注入属性值做铺垫。

## 注入

Spring中有三种属性注入的方式，分别是 **Field注入、Setter注入和构造器（Constructor）注入。** Field注入是指我们给Bean里面某个变量赋值。Setter注入是提供了一个setter方法，调用setXXX()来注入值。constructor就是在构造器/构造函数里传入参数来进行注入。Field注入我们后面会实现，这节课我们先探讨Setter注入和构造器注入两种方式。

### 配置Setter注入

首先我们来看下配置，在XML文件中我们是怎么声明使用Setter注入方式的。

```xml
<beans>
    <bean id="aservice" class="com.minis.test.AServiceImpl">
        <property type="String" name="property1" value="Hello World!"/>
    </bean>
</beans>

```

由上面的示例可以看出，我们在 `<bean>` 标签下引入了 `<property>` 标签，它又包含了type、name和value，分别对应属性类型、属性名称以及赋值。你可以看一下这个Bean的代码。

```java
public class AServiceImpl {
  private String property1;

  public void setProperty1(String property1) {
    this.property1 = property1;
  }
}

```

### 配置构造器注入

接下来我们再看看怎么声明构造器注入，同样是在XML里配置。

```xml
<beans>
    <bean id="aservice" class="com.minis.test.AServiceImpl">
      <constructor-arg type="String" name="name" value="abc"/>
      <constructor-arg type="int" name="level" value="3"/>
    </bean>
</beans>

```

可以看到，与Setter注入类似，我们只是把 `<property>` 标签换成了 `<constructor-args>` 标签。

```java
public class AServiceImpl {

  private String name;
  private int level;

  public AServiceImpl(String name, int level) {
    this.name = name;
    this.level = level;
  }
}

```

由上述两种方式可以看出， **注入操作的本质，就是给Bean的各个属性进行赋值。** 具体方式取决于实际情况，哪一种更便捷就可以选择哪一种。如果采用构造器注入的方式满足不了对域的赋值，也可以将构造器注入和Setter注入搭配使用。

```xml
<beans>
    <bean id="aservice" class="com.minis.test.AServiceImpl">
        <constructor-arg type="String" name="name" value="abc"/>
        <constructor-arg type="int" name="level" value="3"/>
        <property type="String" name="property1" value="Someone says"/>
        <property type="String" name="property2" value="Hello World!"/>
    </bean>
</beans>

```

现在我们已经明确了 `<property>` 和 `<constructor-args>` 标签的定义，但是只有外部的XML文件配置定义肯定是不行的，还要去实现。这就是我们接下来需要完成的工作。

## 实现属性类

与这个定义相关，我们要配置对应的属性类，分别命名为ArgumentValue和PropertyValue。

```java
public class ArgumentValue {
    private Object value;
    private String type;
    private String name;
    public ArgumentValue(Object value, String type) {
        this.value = value;
        this.type = type;
    }
    public ArgumentValue(Object value, String type, String name) {
        this.value = value;
        this.type = type;
        this.name = name;
    }
    //省略getter和setter
}

```

```java
public class PropertyValue {
    private final String name;
    private final Object value;
    public PropertyValue(String name, Object value) {
        this.name = name;
        this.value = value;
    }
    //省略getter
}

```

我们看Value这个词，后面不带“s”就表示他只是针对的某一个属性或者某一个参数，但一个Bean里面有很多属性、很多参数，所以我们就需要一个带“s”的集合类。 在Spring中也是这样的，所以我们参考Spring的方法，提供了ArgumentValues和PropertyValues两个类，封装、 增加、获取、判断等操作方法，简化调用。既给外面提供单个的参数/属性的对象，也提供集合对象。

- ArgumentValues类

```java
public class ArgumentValues {
    private final Map<Integer, ArgumentValue> indexedArgumentValues = new HashMap<>(0);
    private final List<ArgumentValue> genericArgumentValues = new LinkedList<>();
    public ArgumentValues() {
    }
    private void addArgumentValue(Integer key, ArgumentValue newValue) {
        this.indexedArgumentValues.put(key, newValue);
    }
    public boolean hasIndexedArgumentValue(int index) {
        return this.indexedArgumentValues.containsKey(index);
    }
    public ArgumentValue getIndexedArgumentValue(int index) {
        return this.indexedArgumentValues.get(index);
    }
    public void addGenericArgumentValue(Object value, String type) {
        this.genericArgumentValues.add(new ArgumentValue(value, type));
    }
    private void addGenericArgumentValue(ArgumentValue newValue) {
        if (newValue.getName() != null) {
            for (Iterator<ArgumentValue> it =
                 this.genericArgumentValues.iterator(); it.hasNext(); ) {
                ArgumentValue currentValue = it.next();
                if (newValue.getName().equals(currentValue.getName())) {
                    it.remove();
                }
            }
        }
        this.genericArgumentValues.add(newValue);
    }
    public ArgumentValue getGenericArgumentValue(String requiredName) {
        for (ArgumentValue valueHolder : this.genericArgumentValues) {
            if (valueHolder.getName() != null && (requiredName == null || !valueHolder.getName().equals(requiredName))) {
                continue;
            }
            return valueHolder;
        }
        return null;
    }
    public int getArgumentCount() {
        return this.genericArgumentValues.size();
    }
    public boolean isEmpty() {
        return this.genericArgumentValues.isEmpty();
    }
}

```

- PropertyValues类

```java
public class PropertyValues {
    private final List<PropertyValue> propertyValueList;
    public PropertyValues() {
        this.propertyValueList = new ArrayList<>(0);
    }
    public List<PropertyValue> getPropertyValueList() {
        return this.propertyValueList;
    }
    public int size() {
        return this.propertyValueList.size();
    }
    public void addPropertyValue(PropertyValue pv) {
        this.propertyValueList.add(pv);
    }
    public void addPropertyValue(String propertyName, Object propertyValue) {
        addPropertyValue(new PropertyValue(propertyName, propertyValue));
    }
    public void removePropertyValue(PropertyValue pv) {
        this.propertyValueList.remove(pv);
    }
    public void removePropertyValue(String propertyName) {
        this.propertyValueList.remove(getPropertyValue(propertyName));
    }
    public PropertyValue[] getPropertyValues() {
        return this.propertyValueList.toArray(new PropertyValue[this.propertyValueList.size()]);
    }
    public PropertyValue getPropertyValue(String propertyName) {
        for (PropertyValue pv : this.propertyValueList) {
            if (pv.getName().equals(propertyName)) {
                return pv;
            }
        }
        return null;
    }
    public Object get(String propertyName) {
        PropertyValue pv = getPropertyValue(propertyName);
        return pv != null ? pv.getValue() : null;
    }
    public boolean contains(String propertyName) {
        return getPropertyValue(propertyName) != null;
    }
    public boolean isEmpty() {
        return this.propertyValueList.isEmpty();
    }
}

```

上面这些代码整体还是比较简单的，根据各个封装方法的名称，也基本能明确它们的用途，这里就不再赘述了。对于构造器注入和Setter注入两种方式，这里我们只是初步定义相关类，做一点准备，后面我们将实现具体解析以及注入的过程。

接下来，我们还要做两件事。

1. 扩展BeanDefinition的属性，在原有id与name两个属性的基础上，新增lazyInit、dependsOn、initMethodName等属性。
2. 继续扩展BeanFactory接口，增强对Bean的处理能力。

## 扩展BeanDefinition

我们先给BeanDefinition和BeanFactory增加新的接口，新增接口基本上是适配BeanDefinition新增属性的。

我们给BeanDefinition类添加了哪些属性呢？一起来看下。

```java
public class BeanDefinition {
    String SCOPE_SINGLETON = "singleton";
    String SCOPE_PROTOTYPE = "prototype";
    private boolean lazyInit = false;
    private String[] dependsOn;
    private ArgumentValues constructorArgumentValues;
    private PropertyValues propertyValues;
    private String initMethodName;
    private volatile Object beanClass;
    private String id;
    private String className;
    private String scope = SCOPE_SINGLETON;
    public BeanDefinition(String id, String className) {
        this.id = id;
        this.className = className;
    }
    //省略getter和setter
}

```

从上面代码可以看出，之前我们只有id和className属性，现在增加了scope属性，表示bean是单例模式还是原型模式，还增加了lazyInit属性，表示Bean要不要在加载的时候初始化，以及初始化方法initMethodName的声明，当一个Bean构造好并实例化之后是否要让框架调用初始化方法。还有dependsOn属性记录Bean之间的依赖关系，最后还有构造器参数和property列表。

## 集中存放BeanDefinition

接下来，我们新增BeanDefinitionRegistry接口。它类似于一个存放BeanDefinition的仓库，可以存放、移除、获取及判断BeanDefinition对象。所以，我们初步定义四个接口对应这四个功能，分别是register、remove、get、contains。

```java
public interface BeanDefinitionRegistry {
    void registerBeanDefinition(String name, BeanDefinition bd);
    void removeBeanDefinition(String name);
    BeanDefinition getBeanDefinition(String name);
    boolean containsBeanDefinition(String name);
}

```

随后调整BeanFactory，新增Singleton、Prototype的判断，获取Bean的类型。

```java
public interface BeanFactory {
    Object getBean(String name) throws BeansException;
    boolean containsBean(String name);
    boolean isSingleton(String name);
    boolean isPrototype(String name);
    Class<?> getType(String name);
}

```

通过代码可以看到，我们让SimpleBeanFactory实现了BeanDefinitionRegistry，这样SimpleBeanFactory既是一个工厂同时也是一个仓库，你可以看下调整后的部分代码。

```java
public class SimpleBeanFactory extends DefaultSingletonBeanRegistry implements BeanFactory, BeanDefinitionRegistry{
    private Map<String, BeanDefinition> beanDefinitionMap = new ConcurrentHashMap<>(256);
    private List<String> beanDefinitionNames = new ArrayList<>();

    public void registerBeanDefinition(String name, BeanDefinition beanDefinition) {
        this.beanDefinitionMap.put(name, beanDefinition);
        this.beanDefinitionNames.add(name);
        if (!beanDefinition.isLazyInit()) {
            try {
                getBean(name);
            } catch (BeansException e) {
            }
        }
    }
    public void removeBeanDefinition(String name) {
        this.beanDefinitionMap.remove(name);
        this.beanDefinitionNames.remove(name);
        this.removeSingleton(name);
    }
    public BeanDefinition getBeanDefinition(String name) {
        return this.beanDefinitionMap.get(name);
    }
    public boolean containsBeanDefinition(String name) {
        return this.beanDefinitionMap.containsKey(name);
    }
    public boolean isSingleton(String name) {
        return this.beanDefinitionMap.get(name).isSingleton();
    }
    public boolean isPrototype(String name) {
        return this.beanDefinitionMap.get(name).isPrototype();
    }
    public Class<?> getType(String name) {
        return this.beanDefinitionMap.get(name).getClass();
    }
}

```

修改完BeanFactory这个核心之后，上层对应的 ClassPathXmlApplicationContext部分作为外部集成包装也需要修改。

```java
public class ClassPathXmlApplicationContext implements BeanFactory,
ApplicationEventPublisher{
    public void publishEvent(ApplicationEvent event) {
    }
    public boolean isSingleton(String name) {
        return false;
    }
    public boolean isPrototype(String name) {
        return false;
    }
    public Class<?> getType(String name) {
        return null;
    }
}

```

## 小结

![](https://static001.geekbang.org/resource/image/48/8d/4868fb2cc4f11bd1e578c9c68430d58d.jpg?wh=3736x2085)

这节课，我们模仿Spring构造了单例Bean，还增加了容器事件监听处理，完善了BeanDefinition的属性。此外，参照Spring的实现，我们增加了一些有用的特性，例如lazyInit，initMethodName等等，BeanFactory也做了相应的修改。同时，我们还提前为构造器注入、Setter注入提供了基本的实例类，这为后面实现上述两种依赖注入方式提供了基础。

通过对上一节课原始IoC容器的扩展和丰富，它已经越来越像Spring框架了。

完整源代码参见 [https://github.com/YaleGuo/minis](https://github.com/YaleGuo/minis)

## 课后题

学完这节课，我也给你留一道思考题。你认为构造器注入和Setter注入有什么异同？它们各自的优缺点是什么？欢迎你在留言区与我交流讨论，也欢迎你把这节课分享给需要的朋友。我们下节课见！