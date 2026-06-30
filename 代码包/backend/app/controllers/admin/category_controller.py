"""垃圾分类品类管理 — CRUD"""
from flask import Blueprint, request
from ...common.response import success, fail, paginated
from ...common.auth import admin_required
from ...common.validators import get_pagination
from ...common.log_helper import log
from ...models.garbage_category import GarbageCategory
from ...extensions import db
from sqlalchemy import func

bp = Blueprint("admin_category", __name__)

@bp.route("/categories", methods=["GET"])
@admin_required
def list_categories():
    p = get_pagination()
    q = GarbageCategory.query
    keyword = request.args.get("keyword", "")
    if keyword:
        q = q.filter(GarbageCategory.categoryName.contains(keyword))
    parent_type = request.args.get("parentType", "")
    if parent_type:
        q = q.filter(GarbageCategory.parentType == parent_type)
    q = q.order_by(GarbageCategory.categoryId)
    pagination = q.paginate(page=p["page"], per_page=p["size"], error_out=False)
    records = [{"categoryId": c.categoryId, "categoryName": c.categoryName,
                "parentType": c.parentType, "parentTypeName": c.parentTypeName,
                "rewardPoint": c.rewardPoint, "penaltyPoint": c.penaltyPoint,
                "guide": c.guide, "status": c.status}
               for c in pagination.items]
    return paginated(records, pagination.total, p["page"], p["size"])

@bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    body = request.get_json(silent=True) or {}
    name = body.get("categoryName", "").strip()
    if not name: return fail(400, "品类名称不能为空")
    if GarbageCategory.query.filter_by(categoryName=name).first():
        return fail(400, "品类名称已存在")
    cid = body.get("categoryId") or (GarbageCategory.query.order_by(GarbageCategory.categoryId.desc()).first().categoryId + 1)
    c = GarbageCategory(
        categoryId=cid , categoryName=name,
        parentType=body.get("parentType", "other"),
        parentTypeName=body.get("parentTypeName", "其他垃圾"),
        rewardPoint=body.get("rewardPoint", 5),
        penaltyPoint=body.get("penaltyPoint", 3),
        guide=body.get("guide", ""),
        status=body.get("status", "enable")
    )
    db.session.add(c); db.session.commit()
    log("category_create", c.categoryId, f"新增品类: {name}")
    return success({"categoryId": c.categoryId}, "新增成功")

@bp.route("/categories/<int:category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    c = GarbageCategory.query.get(category_id)
    if not c: return fail(404, "品类不存在")
    body = request.get_json(silent=True) or {}
    for key in ("categoryName", "parentType", "parentTypeName", "rewardPoint", "penaltyPoint", "guide", "status"):
        if key in body and body[key] is not None:
            setattr(c, key, body[key])
    db.session.commit()
    log("category_update", category_id, f"修改品类: {c.categoryName}")
    return success(None, "更新成功")

@bp.route("/categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    c = GarbageCategory.query.get(category_id)
    if not c: return fail(404, "品类不存在")
    db.session.delete(c); db.session.commit()
    log("category_delete", category_id, f"删除品类: {c.categoryName}")
    return success(None, "删除成功")

@bp.route("/categories/stats", methods=["GET"])
@admin_required
def category_stats():
    """品类统计概览"""
    total = GarbageCategory.query.count()
    by_type = {}
    for pt in ("recyclable", "kitchen", "hazardous", "other"):
        by_type[pt] = GarbageCategory.query.filter_by(parentType=pt).count()
    return success({"totalCategories": total, "byType": by_type})
