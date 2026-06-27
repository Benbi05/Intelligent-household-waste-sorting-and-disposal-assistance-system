"""短信验证码服务"""
import random
from ..extensions import redis_client

SMS_EXPIRE = 300       # 5分钟
SMS_INTERVAL = 60      # 重发间隔
SMS_DAILY_MAX = 10     # 每日上限


def send(phone: str) -> dict:
    """发送验证码，返回 {ok, error_code, message}"""
    rate_key = f'sms:rate:{phone}'
    daily_key = f'sms:daily:{phone}'

    if redis_client.exists(rate_key):
        ttl = redis_client.ttl(rate_key)
        return {'ok': False, 'error_code': 1001, 'message': f'发送太频繁，请 {ttl} 秒后再试'}

    daily = int(redis_client.get(daily_key) or 0)
    if daily >= SMS_DAILY_MAX:
        return {'ok': False, 'error_code': 1002, 'message': '今日发送次数已达上限'}

    code = str(random.randint(1000, 9999))
    redis_client.setex(f'sms:code:{phone}', SMS_EXPIRE, code)
    redis_client.setex(rate_key, SMS_INTERVAL, '1')
    redis_client.incr(daily_key)
    redis_client.expire(daily_key, 86400)

    # TODO: 接入腾讯云/阿里云短信通道
    print(f'[SMS] {phone} → {code}')

    return {'ok': True, 'error_code': 0, 'message': '验证码已发送'}


def verify(phone: str, code: str) -> bool:
    """校验验证码，成功则删除"""
    key = f'sms:code:{phone}'
    stored = redis_client.get(key)
    if stored and stored.decode() == code:
        redis_client.delete(key)
        return True
    return False