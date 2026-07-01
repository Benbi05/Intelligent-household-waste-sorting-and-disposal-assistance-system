"""
Image Download & Preprocessing Utilities
- Download image from URL (with SSRF validation)
- Image format validation
- Preprocessing for YOLOv11 ONNX inference
"""
import time
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from 代码包.ai_service.config import IMAGE_CONFIG, MODEL_INPUT_SIZE, logger
from 代码包.ai_service.utils.security import validate_image_url


def download_image(image_url: str) -> tuple[bytes, str]:
    """
    Download image from URL with SSRF protection and validation.

    Returns:
        (image_bytes, error_key_or_empty_string)
    """
    # 1. SSRF validation
    is_valid, error_key = validate_image_url(image_url)
    if not is_valid:
        return b'', error_key

    # 2. Download with timeout and size limits
    try:
        response = requests.get(
            image_url,
            timeout=IMAGE_CONFIG['download_timeout'],
            stream=True,
            headers={'User-Agent': 'GarbageSystem-AI/1.0'},
        )
        response.raise_for_status()
    except requests.Timeout:
        logger.error(f'Image download timeout: {image_url}')
        return b'', 'IMAGE_DOWNLOAD_FAILED'
    except requests.RequestException as e:
        logger.error(f'Image download failed: {image_url}, error: {e}')
        return b'', 'IMAGE_DOWNLOAD_FAILED'

    # 3. Check content type
    content_type = response.headers.get('Content-Type', '')
    if not content_type.startswith('image/'):
        return b'', 'IMAGE_FORMAT_INVALID'

    mime_type = content_type.split(';')[0].strip()
    if mime_type not in IMAGE_CONFIG['allowed_mime_types']:
        return b'', 'IMAGE_FORMAT_INVALID'

    # 4. Check file size
    content_length = response.headers.get('Content-Length')
    if content_length and int(content_length) > IMAGE_CONFIG['max_file_size']:
        return b'', 'IMAGE_SIZE_EXCEEDED'

    # 5. Read content (with size cap)
    chunks = []
    total_size = 0
    for chunk in response.iter_content(chunk_size=8192):
        total_size += len(chunk)
        if total_size > IMAGE_CONFIG['max_file_size']:
            return b'', 'IMAGE_SIZE_EXCEEDED'
        chunks.append(chunk)

    image_bytes = b''.join(chunks)
    logger.info(f'Downloaded image: {len(image_bytes)} bytes from {image_url}')
    return image_bytes, ''


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess image bytes for ONNX YOLOv11 inference.

    Steps:
    1. Decode image from bytes
    2. Convert to RGB
    3. Resize to MODEL_INPUT_SIZE while maintaining aspect ratio (letterbox)
    4. Normalize to [0, 1]
    5. Convert to NCHW format (batch, channels, height, width)

    Returns:
        Preprocessed numpy array with shape (1, 3, H, W), dtype float32
    """
    target_w, target_h = MODEL_INPUT_SIZE

    # 1. Decode
    img = Image.open(BytesIO(image_bytes))

    # 2. Convert to RGB (handle RGBA, grayscale, etc.)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 3. Letterbox resize (maintain aspect ratio, pad with gray)
    img_w, img_h = img.size
    scale = min(target_w / img_w, target_h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    img_resized = img.resize((new_w, new_h), Image.BILINEAR)

    # Create letterbox canvas (gray padding = 114 is YOLO convention)
    canvas = Image.new('RGB', (target_w, target_h), (114, 114, 114))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    canvas.paste(img_resized, (paste_x, paste_y))

    # 4. Convert to numpy array and normalize
    img_array = np.array(canvas, dtype=np.float32) / 255.0

    # 5. HWC -> CHW, add batch dimension
    img_array = img_array.transpose(2, 0, 1)  # (H, W, C) -> (C, H, W)
    img_array = np.expand_dims(img_array, axis=0)  # (C, H, W) -> (1, C, H, W)

    return img_array.astype(np.float32)


def preprocess_image_with_scale(image_bytes: bytes) -> tuple[np.ndarray, tuple[float, float], tuple[int, int]]:
    """
    Preprocess image and return additional scaling info for box coordinate recovery.

    Returns:
        (preprocessed_array, (scale_x, scale_y), (original_w, original_h))
    """
    target_w, target_h = MODEL_INPUT_SIZE

    img = Image.open(BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')

    orig_w, orig_h = img.size
    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    # Scale factors for coordinate transformation
    scale_x = orig_w / target_w
    scale_y = orig_h / target_h

    # Letterbox
    img_resized = img.resize((new_w, new_h), Image.BILINEAR)
    canvas = Image.new('RGB', (target_w, target_h), (114, 114, 114))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    canvas.paste(img_resized, (paste_x, paste_y))

    # Convert
    img_array = np.array(canvas, dtype=np.float32) / 255.0
    img_array = img_array.transpose(2, 0, 1)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array.astype(np.float32), (scale_x, scale_y), (orig_w, orig_h)


def is_image_blurry(image_bytes: bytes, threshold: float = 100.0) -> bool:
    """
    Detect if an image is too blurry for recognition.
    Uses Laplacian variance method.

    Args:
        image_bytes: Raw image bytes
        threshold: Variance threshold below which image is considered blurry

    Returns:
        True if image is blurry
    """
    import cv2
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True
    variance = cv2.Laplacian(img, cv2.CV_64F).var()
    return variance < threshold
