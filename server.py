import json, config
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_cors import CORS
from DBUtils.PersistentDB import PersistentDB

# import
from classStore.first import First # 测试接口
from classStore.login import Login
from classStore.register import Register
from classStore.calendar import Calendar
from classStore.server.dataLab import POOL

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(config.Config)
SQLConfig = config.SQLConfig

getPool = POOL()
config = getPool.config(SQLConfig)
print(config)

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
  print(select)
  return select

@app.route('/register', methods=['POST'])
def register():
  reg = Register()
  findHad = reg.findHad(config)
  print(findHad)
  return findHad

@app.route('/canlendar', method=['POST'])
def getUser():
  cal = Calendar()
  getUser = cal.getUser(config)
  return 'get user success'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)