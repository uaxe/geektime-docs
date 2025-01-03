接上一讲

### POSSIBLE\_KEYS

possible\_keys列显示查询单元能使用range、ref等访问路径访问的索引。执行计划最终选择的索引在keys列显示。是否使用索引，以及使用哪个索引，取决于优化器对各种访问方式的成本评估，还跟表连接的顺序和连接算法也有关系。

下面这个例子中，t1表的possible\_keys有索引idx\_abc，但是当t1表作为驱动表时，就无法使用索引idx\_abc。

```plain
mysql> explain select * from tab t1, tab t2 where t1.a = t2.a and t1.b = t2.b;

+----+-------------+-------+------+---------------+---------+---------+-------------------+------+----------+-------+
| id | select_type | table | type | possible_keys | key     | key_len | ref               | rows | filtered | Extra |
+----+-------------+-------+------+---------------+---------+---------+-------------------+------+----------+-------+
|  1 | SIMPLE      | t1    | ALL  | idx_abc       | NULL    | NULL    | NULL              | 9913 |   100.00 | NULL  |
|  1 | SIMPLE      | t2    | ref  | idx_abc       | idx_abc | 8       | rep.t1.a,rep.t1.b |    1 |   100.00 | NULL  |
+----+-------------+-------+------+---------------+---------+---------+-------------------+------+----------+-------+

```

### KEY

key列显示执行计划实际使用的索引。如果key列为NULL，则说明查询单元没有使用索引。对于index\_merge访问路径，key列中会显示多个索引。

### KEY\_LEN

key\_len列显示执行计划使用到的索引列的总长度。根据key\_len可以推算出执行计划使用到了索引中的哪几个字段。key\_len根据索引字段的类型和字段是否为空计算得到。对于字符类型如varchar、char，key\_len为字符数乘以单个字符的最大可能字节数。对于每个可变长类型如varchar，key\_len额外加2。对于每个可以为空的字段，key\_len额外加1。

```plain
 create table t_k(
     a varchar(20),
     b char(20),
     key idx_a(a,b)
) engine=innodb charset=utf8mb4;

mysql> explain select * from t_k where  a='x';
+----+-------------+-------+------+---------------+-------+---------+-------+------+----------+-------------+
| id | select_type | table | type | possible_keys | key   | key_len | ref   | rows | filtered | Extra       |
+----+-------------+-------+------+---------------+-------+---------+-------+------+----------+-------------+
|  1 | SIMPLE      | t_k   | ref  | idx_a         | idx_a | 83      | const |    1 |   100.00 | Using index |
+----+-------------+-------+------+---------------+-------+---------+-------+------+----------+-------------+

mysql> explain select * from t_k where  a='x' and b='x';

+----+-------------+-------+------+---------------+-------+---------+-------------+------+----------+--------------------------+
| id | select_type | table | type | possible_keys | key   | key_len | ref         | rows | filtered | Extra                    |
+----+-------------+-------+------+---------------+-------+---------+-------------+------+----------+--------------------------+
|  1 | SIMPLE      | t_k   | ref  | idx_a         | idx_a | 164     | const,const |    1 |   100.00 | Using where; Using index |
+----+-------------+-------+------+---------------+-------+---------+-------------+------+----------+--------------------------+

```

上面这个例子中，SQL 1使用索引中的字段a，字段A的类型为varchar(20)，字符集为utf8mb4，key\_len为20 \* 4 + 2 + 1 = 83。

SQL 2使用到了字段A和B，字段A的key\_len为83，字段B的key\_len为20 \* 4 + 1 = 81，整体Key\_len为字段A和字段B相加164。

### REF

ref列显示用来进行索引查找的值，ref的取值可能是以下几种情况：

- const：使用常量匹配

- db.tab.c：使用驱动表的某个字段匹配

- func：使用某个函数的计算结果匹配。可以在执行explain后使用show warnings命令查看转换后的SQL。


### ROWS

查询单元需要访问的记录数。对于InnoDB引擎，这里的记录数是一个预估的行数，跟实际执行过程中真实访问的记录数可能会有一些差异。对于全表扫描和全索引扫描，这里的行数从统计信息中获取。对于索引访问（type为ref或range），rows通过访问索引评估得到，或通过索引的统计信息计算得到。对应派生表，rows通过一些规则评估得到。

一般来说，rows越大，说明查询单元需要访问的记录数越多，执行时间越长。

### FILTERED

filtered字段单位为百分比，取值范围为0-100，表示经过where子句中的条件过滤后，满足条件的记录数相对于rows列中显示的行数所占的百分比。使用公示rows \* filtered / 100可以得到优化器预估的查询单元返回的记录数。如果当前的查询单元作为驱动表，那么这里的记录数还决定了被驱动的查询单元需要执行多次。

