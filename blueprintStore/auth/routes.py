from flask import request
from classStore.common.db import query_one, execute
from classStore.common.auth import generate_token
from classStore.common.response import ok, fail
from classStore.common.limiter import limiter
from blueprintStore.auth import auth_blue


@auth_blue.route('/first', methods=['GET'])
def first():
    name = request.args.get('name')
    if name:
        return ok({'message': name})
    return fail('No data', http_status=400)


@auth_blue.route('/login', methods=['POST'])
@limiter.limit('5 per minute')  # 防暴力破解:同 IP 每分钟最多 5 次登录尝试
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
            'tokenId': generate_token(row['id'], username)
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
