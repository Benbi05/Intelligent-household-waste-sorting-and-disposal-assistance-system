"""数据库初始化 — 创建所有表"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app('development')

with app.app_context():
    db.create_all()
    print('所有表创建完成！')

    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'共 {len(tables)} 张表:')
    for t in tables:
        print(f'  - {t}')