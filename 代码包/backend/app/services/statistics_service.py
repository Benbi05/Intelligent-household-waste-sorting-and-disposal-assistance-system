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
    month_total = DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= month_start).count()
    month_correct = DeliveryRecord.query.filter(DeliveryRecord.deliveryTime >= month_start, DeliveryRecord.isCorrect == True).count()
    correct_rate = round(month_correct / month_total, 2) if month_total > 0 else 0

    return {
        "totalUsers": User.query.filter_by(userType="resident").count(),
        "onlineDevices": Device.query.filter_by(onlineStatus="online").count(),
        "totalDevices": Device.query.count(),
        "monthDeliveryCount": month_total,
        "monthCorrectRate": correct_rate,
        "pendingMerchantCount": Merchant.query.filter_by(status="pending").count(),
    }
