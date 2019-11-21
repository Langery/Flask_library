from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Register():
  def __init__(self):
    print('success use register')
    data = request.get_data()
    username = json.loads(data)['username']
    password = json.loads(data)['password']
    nickname = json.loads(data)['nickname']
    print(username, password, nickname)
    self.username = username
    self.password = password
    self.nickname = nickname
  def findHad(self, config):
    username = self.username
    nickname = self.nickname
    password = self.password
    conn = config.connection()
    cursor = conn.cursor()
    # find in SQL
    regSQL = SQLFun('*', 'users')
    
    sqlUser = regSQL.select('name')
    sqlNick = regSQL.select('nickname')

    rowUser = cursor.execute(sqlUser, [username])
    rowNick = cursor.execute(sqlNick, [nickname])
    
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