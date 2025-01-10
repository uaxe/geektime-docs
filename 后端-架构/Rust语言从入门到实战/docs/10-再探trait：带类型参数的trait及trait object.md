你好，我是Mike，今天我们继续学习trait相关知识。

回顾一下我们上一节课中类型参数出现的地方。

- 用 trait 对 Ｔ 作类型空间的约束，比如 `T: TraitA`。
- blanket implementation 时的 T，比如 `impl<T: TraitB> TraitA for T {}`。
- 函数里的 T 参数，比如 `fn doit<T>(a: T) {}`。

你要注意区分不同位置的 T。它的基础意义都是类型参数，但是放在不同的位置其侧重的意义有所不同。

- `T: TraitA` 里的T表示类型参数，强调“参数”，使用TraitA来削减它的类型空间。
- `impl<T: TraitB> TraitA for T {}` 末尾的T更强调类型参数的“类型”部分，为某些类型实现 TraitA。
- `doit<T>(a: T) {}` 中第二个T表示某种类型，更强调类型参数的“类型”部分。

这节课我们要讲的是另外一个东西，它里面也带T参数。我们一起来看一下，它与之前这几种形式有什么不同。

## trait上带类型参数

trait上也是可以带类型参数的，形式像下面这样：

```plain
trait TraitA<T> {}

```

表示这个trait里面的函数或方法，可能会用到这个类型参数。在定义trait的时候，还没确定这个类型参数的具体类型。要等到impl甚至使用类型方法的时候，才会具体化这个T的具体类型。

注意，这个时候 `TraitA<T>` 是一个整体，表示一个trait。比如 `TraitA<u8>` 和 `TraitA<u32>` 就是两个不同的trait，这里单独把TraitA拿出来说是没有意义的。

实现时需要在impl后面先定义类型参数，比如：

```plain
impl<T> TraitA<T> for Atype {}

```

当然也可以在对类型实现时，将T参数具体化，比如：

```plain
impl TraitA<u8> for Atype {}

```

而如果被实现的类型上自身也带类型参数，那么情况会更复杂。

```plain
trait TraitA<T> {}
struct Atype<U> {
    a: U,
}
impl<T, U> TraitA<T> for Atype<U> {}

```

这些类型参数都是可以在impl时被约束的，像下面这样：

```plain
use std::fmt::Debug;

trait TraitA<T> {}
struct Atype<U> {
    a: U,
}
impl<T, U> TraitA<T> for Atype<U>
where
    T: Debug,      // 在 impl 时添加了约束
    U: PartialEq,  // 在 impl 时添加了约束
{}

```

注：以上代码都是可以放到playground中编译通过的。

### impl 示例

下面我们通过一个具体的实例体会一下带类型参数的trait的威力。

我们现在要实现一个模型。

1. 平面上的一个点与平面上的另一个点相加，形成一个新的点。算法是两个点的x分量和y分量分别相加。
2. 平面上的一个点加一个整数i32，形成一个新的点。算法是分别在x分量和y分量上面加这个i32参数。

