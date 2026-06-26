"""请求参数校验"""
from flask import request
import re

PHONE_RE = re.compile(r'^1[3-9]\d{9}$')


def require_fields(*fields):
    """校验必填字段，返回第一个缺失的字段名，全部存在返回 None"""
    data = request.get_json(silent=True) or {}
    for f in fields:
        if f not in data or data[f] in (None, ''):
            return f
    return None


def get_pagination():
    """从 Query 参数提取分页信息"""
    return {
        'page': request.args.get('page', 1, type=int),
        'size': min(request.args.get('size', 10, type=int), 100),
        'sort_field': request.args.get('sortField', 'createTime'),
        'sort_order': request.args.get('sortOrder', 'desc'),
    }


def is_valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone))