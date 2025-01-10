你好，我是朱涛。从今天开始，我们就正式踏上Kotlin语言学习与实践的旅途了。这节课，我想先带你来学习下Kotlin的基础语法，包括变量、基础类型、函数和流程控制。这些基础语法是程序最基本的元素。

不过，如果你有使用Java的经验，可能会觉得今天的内容有点多余，毕竟Kotlin和Java的基础语法是比较相似的，它们都是基于JVM的语言。但其实不然，Kotlin作为一门新的语言，它包含了许多新的特性，由此也决定着Kotlin的代码风格。 **如果你不够了解Kotlin的这些新特性，你会发现自己只是换了种方式在写Java而已。**

并且，在具备Java语言的知识基础上，这节课的内容也可以帮你快速将已有的经验迁移过来。这样的话，针对相似的语法，你可以直接建立Kotlin与Java的对应关系，进而加深理解。当然，即使你没有其他编程经验也没关系，从头学即可，Kotlin的语法足够简洁，也非常适合作为第一门计算机语言来学习。

在课程中，我会用最通俗易懂的语言，来给你解释Kotlin的基础知识，并且会结合一些Java和Kotlin的代码案例，来帮助你直观地体会两种语言的异同点。而针对新的语法，我也会详细解释它存在的意义，以及都填补了Java的哪些短板，让你可以对Kotlin新语法的使用场景做到心中基本有数。

## 开发环境

在正式开始学习基础语法之前，我们还需要配置一下Kotlin语言的环境，因为直接从代码开始学能给我们带来最直观的体验。

