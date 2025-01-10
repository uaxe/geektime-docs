你好，我是潘野。

上一讲，我们学习了如何使用GitHub Action来管理Terraform代码，并且也实现了GitOps的整个过程。

虽然这种方式比较容易上手，但是GitHub Action存在一定的局限性。比如有些公司并没有选择GitHub作为代码管理平台，而是选择Gitlab作为公司的代码管理平台。或者是有些公司购买的是Github Enterprise版本，这时候有一些GitHub上的第三方插件就无法在内网环境里使用。针对这些场景，我们就需要找到一个适用度更好的CI/CD工具。

在持续集成领域，有很多持续集成、持续部署的工具，除了前一讲使用的Github Action，还有大名鼎鼎的Jenkins，来自Kubernetes社区的Prow等等，而今天我们将会选择使用Tekton来作为我们CI/CD的工具链。

## 为什么选择使用 Tekton？

和其他的CI/CD工具相比，Tekton有三个优势。

第一，Tekton的设计考虑到了多种使用场景，定制程度高且相对容易上手，能够适应各种复杂的需求。例如，它用Task这个资源来描述每个步骤细节，用Pipeline这个资源将各个步骤串联在一起。因此，相比Jenkins Pipeline中将步骤与流水线混合编写，Tekton配置代码的可读性和可维护性会更好。

第二，Tekton的可扩展性好。Tekton Catalog 是 Tekton 社区驱动的存储库，其中包含大量预制组件，可以直接使用这些组件，快速创建新的 CI/CD 流水线，或者扩展现有流水线；同时Tekton 本身也支持扩展，我们也可以开发自定义的 Task 和 Pipeline 来满足特定的需求。

第三，Tekton诞生自Knative项目，原生于Kubernetes平台，它与Kubernetes紧密结合，能够充分利用Kubernetes的动态扩展能力。

正是因为这三方面的优势，借助Tekton，你可以 **更容易地创建复杂的CI/CD工作流**，提高GitOps的定制能力，降低GitOps的维护压力。

## Tekton基本概念

不难发现，Tekton 是一个强大的 CI/CD 工具。我们接下来学习一下Tekton 的基本概念，最重要的四个概念分别是Task、TaskRun、Pipeline和PipelineRun。

### Task

Task中定义了完成特定任务所需的步骤和材料。它就好比烹饪食谱一样，包含多个步骤，每个步骤可以执行一个具体的命令或操作。例如一个 Task 可以包含以下步骤：

- 从代码仓库拉取代码
- 运行单元测试
- 构建镜像
- 推送镜像到镜像仓库

**TaskRun**

TaskRun 就是 Task 的实际执行，就像根据食谱烹饪一道菜一样，TaskRun 代表了一次具体的任务执行过程。每个 TaskRun 会创建一个 Pod，其中每个步骤对应 Pod 中的一个容器，TaskRun 会记录任务执行的状态，例如成功、失败或正在运行。

### Pipeline

Pipeline表示流水线模版，它就像一个工作流程图，定义了多个 Task 的执行顺序，最终合成一个完整的 CI/CD 流水线。例如，一个应用从构建到上线的 Pipeline 可以包含以下步骤：

- 构建代码
- 运行单元测试
- 构建镜像
- 推送镜像
- 部署应用程序

### PipelineRun

PipelineRun 是 Pipeline 的实际执行，就像我们根据工作流程图完成一项工作一样，PipelineRun 代表了一次具体的流水线执行过程。每个 PipelineRun 会生成一条流水线记录，其中包含所有任务的执行状态。

## 如何将GitOps与Tekton结合使用？

回想下我们执行terraform的三个步骤，分别是terraform init、terraform plan和terrafrom apply。

其实这些步骤，我们都可以通过定义Tekton的Task来完成。因为从init到plan，再到apply这三步存在先后顺序，这是一个流水线的形态。对应到Tekton中的就是Pipeline，所以这个Pipeline的全貌应该分成4个Task。

1. 第一个Task是克隆你的Terraform代码的Git仓库。
2. 接下来，第二个Task是运行 `terraform init` 来初始化你的Terraform工作区。请注意，这时候不要忘记将Terraform的状态文件存进远端存储中。
3. 第三个Task是运行 `terraform plan` 来创建一个执行计划。
4. 最后一个Task是运行 `terraform apply` 来应用你的执行计划。

## Trigger类型及原理

