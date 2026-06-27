"""设备鉴权接口 — API201"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...services.device_service import auth_device

bp = Blueprint('device_auth', __name__)

@bp.route('/auth', methods=['POST'])
def auth():
    body = request.get_json(silent=True) or {}
    device_id = body.get('deviceId', '')
    device_secret = body.get('deviceSecret', '')
    if not device_id or not device_secret:
        return fail(400, '缺少设备凭证')
    result = auth_device(device_id, device_secret)
    if result['ok']:
        return success({
            'deviceToken': result['deviceToken'],
            'boxCategory': result['boxCategory'],
            'heartbeatInterval': result['heartbeatInterval'],
        })
    return fail(result['error_code'], '设备鉴权失败')