本示例借鉴了： [https://github.com/pretzelhammer/rust-blog/blob/master/posts/tour-of-rusts-standard-library-traits.md#generic-types-vs-associated-types](https://github.com/pretzelhammer/rust-blog/blob/master/posts/tour-of-rusts-standard-library-traits.md#generic-types-vs-associated-types)

代码如下：

```plain
// 定义一个带类型参数的trait
trait Add<T> {
    type Output;
    fn add(self, rhs: T) -> Self::Output;
}

struct Point {
    x: i32,
    y: i32,
}

// 为 Point 实现 Add<Point> 这个 trait
impl Add<Point> for Point {
    type Output = Self;
    fn add(self, rhs: Point) -> Self::Output {
        Point {
            x: self.x + rhs.x,
            y: self.y + rhs.y,
        }
    }
}

// 为 Point 实现 Add<i32> 这个 trait
impl Add<i32> for Point {
    type Output = Self;
    fn add(self, rhs: i32) -> Self::Output {
        Point {
            x: self.x + rhs,
            y: self.y + rhs,
        }
    }
}

fn main() {
    let p1 = Point { x: 1, y: 1 };
    let p2 = Point { x: 2, y: 2 };
    let p3 = p1.add(p2);  // 两个Point实例相加
    assert_eq!(p3.x, 3);
    assert_eq!(p3.y, 3);

    let p1 = Point { x: 1, y: 1 };
    let delta = 2;
    let p3 = p1.add(delta);   // 一个Point实例加一个i32
    assert_eq!(p3.x, 3);
    assert_eq!(p3.y, 3);
}

```

我们详细解释一下这个示例。 `Add<T>` 这个trait，带一个类型参数T，还带一个关联类型 Output。

对Point类型，我们实现了两个trait： `Add<Point>` 和 `Add<i32>`。注意这已经是两个不同的trait了，所以能对同一个类型实现。前面我们反复强调过，同一个trait只能对一个类型实现一次。

根据需求，运算后的类型也是Point，所以看到两个trait中的关联类型都是 Self。请注意两个trait中实现的不同算法。

通过这种形式，我们在同一个类型上实现了同名方法（add方法）参数类型的多种形态。在这里看起来就是，Point实例的add方法既可以接收Point参数，又可以接收i32参数，Rustc小助手可以根据不同的参数类型自动找到对应的方法调用。在Java、C++这些语言中，有语言层面的函数重载特性来支持这种功能，Rust中自身并不直接支持函数重载特性，但是它用trait就轻松实现了同样的效果，这是一种全新的思路。

### trait 类型参数的默认实现

定义带类型参数的trait的时候，可以为类型参数指定一个默认类型，比如 `trait TraitA<T = u64> {}`。这样使用时， `impl TraitA for SomeType {}` 就等价于 `impl TraitA<u64> for SomeType {}`。

我们来看一个完整的例子。

```plain
// Self可以用在默认类型位置上
trait TraitA<T = Self> {
    fn func(t: T) {}
}

// 这个默认类型为i32
trait TraitB<T = i32> {
    fn func2(t: T) {}
}

struct SomeType;

// 这里省略了类型参数，所以这里的T为Self
// 进而T就是SomeType本身
impl TraitA for SomeType {
    fn func(t: SomeType) {}
}
// 这里省略了类型参数，使用默认类型i32
impl TraitB for SomeType {
    fn func2(t: i32) {}
}
// 这里不省略类型参数，明确指定类型参数为String
impl TraitA<String> for SomeType {
    fn func(t: String) {}
}
// 这里不省略类型参数，明确指定类型参数为String
impl TraitB<String> for SomeType {
    fn func2(t: String) {}
}

```

默认参数给表达上带来了一定程度的简洁，但是增加了初学者识别和理解上的困难。

你还记得上一节课讲关联类型时我们提到过在使用约束时可以具化关联类型。那里也是用的＝号。比如：

```plain
trait TraitA {
    type Item;
}
// 这里，定义结构体类型时，用到了TraitA作为约束
struct Foo<T: TraitA<Item=String>> {
    x: T
}

```

初看这里容易混淆。区别在于， **关联类型的具化是在应用约束时，类型参数的默认类型指定是在定义trait时**，通过trait出现的场景可以区分它们。

### trait中的类型参数与关联类型的区别

现在你可能会有些疑惑：trait上的类型参数和关联类型都具有延迟具化的特点，那么它们的区别是什么呢？为什么要设计两种不同的机制呢？

首先要明确的一点是，Rust本身也在持续演化过程中。有些特性先出现，有些特性是后出现的。最后演化出功能相似但是不完全一样的特性是完全有可能的。

具体到这两者来说，它们主要有两点不同。

1. 类型参数可以在impl 类型的时候具化，也可以延迟到使用的时候具化。而关联类型在被impl时就必须具化。
2. 由于类型参数和trait名一起组成了完整的trait名字，不同的具化类型会构成不同的trait，所以看起来同一个定义可以在目标类型上实现“多次”。而关联类型没有这个作用。

下面我们分别举例说明。

对于第一点，请看下面的示例：

```plain
use std::fmt::Debug;

trait TraitA<T>
where
    T: Debug,  // 定义TraitA<T>的时候，对T作了约束
{
    fn play(&self, _t: T) {}
}
struct Atype;

impl<T> TraitA<T> for Atype
where
    T: Debug + PartialEq,  // 将TraitA<T>实现到类型Atype上时，加强了约束
{}

fn main() {
    let a = Atype;
    a.play(10u32);  // 在使用时，通过实例方法传入的参数类型具化T
}

```

这个示例展示了几个要点。

1. 定义带类型参数的trait时可以用where表达，并提供约束。
2. impl trait时可以对类型参数加强约束，对应例子中的 Debug + PartialEq。
3. impl trait时可以不具化类型参数。
4. 可以在使用方法时具化类型参数。例子里的 `a.play(10u32)`，把T具象化成了u32。

当然，在impl的时候也可以指定成u32类型，所以下面的代码也可以。

```plain
use std::fmt::Debug;

trait TraitA<T>
where
    T: Debug,
{
    fn play(&self, _t: T) {}
}
struct Atype;

impl TraitA<u32> for Atype {} // 这里具化成了 TraitA<u32>

fn main() {
    let a = Atype;
    a.play(10u32);
}

```

但是这样就没前面那么灵活了，比如 `a.play(10u64)` 就不行了。

对应的，对关联类型来说，如果你在impl时不对其具化，就无法编译通过。所以对于第二点，我也给出一个例子来解释。我们把前面对Point类型实现Add的模型尝试用关联类型实现一遍。

```plain
trait Add {
    type ToAdd;    // 多定义一个关联类型
    type Output;
    fn add(self, rhs: Self::ToAdd) -> Self::Output;
}

struct Point {
    x: i32,
    y: i32,
}

impl Add for Point {
    type ToAdd = Point;
    type Output = Point;
    fn add(self, rhs: Point) -> Point {
        Point {
            x: self.x + rhs.x,
            y: self.y + rhs.y,
        }
    }
}

impl Add for Point { // 这里重复impl了同一个trait，无法编译通过
    type ToAdd = i32;
    type Output = Point;
    fn add(self, rhs: i32) -> Point {
        Point {
            x: self.x + rhs,
            y: self.y + rhs,
        }
    }
}

fn main() {
    let p1 = Point { x: 1, y: 1 };
    let p2 = Point { x: 2, y: 2 };
    let p3 = p1.add(p2);
    assert_eq!(p3.x, 3);
    assert_eq!(p3.y, 3);

    let p1 = Point { x: 1, y: 1 };
    let delta = 2;
    let p3 = p1.add(delta); // 这句是错的
    assert_eq!(p3.x, 3);
    assert_eq!(p3.y, 3);

```

编译器会抱怨：

```plain
error[E0119]: conflicting implementations of trait `Add` for type `Point`:
  --> src/main.rs:23:1
   |
12 | impl Add for Point {
   | ------------------ first implementation here
...
23 | impl Add for Point {
   | ^^^^^^^^^^^^^^^^^^ conflicting implementation for `Point`

```

提示说，对Point类型实现了多次Add，导致冲突。编译不通过。所以这个模型仅用关联类型来实现，是写不出来的。

这么看起来，好像带类型参数的trait功能更强大，那用这个不就够了？但关联类型也有它的优点，比如关联类型没有类型参数，不存在多引入了一个参数的问题，而类型参数是具有传染性的，特别是在一个调用层次很深的系统中，增删一个类型参数可能会导致整个项目文件到处都需要改，非常头疼。

而关联类型没有这个问题。在一些场合下，关联类型正好是减少类型参数数量的一种方法。更不要说，有时模型比较简单，不需要多态特性，这时用关联类型就更简洁，代码可读性更好。

## trait object

下面我们开始讲trait object。

我们从一个函数要返回不同的类型说起。比如一个常见的需求，要在一个Rust函数中返回可能的多种类型，应该怎么写？

如果我们写成返回固定类型的函数签名，那么它就只能返回那个类型。比如：

```plain
struct Atype;
struct Btype;
struct Ctype;
fn doit() -> Atype {
    let a = Atype;
    a
}

```

你想到的第一个办法可能是利用enum。

```plain
struct Atype;
struct Btype;
struct Ctype;

enum TotalType {
  A(Atype),    // 用变体把目标类型包起来
  B(Btype),
  C(Ctype),
}

fn doit(i: u32) -> TotalType {  // 返回枚举类型
  if i == 0 {
    let a = Atype;
    TotalType::A(a)    // 在这个分支中返回变体A
  } else if i == 1 {
    let b = Btype;
    TotalType::B(b)    // 在这个分支中返回变体B
  } else {
    let c = Ctype;
    TotalType::C(c)    // 在这个分支中返回变体C
  }
}

```

**enum 常用于聚合类型**。这些类型之间可以没有任何关系，用enum可以 **无脑+强行** 把它们揉在一起。enum聚合类型是编码时已知的类型，也就是说在聚合前，需要知道待聚合类型的边界，一旦定义完成，之后运行时就不能改动了，它是 **封闭类型集**。

第二种办法是利用类型参数，我们试着引入一个类型参数，改写一下。

```plain
struct Atype;
struct Btype;
struct Ctype;
fn doit<T>() -> T {
  let a = Atype;
  a
}

```

很明显，这种代码无法通过编译。提示：

```plain
error[E0308]: mismatched types
 --> src/lib.rs:6:3
  |
4 | fn doit<T>() -> T {
  |         -       - expected `T` because of return type
  |         |
  |         this type parameter
5 |   let a = Atype;
6 |   a
  |   ^ expected type parameter `T`, found `Atype`
  |
  = note: expected type parameter `T`
                     found struct `Atype`

```

因为这里这个类型参数T是在这个函数调用时指定，而不是在这个函数定义时指定的。所以针对我们的需求，你没法在这里直接返回一个具体的类型代入T。只能尝试用T来返回，于是我们改出第二个版本。

```plain
struct Atype;
struct Btype;
struct Ctype;

impl Atype {
    fn new() -> Atype {
        Atype
    }
}

impl Btype {
    fn new() -> Btype {
        Btype
    }
}

impl Ctype {
    fn new() -> Ctype {
        Ctype
    }
}

fn doit<T>() -> T {
  T::new()
}

```

编译还是报错。

```plain
error[E0599]: no function or associated item named `new` found for type parameter `T` in the current scope
  --> src/main.rs:24:6
   |
23 | fn doit<T>() -> T {
   |         - function or associated item `new` not found for this type parameter
24 |   T::new()
   |      ^^^ function or associated item not found in `T`

```

也就是说，Rustc小助手并不知道我们定义这个类型参数T里面有new这个关联函数。联想到我们前面学过的，可以用trait来定义这个协议，让Rust认识它。

第三个版本：

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {
    fn new() -> Self;    // TraitA中定义了new()函数
}

impl TraitA for Atype {
    fn new() -> Atype {
        Atype
    }
}

impl TraitA for Btype {
    fn new() -> Btype {
        Btype
    }
}

impl TraitA for Ctype {
    fn new() -> Ctype {
        Ctype
    }
}

fn doit<T: TraitA>() -> T {
  T::new()
}

fn main() {
    let a: Atype = doit::<Atype>();
    let b: Btype = doit::<Btype>();
    let c: Ctype = doit::<Ctype>();
}

```

这个版本顺利通过编译。在这个示例中，我们认识到了引入trait的必要性，就是让Rustc小助手知道我们在协议层面有一个new()函数，一旦类型参数被trait约束后，它就可以去trait中寻找协议定义的函数和方法。

为了解决上面那个问题，我们真的是费了不少力气。实际上，Rust提供了更优雅的方案来解决这个需求。Rust利用trait提供了一种特殊语法 impl trait，你可以看一下示例。

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit() -> impl TraitA {  // 注意这一行的函数返回类型
  let a = Atype;
  a
  // 或
  // let b = Btype;
  // b
  // 或
  // let c = Ctype;
  // c
}

```

可以看到，这种表达非常简洁，同一个函数签名可以返回多种不同的类型，并且在函数定义时就可以返回具体的类型的实例。更重要的是消除了类型参数T。

上述代码已经很有用了，但是还是不够灵活，比如我们要用if逻辑选择不同的分支返回不同的类型，就会遇到问题。

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit(i: u32) -> impl TraitA {
  if i == 0 {
    let a = Atype;
    a                    // 在这个分支中返回类型a
  } else if i == 1 {
    let b = Btype;
    b                    // 在这个分支中返回类型b
  } else {
    let c = Ctype;
    c                    // 在这个分支中返回类型c
  }
}

```

提示：

```plain
error[E0308]: `if` and `else` have incompatible types
  --> src/lib.rs:22:5
   |
17 |     } else if i == 1 {
   |  __________-
18 | |     let b = Btype;
19 | |     b
   | |     - expected because of this
20 | |   } else {
21 | |     let c = Ctype;
22 | |     c
   | |     ^ expected `Btype`, found `Ctype`
23 | |   }
   | |___- `if` and `else` have incompatible types

