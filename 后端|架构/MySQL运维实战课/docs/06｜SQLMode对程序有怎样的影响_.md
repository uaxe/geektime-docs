你好，我是俊达。

SQL Mode是MySQL中比较特殊的一个概念，可以通过参数sql\_mode进行设置。设置SQL Mode会影响数据库对SQL的语法支持，也会影响数据写入时的校验规则。早期的MySQL使用非严格模式，这样有一些不符合SQL标准的语句在MySQL中也能执行，一些按SQL标准来说不合法的数据，也能写到表里面。

不过从MySQL 5.7开始，默认就开启了严格模式。这一讲中，我们一起来看看SQL Mode是怎么影响到SQL语句的，以及应该怎么设置SQL Mode。

## 非严格模式

非严格模式下，MySQL会允许你执行一些不符合SQL标准的语句。我们通过一些例子来说明这种情况。先创建一个测试表，写入一些数据。

```go
mysql> create table tab2(
    b int,
    c varchar(10),
    d varchar(30)
) engine=innodb;

Query OK, 0 rows affected (10.16 sec)

mysql> insert into tab2 values
    (10, 'AAA1', 'BBB1'),
    (20, 'AAA4', 'BBB4'),
    (10, 'AAA3', 'BBB3'),
    (20, 'AAA2', 'BBB2')

Query OK, 4 rows affected (0.56 sec)
Records: 4  Duplicates: 0  Warnings: 0

mysql> select * from tab2;
+------+------+------+
| b    | c    | d    |
+------+------+------+
|   10 | AAA1 | BBB1 |
|   20 | AAA4 | BBB4 |
|   10 | AAA3 | BBB3 |
|   20 | AAA2 | BBB2 |
+------+------+------+
4 rows in set (0.00 sec)

```

执行下面这个带了GROUP BY的语句时，你会发现执行会报错。因为按SQL标准语法，如果SQL带了GROUP BY，那么SELECT列表中的字段，要么也出现在GROUP BY的字段列表中，要么就加上聚合函数，比如avg、max、min等。

```go
mysql> select b,c,d from tab2 group by b;
ERROR 1055 (42000): Expression #2 of SELECT list is not in GROUP BY clause and contains nonaggregated column 'src_db.tab2.c' which is not functionally dependent on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by

```

但是在MySQL中，如果你把SQL Mode中的only\_full\_group\_by选项去掉，就可以正常执行上面这个SQL。从输出结果看，字段C和D的取值跟数据写入的顺序有关。

```go
mysql> set sql_mode='';
Query OK, 0 rows affected (0.00 sec)

mysql> select b, c, d from tab2 group by b;
+------+------+------+
| b    | c    | d    |
+------+------+------+
|   10 | AAA1 | BBB1 |
|   20 | AAA4 | BBB4 |
+------+------+------+

```

严格模式下，下面这两个SQL都会报错。第一个SQL是因为往int类型的字段中写入了非数字的字符，第二个SQL是因为写入的字符串长度超过了字段定义时允许的范围。

```go
mysql> insert into tab3(b,c,d) values('a', 'a', 'a');
ERROR 1366 (HY000): Incorrect integer value: 'a' for column 'b' at row 1

mysql> insert into tab3(b,c) values('100', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
ERROR 1406 (22001): Data too long for column 'c' at row 1

```

但是在非严格模式下，这两个SQL都能执行，虽然执行时会有Warning。

```go
mysql> delete from tab3;
Query OK, 4 rows affected (0.54 sec)

mysql> set sql_mode='';
Query OK, 0 rows affected (0.00 sec)

mysql> insert into tab3 values('a', 'a', 'a');
Query OK, 1 row affected, 1 warning (0.45 sec)

mysql> show warnings;
+---------+------+------------------------------------------------------+
| Level   | Code | Message                                              |
+---------+------+------------------------------------------------------+
| Warning | 1366 | Incorrect integer value: 'a' for column 'b' at row 1 |
+---------+------+------------------------------------------------------+
1 row in set (0.00 sec)

mysql> insert into tab3(b,c) values('100', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
Query OK, 1 row affected, 1 warning (0.70 sec)

mysql> show warnings;
+---------+------+----------------------------------------+
| Level   | Code | Message                                |
+---------+------+----------------------------------------+
| Warning | 1265 | Data truncated for column 'c' at row 1 |
+---------+------+----------------------------------------+
1 row in set (0.00 sec)

```

