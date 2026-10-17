# 3. 产出文档（一源双视图 + 可交互 HTML 预览 + 决策日志）

**何时读**：处理3. 产出文档（一源双视图 + 可交互 HTML 预览 + 决策日志）时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
### 3. 产出文档（一源双视图 + 可交互 HTML 预览 + 决策日志）
- （可选）`hs_dev_docs/_01_product_vision/_03_business_plan/…`
- `hs_dev_docs/_01_product_vision/_01_design_charter/DESIGN.md`（项目根目录 `DESIGN.md` 归档）
- `hs_dev_docs/_01_product_vision/_02_phased_roadmap/{feature_name}_phased_plan.md`（《产品开发分阶段规划书》，源自阶段 0A 审讯结论：MVP 范围（开发者裁定）、MoSCoW 分级矩阵与路线图、Day 1 垂直切片）
- `hs_dev_docs/_02_feature_spec/_01_human_prd/{feature_name}_prd.md`（【视图一：面向人】产品功能设计书，含痛点 JTBD/FTUE、方案比选、详细规格矩阵、交互逻辑流、Gherkin DoD 与规模评估，**仅覆盖 MVP 范围**）
- `hs_dev_docs/_02_feature_spec/_02_vibe_spec/{feature_name}_vibe_spec.md`（【视图二：面向 VibeCoding】机器执行契约，含 Tokens、组件树 DOM 骨架、状态机、字段约束字典、Gherkin 可测用例与机器硬护栏）
- `hs_dev_docs/_02_feature_spec/_03_prototype_html/{feature_name}_prototype.html`（【视图一高保真：面向开发者可视化核准】单文件可交互 HTML 预览，内联 Tailwind CDN + 多端 1440/768/390px 视口切换 + 四态无死角仿真）
- `hs_dev_docs/_02_feature_spec/_04_prototype_wireframe/{feature_name}_prototype.md`（双轨多态线框与拓扑）
- `hs_dev_docs/_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml`（统一术语词典）
- `hs_dev_docs/_06_dev_process/_03_qa_log/`（**Q&A 决策日志**：审讯/变更请求问答与拍板，跨会话可追溯；模板见 `resources/templates/process/qa_log.md`）
- **《冻结确认单》**（`resources/templates/process/freeze_signoff.md`）：业务语义签收（A 部分）+ 视觉签收（B 部分）+ 冻结结论
- 更新 `_01_product_vision/_00_product_vision.idx` 与 `_02_feature_spec/_00_feature_spec.idx`

### 4. 阶段 0 冻结门禁（进入阶段 1 的硬前提）

下列条件**全部**满足（且通过 `product_design.md` §5.1 的 **10 维产品与体验自审标尺**）方可进入阶段 1；任一项不满足则停在阶段 0（询问或补齐），开发者确认后更新文档再检：

| 条件 | 含义 |
|---|---|
| **一源双视图齐套** | 存在面向人类的 `{feature}_prd.md`（+原型）与面向机器的 `{feature}_vibe_spec.md`，两者由同一设计数据提纯，无语义冲突； |
| **产品探索与方案比选完备** | 明确定义了 Status Quo（现状痛点）、JTBD、Aha Moment、FTUE 冷启动引导及 ≥2 种核心交互形态的 Trade-offs 比选； |
| **设计语言与 UX 定律完备** | 有 UI 时：具象调性定位清晰、Design Tokens 完整、落实 UX 认知四定律（渐进式披露/视觉层级/费茨希克/真实微文案）、核心组件六态定义完备； |
| **功能与双轨交互完备** | 功能架构树、端到端旅程（含 FTUE）、详细规格矩阵清晰；双轨原型覆盖页面四态（空/加载/正常/错误）；产品 DoD 采用 **Gherkin (`Given/When/Then`)** 从用户交互视角清晰可测； |
| **MVP 范围已裁定（产品设计沟通时）** | Q1 核心假设 / Q2 CEO 质疑式裁剪 / Q3 胃口时间箱已在阶段 0A 审讯中由开发者裁定；**详细规格与原型仅覆盖 MVP 范围**；非 MVP 仅入 MoSCoW 池； |
| **分阶段规划与规模评估就绪** | `_02_phased_roadmap/` 存在《产品开发分阶段规划书》（源自审讯结论），MVP 与演进阶段边界明确，完成客观规模评估； |
| **业务语义签收** | 权限/计费/归属/规则/流程 + Gherkin DoD 由开发者**逐条**确认（《冻结确认单》A 部分）；**触达 DB 时持久化业务规则已确认，物理 DB 设计在阶段 3 经开发者决策**； |
| **纯净无技术侵入** | 严格杜绝在阶段 0 文档中提前塞入底层技术选型、物理表 DDL、RPC 接口签名、Saga 补偿、代码单测覆盖率等研发实现细节； |
| **多端原型与 HTML 齐套** | 有 UI：存在字符拓扑标注与可交互 HTML 原型（多端仿真 + 四态直读）；无 UI：PRD 已声明豁免； |
| **开发者可视化确认签收** | 有 UI：开发者基于 HTML 原型与规约完成 6 大检查点审阅并签署《开发者可视化确认签收单》(APPROVED)，无技术实现阻断缺陷； |
| **冻结确认单 APPROVED** | 《冻结确认单》（业务语义签收 A + 视觉签收 B + 冻结结论）由开发者签署 APPROVED；Q&A 决策日志（`_03_qa_log/`）已记录关键问答与拍板。 |


通过后**立即**进入阶段 1。

> [!IMPORTANT]
> **研发范围收敛铁律**：后续阶段 1（选型）至阶段 6（交付）**严格收敛于当前阶段（Phase 1 MVP）所定义的功能边界与规模评估**，坚决不为远期特性超前开发。


---
