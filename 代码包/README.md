# 智能垃圾分类监管与积分运营系统

> 集智能识别、积分运营、数据决策、商家赋能于一体的智能垃圾分类监管系统

---

## 项目简介

针对当前垃圾分类落地中**居民分类准确率低、监管数据缺失、产业链路脱节**的痛点，本项目构建 "投放 → 识别 → 激励 → 分析 → 运营" 完整闭环：

| 角色 | 能力 |
|------|------|
| 🏠 **居民** | 微信小程序 — 拍照查询分类、积分账户管理、投放记录查询、积分商品兑换 |
| 📊 **监管方** | Web 管理后台 — 数据统计看板、LLM 智能分析报告、模型迭代管理、积分规则配置 |
| 🏪 **商家** | Web 运营后台 — 热销商品预测、兑换商品管理、订单核销、运营数据看板 |
| 🗑️ **终端** | 智能垃圾箱 — 投放抓拍识别、积分自动结算、语音播报、离线缓存补传 |

---

## 项目文件结构

```
代码包/
│
├── backend/                          # 🔧 Flask 后端服务
│   ├── app/                          #   应用主包
│   │   ├── __init__.py               #     Flask 工厂函数、配置加载
│   │   ├── config.py                 #     配置类（开发/生产/测试）
│   │   ├── extensions.py            #     扩展初始化（SQLAlchemy/Redis/MQTT）
│   │   │
│   │   ├── common/                   #   ── 公共服务层 ──
│   │   │   ├── auth.py              #     Token 鉴权装饰器（JWT）
│   │   │   ├── response.py          #     统一响应格式封装
│   │   │   ├── errors.py            #     全局异常捕获与错误码映射
│   │   │   ├── validators.py        #     请求参数校验器
│   │   │   ├── pagination.py        #     分页工具
│   │   │   ├── sms.py               #     短信发送服务
│   │   │   ├── captcha.py           #     图形验证码生成/校验
│   │   │   └── upload.py            #     文件上传（类型校验+病毒扫描）
│   │   │
│   │   ├── models/                   #   ── Model 层：18 个数据实体 ──
│   │   │   ├── base.py             #     User/Device/DeliveryRecord/PointAccount
│   │   │   ├── user.py             #     PointOrder/GarbageCategory/RecognitionModel
│   │   │   ├── resident.py         #     Commodity/AnalysisReport/Role/Permission
│   │   │   ├── administrator.py    #     OperationLog/Area/SubAccount
│   │   │   ├── merchant.py         #     ...
│   │   │   └── ...
│   │   │
│   │   ├── dao/                      #   ── DAO 层：数据操作 ──
│   │   │   ├── base_dao.py         #     通用 CRUD 基类
│   │   │   └── ...
│   │   │
│   │   ├── controllers/              #   ── Controller 层：5 组接口控制器 ──
│   │   │   ├── common/              #     公共服务（短信/上传/验证码）
│   │   │   ├── user/                #     居民用户（18 个接口）
│   │   │   ├── device/              #     智能终端（6 个接口）
│   │   │   ├── admin/               #     管理员后台（18 个接口）
│   │   │   └── merchant/            #     商家运营（14 个接口）
│   │   │
│   │   └── services/                 #   ── Service 层：业务逻辑 ──
│   │       ├── auth_service.py      #     鉴权（Token 生成/校验/黑名单）
│   │       ├── point_service.py     #     积分结算/流水/规则同步
│   │       ├── order_service.py     #     兑换/核销/库存扣减
│   │       ├── recognition_service.py #   识别服务调用
│   │       ├── report_service.py    #     LLM 报告生成
│   │       ├── mqtt_service.py      #     MQTT 终端通信
│   │       └── ai_client.py         #     AI 服务调用客户端
│   │
│   ├── migrations/                   #   数据库迁移脚本
│   ├── tests/                        #   单元测试
│   ├── scripts/                      #   初始化脚本
│   ├── requirements.txt             #    Python 依赖
│   ├── Dockerfile                   #    Docker 镜像
│   └── wsgi.py                      #    WSGI 入口
│
├── frontend/                         # 🎨 三套前端应用
│   │
│   ├── miniapp/                      #   微信小程序（居民端）
│   │   ├── app.js / app.json / app.wxss
│   │   ├── utils/                   #     请求封装/登录管理/图片压缩
│   │   ├── components/              #     公共组件
│   │   └── pages/                   #     6 个页面
│   │       ├── login/               #       登录授权
│   │       ├── home/                #       首页
│   │       ├── recognize/           #       拍照识别
│   │       ├── delivery/            #       投放记录（列表+详情）
│   │       ├── mall/                #       积分商城（商品+兑换+订单）
│   │       └── profile/             #       个人中心（信息+积分明细）
│   │
│   ├── admin-web/                    #   管理员 Web 后台（Vue3 + Element Plus）
│   │   └── src/
│   │       ├── api/                 #     接口请求层（10 个模块）
│   │       ├── router/ / store/     #     路由 + 状态管理（Pinia）
│   │       ├── components/          #     通用组件（表格/弹窗/图表/搜索）
│   │       └── views/               #     7 个页面
│   │           ├── login/           #       登录
│   │           ├── dashboard/       #       数据仪表盘
│   │           ├── user/            #       用户管理
│   │           ├── device/          #       设备管理
│   │           ├── point/           #       积分规则
│   │           ├── model/           #       模型管理
│   │           ├── report/          #       报告管理
│   │           ├── merchant/        #       商家审核
│   │           └── system/          #       区域/角色/日志
│   │
│   └── merchant-web/                 #   商家 Web 后台（Vue3 + Element Plus）
│       └── src/
│           ├── api/                 #     接口请求层
│           ├── components/          #     通用组件（复用 admin-web）
│           └── views/               #     5 个页面
│               ├── login/           #       登录 + 入驻申请
│               ├── dashboard/       #       运营看板
│               ├── commodity/       #       商品管理
│               ├── order/           #       订单核销
│               ├── report/          #       商业报告
│               └── settings/        #       店铺设置 + 子账号
│
├── ai-service/                       # 🤖 AI 推理服务（独立部署）
│   ├── recognition/                  #   垃圾图像识别
│   │   ├── app.py                   #     Flask 推理 API
│   │   ├── preprocess.py            #     图片预处理
│   │   ├── inference.py             #     ONNX Runtime 推理
│   │   ├── postprocess.py           #     后处理（NMS/坐标还原）
│   │   ├── classes.txt              #     类别清单
│   │   └── config.yaml              #     推理配置
│   │
│   ├── llm/                         #   大语言模型分析
│   │   ├── app.py                   #     LLM 分析 API
│   │   ├── preprocessor.py          #     数据清洗结构化
│   │   ├── prompts/                 #     Prompt 模板
│   │   ├── generator.py             #     LLM 调用与流式生成
│   │   └── formatter.py             #     报告格式化
│   │
│   └── training/                    #   模型训练工具
│       ├── train.py                 #     YOLOv5 增量训练
│       ├── validate.py              #     指标验证
│       ├── export_onnx.py           #     模型导出
│       └── dataset/                 #     数据集目录
│
├── database/                         # 🗄️ 数据库
│   ├── schema.sql                   #   全量表结构
│   ├── seed.sql                     #   种子数据
│   └── migrations/                  #   增量变更
│
├── deploy/                           # 🚀 部署配置
│   ├── docker-compose.yml           #   全栈服务编排
│   ├── nginx/                       #   反向代理
│   ├── mqtt/                        #   MQTT Broker
│   └── env/                         #   环境变量模板
│
├── 项目文档/                         # 📄 项目文档
│   ├── 03-智能垃圾分类监管与积分运营系统-需求说明书(1).docx   # 需求说明
│   ├── 04-智能垃圾分类监管与积分运营系统-概要设计文档.docx     # 概要设计
│   ├── API接口文档.md                # 59 个接口完整定义
│   ├── 分工文档.md                   # 三人分工与协作规范
│   └── 项目文件结构.md               # 完整目录树
│
└── README.md                         # 📘 本文档
```

