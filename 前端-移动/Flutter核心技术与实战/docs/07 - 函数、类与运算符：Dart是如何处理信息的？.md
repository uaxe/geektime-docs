你好，我是陈航。

在上一篇文章中，我通过一个基本hello word的示例，带你体验了Dart的基础语法与类型变量，并与其他编程语言的特性进行对比，希望可以帮助你快速建立起对Dart的初步印象。

其实，编程语言虽然千差万别，但归根结底，它们的设计思想无非就是回答两个问题：

- 如何表示信息；
- 如何处理信息。

在上一篇文章中，我们已经解决了Dart如何表示信息的问题，今天这篇文章我就着重和你分享它是如何处理信息的。

作为一门真正面向对象的编程语言，Dart将处理信息的过程抽象为了对象，以结构化的方式将功能分解，而函数、类与运算符就是抽象中最重要的手段。

接下来，我就从函数、类与运算符的角度，来进一步和你讲述Dart面向对象设计的基本思路。

## 函数

函数是一段用来独立地完成某个功能的代码。我在上一篇文章中和你提到，在Dart中，所有类型都是对象类型，函数也是对象，它的类型叫作Function。这意味着函数也可以被定义为变量，甚至可以被定义为参数传递给另一个函数。

在下面这段代码示例中，我定义了一个判断整数是否为0的isZero函数，并把它传递了给另一个printInfo函数，完成格式化打印出判断结果的功能。

```
bool isZero(int number) { //判断整数是否为0
  return number == 0;
}

void printInfo(int number,Function check) { //用check函数来判断整数是否为0
  print("$number is Zero: ${check(number)}");
}

Function f = isZero;
int x = 10;
int y = 0;
printInfo(x,f);  // 输出 10 is Zero: false
printInfo(y,f);  // 输出 0 is Zero: true

```

如果函数体只有一行表达式，就比如上面示例中的isZero和printInfo函数，我们还可以像JavaScript语言那样用箭头函数来简化这个函数：

```
bool isZero(int number) => number == 0;

void printInfo(int number,Function check) => print("$number is Zero: ${check(number)}");

```

有时，一个函数中可能需要传递多个参数。那么，如何让这类函数的参数声明变得更加优雅、可维护，同时降低调用者的使用成本呢？

C++与Java的做法是，提供函数的重载，即提供同名但参数不同的函数。但 **Dart认为重载会导致混乱，因此从设计之初就不支持重载，而是提供了可选命名参数和可选参数**。

具体方式是，在声明函数时：

- 给参数增加{}，以paramName: value的方式指定调用参数，也就是可选命名参数；
- 给参数增加\[\]，则意味着这些参数是可以忽略的，也就是可选参数。

在使用这两种方式定义函数时，我们还可以在参数未传递时设置默认值。我以一个只有两个参数的简单函数为例，来和你说明这两种方式的具体用法：

```
//要达到可选命名参数的用法，那就在定义函数的时候给参数加上 {}
void enable1Flags({bool bold, bool hidden}) => print("$bold , $hidden");

//定义可选命名参数时增加默认值
void enable2Flags({bool bold = true, bool hidden = false}) => print("$bold ,$hidden");

//可忽略的参数在函数定义时用[]符号指定
void enable3Flags(bool bold, [bool hidden]) => print("$bold ,$hidden");

//定义可忽略参数时增加默认值
void enable4Flags(bool bold, [bool hidden = false]) => print("$bold ,$hidden");

//可选命名参数函数调用
enable1Flags(bold: true, hidden: false); //true, false
enable1Flags(bold: true); //true, null
enable2Flags(bold: false); //false, false

//可忽略参数函数调用
enable3Flags(true, false); //true, false
enable3Flags(true,); //true, null
enable4Flags(true); //true, false
enable4Flags(true,true); // true, true

```

**这里我要和你强调的是，在Flutter中会大量用到可选命名参数的方式，你一定要记住它的用法。**

## 类

类是特定类型的数据和方法的集合，也是创建对象的模板。与其他语言一样，Dart为类概念提供了内置支持。

### 类的定义及初始化

Dart是面向对象的语言，每个对象都是一个类的实例，都继承自顶层类型Object。在Dart中，实例变量与实例方法、类变量与类方法的声明与Java类似，我就不再过多展开了。

值得一提的是，Dart中并没有public、protected、private这些关键字，我们只要在声明变量与方法时，在前面加上“\_”即可作为private方法使用。如果不加“\_”，则默认为public。不过， **“\_”的限制范围并不是类访问级别的，而是库访问级别**。

