你好，我是郭屹。

上一节课我们一起学习了如何使用ChatGPT来辅助我们编程，通过问答它给出了我们想要的答案。这个过程实际上还是以手工的方式来对话，不过好在OpenAI还提供一些API供程序调用。现在微软的搜索引擎Bing和Quora网站推出的Poe都使用了它。所以今天我们一起看看这些API。

## API入门

OpenAI给开发者提供API来访问它的模型，帮助开发者解决语言处理类任务。

它提供多种基础功能，包括：

- 内容生成Content generation
- 摘要Summarization
- 分类及语义分析Classification, categorization, and sentiment analysis
- 翻译Translation
- …

最主要的API访问入口是 [Completions](https://platform.openai.com/docs/api-reference/completions)。开发者输入一些文本，API会根据你在文本中的意图返回另一段文本。你可以以HTTP Request的方式与API进行交互，然后通过API key进行身份认证。

格式如下：

```plain
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
     "model": "gpt-3.5-turbo",
     "messages": [{"role": "user", "content": "Say this is a test!"}],
     "temperature": 0.7
   }'

```

支持的模型有7个。

- [GPT-4](https://platform.openai.com/docs/models/gpt-4) **Limited beta：** GPT-3.5 之上的改进，对自然语言的理解和处理更强。
- [GPT-3.5](https://platform.openai.com/docs/models/gpt-3-5)：在GPT-3 基础上改进的，对自然语言的理解和处理更强。
- [DALL·E](https://platform.openai.com/docs/models/dall-e) **Beta：** 图像处理。
- [Whisper](https://platform.openai.com/docs/models/whisper) **Beta：** 音频转文本。
- [Embeddings](https://platform.openai.com/docs/models/embeddings)：将文本转成嵌入向量。
- [Moderation](https://platform.openai.com/docs/models/moderation)：检测敏感信息和非安全内容。
- [GPT-3](https://platform.openai.com/docs/models/gpt-3)：自然语言理解和处理的模型。

有了这些API，在我们的程序中就可以使用它们，也可以用这些API做出我们自己的插件来。

## 程序中调用OpenAI的API

在Spring中用HTTPClient直接调用OpenAI 的API。我们从 /v1/chat/completions、 /v1/completions、/v1/edits 与 /v1/images/generations四个API入手，一步步进行封装。

先定义一个 **基础请求实体类**，供service使用，参考如下：

```java
package com.example.chatgptdemo.api.request;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class BaseRequest {
    @NotBlank(message = "openai_apiKey cannot be blank")
    private String apiKey;
}

```

再按照我们示例的几种API，定义多种请求实体类。

```java
package com.example.chatgptdemo.api.request;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class ChatCompletionRequest extends BaseRequest{
    private String content;
}

```

```java
package com.example.chatgptdemo.api.request;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class CompletionRequest extends BaseRequest{
    private String prompt;
}

```

```java
package com.example.chatgptdemo.api.request;

import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class EditRequest extends BaseRequest{
    private String input;
    private String instruction;
}

```

```java
package com.example.chatgptdemo.api.request;

import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class ImageGenerationRequest extends BaseRequest {
    private String prompt;
    private Integer n;
}

```

然后定义返回给调用方的Response类。

```java
package com.example.chatgptdemo.api.response;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class ChatCompletionResponse {
    private String content;
}

```

```java
package com.example.chatgptdemo.api.response;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class CompletionResponse {
    private String text;
}

```

```java
package com.example.chatgptdemo.api.response;

import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class EditResponse {
    private String text;
}

```

```java
package com.example.chatgptdemo.api.response;
import lombok.Getter;
import lombok.Setter;
import java.util.List;
@Getter
@Setter
public class ImageGenerationResponse {
    private List<String> urls;
}

```

接下来则 **定义Service层**，这也是我们进行核心业务定制的部分。定义ChatgptDemoService接口和ChatgptDemoServiceImpl实现类。

```java
package com.example.chatgptdemo.service;

public interface ChatgptDemoService {
    ChatCompletionResponse chatCompletions(ChatCompletionRequest request);
    CompletionResponse completions(CompletionRequest request);
    EditResponse edits(EditRequest request);
    ImageGenerationResponse imageGenerations(ImageGenerationRequest request);
}

```

Service的实现如下：

```java
package com.example.chatgptdemo.service.impl;
@Service
public class ChatgptDemoServiceImpl implements ChatgptDemoService {
    final private ChatgptNetworkService networkService;
    @Autowired
    public ChatgptDemoServiceImpl(ChatgptNetworkService networkService) {
        this.networkService = networkService;
    }
    @Override
    public ChatCompletionResponse chatCompletions(ChatCompletionRequest request) {
        MessageObject message = new MessageObject();
        message.setContent(request.getContent());
        message.setRole("user");
        ChatCompletionModel model = new ChatCompletionModel();
        model.setModel("gpt-3.5-turbo");
        model.setMessages(Collections.singletonList(message));
        model.setTemperature(0.7);
        ChatCompletionResult result = networkService.ChatCompletions(model, request.getApiKey());
        Optional<ChoiceResult> firstResultOptional = result.getChoices().stream().findFirst();
        ChatCompletionResponse response = new ChatCompletionResponse();
        if (firstResultOptional.isEmpty()) {
            return response;
        }
        ChoiceResult choiceResult = firstResultOptional.get();
        response.setContent(choiceResult.getMessage().getContent());
        return response;
    }
    @Override
    public CompletionResponse completions(CompletionRequest request) {
        CompletionModel model = new CompletionModel();
        model.setModel("text-davinci-003");
        model.setPrompt(request.getPrompt());
        model.setMaxTokens(7);
        model.setN(1);
        model.setTopP(1);
        model.setStream(false);
        CompletionResult result = networkService.completions(model, request.getApiKey());
        Optional<ChoiceResult> firstResultOptional = result.getChoices().stream().findFirst();
        CompletionResponse response = new CompletionResponse();
        if (firstResultOptional.isEmpty()) {
            return response;
        }
        ChoiceResult choiceResult = firstResultOptional.get();
        response.setText(choiceResult.getText());
        return response;
    }
    @Override
    public EditResponse edits(EditRequest request) {
        EditModel model = new EditModel();
        model.setInput(request.getInput());
        model.setInstruction(request.getInstruction());
        EditResult result = networkService.edits(model, request.getApiKey());
        Optional<ChoiceResult> firstResultOptional = result.getChoices().stream().findFirst();
        EditResponse response = new EditResponse();
        if (firstResultOptional.isEmpty()) {
            return response;
        }
        ChoiceResult choiceResult = firstResultOptional.get();
        response.setText(choiceResult.getText());
        return response;
    }
    @Override
    public ImageGenerationResponse imageGenerations(ImageGenerationRequest request) {
        ImageGenerationModel model = new ImageGenerationModel();
        model.setPrompt(request.getPrompt());
        model.setN(request.getN());
        model.setSize("1024x1024");
        ImageGenerationResult result = networkService.imageGenerations(model, request.getApiKey());
        List<ImageGenerationResult.ImageGenerationData> resultList =
                result.getData().stream().toList();
        List<String> urls = new ArrayList<>(resultList.size());
        resultList.forEach(r -> urls.add(r.getUrl()));
        ImageGenerationResponse response = new ImageGenerationResponse();
        response.setUrls(urls);
        return response;
    }
}

```

通过实现类的代码可以看出，基本是围绕构造OpenAI提供的API调用参数作文章，只不过为了验证，我们写死了很多参数，在实际实操过程中我们可以依据自身业务情况，进行动态调整。

我们使用了ChatgptNetworkService这样一个Bean作为通讯基础，而这个Bean的功能正是对OpenAI的API进行调用。我们直接使用RestTemplate访问的API。

为了构造API调用，我们定义了xxxModel作为API调用的请求参数实体类，还定义了xxxResult作为API接口返回值。

Model实体类：

```java
package com.example.chatgptdemo.network.model;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class CompletionModel {
    private String model;
    private String prompt;
    @JsonProperty("max_tokens")
    private Integer maxTokens;
    private Integer n;
    @JsonProperty("top_p")
    private Integer topP;
    private Boolean stream;
}

```

```java
package com.example.chatgptdemo.network.model;
import lombok.Getter;
import lombok.Setter;
@Setter
@Getter
public class MessageObject {
    private String role;
    private String content;
}

```

```java
package com.example.chatgptdemo.network.model.chat;
import com.example.chatgptdemo.network.model.MessageObject;
import lombok.Getter;
import lombok.Setter;
import java.util.List;
@Getter
@Setter
public class ChatCompletionModel {
    private String model;
    private List<MessageObject> messages;
    private Double temperature;
}

```

```java
package com.example.chatgptdemo.network.model;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class EditModel {
    private String model;
    private String input;
    private String instruction;
}

```

```java
package com.example.chatgptdemo.network.model;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class ImageGenerationModel {
    private String prompt;
    private Integer n;
    private String size;
}

```

Result实体类：

```java
package com.example.chatgptdemo.network.result;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class CreatedResult {
    private Long created;
}

```

```java
package com.example.chatgptdemo.network.result;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class ObjectResult extends CreatedResult{
    private String id;
    private String object;
    private String model;
}

```

```java
package com.example.chatgptdemo.network.result;
import com.example.chatgptdemo.network.model.MessageObject;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class ChoiceResult {
    private MessageObject message;
    private String text;
    @JsonProperty("finish_reason")
    private String finishReason;
    private Integer index;
}

```

```java
package com.example.chatgptdemo.network.result;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class UsageResult {
    @JsonProperty("prompt_tokens")
    private Integer promptTokens;
    @JsonProperty("completion_tokens")
    private Integer completionTokens;
    @JsonProperty("total_tokens")
    private Integer totalTokens;
}

```

```java
package com.example.chatgptdemo.network.result;
@Getter
@Setter
public class CompletionResult {
    private UsageResult usage;
    private List<ChoiceResult> choices;
}

```

```java
package com.example.chatgptdemo.network.result.chat;
@Getter
@Setter
public class ChatCompletionResult extends CompletionResult {
}

```

```java
package com.example.chatgptdemo.network.result;
import lombok.Getter;
import lombok.Setter;
@Getter
@Setter
public class EditResult extends CompletionResult {
}

```

```java
package com.example.chatgptdemo.network.result;
import com.example.chatgptdemo.api.response.ImageGenerationResponse;
import lombok.Getter;
import lombok.Setter;
import java.util.List;
@Getter
@Setter
public class ImageGenerationResult extends CreatedResult{
    private List<ImageGenerationData> data;
    @Getter
    @Setter
    public static class ImageGenerationData {
        private String url;
    }
}

```

在实体类定义完毕之后，接下来我们着手实现ChatGptNetworkService，看看Spring中如何通过RestTemplate调用OpenAI的API。

```java
package com.example.chatgptdemo.network;
@Service
public class ChatgptNetworkService {
    Gson gson = new Gson();
    private static final Logger logger = LoggerFactory.getLogger(ChatgptNetworkService.class);
    final private RestTemplate restTemplate;
    @Autowired
    public ChatgptNetworkService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    public ChatCompletionResult ChatCompletions(ChatCompletionModel model, String apiKey) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);
        HttpEntity<?> entity = new HttpEntity<>(model, headers);
        URI uri = UriComponentsBuilder.newInstance()
                .scheme("https")
                .host("api.openai.com")
                .path("/v1/chat/completions")
                .build()
                .toUri();
        logger.info("The parameters for request API {}: {}", uri, gson.toJson(entity));
        ResponseEntity<ChatCompletionResult> response = restTemplate.postForEntity(uri, entity, ChatCompletionResult.class);
        logger.info("The response result from API {}: {}", uri, gson.toJson(response));
        if (response.getStatusCode().isError()) {
            throw new RuntimeException(gson.toJson(response.getBody()));
        }
        return response.getBody();
    }
    public CompletionResult completions(CompletionModel model, String apiKey) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);
        HttpEntity<?> entity = new HttpEntity<>(model, headers);
        URI uri = UriComponentsBuilder.newInstance()
                .scheme("https")
                .host("api.openai.com")
                .path("/v1/completions")
                .build()
                .toUri();
        logger.info("The parameters for request API {}: {}", uri, gson.toJson(entity));
        ResponseEntity<CompletionResult> response = restTemplate.postForEntity(uri, entity, CompletionResult.class);
        logger.info("The response result from API {}: {}", uri, gson.toJson(response));
        if (response.getStatusCode().isError()) {
            throw new RuntimeException(gson.toJson(response.getBody()));
        }
        return response.getBody();
    }
    public EditResult edits(EditModel model, String apiKey) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);
        HttpEntity<?> entity = new HttpEntity<>(model, headers);
        URI uri = UriComponentsBuilder.newInstance()
                .scheme("https")
                .host("api.openai.com")
                .path("/v1/edits")
                .build()
                .toUri();
        logger.info("The parameters for request API {}: {}", uri, gson.toJson(entity));
        ResponseEntity<EditResult> response = restTemplate.postForEntity(uri, entity, EditResult.class);
        logger.info("The response result from API {}: {}", uri, gson.toJson(response));
        if (response.getStatusCode().isError()) {
            throw new RuntimeException(gson.toJson(response.getBody()));
        }
        return response.getBody();
    }
    public ImageGenerationResult imageGenerations(ImageGenerationModel model, String apiKey) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);
        HttpEntity<?> entity = new HttpEntity<>(model, headers);
        URI uri = UriComponentsBuilder.newInstance()
                .scheme("https")
                .host("api.openai.com")
                .path("/v1/images/generations")
                .build()
                .toUri();
        logger.info("The parameters for request API {}: {}", uri, gson.toJson(entity));
        ResponseEntity<ImageGenerationResult> response = restTemplate.postForEntity(uri, entity, ImageGenerationResult.class);
        logger.info("The response result from API {}: {}", uri, gson.toJson(response));
        if (response.getStatusCode().isError()) {
            throw new RuntimeException(gson.toJson(response.getBody()));
        }
        return response.getBody();
    }
}

```

代码一点都不复杂，就是按照API的规定进行常规的HTTP REST请求。

有了这个service，再定义Controller层。这层是整个系统与外部调用API的门户。我们先定义ChatgptDemoController类。

```java
package com.example.chatgptdemo.controller;

@RestController
public class ChatgptDemoController {
    final private ChatgptDemoService chatgptDemoService;
    @Autowired
    public ChatgptDemoController(ChatgptDemoService chatgptDemoService) {
        this.chatgptDemoService = chatgptDemoService;
    }
    @PostMapping("/v1/chat/completions")
    public ChatCompletionResponse chatCompletions(@Validated @RequestBody ChatCompletionRequest request) {
        return chatgptDemoService.chatCompletions(request);
    }
    @PostMapping("/v1/completions")
    public CompletionResponse completions(@Validated @RequestBody CompletionRequest request) {
        return chatgptDemoService.completions(request);
    }
    @PostMapping("/v1/edits")
    public EditResponse edits(@Validated @RequestBody EditRequest request) {
        return chatgptDemoService.edits(request);
    }
    @PostMapping("/v1/images/generations")
    public ImageGenerationResponse imageGenerations(@Validated @RequestBody ImageGenerationRequest request) {
        return chatgptDemoService.imageGenerations(request);
    }
}

```

在这里，我们用的接口路径，依然和OpenAI的API保持一致，便于我们的理解。

接下来，基于封装好的框架，我们用几个常见的例子，来实际调用一下。

1. 把自然语言转换成程序代码：我们利用API 来编写“hello world”程序。

请求参数如下：

```xml
POST http://localhost:8080/v1/chat/completions
Content-Type: application/json

{
    "apiKey": "sk-xxxxxx",
    "content": "Please output helloworld in Java"
}

```

在这里我们本地启动Springboot项目，传入 apiKey（填入在OpenAI官网上申请的Open\_API\_KEY，均为sk前缀开头）。content字段则敲入自然语言表达我们的意图。

返回结果如下：

````xml
HTTP/1.1 200
Content-Type: application/json
Transfer-Encoding: chunked
Date: Tue, 02 May 2023 00:42:59 GMT
Connection: close
{
  "content": "Here's the code to output \"Hello World\" in Java:\n\n```\npublic class HelloWorld {\n  public static void main(String[] args) {\n    System.out.println(\"Hello World\");\n  }\n}\n```"
}

````

通过返回结果可以看出，返回值在一个字段中以字符串形式完整返回，代码是可以正常运行的。

2. 生成SQL语句

SQL也是开发过程中不可绕过的一个话题，同样地，我们可以借助API帮我们编写SQL语句。在这里我们测试一个简单的场景：在学生表中查询所有学生的姓名。

请求参数如下：

```xml
POST http://localhost:8080/v1/chat/completions
Content-Type: application/json

{
    "apiKey": "sk-xxxxxx",
    "content": "Please select all students' name from Student table in SQL"
}

```

返回结果如下：

```xml
HTTP/1.1 200
Content-Type: application/json
Transfer-Encoding: chunked
Date: Tue, 02 May 2023 00:50:11 GMT
Connection: close
{
  "content": "SELECT name FROM Student;"
}

```

3. 查找图片

我们还可以通过描述查询对应的图片，一般描述越精确，图片准确度越高。你可以看一下这个示例。

请求参数：

```xml
POST http://localhost:8080/v1/images/generations
Content-Type: application/json

{
    "apiKey": "sk-xxxxxx",
    "prompt": "find a tiger image",
    "n": 1
}

```

返回参数如下：

```xml
HTTP/1.1 200
Content-Type: application/json
Transfer-Encoding: chunked
Date: Tue, 02 May 2023 04:12:48 GMT
Connection: close
{
  "urls": [
    "https://oaidalleapiprodscus.blob.core.windows.net/private/org-mnyBsdtqxGUtwxCfi4SnEVIR/user-TapQIQ3nCgz483OGGnKll1N3/img-szYL9tqKuKPKZ00ywwofigLY.png?st=2023-05-02T03%3A12%3A48Z&se=2023-05-02T05%3A12%3A48Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-05-01T17%3A37%3A04Z&ske=2023-05-02T17%3A37%3A04Z&sks=b&skv=2021-08-06&sig=qnREx8BFjeikttJyA71Qp4WrXT3RuvRHhzU1xUr1Le8%3D"
  ]
}

```

可以看到，返回值中返回了URL的数组，这个URL对应的图片与请求参数中的语义尽可能保持一致，而返回的URL个数则取决于请求参数中n的值。

4. 拼写检查

拼写错误也是我们经常会遇到的场景，而且总是难以发现。正好有个接口可以帮我们校验拼写错误。

请求参数如下：

```xml
POST http://8.218.233.184:8080/v1/edits
Content-Type: application/json

{
    "apiKey": "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",
    "input": "It is an rainn day",
    "instruction": "Fix the spell mistakes"
}

```

返回参数如下：

```xml
HTTP/1.1 200
Content-Type: application/json
Transfer-Encoding: chunked
Date: Tue, 02 May 2023 05:25:38 GMT
Connection: close
{
  "text": "It is a rainy day\n"
}

```

可以看到，这个接口纠正了我们两处拼写错误。

5. 为代码添加注释

我们写的代码，一样可以被分析，下面是一个简单的冒泡排序算法的实现。不过为了解析方便，我们用了很多换行符来把多行代码压缩到一行了。

请求参数：

```xml
POST http://localhost:8080/v1/edits
Content-Type: application/json

{
    "apiKey": "sk-xxxxx",
    "input": "public static void sort(int[] arrays) { \nif (arrays.length == 0) { \nreturn;  \n}  \nfor (int i = 0; i < arrays.length; i++) {  \nfor (int j = 0; j < i; j++) { \nif (arrays[j] > arrays[j + 1]) { \n  int temp = arrays[j];       \narrays[j] = arrays[j + 1];       \narrays[j + 1] = temp;\n}\n}\n}\n}",
    "instruction": "Explain this Java code"
}

```

返回参数如下：

```xml
HTTP/1.1 200
Content-Type: application/json
Transfer-Encoding: chunked
Date: Tue, 02 May 2023 23:45:37 GMT
Connection: close
{
  "text": "/** Java\nI discovered this code from a tutorial from edx from Havard but the idea is based of \ntheese steps:\n1) Complete these steps in the *sort* method:\n* Compare the first two elements of the array\n* If elem 1 is greater than elem 2, swap them\n* Repeat this step until all pairs are sorted\n* Repeat this step while traversing the array\n\n2) Complete these steps in the *sort2* method:\n* Create the two arrays needed (one with the first half the size of the original array, one with the \nsecond half of the array)\n* Use a for loop to find the first half of the array\n* Use another for loop to find the second half of the array\n\n3) Complete the rest of the *mergeSortedArrays* method\n* Merge the arrays back into a single sorted array\n*/\n\n// Try recreating it without looking at the code\n\npublic static void sort(int[] arrays) { \nif (arrays.length == 0) { \nreturn; \n}\nfor (int i = 0; i < arrays.length; i++) { \n    for (int j = 0; j < i; j++) {\n        if (arrays[j] > arrays[j + 1]) {\n        int temp = arrays[j];      \n        arrays[j] = arrays[j + 1];       \n        arrays[j + 1] = temp;\n       }\n    }\n }\n}\n}\n\n/**\nThis algorithm can also sort lists but to use list you have to type this code at the top\npublic static void sort(List<Integer> list) {\t\nThis is how array list works: \nFirst is the value of the array and the array name which is list, in the similiar fashion\nof calling a array and giving it a value.\n\npublic static void main(String[] args) {\n    List<Integer> list = new ArrayList<>();\n    list.add(10);\n    list.add(5);\n    list.add(1);\n    list.add(12);\n    list.add(6);\t\nSo you call a add function from ArrayList and set the number to the array list,\nalthough this is not setting the values it is just an example.\n\nint[] arrays = new int[]{10, 5, 1, 12, 6};\nsort(arrays);\nfor (int elem:arrays) {\n    System.out.print(elem + \" \");\n}  \nThis code is basically traversing through the array to print the output and to add the sort function\nand it prints out this output: 1 5 6 10 12 (To show that it is sorted)\n\nThe intarray code is similiar but it defines the construtor of the array and gives it a \nvalue like this: new int []{10, 5, 1, 12, 6}\n\nThe sort function is is sorted algorithm which is just one function of the sort method.\nHowever, to get this work without the arrays you have to call a public static void\nsort method but with a list instead or you varible name for the array.\nExample:      \npublic static void sort(List<Integer> varible) {\n\nCreated a mergeSortedArrays\n\nif (firstArray.length == 0 || secondArray.length == 0'd) {\n    return;  \n    }  \n\nThis makes sure that nothing is printed if the first array length or second array\nlength is empty.\n\nint[] mergedArray = new int[firstArray.length + secondArray.length];\nint firstArrayPointer = 0;\nint secondArrayPointer = 0;\t\nAs said above, we stick values to the array to merge into a storeage usage. The first part\nis the array name which is mergedArray and the second is the value. The plus method is used to \nadd variables and make them a whole array.\n\nfor (int mergedArrayPointer = 0; mergedArrayPointer < firstArray.length \n                            + secondArray.length; mergedArrayPointer++) {\n\tThis code is saying is that if the count of the array pointer is going to be smaller that\n\tthe leangth of the firstArray and secondArray then the array pointer is going to count \n\tand only going to contine to one not adding any more to the count.\n\tsecondArrayPointer++ means adding one more to the count and on so forth. \n\t\n\tmergedArray[mergedArrayPointer] = (firstArray[firstArrayPointer] <= \n                       secondArray[secondArrayPointer])?firstArray[firstArrayPointer\n                                      ]:secondArray[secondArrayPointer];\t\nIf the value of firstArray is greater than secondArrayPointer OR equal to then it is going to\nmerge to the mergedArray so we got an array sorting inside another array. \n */\n"
}

```

可以看到返回内容非常多，不仅给出了测试用例，还详细解释了每一行的功能。给人的感觉就是，它真的读懂了我们的代码。

## 小结

好了，这就是这节课的主要内容，最后我们来总结一下。

这节课我们了解了OpenAI的API的基础能力，包括内容生成、摘要、分类及语义分析、翻译等等。我也带你一步步实现了在程序中调用OpenAI的API，还用它完成了很多任务，比如写代码、生成SQL语句、查找图片、检查拼写等等。利用好这些能力能够帮助我们程序员省去很多繁琐的工作，所以我们要更加积极地去拥抱这个变化。

我们可以将GPT作为我们编程的助手来提高工作效率，如编写标准程序单元、测试用例、生成注释说明，之后还可以进一步利用它来构建低代码平台和工具集，基于它训练特定业务领域的大模型。我们一起参与这个过程，会让新时代来得更早、更快。

最后我想用软件大师Alan Kay的话来结束这节课的内容，“The best way to predict the future is to invent it.”。

如果你觉得这节课的内容对你有帮助的话，可以分享给你的朋友，同时也欢迎你把你的感悟和思考分享到评论区和我讨论。