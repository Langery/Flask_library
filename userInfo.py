import os


class _Password(object):
    """数据库连接配置。实例属性(property)每次访问时读 env,便于测试隔离。"""

    @property
    def user(self):
        return os.environ['SQL_USER']

    @property
    def password(self):
        return os.environ['SQL_PASSWORD']

    @property
    def database(self):
        return os.environ['SQL_DATABASE']


# 模块级单例,保持 `Password.user` 调用方式兼容
Password = _Password()