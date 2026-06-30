"""虎溪街道8个社区演示数据"""
import sys, os; sys.path.insert(0, '.')
from app import create_app
from app.extensions import db
from app.models import *
from datetime import datetime, timedelta
import random, uuid, hashlib

app = create_app('development')
random.seed(42)

COMMUNITIES = [
    ('虎溪花园', 12, 0.88, 0.72),     # 12栋，A区88% B区72%
    ('学府悦园', 10, 0.82, 0.76),     # 10栋
    ('康居西城', 15, 0.75, 0.70),     # 15栋，老旧社区，分类较差
    ('龙湖U城', 8, 0.91, 0.86),       # 8栋，高档小区，分类好
    ('金科廊桥水乡', 10, 0.85, 0.78),
    ('富力城', 14, 0.79, 0.73),
    ('恒大未来城', 11, 0.83, 0.77),
    ('融创文旅城', 9, 0.87, 0.80),
]

with app.app_context():
    # 清空旧数据
    DeliveryRecord.query.delete()
    PointRecord.query.delete()
    PointAccount.query.delete()
    Resident.query.delete()
    Device.query.delete()
    User.query.filter_by(userType='resident').delete()
    db.session.commit()

    # 取品类
    cats = GarbageCategory.query.with_entities(GarbageCategory.categoryName, GarbageCategory.parentType).all()
    now = datetime.utcnow()
    all_device_ids = []
    all_user_ids = []

    # 为每个社区建设备和居民
    for comm_name, bld_count, a_rate, b_rate in COMMUNITIES:
        # 区域
        area_name = comm_name[:3]
        if not Area.query.filter_by(areaName=area_name).first():
            db.session.add(Area(areaName=area_name, description=comm_name))
            db.session.flush()

        # 设备（每栋3个）
        for bnum in range(1, bld_count + 1):
            for bt, bn, ct in [('R','可回收','recyclable'), ('K','厨余','kitchen'), ('O','其他','other')]:
                did = f'{area_name}-{str(bnum).zfill(2)}-{bt}'
                dev = Device(deviceId=did, deviceName=f'{comm_name}{bnum}栋{bn}箱', deviceSecret='demo',
                       boxCategory=ct, area=area_name, location=f'{comm_name}{bnum}栋',
                       onlineStatus=random.choice(['online']*9+['offline']+['fault']),
                       fullRate=round(random.uniform(0.1,0.9),2),
                       cameraStatus='online', networkStatus='online', powerStatus='online',
                       totalDeliveryCount=random.randint(300,2000),
                       lastOnlineTime=now - timedelta(minutes=random.randint(0,120)))
                db.session.add(dev)
                all_device_ids.append(did)

        # 居民（每栋5个）
        for bnum in range(1, bld_count + 1):
            for i in range(1, 6):
                u = User(phone=f'139{hashlib.md5(f"{comm_name}{bnum}{i}".encode()).hexdigest()[:8]}',
                         nickName=f'{comm_name}{bnum}栋0{i}', userType='resident', status='enable')
                db.session.add(u); db.session.flush()
                Resident(userId=u.id, totalDeliveryTimes=random.randint(10,60),
                         correctRate=round(random.uniform(0.6,0.98),2))
                PointAccount(userId=u.id, balance=random.randint(30,300),
                             totalEarned=random.randint(50,800), totalSpent=random.randint(0,200))
                all_user_ids.append(u.id)
    db.session.commit()

    print(f'设备: {len(all_device_ids)} 台')
    print(f'居民: {len(all_user_ids)} 人')

    # 生成投放记录
    print('生成投放记录...')
    batch = []
    for day in range(30, -1, -1):
        date = now - timedelta(days=day)
        day_count = random.randint(600, 1200)
        for _ in range(day_count):
            did = random.choice(all_device_ids)
            comm = did.split('-')[0]
            cat = random.choice(cats)
            is_correct = random.random() < random.uniform(0.72, 0.90)
            pts = random.choice([10,12,15]) if is_correct else -random.choice([3,5,8])
            h, m = random.randint(6,22), random.randint(0,59)
            batch.append(DeliveryRecord(
                recordId=f'{comm}{date:%Y%m%d}{uuid.uuid4().hex[:8].upper()}',
                deviceId=did, userId=random.choice(all_user_ids),
                boxCategory=cat[1], garbageCategory=cat[0], parentType=cat[1],
                isCorrect=is_correct, pointChange=pts, weight=round(random.uniform(0.1, 1.5), 2),
                deliveryTime=date.replace(hour=h, minute=m), ruleVersion='v1.0'))
        if len(batch) > 1000:
            db.session.bulk_save_objects(batch); db.session.commit()
            batch = []
    if batch:
        db.session.bulk_save_objects(batch); db.session.commit()

    total = DeliveryRecord.query.count()
    correct = DeliveryRecord.query.filter_by(isCorrect=True).count()
    print(f'投放记录: {total} 条, 正确率: {correct/total*100:.1f}%')
    for c in COMMUNITIES:
        comm = c[0][:3]
        t = DeliveryRecord.query.filter(DeliveryRecord.deviceId.like(f'{comm}%')).count()
        cr = DeliveryRecord.query.filter(DeliveryRecord.deviceId.like(f'{comm}%'), DeliveryRecord.isCorrect==True).count()
        print(f'  {c[0]}: {t}次, {cr/t*100:.1f}%' if t else f'  {c[0]}: 无数据')
    print('完成！')
