# 多语言代码开发规范与静态检查门禁指南 (Multi-Language Coding Standards & Quality Gates)

**何时读**：
- 阶段 1 技术选型后确定语言与 Linter 规范；
- 阶段 3 详细设计中编写跨语言接口签名与异常体系；
- 阶段 5 编码与测试实现（编写 Go、Python、Rust、Java/Kotlin、TypeScript/Vue/React 等多语言代码）；
- 提交前排查消除 Linter 告警与代码坏味道；
- 检索命令：`python3 scripts/skill_ref_index.py search --scenario 开发规范` 或 `search --q 语言规范`

---

## 1. 核心理念：跨语言三层防护体系

在 AI 辅助编程（VibeCoding）时代，单纯向大模型全量灌输动辄上百页的语法指南（如阿里 Java 开发手册、PEP 8、Effective Go）会导致严重的 Token 膨胀、上下文遗忘与软约束失效。

本 Skill 确立**跨语言三层防护体系**：

```text
┌────────────────────────────────────────────────────────┐
│  L1: 语言无关架构元模型 (Language-Agnostic Invariants) │
│      七大方法标准模型 · 六元组运行时 · 深模块防腐 · V/U 原子同步│
├────────────────────────────────────────────────────────┤
│  L2: 语言原生工具链硬门禁 (Tooling & Linter Hard Gate) │
│      Zero Warnings / Zero Errors · 退出码非零强制阻断   │
├────────────────────────────────────────────────────────┤
│  L3: 语言/框架最佳实践 (On-Demand Sliced Rules)        │
│      rule_sources.yaml 注册 · rule_fetch 按需切片 ≤2 源│
└────────────────────────────────────────────────────────┘
```

1. **L1 架构元模型不变量（顶层设计同构）**：不论使用哪种后端或前端语言，业务方法的抽象、接口契约、安全隔离和状态跃迁必须遵守统一的软件工程哲学。
2. **L2 原生工具链硬门禁（物理严格裁决）**：语言对应的编译器、类型检查器、静态代码分析器（Linter）拥有最高裁决权。**0 Warning 0 Error 是铁律**。
3. **L3 语言最佳实践按需切片（防 Token 膨胀）**：特定框架的细粒度 Idiomatic Rules 通过 `rule_fetch.py` 按需检索 10～30 行切片注入，严禁整库灌入。

---

## 2. 多语言静态检测与 Linter 门禁矩阵表

项目必须在根目录的 `Makefile`、`package.json` 或构建脚本中集成对应语言的标准检测命令，并纳入 `make test` 执行链。任何 Warning 均视为致命阻断项：

| 语言/生态 | 官方/行业推荐工具链 | 强制执行命令（0 告警 0 错误） | 核心拦截范畴 |
|---|---|---|---|
| **Python** | `Ruff` + `Mypy` | `ruff check . && mypy .` | PEP 8 风格、未捕获异常、未用导入、强类型推断与 None 检查 |
| **Go** | `golangci-lint` + `go vet` | `golangci-lint run ./... && go vet ./...` | 错误处理丢弃 (`errcheck`)、Goroutine 泄漏、锁并发竞态、Shadowing |
| **Rust** | `cargo clippy` + `rustfmt` | `cargo clippy --all-targets -- -D warnings && cargo test` | 生命周期悬垂、未处理 Result/Option、内存借用越界、Unsafe 滥用 |
| **TypeScript / Node** | `ESLint` + `tsc` | `eslint . --max-warnings 0 && tsc --noEmit` | `any` 泛滥、Promise 未 await/catch、解构空指针、类型漂移 |
| **React / Next.js** | `ESLint (React Hooks / Next)` | `eslint . --max-warnings 0` | Hook 依赖缺失、服务端组件缓存失效、水合不一致、无障碍 ARIA |
| **Vue.js 3** | `eslint-plugin-vue` + `vue-tsc` | `eslint . --ext .vue,.ts --max-warnings 0 && vue-tsc --noEmit` | 响应式解构丢失 (`toRefs`)、组件 Props 校验、Template 语法坏味道 |
| **Java** | `Checkstyle` + `SpotBugs` | `mvn checkstyle:check spotbugs:check` | 阿里规约/Google 规约违规、空指针隐患、线程池未受控、资源未释放 |
| **Kotlin / Android** | `Detekt` + `Android Lint` | `./gradlew detekt lint` | 协程上下文泄漏、不可变状态破坏、Compose 重组性能陷阱 |
| **C# / .NET** | `dotnet format` + Roslyn | `dotnet build /warnaserror` | 空引用注解 (Nullable)、异步死锁 (`.Result`)、LINQ 隐式性能消耗 |

