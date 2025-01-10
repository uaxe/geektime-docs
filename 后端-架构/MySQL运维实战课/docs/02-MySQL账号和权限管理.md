你好，我是俊达。

在上一讲中，我们学习了安装MySQL的几种方法。MySQL安装好之后，系统默认建好了root@localhost用户，这个用户只能在MySQL服务器上登录本地的数据库。root账号拥有数据库所有的权限，可以执行任何操作，因此我建议应用程序不要使用root账号访问数据库，这存在很大的安全隐患。

我们需要根据各个业务方的访问需求，分别创建数据库用户，并授予合理的权限。在这一讲中，我们来学习如何创建和管理数据库用户，以及如何给用户授权。

## 用户管理

我们使用create user命令创建用户，你可以看一下命令的基本格式。

```plain
create user 'username'@'host' identified by 'complex_password';

```

在MySQL中，一个用户由两部分组成，username是用户名，host是允许登录数据库的客户端的主机名或IP。host中可以使用通配符，使用百分号 `"%"` 匹配任意字符串，使用下划线 `"_"` 匹配一个字符。比如我们下面创建的这个用户，可以在任何地方登录数据库。

```plain
create user 'u01'@'%' identified by 'somepassword';

```

创建账号时，也可以使用IP地址段来指定客户端IP范围，比如下面创建的u02用户可以在172.16这个网段内访问数据库。

```plain
create user 'u02'@'172.16.0.0/16' identified by 'somepassword';

```

### 用户条目的优先级

MySQL允许创建username相同，但host不同的用户。

```plain
create user 'u03'@'%' identified by 'somepassword';
create user 'u03'@'172.16.0.0/16' identified by 'somepassword';
create user 'u03'@'mysql02' identified by 'somepassword';
create user 'u03'@'172.16.121.%' identified by 'somepassword';
create user 'u03'@'172.16.121.237' identified by 'somepassword';

```

我们上面创建了5个用户，虽然用户名都是u03，但这是5个不同的用户，可以分别给这5个用户设置不同的密码、授予不同的权限。你可以在mysql.user表中查询到这些用户。

```plain
mysql> select user,host from mysql.user where user='u03';
+------+----------------+
| user | host           |
+------+----------------+
| u03  | %              |
| u03  | 172.16.0.0/16  |
| u03  | 172.16.121.%   |
| u03  | 172.16.121.237 |
| u03  | mysql02        |
+------+----------------+
5 rows in set (0.00 sec)

```

那么问题来了，当使用u03这个用户名登录数据库时，服务端应该使用哪条用户信息来验证用户密码呢？与之相关的还有另外一个问题，使用u03登录数据库后，我怎么知道当前登录的是哪个u03？我们先来回答后面这个问题，登录数据库之后，可以用函数current\_user来获取当前的登录用户，或者用show grants命令也能看到当前的登录用户。

```plain
# mysql -u u03 -psomepassword -h172.16.121.234

mysql> select current_user();
+-------------------+
| current_user()    |
+-------------------+
| u03@172.16.0.0/16 |
+-------------------+
1 row in set (0.01 sec)

mysql> show grants;
+---------------------------------------------+
| Grants for u03@172.16.0.0/16                |
+---------------------------------------------+
| GRANT USAGE ON *.* TO `u03`@`172.16.0.0/16` |
+---------------------------------------------+
1 row in set (0.00 sec)

```

至于前面那个问题，用户表中的每一行记录，都有相应的优先级。MySQL会把所有的用户记录按优先级从高到低的顺序排列，缓存到内存里。服务端接收到客户端发起的连接请求后，从请求包中解析出用户名和密码信息，从tcp连接信息中得到客户端的IP，然后依次匹配缓存的用户记录列表中的条目。

先匹配host字段，如果host匹配，再匹配用户名，用户名也匹配后，再验证密码是否正确。如果匹配不到对应的用户记录，或密码不正确，或存在其它问题，服务端会把错误信息发送给客户端。用户验证成功后，客户端就可以开始执行各类命令或SQL，此时服务端会验证用户是否有权限执行这些命令和SQL。

mysql.user表中用户条目的优先级如何确定呢？

基本的规则是这样的：

