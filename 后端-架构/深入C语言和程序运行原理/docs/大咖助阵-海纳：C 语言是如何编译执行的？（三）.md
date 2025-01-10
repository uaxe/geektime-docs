你好，我是海纳。今天是“C 语言是如何编译执行的？”这一加餐系列的最后一讲。

一个编译器通常分为前端、中端和后端三个典型模块。前端主要包括词法分析和文法分析两个步骤，它的作用是把源文件转换成抽象语法树（Abstract Syntax Tree, AST）。在前面两期加餐中，我讲解了预处理、词法分析、文法分析的编译过程基本步骤，带你实现了一个小型 C 语言编译器前端。它将源代码翻译成了AST，而且支持了变量定义和赋值，if语句和while语句。

中端则主要是将AST转成中间表示（Intermediate Representation, IR），常见的中间表示有三地址码、基于图的静态单赋值表示等等，例如LLVM IR就是最常见的一种中间表示。编译器的优化主要集中在中端。

而后端的作用是将中间表示翻译成目标平台的机器码，并生成相应平台的可执行程序。机器码是由CPU指令集决定的，例如x86平台就要使用x86指令集，而arm64平台就应该使用aarch64指令集。华为的鲲鹏平台也是采用了aarch64指令集。可执行程序的格式则是由操作系统决定，例如在Windows系统上，可执行程序是PE格式的，exe文件或者dll文件都是PE格式；而Linux系统上，可执行程序则是ELF文件。

如果完全按顺序来的话，这节课应该继续介绍中端和后端。但是中端优化和后端代码生成这两个话题都涉及很多内容，展开来讲的话，往往需要一整本书的篇幅。为了帮你通过有限的篇幅快速理解编译器的结构，这节课我会介绍一种最简单的执行模型：基于栈的字节码和虚拟机。

## 字节码和虚拟机

和静态编译一样，字节码也是一种非常常见的策略。由于字节码具有跨平台的特性，所以它得到了广泛的普及，其中最有影响力的就是 Java 和 Python 字节码。“javac”这个工具会把Java源代码翻译成class文件，这个class文件就是字节码文件，它的代码部分全部由Java字节码组成。Python也是一样的，编译器也会先把py文件翻译成pyc文件，而pyc文件的代码部分则由Python字节码组成。

Java和Python的相似之处在于，它们都采用了一种基于栈的计算模型。我们来看下这个Python源文件：

```plain
a = 1
b = 2
def foo(c):
  return a + b + 3 * c

```

如果使用dis方法对foo函数进行反编译，就会得到如下输出：

```plain
>>> dis.dis(foo)
  2           0 LOAD_GLOBAL              0 (a)
              3 LOAD_GLOBAL              1 (b)
              6 BINARY_ADD
              7 LOAD_CONST               1 (3)
             10 LOAD_FAST                0 (c)
             13 BINARY_MULTIPLY
             14 BINARY_ADD
             15 RETURN_VALUE

```

其中LOAD\_XX指令的作用是把值加载到栈顶。GLOBAL表示当前字节码加载的是全局变量，CONST代表常量，FAST代表局部变量。

BINARY\_ADD的作用是把栈上的两个变量出栈，然后把这两个值相加的和再压入栈中，这是对两个值进行求和。BINARY\_MULTIPLY的作用是对两个值求积。这个过程比较简单，我就不再画图表示了，你可以想象一下每执行一个字节码，栈会发生怎样的变化。欢迎在评论区交流你的想法。

