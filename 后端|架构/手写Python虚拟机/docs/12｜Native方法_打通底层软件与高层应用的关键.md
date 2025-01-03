你好，我是海纳。

在过去的几节课中，我们实现了函数的基本功能。实际上，在 Python 中有很多内建函数，例如，range、print、len 等都是内建函数。这些内建函数往往是使用 C/C++ 在虚拟机内部实现的，所以我们把这些函数也称为 native 函数。

这节课我们就通过实现 len 方法来讲解如何在虚拟机里实现 native 函数。

## 实现内建函数（Builtin Function）

在 Python 开发者看来，内建函数和普通函数是一样。也就是说，开发者使用自定义的函数和使用 len、print 等内建函数时，并不需要感知它们之间有什么不同。

这就决定了，在虚拟机层面，我们希望内建函数与 FunctionObject 所代表的自定义函数也是统一的。所以我们选择继续使用 FunctionObject 来代表内建函数，不同点在于，普通的FunctionObject 是由 MAKE\_FUNCTION 字节码使用 CodeObject 主动创建的。前边两节课，我们重点介绍了这个机制。

但是内建函数并没有对应的字节码，它的所有实现都在虚拟机内部，也就是说，内建函数都是使用 C++ 来实现的。这里需要一种方法把 CALL\_FUNCTION 与虚拟机内部的实现联系起来。我们还是要在 FunctionObject 身上想办法。

我们可以在 FunctionObject 里增加一个方法，名为 call。当调用一个 FunctionObject 时，如果虚拟机检查到当前的 FunctionObject 是内建函数的话，就通过 call 方法去调用相关的逻辑。

要完成以上功能，第一个要解决的问题就是如何判断一个 FunctionObject 所代表的函数是不是内建函数。

这个问题的本质是 **判断对象的类型**，虚拟机使用对象的 **Klass** 来判断一个对象的类型。在这里，我们继续使用这种方法，引入一个 NativeFunctionKlass 来代表内建函数。

```c++
// runtime/functionObject.hpp
class NativeFunctionKlass : public Klass {
private:
    NativeFunctionKlass();
    static NativeFunctionKlass* instance;

public:
    static NativeFunctionKlass* get_instance();
};

// runtime/functionObject.cpp
NativeFunctionKlass* NativeFunctionKlass::instance = NULL;

NativeFunctionKlass* NativeFunctionKlass::get_instance() {
    if (instance == NULL)
        instance = new NativeFunctionKlass();

    return instance;
}

NativeFunctionKlass::NativeFunctionKlass() {
    set_super(FunctionKlass::get_instance());
}

```

如果要创建一个内建函数，只需要把它的 Klass 指向 NativeFunctionKlass 的实例即可。

第二个要解决的问题，是如何实现 call 方法。

print、len、range 等都是内建函数，它们 call 方法的逻辑各不相同。一种策略是像之前实现 print 方法一样，为每一种不同的对象实现不同的 print 方法。这样做的话，就是为 len 这个函数对象创建一个独立的 Klass，为 range 这个函数对象也创建一个独立的 Klass，在 Klass 内部实现不同的 call 的逻辑。这样做当然可以，但是太复杂了。

我们回到问题的本源，len 和 range 都是内建函数，不同的只是它们被调用时要执行什么功能。那我们其实可以使用函数指针来完成这个需求。

```c++
HiObject* len(ObjList args);
typedef HiObject* (*NativeFuncPointer)(ObjList args);

class FunctionObject : public HiObject {
private:
    ...
    NativeFuncPointer _native_func;

public:
    FunctionObject(NativeFuncPointer nfp);
    ...
    HiObject*  call(ObjList args);
};

```

在 FunctionObject 的定义里，引入一个函数指针，这个指针指向的函数可以接受 ObjList 作为参数，并且返回值类型是 HiObject\*（第 2 行和第 7 行）。

我们把所有的参数都放入到参数列表 args 中去了，而 args 是不定长的，所以理论上这种类型可以接受任意多的参数，用于实现内建函数是绰绰有余的。

接下来就是上面的声明所对应的具体实现：

```c++
FunctionObject::FunctionObject(NativeFuncPointer nfp) {
    _func_code = NULL;
    _func_name = NULL;
    _flags     = 0;
    _globals   = NULL;
    _native_func = nfp;

    set_klass(NativeFunctionKlass::get_instance());
}

HiObject* FunctionObject::call(ObjList args) {
    return (*_native_func)(args);
}

```

