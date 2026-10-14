# 文档驱动开发（DDD）全生命周期驱动引擎指南

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
- 合法停点：询问闸门、（M/L）冻结未过、外部依赖 `BLOCKED`。确认后立即继续。

### 阶段依赖与跃迁总则

- **L**：`0 → 1 → 2 → 3 → 4 → 5 → 6`；0→1 须产品冻结门禁。
- **M/S**：按 `right_sizing.md`；禁止为空跑阶段制造空 ADR/空四要素。
- 其余跃迁：路径要求的产出齐套且无未关闭询问项即可；不要求每阶段全文请确认。
- 暴露产品语义未决：回退阶段 0（或升为 M/L）闭合后再前进。

---

## 阶段 0：产品设计与分阶段规划冻结 (Product Design & Phased Roadmap)

### 1. 核心目标
全面强化专业产品设计能力，并通过**两层解耦架构（宏观品味宪章 + 微观特性规格）**与**MVP 裁剪与分阶段实施规划**，杜绝一次性全量研发 (Big Bang)，产出可冻结的专业级产品设计方案与分阶段规划书，作为后续研发路径的权威真理源。

**两层解耦与产出边界铁律**：
1. **宏观层：项目级设计系统宪章 (Macro Product Taste & Design System Charter)**：
   - 固化于**项目根目录 `DESIGN.md`**（并在 `_01_product_vision/` 存档）；
   - 定义全项目的真实物理隐喻（对标具象产品）、调色盘与 Tokens、Anti-Slop 审美红线与 10 星惊喜标准。
   - 具有全局跨特性约束力，单次定义、长期驻留，防止多功能各自发明设计规范造成风格撕裂。
2. **微观层：特性级功能规格与交互原型 (Micro Feature Construction Specs)**：
   - 存放于 `_02_product_design/{feature}_prd.md`、`{feature}_vibe_spec.md` 及原型中；
   - 顶部必须显式声明 `Inherits: /DESIGN.md`，禁止私自重定义全局美学与色盘，专注模块业务流、认知层级与组件局部多态。

> [!IMPORTANT]
> **严禁底层技术细节反向侵入产品设计**：
> 严禁在阶段 0 的 PRD、原型或规划文档中提前塞入底层技术选型（如 MySQL vs PG）、物理数据库 DDL、接口代码实现签名、分布式 Saga 补偿、代码单元测试覆盖率指标等工程实现细节！这些是阶段 1（选型）至阶段 3（四要素详设）的职责。产品设计阶段只对产品的设计语言与功能规格负责。

### 2. 阶段执行三步法 (0.1 宏观品味宪章 → 0A 微观特性设计 → 0B MVP 分阶段规划)

#### 阶段 0.1：确立项目级宏观品味宪章 (Project Design Charter, 仅项目启动或全局重构时)
- 在项目根目录创建并固化 `DESIGN.md`（详见 [`design_md.md`](design_md.md) 与 [`product_design.md`](product_design.md) §0.1）；
- 确立具象物理隐喻（如 Linear/Stripe/Raycast，严禁假大空词汇）、基准 Design Tokens、Anti-Slop 审美禁令（禁止紫色渐变/无意义动画/居中文案等 AI 滥觞）、10 星惊喜门槛；
- 作为后续所有特性功能 PRD、原型与 VibeSpec 的唯一继承根。

