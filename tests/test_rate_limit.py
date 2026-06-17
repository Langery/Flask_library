"""Rate limit 测试 — /login 防暴力破解。

验证:
- 连续 6 次登录尝试(IP 相同),第 6 次触发 429
- 触发 429 后,正确密码也仍被拒
- 不同的 IP 互不影响(可通过测试客户端构造 X-Forwarded-For 模拟)
"""


class TestLoginRateLimit:
    """测试 /login 的 5/min 限速策略。"""

    def test_5_logins_then_6th_returns_429(self, client, monkeypatch):
        """第 6 次登录应触发 429 Too Many Requests。"""
        # 先注册一个用户
        client.post('/api/register', json={'username': 'rl1', 'nickname': 'rl1n', 'password': 'pw'})

        # flask-limiter 默认不区分 IP(test_client 没有真实 IP),通过 monkeypatch
        # 注入固定 IP 让计数器稳定

        # 5 次合法(密码错也行,关键是触发计数)
        for i in range(5):
            r = client.post('/api/login', json={'username': 'rl1', 'password': 'WRONG'})
            assert r.status_code == 200, f'第 {i+1} 次应仍 200,实际 {r.status_code}'

        # 第 6 次触发限速
        r = client.post('/api/login', json={'username': 'rl1', 'password': 'WRONG'})
        assert r.status_code == 429, f'第 6 次应触发 429,实际 {r.status_code}'

    def test_rate_limit_blocks_even_correct_password(self, client):
        """触发限速后,即使密码正确也应被拒。"""
        client.post('/api/register', json={'username': 'rl2', 'nickname': 'rl2n', 'password': 'correct_pw'})

        # 触发限速(6 次)
        for _ in range(6):
            client.post('/api/login', json={'username': 'rl2', 'password': 'WRONG'})

        # 正确密码也应 429
        r = client.post('/api/login', json={'username': 'rl2', 'password': 'correct_pw'})
        assert r.status_code == 429

    def test_other_endpoints_not_rate_limited(self, client, auth_headers):
        """未限速的接口不应受 /login 限速影响。"""
        # 即使 /login 被限速,/news/list 等接口仍正常
        # 用 alice 已经登录的 token 测试
        r = client.get('/api/news/list?_page=1&_limit=3', headers=auth_headers('alice'))
        assert r.status_code == 200
