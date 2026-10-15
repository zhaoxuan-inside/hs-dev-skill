# 接口设计文档：payment_process

## 1. 接口元数据
- **接口名称**：`payment_process`
- **协议**：RESTful JSON POST
- **路径**：`POST /api/v1/payment/process`

---

## 2. 请求定义
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["order_id", "amount", "channel"],
  "properties": {
    "order_id": { "type": "string" },
    "amount": { "type": "number", "minimum": 0.01 },
    "channel": { "type": "string", "enum": ["ALIPAY", "WECHAT", "MOCK"] }
  }
}
```

---

## 3. 响应定义
```json
{
  "code": "SUCCESS",
  "msg": "支付处理成功",
  "data": {
    "payment_id": "pay_987654321",
    "status": "SUCCESS"
  }
}
```
