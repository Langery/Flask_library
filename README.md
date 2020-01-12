## Flask_library

![](https://img.shields.io/badge/Language-Flask-green)
[![](https://img.shields.io/bitbucket/issues-raw/Langery/Flask_library)](https://github.com/Langery/Flask_library/issues)

> 启动

``` python
  python3 server.py
```

### Flask 后台库 Menu

- <a href="#idea">idea</a>
- <a href="#advice">advice</a>
- <a href="#need-to-do">need to do</a>
- <a href="#finished">finished</a>
- <a href="#notes">Notes</a>
- <a href="#mysql-order">MySQL Order</a>
- <a href="#links">Links</a>
- <a href="#change-log">Change Log<a>

> 项目说明

&emsp;&emsp;暂无~

> [idea](#idea)

- [ ] 针对多种请求方式需要单独做处理
  - [ ] get
  - [ ] put
  - [x] post
  - [ ] delete
- [ ] ORM 数据处理
- [x] 连接到数据库
  - [x] 数据校验
  - [ ] 数据库做表链接
    - [ ] **创建表关联**
- [ ] 对数据库做数据存储和处理
 - [x] 信息存储格式处理
- [ ] 表单数据处理
- [ ] 日历
  - [ ] 存/取
  - [x] 存储格式和请求方式
  - [x] 数据表建立
  - [x] 返回格式待优化
   - [x] json
   - [ ] 应该以天为索引，便于界面渲染（结合前端内容考虑~）
  - [x] 获取到的用户为 id，需要做二次过滤
  - [ ] 好友信息渲染
- [ ] 图像数据存储
  - [ ] svg
  - [ ] canvas
- [ ] 视图数据存储及处理
  - [ ] 三维视图数据
- [x] Blueprint
  - [ ] 权限
    - [ ] 针对不同的权限进行路由配置
  - [ ] 功能
    - [ ] 将之前的已开发模块嵌入到蓝图框架中，进行近一步优化
    - [x] Calendar
  - [ ] 抛弃原有的开发模式概念，将整体开发模块再次细化
- [ ] 创建几个数据仓库
  - [ ] 分类
    - [ ] 垃圾文件仓库
    - [ ] 用户数据仓库
    - [ ] 分析数据仓库
  - [ ] 数据收集以及数据分析
  - [ ] 用户数据分析处理
- [ ] 待续...

> [advice](#advice)

- [ ] flask 配置文件
  - [x] 数据库链接写成方法
- [x] Connection 静态变量
- [X] connection 连接池（pymysql 自带连接池）
- [ ] 缓存区（如：redis）
- [ ] 安全性监控
- [ ] ~~Hibemate~~
- [ ] Powerdesigner
- [ ] 雪花算法
- [x] 分支开发
  - [x] 合并 & 复查代码（~~反正是一个人开发干嘛建分支？？~~）
- [ ] 多异步处理
- [ ] 待续...

> [need to do](#need-to-do)

- [x] 创建总入口，然后通过总入口做请求下发
- [ ] 登录注册
  - [ ] 密码校验
  - [ ] 用户信息校验
  - [ ] 用户第三发校验
- [ ] 打包/发版
- [x] 错误日志输出
  - [x] 错误日志配置
  - [ ] 错误日志输出
  - [ ] 错误日志归档 & 定期分类
- [ ] 测试
  - [ ] 单元测试
  - [ ] 本地测试
  - [ ] 模块测试
- [x] 模糊查询
- [ ] 待续...

> [finished](#finished)

- [x] 实现前端对后台的链接和通讯
- [x] 实现登录和注册接口
- [x] 封装独立 Class 类，并实现调用
- [x] 实现外网访问
- [x] 后台数据返回以对象形式返回
- [x] 后台数据返回以 JSON 形式返回
- [x] 基础的模糊查询
- [ ] 待续...

### [Notes](#notes)

1. 登录注册都为 POST 请求方式，传入格式为 json 格式
2. Address already in use
``` python
  sudo lsof -i:5000
  kill 进程编号(Number)
```
3. 外网访问
``` python
  # 修改 app.run
  app.run(host='0.0.0.0', port=5000)
  # 获取本机 ip 即可访问
```
4. server.py 为主请求入口，所有的请求都通过此文件进行下发

5. 变量规则

    - string  文本
    - int  正整数
    - float  正浮点数
    - path  类似 string 但是包含斜杆
    - uuid UUID 字符串
6. log Folder

### [MySQL order](#mysql-order)

1. 删除一条数据
``` sql
  DELETE FROM tablename WHERE NAME = 'abc'
```
2. 查询
``` sql
  SELECT columnname FROM tablename
  -- 通过 username 找 id
  SELECT id FROM tablename WHERE username = 'xxx'
  -- 查询一段时间的内容
  SELECT * FROM tablename WHERE startNum < columnname < endNum
```
3. 添加
``` sql
  INSERT INTO tablename VALUES (value)
  INSERT INTO tablename (columnname...) VALUES (value...)
```
4. 修改
```sql
  UPDATE tablename SET columnname = 'newValue' WHERE columnvalue = 'xxx'
```

### [Links](#links):

1. [Python Flask数据库连接池](https://www.cnblogs.com/supery007/p/8206442.html)
2. [Python编程：flask-cors模块解决Flask跨域请求Cross-Origin问题](https://blog.csdn.net/mouday/article/details/85219076)
3. [Flask了解和基础配置及使用](https://www.jianshu.com/p/997e68df40e3)
4. [Flask配置参数简单说明](https://blog.csdn.net/qq_42517220/article/details/88687341)
5. [flask配置文件](https://www.jianshu.com/p/6b9a77f1c0cf)
6. [Deleting a Git commit](https://www.jianshu.com/p/073acdc79c7b)
7. [flask项目结构（三）使用蓝图](https://www.cnblogs.com/jackadam/p/8684148.html)
8. [flask SQLAlchemy模型属性和MySQL数据库数据类型对应关系](https://www.jianshu.com/p/0b23e197e7e0)
9. [【Flask】Sqlalchemy 常用数据类型](https://www.cnblogs.com/chen0427/p/8627587.html)

### [Change Log](#change-log)

> 2019-12-17

1. 修改 data 处理位置，传给指定函数为 data 整体，在指定函数内做对应参数的获取和处理
2. 增加日志事件获取事件（待完成）

> 2019-12-18

1. 模糊查询未解决...问题存在于转义字符的处理...

> 2019-12-20

1. 解决模糊查询，已获取查询到的具体数据
2. 目前数据格式不规范，待优化
3. 目前用户信息只是 id，未拿到对应的用户名，待解决

> 2019-12-23

1. 解决通过用户 id 拿取到用户姓名
2. 实现单独函数创建于调用，基于同一个 Class 下

> 2019-12-24

1. 添加蓝图模块，还未细化蓝图内部功能，待开发...
2. 增加添加查询模块
3. common 的思考
4. 待修改获取日历信息的返回数据

> 2019-12-25

1. 处理蓝图里的 config 问题，解决日历接口的蓝图划分
2. 导出数据库的设计表

> 2020-01-04

1. 重新设计数据库解构

> 2020-01-06

1. 完成多个参数查询拼接
2. 创建测试文件—— demo.py

> 2020-01-12

1. 完成时间段查询，重新定义新的数据请求
