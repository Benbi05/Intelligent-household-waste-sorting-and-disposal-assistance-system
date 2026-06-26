# 《智能垃圾分类监管与积分运营系统》接口文档 **v3.0**

> **修订说明（v2.0 → v3.0）**  
> 本版基于安全审计结果进行全面加固，主要改进：
> - 🔴 **安全修复**：投放/补传接口移除客户端传入的 `userId`，改为扫码会话关联；`openid` 不再暴露到前端；文件上传增加类型/大小/病毒检测；核销增加跨商铺校验
> - 🟠 **补齐缺失接口**：新增短信发送、用户信息修改、识别历史、投放详情、设备 CRUD、角色权限、操作日志、规则回退、模型切换、固件升级、远程配置、统计导出、商家申请、子账号、运营看板、区域管理等 **27 个接口**
> - 🟡 **逻辑修复**：识别接口增加 SSRF 防护；积分兑换增加事务隔离说明；统一子状态枚举；补充订单取消接口
> - 🟢 **规范完善**：建立全局错误码体系（1000~5999）；增加幂等实现指引；增加异步任务回调机制；增加消息推送触发说明；增加区域管理

---

## 目录
- 一、接口规范说明
- 二、公共服务模块
- 三、居民用户模块（小程序端）
- 四、智能终端模块（垃圾箱端）
- 五、管理员后台模块
- 六、商家运营模块
- 七、全局错误码表
- 八、通用枚举说明
- 九、附录（幂等指引、回调规范、安全要求）

---

## 一、接口规范说明

### 1. 基础URL
- 开发环境：`http://10.2.0.247:8082/api/v1`
- 生产环境：`https://api.garbage-system.com/v1`

### 2. 请求头通用规则

| 参数名 | 类型 | 适用端 | 必填 | 说明 |
|--------|------|--------|------|------|
| Content-Type | String | 全部 | 是 | 统一为 `application/json`（图片上传接口使用 `multipart/form-data`） |
| X-Token | String | 全部（除登录和上传外） | 是 | 登录后返回的 JWT Token，用于身份鉴权，有效期 2 小时 |
| X-Device-Id | String | 智能终端 | 是 | 设备唯一编号（仅在设备鉴权前使用，鉴权后改用 Token） |
| X-Device-Secret | String | 智能终端 | 是 | 设备接入密钥（仅在设备鉴权接口使用） |
| X-Refresh-Token | String | 全部 | 否 | 用于刷新过期的 X-Token，有效期 7 天 |

> **身份识别规则（强制）**：所有业务接口（登录接口除外）均通过 `X-Token` 解析出用户/管理员/商家/设备身份，后端**禁止**依据前端传递的任何 ID 字段进行权限判断。用户 ID 从 Token 中解析，不得出现在请求 Body 中，防止越权攻击。

### 3. 统一响应格式
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "2026-06-26T10:30:00+08:00"
}
```

### 4. HTTP 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 操作成功（业务 code=200） |
| 400 | 请求参数错误或业务逻辑失败（业务 code 非 200） |
| 401 | Token 无效或已过期 |
| 403 | 无权限访问该资源 |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

### 5. 分页请求参数规范
所有列表接口统一使用以下分页参数（均为 Query 参数）：
- `page`：页码，从 1 开始，默认 1
- `size`：每页数量，默认 10，最大 100
- `sortField`：排序字段，默认 `createTime`
- `sortOrder`：排序方向，`asc` 或 `desc`，默认 `desc`

### 6. 时间格式
所有时间字段统一使用 ISO 8601 格式，如 `2026-06-26T10:30:00+08:00`。

### 7. 安全通用要求

| 要求项 | 说明 |
|--------|------|
| 密码复杂度 | 最少 8 位，包含大小写字母、数字、特殊字符中至少 3 类 |
| 登录失败锁定 | 同一账号 5 分钟内连续失败 5 次，锁定 15 分钟 |
| 验证码有效期 | SMS 验证码 5 分钟有效，4 位数字，同一手机号 60 秒内仅可发送 1 次，每日上限 10 次 |
| Token 刷新 | X-Token 有效期 2 小时，过期后使用 X-Refresh-Token 换取新 Token |
| 接口幂等 | 写操作接口均需实现幂等，详见附录一 |
| 敏感数据 | 手机号在列表接口中脱敏展示（如 138****8000），详情接口需二次鉴权 |

---

## 二、公共服务模块

### 1. 发送短信验证码

| 项目 | 说明 |
|------|------|
| 编号 | API0001 |
| 功能描述 | 发送短信验证码到指定手机号，含频率限制和图形验证码校验 |
| 请求URL | POST /common/sms/send |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "phone": "13800138000",
  "captchaToken": "图形验证码Token"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "expireSeconds": 300
  }
}
```

**安全约束**：
- 同一手机号 60 秒内仅可发送 1 次，每日累计不超过 10 次
- 需先通过图形验证码校验，防止自动化攻击
- 验证码 5 分钟有效，4 位数字

**错误码**：
- 1001：发送频率超限（60 秒内重复请求）
- 1002：当日发送次数已达上限
- 1003：图形验证码校验失败

---

### 2. 图片上传（通用）

| 项目 | 说明 |
|------|------|
| 编号 | API0002 |
| 功能描述 | 上传图片文件，返回访问 URL，用于后续识别或记录 |
| 请求URL | POST /common/upload/image |
| 完成情况 | 待开发 |

**请求参数**：`multipart/form-data`，字段名 `file`

**安全约束**：
| 约束项 | 限制值 |
|--------|--------|
| 允许的 MIME 类型 | image/jpeg, image/png, image/webp |
| 文件大小上限 | 10 MB |
| 文件名 | 服务端随机重命名，不保留原始文件名 |
| 病毒扫描 | 上传后服务端执行 ClamAV 扫描 |

**响应数据**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "imageUrl": "https://cdn.garbage-system.com/images/2026/06/abc123.jpg",
    "expireTime": "2026-12-26T10:30:00+08:00"
  }
}
```

**错误码**：
- 2001：文件类型不允许
- 2002：文件大小超过上限
- 2003：文件安全扫描未通过

---

### 3. 获取图形验证码

| 项目 | 说明 |
|------|------|
| 编号 | API0003 |
| 功能描述 | 获取图形验证码，用于短信发送前的安全校验 |
| 请求URL | GET /common/captcha |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "captchaToken": "验证码Token（用于校验）",
    "captchaImage": "data:image/png;base64,..."
  }
}
```

---

## 三、居民用户模块（小程序端）

### 1. 微信授权登录（获取 openid）

| 项目 | 说明 |
|------|------|
| 编号 | API101 |
| 功能描述 | 通过微信 code 换取 openid 和 session_key，若用户已注册则直接登录返回 Token；若未注册则返回临时会话 Token 引导绑定手机 |
| 请求URL | POST /user/wx-login |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "wxCode": "微信授权code"
}
```

**响应数据（已注册用户）**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "userId": 1,
    "token": "JWT_TOKEN",
    "refreshToken": "REFRESH_TOKEN",
    "nickName": "张三",
    "avatarUrl": "https://...",
    "phone": "138****8000",
    "pointBalance": 350
  }
}
```

**响应数据（未注册用户）**
```json
{
  "code": 200,
  "message": "需要绑定手机号",
  "data": {
    "needBindPhone": true,
    "bindToken": "临时绑定Token（有效期10分钟）"
  }
}
```

> **安全说明**：`openid` 不返回给前端，由服务端与 `bindToken` 关联存储在 Redis 中，有效期 10 分钟。`bind-phone` 接口仅需传入 `bindToken`，防止 `openid` 暴露和伪造。

---

### 2. 绑定手机号（新用户注册）