---

## 3. 跨语言零容忍代码坏味道清单 (Zero-Tolerance Code Smells)

无论选用何种语言，以下代码坏味道在 `hs-dev-skill` 中均属**绝对禁止事项**：

### 3.1 异常与错误处理 (Error Handling)
- ❌ **严禁吞咽异常**：禁止空的 `catch`/`except` 块或 `_ = err`（Go 中忽略错误）。
- ❌ **严禁打印后不处理**：禁止仅仅调用 `print(e)` / `e.printStackTrace()` / `console.log(e)` 而不向上抛出或降级返回。
- ❌ **严禁丢失原始上下文**：抛出新异常时必须链式包裹原异常（如 Python `raise ... from e`，Java `new BizException(msg, cause)`）。

### 3.2 并发、异步与资源生命周期 (Concurrency & Resources)
- ❌ **严禁未受控并发**：严禁裸跑未经管理的 Goroutine 或 `new Thread()`，必须通过有界线程池、TaskGroup 或 Worker 机制。
- ❌ **严禁浮动 Promise / 悬空协程**：前端与 Node 中严禁出现未 `await` 或未 `.catch()` 的浮动 Promise；Go 中严禁缺少 `context.Context` 超时控制的外部 I/O。
- ❌ **严禁资源泄漏**：文件句柄、数据库连接、HTTP Response Body、互斥锁必须使用语言原生的 RAII/作用域管理器（Go `defer`、Python `with`、Java `try-with-resources`、Rust 所有权）。

### 3.3 安全与防注入 (Security by Default)
- ❌ **严禁 SQL 字符串拼接**：必须使用参数化查询或 ORM 安全绑定，严禁 `fmt.Sprintf("SELECT ... %s", input)`。
- ❌ **严禁凭证硬编码**：API Key、数据库密码、Token 绝不上库，必须从环境变量读取并提供 `.env.example` 声明。
- ❌ **严禁反射与绕过封装**：禁止为了测试或偷懒而通过反射修改私有变量或跳过校验守卫。

### 3.4 命名统一性、词态矩阵与单一事实源 (Ubiquitous Language & Naming Invariants)
开发与 AI 生成过程中，极易出现**同义不同词、词态混淆与语义漂移（Semantic Drift）**（例如同一个更新概念，在指令中叫 `update`，事件中叫 `order.update`，时间戳叫 `updated_at`，甚至派生出 `modify`、`change`、`alter` 等同义词），导致全局代码检索断裂、监听漏网和维护灾难。

本 Skill 强制执行以下四项命名守卫法则：

1. **三概念严格解耦与词态矩阵 (Grammar Matrix)**：
   - **Command（动作/指令）**：必须使用**动词原形**（如 `update_order` / `create_user`）。表示请求尚未执行，可能会被拒绝。
   - **Domain Event（领域事件）**：必须使用**过去分词**（如 `order.updated` / `user.created` 或 PascalCase `OrderUpdated`）。表示系统内已客观发生的事实，只读通知。**严禁使用动词原形（如 `order.update`）作为事件名；严禁把时间戳属性作为事件名**。
   - **Entity Attribute（实体属性/时间戳）**：时间戳必须统一使用**过去分词 + `_at`**（如 `created_at`、`updated_at`、`deleted_at`），只作为数据列，禁止用作动作或事件标识。
   - **Payload Action（变更日志类型）**：CDC / Webhook 变更类型统一使用**全大写**（如 `CREATE`、`UPDATE`、`DELETE`）。
