你好，我是海纳。

上一节课，我们使用 Python 源码实现了 Exception 类，从而构建起了异常对象的继承体系，同时也实现了异常对象的匹配功能。在这个基础上，我们进一步实现了用于处理异常控制流的几条字节码。

第一条重要的字节码是 SETUP\_FINALLY，它的作用是创建一个 Block，指定了如果在执行 try 语句的过程中发生异常应该跳转到哪里执行。第二条是 CALL\_FINALLY，它的作用是如果 try 语句正常结束了，就跳转进 finally 子句执行。这节课，我们就来实现整个异常控制流的最后一条重要的指令，就是 **END\_FINALLY**，我们要在 END\_FINALLY 中增加恢复异常的逻辑。从而让解释器可以在退出函数栈帧的时候还能正确地维护异常对象。

## 实现 END\_FINALLY

就像之前分析的，END\_FINALLY 的主要作用是结束 finally 子句的执行。根据上节课说的进入 finally 子句的三种情况，我们这里分别做了处理，你可以看一下具体实现。

```c++
void Interpreter::eval_frame() {
    ...
    while (_frame->has_more_codes()) {
	    unsigned char op_code = _frame->get_op_code();
        ...
        switch (op_code) {
		...
            case ByteCode::END_FINALLY: {
                v = POP();
                long long t = (long long)v();
                if (t == 0) {
                    // do nothing.
                }
                else if (t & 0x1) {
                    _frame->set_pc(t >> 1);
                }
                else {
                    _exception_class = v;
                    _pending_exception = POP();
                    _trace_back = POP();
                    _int_status = IS_EXCEPTION;
                }
                break;
            }
        ...
        }
    }
}

```

由此可见，END\_FINALLY 的实现正好对应了三种情况，第一种情况对应 BEGIN\_FINALLY，这个时候栈顶上只有一个数字 0，所以遇到这种情况，就什么都不用做（第 11 到 13 行）。

第二种情况栈上的值是一个地址，这对应了 CALL\_FINALLY，这种情况下，只要把解释器的 pc 值修改为栈上的值就可以了（第14 至 16 行）。

最后一种是发生异常了，通过 SETUP\_FINALLY Block 进入的，这种情况下，当 finally 子句执行完以后，就要从栈上恢复异常状态，进行进一步的处理（第 17 至 22 行）。所谓进一步处理， 指的是有可能更外层还有 except 子句，也有可能引发函数退栈，如果是在主文件中，还有可能直接导致进程退出。

最后，我们再把一些用于处理异常时的栈状态的字节码补齐，例如：

```c++
            case ByteCode::POP_EXCEPT: {
                Block b = _frame->pop_block();
                assert(b._type == ByteCode::EXCEPT_HANDLER);
                assert(STACK_LEVEL() >= b._level + 3 &&
                    STACK_LEVEL() <= b._level + 4);
                _exception_class = POP();
                _pending_exception = POP();
                _trace_back = POP();
                _int_status = IS_EXCEPTION;
                break;
            }

```

POP\_EXCEPT 是明确地知道当前解释器已经发生了异常情况时，在 except 子句或者 finally 子句中用来恢复异常所使用的。所以它的功能只是 END\_FINALLY 的一部分。

到这里，我们就完成了基本的异常处理机制。你可以试着运行一下这节课开始的那个例子，再测试一下异常和 finally 子句的组合是否能够正常执行。

接下来，我们关注异常处理的最后一个对象，那就是用于回栈的 Traceback 对象。

## Traceback 对象

Traceback 是指发生异常时，用于记录异常栈信息的一种机制。我们用一个例子演示一下。

```python
def foo(a):
    b = a - 1
    bar(a, b)

def bar(a, b):
    raise Exception("something wrong!")

foo(1)

```

使用 Python 执行这个例子，结果是这样的：

```plain
Traceback (most recent call last):
  File "test_tb.py", line 8, in <module>
    foo(1)
  File "test_tb.py", line 3, in foo
    bar(a, b)
  File "test_tb.py", line 6, in bar
    raise Exception("something wrong!")
Exception: something wrong!

```

执行到 bar 函数中的语句时，调用栈是由 **main** 调用了 foo 方法，再由 foo 调用了 bar 方法。

如果这个时候发生了异常，并且异常没有被 except 语句处理掉，那么就会使用默认的处理方式，也就是退回到上一帧。如果已经退到了最后一帧，就打印 Traceback，并且退出程序。