| 项目 | 说明 |
|------|------|
| 编号 | API102 |
| 功能描述 | 新用户绑定手机号，完成注册并生成积分账户 |
| 请求URL | POST /user/bind-phone |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "bindToken": "临时绑定Token",
  "phone": "13800138000",
  "smsCode": "123456"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "userId": 1,
    "token": "JWT_TOKEN",
    "refreshToken": "REFRESH_TOKEN",
    "nickName": "用户",
    "avatarUrl": "",
    "phone": "138****8000",
    "pointBalance": 0
  }
}
```

**错误码**：
- 3001：bindToken 无效或已过期
- 3002：手机号已被其他账号绑定
- 3003：验证码错误或已过期
- 3004：验证码错误次数超限，请重新发送

---

### 3. Token 刷新

| 项目 | 说明 |
|------|------|
| 编号 | API103 |
| 功能描述 | X-Token 过期后使用 Refresh-Token 换取新 Token |
| 请求URL | POST /user/refresh-token |
| 完成情况 | 待开发 |

**请求参数**（Header）
| 参数名 | 必填 | 说明 |
|--------|------|------|
| X-Refresh-Token | 是 | 登录时获取的刷新 Token |

**响应数据**
```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "NEW_JWT_TOKEN",
    "refreshToken": "NEW_REFRESH_TOKEN"
  }
}
```

**错误码**：
- 3005：Refresh-Token 无效或已过期（需重新登录）

---

### 4. 用户登出

| 项目 | 说明 |
|------|------|
| 编号 | API104 |
| 功能描述 | 主动使当前 Token 失效 |
| 请求URL | POST /user/logout |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

---

### 5. 拍照查询垃圾分类

| 项目 | 说明 |
|------|------|
| 编号 | API105 |
| 功能描述 | 上传垃圾图片 URL，返回分类结果与投放指引，支持多目标识别 |
| 请求URL | POST /user/garbage/recognize |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "imageUrl": "https://cdn.garbage-system.com/images/2026/06/abc123.jpg"
}
```

> **SSRF 防护（强制）**：服务端仅接受白名单域名（如 `cdn.garbage-system.com`）的 URL，拒绝内网 IP（10.x, 172.16-31.x, 192.168.x, 127.x）、非白名单域名和非 HTTP/HTTPS 协议的 URL。URL 解析到内网地址时直接拒绝。

**响应数据**
```json
{
  "code": 200,
  "message": "识别成功",
  "data": {
    "recognizeId": "REC1718123456789",
    "resultList": [
      {
        "categoryId": 101,
        "categoryName": "塑料饮料瓶",
        "parentType": "recyclable",
        "parentTypeName": "可回收物",
        "confidence": 0.96,
        "guide": "请清空内容物后投入可回收物桶",
        "boxRegion": { "x": 0.15, "y": 0.22, "width": 0.45, "height": 0.63 }
      }
    ],
    "createTime": "2026-06-26T10:30:00+08:00"
  }
}
```

**错误码**：
- 3101：图片模糊或无有效垃圾
- 3102：识别服务超时
- 3103：URL 域名不在白名单内
- 3104：URL 指向内网地址

---

### 6. 拍照识别历史记录

| 项目 | 说明 |
|------|------|
| 编号 | API106 |
| 功能描述 | 分页查询用户的历史拍照识别记录 |
| 请求URL | GET /user/recognize/history |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| startTime | String | 否 | ISO 8601 |
| endTime | String | 否 | ISO 8601 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "recognizeId": "REC1718123456789",
        "imageUrl": "https://cdn.../abc123.jpg",
        "categoryName": "塑料饮料瓶",
        "parentTypeName": "可回收物",
        "confidence": 0.96,
        "createTime": "2026-06-26T10:30:00+08:00"
      }
    ],
    "total": 22,
    "page": 1,
    "size": 10
  }
}
```

---

### 7. 获取用户信息

| 项目 | 说明 |
|------|------|
| 编号 | API107 |
| 功能描述 | 获取当前登录用户基础信息与积分概览 |
| 请求URL | GET /user/info |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "userId": 1,
    "nickName": "张三",
    "avatarUrl": "https://...",
    "phone": "138****8000",
    "pointBalance": 260,
    "totalDeliveryTimes": 18,
    "correctRate": 0.89
  }
}
```

---

### 8. 修改用户信息

| 项目 | 说明 |
|------|------|
| 编号 | API108 |
| 功能描述 | 修改当前登录用户的昵称、头像等个人信息 |
| 请求URL | PUT /user/info |
| 完成情况 | 待开发 |

**请求参数**（可部分更新）
```json
{
  "nickName": "张三",
  "avatarUrl": "https://..."
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

### 9. 获取积分账户详情

| 项目 | 说明 |
|------|------|
| 编号 | API109 |
| 功能描述 | 获取积分余额与累计统计 |
| 请求URL | GET /user/point/account |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "balance": 350,
    "totalEarned": 520,
    "totalSpent": 170,
    "updateTime": "2026-06-25T10:30:00+08:00"
  }
}
```

---

### 10. 获取积分规则（用户视角）

| 项目 | 说明 |
|------|------|
| 编号 | API110 |
| 功能描述 | 查看当前生效的积分奖惩规则，供用户了解投放积分标准 |
| 请求URL | GET /user/point/rules |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "version": "v2.3",
    "ruleList": [
      {
        "categoryId": 101,
        "categoryName": "塑料饮料瓶",
        "parentType": "可回收物",
        "rewardPoint": 15,
        "penaltyPoint": 5
      },
      {
        "categoryId": 201,
        "categoryName": "剩饭菜",
        "parentType": "厨余垃圾",
        "rewardPoint": 10,
        "penaltyPoint": 3
      }
    ]
  }
}
```

---

### 11. 获取积分明细列表

| 项目 | 说明 |
|------|------|
| 编号 | API111 |
| 功能描述 | 分页查询积分增减流水 |
| 请求URL | GET /user/point/records |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| recordType | String | 否 | earn / spend / all |
| startTime | String | 否 | ISO 8601 |
| endTime | String | 否 | ISO 8601 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "id": 1,
        "changeAmount": 15,
        "recordType": "earn",
        "reason": "可回收物正确投放奖励",
        "relatedId": "DLV20260625001",
        "createTime": "2026-06-25T09:15:00+08:00"
      }
    ],
    "total": 36,
    "page": 1,
    "size": 10
  }
}
```

---

### 12. 获取投放记录列表

| 项目 | 说明 |
|------|------|
| 编号 | API112 |
| 功能描述 | 分页查询历史投放记录，支持筛选 |
| 请求URL | GET /user/delivery/records |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| isCorrect | Boolean | 否 | true/false |
| startTime | String | 否 | ISO 8601 |
| endTime | String | 否 | ISO 8601 |
| area | String | 否 | 投放区域 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "recordId": "DLV20260625001",
        "deliveryTime": "2026-06-25T09:15:00+08:00",
        "location": "A区1号垃圾箱",
        "garbageTypeName": "可回收物",
        "isCorrect": true,
        "pointChange": 15,
        "deviceName": "A区1号可回收箱"
      }
    ],
    "total": 28,
    "page": 1,
    "size": 10
  }
}
```

---

### 13. 获取投放记录详情

| 项目 | 说明 |
|------|------|
| 编号 | API113 |
| 功能描述 | 查看单条投放记录的完整详情，包含抓拍图像 |
| 请求URL | GET /user/delivery/records/{recordId} |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "recordId": "DLV20260625001",
    "deliveryTime": "2026-06-25T09:15:00+08:00",
    "deviceName": "A区1号可回收箱",
    "location": "A区",
    "boxCategory": "recyclable",
    "garbageCategory": "塑料饮料瓶",
    "parentTypeName": "可回收物",
    "isCorrect": true,
    "pointChange": 15,
    "captureImageUrl": "https://cdn.../capture.jpg",
    "weight": 0.35
  }
}
```

---

### 14. 积分商品列表

