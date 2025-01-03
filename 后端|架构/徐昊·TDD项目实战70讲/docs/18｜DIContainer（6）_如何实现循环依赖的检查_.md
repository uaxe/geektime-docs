你好，我是徐昊。今天我们继续使用TDD的方式实现注入依赖容器。

## 回顾代码与任务列表

到目前为止，我们的代码是这样的：

```
 ContextConfig.java:

    package geektime.tdd.di;

    import jakarta.inject.Inject;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Parameter;
    import java.util.HashMap;
    import java.util.List;
    import java.util.Map;
    import java.util.Optional;
    import java.util.stream.Collectors;
    import static java.util.Arrays.asList;
    import static java.util.Arrays.stream;

    public class ContextConfig {
        private Map<Class<?>, ComponentProvider<?>> providers = new HashMap<>();
        private Map<Class<?>, List<Class<?>>> dependencies = new HashMap<>();

        public <Type> void bind(Class<Type> type, Type instance) {
            providers.put(type, context -> instance);
            dependencies.put(type, asList());
        }

        public <Type, Implementation extends Type>
        void bind(Class<Type> type, Class<Implementation> implementation) {
            Constructor<Implementation> injectConstructor = getInjectConstructor(implementation);
            providers.put(type, new ConstructorInjectionProvider<>(type, injectConstructor));
            dependencies.put(type, stream(injectConstructor.getParameters()).map(Parameter::getType).collect(Collectors.toList()));
        }

        public Context getContext() {
            for (Class<?> component: dependencies.keySet()) {
                for (Class<?> dependency: dependencies.get(component)) {
                    if (!dependencies.containsKey(dependency)) throw new DependencyNotFoundException(component, dependency);
                }
            }
            return new Context() {
                @Override
                public <Type> Optional<Type> get(Class<Type> type) {
                    return Optional.ofNullable(providers.get(type)).map(provider -> (Type) provider.get(this));
                }
            };
        }

        interface ComponentProvider<T> {
            T get(Context context);
        }

        class ConstructorInjectionProvider<T> implements ComponentProvider<T> {
            private Class<?> componentType;
            private Constructor<T> injectConstructor;
            private boolean constructing = false;
            public ConstructorInjectionProvider(Class<?> componentType, Constructor<T> injectConstructor) {
                this.componentType = componentType;
                this.injectConstructor = injectConstructor;
            }
            @Override
            public T get(Context context) {
                if (constructing) throw new CyclicDependenciesFoundException(componentType);
                try {
                    constructing = true;
                    Object[] dependencies = stream(injectConstructor.getParameters())
                            .map(p -> context.get(p.getType())
                                    .orElseThrow(() -> new DependencyNotFoundException(componentType, p.getType())))
                            .toArray(Object[]::new);
                    return injectConstructor.newInstance(dependencies);
                } catch (CyclicDependenciesFoundException e) {
                    throw new CyclicDependenciesFoundException(componentType, e);
                } catch (InvocationTargetException | InstantiationException | IllegalAccessException e) {
                    throw new RuntimeException(e);
                } finally {
                    constructing = false;
                }
            }
        }

        private <Type> Constructor<Type> getInjectConstructor(Class<Type> implementation) {
            List<Constructor<?>> injectConstructors = stream(implementation.getConstructors())
                    .filter(c -> c.isAnnotationPresent(Inject.class)).collect(Collectors.toList());
            if (injectConstructors.size() > 1) throw new IllegalComponentException();
            return (Constructor<Type>) injectConstructors.stream().findFirst().orElseGet(() -> {
                try {
                    return implementation.getConstructor();
                } catch (NoSuchMethodException e) {
                    throw new IllegalComponentException();
                }
            });
        }
    }

    Context.java:

    package geektime.tdd.di;

    import java.util.Optional;

    public interface Context {
        <Type> Optional<Type> get(Class<Type> type);
    }

```

任务列表状态为：

![](https://static001.geekbang.org/resource/image/ce/4c/cebe21e8012af25ae8b11824cd73c44c.jpg?wh=6294x10999)

## 视频演示

让我们进入今天的部分：

## 思考题

为了我们更好的交流与互动，从这节课开始，思考题目除了固定的技术问题外，我还会设置一道较为轻松的题目，供你选择与回答。

1. 在当前的代码结构下，后续任务需要做何种改变？
2. 在学习课程的过程中，你对TDD的认识有发生什么变化吗？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码的链接分享出来。相信经过你的思考与实操，学习效果会更好！