在实现了 NativeFunctionKlass 以后，就可以在 FunctionObject 中使用它了，将FunctionObject 的 Klass 设为 NativeFunctionKlass 的实例，这个 FunctionObject 就代表一个内建函数了（第 8 行）。同时，要把函数指针指向具体的函数实现（第 6 行）。在 call 方法里，通过函数指针调用到具体的方法。

接下来我们就以一个具体的例子来说明如何实现内建函数。

### 实现 len 方法

我们以 len 方法为例，在 len 的具体实现中，只需要调用对象的 len 方法即可。目前虚拟机里只有 String 类型，所以我们在 StringKlass 中添加 len 的实现。

```c++
// runtime/functionObject.cpp
HiObject* len(ObjList args) {
    return args->get(0)->len();
}

// object/hiObject.cpp
HiObject* HiObject::len() {
    return klass()->len(this);
}

// object/hiString.cpp
HiObject* StringKlass::len(HiObject* x) {
    return new HiInteger(((HiString*)x)->length());
}

```

列表、元组、字典等类型也支持 len 方法。我们这里先略过，等到后面实现列表类和字典类的时候，会把相应类型的 len 方法都正确地实现。

最后，还要把 len 函数加到 \_builtins 表中去。建立起 Python 中“len”符号与内建函数的联系。

```c++
#define PUSH(x)       _frame->stack()->add((x))

Interpreter::Interpreter() {
    _builtins = new Map<HiObject*, HiObject*>();
    ...
    _builtins->put(new HiString("len"),      new FunctionObject(len));
}

void Interpreter::build_frame(HiObject* callable, ObjList args) {
    if (callable->klass() == NativeFunctionKlass::get_instance()) {
        PUSH(((FunctionObject*)callable)->call(args));
    }
    else if (callable->klass() == FunctionKlass::get_instance()) {
        FrameObject* frame = new FrameObject((FunctionObject*) callable, args);
        frame->set_sender(_frame);
        _frame = frame;
    }
}

```

在 build\_frame 里，我们要对 native 函数和普通函数加以区分。前边已经分析过了，区分的关键就在于 Klass 的类型，如果是 FunctionKlass，就仍然走原来的路径，创建 FrameObject。如果是 NativeFunctionKlass，就调用 FunctionObject 的 call 方法，并且把 call 的返回值放到栈里。

我们通过一个测试用例来验证我们的实现。

```python
s = "hello"
print len(s)

def py_len(o):
    return len(o)

print py_len(s)

```

这里有一点需要注意的是，在某些情况下，py\_len 中对 len 函数的调用会被翻译成LOAD\_GLOBAL。而我们之前在实现 LOAD\_GLOBAL 的时候，只去检查了 FrameObject 里的全局变量表。实际上这是不够的，我们还应该在查找失败以后，继续查找内建变量表。这个逻辑与 LOAD\_NAME 是一样的，代码实现也相对简单，你可以自己实现，这里就不再列出源代码了。

### 实现print函数