| 项目 | 说明 |
|------|------|
| 编号 | API114 |
| 功能描述 | 浏览可兑换商品，支持按积分范围筛选 |
| 请求URL | GET /mall/commodities |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| pointMin | Integer | 否 | 最低积分 |
| pointMax | Integer | 否 | 最高积分 |
| keyword | String | 否 | 商品名称模糊搜索 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "commodityId": 1,
        "commodityName": "环保垃圾袋50只装",
        "pointPrice": 200,
        "stock": 500,
        "imageUrl": "https://...",
        "merchantName": "绿色家园便利店"
      }
    ],
    "total": 24,
    "page": 1,
    "size": 10
  }
}
```

---

### 15. 提交积分兑换订单

| 项目 | 说明 |
|------|------|
| 编号 | API115 |
| 功能描述 | 使用积分兑换商品，生成核销订单（幂等，重复提交返回已有订单） |
| 请求URL | POST /mall/orders |
| 完成情况 | 待开发 |

> **事务一致性要求（强制）**：扣减用户积分、扣减商品库存、生成兑换订单必须在同一数据库事务中完成。使用 `SELECT ... FOR UPDATE` 对商品库存行加悲观锁，或使用乐观锁（version 字段）防止超卖。事务失败时全部回滚。

**请求参数**
```json
{
  "commodityId": 1,
  "quantity": 1,
  "idempotentKey": "UUID"   // 客户端生成，服务端按 userId + idempotentKey 联合校验
}
```

**响应数据（成功）**
```json
{
  "code": 200,
  "message": "兑换成功",
  "data": {
    "orderId": "ORD20260625001",
    "verifyCode": "V8X2K9",
    "deductPoint": 200,
    "merchantName": "绿色家园便利店",
    "expireTime": "2026-07-25T23:59:59+08:00"
  }
}
```

**错误码**：
- 3201：积分不足
- 3202：库存不足
- 3203：商品已下架
- 3204：重复提交（idempotentKey 已存在）

---

### 16. 取消兑换订单

| 项目 | 说明 |
|------|------|
| 编号 | API116 |
| 功能描述 | 未核销的兑换订单可在有效期内取消，退回积分与库存 |
| 请求URL | POST /mall/orders/{orderId}/cancel |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "订单已取消，积分已退回",
  "data": {
    "returnedPoint": 200
  }
}
```

**错误码**：
- 3205：订单已核销，无法取消
- 3206：订单已过期，无法取消

---

### 17. 我的兑换订单列表

| 项目 | 说明 |
|------|------|
| 编号 | API117 |
| 功能描述 | 查询用户所有兑换订单 |
| 请求URL | GET /mall/orders/my |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| orderStatus | String | 否 | unverified / verified / expired / cancelled |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "orderId": "ORD20260625001",
        "commodityName": "环保垃圾袋50只装",
        "pointCost": 200,
        "orderStatus": "unverified",
        "verifyCode": "V8X2K9",
        "createTime": "2026-06-25T14:20:00+08:00",
        "expireTime": "2026-07-25T23:59:59+08:00"
      }
    ],
    "total": 6,
    "page": 1,
    "size": 10
  }
}
```

---

### 18. 兑换订单详情

| 项目 | 说明 |
|------|------|
| 编号 | API118 |
| 功能描述 | 查看单条兑换订单详情，包含核销码、商家信息 |
| 请求URL | GET /mall/orders/{orderId} |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "orderId": "ORD20260625001",
    "commodityName": "环保垃圾袋50只装",
    "commodityImage": "https://...",
    "pointCost": 200,
    "orderStatus": "unverified",
    "verifyCode": "V8X2K9",
    "merchantName": "绿色家园便利店",
    "merchantAddress": "A区商业街12号",
    "merchantPhone": "138****1234",
    "createTime": "2026-06-25T14:20:00+08:00",
    "expireTime": "2026-07-25T23:59:59+08:00",
    "verifyTime": null
  }
}
```

---

## 四、智能终端模块（垃圾箱端）

### 1. 设备鉴权注册

| 项目 | 说明 |
|------|------|
| 编号 | API201 |
| 功能描述 | 设备启动时使用 DeviceId+Secret 换取设备 Token，后续所有请求使用此 Token |
| 请求URL | POST /device/auth |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "deviceId": "DEV-A001",
  "deviceSecret": "设备密钥"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "鉴权成功",
  "data": {
    "deviceToken": "设备会话Token",
    "boxCategory": "recyclable",
    "pointRuleVersion": "v2.3",
    "modelVersion": "v1.5",
    "heartbeatInterval": 300,
    "configUpdated": false
  }
}
```

---

### 2. 用户身份核验（扫码/刷卡）

| 项目 | 说明 |
|------|------|
| 编号 | API202 |
| 功能描述 | 用户通过扫码或刷卡在终端完成身份核验，建立用户-设备临时会话，返回 sessionToken 用于后续投放操作 |
| 请求URL | POST /device/user/session |
| 完成情况 | 待开发 |

> **设计说明**：此接口替代 v2.0 中由客户端直接传入 `userId` 的方案。用户扫码后，小程序将扫码信息（设备编号 + 临时授权码）提交给服务端，服务端建立用户-设备临时会话。终端通过轮询或 WebSocket 获取会话状态。本次投放识别的 API203 使用 `sessionToken` 而非 `userId`，杜绝身份伪造。

**请求参数**
```json
{
  "authCode": "用户扫码生成的临时授权码"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "身份核验成功",
  "data": {
    "sessionToken": "临时会话Token（有效期60秒）",
    "userMaskedName": "张**",
    "expireSeconds": 60
  }
}
```

**错误码**：
- 4101：授权码无效或已过期
- 4102：用户账号已被禁用

---

### 3. 投放识别与积分结算（统一接口）

| 项目 | 说明 |
|------|------|
| 编号 | API203 |
| 功能描述 | 上传投放抓拍图像，系统识别并校验分类，同时完成积分奖惩和记录持久化（幂等，通过 deliveryId 防重） |
| 请求URL | POST /device/delivery/submit |
| 完成情况 | 待开发 |

> **安全变更（v3.0）**：`userId` 不再由客户端传入，改为传入 API202 获取的 `sessionToken`。服务端从 `sessionToken` 中解析用户身份，防止终端伪造用户身份。

**请求参数**
```json
{
  "deliveryId": "DLV20260625A001",
  "sessionToken": "API202返回的临时会话Token",
  "imageUrl": "https://cdn.../capture.jpg",
  "boxCategory": "recyclable",
  "weight": 0.35,
  "deliveryTime": "2026-06-25T09:15:00+08:00"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "投放处理完成",
  "data": {
    "deliveryId": "DLV20260625A001",
    "isCorrect": true,
    "pointChange": 15,
    "garbageCategory": "塑料瓶",
    "voiceText": "分类正确，积分已到账",
    "correctCategory": "可回收物",
    "pointBalance": 365
  }
}
```

**错误码**：
- 4101：识别失败，请重试
- 4102：重复提交（deliveryId 已存在）
- 4103：sessionToken 无效或已过期
- 4104：设备在线状态异常

---

### 4. 设备状态周期上报

| 项目 | 说明 |
|------|------|
| 编号 | API204 |
| 功能描述 | 定时上报设备运行状态，异常时主动告警 |
| 请求URL | POST /device/status/report |
| 完成情况 | 待开发 |

> **枚举统一**：各子状态字段统一为 `online` / `offline` / `fault` 三态。`fault` 状态触发即时告警工单。

**请求参数**
```json
{
  "deviceId": "DEV-A001",
  "fullRate": 0.68,
  "cameraStatus": "online",
  "networkStatus": "online",
  "powerStatus": "online",
  "displayStatus": "online",
  "firmwareVersion": "v2.1.0",
  "errorCode": ""
}
```

**子状态字段说明**：

| 字段 | 可选值 | 说明 |
|------|--------|------|
| cameraStatus | online / offline / fault | 摄像头工作状态 |
| networkStatus | online / offline | 网络连接状态 |
| powerStatus | online / offline / fault | 供电状态 |
| displayStatus | online / offline / fault | 触控屏状态 |
| errorCode | 空字符串 或 故障码 | 非空时触发告警工单 |

**响应数据**
```json
{
  "code": 200,
  "message": "上报成功",
  "data": {
    "configUpdated": false,
    "latestRuleVersion": "v2.3",
    "latestFirmwareVersion": "v2.1.0"
  }
}
```

---

### 5. 离线数据批量补传

| 项目 | 说明 |
|------|------|
| 编号 | API205 |
| 功能描述 | 网络恢复后批量补传离线缓存的投放数据（每条记录自带 deliveryId 保证幂等） |
| 请求URL | POST /device/delivery/batch-upload |
| 完成情况 | 待开发 |

> **安全变更（v3.0）**：同 API203，每条记录使用 `sessionToken` 代替 `userId`。

**请求参数**
```json
{
  "deviceId": "DEV-A001",
  "deliveryList": [
    {
      "deliveryId": "DLV20260625A002",
      "sessionToken": "SESS_xxx",
      "imageUrl": "https://...",
      "boxCategory": "recyclable",
      "deliveryTime": "2026-06-25T08:10:00+08:00",
      "weight": 0.2
    }
  ]
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "补传完成",
  "data": {
    "successCount": 1,
    "failCount": 0,
    "failedList": [
      {
        "deliveryId": "DLV20260625A003",
        "reason": "sessionToken 已过期"
      }
    ]
  }
}
```

> **补传处理策略**：
> - 每条记录独立处理，一条失败不影响其他记录
> - 补传记录按实际投放时间 `deliveryTime` 应用当时的积分规则版本（由会话建立时的规则版本快照决定）
> - `failedList` 中的记录需修正后重新补传，不合规数据永久失败
> - 图片 URL 超过 30 天有效期时补传将失败，终端应在离线前先完成图片上传

---

### 6. 设备心跳保活

| 项目 | 说明 |
|------|------|
| 编号 | API206 |
| 功能描述 | 轻量级心跳接口，维持设备在线状态，拉取待执行指令 |
| 请求URL | POST /device/heartbeat |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "deviceId": "DEV-A001"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "心跳成功",
  "data": {
    "pendingCommands": [
      {
        "commandId": "CMD001",
        "commandType": "config_update",
        "commandBody": {
          "heartbeatInterval": 600
        }
      }
    ]
  }
}
```

