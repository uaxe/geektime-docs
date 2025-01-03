你好，我是俊达。

在第一讲中，我们使用了一个极简的配置文件，只包含了最基本的一些参数，使MySQL能正常运行起来，便于我们进行测试、熟悉MySQL。但是供正式环境使用的MySQL就不能仅仅依赖这个基础的配置了，我们需要根据部署MySQL的主机配置、使用MySQL的业务场景等因素，设置合理的参数，使MySQL能以比较高的性能运行，并满足业务对数据一致性的要求。

这一讲中，我们会介绍MySQL参数配置的基本机制。然后再介绍一些比较重要的参数，讲解这些参数的作用是什么，如何合理地设置这些参数。你可以根据这里提供的基本方法，为自己的MySQL设置一个相对合理的配置。

## MySQL参数设置机制

MySQL 8.0总共有六百多个配置参数。有时候我们也将这些参数称为变量，因为官方文档中的术语是Variables。同时在MySQL中，我们使用命令show variables查看参数的当前值。因此在这一系列的课程中，“参数”和“变量”很多时候指的都是同一个概念。

### 设置参数

有几个方法都可以用来设置参数。首先mysqld进程启动时，可以指定一系列的命令行参数。下面是一个比较典型的例子。

```go
$ ps -elf | grep mysqld
... /usr/local/mysql/bin/mysqld \
    --defaults-file=/data/mysql01/my.cnf \
    --basedir=/usr/local/mysql \
    --datadir=/data/mysql01/data \
    --plugin-dir=/usr/local/mysql/lib/plugin \
    --user=mysql \
    --log-error=/data/mysql01/log/alert.log \
    --open-files-limit=1024 \
    --pid-file=/data/mysql01/run/mysqld.pid \
    --socket=/data/mysql01/run/mysql.sock

```

当然更多的情况下，我们会把参数写到配置文件中。MySQL默认会从一些固定位置读取配置。执行mysqld --verbose --help命令可以观察到mysqld读取默认参数文件的路径。

```go
/opt/mysql# ./bin/mysqld --verbose --help | head -30
......

Default options are read from the following files in the given order:
/etc/my.cnf /etc/mysql/my.cnf /usr/local/mysql/etc/my.cnf ~/.my.cnf
The following groups are read: mysql_cluster mysqld server mysqld-8.0

```

上面的例子中，mysqld默认会从 `/etc/my.cnf`、 `/etc/mysql/my.cnf`、 `/usr/local/mysql/etc/my.cnf ~/.my.cnf` 多个文件依次读取配置。如果某个参数在多个文件都有配置，那么就以最后读取到的那个参数值为准。当然，为了避免引起混乱，我建议一个MySQL实例只使用一个配置文件。在启动MySQL时，可以使用命令行参数defaults-file指定配置文件，指定这个参数后，MySQL只会从这个文件中读取配置项。需要注意，defaults-file在所有命令行参数中必须排在最前面才有效。

```go
mysqld --defaults-file=/data/mysql3306/my.cnf --datadir=......

```

MySQL的参数中，有的是只读的，你不能修改这些参数。比如参数lower\_case\_file\_system反映了数据目录所在的文件系统是否区分文件名大小写，它是由底层操作系统的特性决定的，无法通过参数来修改。一般Linux和macOS文件名区分大小写，Windows不区分文件名大小写。

有一些参数不能动态修改，你只能将参数加到命令行，或者将参数写到配置文件中。MySQL只有在启动时才会读取这些参数。比如参数port指定了数据库的监听端口，要修改这个参数，只能重启数据库。

还有很多参数可以动态修改，你可以通过SET命令修改这些参数。

```go
mysql> set global slow_query_log=ON;
Query OK, 0 rows affected (0.01 sec)

```

通过SET命令设置的参数，只对当前运行中的实例生效，实例重启后，这些设置就失效了。MySQL 8.0开始支持参数修改持久化，通过SET PERSIST命令来设置。

```go
mysql> set persist slow_query_log=ON;
Query OK, 0 rows affected (0.00 sec)

```

set persist命令不仅修改了参数的当前值，还会将参数的设置保存在数据目录（datadir）下的mysqld-auto.cnf文件中。MySQL重启时，会加载mysqld-auto.cnf文件中保存的参数。当然，你也可以通过reset persist命令将参数从mysqld-auto.cnf中移除。reset persist不会修改变量的当前值。

