"""
AI Service Configuration
Manages model paths, ONNX Runtime settings, LLM config, and service parameters.
"""
import os
import logging

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_STORE_DIR = os.path.join(BASE_DIR, 'models_store')
PROMPTS_DIR = os.path.join(BASE_DIR, 'prompts')

# ============================================================
# ONNX Runtime / Model Inference Config
# ============================================================
ONNX_CONFIG = {
    'execution_provider': 'CPUExecutionProvider',  # 'CUDAExecutionProvider' for GPU
    'inter_op_num_threads': 4,
    'intra_op_num_threads': 4,
    'graph_optimization_level': 'enable_all',  # enable_all, enable_basic, enable_extended, disable_all
    'enable_profiling': False,
}

# Model input dimensions (YOLOv11 standard)
MODEL_INPUT_SIZE = (640, 640)  # width x height
MODEL_INPUT_CHANNELS = 3

# Inference parameters
INFERENCE_CONFIG = {
    'confidence_threshold': 0.25,     # minimum confidence for detection
    'nms_threshold': 0.45,            # NMS IoU threshold
    'max_detections': 20,             # max objects per image
    'inference_timeout': 5,           # seconds
}

# ============================================================
# Model Registry Config
# ============================================================
# Currently active model version
ACTIVE_MODEL_VERSION = 'v1.5'

# Canary (grayscale) deployment config
CANARY_CONFIG = {
    'enabled': False,
    'canary_version': None,
    'canary_percent': 0,  # 5-50, percentage of traffic to canary model
}

# ============================================================
# Image Processing Config
# ============================================================
IMAGE_CONFIG = {
    'allowed_mime_types': ['image/jpeg', 'image/png', 'image/webp'],
    'max_file_size': 10 * 1024 * 1024,  # 10 MB
    'download_timeout': 10,              # seconds
    # SSRF Protection: allowed image URL domains
    'allowed_image_domains': [
        'cdn.garbage-system.com',
        'img.garbage-system.com',
    ],
    # Internal IP ranges to block
    'blocked_ip_ranges': [
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
        '127.0.0.0/8',
        '169.254.0.0/16',
        '0.0.0.0/8',
    ],
}

# ============================================================
# LLM Analysis Config
# ============================================================
LLM_CONFIG = {
    'provider': 'anthropic',  # or 'openai' / 'local'
    'model': 'claude-sonnet-4-6',
    'max_tokens': 4096,
    'temperature': 0.3,
    'api_key': os.environ.get('ANTHROPIC_API_KEY', ''),
    'base_url': os.environ.get('ANTHROPIC_BASE_URL', ''),
}

# Async task config
ASYNC_CONFIG = {
    'max_workers': 4,
    'task_timeout': 300,  # seconds for analysis report generation
    'training_timeout': 7200,  # seconds for model training
    'callback_retry_count': 3,
    'callback_retry_delays': [10, 60, 300],  # seconds
}

# ============================================================
# Category Mapping (50+ categories -> 4 parent types)
# ============================================================
# Parent type enum
PARENT_TYPES = {
    1: 'recyclable',    # 可回收物
    2: 'kitchen',        # 厨余垃圾
    3: 'hazardous',      # 有害垃圾
    4: 'other',          # 其他垃圾
}

PARENT_TYPE_NAMES = {
    'recyclable': '可回收物',
    'kitchen': '厨余垃圾',
    'hazardous': '有害垃圾',
    'other': '其他垃圾',
}

# Detailed category mapping (category_id -> {name, parent_type})
# This should be loaded from database in production; here as fallback
CATEGORY_MAP = {
    # Recyclable (可回收物) 1xxx
    101: {'name': '塑料饮料瓶', 'parent_type': 'recyclable'},
    102: {'name': '塑料包装盒', 'parent_type': 'recyclable'},
    103: {'name': '塑料袋', 'parent_type': 'recyclable'},
    104: {'name': '玻璃瓶', 'parent_type': 'recyclable'},
    105: {'name': '易拉罐', 'parent_type': 'recyclable'},
    106: {'name': '废纸', 'parent_type': 'recyclable'},
    107: {'name': '纸箱', 'parent_type': 'recyclable'},
    108: {'name': '旧衣物', 'parent_type': 'recyclable'},
    109: {'name': '金属制品', 'parent_type': 'recyclable'},
    110: {'name': '电子产品', 'parent_type': 'recyclable'},
    111: {'name': '旧书本', 'parent_type': 'recyclable'},
    112: {'name': '泡沫塑料', 'parent_type': 'recyclable'},
    # Kitchen (厨余垃圾) 2xxx
    201: {'name': '剩饭菜', 'parent_type': 'kitchen'},
    202: {'name': '果皮果核', 'parent_type': 'kitchen'},
    203: {'name': '菜叶菜根', 'parent_type': 'kitchen'},
    204: {'name': '蛋壳', 'parent_type': 'kitchen'},
    205: {'name': '骨头', 'parent_type': 'kitchen'},
    206: {'name': '茶叶渣', 'parent_type': 'kitchen'},
    207: {'name': '咖啡渣', 'parent_type': 'kitchen'},
    208: {'name': '过期食品', 'parent_type': 'kitchen'},
    # Hazardous (有害垃圾) 3xxx
    301: {'name': '废电池', 'parent_type': 'hazardous'},
    302: {'name': '废灯管', 'parent_type': 'hazardous'},
    303: {'name': '废药品', 'parent_type': 'hazardous'},
    304: {'name': '废油漆', 'parent_type': 'hazardous'},
    305: {'name': '废杀虫剂', 'parent_type': 'hazardous'},
    306: {'name': '废化妆品', 'parent_type': 'hazardous'},
    307: {'name': '废胶片', 'parent_type': 'hazardous'},
    308: {'name': '水银温度计', 'parent_type': 'hazardous'},
    # Other (其他垃圾) 4xxx
    401: {'name': '餐巾纸', 'parent_type': 'other'},
    402: {'name': '卫生纸', 'parent_type': 'other'},
    403: {'name': '尿不湿', 'parent_type': 'other'},
    404: {'name': '烟蒂', 'parent_type': 'other'},
    405: {'name': '陶瓷碎片', 'parent_type': 'other'},
    406: {'name': '一次性餐具', 'parent_type': 'other'},
    407: {'name': '灰土', 'parent_type': 'other'},
    408: {'name': '毛发', 'parent_type': 'other'},
    409: {'name': '宠物粪便', 'parent_type': 'other'},
    410: {'name': '污染纸张', 'parent_type': 'other'},
}

# ============================================================
# Disposal Guide Templates
# ============================================================
DISPOSAL_GUIDES = {
    'recyclable': '请投入可回收物桶',
    'kitchen': '请投入厨余垃圾桶',
    'hazardous': '请投入有害垃圾桶',
    'other': '请投入其他垃圾桶',
}

# Category-specific guides (override generic ones)
CATEGORY_SPECIFIC_GUIDES = {
    101: '请清空内容物后投入可回收物桶',
    102: '请清洗干净后投入可回收物桶',
    301: '请轻拿轻放，投入有害垃圾桶',
    302: '请使用原包装包裹后投入有害垃圾桶',
}

# ============================================================
# Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger('ai_service')
