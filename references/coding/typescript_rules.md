# 4.3 TypeScript 范式

**何时读**：处理4.3 TypeScript 范式时；先沿用[入口公共约束](../coding_standards.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
### 4.3 TypeScript 范式
```typescript
export interface InOrderCreate {
  readonly userId: string;
  readonly productId: string;
  readonly quantity: number;
}

export interface RequestContext { readonly traceId: string; }
export interface MetricsCollector { increment(name: string): void; }
export interface RecallController { resume(operationId: string): Promise<void>; }

export interface OutOrderCreate {
  orderId?: string;
  totalAmount?: number;
}

export interface SecurityIsolate {
  readonly tenantId: string;
  readonly roles: readonly string[];
}

export interface BizError {
  code: string;
  msg: string;
  retryable: boolean;
}

export function createOrder(
  input: InOrderCreate,
  output: OutOrderCreate,
  isolate: SecurityIsolate,
  context: RequestContext,
  metrics: MetricsCollector,
  recall: RecallController,
): BizError | null {
  if (input.quantity <= 0) {
    return { code: "INVALID_QUANTITY", msg: "购买数量必须大于0", retryable: false };
  }
  output.orderId = "ord_1001";
  output.totalAmount = 99.0;
  return null;
}
```

---

## 5. 语言规则库的检索与动态装载

当需要深入某一特定语言或框架的最新权威规范时，通过 `rule_fetch.py` 进行局部检索与解析：

```bash
# 检索 Go 语言编码规范与并发安全
python scripts/rule_fetch.py search --q Go

# 检索 Java 阿里规约与并发规范
python scripts/rule_fetch.py search --q Java

# 检索 Python PEP8 与 Ruff 规范
python scripts/rule_fetch.py search --q Python

# 检索 Rust API 指南
python scripts/rule_fetch.py search --q Rust

# 检索 Vue 3 风格指南
python scripts/rule_fetch.py search --q Vue

# 检索 React / Next 性能最佳实践
python scripts/rule_fetch.py search --q React
```

在获取切片后，遵循**“每任务加载规则源 ≤ 2 个”**的 Token 纪律，针对性吸收，杜绝全文搬运。
