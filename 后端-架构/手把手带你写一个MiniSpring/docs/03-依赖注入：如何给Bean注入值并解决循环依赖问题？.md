你好，我是郭屹，今天我们继续手写MiniSpring，探讨Bean的依赖注入。

上节课，我们定义了在XML配置文件中使用setter注入和构造器注入的配置方式，但同时也留下了一个悬念：这些配置是如何生效的呢？

## 值的注入

要理清这个问题，我们要先来看看 **Spring是如何解析 `<property>` 和 `<constructor-arg>` 标签。**

我们以下面的XML配置为基准进行学习。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<beans>
    <bean id="aservice" class="com.minis.test.AServiceImpl">
        <constructor-arg type="String" name="name" value="abc"/>
        <constructor-arg type="int" name="level" value="3"/>
        <property type="String" name="property1" value="Someone says"/>
        <property type="String" name="property2" value="Hello World!"/>
    </bean>
</beans>

```

和上面的配置属性对应，在测试类AServiceImpl中，要有相应的name、level、property1、property2字段来建立映射关系，这些实现体现在构造函数以及settter、getter等方法中。

```java
public class AServiceImpl implements AService {
    private String name;
    private int level;
    private String property1;
    private String property2;

    public AServiceImpl() {
    }
    public AServiceImpl(String name, int level) {
        this.name = name;
        this.level = level;
        System.out.println(this.name + "," + this.level);
    }
    public void sayHello() {
        System.out.println(this.property1 + "," + this.property2);
    }
    // 在此省略property1和property2的setter、getter方法
}

```

接着，简化ArgumentValues类，移除暂时未用到的方法。

```java
public class ArgumentValues {
    private final List<ArgumentValue> argumentValueList = new ArrayList<>();
    public ArgumentValues() {
    }
    public void addArgumentValue(ArgumentValue argumentValue) {
        this.argumentValueList.add(argumentValue);
    }
    public ArgumentValue getIndexedArgumentValue(int index) {
        ArgumentValue argumentValue = this.argumentValueList.get(index);
        return argumentValue;
    }
    public int getArgumentCount() {
        return (this.argumentValueList.size());
    }
    public boolean isEmpty() {
        return (this.argumentValueList.isEmpty());
    }
}

```

做完准备工作之后，我们重点来看核心工作：解析 `<property>` 和 `<constructor-arg>` 两个标签。我们要在XmlBeanDefinitionReader类中处理这两个标签。

```java
 public void loadBeanDefinitions(Resource resource) {
        while (resource.hasNext()) {
            Element element = (Element) resource.next();
            String beanID = element.attributeValue("id");
            String beanClassName = element.attributeValue("class");
            BeanDefinition beanDefinition = new BeanDefinition(beanID,
beanClassName);
            //处理属性
            List<Element> propertyElements = element.elements("property");
            PropertyValues PVS = new PropertyValues();
            for (Element e : propertyElements) {
                String pType = e.attributeValue("type");
                String pName = e.attributeValue("name");
                String pValue = e.attributeValue("value");
                PVS.addPropertyValue(new PropertyValue(pType, pName, pValue));
            }
            beanDefinition.setPropertyValues(PVS);

            //处理构造器参数
            List<Element> constructorElements = element.elements("constructor-
arg");
            ArgumentValues AVS = new ArgumentValues();
            for (Element e : constructorElements) {
                String aType = e.attributeValue("type");
                String aName = e.attributeValue("name");
                String aValue = e.attributeValue("value");
                AVS.addArgumentValue(new ArgumentValue(aType, aName, aValue));
            }
            beanDefinition.setConstructorArgumentValues(AVS);

            this.simpleBeanFactory.registerBeanDefinition(beanID,
beanDefinition);
        }
    }
}