上面提到的每一条指令，在文件中都有一个编号。还是以Python虚拟机为例，它的指令编码可以在 [这里](https://gitee.com/sync_repo/cpython/blob/main/Include/opcode.h) 查看。指令总数不超过256，所以可以使用一个字节进行编码，这就是 **字节码(bytecode)** 这个名称的由来。

无论是在 arm 平台还是 x86 平台上，也不管是在 macOS 还是 Linux 系统上，相同的源文件翻译成的字节码都是相同的。字节码文件会被虚拟机加载、解析并执行。就像每个CPU可以执行自己指令集中的指令一样，虚拟机一般是由静态编译语言（例如C/C++/Rust）实现的，它就像一个CPU一样，逐条执行字节码，而字节码可以看成是虚拟机的指令集。

显然，不同平台的差异被虚拟机屏蔽掉了。正如上面所说，这种屏蔽底层差别，向上提供统一的指令集的办法，就像一个虚拟的计算机。这也正是语言虚拟机名字的由来。

基于栈的字节码，核心操作无非是压栈和出栈，大多数指令的操作数都在栈上，带有操作数的指令最多只带有一个操作数。基于栈的字节码，其指令不带参数或者只带一个参数，无论是编译器的实现还是虚拟机的实现都很简单。

接下来，我们就具体研究一下如何从AST生成基于栈的字节码。

## 生成字节码

如果你对后缀表达式求值比较熟悉的话，就会发现，上述字节码的执行过程是和后缀表达式求值相对应的。而且， [上节课](https://time.geekbang.org/column/article/493848) 我讲到了，对表达式的AST进行后序遍历就可以生成后缀表达式。其实，上节课的程序只要稍加修改就可以变成字节码的生成程序，具体如下所示：

```plain
void code_object_emit_code(CodeObject* co, Node* root, Context* context) {
    if (root->ntype == NT_INT) {
        byte param = (byte)code_object_find_constant_index(co, ((IntNode*)root)->value);
        code_object_append_bytecode(co, LOAD_CONST, param);
    }
    else if (root->ntype == NT_ASN) {
        AssignNode* node = (AssignNode*)root;
        code_object_emit_code(co, node->value, context);
        context->is_store = Store;
        code_object_emit_code(co, node->var, context);
        context->is_store = Load;
    }
    else if (root->ntype == NT_VAR) {
        VarNode* node = (VarNode*)root;
        if (context->is_store == Store) {
            byte param = (byte)code_object_find_variable_index(co, node->name);
            code_object_append_bytecode(co, STORE_NAME, param);
        }
        else {
            byte param = (byte)code_object_find_variable_index(co, node->name);
            code_object_append_bytecode(co, LOAD_NAME, param);
        }
    }
    else if (root->ntype == NT_IF) {
        IfNode* node = (IfNode*)root;
        code_object_emit_code(co, node->cond, context);
        code_object_jump_false(co, IF_ELSE);
        code_object_emit_code(co, node->then_clause, context);
        code_object_jump(co, IF_END);
        code_object_bind(co, IF_ELSE);
        code_object_emit_code(co, node->else_clause, context);
        code_object_bind(co, IF_END);
    }
    else if (root->ntype == NT_WHILE) {
        code_object_bind(co, WHILE_HEAD);

        WhileNode* node = (WhileNode*)root;
        code_object_emit_code(co, node->cond, context);

        code_object_jump_false(co, WHILE_END);
        code_object_emit_code(co, node->body, context);
        code_object_jump(co, WHILE_HEAD);
        code_object_bind(co, WHILE_END);
    }
    else if (root->ntype == NT_LIST) {
        ListNode* node = (ListNode*)root;
        for (int i = 0; i < node->length; i++) {
            code_object_emit_code(co, node->array[i], context);
        }
    }
    else if (root->ntype == NT_PRINT) {
        code_object_emit_code(co, ((PrintNode*)root)->expr, context);
        code_object_append_bytecode(co, PRINT, 0);
    }
    else {
        BinOpNode* binop = (BinOpNode*)root;
        code_object_emit_code(co, binop->left, context);
        code_object_emit_code(co, binop->right, context);

        enum NodeType tt = root->ntype;
        byte param = 0;
        if (tt == NT_ADD) {
            code_object_append_bytecode(co, BINARY_ADD, param);
        }
        else if (tt == NT_SUB) {
            code_object_append_bytecode(co, BINARY_SUB, param);
        }
        else if (tt == NT_DIV) {
            code_object_append_bytecode(co, BINARY_DIV, param);
        }
        else if (tt == NT_MUL) {
            code_object_append_bytecode(co, BINARY_MUL, param);
        }
        else if (tt == NT_LT) {
            code_object_append_bytecode(co, COMPARE, COMPARE_LT);
        }
    }
}

```

我知道，当你第一次读到这段代码的时候，内心一定是崩溃的。但不要害怕，其实用C语言写出来的代码比使用C++实现的访问者模式还要直观。接下来，我带着你一起来分析这段代码，你就会发现，这段程序的逻辑是简明直接的。

下面，我举四个例子来说明这段程序的工作原理。

先来看第一个例子，表达式“1+2”的AST如下图所示：

![图片](https://static001.geekbang.org/resource/image/c4/21/c4da4610259aca163ef063ed064c0b21.jpg?wh=1920x1073)

code\_object\_emit\_code 在访问加号结点时，会先访问它的左子树（代码第57行），再访问它的右子树（第58行），这将保证加法的两个操作数都在栈上。对于“1+2”这个例子，左子树是整型，所以程序会在常量池里找到整型的序号（第3行），把它作为LOAD\_CONST的参数（第4行）。之所以使用常量池序号作为LOAD\_CONST的参数，而不是直接使用整数，是因为参数是一个字节，而表示一个整数需要4个字节。这同时也意味着常量池的大小不能超过256。

综上所述，“1+2”这个表达式对应的字节码如下：

```plain
LOAD_CONST 0 # 代表数字1在常量池中的序号
LOAD_CONST 1 # 代表数字2在常量池中的序号
BINARY_ADD

```

第二个例子是赋值语句“int a = b”，这条语句所产生的AST如下图所示：

![图片](https://static001.geekbang.org/resource/image/30/50/30aae724700ee409e91530fefbccc250.jpg?wh=1920x1049)

从图中可以看出，赋值结点的左孩子和右孩子都是变量名，但这两个变量却是有所区别的。对变量a的访问，应该生成STORE指令，而对变量b的访问则应该生成LOAD指令。所以在这里我使用了一个Context变量，来指定 **当访问的是赋值语句的左端变量时，就使用STORE\_NAME指令（第9、16、17行），如果是访问普通的变量，则使用LOAD\_NAME指令（第20、21行）**。

和访问常量类似，我在生成代码的时候，也引入一个变量表。变量表和常量表都是一个列表，这里你也可以把它设计成哈希表，以加快查找速度。但总之，这两个表都是一种容器。所以，“int a = b”这个赋值语句所对应的字节码是：

```plain
LOAD_NAME 0 # 变量 b 在变量表中的序号
STORE_NAME 1 # 变量 a 在变量表中的序号

```

第三个例子是分支语句，代码“if (1 < 2) { print(1); } else {print(2);}”，它的AST如下图所示：

![](https://static001.geekbang.org/resource/image/e3/8e/e3926015c433f7b230e934b5cf73218e.jpg?wh=2284x1435)

这里说明下，print是我为了方便打印值而引入的一种非常规手段。由于支持函数调用需要的基础设施太多，我不可能在这短短的几节课内讲清楚，所以就把print当成了关键字来处理。遇到Print结点时，生成PRINT指令即可（第52、53行）。

对于If结点，它的cond、then\_clause、else\_clause的访问都很简单。难就难在，当条件不成立时，控制流应该跳过then\_clause，转而去执行else\_clause，这需要通过jump语句实现。

代码的第27行就是这个思路的直接体现。第27行的作用是生成JUMP\_IF\_FALSE指令，也就是说cond条件的执行结果为false时，就进行跳转。但是跳转的目标是哪里呢？答案是在then\_clause结束，else\_clause开始之前。

但这时候我们就遇到问题了：在生成JUMP指令的时候，我们还不知道then\_clause会产生多少字节码，也就是说，我们并不知道JUMP的目标地址在哪里。所以，在生成JUMP指令的时候，我们只能将目标地址空着（第27行），当目标地址确定了以后，再把目标地址回填到JUMP指令处，这正是bind函数所做的事情（第30行）。

相信你对这个过程已经不陌生了，因为这就是 **重定位（Relocation）** 所做的工作：把目标地址回填到JUMP、CALL等指令参数里。为了能够在重定位时正确地找到需要重定位的那条jump指令，我们必须要在code\_object\_jump\_false里将这条jump指令的地址记录下来。这种用于辅助重定位的信息就是重定位信息（Reloc Info）。

所以，经过重定位以后，这个例子中的分支语句最终生成的字节码就是：

```plain
	LOAD_CONST	1
	LOAD_CONST	2
	COMPARE	<
	JUMP_IF_FALSE	5
	LOAD_CONST	1
	PRINT
	JUMP	3
	LOAD_CONST	2
	PRINT

```

其中，第4行的字节码JUMP\_IF\_FALSE的作用就是让控制流向后跳5个字节。由于第5行的LOAD\_CONST和第7行的JUMP都带有一个参数，所以跳5个字节，控制流就指向了第8行，而这正是else\_clause开始的地方。

第7行的JUMP指令则是then\_clause结束的地方，这就意味着当if条件为true时，else\_clause就被跳过了。

最后一个例子是循环语句，代码“int i = 0; while (i < 10) { i = i + 1; print(i); }”。循环语句和分支语句有相似之处，它也包含两个跳转：第一个是当条件不成立时，要跳过循环体，第二个是循环体结束处，应该再跳转回循环头继续下一次判断。所以第一个跳转是条件跳转，第二个跳转则是绝对跳转。

而这两种跳转，我们都已经支持了。但是循环语句有一个分支语句所没有的特点，那就是循环体内可能会出现break。当遇到break语句时，控制流就应该直接跳到循环体的结尾。而循环体内可能有多个break语句，这就要求我们要在每个break语句处都记录下需要重定位的地址，所以我把这些重定位信息使用一个双向链表记录在了一起。具体的代码我就不在这里展示了，你可以去 [gitee](https://gitee.com/hinus/codelet/blob/master/compiler/code.c) 上查看。

同样地，最后一个例子的字节码展示如下：

```plain
	LOAD_CONST	0
	STORE_NAME	i
	LOAD_NAME	i
	LOAD_CONST	10
	COMPARE	<
	JUMP_IF_FALSE	12
	LOAD_NAME	i
	LOAD_CONST	1
	BINARY_ADD
	STORE_NAME	i
	LOAD_NAME	i
	PRINT
	JUMP	-20

```

通过这四个例子，我就把最基本的变量、分支和循环全部实现了。接下来，我们就再看一下这些字节码是如何实现的。也就是说，我们需要再研究一下虚拟机的具体实现。

## 虚拟机的实现

跟编译器的实现相比，虚拟机的实现更加直观：通过一个循环，不断地取出字节码，然后按照这个字节码的语义对栈进行操作。

按照上面的分析，我在这里展示一种常见的虚拟机实现：

```plain
void interpret(VirtualMachine* vm, CodeObject* co) {
    for (int i = 0; i < co->bytecodes->length; i++) {
        byte opcode = co->bytecodes->array[i];
        byte param = 0;
        int u, v;

        if (opcode >= OP_CODE_PARAMETER) {
            param = co->bytecodes->array[++i];
        }

        switch(opcode) {
        case LOAD_CONST:
            PUSH(co->constant_pool->array[param]);
            break;
        case STORE_NAME:
            u = POP();
            vm->var_table->array[param] = u;
            break;
        case LOAD_NAME:
            PUSH(vm->var_table->array[param]);
            break;
        case BINARY_ADD:
            u = POP();
            v = POP();
            PUSH(u+v);
            break;
        case PRINT:
            u = POP();
            printf("%d\n", u);
            break;
        case COMPARE:
            u = POP();
            v = POP();
            if (param == COMPARE_LT) {
                if (v < u) {
                    PUSH(1);
                }
                else {
                    PUSH(0);
                }
            }
            break;
        case JUMP_IF_FALSE:
            u = POP();
            if (!u) {
                i += param;
            }
            break;
        case JUMP:
            i += param;
            break;
        default:
            printf("Error, unrecognized bytecode: %d\n", opcode);
        }
    }
}

```

这里，我以JUMP\_IF\_FALSE为例进行讲解：虚拟机先从栈顶得到一个元素，再判断这个元素是否为false。如果不是false，则什么都不做，直接执行下一条字节码；但如果为false，就会给变量i加上这个跳转指令的参数。这样一来，i 就变成跳转的目标地址了。

其他字节码都比较简单，我就不再一一解释了，你可以在 [这里](https://gitee.com/hinus/codelet/tree/f6481d91d51df7bd59d16213e9dc1748fb05af84) 查看全部代码。

## 总结

在这节课里，我介绍了一种最简单的执行模型：基于栈的字节码和虚拟机。

把AST转换成字节码的过程，主要是通过后序遍历整个语法树，分别生成相应的字节码。其中，最难的部分是重定位的过程。重定位是指 **指令在生成的时候，跳转的目标地址尚不能确定，只能先把这条指令记录下来，当目标地址确定以后再将地址回填到指令参数里**。用于记录指令的信息称为重定位信息。条件语句的重定位信息只要有一条就够了，但循环语句因为存在break语句，所以重定位信息可能有多条，这就需要使用容器对它们进行管理。

字节码的指令不会超过256个，一个字节足够编码所有指令。另外，基于栈的字节码还有一个优势，就是参数都在栈上，所以指令参数的个数很少，最多只有一个参数，这就让字节码变得简洁，也让编译器的实现和虚拟机的实现都变得简单很多。

最后，我还展示了一个真实的虚拟机例子。典型的虚拟机的结构就是使用循环语句不断地取出字节码进行解析执行，循环体里包含一个巨大的switch-case。Python虚拟机和Java虚拟机都有类似的实现。

到这里，关于 C 语言编译过程的系列加餐先暂告一段落了。最后想说的是，编译器的设计是一个十分复杂的工程，因此很难在短短几篇文章中把中端后端的相关知识全部介绍给你。希望以后还有机会能在课程里带你从头开始实现一个完整的编译器。

青山不改，绿水长流，后会有期。我们有机会再见。