#### 阶段 0A：微观特性探索与双视图设计 (Feature Discovery & Dual Views)
- **设计指南驱动**：深度遵循 [`product_design.md`](product_design.md)，显式声明 `Inherits: /DESIGN.md`，先完成**产品探索五步推演**（Status Quo 现状痛点、JTBD 用户雇佣任务、Aha Moment 惊喜时刻、FTUE 首分钟冷启动体验、2～3 种交互形态方案 Trade-offs 比选）；
- **支柱一：特性级交互流与原型 (Interaction & Prototyping)**：承袭全局 Tokens，落实 **UX 认知心理学四定律**（渐进式披露、视觉扫视层级、费茨与希克定律、真实微文案规范）、核心组件六态规范、**双轨多态原型（Mermaid 拓扑 + ASCII 空间比例线框，覆盖 Empty/Loading/Populated/Error 四态，融合 OpenPencil PenNode 矢量层级与 Generative UI 动态部件仿真）**；
- **支柱二：特性功能规格与双视图 (Features & Dual Views)**：
  - **【视图一：面向人】** `{feature}_prd.md`：痛点叙事、方案论证、业务规则矩阵、端到端旅程、Gherkin (`Given/When/Then`) 验收断言；
  - **【视图二：面向 VibeCoding】** `{feature}_vibe_spec.md`：高信息密度 YAML 契约（继承 `/DESIGN.md`、Tokens 代码映射、DOM 骨架、状态机、字段规则、硬护栏），供 AI 编码无噪音直读；
- **商业计划可选；双轨原型必产**：无位图则采用 **Mermaid 拓扑 + ASCII 比例线框**（[`product_prototype.md`](product_prototype.md)）。

#### 阶段 0B：MVP 决策与分阶段实施规划 (Phased Roadmap & MVP Decision)

- **规划指南驱动**：深度遵循 [`product_roadmap.md`](product_roadmap.md)，严禁直接对全量功能进行大包大揽式开发；
- **强制人机交互对齐机制 (Human-in-the-Loop Alignment & CEO Cut)**：Agent 主动发起针对性问询，向人类决策者提问并确认：
  1. *Q1 单一核心假设 (Single Risky Assumption)*：MVP 最关键要验证的核心闭环与痛点是什么？
  2. *Q2 CEO 视角激进砍半提案 (The Radical Cut)*：Agent 主动提案砍掉 50% 次级特性（高级筛选/批量导出/站内通知/权限管理），严格落实 **No Admin in MVP**；
  3. *Q3 团队胃口与时间箱 (Appetite & Circuit Breaker)*：本次 MVP 设定的胃口周期（1~3天/1~2周），触发断路器坚决砍功能保上线；
  4. *Q4 Day 1 垂直曳光弹切片与验收 (Tracer Bullet & DoD)*：端到端纵向贯通 UI+API+DB 的首日冒烟切片与 Gherkin 验收断言；
- **编制分阶段规划书**：形成各阶段功能映射表、阶段依赖路线图与准出条件。


#### 阶段 0C：MVP 详细功能设计、整体交互逻辑与规模评估 (Detailed Interaction & Scale Assessment)
> [!IMPORTANT]
> **先交互与功能，后技术选型**：
> 绝对不能在没有明确详细功能与交互逻辑前空泛搞技术选型！必须先有 0C 的详细设计与规模评估，阶段 1 的技术栈匹配与选型论证才有据可依。
- **详细功能规格详述**：所有输入项与约束规则（含首屏披露与高级折叠层级）、前置触发条件、业务分支矩阵、边界极端异常处理；
- **整体交互逻辑网络**：页面路由流转拓扑（Mermaid）、组件交互层级（视图/抽屉/弹窗/浮层）、未保存脏数据退出拦截、异步与状态迁移（防抖锁定/乐观渲染/草稿保护与错误自愈）；
- **规模与复杂度客观评估 (Scale Assessment)**：量化评估交互复杂度（轻/中/高）、数据规则规模（简/中/复）、通信实时性要求，明确项目工程量级，为阶段 1 技术选型提供精准约束输入。

