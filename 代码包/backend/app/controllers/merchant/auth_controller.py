"""商家认证接口 — API402~404"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.auth import login_required
from ...services.auth_service import merchant_login, refresh_access_token, logout

bp = Blueprint('merchant_auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    body = request.get_json(silent=True) or {}
    username = body.get('username', '')
    password = body.get('password', '')
    if not username or not password:
        return fail(400, '请输入用户名和密码')
    result = merchant_login(username, password)
    if result['ok']:
        return success({
            'merchantId': result['merchantId'], 'storeName': result['storeName'],
            'area': result['area'], 'token': result['token'],
            'refreshToken': result['refreshToken'],
        })
    return fail(result['error_code'], result.get('message', '登录失败'))

@bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    refresh = request.headers.get('X-Refresh-Token', '')
    if not refresh: return fail(400, '缺少 Refresh-Token')
    result = refresh_access_token(refresh)
    if result['ok']:
        return success({'token': result['token'], 'refreshToken': result['refreshToken']})
    return fail(result['error_code'], 'Token 刷新失败')

@bp.route('/logout', methods=['POST'])
@login_required
def logout_api():
    logout(request.headers.get('X-Token', ''))
    return success(None, '登出成功')
