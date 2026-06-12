from flask import jsonify

SUCCESS_CODE = 0
FAIL_CODE = 1


def ok(data=None, message='success', http_status=200):
    """统一成功返回:{code:0, message, data}"""
    return jsonify({'code': SUCCESS_CODE, 'message': message, 'data': data}), http_status


def fail(message='fail', code=FAIL_CODE, http_status=400, data=None):
    """统一失败返回:{code:1, message, data}"""
    return jsonify({'code': code, 'message': message, 'data': data}), http_status
