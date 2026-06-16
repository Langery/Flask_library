import os
# from userPwd import Password
from userInfo import Password

class Config(object):
  DEBUG = True
  TESTING = True
  SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()

class SQLConfig(object):
  host = '127.0.0.1'
  port = 3306
  charset = 'utf8'
  user = Password.user
  password = Password.password
  database = Password.database

class TestConfig(object):
  TESTING = True

config = {
  'development': '',
  'testing': TestConfig,
  'production': '',
  'sqlLink': SQLConfig
}
