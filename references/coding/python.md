# 4.2 Python 语言范式

**何时读**：处理4.2 Python 语言范式时；先沿用[入口公共约束](../coding_standards.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
### 4.2 Python 语言范式
```python
from dataclasses import dataclass
from typing import Optional, List, Protocol

class MetricsCollector(Protocol):
    def increment(self, name: str) -> None: ...

class RecallController(Protocol):
    def resume(self, operation_id: str) -> None: ...

@dataclass(frozen=True)  # 严格只读入参
class InOrderCreate:
    user_id: str
    product_id: str
    quantity: int

@dataclass
class OutOrderCreate:
    order_id: str = ""
    total_amount: float = 0.0

@dataclass(frozen=True)
class SecurityIsolate:
    tenant_id: str
    roles: List[str]

@dataclass
class BizException(Exception):
    code: str
    msg: str
    retryable: bool = False

def create_order(
    in_dto: InOrderCreate,
    out_dto: OutOrderCreate,
    isolate: SecurityIsolate,
    context: dict,
    metrics: MetricsCollector,
    recall: RecallController,
) -> Optional[BizException]:
    if in_dto.quantity <= 0:
        return BizException("INVALID_QUANTITY", "购买数量必须大于0", retryable=False)

    out_dto.order_id = "ord_1001"
    out_dto.total_amount = 99.0
    return None
```
