"""商家管理 - API331~332"""
from flask import Blueprint, request, g
from ...common.response import success, fail, paginated
from ...common.auth import admin_required
from ...common.validators import get_pagination
from ...models.merchant import Merchant
from ...models.user import User
from ...models.operation_log import OperationLog
from ...extensions import db
from datetime import datetime

bp = Blueprint("admin_merchant", __name__)

@bp.route("/merchants", methods=["GET"])
@admin_required
def list_merchants():
    p = get_pagination()
    q = db.session.query(Merchant, User).join(User, Merchant.userId == User.id)
    status = request.args.get("status", "")
    if status: q = q.filter(Merchant.status == status)
    keyword = request.args.get("keyword", "")
    if keyword: q = q.filter(Merchant.storeName.contains(keyword))
    q = q.order_by(Merchant.id.desc())
    pagination = q.paginate(page=p["page"], per_page=p["size"], error_out=False)
    records = []
    for m, u in pagination.items:
        records.append({
            "merchantId": m.id, "storeName": m.storeName,
            "contactName": m.contactName, "contactPhone": m.contactPhone,
            "area": m.area, "status": m.status,
            "applyTime": u.createTime.isoformat() if u.createTime else "",
            "auditTime": m.auditTime.isoformat() if m.auditTime else None,
        })
    return paginated(records, pagination.total, p["page"], p["size"])

@bp.route("/merchants/<int:merchant_id>/audit", methods=["PUT"])
@admin_required
def audit_merchant(merchant_id):
    m = Merchant.query.get(merchant_id)
    if not m: return fail(404, "商家不存在")
    body = request.get_json(silent=True) or {}
    status = body.get("status", "")
    if status not in ("approved", "rejected"): return fail(400, "审核状态无效")
    m.status = status
    if status == "rejected" and body.get("rejectReason"):
        m.description = (m.description or "") + " | rejected: " + body["rejectReason"]
    m.auditTime = datetime.utcnow()
    log = OperationLog(adminId=g.user_id, adminName="admin",
                       actionType="merchant_audit", targetId=merchant_id,
                       detail=f"商家 {m.storeName} 审核{'通过' if status=='approved' else '驳回'}",
                       ip=request.remote_addr or "")
    db.session.add(log)
    db.session.commit()
    return success(None, "审核完成")
