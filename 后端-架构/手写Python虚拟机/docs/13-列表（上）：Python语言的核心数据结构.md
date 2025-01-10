你好，我是海纳。

在 [第 7 节课](https://time.geekbang.org/column/article/774409)，我们实现了 Python 的两个基本的内建类型：整数和字符串，从而构建了虚拟机的最基本的对象系统。从这节课开始，我们来实现两个重要的基本内建类型，分别是列表（list）和字典（dict）。

我们先来研究如何实现列表。

## 列表的定义

Python 中的列表很像数组操作，可以支持对元素的插入、添加、删除等操作。实际上 Python 的 list 和 C++ STL 中的 vector 非常相似。区别在于，Python 的 list 允许它的元素是不同类型的。我们以一个例子来说明 list 的特性。

```python
# test_list.py
lst = [1, "hello"]

# result is [1, 'hello']
print(lst)

```

上面的代码定义了一个列表，这个列表包含了两个元素。第一个元素是整数 1，第二个元素是字符串 `“hello”`。第二行代码把这个列表打印了出来。

通过 show\_file 工具，我们能观察到 Python 为了定义列表引入了新的字节码。这节课我们的任务就是实现这些定义列表所用的字节码。

```plain
  1           0 LOAD_CONST               0 (1)
              2 LOAD_CONST               1 ('hello')
              4 BUILD_LIST               2
              6 STORE_NAME               0 (lst)

  4           8 LOAD_NAME                1 (print)
             10 LOAD_NAME                0 (lst)
             12 CALL_FUNCTION            1
             14 POP_TOP
             16 LOAD_CONST               2 (None)
             18 RETURN_VALUE

```

定义列表并打印，所使用的字节码就是我们上面列出来的，其中绝大部分的字节码都已经实现好了，唯一一个新的字节码是 BUILD\_LIST。

在 BUILD\_LIST 之前有两个 LOAD\_CONST 指令，分别把整数 1、字符串 `“hello”` 送到栈顶。 BUILD\_LIST 指令是带有参数的，它的参数就代表了操作数栈上有多少个元素是列表中的内容。在这个例子里，参数是 2，这就表示我们应该从栈上取出两个对象，以这两个对象为参数去创建一个新的列表，并把这个列表再放到操作数栈顶。

在 [第 5 节课](https://time.geekbang.org/column/article/772703)，我们已经实现了一个基本的列表雏形，那就是 HiList 类，但在 [第 7 节课](https://time.geekbang.org/column/article/774409) 对类型进行重构的时候，只做了 HiInteger 和 HiString 的重构工作，HiList 类被忽略了。HiList 类包含了很多内建方法，所以我们选择在实现了函数和方法以后再来重构 HiList。

重构的第一步是引入 ListKlass，为列表类增加类型标志。

```c++
class ListKlass : public Klass {
private:
    ListKlass();
    static ListKlass* instance;

public:
    static ListKlass* get_instance();

    virtual void print(HiObject* obj);
};

class HiList : public HiObject {
friend class ListKlass;

private:
    ArrayList<HiObject*>* _inner_list;

public:
    HiList();
    HiList(ObjList ol);
    ArrayList<HiObject*>* inner_list()  { return _inner_list; }

    int size()                          { return _inner_list->size(); }
    void append(HiObject* obj)          { _inner_list->add(obj); }
    HiObject* pop()                     { return _inner_list->pop(); }
    HiObject* get(int index)            { return _inner_list->get(index); }
    void      set(int i, HiObject* o)   { _inner_list->set(i, o); }
    HiObject* top()                     { return get(size() - 1); }
};

```

在上面的代码里，我们定义了一个新的类型 HiList，它是 HiObject 的子类。在 HiList 中，有一个域 \_inner\_list，它的类型是 ArrayList。我们在 HiList 中定义了各种操作，最终都转化成了对 ArrayList 的操作。这些操作包括：

1. append：向列表的尾部添加一个元素。
2. pop：把列表的最后一个元素删除，并返回这个元素。
3. get：给定下标，取出列表中相应的值。
4. set：给定下标，把列表中相应的值设为输入参数的值。
5. top：取列表的最后一个元素，但不删除。

如何把这些方法与 Python 字节码相联系是下节课的主要任务。我们这节课还是把注意力集中到 ListKlass 的实现上。在我们的设计理念中，所有与类型相关的操作都会在 Klass 中实现。为了支持打印列表，我们要在 ListKlass 中实现 HiList 的 print 方法。

```c++
HiList::HiList() {
    set_klass(ListKlass::get_instance());
    _inner_list = new ArrayList<HiObject*>();
}

HiList::HiList(ObjList ol) {
    set_klass(ListKlass::get_instance());
    _inner_list = ol;
}

ListKlass* ListKlass::instance = NULL;

ListKlass* ListKlass::get_instance() {
    if (instance == NULL)
        instance = new ListKlass();

    return instance;
}

ListKlass::ListKlass() {
}

void ListKlass::print(HiObject* x) {
    HiList * lx = (HiList*)x;
    assert(lx && lx->klass() == (Klass*) this);

    printf("[");

    int size = lx->_inner_list->size();
    if (size >= 1)
        lx->_inner_list->get(0)->print();

    for (int i = 1; i < size; i++) {
        printf(", ");
        lx->_inner_list->get(i)->print();
    }
    printf("]");
}

```

上述代码先定义了 HiList 的构造方法（第 1 至 9 行）。在构造方法里，把 klass 设置为 ListKlass。这个操作和 HiInteger、HiString 等如出一辙，我就不再详细解释了。

第二部分实现了 ListKlass 单例类（第 11 行至第 21 行）。关于单例模式，我们也反复使用多次了，这里也不再过多解释了。

最后一部分定义了 ListKlass 的 print 方法（第 23 至 38 行）。print 方法是定义在 HiObject 中的虚方法。ListKlass 中的 print 方法仅仅是为了实现对 HiList 对象的打印。它的逻辑比较简单，打印左中括号以后，就把 list 中的所有元素逐个取出并且调用它的 print 方法。

在构建好了 HiList 这个基础设施以后，字节码 BUILD\_LIST 的实现就水到渠成了。实际上，我们上一节课已经借助 HiList 实现了元组（tuple），所以这里完全可以复用 BUILD\_TUPLE 的逻辑，你可以看一下对应的代码。

```c++
void Interpreter::run(CodeObject* codes) {
    _frame = new FrameObject(codes);
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        FunctionObject* fo;
        ...
        switch (op_code) {
		...
            case ByteCode::BUILD_LIST:
            case ByteCode::BUILD_TUPLE:
                lst = new HiList();
                while (op_arg--) {
                    lst->set(op_arg, POP());
        ...
        }
    }
}

```

就像前面分析的，BUILD\_LIST 的实现就是新建一个列表，把栈上的元素取出来，放到列表中，再把这个列表放到栈顶。

编译并执行，就能看到这节课开始的两行代码可以正确地打印了。

列表对象上定义了很多操作，最典型的就是查找、修改、增加和删除。这节课我们就分别来研究一下，如何实现这些功能。

## 列表的取下标操作

列表取下标很像 C 语言中的数组，它是通过中括号语法进行索引的，例如：

```python
lst = ["hello", "world"]

# result is "hello"
print lst[0]

```

使用中括号和下标的形式取得列表中的指定元素，这种语法我们是第一次遇到，所以就可以通过 show\_file 工具进行观察，这种数组下标的语法会被翻译成怎样的字节码。

```plain
  4           8 LOAD_NAME                1 (print)
             10 LOAD_NAME                0 (lst)
             12 LOAD_CONST               2 (0)
             14 BINARY_SUBSCR
             16 CALL_FUNCTION            1
             18 POP_TOP
             20 LOAD_CONST               3 (None)
             22 RETURN_VALUE

```

这里出现了一个新的字节码：BINARY\_SUBSCR（第 4 行）。在这个字节码之前，已经把列表 lst 和整数 0 加载到了栈顶（第 1 行和第 2 行）。

BINARY\_SUBSCR的意义是取出列表 lst 的第 0 项，并把结果送入栈顶。这个字节码是 subscript 的缩写。

实际上，除了列表有取下标操作以外，string 对象也支持取下标操作。未来，我们还会遇到自定义类型中也可以支持取下标操作。因此，这就有必要在 HiObject 对象体系中引入取下标操作了。

我们先来定义 HiObject 中的 subscr 方法，然后再扩展到 HiList 和 HiString 类中去。

```c++
// object/hiObject.hpp
class HiObject {
    ...
    HiObject* subscr(HiObject* x);
};

// object/hiObject.cpp
HiObject* HiObject::subscr(HiObject* x) {
    return klass()->subscr(this, x);
}

```

在 Object 类中，我们把 subscr 的真正实现转移到它的 Klass 中去了。在 Klass 中，subscr 会是一个虚函数，通过虚函数机制保证了不同类型的对象可以调用相应的 subscr 方法。你可以看一下list 类型的实现。

```c++
// object/klass.hpp
class Klass {
private:
    ...
public:
    ...
    virtual HiObject* subscr   (HiObject* x, HiObject* y) { return 0; }
};

// object/hiList.hpp
class ListKlass : public Klass {
private:
    ...
public:
    ...
    virtual HiObject* subscr (HiObject* x, HiObject* y);
};

// object/hiList.cpp
HiObject* ListKlass::subscr(HiObject* x, HiObject* y) {
    assert(x && x->klass() == (Klass*) this);
    assert(y && y->klass() == (Klass*) IntegerKlass::get_instance());

    HiList * lx = (HiList*)x;
    HiInteger* iy = (HiInteger*)y;

    return lx->inner_list()->get(iy->value());
}

```

这段代码主要是描述了 Klass 的架构设计，真正在列表中取值的只有第 27 行而已。ListKlass 的 subscr 函数检查了第二个参数的类型，也就是下标，在 list 中它必须是整型（第 22 行）。

如果不是整型的话，assert 语句就不能成功，虚拟机会直接退出。实际上，Python 的正确行为是抛出异常，由于目前我们还没有实现异常机制，所以这里就先采用报错退出这种处理方式。除此之外的其他代码都比较简单，就不再解释了。

最后，我们还要在 Interpreter 中添加 BINARY\_SUBSCR 的实现，只需要把栈顶的两个对象取出来，再以第一个对象为参数，调用第二个对象的 subscr 方法即可。

```c++
void Interpreter::run(CodeObject* codes) {
    _frame = new FrameObject(codes);
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        FunctionObject* fo;
        ...
        switch (op_code) {
		...
            case ByteCode::BINARY_SUBSCR:
                v = POP();
                w = POP();
                PUSH(w->subscr(v));
                break;
        ...
        }
    }
}

```

到此为止，这节课开始的那个测试代码就可以正确执行了。

在完成了 list 的 subscr 操作之后，为 string 添加相应的操作就很简单了。整个流程的框架已经搭建起来了，我们只需要在 StringKlass 中添加 subscr 即可。

```c++
// object/hiString.hpp
class StringKlass : public Klass {
private:
    ...
public:
    ...
    virtual HiObject* subscr (HiObject* x, HiObject* y);
};

// object/hiString.cpp
HiObject* StringKlass::subscr(HiObject* x, HiObject* y) {
    assert(x && x->klass() == (Klass*) this);
    assert(y && y->klass() == (Klass*) IntegerKlass::get_instance());

    HiString * sx = (HiString*)x;
    HiInteger* iy = (HiInteger*)y;

    return new HiString(&(sx->value()[iy->value()]), 1);
}

```

字符串的取下标操作与列表的取下标操作几乎一样，区别在于两者的 subscr 方法的返回值类型不同。

列表的取下标操作的返回值是一个普通对象，而字符串的返回值则是另一个字符串。在 StringKlass 中先创建一个新的 string 对象。我们使用了带有长度参数的构造方法来创建这个字符串对象（第 18 行）。这个构造方法的具体实现，你可以参考 [第 7 节课](https://time.geekbang.org/column/article/774409) 字符串的实现部分。

到这里，取下标操作就完成了，接下来我们继续实现在列表中查找元素的功能。

## 判断列表中是否包含某元素

在 Python 中，查找列表是否包含了某个对象，通常使用 in 关键字，例如：

```python
l = ["hello", "world"]

if "hello" in l:
    # this statement will be executed
    print "yes"
else:
    print "no"

```

使用 in 关键字可以判断 `“hello”` 是否在列表中。和以前一样，我们使用 show\_file 工具查看这个例子的字节码。

```plain
             ...
  4          12 LOAD_CONST               0 ('hello')
             15 LOAD_NAME                0 (l)
             18 COMPARE_OP               6 (in)
             21 POP_JUMP_IF_FALSE       32
             ...

```

注意第 4 行的字节码 COMPARE\_OP。在 [第 5 节课](https://time.geekbang.org/column/article/772703) 实现控制流的时候，这个字节码就已经得到支持了，它可以对两个对象进行判断相等、比较大小等操作。

COMPARE\_OP 字节码是带有参数的，它的参数用于指定比较操作符的类型，比如 4 就代表大于，0 代表小于，2 代表等于。这节课 COMPARE\_OP 带了一个新的参数：6。括号里的注释也标明了，这个参数代表 in。

所以我们接下来就要在 COMPARE\_OP 中实现 in 比较操作。

```c++
void Interpreter::run(CodeObject* codes) {
    _frame = new FrameObject(codes);
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        switch (op_code) {
		...
            case ByteCode::COMPARE_OP:
                w = POP();
                v = POP();

                switch(op_arg) {
                ...
                case ByteCode::IN:
                    PUSH(w->contains(v));
                    break;
                ...
                default:
                    printf("Error: Unrecognized compare op %d\n", op_arg);

                }
                break;
        ...
        }
    }
}

```

和取下标以及比较是否相等的操作一样，我们通过调用 w 的 contains 方法来判断 w 中是否含有 v。

not in 的实现就交给你自己了，只需要把 contains 的返回进行取反操作就可以了。也就是说，如果 contains 为 True，就往栈顶送入 False，如果 contains 的返回值为 False，就往栈顶送入 True。

接下来，我们就从 HiObject 开始增加 contains 方法，思路和步骤与之前添加 subscr 是一样的，具体的代码如下所示：

```c++
// object/hiObject.hpp
class HiObject {
    ...
    HiObject* subscr(HiObject* x);
	HiObject* contains(HiObject* x);
};

// object/hiObject.cpp
HiObject* HiObject::contains(HiObject* x) {
    return klass()->contains(this, x);
}

// object/klass.hpp
class Klass {
private:
    ...
public:
    ...
    virtual HiObject* contains (HiObject* x, HiObject* y) { return 0; }
};

```

然后，在 ListKlass 中，添加 contains 方法的具体实现。

```c++
// object/hiList.hpp
class ListKlass : public Klass {
private:
    ...
public:
    ...
    virtual HiObject* contains (HiObject* x, HiObject* y);
};

// object/hiList.cpp
HiObject* ListKlass::contains(HiObject* x, HiObject* y) {
    HiList * lx = (HiList*)x;
    assert(lx && lx->klass() == (Klass*) this);

    int size = lx->_inner_list->size();
    for (int i = 1; i < size; i++) {
        if (lx->_inner_list->get(i)->equal(y))
            return Universe::HiTrue;
    }

    return Universe::HiFalse;
}

```

contains 方法的核心逻辑是遍历整个 list，对于它的每一个元素，都与参数 y 进行比较，查看它们是否相等。如果相等，就返回 True，如果不相等，就在方法的结尾返回 False。

注意，这里使用 equal 方法来判断对象是否相等。这个方法在 klass 中也是一个虚函数。比较相等的具体逻辑都封装在相应类型的 klass 中了。你可以通过查看 [第 5 节课](https://time.geekbang.org/column/article/772703) 和 [第 7 节课](https://time.geekbang.org/column/article/774409) 的相关内容进行复习。

字符串类型也支持 in 比较，例如：

```python
if "lo" in "hello":
    # this statement will be executed
    print("yes")
else:
    print("no")

```

在字符串里添加 contains 方法，相信你已经可以驾轻就熟了，我们这里就不再重复了，你可以自己动手尝试一下。

判断列表中是否包含某一元素的功能就实现完了。对于一个数据结构来说，支持增删查改的操作是必须具备的能力。接下来，我们会依次实现这些功能。

## 向列表中添加元素

往列表中添加元素有两个比较常用的方法，一个是调用 append 方法，另一个是调用 insert 方法。我们先来实现 append 方法。

先来写一个 append 方法的测试用例。

```python
l = []
l.append(0)
print l

```

在使用 show\_file 工具查看字节码之前，你可以试着自己推断一下，这段代码所对应的字节码是什么。然后再来核查自己的推测是不是正确。append 方法的调用会被翻译成以下字节码：

```plain
  2           4 LOAD_NAME                0 (lst)
              6 LOAD_METHOD              1 (append)
              8 LOAD_CONST               0 (1)
             10 CALL_METHOD              1
             12 POP_TOP

```

这些字节码都已经实现过了。这里只要再为 List 类型增加 append 方法即可。对照在 [第 12 节课](https://time.geekbang.org/column/article/778919) 为字符串增加 upper 方法的过程，list 的 append 方法是完全一样的。

首先，完成 append 方法的定义。

```c++
// object/hiList.hpp
HiObject* list_append(ObjList args);

// object/hiList.cpp
HiObject* list_append(ObjList args) {
    ((HiList*)(args->get(0)))->append(args->get(1));
    return Universe::HiNone;
}

```

list\_append 方法所接受的参数和 string\_upper 一样，也是一个 ArrayList。ArrayList 的第一项，也就是第一个参数，是要添加元素的列表，第二个参数是待添加的元素，它的返回值是 None。

接下来，我们要把它放到 ListKlass 的 klass\_dict 中去。只需要在 ListKlass 的构造方法中添加 klass\_dict 的初始化逻辑即可。

```c++
ListKlass::ListKlass() {
    HiDict * klass_dict = new HiDict();
    klass_dict->put(new HiString("append"),
        new FunctionObject(list_append));
    set_klass_dict(klass_dict);
}

```

通过这种方式就把字符串 `“append”` 与内建方法联系了起来。当虚拟机执行到了 LOAD\_METHOD 时，就通过字符串查找到了 list\_append 所对应的 FunctionObject。然后，在 HiObject 的 getattr 方法中，列表对象会与 append 方法绑定在一起，生成一个 MethodObject。

所以，当执行到 CALL\_METHOD 时，本质上是通用这个经过绑定的 MethodObject，进一步就会调用 Interpreter::build\_frame 方法。在那里，我们对 MethodObject 做了正确的处理。

经过这样的推演，我们就知道这个过程是完整的了。编译执行，这节课开始处的测试用例就可以正确执行。

往列表中添加元素的第二种方法是 insert 方法，例如：

```python
l = [1, 2]
l.insert(0, 3)
# result is [3, 1, 2]
print(l)

```

insert 方法与 append 方法在原理上并无二致。作为练习，就留给你自行添加。

## 修改列表中的元素

修改列表中的元素与 C 语言中的数组操作相同，是使用取下标操作符和赋值操作完成的。例如：

```python
l = [1, 2]
l[0] = 3
# result is [3, 2]
print(l)

```

修改元素与添加元素不同，不再是使用内建方法来完成这个功能了，而是使用了一种新的语法。往往新的语法所对应的是新的字节码。接下来我们就来验证上述例子所对应的字节码：

```plain
             ...
 12          12 LOAD_CONST               2 (3)
             15 LOAD_NAME                0 (l)
             18 LOAD_CONST               3 (0)
             21 STORE_SUBSCR
			 ...

```

正如我们所预料的，在第 5 行出现了一个新的字节码： **STORE\_SUBSCR**。这个字节码和 BINARY\_SUBSCR 正好是一对相对应的操作，一个是用于取列表元素，一个是用于修改列表元素。

除了列表支持修改列表元素的操作之外，第 15 节课要讲的字典类型也支持这个操作，另外，自定义类型也可以重载这个操作。所以我们有必要在 HiObject 类型中增加元素修改的操作。

```c++
// object/hiObject.hpp
class HiObject {
    ...
    HiObject* subscr(HiObject* x);
    void      store_subscr(HiObject* x, HiObject* y);
    HiObject* contains(HiObject* x);
};

// object/hiObject.cpp
void HiObject::store_subscr(HiObject* x, HiObject* y) {
    klass()->store_subscr(this, x, y);
}

```

与前边添加 subscr 和 contains 方法一样，我们在 HiObject 类的 store\_subscr 方法中，直接调用它所对应的 klass 的 store\_subscr 方法。所以，接下来我们就要在 klass 中添加 store\_subscr 方法。

```c++
// object/klass.hpp
class Klass {
private:
    ...
public:
    ...
    virtual void store_subscr  (HiObject* x, HiObject* y, HiObject* z) { return; }
};

// object/hiList.hpp
class ListKlass : public Klass {
private:
    ...
public:
    ...
    virtual void store_subscr (HiObject* x, HiObject* y, HiObject* z);
};

// object/hiList.cpp
void ListKlass::store_subscr(HiObject* x, HiObject* y, HiObject* z) {
    assert(x && x->klass() == (Klass*) this);
    assert(y && y->klass() == IntegerKlass::get_instance());

    HiList * lx = (HiList*)x;
    HiInteger* iy = (HiInteger*)y;

    lx->inner_list()->set(iy->value(), z);
}

```

ListKlass 的 store\_subscr 方法的第一个参数代表要修改的列表，第二个参数代表下标，第三个参数代表真正的目标对象。

store\_subscr 的主要逻辑是很简单的，它只是调用了 inner\_list 的 set 方法，把相应序号的元素设为 z。最后，要实现的字节码 STORE\_SUBSCR 也就水到渠成了。

```c++
void Interpreter::run(CodeObject* codes) {
    _frame = new FrameObject(codes);
	HiObject *v, *w, *u;
	...
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        switch (op_code) {
		...
            case ByteCode::STORE_SUBSCR:
                u = POP();
                v = POP();
                w = POP();
                v->store_subscr(u, w);
                break;
        ...
        }
    }
}

```

这是我们第一次遇到一个不带参数的字节码关系到三个对象的情况，所以一定要注意三个参数的顺序，不要搞错了。到这里，我们就能正确地执行这部分开始的那个例子了。

## 在列表中查找元素

查找元素本质上与判断列表是否包含特定元素的操作是一样的。不同之处在于查找元素的操作，其返回值是这个元素在列表中的序号，如果元素不在列表中，则抛出异常（ValueError）。而判断是否包含操作的返回值是布尔型。

在列表中查找元素的位置，需使用 index 方法。与 append 方法类似，我们也采用内建方法来实现它。先来定义一个名为 list\_index 的方法。

```c++
HiObject* list_index(ObjList args) {
    HiList* list = (HiList*)(args->get(0));
    HiObject* target = (HiObject*)(args->get(1));

    assert(list && list->klass() == ListKlass::get_instance());

    for (int i = 0; i < list->inner_list()->size(); i++) {
        if (list->get(i)->equal(target) == (HiObject*)Universe::HiTrue) {
            return new HiInteger(i);
        }
    }

    return NULL;
}

```

这个方法的核心逻辑是遍历列表的每一个元素，把它与目标元素进行比较，如果 equal 方法的返回值为 True，就认为在列表中找到目标元素。然后把目标元素的序号返回。如果没有找到，应该抛出异常，由于我们还没有实现异常，这里先使用空返回值代替。

最后只需要在 ListKlass 的构造函数里把字符串 `“index”` 与 `list_index` 方法关联起来就可以了。

```c++
ListKlass::ListKlass() {
    HiDict * klass_dict = new HiDict();
    ...
    klass_dict->put(new HiString("index"),
        new FunctionObject(list_index));
    ...
    set_klass_dict(klass_dict);
}

```

到这里，我们就把列表的增、改、查的功能实现了。下节课我们会继续实现删除元素的功能。

## 总结

列表和字典是 Python 虚拟机中两个核心的内建数据结构。这节课我们重点实现了列表的基本功能。

首先是列表的表示，在这节课之前，我们已经实现了 HiList 类，但它的功能并不完善。所以这节课的第一个任务是补全 ListKlass，把列表类也加入到虚拟机的对象体系中来。

接下来，就是向列表中增加功能。这里我们把列表的功能分成两大类，第一类是通过内建方法实现的，第二类是通过新的语法和字节码来扩展的。

内建方法包括向列表的末尾添加元素的append方法，向列表的指定位置添加元素的insert方法，还有查询元素在列表中的位置的 index方法。

新增的语法包括通过取下标访问列表中的元素，对应的字节码是BINARY\_SUBSCR；判断列表中是否包括某个元素，对应的字节码说 COMPARE\_OP/in；还有修改列表中的元素，字节码是 STORE\_SUBSCR。

增加了这些功能以后，列表就基本可用了。下节课我们会继续补齐列表的其他功能。

## 思考题

字符串的 contains 方法需要在字符串中进行子串查找操作。你知道有哪些高效的子串查找算法吗？欢迎你把你知道的方法分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！