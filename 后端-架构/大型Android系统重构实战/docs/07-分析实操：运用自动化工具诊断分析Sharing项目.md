你好，我是黄俊彬。上一节我给你介绍了两个遗留系统常用的分析工具：ArchUnit和Dependencies依赖分析工具。

虽然我们了解了它们的基本使用方法，但是实际落地到项目中，我们经常会遇到一些问题，比如：

1.代码散落各处，约束规则不好写？

2.结合架构设计，怎么来设计约束规则？

3.约束规则怎么应用到自动化分析工具上？

这节课我们就一起用ArchUnit和Dependencies对Sharing项目进行一次整体分析。

这个分析由五部分组成。

- 第一部分，将代码结构按新的架构设计进行调整。
- 第二部分，根据代码结构以及新架构设计定义出依赖规则。
- 第三部分，将依赖规则转化成Dependencies的Rule规则，然后进行扫描分析。
- 第四部分，将依赖规则转化成ArchUnit的用例，进行扫描分析。
- 最后，总结出从现有的代码结构按未来架构设计需要重构的问题清单，作为下一阶段代码重构的输入。

通过这节课的分析，你可以学会在实际项目中如何结合工具来落地架构分析工作，上面的问题也能得到解答。

## 以新架构设计来组织代码

首先，我们一起回顾一下Sharing项目目前代码的方式。如下图所示，所有的代码是以技术维度来组织。例如把所有页面都放在ui的包下，或者把所有的模型都放在model下。

