"""News 接口回归测试 — 重点验证 X-F 修复 (B):/news/related 越权读取。"""


class TestNewsList:
    def test_list_returns_paginated_items(self, client, auth_headers):
        r = client.get('/api/news/list?_page=1&_limit=5', headers=auth_headers('alice'))
        assert r.status_code == 200
        body = r.get_json()['data']
        assert body['page'] == 1
        assert body['limit'] == 5
        assert len(body['items']) == 5
        assert body['total'] >= 100  # seed 注入 100 条

    def test_list_keyword_filter(self, client, auth_headers):
        r = client.get('/api/news/list?q=News+%2311&_limit=5', headers=auth_headers('alice'))
        assert r.status_code == 200
        items = r.get_json()['data']['items']
        # seed 数据 News #11 存在
        assert any('News #11' in it['title'] for it in items)

    def test_list_clamps_limit_to_max_50(self, client, auth_headers):
        r = client.get('/api/news/list?_limit=999', headers=auth_headers('alice'))
        body = r.get_json()['data']
        assert body['limit'] == 50  # MAX_LIMIT

    def test_list_normalizes_page_to_at_least_1(self, client, auth_headers):
        r = client.get('/api/news/list?_page=0', headers=auth_headers('alice'))
        body = r.get_json()['data']
        assert body['page'] == 1

    def test_list_invalid_limit_returns_400(self, client, auth_headers):
        r = client.get('/api/news/list?_limit=abc', headers=auth_headers('alice'))
        assert r.status_code == 400


class TestNewsDetail:
    def test_existing_id_returns_200(self, client, auth_headers):
        r = client.get('/api/news/detail/1', headers=auth_headers('alice'))
        assert r.status_code == 200

    def test_nonexistent_id_returns_404(self, client, auth_headers):
        r = client.get('/api/news/detail/99999', headers=auth_headers('alice'))
        assert r.status_code == 404


class TestNewsRelatedAuthorization:
    """X-F 修复点:Alice 只能查自己的 related,查 Bob 必须 403。"""

    def test_self_related_returns_200(self, client, auth_headers, two_users):
        r = client.get(f"/api/news/related/{two_users['alice_id']}", headers=auth_headers('alice'))
        assert r.status_code == 200

    def test_other_user_related_returns_403(self, client, auth_headers, two_users):
        """这是 X-F 修复的核心断言:alice 查 bob 的 related 必须被拒。"""
        r = client.get(f"/api/news/related/{two_users['bob_id']}", headers=auth_headers('alice'))
        assert r.status_code == 403
        assert 'forbidden' in r.get_json()['message'].lower()

    def test_reverse_other_user_related_returns_403(self, client, auth_headers, two_users):
        """Bob 查 Alice 的同样要 403,不能单向。"""
        r = client.get(f"/api/news/related/{two_users['alice_id']}", headers=auth_headers('bob'))
        assert r.status_code == 403

    def test_related_without_token_returns_401(self, client, two_users):
        r = client.get(f"/api/news/related/{two_users['alice_id']}")
        assert r.status_code == 401

    def test_related_with_exclude_id_still_403_when_target_other(self, client, auth_headers, two_users):
        """带 exclude_id 参数也不能绕过 user_id 校验。"""
        r = client.get(
            f"/api/news/related/{two_users['bob_id']}?exclude_id=1",
            headers=auth_headers('alice')
        )
        assert r.status_code == 403
