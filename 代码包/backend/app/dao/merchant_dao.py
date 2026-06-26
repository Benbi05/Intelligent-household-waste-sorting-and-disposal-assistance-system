"""Merchant 数据操作类"""
from .base_dao import BaseDAO
from ..models.merchant import Merchant


class MerchantDAO(BaseDAO):
    model = Merchant

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.model.query.filter_by(userId=user_id).all()
