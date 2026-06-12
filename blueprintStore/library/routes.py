import uuid
from datetime import datetime, timezone
from flask import g, request
from classStore.common.db import query_all, query_one, execute, execute_rowcount
from classStore.common.auth import require_auth
from classStore.common.response import ok, fail
from blueprintStore.library import library_blue


_SORT_MAP = {
    'create_time_desc': 'create_time DESC',
    'create_time_asc': 'create_time ASC',
    'name_asc': 'name ASC',
}


def _serialize(row):
    return {
        'id': row['id'],
        'name': row['name'],
        'age': row['age'],
        'nickname': row['nickname'],
        'createTime': row['create_time'],
    }


@library_blue.route('/library/list', methods=['GET'])
@require_auth
def list_items():
    sort = request.args.get('sort', 'create_time_desc')
    order_by = _SORT_MAP.get(sort, 'create_time DESC')
    keyword = request.args.get('keyword', '').strip()

    sql = 'SELECT * FROM library_items WHERE user_id = ?'
    params = [g.user_id]
    if keyword:
        sql += ' AND name LIKE ?'
        params.append(f'%{keyword}%')
    sql += f' ORDER BY {order_by}'

    rows = query_all(sql, tuple(params))
    return ok({'items': [_serialize(r) for r in rows]})


@library_blue.route('/library/add', methods=['POST'])
@require_auth
def add_item():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    age = (data.get('age') or '').strip()
    nickname = (data.get('nickname') or '').strip()

    if not name:
        return fail('name is required', http_status=400)

    item_id = uuid.uuid4().hex
    create_time = datetime.now(timezone.utc).isoformat()

    execute(
        'INSERT INTO library_items (id, user_id, name, age, nickname, create_time) VALUES (?, ?, ?, ?, ?, ?)',
        (item_id, g.user_id, name, age, nickname, create_time)
    )

    return ok({'item': {
        'id': item_id,
        'name': name,
        'age': age,
        'nickname': nickname,
        'createTime': create_time,
    }})


@library_blue.route('/library/delete/<item_id>', methods=['DELETE'])
@require_auth
def delete_item(item_id):
    row = query_one('SELECT user_id FROM library_items WHERE id = ?', (item_id,))
    if not row:
        return fail('item not found', http_status=404)
    if row['user_id'] != g.user_id:
        return fail('forbidden', http_status=403)

    execute('DELETE FROM library_items WHERE id = ? AND user_id = ?', (item_id, g.user_id))
    return ok({'deleted': item_id})


@library_blue.route('/library/clear', methods=['POST'])
@require_auth
def clear_items():
    cleared = execute_rowcount('DELETE FROM library_items WHERE user_id = ?', (g.user_id,))
    return ok({'cleared': cleared})
