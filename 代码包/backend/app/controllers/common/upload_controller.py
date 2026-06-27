"""图片上传接口 — API0002"""
from flask import Blueprint
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
