"""Token 鉴权"""
import functools
import jwt
from datetime import datetime, timedelta
from flask import request, g, current_app
from .response import fail


def generate_token(user_id, role='resident'):
    """生成 JWT access token（2小时有效）"""
    expires = current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expires,
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def generate_refresh_token(user_id, role='resident'):
    """生成 refresh token（7天有效）"""
    expires = current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
    payload = {
        'user_id': user_id,
        'role': role,
        'type': 'refresh',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expires,
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def _decode_token(token):
    """解析 Token，返回 payload 或 None"""
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """用户登录鉴权装饰器"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Token', '')
        if not token:
            return fail(401, '未登录，请先授权')
        payload = _decode_token(token)
        if payload is None:
            return fail(401, 'Token 已过期或无效')
        g.user_id = payload['user_id']
        g.role = payload['role']
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """管理员鉴权装饰器"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Token', '')
        if not token:
            return fail(401, '未登录')
        payload = _decode_token(token)
        if payload is None:
            return fail(401, 'Token 已过期')
        if payload.get('role') not in ('super_admin', 'admin'):
            return fail(403, '无管理员权限')
        g.user_id = payload['user_id']
        g.role = payload['role']
        return f(*args, **kwargs)
    return decorated


def device_required(f):
    """设备鉴权装饰器"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Token', '')
        if not token:
            return fail(401, '设备未鉴权')
        payload = _decode_token(token)
        if payload is None:
            return fail(401, '设备 Token 已过期')
        if payload.get('role') != 'device':
            return fail(403, '非设备 Token')
        g.device_id = payload['device_id']
        return f(*args, **kwargs)
    return decorated