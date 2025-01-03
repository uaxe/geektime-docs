你好，我是俊达。

通过前面几讲，我们知道了怎么使用MySQL的数据复制技术，来实现数据库层面的高可用。但是对于应用系统，当后端的MySQL发生高可用切换时，应该怎么处理？

这里有几种可选的方案。

1. 应用通过域名访问数据库。域名指向主库，当后端数据库发生主备切换后，将域名指向新的主库。使用域名存在几个问题，包括域名缓存的问题，以及端口的问题。因为域名只能解析到IP，如果主库和备库的端口不一样，就无法直接通过切换域名来解决。

2. 在客户端解决。将MySQL集群中的实例信息都配置到应用程序中，在应用程序中自动检测主库和备库信息。也可以引入一些客户端的SDK来实现高可用。使用客户端的方案，会给应用开发带来额外的编码工作，或者对程序的开发语言有要求。

3. 引入Proxy，应用程序只访问Proxy。Proxy内部自动识别主库，将应用的请求转发给正确的后端数据库。这里Proxy的作用，和在web高可用架构中的负载均衡器作用类似。使用Proxy的好处，一是对客户端的限制少，你可以使用熟悉的方式访问数据库。而且有的Proxy可以通过一些策略，实现读写分离、SQL黑名单和白名单、SQL改写等功能。


业界MySQL Proxy的产品比较多。这一讲中，我们就以开源的ProxySQL为例，来看一下数据库高可用的一种实现方式。

ProxySQL支持MySQL传统的主备复制架构，也支持MGR架构。

客户端使用标准的MySQL协议访问ProxySQL，在客户端眼里，ProxySQL和MySQL没有大的区别。ProxySQL根据访问的用户、执行的SQL语句，将请求转发给后端MySQL，SQL执行完成后，再由ProxySQL将结果返回到客户端。

