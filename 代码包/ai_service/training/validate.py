"""数据集校验：验证YOLO格式数据集"""
import os, zipfile


def validate_dataset(dataset_path: str) -> tuple:
    """验证数据集是否符合YOLO训练格式

    要求:
    - ZIP文件结构: images/ + labels/ + classes.txt 或 data.yaml
    - labels/*.txt: 每行5个数字 (class_id cx cy w h)

    Returns: (is_valid: bool, message: str)
    """
    if not os.path.exists(dataset_path):
        return False, f'文件不存在: {dataset_path}'

    if not dataset_path.endswith('.zip'):
        return False, '仅支持ZIP格式数据集'

    try:
        with zipfile.ZipFile(dataset_path, 'r') as zf:
            files = zf.namelist()
            has_images = any('images/' in f.lower() for f in files)
            has_labels = any('labels/' in f.lower() for f in files)
            has_classes = any(f.endswith('classes.txt') for f in files)
            has_yaml = any(f.endswith('data.yaml') for f in files)

            if not has_images:
                return False, '缺少 images/ 目录'
            if not has_labels:
                return False, '缺少 labels/ 目录'
            if not has_classes and not has_yaml:
                return False, '缺少 classes.txt 或 data.yaml'

            # 校验标注格式
            label_files = [f for f in files if 'labels/' in f.lower() and f.endswith('.txt')]
            if not label_files:
                return False, 'labels/ 目录为空'

            for lf in label_files[:10]:
                content = zf.read(lf).decode('utf-8').strip()
                if not content:
                    continue
                for line in content.split('\n')[:5]:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        return False, f'标注格式错误 ({lf}): 应为5列，实际{len(parts)}列'
                    try:
                        vals = [float(p) for p in parts]
                        if not (0 <= vals[1] <= 1 and 0 <= vals[2] <= 1 and 0 < vals[3] <= 1 and 0 < vals[4] <= 1):
                            return False, f'坐标越界 ({lf}): 坐标应在0-1之间'
                    except ValueError:
                        return False, f'标注非数字 ({lf}): {line[:50]}'

        return True, f'校验通过: {len(label_files)} 个标注文件'
    except zipfile.BadZipFile:
        return False, '不是有效的ZIP文件'
    except Exception as e:
        return False, f'校验异常: {e}'


def count_classes(dataset_path: str) -> dict:
    """统计数据集中各类别的样本数"""
    counts = {}
    try:
        with zipfile.ZipFile(dataset_path, 'r') as zf:
            for name in zf.namelist():
                if 'labels/' in name.lower() and name.endswith('.txt'):
                    content = zf.read(name).decode('utf-8').strip()
                    for line in content.split('\n'):
                        parts = line.strip().split()
                        if len(parts) >= 1:
                            cls = parts[0]
                            counts[cls] = counts.get(cls, 0) + 1
    except Exception:
        pass
    return counts
