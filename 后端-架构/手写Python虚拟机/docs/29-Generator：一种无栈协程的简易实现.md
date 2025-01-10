你好，我是海纳。

上一节课我们主要是实现了异常功能，并且实现了 StopIteration 异常，依赖它重构了 FOR\_ITER 循环。这一节课，我们就依赖于 StopIteration 异常来实现 Python 虚拟机中的另外一个重要功能——Generator。

## 自定义迭代器类

Python 中可以通过自定义迭代器类来实现迭代功能。其中包含了两个步骤，一个是新建一个迭代器对象，另一个是在这个迭代器对象执行迭代。

我们知道，使用 for 语句的时候，会涉及到两个字节码，分别是 GET\_ITER 和 FOR\_ITER。GET\_ITER 的作用是对一个可遍历对象，取得它的迭代器，FOR\_ITER 的作用是针对迭代器进行迭代。

Python 也提供了机制让我们可以手动实现这个功能，与 GET\_ITER 字节码等价的是 iter 函数，与 FOR\_ITER 等价的则是 next 方法。我们通过例子来说明这个问题。

```python
lst = [1, 2]
itor = iter(lst)

while True:
    try:
        print(next(itor))
    except StopIteration as e:
        break

for i in lst:
    print(i)

```

使用第 10 行和 11 行的 for 的写法的迭代过程，与第 4 行至第 8 行的 while 的写法是完全等价的。只是 for 循环隐藏掉了迭代器，而 while 循环则显式地持有一个迭代器。

在 for 循环中，每一次迭代，虚拟机都会调用迭代器对象的 next 方法，得到本次迭代的结果，如果迭代结束了，也就是说在最后一次迭代中，next 方法应该产生一个 StopIteration 异常。for 语句会自动处理这个异常（参考我们对 FOR\_ITER 字节码的实现），并结束迭代。

而 while 语句则需要通过 try except 语句手动处理，在我们的例子里，在处理异常的 except 子句中，使用 break 跳出迭代过程。

通过这个例子，我们就搞明白 iter 和 next 的作用了。接下来，我们就来实现 iter 函数。

iter 函数和 len 函数非常相似，都是一个语言内建的函数，也可以在自定义类中被重载。只要在自定义类中实现了 `__iter__` 方法，这个类的实例就可以作为 iter 函数的参数来获取它的迭代器。

我们已经有了列表和字典，以及 len 方法的经验了，实现 iter 函数并不是什么困难的事情了。你可以看一下对应的代码。

```python
// [runtime/interpreter.cpp]
Interpreter::Interpreter() {
    ...
    // prepare for import builtin, this should be created first
    name = HiString::new_instance("iter");
    _builtins->put(name,         new FunctionObject(iter, name));
    name = HiString::new_instance("next");
    _builtins->put(name,         new FunctionObject(next, name));
}

// [runtime/functionObject.cpp]
HiObject* iter(HiList* args, HiDict* kwargs) {
    HiObject* arg0 = args->get(0);
    return arg0->iter();
}

HiObject* next(HiList* args, HiDict* kwargs) {
    HiObject* arg0 = args->get(0);
    return arg0->next();
}
// [object/hiObject.cpp]
HiObject* HiObject::iter() {
    return klass()->iter(this);
}

// [object/klass.cpp]
HiObject* Klass::iter(HiObject* x) {
    return find_and_call(x, NULL, ST(iter));
}

HiObject* Klass::next(HiObject* x) {
    return find_and_call(x, NULL, ST(next));
}

```

在所有的机制都已经搭建好了的情况下，添加一个内建函数是非常简单的。第 2 到 9 行，我们把字符串 iter 与内建函数 iter 关联起来，字符串 next 与内建函数 next 关联起来。

在第 12 至 15 行，是 iter 方法的具体实现，其主要逻辑是调用 HiObject 的 iter 方法。而 HiObject 的 iter 方法则是在我们实现 FOR\_ITER 字节码时就已经实现了的。

