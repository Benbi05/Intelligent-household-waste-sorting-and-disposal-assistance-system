"""商家入驻申请 — API401"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...models.user import User
from ...models.merchant import Merchant
from ...extensions import db
from ...services.auth_service import hash_password

bp = Blueprint('merchant_apply', __name__)


@bp.route('/apply', methods=['POST'])
def apply():
    body = request.get_json(silent=True) or {}
    store_name = body.get('storeName', '').strip()
    contact_name = body.get('contactName', '').strip()
    contact_phone = body.get('contactPhone', '').strip()
    password = body.get('password', '').strip()
    area = body.get('area', '').strip()

    if not all([store_name, contact_name, contact_phone, password]):
        return fail(400, '请填写完整信息（店铺名称、联系人、手机号、密码）')

    if Merchant.query.filter_by(storeName=store_name).first():
        return fail(6001, '店铺名称已存在')

    if User.query.filter_by(phone=contact_phone).first():
        return fail(6002, '手机号已被注册')

    user = User(phone=contact_phone, nickName=contact_name, userType='merchant', status='enable')
    db.session.add(user)
    db.session.flush()

    merchant = Merchant(
        userId=user.id, username=store_name, passwordHash=hash_password(password),
        storeName=store_name, contactName=contact_name, contactPhone=contact_phone,
        area=area, status='pending'
    )
    db.session.add(merchant)
    db.session.commit()

    return success({'merchantId': merchant.id, 'storeName': store_name}, '申请已提交，等待管理员审核')
