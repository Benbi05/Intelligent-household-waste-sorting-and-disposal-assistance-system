"""操作日志"""
from ..extensions import db
from datetime import datetime


class OperationLog(db.Model):
    __tablename__ = 'operation_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    adminId = db.Column(db.Integer, nullable=False)
    adminName = db.Column(db.String(64))
    actionType = db.Column(db.String(64), nullable=False)
    targetId = db.Column(db.Integer)
    detail = db.Column(db.Text)
    ip = db.Column(db.String(64))
    createTime = db.Column(db.DateTime, default=datetime.utcnow)