import json, pymysql, config
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_cors import CORS
from DBUtils.PersistentDB import PersistentDB

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(config.Config)
SQLConfig = config.SQLConfig

POOL = PersistentDB(
  creator = pymysql, # use data model
  maxusage = None, # used more times
  setsession = [], # the order list before start
  ping = 0, # check MySQL server is available
  closeable = False, # ignored the `conn.close()` ,
  threadlocal = None, # save the link object
  host = SQLConfig.host,
  port = SQLConfig.port,
  user = SQLConfig.user,
  password = SQLConfig.password,
  database = SQLConfig.database,
  charset = SQLConfig.charset
)

# 测试接口
@app.route('/first', methods=['GET'])
def first():
  print('success')
  name = request.args.get('name')
  print(request)
  if name:
    print(name)
    res = make_response('Hello Ajax ' + name)
    return res
  # return 'First message'

'''
POST way to save data
'''
@app.route('/login', methods=['POST'])
def login():
  print('login')
  conn = POOL.connection()

  username = request.form.get('name')
  password = request.form.get('password')
  print(username, password)
  cursor = conn.cursor()
  # select
  sqlName = 'SELECT * FROM login where name = %s'
  sqlPwd = 'SELECT * FROM login where pwd = %s'
  # add
  # find = 'insert into login(name, pwd, nickname) values(%s, %s, %s)'
  # endFind = cursor.execute(find, [username, password, ''])
  # print(endFind)
  rowName = cursor.execute(sqlName,[username])
  rowPws = cursor.execute(sqlPwd,[password])
  conn.commit()
  # conn.close() # false closure
  if rowName >= 1:
    nameData = True
  else:
    nameData = False
  if rowPws >= 1:
    pwdData = True
  else:
    pwdData = False
  res = {}
  res['username'] = nameData
  res['password'] = pwdData
  print(res)
  return json.dumps(res)

@app.route('/register', methods=['POST'])
def register():
  print('register')
  
if __name__ == '__main__':
  app.run()