1. IP条目的优先级最高。IP条目中没有通配符，精确的IP和IP地址段都是IP条目。
2. 精确IP的优先级比IP地址段的优先级高。
3. 对于2个IP地址段，前缀长的优先级更高。比如172.16.121.0/24优先级比172.16.0.0/16高。
4. 不使用通配符的条目比使用通配符的条目优先级高。
5. 对于都使用了通配符的条目，则根据第一个通配符在host字段中出现的位置来判断优先级。通配符出现的位置越靠前，优先级越低。比如 `'%'` 的优先级最低， `'abc%'` 的优先级比 `'abcd%'` 低。

在我们前面的这个例子中，u03的5条用户条目按优先级从高到低排序后是这样的。

```plain
'u03'@'172.16.121.237'
'u03'@'172.16.0.0/16'
'u03'@'mysql02'
'u03'@'172.16.121.%'
'u03'@'%'

```

我们可以通过一些例子来进行验证。

- 客户端地址为172.16.121.236，匹配到的用户条目为 `'u03'@'172.16.0.0/16'`。

```plain
[root@172-16-121-236 ~]# mysql -u u03 -psomepassword -h172.16.121.234 -e 'select current_user()'
+-------------------+
| current_user()    |
+-------------------+
| u03@172.16.0.0/16 |
+-------------------+

```

- 客户端地址为172.16.121.237，匹配到的用户条目为 `'u03'@'172.16.121.237'`。

```plain
[root@172-16-121-237 ~]# mysql -u u03 -psomepassword -h172.16.121.234 -e 'select current_user()'
+--------------------+
| current_user()     |
+--------------------+
| u03@172.16.121.237 |
+--------------------+

```

- 客户端地址为192.168.x.x，匹配到的用户条目为 `'u03'@'%'`。

```plain
mysql -u u03 -psomepassword -h172.16.121.234 -e 'select current_user()'
mysql: [Warning] Using a password on the command line interface can be insecure.
+----------------+
| current_user() |
+----------------+
| u03@%          |
+----------------+

```

前面我们提到了，服务端会根据客户端的IP地址来查找用户条目。MySQL怎么判断某个客户端跟某个主机名相匹配呢？服务端需要将客户端的IP反解析成主机名，然后才能进行判断。比如MySQL服务器的/etc/hosts有下面这条信息。

```plain
## /etc/hosts
172.16.121.236 mysql02

```

那么从172.16.121.236连接数据库时，客户端主机名就会解析为mysql02，使用下面这个方法就可以清楚地看到这一点。我们故意使用了错误的密码，服务端会将错误消息发送给客户端。请注意下面例子里错误消息中用户名的格式。

```plain
[root@172-16-121-236 ~]#  mysql -u u03 -pwrongpassword -h172.16.121.234
ERROR 1045 (28000): Access denied for user 'u03'@'mysql02' (using password: YES)

$ mysql -u u03 -pwrongpassword -h172.16.121.234 -e 'select current_user()'
ERROR 1045 (28000): Access denied for user 'u03'@'192.168.113.13' (using password: YES)

```

在真实环境中，我们经常会设置skip\_name\_resolve，这样MySQL就只会根据IP来验证用户，不需要再将IP反解析成主机名。

```plain
## my.cnf
skip_name_resolve

```

在MySQL 5.6和更早的版本中，使用mysql\_install\_db来初始化数据库。初始化脚本执行时，会创建一个用户名为空的无密码用户，这会引起一个问题。我们通过一个例子来说明。我们先创建一个用户名为空的用户，模拟早期MySQL版本的行为。

```plain
mysql> create user ''@'localhost' ;
Query OK, 0 rows affected (1.26 sec)

```

然后在数据库服务器本地使用一个正常的账号登录数据库，你会发现无法登录，报密码错误。

```plain
[root@172-16-121-234 ~]# mysql -u u03 -psomepassword -h 127.0.0.1
ERROR 1045 (28000): Access denied for user 'u03'@'localhost' (using password: YES)

```

但实际上，这并不是密码问题，而是在本地登录时，使用了 `''@'localhost'` 这个条目来进行用户认证。下面这个测试案例就能说明这一点。

```plain
[root@172-16-121-234 ~]# mysql -u u03 -h 127.0.0.1 -e 'select current_user()'
+----------------+
| current_user() |
+----------------+
| @localhost     |
+----------------+

```

