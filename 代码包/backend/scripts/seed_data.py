"""种子数据填充：管理员、区域、垃圾分类"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.administrator import Administrator
from app.models.garbage_category import GarbageCategory
from app.models.area import Area
from app.services.auth_service import hash_password

app = create_app('development')

with app.app_context():
    # 1. 默认管理员
    if not User.query.filter_by(userType='administrator').first():
        admin_user = User(nickName='系统管理员', userType='administrator', status='enable')
        db.session.add(admin_user)
        db.session.flush()
        admin = Administrator(
            userId=admin_user.id, username='admin',
            passwordHash=hash_password('admin123'), role='super_admin')
        db.session.add(admin)
        print('管理员账号: admin / admin123')
    else:
        print('管理员已存在，跳过')

    # 2. 默认区域
    if Area.query.count() == 0:
        for name, desc in [('A区', '住宅区'), ('B区', '商业区'), ('C区', '学校及办公区')]:
            db.session.add(Area(areaName=name, description=desc))
        print('区域已创建')

    # 3. 垃圾分类（4大类 25个细分品类）
    if GarbageCategory.query.count() == 0:
        cats = [
            (101, '塑料饮料瓶', 'recyclable', '可回收物', 15, 5, '请清空内容物后投入可回收物桶'),
            (102, '金属易拉罐', 'recyclable', '可回收物', 12, 5, '请清空内容物后投入可回收物桶'),
            (103, '玻璃瓶', 'recyclable', '可回收物', 10, 5, '请投入可回收物桶，注意轻放'),
            (104, '废纸', 'recyclable', '可回收物', 8, 3, '请折叠后投入可回收物桶'),
            (105, '纸箱', 'recyclable', '可回收物', 10, 3, '请拆开压扁后投入可回收物桶'),
            (106, '旧衣物', 'recyclable', '可回收物', 10, 3, '请清洗后投入旧衣物回收箱'),
            (107, '塑料袋', 'recyclable', '可回收物', 5, 3, '请确保干净干燥后投入可回收物桶'),
            (201, '剩饭菜', 'kitchen', '厨余垃圾', 10, 5, '请沥干水分后投入厨余垃圾桶'),
            (202, '果皮', 'kitchen', '厨余垃圾', 8, 3, '请投入厨余垃圾桶'),
            (203, '菜叶', 'kitchen', '厨余垃圾', 8, 3, '请投入厨余垃圾桶'),
            (204, '蛋壳', 'kitchen', '厨余垃圾', 6, 3, '请投入厨余垃圾桶'),
            (205, '骨头', 'kitchen', '厨余垃圾', 8, 5, '大骨头属于其他垃圾，小骨头投入厨余桶'),
            (206, '茶叶渣', 'kitchen', '厨余垃圾', 8, 3, '请投入厨余垃圾桶'),
            (301, '电池', 'hazardous', '有害垃圾', 15, 10, '请投入有害垃圾桶，禁止随意丢弃'),
            (302, '过期药品', 'hazardous', '有害垃圾', 15, 10, '请带包装投入有害垃圾桶'),
            (303, '废灯管', 'hazardous', '有害垃圾', 15, 10, '请小心轻放投入有害垃圾桶'),
            (304, '废油漆桶', 'hazardous', '有害垃圾', 15, 10, '请密封后投入有害垃圾桶'),
            (305, '水银温度计', 'hazardous', '有害垃圾', 20, 15, '请小心轻放投入有害垃圾桶'),
            (401, '卫生纸', 'other', '其他垃圾', 3, 3, '请投入其他垃圾桶'),
            (402, '一次性餐具', 'other', '其他垃圾', 3, 3, '请投入其他垃圾桶'),
            (403, '陶瓷碎片', 'other', '其他垃圾', 3, 5, '请包裹后投入其他垃圾桶'),
            (404, '烟蒂', 'other', '其他垃圾', 3, 5, '请熄灭后投入其他垃圾桶'),
            (405, '卫生巾', 'other', '其他垃圾', 3, 3, '请投入其他垃圾桶'),
            (406, '尘土', 'other', '其他垃圾', 3, 3, '请投入其他垃圾桶'),
        ]
        for c in cats:
            db.session.add(GarbageCategory(categoryId=c[0], categoryName=c[1],
                parentType=c[2], parentTypeName=c[3], rewardPoint=c[4],
                penaltyPoint=c[5], guide=c[6]))
        print(f'{len(cats)} 个垃圾品类已创建')

    db.session.commit()
    print('\n种子数据填充完成！')