我们再来查看数据，第一个SQL插入的数据，非法的整数值被替换成了0。第二个SQL插入的数据，超出长度的字符串被截去了，留下了一个前缀。

```go
mysql> select * from tab3;
+------+------------+------+
| b    | c          | d    |
+------+------------+------+
|    0 | a          | a    |
|  100 | ABCDEFGHIJ | NULL |
+------+------------+------+
2 rows in set (0.01 sec)

```

在MySQL 5.6和更早版本中，默认使用非严格模式，上面这样的SQL都可以正常执行。如果你的应用中存在这些情况，然后由于某种原因SQL Mode切换成了严格模式，那么原先正常的应用程序，就可能无法正常运行了。

## SQL Mode的各种选项

SQL Mode有很多选项，MySQL 8.0中，sql\_mode的默认设置可以通过下面这个方法获取。

```go
mysql> set sql_mode=default;
Query OK, 0 rows affected (0.00 sec)

mysql> show variables like 'sql_mode'\G
*************************** 1. row ***************************
Variable_name: sql_mode
        Value: ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
1 row in set (0.01 sec)

```

这些选项中，ONLY\_FULL\_GROUP\_BY和STRICT\_TRANS\_TABLES我们已经遇到过了。此外，还有一些选项不在这个默认的设置中，后面我们也会分别进行介绍。

### ONLY\_FULL\_GROUP\_BY

前面的例子已经演示过ONLY\_FULL\_GROUP\_BY的效果了。设置ONLY\_FULL\_GROUP\_BY后，对有GROUP BY的SQL，SELECT的字段要么也出现GROUP BY中，要么使用聚合函数，否则SQL执行会报错。

我们可以对SQL进行改写，在GROUP BY之外的那些字段上使用ANY\_VALUE函数，这样SQL就可以正常执行了。

```go
mysql> set sql_mode='ONLY_FULL_GROUP_BY';
Query OK, 0 rows affected (0.00 sec)

mysql> select b,c,d from tab2 group by b;
ERROR 1055 (42000): Expression #2 of SELECT list is not in GROUP BY clause and contains nonaggregated column 'src_db.tab2.c' which is not functionally dependent on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by

mysql> select b, any_value(c) as c, any_value(d) as d from tab2 group by b;
+------+------+------+
| b    | c    | d    |
+------+------+------+
|   10 | AAA1 | BBB1 |
|   20 | AAA4 | BBB4 |
+------+------+------+
2 rows in set (0.00 sec)

```

### STRICT\_TRANS\_TABLES

设置STRICT\_TRANS\_TABLES后，在数据写入时，如果数据不符合字段定义，比如字符串超出长度，或者数值类型数据超出范围时，SQL会报错。如果不设置STRICT模式，会对异常数据进行截断处理，SQL会显示Warning，但不报错。

```go
mysql> create table t_strict(a tinyint, b tinyint unsigned, c decimal(6,2), d varchar(10));
Query OK, 0 rows affected (6.36 sec)

mysql> set sql_mode='strict_trans_tables';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_strict(a) values(512);
ERROR 1264 (22003): Out of range value for column 'a' at row 1

mysql> insert into t_strict(b) values(512);
ERROR 1264 (22003): Out of range value for column 'b' at row 1

mysql> insert into t_strict(c) values(1000000);
ERROR 1264 (22003): Out of range value for column 'c' at row 1

mysql> insert into t_strict(d) values('0123456789ABCDEF');
ERROR 1406 (22001): Data too long for column 'd' at row 1

```

