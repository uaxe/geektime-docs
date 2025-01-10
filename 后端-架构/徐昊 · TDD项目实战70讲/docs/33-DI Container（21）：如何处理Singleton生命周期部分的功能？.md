你好，我是徐昊。今天我们继续使用TDD的方式实现注入依赖容器。

## 回顾代码与任务列表

到目前为止，我们的代码是这样的：

```
Component.java

package geektime.tdd.di;
import java.lang.annotation.Annotation;
public record Component(Class<?> type, Annotation qualifiers) {
}

ComponentRef.java

package geektime.tdd.di;
import java.lang.annotation.Annotation;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.Objects;
public class ComponentRef<ComponentType> {
    public static <ComponentType> ComponentRef<ComponentType> of(Class<ComponentType> component) {
        return new ComponentRef(component, null);
    }
    public static <ComponentType> ComponentRef<ComponentType> of(Class<ComponentType> component, Annotation qualifier) {
        return new ComponentRef(component, qualifier);
    }
    public static ComponentRef of(Type type) {
        return new ComponentRef(type, null);
    }
    public static ComponentRef of(Type type, Annotation qualifier) {
        return new ComponentRef(type, qualifier);
    }

    private Type container;
    private Component component;
    ComponentRef(Type type, Annotation qualifier) {
        init(type, qualifier);
    }
    protected ComponentRef() {
        this(null);
    }
    protected ComponentRef(Annotation qualifier) {
        Type type = ((ParameterizedType) getClass().getGenericSuperclass()).getActualTypeArguments()[0];
        init(type, qualifier);
    }
    private void init(Type type, Annotation qualifier) {
        if (type instanceof ParameterizedType container) {
            this.container = container.getRawType();
            this.component = new Component((Class<ComponentType>) container.getActualTypeArguments()[0], qualifier);
        } else
            this.component = new Component((Class<ComponentType>) type, qualifier);
    }
    public Type getContainer() {
        return container;
    }
    public Class<?> getComponentType() {
        return component.type();
    }
    public boolean isContainer() {
        return container != null;
    }
    public Component component() {
        return component;
    }
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ComponentRef<?> that = (ComponentRef<?>) o;
        return Objects.equals(container, that.container) && component.equals(that.component);
    }
    @Override
    public int hashCode() {
        return Objects.hash(container, component);
    }
}

Context.java

package geektime.tdd.di;
import java.util.Optional;
public interface Context {
    <ComponentType> Optional<ComponentType> get(ComponentRef<ComponentType> ref);
}

ContextConfig.java

package geektime.tdd.di;
import jakarta.inject.Provider;
import jakarta.inject.Qualifier;
import java.lang.annotation.Annotation;
import java.util.*;
public class ContextConfig {
    private Map<Component, ComponentProvider<?>> components = new HashMap<>();
    public <Type> void bind(Class<Type> type, Type instance) {
        components.put(new Component(type, null), (ComponentProvider<Type>) context -> instance);
    }
    public <Type> void bind(Class<Type> type, Type instance, Annotation... qualifiers) {
        if (Arrays.stream(qualifiers).anyMatch(q -> !q.annotationType().isAnnotationPresent(Qualifier.class)))
            throw new IllegalComponentException();
        for (Annotation qualifier : qualifiers)
            components.put(new Component(type, qualifier), context -> instance);
    }
    public <Type, Implementation extends Type>
    void bind(Class<Type> type, Class<Implementation> implementation) {
        components.put(new Component(type, null), new InjectionProvider<>(implementation));
    }
    public <Type, Implementation extends Type>
    void bind(Class<Type> type, Class<Implementation> implementation, Annotation... qualifiers) {
        if (Arrays.stream(qualifiers).anyMatch(q -> !q.annotationType().isAnnotationPresent(Qualifier.class)))
            throw new IllegalComponentException();
        for (Annotation qualifier : qualifiers)
            components.put(new Component(type, qualifier), new InjectionProvider<>(implementation));
    }
    public Context getContext() {
        components.keySet().forEach(component -> checkDependencies(component, new Stack<>()));
        return new Context() {
            @Override
            public <ComponentType> Optional<ComponentType> get(ComponentRef<ComponentType> ref) {
                if (ref.isContainer()) {
                    if (ref.getContainer() != Provider.class) return Optional.empty();
                    return (Optional<ComponentType>) Optional.ofNullable(getProvider(ref))
                            .map(provider -> (Provider<Object>) () -> provider.get(this));
                }
                return Optional.ofNullable(getProvider(ref)).map(provider -> (ComponentType) provider.get(this));
            }
        };
    }
    private <ComponentType> ComponentProvider<?> getProvider(ComponentRef<ComponentType> ref) {
        return components.get(ref.component());
    }
    private void checkDependencies(Component component, Stack<Component> visiting) {
        for (ComponentRef<?> dependency : components.get(component).getDependencies()) {
            if (!components.containsKey(dependency.component()))
                throw new DependencyNotFoundException(component, dependency.component());
            if (!dependency.isContainer()) {
                if (visiting.contains(dependency.component())) throw new CyclicDependenciesFoundException(visiting);
                visiting.push(dependency.component());
                checkDependencies(dependency.component(), visiting);
                visiting.pop();
            }
        }
    }
    interface ComponentProvider<T> {
        T get(Context context);
        default List<ComponentRef<?>> getDependencies() {
            return List.of();
        }
    }
}

InjectionProvider.java

package geektime.tdd.di;
import jakarta.inject.Inject;
import jakarta.inject.Qualifier;
import java.lang.annotation.Annotation;
import java.lang.reflect.*;
import java.util.*;
import java.util.function.BiFunction;
import java.util.stream.Stream;
import static java.util.Arrays.stream;
import static java.util.stream.Stream.concat;
class InjectionProvider<T> implements ContextConfig.ComponentProvider<T> {
    private Injectable<Constructor<T>> injectConstructor;
    private List<Injectable<Method>> injectMethods;
    private List<Injectable<Field>> injectFields;
    public InjectionProvider(Class<T> component) {
        if (Modifier.isAbstract(component.getModifiers())) throw new IllegalComponentException();
        this.injectConstructor = getInjectConstructor(component);
        this.injectMethods = getInjectMethods(component);
        this.injectFields = getInjectFields(component);
        if (injectFields.stream().anyMatch(f -> Modifier.isFinal(f.element().getModifiers())))
            throw new IllegalComponentException();
        if (injectMethods.stream().anyMatch(m -> m.element().getTypeParameters().length != 0))
            throw new IllegalComponentException();
    }
    @Override
    public T get(Context context) {
        try {
            T instance = injectConstructor.element().newInstance(injectConstructor.toDependencies(context));
            for (Injectable<Field> field : injectFields)
                field.element().set(instance, field.toDependencies(context)[0]);
            for (Injectable<Method> method : injectMethods)
                method.element().invoke(instance, method.toDependencies(context));
            return instance;
        } catch (InvocationTargetException | InstantiationException | IllegalAccessException e) {
            throw new RuntimeException(e);
        }
    }
    @Override
    public List<ComponentRef<?>> getDependencies() {
        return concat(concat(Stream.of(injectConstructor), injectFields.stream()), injectMethods.stream())
                .map(Injectable::required).flatMap(Arrays::stream).toList();
    }
    record Injectable<Element extends AccessibleObject>(Element element, ComponentRef<?>[] required) {
        Object[] toDependencies(Context context) {
            return stream(required).map(context::get).map(Optional::get).toArray();
        }
        static <Element extends Executable> Injectable<Element> of(Element element) {
            return new Injectable<>(element, stream(element.getParameters()).map(Injectable::toComponentRef).toArray(ComponentRef<?>[]::new));
        }
        static Injectable<Field> of(Field field) {
            return new Injectable<>(field, new ComponentRef<?>[]{toComponentRef(field)});
        }
        private static ComponentRef<?> toComponentRef(Field field) {
            return ComponentRef.of(field.getGenericType(), getQualifier(field));
        }
        private static ComponentRef<?> toComponentRef(Parameter parameter) {
            return ComponentRef.of(parameter.getParameterizedType(), getQualifier(parameter));
        }
        private static Annotation getQualifier(AnnotatedElement element) {
            List<Annotation> qualifiers = stream(element.getAnnotations())
                    .filter(a -> a.annotationType().isAnnotationPresent(Qualifier.class)).toList();
            if (qualifiers.size() > 1) throw new IllegalComponentException();
            return qualifiers.stream().findFirst().orElse(null);
        }
    }
    private static <T> List<Injectable<Method>> getInjectMethods(Class<T> component) {
        List<Method> injectMethods = traverse(component, (methods, current) -> injectable(current.getDeclaredMethods())
                .filter(m -> isOverrideByInjectMethod(methods, m))
                .filter(m -> isOverrideByNoInjectMethod(component, m)).toList());
        Collections.reverse(injectMethods);
        return injectMethods.stream().map(Injectable::of).toList();
    }
    private static <T> List<Injectable<Field>> getInjectFields(Class<T> component) {
        return InjectionProvider.<Field>traverse(component, (fields, current) -> injectable(current.getDeclaredFields()).toList())
                .stream().map(Injectable::of).toList();
    }
    private static <Type> Injectable<Constructor<Type>> getInjectConstructor(Class<Type> implementation) {
        List<Constructor<?>> injectConstructors = injectable(implementation.getConstructors()).toList();
        if (injectConstructors.size() > 1) throw new IllegalComponentException();
        return Injectable.of((Constructor<Type>) injectConstructors.stream().findFirst().orElseGet(() -> defaultConstructor(implementation)));
    }
    private static <Type> Constructor<Type> defaultConstructor(Class<Type> implementation) {
        try {
            return implementation.getDeclaredConstructor();
        } catch (NoSuchMethodException e) {
            throw new IllegalComponentException();
        }
    }
    private static <T> List<T> traverse(Class<?> component, BiFunction<List<T>, Class<?>, List<T>> finder) {
        List<T> members = new ArrayList<>();
        Class<?> current = component;
        while (current != Object.class) {
            members.addAll(finder.apply(members, current));
            current = current.getSuperclass();
        }
        return members;
    }
    private static <T extends AnnotatedElement> Stream<T> injectable(T[] declaredFields) {
        return stream(declaredFields).filter(f -> f.isAnnotationPresent(Inject.class));
    }
    private static boolean isOverride(Method m, Method o) {
        return o.getName().equals(m.getName()) && Arrays.equals(o.getParameterTypes(), m.getParameterTypes());
    }
    private static <T> boolean isOverrideByNoInjectMethod(Class<T> component, Method m) {
        return stream(component.getDeclaredMethods()).filter(m1 -> !m1.isAnnotationPresent(Inject.class)).noneMatch(o -> isOverride(m, o));
    }
    private static boolean isOverrideByInjectMethod(List<Method> injectMethods, Method m) {
        return injectMethods.stream().noneMatch(o -> isOverride(m, o));
    }
}

```

