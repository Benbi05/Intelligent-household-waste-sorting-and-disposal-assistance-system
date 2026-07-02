"""PyTorch → ONNX 模型导出

Usage:
  python export_onnx.py --weights best.pt --output model.onnx --img-size 640
"""
import argparse


def export_to_onnx(weights_path: str, output_path: str,
                   img_size: int = 640, opset: int = 12,
                   simplify: bool = True) -> str:
    """将YOLOv11 PyTorch模型导出为ONNX格式

    Args:
        weights_path: .pt 权重文件路径
        output_path: 输出 .onnx 路径
        img_size: 输入尺寸
        opset: ONNX opset版本
        simplify: 是否使用onnx-simplifier简化模型

    Returns: 输出文件路径
    """
    try:
        from ultralytics import YOLO
        model = YOLO(weights_path)
        model.export(format='onnx', imgsz=img_size, opset=opset, simplify=simplify)
        import shutil
        # ultralytics 默认输出在 weights 同目录
        default_out = weights_path.replace('.pt', '.onnx')
        if default_out != output_path:
            shutil.move(default_out, output_path)
        return output_path
    except ImportError:
        raise RuntimeError('请安装 ultralytics: pip install ultralytics')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export YOLOv11 to ONNX')
    parser.add_argument('--weights', required=True, help='PyTorch weights path')
    parser.add_argument('--output', default='model.onnx', help='Output ONNX path')
    parser.add_argument('--img-size', type=int, default=640, help='Input size')
    parser.add_argument('--opset', type=int, default=12, help='ONNX opset')
    args = parser.parse_args()
    path = export_to_onnx(args.weights, args.output, args.img_size, args.opset)
    print(f'ONNX model exported to: {path}')
