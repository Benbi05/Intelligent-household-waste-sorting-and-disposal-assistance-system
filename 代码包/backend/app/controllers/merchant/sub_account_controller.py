"""商家子账号管理 — API414"""
from flask import Blueprint, request, g
from ...common.response import success, fail
from ...common.auth import login_required
from ...models.merchant import Merchant
from ...models.sub_account import SubAccount
from ...extensions import db
from ...services.auth_service import hash_password

bp = Blueprint('merchant_sub_account', __name__)


@bp.route('/sub-accounts', methods=['GET'])
@login_required
def list_sub_accounts():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')
    subs = SubAccount.query.filter_by(merchantId=merchant.id, status='enable').all()
    records = [{
        'id': s.id, 'username': s.username, 'displayName': s.displayName or s.username,
        'permissions': s.permissions or ''
    } for s in subs]
    return success(records)


@bp.route('/sub-accounts', methods=['POST'])
@login_required
def create_sub_account():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')
    # 限制子账号数量
    count = SubAccount.query.filter_by(merchantId=merchant.id, status='enable').count()
    if count >= 5:
        return fail(6201, '子账号数量已达上限（5个）')

    body = request.get_json(silent=True) or {}
    username = body.get('username', '').strip()
    password = body.get('password', '').strip()
    display_name = body.get('displayName', '').strip() or username

    if not username or not password:
        return fail(400, '请输入用户名和密码')
    if SubAccount.query.filter_by(merchantId=merchant.id, username=username).first():
        return fail(6202, '子账号用户名已存在')

    sub = SubAccount(
        merchantId=merchant.id, username=username,
        passwordHash=hash_password(password), displayName=display_name,
        permissions='', status='enable'
    )
    db.session.add(sub)
    db.session.commit()
    return success({'id': sub.id, 'username': sub.username}, '子账号创建成功')


@bp.route('/sub-accounts/<int:account_id>', methods=['DELETE'])
@login_required
def delete_sub_account(account_id):
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')
    sub = SubAccount.query.get(account_id)
    if not sub or sub.merchantId != merchant.id:
        return fail(404, '子账号不存在')
    sub.status = 'disabled'
    db.session.commit()
    return success(None, '子账号已删除')
