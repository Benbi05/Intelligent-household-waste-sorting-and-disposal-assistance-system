"""投放记录"""
from ..extensions import db
from datetime import datetime


class DeliveryRecord(db.Model):
    __tablename__ = 'delivery_record'
    recordId = db.Column(db.String(32), primary_key=True)
    deviceId = db.Column(db.String(32), db.ForeignKey('device.deviceId'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    imageUrl = db.Column(db.String(512))
    boxCategory = db.Column(db.String(32))
    garbageCategory = db.Column(db.String(64))
    parentType = db.Column(db.String(32))
    isCorrect = db.Column(db.Boolean, default=False)
    pointChange = db.Column(db.Integer, default=0)
    weight = db.Column(db.Float, default=0.0)
    deliveryTime = db.Column(db.DateTime, default=datetime.utcnow)
    ruleVersion = db.Column(db.String(16))