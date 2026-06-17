"""异常处理信息泄露防护测试。

验证:
- /api/register 即便内部异常,响应也不含 SQL/schema/技术细节
- /api/uploadImg 写文件失败时,响应不含路径/errno/技术细节
"""


# 绝不能出现在用户响应中的关键词(任何一条命中即失败)
_LEAK_TOKENS = (
    'UNIQUE', 'constraint', 'sqlite', 'IntegrityError',
    'Database', 'SQL', 'errno', 'Traceback', 'FileNotFoundError',
    'PermissionError', 'IsADirectoryError',
)


def _assert_no_leak(resp_json, context):
    """递归检查响应 dict/list/str 中不含 LEAK_TOKENS。"""
    if isinstance(resp_json, dict):
        for k, v in resp_json.items():
            assert k not in _LEAK_TOKENS, f'{context}: key {k!r} 暴露技术细节'
            _assert_no_leak(v, f'{context}.{k}')
    elif isinstance(resp_json, list):
        for i, v in enumerate(resp_json):
            _assert_no_leak(v, f'{context}[{i}]')
    elif isinstance(resp_json, str):
        for tok in _LEAK_TOKENS:
            assert tok not in resp_json, f'{context}: 消息含技术细节 {tok!r}: {resp_json!r}'


class TestRegisterErrorSanitization:
    """X-N: /api/register 不应在异常路径泄露 SQL/schema 信息。"""

    def test_register_happy_path_no_leak(self, client):
        """正常注册响应不应含技术细节(回归保险)。"""
        r = client.post('/api/register', json={'username': 'ok_user', 'nickname': 'ok_n', 'password': 'pw'})
        assert r.status_code == 200
        _assert_no_leak(r.get_json(), 'register.ok')

    def test_register_duplicate_via_race_simulation(self, client):
        """模拟竞态:先直接 INSERT 一个用户,再调用 register 走 SELECT 检查路径,
        验证响应消息不含 UNIQUE/constraint 等 SQL 细节。"""
        from classStore.common.db import execute
        # 直接 INSERT 一个用户,绕过 SELECT 检查的竞态模拟
        # (实际场景:两个请求同时通过 SELECT 检查,后到的 INSERT 失败)
        execute(
            'INSERT INTO usertable (username, password, nickname) VALUES (?, ?, ?)',
            ('racy_user', 'pw', 'racy_n')
        )
        r = client.post('/api/register', json={'username': 'racy_user', 'nickname': 'racy_n2', 'password': 'pw'})
        # SELECT 检查会先命中,返回友好"已存在"消息;响应必须无技术细节
        assert r.status_code == 200
        body = r.get_json()
        assert body['data']['backData'] is False
        _assert_no_leak(body, 'register.duplicate')

    def test_register_insert_failure_returns_friendly_message(self, client, monkeypatch):
        """强制 INSERT 抛 IntegrityError,验证响应是友好消息不是 str(e)。"""
        import sqlite3

        from blueprintStore.auth import routes as auth_routes

        # patch routes 模块本地导入的 execute(不是 db_module.execute,
        # 因为 `from ... import execute` 已把名字绑定到 routes 自己的命名空间)
        original_execute = auth_routes.execute

        def fake_execute(sql, params=()):
            if 'INSERT INTO usertable' in sql:
                raise sqlite3.IntegrityError('UNIQUE constraint failed: usertable.username')
            return original_execute(sql, params)

        monkeypatch.setattr(auth_routes, 'execute', fake_execute)

        r = client.post('/api/register', json={'username': 'new_user', 'nickname': 'new_n', 'password': 'pw'})
        assert r.status_code == 200
        body = r.get_json()
        assert body['data']['backData'] is False
        assert 'UNIQUE' not in body['data']['message']
        assert 'constraint' not in body['data']['message']
        assert body['data']['message'] == '用户名或昵称已存在'
        _assert_no_leak(body, 'register.integrity_error')

    def test_register_unexpected_error_returns_generic_message(self, client, monkeypatch):
        """强制 INSERT 抛 RuntimeError 等未预期异常,验证响应是通用消息。"""
        from blueprintStore.auth import routes as auth_routes

        original_execute = auth_routes.execute

        def fake_execute(sql, params=()):
            if 'INSERT INTO usertable' in sql:
                raise RuntimeError('database connection lost at /var/data/secrets.db')
            return original_execute(sql, params)

        monkeypatch.setattr(auth_routes, 'execute', fake_execute)

        r = client.post('/api/register', json={'username': 'u3', 'nickname': 'u3n', 'password': 'pw'})
        assert r.status_code == 200
        body = r.get_json()
        assert body['data']['backData'] is False
        # 绝不能泄露原始异常消息
        assert '/var/data' not in body['data']['message']
        assert 'RuntimeError' not in body['data']['message']
        assert body['data']['message'] == '注册失败,请稍后重试'


class TestUploadImgErrorSanitization:
    """X-N: /api/uploadImg 写文件失败时不应泄露路径/errno。"""

    def test_upload_img_happy_path(self, client, auth_headers):
        """正常上传响应不应含技术细节。"""
        r = client.post('/api/uploadImg', json={
            'image': 'data:image/png;base64,iVBORw0KGgo=',
            'filename': 'normal.png'
        }, headers=auth_headers('alice'))
        assert r.status_code == 200
        _assert_no_leak(r.get_json(), 'upload.ok')

    def test_upload_img_oserror_returns_friendly_message(self, client, auth_headers, monkeypatch):
        """强制 open() 抛 OSError,验证响应不含 errno/路径。"""
        # 拦截 builtins.open 让它抛 OSError
        import builtins
        original_open = builtins.open

        def fake_open(*args, **kwargs):
            raise OSError(28, 'No space left on device')

        monkeypatch.setattr(builtins, 'open', fake_open)

        r = client.post('/api/uploadImg', json={
            'image': 'data',
            'filename': 'will_fail.png'
        }, headers=auth_headers('alice'))
        assert r.status_code == 500
        body = r.get_json()
        # 响应消息必须是通用"文件保存失败",不能含 errno=28 或 'No space'
        assert body['message'] == '文件保存失败'
        _assert_no_leak(body, 'upload.oserror')
        # 还原 open,避免影响后续测试
        monkeypatch.setattr(builtins, 'open', original_open)

    def test_upload_img_unexpected_error_returns_generic(self, client, auth_headers, monkeypatch):
        """强制 open() 抛 RuntimeError,验证响应是通用消息。"""
        import builtins

        def fake_open(*args, **kwargs):
            raise RuntimeError('disk controller glitch at /dev/sda1')

        monkeypatch.setattr(builtins, 'open', fake_open)

        r = client.post('/api/uploadImg', json={
            'image': 'data',
            'filename': 'weird.png'
        }, headers=auth_headers('alice'))
        assert r.status_code == 500
        body = r.get_json()
        assert body['message'] == '上传失败,请稍后重试'
        assert '/dev/sda1' not in body['message']
        _assert_no_leak(body, 'upload.unexpected')
