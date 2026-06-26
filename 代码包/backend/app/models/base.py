"""模型基类"""
from datetime import datetime
from ..extensions import db


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updateTime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}