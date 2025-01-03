你好，我是徐昊，今天我们来继续学习AI时代的软件工程。

上节课我们介绍了为什么用户故事是大语言模型（Large Language Model，LLM）时代提取业务知识的最佳形态，以及一些编写用户故事的最佳实践。由于用户故事侧重于定义问题 **，** 而LLM往往更擅长提供解决方案，似乎对于用户故事而言，LLM并不能提供太多的帮助。

然而LLM仍然可以在用户故事编写的环节给予我们帮助。主要是从验收条件入手，帮助我们提取整体解决方案，完善用户故事或是将整体解决方案的细节补充到用户故事中去。

那么今天我们就来看一下，如何利用LLM帮助我们更好地编写用户故事。

## 验收条件与用户故事

用户故事的特质可以总结为3C，即Card，Conversation和Confirmation。Card是指用户故事的物理载体，即索引卡（Index Card）。因为索引卡面积有限，不能事无巨细地写下所有需求信息，只能关注最重要的信息也就是用户价值。其他的不可言说知识则通过对话（Conversation）的这种社交活动传播。

在对话过程中，最重要的目标就是明确这张故事卡的验收条件（Acceptance Criteria）有哪些，也就是如何确认（Confirmation）卡确实做完了。

因而，验收条件是用户故事（User Story）的重要组成部分，用于帮助开发团队和客户明确产品或功能的期望表现、功能要求和可接受的标准。

我们知道用户故事不是凭空产生的，而是根据用户的角色画像、整体解决方案以及用户旅程，拆分出来的。那么验收条件，实际就是在当前用户故事语境下，用户旅程或整体解决方案的细化和拆分。

