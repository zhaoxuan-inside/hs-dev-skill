---
name: hs-dev-skill
description: >-
  Guide software project work: build or modify features, fix bugs, refactor,
  design requirements/architecture/APIs/UI, plan tasks, review stage deliverables,
  understand existing code, and resume ongoing work. 适用于开发、修复、重构、设计、
  拆任务、阶段验收、代码分析与继续任务，包括已有项目的局部改动。
  Select the current process and touched domains; preserve accepted requirements
  and evidence. Excludes general questions unrelated to project work.
license: MIT
metadata:
  author: hardstone
  version: "4.2.0.0"
  runtime: "Python >= 3.8; install the complete bundle including skills, scripts, references, resources"
---

# 产品开发主路由 Skill

版本：v4.2.0.0

Agent 驱动文档，已验收的文档驱动代码。本入口只负责分派与共享边界；具体过程和专业规则由真实的子 Skill 执行。完整包含 **10 个过程 Skill + 6 个功能 Skill**，详规和工具保持单份共享。

## 先判路由，再加载

**适用任务的开工约定**：在首次项目调查或修改前，读取本入口及当前过程子 Skill；涉及专业领域时读取相应功能入口。开场简述实际使用的过程、阶段/分级与领域。运行路由脚本、提及 Skill 名称或凭记忆复述均不等于已经读取并执行。直接调用子 Skill 时沿用已有上下文，缺少过程时按运行协议补齐；简单任务走 S 路径，不跳过入口。纯版本查询等元信息读取无需启动项目流程。

