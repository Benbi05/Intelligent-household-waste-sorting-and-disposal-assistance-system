<<<<<<< HEAD
"""ͼ����֤��ӿ� �� API0003"""
=======
"""图形验证码接口 — API0003"""
>>>>>>> afcaa8037da20aa8cdddb7e0f6b7429075c6e41f
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.captcha import generate, verify

bp = Blueprint('captcha', __name__)

<<<<<<< HEAD

@bp.route('/captcha', methods=['GET'])
def get_captcha():
    data = generate()
    return success(data)

=======
@bp.route('/captcha', methods=['GET'])
def get_captcha():
    return success(generate())
>>>>>>> afcaa8037da20aa8cdddb7e0f6b7429075c6e41f

@bp.route('/captcha/verify', methods=['POST'])
def check_captcha():
    body = request.get_json(silent=True) or {}
    token = body.get('captchaToken', '')
    code = body.get('captchaCode', '')
    if not token or not code:
<<<<<<< HEAD
        return fail(400, 'ȱ����֤�����')
    if verify(token, code):
        return success(None, '��֤ͨ��')
    return fail(1004, '��֤�������ѹ���')
=======
        return fail(400, '缺少验证码参数')
    if verify(token, code):
        return success(None, '验证通过')
    return fail(1004, '验证码错误或已过期')
>>>>>>> afcaa8037da20aa8cdddb7e0f6b7429075c6e41f
