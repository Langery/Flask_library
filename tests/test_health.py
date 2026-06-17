"""/api/health 真健康检查测试。

验证:
- 无参 GET → 200 + 完整 status/db/timestamp
- DB 可达 → status=ok, db=ok
- DB 不可达 → 503 + status=degraded, db=error(模拟运维场景)
- 时间戳是合法 ISO 格式
"""
from datetime import datetime


class TestHealthEndpoint:
    """X-O: /api/health 用于 K8s/容器 readiness 探活。"""

    def test_health_returns_200_when_db_ok(self, client):
        """健康路径:DB 可达 → 200"""
        r = client.get('/api/health')
        assert r.status_code == 200

    def test_health_response_shape(self, client):
        """响应必须含 status/db/timestamp 三个字段。"""
        r = client.get('/api/health')
        body = r.get_json()
        data = body['data']
        assert data['status'] == 'ok'
        assert data['db'] == 'ok'
        assert 'timestamp' in data
        # timestamp 必须是合法 ISO 格式
        datetime.fromisoformat(data['timestamp'])

    def test_health_no_params_required(self, client):
        """与 /api/first 不同,/api/health 无需任何 query 参数。"""
        r = client.get('/api/health')
        assert r.status_code == 200
        # 不应返回 400 "No data" 之类的参数缺失错误
        assert r.get_json()['code'] == 0

    def test_health_db_failure_returns_503(self, client, monkeypatch):
        """DB 不可达 → 503 + status=degraded。模拟 DB 宕机场景。"""
        from blueprintStore.auth import routes as auth_routes

        def fake_query_one(sql, params=()):
            if 'SELECT 1' in sql:
                raise RuntimeError('database is down')
            return None

        monkeypatch.setattr(auth_routes, 'query_one', fake_query_one)

        r = client.get('/api/health')
        assert r.status_code == 503
        body = r.get_json()
        assert body['data']['status'] == 'degraded'
        assert body['data']['db'] == 'error'
        # 时间戳仍然存在(便于运维定位故障时刻)
        assert 'timestamp' in body['data']

    def test_health_does_not_leak_db_error_message(self, client, monkeypatch):
        """DB 异常时响应不应泄露原始异常消息(沿用 X-N 的信息泄露防护原则)。"""
        from blueprintStore.auth import routes as auth_routes

        def fake_query_one(sql, params=()):
            if 'SELECT 1' in sql:
                raise RuntimeError('connection lost at /var/secrets/db.sqlite')
            return None

        monkeypatch.setattr(auth_routes, 'query_one', fake_query_one)

        r = client.get('/api/health')
        body = r.get_json()
        # 即使 message 字段出现也不应含原始异常
        all_text = str(body)
        assert '/var/secrets' not in all_text
        assert 'RuntimeError' not in all_text
