"""积分业务：结算、流水、规则"""
from ..dao.point_account_dao import PointAccountDAO
from ..dao.point_record_dao import PointRecordDAO
from ..dao.garbage_category_dao import GarbageCategoryDAO
from ..extensions import db


def get_point_account(user_id: int) -> dict:
    account = PointAccountDAO.get_one(userId=user_id)
    if not account:
        return {"balance": 0, "totalEarned": 0, "totalSpent": 0}
    return {"balance": account.balance, "totalEarned": account.totalEarned,
            "totalSpent": account.totalSpent,
            "updateTime": account.updateTime.isoformat() if account.updateTime else ""}


def get_point_records(user_id: int, page=1, size=10, record_type="") -> tuple:
    q = PointRecordDAO.model.query.filter_by(userId=user_id)
    if record_type and record_type != "all":
        q = q.filter(PointRecordDAO.model.recordType == record_type)
    q = q.order_by(PointRecordDAO.model.createTime.desc())
    pagination = q.paginate(page=page, per_page=size, error_out=False)
    records = [{"id": r.id, "changeAmount": r.changeAmount, "recordType": r.recordType,
                "reason": r.reason, "relatedId": r.relatedId,
                "createTime": r.createTime.isoformat() if r.createTime else ""}
               for r in pagination.items]
    return records, pagination.total


def settle_points(user_id: int, garbage_category: str, is_correct: bool, delivery_id: str) -> dict:
    category = GarbageCategoryDAO.get_one(categoryName=garbage_category)
    if not category:
        return {"isCorrect": is_correct, "pointChange": 0, "voiceText": "识别完成"}
    account = PointAccountDAO.get_one(userId=user_id)
    if not account:
        account = PointAccountDAO.create(userId=user_id, balance=0)
        db.session.flush()
    if is_correct:
        points = category.rewardPoint
        record_type = "earn"
        voice = f"分类正确，+{points} 积分已到账"
    else:
        points = -category.penaltyPoint
        record_type = "penalty"
        voice = f"分类有误，{points} 积分"
    account.balance += points
    account.totalEarned += max(points, 0)
    account.totalSpent += abs(min(points, 0))
    PointRecordDAO.create(userId=user_id, changeAmount=points, recordType=record_type,
                          reason=f"{category.categoryName} {'正确投放奖励' if is_correct else '错误投放扣分'}",
                          relatedId=delivery_id)
    db.session.commit()
    return {"isCorrect": is_correct, "pointChange": points, "voiceText": voice,
            "pointBalance": account.balance}


def get_current_rules() -> dict:
    categories = GarbageCategoryDAO.get_all(status="enable")
    rules = [{"categoryId": c.categoryId, "categoryName": c.categoryName,
              "parentType": c.parentType, "parentTypeName": c.parentTypeName,
              "rewardPoint": c.rewardPoint, "penaltyPoint": c.penaltyPoint}
             for c in categories]
    return {"version": "v1.0", "ruleList": rules}


def publish_rules(rule_list: list) -> str:
    for rule in rule_list:
        GarbageCategoryDAO.update(rule["categoryId"], rewardPoint=rule["rewardPoint"],
                                  penaltyPoint=rule["penaltyPoint"])
    db.session.commit()
    return "v1.1"