---

## 五、管理员后台模块

### 1. 管理员登录

| 项目 | 说明 |
|------|------|
| 编号 | API301 |
| 功能描述 | 管理员账号密码登录，含失败次数限制 |
| 请求URL | POST /admin/login |
| 完成情况 | 待开发 |

> **安全要求**：同账号 5 分钟内连续失败 5 次，锁定 15 分钟。登录需输入图形验证码（调用 API0003 获取）。

**请求参数**
```json
{
  "username": "admin",
  "password": "123456",
  "captchaToken": "图形验证码Token",
  "captchaCode": "图形验证码"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "adminId": 1,
    "username": "admin",
    "role": "super_admin",
    "token": "JWT Token",
    "refreshToken": "REFRESH_TOKEN"
  }
}
```

**错误码**：
- 5001：用户名或密码错误
- 5002：账号已被锁定，请 15 分钟后重试
- 5003：图形验证码错误

---

### 2. 管理员 Token 刷新

| 项目 | 说明 |
|------|------|
| 编号 | API302 |
| 功能描述 | 刷新管理员 Token |
| 请求URL | POST /admin/refresh-token |
| 完成情况 | 待开发 |

**请求参数**（Header）
| 参数名 | 必填 | 说明 |
|--------|------|------|
| X-Refresh-Token | 是 | 登录时获取的刷新 Token |

**响应数据**
```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "NEW_JWT_TOKEN",
    "refreshToken": "NEW_REFRESH_TOKEN"
  }
}
```

---

### 3. 管理员登出

| 项目 | 说明 |
|------|------|
| 编号 | API303 |
| 功能描述 | 主动使当前管理员 Token 失效 |
| 请求URL | POST /admin/logout |
| 完成情况 | 待开发 |

---

### 4. 区域管理 — 获取区域列表

| 项目 | 说明 |
|------|------|
| 编号 | API304 |
| 功能描述 | 获取系统所有投放区域列表，用于设备绑定、统计筛选 |
| 请求URL | GET /admin/areas |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "areaId": 1,
      "areaName": "A区",
      "deviceCount": 12,
      "status": "active"
    },
    {
      "areaId": 2,
      "areaName": "B区",
      "deviceCount": 8,
      "status": "active"
    }
  ]
}
```

---

### 5. 区域管理 — 新增/编辑/删除区域

| 项目 | 说明 |
|------|------|
| 编号 | API305 / API306 / API307 |
| 功能描述 | 区域 CRUD |
| 请求URL | POST /admin/areas / PUT /admin/areas/{areaId} / DELETE /admin/areas/{areaId} |
| 完成情况 | 待开发 |

**请求参数（新增/编辑）**
```json
{
  "areaName": "C区",
  "description": "商业区东侧"
}
```

---

### 6. 居民用户列表

| 项目 | 说明 |
|------|------|
| 编号 | API308 |
| 功能描述 | 分页查询全量居民用户，支持模糊搜索和状态筛选 |
| 请求URL | GET /admin/users |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| keyword | String | 否 | 手机号/昵称（模糊匹配） |
| status | String | 否 | enable / disable |
| area | String | 否 | 所属区域 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "userId": 1,
        "nickName": "张三",
        "phone": "138****8000",
        "pointBalance": 350,
        "correctRate": 0.89,
        "status": "enable",
        "registerTime": "2026-05-10T12:00:00+08:00"
      }
    ],
    "total": 1280,
    "page": 1,
    "size": 10
  }
}
```

---

### 7. 用户详情

| 项目 | 说明 |
|------|------|
| 编号 | API309 |
| 功能描述 | 查看指定用户的完整信息（含手机号需二次鉴权） |
| 请求URL | GET /admin/users/{userId} |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "userId": 1,
    "nickName": "张三",
    "avatarUrl": "https://...",
    "phone": "13800138000",
    "pointBalance": 350,
    "totalDeliveryTimes": 45,
    "correctRate": 0.89,
    "status": "enable",
    "registerTime": "2026-05-10T12:00:00+08:00",
    "lastLoginTime": "2026-06-26T08:30:00+08:00"
  }
}
```

---

### 8. 修改用户状态（启用/禁用）

| 项目 | 说明 |
|------|------|
| 编号 | API310 |
| 功能描述 | 管理员禁用或启用指定用户账号 |
| 请求URL | PUT /admin/users/{userId}/status |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "status": "disable",
  "reason": "违规投放"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": null
}
```

---

### 9. 角色与权限管理

| 项目 | 说明 |
|------|------|
| 编号 | API311 |
| 功能描述 | 创建/编辑角色，分配功能权限 |
| 请求URL | POST /admin/roles / PUT /admin/roles/{roleId} / GET /admin/roles / DELETE /admin/roles/{roleId} |
| 完成情况 | 待开发 |

**请求参数（创建角色）**
```json
{
  "roleName": "区域管理员",
  "permissions": ["user:read", "device:read", "statistics:read", "report:read"],
  "description": "仅可查看所辖区域数据"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "角色创建成功",
  "data": {
    "roleId": 3,
    "roleName": "区域管理员"
  }
}
```

---

### 10. 操作日志查询

| 项目 | 说明 |
|------|------|
| 编号 | API312 |
| 功能描述 | 查询管理员操作行为日志，支持审计追溯 |
| 请求URL | GET /admin/logs |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| adminId | Integer | 否 | 操作人 ID |
| actionType | String | 否 | 操作类型 |
| startTime | String | 否 | ISO 8601 |
| endTime | String | 否 | ISO 8601 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "logId": 1024,
        "adminId": 1,
        "adminName": "admin",
        "actionType": "user_disable",
        "targetId": 15,
        "detail": "禁用了用户 138****8000，原因：违规投放",
        "ip": "192.168.1.100",
        "createTime": "2026-06-26T10:15:00+08:00"
      }
    ],
    "total": 256,
    "page": 1,
    "size": 10
  }
}
```

---

### 11. 智能设备列表

| 项目 | 说明 |
|------|------|
| 编号 | API313 |
| 功能描述 | 分页查询所有设备，支持状态和区域筛选 |
| 请求URL | GET /admin/devices |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| keyword | String | 否 | 设备编号/名称（模糊） |
| onlineStatus | String | 否 | online / offline / fault |
| boxCategory | String | 否 | recyclable / kitchen / hazardous / other |
| area | String | 否 | 所属区域 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "deviceId": "DEV-A001",
        "deviceName": "A区1号可回收箱",
        "boxCategory": "可回收物",
        "area": "A区",
        "onlineStatus": "online",
        "fullRate": 0.68,
        "firmwareVersion": "v2.1.0",
        "lastOnlineTime": "2026-06-25T15:00:00+08:00"
      }
    ],
    "total": 56,
    "page": 1,
    "size": 10
  }
}
```

---

### 12. 新增设备

