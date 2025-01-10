你好，我是葛俊。今天，我们继续来聊聊如何通过Git提高代码提交的原子性吧。

在上一篇文章中，我给你详细介绍了Git助力提高代码提交原子性的五条基础操作，今天我们再来看看Facebook的开发人员具体是如何使用这些操作来实现提交的原子性的。

为了帮助你更直观地理解、学习，在这篇文章里，我会与你详细描述工作场景，并列出具体命令。同时，我还把这些命令的输出也都放到了文章里，供你参考。所以，这篇文章会比较长、比较细。不过不要担心，这些内容都是日常工作中的自然流程，阅读起来也会比较顺畅。

在Facebook，开发人员最常使用两种Git工作流：

- 使用一个分支，完成所有需求的开发；
- 使用多个分支，每个分支支持一个需求的开发。

两种工作流都利用Git的超强功能来提高代码原子性。这里的“需求”包括功能开发和缺陷修复，用大写字母A、B、C等表示；每个需求都可能包含有多个提交，每个提交用需求名+序号表示。比如，A可能包含A1、A2两个提交，B只包含B1这一个提交，而C包含C1、C2、C3三个提交。

需要强调的是，这两种工作流中的一个分支和多个分支，都是在开发者本地机器上的分支，不是远程代码仓中的功能分支。我在前面 [第7篇文章](https://time.geekbang.org/column/article/132499) 中提到过，Facebook的主代码仓是不使用功能分支的。

另外，这两种Git工作流对代码提交原子性的助力作用，跟主代码仓是否使用单分支开发没有关系。也就是说，即使你所在团队的主仓没有使用Facebook那样的单分支开发模式，仍然可以使用这两种工作流来提高代码提交的原子性。

接下来，我们就先看看第一种工作流，也就是使用一个分支完成所有需求的开发。

## 工作流一：使用一个分支完成所有需求的开发

这种工作流程的最大特点是， **使用一个分支上的提交链，大量使用git rebase -i来修改提交链上的提交**。这里的提交链，指的是当前分支上，还没有推送到远端主仓共享分支的所有提交。

首先，我们需要设置一个本地分支来开发需求，通过这个分支和远端主仓的共享分支进行交互。本地分支通常直接使用master分支，而远端主仓的共享分支一般是origin/master，也叫作上游分支（upstream）。

一般来说，在git clone的时候，master是默认已经产生，并且是已经跟踪origin/master了的，你不需要做任何设置，可以查看.git/config文件做确认：

```
> cat .git/config
...
[remote "origin"]
	url = git@github.com:jungejason/git-atomic-demo.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
	remote = origin
	merge = refs/heads/master

```

可以看到，branch "master"里有一个remote = origin选项，表明master分支在跟踪origin这个上游仓库；另外，config文件里还有一个remote "origin"选项，列举了origin这个上游仓库的地址。

当然，除了直接查看config文件外，Git还提供了命令行工具。你可以使用git branch -vv查看某个分支是否在跟踪某个远程分支，然后再使用git remote show 去查看远程代码仓的细节。

```
## 查看远程分支细节
> git branch -vv
  master      5055c14 [origin/master: behind 1] Add documentation for getRandom endpoint

## 查看分支跟踪的远程代码仓细节
> git remote show origin
* remote origin
  Fetch URL: git@github.com:jungejason/git-atomic-demo.git
  Push  URL: git@github.com:jungejason/git-atomic-demo.git
  HEAD branch: master
  Remote branch:
    master tracked
  Local branches configured for 'git pull':
    master  merges with remote master
  Local ref configured for 'git push':
    master pushes to master (fast-forwardable)
11:07:36 (master2) jasonge@Juns-MacBook-Pro-2.local:~/jksj-repo/git-atomic-demo

```

因为config文件简单直观，所以我常常直接到config文件里面查看和修改来完成这些操作。关于远程跟踪上游代码仓分支的更多细节，比如产生新分支、设置上游分支等，你可以参考 [Git: Upstream Tracking Understanding](https://mincong-h.github.io/2018/05/02/git-upstream-tracking/) 这篇文章。

设置好分支之后，我们来看看 **这个工作流中的具体步骤**。

### 单分支工作流具体步骤

单分支工作流的步骤，大致包括以下4步：

1. 一个原子性的功能完成后，使用 [第25篇文章](https://time.geekbang.org/column/article/152715) 中提到的改变提交顺序的方法，把它放到距离origin/master最近的地方。
2. 把这个提交发到代码审查系统Phabricator上进行质量检查，包括代码审查和机器检查。在等待质量检查结果的同时，继续其他提交的开发。
3. 如果没有通过质量检查，则需要对提交进行修改，修改之后返回第2步。
4. 如果通过质量检查， 就把这个提交推送到主代码仓的共享分支上，然后继续其他分支的开发，回到第1步。

请注意第二步的目的是，确保入库代码的质量，你可以根据实际情况进行检查。比如，你可以通过提交PR触发机器检查的工作流，也可以运行单元测试自行检查。如果没有任何质量检查的话，至少也要进行简单手工验证，让进入到远程代码仓的代码有起码的质量保障。

接下来，我设计了一个案例，尽量模拟我在Facebook的真实开发场景，与你讲述这个工作流的操作步骤。大致场景是这样的：我本来在开发需求A，这时来了更紧急的需求B。于是，我开始开发B，把B分成两个原子性提交B1和B2，并在B1完成之后最先推送到远程代码仓共享分支。

这个案例中，提交的改动很简单，但里面涉及了很多开发技巧，可供你借鉴。

### 阶段1：开始开发需求A

某天，我接到开发需求A的任务，要求在项目中添加一个README文件，对项目进行描述。

我先添加一个简单的README.md文件，然后用git commit -am ‘readme’ 快速生成一个提交A1，确保代码不会丢失。

```
## 文件内容
> cat README.md
## This project is for demoing git

## 产生提交
> git commit -am 'readme'
[master 0825c0b] readme
 1 file changed, 1 insertion(+)
 create mode 100644 README.md

## 查看提交历史
> git log --oneline --graph
* 0825c0b (HEAD -> master) readme
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp
...

## 查看提交细节
> git show
commit 0825c0b6cd98af11b171b52367209ad6e29e38d1 (HEAD -> master)
Author: Jason Ge <gejun_1978@yahoo.com>
Date:   Tue Oct 15 12:45:08 2019

    readme

diff --git a/README.md b/README.md
new file mode 100644
index 0000000..789cfa9
--- /dev/null
+++ b/README.md
@@ -0,0 +1 @@
+## This project is for demoing git

```

这时，A1是master上没有推送到origin/master的唯一提交，也就是说，是提交链上的唯一提交。

请注意，A1的Commit Message很简单，就是“readme”这6个字符。在把A1发出去做代码质量检查之前，我需要添加Commit Message的细节。

![](https://static001.geekbang.org/resource/image/d1/0a/d14b3b23385fcb20d9a0013544a7cc0a.png?wh=542*197)

图1 提交链状态第1步

### 阶段2：开始开发需求B

这时，来了另外一个紧急需求B，要求是添加一个endpoint getRandom。开发时，我不切换分支，直接在master上继续开发。

首先，我写一个getRandom的实现，并进行简单验证。

```
## 用VIM修改
> vim index.js

## 查看工作区中的改动
> git diff
diff --git a/index.js b/index.js
index 986fcd8..06695f6 100644
--- a/index.js
+++ b/index.js
@@ -6,6 +6,10 @@ app.get('/timestamp', function (req, res) {
   res.send('' + Date.now())
 })

+app.get('/getRandom', function (req, res) {
+  res.send('' + Math.random())
+})
+
 app.get('/', function (req, res) {
   res.send('hello world')
 })

## 用命令行工具httpie验证结果
> http localhost:3000/getRandom
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 19
Content-Type: text/html; charset=utf-8
Date: Tue, 15 Oct 2019 03:49:15 GMT
ETag: W/"13-U1KCE8QRuz+dioGnmVwMkEWypYI"
X-Powered-By: Express

0.25407324324864167

```

为确保代码不丢失，我用git commit -am ‘random’ 命令生成了一个提交B1：

```
## 产生提交
> git commit -am 'random'
[master 7752df4] random
 1 file changed, 4 insertions(+)

## 查看提交历史
> git log --oneline --graph
* 7752df4 (HEAD -> master) random
* 0825c0b readme
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp
...

## 查看提交细节
> git show
commit f59a4084e3a2c620bdec49960371f8cc93b86825 (HEAD -> master)
Author: Jason Ge <gejun_1978@yahoo.com>
Date:   Tue Oct 15 11:55:06 2019

    random

diff --git a/index.js b/index.js
index 986fcd8..06695f6 100644
--- a/index.js
+++ b/index.js
@@ -6,6 +6,10 @@ app.get('/timestamp', function (req, res) {
   res.send('' + Date.now())
 })

+app.get('/getRandom', function (req, res) {
+  res.send('' + Math.random())
+})
+
 app.get('/', function (req, res) {
   res.send('hello world')
 })

```

B1的Commit Message也很简陋，因为当前的关键任务是先把功能运行起来。

现在，我的提交链上有A1和B1两个提交了。

![](https://static001.geekbang.org/resource/image/74/94/747ab78ca16aefc1f4a74a904014ae94.png?wh=773*196)

图2 提交链状态第2步

接下来，我需要进行需求B的进一步开发：在README文件中给这个新的endpoint添加说明。

```
> git diff
diff --git a/README.md b/README.md
index 789cfa9..7b2b6af 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,3 @@
 ## This project is for demoing git
+
+You can visit endpoint getRandom to get a random real number.

```

我认为这个改动是B1的一部分，所以我用git commit --amend把它添加到B1中。

```
## 添加改动到B1
> git add README.md
> git commit --amend
[master 27c4d40] random
 Date: Tue Oct 15 11:55:06 2019 +0800
 2 files changed, 6 insertions(+)

## 查看提交历史
> git log --oneline --graph
* 27c4d40 (HEAD -> master) random
* 0825c0b readme
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp

```

现在，我的提交链上还是A1和B1’两个提交。这里的B1’是为了区别之前的B1，B1仍然存在代码仓中，不过是不再使用了而已。

![](https://static001.geekbang.org/resource/image/25/37/2581e07273218b464b463cf3243a3c37.png?wh=773*197)

图3 提交链状态第3步

### 阶段3：拆分需求B的代码，把B1’提交检查系统

这时，我觉得B1’的功能实现部分，也就是index.js的改动部分，可以推送到origin/master了。

不过，文档部分也就是README.md文件的改动，还不够好，而且功能实现和文档应该分成两个原子性提交。于是，我将B1’拆分为B1’’ 和B2两部分。

```
## 将B1'拆分
> git reset HEAD^
Unstaged changes after reset:
M	README.md   ## 这个将是B2的内容
M	index.js    ## 这个将是B1''的内容

> git status
On branch master
Your branch is ahead of 'origin/master' by 1 commit.
  (use "git push" to publish your local commits)
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)
	modified:   README.md
	modified:   index.js
no changes added to commit (use "git add" and/or "git commit -a")

> git add index.js
> git commit   ## 这里我认真填写B1''的Commit Message

> git add README.md
> git commit   ## 这里我认真填写B2的Commit Message

## 查看提交历史
* 68d813f (HEAD -> master) [DO NOT PUSH] Add documentation for getRandom endpoint
* 7d43442 Add getRandom endpoint
* 0825c0b readme
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp

```

现在，提交链上有A1、B1’’、B2三个提交。

请注意，在这里我把功能实现和文档分为两个原子性提交，只是为了帮助说明我需要把B1’进行原子性拆分而已，在实际工作中，很可能功能实现和文档就应该放在一个提交当中。

![](https://static001.geekbang.org/resource/image/1a/9d/1abf304f8b1de6fcd4a1487243e4409d.png?wh=994*203)

图4 提交链状态第4步

提交B1’拆开之后，为了把B1’’ 推送到origin/master上去，我需要要把B1’’ 挪到A1的前面。首先，运行git rebase -i origin/master。

```
> git rebase -i origin/master

## 下面是弹出的编辑器
pick 0825c0b readme                   ## 这个是A1
pick 7d43442 Add getRandom endpoint   ## 这个是B1''
pick 68d813f [DO NOT PUSH] Add documentation for getRandom endpoint

# Rebase 7b6ea30..68d813f onto 7b6ea30 (3 commands)
...

```

然后，我把针对B1’’ 的那一行挪到第一行，保存退出。

```
pick 7d43442 Add getRandom endpoint  ## 这个是B1''
pick 0825c0b readme                  ## 这个是A1
pick 68d813f [DO NOT PUSH] Add documentation for getRandom endpoint

# Rebase 7b6ea30..68d813f onto 7b6ea30 (3 commands)
...

```

git rebase -i 命令会显示运行成功，使用git log命令可以看到我成功改变了提交的顺序。

```
> git rebase -i origin/master
Successfully rebased and updated refs/heads/master.

> git log --oneline --graph
* 86126f7 (HEAD -> master) [DO NOT PUSH] Add documentation for getRandom endpoint
* 7113c16 readme
* 4d37768 Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp

```

现在，提交链上有B1’’’、A1’、B2’三个提交了。请注意，B2’也是一个新的提交。虽然我只是交换了B1’’ 和A的顺序，但git rebase的操作是重新应用，产生出了三个新提交。

![](https://static001.geekbang.org/resource/image/2a/a8/2af308dacc801197e5248b49f8cc83a8.png?wh=994*204)

图5 提交链状态第5步

现在，我可以把B1’’’ 发送给质量检查系统了。

首先，产生一个临时分支temp指向B2’，确保能回到原来的代码；然后，用git reset --hard命令把master和HEAD指向B1’’’。

```
> git branch temp
> git reset --hard 4d37768
HEAD is now at 4d37768 Add getRandom endpoint

## 检查提交链
> git log --oneline --graph
* 4d37768 (HEAD -> master) Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp
...

```

这时，提交链中只有B1’’’。当然，A1’和B2’仍然存在，只是不在提交链里了而已。

![](https://static001.geekbang.org/resource/image/71/91/71b4dba396681ffcec08e912edb7b691.png?wh=541*197)

图6 提交链状态第6步

最后，运行命令把B1’’’ 提交到Phabricator上，结束后使用git reset --hard temp命令重新把HEAD指向B2’。

```
## 运行arc命令把B'''提交到Phabricator上
> arc diff

## 重新把HEAD指向B2'
> git reset --hard temp
HEAD is now at 86126f7 [DO NOT PUSH] Add documentation for getRandom endpoint

## 检查提交链
> git log --oneline --graph
* 86126f7 (HEAD -> master, temp, single-branch-step-5) [DO NOT PUSH] Add documentation for getRandom endpoint
* 7113c16 readme
* 4d37768 Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp

```

这时，提交链又恢复成为B1’’’、A1’、B2’三个提交了。

![](https://static001.geekbang.org/resource/image/91/c2/912e4a00c2d08b9d82fee818d780c0c2.png?wh=994*203)

图7 提交链状态第7步

### 阶段4：继续开发B2，同时得到B1的反馈，修改B1

把B1’’’ 发送到质量检查中心之后，我回到B2’ 继续工作，也就是在README文件中继续添加关于getRandom的文档。我正在开发的过程中，得到B1’’’ 的反馈，要求我对其进行修改。于是，我首先保存当前对B2’的修改，用git commit --amend把它添加到B2’中。

```
## 查看工作区中的修改
> git diff
diff --git a/README.md b/README.md
index 8a60943..1f06f52 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 ## This project is for demoing git

 You can visit endpoint getRandom to get a random real number.
+The end endpoint is `/getRandom`.

## 把工作区中的修改添加到B2'中
> git add README.md
> git commit --amend
[master 7b4269c] [DO NOT PUSH] Add documentation for getRandom endpoint
 Date: Tue Oct 15 17:17:18 2019 +0800
 1 file changed, 3 insertions(+)
* 7b4269c (HEAD -> master) [DO NOT PUSH] Add documentation for getRandom endpoint
* 7113c16 readme
* 4d37768 Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp
...

```

这时，提交链成为B1’’’、A1’、B2’’ 三个提交了。

![](https://static001.geekbang.org/resource/image/de/c0/de37ce76ba36c0c8ec3075a67e3a8ac0.png?wh=993*204)

图8 提交链状态第8步

接下来，我使用 [第25篇文章](https://time.geekbang.org/column/article/152715) 中介绍的基础操作对B1’’’ 进行修改。

首先，在git rebase -i origin/master的文本输入框中，将pick B1’’’ 那一行修改为edit B1’’’，然后保存退出，git rebase 暂停在B1’’’ 处：

```
> git rebase -i origin/master

## 以下是弹出编辑器中的文本内容
edit 4d37768 Add getRandom endpoint   ## <-- 这一行开头原本是pick
pick 7113c16 readme
pick 7b4269c [DO NOT PUSH] Add documentation for getRandom endpoint

## 以下是保存退出后 git rebase -i origin/master 的输出
Stopped at 4d37768...  Add getRandom endpoint
You can amend the commit now, with
  git commit --amend
Once you are satisfied with your changes, run
  git rebase --continue

## 查看提交历史
> git log --oneline --graph
* 4d37768 (HEAD) Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp

```

这时，提交链上只有B1’’’ 一个提交。

![](https://static001.geekbang.org/resource/image/6f/66/6f62dbf5e85b3f1705d4a6475ebac966.png?wh=542*146)

图9 提交链状态第9步

然后，我对index.js进行修改，并添加到B1’’’ 中，成为B1’’’’。完成之后，再次把B1’’’’ 发送到代码质量检查系统。

```
## 根据同事反馈，修改index.js
> vim index.js
> git add index.js

## 查看修改
> git diff --cached
diff --git a/index.js b/index.js
index 06695f6..cc92a42 100644
--- a/index.js
+++ b/index.js
@@ -7,7 +7,7 @@ app.get('/timestamp', function (req, res) {
 })

 app.get('/getRandom', function (req, res) {
-  res.send('' + Math.random())
+  res.send('The random number is:' + Math.random())
 })

 app.get('/', function (req, res) {

## 把改动添加到B1'''中。
> git commit --amend
[detached HEAD 29c8249] Add getRandom endpoint
 Date: Tue Oct 15 17:16:12 2019 +0800
 1 file changed, 4 insertions(+)
19:17:28 (master|REBASE-i) jasonge@Juns-MacBook-Pro-2.local:~/jksj-repo/git-atomic-demo
> git show
commit 29c82490256459539c4a1f79f04823044f382d2b (HEAD)
Author: Jason Ge <gejun_1978@yahoo.com>
Date:   Tue Oct 15 17:16:12 2019
    Add getRandom endpoint

    Summary:
    As title.

    Test:
    Verified it on localhost:3000/getRandom

diff --git a/index.js b/index.js
index 986fcd8..cc92a42 100644
--- a/index.js
+++ b/index.js
@@ -6,6 +6,10 @@ app.get('/timestamp', function (req, res) {
   res.send('' + Date.now())
 })

+app.get('/getRandom', function (req, res) {
+  res.send('The random number is:' + Math.random())
+})
+
 app.get('/', function (req, res) {
   res.send('hello world')
 })

## 查看提交链
> git log --oneline --graph
* 29c8249 (HEAD) Add getRandom endpoint
* 7b6ea30 (origin/master, git-add-p) Add a new endpoint to return timestamp

## 将B1''''发送到代码审查系统
> arc diff

```

这时，提交链只有B1’’’’ 一个提交。

![](https://static001.geekbang.org/resource/image/a1/0e/a16c37876defb48c59977c23bb86960e.png?wh=542*145)

图10 提交链状态第10步

最后，运行git rebase --continue完成整个git rebase -i操作。

```
> git rebase --continue
Successfully rebased and updated refs/heads/master.

## 查看提交历史
> git log --oneline --graph
* bc0900d (HEAD -> master) [DO NOT PUSH] Add documentation for getRandom endpoint
* 1562cc7 readme
* 29c8249 Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp
...

```

这时，提交链包含B1’’’’、A1’’、B2’’’ 三个提交。

![](https://static001.geekbang.org/resource/image/a7/fc/a72eba2775d8ebbbe0f9808cc17917fc.png?wh=993*203)

图11 提交链状态第11步

### 阶段5：继续开发A1，并发出代码审查

这时，我认为A1’’ 比B2’’’ 更为紧急重要，于是决定先完成A1’’ 的工作并发送审查，同样也是使用git rebase -i。

```
> git rebase -i HEAD^^  ## 两个^^表示从当前HEAD前面两个提交的地方rebase

## git rebase 弹出编辑窗口
edit 1562cc7 readme  <-- 这一行开头原来是pick。这个是A1''
pick bc0900d [DO NOT PUSH] Add documentation for getRandom endpoint

## 保存退出后git rebase -i HEAD^^ 的结果
Stopped at 1562cc7...  readme
You can amend the commit now, with
  git commit --amend
Once you are satisfied with your changes, run
  git rebase --continue

## 对A1''修改
> vim README.md
> git diff
diff --git a/README.md b/README.md
index 789cfa9..09bcc7d 100644
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-## This project is for demoing git
+# This project is for demoing atomic commit in git

> git add README.md
> git commit --amend

## 下面是git commit弹出编辑器，在里面完善A1''的Commit Message
Add README.md file

Summary: we need a README file for the project.

Test: none.

# Please enter the Commit Message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# Date:      Tue Oct 15 12:45:08 2019 +0800
#
# interactive rebase in progress; onto 29c8249
# Last command done (1 command done):
#    edit 1562cc7 readme
# Next command to do (1 remaining command):
#    pick bc0900d [DO NOT PUSH] Add documentation for getRandom endpoint
# You are currently splitting a commit while rebasing branch 'master' on '29c8249'.
#
# Changes to be committed:
#       new file:   README.md
#

## 保存退出后git commit 输出结果
[detached HEAD 2c66fe9] Add README.md file
 Date: Tue Oct 15 12:45:08 2019 +0800
 1 file changed, 1 insertion(+)
 create mode 100644 README.md

## 继续执行git rebase -i
> git rebase --continue
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
error: could not apply bc0900d... [DO NOT PUSH] Add documentation for getRandom endpoint
Resolve all conflicts manually, mark them as resolved with
"git add/rm <conflicted_files>", then run "git rebase --continue".
You can instead skip this commit: run "git rebase --skip".
To abort and get back to the state before "git rebase", run "git rebase --abort".
Could not apply bc0900d... [DO NOT PUSH] Add documentation for getRandom endpoint

```

这个过程可能会出现冲突，比如在A1’’’ 之上应用B2’’’ 时可能会出现冲突。冲突出现时，你可以使用git log和git status命令查看细节。

```
## 查看当前提交链
> git log --oneline --graph
* 2c66fe9 (HEAD) Add README.md file
* 29c8249 Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp
...

## 查看冲突细节
> git status
interactive rebase in progress; onto 29c8249
Last commands done (2 commands done):
   edit 1562cc7 readme
   pick bc0900d [DO NOT PUSH] Add documentation for getRandom endpoint
No commands remaining.
You are currently rebasing branch 'master' on '29c8249'.
  (fix conflicts and then run "git rebase --continue")
  (use "git rebase --skip" to skip this patch)
  (use "git rebase --abort" to check out the original branch)

Unmerged paths:
  (use "git reset HEAD <file>..." to unstage)
  (use "git add <file>..." to mark resolution)

	both modified:   README.md

no changes added to commit (use "git add" and/or "git commit -a")

## 用git diff 和git diff --cached查看更多细节
> git diff
diff --cc README.md
index 09bcc7d,1f06f52..0000000
--- a/README.md
+++ b/README.md
@@@ -1,1 -1,4 +1,8 @@@
++<<<<<<< HEAD
 +# This project is for demoing atomic commit in git
++=======
+ ## This project is for demoing git
+
+ You can visit endpoint getRandom to get a random real number.
+ The end endpoint is `/getRandom`.
++>>>>>>> bc0900d... [DO NOT PUSH] Add documentation for getRandom endpoint

> git diff --cached
* Unmerged path README.md

```

解决冲突的具体步骤是：

1. 手动修改冲突文件；
2. 使用git add或者git rm把修改添加到暂存区；
3. 运行git rebase --continue。于是，git rebase会把暂存区的内容生成提交，并继续git-rebase后续步骤。

```
> vim README.md

## 这个是初始内容
<<<<<<< HEAD
# This project is for demoing atomic commit in git
=======
## This project is for demoing git

You can visit endpoint getRandom to get a random real number.
The end endpoint is `/getRandom`.
>>>>>>> bc0900d... [DO NOT PUSH] Add documentation for getRandom endpoint

## 这个是修改后内容，并保存退出
# This project is for demoing atomic commit in git

You can visit endpoint getRandom to get a random real number.
The end endpoint is `/getRandom`.

## 添加README.md到暂存区，并使用git status查看状态
> git add README.md
19:51:16 (master|REBASE-i) jasonge@Juns-MacBook-Pro-2.local:~/jksj-repo/git-atomic-demo

## 使用git status查看状态
> git status
interactive rebase in progress; onto 29c8249
Last commands done (2 commands done):
   edit 1562cc7 readme
   pick bc0900d [DO NOT PUSH] Add documentation for getRandom endpoint
No commands remaining.
You are currently rebasing branch 'master' on '29c8249'.
  (all conflicts fixed: run "git rebase --continue")

Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

	modified:   README.md

## 冲突成功解决，继续git rebase -i后续步骤
> git rebase --continue

## git rebase 提示编辑B2''''的Commit Message
[DO NOT PUSH] Add documentation for getRandom endpoint

Summary:
AT.

Test:
None.

## 保存退出之后git rebase --continue的输出
[detached HEAD ae38d9e] [DO NOT PUSH] Add documentation for getRandom endpoint
 1 file changed, 3 insertions(+)
Successfully rebased and updated refs/heads/master.

## 检查提交链
* ae38d9e (HEAD -> master) [DO NOT PUSH] Add documentation for getRandom endpoint
* 2c66fe9 Add README.md file
* 29c8249 Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp

```

这时，提交链上有B1’’’’、A1’’’、B2’’’’ 三个提交。

![](https://static001.geekbang.org/resource/image/03/bb/034757450750df327f5a5d4f94b728bb.png?wh=993*204)

图12 提交链状态第12步

### 阶段6：B1检查通过，推送到远程代码仓共享分支

这时，我从Phabricator得到通知，B1’’’’ 检查通过了，可以将其推送到oringin/master去了！

首先，使用git fetch和git rebase origin/master命令，确保本地有远端主代码仓的最新代码。

```
> git fetch
> git rebase origin/master
Current branch master is up to date.

```

然后，使用git rebase -i，在B1’’’’ 处暂停：

```
> git rebase -i origin/master

## 修改第一行开头：pick -> edit
edit 29c8249 Add getRandom endpoint
pick 2c66fe9 Add README.md file
pick ae38d9e [DO NOT PUSH] Add documentation for getRandom endpoint

## 保存退出结果
Stopped at 29c8249...  Add getRandom endpoint
You can amend the commit now, with
  git commit --amend
Once you are satisfied with your changes, run
  git rebase --continue

## 查看提交链
* 29c8249 (HEAD) Add getRandom endpoint
* 7b6ea30 (origin/master) Add a new endpoint to return timestamp
...

```

这时，origin/master和HEAD之间只有B1’’’’ 一个提交。

![](https://static001.geekbang.org/resource/image/0d/66/0db95ca7cd433baaffe5771636cf7166.png?wh=541*145)

图13 提交链状态第13步

我终于可以运行git push origin HEAD:master，去推送B1’’’’ 了。

注意，当前HEAD不在任何分支上，master分支仍然指向B2’’’’，所以push命令需要明确指向远端代码仓origin和远端分支maser，以及本地要推送的分支HEAD。推送完成之后，再运行git rebase --continue完成rebase操作，把master分支重新指向B2’’’’。

```
## 直接推送。因为当前HEAD不在任何分支上，推送失败。
> git push
fatal: You are not currently on a branch.
To push the history leading to the current (detached HEAD)
state now, use
    git push origin HEAD:<name-of-remote-branch>

## 再次推送，指定远端代码仓origin和远端分支maser，以及本地要推送的分支HEAD。推送成功
> git push origin HEAD:master
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 392 bytes | 392.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
To github.com:jungejason/git-atomic-demo.git
   7b6ea30..29c8249  HEAD -> master

> git rebase --continue
Successfully rebased and updated refs/heads/master.

## 查看提交链
> git log --oneline --graph
* ae38d9e (HEAD -> master) [DO NOT PUSH] Add documentation for getRandom endpoint
* 2c66fe9 Add README.md file
* 29c8249 (origin/master) Add getRandom endpoint
* 7b6ea30 Add a new endpoint to return timestamp

```

这时，origin/master已经指向了B1’’’’，提交链现在只剩下了A1’’’ 和B2’’’’。

![](https://static001.geekbang.org/resource/image/5a/b3/5a1a47e2750cdcecfc764bf2d6deeab3.png?wh=772*197)

图14 提交链状态第14步

至此，我们完成了在一个分支上同时开发两个需求A和B、把提交拆分为原子性提交，并尽早把完成的提交推送到远端代码仓共享分支的全过程！

这个过程看起来比较复杂，但实际上就是根据上面列举的“单分支工作流”的4个步骤执行而已。

接下来，我们再看看使用多个分支，每个分支支持一个需求的开发方式。

## 用本地多分支实现多个需求的提交的原子性

在这种开发工作流下，每个需求都拥有独享的分支。同样的，跟单分支实现提交原子性的方式一样，这些分支都是本地分支，并不是主代码仓上的功能分支。

需要注意的是，在下面的分析中，我只描述每个分支上只有一个提交的简单形式，而至于每个分支上使用多个提交的形式，操作流程与单分支提交链中的描述一样，就不再重复表述了。

### 多分支工作流具体步骤

分支工作流的具体步骤，大致包括以下4步：

1. 切换到某一个分支对某需求进行开发，产生提交。
2. 提交完成后，将其发送到代码审查系统Phabricator上进行质量检查。在等待质量检查结果的同时，切换到其他分支，继续其他需求的开发。
3. 如果第2步的提交没有通过质量检查，则切换回这个提交所在分支，对提交进行修改，修改之后返回第2步。
4. 如果第2步的提交通过了质量检查，则切换回这个提交所在分支，把这个提交推送到远端代码仓中，然回到第1步进行其他需求的开发。

接下来，我们看一个开发两个需求C和D的场景吧。

在这个场景中，我首先开发需求C，并把它的提交C1发送到质量检查中心；然后开始开发需求D，等到C1通过质量检查之后，我立即将其推送到远程共享代码仓中去。

### 阶段1：开发需求C

需求C是一个简单的重构，把index.js中所有的var都改成const。

首先，使用git checkout -b feature-c origin/master产生本地分支feature-c，并跟踪origin/master。

```
> git checkout -b feature-c origin/master
Branch 'feature-c' set up to track remote branch 'master' from 'origin'.
Switched to a new branch 'feature-c'

```

然后，进行C的开发，产生提交C1，并把提交发送到Phabricator进行检查。

```
## 修改代码，产生提交
> vim index.js
> git diff
diff --git a/index.js b/index.js
index cc92a42..e5908f0 100644
--- a/index.js
+++ b/index.js
@@ -1,6 +1,6 @@
-var port = 3000
-var express = require('express')
-var app = express()
+const port = 3000
+const express = require('express')
+const app = express()

 app.get('/timestamp', function (req, res) {
   res.send('' + Date.now())
20:54:10 (feature-c) jasonge@Juns-MacBook-Pro-2.local:~/jksj-repo/git-atomic-demo

> git add .
20:54:16 (feature-c) jasonge@Juns-MacBook-Pro-2.local:~/jksj-repo/git-atomic-demo

> git commit

## 填写详细Commit Message
Refactor to use const instead of var

Summary: const provides more info about a variable. Use it when possible.

Test: ran `node index.js` and verifeid it by visiting localhost:3000.
Endpoints still work.

## 以下是Commit Message保存后退出，git commit的输出结果
[feature-c 2122faa] Refactor to use const instead of var
 1 file changed, 3 insertions(+), 3 deletions(-)

## 使用Phabricator的客户端，arc，把当前提交发送给Phabricator进行检查
> arc diff

## 查看提交链
* 2122faa (HEAD -> feature-c, multi-branch-step-1) Refactor to use const instead of var
* 5055c14 (origin/master) Add documentation for getRandom endpoint
...

```

这时，origin/master之上只有feature-c一个分支，上面有C1一个提交。

![](https://static001.geekbang.org/resource/image/69/b3/6953532b8a3600bbc1753dd274faafb3.png?wh=542*197)

图15 多分支提交状态第1步

### 阶段2：开发需求D

C1发出去进行质量检查后，我开始开发需求D。需求D是在README.md中，添加所有endpoint的文档。

首先，也是使用git checkout -b feature-d origin/master产生一个分支feature-d并跟踪origin/master。

```
> git checkout -b feature-d origin/master
Branch 'feature-d' set up to track remote branch 'master' from 'origin'.
Switched to a new branch 'feature-d'
Your branch is up to date with 'origin/master'.

```

然后，开始开发D，产生提交D1，并把提交发送到Phabricator进行检查。

```
## 进行修改
> vim README.md

## 添加，产生修改，过程中有输入Commit Message
> git add README.md
> git commit

## 查看修改
> git show
commit 97047a33071420dce3b95b89f6d516e5c5b59ec9 (HEAD -> feature-d, multi-branch-step-2)
Author: Jason Ge <gejun_1978@yahoo.com>
Date:   Tue Oct 15 21:12:54 2019

    Add spec for all endpoints

    Summary: We are missing the spec for the endpoints. Adding them.

    Test: none

diff --git a/README.md b/README.md
index 983cb1e..cbefdc3 100644
--- a/README.md
+++ b/README.md
@@ -1,4 +1,8 @@
 # This project is for demoing atomic commit in git

-You can visit endpoint getRandom to get a random real number.
-The end endpoint is `/getRandom`.
+## endpoints
+
+* /getRandom: get a random real number.
+* /timestamp: get the current timestamp.
+* /: get a "hello world" message.

## 将提交发送到Phabricator进行审查
> arc diff

## 查看提交历史
> git log --oneline --graph feature-c feature-d
* 97047a3 (HEAD -> feature-d Add spec for all endpoints
| * 2122faa (feature-c) Refactor to use const instead of var
|/
* 5055c14 (origin/master) Add documentation for getRandom endpoint

```

这时，origin/master之上有feature-c和feature-d两个分支，分别有C1和D1两个提交。

![](https://static001.geekbang.org/resource/image/07/cc/072e1088fd35c6afa757e01ee8819acc.png?wh=563*394)

图16 多分支提交状态第2步

### 阶段3：推送提交C1到远端代码仓共享分支

这时，我收到Phabricator的通知，C1通过了检查，可以推送了！首先，我使用git checkout把分支切换回分支feature-c：

```
> git checkout feature-c
Switched to branch 'feature-c'
Your branch is ahead of 'origin/master' by 1 commit.
  (use "git push" to publish your local commits)

```

然后，运行git fetch; git rebase origin/master，确保我的分支上有最新的远程共享分支代码：

```
> git fetch
> git rebase origin/master
Current branch feature-c is up to date.

```

接下来，运行git push推送C1：

```
> git push
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 460 bytes | 460.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
To github.com:jungejason/git-atomic-demo.git
   5055c14..2122faa  feature-c -> master

## 查看提交状态
* 97047a3 (feature-d) Add spec for all endpoints
| * 2122faa (HEAD -> feature-c, origin/master, multi-branch-step-1) Refactor to use const instead of var
|/
* 5055c14 Add documentation for getRandom endpoint
...

```

这时，origin/master指向C1。分支feature-d从origin/master的父提交上分叉，上面只有D1一个提交。

![](https://static001.geekbang.org/resource/image/07/24/0794c35efb4d17fc4a2bff67d9e83524.png?wh=563*446)

图17 多分支提交状态第3步

### 阶段4：继续开发D1

完成C1的推送后，我继续开发D1。首先，用git checkout命令切换回分支feature-d；然后，运行git fetch和git rebase，确保当前代码D1是包含了远程代码仓最新的代码，以减少将来合并代码产生冲突的可能性。

```
> git checkout feature-d
Switched to branch 'feature-d'
Your branch and 'origin/master' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" to merge the remote branch into yours)
21:38:22 (feature-d) jasonge@Juns-MacBook-Pro-2.local:~/jksj-repo/git-atomic-demo

> git fetch
> git rebase origin/master
First, rewinding head to replay your work on top of it...
Applying: Add spec for all endpoints

## 查看提交状态
> git log --oneline --graph feature-c feature-d
* a8f92f5 (HEAD -> feature-d) Add spec for all endpoints
* 2122faa (origin/master,) Refactor to use const instead of var
...

```

这时，当前分支为feature-d，上面有唯一一个提交D1’，而且D1’已经变基到了origin/master上。

需要注意的是，因为使用的是git rebase，没有使用git merge产生和并提交，所以提交历史是线性的。我在 [第7篇文章](https://time.geekbang.org/column/article/132499) 中提到过，线性的提交历史对Facebook的CI自动化意义重大。

![](https://static001.geekbang.org/resource/image/6a/5b/6af5e952f4846983e05a04b44a0db65b.png?wh=890*230)

图18 多分支提交状态第4步

至此，我们完成了在两个分支上同时开发C和D两个需求，并尽早把完成了的提交推送到远端代码仓中的全过程。

虽然在这个例子中，我简化了这两个需求开发的情况，每个需求只有一个提交并且一次就通过了质量检查，但结合在一个分支上完成所有开发需求的流程，相信你也可以推导出每个需求有多个提交，以及质量检查没有通过时的处理方法了。如果这中间还有什么问题的话，那就直接留言给我吧。

接下来，我与你对比下这两种工作流。

## 两种工作流的对比

如果我们要对比这两工作流的话，那就是各有利弊。

单分支开发方式的好处是，不需要切换分支，可以顺手解决一些缺陷修复，但缺点是rebase操作多，产生冲突的可能性大。

而多分支方式的好处是，一个分支只对应一个需求，相对比较简单、清晰，rebase操作较少，产生冲突的可能性小，但缺点是不如单分支开发方式灵活。

无论是采用哪一种工作流，都有几个需要注意的地方：

- 不要同时开发太多的需求，否则分支管理花销太大；
- 有了可以推送的提交就尽快推送到远端代码仓，从而减少在本地的管理成本，以及推送时产生冲突的可能性；
- 经常使用git fetch和git rebase，确保自己的代码在本地持续与远程共享分支的代码在做集成，降低推送时冲突的可能性

最后，我想说的是，如果你对Git不是特别熟悉，我推荐你先尝试第二种工作流。这种情况rebase操作较少，相对容易上手一些。

## 小结

今天，我与你详细讲述了，在Facebook开发人员借助Git的强大功能，实现代码提交的原子性的两种工作流。

第一种工作流是，在一个单独的分支上进行多个需求的开发。总结来讲，具体的工作方法是：把每一个需求的提交都拆分为比较小的原子提交，并使用git rebase -i的功能，把可以进行质量检查的提交，放到提交链的最底部，也就是最接近origin/master的地方，然后发送到代码检查系统进行检查，之后继续在提交链的其他提交处工作。如果提交没有通过检查，就对它进行修改再提交检查；如果检查通过，就马上把它推送到远端代码仓的共享分支去。在等待代码检察时，继续在提交链的其他提交处工作。

第二种工作流是，使用多个分支来开发多个需求，每个分支对应一个需求。与单分支开发流程类似，我们尽快把当前可以进行代码检查的提交，放到离origin/master最近的地方；然后在代码审查时，继续开发其他提交。与单分支开发流程不同的是，切换工作任务时，需要切换分支。

这两种工作流，无论哪一种都能大大促进代码提交的原子性，从而同时提高个人及团队的研发效能。

我把今天的案例放到了GitHub上的 [git-atomic-demo](https://github.com/jungejason/git-atomic-demo) 代码仓里，并标注出了各个提交状态产生的分支。比如，single-branch-step-14就是单分支流程中的第14个状态，multi-branch-step-4就是多分支流程中的第4个状态。

## 思考题

1. 在对提交链的非当前提交，比如HEAD^，进行修改时，除了使用git rebase -i，在它暂停的时候进行修改，你还其他办法吗？你觉得这种方法的利弊是什么？
2. Git和文字编排系统LaTex有一个有趣的共同点，你知道是什么吗？

感谢你的收听，欢迎你在评论区给我留言分享你的观点，也欢迎你把这篇文章分享给更多的朋友一起阅读。我们下期再见！