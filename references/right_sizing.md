# 变更分级（Right-Sizing）与快路径

**何时读**：任意需求的第一步（写 PRD/编码前）；每会话最多一次。

**问题不是「单体 Skill」**，而是编排把一切需求默认当成「新产品切片」：铁律要求无条件走阶段 0 全量对齐 + 1/2/3 齐套后才允许编码，导致文案微调、单测修复、局部 bugfix 也被迫重建选型/架构/四要素，Token 与耗时陡增。

本文件定义**同 Skill 内**的分级与合法缩短路径；**不拆小 Skill**。未分级前禁止按满配 0→6 开工。

---

## 1. 意图与分级判定（会话第一步，≤10 行落盘）

在阶段 0 写 PRD 或动手前，先判定 `intent`、`change_size` 与 `work_mode`，写入任务 brief / context_pack 首行或 PRD 元数据：

### 1.1 场景意图判定（Intent）

| 场景意图 `intent` | 核心目标 | 专属指南 | 核心原则 |
|---|---|---|---|
| **BUILD** | 从零构建项目或全新独立功能域 | [`spec_driven_lifecycle.md`](spec_driven_lifecycle.md) | 满配 0→6 推进；两层解耦；MVP 激进裁剪 |
| **REVERSE** | 已有项目反向重建、Schema/API 提取与规范接入 | [`reverse_engineering.md`](reverse_engineering.md) | 代码即事实；非侵入式分析；生成四级索引 |
| **FIX** | 已有代码缺陷修复、排查偶发异常 | [`systematic_debugging.md`](systematic_debugging.md) | 科学假设驱动；先红后绿（必须先写失败测试） |
| **REFACTOR** | 消除坏味道、提炼深模块、模式落地 | [`code_refactoring.md`](code_refactoring.md) | 保护网先决（快照/不变量）；零可观测行为漂移 |
| **EXPLORE** | 纯只读理解代码、梳理时序、架构答疑 | [`code_exploration.md`](code_exploration.md) | 纯只读；免任务文件/免PRD/免Commit/免门禁 |
| **RESUME** | 任务续做、恢复断点或快照回退 | [`process_continuity.md`](process_continuity.md) | 沿用既有 plan_log，不当新需求重开 |

### 1.2 规模与模式判定（S / M / L & Work Mode）

| 级别 | 判定（满足即取该级；冲突取更高） | 典型例子 |
|------|----------------------------------|----------|
| **S（快路径）** | 不改产品语义/对外契约/DB schema/限界上下文；局部代码或文案/样式/测试/配置 | 修空指针、改文案、补单测、调 CSS、局部重构 |
| **M（补丁/增量路径）** | 改已有功能行为或内部接口，但**不**新开限界上下文、不换技术栈、不新增表族 | 加可选字段、改校验规则、单模块反向重建、模块级重构 |
| **L（满配路径）** | 新功能/新域、换栈、新表或破坏性 API、架构边界变化、模糊 UI/新技术需对标 | 新支付域、全工程逆向治理、换 ORM、公开 API 破坏性变更 |

**同时写 `work_mode`**（详见 [`confidence_decision.md`](confidence_decision.md)）：

| `work_mode` | 默认何时 |
|---|---|
| **READONLY** | `intent=EXPLORE` 时强制锁定；只读检索解答，禁止写任务/代码/Commit |
| **DESIGN** | M/L 冻结未过；需求模糊；写/改 PRD·ADR·架构·契约；不确定 |
| **IMPLEMENT** | S 且 DoD 已清；或冻结已过、按已定设计编码/修测 |

**不确定时**：`intent=BUILD`，`change_size=M`，`work_mode=DESIGN`。用户口头说「随便改一下」若触及契约/表结构 → 升为 M/L。用户说「跳过澄清 / 直接做」→ 按 [`confidence_decision.md`](confidence_decision.md) §1.5 收紧处理（禁止项不可跳过）。

---

## 2. 各路径合法阶段链

### S — 快路径（禁止空跑 1→3）

```text
分级 → 轻量对齐（记 DoD + 影响面）→ [可选] 切片装载 → 实现 + 单测 → 门禁子集 → 本地 Commit
```

| 步骤 | 要求 |
|------|------|
| 轻量对齐 | 3～8 行：改什么 / 不改什么 / DoD；**不写**完整 PRD，除非触及产品语义（则升 M/L） |
| 选型/架构/四要素 | **跳过**新建；禁止为 S 新建 ADR/架构文/四要素全套 |
| 装载 | `doc_index_db search|slice` 只取**被改文件相关**设计切片入 pack（可极短） |
| 实现 | 直接改代码；UI 有 `DESIGN.md` 则跟它，手艺读 `frontend_craft.md`；视觉未定则先 `design_md.md`；不涉及 API 则不读 `api_engineering.md` |
| 门禁 | 相关测试 + `verify_consistency`（若未动 docs/idx 可只跑测试）；有任务则归档 |
| 询问闸门 | 默认 `IMPLEMENT` 少问；触及产品语义未决 → 升 M/L 并切 `DESIGN` |

### M — 补丁路径

```text
分级 → 阶段 0 迷你 PRD（或 diff 节）→ 只补「触达面」设计 → 任务/pack → 实现 → 门禁 → Commit
```

| 步骤 | 要求 |
|------|------|
| 阶段 0 | 短 PRD 或在既有 PRD 下追加「变更节」；冻结门禁缩为：**触达面的**完整/正确/无冲突 |
| 阶段 1～2 | **跳过**除非换栈或动边界；否则引用既有 ADR/架构，只记「沿用」一行；动范式/边界读 `dev_paradigm.md`；仅当范式含 DDD 再读 `ddd_design.md`；动分层读 `backend_arch`/`frontend_arch` |
| 阶段 3 | **仅更新触达的** DB/API/六元组/调用链文档与 V/U；未触达维禁止重写 |
| 阶段 4～6 | 同满配，但 context_pack 只物化触达切片 |
| API/UI | 改契约读 `api_engineering.md`；改 UI：视觉→`design_md.md`/`DESIGN.md`，结构→`frontend_arch.md`，手艺→`frontend_craft.md`（各每会话最多一次） |

### L — 满配路径

完整 `0 → 1 → 2 → 3 → 4 → 5 → 6`，见 [`spec_driven_lifecycle.md`](spec_driven_lifecycle.md)。阶段 1～2 先[`dev_paradigm.md`](dev_paradigm.md)选范式；仅 DDD 档再读[`ddd_design.md`](ddd_design.md)；模糊 UI→[`design_md.md`](design_md.md)；后端分层→[`backend_arch.md`](backend_arch.md)；前端模块→[`frontend_arch.md`](frontend_arch.md)。

---

## 3. 禁止事项（防「假快路径」）

- 用 S 掩盖产品语义未决或破坏性 API/表变更。
- S/M 路径下仍整读 `spec_v2_4.md` 或整树 `hs_dev_docs`。
- 为走过场复制空 ADR/空四要素文件。
- 分级后不写 `change_size`，导致后续会话又按 L 重做。

---

## 4. 与置信度、门闩、Token 的关系

- 分级本身**不询问**（工程编排）；产品语义空白走 `DESIGN` 多问，不走「实现期四条件」偷懒跳过。
- 动手前过 [`load_latch.md`](load_latch.md) L0～L2。
- Token：S 应明显少于 M，M 少于 L；若 S 会话仍加载 lifecycle 全文 + 多份 references / 远程规则包，视为违规，改回本文件 + `token_budget.md` 挂载表。
