"""gunicorn 生产配置。

worker 数:(2 * CPU) + 1 是社区共识,但 SQLite 场景写锁竞争明显,
硬编码到 2 个 worker 更稳。要扩 worker 请先评估 DB 迁移到 PostgreSQL。

bind: 0.0.0.0:5000(Docker 容器内必须 0.0.0.0 才能被宿主机访问)

access log:指到独立文件,与应用日志(log/app.log)分开,便于运维区分
            "用户访问"和"应用事件"两类日志

timeout: 30s 适配上传图片场景(pages/uploadImg)
"""
import multiprocessing

bind = '0.0.0.0:5000'
workers = 2
threads = 4
worker_class = 'gthread'
timeout = 30
graceful_timeout = 30
keepalive = 5

accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# preload_app:True → app 在 worker fork 之前就初始化,日志 handler / DB connection
# 在主进程挂载,避免每个 worker 都重复 init(注意:SQLite 的 threading.local 会因 fork
# 行为而失真,所以 SQLite 场景下 False 更安全,本项目 SQLite 用 False)
preload_app = False


def on_starting(server):
    """gunicorn 启动 hook,只跑一次(主进程)。
    用于打印启动 banner 到 stdout,便于 docker logs 抓取。
    """
    server.log.info('gunicorn starting with %s workers (cpu=%d)',
                    workers, multiprocessing.cpu_count())
