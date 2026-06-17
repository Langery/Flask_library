import time
from functools import wraps

import jwt
from flask import current_app, g, request

from classStore.common.response import fail


def generate_token(user_id, username, expires_in=86400):
    """生成 JWT,默认 24h 过期。HS256 真签名(SECRET_KEY 从 app config 拿)"""
    payload = {
        'uid': user_id,
        'username': username,
        'iat': time.time(),
        'exp': time.time() + expires_in
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def verify_token(token):
    """验证 token 签名和过期,返回 payload dict;失败抛 jwt.PyJWTError"""
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])


def _extract_bearer_token():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:].strip()
    return None


def require_auth(f):
    """装饰器:从 Authorization header 读 Bearer token,验证后把 uid/username 放到 flask.g"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_bearer_token()
        if not token:
            return fail('未提供 token', http_status=401)
        try:
            payload = verify_token(token)
        except jwt.ExpiredSignatureError:
            return fail('token 已过期', http_status=401)
        except jwt.InvalidTokenError:
            return fail('token 无效', http_status=401)
        g.user_id = payload['uid']
        g.username = payload['username']
        return f(*args, **kwargs)
    return wrapper
