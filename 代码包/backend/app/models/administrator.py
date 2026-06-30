"""管理员"""
from ..extensions import db


class Administrator(db.Model):
    __tablename__ = 'administrator'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    passwordHash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), default='admin')
    community = db.Column(db.String(64), default='')
    lastLoginTime = db.Column(db.DateTime, nullable=True)