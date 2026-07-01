"""识别服务 Flask 应用"""
import uuid
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from .preprocess import download_image, preprocess
from .inference import get_engine
from .postprocess import process_detections, get_parent_type, get_guide

TZ = timezone(timedelta(hours=8))
app = Flask(__name__)


def _now():
    return datetime.now(TZ).isoformat()


def _ok(data=None, msg='操作成功'):
    return jsonify({'code': 200, 'message': msg, 'data': data, 'timestamp': _now()})


def _err(msg, code=400):
    return jsonify({'code': code, 'message': msg, 'data': None, 'timestamp': _now()}), 400


@app.route('/health', methods=['GET'])
def health():
    engine = get_engine()
    return _ok({
        'status': 'healthy',
        'activeModel': engine.active_version,
        'classCount': len(__import__('recognition.inference', fromlist=['CLASS_NAMES']).CLASS_NAMES)
    })


@app.route('/recognize', methods=['POST'])
def recognize():
    """垃圾图片识别

    Request:  {"imageUrl": "https://cdn.garbage-system.com/images/xxx.jpg"}
    Response: {"code":200, "data":{"recognizeId":"...", "resultList":[...], "createTime":"..."}}
    """
    body = request.get_json(silent=True) or {}
    image_url = (body.get('imageUrl') or '').strip()
    if not image_url:
        return _err('缺少 imageUrl 参数')

    # 1. 下载图片
    img_bytes, err = download_image(image_url)
    if err:
        code_map = {
            '域名不在白名单': 3103, '内网地址已拦截': 3104,
            '下载超时': 3105, '下载失败': 3105, '超过10MB上限': 3107,
        }
        for key, code in code_map.items():
            if key in err:
                return _err(err, code)
        return _err(err, 3105)

    # 2. 预处理 + 推理
    try:
        preprocessed, scale_xy, orig_wh = preprocess(img_bytes)
        engine = get_engine()
        detections, elapsed_ms = engine.detect(preprocessed)
    except Exception as e:
        return _err(f'识别失败: {e}', 3102)

    # 3. 后处理
    result_list = process_detections(detections)

    if not result_list:
        return _err('图片模糊或无有效垃圾', 3101)

    return _ok({
        'recognizeId': 'REC' + uuid.uuid4().hex[:12].upper(),
        'resultList': result_list,
        'inferenceTimeMs': round(elapsed_ms, 1),
        'createTime': _now(),
    }, '识别成功')


@app.route('/recognize/delivery', methods=['POST'])
def recognize_delivery():
    """投放校准识别（内部调用）

    Request:  {"imageUrl":"...", "boxCategory":"recyclable"}
    Response: {"code":200, "data":{"isCorrect":bool, "garbageCategory":"...", ...}}
    """
    body = request.get_json(silent=True) or {}
    image_url = (body.get('imageUrl') or '').strip()
    box_cat = (body.get('boxCategory') or '').strip()
    if not image_url or not box_cat:
        return _err('缺少 imageUrl 或 boxCategory')

    valid = {'recyclable', 'kitchen', 'hazardous', 'other'}
    if box_cat not in valid:
        return _err(f'boxCategory 必须为: {", ".join(valid)}')

    img_bytes, err = download_image(image_url)
    if err:
        return _err(err, 3103)

    try:
        preprocessed, _, _ = preprocess(img_bytes)
        engine = get_engine()
        detections, _ = engine.detect(preprocessed)
    except Exception as e:
        return _err(f'识别失败: {e}', 3102)

    if not detections:
        return _ok({
            'isCorrect': False,
            'garbageCategory': '无法识别',
            'recognizedType': 'unknown',
            'confidence': 0,
            'voiceText': '未能识别，请重新投放',
        })

    top = detections[0]
    pt_key, pt_name = get_parent_type(top['class_id'])
    is_correct = (pt_key == box_cat)
    guide = get_guide(top['class_name'], pt_key)
    voice = f'分类正确，+积分已到账' if is_correct else f'分类错误，{top["class_name"]}应投入{box_cat}桶'

    return _ok({
        'isCorrect': is_correct,
        'garbageCategory': top['class_name'],
        'recognizedType': pt_key,
        'recognizedTypeName': pt_name,
        'confidence': top['confidence'],
        'guide': guide,
        'voiceText': voice,
        'correctCategory': box_cat,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
