"""商家商品管理 — API406~408"""
from flask import Blueprint, request, g
from ...common.response import success, fail, paginated
from ...common.auth import login_required
from ...common.validators import get_pagination
from ...models.merchant import Merchant
from ...models.commodity import Commodity
from ...extensions import db

bp = Blueprint('merchant_commodity', __name__)


def _get_merchant():
    return Merchant.query.filter_by(userId=g.user_id).first()


@bp.route('/commodities', methods=['GET'])
@login_required
def list_commodities():
    merchant = _get_merchant()
    if not merchant:
        return fail(404, '商家信息不存在')
    p = get_pagination()
    q = Commodity.query.filter_by(merchantId=merchant.id)
    keyword = request.args.get('keyword', '')
    if keyword:
        q = q.filter(Commodity.commodityName.contains(keyword))
    status = request.args.get('status', '')
    if status:
        q = q.filter_by(status=status)
    q = q.order_by(Commodity.id.desc())
    pagination = q.paginate(page=p['page'], per_page=p['size'], error_out=False)
    records = [{
        'id': c.id, 'commodityName': c.commodityName, 'pointPrice': c.pointPrice,
        'stock': c.stock, 'imageUrl': c.imageUrl or '', 'description': c.description or '',
        'useRules': c.useRules or '', 'status': c.status,
        'monthExchangeCount': c.monthExchangeCount
    } for c in pagination.items]
    return paginated(records, pagination.total, p['page'], p['size'])


@bp.route('/commodities', methods=['POST'])
@login_required
def create_commodity():
    merchant = _get_merchant()
    if not merchant:
        return fail(404, '商家信息不存在')
    body = request.get_json(silent=True) or {}
    name = body.get('commodityName', '').strip()
    if not name:
        return fail(400, '商品名称不能为空')
    point_price = body.get('pointPrice', 0)
    if point_price <= 0:
        return fail(400, '积分价格必须大于0')
    c = Commodity(
        commodityName=name, merchantId=merchant.id, pointPrice=point_price,
        stock=body.get('stock', 0), imageUrl=body.get('imageUrl', ''),
        description=body.get('description', ''), useRules=body.get('useRules', ''),
        status='on'
    )
    db.session.add(c)
    db.session.commit()
    return success({'id': c.id, 'commodityName': c.commodityName}, '商品上架成功')


@bp.route('/commodities/<int:commodity_id>', methods=['PUT'])
@login_required
def update_commodity(commodity_id):
    merchant = _get_merchant()
    if not merchant:
        return fail(404, '商家信息不存在')
    c = Commodity.query.get(commodity_id)
    if not c or c.merchantId != merchant.id:
        return fail(404, '商品不存在')
    body = request.get_json(silent=True) or {}
    for key in ('commodityName', 'pointPrice', 'stock', 'imageUrl', 'description', 'useRules', 'status'):
        if key in body and body[key] is not None:
            setattr(c, key, body[key])
    db.session.commit()
    return success(None, '商品更新成功')
