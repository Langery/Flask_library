from userPwd import Password

class Config(object):
  DEBUG = True

class SQLConfig(object):
  host = '106.14.190.190'
  port = 7306
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
