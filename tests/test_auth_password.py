"""X-S: 密码 pbkdf2 哈希 + 输入格式校验测试。

覆盖:
- 密码存为 hash(非明文) — P0 安全核心
- 登录 round-trip(用 hash 比对)
- 老 plaintext 用户首次登录后自动升级为 hash
- 格式校验:用户名/昵称/密码各种异常路径
- register IntegrityError / 通用异常的回退消息
- 登录 missing fields / user not found(无 enumeration 泄露)

注意:conftest._purge_app_modules() 会清模块缓存 → db helpers 必须在 test 函数体内
重新 import,顶部 from-import 会拿到旧模块引用。
"""


class TestPasswordHashStorage:
    """X-S 核心:密码绝不能明文存储"""

    def test_register_stores_hash_not_plaintext(self, client):
        """注册成功后,DB 中的 password 字段必须是 pbkdf2 哈希,不是明文。"""
        client.post('/api/register', json={
            'username': 'hash_user',
            'nickname': 'hu_n',
            'password': 'pw12345',
        })
        # 函数内 re-import,绕过 _purge_app_modules 缓存
        from classStore.common.db import query_one
        row = query_one('SELECT password FROM usertable WHERE username=?', ('hash_user',))
        assert row is not None
        stored = row['password']
        # 哈希特征:以 pbkdf2:/scrypt:/bcrypt 之一开头(wrkzeug 默认 scrypt),
        # 长度 > 50,不含明文密码
        assert any(stored.startswith(p) for p in ('pbkdf2:', 'scrypt:', 'bcrypt')), (
            f'expected hash, got: {stored!r}'
        )
        assert 'pw12345' not in stored, f'plaintext leaked into stored value: {stored!r}'
        assert len(stored) > 50

    def test_login_with_hashed_password_succeeds(self, client):
        """注册 → 登录 round-trip:登录走 check_password_hash 路径。"""
        client.post('/api/register', json={
            'username': 'roundtrip',
            'nickname': 'rt_n',
            'password': 'pw12345',
        })
        r = client.post('/api/login', json={
            'username': 'roundtrip',
            'password': 'pw12345',
        })
        body = r.get_json()
        assert body['data']['backData'] is True
        assert 'tokenId' in body['data']


class TestPlaintextAutoUpgrade:
    """X-S: 老 plaintext 用户首次登录后自动升级为 hash(零停机迁移)"""

    def test_plaintext_password_gets_hashed_on_first_login(self, client):
        """直接 INSERT 一个 plaintext 密码的用户,登录成功后 password 列应被升级为哈希。"""
        from classStore.common.db import execute, query_one

        # 直接插入 plaintext(模拟历史数据)
        execute(
            'INSERT INTO usertable (username, password, nickname) VALUES (?, ?, ?)',
            ('legacy_user', 'plaintext_pw_legacy', 'legacy_n'),
        )
        # 确认还是 plaintext
        before = query_one('SELECT password FROM usertable WHERE username=?', ('legacy_user',))
        assert before['password'] == 'plaintext_pw_legacy'

        # 登录成功 → 应自动升级
        r = client.post('/api/login', json={
            'username': 'legacy_user',
            'password': 'plaintext_pw_legacy',
        })
        assert r.get_json()['data']['backData'] is True

        after = query_one('SELECT password FROM usertable WHERE username=?', ('legacy_user',))
        assert any(after['password'].startswith(p) for p in ('pbkdf2:', 'scrypt:', 'bcrypt')), (
            f'plaintext password not auto-upgraded, still: {after["password"]!r}'
        )
        assert 'plaintext_pw_legacy' not in after['password']

    def test_plaintext_login_with_wrong_password_fails(self, client):
        """plaintext 用户密码错 → backData=False,且**不**被升级(避免错误地覆盖正确 hash)。"""
        from classStore.common.db import execute, query_one

        execute(
            'INSERT INTO usertable (username, password, nickname) VALUES (?, ?, ?)',
            ('legacy2', 'correct_pw_legacy', 'l2_n'),
        )
        r = client.post('/api/login', json={'username': 'legacy2', 'password': 'WRONG'})
        assert r.get_json()['data']['backData'] is False

        # 关键:失败登录不应触发 hash 升级
        row = query_one('SELECT password FROM usertable WHERE username=?', ('legacy2',))
        assert row['password'] == 'correct_pw_legacy', (
            'auto-upgrade must only run on successful login, not on failure'
        )


