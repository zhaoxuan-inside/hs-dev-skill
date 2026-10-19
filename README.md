```text
  _   _ ____          ____  _______     __
 | | | / ___|        |  _ \| ____\ \   / /
 | |_| \___ \  _____ | | | |  _|  \ \ / /
 |  _  |___) ||_____|| |_| | |___  \ V /
 |_| |_|____/        |____/|_____|  \_/

                 S K I L L
       AI -> DOCUMENTS -> CODE
```

<div align="center">

# hs-dev-skill

**AI 驱动文档，文档驱动代码。**

让 Agent 开发有依据，开发过程可观测、可追溯、知原委。

`v6.0.0.0` · `Python 3.11+` · `SQLite FTS5` · `MIT`

[理念](#理念) · [核心亮点](#核心亮点) · [安装与接入](#安装与接入) · [模式](#模式) · [入口与工作流程](#入口与工作流程) · [Skill 目录](#skill-目录) · [产出目录](#产出目录)

</div>

---

## 理念

**AI 驱动文档，文档驱动代码。** 这是 hs-dev-skill 的核心理念。

AI 将沟通中的目标、需求、约束和决策整理为持续维护的项目文档；文档进一步明确功能行为、架构、接口契约与验证标准，成为 Agent 规划任务、编写代码和检查结果的依据。实现与验证中的发现再反馈到文档，让后续开发始终有据可依。

```text
 INTENT --> AI --> DOCUMENTS --> CODE --> VERIFICATION
                      ^                       |
                      |                       |
                      +------ FEEDBACK <------+
```

这套协作方式希望让开发者始终能够回答四个问题：

| 目标 | 需要回答的问题 | 承载这些信息的材料 |
| :--- | :--- | :--- |
| **开发有依据** | 要做什么、遵循哪些约束、怎样才算完成？ | 需求、设计、契约、任务与检查标准。 |
| **过程可观测** | 目前做到哪里、完成了什么、还有哪些阻碍？ | 当前活动、任务进度、检查结果、交付材料与未决项。 |
| **结果可追溯** | 这项实现来自哪个需求，经过什么验证，由谁确认？ | 产物依赖、变更记录、验证证据与确认决定。 |
| **决策知原委** | 为什么这样设计、为何这样修改、判断依据是什么？ | 设计理由、约束来源、问题根因与变更原因。 |

文档贯穿需求、设计、实现和验证，承载项目的共同认知。任务续做、上下文装配、检查确认和恢复机制，围绕这条主线协同工作。

## 核心亮点

| 亮点 | 对实际协作的帮助 |
| :--- | :--- |
| **AI 驱动文档，文档驱动代码** | 将目标、需求与决策沉淀为文档，以设计、契约和检查标准指导实现，并用实现与验证结果持续校正文档。 |
| **进度可见，来龙去脉可查** | 通过任务状态、交付材料、依赖关系、变更记录与验证证据，了解当前进展，追溯结果来源与决策依据。 |
| **按场景进入，按依赖推进** | 覆盖开发、设计、修复、重构、调查与续做；只展开受影响活动，支持引用已验收的上游产物。 |
| **宏观与细节分层** | 产品构想、功能行为、技术决策、工程契约与交付切片各有职责。 |
| **上下文按需装配** | 定位文件、Markdown 章节、Python 符号和行区间；必要材料连同依赖整体交付，预算不足时明确报告。 |
| **验证与版本绑定** | 检查证据关联实际内容摘要，发布前后复核，防止代码变化后继续沿用旧验证结论。 |
| **确认粒度可选** | 可由模型核验，也可按阶段或内部活动交由开发者确认；统一展示材料、检查结果和未决项。 |
| **修改可恢复，任务可延续** | 操作身份、快照、变更记录与回退协同工作，保留中断现场和继续依据。 |
| **任务追踪支持 Skill 演进** | 开发者可开启 trace，记录不含敏感信息的任务执行摘要，借助 Agent 分析 Skill 的不足并优化，也可分享给作者。 |
| **轻量运行** | 无第三方运行依赖，使用 SQLite FTS5。 |

## 安装与接入

### 1. 准备运行环境

需要 **Python 3.11 或以上版本**，且 Python 的 SQLite 支持 **FTS5**。宿主 Agent 需要能够读取 Skill 文件并执行本地 Python 命令。

### 2. 安装完整仓库

将完整仓库放到宿主支持的 Skill 安装目录，目录名使用 `hs-dev-skill`。以宿主配置的 Skill 目录为准；若该目录为 `~/.codex/skills`，可执行：

```bash
git clone https://github.com/zhaoxuan-inside/hs-dev-skill.git ~/.codex/skills/hs-dev-skill
```

其他 Agent 使用其对应的 Skill 目录或本地加载机制。安装后按宿主要求重新加载 Skill。

> 安装时保留完整目录。主入口依赖 `hs-dev-skill/references/` 与 `hs-dev-skill/scripts/` 等内容，单独复制 `SKILL.md` 无法提供完整能力。

### 3. 在目标工程中接入

向 Agent 明确提出目标，例如：

```text
使用 hs-dev-skill，帮我梳理这个项目的需求和功能设计。
```

也可以从已有工程中的具体问题开始：

```text
使用 hs-dev-skill，修复订单接口超时，先复现并定位根因。
```

Agent 先检查工作区状态；首次使用时显式初始化目标工程。手动接入时，可执行以下命令，路径替换为实际安装位置和工程位置：

```bash
python /path/to/skill-root/hs-dev-skill/scripts/hs_dev.py --root /path/to/project status
python /path/to/skill-root/hs-dev-skill/scripts/hs_dev.py --root /path/to/project init
```

`init` 仅用于尚未初始化的工程。已有任务通过状态检查选择继续或恢复。Skill 程序保留在安装位置，项目文档和运行数据保存在目标工程内。

## 模式

模式决定**由谁、在什么粒度上确认结果**。三种模式都要求执行适用检查并保存证据。

| 模式 | 确认方式 | 适合的协作节奏 |
| :--- | :--- | :--- |
| `mute` | 模型核验检查项与证据，记录模型确认 | 希望减少人工确认交互，由 Agent 连续推进。 |
| `stage` | 开发者按阶段审阅并确认，**默认模式** | 在关键阶段把关，同时保留阶段内的执行连续性。 |
| `activity` | 开发者按内部活动审阅并确认，如 `E2`、`G1` | 需要更细粒度地检查契约、实现和验证结果。 |

项目级配置位于目标工程的 `hs-dev-skill/config/config.json`：

```json
{
  "execution": {
    "mode": "stage"
  }
}
```

创建任务时也可通过 `task-start --mode mute|stage|activity` 指定。配置优先级为：**直接参数 > 任务 > 项目 > 主机 > 默认值**。

人工确认保留开发者的真实决定；暂缓会阻断相关依赖。`mute` 的模型确认会明确标识来源。`trace` 是独立的追踪开关，不改变确认模式。

## 入口与工作流程

### 主入口：从目标选择路径

[SKILL.md](SKILL.md) 是宿主加载的主入口，负责安全检查、意图判断和入口选择。信号不足或冲突时，由宿主模型结合当前目标判断路径。

```text
USER REQUEST
     |
     v
WORKSPACE STATUS
     |
     +-- SAFE ----------> INTENT --> SCENARIO --> ACTIVITIES
                                                       |
     +-- BUSY ----------> WAIT                         v
     |                                      CHECKS + EVIDENCE
     +-- INTERRUPTED ---> RECOVERY                     |
                                                       v
                                               CONFIRMATION
```

只读探索在返回分析与位置证据后结束，不进入任务创建和阶段验收。其余场景根据目标选择活动，并按模式确认结果。

### 活动地图：从构想到交付

下图展示完整开发路径，字母对应[活动地图](hs-dev-skill/references/workflow/README.md)。它用于定位工作阶段；具体任务按依赖选择活动，允许复用已有产物。

```text
 [ A ] --> [ B ] --> [ C ] --> [ D ]
                                 |
                                 v
 [ H ] <-- [ G ] <-- [ F ] <-- [ E ]
```

| 阶段 | 职责 | 阶段 | 职责 |
| :--- | :--- | :--- | :--- |
| A | 产品构想与宏观信息收集 | E | 工程契约与验证环境构建 |
| B | 功能体系与产品行为设计 | F | 交付规划与执行准备 |
| C | 质量约束与技术决策 | G | 实现、测试与增量集成 |
| D | 架构与框架设计 | H | 交付、验收与反馈 |

### 场景入口：每条路径如何工作

下表中的流程概括各入口的职责；实际执行范围由任务目标、活动依赖和已有证据共同决定。

| 入口 | 何时进入 | 工作流程 |
| :--- | :--- | :--- |
| [需求与产品设计](hs-dev-skill/references/skills/process/hs-dev-discovery/SKILL.md) | 新产品、新功能、需求梳理 | 收集问题、愿景与边界（A）→ 提取功能 → 逐功能设计行为与交互 → 串联整体产品（B）。 |
| [工程设计](hs-dev-skill/references/skills/process/hs-dev-design/SKILL.md) | 技术选型、架构、契约与验证环境 | 核验产品输入 → 明确质量约束与技术选择（C）→ 设计架构与协作（D）→ 准备数据、接口、测试、Mock 与配置（E）。 |
| [任务规划](hs-dev-skill/references/skills/process/hs-dev-planning/SKILL.md) | 将设计转成可执行任务 | 核验设计输入 → 划分交付切片 → 映射需求、任务与方法 → 装配上下文 → 准备恢复依据（F）。 |
| [实现与集成](hs-dev-skill/references/skills/process/hs-dev-implementation/SKILL.md) | 实施已明确的工程任务 | 核验契约及依赖 → 按切片实现 → 真实验证 → 增量集成 → 核验文档、代码、索引与任务记录的一致性（G）。 |
| [验收](hs-dev-skill/references/skills/process/hs-dev-acceptance/SKILL.md) | 检查活动或阶段的交付结果 | 核对检查项 → 展示材料、证据与问题 → 按模式记录决定 → 通过后供下游使用；未通过则保留原因及下一动作。 |
| [缺陷修复](hs-dev-skill/references/skills/process/hs-dev-debugging/SKILL.md) | 实际报错、超时、失败或缺陷 | 复现并建立现状基线（H1）→ 核验需求与契约 → 定位根因 → 选择受影响活动 → 修复并执行回归验证。 |
| [结构重构](hs-dev-skill/references/skills/process/hs-dev-refactoring/SKILL.md) | 保持行为并改善结构 | 阅读真实代码并建立行为保护（H1）→ 核验业务边界（A/B）→ 调整受影响设计与实现（C～G）→ 验证行为保持一致。 |
| [存量调查](hs-dev-skill/references/skills/process/hs-dev-reverse/SKILL.md) | 接手已有工程、重建可证实的契约 | 现状取证 → 区分观察与推断 → 重建契约与关系 → 标记未知需求 → 按活动逐步纳管。 |
| [只读探索](hs-dev-skill/references/skills/process/hs-dev-exploration/SKILL.md) | 理解代码、解释设计、分析现有流程 | 检查工作区状态 → 只读定位 → 整理位置证据 → 返回结论；不创建任务、快照或业务文档。 |
| [任务续做](hs-dev-skill/references/skills/process/hs-dev-continuity/SKILL.md) | 继续任务、评估变更影响或回退 | 复用任务 ID → 核对未完成项及一致性 → 识别受影响范围 → 继续执行或按决定回退 → 更新任务状态。 |

### 专业入口：按涉及领域协作

场景入口组织流程，专业入口负责当前领域的设计或实施，随任务按需加载。

| 入口 | 工作流程 |
| :--- | :--- |
| [产品](hs-dev-skill/references/skills/domain/hs-dev-product/SKILL.md) | 明确业务目标与边界 → 设计功能和业务流程 → 整理产品产物与审阅依据。 |
| [前端框架设计](hs-dev-skill/references/skills/domain/hs-dev-framework-frontend/SKILL.md) | 选择 Web 前端框架 → 设计应用模块、路由、状态和服务端调用边界。 |
| [后端框架设计](hs-dev-skill/references/skills/domain/hs-dev-framework-backend/SKILL.md) | 设计服务端模块分层、依赖方向、运行模型和外部适配边界。 |
| [客户端框架基础](hs-dev-skill/references/skills/domain/hs-dev-framework-client-base/SKILL.md) | 提供各客户端平台的共通框架设计原则；按目标端配合平台入口使用。 |
| [Android 客户端框架](hs-dev-skill/references/skills/domain/hs-dev-framework-client-android/SKILL.md) | 设计 Android 应用组件、进程生命周期、系统能力适配和构建边界。 |
| [iOS 客户端框架](hs-dev-skill/references/skills/domain/hs-dev-framework-client-ios/SKILL.md) | 设计 iOS 应用与 Scene 生命周期、状态恢复、系统能力及构建边界。 |
| [Windows 客户端框架](hs-dev-skill/references/skills/domain/hs-dev-framework-client-windows/SKILL.md) | 设计 Windows 应用窗口/进程模型、系统集成、打包和更新边界。 |
| [Linux 客户端框架](hs-dev-skill/references/skills/domain/hs-dev-framework-client-linux/SKILL.md) | 设计 Linux 桌面应用运行环境、桌面集成、分发和更新边界。 |
| [前端基础](hs-dev-skill/references/skills/domain/hs-dev-frontend-base/SKILL.md) | 提供各端通用的界面、组件、交互、可访问性和实现要求；配合具体平台入口使用。 |
| [Web 前端](hs-dev-skill/references/skills/domain/hs-dev-frontend-web/SKILL.md) | 应用浏览器布局、输入、导航、响应式和浏览器兼容特性。 |
| [Android 前端](hs-dev-skill/references/skills/domain/hs-dev-frontend-android/SKILL.md) | 应用 Android 导航、生命周期、权限、系统返回和设备适配特性。 |
| [iOS 前端](hs-dev-skill/references/skills/domain/hs-dev-frontend-ios/SKILL.md) | 应用 iOS 导航、安全区、权限、生命周期和辅助功能特性。 |
| [Windows 前端](hs-dev-skill/references/skills/domain/hs-dev-frontend-windows/SKILL.md) | 应用 Windows 窗口、输入、系统集成、辅助功能和打包特性。 |
| [macOS 前端](hs-dev-skill/references/skills/domain/hs-dev-frontend-mac/SKILL.md) | 应用 macOS 窗口、菜单、快捷键、系统集成、辅助功能和分发特性。 |
| [Linux 前端](hs-dev-skill/references/skills/domain/hs-dev-frontend-linux/SKILL.md) | 应用 Linux 桌面环境、显示协议、输入方式、辅助功能和系统集成特性。 |
| [后端](hs-dev-skill/references/skills/domain/hs-dev-backend/SKILL.md) | 核验业务与数据约束 → 设计数据、接口及方法契约 → 实施并验证后端行为。 |
| [测试](hs-dev-skill/references/skills/domain/hs-dev-testing/SKILL.md) | 识别适用检查 → 执行行为、契约、集成或回归验证 → 记录证据与未决问题。 |
| [治理](hs-dev-skill/references/skills/domain/hs-dev-governance/SKILL.md) | 核验已启用的规范 → 维护文档索引、术语、版本与打包一致性 → 检查治理结果。 |

### 支撑入口：恢复、更新与追踪

| 入口 | 工作流程 |
| :--- | :--- |
| [恢复](hs-dev-skill/references/skills/support/hs-dev-recovery/SKILL.md) | 保存快照与变更记录 → 检测中断及冲突 → 恢复 → 核验一致性 → 按保留策略清理。 |
| [更新](hs-dev-skill/references/skills/support/hs-dev-update/SKILL.md) | 获得明确更新授权 → 校验当前完整包 → 暂存与替换 → 失败时恢复。 |
| [追踪](hs-dev-skill/references/skills/support/hs-dev-trace/SKILL.md) | 按需启用 → 记录本项目摘要事件 → 有界查询与轮转；默认关闭。 |

### Trace：从任务执行中改进 Skill

trace 用于记录 **Skill 的任务执行过程**，保留关联任务的执行事件与摘要，帮助开发者分析 Skill 在流程组织、入口选择、上下文获取和执行效率等方面的不足，为 Skill 演进提供依据。

**默认关闭，由开发者自主开启。** 可在项目配置 `hs-dev-skill/config/config.json` 中加入以下配置，也可通过全局参数 `--trace` 临时开启：

```json
{
  "trace": {
    "enabled": true
  }
}
```

trace 随任务记录，事件通过任务 ID 关联；文件按项目集中存放在 `hs-dev-skill/trace/`，可使用 `trace-query --task-id TASK_ID` 筛选指定任务的记录。记录仅保留允许的摘要字段，不包含凭证、完整对话、代码或文档正文等敏感内容。

开发者可以将筛选后的 trace 交给 Agent，分析问题、提出改进并自行优化 Skill；也可以主动发送给 Skill 作者，作为改进反馈。分析与优化由开发者发起，trace 本身不会自动修改 Skill，也不会自动上传记录。

## Skill 目录

安装根保留主入口与项目说明，`hs-dev-doc/` 保存 Skill 自身的文档体系，内部 `hs-dev-skill/` 集中保存参考资料和辅助程序。

```text
hs-dev-skill/
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- hs-dev-doc/
|   |-- README.md
|   |-- skill-redesign.md
|   |-- implementation-verification.md
|   |-- directory-layout.md
|   `-- host-adapters/
`-- hs-dev-skill/
    |-- references/
    |   |-- README.md
    |   |-- skills/
    |   |   |-- process/
    |   |   |-- domain/
    |   |   `-- support/
    |   |-- workflow/
    |   |-- catalogs/
    |   |-- schemas/
    |   |-- templates/
    |   |-- core/
    |   |-- product/
    |   |-- architecture/
    |   |-- engineering/
    |   |-- testing/
    |   |-- context/
    |   |-- indexing/
    |   `-- support/
    `-- scripts/
        |-- hs_dev.py
        |-- build_docs.py
        |-- benchmark_context.py
        |-- pyproject.toml
        |-- hs_dev/
        |   |-- data/
        |   |-- indexing/
        |   `-- support/
        `-- tests/
```

| 路径 | 说明 |
| :--- | :--- |
| `SKILL.md` | 主入口与执行约束，宿主从这里理解如何使用 Skill。 |
| `hs-dev-doc/` | Skill 自身的设计、演进与验证资料；可选宿主适配示例保留在 `host-adapters/`，核心运行不依赖它。 |
| `hs-dev-skill/references/skills/` | 过程、专业领域及恢复、更新、追踪入口。 |
| `hs-dev-skill/references/workflow/` | A～H 阶段及内部活动的定义和检查依据。 |
| `hs-dev-skill/references/catalogs/` | 通用功能、质量属性与工程实践参考。 |
| `hs-dev-skill/references/schemas/` | 活动、元数据、关系与上下文请求的数据格式约束。 |
| `hs-dev-skill/references/templates/` | 设计与交接等文档模板。 |
| `hs-dev-skill/references/` 的其他分类 | 执行、验收、上下文、恢复等协议及产品、架构、测试等专题参考。 |
| `hs-dev-skill/scripts/` | CLI 入口、构建和基准工具，以及 Python 包配置。 |
| `hs-dev-skill/scripts/hs_dev/` | 任务、配置、索引、上下文、验证与恢复等程序实现；`data/` 保存随包活动数据。 |
| `hs-dev-skill/scripts/tests/` | 辅助程序的自动化测试。 |

进一步阅读：[场景与领域索引](hs-dev-skill/references/skills/skills.idx) · [活动地图](hs-dev-skill/references/workflow/README.md) · [参考资料](hs-dev-skill/references/README.md) · [文档体系](hs-dev-doc/README.md)

## 产出目录

在**目标工程**中，当前有效文档保存在 `hs_dev_docs/`，任务与运行数据保存在 `hs-dev-skill/`。后者与安装包同名，但内容和用途不同。

下图展示初始化及后续执行可能形成的结构；目录按实际需要创建，`<...>` 表示随任务变化的名称。

```text
project/
|-- <application-files>/
|-- hs_dev_docs/
|   |-- README.md
|   |-- foundation/
|   |   |-- README.md
|   |   |-- object_graph.json
|   |   `-- tag_aliases.json
|   `-- <activity-documents>/
`-- hs-dev-skill/
    |-- README.md
    |-- config/
    |   `-- config.json
    |-- state/
    |   `-- workspace.sqlite
    |-- task_index.jsonl
    |-- tasks/
    |   `-- <task_id>/
    |       |-- task.json
    |       |-- current.md
    |       |-- config/
    |       |-- activities/
    |       |   `-- <activity_id>/
    |       |       `-- results.json
    |       |-- acceptance/
    |       |   `-- decisions.json
    |       `-- evidence/
    |-- evidence_archive/
    |-- index/
    |   |-- files.jsonl
    |   |-- catalog.sqlite
    |   `-- publication.json
    |-- cache/
    |-- recovery/
    |   |-- snapshots/
    |   |-- operations/
    |   `-- changelog/
    `-- trace/
```

| 路径 | 保存什么 |
| :--- | :--- |
| `hs_dev_docs/` | 当前有效的项目知识：需求、设计、契约、交付等文档；按活动需要组织，不预先铺满所有阶段。 |
| `hs_dev_docs/foundation/` | 项目说明、术语与权威产物登记等基座资料；对象关系和标签别名在使用时维护。 |
| `hs-dev-skill/config/` | 项目级 Skill 配置，包括确认模式。 |
| `hs-dev-skill/state/` | 工作区安全状态及运行协调信息。 |
| `hs-dev-skill/task_index.jsonl` | 任务状态、更新时间和元数据摘要索引。 |
| `hs-dev-skill/tasks/<task_id>/` | 单个任务的范围、进度、检查结果、确认决定和验证证据。 |
| `task.json`、`current.md` | 结构化任务记录与便于续做的当前任务摘要。 |
| `activities/`、`acceptance/` | 内部活动检查结果，以及材料审阅、确认和历史决定。 |
| `evidence/`、`evidence_archive/` | 验证报告与输出，以及按任务保留策略归档的证据。 |
| `index/` | 文件索引、语义单元检索数据库和当前发布版本记录。 |
| `cache/` | 索引服务等运行缓存；启用服务时可包含通信 socket。 |
| `recovery/` | 恢复快照、操作记录及变更日志，用于中断处理与回退。 |
| `trace/` | 开发者开启后记录的任务执行摘要，通过任务 ID 关联，用于分析不足、辅助优化 Skill 或向作者反馈；默认关闭。 |

应用代码、配置、测试及 Mock 内容仍放在目标工程对应位置。恢复历史不进入模型上下文，运行目录也不作为普通业务源参与索引发布。未完成任务的状态和恢复数据应通过相应命令管理，避免手动删除。

有关使用细节，可继续查看[执行协议](hs-dev-skill/references/core/execution.md)、[验收协议](hs-dev-skill/references/core/acceptance.md)、[上下文协议](hs-dev-skill/references/context/README.md)和[恢复协议](hs-dev-skill/references/support/recovery.md)。