真正需要注意的是第 27 至第 29 行，由于 Klass 是所有内建类型 Klass 的父类，所以在 Klass 中定义的虚方法 iter 可以被子类覆写，比如ListKlass 和 DictKlass 都重写了 iter 方法。Klass 的实现主要是为了给自定义类型提供默认的实现，也就是查找并调用 `__iter__` 方法。

在代码的最后，我们展示了 next 方法的定义。在 FOR\_ITER 字节码的实现中，我们调用了 next 方法，你可以翻看以前的代码实现。

在增加了 iter 方法以后，我们使用迭代器来实现 Fibnacci 数列的计算。你可以看一下我给出的代码。

```c++
class Fib(object):
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return FibIterator(self.n)

class FibIterator(object):
    def __init__(self, n):
        self.n = n
        self.a = 1
        self.b = 1
        self.cnt = 0

    def __next__(self):
        if (self.cnt > self.n):
            raise StopIteration

        self.cnt += 1
        t = self.a
        self.a = self.a + self.b
        self.b = t
        return t

fib = Fib(10)
itor = iter(fib)

while True:
    try:
        print(next(itor))
    except StopIteration as e:
        break

for i in fib:
    print(i)

```

可以看到，我们通过在自定义类中提供 `__iter__` 方法来创建迭代器，在迭代器类中，通过实现 next 方法来进行每次迭代，当迭代结束以后，则通过 raise StopIteration 来结束迭代。运行这个例子，就可以以两种不同的方式打印出 Fibonacci 数列的前 10 项。

## 实现 Generator

最后，我们来研究一下 Python 中的另外一个迭代机制：Generator。本质上，Generator 是一个迭代器，它可以保存函数执行的中间状态，等下一次再被调用的时候，可以恢复中间状态继续执行。

我们把 Generator 的各个技术点拆解开来进行研究，先从 yield 关键字开始，我们看一个具体的例子。

```python
def foo():
    i = 0
    while i < 10:
        yield i
        i += 1

    return

for i in foo():
    print(i)

```

foo 方法看上去和一个普通的函数并没有什么不同，除了第 4 行的那条 yield 语句。这条语句使 foo 函数变成了另外一个东西，当调用 foo 的时候，它返回值并不是第 7 行的那条 return，而是一个 Generator。

按照以前的惯例，我们先来研究这段 Python 代码所对应的字节码。先看 main module 所翻译成的字节码，还是使用 show\_file 工具查看。

```python
   flags 0040
   code
  1           0 LOAD_CONST               0 (<code object foo>)
              2 LOAD_CONST               1 ('foo')
              4 MAKE_FUNCTION            0
              6 STORE_NAME               0 (foo)

  9           8 LOAD_NAME                0 (foo)
             10 CALL_FUNCTION            0
             12 GET_ITER
        >>   14 FOR_ITER                12 (to 28)
             16 STORE_NAME               1 (i)

 10          18 LOAD_NAME                2 (print)
             20 LOAD_NAME                1 (i)
             22 CALL_FUNCTION            1
             24 POP_TOP
             26 JUMP_ABSOLUTE           14
        >>   28 LOAD_CONST               2 (None)
             30 RETURN_VALUE

```

第 11 行的那个 CALL\_FUNCTION 指令，就是在调用 foo 函数了，调用的结果其实就是一个 Generator，它支持 GET\_ITER 操作，我们知道 GET\_ITER 的作用是获得一个可迭代对象的迭代器。也就是说，这条字节码的本意是为了获得 Generator 的迭代器，在虚拟机的真正实现中，我们把 Generator 和它的迭代器合并在一起了。

对 Generator 执行 GET\_ITER 操作，结果是 Generator 本身。接着，再执行 FOR\_ITER 就可以在 Generator 上进行迭代操作了。所以这段字节码向我们揭示了两个事实。

1. foo 函数的调用结果是一个 Generator。
2. Generator 支持迭代操作。

