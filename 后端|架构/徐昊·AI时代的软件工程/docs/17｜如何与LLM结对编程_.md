你好，我是徐昊，今天我们来继续学习AI时代的软件工程。

上节课，我们系统性地介绍了使用大语言模型（Large Language Model，LLM）辅助软件开发的思路，也就是遵从测试驱动开发（Test Driven Development，TDD）的节奏，并与LLM结对编程（Pair Programming）完成需求。

那么，让我们使用这个思路，重新做一遍第15节课的例子，看看这一次有什么不一样。需求和之前是一样的：

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
> “g” 表示一个字符串列表\[“this”, “is”, “a”, “list”\]，"d"标志表示一个整数列表\[1, 2, -3, 5\]。
>
> 如果参数中没有指定某个标志，那么解析器应该指定一个默认值。例如，false代表布尔值，0代表数字， `""` 代表字符串，\[\]代表列表。如果给出的参数与模式不匹配，重要的是给出一个好的错误信息，准确地解释什么是错误的。
>
> 确保你的代码是可扩展的，即如何增加新的数值类型是直接和明显的。

## 测试先行

这次做的时候我们会有一些不一样的地方。按照我们 [上节课](https://time.geekbang.org/column/article/766281) 讲的内容，首先要做的是明确架构和测试策略，然后进行任务分解。目前的需求非常简单，我们知道这是一个单体的应用，最简单的做法就是使用一个类完成所有的功能。需要的测试也就是对于这个类的功能测试。因而，我们目前的任务分解主要围绕功能需求进行。

通过如下的模板，我们可以使用LLM帮助我们分解任务：

> 功能需求
>
> ====
>
> {requirement}
>
> 任务
>
> ====
>
> 请根据上面的功能需求，列出需要测试的场景。描述场景，并给出相关的测试数据。

![](https://static001.geekbang.org/resource/image/2d/ec/2d739a4c3ae67615fd44f1be6be8deec.jpg?wh=2020x3333)

简单阅读GPT的返回结果，我们就能发现几个错误：

1. 场景中存在大量的重复覆盖，比如2、4、6实际测试的是同样的场景。
2. 场景8实际不可测试，而且LLM在理解题目的时候，认为 “-l -p -d -g” 是唯一需要支持的参数，而不是通过配置可以扩展的设计。这就完全误解了题目的意思。

对比我们第一次使用LLM直接生成代码的情况，就会发现这些对于需求的误解是一直存在的，只不过第一次LLM生成的是生产代码，而这一次我们让它生产了测试列表。也就是说， **LLM从需求中提取到的知识是相同的。这些知识会被LLM应用到不同的场景中去**。 **不正确的生产代码和不正确的测试列表，是同一份知识的不同表现形式**。

但是这里有个关键差别： **以自然语言产生的测试/任务列表，我们更容易发现错误，并提出反馈。而以代码形式表示的功能代码，我们却很难在第一时间发现错误。** 因此我们就更需要在更早的时候提出反馈，避免错误的累积。

目前最重要的问题是，LLM认为 “-l -p -d -g” 是必需的参数，而不是通过可以配置的设计。我们首先要反馈调整这个问题：

> 需求中的-l -p -d -g 是例子，并不是必须支持的参数。参数是可配置，可扩展的。比如，用户配置了-x为int类型，那么就可以通过-x 100 指定。如果用户没有配置-p为int类型，那么-p就是非法参数。请按照这个补充，列出需要测试的场景。描述场景，并给出相关的测试数据。

GPT给出的结果如下图所示。

![](https://static001.geekbang.org/resource/image/3d/34/3da905eb5cb57e33b05fe245a0d7df34.jpg?wh=2000x3369)

这一次明显比之前的理解好了很多。虽然测试间仍然存在重复的情况，以及场景4这个更复杂的情况，处理得过于简单了，但是这些并不影响我们目前的操作。

接下来，我们可以让LLM帮助我们生产测试代码：

> 请不要考虑custom type的情况，测试的场景生成junit junpiter测试。
>
> 要求：
>
> - 每个场景对应一个测试方法。
> - 被测试的类叫ArgumentParser。它的构造函数接受Map<String, ArgumentType>作为参数配置；
> - ArgumentParser的parse方法返回Map<String, Object>作为解析结果；
> - 验证时，通过从Map中获取对应参数值，完成验证

![](https://static001.geekbang.org/resource/image/af/e0/af705c7407ec7c71050908e3e58afbe0.jpg?wh=2000x377)

```plain
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.Map;

public class ArgumentParserTest {

    private ArgumentParser parser;

    @BeforeEach
    void setUp() {
        // 在每个测试前初始化解析器
        Map<String, ArgumentType> config = new HashMap<>();
        config.put("-l", ArgumentType.BOOLEAN);
        config.put("-p", ArgumentType.INTEGER);
        config.put("-d", ArgumentType.STRING);
        config.put("-g", ArgumentType.STRING_LIST);
        parser = new ArgumentParser(config);
    }

    @Test
    void testBooleanFlag() {
        // 测试布尔标志
        String input = "-l";
        Map<String, Object> result = parser.parse(input);
        assertTrue((Boolean) result.get("-l"));
    }

    @Test
    void testIntegerValue() {
        // 测试整数值
        String input = "-p 8080";
        Map<String, Object> result = parser.parse(input);
        assertEquals(8080, result.get("-p"));
    }

    @Test
    void testStringValue() {
        // 测试字符串值
        String input = "-d /usr/logs";
        Map<String, Object> result = parser.parse(input);
        assertEquals("/usr/logs", result.get("-d"));
    }

    @Test
    void testStringListValue() {
        // 测试字符串列表值
        String input = "-g this is a list";
        Map<String, Object> result = parser.parse(input);
        assertArrayEquals(new String[]{"this", "is", "a", "list"}, ((Object[]) result.get("-g")));
    }

    @Test
    void testDefaultValues() {
        // 测试默认值
        String input = "-l -p -d";
        Map<String, Object> result = parser.parse(input);
        assertTrue((Boolean) result.get("-l"));
        assertEquals(0, result.get("-p"));
        assertEquals("", result.get("-d"));
    }

    @Test
    void testMixedParameters() {
        // 测试混合参数
        String input = "-l -p 8080 -d /usr/logs -g this is a list";
        Map<String, Object> result = parser.parse(input);
        assertTrue((Boolean) result.get("-l"));
        assertEquals(8080, result.get("-p"));
        assertEquals("/usr/logs", result.get("-d"));
        assertArrayEquals(new String[]{"this", "is", "a", "list"}, ((Object[]) result.get("-g")));
    }

    @Test
    void testIllegalValue() {
        // 测试非法值
        String input = "-p not_an_integer";
        assertThrows(IllegalValueException.class, () -> parser.parse(input));
    }

    @Test
    void testUnconfiguredParameter() {
        // 测试未配置参数
        String input = "-x custom_value";
        assertThrows(UnconfiguredParameterException.class, () -> parser.parse(input));
    }
}

```

![](https://static001.geekbang.org/resource/image/7e/f7/7e5116b12635c78b0000e653b39cf8f7.jpg?wh=2000x397)

## 生成生产代码

不得不说，虽然与LLM给出的测试场景不太相关，但是LLM给出的测试代码质量还是非常不错的。那么，接下来我们就可以生成生产代码了。

> 请按照需求，生成ArgumentParser以及相关类，可以通过这组测试。

![](https://static001.geekbang.org/resource/image/5f/09/5fb01221bda2ab538007de6bfe3d0009.jpg?wh=2000x429)

```plain
import java.util.HashMap;
import java.util.Map;
public class ArgumentParser {
    private Map<String, ArgumentType> config;
    public ArgumentParser(Map<String, ArgumentType> config) {
        this.config = config;
    }
    public Map<String, Object> parse(String input) {
        Map<String, Object> result = new HashMap<>();
        String[] tokens = input.split("\\s+");
        for (int i = 0; i < tokens.length; i++) {
            String token = tokens[i];
            if (config.containsKey(token)) {
                ArgumentType type = config.get(token);
                switch (type) {
                    case BOOLEAN:
                        result.put(token, true);
                        break;
                    case INTEGER:
                        i++;
                        try {
                            result.put(token, Integer.parseInt(tokens[i]));
                        } catch (NumberFormatException e) {
                            throw new IllegalValueException("Illegal value for parameter: " + tokens[i - 1]);
                        }
                        break;
                    case STRING:
                        i++;
                        result.put(token, tokens[i]);
                        break;
                    case STRING_LIST:
                        i++;
                        result.put(token, tokens[i].split(" "));
                        break;
                    default:
                        // Handle custom types if needed
                        break;
                }
            } else {
                throw new UnconfiguredParameterException("Unconfigured parameter: " + token);
            }
        }
        return result;
    }
}
enum ArgumentType {
    BOOLEAN,
    INTEGER,
    STRING,
    STRING_LIST,
    CUSTOM_TYPE // Add more types as needed
}
class IllegalParameterException extends RuntimeException {
    public IllegalParameterException(String message) {
        super(message);
    }
}
class IllegalValueException extends RuntimeException {
    public IllegalValueException(String message) {
        super(message);
    }
}
class UnconfiguredParameterException extends RuntimeException {
    public UnconfiguredParameterException(String message) {
        super(message);
    }
}

```

![](https://static001.geekbang.org/resource/image/08/3f/08e0a06ec28bdb89f8c4e4c4b876313f.jpg?wh=2000x385)

那么接下来，让我们跑一下测试看看结果。

![](https://static001.geekbang.org/resource/image/1d/42/1dcd21a520489c0dfd5bf5b867d23b42.jpg?wh=2896x2062)

一共8个测试，通过了5个失败了3个。其中比较重要的是testStringListValue，错误信息是这样的：

```plain
@Test
void testStringListValue() {
    // 测试字符串列表值
    String input = "-g this is a list";
    Map<String, Object> result = parser.parse(input);
    assertArrayEquals(new String[]{"this", "is", "a", "list"}, ((Object[]) result.get("-g")));
}

```

> UnconfiguredParameterException: Unconfigured parameter: is
>
> at ArgumentParser.parse(ArgumentParser.java:45)
>
> at ArgumentParserTest.testStringListValue(ArgumentParserTest.java:51)
>
> at java.base/java.lang.reflect.Method.invoke(Method.java:580)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)

也就是说，目前代码中只能处理单值的情况，并不能处理多值的情况。那么我们可以让LLM帮助我们修改：

> 执行测试的错误信息如下，请根据错误信息，修改ArgumentParse的代码：
>
> UnconfiguredParameterException: Unconfigured parameter: is
>
> at ArgumentParser.parse(ArgumentParser.java:45)
>
> at ArgumentParserTest.testStringListValue(ArgumentParserTest.java:51)
>
> at java.base/java.lang.reflect.Method.invoke(Method.java:580)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)

![](https://static001.geekbang.org/resource/image/c5/yb/c582b3404d4b50c40cb7b6b3a15c4yyb.jpg?wh=2000x2090)

此时需要注意，ChatGPT尝试通过修改测试的方式蒙混过关。我们需要坚守目前 **生产代码领航员的角色**，对GPT作出要求：

> 不是测试的问题，请修改ArgumentParser的逻辑

![](https://static001.geekbang.org/resource/image/96/ce/9689f38156315f2811c9ab1fc2141dce.jpg?wh=2000x389)

```plain
public class ArgumentParser {
    private Map<String, ArgumentType> config;
    public ArgumentParser(Map<String, ArgumentType> config) {
        this.config = config;
    }
    public Map<String, Object> parse(String input) {
        Map<String, Object> result = new HashMap<>();
        String[] tokens = input.split("\\s+");
        for (int i = 0; i < tokens.length; i++) {
            String token = tokens[i];
            if (config.containsKey(token)) {
                ArgumentType type = config.get(token);
                switch (type) {
                    case BOOLEAN:
                        result.put(token, true);
                        break;
                    case INTEGER:
                        i++;
                        try {
                            result.put(token, Integer.parseInt(tokens[i]));
                        } catch (NumberFormatException e) {
                            throw new IllegalValueException("Illegal value for parameter: " + tokens[i - 1]);
                        }
                        break;
                    case STRING:
                        i++;
                        result.put(token, tokens[i]);
                        break;
                    case STRING_LIST:
                        i++;
                        List<String> stringList = new ArrayList<>();
                        while (i < tokens.length && !tokens[i].startsWith("-")) {
                            stringList.add(tokens[i]);
                            i++;
                        }
                        result.put(token, stringList.toArray(new String[0]));
                        i--;  // Decrement to correctly process the next token in the loop
                        break;
                    default:
                        // Handle custom types if needed
                        break;
                }
            } else {
                throw new UnconfiguredParameterException("Unconfigured parameter: " + token);
            }
        }
        return result;
    }
}

```

![](https://static001.geekbang.org/resource/image/eb/78/eb72cd139988702fbe5dede0e65dab78.jpg?wh=2000x392)

我们再次运行测试：

![](https://static001.geekbang.org/resource/image/c7/61/c77183a21d50d0958bc652ac7a5fd061.jpg?wh=2928x2045)

就这时我们会发现只剩了一个没有通过的测试。而仔细查看会发现这个测试构造有问题。我们也不需要通过LLM再次修改了。自己直接改掉就行：

```plain
@Test
void testDefaultValues() {
    // 测试默认值
    String input = "";
    Map<String, Object> result = parser.parse(input);
    assertFalse((Boolean) result.get("-l"));
    assertEquals(0, result.get("-p"));
    assertEquals("", result.get("-d"));
}

```

再次执行，仍然失败，这时候我们发现代码中并没有对于默认值的处理。反馈给LLM：

> 目前代码中没有对于默认值的处理，请求改变ArgumentParser的逻辑，让它能够通过下面的测试：
>
> @Test
>
> void testDefaultValues() {
>
>     // 测试默认值
>
>     String input = “”;
>
>     Map<String, Object> result = parser.parse(input);
>
>     assertFalse((Boolean) result.get(“-l”));
>
>     assertEquals(0, result.get(“-p”));
>
>     assertEquals(“”, result.get(“-d”));
>
> }

![](https://static001.geekbang.org/resource/image/e9/72/e9d947c9afd5516f711e92dfd8ded472.jpg?wh=2000x391)

```plain
public class ArgumentParser {
    private Map<String, ArgumentType> config;
    public ArgumentParser(Map<String, ArgumentType> config) {
        this.config = config;
    }
    public Map<String, Object> parse(String input) {
        Map<String, Object> result = new HashMap<>();
        String[] tokens = input.split("\\s+");
        if (tokens.length == 1 && tokens[0].isEmpty()) {
            // Handle empty input
            setDefaultValues(result);
            return result;
        }
        for (int i = 0; i < tokens.length; i++) {
            String token = tokens[i];
            if (config.containsKey(token)) {
                ArgumentType type = config.get(token);
                switch (type) {
                    case BOOLEAN:
                        result.put(token, true);
                        break;
                    case INTEGER:
                        i++;
                        try {
                            result.put(token, Integer.parseInt(tokens[i]));
                        } catch (NumberFormatException e) {
                            throw new IllegalValueException("Illegal value for parameter: " + tokens[i - 1]);
                        }
                        break;
                    case STRING:
                        i++;
                        result.put(token, tokens[i]);
                        break;
                    case STRING_LIST:
                        i++;
                        List<String> stringList = new ArrayList<>();
                        while (i < tokens.length && !tokens[i].startsWith("-")) {
                            stringList.add(tokens[i]);
                            i++;
                        }
                        result.put(token, stringList.toArray(new String[0]));
                        i--;  // Decrement to correctly process the next token in the loop
                        break;
                    default:
                        // Handle custom types if needed
                        break;
                }
            } else {
                throw new UnconfiguredParameterException("Unconfigured parameter: " + token);
            }
        }
        return result;
    }
    private void setDefaultValues(Map<String, Object> result) {
        for (Map.Entry<String, ArgumentType> entry : config.entrySet()) {
            String param = entry.getKey();
            ArgumentType type = entry.getValue();
            if (!result.containsKey(param)) {
                switch (type) {
                    case BOOLEAN:
                        result.put(param, false);
                        break;
                    case INTEGER:
                        result.put(param, 0);
                        break;
                    case STRING:
                        result.put(param, "");
                        break;
                    case STRING_LIST:
                        result.put(param, new String[0]);
                        break;
                    default:
                        // Handle custom types if needed
                        break;
                }
            }
        }
    }
}

```

![](https://static001.geekbang.org/resource/image/14/53/1430f70db5716410a4bae76e0c335c53.jpg?wh=2000x399)

现在我们再来跑一次测试，结果如下。

![](https://static001.geekbang.org/resource/image/b7/be/b7605094fca653c2a429c727dbb29cbe.jpg?wh=2917x2079)

## 小结

到此为止，我们基本上完成了这个功能。对比第一次实现这个功能，我们迭代的次数更少，完成的过程中更有把握，严重的设计问题在早期就得到了重视。

我们做出的改变有这么几个：

- 通过测试列表，更加关注与LLM对齐对于知识的理解；
- 以测试驱动的方式，遵守“红-绿-重构”的节奏；
- 按照“导航员-司机”的模式与LLM结对。

这些改变让我们在获得速度提升的时候，保证了代码的质量，得到了真正的效率提升。

## 思考题

请总结在这个过程中，我们使用了哪些认知行为模式。

欢迎你在留言区分享自己的思考或疑惑，我们会把精彩内容置顶供大家学习讨论。