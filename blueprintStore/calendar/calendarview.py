import config
from flask import Blueprint
from classStore.requestway.calendar import Calendar

from classStore.server.dataLab import POOL

calendar_blue = Blueprint('calendar', __name__)

getPool = POOL()
SQLConfig = config.SQLConfig
app_config = getPool.config(SQLConfig)

@calendar_blue.route('/user', methods=['POST'])
def getUser():
  cal = Calendar()
  getUser = cal.getUser(app_config)
  return getUser

@calendar_blue.route('/list', methods=['POST'])
def getShowList():
  cal = Calendar()
  getShowList = cal.getList(app_config)
  return getShowList

@calendar_blue.route('/addInfo', methods=['POST'])
def addInfo():
  cal = Calendar()
  addInfo = cal.addInfo(app_config)
  return addInfo
