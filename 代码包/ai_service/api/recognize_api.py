"""
Recognition API Blueprint
Provides endpoints for garbage image recognition.

Corresponding interface doc APIs:
  - API105: POST /user/garbage/recognize  (mini-program photo query)
  - API203: POST /device/delivery/submit  (terminal delivery, AI part)
"""
from flask import Blueprint, request
from 代码包.ai_service.services.recognition_service import get_recognition_service
from 代码包.ai_service.services.guide_service import get_guide_service
from 代码包.ai_service.utils.response import success, error, ai_error
from 代码包.ai_service.config import logger

recognize_bp = Blueprint('recognize', __name__)


@recognize_bp.route('/recognize', methods=['POST'])
def recognize_garbage():
    """
    Garbage image recognition endpoint.

    Request body (JSON):
        { "imageUrl": "https://cdn.garbage-system.com/images/2026/06/abc.jpg" }

    Response:
        {
            "code": 200,
            "data": {
                "recognizeId": "REC...",
                "resultList": [{
                    "categoryId": 101,
                    "categoryName": "塑料饮料瓶",
                    "parentType": "recyclable",
                    "parentTypeName": "可回收物",
                    "confidence": 0.96,
                    "guide": "请清空内容物后投入可回收物桶",
                    "boxRegion": {"x": 0.15, "y": 0.22, "width": 0.45, "height": 0.63}
                }],
                "createTime": "2026-06-26T10:30:00+08:00"
            }
        }

    Error codes:
        3101: Image blurry or no valid garbage
        3102: Recognition timeout
        3103: URL domain not whitelisted
        3104: URL points to internal IP
        3105: Image download failed
        3106: Image format not supported
        3107: Image size exceeded
    """
    data = request.get_json(silent=True)
    if not data or 'imageUrl' not in data:
        return error('缺少必填参数 imageUrl', 400)

    image_url = data['imageUrl'].strip()
    if not image_url:
        return error('imageUrl 不能为空', 400)

    logger.info(f'Recognition request for image: {image_url[:80]}...')

    try:
        service = get_recognition_service()
        result = service.recognize_from_url(image_url)
        return success(result, '识别成功')

    except ValueError as e:
        error_key = str(e)
        return ai_error(error_key)

    except TimeoutError:
        return ai_error('RECOGNIZE_TIMEOUT')

    except Exception as e:
        logger.error(f'Recognition error: {e}', exc_info=True)
        return error(f'识别服务异常: {str(e)}', 500)


@recognize_bp.route('/recognize/delivery', methods=['POST'])
def recognize_for_delivery():
    """
    Recognition for smart bin delivery verification.
    Internal endpoint called by the main backend service when processing API203.

    Request body (JSON):
        {
            "imageUrl": "https://cdn.../capture.jpg",
            "boxCategory": "recyclable"
        }

    Response:
        {
            "code": 200,
            "data": {
                "isCorrect": true,
                "garbageCategory": "塑料瓶",
                "recognizedType": "recyclable",
                "confidence": 0.96,
                "guide": "请清空内容物后投入可回收物桶",
                "correctCategory": "可回收物"
            }
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return error('请求体不能为空', 400)

    image_url = data.get('imageUrl', '').strip()
    box_category = data.get('boxCategory', '').strip()

    if not image_url:
        return error('缺少必填参数 imageUrl', 400)
    if not box_category:
        return error('缺少必填参数 boxCategory', 400)

    valid_categories = ('recyclable', 'kitchen', 'hazardous', 'other')
    if box_category not in valid_categories:
        return error(f'boxCategory 必须为: {", ".join(valid_categories)}', 400)

    logger.info(f'Delivery recognition: box={box_category}, image={image_url[:80]}...')

    try:
        service = get_recognition_service()
        result = service.recognize_for_delivery(image_url, box_category)

        # Generate voice text
        guide_svc = get_guide_service()
        voice_text = guide_svc.get_voice_text(
            is_correct=result['isCorrect'],
            point_change=0,  # Point value determined by backend
            garbage_category=result.get('garbageCategory', ''),
            correct_category=result.get('correctCategory', ''),
        )
        result['voiceText'] = voice_text

        return success(result, '投放识别完成')

    except ValueError as e:
        error_key = str(e)
        return ai_error(error_key)

    except Exception as e:
        logger.error(f'Delivery recognition error: {e}', exc_info=True)
        return error(f'投放识别异常: {str(e)}', 500)


@recognize_bp.route('/recognize/health', methods=['GET'])
def recognize_health():
    """Health check for recognition service."""
    try:
        from 代码包.ai_service.models.model_loader import get_model_loader
        loader = get_model_loader()
        health = loader.health_check()
        return success(health, 'Recognition service healthy')
    except Exception as e:
        return error(f'Recognition service unhealthy: {str(e)}', 500)
