你好，我是徐昊。今天我们继续使用TDD的方式实现RESTful Web Services。

## 回顾架构愿景与任务列表

目前我们已经实现了ResourceRouter，整体的架构愿景如下：

![](https://static001.geekbang.org/resource/image/59/24/59ee2d534a4ae87623a736157e848924.jpg?wh=2284x1285)

![](https://static001.geekbang.org/resource/image/2e/a4/2ef7e84ba450b36d1df67cfce9e61da4.jpg?wh=2284x1285)

## 细化任务列表

沿着调用栈的顺序，就要进入RootResource/Resource/ResourceMethod的开发中。未经细化的任务列表如下：

- Resource/RootResource/ResourceMethod
  - 在处理请求派分时，可以支持多级子资源（Sub-Resource）
  - 在处理请求派分时，可以根据客户端提供的超媒体类型，选择对应的资源方法（Resource Method）
  - 在处理请求派分时，可以根据客户端提供的Http方法，选择对应的资源方法
  - 资源方法可以返回Java对象，由Runtime自行推断正确的返回状态
  - 资源方法可以不明确指定返回的超媒体类型，由Runtime自行推断，比如，资源方法标注了Produces标注，那么就使用标注提供的超媒体类型等
  - 资源方法可按找期望的类型，访问Http请求的内容
  - 资源对象和资源方法可接受环境组件的注入

而在当前架构愿景下，RootResource/Resource/ResourceMethod都需要使用UriTemplate、UriInfoBuilder作为支撑。其中，UriInfoBuilder还没有具体的接口设计，那么我们可以先实现UriTemplate。视频演示如下：

接下来，我们可以细化UriTemplate的任务：

- UriTemplate
  - 匹配无参数的Uri模版
    - 如果Uri可以与模版匹配，则返回匹配结果
    - 如果Uri不能与模版匹配，则返回Optional.empty
  - 匹配带参数的Uri模版
    - 如果Uri可以与模版匹配，按照指定参数从Uri中提取值
    - 参数可以通过正则表达式指定格式
    - 如果参数重复定义，则抛出异常
  - 模版匹配的结果可以比较大小
    - 如果匹配的非参字符多，则优先（长的优先）
    - 如果匹配的非参数字符一样，匹配的分组多，则优先（参数优先）
    - 如果匹配的分组一样多，指定格式参数匹配多的优先（指定格式参数优先）

## 思考题

如何根据variable获取值？

欢迎把你的想法分享在留言区，也欢迎把你的项目代码分享出来。相信经过你的思考与实操，学习效果会更好！