"""虎溪花园社区演示数据"""
import sys, os; sys.path.insert(0, '.')
from app import create_app
from app.extensions import db
from app.models import *
from app.services.auth_service import hash_password
from datetime import datetime, timedelta
import random, uuid, hashlib

app = create_app('development')
random.seed(42)
BUILDINGS = ['1栋','2栋','3栋','4栋','5栋','6栋','7栋','8栋','9栋','10栋','11栋','12栋']

with app.app_context():
    # 先清空投放记录（外键依赖）
    DeliveryRecord.query.delete()
    db.session.commit()

    # 1. 建设备
    print('创建设备...')
    dev_ids = {}
    for bld in BUILDINGS:
        bnum = bld.replace('栋','').zfill(2)
        area = 'A区' if int(bnum) <= 6 else 'B区'
        for bt, bn, ct in [('REC','可回收箱','recyclable'),('KIT','厨余箱','kitchen'),('OTH','其他箱','other')]:
            did = f'HXHY-{bnum}-{bt}'
            if not Device.query.get(did):
                dev = Device(deviceId=did, deviceName=f'虎溪花园{bld}{bn}', deviceSecret='demo',
                       boxCategory=ct, area=area, location=f'{bld}楼下投放点',
                       onlineStatus=random.choice(['online']*9+['offline']),
                       fullRate=round(random.uniform(0.1, 0.9),2),
                       cameraStatus='online', networkStatus='online', powerStatus='online',
                       totalDeliveryCount=random.randint(500,2000),
                       lastOnlineTime=datetime.utcnow()-timedelta(minutes=random.randint(0,60)))
                db.session.add(dev)
            dev_ids[bld] = did
    db.session.commit()
    print(f'  设备: {Device.query.count()} 台')

    # 2. 建居民
    print('创建居民...')
    res_ids = []
    for bld in BUILDINGS:
        for i in range(1,6):
            u = User(phone=f'139{hashlib.md5(f"{bld}{i}{uuid.uuid4().hex}".encode()).hexdigest()[:8]}', nickName=f'{bld}0{i}住户',
                     userType='resident', status='enable')
            db.session.add(u); db.session.flush()
            Resident(userId=u.id, totalDeliveryTimes=random.randint(20,80),
                     correctRate=round(random.uniform(0.6,0.98),2))
            PointAccount(userId=u.id, balance=random.randint(50,500),
                         totalEarned=random.randint(100,1000), totalSpent=random.randint(0,300))
            res_ids.append(u.id)
    db.session.commit()
    print(f'  居民: {len(res_ids)} 人')

    # 3. 取品类列表
    cats = GarbageCategory.query.with_entities(GarbageCategory.categoryName, GarbageCategory.parentType).all()

    # 4. 生成投放记录
    print('生成投放记录...')
    device_list = [d.deviceId for d in Device.query.all()]
    now = datetime.utcnow()
    batch = []
    for day in range(30, -1, -1):
        date = now - timedelta(days=day)
        for _ in range(random.randint(180, 350)):
            did = random.choice(device_list)
            area = 'A区' if int(did.split('-')[1]) <= 6 else 'B区'
            cat = random.choice(cats)
            correct = random.random() < (0.88 if area=='A区' else 0.74)
            pts = random.choice([10,12,15]) if correct else -random.choice([3,5,8])
            h, m = random.randint(6,22), random.randint(0,59)
            batch.append(DeliveryRecord(
                recordId=f'HX{date:%Y%m%d}{uuid.uuid4().hex[:6].upper()}',
                deviceId=did, userId=random.choice(res_ids),
                boxCategory=cat[1], garbageCategory=cat[0], parentType=cat[1],
                isCorrect=correct, pointChange=pts,
                deliveryTime=date.replace(hour=h, minute=m), ruleVersion='v1.0'))
        if len(batch) > 500:
            db.session.bulk_save_objects(batch); db.session.commit()
            batch = []
    if batch:
        db.session.bulk_save_objects(batch); db.session.commit()
    print(f'  投放记录: {DeliveryRecord.query.count()} 条')
    correct = DeliveryRecord.query.filter_by(isCorrect=True).count()
    total = DeliveryRecord.query.count()
    print(f'  分类正确率: {correct/total*100:.1f}%')
    print('\n演示数据生成完成！')
