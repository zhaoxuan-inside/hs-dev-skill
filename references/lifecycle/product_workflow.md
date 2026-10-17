# 阶段 0：产品设计与分阶段规划冻结 (Product Design & Phased Roadmap)

**何时读**：处理阶段 0：产品设计与分阶段规划冻结 (Product Design & Phased Roadmap)时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 阶段 0：产品设计与分阶段规划冻结 (Product Design & Phased Roadmap)

### 1. 核心目标
全面强化专业产品设计能力，并通过**两层解耦架构（宏观品味宪章 + 微观特性规格）**与**MVP 范围裁定（并入产品设计沟通）+ 分阶段实施规划**，杜绝一次性全量研发 (Big Bang)，产出可冻结的专业级产品设计方案与分阶段规划书，作为后续研发路径的权威真理源。

**两层解耦与产出边界铁律**：
1. **宏观层：项目级设计系统宪章 (Macro Product Taste & Design System Charter)**：
   - 固化于**项目根目录 `DESIGN.md`**（并在 `_01_product_vision/` 存档）；
   - 定义全项目的真实物理隐喻（对标具象产品）、调色盘与 Tokens、Anti-Slop 审美红线与 10 星惊喜标准。
   - 具有全局跨特性约束力，单次定义、长期驻留，防止多功能各自发明设计规范造成风格撕裂。
2. **微观层：特性级功能规格与交互原型 (Micro Feature Construction Specs)**：
   - 存放于 `_02_feature_spec/_01_human_prd/{feature}_prd.md`、`_02_feature_spec/_02_vibe_spec/{feature}_vibe_spec.md` 及原型中；
   - 顶部必须显式声明 `Inherits: /DESIGN.md`，禁止私自重定义全局美学与色盘，专注模块业务流、认知层级与组件局部多态。

> [!IMPORTANT]
> **严禁底层技术细节反向侵入产品设计**：
> 严禁在阶段 0 的 PRD、原型或规划文档中提前塞入底层技术选型（如 MySQL vs PG）、物理数据库 DDL、接口代码实现签名、分布式 Saga 补偿、代码单元测试覆盖率指标等工程实现细节！这些是阶段 1（选型）至阶段 3（四要素详设）的职责。产品设计阶段只对产品的设计语言与功能规格负责。

### 2. 阶段执行流程 (0.1 宏观品味宪章 → 0A 产品设计沟通含 MVP 范围裁定 → 0A' 微观特性设计（限 MVP）→ 0B 分阶段规划 → 0C 详细功能与规模评估（限 MVP）)

#### 阶段 0.1：确立项目级宏观品味宪章 (Project Design Charter, 仅项目启动或全局重构时)
- 在项目根目录创建并固化 `DESIGN.md`（详见 [`design_md.md`](../design_md.md) 与 [`product_design.md`](../product_design.md) §0.1）；
- 确立具象物理隐喻（如 Linear/Stripe/Raycast，严禁假大空词汇）、基准 Design Tokens、Anti-Slop 审美禁令（禁止紫色渐变/无意义动画/居中文案等 AI 滥觞）、10 星惊喜门槛；
- 作为后续所有特性功能 PRD、原型与 VibeSpec 的唯一继承根。

#### 阶段 0A：产品设计沟通（审讯式 · 先定 MVP 范围，再写规格）
> [!IMPORTANT]
> **反返工铁律（MVP 范围前置）**：**MVP 裁剪不再作为全量设计完成后的独立决策步**。产品设计沟通（审讯，见 [`grill_orchestration.md`](../grill_orchestration.md)）必须**先于详细规格**提出并裁定：
> 1. *Q1 单一核心假设 (Single Risky Assumption)*：本产品只保留一个功能还能成立，那个功能是什么？
> 2. *Q2 CEO 视角质疑式裁剪 (The Radical Cut · 开发者裁定)*：Agent 对辅助特性（高级筛选/批量导出/站内通知/多角色权限）发起必要性质疑，提出裁剪建议清单与替代方案，**由开发者逐项拍板**（严守 No Admin in MVP）；
> 3. *Q3 团队胃口与时间箱 (Appetite & Circuit Breaker)*：本次 MVP 的胃口周期（1~3天/1~2周），触发断路器坚决砍功能保上线；
> 4. 裁定后：**详细功能规格、Gherkin DoD 与原型只覆盖已确认的 MVP 范围**；非 MVP 功能仅登记 MoSCoW 池，不写详细规格。

