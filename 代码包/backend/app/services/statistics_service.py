"""统计业务：看板指标"""
from ..extensions import db
from ..models.user import User
from ..models.device import Device
from ..models.delivery_record import DeliveryRecord
from ..models.merchant import Merchant
from datetime import datetime, timedelta


def get_overview() -> dict:
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 本月投放
    month_total = DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= month_start).count()
    month_correct = DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= month_start, DeliveryRecord.isCorrect == True).count()
    correct_rate = round(month_correct / month_total, 2) if month_total > 0 else 0

    # 上月投放（环比）
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    last_month_total = DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= last_month_start, DeliveryRecord.deliveryTime < month_start).count()
    if last_month_total > 0:
        delivery_change = round((month_total - last_month_total) / last_month_total * 100, 1)
    else:
        delivery_change = 0

    # 设备
    online = Device.query.filter_by(onlineStatus="online").count()
    total_devices = Device.query.count()
    offline_fault = Device.query.filter(Device.onlineStatus.in_(("offline", "fault"))).count()

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
