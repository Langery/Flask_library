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
    conn.commit()
    conn.close()