![](https://static001.geekbang.org/resource/image/4a/91/4a551e33a58955bd1079f5d891e64391.jpg?wh=2000x1125)

在不知道用户旅程和整体解决方案之前，我们是无法给出验收条件的。仍然以我们前面的用户故事为例：

> **作为** 学校的教职员工（ **As** a faculty），
>
> **我希望** 学生可以根据录取通知将学籍注册到教学计划上（ **I want** the student to be able to enroll in an academic program with given offer），
>
> **从而** 我可以跟踪他们的获取学位的进度（ **So that** I can track their progress）

由于我们不知道这个故事在用户旅程中处于哪个位置，以及整体解决方案是什么，我们就无法通过验收条件明确这张卡怎么算“做完”。因而，我们需要给出一定的业务上下文，比如：

> 整个学籍管理系统是一个Web应用；
>
> 当教职员工发放录取通知时，会同步建立学生的账号；
>
> 学生可以根据身份信息，查询自己的账号；
>
> 在报道注册时，学生登录账号，按照录取通知书完成学年的注册；

有了上下文之后，我们才能给出相应的验收条件。通常，验收条件遵循 **假设/操作/结果（Given/When/Then）** 格式，这个格式能帮我们清晰地描述功能的期望行为。

假设（Given）描述了在什么条件下功能应该被测试。这些条件可能包括系统的状态、前提条件或输入；操作（When）描述了在给定条件下，用户将执行的操作或事件；结果（Then）描述了功能应该如何响应用户的操作或事件，也就是功能的期望结果。

比照这个格式并结合业务上下文，我们可以为前面的用户故事编写这样的验收条件：

> Given 未完成注册的学生登录系统（用户旅程：在报道注册时，学生登录账号）
>
> When 学生在注册页面点击“注册”按钮时（整体解决方案：整个学籍管理系统是一个Web应用）
>
> Then 完成当前学期的学籍注册 （用户故事： **我希望** 学生可以根据录取通知将学籍注册到教学计划上）

可以看到，这个验收条件中，我们包含了用户旅程，整体解决方案和用户故事中提及的功能。

需要注意的是，每一张用户故事的范围，需要参照其他用户故事才能确定。比如，下面这个验收条件：

> Given 未完成注册的学生
>
> When 学生登录系统
>
> Then 收到提醒并转跳到注册页面
>
> 它是否是当前用户故事的验收条件，取决于是否存在这样一张用户故事：

> **作为** 学生（ **As** a student），
>
> **我希望** 登录之后接收到注册的通知（ **I want** to get a notification after login），
>
> **从而** 我可以不会错过学期注册的期限（ **So that** I would not miss the registration）

如果存在这样的独立故事，那么这个验收条件就不在当前故事卡之中。如果不存在，那么有可能就需要包含这个验收条件。因而，用户故事的功能范围并不是固定的。随着卡片的拆分和细化，每个用户故事的范围都可能发生改变。只有沟通过的验收条件，才表示用户故事的具体范围。

因此，还存在一种说法， **用户故事只是业务价值的占位符（Placeholder）。** 在沟通确认之前，它只表示用户想要达到的某种目的，而具体的功能需要在沟通中才能细化。

## 使用LLM辅助用户故事编写

如果用户故事只是占位符的话，那么我们在使用用户故事表达需求的时候，到底传递了哪些不可言说的知识呢？

答案是显而易见的，是 **整体解决方案** 和 **用户旅程**。我们是否能够有效理解用户故事， **重点并不在故事本身，而在于对于整体解决方案和用户旅程的掌握程度**。

按照这个思路，通过LLM辅助我们编写用户故事的前提是，我们已经有效地提取了 **整体解决方案** 和 **用户旅程**。我们可以通过一个 **推理行动模式（Reasoning and act，ReAct）的变体想-问-答（TQA，Think-Question-Answer）**，使用LLM辅助我们编写用户故事。

由于LLM不善于定义问题，那么定义问题的部分仍需留给人来完成，因而TQA的整体思路这样的：

1. 为LLM提供整体解决方案和用户旅程作为业务背景说明；
2. 提供相应的用户故事卡；
3. 让LLM根据业务背景说明，考虑对于给定的用户故事，还有哪些不清楚的地方，并根据这些不清楚的地方进行提问，并由人来回答；
4. 当LLM觉得已经了解了所有的细节，那么LLM会为当前的用户故事编写验收条件。

那么让我们看一个具体的例子。TQA的形式无法通过ChatGPT直接使用，需要构造一个Agent调用ChatGPT的API完成。

![](https://static001.geekbang.org/resource/image/10/76/10d6b699347f2b25e334d03ac4a1f476.jpg?wh=2068x1709)

如上图所示，这个Agent分成三个部分，分别是用户故事、业务上下文以及与LLM交互的部分。

后面这个例子展示了我们如何利用这个Agent，让LLM尝试理解我们给出的用户故事，并对用户故事进行提问。

![](https://static001.geekbang.org/resource/image/91/87/91cyy9afba6115f4651340798e6cbb87.jpg?wh=2068x1724)

我们与LLM的问答摘录如下， H表示人（Human），L表示LLM：

> 让我们来谈谈这个故事的情节
>
> L: 登记教学计划是否意味着该学生已正式入学？
>
> H: 是的，学生们每年都要注册到教学计划中
>
> L: 录取通知书是电子邮件还是实体邮件？
>
> H：两个都有。教职员工会在学生登录系统之前创建帐户
>
> L：学校是否有专门的系统或平台来跟踪学生的学位进度？
>
> H: 对，这就是我们讨论的这个系统
>
> L：学校需要学生提供哪些具体信息才能注册入学？
>
> H：姓名、身份证以及提供给他们的录取通知书
>
> L：学生是否必须在特定的时间内注册？
>
> H：对，在每个学年的第一学期之前

在一系列问题之后，LLM也给出了它认为的验收条件：

> Scenario 1:
>
> Given: 学生已经收到他们的电子录取通知书（The student has received their admission notice electronically）
>
> When: 学生使用提供用户名密码登录到系统（The student logs into the system using their provided credentials）
>
> Then: 提示学生注册，并提供他们的姓名、身份证和课程（The student is prompted to register their enrollment in the teaching plan by providing their name, ID, and the program they were offered）
>
> Scenario 2:
>
> Given: 学生已经收到他们的纸质录取通知（The student has received their admission notice through physical mail）
>
> When: 学生使用提供用户名密码登录到系统（The student logs into the system using their provided credentials）
>
> Then: 提示学生注册，并提供他们的姓名、身份证和课程（The student is prompted to register their enrollment in the teaching plan by providing their name, ID, and the program they were offered)
>
> Scenario 3:
>
> Given: 学生已经完成注册（The student has registered their enrollment in the teaching plan）.
>
> When: 学校希望通过系统追踪他们获得学位的进度（The school wants to track the progress of the student’s degree attainment）
>
> Then: 学校访问当前系统，并看到他们的进度（The school accesses the current system and views the student’s degree progress）
>
> Scenario 4:
>
> Given: 学校为注册设定了的截止日期（The school has set a deadline for students to register their enrollment in the teaching plan）
>
> When: 目前已经超过截止日期（The deadline for registration passes）
>
> Then: 没有完成注册的学生就不能继续注册了（Students who have not registered their enrollment in the teaching plan are no longer eligible to continue their studies）

## 小结

我们感受到最直观的不同是， **LLM主要负责提问，而不是回答问题**。LLM提问的问题主要是关于解决方案的，这是一个什么系统？有哪些流程等等。

针对LLM提出的问题，我们有三种不同的应对方式：

1. 如果LLM提出的问题，包含了对于基础概念或流程的误解， **那么我们要重新定义和修改业务背景。**
2. 如果LLM提出的问题，包含了对于操作的误解， **那么我们要重新修改用户故事。**
3. 如果LLM提出的问题，仅仅是关于交互细节的，那么我们只需要在会话中回答这些细节就可以了。

这三种应对方式也分别代表了三种通过LLM辅助用户故事编写的形式：通过LLM提取不可言说的业务知识，修改用户故事以及补充完善验收条件。

TQA是我在去年（2023年）年初的时候发明的一种LLM交互模式，在下一节课中，我们将详细讲解如何实现基于TQA的AI Agent。

## 思考题

当我们提取不可言说业务知识时，LLM会问怎样的问题？

欢迎你在留言区分享自己的思考或疑惑，我们会把精彩内容置顶供大家学习讨论。