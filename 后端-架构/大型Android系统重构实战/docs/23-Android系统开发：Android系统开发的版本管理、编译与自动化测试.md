你好，我是黄俊彬。

这节课起，我们进入到扩展篇的学习。扩展篇我们将从系统角度，学习定制Android系统的一些常见问题和解决思路。一起了解定制Android系统中常见的一些开发方式、架构问题以及解耦思路。

从应用到系统开发，代码量从几十万行增长到几千万行，开发框架以及编译环境等与应用开发也不一样。所以如果要学习Android系统开发，我们需要先了解对应的开发框架及工具链。

今天，我们就来聊聊Android系统开发的版本管理、编译调试以及相关的自动化测试等实践，了解引入这些工具及实践的目的。在实践过程中用好这些工具，会大大提升开发效率。

## Repo & Gerrit 代码管理

我们先来看看代码的管理。由于Android源码的代码量庞大，采用的是多个Git仓库来管理代码。你可以通过 [GoogleSource](https://android.googlesource.com/?format=HTML) 查看对应的仓库，大约有3000个仓库。

那么，假如有一个需求开发涉及到跨多个仓库的修改，我们怎么来维护代码提交以及同步工作呢？

为了解决这个问题， **官方提供了一个多Git仓代码管理的工具——** [Repo](https://gerrit.googlesource.com/git-repo/+/refs/heads/master/README.md)。根据官网的介绍，Repo 不会取代 Git，目的是帮助我们在 Android 环境中更轻松地使用 Git。

Repo 将多个 Git 项目汇总到一个Manifest文件中，使用Repo命令来并发操作多个Git仓库的代码提交与代码同步很方便。我用表格梳理了一些Repo常用的命令，供你参考。

![](https://static001.geekbang.org/resource/image/93/14/935a266e7e3508231e617209a5b9e614.jpg?wh=3000x1271)

通常使用Repo进行Android 开发的基本工作流程如下图所示，包括创建分支、修改文件、提交暂存、提交更改以及最后上传到审核服务器。

![](https://static001.geekbang.org/resource/image/d5/a0/d5d4efdf0d40d79e41e47aee15cc33a0.jpg?wh=2900x752)

另外，一般情况下，应用开发使用的代码审核工具都是类似于GitLab平台，通过临时分支拉取Merge Request提交代码审核，审核通过后，完成代码入库。针对于多仓库的代码审核，官方提供了另外一个代码审核工具—— [Gerrit](https://android-review.googlesource.com/q/status:open+-is:wip)。

Gerrit 是一个基于网页的代码审核系统，适用于使用 Git 的项目。Google原先就是为了管理Android项目而设计了Gerrit。与Merge Request的代码审核差异是，Gerrit采用+1 +2打分的方式来控制代码的合入，你可以结合后面的截图来理解。

![](https://static001.geekbang.org/resource/image/69/c4/698f0d4995d1d0124d8e79d262ca1ac4.jpg?wh=2948x796)

那么Gerrit是如何来关联多个仓库的代码提交记录呢？这也是和GitLab等工具不同的地方，Gerrit 提供了标准的 “commit-msg” 钩子来生成Change-Id。通过Change-Id，可以关联到多个代码仓库的提交，方便管理跨仓库的代码提交。

## Soong编译系统

接下来，我们来看看Android系统的编译。

前面从代码仓库管理可以看到，Android系统有近3000多个仓库，如何来管理这么多代码的编译构建以及最终生成img镜像，自然是一个非常复杂的问题。

为此，Google在 Android 7.0 (Nougat) 中引入了Sooong编译系统，旨在取代 Make。它利用 [Kati](https://github.com/google/kati/blob/master/README.md) GNU Make 克隆工具和 [Ninja](https://ninja-build.org/) 构建系统组件来加速 Android 的构建。

我画了一张示意图，帮你梳理Make、Kati、Soong、Ninja等工具的关系。

![](https://static001.geekbang.org/resource/image/8c/b6/8cdf48e23a014bbff1d75608b1c62db6.jpg?wh=2900x2044)

Android.bp与Ninja的区别在于, Android.bp的目标对象是开发者，开发者基于bp的语法规则来编写脚本， Ninja的目标是成为汇编程序，通过将编译任务并行组织，大大提高了构建速度。

我们从上图可以看出，Soong通过Android.bp文件来定义和描述一个模块的构建。Android.bp 文件很简单，它们不包含任何条件语句，也不包含控制流语句。

接下来，我以桌面的Android.bp文件为例，带你了解一下基本的bp语法规则，代码是后面这样。

```plain
//模块类型，定义构建产物的类型，例如这里的android_app就是定义生成APK类型
android_app {
    //应用名称
    name: "Launcher3",
    //编译所依赖的静态库
    static_libs: [
        "Launcher3CommonDepsLib",
    ],
    //编译源码路径
    srcs: [
        "src/**/*.java",
        "src/**/*.kt",
        "src_shortcuts_overrides/**/*.java",
        "src_shortcuts_overrides/**/*.kt",
        "src_ui_overrides/**/*.java",
        "src_ui_overrides/**/*.kt",
        "ext_tests/src/**/*.java",
        "ext_tests/src/**/*.kt",
    ],
    //编译资源路径
    resource_dirs: [
        "ext_tests/res",
    ],
    //配置混淆
    optimize: {
        proguard_flags_files: ["proguard.flags"],
        // Proguard is disable for testing. Derivarive prjects to keep proguard enabled
        enabled: false,
    },
    //配置编译相关的SDK版本号
    sdk_version: "current",
    min_sdk_version: min_launcher3_sdk_version,
    target_sdk_version: "current",
    //... ...
}

```

那么如何来触发执行编译呢？Soong支持整机编译以及指定模块编译。

我们先来看看如何完成整机的编译。当你下载完整个AOSP的源码后，进入到AOSP的根目录，输入后面的命令即可初始化编译环境。

```plain
source build/envsetup.sh

```

接下来，我们需要通过lunch命令选择要构建的目标，lunch是envsetup.sh里定义的一个命令，用来让用户选择编译目标，如下图所示，选择对应的构建目标后，就可以通过m命令触发编译。

![](https://static001.geekbang.org/resource/image/66/a9/667425d613f9c37446accef7660bc1a9.jpg?wh=2900x2044)

假如我们只要编译桌面这个APP怎么办呢？前面提到Soong也支持编译单个模块，我们可以通过编译单个模块的命令触发编译，代码是后面这样。

```plain
// 进入桌面应用所在的目录
cd packages/apps/Launcher3
// 编译当前目录下的模块，不编译依赖模块
mm

```

另外，后面这2种方式也可以触发对一个模块的独立编译。

- mma - 构建当前目录中的所有模块及其依赖项。
- mmma - 构建提供的目录中的所有模块及其依赖项。

特别需要注意的是， **Google计划使用几年的时间将 Android 构建系统迁移到 Bazel。Bazel 将取代 AOSP 中的所有现有构建系统和 build 配置系统（Make、Kati、Soong、基于 Make 的产品配置）。** 对于这种明显的技术趋势，如果团队有条件，可以考虑提前做准备。

## 自动化测试

最后，我们一起来聊聊Android系统中的自动化测试。大部分的厂商都会基于Android系统扩展定制代码，为了保证厂商扩展代码后不会影响原来系统框架的功能，能够满足兼容性的要求，Google提供了CTS以及VTS测试套件。

[CTS（Compatibility Test Suite）](https://source.android.google.cn/docs/compatibility/cts) 中文为兼容性测试套件，主要用于测试App和framework的兼容性。 [VTS（Vendor Test Suite）](https://source.android.com/docs/core/tests/vts) 中文为供应商测试套件 ，主要会自动执行 HAL 和操作系统内核测试，如下图所示。

![](https://static001.geekbang.org/resource/image/b1/71/b14405f428c88f0695a99cf9aa885071.jpg?wh=2900x2044)

以CTS为例，最新的Android 13 CTS的测试模块大概约 1068 个模块，测试用例约 269 万个。从这里可以看出，Google对自动化测试的投入还是非常大的，也侧面反映了自动化测试的重要性。

CTS的代码在AOSP源码的 [cts目录](https://cs.android.com/android/platform/superproject/+/master:cts/) 下，如果你感兴趣，可以学习一下官方的测试设计与编写，CTS中的测试主要也是使用Instrumentation以及Junit Test，与前面介绍的应用测试编写类似。

在应用开发中使用Gradle，我们可以通过testDUT、testCAT等命令来触发测试。前面提到Android源码的编译系统采用的是Soong，那么如果在Android系统中的一个模块添加测试，我们应该怎么来执行测试呢？

首先，我们可以定义测试模块的android.bp配置文件。这里我们同样以桌面应用为例来看看，bp配置文件代码是后面这样。

```plain
//配置文件模块为androidTest
android_test {
//测试模块名称
    name: "Launcher3Tests",
//测试目录
    srcs: [
        ":launcher-tests-src",
    ],
//依赖库
    static_libs: ["Launcher3TestLib"],
    libs: [
        "android.test.base",
        "android.test.runner",
        "android.test.mock",
    ],
//测试Launcher3模块
    instrumentation_for: "Launcher3",
    manifest: "AndroidManifest.xml",
    //... ...
}

```

接下来，我们就可以编写相应的测试，这与应用的编写方式一致，下面我们看看桌面测试模块里面的一个简单的测试用例。

```plain
@SmallTest
@RunWith(AndroidJUnit4.class)
public class IntSetTest {
    @Test
    public void shouldBeEmptyInitially() {
        IntSet set = new IntSet();
        assertThat(set.size()).isEqualTo(0);
    }

    @Test
    public void oneElementSet() {
        IntSet set = new IntSet();
        set.add(2);
        assertThat(set.size()).isEqualTo(1);
        assertTrue(set.contains(2));
        assertFalse(set.contains(1));
    }
}

```

最后要解决的问题就是怎么运行这些测试用例了。Google官方提供了一个运行测试的工具Atest， [Atest](https://source.android.com/docs/core/tests/development/atest) 是一个命令行工具，可让用户在本地构建、安装并运行 Android 测试，同时可以大大加快重新运行测试的速度。

如果我们需要运行整个桌面测试模块的用例，可以直接执行如下命令。

```plain
atest Launcher3Tests

```

但如果我们只想运行模块内的单个类，可以使用Module:Class的方法，命令如下。

```plain
atest Launcher3Tests：IntSetTest

```

更多关于Android系统开发的内容，如果你感兴趣可以参考官网的 [Android开源项目](https://developer.android.com/)，这个网站类似于应用开发的 [官方网站](https://developer.android.com/)。

## 总结

今天我们一起了解了Android系统开发的一些基础设施工具。与应用开发相比，系统开发更加复杂。

为了解决多仓库开发的问题，官方提供了Repo及Gerrit工具。Repo帮助我们可以去批量操作多个Git仓库，这大大简化了我们跨仓修改时代码提交同步的工作量。另外，Gerrit工具也通过Change-ID的形式帮我们关联多个仓库的提交记录，方便我们做CodeReview。

另外，为了管理整机的编译以及独立模块的编译，Android引入了Soong的编译系统，Soong通过Android.bp文件来定义和描述一个模块的构建，最后转换为Ninja文件编译最终的目标产物。

关于自动化测试，Google官方设计CTS及VTS等兼容性套件，保证了框架的兼容稳定性。针对单个模块的自动化测试，也提供了Atest测试套件，帮助我们快速执行模块内的测试。

我将应用开发与系统开发使用的工具与方式总结成了一张表，供你复习参考。

![](https://static001.geekbang.org/resource/image/29/24/29feb709cefed2a9c199f6a727bac624.jpg?wh=2789x1011)

## 思考题

感谢你学完了今天的内容，今天的思考题是这样的：Soong的编译系统也支持单独编译一个模块，但是很多厂商依旧会选择将里面的一些模块从bp编译转换为Gradle编译，你觉得这么做的好处是什么呢？

欢迎你在留言区与我交流讨论，也欢迎你把它分享给你的同事或朋友，我们一起来高效、高质量交付软件！