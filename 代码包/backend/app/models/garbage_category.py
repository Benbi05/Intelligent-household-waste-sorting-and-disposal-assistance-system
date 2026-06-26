"""垃圾分类品类"""
from ..extensions import db


class GarbageCategory(db.Model):
    __tablename__ = 'garbage_category'
    categoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoryName = db.Column(db.String(64), nullable=False)
    parentType = db.Column(db.String(32), nullable=False)
    parentTypeName = db.Column(db.String(32), nullable=False)
    rewardPoint = db.Column(db.Integer, default=10)
    penaltyPoint = db.Column(db.Integer, default=5)
    guide = db.Column(db.String(256))
    status = db.Column(db.String(16), default='enable')