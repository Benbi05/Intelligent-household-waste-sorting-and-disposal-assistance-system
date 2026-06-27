"""用户业务：信息管理、状态管理"""
from ..dao.user_dao import UserDAO
from ..dao.resident_dao import ResidentDAO
from ..dao.point_account_dao import PointAccountDAO
from ..extensions import db


def get_user_info(user_id: int) -> dict:
    user = UserDAO.get_by_id(user_id)
    if not user:
        return None
    resident = ResidentDAO.get_one(userId=user_id)
    point = PointAccountDAO.get_one(userId=user_id)
    return {
        "userId": user.id, "nickName": user.nickName, "avatarUrl": user.avatarUrl,
        "phone": mask(user.phone),
        "pointBalance": point.balance if point else 0,
        "totalDeliveryTimes": resident.totalDeliveryTimes if resident else 0,
        "correctRate": resident.correctRate if resident else 0.0,
    }


def update_user_info(user_id: int, **kwargs) -> bool:
    allowed = {"nickName", "avatarUrl"}
    data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not data:
        return False
    UserDAO.update(user_id, **data)
    db.session.commit()
    return True


def get_user_list(page=1, size=10, keyword="", status="") -> tuple:
    q = UserDAO.model.query.filter(UserDAO.model.userType == "resident")
    if keyword:
        q = q.filter((UserDAO.model.phone.contains(keyword)) |
                     (UserDAO.model.nickName.contains(keyword)))
    if status:
        q = q.filter(UserDAO.model.status == status)
    q = q.order_by(UserDAO.model.createTime.desc())
    pagination = q.paginate(page=page, per_page=size, error_out=False)
    records = []
    for u in pagination.items:
        r = ResidentDAO.get_one(userId=u.id)
        p = PointAccountDAO.get_one(userId=u.id)
        records.append({
            "userId": u.id, "nickName": u.nickName, "phone": mask(u.phone),
            "pointBalance": p.balance if p else 0,
            "correctRate": r.correctRate if r else 0.0,
            "status": u.status, "registerTime": u.createTime.isoformat() if u.createTime else "",
        })
    return records, pagination.total


def set_user_status(user_id: int, status: str) -> bool:
    UserDAO.update(user_id, status=status)
    db.session.commit()
    return True


def mask(phone: str) -> str:
    if phone and len(phone) == 11:
        return phone[:3] + "****" + phone[7:]
    return phone
