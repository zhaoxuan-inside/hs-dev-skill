# 产品设计规范指南（宏观品味宪章 · 微观特性施工图 · 执行契约）

**项目适用性**：视觉、DESIGN.md、原型与 UI vibe_spec 仅在有 UI 时必需；项目 DESIGN.md 的实际 Tokens 为唯一视觉基线，下文数值为按场景选择的示例；无 UI 按 `project_types.md` 与 `product_design.md` §5.2 标记 NA，保留 PRD、API/CLI/库契约、可执行场景和业务冻结确认。

**验收规则**：设计工作按本文展开；每个实际验收点执行 [`product_acceptance.md`](product_acceptance.md) 的 DISC/PROD 清单，使用 [`stage_acceptance.md`](stage_acceptance.md) 的证据与权限规则。10 维自审和文档齐套只能支持提交，不能替代场景演练与开发者验收。

**何时读**：阶段 0 / `work_mode=DESIGN` / 需求规划 / UI 与功能设计；每会话最多一次。  
**核心分工**：
- **产品设计核心指南（本文）**：融合业界标杆（Google Labs `DESIGN.md`、YC `gstack` 品味评审、`pm-skills` 四层漏斗、`superpowers` 方案权衡），确立「**宏观品味宪章（项目级）与微观特性施工图（特性级一源双视图）两层解耦**」之铁律；
- **项目根设计系统宪章** → [`design_md.md`](design_md.md) + 根目录 `DESIGN.md`；
- **产品原型与双轨线框（Mermaid + ASCII）** → [`product_prototype.md`](product_prototype.md)；
- **MVP 范围裁定（并入产品设计沟通）与分阶段规划** → [`product_roadmap.md`](product_roadmap.md)；
- **设计对齐编排 (Grill)** → [`grill_orchestration.md`](grill_orchestration.md)；
- **前端默认审美与手艺** → [`frontend_aesthetic.md`](frontend_aesthetic.md) / [`frontend_craft.md`](frontend_craft.md)；
- **远程产品与 UX 规则按需拉取** → [`rule_library.md`](rule_library.md)（`gstack.office-hours` / `gstack.plan-design-review` / `deanpeters.pm-prd` / `uipro.ux-design`）。

---

<!-- HS_SECTION_INDEX -->

**按业务装载**：正文已拆成独立文件。先沿用本页公共约束，只打开当前业务/阶段需要的分册；不要顺序读全套。分册独立进行变化检查；迁移后旧的行号/摘要须重新定位，已有签收不得自动迁移。

## 0. 两层解耦体系与产出边界铁律

正文见 [product/boundaries_discovery.md](product/boundaries_discovery.md)。

### 0.1 核心解耦架构：宏观品味宪章 vs 微观特性施工图

正文见 [product/boundaries_discovery.md](product/boundaries_discovery.md)。

### 0.2 产出边界铁律（绝对纯净原则）

正文见 [product/boundaries_discovery.md](product/boundaries_discovery.md)。

### 0.3 拒绝“填表式设计”：微观特性探索五步推演 (Feature Discovery)

正文见 [product/boundaries_discovery.md](product/boundaries_discovery.md)。

## 1. 第一层：宏观品味与全局设计系统宪章 (Project Taste Charter)

正文见 [product/design_language.md](product/design_language.md)。

### 1.1 设计哲学与视觉调性 (Philosophy & Mood)

正文见 [product/design_language.md](product/design_language.md)。

### 1.2 全局 Design Tokens 规范基准

正文见 [product/design_language.md](product/design_language.md)。

### 1.3 宏观品味底线与硬护栏 (Anti-Slop Taste Bar & Do's/Don'ts)

正文见 [product/design_language.md](product/design_language.md)。

## 2. 第二层：微观特性施工图与执行契约 (Feature Construction & Contract)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.1 UX 认知心理学与可用性四定律落地 (UX Usability Laws)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.2 核心组件规范与全状态覆盖 (Component Specs & States)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.3 核心方案比选与功能架构全景 (Trade-offs & Feature Architecture)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.4 端到端用户核心旅程 (Core User Journeys)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.5 界面信息架构与双轨多态原型 (Dual-Track Multi-Platform Prototypes)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.6 详细功能规格矩阵 (Detailed Feature Specifications)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.7 整体交互逻辑网络与防丢失机制

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.8 Gherkin 行为驱动产品验收标准 (Functional DoD)

正文见 [product/feature_specification.md](product/feature_specification.md)。

### 2.9 工程规模与复杂度客观评估 (Scale Assessment)

正文见 [product/feature_specification.md](product/feature_specification.md)。

## 3. 产出文档结构与“单一真实源 · 双重视图”落地约定

正文见 [product/documents_roadmap.md](product/documents_roadmap.md)。

### 3.1 大型 PRD 分级拆分与微观索引标准 (Hierarchical PRD Splitting)

正文见 [product/documents_roadmap.md](product/documents_roadmap.md)。

## 4. MVP 范围裁定前置与分阶段实施

正文见 [product/documents_roadmap.md](product/documents_roadmap.md)。

## 5. 阶段 0 产品评审与冻结门禁 (Product Review & Freeze Gate)

正文见 [product/review_freeze.md](product/review_freeze.md)。

### 5.1 产品与体验 10 维自审标尺（借鉴 `gstack /plan-design-review`）

正文见 [product/review_freeze.md](product/review_freeze.md)。

### 5.2 阶段 0 冻结门禁表

正文见 [product/review_freeze.md](product/review_freeze.md)。
