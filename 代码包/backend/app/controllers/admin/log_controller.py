"""操作日志 - API312"""
from flask import Blueprint, request
from ...common.response import success, paginated
from ...common.auth import admin_required
from ...common.validators import get_pagination
from ...models.operation_log import OperationLog
from datetime import datetime

bp = Blueprint("admin_log", __name__)

@bp.route("/logs", methods=["GET"])
@admin_required
def list_logs():
    p = get_pagination()
    q = OperationLog.query
    keyword = request.args.get("keyword", "")
    if keyword:
        q = q.filter((OperationLog.adminName.contains(keyword)) |
                     (OperationLog.actionType.contains(keyword)))
    action_type = request.args.get("actionType", "")
    if action_type: q = q.filter(OperationLog.actionType == action_type)
    start = request.args.get("startTime", "")
    if start:
        try: q = q.filter(OperationLog.createTime >= datetime.fromisoformat(start))
        except ValueError: pass
    end = request.args.get("endTime", "")
    if end:
        try: q = q.filter(OperationLog.createTime <= datetime.fromisoformat(end))
        except ValueError: pass
    q = q.order_by(OperationLog.createTime.desc())
    pagination = q.paginate(page=p["page"], per_page=p["size"], error_out=False)
    records = [{"logId": l.id, "adminId": l.adminId, "adminName": l.adminName,
                "actionType": l.actionType, "targetId": l.targetId,
                "detail": l.detail, "ip": l.ip,
                "createTime": l.createTime.isoformat() if l.createTime else ""}
               for l in pagination.items]
    return paginated(records, pagination.total, p["page"], p["size"])
