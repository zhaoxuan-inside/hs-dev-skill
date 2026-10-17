# 子特性 PRD：Skill 执行轨迹（trace）

- **文档版本 / 内容摘要**：v0.1（2026-10-17 冻结 APPROVED）——项目级可隔离开启的 Skill 执行轨迹能力；自报式 11 类语义事件、按会话 JSONL、最小查询 CLI
- **DISC / PROD 阶段验收记录**：`hs_dev_docs/_06_dev_process/skill_trace_001_phase0_acceptance.md`
- **确认范围及来源**：`hs_dev_docs/_06_dev_process/_03_qa_log/skill_trace_001_qa.md`（Q0～Q8 均已确认，消息日期 2026-10-17）
- **特性 ID**：`FEAT-TRACE-001`
- **所属模块**：hs-dev-skill 框架 / 开发过程与治理（_06_dev_process）
- **优先级**：P0
- **状态**：frozen（2026-10-17 冻结单 APPROVED）
- **task_id / 分级**：`skill_trace_001` / intent=`BUILD`，change_size=`M`，work_mode=`DESIGN`
- **关联界面原型**：NA（无 UI；PROD-07、视觉签收 B 节均 NA）
- **上级总览索引**：NA（框架自身特性，非多特性产品线）

---

## 1. 特性洞察与核心价值（0A 取证）

- **现状与摩擦（Status Quo）**：Skill 执行发生在宿主 Agent 内，过程不可见——无法知道某次会话实际装载了哪些子 Skill、如何路由、阶段如何流转、哪里发生纠偏或返工；优化只能靠回忆与猜测（来源：开发者需求陈述与 Q1/Q6 确认）。
- **用户雇佣任务（JTBD）**：`When` 完成一次由 hs-dev-skill 驱动的开发会话，`I want to` 按会话回放其执行轨迹（装载 / 路由 / 阶段 / 关键动作 / 纠偏 / 错误 / 耗时），`so I can` 用证据定位 skill 的薄弱点并针对性优化。
- **惊喜时刻（Aha Moment）**：开启后当场即可用 `skill_trace.py summary --session <id>` 一屏看到本次会话的装载序列、阶段流转与纠偏/错误清单——此前完全不可见。
- **冷启动体验（FTUE）**：`skill_trace.py enable` 一条命令开启；后续会话按规则自动落盘；`demo_project` 提供回放样本（Q6）。
- **真实案例（Q6 确认）**：(a) 本次 trace 能力开发会话本身（从 discovery 起 dogfooding）；(b) demo_project 上一段标准 BUILD 流程回放。

### 1.1 表达 → 理解 → 结论对账表

| 开发者表达及来源 | Agent 理解 | 结论与状态 |
|---|---|---|
| “开启后要完整记录整个 Skill 执行过程以指导优化”（Q0） | 记录范围 = 语义事件层全流程（Q3 裁定 11 类） | CONFIRMED（Q3=A） |
| “trace 开启和日志记录都要按项目隔离”（Q0） | 开关：工程内独立配置；日志：工程内固定路径；全局目录零写入 | CONFIRMED（Q2/Q4） |
| “自报式，但要讲清楚执行顺序和依赖关系”（Q1） | 必须给出规范事件序列 + 依赖规则（R1～R6）+ 引用字段 | CONFIRMED（Q1 答复） |
| “新增一个项目级别的 skill 执行配置”（Q2） | 新文件 `config/skill_execution.yaml`，不耦合 governance.yaml | CONFIRMED（Q7=A） |
| “最小查询 CLI”（Q5） | `summary` / `query` / `status` 子命令 | CONFIRMED（Q5=A） |
| 事件字段级 Schema、CLI 参数细节、截断上限具体值 | Agent 推导 | DERIVED → 阶段 3 详细契约定稿（不改变本节语义） |

