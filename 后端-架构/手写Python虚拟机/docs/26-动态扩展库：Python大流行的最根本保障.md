你好，我是海纳。

上一节课，我们初步构建了加载模块的能力。模块功能是现代语言的必备功能，只有通过模块组成的库，现代编程语言才有可能进行大规模的软件复用。

除了使用 Python 语言开发的库，还有一些功能是依赖于操作系统平台的，比如图形用户界面、文件、网络等功能。这些功能显然更适合以库的形式存在，而不是直接集成在虚拟机中。这一节课，我们就来研究虚拟机如何管理这种依赖于具体平台的动态库。

## 加载动态库

几乎所有的编程语言虚拟机都会支持使用 C++ 写扩展库，一是因为 C++ 的库非常多，很多十分重要的基础库，都是由 C++ 写成的，另一个原因是 C++ 及其编译器在性能方面的表现确实处于十分领先的位置，一些性能敏感的部分必须使用 C++ 来写本地扩展库。

注：关于动态链接的更多知识，请参阅 [《编程高手必学的内存知识》](https://time.geekbang.org/column/intro/100094901?utm_campaign=geektime_search&utm_content=geektime_search&utm_medium=geektime_search&utm_source=geektime_search&utm_term=geektime_search&tab=catalog)。

这种扩展库往往是以动态链接库的形式组织的，在 Linux 上，动态链接库默认以 so 作为后缀，在 Windows 上，则多用 dll 作为后缀。当然，这种后缀名只是一种习惯，并不是强制的，我们完全可以把动态库的后缀改成其他的，并不影响库的正常加载和运行。

举个例子，如果我们想为某个虚拟机编写一些额外的扩展功能，第一种办法就是找到这个虚拟机的源代码，直接将这些功能写在虚拟机里，然后重新编译，得到一个新的虚拟机可执行文件。这种方式就是静态链接，它有两个缺点，一是代码的开发和维护非常困难，在动手修改虚拟机之前，要求开发者必须非常熟悉虚拟机的代码。二是扩展功能的部署、分发都非常困难，要使用新的功能就必须重新安装虚拟机。

为了解决这些问题，我们就可以使用动态链接的方法，来实现这个扩展功能。我们可以把所有的功能实现为一个动态链接库，这是一个完全独立的二进制文件。只要满足了虚拟机的接口要求，虚拟机就可以在运行时加载这个文件，初始化符号并执行。

这样一来，功能开发的过程与虚拟机是独立的。部署也很轻松，只需要把这个独立的库文件复制到特定的位置，虚拟机就可以加载它。这节课我们就来介绍 **如何让虚拟机在运行时加载动态链接库。**

首先，我们要造一个动态链接库，比如造一个数学库 math，在里面可以进行一些数学计算。我们可以通过 ADD\_LIBRARY 指令在 lib 目录的 CMakeLists.txt 中添加 math 库的构建指令。

```plain
# libmath
ADD_LIBRARY(math SHARED math.cpp)
TARGET_LINK_LIBRARIES(math hivm)

```

这行选项的意思是把 extlib 目录下的 math.cpp 文件，编译成一个动态链接库。这样做的好处是不同平台上会有不同的编译命令和目标文件，而我们却不用再关心这些差异，跨平台的工作就交给 cmake 处理了。

## 定义虚拟机与动态库之间的接口

新建一个动态链接库很容易，但是我们必须要让虚拟机能够识别，这里借鉴了 CPython 中的做法。

当我们要为 CPython 制作动态链接库的扩展库时，要在源文件中提供一个 init 方法，比如说，库名字叫 math，那就要提供一个名为 init\_libmath 的函数，调用这个函数就可以得到一个函数数组，这个数组里描述了动态库包含了多少个可以被虚拟机调用的函数。通过这种方式，虚拟机就能正确地打开并识别加载动态库了。

我们可以定义与 CPython 相同的接口，先创建 os 目录，在其中新建 shared\_library.hpp。

```c++
#ifndef SHARED_LIBRARY_HPP
#define SHARED_LIBRARY_HPP

#include "runtime/functionObject.hpp"
#include "object/hiInteger.hpp"
#include "object/hiList.hpp"
#include "object/hiObject.hpp"

#define SO_PUBLIC __attribute__((visibility("default")))

struct RGMethod {
    const char* meth_name;
    NativeFuncPointer meth;
    int meth_info;
    const char* meth_doc;
};

typedef RGMethod* (*INIT_FUNC)();

#endif

```

上面的代码定义了 RGMethod 结构，并且定义了 init 方法的指针，我们将来就通过这个函数指针去调用各个库里的初始化方法。

还有一个宏 SO\_PUBLIC，它的作用是修饰动态库中的符号，gcc 遇到有这个宏所饰的符号时，就会导出这个符号。 `__attribute__` 是 gcc 中的扩展语法，只在 gcc 中支持。

然后，我们在 math.cpp 中定义一个可以执行两个整数类型的加法运算的函数。

```c++
#include "os/shared_library.hpp"

HiObject* add(HiList* args, HiDict* kwargs) {
    int a = args->get(0)->as<HiInteger>()->value();
    int b = args->get(1)->as<HiInteger>()->value();

    return new HiInteger(a + b);
}

RGMethod math_methods[] = {
    { "add", add, 0, "add tow integer", },
    { NULL, NULL, 0, NULL, },
};

#ifdef __cplusplus
extern "C" {
#endif

SO_PUBLIC RGMethod* init_libmath() {
    return math_methods;
}

#ifdef __cplusplus
}
#endif

```

重新编译整个项目，就可以看到 lib 目录下，多了一个 libmath.so 文件。如果是在 Windows 平台上，就是 libmath.dll。

接下来，我们就尝试在虚拟机中加载它。

## dlopen 打开动态库文件

在虚拟机启动以后，如果不执行 import 模块的动作，动态库就不必要加载。只有执行了 import 动作以后，动态库才会被加载进来。我们可以使用运行时加载的办法来实现这个功能。

在 Linux 上，有一组函数可以进行动态库的装载和关闭，其中 dlopen 用于打开动态库，dlsym 用于查找动态库中的符号，dlerror 用于处理错误，dlclose 用于关闭动态库。这几个函数可以通过 `<dlfcn.h>` 引入。

dlopen 函数的原型是：

```c++
void* dlopen(const char* filename, int flag);

```

其中，第一个参数代表被加载的动态库的文件名，这个路径可以是绝对路径，也可以是相对路径。

由于虚拟机的执行目录与 lib 目录在同级文件夹中，这里就可以使用 ./lib/libmath.so 这种路径加载这个动态库。

第二个参数 flag 代表函数符号的解析方式，它可以是 RTLD\_LAZY ，代表延迟绑定，也就是说符号只用在使用的时候才去解析，加载的时候是不解析的。也可以是 RTLD\_NOW，表示模块被加载时就完成所有的函数绑定工作。RTLD\_NOW 要做的事情明显多一些，所以会导致加载动态度的速度变慢。我们这里使用 RTLD\_NOW 就可以了，因为我们的符号很少，这一点性能损失几乎无法察觉。

dlopen 的返回值是被加载的模块的句柄，这个句柄在后面使用 dlsym 时会用到，如果加载失败，返回值就是 NULL，这时可以通过 dlerror 函数取得失败的具体原因。如果模块已经加载过了，那么重复调用 dlopen，会得到同一个句柄。

dlsym 函数的作用是找到我们所需要的符号。dlsym 函数的原型是：

```plain
void* dlsym(void* handle, char* symbol);

```

第一个参数 handle 是 dlopen 函数所得到的模块的句柄，第二个参数 symbol 是要查找的符号的名称。dlsym 的返回值的含义比较复杂，我们先不关心它的全部情况，在我们的实际场景中，需要得到用于模块初始化的 init\_libmath 函数。

当我们把函数名作为参数传给 dlsym 的时候，如果找到符号了，就返回指向函数的指针，如果返回值为 NULL，就说明加载失败。

由于在某些特殊情况下，NULL 也是一个可能的合理返回值，所以我们还需要使用 dlerror 进行确认。dlerror 的返回值类型是字符串，如果返回 NULL，表示上一次的调用成功，如果不为 NULL，则代表相应的错误信息。

掌握了这三个函数的用法以后，我们就使用它们来从动态库中加载符号。

## 加载动态库

首先，我们修改 search\_file 方法，当虚拟机执行 import math 语句的时候，先尝试加载 lib/libmath.pyc，如果这个文件不存在，就试图加载同一目录下的 libmath.so。

```c++
HiObject* ModuleObject::search_file(Handle<HiObject*> x) {
    Handle<HiList*> paths = Interpreter::get_instance()->search_path();
    for (int i = 0; i < paths->length(); i++) {
        Handle<HiString*> path = paths->get(i)->as<HiString>();
        path = path->add(x)->as<HiString>();

        Handle<HiString*> name = path->add(ST(pyc))->as<HiString>();
        name->print();
        printf("\n");
        if (access(name->value(), R_OK) == 0) {
            return import_pyc(x->as<HiString>(), name);
        }

        name = path->add(ST(so))->as<HiString>();
        name->print();
        printf("\n");
        if (access(name->value(), R_OK) == 0) {
            return import_so(x->as<HiString>(), name);
        }
    }

    return Universe::HiNone;
}

```

接下来，我们要使用 dlopen、dlsym 等函数来实现 import\_so 方法。在这个方法里，会执行动态库的加载、初始化，最关键的是把动态库中定义的函数以一个 ModuleObject 的形式传递给虚拟机，这样虚拟机才可以正常使用。

```c++
ModuleObject* ModuleObject::import_so(HiString* mod_name, HiString* filename) {
    char* error_msg = nullptr;

    void* handle = dlopen(filename->value(), RTLD_NOW);
    if (handle == nullptr) {
        printf("error to open file: %s\n", dlerror());
        return nullptr;
    }

    char* init_meth = new char[5 + mod_name->length() + 1];
    memcpy(init_meth, "init_", 5);
    memcpy(init_meth + 5, mod_name->value(), mod_name->length());
    init_meth[5 + mod_name->length()] = '\0';

    INIT_FUNC init_func = (INIT_FUNC)dlsym(handle, init_meth);
    delete[] init_meth;

    if ((error_msg = dlerror()) != NULL) {
        printf("Symbol init_methods not found: %s\n", error_msg);
        dlclose(handle);
        return NULL;
    }

    RGMethod* ml = init_func();
    Handle<ModuleObject*> mod = new ModuleObject(nullptr);
    mod->set_obj_dict(HiDict::new_instance());

    for (; ml->meth_name != NULL; ml++) {
        Handle<HiString*> name = HiString::new_instance(ml->meth_name);
        Handle<FunctionObject*> func = new FunctionObject(ml->meth, name);
        mod->put(name, func());
    }

    return mod;
}

```

加载动态库的第一步是打开动态库（第 4 至第 9 行）。第二步是加载初始化函数（第 10 至 22 行），这里约定每个库的初始化函数名称都是字符串 init 加上库名称，例如加载 math 库时，使用的就是 init\_libmath 函数。第三步是通过函数指针调用初始化函数，得到 RGMethod 数组（第 24 行）。最后一步，遍历 RGMethod 数组，把其中的符号和函数指针放入新建的 ModuleObject 中（第 25 至 34 行）。

我们之前提到过的符号导出的问题。一个符号是否被导出，代表了这个符号的可见性，也就是在其他地方使用 dlsym 能否成功加载。这里只需要访问 init\_libmath 函数，所以在 math.cpp 中，只把这个函数通过 SO\_PUBLIC 宏导出。

还有一个地方需要注意，那就是下面这个预编译宏：

```c++
#ifdef __cplusplus
extern "C" {
#endif
...
#ifdef __cplusplus
}
#endif

```

当编译器是 C++ 编译器时，\_\_cplusplus 宏就是被定义的，这时 extern “C” 就会起作用。从而通知编译器不要启用 C++ 的 name mangling 机制。

C++ 为了解决命名重复的问题，会把目标文件中的符号名都做一次修饰，例如，我们如果去掉了这个宏，再编译一次 libmath.so，然后使用 readelf 工具查看一下动态库中的符号。

```plain
# readelf -sD libmath.so
Symbol table of `.gnu.hash' for image:
  Num   Type   Bind Vis      Ndx Name
   ...
   24 FUNC    GLOBAL DEFAULT  11 _Z12init_libmathv
   ...
   26 FUNC    WEAK   DEFAULT  11 _ZN8HiDouble5valueEv
   27 FUNC    GLOBAL DEFAULT   9 _init
   28 FUNC    GLOBAL DEFAULT  12 _fini

```

可以看到，init\_libmath 函数的符号变成了 \_Z12init\_libmathv，这样的话，如果使用 dlsym 尝试加载 init\_libmath，就会失败。而如果增加了这个宏，再使用 readelf 查看符号，就会发现符号名变成了下面这个样子：

```plain
# readelf -sD libmath.so
Symbol table of `.gnu.hash' for image:
  Num   Type   Bind Vis      Ndx Name
   ...
   24 FUNC    GLOBAL DEFAULT  11 init_libmath

```

通过对比，我们就能理解 extern 的意义了。到这里为止，就可以重新编译虚拟机，并执行以下测试用例：

```plain
import libmath
print(libmath.add(1, 2))

```

接下来我们的工作是把 math 模块完善起来，让它与 Python 的 math 模块有相同的能力。

## 实现 math module

math 中的 sin 正弦函数、cos 余弦函数等，它们的参数和返回值都是浮点数，为了支持这些浮点计算，我们首先要在虚拟机中引入浮点类型。

### 浮点类型

在第四章我们费了很大的力气才实现了整数类型和字符串类型，但经过了列表、字典以及自定义类型的锻练以后，在虚拟机中增加一种新的内建类型对于我们可以说是驾轻就熟了。

先回顾一下创建一个新的类型的步骤。

1. 定义类和它所对应的 Klass。
2. 实现 Klass 上定义的运算和操作。
3. 在 Klass 中增加 GC 接口。
4. Klass 的初始化：维护类型的继承关系，维护方法解析顺序。

在这个方案的指导下，我们来定义 Klass 和 HiDouble。

```plain
class DoubleKlass : public Klass {
private:
    DoubleKlass();
    static DoubleKlass* instance;

public:
    static DoubleKlass* get_instance();
    void initialize();

    virtual void print(HiObject* obj);

	//...
    virtual HiObject* add(HiObject* x, HiObject* y);
	//...

    virtual HiObject* allocate_instance(HiObject* callable,
            ArrayList<HiObject*>* args);

    virtual size_t size();
    virtual void oops_do(OopClosure* f, HiObject* obj);
};

class HiDouble : public HiObject {
private:
    double _value;

public:
    HiDouble(double x);
    double value() { return _value; }
};

// [object/hiDouble.cpp]
...
void DoubleKlass::print(HiObject* obj) {
    HiDouble* dbl_obj = (HiDouble*) obj;
    assert(dbl_obj && ((char *)dbl_obj->klass()) == ((char *)this));
    printf("%.12g", dbl_obj->value());
}
...

```

这里就不再展示它的全部代码和实现了，你可以自己动手实现，也可以查看对应工程的 [源代码](https://gitee.com/hinus/pythonvm/tree/geektime/lib)。

### 完善 math 库

math 库里有很一些常量定义，例如 pi 和 e。在 so 文件中，只定义了方法，而不会定义这些常量，我们可以把这些常量放在 math.py 中定义。

```python
from libmath import sin
from libmath import sqrt

pi = 3.141592653589793
e = 2.718281828459045

```

这个文件从 libmath 中引入了 sin 和 sqrt 两个方法（第 1 行和第 2 行），分别用于计算正弦值和求平方根。然后定义了圆周率 pi 和自然底数 e 两个浮点常量。

接下来，我们就在 math.cpp 中增加 sin 和 sqrt 的定义。

```c++
#include <math.h>

double get_double(HiList* args) {
    return args->get(0)->as<HiDouble>()->value();
}

HiObject* math_sqrt(HiList* args, HiDict* kwargs) {
    double x = get_double(args);
    return new HiDouble(sqrt(x));
}

HiObject* math_sin(HiList* args, HiDict* kwargs) {
    double x = get_double(args);
    return new HiDouble(sin(x));
}

RGMethod math_methods[] = {
    { "sin",  math_sin,  0, "sin(x)", },
    { "sqrt", math_sqrt, 0, "square root of x", },
    { NULL, NULL, 0, NULL, },
};

```

可以看到，本质上，sin 函数就是对 C 语言的 sin 函数的一次封装，将它包装成虚拟机可以调用的方法。这段代码逻辑很清晰，我就不再过多解释了。

然后，我们就可以编译执行以下测试用例：

```python
import math

print(math.pi)
print(math.e)
print(math.sin(math.pi / 3.0))
print(math.sqrt(200.0))

```

你可以使用 Python 和我们的虚拟机分别执行这个例子，执行完你就会发现，pvm 和 CPython 保持了很好的兼容。

注意，dlopen 和 dlsym 是 POSIX 接口，只在支持 POSIX 接口的操作系统上可以正确执行。比如 macOS 和 Linux。如果你在 Windows 系统上使用 Visual C++ 和 nmake 进行构建的话，就需要使用具有相同功能的 Windows API 来代替 dlopen/dlsym，比如 LoadLibrary。在 Windows 上，我的解决方案是使用 MinGW 进行编译，具体的 CMake 配置你可以参考 [代码仓](https://gitee.com/hinus/pythonvm/tree/geektime/)。

## 总结

这节课我们通过 dlopen 和 dlsym 函数从动态链接库里加载符号，并使用函数指针将动态链接库里的函数封装成 Python 虚拟机可用的函数。为了让虚拟机知道动态库中有多少可用的函数，我们定义了 RGMethod 结构体。在动态库中声明 RGMethod 数组，并且使用 init 函数将这个数组返回出来。

当虚拟机通过函数指针调用 init 函数时就能得到动态库里所有导出函数的信息。然后再通过调用虚拟机的内部函数把符号放入 ModuleObject 中。这样就完成了从动态库中加载符号的全部过程。

我们用了两节课完成了加载库的能力。这对 Python 的模块和库的组织非常重要。当前 Python 语言在 AI 场景被广泛使用，实际上，很多张量计算的加速库都是使用 C++实现的。所以毫不夸张地说，正是 Python 语言能很方便地与 C++ 函数进行互操作这个功能，使 Python 语言同时具备了脚本语言的高开发效率和静态编译语言的高性能。

靠着加载模块的能力，我们就能合理地支持功能更强大的库了。下节课我们就以异常库来说明如何构建语言的运行时库。

## 思考题

跨语言调用一直是运行在虚拟机上的语言的核心痛点之一（例如Java、Go等）。除了这节课所讲的方案之外，你还知道哪些解决方案？欢迎你把你的方案分享出来，我们一起讨论，如果你觉得这节课对你有帮助的话，也欢迎你分享给需要的朋友，我们下节课再见！