"""商家经营报表 — API411~412"""
from flask import Blueprint, g
from ...common.response import success, fail
from ...common.auth import login_required
from ...models.merchant import Merchant
from ...models.point_order import PointOrder
from ...extensions import db
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('merchant_report', __name__)


@bp.route('/reports', methods=['GET'])
@login_required
def list_reports():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')

    monthly = db.session.query(
        func.date_format(PointOrder.createTime, '%Y-%m').label('month'),
        func.count(PointOrder.orderId).label('total'),
        func.sum(func.if_(PointOrder.orderStatus == 'verified', 1, 0)).label('verified'),
        func.sum(func.if_(PointOrder.orderStatus == 'verified', PointOrder.pointCost, 0)).label('points')
    ).filter(
        PointOrder.merchantId == merchant.id
    ).group_by('month').order_by('month').all()

    records = [{
        'month': m[0], 'totalOrders': m[1], 'verifiedOrders': int(m[2] or 0),
        'totalPoints': int(m[3] or 0)
    } for m in monthly]

    return success(records)
