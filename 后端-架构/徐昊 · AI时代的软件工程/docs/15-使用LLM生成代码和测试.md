你好，我是徐昊，今天我们来继续学习AI时代的软件工程。

通过前面的学习，我们了解了如何使用大语言模型（Large Language Model，LLM）辅助进行业务知识管理。接下来，我们继续学习使用LLM辅助软件交付的整体流程，以及其中涉及到的知识管理。

从今天这节课开始，我们将进入如何使用LLM辅助软件开发的环节。让我们从一个例子开始。

## 命令行参数解析

我们所使用的例子源自Robert C. Martin的 *Clean Code* 第十四章，也是我的测试驱动专栏[《TDD项目实战70讲》](https://time.geekbang.org/column/intro/100109401)讲过的第一个项目，需求描述如下：

> 我们中的大多数人都不得不时不时地解析一下命令行参数。如果我们没有一个方便的工具，那么我们就简单地处理一下传入main函数的字符串数组。有很多开源工具可以完成这个任务，但它们可能并不能完全满足我们的要求。所以我们再写一个吧。  
>    
> 传递给程序的参数由标志和值组成。标志应该是一个字符，前面有一个减号。每个标志都应该有零个或多个与之相关的值。例如：  
>    
> -l -p 8080 -d /usr/logs  
>    
> “l”（日志）没有相关的值，它是一个布尔标志，如果存在则为true，不存在则为false。“p”（端口）有一个整数值，“d”（目录）有一个字符串值。标志后面如果存在多个值，则该标志表示一个列表：  
>    
> -g this is a list -d 1 2 -3 5  
>    
> “g” 表示一个字符串列表\[“this”, “is”, “a”, “list”]，"d"标志表示一个整数列表\[1, 2, -3, 5]。  
>    
> 如果参数中没有指定某个标志，那么解析器应该指定一个默认值。例如，false代表布尔值，0代表数字， `""` 代表字符串，\[]代表列表。如果给出的参数与模式不匹配，重要的是给出一个好的错误信息，准确地解释什么是错误的。  
>    
> 确保你的代码是可扩展的，即如何增加新的数值类型是直接和明显的。
<div><strong>精选留言（5）</strong></div><ul>
<li><img src="http://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKkdXSdtiahZTGT2ArFNGa93OaDf9dRE96Vz82YwUDsFJOWXYkGFibkjNHhQ7CPITERuicv6MHKS2Kxw/132" width="30px"><span>穿靴子的加菲猫</span> 👍（0） 💬（1）<div>“l”（日志）没有相关的值，它是一个布尔标志，如果存在则为 true，不存在则为 false。“p”（端口）有一个整数值，“d”（目录）有一个字符串值。标志后面如果存在多个值，则该标志表示一个列表：
 
-g this is a list -d 1 2 -3 5
 
“g” 表示一个字符串列表[“this”, “is”, “a”, “list”]，&quot;d&quot;标志表示一个整数列表[1, 2, -3, 5]。
 
这里第二个d是不是换个字母好点，后文第二次调试时d代表字符串，会增加理解成本</div>2024-04-10</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1c/f6/27/c27599ae.jpg" width="30px"><span>术子米德</span> 👍（0） 💬（1）<div>🤔☕️🤔☕️🤔
【Q】前面的课程，拉来认知模型，拉出LLM辅助建模和用户故事，做了这么多准备，怎么就跳跃到CleanCode的parseCmdLineArgs，这是出现幻觉了嘛？项目里，难道不是基于用户故事和建出来的模型，开始拆解到任务列表，让LLM浸泡在这个KnowledgeContext里持续辅助，然后用TDD的方法边验证、边实现、边详细设计、边螺旋迭代嘛？ 忽然间切换KnowledgeContext，这个人也适用不了，更何况LLM怎么适应，这个跳跃真不懂。
— by 术子米德@2024年4月10日</div>2024-04-10</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1c/f6/27/c27599ae.jpg" width="30px"><span>术子米德</span> 👍（0） 💬（0）<div>
&#47;&#47;BEGIN UT CODE GENERATED BY GITHUB COPILOT, EXCEPT FIRST LINE COMMENT
&#47;&#47;use gtest to test the function CC_parseCmdLineArgs defined in CC_parseCmdLineArgs.h
#include &quot;CC_parseCmdLineArgs.h&quot;
#include &lt;gtest&#47;gtest.h&gt;

TEST(CC_parseCmdLineArgs, NullCmdLineArgs) {
  CC_CmdLineArgs_T CmdLineArgs;
  EXPECT_EQ(CC_FAIL, CC_parseCmdLineArgs(0, NULL, &amp;CmdLineArgs));
}

TEST(CC_parseCmdLineArgs, NullCmdLineArgsPtr) {
  EXPECT_EQ(CC_FAIL, CC_parseCmdLineArgs(0, NULL, NULL));
}

TEST(CC_parseCmdLineArgs, NoArgs) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = { (char *)&quot;test&quot; };
  EXPECT_EQ(CC_SUCCESS, CC_parseCmdLineArgs(1, argv, &amp;CmdLineArgs));
  EXPECT_FALSE(CmdLineArgs.IsLoggingEnabled);
  EXPECT_EQ(0, CmdLineArgs.RecvPort);
  EXPECT_EQ(NULL, CmdLineArgs.pLogSavingDir);
}

