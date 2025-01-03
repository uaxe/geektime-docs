你好，我是孙鹏飞。

专栏上一期，绍文讲了编译插桩的三种方法：AspectJ、ASM、ReDex，以及它们的应用场景。学完以后你是不是有些动心，想赶快把它们应用到实际工作中去。但我也还了解到，不少同学其实接触插桩并不多，在工作中更是很少使用。由于这项技术太重要了，可以实现很多功能，所以我还是希望你通过理论 + 实践的方式尽可能掌握它。因此今天我给你安排了一期“强化训练”，希望你可以趁热打铁，保持学习的连贯性，把上一期的理论知识，应用到今天插桩的练习上。

为了尽量降低上手的难度，我尽量给出详细的操作步骤，相信你只要照着做，并结合专栏上期内容的学习，你一定可以掌握插桩的精髓。

## ASM插桩强化练习

![](https://static001.geekbang.org/resource/image/e2/07/e2f777c2fb2ed535be7367643e43c307.png?wh=1204*1026)

在上一期里，Eateeer同学留言说得非常好，提到了一个工具，我也在使用这个工具帮助自己理解ASM。安装“ASM Bytecode Outline”也非常简单，只需要在Android Studio中的Plugin搜索即可。

![](https://static001.geekbang.org/resource/image/7a/47/7ad456d5f6d5054d6259f66a41cb6047.png?wh=1610*412)

ASM Bytecode Outline插件可以快速展示当前编辑类的字节码表示，也可以展示出生成这个类的ASM代码，你可以在Android Studio源码编译框内右键选择“Show Bytecode Outline“来查看，反编译后的字节码在右侧展示。

我以今天强化练习中的 [SampleApplication](https://github.com/AndroidAdvanceWithGeektime/Chapter-ASM/blob/master/ASMSample/src/main/java/com/sample/asm/SampleApplication.java) 类为例，具体字节码如下图所示。

![](https://static001.geekbang.org/resource/image/fd/bc/fd7c472e83d37fa3a55124309bcb10bc.png?wh=1920*688)

除了字节码模式，ASM Bytecode Outline还有一种“ASMified”模式，你可以看到SampleApplication类应该如何用ASM代码构建。

![](https://static001.geekbang.org/resource/image/f7/66/f7f75f73002335d89289bf03636a6f66.png?wh=1920*606)

下面我们通过两个例子的练习，加深对ASM使用的理解。

**1\. 通过ASM插桩统计方法耗时**

今天我们的第一个练习是：通过ASM实现统计每个方法的耗时。怎么做呢？请你先不要着急，同样以SampleApplication类为例，如下图所示，你可以先手动写一下希望实现插桩前后的对比代码。

![](https://static001.geekbang.org/resource/image/f2/dd/f2bf3b43308b42b78a865f7b36209ddd.png?wh=1920*284)

那这样“差异”代码怎么样转化了ASM代码呢？ASM Bytecode Outline还有一个非常强大的功能，它可以展示相邻两次修改的代码差异，这样我们可以很清晰地看出修改的代码在字节码上的呈现。

![](https://static001.geekbang.org/resource/image/b6/e5/b6502906622a46a638dd9f3af10619e5.png?wh=1920*926)

“onCreate”方法在“ASMified”模式的前后差异代码，也就是我们需要添加的ASM代码。在真正动手去实现插桩之前，我们还是需要理解一下ASM源码中关于Core API里面ClassReader、ClassWriter、ClassVisitor等几个类的用法。

我们使用ASM需要先通过ClassReader读入Class文件的原始字节码，然后使用ClassWriter类基于不同的Visitor类进行修改，其中COMPUTE\_MAXS和EXPAND\_FRAMES都是需要特别注意的参数。

```
ClassReader classReader = new ClassReader(is);
//COMPUTE_MAXS 说明使用ASM自动计算本地变量表最大值和操作数栈的最大值
ClassWriter classWriter = new ClassWriter(ClassWriter.COMPUTE_MAXS);
ClassVisitor classVisitor = new TraceClassAdapter(Opcodes.ASM5, classWriter);
//EXPAND_FRAMES 说明在读取 class 的时候同时展开栈映射帧(StackMap Frame)，在使用 AdviceAdapter里这项是必须打开的
classReader.accept(classVisitor, ClassReader.EXPAND_FRAMES);

```

如果要统计每个方法的耗时，我们可以使用AdviceAdapter来实现。它提供了onMethodEnter()和onMethodExit()函数，非常适合实现方法的前后插桩。具体的实现，你可以参考今天强化练习中的 [TraceClassAdapter](https://github.com/AndroidAdvanceWithGeektime/Chapter-ASM/blob/master/asm-gradle-plugin/src/main/java/com/geektime/asm/ASMCode.java#L60) 的实现：

```
private int timeLocalIndex = 0;
@Override
protected void onMethodEnter() {
    mv.visitMethodInsn(INVOKESTATIC, "java/lang/System", "currentTimeMillis", "()J", false);
    timeLocalIndex = newLocal(Type.LONG_TYPE); //这个是LocalVariablesSorter 提供的功能，可以尽量复用以前的局部变量
    mv.visitVarInsn(LSTORE, timeLocalIndex);
}

@Override
protected void onMethodExit(int opcode) {
    mv.visitMethodInsn(INVOKESTATIC, "java/lang/System", "currentTimeMillis", "()J", false);
    mv.visitVarInsn(LLOAD, timeLocalIndex);
    mv.visitInsn(LSUB);//此处的值在栈顶
    mv.visitVarInsn(LSTORE, timeLocalIndex);//因为后面要用到这个值所以先将其保存到本地变量表中
    int stringBuilderIndex = newLocal(Type.getType("java/lang/StringBuilder"));
    mv.visitTypeInsn(Opcodes.NEW, "java/lang/StringBuilder");
    mv.visitInsn(Opcodes.DUP);
    mv.visitMethodInsn(Opcodes.INVOKESPECIAL, "java/lang/StringBuilder", "<init>", "()V", false);
    mv.visitVarInsn(Opcodes.ASTORE, stringBuilderIndex);//需要将栈顶的 stringbuilder 保存起来否则后面找不到了
    mv.visitVarInsn(Opcodes.ALOAD, stringBuilderIndex);
    mv.visitLdcInsn(className + "." + methodName + " time:");
    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(Ljava/lang/String;)Ljava/lang/StringBuilder;", false);
    mv.visitInsn(Opcodes.POP);//将 append 方法的返回值从栈里 pop 出去
    mv.visitVarInsn(Opcodes.ALOAD, stringBuilderIndex);
    mv.visitVarInsn(Opcodes.LLOAD, timeLocalIndex);
    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/StringBuilder", "append", "(J)Ljava/lang/StringBuilder;", false);
    mv.visitInsn(Opcodes.POP);//将 append 方法的返回值从栈里 pop 出去
    mv.visitLdcInsn("Geek");
    mv.visitVarInsn(Opcodes.ALOAD, stringBuilderIndex);
    mv.visitMethodInsn(Opcodes.INVOKEVIRTUAL, "java/lang/StringBuilder", "toString", "()Ljava/lang/String;", false);
    mv.visitMethodInsn(Opcodes.INVOKESTATIC, "android/util/Log", "d", "(Ljava/lang/String;Ljava/lang/String;)I", false);//注意： Log.d 方法是有返回值的，需要 pop 出去
    mv.visitInsn(Opcodes.POP);//插入字节码后要保证栈的清洁，不影响原来的逻辑，否则就会产生异常，也会对其他框架处理字节码造成影响
}

```

具体实现和我们在ASM Bytecode Outline看到的大同小异，但是这里需要注意局部变量的使用。在练习的例子中用到了AdviceAdapter的一个很重要的父类LocalVariablesSorter，这个类提供了一个很好用的方法newLocal，它可以分配一个本地变量的index，而不用用户考虑本地变量的分配和覆盖问题。

另一个需要注意的情况是，我们在最后的时候需要判断一下插入的代码是否会在栈顶上遗留不使用的数据，如果有的话需要消耗掉或者POP出去，否则就会导致后续代码的异常。

这样我们就可以快速地将这一大段字节码完成了。

**2\. 替换项目中的所有的new Thread**

今天另一个练习是：替换项目中所有的new Thread，换为自己项目的CustomThread类。在实践中，你可以通过这个方法，在CustomThread增加统计代码，从而实现统计每个线程运行的耗时。

不过这也是一个相对来说坑比较多的情况，你可以提前考虑一下可能会遇到什么状况。同样我们通过修改 [MainActivity](https://github.com/AndroidAdvanceWithGeektime/Chapter-ASM/blob/master/ASMSample/src/main/java/com/sample/asm/MainActivity.java#L20) 的startThread方法里面的Thread对象改变成CustomThread，通过ASM Bytecode Outline看看在字节码上面的差异：

![](https://static001.geekbang.org/resource/image/a7/0a/a7579f0e2e6fc1df1fa7b880946c740a.png?wh=1920*452)

InvokeVirtual是根据new出来的对象来调用，所以我们只需要替换new对象的过程就可以了。这里需要处理两个指令：一个new、一个InvokeSpecial。在大多数情况下这两条指令是成对出现的，但是在一些特殊情况下，会遇到直接从其他位置传递过来一个已经存在的对象，并强制调用构造方法的情况。

而我们需要处理这种特殊情况，所以在例子里我们需要判断new和InvokeSpecial是否是成对出现的。

```
 private boolean findNew = false;//标识是否遇到了new指令
        @Override
        public void visitTypeInsn(int opcode, String s) {
            if (opcode == Opcodes.NEW && "java/lang/Thread".equals(s)) {
                findNew = true;//遇到new指令
                mv.visitTypeInsn(Opcodes.NEW, "com/sample/asm/CustomThread");//替换new指令的类名
                return;
            }
            super.visitTypeInsn(opcode, s);
        }

        @Override
        public void visitMethodInsn(int opcode, String owner, String name, String desc, boolean itf) {
            //需要排查CustomThread自己
            if ("java/lang/Thread".equals(owner) && !className.equals("com/sample/asm/CustomThread") && opcode == Opcodes.INVOKESPECIAL && findNew) {
                findNew= false;
                mv.visitMethodInsn(opcode, "com/sample/asm/CustomThread", name, desc, itf);//替换INVOKESPECIAL 的类名，其他参数和原来保持一致
                return;
            }
            super.visitMethodInsn(opcode, owner, name, desc, itf);
        }

```

new指令的形态相对特殊，比如我们可能会遇到下面的情况：

```
new A(new B(2));

```

字节码如下，你会发现两个new指令连在一起。

```
NEW A
    DUP
    NEW B
    DUP
    ICONST_2
    INVOKESPECIAL B.<init> (I)V
    INVOKESPECIAL A.<init> (LB;)V

```

虽然ASM Bytecode Outline工具可以帮助我们完成很多场景下的ASM需求，但是在处理字节码的时候还是需要考虑很多种可能出现的情况，这点需要你注意一下每个指令的特征。所以说在稍微复杂一些的情况下，我们依然需要对ASM字节码以及ASM源码中的一些工具类有所了解，并且需要很多次的实践，毕竟实践是最重要的。

最后再留给你一个思考题，如何给某个方法增加一个try catch呢？你可以尝试一下在今天强化练习的代码里根据我提供的插件示例实现一下。

强化练习的代码： [https://github.com/AndroidAdvanceWithGeektime/Chapter-ASM](https://github.com/AndroidAdvanceWithGeektime/Chapter-ASM)

## 福利彩蛋

学到这里相信你肯定会认同成为一个Android开发高手的确不容易，能够坚持学习和练习，并整理输出分享更是不易。但是也确实有同学坚持下来了。

还记得在专栏导读里我们的承诺吗？我们会选出坚持参与学习并分享心得的同学，送出2019年GMTC大会的门票。今天我们就来兑现承诺，送出价值4800元的GMTC门票一张。获得这个“大礼包”的同学是@唯鹿，他不仅提交了作业，更是在博客里分享了每个练习Sample实现的过程和心得，并且一直在坚持。我在文稿里贴了他的练习心得文章链接，如果你对于之前的练习Sample还有不明白的地方，可以参考唯鹿同学的实现过程。

- [Android 开发高手课 课后练习（1 ~ 5）](https://blog.csdn.net/qq_17766199/article/details/85716750)

- [Android 开发高手课 课后练习（6 ~ 8，12，17，19）](https://blog.csdn.net/qq_17766199/article/details/86770948)

- [专栏第4期完成作业](https://github.com/simplezhli/Chapter04)

- [专栏第19期完成作业](https://github.com/simplezhli/Chapter19)


GMTC门票还有剩余，给自己一个进阶的机会，从现在开始一切都还来得及。

> 小程序、Flutter、移动AI、工程化、性能优化…大前端的下一站在哪里？GMTC 2019全球大前端技术大会将于6月北京盛大开幕，来自Google、BAT、美团、京东、滴滴等一线前端大牛将与你面对面共话前端那些事，聊聊大前端的最新技术趋势和最佳实践案例。
>
> 目前大会最低价7折购票火热进行中，讲师和议题也持续招募中，点击下方图片了解更多大会详情！

[![](https://static001.geekbang.org/resource/image/e6/68/e65943bb1d18357a19b7121678b78b68.png?wh=1110*549)](http://gmtc2019.geekbang.org/?utm_source=wechat&utm_medium=geektime&utm_campaign=yuedu&utm_term=0223)

* * *