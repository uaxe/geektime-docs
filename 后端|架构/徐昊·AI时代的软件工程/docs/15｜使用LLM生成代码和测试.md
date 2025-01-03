你好，我是徐昊，今天我们来继续学习AI时代的软件工程。

通过前面的学习，我们了解了如何使用大语言模型（Large Language Model，LLM）辅助进行业务知识管理。接下来，我们继续学习使用LLM辅助软件交付的整体流程，以及其中涉及到的知识管理。

从今天这节课开始，我们将进入如何使用LLM辅助软件开发的环节。让我们从一个例子开始。

## 命令行参数解析

我们所使用的例子源自Robert C. Martin的 _Clean Code_ 第十四章，也是我的测试驱动专栏 [《TDD项目实战70讲》](https://time.geekbang.org/column/intro/100109401) 讲过的第一个项目，需求描述如下：

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

首先，让我们直接将这段需求扔到LLM中，看看LLM会生成怎样的代码。当然在那之前我们需要将它转化为提示词模板：

> 需求
>
> ====
>
> {requirement}
>
> 实现要求
>
> ====
>
> 使用Java语言实现上面的需求

当然你可以将Java语言换成任何你所熟悉的技术栈。我在这里仅仅是用Java举例。ChatGPT给出的结果是这样的：

```plain
import java.util.*;

public class CommandLineParser {

    public static void main(String[] args) {
        // 示例用法
        Map<String, Object> parsedArgs = parseArgs(args);
        System.out.println(parsedArgs);
    }

    public static Map<String, Object> parseArgs(String[] args) {
        Map<String, Object> parsedArgs = new HashMap<>();
        String currentFlag = null;
        List<Object> currentValues = new ArrayList<>();
        for (String arg : args) {
          if (arg.startsWith("-")) {
              // 处理之前的标志和值
              if (currentFlag != null) {
                  parsedArgs.put(currentFlag, parseValues(currentValues));
              }
              // 开始处理新的标志
              currentFlag = arg.substring(1);
              currentValues = new ArrayList<>();
            } else {
              // 处理标志对应的值
              currentValues.add(arg);
            }
        }
        // 处理最后一个标志和值
        if (currentFlag != null) {
            parsedArgs.put(currentFlag, parseValues(currentValues));
        }
        return parsedArgs;
    }

    private static Object parseValues(List<Object> values) {
        if (values.isEmpty()) {
            // 如果值为空，默认为布尔值false
            return false;
        } else if (values.size() == 1) {
            // 如果只有一个值，返回该值
            return parseSingleValue(values.get(0));
        } else {
            // 如果有多个值，返回值的列表
            List<Object> parsedList = new ArrayList<>();
            for (Object value : values) {
                parsedList.add(parseSingleValue(value));
            }
            return parsedList;
        }
    }

    private static Object parseSingleValue(Object value) {
        // 解析单个值的类型，可以根据需要扩展
        if (value instanceof String) {
            // 如果是字符串，返回原始字符串
            return value;
        } else {
            try {
                // 尝试解析为整数
                return Integer.parseInt(value.toString());
            } catch (NumberFormatException e) {
                // 如果解析失败，返回原始值
                return value;
            }
         }
    }
}

```

无论你是否了解Java，你都可以感受到，这段代码的逻辑是有一定复杂度的。而ChatGPT生成这段代码也就只要几秒钟的时间，显然我们无法在几秒钟内判断这段代码是否符合我们的要求。

这就意味着，我们无法知道这段代码是否完成了功能。我们仍然要回归到为这段代码构造测试，并验证它是否正确的道路上。 **所以哪怕你对于测试驱动开发一无所知，LLM的特性仍然会将你的注意力引导到测试上。** 我们可以在现在的代码基础上，让LLM帮助我们生成测试。

> 请根据需求，为这段代码生成相应的测试

ChatGPT生成的结果是：

```plain
import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.*;
class CommandLineParserTest {
    @Test
    void testParseArgs() {
        // 测试基本的命令行参数解析
        String[] args1 = {"-l", "-p", "8080", "-d", "/usr/logs"};
        Map<String, Object> result1 = CommandLineParser.parseArgs(args1);
        assertEquals(true, result1.get("l"));
        assertEquals(8080, result1.get("p"));
        assertEquals("/usr/logs", result1.get("d"));

        // 测试带有列表的命令行参数解析
        String[] args2 = {"-g", "this", "is", "a", "list", "-d", "1", "2", "-3", "5"};
        Map<String, Object> result2 = CommandLineParser.parseArgs(args2);
        assertEquals(List.of("this", "is", "a", "list"), result2.get("g"));
        assertEquals(List.of(1, 2, -3, 5), result2.get("d"));

        // 测试默认值
        String[] args3 = {};
        Map<String, Object> result3 = CommandLineParser.parseArgs(args3);
        assertEquals(false, result3.get("l"));
        assertEquals(0, result3.get("p"));
        assertEquals("", result3.get("d"));

        // 测试无效参数
        String[] args4 = {"-p", "abc"};
        assertThrows(NumberFormatException.class, () -> CommandLineParser.parseArgs(args4));
        // 添加更多的测试用例，根据需要进行扩展
    }
}

```

我们先忽略ChatGPT生成测试的风格问题，比如不同的场景应该构造成不同的测试，也可以暂时不考虑这些测试的完备性问题，比如缺少边界条件。先看看ChatGPT给出的代码是否能够满足这些测试。

![](https://static001.geekbang.org/resource/image/00/38/0095bd8b5945270a4363939cda7c4e38.jpg?wh=2910x2072)

## 第一次调试

然而结果是并不能，按照测试结果显示，当我们传入参数 “-l” 的时候，ChatGPT生成的代码并没有按照题目要求的逻辑转化为true。那么我们就要去回看ChatGPT生成的代码了，并尝试定位这个问题产生的根源。不难发现问题出在这个地方：

```plain
private static Object parseValues(List<Object> values) {
    if (values.isEmpty()) {
        // 如果值为空，默认为布尔值false
        return false;
    } else if (values.size() == 1) {
        // 如果只有一个值，返回该值
        return parseSingleValue(values.get(0));
    } else {
        // 如果有多个值，返回值的列表
        List<Object> parsedList = new ArrayList<>();
        for (Object value : values) {
            parsedList.add(parseSingleValue(value));
        }
        return parsedList;
    }
}

```

这里ChatGPT给出的逻辑是错误的，当我们给出参数 “-l” 的时候，实际的值是\[“-l”\]，所以values是一个空列表，那么返回值应该是true。我们可以按照这个向ChatGPT提出建议。

当然，我们也可以用一种更简单的方式，直接把错误信息提供给ChatGPT，让它根据错误信息修改代码：

> 执行测试的错误信息如下，请根据错误信息，修改CommandLineParser的代码：
>
> Expected :true
>
> Actual   :false
>
> org.opentest4j.AssertionFailedError: expected:  but was:
>
> at org.junit.jupiter.api.AssertionFailureBuilder.build(AssertionFailureBuilder.java:151)
>
> at org.junit.jupiter.api.AssertionFailureBuilder.buildAndThrow(AssertionFailureBuilder.java:132)
>
> at org.junit.jupiter.api.AssertEquals.failNotEqual(AssertEquals.java:197)
>
> at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:182)
>
> at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:177)
>
> at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:1141)
>
> at CommandLineParserTest.testParseArgs(CommandLineParserTest.java:15)
>
> at java.base/java.lang.reflect.Method.invoke(Method.java:580)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)

