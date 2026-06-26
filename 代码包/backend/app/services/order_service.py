"""订单业务：兑换、核销、库存"""
import uuid, random, string
from datetime import datetime, timedelta
from ..dao.point_account_dao import PointAccountDAO
from ..dao.point_record_dao import PointRecordDAO
from ..dao.point_order_dao import PointOrderDAO
from ..dao.commodity_dao import CommodityDAO
from ..dao.user_dao import UserDAO
from ..extensions import db


def create_order(user_id: int, commodity_id: int, quantity: int, idempotent_key: str) -> dict:
    exist = PointOrderDAO.get_one(idempotentKey=f"{user_id}:{idempotent_key}")
    if exist:
        return {"ok": False, "error_code": 3204}
    commodity = CommodityDAO.get_by_id(commodity_id)
    if not commodity or commodity.status != "on":
        return {"ok": False, "error_code": 3203}
    if commodity.stock < quantity:
        return {"ok": False, "error_code": 3202}
    total_points = commodity.pointPrice * quantity
    account = PointAccountDAO.get_one(userId=user_id)
    if not account or account.balance < total_points:
        return {"ok": False, "error_code": 3201}
    result = CommodityDAO.model.query.filter(
        CommodityDAO.model.id == commodity_id,
        CommodityDAO.model.version == commodity.version
    ).update({"stock": CommodityDAO.model.stock - quantity,
              "version": CommodityDAO.model.version + 1,
              "monthExchangeCount": CommodityDAO.model.monthExchangeCount + quantity})
    if result == 0:
        return {"ok": False, "error_code": 3202}
    account.balance -= total_points
    account.totalSpent += total_points
    order_id = f"ORD{datetime.utcnow():%Y%m%d}{uuid.uuid4().hex[:8].upper()}"
    verify_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    order = PointOrderDAO.create(
        orderId=order_id, userId=user_id, commodityId=commodity_id,
        merchantId=commodity.merchantId, pointCost=total_points, quantity=quantity,
        verifyCode=verify_code, idempotentKey=f"{user_id}:{idempotent_key}",
        orderStatus="unverified", expireTime=datetime.utcnow() + timedelta(days=30))
    PointRecordDAO.create(userId=user_id, changeAmount=-total_points, recordType="spend",
                          reason=f"兑换 {commodity.commodityName} x{quantity}", relatedId=order_id)
    db.session.commit()
    return {"ok": True, "error_code": 0, "orderId": order_id, "verifyCode": verify_code,
            "deductPoint": total_points, "expireTime": order.expireTime.isoformat()}


def cancel_order(user_id: int, order_id: str) -> dict:
    order = PointOrderDAO.get_by_id(order_id)
    if not order or order.userId != user_id:
        return {"ok": False, "error_code": 3205}
    if order.orderStatus == "verified":
        return {"ok": False, "error_code": 3205}
    if order.orderStatus == "expired":
        return {"ok": False, "error_code": 3206}
    order.orderStatus = "cancelled"
    account = PointAccountDAO.get_one(userId=user_id)
    account.balance += order.pointCost
    account.totalSpent -= order.pointCost
    CommodityDAO.model.query.filter_by(id=order.commodityId).update(
        {"stock": CommodityDAO.model.stock + order.quantity})
    PointRecordDAO.create(userId=user_id, changeAmount=order.pointCost, recordType="refund",
                          reason=f"订单 {order_id} 取消退回", relatedId=order_id)
    db.session.commit()
    return {"ok": True, "error_code": 0, "returnedPoint": order.pointCost}


def verify_order(merchant_id: int, verify_code: str) -> dict:
    order = PointOrderDAO.get_one(verifyCode=verify_code)
    if not order:
        return {"ok": False, "error_code": 6101}
    if order.merchantId != merchant_id:
        return {"ok": False, "error_code": 6102}
    if order.orderStatus == "verified":
        return {"ok": False, "error_code": 6103}
    if order.orderStatus == "expired":
        return {"ok": False, "error_code": 6104}
    if order.orderStatus == "cancelled":
        return {"ok": False, "error_code": 6105}
    order.orderStatus = "verified"
    order.verifyTime = datetime.utcnow()
    db.session.commit()
    commodity = CommodityDAO.get_by_id(order.commodityId)
    return {"ok": True, "error_code": 0, "orderId": order.orderId,
            "commodityName": commodity.commodityName if commodity else "",
            "verifyTime": order.verifyTime.isoformat()}


def get_user_orders(user_id: int, page=1, size=10, order_status="") -> tuple:
    q = PointOrderDAO.model.query.filter_by(userId=user_id)
    if order_status:
        q = q.filter_by(orderStatus=order_status)
    q = q.order_by(PointOrderDAO.model.createTime.desc())
    pagination = q.paginate(page=page, per_page=size, error_out=False)
    records = [{"orderId": o.orderId, "pointCost": o.pointCost, "orderStatus": o.orderStatus,
                "verifyCode": o.verifyCode, "createTime": o.createTime.isoformat(),
                "expireTime": o.expireTime.isoformat()} for o in pagination.items]
    return records, pagination.total


def get_merchant_orders(merchant_id: int, page=1, size=10, order_status="") -> tuple:
    q = PointOrderDAO.model.query.filter_by(merchantId=merchant_id)
    if order_status:
        q = q.filter_by(orderStatus=order_status)
    q = q.order_by(PointOrderDAO.model.createTime.desc())
    pagination = q.paginate(page=page, per_page=size, error_out=False)
    records = []
    for o in pagination.items:
        c = CommodityDAO.get_by_id(o.commodityId)
        u = UserDAO.get_by_id(o.userId)
        records.append({"orderId": o.orderId, "commodityName": c.commodityName if c else "",
                        "pointCost": o.pointCost, "userPhone": mask(u.phone) if u else "",
                        "orderStatus": o.orderStatus, "createTime": o.createTime.isoformat(),
                        "expireTime": o.expireTime.isoformat()})
    return records, pagination.total


def mask(phone: str) -> str:
    if phone and len(phone) == 11:
        return phone[:3] + "****" + phone[7:]
    return phone