实现了第一个内建函数以后，我们再来修改 print 函数就很简单了。从 [第 4 节课](https://time.geekbang.org/column/article/772694) 开始，我们就一直在使用各种方法对 print 方法进行规避，现在终于到了正面解决它的时候了。

第一步，在 builtin 里增加一项，将 `"print"` 字符串与 object\_print 方法关联起来。

```c++
Interpreter::Interpreter() {
    _builtins = new Map<HiObject*, HiObject*>();
    // ...
    _builtins->put(new HiString("print"),    new FunctionObject(object_print));
    _builtins->put(new HiString("len"),      new FunctionObject(len));
}

```

第二步，实现 object\_print 方法。

```c++
HiObject* object_print(ObjList args) {
    HiObject* arg0 = args->get(0);
    arg0->print();
    printf("\n");

    return Universe::HiNone;
}

```

最后，把 CALL\_FUNCTION 里的规避方法直接去掉就可以了，这个字节码的实现也变得非常简洁了。

```c++
void Interpreter::run(CodeObject* codes) {
    _frame = new FrameObject(codes);
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        switch (op_code) {
		...
            case ByteCode::CALL_FUNCTION:
                if (op_arg > 0) {
                    args = new ArrayList<HiObject*>(op_arg);
                    while (op_arg--) {
                        args->set(op_arg, POP());
                    }
                }

                fo = static_cast<FunctionObject*>(POP());
                build_frame(fo, args);

                if (args != NULL) {
                    delete args;
                    args = NULL;
                }
                break;
        ...
        }
    }
}

```

上述两个例子详细地展示了如何新增内建函数。从例子中可以看到，在打通了第一个例子以后，新增内建函数就变得非常简单了。

接下来，我们再看内建类型的方法是如何实现的。

## 实现方法（Method）

我们使用函数（function）和方法（method）这两个名词来区分一个函数是否与类绑定。在 C++ 这种面向对象编程语言中，如果一个函数不与类相关，在类的外部独立定义，就会被称为函数。

如果一个函数在类中定义，只有通过类的实例才能调用，这种函数就被称为方法。这里我们是严格区分函数和方法的。例如下面的两个例子。

```python
def foo():
    print("hello")

class A(object):
    def func(self):
        print(self)
        print("world")

a = A()
a.func()

```

foo 不和任何对象相联系，独立定义，它就是一个函数，而 func 则必须通过 A 的实例 a 进行调用，而且 a 还会继续作为实参传入到 func 中去，也就是说，第一个参数 self 实际上就是对象 a。

通过这两个例子我们展示了函数和方法的区别。由于我们的虚拟机现在还不能支持 class 语句定义类，所以你可以使用标准 Python 虚拟机来执行这个例子，便于观察这个例子的执行结果。

虽然目前的虚拟机还不能支持自定义类型，但也实现了多种内建类型，例如整数、字符串和列表等，所以我们仍然可以实现某些内建类型的方法。接下来我们就以 String 类型的 upper 方法来说明如何实现一个内建类型的方法。

我们从最简单的例子开始。Python 中的 String 类型，定义了一个方法 upper，它的作用是返回一个新的字符串，新字符串中的所有字母都变成大写的。通过下面的例子来观察 upper 方法的效果。

```python
s = "hello"
t = s.upper()

print(s)
print(t)

```

使用标准虚拟机执行这个例子，结果是 hello 和 HELLO，这说明对字符串 s 调用 upper 方法，并不会改变 s 的内容，而是会返回一个新的字符串。我们再来看这一段代码所对应的字节码是什么。

```python
  1           0 LOAD_CONST               0 ('hello')
              2 STORE_NAME               0 (s)

  2           4 LOAD_NAME                0 (s)
              6 LOAD_METHOD              1 (upper)
              8 CALL_METHOD              0
             10 STORE_NAME               2 (t)

  4          12 LOAD_NAME                3 (print)
             14 LOAD_NAME                0 (s)
             16 CALL_FUNCTION            1
             18 POP_TOP

  5          20 LOAD_NAME                3 (print)
             22 LOAD_NAME                2 (t)
             24 CALL_FUNCTION            1
             26 POP_TOP
             28 LOAD_CONST               1 (None)
             30 RETURN_VALUE
   consts
      'hello'
      None
   names ('s', 'upper', 't', 'print')

```

这段字节码里的大多数指令我们都已经见过了。新的指令只有两条：LOAD\_METHOD 和 CALL\_METHOD（第 5 行和第 6 行）。

LOAD\_METHOD 是一个带有参数的字节码，它的参数是一个整数，这是一个 names 表中的序号。在这个具体的例子里，参数为 1，也就是 names 表中的第 1 项，正是字符串 `"upper"`， 这就意味着 LOAD\_METHOD 的真实参数其实是方法名 upper。

在 LOAD\_METHOD 之前，已经通过 LOAD\_NAME 把字符串 s 加载到栈顶了。而 LOAD\_METHOD 是一个需要两个操作数的字节码，一个是调用方法的目标对象，另一个是方法的名称。

目标对象通过预先加载到操作数栈来提供，方法的名称则通过 names 表的序号，以字节码参数的形式提供。

另外一个字节码 CALL\_METHOD 的实现和 CALL\_FUNCTION 的实现是一样的，它可以直接复用 CALL\_FUNCTION 的代码，这里就不再赘述了。

由于 upper 是字符串类的一个方法，我们自然会想到在代表字符串类的 StringKlass 中增加这个方法。其实，不仅仅是 StringKlass 中会增加新的方法，其他所有类型的 Klass 都有定义新的方法，例如列表对象的 append 方法、字典对象的 update 方法等等。所以我们可以在 Klass 中引入一个 Map，专门用于记录某一种类型上的所有属性和方法。

```c++
class Klass {
private:
    ...
    HiDict*       _klass_dict;

public:
    ...
    void set_klass_dict(HiDict* dict)     { _klass_dict = dict; }
    HiDict* klass_dict()                  { return _klass_dict; }
    ...
};

```

我们可以在 StringKlass 的 klass\_dict 中，以字符串 `"upper"` 为 key，以 string\_upper 方法为 value。这样一来，我们就可以把方法与其名称联系起来了。

```c++
// runtime/hiString.cpp
HiObject* string_upper(ObjList args) {
    HiObject* arg0 = args->get(0);
    assert(arg0->klass() == StringKlass::get_instance());

    HiString* str_obj = (HiString*)arg0;

    int length = str_obj->length();
    if (length <= 0)
        return Universe::HiNone;

    char* v = new char[length];
    char c;
    for (int i = 0; i < length; i++) {
        c = str_obj->value()[i];
        // convert to upper
        if (c >= 'a' && c <= 'z')
            v[i] = c - 0x20;
        else
            v[i] = c;
    }

	HiString* s = new HiString(v, length);
	delete[] v;
    return s;
}

// runtime/universe.cpp
void Universe::genesis() {
    HiTrue       = new HiInteger(1);
    HiFalse      = new HiInteger(0);
    HiNone       = new HiObject();

    // initialize StringKlass
    HiDict* klass_dict = new HiDict();
    StringKlass::get_instance()->set_klass_dict(klass_dict);
    klass_dict->put(new HiString("upper"), new FunctionObject(string_upper));
}

```

string\_upper 函数实现了 upper 方法的逻辑（第 2 行至第 26 行）。upper 方法的逻辑比较简单，思路就是对字符串里的所有字符进行遍历，如果该字符是小写字母，就将其变成大写字母。做法就是直接将字符减去 32，即 16 进制的 20，因为大写字母的 ASCII 码值比相应的小写字母的值小 32。

genesis 函数又把它封装成了一个内建方法。以字符串 `"upper"` 为 key，将这个 function 放到了 klass\_dict 中（第 35 行至 37 行）。

这里要多解释一下 genesisi 方法。这个方法只在虚拟机初始化的时候调用一次。为什么要把 StringKlass 的初始化放到这个地方呢？能不能直接在 StringKlass 的构造函数里完成初始化呢？

答案是不能，因为我们在初始化 StringKlass 的 klass\_dict 时，会使用字符串 `"upper"` ，它是一个 HiString 对象。而 HiString 对象又依赖于 StringKlass。这种循环依赖会使程序陷入无限递归调用中。

为了解决这个问题，我们只能把 StringKlass 的初始化逻辑搬到外面来，而最合适做初始化的地方，自然就是这个只在虚拟机启动时执行一次的“创世纪”函数。

然后，我们来实现 LOAD\_METHOD 这条指令。

```c++
// [runtime/interpreter.cpp]
void Interpreter::run(CodeObject* codes) {
    _frame = new FrameObject(codes);
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        switch (op_code) {
		...
            case ByteCode::LOAD_ATTR:
            case ByteCode::LOAD_METHOD:
                v = POP();
                w = _frame->_names->get(op_arg);
                PUSH(v->getattr(w));
                break;
        ...
        }
    }
}

// object/hiObject.cpp
HiObject* HiObject::getattr(HiObject* x) {
    HiObject* result = Universe::HiNone;
    result = klass()->klass_dict()->get(x);
    return result;
}

```

查找属性和方法的逻辑都被封装到对象的 getattr 方法里了。好像一切都是正常的，但我们思考一下，upper 方法的参数是怎么传递的，问题就出现了。

upper 方法看上去是不用传任何参数的，但实际上，它却有一个隐含的参数：调用方法时的那个目标对象，在这节课的例子中，就是字符串“hello”。

虚拟机需要一种机制来传递这个隐式的参数。在之前的讲解中，我们已经明确了函数和方法的不同。函数没有隐含的参数，但是方法有，所以我们可以为方法定义一种新的类型，让它完成传递隐式参数的功能。这个新的类型就是 MethodObject。

```c++
// runtime/functionObject.hpp
// Method objects.
class MethodKlass : public Klass {
private:
    MethodKlass();
    static MethodKlass* instance;

public:
    static MethodKlass* get_instance();
};

class MethodObject : public HiObject {
friend class MethodKlass;

private:
    HiObject* _owner;
    FunctionObject* _func;

public:
    MethodObject(FunctionObject* func) : _owner(NULL), _func(func) {
        set_klass(MethodKlass::get_instance());
    }

    MethodObject(FunctionObject* func, HiObject* owner) : _owner(owner), _func(func) {
        set_klass(MethodKlass::get_instance());
    }

    void set_owner(HiObject * x)   { _owner = x; }
    HiObject* owner()              { return _owner; }
    FunctionObject* func()         { return _func; }
};

// runtime/functionObject.cpp
/*
 *  Operations for methods
 *  Method is a wrapper for function.
 */
MethodKlass* MethodKlass::instance = NULL;

MethodKlass* MethodKlass::get_instance() {
    if (instance == NULL)
        instance = new MethodKlass();

    return instance;
}

MethodKlass::MethodKlass() {
    set_klass_dict(new HiDict());
}

```

上述代码定义了 MethodObject 和 MethodKlass。定义一种新的 Object 以及它所对应的 Klass 对于我们来说已经算得上是轻车熟路了。

在这段代码里，我们看到 MethodObject 不过是 FunctionObject 的一层封装而已。MethodObject 与 FunctionObject 的唯一区别就是 MethodObject 多了一个 \_owner 属性。

定义完了 MethodObject 以后，我们终于可以把 getattr 的逻辑补全了。如果从 klass\_dict 中得到的是一个 FunctionObject，那么我们应该构建一个 MethodObject，把 FunctionObject 与目标对象绑定在一起。

```c++
HiObject* HiObject::getattr(HiObject* x) {
    HiObject* result = Universe::HiNone;

    result = klass()->klass_dict()->get(x);

    if (result == Universe::HiNone)
        return result;

    // Only klass attribute needs bind.
    if (MethodObject::is_function(result)) {
        result = new MethodObject((FunctionObject*)result, this);
    }
    return result;
}

```

LOAD\_METHOD 终于完成了，这条字节码执行成功以后，加载到栈顶的就是一个正确的 MethodObject 了。

最后一步，CALL\_FUNCTION 处还要增加对 MethodObject 的支持。所以我们要在 build\_frame 中对 MethodObject 加以处理。

```c++
void Interpreter::build_frame(HiObject* callable, ObjList args) {
    if (callable->klass() == NativeFunctionKlass::get_instance()) {
        PUSH(((FunctionObject*)callable)->call(args));
    }
    else if (callable->klass() == MethodKlass::get_instance()) {
        MethodObject* method = (MethodObject*) callable;
        if (!args) {
            args = new ArrayList<HiObject*>(1);
        }
        args->insert(0, method->owner());
        build_frame(method->func(), args);
    }
    else if (callable->klass() == FunctionKlass::get_instance()) {
        FrameObject* frame = new FrameObject((FunctionObject*) callable, args);
        frame->set_sender(_frame);
        _frame = frame;
    }
}

```

栈顶那个被调用的对象如果是 MethodObject 时，我们就将其 owner 放到参数列表的第一位（第 5 至 11 行）。我们正是通过这种方式将隐式参数与实参一起传给方法的。编译运行，就会发现这节课开始的那个 test\_upper 的例子可以正确执行了。

到此为止，虚拟机中已经有了基本的内建类型、整数和字符串，也有了基本的函数和方法的功能。函数和方法还有更多的机制，但这需要虚拟机中支持了更多的内建对象以后才能实现。在完善函数的全部特性之前，我们下一节课需要先实现列表和字典这两种重要的内建类型。

## 总结

我们这节课重点介绍了如何实现内建函数和内建方法。我们使用 NativeFunctionKlass 来标识内建函数。一个 FunctionObject 的类型是内建函数，那么它就会包含一个函数指针，指向 C++ 所实现的函数。

在虚拟机的初始化阶段，builtin 结构中把字符串与 FunctionObject 关联起来，这样就可以使 LOAD\_NAME 字节码正确地将 FunctionObject 加载到栈顶。

当函数被调用时，可以通过函数指针调用到相关的逻辑里。你可以看一下整体的流程图。

![图片](https://static001.geekbang.org/resource/image/6b/11/6bea886237c2427e3e155305fece5211.png?wh=1804x518)

在这节课的第二部分，我们讲解了如何实现一个内建方法。函数和方法的不同就在于是否绑定对象。所以内建方法需要使用 LOAD\_METHOD 字节码进行加载，在加载的过程中，虚拟机将方法与对象进行绑定。

## 思考题

你是否能向虚拟机中添加更多的内建函数呢？欢迎你把你的想法分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！