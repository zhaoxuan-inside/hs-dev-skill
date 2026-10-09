# 方法设计规范：payment_process

## 1. 业务主方法 (Core Method)
- **方法名称**：`payment_process`
- **签名**：`exception payment_process(input, output, context, isolate, metrics, recall)`
- **功能描述**：扣减用户账户资金，并向渠道网关发起扣款

### input / output
- `input.payment.order_id` (String, 必填)
- `input.payment.amount` (Decimal, 必填)
- `output.payment.id` (String)
- `output.payment.status` (String)

---

## 2. 事务补偿方法 (Compensate Method)
- **方法名称**：`payment_process_compensate`
- **签名**：`exception payment_process_compensate(input, output, context, isolate, metrics, recall)`
- **功能描述**：渠道扣款失败或超时时，解冻用户账户资金并标记流水失败

---

## 3. 异常降级方法 (Fallback Method)
- **方法名称**：`payment_process_fallback`
- **签名**：`exception payment_process_fallback(input, output, context, isolate, metrics, recall)`
- **功能描述**：网关熔断时将订单推入异步支付对账重试队列
