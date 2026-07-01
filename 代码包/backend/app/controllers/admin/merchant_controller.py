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
    community = request.args.get("community", "")
    if community:
        # 匹配商家area字段（社区全名如"虎溪花园"）或area包含前缀
        comm_full_map = {'虎溪':'虎溪花园','学府':'学府悦园','康居':'康居西城','龙湖':'龙湖U城','金科':'金科廊桥水乡','富力':'富力城','恒大':'恒大未来城','融创':'融创文旅城'}
        full_name = comm_full_map.get(community, community)
        q = q.filter(Merchant.area.like(f'%{full_name}%') if full_name != community else Merchant.area.contains(community))
    q = q.order_by(Merchant.id.desc())
    pagination = q.paginate(page=p["page"], per_page=p["size"], error_out=False)
    records = []
    for m, u in pagination.items:
        records.append({
            "merchantId": m.id, "storeName": m.storeName,
            "contactName": m.contactName, "contactPhone": m.contactPhone,
            "area": m.area, "status": m.status,
            "storeAddress": m.storeAddress or '',
            "businessLicense": m.businessLicense or '',
            "idCard": m.idCard or '',
            "username": m.username,
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

@bp.route("/merchants/stats", methods=["GET"])
@admin_required
def merchant_stats():
    """商家统计概览"""
    pending = Merchant.query.filter_by(status="pending").count()
    approved = Merchant.query.filter_by(status="approved").count()
    rejected = Merchant.query.filter_by(status="rejected").count()
    return success({"pending": pending, "approved": approved, "rejected": rejected, "frozen": Merchant.query.filter_by(status="frozen").count()})


@bp.route("/merchants/<int:merchant_id>/freeze", methods=["PUT"])
@admin_required
def freeze_merchant(merchant_id):
    """冻结/解冻商家"""
    m = Merchant.query.get(merchant_id)
    if not m: return fail(404, "商家不存在")
    if m.status == "frozen":
        m.status = "approved"
        msg = "商家已解冻"
    else:
        m.status = "frozen"
        msg = "商家已冻结"
    db.session.commit()
    db.session.add(OperationLog(adminId=g.user_id, adminName="admin", actionType="merchant_freeze",
        targetId=merchant_id, detail=f"商家 {m.storeName} {msg}", ip=request.remote_addr or ""))
    db.session.commit()
    return success({"status": m.status}, msg)


@bp.route("/merchants/<int:merchant_id>/delete", methods=["DELETE"])
@admin_required
def delete_merchant(merchant_id):
    """注销商家账号"""
    m = Merchant.query.get(merchant_id)
    if not m: return fail(404, "商家不存在")
    # 清理关联数据
    from ...models.recommendation import Recommendation
    from ...models.commodity import Commodity
    from ...models.point_order import PointOrder
    Recommendation.query.filter_by(merchantId=merchant_id).delete()
    Commodity.query.filter_by(merchantId=merchant_id).delete()
    PointOrder.query.filter_by(merchantId=merchant_id).delete()
    uid = m.userId
    db.session.delete(m)
    User.query.filter_by(id=uid).delete()
    db.session.commit()
    db.session.add(OperationLog(adminId=g.user_id, adminName="admin", actionType="merchant_delete",
        targetId=merchant_id, detail=f"注销商家: {m.storeName}", ip=request.remote_addr or ""))
    db.session.commit()
    return success(None, "商家已注销")
