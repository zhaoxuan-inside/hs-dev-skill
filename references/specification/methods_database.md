# 2. 个人开发规范

**何时读**：处理2. 个人开发规范时；先沿用[入口公共约束](../spec_v2_4.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 2. 个人开发规范

### 2.1 基本原则

1. 零死代码、零桩代码；
2. 配置与代码分离，禁止硬编码；
3. DDD 架构边界，模块自治，只访问自己的库和表；
4. 方法长度 20–40 行，超长强制拆分；
5. 逻辑控制与数据处理分离；
6. 通用控制逻辑沉淀到公共模块。

### 2.2 六元组标准化方法签名

```text
exception method_name(input, output, context, isolate, metrics, recall);
exception method_name_fallback(input, output, context, isolate, metrics, recall);
exception method_name_compensate(input, output, context, isolate, metrics, recall);
exception method_name_metrics(input, output, context, isolate, metrics, recall);
exception method_name_recall(input, output, context, isolate, metrics, recall);
```

| 字段 | 含义 | 约束 |
|---|---|---|
| `exception` | 执行结果状态 | 成功时为 `null` / `None` / `Ok(())`；失败时为 map/struct，含 `code`、`msg`、`retryable`、`details` |
| `input` | 输入 | 扁平化键名或类型载荷，如 `user.profile.age` |
| `output` | 输出 | 扁平化键名或容器对象 |
| `context` | 运行时上下文 | traceId、时间戳等；补偿/降级时挂载 `context.last_exception` |
| `isolate` | 隔离与安全 | 只读，包含 `tenant_id`、安全凭据等，严格限制透传 |
| `metrics` | 度量统计 | 耗时、计数、链路 |
| `recall` | 回调控制器 | 封装流程挂起、重试、安全与事件回调控制器 |

**异常结构标准**：

```json
{
  "code": "ORDER_STOCK_LOCK_TIMEOUT",
  "msg": "库存服务响应超时",
  "retryable": true,
  "details": {}
}
```

### 2.3 数据库设计与迁移规范

强制字段：
* `id`：主键（BIGINT / UUID）
* `created_at`：创建时间（UTC 时间戳 / DATETIME(6)）
* `updated_at`：更新时间（UTC 时间戳 / DATETIME(6)）
* `description`：描述与备注（**禁止使用 SQL 保留关键字 `desc`**）
* `is_del`：软删除标记（`0` 未删，大于 0 表示已删）
* `version`：乐观锁版本（默认 `1`，自增递增）

外键命名：`{table_name}_id`。

表设计文档必须包含：当前表结构表格、按版本倒序的变更历史、对应 V/U 脚本路径。
Design、V、U 三者原子同步。

迁移脚本命名：
```text
V{主}.{次}.{补丁}__{描述}.sql
U{主}.{次}.{补丁}__{描述}.sql
```

---
