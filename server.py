import logging
import os

from flask import Flask
from flask_cors import CORS

import config
from blueprintStore.auth import auth_blue
from blueprintStore.layout import layout_blue
from blueprintStore.library import library_blue
from blueprintStore.news import news_blue
from blueprintStore.pages import pages_blue
from classStore.common.db import init_db
from classStore.common.errors import register_error_handlers
from classStore.common.limiter import limiter
from classStore.common.logging_setup import setup_logging

app = Flask(__name__)

# CORS origin 白名单:从 CORS_ORIGINS env 读取,逗号分隔
# 缺省值仅供本地开发使用,生产必须显式注入(如 CORS_ORIGINS=https://app.example.com)
_default_origins = 'http://localhost:5173,http://127.0.0.1:5173'
_cors_origins = os.environ.get('CORS_ORIGINS', _default_origins)
_cors_origin_list = [o.strip() for o in _cors_origins.split(',') if o.strip()]
CORS(app, origins=_cors_origin_list, supports_credentials=True)
logging.getLogger(__name__).info(
    'CORS allowed origins: %s (set CORS_ORIGINS env to override)',
    _cors_origin_list
)

# Rate limit 存储:生产用 Redis,测试用 SQLite(隔离),缺省用内存
# RATELIMIT_STORAGE_URI 示例:
#   redis://localhost:6379/0   (生产)
#   sqlite:///path/to/db       (测试)
#   memory://                  (开发)
_default_storage = 'memory://'
app.config['RATELIMIT_STORAGE_URI'] = os.environ.get('RATELIMIT_STORAGE_URI', _default_storage)
logging.getLogger(__name__).info(
    'Rate limit storage: %s (set RATELIMIT_STORAGE_URI env to override)',
    app.config['RATELIMIT_STORAGE_URI']
)

app.config.from_object(config.Config)

init_db()

app.register_blueprint(auth_blue)
app.register_blueprint(pages_blue)
app.register_blueprint(library_blue)
app.register_blueprint(layout_blue)
app.register_blueprint(news_blue)

limiter.init_app(app)

register_error_handlers(app)

# 日志必须在 app.config / limiter / error handler 全部就位后再 setup,
# 否则 setup 之前产生的启动日志会落到 root logger 而非 app.logger,
# 出现"切了归档但启动 banner 漏了"的诡异现象
setup_logging(app)
app.logger.info('Flask_library module loaded; blueprints registered')


if __name__ == '__main__':
    app.logger.info('Flask_library starting on http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000)
