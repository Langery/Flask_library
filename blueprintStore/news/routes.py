import re

from flask import g, request

from blueprintStore.news import news_blue
from classStore.common.auth import require_auth
from classStore.common.db import query_all, query_one
from classStore.common.response import fail, ok

_DEFAULT_LIMIT = 10
_MAX_LIMIT = 50

# FTS5 安全字符:只允许字母/数字/CJK,其他全部 strip 掉,防 MATCH 语法注入
_FTS_SAFE_CHARS = re.compile(r'[a-zA-Z0-9一-鿿\s]+')


def _build_fts_query(raw_keyword):
    """把用户输入转成安全的 FTS5 MATCH 表达式。

    unicode61 tokenizer 已自动 lowercase + 按空白分词,所以这里只需要:
    1. 去掉非字母数字/CJK 的字符(防注入,也避开 FTS 保留字符 `* " : ^`)
    2. 每个 token 加 `*` 后缀做前缀匹配(用户输入"New"能命中"News")
    3. 多 token 用空格连接(AND 语义,所有词都得命中)

    返回 None 表示无有效 token,调用方应跳过搜索。
    """
    cleaned = _FTS_SAFE_CHARS.findall(raw_keyword)
    tokens = [tok for fragment in cleaned for tok in fragment.split() if tok]
    if not tokens:
        return None
    return ' '.join(f'{tok}*' for tok in tokens)


def _serialize(row, include_created_at=False):
    item = {
        'id': row['id'],
        'userId': row['user_id'],
        'title': row['title'],
        'body': row['body'],
    }
    if include_created_at and 'created_at' in row.keys():
        item['createdAt'] = row['created_at']
    return item


@news_blue.route('/news/list', methods=['GET'])
@require_auth
def list_news():
    try:
        page = max(1, int(request.args.get('_page', 1)))
        limit = int(request.args.get('_limit', _DEFAULT_LIMIT))
    except ValueError:
        return fail('_page and _limit must be integers', http_status=400)
    limit = min(max(1, limit), _MAX_LIMIT)
    offset = (page - 1) * limit

    keyword = request.args.get('q', '').strip()
    fts_query = _build_fts_query(keyword) if keyword else None

    if fts_query:
        where = 'WHERE n.id IN (SELECT rowid FROM news_fts WHERE news_fts MATCH ?)'
        params = [fts_query]
        count_sql = f'SELECT COUNT(*) AS c FROM news n {where}'
    else:
        where = ''
        params = []
        count_sql = 'SELECT COUNT(*) AS c FROM news'

    total_row = query_one(count_sql, tuple(params))
    total = total_row['c'] if total_row else 0

    rows = query_all(
        f'SELECT n.id, n.user_id, n.title, n.body FROM news n {where} ORDER BY n.id DESC LIMIT ? OFFSET ?',
        tuple(params) + (limit, offset)
    )
    return ok({
        'items': [_serialize(r) for r in rows],
        'total': total,
        'page': page,
        'limit': limit,
    })


@news_blue.route('/news/detail/<int:news_id>', methods=['GET'])
@require_auth
def news_detail(news_id):
    row = query_one(
        'SELECT id, user_id, title, body, created_at FROM news WHERE id = ?',
        (news_id,)
    )
    if not row:
        return fail('news not found', http_status=404)
    return ok({'item': _serialize(row, include_created_at=True)})


@news_blue.route('/news/related/<int:user_id>', methods=['GET'])
@require_auth
def news_related(user_id):
    if g.user_id != user_id:
        return fail('forbidden', http_status=403)

    exclude_id = request.args.get('exclude_id')
    if exclude_id is not None:
        try:
            exclude_id = int(exclude_id)
        except ValueError:
            return fail('exclude_id must be integer', http_status=400)
        rows = query_all(
            'SELECT id, user_id, title, body FROM news WHERE user_id = ? AND id != ? ORDER BY id DESC LIMIT 5',
            (user_id, exclude_id)
        )
    else:
        rows = query_all(
            'SELECT id, user_id, title, body FROM news WHERE user_id = ? ORDER BY id DESC LIMIT 5',
            (user_id,)
        )
    return ok({'items': [_serialize(r) for r in rows]})
