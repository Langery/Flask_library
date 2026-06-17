"""News FTS5 搜索回归测试。

验证:
- 单 token 前缀匹配 (q=News 命中 News #11)
- 多 token AND 语义 (q=News+11 必须两个 token 都命中)
- 无匹配返回空 total
- 纯特殊字符被剥离后等价于无搜索
- FTS5 触发器自动同步(直接 INSERT 后能搜到)
"""
import pytest


class TestNewsFtsSearch:
    """X-L: /news/list?q= 走 SQLite FTS5 倒排索引。"""

    def test_fts_finds_single_word(self, client, auth_headers):
        """单 token 前缀匹配:q=News 命中 News #11..#19 等"""
        r = client.get('/news/list?q=News&_limit=5', headers=auth_headers('alice'))
        assert r.status_code == 200
        items = r.get_json()['data']['items']
        # seed 标题形如 "News #11: ...",News 前缀匹配应至少命中 1 条
        assert len(items) >= 1
        assert all('News' in it['title'] for it in items)

    def test_fts_multi_token_and_semantics(self, client, auth_headers):
        """多 token 走 AND 语义:q=News+11 必须同时含 News 和 11 → News #11..#19"""
        r = client.get('/news/list?q=News+11&_limit=20', headers=auth_headers('alice'))
        assert r.status_code == 200
        items = r.get_json()['data']['items']
        # 全部标题必须同时包含 News 和 11
        assert all('News' in it['title'] and '11' in it['title'] for it in items)
        assert len(items) >= 1

    def test_fts_no_match_returns_empty(self, client, auth_headers):
        """不存在的关键词 → total=0,items=[]"""
        r = client.get('/news/list?q=xyzzy_no_such_token', headers=auth_headers('alice'))
        assert r.status_code == 200
        body = r.get_json()['data']
        assert body['total'] == 0
        assert body['items'] == []

    def test_fts_pure_special_chars_falls_back_to_all(self, client, auth_headers):
        """纯特殊字符(被全部 strip 后无有效 token)→ 等价无搜索,返回全表"""
        r = client.get('/news/list?q=!@%23%24&_limit=5', headers=auth_headers('alice'))
        assert r.status_code == 200
        items = r.get_json()['data']['items']
        # 应返回种子数据,不是空
        assert len(items) == 5

    def test_fts_trigger_syncs_direct_insert(self, client, auth_headers):
        """触发器自动同步:绕过 route 直接 INSERT news 行,FTS 也能搜到"""
        from classStore.common.db import execute
        execute(
            'INSERT INTO news (id, user_id, title, body, created_at) VALUES (?, ?, ?, ?, ?)',
            (9999, 1, 'unique_fts_marker_xyz', 'body text', '2026-01-01T00:00:00')
        )
        r = client.get('/news/list?q=unique_fts_marker', headers=auth_headers('alice'))
        assert r.status_code == 200
        items = r.get_json()['data']['items']
        # 触发器应已把这一行写入 news_fts
        assert any('unique_fts_marker' in it['title'] for it in items)