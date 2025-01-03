现在主流的编程范式主要有三种，面向过程、面向对象和函数式编程。在理论部分，我们已经详细讲过前两种了。今天，我们再借机会讲讲剩下的一种，函数式编程。

函数式编程并非一个很新的东西，早在50多年前就已经出现了。近几年，函数式编程越来越被人关注，出现了很多新的函数式编程语言，比如Clojure、Scala、Erlang等。一些非函数式编程语言也加入了很多特性、语法、类库来支持函数式编程，比如Java、Python、Ruby、JavaScript等。除此之外，Google Guava也有对函数式编程的增强功能。

函数式编程因其编程的特殊性，仅在科学计算、数据处理、统计分析等领域，才能更好地发挥它的优势，所以，我个人觉得，它并不能完全替代更加通用的面向对象编程范式。但是，作为一种补充，它也有很大存在、发展和学习的意义。所以，我觉得有必要在专栏里带你一块学习一下。

话不多说，让我们正式开始今天的学习吧！

## 到底什么是函数式编程?

函数式编程的英文翻译是Functional Programming。 那到底什么是函数式编程呢？

在前面的章节中，我们讲到，面向过程、面向对象编程并没有严格的官方定义。在当时的讲解中，我也只是给出了我自己总结的定义。而且，当时给出的定义也只是对两个范式主要特性的总结，并不是很严格。实际上，函数式编程也是如此，也没有一个严格的官方定义。所以，接下来，我就从特性上来告诉你，什么是函数式编程。

严格上来讲，函数式编程中的“函数”，并不是指我们编程语言中的“函数”概念，而是指数学“函数”或者“表达式”（比如，y=f(x)）。不过，在编程实现的时候，对于数学“函数”或“表达式”，我们一般习惯性地将它们设计成函数。所以，如果不深究的话，函数式编程中的“函数”也可以理解为编程语言中的“函数”。

每个编程范式都有自己独特的地方，这就是它们会被抽象出来作为一种范式的原因。面向对象编程最大的特点是：以类、对象作为组织代码的单元以及它的四大特性。面向过程编程最大的特点是：以函数作为组织代码的单元，数据与方法相分离。那函数式编程最独特的地方又在哪里呢？

实际上，函数式编程最独特的地方在于它的编程思想。函数式编程认为，程序可以用一系列数学函数或表达式的组合来表示。函数式编程是程序面向数学的更底层的抽象，将计算过程描述为表达式。不过，这样说你肯定会有疑问，真的可以把任何程序都表示成一组数学表达式吗？

理论上讲是可以的。但是，并不是所有的程序都适合这么做。函数式编程有它自己适合的应用场景，比如开篇提到的科学计算、数据处理、统计分析等。在这些领域，程序往往比较容易用数学表达式来表示，比起非函数式编程，实现同样的功能，函数式编程可以用很少的代码就能搞定。但是，对于强业务相关的大型业务系统开发来说，费劲吧啦地将它抽象成数学表达式，硬要用函数式编程来实现，显然是自讨苦吃。相反，在这种应用场景下，面向对象编程更加合适，写出来的代码更加可读、可维护。

刚刚讲的是函数式编程的编程思想，如果我们再具体到编程实现，函数式编程跟面向过程编程一样，也是以函数作为组织代码的单元。不过，它跟面向过程编程的区别在于，它的函数是无状态的。何为无状态？简单点讲就是，函数内部涉及的变量都是局部变量，不会像面向对象编程那样，共享类成员变量，也不会像面向过程编程那样，共享全局变量。函数的执行结果只与入参有关，跟其他任何外部变量无关。同样的入参，不管怎么执行，得到的结果都是一样的。这实际上就是数学函数或数学表达式的基本要求。我举个例子来简单解释一下。