```

if else 要求返回同一种类型，Rust检查确实严格。不过我们可以通过加return跳过 if else 的限制。

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit(i: u32) -> impl TraitA {
  if i == 0 {
    let a = Atype;
    return a;          // 这里用return语句直接从函数返回
  } else if i == 1 {
    let b = Btype;
    return b;
  } else {
    let c = Ctype;
    return c;
  }
}

```

但是还是报错。

```plain
error[E0308]: mismatched types
  --> src/lib.rs:19:12
   |
13 | fn doit(i: u32) -> impl TraitA {  // 这一行
   |                    ----------- expected `Atype` because of return type
...
19 |     return b
   |            ^ expected `Atype`, found `Btype`

```

它说期望Atype，却得到了Btype。这个报错其实有点奇怪，它们不是都满足 impl TraitA 吗？

原来问题在于，impl TraitA 作为函数返回值这种语法，其实也只是 **指代某一种类型** 而已，而这种类型是在函数体中由返回值的类型来自动推导出来的。例子中，Rustc小助手遇到Atype这个分支时，就已经确定了函数返回类型为Atype，因此当它分析到后面的Btype分支时，就发现类型不匹配了。问题就在这里。你可以将条件分支顺序换一下，看一下报错的提示，加深印象。

那我们应该怎么处理这种问题呢？

