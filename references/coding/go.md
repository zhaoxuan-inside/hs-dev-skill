# 4. 六元组与方法分类在主流语言中的实现范式 (Polyglot Six-Tuple)

**何时读**：处理4. 六元组与方法分类在主流语言中的实现范式 (Polyglot Six-Tuple)时；先沿用[入口公共约束](../coding_standards.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 4. 六元组与方法分类在主流语言中的实现范式 (Polyglot Six-Tuple)

六元组签名：$$\text{Method}(Input, Output, Context, Isolate, Metrics, Recall) \to Exception$$

以下示意业务方法的参数与异常边界；`MetricsCollector` 和 `RecallController` 在实际项目中使用已选运行时提供的接口。

### 4.1 Go 语言范式
```go
package domain

import (
	"context"
)

type MetricsCollector interface { Increment(name string) }
type RecallController interface { Resume(operationID string) error }

// InOrderCreate 入参结构体（只读契约）
type InOrderCreate struct {
	UserID    string `json:"user_id"`
	ProductID string `json:"product_id"`
	Quantity  int    `json:"quantity"`
}

// OutOrderCreate 出参容器（方法负责填充）
type OutOrderCreate struct {
	OrderID     string  `json:"order_id"`
	TotalAmount float64 `json:"total_amount"`
}

// SecurityIsolate 租户与安全隔离
type SecurityIsolate struct {
	TenantID string
	Roles    []string
}

// BizError 标准业务异常
type BizError struct {
	Code      string `json:"code"`
	Msg       string `json:"msg"`
	Retryable bool   `json:"retryable"`
}

func (e *BizError) Error() string { return e.Msg }

// CreateOrder 六元组方法实现 (TRANSFORM / ORCHESTRATE)
func CreateOrder(
	ctx context.Context,
	in InOrderCreate,
	out *OutOrderCreate,
	iso SecurityIsolate,
	metrics MetricsCollector,
	recall RecallController,
) *BizError {
	if in.Quantity <= 0 {
		return &BizError{Code: "INVALID_QUANTITY", Msg: "购买数量必须大于0", Retryable: false}
	}
	// 业务逻辑实现...
	out.OrderID = "ord_1001"
	out.TotalAmount = 99.0
	return nil
}
```