去掉STRICT\_TRANS\_TABLES后，虽然能写入数据，但是数据被截断了，和应用本来想写入的数据有很大的差异。

```go
mysql> set sql_mode='';
Query OK, 0 rows affected (0.00 sec)

mysql> insert into t_strict(a,b,c,d) values(512, 512, 1000000, '0123456789ABCDEF');
Query OK, 1 row affected, 4 warnings (0.04 sec)

mysql> select * from t_strict;
+------+------+---------+------------+
| a    | b    | c       | d          |
+------+------+---------+------------+
|  127 |  255 | 9999.99 | 0123456789 |
+------+------+---------+------------+
1 row in set (0.00 sec)

```

对不支持事务的存储引擎，比如MyISAM，STRICT\_TRANS\_TABLES的作用就比较复杂了。如果使用了批量INSERT，也就是同时INSERT了多行记录，那么当第一行记录中有数据和字段定义不符合时，SQL会报错，如果第一行数据没问题，但是后续的记录有问题，那么SQL能执行成功，但是会对超出范围的数据进行截断处理。下面这个例子中的第二个INSERT语句，插入了两行记录，第二行记录的数据被截断了。

```go
mysql> create table t_strict_myisam(a tinyint, b tinyint unsigned, c decimal(6,2), d varchar(10)) engine=myisam;
Query OK, 0 rows affected (0.19 sec)

mysql> set sql_mode='strict_trans_tables';
Query OK, 0 rows affected, 1 warning (0.01 sec)

mysql> insert into t_strict_myisam values(512, 512, 1000000, '0123456789ABCDEF');
ERROR 1264 (22003): Out of range value for column 'a' at row 1

mysql> insert into t_strict_myisam values(100, 200, 9999, '0123456789'), (512, 512, 1000000, '0123456789ABCDEF');
Query OK, 2 rows affected, 4 warnings (0.01 sec)
Records: 2  Duplicates: 0  Warnings: 4

mysql> select * from t_strict_myisam;
+------+------+---------+------------+
| a    | b    | c       | d          |
+------+------+---------+------------+
|  100 |  200 | 9999.00 | 0123456789 |
|  127 |  255 | 9999.99 | 0123456789 |
+------+------+---------+------------+
2 rows in set (0.00 sec)

```

### STRICT\_ALL\_TABLES

STRICT\_ALL\_TABLES对所有存储引擎都生效。对于MyISAM这类不支持事务的存储引擎，使用批量INSERT时，如果SQL中存在超出范围的值，SQL执行就会报错，但是对于已经写入的数据，无法回滚。下面这个例子就演示了这种情况。

例子中INSERT语句的第一行数据是合法的，第二行数据超出了范围，SQL执行时，第一行数据写入成功，第二行数据无法写入，因此SQL就报错了，第三行数据虽然没问题，但是也不会再写入了。虽然SQL失败了，但是第一行数据已经写入了，而MyISAM不支持事务，无法回滚这一行记录。

```go
mysql> create table t_strict_all(a tinyint, b tinyint unsigned, c decimal(6,2), d varchar(10)) engine=myisam;
Query OK, 0 rows affected (0.40 sec)

mysql> set  sql_mode='strict_all_tables';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_strict_all values(100, 200, 9999, '0123456789'), (512, 512, 1000000, '0123456789ABCDEF'), (10, 20, 1000, 'ABCD');
ERROR 1264 (22003): Out of range value for column 'a' at row 2

mysql> select * from t_strict_all;
+------+------+---------+------------+
| a    | b    | c       | d          |
+------+------+---------+------------+
|  100 |  200 | 9999.00 | 0123456789 |
+------+------+---------+------------+

```

### NO\_ZERO\_DATE和NO\_ZERO\_IN\_DATE

设置STRICT\_TRANS\_TABLES和STRICT\_ALL\_TABLES后，表中无法写入非法的日期值。