### 3. 产出文档（一源双视图 + 可交互 HTML 预览）
- （可选）`hs_dev_docs/_01_product_vision/_03_business_plan/…`
- `hs_dev_docs/_01_product_vision/_01_design_charter/DESIGN.md`（项目根目录 `DESIGN.md` 归档）
- `hs_dev_docs/_01_product_vision/_02_phased_roadmap/{feature_name}_phased_plan.md`（《产品开发分阶段规划书》，包含 MVP 范围、人机交互对齐记录、MoSCoW 分级矩阵与路线图）
- `hs_dev_docs/_02_feature_spec/_01_human_prd/{feature_name}_prd.md`（【视图一：面向人】产品功能设计书，含痛点 JTBD/FTUE、方案比选、详细规格矩阵、交互逻辑流、Gherkin DoD 与规模评估）
- `hs_dev_docs/_02_feature_spec/_02_vibe_spec/{feature_name}_vibe_spec.md`（【视图二：面向 VibeCoding】机器执行契约，含 Tokens、组件树 DOM 骨架、状态机、字段约束字典、Gherkin 可测用例与机器硬护栏）
- `hs_dev_docs/_02_feature_spec/_03_prototype_html/{feature_name}_prototype.html`（【视图一高保真：面向开发者可视化核准】单文件可交互 HTML 预览，内联 Tailwind CDN + 多端 1440/768/390px 视口切换 + 四态无死角仿真）
- `hs_dev_docs/_02_feature_spec/_04_prototype_wireframe/{feature_name}_prototype.md`（双轨多态线框与拓扑）
- `hs_dev_docs/_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml`（统一术语词典）
- 更新 `_01_product_vision/_00_product_vision.idx` 与 `_02_feature_spec/_00_feature_spec.idx`

### 4. 阶段 0 冻结门禁（进入阶段 1 的硬前提）

下列条件**全部**满足（且通过 `product_design.md` §5.1 的 **10 维产品与体验自审标尺**）方可进入阶段 1；任一项不满足则停在阶段 0（询问或补齐），开发者确认后更新文档再检：

| 条件 | 含义 |
|---|---|
| **一源双视图齐套** | 存在面向人类的 `{feature}_prd.md`（+原型）与面向机器的 `{feature}_vibe_spec.md`，两者由同一设计数据提纯，无语义冲突； |
| **产品探索与方案比选完备** | 明确定义了 Status Quo（现状痛点）、JTBD、Aha Moment、FTUE 冷启动引导及 ≥2 种核心交互形态的 Trade-offs 比选； |
| **设计语言与 UX 定律完备** | 有 UI 时：具象调性定位清晰、Design Tokens 完整、落实 UX 认知四定律（渐进式披露/视觉层级/费茨希克/真实微文案）、核心组件六态定义完备； |
| **功能与双轨交互完备** | 功能架构树、端到端旅程（含 FTUE）、详细规格矩阵清晰；双轨原型覆盖页面四态（空/加载/正常/错误）；产品 DoD 采用 **Gherkin (`Given/When/Then`)** 从用户交互视角清晰可测； |
| **分阶段规划与规模评估就绪** | 完成人机交互对齐，`_02_phased_roadmap/` 存在《产品开发分阶段规划书》，MVP 与演进阶段边界明确，完成客观规模评估； |
| **纯净无技术侵入** | 严格杜绝在阶段 0 文档中提前塞入底层技术选型、物理表 DDL、RPC 接口签名、Saga 补偿、代码单测覆盖率等研发实现细节； |
| **多端原型与 HTML 齐套** | 有 UI：存在字符拓扑标注与可交互 HTML 原型（多端仿真 + 四态直读）；无 UI：PRD 已声明豁免； |
| **开发者可视化确认签收** | 有 UI：开发者基于 HTML 原型与规约完成 6 大检查点审阅并签署《开发者可视化确认签收单》(APPROVED)，无技术实现阻断缺陷； |


通过后**立即**进入阶段 1。  

> [!IMPORTANT]
> **研发范围收敛铁律**：后续阶段 1（选型）至阶段 6（交付）**严格收敛于当前阶段（Phase 1 MVP）所定义的功能边界与规模评估**，坚决不为远期特性超前开发。


---

## 阶段 1：技术选型与论证 (Tech Selection & ADR)

### 1. 核心目标
在**已冻结的 MVP 详细功能、整体交互逻辑与规模评估约束**下，针对多端（后端/前端/移动端/桌面端）、语言、存储引擎、中间件、网络协议进行多方案对比分析，输出明确的架构决策记录（ADR）。
**单文件内联分层铁律 (Top-Contract Slice)**：
选型文档与 ADR 必须强制在**文档顶部 1～35 行置顶 `## [VIBE_CONTRACT] 机器执行契约`**（记录锁定的唯一技术栈、明确版本号、硬性禁令）；下半部保留 `## [HUMAN_RATIONALE]` 供人类评审方案权衡。**严禁让 VibeCoding 工具读取落选方案的讨论，防止 AI 产生误导性技术混淆！**

