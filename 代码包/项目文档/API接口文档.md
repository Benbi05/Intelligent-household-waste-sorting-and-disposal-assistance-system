# 《智能垃圾分类监管与积分运营系统》接口文档 **v2.0**

> **修订说明**  
> 本版基于 v1.0 进行全面修订，主要改进：
> - 新增图片上传接口，解决识别流程图片来源缺失问题  
> - 统一鉴权方式：所有身份信息从 Token 解析，删除 Header 中的 `X-User-Id`、`X-Admin-Id`、`X-Merchant-Id`  
> - 拆分微信登录与手机号绑定，明确注册流程  
> - 合并终端投放识别与确认接口，保证积分事务一致性  
> - 补充缺失的列表接口（商家报告列表、模型训练状态查询）  
> - 增加用户/设备状态管理接口，补全 CRUD  
> - 统一分页参数、时间格式（ISO 8601）  
> - 所有接口增加幂等性说明和错误码细化

---

## 目录
- 一、接口规范说明  
- 二、居民用户模块（小程序端）  
- 三、智能终端模块（垃圾箱端）  
- 四、管理员后台模块  
- 五、商家运营模块  
- 六、通用枚举说明  

---

## 一、接口规范说明

### 1. 基础URL
- 开发环境：`http://10.2.0.247:8082/api/v1`
- 生产环境：`https://api.garbage-system.com/v1`

### 2. 请求头通用规则

| 参数名 | 类型 | 适用端 | 必填 | 说明 |
|--------|------|--------|------|------|
| Content-Type | String | 全部 | 是 | 统一为 `application/json`（图片上传接口使用 `multipart/form-data`） |
| X-Token | String | 全部（除登录和上传外） | 是 | 登录后返回的 JWT Token，用于身份鉴权 |
| X-Device-Id | String | 智能终端 | 是 | 设备唯一编号（仅在设备鉴权前使用，鉴权后改用 Token） |
| X-Device-Secret | String | 智能终端 | 是 | 设备接入密钥（仅在设备鉴权接口使用） |

> **身份识别规则**：所有业务接口（登录接口除外）均通过 `X-Token` 解析出用户/管理员/商家身份，后端**禁止**依据前端传递的 ID 字段进行权限判断，防止越权。

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
| 500 | 服务器内部错误 |

业务 `code` 统一为 200 表示成功，其他值表示失败（如 4001 积分不足、4002 库存不足等），具体在接口说明中给出。

### 5. 分页请求参数规范
所有列表接口统一使用以下分页参数（均为 Query 参数）：
- `page`：页码，从 1 开始，默认 1
- `size`：每页数量，默认 10，最大 100
- `sortField`：排序字段，默认 `createTime`
- `sortOrder`：排序方向，`asc` 或 `desc`，默认 `desc`

### 6. 时间格式
所有时间字段统一使用 ISO 8601 格式，如 `2026-06-26T10:30:00+08:00`。

---

## 二、居民用户模块（小程序端）

### 1. 微信授权登录（获取 openid）

| 项目 | 说明 |
|------|------|
| 编号 | API001 |
| 功能描述 | 通过微信 code 换取 openid 和 session_key，若用户已注册则直接登录返回 Token；若未注册则返回需绑定手机的标识 |
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
    "nickName": "张三",
    "avatarUrl": "https://...",
    "phone": "13800138000",
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
    "openid": "oXXXX"
  }
}
```

---

### 2. 绑定手机号（新用户注册）

| 项目 | 说明 |
|------|------|
| 编号 | API002 |
| 功能描述 | 新用户绑定手机号，完成注册并生成积分账户 |
| 请求URL | POST /user/bind-phone |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "openid": "oXXXX",
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
    "nickName": "用户",
    "avatarUrl": "",
    "phone": "13800138000",
    "pointBalance": 0
  }
}
```

---

### 3. 图片上传（通用）

| 项目 | 说明 |
|------|------|
| 编号 | API003 |
| 功能描述 | 上传图片文件，返回访问 URL，用于后续识别或记录 |
| 请求URL | POST /common/upload/image |
| 完成情况 | 待开发 |