```go
mysql> create table t_date(a date, b datetime, c timestamp);
Query OK, 0 rows affected (5.47 sec)

mysql> set sql_mode='strict_trans_tables';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_date(a) values('2024-02-30');
ERROR 1292 (22007): Incorrect date value: '2024-02-30' for column 'a' at row 1

mysql> insert into t_date(b) values('2024-02-30 01:23:45');
ERROR 1292 (22007): Incorrect datetime value: '2024-02-30 01:23:45' for column 'b' at row 1

mysql> insert into t_date(c) values('2024-02-30 01:23:45');
ERROR 1292 (22007): Incorrect datetime value: '2024-02-30 01:23:45' for column 'c' at row 1

```

但是却可以往date和datetime类型的字段中写入日期为0或年月日中存在0的数据。

```go
mysql> set sql_mode='';
Query OK, 0 rows affected (0.00 sec)

mysql> insert into t_date values('0000-00-00', '0000-01-00 01:23:45', '1970-01-02 01:23:45');
Query OK, 1 row affected (0.98 sec)

mysql> select * from t_date;
+------------+---------------------+---------------------+
| a          | b                   | c                   |
+------------+---------------------+---------------------+
| 0000-00-00 | 0000-01-00 01:23:45 | 1970-01-02 01:23:45 |
+------------+---------------------+---------------------+

```

如果要阻止往数据库中写入年月日为0的数据，就需要设置NO\_ZERO\_DATE和NO\_ZERO\_IN\_DATE。

```go
mysql> set sql_mode='no_zero_date,no_zero_in_date,strict_trans_tables';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_date(a) values('0000-00-00');
ERROR 1292 (22007): Incorrect date value: '0000-00-00' for column 'a' at row 1

mysql> insert into t_date(a) values('0000-01-00');
ERROR 1292 (22007): Incorrect date value: '0000-01-00' for column 'a' at row 1

mysql> insert into t_date(b) values('0001-00-00 01:23:45');
ERROR 1292 (22007): Incorrect datetime value: '0001-00-00 01:23:45' for column 'b' at row 1

```

需要注意的是，NO\_ZERO\_DATE和NO\_ZERO\_IN\_DATE需要跟STRICT\_TRANS\_TABLES一起设置，如果只是设置了NO\_ZERO\_DATE和NO\_ZERO\_IN\_DATE，还是能往数据库中写入日期为0或年月日中有0的数据。

```go
mysql> delete from t_date;
Query OK, 1 row affected (0.85 sec)

mysql> set sql_mode='no_zero_date,no_zero_in_date';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_date(a,b,c) values('0000-00-00', '0000-01-00 01:23:45', '1970-01-02 01:23:45');
Query OK, 1 row affected, 2 warnings (0.83 sec)

mysql> show warnings;
+---------+------+--------------------------------------------+
| Level   | Code | Message                                    |
+---------+------+--------------------------------------------+
| Warning | 1264 | Out of range value for column 'a' at row 1 |
| Warning | 1264 | Out of range value for column 'b' at row 1 |
+---------+------+--------------------------------------------+
2 rows in set (0.00 sec)

mysql> select * from t_date;
+------------+---------------------+---------------------+
| a          | b                   | c                   |
+------------+---------------------+---------------------+
| 0000-00-00 | 0000-00-00 00:00:00 | 1970-01-02 01:23:45 |
+------------+---------------------+---------------------+
1 row in set (0.00 sec)

```

### ALLOW\_INVALID\_DATES

MySQL中默认无法写入不合法的日期。不开启严格模式时，非法的日期值都会被转换成0000-00-00。

```go
mysql> create table t_date2(a date, b datetime, c timestamp);
Query OK, 0 rows affected (5.15 sec)

mysql> set sql_mode='';
Query OK, 0 rows affected (0.00 sec)

mysql> insert into t_date2 values('2024-02-30', '2024-02-30 01:23:45', '2024-02-30 01:23:45');
Query OK, 1 row affected, 3 warnings (0.26 sec)

mysql> select * from t_date2;
+------------+---------------------+---------------------+
| a          | b                   | c                   |
+------------+---------------------+---------------------+
| 0000-00-00 | 0000-00-00 00:00:00 | 0000-00-00 00:00:00 |
+------------+---------------------+---------------------+

```

