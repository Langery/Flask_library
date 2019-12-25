from flask import request, make_response
import json
from classStore.server.dataLab import SQLFun

class Calendar():
  def __init__(self):
    print('sucess user calendar')
    data = request.get_data()
    self.data = data
  def getUser(self, config):
    print('success get user')
    username = json.loads(self.data)['username']
    conn = config.connection()
    cursor = conn.cursor()
    # find user id SQL
    selectSQL = SQLFun('*', 'dbusers')
    # get user id
    sqlUserName = selectSQL.select('nickname')
    hadUserId = cursor.execute(sqlUserName, username)
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
      sqlUserId = tableSQL.select('nickname')
      cursor.execute(sqlUserId, username)
      getRetData = cursor.fetchall()
      getUserId = getRetData[0][0]
      # 通过 ID 去事件表查是否有数据
      eventSQL = SQLFun('event', 'event')
      sqlEvent = eventSQL.select('userId')
      cursor.execute(sqlEvent, getUserId)
      getEventData = cursor.fetchall()
      backArr = {
        'msg': getEventData[0][0]
      }
      backEventData = {}
      backEventData['data'] = backArr
      backEventData['status'] = '200'
      return json.dumps(backEventData, ensure_ascii=False)

  def getList(self, config):
    print('get list info')
    data = json.loads(self.data)
    sendtime = data['time']
    conn = config.connection()
    cursor = conn.cursor()
    ListSQL = SQLFun('*', 'event')
    sqlEventTime = ListSQL.like('isNew', sendtime)
    # cursor.execute(sqlEventTime, [sendtime])
    cursor.execute(sqlEventTime)
    # SELECT * FROM event WHERE isNew LIKE '2019-12%'
    EventSel = cursor.fetchall()
    conn.commit()
    backInfo = []
    # 待修改
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
    cursor.execute(sqlUserName, data)
    NameSel = cursor.fetchall()
    return NameSel[0][0]

  # Not for the time being
  def getTime(self, config):
    # get time to select
    print('success link get time')

  def addInfo(self, config):
    # nickname, create time, info
    '''
      data = {
        userId: ''
        time: '',
        username: '',
        info: '',
        status: ''
      }
    '''
    data = json.loads(self.data)
    userId = data['userId']
    createtime = data['time']
    username = data['username']
    status = data['status']
    info = data['info']
    conn = config.connection()
    cursor = conn.cursor()
    addSQL = SQLFun('*', 'event')
    sqlInfoAdd = addSQL.add('userId', 'event', 'createTime', 'updaeTime', 'deleteTime', 'status', 'isNew')
    rowAddInfo = cursor.execute(userId, info, createtime, '-1', '-1', status, createTime)
    print(rowAddInfo)
    newShowInfo = cursor.fetchall()
    print(newShowInfo)
    # user add info into list
    print('success add info into list')