好在，Rust还给我们提供了进一步的措施： **trait object**。形式上，就是在trait名前加 dyn 关键字修饰，在这个例子里就是 dyn TraitA。 **dyn TraitName 本身就是一种类型**，它和 TraitName 这个 trait 相关，但是它们不同，dyn TraitName 是一个独立的类型。

我们使用dyn TraitA改写上面的代码。

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit(i: u32) -> dyn TraitA { // 注意这里的返回类型换成了 dyn TraitA
  if i == 0 {
    let a = Atype;
    return a
  } else if i == 1 {
    let b = Btype;
    return b
  } else {
    let c = Ctype;
    return c
  }
}

```

但是编译会报错。

```plain
error[E0746]: return type cannot have an unboxed trait object
  --> src/lib.rs:13:20
   |
13 | fn doit(i: u32) -> dyn TraitA {
   |                    ^^^^^^^^^^ doesn't have a size known at compile-time
   |
help: return an `impl Trait` instead of a `dyn Trait`, if all returned values are the same type
   |
13 | fn doit(i: u32) -> impl TraitA {
   |                    ~~~~
help: box the return type, and wrap all of the returned values in `Box::new`
   |
13 ~ fn doit(i: u32) -> Box<dyn TraitA> {
14 |   if i == 0 {
15 |     let a = Atype;
16 ~     return Box::new(a)
17 |   } else if i == 1 {
18 |     let b = Btype;
19 ~     return Box::new(b)
20 |   } else {
21 |     let c = Ctype;
22 ~     return Box::new(c)

```

这段提示很经典，我们来仔细阅读一下。

它说 dyn TraitA 编译时尺寸未知。dyn trait确实不是一个固定尺寸类型。然后给出了第一个建议：你可以用 impl TraitA 来解决，前提是所有分支返回同一类型。随后给出了第二个建议，你可以用Box把dyn TraitA包起来。

（👨‍🏫：有没有ChatGPT的即时感，聪明得不太像一个编译器。）

第一个建议我们已经试过了，Pass，我们按照第二种建议改一下试试。

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit(i: u32) -> Box<dyn TraitA> {
    if i == 0 {
        let a = Atype;
        Box::new(a)
    } else if i == 1 {
        let b = Btype;
        Box::new(b)
    } else {
        let c = Ctype;
        Box::new(c)
    }
}

```

这下完美了，编译通过，达成目标，我们成功地将不同类型的实例在同一个函数中返回了。

这里我们引入了一个新的东西 `Box<T>`。 `Box<T>` 的作用是可以保证获得里面值的所有权，必要的时候会进行内存的复制，比如把栈上的值复制到堆中去。一旦值到了堆中，就很容易掌握到它的所有权。

具体到这个示例中，因为a、b、c都是函数中的局部变量，这里如果返回引用 `&dyn TraitA` 的话是万万不能的，因为违反了所有权规则。而 `Box<T>` 就能满足这里的要求。后续我们在智能指针一讲中会继续讲解 `Box<T>`。

这里我们先暂停，我希望你可以用一点时间来回顾一下整个推导过程，这次令人印象深刻的类型“体操”值得我们多品味几次。

### 利用trait object传参

impl trait 和 dyn trait 也可以用于函数传参。

impl trait的示例：

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit(x: impl TraitA) {}
// 等价于
// fn doit<T: TraitA>(x: T) {}

fn main() {
    let a = Atype;
    doit(a);
    let b = Btype;
    doit(b);
    let c = Ctype;
    doit(c);
}

```

dyn trait的示例：

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit(x: &dyn TraitA) {}  // 注意这里用了引用形式 &dyn TraitA

fn main() {
    let a = Atype;
    doit(&a);
    let b = Btype;
    doit(&b);
    let c = Ctype;
    doit(&c);
}

```

两种都可以。那么它们的区别是什么呢？

impl trait用的是编译器静态展开，也就是编译时具化（单态化）。上面那个impl trait示例展开后类似于下面这个样子。

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn doit_a(x: Atype) {}
fn doit_b(x: Btype) {}
fn doit_c(x: Ctype) {}

fn main() {
    let a = Atype;
    doit_a(a);
    let b = Btype;
    doit_b(b);
    let c = Ctype;
    doit_c(c);
}

```

而 dyn trait的版本不会在编译期间做任何展开，dyn TraitA 自己就是一个类型，这个类型相当于一个代理类型，用于在运行时代理相关类型及调用对应方法。既然是代理，也就是调用方法的时候需要多跳转一次，从性能上来说，当然要比在编译期直接展开一步到位调用对应函数要慢一点。

静态展开也有问题，就是会使编译出来的内容体积增大，而dyn trait就不会。所以它们各有利弊，可以根据需求视情况选择。另外， **impl trait和dyn trait都是消除类型参数的办法**。

那它们和enum相比呢？

enum是封闭类型集，可以把没有任何关系的任意类型包裹成一个统一的单一类型。后续的任何变动，都需要改这个统一类型，以及基于这个enum的模式匹配等相关代码。而impl trait和dyn trait是开放类型集。只要对新的类型实现trait，就可以传入使用了impl trait或dyn trait的函数，其函数签名不用变。

上述区别对于库的提供者非常重要。如果你提供了一个库，里面的多类型使用的enum包装，那么库的使用者没办法对你的enum进行扩展。因为一般来说，我们不鼓励去修改库里面的代码。而用 impl trait 或 dyn trait 就可以让接口具有可扩展性。用户只需要给他们的类型实现你的库提供的trait，就可以代入库的接口使用了。

而对于impl trait来说，它目前只能用于少数几个地方。一个是函数参数，另一个是函数返回值。其他的静态展开场景就得用类型参数形式了。

dyn trait本身是一种非固定尺寸类型，这就注定了相比于 impl trait 它能应用于更多场合，比如利用trait obj把不同的类型装进集合里。

### 利用trait obj将不同的类型装进集合里

我们看下面的示例，我们想把三种类型装进一个Vec里面。

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn main() {
    let a = Atype;
    let b = Btype;
    let c = Ctype;

    let v = vec![a, b, c];
}

```

报错：

```plain
error[E0308]: mismatched types
  --> src/main.rs:19:21
   |
19 |     let v = vec![a, b, c];
   |                     ^ expected `Atype`, found `Btype`

```

因为Vec中要求每一个元素是同一种类型，不能将不同的类型实例放入同一个Vec。而利用trait object，我们可以“绕”过这个限制。

请看示例：

```plain
struct Atype;
struct Btype;
struct Ctype;

trait TraitA {}

impl TraitA for Atype {}
impl TraitA for Btype {}
impl TraitA for Ctype {}

fn main() {
    let a = Atype;
    let b = Btype;
    let c = Ctype;
    let v: Vec<&dyn TraitA> = vec![&a, &b, &c];
}

```

成功了，不同类型的实例（实际是实例的引用）竟然被放进了同一个Vec中，强大！你可以自己尝试一下，将不同类型的实例放入HashMap中。

既然trait object这么好用，那是不是可以随便使用呢？不是的。除了前面提到的性能损失之外，还有一个问题，不是所有的trait都可以做dyn化，也就是说，不是所有的trait都能转成trait object使用。

### 哪些trait能用作trait object？

只有满足对象安全（object safety）的trait才能被用作trait object。Rust参考手册上有关于 [object safety](https://doc.rust-lang.org/beta/reference/items/traits.html?highlight=object#object-safety) 的详细规则，比较复杂。这里我们了解常用的模式就行。

安全的trait object：

```plain
trait TraitA {
    fn foo(&self) {}
    fn foo_mut(&mut self) {}
    fn foo_box(self: Box<Self>) {}
}

```

不安全的trait object：

```plain
trait NotObjectSafe {
    const CONST: i32 = 1;  // 不能包含关联常量

    fn foo() {}  // 不能包含这样的关联函数
    fn selfin(self); // 不能将Self所有权传入
    fn returns(&self) -> Self; // 不能返回Self
    fn typed<T>(&self, x: T) {} // 方法中不能有类型参数
}

```

规则确实比较复杂，你可以简单记住几种场景。

1. 不要在trait里面定义构造函数，比如new这种返回Self的关联函数。你可以发现，确实在整个Rust生态中都没有将构造函数定义在trait中的习惯。
2. trait里面尽量定义传引用 &self 或 &mut self的方法，而不要定义传值 self 的方法。

并不是所有的trait都能以trait object形式（dyn trait）使用，实际上，以dyn trait使用的场景可能是少数。所以你可以在遇到编译器报错的时候再回头来审视trait定义得是否合理。大部分情况下可以放心使用。

## 小结

![](https://static001.geekbang.org/resource/image/49/82/4951a0fdf2c4636f357702ac837c3382.jpg?wh=1390x1048)

在这节课的前半部分，我们讲解了trait中带类型参数的情况。各种符号组合起来，确实越来越复杂了。不过还是那句话，模式就那几种，只要花点时间熟悉理解，其实并不难。开始的时候能认识就行，后面在实践中再慢慢掌握。

我们使用带类型参数的trait实现了其他语言中函数重载的功能。看起来途径有点曲折，但是带给了我们一条全新的思路：以往的语言必须给自身添加各种特性来满足用户的要求，在Rust中，用好trait就能搞定。这让我们对Rust的未来充满期待，随着时间的发展，它不会像C++、Java那样永不停歇地添加可能会导致组合爆炸的新特性，而让自身越来越臃肿。

我们还讨论了带类型参数的trait与关联类型的区别。它们之间并不存在绝对优势的一方，在合适的场景下选择合适的方案是最重要的。

然后我们通过一个问题：如何让一个Rust函数返回可能的多种类型？推导出了引入trait object方案的必要性。整个推导过程比较曲折，同时也是对Rust类型系统的一次精彩探索。在这个探索过程中，我们和Rustc小助手成为了好朋友，在它的协助下，我们找到了最佳方案。

最后我们了解了trait object的一些用途，并讨论了trait object、impl trait，还有使用枚举对类型进行聚合这三种方式之间的区别。类型系统（类型+ trait）是Rust的大脑，你可以多加练习，熟悉它的形式，掌握它的用法。

## 思考题

请谈谈在函数参数中传入 `&dyn TraitA` 与 `Box<dyn TraitA>` 两种类型的区别。

欢迎你把思考后的结果分享到评论区，也欢迎你把这节课的内容分享给其他朋友，我们下节课再见！