任务列表的状态为：

- 无需构造的组件——组件实例

- 如果注册的组件不可实例化，则抛出异常
  - 抽象类
  - 接口
- 构造函数注入
  - 无依赖的组件应该通过默认构造函数生成组件实例
  - 有依赖的组件，通过Inject标注的构造函数生成组件实例
  - 如果所依赖的组件也存在依赖，那么需要对所依赖的组件也完成依赖注入
  - 如果组件有多于一个Inject标注的构造函数，则抛出异常
  - 如果组件没有Inject标注的构造函数，也没有默认构造函数（新增任务）
  - 如果组件需要的依赖不存在，则抛出异常
  - 如果组件间存在循环依赖，则抛出异常
- 字段注入
  - 通过Inject标注将字段声明为依赖组件
  - 如果字段为final则抛出异常
  - 依赖中应包含Inject Field声明的依赖
- 方法注入
  - 通过Inject标注的方法，其参数为依赖组件
  - 通过Inject标注的无参数方法，会被调用
  - 按照子类中的规则，覆盖父类中的Inject方法
  - 如果方法定义类型参数，则抛出异常
  - 依赖中应包含Inject Method声明的依赖
- 对Provider类型的依赖
  - 从容器中取得组件的Provider（新增任务）
  - 注入构造函数中可以声明对于Provider的依赖
  - 注入字段中可以声明对于Provider的依赖
  - 注入方法中可声明对于Provider的依赖
  - 将构造函数中的Provider加入依赖（新增任务）
  - 将字段中的Provider加入依赖（新增任务）
  - 将方法中的Provider加入依赖（新增任务）
