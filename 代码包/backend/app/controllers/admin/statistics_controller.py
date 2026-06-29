"""数据统计 - API328~330"""
from flask import Blueprint, request
from ...common.response import success
from ...common.auth import admin_required
from ...services.statistics_service import get_overview
from ...models.delivery_record import DeliveryRecord
from ...extensions import db
from sqlalchemy import func
from datetime import datetime

bp = Blueprint("admin_statistics", __name__)

@bp.route("/statistics/overview", methods=["GET"])
@admin_required
def overview():
    return success(get_overview())

@bp.route("/statistics/delivery", methods=["GET"])
@admin_required
def delivery_stats():
    q = DeliveryRecord.query
    start = request.args.get("startTime", "")
    if start:
        try: q = q.filter(DeliveryRecord.deliveryTime >= datetime.fromisoformat(start))
        except ValueError: pass
    end = request.args.get("endTime", "")
    if end:
        try: q = q.filter(DeliveryRecord.deliveryTime <= datetime.fromisoformat(end))
        except ValueError: pass
    area = request.args.get("area", "")
    if area: q = q.filter(DeliveryRecord.deviceId.contains(area[:3]))
    total = q.count()
    correct = q.filter(DeliveryRecord.isCorrect == True).count()
    points = db.session.query(func.sum(DeliveryRecord.pointChange)).scalar() or 0
    return success({
        "totalDeliveryCount": total, "correctCount": correct,
        "incorrectCount": total - correct,
        "correctRate": round(correct / total, 2) if total > 0 else 0,
        "totalPointsAwarded": int(points) if points > 0 else 0
    })

@bp.route("/statistics/export", methods=["GET"])
@admin_required
def export_data():
    return success({"exportUrl": "/download/export.xlsx"}, "导出任务已提交")
