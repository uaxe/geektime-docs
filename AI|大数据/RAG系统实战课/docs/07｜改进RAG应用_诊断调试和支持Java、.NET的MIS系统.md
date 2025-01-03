你好，我是叶伟民。

上一节课我们完成了实战案例1的代码。然而这只是个demo，如果要支持更多的用例，支持更多的模块，我们需要添加更多选项序号和提示。

但是这又会引起一个新问题，用户在用我们系统的时候，你并没有在旁边看着，你怎么知道如何添加这些内容呢？你又怎么知道如何改进呢？

这就是我们今天要讨论的主题——诊断与调试。我们先开始第一步，查看用户的提问。

## 查看用户的提问

前面我们已经把对话记录保存在数据库里面了。现在，我们只需要在管理员界面添加相关模块就可以查看它们了。

### 启用管理员界面

首先，我们需要启用管理员界面。

我们打开 **实战案例1\\改造前\\mysite\\urls.py** 文件。然后把第7行的注释取消掉。

```python
from django.contrib import admin
from django.urls import include, path

app_name = "home"
urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
]

```

然后重新运行，打开浏览器，导航到 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)。将会出现以下界面。

![](https://static001.geekbang.org/resource/image/af/5e/af5e0cf631fa0218145081yyae66f25e.jpg?wh=1990x715)

然后我们还需要添加管理员，设置管理员密码，才能登录管理员界面。

### 添加管理员

我们回到 **Anaconda Powershell Prompt**。按ctrl+c停止运行，然后输入以下命令。

```python
python manage.py createsuperuser

```

这时将会出现以下提示。

![](https://static001.geekbang.org/resource/image/d5/bb/d5484c0cc53e805caaa87356892b63bb.jpg?wh=1946x117)

我们输入admin。然后在接下来的Email Address输入 “admin@admin.com”。

Password和Password(again)都输入admin。如果需要跳过密码验证这一步，这里输入y。

如果一切顺利，将会提示超级用户创建成功。

![图3](https://static001.geekbang.org/resource/image/27/b3/270b8556157a3ea4764b703eab229eb3.jpg?wh=1139x101)

然后我们重新运行，打开浏览器，导航到 [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)。用户名输入admin，密码输入admin，点击登录。

然后我们将会看到如下界面。

![](https://static001.geekbang.org/resource/image/38/53/38e6a3097fd1b95b1041b7cc42532753.jpg?wh=975x341)

### 在管理员界面添加对话记录模块

不过，现在这个管理员界面并没有地方可以查看对话记录。我们还需要在管理员界面添加对话记录模块。

我们打开实战案例1\\改造前\\home\\admin.py文件。在文件尾部添加以下代码。

```python
from .models import 对话记录

class 对话记录Admin(admin.ModelAdmin):
    ordering = ["created_time"]
    list_display = ['已结束','created_time','不带入大模型对话中','role', 'content', '处理后content','提交给大模型的payload']
    search_fields = ['已结束']
    list_filter = ('已结束',)

admin.site.register(对话记录, 对话记录Admin)

```

这段代码很好理解，其中第1行导入对话记录模型。第3行到第7行声明了对话记录模块在管理员界面里面的表现方式。第9行将对话记录模块注册到了管理员界面。

添加完刚才的代码，我们重新运行，打开浏览器登录管理员界面。这时将会看到以下界面。

![](https://static001.geekbang.org/resource/image/e7/3e/e79f8yy27a2cdf29c01080c204b4383e.jpg?wh=968x393)

点击“对话记录”来链接之后，我们可以看到后面这几项内容。

首先是用户的对话记录。

![](https://static001.geekbang.org/resource/image/98/ae/98b9037edae77c1c5b9e87c2623c13ae.jpg?wh=1934x581)

然后是大模型返回的结构化结果和AI处理后的结果。

![](https://static001.geekbang.org/resource/image/68/7a/689db3be08a01d3232b212d2fa4c487a.jpg?wh=1624x450)

另外还有提交给大模型的payload。

![](https://static001.geekbang.org/resource/image/yy/d2/yyf0c4e6c3b09697ed5ac84157801dd2.jpg?wh=1938x490)

细心的同学可能会注意到，提交给大模型的payload里面的文字是乱码，这样是否会影响到调试和诊断呢？

实际上，我们并不需要查看这些文字，我一般只关心payload里面有多少条messages，前面的内容在提交时有没有遗漏。如果你一定要查看，网上有很多unicode转中文的小工具，自行搜索一下就会发现很多。

现在我们可以根据前面这些信息来改进我们的RAG质量。和我们上节课讲的一样，如果示例不够多，那就加示例；如果对大模型结果做的进一步处理不到位，那就加上对应代码；如果大模型还是出现其他意外，那就参考之前 [第五节课“](https://time.geekbang.org/column/article/807859) 让大模型不要那么啰嗦”一节中所说的，添加更多指令。

讲到这里，我们实战案例1的相关代码都讲解完了。但是目前的代码还很乱。因此，我们需要整理一下代码。

## 整理一下代码

我们可以使用python的region关键词将同一类型的函数归类到一起。我们用VSCode打开项目以后，就可以使用ctrl+shift+a快捷键把

**rag.py文件** 的代码按region折叠。这时代码将会变成后面这样。

![](https://static001.geekbang.org/resource/image/27/71/2778b117f180084825cf7f1592273971.jpg?wh=1990x1265)

你可以在 [这里](https://github.com/weiminye/time-geekbang-org-rag/blob/main/%E5%AE%9E%E6%88%98%E6%A1%88%E4%BE%8B1/%E6%94%B9%E9%80%A0%E5%90%8E/home/rag.py) 查看完整的rag.py代码。另外，我们会在这门专栏的最后一节课使用AI帮助我们认真的重构代码。

## 如何将本实战案例代码重用到你的MIS系统？

这里还有一个问题，有很多MIS系统并非使用Python编写，而是使用Java或.NET编写。那么如何将本实战案例的代码重用到你的MIS系统呢？

其中一个方案是将这个实战案例的代码从Python改成Java或.NET。然而AI基本是Python的世界，要想在AI的大道上走得更远，我并不建议你采用这个方案。

还有一个方案就是将现有的MIS系统从Java或.NET全部改成Python。这个方案工程量实在是太大，风险实在是太高。我也不建议你采用这个方案。

另一个方案是将这个实战案例的功能开放成API接口，提供给现有的MIS系统调用。这个方案是比较可行的，我们现在就来动手做做！

### 新增接口

我们在 **实战案例1\\改造后\\home** 目录下新增一个文件，命名为 **views\_api.py**。然后添加后面的代码。

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from .rag import *
def 开始新的对话api(request):
    开始新的对话()
    return JsonResponse({"code":200,"message":"已经成功开始新的对话"})

@csrf_exempt
def 获取结构化数据查询参数api(request):
    用户输入 = request.POST['question']

    查询参数 = 获取结构化数据查询参数(用户输入)
    return JsonResponse({"querydata":查询参数})

def 从数据库查不到相关数据时的操作api(request):
    从数据库查不到相关数据时的操作()
    return JsonResponse({"code":200,"message":"已经成功执行从数据库查不到相关数据时的操作"})

@csrf_exempt
def 根据查询结果回答用户输入api(request):
    用户输入 = request.POST['question']
    查询结果 = request.POST['query-result']

    根据查询结果回答用户输入(查询结果,用户输入)
    return JsonResponse({"code":200,"message":"已经成功根据查询结果回答用户输入"})

def 获取对话记录api(request):
    conversation_list = 获取当前对话记录()
    conversation_list_json = serializers.serialize("json", list(conversation_list))
    return JsonResponse({"conversationlist":conversation_list_json})

```

以上代码总共有5个接口，接口的功能都是我们之前接触过的。

除了新增接口，我们还需要修改rag.py和views.py文件。

第一处要修改的是 **开始新的对话** 函数。原因是views\_api.py和views.py都重用了这个函数。首先我们打开views.py文件，将newtalk函数修改成以下模样。

```python
def newtalk(request):
    开始新的对话()
    return redirect(reverse('home:index'))

```

现在我们看到，第2行代码已经和接口文件里面的代码一样了。

然后打开rag.py文件，在文件尾部新增这个函数。

```python
def 开始新的对话():
  未结束的对话 = 对话记录.objects.filter(已结束=False)
  for current in 未结束的对话:
      current.已结束 = True
  对话记录.objects.bulk_update(未结束的对话, ['已结束'])

```

其实就是将这段原来在views.py文件的代码移到了rag.py文件，从而让views\_api.py和views.py能够共用它。

第二处是将获取当前对话记录的代码从views.py文件移到了rag.py文件，从而让views\_api.py和views.py共用它。也就是说，我们首先需要在rag.py文件尾部新增这个函数。

```python
def 获取当前对话记录():
  return 对话记录.objects.filter(已结束=False).order_by('created_time')

```

然后将views.py文件的index函数改成如下模样。

```python
def index(request):
    if request.method == 'POST':
        用户输入 = request.POST['question']

        查询参数 = 获取结构化数据查询参数(用户输入)
        查询结果 = None
        if 查询参数 is not None:
            查询结果 = 查询(查询参数)

        if 查询结果 is None:
            从数据库查不到相关数据时的操作()
        else:
            查询结果json格式 = serializers.serialize("json", list(查询结果))
            根据查询结果回答用户输入(查询结果json格式,用户输入)

    conversation_list = 获取当前对话记录()
    return render(request, "home/index.html",{"object_list":conversation_list})

```

第16行就是我们修改的地方。

然而细心的同学会发现，第13行也有变化。是的，这就是我们第三处需要修改的地方，把我们这个Python MIS系统才支持的功能从rag.py文件移出来。

我们需要打开rag.py文件，把将查询结果转为字符串函数修改成以下模样。

```python
def 将查询结果转为字符串(查询结果):
  return_str = ""
  data = json.loads(查询结果)
  for current in data:
    if 'fields' in current:
      for key, value in current['fields'].items():
        return_str += f"{key}：{value}\n"
    else:
      for key, value in current.items():
        return_str += f"{key}：{value}\n"
  return return_str

```

我们可以看到，其实就是把原来的第2行代码从rag.py文件移到了views.py文件的index函数。

现在我们已经编写完API接口了，我们还需要注册这些接口，才能让外部调用它们。

### 注册接口

我们打开 **home\\urls.py** 文件，在第11行之前插入以下代码。

```python
path("api/new-talk", views_api.开始新的对话api, name="api-new-talk"),
path("api/get-query-paras", views_api.获取结构化数据查询参数api, name="api-get-query-paras"),
path("api/answer-without-data", views_api.从数据库查不到相关数据时的操作api, name="api-answer-without-data"),
path("api/answer-with-data", views_api.根据查询结果回答用户输入api, name="api-answer-with-data"),
path("api/get-conversation-list", views_api.获取对话记录api, name="api-get-conversation-list"),

```

### 测试接口

现在我们已经注册完接口了，我们重新运行，然后测试接口。

这里需要我们打开postman，输入以下接口url、提交方法和提交数据。然后进行测试。

![](https://static001.geekbang.org/resource/image/e7/ef/e7f1bc1f62bb19fa1c55964d120744ef.jpg?wh=6781x3336)

需要注意的是， **在测试第2和第5个接口时，我们的key和value是需要添加body里面的，并且数据提交类型下拉列表要选form-data。**

![](https://static001.geekbang.org/resource/image/89/6b/89f2f5175ee2fbe62bb7c51223a1c36b.jpg?wh=1990x878)

完成这些操作后，你的Java或者.NET MIS系统就能通过以上接口调用我们的实战案例了。

至此，我们的实战案例1就结束了。完整的代码可以在 [这里](https://github.com/weiminye/time-geekbang-org-rag) 下载。

希望你通过这个实战案例能够说服你的利益相关者，说服他支持改造现有的MIS系统，从而真正进入生成式AI这条热门赛道。

## 小结

好了，今天这一讲到这里就结束了，最后我们来回顾一下。这一讲我们学会了两件事情。

第一件事情是通过查看用户的提问来改进我们的RAG应用。我们可以在管理员界面查看用户的提问，借此改进我们的RAG应用。

第二件事情是如何将实战案例1的代码重用到你的MIS系统。我们可以把rag.py文件里面的函数包装成http接口对外开放，这样你的MIS系统可以通过调用这些http接口来实现RAG功能了。

## 思考题

为了教学方便，代码中的数据库字段都是使用中文，但是实际工作中基本是英文，所以传给大模型的都会是英文而不是中文，如何处理这个问题？

欢迎你在留言区和我交流互动，如果这节课对你有启发，也推荐分享给身边更多朋友。