虚拟机是如何知道 foo 函数不是一个普通的函数，而是一个可以产生 Generator 的特殊函数的呢？我们继续探究 foo 函数的 CodeObject。我们看一下下面这段字节码。

```plain
         flags 0063
  2           0 LOAD_CONST               1 (0)
              2 STORE_FAST               0 (i)

  3     >>    4 LOAD_FAST                0 (i)
              6 LOAD_CONST               2 (10)
              8 COMPARE_OP               0 (<)
             10 POP_JUMP_IF_FALSE       28

  4          12 LOAD_FAST                0 (i)
             14 YIELD_VALUE
             16 POP_TOP

  5          18 LOAD_FAST                0 (i)
             20 LOAD_CONST               3 (1)
             22 INPLACE_ADD
             24 STORE_FAST               0 (i)
             26 JUMP_ABSOLUTE            4

  7     >>   28 LOAD_CONST               0 (None)
             30 RETURN_VALUE

```

这段字节码的最大玄机是它的 flags 的值，如果一个 CodeObject，它的 flags 与 0x20 做与操作，它值不为 0 的话，那么这个 CodeObject 一旦被调用，结果就会是一个 Generator。

你可以把 foo 的 flags 和 main module 的 flags 进行对比，就可以看到在 0x20 这一位上的不同了。至于 flags 的其他作用，在讲解函数和方法的时候我们已经介绍过一些了，除此之外，还有一些是没有讲到的，是由于 Python 虚拟机的历史原因而引入的，我们就不再关注了。

所以我们在实现函数调用的时候，要去查看它的 flags，如果发现 0x20 这一位是 1，那么就可以知道它的返回值是一个 Generator。如果发现它不是 1，就知道它是一个普通的函数而已。

另一个特殊的地方是第 11行的那个 YIELD\_VALUE 字节码，它是由 yield 语句翻译过来的。yield 语句的作用是，当在 generator 对象上进行迭代的时候，遇到 yield 语句就把它后面的值当做这一次迭代的结果，并且结束本次迭代。

在下一次迭代开始的时候，直接从 yield 下面的那条字节码开始。就像例子里展示的那样，第一次迭代的时候，i 的值是 0，所以 yield i 的结果就是 0，第二次迭代的时候，直接从第 5 行开始继续这次迭代，当再次遇到 yield 指令时，i 的值是 1。

在搞清楚了 generator 对象的接口定义和 yield 指令的意义以后，我们先来实现基本的数据结构，Generator 对象。

## Generator 对象

我们通过更多的例子来研究 Generator 对象的功能。代码我放在下面了，供你参考。

```plain
def func():
    i = 0
    while i < 2:
        yield i
        i += 1

    return

g = func()
print(next(g))
print(next(g))
print(next(g))

```

上述代码的执行结果如下所示：

```plain
0
1
Traceback (most recent call last):
  File "test_yi.py", line 12, in <module>
    print(next(g))
StopIteration

```

通过例子，我们可以看到，变量 g 代表的就是一个 generator 对象。在这个对象上可以调用 next 方法，当迭代结束的时候，它也会以 StopIteration 异常结束迭代。

回忆上一章我们所实现的迭代器类，generator 对象和一个正确定义了 next 方法的 Python 类的功能是完全相同的。

需要一点技巧的地方是，如何保存 yield 方法里定义的局部变量呢？比如 foo 方法里的 i，当我们结束了一次迭代以后，必须把这个值保存下来，下一次迭代的时候还要使用。

回忆一下，所有局部变量的值实际上都记录在 FrameObject 中的局部变量表里，所以我们可以在迭代结束的时候不销毁 FrameObject，供下一次迭代使用。分析到这里，我们就可以实现 Generator 类了。我们来看一下具体的实现代码。