- **未决项（OPEN）**：无产品级未决项；工程细节（字段命名、默认上限值）在阶段 3 契约评审中定稿。
- **反目标（Q0 确认）**：不改 `observability_telemetry` 语义；不做跨工程聚合/中央收集；不重写 process_log 既有契约；不承诺超出 Agent 自报范畴（工具调用级明细）的捕获。

---

## 2. 形态比选与取舍（Approaches & Trade-offs）

| 决策点 | 方案 A（采纳） | 方案 B（弃用本期） | 取舍理由 |
|---|---|---|---|
| **采集机制** | Agent 自报式语义事件（零宿主依赖，三端一致） | 宿主 Hook 自动采集工具调用级 | 框架本体无法观测宿主；Hook 平台碎片化、需升 L；本期以“明确时序与依赖约定”保证自报一致性（Q1） |
| **开关形态** | 独立项目级 `config/skill_execution.yaml` | 挂靠 `governance.yaml` / 环境变量 | 语义解耦、项目级持久、不扩大 governance 语义（Q2/Q7） |
| **存储形态** | 工程内按会话 JSONL | 按任务文件 / 按日滚动 | 会话边界清晰、最贴合“回放一次执行”；未建任务前的会话事件也有归属（Q4） |

---

## 3. 规格与契约（语义级；字段细节留阶段 3）

### 3.1 配置契约（项目隔离的开关）

- 文件：`config/skill_execution.yaml`（工程根，随工程走；缺省生成）。
- 结构：

```yaml
version: "1.0"
description: 项目级 skill 执行配置
features:
  skill_trace: false   # Skill 执行轨迹（默认关闭）
```

- 读写：`python3 scripts/skill_trace.py enable|disable|status`；写策略沿用 `governance_toggle` 模式（有 PyYAML 用 YAML 解析、无则逐行兜底；写出固定模板）。
- 初始化：`init_hs_dev_docs.py` 在目标工程缺省生成（`skill_trace: false`）。
- 隔离语义：开关读取顺序 = 当前工程根 `config/`；任何工程均不读取其他工程或全局目录的开关；缺省（无文件）一律视为关闭。

### 3.2 事件模型（11 类语义事件，Q3 裁定）

| # | 类 | 事件名（规范键） | 语义 | 关键字段（概要） | 依赖 |
|---|---|---|---|---|---|
| 1 | 会话 | `session_start` / `session_end` | 会话轨迹边界 | `session_id`、时间、宿主、cwd | `session_end` 须有对应 `session_start` |
| 2 | 意图分级 | `intent_sizing` | 意图、分级、模式与确认 | `intent`、`change_size`、`work_mode`、确认来源 | 在 `session_start` 之后 |
| 3 | 装载 | `skill_load` | 加载的子 Skill 及时机 | `skill_id`、阶段/原因 | 关联当次 `route_decision` |
| 4 | 路由 | `route_decision` | 阶段路由结果 | `intent`、`phase`、`process_skill`、`functional_skills[]` | — |
| 5 | 阶段 | `phase_transition` | 阶段进入/待验收/通过/阻断 | `from`、`to`、`status` | 引用对应验收记录路径（若有） |
| 6 | 任务关联 | `task_link` | 关联任务/计划/checkpoint | `task_id`、`plan_path`、`checkpoint_id` | 引用不复制 process_log 数据 |
| 7 | 关键动作 | `key_action` | 关键命令/测试/产出 | `kind`、`summary`、`result` | 结果须为可观察事实 |
| 8 | 决策 | `decision` | 开发者拍板引用 | `question`、`adopted`、`ref` | `ref` 指向 `_03_qa_log/` 记录 |
| 9 | 纠偏 | `deviation` | 纠偏/返工/用户纠正 | `what_happened`、`correction`、`ref` | `ref` 指向触发事件 `event_id` |
| 10 | 错误 | `error_retry` | 错误与重试/中止 | `error`、`action`、`attempt` | — |
| 11 | 耗时 | `timing` | 关键节点耗时 | `scope`、`duration_ms` | 或以 `duration_ms` 字段附于他事件 |

