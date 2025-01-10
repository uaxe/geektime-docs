你好，我是Tony Bai。

在 [《Go语言第一课》](http://gk.link/a/10AVZ) 专栏中，缺少专门讲解Go测试的章节，这无疑是一个遗憾。在工程实践中，针对代码的测试是确保代码执行逻辑正确和代码质量的重要手段。所以，Go测试内容的空缺可能会让一些小伙伴在学习和实践过程中感到困惑。

为了解决这个问题，我决定用一篇加餐详细补充说明。我将带你快速入门Go测试的基本知识点，并针对实际开发中的Go测试实践提供几点实用建议。这不仅仅是一篇加餐，更是帮助你完善Go语言知识体系的重要一环。

## Go测试快速入门

Go语言内置了一个轻量级的测试框架，该框架通过 **go test命令** 和标准库的 **testing 包** 来提供测试功能。

Go测试框架要求所有Go测试代码都要放在以\_test.go结尾的测试源文件中。Go测试被抽象为一个个测试函数，测试源文件中的测试函数必须以Test开头，并且接受一个名为testing.T的参数，比如下面示例代码中的TestAdd函数：

```plain
// go-testing/add/add_test.go
package add

import (
    "testing"
)

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("want %d, but got %d", want, got)
    }
}

```

我们看到，在这个测试源文件中只有一个测试用例函数TestAdd。TestAdd向被测函数Add传入两个预设值2和3，并比较被测函数Add的返回结果与预期结果want。如果不一致，则调用testing.T的Errorf方法输出测试错误信息。

通常我们会使用 **断言（assert）** 来比较实际结果与预期结果之间的差异，验证代码行为是否符合预期，并在两者不匹配时触发测试失败。许多编程语言和测试框架都包含了丰富的断言库或断言函数，可以方便我们进行断言操作。常见的断言函数包括等值断言、不等值断言和真值断言等。不过，Go测试框架并未内置断言支持，你可以像上面示例代码那样使用 **if got != want的模式**，也可以借助第三方断言包，比如：github.com/stretchr/testify/assert。

go test命令负责提取测试文件中以Test开头的测试用例，并驱动测试的执行。我们在add目录下执行go test来运行上面的测试用例：

```plain
$go test
PASS
ok      add 0.007s

```

测试如我们预期那样通过了！如果你想看看go test执行过程的细节，可以使用下面的命令：

```plain
$go test -v
=== RUN   TestAdd
--- PASS: TestAdd (0.00s)
PASS
ok      add 0.007s

```

如果我们想模拟测试失败的情况，可以将预期结果改为6，再运行go test将得到下面的结果：

```plain
$go test -v
=== RUN   TestAdd
    add_test.go:11: want 6, but got 5
--- FAIL: TestAdd (0.00s)
FAIL
exit status 1
FAIL    add 0.005s

```

我们看到，当测试失败时，go test会打印出错误发生的具体上下文信息，包括测试文件名、行号以及Errorf打印的内容，这些上下文信息可以帮助开发者快速定位错误发生的位置。

如果测试文件中的某个TestXxx使用testing.T的Error/Errorf方法输出错误上下文信息，那么即便测试用例执行失败，TestXxx中的后续测试用例还可以继续得到执行。反之，如果使用的是testing.T的Fatal/Fatalf方法，那么一旦测试用例执行失败，Fatal/Fatalf输出错误上下文信息后，TestXxx函数中即便有后续测试用例，也不会被继续执行了。

像上面那样直接在当前目录下执行不带命令行参数的go test命令的模式，被称为 **本地目录模式（Local Directory Mode）**。在这种模式下，go test会编译当前目录下的包源码以及所有以 `_test.go` 结尾的测试源文件，并运行得到的测试二进制文件。

除此之外，go test还有另外一种运行模式，那就是 **包列表模式（package list mode）**，即go test后面带有显式的参数，如包名或具体路径：

```plain
$go test .
ok      add 0.005s

$go test -v .
=== RUN   TestAdd
--- PASS: TestAdd (0.00s)
PASS
ok      add 0.005s

$go test add
ok      add 0.005s

$go test -v add
=== RUN   TestAdd
--- PASS: TestAdd (0.00s)
PASS
ok      add 0.006s

```

**与本地目录模式不同的是，包列表模式下的go test支持缓存测试成功的结果**。如果当前测试都能通过且测试用例不变，那么后续多次在包列表模式下执行go test将直接从缓存中读取结果，而不会重复执行测试。下面展示了包列表模式下第二次执行go test -v add的输出结果：

```plain
$go test -v add
=== RUN   TestAdd
--- PASS: TestAdd (0.00s)
PASS
ok      add (cached)

```

我们看到，对于从缓存中读取的测试结果， **go test会在结果中使用 “(cached)” 字样做显式的标识**。

go test还支持通过-run来选择不同的测试用例执行，-run后面接一个正则表达式用于匹配测试用例的名字，比如：

```plain
$go test -v -run=.  //运行当前目录下所有测试用例
$go test -v -run=TestAdd //运行当前目录下所有名字中包含TestAdd的测试用例
$go test -v -run=^TestAdd$ // 运行当前目录下名字为TestAdd的测试用例
$go test -v -run=^$  // 不运行任何测试用例

```

go test命令还有很多常用的命令行选项，如果你对这些选项的用法感兴趣，可以使用go help testflag查看详细说明。

到这里，我们已经初步了解了Go测试框架，掌握了Go对测试的抽象以及如何使用go test驱动测试的执行，但这还不够。在实际的工程实践中，如何让测试更高效、实用和易于维护至关重要。为此，我整理了5个关于Go测试的实用建议，旨在帮助你简化测试的编写和维护，提高测试的效率与质量。

## 建议1：让添加新测试用例变得容易

我们知道，代码测试是保证代码质量的重要手段，为了团队能够更高效地编写和管理维护测试，我们应该努力降低添加新测试用例的门槛，让添加新测试用例变得更容易，鼓励团队成员多写测试，写出高质量的测试。

下面在原先测试的基础上，又添加了两个测试用例后的代码：

```plain
package add

import (
    "testing"
)

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("want %d, but got %d", want, got)
    }

    // add zero
    got = Add(2, 0)
    want = 2
    if got != want {
        t.Errorf("want %d, but got %d", want, got)
    }

    // add opposite number
    got = Add(2, -2)
    want = 0
    if got != want {
        t.Errorf("want %d, but got %d", want, got)
    }
}

```

我们看到，每增加一个新测试用例，都要编写很多重复的代码。这样既不方便测试用例的增加，也会导致整个测试函数冗长繁复。

**在Go语言中，要让添加新测试用例变得简单、直观，可以使用表驱动测试**。所谓表驱动就是将多个测试用例组织在一个表（通常是切片或map）中，然后利用循环来运行它们。下面的示例就是将Add函数的测试用例组织为一张表：

```plain
// go-testing/add/add_table_test.go

package add

import "testing"

func TestAddWithTable(t *testing.T) {
    cases := []struct {
        name string
        a    int
        b    int
        r    int
    }{
        {"2+3", 2, 3, 5},
        {"2+0", 2, 0, 2},
        {"2+(-2)", 2, -2, 0},
        //... ...
    }

    for _, caze := range cases {
        got := Add(caze.a, caze.b)
        if got != caze.r {
            t.Errorf("%s got %d, want %d", caze.name, got, caze.r)
        }
    }
}

```

TestAddWithTable与签名的TestAdd是一个等价的测试函数，不同之处在于TestAddWithTable将测试需要输入的数据与具体的测试执行逻辑“解耦”开了。现在添加一个用例，我们根本不需要编写任何新的代码，只需要添加一行新的数据。

如果目标是“使添加新的测试用例变得容易”，那对于像Add这样的简单函数，向表中添加一行数据就足够了。不过，这也引出了一个问题：我们应该添加哪些测试用例？这正是我们下一个建议要讲的。

## 建议2：使用测试覆盖率发现未经测试的代码

在日常开发中，开发人员不仅需要掌握如何编写测试代码，还要了解这些测试覆盖了哪些被测代码。毕竟，测试无法捕捉到未执行代码中的错误。

理想的情况是将被测代码的每个执行路径都覆盖到，为此人们还发明了一个术语“测试覆盖率（Test Coverage）”。这是软件测试中的一个度量指标，表示测试用例对代码的覆盖程度，即测试用例能够触及多少代码执行路径。测试覆盖率可以帮助开发者确定哪些代码路径没有被测试到。通过检查测试覆盖率报告，开发者可以确认是否存在未被覆盖的代码块，这些代码块可能隐藏着潜在的错误或漏洞。

Go语言的go test命令原生支持计算测试覆盖率，并可生成包含测试覆盖率信息的报告。我们来看下面这个例子。

```plain
// go-testing/coverage/demo.go

package main

// Add 函数将两个整数相加并返回结果
func Add(a, b int) int {
    if a == 0 {
        return b
    }
    if b == 0 {
        return a
    }
    return a + b
}

// IsPositive 函数检查给定的整数是否为正数
func IsPositive(num int) bool {
    if num > 0 {
        return true
    }
    return false
}

```

上面是demo.go中的两个被测函数：Add和IsPositive的实现。接下来，我们编写一些针对Add和IsPositive的测试代码：

```plain
// go-testing/coverage/demo_test.go

package main

import "testing"

func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", result)
    }

    result = Add(0, 5)
    if result != 5 {
        t.Errorf("Add(0, 5) = %d; want 5", result)
    }
}

func TestIsPositive(t *testing.T) {
    result := IsPositive(10)
    if !result {
        t.Error("IsPositive(10) = false; want true")
    }

    result = IsPositive(-5)
    if result {
        t.Error("IsPositive(-5) = true; want false")
    }

    result = IsPositive(0)
    if result {
        t.Error("IsPositive(0) = true; want false")
    }
}

```

在coverage目录下，我们执行下面命令便可以详细了解到底哪些代码被测试覆盖了，哪些没有被覆盖，还可以通过添加-coverprofile选项生成覆盖率报告文件，通过这些报告文件，我们可以对测试覆盖情况做进一步分析和处理。例如：

```plain
$go test -coverprofile=coverage.out
PASS
coverage: 87.5% of statements
ok      demo    0.007s

```

然后，我们用go tool cover来查看生成的覆盖率测试报告文件coverage.out的内容：

```plain
$go tool cover -html=coverage.out

```

go tool cover会自动打开浏览器，并展示一个html格式的覆盖率测试报告：

![图片](https://static001.geekbang.org/resource/image/27/87/270b9962180cdec2bdeef877a34bfd87.png?wh=1032x904)

通过该报告，我们看到Add函数的if b == 0在条件成立情况的分支尚未被测试覆盖到。找到未测试代码后，下一步就是思考怎么添加针对这部分代码的测试了。

我们看到覆盖率测试对指出可能被忽略的代码部分非常有用，但工具生成的覆盖率报告不能替代思考，即使代码拥有100%的测试覆盖率，仍然可能存在bug。因此，如何编写高质量的测试用例，仍然是开发人员的事情。

## 建议3：将子测试视为Test Case

要理解这个建议，我们需要先就 **什么是Go测试的最小测试单元** 达成共识。

什么是最小测试单元？是上面提到的TestXxx函数吗？在这里，我定义的最小测试单元，是TestAdd函数中的一段代码：

```plain
// add zero
got = Add(2, 0)
want = 2
if got != want {
    t.Errorf("want %d, but got %d", want, got)
}

```

也是TestAddWithTable函数中cases表的每一行输入数据：

```plain
cases := []struct {
    name string
    a    int
    b    int
    r    int
}{
    {"2+3", 2, 3, 5},
    {"2+0", 2, 0, 2},
    {"2+(-2)", 2, -2, 0},
    //... ...
}

```

所谓最小测试单元，就是被测函数针对指定输入的一次执行，并比对返回结果和预期结果，我也称它为一个测试用例（Test Case）。在进行测试中，我们应尽量保证各个测试用例之间互不影响，从而实现良好的隔离。这就需要合理组织测试用例。

我们将\*\_test.go文件中以Test开头的函数定义为 **Go顶层测试函数**。在Go测试框架中，顶层测试函数是组织Test Case的最佳容器，允许我们按照功能类别、测试目的等进行分类和组织。

而Go的子测试（subtest）使得我们可以将一个测试函数（TestXxx）分成多个小测试函数，每个小测试函数可以独立运行并报告测试结果。这种测试方式不仅有助于更好地隔离测试用例，还能实现更细粒度地控制测试执行，方便定位问题和调试。

下面是一个使用subtest改造TestAddWithTable的示例代码，展示了如何使用Go语言编写subtest：

```plain
// go-testing/add/add_sub_test.go

func TestAddWithSubtest(t *testing.T) {
    cases := []struct {
        name string
        a    int
        b    int
        r    int
    }{
        {"2+3", 2, 3, 5},
        {"2+0", 2, 0, 2},
        {"2+(-2)", 2, -2, 0},
        //... ...
    }

    for _, caze := range cases {
        t.Run(caze.name, func(t *testing.T) {
            got := Add(caze.a, caze.b)
            if got != caze.r {
                t.Errorf("got %d, want %d", got, caze.r)
            }
        })
    }
}

```

在上面的代码中，我们定义了一个名为TestAddWithSubtest的测试函数，并在其中使用t.Run()方法结合表驱动方式创建了三个subtest。这样一来，每个subtest都可以复用相同的错误处理逻辑，同时测试用例参数的不同又能体现差异。当然，若你不使用表驱动测试，那么每个subtest也都可以有自己独立的错误处理逻辑。执行上面TestAddWithSubtest这个测试用例（我们故意将Add函数的实现改成错误的），我们将看到下面结果：

```plain
$go test add_sub_test.go add.go
--- FAIL: TestAddWithSubtest (0.00s)
    --- FAIL: TestAddWithSubtest/2+3 (0.00s)
        add_sub_test.go:54: got 6, want 5
    --- FAIL: TestAddWithSubtest/2+0 (0.00s)
        add_sub_test.go:54: got 3, want 2
    --- FAIL: TestAddWithSubtest/2+(-2) (0.00s)
        add_sub_test.go:54: got 1, want 0

```

我们看到：在错误信息输出中，每个失败的用例都是以“TestXxx/subtestName”来标识的，这样我们可以很容易地将其与相应的代码行对应起来。更深层的意义是subtest让整个测试组织形式有了“层次感”！通过go test -run，我们甚至还能以这种“层次”选择要执行的subtest：

```plain
$go test  -v -run TestAddWithSubtest/-2 add_sub_test.go add.go
=== RUN   TestAddWithSubtest
=== RUN   TestAddWithSubtest/2+(-2)
    add_sub_test.go:54: got 1, want 0
--- FAIL: TestAddWithSubtest (0.00s)
    --- FAIL: TestAddWithSubtest/2+(-2) (0.00s)
FAIL
FAIL    command-line-arguments  0.006s
FAIL

```

除此之外，Go subtest在执行层面还有如下特点：

- 每个subtest都会放在单独的goroutine中执行，这有利于测试用例间保持相互的隔离。

- 某个subtest用例未过，通过Errorf，甚至是Fatalf输出错误结果，都不会影响到同一TestXxx下其他subtest的执行。

- 某个subtest中的某个测试结果判断未过，如果通过Errorf输出错误结果，则该subtest会继续执行；不过，如果subtest使用的是Fatal/Fatalf输出错误结果，则会导致该subtest的执行在调用Fatal/Fatalf的位置立即结束，subtest函数体内的后续测试代码将不会得到执行。

- 默认各个TestXxx下的subtest将按声明顺序逐一执行，即便它们是在各自的goroutine中执行的。


总的来说，对于稍大一些工程中的复杂包，以顶层测试函数为Test Suite，以subtest作为Test Case，可以实现更有层次、更灵活、更具扩展性以及更佳执行效率的测试组织形式。

## 建议4：如果你没有添加测试，那就没有修复Bug

工作中你可能会遇到这样一个场景：有人告诉你有一个Bug，你知道修复方法。更改后，你立即告诉他们问题已经修复，但他们却回复你，不，问题还存在。这听起来又低级又尴尬，但你却不知道面对过多少次了。我现在要分享给你的是，编写测试可以避免这种尴尬。

有些时候，在任何给定的程序中，某些错误比其他错误更有可能发生，比如空指针引用、数组越界等。因此，如果你犯了一次这个错误，你或其他人将来很可能再犯同样的错误。如果没有测试来阻止它们，Bug就会重新出现。

针对上述两种情况，你只需添加一个测试。一旦测试通过，Bug就会被修复，你就可以阻止同样的错误再次发生。

## 建议5：使用Fake Object解决依赖外部系统的测试

实际测试中，被测代码（System Under Test，SUT）常常要依赖真实组件的对象或程序（下图中的外部协作者）。于是我们需要在测试阶段使用测试替身（Test Double）来替代这些依赖，以方便测试。它们的关系如下图：

![图片](https://static001.geekbang.org/resource/image/0d/fb/0dfb779367a7b926d81ea1f2856403fb.png?wh=1001x446)

测试替身是通用术语，指的是不同类型的替换对象或程序。目前xUnit Patterns至少定义了五种类型的Test Double：

- Test Stubs
- Mock Objects
- Test Spies
- Fake Objects
- Dummy Objects

**这其中最为常用的是Fake Objects、Stub和Mock Objects。**

Fake Object最容易理解，它是被测代码SUT依赖的外部协作者的“替身”。和真实的外部协作者相比，Fake Object外部行为表现与真实组件几乎一致，但更简单也更易用，实现更轻量，足以满足测试需求。

Stub也是一个在测试阶段专用的，用来替代真实外部协作者与SUT进行交互的对象。与Fake Object稍有不同的是，Stub是一个内置了预期值/响应值，并且可以在多个测试间复用的测试替身。因此， **Stub可以理解为一种Fake Object的特例**。

而对于Mock Object这种测试替身（Test Double），它建立和使用的复杂程度取决于被测目标与外部协作者之间的交互复杂性。我们来看下面这个例子：

```plain
// go-testing/testdouble/mock/db/db.go
package main

// Define the `Database` interface
type Database interface {
    Save(data string) error
    Get(id int) (string, error)
}

// Example functions that use the `Database` interface
func saveData(db Database, data string) error {
    return db.Save(data)
}

func getData(db Database, id int) (string, error) {
    return db.Get(id)
}

// go-testing/testdouble/mock/db/db_test.go
package main

import (
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)

// Define a mock struct that implements the `Database` interface
type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) Save(data string) error {
    args := m.Called(data)
    return args.Error(0)
}

func (m *MockDatabase) Get(id int) (string, error) {
    args := m.Called(id)
    return args.String(0), args.Error(1)
}

func TestSaveData(t *testing.T) {
    // Create a new mock database
    db := new(MockDatabase)

    // Expect the `Save` method to be called with "test data"
    db.On("Save", "test data").Return(nil)

    // Call the code that uses the database
    err := saveData(db, "test data")

    // Assert that the `Save` method was called with the correct argument
    db.AssertCalled(t, "Save", "test data")

    // Assert that no errors were returned
    assert.NoError(t, err)
}

func TestGetData(t *testing.T) {
    // Create a new mock database
    db := new(MockDatabase)

    // Expect the `Get` method to be called with ID 123 and return "test data"
    db.On("Get", 123).Return("test data", nil)

    // Call the code that uses the database
    data, err := getData(db, 123)

    // Assert that the `Get` method was called with the correct argument
    db.AssertCalled(t, "Get", 123)

    // Assert that the correct data was returned
    assert.Equal(t, "test data", data)

    // Assert that no errors were returned
    assert.NoError(t, err)
}

```

在这个例子中，被测目标是两个接受Database接口类型参数的函数：saveData和getData。显然在测试阶段，我们不能为这两个函数传入真实的Database实例去测试。

这里，我们没有使用Fake Object，而是定义了一个Mock Object：MockDatabase，该类型实现了Database接口。然后我们定义了两个测试函数，TestSaveData和TestGetData，它们分别使用MockDatabase实例来测试saveData和getData函数。

在每个测试函数中，我们对MockDatabase实例进行设置，包括期待特定参数的方法调用，然后调用该数据库的代码（即被测目标函数saveData和getData）。最后我们使用github.com/stretchr/testify中的assert包，断言代码的预期行为。

那在日常编码时究竟应该选择哪一种呢？下面我就来简单对比这三种测试替身的优缺点。

从Mock Object的例子来看，测试代码的核心在于构建Mock Object以及设置其方法的参数和返回结果。相较于Fake Object的简单直接，Mock Object在使用上较为复杂。

对Go语言来说，Mock Object要与接口类型联合使用。如果被测目标的参数是非接口类型，Mock Object便“无从下嘴”了。此外，Mock Object使用难易程度和被测目标与外部协作者的交互复杂度相关。像上面这个例子，建立Mock Object就比较简单。但对于一些复杂的函数，当存在多个外部协作者，并且与每个协作者都有多次交互的情况下，建立和设置Mock Object就变得困难且更加难于理解。

但是，Mock Object仅是满足了被测目标对依赖的外部协作者的调用需求，比如设置不同参数传入下的不同返回值，并未真实处理被测目标传入的参数。这会降低测试的可信度以及开发人员对代码正确性的信心。

此外，如果被测函数的输入输出未发生变化，但内部逻辑发生了变化，比如调用的外部协作者的方法参数、调用次数等，使用Mock Object的测试代码也需要一并更新维护。

而作为测试替身，Fake Object/Stub有如下优点：

- 我们与Fake Object的交互方式与真实外部协作者交互的方式相同。这让其显得更简单，更容易使用，也降低了测试的复杂性。

- Fake Object的行为更像真正的协作者，可以给开发人员更多的信心。

- 当真实协作者更新时，我们不需要更新使用Fake Object时设置的预期结果和结果验证条件。因此，使用Fake Object时，重构代码往往比使用其他测试替身更容易。


因为测试的主要目的是保证被测系统代码的正确性，让开发人员对自己编写的代码更有信心，所以从这个角度来看，我们在 **单测时应优先为外部协作者提供满足测试需求的Fake Object**。

不过，Fake Object使用容易，但建立较难。但随着技术的进步，Fake Object的实现和获取也变得日益容易。比如，要想快速构建一个Fake Object，我们可以借助类似ChatGPT或GitHub Copilot这样的AI辅助编码工具，即便是几百行代码的Fake Object，实现起来也很容易。

如果要追求更高的可信度和功能覆盖水平，我们还可以借助容器技术来构建“真实版/无阉割版”的Fake Object。比如借助GitHub上开源的testcontainers-go，构建Fake Object更简便，并且testcontainer提供了常见的外部协作者的封装实现，如MySQL、Redis和Postgres等。

以测试redis client为例，我们可借助testcontainer建立如下测试代码：

```plain
// go-testing/testdouble/fake/redis_test.go

package main

import (
    "context"
    "fmt"
    "testing"

    "github.com/go-redis/redis/v8"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func TestRedisClient(t *testing.T) {
    // Create a Redis container with a random port and wait for it to start
    req := testcontainers.ContainerRequest{
        Image:        "redis:latest",
        ExposedPorts: []string{"6379/tcp"},
        WaitingFor:   wait.ForLog("Ready to accept connections"),
    }
    ctx := context.Background()
    redisC, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started:          true,
    })
    if err != nil {
        t.Fatalf("Failed to start Redis container: %v", err)
    }
    defer redisC.Terminate(ctx)

    // Get the Redis container's host and port
    redisHost, err := redisC.Host(ctx)
    if err != nil {
        t.Fatalf("Failed to get Redis container's host: %v", err)
    }
    redisPort, err := redisC.MappedPort(ctx, "6379/tcp")
    if err != nil {
        t.Fatalf("Failed to get Redis container's port: %v", err)
    }

    // Create a Redis client and perform some operations
    client := redis.NewClient(&redis.Options{
        Addr: fmt.Sprintf("%s:%s", redisHost, redisPort.Port()),
    })
    defer client.Close()

    err = client.Set(ctx, "key", "value", 0).Err()
    if err != nil {
        t.Fatalf("Failed to set key: %v", err)
    }

    val, err := client.Get(ctx, "key").Result()
    if err != nil {
        t.Fatalf("Failed to get key: %v", err)
    }

    if val != "value" {
        t.Errorf("Expected value %q, but got %q", "value", val)
    }
}

```

运行这个测试，我们将看到像下面这样的结果：

```plain
$go test
2024/12/15 16:18:20 github.com/testcontainers/testcontainers-go - Connected to docker:
  Server Version: 20.10.8
  API Version: 1.41
  Operating System: Ubuntu 20.04.3 LTS
  Total Memory: 10632 MB
2024/12/15 16:18:21 Failed to get image auth for docker.io. Setting empty credentials for the image: docker.io/testcontainers/ryuk:0.3.4. Error is:credentials not found in native keychain

2024/12/15 16:19:06 Starting container id: 0d8341b2270e image: docker.io/testcontainers/ryuk:0.3.4
2024/12/15 16:19:10 Waiting for container id 0d8341b2270e image: docker.io/testcontainers/ryuk:0.3.4
2024/12/15 16:19:10 Container is ready id: 0d8341b2270e image: docker.io/testcontainers/ryuk:0.3.4
2024/12/15 16:19:28 Starting container id: 999cf02b5a82 image: redis:latest
2024/12/15 16:19:30 Waiting for container id 999cf02b5a82 image: redis:latest
2024/12/15 16:19:30 Container is ready id: 999cf02b5a82 image: redis:latest
PASS
ok      demo    73.262s

```

一些开源项目，如etcd也提供了用于测试的自身简化版的实现（embed），我们可以用它们作为Fake Object。并且，这一点也值得我们效仿，在团队内部每个服务的开发者如果都能提供一个服务的简化版实现，那对该服务调用者来说，代码测试就会变得十分容易。

## 小结

这一节我们深入探讨了Go语言测试，完善了《Go语言第一课》的知识体系。我们一定要重视测试，学会使用Go测试工具和testing包来编写和执行Go代码测试用例。

此外，对于实际开发中的Go测试实践，我也提供了5个实用建议。

1. **简化新测试用例的添加**：使用表驱动测试让增加测试用例变得简单直观，门槛更低。

2. **利用测试覆盖率**：通过覆盖率工具识别未被测试的代码，确保代码的每条执行路径都被覆盖。

3. **将子测试视为测试用例**：利用子测试实现更细粒度的测试组织，提高测试的可维护性和清晰度。

4. **添加测试以修复Bug**：保证每次修复都有对应的测试，防止Bug复发。

5. **使用测试替身**：在依赖外部系统时多使用行为更像真正协作者的Fake对象，确保测试独立性和可控性的同时，可以 **给开发人员更多的信心**。


希望你能将这些建议应用于实际项目中，编写出更高质量的测试代码，提高代码的可靠性与可维护性，提升开发效率。

最后，建议你自己动手实践下这一节的测试建议。如果有新的想法，也欢迎分享在留言区，我们一起交流。我是Tony Bai，我们下节课见。