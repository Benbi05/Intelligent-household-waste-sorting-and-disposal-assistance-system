"""短信验证码接口 — API0001"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.validators import is_valid_phone
from ...common.sms import send

bp = Blueprint('sms', __name__)

@bp.route('/sms/send', methods=['POST'])
def send_sms():
    body = request.get_json(silent=True) or {}
    phone = body.get('phone', '')
    captcha_token = body.get('captchaToken', '')
    captcha_code = body.get('captchaCode', '')
    if not phone or not captcha_token or not captcha_code:
        return fail(400, '参数不完整')
    if not is_valid_phone(phone):
        return fail(400, '手机号格式不正确')
    from ...common.captcha import verify
    if not verify(captcha_token, captcha_code):
        return fail(1003, '图形验证码校验失败')
    result = send(phone)
    if result['ok']:
        return success({'expireSeconds': 300}, result['message'])
    return fail(result['error_code'], result['message'])
