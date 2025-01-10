你好，我是蒋宏伟。这节课我们来聊聊 React Native 的近况。

经常有朋友问我，现阶段 React Native 的发展如何？新架构是否真的可用？我是否应该对我的业务进行升级？

今天，我们就来迅速了解下，在过去的两年中 React Native 都做了哪些改进。

## 新架构

众所周知，React Native团队在2018年时提出了新架构的设想，2022年开始发布新架构的预览版。又一年过去了，我们先来看看新架构的进展如何。

去年，新架构的预览版刚推出时，社区发布了 4 篇帖子，比较了新架构和旧架构的性能。一些人测试了ScrollView组件的渲染性能，有些人则测试了View、Text组件，还有人对比了 FlatList 和 ScrollView 场景下的渲染性能。得出的结论是： **虽然新架构在某些场景下有优势，但在更多的场景中新架构的性能却下降了。**

例如，一位社区成员在他的帖子中测试了FlatList（Virtualized）和ScrollView（Non Virtualized）组件，以及渲染导航组件和View组件的性能。

在ScrollView场景下，所有的组件都会被渲染出来，此时新架构的性能明显不如旧架构。而在FlatList 场景下，只有可视区附近的组件会被渲染出来，这时新架构的导航组件渲染性能优于旧架构，但View组件的渲染性能却弱于旧架构。

测试数据如下：

- ScrollView (毫秒)

