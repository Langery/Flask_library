"""/api/layout/* 拖拽布局接口测试。

补 layout/routes.py 覆盖率(原 39%),覆盖:
- /api/layout/get 无布局 / 有布局 / 损坏 JSON 三种情况
- /api/layout/save 正常 / 校验失败 / 超容量
"""
import json


class TestLayoutGet:
    """GET /api/layout/get: 拉取当前用户的拖拽布局"""

    def test_get_empty_layout_returns_empty_list(self, client, auth_headers):
        """新用户无布局记录 → 返回空 items + updatedAt=None。"""
        r = client.get('/api/layout/get', headers=auth_headers('alice'))
        assert r.status_code == 200
        body = r.get_json()['data']
        assert body['items'] == []
        assert body['updatedAt'] is None

    def test_get_existing_layout(self, client, auth_headers):
        """先 save 再 get,验证数据往返正确。"""
        payload = [{'i': 'foo', 'x': 1, 'y': 2}, {'i': 'bar', 'x': 3, 'y': 4}]
        # save
        r = client.put(
            '/api/layout/save',
            json={'items': payload},
            headers=auth_headers('alice'),
        )
        assert r.status_code == 200
        # get
        r = client.get('/api/layout/get', headers=auth_headers('alice'))
        body = r.get_json()['data']
        assert body['items'] == payload
        assert body['updatedAt'] is not None

    def test_get_corrupt_json_falls_back_to_empty(self, client, auth_headers, monkeypatch):
        """layout_json 字段损坏时,返回空 items 而不是 500。"""
        from blueprintStore.layout import routes as layout_routes

        original_query_one = layout_routes.query_one

        def fake_query_one(sql, params=()):
            # 模拟数据库里存了非法 JSON
            return {'layout_json': '{not valid json', 'updated_at': '2026-01-01'}
        monkeypatch.setattr(layout_routes, 'query_one', fake_query_one)

        r = client.get('/api/layout/get', headers=auth_headers('alice'))
        # 不应 500,应优雅降级返回空
        assert r.status_code == 200
        body = r.get_json()['data']
        assert body['items'] == []


class TestLayoutSave:
    """PUT /api/layout/save: 保存拖拽布局"""

    def test_save_normal_layout(self, client, auth_headers):
        r = client.put(
            '/api/layout/save',
            json={'items': [{'i': 'a'}]},
            headers=auth_headers('alice'),
        )
        assert r.status_code == 200
        body = r.get_json()['data']
        assert body['saved'] == 1
        assert body['updatedAt'] is not None

    def test_save_overwrites_existing(self, client, auth_headers):
        """二次 save 应覆盖,不是追加。"""
        client.put('/api/layout/save', json={'items': [{'v': 1}]}, headers=auth_headers('alice'))
        client.put('/api/layout/save', json={'items': [{'v': 2}, {'v': 3}]}, headers=auth_headers('alice'))
        r = client.get('/api/layout/get', headers=auth_headers('alice'))
        assert r.get_json()['data']['items'] == [{'v': 2}, {'v': 3}]

    def test_save_items_not_list_returns_400(self, client, auth_headers):
        """items 必须是 list,否则 400。"""
        r = client.put(
            '/api/layout/save',
            json={'items': 'not a list'},
            headers=auth_headers('alice'),
        )
        assert r.status_code == 400
        assert 'list' in r.get_json()['message'].lower()

    def test_save_too_many_items_returns_400(self, client, auth_headers):
        """items 数量超过 MAX_ITEMS(200) → 400。"""
        big = [{'i': str(i)} for i in range(201)]
        r = client.put(
            '/api/layout/save',
            json={'items': big},
            headers=auth_headers('alice'),
        )
        assert r.status_code == 400
        assert 'too many' in r.get_json()['message'].lower()

    def test_save_without_auth_returns_401(self, client):
        """未带 token 应 401。"""
        r = client.put('/api/layout/save', json={'items': []})
        assert r.status_code == 401