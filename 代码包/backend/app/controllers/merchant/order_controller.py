"""商家订单管理 + 核销 — API409~410"""
from flask import Blueprint, request, g
from ...common.response import success, fail, paginated
from ...common.auth import login_required
from ...common.validators import get_pagination
from ...models.merchant import Merchant
from ...services.order_service import get_merchant_orders, verify_order

bp = Blueprint('merchant_order', __name__)


@bp.route('/orders', methods=['GET'])
@login_required
def list_orders():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')
    p = get_pagination()
    records, total = get_merchant_orders(
        merchant.id, page=p['page'], size=p['size'],
        order_status=request.args.get('orderStatus', '')
    )
    return paginated(records, total, p['page'], p['size'])


@bp.route('/orders/verify', methods=['POST'])
@login_required
def verify():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')
    body = request.get_json(silent=True) or {}
    verify_code = body.get('verifyCode', '').strip().upper()
    if not verify_code:
        return fail(400, '请输入核销码')
    result = verify_order(merchant.id, verify_code)
    if result['ok']:
        return success({
            'orderId': result['orderId'], 'commodityName': result['commodityName'],
            'verifyTime': result['verifyTime']
        }, '核销成功')
    return fail(result['error_code'], {
        6101: '核销码无效', 6102: '该订单不属于本店', 6103: '该订单已核销',
        6104: '该订单已过期', 6105: '该订单已取消'
    }.get(result['error_code'], '核销失败'))