![图片](https://static001.geekbang.org/resource/image/ef/e0/ef1a0f52b49b3d0b7de756a6e65c5de0.jpg?wh=1604x938)

- FlatList (毫秒)

![图片](https://static001.geekbang.org/resource/image/66/c1/66356cd1436c0dd7c5730c43f1a2bec1.jpg?wh=1596x922)

好在，官方已经注意到了新架构预览版的性能问题，目前已经推出了0.72 RC版本，对上述的性能问题进行了修复。性能问题的主要原因竟然是官方忘记了关闭C++层的Debug开关。此外，官方还对Text组件的操作进行了简化。

优化后，官方通过在ScrollView组件中大量渲染View、Text或Image组件（1500或5000个），以测试新架构的性能。根据官方给出的性能测试报告，Android的渲染性能提升了0%～8%，而iOS的提升更为明显，达到了13%～39%。

至此，新架构的性能在各方面都超越了旧架构。

- Google Pixel 4

![图片](https://static001.geekbang.org/resource/image/a8/0c/a803b472b1dd4179e006dc4f0701da0c.jpg?wh=1594x828)

- iPhone 12 Pro

## ![图片](https://static001.geekbang.org/resource/image/7d/c9/7d5b38441563a9350e6c9a629dff95c9.jpg?wh=1600x842)

## Hermes

在过去的两年中，React Native 进行的另外一次重大升级是，Hermes 成为了默认 JavaScript 引擎。

Hermes 是一款专为 React Native 打造的轻量级 JavaScript 引擎。2019 年，0.60 版本时，Facebook 首次将 Hermes 引擎集成到了 React Native Android 中。到了 2021 年，0.64 版本的 React Native iOS 也开始支持手动启用 Hermes 引擎。而在 2022 年，从 0.70 版本开始，Hermes 替代了 JavaScript Core，正式成为了 React Native 的默认引擎。

另外，已经有更多的开发者开始选择 Hermes 引擎。根据 Expo 公开的数据，到 2023 年 3 月，在其平台上，使用 Hermes 引擎构建的项目数量已经超过了使用 JavaScript Core 引擎的数量。因此，Expo 强烈建议 React Native 开发者和 Expo SDK 的用户们都切换到 Hermes 引擎，以便享受到 Hermes 引擎带来的诸多优势，如改进的调试体验，特别是性能改善。

![图片](https://static001.geekbang.org/resource/image/50/c4/50f0be54198d1bec4aa7692f53c9cbc4.png?wh=1502x1303)

Hermes 在设计之初，目标是优化在低端设备上运行的 React Native 应用的性能，为了实现这个目标，它采用了一种预编译策略。

在传统的 JavaScript 引擎，如 JavaScriptCore 中，JavaScript 代码在运行时会经历以下几个阶段。

1. **解析阶段**：在这个阶段，JavaScript 源代码被解析为一个抽象语法树（AST）。AST 是源代码的树状表示形式，其中每个节点代表代码中的一种结构，如函数、变量声明或表达式。
2. **编译阶段**：在这个阶段，AST 被转换成字节码，这是一种低级的、与平台无关的代码。这些字节码可以被 JavaScript 引擎直接执行。
3. **优化阶段**：在这个阶段，JavaScript 引擎可能会对字节码进行进一步的优化，以提高运行时性能。例如，引擎可能会使用即时（JIT）编译器将频繁执行的字节码片段编译成机器代码，以减少解释字节码的开销。

然而，Hermes 引擎可以将解析和编译的操作提前到构建阶段，当你构建你的 React Native 应用时，它已经完成了解析和编译的过程，并直接生成了字节码。因此，运行时只需要执行字节码，大大节省了解析和编译的时间。

**那么Hermes究竟快多少呢？**

在启动性能上，使用字节码技术的 Hermes 明显优于 JavaScriptCore。根据 CallStack 团队在 2021 年公开的实测数据，对于冷启动的可交互时间（TTI），在三款不同的 iOS 机型上，Hermes 比 JavaScriptCore 快了 36%～40%。我们的团队在今年也进行了类似的启动时间性能测试，结果显示，iOS 和 Android 的性能分别提升了 50% 和 48%。

![图片](https://static001.geekbang.org/resource/image/dd/02/dd4425ddf22a9f71ee4b7ab8072fbf02.jpg?wh=1600x842)

不过，尽管 Hermes 引擎带来了显著的性能提升，但在 iOS 上启用它需要谨慎。

国内的 React Native 应用普遍配备了热更新技术，然而热更新与 Hermes 的字节码技术并不兼容。值得注意的是，根据 Apple 的政策，Apple 明确规定只允许使用 JavaScriptCore 引擎动态执行脚本，使用 Hermes 引擎动态执行字节码可能会导致违规。因此， **我并不推荐你在 iOS 上使用 Hermes 进行热更新。**

我更推荐的做法是，在 Android 上使用 Hermes，并开启字节码。而在 iOS 上继续使用 JavaScriptCore。这样也能从 Hermes 引擎带来的性能优化中获益。

## FlashList

FlatList 是 React Native 提供的默认列表组件，然而，这个组件在众多设备上常常遭遇性能问题。在 [第 08 讲](https://time.geekbang.org/column/article/506825) 中，我推荐了一款替代组件——RecyclerListView。近两年来，RecyclerListView 的作者加入了 Shopify，并在原有的 RecyclerListView 基础上，打造了一个更易用的组件，名为 [FlashList](https://shopify.github.io/flash-list/docs/usage)。

过去，我向你解释过 RecyclerListView 的工作原理，其基本思路是通过调整 Absolute 布局元素的 Top 位置值，实现元素复用。然而，要确定每个列表项 Item 的 Top 位置值，就必须先知道每个 Item 的 Height 值。因此，开发者需要手动创建一个 LayoutProvider 类，该类需要对 Item 进行分类，并为每一类 Item 设置固定高度。

开发者需要定义一个 LayoutProvider 类，代码示例如下：

```plain
const _layoutProvider = new LayoutProvider(
  index => {
    if (index % 3 === 0) {
      return ViewTypes.FULL;
    } else {
      return ViewTypes.HALF_RIGHT;
    }
  },
  (type, dimension) => {
    switch (type) {
      case ViewTypes.HALF_RIGHT:
        dimension.width = width / 2;
        dimension.height = 160;
        break;
      case ViewTypes.FULL:
        dimension.width = width;
        dimension.height = 140;
        break;
    }
  },
);

```

这样虽然解决了问题，但实际上开发过的同学都痛苦不已。对于复杂的业务需求，Item 类型太多了，文字高度也不固定。而且一旦计算错误，要定位是哪个 Item 导致的问题，是十分困难的。

而 FlashList 只通过一个简单的参数 estimatedItemSize 就解决了这个问题。FlashList 的示例代码如下：

```plain
import React from "react";
import { View, Text, StatusBar } from "react-native";
import { FlashList } from "@shopify/flash-list";

const DATA = [
  {
    title: "First Item",
  },
  {
    title: "Second Item",
  },
];

const MyList = () => {
  return (
    <FlashList
      data={DATA}
      renderItem={({ item }) => <Text>{item.title}</Text>}
      estimatedItemSize={200}
    />
  );
};

```

那 FlashList 是如何做到的呢？

**是渲染两次，不过是直接在 Native 层渲染两次。**

前面我们提到，要计算每个列表项 Item 的 Top 位置值，就必须知道每个 Item 的 Height 值。FlashList 第一次渲染时，在 Native 层，通过预估的 Item Height 值，也就是 estimatedItemSize，计算出每个列表项预估的 Top 值，进行渲染。渲染后，获取真实的 Item Height 值，再计算出实际的 Top 值，然后再渲染一次。

由于两次渲染之间没有 JS 与 Native 的通信，是直接发生在 Native 层的，速度非常快，正常看是看不出抖动的。

RecyclerListView 是纯 JS 代码，FlashList 在 RecyclerListView 之上借助了 Native 代码，借助两次快速渲染（如果无需高度修正就是一次渲染），实现了自动布局。

理论上，一次渲染的性能必然大于两次渲染。即便 FlashList 是直接在 Native 层渲染两次，它依旧是多了一次渲染的消耗。因此，如果你能正确地给出每个 Item 的 Height 值，就不要粗略地估计一个 estimatedItemSize 值，然后让 FlashList 帮你去自动纠正。通过二次渲染进行布局纠正，肯定是有性能损耗的。

在性能达标的前提下，列表 Item 有文字内容，其高度是动态，计算高度非常复杂，那么 **让 FlashList 帮你自动去计算布局，也不失为一种好的策略**。这能很大程度地节约开发成本。

性能上，官方未给出 FlashList 和 RecyclerListView 的性能对比，给出的是 FlashList 和 FlatList 的性能对比，也就是 Shopify 团队提供的 List 组件和 React Native 默认的 List 组件的性能对比。在 Twitter 场景下，整体上 FlatList 只拿到了 39 分，而 FlashList 拿到了 89 分。

从性能截图中也可以看出，FlatList 的 UI FPS 帧率绝大部分时间保持在 55 帧率以下，而 FlashList 绝大部分时间保持在 55 帧率以上。

![图片](https://static001.geekbang.org/resource/image/a7/1c/a7ef03f9938fcedd020c8ae1b321141c.png?wh=1486x708)

## 总结

近两年，新架构预览版的推出和默认引擎 Hermes 的应用，无疑是亮点，这两项技术从根本上为 React Native 带来了显著的性能提升。

在生态方面，FlashList 组件的推出显著降低了高性能列表组件的开发成本。FlashList 的使用方式与 FlatList 组件相似，因此从 FlatList 迁移到 FlashList 的成本极低，同时可以显著提升 FPS 方面的性能。

FlashList 不依赖特定版本，只要你能使用，就直接上手吧。至于 Hermes 的字节码技术，你可以在 Android 平台上先行使用，但如果在 iOS 上使用热更新，还是建议放弃，因为下架的风险实在太大。至于新架构，你可以尝试使用，但如果想大规模推广，最好等到正式版发布后再开始。

## 思考题

这两年，你还观察到了 React Native 的哪些重要升级？

欢迎在留言区分享你的看法、交流学习心得或者提出问题，如果觉得有收获，也期待你把今天的内容分享给更多的朋友！