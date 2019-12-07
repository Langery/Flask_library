## 思路草稿纸

&emsp;&emsp;用于记录思路，此文件不删除，用于后期追踪思路

### 登录注册

> 登录

1. 获取前端拿到的数据
    - username
    - password
2. username 与后台做查询，确定是否有此数据
    - 如果有此数据，对密码做校验
    - 如果没有此数据，返回前端 False ，前端对用户做对应提示
3. password 与后台做查询
    - yes，验证通过
    - no，返回密码错误，验证重新输入
    ~~* 注：如果一开始用户名正确，则直接跳过用户名，验证密码~~

> 日历信息处理

1. 按照一个月的信息做数据存储，然后对某一天的数据做对象查询
    - 日期格式：yyyy-mm-dd hh:mm (string)
    - 数据格式：json
    - 对象内容数据：objcet
2. 如果是按照年的方式的话需要逐层过滤，获取到指定的日期

### 草稿

1. server.py
``` python
	@app.route('/login', methods=['POST'])
	def login():
		res = Login()
		select = res.select(config)
		print(select)
		# print(select['username'])
		# if not(select['username']):
		#   # false
		#   return False
		# if not(select['password']):
		#   # false
		#   return False
		return select
```