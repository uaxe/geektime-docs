你好，我是王新栋。

如果你是一个第三方软件开发者，在实现用户登录的逻辑时，除了可以让用户新注册一个账号再登录外，还可以接入微信、微博等平台，让用户使用自己的微信、微博账号去登录。同时，如果你的应用下面又有多个子应用，还可以让用户只登录一次就能访问所有的子应用，来提升用户体验。

这就是联合登录和单点登录了。再继续深究，它们其实都是OpenID Connect（简称OIDC）的应用场景的实现。那OIDC又是什么呢？

今天，我们就来学习下OIDC和OAuth 2.0的关系，以及如何用OAuth 2.0来实现一个OIDC用户身份认证协议。

## OIDC是什么？

OIDC其实就是一种用户身份认证的开放标准。使用微信账号登录极客时间的场景，就是这种开放标准的实践。

说到这里，你可能要发问了：“不对呀，使用微信登录第三方App用的不是OAuth 2.0开放协议吗，怎么又扯上OIDC了呢？”

没错，用微信登录某第三方软件，确实使用的是OAuth 2.0。但OAuth2.0是一种授权协议，而不是身份认证协议。OIDC才是身份认证协议，而且是基于OAuth 2.0来执行用户身份认证的互通协议。更概括地说，OIDC就是直接基于OAuth 2.0 构建的身份认证框架协议。

换种表述方式， **OIDC=授权协议+身份认证**，是OAuth 2.0的超集。为方便理解，我们可以把OAuth 2.0理解为面粉，把OIDC理解为面包。这下，你是不是就理解它们的关系了？因此，我们说“第三方App使用微信登录用到了OAuth 2.0”没有错，说“使用到了OIDC”更没有错。

考虑到单点登录、联合登录，都遵循的是OIDC的标准流程，因此今天我们就讲讲如何利用OAuth2.0来实现一个OIDC，“高屋建瓴” 地去看问题。掌握了这一点，我们再去做单点登录、联合登录的场景，以及其他更多关于身份认证的场景，就都不再是问题了。

## OIDC 和 OAuth 2.0 的角色对应关系

说到“如何利用 OAuth 2.0 来构建 OIDC 这样的认证协议”，我们可以想到一个切入点，这个切入点就是OAuth 2.0 的四种角色。

OAuth 2.0的授权码许可流程的运转，需要资源拥有者、第三方软件、授权服务、受保护资源这4个角色间的顺畅通信、配合才能够完成。如果我们要想在OAuth 2.0的授权码许可类型的基础上，来构建 OIDC 的话，这4个角色仍然要继续发挥 “它们的价值”。那么，这4个角色又是怎么对应到OIDC中的参与方的呢？

那么，我们就先想想一个关于身份认证的协议框架，应该有什么角色。你可能已经想出来了，它需要一个登录第三方软件的最终用户、一个第三方软件，以及一个认证服务来为这个用户提供身份证明的验证判断。

没错，这就是OIDC的三个主要角色了。在OIDC的官方标准框架中，这三个角色的名字是：

- EU（End User），代表最终用户。
- RP（Relying Party），代表认证服务的依赖方，就是上面我提到的第三方软件。
- OP（OpenID Provider），代表提供身份认证服务方。

EU、RP和OP这三个角色对于OIDC非常重要，我后面也会时常使用简称来描述，希望你能先记住。

现在很多App都接入了微信登录，那么微信登录就是一个大的身份认证服务（OP）。一旦我们有了微信账号，就可以登录所有接入了微信登录体系的App（RP），这就是我们常说的联合登录。

现在，我们就借助极客时间的例子，来看一下OAuth 2.0的4个角色和OIDC的3个角色之间的对应关系：