这个问题的解决方法一般就是 **删除用户名为空的用户**。

### 密码验证组件

不要给MySQL用户设置过于简单的密码，可以通过密码验证组件来强制密码的复杂度。使用RPM安装的MySQL默认就已经开启了密码验证组件。如果你使用了二进制安装，可以用命令INSTALL COMPONENT来启用密码验证。

```plain
mysql> INSTALL COMPONENT 'file://component_validate_password';
Query OK, 0 rows affected (1.03 sec)

```

开启密码验证组件后，你就无法创建密码过于简单的用户了。

```plain
mysql> create user 'ux'@'%' identified by 'simplepassword';
ERROR 1819 (HY000): Your password does not satisfy the current policy requirements

```

需要在密码中使用数字、大小写字母和特殊字符，而且密码要超过一定的长度。

```plain
mysql> create user 'ux'@'%' identified by 'Complex-Password-2024';
Query OK, 0 rows affected (1.04 sec)

```

密码验证组件有几个参数可以配置，你可以根据自己的需求适当调整这些参数。

```plain
mysql> show variables like 'validate_password%';
+--------------------------------------+--------+
| Variable_name                        | Value  |
+--------------------------------------+--------+
| validate_password.check_user_name    | ON     |
| validate_password.dictionary_file    |        |
| validate_password.length             | 8      |
| validate_password.mixed_case_count   | 1      |
| validate_password.number_count       | 1      |
| validate_password.policy             | MEDIUM |
| validate_password.special_char_count | 1      |
+--------------------------------------+--------+

```

### 忘记密码处理

上一讲结束时，我留了一个思考题，root密码忘记了怎么处理？我们可以使用参数skip-grant-tables来解决这个问题。先停止MySQL，由于已经忘记了管理员密码，无法使用shutdown命令正常关闭MySQL，可以直接kill mysqld进程。

然后启动MySQL，加上skip-grant-tables选项。

```plain
/usr/local/mysql/bin/mysqld_safe \
    --defaults-file=/data/mysql01/my.cnf \
    --skip-grant-tables \
    --skip-networking  &

```

加上skip-grant-tables选项后，不需要密码就能登录数据库。此时MySQL也不会验证权限。

```plain
# mysql -uroot -S /data/mysql01/run/mysql.sock

```

登录后，需要先执行flush privileges命令，加载用户和权限相关的表，再执行alter user命令修改密码，然后重新启动MySQL，就可以正常访问数据库了。

```plain
mysql> flush privileges;
Query OK, 0 rows affected (0.55 sec)

mysql> alter user 'root'@'localhost' identified by 'newpassword';
Query OK, 0 rows affected (0.93 sec)

```

## 权限管理

新创建的用户只有Usage权限，只能执行一些最基本的操作。用户需要授权后，才能执行其他的一些操作，比如建库建表，读写数据。在MySQL中使用grant语句进行授权。grant语句的基本语法如下：

```plain
grant privileges
on something
to 'user'@'host';

```

早期版本中，如果被授权的用户不存在，那么在执行grant语句时，会自动创建这个用户。在MySQL 5.7中，SQL\_MODE中加入了NO\_AUTO\_CREATE\_USER选项，用来避免这种grant语句自动创建用户的行为。到了MySQL 8.0，已经不再支持NO\_AUTO\_CREATE\_USER选项了。

执行grant时，被授权的用户必须已经存在，否则会报错。

```plain
mysql> grant select on *.* to 'readonly'@'%';
ERROR 1410 (42000): You are not allowed to create a user with GRANT

```

在MySQL中，有的权限是全局的，这些权限跟某个具体的数据库没有关系，授权时需要使用 `on *.*`，比如下面这个例子给用户u03授权了查看process列表的权限。

```plain
grant process on *.* to 'u03'@'%';

```

有的权限跟数据库或数据库中的对象相关，授权时可以指定具体的数据库或数据库对象。下面这个grant语句给用户u03授权了数据库db01的DDL权限。

```plain
grant create,index,alter,drop on db01.* to 'u03'@'%';

```

授权后，u03可以创建库名为db01的数据库，并在这个库中创建表、修改表结构、DROP表，但是不能读写表中的数据。

