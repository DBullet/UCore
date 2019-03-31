# 数据库设计及使用规范

一、基础规范

（1）必须使用 InnoDB 存储引擎

解读：支持事务、行级锁、并发性能更好、CPU 及内存缓存页优化使得资源利用率更高

 

（2）使用 utf8mb4 字符集

解读：万国码，无需转码，无乱码风险，可存储 emoji

 

（3）禁止使用存储过程、视图、触发器、Event

解读：高并发大数据的互联网业务，架构设计思路是 “解放数据库 CPU，将计算转移到服务层”，并发量大的情况下，这些功能很可能将数据库拖死，业务逻辑放到服务层具备更好的扩展性，能够轻易实现 “增机器就加性能”。数据库擅长存储与索引，CPU 计算还是上移吧

 

（4）禁止存储大文件或者大照片

解读：为何要让数据库做它不擅长的事情？大文件和照片存储在文件系统，数据库里存 URI 多好

 

二、命名规范

 

（5）库名、表名、字段名：小写，下划线风格，不超过 32 个字符，必须见名知意，禁止拼音英文混用

后缀与类型：

项目中 id、status、type 字段名明确为数字枚举类型。

time 时间型、date 日期型，譬如：不要使用 start_date 作为一个时间型字段。

status、type 为整型，使用枚举。

key、title、label、name、description、uri、url 等为字符型。

id 为数字类型。

不要使用对象名作为简单类型的字段名，为其增加可识别其类型的后缀，如：uri、key 等。

头像不要使用 avatar 作为字段名，使用 avatar_key 或者 avatar_url。

字段名 user 不知道是 user_id 还是 user_name。

（6）索引名 idx_xxx，唯一索引名 uniq_xxx

 

三、表设计规范

（7）单实例表数目必须小于 500

 

（8）单表列数目必须小于 30

 

（9）表必须有主键，例如自增主键

解读：

a）主键递增，数据行写入可以提高插入性能，可以避免 page 分裂，减少表碎片提升空间和内存的使用

b）主键要选择较短的数据类型， Innodb 引擎普通索引都会保存主键的值，较短的数据类型可以有效的减少索引的磁盘空间，提高索引的缓存效率

c） 无主键的表删除，在 row 模式的主从架构，会导致备库夯住

 

（10）性能优先的表禁止使用外键，如果有外键完整性约束，需要应用程序控制

解读：外键会导致表与表之间耦合，update 与 delete 操作都会涉及相关联的表，十分影响 sql 的性能，甚至会造成死锁。高并发情况下容易造成数据库性能，大数据高并发业务场景数据库使用以性能优先

 

四、字段设计规范

（*）时间型字段应该如何选择？DATETIME、TIMESTAMP、BITINT 
正常情况下使用 DATETIME 类型，并在字段的注释中记录下该字段对应的时区。时区的话应用程序自己来处理就好了，不要依赖数据库帮忙来处理。
可以使用 BIGINT 存储「UNIX 时间戳」，时区的话应用程序来处理。
使用 TIMESTAMP 必须要注意 time zone 的设置，应用程序与数据库的 time zone 要一致，如：在做跨国数据同步的时候国内的服务要读写国外的数据库，国内服务是 UTC+8，国外数据库是 UTC，会出现问题。
解读：

DATETIME
占用 8 个字节
允许为空值，可以自定义值，系统不会自动修改其值。
实际格式储存与时区无关（Just stores what you have stored and retrieves the same thing which you have stored. It has nothing to deal with the TIMEZONE and Conversion.）
可以使用 MySQL 提供的日期函数。
MySQL 5.6.5 之前是无法使用DEFAULT 和 ON UPDATE 等机制，5.6.5 后可以。
TIMESTAMP
占用 4 个字节
允许为空值，自定义与 MySQL 版本有关。
TIMESTAMP 值不能早于 1970 或晚于 2037。这说明一个日期，例如'1968-01-01'，虽然对于 DATETIME 或 DATE 值是有效的，但对于 TIMESTAMP 值却无效，如果分配给这样一个对象将被转换为 0。
值以 UTC 格式保存（ it stores the number of milliseconds），存储时会发生时区转化 ，存储时对当前的时区进行转换，检索时再转换回当前的时区。MySQL converts TIMESTAMP values from the current time zone to UTC for storage, and back from UTC to the current time zone for retrieval. (This does not occur for other types such as DATETIME.) By default, the current time zone for each connection is the server's time. The time zone can be set on a per-connection basis. As long as the time zone setting remains constant, you get back the same value you store. If you store a TIMESTAMP value, and then change the time zone and retrieve the value, the retrieved value is different from the value you stored. This occurs because the same time zone was not used for conversion in both directions. The current time zone is available as the value of the time_zone system variable. For more information, see Section 5.1.12, “MySQL Server Time Zone Support”.

可以使用如 ON UPDATE 等自动更新字段值的机制；MySQL 5.6.5 之前每张表 DEFAULT 和 ON UPDATE 只能使用一种（DEFAULT CURRENT_TIMESTAMP and ON UPDATE CURRENT_TIMESTAMP can be used with at most one TIMESTAMP column per table. It is not possible to have the current timestamp be the default value for one column and the auto-update value for another column.）