![](https://static001.geekbang.org/resource/image/8f/e9/8f794280f949862af3ebdc61d69c5fe9.png?wh=1424*468)

## OIDC 和 OAuth 2.0 的关键区别

看到这张角色对应关系图，你是不是有点 “恍然大悟” 的感觉：要实现一个OIDC协议，不就是直接实现一个OAuth 2.0协议吗。没错，我在这一讲的开始也说了，OIDC就是基于OAuth 2.0来实现的一个身份认证协议框架。

我再继续给你画一张OIDC的通信流程图，你就更清楚OIDC和OAuth 2.0的关系了：

![](https://static001.geekbang.org/resource/image/23/4b/23ce63497f6734dbc6dc9c5b6399c54b.png?wh=1644*1032)

可以发现，一个基于授权码流程的OIDC协议流程，跟OAuth 2.0中的授权码许可的流程几乎完全一致，唯一的区别就是多返回了一个 **ID\_TOKEN**，我们称之为 **ID令牌**。这个令牌是身份认证的关键。所以，接下来我就着重和你讲一下这个令牌，而不再细讲OIDC的整个流程。

### OIDC 中的ID令牌生成和解析方法

在图2的OIDC通信流程的第6步，我们可以看到ID令牌（ID\_TOKEN）和访问令牌（ACCESS\_TOKEN）是一起返回的。关于为什么要同时返回两个令牌，我后面再和你分析。我们先把焦点放在ID令牌上。

我们知道，访问令牌不需要被第三方软件解析，因为它对第三方软件来说是不透明的。但ID令牌需要能够被第三方软件解析出来，因为第三方软件需要获取ID令牌里面的内容，来处理用户的登录态逻辑。

那 **ID令牌的内容是什么呢**？

首先，ID令牌是一个JWT格式的令牌。你可以到 [第4讲](https://time.geekbang.org/column/article/257747) 中复习下JWT的相关内容。这里需要强调的是，虽然JWT令牌是一种自包含信息体的令牌，为将其作为ID令牌带来了方便性，但是因为ID令牌需要能够标识出用户、失效时间等属性来达到身份认证的目的，所以要将其作为OIDC的ID令牌时，下面这5个JWT声明参数也是必须要有的。

- iss，令牌的颁发者，其值就是身份认证服务（OP）的URL。
- sub，令牌的主题，其值是一个能够代表最终用户（EU）的全局唯一标识符。
- aud，令牌的目标受众，其值是三方软件（RP）的app\_id。
- exp，令牌的到期时间戳，所有的ID令牌都会有一个过期时间。
- iat，颁发令牌的时间戳。

生成ID令牌这部分的示例代码如下：

```
//GENATE ID TOKEN
String id_token=genrateIdToken(appId,user);

private String genrateIdToken(String appId,String user){
    String sharedTokenSecret="hellooauthhellooauthhellooauthhellooauth";//秘钥
    Key key = new SecretKeySpec(sharedTokenSecret.getBytes(),
            SignatureAlgorithm.HS256.getJcaName());//采用HS256算法

    Map<String, Object> headerMap = new HashMap<>();//ID令牌的头部信息
    headerMap.put("typ", "JWT");
    headerMap.put("alg", "HS256");

    Map<String, Object> payloadMap = new HashMap<>();//ID令牌的主体信息
    payloadMap.put("iss", "http://localhost:8081/");
    payloadMap.put("sub", user);
    payloadMap.put("aud", appId);
    payloadMap.put("exp", 1584105790703L);
    payloadMap.put("iat", 1584105948372L);

    return Jwts.builder().setHeaderParams(headerMap).setClaims(payloadMap).signWith(key,SignatureAlgorithm.HS256).compact();
}

```

接下来，我们再看看 **处理用户登录状态的逻辑是如何处理的**。

你可以先试想一下，如果 “不跟OIDC扯上关系”，也就是 “单纯” 构建一个用户身份认证登录系统，我们是不是得保存用户登录的会话关系。一般的做法是，要么放在远程服务器上，要么写进浏览器的cookie中，同时为会话ID设置一个过期时间。

但是，当我们有了一个JWT这样的结构化信息体的时候，尤其是包含了令牌的主题和过期时间后，不就是有了一个“天然”的会话关系信息么。

所以，依靠JWT格式的ID令牌，就足以让我们解决身份认证后的登录态问题。这也就是为什么在OIDC协议里面要返回ID令牌的原因， **ID令牌才是OIDC作为身份认证协议的关键所在**。

那么有了ID令牌后，第三方软件应该如何解析它呢？接下来，我们看一段解析ID令牌的具体代码，如下：

```
private Map<String,String> parseJwt(String jwt){
        String sharedTokenSecret="hellooauthhellooauthhellooauthhellooauth";//密钥
        Key key = new SecretKeySpec(sharedTokenSecret.getBytes(),
                SignatureAlgorithm.HS256.getJcaName());//HS256算法

        Map<String,String> map = new HashMap<String, String>();
        Jws<Claims> claimsJws = Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(jwt);
        //解析ID令牌主体信息
        Claims body = claimsJws.getBody();
        map.put("sub",body.getSubject());
        map.put("aud",body.getAudience());
        map.put("iss",body.getIssuer());
        map.put("exp",String.valueOf(body.getExpiration().getTime()));
        map.put("iat",String.valueOf(body.getIssuedAt().getTime()));

        return map;
    }

```

需要特别指出的是，第三方软件解析并验证ID令牌的合法性之后，不需要将整个JWT信息保存下来，只需保留JWT中的PAYLOAD（数据体）部分就可以了。因为正是这部分内容，包含了身份认证所需要的用户唯一标识等信息。

另外，在验证JWT合法性的时候，因为ID令牌本身已经被身份认证服务（OP）的密钥签名过，所以关键的一点是合法性校验时需要做签名校验。具体的加密方法和校验方法，你可以回顾下 [第4讲](https://time.geekbang.org/column/article/257747)。

这样当第三方软件（RP）拿到ID令牌之后，就已经获得了处理身份认证标识动作的信息，也就是拿到了那个能够唯一标识最终用户（EU）的ID值，比如3521。

### 用访问令牌获取ID令牌之外的信息

但是，为了提升第三方软件对用户的友好性，在页面上显示 “您好，3521” 肯定不如显示 “您好，小明同学”的体验好。这里的 “小明同学”，恰恰就是用户的昵称。

那如何来获取“小明同学”这个昵称呢。这也很简单，就是 **通过返回的访问令牌access\_token来重新发送一次请求**。当然，这个流程我们现在也已经很熟悉了，它属于OAuth 2.0标准流程中的请求受保护资源服务的流程。

这也就是为什么在OIDC协议里面，既给我们返回ID令牌又返回访问令牌的原因了。在保证用户身份认证功能的前提下，如果想获取更多的用户信息，就再通过访问令牌获取。在OIDC框架里，这部分内容叫做创建UserInfo端点和获取UserInfo信息。

这样看下来，细粒度地去看OIDC的流程就是： **生成ID令牌->创建UserInfo端点->解析ID令牌->记录登录状态->获取UserInfo**。

好了，利用OAuth 2.0实现一个OIDC框架的工作，我们就做完了。你可以到 [GitHub](https://github.com/xindongbook/oauth2-code/tree/master/src/com/oauth/ch09) 上查看这些流程的完整代码。现在，我再来和你小结下。

用OAuth 2.0实现OIDC的最关键的方法是：在原有OAuth 2.0流程的基础上增加ID令牌和UserInfo端点，以保障OIDC中的第三方软件能够记录用户状态和获取用户详情的功能。

因为第三方软件可以通过解析ID令牌的关键用户标识信息来记录用户状态，同时可以通过Userinfo端点来获取更详细的用户信息。有了用户态和用户信息，也就理所当然地实现了一个身份认证。

接下来，我们就具体看看如何实现单点登录（Single Sign On，SSO）。

## 单点登录

一个用户G要登录第三方软件A，A有三个子应用，域名分别是a1.com、a2.com、a3.com。如果A想要为用户提供更流畅的登录体验，让用户G登录了a1.com之后也能顺利登录其他两个域名，就可以创建一个身份认证服务，来支持a1.com、a2.com和a3.com的登录。

这就是我们说的单点登录，“一次登录，畅通所有”。

那么，可以使用OIDC协议标准来实现这样的单点登录吗？我只能说 “太可以了”。如下图所示，只需要让第三方软件（RP）重复我们OIDC的通信流程就可以了。

![](https://static001.geekbang.org/resource/image/7b/48/7bf3cb13a5174f2068c916a4d1ef2748.png?wh=1624*1272)

你看，单点登录就是OIDC的一种具体应用方式，只要掌握了OIDC框架的原理，实现单点登录就不在话下了。关于单点登录的具体实现，在GitHub上搜索“通过OIDC来实现单点登录”，你就可以看到很多相关的开源内容。

## 总结

在一些较大的、已经具备身份认证服务的平台上，你可能并没有发现OIDC的描述，但大可不必纠结。有时候，我们可能会困惑于，到底是先有OIDC这样的标准，还是先有类似微信登录这样的身份认证实现方式呢？

其实，要理解这层先后关系，我们可以拿设计模式来举例。当你想设计一个较为松耦合、可扩展的系统时，即使没有接触过设计模式，通过不断地尝试修改后，也会得出一个逐渐符合了设计模式那样“味道”的代码架构思路。理解OIDC解决身份认证问题的思路，也是同样的道理。

今天，我们在OAuth2.0的基础上实现了一个OIDC的流程，我希望你能记住以下两点。

1. **OAuth 2.0 不是一个身份认证协议**，请一定要记住这点。身份认证强调的是“谁的问题”，而OAuth2.0强调的是授权，是“可不可以”的问题。但是，我们可以在OAuth2.0的基础上，通过增加ID令牌来获取用户的唯一标识，从而就能够去实现一个身份认证协议。
2. 有些App不想非常麻烦地自己设计一套注册和登录认证流程，就会寻求统一的解决方案，然后势必会出现一个平台来收揽所有类似的认证登录场景。我们再反过来理解也是成立的。如果有个拥有海量用户的、大流量的访问平台，来 **提供一套统一的登录认证服务**，让其他第三方应用来对接，不就可以解决一个用户使用同一个账号来登录众多第三方App的问题了吗？而OIDC，就是这样的登录认证场景的开放解决方案。

说到这里，你是不是对OIDC理解得更透彻了呢？好了，让我们看看今天我为了大家留了什么思考题吧。

## 思考题

如果你自己通过OAuth 2.0来实现一个类似OIDC的身份认证协议，你觉得需要注意哪些事项呢？

欢迎你在留言区分享你的观点，也欢迎你把今天的内容分享给其他朋友，我们一起交流。