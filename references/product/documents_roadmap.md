# 3. 产出文档结构与“单一真实源 · 双重视图”落地约定

**何时读**：处理3. 产出文档结构与“单一真实源 · 双重视图”落地约定时；先沿用[入口公共约束](../product_design.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 3. 产出文档结构与“单一真实源 · 双重视图”落地约定

```text
hs_dev_docs/
├── _01_product_vision/
│   ├── _00_product_vision.idx                 # 愿景与路线图索引
│   ├── _01_design_charter/                    # 【第一层：宏观品味宪章】DESIGN.md 归档与物理隐喻
│   ├── _02_phased_roadmap/                    # 【演进规划】MVP 范围（审讯裁定）、MoSCoW 分级矩阵与路线图
│   └── _03_business_plan/                     # 【业务意图】商业模式、用户客群主职、战略反目标 (可选)
├── _02_feature_spec/
│   ├── _00_feature_spec.idx                   # 特性规格索引
│   ├── _01_human_prd/                         # 【第二层：微观施工图】面向人（JTBD/方案比选/规格矩阵/规模评估，仅覆盖 MVP）
│   ├── _02_vibe_spec/                         # 【第二层：机器契约】面向 VibeCoding（Tokens代码映射/组件树DOM骨架/状态机）
│   ├── _03_prototype_html/                    # 【第二层：单文件可交互原型】多端四态 HTML 预览
│   └── _04_prototype_wireframe/               # 【第二层：线框拓扑】Mermaid 拓扑 + ASCII 空间比例四态线框
└── _06_dev_process/_03_qa_log/                # 【决策日志】审讯/变更请求问答与拍板（跨会话可追溯）
```

同时，在项目根目录维护 **`DESIGN.md`**，作为全局宏观品味与 Design Tokens 的单一真实源；冻结时签署《冻结确认单》（业务语义签收 A + 视觉签收 B + 冻结结论，模板见 `resources/templates/process/freeze_signoff.md`）。

### 3.1 大型 PRD 分级拆分与微观索引标准 (Hierarchical PRD Splitting)
当系统规模扩张、包含多模块或 >3 个功能特性时，**严禁将全部功能堆砌在单一巨型 PRD 中**（容易导致 Token 溢出与注意力分散）。必须执行两级拆分：
1. **L1 全景总览 (`overview_prd.md`)**：
   - 载体：`_02_feature_spec/_01_human_prd/overview_prd.md`（参照 [`overview_prd_template.md`](../../resources/templates/product_design/overview_prd_template.md)）；
   - 职责：维护全局模块矩阵、特性索引导航表（含 `FEAT-ID`、特性名称、所属模块、优先级、PRD 相对路径）及 Mermaid 功能全景树。
2. **L2 微观子特性施工图 (`{feature_key}_prd.md`)**：
   - 载体：`_02_feature_spec/_01_human_prd/{feature_key}_prd.md`（参照 [`sub_feature_prd_template.md`](../../resources/templates/product_design/sub_feature_prd_template.md)）；
   - 职责：单文档严格控制在 100~250 行，专精当前 `FEAT-ID` 的微观 JTBD、方案比选、字段约束矩阵与 Gherkin 验收标准；
   - 自动化建库：由 `python scripts/doc_index_db.py rebuild` 自动化解析入库 `features` 表与 `features_fts`，支持 `feature-search` 毫秒级定向按需召回。
3. **L2 页面与空间布局原型 (`_04_prototype_wireframe/{feature_key}_prototype.md`)**：
   - 自动化建库：由 `doc_index_db.py` 自动化解析页面 ID、路由、布局形态与原型 HTML 入库 `pages` 表与 `pages_fts`，支持 `page-search` 检索页面拓扑。

---

## 4. MVP 范围裁定前置与分阶段实施

**绝对禁止一次性全量研发 (Big Bang)**；也**禁止先写完全量设计再做 MVP 裁剪**（全量规格白做 = 结构性返工）。
MVP 范围裁定**前置到产品设计沟通（审讯）阶段**（详见 [`grill_orchestration.md`](../grill_orchestration.md) / [`product_roadmap.md`](../product_roadmap.md)）：
1. **设计沟通即裁定**：在产品设计沟通时由 Agent 提出 **Q1 核心假设、Q2 CEO 质疑式裁剪建议清单、Q3 团队胃口时间箱**，**开发者逐项拍板**后才展开详细规格；
2. **详细规格只覆盖 MVP**：本文 §2 的微观特性施工图、双轨原型与 Gherkin DoD **仅对已裁定并入 MVP 的功能**输出；非 MVP 功能仅登记 MoSCoW 池，不写详细设计；
3. **落盘规划书**：输出《产品开发分阶段规划书》(`{feature_name}_phased_plan.md`)，源自审讯结论；
4. **锁定研发范围**：后续阶段 1（选型）至阶段 6（交付）**严格收敛于当前阶段（Phase 1 MVP）**，坚决不超前开发。

---
