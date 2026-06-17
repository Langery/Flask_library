"""基础鉴权 + 配置加载回归测试。"""
import pytest


class TestConfigLoading:
    def test_secret_key_from_env(self):
        """SECRET_KEY 应从环境变量读取,而非硬编码。"""
        from config import Config
        assert Config.SECRET_KEY == 'test-secret-key-for-pytest-only-32B'

    def test_userinfo_uses_env(self):
        """userInfo 的 Password 字段不应是硬编码字符串。"""
        from userInfo import Password
        assert Password.user == 'test'
        assert Password.password == 'test'
        assert Password.database == 'test'


class TestHealthEndpoint:
    def test_first_returns_message(self, client):
        r = client.get('/api/first?name=ping')
        assert r.status_code == 200
        body = r.get_json()
        assert body['code'] == 0
        assert body['data']['message'] == 'ping'

    def test_first_without_name_returns_400(self, client):
        r = client.get('/api/first')
        assert r.status_code == 400
        assert r.get_json()['code'] == 1


class TestRegisterLogin:
    def test_register_then_login_succeeds(self, client):
        r = client.post('/api/register', json={'username': 'u1', 'nickname': 'u1n', 'password': 'pw'})
        assert r.status_code == 200
        assert r.get_json()['data']['backData'] is True

        r = client.post('/api/login', json={'username': 'u1', 'password': 'pw'})
        assert r.status_code == 200
        body = r.get_json()
        assert body['data']['backData'] is True
        assert 'tokenId' in body['data']
        assert len(body['data']['tokenId']) > 20  # JWT 长度

    def test_register_missing_fields_returns_400(self, client):
        r = client.post('/api/register', json={'username': 'only_name'})
        assert r.status_code == 400

    def test_login_wrong_password_returns_backdata_false(self, client):
        client.post('/api/register', json={'username': 'u2', 'nickname': 'u2n', 'password': 'pw'})
        r = client.post('/api/login', json={'username': 'u2', 'password': 'WRONG'})
        assert r.status_code == 200  # 注意:后端业务上不算 fail
        assert r.get_json()['data']['backData'] is False


class TestRequireAuth:
    def test_protected_endpoint_without_token_returns_401(self, client):
        r = client.get('/api/news/list')
        assert r.status_code == 401

    def test_protected_endpoint_with_garbage_token_returns_401(self, client):
        r = client.get('/api/news/list', headers={'Authorization': 'Bearer not-a-real-jwt'})
        assert r.status_code == 401

    def test_protected_endpoint_with_valid_token_returns_200(self, client, auth_headers):
        r = client.get('/api/news/list', headers=auth_headers('alice'))
        assert r.status_code == 200