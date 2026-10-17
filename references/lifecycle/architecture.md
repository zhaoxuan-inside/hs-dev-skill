# 阶段 2：范式落地与架构设计 (Paradigm & Architecture)

**何时读**：处理阶段 2：范式落地与架构设计 (Paradigm & Architecture)时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 阶段 2：范式落地与架构设计 (Paradigm & Architecture)

### 1. 核心目标
按规模/类型选定开发范式（后端 B 阶 / 前端 F 阶），再落模块边界与术语；**仅当范式含 DDD** 才做战略/战术领域模型。文档顶部同样强制包含 **`## [VIBE_CONTRACT] 架构执行契约`**（锁定范式阶、模块路径映射与依赖方向硬规则）。主详规：**[dev_paradigm.md](../dev_paradigm.md)**；子集：**[ddd_design.md](../ddd_design.md)** / **[backend_arch.md](../backend_arch.md)** / **[frontend_arch.md](../frontend_arch.md)**。

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
