import sqlite3
import threading

class POOL:
    def __init__(self):
        print('pool.init')

    def config(self, SQLConfig=None):
        return SQLitePool()

class SQLitePool:
    def __init__(self):
        self.db_path = 'flask.db'
        self._local = threading.local()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
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

    def connection(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def cursor(self):
        return self.connection().cursor()