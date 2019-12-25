import json, config
import logging
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_cors import CORS
from DBUtils.PersistentDB import PersistentDB

# import
from classStore.requestway.first import First # 测试接口
from classStore.requestway.login import Login
from classStore.requestway.register import Register
# from classStore.requestway.calendar import Calendar
# data lab
from classStore.server.dataLab import POOL

# import blueprint
from blueprintStore.admin.adminview import *
from blueprintStore.user.userview import *
from blueprintStore.calendar.calendarview import *

app = Flask(__name__)

CORS(app, supports_credentials=True)

app.config.from_object(config.Config)
SQLConfig = config.SQLConfig

getPool = POOL()
config = getPool.config(SQLConfig)
print(config)

# Blueprint
app.register_blueprint(admin_blue, url_prefix = '/admin')
app.register_blueprint(user_blue, url_prefix = "/user")
app.register_blueprint(calendar_blue, url_prefix="/calendar")

# 错误日志处理
# 1. 配置
handler = logging.FileHandler('log/app.log', encoding='UTF-8')
# 2. 设置日志文件
logging_format = logging.Formatter(
  '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
)
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

# 测试接口
@app.route('/first', methods=['GET'])
def first():
  res = First()
  first = res.first()
  print(first)
  return first

@app.errorhandler(404)
def page_not_found(error):
  return 'This address does not exist', 404

'''
POST way to save data
'''
@app.route('/login', methods=['POST'])
def login():
  res = Login()
  select = res.select(config)
  # app.logger.info(select)
  return select

@app.route('/register', methods=['POST'])
def register():
  reg = Register()
  findHad = reg.findHad(config)
  # app.logger.info(findHad)
  return findHad

# @app.route('/calendar/user', methods=['POST'])
# def getUser():
#   cal = Calendar()
#   getUser = cal.getUser(config)
#   # app.logger.info(getUser)
#   return getUser
#
# # get show list
# @app.route('/calendar/list', methods=['POST'])
# def getShowList():
#   cal = Calendar()
#   getShowList = cal.getList(config)
#   return getShowList
#
# @app.route('/calendar/addInfo', methods=['POST'])
# def addInfo():
#   cal = Calendar()
#   addInfo = cal.addInfo(config)
#   return addInfo

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
