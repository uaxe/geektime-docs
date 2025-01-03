你好，我是陈航。

在上一篇文章中，我带你一起学习了Dart中异步与并发的机制及实现原理。与其他语言类似，Dart的异步是通过事件循环与队列实现的，我们可以使用Future来封装异步任务。而另一方面，尽管Dart是基于单线程模型的，但也提供了Isolate这样的“多线程”能力，这使得我们可以充分利用系统资源，在并发Isolate中搞定CPU密集型的任务，并通过消息机制通知主Isolate运行结果。

异步与并发的一个典型应用场景，就是网络编程。一个好的移动应用，不仅需要有良好的界面和易用的交互体验，也需要具备和外界进行信息交互的能力。而通过网络，信息隔离的客户端与服务端间可以建立一个双向的通信通道，从而实现资源访问、接口数据请求和提交、上传下载文件等操作。

为了便于我们快速实现基于网络通道的信息交换实时更新App数据，Flutter也提供了一系列的网络编程类库和工具。因此在今天的分享中，我会通过一些小例子与你讲述在Flutter应用中，如何实现与服务端的数据交互，以及如何将交互响应的数据格式化。

## Http网络编程

我们在通过网络与服务端数据交互时，不可避免地需要用到三个概念：定位、传输与应用。

其中， **定位**，定义了如何准确地找到网络上的一台或者多台主机（即IP地址）； **传输**，则主要负责在找到主机后如何高效且可靠地进行数据通信（即TCP、UDP协议）；而 **应用**，则负责识别双方通信的内容（即HTTP协议）。

我们在进行数据通信时，可以只使用传输层协议。但传输层传递的数据是二进制流，如果没有应用层，我们无法识别数据内容。如果想要使传输的数据有意义，则必须要用到应用层协议。移动应用通常使用HTTP协议作应用层协议，来封装HTTP信息。

在编程框架中，一次HTTP网络调用通常可以拆解为以下步骤：

1. 创建网络调用实例client，设置通用请求行为（如超时时间）；
2. 构造URI，设置请求header、body；
3. 发起请求, 等待响应；
4. 解码响应的内容。

当然，Flutter也不例外。在Flutter中，Http网络编程的实现方式主要分为三种：dart:io里的HttpClient实现、Dart原生http请求库实现、第三方库dio实现。接下来，我依次为你讲解这三种方式。

### HttpClient

HttpClient是dart:io库中提供的网络请求类，实现了基本的网络编程功能。

接下来，我将和你分享一个实例，对照着上面提到的网络调用步骤，来演示HttpClient如何使用。

在下面的代码中，我们创建了一个HttpClien网络调用实例，设置了其超时时间为5秒。随后构造了Flutter官网的URI，并设置了请求Header的user-agent为Custom-UA。然后发起请求，等待Flutter官网响应。最后在收到响应后，打印出返回结果：

```
get() async {
  //创建网络调用示例，设置通用请求行为(超时时间)
  var httpClient = HttpClient();
  httpClient.idleTimeout = Duration(seconds: 5);

  //构造URI，设置user-agent为"Custom-UA"
  var uri = Uri.parse("https://flutter.dev");
  var request = await httpClient.getUrl(uri);
  request.headers.add("user-agent", "Custom-UA");

  //发起请求，等待响应
  var response = await request.close();

  //收到响应，打印结果
  if (response.statusCode == HttpStatus.ok) {
    print(await response.transform(utf8.decoder).join());
  } else {
    print('Error: \nHttp status ${response.statusCode}');
  }
}

```

可以看到，使用HttpClient来发起网络调用还是相对比较简单的。

这里需要注意的是，由于网络请求是异步行为，因此 **在Flutter中，所有网络编程框架都是以Future作为异步请求的包装**，所以我们需要使用await与async进行非阻塞的等待。当然，你也可以注册then，以回调的方式进行相应的事件处理。

### http

HttpClient使用方式虽然简单，但其接口却暴露了不少内部实现细节。比如，异步调用拆分得过细，链接需要调用方主动关闭，请求结果是字符串但却需要手动解码等。

http是Dart官方提供的另一个网络请求类，相比于HttpClient，易用性提升了不少。同样，我们以一个例子来介绍http的使用方法。

首先，我们需要将http加入到pubspec中的依赖里：

```
dependencies:
  http: '>=0.11.3+12'

```

