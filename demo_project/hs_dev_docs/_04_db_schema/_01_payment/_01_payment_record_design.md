# 数据表设计文档：payment_record

## 1. 表基础信息
- **表名**：`payment_record`
- **说明**：支付流水记录表
- **所属模块**：`payment`

---

## 2. 字段定义

| 字段名 | 类型 | 长度/精度 | 允许空 | 默认值 | 说明 |
|---|---|---|---|---|---|
| `id` | BIGINT | - | 否 | - | 流水主键 ID |
| `created_at` | TIMESTAMP | - | 否 | CURRENT_TIMESTAMP | 创建时间 (UTC) |
| `updated_at` | TIMESTAMP | - | 否 | CURRENT_TIMESTAMP | 更新时间 (UTC) |
| `description`| VARCHAR | 255 | 是 | '' | 业务描述与备注 (无SQL保留字冲突) |
| `is_del` | BIGINT | - | 否 | 0 | 软删除标记 (0:未删, >0:删除时间戳) |
| `version` | INT | - | 否 | 1 | 乐观锁版本号 |
| `order_id` | VARCHAR | 64 | 否 | - | 关联业务订单 ID |
| `amount` | DECIMAL | (18,2) | 否 | 0.00 | 支付金额 |
| `status` | VARCHAR | 32 | 否 | 'PENDING' | 支付状态 (PENDING/SUCCESS/FAILED/REFUNDED) |

---

## 3. 迁移脚本映射
| 版本号 | 脚本类型 | 脚本文件路径 | 描述 |
|---|---|---|---|
| `V1.0.0` | 前向迁移 | `migrations/V1.0.0__init_payment_record.sql` | 初始化 payment_record 表结构 |
| `U1.0.0` | 回滚脚本 | `migrations/U1.0.0__init_payment_record.sql` | 删除 payment_record 表 |