接下来，我们以一个具体的案例看看 **Dart是如何定义和使用类的。**

我在Point类中，定义了两个成员变量x和y，通过构造函数语法糖进行初始化，成员函数printInfo的作用是打印它们的信息；而类变量factor，则在声明时就已经赋好了默认值0，类函数printZValue会打印出它的信息。

```
class Point {
  num x, y;
  static num factor = 0;
  //语法糖，等同于在函数体内：this.x = x;this.y = y;
  Point(this.x,this.y);
  void printInfo() => print('($x, $y)');
  static void printZValue() => print('$factor');
}

var p = new Point(100,200); // new 关键字可以省略
p.printInfo();  // 输出(100, 200);
Point.factor = 10;
Point.printZValue(); // 输出10

```

有时候类的实例化需要根据参数提供多种初始化方式。除了可选命名参数和可选参数之外，Dart还提供了 **命名构造函数** 的方式，使得类的实例化过程语义更清晰。

此外， **与C++类似，Dart支持初始化列表**。在构造函数的函数体真正执行之前，你还有机会给实例变量赋值，甚至重定向至另一个构造函数。

如下面实例所示，Point类中有两个构造函数Point.bottom与Point，其中：Point.bottom将其成员变量的初始化重定向到了Point中，而Point则在初始化列表中为z赋上了默认值0。

```
class Point {
  num x, y, z;
  Point(this.x, this.y) : z = 0; // 初始化变量z
  Point.bottom(num x) : this(x, 0); // 重定向构造函数
  void printInfo() => print('($x,$y,$z)');
}

var p = Point.bottom(100);
p.printInfo(); // 输出(100,0,0)

```

### 复用

在面向对象的编程语言中，将其他类的变量与方法纳入本类中进行复用的方式一般有两种： **继承父类和接口实现**。当然，在Dart也不例外。

在Dart中，你可以对同一个父类进行继承或接口实现：

- 继承父类意味着，子类由父类派生，会自动获取父类的成员变量和方法实现，子类可以根据需要覆写构造函数及父类方法；
- 接口实现则意味着，子类获取到的仅仅是接口的成员变量符号和方法符号，需要重新实现成员变量，以及方法的声明和初始化，否则编译器会报错。

接下来，我以一个例子和你说明 **在Dart中继承和接口的差别**。

Vector通过继承Point的方式增加了成员变量，并覆写了printInfo的实现；而Coordinate，则通过接口实现的方式，覆写了Point的变量定义及函数实现：

```
class Point {
  num x = 0, y = 0;
  void printInfo() => print('($x,$y)');
}

//Vector继承自Point
class Vector extends Point{
  num z = 0;
  @override
  void printInfo() => print('($x,$y,$z)'); //覆写了printInfo实现
}

//Coordinate是对Point的接口实现
class Coordinate implements Point {
  num x = 0, y = 0; //成员变量需要重新声明
  void printInfo() => print('($x,$y)'); //成员函数需要重新声明实现
}

var xxx = Vector();
xxx
  ..x = 1
  ..y = 2
  ..z = 3; //级联运算符，等同于xxx.x=1; xxx.y=2;xxx.z=3;
xxx.printInfo(); //输出(1,2,3)

var yyy = Coordinate();
yyy
  ..x = 1
  ..y = 2; //级联运算符，等同于yyy.x=1; yyy.y=2;
yyy.printInfo(); //输出(1,2)
print (yyy is Point); //true
print(yyy is Coordinate); //true

```

可以看出，子类Coordinate采用接口实现的方式，仅仅是获取到了父类Point的一个“空壳子”，只能从语义层面当成接口Point来用，但并不能复用Point的原有实现。那么， **我们是否能够找到方法去复用Point的对应方法实现呢？**

也许你很快就想到了，我可以让Coordinate继承Point，来复用其对应的方法。但，如果Coordinate还有其他的父类，我们又该如何处理呢？

其实， **除了继承和接口实现之外，Dart还提供了另一种机制来实现类的复用，即“混入”（Mixin）**。混入鼓励代码重用，可以被视为具有实现方法的接口。这样一来，不仅可以解决Dart缺少对多重继承的支持问题，还能够避免由于多重继承可能导致的歧义（菱形问题）。

> 备注：继承歧义，也叫菱形问题，是支持多继承的编程语言中一个相当棘手的问题。当B类和C类继承自A类，而D类继承自B类和C类时会产生歧义。如果A中有一个方法在B和C中已经覆写，而D没有覆写它，那么D继承的方法的版本是B类，还是C类的呢？

