"""Rate limit 模块。

Limiter 实例在模块加载时创建(不绑定 app),避免循环 import。
具体绑定在 server.py 末尾通过 limiter.init_app(app) 完成。
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
)
