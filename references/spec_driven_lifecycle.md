# 文档驱动开发（DDD）全生命周期驱动引擎指南

**项目适用性**：视觉、DESIGN.md、原型与 UI vibe_spec 仅在有 UI 时必需；无 UI 按 `project_types.md` 与 `product_design.md` §5.2 标记 NA，保留 PRD、API/CLI/库契约、可执行场景和业务冻结确认。

**阶段验收入口**：0A/0B 验收点见 [`product_acceptance.md`](product_acceptance.md)，阶段 1～6 只读 [`engineering_acceptance.md`](engineering_acceptance.md) 当前节；记录使用 [`stage_acceptance 模板`](../resources/templates/process/stage_acceptance.md)。通用判定以 [`stage_acceptance.md`](stage_acceptance.md) 为准。

本指南定义 `hs-dev-skill` 的 **7 阶段满配链（L）**。  
**任意需求第一步**先做变更分级：见 **[right_sizing.md](right_sizing.md)**（S/M 缩短路径；未分级禁止按满配开工）。

交互边界：**[confidence_decision.md](confidence_decision.md)**、**[learn_and_prefer.md](learn_and_prefer.md)**。  
架构/UI/API 详设与实现按需：**[dev_paradigm.md](dev_paradigm.md)**（先选型）、**[ddd_design.md](ddd_design.md)**（仅 DDD 档）、**[backend_arch.md](backend_arch.md)**、**[frontend_arch.md](frontend_arch.md)**、**[frontend_craft.md](frontend_craft.md)**、**[api_engineering.md](api_engineering.md)**。

```text
  [分级 S|M|L] -- right_sizing.md
       |
       +-- S/M: 缩短链（见 right_sizing）
       +-- L: 下列满配 0→6
  [阶段 0] PRD 冻结门禁
  [阶段 1] 选型与 ADR
  [阶段 2] 领域与架构
  [阶段 3] 四要素（DB+API+六元组+调用链）
  [阶段 4] 任务与 context_pack
  [阶段 5] 三同步实现
  [阶段 6] 门禁 + 归档 + 本地 Commit
```

### 持续推进与合法停点

- 不要求单次会话跑完；无待确认事项时须沿**当前路径**推进至终点。
- 合法停点：阶段待验收、询问闸门、（M/L）冻结未过、外部依赖 `BLOCKED`。确认后立即继续。

### 阶段依赖与跃迁总则

- **L**：`0 → 1 → 2 → 3 → 4 → 5 → 6`；0→1 须产品冻结门禁。
- **M/S**：按 `right_sizing.md`；禁止为空跑阶段制造空 ADR/空四要素。
- 所有实际阶段跃迁：按 [`stage_acceptance.md`](stage_acceptance.md) 核对当前阶段规则、证据、输入版本和开发者验收记录；不要求每阶段全文请确认，但必须提交验收摘要。Agent 自检、产出齐套或脚本成功不能替代验收。
- 暴露产品语义未决：回退阶段 0（或升为 M/L）闭合后再前进。

---

<!-- HS_SECTION_INDEX -->

**按业务装载**：正文已拆成独立文件。先沿用本页公共约束，只打开当前业务/阶段需要的分册；不要顺序读全套。分册独立进行变化检查；迁移后旧的行号/摘要须重新定位，已有签收不得自动迁移。

## 阶段 0：产品设计与分阶段规划冻结 (Product Design & Phased Roadmap)

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

### 1. 核心目标

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

### 2. 阶段执行流程 (0.1 宏观品味宪章 → 0A 产品设计沟通含 MVP 范围裁定 → 0A' 微观特性设计（限 MVP）→ 0B 分阶段规划 → 0C 详细功能与规模评估（限 MVP）)

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

#### 阶段 0.1：确立项目级宏观品味宪章 (Project Design Charter, 仅项目启动或全局重构时)

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

#### 阶段 0A：产品设计沟通（审讯式 · 先定 MVP 范围，再写规格）

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

#### 阶段 0A'：微观特性探索与双视图设计 (Feature Discovery & Dual Views, 限 MVP 范围)

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

#### 阶段 0B：分阶段实施规划（记录·源自审讯结论）(Phased Roadmap)

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

#### 阶段 0C：MVP 详细功能设计、整体交互逻辑与规模评估 (Detailed Interaction & Scale Assessment · 限 MVP 范围)

正文见 [lifecycle/product_workflow.md](lifecycle/product_workflow.md)。

### 3. 产出文档（一源双视图 + 可交互 HTML 预览 + 决策日志）

正文见 [lifecycle/product_delivery.md](lifecycle/product_delivery.md)。

### 4. 阶段 0 冻结门禁（进入阶段 1 的硬前提）

正文见 [lifecycle/product_delivery.md](lifecycle/product_delivery.md)。

## 阶段 1：技术选型与论证 (Tech Selection & ADR)

正文见 [lifecycle/tech_selection.md](lifecycle/tech_selection.md)。

### 1. 核心目标

正文见 [lifecycle/tech_selection.md](lifecycle/tech_selection.md)。

### 2. Agent 行为准则

正文见 [lifecycle/tech_selection.md](lifecycle/tech_selection.md)。

### 3. 产出文档

正文见 [lifecycle/tech_selection.md](lifecycle/tech_selection.md)。

### 4. 阶段门禁

正文见 [lifecycle/tech_selection.md](lifecycle/tech_selection.md)。

## 阶段 2：范式落地与架构设计 (Paradigm & Architecture)

正文见 [lifecycle/architecture.md](lifecycle/architecture.md)。

### 1. 核心目标

正文见 [lifecycle/architecture.md](lifecycle/architecture.md)。

### 2. Agent 行为准则

正文见 [lifecycle/architecture.md](lifecycle/architecture.md)。

### 3. 产出文档

正文见 [lifecycle/architecture.md](lifecycle/architecture.md)。

### 4. 阶段门禁

正文见 [lifecycle/architecture.md](lifecycle/architecture.md)。

## 阶段 3：详细规格设计四要素 (Detailed Spec Design)

正文见 [lifecycle/detailed_design.md](lifecycle/detailed_design.md)。

### 1. 核心目标

正文见 [lifecycle/detailed_design.md](lifecycle/detailed_design.md)。

### 2. 四维产出物

正文见 [lifecycle/detailed_design.md](lifecycle/detailed_design.md)。

### 3. 阶段门禁

正文见 [lifecycle/detailed_design.md](lifecycle/detailed_design.md)。

## 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

正文见 [lifecycle/task_planning.md](lifecycle/task_planning.md)。

### 1. 核心目标

正文见 [lifecycle/task_planning.md](lifecycle/task_planning.md)。

### 2. Context Pack 机器装配法则 (VibeCoding Assembly Rules)

正文见 [lifecycle/task_planning.md](lifecycle/task_planning.md)。

## 阶段 5：开发三同步实现 (Implementation & Three-Sync)

正文见 [lifecycle/implementation.md](lifecycle/implementation.md)。

### 1. 核心目标

正文见 [lifecycle/implementation.md](lifecycle/implementation.md)。

### 2. 执行原则

正文见 [lifecycle/implementation.md](lifecycle/implementation.md)。

## 阶段 6：全层级门禁自检与交付归档 (Quality Gate & Closure)

正文见 [lifecycle/delivery.md](lifecycle/delivery.md)。

### 1. 核心目标

正文见 [lifecycle/delivery.md](lifecycle/delivery.md)。

### 2. 自检动作

正文见 [lifecycle/delivery.md](lifecycle/delivery.md)。