### 3.3 事件顺序与依赖约定（Q1 强制要求）

规范序列（一次会话）：

```text
session_start → (intent_sizing → skill_load → route_decision → phase_transition / task_link
                → key_action / decision / deviation / error_retry / timing)* → session_end
```

- **R1 追加与有序**：轨迹文件 append-only；同一会话内事件时间戳单调不减。
- **R2 会话归属**：除 `session_start` 外，所有事件必须携带有效 `session_id`；`session_id` 由记录器在 `session_start` 时生成并返回。
- **R3 引用完整**：`task_link` / `decision` / `deviation` 必须携带 `ref`（任务、QA 日志或触发事件 `event_id`）；引用目标须可解析。
- **R4 关闭即静默**：未开启时所有写操作 no-op：不报错、不落盘、不做目录初始化（开关隔离的直接体现）。
- **R5 不阻断主流程**：记录失败为 best-effort，仅告警一次，不得中断 Agent 任务。
- **R6 隐私与体积**：单事件载荷超限截断并标记 `truncated: true`；不记录完整对话或代码正文；不记录密钥/凭据。

### 3.4 存储契约

- 位置：`hs_dev_docs/_06_dev_process/_05_skill_trace/sessions/{session_id}.jsonl`（工程内）。
- 格式：UTF-8，一行一事件（JSON）；首行必为 `session_start`。
- 生命周期：仅开启且首个事件时创建；不做自动清理/轮转/压缩（MVP 裁剪项）；保留策略=手动清理 + 文档说明。
- 隔离：日志只写入当前工程根；全局目录（`~/.hs-dev-skill/` 等）永不接收 trace 数据。

### 3.5 查询 CLI（最小）

- `summary`（`--session` / `--task` / `--since`）：会话/任务摘要——事件计数、时间跨度、阶段序列、纠偏与错误列表。
- `query`（`--session` / `--task` / `--event` / `--since` / `--limit`）：筛选输出原始事件。
- `status`：当前工程开关状态 + 最近会话列表。
- `enable` / `disable`：开关读写（§3.1）。

---

## 4. 需求原子分解与行为验收（Functional DoD）

### 4.1 需求矩阵

| 需求编号 | 需求名称与规则简述 | 验收物理证据 | 优先级 |
|---|---|---|---|
| `REQ-TR-01` | 项目级独立开关：`config/skill_execution.yaml` 生成/读写；缺省关闭；跨工程互不影响 | 两工程 A/B 隔离演示（A 开启 B 不落盘）；配置读写命令输出 | P0 |
| `REQ-TR-02` | 开启后自动记录 11 类语义事件为会话 JSONL | 会话样本文件 + 事件类型断言测试 | P0 |
| `REQ-TR-03` | 顺序与依赖约定 R1～R3 可校验（会话归属、时序、引用完整） | 校验测试（缺 session/坏引用/乱序用例） | P0 |
| `REQ-TR-04` | 关闭态 no-op 且不阻断主流程（R4/R5） | 关闭态运行零落盘、零报错；故障注入仅告警 | P0 |
| `REQ-TR-05` | `summary`/`query` 可复盘一次会话（阶段序列、纠偏/错误） | demo 回放演练输出 | P0 |
| `REQ-TR-06` | 隐私与体积约束 R6（截断标记、不落正文） | 超长载荷截断用例 | P1 |
| `REQ-TR-07` | 初始化集成：`init_hs_dev_docs` 缺省生成配置与目录 | 初始化后目录/配置断言 | P1 |
| `REQ-TR-08` | 三端兼容且不破坏既有门禁 | 全量测试 + `verify_consistency --strict` 绿 | P0 |

### 4.2 Gherkin 验收场景

