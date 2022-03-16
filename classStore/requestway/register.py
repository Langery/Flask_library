from flask import request
# make_response
import json
from classStore.server.dataLab import SQLFun

class Register():
  def __init__(self):
    print('success use register')
    data = request.get_data()
    self.data = data
  def findHad(self, config):
    data = json.loads(self.data)
    username = data['username']
    nickname = data['nickname']
    password = data['password']
    # print(username, nickname, password)
    conn = config.connection()
    cursor = conn.cursor()

    regSQL = SQLFun('*', 'usertable')

    sqlUser = regSQL.select('username')
    sqlNick = regSQL.select('nickname')

    rowUser = cursor.execute(sqlUser, username)
    rowNick = cursor.execute(sqlNick, nickname)

    # print(rowUser, rowNick)
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
      res['backData'] = False
      return res
    else:
      addUser = regSQL.add('username', 'password', 'nickname')
      rowAdd = cursor.execute(addUser, [username, password, nickname])
      conn.commit()
      if rowAdd >= 1:
        addData = True
      else:
        addData = False
      res = {}
      res['backData'] = addData
      return res