### 2. Agent 行为准则
- **前置**：阶段 0 产品需求冻结门禁已通过；未通过则禁止本阶段任何落盘与选型结论。
- 选型前读 `~/.hs-dev-skill/preferences.yaml`；新技术写 `~/.hs-dev-skill/tech_learning/` 笔记；模糊路线先 GitHub 高星对标（≥2 候选）；
- 梳理至少 2 种备选方案（例如：MySQL vs PostgreSQL，gRPC vs RESTful，Redis vs 本地缓存）；
- 从性能、开发成本、可维护性、团队技术栈契合度等维度打分评估（含置信度）；
- 推荐首选方案并阐述理由；**与现有栈一致或大家通用的最优解直接选定并在顶部写入 `[VIBE_CONTRACT]` 与对应 ADR**；
- 选型结论必须可追溯到已冻结 PRD 的约束与 DoD；
- 涉及垂直领域 SDK 或外部平台依赖（如大模型 API/Live 流式、Android 原生、浏览器扩展 MV3）时，必须评估防腐层（Adapter）与版本适配方案，禁止外部不可控依赖直连业务核心；
- 仅当影响面广、项目特有、资料与全局偏好未提及且顶部分数接近时，结构化询问开发者；答复后更新全局偏好账本；
- 若选型暴露产品语义未决：**回退阶段 0**，闭合后再继续。

### 3. 产出文档
- `hs_dev_docs/_03_architecture_design/_01_system_architecture/_{platform}_tech_select.md`（含顶部 `[VIBE_CONTRACT]` 契约块）
- `hs_dev_docs/_00_project_foundation/_03_decision_record/ADR_{xxx}.md`（含顶部 `[VIBE_CONTRACT]` 契约块）
- 必要时：`~/.hs-dev-skill/tech_learning/{tech}_notes.md`、更新 `~/.hs-dev-skill/preferences.yaml`
- 更新对应 `.idx`

### 4. 阶段门禁
选型文档与 ADR 齐套且具备顶部 `[VIBE_CONTRACT]` 契约；涉及新技术时全局学习笔记就绪；无未关闭的询问闸门事项；且仍建立在已冻结 PRD 之上（PRD 未回退破坏冻结）。

---

## 阶段 2：范式落地与架构设计 (Paradigm & Architecture)

### 1. 核心目标
按规模/类型选定开发范式（后端 B 阶 / 前端 F 阶），再落模块边界与术语；**仅当范式含 DDD** 才做战略/战术领域模型。文档顶部同样强制包含 **`## [VIBE_CONTRACT] 架构执行契约`**（锁定范式阶、模块路径映射与依赖方向硬规则）。主详规：**[dev_paradigm.md](dev_paradigm.md)**；子集：**[ddd_design.md](ddd_design.md)** / **[backend_arch.md](backend_arch.md)** / **[frontend_arch.md](frontend_arch.md)**。

### 2. Agent 行为准则
- L2 优先读 `dev_paradigm.md`（本会话未读时）；按选定阶再读 `backend_arch` / `frontend_arch` /（若 B4+）`ddd_design`（各每会话最多一次）；
- 非 DDD：模块图 + 依赖方向 + 词典即可；禁止硬套聚合/BC 仪式；
- DDD 档：BC 图 + 上下文映射 + 聚合/VO/事件；前端 feature 与边界对齐（或显式 BFF）；
- 依赖只向内；外部经 Adapter；模板见 `resources/templates/architecture_design/arch_design_template.md`（含 `[VIBE_CONTRACT]` 契约块）；
- 常规分层高置信自主推进；范式升级/BC 切割若触询问闸门四条件则询问；
- 仍不够 → `rule_fetch`：按范式选 `ciembor.*` / `wshobson.*` / `fsd.skill` 等。

