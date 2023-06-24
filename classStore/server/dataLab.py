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

# SQL Type
class SQLFun():
  def __init__(self, way, lab):
    self.way = way
    self.lab = lab
    #TODO selectway 改成map  遍历数组生成SQL语句
  def search(self):
    way = self.way
    lab = self.lab
    return  'SELECT ' + way + ' FROM ' + lab;
  def select(self, selectway):
  # def select(self, *key):
    way = self.way
    lab = self.lab
    return 'SELECT ' + way + ' FROM ' + lab + ' WHERE ' + selectway + '='
    # SELECT * FROM `event` WHERE userId = "" and createTime = 11 AND isNew = 1;
  def selectStr(self, selectway, variable):
  # def select(self, *key):
    way = self.way
    lab = self.lab
    return 'SELECT ' + way + ' FROM ' + lab + ' WHERE ' + selectway + '= "' + variable + '"'
    # SELECT * FROM `event` WHERE userId = "" and createTime = 11 AND isNew = 1;
  def selectMoreObj(self, *key):
    lab = self.lab
    way = self.way
    newAdd = ''
    for index, everyOne in enumerate(key):
      newAdd += everyOne + '=%s and'

    newAdd = newAdd[:-5]

    return 'SELECT ' + way + ' FROM ' + lab + ' WHERE ' + newAdd


  def add(self, *key):
    lab = self.lab
    valueS = ''
    keyS = ''
    for index, everyOne in enumerate(key):
      keyS += everyOne+','
      valueS += '%s,'

    keyS = keyS[:-1]
    valueS = valueS[:-1]

    return 'INSERT INTO ' + lab + ' (' + keyS + ')' + ' VALUES (' + valueS + ')'
  def like(self, selectway, obj_param):
    way = self.way
    lab = self.lab
    return '''SELECT {} FROM {} WHERE {} LIKE "{}%"'''.format(way, lab, selectway, obj_param)
  def select_timestamp(self, selectway, obj_param, new_param):
    way = self.way
    lab = self.lab

    return 'SELECT ' + way + ' FROM ' + lab + ' WHERE ' + str(obj_param) + ' < ' + selectway + ' < ' + str(new_param)