我们先从最基本的结构开始实现，首先要实现 Traceback 类型，可以考虑使用 C++ 实现，也可以使用 Python 实现。因为 Traceback 要访问栈帧，从栈帧中获取信息，所以使用 C++ 在虚拟机内部实现会更方便一些。

```c++
class StackElementKlass : public Klass {
private:
    StackElementKlass() {}
    static StackElementKlass* _instance;

public:
    static StackElementKlass* get_instance();

    virtual void print(HiObject* x);
    virtual size_t size();
    virtual void oops_do(OopClosure* f, HiObject* obj);
};

class StackElement : public HiObject {
friend StackElementKlass;
private:
    HiString*   _file_name;
    HiString*   _func_name;
    int         _line_no;

public:
    StackElement(HiString* fname, HiString* mname, int lineno);
};

class TracebackKlass : public Klass {
private:
    TracebackKlass() {}
    static TracebackKlass* _instance;

public:
    static TracebackKlass* get_instance();

    virtual void print(HiObject* x);
    virtual size_t size();
    virtual void oops_do(OopClosure* f, HiObject* obj);
};

class Traceback : public HiObject {
friend class TracebackKlass;
private:
    HiList*   _stack_elements;

public:
    Traceback();

    void record_frame(FrameObject* frame);
};

```

与其他继承自 HiObject 的类型相似，Traceback 类型也有自己的 Klass，在 Klass 里增加 GC 接口，实现 print 方法。Traceback 中定义了一个列表 \_stack\_elements，其中记录着多个 StackElement。而 StackElement 中则存着栈帧的信息。

在刚刚那个例子中，我们已经观察到了 Traceback 的打印是由多帧组成的，我们把每一帧的信息都存到 StackElement 这个结构中。其中最重要的三个信息就是文件名、函数名和当前行数。可以看到，在 StackElement 中，我们分别加以定义。

其他地方就不再解释了，创建对象你应该都已经比较熟悉了。在异常处理的过程中，一直跟在 exception\_class 后面的 Traceback 对象，终于在这里补齐了。

如果解释器的状态不是 OK，并且当前栈帧的 block\_stack 为空，也就是没有其他的 Block 了，我们就可以离开栈帧了。所以这里可以在处理异常结束的地方增加离开函数栈帧的代码。

```c++
void Interpreter::eval_frame() {
    ...
    while (_frame->has_more_codes()) {
        ...
        switch (op_code) {
        } // end of switch

		// handle EXCEPTION with loop stack is not empty
		...

        // has pending exception and no handler found, unwind stack.
        if (_int_status == IS_EXCEPTION && _frame->blocks()->length() == 0) {
            _trace_back->as<Traceback>()->record_frame(_frame);

            if (_frame->is_first_frame() ||
                    _frame->is_entry_frame())
                return;
            leave_frame();
            goto error_handling;
        }
    }
}

```

第 13 行使用了 Traceback 的 record\_frame 方法来记录当前栈帧。你可以看一下它的具体实现。

```c++
void Traceback::record_frame(FrameObject* frame) {
    _stack_elements->append(
            new StackElement(
                frame->file_name(),
                frame->func_name(),
                frame->lineno()));
}

HiString* FrameObject::file_name() {
    return _codes->_file_name;
}

HiString* FrameObject::func_name() {
    return _codes->_co_name;
}

int FrameObject::lineno() {
    int pc_offset = 0;
    int line_no = _codes->_lineno;

    const char* lnotab = _codes->_notable->value();
    int length = _codes->_notable->length();

    for (int i = 0; i < length; i++) {
        pc_offset += lnotab[i++];
        if (pc_offset >= _pc)
            return line_no;

        line_no += lnotab[i];
    }

    return line_no;
}

```

\_stack\_elements 是一个列表，它的每一个元素都是一个 StackElement 实例。其中记录了这个栈帧所对应的函数名和文件名，最重要的一个信息是行号。也就是说提示我们问题发生在哪一行。

行号的信息也存储在 CodeObject 中，我们以前还从来没有使用过。栈帧中只保留了 pc 的信息，它代表的是字节码的位置，而不是源代码的位置。要把字节码位置转换成源代码位置，就要使用 CodeObject 的 lineno 和 notable 来进行转换。

lineno 代表了这个函数源代码的起始行号，notable 则描述了字节码与源文件的行号对应关系。

我们来看一个具体的例子。

```python
print("hello")

def foo():
    a = 1 + 1
    print(a)

```

通过 show\_file 工具查看 foo 方法的字节码。

