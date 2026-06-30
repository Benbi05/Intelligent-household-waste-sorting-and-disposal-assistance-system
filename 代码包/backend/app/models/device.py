"""智能垃圾箱设备"""
from ..extensions import db
from datetime import datetime


class Device(db.Model):
    __tablename__ = 'device'
    deviceId = db.Column(db.String(32), primary_key=True)
    deviceName = db.Column(db.String(128), nullable=False)
    deviceSecret = db.Column(db.String(256), nullable=False)
    boxCategory = db.Column(db.String(32), nullable=False)
    area = db.Column(db.String(64))
    location = db.Column(db.String(256))
    onlineStatus = db.Column(db.String(16), default='offline')
    fullRate = db.Column(db.Float, default=0.0)
    cameraStatus = db.Column(db.String(16), default='offline')
    networkStatus = db.Column(db.String(16), default='offline')
    powerStatus = db.Column(db.String(16), default='offline')
    displayStatus = db.Column(db.String(16), default='offline')
    firmwareVersion = db.Column(db.String(32), default='v1.0.0')
    status = db.Column(db.String(16), default='enable')
    lastOnlineTime = db.Column(db.DateTime, default=datetime.utcnow)
    totalDeliveryCount = db.Column(db.Integer, default=0)
    todayDeliveryCount = db.Column(db.Integer, default=0)
    lat = db.Column(db.Float, default=None)
    lng = db.Column(db.Float, default=None)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}