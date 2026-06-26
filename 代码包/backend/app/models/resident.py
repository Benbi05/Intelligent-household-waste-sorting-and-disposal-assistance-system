"""居民用户"""
from ..extensions import db


class Resident(db.Model):
    __tablename__ = 'resident'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    totalDeliveryTimes = db.Column(db.Integer, default=0)
    correctTimes = db.Column(db.Integer, default=0)
    correctRate = db.Column(db.Float, default=0.0)
    area = db.Column(db.String(64), default='')