**请求参数**：`multipart/form-data`，字段名 `file`

**响应数据**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "imageUrl": "https://cdn.garbage-system.com/images/2026/06/abc123.jpg"
  }
}
```

---

### 4. 拍照查询垃圾分类

| 项目 | 说明 |
|------|------|
| 编号 | API004 |
| 功能描述 | 上传垃圾图片 URL，返回分类结果与投放指引，支持多目标识别 |
| 请求URL | POST /user/garbage/recognize |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "imageUrl": "https://cdn.../abc123.jpg"
}
```

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
        "guide": "请清空内容物后投入可回收物桶"
      }
    ]
  }
}
```

**错误码**：
- 4001：图片模糊或无有效垃圾
- 4002：识别服务超时

---

### 5. 获取用户信息

| 项目 | 说明 |
|------|------|
| 编号 | API005 |
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
    "phone": "13800138000",
    "pointBalance": 260,
    "totalDeliveryTimes": 18,
    "correctRate": 0.89
  }
}
```

---

### 6. 获取积分账户详情

| 项目 | 说明 |
|------|------|
| 编号 | API006 |
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

### 7. 获取积分明细列表

| 项目 | 说明 |
|------|------|
| 编号 | API007 |
| 功能描述 | 分页查询积分增减流水 |
| 请求URL | GET /user/point/records |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| recordType | String | 否 | earn / spend / all |

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

### 8. 获取投放记录列表

| 项目 | 说明 |
|------|------|
| 编号 | API008 |
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

### 9. 积分商品列表

| 项目 | 说明 |
|------|------|
| 编号 | API009 |
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

### 10. 提交积分兑换订单

| 项目 | 说明 |
|------|------|
| 编号 | API010 |
| 功能描述 | 使用积分兑换商品，生成核销订单（幂等，重复提交返回已有订单） |
| 请求URL | POST /mall/orders |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "commodityId": 1,
  "quantity": 1,
  "idempotentKey": "UUID"   // 客户端生成，防止重复提交
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
- 4001：积分不足
- 4002：库存不足

---

### 11. 我的兑换订单列表

| 项目 | 说明 |
|------|------|
| 编号 | API011 |
| 功能描述 | 查询用户所有兑换订单 |
| 请求URL | GET /mall/orders/my |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| orderStatus | String | 否 | unverified / verified / expired |

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
        "createTime": "2026-06-25T14:20:00+08:00"
      }
    ],
    "total": 6,
    "page": 1,
    "size": 10
  }
}
```

---

## 三、智能终端模块（垃圾箱端）

### 1. 设备鉴权注册

| 项目 | 说明 |
|------|------|
| 编号 | API101 |
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
    "heartbeatInterval": 300
  }
}
```

---

### 2. 投放识别与积分结算（统一接口）

> **合并原 API102 和 API103**，一次请求完成识别、校验、积分扣减和记录生成，保证事务一致性。终端调用此接口后，无需再调用确认接口。

| 项目 | 说明 |
|------|------|
| 编号 | API102 |
| 功能描述 | 上传投放抓拍图像，系统识别并校验分类，同时完成积分奖惩和记录持久化（幂等，通过 deliveryId 防重） |
| 请求URL | POST /device/delivery/submit |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "deliveryId": "DLV20260625A001",   // 终端生成唯一ID，用于幂等
  "userId": 1,
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
    "correctCategory": "可回收物"
  }
}
```

**错误码**：
- 4001：识别失败，请重试
- 4002：重复提交（deliveryId 已存在）

---

### 3. 设备状态周期上报

| 项目 | 说明 |
|------|------|
| 编号 | API103 |
| 功能描述 | 定时上报设备运行状态，异常时主动告警 |
| 请求URL | POST /device/status/report |
| 完成情况 | 待开发 |

**请求参数**（Body 中必须包含 deviceId，便于日志追踪）
```json
{
  "deviceId": "DEV-A001",
  "fullRate": 0.68,
  "cameraStatus": "normal",
  "networkStatus": "online",
  "powerStatus": "normal",
  "firmwareVersion": "v2.1.0"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "上报成功",
  "data": {
    "configUpdated": false,
    "latestRuleVersion": "v2.3"
  }
}
```

---

### 4. 离线数据批量补传

| 项目 | 说明 |
|------|------|
| 编号 | API104 |
| 功能描述 | 网络恢复后批量补传离线缓存的投放数据（每条记录自带 deliveryId 保证幂等） |
| 请求URL | POST /device/delivery/batch-upload |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "deviceId": "DEV-A001",
  "deliveryList": [
    {
      "deliveryId": "DLV20260625A002",
      "userId": 1,
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
    "failedIds": []
  }
}
```