优化器中有一系列固定的规则来计算filtered的取值。你可以在分析表（analyze table）的时候给字段添加直方图，使优化器能更精确地计算filtered。参数optimizer\_switch中的选项condition\_fanout\_filter用来控制是否开启条件过滤。

### EXTRA

Extra列中显示了执行计划额外的一些重要信息。

- using where

如果访问路径为ALL或index，Extra中没用using where，说明查询需要读取整个表或索引的数据。

- Range checked for each record (index map: 0x n)

如果Extra中出现了“Range checked for each record”，那么查询的性能很可能不太好。这里index map是索引编号的位图信息。

```plain
mysql> explain select * from tab a, tab b where  a.id > b.id and a.c > b.c;

+----+-------------+-------+------+---------------+------+---------+------+------+----------+------------------------------------------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra                                          |
+----+-------------+-------+------+---------------+------+---------+------+------+----------+------------------------------------------------+
|  1 | SIMPLE      | a     | ALL  | PRIMARY       | NULL | NULL    | NULL | 9913 |   100.00 | NULL                                           |
|  1 | SIMPLE      | b     | ALL  | PRIMARY       | NULL | NULL    | NULL | 9913 |    11.11 | Range checked for each record (index map: 0x1) |
+----+-------------+-------+------+---------------+------+---------+------+------+----------+------------------------------------------------+

```

- Using index; Using temporary

Extra中出现Using temporary，说明用到了临时表。

```plain
mysql> explain select b,a,count(*) from  tab group by b,a;

+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+------------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref  | rows | filtered | Extra                        |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+------------------------------+
|  1 | SIMPLE      | tab   | index | idx_abc       | idx_abc | 12      | NULL | 9913 |   100.00 | Using index; Using temporary |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+------------------------------+

```

- Using index for skip scan

查询条件没有传入索引的前缀字段，又用到了覆盖索引时，MySQL可能会使用skip scan。如果前缀列的唯一值很低，skip scan也可能会有不错的性能。

```plain
mysql> explain select c from tab where b=1;

+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+----------------------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref  | rows | filtered | Extra                                  |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+----------------------------------------+
|  1 | SIMPLE      | tab   | range | idx_abc       | idx_abc | 8       | NULL |  991 |   100.00 | Using where; Using index for skip scan |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+----------------------------------------+

```

- Using index

使用了覆盖索引，也就是查询中所有列都包含在索引中。

- no matching row in const table

说明表里面不存在满足条件的记录。

```plain
mysql> explain select * from tab where id = 12345;

+----+-------------+-------------+---------------+------+---------+------+------+----------+--------------------------------+
| id | select_type | table  type | possible_keys | key  | key_len | ref  | rows | filtered | Extra                          |
+----+-------------+-------------+---------------+------+---------+------+------+----------+--------------------------------+
|  1 | SIMPLE      | NULL   NULL | NULL          | NULL | NULL    | NULL | NULL |     NULL | no matching row in const table |
+----+-------------+-------------+---------------+------+---------+------+------+----------+--------------------------------+

```

- Using index for group-by

```plain
mysql> explain select a, min(b) from tab group by a;

+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+--------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref  | rows | filtered | Extra                    |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+--------------------------+
|  1 | SIMPLE      | tab   | range | idx_abc       | idx_abc | 4       | NULL |    4 |   100.00 | Using index for group-by |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+--------------------------+

```

- LooseScan

LooseScan，以及FirstMatch、Start temporary、End temporary，都是子查询自动改写为表连接后的执行方式，我们在后续的子查询这一讲中再具体介绍。

```plain
mysql> set optimizer_switch='materialization=off';
Query OK, 0 rows affected (0.01 sec)

mysql> explain select * from tab ta
  where a=1 and c in (select a from tab tb);

+----+-------------+-------+-------+---------------+---------+---------+-------+------+----------+------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref   | rows | filtered | Extra                  |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+----------+------------------------+
|  1 | SIMPLE      | tb    | index | idx_abc       | idx_abc | 12      | NULL  | 9913 |     0.03 | Using index; LooseScan |
|  1 | SIMPLE      | ta    | ref   | idx_abc       | idx_abc | 4       | const | 3333 |    10.00 | Using index condition  |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+----------+------------------------+

```

- FirstMatch(ta)

```plain
mysql> set optimizer_switch='materialization=off';
Query OK, 0 rows affected (0.01 sec)

mysql> explain select * from tab ta where a=1 and c in (select c from tab tb);
+----+-------------+-------+-------+---------------+---------+---------+-------+------+----------+-------------------------------------------------------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref   | rows | filtered | Extra                                                                   |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+----------+-------------------------------------------------------------------------+
|  1 | SIMPLE      | ta    | ref   | idx_abc       | idx_abc | 4       | const | 3333 |   100.00 | NULL                                                                    |
|  1 | SIMPLE      | tb    | index | NULL          | idx_abc | 12      | NULL  | 9913 |    10.00 | Using where; Using index; FirstMatch(ta); Using join buffer (hash join) |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+----------+-------------------------------------------------------------------------+

```