那么要运行Kotlin代码，最快的方式，就是 **使用Kotlin官方的** [PlayGround](https://play.kotlinlang.org/)。通过这个在线工具，我们可以非常方便地运行Kotlin代码片段。当然，这种方式用来临时测试一小段代码是没有问题的，但对于复杂的工程就有些力不从心了。

另一种方式，也是 **我个人比较推荐的方式，那就是安装** [IntelliJ IDEA](https://www.jetbrains.com/idea/download/)。它是Kotlin官方提供的集成开发工具，也是世界上最好的IDE之一，如果你用过Android Studio，你一定会对它很熟悉，因为Android Studio就是由IntelliJ IDEA改造的。

如果你的电脑没有Java环境，在安装完最新版的IntelliJ IDEA以后，通过“File -> Project Structure -> SDKs”，然后点击“加号按钮”就可以选择第三方提供的OpenJDK 1.8版本进行下载了。

![图片](https://static001.geekbang.org/resource/image/04/a7/04cf1b899574ceff2ecd099e41af1fa7.gif?wh=1000x770)

当然，这里我更推荐你可以自己手动从 [Oracle官网](https://www.oracle.com/java/technologies/downloads/) 下载JDK 1.6、1.7、1.8、11这几个版本，然后再安装、配置Java多版本环境。这在实际工作中也是必备的。

需要注意的是，IntelliJ IDEA分为Ultimate付费版和Community免费版，对于我们的Kotlin学习来说，免费版完全够用。

这样，在配置好了开发环境之后，我们就可以试着一边敲代码，一边体会、思考和学习Kotlin语言中这些最基础的语法知识了。那么下面我们就来看下，在Kotlin语言中是如何定义变量的吧。

## 变量

在Java/C当中，如果我们要声明变量，我们必须要声明它的类型，后面跟着变量的名称和对应的值，然后以分号结尾。就像这样：

```java
Integer price = 100;

```

而Kotlin则不一样，我们要使用“ **val**”或者是“ **var**”这样的关键字作为开头，后面跟“变量名称”，接着是“变量类型”和“赋值语句”，最后是分号结尾。就像这样：

```plain
/*
关键字     变量类型
 ↓          ↓           */
var price: Int = 100;   /*
     ↑            ↑
   变量名        变量值   */

```

不过，像Java那样每写一行代码就写一个分号，其实也挺麻烦的。所以为了省事，在Kotlin里面，我们一般会把代码末尾的分号省略，就像这样：

```plain
var price: Int = 100

```

另外，由于Kotlin支持 **类型推导**，大部分情况下，我们的变量类型可以省略不写，就像这样：

```plain
var price = 100 // 默认推导类型为： Int

```

还有一点我们要注意，就是在Kotlin当中，我们应该尽可能避免使用var， **尽可能多地去使用val**。

```plain
var price = 100
price = 101

val i = 0
i = 1 // 编译器报错

```

原因其实很简单：

- val声明的变量，我们叫做 **不可变变量**，它的值在初始化以后就无法再次被修改，它相当于Java里面的final变量。
- var声明的变量，我们叫做 **可变变量**，它对应Java里的普通变量。

## 基础类型

了解了变量类型如何声明之后，我们再来看下Kotlin中的基础类型。

基础类型，包括我们常见的数字类型、布尔类型、字符类型，以及前面这些类型组成的数组。这些类型是我们经常会遇到的概念，因此我们把它统一归为“基础类型”。

### 一切都是对象

在Java里面，基础类型分为原始类型（Primitive Types）和包装类型（Wrapper Type）。比如，整型会有对应的int和Integer，前者是原始类型，后者是包装类型。

```java
int i = 0; // 原始类型
Integer j = 1; // 包装类型

```

Java之所以要这样做，是因为原始类型的开销小、性能高，但它不是对象，无法很好地融入到面向对象的系统中。而包装类型的开销大、性能相对较差，但它是对象，可以很好地发挥面向对象的特性。在 [JDK源码](https://hg.openjdk.java.net/jdk8/jdk8/jdk/file/687fd7c7986d/src/share/classes/java/lang/Integer.java) 当中，我们可以看到Integer作为包装类型，它是有成员变量以及成员方法的，这就是它作为对象的优势。

然而，在Kotlin语言体系当中，是没有原始类型这个概念的。这也就意味着， **在Kotlin里，一切都是对象。**

![](https://static001.geekbang.org/resource/image/yy/3b/yyd95b04616943878351867c4d1e063b.jpg?wh=2000x1077)

实际上，从某种程度上讲，Java的类型系统并不是完全面向对象的，因为它存在原始类型，而原始类型并不属于对象。而Kotlin则不一样，它从语言设计的层面上就规避了这个问题，类型系统则是完全面向对象的。

我们看一段代码，来更直观地感受Kotlin的独特之处：

```plain
val i: Double = 1.toDouble()

```

可以发现，由于在Kotlin中，整型数字“1”被看作是对象了，所以我们可以调用它的成员方法toDouble()，而这样的代码在Java中是无法实现的。

### 空安全

既然Kotlin中的一切都是对象，那么对象就有可能为空。也许你会想到写这样的代码：

```plain
val i: Double = null // 编译器报错

```

可事实上，以上的代码并不能通过Kotlin编译。这是因为Kotlin强制要求开发者 **在定义变量的时候，指定这个变量是否可能为null**。对于可能为null的变量，我们需要在声明的时候，在变量类型后面加一个问号“?”：

```plain
val i: Double = null // 编译器报错
val j: Double? = null // 编译通过

```

并且由于Kotlin对可能为空的变量类型做了强制区分，这就意味着，“可能为空的变量”无法直接赋值给“不可为空的变量”，当然，反向赋值是没有问题的。

```plain
var i: Double = 1.0
var j: Double? = null

i = j  // 编译器报错
j = i  // 编译通过

```

Kotlin这么设计的原因也很简单，如果我们将“可能为空的变量”直接赋值给了“不可为空的变量”，这会跟它自身的定义产生冲突。而如果我们实在有这样的需求，也不难实现，只要做个判断即可：

```plain
var i: Double = 1.0
val j: Double? = null

if (j != null) {
    i = j  // 编译通过
}

```

好，在了解了Kotlin和Java这两种语言的主要区别后，下面就让我们来全面认识下Kotlin的基础类型。

### 数字类型

首先，在数字类型上，Kotlin和Java几乎是一致的，包括它们对数字“字面量”的定义方式。

```plain
val int = 1
val long = 1234567L
val double = 13.14
val float = 13.14F
val hexadecimal = 0xAF
val binary = 0b01010101

```

这里我也来给你具体介绍下：

- 整数默认会被推导为“Int”类型；
- Long类型，我们则需要使用“L”后缀；
- 小数默认会被推导为“Double”，我们不需要使用“D”后缀；
- Float类型，我们需要使用“F”后缀；
- 使用“0x”，来代表十六进制字面量；
- 使用“0b”，来代表二进制字面量。

但是，对于数字类型的转换，Kotlin与Java的转换行为是不一样的。 **Java可以隐式转换数字类型，而Kotlin更推崇显式转换。**

举个简单的例子，在Java和C当中，我们经常直接把int类型赋值给long类型，编译器会自动为我们做类型转换，如下所示：

```java
int i = 100;
long j = i;

```

这段代码按照Java的编程思维方式来看，的确好像是OK的。但是你要注意，虽然Java编译器不会报错，可它仍然可能会带来问题，因为它们本质上不是一个类型，int、long、float、double这些类型之间的互相转换是存在精度问题的。尤其是当这样的代码掺杂在复杂的逻辑中时，在碰到一些边界条件的情况下，即使出现了Bug也不容易排查出来。

所以，同样的代码，在Kotlin当中是行不通的：

```plain
val i = 100
val j: Long = i // 编译器报错

```

在Kotlin里，这样的隐式转换被抛弃了。正确的做法应该是显式调用Int类型的toLong()函数：

```plain
val i = 100
val j: Long = i.toLong() // 编译通过

```

其实，如果我们仔细翻看Kotlin的源代码，会发现更多类似的函数，比如toByte()、toShort()、toInt()、toLong()、toFloat()、toDouble()、toChar()等等。Kotlin这样设计的优势也是显而易见的， **我们代码的可读性更强了，将来也更容易维护了**。

### 布尔类型

然后我们再来了解下Kotlin中布尔类型的变量，它只有两种值，分别是 **true和false**。布尔类型支持一些逻辑操作，比如说：

- “&”代表“与运算”；
- “\|”代表“或运算”；
- “!”代表“非运算”；
- “&&”和“\|\|”分别代表它们对应的“短路逻辑运算”。

```plain
val i = 1
val j = 2
val k = 3

val isTrue: Boolean = i < j && j < k

```

### 字符：Char

Char用于代表单个的字符，比如 `'A'`、 `'B'`、 `'C'`，字符应该用单引号括起来。

```plain
val c: Char = 'A'

```

如果你有Java或C的使用经验，也许会写出这样的代码：

```plain
val c: Char = 'A'
val i: Int = c // 编译器报错

```

这个问题其实跟前面Java的数字类型隐式转换的问题类似，所以针对这种情况，我们应该调用对应的函数来做类型转换。这一点我们一定要牢记在心。

```plain
val c: Char = 'A'
val i: Int = c.toInt() // 编译通过

```

### 字符串：String

字符串（String），顾名思义，就是一连串的字符。和Java一样，Kotlin中的字符串也是不可变的。在大部分情况下，我们会使用双引号来表示字符串的字面量，这一点跟Java也是一样的。

```plain
val s = "Hello Kotlin!"

```

不过与此同时，Kotlin还为我们提供了非常简洁的 **字符串模板**：

```plain
val name = "Kotlin"
print("Hello $name!")
/*            ↑
    直接在字符串中访问变量
*/
// 输出结果：
Hello Kotlin!

```

这样的特性，在Java当中是没有的，这是Kotlin提供的新特性。虽然说这个字符串模板功能，我们用Java也同样可以实现，但它远没有Kotlin这么简洁。在Java当中，我们必须使用两个“+”进行拼接，比如说 `("Hello" + name + "!")`。这样一来，在字符串格式更复杂的情况下，代码就会很臃肿。

当然，如果我们需要在字符串当中引用更加复杂的变量，则需要使用花括号将变量括起来：

```plain
val array = arrayOf("Java", "Kotlin")
print("Hello ${array.get(1)}!")
/*            ↑
      复杂的变量，使用${}
*/
// 输出结果：
Hello Kotlin!

```

另外，Kotlin还新增了一个 **原始字符串**，是用三个引号来表示的。它可以用于存放复杂的多行文本，并且它定义的时候是什么格式，最终打印也会是对应的格式。所以当我们需要复杂文本的时候，就不需要像Java那样写一堆的加号和换行符了。

```plain
val s = """
       当我们的字符串有复杂的格式时
       原始字符串非常的方便
       因为它可以做到所见即所得。 """

print(s)

```

### 数组

最后，我们再来看看Kotlin中数组的一些改变。

在Kotlin当中，我们一般会使用 **arrayOf()** 来创建数组，括号当中可以用于传递数组元素进行初始化，同时，Kotlin编译器也会根据传入的参数进行类型推导。

```plain
val arrayInt = arrayOf(1, 2, 3)
val arrayString = arrayOf("apple", "pear")

```

比如说，针对这里的arrayInt，由于我们赋值的时候传入了整数，所以它的类型会被推导为整型数组；对于arrayString，它的类型会被推导为字符串数组。

而你应该也知道，在Java当中，数组和其他集合的操作是不一样的。举个例子，如果要获取数组的长度，Java中应该使用“array.length”；但如果是获取List的大小，那么Java中则应该使用“list.size”。这主要是因为数组不属于Java集合。

不过，Kotlin在这个问题的处理上并不一样。 **虽然Kotlin的数组仍然不属于集合，但它的一些操作是跟集合统一的。**

```plain
val array = arrayOf("apple", "pear")
println("Size is ${array.size}")
println("First element is ${array[0]}")

// 输出结果：
Size is 2
First element is apple

```

就比如说，以上代码中，我们直接使用array.size就能拿到数组的长度。

## 函数声明

好，了解了Kotlin中变量和基础类型的相关概念之后，我们再来看看它的函数是如何定义的。

在Kotlin当中，函数的声明与Java不太一样，让我们看一段简单的Kotlin代码：

```plain
/*
关键字    函数名          参数类型   返回值类型
 ↓        ↓                ↓       ↓      */
fun helloFunction(name: String): String {
    return "Hello $name !"
}/*   ↑
   花括号内为：函数体
*/

```

可以看到，在这段代码中：

- 使用了 **fun关键字** 来定义函数；
- **函数名称**，使用的是 [驼峰命名法](https://zh.wikipedia.org/zh/%E9%A7%9D%E5%B3%B0%E5%BC%8F%E5%A4%A7%E5%B0%8F%E5%AF%AB)（大部分情况下）；
- **函数参数**，是以(name: String)这样的形式传递的，这代表了参数类型为String类型；
- **返回值类型**，紧跟在参数的后面；
- 最后是 **花括号内的函数体**，它代表了整个函数的逻辑。

另外你可以再注意一个地方，前面代码中的helloFunction函数，它的函数体实际上只有一行代码。那么针对这种情况，我们其实就可以省略函数体的花括号，直接使用“=”来连接，将其变成一种类似变量赋值的函数形式：

```plain
fun helloFunction(name: String): String = "Hello $name !"

```

这种写法，我们称之为 **单一表达式函数**。需要注意的是，在这种情况下，表达式当中的“return”是需要去掉的。

另外，由于Kotlin支持类型推导，我们在使用单一表达式形式的时候，返回值的类型也可以省略：

```plain
fun helloFunction(name: String) = "Hello $name !"

```

看到这里，你一定能体会到Kotlin的魅力。它的语法非常得简洁，并且是符合人类的阅读直觉的，我们读这样的代码，就跟读自然语言一样轻松。

然而，Kotlin的优势不仅仅体现在函数声明上，在函数调用的地方，它也有很多独到之处。

### 函数调用

以我们前面定义的函数为例子，如果我们想要调用它，代码的风格和Java基本一致：

```plain
helloFunction("Kotlin")

```

不过，Kotlin提供了一些新的特性，那就是 **命名参数**。简单理解，就是它允许我们在调用函数的时候传入“形参的名字”。

```plain
helloFunction(name = "Kotlin")

```

让我们看一个更具体的使用场景：

```plain
fun createUser(
    name: String,
    age: Int,
    gender: Int,
    friendCount: Int,
    feedCount: Int,
    likeCount: Long,
    commentCount: Int
) {
    //..
}

```

这是一个包含了很多参数的函数，在Kotlin当中，针对参数较多的函数，我们一般会 **以纵向的方式排列**，这样的代码更符合我们从上到下的阅读习惯，省去从左往右翻的麻烦。

但是，如果我们像Java那样调用createUser，代码就会非常难以阅读：

```plain
createUser("Tom", 30, 1, 78, 2093, 10937, 3285)

```

这里代码中的第一个参数，我们知道肯定是name，但是到了后面那一堆的数字，就会让人迷惑了。这样的代码不仅难懂，同时还不好维护。

但如果我们这样写呢？

```plain
createUser(
    name = "Tom",
    age = 30,
    gender = 1,
    friendCount = 78,
    feedCount = 2093,
    likeCount = 10937,
    commentCount = 3285
)

```

可以看到，在这段代码中，我们把函数的形参加了进来，形参和实参用“=”连接，建立了两者的对应关系。对比前面Java风格的写法，这样的代码可读性更强了。如果将来你想修改likeCount这个参数，也可以轻松做到。这其实就体现出了Kotlin命名参数的 **可读性** 与 **易维护性** 两个优势。

而除了命名参数这个特性，Kotlin还支持 **参数默认值**，这个特性在参数较多的情况下同样有很大的优势：

```plain
fun createUser(
    name: String,
    age: Int,
    gender: Int = 1,
    friendCount: Int = 0,
    feedCount: Int = 0,
    likeCount: Long = 0L,
    commentCount: Int = 0
) {
    //..
}

```

我们可以看到，gender、friendCount、feedCount、likeCount、commentCount这几个参数都被赋予了默认值。这样做的好处就在于，我们在调用的时候可以省很多事情。比如说，下面这段代码就只需要传3个参数，剩余的4个参数没有传，但是Kotlin编译器会自动帮我们填上默认值。

```plain
createUser(
    name = "Tom",
    age = 30,
    commentCount = 3285
)

```

对于无默认值的参数，编译器会强制要求我们在调用处传参；对于有默认值的参数，则可传可不传。Kotlin这样的特性，在一些场景下就可以极大地提升我们的开发效率。

而如果是在Java当中要实现类似的事情，我们就必须手动定义“3个参数的createUser函数”，或者是使用Builder设计模式。

## 流程控制

在Kotlin当中，流程控制主要有if、when、for、 while，这些语句可以控制代码的执行流程。它们也是体现代码逻辑的关键。下面我们就来一一学习下。

### if

if语句，在程序当中主要是用于逻辑判断。Kotlin当中的if与Java当中的基本一致：

```plain
val i = 1
if (i > 0) {
    print("Big")
} else {
    print("Small")
}

输出结果：
Big

```

可以看到，由于i大于0，所以程序会输出“Big”，这很好理解。不过Kotlin的if，并不是程序语句（Statement）那么简单，它还可以作为 **表达式**（Expression）来使用。

```plain
val i = 1
val message = if (i > 0) "Big" else "Small"

print(message)

输出结果：
Big

```

以上的代码其实跟之前的代码差不多，它们做的是同一件事。不同的是，我们把if当作表达式在用，将if判断的结果，赋值给了一个变量。同时，Kotlin编译会根据if表达式的结果自动推导出变量“message”的类型为“String”。这种方式就使得Kotlin的代码更加简洁。

而类似的逻辑，如果要用Java来实现的话，我们就必须先在if外面定义一个变量message，然后分别在两个分支内对message赋值：

```java
int i = 1
String message = ""
if (i > 0) {
    message = "Big"
} else {
    message = "Small"
}

print(message)

```

这样两相对比下，我们会发现Java的实现方式明显丑陋一些： **不仅代码行数更多，逻辑也松散了**。

另外，由于Kotlin当中明确规定了类型分为“可空类型”“不可空类型”，因此，我们会经常遇到可空的变量，并且要判断它们是否为空。我们直接来看个例子：

```plain
fun getLength(text: String?): Int {
  return if (text != null) text.length else 0
}

```

在这个例子当中，我们把if当作表达式，如果text不为空，我们就算出它的长度；如果它为空，长度就取0。

但是，如果你实际使用Kotlin写过代码，你会发现：在Kotlin中，类似这样的判断逻辑出现得非常频繁，如果每次都要写一个完整的if else分支，其实也很麻烦。

为此，Kotlin针对这种情况就提供了一种简写，叫做 **Elvis表达式**。

```plain
fun getLength(text: String?): Int {
  return text?.length ?: 0
}

```

可以看到，通过Elvis表达式，我们就再也不必写“ `if (xxx != null) xxx else xxx`”这样的赋值代码了。它在提高代码可读性的同时，还能提高我们的编码效率。

### when

when语句，在程序当中主要也是用于逻辑判断的。当我们的代码逻辑只有两个分支的时候，我们一般会使用if/else，而在大于两个逻辑分支的情况下，我们使用when。

```plain
val i: Int = 1

when(i) {
    1 -> print("一")
    2 -> print("二")
    else -> print("i 不是一也不是二")
}

输出结果：
一

```

when语句有点像Java里的switch case语句，不过Kotlin的when更加强大，它同时也可以 **作为表达式，为变量赋值**，如下所示：

```plain
val i: Int = 1

val message = when(i) {
    1 -> "一"
    2 -> "二"
    else -> "i 不是一也不是二" // 如果去掉这行，会报错
}

print(message)

```

另外，与switch不一样的是，when表达式要求它里面的逻辑分支必须是完整的。举个例子，以上的代码，如果去掉else分支，编译器将报错，原因是：i的值不仅仅只有1和2，这两个分支并没有覆盖所有的情况，所以会报错。

### 循环迭代：while与for

首先while循环，我们一般是用于重复执行某些代码，它在使用上和Java也没有什么区别：

```plain
var i = 0
while (i <= 2) {
    println(i)
    i++
}

var j = 0
do {
    println(j)
    j++
} while (j <= 2)

输出结果：
0
1
2
0
1
2

```

但是对于for语句，Kotlin和Java的用法就明显不一样了。

在Java当中，for也会经常被用于循环，经常被用来替代while。不过， **Kotlin的for语句更多的是用于“迭代”。** 比如，以下代码就代表了迭代array这个数组里的所有元素，程序会依次打印出：“1、2、3”。

```plain
val array = arrayOf(1, 2, 3)
for (i in array) {
    println(i)
}

```

而除了迭代数组和集合以外，Kotlin还支持迭代一个“区间”。

首先，要定义一个区间，我们可以使用“ `..`”来连接数值区间的两端，比如“ `1..3`”就代表从1到3的闭区间，左闭右闭：

```plain
val oneToThree = 1..3 // 代表 [1, 3]

```

接着，我们就可以使用for语句，来对这个闭区间范围进行迭代：

```plain
for (i in oneToThree) {
    println(i)
}

输出结果：
1
2
3

```

甚至，我们还可以 **逆序迭代** 一个区间，比如：

```plain
for (i in 6 downTo 0 step 2) {
    println(i)
}

输出结果：
6
4
2
0

```

以上代码的含义就是逆序迭代一个区间，从6到0，每次迭代的步长是2，这意味着6迭代过后，到4、2，最后到0。 **需要特别注意的是**，逆序区间我们不能使用“ `6..0`”来定义，如果用这样的方式来定义的话，代码将无法正常运行。

好了，那么到目前为止，Kotlin的变量、基础类型、函数、流程控制，我们就都已经介绍完了。掌握好这些知识点，我们就已经可以写出简单的程序了。当然，我们的Kotlin学习之路才刚刚开始，在下节课，我会带你来学习Kotlin面向对象相关的知识点。

## 小结

学完了这节课，现在我们知道虽然Kotlin和Java的语法很像，但在一些细节之处，Kotlin总会有一些新的东西。如果你仔细琢磨这些不同点，你会发现它正是大部分程序员所需要的。举个例子，作为开发者，我们都讨厌写冗余的代码，喜欢简洁易懂的代码。那么在今天学完了基础语法之后，我们可以来看看Kotlin在这方面都做了哪些改进：

- 支持类型推导；
- 代码末尾不需要分号；
- 字符串模板；
- 原始字符串，支持复杂文本格式；
- 单一表达式函数，简洁且符合直觉；
- 函数参数支持默认值，替代Builder模式的同时，可读性还很强；
- if和when可以作为表达式。

同时，JetBrains也非常清楚开发者在什么情况下容易出错，所以，它在语言层面也做了很多改进：

- 强制区分“可为空变量类型”和“不可为空变量类型”，规避空指针异常；
- 推崇不可变性（val），对于没有修改需求的变量，IDE会智能提示开发者将“var”改为“val”；
- 基础类型不支持隐式类型转换，这能避免很多隐藏的问题；
- 数组访问行为与集合统一，不会出现array.length、list.size这种恼人的情况；
- 函数调用支持命名参数，提高可读性，在后续维护代码的时候不易出错；
- when表达式，强制要求逻辑分支完整，让你写出来的逻辑永远不会有漏洞。

![图片](https://static001.geekbang.org/resource/image/32/67/32ab3d37cd7f9650f4cba17736305c67.jpg?wh=1920x1983)

这些都是Kotlin的 **闪光点**，也是它最珍贵的地方。

这一切，都得益于Kotlin的发明者JetBrains。作为最负盛名的IDE创造者，JetBrains能深刻捕捉到开发者的需求。它知道开发者喜欢什么、讨厌什么，它甚至知道开发者容易犯什么样的错误，从而在语言设计的层面规避错误。站在这个角度看，JetBrains能够创造出炙手可热的Kotlin语言，就一点都不奇怪了。

以上这么多的“闪光点”还仅仅只是局限于我们这节课的内容，如果放眼全局，这样的例子更是数不胜数。 **Kotlin对比Java的提升，如果独立去看其中的某一个点，都不足以让一个开发者心动。不过，一旦这样的改善积少成多，Kotlin的优势就会显得尤为明显。** 这也是很多程序员表示“Kotlin用过了就回不去”的原因。

## 思考题

虽然Kotlin在语法层面摒弃了“原始类型”，但有时候为了性能考虑，我们确实需要用“原始类型”。这时候我们应该怎么办？

欢迎在评论区分享你的思路，这个问题我会在第三节课给出答案，我们下节课再见。