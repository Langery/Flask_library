import logging
import os
from datetime import datetime

from flask import request
from werkzeug.utils import secure_filename

from blueprintStore.pages import pages_blue
from classStore.common.auth import require_auth
from classStore.common.db import query_all, query_one
from classStore.common.response import fail, ok

logger = logging.getLogger(__name__)


@pages_blue.route('/getTree', methods=['POST'])
@require_auth
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
@require_auth
def list_infor():
    item_id = request.args.get('id')
    if not item_id:
        return fail('id is required', http_status=400)

    row = query_one('SELECT describeInfor FROM listtable WHERE id = ?', (item_id,))
    if row:
        return ok({'describe': row['describeInfor']})
    return fail('Not found', http_status=404)


@pages_blue.route('/uploadImg', methods=['POST'])
@require_auth
def upload_img():
    data = request.get_json(silent=True) or {}
    image_data = data.get('image')
    raw_filename = data.get('filename', f'img_{datetime.now().timestamp()}.jpg')

    if not image_data:
        return fail('No image data provided', http_status=400)

    # 防御 path traversal:secure_filename 移除路径分隔符和危险字符
    safe_filename = secure_filename(raw_filename) or f'img_{datetime.now().timestamp()}.jpg'

    upload_dir = os.path.join(os.path.dirname(__file__), '../../uploads')
    upload_dir = os.path.realpath(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.realpath(os.path.join(upload_dir, safe_filename))
    # 二次校验:filepath 必须仍在 upload_dir 之内
    if not filepath.startswith(upload_dir + os.sep) and filepath != upload_dir:
        return fail('Invalid filename', http_status=400)

    try:
        with open(filepath, 'wb') as f:
            f.write(image_data.encode('utf-8'))
        return ok({'success': True, 'path': f'/uploads/{safe_filename}'})
    except (OSError, PermissionError) as e:
        # 磁盘满/权限拒绝/路径不存在等:日志带 traceback + 绝对路径(运维排查用),
        # 但响应只回"文件保存失败",不暴露路径和 errno
        logger.exception('Upload write failed: filepath=%r errno=%s', filepath, e.errno)
        return fail('文件保存失败', http_status=500)
    except Exception:
        logger.exception('Upload unexpected error: filepath=%r', filepath)
        return fail('上传失败,请稍后重试', http_status=500)
