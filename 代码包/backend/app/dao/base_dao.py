"""通用 DAO 基类 — 提供所有表通用的 CRUD 方法"""
from ..extensions import db


class BaseDAO:
    model = None

    @classmethod
    def get_by_id(cls, id):
        return cls.model.query.get(id)

    @classmethod
    def get_one(cls, **filters):
        return cls.model.query.filter_by(**filters).first()

    @classmethod
    def get_all(cls, **filters):
        return cls.model.query.filter_by(**filters).all()

    @classmethod
    def get_paginated(cls, page=1, size=10, order_by='createTime', order_dir='desc', **filters):
        q = cls.model.query.filter_by(**filters)
        col = getattr(cls.model, order_by, cls.model.createTime)
        q = q.order_by(col.desc() if order_dir == 'desc' else col.asc())
        p = q.paginate(page=page, per_page=size, error_out=False)
        return p.items, p.total

    @classmethod
    def create(cls, **kwargs):
        obj = cls.model(**kwargs)
        db.session.add(obj)
        db.session.flush()
        return obj

    @classmethod
    def update(cls, id, **kwargs):
        obj = cls.get_by_id(id)
        if obj:
            for k, v in kwargs.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
            db.session.flush()
        return obj

    @classmethod
    def delete(cls, id):
        obj = cls.get_by_id(id)
        if obj:
            db.session.delete(obj)
            db.session.flush()
            return True
        return False

    @classmethod
    def count(cls, **filters):
        return cls.model.query.filter_by(**filters).count()

    @classmethod
    def commit(cls):
        db.session.commit()

    @classmethod
    def rollback(cls):
        db.session.rollback()