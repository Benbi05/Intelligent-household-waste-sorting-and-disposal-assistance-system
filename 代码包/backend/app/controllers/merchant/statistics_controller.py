"""商家仪表盘统计 — API413"""
from flask import Blueprint, g, request
from ...common.response import success, fail
from ...common.auth import login_required
from ...models.merchant import Merchant
from ...models.commodity import Commodity
from ...models.point_order import PointOrder
from ...models.delivery_record import DeliveryRecord
from ...extensions import db
from sqlalchemy import func
from datetime import datetime
import json

# 垃圾品类 → 建议备货商品
SUGGEST_MAP = {
    '牛奶盒':'牛奶/乳制品','酸奶盒':'酸奶','饮料瓶':'饮料/矿泉水',
    '方便面桶':'方便面/速食','外卖餐盒':'外卖','快餐盒':'快餐',
    '啤酒罐':'啤酒','白酒瓶':'白酒','食用油桶':'食用油',
    '酱油瓶':'调味品','洗发水瓶':'洗发水','沐浴露瓶':'沐浴露',
    '洗衣液瓶':'洗衣液/清洁','洗衣粉袋':'洗衣粉',
    '纸巾包装':'纸巾/纸品','卫生纸芯':'卫生纸',
    '牙膏盒':'牙膏','零食袋':'零食','坚果壳':'坚果',
    '水果皮':'水果','蔬菜叶':'蔬菜','鸡蛋壳':'鸡蛋',
    '快递纸箱':'日用品','塑料袋':'日用品',
}

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
    """AI进货建议 — 基于本社区投放数据实时生成"""
    merchant = Merchant.query.filter_by(userId=g.user_id).first()
    if not merchant:
        return fail(404, '商家信息不存在')

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 根据商家所在社区匹配投放记录前缀
    comm_map = {
        '虎溪花园':'WD','学府悦园':'XF','康居西城':'KJ',
        '龙湖U城':'LH','金科廊桥水乡':'JK','富力城':'FL',
        '恒大未来城':'HD','融创文旅城':'RC',
    }
    prefix = comm_map.get(merchant.area, '')
    if not prefix:
        prefix = merchant.area[:2] if len(merchant.area) >= 2 else merchant.area

    # 统计该社区本月 top 投放品类
    q = db.session.query(
        DeliveryRecord.garbageCategory, func.count(DeliveryRecord.recordId).label('cnt')
    ).filter(
        DeliveryRecord.deviceId.like(f'{prefix}%'),
        DeliveryRecord.deliveryTime >= month_start
    ).group_by(DeliveryRecord.garbageCategory).order_by(
        func.count(DeliveryRecord.recordId).desc()
    ).limit(15).all()

    total = sum(c[1] for c in q)
    products = []
    for cat_name, cnt in q:
        suggest = SUGGEST_MAP.get(cat_name)
        if suggest:
            products.append({
                'category': cat_name, 'count': cnt,
                'product': suggest,
                'ratio': round(cnt / total * 100, 1) if total > 0 else 0
            })

    return success({
        'community': merchant.area or '本社区',
        'month': now.strftime('%Y-%m'),
        'content': f'AI分析：{merchant.area}本月投放数据显示以下消费趋势，建议调整进货策略',
        'products': products[:5],
        'totalDeliveries': total,
    })


@bp.route('/recommendations/<int:rec_id>/read', methods=['PUT'])
@login_required
def mark_read(rec_id):
    """标记推荐已读"""
    rec = Recommendation.query.get(rec_id)
    if rec:
        rec.status = 'read'
        db.session.commit()
    return success(None)
