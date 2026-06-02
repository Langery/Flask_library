from flask import request, jsonify
import json
from classStore.server.dataLab import SQLFun


class TalkRequest:
    def __init__(self):
        print("success use talk request")
        data = request.get_data()
        self.data = data

    def talkMess(self, config):
        print("This is talk messages")
        conn = config.connection()
        cursor = conn.cursor()

        data = json.loads(self.data)
        cursor.close()
        conn.close()

        return jsonify({'message': 'Talk message received', 'data': data})