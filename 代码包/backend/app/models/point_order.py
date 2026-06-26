"""积分兑换订单"""
from ..extensions import db
from datetime import datetime


class PointOrder(db.Model):
    __tablename__ = 'point_order'
    orderId = db.Column(db.String(32), primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commodityId = db.Column(db.Integer, db.ForeignKey('commodity.id'), nullable=False)
    merchantId = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    pointCost = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    verifyCode = db.Column(db.String(16), unique=True)
    orderStatus = db.Column(db.String(16), default='unverified')
    idempotentKey = db.Column(db.String(64))
    createTime = db.Column(db.DateTime, default=datetime.utcnow)
    verifyTime = db.Column(db.DateTime, nullable=True)
    expireTime = db.Column(db.DateTime, nullable=False)