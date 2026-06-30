"""社区维度聚合统计"""
from flask import Blueprint, request
from ...common.response import success
from ...common.auth import admin_required
from ...models.delivery_record import DeliveryRecord
from ...models.device import Device
from ...models.user import User
from ...models.point_record import PointRecord
from ...extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint("community_stats", __name__)

COMMUNITIES = [
    ('虎溪花园', '虎溪'), ('学府悦园', '学府'), ('康居西城', '康居'),
    ('龙湖U城', '龙湖'), ('金科廊桥水乡', '金科'), ('富力城', '富力'),
    ('恒大未来城', '恒大'), ('融创文旅城', '融创'),
]

@bp.route("/community/delivery-compare", methods=["GET"])
@admin_required
def delivery_compare():
    """各社区本月/上月投放总量对比，按本月降序"""
    now = datetime.utcnow()
    this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    result = []
    for name, prefix in COMMUNITIES:
        tm = DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= this_month, DeliveryRecord.deviceId.like(f'{prefix}%')).count()
        lm = DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= last_month, DeliveryRecord.deliveryTime < this_month, DeliveryRecord.deviceId.like(f'{prefix}%')).count()
        result.append({'community': name, 'thisMonth': tm, 'lastMonth': lm, 'change': tm - lm})
    result.sort(key=lambda x: x['thisMonth'], reverse=True)
    return success(result)

@bp.route("/community/rate-compare", methods=["GET"])
@admin_required
def rate_compare():
    """各社区分类正确率列表，支持按品类筛选"""
    cat_filter = request.args.get("categoryType", "")
    result = []
    for name, prefix in COMMUNITIES:
        q = DeliveryRecord.query.filter(DeliveryRecord.deviceId.like(f'{prefix}%'))
        if cat_filter:
            q = q.filter(DeliveryRecord.parentType == cat_filter)
        total = q.count()
        correct = q.filter(DeliveryRecord.isCorrect == True).count()
        rate = round(correct / total * 100, 1) if total > 0 else 0
        result.append({'community': name, 'total': total, 'correct': correct, 'rate': rate})
    return success(result)

@bp.route("/community/device-issues", methods=["GET"])
@admin_required
def device_issues():
    """各社区待处理设备列表"""
    devices = Device.query.filter(Device.onlineStatus.in_(("offline", "fault"))).all()
    result = []
    for d in devices:
        prefix = d.deviceId[:2] if len(d.deviceId) >= 2 else ''
        community = ''
        for name, p in COMMUNITIES:
            if d.deviceId.startswith(p):
                community = name; break
        result.append({
            'deviceId': d.deviceId,
            'deviceName': d.deviceName,
            'community': community or '未知',
            'status': d.onlineStatus,
            'location': d.location or '',
            'fullRate': d.fullRate,
            'lastOnline': d.lastOnlineTime.isoformat() if d.lastOnlineTime else '',
        })
    return success(result)

@bp.route("/community/user-stats", methods=["GET"])
@admin_required
def user_stats():
    """各社区用户统计"""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # 简单处理：用户不按社区分，返回总数和月新增
    total = User.query.filter_by(userType="resident").count()
    new_this_month = User.query.filter(User.userType == "resident", User.createTime >= month_start).count()
    result = []
    for name, prefix in COMMUNITIES:
        # 按设备前缀关联小区，通过投放记录的userId去重估算
        user_ids = db.session.query(DeliveryRecord.userId).filter(DeliveryRecord.deviceId.like(f'{prefix}%')).distinct().all()
        uid_list = [u[0] for u in user_ids]
        total_u = len(uid_list)
        new_u = User.query.filter(User.id.in_(uid_list), User.createTime >= month_start).count() if uid_list else 0
        result.append({'community': name, 'totalUsers': total_u, 'newUsers': new_u})
    return success(result)