- Start temporary, End temporary

```plain
mysql> set optimizer_switch='materialization=off';
Query OK, 0 rows affected (0.01 sec)

mysql> explain select * from tab ta where id in (select b from tab tb where b < 10);

+----+-------------+-------+--------+---------------+---------+---------+----------+------+----------+-------------------------------------------+
| id | select_type | table | type   | possible_keys | key     | key_len | ref      | rows | filtered | Extra                                     |
+----+-------------+-------+--------+---------------+---------+---------+----------+------+----------+-------------------------------------------+
|  1 | SIMPLE      | tb    | index  | NULL          | idx_abc | 12      | NULL     | 9913 |    33.33 | Using where; Using index; Start temporary |
|  1 | SIMPLE      | ta    | eq_ref | PRIMARY       | PRIMARY | 4       | rep.tb.b |    1 |   100.00 | End temporary                             |
+----+-------------+-------+--------+---------------+---------+---------+----------+------+----------+-------------------------------------------+

```

- Using index condition

使用到了索引下推条件。

```plain
mysql> explain select * from tab where a=1 and c=1;

+----+-------------+-------+------+---------------+---------+---------+-------+------+----------+-----------------------+
| id | select_type | table | type | possible_keys | key     | key_len | ref   | rows | filtered | Extra                 |
+----+-------------+-------+------+---------------+---------+---------+-------+------+----------+-----------------------+
|  1 | SIMPLE      | tab   | ref  | idx_abc       | idx_abc | 4       | const | 3333 |    10.00 | Using index condition |
+----+-------------+-------+------+---------------+---------+---------+-------+------+----------+-----------------------+

```

- Using filesort

说明查询需要排序。

```plain
mysql> explain select * from tab order by b;

+----+-------------+-------+------+---------------+------+---------+------+------+----------+----------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra          |
+----+-------------+-------+------+---------------+------+---------+------+------+----------+----------------+
|  1 | SIMPLE      | tab   | ALL  | NULL          | NULL | NULL    | NULL | 9913 |   100.00 | Using filesort |
+----+-------------+-------+------+---------------+------+---------+------+------+----------+----------------+

```

- Using join buffer (hash join)

被驱动表缺少合适的索引时，MySQL会考虑使用Hash连接算法。

```plain
mysql> explain select * from tab t1, tab t2 where t1.a = 1 and t1.c=t2.c;

+----+-------------+-------+------+---------------+---------+---------+-------+------+----------+--------------------------------------------+
| id | select_type | table | type | possible_keys | key     | key_len | ref   | rows | filtered | Extra                                      |
+----+-------------+-------+------+---------------+---------+---------+-------+------+----------+--------------------------------------------+
|  1 | SIMPLE      | t1    | ref  | idx_abc       | idx_abc | 4       | const | 3333 |   100.00 | NULL                                       |
|  1 | SIMPLE      | t2    | ALL  | NULL          | NULL    | NULL    | NULL  | 9913 |    10.00 | Using where; Using join buffer (hash join) |
+----+-------------+-------+------+---------------+---------+---------+-------+------+----------+--------------------------------------------+

```

- Using join buffer (Batched Key Access)

表关联时，使用了BKA优化。和MRR类似，BKA也是为了减少查询的随机IO的数量。

```plain
mysql> explain select /*+ BKA(tb) */ *
  from tab ta, tab tb where ta.a = tb.a;

+----+-------------+-------+------+---------------+---------+---------+----------+------+----------+----------------------------------------+
| id | select_type | table | type | possible_keys | key     | key_len | ref      | rows | filtered | Extra                                  |
+----+-------------+-------+------+---------------+---------+---------+----------+------+----------+----------------------------------------+
|  1 | SIMPLE      | ta    | ALL  | idx_abc       | NULL    | NULL    | NULL     | 9913 |   100.00 | NULL                                   |
|  1 | SIMPLE      | tb    | ref  | idx_abc       | idx_abc | 4       | rep.ta.a | 3304 |   100.00 | Using join buffer (Batched Key Access) |
+----+-------------+-------+------+---------------+---------+---------+----------+------+----------+----------------------------------------+

```

- Using MRR

查询使用了MRR（Multi-Range Read），MRR主要是为了减少回表查询数据时随机IO的数量。下面这个例子中使用了BKA提示，强制优化器使用MRR。

