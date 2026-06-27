"""ͼ����֤��ӿ� �� API0003"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.captcha import generate, verify

bp = Blueprint('captcha', __name__)


@bp.route('/captcha', methods=['GET'])
def get_captcha():
    data = generate()
    return success(data)


@bp.route('/captcha/verify', methods=['POST'])
def check_captcha():
    body = request.get_json(silent=True) or {}
    token = body.get('captchaToken', '')
    code = body.get('captchaCode', '')
    if not token or not code:
        return fail(400, 'ȱ����֤�����')
    if verify(token, code):
        return success(None, '��֤ͨ��')
    return fail(1004, '��֤�������ѹ���')
