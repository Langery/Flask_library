import sqlite3
import threading
import os

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
    conn.commit()
    conn.close()

    from blueprintStore.news.seed import seed_news_if_empty
    seeded = seed_news_if_empty()
    if seeded:
        import logging
        logging.getLogger('flask.app').info(f'News seed injected: {seeded} posts')
