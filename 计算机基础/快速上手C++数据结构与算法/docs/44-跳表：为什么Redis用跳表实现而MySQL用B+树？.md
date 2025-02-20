你好，我是王健伟。

字符串方面知识的讲解告一段落后，这次，我们讲一讲跳表相关的知识，也讲一讲大家所关心的一个问题——为什么Redis用跳表实现而MySQL用B+树实现。

## 在跳表中查询及复杂度分析

回顾以往学习过的数组（线性表的顺序存储）和链表（线性表的链式存储）这两种数据结构，它们各有特点。数组查找速度非常快，但插入、删除速度很慢（要挪动数据）。而链表插入、删除速度快，但查找数据慢。

假设在一个数组中的数据是有序（比如从小到大）排列的，此时若需要快速查询某个元素，那么进行折半（二分）查找是很快就可以找到该元素或者确认该元素不存在的。但如果这组有序的数据并不是用数组而是用链表保存的，那么如何快速查找数据呢？

于是在1989年，美国的一位计算机科学家发明了一种新的数据结构——跳跃表，简称跳表。跳表本身基于链表，是对链表的优化（改进版的链表）。跳表这种数据结构因为出现得比较晚，所以很多老项目中并没有采用。

跳表是只能在链表中元素有序的情况下使用的数据结构，即跳表中的元素必须有序。其插入、删除、搜索的时间复杂度都是O($log\_{2}^{n}$)。它的最大特点是实现相对简单，效率更高，在一些流行项目比如Redis、LevelDB中常被用来代替平衡二叉树（AVL树）或二分查找。