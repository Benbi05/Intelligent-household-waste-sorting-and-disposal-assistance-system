"""
Model Management API Blueprint
Provides endpoints for model version management, switching, and training.

Corresponding interface doc APIs:
  - API326: GET  /admin/model/versions    (model version list)
  - API327: POST /admin/model/switch      (switch model version)
  - API328: POST /admin/model/train       (trigger incremental training)
  - API329: GET  /admin/model/train/{id}  (training status query)
"""
from flask import Blueprint, request
from 代码包.ai_service.models.model_registry import get_model_registry
from 代码包.ai_service.models.model_loader import get_model_loader
from 代码包.ai_service.services.training_service import get_training_service
from 代码包.ai_service.utils.response import success, error, ai_error
from 代码包.ai_service.config import CANARY_CONFIG, logger

model_bp = Blueprint('model', __name__)


@model_bp.route('/model/versions', methods=['GET'])
def list_model_versions():
    """
    Get all model versions with metrics.

    Response:
        {
            "code": 200,
            "data": [{
                "modelId": 5,
                "version": "v1.5",
                "mAP": 0.92,
                "accuracy": 0.91,
                "precision": 0.93,
                "recall": 0.89,
                "categoryCount": 56,
                "status": "online",
                "publishTime": "2026-06-01T00:00:00+08:00"
            }]
        }
    """
    try:
        registry = get_model_registry()
        versions = registry.list_versions()
        return success(versions, '查询成功')
    except Exception as e:
        logger.error(f'Failed to list model versions: {e}', exc_info=True)
        return error(f'查询模型版本失败: {str(e)}', 500)


@model_bp.route('/model/versions/active', methods=['GET'])
def get_active_model():
    """Get the currently active (online) model version info."""
    try:
        registry = get_model_registry()
        active = registry.get_active_version()
        if active:
            return success(active, '查询成功')
        return ai_error('MODEL_NOT_FOUND', '无在线模型版本')
    except Exception as e:
        return error(f'查询失败: {str(e)}', 500)