### 3. 产出文档
- `hs_dev_docs/_03_architecture_design/_01_system_architecture/_{platform}_architecture_design.md`（含顶部 `[VIBE_CONTRACT]` 契约块 + 范式阶 + 模块/BC 与前端对齐表）
- `hs_dev_docs/_03_architecture_design/_02_pattern_clusters/`（GoF 23 种设计模式协同集群档案）
- `hs_dev_docs/_03_architecture_design/_03_adapter_spec/`（防腐层规约）
- 更新对应 `.idx`

### 4. 阶段门禁
架构文档齐套且顶部 `[VIBE_CONTRACT]` 契约块完备；范式阶与「不升级」理由已写；模块（或 BC）边界清晰；词典完备；前端模块对齐表已填（若有 UI）；触发的询问项已关闭。

---

## 阶段 3：详细规格设计四要素 (Detailed Spec Design)

### 1. 核心目标
L：四维契约齐套后再编码。M：只更新触达维。S：跳过。范式见 `dev_paradigm.md`；DDD 档见 `ddd_design.md`；后端见 `backend_arch.md`；前端结构见 `frontend_arch.md`；接口见 `api_engineering.md`；UI 手艺/视觉见 `frontend_craft.md` / `design_md.md`（**强制遵循 Modern Web Guidance 最新标准**：原生 Dialog/Popover、Container Queries、CSS `:has()`、Fetch Priority 与流式传输规范）。
**人机同构原则**：阶段 3 产出的 SQL DDL、接口 Schema、六元组签名和调用链时序图本身即为高度精确的工程语言，**保持单文件天然人机同构，绝不额外拆分**。

### 2. 四维产出物
1. **数据库设计与迁移 (DB Schema)**：
   - 表结构设计：`_04_engineering_contract/_01_db_schema/_01_{model}/_01_{table}_design.md`（强制字段：`id`, `created_at`, `updated_at`, `description`, `is_del`, `version`，**严禁使用 SQL 关键字 `desc`**）；
   - 前向脚本：`migrations/V1.0.0__init_{table}.sql`；
   - 回滚脚本：`migrations/U1.0.0__init_{table}.sql`（V/U 强制原子配对）。
2. **接口契约设计 (Interface Design)**：
   - 接口文档：`_04_engineering_contract/_02_interface_design/_01_{model}/_01_{api}_design.md`（错误码、分页、幂等）；
   - Mock 契约：`_04_engineering_contract/_03_mock_contract/{contract_name}.json` 与 `mock/_06_test_profile/`。
3. **六元组与前端方法设计契约画像 (Method Archetypes & Contract Design)**：
   - 后端方法设计：`_04_engineering_contract/_04_method_design/_01_{model}/_01_{method}_design.md`（六元组主方法、`_compensate`、`_fallback`、`_metrics`、`_recall`，模板见 `method_design.md`）；
   - 前端方法设计：`_04_engineering_contract/_04_method_design/_02_{feature}/_01_{method}_design.md`（纯计算 ALGO、转换 TRANSFORM、策略 GUARD、状态 STATE、Hook 编排 ORCHESTRATE、适配 ADAPTER，模板见 `frontend_method_design.md`）；
   - 登记标准：**代码物理定位（实现后自动回填）、7 大方法类型、敏感度及理由、副作用及具体表现、0 DOM 依赖/精准跑测命令、以本方法为中心的局部依赖图与三段式历史修改记录**（遵循 [`method_archetypes.md`](method_archetypes.md) 规范）。
4. **调用链拓扑分析 (Call Chain)**：
   - `_04_engineering_contract/_05_call_chain/_01_{source}/_01_{source}_call_chain.md`。

### 3. 阶段门禁
路径要求的设计与 V/U（若触达 DB）及 `.idx` 齐套。骨架不询问；契约语义/业务字段/不可逆补偿若触询问闸门须先关闭。

---

## 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

### 1. 核心目标
将经过评审的详细设计拆解为独立、原子、可验证的工程任务项，通过渐进式四级路由 / SQLite 检索，将各阶段的**机器执行契约切片**物化装配进 `_05_task_orchestration/_03_task_context_pack/{task_id}_context_pack.md`，充当面向 VibeCoding 的极速装载包。

