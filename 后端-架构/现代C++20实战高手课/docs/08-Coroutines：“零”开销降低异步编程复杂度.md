你好，我是卢誉声。

在上一讲中，我们看到在传统的C++异步方案中，想要实现高效易用的异步方案是非常困难的。好消息是从C++20开始，提供了一个全新的解决异步问题（特别是异步I/O）的方案——那就是协程。

协程提供了泛化的协作式多任务模型，在并发计算和高性能I/O领域有着广泛的应用，相较于多线程或多进程运行时来说，可以实现几乎“零”开销的代码调度。虽说如此，协程并不是一个新概念，早在1958年Melvin E. Conway就提出这一概念，早期的C++也支持基于协程的任务模型编程。

但是，早期C++对协程的支持简陋且不可移植。与此同时，协程在设计上相较于规范函数调用来说更加泛化，因此针对C++的标准化协程方案很难得到一致认可。经过几十年的探索和努力，C++20及其后续演进中终于回归了标准化协程（C++ coroutines）。

由于以往的协程都被编写在非常底层的实现上，因此常见的应用系统上很少使用它。

但这次标准化让它重回大众视野，也启发了我们用另一种思维模式来解决高性能计算问题——通过协程，就能在几乎零性能开销的情况下，大幅降低异步编程复杂度。甚至可以说， **标准化协程促使C++20成长为全新的编程模型**，让我们用现代C++解决工程问题时更加游刃有余。