**首次触发边界**：正文无法约束尚未加载本 Skill 的 Agent。希望项目持续采用本流程时，应将 [项目入口约定](references/subskill_contract.md#7-项目入口约定与触发验证) 合并到宿主实际读取的项目指令中，并用新会话验证；不自动改写其他项目或全局配置，也不承诺安装即强制执行。

每个会话首次加载时按 [版本更新协议](references/skill_update.md) 执行 `python <安装根>/scripts/skill_update.py check --quiet`：有新版就提示用户，网络不可用不阻断任务；检测不自动安装，同一会话不重复提醒。更新方式与完整包校验见该协议。

1. 识别当前任务的 `intent`、`change_size=S/M/L`、`work_mode=DESIGN/IMPLEMENT/READONLY`、实际阶段及触达领域。沿用已有明确确认；模糊业务预期交 discovery，不靠工程假设补齐。
2. 只读分析走 exploration；“继续”走 continuity 先恢复；变更和验收事件优先进入对应子过程。FIX/REFACTOR/REVERSE 不套 BUILD 全链。
3. 从下表读取 **一个过程子 Skill**，再按任务触达面读取功能子 Skill；未触达领域不加载。每次只推进当前切片，不能开局通读所有子 Skill。
4. 按[各入口执行流程](references/entry_workflows.md)读取指导文档、建立/更新计划、执行、提交证据并形成工作文档；用检索/切片加载子 Skill 指定详规和项目输入，遵循[装载规则](references/load_latch.md)。输入、输出与返回约定见[子 Skill 协议](references/subskill_contract.md)。
5. 子 Skill 返回当前产物、证据、验收状态及下一动作后，主路由继续分派；不得将调用成功解释成阶段完成。

路由唯一机器清单：[`resources/skill_routes.json`](resources/skill_routes.json)。工具不猜阶段、不执行任务、不代签：

```bash
# Linux/macOS 可用 python3，Windows 可用 py -3；以下 python 须为 Python >= 3.8
# 路径相对安装包；在工程中使用时换成安装包脚本的绝对路径
python scripts/skill_router.py check
python scripts/skill_router.py list
python scripts/skill_router.py route --intent BUILD --phase 3 --domains backend
python scripts/skill_router.py route --intent FIX --domains frontend testing
python scripts/skill_router.py route --intent RESUME
```

## 纵向：过程分派

| 当前目标 | 过程子 Skill | 交付边界 |
|---|---|---|
| BUILD 阶段 0：需求与产品对齐 | [hs-dev-discovery](skills/hs-dev-discovery/SKILL.md) | 真实场景、范围、预期、产品冻结 |
| BUILD 阶段 1/2/3：选型/架构/详设 | [hs-dev-design](skills/hs-dev-design/SKILL.md) | 仅当前阶段设计与验收证据 |
| BUILD 阶段 4：拆任务与装配 | [hs-dev-planning](skills/hs-dev-planning/SKILL.md) | 需求映射、任务、有效 Pack |
| BUILD 阶段 5：执行切片 | [hs-dev-implementation](skills/hs-dev-implementation/SKILL.md) | 代码、契约、测试及切片演练 |
| BUILD 阶段 6 / 任意阶段验收 | [hs-dev-acceptance](skills/hs-dev-acceptance/SKILL.md) | 当前版本的证据与开发者验收 |
| FIX：修复实际缺陷 | [hs-dev-debugging](skills/hs-dev-debugging/SKILL.md) | 复现、根因、修复与回归 |
| REFACTOR：保持行为的结构调整 | [hs-dev-refactoring](skills/hs-dev-refactoring/SKILL.md) | 保护网、结构改善、等价证据 |
| REVERSE：存量项目纳管 | [hs-dev-reverse](skills/hs-dev-reverse/SKILL.md) | 可证实的现状契约与索引 |
| EXPLORE：只读理解 | [hs-dev-exploration](skills/hs-dev-exploration/SKILL.md) | 解答与证据，免任务/PRD/Commit |
| RESUME / 需求变更 / 回退 | [hs-dev-continuity](skills/hs-dev-continuity/SKILL.md) | 恢复阶段、影响分析、有效基线 |

BUILD 的 L 路径为 `0→1→2→3→4→5→6`；M 仅补触达面，S 只做已清晰的局部变更。分级细则见 [right_sizing](references/right_sizing.md)，不得为走流程制造空文档。

## 横向：功能分派

| 触达面 | 功能子 Skill | 负责内容 |
|---|---|---|
| 产品目标、功能、业务流程 | [hs-dev-product](skills/hs-dev-product/SKILL.md) | PRD、规则、场景、MVP、原型验收 |
| 选型、系统边界、模块协作 | [hs-dev-architecture](skills/hs-dev-architecture/SKILL.md) | 范式、ADR、架构、模式权衡 |
| 界面、交互、前端结构与代码 | [hs-dev-frontend](skills/hs-dev-frontend/SKILL.md) | DESIGN.md、原型、组件、a11y、运行体验 |
| 后端、DB、API、方法契约 | [hs-dev-backend](skills/hs-dev-backend/SKILL.md) | 数据约束、接口、Adapter、方法与迁移 |
| 测试策略与执行证据 | [hs-dev-testing](skills/hs-dev-testing/SKILL.md) | TDD、契约/集成/回归、DoD 对账 |
| 索引、版本、词典与工程治理 | [hs-dev-governance](skills/hs-dev-governance/SKILL.md) | 共享工程设施及按开关启用的治理 |

例如“支付接口超时”是 debugging + backend/testing；“设计采购工作台”是 discovery + product/frontend；“继续支付任务”先 continuity，恢复后再确定过程。过程 Skill 管推进，功能 Skill 管专业结果，均不能自行扩大授权。

## 所有子 Skill 共同遵守

- **范围与确认**：保留开发者目标、范围和已确认决定。Agent 推导与真实确认分开；新增业务的 DB 设计、计费/权限/归属及关键契约按既有决策规则处理。
- **验收驱动流转**：每个实际阶段按 [阶段验收协议](references/stage_acceptance.md) 的标准、证据和有效确认流转；阶段工作完成时在回复中逐项展示全部待验收文档的文件名、绝对路径、版本及状态（含验收记录本身），不能只说“见文档”。模型自检只是候选结论。源语义变化使相关验收和派生 Pack 失效。
- **基线与优化闭环**：按 [基线、观测与分级优化](references/workflow_improvement.md) 登记完整需求分母、源摘要和派生依赖；实现/验收前核对有效性。致命问题立即修复并回归，习惯性问题积累案例后小步更新，其他问题只提示；评测不能自动改规则或代签验收。
- **测试与完成**：实现必有适用验证，测试全绿、静态检查零告警、严格一致性检查及需求/DoD 回收按 [testing](references/testing.md) 和 [quality_gates](references/quality_gates.md) 执行；不得假代码、伪造证据或静默砍功能。
- **只读边界**：EXPLORE 不建任务/PRD、不改状态、不初始化、不提交（trace 日志按 [skill_trace](references/skill_trace.md) 项目开关处理）；此约束传递到所有功能 Skill。
- **持续与恢复**：有独立可推进工作就继续；阶段待验收、必要决策或外部条件阻断时记录交接。续做沿用 plan/change，不重开需求。
- **执行轨迹（按项目开关）**：工程开启 trace 时，会话、路由、阶段、拍板与纠偏按 [skill_trace](references/skill_trace.md) 自报；任务/门禁/checkpoint 等由工具自动记录事实。缺省关闭时静默、不落盘、不阻断；复盘明确数据缺口，不以事件数证明质量。
- **共享单源与变化感知**：详规、模板、脚本维持既有路径；功能性细则只在对应子 Skill 按需加载。“只读一次”统一按 [装载缓存协议](references/load_latch.md#5-变化感知与装载缓存统一重读规则)：未变化且当前范围可用则复用，再次依赖时轻查元数据，变更/恢复/阶段及实现验收边界核对当前依赖摘要；变化或上下文缺失才重读必要片段，不每轮重读原文。[规范来源](references/standards_basis.md)区分公开阅读、标准范围及项目自定规则。
- **操作边界**：代码/设计修改前按既有 checkpoint 约定保留回退依据；默认本地 Commit，只有明确授权才 push/发布。不因选中治理 Skill 自动开启重型设施。

## 定位共享资源

主包根与目标工程根分开，详见 [运行协议](references/subskill_contract.md#2-包结构与安装边界)。本包的 `scripts/skill_ref_index.py search` 检索子入口/详规；`doc_index_db.py --root <工程根>` 检索业务文档；工具总览见 [README](README.md)。子 Skill 是本包组成部分，安装需保留整个目录树。
