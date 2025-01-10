你好，我是陈博士。今天我们来看下银行贷款业务的数据查询与优化。

贷款业务是银行的重要工作之一。通过数据查询，可以了解客户的信用风险，对后续审批贷款进行决策。同时在日常运营中，也需要做各种数据报表和统计，以便了解不同时期、不同类型用户、不同产品的经营业绩和风险情况。

针对该场景，我整理了3张数据表以及对应的查询问题。针对这些查询问题，你可以了解到这些SQL该如何撰写。

## 数据表

- 客户信息表 customer

![图片](https://static001.geekbang.org/resource/image/65/8b/651aec6416d34f6fe7f2e1efaf7d098b.jpg?wh=1332x1190)

- 产品信息表 product

![图片](https://static001.geekbang.org/resource/image/ac/96/acb459a209237a10b3fdf2833e411e96.jpg?wh=1316x642)

- 贷款信息表 loan

## ![图片](https://static001.geekbang.org/resource/image/4c/8c/4c8f64b404c5c12b35d1f5b68becb68c.jpg?wh=1332x1464)

## 问题设定

我从客户信息查询、产品信息查询、贷款信息查询、综合查询、聚合查询等维度，设置了一些常见的查询问题。我们一起来看一下。

### **客户信息查询**

查询身份号为 478116535425961877 的用户贷款的情况。

```plain
SELECT c.name, c.id_number, l.loan_type, l.loan_amount, l.loan_term, l.loan_issue_date, l.loan_status
FROM customer c
JOIN loan l ON c.customer_id = l.customer_id
WHERE c.id_number = '478116535425961877';

```

说明：使用JOIN连接customer和loan表，通过ON指定连接条件，WHERE子句筛选特定身份证号的用户贷款信息。

查询信用评分在 \[600-700\] 之间，贷款总额最多的TOP10用户。

```plain
SELECT c.customer_id,
       c.name,
       c.credit_score,
       SUM(l.loan_amount) AS total_loan_amount
FROM customer c
JOIN loan l ON c.customer_id = l.customer_id
WHERE c.credit_score BETWEEN 600 AND 700
GROUP BY c.customer_id
ORDER BY total_loan_amount DESC
LIMIT 10;

```

说明：这里BETWEEN是包括边界的。也就是说，BETWEEN 600 AND 700，会包括边界值 600 和 700。

### **产品信息查询**

查询所有消费贷产品的名称。

```plain
SELECT product_name
FROM product
WHERE product_category = '消费贷'

```

按产品类别统计各类贷款产品的数量。

```plain
SELECT product_category, COUNT(*) AS product_count
FROM product
GROUP BY product_category

```

说明：使用GROUP BY按产品类别分组，COUNT(\*) 统计每组的贷款产品数量，从而得出各类贷款产品的总数。

### **贷款信息查询**

查询2024年之前尚未结清的房贷产品A的贷款。

```plain
SELECT l.loan_id,
       l.customer_id,
       l.loan_amount,
       l.loan_term,
       l.loan_issue_date,
       l.loan_application_date,
       l.loan_status,
       l.loan_channel,
       l.interest_rate,
       l.loan_balance
FROM loan l
JOIN product p ON l.product_id = p.product_id
WHERE p.product_name = '房贷产品A'
  AND l.loan_status != '已结清'
  AND YEAR(l.loan_application_date) < 2024

```

说明：YEAR() 是一个SQL函数，用于从日期中提取年份。

查询在2024-05-01到2024-05-07之间内申请的贷款。

```plain
SELECT loan_id,
       customer_id,
       product_id,
       loan_amount,
       loan_term,
       loan_application_date,
       loan_status
FROM loan
WHERE loan_application_date BETWEEN '2024-05-01' AND '2024-05-07'

```

说明：这里的 BETWEEN 也是包含 2024-05-01 和 2024-05-07 的日期的。

### **综合查询**

查询每个贷款产品的平均放款利率。

```plain
SELECT p.product_name,
       AVG(l.interest_rate) AS avg_interest_rate
FROM loan l
JOIN product p ON l.product_id = p.product_id
GROUP BY p.product_name

```

说明：在使用GROUP BY进行分组操作的时候，我们可以使用 AVG计算每组贷款产品的平均放款利率。

统计不同就业状态下客户的贷款情况。

```plain
SELECT c.employment_status,
       COUNT(l.loan_id) AS total_loans,
       SUM(l.loan_amount) AS total_loan_amount,
       AVG(l.loan_amount) AS avg_loan_amount
FROM customer c
JOIN loan l ON c.customer_id = l.customer_id
GROUP BY c.employment_status

```

说明：通过JOIN连接customer和loan表，GROUP BY按就业状态分组，使用聚合函数COUNT、SUM和AVG分别统计贷款数量、总额和平均金额。

查询贷款余额超过10万、且信用评分低于600、且最近3个月有借款记录的客户列表。

说明：DATE\_SUB() 是日期计算的SQL函数，它从给定的日期中减去指定的时间间隔。

```plain
SELECT c.customer_id,
       c.name,
       c.credit_score,
       l.loan_balance,
       l.loan_application_date
FROM customer c
JOIN loan l ON c.customer_id = l.customer_id
WHERE l.loan_balance > 100000
      AND c.credit_score < 600
      AND l.loan_application_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)

```

函数有两个参数：第一个是日期表达式，第二个是表示时间间隔的INTERVAL表达式。

### **聚合查询**

统计2024年每月贷款发放量及总金额。

```plain
SELECT MONTH(loan_issue_date) AS loan_month,
       COUNT(loan_id) AS total_loans,
       SUM(loan_amount) AS total_loan_amount
FROM loan
WHERE YEAR(loan_issue_date) = 2024
GROUP BY MONTH(loan_issue_date)
ORDER BY loan_month

```

说明：使用WHERE筛选2024年的贷款记录，GROUP BY按月份分组，COUNT和SUM分别统计每月贷款数量和总金额，ORDER BY按月份排序。

分析不同信用评分段客户的平均月收入。

```plain
SELECT
  CASE
    WHEN credit_score BETWEEN 300 AND 399 THEN '300-399'
    WHEN credit_score BETWEEN 400 AND 499 THEN '400-499'
    WHEN credit_score BETWEEN 500 AND 599 THEN '500-599'
    WHEN credit_score BETWEEN 600 AND 699 THEN '600-699'
    WHEN credit_score BETWEEN 700 AND 799 THEN '700-799'
    WHEN credit_score BETWEEN 800 AND 899 THEN '800-899'
    WHEN credit_score >= 900 THEN '900+'
  END AS credit_score_range,
  AVG(income) AS average_income
FROM customer
GROUP BY credit_score_range
ORDER BY credit_score_range

```

说明：CASE 表达式在SQL中用于实现条件逻辑，类似于编程语言中的 if-else 或 switch-case 语句。它允许你在查询中执行复杂的逻辑判断，并基于这些判断返回不同的值。

CASE 表达式有两种形式：简单 CASE 和搜索 CASE。

在这个查询中使用的是搜索 CASE，它可以根据一个或多个布尔表达式的真假来决定返回哪个结果，即：

```plain
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    ...
    ELSE else_result
END

```

分析贷款期限与还款表现之间的关系。

```plain
SELECT
  loan_term,
  COUNT(loan_id) AS total_loans,
  SUM(CASE WHEN loan_status = '已结清' THEN 1 ELSE 0 END) AS loans_paid_off,
  SUM(CASE WHEN loan_status IN ('申请中', '已放款') THEN 1 ELSE 0 END) AS loans_active,
  ROUND(SUM(CASE WHEN loan_status = '已结清' THEN 1 ELSE 0 END) / COUNT(loan_id) * 100, 2) AS percentage_paid_off,
  ROUND(SUM(CASE WHEN loan_status IN ('申请中', '已放款') THEN 1 ELSE 0 END) / COUNT(loan_id) * 100, 2) AS percentage_active
FROM loan
GROUP BY loan_term
ORDER BY loan_term;

```

说明：SUM 和 CASE 联合使用是一种非常强大的SQL技巧，它允许你根据特定条件对数据进行有条件的聚合。这种组合通常用于在同一个查询中创建多个聚合统计，如计数、求和等，并且可以根据不同的逻辑来定制这些统计。

SUM 和 CASE 联合使用的语法：

```plain
SUM(CASE WHEN condition THEN value ELSE 0 END)

```

在这个查询中：

- 贷款总数： `COUNT(loan_id)` 统计每个贷款期限内的总贷款数量。

- 已结清贷款数量： `SUM(CASE WHEN loan_status = '已结清' THEN 1 ELSE 0 END)` 对于状态为“已结清”的每条记录，返回1，然后对这些1求和，得到该贷款期限内已结清的贷款数量。

- 活跃贷款数量： `SUM(CASE WHEN loan_status IN ('申请中', '已放款') THEN 1 ELSE 0 END)` 对于状态为“申请中”或“已放款”的每条记录，返回1，然后对这些1求和，得到该贷款期限内活跃的贷款数量。

- 计算百分比：使用类似的 SUM 和 CASE 结构，来计算已结清贷款和活跃贷款的比例，并用 `ROUND()` 函数保留两位小数。


这段SQL查询，按照贷款期限进行分组，统计了不同贷款期限下的主要特征，包括：贷款总数、已结清贷款数量、活跃贷款数量、计算百分比（已结清贷款百分比、活跃贷款百分比）。这样更方便观察不同贷款期限下的比例关系，更好地进行趋势识别和风险评估。

如果你是金融行业的从业人员，这节课将对你非常有帮助。期待你的转发，我们下节课再见！