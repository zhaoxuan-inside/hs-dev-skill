# 各入口执行流程

本文展示主 Skill 收到不同类型任务后，如何选择过程 Skill、功能 Skill、指导文档、计划、验收和工作结果。机器路由目标以 [`skill_routes.json`](../resources/skill_routes.json) 为准。

## 所有可变更入口共用的闭环

```mermaid
flowchart LR
    A[识别入口与授权范围] --> B[恢复当前基线与确认]
    B --> C[读取当前入口的指导文档]
    C --> D[创建或更新计划文档]
    D --> E[按计划调用过程与功能 Skill]
    E --> F[形成产物与可复核证据]
    F --> G[按验收文档逐项核验]
    G -->|缺证据或未通过| D
    G -->|待开发者确认| H[提交候选结果并等待确认]
    G -->|适用项通过且确认齐全| I[输出工作文档与交接]
    H --> I
    I --> J[主路由更新阶段与下一动作]
```

计划文档应包含目标、范围/非目标、基线版本、要做的步骤、对应指导文档、验收项、证据位置、阻断项和下一步。工作文档记录实际改动/发现、证据、偏差、未完成项、验收状态与交接。沿用项目已有 `plan_log`、`change_log`、任务、Pack 和验收记录，不为形式重复造文档；没有可复用载体时，由当前入口建立最小记录。

**执行轨迹（按项目开关）**：工程开启 trace 时，沿上述闭环按 [skill_trace](skill_trace.md) §7 自报事件（会话开始/结束、分级、装载、路由、阶段流转、任务关联、关键动作、拍板、纠偏、错误重试、耗时），关闭时静默、不落盘。只读入口（EXPLORE）同样遵循项目开关——trace 日志属本地可观测副作用，不视为任务/产物状态变更；未开启时不记录。

**结束条件**：适用验收项逐项有结论和证据；未通过项清零或按范围明确延期并获确认；需要开发者签收的决策已有当前版本确认；工作文档和交接状态已更新。Agent 的“完成”判断、目录齐全或命令成功不能代替这些条件。

## 纵向过程入口

| 入口 | 执行顺序 | 主要计划/工作文档 | 验收依据 | 结束后的路由 |
|---|---|---|---|---|
| BUILD 阶段 0 / discovery | 对齐真实场景与授权 → 读取产品指导 → 计划待澄清问题与产物 → 产品 Skill 形成范围和规格 → 对照 DISC/PROD → 记录签收 | 需求对账、范围/假设、PRD/原型、冻结记录 | `product_acceptance.md` + 阶段验收协议 | 通过后阶段 1；未决业务问题留在 discovery |
| BUILD 阶段 1 / design | 核验产品基线 → 规划候选和验证 → architecture 比较选型 → 对照 TECH → 记录 ADR 和裁决 | 选型计划、ADR、风险与验证记录 | `engineering_acceptance.md` TECH | 通过后阶段 2 |
| BUILD 阶段 2 / design | 核验 ADR → 规划边界、依赖及视图 → architecture 与触达的前后端协作 → 对照 ARCH → 记录裁决 | 架构设计计划、视图、边界/依赖、ADR | `engineering_acceptance.md` ARCH | 通过后阶段 3 |
| BUILD 阶段 3 / design | 核验架构基线 → 规划本次契约 → 后端及需要的前端设计 DB/API/UI → 对照 DETAIL → 记录机器契约和决策 | 详细设计计划、DB/API/UI 契约、风险记录 | `engineering_acceptance.md` DETAIL | 通过后阶段 4 |
| BUILD 阶段 4 / planning | 核验已验收需求和设计 → 分配需求到任务 → 规划垂直切片与 DoD → 生成 Pack/任务 → 对照 TASK | 任务清单、映射、依赖、Pack | `engineering_acceptance.md` TASK + task 状态机 | 通过后阶段 5 |
| BUILD 阶段 5 / implementation | 核验 Pack 版本 → 规划单个切片 → checkpoint → 调前后端实现、testing 验证 → 对照 IMPL → 更新代码/契约/证据 | 切片计划、checkpoint、测试结果、偏差记录 | `engineering_acceptance.md` IMPL + 该切片 DoD | 通过后继续下一切片或阶段 6 |
| BUILD 阶段 6 / acceptance | 冻结本次交付分母 → 汇集版本化证据 → testing/governance 提供验证 → acceptance 逐项复核 → 开发者签收 → 整理交付 | 验收记录、交付报告、未实现项/偏差 | `stage_acceptance.md` + `engineering_acceptance.md` DELIV | 通过后归档/本地提交；push 需明确授权 |
| FIX / debugging | 复述现象与预期 → 计划复现及可证伪假设 → 获取失败证据 → 触达专业 Skill 最小修复 → testing 回归 → 记录根因和证据 | 缺陷计划、复现步骤、根因记录、修复报告 | `systematic_debugging.md` + 相关 IMPL/DELIV 项 | 通过后交当前过程或 acceptance |
| REFACTOR / refactoring | 界定保持行为与结构目标 → 计划保护网和迁移步骤 → architecture/领域 Skill 逐步调整 → testing 验证等价 → 记录结构差异 | 重构计划、行为基线、等价证据、结果报告 | `code_refactoring.md` + 适用测试/IMPL 项 | 通过后归档或交付验收 |
| REVERSE / reverse | 确定纳管范围 → 计划证据采集 → 读取代码/运行事实 → 专业 Skill 提取契约 → 区分事实/推导/未知 → 开发者核对 | 逆向计划、现状契约、词典/索引、差异清单 | `reverse_engineering.md` + 纳管验收项 | 完成纳管后由主路由决定后续 intent |
| EXPLORE / exploration | 锁定只读问题 → 计划需查证的问题/路径 → 搜索代码和文档 → 调专业 Skill 解释 → 输出证据与未知 | 只读调查提纲、结论与证据 | `code_exploration.md`；不得触发写操作（trace 日志按 [skill_trace](skill_trace.md) 项目开关处理） | 直接答复，不创建任务或提交 |
| RESUME / continuity | 扫描日志与当前树 → 恢复目标/确认/阶段/断点 → 计划最小恢复动作 → 继续原过程 → 核查基线有效性 → 更新交接 | 恢复摘要、续做计划、有效/失效基线 | `process_continuity.md` + 当前阶段验收记录 | 恢复后路由到实际阶段，不默认重开 BUILD |
| 需求变更 / continuity | 记录新表达 → 比较旧基线 → 计划影响分析 → 评估需求/设计/任务/代码/测试影响 → 请求必要裁决 → 更新源基线并使派生项失效 | 变更请求、影响矩阵、更新计划 | `requirement_change.md` + 受影响阶段验收 | 按影响回到 discovery/design/planning/implementation |
| 任意阶段验收 / acceptance | 确认阶段和版本 → 计划验收项 → 收集证据 → 按 checklist 判适用/通过/失败/待确认 → 汇总签收候选 | 阶段验收记录、差异清单 | `stage_acceptance.md` 对应阶段清单 | 通过回主路由；否则返修原负责人 |

