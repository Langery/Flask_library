from flask import request, jsonify
import json


class ListTable:
    def __init__(self):
        print('success use ListTable')
        data = request.get_data()
        self.data = data

    def getTree(self, config):
        print('This is the getTree')
        conn = config.connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM listtable"
        cursor.execute(sql)
        result = cursor.fetchall()

        initTree = []

        for item in result:
            is_leaf = item[2] != 1

            if item[3] == 0:
                loopData = {
                    'key': item[0],
                    'title': item[1],
                    'isLeaf': is_leaf,
                    'children': []
                }
                initTree.append(loopData)
            else:
                for initTreeData in initTree:
                    if item[3] == initTreeData['key']:
                        childData = {
                            'key': item[0],
                            'title': item[1],
                            'isLeaf': is_leaf
                        }
                        initTreeData['children'].append(childData)
                        break

        return jsonify(initTree)

    def listInfor(self, config):
        print('This is the listInfor')
        item_id = request.args.get('id')

        if not item_id:
            return jsonify({'error': 'id is required'}), 400

        conn = config.connection()
        cursor = conn.cursor()

        sql = "SELECT describeInfor FROM listtable WHERE id = ?"
        cursor.execute(sql, (item_id,))
        row = cursor.fetchone()

        if row:
            return jsonify({'describe': row[0]})
        return jsonify({'error': 'Not found'}), 404