但如果设置了ALLOW\_INVALID\_DATES这个SQL Mode，就可以在date和datetime类型中写入不存在的日期值了。注意，即使设置了ALLOW\_INVALID\_DATES，timestamp类型的字段中还是无法写入这些日期值。

```go
mysql> insert into t_date2 values('2024-02-30', '2024-02-30 01:23:45', '2024-02-30 01:23:45');
Query OK, 1 row affected, 1 warning (1.53 sec)

mysql> show warnings;
+---------+------+--------------------------------------------+
| Level   | Code | Message                                    |
+---------+------+--------------------------------------------+
| Warning | 1264 | Out of range value for column 'c' at row 1 |
+---------+------+--------------------------------------------+

mysql> select * from t_date2;
+------------+---------------------+---------------------+
| a          | b                   | c                   |
+------------+---------------------+---------------------+
| 2024-02-30 | 2024-02-30 01:23:45 | 0000-00-00 00:00:00 |
+------------+---------------------+---------------------+

```

### ERROR\_FOR\_DIVISION\_BY\_ZERO

我们知道，从数学的意义上看，除数不能为0。在MySQL中，如果除数为0，会出现什么结果呢？这其实和SQL Mode有关系。如果SQL Mode中同时设置了ERROR\_FOR\_DIVISION\_BY\_ZERO和STRICT\_TRANS\_TABLES，那么当除数为0时，SQL会报错。否则除数为0时，结果为NULL。

```go
mysql> create table t_n(a int);
Query OK, 0 rows affected (4.25 sec)

mysql> set sql_mode='strict_trans_tables';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_n values(1/0);
Query OK, 1 row affected (2.10 sec)

mysql> set sql_mode='ERROR_FOR_DIVISION_BY_ZERO';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_n values(1/0);
Query OK, 1 row affected, 1 warning (0.83 sec)

mysql> show warnings;
+---------+------+---------------+
| Level   | Code | Message       |
+---------+------+---------------+
| Warning | 1365 | Division by 0 |
+---------+------+---------------+

mysql> select * from t_n;
+------+
| a    |
+------+
| NULL |
| NULL |
+------+
2 rows in set (0.01 sec)

```

同时设置ERROR\_FOR\_DIVISION\_BY\_ZERO和STRICT\_TRANS\_TABLES后，如果除数为0，SQL会报错。

```go
mysql>  set sql_mode='ERROR_FOR_DIVISION_BY_ZERO,strict_trans_tables';
Query OK, 0 rows affected, 1 warning (0.00 sec)

mysql> insert into t_n values(1/0);
ERROR 1365 (22012): Division by 0

```

### NO\_BACKSLASH\_ESCAPES

在MySQL中，反斜杠“\\”是一个转义符，有特殊的含义。下面这个例子中，本来我们想写入一个Windows下的文件路径，但是查询数据时，发现路径分隔符“\\”不见了。

```go
mysql> create table t_char(a varchar(100));
Query OK, 0 rows affected (3.23 sec)

mysql> set sql_mode=default;
Query OK, 0 rows affected (0.00 sec)

mysql> insert into t_char values('C:\Downloads\File');
Query OK, 1 row affected (0.80 sec)

mysql> select * from t_char;
+-----------------+
| a               |
+-----------------+
| C:DownloadsFile |
+-----------------+
1 row in set (0.00 sec)

```

这是因为在MySQL中“\\”是一个转义符，如果你想写入“\\”这个符号，需要对它进行转义。

```go
mysql> delete from t_char;
Query OK, 1 row affected (1.50 sec)

mysql> insert into t_char values('C:\\Downloads\\File');
Query OK, 1 row affected (0.89 sec)

mysql> select * from t_char;
+-------------------+
| a                 |
+-------------------+
| C:\Downloads\File |
+-------------------+
1 row in set (0.00 sec)

```