```
// 有状态函数: 执行结果依赖b的值是多少，即便入参相同，多次执行函数，函数的返回值有可能不同，因为b值有可能不同。
int b;
int increase(int a) {
  return a + b;
}

// 无状态函数：执行结果不依赖任何外部变量值，只要入参相同，不管执行多少次，函数的返回值就相同
int increase(int a, int b) {
  return a + b;
}

```

这里稍微总结一下，不同的编程范式之间并不是截然不同的，总是有一些相同的编程规则。比如，不管是面向过程、面向对象还是函数式编程，它们都有变量、函数的概念，最顶层都要有main函数执行入口，来组装编程单元（类、函数等）。只不过，面向对象的编程单元是类或对象，面向过程的编程单元是函数，函数式编程的编程单元是无状态函数。

## Java对函数式编程的支持

我们前面讲到，实现面向对象编程不一定非得使用面向对象编程语言，同理，实现函数式编程也不一定非得使用函数式编程语言。现在，很多面向对象编程语言，也提供了相应的语法、类库来支持函数式编程。

接下来，我们就看下Java这种面向对象编程语言，对函数式编程的支持，借机加深一下你对函数式编程的理解。我们先来看下面这样一段非常典型的Java函数式编程的代码。

```
public class FPDemo {
  public static void main(String[] args) {
    Optional<Integer> result = Stream.of("f", "ba", "hello")
            .map(s -> s.length())
            .filter(l -> l <= 3)
            .max((o1, o2) -> o1-o2);
    System.out.println(result.get()); // 输出2
  }
}

```

这段代码的作用是从一组字符串数组中，过滤出长度小于等于3的字符串，并且求得这其中的最大长度。

如果你不了解Java函数式编程的语法，看了上面的代码或许会有些懵，主要的原因是，Java为函数式编程引入了三个新的语法概念：Stream类、Lambda表达式和函数接口（Functional Inteface）。Stream类用来支持通过“.”级联多个函数操作的代码编写方式；引入Lambda表达式的作用是简化代码编写；函数接口的作用是让我们可以把函数包裹成函数接口，来实现把函数当做参数一样来使用（Java不像C一样支持函数指针，可以把函数直接当参数来使用）。

**首先，我们来看下Stream类。**

假设我们要计算这样一个表达式：(3-1)\*2+5。如果按照普通的函数调用的方式写出来，就是下面这个样子：

```
add(multiply(subtract(3,1),2),5);

```

不过，这样编写代码看起来会比较难理解，我们换个更易读的写法，如下所示：

```
subtract(3,1).multiply(2).add(5);

```

我们知道，在Java中，“.”表示调用某个对象的方法。为了支持上面这种级联调用方式，我们让每个函数都返回一个通用的类型：Stream类对象。在Stream类上的操作有两种：中间操作和终止操作。中间操作返回的仍然是Stream类对象，而终止操作返回的是确定的值结果。

我们再来看之前的例子。我对代码做了注释解释，如下所示。其中，map、filter是中间操作，返回Stream类对象，可以继续级联其他操作；max是终止操作，返回的不是Stream类对象，无法再继续往下级联处理了。

```
public class FPDemo {
  public static void main(String[] args) {
    Optional<Integer> result = Stream.of("f", "ba", "hello") // of返回Stream<String>对象
            .map(s -> s.length()) // map返回Stream<Integer>对象
            .filter(l -> l <= 3) // filter返回Stream<Integer>对象
            .max((o1, o2) -> o1-o2); // max终止操作：返回Optional<Integer>
    System.out.println(result.get()); // 输出2
  }
}

```

**其次，我们再来看下Lambda表达式。**

我们前面讲到，Java引入Lambda表达式的主要作用是简化代码编写。实际上，我们也可以不用Lambda表达式来书写例子中的代码。我们拿其中的map函数来举例说明一下。