```plain
      code
         argcount 0
         nlocals 1
         stacksize 2
         flags 0043
         code 64017d0074007c008301010064005300
  4           0 LOAD_CONST               1 (2)
              2 STORE_FAST               0 (a)

  5           4 LOAD_GLOBAL              0 (print)
              6 LOAD_FAST                0 (a)
              8 CALL_FUNCTION            1
             10 POP_TOP
             12 LOAD_CONST               0 (None)
             14 RETURN_VALUE
         consts
            None
            2
         names ('print',)
         varnames ('a',)
         freevars ()
         cellvars ()
         filename '/Users/dandan/hinusDocs/gitee/pythonvm/build/htb.py'
         name 'foo'
         firstlineno 3
         lnotab 00010401

```

注意到 firstlineno 的值是 3 ，这说明 foo 方法是在第 3 行开始被定义的。

lnotab 每两位是一个独立的数字，每两个数字为一组，代表源代码行号和字节码行号的变化。例如，00010601 可以拆分为 (\[00, 01\], \[06, 01\]) 这样的结构。字节码的起始偏移是 0，而源代码的起始行号是 3。\[00, 01\] 代表了字节码偏移为 0+0 的地方对应的源代码是 3+1，也就是 4。

第二组，\[06, 01\] 代表了字节码偏移为 0+6 的地方对应的源代码是 4+1，也就是 5。就是说，在 lnotab 里，并不是直接把字节码偏移与源代码行号的对应关系记录下来，而是记录当源代码行号发生变化时，字节码偏移发生了多少变化。

明白了这个公式以后，FrameObject 的 lineno 方法也就清楚了。再回过头来看这个方法的实现，我们每次通过不断地改变 pc 偏移量，并且检查当前的 pc 是否落在两次变化之间，来确定当前的 pc 所对应的源代码行号。

如果在退栈的过程中，一直没有遇到可以处理这个异常的 except 语句，这个异常就会导致栈帧回退到最后一帧。在这里，虚拟机要提供一个默认的实现：打印这个 traceback。

```c++
void Interpreter::run(CodeObject* codes) {
    _frame = new FrameObject(codes);
    _frame->locals()->put(ST(name), new HiString("__main__"));
    eval_frame();

    if (_int_status == IS_EXCEPTION) {
        _int_status = IS_OK;

        _trace_back->print();
        _pending_exception->print();
        printf("\n");

        _trace_back = NULL;
        _pending_exception = NULL;
        _exception_class = NULL;
    }

    destroy_frame();
}

void TracebackKlass::print(HiObject* x) {
    Traceback* tbx = (Traceback*)x;

    printf("Traceback (most recent call last):\n");
    for (int i = tbx->_stack_elements->size() - 1; i >= 0; i--) {
        tbx->_stack_elements->get(i)->print();
    }
}

void StackElementKlass::print(HiObject* x) {
    StackElement* xse = (StackElement*)x;
    printf("  File \"");
    xse->_file_name->print();
    printf("\", line %d,", xse->_line_no);
    printf(" in ");
    xse->_func_name->print();
    printf("\n");
}

```

在 run 方法中，如果 eval\_frame 结束以后，解释器的状态是 EXCEPTION，那就在这里把它处理掉。具体的动作是把 Traceback 打印出来，将状态改为 OK，并且把所有的异常信息都清空。Traceback 的打印也是比较简单的，只需要把每个栈帧的信息打印出来就可以了。

到这里，我们就把与异常相关的所有机制全部实现了。

## 总结

这节课完成了异常的全部功能以后，我们可以回顾一下异常处理的全部流程。

首先，解释器在正常执行的情况下，有些语句可能会发生异常，比如除法中遇到除数为 0 的情况会产生 ZeroDivisionError，循环执行到最后一个元素时会产生 StopIteration 异常，访问列表下标越界时会产生 IndexOutOrRangeErrror 等等。

如果异常发生在 try 语句中，解释器就会通过 SETUP\_FINALLY Block 跳转入 except 子句或者 finally 子句执行。这个时候，要把栈上的 Block 状态设置为 EXCEPT\_HANDLER，表示解释器正在处理异常对象。在这之前，解释器会把异常对象放入栈上，同时修改异常状态，这样解释器才能顺利执行 except 语句和 finally 语句中的指令。

最后，当 finally 子句执行完以后，END\_FINALLY 会把异常状态全部恢复，以便于解释器带着异常状态退出当前函数栈帧。同时，我们还实现了 Traceback 对象在退栈时记录栈帧。这样异常处理的全部功能才算完成。

## 思考题

在现有的条件下，如果让你自己实现自定义类的迭代器，你会如何实现呢？欢迎你把思考结果分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！