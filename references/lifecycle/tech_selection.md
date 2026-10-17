# 阶段 1：技术选型与论证 (Tech Selection & ADR)

**何时读**：处理阶段 1：技术选型与论证 (Tech Selection & ADR)时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 阶段 1：技术选型与论证 (Tech Selection & ADR)

### 1. 核心目标
在**已冻结的 MVP 详细功能、整体交互逻辑与规模评估约束**下，针对多端（后端/前端/移动端/桌面端）、语言、存储引擎、中间件、网络协议进行多方案对比分析，输出明确的架构决策记录（ADR）。
**单文件内联分层铁律 (Top-Contract Slice)**：
选型文档与 ADR 必须强制在**文档顶部置顶 `## [VIBE_CONTRACT] 机器执行契约`**（记录锁定的唯一技术栈、明确版本号、硬性禁令）；下半部保留 `## [HUMAN_RATIONALE]` 供人类评审方案权衡。**严禁让 VibeCoding 工具读取落选方案的讨论，防止 AI 产生误导性技术混淆！**

### 2. Agent 行为准则
- **前置**：阶段 0 产品需求冻结门禁已通过；未通过则禁止锁定本阶段选型结论。阶段 0 为关闭关键能力未知项所做的有边界探查允许独立记录，不等同提前选型。
- 选型前读 `~/.hs-dev-skill/preferences.yaml`；新技术写 `~/.hs-dev-skill/tech_learning/` 笔记；模糊路线先 GitHub 高星对标（≥2 候选）；
- 梳理至少 2 种备选方案（例如：MySQL vs PostgreSQL，gRPC vs RESTful，Redis vs 本地缓存）；
- 从性能、开发成本、可维护性、团队技术栈契合度等维度打分评估（含置信度）；
- 推荐首选方案并阐述理由；与现有栈一致或大家通用的最优解，**首选直接写入顶部 `[VIBE_CONTRACT]` 与对应 ADR**；
- **选型拍板单（低成本确认点，阶段末强制）**：向开发者提交一页《选型拍板单》——首选方案 + 落选方案一句话理由 + 影响面，请开发者确认（APPROVED / 修订）；**选型是高返工风险决策，禁止完全静默自决**（纯工程内部等价选择除外）；
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
选型文档与 ADR 齐套且具备顶部 `[VIBE_CONTRACT]` 契约；**《选型拍板单》已获开发者确认（APPROVED）**；涉及新技术时全局学习笔记就绪；无未关闭的询问闸门事项；且仍建立在已冻结 PRD 之上（PRD 未回退破坏冻结）。

---
