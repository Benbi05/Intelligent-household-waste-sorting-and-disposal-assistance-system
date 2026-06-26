"""用户基类"""
from .base import BaseModel
from ..extensions import db


class User(BaseModel):
    __tablename__ = 'user'
    openid = db.Column(db.String(128), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    nickName = db.Column(db.String(64), default='用户')
    avatarUrl = db.Column(db.String(512), default='')
    status = db.Column(db.String(16), default='enable')
    userType = db.Column(db.String(16), nullable=False)