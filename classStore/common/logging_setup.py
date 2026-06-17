"""统一的日志配置:按天切分 + JSON 结构化 + 双写 stdout/文件。

设计要点:
- 模块级别挂载:`setup_logging(app)` 之后 flask run / gunicorn / __main__ 都生效
- TimedRotatingFileHandler:按天切分,保留 30 天(可配),不会无限增长
- StreamHandler(sys.stdout):容器化部署时日志能被 docker/k8s log-driver 抓取
- propagate=False:避免 root logger 也配 handler 时的双写
- JSON 格式可选:LOG_FORMAT=json 走结构化,Grok/Loki/ES 友好;text 走传统可读
"""
import json
import logging
import logging.handlers
import os
import sys
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """JSON Lines 格式:每行一个完整 JSON,字段固定,便于日志聚合工具解析。"""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'ts': datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'msg': record.getMessage(),
            'module': record.module,
            'func': record.funcName,
            'line': record.lineno,
        }
        if record.exc_info:
            payload['exc'] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(
    app,
    log_dir: str | None = None,
    level: str | None = None,
    fmt: str | None = None,
    backup_days: int = 30,
):
    """为 Flask app 装配按天切分的文件 handler + stdout handler。

    Args:
        app: Flask 应用实例
        log_dir: 日志目录;None 时从环境变量 LOG_DIR 读,缺省 'log'
        level: 日志级别;None 时从 LOG_LEVEL 读,缺省 INFO
        fmt: 'text' 或 'json';None 时从 LOG_FORMAT 读,缺省 'text'
        backup_days: 保留多少天的归档,超过自动删除

    Returns:
        配置到 app.logger 上的 handler 列表(测试用)
    """
    log_dir = log_dir or os.environ.get('LOG_DIR', 'log')
    level_name = (level or os.environ.get('LOG_LEVEL', 'INFO')).upper()
    fmt = (fmt or os.environ.get('LOG_FORMAT', 'text')).lower()

    os.makedirs(log_dir, exist_ok=True)

    numeric_level = getattr(logging, level_name, logging.INFO)
    formatter = _build_formatter(fmt)

    handlers = [
        _make_file_handler(log_dir, formatter, backup_days),
        _make_stream_handler(formatter),
    ]

    # 清掉旧 handler(避免重复挂载 + 解决 reload 时累积)
    logger = app.logger
    for h in list(logger.handlers):
        logger.removeHandler(h)
    for h in handlers:
        logger.addHandler(h)
    logger.setLevel(numeric_level)
    # 关闭向上传播:避免 root logger 也配 handler 导致同一条日志写两次
    logger.propagate = False
    return handlers


def _build_formatter(fmt: str) -> logging.Formatter:
    if fmt == 'json':
        return JSONFormatter()
    # 传统文本:与旧 server.py 保持兼容,带模块/函数/行号便于排查
    return logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s'
    )


def _make_file_handler(log_dir: str, formatter: logging.Formatter, backup_days: int):
    fh = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        when='midnight',
        interval=1,
        backupCount=backup_days,
        encoding='utf-8',
        utc=False,
    )
    # suffix 决定切分后的文件名:app.log.2026-06-17
    fh.suffix = '%Y-%m-%d'
    fh.setFormatter(formatter)
    return fh


def _make_stream_handler(formatter: logging.Formatter):
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    return sh
