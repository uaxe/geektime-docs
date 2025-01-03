你好！我是Barry。

通过前面课程的数据库实战，相信你已经能熟练应用数据库了。接下来,我们就来学习功能接口模块化开发。

为什么需要模块化开发呢？随着Flask项目的程序越来越复杂，我们在项目开发和迭代管理上都会成倍消耗精力。为了提升效率，就需要对项目里的请求方法进行封装管理，并且把项目划分成多个单独的功能模块，让每个模块负责不同的处理功能，再通过路由分配把各模块连接成一个完整的Flask项目。

那么在Flask框架中，我们如何实现模块化呢？这就要用到今天要学的内容——蓝图和红图了。

## 什么是蓝图？

我们先通过一个案例，来了解一下蓝图能为我们解决什么问题。

### 案例解析

在我们的视频项目中，包含了首页、分区列表、视频详情等模块，我们先看看代码实现。

```plain
源程序app.py文件:
from flask import Flask

app=Flask(__name__)

@app.route('/')
def VideoIndex():
    return 'VideoIndex'

@app.route('/VideoList')
def VideoList():
    return 'VideoList'

@app.route('/VideoDetail')
def VideoDetail():
    return 'VideoDetail'

if __name__=='__main__':
    app.run()

```

按照常规的编写逻辑，这时候我们需要在app.py文件中再定义添加、修改、发布的实现方法，代码如下。

```plain
源程序app.py文件:
from flask import Flask

app=Flask(__name__)

@app.route('/')
def VideoIndex():
    return 'VideoIndex'

@app.route('/VideoList')
def VideoList():
    return 'VideoList'

@app.route('/VideoDetail')
def VideoDetail():
@app.route('/')
def admin_home():
    return 'admin_home'

@app.route('/add')
def new():
    return 'add'

@app.route('/edit')
def edit():
    return 'edit'

@app.route('/publish')
def publish():
    return 'publish'

if __name__=='__main__':
    app.run()

```

像上面这种情况，我们需要在文件内写大量的路由，内容繁杂不说，整个功能模块管理起来也极其不友好。

这时就要引入 **模块化的思维**，引入Flask内置模块化处理的类Blueprint，也就是蓝图。

我们来看看优化之后的代码实现是什么样，后面是app.py文件的具体代码。

```plain
源程序app.py文件:
from flask import Flask

app=Flask(__name__)

@app.route('/')
def VideoIndex():
    return 'VideoIndex'

@app.route('/VideoList')
def VideoList():
    return 'VideoList'

@app.route('/VideoDetail')
def VideoDetail():
    return 'VideoDetail'

if __name__=='__main__':
    app.run()


//  admin.py文件，进行模块化分别管理
@app.route('/')
def admin_home():
    return 'admin_home'

@app.route('/add')
def new():
    return 'add'

@app.route('/edit')
def edit():
    return 'edit'

@app.route('/publish')
def publish():
    return 'publish'

```

像上面这样，我们可以用蓝图把每个项目的每个模块当作一个独立的app，这里的 app 是一个 Flask 应用对象，用于管理应用程序的各个方面，如路由、模板、中间件等。 然后把功能模块拆分开。这样不管在编写过程里，还是后期维护时模块划分都更加清晰，也更有利于项目模块的管理。

到了这里，你应该对蓝图的思想有了初步的概念： **通过蓝图，开发者能够把项目中的应用拆分成不同组件，并完成对各个应用的控制和实现。**

### 蓝图概念

了解了蓝图可以解决的问题之后，现在我们一起来揭开蓝图的面纱，看看它的定义和属性。

**我们可以把蓝图理解成一个操作方法的集合容器，各个模块的路由都会绑定在该模块的蓝图上。** Flask可以通过蓝图来组织URL和处理请求，这就是蓝图的概念。

例如，视频模块的路由只放在视频模块的蓝图上，用户模块的路由放在用户模块的蓝图上。

你可以结合后面的图解加深印象。

