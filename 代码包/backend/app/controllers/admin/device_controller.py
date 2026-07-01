"""设备管理 - API313~319"""
from flask import Blueprint, request
from ...common.response import success, fail, paginated
from ...common.auth import admin_required
from ...common.validators import get_pagination
from ...common.log_helper import log
from ...services.device_service import add_device, get_device_list
from ...models.device import Device
from ...extensions import db

bp = Blueprint("admin_device", __name__)

@bp.route("/devices", methods=["GET"])
@admin_required
def list_devices():
    p = get_pagination()
    records, total = get_device_list(
        p["page"], p["size"],
        keyword=request.args.get("keyword", ""),
        online_status=request.args.get("onlineStatus", ""),
        box_category=request.args.get("boxCategory", ""),
        area=request.args.get("area", ""),
        community=request.args.get("community", "")
    )
    return paginated(records, total, p["page"], p["size"])

@bp.route("/devices", methods=["POST"])
@admin_required
def create_device():
    body = request.get_json(silent=True) or {}
    name = body.get("deviceName", "").strip()
    if not name: return fail(400, "设备名称不能为空")
    device_id = add_device(name, body.get("boxCategory", "recyclable"),
                           body.get("area", ""), body.get("location", ""),
                           body.get("secret", "default123"))
    log('device_create', None, f'新增设备: {name} ({device_id})')
    return success({"deviceId": device_id}, "设备添加成功")

@bp.route("/devices/<device_id>", methods=["GET"])
@admin_required
def device_detail(device_id):
    d = Device.query.get(device_id)
    if not d: return fail(404, "设备不存在")
    return success(d.to_dict())

@bp.route("/devices/<device_id>/status", methods=["PUT"])
@admin_required
def device_status(device_id):
    body = request.get_json(silent=True) or {}
    status = body.get("status", "")
    if status not in ("enable", "disable"): return fail(400, "状态值无效")
    d = Device.query.get(device_id)
    if not d: return fail(404, "设备不存在")
    d.status = status; db.session.commit()
    log('device_status', None, f'设备 {device_id} 状态改为 {status}')
    return success(None, "状态更新成功")

@bp.route("/devices/<device_id>", methods=["DELETE"])
@admin_required
def delete_device(device_id):
    d = Device.query.get(device_id)
    if not d: return fail(404, "设备不存在")
    db.session.delete(d); db.session.commit()
    log('device_delete', None, f'删除设备: {device_id}')
    return success(None, "删除成功")

@bp.route("/devices/<device_id>/config", methods=["PUT"])
@admin_required
def device_config(device_id):
    d = Device.query.get(device_id)
    if not d: return fail(404, "设备不存在")
    body = request.get_json(silent=True) or {}
    for key in ("deviceName", "boxCategory", "area", "location"):
        if key in body and body[key] is not None:
            setattr(d, key, body[key])
    db.session.commit()
    log('device_config', None, f'修改设备配置: {device_id}')
    return success({"commandId": f"CMD{device_id}"}, "配置已下发")

@bp.route("/devices/firmware-upgrade", methods=["POST"])
@admin_required
def firmware_upgrade():
    body = request.get_json(silent=True) or {}
    device_ids = body.get("deviceIds", [])
    if not device_ids: return fail(400, "请选择设备")
    version = body.get("firmwareVersion", "")
    if not version: return fail(400, "请指定固件版本")
    log('firmware_upgrade', None, f'固件升级: {version}, 设备数={len(device_ids)}')
    return success({"commandId": f"OTA{len(device_ids)}", "affectedDeviceCount": len(device_ids)}, "升级指令已下发")

@bp.route("/devices/stats", methods=["GET"])
@admin_required
def device_stats():
    """设备统计概览"""
    c = request.args.get("community", "")
    q = Device.query
    if c: q = q.filter(Device.deviceId.like(f'{c}%'))
    total = q.count()
    online = q.filter_by(onlineStatus="online").count()
    offline = q.filter_by(onlineStatus="offline").count()
    fault = q.filter_by(onlineStatus="fault").count()
    pending = q.filter_by(onlineStatus="pending_check").count()
    return success({"totalDevices": total, "online": online, "offline": offline, "fault": fault, "pending": pending})
