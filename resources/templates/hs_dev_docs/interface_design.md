# 接口设计文档：{interface_name}

> 细则见 Skill 内 `references/api_engineering.md`（错误语义、边界校验、幂等、兼容）。

## 1. 接口元数据
- **接口名称**：`{interface_name}`
- **接口协议**：RESTful JSON / gRPC / WebSocket
- **端点路径 / 方法**：`POST /api/v1/{module}/{resource}`
- **鉴权与隔离**：Bearer Token + Tenant Header
- **幂等**：是 / 否（否须标明不可安全重试）；键来源与保留期：
- **分页**：列表是否支持（page/pageSize 或 cursor）

---

## 2. 请求定义 (Request)

### Headers
| Header 名 | 类型 | 必填 | 描述 |
|---|---|---|---|
| `X-Trace-Id` | String | 是 | 全链路追踪 ID |
| `X-Tenant-Id` | String | 是 | 租户隔离 ID |

### Body (JSON Schema)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["item_id", "quantity"],
  "properties": {
    "item_id": { "type": "string", "description": "商品唯一标识" },
    "quantity": { "type": "integer", "minimum": 1, "description": "购买数量" }
  }
}
```

---

## 3. 响应定义 (Response)

### 成功响应 (HTTP 200)
```json
{
  "code": "SUCCESS",
  "msg": "操作成功",
  "data": {
    "order_id": "ord_1029384756",
    "status": "CREATED"
  }
}
```

### 失败响应 (HTTP 4xx / 5xx)
```json
{
  "code": "STOCK_LOCK_FAILED",
  "msg": "库存不足，锁定失败",
  "retryable": false,
  "details": {
    "item_id": "item_123",
    "available": 0
  }
}
```