**要使用混入，只需要with关键字即可。** 我们来试着改造Coordinate的实现，把类中的变量声明和函数实现全部删掉：

```
class Coordinate with Point {
}

var yyy = Coordinate();
print (yyy is Point); //true
print(yyy is Coordinate); //true

```

可以看到，通过混入，一个类里可以以非继承的方式使用其他类中的变量与方法，效果正如你想象的那样。

## 运算符

Dart和绝大部分编程语言的运算符一样，所以你可以用熟悉的方式去执行程序代码运算。不过， **Dart多了几个额外的运算符，用于简化处理变量实例缺失（即null）的情况**。

- **?.** 运算符：假设Point类有printInfo()方法，p是Point的一个可能为null的实例。那么，p调用成员方法的安全代码，可以简化为p?.printInfo() ，表示p为null的时候跳过，避免抛出异常。
- **??=** 运算符：如果a为null，则给a赋值value，否则跳过。这种用默认值兜底的赋值语句在Dart中我们可以用a ??= value表示。
- **??** 运算符：如果a不为null，返回a的值，否则返回b。在Java或者C++中，我们需要通过三元表达式(a != null)? a : b来实现这种情况。而在Dart中，这类代码可以简化为a ?? b。

**在Dart中，一切都是对象，就连运算符也是对象成员函数的一部分。**

对于系统的运算符，一般情况下只支持基本数据类型和标准库中提供的类型。而对于用户自定义的类，如果想支持基本操作，比如比较大小、相加相减等，则需要用户自己来定义关于这个运算符的具体实现。

**Dart提供了类似C++的运算符覆写机制**，使得我们不仅可以覆写方法，还可以覆写或者自定义运算符。

接下来，我们一起看一个Vector类中自定义“+”运算符和覆写"=="运算符的例子：

```
class Vector {
  num x, y;
  Vector(this.x, this.y);
  // 自定义相加运算符，实现向量相加
  Vector operator +(Vector v) =>  Vector(x + v.x, y + v.y);
  // 覆写相等运算符，判断向量相等
  bool operator == (dynamic v) => x == v.x && y == v.y;
}

final x = Vector(3, 3);
final y = Vector(2, 2);
final z = Vector(1, 1);
print(x == (y + z)); //  输出true

```

operator是Dart的关键字，与运算符一起使用，表示一个类成员运算符函数。在理解时，我们应该把operator和运算符作为整体，看作是一个成员函数名。

## 总结

函数、类与运算符是Dart处理信息的抽象手段。从今天的学习中你可以发现，Dart面向对象的设计吸纳了其他编程语言的优点，表达和处理信息的方式既简单又简洁，但又不失强大。

通过这两篇文章的内容，相信你已经了解了Dart的基本设计思路，熟悉了在Flutter开发中常用的语法特性，也已经具备了快速上手实践的能力。

接下来，我们简单回顾一下今天的内容，以便加深记忆与理解。

首先，我们认识了函数。函数也是对象，可以被定义为变量，或者参数。Dart不支持函数重载，但提供了可选命名参数和可选参数的方式，从而解决了函数声明时需要传递多个参数的可维护性。

然后，我带你学习了类。类提供了数据和函数的抽象复用能力，可以通过继承（父类继承，接口实现）和非继承（Mixin）方式实现复用。在类的内部，关于成员变量，Dart提供了包括命名构造函数和初始化列表在内的两种初始化方式。

最后，需要注意的是，运算符也是对象成员函数的一部分，可以覆写或者自定义。

## 思考题

最后，请你思考以下两个问题。

1. 你是怎样理解父类继承，接口实现和混入的？我们应该在什么场景下使用它们？
2. 在父类继承的场景中，父类子类之间的构造函数执行顺序是怎样的？如果父类有多个构造函数，子类也有多个构造函数，如何从代码层面确保父类子类之间构造函数的正确调用？

```
class Point {
  num x, y;
  Point() : this.make(0,0);
  Point.left(x) : this.make(x,0);
  Point.right(y) : this.make(0,y);
  Point.make(this.x, this.y);
  void printInfo() => print('($x,$y)');
}

class Vector extends Point{
  num z = 0;
/*5个构造函数
  Vector
  Vector.left;
  Vector.middle
  Vector.right
  Vector.make
*/
  @override
  void printInfo() => print('($x,$y,$z)'); //覆写了printInfo实现
}

```

欢迎将你的答案留言告诉我，我们一起讨论。感谢你的收听，也欢迎你把这篇文章分享给更多的朋友一起阅读。