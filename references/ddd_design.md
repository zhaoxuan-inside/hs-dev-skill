# DDD 领域驱动设计指南（范式子集 · 按需）

**何时读**：[`dev_paradigm.md`](dev_paradigm.md) 已选定 **B4/B5（含 DDD）** 之后；新建/调整限界上下文；术语混乱。未选型前**禁止**默认打开本文。每会话最多一次。  
**分工**：本文 = DDD **战略 + 战术 + 前后端映射**；范式总表 → `dev_paradigm`；后端分层/Saga → [`backend_arch.md`](backend_arch.md)；前端切片 → [`frontend_arch.md`](frontend_arch.md)；API → [`api_engineering.md`](api_engineering.md)。

```bash
python scripts/rule_fetch.py search --q DDD
python scripts/rule_fetch.py resolve --id local.ddd.design
python scripts/rule_fetch.py resolve --id ciembor.architecture-books --rule domain-driven-design
python scripts/rule_fetch.py resolve --id ciembor.architecture-books --rule domain-driven-design-distilled
python scripts/rule_fetch.py resolve --id wshobson.architecture-patterns
python scripts/rule_fetch.py resolve --id wshobson.architecture-refs --rule advanced-patterns
```

**溯源**：[ciembor/agent-rules-books](https://github.com/ciembor/agent-rules-books)（Evans / Distilled）· [wshobson/agents](https://github.com/wshobson/agents) · [Sairyss/domain-driven-hexagon](https://github.com/Sairyss/domain-driven-hexagon)（实践对照，勿整读）· 本仓库架构模板。

---

## 1. 何时用 DDD（分档）

| 档 | 信号 | 做法 |
|----|------|------|
| **不用** | CRUD 为主、规则少、单表维护 | 简单分层即可；禁止堆 Aggregate/Factory 仪式 |
| **轻量** | 有状态机/不变量，上下文 ≤2 | 统一语言 + 聚合边界 + 应用层编排 |
| **完整** | 多团队/多模型、集成多、核心域复杂 | 战略切割 + 上下文映射 + 战术齐全 + ADR |

与 `change_size`：S 不新建 DDD 文档；M 只改触达上下文；L 阶段 2 必须落盘战略图 + 词典。不确定 → **默认轻量**。

---

## 2. 战略设计（先于类图）

### 2.1 统一语言（Ubiquitous Language）

- **一上下文一词一义**；代码、测试、PRD、词典同一套名词。  
- 登记：`hs_dev_docs/_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml`（禁止同义多词）。  
- 术语尴尬/需反复翻译 → 先改语言再加行为。

### 2.2 限界上下文（Bounded Context）

```text
1) 从用户价值与业务能力切（订单 / 库存 / 支付…），不是从技术层切
2) 每个上下文有自己的模型；禁止全系统共享一个「上帝 Entity」
3) 跨上下文只暴露：Id / ACL DTO / 领域事件 / 明确应用服务接口
```

**切割启发式**：不同专家用不同定义同一词 → 拆；变更节奏/部署边界不同 → 拆；强一致事务必须同库同聚合 → 合。

### 2.3 上下文映射（必选一种关系）

| 关系 | 何时 |
|------|------|
| **ACL（防腐层）** | 对接外部/遗留/另一上下文模型（默认首选） |
| Customer/Supplier | 上游按下游需求演进 |
| Conformist | 下游被迫服从上游模型 |
| Shared Kernel | 极小共享；需共同治理，慎用 |
| Open Host + Published Language | 对外稳定协议（API/事件契约） |
| Separate Ways | 集成成本高于收益 |

未声明关系就写跨模块 import → **设计失败**。

### 2.4 核心域蒸馏

- **Core Domain**：差异化价值，优先建模与测试。  
- Supporting / Generic：可简化、可买可借，勿与核心抢注意力。

---

## 3. 战术设计（模型驱动实现）

| 构件 | 要点 |
|------|------|
| **Entity** | 稳定身份；用领域方法改状态，禁外部乱设字段 |
| **Value Object** | 不可变、由属性定义相等；校验在构造时失败 |
| **Aggregate** | 一致性边界；**只通过根**访问；一事务一聚合（跨聚合用最终一致/事件） |
| **Domain Service** | 无自然宿主的领域操作；仍属领域语言，不是「万能 Service 类」 |
| **Domain Event** | 领域内已发生的事实；跨聚合协调优先事件，非共享实体 |
| **Repository** | 按聚合重建/保存；隐藏持久化；查询勿泄漏表结构 |
| **Factory** | 复杂创建与不变量；禁止半成品对象流出 |

**六元组落点**：应用层用例 = `method` 编排；领域不变量在聚合内；补偿/降级见 [`six_tuple_runtime.md`](six_tuple_runtime.md) + [`backend_arch.md`](backend_arch.md)。

---

## 4. 与总范式表的衔接

部署/分层/FE 阶梯以 [`dev_paradigm.md`](dev_paradigm.md) §3～§4 为准。本文只约束：**已选 DDD 时**如何切 BC 与战术模型。  
选了 B4/B5 后：先切领域边界，再选模块化单体 vs 微服务、Feature vs FSD；禁止未切 BC 就上微服务或全套 FSD。

---

## 5. 前后端如何「同域不同模型」

| 端 | 映射 |
|----|------|
| **后端** | 一 BC → 一模块（或一服务）；Hexagonal：Domain 无框架；见 `backend_arch` |
| **前端** | 一 BC → 一 feature/slice（或 BFF 视图模型）；**禁止**把后端聚合 JSON 原样当 UI 状态；见 `frontend_arch` |
| **契约** | 公开 API / 事件 = Published Language；版本与幂等见 `api_engineering` |
| **词典** | 产品词以域词典为准；UI 文案可口语化，但类型/字段名跟上下文语言 |

```text
[PRD 场景] → 切 BC + 词典
    → 选方案（单体分包 / 微服务 / FE Feature|FSD）
    → 后端：聚合 / 用例 / 端口
    → 前端：按 BC 的 feature + 页面用例状态
    → 接口：DTO / 错误码（非领域对象直出）
    → C4 + ADR（L）
```

---

## 6. 设计产出清单（阶段 2）

模板：[`arch_design_template.md`](../resources/templates/architecture_design/arch_design_template.md)。

- [ ] 上下文图（Mermaid）+ 每种跨边界关系已标注  
- [ ] 核心聚合表：根、不变量、状态跃迁  
- [ ] 词典条目已登记；无未解释的同义词  
- [ ] 核心用例落在哪个上下文、哪个应用服务（六元组名）  
- [ ] 前端 feature 边界与 BC 对齐（或显式 BFF 聚合视图）  
- [ ] 「为何不拆/不合」写入 ADR（L 或边界争议时）

---

## 7. 反模式（出现即改）

| 反模式 | 改为 |
|--------|------|
| 贫血模型 + 巨型 Service | 行为进实体/领域服务 |
| 一张「User/Order」表模型打天下 | 按上下文拆模型 + ACL |
| 前端直接复用后端 Entity 形状 | 视图模型 / 用例状态 |
| 为 DDD 而 DDD（小 CRUD） | 降档到简单分层 |
| 跨聚合强一致分布式事务 | 领域事件 + 幂等 + 补偿 |

深化（按需，每任务 ≤2 source）：

```bash
python scripts/rule_fetch.py resolve --id ciembor.architecture-books --rule domain-driven-design-distilled
python scripts/rule_fetch.py resolve --id ciembor.architecture-books --rule implementing-domain-driven-design
python scripts/rule_fetch.py resolve --id sairyss.dddh-readme   # 仅 search-cache，禁止整读
python scripts/rule_fetch.py resolve --id kgrzybek.modular-monolith  # 模块化单体实践对照
```
