# 六元组标准化运行时详细指南

## 1. 六元组核心设计理念

六元组（Six-Tuple Architecture）是面向高可靠、分布式微服务以及复杂业务编排的标准方法签名与运行时模型。它将业务调用的各个关注点彻底正交解耦：

$$\text{Method}(Input, Output, Context, Isolate, Metrics, Recall) \to Exception$$

```text
       ┌───────────┐       ┌────────────┐
       │   Input   │       │   Output   │
       └─────┬─────┘       └─────▲──────┘
             │                   │
      ┌──────▼───────────────────┴──────┐
      │          Core Method            │ ───► Exception (Result Status)
      └──────┬──────────┬────────┬──────┘
             │          │        │
       ┌─────▼─────┐ ┌──▼───┐ ┌──▼───┐
       │  Context  │ │Isolat│ │Recall│
       └───────────┘ └──────┘ └──────┘
             │
       ┌─────▼─────┐
       │  Metrics  │
       └───────────┘
```

---

## 2. 六元组参数详细规范

| 字段 | 类型/结构 | 访问权限 | 职责与规范 |
|---|---|---|---|
| `exception` | `ExceptionObject \| null` | 返回值 | 执行状态：成功返回 `null`/`None`/`Ok(())`；失败返回标准异常对象，包含 `code`、`msg`、`retryable`、`details`。 |
| `input` | `Struct / Map / DTO` | 只读 (Read-Only) | 业务入参载荷。采用扁平化键名或类型定义，严禁在方法内修改 `input` 原对象。 |
| `output` | `Struct / Map / Container` | 可写 (Write-Only/Out) | 业务出参载荷容器。方法执行成功后将计算结果写入 `output`。 |
| `context` | `RuntimeContext` | 读写 | 跨方法与链路透传上下文：`trace_id`、`span_id`、`deadline`、`baggage`。降级/补偿时注入 `context.last_exception`。 |
| `isolate` | `SecurityIsolate` | 只读 (Strict Read-Only) | 租户与安全隔离层：`tenant_id`、`user_id`、`data_scope`、`auth_claims`。禁止向不可信下游透传。 |
| `metrics` | `MetricsCollector` | 可追加 | 性能与可观测性收集器：耗时统计、计数器、业务指标上报。 |
| `recall` | `RecallController` | 可调用 | 流程控制器与回调网关：用于长事务挂起（Suspend）、异步唤醒（Resume）、权限重验或事件广播。 |

---

## 3. 标准异常结构（Exception Schema）

```json
{
  "code": "ORDER_STOCK_LOCK_TIMEOUT",
  "msg": "下游库存锁定服务响应超时",
  "retryable": true,
  "details": {
    "item_id": "item_123456",
    "requested_qty": 2,
    "elapsed_ms": 3050
  }
}
```

- `code`（string, 必填）：大写下划线语义化错误码，全局唯一且具可读性。
- `msg`（string, 必填）：面向开发者/运维的简要错误描述。
- `retryable`（boolean, 必填）：标识该错误是否支持安全幂等重试（如网络超时可重试，校验失败不可重试）。
- `details`（object, 可选）：上下文故障现场快照。

---

## 4. 五大衍生方法规范

对于每个核心业务方法 `method_name`，定义 5 个标准方法：

1. **`method_name`（业务主方法）**：执行核心正向业务逻辑。
2. **`method_name_fallback`（降级方法）**：当主方法或下游服务不可用且不可重试时触发，返回兜底数据或默认状态。入参由 `context.last_exception` 获取失败原因。
3. **`method_name_compensate`（补偿/回滚方法）**：分布式事务（Saga 模式）或部分步骤失败时的逆向操作，用于释放锁、退款、撤销状态变更。
4. **`method_name_metrics`（度量方法）**：专用度量与健康检查拦截器，用于自定义吞吐量、业务 SLA 聚合。
5. **`method_name_recall`（回调/挂起方法）**：异步任务或多步审批中的状态流转唤醒钩子。

---

## 5. 多语言落地代码模式

### TypeScript / Node.js
```typescript
export interface SixTupleException {
  code: string;
  msg: string;
  retryable: boolean;
  details?: Record<string, unknown>;
}

export interface SixTupleContext {
  traceId: string;
  spanId: string;
  deadlineMs?: number;
  lastException?: SixTupleException;
  baggage: Record<string, string>;
}

export interface SecurityIsolate {
  readonly tenantId: string;
  readonly userId?: string;
  readonly roles: readonly string[];
}

export interface MetricsCollector {
  recordTimer(name: string, durationMs: number): void;
  increment(name: string, count?: number): void;
}

export interface RecallController {
  suspend(checkpointId: string): void;
  triggerHook(eventName: string, payload: unknown): void;
}

// 主方法签名
export async function orderCreate(
  input: { userId: string; itemId: string; quantity: number },
  output: { orderId?: string; status?: string },
  context: SixTupleContext,
  isolate: SecurityIsolate,
  metrics: MetricsCollector,
  recall: RecallController
): Promise<SixTupleException | null> {
  const start = Date.now();
  try {
    // 1. 业务逻辑
    output.orderId = "ord_" + Math.random().toString(36).substring(2, 10);
    output.status = "CREATED";
    metrics.increment("order.create.success");
    return null;
  } catch (err: any) {
    metrics.increment("order.create.failure");
    return {
      code: "ORDER_CREATE_ERROR",
      msg: err.message || "Failed to create order",
      retryable: false,
    };
  } finally {
    metrics.recordTimer("order.create.duration", Date.now() - start);
  }
}
```

### Go
```go
type SixTupleException struct {
	Code      string                 `json:"code"`
	Msg       string                 `json:"msg"`
	Retryable bool                   `json:"retryable"`
	Details   map[string]interface{} `json:"details,omitempty"`
}

type SixTupleContext struct {
	TraceID       string
	SpanID        string
	LastException *SixTupleException
	Baggage       map[string]string
}

func OrderCreate(
	in *OrderCreateInput,
	out *OrderCreateOutput,
	ctx *SixTupleContext,
	iso *SecurityIsolate,
	met MetricsCollector,
	rec RecallController,
) *SixTupleException {
	// 核心逻辑
	out.OrderID = "ord_12345"
	out.Status = "CREATED"
	return nil
}
```

---

## 6. 与方法类型契约画像（Method Archetypes）的深度融合

六元组是服务间与关键用例的标准调用骨架，而在代码编写与维护中，每个六元组方法（主方法、补偿、降级等）以及其内部调用的子方法均应挂载**方法类型画像与属性契约**（详见 [`method_archetypes.md`](method_archetypes.md)）：

1. **类型分治**：
   - 用例级六元组主方法通常属于 **`ORCHESTRATE`**（编排层），负责串联调用 `TRANSFORM`、`ALGO` 与 `ADAPTER`；
   - 内部纯计算、计价、加解密逻辑必须剥离为独立的 **`ALGO`** 纯函数，禁止混杂在带 I/O 的方法体中；
   - 权限越权拦截与前置条件校验提取为 **`GUARD`**；
   - 外部数据库与微服务 RPC 调用统一封装为 **`ADAPTER`**。
2. **文档定义代码与物理定位**：
   - 在 `hs_dev_docs/_04_engineering_contract/_04_method_design/` 中完整登记该六元组方法的物理行号坐标、敏感度理由、副作用类型与以本方法为中心的局部依赖拓扑图。
3. **精准跑测与 Token 节约**：
   - 改动该方法时，依据画像属性直跑指定单测或契约测试命令，杜绝全量跑测与全量代码扫描。
