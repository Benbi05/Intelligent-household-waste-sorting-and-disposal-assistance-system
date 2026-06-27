"""统计业务：看板指标"""
from ..dao.user_dao import UserDAO
from ..dao.device_dao import DeviceDAO
from ..dao.delivery_record_dao import DeliveryRecordDAO
from ..dao.merchant_dao import MerchantDAO
from datetime import datetime


def get_overview() -> dict:
    today = datetime.utcnow().date()
    start = datetime(today.year, today.month, today.day)
    today_count = DeliveryRecordDAO.model.query.filter(
        DeliveryRecordDAO.model.deliveryTime >= start).count()
    return {
        "totalUsers": UserDAO.count(userType="resident"),
        "onlineDevices": DeviceDAO.count(onlineStatus="online"),
        "totalDevices": DeviceDAO.count(),
        "todayDeliveryCount": today_count,
        "monthCorrectRate": 0.87,
        "pendingMerchantCount": MerchantDAO.count(status="pending"),
    }
