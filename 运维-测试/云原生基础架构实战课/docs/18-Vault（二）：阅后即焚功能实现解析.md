你好，我是潘野。

上一讲，我们一起初步了解了Vault的架构和核心概念，并且还结合案例，实际练习了如何在Kubernetes上使用Vault管理和获取密钥。

这一次，我们要聊点更酷的东西，一起学习Vault的另一个神奇功能——租赁与回收机制。可能你并没有听说过这个功能，所以我们先从一个你更熟悉的场景聊起。

## 阅后即焚功能

想象一下，你在使用微信时，有没有使用过那个超级酷的“阅后即焚”小程序？就是你发送一个秘密消息给朋友，他们一看完，那消息就像被魔法师施了魔法一样消失不见了！

## 在企业安全管理中的妙用

你可能会好奇，这个功能与企业安全管理有何关联呢？

让我们先来对比一下传统的密钥管理方式——手动创建、分发、销毁密钥。听起来就很繁琐对吧？而且这样很容易出错。

这时候，“阅后即焚”功能就能大显身手了。它能自动管理密钥的整个生命周期，简化操作流程，大幅降低出错率，使得密钥管理变得既简单又安全。

我来举个例子，想象一下你和几个同事在管理一个分布式系统，需要在多个数据中心的服务器之间共享密码。一般来说，大家都是在内部聊天软件中直接发送。但是，这种使用传统方法传递密码的方式，很容易在内部的审计系统和日志系统中留下痕迹。一旦密码泄露，整个系统的安全都可能受到威胁。

但如果使用了类似“阅后即焚”的功能情况就不一样了。你把密码分享给一起协作的同事，设定只有指定同事能看，且只让他看一次。因为经过加密和权限设置，同事接收到密码之后，密码就会自动消失；如果未按时查看，密码也会消失，避免泄露。整个传输过程是加密的，并且是点对点的传递，且密码销毁及时，可以极大降低遭受攻击的风险。

在这个过程中，有两个特别重要的点：

- **查看后自动销毁**：这确保了信息只被授权的人看到一次，之后就无迹可寻。
- **超时自动销毁**：如果没在规定时间内查看，信息也会自动消失，又增加了一重保护。

这两点在Vault里头，就对应着 **租赁与回收** 这两个实用的功能。通过这种方式，Vault不只是保护了密钥的安全，还能智能地管理密钥的生命周期，让一切变得既安全又便捷！

## 租赁与回收的例子

接下来我们结合例子，来看看这两个功能的具体实现。

假设你在一个云环境中管理应用，需要从 Vault 获取数据库的访问凭证。

1. 请求凭证：你的应用通过 API 向 Vault 请求访问特定数据库的凭证。
2. 接收凭证和租赁信息：Vault 处理这个请求，生成一个数据库用户名和密码，并创建一个租赁。假设租赁时长设置为24小时。
3. 使用凭证：应用使用这些凭证来访问数据库，进行数据读写操作。
4. 租赁过期：如果24小时后你没有请求续约，Vault 会自动让这些凭证失效，并从数据库中撤销这些凭证，确保它们不会被再次使用。

## 租赁的机制与方法

在这个流程中涉及几个关键步骤，包括请求密钥、管理租赁以及必要时续约或撤销租赁。我们来看看实际是怎么操作的。

### 1\. 请求密钥

首先，你需要从 Vault 请求一个密钥或凭证。这通常是通过执行一个 API 调用或使用 Vault 的 CLI 命令来完成的。例如，如果你想从 Vault 中获取一个数据库的凭证，就可以通过后面这条命令完成。这条命令会根据 my-role 的配置生成一个数据库用户名和密码。

```plain
vault read database/creds/my-role

```

### 2\. 接收租赁信息

执行上述命令后，Vault 不仅会返回所请求的凭证，还将返回与这些凭证相关的租赁信息。这包括：

- 租赁ID（Lease ID）：这是一个唯一标识符，用于追踪和管理租赁。
- 租赁时长（Lease Duration）：这表明了凭证的有效期限，通常以秒为单位。
- 续约策略：指示这个租赁是否可以续约以及如何续约。

