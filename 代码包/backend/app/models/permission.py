"""权限"""
from ..extensions import db


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    permKey = db.Column(db.String(64), unique=True, nullable=False)
    permName = db.Column(db.String(64), nullable=False)
    group = db.Column(db.String(32))