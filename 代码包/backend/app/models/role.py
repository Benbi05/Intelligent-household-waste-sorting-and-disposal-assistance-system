"""管理员角色"""
from ..extensions import db


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roleName = db.Column(db.String(64), unique=True, nullable=False)
    permissions = db.Column(db.Text)
    description = db.Column(db.String(256))