但是在别的数据库中，符号“\\”可能没有任何特殊含义。如果你需要将数据从别的数据库迁移到MySQL中，需要对数据进行转换。

其实MySQL中可以通过SQL Mode来进行控制，设置NO\_BACKSLASH\_ESCAPES选项后，反斜杠“\\”就变成一个普通的字符了，没有特殊含义。所以如果你需要从别的数据库迁移到MySQL，设置NO\_BACKSLASH\_ESCAPES可能会帮你减少一些麻烦。

```go
mysql> set sql_mode='NO_BACKSLASH_ESCAPES';
Query OK, 0 rows affected (0.00 sec)

mysql> delete from t_char;
Query OK, 1 row affected (0.32 sec)

mysql>  insert into t_char values('C:\Downloads\File');
Query OK, 1 row affected (1.18 sec)

mysql> select * from t_char;
+-------------------+
| a                 |
+-------------------+
| C:\Downloads\File |
+-------------------+
1 row in set (0.00 sec)

```

### ANSI\_QUOTES

在MySQL中，字符串常量可以使用单引号或双引号来引用。

```go
mysql> set sql_mode=default;
Query OK, 0 rows affected (0.00 sec)

mysql> insert into t_quote values("Let's go");
Query OK, 1 row affected (1.41 sec)

mysql> insert into t_quote values('String s = "Helloworld"');
Query OK, 1 row affected (1.79 sec)

mysql> select * from t_quote;
+-------------------------+
| a                       |
+-------------------------+
| Let's go                |
| String s = "Helloworld" |
+-------------------------+

```

但是在其他数据库中，双引号用来引用标识符，和在MySQL中的反引号“\`”的作用类似。比如下面这个例子中，order是MySQL中的一个关键词，不能用作表名，但是加上反引号之后就可以了。

```go
mysql> create table order(a int);
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'order(a int)' at line 1

mysql> create table `order`(a int);
Query OK, 0 rows affected (8.92 sec)

mysql> select * from `order`;
Empty set (0.00 sec)

```

在SQL Mode中设置ANSI\_QUOTES选项可以改变双引号的作用。设置ANSI\_QUOTES，双引号不再是用来引用字符串常量，而是用来引用标识符。

```go
mysql> set sql_mode='ANSI_QUOTES';
Query OK, 0 rows affected (0.00 sec)

mysql> select * from "order";
Empty set (0.00 sec)

mysql> insert into t_quote values ("some data");
ERROR 1054 (42S22): Unknown column 'some data' in 'field list'

```

### NO\_ENGINE\_SUBSTITUTION

MySQL支持多种存储引擎，存储引擎可以用插件的方式动态加载。在编译MySQL时，也可以通过cmake选项指定是否要将某个存储引擎编译出来。我们在建表的时候可以指定使用哪个存储引擎。如果指定的存储引擎不存在，那么MySQL可以将引擎替换为默认的存储引擎。在下面这个例子中，我们想创建一个federated表，但是我们的环境中没有federated存储引擎，因此存储引擎被改成了InnoDB。

```go
mysql> set sql_mode='';
Query OK, 0 rows affected (0.00 sec)

mysql> create table t_engine(a int) engine=federated;
Query OK, 0 rows affected, 2 warnings (8.95 sec)

mysql> show warnings;
+---------+------+--------------------------------------------------+
| Level   | Code | Message                                          |
+---------+------+--------------------------------------------------+
| Warning | 1286 | Unknown storage engine 'federated'               |
| Warning | 1266 | Using storage engine InnoDB for table 't_engine' |
+---------+------+--------------------------------------------------+

mysql> show create table t_engine\G
*************************** 1. row ***************************
       Table: t_engine
Create Table: CREATE TABLE `t_engine` (
  `a` int DEFAULT NULL
) ENGINE=InnoDB
1 row in set (0.00 sec)

