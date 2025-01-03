你好，我是俊达。

这一讲我们来看一下SQL优化篇中的思考题的解答。

## 第17讲

问题：

```plain
create table t_n(a int not null, primary key(a));

insert into t_n values(1),(2),(3),(4),(5),(6),(7),(8),(9),(10),
  (11),(12),(13),(14),(15),(16),(17),(18),(19),(20);

create table t_abc(
    id int not null auto_increment,
    a int not null,
    b int not null,
    c int not null,
    d int not null,
    padding varchar(200),
    primary key(id),
    key idx_abc(a,b,c)
) engine=innodb;

insert into t_abc(a,b,c,d, padding)
select t1.a, t2.a, t3.a, t3.a, rpad('', 200, 'ABC DEF G XYZ')
from t_n t1, t_n t2, t_n t3;

```

根据测试表t\_abc的结构，分析下面这几个SQL语句的执行路径，有哪些区别？

```plain
-- SQL 1
select * from t_abc where a = 10 and b = 10;
-- SQL 2
select * from t_abc where a = 10 and c = 10;
-- SQL 3
select * from t_abc where a = 10 and d = 10;

-- SQL 4
select * from t_abc where a = 10 order by a,c;
-- SQL 5
select * from t_abc where a = 10 order by b,c;

-- SQL 6
select id, a, b, c from t_abc where a = 10;
-- SQL 7
select id, a, b, c from t_abc where b = 10;
-- SQL 8
select id, a, b, c, d from t_abc where b = 10;

```

@123 在评论区中提供了这个问题比较全面的回答。

这个问题主要是关于组合索引的使用情况。前面的三个SQL，SQL 1能用到索引前缀（a,b)。SQL 2和SQL 3只能用到索引前缀（a）。但是SQL 2和SQL 3还是有一些区别的。SQL 2可以用到索引条件下推。

SQL 4和SQL 5的区别，主要在于是否能使用索引的有序性来避免排序。SQL 4需要使用文件排序，因为order by的字段顺序（a，c）和索引字段顺序（a，b，c）不一样。SQL 5可以避免排序，条件a使用了等值条件，再加上排序字段，和索引字段顺序一致。

SQL 6可以用到索引前缀（a），但是SQL 7无法使用索引来过滤数据。当然，这里SQL 7用到了覆盖索引，这种情况下有可能用到 skip scan。

```plain
mysql> explain select id, a, b, c from t_abc where b = 10;
+----+-------------+-------+-------+---------------+---------+---------+------+----------------------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | rows | Extra                                  |
+----+-------------+-------+-------+---------------+---------+---------+------+----------------------------------------+
|  1 | SIMPLE      | t_abc | range | idx_abc       | idx_abc | 8       |  793 | Using where; Using index for skip scan |
+----+-------------+-------+-------+---------------+---------+---------+------+----------------------------------------+

```