![](https://static001.geekbang.org/resource/image/be/5f/bea166f905819cca33eb407cc5b0165f.jpg?wh=1811x1268)

了解了概念后，我们还必须全面掌握蓝图的属性，方便以后去编写和设计蓝图。

首先，我们要知道，一个应用中不是只能定义一个蓝图。你可以根据你的模块需求定义多个蓝图；还可以将一个Blueprint注册到任何一个未使用的URL下，例如 “/”、或者子域名。

其次，在一个应用中，你的每一个模块都可以注册多次。这样的设计模式可以根据需求做多次拆分，让应用管理更细致。

最后，蓝图在实现的过程中，可以单独具有自己的模板、静态文件或者其它的通用操作方法，它并不是必须要实现应用的视图和函数。当然这时你要记住，在一个应用初始化时，就应该要注册需要使用的Blueprint。

此外，我们还需要注意，单独的Blueprint并不代表一个完整的app，换句话说，蓝图不可以独立运行，不可以独立应用，必须注册在某个应用之下。

### 初识蓝图

理解了蓝图的概念和属性，想要进一步认识它，还是要结合例子。接下来我用伪代码写一个单文件，带你看一下蓝图究竟长什么样子，要怎么用。蓝图的使用和Flask对象差不多，最大的区别是蓝图对象没有办法独立运行，必须将它注册到一个应用对象上才能生效。

我们先来初始化一个蓝图，导入Blueprint。其中的video就是我们指定的模块名称，\_\_name\_\_代表模块的地址。

```plain
from flask import Blueprint //导入蓝图
video=Blueprint('video',__name__)

```

然后我们可以像往常写项目一样，定义各个功能模块的路由。有了这个蓝图对象，我们就可以像 app 加路由一样把它 “.route” 一下。这时我们调用了蓝图的对象，让它只注册路由指定静态文件夹，然后注册模块过滤器。后续我们可以在里面写上对应的视图函数，让它处理相应的业务逻辑。

```plain
//注册与业务逻辑
@admin.route('/')
def video_index():
    return 'video_index'

//注册蓝图，并且指定前缀
app.register_blueprint(video,url_prefix='/admin')

```

最后，别忘了在我们的 app 里面注册蓝图，让你定义的蓝图的路径，也就是接口能够挂载到我们的 app下。注册的时候也可以指定访问路由的前缀。

### 重要规则

看完伪代码你是不是想直接动手改造代码了？别着急，想要更好运用蓝图，还得多多了解蓝图的“游戏规则”，即实现蓝图的规则、设计方式、命名方式。掌握了这些前置规则，后面使用蓝图的时候才能少踩坑。

#### 运行机制

蓝图运行机制分为以下四点。

**第一，蓝图保存了一组可以在应用对象上执行的操作，注册路由就是其中的一种。** 它的意思是，我们注册蓝图之后，就可以根据蓝图来写相应的接口了。接下来通过蓝图中定义的URL，就可以调用应用下模块的功能接口，直接访问该模块的视图函数并处理相应的请求。

**第二，在应用对象上调用 route 装饰器完成注册后，这个操作将修改对象的 url\_map，也就是我们存储的路由。url\_map就是路由的映射关系表**，有了它才能根据访问请求里的访问接口找到对应的视图函数。

**第三，蓝图对象本来没有路由表，** 当我们在蓝图对象上调用route装饰器注册路由时，它只是在内部的延迟操作记录列表defered\_functions中添加了一个项，在蓝图的底层代码中会有一些相应的方法。然后， **执行注册路由时defered\_functions会存储在表中对应的位置**，以便后续处理相应业务逻辑时，defered\_functions能找到对应的视图函数。

第四：执行注册蓝图的注册方法，就是从 **这个蓝图对象的defered\_functions 列表中取出每一项，把它作为参数，然后执行该匿名函数（也就是这个注册方法）。** 执行函数的过程实际上就是调用蓝图这个方法实现了对add\_url\_rule的加入。然后我们再修改应用对象，这样就把最后的路由表修改成了总的路由表。最后根据这种映射关系来即可找到对应的路由，让项目能够跑起来。

#### 蓝图的URL前缀

我们在应用对象上注册一个蓝图时，还要着重关注一下蓝图的前缀，这样我们在注册和命名的过程中才能更好地封装路由。

具体做法就是在应用最终的路由表 url\_map 中，指定一个url\_prefix关键字参数（这个参数默认是/）。这个前缀将会自动添加到之后注册的URL上，这样即使多个蓝图定义了相同URL，也不会发生冲突。

我们这就结合代码示例看一下。

```plain
// url_for

url_for('admin.index') # /admin/

```

通过这种方式来获取我们的接口，然后访问蓝图的视图函数，你就能找到对应的一个接口，可以看到你的路由是什么。当然也可以通过url\_for倒推查找视图函数，直接找到你对应的 URL 。

说到URL，蓝图中必不可少的还有静态路由，接下来我们一起看看如何注册静态路由。

#### 注册静态路由

和应用对象不同，蓝图在对象创建时不会默认注册静态目录的路由，而是需要我们在创建时指定 static\_admin目录，将其设置为静态目录。

我们看看下面的示例，这段代码将蓝图所在目录下的static\_admin目录设置成了静态目录。

```plain

admin = Blueprint("admin",__name__,static_folder='static_admin')
app.register_blueprint(admin,url_prefix='/admin')

```

有了前面的设置，现在我们就可以使用/admin/static\_admin/ 来访问static\_admin目录下的静态文件了。定制静态目录URL规则就是，在创建蓝图对象时使用 static\_url\_path 改变静态目录的路由。

就像后面的例子这样，把 static\_admin 文件夹的路由设置为 /lib即可指定 admin 的静态文件。

```plain

admin = Blueprint("admin",__name__,static_folder='static_admin',static_url_path='/lib')
app.register_blueprint(admin,url_prefix='/admin')

```

静态文件static\_folder可以指定蓝图静态文件。对应到视图文件里就是：如果你注册时设置了 URL 前缀，之后访问这个蓝图下面的所有接口时，都需要在前面单独再加一个前缀，这样所有的接口都会有统一的前缀。

在静态文件中还可以看到指定的静态路由，如果没手动添加过，它可能就是 “static\_folder” 前面的 static。 如果你写了前缀，就可能会改变静态路由的接口写法，通过这种方式来修改。

### 项目操练环节

接下来我们来尝试实操一下怎么搭建蓝图，帮助你更全面地掌握蓝图。话不多说，我们按步骤分解一下。

第一步，在项目的app文件之下创建一个index package。\_ _init_\_.py文件之下的代码如下所示。

```plain
app的__init__.py文件
from flask import Blueprint //导入蓝图

index_blu = Blueprint('index', __name__) //实例化Blueprint对象 同时指定模块名index，同时指向当前文件

```

第二步，还是在 index package 下创建一个视图文件views.py。为了满足文件查找需求，需要在我们的init文件中导入视图文件，代码如下。

```plain
app/index/__init__.py文件

from flask import Blueprint //导入蓝图
from . import views // 导入视图文件

index_blu = Blueprint('index', __name__) //实例化Blueprint对象 同时指定模块名index，同时指向当前文件

```

第三步就是定义视图函数。由于视图函数对应蓝图模块，所以这里面肯定需要蓝图对象。你需要把你的蓝图对象 index\_blu 导入进来，视图函数会通过装饰器路由route去找到下一个路由的地址。

我们直接指定一个 ‘/’， def 是一个 index ，然后我们 return 一个 index，这个index是已经创建好了的路由。下面是具体的代码实现。

```plain
views.py文件

from app.index import index_blu //导入Blueprint

@index_blu.route('/') //使用装饰器进行定义route
def index():
  return 'index'

```

定义好了视图函数后，第四步就是在app的\_\_init\_\_.py下注册蓝图。

```plain
app/__init__.py

from app.index import index_blu //导入Blueprint
app.register_blueprint(index_blu)

```

第五步，在manager.py直接右键选择 run manager，这时我们就可以在控制台上看到启动的地址，如下图所示。

![](https://static001.geekbang.org/resource/image/3d/e0/3df45f5b39b88da01748571yy26df7e0.jpg?wh=2861x691)

然后我们直接通过浏览器访问 “127.0.0.1:5000” 页面的index，效果图如下。

![](https://static001.geekbang.org/resource/image/1f/fd/1f59442cdf57f1d2ed087815649cc9fd.jpg?wh=2861x691)

到这里就代表我们成功完成了蓝图的搭建，在之后的项目中你就可以应用起来了。当然，我们后边做功能实践时，它也是必要的模块。

## 什么是红图？

通过前面的学习我们知道蓝图是模块级别的拆分，但是它的设计不是用来拆分视图函数的。那如果我们要实现比模块级别更细分的视图函数的拆分，又该怎么办呢？这时就要用到红图了。

当然使用红图也是基于蓝图的。红图就是在蓝图的基础上又分了一层，负责实现比模块级别更具体的视图拆分，这就是红图的价值所在。

我给你画了一个简单的层级关系图，在红图层之下就是视图函数，这一点非常好理解。

![](https://static001.geekbang.org/resource/image/a7/8c/a760d476860071c8bb049d152627a88c.jpg?wh=1920x852)

我们这就来看看红图的实现，全面了解它的运行机制。

### 红图的实现

我们首先需要了解蓝图的route方法，这是红图对象创建的前置知识。我们直接来看源码。

```plain

def route(self, rule, **options):
    def decorator(f):
        endpoint = options.pop("endpoint", f.__name__)
        self.add_url_rule(rule, endpoint, f, **options)
        return f
    return decorator

```

我来解读一下这段代码。蓝图的route实现就是内部调用了add\_url\_rule方法。它的参数 rule就是我们装饰器中定义的URL，这也就是装饰器所作用的方法；endpoint我们直接复用即可，\*\*options 其实就是一系列关键字参数。

我们来梳理一下流程，装饰器接收了一组参数，并且调用了add\_url\_rule方法完成视图函数向蓝图的注册。我们要让红图的route代替蓝图的route，就需要在我们的Redprint里把视图函数注册到蓝图里去，因为要传参f嘛，实现形式我们通过模仿蓝图得到。过程你可以参考后面的代码。

```plain
class Redprint:
    def __init__(self, name):
        self.name = name
        self.mound = []  # 把参数记录下来
        pass

    def route(self, endpoint, f, **options):
        def decorator(f):
            self.mound.append((f, rule, options))  # self是蓝图对象，以元组形式添加到列表中
            return f
        return decorator

    def register(self)
        pass

```

到这里，我们对红图已经有一个较为全面的了解了，接下来我们进入实操练习环节。

### 代码实操环节

**第一步，我们需要在app/api/lib目录下创建一个红图类的包文件，将其命名为redprint**。 \_ _init_\_.py文件内容放的就是红图的类，因为我们之后要调用它，代码如下。

```plain
redprint/__init__.py文件：

class Redprint:
    def __init__(self, name):
        self.name = name
        self.mound = []  # 把参数记录下来
        pass

    def route(self, endpoint, f, **options):
        def decorator(f):
            self.mound.append((f, rule, options))  # self是蓝图对象，以元组形式添加到列表中
            return f
        return decorator

    def register(self)
        pass

```

**第二步**，因为红图是依附于蓝图之下的，所以我们先模拟创建好蓝图V1和V2，这一步你直接在api文件下新建即可。重点在创建蓝图这部分，具体代码与之前的创建相似。

```plain
v1/__init__.py

from flask import Blueprint
//创建V1蓝图
def creat_blueprint_v1():
  bp_v1 = Blueprint('v1',__name__)
  return bp_v1

```

有一点相当重要，我提醒你一下，一定要记得 **在app下注册蓝图**，这样之后你才能访问到对应的URL。

```plain
api/__init__.py

from flask import Flask
from app.index import index_blu //导入Blueprint

app = Flask(__name__)

//注册蓝图
//先导入
from app.v1 improt creat_blueprint_v1
//注册蓝图,并且制定前缀"v1"
app.register_blueprint(creat_blueprint_v1(), url_prefix='/v1')

```

**第三步，我们在v1蓝图下新建两个红图模块，将其命名为user.py和admin.py.。** 这一步我们相当于对蓝图V1进行了分层。

```plain
user.py文件
// 因为红图类是我们自己创建的，所以我们要使用创建的红图
// 我们先来导入红图类包
from app.lib.redprint import Redprint

// 定义红图
api = Redprint('user')

//定义路由
@api.route('/')
def user_index():
  return 'user_index'
--------------------------------------------------------------------

admin.py文件
from app.lib.redprint import Redprint

// 定义红图
api = Redprint('admin')

//定义路由
@api.route('/')
def admin_index():
  return 'admin _index'


```

**第四步，** 将我们的红图对象注册在蓝图上。

```plain
v1/__init__.py

from flask import Blueprint
导入user、admin 红图对象
from app.v1 improt user,admin
//创建V1蓝图
def creat_blueprint_v1():
  bp_v1 = Blueprint('v1',__name__)
  //将红图对象使用register方法注册到蓝图上
  user.api.register(bp_v1, url_prefix='/user') //使用url_prefix指定前缀
  admin.api.register(bp_v1, url_prefix='/admin')
  return bp_v1

```

**第五步**，直接启动命令在浏览器中查看效果。

![](https://static001.geekbang.org/resource/image/28/64/28da069049083e5aa282cdafaaf85164.jpg?wh=2861x571)

这里有个容易踩坑的地方，那就是访问路径。我们已经看到启动的地址为 **127.0.0.1:5000**，但是直接访问你会发现浏览器是 “Not found”，这时候你应该想到，我们在注册蓝图时已经指定了访问前缀，所以应该访问的是 “ **127.0.0.1:5000/v1/user**” 这个域名，访问后你会在浏览器中看到页面的效果。

![](https://static001.geekbang.org/resource/image/ba/fb/ba36c41463a0ec7e963ce996c10abafb.jpg?wh=2861x653)

进行到这一步，说明操作就成功了，现在你就可以在项目里使用红图了。

## 总结

好，我们来做个总结回顾。

除了要明白红蓝图的属性以及它们解决了哪些问题，更重要的是如何把红蓝图熟练用起来。所以最后我重点带你梳理总结一下蓝图创建的过程，关键动作有三步。

首先，创建蓝图对象。

```plain
from flask import Blueprint
# 创建蓝图对象,设置访问前缀,所有的访问该蓝图的请求都需要加上/admin
admin_blu = Blueprint("admin", __name__, url_prefix="/admin")
from .import views

```

其次，注册定义视图文件。

```plain
from app.index import index_blu //导入Blueprint

@index_blu.route('/') //使用装饰器进行定义route
def index():
  return 'index'

```

最后，在程序实例中注册该蓝图。

```plain
# 注册admin蓝图对象
from api.modules.admin import admin_blu
app.register_blueprint(admin_blu)

```

当然，只记住这关键的内容还不够，我建议你自己尝试按课程讲解的内容，进行全链路的实践，这样可以掌握得更扎实。

红图可以实现比模块级别更细分的视图函数的拆分。整体实现的逻辑也是模仿了蓝图route设计原理，进一步对模块层级进行分层，把业务对象的函数拆分开，让项目模块化的管理更精细。你掌握蓝图之后，红图应用起来就没什么难度了，重点同样是实现过程。

下节课我们继续学习 “Restful API与Flask-Restful”，敬请期待。

## 思考题

如果在user.py红图模块下再创建一个route，命名为massage，你觉得这时浏览器访问的地址应该是怎样的呢？ **如果我们就以 “127.0.0.1:5000” 为案例，那这个路由地址最后是什么样子呢？**

欢迎你在留言区和我交流互动。如果这节课对你有启发，也欢迎你转发给朋友、同事，说不定就能帮他解决疑问。