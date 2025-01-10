你好，我是康杨。

Java 作为一门面向对象的编程语言，在近年来也逐步拥抱了函数式编程。在 JDK 8 中，引入了 Lambda 表达式和 Stream API，为 Java 开发者提供了更简洁、更易读的编写方式。今天我们来详细聊聊JDK 对函数式编程的支持，以及 JDK 中的各种函数式接口，并通过丰富的场景案例和实践，让你轻松掌握 Java 的函数式编程。

## JDK 函数式接口

函数式接口是Java 8引入的一种新特性，它有点像一种“超级接口”，因为它只有一个抽象方法，但却可以以Lambda表达式的形式被实例化和执行。在JDK中，Function、Predicate和Consumer是最常用的函数式接口。在开发过程中，有时候可能我们需要的功能在JDK中并没有现成的实现，但是借助于函数式接口，我们就可以很方便地自定义自己需要的功能。

首先，我们来看看 **Function接口**。在我们的日常生活里也有类似的例子，比如能够把苹果转变为苹果汁的机器，其实就是一个Function，它把一个输入转变为一个输出。在Function接口中，有一个主要的方法，就是apply，它可以把输入的东西转变成输出的东西。例如，我们可以实现一个Function，把字符串变成整数。这个Function就像一个黑盒子，你给它一个字符串，它就会给你一个整数。

如果我们代码里有这样一个Function：

```java
Function<String, Integer> stringToInt =
              s -> Integer.parseInt(s);

```

当我们调用 `stringToInt.apply("123")` 的时候，就能得到整数123。

再来看看 **Predicate接口**。Predicate接口就像一个门卫，它的测试方法test就像检查身份证一样，只有通过检查的才能进去。比如，我们可以写一个Predicate，判断一个字符串列表是否为空。

```java
Predicate<List<String>> listIsEmpty =
              lst -> lst.isEmpty();

```

然后，我们可以使用这个Predicate，检查一个字符串列表。

```plain
List<String> names = Arrays.asList("张三", "李四", "王五");
System.out.println(listIsEmpty.test(names));

```

这样，当字符串列表为空时，输出就是true，否则就是false。

最后，我们来看看 **Consumer接口**。它的accept方法所做的就是消费输入的东西。比如我们可以写一个Consumer，打印出一个字符串列表里所有的名字。

```plain
Consumer<String> printName = name -> System.out.println(name);

```

然后我们就可以把这个Consumer应用到一个字符串列表里，打印出所有的名字。

```plain
List<String> names = Arrays.asList("张三", "李四", "王五");
names.forEach(printName);

```

以上就是JDK中的一些主要的函数式接口，通过这些接口，我们可以更加灵活、方便地进行各种编程任务。

### Function

Function 接口只有一个方法： `apply(T t, R r)`，用来把一个输入映射成一个输出。它的实现类包括：

- Identity：恒等映射，输出与输入相同。
- compose：组合两个函数。
- andThen：在输入经过第一个函数处理后，再经过第二个函数处理。

例如，使用 Function 接口，实现一个字符串转换为整数的函数。

```java
Function<String, Integer> stringToInt = new Function<String, Integer>() {
    @Override
    public Integer apply(String s) {
        return Integer.parseInt(s);
    }
};

```

### Predicate

Predicate 接口只有一个方法： `test(T t)`，用来判断一个输入是否满足某个条件。它的实现类包括：

- Always：始终返回 true。
- Never：始终返回 false。
- isTrue：输入为 null 或为空时返回 false，否则返回 true。
- isFalse：输入为 null 或为空时返回 true，否则返回 false。

例如，使用 Predicate 接口判断一个字符串列表是否为空。

```java
List<String> names = Arrays.asList("张三", "李四", "王五");
Predicate<String> isEmpty = Predicate.isTrue(names.isEmpty());
System.out.println(isEmpty.test(names));

```

### Consumer

Consumer 接口只有一个方法： `void accept(T t)`，用来消费一个输入。它的实现类包括：

- identity：消费输入并返回它本身。
- void：消费输入并返回 void。

例如，使用 Consumer 接口打印一个字符串列表。

```plain
List<String> names = Arrays.asList("张三", "李四", "王五");
Consumer<String> println = System.out::println;
names.forEach(println);

```

## Stream API

Java 的 Stream API 为我们提供了一种全新方便的处理数据的方式。它的特点是强大、灵活且简便，下面我们来详细介绍下。

首先，Stream API 有各种各样的操作，包括转换流、对每个元素进行映射、过滤元素、排序流、归约流以及将流转换回集合。每个操作都有其独特之处和使用场景。

比如说， `stream()` 是一种非常简单的把集合转化为 Stream 的方法。只需要在集合对象后面加上 `.stream()` 就可以了。接下来你就可以在这个 Stream 上进行各种操作，并且它不会改变原有的集合。比如，如果我们有一个整数列表，我们可以用 `.stream()` 把它转化为流，代码如下：

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5); Stream<Integer> stream = numbers.stream();

```

接着我们看看 `map()`， `map()` 非常有用，例如你有一组数据，你想对这些数据操作后得到一组新的数据，这个时候就可以用 `map()`。它的参数是一个函数，这个函数会被应用到流中的每一个元素上。比如，我们可以把上面流里的每个整数转换成它的平方数，代码如下：

```java
Stream<Integer> squareNums = stream.map(n -> n * n);