| 项目 | 说明 |
|------|------|
| 编号 | API314 |
| 功能描述 | 录入新的智能垃圾箱终端设备，生成 DeviceId 和接入密钥 |
| 请求URL | POST /admin/devices |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "deviceName": "B区2号厨余箱",
  "boxCategory": "kitchen",
  "area": "B区",
  "location": "B区3栋旁",
  "secret": "初始设备密钥"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "设备添加成功",
  "data": {
    "deviceId": "DEV-B002",
    "deviceSecret": "系统生成的设备密钥"
  }
}
```

---

### 13. 设备详情

| 项目 | 说明 |
|------|------|
| 编号 | API315 |
| 功能描述 | 查看指定设备的完整详细信息 |
| 请求URL | GET /admin/devices/{deviceId} |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "deviceId": "DEV-A001",
    "deviceName": "A区1号可回收箱",
    "boxCategory": "可回收物",
    "area": "A区",
    "location": "A区1栋旁",
    "onlineStatus": "online",
    "fullRate": 0.68,
    "cameraStatus": "online",
    "networkStatus": "online",
    "powerStatus": "online",
    "displayStatus": "online",
    "firmwareVersion": "v2.1.0",
    "lastOnlineTime": "2026-06-25T15:00:00+08:00",
    "createTime": "2026-03-01T00:00:00+08:00",
    "todayDeliveryCount": 42,
    "totalDeliveryCount": 12890
  }
}
```

---

### 14. 修改设备状态/删除设备

| 项目 | 说明 |
|------|------|
| 编号 | API316 / API317 |
| 功能描述 | 启用/禁用设备、删除设备 |
| 请求URL | PUT /admin/devices/{deviceId}/status / DELETE /admin/devices/{deviceId} |
| 完成情况 | 待开发 |

**请求参数（状态修改）**
```json
{
  "status": "disable",
  "reason": "设备维修"
}
```

---

### 15. 远程配置设备参数

| 项目 | 说明 |
|------|------|
| 编号 | API318 |
| 功能描述 | 远程下发设备配置参数，设备下次心跳时拉取 |
| 请求URL | PUT /admin/devices/{deviceId}/config |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "heartbeatInterval": 600,
  "captureResolution": "720p",
  "voiceVolume": 80,
  "offlineCacheLimit": 500
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "配置已下发，等待设备同步",
  "data": {
    "commandId": "CMD20260626001"
  }
}
```

---

### 16. 固件升级下发

| 项目 | 说明 |
|------|------|
| 编号 | API319 |
| 功能描述 | 向指定设备或批量设备下发固件升级指令 |
| 请求URL | POST /admin/devices/firmware-upgrade |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "deviceIds": ["DEV-A001", "DEV-A002"],
  "firmwareVersion": "v2.2.0",
  "firmwareUrl": "https://cdn.../firmware-v2.2.0.bin",
  "upgradeStrategy": "scheduled",
  "scheduledTime": "2026-06-27T02:00:00+08:00"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "升级指令已下发",
  "data": {
    "commandId": "CMD20260626002",
    "affectedDeviceCount": 2
  }
}
```

---

### 17. 获取当前积分规则

| 项目 | 说明 |
|------|------|
| 编号 | API320 |
| 功能描述 | 查看当前生效的全品类积分奖惩规则 |
| 请求URL | GET /admin/point-rules/current |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "version": "v2.3",
    "publishTime": "2026-06-01T00:00:00+08:00",
    "operatorId": 1,
    "operatorName": "admin",
    "ruleList": [
      {
        "categoryId": 101,
        "categoryName": "塑料饮料瓶",
        "parentType": "可回收物",
        "rewardPoint": 15,
        "penaltyPoint": 5
      }
    ]
  }
}
```

---

### 18. 积分规则历史版本

| 项目 | 说明 |
|------|------|
| 编号 | API321 |
| 功能描述 | 查看积分规则的所有历史版本 |
| 请求URL | GET /admin/point-rules/history |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "version": "v2.3",
        "publishTime": "2026-06-01T00:00:00+08:00",
        "operatorName": "admin",
        "status": "current"
      },
      {
        "version": "v2.2",
        "publishTime": "2026-05-01T00:00:00+08:00",
        "operatorName": "admin",
        "status": "archived"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 10
  }
}
```

---

### 19. 发布新积分规则

| 项目 | 说明 |
|------|------|
| 编号 | API322 |
| 功能描述 | 发布新版本积分规则，系统异步同步至全端（最终一致性） |
| 请求URL | POST /admin/point-rules |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "ruleList": [
    {
      "categoryId": 101,
      "rewardPoint": 20,
      "penaltyPoint": 5
    }
  ]
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "规则发布成功，正在同步",
  "data": {
    "newVersion": "v2.4",
    "effectTime": "2026-06-26T12:00:00+08:00"
  }
}
```

---

### 20. 回退积分规则

| 项目 | 说明 |
|------|------|
| 编号 | API323 |
| 功能描述 | 回退积分规则到指定历史版本 |
| 请求URL | POST /admin/point-rules/rollback |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "targetVersion": "v2.2",
  "reason": "新规则存在配置错误"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "规则已回退至 v2.2，正在同步",
  "data": {
    "newVersion": "v2.5",
    "effectTime": "2026-06-26T13:00:00+08:00"
  }
}
```

---

### 21. 识别模型版本列表

| 项目 | 说明 |
|------|------|
| 编号 | API324 |
| 功能描述 | 查看所有历史模型版本与性能指标 |
| 请求URL | GET /admin/models/versions |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "modelId": 5,
      "version": "v1.5",
      "mapValue": 0.92,
      "accuracy": 0.91,
      "precision": 0.93,
      "recall": 0.89,
      "categoryCount": 56,
      "status": "online",
      "publishTime": "2026-06-01T00:00:00+08:00"
    }
  ]
}
```

---

### 22. 切换模型版本

| 项目 | 说明 |
|------|------|
| 编号 | API325 |
| 功能描述 | 将指定模型版本切换为线上生效版本（支持一键回滚） |
| 请求URL | PUT /admin/models/{modelId}/switch |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "switchType": "full",
  "canaryPercent": 0
}
```

> `switchType`: `full`（全量切换）/ `canary`（灰度发布）。灰度发布时 `canaryPercent` 取值 5~50，表示仅该比例的流量命中新模型。

**响应数据**
```json
{
  "code": 200,
  "message": "模型版本已切换",
  "data": {
    "newVersion": "v1.6",
    "effectTime": "2026-06-26T12:00:00+08:00"
  }
}
```

---

### 23. 触发模型增量训练

| 项目 | 说明 |
|------|------|
| 编号 | API326 |
| 功能描述 | 上传新增数据集，触发异步增量训练任务 |
| 请求URL | POST /admin/models/train |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "datasetUrl": "https://cdn.../dataset.zip",
  "datasetName": "6月新增垃圾品类数据集",
  "baseModelVersion": "v1.5",
  "callbackUrl": "https://api.garbage-system.com/v1/internal/train-callback"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "训练任务已提交",
  "data": {
    "taskId": "TRAIN20260625001",
    "status": "pending",
    "estimatedTime": 7200
  }
}
```

---

### 24. 查询模型训练任务状态

| 项目 | 说明 |
|------|------|
| 编号 | API327 |
| 功能描述 | 查询增量训练任务进度和结果 |
| 请求URL | GET /admin/models/train/{taskId}/status |
| 完成情况 | 待开发 |

**响应数据（进行中）**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "taskId": "TRAIN20260625001",
    "status": "running",
    "progress": 45,
    "estimatedRemain": 3600
  }
}
```

**响应数据（完成）**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "taskId": "TRAIN20260625001",
    "status": "success",
    "newModelVersion": "v1.6",
    "modelId": 6,
    "accuracy": 0.93,
    "mapValue": 0.94,
    "precision": 0.94,
    "recall": 0.91
  }
}
```

**响应数据（失败）**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "taskId": "TRAIN20260625001",
    "status": "failed",
    "errorMessage": "数据集格式校验失败：缺少 classes.txt"
  }
}
```

---

### 25. 数据看板概览统计

| 项目 | 说明 |
|------|------|
| 编号 | API328 |
| 功能描述 | 获取平台整体运营核心指标 |
| 请求URL | GET /admin/statistics/overview |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "totalUsers": 1280,
    "onlineDevices": 48,
    "totalDevices": 56,
    "todayDeliveryCount": 892,
    "monthCorrectRate": 0.87,
    "monthTotalPoint": 126500,
    "pendingMerchantCount": 3
  }
}
```

---

### 26. 投放数据多维度统计

| 项目 | 说明 |
|------|------|
| 编号 | API329 |
| 功能描述 | 按区域、时间、品类、正确率等维度进行投放数据统计查询 |
| 请求URL | GET /admin/statistics/delivery |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| startTime | String | 否 | ISO 8601 |
| endTime | String | 否 | ISO 8601 |
| area | String | 否 | 区域 |
| boxCategory | String | 否 | recyclable / kitchen / hazardous / other |
| groupBy | String | 否 | area / category / day / month |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "totalDeliveryCount": 25680,
    "correctRate": 0.87,
    "totalPointsAwarded": 385200,
    "totalPointsPenalized": 28600,
    "details": [
      {
        "group": "A区",
        "deliveryCount": 8900,
        "correctRate": 0.91,
        "topCategory": "可回收物",
        "pointsAwarded": 133500
      }
    ]
  }
}
```

