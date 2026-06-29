"""鉴权业务：登录、注册、Token 管理"""
import bcrypt
from ..common.auth import generate_token, generate_refresh_token
from ..common.sms import verify as verify_sms
from ..extensions import redis_client
from ..dao.user_dao import UserDAO
from ..dao.resident_dao import ResidentDAO
from ..dao.administrator_dao import AdministratorDAO
from ..dao.merchant_dao import MerchantDAO
from ..dao.point_account_dao import PointAccountDAO


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


LOGIN_MAX_FAIL = 5
LOGIN_LOCK_MINUTES = 15


def check_login_lock(user_type: str, username: str) -> tuple:
    key = f"login:lock:{user_type}:{username}"
    fail_count = int(redis_client.get(key) or 0)
    if fail_count >= LOGIN_MAX_FAIL:
        ttl = redis_client.ttl(key)
        return True, f"账号已锁定，请 {ttl // 60 + 1} 分钟后重试"
    return False, ""


def record_login_fail(user_type: str, username: str):
    key = f"login:lock:{user_type}:{username}"
    redis_client.incr(key)
    redis_client.expire(key, LOGIN_LOCK_MINUTES * 60)


def reset_login_fail(user_type: str, username: str):
    redis_client.delete(f"login:lock:{user_type}:{username}")


def wx_login(wx_code: str) -> dict:
    openid = f"mock_openid_{wx_code[:8]}"
    user = UserDAO.get_one(openid=openid)
    if user:
        token = generate_token(user.id, "resident")
        refresh = generate_refresh_token(user.id, "resident")
        resident = ResidentDAO.get_one(userId=user.id)
        point = PointAccountDAO.get_one(userId=user.id)
        return {"ok": True, "needBindPhone": False, "userId": user.id,
                "token": token, "refreshToken": refresh,
                "nickName": user.nickName, "avatarUrl": user.avatarUrl,
                "phone": mask_phone(user.phone or ""),
                "pointBalance": point.balance if point else 0}
    bind_token = f"bind:{openid}"
    redis_client.setex(bind_token, 600, openid)
    return {"ok": True, "needBindPhone": True, "bindToken": bind_token}


def bind_phone(bind_token: str, phone: str, sms_code: str) -> dict:
    openid = redis_client.get(bind_token)
    if not openid:
        return {"ok": False, "error_code": 3001}
    if not verify_sms(phone, sms_code):
        return {"ok": False, "error_code": 3003}
    exist = UserDAO.get_one(phone=phone)
    if exist:
        return {"ok": False, "error_code": 3002}
    user = UserDAO.create(openid=openid.decode(), phone=phone, userType="resident")
    ResidentDAO.create(userId=user.id)
    PointAccountDAO.create(userId=user.id, balance=0)
    UserDAO.commit()
    redis_client.delete(bind_token)
    token = generate_token(user.id, "resident")
    refresh = generate_refresh_token(user.id, "resident")
    return {"ok": True, "error_code": 0, "userId": user.id,
            "token": token, "refreshToken": refresh,
            "nickName": "用户", "avatarUrl": "", "phone": mask_phone(phone), "pointBalance": 0}


def admin_login(username: str, password: str) -> dict:
    locked, msg = check_login_lock("admin", username)
    if locked:
        return {"ok": False, "error_code": 5002, "message": msg}
    admin = AdministratorDAO.get_one(username=username)
    if not admin or not check_password(password, admin.passwordHash):
        record_login_fail("admin", username)
        return {"ok": False, "error_code": 5001, "message": "用户名或密码错误"}
    reset_login_fail("admin", username)
    token = generate_token(admin.userId, admin.role)
    refresh = generate_refresh_token(admin.userId, admin.role)
    from ..extensions import db
    from datetime import datetime
    admin.lastLoginTime = datetime.utcnow()
    db.session.commit()
    return {"ok": True, "error_code": 0, "adminId": admin.id,
            "username": admin.username, "role": admin.role,
            "token": token, "refreshToken": refresh}


def merchant_login(username: str, password: str) -> dict:
    locked, msg = check_login_lock("merchant", username)
    if locked:
        return {"ok": False, "error_code": 6006, "message": msg}
    merchant = MerchantDAO.get_one(username=username)
    if not merchant:
        record_login_fail("merchant", username)
        return {"ok": False, "error_code": 6005, "message": "用户名或密码错误"}
    if not check_password(password, merchant.passwordHash):
        record_login_fail("merchant", username)
        return {"ok": False, "error_code": 6005, "message": "用户名或密码错误"}
    if merchant.status == "pending":
        return {"ok": False, "error_code": 6003, "message": "商家账号未通过审核"}
    if merchant.status == "disabled":
        return {"ok": False, "error_code": 6004}
    reset_login_fail("merchant", username)
    token = generate_token(merchant.userId, "merchant")
    refresh = generate_refresh_token(merchant.userId, "merchant")
    return {"ok": True, "error_code": 0, "merchantId": merchant.id,
            "storeName": merchant.storeName, "area": merchant.area,
            "token": token, "refreshToken": refresh}


def refresh_access_token(refresh_token: str) -> dict:
    import jwt
    from flask import current_app
    try:
        payload = jwt.decode(refresh_token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return {"ok": False, "error_code": 3005}
        new_token = generate_token(payload["user_id"], payload["role"])
        new_refresh = generate_refresh_token(payload["user_id"], payload["role"])
        return {"ok": True, "token": new_token, "refreshToken": new_refresh}
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {"ok": False, "error_code": 3005}


def logout(token: str):
    redis_client.sadd("token:blacklist", token)


def mask_phone(phone: str) -> str:
    if phone and len(phone) == 11:
        return phone[:3] + "****" + phone[7:]
    return phone
