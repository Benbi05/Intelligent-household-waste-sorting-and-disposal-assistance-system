"""AI消费推荐 — 运维推送给商家"""
from ..extensions import db
from datetime import datetime


class Recommendation(db.Model):
    __tablename__ = 'recommendation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merchantId = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    community = db.Column(db.String(64))
    content = db.Column(db.Text)
    products = db.Column(db.Text)  # JSON: [{category, product, reason}]
    status = db.Column(db.String(16), default='unread')  # unread / read
    createTime = db.Column(db.DateTime, default=datetime.utcnow)
