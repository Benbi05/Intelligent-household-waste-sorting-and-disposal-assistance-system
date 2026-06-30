"""统计业务：看板指标"""
from ..extensions import db
from ..models.user import User
from ..models.device import Device
from ..models.delivery_record import DeliveryRecord
from ..models.merchant import Merchant
from datetime import datetime, timedelta


def get_overview(community='') -> dict:
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _filter(query, model):
        if community:
            return query.filter(model.deviceId.like(f'{community}%'))
        return query

    # 本月投放
    month_total = _filter(DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= month_start), DeliveryRecord).count()
    month_correct = _filter(DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= month_start, DeliveryRecord.isCorrect == True), DeliveryRecord).count()
    correct_rate = round(month_correct / month_total, 2) if month_total > 0 else 0

    # 上月投放（环比）
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    last_month_total = _filter(DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= last_month_start, DeliveryRecord.deliveryTime < month_start), DeliveryRecord).count()
    delivery_change = round((month_total - last_month_total) / last_month_total * 100, 1) if last_month_total > 0 else 0

    # 设备
    dev_q = Device.query
    if community:
        dev_q = dev_q.filter(Device.deviceId.like(f'{community}%'))
    online = dev_q.filter_by(onlineStatus="online").count()
    total_devices = dev_q.count()
    offline_fault = dev_q.filter(Device.onlineStatus.in_(("offline", "fault"))).count()

    # 用户
    total_users = User.query.filter_by(userType="resident").count()
    new_users = User.query.filter(User.userType == "resident", User.createTime >= month_start).count()

    return {
        "totalUsers": total_users,
        "newUsersThisMonth": new_users,
        "onlineDevices": online,
        "totalDevices": total_devices,
        "offlineFaultDevices": offline_fault,
        "monthDeliveryCount": month_total,
        "deliveryChangeRate": delivery_change,
        "monthCorrectRate": correct_rate,
        "pendingMerchantCount": Merchant.query.filter_by(status="pending").count(),
    }
