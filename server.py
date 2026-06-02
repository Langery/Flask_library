import json
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from flask_cors import CORS
from classStore.server.__init__ import POOL

import config

# import
from classStore.requestway.first import First
from classStore.requestway.login import Login
from classStore.requestway.register import Register

# ListTree
from classStore.requestway.pages_server.list_table import ListTable
# upload
from classStore.requestway.pages_server.upload_images import Upload

# data lab
from classStore.server.__init__ import POOL

# import blueprint
from blueprintStore.admin.adminview import admin_blue
from blueprintStore.user.userview import user_blue

logging.basicConfig(level=logging.DEBUG)

# >>> def app
app = Flask(__name__)

CORS(app, supports_credentials=True)

app.config.from_object(config.Config)
SQLConfig = config.SQLConfig
app.config.from_mapping(SECRET_KEY='dev')

getPool = POOL()
db_config = getPool.config(SQLConfig)
print(db_config)

# Blueprint
app.register_blueprint(admin_blue, url_prefix='/admin')
app.register_blueprint(user_blue, url_prefix='/user')


@app.route('/first', methods=['GET'])
def first():
    res = First()
    first = res.first()
    print('server ' + first)
    return first


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'error': 'This address does not exist'}), 404


@app.route('/login', methods=['POST'])
def login():
    res = Login()
    select = res.select(db_config)
    return select


@app.route('/register', methods=['POST'])
def register():
    reg = Register()
    findHad = reg.findHad(db_config)
    return findHad


@app.route('/logout')
def logout():
    return jsonify({'message': 'This is logout!'})


@app.route('/getTree', methods=['POST'])
def listTree():
    res = ListTable()
    getTree = res.getTree(db_config)
    return getTree


@app.route('/getListInfor', methods=['GET'])
def listInfor():
    res = ListTable()
    listInfor = res.listInfor(db_config)
    return listInfor


@app.route('/uploadImg', methods=['POST'])
def uploadsImage():
    res = Upload()
    uploadImg = res.uploadImg(db_config)
    return uploadImg


if __name__ == '__main__':
    if not os.path.exists('log'):
        os.makedirs('log')

    handler = logging.FileHandler('log/app.log', encoding='UTF-8')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
    )
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    app.run(host='127.0.0.1', port=5000)
