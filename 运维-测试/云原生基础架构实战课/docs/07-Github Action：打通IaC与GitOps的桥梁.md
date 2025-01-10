你好，我是潘野。

前面的课程里，我们学习了通过持续集成与部署的方式管理IaC代码的思路。不过知识必须学以致用，才能真正掌握。接下来的三讲内容，我们就来实操演练，学会如何使用GitOps，从而更好地管理IaC代码。

今天，我们会使用GitHub Actions这个工具来管理Terraform代码。为什么要选择GitHub Actions呢？

之前我们已经了解到，GitOps方式离不开在GitHub里管理代码。GitHub是一个广泛使用的代码托管平台，提供了许多与代码管理和协作相关的功能。而GitHub Actions是Github中自带的CI/CD工具，上手门槛较低。掌握了这个工具，能让你的管理、部署工作事半功倍。

## 基于Github Action的管理架构

在进入实操演练之前，我们需要先了解一下基于Github Action的管理架构长什么样。具体来说，就是通过Github Action来管理Terrafrom代码，并自动执行变化的代码，从而更改基础设施的架构。

![](https://static001.geekbang.org/resource/image/8c/ce/8c06230517da0ff6bfa5d7d1de1a24ce.jpg?wh=2119x1658)

对照架构图，不难看出Github Action的Terraform代码的管理主要体现在以下方面：

- 用户提交Pull Request之后，Github Action 通过OIDC的方式与AWS账户进行认证。
- 通过认证之后，Github Action执行 `terrafrom plan` 和 `terrafrom apply` 两个命令，Terrafrom会根据代码去更改基础设施配置。
- Terrafrom的状态文件会存在对象存储S3中，以便追踪Terrafrom的变化。

所以我们要做的是这么几步：

1. 配置AWS IAM权限，使得GitHub Action可以通过OIDC的方式连接上AWS
2. 创建S3存储桶，让Terraform通过Github Action的流水线将状态文件存储进S3中
3. 编写Github Action配置，实现使用Github Action来执行Terraform的操作。

那么接下来，我们就进入实战环节。

## GitHub Action如何与AWS做认证？

当我们手动执行 `terrafrom plan` 之前，需要先在AWS里的IAM中新建一个USER，并且生成一组access key，里面包含了Access Key ID，Secret Access Key。

但是这种方式存在一些弊端。首先是安全隐患。因为AWS Access Key 是以明文形式生成出来的，交给用户使用。所以，如果在使用的过程中没有规范存放，就有可能会泄露，带来安全风险。

其次，这种方式非常依赖人工检查，比较低效。AWS 建议定期更换 AWS Access Key，并且始终使用最低的必要权限来控制对 AWS Access Key 的访问。那么一旦Acess Key过期，我们又恰好忘记检查，就会导致自动化程序不可用。

所以，在GitHub上，我们可以通过使用 GitHub OIDC (OpenID Connect) 提供程序并仅允许在特定的 GitHub 操作中运行这些凭证。相比将AWS的Access Key的所有信息存储在 GitHub 密钥中，这样做更加安全且高效。

我们这就来看看GitHub OIDC是如何与AWS对接做认证的。你可以结合后面的认证流程图听我分析。

![](https://static001.geekbang.org/resource/image/e6/f8/e6ac3bebf4c110e08031c776801643f8.jpg?wh=2218x1193)

图里面序号1～5代表认证的操作步骤，我们挨个顺一遍。

1. GitHub Action 向 Github OIDC 提供商请求 JWT（Java Web Token）。
2. GitHub OIDC Provider 将签名的 JWT 发布到我们的 GitHub Action。
3. 带有我们签名的 JWT 的 GitHub Action 将向 AWS 中的 IAM 身份提供商请求临时访问令牌。
4. IAM 身份提供商将会使用 GitHub OIDC 提供商验证签名的 JWT，并验证身份提供商是否可以使用我们想要承担的角色。
5. AWS IAM基于角色的权限，给GitHub 颁发临时访问令牌。

经过这些步骤后，我们的 GitHub 操作环境就可以访问AWS的相关资源了。

OIDC provider的整个配置过程也相当简单。如下图所示，我们只需要在IAM的身份提供商里填上GitHub Action的token URL以及受众，然后点击添加提供商即可。

![](https://static001.geekbang.org/resource/image/58/f9/5887a798530f4f6af0dbdbac43cb63f9.jpg?wh=2000x2073)

最后，我们就会看到生成了一个专门用于GitHub Action的身份提供商。这样认证工作就完成了。

![](https://static001.geekbang.org/resource/image/b5/45/b589e19fa6e55f976e23c866ae0df245.jpg?wh=2000x870)

## 如何让Terrafrom将状态文件存到S3中？

我们回想一下第2讲学过的Terraform的状态管理，我曾提到状态文件管理非常重要。所以在GitHub Action中，我们需要将Terraform的状态文件存在AWS的S3中。这样既安全地存储我们的管理文件，又能让我们拥有版本追溯的能力。

#### 创建S3

我们需要先创建一个 S3 存储桶。这里有两种创建方式，我们分别看一下。

第一种方式是登陆到Web Console上创建。我们在AWS的Web Console上进入S3界面，点击创建存储桶，然后输入存储桶名称 “cloudnative-tfstate-1”。

请注意，在对象所有权这里我们要选择 ACL已禁用，因为Terraform状态的文件也需要安全保护，不能被其他人随意访问到。

![](https://static001.geekbang.org/resource/image/6b/f9/6ba2cd54128a1fe874c3082acdcf2df9.jpg?wh=2020x3401)

接着，点击启用存储桶版本，再点击默认加密启用即可。

![](https://static001.geekbang.org/resource/image/f7/7d/f778bd8786c095fd6a2710ba0d43097d.jpg?wh=2040x2046)

另外一种创建方法是用Terrafrom代码来生成S3的存储桶。这里我的 [GitHub代码库](https://github.com/cloudnative-automation/github-terrafrom) 中提供了一个创建S3存储桶样例代码，你可以自行尝试运行创建。

这里需要注意的是，创建了存储桶以后，我们还无法直接用上它。这是因为AWS采用了ABAC方式来管理资源，也就是基础属性的访问控制。怎么理解呢？其实ABAC这一种授权机制，作用就是根据资源和用户属性来控制用户访问资源的权限。

一般来说，创建好资源以后，还需要为其附加上相应的策略，这样才完成了资源的配置。这些策略一般描述的是，谁可以对这个资源作出哪些操作。对应到我们课程里的例子，就需要给cloudnative-tfstate-1这个存储桶做授权。

我们在IAM中创建一个角色叫 `github-action-terraform`，这个角色是专门操作AWS资源的，具体配置，你可以参考后面的截图。

![](https://static001.geekbang.org/resource/image/61/56/618e671f59f735cf132d060895f6f356.jpg?wh=2000x1104)

在步骤1的信任实体中，填入上一步创建的oidc-provider的arn号，以及你的github repo地址。这里请注意你的环境与我环境有所不同，不要直接复制粘贴，需要根据你的情况调整。

```go
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::{UID}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:cloudnative-automation/github-action-terrafrom:*"
                }
            }
        }
    ]
}

```

我们有了操作AWS资源的角色，那么我要为这个角色划定权限，也就是赋予一个权限策略，在AWS IAM 策略中，我们新建一个访问S3存储桶的策略，然后填入图上的权限配置，我将权限配置贴在后面，请对照文稿自行查阅。

![](https://static001.geekbang.org/resource/image/a3/86/a34579c9491ba79a2607368bb442f186.jpg?wh=945x929)

策略的配置如下，也非常好理解，对于S3存储桶中的资源 `arn:aws:s3:::cloudnative-tfstate-1` 一般需要有List、Put等的权限，这里我在Action中加入了Put和List权限，具体请查看下面的代码。

```go
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::cloudnative-tfstate-1/*",
                "arn:aws:s3:::cloudnative-tfstate-1"
            ]
        }
    ]
}

```

最后我们将角色与策略绑定在一起，只要在角色-权限策略中，将你刚才新建的策略附加上就可以了。

![](https://static001.geekbang.org/resource/image/5b/0e/5b5f13b08c883d6cyy7fa32eab285b0e.jpg?wh=2020x1495)

除了自定义策略之外，你也可以复用AWS自带的策略，你可以在角色的权限中选择附加策略，这里我附加上AmazonEC2FullAccess的策略，在接下来的EC2创建中，我们会使用到这个策略。

![](https://static001.geekbang.org/resource/image/6f/b7/6f753dd5747f396931a74a98b45e1ab7.jpg?wh=2138x665)

#### 密钥怎么处理？

现在，我们建好了S3存储桶，那么Github Action是怎么把状态文件存进去的呢？我们这就来看看S3要怎么使用。

因为Terrafrom里已经支持了将状态文件直接存储进S3，所以我们只要在terrafrom init的时候配置backend storage的存储桶以及相应权限即可。命令如下：

```plain
terraform init -backend-config="bucket=${AWS_BUCKET_NAME}" -backend-config="key=${AWS_BUCKET_KEY_NAME}" -backend-config="region=${AWS_REGION}"

```

我们需要注意的是，这条命令里有一些变量，比如 **AWS\_BUCKET\_NAME，AWS\_REGION** 等。这些变量需要从GitHub上通过Secret注入到执行过程。

这一步的操作发生在GitHub上，过程也很简单。我们只需要点击代码仓库的setting，找到左下方的Secret and vaiables，在Actions中添加这几个Secret。

- AWS\_BUCKET\_NAME，存储桶名称，这里我们填入上一步中创建的存储桶的名称 cloudnative-tfstate-1
- AWS\_BUCKET\_KEY\_NAME，这里指的是你在存储桶中存储文件的名称，这里我们填入的是eks.tfstate，稍后你可以在存储桶中看到这个文件。
- AWS\_REGION ：存储桶所在的区域，这里我们填入的是ap-east-1。
- AWS\_ROLE ：存储桶角色的 ARN，这里可以从创建好的存储桶的属性中找到，这里我们填入 `arn:aws:s3:::cloudnative-tfstate-1`。

在Github的界面中，最终看起来像下图一样，就表示我们成功完成了配置。

![](https://static001.geekbang.org/resource/image/a8/yy/a8245885814094ecca16c6ea022bf8yy.jpg?wh=2000x1295)

## Github Action的配置怎么写？

好，现在最关键的一步来了，也就是GitHub Action的配置要怎么写？完成这一步，我们才能真正用GitHub Action来管理Terrafrom代码。

GitHub Action中有这么几个重要的字段，on、env还有job。on表示在哪一个Git分支上执行。

env是环境变量，例如我们需要引入上一步中Region的这个变量，就可以这样写：

```go
env:
  TF_LOG: INFO
  AWS_REGION: ${{ secrets.AWS_REGION }}

```

而在job这个字段里，就是我们定义真正执行操作步骤的地方。了解了重要字段，我们就可以动手写代码了。

首先，我们需要对环境做一些初始化，例如将代码checkout出来，配置Terraform的版本，环境等等，我将样例代码贴在了后面。

```go
    steps:
      - name: Git checkout
        uses: actions/checkout@v3

      - name: Configure AWS credentials from AWS account
        uses: aws-actions/configure-aws-credentials@v1
        with:
          role-to-assume: ${{ secrets.AWS_ROLE }}
          aws-region: ${{ secrets.AWS_REGION }}
          role-session-name: GitHub-OIDC-TERRAFORM

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.2.5

```

其次，GitHub Pull Request中有两个主要动作。第一是创建Pull Request，提交代码并审核；第二是在代码审核完成之后，合并代码。

相应地，我们在第一步创建Pull Request的时候，就需要运行terraform plan来检查这次提交的代码是否符合预期。然后在第二步合并代码的时候，通过GitHub Action运行terrafrom apply，真正执行基础设施上的变更。

GitHub Action的配置很长，为了让你聚焦重点，这里我将两步的核心代码贴在这里，帮助你理解核心用法。GitHub Action中定义Terraform plan这一步，它的触发条件是 github.event\_name == ‘pull\_request’。

```plain
- name: Terraform Plan
  id: plan
  run: terraform plan -no-color
  if: github.event_name == 'pull_request'
  continue-on-error: true

```

接着，我们来看GitHub Action中定义Terraform Apply这一步。它的触发条件是 github.ref == ‘refs/heads/main’ && github.event\_name == ‘push’，含义是当main branch有push的这个动作时候，就执行terraform apply这个命令。

```plain
- name: Terraform Apply
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: terraform apply -auto-approve -input=false

```

完整的GitHub Action的配置，请参考 [GitHub仓库里](https://github.com/cloudnative-automation/github-action-terrafrom/tree/main/.github/workflows) 的代码。

## 万事俱备，运行管理

这一切都设置完成之后，就到了收割战果的时刻，我们提交一个PR来运行一下。

![](https://static001.geekbang.org/resource/image/48/bf/489208ff6108f3def811d3516c8928bf.jpg?wh=2000x744)

从图里我们可以看到，当Pull Request提交的时候，自动触发了Github Actions的流水线，此时正在运行的是terrafrom init以及terrafrom plan的步骤。

![](https://static001.geekbang.org/resource/image/b5/01/b5a7d492b88775deac2yyaa31f3c3801.jpg?wh=2000x2107)

从这个图中，我们可以看到，当Pull Request被merge的时候，自动触发了Github Actions的流水线，此时正在运行的是terrafrom apply这一步。

![](https://static001.geekbang.org/resource/image/55/dd/5524aeec718ee20ee96385cae1b10edd.jpg?wh=2020x2042)

最后，我们在AWS的页面上可以看到EC2实例创建成功了。

![](https://static001.geekbang.org/resource/image/75/81/75a73cc2fcd6a1ca8c904d98305ccf81.jpg?wh=2020x1600)

同时在S3存储桶中，我们可以看到Terraform的状态文件的不同版本，达到了安全地存储我们的管理文件，又能让我们拥有版本追溯的要求。

![](https://static001.geekbang.org/resource/image/d1/29/d114a69406f44a02c7fa5f271aec4029.jpg?wh=2252x673)

这样，我们就初步完成了用Github Action来管理Terraform的整个过程。这时，我们真正地将IaC完整地实现了。

## 总结

我们来做个总结。

通过今天的学习，我们应该理解了 GitOps 模式是如何工作的，GitOps是一种使用 Git 仓库作为 IaC 代码的中央存储库的模式，并使用 DevOps中的CI/CD的形式来管理它。

理解原理只是第一步，今天的重点是配置实操，这个过程掌握了，你才能熟练地使用GitHub Actions 来管理 Terraform 代码。

我们来回顾一下其中的关键步骤。首先，我们在AWS上配置了Github OIDC，让GitHub Action可以通过OIDC认证将AWS权限安全地转移给GitHub Action。

然后，我们创建了S3存储桶用于保存terrafrom状态文件，并且在创建S3存储桶的过程中，我们学习了AWS IAM是如何配置的，同时我们在GitHub上，利用了Github Secret的这个功能，存储了S3存储桶的一些相关信息，通过变量的形式传递给Github Action流水线。

最后，我们仓库中 `.github/workflows` 目录下创建一个新的 YAML 文件，来完成一个 GitHub Actions 工作流的设置。在这个YAML文件中，我们可以定义我们的工作流，包括触发的事件（例如 push 或 pull request）、运行的环境和执行的步骤。

其实整个配置的过程并不简单，尤其是Github Action的配置文件的编写，需要不断修改与调试才能达到满意的效果，希望你能够跟着课程实际操作一遍，加深对整个过程的理解。

## 思考题

课程里，我们将Terraform状态文件存放在S3这步中，S3存储桶是我们手动在页面上创建出来的，你能否自己写一段Terraform代码，通过GitHub Action来创建出S3存储桶呢？

欢迎在评论区里给我留言。如果这一讲对你有启发，别忘了分享给身边更多朋友。