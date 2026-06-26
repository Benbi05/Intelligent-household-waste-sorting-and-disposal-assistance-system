"""OperationLog 数据操作类"""
from .base_dao import BaseDAO
from ..models.operation_log import OperationLog


class OperationLogDAO(BaseDAO):
    model = OperationLog

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.model.query.filter_by(userId=user_id).all()
