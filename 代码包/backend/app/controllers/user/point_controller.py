"""用户积分接口 — API109~111"""
from flask import Blueprint, request, g
from ...common.response import success, paginated
from ...common.auth import login_required
from ...common.validators import get_pagination
from ...services.point_service import get_point_account, get_point_records, get_current_rules

bp = Blueprint('user_point', __name__)

@bp.route('/point/account', methods=['GET'])
@login_required
def point_account():
    return success(get_point_account(g.user_id))

@bp.route('/point/records', methods=['GET'])
@login_required
def point_records():
    p = get_pagination()
    record_type = request.args.get('recordType', '')
    records, total = get_point_records(g.user_id, p['page'], p['size'], record_type)
    return paginated(records, total, p['page'], p['size'])

@bp.route('/point/rules', methods=['GET'])
@login_required
def point_rules():
    return success(get_current_rules())
