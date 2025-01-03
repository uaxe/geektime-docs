你好，我是LMOS。

上节课，我们学习了算术指令中的加减指令和比较指令。不过一个CPU只能实现这两类指令还不够。如果你学过C语言，应该对“<<、>>、&、\|、!”这些运算符并不陌生，这些运算符都需要CPU提供逻辑和移位指令才可以实现。

今天我们就继续学习逻辑指令（and、or、xor）和移位指令 （sll、srl、sra）。代码你可以从 [这里](https://gitee.com/lmos/Geek-time-computer-foundation/tree/master/lesson16~17) 下载。话不多说，我们开始吧。

## 逻辑指令

从CPU芯片电路角度来看，其实CPU更擅长执行逻辑操作，如与、或、异或。至于为什么，你可以看看CPU的基础门电路。

RISC-V指令集中包含了三种逻辑指令，这些指令又分为立即数版本和寄存器版本，分别是andi、and、ori、or、xori、xor这六条指令。我们学习这些指令的方法和上节课类似，也涉及到写代码验证调试的部分。

### 按位与操作：andi、and指令

首先我们来学习一下andi、and指令，它们的形式如下所示：

```plain
andi rd，rs1，imm
#andi 立即数按位与指令
#rd 目标寄存器
#rs1 源寄存器1
#imm 立即数
and rd，rs1，rs2
#and 寄存器按位与指令
#rd 目标寄存器
#rs1 源寄存器1
#rs2 源寄存器2

```

上述代码中rd、rs1、rs2可以是任何通用寄存器，imm是立即数。

andi、and这两个指令完成的操作，我们用伪代码描述如下：

```plain
//andi
rd = rs1 & imm
//and
rd = rs1 & rs2

```

按位与的操作，就是把rs1与imm或者rs1与rs2其中的每个数据位两两相与。两个位都是1，结果为1，否则结果为0。

下面我们在工程目录下建立一个and.S文件，写代码验证一下这两个指令，如下所示：

```plain
.globl andi_ins
andi_ins:
    andi a0，a0，0xff       #a0 = a0&0xff，a0是C语言调用者传递的参数，a0也是返回值，这样计算结果就返回了
    jr ra                   #函数返回

.globl and_ins
and_ins:
    and a0，a0，a1          #a0 = a0&a1，a0、a1是C语言调用者传递的参数，a0是返回值，这样计算结果就返回了
    jr ra                   #函数返回

```

这里我们已经写好了andi\_ins与and\_ins函数，分别去执行andi和and指令。

andi指令是拿a0寄存器和立即数0xff进行与操作。由于立即数是0xff，所以总是返回a0的低8位数据；and指令则是拿a0和a1寄存器进行与操作，再把结果写入到a0寄存器。

下面我们用VSCode打开工程按下“F5”调试一下，如下所示：

![图片](https://static001.geekbang.org/resource/image/9f/85/9fa8f30d6acbe99195857b5412cab385.jpg?wh=1920x1018)

上图中是执行完andi a0，a0，0xff指令之后，执行jr ra指令之前的状态。可以看到，a0寄存器中的值确实已经变成2了，这说明运算的结果是符合预期的。

andi\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/cf/bf/cf81a2914a7d4a04abb5f33b886a53bf.jpg?wh=1920x1018)

因为2的二进制数据是（0b00000000000000000000000000000010）与上0xff的二进制数据是（0b00000000000000000000000011111111）结果确实是2，所以返回2，结果是正确的。

接下来，我们对and\_ins函数进行调试。

![图片](https://static001.geekbang.org/resource/image/26/ba/26b174f2983d6fcb3f1bee6a2a1513ba.jpg?wh=1920x1018)

上图展示的是执行完and a0，a0，a1指令之后，执行jr ra指令之前的状态。我们看到a0寄存器中的值已经变成了1，这说明运算的结果是正确的。

and\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/d8/07/d8923c72b17aa6653ef814ba9a9a4a07.jpg?wh=1920x1018)

上图中因为1的二进制数据是（0b00000000000000000000000000000001）与上1的二进制数据是（0b00000000000000000000000000000001）确实是1，所以返回1，结果完全正确。

### 按位或操作：ori、or指令

按位与操作说完了，我们接着来学习一下或指令ori、or，它们的形式如下：

```plain
ori rd，rs1，imm
#ori 立即数按位或指令
#rd 目标寄存器
#rs1 源寄存器1
#imm 立即数
or rd，rs1，rs2
#or 寄存器按位或指令
#rd 目标寄存器
#rs1 源寄存器1
#rs2 源寄存器2

```

同样地，上述代码中rd、rs1、rs2可以是任何通用寄存器，imm表示立即数。

我们还是从伪代码的描述入手，看看ori、or完成的操作。

```plain
//ori
rd = rs1 | imm
//or
rd = rs1 | rs2

```

按位或的操作就是把rs1与imm或者rs1与rs2其中的每个数据位两两相或，两个位有一位为1，结果为1，否则结果为0。

我们在and.S文件中写写代码，做个验证，如下所示：

```plain
.globl ori_ins
ori_ins:
    ori a0，a0，0           #a0 = a0|0，a0是C语言调用者传递的参数，a0也是返回值，这样计算结果就返回了
    jr ra                   #函数返回

.globl or_ins
or_ins:
    or a0，a0，a1           #a0 = a0|a1，a0、a1是C语言调用者传递的参数，a0是返回值，这样计算结果就返回了
    jr ra                   #函数返回

```

上述代码中ori\_ins与or\_ins函数，分别执行了ori和or指令。

ori指令是拿a0寄存器和立即数0进行或操作，由于立即数是0，所以总是返回a0原本的数据；or指令是拿a0和a1寄存器进行或操作，再把结果写入到a0寄存器。

我们还是到VSCode里，按下“F5”调试一下，如下所示：

![图片](https://static001.geekbang.org/resource/image/5e/0a/5e5ce8070d974bf0e52e754d79007d0a.jpg?wh=1920x1018)

上图中是执行完ori a0，a0，0指令之后，执行jr ra指令之前的状态。如果a0寄存器中的值确实已经变成0xf0f0了，就说明运算的结果正确。

ori\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/e6/cc/e61ddf5e843338ea343fa574cf1164cc.jpg?wh=1920x1018)

因为0xf0f0的二进制数据是（0b00000000000000001111000011110000）或上0的二进制数据是（0b00000000000000000000000000000000）按位或操作是“有1为1”，所以返回0xf0f0，结果是正确的。

我们再用同样的方法调试一下or\_ins函数，如下图所示：

![图片](https://static001.geekbang.org/resource/image/5f/c0/5f8a306758312ded463bb189338db7c0.jpg?wh=1920x1018)

上图展示的是执行完or a0，a0，a1指令之后，执行jr ra指令之前的状态。如果我们看到a0寄存器中的值确实已经变成0x1111了，就说明运算的结果正确，符合预期。

or\_ins函数返回后，输出的结果如下：

![图片](https://static001.geekbang.org/resource/image/57/2d/5757744ae7ef2f103052bdd73c4fee2d.jpg?wh=1920x1018)

上图中or\_ins函数第一个参数为0x1000的二进制数据是（0b00000000000000000001000000000000）第二个参数为0x1111的二进制数据是（0b00000000000000000001000100010001）两个参数相或，而按位或操作是“有1为1”，所以返回0x1111，结果是正确的。

### 按位异或操作：xori、xor指令

最后，我们再说说逻辑指令中的最后两条指令xori、xor，即异或指令的立即数版本和寄存器版本，它们的形式如下所示：

```plain
xori rd，rs1，imm
#xori 立即数按位异或指令
#rd 目标寄存器
#rs1 源寄存器1
#imm 立即数
xor rd，rs1，rs2
#xor 寄存器按位异或指令
#rd 目标寄存器
#rs1 源寄存器1
#rs2 源寄存器2

```

形式上和前面与操作、或操作差不多，就不过多重复了。

xori、xor完成的操作用伪代码描述如下：

```plain
//xori
rd = rs1 ^ imm
//xor
rd = rs1 ^ rs2

```

按位异或的操作是把rs1与imm或者rs1与rs2其中的每个数据位两两相异或，两个位如果不相同，结果为1。如果两个位相同，结果为0。

在and.S文件中写代码验证一下，如下所示。

```plain
.globl xori_ins
xori_ins:
    xori a0，a0，0          #a0 = a0^0，a0是C语言调用者传递的参数，a0也是返回值，这样计算结果就返回了
    jr ra                   #函数返回

.globl xor_ins
xor_ins:
    xor a0，a0，a1          #a0 = a0^a1，a0、a1是C语言调用者传递的参数，a0是返回值，这样计算结果就返回了
    jr ra                   #函数返回

```

我们已经写好了xori\_ins与xor\_ins函数，分别是执行xori和xor指令。xori指令是拿a0寄存器和立即数0进行异或操作，由于立即数是0，而且各个数据位相同为0，不同为1，所以同样会返回a0原本的数据 ；而xor指令是拿a0和a1寄存器进行或操作，再把结果写入到a0寄存器。

下面我们按下“F5”调试一下，如下所示：

![图片](https://static001.geekbang.org/resource/image/c1/18/c1526857c0858d8a3aaa677a9f0c2218.jpg?wh=1920x1018)

上图中是执行完xori a0，a0，0指令之后，执行jr ra指令之前的状态，我们已经看到a0寄存器中的值已经变成0xff了，这说明运算的结果正确。

xori\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/14/c1/14b11e93584c57fdd1ff280963fe8fc1.jpg?wh=1920x1018)

结合上面这张截图不难发现，我们传递给xori\_ins函数的参数是0xff，因为0xff的二进制数据是（0b00000000000000000000000011111111）异或上0的二进制数据是（0b00000000000000000000000000000000）按位异或操作是“相同为0，不同为1”，所以返回0xff，结果是正确的。

我们再来调试一下xor\_ins函数。xor a0，a0，a1指令执行完成之后，执行jr ra指令之前的状态如图所示：

![图片](https://static001.geekbang.org/resource/image/5f/2d/5f7f46c2d0bfb3606fb3688ba0a2df2d.jpg?wh=1920x1018)

我们看到a0寄存器中的值已经变成0了，这说明运算的结果正确，符合预期。

xor\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/77/50/7715a7a17fb10ce1b92f927af3df6050.jpg?wh=1920x1018)

由于我们给xor\_ins函数传递了两个相同的参数都是0xffff。因为0xffff的二进制数据是（0b00000000000000001111111111111111）两者异或，按位异或操作是“相同为0，不同为1”，所以返回0，结果是正确的。

下面我们看一下andi、and、ori、or、xori、xor这六条指令的二进制数据。

我们打开工程目录下的and.bin文件，如下所示：

![图片](https://static001.geekbang.org/resource/image/e8/14/e88bced6c98efd0fc41c012da6581b14.jpg?wh=1920x1018)

上述图中的12个32位数据是12条指令，其中六个0x00008067数据是六个函数的返回指令。

具体的指令形式，还有对应的汇编语句，我用表格帮你做了整理。

![](https://static001.geekbang.org/resource/image/a2/0c/a26bb58d2d217a803ee0cd37dbfa950c.jpg?wh=1990x1077)

同样地，我带你拆分一下andi、and、ori、or、xori、xor指令的各位段的数据，看看它们是如何编码的。

![图片](https://static001.geekbang.org/resource/image/f2/05/f2a7d01e3f94fyyf939a2890e0925e05.jpg?wh=1920x2118)

从上图中可以发现，立即数版本和寄存器版本的and、or、xor指令通过 **操作码** 区分，而它们之间的寄存器和立即数版本是靠 **功能位段** 来区分，立即数位段和源寄存器与目标寄存器位段和之前的指令是相同的。

到这里六条逻辑指令已经拿下了，咱们继续学习移位指令。

## 移位指令

移位指令和逻辑操作指令一样，都是CPU电路很容易就能实现的。

RISC-V指令集中的移位指令包括逻辑左移、逻辑右移和算术右移，它们分别有立即数和寄存器版本，所以一共有六条。逻辑右移和算术右移是不同的，等我们后面用到时再专门讲解。

### 逻辑左移指令：slli、sll指令

我们先看看逻辑左移指令，也就是slli、sll指令，它们的形式如下所示：

```plain
slli rd，rs1，imm
#slli 立即数逻辑左移指令
#rd 目标寄存器
#rs1 源寄存器1
#imm 立即数，rs1左移的位数，0~31
sll rd，rs1，rs2
#sll 寄存器逻辑左移指令
#rd 目标寄存器
#rs1 源寄存器1
#rs2 源寄存器2，rs1左移的位数

```

上述代码中rd、rs1、rs2可以是任何通用寄存器。imm是立即数，其实在官方文档中，这里是shamt，表示rs1 左移 shamt 位。这里我为了和之前的形式保持一致，才继续沿用了imm。

![](https://static001.geekbang.org/resource/image/31/93/31d86b306ec670c9b13ce51a8f898f93.jpg?wh=4127x668)

slli、sll它们俩完成的操作，用伪代码描述如下：

```plain
//slli
rd = rs1 << imm
//sll
rd = rs1 << rs2

```

逻辑左移的操作是把rs1中的数据向左移动imm位，或者把rs1中的数据向左移动rs2位，右边多出的空位填 0 并写入 rd 中。

我们用图解来表达这一过程，这样你就能一目了然了。

![图片](https://static001.geekbang.org/resource/image/7a/4f/7a38a717cfce6c6a07afdeae71b44e4f.jpg?wh=1920x887)

接下来我们在工程目录下，建立一个sll.S文件，写代码验证一下，如下所示：

```plain
.globl slli_ins
slli_ins:
    slli a0, a0, 4          #a0 = a0<<4，a0是C语言调用者传递的参数，a0也是返回值，这样计算结果就返回了
    jr ra                   #函数返回

.globl sll_ins
sll_ins:
    sll a0, a0, a1          #a0 = a0<<a1，a0、a1是C语言调用者传递的参数，a0是返回值，这样计算结果就返回了
    jr ra                   #函数返回

```

这里已经写好了slli\_ins与sll\_ins函数，它们会分别执行slli和sll指令。立即数逻辑左移slli指令是把a0中的数据左移4位。而逻辑左移sll指令是把a0中的数据左移，左移多少位要取决于a1中的数据，完成移动后再把结果写入到a0寄存器。

我们还是用VSCode打开工程，按下“F5”调试，如下所示：

![图片](https://static001.geekbang.org/resource/image/14/81/14ce5c27f3821d280a89473f1be2f881.jpg?wh=1920x1018)

上图中是进入slli\_ins函数，执行完slli a0，a0，4指令之后，执行jr ra指令之前的状态，我们给slli\_ins函数传进来的参数是0xffff。现在对照图示就能看到，a0寄存器中的值确实已经变成0xffff0了，这说明运算结果是正确的。

slli\_ins函数返回后，输出的结果如下：

![图片](https://static001.geekbang.org/resource/image/54/96/54b331abb31b9c670501801d9b1a4196.jpg?wh=1920x1018)

因为0xffff二进制数据是（0b00000000000000001111111111111111），逻辑左移4位后的结果是0xffff0，它的二进制数据是（0b00000000000011111111111111110000），结果正确无误。

下面我们接着对sll\_ins函数进行调试，如下所示：

![图片](https://static001.geekbang.org/resource/image/fd/e6/fd743ff7bc5a08326a930117a312e9e6.jpg?wh=1920x1018)

上图中是进入sll\_ins函数，执行完sll a0，a0，a1指令之后，执行jr ra指令之前的状态，我们给sll\_ins函数传进来的参数是0xeeeeeeee和31（a1寄存器）。如果看到a0寄存器中的值确实已经变成0了，这说明运算结果是正确的。

sll\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/dc/40/dcd32534bbb191edea2863106173fc40.jpg?wh=1920x1018)

第一个参数0xeeeeeeee的二进制数据是（0b11101110111011101110111011101110），逻辑左移31位后的结果是0，因为它把所有的二进制数据位都移出去了，然后空位补0，所以结果正确无误。

### 逻辑右移指令：srli、srl

有逻辑左移就有逻辑右移。逻辑右移指令srli、srl，分别对应着立即数和寄存器版本，它们的形式如下：

```plain
srli rd，rs1，imm
#srli 立即数逻辑右移指令
#rd 目标寄存器
#rs1 源寄存器1
#imm 立即数，rs1右移的位数，0~31
srl rd，rs1，rs2
#srl 寄存器逻辑右移指令
#rd 目标寄存器
#rs1 源寄存器1
#rs2 源寄存器2，rs1右移的位数

```

上述代码中rd、rs1、rs2可以是任何通用寄存器。imm是立即数。为了和之前的形式保持一致，我们还是沿用imm，而非官方文档中的shamt。

srli、srl完成的操作，可以用后面的伪代码来描述：

```plain
//srli
rd = rs1 >> imm
//srl
rd = rs1 >> rs2

```

逻辑右移的操作是把rs1中的数据向右移动imm位。或者把rs1中的数据向右移动rs2位，左边多出的空位填 0 并写入 rd 中。

你可以对照我画的图示来理解这一过程。

![图片](https://static001.geekbang.org/resource/image/ef/96/efabf037545b87932a801fd0d0f52b96.jpg?wh=1920x852)

光看看格式自然不够，我们在sll.S文件中写段代码来验证一下，如下所示：

```plain
.globl srli_ins
srli_ins:
    srli a0, a0, 8          #a0 = a0>>8,a0是C语言调用者传递的参数，a0也是返回值，这样计算结果就返回了
    jr ra                   #函数返回

.globl srl_ins
srl_ins:
    srl a0, a0, a1          #a0 = a0>>a1,a0、a1是C语言调用者传递的参数，a0是返回值，这样计算结果就返回了
    jr ra                   #函数返回

```

逻辑右移的两个函数srli\_ins与srl\_ins，我已经帮你写好了。代码中立即数逻辑右移srli指令是把a0中的数据右移8位。逻辑右移srl指令，则是把a0中的数据右移，右移多少位要看a1中数据表示的位数是多少，再把结果写入到a0寄存器。

两条右移指令做了哪些事儿咱们说完了，老规矩，打开工程按下“F5”就可以调试了，效果如图：

![图片](https://static001.geekbang.org/resource/image/5a/9c/5a31254538411e323fde6aa4a9a8189c.jpg?wh=1920x1018)

上图中是进入srli\_ins函数，执行完srli a0，a0，8指令之后，执行jr ra指令之前的状态，我们给srli\_ins函数传进来的参数是0xffff。现在，对照截图可以看到a0寄存器中的值确实已经变成0xff了，这说明运算结果正确。

srli\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/54/2e/54e7a1bfa5d16657c44006a2145fa12e.jpg?wh=1920x1018)

因为调用函数srli\_ins的参数0xffff的二进制数据是（0b00000000000000001111111111111111），逻辑右移8位后的结果是0xff，它的二进制数据是（0b00000000000000000000000011111111），结果正确，符合我们的预期。

拿下了srli\_ins函数，接下来就是srl\_ins函数的调试，如下所示：

![图片](https://static001.geekbang.org/resource/image/c9/6f/c93920be7759af658c978a26327e756f.jpg?wh=1920x1018)

上图中是调用进入srl\_ins函数，执行完srl a0，a0，a1指令之后，执行jr ra指令之前的状态，给srl\_ins函数传进来的参数是0xaaaaaaaa。可以看到，a0寄存器中的值确实已经变成0xaaaa了，所以运算结果也是正确的。

srl\_ins函数返回后，输出的结果如下图所示：

![图片](https://static001.geekbang.org/resource/image/03/b7/03e4500cb8544ab75f8634094f7b67b7.jpg?wh=1920x1018)

给srl\_ins函数传进来的第一个参数是0xaaaaaaaa的二进制数据是（0b10101010101010101010101010101010），逻辑右移16位后的结果是0xaaaa，其二进制数据为（0b00000000000000001010101010101010 ），因为它把低16位二进制数据位移出去了，然后高16位的空位补0，所以结果正确无误。

### 算术右移指令：srai、sra

最后还有两个算术右移指令，它们和逻辑右移的最大区别是， **数据在逻辑右移之后左边多出空位用0填充，而数据在算术右移之后左边多出的空位是用数据的符号位填充。** 如果数据的符号位为1就填充1，如果为0就填充0。

它们的形式和伪代码与逻辑右移是一样的，只不过指令助记符由srli、srl，变成了srai、sra。

下面我们直接在sll.S文件中，写代码进行验证。

```plain
.globl srai_ins
srai_ins:
    srai a0, a0, 8          #a0 = a0>>8,a0是C语言调用者传递的参数，a0也是返回值，这样计算结果就返回了
    jr ra                   #函数返回

.globl sra_ins
sra_ins:
    sra a0, a0, a1          #a0 = a0>>a1,a0、a1是C语言调用者传递的参数，a0是返回值，这样计算结果就返回了
    jr ra                   #函数返回

```

上述代码中的两个函数srai\_ins与sra\_ins，可以实现算术右移。先看立即数算术右移srai指令，它把a0中的数据右移了8位。而算术右移srl指令是把a0中的数据右移，右移多少位由a1中的数据表示的位数来决定，之后再把结果写入到a0寄存器。

我们按下“F5”，调试的结果如下：

![图片](https://static001.geekbang.org/resource/image/9a/2b/9aa7f0f2aa4a9abaf23ed0d592d6aa2b.jpg?wh=1920x1018)

上图中是进入立即数算术右移函数srai\_ins，执行完srai a0，a0，8指令之后，执行jr ra指令之前的状态。对照图里红框的内容可以看到，给srai\_ins函数传进来的参数是0x1111。如果a0寄存器中的值确实已经变成0x11了，就代表运算结果正确。

srai\_ins函数返回后，输出的结果如下：

![图片](https://static001.geekbang.org/resource/image/90/b8/90f4c5995f6bbcbca6cee49e4ebyy6b8.jpg?wh=1920x1018)

因为我们给立即数算术右移函数srai\_ins的参数0x1111，其二进制数据是（0b00000000000000000001000100010001），符号位为0，所以算术右移8位后的结果是0x11，它的二进制数据是（0b00000000000000000000000000010001），结果非常正确。

我们接着调试一下sra\_ins函数，如下所示：

![图片](https://static001.geekbang.org/resource/image/35/1d/35de77c0e524003a44025e2be12cb31d.jpg?wh=1920x1018)

上图中是进入算术右移函数sra\_ins，执行完sra a0，a0，a1指令之后，执行jr ra指令之前的状态。对照图里左侧红框的部分，我们就能知道sra\_ins函数传进来的参数是0xaaaaaaaa，你可能判断a0寄存器里输出的结果应该是0x0000aaaa，但调试显示的实际结果却是0xffffaaaa。

出现这个结果，你很奇怪是不是？但这恰恰说明运算结果是正确的。我们先看看sra\_ins函数返回后输出的结果是什么，然后再分析原因。

![图片](https://static001.geekbang.org/resource/image/d8/18/d885d37ca6d113bdb94f9bdb2edf1318.jpg?wh=1920x1018)

因为我们给算术右移函数sra\_ins的参数是0xaaaaaaaa和16，这表明对0xaaaaaaaa算术右移16，0xaaaaaaaa的二进制数据是（0b10101010101010101010101010101010），注意 **其符号位为1，所以算术右移16位后的结果是0xffffaaaa**，它的二进制数据是（0b11111111111111111010101010101010），结果是符合预期的。输出的结果也证实了这一点。

下面我们还是要看一下slli、sll、srli、srl、srai、sra这六条指令的二进制数据，我们打开工程目录下的sll.bin文件。

![图片](https://static001.geekbang.org/resource/image/fc/22/fc286f7194da0c7d3f8e70b56488fa22.jpg?wh=1920x1018)

可以看出，图中的12个32位数据是12条指令，其中六个0x00008067数据是六个函数的返回指令。具体的指令形式，还有对应的汇编语句，你可以参考后面的表格。

![图片](https://static001.geekbang.org/resource/image/26/fd/2684dc87df76536ffce7868f50e42dfd.jpg?wh=1920x1002)

我们拆分一下slli、sll、srli、srl、srai、sra指令的各位段的数据，看看它们是在内存中如何编码的，你可以结合示意图来理解。

![图片](https://static001.geekbang.org/resource/image/21/62/2112acb08732cbbd227b777407a5b262.jpg?wh=1920x1930)

我虽然给你详细展示了这些指令如何编码，但并不需要你把细节全部硬记下来，重点是观察其中的规律。

从上图中我们可以发现，sll、srl、sra指令的立即数版本和寄存器版本要通过操作码区分，而它们之间是靠功能位段来区分的， **源寄存器与目标寄存器所在的位段和之前的指令是相同的**。需要注意的是，这些立即数版本的立即数位段在官方文档中叫shamt位段，并且只占5位，而其它指令的立即数占12位，这里为了一致性还是沿用立即数。

到这里，六条移位指令我们就讲完了。

## 重点回顾

今天我们学习了逻辑指令和移位指令。

逻辑操作的指令包括andi、ori、or、xori、xor，分别能对寄存器与寄存器、寄存器与立即数进行与、或、异或操作。有了这些操作，CPU才能对数据进行逻辑运算，在一些情况下还能提升CPU的执行性能。更多的应用，后面课程里我们还会继续学习。

数据移位指令包括slli、sll、srli、srl、srai、sra，也能分别能对寄存器与寄存器、寄存器与立即数进行逻辑左移、逻辑右移、算术右移操作。这些指令与逻辑指令一起执行数据的位运算时，相当有用，在特定情况下能代替乘除法指令。

![图片](https://static001.geekbang.org/resource/image/04/f3/0463e88de6e311593bbc497eb8779bf3.jpg?wh=1920x1707)

经过漫长的学习，我们用两节课程的篇幅，一鼓作气学习了RISC-V全部的算术指令，分为加减、比较、逻辑、移位四大类别，一共有19条指令。这些指令作用于数据的运算，在应用程序中扮演着重要角色。

但是CPU有了这些算术指令就够了吗？这显然是不行的，起码还需要流程控制指令和数据加载储存指令，我们会在后续课程中继续讨论。

## 思考题

为什么指令编码中，目标寄存器，源寄存器1，源寄存器2，占用的位宽都是5位呢？

欢迎你在留言区记录自己的疑问或收获，参与越多，你对内容的理解也更深入。如果觉得这节课内容不错，别忘了分享给更多朋友。