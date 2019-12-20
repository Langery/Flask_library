from DBUtils.PersistentDB import PersistentDB
import pymysql

class POOL():
  def __init__(self):
    print('pool.init')
  def config(self, SQLConfig):
    POOL = PersistentDB(
      creator = pymysql, # use data model
      maxusage = None, # used more times
      setsession = [], # the order list before start
      ping = 0, # check MySQL server is available
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

class SQLFun():
  def __init__(self, way, lab):
    print('sql way')
    self.way = way
    self.lab = lab
  def select(self, selectway):
    way = self.way
    lab = self.lab
    return 'SELECT ' + way + ' FROM ' + lab + ' WHERE ' + selectway + '=%s'
  def add(self, *key):
    print(key)
    print(type(key))
    lab = self.lab
    valueS = ''
    keyS = ''
    for index, everyOne in enumerate(key):
      keyS += everyOne+','
      valueS += '%s,'
    # find = 'insert into login(name, pwd, nickname) values(%s, %s, %s)'
    # endFind = cursor.execute(find, [username, password, ''])
    # print(endFind)
    keyS = keyS[:-1]
    valueS = valueS[:-1]
    print(keyS)
    print(valueS)
    print('INSERT INTO ' + lab + ' (' + keyS + ')' + ' VALUES (' + valueS + ')')
    return 'INSERT INTO ' + lab + ' (' + keyS + ')' + ' VALUES (' + valueS + ')'
  def like(self, selectway, obj_param):
    way = self.way
    lab = self.lab
    # 'SELECT {} FROM {} WHERE {} LIKE {}%'.format(way, lab, selectway)
    # return 'SELECT ' + way + ' FROM ' + lab + ' WHERE ' + selectway + ' LIKE ' + '("% %s %")'
    return '''SELECT {} FROM {} WHERE {} LIKE "{}%"'''.format(way, lab, selectway, obj_param)
