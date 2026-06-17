"""测试公共 fixture。

启动一个 in-process Flask test_client + 临时 SQLite 数据库,
每个测试 case 拿到全新的隔离环境,无需任何外部服务。
"""
import os
import sys

import pytest

# 让 import 找到项目根目录的 server.py / config.py / classStore / blueprintStore
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _purge_app_modules():
    """清除所有 app 模块的 import 缓存,确保下一次 import 走最新代码/env。"""
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'server' or mod_name.startswith(('config', 'classStore', 'blueprintStore')):
            del sys.modules[mod_name]


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    """每个测试自动注入测试所需的环境变量。autouse=True 让所有测试都先经过这里。"""
    monkeypatch.setenv('SQL_USER', 'test')
    monkeypatch.setenv('SQL_PASSWORD', 'test')
    monkeypatch.setenv('SQL_DATABASE', 'test')
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key-for-pytest-only-32B')


@pytest.fixture
def app(tmp_path, monkeypatch):
    # 1. 每次 fixture 入口先清模块缓存,让 monkeypatch.setenv 生效后再 import
    _purge_app_modules()

    # 2. rate limit 用 memory://,每个测试因 _purge_app_modules 拿到全新的 server 实例,
    #    内存计数器天然隔离(flask-limiter 不支持 sqlite:// URI)
    monkeypatch.setenv('RATELIMIT_STORAGE_URI', 'memory://')

    # 3. 在 import 之前,把 db._DB_PATH 切到 tmp_path
    #    这一步必须先 import classStore.common.db 拿到模块对象
    import classStore.common.db as db_module
    db_module._DB_PATH = str(tmp_path / 'test.db')

    # 4. 现在 import server,触发 init_db() 用新的 _DB_PATH 建表
    import server
    server.app.config['TESTING'] = True

    yield server.app

    # 5. 测试结束后清模块缓存,避免下一个测试拿到旧的 app 实例
    _purge_app_modules()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def two_users(client, app):
    """注册 alice / bob 并返回两个 JWT token + 各自的 user_id。"""
    client.post('/api/register', json={'username': 'alice', 'nickname': 'alice_n', 'password': 'pw_alice'})
    client.post('/api/register', json={'username': 'bob', 'nickname': 'bob_n', 'password': 'pw_bob'})

    alice_login = client.post('/api/login', json={'username': 'alice', 'password': 'pw_alice'}).get_json()
    bob_login = client.post('/api/login', json={'username': 'bob', 'password': 'pw_bob'}).get_json()

    with app.app_context():
        from classStore.common.db import query_one
        alice_id = query_one('SELECT id FROM usertable WHERE username=?', ('alice',))['id']
        bob_id = query_one('SELECT id FROM usertable WHERE username=?', ('bob',))['id']

    return {
        'alice_token': alice_login['data']['tokenId'],
        'bob_token': bob_login['data']['tokenId'],
        'alice_id': alice_id,
        'bob_id': bob_id,
    }


@pytest.fixture
def auth_headers(two_users):
    """返回 factory:auth_headers('alice') -> {'Authorization': 'Bearer ...'}"""
    def _make(user):
        return {'Authorization': f"Bearer {two_users[f'{user}_token']}"}
    return _make