BIGINT

使用日期函数不方便。



https://dev.mysql.com/doc/refman/5.7/en/datetime.html
https://dev.mysql.com/doc/refman/5.6/en/timestamp-initialization.html
（*）布尔类型如何选择？
对于 MySQL 来说，BOOL and BOOLEAN are synonyms of TINYINT(1)
解读：BIT(1) 实际上的存储空间也是 1 byte。
https://dev.mysql.com/doc/refman/5.7/en/numeric-type-overview.html
（*）不需要检索、过滤的字段、不需要进行原子操作或者附加 MySQL 函数来操作的字段可以放到 JSON/PROTOBUF/THRIFT/MSGPACK 格式的 DATA/EXTRA 字段中。
解读：可以避免频繁地改表。

（*）存储层不要存储多余的数据
解读：协议层用的数据（譬如 key），可以通过 id 计算出来的（key = user-<id>@bytedance.com），可以不要 key 这个字段。



（11）必须把字段定义为 NOT NULL 并且提供默认值
解读：

a）null 的列使索引 / 索引统计 / 值比较都更加复杂，对 MySQL 来说更难优化

b）null 这种类型 MySQL 内部需要进行特殊处理，增加数据库处理记录的复杂性；同等条件下，表中有较多空字段的时候，数据库的处理性能会降低很多

c）null 值需要更多的存储空，无论是表还是索引中每行中的 null 的列都需要额外的空间来标识

d）对 null 的处理时候，只能采用 is null 或 is not null，而不能采用 =、in、<、<>、!=、not in 这些操作符号。如：where name!=’shenjian’，如果存在 name 为 null 值的记录，查询结果就不会包含 name 为 null 值的记录

 

（12）禁止使用 TEXT、BLOB 类型

解读：会浪费更多的磁盘和内存空间，非必要的大量的大字段查询会淘汰掉热数据，导致内存命中率急剧降低，影响数据库性能

 

（13）禁止使用小数存储货币

解读：使用整数吧，小数容易导致钱对不上

 

（14）必须使用 varchar(20) 存储手机号

解读：

a）涉及到区号或者国家代号，可能出现 +-()

b）手机号会去做数学运算么？

c）varchar 可以支持模糊查询，例如：like“138%”

 

（15）禁止使用 ENUM，可使用 TINYINT 代替

解读：

a）增加新的 ENUM 值要做 DDL 操作

b）ENUM 的内部实际存储就是整数，你以为自己定义的是字符串？

 

五、索引设计规范

（16）单表索引建议控制在 5 个以内

 

（17）单索引字段数不允许超过 5 个

解读：字段超过 5 个时，实际已经起不到有效过滤数据的作用了

 

（18）禁止在更新十分频繁、区分度不高的属性上建立索引

解读：

a）更新会变更 B+ 树，更新频繁的字段建立索引会大大降低数据库性能

b）“性别” 这种区分度不大的属性，建立索引是没有什么意义的，不能有效过滤数据，性能与全表扫描类似

 

（19）建立组合索引，必须把区分度高的字段放在前面

解读：能够更加有效的过滤数据

 

六、SQL 使用规范

（20）禁止使用 SELECT *，只获取必要的字段，需要显示说明列属性

解读：

a）读取不需要的列会增加 CPU、IO、NET 消耗

b）不能有效的利用覆盖索引

c）使用 SELECT * 容易在增加或者删除字段后出现程序 BUG

 

（21）禁止使用 INSERT INTO t_xxx VALUES(xxx)，必须显示指定插入的列属性

解读：容易在增加或者删除字段后出现程序 BUG

 

（22）禁止使用属性隐式转换

解读：SELECT uid FROM t_user WHERE phone=13812345678 会导致全表扫描，而不能命中 phone 索引，猜猜为什么？（这个线上问题不止出现过一次）

 

（23）禁止在 WHERE 条件的属性上使用函数或者表达式

解读：SELECT uid FROM t_user WHERE from_unixtime(day)>='2017-02-15' 会导致全表扫描

正确的写法是：SELECT uid FROM t_user WHERE day>= unix_timestamp('2017-02-15 00:00:00')

 

（24）禁止负向查询，以及 % 开头的模糊查询

解读：

a）负向查询条件：NOT、!=、<>、!<、!>、NOT IN、NOT LIKE 等，会导致全表扫描

b）% 开头的模糊查询，会导致全表扫描

 

（25）禁止大表使用 JOIN 查询，禁止大表使用子查询

解读：会产生临时表，消耗较多内存与 CPU，极大影响数据库性能

 

（26）禁止使用 OR 条件，必须改为 IN 查询

解读：旧版本 Mysql 的 OR 查询是不能命中索引的，即使能命中索引，为何要让数据库耗费更多的 CPU 帮助实施查询优化呢？

 

（27）应用程序必须捕获 SQL 异常，并有相应处


1. phone 字符串和整形比较时，phone 会被转换为浮点型，导致不能使用到 phone 上的索引（可以理解为 phone 上有函数调用）

2. phone 的值为 13812345678abcd 时，会被转换为 13812345678，判等成立，导致 bug