#### 阶段 0A'：微观特性探索与双视图设计 (Feature Discovery & Dual Views, 限 MVP 范围)
- **设计指南驱动**：深度遵循 [`product_design.md`](../product_design.md)，显式声明 `Inherits: /DESIGN.md`，先完成**产品探索五步推演**（Status Quo 现状痛点、JTBD 用户雇佣任务、Aha Moment 惊喜时刻、FTUE 首分钟冷启动体验、2～3 种交互形态方案 Trade-offs 比选）；
- **支柱一：特性级交互流与原型 (Interaction & Prototyping)**：承袭全局 Tokens，落实 **UX 认知心理学四定律**（渐进式披露、视觉扫视层级、费茨与希克定律、真实微文案规范）、核心组件六态规范、**双轨多态原型（Mermaid 拓扑 + ASCII 空间比例线框，覆盖 Empty/Loading/Populated/Error 四态，融合 OpenPencil PenNode 矢量层级与 Generative UI 动态部件仿真）**；
- **支柱二：特性功能规格与双视图 (Features & Dual Views)**：
  - **【视图一：面向人】** `{feature}_prd.md`：痛点叙事、方案论证、业务规则矩阵、端到端旅程、Gherkin (`Given/When/Then`) 验收断言；
  - **【视图二：面向 VibeCoding】** `{feature}_vibe_spec.md`：高信息密度 YAML 契约（继承 `/DESIGN.md`、Tokens 代码映射、DOM 骨架、状态机、字段规则、硬护栏），供 AI 编码无噪音直读；
- **商业计划可选；双轨原型必产**：无位图则采用 **Mermaid 拓扑 + ASCII 比例线框**（[`product_prototype.md`](../product_prototype.md)）。

#### 阶段 0B：分阶段实施规划（记录·源自审讯结论）(Phased Roadmap)

- **规划指南驱动**：深度遵循 [`product_roadmap.md`](../product_roadmap.md)；**MVP 范围与 Q1/Q2/Q3 已在阶段 0A 产品设计沟通中裁定，本节不再重复决策**，仅将结论落盘；
- **编制分阶段规划书**：形成各阶段功能映射表（MoSCoW 矩阵）、阶段依赖路线图与准出条件；Q4 Day 1 垂直曳光弹切片（UI+API+DB 贯通）在此定义。严禁在 0B 回头做「全量设计再砍半」。


#### 阶段 0C：MVP 详细功能设计、整体交互逻辑与规模评估 (Detailed Interaction & Scale Assessment · 限 MVP 范围)
> [!IMPORTANT]
> **先交互与功能，后技术选型**：
> 绝对不能在没有明确详细功能与交互逻辑前空泛搞技术选型！必须先有 0C 的详细设计与规模评估，阶段 1 的技术栈匹配与选型论证才有据可依。**0C 只覆盖阶段 0A 已裁定并入 MVP 的功能**，非 MVP 功能不入详细规格。
- **详细功能规格详述**：所有输入项与约束规则（含首屏披露与高级折叠层级）、前置触发条件、业务分支矩阵、边界极端异常处理；
- **整体交互逻辑网络**：页面路由流转拓扑（Mermaid）、组件交互层级（视图/抽屉/弹窗/浮层）、未保存脏数据退出拦截、异步与状态迁移（防抖锁定/乐观渲染/草稿保护与错误自愈）；
- **规模与复杂度客观评估 (Scale Assessment)**：量化评估交互复杂度（轻/中/高）、数据规则规模（简/中/复）、通信实时性要求，明确项目工程量级，为阶段 1 技术选型提供精准约束输入。
