import json, pymysql, config
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_cors import CORS
from DBUtils.PersistentDB import PersistentDB

# import
from classStore.first import First
from classStore.login import Login
from classStore.register import Register
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
  # print(select['username'])
  # if not(select['username']):
  #   # false
  #   return False
  # if not(select['password']):
  #   # false
  #   return False
  return select

@app.route('/register', methods=['POST'])
def register():
  reg = Register()
  findHad = reg.findHad(config)
  print(findHad)
  return findHad

  # add
  # find = 'insert into login(name, pwd, nickname) values(%s, %s, %s)'
  # endFind = cursor.execute(find, [username, password, ''])
  # print(endFind)

if __name__ == '__main__':
  app.run()