- 自定义Qualifier的依赖
  - 注册组件时，可额外指定Qualifier
    - 针对instance指定一个Qualifieri（新增任务）
    - 针对组件指定一个Qualiifer（新增任务）
    - 针对instance指定多个Qualifieri（新增任务）
    - 针对组件指定多个Qualiifer（新增任务）
  - 注册组件时，如果不是合法的Qualifier，则不接受组件注册（新增任务）

  - 寻找依赖时，需同时满足类型与自定义Qualifier标注
    - 在检查依赖时使用Qualifier（新增任务）

    - 在检查循环依赖时使用Qualifier（新增任务）

    - 构造函数注入可以使用Qualifier声明依赖（新增任务）
      - 依赖中包含Qualifier（新增任务）
      - 如果不是合法的Qualifier，则组件非法
    - 字段注入可以使用Qualifier声明依赖（新增任务）
      - 依赖中包含Qualifier（新增任务）
      - 如果不是合法的Qualifier，则组件非法
    - 函数注入可以使用Qualifier声明依赖（新增任务）
      - 依赖中包含Qualifier（新增任务）
      - 如果不是合法的Qualifier，则组件非法
  - 支持默认Qualifier——Named（不需要）

  - 注册组件时，可从类对象上提取Qualifier（不需要）
- Singleton生命周期
  - 注册组件时，可额外指定是否为Singleton
  - 注册组件时，可从类对象上提取Singleton标注
  - 对于包含Singleton标注的组件，在容器范围内提供唯一实例
  - 容器组件默认不是Single生命周期
- 自定义Scope标注
  - 可向容器注册自定义Scope标注的回调

## 视频演示

让我们进入今天的部分：

## 思考题

在进入下节课之前，希望你能认真思考如下两个问题，并选择最有感触的一道进行回答。

1. 对于Bind的逻辑要进行什么样的重构？
2. 到这里，我们已经进行了很多次的重构。现在你对重构的使用是什么看法呢？

**编辑来信**：

> 第二期“TDD·代码评点”活动正式启动啦！为了帮助你更平滑地过渡到第三个实战项目，徐老师发起了代码评点活动。
>
> 你可以填写 [学习问卷](https://jinshuju.net/f/fnh84B) 提交项目代码，而后，徐老师会一一查看，并进行评点与答疑。关于评点的详细内容，我们也将制成加餐展示在专栏里，供其他同学学习与参考。
>
> 请注意，此次收集时间截至5月27日晚上12点。此外，我也会从中选出1-2位同学，送出《重构与模式》一书。请抓紧上车，入股不亏哦！

欢迎把你的想法分享在留言区，也欢迎把你的项目代码的链接分享出来。相信经过你的思考与实操，学习效果会更好！