在下面的代码中，与HttpClient的例子类似的，我们也是先后构造了http网络调用实例和Flutter官网URI，在设置user-agent为Custom-UA后，发出请求，最后打印请求结果：

```
httpGet() async {
  //创建网络调用示例
  var client = http.Client();

  //构造URI
  var uri = Uri.parse("https://flutter.dev");

  //设置user-agent为"Custom-UA"，随后立即发出请求
  http.Response response = await client.get(uri, headers : {"user-agent" : "Custom-UA"});

  //打印请求结果
  if(response.statusCode == HttpStatus.ok) {
    print(response.body);
  } else {
    print("Error: ${response.statusCode}");
  }
}

```

可以看到，相比于HttpClient，http的使用方式更加简单，仅需一次异步调用就可以实现基本的网络通信。

### dio

HttpClient和http使用方式虽然简单，但其暴露的定制化能力都相对较弱，很多常用的功能都不支持（或者实现异常繁琐），比如取消请求、定制拦截器、Cookie管理等。因此对于复杂的网络请求行为，我推荐使用目前在Dart社区人气较高的第三方dio来发起网络请求。

接下来，我通过几个例子来和你介绍dio的使用方法。与http类似的，我们首先需要把dio加到pubspec中的依赖里：

```
dependencies:
  dio: '>2.1.3'

```

在下面的代码中，与前面HttpClient与http例子类似的，我们也是先后创建了dio网络调用实例、创建URI、设置Header、发出请求，最后等待请求结果：

```
void getRequest() async {
  //创建网络调用示例
  Dio dio = new Dio();

  //设置URI及请求user-agent后发起请求
  var response = await dio.get("https://flutter.dev", options:Options(headers: {"user-agent" : "Custom-UA"}));

 //打印请求结果
  if(response.statusCode == HttpStatus.ok) {
    print(response.data.toString());
  } else {
    print("Error: ${response.statusCode}");
  }
}

```

