"""积分账户"""
from ..extensions import db


class PointAccount(db.Model):
    __tablename__ = 'point_account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=0)
    totalEarned = db.Column(db.Integer, default=0)
    totalSpent = db.Column(db.Integer, default=0)