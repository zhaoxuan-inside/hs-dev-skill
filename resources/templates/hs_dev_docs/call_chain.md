# 调用链与拓扑分析：{call_source}

## 1. 概览
- **调用源**：`{call_source}`（例如：`http:POST /api/v1/order/create`、`mq:order_paid_event`、`cron:daily_settlement`）
- **触发类型**：HTTP Request / MQ Message / Cron Job / RPC Call
- **所属端**：Backend / Frontend / Worker

---

## 2. 调用时序与拓扑图 (Call Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Gateway as API Gateway
    participant OrderCtrl as OrderController
    participant OrderSvc as OrderService
    participant StockRpc as StockClient (RPC)
    participant OrderRepo as OrderRepository (DB)

    Client->>Gateway: POST /api/v1/order/create
    Gateway->>OrderCtrl: Forward with Trace & Tenant
    OrderCtrl->>OrderSvc: order_create(input, output, ctx, iso, met, rec)
    OrderSvc->>StockRpc: stock_lock(itemId, qty)
    alt Stock Locked
        OrderSvc->>OrderRepo: insert(order)
        OrderSvc-->>OrderCtrl: return null (Success)
        OrderCtrl-->>Client: 200 OK (orderId)
    else Stock Failed / Timeout
        OrderSvc->>OrderSvc: order_create_compensate(...)
        OrderSvc-->>OrderCtrl: return Exception
        OrderCtrl-->>Client: 400 Bad Request / 504 Timeout
    end
```

---

## 3. 依赖方法清单 (Method Dependency List)

| 方法名 | 所属模块/服务 | 职责 | 失败策略 | 豁免注解 |
|---|---|---|---|---|
| `order_create` | `order` | 订单创建主方法 | 触发补偿 | - |
| `stock_lock` | `inventory` | 锁定库存 | 重试 2 次后熔断 | - |
| `order_insert` | `order` | 落库持久化 | 事务回滚 | - |