```

如果SQL Mode中开启NO\_ENGINE\_SUBSTITUTION选项，建表时如果指定的存储引擎不可用或不存在，SQL就会报错。

```go
mysql> set sql_mode='NO_ENGINE_SUBSTITUTION';
Query OK, 0 rows affected (0.00 sec)

mysql> create table t_engine2(a int) engine=federated;
ERROR 1286 (42000): Unknown storage engine 'federated'

```

### PIPES\_AS\_CONCAT

在MySQL中，管道符“\|\|”相当于OR，这可能和别的数据库不一样。比如在Oracle中，经常使用管道符连接字符串。

```go
mysql> set sql_mode=default;
Query OK, 0 rows affected (0.00 sec)

mysql> select 'a' || 'b';
+------------+
| 'a' || 'b' |
+------------+
|          0 |
+------------+
1 row in set, 3 warnings (0.00 sec)

```

SQL Mode中设置PIPES\_AS\_CONCAT选项后，管道符就变成了字符串连接符。

```go
mysql> set sql_mode='pipes_as_concat';
Query OK, 0 rows affected (0.00 sec)

mysql> select 'a' || 'b';
+------------+
| 'a' || 'b' |
+------------+
| ab         |
+------------+
1 row in set (0.00 sec)

```

### REAL\_AS\_FLOAT

设置REAL\_AS\_FLOAT后，MySQL会将REAL类型映射为Float类型。不设置REAL\_AS\_FLOAT的话，REAL类型映射为Double类型。

### IGNORE\_SPACE

MySQL中，函数和参数列表之间默认是不允许加空格的。比如下面这个例子中，函数count和括号之间加了几个空格，语句就无法执行了。

```go
mysql> select count  (*) from information_schema.tables;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '*) from information_schema.tables' at line 1

mysql> select count(*) from information_schema.tables;
+----------+
| count(*) |
+----------+
|      438 |
+----------+
1 row in set (2.56 sec)

```

这种行为有时候可能比较讨厌。你可以在SQL Mode中加上IGNORE\_SPACE选项，这样函数名之后有空格也不影响SQL的正确执行。

```go
mysql> set sql_mode='ignore_space';
Query OK, 0 rows affected (0.00 sec)

mysql> select count  (*) from information_schema.tables;
+------------+
| count  (*) |
+------------+
|        438 |
+------------+
1 row in set (0.06 sec)

