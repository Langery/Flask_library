from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Register():
  def __init__(self):
    print('success use register')
    data = request.get_data()
    self.data = data
  def findHad(self, config):
    username = json.loads(self.data)['username']
    nickname = json.loads(self.data)['nickname']
    password = json.loads(self.data)['password']
    conn = config.connection()
    cursor = conn.cursor()
    # find in SQL
    regSQL = SQLFun('*', 'dbusers')

    sqlUser = regSQL.select('name')
    sqlNick = regSQL.select('nickname')

    rowUser = cursor.execute(sqlUser, username)
    rowNick = cursor.execute(sqlNick, nickname)

    print(rowUser, rowNick)
    conn.commit()
    if rowUser >= 1:
      nameData = True
    else:
      nameData = False

    if rowNick >= 1:
      nickData = True
    else:
      nickData = False
    res = {}
    if nameData and nickData:
      # res['username'] = nameData
      # res['nickname'] = nickData
      res['backData'] = False
      print(res)
      return json.dumps(res)
    else:
      addUser = regSQL.add('name', 'pwd', 'nickname')
      print(addUser)
      rowAdd = cursor.execute(addUser, [username, password, nickname])
      print(rowAdd)
      conn.commit()
      if rowAdd >= 1:
        addData = True
      else:
        addData = False
      res = {}
      res['backData'] = addData
      return json.dumps(res)