```plain
class GeneratorKlass : public Klass {
private:
    static GeneratorKlass* instance;
    GeneratorKlass();

public:
    static GeneratorKlass* get_instance();

    virtual HiObject* next(HiObject* obj);
    virtual HiObject* iter(HiObject* obj);

    virtual size_t size();
    virtual void oops_do(OopClosure* f, HiObject* obj);
};

class Generator : public HiObject {
friend class Interpreter;
friend class FrameObject;
friend class GeneratorKlass;

private:
    FrameObject* _frame;

public:
    Generator(FunctionObject* func, ArrayList<HiObject*>* args, int arg_cnt);

    FrameObject* frame()           { return _frame; }
    void set_frame(FrameObject* x) { _frame = x; }
};

```

Generator 依然是一个普通的 Python 内建类型，所以它还是经典的 Klass-Oop 结构。GeneratorKlass 采用单例实现，里面要实现的最重要的两个虚函数是 iter 和 next，分别用来实现 GET\_ITER 字节码和 FOR\_ITER 字节码。

Generator 对象里，有一个成员变量是 FrameObject 的指针，就像我们之前分析的，它的作用是当迭代结束以后，还是可以保存局部变量的值。它们的具体实现我放在这里，供你参考。

```c++
HiObject* GeneratorKlass::iter(HiObject* obj) {
    return obj;
}

HiObject* GeneratorKlass::next(HiObject* obj) {
    assert(obj->klass() == (Klass*) this);
    Generator* g = (Generator*) obj;
    return Interpreter::get_instance()->eval_generator(g);
}

size_t GeneratorKlass::size() {
    return sizeof(Generator);
}

void GeneratorKlass::oops_do(OopClosure* f, HiObject* obj) {
    Generator* g = (Generator*)obj;
    assert(g->klass() == (Klass*)this);

    if (g->frame())
        g->frame()->oops_do(f);
}

Generator::Generator(FunctionObject* func, ArrayList<HiObject*>* args, int arg_cnt) {
    _frame = new FrameObject(func, args, arg_cnt);
    set_klass(GeneratorKlass::get_instance());
}

```

size 和 oops\_do 方法是支持 GC 的接口，我就不详细解释了。

GeneratorKlasss 的 iter 方法是把对象原封不动的返回出去，我们之前也说过，Generator 对象里把它和它的迭代器合并了。所以，实际上generator 对象的迭代器就是它自己。

next 方法是用于迭代的，迭代的逻辑比较复杂，所以我们把这个逻辑封装到 Interpreter 的 eval\_generator 方法中去处理了。

接下来，我们扩展一下 CALL\_FUNCTION 指令，让它支持 generator。

```c++
// [runtime/functionObject.cpp]
bool MethodObject::is_yield_function(HiObject *x) {
    Klass* k = x->klass();
    if (k != (Klass*) FunctionKlass::get_instance())
        return false;

    FunctionObject* fo = (FunctionObject*)x;
    return ((fo->flags() & FunctionObject::CO_GENERATOR) != 0);
}

// [runtime/interpreter.cpp]
void Interpreter::build_frame(HiObject* callable, ObjList args, int op_arg) {
    if (callable->klass() == NativeFunctionKlass::get_instance()) {
        PUSH(((FunctionObject*)callable)->call(args));
    }
    ...
    else if (MethodObject::is_yield_function(callable)) {
        Generator* gtor = new Generator((FunctionObject*) callable, args, op_arg);
        PUSH(gtor);
        return;
    }
    ...
}

```

这段代码的关键部分位于第 18 行和第 19 行。如果判断当前的 FunctionObject 是一个带有 yield 标记的 Function 的话，就创建一个 Generator 对象，并把这个对象放到栈顶。这样，我们就完成了 generator 对象的创建。

然后，再来实现 eval\_generator 方法。

```c++
HiObject* Interpreter::eval_generator(Generator* g) {
    Handle handle(g);
    enter_frame(g->frame());
    g->frame()->set_entry_frame(true);
    eval_frame();

    if (_int_status != IS_YIELD) {
        _int_status = IS_OK;
        leave_frame();
        ((Generator*)handle())->set_frame(NULL);
        return NULL;
    }

    _int_status = IS_OK;
    _frame = _frame->sender();

    return _ret_value;
}

```

