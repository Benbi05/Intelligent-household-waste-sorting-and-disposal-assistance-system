"""区域"""
from ..extensions import db


class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    areaName = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    deviceCount = db.Column(db.Integer, default=0)
    status = db.Column(db.String(16), default='active')