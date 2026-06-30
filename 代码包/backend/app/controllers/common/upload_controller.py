"""图片上传接口 — API0002"""
import os
from flask import Blueprint, send_file
from ...common.auth import login_required
from ...common.response import success, fail
from ...common.upload import handle

bp = Blueprint('upload', __name__)

@bp.route('/upload/image', methods=['POST'])
@login_required
def upload_image():
    result = handle()
    if result['ok']:
        return success({'imageUrl': result['imageUrl']}, '上传成功')
    return fail(result['error_code'], '上传失败')

@bp.route('/upload/public', methods=['POST'])
def upload_public():
    """公开上传（商家入驻时上传证照）"""
    result = handle()
    if result['ok']:
        return success({'imageUrl': result['imageUrl'], 'url': result['url']}, '上传成功')
    return fail(result['error_code'], '上传失败')

@bp.route('/upload/file/<filename>', methods=['GET'])
def serve_upload(filename):
    """访问上传的文件"""
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'uploads')
    filepath = os.path.join(upload_dir, filename)
    if not os.path.exists(filepath):
        return fail(404, '文件不存在')
    return send_file(filepath)