---

## 四、管理员后台模块

### 1. 管理员登录

| 项目 | 说明 |
|------|------|
| 编号 | API201 |
| 功能描述 | 管理员账号密码登录 |
| 请求URL | POST /admin/login |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "username": "admin",
  "password": "123456"
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
    "token": "JWT Token"
  }
}
```

---

### 2. 居民用户列表

| 项目 | 说明 |
|------|------|
| 编号 | API202 |
| 功能描述 | 分页查询全量居民用户，支持模糊搜索和状态筛选 |
| 请求URL | GET /admin/users |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| keyword | String | 否 | 手机号/昵称 |
| status | String | 否 | enable / disable |

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
        "phone": "13800138000",
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

### 3. 修改用户状态（启用/禁用）

| 项目 | 说明 |
|------|------|
| 编号 | API203 |
| 功能描述 | 管理员禁用或启用指定用户账号 |
| 请求URL | PUT /admin/users/{userId}/status |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "status": "disable"   // 或 enable
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

### 4. 智能设备列表

| 项目 | 说明 |
|------|------|
| 编号 | API204 |
| 功能描述 | 分页查询所有设备，支持状态和区域筛选 |
| 请求URL | GET /admin/devices |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| keyword | String | 否 | 设备编号/名称 |
| onlineStatus | String | 否 | online / offline |
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

### 5. 修改设备状态（禁用/启用）

| 项目 | 说明 |
|------|------|
| 编号 | API205 |
| 功能描述 | 管理员禁用或启用设备（禁用后设备无法接入） |
| 请求URL | PUT /admin/devices/{deviceId}/status |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "status": "disable"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "设备状态更新成功",
  "data": null
}
```

---

### 6. 获取当前积分规则

| 项目 | 说明 |
|------|------|
| 编号 | API206 |
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

### 7. 发布新积分规则

| 项目 | 说明 |
|------|------|
| 编号 | API207 |
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

### 8. 识别模型版本列表

| 项目 | 说明 |
|------|------|
| 编号 | API208 |
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
      "categoryCount": 56,
      "status": "online",
      "publishTime": "2026-06-01T00:00:00+08:00"
    }
  ]
}
```

---

### 9. 触发模型增量训练

| 项目 | 说明 |
|------|------|
| 编号 | API209 |
| 功能描述 | 上传新增数据集，触发异步增量训练任务 |
| 请求URL | POST /admin/models/train |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "datasetUrl": "https://cdn.../dataset.zip",
  "datasetName": "6月新增垃圾品类数据集"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "训练任务已提交",
  "data": {
    "taskId": "TRAIN20260625001",
    "estimatedTime": 7200   // 秒
  }
}
```

---

### 10. 查询模型训练任务状态

| 项目 | 说明 |
|------|------|
| 编号 | API210 |
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
    "status": "running",   // pending / running / success / failed
    "progress": 45,        // 百分比
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
    "accuracy": 0.93,
    "mapValue": 0.94
  }
}
```

---

### 11. 数据看板概览统计

| 项目 | 说明 |
|------|------|
| 编号 | API211 |
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
    "todayDeliveryCount": 892,
    "monthCorrectRate": 0.87,
    "monthTotalPoint": 126500,
    "pendingMerchantCount": 3
  }
}
```

---

### 12. 触发生成月度分析报告

