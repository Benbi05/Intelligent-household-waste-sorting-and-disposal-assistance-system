"""管理员用户管理接口 — API308~310"""
from flask import Blueprint, request
from ...common.response import success, fail, paginated
from ...common.auth import admin_required
from ...common.validators import get_pagination
from ...common.log_helper import log
from ...services.user_service import get_user_list, set_user_status, get_user_info

bp = Blueprint('admin_user', __name__)

@bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    p = get_pagination()
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    records, total = get_user_list(p['page'], p['size'], keyword, status)
    return paginated(records, total, p['page'], p['size'])

@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def user_detail(user_id):
    data = get_user_info(user_id)
    if data is None: return fail(404, '用户不存在')
    return success(data)

@bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    body = request.get_json(silent=True) or {}
    status = body.get('status', '')
    if status not in ('enable', 'disable'):
        return fail(400, '状态值无效')
    set_user_status(user_id, status)
    log('user_status', user_id, f'用户 {user_id} 状态改为 {status}')
    return success(None, '状态更新成功')
