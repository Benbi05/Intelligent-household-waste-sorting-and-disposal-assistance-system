"""商家店铺信息接口 — API405"""
from flask import Blueprint, request, g
from ...common.response import success, fail
from ...common.auth import login_required
from ...models.merchant import Merchant
from ...extensions import db

bp = Blueprint('merchant_info', __name__)

@bp.route('/info', methods=['GET'])
@login_required
def get_info():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant: return fail(404, '商家信息不存在')
    return success({
        'merchantId': merchant.id, 'storeName': merchant.storeName,
        'storeAddress': merchant.storeAddress, 'contactName': merchant.contactName,
        'contactPhone': merchant.contactPhone, 'area': merchant.area,
        'description': merchant.description, 'status': merchant.status,
    })

@bp.route('/info', methods=['PUT'])
@login_required
def update_info():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant: return fail(404, '商家信息不存在')
    body = request.get_json(silent=True) or {}
    for key in ('storeName', 'storeAddress', 'contactName', 'contactPhone', 'description'):
        if key in body and body[key] is not None:
            setattr(merchant, key, body[key])
    db.session.commit()
    return success(None, '更新成功')
