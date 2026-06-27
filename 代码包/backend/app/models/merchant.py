"""商家"""
from ..extensions import db


class Merchant(db.Model):
    __tablename__ = 'merchant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    passwordHash = db.Column(db.String(256), nullable=False)
    storeName = db.Column(db.String(128), unique=True, nullable=False)
    contactName = db.Column(db.String(64))
    contactPhone = db.Column(db.String(20))
    storeAddress = db.Column(db.String(256))
    businessLicense = db.Column(db.String(512))
    area = db.Column(db.String(64))
    description = db.Column(db.Text)
    status = db.Column(db.String(16), default='pending')
    auditTime = db.Column(db.DateTime, nullable=True)