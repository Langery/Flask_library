from DBUtils.PersistentDB import PersistentDB
import pymysql

# POOL information
class POOL():
  def __init__(self):
    print('pool.init')
  def config(self, SQLConfig):
    POOL = PersistentDB(
      creator = pymysql, # use data model
      maxusage = None, # used more times
      setsession = [], # the order list before start
      # ping = 0, # check MySQL server is available
      ping = 2,
      closeable = False, # ignored the `conn.close()` ,
      threadlocal = None, # save the link object
      host = SQLConfig.host,
      port = SQLConfig.port,
      user = SQLConfig.user,
      password = SQLConfig.password,
      database = SQLConfig.database,
      charset = SQLConfig.charset
    )
    return POOL