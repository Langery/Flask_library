from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Login():
  def __init__(self):
    print('success use login')
    data = request.get_data()
    self.data = data
  def select(self, config):
    data = json.loads(self.data)
    username = data['username']
    password = data['password']
    conn = config.connection()
    cursor = conn.cursor()
    # select
    loginSQL = SQLFun('*', 'dbusers')
    sqlName = loginSQL.select('nickname')
    sqlPwd = loginSQL.select('pwd')
    rowName = cursor.execute(sqlName, username)
    rowPws = cursor.execute(sqlPwd, password)
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