BUILD 的阶段路由由意图和**当前已恢复阶段**共同决定；大规模任务通常经过 0→1→2→3→4→5→6，小任务只走实际触达的阶段并沿用有效基线。

## 横向功能入口

功能 Skill 不独立推进生命周期。它继承调用方的计划、授权、阶段和只读约束，在计划中认领专业任务，产出领域结果与证据，再交回过程负责人验收。

| 功能入口 | 专业执行流程 | 计划中应列的工作 | 专业输出与验收证据 |
|---|---|---|---|
| product | 用户/业务事实 → 规则与状态 → 场景演练 → 规格/原型 | 需求问题、范围、业务规则、场景和确认点 | PRD、REQ/Gherkin、MVP/原型；DISC/PROD 证据 |
| architecture | 约束 → 候选及代价 → 边界/依赖/运行视图 → 风险验证 | 需裁决的选型、边界和风险验证 | ADR、架构图、机器约束；TECH/ARCH 证据 |
| frontend | 继承设计语言 → 结构/状态/交互 → 实现 → 浏览器体验验证 | 终端、页面状态、可访问性、网络/控制台验证 | 原型、Tokens/组件或代码；PROD/DETAIL/IMPL 证据 |
| backend | 业务不变量 → 数据/API/方法契约 → Adapter 实现 → 迁移/集成验证 | 数据决策、接口、失败语义、迁移与测试 | DB/API/方法契约、实现/迁移；DETAIL/IMPL 证据 |
| testing | 需求/风险 → 测试层级和反例 → 执行 → 需求分母/结果回收 | 命令、环境、基线、断言和覆盖映射 | 可复跑测试报告、失败/跳过/限制；不代签业务验收 |
| governance | 范围/开关 → 核对适用治理项 → 更新索引/版本/安全证据 | 适用规则、来源、版本、产物检查 | 索引/词典/版本/治理结果；逐项说明适用性和证据 |

## 交接字段

每次子 Skill 返回至少包含：计划文档及版本、实际完成项、产物路径/版本、验收项状态及证据、偏差/阻断、开发者待确认点、失效基线、建议下一入口。只读 exploration 以问题、证据位置、未证实推断和边界替代变更计划与验收签收。
