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
    getUserback = cal.getUser(app_config)
    return getUserback

@calendar_blue.route('/list', methods=['POST'])
def getShowList():
    cal = Calendar()
    getShowListback = cal.getList(app_config)
    return getShowListback


@calendar_blue.route('/addInfo', methods=['POST'])
def addInfo():
    cal = Calendar()
    addInfoback = cal.addInfo(app_config)
    return addInfoback