class TestRegisterValidation:
    """X-S: 注册输入格式校验"""

    def test_password_too_short_returns_400(self, client):
        r = client.post('/api/register', json={
            'username': 'shortpw',
            'nickname': 'sp_n',
            'password': '12345',  # 5 chars, < 6 minimum
        })
        assert r.status_code == 400
        assert '密码' in r.get_json()['message']

    def test_password_exactly_six_chars_accepted(self, client):
        """边界:6 字符密码应被接受。"""
        r = client.post('/api/register', json={
            'username': 'edge6',
            'nickname': 'e6_n',
            'password': '123456',
        })
        assert r.status_code == 200
        assert r.get_json()['data']['backData'] is True

    def test_username_too_short_returns_400(self, client):
        r = client.post('/api/register', json={
            'username': 'ab',  # 2 chars, < 3
            'nickname': 'short_n',
            'password': 'pw12345',
        })
        assert r.status_code == 400
        assert '用户名' in r.get_json()['message']

    def test_username_with_special_chars_returns_400(self, client):
        """中文/特殊字符都应被拒(防止 SQL 注入残留风险 + 业务规则)。"""
        r = client.post('/api/register', json={
            'username': "u'; DROP--",  # 注入 payload + 长度问题
            'nickname': 'sqli_n',
            'password': 'pw12345',
        })
        assert r.status_code == 400
        assert '用户名' in r.get_json()['message']

    def test_username_chinese_returns_400(self, client):
        """中文用户名应被拒(USERNAME_RE 限制 A-Za-z0-9_)。"""
        r = client.post('/api/register', json={
            'username': '中文用户',
            'nickname': 'cn_n',
            'password': 'pw12345',
        })
        assert r.status_code == 400

    def test_nickname_too_long_returns_400(self, client):
        long_nick = 'a' * 31  # > 30 max
        r = client.post('/api/register', json={
            'username': 'longnick',
            'nickname': long_nick,
            'password': 'pw12345',
        })
        assert r.status_code == 400
        assert '昵称' in r.get_json()['message']

    def test_nickname_whitespace_only_returns_400(self, client):
        r = client.post('/api/register', json={
            'username': 'whitenick',
            'nickname': '   ',
            'password': 'pw12345',
        })
        assert r.status_code == 400
        assert '昵称' in r.get_json()['message']


class TestRegisterErrorPaths:
    """X-S: register 在竞态 / 异常路径的消息脱敏"""

    def test_register_duplicate_returns_friendly_message(self, client):
        """正常路径下用户名重复 → '用户名或昵称已存在'(不应含 SQL 细节)。"""
        from classStore.common.db import execute
        execute(
            'INSERT INTO usertable (username, password, nickname) VALUES (?, ?, ?)',
            ('dupe', 'pbkdf2:fake', 'dupe_n'),
        )
        r = client.post('/api/register', json={
            'username': 'dupe', 'nickname': 'dupe_n2', 'password': 'pw12345',
        })
        assert r.status_code == 200
        body = r.get_json()
        assert body['data']['backData'] is False
        assert body['data']['message'] == '用户名或昵称已存在'

    def test_register_integrity_error_returns_friendly(self, client, monkeypatch):
        """强制 INSERT 抛 IntegrityError → 走 except 分支,响应是友好消息。"""
        import sqlite3

        from blueprintStore.auth import routes as auth_routes

        original_execute = auth_routes.execute

        def fake_execute(sql, params=()):
            if 'INSERT INTO usertable' in sql:
                raise sqlite3.IntegrityError('UNIQUE constraint failed: usertable.username')
            return original_execute(sql, params)

        monkeypatch.setattr(auth_routes, 'execute', fake_execute)
        r = client.post('/api/register', json={
            'username': 'race_user', 'nickname': 'ru_n', 'password': 'pw12345',
        })
        body = r.get_json()
        assert body['data']['backData'] is False
        assert body['data']['message'] == '用户名或昵称已存在'
        # 关键:响应里没有 raw 异常消息
        assert 'UNIQUE' not in body['data']['message']

    def test_register_unexpected_error_returns_generic(self, client, monkeypatch):
        """强制 INSERT 抛 RuntimeError → 通用兜底消息,不泄露原始内容。"""
        from blueprintStore.auth import routes as auth_routes

        original_execute = auth_routes.execute

        def fake_execute(sql, params=()):
            if 'INSERT INTO usertable' in sql:
                raise RuntimeError('database connection lost at /var/secrets.db')
            return original_execute(sql, params)

        monkeypatch.setattr(auth_routes, 'execute', fake_execute)
        r = client.post('/api/register', json={
            'username': 'unexpected', 'nickname': 'u_n', 'password': 'pw12345',
        })
        body = r.get_json()
        assert body['data']['backData'] is False
        assert body['data']['message'] == '注册失败,请稍后重试'
        assert '/var/secrets.db' not in body['data']['message']
        assert 'RuntimeError' not in body['data']['message']


class TestLoginEdgeCases:
    """X-S: 登录路径的输入校验 + enumeration 防御"""

    def test_login_missing_username_returns_400(self, client):
        r = client.post('/api/login', json={'password': 'pw12345'})
        assert r.status_code == 400

    def test_login_missing_password_returns_400(self, client):
        r = client.post('/api/login', json={'username': 'somebody'})
        assert r.status_code == 400

    def test_login_nonexistent_user_returns_backdata_false(self, client):
        """用户不存在 → backData=False,与"密码错"统一响应(防 enumeration)。"""
        r = client.post('/api/login', json={
            'username': 'ghost_user_xyz',
            'password': 'whatever',
        })
        assert r.status_code == 200
        assert r.get_json()['data']['backData'] is False
        # 关键:响应里没有"用户不存在"等区分性文案
        msg = r.get_json()['data'].get('message', '')
        assert '不存在' not in msg
        assert '用户' not in msg

    def test_login_wrong_password_for_hashed_user(self, client):
        """已哈希的用户密码错 → backData=False。"""
        client.post('/api/register', json={
            'username': 'hashed_user', 'nickname': 'hu_n2', 'password': 'pw12345',
        })
        r = client.post('/api/login', json={
            'username': 'hashed_user', 'password': 'WRONG_PW',
        })
        assert r.get_json()['data']['backData'] is False
