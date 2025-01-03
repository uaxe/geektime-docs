函数在计算机语言的使用中贯穿始终，在SQL中我们也可以使用函数对检索出来的数据进行函数操作，比如求某列数据的平均值，或者求字符串的长度等。从函数定义的角度出发，我们可以将函数分成内置函数和自定义函数。在SQL语言中，同样也包括了内置函数和自定义函数。内置函数是系统内置的通用函数，而自定义函数是我们根据自己的需要编写的，下面讲解的是SQL的内置函数。

你需要从以下几个方面掌握SQL函数：

1. 什么是SQL函数？
2. 内置的SQL函数都包括哪些？
3. 如何使用SQL函数对一个数据表进行操作，比如针对一个王者荣耀的英雄数据库，我们可以使用这些函数完成哪些操作？
4. 什么情况下使用SQL函数？为什么使用SQL函数有时候会带来问题？

## 什么是SQL函数

当我们学习编程语言的时候，也会遇到函数。函数的作用是什么呢？它可以把我们经常使用的代码封装起来，需要的时候直接调用即可。这样既提高了代码效率，又提高了可维护性。

SQL中的函数一般是在数据上执行的，可以很方便地转换和处理数据。一般来说，当我们从数据表中检索出数据之后，就可以进一步对这些数据进行操作，得到更有意义的结果，比如返回指定条件的函数，或者求某个字段的平均值等。

## 常用的SQL函数有哪些

SQL提供了一些常用的内置函数，当然你也可以自己定义SQL函数。SQL的内置函数对于不同的数据库软件来说具有一定的通用性，我们可以把内置函数分成四类：

1. 算术函数
2. 字符串函数
3. 日期函数
4. 转换函数

这4类函数分别代表了算术处理、字符串处理、日期处理、数据类型转换，它们是SQL函数常用的划分形式，你可以思考下，为什么是这4个维度？

函数是对提取出来的数据进行操作，那么数据表中字段类型的定义有哪几种呢？

我们经常会保存一些数值，不论是整数类型，还是浮点类型，实际上对应的就是数值类型。同样我们也会保存一些文本内容，可能是人名，也可能是某个说明，对应的就是字符串类型。此外我们还需要保存时间，也就是日期类型。那么针对数值、字符串和日期类型的数据，我们可以对它们分别进行算术函数、字符串函数以及日期函数的操作。如果想要完成不同类型数据之间的转换，就可以使用转换函数。

### 算术函数

算术函数，顾名思义就是对数值类型的字段进行算术运算。常用的算术函数及含义如下表所示：