下面有三段代码，第一段代码展示了map函数的定义，实际上，map函数接收的参数是一个Function接口，也就是待会儿要讲到的函数接口。第二段代码展示了map函数的使用方式。第三段代码是针对第二段代码用Lambda表达式简化之后的写法。实际上，Lambda表达式在Java中只是一个语法糖而已，底层是基于函数接口来实现的，也就是第二段代码展示的写法。

```
// Stream中map函数的定义：
public interface Stream<T> extends BaseStream<T, Stream<T>> {
  <R> Stream<R> map(Function<? super T, ? extends R> mapper);
  //...省略其他函数...
}

// Stream中map的使用方法：
Stream.of("fo", "bar", "hello").map(new Function<String, Integer>() {
  @Override
  public Integer apply(String s) {
    return s.length();
  }
});

// 用Lambda表达式简化后的写法：
Stream.of("fo", "bar", "hello").map(s -> s.length());

```

Lambda表达式语法不是我们学习的重点。我这里只稍微介绍一下。如果感兴趣，你可以自行深入研究。

Lambda表达式包括三部分：输入、函数体、输出。表示出来的话就是下面这个样子：

```
(a, b) -> { 语句1； 语句2；...; return 输出; } //a,b是输入参数

```

实际上，Lambda表达式的写法非常灵活。我们刚刚给出的是标准写法，还有很多简化写法。比如，如果输入参数只有一个，可以省略()，直接写成a->{…}；如果没有入参，可以直接将输入和箭头都省略掉，只保留函数体；如果函数体只有一个语句，那可以将{}省略掉；如果函数没有返回值，return语句就可以不用写了。

如果我们把之前例子中的Lambda表达式，全部替换为函数接口的实现方式，就是下面这样子的。代码是不是多了很多？

```
Optional<Integer> result = Stream.of("f", "ba", "hello")
        .map(s -> s.length())
        .filter(l -> l <= 3)
        .max((o1, o2) -> o1-o2);

// 还原为函数接口的实现方式
Optional<Integer> result2 = Stream.of("fo", "bar", "hello")
        .map(new Function<String, Integer>() {
          @Override
          public Integer apply(String s) {
            return s.length();
          }
        })
        .filter(new Predicate<Integer>() {
          @Override
          public boolean test(Integer l) {
            return l <= 3;
          }
        })
        .max(new Comparator<Integer>() {
          @Override
          public int compare(Integer o1, Integer o2) {
            return o1 - o2;
          }
        });

```

**最后，我们来看下函数接口。**

实际上，上面一段代码中的Function、Predicate、Comparator都是函数接口。我们知道，C语言支持函数指针，它可以把函数直接当变量来使用。但是，Java没有函数指针这样的语法。所以，它通过函数接口，将函数包裹在接口中，当作变量来使用。

实际上，函数接口就是接口。不过，它也有自己特别的地方，那就是要求只包含一个未实现的方法。因为只有这样，Lambda表达式才能明确知道匹配的是哪个接口。如果有两个未实现的方法，并且接口入参、返回值都一样，那Java在翻译Lambda表达式的时候，就不知道表达式对应哪个方法了。

我把Java提供的Function、Predicate这两个函数接口的源码，摘抄过来贴到了下面，你可以对照着它们，理解我刚刚对函数接口的讲解。

```
@FunctionalInterface
public interface Function<T, R> {
    R apply(T t);  // 只有这一个未实现的方法

    default <V> Function<V, R> compose(Function<? super V, ? extends T> before) {
        Objects.requireNonNull(before);
        return (V v) -> apply(before.apply(v));
    }

    default <V> Function<T, V> andThen(Function<? super R, ? extends V> after) {
        Objects.requireNonNull(after);
        return (T t) -> after.apply(apply(t));
    }

    static <T> Function<T, T> identity() {
        return t -> t;
    }
}

@FunctionalInterface
public interface Predicate<T> {
    boolean test(T t); // 只有这一个未实现的方法

    default Predicate<T> and(Predicate<? super T> other) {
        Objects.requireNonNull(other);
        return (t) -> test(t) && other.test(t);
    }

    default Predicate<T> negate() {
        return (t) -> !test(t);
    }

    default Predicate<T> or(Predicate<? super T> other) {
        Objects.requireNonNull(other);
        return (t) -> test(t) || other.test(t);
    }

    static <T> Predicate<T> isEqual(Object targetRef) {
        return (null == targetRef)
                ? Objects::isNull
                : object -> targetRef.equals(object);
    }
}

```

