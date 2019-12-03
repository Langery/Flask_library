## Flask_library

> 启动

``` python
  python3 server.py
```

### Flask 后台库

> idea

- [ ] 针对多种请求方式需要单独做处理
  - [ ] get
  - [ ] put
  - [x] post
  - [ ] delete
- [x] 连接到数据库
  - [x] 数据校验
  - [ ] 数据库做表链接
    - [ ] **创建表关联**
- [ ] 对数据库做数据存储和处理
- [ ] 表单数据处理
- [ ] 日历
  - [ ] 存/取
  - [ ] 存储格式和请求方式
  - [ ] 数据表建立
- [ ] Blueprint
  - [ ] 针对不同的权限进行路由配置
- [ ] 待续...

> advice
- [ ] flask 配置文件
  - [x] 数据库链接写成方法
- [x] Connection 静态变量
- [X] connection 连接池（pymysql 自带连接池）
- [ ] 缓存区（如：redis）
- [ ] 安全性监控
- [ ] Hibemate
- [ ] Powerdesigner
- [ ] 待续...

> need to do

- [x] 创建总入口，然后通过总入口做请求下发
- [ ] 打包/发版
- [x] 错误日志输出
  - [x] 错误日志配置
  - [x] 错误日志输出
- [ ] 测试
  - [ ] 单元测试
  - [ ] 本地测试
  - [ ] 模块测试
- [ ] 数据收集以及数据分析
- [ ] 用户数据分析处理
- [ ] 待续...

> finished

- [x] 实现前端对后台的链接和通讯
- [x] 实现登录和注册接口
- [x] 封装独立 Class 类，并实现调用
- [x] 实现外网访问
- [ ] 待续...

### Notes

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
4. server.py 为主要请求入口，所有的请求都通过此文件进行下发

5. 变量规则

    - string  文本
    - int  正整数
    - float  正浮点数
    - path  类似 string 但是包含斜杆
    - uuid UUID 字符串

### MySQL order

1. 删除一条数据
``` sql
  DELETE FROM tablename WHERE NAME = 'abc'
```
2. 查询
``` sql
  SELECT columnname FROM tablename
  -- 通过 username 找 id
  SELECT id FROM tablename WHERE username = 'xxx'
```

### Links:

1. [Python Flask数据库连接池](https://www.cnblogs.com/supery007/p/8206442.html)
2. [Python编程：flask-cors模块解决Flask跨域请求Cross-Origin问题](https://blog.csdn.net/mouday/article/details/85219076)
3. [Flask了解和基础配置及使用](https://www.jianshu.com/p/997e68df40e3)
4. [Flask配置参数简单说明](https://blog.csdn.net/qq_42517220/article/details/88687341)
5. [flask配置文件](https://www.jianshu.com/p/6b9a77f1c0cf)
6. [Deleting a Git commit](https://www.jianshu.com/p/073acdc79c7b)
7. [flask项目结构（三）使用蓝图](https://www.cnblogs.com/jackadam/p/8684148.html)