这个方法和 run 方法、run\_mod 方法非常相似，不过就是设置好与 generator 相对应的 frame，然后调用 enter\_frame 和 eval\_frame，来执行里面 CodeObject 中的逻辑。

区别之处在于，对于 generator每次进来都不用新建一个 frame 对象，而是从 generator 里去获取。当 eval\_frame 执行结束以后，也不用销毁这个 frame，这样局部变量就保存在这个 frame 中了。下一次迭代的时候，也就是 next 方法被调用的时候，就可以继续使用同一个 frame。

第 4 行也是要注意的地方，把 generator 所对应的 frame 设为 entry frame，是为了遇到 return 语句的时候，可以直接返回到这里继续执行。

这个 frame 的特殊的地方是它有两种类型的出口，一种是执行 yield 语句，另一种是 return 或者遇到异常。这两种出口的区别是，yield 语句退出时，不会销毁 frame，另一种就像其他普通函数一样，需要销毁这个 frame。

最后一个步骤，就是在 eval\_frame 里实现 YIELD\_VALUE 字节码。你可以看一下具体的代码。

```c++
void Interpreter::eval_frame() {
    ...
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        switch (op_code) {
		...
            case ByteCode::YIELD_VALUE:
                // we are assured that we're in the progress
                // of evalating generator.
                _int_status = IS_YIELD;
                _ret_value = TOP();
                return;
        ...
        }
    }
}

```

一定要注意的是第 13 行，这里是 return，而不是 break。注释里也写得很清楚了，只有在 generator 里才会遇到 YIELD\_VALUE 字节码，这个时候只需要直接从 eval\_frame 中结束执行就可以了。

到这里，我们就可以正确地执行这节课开始的那个例子了。同时，在 builtin 中我们还可以添加 xrange 的实现。

```python
// [lib/builtin.py]
def range(*alist):
    start = 0
    step = 1
    if len(alist) == 1:
        end = alist[0]
    elif len(alist) == 2:
        start = alist[0]
        end = alist[1]
    elif len(alist) == 3:
        start = alist[0]
        end = alist[1]
        step = alist[2]

    if (start < end and step > 0):
        while start < end:
            yield start
            start += step
    elif (start > end and step < 0):
        while start > end:
            yield start
            start += step
    else:
        raise StopIteration

    return

```

到这里，我们的虚拟机对 Python 的语言特性的支持就基本完成了，在这个框架下面，我们可以尝试增加对文件、网络的支持，这些支持基本上不用修改虚拟机内部的实现，我们只需要在外部通过模块功能进行添加就可以了。

## 总结

这节课是专栏正文的最后一节课，主要完成两个功能：一是基于 StopIteration 异常完善了迭代的实现机制；二是实现了 Generator 机制。

一个函数中如果出现了 yield 语句，那么它的函数标志 CO\_GENERATOR(0x20) 就会被置位，当虚拟机在执行一个函数的时候，发现函数的这个标志位被置位了，那就应该创建一个 Generator，而不是直接执行。

Generator 对象的迭代器就是它自身，所以Generator既支持 iter 方法也支持 next 方法。每次调用 next 方法都会像处理普通函数那样创建栈帧，逐条字节码执行，直到遇到 YIELD\_VALUE 指令就从 eval 函数中退出，但是栈帧却并不销毁。这意味着，当前栈帧里的状态都被保留在这个帧里了。

当下一次再调用 next 方法的时候，就从上一次的那条 YIELD 语句之后继续执行。直到 next 方法产生 StopIteration 为止。到这里，我们课程的任务就基本完成了。

## 思考题

如果进一步实现元类、文件等功能，请你思考一下，现有的机制是否可以支持？欢迎你把思考后的结果分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！