import json
from datetime import UTC, datetime

from flask import g, request

from blueprintStore.layout import layout_blue
from classStore.common.auth import require_auth
from classStore.common.db import execute, query_one
from classStore.common.response import fail, ok

MAX_LAYOUT_BYTES = 64 * 1024
MAX_ITEMS = 200


@layout_blue.route('/layout/get', methods=['GET'])
@require_auth
def get_layout():
    row = query_one('SELECT layout_json, updated_at FROM drag_layouts WHERE user_id = ?', (g.user_id,))
    if not row:
        return ok({'items': [], 'updatedAt': None})
    try:
        items = json.loads(row['layout_json'])
    except (json.JSONDecodeError, TypeError):
        return ok({'items': [], 'updatedAt': None})
    return ok({'items': items, 'updatedAt': row['updated_at']})


@layout_blue.route('/layout/save', methods=['PUT'])
@require_auth
def save_layout():
    data = request.get_json(silent=True) or {}
    items = data.get('items')
    if not isinstance(items, list):
        return fail('items must be a list', http_status=400)
    if len(items) >= MAX_ITEMS:
        return fail(f'too many items (max {MAX_ITEMS})', http_status=400)

    try:
        layout_json = json.dumps(items, ensure_ascii=False, separators=(',', ':'))
    except (TypeError, ValueError) as e:
        return fail(f'invalid items payload: {e}', http_status=400)

    if len(layout_json.encode('utf-8')) >= MAX_LAYOUT_BYTES:
        return fail(f'layout too large (max {MAX_LAYOUT_BYTES} bytes)', http_status=400)

    updated_at = datetime.now(UTC).isoformat()
    execute('''
        INSERT INTO drag_layouts (user_id, layout_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            layout_json = excluded.layout_json,
            updated_at = excluded.updated_at
    ''', (g.user_id, layout_json, updated_at))
    return ok({'saved': len(items), 'updatedAt': updated_at})
