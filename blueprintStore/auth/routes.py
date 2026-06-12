import json
import base64
import hmac
import time
from flask import request
from classStore.common.db import query_one, execute
from classStore.common.response import ok, fail
from blueprintStore.auth import auth_blue


def _generate_token(username, user_id):
    """手搓 JWT(X-B 替换为 PyJWT 真签名)"""
    header = {'typ': 'JWT', 'alg': 'HS256'}
    header_encode = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).replace(b'=', b'')

    payload = {
        'username': username,
        'uid': user_id,
        'exp': time.time() + 300
    }
    payload_encode = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).replace(b'=', b'')

    temp = header_encode + b'.' + payload_encode
    temp_hash = hmac.new(b'', temp, digestmod='SHA256')
    signature = base64.urlsafe_b64encode(temp_hash.digest()).replace(b'=', b'')

    return (header_encode + b'.' + payload_encode + b'.' + signature).decode()


@auth_blue.route('/first', methods=['GET'])
def first():
    name = request.args.get('name')
    if name:
        return ok({'message': name})
    return fail('No data', http_status=400)


@auth_blue.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return fail('username and password are required', http_status=400)

    row = query_one(
        'SELECT id, nickname, password FROM usertable WHERE (username = ? OR nickname = ?) AND password = ?',
        (username, username, password)
    )

    if row:
        return ok({
            'backData': True,
            'tokenId': _generate_token(username, row['id'])
        })
    return ok({'backData': False})


@auth_blue.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    nickname = data.get('nickname')
    password = data.get('password')

    if not username or not nickname or not password:
        return fail('username, nickname, password are required', http_status=400)

    existing = query_one(
        'SELECT id FROM usertable WHERE username = ? OR nickname = ?',
        (username, nickname)
    )
    if existing:
        return ok({'backData': False, 'message': '用户名或昵称已存在'})

    try:
        execute(
            'INSERT INTO usertable (username, password, nickname) VALUES (?, ?, ?)',
            (username, password, nickname)
        )
        return ok({'backData': True, 'message': '注册成功'})
    except Exception as e:
        return ok({'backData': False, 'message': str(e)})
