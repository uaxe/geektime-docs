你好，我是景霄。

我想你对Python中的with语句一定不陌生，在专栏里它也曾多次出现，尤其是在文件的输入输出操作中，不过我想，大部分人可能习惯了它的使用，却并不知道隐藏在其背后的“秘密”。

那么，究竟with语句要怎么用，与之相关的上下文管理器（context manager）是什么，它们之间又有着怎样的联系呢？这节课，我就带你一起揭开它们的神秘面纱。

## 什么是上下文管理器？

在任何一门编程语言中，文件的输入输出、数据库的连接断开等，都是很常见的资源管理操作。但资源都是有限的，在写程序时，我们必须保证这些资源在使用过后得到释放，不然就容易造成资源泄露，轻者使得系统处理缓慢，重则会使系统崩溃。

光说这些概念，你可能体会不到这一点，我们可以看看下面的例子：

```
for x in range(10000000):
    f = open('test.txt', 'w')
    f.write('hello')

```

这里我们一共打开了10000000个文件，但是用完以后都没有关闭它们，如果你运行该段代码，便会报错：

```
OSError: [Errno 23] Too many open files in system: 'test.txt'

```

这就是一个典型的资源泄露的例子。因为程序中同时打开了太多的文件，占据了太多的资源，造成系统崩溃。

为了解决这个问题，不同的编程语言都引入了不同的机制。而在Python中，对应的解决方式便是上下文管理器（context manager）。上下文管理器，能够帮助你自动分配并且释放资源，其中最典型的应用便是with语句。所以，上面代码的正确写法应该如下所示：

```
for x in range(10000000):
    with open('test.txt', 'w') as f:
        f.write('hello')

```

这样，我们每次打开文件 `“test.txt”`，并写入 `‘hello’` 之后，这个文件便会自动关闭，相应的资源也可以得到释放，防止资源泄露。当然，with语句的代码，也可以用下面的形式表示：

```
f = open('test.txt', 'w')
try:
    f.write('hello')
finally:
    f.close()

```

要注意的是，最后的finally block尤其重要，哪怕在写入文件时发生错误异常，它也可以保证该文件最终被关闭。不过与with语句相比，这样的代码就显得冗余了，并且还容易漏写，因此我们一般更倾向于使用with语句。

另外一个典型的例子，是Python中的threading.lock类。举个例子，比如我想要获取一个锁，执行相应的操作，完成后再释放，那么代码就可以写成下面这样：

```
some_lock = threading.Lock()
some_lock.acquire()
try:
    ...
finally:
    some_lock.release()

```

而对应的with语句，同样非常简洁：

```
some_lock = threading.Lock()
with somelock:
    ...

```

我们可以从这两个例子中看到，with语句的使用，可以简化了代码，有效避免资源泄露的发生。

## 上下文管理器的实现

### 基于类的上下文管理器

了解了上下文管理的概念和优点后，下面我们就通过具体的例子，一起来看看上下文管理器的原理，搞清楚它的内部实现。这里，我自定义了一个上下文管理类FileManager，模拟Python的打开、关闭文件操作：

```
class FileManager:
    def __init__(self, name, mode):
        print('calling __init__ method')
        self.name = name
        self.mode = mode
        self.file = None

    def __enter__(self):
        print('calling __enter__ method')
        self.file = open(self.name, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('calling __exit__ method')
        if self.file:
            self.file.close()

with FileManager('test.txt', 'w') as f:
    print('ready to write to file')
    f.write('hello world')

## 输出
calling __init__ method
calling __enter__ method
ready to write to file
calling __exit__ method

```

需要注意的是，当我们用类来创建上下文管理器时，必须保证这个类包括方法 `”__enter__()”` 和方法 `“__exit__()”`。其中，方法 `“__enter__()”` 返回需要被管理的资源，方法 `“__exit__()”` 里通常会存在一些释放、清理资源的操作，比如这个例子中的关闭文件等等。

而当我们用with语句，执行这个上下文管理器时：

```
with FileManager('test.txt', 'w') as f:
    f.write('hello world')

```

下面这四步操作会依次发生：

1. 方法 `“__init__()”` 被调用，程序初始化对象FileManager，使得文件名（name）是 `"test.txt"`，文件模式(mode)是 `'w'`；
2. 方法 `“__enter__()”` 被调用，文件 `“test.txt”` 以写入的模式被打开，并且返回FileManager对象赋予变量f；
3. 字符串 `“hello world”` 被写入文件 `“test.txt”`；
4. 方法 `“__exit__()”` 被调用，负责关闭之前打开的文件流。

因此，这个程序的输出是：

```
calling __init__ method
calling __enter__ method
ready to write to file
calling __exit__ meth

```

另外，值得一提的是，方法 `“__exit__()”` 中的参数 `“exc_type, exc_val, exc_tb”`，分别表示exception\_type、exception\_value和traceback。当我们执行含有上下文管理器的with语句时，如果有异常抛出，异常的信息就会包含在这三个变量中，传入方法 `“__exit__()”`。

