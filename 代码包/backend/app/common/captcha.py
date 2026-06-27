"""图形验证码"""
import io
import base64
import random
import string
from ..extensions import redis_client

try:
    from PIL import Image, ImageDraw, ImageFont
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

CAPTCHA_EXPIRE = 300


def generate() -> dict:
    """生成验证码，返回 {captchaToken, captchaImage}"""
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    token = f'captcha:{random.getrandbits(64):x}'

    if _HAS_PIL:
        img = Image.new('RGB', (120, 40), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        for i, c in enumerate(chars):
            color = (random.randint(0, 128), random.randint(0, 128), random.randint(0, 128))
            draw.text((10 + i * 28, 5), c, fill=color)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
    else:
        b64 = ''

    redis_client.setex(f'captcha:{token}', CAPTCHA_EXPIRE, chars.lower())
    return {'captchaToken': token, 'captchaImage': f'data:image/png;base64,{b64}'}


def verify(token: str, code: str) -> bool:
    """校验验证码，成功则删除"""
    key = f'captcha:{token}'
    stored = redis_client.get(key)
    if stored:
        redis_client.delete(key)
        return stored == code.lower()
    return False