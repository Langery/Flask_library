import os
import logging
from flask import Flask
from flask_cors import CORS
from classStore.common.limiter import limiter
from classStore.common.errors import register_error_handlers
from classStore.common.db import init_db
from blueprintStore.pages import pages_blue
from blueprintStore.auth import auth_blue
from blueprintStore.library import library_blue
from blueprintStore.layout import layout_blue
from blueprintStore.news import news_blue
import config

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


if __name__ == '__main__':
    if not os.path.exists('log'):
        os.makedirs('log')
    handler = logging.FileHandler('log/app.log', encoding='UTF-8')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info('Flask_library starting on http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000)
