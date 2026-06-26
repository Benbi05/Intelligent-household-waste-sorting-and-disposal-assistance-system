"""识别模型版本"""
from ..extensions import db
from datetime import datetime


class RecognitionModel(db.Model):
    __tablename__ = 'recognition_model'
    modelId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version = db.Column(db.String(16), unique=True, nullable=False)
    accuracy = db.Column(db.Float, default=0.0)
    mapValue = db.Column(db.Float, default=0.0)
    precision = db.Column(db.Float, default=0.0)
    recall = db.Column(db.Float, default=0.0)
    categoryCount = db.Column(db.Integer, default=0)
    status = db.Column(db.String(16), default='offline')
    modelPath = db.Column(db.String(256))
    publishTime = db.Column(db.DateTime, default=datetime.utcnow)