"""统一响应格式"""
from flask import jsonify
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))


def success(data=None, message='操作成功'):
    return jsonify({
        'code': 200,
        'message': message,
        'data': data,
        'timestamp': datetime.now(TZ).isoformat(),
    })


def fail(code, message, data=None):
    http_status = 500 if code == 500 else 400
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now(TZ).isoformat(),
    }), http_status


def paginated(records, total, page, size):
    return success({
        'records': records,
        'total': total,
        'page': page,
        'size': size,
    })