![](https://static001.geekbang.org/resource/image/45/35/45a751578ac9b6c1831c839ae195e835.jpg?wh=1404x456)

```plain
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CommandLineParser {

    public static void main(String[] args) {
        // 示例用法
        Map<String, Object> parsedArgs = parseArgs(args);
        System.out.println(parsedArgs);
    }

    public static Map<String, Object> parseArgs(String[] args) {
        Map<String, Object> parsedArgs = new HashMap<>();
        String currentFlag = null;
        List<Object> currentValues = new ArrayList<>();

        for (String arg : args) {
            if (arg.startsWith("-")) {
                // 处理之前的标志和值
                if (currentFlag != null) {
                    parsedArgs.put(currentFlag, parseValues(currentValues));
                }

                // 开始处理新的标志
                currentFlag = arg.substring(1);
                currentValues = new ArrayList<>();
            } else {
                // 处理标志对应的值
                currentValues.add(arg);
            }
        }

        // 处理最后一个标志和值
        if (currentFlag != null) {
            parsedArgs.put(currentFlag, parseValues(currentValues));
        }

        return parsedArgs;
    }

    private static Object parseValues(List<Object> values) {
        if (values.isEmpty()) {
            // 如果值为空，默认为布尔值true
            return true;
        } else if (values.size() == 1) {
            // 如果只有一个值，返回该值
            return parseSingleValue(values.get(0));
        } else {
            // 如果有多个值，返回值的列表
            List<Object> parsedList = new ArrayList<>();
            for (Object value : values) {
                parsedList.add(parseSingleValue(value));
            }
            return parsedList;
        }
    }

    private static Object parseSingleValue(Object value) {
        // 解析单个值的类型，可以根据需要扩展
        if (value instanceof String) {
            // 如果是字符串，返回原始字符串
            return value;
        } else {
            try {
                // 尝试解析为整数
                return Integer.parseInt(value.toString());
            } catch (NumberFormatException e) {
                // 如果解析失败，返回原始值
                return value;
            }
        }
    }
}

```

再次执行测试，依然存在错误。

![](https://static001.geekbang.org/resource/image/fd/30/fdffe163b783560byy69e8e04b980430.jpg?wh=2932x2132)

## 第二次调试

这次的问题要更严重一些，从错误结果上看，我们期待传入 “-p 8080” 时，得到参数的类型是整型，而ChatGPT生成的代码给出的结果是字符串。同样我们不难定位到错误在什么地方：

```plain
    } else if (values.size() == 1) {
        // 如果只有一个值，返回该值
        return parseSingleValue(values.get(0));
    } else {

```

在这段代码中，ChatGPT将任何的单值参数都当作了字符串类型。这背后反映的是 **ChatGPT给出的代码在设计上的缺陷**。也就是说是，不同的参数 “-l”, “-p” 和 “-d” 对应了不同的类型（bool，int和string）。而ChatGPT给出的代码忽略了类型的差异，尝试从结果上去推断类型，这自然是不能成功的。那么如果我们仍然按照前面的做法，让ChatGPT自行解决，它会发现这个问题吗？

> 执行测试的错误信息如下，请根据错误信息，修改CommandLineParser的代码：
>
> Expected :8080
>
> Actual   :8080
>
> org.opentest4j.AssertionFailedError: expected: java.lang.Integer@1c5920df<8080> but was: java.lang.String@17f9d882<8080>
>
> at org.junit.jupiter.api.AssertionFailureBuilder.build(AssertionFailureBuilder.java:151)
>
> at org.junit.jupiter.api.AssertionFailureBuilder.buildAndThrow(AssertionFailureBuilder.java:132)
>
> at org.junit.jupiter.api.AssertEquals.failNotEqual(AssertEquals.java:197)
>
> at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:182)
>
> at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:177)
>
> at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:1141)
>
> at CommandLineParserTest.testParseArgs(CommandLineParserTest.java:16)
>
> at java.base/java.lang.reflect.Method.invoke(Method.java:580)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)
>
> at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)