2. **Search-Before-Name 铁律（先搜已有命名，再做新定义）**：
   - 开发者或 AI Agent 在引入新的事件名、错误码、状态字段或公共常量前，**必须先检索现有代码库与 `hs_dev_docs/_00_project/_02_project_word.dict.yaml`**。
   - 若已有约定词汇，必须直接复用；严禁随意发明 `modify`、`change`、`alter`、`renew`、`bill_order` 等同义别名。
3. **零裸字符串与单一事实源 (Zero Magic Strings & Single Source of Truth)**：
   - 跨模块或跨服务调用的事件主题（Topic）、状态机枚举、通知类型，**严禁在业务逻辑中直接硬编码裸字符串**。
   - 必须通过集中常量文件收敛导出（如 TS `events.ts`、Python `events.py`、Go `events.go`）。全局搜索时只需定位常量引用符号，杜绝字符串漏搜。
4. **项目词典与自动化门禁硬拦截**：
   - 核心领域词汇、标准缩写与禁用同义词列表统一登记在 `_00_project/_02_project_word.dict.yaml`。
   - 提交前 `verify_consistency.py` 将自动扫描代码库与 SQL 迁移文件，命中 `forbidden_alias` 或事件动词原形时直接阻断门禁。

### 3.5 方法爆炸与影子函数禁令 (Anti-Method Explosion & Shadow Functions)
AI 辅助编程（VibeCoding）最容易落入“只建不选、方法爆炸”的陷阱。以下行为在本项目中**一律视为代码坏味道并阻断合并**：
- ❌ **严禁未经检索直接新建辅助方法**：编写任何通用转换（`TRANSFORM`）、算法（`ALGO`）、守卫（`GUARD`）或适配逻辑前，**严禁凭空新建函数**。必须首先调用 `python scripts/doc_index_db.py method-search --q <业务意图>` 检索现有方法画像。
- ❌ **严禁同义影子函数 (Shadow Functions)**：若已有方法已覆盖 ≥80% 逻辑，**严禁创建 `formatDate2`、`parseUserCustom`、`validateMobileHelper` 等近义变体**。必须采用可选入参（Options Pattern / Overload）扩展旧函数并保持单测兼容。
- ❌ **严禁浅透传与过度微小抽取 (Shallow Modules)**：严禁为了盲目追求“单一职责”将仅有 1~3 行且全仓仅使用一次的代码抽取为公共方法。遵循深模块原则与三次原则（Rule of Three），单次使用的轻微逻辑**强制就地内联（Inline）**。

---

## 4. 六元组与方法分类在主流语言中的实现范式 (Polyglot Six-Tuple)

六元组签名：$$\text{Method}(Input, Output, Context, Isolate, Metrics, Recall) \to Exception$$

### 4.1 Go 语言范式
```go
package domain

import (
	"context"
	"errors"
)

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

### 4.2 Python 语言范式
```python
from dataclasses import dataclass
from typing import Optional, List

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
    context: Optional[dict] = None
) -> Optional[BizException]:
    if in_dto.quantity <= 0:
        return BizException("INVALID_QUANTITY", "购买数量必须大于0", retryable=False)
    
    out_dto.order_id = "ord_1001"
    out_dto.total_amount = 99.0
    return None
```

### 4.3 TypeScript 范式
```typescript
export interface InOrderCreate {
  readonly userId: string;
  readonly productId: string;
  readonly quantity: number;
}

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
python3 scripts/rule_fetch.py search --q Go

# 检索 Java 阿里规约与并发规范
python3 scripts/rule_fetch.py search --q Java

# 检索 Python PEP8 与 Ruff 规范
python3 scripts/rule_fetch.py search --q Python

# 检索 Rust API 指南
python3 scripts/rule_fetch.py search --q Rust

# 检索 Vue 3 风格指南
python3 scripts/rule_fetch.py search --q Vue

# 检索 React / Next 性能最佳实践
python3 scripts/rule_fetch.py search --q React
```

在获取切片后，遵循**“每任务加载规则源 ≤ 2 个”**的 Token 纪律，针对性吸收，杜绝全文搬运。
