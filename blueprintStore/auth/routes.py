import logging
import re
import sqlite3
from datetime import UTC, datetime

from flask import request
from werkzeug.security import check_password_hash, generate_password_hash

from blueprintStore.auth import auth_blue
from classStore.common.auth import generate_token
from classStore.common.db import execute, query_one
from classStore.common.limiter import limiter
from classStore.common.response import fail, ok

logger = logging.getLogger(__name__)

USERNAME_RE = re.compile(r'^[A-Za-z0-9_]{3,20}$')
NICKNAME_MAX_LEN = 30
PASSWORD_MIN_LEN = 6


@auth_blue.route('/first', methods=['GET'])
def first():
    name = request.args.get('name')
    if name:
        return ok({'message': name})
    return fail('No data', http_status=400)


@auth_blue.route('/health', methods=['GET'])
def health():
    """Liveness + readiness 探活:DB 可达 → 200,否则 503。

    与 /api/first 的区别:
    - /api/first: 纯 echo,验证进程在跑(liveness)
    - /api/health: 验证 DB 连接可用(readiness),K8s/容器编排用这个
    """
    db_status = 'ok'
    try:
        query_one('SELECT 1 AS x')
    except Exception:
        logger.exception('Health check: DB probe failed')
        db_status = 'error'

    body = {
        'status': 'ok' if db_status == 'ok' else 'degraded',
        'db': db_status,
        'timestamp': datetime.now(UTC).isoformat(),
    }
    http_status = 200 if db_status == 'ok' else 503
    return ok(body, http_status=http_status)


@auth_blue.route('/login', methods=['POST'])
@limiter.limit('5 per minute')  # 防暴力破解:同 IP 每分钟最多 5 次登录尝试
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return fail('username and password are required', http_status=400)

    row = query_one(
        'SELECT id, nickname, password FROM usertable WHERE (username = ? OR nickname = ?)',
        (username, username)
    )
    if not row:
        # 用户不存在:统一返回 backData=False,不区分"用户不存在"和"密码错"
        # 防止 username enumeration 攻击
        return ok({'backData': False})

    # check_password_hash 自动识别 pbkdf2/scrypt/bcrypt 等格式
    # 对老用户(若 DB 残留 plaintext)用 == 兜底,然后自动升级为 hash
    stored = row['password']
    if stored.startswith(('pbkdf2:', 'scrypt:', 'bcrypt')):
        password_ok = check_password_hash(stored, password)
    else:
        # 兼容老 plaintext 用户:比对成功则自动升级为 hash
        password_ok = (stored == password)
        if password_ok:
            new_hash = generate_password_hash(password)
            execute('UPDATE usertable SET password = ? WHERE id = ?', (new_hash, row['id']))
            logger.info('Auto-upgraded password hash for user id=%s', row['id'])

    if password_ok:
        return ok({
            'backData': True,
            'tokenId': generate_token(row['id'], username)
        })
    return ok({'backData': False})


@auth_blue.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    nickname = data.get('nickname')
    password = data.get('password')

    if not username or not nickname or not password:
        return fail('username, nickname, password are required', http_status=400)

    # 格式校验:防 SQL 注入残留风险 + 业务规则
    if not USERNAME_RE.match(username):
        return fail('用户名必须是 3-20 位字母/数字/下划线', http_status=400)
    if not nickname.strip() or len(nickname) > NICKNAME_MAX_LEN:
        return fail(f'昵称必须是 1-{NICKNAME_MAX_LEN} 位非空字符', http_status=400)
    if len(password) < PASSWORD_MIN_LEN:
        return fail(f'密码至少 {PASSWORD_MIN_LEN} 位', http_status=400)

    existing = query_one(
        'SELECT id FROM usertable WHERE username = ? OR nickname = ?',
        (username, nickname)
    )
    if existing:
        return ok({'backData': False, 'message': '用户名或昵称已存在'})

    # pbkdf2:sha256 默认 600000 iterations,带 16 字节 salt
    # 输出格式 pbkdf2:sha256:600000$<salt>$<hash> ≈ 100+ 字符
    password_hash = generate_password_hash(password)

    try:
        execute(
            'INSERT INTO usertable (username, password, nickname) VALUES (?, ?, ?)',
            (username, password_hash, nickname)
        )
        return ok({'backData': True, 'message': '注册成功'})
    except sqlite3.IntegrityError:
        # 竞态:SELECT 检查与 INSERT 之间被另一请求抢先(UNIQUE 约束冲突)
        # 对用户而言与"已存在"等价,但日志要带 traceback 便于排查
        logger.exception('Register race condition: username=%r nickname=%r', username, nickname)
        return ok({'backData': False, 'message': '用户名或昵称已存在'})
    except Exception:
        # 兜底:任何未预期异常都只记日志,绝不回传原始消息
        # 原始 str(e) 可能含 schema/路径/SQL 信息,属信息泄露
        logger.exception('Register failed: username=%r', username)
        return ok({'backData': False, 'message': '注册失败,请稍后重试'})