![](https://static001.geekbang.org/resource/image/19/e1/193b171970c90394576d3812a46dd8e1.png?wh=1243*256)

这里我举一些简单的例子，你来体会下：

`SELECT ABS(-2)`，运行结果为2。

`SELECT MOD(101,3)`，运行结果2。

`SELECT ROUND(37.25,1)`，运行结果37.3。

### 字符串函数

常用的字符串函数操作包括了字符串拼接，大小写转换，求长度以及字符串替换和截取等。具体的函数名称及含义如下表所示：

![](https://static001.geekbang.org/resource/image/c1/4d/c161033ebeeaa8eb2436742f0f818a4d.png?wh=1237*568)

这里同样有一些简单的例子，你可以自己运行下：

`SELECT CONCAT('abc', 123)`，运行结果为abc123。

`SELECT LENGTH('你好')`，运行结果为6。

`SELECT CHAR_LENGTH('你好')`，运行结果为2。

`SELECT LOWER('ABC')`，运行结果为abc。

`SELECT UPPER('abc')`，运行结果ABC。

`SELECT REPLACE('fabcd', 'abc', 123)`，运行结果为f123d。

`SELECT SUBSTRING('fabcd', 1,3)`，运行结果为fab。

### 日期函数

日期函数是对数据表中的日期进行处理，常用的函数包括：

![](https://static001.geekbang.org/resource/image/3d/45/3dec8d799b1363d38df34ed3fdd29045.png?wh=931*615)

下面是一些简单的例子，你可自己运行下：

`SELECT CURRENT_DATE()`，运行结果为2019-04-03。

`SELECT CURRENT_TIME()`，运行结果为21:26:34。

`SELECT CURRENT_TIMESTAMP()`，运行结果为2019-04-03 21:26:34。

`SELECT EXTRACT(YEAR FROM '2019-04-03')`，运行结果为2019。

`SELECT DATE('2019-04-01 12:00:05')`，运行结果为2019-04-01。

这里需要注意的是，DATE日期格式必须是yyyy-mm-dd的形式。如果要进行日期比较，就要使用DATE函数，不要直接使用日期与字符串进行比较，我会在后面的例子中讲具体的原因。

### 转换函数

转换函数可以转换数据之间的类型，常用的函数如下表所示：

![](https://static001.geekbang.org/resource/image/5d/59/5d977d747ed1fddca3acaab33d29f459.png?wh=1085*209)

这两个函数不像其他函数，看一眼函数名就知道代表什么、如何使用。下面举了这两个函数的例子，你需要自己运行下：

`SELECT CAST(123.123 AS INT)`，运行结果会报错。

`SELECT CAST(123.123 AS DECIMAL(8,2))`，运行结果为123.12。

`SELECT COALESCE(null,1,2)`，运行结果为1。

CAST函数在转换数据类型的时候，不会四舍五入，如果原数值有小数，那么转换为整数类型的时候就会报错。不过你可以指定转化的小数类型，在MySQL和SQL Server中，你可以用 `DECIMAL(a,b)` 来指定，其中a代表整数部分和小数部分加起来最大的位数，b代表小数位数，比如 `DECIMAL(8,2)` 代表的是精度为8位（整数加小数位数最多为8位），小数位数为2位的数据类型。所以 `SELECT CAST(123.123 AS DECIMAL(8,2))` 的转换结果为123.12。

## 用SQL函数对王者荣耀英雄数据做处理

我创建了一个王者荣耀英雄数据库，一共有69个英雄，23个属性值。SQL文件见Github地址： [https://github.com/cystanford/sql\_heros\_data](https://github.com/cystanford/sql_heros_data)。

![](https://static001.geekbang.org/resource/image/7b/24/7b14aeedd80fd7e8fb8074f9884d6b24.png?wh=1107*344)

我们现在把这个文件导入到MySQL中，你可以使用Navicat可视化数据库管理工具将.sql文件导入到数据库中。数据表为heros，然后使用今天学习的SQL函数，对这个英雄数据表进行处理。

首先显示英雄以及他的物攻成长，对应字段为 `attack_growth`。我们让这个字段精确到小数点后一位，需要使用的是算术函数里的ROUND函数。

```
SQL：SELECT name, ROUND(attack_growth,1) FROM heros

```

代码中， `ROUND(attack_growth,1)` 中的 `attack_growth` 代表想要处理的数据，“1”代表四舍五入的位数，也就是我们这里需要精确到的位数。

运行结果为：

![](https://static001.geekbang.org/resource/image/fb/ed/fb55a715543e1ed3245ae37210ad75ed.png?wh=640*346)

假设我们想显示英雄最大生命值的最大值，就需要用到MAX函数。在数据中，“最大生命值”对应的列数为 `hp_max`，在代码中的格式为 `MAX(hp_max)`。

```
SQL：SELECT MAX(hp_max) FROM heros

```

运行结果为9328。

假如我们想要知道最大生命值最大的是哪个英雄，以及对应的数值，就需要分成两个步骤来处理：首先找到英雄的最大生命值的最大值，即 `SELECT MAX(hp_max) FROM heros`，然后再筛选最大生命值等于这个最大值的英雄，如下所示。

```
SQL：SELECT name, hp_max FROM heros WHERE hp_max = (SELECT MAX(hp_max) FROM heros)

```

运行结果：

![](https://static001.geekbang.org/resource/image/93/20/9371fdcee4d1f7bdfdd71bc0a58aac20.png?wh=371*125)

假如我们想显示英雄的名字，以及他们的名字字数，需要用到 `CHAR_LENGTH` 函数。

```
SQL：SELECT CHAR_LENGTH(name), name FROM heros

```

运行结果为：

![](https://static001.geekbang.org/resource/image/41/8c/415aa09e2fdc121861e3c96bd8a2af8c.png?wh=614*345)

假如想要提取英雄上线日期（对应字段birthdate）的年份，只显示有上线日期的英雄即可（有些英雄没有上线日期的数据，不需要显示），这里我们需要使用EXTRACT函数，提取某一个时间元素。所以我们需要筛选上线日期不为空的英雄，即 `WHERE birthdate is not null`，然后再显示他们的名字和上线日期的年份，即：

```
SQL： SELECT name, EXTRACT(YEAR FROM birthdate) AS birthdate FROM heros WHERE birthdate is NOT NULL

```

或者使用如下形式：

```
SQL: SELECT name, YEAR(birthdate) AS birthdate FROM heros WHERE birthdate is NOT NULL

```

运行结果为：

![](https://static001.geekbang.org/resource/image/26/16/26cacf4d619d9f177a1f5b22059f9916.png?wh=615*344)

假设我们需要找出在2016年10月1日之后上线的所有英雄。这里我们可以采用DATE函数来判断birthdate的日期是否大于2016-10-01，即 `WHERE DATE(birthdate)>'2016-10-01'`，然后再显示符合要求的全部字段信息，即：

```
SQL： SELECT * FROM heros WHERE DATE(birthdate)>'2016-10-01'

```

需要注意的是下面这种写法是不安全的：

```
SELECT * FROM heros WHERE birthdate>'2016-10-01'

```

因为很多时候你无法确认birthdate的数据类型是字符串，还是datetime类型，如果你想对日期部分进行比较，那么使用 `DATE(birthdate)` 来进行比较是更安全的。

运行结果为：

![](https://static001.geekbang.org/resource/image/e5/22/e5696b5ff0aae0fd910463b1f8e6ed22.png?wh=1112*350)

假设我们需要知道在2016年10月1日之后上线英雄的平均最大生命值、平均最大法力和最高物攻最大值。同样我们需要先筛选日期条件，即 `WHERE DATE(birthdate)>'2016-10-01'`，然后再选择 `AVG(hp_max), AVG(mp_max), MAX(attack_max)` 字段进行显示。

```
SQL： SELECT AVG(hp_max), AVG(mp_max), MAX(attack_max) FROM heros WHERE DATE(birthdate)>'2016-10-01'

```

运行结果为：

![](https://static001.geekbang.org/resource/image/8f/6b/8f559dc1be7d62e4c58402ebe2e7856b.png?wh=1105*128)

## 为什么使用SQL函数会带来问题

尽管SQL函数使用起来会很方便，但我们使用的时候还是要谨慎，因为你使用的函数很可能在运行环境中无法工作，这是为什么呢？

如果你学习过编程语言，就会知道语言是有不同版本的，比如Python会有2.7版本和3.x版本，不过它们之间的函数差异不大，也就在10%左右。但我们在使用SQL语言的时候，不是直接和这门语言打交道，而是通过它使用不同的数据库软件，即DBMS。DBMS之间的差异性很大，远大于同一个语言不同版本之间的差异。实际上，只有很少的函数是被DBMS同时支持的。比如，大多数DBMS使用（\|\|）或者（+）来做拼接符，而在MySQL中的字符串拼接函数为 `Concat()`。大部分DBMS会有自己特定的函数，这就意味着采用SQL函数的代码可移植性是很差的，因此在使用函数的时候需要特别注意。

## 关于大小写的规范

细心的人可能会发现，我在写SELECT语句的时候用的是大写，而你在网上很多地方，包括你自己写的时候可能用的是小写。实际上在SQL中，关键字和函数名是不用区分字母大小写的，比如SELECT、WHERE、ORDER、GROUP BY等关键字，以及ABS、MOD、ROUND、MAX等函数名。

不过在SQL中，你还是要确定大小写的规范，因为在Linux和Windows环境下，你可能会遇到不同的大小写问题。

比如MySQL在Linux的环境下，数据库名、表名、变量名是严格区分大小写的，而字段名是忽略大小写的。

而MySQL在Windows的环境下全部不区分大小写。

这就意味着如果你的变量名命名规范没有统一，就可能产生错误。这里有一个有关命名规范的建议：

1. 关键字和函数名称全部大写；
2. 数据库名、表名、字段名称全部小写；
3. SQL语句必须以分号结尾。

虽然关键字和函数名称在SQL中不区分大小写，也就是如果小写的话同样可以执行，但是数据库名、表名和字段名在Linux MySQL环境下是区分大小写的，因此建议你统一这些字段的命名规则，比如全部采用小写的方式。同时将关键词和函数名称全部大写，以便于区分数据库名、表名、字段名。

## 总结

函数对于一门语言的重要性毋庸置疑，我们在写Python代码的时候，会自己编写函数，也会使用Python内置的函数。在SQL中，使用函数的时候需要格外留意。不过如果工程量不大，使用的是同一个DBMS的话，还是可以使用函数简化操作的，这样也能提高代码效率。只是在系统集成，或者在多个DBMS同时存在的情况下，使用函数的时候就需要慎重一些。

比如 `CONCAT()` 是字符串拼接函数，在MySQL和Oracle中都有这个函数，但是在这两个DBMS中作用却不一样， `CONCAT` 函数在MySQL中可以连接多个字符串，而在Oracle中 `CONCAT` 函数只能连接两个字符串，如果要连接多个字符串就需要用（\|\|）连字符来解决。

![](https://static001.geekbang.org/resource/image/8c/c9/8c5e316b466e8fa65789a9c6a220ebc9.jpg?wh=3341*1309)

讲完了SQL函数的使用，我们来做一道练习题。还是根据王者荣耀英雄数据表，请你使用SQL函数作如下的练习：计算英雄的最大生命平均值；显示出所有在2017年之前上线的英雄，如果英雄没有统计上线日期则不显示。

欢迎你在评论区与我分享你的答案，也欢迎点击”请朋友读“，把这篇文章分享给你的朋友或者同事。