@model_bp.route('/model/switch', methods=['POST'])
def switch_model():
    """
    Switch the active model version.
    Supports full switch and canary (grayscale) deployment.

    Request body (JSON):
        {
            "switchType": "full",        // "full" | "canary"
            "targetVersion": "v1.6",     // target model version
            "canaryPercent": 20          // 5-50, only for canary mode
        }

    Response:
        {
            "code": 200,
            "data": {
                "newVersion": "v1.6",
                "effectTime": "2026-06-26T12:00:00+08:00"
            }
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return error('请求体不能为空', 400)

    switch_type = data.get('switchType', 'full').strip()
    target_version = data.get('targetVersion', '').strip()
    canary_percent = data.get('canaryPercent', 0)

    if not target_version:
        return error('缺少必填参数 targetVersion', 400)

    if switch_type not in ('full', 'canary'):
        return error('switchType 必须为 full 或 canary', 400)

    # Verify target version exists
    registry = get_model_registry()
    version_info = registry.get_version(target_version)
    if version_info is None:
        return ai_error('MODEL_NOT_FOUND', f'版本 {target_version} 不存在')

    try:
        if switch_type == 'full':
            # Full switch: set target as online, archive current
            registry.set_version_status(target_version, 'online')
            CANARY_CONFIG['enabled'] = False
            CANARY_CONFIG['canary_version'] = None
            CANARY_CONFIG['canary_percent'] = 0

            # Pre-load the new model
            loader = get_model_loader()
            loader.load_model(target_version)

            logger.info(f'Model switched to {target_version} (full)')

        elif switch_type == 'canary':
            # Canary: keep current online, route percentage to new
            if canary_percent < 5 or canary_percent > 50:
                return error('canaryPercent 必须在 5-50 之间', 400)

            CANARY_CONFIG['enabled'] = True
            CANARY_CONFIG['canary_version'] = target_version
            CANARY_CONFIG['canary_percent'] = canary_percent

            # Pre-load the canary model
            loader = get_model_loader()
            loader.load_model(target_version)

            registry.set_version_status(target_version, 'online')
            logger.info(
                f'Model canary deployment: {target_version} at {canary_percent}%'
            )

        from datetime import datetime, timezone, timedelta
        return success({
            'newVersion': target_version,
            'switchType': switch_type,
            'canaryPercent': canary_percent if switch_type == 'canary' else None,
            'effectTime': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        }, '模型版本已切换')

    except FileNotFoundError as e:
        return ai_error('MODEL_SWITCH_FAILED', f'模型文件不存在: {e}')
    except Exception as e:
        logger.error(f'Model switch failed: {e}', exc_info=True)
        return ai_error('MODEL_SWITCH_FAILED', str(e))


@model_bp.route('/model/train', methods=['POST'])
def trigger_training():
    """
    Trigger incremental model training.

    Request body (JSON):
        {
            "datasetUrl": "https://cdn.../dataset.zip",
            "datasetName": "6月新增垃圾品类数据集",
            "baseModelVersion": "v1.5",
            "callbackUrl": "https://api.garbage-system.com/v1/internal/train-callback"
        }

    Response:
        {
            "code": 200,
            "data": {
                "taskId": "TRAIN20260625001",
                "status": "pending",
                "estimatedTime": 7200
            }
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return error('请求体不能为空', 400)

    dataset_url = data.get('datasetUrl', '').strip()
    dataset_name = data.get('datasetName', '').strip()
    base_model_version = data.get('baseModelVersion', '').strip()
    callback_url = data.get('callbackUrl', '').strip()

    if not dataset_url:
        return error('缺少必填参数 datasetUrl', 400)
    if not base_model_version:
        return error('缺少必填参数 baseModelVersion', 400)

    # Verify base model exists
    registry = get_model_registry()
    if not registry.get_version(base_model_version):
        return ai_error('MODEL_NOT_FOUND', f'基础模型版本 {base_model_version} 不存在')

    try:
        training_svc = get_training_service()
        task_id = training_svc.trigger_training(
            dataset_url, dataset_name,
            base_model_version,
            callback_url,
        )

        return success({
            'taskId': task_id,
            'status': 'pending',
            'estimatedTime': 7200,
        }, '训练任务已提交')

    except ValueError as e:
        error_msg = str(e)
        if error_msg.startswith('TRAIN_DATASET_INVALID'):
            return ai_error('TRAIN_DATASET_INVALID', error_msg.split(': ', 1)[-1])
        return error(error_msg, 400)

    except Exception as e:
        logger.error(f'Training trigger failed: {e}', exc_info=True)
        return error(f'训练任务提交失败: {str(e)}', 500)


@model_bp.route('/model/train/<task_id>', methods=['GET'])
def get_training_status(task_id):
    """
    Query training task status and progress.

    Response (running):
        {
            "code": 200,
            "data": {
                "taskId": "TRAIN20260625001",
                "status": "running",
                "progress": 45,
                "estimatedRemain": 3600
            }
        }

    Response (completed):
        {
            "code": 200,
            "data": {
                "taskId": "TRAIN20260625001",
                "status": "success",
                "newModelVersion": "v1.6",
                "modelId": 6,
                "accuracy": 0.93,
                "mAP": 0.94,
                "precision": 0.94,
                "recall": 0.91
            }
        }
    """
    training_svc = get_training_service()
    status = training_svc.get_training_status(task_id)

    if status is None:
        return ai_error('TRAIN_TASK_NOT_FOUND', f'训练任务 {task_id} 不存在')

    return success(status, '查询成功')


@model_bp.route('/model/health', methods=['GET'])
def model_health():
    """Health check for model management service."""
    try:
        loader = get_model_loader()
        return success(loader.health_check(), 'Model service healthy')
    except Exception as e:
        return error(f'Model service unhealthy: {str(e)}', 500)