```go
mysql> reset persist slow_query_log;
Query OK, 0 rows affected (0.00 sec)

```

按参数的作用范围来看，MySQL的参数分为全局参数和会话参数。全局参数对整个实例生效，需要用SET GLOBAL命令设置，使用SET命令会报错。

```go
mysql> set innodb_flush_log_at_timeout=1;
ERROR 1229 (HY000): Variable 'innodb_flush_log_at_timeout' is a GLOBAL variable and should be set with SET GLOBAL

mysql> set global innodb_flush_log_at_timeout=1;
Query OK, 0 rows affected (0.00 sec)

```

会话参数只对某一个会话生效，使用SET命令设置，不能加GLOBAL关键字。

```go
mysql> set global timestamp=0;
ERROR 1228 (HY000): Variable 'timestamp' is a SESSION variable and can't be used with SET GLOBAL

mysql> set timestamp=0;
Query OK, 0 rows affected (0.00 sec)

```

MySQL中很多会话参数同时拥有同名的全局参数。使用SET GLOBAL命令时，设置的是全局变量的值，不影响现有会话的Session值，包括执行SET GLOBAL命令的那个会话。会话真正使用的是Session变量的值，会话创建时，会话变量会默认设置成全局变量的值，也可以使用SET命令修改会话变量。

```go
## 查看参数当前值
mysql> show variables like 'long_query_time';
+-----------------+----------+
| Variable_name   | Value    |
+-----------------+----------+
| long_query_time | 0.100000 |
+-----------------+----------+
1 row in set (0.00 sec)

## 设置全局值
mysql> set global long_query_time=10;
Query OK, 0 rows affected (0.00 sec)

## 当前值没有变化
mysql> show variables like 'long_query_time';
+-----------------+----------+
| Variable_name   | Value    |
+-----------------+----------+
| long_query_time | 0.100000 |
+-----------------+----------+
1 row in set (0.00 sec)

## 全局值被修改了
mysql> show global variables like 'long_query_time';
+-----------------+-----------+
| Variable_name   | Value     |
+-----------------+-----------+
| long_query_time | 10.000000 |
+-----------------+-----------+
1 row in set (0.00 sec)

```

percona的MySQL分支对参数long\_query\_time做了特殊处理，修改全局值时，也会修改当前已经存在的那些会话的参数值，这样更符合我们在这个场景下的需求。

如果想了解某个参数的具体含义，我的建议是查阅官方文档。