![](https://static001.geekbang.org/resource/image/63/6a/63203311acec12805f1b8078c507d36a.jpg?wh=1372x1608)

很显然，它没发现这是个设计问题，但是它给出了一个能通过测试的最简单的办法。这种做法也蛮符合测试驱动开发对于节奏的要求。那么这时候，应该由我们给出设计上的建议和改进了。

> 需求中给出的参数具有不同类型，比如：
>
> -l 是bool
>
> -p 是 int
>
> -d 是 string
>
> -g 是 list
>
> 我们需要指定不同参数的不同类型。然后根据类型去解析参数。请按照这个思路重新编写CommandLineParser

提供建议以后，GPT返回的修改结果如下。

![](https://static001.geekbang.org/resource/image/72/9e/7272e7e8cf264153cc9616f794f2529e.jpg?wh=1372x318)

```plain
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CommandLineParser {

    // 定义参数类型的枚举
    public enum ArgType {
        BOOLEAN, INTEGER, STRING, LIST
    }

    public static void main(String[] args) {
        // 示例用法
        Map<String, Object> parsedArgs = parseArgs(args);
        System.out.println(parsedArgs);
    }

    public static Map<String, Object> parseArgs(String[] args) {
        Map<String, Object> parsedArgs = new HashMap<>();
        String currentFlag = null;
        List<Object> currentValues = new ArrayList<>();
        ArgType currentType = null;

        for (String arg : args) {
            if (arg.startsWith("-")) {
                // 处理之前的标志和值
                if (currentFlag != null) {
                    parsedArgs.put(currentFlag, parseValues(currentValues, currentType));
                }

                // 开始处理新的标志
                currentFlag = arg.substring(1);
                currentValues = new ArrayList<>();
                currentType = determineArgType(currentFlag);
            } else {
                // 处理标志对应的值
                currentValues.add(arg);
            }
        }

        // 处理最后一个标志和值
        if (currentFlag != null) {
            parsedArgs.put(currentFlag, parseValues(currentValues, currentType));
        }

        return parsedArgs;
    }

    private static ArgType determineArgType(String flag) {
        // 根据标志确定参数类型
        switch (flag) {
            case "l":
                return ArgType.BOOLEAN;
            case "p":
                return ArgType.INTEGER;
            case "d":
                return ArgType.STRING;
            case "g":
                return ArgType.LIST;
            // 添加更多的类型，根据需要进行扩展
            default:
                throw new IllegalArgumentException("Unknown flag: " + flag);
        }
    }

    private static Object parseValues(List<Object> values, ArgType type) {
        if (values.isEmpty()) {
            // 如果值为空，默认为布尔值true
            return true;
        } else if (values.size() == 1) {
            // 如果只有一个值，返回该值
            return parseSingleValue(values.get(0), type);
        } else {
            // 如果有多个值，返回值的列表
            List<Object> parsedList = new ArrayList<>();
            for (Object value : values) {
                parsedList.add(parseSingleValue(value, type));
            }
            return parsedList;
        }
    }

    private static Object parseSingleValue(Object value, ArgType type) {
        // 解析单个值的类型，可以根据需要扩展
        switch (type) {
            case BOOLEAN:
                return true;  // 目前布尔值都设为true，可以根据实际需求调整
            case INTEGER:
                try {
                    return Integer.parseInt(value.toString());
                } catch (NumberFormatException e) {
                    throw new IllegalArgumentException("Invalid integer value: " + value);
                }
            case STRING:
                return value.toString();
            case LIST:
                return parseListValue(value);
            // 添加更多的类型，根据需要进行扩展
            default:
                throw new IllegalArgumentException("Unsupported type: " + type);
        }
    }

    private static List<Object> parseListValue(Object value) {
        // 解析列表类型的值
        if (value instanceof String) {
            // 如果是字符串，按空格分割
            String[] parts = ((String) value).split(" ");
            List<Object> listValues = new ArrayList<>();
            for (String part : parts) {
                listValues.add(part);
            }
            return listValues;
        } else {
            throw new IllegalArgumentException("Invalid list value: " + value);
        }
    }
}

```

![](https://static001.geekbang.org/resource/image/33/77/338b6e8c85b26ec9039ed7d538a06a77.jpg?wh=1392x298)

## 第三次调试

按照ChatGPT给出的修改，我们仍然没能通过全部的测试。新的错误继续出现：

![](https://static001.geekbang.org/resource/image/b4/da/b4bec30568d84f5b9958dbd9ab0e93da.jpg?wh=2888x2081)

现在测试失败的地方在于，ChatGPT生成的代码将-3看作了参数名，而不是参数值。现在我们可以直接告诉ChatGPT现在的问题在哪，问题出在下面这个方法中将参数类型硬编码了（hard-coded）：

```plain
private static ArgType determineArgType(String flag) {
        // 根据标志确定参数类型
        switch (flag) {
            case "l":
                return ArgType.BOOLEAN;
            case "p":
                return ArgType.INTEGER;
            case "d":
                return ArgType.STRING;
            case "g":
                return ArgType.LIST;
            // 添加更多的类型，根据需要进行扩展
            default:
                throw new IllegalArgumentException("Unknown flag: " + flag);
        }
    }

```

那么我们现在可以告诉ChatGPT这个问题，并让它重新生成代码：

> 目前determineArgType中限定了可以使用的参数，将它改编为可配置的情况。也就是当用户初始化CommandLineParser时，可以指定支持的参数及其类型。

GPT的回复如下。

![](https://static001.geekbang.org/resource/image/c3/39/c32f763bc08f7610e3886a7ff0f68839.jpg?wh=1372x288)

```plain
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CommandLineParser {

    // 定义参数类型的枚举
    public enum ArgType {
        BOOLEAN, INTEGER, STRING, LIST
    }

    // 可配置的参数类型映射
    private final Map<String, ArgType> argTypeMap;

    public CommandLineParser(Map<String, ArgType> argTypeMap) {
        // 初始化参数类型映射
        this.argTypeMap = new HashMap<>(argTypeMap);
    }

    public static void main(String[] args) {
        // 示例用法
        // 初始化参数类型映射，可以根据需要配置
        Map<String, ArgType> customArgTypeMap = new HashMap<>();
        customArgTypeMap.put("l", ArgType.BOOLEAN);
        customArgTypeMap.put("p", ArgType.INTEGER);
        customArgTypeMap.put("d", ArgType.STRING);
        customArgTypeMap.put("g", ArgType.LIST);

        // 创建 CommandLineParser 实例时传入自定义的参数类型映射
        CommandLineParser parser = new CommandLineParser(customArgTypeMap);

        Map<String, Object> parsedArgs = parser.parseArgs(args);
        System.out.println(parsedArgs);
    }

    public Map<String, Object> parseArgs(String[] args) {
        Map<String, Object> parsedArgs = new HashMap<>();
        String currentFlag = null;
        List<Object> currentValues = new ArrayList<>();
        ArgType currentType = null;

        for (String arg : args) {
            if (arg.startsWith("-")) {
                // 处理之前的标志和值
                if (currentFlag != null) {
                    parsedArgs.put(currentFlag, parseValues(currentValues, currentType));
                }

                // 开始处理新的标志
                currentFlag = arg.substring(1);
                currentValues = new ArrayList<>();
                currentType = determineArgType(currentFlag);
            } else {
                // 处理标志对应的值
                currentValues.add(arg);
            }
        }

        // 处理最后一个标志和值
        if (currentFlag != null) {
            parsedArgs.put(currentFlag, parseValues(currentValues, currentType));
        }

        return parsedArgs;
    }

    private ArgType determineArgType(String flag) {
        // 根据标志确定参数类型，如果未配置，默认为STRING类型
        return argTypeMap.getOrDefault(flag, ArgType.STRING);
    }

    private Object parseValues(List<Object> values, ArgType type) {
        if (values.isEmpty()) {
            // 如果值为空，默认为布尔值true
            return true;
        } else if (values.size() == 1) {
            // 如果只有一个值，返回该值
            return parseSingleValue(values.get(0), type);
        } else {
            // 如果有多个值，返回值的列表
            List<Object> parsedList = new ArrayList<>();
            for (Object value : values) {
                parsedList.add(parseSingleValue(value, type));
            }
            return parsedList;
        }
    }

    private Object parseSingleValue(Object value, ArgType type) {
        // 解析单个值的类型，可以根据需要扩展
        switch (type) {
            case BOOLEAN:
                return true;  // 目前布尔值都设为true，可以根据实际需求调整
            case INTEGER:
                try {
                    return Integer.parseInt(value.toString());
                } catch (NumberFormatException e) {
                    throw new IllegalArgumentException("Invalid integer value: " + value);
                }
            case STRING:
                return value.toString();
            case LIST:
                return parseListValue(value);
            // 添加更多的类型，根据需要进行扩展
            default:
                throw new IllegalArgumentException("Unsupported type: " + type);
        }
    }

    private List<Object> parseListValue(Object value) {
        // 解析列表类型的值
        if (value instanceof String) {
            // 如果是字符串，按空格分割
            String[] parts = ((String) value).split(" ");
            List<Object> listValues = new ArrayList<>();
            for (String part : parts) {
                listValues.add(part);
            }
            return listValues;
        } else {
            throw new IllegalArgumentException("Invalid list value: " + value);
        }
    }
}

```

![](https://static001.geekbang.org/resource/image/yy/f6/yyf4a222257dacf4f2f35a0833c03ff6.jpg?wh=1372x284)

我们看到这里ChatGPT在main方法中给出了配置CommandLineParser的方式，我们需要将它改到我们的测试中。当然也可以用ChatGPT修改我们的测试，但其实没有这个必要。

## 小结

按照ChatGPT给出的修改，我们仍然没能通过全部的测试。新的错误继续出现：

![](https://static001.geekbang.org/resource/image/7a/1f/7a724809834fd15fa3ee36b5fb5f7a1f.jpg?wh=2911x2089)

这次是列表的结构错误。当然，这里我们可以继续告诉ChatGPT，错误发生在哪，然后让ChatGPT再重写代码。过程与前面的类似，我们就不再重复了。

在这里我并不是想说ChatGPT生成的代码有多么的不靠谱。恰恰相反，哪怕漏洞百出，这仍然展示了巨大的效率提升。你可以试试自己从头开始编写这么一段功能，再比较一下这节课展示的方法，就会明白我的意思。

这里我想提醒你的是， **LLM快则快矣，质量堪忧。当我们使用LLM辅助软件开发的时候，更多的精力要放到质量的控制上。而不是一味地关注效率。**

那么下节课，我们就来讲讲怎么在提高效率的同时保持质量。

## 思考题

请跟LLM一起完成课程中的这个题目。

欢迎你在留言区分享自己的思考或疑惑，我们会把精彩内容置顶供大家学习讨论。