![](https://static001.geekbang.org/resource/image/7d/67/7d0d10c32f45f6ab1e73d248f771a667.jpg?wh=2546x2220)

这个时候我们就会遇到代码散落在各处，约束规则不好写的问题。如果我们不先以未来架构设计的方式来组织代码，那么所有依赖规则的编写只能细分到类，不能按包的维度来编写。这样首先会导致用例增多，其次规则也会比较分散，给后续维护带来不便。

所以为了更好地进行分析，首先我们会先按未来的架构设计组织代码。我们来看看第6节课梳理的新组件划分架构。在新的架构设计中，横向维度划分了3个分层，纵向维度划分了3个业务组件、2个功能组件以及3个技术组件。

![](https://static001.geekbang.org/resource/image/cd/0c/cddd3b628356afb668520e30173d9a0c.jpg?wh=3242x1857)

根据新的架构图，我们重新划分新的包结构，如下表所示。注意， **我们需要让代码的架构以及名称与架构图的设计对应上，这样便于我们理解和维护。**

![](https://static001.geekbang.org/resource/image/16/7d/16da758a195bc19bd5daccc8f7de5c7d.jpg?wh=3500x1422)

接下来，我们就可以按照新的代码结构进行调整了。这个时候要注意 **借助IDE的安全重构方法来移动代码，避免手工移动**。

比如，我们可以通过Move Class的方法（选中文件后按下F6快捷键或者点击 Refactor->Move Class菜单）进行移动，这样编辑器会自动帮我们调整相关的引用，调整后Sharing新的目录结构是后面这样。

![](https://static001.geekbang.org/resource/image/61/13/618564e1d7a4421037e44bdc2da2a013.jpg?wh=2546x2220)

在实际项目落地中，这个步骤有三点注意事项。

第一点，这个步骤我们最好可以拉通相关的开发、架构等干系人（我们可以通过版本管理系统来查看之前这个文件主要的维护人）一起进行梳理。因为有些文件我们能从类名判断它属于哪个组件，但是有些文件如果之前设计得不好，我们还需要跟相关的同学确认。

第二点，移动文件会触发CI判定这些文件是新增文件，进而触发增量扫描，CI会将以前遗留的很多问题也扫描出来。但注意，这些问题不是因为移动文件产生的，而是原本就存在于代码库中。我们需要和相关的干系人进行澄清说明，以免移动后的代码提交无法入库。

第三点，工程目录结构的调整会涉及到大量文件的位置变化，需要在团队中进行拉通，避免很多临时分支还在基于旧的代码目录结构进行开发，否则后期会产生大量的代码冲突，解决成本非常高。

## Sharing架构代码规则设计

基于新的代码结构，我们就可以设计架构约束规则了。首先，我们再来回顾一下Sharing2.0架构的两个重要约束原则。

- **纵向规则：上层组件可以依赖下层组件，下层组件不能反向依赖上层的组件**。

- **横向规则：业务组件之间不能有直接的依赖，功能及技术组件之间尽量减少依赖**。


基于这两个原则，我们结合代码结构设计出新的架构核心的5个约束规则，你可以参考后面这张表格。

![](https://static001.geekbang.org/resource/image/aa/f2/aac3ba374347c540bf34b594a0ec7bf2.jpg?wh=3409x1394)

梳理出这些约束规则后，我们就可以将这些规则转换成工具的规则进行分析了。

## Dependencies依赖分析

首先，我们需要定义各个组件的Scope，这一步相当于是定义各个组件的范围。如下图所示，新增一个Scope后，可以选择在项目中对应的的目录，当然也可以直接在Pattern中写正则表达式来进行定义。

![](https://static001.geekbang.org/resource/image/7e/a1/7e5f828f2577cd1a432d2591aa71dda1.jpg?wh=2546x2220)

定义好Scope之后，我们将5个核心约束规则转化为Dependencies的依赖规则。

下图中的 **Deny usages of feature in library** 表示feature范围下的代码不能被library范围下的代码直接依赖。

![](https://static001.geekbang.org/resource/image/6f/4a/6fc7a2f0fa19f2573c51e5f6d026ba4a.jpg?wh=2117x2220)

当完成依赖规则定义后，Dependencies扫描结果会自动化将所有的异常依赖标记为红色，如下图所示。

![](https://static001.geekbang.org/resource/image/6b/42/6b2a5977f8ef5ac8fca7cd6e8a62a842.jpg?wh=2839x957)

从分析结果可以看出，目前Sharing项目有四个组件存在依赖问题，需要我们解耦，分别为文件组件、消息组件、基座组件以及日志组件。

我们打开具体有异常的类，IDE还会自动在代码加上警告的红色线。

![](https://static001.geekbang.org/resource/image/4d/92/4d3273bec173000f223291abcb16cd92.jpg?wh=2346x1101)

这是Dependencies功能与IDE高度集成带来的好处，我们可以在日常开发中就注意到架构约束的问题，避免破坏架构规则。

## ArchUnit 分析

接下来，ArchUnit的分析思路也是定义包范围，并将5个约束转化为依赖规则。首先，我们可以参考Dependencies的规则封装形式，将ArchUnit的语法也做进一步的封装，这样可以提高代码的复用性，降低后续用例的维护成本。

```plain
//某个包只能依赖另外一个包
private static ClassesShouldConjunction target_package_not_dependOn_other_package(String targetPackage, String... otherPackages) {
    return noClasses().that().resideInAPackage(targetPackage)
            .should().dependOnClassesThat().resideInAnyPackage(otherPackages);
}
//某个包只能依赖它自己，不能依赖其他包
private static ClassesShouldConjunction target_package_only_dependOn_itSelf(String targetPackage) {
    return classes().that().resideInAPackage(targetPackage)
            .should().dependOnClassesThat().resideInAPackage(targetPackage);
}

```

接着，我们定义不同的分层和组件。因为我们已经按未来的架构调整了工程目录，所以这一步我们可以很方便地定义出对应的分层和组件范围。

```plain
private static final String BASE = "com.jkb.junbin.sharing.";
private static final String FEATURE = BASE + "feature..";
private static final String FUNCTION = BASE + "function..";
private static final String LIBRARY = BASE + "library..";
private static final String FILE_BUNDLE = BASE + "feature.file..";
private static final String MESSAGE_BUNDLE = BASE + "feature.message..";
private static final String ACCOUNT_BUNDLE = BASE + "feature.account..";

```

最后将5个约束规则转化为ArchUnit的架构约束代码。这个时候前面封装的约束规则方法就起作用了，每个用例只需要传递相关的组件定义就可以了。

```plain
//规则1：library包下的类只能依赖自己包下的类，不能依赖function包或者feature包下的类
@ArchTest
public static final ArchRule library_should_only_dependOn_itself =
        target_package_not_dependOn_other_package(LIBRARY,FUNCTION,FEATURE);

//规则2：function包下的类不能依赖feature包下的类
@ArchTest
public static final ArchRule function_should_not_dependOn_feature =
        target_package_not_dependOn_other_package(FUNCTION, FEATURE);

//规则3：account包下的类不能依赖file或者message包下的类
@ArchTest
public static final ArchRule account_bundle_should_not_dependOn_other_bundle =
        target_package_not_dependOn_other_package(ACCOUNT_BUNDLE, FILE_BUNDLE, MESSAGE_BUNDLE);

//规则4：file包下的类不能依赖account或者message包下的类
@ArchTest
public static final ArchRule file_bundle_should_not_dependOn_other_feature =
        target_package_not_dependOn_other_package(FILE_BUNDLE, MESSAGE_BUNDLE, ACCOUNT_BUNDLE);

//规则5：message包下的类不能依赖account或者file包下的类
@ArchTest
public static final ArchRule message_bundle_should_not_dependOn_other_bundle =
        target_package_not_dependOn_other_package(MESSAGE_BUNDLE, FILE_BUNDLE, ACCOUNT_BUNDLE);

```

编写完成后，我们可以直接执行这5个用例。用例执行的结果是后面这样。

![](https://static001.geekbang.org/resource/image/2a/c6/2a62b6e103cd45592ed151441a1fcfc6.jpg?wh=2997x887)

从日志结果可以看出，目前Sharing项目有4个约束规则不通过，分别是文件组件存在横向依赖、消息组件存在横向依赖、功能组件存在反向依赖以及基础组件存在反向依赖。

## 总结

今天我们借助ArchUnit和Dependencies依赖分析功能对Sharing项目进行了一次分析。

为了更加方便地编写架构规则，我们需要将代码架构先按未来的架构设计进行调整。接着只需要定义组件的范围以及约束规则就可以了。最后结合工具辅助，我们梳理出Sharing按未来架构设计需要处理的问题清单。

![](https://static001.geekbang.org/resource/image/ba/af/ba1a41fd3432a0f5beef0e00cd10eaaf.jpg?wh=3500x1888)

我相信通过今天的学习，开头的3个问题你应该能找到答案。

**第一个问题，代码散落各处，约束规则不好写？对此，我们需要先按未来的架构设计调整代码结构，方便约束规则的设计。**

**第二个问题，结合架构设计，怎么来设计约束规则？我们需要结合架构原则以及代码结构来进行设计。**

**最后一个问题，约束规则怎么应用到自动化分析工具上？我们需要将约束规则转换成各个工具上的编写规则。**

至此，我们完成了“分析设计篇”的学习。通过学习移动应用的架构演进以及常用的遗留系统分析工具，我们全面诊断了对Sharing项目，最终输出了按未来架构设计需要处理的问题清单。

在接下来的“解耦重构篇”中，我们将基于这些分析结果，开始动手对Sharing进行代码的架构改造，敬请期待。

## 思考题

感谢你学完了今天的内容，今天的思考题是这样的：你能分析一下你所在项目的架构规则吗？请你尝试用ArchUnit来定义规则。

欢迎你在留言区与我交流讨论，也欢迎你把它分享给你的同事或朋友，我们一起来高效、高质量交付软件！