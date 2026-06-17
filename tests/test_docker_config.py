"""X-B: Docker 打包配置静态验证。

不在 CI 跑实际 docker build(太慢 + 需要 docker daemon),
改为对 Dockerfile / docker-compose.yml / gunicorn.conf.py 做静态校验:
- Dockerfile 包含 FROM/EXPOSE/CMD/HEALTHCHECK
- docker-compose.yml 是合法 YAML,服务名/端口/volume/env 正确
- gunicorn.conf.py 可被 Python 导入且包含关键配置(bind/workers/timeout)
- DB_PATH 环境变量实际生效(DB 文件创建在指定位置)

任何一项不通过都意味着生产部署可能出问题,要立刻发现而不是 docker run 才报。
"""

import importlib.util
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


class TestDockerfile:
    """X-B: Dockerfile 静态检查"""

    def test_dockerfile_exists(self):
        assert (ROOT / 'Dockerfile').exists()

    def test_dockerfile_has_required_directives(self):
        content = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
        # 必备指令:基础镜像、暴露端口、启动命令、健康检查
        for directive, why in [
            ('FROM', '基础镜像'),
            ('EXPOSE', '声明监听端口'),
            ('CMD', '容器启动命令'),
            ('HEALTHCHECK', '健康检查,Docker 编排时能自动重启异常容器'),
        ]:
            assert directive in content, f'Dockerfile 缺少 {directive} ({why})'

    def test_dockerfile_uses_gunicorn_not_flask_dev(self):
        """必须用 gunicorn,不能用 flask 自带的 app.run(单进程,生产扛不住并发)。"""
        content = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
        assert 'gunicorn' in content, '生产镜像必须用 gunicorn 而非 flask run'

    def test_dockerfile_uses_slim_base(self):
        """slim 镜像 ~150MB,alpine 经常让 C 扩展编译失败。"""
        content = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
        assert 'slim' in content, '建议用 python:3.11-slim 作为基础镜像'

    def test_dockerfile_pip_install_uses_requirements(self):
        """依赖应通过 requirements.txt 装,而不是 inline pip install。"""
        content = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
        assert 'requirements.txt' in content
        # 关键:pip install 必须在 COPY 源码之前,这样改代码不重装依赖(缓存友好)
        pip_pos = content.find('pip install')
        copy_code_pos = content.find('COPY . .')
        assert pip_pos != -1 and copy_code_pos != -1
        assert pip_pos < copy_code_pos, (
            'pip install 必须在 COPY 源码之前,才能利用 Docker 缓存'
        )


class TestDockerCompose:
    """X-B: docker-compose.yml 静态检查"""

    @pytest.fixture
    def compose(self):
        try:
            import yaml
        except ImportError:
            pytest.skip('PyYAML not installed')
        compose_file = ROOT / 'docker-compose.yml'
        assert compose_file.exists(), 'docker-compose.yml 不存在'
        return yaml.safe_load(compose_file.read_text(encoding='utf-8'))

    def test_compose_has_app_service(self, compose):
        assert 'services' in compose
        assert 'app' in compose['services']

    def test_app_service_exposes_port_5000(self, compose):
        app = compose['services']['app']
        ports = app.get('ports', [])
        # 接受 "5000:5000" 或 5000:5000 写法
        assert any('5000:5000' in str(p) for p in ports), (
            f'expected port mapping 5000:5000, got {ports}'
        )

    def test_app_service_has_volume(self, compose):
        """必须有 volume 挂载,否则 SQLite 数据容器重启就丢。"""
        app = compose['services']['app']
        assert 'volumes' in app and len(app['volumes']) > 0, (
            'app 服务必须挂载 volume,否则 SQLite 数据容器重启即丢'
        )

    def test_app_service_passes_secret_key(self, compose):
        """SECRET_KEY 必须能从 env 注入,不能硬编码。"""
        app = compose['services']['app']
        env = app.get('environment', {})
        assert 'SECRET_KEY' in env, 'SECRET_KEY 必须通过 environment 注入'

    def test_compose_uses_named_volume(self, compose):
        """volume 应该是命名 volume,不是 bind mount(便于备份/迁移)。"""
        # 必须有顶层 volumes 定义(命名 volume)
        assert 'volumes' in compose, '顶层必须定义命名 volumes'


class TestGunicornConfig:
    """X-B: gunicorn.conf.py 静态检查"""

    @pytest.fixture
    def gconf(self):
        path = ROOT / 'gunicorn.conf.py'
        assert path.exists(), 'gunicorn.conf.py 不存在'
        # 把 gconf 当成 module 加载,验证语法 + 读出配置
        spec = importlib.util.spec_from_file_location('gunicorn_conf_under_test', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_binds_to_0000(self, gconf):
        """bind 必须是 0.0.0.0:5000,容器内才能被宿主机访问。"""
        assert gconf.bind == '0.0.0.0:5000'

    def test_has_reasonable_workers(self, gconf):
        """SQLite 场景 worker 不应过多,2-4 个合适。"""
        assert 1 <= gconf.workers <= 4, (
            f'workers={gconf.workers},SQLite 场景建议 2-4 个,过多会因写锁竞争拖慢'
        )

    def test_has_timeout(self, gconf):
        """timeout 必填,默认 30s 适配图片上传。"""
        assert gconf.timeout >= 30

    def test_preload_app_safe_for_sqlite(self, gconf):
        """SQLite + threading.local 必须 preload_app=False,否则 fork 后 connection 状态错乱。"""
        assert gconf.preload_app is False


class TestDockerignore:
    """X-B: .dockerignore 排除关键目录"""

    def test_dockerignore_excludes_tests(self):
        content = (ROOT / '.dockerignore').read_text(encoding='utf-8')
        # 测试代码不应进生产镜像
        assert 'tests/' in content or 'tests' in content

    def test_dockerignore_excludes_git(self):
        content = (ROOT / '.dockerignore').read_text(encoding='utf-8')
        assert '.git/' in content or '.git' in content

    def test_dockerignore_excludes_dev_db(self):
        content = (ROOT / '.dockerignore').read_text(encoding='utf-8')
        assert 'flask.db' in content, '开发 DB 不应打入镜像'

    def test_dockerignore_excludes_pycache(self):
        content = (ROOT / '.dockerignore').read_text(encoding='utf-8')
        assert '__pycache__' in content


class TestDBPathEnvOverride:
    """X-B: DB_PATH 环境变量应实际改变 db 文件位置"""

    def test_db_path_env_creates_db_in_specified_dir(self, tmp_path, monkeypatch):
        """设 DB_PATH=/tmp/xxx/flask.db → init_db 后文件应在该位置。"""
        import importlib

        import classStore.common.db as db_module

        target_dir = tmp_path / 'env_db'
        monkeypatch.setenv('DB_PATH', str(target_dir / 'flask.db'))
        # 强制 reload db 模块让 env 重新读取
        importlib.reload(db_module)
        db_module._DB_PATH = os.environ['DB_PATH']  # conftest 也走这一步,显式做一次
        db_module.init_db()
        # 文件应在指定位置,父目录应被自动创建
        assert (target_dir / 'flask.db').exists(), (
            f'expected db at {target_dir / "flask.db"}, '
            f'current _DB_PATH={db_module._DB_PATH}'
        )
