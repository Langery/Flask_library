import json, config
import logging
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_cors import CORS
from DBUtils.PersistentDB import PersistentDB

# Blueprint
# from flask import Blueprint
# main = Blueprint('main', __name__)
# @main.route()

# import
from classStore.requestway.first import First # 测试接口
from classStore.requestway.login import Login
from classStore.requestway.register import Register
from classStore.requestway.calendar import Calendar
# data lab
from classStore.server.dataLab import POOL

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(config.Config)
SQLConfig = config.SQLConfig

getPool = POOL()
config = getPool.config(SQLConfig)
print(config)

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

'''
POST way to save data
'''
@app.route('/login', methods=['POST'])
def login():
  res = Login()
  select = res.select(config)
  # print(select)
  app.logger.info(select)
  return select

@app.route('/register', methods=['POST'])
def register():
  reg = Register()
  findHad = reg.findHad(config)
  # print(findHad)
  app.logger.info(findHad)
  return findHad

@app.route('/canlendar', methods=['POST'])
def getUser():
  cal = Calendar()
  getUser = cal.getUser(config)
  app.logger.info(getUser)
  return 'get user success'
  # return getUser

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)