| 项目 | 说明 |
|------|------|
| 编号 | API212 |
| 功能描述 | 调用大语言模型生成治理与商业分析报告（异步） |
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

### 13. 商家入驻审核

| 项目 | 说明 |
|------|------|
| 编号 | API213 |
| 功能描述 | 审核商家入驻申请 |
| 请求URL | PUT /admin/merchants/{merchantId}/audit |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "status": "approved",   // approved / rejected
  "rejectReason": "资料不完整"  // 驳回时必填
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

## 五、商家运营模块

### 1. 商家登录

| 项目 | 说明 |
|------|------|
| 编号 | API301 |
| 功能描述 | 商家运营人员登录 |
| 请求URL | POST /merchant/login |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "username": "lvsejiayuan",
  "password": "123456"
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
    "token": "JWT Token"
  }
}
```

---

### 2. 兑换商品列表（商家侧）

| 项目 | 说明 |
|------|------|
| 编号 | API302 |
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

### 3. 新增兑换商品

| 项目 | 说明 |
|------|------|
| 编号 | API303 |
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
  "description": "天然木浆材质，可自然降解"
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

### 4. 编辑/下架商品

| 项目 | 说明 |
|------|------|
| 编号 | API304 |
| 功能描述 | 修改商品信息或下架 |
| 请求URL | PUT /merchant/commodities/{commodityId} |
| 完成情况 | 待开发 |

**请求参数**（可部分更新）
```json
{
  "pointPrice": 180,
  "stock": 300,
  "status": "off"   // 下架
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

### 5. 兑换订单列表（商家侧）

| 项目 | 说明 |
|------|------|
| 编号 | API305 |
| 功能描述 | 查询本店铺所有兑换订单 |
| 请求URL | GET /merchant/orders |
| 完成情况 | 待开发 |

**请求参数**（Query）
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | 否 | 默认1 |
| size | Integer | 否 | 默认10 |
| orderStatus | String | 否 | unverified / verified |

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
        "createTime": "2026-06-25T14:20:00+08:00"
      }
    ],
    "total": 156,
    "page": 1,
    "size": 10
  }
}
```

---

### 6. 订单核销

| 项目 | 说明 |
|------|------|
| 编号 | API306 |
| 功能描述 | 通过核销码完成订单核销（幂等） |
| 请求URL | POST /merchant/orders/verify |
| 完成情况 | 待开发 |

**请求参数**
```json
{
  "verifyCode": "V8X2K9"
}
```

**响应数据**
```json
{
  "code": 200,
  "message": "核销成功",
  "data": {
    "orderId": "ORD20260625001",
    "commodityName": "环保垃圾袋50只装"
  }
}
```

**错误码**：
- 4001：核销码不存在或已核销

---

### 7. 商业分析报告列表

| 项目 | 说明 |
|------|------|
| 编号 | API307 |
| 功能描述 | 获取商家可查看的月度分析报告列表（按区域分配） |
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

### 8. 商业分析报告详情

| 项目 | 说明 |
|------|------|
| 编号 | API308 |
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
    "fullContent": "..."   // 完整报告文本
  }
}
```

---

## 六、通用枚举说明

### 1. 垃圾分类大类
| 类型值 | 说明 |
|--------|------|
| recyclable | 可回收物 |
| kitchen | 厨余垃圾 |
| hazardous | 有害垃圾 |
| other | 其他垃圾 |

### 2. 订单状态
| 状态值 | 说明 |
|--------|------|
| unverified | 待核销 |
| verified | 已核销 |
| expired | 已过期 |
| cancelled | 已取消 |

### 3. 设备在线状态
| 状态值 | 说明 |
|--------|------|
| online | 在线 |
| offline | 离线 |
| fault | 故障 |

### 4. 报告类型
| 类型值 | 说明 |
|--------|------|
| governance | 治理分析报告 |
| business | 商业预测报告 |
| all | 综合报告 |

### 5. 积分流水类型
| 类型值 | 说明 |
|--------|------|
| earn | 获得 |
| spend | 消耗 |

---

*文档版本 v2.0 | 最后更新：2026-06-26*