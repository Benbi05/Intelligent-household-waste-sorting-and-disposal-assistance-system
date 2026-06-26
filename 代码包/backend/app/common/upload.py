"""文件上传处理"""
import os
import uuid
from flask import request

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_SIZE = 10 * 1024 * 1024  # 10MB


def handle() -> dict:
    """处理上传，返回 {ok, error_code, imageUrl|None}"""
    if 'file' not in request.files:
        return {'ok': False, 'error_code': 2004}

    file = request.files['file']
    if file.mimetype not in ALLOWED_TYPES:
        return {'ok': False, 'error_code': 2001}

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_SIZE:
        return {'ok': False, 'error_code': 2002}

    ext = 'jpg' if file.mimetype == 'image/jpeg' else file.mimetype.split('/')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'

    # TODO: 上传至 OSS/S3，病毒扫描
    image_url = f'https://cdn.garbage-system.com/images/{filename}'
    return {'ok': True, 'error_code': 0, 'imageUrl': image_url}