以上讲的就是Java对函数式编程的语法支持，我想，最开始给到的那个函数式编程的例子，现在你应该能轻松看懂了吧？

## Guava对函数式编程的增强

如果你是Google Guava的设计者，对于Java函数式编程，Google Guava还能做些什么呢？

颠覆式创新是很难的。不过我们可以进行一些补充，一方面，可以增加Stream类上的操作（类似map、filter、max这样的终止操作和中间操作），另一方面，也可以增加更多的函数接口（类似Function、Predicate这样的函数接口）。实际上，我们还可以设计一些类似Stream类的新的支持级联操作的类。这样，使用Java配合Guava进行函数式编程会更加方便。

但是，跟我们预期的相反，Google Guava并没有提供太多函数式编程的支持，仅仅封装了几个遍历集合操作的接口，代码如下所示：

```
Iterables.transform(Iterable, Function);
Iterators.transform(Iterator, Function);
Collections.transfrom(Collection, Function);
Lists.transform(List, Function);
Maps.transformValues(Map, Function);
Multimaps.transformValues(Mltimap, Function);
...
Iterables.filter(Iterable, Predicate);
Iterators.filter(Iterator, Predicate);
Collections2.filter(Collection, Predicate);
...

```

从Google Guava的GitHub Wiki中，我们发现，Google对于函数式编程的使用还是很谨慎的，认为过度地使用函数式编程，会导致代码可读性变差，强调不要滥用。这跟我前面对函数式编程的观点是一致的。所以，在函数式编程方面，Google Guava并没有提供太多的支持。

之所以对遍历集合操作做了优化，主要是因为函数式编程一个重要的应用场景就是遍历集合。如果不使用函数式编程，我们只能for循环，一个一个的处理集合中的数据。使用函数式编程，可以大大简化遍历集合操作的代码编写，一行代码就能搞定，而且在可读性方面也没有太大损失。

## 重点回顾

好了，今天的内容到此就讲完了。我们一块来总结回顾一下，你需要重点掌握的内容。

今天，我们讲了一下三大编程范式中的最后一个，函数式编程。尽管越来越多的编程语言开始支持函数式编程，但我个人觉得，它只能是其他编程范式的补充，用在一些特殊的领域发挥它的特殊作用，没法完全替代面向对象、面向过程编程范式。

关于什么是函数式编程，实际上不是很好理解。函数式编程中的“函数”，并不是指我们编程语言中的“函数”概念，而是数学中的“函数”或者“表达式”概念。函数式编程认为，程序可以用一系列数学函数或表达式的组合来表示。

具体到编程实现，函数式编程以无状态函数作为组织代码的单元。函数的执行结果只与入参有关，跟其他任何外部变量无关。同样的入参，不管怎么执行，得到的结果都是一样。

具体到Java语言，它提供了三个语法机制来支持函数式编程。它们分别是Stream类、Lambda表达式和函数接口。Google Guava对函数式编程的一个重要应用场景，遍历集合，做了优化，但并没有太多的支持，并且我们强调，不要为了节省代码行数，滥用函数式编程，导致代码可读性变差。

## 课堂讨论

你可以说一说函数式编程的优点和缺点，以及你对函数式编程的看法。你觉得它能否替代面向对象编程，成为最主流的编程范式？

欢迎留言和我分享你的想法，如果有收获，也欢迎你把这篇文章分享给你的朋友。