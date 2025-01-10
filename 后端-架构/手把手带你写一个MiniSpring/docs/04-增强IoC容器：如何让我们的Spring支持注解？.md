你好，我是郭屹。

上节课我们通过一系列的操作使XML使配置文件生效，然后实现了Spring中Bean的构造器注入与setter注入，通过引入“早期毛胚Bean”的概念解决了循环依赖的问题，我们还为容器增加了Spring中的一个核心方法refresh()，作为整个容器启动的入口。现在我们的容器已经初具模型了，那如何让它变得更强大，从种子长成一株幼苗呢？

这节课我们就来实现一个增强版的IoC容器，支持通过注解的方式进行依赖注入。注解是我们在编程中常用的技术，可以减少配置文件的内容，便于管理的同时还能提高开发效率。所以这节课我们将 **实现Autowired注解，并用这个方式进行依赖注入**。

## 目录结构

我们手写MiniSpring的目的是更好地学习Spring。因此，我们会时不时回头来整理整个项目的目录结构，和Spring保持一致。

现在我们先参考Spring框架的结构，来调整我们的项目结构，在beans目录下新增factory目录，factory目录中则新增xml、support、config与annotation四个目录。

```java
├── beans
│   └── factory
│       ├── xml
│       └── support
│       └── config
│       └── annotation

```

接下来将之前所写的类文件移动至新增目录下，你可以看一下移动后的结构。

```java
factory —— BeanFactory.java
factory.xml —— XmlBeanDefinitionReader.java
factory.support —— DefaultSingletonBeanRegistry.java、
BeanDefinitionRegistry.java、SimpleBeanFactory.java
factory.config —— SingletonBeanRegistry.java、ConstructorArgumentValues.java、
ConstructorArgumentValue.java、BeanDefinition.java

// 注：
// ConstructorArgumentValues由ArgumentValues改名而来
// ConstructorArgumentValue由ArgumentValue改名而来

```

熟悉了这个项目结构后，你再回头去看Spring框架的结构，会发现它们是一样的，不光目录一样，文件名也是一样的，类中的主要方法名和属性名也是一样的。我这么做的目的是便于你之后自己继续学习。

## 注解支持

如果你用过Spring的话，对Autowired注解想必不陌生，这也是常用的依赖注入的方式，在需要注入的对象上增加@Autowired注解就可以了，你可以参考下面这个例子。

```java
public class Test {
  @Autowired
  private TestAutowired testAutowired;
}

```

这种方式的好处在于，不再需要显式地在XML配置文件中使用ref属性，指定需要依赖的对象，直接在代码中加上这个注解，就能起到同样的依赖注入效果。但是你要知道，计算机运行程序是机械式的，并没有魔法，加的这一行注解不会自我解释，必须有另一个程序去解释它，否则注解就变成了注释。

那么，问题就来了， **我们要在哪一段程序、哪个时机去解释这个注解呢？**

简单分析一下，这个注解是作用在一个实例变量上的，为了生效，我们首先必须创建好这个对象，也就是在createBean时机之后。

回顾前面几节课的内容，我们通过一个refresh()方法包装了整个Bean的创建过程，我们能看到在创建Bean实例之后，要进行初始化工作，refresh()方法内预留了postProcessBeforeInitialization、init-method与postProcessAfterInitialization的位置，根据它们的名称也能看出是在初始化前、中、后分别对Bean进行处理。这里就是很好的时机。

接下来我们一起看看这些功能是如何实现的。

在这个预留的位置，我们可以考虑调用一个Bean处理器Processor，由处理器来解释注解。我们首先来定义BeanPostProcessor，它内部的两个方法分别用于Bean初始化之前和之后。

1. Bean初始化之前

```java
public interface BeanPostProcessor {
    Object postProcessBeforeInitialization(Object bean, String beanName) throws
BeansException;
}

```

2. Bean初始化之后

```java
public interface BeanPostProcessor {
    Object postProcessAfterInitialization(Object bean, String beanName) throws
BeansException;
}

```

接下来我们定义Autowired注解，很简单，你可以参考一下。

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Autowired {
}

