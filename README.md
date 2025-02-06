<div align="center">

## Flask_library

![](https://img.shields.io/badge/Language-Python-green)
[![](https://img.shields.io/bitbucket/issues-raw/Langery/Flask_library)](https://github.com/Langery/Flask_library/issues)

</div>

<div align="center">

[项目说明](#xiang) | [启动](#start) | [idea](#idea) | [advice](#advice) | [need to do](#todo) | [finished](#finished) | [Link](#links)

</div>

## <a id="xiang">项目说明</a>

&emsp;&emsp;Flask 后台库 Menu

## <a id="start">启动</a>

``` python
  python3 server.py
```

## <a id="idea">idea</a>

- [ ] 针对多种请求方式需要单独做处理
  - [x] get
  - [ ] put
  - [x] post
  - [ ] delete
- [ ] ORM 数据处理
- [ ] 数据库图片存储
  - [ ] 图片存入
  - [ ] 图片读取
  - [ ] 图片格式处理
- [x] 连接到数据库
  - [x] 数据校验
  - [ ] 数据库做表链接
    - [ ] **创建表关联**
- [ ] 对数据库做数据存储和处理
 - [x] 信息存储格式处理
- [ ] 表单数据处理
- [ ] ~~日历~~ **[此节点下所有开发暂停或取消]**
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
    - [x] 功能分区
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

## <a id="advice">advice</a>

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
- [ ] 本机部署数据库，将数据库数据结构做存储，确保每次部署到新的电脑时有本地数据可以读取
- [ ] 待续...

## <a id="todo">need to do</a>

- [x] 创建总入口，然后通过总入口做请求下发
- [ ] 登录注册
  - [x] 注册
  - [ ] 密码校验
  - [ ] 用户信息校验
  - [ ] 用户第三发校验
- [ ] 打包/发版
- [x] 错误日志输出
  - [x] 错误日志配置
  - [x] 错误日志输出
  - [ ] 错误日志归档 & 定期分类
- [ ] 测试
  - [ ] 单元测试
  - [ ] 本地测试
  - [ ] 模块测试
- [x] 模糊查询
- [ ] 数据结构 & 算法
- [ ] 待续...

## <a id="finished">finished</a>

- [x] 实现前端对后台的链接和通讯
- [x] 实现登录和注册接口
- [x] 封装独立 Class 类，并实现调用
- [x] 实现外网访问
- [x] 后台数据返回以对象形式返回
- [x] 后台数据返回以 JSON 形式返回
- [x] 基础的模糊查询
- [ ] 待续... --> 转到 [Log 日志](https://github.com/Langery/Flask_library/tree/master/doc/log)

## <a id="links">Links</a>

1. [Python Flask数据库连接池](https://www.cnblogs.com/supery007/p/8206442.html)
2. [Python编程：flask-cors模块解决Flask跨域请求Cross-Origin问题](https://blog.csdn.net/mouday/article/details/85219076)
3. [Flask了解和基础配置及使用](https://www.jianshu.com/p/997e68df40e3)
4. [Flask配置参数简单说明](https://blog.csdn.net/qq_42517220/article/details/88687341)
5. [flask配置文件](https://www.jianshu.com/p/6b9a77f1c0cf)
6. [Deleting a Git commit](https://www.jianshu.com/p/073acdc79c7b)
7. [flask项目结构（三）使用蓝图](https://www.cnblogs.com/jackadam/p/8684148.html)
8. [flask SQLAlchemy模型属性和MySQL数据库数据类型对应关系](https://www.jianshu.com/p/0b23e197e7e0)
9. [【Flask】Sqlalchemy 常用数据类型](https://www.cnblogs.com/chen0427/p/8627587.html)
10. &ensp;[Flask 使用日志](https://www.cnblogs.com/klvchen/p/13754834.html)
11. &ensp;[token 生成详解](https://blog.csdn.net/m0_56477185/article/details/124616865)
12. &ensp;[Flask 中使用 WebSocket 通信](https://blog.csdn.net/WonderThink/article/details/128112042)