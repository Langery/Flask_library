"""X-T: 日志归档 & 结构化输出测试。

覆盖:
- setup_logging 挂载 file + stream 两个 handler
- file handler 是 TimedRotatingFileHandler(when=midnight, backupCount=30)
- 写日志真的落盘(log/app.log)
- propagate=False,避免 root handler 双写
- LOG_FORMAT=json 时输出可被 json.loads 解析
- log_dir 缺省时自动创建
- backup_days 可配
"""


class TestSetupLoggingStructure:
    """X-T: handler 结构正确性"""

    def test_setup_attaches_two_handlers(self, app):
        """file + stream 各一个,不能多也不能少。
        pytest caplog 会偷偷加 LogCaptureHandler,这里按 h.stream == sys.stdout
        精确识别 setup_logging 加的那个 stream handler。
        """
        import logging
        import sys
        handlers = app.logger.handlers
        file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
        stdout_handlers = [h for h in handlers
                           if isinstance(h, logging.StreamHandler)
                           and not isinstance(h, logging.FileHandler)
                           and getattr(h, 'stream', None) is sys.stdout]
        assert len(file_handlers) == 1, f'expected 1 file handler, got {len(file_handlers)}'
        assert len(stdout_handlers) == 1, (
            f'expected 1 stdout stream handler, got {len(stdout_handlers)}: {handlers}'
        )

    def test_file_handler_is_timed_rotating(self, app):
        """file handler 必须是 TimedRotatingFileHandler,不是裸 FileHandler。"""
        import logging
        import logging.handlers
        file_handlers = [h for h in app.logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1
        fh = file_handlers[0]
        assert isinstance(fh, logging.handlers.TimedRotatingFileHandler)
        assert fh.when == 'MIDNIGHT', f'expected MIDNIGHT rotation, got {fh.when}'
        assert fh.backupCount == 30
        assert fh.encoding == 'utf-8'

    def test_propagate_disabled(self, app):
        """propagate=False:避免 root logger 重复写日志。"""
        assert app.logger.propagate is False

    def test_level_set_from_env(self, app):
        """LOG_LEVEL=INFO 缺省生效;app.logger.level 应映射到 logging.INFO。"""
        import logging
        assert app.logger.level == logging.INFO


class TestLogFileCreation:
    """X-T: 日志文件确实落盘"""

    def test_log_file_created_in_log_dir(self, app, tmp_path):
        """setup_logging 之后 log/app.log 必须出现在 LOG_DIR 下。"""
        log_dir = tmp_path / 'logs'
        # server.py import 时已调 setup_logging,此时文件应已存在
        assert log_dir.exists()
        log_file = log_dir / 'app.log'
        assert log_file.exists(), f'expected {log_file} to exist'

    def test_info_message_lands_in_file(self, app, tmp_path):
        """写一条 INFO 消息,应能在 log/app.log 中 grep 到。"""
        log_file = tmp_path / 'logs' / 'app.log'
        # 落盘需要 flush;TimedRotatingFileHandler 有自己的 emit,需要 trigger
        app.logger.info('X-T_TEST_MARKER_INFO_MESSAGE')
        for h in app.logger.handlers:
            h.flush()
        content = log_file.read_text(encoding='utf-8')
        assert 'X-T_TEST_MARKER_INFO_MESSAGE' in content

    def test_error_with_traceback_captured(self, app, tmp_path):
        """logger.exception 应把 traceback 写入日志文件。"""
        log_file = tmp_path / 'logs' / 'app.log'
        try:
            raise ValueError('X-T_TEST_MARKER_TRACEBACK')
        except ValueError:
            app.logger.exception('caught expected')
        for h in app.logger.handlers:
            h.flush()
        content = log_file.read_text(encoding='utf-8')
        assert 'caught expected' in content
        assert 'X-T_TEST_MARKER_TRACEBACK' in content
        assert 'Traceback' in content


class TestJsonFormatter:
    """X-T: JSON 结构化输出"""

    def test_json_format_produces_parseable_json(self, tmp_path, monkeypatch):
        """LOG_FORMAT=json 时,每行必须是合法 JSON。"""
        import json

        # 1. 清掉 app logger 的 handler 避免污染
        monkeypatch.setenv('LOG_DIR', str(tmp_path / 'json_logs'))
        monkeypatch.setenv('LOG_FORMAT', 'json')

        from flask import Flask

        from classStore.common.logging_setup import setup_logging
        test_app = Flask('test_json')
        setup_logging(test_app)

        test_app.logger.info('json_format_test_marker')

        # 找 file handler
        log_file = tmp_path / 'json_logs' / 'app.log'
        for h in test_app.logger.handlers:
            h.flush()
        content = log_file.read_text(encoding='utf-8')
        lines = [line for line in content.splitlines() if 'json_format_test_marker' in line]
        assert len(lines) == 1
        # 关键:必须能 json.loads 解析
        parsed = json.loads(lines[0])
        assert parsed['msg'] == 'json_format_test_marker'
        assert parsed['level'] == 'INFO'
        assert 'ts' in parsed
        assert 'logger' in parsed
        assert 'module' in parsed

    def test_json_format_includes_exception(self, tmp_path, monkeypatch):
        """JSON 模式下,exc_info 应序列化为 'exc' 字段。"""
        import json

        from flask import Flask

        from classStore.common.logging_setup import setup_logging

        monkeypatch.setenv('LOG_DIR', str(tmp_path / 'json_logs2'))
        monkeypatch.setenv('LOG_FORMAT', 'json')
        test_app = Flask('test_json_exc')
        setup_logging(test_app)

        try:
            raise RuntimeError('json_exc_marker')
        except RuntimeError:
            test_app.logger.exception('json exc happened')
        for h in test_app.logger.handlers:
            h.flush()

        log_file = tmp_path / 'json_logs2' / 'app.log'
        lines = [line for line in log_file.read_text(encoding='utf-8').splitlines() if 'json exc happened' in line]
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert 'exc' in parsed
        assert 'json_exc_marker' in parsed['exc']


class TestSetupConfigurability:
    """X-T: setup_logging 参数可定制"""

    def test_log_dir_auto_created(self, tmp_path):
        """传入不存在的 log_dir 应自动创建。"""
        new_dir = tmp_path / 'autocreated_logs'
        assert not new_dir.exists()

        from flask import Flask

        from classStore.common.logging_setup import setup_logging
        test_app = Flask('test_autocreate')
        setup_logging(test_app, log_dir=str(new_dir))
        assert new_dir.exists()
        assert (new_dir / 'app.log').exists()

    def test_backup_days_configurable(self, tmp_path):
        """backup_days 参数应影响 TimedRotatingFileHandler.backupCount。"""
        import logging

        from flask import Flask

        from classStore.common.logging_setup import setup_logging
        test_app = Flask('test_backup')
        setup_logging(test_app, log_dir=str(tmp_path / 'bd_logs'), backup_days=7)

        file_handlers = [h for h in test_app.logger.handlers if isinstance(h, logging.FileHandler)]
        assert file_handlers[0].backupCount == 7

    def test_calling_setup_twice_does_not_duplicate(self, tmp_path):
        """连续两次 setup_logging 不会让 handler 数量翻倍(防 reload 累积)。"""
        from flask import Flask

        from classStore.common.logging_setup import setup_logging
        test_app = Flask('test_double')
        setup_logging(test_app, log_dir=str(tmp_path / 'd_logs'))
        first_count = len(test_app.logger.handlers)
        setup_logging(test_app, log_dir=str(tmp_path / 'd_logs'))
        second_count = len(test_app.logger.handlers)
        assert first_count == second_count, (
            f'setup_logging should be idempotent; got {first_count} → {second_count}'
        )