---

## 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| 后端框架 | Python 3.8+ / Flask | 轻量级 Web 框架，MVC 分层 |
| ORM | SQLAlchemy + Flask-Migrate | 数据库映射与迁移 |
| 鉴权 | PyJWT | JWT Token + Refresh Token 双令牌 |
| 缓存 | Redis | Token 黑名单、短信限流、会话暂存 |
| 数据库 | MySQL 8.0 | 18 张业务表，第三范式 |
| 消息队列 | Eclipse Mosquitto (MQTT) | 终端设备双向通信 |
| 小程序 | 微信原生框架 | 居民端 6 页面 |
| Web 前端 | Vue 3 + Vite + Element Plus + ECharts | 管理后台 + 商家后台 |
| 目标检测 | YOLOv5 + ONNX Runtime | 图像识别，mAP ≥ 0.85 |
| 大模型 | LLM API + Prompt 模板 | 治理报告 + 商业预测 |
| 容器化 | Docker + Docker Compose | 一键部署 |
| 反向代理 | Nginx | 负载均衡与静态资源 |

---

## 核心量化目标

| 指标 | 目标值 |
|------|--------|
| 常见生活垃圾识别准确率 | ≥ 90% |
| 单张图片识别速度 | ≤ 1 秒 |
| 支持垃圾品类 | 4 大类、50+ 细分品类 |
| 系统年可用率 | ≥ 99% |
| 投放数据上报成功率 | ≥ 99% |
| 积分结算延迟 | ≤ 1 分钟 |
| 核心业务接口响应 | ≤ 200ms |
| 支持并发终端数 | ≥ 1000 台 |

---

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0
- Redis 6.0+
- Docker & Docker Compose（可选）

### 本地开发

```bash
# 1. 克隆项目
git clone <repo-url>
cd 代码包

# 2. 启动后端
cd backend
pip install -r requirements.txt
flask run

# 3. 启动 AI 服务
cd ../ai-service/recognition
pip install -r requirements.txt
python app.py

# 4. 启动前端（管理后台）
cd ../../frontend/admin-web
npm install
npm run dev

# 5. 打开微信开发者工具导入 frontend/miniapp/
```

### Docker 一键部署

```bash
cd deploy
docker-compose up -d
```

---

## 团队分工

| 成员 | 角色 | 核心职责 |
|------|------|----------|
| 同学1 | **后端** | Flask 服务端 59 个接口开发、18 张表数据库设计 |
| 同学2 | **前端** | 微信小程序 + 管理员 Web + 商家 Web 三端开发 |
| 同学3 | **AI + 工程支撑** | YOLO 模型训练推理 + LLM 分析 + 部署 + 测试 |

> 详见 [分工文档](项目文档/分工文档.md)

---

## 相关文档

- [需求说明书](项目文档/03-智能垃圾分类监管与积分运营系统-需求说明书(1).docx)
- [概要设计文档](项目文档/04-智能垃圾分类监管与积分运营系统-概要设计文档.docx)
- [API 接口文档 v3.0](项目文档/API接口文档.md)
- [分工文档](项目文档/分工文档.md)

---

*基于重庆大学实训课程（2026年6月）*