![图片](https://static001.geekbang.org/resource/image/5e/40/5ef6c62e2cd7cce08c5c18bc5bb17b40.jpg?wh=1130x907)

## ProxySQL安装部署

先安装一个ProxySQL。

1. 从github下载安装包

根据OS版本，选择对应的安装包。这里我们以CentOS 7为例，选择了当前最新的版本。

```plain
wget https://github.com/sysown/proxysql/releases/download/v2.7.1/proxysql-2.7.1-1-centos7.x86_64.rpm

```

下载后验证一下文件校验码是否正确。

```plain
# sha256sum proxysql-2.7.1-1-centos7.x86_64.rpm
336b913c1b2bde5bdac49b1b6290a6ce636405e5e19090a1de6030e47b92b8fa  proxysql-2.7.1-1-centos7.x86_64.rpm

```

2. 安装ProxySQL

我们下载的是rpm安装包，使用rpm命令进行安装。先安装依赖包。

```plain
yum install perl-DBI
yum install perl-DBD-mysql

```

再安装ProxySQL。

```plain
[root@172-16-121-234 opt]# rpm -ivh proxysql-2.7.1-1-centos7.x86_64.rpm
警告：proxysql-2.7.1-1-centos7.x86_64.rpm: 头V4 RSA/SHA512 Signature, 密钥 ID 8217c97e: NOKEY
准备中...                          ################################# [100%]
正在升级/安装...
   1:proxysql-2.7.1-1                 ################################# [100%]

```

安装完成后，使用系统脚本启动ProxySQL。

```plain
# systemctl start proxysql

# systemctl status proxysql
● proxysql.service - High Performance Advanced Proxy for MySQL
   Loaded: loaded (/etc/systemd/system/proxysql.service; enabled; vendor preset: disabled)
   Active: active (running) since 四 2024-11-14 14:15:19 CST; 38s ago
  Process: 10042 ExecStart=/usr/bin/proxysql --idle-threads -c /etc/proxysql.cnf $PROXYSQL_OPTS (code=exited, status=0/SUCCESS)
 Main PID: 10044 (proxysql)
   CGroup: /system.slice/proxysql.service
           ├─10044 /usr/bin/proxysql --idle-threads -c /etc/proxysql.cnf
           └─10045 /usr/bin/proxysql --idle-threads -c /etc/proxysql.cnf

```

### 配置ProxySQL

有几个地方可以配置ProxySQL。

3. 配置文件。

默认的配置文件是/etc/proxysql.cnf，也可以通过命令行参数-c指定配置文件。

```plain
## /etc/proxysql.cnf
datadir="/var/lib/proxysql"
errorlog="/var/lib/proxysql/proxysql.log"

admin_variables=
{
	admin_credentials="admin:admin"
	mysql_ifaces="0.0.0.0:6032"
}

mysql_variables=
{
	threads=4
	interfaces="0.0.0.0:6033"
  ...
}

...

```

datadir指定了proxysql内置数据库的存放路径。需要注意的是，proxysql.cnf中的配置只在初次启动proxysql时生效。如果proxysql的内置数据库已经创建，后续只会从内置的数据库中读取配置信息，这时再修改proxysql.cnf就不起作用了。

4. 配置数据库

你可以用mysql客户端登录proxysql的admin端口，使用标准的SQL语句来配置参数。admin端口由参数admin\_variables mysql\_ifaces指定，admin账号密码由参数admin\_credentials指定。admin账号只能在本地登录。登录后可以查看和修改配置项。

```plain
# mysql -uadmin -padmin -P6032 -h127.0.0.1
Server version: 5.5.30 (ProxySQL Admin Module)

mysql>

mysql> show databases;
+-----+---------------+-------------------------------------+
| seq | name          | file                                |
+-----+---------------+-------------------------------------+
| 0   | main          |                                     |
| 2   | disk          | /var/lib/proxysql/proxysql.db       |
| 3   | stats         |                                     |
| 4   | monitor       |                                     |
| 5   | stats_history | /var/lib/proxysql/proxysql_stats.db

```

使用show databases命令，可以看到ProxySQL的几个配置数据库。

- main：内存数据库。这个库里的表分两类，runtime开头的表存的是当前实际生效的配置。其它表存的是配置值，可通过load命令加载到runtime中，通过save命令持久化到磁盘中。

- disk：sqllite数据库。proxysql启动时从这个数据库加载配置项。


常用的一些配置表，我整理到了这个表格中，后续我会通过一些具体的例子来介绍这些表的使用方法。

![图片](https://static001.geekbang.org/resource/image/0a/7e/0a1cfb18ffcf961f127fec498c31187e.png?wh=1506x1334)

使用ProxySQL，一般要完成下面这几项内容的配置。

1. 配置监控账号，监控账号用来检测后端MySQL实例是否健康，比如是否能连接上、复制是否正常、复制是否有延迟等。

2. 配置后端mysql实例连接信息，实例连接信息存储在mysql\_servers表。

3. 配置连接proxysql和后端实例的账号，账号信息存储在mysql\_users表。

4. 配置查询路由信息，路由信息存储在mysql\_query\_rules表。

5. 配置后端mysql集群信息，根据后端mysql集群架构，配置分别存储在mysql\_replication\_hostgroups、mysql\_group\_replication\_hostgroups、runtime\_mysql\_galera\_hostgroups、runtime\_mysql\_aws\_aurora\_hostgroups等表中。

6. 根据具体需要，调优相关参数，参数存储在global\_variables表。


### 配置监控账号

ProxySQL使用监控账号来探测后端MySQL实例的健康度。监控账号要有一些基本的权限，包括：连接数据库、查看复制状态（replication client）、查看group replication相关表（performance\_schema）。

使用下面这些命令创建监控账号。

```plain
create user 'dbmonitor'@'%' identified with mysql_native_password
 by 'monitorpasswd';

grant replication client on *.* to 'dbmonitor'@'%';

-- group replication
grant select on performance_schema.replication_group_member_stats
 to 'dbmonitor'@'%';

grant select on performance_schema.replication_group_members
 to 'dbmonitor'@'%';

```

然后在ProxySQL中配置监控账号。

```plain
set mysql-monitor_username = 'dbmonitor';
set mysql-monitor_password = 'monitorpasswd';
load mysql variables to runtime;
save mysql variables to disk;

```

## ProxySQL使用场景

接下来我们通过一些使用场景，来看看怎么配置ProxySQL。例子中，会用到两个MySQL集群，一个是普通的主备复制集群，一个是MGR集群。

![图片](https://static001.geekbang.org/resource/image/6b/c0/6ba48f8bf9da5966096807da4b7dccc0.png?wh=1920x1057)

### 场景1：使用Proxysql实现读写分离

我们把下面这个MySQL数据复制集群配置到ProxySQL中。

![图片](https://static001.geekbang.org/resource/image/f2/30/f2777afdaa47f3f339199f6009abc730.jpg?wh=1244x664)

#### 配置hostgroup

先把数据库节点的信息写到mysql\_servers表。

```plain
insert into mysql_servers (
  hostgroup_id, hostname, port, max_replication_lag)
values ( 200, '172.16.121.234', 3308, 3);

insert into mysql_servers (
  hostgroup_id, hostname, port, max_replication_lag)
values ( 201, '172.16.121.236', 3308, 3);

insert into mysql_servers (
  hostgroup_id, hostname, port, max_replication_lag)
values ( 201, '172.16.121.237', 3308, 3);

load mysql servers  to runtime;
save mysql servers  to disk;

```

这里我们把两个备库都加到了hostgroup 201中。

#### 配置用户信息

然后到ProxySQL中配置用户信息。

```plain
insert into mysql_users
(username, password, default_hostgroup, transaction_persistent, backend, frontend, comment)
values ('user1', 'somepass', 200, 1, 1, 1, 'user1');

load mysql users  to runtime;
save mysql users  TO disk;

```

这里我们将用户的请求默认转发到hostgroup 200，也就是主库。transaction\_persistent设置为1，这是为了将一个事务中的所有SQL都发送到同一个后端MySQL。

当然，还要到后端的MySQL上创建用户和授权。

```plain
create user 'user1'@'%' identified by 'somepass';
grant create,alter,insert,update,delete,select on *.* to 'user1'@'%';

```

关于用户认证插件，在ProxySQL2.6.0版本前，如果后端账号使用了caching\_sha2\_password插件认证，配置用户时需要做一些特殊处理。

先把admin-hash\_passwords设置为false。

```plain
 set admin-hash_passwords=1;

 LOAD ADMIN VARIABLES to runtime;
 save ADMIN VARIABLES to disk;

 -- 确认配置生效
 mysql> select * from runtime_global_variables where variable_name = 'admin-hash_passwords';
+----------------------+----------------+
| variable_name        | variable_value |
+----------------------+----------------+
| admin-hash_passwords | false           |
+----------------------+----------------+

```

然后再配置用户表，以明文的形式存储password字段。

```plain
load mysql users to runtime;
save mysql users to disk;

-- 确认runtime_mysql_users表中的密码是明文
mysql> select username, password
  from runtime_mysql_users
  where username = 'user1';
+----------+---------------+
| username | password      |
+----------+---------------+
| user1    | user1-backend |

```

#### 配置读写分离规则

按前面这样配置，读写请求都会路由到主库。如果你想将一些查询转发到备库上执行，可以到mysql\_query\_rules表中添加一些转发规则。

```plain
insert into mysql_query_rules
(rule_id, username, match_pattern, destination_hostgroup,active, apply, comment )
values (101, 'user1', '^SELECT.*FOR UPDATE$', 200,1,1, 'route to hostgroup 200');

insert into mysql_query_rules
(rule_id, username, match_pattern, destination_hostgroup, active, apply, comment)
values (102, 'user1', '^SELECT', 201,1,1, 'select query route to hostgroup 201');

load mysql query rules to runtime;
save mysql query rules to disk;

```

上面这个例子中，除了select for update，其他所有SELECT开头的查询都转发到备库。

```plain
mysql> select @@hostname,@@server_id  for update;
+----------------+-------------+
| @@hostname     | @@server_id |
+----------------+-------------+
| 172-16-121-234 |     3308234 |
+----------------+-------------+
1 row in set (0.00 sec)

mysql> select @@hostname,@@server_id ;
+----------------+-------------+
| @@hostname     | @@server_id |
+----------------+-------------+
| 172-16-121-237 |     3308237 |
+----------------+-------------+
1 row in set (0.00 sec)

mysql> /*+ comment */ select  @@hostname,@@server_id ;
+----------------+-------------+
| @@hostname     | @@server_id |
+----------------+-------------+
| 172-16-121-234 |     3308234 |
+----------------+-------------+

```

上面这个配置，只是一个演示的例子，正式环境中，并不建议像这样将所有SELECT都无条件转发到备库。我建议你根据业务的需求，配置更精确的转发规则。而且在正式环境中添加转发规则前，要做好充分的测试。

### 场景2：后端MySQL自动切换

上一个场景中，所有的写入都转发到hostgroup 200。如果后端的数据库发生了主备切换，怎么将写请求转发到新的主库呢？

我们可以到mysql\_replication\_hostgroups表里添加一条配置记录，告诉ProxySQL，hostgroup 200和201是一个数据复制集群。

```plain
insert into mysql_replication_hostgroups
(writer_hostgroup, reader_hostgroup, check_type, comment)
values(200, 201, 'read_only', 'mysql mm cluster');

load mysql servers to runtime;
save mysql servers to disk;

```

这样配置后，ProxySQL会检测主备库的read\_only状态。检测到read\_only从OFF变成ON时，会将writer\_hostgroup中的主机添加到reader\_hostgrup中；当检测到read\_only从ON变成OFF时，会将主机从reader\_hostgroup中移到writer\_hostgroup中。

这里check\_type可以设置为read\_only、innodb\_read\_only、super\_read\_only、read\_only\|innodb\_read\_only、read\_only&innodb\_read\_only这几种类型，区别就是检测的条件不一样。

我们来做一个测试。当前172.16.121.234是主库。

```plain
mysql> select hostgroup_id, hostname, port, status from runtime_mysql_servers;
+--------------+----------------+------+--------+
| hostgroup_id | hostname       | port | status |
+--------------+----------------+------+--------+
| 200          | 172.16.121.234 | 3308 | ONLINE |
| 201          | 172.16.121.236 | 3308 | ONLINE |
| 201          | 172.16.121.237 | 3308 | ONLINE |
+--------------+----------------+------+--------+

```

我们把172.16.121.236切换为主库，先将172.16.121.234的Read\_only设置为ON。这时可以看到hostgroup 200中的主机被下线了。

```plain
mysql> select hostgroup_id, hostname, port, status from runtime_mysql_servers;
+--------------+----------------+------+--------------+
| hostgroup_id | hostname       | port | status       |
+--------------+----------------+------+--------------+
| 200          | 172.16.121.234 | 3308 | OFFLINE_HARD |
| 201          | 172.16.121.234 | 3308 | ONLINE       |
| 201          | 172.16.121.236 | 3308 | ONLINE       |
| 201          | 172.16.121.237 | 3308 | ONLINE       |
+--------------+----------------+------+--------------+

```

然后再把172.16.121.236的read\_only设置为OFF。可以看到，172.16.121.236加到了hostgroup 200中。

```plain
mysql> select hostgroup_id, hostname, port, status from runtime_mysql_servers;
+--------------+----------------+------+--------------+
| hostgroup_id | hostname       | port | status       |
+--------------+----------------+------+--------------+
| 200          | 172.16.121.234 | 3308 | OFFLINE_HARD |
| 200          | 172.16.121.236 | 3308 | ONLINE       |
| 201          | 172.16.121.234 | 3308 | ONLINE       |
| 201          | 172.16.121.236 | 3308 | ONLINE       |
| 201          | 172.16.121.237 | 3308 | ONLINE       |
+--------------+----------------+------+--------------+

```

上面的例子中，172.16.121.236加到hostgroup 200后，同时还在hostgroup 201中。

如果需要将这个实例从read hostgroup中移除，要将参数mysql-monitor\_writer\_is\_also\_reader 设置为false。

```plain
set mysql-monitor_writer_is_also_reader='false';
load mysql variables to runtime;
save mysql variables to disk;

```

然后再重新加载mysql server，就可以把设置了read\_only=OFF状态的后端实例从read hostgroup中移除。

```plain
mysql> load mysql servers to runtime;

mysql> select hostgroup_id, hostname, port, status from runtime_mysql_servers;
+--------------+----------------+------+--------------+
| hostgroup_id | hostname       | port | status       |
+--------------+----------------+------+--------------+
| 200          | 172.16.121.234 | 3308 | OFFLINE_HARD |
| 200          | 172.16.121.236 | 3308 | ONLINE       |
| 201          | 172.16.121.234 | 3308 | ONLINE       |
| 201          | 172.16.121.237 | 3308 | ONLINE       |
+--------------+----------------+------+--------------+

```

ProxySQL只根据后端MySQL的read\_only状态来判断，是将实例放到write hostgroup还是read hostgroup。所以需要正确地设置read\_only状态。如果主备实例都设置了read\_only=OFF，会发生双写，容易引起数据不一致。如果在备库复制有延迟或备库复制中断的情况下，将备库的read only设置为OFF，同样也可能会引起数据不一致。

这通常要使用一些MySQL自动切换的工具，比如MHA，来进行判断、设置。

### 场景3：ProxySQL和MGR配合使用

MGR自带故障检测和自动切换能力，接下来我们看一下MGR的一个例子。

#### 配置集群节点

```plain
insert into mysql_servers (
  hostgroup_id, hostname, port, max_replication_lag)
values ( 500, '172.16.121.234', 3307, 3);

insert into mysql_servers (
  hostgroup_id, hostname, port, max_replication_lag)
values ( 501, '172.16.121.236', 3307, 3);

insert into mysql_servers (
  hostgroup_id, hostname, port, max_replication_lag)
values ( 501, '172.16.121.237', 3307, 3);

load mysql servers  to runtime;
save mysql servers  to disk;

```

#### 配置集群信息

到mysql\_group\_replication\_hostgroups表中添加一条记录，告诉ProxySQL，hostgroup 500，501组成了一个MGR集群。

```plain
insert into mysql_group_replication_hostgroups
(writer_hostgroup, backup_writer_hostgroup, reader_hostgroup,
offline_hostgroup, active, max_writers, writer_is_also_reader,
max_transactions_behind, comment)
values(500, 502, 501, 503, 1, 1, 0, 0, 'mysql mgr cluster 1');

load mysql servers to runtime;
save mysql servers to disk;

```

#### 创建和配置用户信息

在ProxySQL中配置用户信息。

```plain
insert into mysql_users
(username, password, transaction_persistent, backend, frontend, default_hostgroup, comment)
values ('mgr', 'mgr123', 1, 1, 1, 500, 'backend user for mgr cluster');

load mysql users  to runtime;
save mysql users to disk;

```

然后到后端MySQL创建用户。

```plain
create user 'mgr'@'%' identified by 'mgr123';
grant select,insert,update,delete,create,alter on *.* to 'mgr'@'%';

```

都配置好之后，查看集群的配置信息。

```plain
mysql> select hostgroup_id, hostname, port, status
  from runtime_mysql_servers
  where hostgroup_id >= 500;
+--------------+----------------+------+--------------+
| hostgroup_id | hostname       | port | status       |
+--------------+----------------+------+--------------+
| 500          | 172.16.121.234 | 3307 | ONLINE       |
| 501          | 172-16-121-236 | 3307 | ONLINE       |
| 501          | 172-16-121-237 | 3307 | ONLINE       |
| 501          | 172.16.121.236 | 3307 | ONLINE       |
| 501          | 172.16.121.237 | 3307 | ONLINE       |
+--------------+----------------+------+--------------+

```

我们把172.16.121.234强制下线，可以看到集群选举了新的主节点。

```plain
mysql> select  member_host, member_port, member_state, member_role from replication_group_members;
+----------------+-------------+--------------+-------------+
| member_host    | member_port | member_state | member_role |
+----------------+-------------+--------------+-------------+
| 172-16-121-237 |        3307 | ONLINE       | PRIMARY     |
| 172-16-121-236 |        3307 | ONLINE       | SECONDARY   |
+----------------+-------------+--------------+-------------+

```

ProxySQL中的hostgroup也自动更新了。

```plain
mysql> select hostgroup_id, hostname, port, status
       from runtime_mysql_servers
       where hostgroup_id >= 500;
+--------------+----------------+------+---------+
| hostgroup_id | hostname       | port | status  |
+--------------+----------------+------+---------+
| 500          | 172.16.121.237 | 3307 | ONLINE  |
| 501          | 172-16-121-236 | 3307 | ONLINE  |
| 501          | 172.16.121.236 | 3307 | ONLINE  |
| 502          | 172-16-121-237 | 3307 | ONLINE  |
| 503          | 172-16-121-234 | 3307 | SHUNNED |
| 503          | 172.16.121.234 | 3307 | SHUNNED |
+--------------+----------------+------+---------+

```

### 场景4：强制查询走主库

使用读写分离时，有时候我们可能想让一些查询到主库上执行。这里提供一些强制让查询路由到主库的方法。

#### 方法一：使用用户表的transaction\_persistent设置

先把用户transaction\_persistent字段设置为1。

```plain
update mysql_users set transaction_persistent=1 where username='user1';
load mysql users to runtime;

```

查询前先开启事务，这样查询就会转发到主库。

```plain
mysql> start transaction read only;
Query OK, 0 rows affected (0.00 sec)

mysql> select @@hostname;
+----------------+
| @@hostname     |
+----------------+
| 172-16-121-236 |
+----------------+
1 row in set (0.00 sec)

mysql> commit;
Query OK, 0 rows affected (0.00 sec)

```

#### 方法二：使用query注释

还有一种方法是通过注释，指定主库的hostgroup。

```plain
mysql> SELECT /*+ ;hostgroup=200 */ @@hostname;
+----------------+
| @@hostname     |
+----------------+
| 172-16-121-236 |
+----------------+
1 row in set (0.00 sec)

mysql> SELECT /*+ ;hostgroup=201 */ @@hostname;
+----------------+
| @@hostname     |
+----------------+
| 172-16-121-237 |
+----------------+
1 row in set (0.00 sec)

```

需要注意，如果指定的hostgroup不存在，查询会超时。

```plain
mysql> SELECT /*+ ;hostgroup=999 */ @@hostname;
ERROR 9001 (HY000): Max connect timeout reached while reaching hostgroup 999 after 10000ms

```

### 场景5：SQL黑名单

利用mysql\_query\_rules表中的error\_msg字段，可以实现SQL黑名单的功能。如果规则设置了error\_msg，当SQL语句匹配这条规则时，proxysql会直接将error\_msg的内容返回给客户端。

当遇到一些大查询严重影响数据库性能时，可以使用proxysql规则临时屏蔽这些SQL。

#### 查询stats\_mysql\_query\_digest

假设我们想屏蔽下面这条SQL。

```plain
select count(*) from information_schema.tables;

```

先到stats\_mysql\_query\_digest查询这个SQL的摘要，使用SQL摘要可以精确屏蔽某一类SQL。

```plain
mysql> select * from stats.stats_mysql_query_digest
  where digest_text like '%tables%' limit 1\G

*************************** 1. row ***************************
        hostgroup: 201
       schemaname: information_schema
         username: user1
   client_address:
           digest: 0x98CB260C02C33558
      digest_text: select count(*) from information_schema.tables
       count_star: 1
       first_seen: 1731567555
        last_seen: 1731567555
         sum_time: 25779
         min_time: 25779
         max_time: 25779
sum_rows_affected: 0
    sum_rows_sent: 1

```

#### 配置屏蔽规则

我们选择按查询的digest来屏蔽，往mysql\_query\_rules写入下面这条规则。

```plain
insert into mysql_query_rules
(rule_id, username, digest, error_msg, active, apply, comment )
values (10, 'user1', '0x98CB260C02C33558', 'request denied by rule' ,1,1, 'request denied by rule');

load mysql query rules to runtime;
save mysql query rules to disk;

```

需要注意，屏蔽规则的rule\_id需要比其它规则的rule\_id小，proxysql是按rule\_id的顺序依次判断是否匹配规则。

#### 测试屏蔽效果

使用digest，屏蔽的是一类SQL，如果SQL只是传入的参数有差异，SQL的digest一样，那么也会匹配该规则。

```plain
mysql> select count(*) from information_schema.tables;
ERROR 1148 (42000): request denied by rule

```

### 场景6：改写SQL

使用查询修改功能，可以在不改变应用程序的情况下，修改SQL语句。比如，我们可以使用SQL改写的功能，给SQL添加hint，以此来优化性能。

```plain
delete from mysql_query_rules;

insert into mysql_query_rules
(rule_id, username, match_pattern, replace_pattern,
  destination_hostgroup, active, apply, comment )
values (20, 'user1',
  '^SELECT\s+(.*?)\s+FROM\s+ta\s+where\s+a\s+=\s+(\d+)$',
  'SELECT \1 FROM ta force index(idx_a) WHERE A = \2',
  200, 1, 1, 'add force index');

load mysql query rules to runtime;

```

在上面的例子中，我们给TA表的查询加上了force index提示。

```plain
mysql> select * from ta where a = 10;
ERROR 1176 (42000): Key 'idx_a' doesn't exist in table 'ta'

mysql> select a, val from ta where a = 10;
ERROR 1176 (42000): Key 'idx_a' doesn't exist in table 'ta'

```

### 场景7：SQL Mirror

使用ProxySQL的镜像（mirror）功能，可以把SQL发送到一个额外的后端实例执行。

还可以把发送到镜像的SQL进行改写，以测试修改后的SQL是否能正常执行。

通过mirror\_flagOut字段，可以将多条规则串联起来。

```plain
delete from mysql_query_rules;

-- 执行SQL，同时将SQL mirror一份
insert into mysql_query_rules
(rule_id, username, match_pattern, destination_hostgroup,
 mirror_flagOut, active, apply, comment )
values (20, 'user1', '^SELECT', 200,
  1001, 1, 1, 'mirror');

-- 对于mirror的SQL，增加注释，发送到hostgroup 201执行
insert into mysql_query_rules
(rule_id, username, flagIn, match_pattern, destination_hostgroup,
 replace_pattern, active, apply, comment )
values (21, 'user1', 1001, '^SELECT', 201,
  'select /*+ mirrored */', 1, 1, 'mirror sql modified');

load mysql query rules to runtime;

```

上面的例子中，rule\_id为20的规则，设置了mirror\_flagOut=1001，rule\_id为21的规则，设置了flagIn=1001，也就是将转发给hostgroup 200的Select语句，同时也转发一份到hostgroup 201，转发时，还加上了一个注释。

## ProxySQL本身的高可用

ProxySQL作为一个程序，本身也可能出现故障。部署ProxySQL的服务器也可能出现故障。高可用架构的一个基本原则是消除单点。那我们怎么解决ProxySQL的单点问题呢？

我们来看解决办法。你可以在多台服务器上部署ProxySQL，在ProxySQL前再加一层负载均衡（如使用LVS或其他网络层的技术），从而消除ProxySQL的单点。

![图片](https://static001.geekbang.org/resource/image/36/ca/3654072765f00ee62a2fb7f95285a7ca.jpg?wh=1344x974)

部署多台ProxySQL后，需要保证配置信息同步。不然就可能会引起客户端访问出错。可以使用ProxySQL自带的集群功能，来实现多个节点之间的配置信息同步。

开启ProxySQL的集群功能，需要做一些配置。

1. 配置cluster账号，用于查询对比集群内各proxysql节点的配置信息。

2. 配置proxysql\_servers，将集群内的proxysql节点信息添加到proxysql\_servers表。


这些操作要到集群中的所有ProxySQL节点上执行。

### 配置cluster账号

通过参数admin-cluster\_username和admin-cluster\_password设置cluster账号。不能使用admin账号作为cluster账号，因为admin账号只能在本地（127.0.0.1）登录。同时还需要将cluster账号添加到参数admin-admin\_credentials中。

```plain
set admin-admin_credentials = 'admin:admin;clusteradmin:passadmin';

set admin-cluster_username='clusteradmin';
set admin-cluster_password='passadmin';

load admin variables to runtime;
save admin variables to disk;

```

### 使用ProxySQL集群

我们把组成proxysql集群的多个节点的信息添加到proxysql\_servers表。

```plain
mysql> show create table proxysql_servers\G
*************************** 1. row ***************************
       table: proxysql_servers
Create Table: CREATE TABLE proxysql_servers (
    hostname VARCHAR NOT NULL,
    port INT NOT NULL DEFAULT 6032,
    weight INT CHECK (weight >= 0) NOT NULL DEFAULT 0,
    comment VARCHAR NOT NULL DEFAULT '',
    PRIMARY KEY (hostname, port) )
1 row in set (0.00 sec)

insert into proxysql_servers（hostname, port, weight, comment)
    values('172.16.121.234', 6032, 1, 'proxysql node 1');

insert into proxysql_servers
    values('172.16.121.236', 7032, 1, 'proxysql node 2');

load proxysql servers to runtime;
save proxysql servers to disk;

```

这样配置好之后，在一个ProxySQL节点上修改的配置，会自动同步到集群的其他节点上。

## ProxySQL配置表参考

ProxySQL的配置主要通过一些配置表来实现。这里我对文章中用到的几个配置表做一个简单的说明，方便你查看。更详细的信息，你可以看 [官方文档](https://proxysql.com/documentation/main-runtime/)。

### mysql\_servers

![图片](https://static001.geekbang.org/resource/image/59/8f/5926bf91221e0a9fd9028ca63a3b3f8f.png?wh=1518x1406)

### mysql\_users

![图片](https://static001.geekbang.org/resource/image/b0/dc/b00d47234ce3276dab01a285abb00bdc.png?wh=1518x1440)

### mysql\_query\_rules

![图片](https://static001.geekbang.org/resource/image/9d/6f/9d0c9607f8127e64fef00982be82b36f.png?wh=1620x1532)

### mysql\_replication\_hostgroups

![图片](https://static001.geekbang.org/resource/image/c9/f2/c9c36e35e9608yy0928yy587b56ce6f2.png?wh=1920x764)

### mysql\_group\_replication\_hostgroups

![图片](https://static001.geekbang.org/resource/image/1a/39/1a777fa64274d8f256eebccf7d722839.png?wh=1470x1374)

## 总结

在应用程序和后端MySQL之间，增加一层Proxy，可以向应用屏蔽掉后端MySQL主备切换的一些细节。这样对应用程序而言，使用起来更加方便。同时，Proxy还可以起到连接池的作用。

这里，其实还有一个问题没有解决，就是后端的MySQL怎么切换？早期比较有名的是MHA工具。在云上，各个云厂商提供的RDS高可用版本，一般都标配了数据库自动切换的功能。

如果是自建的环境，你可以调研下一些开源的工具，比如MHA、Orchestrator等。如果数据库的数量有一定的规模，你也可以考虑自己实现一个数据库自动切换的工具。

## 思考题

如果自己实现一个MySQL的自动切换程序，要考虑哪些方面的问题？

期待你的思考，欢迎在留言区中与我交流。如果今天的课程让你有所收获，也欢迎转发给有需要的朋友。我们下节课再见。