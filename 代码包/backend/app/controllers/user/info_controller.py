"""用户信息接口 — API107~108"""
from flask import Blueprint, request, g
from ...common.response import success, fail
from ...common.auth import login_required
from ...services.user_service import get_user_info, update_user_info

bp = Blueprint('user_info', __name__)

@bp.route('/info', methods=['GET'])
@login_required
def get_info():
    data = get_user_info(g.user_id)
    if data is None:
        return fail(404, '用户不存在')
    return success(data)

@bp.route('/info', methods=['PUT'])
@login_required
def update_info():
    body = request.get_json(silent=True) or {}
    ok = update_user_info(g.user_id, nickName=body.get('nickName'), avatarUrl=body.get('avatarUrl'))
    if ok:
        return success(None, '更新成功')
    return fail(400, '无可修改的内容')
