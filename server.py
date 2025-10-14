import json, config, os
from pickle import TRUE
import logging
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_cors import CORS
from DBUtils.PersistentDB import PersistentDB

# import
from classStore.requestway.first import First # 测试接口
from classStore.requestway.login import Login
from classStore.requestway.register import Register

# demo
# from lab.demo import RegisterDemo;

# ListTree
from classStore.requestway.pages_server.list_table import ListTable
# upload
from classStore.requestway.pages_server.upload_images import Upload

# data lab
from classStore.server.__init__ import POOL;

# import blueprint
from blueprintStore.admin.adminview import *;
from blueprintStore.user.userview import *;

logging.basicConfig(level=logging.DEBUG);

# >>> def app
app = Flask(__name__);

CORS(app, supports_credentials=True);

# from_config 配置项设置
app.config.from_object(config.Config);
SQLConfig = config.SQLConfig;
app.config.from_mapping(
  SECRET_KEY = 'dev'
)

getPool = POOL();
config = getPool.config(SQLConfig);
print(config);

# Blueprint
# 访问：127.0.0.1:5000/admin
# 访问：127.0.0.1:5000/user
app.register_blueprint(admin_blue, url_prefix = '/admin')
app.register_blueprint(user_blue, url_prefix = "/user")


# 测试接口 ====================================================> start
# address: http://127.0.0.1:5000/first?name=xxx
@app.route('/first', methods=['GET'])
def first():
  res = First()
  first = res.first()
  print('server ' + first)
  return first
# 测试接口 =====================================================> end

@app.errorhandler(404)
def page_not_found(error):
  return 'This address does not exist ~~', 404

'''
POST way to save data
'''
# 登录接口 =====================================================> start
@app.route('/login', methods=['POST'])
def login():
  res = Login()
  select = res.select(config)
  # app.logger.info(select)
  return select

# 登录接口 =====================================================> end

# 注册接口 =====================================================> start
@app.route('/register', methods=['POST'])
def register():
  reg = Register()
  findHad = reg.findHad(config)
  # app.logger.info(findHad)
  return findHad
# 注册接口 =====================================================> end

# 注销接口 =====================================================> start
@app.route('/logout')
def logout():
  return 'This is logout!'
# 注销接口 =====================================================> end

# 首页接口 =======================================================> start

# 列表树接口
@app.route('/getTree', methods=['POST'])
def listTree():
  res = ListTable()
  getTree = res.getTree(config)
  # app.logger.info(getTree)
  return getTree

# 获取列表详细信息接口
@app.route('/getListInfor', methods=['GET'])
def listInfor():
  res = ListTable();
  listInfor = res.listInfor(config);
  # app.logger.info(getTree)
  return listInfor;

# 上传图片接口
@app.route('/uploadImg', methods=['POST'])
def uploadsImage():
  res = Upload()
  uploadImg = res.uploadImg(config)
  # app.logger.info(getTree)
  return uploadImg

# 首页接口 =======================================================> ends

if __name__ == '__main__':
  # 错误日志处理
  # 1. 配置
  handler = logging.FileHandler('log/app.log', encoding='UTF-8')
  # 2. 设置日志文件
  logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
  )
  handler.setFormatter(logging_format)

  app.logger.addHandler(handler)
  app.run(host='127.0.0.1', port=5000)
