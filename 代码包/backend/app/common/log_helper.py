"""操作日志记录工具"""
from flask import request, g
from ..extensions import db
from ..models.operation_log import OperationLog


def log(action_type: str, target_id=None, detail=''):
    try:
        admin_id = g.user_id
        role = g.role
        entry = OperationLog(
            adminId=admin_id, adminName=role,
            actionType=action_type, targetId=target_id,
            detail=detail, ip=request.remote_addr or ''
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        pass  # 日志记录失败不影响主流程
