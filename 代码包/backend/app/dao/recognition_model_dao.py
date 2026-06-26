"""RecognitionModel 数据操作类"""
from .base_dao import BaseDAO
from ..models.recognition_model import RecognitionModel


class RecognitionModelDAO(BaseDAO):
    model = RecognitionModel

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.model.query.filter_by(userId=user_id).all()
