"""角色权限管理 - API311"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.auth import admin_required
from ...common.log_helper import log
from ...models.role import Role
from ...extensions import db

bp = Blueprint("admin_role", __name__)

@bp.route("/roles", methods=["GET"])
@admin_required
def list_roles():
    roles = Role.query.order_by(Role.id).all()
    return success([{"roleId": r.id, "roleName": r.roleName,
                     "permissions": r.permissions, "description": r.description} for r in roles])

@bp.route("/roles", methods=["POST"])
@admin_required
def create_role():
    body = request.get_json(silent=True) or {}
    name = body.get("roleName", "").strip()
    if not name: return fail(400, "角色名称不能为空")
    if Role.query.filter_by(roleName=name).first(): return fail(400, "角色名称已存在")
    r = Role(roleName=name, permissions=body.get("permissions",""), description=body.get("description",""))
    db.session.add(r); db.session.commit()
    log('role_create', r.id, f'创建角色: {name}')
    return success({"roleId": r.id}, "创建成功")

@bp.route("/roles/<int:role_id>", methods=["PUT"])
@admin_required
def update_role(role_id):
    r = Role.query.get(role_id)
    if not r: return fail(404, "角色不存在")
    body = request.get_json(silent=True) or {}
    if "roleName" in body: r.roleName = body["roleName"]
    if "permissions" in body: r.permissions = body["permissions"]
    if "description" in body: r.description = body["description"]
    db.session.commit()
    log('role_update', role_id, f'修改角色: {r.roleName}')
    return success(None, "更新成功")

@bp.route("/roles/<int:role_id>", methods=["DELETE"])
@admin_required
def delete_role(role_id):
    r = Role.query.get(role_id)
    if not r: return fail(404, "角色不存在")
    db.session.delete(r); db.session.commit()
    log('role_delete', role_id, f'删除角色: {r.roleName}')
    return success(None, "删除成功")
