"""YOLOv11 ONNX Runtime 推理引擎"""
import os
import time
import threading
import numpy as np
import onnxruntime as ort
import yaml

_conf_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(_conf_path, 'r', encoding='utf-8') as f:
    _cfg = yaml.safe_load(f)

_MODEL_CFG = _cfg['model']
_ONNX_CFG = _cfg['onnx']

_CLASSES_PATH = os.path.join(os.path.dirname(__file__), 'classes.txt')
with open(_CLASSES_PATH, 'r', encoding='utf-8') as f:
    CLASS_NAMES = [line.strip() for line in f if line.strip()]

_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')


class InferenceEngine:
    """YOLOv11 ONNX 推理引擎（支持热切换和灰度发布）"""

    def __init__(self):
        self._sessions: dict = {}
        self._lock = threading.RLock()
        self._active_version = 'v1.0'
        self._canary_version = None
        self._canary_percent = 0
        self._init_session()

    def _init_session(self):
        opts = ort.SessionOptions()
        opt_level = getattr(ort.GraphOptimizationLevel,
                           f'ORT_{_ONNX_CFG["graph_optimization"].upper()}',
                           ort.GraphOptimizationLevel.ORT_ENABLE_ALL)
        opts.graph_optimization_level = opt_level
        opts.inter_op_num_threads = _ONNX_CFG['inter_op_threads']
        opts.intra_op_num_threads = _ONNX_CFG['intra_op_threads']
        self._session_opts = opts
        self._providers = [_ONNX_CFG['execution_provider']]
        if 'CPUExecutionProvider' not in self._providers:
            self._providers.append('CPUExecutionProvider')

    def _model_path(self, version: str) -> str:
        return os.path.join(_MODEL_DIR, version, 'model.onnx')

    def load_model(self, version: str):
        with self._lock:
            if version in self._sessions:
                return self._sessions[version]
            path = self._model_path(version)
            if not os.path.exists(path):
                raise FileNotFoundError(f'模型文件不存在: {path}')
            sess = ort.InferenceSession(path, sess_options=self._session_opts,
                                       providers=self._providers)
            self._sessions[version] = sess
            return sess

    def get_session(self):
        """获取当前激活的推理会话（支持灰度路由）"""
        if self._canary_version and self._canary_percent > 0:
            import random
            if random.random() * 100 < self._canary_percent:
                return self.load_model(self._canary_version)
        return self.load_model(self._active_version)

    def switch_model(self, version: str, canary_percent: int = 0):
        """切换模型版本（full/canary）"""
        self.load_model(version)  # 预加载
        if canary_percent > 0:
            self._canary_version = version
            self._canary_percent = canary_percent
        else:
            self._active_version = version
            self._canary_version = None
            self._canary_percent = 0

    @property
    def active_version(self):
        return self._active_version

    def detect(self, preprocessed: np.ndarray) -> list:
        """执行推理并后处理"""
        start = time.time()
        session = self.get_session()
        in_name = session.get_inputs()[0].name
        outputs = session.run(None, {in_name: preprocessed})
        detections = self._postprocess(outputs[0])
        elapsed = (time.time() - start) * 1000
        return detections, elapsed

    def _postprocess(self, raw: np.ndarray) -> list:
        """后处理：NMS + box解码"""
        if len(raw.shape) == 3:
            raw = raw[0]
        if raw.shape[0] == 0:
            return []

        boxes = raw[:, :4]      # cx, cy, w, h (归一化)
        obj_conf = raw[:, 4:5]
        class_scores = raw[:, 5:]

        class_ids = np.argmax(class_scores, axis=1)
        scores = obj_conf.flatten() * np.max(class_scores, axis=1)

        mask = scores >= _MODEL_CFG['confidence_threshold']
        if not np.any(mask):
            return []

        boxes, scores, class_ids = boxes[mask], scores[mask], class_ids[mask]
        xyxy = self._cxcywh_to_xyxy(boxes)
        keep = self._nms(xyxy, scores)

        results = []
        for idx in keep[:_MODEL_CFG['max_detections']]:
            cls_id = int(class_ids[idx])
            bbox = xyxy[idx]
            results.append({
                'class_id': cls_id,
                'class_name': CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f'class_{cls_id}',
                'confidence': round(float(scores[idx]), 4),
                'boxRegion': {
                    'x': round(float(bbox[0]), 4),
                    'y': round(float(bbox[1]), 4),
                    'width': round(float(bbox[2] - bbox[0]), 4),
                    'height': round(float(bbox[3] - bbox[1]), 4),
                },
            })
        return results

    @staticmethod
    def _cxcywh_to_xyxy(boxes: np.ndarray) -> np.ndarray:
        cx, cy, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        return np.stack([cx - w/2, cy - h/2, cx + w/2, cy + h/2], axis=1)

    def _nms(self, boxes: np.ndarray, scores: np.ndarray) -> np.ndarray:
        if len(boxes) == 0:
            return np.array([], dtype=int)
        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]
        keep = []
        threshold = _MODEL_CFG['nms_threshold']
        while order.size > 0:
            i = order[0]
            keep.append(i)
            if order.size == 1:
                break
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            iou = (w * h) / (areas[i] + areas[order[1:]] - w * h)
            remain = np.where(iou <= threshold)[0]
            order = order[remain + 1]
        return np.array(keep, dtype=int)


# 全局单例
_engine: InferenceEngine = None
_lock = threading.Lock()


def get_engine() -> InferenceEngine:
    global _engine
    if _engine is None:
        with _lock:
            if _engine is None:
                _engine = InferenceEngine()
    return _engine