这是一次令人激动的C++标准化核心语言特性推进。今天，就让我们从定义C++协程开始讲起（课程配套代码，点击 [这里](https://github.com/samblg/cpp20-plus-indepth) 即可获取）。

## 定义C++协程

现代C++20标准下的协程， **是一种可休眠、可恢复、不基于栈实现的函数**。为了方便起见，后续提到的“协程”均特指C++20及其后续演进标准中的协程。

协程相较于函数来说是一个更加泛化的概念。函数只有“调用”和“返回”两个行为，而协程在这一基础上进行了扩展，增加了“休眠”和“恢复”。

![](https://static001.geekbang.org/resource/image/40/98/40d5f8cbec470610713aa2ff94792298.jpg?wh=2600x1285)

与此同时，协程这一核心语言特性不会定义协程的语义，库开发者需要根据一定的规则实现所需的接口约定，包括后面这些约定。

1. 调用者的传参方式。
2. 将值返回给调用者的方式。
3. 休眠与恢复执行的规则。
4. 异常处理方式。

由于C++协程属于无栈协程，因此C++并没有提供标准调度器，开发者必须在定义上述接口后，基于C++提供的关键字在协程调用函数中手动处理协程的调度。

协程的泛化特性在这里进一步展现，编译器在生成协程代码时，会调用库开发者定义的行为——即实现好的、标准的接口规定。

## 协程的执行

在掌握了协程的基本定义后，我们发现协程可以被认作是一种函数的扩展或泛化。为了帮你进一步理解协程的工作机制，让我们来看看协程在运行时的行为和生命周期管理。

前面说过，相较于函数，协程是一种可休眠、可恢复、不基于栈实现的函数。因此，它的生命周期管理自然与普通函数不同。也可以预见，C++中的协程是基于堆来实现的。下图展示了协程与函数交互的过程。

![](https://static001.geekbang.org/resource/image/cc/61/cc47d3703ffb92860743f77641463a61.jpg?wh=2600x1696)

我们根据图中的序号逐一解释每个过程。

1. 调用函数在堆上创建协程帧（coroutine frame），用于存储协程的各类数据。协程帧的结构属于内存模型，因此不同编译器可能会有不同实现。
2. 调用被调协程，开始执行协程代码。
3. 被调协程执行到某个特定点，通过co\_await/co\_yield将当前协程休眠，线程1恢复自身原本的执行流程继续执行剩余代码。co\_await与co\_yield将在下一节中讲解。
4. 线程2通过协程句柄coroutine\_handle的恢复函数resume恢复协程执行。
5. 协程在线程2上恢复执行，继续向下执行，直到协程执行结束为止。结束后回到线程2的原本执行流程继续执行代码。
6. 最后，线程2负责通过协程句柄coroutine\_handle销毁协程帧。

同时，C++中的协程并不会像函数调用那样在栈上执行，它的状态储存在堆上。因此，我们只能在函数调用过程中，通过协程句柄coroutine\_handle改变“部分”协程的状态——恢复或销毁。

## Promise

在讲解协程的执行时，我忽略了一些细节。C++的协程要求开发者实现大量接口约定，而我们很难通过阅读标准文档来编写实际的代码，所以我们有必要学习一下实现接口约定的实践方法，这对我们在C++里熟练应用协程非常重要。

实践里，有两个重要的用户自定义类型Promise和Awaitable。我们先来看看Promise。

![](https://static001.geekbang.org/resource/image/7f/7a/7f872af04d4a6fc947cd17ece4c3387a.jpg?wh=1990x612)

Promise其实是异步编程领域（比如JavaScript）中常见的概念和关键字，它用于描述一个未知值的闭包，闭包在C++中以对象的形式体现。我们可以通过Promise对象提供一个值，而这个值会在未来某个时候计算得出。

![](https://static001.geekbang.org/resource/image/e9/5c/e9d0b8cd08ff6acf2b7ebf0fbfa0065c.jpg?wh=2600x1588)

如上图所示，生成器Generator用来控制协程，包括协程调用、返回值的操作、co\_await/co\_yield的具体行为以及promise\_type的具体定义。那么，这些接口约定该如何实现呢？

我们要从coroutine\_traits这一concept开始说起。标准中提供的代码如下。

```c++
template<class, class...>
struct coroutine_traits {};

template<class R, class... Args>
requires requires { typename R::promise_type; }
struct coroutine_traits<R, Args...> {
  using promise_type = typename R::promise_type;
};

```

从这段代码我们可以看出，实际编程代码中特化的coroutine\_traits必须定义一个公有的promise\_type成员（见代码第7行）。否则，这就不是一个有效的协程类且属于未定义行为。也就是说，编译器会查找协程类中的promise\_type作为Promise，若promise\_type不存在，就会发生编译时报错。

与此同时，一个协程类需要包含三个成员，分别是promise\_type、coroutine\_handle和coroutine\_state。

**promise\_type** 在协程内操作时使用，它必须满足一定规则的类型，包含一系列约束的函数来支持休眠和恢复等功能，包括提交协程的返回值、提交协程异常。通常来说，编译器会通过promise\_type的具体实现来判断协程是否合法。

**coroutine\_handle** 在协程外部操作时使用，可供调用者使用来休眠协程。它的类型是标准库提供的模板类，封装了协程帧的指针以及恢复、销毁协程帧的接口。

**coroutine\_state** 用于支持协程的生命周期，是运行时分配在堆（如果开启了编译器优化选项，则有可能会被优化使用寄存器）上的对象，目的是进一步规范说明协程执行时在堆上创建的数据，包括以下内容。

- promise对象
- 参数（在协程创建时，会拷贝所有函数参数进入协程帧）
- 当前休眠的状态（在运行时，供后续恢复或销毁协程帧使用）
- 局部变量（在运行时，供协程帧使用）
- 临时变量（在运行时，供协程帧使用，它的生命周期是整个协程帧的生命周期）

**coroutine\_state** 参数还可以细分成这两种情况。

- 值类型的参数会被移动或拷贝。
- 引用类型的参数会拷贝引用，当被引用的内存被释放了，那么协程状态中的引用会变成一个野引用。

这三个成员里，coroutine\_state是比较特殊的抽象，是支持协程运行时的。但是，我们需要进一步了解promise\_type和coroutine\_handle的接口约定，并在编写协程时实现它们。

### promise\_type

对于promise\_type，它是实现协程的最关键一环。开发者需要自己来实现它，代码如下所示。

```c++
template<typename T>
struct promise;

template<typename T>
struct Generator : std::coroutine_handle<promise<T>> {
  using promise_type = promise<T>;
};

template<typename T>
struct promise {
  T _value; // 待计算的值
  std::exception_ptr _exception; // 待抛出的异常

  template<typename Ty>
  promise(Ty&& lambdaObj, T value) : _value(value) {}
  promise(T value) : _value(value) {}
  promise() {}

  Generator<T> get_return_object() { return { Generator<T>::from_promise(*this) }; }
  std::suspend_always initial_suspend() noexcept { return {}; }
  std::suspend_always final_suspend() noexcept { return {}; }
  // optional，但co_yield需要这一函数实现
  std::suspend_always yield_value(T value) {
      _value = value;
      return {};
  }
  // optional，但co_return需要这一函数实现或return_void
  std::suspend_always return_value(T value) {
      _value = value;
      return {};
  }
  void return_void() {}
  void unhandled_exception() { _exception = std::current_exception(); }
};

```

关键部分我已经在代码里做了注释，你可以仔细体会一下。

此外，我用下图总结了协程生命周期内，这些接口的一般调用顺序，供你参考使用。

![](https://static001.geekbang.org/resource/image/e2/45/e2be01ae94ba05e6c5090922ed105b45.jpg?wh=2600x1588)

### coroutine\_handle

在了解了promise\_type的结构后，我们再来看看标准库提供的coroutine\_handle这一模版类的定义。在编写协程代码的过程中，我们需要依据这一接口约定来实现。

标准中提供的代码如下。我加了一些注释帮助你理解。

```c++
template<class Promise>
struct coroutine_handle {
  // 构造函数和赋值函数
  constexpr coroutine_handle() noexcept;
  constexpr coroutine_handle(nullptr_t) noexcept;
  static coroutine_handle from_promise(Promise&);
  coroutine_handle& operator=(nullptr_t) noexcept;

  // 导入和导出
  constexpr void* address() const noexcept; // 获取coroutine_handle内部数据的指针
  static constexpr coroutine_handle from_address(void* addr); // 将内部数据指针转换为对应的coroutine_handle对象，会创建一个新对象

  // 转换函数
  constexpr operator coroutine_handle<void>() const noexcept;

  // 查询协程状态
  constexpr explicit operator bool() const noexcept; // 用于确定coroutine_handle是否有效
  bool done() const; // 用于确定协程是否已经执行完成

  // 控制协程执行
  void operator()() const; // 行为同resume，用于唤醒协程
  void resume() const; // 用于唤醒协程
  void destroy() const; // 用于销毁协程

  // 访问Promise对象
  Promise& promise() const;

private:
  void* ptr;  // exposition only
};

template<>
struct coroutine_handle<void> {
  // 构造函数和赋值函数
  constexpr coroutine_handle() noexcept;
  constexpr coroutine_handle(nullptr_t) noexcept;
  coroutine_handle& operator=(nullptr_t) noexcept;

  // 导入和导出
  constexpr void* address() const noexcept;
  static constexpr coroutine_handle from_address(void* addr);

  // 查询协程状态
  constexpr explicit operator bool() const noexcept;
  bool done() const;

  // 恢复协程执行
  void operator()() const;
  void resume() const;
  void destroy() const;

private:
  void* ptr;  // exposition only
};

```

相比于void类型的特化版本，如果开发者指定了promise类型，那么就会用通用版本的coroutine\_handle，这个类多了以下几个成员函数。

- from\_promise：获取promise对应的coroutine\_handle。实际行为会根据promise创建新的coroutine\_handle对象。
- operator coroutine\_handle<>：将promise版本的coroutine\_handle转换为void类型的coroutine\_handle。
- promise：获取coroutine\_handle内部的promise对象。

两个版本最后一行用“exposition only”标识出来的部分，就是coroutine\_handle的内部存储内容，这部分只是为了说明标准做的示例，实际不同编译器可以根据自己的需求定义这里的实现。

## 协程的调度

在了解如何实现协程类型与Promise后，我们还需要学习如何对协程进行调度，包括协程休眠、控制权转移和待计算值的传递。对协程进行调度的关键在于co\_await和co\_yield操作符（关键字）。

### co\_await

co\_await是协程中必须要了解的与编译器的约定。只有了解它，我们才能知道如何通过co\_await灵活处理线程的休眠与唤醒。而搞清楚co\_await操作符的具体行为表现，是我们理解Awaitable的重点，我们就从这个操作符开始讲起。

co\_await操作符用于休眠协程，并将控制权返还给协程调用者，用法如下。

```c++
co_await 表达式;

```

与此同时，co\_await的表达式需要满足下列两个条件之一。

1. 表达式类型必须定义了co\_await操作符重载。
2. 可以通过当前协程的Promise::await\_transform转换为定义了co\_await操作符的类型。

请注意，co\_await只能出现在函数体的执行表达式中，不能出现在异常处理、声明语句、简单声明表达式、默认参数和带static和thread\_local的局部变量定义中。另外，co\_await的执行过程较为复杂，其中涉及到两个类型。

1. Awaitable：用于获取Awaiter对象。
2. Awaiter：用于控制实际的休眠操作细节。

下面通过co\_await的执行过程来看看这两个类型的作用。我们需要将其分为编译时和运行时两个阶段来理解。先看编译时，你可以结合下图来理解。

![](https://static001.geekbang.org/resource/image/yy/c7/yy19b83b2cdc260264e6a899776ab5c7.jpg?wh=3500x4305)

**编译时**，编译器通过以下方式，将表达式转换成Awaitable对象。

- 如果表达式是通过初始休眠点、结束休眠点或yield产生的，那么表达式本身就是Awaitable对象。
- 否则，如果当前协程的promise中包含await\_transform函数，那么就会调用promise.await\_transform将表达式转换为Awaitable对象。
- 否则，表达式本身就是Awaitable对象。

接着，编译器就会通过以下操作获取Awaiter对象。

- 如果Awaitable类型包含co\_await操作符重载，那么就会将co\_await重载的执行结果作为Awaiter。
- 如果没有找到co\_await操作符重载，那么就会将Awaitable对象自身作为Awaiter对象。

接着，我们再了解一下co\_await在运行时的执行过程，如下图所示。

![](https://static001.geekbang.org/resource/image/30/5f/30b1dyy44759ae6364e0d6421d3f325f.jpg?wh=3500x4305)

在 **运行时**，代码会调用Awaiter对象的await\_ready函数，如果该函数返回值为false，那么就会执行以下行为：首先，将协程休眠；然后，使用当前协程的句柄，调用Awaiter对象的await\_suspend(handle)函数。

我们可以在await\_suspend中通过句柄获取到当前协程的各种信息，在自己编写的调度器中选择何时唤醒或者销毁这个协程，你可以参照下表了解不同返回值对应的动作。

![](https://static001.geekbang.org/resource/image/7e/55/7e8dffc7fb0e5a390684e44f8cc1fb55.jpg?wh=2492x1285)

在唤醒协程时，会调用Awaiter的await\_resume函数，并使用该函数的返回值作为co\_await表达式的值。其中，await\_resume函数的执行，会根据await\_ready和await\_suspend的执行结果有所不同。

![](https://static001.geekbang.org/resource/image/de/0a/de0445876d0b3ccae84a2fb045990c0a.jpg?wh=2492x764)

这里可能会有一些关于多线程上执行协程的疑问。 **如果协程的执行涉及在不同线程上执行，会有线程安全问题吗？**

答案其实是不会。协程在进入await\_suspend之前会休眠，因此await\_suspend函数可以将协程句柄传递给任意的线程，而不需要考虑额外的线程同步问题。

举例来说，通过协程处理异步任务，await\_suspend函数是某个Awaiter类的成员函数，其this指针指向Awaiter对象。

![](https://static001.geekbang.org/resource/image/15/7e/1523cf66295f8d588f0544c3cbac877e.jpg?wh=2804x2074)

我们将句柄存储在一个回调函数中（如图中的lambda表达式）。然后，在预先设定的线程池中完成异步任务。最后，调用回调函数利用协程句柄调度唤醒协程。

在这种情况下，代码块2依然会在本线程继续执行，回调函数中的代码则会在其他线程执行。由于其他线程的调度时序是未知的，因此本线程在执行代码块2时，协程可能已经被其他线程唤醒。这种多线程同时访问同一内存块上数据的情况，我们通常称为 **数据竞争问题**。

为了避免出现这种数据竞争问题，将协程句柄传递给其他线程后，await\_suspend后续代码（示例中代码块2）必须假定\*this（也就是调用await\_suspend的Awaiter对象）已经被销毁，并且再也不对其进行访问。

这是一种典型的使用异步I/O处理的场景。我们将在下一讲中，详细阐述如何实现Awaitable和Awaiter对象以及异步I/O处理。

### 生成器和co\_yield

除了co\_await，在协程的上下文中还有一个常见操作符（关键字）——co\_yield，它本质上是co\_await的语法糖，一般用在生成器这种协程的常见场景中。 **那么，什么是生成器呢？**

生成器是基于协程的异步编程中常见的一种编程模式。最常见的应用场景就是，通过生成或其他数据源来获取某种序列。

生成器的核心思路是让协程的调用者和被调用的协程进行协同调度，其中被调用的协程就是生成器。

这个协同调度过程是这样的：首先，调用者唤醒生成器，生成器返回一个值，接着就会主动进入休眠状态；然后，调用者使用这个值来执行相应代码逻辑，然后重新唤醒生成器……这个过程如此往复，直到调用者从生成器获取了所需的值为止。

后面我画了一张过程示意图。

![](https://static001.geekbang.org/resource/image/f6/92/f656b0b9ce6dc9ce789003e348236892.jpg?wh=2600x3293)

从图中可以看出，在生成器这种模式下，主要就是两个操作。

- 调用者作为调度方恢复协程执行。
- 协程将获取或生成的值返回给调用者并继续休眠，等待调用者恢复执行。

而其中的关键就是co\_yield关键字，用法是这样。

```c++
co_yield 表达式;

```

协程可以通过该关键字将表达式的结果传回给调用方并自动休眠。代码等价于：

```c++
co_await promise.yield_value(表达式);

```

可以看出，调用co\_yield的本质就是调用了promise的yield\_value函数，并通过co\_await将自身休眠。

为了进一步帮你理解，我还准备了后面的代码，为你演示一下最简单的生成器模式用法。

```c++
#include <coroutine>
#include <iostream>
#include <cstdint>

struct CountGenerator {
    struct promise_type {
        int32_t _value{ 0 };

        ~promise_type() {
            std::cout << "promise_type 对象销毁" << std::endl;
        }
        CountGenerator get_return_object() {
            return {
              ._handle = std::coroutine_handle<promise_type>::from_promise(*this)
            };
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void unhandled_exception() {}
        std::suspend_always yield_value(int32_t value) {
            _value = value;
            return {};
        }
        void return_void() {}
    };

    std::coroutine_handle<promise_type> _handle;
};

CountGenerator doCount() {
    for (int32_t i = 0; i < 3; ++i) {
        co_yield i;
    }
}

int main() {
    auto h = doCount()._handle;
    auto& promise = h.promise();
    while (!h.done()) {
        std::cout << "计数: " << promise._value << std::endl;
        h();
    }
    h.destroy();

    return 0;
}

```

我在这里定义了一个协程类CountGenerator，比较特殊的是，这个类定义了一个yield\_value成员函数，用于把co\_yield的表达式值存储到promise对象内部，调用者通过这一方式来获取值。

由于调用方不知道协程什么时候结束执行，所以通过coroutine\_handle中的done函数获取运行时状态。如果协程尚未结束执行，就获取相应的值并继续，否则就销毁协程并退出程序。

## 总结

协程是一种可休眠、可恢复的函数，可以实现几乎“零”开销的代码调度，是C++支持异步编程的重要一环，也是彻底迈向现代编程语言的关键标志之一。

一个协程类（Generator类）包含promise\_type、coroutine\_handle、coroutine\_state。但是C++20的协程缺乏具体实现，接口约定都需要开发者来实现。

我们在这一讲中详细阐述了实现这些约定的代码和具体方法，并在这里对promise\_type和Awaitable的接口约定，一并总结成用concept描述的约束表达式，供你今后参考。

```c++
// ============= Promise的Concept定义 ===================
// PromiseType是Promise的类型，ValueType是协程中待计算的值的类型
template<typename PromiseType, typename ValueType>
concept Promise = requires(PromiseType promise) {
  { promise.get_return_object() } -> Coroutine<PromiseType>;
  { promise.initial_suspend() } -> Awaiter;
  { promise.final_suspend() } -> Awaiter;

  requires (requires(ValueType value) { promise.return_value(value); } || { promise.return_void(); })
  { promise.unhandled_exception() };
};

// ============= Awaiter的Concept定义 ===================
// AwaitSuspendResult约束了await_suspend的返回值类型
// AwaiterType是Awaiter的类型，Promise是协程的Promise类型，下同
template <typename ResultType, typename Promise>
concept AwaitSuspendResult = std::same_as<ResultType, void> ||
  std::same_as<ResultType, bool> ||
  std::same_as<ResultType, std::coroutine_handle<Promise>>;

// Awaiter约束定义，Awaiter类型必须满足requires中的所有接口约定
template <typename AwaiterType, typename Promise>
concept Awaiter = requires(AwaiterType awaiter, std::coroutine_handle<Promise> h) {
    awaiter.await_resume();
    { awaiter.await_ready() } -> std::same_as<bool>;
    { awaiter.await_suspend(h) } -> AwaitSuspendResult<Promise>;
};

// ============= Awaitable的Concept定义 ===================
// ValidCoAwait约束用于判断对于AwaitableType是否存在正确的co_await操作符重载
// co_await可以重载为成员函数或者非成员函数，约束中都需要判断
// AwaitableType是Awaitable的类型，Promise是协程的Promise类型，下同
template <typename AwaitableType, typename Promise>
concept ValidCoAwait = requires(AwaitableType awaitable) {
    { awaitable.operator co_await() } -> Awaiter<Promise>;
} || requires(AwaitableType awaitable) {
    { operator co_await(static_cast<AwaitableType&&>(awaitable)) } -> Awaiter<Promise>;
};

// Awaitable约束定义
// Awaitable必须存在正确的co_await操作符重载，或者自身是一个Awaiter
template <typename AwaitableType, typename Promise>
concept Awaitable = ValidCoAwait<AwaitableType, Promise> ||
  Awaiter<AwaitableType, Promise>;

```

因此，我们从整体上看，C++20中提供的coroutines较为粗糙，它仅提供了语言层面的支持，缺乏标准库的支持。我们期待更加成熟的支持会在C++26或后续标准中到来。

## 课后思考

当我们讲解生成器的时候，\_handle和promise都是协程的内部状态，应该不需要让调用方关心。那么，我们该如何修改CountGenerator，才能让调用者无需关心这些内部细节，并直接获取到co\_yield的结果呢？

不妨在这里分享你的方案，与大家一起分享。我们一同交流。下一讲见！

## 课后小知识

![](https://static001.geekbang.org/resource/image/bd/1b/bd0426eyy1b2a951a8f17bff88bbf01b.jpg?wh=2600x1490)

![](https://static001.geekbang.org/resource/image/3f/f6/3fcfb3a4f8cef31ec9bd3451886e5ef6.jpg?wh=2600x1285)