"""
YOLOv11 ONNX Inference Pipeline
Implements the full inference flow:
  preprocess -> ONNX Runtime inference -> postprocess (NMS + box decoding)
"""
import numpy as np
import time
from 代码包.ai_service.config import INFERENCE_CONFIG, MODEL_INPUT_SIZE, logger
from 代码包.ai_service.models.model_loader import get_model_loader


class YOLOv11Inference:
    """
    YOLOv11 object detection inference using ONNX Runtime.
    Handles pre-processing, inference, and post-processing.
    """

    def __init__(self, confidence_threshold: float = None,
                 nms_threshold: float = None):
        self.confidence_threshold = confidence_threshold or INFERENCE_CONFIG['confidence_threshold']
        self.nms_threshold = nms_threshold or INFERENCE_CONFIG['nms_threshold']
        self.max_detections = INFERENCE_CONFIG['max_detections']
        self.model_loader = get_model_loader()

        # Class names — loaded from model metadata or config
        self._class_names: dict[int, str] = {}

    def set_class_names(self, class_names: dict[int, str]):
        """Set the class ID -> class name mapping."""
        self._class_names = class_names

    def detect(self, preprocessed_image: np.ndarray) -> list[dict]:
        """
        Run detection on a preprocessed image.

        Args:
            preprocessed_image: shape (1, 3, 640, 640), float32

        Returns:
            List of detection dicts:
            [{
                'class_id': int,
                'class_name': str,
                'confidence': float,
                'bbox': [x1, y1, x2, y2],  # normalized 0-1
            }, ...]
        """
        start_time = time.time()

        # 1. Run ONNX inference
        outputs = self.model_loader.run_inference(preprocessed_image)

        # 2. Post-process: decode boxes, apply NMS
        detections = self._postprocess(outputs)

        elapsed = (time.time() - start_time) * 1000
        logger.info(
            f'Inference completed in {elapsed:.1f}ms, '
            f'detected {len(detections)} objects'
        )
        return detections

    def detect_batch(self, preprocessed_images: np.ndarray) -> list[list[dict]]:
        """
        Run detection on a batch of preprocessed images.

        Args:
            preprocessed_images: shape (B, 3, 640, 640), float32

        Returns:
            List of detection lists, one per image
        """
        outputs = self.model_loader.run_inference(preprocessed_images)
        # Process each image's outputs
        batch_results = []
        # Assuming outputs contain all batch results
        # Actual implementation depends on model output format
        for i in range(preprocessed_images.shape[0]):
            img_outputs = [o[i:i+1] for o in outputs]
            detections = self._postprocess(img_outputs)
            batch_results.append(detections)
        return batch_results

    def _postprocess(self, outputs: list[np.ndarray]) -> list[dict]:
        """
        Post-process model outputs into structured detections.

        YOLOv11 ONNX output format (varies by export config):
        - Single output: [batch, num_boxes, 4 + 1 + num_classes]
          where columns are [x_center, y_center, width, height, objectness, class_probs...]
        - Or separate outputs for boxes and scores

        This implementation handles the single-output format.
        """
        if not outputs:
            return []

        # Assume first output is the detection tensor
        detections_raw = outputs[0]

        # Remove batch dimension if present
        if len(detections_raw.shape) == 3:
            detections_raw = detections_raw[0]  # (num_boxes, 4 + 1 + num_classes)

        if detections_raw.shape[0] == 0:
            return []

        # Split into boxes, objectness, class scores
        # YOLO format: [cx, cy, w, h, obj_conf, class_0, class_1, ...]
        boxes_raw = detections_raw[:, :4]       # cx, cy, w, h (normalized 0-1)
        obj_conf = detections_raw[:, 4:5]       # objectness
        class_scores = detections_raw[:, 5:]     # class probabilities

        # Combined confidence = objectness * class_prob
        class_ids = np.argmax(class_scores, axis=1)
        max_class_scores = np.max(class_scores, axis=1)
        confidences = obj_conf.flatten() * max_class_scores

        # Filter by confidence threshold
        mask = confidences >= self.confidence_threshold
        if not np.any(mask):
            return []

        boxes_raw = boxes_raw[mask]
        confidences = confidences[mask]
        class_ids = class_ids[mask]

        # Convert cxcywh -> x1y1x2y2 (normalized)
        boxes_xyxy = self._cxcywh_to_xyxy(boxes_raw)

        # Apply NMS
        keep_indices = self._nms(boxes_xyxy, confidences)
        if len(keep_indices) == 0:
            return []

        # Build result list
        detections = []
        for idx in keep_indices[:self.max_detections]:
            cls_id = int(class_ids[idx])
            detections.append({
                'class_id': cls_id,
                'class_name': self._class_names.get(cls_id, f'class_{cls_id}'),
                'confidence': round(float(confidences[idx]), 4),
                'bbox': [round(float(x), 4) for x in boxes_xyxy[idx]],
            })

        return detections

    def _cxcywh_to_xyxy(self, boxes: np.ndarray) -> np.ndarray:
        """
        Convert boxes from [cx, cy, w, h] to [x1, y1, x2, y2].
        All coordinates are normalized (0-1).
        """
        cx, cy, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2
        return np.stack([x1, y1, x2, y2], axis=1)

    def _nms(self, boxes: np.ndarray, scores: np.ndarray) -> np.ndarray:
        """
        Non-Maximum Suppression.
        Returns indices of boxes to keep.
        """
        if len(boxes) == 0:
            return np.array([], dtype=int)

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]  # descending by score

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            if order.size == 1:
                break

            # Compute IoU of the top box with the rest
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h
            iou = inter / (areas[i] + areas[order[1:]] - inter)

            # Keep boxes with IoU below threshold
            remain_indices = np.where(iou <= self.nms_threshold)[0]
            order = order[remain_indices + 1]

        return np.array(keep, dtype=int)
