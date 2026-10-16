# 后端框架设计清单（本地高频 · 按需加载）

**何时读**：[`dev_paradigm.md`](dev_paradigm.md) 选定后端阶之后；依赖环；微服务拆分 / Saga；每会话最多一次。  
**分工**：本文 = **后端分层与部署边界**；范式总表 → `dev_paradigm`；**深模块 / seam / Adapter** → [`deep_modules.md`](deep_modules.md)；**DDD（仅 B4+）** → [`ddd_design.md`](ddd_design.md)；前端模块 → [`frontend_arch.md`](frontend_arch.md)；契约 → [`api_engineering.md`](api_engineering.md)；六元组 → [`six_tuple_runtime.md`](six_tuple_runtime.md)。

```bash
python scripts/rule_fetch.py search --q 架构
python scripts/rule_fetch.py resolve --id local.backend.arch
python scripts/rule_fetch.py resolve --id wshobson.architecture-patterns
python scripts/rule_fetch.py resolve --id clean-arch.skill
python scripts/rule_fetch.py resolve --id wshobson.architecture-refs --rule advanced-patterns
python scripts/rule_fetch.py resolve --id ciembor.architecture-books --rule clean-architecture
python scripts/rule_fetch.py resolve --id muthub.c4designer          # C4 图
python scripts/rule_fetch.py resolve --id muthub.adr-scribe          # ADR 写法
python scripts/rule_fetch.py resolve --id wshobson.microservices-patterns
python scripts/rule_fetch.py resolve --id wshobson.saga-orchestration
```

**溯源**：