SQL 6和SQL 8的主要区别，是SQL 6可以用到覆盖索引。当然，由于InnoDB MVCC的实现机制，即使用了覆盖索引，也有可能要访问聚簇索引查询数据，具体可以参考 [第32讲](https://time.geekbang.org/column/article/819420)。

## 第18讲

问题：

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

@Shelly @叶明 在评论区中提供了一种优化方法，改写SQL，子查询中先进行group by，然后再和原表join。

```plain
select
  t1.id,
  t1.a,
  t2.avg_b
from
  tab t1
  inner join (
    select
      a,
      avg(b) avg_b
    from
      tab
    group by
      a
  ) t2 on t1.a = t2.a
order by
  id;

```

## 第19讲

问题：有时我们需要分段处理全表的数据。如果表使用了单列主键，那么可以很方便地按主键范围来进行数据分片。但有些情况下，业务使用了联合主键，那么此时你应该怎么按主键范围来对数据进行分片呢？

```plain
create table t_business(
  id1 varchar(30) not null,
  id2 varchar(30) not null,
  id3 varchar(30) not null,
  col1 ...,
  col2 ...,
  primry key(id1, id2, id3)
) engine=innodb;

```

考虑上面这个表，使用了联合主键(id1, id2, id3)。你需要分片处理这个表的数据，每次处理1000行数据，要求不要重复处理数据，但也不要漏掉任何一条数据。整个表的数据量比较大，要尽可能保证性能。你会怎么来写这个分页的SQL呢？

@叶明 在评论区中提供了解决这个问题的几种思路。

一种方法是使用下面这种写法，‘id1’, ‘id2’,'id3’是上一批数据中的最后一条记录。不过这么写MySQL好像使用了全表扫描。

```plain
select *
from t_business
where (id1, id2, id3) > ('id1', 'id2', 'id3')
order by id1, id2, id3
limit 1000

```

另一种方法是使用下面这种写法。

```plain
select *
from t_business
where (id1 > 'id1')
or (id1 = 'id1' and id2 > 'id2')
or (id1 = 'id1' and id2 = 'id2' and id3 > 'id3')
order by id1, id2, id3
limit 1000

```

首先这种写法逻辑是上正确的，和条件(id1, id2, id3) > (‘id1’, ‘id2’, ‘id3’)等价。而且这么写也能用到主键，效率上也有保障。

## 第20讲

问题：回到我们前面那个订单列表的场景，有一天，产品决定要做一个订单删除的功能，方便用户将一些不想让人看到订单隐藏起来。相应地，业务SQL需要做一些相应的调整，where条件中需要增加is\_deleted的条件。

```plain
select count(*)
from t_order_detail
where seller_id = ?
and order_status in (?)
and refund_status in(?)
and is_deleted=0;

select t2.* from (
  select id
  from t_order_detail
  where seller_id = ?
  and order_status in (?)
  and refund_status in(?)
  and is_deleted=0
  order by create_time
limit M, N) t1 straight_join t_order_detail t2
where t1.id = t2.id;

```

作为一名研发人员，或者是一名DBA，接到这个需求后，在数据库这一层，有哪些需要考虑的地方？为了实现这个功能，你会怎样做？

@叶明 @123 在评论区中提供了这个问题的解答。

where条件中添加is\_deleted条件后，由于原先的索引中不包含这个字段，因此会增加大量的回表操作。原先的select count(\*)查询可以使用覆盖索引，增加is\_deleted条件后就不能使用覆盖索引了。原先的分页SQL，可以在索引上分页，获取一批主键ID，增加is\_deleted条件后，也会增量很多回表操作，检查记录是否满足条件。

对于这个场景，一般会在索引中添加is\_deleted字段。is\_deleted字段过滤性并不高，可以放在索引字段的最后面。

@binzhang 提供了另外一种思路，就是不添加is\_deleted字段，而是使用原先的order\_status字段来满足这个需求。在这个场景下，这也是一种很好的方法，不修改表结构，不调整索引，只调整应用程序的代码逻辑。

## 第21讲

问题：最后来看一个表连接的例子，先创建一个测试表，写入10000行数据。

```plain
create table t_jointab(
  id int not null auto_increment,
  a int not null,
  b int not null,
  c varchar(4000),
    primary key(id),
    key idx_a(a)
) engine=innodb charset utf8mb4;

insert into t_jointab(a,b,c)
select case when n < 9000 then n else 9000 end as a,
    n % 1000, rpad('x', 2000, 'ABCD')
from numbers where n < 10000;

```

收集并查看统计信息。

```plain
mysql> analyze table t_jointab;
+---------------+---------+----------+----------+
| Table         | Op      | Msg_type | Msg_text |
+---------------+---------+----------+----------+
| rep.t_jointab | analyze | status   | OK       |
+---------------+---------+----------+----------+
1 row in set (0.62 sec)

mysql> show indexes from t_jointab;
+------------+----------+--------------+-------------+-------------+
| Non_unique | Key_name | Seq_in_index | Column_name | Cardinality |
+------------+----------+--------------+-------------+-------------+
|          0 | PRIMARY  |            1 | id          |        8580 |
|          1 | idx_a    |            1 | a           |        8580 |
+------------+----------+--------------+-------------+-------------+

```

我们来看一下这个SQL的执行计划，使用了嵌套循环。

```plain
mysql> explain format=tree
    select count(*)
    from t_jointab t1, t_jointab t2
    where t1.a = t2.a and t1.b = t2.b\G
*************************** 1. row ***************************
EXPLAIN:
-> Aggregate: count(0)  (cost=5079.75 rows=1)
    -> Nested loop inner join  (cost=4221.75 rows=8580)
        -> Table scan on t1  (cost=1218.75 rows=8580)
        -> Filter: (t2.b = t1.b)  (cost=0.25 rows=1)
            -> Index lookup on t2 using idx_a (a=t1.a)  (cost=0.25 rows=1)

```

上面这个执行计划看上去没什么大问题，但是在我的环境中，执行消耗了1分多的时间。

```plain
mysql> select count(*)
   from t_jointab t1, t_jointab t2
   where t1.a = t2.a and t1.b = t2.b;
+----------+
| count(*) |
+----------+
|    10000 |
+----------+
1 row in set (1 min 19.29 sec)

```

查看慢日志发现，这个语句的Rows\_examined比较高，有100多万。

```plain
# Query_time: 79.285872  Lock_time: 0.000036 Rows_sent: 1  Rows_examined: 1019000
SET timestamp=1724921875;
select count(*)。
   from t_jointab t1, t_jointab t2
   where t1.a = t2.a and t1.b = t2.b;

```

请你分析一下，这个SQL执行比较慢的原因是什么？ 有哪些可能的优化方案（前提是不能修改表里的数据）？

这个问题 @叶明 在评论区做了很详细的分析，并且提供了两种有效的解决方法。

一种方法是使用Hash Join，通过ignore index提示，让优化器忽略掉索引idx\_a，从而使用Hash Join。

```plain
select count(*) from t_jointab t1 ignore index(idx_a), t_jointab t2 ignore index(idx_a) where t1.a = t2.a and t1.b = t2.b;

```

还有一种方法是修改索引，在索引中添加字段b。

```plain
alter table t_jointab drop index idx_a, add index idx_a(a,b);

```

如果对比下Hash join和Nested Loop Join的执行计划，你会发现这个例子中Nested loop Join的cost比Hash join要低很多，但是实际执行时，Hash Join比Nested Loop Join要快很多。所以，对于一个SQL，cost低的执行计划，执行效率不一定更高。

```plain
mysql> explain format=tree  select count(*)
    from t_jointab t1 , t_jointab t2
    where t1.a = t2.a and t1.b = t2.b\G
*************************** 1. row ***************************
EXPLAIN: -> Aggregate: count(0)  (cost=4307.55 rows=1)
    -> Nested loop inner join  (cost=4221.75 rows=858)
        -> Table scan on t1  (cost=1218.75 rows=8580)
        -> Filter: (t2.b = t1.b)  (cost=0.25 rows=0.1)
            -> Index lookup on t2 using idx_a (a=t1.a)  (cost=0.25 rows=1)

```

```plain
mysql>explain format=tree  select count(*)
  from t_jointab t1 ignore index(idx_a)  , t_jointab t2 ignore index(idx_a)
  where t1.a = t2.a and t1.b = t2.b\G
*************************** 1. row ***************************
EXPLAIN:
-> Aggregate: count(0)  (cost=7364171.96 rows=1)
    -> Inner hash join (t2.b = t1.b), (t2.a = t1.a)  (cost=7363313.96 rows=8580)
        -> Table scan on t2  (cost=0.05 rows=8580)
        -> Hash
            -> Table scan on t1  (cost=1218.75 rows=8580)

```

## 第22讲

问题：

这一讲中，我提供了两种手动改写子查询的思路。

思路1：

```plain
mysql> select t1.item_id, sum(t1.sold) as sold
from stat_item_detail t1, (
  select distinct item_id
  from stat_item_detail t2
  where t2.gmt_create >= '2026-04-26 10:30:00') t22
where t1.item_id = t22.item_id
group by t1.item_id;

```

思路2：

```plain
select item_id, sum(sold) from (
    select distinct t1.id,  t1.item_id, t1.sold as sold
    from stat_item_detail t1, stat_item_detail t2
    where t1.item_id = t2.item_id
    and t2.gmt_create >= '2026-04-26 10:30:00'
) t group by item_id;

```

请问这两种改写方式，分别对应了MySQL半连接转换中的哪一个策略？

我们来回顾一下MySQL半连接转换的几种策略。

- Pullout：直接将子查询提到外层，改写成表连接。

能使用Pullout的前提是自查询中有主键或唯一索引能保证数据不重复。

- Duplicate weedout：如果子查询中的数据可能存在重复，MySQL会对结果数据进行去重。

Duplicate weedout是先执行Join，然后对结果集进行去重处理。

- First Match：执行表连接时，对于驱动表中的每一行记录，只需要匹配子查询的第一条记录就返回。

使用First Match策略时，以主查询作为驱动表，连接子查询的表时，只要匹配到一条记录就返回。

- Loose Scan：利用子查询中索引的有序性，获取关联条件的唯一值。

Loose Scan是利用子查询中的索引，来获取一组不重复的数据，和主查询进行表连接。

- Materialization：将子查询的结果存储在临时表，临时表再和父表进行关联。

Materialization是先对子查询的结果集进行去重，然后再和主查询进行表连接操作。

这里的第一种改写方式是先对子查询中的数据进行去重，对应Materialization这种转换方式。第二种改写方式是先Join，然后再去重，对应Duplicate weedout。评论区中 @叶明 也提供了这个问题的解答。

## 第23讲

问题：有时候我们会遇到执行计划选择了错误的索引，导致SQL性能比较差。一个可能的解决方案是使用force index强制索引。使用force index可能会存在哪些潜在的风险？有没有其他办法来避免执行计划选错索引？

@叶明 @Geek\_c37964 @陈星宇(2.11) 在评论区中提供了一些解答。

先来看一下force index的一些特点。

- force index可以指定多个索引，比如force index(idx\_a, idx\_b, idx\_c)

- 如果force index中指定的某个索引在表中不存在，或者是invisible索引，SQL会报错

- 如果使用了force index，那么MySQL不会再考虑使用不在这个列表中的索引。


比如id是主键， 下面这个SQL使用了force index。虽然有主键的条件，但还是会使用全表扫描。

```plain
select * from tab force index(idx_x) where id = 10

```

- 如果使用了force index，优化器会认为全表扫描的成本是无穷大。如果指定的索引可以用到，优化器就不会使用全表扫描。

比如下面这个查询，表tab上有索引idx\_abc(a,b,c)。虽然表中的所有记录都满足a >=0的条件，这种情况下走全表扫描效率更高，但是优化器还是会使用idx\_abc的range访问路径。

```plain
select * from tab force index(idx_abc) where a >=0

```

因此使用force index有几点需要注意。

1. 如果使用了force index，不能删除或修改列表中的索引名，否则会导致SQL报错。

2. 要确保SQL中传入了指定索引的前缀字段的条件。

3. 如果查询选错了索引，要先分析下走错索引的原因。有的时候是因为表上存在相似的索引，比如表上存在多个前缀一样的索引。或者现有的索引不够优化。如果调整索引能解决，就优先考虑调整下索引。


如果某个特定的场景下优化器真的选不到最优的索引和执行计划，可以适当使用force index提示。

## 第24讲

问题：下面这类SQL按多个表的字段来排序，请分析下这么排序，对SQL性能的影响是什么？如果只使用一个表的字段来排序，性能上会有什么区别吗？

```plain
select *
from t1, t2, t3
where t1.c1 = t2.c1
and t2.c2 = t3.c3
order by t1.s1, t2.s2
limit 100;

```

这个问题 @叶明 在评论区给出了解答。

我们来看一个例子。

```plain
mysql> show indexes from tab;
+-------+------------+----------+--------------+-------------+-------------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Cardinality |
+-------+------------+----------+--------------+-------------+-------------+
| tab   |          0 | PRIMARY  |            1 | id          |       10010 |
| tab   |          1 | idx_abc  |            1 | a           |           3 |
| tab   |          1 | idx_abc  |            2 | b           |       10000 |
| tab   |          1 | idx_abc  |            3 | c           |       10000 |
+-------+------------+----------+--------------+-------------+-------------+

```

如果排序字段都来自于同一个表，可以先对这个表进行排序，然后再连接到另外一个表。

```plain
mysql> explain format=tree
  select *
  from tab t1, tab t2
  where t1.id = t2.id
  order by t1.b, t1.c
  limit 10\G
*************************** 1. row ***************************
EXPLAIN: -> Limit: 10 row(s)  (cost=12089.17 rows=10)
    -> Nested loop inner join  (cost=12089.17 rows=10010)
        -> Sort: t1.b, t1.c  (cost=1160.67 rows=10010)
            -> Table scan on t1  (cost=1160.67 rows=10010)
        -> Single-row index lookup on t2 using PRIMARY (id=t1.id)  (cost=0.99 rows=1)

```

如果排序字段来自不同的表，需要先进行表连接，数据写到临时表，然后再对临时表进行排序。

```plain
mysql> explain format=tree
  select *
  from tab t1, tab t2
  where t1.id = t2.id
  order by t1.b, t2.c
  limit 10\G
*************************** 1. row ***************************
EXPLAIN: -> Limit: 10 row(s)
    -> Sort: t1.b, t2.c, limit input to 10 row(s) per chunk
        -> Stream results  (cost=12089.17 rows=10010)
            -> Nested loop inner join  (cost=12089.17 rows=10010)
                -> Table scan on t1  (cost=1160.67 rows=10010)
                -> Single-row index lookup on t2 using PRIMARY (id=t1.id)  (cost=0.99 rows=1)

```

对比这两个SQL的optimizer\_trace，使用多个表的字段排序时，resulting\_clause\_is\_simple为False。

```plain
{
  "optimizing_distinct_group_by_order_by": {
    "simplifying_order_by": {
      "original_clause": "`t1`.`b`,`t2`.`c`",
      "items": [
        {
          "item": "`t1`.`b`"
        },
        {
          "item": "`t2`.`c`"
        }
      ],
      "resulting_clause_is_simple": false,
      "resulting_clause": "`t1`.`b`,`t2`.`c`"
    }
  }
}

```