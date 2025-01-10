你好，我是卢誉声。

最近一段时间，AIGC和GPT技术的讨论十分火热。甚至我在跟跨行业的朋友聊天时，ChatGPT也成了绕不开的饭后谈资——这其实很容易理解，毕竟新闻、媒体在涉及相关技术的时候，标题会非常吸引眼球，而且容易引发“焦虑”。

类似的，AIGC技术也可能会对软件工程领域产生深远影响。这次加餐，我想通过我对AIGC技术的理解以及一些案例，简单分析一下软件工程师的生存指南，和你聊聊这件事是否值得我们“焦虑”。

## 怎么理解AIGC

首先，我们先来梳理一下AIGC、GPT以及ChatGPT这几个词的含义和关系。

所谓AIGC，全称是Artifcial Intelligence Generated Content，即“AI生成内容”。生成模型一直是AI研究中的重要分支，而AIGC的提出意味着Al生成数据的能力越来越成熟，也越来也越值得重视。

按照模态来划分，AIGC有文本生成、音频生成、图像生成、视频生成及基于它们的多模态生成等。

![](https://static001.geekbang.org/resource/image/74/b4/74d4a0801dc545309bd126dbab284bb4.jpg?wh=3700x2099)

而 **GPT** 就属于AIGC中的文本生成，全称是Generative Pre-trained Transformer，即“生成式预训练变形器”。

另外还有 **ChatGPT**，它是由OpenAI建立在GPT模型基础上的特定变体模型，专注于提供对话生成和回应的能力。它旨在模拟自然语言的对话过程，并与用户进行交互。

#### ChatGPT with GPT-4：AIGC技术的集大成

目前ChatGPT中使用的GPT-3.5是一种通过自然语言描述“意图”就能生成答案的技术，它是在GPT-3的基础上实现的。

GPT-3通过大规模参数和上下文学习推测用户的意图。到了GPT-3.5，通过融入基于人工标注的指令学习，就能更精准地预测人的意图，从而得到更好的生成效果。

GPT-4是一种多模态模型，而GPT-3.5是一种自然语言处理模型。简单来说，就是自然语言模型只能听或看懂语言，而多模态模型可以处理多种媒体数据，并且将它们整合到统一的语义空间之中。

不过，从某个层面来说，ChatGPT其实很难被定义成一种革命性技术。当然了，即便是革命性技术，也是基于过去的技术构建、发展而来。每一代新技术的基石往往就是上一代技术。

就目前来看，ChatGPT还无法处理非常复杂的“意图”组合，尤其在“意图”之间逻辑关系非常复杂时，就很难避免生成不符合实际逻辑内容的情况。虽然现在ChatGPT能通过“插件”检索知识库，一定程度上弥补了这一点，但实际这个也就和GPT本身没什么关系了。

#### ChatGPT with GPT-4与C++

现在，让我们回到软件工程师这个身份上来，讨论一下ChatGPT能否解放开发效率、甚至代替我们的日常工作？先给出我的结论—— **现在不能，将来也比较困难。**

**首个版本**

我现在期望用ChatGPT with GPT-4生成一份非常基本的代码，给出的Prompt是后面这样。

> Write a simple, asynchronous, invoking file I/O framework in C++20 coroutine. The framework should accept lambda function as argument. The degree of parallelism is 6.

可以看到，ChatGPT首次生成的代码中纯粹使用了std::thread来实现异步，忽略了C++20 coroutine这一关键点。

因此，我接着问：“You need to provide the definition of promise\_type.”。这次，它给了我一份“至少方向对了”的代码。

```c++
#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <experimental/coroutine>
#include <future>

template<typename T>
struct Future {
    std::promise<T> p;
    std::future<T> f = p.get_future();
    Future() {}
    Future(Future&&) = default;
    Future(const Future&) = delete;
    struct promise_type {
        Future* fut = nullptr;
        auto get_return_object() {
            return Future{};
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_never final_suspend() { return {}; }
        void unhandled_exception() { std::terminate(); }
        template<typename U>
        void return_value(U&& u) {
            fut->p.set_value(std::forward<U>(u));
        }
    };
};

// Placeholder function, replace with your actual implementation
Future<std::string> async_read_file(const std::string& path) {
    return std::async([path] {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        return std::string("File content: ") + path;
    });
}

// Coroutine that reads a file asynchronously
Future<std::string> read_file(const std::string& path) {
    co_return co_await async_read_file(path);
}

// Invoking framework
void invoke(const std::vector<std::string>& paths, const std::function<void(const std::string&)>& lambda) {
    std::vector<std::future<void>> tasks;

    for (const auto& path : paths) {
        // Wait for an available slot
        if (tasks.size() >= 6) {
            auto it = std::find_if(tasks.begin(), tasks.end(), [](const std::future<void>& task) { return task.wait_for(std::chrono::seconds(0)) == std::future_status::ready; });
            while (it == tasks.end()) {
                std::this_thread::yield(); // Yield this thread to not busy-wait
                it = std::find_if(tasks.begin(), tasks.end(), [](const std::future<void>& task) { return task.wait_for(std::chrono::seconds(0)) == std::future_status::ready; });
            }
            lambda(it->get());
            tasks.erase(it);
        }

        tasks.push_back(std::async(std::launch::async, [&, path] {
            auto content = read_file(path).get();
            return content;
        }));
    }

    // Wait for remaining tasks
    for (auto& task : tasks) {
        lambda(task.get());
    }
}

// Usage:
int main() {
    std::vector<std::string> paths = {"file1", "file2", /*...*/ "fileN"};

    invoke(paths, [](const std::string& content) {
        // Process the file content
        std::cout << "File content: " << content << std::endl;
    });

    return 0;
}

```

**编译代码**

现在我们尝试编译代码——哦，出现了太多错误，你可以参考后面的截图。

![](https://static001.geekbang.org/resource/image/4f/52/4fc588117ff453ab98eb91ddceedf652.jpg?wh=3700x1149)

```c++
fatal  error C1189: #error:  The <experimental/coroutine> and <experimental/resumable> headers are only supported with /await and implement pre-C++20 coroutine support. Use <coroutine> for standard C++20 coroutines.

```

嗯，这个问题是C++20已经支持coroutine而不是用experimental/coroutine了，我们尝试将这个错误抛给ChatGPT，看看它能否自动修正错误。

不错，ChatGPT成功修正了头文件错误。

```c++
//
#include <coroutine>  // replaced <experimental/coroutine>
#include <future>
//

```

但是编译过程在继续报错，比如下面这个错误。

```c++
error C2440: “return”: 无法从“std::future<_Ty>”转换为“Future<std::string>”
1>        with
1>        [
1>            _Ty=std::string
1>        ]

```

因此，我告诉ChatGPT：

> Now the compiler tells me: std::future<std::string> can’t be converted to Future<std::string>

头文件都修复了，这个类型转化问题岂不是小菜一碟？ChatGPT很快就给了我们答案。但是，问题接踵而来，我们继续往下看。

```c++
// Placeholder function, replace with your actual implementation
Future<std::string> async_read_file(const std::string& path) {
    std::promise<std::string> p;
    std::thread([p = std::move(p), path]() mutable {
        std::this_thread::sleep_for(std::chrono::seconds(1)); // simulate delay
    p.set_value(std::string("File content: ") + path);
        }).detach();
        return Future<std::string>{p.get_future()};
}

```

Oh, no，还是有错误。

```c++
error C2440: '<function-style-cast>': cannot convert from 'initializer list' to 'Future<std::string>'

```

Future类根本没有这个构造函数，怎么能这样构建Future对象呢？于是我向ChatGPT告知编译器错误消息，希望可以修正这个问题。

在给出Prompt后，新结果真就是换汤不换药，我依然得到上面的错误，于是我再次将这个问题抛给ChatGPT。

> Still error:
>
> error C2440: ‘<function-style-cast>’: cannot convert from ‘initializer list’ to ‘Future<std::string>’

ChatGPT飞快地认错了，并且给出了新答案。

> I apologize for the confusion. I misunderstood the error previously. The issue is related to how the Future object is being constructed. Let’s modify the promise\_type and Future constructor to make this work correctly.

```c++
template<typename T>
struct Future {
    std::promise<T> p;
    std::shared_future<T> f;
    Future() {}
    Future(std::promise<T>&& p) : p(std::move(p)), f(this->p.get_future()) {}
    Future(Future&&) = default;
    Future(const Future&) = delete;

    struct promise_type {
        std::promise<T> p;
        Future<T> get_return_object() {
            return Future<T>{std::move(p)};
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void unhandled_exception() { std::terminate(); }
        void return_value(T value) { p.set_value(std::move(value)); }
    };

    bool await_ready() const noexcept { return f.wait_for(std::chrono::seconds(0)) == std::future_status::ready; }
    void await_suspend(std::coroutine_handle<> h) { f.wait(); }
    T await_resume() { return f.get(); }
};

```

嗯，它还补充了一句修改的理由。

> In this modification, we’ve added a new constructor to Future that takes a std::promise<T> by rvalue reference and initializes f from it. Then, in get\_return\_object, we’re moving the promise p into this

很可惜，这次的修改代码还是错误的。既然事不过三（其实我尝试了更多次），我们发现，ChatGPT明显无法区分清楚Future和std::future，于是我再给了ChatGPT一次机会，明确反馈了这个问题。

> No, it’s not working.
>
> Future<std::string> doesn’t have constructor of std::future<std::string>.
>
> Future isn’t std::future
>
> Please give me the new complete code

ChatGPT很快给出了后面的回复。

> I apologize for the confusion earlier. You’re correct, and I appreciate your patience. We need to properly construct the Future and its promise\_type. Here is a revised version:

接着给出了新生成的代码。

```c++
#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <coroutine>
#include <future>

template<typename T>
struct Future {
    std::shared_future<T> f;

    Future(std::shared_future<T>&& f) : f(std::move(f)) {}

    bool await_ready() const noexcept { return f.wait_for(std::chrono::seconds(0)) == std::future_status::ready; }
    void await_suspend(std::coroutine_handle<> h) { f.wait(); }
    T await_resume() { return f.get(); }

    struct promise_type {
        std::promise<T> p;

        auto get_return_object() {
            return Future{p.get_future()};
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void unhandled_exception() { std::terminate(); }
        void return_value(T value) { p.set_value(std::move(value)); }
    };
};

// Placeholder function, replace with your actual implementation
Future<std::string> async_read_file(const std::string& path) {
    std::promise<std::string> p;
    std::thread([p = std::move(p), path]() mutable {
        std::this_thread::sleep_for(std::chrono::seconds(1)); // simulate delay
        p.set_value(std::string("File content: ") + path);
    }).detach();
    return p.get_future();
}

// Coroutine that reads a file asynchronously
Future<std::string> read_file(const std::string& path) {
    co_return co_await async_read_file(path);
}

// Invoking framework
void invoke(const std::vector<std::string>& paths, const std::function<void(const std::string&)>& lambda) {
    std::vector<Future<void>> tasks;

    for (const auto& path : paths) {
        // Wait for an available slot
        if (tasks.size() >= 6) {
            auto it = std::find_if(tasks.begin(), tasks.end(), [](const Future<void>& task) { return task.await_ready(); });
            while (it == tasks.end()) {
                std::this_thread::yield(); // Yield this thread to not busy-wait
                it = std::find_if(tasks.begin(), tasks.end(), [](const Future<void>& task) { return task.await_ready(); });
            }
            lambda(it->await_resume());
            tasks.erase(it);
        }

        tasks.push_back(std::async(std::launch::async, [&, path] {
            auto content = read_file(path).await_resume();
            return content;
        }));
    }

    // Wait for remaining tasks
    for (auto& task : tasks) {
        lambda(task.await_resume());
    }
}

// Usage:
int main() {
    std::vector<std::string> paths = {"file1", "file2", /*...*/ "fileN"};

    invoke(paths, [](const std::string& content) {
        // Process the file content
        std::cout << "File content: " << content << std::endl;
    });

    return 0;
}

```

到最后，ChatGPT还是没有解决这个问题。通过阅读和编译，我们不难发现这段代码还有非常多的问题。

首先是 **逻辑错误**。比如代码12行，std::shared\_future的作用是允许多个线程可以在一个future对象上等待线程返回的结果，因此一般不需要定义移动构造函数，移动构造函数往往会用在std::future这种线程不安全的类型上。

接下来还有 **编码错误**。这个就很多了，比如我们最后来看下这段代码产生的错误。

```c++
错误    C2664    “_Ret std::_Func_class<_Ret,const std::string &>::operator ()(const std::string &) const”: 无法将参数 1 从“T”转换为“const std::string &”    cg-cr-demo    main.cpp    58
错误    C2664    “_Ret std::_Func_class<_Ret,const std::string &>::operator ()(const std::string &) const”: 无法将参数 1 从“T”转换为“const std::string &”    cg-cr-demo    main.cpp    70
错误    C2665    “std::vector<Future<void>,std::allocator<Future<void>>>::push_back”: 没有重载函数可以转换所有参数类型    cg-cr-demo    main.cpp    62
错误    C2440    “return”: 无法从“std::future<_Ty>”转换为“Future<std::string>”    cg-cr-demo    main.cpp    38

```

可以发现，ChatGPT生成的这段代码最大的问题就是围绕Coroutine和Promise的类型定义引发的各种参数和返回值的类型转换问题，更不用说代码自身的逻辑，根本就无法解决我们提出的问题。

还有 **理解错误**。我们只期望invoke函数接收一个lambda函数，并没有要求invoke函数接收一个路径数组，因为我们希望可以循环调用这个函数将执行任务放入协程的执行队列中，并且通过闭包将参数闭包到lambda函数上下文中。

其实还有 **其他问题**。我们看一下代码第42行，read\_file其实是一个无用的包装函数，理论上直接调用async\_read\_file就行了，否则还需要通过协程框架多调度一次；另外第55行里，std::this\_thread::yield的实现在不同平台上并不一致，因此如果我要用这个函数让出线程执行权需要充分考量。

## 工程难题

工业界的编程问题往往伴随着海量的上下文信息，以及大量依赖于第三方的开发工具、SDK。ChatGPT难以获取这些上下文，很难有效解决工程难题。

因此，使用ChatGPT生成简单任务的代码是最低级的用法、也是GPT最擅长的。如果想要解决复杂的任务，我们要先对任务进行分解，然后分层次、分步骤地让ChatGPT给出相应的答案。

在整体结构相当复杂的情况下，软件工程师的丰富经验和对整体系统架构的理解必不可少。也就是说，解决工程难题永远脱离不开人的思维。

所以如果你能理解ChatGPT的原理，就能充分利用它在合理的场景下帮你解决问题。即使用ChatGPT和自然语言解决编程问题——由此引出“自然语言编程”这一概念。

由于ChatGPT技术的出现，自然语言编程终于有了一个较为实际的实验平台。回想编程语言的演进，我们发现高级编程语言相较于汇编是一次巨大的生产力提升，同时也是一次高级抽象的完美演绎。而对于自然语言编程来说，很可能是未来的发展方向之一（不是唯一的演进方向）。

这么说的原因在于：ChatGPT生成的内容，是一种通过“意图”生成的“大致准确的结果”。这与通过“需求”生成的“精确的结果”之间，在工业界存在着巨大鸿沟。

![](https://static001.geekbang.org/resource/image/85/7d/851a0a10643958886c9210ce47fab87d.jpg?wh=3721x2080)

从上面的 _“ChatGPT with GPT-4与C++”_ 一节就可以看出，如何准确地表达意图是一门学问，提示词（prompt）往往特别重要。总的来说，现阶段自然语言编程不能代替高级编程语言，因为后面这几个问题还无法解决。

第一，工程师如何精准地表达自己的“意图”，避免GPT错误理解意图，生成错误的结果。

第二，GPT的参数规模虽然足够大，但参数数量始终是有限的，因此上下文空间受限，不可能生成无限复杂的代码。

第三，GPT本质并没有学习知识之间的关系，在没有完备的先验知识下可能生成逻辑相悖的内容，而且对生成内容的人工限制能力较弱（目前一部分可以通过Plugin接入知识库解决）。

因此，如何精准表达自己的“意图”，对用好ChatGPT模型非常重要。当然了，精准的表达意图同样依赖于经验丰富的软件工程师。而生成的内容，还需要经验丰富的工程师来进一步验证其准确性。

根据我使用ChatGPT with GPT-4的经验来说，它很容易生成一些存在安全缺陷的代码，甚至会生成一些完全错误的代码，而且这些代码许可证协议我们无从得知，更重要的是它们是否被版权保护？这些都是目前使用ChatGPT模型的风险。

这些问题都离不开“工程难题”，而自然语言编程与高级编程语言之间仍然存在巨大鸿沟。就目前来说，不要指望ChatGPT模型能够帮你完成所有工作，它还处在一个日新月异的阶段，每天都汲取更多的知识，它的AI模型也在快速进化。

## 积极拥抱AIGC

我在深深感叹AIGC技术演进的速度，单从ChatGPT将GPT-3.5升级到GPT-4来说，OpenAI在短短时间内就大幅提升了训练参数个数，实现了多模态模型，这在以往的技术迭代和发展中是几乎找不到的——这是现象级的技术进化，也是一种量变引起的质变。

不过，AIGC包罗万象。ChatGPT现在无法解决的工程难题，不代表不会被后续的新模型解决。同时，在软件工程领域提高生产力还有很长的路要走，但我们其实已经能够通过ChatGPT来提升工作效率了。

比如说，通过ChatGPT快速生成功能单一的代码片段，然后通过代码审阅、错误或漏洞修复来调整生成的内容，让它能够融入我们的软件开发工作中。看到了么？AIGC技术不能代替我们，它生成的内容需要经过工程师的审计、评估和再集成——它们会成为我们的得力助手，在未来会是生产力工具。

因此，我们需要拥抱AIGC技术，了解、掌握并善加利用。

#### 思想转变往往是困难的

不过，变化往往伴随着痛苦。我想在每次发生技术变革的时候，这种阵痛都难以避免。比如汇编时代过渡到高级编程语言时代，我们就得学习和掌握不同的编程范式（比如面向对象编程、函数式编程）。

我在构想了一种即将到来的工作流，那就是通过prompt和GPT模型生成的内容，外加软件工程师的审查、调优，提高解决局部工程问题的效率——由此构成新的工作流和思想。

因此，了解、学习和掌握AIGC技术有必要，但是，扎实的基本功才能让你不被GPT模型生成的内容误导。毕竟，真正了解整个系统架构的、集成这些简单代码片段的人，还得是软件工程师。

#### 小心AIGC陷阱

AIGC并不是什么新的概念，只是近几年由于数据规模爆炸、算力提升以及新的理论模型的提出，让它终于有了可以落地的可用产品，比如ChatGPT就是其中一颗闪耀的明星。当然，也正是因为这类明星产品落地，让更多人开始注意到AI技术的实力和潜力。

不过，我们需要警惕AIGC陷阱，避免让错误的人或错误的内容把自己带入沟里。你不值得在这种内容上投入时间和精力——你总有更重要和值得的事情做。

用已知解释ChatGPT，是一种狭隘、错误的思维模式。比如：ChatGPT只是更高效的搜索引擎，只不过他使用聊天交流的方式提供的——不能拿历史上现有事物来类比大语言模型。

另外，我想分享两个标题。

> “ChatGPT新手秘籍”“10招玩转ChatGPT”

这两个标题是我临时想的，欢迎大家在评论区补充。像是这种内容你要小心， **技术变革发生的时候，技巧是次要的，更新自己的认知才更加重要。**

## 巨大技术变革的前夜

我们现在处于巨大技术变革的前夜，为了应景，我还在文稿里配了一张在曼哈顿拍的照片。

![](https://static001.geekbang.org/resource/image/3a/c7/3ac13673cb4ac7c4a70cac44489e4bc7.jpg?wh=3017x2654)

首先，不可否认ChatGPT的确是一个强大的工具，在部分领域，比如文书撰写、修饰、检索、简单编程代码生成，已经基本可以直接替代人工。

但是，如果想要完成复杂任务，就必须有人工介入。需要人在了解了GPT原理的基础上，结合自己的思维逻辑，去引导ChatGPT才能一定程度解决问题（最终生成的结果往往也很难尽如人意）。而人的思维，才是解决复杂任务时的根本创造力，GPT模型难以做到，GPT代替人这件事还有很长很长的路要走。

GPT还有另一个问题——成本。虽然GPT能做检索，但真的用在简单检索上无法控制，同时单位检索成本相对于现在的检索模型也高出太多，因此目前不会完全替代掉目前搜索引擎。至于New Bing则是过于激进，由于Bing在传统搜索引擎中属于检索技术相对落后的，因此New Bing的确可以带来效果上的助益。出于成本问题，类GPT的LLM在国内更好的商业化落地可能还需要1-2年的工程实践。

那么，AIGC或ChatGPT模型会引发软件开发行业的生产力革命吗？我的观点是：以后会是，但现在还不是。至于多久以后，则存在巨大的不确定性。

#### 我们会丢掉工作吗？

当你读到这里，我相信你心中也有了自己的答案。我的观点是——ChatGPT技术或其后续演进是不会代替软件工程师的工作的，因为它不能解决复杂上下文的问题，现在不会，将来也很难。不过，ChatGPT可以成为软件工程师的效率工具。

工程难题、精确表达都是目前自然语言处理难以逾越的鸿沟。 **而人的创造力，在AIGC面前显示出了更加耀眼的不可替代性。** 但是，人工智能技术可不仅限于AIGC和ChatGPT。所以AI能够代替我们的工作吗？

我想说，道阻且长，行则将至。行而不辍，未来可期。

不过，可以预见的是，对软件工程师来说，未来的要求会更高。但AIGC与人之间不是替代的关系，而是更紧密的协作关系。从上面我给出的一个案例，其实也能窥之一二。作为软件工程师的我们，更应该为此扎实自己的基本功。具备甄别和改造AIGC生成内容的正确性的能力，才是提高工作效率的基本前提。

但是更重要的底层逻辑是：新技术带来的完全不同的思维模式和完全不同的发展逻辑。抓住这一点才不会被时代淘汰。

AI技术很有可能成为下一次工业革命的催化剂。每次工业革命，真正享受红利、参与其中的总是工程师，而这一次结合prompt只会让工程师更加如虎添翼（虽然不懂技术的人也能参与这次变革）。所以，又怎么会丢掉工作呢？

## 我可能都是错的

我们可能处在巨大的技术革命前夜，前方具备高度的不确定性。我在这里分享的发现和思考，不一定正确，还有可能都是错的。不过，这并不妨碍我们以此为基石展开讨论、引发你我的思考。

只有时间能够逐步验证这些想法。而想法和思考，又会随着技术的演进和时间的推移，逐渐完善和成熟。

让我们保持持续学习的习惯，我相信未来可期。希望这次加餐也能引发你的头脑风暴，期待你在留言区和我交流你的想法。