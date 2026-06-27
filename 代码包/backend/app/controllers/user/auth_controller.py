"""用户认证接口 — API101~104"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.validators import require_fields, is_valid_phone
from ...common.auth import login_required
from ...services.auth_service import wx_login, bind_phone, refresh_access_token, logout

bp = Blueprint('user_auth', __name__)

@bp.route('/wx-login', methods=['POST'])
def wx_login_api():
    body = request.get_json(silent=True) or {}
    wx_code = body.get('wxCode', '')
    if not wx_code:
        return fail(400, '缺少微信授权码')
    result = wx_login(wx_code)
    if result['ok']:
        if result['needBindPhone']:
            return success({'needBindPhone': True, 'bindToken': result['bindToken']}, '需要绑定手机号')
        return success({
            'userId': result['userId'], 'token': result['token'],
            'refreshToken': result['refreshToken'], 'nickName': result['nickName'],
            'avatarUrl': result['avatarUrl'], 'phone': result['phone'],
            'pointBalance': result['pointBalance'],
        })
    return fail(400, '登录失败')

@bp.route('/bind-phone', methods=['POST'])
def bind_phone_api():
    body = request.get_json(silent=True) or {}
    missing = require_fields('bindToken', 'phone', 'smsCode')
    if missing:
        return fail(400, f'缺少参数: {missing}')
    if not is_valid_phone(body['phone']):
        return fail(400, '手机号格式不正确')
    result = bind_phone(body['bindToken'], body['phone'], body['smsCode'])
    if result['ok']:
        return success({
            'userId': result['userId'], 'token': result['token'],
            'refreshToken': result['refreshToken'], 'nickName': result['nickName'],
            'avatarUrl': result['avatarUrl'], 'phone': result['phone'],
            'pointBalance': result['pointBalance'],
        }, '注册成功')
    return fail(result['error_code'], result.get('message', '注册失败'))

@bp.route('/refresh-token', methods=['POST'])
def refresh_token_api():
    refresh = request.headers.get('X-Refresh-Token', '')
    if not refresh:
        return fail(400, '缺少 Refresh-Token')
    result = refresh_access_token(refresh)
    if result['ok']:
        return success({'token': result['token'], 'refreshToken': result['refreshToken']})
    return fail(result['error_code'], 'Token 刷新失败')

@bp.route('/logout', methods=['POST'])
@login_required
def logout_api():
    logout(request.headers.get('X-Token', ''))
    return success(None, '登出成功')
