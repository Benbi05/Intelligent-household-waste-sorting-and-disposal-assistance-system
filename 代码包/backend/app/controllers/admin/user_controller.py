"""管理员用户管理接口 — API308~310"""
from flask import Blueprint, request
from ...common.response import success, fail, paginated
from ...common.auth import admin_required
from ...common.validators import get_pagination
from ...common.log_helper import log
from ...services.user_service import get_user_list, set_user_status, get_user_info
from ...models.user import User
from ...models.delivery_record import DeliveryRecord
from ...extensions import db
from sqlalchemy import func
from datetime import datetime

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

@bp.route('/users/stats', methods=['GET'])
@admin_required
def user_stats():
    """用户统计概览"""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total = User.query.filter_by(userType="resident").count()
    new_this_month = User.query.filter(User.userType == "resident", User.createTime >= month_start).count()
    active = User.query.filter_by(userType="resident", status="enable").count()
    # 从投放记录计算平均正确率
    result = db.session.query(
        func.count(DeliveryRecord.recordId),
        func.sum(DeliveryRecord.isCorrect.cast(db.Integer))
    ).first()
    total_deliveries, total_correct = result[0] or 0, result[1] or 0
    avg_rate = round(total_correct / total_deliveries, 2) if total_deliveries > 0 else 0
    return success({"totalUsers": total, "newThisMonth": new_this_month, "activeUsers": active, "avgCorrectRate": avg_rate})
