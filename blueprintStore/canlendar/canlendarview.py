from flask import Blueprint
from classStore.requestway.calendar import Calendar
from flask import current_app

canlendar_blue = Blueprint('canlendar', __name__)

@canlendar_blue.route('/user', methods=['POST'])
def getUser():
  cal = Calendar()
  getUser = cal.getUser(current_app.config)
  return getUser

@canlendar_blue.route('/list', methods=['POST'])
def getShowList():
  cal = Calendar()
  print(current_app.config)
  getShowList = cal.getList(current_app.config)
  return getShowList

@canlendar_blue.route('/addInfo', methods=['POST'])
def addInfo():
  cal = Calendar()
  addInfo = cal.addInfo(config)
  return addInfo