| 库 | Stars（量级） | 用途 |
|----|---------------|------|
| [wshobson/agents](https://github.com/wshobson/agents) | ~4 万★ | Clean / Hexagonal / DDD / 微服务 / Saga / CQRS |
| [omaromar9091/clean-architecture-skill](https://github.com/omaromar9091/clean-architecture-skill) | 社区 | 分档防过度设计 |
| [ciembor/agent-rules-books](https://github.com/ciembor/agent-rules-books) | ~3k★ | CA / DDD / DDIA 等书规则（mini） |
| [muthub-ai/c4-skills](https://github.com/muthub-ai/c4-skills) | 社区 | C4 图 + ADR 撰写 |
| 本 Skill | — | 六元组、架构模板、`change_size` 分档 |

---

## 1. 先定边界，再定分层（强制）

| 步骤 | 要求 |
|------|------|
| 1. 变更档 | 跟 `change_size`：S 不新建架构文；M 只改触达边界；L 写完整架构 |
| 2. 边界 | 先 `dev_paradigm` 定阶；B4+ 再 `ddd_design` 切 BC；否则按业务模块切；跨边界用 ACL/事件，禁止共享上帝模型 |
| 3. 依赖方向 | **只向内**：Domain ← Application ← Adapters ← Frameworks；内层不知外层 |
| 4. 外部封装 | 业务代码禁止直接 import 第三方 SDK/DB 驱动；经 infra **Adapter** 落在明确 **seam**（见 `deep_modules`；真有 ≥2 实现再抽端口） |
| 4b. 深度自检 | 用例/域模块做**删除测试**：删掉后复杂度是否散到 N 处调用方？浅透传则合并或加深 |
| 5. 文档落盘 | L：`hs_dev_docs/_03_architecture_design/`；模板见 [`arch_design_template.md`](../resources/templates/architecture_design/arch_design_template.md)。DB 详设使用 [`db_table_design.md`](../resources/templates/hs_dev_docs/db_table_design.md) |

模糊新技术栈：GitHub 高星对标 ≥2（框架官方样例 / 同域开源）再写 ADR。

---

## 2. 四层映射（与本 Skill 分层对齐）

```text
Interfaces / Controller / Gateway     ← 协议、鉴权、入参校验、错误码映射
Application / Orchestrator / Saga     ← 用例编排、六元组 method、事务/补偿控制
Domain / Aggregates / Entities        ← 不变量、状态跃迁、领域事件（无框架注解）
Infrastructure / Repo / RPC Client    ← 持久化、缓存、消息、三方网关
```

| 禁令 | 改为 |
|------|------|
| Controller 写业务规则 | 抽 Use Case / 六元组 method |
| 领域实体挂 ORM/Column | 外层 ORM Model + Repository 映射 |
| Use Case 直接 `new SqlRepo()` | 依赖 Port 接口，Composition Root 注入 |
| 跨上下文 import 对方 Entity | ACL + 本上下文 Value/Id |
| HTTP `req/res` 传入领域层 | 边缘 DTO → 领域对象 |

**测试指纹**：用例可用内存 Adapter 测通，不必起真实 DB（测不通 → 依赖漏进领域/应用层）。

---

## 3. 分档：防过度架构（对齐 Clean skill）

| 档 | 例 | 做法 |
|----|----|------|
| T0 | 文案/日志/单点 bug | 直接改；禁止新建分层目录 |
| T1 | 既有用例加字段/修一层内逻辑 | 尊重现有边界；不重构文件夹 |
| T2 | 新模块/新集成 | 按实际职责分层；有至少两种实现或明确边界需求才抽 Port，文件粒度适中 |
| T3 | 新服务/限界上下文 | 战略 DDD + ADR + 验证表 |

不确定 → **默认低一档**。一次性脚本 / 明确 spike → 声明轻量结构即可，禁止假装企业架构。

---

## 4. 架构表达（C4 + ADR）

| 产出 | 何时 | 远程 |
|------|------|------|
| **C4** Context → Container →（可选）Component | L 阶段 2；M 仅触达边界变化时补 Container | `muthub.c4designer` |
| **ADR** | L 阶段 1；换栈/跨上下文通信/数据所有权决策 | `muthub.adr-scribe` + 本地 [`adr_template.md`](../resources/templates/hs_dev_docs/adr_template.md) |

C4 先画人与系统边界，再画容器与数据所有权；禁止一上来画类图当架构。ADR 必须写「为何不选」≥1 备选。

---

## 5. 单体 vs 微服务（决策摘要）

默认 **模块化单体**（按业务模块分包；选定 DDD 后才使用限界上下文），直到出现独立部署/扩展/团队边界的硬理由。

| 做微服务前必须有 | 不做时 |
|------------------|--------|
| 清晰上下文边界 + 数据所有权 | 共享库硬拽多团队发布 |
| 跨服务失败与补偿设计（Saga/出箱） | 「先拆再补一致性」 |
| 可观测（trace / saga_id） | 同步链路串一长串 |

微服务通信：同步（REST/gRPC）用于查询与简单命令；跨聚合一致用异步 + **幂等步骤 + 补偿**。深化：`wshobson.microservices-patterns`。

---

## 6. 编排与六元组

- 应用层编排 ↔ 六元组 `method`；补偿 ↔ `method_compensate`（须幂等、已回滚也算成功）；降级 ↔ `method_fallback`。
- Saga：每步幂等；`saga_id`/correlation 贯通；**逐步超时**勿全局一把；补偿逆序；显式测失败注入。
- 长事务：状态落盘可恢复；禁同步链式调用当「分布式事务」。

细则：[`six_tuple_runtime.md`](six_tuple_runtime.md)；Saga 深化：`wshobson.saga-orchestration`。事件溯源仅在有明确审计/重建需求时启用：`wshobson.event-store`。

---

## 7. 交付自检

- [ ] 依赖箭头只向内；领域无框架 import
- [ ] 跨上下文无实体共享；对外契约见 `api_engineering`
- [ ] 关键用例有内存/假 Adapter 测试；补偿路径有覆盖（若有）
- [ ] 档位与 `change_size` 匹配；无为空造的空架构文
- [ ] ADR 记录「为何不选」至少一个备选（L / 换栈时）
