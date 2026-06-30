"""AI消费洞察 — 从投放数据推断消费趋势"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.auth import admin_required
from ...models.delivery_record import DeliveryRecord
from ...models.merchant import Merchant
from ...models.recommendation import Recommendation
from ...extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta
import json

bp = Blueprint('admin_insight', __name__)

# 垃圾品类 → 消费商品映射表
CATEGORY_PRODUCT_MAP = {
    '牛奶盒': '牛奶/乳制品', '酸奶盒': '酸奶', '饮料瓶': '饮料/矿泉水',
    '方便面桶': '方便面/速食', '外卖餐盒': '外卖', '快餐盒': '快餐',
    '啤酒罐': '啤酒', '白酒瓶': '白酒', '红酒瓶': '红酒',
    '食用油桶': '食用油', '酱油瓶': '调味品', '醋瓶': '调味品',
    '洗发水瓶': '洗发水/日化', '沐浴露瓶': '沐浴露',
    '洗衣液瓶': '洗衣液/清洁', '洗衣粉袋': '洗衣粉',
    '纸巾包装': '纸巾/纸品', '卫生纸芯': '卫生纸',
    '牙膏盒': '牙膏', '牙刷包装': '牙刷',
    '零食袋': '零食', '坚果壳': '坚果', '水果皮': '水果',
    '蔬菜叶': '蔬菜', '鸡蛋壳': '鸡蛋',
    '快递纸箱': '网购', '塑料袋': '塑料袋',
}

COMMUNITIES = [
    ('虎溪花园', 'WD'), ('学府悦园', 'XF'), ('康居西城', 'KJ'),
    ('龙湖U城', 'LH'), ('金科廊桥水乡', 'JK'), ('富力城', 'FL'),
    ('恒大未来城', 'HD'), ('融创文旅城', 'RC'),
]


@bp.route('/ops/insights', methods=['GET'])
@admin_required
def consumption_insights():
    """各社区消费洞察"""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 本月全区 top 品类
    top_categories = db.session.query(
        DeliveryRecord.garbageCategory, func.count(DeliveryRecord.recordId).label('cnt')
    ).filter(
        DeliveryRecord.deliveryTime >= month_start
    ).group_by(DeliveryRecord.garbageCategory).order_by(func.count(DeliveryRecord.recordId).desc()).limit(20).all()

    # 按社区分组统计
    community_insights = []
    for comm_name, prefix in COMMUNITIES:
        cats = db.session.query(
            DeliveryRecord.garbageCategory, func.count(DeliveryRecord.recordId).label('cnt')
        ).filter(
            DeliveryRecord.deviceId.like(f'{prefix}%'),
            DeliveryRecord.deliveryTime >= month_start
        ).group_by(DeliveryRecord.garbageCategory).order_by(
            func.count(DeliveryRecord.recordId).desc()
        ).limit(10).all()

        total = sum(c[1] for c in cats)
        top_products = []
        for cat_name, cnt in cats:
            product = CATEGORY_PRODUCT_MAP.get(cat_name)
            if product:
                top_products.append({
                    'category': cat_name, 'count': cnt,
                    'product': product, 'ratio': round(cnt / total * 100, 1)
                })

        community_insights.append({
            'community': comm_name,
            'totalDeliveries': total,
            'topProducts': top_products[:5],  # Top 5 建议
        })

    # 全区趋势
    overall = []
    for cat_name, cnt in top_categories[:10]:
        product = CATEGORY_PRODUCT_MAP.get(cat_name)
        if product:
            overall.append({'category': cat_name, 'count': cnt, 'product': product})

    return success({
        'overall': overall,
        'communities': community_insights,
        'month': now.strftime('%Y-%m'),
    })


@bp.route('/ops/insights/trend', methods=['GET'])
@admin_required
def category_trend():
    """某品类近30天趋势"""
    cat = request.args.get('category', '牛奶盒')
    now = datetime.utcnow()
    trend = []
    for day in range(29, -1, -1):
        d_start = (now - timedelta(days=day)).replace(hour=0, minute=0, second=0, microsecond=0)
        d_end = d_start + timedelta(days=1)
        cnt = DeliveryRecord.query.filter(
            DeliveryRecord.garbageCategory == cat,
            DeliveryRecord.deliveryTime >= d_start,
            DeliveryRecord.deliveryTime < d_end
        ).count()
        trend.append({'date': d_start.strftime('%m/%d'), 'count': cnt})
    return success({'category': cat, 'product': CATEGORY_PRODUCT_MAP.get(cat, cat), 'trend': trend})


@bp.route('/ops/insights/push', methods=['POST'])
@admin_required
def push_recommendation():
    """推送消费建议给指定商家"""
    body = request.get_json(silent=True) or {}
    merchant_id = body.get('merchantId')
    community = body.get('community', '')
    products = body.get('products', [])  # [{category, product, count}]
    content = body.get('content', '')

    if not merchant_id:
        return fail(400, '请选择目标商家')

    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return fail(404, '商家不存在')

    rec = Recommendation(
        merchantId=merchant_id,
        community=community,
        content=content or f'AI消费洞察：{community}本月投放数据分析',
        products=json.dumps(products, ensure_ascii=False),
        status='unread'
    )
    db.session.add(rec)
    db.session.commit()

    return success({'id': rec.id}, f'已推送给「{merchant.storeName}」')

