from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Login():
  def __init__(self, config):
    print('success')
    data = request.get_data()
    username = json.loads(data)['username']
    password = json.loads(data)['password']
    print(username, password)
    self.config = config
    self.username = username
    self.password = password
  def select(self):
    config = self.config
    username = self.username
    password = self.password
    conn = config.connection()
    cursor = conn.cursor()
    # select
    loginSQL = SQLFun('*', 'login')
    sqlName = loginSQL.select('name')
    sqlPwd = loginSQL.select('pwd')
    rowName = cursor.execute(sqlName,[username])
    rowPws = cursor.execute(sqlPwd,[password])
    print(rowName, rowPws)
    conn.commit()
    # conn.close() # false closure
    if rowName >= 1:
      nameData = True
    else:
      nameData = False
    if rowPws >= 1:
      pwdData = True
    else:
      pwdData = False
    res = {}
    res['username'] = nameData
    res['password'] = pwdData
    print(res)
    return json.dumps(res)
    # return res