我们定义好Task和Pipeline之后，需要触发Task或者Pipeline的时候，必须手动创建一个 TaskRun 或者 PipelineRun，这样显然不符合GitOps自动化的要求。

这时候，我们就需要用到Tekton Trigger 组件，它是专门用来解决 CI/CD 流水线触发问题的。它可以监听各种来源的事件，并根据事件信息自动触发 Task 或 Pipeline 的执行，从而自动化我们的 CI/CD 工作流。Tekton 支持多种类型的Trigger，具体包括这几类。

- Git Trigger：监听 Git 仓库的更改。
- Event Trigger：监听 Kubernetes 事件。
- Time Trigger：定期触发。

你可以从 [官方的代码仓库](https://github.com/tektoncd/triggers/tree/v0.20.0/examples/v1beta1) 看到Tekton支持的各类Trigger的使用样例 。接下来，我们看看Trigger是如何工作的，流程图我贴在了后面。

![](https://static001.geekbang.org/resource/image/c7/29/c7655372bc8008e5766075a2c5fb4a29.jpg?wh=1011x261)

Tekton EventListener 用来监听外部事件，当事件进入到EventListener内部，TriggerBinding 就会从事件内容中提取对应参数，然后将参数传递给TriggerTemplate。TriggerTemplate 则会根据预先定义的模版以及收到的参数，创建 TaskRun 或者 PipelineRun 对象。

## 配置环节

明确了思路以后，我们动手尝试一下，用Tekton创建一个能执行Terraform操作的流水线。

首先，你需要在你的Kubernetes集群中安装和设置Tekton。这里我们需要安装Tekton的Pipeline和Triggers组件。

因为安装部署只需要apply tekton配置文件即可，所以这里我贴出安装Tekton的命令。至于更细节的内容，你可以参考官方文档中 [Installation的这个章节](https://tekton.dev/docs/installation/pipelines/)。

Tekton Pipeline和Trigger的安装命令如下：

```plain
kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

kubectl apply --filename \
https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml

kubectl apply --filename \
https://storage.googleapis.com/tekton-releases/triggers/latest/interceptors.yaml

```

同时，我们也把Tekton Dashboard安装上，方便我们使用过程中排查流水线的运行状态和问题。安装的命令如下：

```plain
kubectl apply --filename https://storage.googleapis.com/tekton-releases/dashboard/latest/release.yaml

```

### Github Webhook的配置

Webhook的配置分为两个部分，第一部分是Trigger的配置，第二部分是Github状态的配置。

我们先讲Trigger部分的配置，这部分安装配置比较简单，我将所需要的文件和配置的方法放在了 [代码仓库](https://github.com/cloudnative-automation/tekton-terraform/tree/main/tigger/github) 里供你参考。下面，我简单描述下几个文件的作用。

首先来看 [github-eventlistener-interceptor.yaml](https://github.com/cloudnative-automation/tekton-terraform/blob/main/tigger/github/github-eventlistener-interceptor.yaml) 这个文件。

当我们提交源代码到 GitHub 的时候，需要触发 Tekton 的任务运行。所以首先需要完成这个触发器。这里就可以通过 EventListener 这个资源对象来完成。

注意，对于resources中的ServiceType，你需要根据实际情况选择。如果你在云上，选择LoadBalancer；如果你是在自建机房内，没有负载均衡器条件的，就可以选择NodePort。

```yaml
    resources:
      kubernetesResource:
        serviceType: LoadBalancer

```

这样就生成了EventListener的访问地址。当Service生成之后，我们还要将tk.github.51.cafe的DNS解析到Service的IP上，方便接下来的配置。

```yaml
> kubectl get svc -n terraform-tekton el-github-listener
NAME                 TYPE           CLUSTER-IP     EXTERNAL-IP    PORT(S)                         AGE
el-github-listener   LoadBalancer   10.0.138.249   4.189.196.54   8080:31669/TCP,9000:32216/TCP   2d13h

```

然后我们来配置Github Webhook，配置如下图所示，这里选择什么情况下触发Webhook，如果你不熟悉Github Event，这里可以选择 “Send me everything”。如果你对Github Event比较了解，可以选择 “individual event”，根据你的需求来灵活定制 。

![](https://static001.geekbang.org/resource/image/d8/d2/d8eea34139902b5a6yy1d9b8d4a0ced2.jpg?wh=1125x924)

一切配置好了之后，回到Webhook页面，此时你应该看到一个绿勾，这代表你的Webhook是可以正常工作了。

![](https://static001.geekbang.org/resource/image/92/42/928dbc554d1434c3e17d531640b3b442.jpg?wh=1514x624)

配置好Webhook之后，我们再来讲讲GitHub状态的配置。配置GitHub PR状态的目的是方便你快速定位到这个PR所对应的Tekton流水线，因为Tekton官方已经提供了插件，我们只要根据 [插件文档](https://hub.tekton.dev/tekton/task/github-set-status) 安装和 [配置](https://github.com/cloudnative-automation/tekton-terraform/blob/main/src/task/github-set-status.yaml) 即可。

下图展示了Pull Request的CI状态。

![](https://static001.geekbang.org/resource/image/4d/54/4d13e16973cfffb831752bc5c5b52754.jpg?wh=1232x919)

### Task定义

接下来，我们开始定义我们的Task。

Tekton官方提供了很多关于Git和Terraform操作的Task，我们可以直接拿来使用。具体你可以从 [官网的插件仓库](https://hub.tekton.dev/?category=Git) 中获取到你想要的Task插件。

这里我们需要用到这两个Task插件。 [git-clone插件](https://hub.tekton.dev/tekton/task/git-clone) 能够帮助我们把代码克隆到Tekton的容器中。 [terraform-cli](https://artifacthub.io/packages/tekton-task/tekton-tasks/terraform-cli) 则是我们运行Terraform命令的基础。

同样，具体安装方法你可以参考插件的官方文档。

#### Git

首先是定义Git方面的操作，这里我们重点关注核心的配置部分。完整的配置文件请参考 [GitHub仓库中的配置](https://github.com/cloudnative-automation/tekton)。

首先，我们要在steps中定义git clone操作。

```plain
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: git-clone
spec:
    workspaces:
    (省略..）
    params:
      - name: url
        type: string
      - name: gitInitImage
        type: string
    (...)
    steps:
    - name: clone
      image: "$(params.gitInitImage)"
      env:
      - name: HOME
        value: "$(params.userHome)"
      - name: PARAM_URL
        value: $(params.url)

```

可以看到，我们把git clone中需要的一些参数定义在了 `params` 中，例如Git仓库的URL，clone时用的Token等。

#### init

当我们执行 `terrafrom init` 这个动作的时候，其实主要目的是将相对应的模块下载下来，并且定义状态文件所需要的一些权限。这里我建议你在Task中用script字段配合params来实现初始化。

这里肯定有同学会问了，AWS\_SECRET\_ACCESS\_KEY和AWS\_ACCESS\_KEY\_ID是从哪里读取到的？

这里是我们预先将AWS\_SECRET\_ACCESS\_KEY和AWS\_ACCESS\_KEY\_ID以Secret的形式存在了Tekton的namespace中，然后以环境变量的形式导入Tekton。

```plain
- name: init
  image: $(params.image)
  workingDir: $(workspaces.source.path)
  env:
  - name: AWS_SECRET_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: aws-iam-key
        key: $(params.iam-key)
  - name: AWS_ACCESS_KEY_ID
    valueFrom:
      secretKeyRef:
        name: aws-iam-key
        key: $(params.iam-id)
  script: |
        #!/usr/bin/env sh
        set -eu
        terraform init

```

#### plan

接下来是terrafrom plan这步。我们将Terrafrom的执行步骤放在terraform-cli的script字段中，script字段中，你可以嵌入任何你熟悉的脚本语言来运行Terraform命令。

```plain
- name: terraform-cli
  image: $(params.image)
  workingDir: $(workspaces.source.path)/$(params.reponame)
  script: |
    #!/usr/bin/env sh
    set -eu
    TERRAFORM_VERSION=`grep -A1 "terraform_version" variables.tf |grep "default" |awk -F '"' '{print $2}'`
    if [ ! -z "$TERRAFORM_VERSION" ] ; then
      export TFENV_TERRAFORM_VERSION=$TERRAFORM_VERSION
    fi
    # terraform --version
    tfenv list
    terraform plan -input=false -no-color -out=tfplan
    terraform show tfplan -no-color 2>&1 | tee tfplan.txt

```

#### terrafrom apply

之后是创建执行计划。在script中，我们定义了执行 `terrafrom apply --auto-approval` 这条命令，同时将输出结果写入一个文本文件中，这样的作用是通过其他的插件将apply的输出内容回传到Github上。

```plain
- name: terraform-cli
  image: $(params.image)
  workingDir: $(workspaces.source.path)/$(params.reponame)
  script: |
    #!/usr/bin/env sh
    terraform apply -input=false -auto-approve -no-color 2>&1 | tee tfapply.txt

```

### Pipeline配置

定义完Task之后，我们需要将这些Task串联成一个Pipeline。同样为了让你抓住重点，我将配置文件的核心部分提炼出来。完整的配置文件请参考 [GitHub仓库中的配置](https://github.com/cloudnative-automation/tekton-terraform)。

```plain
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: terraform-pr
spec:
  tasks:
  - name: fetch-from-git
    taskRef:
      name: git-clone
  - name: terraform-plan
      runAfter: [fetch-from-git]
  - name: git-commit-terraform-results
      runAfter: [terraform-plan]
  - name: terraform-apply
      runAfter: [git-commit-terraform-results]
  finally:
  - name: report-pipeline-status-to-github
    taskRef:
      name: github-set-status

```

对照代码我们看看串联思路是怎样的。在Tasks中，我们将之前定义的每个小Task放在里面，同时用runAfter这个关键词来定义Task的执行顺序。然后用finally这个关键词定义了一个收尾的Task，将之前运行的所有结果送回到GitHub的页面上。

这样我们就完成了一个基于Tekton的GitOps流水线！

## Github Action与Tekton的比较

我们完成了两种不同的CI/CD工具的GitOps，这里我们做一个比较。

相比Tekton来说，GitHub Actions使用起来更加简单直接。我们只需要定义好workflow的配置，并将AWS的相关密钥存储在Github仓库的Secrets and variable中，就基本完成了配置。对于GitHub项目，使用GitHub Actions进行CI/CD流程可以说是无缝集成，设置和使用都非常便捷。

但是Github与云服务的集成可能不够完美，比如runner需要一个单独的机器来运行，也需要更多的配置工作，这使得runner弹性扩展能力稍显不足；再比如它目前还缺少一些高级功能，如审计追踪等；另外，因为GitHub Action是Github的服务，所以在GitHub以外的代码托管平台上无法使用。

至于Tekton呢，我们可以将一个任务拆解成小任务，通过Pipeline将这些小任务串联起来，定制化程度很高，并且与各个云提供商的集成也比较容易。其次，Tekton是云原生的CI/CD工具，所以与Kubernetes配合度好，在高度定制化的基础上又具有弹性扩展的能力。

然而，Tekton也存在一些不足。例如，虽然它的上手难度不大，但是配置文件比较冗长，新手可能会望而生怯。此外，尽管其高度定制化的特性为复杂的工作流提供了可能，但这同时也意味着我们需要花费更多的时间和精力来配置和管理。这与一些更加“开箱即用”的CI/CD工具形成了对比。

我将GitHub Action与Tekton的对比做成了一个表格，供你参考。

![](https://static001.geekbang.org/resource/image/f6/4e/f6c47ed94ebf1bb6425e09e824760b4e.jpg?wh=3859x1649)

总的来说，选择哪种工具取决于具体的项目需求和团队的偏好。你可以考虑综合前面的对比项，选出更适合自己团队的工具。

## 总结

今天，我们通过分解运行Terrafrom代码的三大步骤init、plan、apply，一起学习了如何使用Tekton。我们在掌握了一种新的CI/CD工具同时，也学会了如何使用Tekton来管理我们的Terraform代码，实现了基于另外一种工具的GitOps。

Tekton流水线配置中还有大量的配置细节与注释，完整配置超过1000行，因此课程里着重和你分享了配置重点。完整配置我放在了代码仓库中，请你课后一定要仔细研读代码与注释，这样才能完整地理解基于Tekton的GitOps的实现方式。

最后，我带你比较了Github Action与Tekton，分析了两者的优势和不足。虽然我只是对比了两款CI/CD工具，但你不必局限于此，完全可以参考我的分析对比思路，想想有什么其他方式也能自动化地实现Terraform的执行过程（毕竟工具可能更新换代，但都是为了自动完成Terraform的执行过程）。

至此我们已经打下了基于GitOps的IaC的基础。但是我们GitOps之旅还未走完，离最后真正的交付还有最后的一公里，下一讲我将带你继续探索，敬请期待。

## 思考题

在terraform init的这个环节中，我们加载模块代码往往需要花费5到10分钟。你有哪些手法可以加速加载模块代码么？

欢迎在评论区与我讨论。如果这一讲对你有启发，也欢迎分享给身边更多朋友。