import os
import logging
# from userPwd import Password
from userInfo import Password

logger = logging.getLogger(__name__)

class Config(object):
  DEBUG = True
  TESTING = True
  _env_secret = os.environ.get('SECRET_KEY')
  if not _env_secret:
    logger.warning(
      'SECRET_KEY 环境变量未设置,使用 urandom 生成进程级密钥。'
      '重启后所有 JWT token 将失效。生产环境必须显式注入 SECRET_KEY。'
    )
    SECRET_KEY = os.urandom(32).hex()
  else:
    SECRET_KEY = _env_secret

class SQLConfig(object):
  """MySQL 配置。字段用 property 实现,每次访问读 env,便于测试隔离。"""
  host = '127.0.0.1'
  port = 3306
  charset = 'utf8'

  @property
  def user(self):
    return Password.user

  @property
  def password(self):
    return Password.password

  @property
  def database(self):
    return Password.database

class TestConfig(object):
  TESTING = True

config = {
  'development': '',
  'testing': TestConfig,
  'production': '',
  'sqlLink': SQLConfig
}