```

从上述代码可以看出，程序在加载Bean的定义时要获取 `<property>` 和 `<constructor-arg>`，只要循环处理它们对应标签的属性：type、name、value即可。随后，我们通过addPropertyValue和addArgumentValue两个方法就能将注入的配置读取进内存。

那么，将这些配置的值读取进内存之后，我们怎么把它作为Bean的属性注入进去呢？这要求我们在创建Bean的时候就要做相应的处理，给属性赋值。针对XML配置的Value值，我们要按照数据类型分别将它们解析为字符串、整型、浮点型等基本类型。在SimpleBeanFactory类中，调整核心的createBean方法，我们修改一下。

```java
    private Object createBean(BeanDefinition beanDefinition) {
        Class<?> clz = null;
        Object obj = null;
        Constructor<?> con = null;
        try {
            clz = Class.forName(beanDefinition.getClassName());
            // 处理构造器参数
            ArgumentValues argumentValues =
beanDefinition.getConstructorArgumentValues();
            //如果有参数
            if (!argumentValues.isEmpty()) {
                Class<?>[] paramTypes = new Class<?>
[argumentValues.getArgumentCount()];
                Object[] paramValues = new
Object[argumentValues.getArgumentCount()];
                //对每一个参数，分数据类型分别处理
                for (int i = 0; i < argumentValues.getArgumentCount(); i++) {
                    ArgumentValue argumentValue =
argumentValues.getIndexedArgumentValue(i);
                    if ("String".equals(argumentValue.getType()) ||
"java.lang.String".equals(argumentValue.getType())) {
                        paramTypes[i] = String.class;
                        paramValues[i] = argumentValue.getValue();
                    } else if ("Integer".equals(argumentValue.getType()) ||
"java.lang.Integer".equals(argumentValue.getType())) {
                        paramTypes[i] = Integer.class;
                        paramValues[i] =
Integer.valueOf((String)argumentValue.getValue());
                    } else if ("int".equals(argumentValue.getType())) {
                        paramTypes[i] = int.class;
                        paramValues[i] = Integer.valueOf((String)
argumentValue.getValue());
                    } else { //默认为string
                        paramTypes[i] = String.class;
                        paramValues[i] = argumentValue.getValue();
                    }
                }
                try {
                    //按照特定构造器创建实例
                    con = clz.getConstructor(paramTypes);
                    obj = con.newInstance(paramValues);
                }
            } else { //如果没有参数，直接创建实例
                obj = clz.newInstance();
            }
        } catch (Exception e) {
        }
        // 处理属性
        PropertyValues propertyValues = beanDefinition.getPropertyValues();
        if (!propertyValues.isEmpty()) {
            for (int i = 0; i < propertyValues.size(); i++) {
                //对每一个属性，分数据类型分别处理
                PropertyValue propertyValue =
propertyValues.getPropertyValueList().get(i);
                String pType = propertyValue.getType();
                String pName = propertyValue.getName();
                Object pValue = propertyValue.getValue();
                Class<?>[] paramTypes = new Class<?>[1];
               if ("String".equals(pType) || "java.lang.String".equals(pType))
{
                    paramTypes[0] = String.class;
                } else if ("Integer".equals(pType) ||
"java.lang.Integer".equals(pType)) {
                    paramTypes[0] = Integer.class;
                } else if ("int".equals(pType)) {
                    paramTypes[0] = int.class;
                } else { // 默认为string
                    paramTypes[0] = String.class;
                }
                Object[] paramValues = new Object[1];
                paramValues[0] = pValue;

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
        return obj;
    }
}

```

我们这里的代码主要可以分成两个部分：一部分是处理constructor的里面的参数，另外一部分是处理各个property的属性。现在程序的代码是写在一起的，后面我们还会抽出单独的方法。

### 如何处理constructor？

首先，获取XML配置中的属性值，这个时候它们都是通用的Object类型，我们需要根据type字段的定义判断不同Value所属的类型，作为一个原始的实现这里我们只提供了String、Integer 和 int三种类型的判断。最终通过反射构造对象，将配置的属性值注入到了Bean对象中，实现构造器注入。

### 如何处理property？

和处理constructor相同，我们依然要通过type字段确定Value的归属类型。但不同之处在于，判断好归属类型后，我们还要手动构造setter方法，通过反射将属性值注入到setter方法之中。通过这种方式来实现对属性的赋值。

可以看出，其实代码的核心是通过Java的反射机制调用构造器及setter方法，在调用过程中根据具体的类型把属性值作为一个参数赋值进去。这也是所有的框架在实现IoC时的思路。 **反射技术是IoC容器赖以工作的基础。**

到这里，我们就完成了对XML配置的解析，实现了Spring中Bean的构造器注入与setter注入方式。回到我们开头的问题：配置文件中的属性设置是如何生效的？到这里我们就有答案了，就是 **通过反射给Bean里面的属性赋值，就意味着配置文件生效了。**

这里，我还想带你理清一个小的概念问题。在实现过程中，我们经常会用到依赖注入和IoC这两个术语，初学者很容易被这两个术语弄糊涂。其实，一开始只有IoC，也就是控制反转，但是这个术语让人很难快速理解，我们不知道反转了什么东西。但是通过之前的实现过程，我们就可以理解这个词了。

![图片](https://static001.geekbang.org/resource/image/d5/4b/d508800320aa0f8688b7c986e0148e4b.png?wh=1920x975)

一个“正常”的控制过程是由调用者直接创建Bean，但是IoC的过程正好相反，是由框架来创建Bean，然后注入给调用者，这与“正常”的过程是反的，控制反转就是这个意思。但是总的来说，这个术语还是过于隐晦，引发了很长一段时间的争议，直到传奇程序员Martin Fowler一锤定音，将其更名为“依赖注入”，一切才尘埃落定，“依赖注入”从此成为大家最常使用的术语。

## Bean之间的依赖问题

现在我们进一步考虑一个问题。在注入属性值的时候，如果这个属性本身是一个对象怎么办呢？这就是Bean之间的依赖问题了。

这个场景在我们进行代码开发时还是非常常见的。比如，操作MySQL数据库的时候，经常需要引入Mapper类，而Mapper类本质上也是在IoC容器在启动时加载的一个Bean对象。

或许有人会说，我们就按照前面的配置方式，在type里配置需要配置Bean的绝对包路径，name里对应Bean的属性，不就好了吗？但这样还是会存在一个问题， **如何用Value这样一个简单的值表示某个对象中所有的域呢？**

为此，Spring做了一个很巧妙的事情，它在标签里增加了 **ref属性（引用）**，这个属性就记录了需要引用的另外一个Bean，这就方便多了。你可以参考下面的配置文件。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<beans>
    <bean id="basebaseservice" class="com.minis.test.BaseBaseService">
        <property type="com.minis.test.AServiceImpl" name="as" ref="aservice" />
    </bean>
    <bean id="aservice" class="com.minis.test.AServiceImpl">
        <constructor-arg type="String" name="name" value="abc"/>
        <constructor-arg type="int" name="level" value="3"/>
        <property type="String" name="property1" value="Someone says"/>
        <property type="String" name="property2" value="Hello World!"/>
        <property type="com.minis.test.BaseService" name="ref1" ref="baseservice"/>
    </bean>
    <bean id="baseservice" class="com.minis.test.BaseService">
        <property type="com.minis.test.BaseBaseService" name="bbs" ref="basebaseservice" />
    </bean>

```

在上面的XML配置文件中，我们配置了一个Bean，ID命名为baseservice，随后在aservice bean的标签中设置ref=“baseservice”，也就是说我们希望此处注入的是一个Bean而不是一个简单的值。所以在对应的AServiceImpl里，也得有类型为BaseService的域ref1。

```java
public class AServiceImpl implements AService {
    private String name;
    private int level;
    private String property1;
    private String property2;
    private BaseService ref1;

    public AServiceImpl() {
    }
    public AServiceImpl(String name, int level) {
        this.name = name;
        this.level = level;
        System.out.println(this.name + "," + this.level);
    }
    public void sayHello() {
        System.out.println(this.property1 + "," + this.property2);
    }

    // 在此省略property1和property2的setter、getter方法
}

```

既然添加了ref属性，接下来我们很自然地会想到，要解析这个属性。下面我们就来解析一下ref，看看Spring是如何将配置的Bean注入到另外一个Bean中的。

我们为PropertyValue.java程序增加isRef字段，它可以判断属性是引用类型还是普通的值类型，我们看下修改后的代码。

```java
public class PropertyValue {
    private final String type;
    private final String name;
    private final Object value;
    private final boolean isRef;
    public PropertyValue(String type, String name, Object value, boolean isRef)
{
        this.type = type;
        this.name = name;
        this.value = value;
        this.isRef = isRef;
}

```

在这里我们调整了PropertyValue的构造函数，增加了isRef参数。

接下来我们看看如何解析ref属性，我们还是在XmlBeanDefinitionReader类中来处理。

```java
 public void loadBeanDefinitions(Resource resource) {
        while (resource.hasNext()) {
            Element element = (Element) resource.next();
            String beanID = element.attributeValue("id");
            String beanClassName = element.attributeValue("class");
            BeanDefinition beanDefinition = new BeanDefinition(beanID,
beanClassName);
            // handle constructor
            List<Element> constructorElements = element.elements("constructor-
arg");
            ArgumentValues AVS = new ArgumentValues();
            for (Element e : constructorElements) {
                String aType = e.attributeValue("type");
                String aName = e.attributeValue("name");
                String aValue = e.attributeValue("value");
                AVS.addArgumentValue(new ArgumentValue(aType, aName, aValue));
            }
            beanDefinition.setConstructorArgumentValues(AVS);

            // handle properties
            List<Element> propertyElements = element.elements("property");
            PropertyValues PVS = new PropertyValues();
            List<String> refs = new ArrayList<>();
            for (Element e : propertyElements) {
                String pType = e.attributeValue("type");
                String pName = e.attributeValue("name");
                String pValue = e.attributeValue("value");
                String pRef = e.attributeValue("ref");
                String pV = "";
                boolean isRef = false;
                if (pValue != null && !pValue.equals("")) {
                    isRef = false;
                    pV = pValue;
                } else if (pRef != null && !pRef.equals("")) {
                    isRef = true;
                    pV = pRef;
                    refs.add(pRef);
                }
                PVS.addPropertyValue(new PropertyValue(pType, pName, pV,
isRef));
            }
            beanDefinition.setPropertyValues(PVS);

            String[] refArray = refs.toArray(new String[0]);
            beanDefinition.setDependsOn(refArray);
            this.simpleBeanFactory.registerBeanDefinition(beanID,
beanDefinition);
        }
   }

```

由上述代码可以看出，程序解析 `<property>` 标签后，获取了ref的参数，同时有针对性地设置了isRef的值，把它添加到了PropertyValues内，最后程序调用setDependsOn方法，它记录了某一个Bean引用的其他Bean。这样，我们引用ref的配置就定义好了。

然后，我们改造一下以前的createBean()方法，抽取出一个单独处理属性的方法。

```java
	private Object createBean(BeanDefinition bd) {
		... ...
		handleProperties(bd, clz, obj);
		return obj;
	}

	private void handleProperties(BeanDefinition bd, Class<?> clz, Object obj) {
        // 处理属性
		System.out.println("handle properties for bean : " + bd.getId());
		PropertyValues propertyValues = bd.getPropertyValues();
        //如果有属性
		if (!propertyValues.isEmpty()) {
			for (int i=0; i<propertyValues.size(); i++) {
				PropertyValue propertyValue = propertyValues.getPropertyValueList().get(i);
				String pName = propertyValue.getName();
				String pType = propertyValue.getType();
    			Object pValue = propertyValue.getValue();
    			boolean isRef = propertyValue.getIsRef();
    			Class<?>[] paramTypes = new Class<?>[1];
				Object[] paramValues =   new Object[1];
    			if (!isRef) { //如果不是ref，只是普通属性
                    //对每一个属性，分数据类型分别处理
					if ("String".equals(pType) || "java.lang.String".equals(pType)) {
						paramTypes[0] = String.class;
					}
					else if ("Integer".equals(pType) || "java.lang.Integer".equals(pType)) {
						paramTypes[0] = Integer.class;
					}
					else if ("int".equals(pType)) {
						paramTypes[0] = int.class;
					}
					else {
						paramTypes[0] = String.class;
					}

					paramValues[0] = pValue;
    			}
    			else { //is ref, create the dependent beans
    				try {
						paramTypes[0] = Class.forName(pType);
					} catch (ClassNotFoundException e) {
						e.printStackTrace();
					}
    				try {
                        //再次调用getBean创建ref的bean实例
						paramValues[0] = getBean((String)pValue);
					}
    			}

                //按照setXxxx规范查找setter方法，调用setter方法设置属性
    			String methodName = "set" + pName.substring(0,1).toUpperCase() + pName.substring(1);
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

```

这里的重点是处理ref的这几行代码。

```plain
//is ref, create the dependent beans
paramTypes[0] = Class.forName(pType);
paramValues[0] = getBean((String)pValue);

```

这段代码实现的思路就是，对ref所指向的另一个Bean再次调用getBean()方法，这个方法会获取到另一个Bean实例，这样就实现了另一个Bean的注入。

这样一来，如果有多级引用，就会形成一个多级的getBean()调用链。由于在调用getBean()的时候会判断容器中是否包含了bean instance，没有的话会立即创建，所以XML配置文件中声明Bean的先后次序是任意的。

## 循环依赖问题

这又引出了另一个问题，在某个Bean需要注入另一个Bean的时候，如果那个Bean还不存在，该怎么办？

请你想象一个场景，Spring扫描到了ABean，在解析它并设置内部属性时，发现某个属性是另一个BBean，而此时Spring内部还不存在BBean的实例。这就要求Spring在创建ABean的过程中，能够再去创建一个BBean，继续推衍下去，BBean可能又会依赖第三个CBean。事情还可能进一步复杂化，如果CBean又反过来依赖ABean，就会形成循环依赖。

在逻辑上，我们好像陷入了一个死结，我们必须想办法打破这个循环。我们来看看Spring是如何解决这个问题的。

请你回顾一下创建Bean的过程。我们根据Bean的定义配置生成了BeanDefinition，然后根据定义加载Bean类，再进行实例化，最后在Bean中注入属性。

从这个过程中可以看出，在注入属性之前，其实这个Bean的实例已经生成出来了，只不过此时的实例还不是一个完整的实例，它还有很多属性没有值，可以说是一个早期的毛胚实例。而我们现在讨论的Bean之间的依赖是在属性注入这一阶段，因此我们可以在实例化与属性注入这两个阶段之间增加一个环节，确保给Bean注入属性的时候，Spring内部已经准备好了Bean的实例。

Spring的做法是在BeanFactory中引入一个结构： **earlySingletonObjects**，这里面存放的就是早期的毛胚实例。创建Bean实例的时候，不用等到所有步骤完成，而是可以在属性还没有注入之前，就把早期的毛胚实例先保存起来，供属性注入时使用。

这时再回到我们的复杂依赖场景，ABean依赖BBean，BBean又依赖CBean，而CBean反过来还要依赖ABean。现在，我们可以这样实现依赖注入。

![图片](https://static001.geekbang.org/resource/image/f4/ee/f4a1a6b8973eae18d9edb54cd8277bee.png?wh=1806x1482)

第一步，先实例化ABean，此时它是早期的不完整毛胚实例，好多属性还没被赋值，将实例放置到earlySingletonObjects中备用。然后给ABean注入属性，这个时候发现它还要依赖BBean。

第二步，实例化BBean，它也是早期的不完整毛胚实例，我们也将实例放到earlySingletonObjects中备用。然后再给BBean注入属性，又发现它依赖CBean。

第三步，实例化CBean，此时它仍然是早期的不完整的实例，同样将实例放置到earlySingletonObjects中备用，然后再给CBean属性赋值，这个时候又发现它反过来还要依赖ABean。

第四步，我们从earlySingletonObjects结构中找到ABean的早期毛胚实例，取出来给CBean注入属性，这意味着这时CBean所用的ABean实例是那个早期的毛胚实例。这样就先创建好了CBean。

第五步，程序控制流回到第二步，完成BBean的属性注入。

第六步，程序控制流回到第一步，完成ABean的属性注入。至此，所有的Bean就都创建完了。

通过上述过程可以知道，这一系列的Bean是纠缠在一起创建的，我们不能简单地先后独立创建它们，而是要作为一个整体来创建。

相应的程序代码，反映在getBean(), createBean() 和 doCreateBean()中。

```java
@Override
public Object getBean(String beanName) throws BeansException {
    //先尝试直接从容器中获取bean实例
    Object singleton = this.getSingleton(beanName);
    if (singleton == null) {
        //如果没有实例，则尝试从毛胚实例中获取
        singleton = this.earlySingletonObjects.get(beanName);
        if (singleton == null) {
            //如果连毛胚都没有，则创建bean实例并注册
            BeanDefinition beanDefinition = beanDefinitionMap.get(beanName);
            singleton = createBean(beanDefinition);
            this.registerSingleton(beanName, singleton);
            // 预留beanpostprocessor位置
            // step 1: postProcessBeforeInitialization
            // step 2: afterPropertiesSet
            // step 3: init-method
            // step 4: postProcessAfterInitialization
        }
    }
    return singleton;
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
    //处理属性
    handleProperties(beanDefinition, clz, obj);
    return obj;
}

//doCreateBean创建毛胚实例，仅仅调用构造方法，没有进行属性处理
private Object doCreateBean(BeanDefinition bd) {
		Class<?> clz = null;
		Object obj = null;
		Constructor<?> con = null;

		try {
    		clz = Class.forName(bd.getClassName());

    		//handle constructor
    		ArgumentValues argumentValues = bd.getConstructorArgumentValues();
    		if (!argumentValues.isEmpty()) {
        		Class<?>[] paramTypes = new Class<?>[argumentValues.getArgumentCount()];
        		Object[] paramValues =   new Object[argumentValues.getArgumentCount()];
    			for (int i=0; i<argumentValues.getArgumentCount(); i++) {
    				ArgumentValue argumentValue = argumentValues.getIndexedArgumentValue(i);
    				if ("String".equals(argumentValue.getType()) || "java.lang.String".equals(argumentValue.getType())) {
    					paramTypes[i] = String.class;
        				paramValues[i] = argumentValue.getValue();
    				}
    				else if ("Integer".equals(argumentValue.getType()) || "java.lang.Integer".equals(argumentValue.getType())) {
    					paramTypes[i] = Integer.class;
        				paramValues[i] = Integer.valueOf((String) argumentValue.getValue());
    				}
    				else if ("int".equals(argumentValue.getType())) {
    					paramTypes[i] = int.class;
        				paramValues[i] = Integer.valueOf((String) argumentValue.getValue()).intValue();
    				}
    				else {
    					paramTypes[i] = String.class;
        				paramValues[i] = argumentValue.getValue();
    				}
    			}
				try {
					con = clz.getConstructor(paramTypes);
					obj = con.newInstance(paramValues);
				}
    		}
    		else {
    			obj = clz.newInstance();
    		}
		}

		System.out.println(bd.getId() + " bean created. " + bd.getClassName() + " : " + obj.toString());
		return obj;

}

```

createBean()方法中调用了一个 **doCreateBean(bd)方法**，专门负责创建早期的毛胚实例。毛胚实例创建好后会放在earlySingletonObjects结构中，然后createBean()方法再调用handleProperties()补齐这些property的值。

在getBean()方法中，首先要判断有没有已经创建好的bean，有的话直接取出来，如果没有就检查earlySingletonObjects中有没有相应的毛胚Bean，有的话直接取出来，没有的话就去创建，并且会根据Bean之间的依赖关系把相关的Bean全部创建好。

很多资料把这个过程叫做bean的“三级缓存”，这个术语来自于Spring源代码中的程序注释。实际上我们弄清楚了这个getBean()的过程后就会知道这段注释并不是很恰当。只不过这是Spring发明人自己写下的注释，大家也都这么称呼而已。

## 包装方法refresh()

可以看出，在Spring体系中，Bean是结合在一起同时创建完毕的。为了减少它内部的复杂性，Spring对外提供了一个很重要的包装方法： **refresh()**。具体的包装方法也很简单，就是对所有的Bean调用了一次getBean()，利用getBean()方法中的createBean()创建Bean实例，就可以只用一个方法把容器中所有的Bean的实例创建出来了。

我们先在SimpleBeanFactory中实现一个最简化的refresh()方法。

```java
public void refresh() {
    for (String beanName : beanDefinitionNames) {
        try {
            getBean(beanName);
        }
    }
}

```

然后我们改造ClassPathXmlApplicationContext，配合我们上一步增加的refresh()方法使用，你可以看下相应的代码。

```java
public class ClassPathXmlApplicationContext implements BeanFactory, ApplicationEventPublisher{

  SimpleBeanFactory beanFactory;
  public ClassPathXmlApplicationContext(String fileName) {
      this(fileName, true);
  }
  public ClassPathXmlApplicationContext(String fileName, boolean isRefresh) {
      Resource resource = new ClassPathXmlResource(fileName);
      SimpleBeanFactory simpleBeanFactory = new SimpleBeanFactory();
      XmlBeanDefinitionReader reader = new XmlBeanDefinitionReader(simpleBeanFactory);
      reader.loadBeanDefinitions(resource);
      this.beanFactory = simpleBeanFactory;
      if (isRefresh) {
          this.beanFactory.refresh();
      }
  }
  // 省略方法实现
 }

```

到这里，我们的ClassPAthXmlApplicationContext用一个refresh() 就将整个IoC容器激活了，运行起来，加载所有配置好的Bean。

你可以试着构建一下的测试代码。

```java
public class BaseBaseService {
    private AServiceImpl as;
    // 省略 getter、setter方法
}

```

```java
public class BaseService {
    private BaseBaseService bbs;
    // 省略 getter、setter方法
}

```

```java
public class AServiceImpl implements AService {
    private String name;
    private int level;
    private String property1;
    private String property2;
    private BaseService ref1;
    // 省略 getter、setter方法
}

```

相应的XML配置如下：

```java
<?xml version="1.0" encoding="UTF-8" ?>
<beans>
    <bean id="aservice" class="com.minis.test.AServiceImpl">
        <constructor-arg type="String" name="name" value="abc"/>
        <constructor-arg type="int" name="level" value="3"/>
        <property type="String" name="property1" value="Someone says"/>
        <property type="String" name="property2" value="Hello World!"/>
        <property type="com.minis.test.BaseService" name="ref1"
ref="baseservice"/>
    </bean>
    <bean id="basebaseservice" class="com.minis.test.BaseBaseService">
        <property type="com.minis.test.AServiceImpl" name="as" ref="aservice" />
    </bean>
    <bean id="baseservice" class="com.minis.test.BaseService">
        <property type="com.minis.test.BaseBaseService" name="bbs"
ref="basebaseservice" />
    </bean>

```

然后运行测试程序，可以看到我们自己的IoC容器运行起来了。

## 小结

这节课，我们紧接着上一节课对XML配置的解析，实现了Spring中Bean的构造器注入与setter注入两种方式。

在将属性注入Bean的过程中，我们还增加了ref属性，它可以在一个Bean对象中引入另外的Bean对象。我们还通过引入“毛胚Bean”的概念解决了循环依赖的问题。

我们还为容器增加了refresh()方法，这个方法包装了容器启动的各个步骤，从Bean工厂的创建到Bean对象的实例化和初始化，再到完成Spring容器加载，一切Bean的处理都能在这里完成，可以说是Spring中的核心方法了。

完整源代码参见 [https://github.com/YaleGuo/minis](https://github.com/YaleGuo/minis)

## 课后题

学完这节课内容，我也给你留一道思考题。你认为能不能在一个Bean的构造器中注入另一个Bean？欢迎你在留言区与我交流讨论，也欢迎你把这节课分享给需要的朋友。我们下节课见！