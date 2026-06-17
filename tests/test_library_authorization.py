"""Library 接口回归测试 — 验证已有 403 保护仍生效。"""
import pytest


class TestLibraryCRUD:
    def test_add_then_list_returns_item(self, client, auth_headers):
        r = client.post('/library/add', json={
            'name': 'Test Book',
            'age': '2024',
            'nickname': 'tb'
        }, headers=auth_headers('alice'))
        assert r.status_code == 200
        item = r.get_json()['data']['item']
        assert item['name'] == 'Test Book'
        assert len(item['id']) == 32  # uuid4 hex

    def test_add_without_name_returns_400(self, client, auth_headers):
        r = client.post('/library/add', json={'age': '2024'}, headers=auth_headers('alice'))
        assert r.status_code == 400

    def test_list_isolated_per_user(self, client, auth_headers):
        """Alice 添加的项,Bob 的列表不应看到。"""
        client.post('/library/add', json={'name': 'Alice Secret'}, headers=auth_headers('alice'))

        r = client.get('/library/list', headers=auth_headers('bob'))
        assert r.status_code == 200
        items = r.get_json()['data']['items']
        assert all(it['name'] != 'Alice Secret' for it in items)


class TestLibraryAuthorization:
    """已有的跨用户 403 保护 — 任何 refactor 都不应破坏它。"""

    def test_other_user_cannot_delete_my_item(self, client, auth_headers):
        # Alice 创建
        r = client.post('/library/add', json={'name': 'Alice Item'}, headers=auth_headers('alice'))
        item_id = r.get_json()['data']['item']['id']

        # Bob 尝试删除
        r = client.delete(f'/library/delete/{item_id}', headers=auth_headers('bob'))
        assert r.status_code == 403

        # Alice 列表里还在
        r = client.get('/library/list', headers=auth_headers('alice'))
        items = r.get_json()['data']['items']
        assert any(it['id'] == item_id for it in items)

    def test_owner_can_delete_own_item(self, client, auth_headers):
        r = client.post('/library/add', json={'name': 'My Item'}, headers=auth_headers('alice'))
        item_id = r.get_json()['data']['item']['id']

        r = client.delete(f'/library/delete/{item_id}', headers=auth_headers('alice'))
        assert r.status_code == 200

    def test_delete_nonexistent_item_returns_404(self, client, auth_headers):
        r = client.delete('/library/delete/nonexistent_id_12345', headers=auth_headers('alice'))
        assert r.status_code == 404

    def test_clear_only_affects_own_items(self, client, auth_headers):
        client.post('/library/add', json={'name': 'A1'}, headers=auth_headers('alice'))
        client.post('/library/add', json={'name': 'A2'}, headers=auth_headers('alice'))
        client.post('/library/add', json={'name': 'B1'}, headers=auth_headers('bob'))

        r = client.post('/library/clear', headers=auth_headers('alice'))
        assert r.status_code == 200
        assert r.get_json()['data']['cleared'] == 2

        # Bob 的还在
        r = client.get('/library/list', headers=auth_headers('bob'))
        items = r.get_json()['data']['items']
        assert len(items) == 1
        assert items[0]['name'] == 'B1'