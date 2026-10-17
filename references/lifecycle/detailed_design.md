# 阶段 3：详细规格设计四要素 (Detailed Spec Design)

**何时读**：处理阶段 3：详细规格设计四要素 (Detailed Spec Design)时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 阶段 3：详细规格设计四要素 (Detailed Spec Design)

### 1. 核心目标
L：四维契约齐套后再编码。M：只更新触达维。S：跳过。范式见 `dev_paradigm.md`；DDD 档见 `ddd_design.md`；后端见 `backend_arch.md`；前端结构见 `frontend_arch.md`；接口见 `api_engineering.md`；UI 手艺/视觉见 `frontend_craft.md` / `design_md.md`（**强制遵循 Modern Web Guidance 最新标准**：原生 Dialog/Popover、Container Queries、CSS `:has()`、Fetch Priority 与流式传输规范）。
**人机同构原则**：阶段 3 产出的 SQL DDL、接口 Schema、六元组签名和调用链时序图本身即为高度精确的工程语言，**保持单文件天然人机同构，绝不额外拆分**。

### 2. 四维产出物
1. **数据库设计与迁移 (DB Schema)**：
   - > [!IMPORTANT]
   > **DB 决策硬闸门（新增业务）**：**新增业务/新功能需要改动数据库设计（新增表、改表结构、破坏性迁移、不可逆字段）时，必须先经开发者决策确认**（见 [`confidence_decision.md`](../confidence_decision.md) §1.5 禁止跳过清单），再落表结构设计与 V/U 迁移脚本与编码。**不受实现期置信度自决约束**；开发者未确认前禁止写死 DDL。
   - 表结构设计：`_04_engineering_contract/_01_db_schema/_01_{model}/_01_{table}_design.md`（强制字段：`id`, `created_at`, `updated_at`, `description`, `is_del`, `version`，**严禁使用 SQL 关键字 `desc`**）；
   - 前向脚本：`migrations/V1.0.0__init_{table}.sql`；
   - 回滚脚本：`migrations/U1.0.0__init_{table}.sql`（V/U 强制原子配对）。
2. **接口契约设计 (Interface Design)**：
   - 接口文档：`_04_engineering_contract/_02_interface_design/_01_{model}/_01_{api}_design.md`（错误码、分页、幂等）；
   - Mock 契约：`_04_engineering_contract/_03_mock_contract/{contract_name}.json` 与 `mock/_06_test_profile/`。
3. **六元组与前端方法设计契约画像 (Method Archetypes & Contract Design)**：
   - 后端方法设计：`_04_engineering_contract/_04_method_design/_01_{model}/_01_{method}_design.md`（六元组主方法、`_compensate`、`_fallback`、`_metrics`、`_recall`，模板见 `method_design.md`）；
   - 前端方法设计：`_04_engineering_contract/_04_method_design/_02_{feature}/_01_{method}_design.md`（纯计算 ALGO、转换 TRANSFORM、策略 GUARD、状态 STATE、Hook 编排 ORCHESTRATE、适配 ADAPTER，模板见 `frontend_method_design.md`）；
   - 登记标准：**代码物理定位（实现后自动回填）、7 大方法类型、敏感度及理由、副作用及具体表现、0 DOM 依赖/精准跑测命令、以本方法为中心的局部依赖图与三段式历史修改记录**（遵循 [`method_archetypes.md`](../method_archetypes.md) 规范）。
4. **调用链拓扑分析 (Call Chain)**：
   - `_04_engineering_contract/_05_call_chain/_01_{source}/_01_{source}_call_chain.md`。

### 3. 阶段门禁
路径要求的设计与 V/U（若触达 DB）及 `.idx` 齐套。骨架不询问；契约语义/业务字段/不可逆补偿若触询问闸门须先关闭；**触达 DB 的新增业务：表结构设计与迁移须已获开发者决策确认**。

---
