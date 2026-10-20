---
name: hs-dev-skill
description: >-
  Coordinate software development, design, fixes, refactoring, tests and project
  investigation through safe workspace access, signal-based intent and activity
  dependencies. 开发、设计、修复、重构、验收、续做和只读分析；排除无关问答。
license: MIT
metadata:
  author: hardstone
  version: "6.0.0.0"
  runtime: "Python >= 3.11, SQLite FTS5; install complete bundle"
---

# hs-dev-skill

协调软件工程任务：识别用户期望的结果，选择当前过程，按需加载专业能力，并在条件变化时切换。入口不复制各过程的操作步骤，不要求每个任务重走完整流水线。

## 识别当前诉求

结合当前消息、已有对话和任务证据，先明确：

- **结果**：解释或评估、定位缺陷、改变行为、保留行为调整结构、形成设计、拆解任务，还是核验交付。
- **范围与约束**：目标对象、允许修改的范围，以及“只读”“先讨论”“保持行为”等明确要求。
- **现有条件**：是否已有 task_id、已明确的需求、设计、实施任务或验收标准；引用已有成果，不重复发现。
- **本轮动作**：区分用户最终目标与当前要求先完成的步骤；专业领域不单独决定过程。

关键词和分类器只提供候选信号，不替代语义判断。否定、引用、假设和背景描述不能直接作为执行意图。`classify` 返回 `NEEDS_MODEL` 时，由宿主模型结合上述上下文解释信号；`classify --model` 只记录有依据的分类，不得用它消除真实的需求歧义。

**无法判断需求，或多个解释会改变过程、预期产出、目标对象或修改范围时，必须请用户明确。** 简要列出候选解释及差别，只问影响决策的信息；用户明确前不选择依赖该答案的流程，不创建任务或执行相关修改。缺少信息不等于同意默认方案；不得用猜测或置信分数替用户决定。可以继续不依赖该答案的只读核实。

## 选择当前过程

按期望结果和已有条件选择一个主过程，再读取对应入口。表格按条件匹配，不是固定执行顺序。

| 用户诉求与已有条件 | 主过程 |
|---|---|
| 理解代码、解释架构、评估方案，仅要求分析 | [exploration](skills/hs-dev-exploration/SKILL.md) |
| 已观察到异常，需要定位原因或修复 | [debugging](skills/hs-dev-debugging/SKILL.md) |
| 明确保留可观察行为，调整现有结构 | [refactoring](skills/hs-dev-refactoring/SKILL.md) |
| 为已有项目重建并核实模型、接口、术语和文档索引 | [reverse](skills/hs-dev-reverse/SKILL.md) |
| 新需求的目标、场景、范围或预期行为需要共同明确 | [discovery](skills/hs-dev-discovery/SKILL.md) |
| 产品输入已明确，需要技术选型、架构、契约或验证环境设计 | [design](skills/hs-dev-design/SKILL.md) |
| 设计已明确，需要拆解任务和依赖、安排交付顺序 | [planning](skills/hs-dev-planning/SKILL.md) |
| 已有明确任务及必要设计，要求实现 | [implementation](skills/hs-dev-implementation/SKILL.md) |
| 对照清单和标准核验交付、收集验收证据 | [acceptance](skills/hs-dev-acceptance/SKILL.md) |
| 恢复已有任务、评估需求变化影响或回退检查点 | [continuity](skills/hs-dev-continuity/SKILL.md) |

边界与切换规则：

- 当前明确诉求决定本轮动作，历史任务补充条件。“分析这个设计的问题”进入只读分析，不能仅因出现“设计”进入设计流程。
- “继续”先恢复已有 task_id、约束和未完成项，再回到具体过程；不新建同义任务，不停留在交接摘要。
- “先分析，再修改”先完成分析；后续修改沿用已有授权与约束。分析结果若暴露影响范围的歧义，先请用户明确。
- “修复并顺便重构”先定位缺陷；仅在重构范围和保留行为要求已明确时安排后续重构，不借修复扩大范围。
- “了解现有项目”通常是 exploration；要求建立经过核实的项目知识和文档体系才进入 reverse。
- “做前端”“改后端”只确定领域；仍需根据结果和已有条件选择过程。缺失的必要前置产物按实际需要补齐，不自动从头走 A～H。
- 明确的需求梳理诉求可进入 discovery；不知道用户要解释、修改还是重建时，应先询问，不能把 discovery 当作所有不确定请求的默认入口。