---

### 27. 统计报表导出

| 项目 | 说明 |
|------|------|
| 编号 | API330 |
| 功能描述 | 将投放统计数据导出为 Excel 文件下载 |
| 请求URL | GET /admin/statistics/export |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| startTime | String | 是 | ISO 8601 |
| endTime | String | 是 | ISO 8601 |
| area | String | 否 | 区域 |
| format | String | 否 | xlsx / csv，默认 xlsx |

**响应数据**：文件流下载，Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

---

### 28. 商家列表

| 项目 | 说明 |
|------|------|
| 编号 | API331 |
| 功能描述 | 分页查询全量商家列表 |
| 请求URL | GET /admin/merchants |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| status | String | 否 | pending / approved / rejected / disabled |
| keyword | String | 否 | 店铺名称（模糊） |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "merchantId": 1,
        "storeName": "绿色家园便利店",
        "contactName": "李四",
        "contactPhone": "139****5678",
        "status": "approved",
        "applyTime": "2026-05-01T00:00:00+08:00",
        "auditTime": "2026-05-03T00:00:00+08:00"
      }
    ],
    "total": 15,
    "page": 1,
    "size": 10
  }
}
```

---

### 29. 商家入驻审核

| 项目 | 说明 |
|------|------|
| 编号 | API332 |
| 功能描述 | 审核商家入驻申请 |
| 请求URL | PUT /admin/merchants/{merchantId}/audit |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "status": "approved",
  "rejectReason": "资料不完整"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "审核完成",
  "data": null
}
```

---

### 30. 触发生成月度分析报告

| 项目 | 说明 |
|------|------|
| 编号 | API333 |
| 功能描述 | 调用大语言模型生成治理与商业分析报告（异步，完成后回调） |
| 请求URL | POST /admin/reports/generate |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "statMonth": "2026-06",
  "statArea": "全部区域",
  "reportType": "all"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "报告生成任务已提交",
  "data": {
    "reportId": "RPT202606001",
    "estimatedTime": 1800
  }
}
```

---

### 31. 分析报告列表（管理员侧）

| 项目 | 说明 |
|------|------|
| 编号 | API334 |
| 功能描述 | 查询所有已生成的分析报告 |
| 请求URL | GET /admin/reports |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| statMonth | String | 否 | 2026-06 |
| reportType | String | 否 | governance / business / all |
| area | String | 否 | 区域 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "reportId": "RPT202606001",
        "statMonth": "2026-06",
        "statArea": "全部区域",
        "reportType": "all",
        "status": "completed",
        "generateTime": "2026-06-26T00:00:00+08:00"
      }
    ],
    "total": 6,
    "page": 1,
    "size": 10
  }
}
```

---

### 32. 分析报告详情（管理员侧）

| 项目 | 说明 |
|------|------|
| 编号 | API335 |
| 功能描述 | 查看指定报告的完整内容 |
| 请求URL | GET /admin/reports/{reportId} |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "reportId": "RPT202606001",
    "statMonth": "2026-06",
    "statArea": "全部区域",
    "reportType": "all",
    "status": "completed",
    "governanceSection": {
      "deliveryTrend": "本月投放总量环比增长12%...",
      "correctRateTrend": "A区分类正确率上升3个百分点...",
      "problemAreas": ["C区厨余垃圾混投率偏高"],
      "optimizationAdvice": "建议在C区增设厨余垃圾专项指引牌"
    },
    "businessSection": {
      "consumeTrend": "塑料类可回收物增长18%...",
      "hotProducts": ["环保垃圾袋", "瓶装饮用水", "一次性餐具"],
      "suggestion": "建议增加日用清洁类商品库存"
    },
    "fullContent": "完整报告 Markdown 文本",
    "generateTime": "2026-06-26T00:00:00+08:00",
    "generateDuration": 1235
  }
}
```

---

### 33. 报告导出

| 项目 | 说明 |
|------|------|
| 编号 | API336 |
| 功能描述 | 将分析报告导出为 PDF 或 Word 文件 |
| 请求URL | GET /admin/reports/{reportId}/export |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| format | String | 否 | pdf / docx，默认 pdf |

**响应数据**：文件流下载

---

## 六、商家运营模块

### 1. 商家入驻申请

| 项目 | 说明 |
|------|------|
| 编号 | API401 |
| 功能描述 | 商家提交入驻申请资料，待管理员审核 |
| 请求URL | POST /merchant/apply |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "storeName": "绿色家园便利店",
  "contactName": "李四",
  "contactPhone": "13900005678",
  "businessLicense": "https://cdn.../license.jpg",
  "storeAddress": "A区商业街12号",
  "area": "A区",
  "description": "主营日用百货、清洁用品"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "申请已提交，等待审核",
  "data": {
    "merchantId": 1,
    "status": "pending"
  }
}
```

**错误码**：
- 6001：店铺名称已存在
- 6002：手机号已被其他商家绑定

---

### 2. 商家登录

| 项目 | 说明 |
|------|------|
| 编号 | API402 |
| 功能描述 | 商家运营人员登录，含失败次数限制 |
| 请求URL | POST /merchant/login |
| 完成情况 | 待开发 |

> **安全要求**：同管理员登录，5 分钟内失败 5 次锁定 15 分钟，需输入图形验证码。

**请求参数**
```json
{
  "username": "lvsejiayuan",
  "password": "123456",
  "captchaToken": "图形验证码Token",
  "captchaCode": "图形验证码"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "merchantId": 1,
    "storeName": "绿色家园便利店",
    "area": "A区",
    "token": "JWT Token",
    "refreshToken": "REFRESH_TOKEN"
  }
}
```

**错误码**：
- 6003：商家账号未通过审核
- 6004：商家账号已被禁用
- 6005：用户名或密码错误
- 6006：账号已锁定

---

### 3. 商家 Token 刷新

| 项目 | 说明 |
|------|------|
| 编号 | API403 |
| 功能描述 | 刷新商家 Token |
| 请求URL | POST /merchant/refresh-token |
| 完成情况 | 待开发 |

---

### 4. 商家登出

| 项目 | 说明 |
|------|------|
| 编号 | API404 |
| 功能描述 | 主动使当前商家 Token 失效 |
| 请求URL | POST /merchant/logout |
| 完成情况 | 待开发 |

---

### 5. 商家店铺信息管理

| 项目 | 说明 |
|------|------|
| 编号 | API405 |
| 功能描述 | 获取/修改店铺基础信息 |
| 请求URL | GET /merchant/info / PUT /merchant/info |
| 完成情况 | 待开发 |

**请求参数（修改）**
```json
{
  "storeName": "绿色家园便利店（旗舰店）",
  "storeAddress": "A区商业街12号-1",
  "description": "主营日用百货、清洁用品、环保产品",
  "contactPhone": "139****5678"
}
```

---

### 6. 兑换商品列表（商家侧）

| 项目 | 说明 |
|------|------|
| 编号 | API406 |
| 功能描述 | 查询本店铺所有积分兑换商品 |
| 请求URL | GET /merchant/commodities |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| status | String | 否 | on / off |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "commodityId": 1,
        "commodityName": "环保垃圾袋50只装",
        "pointPrice": 200,
        "stock": 500,
        "status": "on",
        "monthExchangeCount": 86
      }
    ],
    "total": 12,
    "page": 1,
    "size": 10
  }
}
```

---

### 7. 新增兑换商品

| 项目 | 说明 |
|------|------|
| 编号 | API407 |
| 功能描述 | 上架新的积分兑换商品 |
| 请求URL | POST /merchant/commodities |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "commodityName": "可降解洗碗海绵",
  "pointPrice": 150,
  "stock": 320,
  "imageUrl": "https://...",
  "description": "天然木浆材质，可自然降解",
  "useRules": "每人每月限兑2件"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "商品上架成功",
  "data": {
    "commodityId": 2
  }
}
```

