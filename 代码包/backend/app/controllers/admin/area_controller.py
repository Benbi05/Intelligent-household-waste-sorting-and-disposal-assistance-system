"""区域管理接口 — API304~307"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.auth import admin_required
from ...common.log_helper import log
from ...models.area import Area
from ...extensions import db

bp = Blueprint('admin_area', __name__)

@bp.route('/areas', methods=['GET'])
@admin_required
def list_areas():
    areas = Area.query.order_by(Area.id).all()
    return success([{
        'areaId': a.id, 'areaName': a.areaName,
        'deviceCount': a.deviceCount, 'status': a.status,
        'description': a.description,
    } for a in areas])

@bp.route('/areas', methods=['POST'])
@admin_required
def create_area():
    body = request.get_json(silent=True) or {}
    name = body.get('areaName', '').strip()
    if not name:
        return fail(400, '区域名称不能为空')
    if Area.query.filter_by(areaName=name).first():
        return fail(400, '区域名称已存在')
    area = Area(areaName=name, description=body.get('description', ''))
    db.session.add(area)
    db.session.commit()
    log('area_create', area.id, f'创建区域: {name}')
    return success({'areaId': area.id}, '创建成功')

@bp.route('/areas/<int:area_id>', methods=['PUT'])
@admin_required
def update_area(area_id):
    area = Area.query.get(area_id)
    if not area:
        return fail(404, '区域不存在')
    body = request.get_json(silent=True) or {}
    if 'areaName' in body: area.areaName = body['areaName']
    if 'description' in body: area.description = body['description']
    db.session.commit()
    log('area_update', area_id, f'修改区域: {area.areaName}')
    return success(None, '更新成功')

@bp.route('/areas/<int:area_id>', methods=['DELETE'])
@admin_required
def delete_area(area_id):
    area = Area.query.get(area_id)
    if not area: return fail(404, '区域不存在')
    db.session.delete(area)
    db.session.commit()
    log('area_delete', area_id, f'删除区域: {area.areaName}')
    return success(None, '删除成功')
