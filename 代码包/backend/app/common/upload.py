"""文件上传处理 — base64 存储，无需本地文件系统"""
import base64
from flask import request

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def handle() -> dict:
    """处理上传，返回 {ok, error_code, imageUrl|None}"""
    if 'file' not in request.files:
        return {'ok': False, 'error_code': 2004}

    file = request.files['file']
    if file.mimetype not in ALLOWED_TYPES:
        return {'ok': False, 'error_code': 2001}

    file.seek(0, 2)  # SEEK_END
    size = file.tell()
    file.seek(0)
    if size > MAX_SIZE:
        return {'ok': False, 'error_code': 2002}

    # base64 编码存储，不依赖本地文件
    b64 = base64.b64encode(file.read()).decode()
    data_uri = f'data:{file.mimetype};base64,{b64}'
    return {'ok': True, 'error_code': 0, 'imageUrl': data_uri, 'url': data_uri}