...

TEST(CC_parseCmdLineArgs, RecvPort) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = { (char *)&quot;test&quot;, (char *)&quot;-p&quot;, (char *)&quot;1234&quot; };
  EXPECT_EQ(CC_SUCCESS, CC_parseCmdLineArgs(3, argv, &amp;CmdLineArgs));
  EXPECT_FALSE(CmdLineArgs.IsLoggingEnabled);
  EXPECT_EQ(1234, CmdLineArgs.RecvPort);
  EXPECT_EQ(NULL, CmdLineArgs.pLogSavingDir);
}

TEST(CC_parseCmdLineArgs, LogSavingDir) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = { (char *)&quot;test&quot;, (char *)&quot;-d&quot;, (char *)&quot;&#47;tmp&quot; };
  EXPECT_EQ(CC_SUCCESS, CC_parseCmdLineArgs(3, argv, &amp;CmdLineArgs));
  EXPECT_FALSE(CmdLineArgs.IsLoggingEnabled);
  EXPECT_EQ(0, CmdLineArgs.RecvPort);
  EXPECT_STREQ(&quot;&#47;tmp&quot;, CmdLineArgs.pLogSavingDir);
}

TEST(CC_parseCmdLineArgs, AllArgs) {
  CC_CmdLineArgs_T CmdLineArgs;
  char *argv[] = { (char *)&quot;test&quot;, (char *)&quot;-l&quot;, (char *)&quot;-p&quot;, (char *)&quot;1234&quot;, (char *)&quot;-d&quot;, (char *)&quot;&#47;tmp&quot; };
  EXPECT_EQ(CC_SUCCESS, CC_parseCmdLineArgs(7, argv, &amp;CmdLineArgs));
  EXPECT_TRUE(CmdLineArgs.IsLoggingEnabled);
  EXPECT_EQ(1234, CmdLineArgs.RecvPort);
  EXPECT_STREQ(&quot;&#47;tmp&quot;, CmdLineArgs.pLogSavingDir);
}

int main(int argc, char **argv) {
  testing::InitGoogleTest(&amp;argc, argv);
  return RUN_ALL_TESTS();
}</div>2024-04-10</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/1c/f6/27/c27599ae.jpg" width="30px"><span>术子米德</span> 👍（0） 💬（0）<div>&#47;&#47;BEGIN CODE&amp;COMMENT BY ME

typedef enum {
  CC_SUCCESS = 0,
  CC_FAIL    = 1,
} CC_Result_T;

typedef struct {
  bool IsLoggingEnabled;  &#47;&#47;-l
  int RecvPort;           &#47;&#47;-p &lt;port&gt;
  char *pLogSavingDir;    &#47;&#47;-d &lt;dir&gt;
} CC_CmdLineArgs_T;

&#47;**
 * @brief: Use CC_parseCmdLineArgs to parse command line arguments and save them in CC_CmdLingArgs_T.
 *
 * @param argc same as main
 * @param argv same as main
 * @param pCmdLineArgs pointer to CC_CmdLineArgs_T
 * @return CC_SUCCESS if successful, CC_FAIL otherwise in CC_Result_T
 *&#47;
CC_Result_T CC_parseCmdLineArgs(int argc, char *argv[], CC_CmdLineArgs_T *pCmdLineArgs);
</div>2024-04-10</li><br/><li><img src="https://static001.geekbang.org/account/avatar/00/11/1d/de/62bfa83f.jpg" width="30px"><span>aoe</span> 👍（0） 💬（1）<div>使用 AI 生成的测试通过 9 个，失败 7 个。在已有代码上修补，比自己从 0 到 1 实现快了非常多，这个只用了十几分钟！

主要步骤：
1. 15 课的例子扔给 coze 的 GPT4，得到的代码简单粗暴
2. 使用 Optimize 功能优化一下 prompt
3. 在优化的 prompt 上添加自己的想法
4. 因返回 token 限制，需要多次对话完成结果
  4.1 请给出 CommandLineParser 的完整代码
  4.2 请给出完整测试代码
  4.3 补全测试代码：测试用例可以继续增加，包括各种边界情况和无效输入
5. 最终得到的代码虽然测试没跑通，但功能强大</div>2024-04-10</li><br/>
</ul>