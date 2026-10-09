# 方法设计规范模板：{method_name}

## 1. 业务主方法 (Core Method)
- **方法名称**：`{method_name}`
- **签名**：`exception {method_name}(input, output, context, isolate, metrics, recall)`
- **功能描述**：{简述该方法的业务职责与核心流程}

### 1.1 input 入参规范
| 字段路径 | 类型 | 取值范围 / 格式 | 可空 | 描述 |
|---|---|---|---|---|
| `{entity}.id` | String | UUID / Snowflake | 否 | 实体唯一标识 |
| `{entity}.amount` | Decimal | (0, 99999999.99] | 否 | 交易金额 |

### 1.2 output 出参规范
| 字段路径 | 类型 | 取值范围 / 格式 | 可空 | 描述 |
|---|---|---|---|---|
| `{entity}.status` | String | ENUM: CREATED, PAID | 否 | 状态 |

### 1.3 context 上下文依赖
| 字段路径 | 类型 | 描述 |
|---|---|---|
| `context.trace_id` | String | 链路追踪 ID |
| `context.deadline` | Timestamp | 超时时间截点 |

### 1.4 isolate 隔离约束
| 字段路径 | 类型 | 约束说明 |
|---|---|---|
| `isolate.tenant_id` | String | 多租户隔离 ID，只读 |

---

## 2. 事务补偿方法 (Compensate Method)
- **方法名称**：`{method_name}_compensate`
- **签名**：`exception {method_name}_compensate(input, output, context, isolate, metrics, recall)`
- **触发条件**：分布式事务下游失败或 Saga 流程回滚。
- **补偿动作**：释放预占资源、还原业务状态。
- **异常挂载**：`context.last_exception` 携带失败现场信息。

---

## 3. 异常降级方法 (Fallback Method)
- **方法名称**：`{method_name}_fallback`
- **签名**：`exception {method_name}_fallback(input, output, context, isolate, metrics, recall)`
- **触发条件**：主方法熔断、下游不可用且不可重试。
- **降级动作**：返回兜底缓存数据或降级提示。

---

## 4. 度量与回调控制器 (Metrics & Recall)
- **Metrics 埋点**：
  - `{method_name}.duration_ms` (Timer)
  - `{method_name}.call_count` (Counter)
  - `{method_name}.error_count` (Counter)
- **Recall 控制器动作**：
  - 挂起检查点：`checkpoint_id`
  - 异步事件：`event_name`
