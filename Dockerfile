# syntax=docker/dockerfile:1.6
# X-B: Flask_library 容器化镜像
# 基础镜像:python:3.11-slim(Debian-based,C 扩展编译友好;~150MB)
# Alpine 镜像虽小但 musl libc 经常让 cryptography/psycopg2 编译失败,新手先稳

FROM python:3.11-slim AS base

# 时区与 locale,日志时间戳与本地对齐
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=UTC

# 系统依赖:sqlite3 已经在 python:3.11-slim 镜像里,不需要额外装
# 但 curl 是 healthcheck 需要的(轻量,~100KB)
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先只 copy requirements,利用 Docker 缓存(改代码不重装依赖)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 再 copy 源码
COPY . .

# 持久化数据目录:DB 文件 + 日志归档都放这里,volume 挂进来
RUN mkdir -p /data/log && chmod 755 /data

# 生产环境用 env 注入;缺省值仅供本地 docker run 用
ENV DB_PATH=/data/flask.db \
    LOG_DIR=/data/log \
    LOG_FORMAT=text \
    LOG_LEVEL=INFO \
    RATELIMIT_STORAGE_URI=memory:// \
    PORT=5000

# 健康检查:容器内 curl /api/health,失败 → 重启
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:5000/api/health || exit 1

EXPOSE 5000

# 启动 gunicorn,配置从文件读
# 不用 flask 自带的 app.run(单进程,Werkzeug 性能差)
CMD ["gunicorn", "-c", "gunicorn.conf.py", "server:app"]