```plain
mysql> explain select /*+ BKA(tab) */ *
  from tab
  where a=1 and b in (1,2,3);

+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+----------------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref  | rows | filtered | Extra                            |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+----------------------------------+
|  1 | SIMPLE      | tab   | range | idx_abc       | idx_abc | 8       | NULL |    3 |   100.00 | Using index condition; Using MRR |
+----+-------------+-------+-------+---------------+---------+---------+------+------+----------+----------------------------------+

```

- Using sort\_union(…), Using union(…), Using intersect(…)

```plain
mysql> explain select *
  from t_merge
  where b=2 and c=2 and d=1;
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+---------------------------------------------+
| id | select_type | table   | type        | possible_keys | key           | key_len | ref  | rows | filtered | Extra                                       |
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+---------------------------------------------+
|  1 | SIMPLE      | t_merge | index_merge | idx_bd,idx_cd | idx_cd,idx_bd | 8,8     | NULL |    2 |    66.99 | Using intersect(idx_cd,idx_bd); Using where |
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+---------------------------------------------+

mysql> explain select *
  from t_merge
  where (b=2 and d=1) or (c=2 and d=1);
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+-----------------------------------------+
| id | select_type | table   | type        | possible_keys | key           | key_len | ref  | rows | filtered | Extra                                   |
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+-----------------------------------------+
|  1 | SIMPLE      | t_merge | index_merge | idx_bd,idx_cd | idx_bd,idx_cd | 8,8     | NULL |  108 |   100.00 | Using union(idx_bd,idx_cd); Using where |
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+-----------------------------------------+

mysql> explain select *
  from t_merge
  where (b=2 and d between 1 and 2) or (d=1 and c=2);
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+----------------------------------------------+
| id | select_type | table   | type        | possible_keys | key           | key_len | ref  | rows | filtered | Extra                                        |
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+----------------------------------------------+
|  1 | SIMPLE      | t_merge | index_merge | idx_bd,idx_cd | idx_bd,idx_cd | 8,8     | NULL |  165 |   100.00 | Using sort_union(idx_bd,idx_cd); Using where |
+----+-------------+---------+-------------+---------------+---------------+---------+------+------+----------+----------------------------------------------+

```

## 总结

出于完整性的考虑，这一讲中我们使用了四十多个SQL语句，演示并解释了MySQL执行计划的各种输出。在实际工作中，一般也不会遇到这里的每一种情况。

执行计划有几个信息要重点关注：

- 通过ID、SELECT\_TYPE、TABLE这几列可以了解语句整体的连接、嵌套结构。

- TYPE列为ref、range时，才是我们平时说的用到了索引。type为index时，实际上是使用了全索引扫描。

- ROWS列是优化器评估的需要从到存储引擎里访问的记录的数量，这个数量对性能有直接的影响。

- EXTRA列里面提供了执行计划的额外信息，对这里出现的内容要有大致的了解。


你也可以使用FORMAT=TREE，以树的形式显示执行计划，有时候这样可能会更直观。

## 思考题

这一讲中有这么一个SQL：

```plain
select id, a, (select avg(b) from tab where a=t1.a) from tab t1;

```

在我们的测试表中，字段A的唯一值有三个，所以理论上，最优的情况下只需要将3个不同的A的值分别传入子查询中（select avg(b) from tab where a = t1.a），并将计算结果缓存起来，这样子查询只需要执行3次。

MariaDB实际上就有这样的处理，因此在执行上面这个SQL时，速度比较快。

```plain
mariadb> select id, a, (select avg(b) from tab where a=t1.a) from tab t1 order by id;
+------+---+---------------------------------------+
| id   | a | (select avg(b) from tab where a=t1.a) |
+------+---+---------------------------------------+
|    0 | 0 |                             4999.5000 |
|    1 | 1 |                             4999.0000 |
|    2 | 2 |                             5000.0000 |
......
| 9999 | 0 |                             4999.5000 |
+------+---+---------------------------------------+
10000 rows in set (0.01 sec)

```

但是MySQL中，同样的表结构和数据，配置一样的服务器，执行这个SQL时，执行时间是好几个数量级。

```plain
mysql> select id, a, (select avg(b) from tab where a=t1.a) from tab t1 order by id;
+------+------+---------------------------------------+
| id   | a    | (select avg(b) from tab where a=t1.a) |
+------+------+---------------------------------------+
|    0 |    0 |                             4999.5000 |
|    1 |    1 |                             4999.0000 |
|    2 |    2 |                             5000.0000 |
......
| 9999 |    0 |                             4999.5000 |
+------+------+---------------------------------------+
10000 rows in set (4 min 17.90 sec)

```

对于这种情况，你会怎么解决呢？

期待你的思考，欢迎在留言区中与我交流。如果今天的课程让你有所收获，也欢迎转发给有需要的朋友。我们下节课再见！