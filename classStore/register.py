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
    conn = config.connection()
    cursor = conn.cursor()
    # find in SQL
    regSQL = SQLFun('*', 'login')
    sqlUser = regSQL.select('name')
    sqlNick = regSQL.select('nickname')
    rowUser = cursor.execute(sqlUser, [username])
    rowNick =cursor.execute(sqlNick, [nickname])
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
    res['username'] = nameData
    res['nickname'] = nickData
    print(res)
    return json.dumps(res)