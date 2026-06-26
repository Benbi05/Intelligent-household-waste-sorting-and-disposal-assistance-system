"""分析报告"""
from ..extensions import db
from datetime import datetime


class AnalysisReport(db.Model):
    __tablename__ = 'analysis_report'
    reportId = db.Column(db.String(32), primary_key=True)
    statMonth = db.Column(db.String(16), nullable=False)
    statArea = db.Column(db.String(64))
    reportType = db.Column(db.String(16), nullable=False)
    status = db.Column(db.String(16), default='pending')
    consumeTrend = db.Column(db.Text)
    hotProducts = db.Column(db.Text)
    suggestion = db.Column(db.Text)
    fullContent = db.Column(db.Text)
    generateTime = db.Column(db.DateTime, default=datetime.utcnow)
    generateDuration = db.Column(db.Integer, default=0)