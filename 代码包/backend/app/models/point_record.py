"""积分流水"""
from ..extensions import db
from datetime import datetime


class PointRecord(db.Model):
    __tablename__ = 'point_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    changeAmount = db.Column(db.Integer, nullable=False)
    recordType = db.Column(db.String(16), nullable=False)
    reason = db.Column(db.String(256))
    relatedId = db.Column(db.String(64))
    createTime = db.Column(db.DateTime, default=datetime.utcnow)