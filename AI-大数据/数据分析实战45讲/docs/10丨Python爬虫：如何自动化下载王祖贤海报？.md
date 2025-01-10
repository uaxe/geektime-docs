上一讲中我给你讲了如何使用八爪鱼采集数据，对于数据采集刚刚入门的人来说，像八爪鱼这种可视化的采集是一种非常好的方式。它最大的优点就是上手速度快，当然也存在一些问题，比如运行速度慢、可控性差等。

相比之下，爬虫可以很好地避免这些问题，今天我来分享下如何通过编写爬虫抓取数据。

## 爬虫的流程

相信你对“爬虫”这个词已经非常熟悉了，爬虫实际上是用浏览器访问的方式模拟了访问网站的过程，整个过程包括三个阶段：打开网页、提取数据和保存数据。

在Python中，这三个阶段都有对应的工具可以使用。

在“打开网页”这一步骤中，可以使用 Requests 访问页面，得到服务器返回给我们的数据，这里包括HTML页面以及JSON数据。

在“提取数据”这一步骤中，主要用到了两个工具。针对HTML页面，可以使用 XPath 进行元素定位，提取数据；针对JSON数据，可以使用JSON进行解析。

在最后一步“保存数据”中，我们可以使用 Pandas 保存数据，最后导出CSV文件。

下面我来分别介绍下这些工具的使用。

**Requests访问页面**

Requests是Python HTTP的客户端库，编写爬虫的时候都会用到，编写起来也很简单。它有两种访问方式：Get和Post。这两者最直观的区别就是：Get把参数包含在url中，而Post通过request body来传递参数。

假设我们想访问豆瓣，那么用Get访问的话，代码可以写成下面这样的：

```
r = requests.get('http://www.douban.com')

```

代码里的“r”就是Get请求后的访问结果，然后我们可以使用r.text或r.content来获取HTML的正文。

如果我们想要使用Post进行表单传递，代码就可以这样写：

```
r = requests.post('http://xxx.com', data = {'key':'value'})

```

这里data就是传递的表单参数，data的数据类型是个字典的结构，采用key和value的方式进行存储。

**XPath定位**

XPath是XML的路径语言，实际上是通过元素和属性进行导航，帮我们定位位置。它有几种常用的路径表达方式。

