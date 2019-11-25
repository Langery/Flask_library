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
    # select SQL
    calSQL = SQLFun('*', 'event')
    # get user id
    sqlUserId = calSQL.select('userId')
    print(sqlUserId)

