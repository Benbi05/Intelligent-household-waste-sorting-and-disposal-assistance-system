"""商家子账号"""
from ..extensions import db


class SubAccount(db.Model):
    __tablename__ = 'sub_account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merchantId = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    passwordHash = db.Column(db.String(256), nullable=False)
    displayName = db.Column(db.String(64))
    permissions = db.Column(db.Text)
    status = db.Column(db.String(16), default='enable')