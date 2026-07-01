"""
Unified API response format.
Matches the project-wide response convention:
{ "code": 200, "message": "...", "data": {}, "timestamp": "ISO8601" }
"""
from datetime import datetime, timezone, timedelta
from flask import jsonify


# Beijing timezone (UTC+8)
TZ_BEIJING = timezone(timedelta(hours=8))


def _now_iso() -> str:
    """Return current time in ISO 8601 with Beijing timezone."""
    return datetime.now(TZ_BEIJING).isoformat()


def success(data=None, message: str = '操作成功', code: int = 200):
    """Build a success response."""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': _now_iso(),
    })


def error(message: str, code: int = 400, data=None):
    """Build an error response."""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': _now_iso(),
    }), 400 if code >= 400 and code < 500 else 500


# Common error codes specific to AI service
AI_ERROR_CODES = {
    # Recognition errors
    'IMAGE_BLURRY': (3101, '图片模糊或无有效垃圾'),
    'RECOGNIZE_TIMEOUT': (3102, '识别服务超时'),
    'URL_NOT_WHITELISTED': (3103, 'URL域名不在白名单内'),
    'URL_INTERNAL_IP': (3104, 'URL指向内网地址'),
    'IMAGE_DOWNLOAD_FAILED': (3105, '图片下载失败'),
    'IMAGE_FORMAT_INVALID': (3106, '图片格式不支持'),
    'IMAGE_SIZE_EXCEEDED': (3107, '图片大小超过上限'),
    # Model management errors
    'MODEL_NOT_FOUND': (3301, '模型版本不存在'),
    'TRAIN_DATASET_INVALID': (3302, '训练数据集格式校验失败'),
    'TRAIN_TASK_NOT_FOUND': (3303, '训练任务不存在'),
    'MODEL_SWITCH_FAILED': (3304, '模型切换失败'),
    # Analysis errors
    'ANALYSIS_TIMEOUT': (3401, '分析报告生成超时'),
    'ANALYSIS_NO_DATA': (3402, '当前周期无可用数据'),
    'REPORT_NOT_FOUND': (3403, '分析报告不存在'),
}


def ai_error(error_key: str, detail: str = ''):
    """Build an AI-specific error response from predefined error codes."""
    code, default_msg = AI_ERROR_CODES.get(error_key, (500, '未知错误'))
    message = f'{default_msg}：{detail}' if detail else default_msg
    return error(message, code)
