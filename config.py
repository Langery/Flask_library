"""Flask_library 配置:按场景分层的 Config + 工厂函数。

设计:
- BaseConfig/DevConfig/TestConfig/ProdConfig:定义静态默认值
- get_config(name):返回 dict(供 app.config.update),SECRET_KEY 在调用时读 env
  - 这样既能在测试运行时切换 env(不用 reload 模块),也能在生产启动时立刻
    检测到 SECRET_KEY 缺失并抛错
- ProdConfig.SECRET_KEY 缺失:启动即 RuntimeError,绝不静默 fallback

入口:server.py 用 app.config.update(config.get_config()) 一行搞定。
环境切换:APP_ENV=development|testing|production(也可传参给 get_config)。
"""
import logging
import os

from userInfo import Password

logger = logging.getLogger(__name__)


class BaseConfig:
    """所有场景共享的静态默认值。SECRET_KEY 在 get_config() 中动态读 env。"""

    DEBUG = False
    TESTING = False

    # Flask 框架基础
    JSON_SORT_KEYS = False

    # 跨域白名单,server.py 还会再读 CORS_ORIGINS env 覆盖
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
    )

    # 限流存储:子类按需覆盖
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    # 日志(由 classStore.common.logging_setup 读取)
    LOG_DIR = os.environ.get('LOG_DIR', 'log')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'text')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # DB 路径:classStore.common.db 读取
    DB_PATH = os.environ.get('DB_PATH')


class DevConfig(BaseConfig):
    """本地开发:DEBUG 打开,日志尽量详细,限流走内存。"""

    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestConfig(BaseConfig):
    """pytest 用:TESTING=True,日志降到 WARNING(避免 100+ 测试刷屏)。"""

    TESTING = True
    LOG_LEVEL = 'WARNING'


class ProdConfig(BaseConfig):
    """生产:DEBUG 必须关,SECRET_KEY 缺失即抛错(在 get_config() 中检查)。"""

    DEBUG = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


# 工厂:按 APP_ENV 选 Config,缺省 development
_CONFIGS = {
    'development': DevConfig,
    'dev': DevConfig,
    'testing': TestConfig,
    'test': TestConfig,
    'production': ProdConfig,
    'prod': ProdConfig,
}

# SECRET_KEY 缺省值(仅 Dev 用,Test 走测试固定值,Prod 走必填检查)
_DEV_SECRET_FALLBACK = 'dev-insecure-secret-CHANGE-ME'
_TEST_SECRET_DEFAULT = 'test-secret-key-for-pytest-only-32B'


def get_config(name: str | None = None) -> dict:
    """按场景返回配置 dict,供 app.config.update() 使用。

    关键设计:SECRET_KEY 在调用时读 env(而不是 class 定义时),
    这样:
    - 测试可以先 setenv 再 get_config 拿到对应值,不需要 reload config 模块
    - 缺失 SECRET_KEY 的生产启动会立刻抛 RuntimeError,不会带着默认密钥上线

    Returns:
        dict,所有 key 都是大写,符合 Flask config 约定
    """
    name = (name or os.environ.get('APP_ENV', 'development')).lower()
    if name not in _CONFIGS:
        raise ValueError(
            f'unknown APP_ENV={name!r}, expected one of: {sorted(set(_CONFIGS))}'
        )
    cls = _CONFIGS[name]

    # 1. 收集类的静态属性(走 MRO 拿继承的属性,不能只用 vars(cls))
    # MRO 顺序:子类 → 父类 → object,所以反向遍历,让子类的赋值覆盖父类
    cfg = {}
    for klass in reversed(cls.__mro__):
        for key, value in vars(klass).items():
            if key.isupper() and not key.startswith('_') and not callable(value):
                cfg[key] = value

    # 2. SECRET_KEY 单独处理:按场景决定来源
    env_secret = os.environ.get('SECRET_KEY')
    if name in ('production', 'prod'):
        if not env_secret:
            raise RuntimeError(
                'SECRET_KEY 环境变量未设置。生产环境必须显式注入,'
                '可用 `python3 -c "import secrets; print(secrets.token_hex(32))"` 生成'
            )
        cfg['SECRET_KEY'] = env_secret
    elif name in ('testing', 'test'):
        cfg['SECRET_KEY'] = env_secret or _TEST_SECRET_DEFAULT
    else:
        # development:env 优先,缺省用 insecure 提醒字符串
        cfg['SECRET_KEY'] = env_secret or _DEV_SECRET_FALLBACK

    return cfg


# ========================================================================
# 向后兼容:旧代码(server.py / tests/test_auth.py)引用的旧符号保留
# ========================================================================

# 旧 Config 类 → DevConfig(让 `from config import Config` 继续可用)
Config = DevConfig

SQLConfig = type('SQLConfig', (), {
    'host': '127.0.0.1',
    'port': 3306,
    'charset': 'utf8',
    'user': property(lambda self: Password.user),
    'password': property(lambda self: Password.password),
    'database': property(lambda self: Password.database),
})

# 旧 config dict(仅供外部脚本 import,不强制)
config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig,
    'sqlLink': SQLConfig,
}