例如，返回的信息可能看起来是这样的：

```plain
{
  "lease_id": "database/creds/my-role/1b4a7a00-f211-d3e9-3b8c-cea7b6f05a0c",
  "lease_duration": 3600,
  "renewable": true
}

```

### 3\. 租赁的续约

如果租赁是可续约的，并且你希望在租期到期之后，能够继续使用这些凭证，这时就需要请求续约租赁。

使用 Vault CLI，你可以执行如下命令来续约租赁。

```plain
vault lease renew [lease_id]

```

其中 \[lease\_id\] 是你在租赁信息中获得的 Lease ID。你也可以指定续约的时长，前提是这不超过最大租赁时长的限制。

### 4\. 租赁的撤销

如果你不再需要这些凭证，或者出于安全考虑需要立即使它们失效，就可以撤销租赁。使用 Vault CLI，执行如下命令将立即结束租赁，让相关的凭证失效。

```plain
vault lease revoke [lease_id]

```

## 自动回收的机制

一旦租赁到期，如果没有续约凭证，Vault 会自动执行回收操作，确保这些敏感信息不会被未授权访问或留存超出其必要的时间。

具体分成两个步骤。

1. 撤销密钥或凭证：相关的密钥或凭证将被自动从系统中删除，使其无法再被使用。
2. 记录日志：Vault 通常会记录相关的撤销操作，以便于审计和监控。

这个过程完全自动化，大大减少了出现人为错误的可能性。通过这种方式，即使凭证被泄露，它们也只在一个非常有限的时间窗口内有效，大大降低了安全风险。同时，自动化的租赁和回收机制也减轻了管理负担，使得操作更加高效和安全。

### 设置自动回收

自动回收通常是在设置 Vault密钥引擎（Secret Engine）时配置的，例如在配置数据库密钥时，你可以指定租赁的默认时长和最大时长。后面就是一个设置数据库密钥的示例，首先建立一个密钥，允许访问该数据库连接的Vault角色为“db-role”。

```plain
vault write database/config/my-database \
    plugin_name=postgresql-database-plugin \
    allowed_roles="db-role" \
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb?sslmode=disable" \
    username="vaultuser" \
    password="vaultpass"

```

接着，你可以为特定角色配置租赁的时长，通过执行这个命令，Vault将创建或更新一个名为 “db-role” 的数据库角色，该角色关联到之前配置的 “my-database” 数据库链接。当使用该角色请求动态数据库凭据时，Vault将执行指定的创建语句来创建一个新的数据库用户，并将生成的凭据返回给请求者。

请注意，你需要将 `creation_statements` 中 的 `"..."` 替换为实际的SQL语句，以根据你的数据库类型和所需的权限来创建用户。

```plain
vault write database/roles/db-role \
    db_name=my-database \
    creation_statements="..." \
    default_ttl="1h" \
    max_ttl="24h"

```

在这个例子中， `default_ttl="1h"` 指定了动态生成的数据库凭据的默认生存时间（TTL）为1小时。这意味着如果在请求动态凭据时没有显式指定TTL，则默认情况下凭据将在1小时后过期。

类似地， `max_ttl="24h"` 指定了动态生成的数据库凭据的最大生存时间（TTL）为24小时。这意味着请求动态凭据时指定的TTL不能超过24小时。一旦租赁期满，而且没有进行续约，Vault 将自动撤销该租赁。

### 监控自动回收

虽然自动回收是自动进行的，但为了确保回收正确可靠地运行，我们还需要监控这一过程，特别是在生产环境中。Vault 提供了日志功能，你可以通过查看日志来监控租赁的撤销情况。如果你配置了 Vault 的审计日志，撤销操作会被自动记录下来。

## 程序实现

前面我们学习了租赁与回收的机制和操作方法。回顾之前的例子，在实际工作中，我们其实不太可能直接使用vault命令来分享或获取密钥。一方面，操作过程中容易出错；另一方面，这种方式也不符合我们追求的自动化原则。

接下来，我们将通过一段Go语言代码，来说明如何用代码方式来使用Vault的租赁与回收功能。

