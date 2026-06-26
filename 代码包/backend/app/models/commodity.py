"""兑换商品"""
from ..extensions import db


class Commodity(db.Model):
    __tablename__ = 'commodity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    commodityName = db.Column(db.String(128), nullable=False)
    merchantId = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    pointPrice = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imageUrl = db.Column(db.String(512))
    description = db.Column(db.Text)
    useRules = db.Column(db.String(256))
    status = db.Column(db.String(16), default='on')
    monthExchangeCount = db.Column(db.Integer, default=0)
    version = db.Column(db.Integer, default=1)