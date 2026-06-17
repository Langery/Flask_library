import os
import sqlite3
import threading

_local = threading.local()
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'flask.db')


def _get_conn():
    if not hasattr(_local, 'conn') or _local.conn is None:
        conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _local.conn = conn
    return _local.conn


def query_all(sql, params=()):
    """执行 SELECT,返回 Row 列表"""
    cursor = _get_conn().cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()


def query_one(sql, params=()):
    """执行 SELECT,返回单条 Row 或 None"""
    cursor = _get_conn().cursor()
    cursor.execute(sql, params)
    return cursor.fetchone()


def execute(sql, params=()):
    """执行 INSERT/UPDATE/DELETE,自动 commit,返回 lastrowid"""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return cursor.lastrowid


def execute_rowcount(sql, params=()):
    """执行 INSERT/UPDATE/DELETE,自动 commit,返回受影响行数(用于 DELETE 拿删除数量)"""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return cursor.rowcount


def init_db():
    """启动时建表(已有 IF NOT EXISTS,不会丢数据)"""
    conn = sqlite3.connect(_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usertable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nickname TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listtable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            describeInfor TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS library_items (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age TEXT,
            nickname TEXT,
            create_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES usertable(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_library_user ON library_items(user_id)
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drag_layouts (
            user_id INTEGER PRIMARY KEY,
            layout_json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES usertable(id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_news_user ON news(user_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_news_title ON news(title)
    ''')

    # FTS5 虚表 + 触发器:让 /news/list 的关键词搜索从 O(n) 全扫变为倒排索引
    # content='news' + content_rowid='id' 让 FTS5 镜像原表的 rowid,UPDATE 需 delete+insert
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS news_fts USING fts5(
            title, body,
            content='news', content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        )
    ''')
    # news_ai: INSERT news → 自动写入 news_fts
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS news_ai AFTER INSERT ON news BEGIN
            INSERT INTO news_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
        END
    ''')
    # news_ad: DELETE news → 自动清理 news_fts(走 delete 命令才能级联)
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS news_ad AFTER DELETE ON news BEGIN
            INSERT INTO news_fts(news_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
        END
    ''')
    # news_au: UPDATE news → delete + insert 重建 FTS 行
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS news_au AFTER UPDATE ON news BEGIN
            INSERT INTO news_fts(news_fts, rowid, title, body) VALUES('delete', old.id, old.title, old.body);
            INSERT INTO news_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
        END
    ''')
    conn.commit()
    conn.close()

    from blueprintStore.news.seed import seed_news_if_empty
    seeded = seed_news_if_empty()
    if seeded:
        import logging
        logging.getLogger('flask.app').info(f'News seed injected: {seeded} posts')

    # FTS5 回填:news_fts 是 external content 模式(content='news'),
    # 普通 INSERT INTO news_fts SELECT ... FROM news 对索引是 no-op,
    # 必须用 'rebuild' 命令触发 FTS5 扫描 content table 重建索引
    # (首次启动 news 为空,rebuild 是空操作;老数据升级场景下补齐缺失行)
    conn = sqlite3.connect(_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO news_fts(news_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()