因此，如果你需要处理可能发生的异常，可以在 `“__exit__()”` 添加相应的代码，比如下面这样来写：

```
class Foo:
    def __init__(self):
        print('__init__ called')

    def __enter__(self):
        print('__enter__ called')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        print('__exit__ called')
        if exc_type:
            print(f'exc_type: {exc_type}')
            print(f'exc_value: {exc_value}')
            print(f'exc_traceback: {exc_tb}')
            print('exception handled')
        return True

with Foo() as obj:
    raise Exception('exception raised').with_traceback(None)

# 输出
__init__ called
__enter__ called
__exit__ called
exc_type: <class 'Exception'>
exc_value: exception raised
exc_traceback: <traceback object at 0x1046036c8>
exception handled

```

这里，我们在with语句中手动抛出了异常“exception raised”，你可以看到， `“__exit__()”` 方法中异常，被顺利捕捉并进行了处理。不过需要注意的是，如果方法 `“__exit__()”` 没有返回True，异常仍然会被抛出。因此，如果你确定异常已经被处理了，请在 `“__exit__()”` 的最后，加上 `“return True”` 这条语句。

同样的，数据库的连接操作，也常常用上下文管理器来表示，这里我给出了比较简化的代码：

```
class DBConnectionManager:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.connection = None

    def __enter__(self):
        self.connection = DBClient(self.hostname, self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

with DBConnectionManager('localhost', '8080') as db_client:

```

与前面FileManager的例子类似：

- 方法 `“__init__()”` 负责对数据库进行初始化，也就是将主机名、接口（这里是localhost和8080）分别赋予变量hostname和port；
- 方法 `“__enter__()”` 连接数据库，并且返回对象DBConnectionManager；
- 方法 `“__exit__()”` 则负责关闭数据库的连接。

这样一来，只要你写完了DBconnectionManager这个类，那么在程序每次连接数据库时，我们都只需要简单地调用with语句即可，并不需要关心数据库的关闭、异常等等，显然大大提高了开发的效率。

### 基于生成器的上下文管理器

诚然，基于类的上下文管理器，在Python中应用广泛，也是我们经常看到的形式，不过Python中的上下文管理器并不局限于此。除了基于类，它还可以基于生成器实现。接下来我们来看一个例子。

比如，你可以使用装饰器contextlib.contextmanager，来定义自己所需的基于生成器的上下文管理器，用以支持with语句。还是拿前面的类上下文管理器FileManager来说，我们也可以用下面形式来表示：

```
from contextlib import contextmanager

@contextmanager
def file_manager(name, mode):
    try:
        f = open(name, mode)
        yield f
    finally:
        f.close()

with file_manager('test.txt', 'w') as f:
    f.write('hello world')

```

这段代码中，函数file\_manager()是一个生成器，当我们执行with语句时，便会打开文件，并返回文件对象f；当with语句执行完后，finally block中的关闭文件操作便会执行。

你可以看到，使用基于生成器的上下文管理器时，我们不再用定义 `“__enter__()”` 和 `“__exit__()”` 方法，但请务必加上装饰器@contextmanager，这一点新手很容易疏忽。

讲完这两种不同原理的上下文管理器后，还需要强调的是，基于类的上下文管理器和基于生成器的上下文管理器，这两者在功能上是一致的。只不过，

- 基于类的上下文管理器更加flexible，适用于大型的系统开发；
- 而基于生成器的上下文管理器更加方便、简洁，适用于中小型程序。

无论你使用哪一种，请不用忘记在方法 `“__exit__()”` 或者是finally block中释放资源，这一点尤其重要。

## 总结

这节课，我们先通过一个简单的例子，了解了资源泄露的易发生性，和其带来的严重后果，从而引入了应对方案——即上下文管理器的概念。上下文管理器，通常应用在文件的打开关闭和数据库的连接关闭等场景中，可以确保用过的资源得到迅速释放，有效提高了程序的安全性，

接着，我们通过自定义上下文管理的实例，了解了上下文管理工作的原理，并一起学习了基于类的上下文管理器和基于生成器的上下文管理器，这两者的功能相同，具体用哪个，取决于你的具体使用场景。

另外，上下文管理器通常和with语句一起使用，大大提高了程序的简洁度。需要注意的是，当我们用with语句执行上下文管理器的操作时，一旦有异常抛出，异常的类型、值等具体信息，都会通过参数传入 `“__exit__()”` 函数中。你可以自行定义相关的操作对异常进行处理，而处理完异常后，也别忘了加上 `“return True”` 这条语句，否则仍然会抛出异常。

## 思考题

那么，在你日常的学习工作中，哪些场景使用过上下文管理器？使用过程中又遇到了哪些问题，或是有什么新的发现呢？欢迎在下方留言与我讨论，也欢迎你把这篇文章分享出去，我们一起交流，一起进步。