> 这里需要注意的是，创建URI、设置Header及发出请求的行为，都是通过dio.get方法实现的。这个方法的options参数提供了精细化控制网络请求的能力，可以支持设置Header、超时时间、Cookie、请求方法等。这部分内容不是今天分享的重点，如果你想深入理解的话，可以访问其 [API文档](https://github.com/flutterchina/dio#dio-apis) 学习具体使用方法。

对于常见的上传及下载文件需求，dio也提供了良好的支持：文件上传可以通过构建表单FormData实现，而文件下载则可以使用download方法搞定。

在下面的代码中，我们通过FormData创建了两个待上传的文件，通过post方法发送至服务端。download的使用方法则更为简单，我们直接在请求参数中，把待下载的文件地址和本地文件名提供给dio即可。如果我们需要感知下载进度，可以增加onReceiveProgress回调函数：

```
//使用FormData表单构建待上传文件
FormData formData = FormData.from({
  "file1": UploadFileInfo(File("./file1.txt"), "file1.txt"),
  "file2": UploadFileInfo(File("./file2.txt"), "file1.txt"),

});
//通过post方法发送至服务端
var responseY = await dio.post("https://xxx.com/upload", data: formData);
print(responseY.toString());

//使用download方法下载文件
dio.download("https://xxx.com/file1", "xx1.zip");

//增加下载进度回调函数
dio.download("https://xxx.com/file1", "xx2.zip", onReceiveProgress: (count, total) {
	//do something
});

```

有时，我们的页面由多个并行的请求响应结果构成，这就需要等待这些请求都返回后才能刷新界面。在dio中，我们可以结合Future.wait方法轻松实现：

```
//同时发起两个并行请求
List<Response> responseX= await Future.wait([dio.get("https://flutter.dev"),dio.get("https://pub.dev/packages/dio")]);

//打印请求1响应结果
print("Response1: ${responseX[0].toString()}");
//打印请求2响应结果
print("Response2: ${responseX[1].toString()}");

```

此外，与Android的okHttp一样，dio还提供了请求拦截器，通过拦截器，我们可以在请求之前，或响应之后做一些特殊的操作。比如可以为请求option统一增加一个header，或是返回缓存数据，或是增加本地校验处理等等。

在下面的例子中，我们为dio增加了一个拦截器。在请求发送之前，不仅为每个请求头都加上了自定义的user-agent，还实现了基本的token认证信息检查功能。而对于本地已经缓存了请求uri资源的场景，我们可以直接返回缓存数据，避免再次下载：

```
//增加拦截器
dio.interceptors.add(InterceptorsWrapper(
    onRequest: (RequestOptions options){
      //为每个请求头都增加user-agent
      options.headers["user-agent"] = "Custom-UA";
      //检查是否有token，没有则直接报错
      if(options.headers['token'] == null) {
        return dio.reject("Error:请先登录");
      }
      //检查缓存是否有数据
      if(options.uri == Uri.parse('http://xxx.com/file1')) {
        return dio.resolve("返回缓存数据");
      }
      //放行请求
      return options;
    }
));

//增加try catch，防止请求报错
try {
  var response = await dio.get("https://xxx.com/xxx.zip");
  print(response.data.toString());
}catch(e) {
  print(e);
}

```

需要注意的是，由于网络通信期间有可能会出现异常（比如，域名无法解析、超时等），因此我们需要使用try-catch来捕获这些未知错误，防止程序出现异常。

除了这些基本的用法，dio还支持请求取消、设置代理，证书校验等功能。不过，这些高级特性不属于本次分享的重点，故不再赘述，详情可以参考dio的 [GitHub主页](https://github.com/flutterchina/dio/blob/master/README-ZH.md) 了解具体用法。

## JSON解析

移动应用与Web服务器建立好了连接之后，接下来的两个重要工作分别是：服务器如何结构化地去描述返回的通信信息，以及移动应用如何解析这些格式化的信息。

### 如何结构化地描述返回的通信信息？

在如何结构化地去表达信息上，我们需要用到JSON。JSON是一种轻量级的、用于表达由属性值和字面量组成对象的数据交换语言。

一个简单的表示学生成绩的JSON结构，如下所示：

```
String jsonString = '''
{
  "id":"123",
  "name":"张三",
  "score" : 95
}
''';

```

需要注意的是，由于Flutter不支持运行时反射，因此并没有提供像Gson、Mantle这样自动解析JSON的库来降低解析成本。在Flutter中，JSON解析完全是手动的，开发者要做的事情多了一些，但使用起来倒也相对灵活。

接下来，我们就看看Flutter应用是如何解析这些格式化的信息。

### 如何解析格式化的信息？

所谓手动解析，是指使用dart:convert库中内置的JSON解码器，将JSON字符串解析成自定义对象的过程。使用这种方式，我们需要先将JSON字符串传递给JSON.decode方法解析成一个Map，然后把这个Map传给自定义的类，进行相关属性的赋值。

以上面表示学生成绩的JSON结构为例，我来和你演示手动解析的使用方法。

首先，我们根据JSON结构定义Student类，并创建一个工厂类，来处理Student类属性成员与JSON字典对象的值之间的映射关系：

```
class Student{
  //属性id，名字与成绩
  String id;
  String name;
  int score;
  //构造方法
  Student({
    this.id,
    this.name,
    this.score
  });
  //JSON解析工厂类，使用字典数据为对象初始化赋值
  factory Student.fromJson(Map<String, dynamic> parsedJson){
    return Student(
        id: parsedJson['id'],
        name : parsedJson['name'],
        score : parsedJson ['score']
    );
  }
}

```

数据解析类创建好了，剩下的事情就相对简单了，我们只需要把JSON文本通过JSON.decode方法转换成Map，然后把它交给Student的工厂类fromJson方法，即可完成Student对象的解析：

```
loadStudent() {
  //jsonString为JSON文本
  final jsonResponse = json.decode(jsonString);
  Student student = Student.fromJson(jsonResponse);
  print(student.name);
}

```

在上面的例子中，JSON文本所有的属性都是基本类型，因此我们直接从JSON字典取出相应的元素为对象赋值即可。而如果JSON下面还有嵌套对象属性，比如下面的例子中，Student还有一个teacher的属性，我们又该如何解析呢？

```
String jsonString = '''
{
  "id":"123",
  "name":"张三",
  "score" : 95,
  "teacher": {
    "name": "李四",
    "age" : 40
  }
}
''';

```

这里，teacher不再是一个基本类型，而是一个对象。面对这种情况，我们需要为每一个非基本类型属性创建一个解析类。与Student类似，我们也需要为它的属性teacher创建一个解析类Teacher：

```
class Teacher {
  //Teacher的名字与年龄
  String name;
  int age;
  //构造方法
  Teacher({this.name,this.age});
  //JSON解析工厂类，使用字典数据为对象初始化赋值
  factory Teacher.fromJson(Map<String, dynamic> parsedJson){
    return Teacher(
        name : parsedJson['name'],
        age : parsedJson ['age']
    );
  }
}

```

然后，我们只需要在Student类中，增加teacher属性及对应的JSON映射规则即可：

```
class Student{
  ...
  //增加teacher属性
  Teacher teacher;
  //构造函数增加teacher
  Student({
    ...
    this.teacher
  });
  factory Student.fromJson(Map<String, dynamic> parsedJson){
    return Student(
        ...
        //增加映射规则
        teacher: Teacher.fromJson(parsedJson ['teacher'])
    );
  }
}

```

完成了teacher属性的映射规则添加之后，我们就可以继续使用Student来解析上述的JSON文本了：

```
final jsonResponse = json.decode(jsonString);//将字符串解码成Map对象
Student student = Student.fromJson(jsonResponse);//手动解析
print(student.teacher.name);

```

可以看到，通过这种方法，无论对象有多复杂的非基本类型属性，我们都可以创建对应的解析类进行处理。

不过到现在为止，我们的JSON数据解析还是在主Isolate中完成。如果JSON的数据格式比较复杂，数据量又大，这种解析方式可能会造成短期UI无法响应。对于这类CPU密集型的操作，我们可以使用上一篇文章中提到的compute函数，将解析工作放到新的Isolate中完成：

```
static Student parseStudent(String content) {
  final jsonResponse = json.decode(content);
  Student student = Student.fromJson(jsonResponse);
  return student;
}
doSth() {
 ...
 //用compute函数将json解析放到新Isolate
 compute(parseStudent,jsonString).then((student)=>print(student.teacher.name));
}

```

通过compute的改造，我们就不用担心JSON解析时间过长阻塞UI响应了。

## 总结

好了，今天的分享就到这里了，我们简单回顾一下主要内容。

首先，我带你学习了实现Flutter应用与服务端通信的三种方式，即HttpClient、http与dio。其中dio提供的功能更为强大，可以支持请求拦截、文件上传下载、请求合并等高级能力。因此，我推荐你在实际项目中使用dio的方式。

然后，我和你分享了JSON解析的相关内容。JSON解析在Flutter中相对比较简单，但由于不支持反射，所以我们只能手动解析，即：先将JSON字符串转换成Map，然后再把这个Map给到自定义类，进行相关属性的赋值。

如果你有原生Android、iOS开发经验的话，可能会觉得Flutter提供的JSON手动解析方案并不好用。在Flutter中，没有像原生开发那样提供了Gson或Mantle等库，用于将JSON字符串直接转换为对应的实体类。而这些能力无一例外都需要用到运行时反射，这是Flutter从设计之初就不支持的，理由如下：

1. 运行时反射破坏了类的封装性和安全性，会带来安全风险。就在前段时间，Fastjson框架就爆出了一个巨大的安全漏洞。这个漏洞使得精心构造的字符串文本，可以在反序列化时让服务器执行任意代码，直接导致业务机器被远程控制、内网渗透、窃取敏感信息等操作。
2. 运行时反射会增加二进制文件大小。因为搞不清楚哪些代码可能会在运行时用到，因此使用反射后，会默认使用所有代码构建应用程序，这就导致编译器无法优化编译期间未使用的代码，应用安装包体积无法进一步压缩，这对于自带Dart虚拟机的Flutter应用程序是难以接受的。

反射给开发者编程带来了方便，但也带来了很多难以解决的新问题，因此Flutter并不支持反射。而我们要做的就是，老老实实地手动解析JSON吧。

我把今天分享所涉及到的知识点打包到了 [GitHub](https://github.com/cyndibaby905/24_network_demo) 中，你可以下载下来，反复运行几次，加深理解与记忆。

## 思考题

最后，我给你留两道思考题吧。

1. 请使用dio实现一个自定义拦截器，拦截器内检查header中的token：如果没有token，需要暂停本次请求，同时访问" [http://xxxx.com/token](http://xxxx.com/token)"，在获取新token后继续本次请求。
2. 为以下Student JSON写相应的解析类：

```
String jsonString = '''
  {
    "id":"123",
    "name":"张三",
    "score" : 95,
    "teachers": [
       {
         "name": "李四",
         "age" : 40
       },
       {
         "name": "王五",
         "age" : 45
       }
    ]
  }
  ''';

```

欢迎你在评论区给我留言分享你的观点，我会在下一篇文章中等待你！感谢你的收听，也欢迎你把这篇文章分享给更多的朋友一起阅读。