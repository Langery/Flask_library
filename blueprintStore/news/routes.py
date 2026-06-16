from flask import g, request
from classStore.common.db import query_all, query_one
from classStore.common.auth import require_auth
from classStore.common.response import ok, fail
from blueprintStore.news import news_blue


_DEFAULT_LIMIT = 10
_MAX_LIMIT = 50


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

    where = ''
    params = []
    if keyword:
        where = 'WHERE title LIKE ?'
        params.append(f'%{keyword}%')

    total_row = query_one(f'SELECT COUNT(*) AS c FROM news {where}', tuple(params))
    total = total_row['c'] if total_row else 0

    rows = query_all(
        f'SELECT id, user_id, title, body FROM news {where} ORDER BY id DESC LIMIT ? OFFSET ?',
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