---

### 8. 编辑/下架商品

| 项目 | 说明 |
|------|------|
| 编号 | API408 |
| 功能描述 | 修改商品信息或下架 |
| 请求URL | PUT /merchant/commodities/{commodityId} |
| 完成情况 | 待开发 |

**请求参数**（可部分更新）
```json
{
  "pointPrice": 180,
  "stock": 300,
  "status": "off"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

### 9. 兑换订单列表（商家侧）

| 项目 | 说明 |
|------|------|
| 编号 | API409 |
| 功能描述 | 查询本店铺所有兑换订单 |
| 请求URL | GET /merchant/orders |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| orderStatus | String | 否 | unverified / verified / expired / cancelled |
| keyword | String | 否 | 商品名称或用户手机号 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "orderId": "ORD20260625001",
        "commodityName": "环保垃圾袋50只装",
        "pointCost": 200,
        "userPhone": "138****8000",
        "orderStatus": "unverified",
        "createTime": "2026-06-25T14:20:00+08:00",
        "expireTime": "2026-07-25T23:59:59+08:00"
      }
    ],
    "total": 156,
    "page": 1,
    "size": 10
  }
}
```

---

### 10. 订单核销

| 项目 | 说明 |
|------|------|
| 编号 | API410 |
| 功能描述 | 通过核销码完成订单核销（幂等，且校验订单属于当前商家） |
| 请求URL | POST /merchant/orders/verify |
| 完成情况 | 待开发 |

> **安全变更（v3.0）**：核销时服务端必须校验该订单的 `merchantId` 与当前登录商家一致，防止跨商铺核销。核销码应具备足够熵值（8 位字母数字组合），防止枚举攻击。

**请求参数**
```json
{
  "verifyCode": "V8X2K9",
  "idempotentKey": "UUID"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "核销成功",
  "data": {
    "orderId": "ORD20260625001",
    "commodityName": "环保垃圾袋50只装",
    "verifyTime": "2026-06-26T15:30:00+08:00"
  }
}
```

**错误码**：
- 6101：核销码不存在
- 6102：该订单不属于当前商家
- 6103：订单已核销（重复核销）
- 6104：订单已过期
- 6105：订单已取消

---

### 11. 商业分析报告列表

| 项目 | 说明 |
|------|------|
| 编号 | API411 |
| 功能描述 | 获取商家可查看的月度分析报告列表（仅返回本商家所属区域的报告） |
| 请求URL | GET /merchant/reports |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| statMonth | String | 否 | 2026-06 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "reportId": "RPT202606001",
        "statMonth": "2026-06",
        "statArea": "A区",
        "reportType": "business",
        "generateTime": "2026-06-26T00:00:00+08:00"
      }
    ],
    "total": 6,
    "page": 1,
    "size": 10
  }
}
```

---

### 12. 商业分析报告详情

| 项目 | 说明 |
|------|------|
| 编号 | API412 |
| 功能描述 | 查看指定报告的完整内容 |
| 请求URL | GET /merchant/reports/{reportId} |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "reportId": "RPT202606001",
    "statMonth": "2026-06",
    "statArea": "A区",
    "consumeTrend": "本月塑料类可回收物增长18%，对应日用消费品需求上升",
    "hotProducts": ["环保垃圾袋", "瓶装饮用水", "一次性餐具"],
    "suggestion": "建议增加日用清洁类商品库存，配合积分兑换活动引流",
    "categoryBreakdown": {
      "塑料类": { "deliveryCount": 5800, "changeRate": 0.18 },
      "金属类": { "deliveryCount": 1200, "changeRate": 0.05 },
      "纸类": { "deliveryCount": 3200, "changeRate": -0.03 }
    },
    "fullContent": "完整报告文本"
  }
}
```

---

### 13. 商家运营数据看板

| 项目 | 说明 |
|------|------|
| 编号 | API413 |
| 功能描述 | 获取商家店铺运营核心指标 |
| 请求URL | GET /merchant/statistics |
| 完成情况 | 待开发 |

