from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Login():
  def __init__(self):
    print('success use login')
    data = request.get_data()
    username = json.loads(data)['username']
    password = json.loads(data)['password']
    print(username, password)
    self.username = username
    self.password = password
  def select(self, config):
    username = self.username
    password = self.password
    conn = config.connection()
    cursor = conn.cursor()
    # select
    loginSQL = SQLFun('*', 'users')
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
    # res['username'] = nameData
    # res['password'] = pwdData
    if nameData and pwdData:
      res['backData'] = True
    else:
      res['backData'] = False
    print(res)
    return json.dumps(res)
    # return res
