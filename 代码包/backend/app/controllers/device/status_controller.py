"""设备状态上报接口 — API204"""
from flask import Blueprint, request, g
from ...common.response import success
from ...common.auth import device_required
from ...services.device_service import report_device_status

bp = Blueprint('device_status', __name__)

@bp.route('/status/report', methods=['POST'])
@device_required
def report():
    body = request.get_json(silent=True) or {}
    result = report_device_status(
        device_id=g.device_id,
        fullRate=body.get('fullRate', 0),
        cameraStatus=body.get('cameraStatus', 'online'),
        networkStatus=body.get('networkStatus', 'online'),
        powerStatus=body.get('powerStatus', 'online'),
        displayStatus=body.get('displayStatus', 'online'),
        firmwareVersion=body.get('firmwareVersion', ''),
        errorCode=body.get('errorCode', ''),
    )
    return success(result, '上报成功')
