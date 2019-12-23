from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun
from classStore.server.dataLab import POOL

class Calendar():
  def __init__(self):
    print('sucess user calendar')
    data = request.get_data()
    self.data = data
  def getUser(self, config):
    print('success get user')
    # username = self.username
    username = json.loads(self.data)['username']
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

  def getList(self, config):
    print('get list info')
    # sendtime = self.sendtime
    sendtime = json.loads(self.data)['time']
    conn = config.connection()
    cursor = conn.cursor()
    ListSQL = SQLFun('*', 'event')
    sqlEventTime = ListSQL.like('isNew', sendtime)
    print('sqlEventTime:' + sqlEventTime)
    # cursor.execute(sqlEventTime, [sendtime])
    cursor.execute(sqlEventTime)
    # SELECT * FROM event WHERE isNew LIKE '2019-12%'
    EventSel = cursor.fetchall()
    print(EventSel)
    print(type(EventSel))
    conn.commit()
    backInfo = []
    for eventOne in EventSel:
      newObj = {
        'userId': self.getName(cursor, eventOne[1]),
        'event': eventOne[2],
        'createtime': eventOne[3],
        'status': eventOne[6],
        'newtime': eventOne[7],
      }
      backInfo.append(newObj)
    return json.dumps(backInfo, ensure_ascii=False)

  def getName(self, cursor, data):
    userSQL = SQLFun('nickname', 'dbusers')
    sqlUserName = userSQL.select('id')
    cursor.execute(sqlUserName, [data])
    NameSel = cursor.fetchall()
    return NameSel[0][0]


  def getTime(self, config):
    # get time to select
    print('success link get time')

  def addInfo(self, config):
    # user add info into list
    print('success add info into list')