```plain
mysql> show grants;
+----------------------------------------------------+
| Grants for u03@%                                   |
+----------------------------------------------------+
| GRANT USAGE ON *.* TO `u03`@`%`                    |
| GRANT CREATE, INDEX, DROP, ALTER ON `db01`.* TO `u03`@`%` |
+----------------------------------------------------+

## 可以创建库名为db01的数据库
mysql> create database db01;
Query OK, 1 row affected (2.91 sec)

## 但是不能创建其他数据库
mysql> create database db02;
ERROR 1044 (42000): Access denied for user 'u03'@'%' to database 'db02'

## 可以创建表，修改表结构，DROP表，但是不能读写表中的数据
mysql> create table t1(a int, b int);
Query OK, 0 rows affected (11.54 sec)

mysql> alter table t1 add c int;
Query OK, 0 rows affected (4.98 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> insert into t1 values(1,2,3);
ERROR 1142 (42000): INSERT command denied to user 'u03'@'192.168.113.13' for table 't1'

mysql> select * from t1;
ERROR 1142 (42000): SELECT command denied to user 'u03'@'192.168.113.13' for table 't1'

```

需要给账号添加相应的权限后，才能访问表中的数据。

```plain
mysql> grant select,insert,update,delete on db01.* to 'u03'@'%';
Query OK, 0 rows affected (2.31 sec)

```

```plain
mysql> show grants;
+-------------------------------------------------------------------------------------------+
| Grants for u03@%                                                                          |
+-------------------------------------------------------------------------------------------+
| GRANT USAGE ON *.* TO `u03`@`%`                                                           |
| GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER ON `db01`.* TO `u03`@`%` |
+-------------------------------------------------------------------------------------------+
2 rows in set (0.01 sec)

mysql> insert into t1 values(1,2,3);
Query OK, 1 row affected (0.28 sec)

mysql> select * from t1;
+------+------+------+
| a    | b    | c    |
+------+------+------+
|    1 |    2 |    3 |
+------+------+------+
1 row in set (0.01 sec)

```

grant语句中，授权对象（库名和对象名）也可以使用通配符，使用 `"%"` 匹配任意字符，使用 `"_"` 匹配一个字符。

```plain
grant create,drop,alter,index on `db__`.* to 'u03'@'%';

```

授权后，u03用户可以创建库名以db开头，并且库名长度是4个字节的数据库。

```plain
mysql> create database db_1;
Query OK, 1 row affected (1.89 sec)

mysql> create database db_2;
Query OK, 1 row affected (0.12 sec)

mysql> create database db_10;
ERROR 1044 (42000): Access denied for user 'u03'@'%' to database 'db_10'

```

如果库名中有下划线 `"_"`，可以在grant时使用转义符对通配符 `"_"` 进行转义。下面的SQL把db\_1库的读写权限赋给了u03用户。

```plain
mysql> grant select,insert,update,delete on `db\_1`.* to 'u03'@'%';
Query OK, 0 rows affected (0.91 sec)

```

我们先使用show grants命令查看u03用户当前的权限。

```plain
mysql> show grants;
+----------------------------------------------------------------+
| Grants for u03@%                                               |
+----------------------------------------------------------------+
| GRANT USAGE ON *.* TO `u03`@`%`                                |
| GRANT SELECT, INSERT, UPDATE, DELETE ON `db01`.* TO `u03`@`%`  |
| GRANT SELECT, INSERT, UPDATE, DELETE ON `db\_1`.* TO `u03`@`%` |
| GRANT CREATE, DROP, INDEX, ALTER ON `db__`.* TO `u03`@`%`      |
+----------------------------------------------------------------+

```

从上面的输出可以看出，u03用户有数据库db01、db\_1的DDL权限和数据读写权限，有库名以db开头并且长度为4个字节的数据库的DDL权限。

但是在下面这个测试中，我们可以看到，在db\_1库中执行DDL时，报权限不足。

```plain
mysql> use db_2;
Database changed

mysql> create table t1(a int);
Query OK, 0 rows affected (14.64 sec)

mysql> use db_1;
Database changed

mysql> create table t1(a int);
ERROR 1142 (42000): CREATE command denied to user 'u03'@'192.168.113.13' for table 't1'

```

