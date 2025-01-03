你好，我是宝玉。如果你所在的团队在日常的软件项目开发中，能科学地应用软件工程的知识，让你的项目能持续取得进展，最终交付的产品也有很好的质量，那么是一件非常幸运的事情。

然而现实中，很多人并没有机会去参与或观察一个好的项目是什么样子的，也没机会去分析一个好的项目是如何科学应用软件工程的。

好在现在有很多优秀的开源项目，不仅代码是公开的，它们整个项目的开发过程都是公开的。通过研究这些开源项目的开发，你能从中学习到一个优秀项目对软件工程的应用，加深你对软件工程知识的理解，进而应用到你自己的项目实践中。

我想你对VS Code应该不陌生，它是一个非常优秀的编辑器，很多程序员包括我非常喜欢它。VS Code也是一个大型的开源项目，整个开发过程非常透明，所以今天我将带你一起看一下VS Code是如何应用软件工程的，为什么它能构建出这么高质量的软件。

## 如何从VS Code的开发中学习软件工程？

也许你会很好奇，平时也去看过VS Code的网站，但并没有提到软件工程的呀？

是的，VS Code的网站并没有特别突出这些信息，但是如果你有心，可以找到很多有价值的信息，它的整个开发过程都是公开透明的。

比如通过它项目的 [WIKI](http://github.com/microsoft/vscode/wiki) 和 [博客栏目](http://code.visualstudio.com/blogs)，可以看到项目的计划、项目开发流程、测试流程、发布流程等信息。通过它的 [GitHub](http://github.com/microsoft/vscode) 网站，你可以看到团队是如何基于分支开发，开发完成后提交Pull Request，团队成员如何对代码进行审核，合并代码后如何通过持续集成运行自动化测试。

除此之外，团队成员在网上也有一些对于VS Code开发的分享，比如说VS Code主要负责人Erich Gamma 2016年在GOTO技术大会上有一个专门关于VS Code的 [主题演讲](http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2F1727858283%2FHy6b647zm&domain=.weibo.com&sudaref=https%3A%2F%2Fshimo.im%2Fdocs%2FCTa8mSsYEcc8KgOg&ua=php-sso_sdk_client-0.6.28&_rand=1560153401.1655)。

也许你还会想问：这些信息我也知道，也能从网上看到，但怎么通过这些信息去观察和学习它跟软件工程相关的部分呢？

不知道你是否还记得，在我们专栏的第一篇文章《 [01 \| 到底应该怎样理解软件工程？](http://time.geekbang.org/column/article/82848)》中提到了： **软件工程的核心，就是围绕软件项目开发，对开发过程的组织，对方法的运用，对工具的使用。** 所以当我们去观察一个软件项目，我们就可以去看它的开发过程是怎么被组织的？运用了哪些软件工程的方法？使用了哪些工具？

接下来，我就带你一起从以下几个方面分析VS Code对软件工程的应用：

- VS Code的开发过程；
- 团队的分工角色；
- 各个阶段如何进行；
- 使用了哪些工具。

## VS Code的开发迭代过程

如果你是VS Code的用户，你会发现VS Code每个月都会有新版本的更新，每次更新都会有很多新酷的功能。这是因为VS Code每个版本的开发周期是4周，每四周都会发布一个新的版本。

从开发模式来说，VS Code采用的是快速迭代的开发模式，每四周一个迭代。那么这四周迭代的工作都是如何进行的呢？

- 第一周

每个版本的第一周，通常是起着承上启下的作用，一方面要准备新版本，一方面还要对上一个版本的工作进行收尾。

在这一周里，开发团队要去做一些偿还技术债务的事情，比如说重构代码，优化性能。所以如果你的团队抱怨说没有时间做偿还技术债务的事情，不妨也去学习VS Code团队，定期留出专门的时间，做偿还技术债务的事情。

另一个主要工作就是一起讨论下一个迭代要做的功能。其实这有点类似于敏捷开发中，每个Sprint开始之前的项目计划会议。

如果上一个版本开发完成的功能，发现了严重Bug，第一周还要去修复这些紧急Bug。

- 第二周和第三周

第二周和第三周主要工作就是按照计划去开发，一部分是开发新功能，一部分是修复Bug，所有的Bug都是通过GitHub的Issue来分配和跟踪的。

团队成员每天还要先检查一下分配给自己的Issue，如果遇到线上版本紧急的Bug，要优先修复。

- 第四周

VS Code团队把最后一周叫End game，你可以理解为测试周，因为这一周只做测试和修复Bug。

这一周要测试所有新的Feature和验证已经修复的Bug，确保被修复。同时还要更新文档和写Release Notes。

测试完成后就发布预发布版本，这个预发布版本会先邀请一部分人使用，比如说微软内部员工、热心网友。

- 下一个迭代第一周

每个迭代开发测试完成的版本，会放在下一个迭代的第一周发布。如果在预发布版本中发现严重Bug，需要在第一周中修复。

如果没有发现影响发布的Bug，那么第一周的周三左右就会正式发布上一个迭代完成的版本。

前面我在专栏文章《 [40 \| 最佳实践：小团队如何应用软件工程？](http://time.geekbang.org/column/article/98985)》中，建议小团队可以缩短迭代周期到2-4周，有同学担心不可行，但你看VS Code这样稳定的4周迭代，不但可行，而且还是VS Code能保持每月发布一个新版本的关键所在。

## VS Code团队的角色和分工

VS Code的开发团队现在大约20人左右，一半在苏黎世，一半在西雅图。整个团队基本上都是开发人员，结构很扁平。

从分工上来说，在开发新功能和修复Bug的时候，会有一些侧重，比如有人侧重做Git相关的功能，有人侧重做编辑器部分功能。这样有侧重的分工对于提升开发效率是有好处的。

从角色上来说，除了开发，还有主要有两种角色： [Inbox Tracker](http://github.com/microsoft/vscode/wiki/Issue-Tracking#inbox-tracking) 和 [Endgame Master](http://github.com/microsoft/vscode/wiki/Running-the-Endgame#duties-of-the-endgame-master)。这两种角色在每个迭代的时候是轮值的，每个人都有机会去担任这两个角色。

- Inbox Tracker

Inbox Tracker的主要任务就是收集、验证、跟踪Bug。但这个工作对于VS Code团队来说可不轻松，现在Issue的总量已经超过了5000，每天提交的新的Issue的量大概有100左右。所以VS Code团队写了一个机器人叫 [VSCodeBot](http://github.com/apps/vscodebot)，可以帮助对Issue先自动处理，打标签或回复，然后Inbox Tracker再对剩下的Issue进行人工处理。

Inbox Tracker要检查新提交的Issue是不是一个真正的Bug，如果是提问，建议到StackOverflow去问，如果是Bug，打上Bug的标签，并指派给相应模块的负责人。

- Endgame Master

VS Code团队是没有专职的测试人员的，所有的测试工作都是开发人员自己完成。在每一个迭代中。Endgame Master在这里就很重要，要组织管理整个迭代的测试和发布工作。

Endgame Master在每个迭代测试之前，根据迭代的开发计划制定相应的测试计划，生成Check List，确保每一个新的功能都有在Check List中列出来。

因为VS Code团队没有专职测试，为了避免开发人员自己测试自己的代码会存在盲区，所以自己写的功能都是让其他人帮忙测试。Endgame Master一个主要工作就是要将这些测试项分配给团队成员。

最后整个测试计划会作为一条GitHub Issue发出来给大家审查。比如说这是某一个月的 [Endgame计划](http://github.com/microsoft/vscode/issues/74412)。

团队的日常沟通是通过Slack，在测试期间，Endgame Master需要每天把当前测试进展同步给所有人，比如说总共有多少需要测试的项，哪些已经验证通过，哪些还没验证。

## VS Code的各个阶段

接下来，我们来按照整个开发生命周期，从需求收集和版本计划、设计开发、测试到发布，来观察VS Code各个阶段是如何运作的。

**1\. VS Code的需求收集和版本计划**

VS Code每次版本发布，都能为我们带来很多新酷的功能体验，那么这些功能需求是怎么产生的呢？又是怎么加入到一个个版本中的呢？

VS Code的需求，一部分是团队内部产生的；一部分是从社区收集的，比如GitHub、Twitter、StackOverflow的反馈。最终这些收集上的需求，都会通过GitHub的Issue管理起来。如果你在它的GitHub Issue中按照 [feature-request](http://github.com/Microsoft/vscode/issues?q=is%3Aopen+is%3Aissue+label%3Afeature-request+sort%3Areactions-%2B1-desc) 的标签去搜索，可以看到所有请求的需求列表。

VS Code每半年或一年会对下一个阶段做一个 [Roadmap](http://github.com/microsoft/vscode/wiki/Roadmap)，规划下一个半年或一年的计划，并公布在GitHub的WIKI上，这样用户可以及时了解VS Code的发展，还可以根据Roadmap上的内容提出自己的意见。

大的RoadMap确定后，就是基于大的RoadMap制定每个迭代具体的开发计划了。前面已经提到了，在每个迭代的第一周，团队会有专门的会议讨论下一个迭代的开发计划。在VS Code的WIKI上，也同样会公布所有确定了的 [迭代计划](http://github.com/microsoft/vscode/wiki/Iteration-Plans)。

那么，有了功能需求和Bug的Issue，也有了迭代的计划，怎么将Issue和迭代关联起来呢？

GitHub的Issue管理有一个Milestone的功能，VS Code有四个主要的Milestone。

- 当前迭代：当前正在开发中的Milestone；
- On Deck：下一个迭代对应的Milestone；
- Backlog：还没开始，表示未来要做的；
- Recovery：已经完成的迭代，但是可能要打一些补丁。

![](https://static001.geekbang.org/resource/image/2c/1a/2cd5a5c18253658323dd296ec751be1a.png?wh=1920*1494)

（图片来源： [VSCode Milestones](http://github.com/microsoft/vscode/milestones)）

**2\. VS Code的设计和开发**

VS Code的架构设计现在基本上已经定型，你在它的WIKI和博客上还能看到很多VS Code架构和技术实现的分享。

在每个迭代开发的时候，一般小的功能不需要做特别的架构设计，基于现有架构增加功能就好了。如果要做的是大的功能改造，也需要有设计，负责这个模块开发的成员会先写设计文档，然后邀请其他项目成员进行Review，并给出反馈。

VS Code的开发流程也是用的 [GitHub Flow](http://guides.github.com/introduction/flow/)，要开发一个新功能或者修复一个Bug，都创建一个新的分支，开发完成之后提交PR。PR合并之前，必须要有核心成员的代码审查通过，并且要确保所有的自动化测试通过。

对于GitHub Flow的开发流程，我在专栏文章《 [30 \| 用好源代码管理工具，让你的协作更高效](http://time.geekbang.org/column/article/93757)》中有详细的介绍。你也可以在VSCode 的 [Pull requests](http://github.com/microsoft/vscode/pulls) 中看到所有提交的PR，去看看这些PR是怎么被Review的，每个PR的自动化测试的结果是什么样的。通过自己的观察，去印证专栏相关内容的介绍，同时思考是否有可以借鉴到你自己项目中的地方。

VS Code对自动化测试代码也是非常重视，在实现功能代码的时候，还要加上自动化测试代码。如果你还记得专栏文章《 [29 \| 自动化测试：如何把Bug杀死在摇篮里？](http://time.geekbang.org/column/article/93405)》中的内容：自动化测试有小型测试、中型测试和大型测试。VS Code的自动化测试也分为单元测试、集成测试和冒烟测试。

VS Code的 [CI（持续集成](http://dev.azure.com/vscode/VSCode)）用的是微软自己的Azure DevOps，每一次提交代码到GitHub，CI都会运行单元测试和集成测试代码，对Windows/Linux/macOS三个操作系统分别运行测试。在 [持续集成](http://dev.azure.com/vscode/VSCode) 上可以直观地看到测试的结果，VS Code现在有大约4581个单元测试用例，运行一次1分钟多；集成测试466个，运行一次大约3分钟。

![](https://static001.geekbang.org/resource/image/ca/9a/ca8dc2cc12e423d92020a7a5a964c99a.png?wh=1920*1629)（图片来源： [VSCode的持续集成工具Azure DevOps](http://dev.azure.com/vscode/VSCode)）

如果你的团队还没有开始相应的开发流程，没有使用持续集成工具，不妨学习VS Code，使用类似于GitHub Flow的开发流程，使用像Azure DevOps这样现成的持续集成工具。

**3\. VS Code的测试**

前面提到了，迭代的最后一周是End game，这一周就是专门用来测试的，并且有轮值的Endgame Master负责整个测试过程的组织。

具体测试的时候，大家就是遵循Endgame Master制定好的测试计划，各自按照Check List逐一去检查验证，确保所有的新功能都通过了测试，标记为修复的Bug真的被修复了。对于验证通过的Bug，在对应的Issue上打上verified的标签。

在人工测试结束后，Endgame Master就需要跑 [冒烟测试](http://github.com/Microsoft/vscode/wiki/Smoke-Test)，确保这个迭代的改动不会导致严重的Bug发生。

如果你的团队也没有专职测试，可以学习VS Code这样的做法：留出专门的测试阶段，事先制定出详细的测试计划，把所有要测试的项都通过测试跟踪工具跟踪起来，开发人员按照测试计划逐一测试。

**4\. VS Code的发布流程**

在Endgame测试后，就要从master创建一个release分支出去，比如说 release/1.10 ，后面的预发布版本和正式版本包括补丁版本都将从这个 release 分支发布。

如果在创建release分支后发现了新的Bug，那么对Bug修复的代码，要同时合并到master和release分支。每一次对Release的代码有任何改动，都需要重新跑冒烟测试。

在Release分支的代码修改后的24小时之内，都不能发布正式版本。每次Release代码修改后，都会发布一个新的预发布版本，邀请大约两万的内部用户进行试用，然后看反馈，试用24小时后没有什么问题就可以准备发布正式版本。

发布正式版本之前，还要做的一件事，就是Endgame master要写Release Notes，也就是你每次升级VS Code后看到的更新说明，详细说明这个版本新增了哪些功能，修复了哪些Bug。

如果版本发布后，发现了严重的线上Bug，那么就要在Release分支进行修复，重新生成补丁版本。

除此之外，VS Code每天都会将最新的代码编译一个最新的版本供内部测试，这个版本跟我们使用的稳定版Logo颜色不一样，是绿色的Logo。VS Code内部有“吃自己狗粮”（eat your own dog food）的传统，也就是团队成员自己会使用每天更新的测试版本VS Code进行开发，这样可以在使用过程中及时发现代码中的问题。

![](https://static001.geekbang.org/resource/image/a6/2b/a6540bfea13c3679e3a4dad78d9ae02b.png?wh=1920*1080)

（图片来源： [The Journey of Visual Studio Code](http://gotocon.com/dl/goto-amsterdam-2016/slides/ErichGamma_TheJourneyOfALargeScaleApplicationBuiltUsingJavaScriptTypeScriptNodeElectron100OSSComponentsAtMicrosoft.pdf)）

像VS Code这样的发布流程，通过创建Release分支可以保障有一个稳定的、可以具备发布条件的代码分支；通过预发布内部试用的机制，有问题可以及时发现，避免造成严重的影响。

关于发布流程的内容，你也可以将VS Code的 [发布流程](http://github.com/microsoft/vscode/wiki/Release-Process) 对照我们专栏文章《 [35 \| 版本发布：软件上线只是新的开始](http://time.geekbang.org/column/article/96289)》中的介绍，加深理解。

## VS Code使用的工具

VS Code的源代码管理工具就是基于GitHub，整个开发流程也完全是基于GitHub来进行的。

它的任务跟踪系统是用的GitHub的Issue系统，用来收集需求、跟踪Bug。通过标记不同的Label来区分 [Issue的类型和状态](http://github.com/microsoft/vscode/wiki/Issue-Grooming#categorizing-issues)，比如bug表示Bug，feature-request表示功能请求，debt表示技术债务。通过Issue的Milestone来标注版本。

VS Code的持续集成工具最早用的是 [Travis CI](http://travis-ci.org) 和 [AppVeyor](http://www.appveyor.com)，最近换成了微软的 [Azure Pipelines](http://azure.microsoft.com/en-us/blog/announcing-azure-pipelines-with-unlimited-ci-cd-minutes-for-open-source/)，在他们的Blog上有一篇文章《 [Visual Studio Code using Azure Pipelines](http://code.visualstudio.com/blogs/2018/09/12/engineering-with-azure-pipelines)》专门解释了为什么要迁移过去。

VS Code的文档一部分是用的GitHub的WIKI系统，一部分是它网站的博客系统。WIKI主要是日常项目开发、维护的操作说明，博客上更多的是一些技术分享。

另外VS Code团队还自己开发了一些小工具，比如说帮助对Issue进行自动处理回复的GitHub机器人VSCodeBot。

通过这些工具的使用，基本上就可以满足像VS Code这样一个项目的日常运作。像这些源代码管理、任务跟踪系统、持续集成工具的使用，在我们专栏也都有相应的文章介绍，你也可以对照着文章的内容和VS Code的使用情况加以印证，从而加深对这些工具的理解，更好把这些工具应用在你的项目中。

## 总结

当你日常在看一个开源项目的时候，不仅可以去看它的代码，还可以去观察它是怎么应用软件工程的，不仅可以加深你对软件工程知识的理解，还能从中学习到好的实践。

比如观察一个软件项目的开发过程是怎么被组织的，团队如何分工协作的，运用了哪些软件工程的方法，以及使用了哪些工具。

VS Code使用的是快速迭代的开发模式，每四周一个迭代：

- 第一周：偿还技术债务，修复上个版本的Bug，制定下一个版本的计划；
- 第二、三周：按照计划开发和修复Bug；
- 第四周：测试开发完成的版本；
- 下一迭代第一周：发布新版本。

在团队分工上，VS Code的团队很扁平，没有专职测试，通过轮值的Inbox Tracker和Endgame Master来帮助团队处理日常Issue和推动测试和发布工作的进行。

在工具的使用方面，VS Code使用的是GitHub托管代码，基于GitHub Flow的开发流程使用。还有使用Azure DevOps作为它的持续集成系统。

通过观察对VS Code对软件工程知识点的应用，再对照专栏中相关文章的介绍，可以帮助你更好的理解这些知识点，也可以借鉴它们好的实践到你的项目开发中。

## 课后思考

你可以尝试自己去观察一遍VS Code项目对软件工程知识的应用，得出自己的结论。你也可以应用这样的观察分析方法，去观察其他你熟悉的优秀开源项目，比如像Vue、React，看它们是怎么应用软件工程的。欢迎在留言区与我分享讨论。

感谢阅读，如果你觉得这篇文章对你有一些启发，也欢迎把它分享给你的朋友。