你好，我是徐昊，今天我们继续使用TDD的方式实现注入依赖容器。

## 回顾代码与任务列表

到目前为止，我们的代码是这样的：

```
package geektime.tdd.di;

import jakarta.inject.Inject;
import jakarta.inject.Provider;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import static java.util.Arrays.stream;

public class Context {
    private Map<Class<?>, Provider<?>> providers = new HashMap<>();

    public <Type> void bind(Class<Type> type, Type instance) {
        providers.put(type, (Provider<Type>) () -> instance);
    }

    public <Type, Implementation extends Type>
    void bind(Class<Type> type, Class<Implementation> implementation) {
        Constructor<Implementation> injectConstructor = getInjectConstructor(implementation);
        providers.put(type, (Provider<Type>) () -> {
            try {
                Object[] dependencies = stream(injectConstructor.getParameters())
                        .map(p -> get(p.getType()).orElseThrow(DependencyNotFoundException::new))
                        .toArray(Object[]::new);
                return injectConstructor.newInstance(dependencies);
            } catch (InvocationTargetException | InstantiationException | IllegalAccessException e) {
                throw new RuntimeException(e);
            }
        });
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

    public <Type> Optional<Type> get(Class<Type> type) {
        return Optional.ofNullable(providers.get(type)).map(provider -> (Type)provider.get());
    }
}

```

任务列表状态为:

![](https://static001.geekbang.org/resource/image/3d/f1/3dbd7ede7cc98a5ea9d1bf275b362ff1.jpg?wh=6259x10979)

## 视频演示

让我们进入今天的部分：

## 思考题

为了我们更好的交流与互动，从这节课开始，思考题目除了固定的技术问题外，我还会设置一道较为轻松的题目，供你选择与回答。

1. 对于依赖的检测，目前代码的实现是在实际创建组件对象时进行的。如果改为预先检查，我们要做哪些改变呢？
2. 在今天这节课中，最让你有收获的地方是什么？为什么？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码的链接分享出来。相信经过你的思考与实操，学习效果会更好！