### 2. Context Pack 机器装配法则 (VibeCoding Assembly Rules)
1. **产品与 UI 契约**：优先装入阶段 0 的 **`{feature}_vibe_spec.md` 机器契约切片**（Design Tokens、组件树 DOM 骨架、状态机、Gherkin DoD），严禁整篇灌入人类版故事与讨论；
2. **选型与架构契约**：仅装入阶段 1/2 文档顶部的 **`[VIBE_CONTRACT]` 置顶切片**（仅占前几十行），跳过下半部废案讨论；
3. **实现四要素契约**：装入阶段 3 相关的局部表结构 SQL、API 契约或六元组方法签名切片；
4. 改代码/设计文件前：`python scripts/process_log.py checkpoint --id {task_id} --step … --summary "…" --paths …`（见 [`process_continuity.md`](process_continuity.md)）。

---

## 阶段 5：开发三同步实现 (Implementation & Three-Sync)

### 1. 核心目标
**质量优先**：以 [`testing.md`](testing.md) 垂直切片 TDD + 六元组规范驱动编码，保证业务代码、设计文档、迁移脚本、测试用例的绝对一致性。分步红绿通过，最大可能保证最终正确。

### 2. 执行原则
1. **确认 seam**：落盘测面后再红灯（见 testing §2）；接口即测试面（见 [`deep_modules.md`](deep_modules.md)）。
2. **Mock 先行与契约隔离**：在 `mock/_06_test_profile/` 配置测试集 Profile，业务代码零 Mock 污染。
3. **六元组业务逻辑**：在 `backend/` 或对应端实现 `method`、`method_compensate`、`method_fallback`。
4. **垂直切片 + 全覆盖**：一次一个行为红→绿→重构；`test/_01_method_test/` 核心域分支覆盖率 ≥ 85%，降级与补偿分支 100% 覆盖。
5. **实现期分叉**：新暴露的选择点同样适用置信度决策；产品空白回切 DESIGN（审讯式）；触发询问则 `status --set BLOCKED`，禁止静默猜测业务特有规则。

---

## 阶段 6：全层级门禁自检与交付归档 (Quality Gate & Closure)

### 1. 核心目标
执行严格的提交前质量门禁自检，保障零死代码、零破坏性迁移、零索引漂移。

### 2. 自检动作
1. **运行全量测试与运行态走查（测试零报错绝对阻断门禁）**：`make test` 确保 **100% PASS**，**无任何失败、报错或异常用例**；若有任何报错，**绝对禁止将任务置为 COMPLETED，绝对禁止 Git Commit，绝对禁止向用户汇报交付或完工**！严禁出现“代码已交付但有测试报错稍后修”的严重违规，必须就地 Debug 修复直至全绿。前端工程结合 Chrome DevTools CDP 自动化排查，确保无未捕获 Console 报错与网络死锁，满足 WCAG a11y 对比度与 LCP/内存泄漏安全线。
2. **运行代码静态检测（零告警零错误门禁）**：语言对应 Linter（ESLint/Ruff/Flake8 等）与类型检查（TSC/Mypy）**必须达到 0 警告（0 Warning）且 0 错误（0 Error）**；任何 Warning 均视为阻断性质量缺陷必须就地消除，严禁带 Warning 提交代码。
3. **运行一致性门禁检查**：`python3 scripts/verify_consistency.py --root .` 确保三文件、索引、V/U 脚本原子配对与目录卫生 100% 合规。
4. **运行死代码与孤儿方法扫描**：`python3 scripts/dead_code_scanner.py --root .`。
5. **流转任务状态并归档**：**仅当上述测试全绿、静态检测零告警零错误、一致性验证全部通过后**，方可执行 `python3 scripts/task_manager.py status --id {task_id} --set COMPLETED`（自动归档至 `_00_task_archive.idx`）。
6. **Git 规范提交**：按照 `<type>(<scope>): <subject>` 规范生成本地 Commit。**默认不** `git push`；**仅当用户明确要求推送**时代为执行并回报结果。