```

根据这个定义可以知道，Autowired修饰成员变量（属性），并且在运行时生效。

为了实现@Autowired这个注解，我们很自然地会想到，利用反射获取所有标注了Autowired注解的成员变量，把它初始化成一个Bean，然后注入属性。结合前面我们定义的BeanPostProcessor接口，我们来定义Autowired的处理类AutowiredAnnotationBeanPostProcessor。

```java
public class AutowiredAnnotationBeanPostProcessor implements BeanPostProcessor {
    private AutowireCapableBeanFactory beanFactory;

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName)
throws BeansException {
        Object result = bean;

        Class<?> clazz = bean.getClass();
        Field[] fields = clazz.getDeclaredFields();
        if(fields!=null){
            //对每一个属性进行判断，如果带有@Autowired注解则进行处理
            for(Field field : fields){
                boolean isAutowired =
field.isAnnotationPresent(Autowired.class);
                if(isAutowired){
                    //根据属性名查找同名的bean
                    String fieldName = field.getName();
                    Object autowiredObj =
this.getBeanFactory().getBean(fieldName);
                    //设置属性值，完成注入
                    try {
                        field.setAccessible(true);
                        field.set(bean, autowiredObj);
                        System.out.println("autowire " + fieldName + " for bean
" + beanName);
                    }
                }
            }
        }
        return result;
    }
    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName)
throws BeansException {
        return null;
    }
    public AutowireCapableBeanFactory getBeanFactory() {
        return beanFactory;
    }
    public void setBeanFactory(AutowireCapableBeanFactory beanFactory) {
        this.beanFactory = beanFactory;
    }
}