```gherkin
Feature: Skill 执行轨迹（trace）

  Scenario: REQ-TR-01 项目隔离——A 工程开启不影响 B 工程
    Given 工程 A 执行 skill_trace enable，工程 B 未开启
    When 两工程各自产生一次会话事件
    Then 仅工程 A 的 _05_skill_trace/sessions/ 出现轨迹文件，工程 B 无任何 trace 产物

  Scenario: REQ-TR-02 开启后按序落盘 11 类事件
    Given 工程已执行 skill_trace enable
    When 依次产生 session_start、intent_sizing、skill_load、route_decision、phase_transition 与 session_end
    Then 该会话 JSONL 首行是 session_start、末行是 session_end，且事件类型与顺序符合规范序列

  Scenario: REQ-TR-03 依赖校验——缺失会话归属被拒绝
    Given 工程开启了 trace，但某次 record 未携带 --session
    When 记录器校验依赖规则
    Then 该事件不被写入（或写入即标记非法），并给出可定位的告警

  Scenario: REQ-TR-04 关闭态静默
    Given 工程未开启 trace
    When 执行任意 trace record 与查询
    Then 不产生目录与文件、无报错；主流程退出码不受影响

  Scenario: REQ-TR-05 复盘一次 demo 回放的 BUILD 流程
    Given demo_project 开启 trace 并完成一段标准 BUILD 流程
    When 执行 skill_trace summary --session <id>
    Then 摘要展示阶段序列、关键动作/决策计数、纠偏与错误清单，且与回放记录一致

  Scenario: REQ-TR-06 超长载荷截断
    Given 某事件载荷超过上限
    When 被记录
    Then 载荷被截断并携带 truncated 标记，轨迹文件仍可解析
```

---

## 5. 质量约束

- **兼容性**：Windows / Linux / macOS；Python 标准库优先（可选 PyYAML 回退策略与 `governance_toggle` 一致）。
- **性能**：记录为单次追加写，不得显著阻塞 Agent 主流程（设计阶段定量化目标）。
- **门禁**：既有全量测试与 `verify_consistency --strict` 保持通过；不修改 process_log/plan/change/qa 现有契约（仅通过引用关联）。
- **隐私**：不落对话/代码正文、不落密钥；截断上限在阶段 3 契约定稿。
- **NA 项**：UI 相关（PROD-07、视觉签收 B 节）NA——本特性无 UI。

---

## 6. MVP 范围裁定（Q8 开发者拍板）

- **本期做（MVP）**：①项目级配置 + 开关 CLI；②自报式事件记录（按会话 JSONL）；③事件时序与依赖约定（详规 + 路由层挂载规则）；④最小查询 CLI；⑤测试 / 文档 / 模板。
- **裁剪项（仅登记 MoSCoW 池，不写详细规格）**：①Hook 适配器实现（仅扩展点文档）；②`doc_index_db` 索引与门禁联动；③自动清理 / 轮转 / 压缩；④多工程聚合统计；⑤可视化 UI；⑥token 用量采集（宿主依赖，不可自报）。
- **胃口（Appetite）**：单任务内小步交付，无排期硬点；断路器=裁功能保可用。

---

## 7. 验收演练计划（PROD-06）

1. **本会话 dogfooding**：trace 能力自身开发会话按规范序列落盘（启用后手动补记关键节点，作首个真实样本）。
2. **demo_project 回放**：在 demo_project 开启 trace，执行一段标准 BUILD 流程，产出 `summary`/`query` 复盘输出与真实轨迹文件。
3. 演练记录（输入、路径、预期、差异、裁决）追加至阶段验收记录与 Q&A 日志。

---

## 8. 阶段 0 验收与冻结

- DISC/PROD 逐项检查：见 `hs_dev_docs/_06_dev_process/skill_trace_001_phase0_acceptance.md`（SUBMITTED，待开发者核验）。
- 冻结签收：见 `hs_dev_docs/_06_dev_process/skill_trace_001_freeze_signoff.md`（业务语义签收 A；视觉签收 B 为 NA）。
- 冻结通过后进入阶段 1～3 的触达面设计（M 路径：仅补 trace 契约与集成面，不重做选型/架构）。
