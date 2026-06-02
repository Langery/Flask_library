from flask import request, jsonify


class First:
    def __init__(self):
        print('success')

    def first(self):
        name = request.args.get('name')
        print(name)

        if name:
            return jsonify({'message': name})
        return jsonify({'error': 'No data'})