![](https://static001.geekbang.org/resource/image/3b/ea/3bcb311361c76bfbeb90d360b21195ea.jpg?wh=518*690)

我来给你简单举一些例子：

1. xpath(‘node’) 选取了node节点的所有子节点；

2. xpath(’/div’) 从根节点上选取div节点；

3. xpath(’//div’) 选取所有的div节点；

4. xpath(’./div’) 选取当前节点下的div节点；

5. xpath(’…’) 回到上一个节点；

6. xpath(’//@id’) 选取所有的id属性；

7. xpath(’//book\[@id\]’) 选取所有拥有名为id的属性的book元素；

8. xpath(’//book\[@id=“abc”\]’) 选取所有book元素，且这些book元素拥有id= "abc"的属性；

9. xpath(’//book/title \| //book/price’) 选取book元素的所有title和price元素。


上面我只是列举了XPath的部分应用，XPath的选择功能非常强大，它可以提供超过100个内建函数，来做匹配。我们想要定位的节点，几乎都可以使用XPath来选择。

使用XPath定位，你会用到Python的一个解析库lxml。这个库的解析效率非常高，使用起来也很简便，只需要调用HTML解析命令即可，然后再对HTML进行XPath函数的调用。

比如我们想要定位到HTML中的所有列表项目，可以采用下面这段代码。

```
from lxml import etree
html = etree.HTML(html)
result = html.xpath('//li')

```

**JSON对象**

JSON是一种轻量级的交互方式，在Python中有JSON库，可以让我们将Python对象和JSON对象进行转换。为什么要转换呢？原因也很简单。将JSON对象转换成为Python对象，我们对数据进行解析就更方便了。

![](https://static001.geekbang.org/resource/image/9a/43/9a6d6564a64cf2b1c256265eea78c543.png?wh=477*237)

这是一段将JSON格式转换成Python对象的代码，你可以自己运行下这个程序的结果。

```
import json
jsonData = '{"a":1,"b":2,"c":3,"d":4,"e":5}';
input = json.loads(jsonData)
print input

```

接下来，我们就要进行实战了，我会从两个角度给你讲解如何使用Python爬取海报，一个是通过JSON数据爬取，一个是通过XPath定位爬取。

## 如何使用JSON数据自动下载王祖贤的海报

我在上面讲了Python爬虫的基本原理和实现的工具，下面我们来实战一下。如果想要从豆瓣图片中下载王祖贤的海报，你应该先把我们日常的操作步骤整理下来：

1. 打开网页；

2. 输入关键词“王祖贤”；

3. 在搜索结果页中选择“图片”；

4. 下载图片页中的所有海报。


这里你需要注意的是，如果爬取的页面是动态页面，就需要关注XHR数据。因为动态页面的原理就是通过原生的XHR数据对象发出HTTP请求，得到服务器返回的数据后，再进行处理。XHR会用于在后台与服务器交换数据。

你需要使用浏览器的插件查看XHR数据，比如在Chrome浏览器中使用开发者工具。

在豆瓣搜索中，我们对“王祖贤”进行了模拟，发现XHR数据中有一个请求是这样的：

[https://www.douban.com/j/search\_photo?q=%E7%8E%8B%E7%A5%96%E8%B4%A4&limit=20&start=0](https://www.douban.com/j/search_photo?q=%E7%8E%8B%E7%A5%96%E8%B4%A4&limit=20&start=0)

url中的乱码正是中文的url编码，打开后，我们看到了很清爽的JSON格式对象，展示的形式是这样的：

```
{"images":
       [{"src": …, "author": …, "url":…, "id": …, "title": …, "width":…, "height":…},
    …
	 {"src": …, "author": …, "url":…, "id": …, "title": …, "width":…, "height":…}],
 "total":22471,"limit":20,"more":true}

```

从这个JSON对象中，我们能看到，王祖贤的图片一共有22471张，其中一次只返回了20张，还有更多的数据可以请求。数据被放到了images对象里，它是个数组的结构，每个数组的元素是个字典的类型，分别告诉了src、author、url、id、title、width和height字段，这些字段代表的含义分别是原图片的地址、作者、发布地址、图片ID、标题、图片宽度、图片高度等信息。

有了这个JSON信息，你很容易就可以把图片下载下来。当然你还需要寻找XHR请求的url规律。

如何查看呢，我们再来重新看下这个网址本身。

[https://www.douban.com/j/search\_photo?q=王祖贤&limit=20&start=0](https://www.douban.com/j/search_photo?q=%E7%8E%8B%E7%A5%96%E8%B4%A4&limit=20&start=0)

你会发现，网址中有三个参数：q、limit和start。start实际上是请求的起始ID，这里我们注意到它对图片的顺序标识是从0开始计算的。所以如果你想要从第21个图片进行下载，你可以将start设置为20。

王祖贤的图片一共有22471张，你可以写个for循环来跑完所有的请求，具体的代码如下：

```
# coding:utf-8
import requests
import json
query = '王祖贤'
''' 下载图片 '''
def download(src, id):
	dir = './' + str(id) + '.jpg'
	try:
		pic = requests.get(src, timeout=10)
		fp = open(dir, 'wb')
		fp.write(pic.content)
		fp.close()
	except requests.exceptions.ConnectionError:
		print('图片无法下载')

''' for 循环 请求全部的 url '''
for i in range(0, 22471, 20):
	url = 'https://www.douban.com/j/search_photo?q='+query+'&limit=20&start='+str(i)
	html = requests.get(url).text    # 得到返回结果
	response = json.loads(html,encoding='utf-8') # 将 JSON 格式转换成 Python 对象
	for image in response['images']:
		print(image['src']) # 查看当前下载的图片网址
		download(image['src'], image['id']) # 下载一张图片

```

## 如何使用XPath自动下载王祖贤的电影海报封面

如果你遇到JSON的数据格式，那么恭喜你，数据结构很清爽，通过Python的JSON库就可以解析。

但有时候，网页会用JS请求数据，那么只有JS都加载完之后，我们才能获取完整的HTML文件。XPath可以不受加载的限制，帮我们定位想要的元素。

比如，我们想要从豆瓣电影上下载王祖贤的电影封面，需要先梳理下人工的操作流程：

1. [打开网页movie.douban.com](http://xn--movie-hr2j95qrv1e8j7b.douban.com)；

2. 输入关键词“王祖贤”；

3. 下载图片页中的所有电影封面。


这里你需要用XPath定位图片的网址，以及电影的名称。

一个快速定位XPath的方法就是采用浏览器的XPath Helper插件，使用Ctrl+Shift+X快捷键的时候，用鼠标选中你想要定位的元素，就会得到类似下面的结果。

![](https://static001.geekbang.org/resource/image/0e/c7/0e0fef601ee043f4bea8dd2874e788c7.png?wh=865*111)

XPath Helper插件中有两个参数，一个是Query，另一个是Results。Query其实就是让你来输入XPath语法，然后在Results里看到匹配的元素的结果。

我们看到，这里选中的是一个元素，我们要匹配上所有的电影海报，就需要缩减XPath表达式。你可以在Query中进行XPath表达式的缩减，尝试去掉XPath表达式中的一些内容，在Results中会自动出现匹配的结果。

经过缩减之后，你可以得到电影海报的XPath（假设为变量src\_xpath）：

```
//div[@class='item-root']/a[@class='cover-link']/img[@class='cover']/@src

```

以及电影名称的XPath（假设为变量title\_xpath）：

```
//div[@class='item-root']/div[@class='detail']/div[@class='title']/a[@class='title-text']

```

但有时候当我们直接用Requests获取HTML的时候，发现想要的XPath并不存在。这是因为HTML还没有加载完，因此你需要一个工具，来进行网页加载的模拟，直到完成加载后再给你完整的HTML。

在Python中，这个工具就是Selenium库，使用方法如下：

```
from selenium import webdriver
driver = webdriver.Chrome()
driver.get(request_url)

```

Selenium是Web应用的测试工具，可以直接运行在浏览器中，它的原理是模拟用户在进行操作，支持当前多种主流的浏览器。

这里我们模拟Chrome浏览器的页面访问。

你需要先引用Selenium中的WebDriver库。WebDriver实际上就是Selenium 2，是一种用于Web应用程序的自动测试工具，提供了一套友好的API，方便我们进行操作。

然后通过WebDriver创建一个Chrome浏览器的drive，再通过drive获取访问页面的完整HTML。

当你获取到完整的HTML时，就可以对HTML中的XPath进行提取，在这里我们需要找到图片地址srcs和电影名称titles。这里通过XPath语法匹配到了多个元素，因为是多个元素，所以我们需要用for循环来对每个元素进行提取。

```
srcs = html.xpath(src_xpath)
titles = html.xpath(title_path)
for src, title in zip(srcs, titles):
	download(src, title.text)

```

然后使用上面我编写好的download函数进行图片下载。

## 总结

好了，这样就大功告成了，程序可以源源不断地采集你想要的内容。这节课，我想让你掌握的是：

1. Python爬虫的流程；

2. 了解XPath定位，JSON对象解析；

3. 如何使用lxml库，进行XPath的提取；

4. 如何在Python中使用Selenium库来帮助你模拟浏览器，获取完整的HTML。


其中，Python + Selenium + 第三方浏览器可以让我们处理多种复杂场景，包括网页动态加载、JS响应、Post表单等。因为Selenium模拟的就是一个真实的用户的操作行为，就不用担心cookie追踪和隐藏字段的干扰了。

当然，Python还给我们提供了数据处理工具，比如lxml库和JSON库，这样就可以提取想要的内容了。

![](https://static001.geekbang.org/resource/image/eb/ab/eb3e48f714ca857a79948d831de521ab.jpg?wh=3200*1800)

最后，你不妨来实践一下，你最喜欢哪个明星？如果想要自动下载这个明星的图片，该如何操作呢？欢迎和我在评论区进行探讨。

你也可以把这篇文章分享给你的朋友或者同事，一起动手练习一下。