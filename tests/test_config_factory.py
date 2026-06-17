"""X-C: Config 分场景测试。

覆盖:
- get_config('development'/'dev') → dict 含 DEBUG=True
- get_config('testing'/'test') → dict 含 TESTING=True, LOG_LEVEL=WARNING
- get_config('production'/'prod') → dict 含 DEBUG=False, 缺 SECRET_KEY 抛 RuntimeError
- 缺省 APP_ENV → development
- 无效 APP_ENV → ValueError
- get_config() 在调用时读 env(不依赖 class 定义时机)
- 旧 `from config import Config` 向后兼容
- server.app.config 实际反映 APP_ENV=test 时的 TestConfig
"""


class TestGetConfigByName:
    """X-C: get_config(name) 直接调用"""

    def test_development_returns_dict_with_debug(self):
        from config import get_config
        cfg = get_config('development')
        assert isinstance(cfg, dict)
        assert cfg['DEBUG'] is True
        assert cfg['TESTING'] is False

    def test_dev_alias(self):
        from config import get_config
        cfg = get_config('dev')
        assert cfg['DEBUG'] is True

    def test_testing_returns_dict_with_testing_flag(self):
        from config import get_config
        cfg = get_config('testing')
        assert cfg['TESTING'] is True
        assert cfg['DEBUG'] is False
        # 测试场景日志降级到 WARNING,避免 100+ 测试刷屏
        assert cfg['LOG_LEVEL'] == 'WARNING'

    def test_test_alias(self):
        from config import get_config
        cfg = get_config('test')
        assert cfg['TESTING'] is True

    def test_production_returns_dict_with_debug_false(self, monkeypatch):
        from config import get_config
        monkeypatch.setenv('SECRET_KEY', 'prod-test-secret-key')
        cfg = get_config('production')
        assert cfg['DEBUG'] is False
        assert cfg['TESTING'] is False
        assert cfg['SECRET_KEY'] == 'prod-test-secret-key'

    def test_prod_alias(self, monkeypatch):
        from config import get_config
        monkeypatch.setenv('SECRET_KEY', 'prod-test-secret-key')
        cfg = get_config('prod')
        assert cfg['DEBUG'] is False

    def test_unknown_env_raises(self):
        from config import get_config
        with __import__('pytest').raises(ValueError, match='unknown APP_ENV'):
            get_config('staging')

    def test_name_is_case_insensitive(self):
        from config import get_config
        cfg = get_config('DEVELOPMENT')
        assert cfg['DEBUG'] is True


class TestGetConfigFromEnv:
    """X-C: get_config() 不传参时从 APP_ENV 读"""

    def test_reads_app_env_var(self, monkeypatch):
        """APP_ENV=production → ProdConfig dict,DEBUG=False。"""
        from config import get_config
        monkeypatch.setenv('APP_ENV', 'production')
        monkeypatch.setenv('SECRET_KEY', 'env-test-secret')
        cfg = get_config()
        assert cfg['DEBUG'] is False
        assert cfg['SECRET_KEY'] == 'env-test-secret'

    def test_defaults_to_development(self, monkeypatch):
        """APP_ENV 未设 → DevConfig 形态。"""
        from config import get_config
        monkeypatch.delenv('APP_ENV', raising=False)
        cfg = get_config()
        assert cfg['DEBUG'] is True

    def test_secret_key_read_at_call_time(self, monkeypatch):
        """关键设计:get_config() 在调用时读 env,不是 class 定义时。
        这意味着测试可以先 setenv 再调用,不需要 reload config 模块。
        """
        from config import get_config
        # 清掉 conftest 设的 SECRET_KEY
        monkeypatch.delenv('SECRET_KEY', raising=False)
        # 此时 get_config('testing') 走 TestConfig fallback
        cfg = get_config('testing')
        assert cfg['SECRET_KEY'] == 'test-secret-key-for-pytest-only-32B'
        # 现在 setenv,应立即生效
        monkeypatch.setenv('SECRET_KEY', 'freshly-set-secret')
        cfg = get_config('testing')
        assert cfg['SECRET_KEY'] == 'freshly-set-secret'


class TestProductionSecurityGuard:
    """X-C: ProdConfig 缺失 SECRET_KEY 必须抛错(绝不能静默 fallback)"""

    def test_prod_raises_when_secret_missing(self, monkeypatch):
        from config import get_config
        monkeypatch.delenv('SECRET_KEY', raising=False)
        with __import__('pytest').raises(RuntimeError, match='SECRET_KEY'):
            get_config('production')

    def test_prod_alias_also_raises(self, monkeypatch):
        from config import get_config
        monkeypatch.delenv('SECRET_KEY', raising=False)
        with __import__('pytest').raises(RuntimeError, match='SECRET_KEY'):
            get_config('prod')

    def test_dev_does_not_require_secret(self, monkeypatch):
        """DevConfig 不强制 SECRET_KEY(本地开发友好)。"""
        from config import get_config
        monkeypatch.delenv('SECRET_KEY', raising=False)
        # 不应抛错
        cfg = get_config('development')
        assert cfg['SECRET_KEY'] == 'dev-insecure-secret-CHANGE-ME'

    def test_test_does_not_require_secret(self, monkeypatch):
        """TestConfig 用固定默认 secret。"""
        from config import get_config
        monkeypatch.delenv('SECRET_KEY', raising=False)
        cfg = get_config('testing')
        assert cfg['SECRET_KEY'] == 'test-secret-key-for-pytest-only-32B'


class TestBackwardCompat:
    """X-C: 旧 `from config import Config` 仍可用"""

    def test_old_config_alias_resolves(self):
        # 旧 Config 现在是 DevConfig 的别名
        from config import Config, DevConfig
        assert Config is DevConfig

    def test_old_sqlconfig_still_exists(self):
        from config import SQLConfig
        # 应有 host/port/user/password/database 属性
        assert SQLConfig.host == '127.0.0.1'
        assert SQLConfig.port == 3306
        assert SQLConfig.charset == 'utf8'

    def test_old_config_dict_still_exists(self):
        # 旧 config['development'] 现在是 DevConfig class(不再是被 bug 掉的空串)
        from config import DevConfig, ProdConfig, TestConfig, config
        assert config['development'] is DevConfig
        assert config['testing'] is TestConfig
        assert config['production'] is ProdConfig


class TestServerUsesConfig:
    """X-C: server.app.config 实际反映 get_config() 选中的类"""

    def test_app_config_matches_testing(self, app):
        """conftest 设 APP_ENV=testing,server 启动后 app.config 应是 TestConfig 形态。"""
        # TESTING=True 是 TestConfig 的标志
        assert app.config['TESTING'] is True
        # LOG_LEVEL 是 WARNING(测试默认)
        assert app.config['LOG_LEVEL'] == 'WARNING'

    def test_app_config_has_secret_key(self, app):
        """SECRET_KEY 应来自 env(conftest 注入 'test-secret-...')。"""
        assert app.config['SECRET_KEY'] == 'test-secret-key-for-pytest-only-32B'