首先，确保你已经安装了 Vault 的 Go 客户端库。如果还没有安装，可以通过下面的命令安装。

```yaml
go get github.com/hashicorp/vault/api

```

或者在go.mod中引用 `github.com/hashicorp/vault/api` 包，这是由Vault官方提供的Go客户端。

然后，你可以创建一个简单的 Go 程序来实现这些功能。这段代码非常短，我来简单地解释下这段代码都做了什么。

首先是初始化，里面有两步。第一步是设置Vault服务器地址，程序是从环境变量 `VAULT_ADDR` 和 `VAULT_TOKEN` 中读取 Vault 的地址和访问令牌。你可以使用其他方式将Vault地址导入程序中。第二步是使用 Vault 的地址在程序内创建一个新的 Vault 客户端。

接下来是读取密钥，从 Vault 中读取一个密码，在这个例子中是 `secret/data/my-secret`。接着在终端中打印出获取的密钥数据和租赁信息。

获取到租赁信息之后，你可以延长租赁时间，也可以撤销租赁并清理资源。比如后面这段代码，就表示我们是在程序退出前使用了 `Revoke` 函数撤销了租赁，而且清理了资源。

```plain
package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/hashicorp/vault/api"
)

func main() {
	// 设置 Vault 服务器的地址
	vaultAddr := os.Getenv("VAULT_ADDR") // 例如: "http://127.0.0.1:8200"
	if vaultAddr == "" {
		log.Fatal("VAULT_ADDR environment variable is not set")
	}

	// 创建 Vault 客户端
	config := &api.Config{
		Address: vaultAddr,
	}

	client, err := api.NewClient(config)
	if err != nil {
		log.Fatalf("failed to create Vault client: %s", err)
	}

	// 设置 Vault token
	vaultToken := os.Getenv("VAULT_TOKEN") // 从环境变量中获取
	if vaultToken == "" {
		log.Fatal("VAULT_TOKEN environment variable is not set")
	}
	client.SetToken(vaultToken)

	// 从 Vault 读取密钥
	secret, err := client.Logical().Read("secret/data/my-secret")
	if err != nil {
		log.Fatalf("failed to read secret: %s", err)
	}

	// 输出获取的密钥
	fmt.Printf("Secret data: %v\n", secret.Data["data"])

	// 获取租赁信息
	leaseID := secret.LeaseID
	leaseDuration := secret.LeaseDuration

	fmt.Printf("Lease ID: %s\n", leaseID)
	fmt.Printf("Lease Duration: %d seconds\n", leaseDuration)

	// 如果需要，可以在程序结束前撤销租赁
	defer func() {
		log.Println("Revoking lease...")
		if _, err := client.Sys().Revoke(leaseID); err != nil {
			log.Fatalf("failed to revoke lease: %s", err)
		}
		log.Println("Lease revoked")
	}()

	// 模拟使用秘密一段时间
	time.Sleep(10 * time.Second)
}

```

## 总结

今天，我们主要学习了使用Vault进行密钥管理的高级功能——租赁与回收机制。

通过类比微信的“阅后即焚”功能，我们详细了解了Vault的租赁与回收功能如何工作，包括请求密钥、接收租赁信息、租赁的续约和撤销。这些功能使得密钥在使用后可以被自动回收，减少了密钥泄露的风险，并且减轻了管理负担。

企业安全管理中，密钥的租赁与回收常用于这些场景：

- 分享临时密码或一次性密码，例如用于登录网站或账户。
- 发送包含敏感信息的私人消息，例如财务信息或个人信息。
- 共享机密文件，例如企业销售数据等等

我们还通过一段Go语言代码示例，学习了如何在实际编程中使用Vault的API来实现密钥的获取、使用和撤销。代码中包括如何设置和使用Vault客户端、如何从Vault获取秘密信息以及如何在不再需要时撤销秘密的租赁，你可以课后自己动手练习一下。

## 思考题

不同类型的敏感数据（如数据库凭证、API密钥等）对租赁时间的需求可能不同。想一想，我们应该如何优化租赁与回收策略呢？

欢迎在评论区与我讨论。如果这一讲对你有启发，也欢迎分享给身边更多朋友。