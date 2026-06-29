"""积分规则管理 - API320~323"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.auth import admin_required
from ...common.log_helper import log
from ...services.point_service import get_current_rules, publish_rules

bp = Blueprint("admin_rule", __name__)

@bp.route("/point-rules/current", methods=["GET"])
@admin_required
def current_rules():
    return success(get_current_rules())

@bp.route("/point-rules/history", methods=["GET"])
@admin_required
def rule_history():
    return success({"records": [get_current_rules()], "total": 1})

@bp.route("/point-rules", methods=["POST"])
@admin_required
def publish_new_rules():
    body = request.get_json(silent=True) or {}
    rule_list = body.get("ruleList", [])
    if not rule_list: return fail(400, "规则列表不能为空")
    new_version = publish_rules(rule_list)
    log('rule_publish', None, f'发布积分规则: {new_version}, {len(rule_list)}条')
    return success({"newVersion": new_version}, "规则发布成功")

@bp.route("/point-rules/rollback", methods=["POST"])
@admin_required
def rollback_rules():
    body = request.get_json(silent=True) or {}
    target_version = body.get("targetVersion", "")
    log('rule_rollback', None, f'回退积分规则至: {target_version}')
    return success({"newVersion": target_version}, "规则已回退")
