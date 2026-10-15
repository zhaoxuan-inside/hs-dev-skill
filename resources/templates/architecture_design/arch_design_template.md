# 架构设计文档：{name}

- **产品/域名称**：{name}
- **产品类型 / 规模**：{CRUD | 标准产品 | 复杂域 | …} / {小 | 中 | 大}
- **选定范式**：后端 {B0～B7} + 前端 {F0～F4}（见 `references/dev_paradigm.md`）
- **架构模式**：{事务脚本 | 模块化单体 | Hexagonal | DDD 轻量/完整 | 微服务 | …} / 前端 {按页 | Feature | FSD}
- **指导详规**：`dev_paradigm.md` →（按档）`ddd_design` / `backend_arch` / `frontend_arch`
- **更新日期**：{YYYY-MM-DD}

---

## [VIBE_CONTRACT] 架构执行契约 (Machine-Actionable Architecture)
<!-- 
  【专供 VibeCoding / AI 编码切片读取（行 10～40）】
  说明：本区块记录锁定的范式阶梯、模块根路径映射与硬性依赖禁令。
  AI 编码切片直接读取本区块，作为代码组织与 import 依赖的绝对红线！
-->
```yaml
architecture_contract:
  domain_name: "{name}"
  paradigm:
    backend_tier: "{B0～B7，如 B1 事务脚本 / B2 模块化单体 / B4 Hexagonal / B5 DDD}"
    frontend_tier: "{F0～F4，如 F1 组件化 / F2 Feature模块 / F3 FSD}"
  module_path_map:
    core_logic: "backend/{module}/domain"
    application_services: "backend/{module}/app"
    infrastructure_adapters: "backend/{module}/infra"
    api_entrypoints: "backend/{module}/interfaces"

dependency_rules:
  - "RULE: 依赖方向严禁向外倒流！domain 层严禁 import infra 或 interfaces"
  - "RULE: 模块间通信严禁私自跨库直连，必须通过显式 API 或 Seam Adapter"
```

---

## 0. 范式选型与权衡 (Human Rationale)

| 项 | 值 |
|----|-----|
| 复杂度信号 | {规则密度 / 集成数 / 一致性 / …} |
| 后端阶 | B? — {名称} |
| 前端阶 | F? — {名称} |
| 为何不升级 | |
| 为何不降级 | |

非 DDD 档：跳过 §1/§4 的 BC/聚合表，用 §1b 模块图即可。

---

## 1. 边界设计

### 1a. （DDD 档）限界上下文与映射

```mermaid
graph LR
    UserContext[用户上下文] -->|ACL| OrderContext[订单上下文]
    OrderContext -->|事件| PaymentContext[支付上下文]
```

| 上游 | 下游 | 关系（ACL/OHS/…） | 集成方式 | 备注 |
|------|------|-------------------|----------|------|
| | | | | |

| 类型 | 上下文 | 说明 |
|------|--------|------|
| Core / Supporting / Generic | | |

### 1b. （非 DDD）业务模块图

```mermaid
graph LR
    Auth[认证模块] --> Catalog[目录模块]
    Catalog --> Order[订单模块]
```

| 模块 | 职责 | 依赖 | 数据归属 |
|------|------|------|----------|
| | | | |

---

## 2. 统一语言（摘录）

| 术语 | 定义 | 禁止别名 | 所在模块/上下文 |
|------|------|----------|-----------------|
| | | | |

完整词典：`_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml`。

---

## 3. 分层与职责（按选定后端阶裁剪）

```text
Interfaces / Controller / Gateway
Application / Orchestrator（六元组 method）
Domain 或 Service（按阶：B1 可为事务脚本；B4+ 为领域模型）
Infrastructure / Repo / RPC
```

依赖**只向内**。前端映射见 §6。

---

## 4. （DDD 档）核心聚合与实体

| 名称 | 角色（根/实体/VO） | 身份/键 | 不变量 / 状态跃迁 | 仓储 |
|------|-------------------|---------|-------------------|------|
| | | | | |

非 DDD：改为「核心实体/表与不变量」简表即可。

---

## 5. 关键用例 → 六元组

| 用例 | 模块/上下文 | method | compensate | fallback | 说明 |
|------|-------------|--------|------------|----------|------|
| | | | | | |

---

## 6. 前端架构对齐

| 后端模块/上下文 | 前端 feature / slice | 页面/路由 | 状态来源（BFF/API） |
|-----------------|----------------------|-----------|---------------------|
| | | | |

前端阶：{F0～F4}；细则见 `frontend_arch.md`。

---

## 7. 决策与禁忌

- **Do**：
- **Don't**：
- 相关 ADR：`_00_project_foundation/_03_decision_record/ADR_{xxx}.md`