**响应数据**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "totalCommodities": 12,
    "onlineCommodities": 8,
    "monthOrderCount": 156,
    "monthVerifyCount": 142,
    "monthPointIncome": 31200,
    "topCommodity": "环保垃圾袋50只装",
    "topCommodityExchangeCount": 86
  }
}
```

---

### 14. 子账号管理

| 项目 | 说明 |
|------|------|
| 编号 | API414 |
| 功能描述 | 商家创建/管理子账号（店员核销账号） |
| 请求URL | POST /merchant/sub-accounts / GET /merchant/sub-accounts / PUT /merchant/sub-accounts/{subAccountId} / DELETE /merchant/sub-accounts/{subAccountId} |
| 完成情况 | 待开发 |

**请求参数（创建子账号）**
```json
{
  "username": "staff01",
  "password": "123456",
  "displayName": "店员小张",
  "permissions": ["order:view", "order:verify"]
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "子账号创建成功",
  "data": {
    "subAccountId": 1,
    "username": "staff01"
  }
}
```

---

## 七、全局错误码表

### 7.1 错误码段划分

| 码段 | 模块 | 说明 |
|------|------|------|
| 200 | 全局 | 操作成功 |
| 500 | 全局 | 服务器内部错误 |
| 1000~1999 | 公共服务 | 短信、上传、验证码 |
| 2000~2999 | 通用上传 | 文件上传相关 |
| 3000~3999 | 居民用户 | 登录、注册、识别、积分、兑换 |
| 4000~4999 | 智能终端 | 鉴权、投放、状态上报 |
| 5000~5999 | 管理员后台 | 登录、用户管理、设备管理、规则、模型、报告 |
| 6000~6999 | 商家运营 | 入驻、登录、商品、订单、报告 |

### 7.2 详细错误码

#### 公共服务（1000~1999）
| 错误码 | 说明 |
|--------|------|
| 1001 | 短信发送频率超限（60秒内重复请求） |
| 1002 | 当日短信发送次数已达上限（10次） |
| 1003 | 图形验证码校验失败 |
| 1004 | 图形验证码已过期 |

#### 文件上传（2000~2999）
| 错误码 | 说明 |
|--------|------|
| 2001 | 文件类型不允许 |
| 2002 | 文件大小超过上限（10MB） |
| 2003 | 文件安全扫描未通过 |
| 2004 | 文件上传失败，请重试 |

#### 居民用户（3000~3999）
| 错误码 | 说明 |
|--------|------|
| 3001 | bindToken 无效或已过期 |
| 3002 | 手机号已被其他账号绑定 |
| 3003 | 短信验证码错误或已过期 |
| 3004 | 验证码错误次数超限，请重新发送 |
| 3005 | Refresh-Token 无效或已过期，需重新登录 |
| 3006 | 微信授权 code 无效或已过期 |
| 3007 | 账号已被禁用，请联系管理员 |
| 3101 | 图片模糊或无有效垃圾 |
| 3102 | 识别服务超时，请重试 |
| 3103 | 图片 URL 域名不在白名单内 |
| 3104 | 图片 URL 指向内网地址 |
| 3201 | 积分不足 |
| 3202 | 商品库存不足 |
| 3203 | 商品已下架 |
| 3204 | 重复提交（idempotentKey 已存在） |
| 3205 | 订单已核销，无法取消 |
| 3206 | 订单已过期，无法取消 |

#### 智能终端（4000~4999）
| 错误码 | 说明 |
|--------|------|
| 4001 | 设备鉴权失败，DeviceId 或 Secret 无效 |
| 4002 | 设备已被禁用 |
| 4101 | 投放识别失败，请重试 |
| 4102 | 重复提交（deliveryId 已存在） |
| 4103 | sessionToken 无效或已过期 |
| 4104 | 设备权限不足 |
| 4201 | 批量补传部分失败 |
| 4202 | 离线数据图片 URL 已过期 |

#### 管理员后台（5000~5999）
| 错误码 | 说明 |
|--------|------|
| 5001 | 用户名或密码错误 |
| 5002 | 账号已被锁定，请 15 分钟后重试 |
| 5003 | 图形验证码错误 |
| 5004 | 无权限执行此操作 |
| 5101 | 用户不存在 |
| 5102 | 用户状态更新失败 |
| 5201 | 设备不存在 |
| 5202 | 设备编号重复 |
| 5301 | 规则参数非法 |
| 5302 | 规则版本冲突 |
| 5401 | 模型训练任务提交失败 |
| 5402 | 数据集格式校验失败 |
| 5403 | 训练任务失败 |
| 5501 | 报告生成失败 |
| 5502 | 报告不存在 |
| 5601 | 商家审核参数错误 |

#### 商家运营（6000~6999）
| 错误码 | 说明 |
|--------|------|
| 6001 | 店铺名称已存在 |
| 6002 | 手机号已被其他商家绑定 |
| 6003 | 商家账号未通过审核 |
| 6004 | 商家账号已被禁用 |
| 6005 | 用户名或密码错误 |
| 6006 | 账号已被锁定，请 15 分钟后重试 |
| 6101 | 核销码不存在 |
| 6102 | 该订单不属于当前商家 |
| 6103 | 订单已核销（重复核销） |
| 6104 | 订单已过期 |
| 6105 | 订单已取消 |
| 6201 | 子账号数量已达上限 |
| 6202 | 子账号用户名已存在 |

---

## 八、通用枚举说明

### 1. 垃圾分类大类
| 类型值 | 说明 |
|--------|------|
| recyclable | 可回收物 |
| kitchen | 厨余垃圾 |
| hazardous | 有害垃圾 |
| other | 其他垃圾 |

### 2. 订单状态
| 状态值 | 说明 | 合法流转 |
|--------|------|----------|
| unverified | 待核销 | → verified / expired / cancelled |
| verified | 已核销 | 终态 |
| expired | 已过期 | 终态（超过有效期自动流转） |
| cancelled | 已取消 | 终态（用户主动取消） |

### 3. 设备综合在线状态
| 状态值 | 说明 |
|--------|------|
| online | 在线（心跳正常） |
| offline | 离线（超过 3 个心跳周期无上报） |
| fault | 故障（任一子状态为 fault） |

### 4. 设备子状态（统一三态）
| 状态值 | 说明 |
|--------|------|
| online | 正常工作 |
| offline | 未连接/未检测到 |
| fault | 检测到故障，触发告警 |

> 适用字段：`cameraStatus`、`networkStatus`、`powerStatus`、`displayStatus`

### 5. 报告类型
| 类型值 | 说明 |
|--------|------|
| governance | 治理分析报告 |
| business | 商业预测报告 |
| all | 综合报告（治理+商业） |

### 6. 积分流水类型
| 类型值 | 说明 |
|--------|------|
| earn | 获得（投放奖励） |
| spend | 消耗（兑换商品） |
| penalty | 扣除（错误投放罚分） |
| refund | 退回（订单取消退回） |

### 7. 账号状态
| 状态值 | 说明 |
|--------|------|
| enable | 正常启用 |
| disable | 已禁用 |

### 8. 商家审核状态
| 状态值 | 说明 |
|--------|------|
| pending | 待审核 |
| approved | 已通过 |
| rejected | 已驳回 |
| disabled | 已禁用 |

### 9. 模型训练任务状态
| 状态值 | 说明 |
|--------|------|
| pending | 排队中 |
| running | 训练中 |
| success | 训练成功 |
| failed | 训练失败 |

### 10. 报告生成状态
| 状态值 | 说明 |
|--------|------|
| pending | 排队中 |
| generating | 生成中 |
| completed | 已完成 |
| failed | 生成失败 |

### 11. 操作日志类型
| 类型值 | 说明 |
|--------|------|
| user_create | 创建用户 |
| user_disable | 禁用/启用用户 |
| device_add | 新增设备 |
| device_config | 设备配置变更 |
| rule_publish | 发布积分规则 |
| rule_rollback | 回退积分规则 |
| model_train | 触发模型训练 |
| model_switch | 切换模型版本 |
| merchant_audit | 商家审核 |
| firmware_upgrade | 固件升级 |

---

## 九、附录

### 附录一：幂等性实现指引

| 接口 | 幂等键 | 幂等有效期 | 实现方式 |
|------|--------|------------|----------|
| API203 投放结算 | `deliveryId`（终端生成） | 30 天 | 数据库唯一索引 `(deliveryId)` |
| API205 批量补传 | 每条 `deliveryId` | 30 天 | 同 API203，逐条校验 |
| API115 积分兑换 | `userId + idempotentKey` | 24 小时 | Redis 缓存 + DB 唯一约束 |
| API410 订单核销 | `orderId + merchantId` | 永久 | 订单状态机，已核销不可重复 |
| API322 规则发布 | `version`（系统自增） | 永久 | 版本号自增，同一版本不可重复发布 |

> **幂等实现原则**：
> 1. 幂等键必须在服务端生成或由客户端与服务端联合校验（仅靠客户端 UUID 不可信）
> 2. 幂等记录必须设置合理过期时间，避免无限增长
> 3. 重复请求必须返回与原请求一致的响应（至少业务结果一致）
> 4. 分布式环境下使用 Redis + DB 双重保障

### 附录二：异步任务回调规范

以下接口为异步处理，完成后通过回调或 WebSocket 通知调用方：

| 接口 | 异步任务 | 完成通知方式 |
|------|----------|--------------|
| API326 模型训练 | 增量训练 | 训练完成后回调 `callbackUrl`，POST JSON 格式结果 |
| API333 报告生成 | LLM 分析 | 报告生成完成后服务端推送 WebSocket 消息，同时更新轮询接口状态 |
| API319 固件升级 | 设备升级 | 设备升级完成后通过 API206 心跳上行升级结果 |

**回调请求格式**：
```json
POST {callbackUrl}
{
  "taskId": "TRAIN20260625001",
  "status": "success",
  "result": { ... },
  "completeTime": "2026-06-27T00:00:00+08:00"
}
```

**回调安全要求**：
- 回调 URL 必须为系统内部白名单域名
- 回调请求需携带签名 `X-Callback-Signature`，接收方校验签名真实性
- 回调失败需重试 3 次（间隔 10s/60s/300s）

### 附录三：消息推送触发说明

系统在以下业务节点向用户小程序推送微信订阅消息：

| 触发场景 | 推送内容 | 推送时机 |
|----------|----------|----------|
| 投放完成 | 积分变动通知、分类结果 | API203 完成后即时推送 |
| 兑换成功 | 订单确认、核销码 | API115 完成后即时推送 |
| 订单核销 | 核销完成通知 | API410 完成后即时推送 |
| 订单即将过期 | 过期提醒 | 定时任务：过期前 24 小时 |
| 报告生成 | 月度报告已更新 | API333 完成后推送至管理员和对应区域商家 |
| 规则变更 | 积分规则已更新 | API322 发布后推送至全量用户 |

> 推送依赖微信小程序订阅消息模板，用户需先授权订阅。未授权订阅的用户不推送，不影响核心业务。

### 附录四：数据安全与隐私要求

| 数据类别 | 存储要求 | 访问控制 | 脱敏规则 |
|----------|----------|----------|----------|
| 用户手机号 | AES-256 加密存储 | 本人可查看完整号码，列表接口脱敏 | `138****8000` |
| 用户 openid | 单向哈希存储 | 仅服务端内部使用 | 禁止返回前端 |
| 用户密码 | bcrypt 加盐哈希 | 不可逆 | 不存储明文 |
| 设备密钥 | AES-256 加密存储 | 仅设备鉴权服务可读取 | 不对外暴露 |
| 投放抓拍图像 | 对象存储，访问签名 URL | 投放者和管理员可查看 | / |
| 核销码 | 明文存储 | 用户和对应商家可查看 | / |
| 操作日志 | 明文存储，只追加不修改 | 仅超级管理员可查看 | / |
| 用户位置信息 | AES-256 加密存储 | 仅用户本人和管理员可查看 | 仅展示区域级 |

### 附录五：接口变更记录

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-06 | 初始版本 |
| v2.0 | 2026-06 | 新增图片上传接口、统一鉴权、合并投放接口、补充列表接口、统一分页和时间格式 |
| v3.0 | 2026-06-26 | 安全加固：去除 userId 客户端传入、openid 不暴露、SSRF 防护、跨商铺核销校验；补齐 27 个缺失接口；建立全局错误码体系（1000~6999）；统一设备子状态枚举；增加异步回调、消息推送、幂等指引、数据安全附录 |

---

*文档版本 v3.0 | 最后更新：2026-06-26*
