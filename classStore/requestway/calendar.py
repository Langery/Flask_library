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
      msg = '当前用户不存在'
      backSend = {}
      backSend['msg'] = msg
      backSend['status'] = 0
      return json.dumps(backSend, ensure_ascii=False)
    else:
      # find id by username
      tableSQL = SQLFun('id', 'dbusers')
      sqlUserId = tableSQL.select('name')
      cursor.execute(sqlUserId, username)
      getRetData = cursor.fetchall()
      getUserId = getRetData[0][0]
      # 通过 ID 去事件表查是否有数据
      eventSQL = SQLFun('event', 'event')
      sqlEvent = eventSQL.select('userId')
      cursor.execute(sqlEvent, getUserId)
      getEventData = cursor.fetchall()
      print(getEventData)
      backArr = {
        'msg': getEventData[0][0]
      }
      backEventData = {}
      backEventData['data'] = backArr
      backEventData['status'] = '200'
      return json.dumps(backEventData, ensure_ascii=False)
    # select SQL
    # calSQL = SQLFun('*', 'event')
    # sqlUerName = selectSQL.select('userId')
  
  def getTime(self, config):
    # get time to select
    print('success link get time')

  def addInfo(self, config):
    # user add info into list
    print('success add info into list')
