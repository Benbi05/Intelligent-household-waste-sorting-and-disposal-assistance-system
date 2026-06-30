"""运维仪表盘 + 系统监控 — ops_admin"""
from flask import Blueprint
from ...common.response import success
from ...common.auth import admin_required
from ...models.device import Device
from ...models.delivery_record import DeliveryRecord
from ...models.user import User
from ...models.recognition_model import RecognitionModel
from ...extensions import db, redis_client
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('admin_ops', __name__)


@bp.route('/ops/dashboard', methods=['GET'])
@admin_required
def ops_dashboard():
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 系统健康
    total_devices = Device.query.count()
    online_devices = Device.query.filter_by(onlineStatus='online').count()
    offline_devices = Device.query.filter_by(onlineStatus='offline').count()
    fault_devices = Device.query.filter_by(onlineStatus='fault').count()

    # 今日识别统计
    today_deliveries = DeliveryRecord.query.filter(DeliveryRecord.createTime >= today_start).count()
    today_correct = DeliveryRecord.query.filter(
        DeliveryRecord.createTime >= today_start, DeliveryRecord.isCorrect == True
    ).count()

    # 活跃模型
    active_model = RecognitionModel.query.filter_by(status='active').first()
    model_info = None
    if active_model:
        model_info = {
            'modelId': active_model.modelId, 'version': active_model.version,
            'accuracy': round(active_model.accuracy * 100, 1) if active_model.accuracy else 0,
        }

    # 总用户/商家
    total_residents = User.query.filter_by(userType='resident').count()
    total_merchants = User.query.filter_by(userType='merchant').count()

    # Redis 状态
    redis_ok = False
    try:
        redis_client.ping()
        redis_ok = True
    except:
        pass

    return success({
        'devices': {'total': total_devices, 'online': online_devices,
                    'offline': offline_devices, 'fault': fault_devices},
        'todayDeliveries': today_deliveries,
        'todayCorrectRate': round(today_correct / today_deliveries * 100, 1) if today_deliveries > 0 else 0,
        'activeModel': model_info,
        'totalResidents': total_residents,
        'totalMerchants': total_merchants,
        'redisOk': redis_ok,
        'dbOk': True,
    })
