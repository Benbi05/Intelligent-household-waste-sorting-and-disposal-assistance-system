"""AI模型管理 — ops_admin"""
from flask import Blueprint, request
from ...common.response import success, fail
from ...common.auth import admin_required
from ...common.log_helper import log
from ...models.recognition_model import RecognitionModel
from ...extensions import db
from datetime import datetime

bp = Blueprint('admin_model', __name__)


@bp.route('/models', methods=['GET'])
@admin_required
def list_models():
    models = RecognitionModel.query.order_by(RecognitionModel.modelId.desc()).all()
    records = []
    for m in models:
        records.append({
            'modelId': m.modelId, 'version': m.version,
            'accuracy': round(m.accuracy * 100, 1) if m.accuracy else 0,
            'mapValue': round(m.mapValue * 100, 1) if m.mapValue else 0,
            'precision': round(m.precision * 100, 1) if m.precision else 0,
            'recall': round(m.recall * 100, 1) if m.recall else 0,
            'categoryCount': m.categoryCount or 0,
            'status': m.status,
            'publishTime': m.publishTime.isoformat() if m.publishTime else '',
        })
    return success(records)


@bp.route('/models/publish', methods=['POST'])
@admin_required
def publish_model():
    body = request.get_json(silent=True) or {}
    version = body.get('version', '').strip()
    if not version:
        return fail(400, '请输入版本号')
    if RecognitionModel.query.filter_by(version=version).first():
        return fail(400, '该版本已存在')
    model = RecognitionModel(
        version=version,
        accuracy=body.get('accuracy', 0.9),
        mapValue=body.get('mapValue', 0.85),
        precision=body.get('precision', 0.88),
        recall=body.get('recall', 0.82),
        categoryCount=body.get('categoryCount', 517),
        status='offline', publishTime=datetime.utcnow()
    )
    db.session.add(model)
    db.session.commit()
    log('model_publish', model.modelId, f'发布模型版本: {version}')
    return success({'modelId': model.modelId}, '模型发布成功')


@bp.route('/models/<int:model_id>/switch', methods=['POST'])
@admin_required
def switch_model(model_id):
    model = RecognitionModel.query.get(model_id)
    if not model:
        return fail(404, '模型不存在')
    RecognitionModel.query.update({'status': 'offline'})
    model.status = 'active'
    db.session.commit()
    log('model_switch', model_id, f'切换AI模型至: {model.version}')
    return success({'version': model.version}, f'已切换至 {model.version}')
