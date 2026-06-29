"""数据统计 - API328~330"""
from io import BytesIO
from flask import Blueprint, request, send_file
from ...common.response import success
from ...common.auth import admin_required
from ...common.log_helper import log
from ...services.statistics_service import get_overview
from ...models.delivery_record import DeliveryRecord
from ...models.user import User
from ...models.device import Device
from ...extensions import db
from sqlalchemy import func
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

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
    wb = Workbook()

    # ── Sheet 1: 投放记录 ──
    ws1 = wb.active
    ws1.title = "投放记录"
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid")
    headers = ["记录ID", "设备ID", "用户ID", "垃圾品类", "大类", "是否正确", "积分变动", "投放时间"]
    for col, h in enumerate(headers, 1):
        cell = ws1.cell(row=1, column=col, value=h)
        cell.font = header_font; cell.fill = header_fill; cell.alignment = Alignment(horizontal="center")

    q = DeliveryRecord.query.order_by(DeliveryRecord.deliveryTime.desc()).limit(1000)
    start = request.args.get("startTime", "")
    if start:
        try: q = q.filter(DeliveryRecord.deliveryTime >= datetime.fromisoformat(start))
        except ValueError: pass
    end = request.args.get("endTime", "")
    if end:
        try: q = q.filter(DeliveryRecord.deliveryTime <= datetime.fromisoformat(end))
        except ValueError: pass

    for row, r in enumerate(q.all(), 2):
        ws1.cell(row=row, column=1, value=r.recordId)
        ws1.cell(row=row, column=2, value=r.deviceId)
        ws1.cell(row=row, column=3, value=r.userId)
        ws1.cell(row=row, column=4, value=r.garbageCategory)
        ws1.cell(row=row, column=5, value=r.parentType)
        ws1.cell(row=row, column=6, value="是" if r.isCorrect else "否")
        ws1.cell(row=row, column=7, value=r.pointChange)
        ws1.cell(row=row, column=8, value=r.deliveryTime.isoformat() if r.deliveryTime else "")

    # ── Sheet 2: 用户列表 ──
    ws2 = wb.create_sheet("用户列表")
    headers2 = ["用户ID", "昵称", "手机号", "状态", "注册时间"]
    for col, h in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col, value=h)
        cell.font = header_font; cell.fill = header_fill; cell.alignment = Alignment(horizontal="center")

    users = User.query.filter_by(userType="resident").order_by(User.id.desc()).limit(1000).all()
    for row, u in enumerate(users, 2):
        ws2.cell(row=row, column=1, value=u.id)
        ws2.cell(row=row, column=2, value=u.nickName)
        ws2.cell(row=row, column=3, value=u.phone)
        ws2.cell(row=row, column=4, value=u.status)
        ws2.cell(row=row, column=5, value=u.createTime.isoformat() if u.createTime else "")

    # ── Sheet 3: 设备列表 ──
    ws3 = wb.create_sheet("设备列表")
    headers3 = ["设备ID", "设备名称", "类型", "区域", "在线状态", "满溢度", "最后在线"]
    for col, h in enumerate(headers3, 1):
        cell = ws3.cell(row=1, column=col, value=h)
        cell.font = header_font; cell.fill = header_fill; cell.alignment = Alignment(horizontal="center")

    devices = Device.query.order_by(Device.lastOnlineTime.desc()).limit(1000).all()
    for row, d in enumerate(devices, 2):
        ws3.cell(row=row, column=1, value=d.deviceId)
        ws3.cell(row=row, column=2, value=d.deviceName)
        ws3.cell(row=row, column=3, value=d.boxCategory)
        ws3.cell(row=row, column=4, value=d.area)
        ws3.cell(row=row, column=5, value=d.onlineStatus)
        ws3.cell(row=row, column=6, value=f"{d.fullRate:.0%}" if d.fullRate else "0%")
        ws3.cell(row=row, column=7, value=d.lastOnlineTime.isoformat() if d.lastOnlineTime else "")

    # 输出
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    log('statistics_export', None, '导出统计报表')
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name="数据统计报表.xlsx")
