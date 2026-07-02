"""图像预处理：下载、校验、归一化"""
import io, os, ipaddress, socket, numpy as np
from urllib.parse import urlparse
from PIL import Image
import requests, yaml

_conf_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(_conf_path, 'r', encoding='utf-8') as f:
    _cfg = yaml.safe_load(f)
_IMG = _cfg['image']; _SEC = _cfg['security']; _MODEL = _cfg['model']


def _is_internal_ip(hostname: str) -> bool:
    blocked = _SEC['blocked_ip_ranges']
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        except (socket.gaierror, ValueError):
            return True
    return any(ip in ipaddress.ip_network(c) for c in blocked)


def validate_image_url(url: str) -> tuple:
    try:
        p = urlparse(url)
    except Exception:
        return False, 'URL格式无效'
    if p.scheme not in ('http', 'https'):
        return False, '仅支持HTTP/HTTPS'
    if not p.hostname:
        return False, '缺少主机名'
    if not any(p.hostname == d or p.hostname.endswith('.' + d) for d in _SEC['allowed_domains']):
        return False, '域名不在白名单'
    if _is_internal_ip(p.hostname):
        return False, '内网地址已拦截'
    return True, ''


def download_image(url: str) -> tuple:
    ok, err = validate_image_url(url)
    if not ok:
        return b'', err
    try:
        r = requests.get(url, timeout=_IMG['download_timeout'], stream=True,
                        headers={'User-Agent': 'GarbageSystem-AI/1.0'})
        r.raise_for_status()
        ct = r.headers.get('Content-Type', '')
        mime = ct.split(';')[0].strip()
        if not ct.startswith('image/') or mime not in _IMG['allowed_mime_types']:
            return b'', f'不支持的格式: {mime}'
        cl = r.headers.get('Content-Length')
        if cl and int(cl) > _IMG['max_file_size']:
            return b'', '超过10MB上限'
        chunks, total = [], 0
        for c in r.iter_content(8192):
            total += len(c)
            if total > _IMG['max_file_size']:
                return b'', '超过10MB上限'
            chunks.append(c)
        return b''.join(chunks), ''
    except requests.Timeout:
        return b'', '下载超时'
    except requests.RequestException as e:
        return b'', f'下载失败: {e}'


def preprocess(image_bytes: bytes):
    tw, th = _MODEL['input_width'], _MODEL['input_height']
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    ow, oh = img.size
    scale = min(tw / ow, th / oh)
    nw, nh = int(ow * scale), int(oh * scale)
    img = img.resize((nw, nh), Image.BILINEAR)
    canvas = Image.new('RGB', (tw, th), (114, 114, 114))
    canvas.paste(img, ((tw - nw) // 2, (th - nh) // 2))
    arr = np.array(canvas, dtype=np.float32) / 255.0
    arr = arr.transpose(2, 0, 1)
    arr = np.expand_dims(arr, axis=0)
    return arr.astype(np.float32), (ow / tw, oh / th), (ow, oh)