```

其实，核心代码就只有几行。

```java
boolean isAutowired = field.isAnnotationPresent(Autowired.class);
if(isAutowired){
    String fieldName = field.getName();
    Object autowiredObj =  this.getBeanFactory().getBean(fieldName);
    field.setAccessible(true);
    field.set(bean, autowiredObj);

```

判断类里面的每一个属性是不是带有Autowired注解，如果有，就根据属性名获取Bean。从这里我们可以看出，属性名字很关键，我们就是靠它来获取和创建的Bean。有了Bean之后，我们通过反射设置属性值，完成依赖注入。

## 新的BeanFactory

在这里我们引入了AutowireCapableBeanFactory，这个BeanFactory就是专为Autowired注入的Bean准备的。

在此之前我们已经定义了BeanFactory接口，以及一个SimpleBeanFactory的实现类。现在我们又需要引入另外一个BeanFactory—— **AutowireCapableBeanFactory**。基于代码复用、解耦的原则，我们可以对通用部分代码进行抽象，抽象出一个AbstractBeanFactory类。

目前，我们可以把refresh()、getBean()、registerBeanDefinition()等方法提取到抽象类，因为我们提供了默认实现，确保这些方法即使不再被其他BeanFactory实现也能正常生效。改动比较大，所以这里我贴出完整的类代码，下面就是AbstractBeanFactory的完整实现。

```java
public abstract class AbstractBeanFactory extends DefaultSingletonBeanRegistry
implements BeanFactory, BeanDefinitionRegistry {
    private Map<String, BeanDefinition> beanDefinitionMap = new
ConcurrentHashMap<>(256);
    private List<String> beanDefinitionNames = new ArrayList<>();
    private final Map<String, Object> earlySingletonObjects = new HashMap<>(16);
    public AbstractBeanFactory() {
    }
    public void refresh() {
        for (String beanName : beanDefinitionNames) {
            try {
                getBean(beanName);
            }
        }
    }
    @Override
    public Object getBean(String beanName) throws BeansException {
        //先尝试直接从容器中获取bean实例
        Object singleton = this.getSingleton(beanName);
        if (singleton == null) {
            //如果没有实例，则尝试从毛胚实例中获取
            singleton = this.earlySingletonObjects.get(beanName);
            if (singleton == null) {
                //如果连毛胚都没有，则创建bean实例并注册
                System.out.println("get bean null -------------- " + beanName);
                BeanDefinition beanDefinition = beanDefinitionMap.get(beanName);
                singleton = createBean(beanDefinition);
                this.registerBean(beanName, singleton);
                // 进行beanpostprocessor处理
                // step 1: postProcessBeforeInitialization
                applyBeanPostProcessorBeforeInitialization(singleton, beanName);
                // step 2: init-method
                if (beanDefinition.getInitMethodName() != null &&
!beanDefinition.equals("")) {
                    invokeInitMethod(beanDefinition, singleton);
                }
                // step 3: postProcessAfterInitialization
                applyBeanPostProcessorAfterInitialization(singleton, beanName);
            }
        }

        return singleton;
    }
    private void invokeInitMethod(BeanDefinition beanDefinition, Object obj) {
        Class<?> clz = beanDefinition.getClass();
        Method method = null;
        try {
            method = clz.getMethod(beanDefinition.getInitMethodName());
        }
        try {
            method.invoke(obj);
        }
    }
    @Override
    public Boolean containsBean(String name) {
        return containsSingleton(name);
    }
   public void registerBean(String beanName, Object obj) {
        this.registerSingleton(beanName, obj);
    }
    @Override
    public void registerBeanDefinition(String name, BeanDefinition
beanDefinition) {
        this.beanDefinitionMap.put(name, beanDefinition);
        this.beanDefinitionNames.add(name);
        if (!beanDefinition.isLazyInit()) {
            try {
                getBean(name);
            }
        }
    }
    @Override
    public void removeBeanDefinition(String name) {
        this.beanDefinitionMap.remove(name);
        this.beanDefinitionNames.remove(name);
        this.removeSingleton(name);
    }
    @Override
    public BeanDefinition getBeanDefinition(String name) {
        return this.beanDefinitionMap.get(name);
    }
    @Override
    public boolean containsBeanDefinition(String name) {
        return this.beanDefinitionMap.containsKey(name);
    }
    @Override
    public boolean isSingleton(String name) {
        return this.beanDefinitionMap.get(name).isSingleton();
    }
    @Override
    public boolean isPrototype(String name) {
        return this.beanDefinitionMap.get(name).isPrototype();
    }
    @Override
    public Class<?> getType(String name) {
        return this.beanDefinitionMap.get(name).getClass();
    }
    private Object createBean(BeanDefinition beanDefinition) {
        Class<?> clz = null;
        //创建毛胚bean实例
        Object obj = doCreateBean(beanDefinition);
        //存放到毛胚实例缓存中
        this.earlySingletonObjects.put(beanDefinition.getId(), obj);
        try {
            clz = Class.forName(beanDefinition.getClassName());
        }
        //完善bean，主要是处理属性
        populateBean(beanDefinition, clz, obj);
        return obj;
    }
    //doCreateBean创建毛胚实例，仅仅调用构造方法，没有进行属性处理
    private Object doCreateBean(BeanDefinition beanDefinition) {
        Class<?> clz = null;
        Object obj = null;
        Constructor<?> con = null;
        try {
            clz = Class.forName(beanDefinition.getClassName());
            // handle constructor
            ConstructorArgumentValues constructorArgumentValues =
beanDefinition.getConstructorArgumentValues();
            if (!constructorArgumentValues.isEmpty()) {
                Class<?>[] paramTypes = new Class<?>
[constructorArgumentValues.getArgumentCount()];
                Object[] paramValues = new
Object[constructorArgumentValues.getArgumentCount()];
                for (int i = 0; i <
constructorArgumentValues.getArgumentCount(); i++) {
                    ConstructorArgumentValue constructorArgumentValue =
constructorArgumentValues.getIndexedArgumentValue(i);
                    if ("String".equals(constructorArgumentValue.getType()) ||
"java.lang.String".equals(constructorArgumentValue.getType())) {
                        paramTypes[i] = String.class;
                        paramValues[i] = constructorArgumentValue.getValue();
                    } else if
("Integer".equals(constructorArgumentValue.getType()) ||
"java.lang.Integer".equals(constructorArgumentValue.getType())) {
                        paramTypes[i] = Integer.class;
                        paramValues[i] = Integer.valueOf((String)
constructorArgumentValue.getValue());
                    } else if ("int".equals(constructorArgumentValue.getType()))
{
                        paramTypes[i] = int.class;
                        paramValues[i] = Integer.valueOf((String)
constructorArgumentValue.getValue());
                    } else {
                        paramTypes[i] = String.class;
                        paramValues[i] = constructorArgumentValue.getValue();
                    }
                }
                try {
                    con = clz.getConstructor(paramTypes);
                    obj = con.newInstance(paramValues);
                }
            }
        }
        System.out.println(beanDefinition.getId() + " bean created. " +
beanDefinition.getClassName() + " : " + obj.toString());
        return obj;
    }
    private void populateBean(BeanDefinition beanDefinition, Class<?> clz,
Object obj) {
        handleProperties(beanDefinition, clz, obj);
    }
    private void handleProperties(BeanDefinition beanDefinition, Class<?> clz,
Object obj) {
        // handle properties
        System.out.println("handle properties for bean : " +
beanDefinition.getId());
        PropertyValues propertyValues = beanDefinition.getPropertyValues();
        //如果有属性
        if (!propertyValues.isEmpty()) {
            for (int i = 0; i < propertyValues.size(); i++) {
                PropertyValue propertyValue =
propertyValues.getPropertyValueList().get(i);
                String pType = propertyValue.getType();
                String pName = propertyValue.getName();
                Object pValue = propertyValue.getValue();
                boolean isRef = propertyValue.getIsRef();
                Class<?>[] paramTypes = new Class<?>[1];
                Object[] paramValues = new Object[1];
                if (!isRef) { //如果不是ref，只是普通属性
                    //对每一个属性，分数据类型分别处理
                    if ("String".equals(pType) ||
"java.lang.String".equals(pType)) {
                        paramTypes[0] = String.class;
                    } else if ("Integer".equals(pType) ||
"java.lang.Integer".equals(pType)) {
                        paramTypes[i] = Integer.class;
                    } else if ("int".equals(pType)) {
                        paramTypes[i] = int.class;
                    } else {
                        paramTypes[i] = String.class;
                    }
                    paramValues[0] = pValue;
                } else {//is ref, create the dependent beans
                    try {
                        paramTypes[0] = Class.forName(pType);
                    }
                    try {//再次调用getBean创建ref的bean实例
                        paramValues[0] = getBean((String) pValue);
                    }
                }
                //按照setXxxx规范查找setter方法，调用setter方法设置属性
                String methodName = "set" + pName.substring(0, 1).toUpperCase()
+ pName.substring(1);
                Method method = null;
                try {
                    method = clz.getMethod(methodName, paramTypes);
                }
                try {
                    method.invoke(obj, paramValues);
                }
            }
        }
    }
    abstract public Object applyBeanPostProcessorBeforeInitialization(Object
existingBean, String beanName) throws BeansException;
    abstract public Object applyBeanPostProcessorAfterInitialization(Object
existingBean, String beanName) throws BeansException;
}

```

上面的代码较长，但仔细一看可以发现绝大多数是我们原本已经实现的方法，只是移动到了AbstractBeanFactory这个抽象类之中。最关键的代码是getBean()中的这一段。

```java
BeanDefinition beanDefinition = beanDefinitionMap.get(beanName);
singleton = createBean(beanDefinition);
this.registerBean(beanName, singleton);

// beanpostprocessor
// step 1: postProcessBeforeInitialization
applyBeanPostProcessorBeforeInitialization(singleton, beanName);
// step 2: init-method
if (beanDefinition.getInitMethodName() != null &&
!beanDefinition.equals("")) {
    invokeInitMethod(beanDefinition, singleton);
}
// step 3: postProcessAfterInitialization
applyBeanPostProcessorAfterInitialization(singleton, beanName);

```

先获取Bean的定义，然后创建Bean实例，再进行Bean的后处理并初始化。在这个抽象类里，我们需要关注两个核心的改动。

1. 定义了抽象方法applyBeanPostProcessorBeforeInitialization与applyBeanPostProcessorAfterInitialization，由名字可以看出，分别是在Bean处理类初始化之前和之后执行的方法。这两个方法交给具体的继承类去实现。
2. 在getBean()方法中，在以前预留的位置，实现了对Bean初始化前、初始化和初始化后的处理。

```java
  // step 1: postProcessBeforeInitialization
  applyBeanPostProcessorBeforeInitialization(singleton, beanName);
  // step 2: init-method
  if (beanDefinition.getInitMethodName() != null && !beanDefinition.equals("")) {
      invokeInitMethod(beanDefinition, singleton);
  }
  // step 3: postProcessAfterInitialization
  applyBeanPostProcessorAfterInitialization(singleton, beanName);

```

现在已经抽象出了一个AbstractBeanFactory，接下来我们看看具体的AutowireCapableBeanFactory是如何实现的。

```java
public class AutowireCapableBeanFactory extends AbstractBeanFactory{
    private final List<AutowiredAnnotationBeanPostProcessor> beanPostProcessors =
new ArrayList<>();
    public void addBeanPostProcessor(AutowiredAnnotationBeanPostProcessor
beanPostProcessor) {
        this.beanPostProcessors.remove(beanPostProcessor);
        this.beanPostProcessors.add(beanPostProcessor);
    }
    public int getBeanPostProcessorCount() {
        return this.beanPostProcessors.size();
    }
    public List<AutowiredAnnotationBeanPostProcessor> getBeanPostProcessors() {
        return this.beanPostProcessors;
    }
    public Object applyBeanPostProcessorsBeforeInitialization(Object
existingBean, String beanName) throws BeansException {
        Object result = existingBean;
        for (AutowiredAnnotationBeanPostProcessor beanProcessor :
getBeanPostProcessors()) {
            beanProcessor.setBeanFactory(this);
            result = beanProcessor.postProcessBeforeInitialization(result,
beanName);
            if (result == null) {
                return result;
            }
        }
        return result;
    }
    public Object applyBeanPostProcessorsAfterInitialization(Object existingBean,
String beanName) throws BeansException {
        Object result = existingBean;
        for (BeanPostProcessor beanProcessor : getBeanPostProcessors()) {
            result = beanProcessor.postProcessAfterInitialization(result,
beanName);
            if (result == null) {
                return result;
            }
        }
        return result;
    }
}

```

从代码里也可以看出，它实现起来并不复杂，用一个列表beanPostProcessors记录所有的Bean处理器，这样可以按照需求注册若干个不同用途的处理器，然后调用处理器。

```java
for (AutowiredAnnotationBeanPostProcessor beanProcessor :
getBeanPostProcessors()) {
    beanProcessor.setBeanFactory(this);
    result = beanProcessor.postProcessBeforeInitialization(result,
beanName);
}

```

代码一目了然，就是对每个Bean处理器，调用方法postProcessBeforeInitialization。

最后则是调整ClassPathXmlApplicationContext，引入的成员变量由SimpleBeanFactory改为新建的AutowireCapableBeanFactory，并在构造函数里增加上下文刷新逻辑。

```java
public ClassPathXmlApplicationContext(String fileName, boolean isRefresh) {
        Resource resource = new ClassPathXmlResource(fileName);
        AutowireCapableBeanFactory beanFactory = new
AutowireCapableBeanFactory();
        XmlBeanDefinitionReader reader = new
XmlBeanDefinitionReader(beanFactory);
        reader.loadBeanDefinitions(resource);
        this.beanFactory = beanFactory;
        if (isRefresh) {
            try {
                refresh();
            }
        }
    }

    public List<BeanFactoryPostProcessor> getBeanFactoryPostProcessors() {
        return this.beanFactoryPostProcessors;
    }
    public void addBeanFactoryPostProcessor(BeanFactoryPostProcessor
postProcessor) {
        this.beanFactoryPostProcessors.add(postProcessor);
    }
    public void refresh() throws BeansException, IllegalStateException {
        // Register bean processors that intercept bean creation.
        registerBeanPostProcessors(this.beanFactory);
        // Initialize other special beans in specific context subclasses.
        onRefresh();
    }
    private void registerBeanPostProcessors(AutowireCapableBeanFactory
beanFactory) {
        beanFactory.addBeanPostProcessor(new
AutowiredAnnotationBeanPostProcessor());
    }
    private void onRefresh() {
        this.beanFactory.refresh();
    }

```

新的refresh()方法，会先注册BeanPostProcessor，这样BeanFactory里就有解释注解的处理器了，然后在getBean()的过程中使用它。

最后，我们来回顾一下完整的过程。

1. 启动ClassPathXmlApplicationContext容器，执行refresh()。
2. 在refresh执行过程中，调用registerBeanPostProcessors()，往BeanFactory里注册Bean处理器，如AutowiredAnnotationBeanPostProcessor。
3. 执行onRefresh()， 执行AbstractBeanFactory的refresh()方法。
4. AbstractBeanFactory的refresh()获取所有Bean的定义，执行getBean()创建Bean实例。
5. getBean()创建完Bean实例后，调用Bean处理器并初始化。

```plain
applyBeanPostProcessorBeforeInitialization(singleton, beanName);
invokeInitMethod(beanDefinition, singleton);
applyBeanPostProcessorAfterInitialization(singleton, beanName);

```

6. applyBeanPostProcessorBeforeInitialization由具体的BeanFactory，如AutowireCapableBeanFactory，来实现，这个实现也很简单，就是对BeanFactory里已经注册好的所有Bean处理器调用相关方法。

```plain
beanProcessor.postProcessBeforeInitialization(result, beanName);
beanProcessor.postProcessAfterInitialization(result, beanName);

```

7. 我们事先准备好的AutowiredAnnotationBeanPostProcessor方法里面会解释Bean中的Autowired注解。

## 测试注解

到这里，支持注解的工作就完成了，接下来就是测试Autowired注解了。在这里我们做两个改动。

1. 在测试类中增加Autowired注解。

```java
package com.minis.test;
import com.minis.beans.factory.annotation.Autowired;
public class BaseService {
    @Autowired
    private BaseBaseService bbs;
    public BaseBaseService getBbs() {
        return bbs;
    }
    public void setBbs(BaseBaseService bbs) {
        this.bbs = bbs;
    }
    public BaseService() {
    }
    public void sayHello() {
        System.out.println("Base Service says Hello");
        bbs.sayHello();
    }
}

```

2. 注释XML配置文件中关于循环依赖的配置。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<beans>
    <bean id="bbs" class="com.minis.test.BaseBaseService">
        <property type="com.minis.test.AServiceImpl" name="as" ref="aservice" />
    </bean>
    <bean id="aservice" class="com.minis.test.AServiceImpl">
        <constructor-arg type="String" name="name" value="abc"/>
        <constructor-arg type="int" name="level" value="3"/>
        <property type="String" name="property1" value="Someone says"/>
        <property type="String" name="property2" value="Hello World!"/>
        <property type="com.minis.test.BaseService" name="ref1"
ref="baseservice"/>
    </bean>
    <bean id="baseservice" class="com.minis.test.BaseService">
<!--        <property type="com.minis.test.BaseBaseService" name="bbs"
ref="basebaseservice" />-->
    </bean>
</beans>

```

## 小结

这节课我们丰富了原来的框架，支持了注解，让它更有模有样了。

注解是现代最受程序员欢迎的特性，我们通过Autowired这个注解实现了Bean的注入，这样程序员不用再在XML配置文件中手动配置property，而是在类中声明property的时候直接加上注解即可，框架使用的机制是名称匹配，这也是Spring所支持的一种匹配方式。

接着我们提取了BeanFactory接口，定义了一个抽象的AbstractBeanFactory。通过这个抽象类，将Bean工厂需要做的事情的框架搭建出来，然后在具体实现类中完善细节。这种程序结构称为interface-abstract class-class（接口抽象类），是一种做框架时常用的设计模式。

![](https://static001.geekbang.org/resource/image/14/38/141ec0beb22e6525cb3fe484be337638.jpg?wh=3569x2229)

我们自己手写MiniSpring，不仅仅是要学习一个功能如何实现，还要学习大师的做法，模仿他们的代码和设计，练习得多了就能像专业程序员一样地写代码了。

完整源代码参见 [https://github.com/YaleGuo/minis](https://github.com/YaleGuo/minis)

## 课后题

学完这节课，我也给你留一道思考题。我们实现了Autowired注解，在现有框架中能否支持多个注解？欢迎你在留言区与我交流讨论，也欢迎你把这节课分享给需要的朋友。我们下节课见！