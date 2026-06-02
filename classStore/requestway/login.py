from flask import request, jsonify
import json
import time
import base64
import hmac

from classStore.server.dataLab import SQLFun


class Login:
    def __init__(self):
        print('success use login')
        data = request.get_data()
        self.data = data

    def select(self, config):
        data = json.loads(self.data)
        username = data['username']
        password = data['password']

        conn = config.connection()
        cursor = conn.cursor()

        sql = "SELECT id, nickname, password FROM usertable WHERE (username = ? OR nickname = ?) AND password = ?"
        cursor.execute(sql, (username, username, password))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            nickname = result[1]
            res = {
                'backData': True,
                'tokenId': self._generate_token(username, user_id)
            }
        else:
            res = {'backData': False}

        return jsonify(res)

    def _generate_token(self, username, user_id):
        header = {"typ": "JWT", "alg": "HS256"}
        header_encode = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).replace(b"=", b"")

        payload = {
            "username": username,
            "uid": user_id,
            "exp": time.time() + 300
        }
        payload_encode = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).replace(b"=", b"")

        temp = header_encode + b"." + payload_encode
        temp_hash = hmac.new(b"", temp, digestmod="SHA256")
        signature = base64.urlsafe_b64encode(temp_hash.digest()).replace(b"=", b"")

        return (header_encode + b"." + payload_encode + b"." + signature).decode()