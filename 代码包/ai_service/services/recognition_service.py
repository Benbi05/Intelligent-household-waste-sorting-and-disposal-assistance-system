"""
Recognition Service
Orchestrates the full garbage recognition pipeline:
  Download image → Validate → Preprocess → Inference → Map categories → Generate guides
"""
from typing import Optional
import uuid
from datetime import datetime, timezone, timedelta
from 代码包.ai_service.config import INFERENCE_CONFIG, logger
from 代码包.ai_service.utils.image_utils import (
    download_image,
    preprocess_image_with_scale,
    is_image_blurry,
)
from 代码包.ai_service.models.yolov11_inference import YOLOv11Inference
from 代码包.ai_service.models.category_mapper import get_category_mapper
from 代码包.ai_service.services.guide_service import get_guide_service

TZ_BEIJING = timezone(timedelta(hours=8))


class RecognitionService:
    """
    Complete garbage recognition service.
    Wraps the entire pipeline from image URL to structured recognition result.
    """

    def __init__(self):
        self.inference_engine = YOLOv11Inference()
        self.category_mapper = get_category_mapper()
        self.guide_service = get_guide_service()

        # Wire class names into inference engine
        class_name_map = self.category_mapper.get_class_name_map()
        self.inference_engine.set_class_names(class_name_map)

    def recognize_from_url(self, image_url: str) -> dict:
        """
        Full recognition pipeline from an image URL.

        Steps:
        1. Download image with SSRF protection
        2. Check image quality (blur detection)
        3. Preprocess for model input
        4. Run YOLOv11 inference
        5. Map class IDs to categories
        6. Generate disposal guides
        7. Build response

        Returns:
            Dict with recognizeId, resultList, createTime
            or raises ValueError with appropriate error key
        """
        recognize_id = f'REC{uuid.uuid4().hex[:12].upper()}'

        # 1. Download image
        logger.info(f'[{recognize_id}] Downloading image from: {image_url}')
        image_bytes, error_key = download_image(image_url)
        if error_key:
            raise ValueError(error_key)

        # 2. Check blur
        try:
            if is_image_blurry(image_bytes):
                logger.warning(f'[{recognize_id}] Image is blurry')
                raise ValueError('IMAGE_BLURRY')
        except ImportError:
            # cv2 not available, skip blur check
            pass

        # 3. Preprocess
        logger.info(f'[{recognize_id}] Preprocessing image ({len(image_bytes)} bytes)')
        preprocessed, (scale_x, scale_y), (orig_w, orig_h) = \
            preprocess_image_with_scale(image_bytes)

        # 4. Run inference
        logger.info(f'[{recognize_id}] Running YOLOv11 inference')
        detections = self.inference_engine.detect(preprocessed)

        # 5. Map to categories and build results
        result_list = []
        for det in detections:
            cat_info = self.category_mapper.get_category(det['class_id'])
            guide = self.guide_service.get_guide(
                det['class_id'], cat_info['parentType']
            )

            # Convert bbox from model coordinates to normalized (0-1)
            bbox = det['bbox']  # [x1, y1, x2, y2] already normalized

            result_list.append({
                'categoryId': cat_info['categoryId'],
                'categoryName': cat_info['categoryName'],
                'parentType': cat_info['parentType'],
                'parentTypeName': cat_info['parentTypeName'],
                'confidence': det['confidence'],
                'guide': guide,
                'boxRegion': {
                    'x': round(bbox[0], 4),
                    'y': round(bbox[1], 4),
                    'width': round(bbox[2] - bbox[0], 4),
                    'height': round(bbox[3] - bbox[1], 4),
                },
            })

        # If no detections, check if image was blurry
        if not result_list:
            raise ValueError('IMAGE_BLURRY')

        logger.info(
            f'[{recognize_id}] Recognition complete: '
            f'{len(result_list)} objects detected'
        )

        return {
            'recognizeId': recognize_id,
            'resultList': result_list,
            'createTime': datetime.now(TZ_BEIJING).isoformat(),
        }

    def recognize_for_delivery(self, image_url: str,
                                box_category: str) -> dict:
        """
        Recognition for smart bin delivery verification.
        Compares recognized type with bin type to determine correctness.

        Args:
            image_url: URL of the capture image
            box_category: The bin's category type (recyclable/kitchen/hazardous/other)

        Returns:
            Dict with isCorrect, pointChange, garbageCategory, voiceText, correctCategory
        """
        try:
            result = self.recognize_from_url(image_url)
        except ValueError as e:
            error_key = str(e)
            if error_key == 'IMAGE_BLURRY':
                return {
                    'isCorrect': False,
                    'garbageCategory': '无法识别',
                    'recognizedType': 'unknown',
                }
            raise

        # Get the highest-confidence detection
        if not result['resultList']:
            return {
                'isCorrect': False,
                'garbageCategory': '未检测到物品',
                'recognizedType': 'unknown',
            }

        top_detection = result['resultList'][0]
        recognized_type = top_detection['parentType']

        # Compare with bin type
        is_correct = (recognized_type == box_category)

        return {
            'isCorrect': is_correct,
            'garbageCategory': top_detection['categoryName'],
            'recognizedType': recognized_type,
            'confidence': top_detection['confidence'],
            'guide': top_detection['guide'],
            'correctCategory': box_category,
            'fullResult': result,  # include all detections
        }


# Singleton
_recognition_service: Optional[RecognitionService] = None


def get_recognition_service() -> RecognitionService:
    global _recognition_service
    if _recognition_service is None:
        _recognition_service = RecognitionService()
    return _recognition_service