```

`filter()` 则是从 Stream 中过滤出符合指定条件的元素。举个例子，如果你有一个整数列表，你想从中找出所有的奇数，那你就可以用 `filter((number) -> number % 2 != 0)`。

另外， `sorted()` 可以对 Stream 里的元素进行排序，你可以传递一个自定义比较器或者直接使用默认的比较器。

减少操作的核心是 `reduce()`，这个操作可以从一堆元素中生成一个值。例如，你可以用 `reduce()` 来算出一组数字的总和，或者找到最大的一个数。

最后 `collect()` 就是把 Stream 再转回集合。可能你在 Stream 里做了各种操作，最后你想把它们收集起来放在一个新的集合里，那就用 `collect()`。 `collect()` 可以让你把一个流转化为任何想要的数据结构，比如 List、Set 或者 Map。例如 `stream.collect(Collectors.toList())` 会将流转换回List集合。

以上描述的就是 Stream 主要的一些操作，你可能需要根据实际情况来选择使用哪一种。但是有一件事是肯定的，如果你要操作的是一系列数据，那 Stream API 一定是你的好帮手。

在日常开发过程中，熟练使用 Stream API 可以让我们的程序变得更加简洁，读写性能更加高效，代码级别的抽象程度也更高，这样可以大大提高我们的开发效率。所以说 Java的Stream API是函数式编程的核心，它以声明式的方式处理集合，简化了编程的复杂度，让代码看起来更加简洁明了。Stream API的运用涵盖了许多常用的操作，包括将集合转为流、将集合中的每个元素应用一个函数、筛选满足特定条件的元素、排序、归约操作以及将流转回集合。

## 场景案例与最佳实践

函数式接口在Java中具有重要的作用，它们的存在让我们的代码变得更加简洁而具有表现力。下面我们通过三个具体的示例，详细讲解Function、Predicate和Consumer接口在实际场景中的使用。

### 案例1：计算列表中每个元素的平方

这个案例中，我们使用Function接口来把整数列表里的每个元素转换成它的平方。代码如下：

```java
// 初始化一个整数列表
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// 利用Function接口定义一个算法，输入一个整数，输出这个整数的平方
Function<Integer,Integer> square = n -> n * n;

// 利用Stream API的 map 方法，将算法应用到列表的每个元素
// 用 collect 方法将结果收集到新的列表中
List<Integer> squaredNumbers = numbers.stream()
.map(square)
.collect(Collectors.toList());

// 打印结果
System.out.println(squaredNumbers);

```

在以上代码中，我们创建了一个Function接口的实例，然后把它应用于列表中的每个元素，得到了原列表元素平方后的新列表。

### 案例2：过滤出字符串列表中偶数个字符的字符串

这个案例中，我们使用Predicate接口过滤出字符串列表里具有偶数个字符的字符串。代码如下：

```java
// 初始化一个字符串列表
List<String> names = Arrays.asList("张三", "李四", "王五", "赵六");

// 利用Predicate接口定义一个测试条件，只有字符串长度是偶数的才符合条件
Predicate<String> hasEvenLength = n -> n.length() % 2 == 0;

// 利用Stream API的 filter 方法，对列表中每个元素进行测试，过滤出符合条件的元素
List<String> evenLengthNames = names.stream()
.filter(hasEvenLength)
.collect(Collectors.toList());

// 打印结果
System.out.println(evenLengthNames);

```

在以上代码中，Predicate接口是对符合特定条件的项进行选择的一种方式。在这个示例中，条件就是字符串的长度是偶数。

### **案例3：将字符串列表转换为字符串数组**

这个案例中，我们使用Consumer接口将一个字符串列表转换为一个字符串数组。代码如下：

```java
// 初始化一个字符串列表
List<String> names = Arrays.asList("张三", "李四", "王五");

// 利用Stream API的 toArray 方法，将列表转换为数组
String[] nameArray = names.stream().toArray(String[]::new);

// 用Consumer接口将每个元素打印出来
Consumer<String> printConsumer = System.out::println;
Arrays.asList(nameArray).forEach(printConsumer);

```

在上述代码中，Consumer接口与System.out::println方法结合使用，打印转换后的字符串数组。

以上就是我们如何在实际场景中使用Function、Predicate和Consumer这三个函数式接口的示例。借助这些接口，我们可以以更为简洁、通用的方式实现复杂的功能，无需显式地为每个需求定制特定的方法。

## 开源框架中的应用

### Spring Framework

Spring Framework 提供了基于 Function 接口的 Web 请求处理函数式编程支持，例如：

```java
@GetMapping("/hello")
public Function<HttpServletRequest, String> hello() {
    return request -> "Hello, " + request.getRemoteUser();
}

```

### Apache Commons Lang

Apache Commons Lang 提供了许多实用的工具类，例如：

- FunctionUtils.compose()：组合两个函数。
- FunctionUtils.andThen()：在输入经过第一个函数处理后，再经过第二个函数处理。
- PredicateUtils.always()：始终返回 true。
- PredicateUtils.never()：始终返回 false。

## 重点回顾

Java作为一门面向对象的编程语言，近年来逐步拥抱了函数式编程，通过引入Lambda表达式、Stream API以及函数式接口等特性，提供了更简洁、易读的编写方式。

JDK中的函数式接口包括Function、Predicate和Consumer，它们分别具有将输入映射为输出、判断输入是否满足条件以及消费输入的功能。Stream API则是处理数据的一种强大、灵活且简便的方式，包括转换流、映射元素、过滤元素、排序流、归约流以及将流转换回集合等操作。在日常开发过程中，熟练使用Stream API和函数式接口可以让程序更加简洁、读写性能更高效，提高开发效率。

## 思考题

学而不思则罔，学完这节课之后，我给你留两个问题。

1. JDK提供了 哪些函数式的接口？
2. 尝试用JDK提供函数式接口改造一段现有代码。

希望你认真思考，然后把思考后的结果分享到评论区，我们一起讨论，如果有收获的话，也欢迎你把这节课的内容分享给需要的朋友，我们下节课再见！