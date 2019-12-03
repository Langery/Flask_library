from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Calendar():
  def __init__(self):
    print('sucess user calendar')
    data = request.get_data()
    username = json.loads(data)['username']
    print(username)
    self.username = username
  def getUser(self, config):
    print('success get user')
    username = self.username
    conn = config.connection()
    cursor = conn.cursor()
    # find user id SQL
    selectSQL = SQLFun('*', 'dbusers')
    # get user id
    sqlUserName = selectSQL.select('name')
    print('sqlUserName:' + sqlUserName)
    hadUserId = cursor.execute(sqlUserName, [username])
    print(hadUserId)
    conn.commit()
    if hadUserId < 1:
      # 当前用户不存在
      return False
    else:
      # find id by username
      tableSQL = SQLFun('id', 'dbusers')
      sqlUserId = tableSQL.select('name')
      print(sqlUserId)
      # getUserId = cursor.execute(sqlUserId, username)
      # print(getUserId)
      getRetData = cursor.fetchall()
      print(getRetData)
      print(getRetData[0][0])

    # select SQL
    # calSQL = SQLFun('*', 'event')
    # sqlUerName = selectSQL.select('userId')
  
  def getTime(self, config):
    # get time to select
    print('success link get time')

  def addInfo(self, config):
    # user add info into list
    print('success add info into list')
