import os
from datetime import datetime
from flask import request
from classStore.common.db import query_all, query_one
from classStore.common.response import ok, fail
from blueprintStore.pages import pages_blue


@pages_blue.route('/getTree', methods=['POST'])
def get_tree():
    rows = query_all('SELECT * FROM listtable')
    init_tree = []
    for item in rows:
        is_leaf = item['describeInfor'] != '1'
        parent_id = item['id'] if len(dict(item)) > 3 else 0
        if parent_id == 0:
            init_tree.append({
                'key': item['id'],
                'title': item['name'],
                'isLeaf': is_leaf,
                'children': []
            })
        else:
            for parent in init_tree:
                if parent_id == parent['key']:
                    parent['children'].append({
                        'key': item['id'],
                        'title': item['name'],
                        'isLeaf': is_leaf
                    })
                    break
    return ok(init_tree)


@pages_blue.route('/getListInfor', methods=['GET'])
def list_infor():
    item_id = request.args.get('id')
    if not item_id:
        return fail('id is required', http_status=400)

    row = query_one('SELECT describeInfor FROM listtable WHERE id = ?', (item_id,))
    if row:
        return ok({'describe': row['describeInfor']})
    return fail('Not found', http_status=404)


@pages_blue.route('/uploadImg', methods=['POST'])
def upload_img():
    data = request.get_json(silent=True) or {}
    image_data = data.get('image')
    filename = data.get('filename', f'img_{datetime.now().timestamp()}.jpg')

    if not image_data:
        return fail('No image data provided', http_status=400)

    upload_dir = os.path.join(os.path.dirname(__file__), '../../uploads')
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)
    try:
        with open(filepath, 'wb') as f:
            f.write(image_data.encode('utf-8'))
        return ok({'success': True, 'path': f'/uploads/{filename}'})
    except Exception as e:
        return fail(str(e), http_status=500)
