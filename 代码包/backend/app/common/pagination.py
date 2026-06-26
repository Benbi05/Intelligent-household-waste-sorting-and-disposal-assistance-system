"""分页查询工具"""
from flask_sqlalchemy.pagination import Pagination


def paginate(query, page=1, size=10):
    """执行分页，返回 (records, total)"""
    p: Pagination = query.paginate(page=page, per_page=size, error_out=False)
    return p.items, p.total