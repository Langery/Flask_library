from flask import request, jsonify
import json

from classStore.server.dataLab import SQLFun


class Register:
    def __init__(self):
        print('success use register')
        data = request.get_data()
        self.data = data

    def findHad(self, config):
        data = json.loads(self.data)
        username = data['username']
        nickname = data['nickname']
        password = data['password']

        conn = config.connection()
        cursor = conn.cursor()

        sql_check = "SELECT id FROM usertable WHERE username = ? OR nickname = ?"
        cursor.execute(sql_check, (username, nickname))
        existing = cursor.fetchone()

        if existing:
            return jsonify({'backData': False, 'message': '用户名或昵称已存在'})

        sql_insert = "INSERT INTO usertable (username, password, nickname) VALUES (?, ?, ?)"
        try:
            cursor.execute(sql_insert, (username, password, nickname))
            conn.commit()
            return jsonify({'backData': True, 'message': '注册成功'})
        except Exception as e:
            conn.rollback()
            return jsonify({'backData': False, 'message': str(e)})
        finally:
            cursor.close()