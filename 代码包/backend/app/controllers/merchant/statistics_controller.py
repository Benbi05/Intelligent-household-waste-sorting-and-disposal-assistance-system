"""商家仪表盘统计 — API413"""
from flask import Blueprint, g, request
from ...common.response import success, fail
from ...common.auth import login_required
from ...models.merchant import Merchant
from ...models.commodity import Commodity
from ...models.point_order import PointOrder
from ...models.recommendation import Recommendation
from ...extensions import db
from sqlalchemy import func
from datetime import datetime
import json

bp = Blueprint('merchant_statistics', __name__)


@bp.route('/statistics', methods=['GET'])
@login_required
def statistics():
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_commodities = Commodity.query.filter_by(merchantId=merchant.id).count()
    on_commodities = Commodity.query.filter_by(merchantId=merchant.id, status='on').count()

    month_orders = PointOrder.query.filter(
        PointOrder.merchantId == merchant.id,
        PointOrder.createTime >= month_start
    ).count()

    month_verified = PointOrder.query.filter(
        PointOrder.merchantId == merchant.id,
        PointOrder.orderStatus == 'verified',
        PointOrder.createTime >= month_start
    ).count()

    month_points = db.session.query(func.sum(PointOrder.pointCost)).filter(
        PointOrder.merchantId == merchant.id,
        PointOrder.orderStatus == 'verified',
        PointOrder.createTime >= month_start
    ).scalar() or 0

    # 最近5条订单
    recent = PointOrder.query.filter_by(merchantId=merchant.id)\
        .order_by(PointOrder.createTime.desc()).limit(5).all()
    recent_orders = [{
        'orderId': o.orderId, 'pointCost': o.pointCost,
        'orderStatus': o.orderStatus, 'createTime': o.createTime.isoformat()
    } for o in recent]

    return success({
        'totalCommodities': total_commodities,
        'onCommodities': on_commodities,
        'monthOrders': month_orders,
        'monthVerified': month_verified,
        'monthTotalPoints': int(month_points),
        'recentOrders': recent_orders
    })


@bp.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    """获取AI推荐"""
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')

    recs = Recommendation.query.filter_by(merchantId=merchant.id)\
        .order_by(Recommendation.createTime.desc()).limit(10).all()

    records = []
    for r in recs:
        products = []
        try:
            products = json.loads(r.products) if r.products else []
        except:
            pass
        records.append({
            'id': r.id, 'community': r.community,
            'content': r.content, 'products': products,
            'status': r.status,
            'createTime': r.createTime.isoformat() if r.createTime else '',
        })

    return success(records)


@bp.route('/recommendations/<int:rec_id>/read', methods=['PUT'])
@login_required
def mark_read(rec_id):
    """标记推荐已读"""
    rec = Recommendation.query.get(rec_id)
    if rec:
        rec.status = 'read'
        db.session.commit()
    return success(None)