## 按需加载与执行

路由审查样例见[Skill 加载矩阵](../hs-dev-docs/skill-loading.md)，只在体系审查时读取，不加入日常任务上下文。

需要选择通用功能、质量属性或工程实践参考时，再读[目录索引](share/catalogs/catalogs.idx)，并只打开命中的单项资料。

过程确定后，从[领域入口](share/skills/skills.idx)只加载实际需要的产品、前端/后端/客户端框架、前端、后端、测试或治理 Skill。**任何包含前端界面设计、实现、调试、重构或评审的任务，默认加载 `hs-dev-frontend-base`；再按目标平台加载对应的端侧 Skill。**根据目标代码和项目配置识别平台：Web 加载 `hs-dev-frontend-web`，Android 加载 `hs-dev-frontend-android`，iOS 加载 `hs-dev-frontend-ios`，Windows 加载 `hs-dev-frontend-windows`，macOS 加载 `hs-dev-frontend-mac`，Linux 加载 `hs-dev-frontend-linux`。跨端任务加载实际涉及的平台 Skill，不把所有平台入口一起加载。平台暂时无法判断时先加载 Base，并依据代码或项目配置继续识别；只有后续工作确实依赖平台差异且无法从工程判断时，才向用户澄清。**任何涉及移动端或桌面客户端框架设计、实现、调试、重构或评审的任务，默认加载 `hs-dev-framework-client-base`；再按目标操作系统加载 `hs-dev-framework-client-android`、`hs-dev-framework-client-ios`、`hs-dev-framework-client-windows` 或 `hs-dev-framework-client-linux`。**跨平台任务只加载实际目标平台；macOS 客户端当前使用框架 Base，界面任务另加载 macOS 前端特性。平台不明时先依据工程文件和项目配置识别。若任务还涉及 Web 应用框架或服务端框架，再加载相应框架设计 Skill。由当前过程根据任务缺口选择具体活动清单，不先读取 workflow 总目录、阶段目录或全部活动。跨过程任务按依赖顺序切换，不预先加载所有入口。

上下文按“当前目标对象 → 必要约束和证据 → 实际缺口”逐步收窄：先定位本次代码、产物章节及已有决定，只读命中条件的活动清单。上游依赖优先引用有效产物的相关单元，不递归加载上游全部流程资料；发现缺失、失效或本次影响后才扩大。读取前说明选择理由，完成当前目标后停止扩展。活动地图仅供活动无法定位或明确审阅全流程结构时导航；任务明确要求完整范围时可逐项覆盖，但不要求同时装入全部正文。

第一项工程操作执行 `python <安装根>/hs-dev-skill/scripts/hs_dev.py --root <工程根> status`。在途修改等待；中断或漂移进入恢复，不读取混合版本。首次工程显式 init。开始逻辑任务时展示 `hs-dev-skill | 版本 | 场景 | 确认模式 | trace on/off`；宿主集成只展示一次，底层命令 JSON 通过 meta 标识来源。

- 只读咨询不建任务、不修改业务内容、不自动修复索引。协调状态读取与可选 trace 不等同业务修改。
- 内容通过 `context @request.json` 获取，必要选择器标记 `required: true`；检查 status 与 coverage 后使用 body。恢复快照和恢复历史不提供给模型。具体读取规则见[索引与上下文](share/indexing/protocol.md)。
- 进入受管修改前读取[执行协议](share/core/execution.md)，执行操作凭据、快照、验证、发布与恢复要求；安全门禁独立于意图分类。
- 活动开始前核验必要上游；已有已完成结果或明确绑定的已验收产物可以复用。需要确认或验收时读取[验收协议](share/core/acceptance.md)，不以索引重建代替验收，不代签用户确认。
- trace 是独立开关，仅在使用时读取[追踪协议](share/support/trace.md)。具体命令见[命令说明](../README.md)；完整[目标设计](../hs-dev-docs/skill-redesign.md)用于体系审阅，不要求每次通读。