为什么会出现这样的问题呢？大概是因为MySQL只使用了库名为 `'db\_1'` 的这条授权记录。从权限表mysql.db中可以看到，db\_1这个库没有create权限。

```plain
mysql> select user,host, db, create_priv from mysql.db where user='u03';
+------+------+-------+-------------+
| user | host | db    | create_priv |
+------+------+-------+-------------+
| u03  | %    | db01  | N           |
| u03  | %    | db\_1 | N           |
| u03  | %    | db__  | Y           |
+------+------+-------+-------------+
3 rows in set (0.00 sec)

```

为了解决这个问题，可以将数据库db\_1的DDL的权限也授予u03。

```plain
mysql> grant create,alter,index,drop on `db\_1`.* to 'u03'@'%';
Query OK, 0 rows affected (0.55 sec)

```

重新授权后，用户u03就可以在数据库db\_1中执行DDL操作了。

### MySQL中有哪些权限

我们使用下面这个表格对MySQL中的一些权限做一个简单的介绍。

![图片](https://static001.geekbang.org/resource/image/e9/ac/e914049f835f8c8563db560b104d78ac.jpg?wh=1920x2848)

### 最小权限原则

管理数据库用户的权限时，要遵循最小权限原则。root用户要交给少数管理人员管理，其他任何人不能使用root用户。有的公司出于安全考虑，还会删除系统自带的root用户，并单独创建一个超级管理员用户。给不同的业务方分配不同的用户，并按业务的实际需求授予最小的权限。

举例来说，如果业务方的需求是同步数据库中的数据，只需要对库表授予SELECT权限。对于一般的应用程序，需要读写数据，授予SELECT、INSERT、UPDATE、DELETE、EXECUTE这些权限就可以了。对于DBA或运维人员，需要执行数据库变更，可以授予CREATE、ALTER、DROP、INDEX等DDL权限，以及PROCESS、SUPER等管理权限。

另外需要注意的一点，给不同环境的数据库创建不同的用户。开发环境和生产环境的用户，不要使用相同的密码。不同的业务方共用同一个用户、授予用户超出需要的权限、开发环境和生产环境使用相同的用户名和密码，都会给数据库安全带来极大的风险。

有时候为了方便，你可能会把all privileges授予一个用户，然后所有业务方都使用这个用户来访问数据库。这是非常危险的，千万不要这么做。

我遇到过很多数据库权限设置不当引起的故障。比如开发人员使用图形化管理工具连接到正式环境的数据库，然后在界面上把整个库都删掉了。数据分析人员使用第三方程序库连接生产环境的数据库做数据分析，但是由于配置不当，第三方程序库在关闭数据库连接时将表DROP了。DBA在导入数据时，本来应该到测试环境操作，但是错误地将导入命令贴到了生产环境的终端下执行，而且生产环境和测试环境的用户名和密码还都是一样的，然后在导入数据时将生产环境的表都先DROP掉了。

这些场景下，如果我们遵循了最小权限原则，至少可以避免一部分重大故障。如果你使用了只读账号，即使错误地执行了DROP命令，但是由于用户权限不足，数据库和表并不会被真正DROP。如果生产环境和开发环境设置了不同的用户名和密码，即使错误地将命令贴到了生产环境，因为密码不对，也不会对生产环境造成影响。

## 总结

这一讲我们学习了MySQL用户和权限管理。MySQL的用户由用户名和主机名两部分组成。用户名相同，但主机名不同的多个用户，实际上是完全独立的用户，为了便于管理，要尽量避免创建这样的用户。如果你要限制数据库只允许某些IP访问，可以考虑从网络防火墙层面来限制。用户密码应该要有一定的复杂度，可以启用密码验证组件，防止给数据库用户设置过于简单的密码。授权时，要遵循 **最小权限原则**，给用户授予正常业务需求之外的权限会带来额外的安全风险。

## 思考题

一般情况下，我们都建议将数据库部署到内网，因为将数据库暴露到公网上有比较大的安全风险。但是你的公司有一个特殊的业务，就是需要通过公网访问MySQL数据库。请你评估下将数据库放到公网有哪些风险？你应使用哪些方法来尽量保证数据库和数据的安全？

期待你的思考，欢迎在留言区中与我交流。如果今天的课程让你有所收获，也欢迎转发给有需要的朋友。我们下节课再见！