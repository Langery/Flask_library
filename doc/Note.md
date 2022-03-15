## Note

&emsp;&emsp;备注说明文件 & 备忘录

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