- [Server参数](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html)
- [InnoDB参数](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html)
- [主备复制相关参数](https://dev.mysql.com/doc/refman/8.0/en/replication-options-replica.html)

### 查看参数

一般我们使用show variables和show global variables命令查看参数的当前值。show global variables显示全局参数的配置值，show variables命令显示当前会话的所有参数值。

```go
mysql> show variables like 'wait%';
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| wait_timeout  | 28800 |
+---------------+-------+
1 row in set (0.01 sec)

mysql> show global variables  like 'wait%';
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| wait_timeout  | 86400 |
+---------------+-------+
1 row in set (0.01 sec)

```

在以前的MySQL版本中，如果想查看别的会话的某个参数值，没有很简便的方法。8.0中，可以到performance\_schema.variables\_by\_thread表查看其他会话的变量值。

```go
mysql>  select * from performance_schema.variables_by_thread
    where variable_name = 'wait_timeout';
+-----------+---------------+----------------+
| THREAD_ID | VARIABLE_NAME | VARIABLE_VALUE |
+-----------+---------------+----------------+
|        64 | wait_timeout  | 28800          |
|        65 | wait_timeout  | 3600           |
+-----------+---------------+----------------+

```

这个表的THREAD\_ID是线程ID，不是SHOW PROCESSLIST命令输出中的ID。PROCESSLIT\_ID和THREAD\_ID的关系可以到performance\_schema.threads表查找。

### 参数文件的格式

MySQL参数文件一般命名为my.cnf，当然你也可以使用不同的文件名，但需要在启动MySQL时，通过defaults-file参数指定配置文件的路径。参数文件分为多个组，组名用中括号\[\]括起来。一般将MySQL服务端的参数放到\[mysqld\]中。参数设置的一般格式为variable\_name=variable\_value，但是也有的参数值需要提供参数名，不需要提供参数值，如skip\_name\_resolve。

```go
[mysqld_safe]
pid-file=/data/mysql01/run/mysqld.pid

[mysqld]

basedir=/opt/mysql
lc_messages_dir=/opt/mysql/share
datadir=/data/mysql01/data
tmpdir=/data/mysql01/tmp
log-error=/data/mysql01/log/alert.log
slow_query_log_file=/data/mysql01/log/slow.log
general_log_file=/data/mysql01/log/general.log

socket=/data/mysql01/run/mysql.sock
skip_name_resolve

...

```

## 设置合理的参数

### 设置文件路径

MySQL有一系列与文件路径相关的参数，用来指定程序文件的路径和其他文件的存放路径。basedir指定MySQL程序的安装路径，如果MySQL程序没有安装在默认的路径，需要指定basedir。

datadir指定数据文件的存放路径，默认路径是在构建MySQL二进制时确定的。我建议在配置文件中显式指定datadir。如果因为各种原因需要将数据目录移动到其他路径下，要同步修改datadir参数，否则数据库会无法启动。datadir同时也决定了其他很多文件的存放路径，如innodb系统表空间、innodb REDO日志、binlog、relaylog默认都存放在datadir下。当然，我们可以通过一些参数修改这些文件的存放路径。下面这个表格总结了平时比较常用的文件路径相关的参数。

![图片](https://static001.geekbang.org/resource/image/6a/28/6acb451c80c32a8cd25bbc6cbd57be28.jpg?wh=1920x1052)

### 设置日志文件

MySQL的日志文件包括错误日志、慢SQL日志、General Log。建议开启慢SQL日志，这对SQL优化有比较重要的作用。general log一般不开启，只有在一些排查问题的场景下短暂开启。

```go
-- error
log_error=/data/mysql01/log/error.log
slow_query_log_file=/data/mysql01/log/slow.log
general_log_file=/data/mysql01/log/general.log

-- slow log，建议开启慢SQL日志
slow_query_log=ON
long_query_time=1 ## (单位秒，可以精确到1微秒)
log_queries_not_using_indexes=1
log_slow_admin_statements=1

```

### 设置资源限制参数

#### open\_files\_limit

参数open\_files\_limit限制了MySQL进程允许同时打开的文件句柄数。如果MySQL进程打开的文件句柄数达到open\_files\_limit，将无法打开新的文件，就会导致数据库访问异常。以下这些操作都需要占用文件句柄：

- 访问innodb数据文件
- 访问临时文件
- 建立TCP连接
- 访问其他文件（如日志文件）

open\_files\_limit最终的取值受几个因素影响。

1. open\_files\_limit受参数max\_connections和table\_open\_cache的影响。MySQL会将open\_files\_limit调整为以下几项的最大值：

- open\_files\_limit参数的设置值
- max\_connections + 2 \* table\_open\_cache + 10
- max\_connections \* 5

2. open\_files\_limit受操作系统open files限制。

启动mysqld进程时，如果父进程在操作系统中有open files（ulimit -n）限制，那么open\_files\_limit不能超过父进程的open files限制。 下面这个例子中，我们先在操作系统中su到MySQL，ulimit -n设置为1024，然后再启动MySQL数据库。

```go
# su - mysql
$ ulimit -n 1024
$ ulimit -n
1024

$ /usr/local/mysql/bin/mysqld_safe --defaults-file=/data/mysql01/my.cnf &

```

在MySQL的错误日志中，可以看到max\_open\_files被缩小为1024，而且参数max\_connections和table\_open\_cache也被改小了。

```go
[Server] Could not increase number of max_open_files to more than 1024 (request: 30000)
[Server] Changed limits: max_connections: 214 (requested 1000)
[Server] Changed limits: table_open_cache: 400 (requested 1000)

```

为了避免这个问题，需要在操作系统中提高用户的资源限制。

```go
### /etc/security/limits.conf
mysql       -       nofile  1000000
mysql       -       nproc   65535

```

#### max\_connections

max\_connections限制了数据库的最大连接数。需要注意的是max\_connections受参数max\_open\_files影响，它不能超过max\_open\_files - 810，因此在上面的例子中，虽然max\_connection配置为1000，但最终生效的值为214（1024 - 810）。

MySQL的每个连接都会占用一定的资源，max\_connections参数需要根据业务的实际连接需求以及服务器的可用资源来综合评估。

#### table\_open\_cache

table\_open\_cache控制数据库中允许同时打开的表的数量，这个参数的最终取值会受参数max\_open\_files和max\_connections实际运行值的影响。table\_open\_cache上限为(max\_open\_files - max\_connections - 10) / 2或400。在我们的例子中，虽然在参数文件中table\_open\_cache设置为1000，但实际运行时，该参数被调整为400。当数据库中表的数量比较大时，可以适当增加table\_open\_cache。

#### innodb\_open\_files

innodb\_open\_files控制允许同时打开的InnoDB文件的数量。该参数默认取table\_open\_cache的运行值。

#### table\_definition\_cache

MySQL将表结构定义也缓存在内存中，参数table\_definition\_cache设置了允许缓存的表结构定义的数量。如果InnoDB表的数量比较多，可以把这个参数也设置得大一些。

### 设置会话级内存参数

SQL执行的过程中，可能会需要分配一些临时的内存空间，会话级内存参数控制这些临时内存的大小。这些内存参数用来控制单个会话的内存，当多个会话同时执行时，无法限制这些内存的总大小。

#### sort\_buffer\_size

SQL执行时如果需要排序，会先在内存中排序，sort\_buffer\_size控制每个会话可用于排序的内存空间。8.0.12版本之前，如果SQL需要排序，会一次性分配sort\_buffer\_size指定的内存，即使需要排序的数据很少。8.0.12版本进行了优化，会根据实际需要的排序的数据按需分配排序内存，最多不超过sort\_buffer\_size。一般sort\_buffer\_size可以设置为256K-2M。

#### join\_buffer\_size

执行表连接的时候，如果被驱动表缺少索引，会使用BNL连接或Hash连接算法，优化器会根据参数join\_buffer\_size的设置，分配连接缓存，用来缓存驱动表的记录，以提高表连接操作的性能。注意一个SQL可能会使用多个Join Buffer。一般join\_buffer\_size设置为256K-2M。不建议把全局join\_buffer\_size设置得很大，如果有大查询需要使用更多的Join Buffer，可以在会话层面调整。

#### read\_rnd\_buffer\_size

参数read\_rnd\_buffer\_size用来控制MRR访问路径能使用的buffer的大小。关于MRR执行计划的更多信息，可以参考后续SQL优化的相关文章。

#### tmp\_table\_size

tmp\_table\_size控制内存临时表的最大空间，当内存临时表内的数据超过tmp\_table\_size后，会转换成磁盘临时表。如果有SQL需要排序大量数据，可以在会话级别调整这个参数。

### 设置InnoDB存储引擎参数

InnoDB存储引擎是MySQL实现事务ACID属性的关键所在，合理地设置InnoDB相关参数，是实现MySQL高性能和数据强一致的一个基本前提。InnoDB是一个复杂的系统，MySQL 8.0中InnoDB有一百多个参数，当然这里面很多参数使用默认值就可以了，这里对需要重点关注的部分参数做一个介绍。我们按InnoDB的内部结构来介绍这些参数。

下面这个图中，我们将InnoDB分为4个大的结构，分别是InnoDB Buffer Pool、InnoDB数据文件、Redo Log Buffer、Redo日志。

![图片](https://static001.geekbang.org/resource/image/a2/8c/a274bc40b8fc151dcbe04fb6e7f7ea8c.jpg?wh=1723x1077)

#### InnoDB Buffer Pool

访问InnoDB存储引擎表时，需要将数据先缓存到Buffer Pool，缓存的单位是一个数据页。数据页的大小通过参数innodb\_page\_size指定，默认为16K，一般我们使用默认值就可以了。

Buffer Pool的大小通过参数innodb\_buffer\_pool\_size指定，这可能是MySQL中最重要的一个参数。如果innodb\_buffer\_pool\_size设置得太小，无法把大部分热点数据缓存到内存中，会影响数据库的读写性能。但如果innodb\_buffer\_pool\_size设置得太大，又会导致服务器内存资源耗尽，可能会出现SWAP，或者触发OOM-Killer。我们需要根据服务器和MySQL使用的实际情况来设置innodb\_buffer\_pool\_size。

这里提供一个内存评估的方法，供你参考：

- 为操作系统预留一定的内存（min\_free\_kbytes，OS内核运行需要的基础内存），比如5%。
- OS其他程序运行占用的内存，比如MySQL数据库备份程序和其他程序。
- 文件系统Cache会占用一定的内存，比如InnoDB REDO日志、binlog文件。
- MySQL线程分配的内存，包括运行时分配的内存（join buffer, sort buffer, net buffer等）和thread\_stack。
- 如果大量使用MyISAM，需要分配key buffer。myisam数据文件还会使用文件系统cache。
- Inno DB buffer pool管理需要额外占用一部分内存，大致为innodb\_buffer\_pool\_size \* 5%。

除去上述各类内存，将剩余的内存分配给Buffer Pool。假设我们的服务器总共有100G内存，系统内存按下面这个表格来评估。

![图片](https://static001.geekbang.org/resource/image/68/9b/68fee2a6efc97dfcfc6dcae45049719b.png?wh=1920x1094)

那么，留给InnoDB Buffer Pool的内存为79G，考虑到InnoDB Buffer Pool的管理开销，innodb\_buffer\_pool\_size可设置为75G。当然在真实的业务场景下，MySQL连接线程会动态分配、释放内存，需要根据真实的运行情况，适当地调整内存设置。

InnoDB Buffer Pool分为多个内存块（Chunk），每个内存块的大小由参数innodb\_buffer\_pool\_chunk\_size指定，默认为128M。对于大内存的机器，可以适当增加innodb\_buffer\_pool\_chunk\_size，一个经验值是保持总的Chunk数不超过1000，比如Buffer Pool为1T，可以把innodb\_buffer\_pool\_chunk\_size设置为1G。

InnoDB Buffer Pool中存在大量链表结构，并发访问这些链表结构时，需要通过一些互斥锁、读写锁来保证这些数据结构的一致性。当数据库的并发很高的时候，在这些锁结构上会产生严重的争用。可以设置innodb\_buffer\_pool\_instances，把Buffer Pool划分成多个区块，减少争用。

MySQL 8.4中，这个参数默认值取以下两个数字中的较小值：

- 逻辑CPU核数/4
- innodb\_buffer\_pool\_size / innodb\_buffer\_pool\_chunk\_size / 2

我们也可以参考这个方法来得到innodb\_buffer\_pool\_instances的一个合理的设置。

我们通过SQL语句修改表中的数据时，先修改缓存在Buffer Pool中的页面。页面被修改后称为脏页。脏页中的数据最终需要写回到数据文件中。Page Cleaner线程定期扫描Buffer Pool中的脏页，发起IO请求，将脏页写回磁盘。innodb\_page\_cleaners控制Page Cleaner线程数量，可以将该参数和innodb\_buffer\_pool\_instances设置成一样。

InnoDB事务执行过程中，还会生成Undo日志。事务提交时，并不会立刻就清理Undo日志。Purge线程会在合适的时机回收Undo日志。参数innodb\_purge\_threads控制Purge线程的数量。

#### InnoDB数据文件

InnoDB Buffer Pool中的数据，最终会持久化到数据文件中。InnoDB使用IO线程来进行IO操作。参数innodb\_read\_io\_threads、innodb\_write\_io\_threads分别指定了读IO和写IO的线程数，默认值都为4，如果服务器上CPU核数多，可以适当增加这2个参数。

#### Redo Log Buffer

为了保障数据的持久化，修改Buffer Pool中的页面时，需要生成Redo日志。如果数据库或服务器异常崩溃，可以使用Redo日志来恢复数据。事务执行过程中，Redo日志会先写入到Redo Log Buffer中，Buffer的大小由参数innodb\_log\_buffer\_size控制。一般分配几十兆就可以，比如8.4中默认为64M。如果你的数据库并发写入量高，可适当把这个参数增加到几百兆。

事务提交时，需要将事务产生的Redo日志持久化到Redo文件中，这样才能保证数据不丢。参数innodb\_flush\_log\_at\_trx\_commit控制事务提交时，Redo日志的刷盘行为。设置为1时，每个事务提交时都会等待Redo日志刷盘完成，这是最安全的设置。但由于要等待Redo日志刷盘完成，性能上有一定的开销。这个参数设置为2时，事务提交时只会将Redo日志写到Redo文件中，然后每隔1秒刷新一次Redo文件，如果服务器异常崩溃，可能会导致部分数据丢失。

#### Redo日志

早期版本中，通过参数innodb\_log\_file\_size和innodb\_log\_files\_in\_group控制Redo日志文件的大小和数量。8.0.30后，新增了innodb\_redo\_log\_capacity参数，就不再需要单独设置innodb\_log\_file\_size和innodb\_log\_files\_in\_group了。Redo文件循环使用，随着数据库事务不停地执行，新的Redo日志最终会覆盖老的Redo日志。

![图片](https://static001.geekbang.org/resource/image/94/47/946a1fc95719d7b9999bb084eae13847.jpg?wh=858x374)

数据库崩溃恢复时，需要通过Redo日志来恢复数据，那么覆盖老的Redo文件会不会导致数据丢失呢？或者MySQL如何保证覆盖Redo文件不影响数据库恢复？其实只要保证覆盖Redo文件时，数据库的Checkpoint LSN比Redo文件最大的LSN号更大就行了。

```go
mysql> select file_id, start_lsn, end_lsn from innodb_redo_log_files;
+---------+------------+------------+
| file_id | start_lsn  | end_lsn    |
+---------+------------+------------+
|     656 | 2168369664 | 2171644416 |
+---------+------------+------------+

mysql> show global status like '%lsn%';
+-------------------------------------+------------+
| Variable_name                       | Value      |
+-------------------------------------+------------+
| Innodb_redo_log_checkpoint_lsn      | 2170307263 |
| Innodb_redo_log_current_lsn         | 2170307263 |
| Innodb_redo_log_flushed_to_disk_lsn | 2170307263 |
+-------------------------------------+------------+

```

如果innodb\_redo\_log\_capacity设置得太小，数据库写入量又比较大，那么覆盖Redo文件时，就可能需要等待数据库Checkpoint，这会严重影响数据库写入的性能。对于Buffer Pool比较大，写入频繁的数据库，需要把innodb\_redo\_log\_capacity设置得大一些，设置成几个G到几十G都是可以的。

下面以这个表格对InnoDB参数的设置做一个简单的总结。

![图片](https://static001.geekbang.org/resource/image/c7/94/c793b53a1yy146d5621b4b9f7b85fb94.jpg?wh=1578x1550)

### 其它参数设置

关于MySQL主备复制相关的参数，我们到后续的课程中再单独讨论。此外，sql\_mode也是MySQL中非常重要的一个参数。在生产环境中，修改这个参数可能会导致原先能运行的SQL直接报错，下一讲中我们会详细讨论sql\_mode参数的设置。

## 总结

这一讲中，我们一起学习了MySQL的参数设置机制。我建议将一个数据库实例的参数都配置在同一个参数文件中。修改参数时，在参数文件中添加注释，简要说明参数这么设置的原因。有可能的话，使用版本控制工具来管理参数文件。

MySQL只需要配置最基本的参数就能运行起来。但如果对性能和数据一致性有要求，就需要设置一些重要的参数，比如我们在这一讲中讨论到的资源限制参数、InnoDB的一些参数。我们很难给MySQL设置真正意义上最优的参数，而且在不同的业务场景下，最优的配置可能是不一样的。我的建议是将参数设置得差不多好就行了，将更多的时间花在业务优化上。

如果你的业务场景对性能有极致的要求，可以使用真实业务场景，对数据库性能进行测评，测试在不同的参数配置下，数据库的性能表现。

## 思考题

我们写SQL语句时，关键字一般不区分大小，不同的人可能有不同的习惯。对于库名、表名、列名，不同的数据库有不同的处理方法。比如Oracle中，表名默认不区分大小写。在MySQL中，根据操作系统的不同，表名就可能会区分大小写。

```go
mysql> show tables;
+----------------+
| Tables_in_db01 |
+----------------+
| Ta             |
| ta             |
+----------------+
2 rows in set (0.01 sec)

mysql> select * from ta;
Empty set (0.01 sec)

mysql> SELECT * From tA;
ERROR 1146 (42S02): Table 'db01.tA' doesn't exist

```

参数lower\_case\_table\_names可用来控制表名是否区分大小写。

```go
mysql> show variables like '%lower%';
+------------------------+-------+
| Variable_name          | Value |
+------------------------+-------+
| lower_case_file_system | OFF   |
| lower_case_table_names | 0     |
+------------------------+-------+

```

MySQL 8.0中，这个参数只能在数据库初始化之前设置，之后就不能再修改了，修改后数据库都无法启动。

```go
[ERROR] [MY-011087] [Server] Different lower_case_table_names settings for server ('1') and data dictionary ('0').
[ERROR] [MY-010020] [Server] Data Dictionary initialization failed.

```

你觉得这个参数应该怎样设置？原因是什么？

期待你的思考，欢迎在留言区中与我交流。如果今天的课程让你有所收获，也欢迎转发给有需要的朋友。我们下节课再见！