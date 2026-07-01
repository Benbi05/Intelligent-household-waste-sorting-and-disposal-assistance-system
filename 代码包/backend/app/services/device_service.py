"""设备业务：注册、状态、会话"""
import uuid, hashlib
from ..common.auth import generate_token
from ..dao.device_dao import DeviceDAO
from ..extensions import db, redis_client


def auth_device(device_id: str, device_secret: str) -> dict:
    device = DeviceDAO.get_by_id(device_id)
    if not device:
        return {"ok": False, "error_code": 4001}
    if device.status == "disable":
        return {"ok": False, "error_code": 4002}
    if device.deviceSecret != device_secret:
        return {"ok": False, "error_code": 4001}
    token = generate_token(device_id=device_id, role="device")
    return {"ok": True, "error_code": 0, "deviceToken": token,
            "boxCategory": device.boxCategory, "heartbeatInterval": 300}


def create_device_session(auth_code: str) -> dict:
    session_token = f"sess:{uuid.uuid4().hex[:16]}"
    redis_client.setex(session_token, 60, "mock_user_id")
    return {"ok": True, "error_code": 0, "sessionToken": session_token, "expireSeconds": 60}


def resolve_session(session_token: str) -> int:
    uid = redis_client.get(session_token)
    return int(uid) if uid else None


def add_device(device_name: str, box_category: str, area: str, location: str, secret: str) -> str:
    device_id = f"DEV-{uuid.uuid4().hex[:8].upper()}"
    device_secret = hashlib.sha256(f"{device_id}{secret}".encode()).hexdigest()[:32]
    DeviceDAO.create(deviceId=device_id, deviceName=device_name, deviceSecret=device_secret,
                     boxCategory=box_category, area=area, location=location)
    db.session.commit()
    return device_id


def get_device_list(page=1, size=10, keyword="", online_status="", box_category="", area="", community="") -> tuple:
    q = DeviceDAO.model.query
    if community:
        q = q.filter(DeviceDAO.model.deviceId.like(f'{community}%'))
    if keyword:
        q = q.filter((DeviceDAO.model.deviceId.contains(keyword)) |
                     (DeviceDAO.model.deviceName.contains(keyword)))
    if online_status:
        q = q.filter(DeviceDAO.model.onlineStatus == online_status)
    if box_category:
        q = q.filter(DeviceDAO.model.boxCategory == box_category)
    if area:
        q = q.filter(DeviceDAO.model.area == area)
    q = q.order_by(DeviceDAO.model.lastOnlineTime.desc())
    pagination = q.paginate(page=page, per_page=size, error_out=False)
    return [d.to_dict() for d in pagination.items], pagination.total


def report_device_status(device_id: str, **kwargs) -> dict:
    from datetime import datetime
    kwargs["onlineStatus"] = "online"
    kwargs["lastOnlineTime"] = datetime.utcnow()
    allowed = {c.name for c in DeviceDAO.model.__table__.columns}
    DeviceDAO.update(device_id, **{k: v for k, v in kwargs.items() if k in allowed})
    db.session.commit()
    return {"configUpdated": False, "latestFirmwareVersion": "v1.0.0"}
