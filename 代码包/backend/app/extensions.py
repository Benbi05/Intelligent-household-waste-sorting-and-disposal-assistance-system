"""Flask 扩展初始化"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis

db = SQLAlchemy()
migrate = Migrate()
redis_client: redis.Redis = None


def init_extensions(app):
    global redis_client
    db.init_app(app)
    migrate.init_app(app, db)
    redis_client = redis.from_url(app.config['REDIS_URL'])