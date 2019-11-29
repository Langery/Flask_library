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
    username = self.username
    # find user id SQL
    selectSQL = SQLFun('*', 'users')
    # get user id
    # sqlUserId = calSQL.select('userId')
    sqlUserId = selectSQL.select('id')
    print(sqlUserId)
    # select SQL
    calSQL = SQLFun('*', 'event')
    sqlUerName = selectSQL.select('userId')
  
  def getTime(self, config):
    # get time to select
    print('success link get time')

  def addInfo(self, config):
    # user add info into list
    print('success add info into list')