```

### ANSI

ANSI是一个组合的SQL Mode，设置ANSI相当于同时设置REAL\_AS\_FLOAT、PIPES\_AS\_CONCAT、ANSI\_QUOTES、IGNORE\_SPACE和ONLY\_FULL\_GROUP\_BY这几个选项。设置ANSI后，MySQL的语法支持和标准SQL更接近。

### TRADITIONAL

TRADITIONAL也是一个组合的SQL Mode，设置TRADITIONAL相当于同时设置STRICT\_TRANS\_TABLES、STRICT\_ALL\_TABLES、NO\_ZERO\_IN\_DATE、NO\_ZERO\_DATE、ERROR\_FOR\_DIVISION\_BY\_ZERO和NO\_ENGINE\_SUBSTITUTION这几个选项。

## 如何设置SQL Mode？

SQL Mode有这么多的选项，那么我们平时应该怎么设置呢？大部分情况下，我建议使用默认的严格模式设置，也就是设置上ONLY\_FULL\_GROUP\_BY、STRICT\_TRANS\_TABLES、NO\_ZERO\_IN\_DATE、NO\_ZERO\_DATE、ERROR\_FOR\_DIVISION\_BY\_ZERO和NO\_ENGINE\_SUBSTITUTION这几个选项，这可以避免往表中写入意外的错误数据。尽量在所有的环境中将SQL Mode设置成一样的，避免因为SQL Mode设置不一样引起一些不必要的麻烦。

如果你是从别的数据库迁移到MySQL，一些SQL可能和MySQL的默认模式不兼容，比如使用管道符“\|\|”连接字符串，使用引号“"”引用标识符，如果你可以修改SQL，我的建议是将SQL按MySQL的方式进行修改。如果实在是无法修改SQL，或者修改SQL的成本太高了，再考虑设置某些SQL Mode选项来解决。

MySQL数据库从低版本升级或迁移到高版本时，也需要全面测试应用程序。MySQL 5.7开始默认开启严格模式，避免由于SQL Mode默认值的变化而影响程序的正常运行。

下面这个表格对一些SQL Mode的作用做了简单总结，你可以参考。

![图片](https://static001.geekbang.org/resource/image/2c/ba/2c2193d813bea7aa6445a7795d9900ba.png?wh=1740x1496)

## 总结时刻

设置SQL\_MODE可能会使原先能执行的SQL无法执行，也可能影响数据写入操作，因此在生产环境修改这个参数前，需要对应用进行完整的测试验证。

如果你进行了数据库迁移或升级，新环境数据库sql\_mode和原先的设置不一样，也可能引起应用程序出错。因此需要注意迁移或升级前后sql\_mode的设置。MySQL 5.7开始，sql\_mode的默认设置跟之前的版本相比，有很大的改动，如果你是从更早的版本升级过来，需要特别注意。

## 思考题

MySQL的备库复制中断了，查看错误信息，发现是有一个建表的语句报错了。

```go
               Last_SQL_Error: Coordinator stopped because there were error(s) in the worker(s). The most recent failure being: Worker 1 failed executing transaction 'c1a67221-f9fc-11ed-bffd-fa8338b09400:106' at master log binlog.000020, end_log_pos 4203259. See error log and/or performance_schema.replication_applier_status_by_worker table for more details about this failure or others, if any.
  Replicate_Ignore_Server_Ids:

```

```go
mysql> select * from performance_schema.replication_applier_status_by_worker\G
*************************** 1. row ***************************
                                           CHANNEL_NAME:
                                              WORKER_ID: 1
                                              THREAD_ID: NULL
                                          SERVICE_STATE: OFF
                                      LAST_ERROR_NUMBER: 1118
                                     LAST_ERROR_MESSAGE: Worker 1 failed executing transaction 'c1a67221-f9fc-11ed-bffd-fa8338b09400:106' at master log binlog.000020, end_log_pos 4203259; Error 'Row size too large (> 8126). Changing some columns to TEXT or BLOB or using ROW_FORMAT=DYNAMIC or ROW_FORMAT=COMPRESSED may help. In current row format, BLOB prefix of 768 bytes is stored inline.' on query. Default database: 'repl'. Query: 'create table t_inno1(
       c01 varchar(768),
       c02 varchar(768),
       c03 varchar(768),
       c04 varchar(768),
       c05 varchar(768),
       c06 varchar(768),
       c07 varchar(768),
       c08 varchar(768),
       c09 varchar(768),
       c10 varchar(768),
       c11 varchar(398)
    ) engine=innodb row_format=compact charset latin1'

```

但是到主库上查看后，发现这个表创建成功了。

```go
mysql >show create table t_inno1\G
*************************** 1. row ***************************
       Table: t_inno1
Create Table: CREATE TABLE `t_inno1` (
  `c01` varchar(768) DEFAULT NULL,
  `c02` varchar(768) DEFAULT NULL,
  `c03` varchar(768) DEFAULT NULL,
  `c04` varchar(768) DEFAULT NULL,
  `c05` varchar(768) DEFAULT NULL,
  `c06` varchar(768) DEFAULT NULL,
  `c07` varchar(768) DEFAULT NULL,
  `c08` varchar(768) DEFAULT NULL,
  `c09` varchar(768) DEFAULT NULL,
  `c10` varchar(768) DEFAULT NULL,
  `c11` varchar(398) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT
1 row in set (0.00 sec)

```

为什么会出现这种情况呢？

期待你的思考，欢迎在留言区中与我交流。如果今天的课程让你有所收获，也欢迎转发给有需要的朋友。我们下节课再见！