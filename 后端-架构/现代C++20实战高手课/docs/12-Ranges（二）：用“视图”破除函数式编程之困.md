你好，我是卢誉声。

上一讲，我们重点讨论了C++传统函数式编程的困境，介绍了Ranges的概念，了解到range可以视为对传统容器的一种泛化，都具备迭代器等接口。但与传统容器不同的是，range对象不一定直接拥有数据。

在这种情况下，range对象就是一个视图（view）。这一讲，我们来讨论一下视图，它是Ranges中提出的又一个核心概念，是Ranges真正解放函数式编程的重要驱动力（项目的完整代码，你可以 [这里](https://github.com/samblg/cpp20-plus-indepth) 获取）。

## 视图

视图也叫范围视图（range views），它本质是一种轻量级对象，用于间接表示一个可迭代的序列。Ranges也为视图实现了视图的迭代器，我们可以通过迭代器来访问视图。

对于传统STL中大部分可接受迭代器参数的算法函数，在C++20中都针对视图和视图迭代器提供了重载版本， **比如ranges::for\_each等函数，这些算法函数在C++20中叫做Constraint Algorithm**。

那么Ranges库提供的视图有哪些呢？

我把视图类型和举例梳理了一张表格，供你参考。

![](https://static001.geekbang.org/resource/image/ab/15/ab5c7d5043e35756c8dfe7784cafb615.jpg?wh=3500x1365)

所有的视图类型与函数，都定义在std::ranges::views命名空间中，标准库也为我们提供了std::views作为这个命名空间的一个别名，所以实际开发时我们可以直接使用std::views。

后面是直接使用std::views的代码。后面我再解释iota、take的涵义，你可以先忽略这个细节。

```c++
#include <ranges>
#include <cstdint>
#include <iostream>

int main() {
    for (int32_t i : std::views::iota(1) | std::views::take(4)) {
        std::cout << i << " ";
    }

    return 0;
}

```

## 基础视图接口

了解了视图概念还不够，我们再聊聊C++标准中基础接口的详细设计，以及自定义实现方法。

C++ Ranges定义了一个标准接口ranges::view\_interface（本质是一个抽象类）。我们首先来看一下如何使用该类，自定义自己的视图类。

```c++
template <class Element, size_t Size>
class ArrayView : public std::ranges::view_interface<ArrayView<Element, Size>> {
public:
    using Container = std::array<Element, Size>;

    ArrayView() = default;
    ArrayView(const Container& container) :
        _begin(container.cbegin()), _end(container.cend())
    {}

    auto begin() const {
        return _begin;
    }

    auto end() const {
        return _end;
    }

private:
    typename Container::const_iterator _begin;
    typename Container::const_iterator _end;
};

```

可以看到，代码中定义了ArrayView类，该类型表示array容器的视图。我们定义了三个成员函数。

- 构造函数：包含默认构造函数和通过array对象创建视图的构造函数。构造函数将\_begin和\_end初始化为array的cbegin和cend。
- begin：返回\_begin，Ranges可以通过该函数获取begin迭代器。
- end：返回\_end，Ranges可以通过该函数获取end迭代器。

这样我们就可以将其作为视图来使用，你可以对照示例代码来理解。

```c++
int main() {
    std::array<int, 4> array = { 1, 2, 3, 4 };
    ArrayView arrayView { array };

    for (auto v : arrayView) {
        std::cout << v << " ";
    }
    std::cout << std::endl;

    return 0;
}

```

在这段代码中，创建array对象后创建视图，由于视图类中定义了begin和end成员函数，因此可以用C++的for循环直接遍历这个视图。

除此以外，ranges::view\_interface中还定义了几个成员函数，当视图类满足特定约束时基类会提供默认实现，开发者必要时可以覆盖其实现，具体可以参考后面这张表。

![](https://static001.geekbang.org/resource/image/0e/bc/0e7f4a7a3edf9c55e27187bc73de06bc.jpg?wh=3270x1803)

从这里我们就可以看出视图的本质就是对一个可迭代序列的间接引用，视图自身不存储数据，只是引用了可迭代序列的一部分数据。

虽然Ranges提供了视图的基础接口。但总体来说，我们自己实现所有的视图接口可就太麻烦了。

因此，Ranges提供了视图工厂和适配器，为我们提供了便利的构造视图的方法——这是我们使用视图的主要方法。接下来，我们就来仔细看一下视图工厂与适配器的细节。

### 工厂

视图工厂提供了一些常用的视图类，以及基于这些视图类构建视图对象的工具函数。

我们先来看一段代码，感性地认识一下如何使用视图工厂。

```c++
#include <array>
#include <ranges>
#include <iostream>
#include <sstream>

int main() {
    namespace ranges = std::ranges;
    namespace views = std::views;

    // iota_view与iota
    for (int32_t i : ranges::iota_view{ 0, 10 }) {
        std::cout << i << " ";
    }
    std::cout << std::endl;

    for (int32_t i : views::iota(1) | views::take(4)) {
        std::cout << i << " ";
    }
    std::cout << std::endl;

    // istream_view与istream
    std::istringstream textStream{ "hello, world" };
    for (const std::string& s : ranges::istream_view<std::string>{ textStream }) {
        std::cout << "Text: " << s << std::endl;
    }

    std::istringstream numberStream{ "3 1 4 1 5" };
    for (int n : views::istream<int32_t>(numberStream)) {
        std::cout << "Number: " << n << std::endl;
    }

    return 0;
}

```

在这段代码中，我们使用了两个视图工厂——ranges::iota\_view和ranges::istream\_view。

views::iota是ranges::iota\_view的工具函数，有了它，就能更方便地创建一个iota\_view对象。调用views::iota时，我们也使用了视图适配器views::take(4)创建一个新视图，包含前一个视图的前4个元素。类似于L \| R这种语法就是所谓的视图管道，允许我们将多个视图连接在一起，让分步的数据处理变得简洁优雅。

另一个视图工厂是ranges::istream\_view，作用是创建一个从输入流中不断读取数据的视图类。在遍历这个视图的时候，视图会尝试从输入流中读取数据，直到输入流结束为止。views::istream（也就是ranges::istream\_view的工具函数），可以返回一个istream\_view对象。

由此可见，使用视图工厂是非常简单的。后面表格里整理了C++20中提供的所有工厂，供你参考。

![](https://static001.geekbang.org/resource/image/24/bb/24cffca4f0693a29f950ae0afb6e59bb.jpg?wh=2970x1444)

除此之外，还有一些在C++23中提供的新视图工厂，待后续讨论C++23时我再介绍。

### 适配器

除了直接创建视图，Ranges还提供了一系列工具，可以将一个或者多个视图转换成一个新的视图，用来支持数据处理和运算工作。

这些用视图作为参数的“工厂”就是视图适配器。比如说，上一节中用到的views::take返回的就是类型为take\_view的视图适配器对象。

Ranges也支持通过嵌套和组合的方式来使用视图适配器。后面的例子是一个典型的函数式编程案例。

```c++
#include <vector>
#include <ranges>
#include <iostream>
#include <random>
#include <algorithm>

int main() {
    namespace ranges = std::ranges;
    namespace views = std::views;

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(1, 10);

    // 步骤6：输出
    ranges::for_each(
        // 步骤5：将键值对序列[(0,a1),(1,a2),...,(n, an)]转换为[0+a1,1+a2,...,n+an]的求和序列
        views::transform(
            // 步骤4：选取结果键值对的至多前3个键值对（不足3个则全部返回）
            views::take(
                // 步骤3：从随机数键值对中筛选数值大于5的键值对
                views::filter(
                    // 步骤2：生成随机数键值对序列[(0,a1),(1,a2),...,(n, an)]
                    views::transform(
                        // 步骤1：生成序列[0,10)
                        views::iota(0, 10),
                        [&distrib, &gen](auto index) { return std::make_pair(index, distrib(gen)); }
                    ),
                    [](auto element) { return element.second > 5;  }
                ),
                3
            ),
            [](auto element) { return element.first + element.second; }
        ),
        [](auto number) {
            std::cout << number << " ";
        }
    );
    std::cout << std::endl;

    return 0;
}

```

这段代码是一个典型的函数式编程案例。你可以结合代码来理解这几个步骤。

第一步，使用views::iota生成一个\[0,10)的等差序列，相当于一个range。

第二步，使用views::transform为等差序列中的每一个数生成一个随机数，返回一个由随机数键值对组成的序列，序列形式为\[(0,a1),(1,a2),…,(n, an)\]。

第三步，使用views::filter从随机数键值对序列中筛选所有随机数大于5的键值对，生成一个新的序列。

第四步，使用views::take从filter输出的键值对序列中选取前3个键值对，如果filter输出的数量不足3个则返回所有元素，也就是这里肯定不会产生越界。

第五步，使用views::transform将take返回的键值对序列\[(0,a1),(1,a2),…,(n, an)\]转换为\[0+a1,1+a2,…,n+an\]的求和序列。

第六步，使用views::for\_each输出结果。

我们可以看出，整段代码是用嵌套函数的形式编写的，而且在transform、filter和for\_each中，都使用了Lambda表达式作为高阶函数。这段编码已经非常简洁了，除了部分C++无法避免的语法特性，可读性堪比其他函数式编程语言。

不过，如果你还不熟悉函数式编程，那么看到这种深度的括号嵌套应该会感到非常头痛。对此，我跟你说一个有关Lisp的地狱笑话。

> 某个程序员偷到了一个系统代码的最后一页，结果发现那一页上全部都是右括号。

或许，你现在应该理解了这个笑话的梗在哪里。

如果我们要用传统STL算法来实现这个函数式编程的过程，大概情况会是这样的。

```c++
#include <vector>
#include <iostream>
#include <random>
#include <algorithm>
#include <numeric>

int main() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(1, 10);

    std::vector<int> rangeNumbers(10, 0);
    std::iota(rangeNumbers.begin(), rangeNumbers.end(), 0);

    std::vector<std::pair<int, int>> rangePairs;
    std::transform(rangeNumbers.begin(), rangeNumbers.end(), std::back_inserter(rangePairs), [&distrib, &gen](int index) {
        return std::make_pair(index, distrib(gen));
    });

    std::vector<std::pair<int, int>> filteredPairs;
    std::copy_if(rangePairs.begin(), rangePairs.end(), std::back_inserter(filteredPairs), [](const auto& element) {
        return element.second > 5;
    });

    std::vector<std::pair<int, int>> leadingPairs;
    std::copy_n(filteredPairs.begin(), 3, std::back_inserter(leadingPairs));

    std::vector<int> resultNumbers;
    std::transform(leadingPairs.begin(), leadingPairs.end(), std::back_inserter(resultNumbers), [](const auto& element) {
        return element.first + element.second;
    });

    std::for_each(resultNumbers.begin(), resultNumbers.end(), [](int number) {
        std::cout << number << " ";
    });

    return 0;
}

```

由于传统算法为了通用性，所以算法函数的输入都是迭代器，我们也就不得不创建大量的临时变量存储中间结果。有了对比，我们可以直观感受到，相比采用视图的方法，传统STL算法写的代码可读性就差了很多，而且也没有提供越界检查功能。

除了上述案例中用到的适配器，Ranges还提供了大量的适配器。如果你感兴趣的话，可以查一下<ranges>头文件的文档，进一步了解所有的适配器。

### 视图管道

在实际编码时，虽然有适配器的帮助，但是大量的函数嵌套还是非常影响代码可读性。为此，C++还提供了视图管道（pipeline）来帮助我们更好地组织代码。比如前面的代码就还有改进空间，我们可以修改成后面这样。

```c++
#include <vector>
#include <ranges>
#include <iostream>
#include <random>
#include <algorithm>

int main() {
    namespace ranges = std::ranges;
    namespace views = std::views;

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(1, 10);

    ranges::for_each(
        views::iota(0, 10) |
        views::transform([&distrib, &gen](int index) { return std::make_pair(index, distrib(gen)); }) |
        views::filter([](const auto& element) { return element.second > 5;  }) |
        views::take(3) |
        views::transform([](const auto& element) { return element.first + element.second; }),
        [](int number) {
            std::cout << number << " ";
        }
    );
    std::cout << std::endl;

    return 0;
}

```

这个代码中，除了ranges::for\_each属于算法函数，其他的嵌套视图都修改成了通过\|这个视图管道操作符连接的形式。比如原本代码中的transform(iota(), fn)，我们可以修改成iota() \| transform(fn)这种形式。

所谓的视图管道依赖于 **Range适配器对象（range adaptor object）** 这个概念。简单来说，Range适配器对象需要重载operator()操作符，并且满足后面这三个条件。

1.参数列表为(R, …args)。

2.第一个参数是另一个Range适配器对象R。

3.可以存在后续参数…args，也可以不存在后续参数。

也就是说，Range适配器对象必定是一个仿函数（functor）。由于第一个参数可以接收另一个适配器对象，因此我们可以像上一节中那样实现视图适配器的嵌套。 **那么视图管道又是怎么实现的呢？**

首先，Range适配器对象中有一个特例，就是如果后续参数…args不存在时，我们就把这种适配器对象叫做 **range适配器闭包对象（range adaptor closure object）**。假设有一个适配器闭包对象C，其参数列表只有一个参数R，并且R也是一个适配器对象，那么我们可以这样将两者嵌套调用。

```c++
C(R)

```

这时，C++ Ranges就提供了视图管道，让我们可以将这种函数调用写成：

```c++
R | C

```

所以视图管道，本质上就是一个对 “range适配器闭包对象函数调用”的语法糖。

那么， **普通的Range适配器对象如何转换成闭包对象呢**？很简单，只需要将除了第一个参数的后续参数…args通过binding绑定上固定的参数，生成只有一个参数的偏函数就可以了。

此外，视图管道还可以复合使用，假设R、C和D都是range适配器闭包对象，我们就可以写成这样。

```c++
R | C | D
(R | C) | D
D(C(R))

```

这三者是完全等价的。所以可以看出 \| 管道操作符的结合方向是自左向右结合。如果想要改变结合性，我们可以使用括号，后面这种形式代码就是等价的。

```c++
R | (C | D)
D(C)(R)

```

这样一来，通过视图管道和视图适配器，我们就能组织出C++中非常优雅的函数式代码了。

需要额外说明的是，C++20中暂时只能使用标准库中定义的视图类型，我们自己哪怕实现了满足range适配器闭包对象的接口也无法在视图管道中使用，用户自定义的适配器闭包对象类型在C++23中才会得到支持。不过现阶段我们也有变通的方法可以将自定义的类型组合到视图管道中，我们将会在下一讲中具体讨论。

## 总结

通过两讲的内容，我们一起了解了Ranges的来龙去脉。

这一讲我们学习了Ranges的另一个重要概念——视图，我们通过它来间接引用特定范围的数据，而非拥有数据。在视图的基础上，通过视图工厂、视图适配器和视图管道，我们可以让复杂的数据处理变得简洁优雅。

我们还讨论了range适配器闭包对象，这种对象只需要满足后面三个条件中的一个。

1.只有一个参数，参数类型为Range适配器对象。

2.将另一个range适配器对象的后续参数…args绑定固定参数后生成的仿函数（functor）。

3.使用视图管道操作符 \| 连接两个range适配器闭包对象后返回的对象。

## 课后思考

我们在讨论Ranges视图适配器的时候，曾提到除了课程里用到的适配器，Ranges还提供了大量的适配器。你能否查阅相关文档进一步了解这些适配器，并结合一段简短的代码来展示其使用？

欢迎把你的代码贴出来，与大家一起分享。我们一同交流。下一讲见！