"""后处理：品类映射 + 投放指引生成"""
import os
from .inference import CLASS_NAMES

# 父类映射：根据 classes.txt 中的顺序（前12=可回收, 中8=厨余, 中8=有害, 后10=其他）
_PARENT_MAP = {}
for i in range(38):
    if i < 12:
        _PARENT_MAP[i] = ('recyclable', '可回收物')
    elif i < 20:
        _PARENT_MAP[i] = ('kitchen', '厨余垃圾')
    elif i < 28:
        _PARENT_MAP[i] = ('hazardous', '有害垃圾')
    else:
        _PARENT_MAP[i] = ('other', '其他垃圾')

# 投放指引
_GUIDES = {
    'recyclable': '请投入可回收物桶',
    'kitchen': '请投入厨余垃圾桶',
    'hazardous': '请投入有害垃圾桶',
    'other': '请投入其他垃圾桶',
}
_SPECIFIC = {
    '塑料饮料瓶': '请清空内容物后投入可回收物桶',
    '塑料包装盒': '请清洗干净后投入可回收物桶',
    '废电池': '请轻拿轻放，投入有害垃圾桶',
    '废灯管': '请用原包装包裹后投入有害垃圾桶',
    '废药品': '请保留原包装投入有害垃圾桶',
    '陶瓷碎片': '请用纸包好后投入其他垃圾桶',
}


def get_parent_type(idx: int) -> tuple:
    return _PARENT_MAP.get(idx, ('other', '其他垃圾'))


def get_guide(class_name: str, parent_type: str) -> str:
    if class_name in _SPECIFIC:
        return _SPECIFIC[class_name]
    return _GUIDES.get(parent_type, '请根据分类投入对应垃圾桶')


def process_detections(detections: list) -> list:
    """将推理结果转换为前端需要的格式"""
    results = []
    for d in detections:
        pt_key, pt_name = get_parent_type(d['class_id'])
        guide = get_guide(d['class_name'], pt_key)
        results.append({
            'categoryName': d['class_name'],
            'parentType': pt_key,
            'parentTypeName': pt_name,
            'confidence': d['confidence'],
            'guide': guide,
            'boxRegion': d['boxRegion'],
        })
    return results


def get_category_id(class_name: str) -> int:
    """根据品类名映射到数据库中的 category_id（用于积分结算）"""
    if class_name in CLASS_NAMES:
        idx = CLASS_NAMES.index(class_name)
        # 品类ID编码: 1xx=可回收, 2xx=厨余, 3xx=有害, 4xx=其他
        if idx < 12:
            return 101 + idx
        elif idx < 20:
            return 201 + (idx - 12)
        elif idx < 28:
            return 301 + (idx - 20)
        else:
            return 401 + (idx - 28)
    return 0
