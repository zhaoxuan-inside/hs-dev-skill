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

## 阶段 0：产品设计与需求冻结 (Product Design & Alignment)

### 1. 核心目标
全面强化专业产品设计能力，产出可冻结的专业级产品设计方案，作为后续研发路径的权威真理源。
**产出边界铁律（绝对纯净原则）**：产品设计的产出**只需要且必须**包含两大部分：
1. **产品的设计语言 (Product Design Language)**（详见 [`product_design.md`](product_design.md)）；
2. **产品的功能 (Product Features & Functionality)**（详见 [`product_design.md`](product_design.md)）。

> [!IMPORTANT]
> **严禁底层技术细节反向侵入产品设计**：
> 严禁在阶段 0 的 PRD 或原型文档中提前塞入底层技术选型（如 MySQL vs PG）、物理数据库 DDL、接口代码实现签名、分布式 Saga 补偿、代码单元测试覆盖率指标等工程实现细节！这些是阶段 1（选型）至阶段 3（四要素详设）的职责。产品设计阶段只对产品的设计语言与功能规格负责。

### 2. Agent 行为准则
- **第一步是分级**（[`right_sizing.md`](right_sizing.md)），再进入本阶段的设计与对齐深度。
- **产品设计指南驱动**：深度遵循 [`product_design.md`](product_design.md)，从产品定位到交互全状态进行专业设计。
- **审讯式对齐**：`work_mode=DESIGN` 时走 [`grill_orchestration.md`](grill_orchestration.md) / [`confidence_decision.md`](confidence_decision.md)；跳过受 §1.5 收紧。
- **商业计划可选**：存在 `_01_business_plan/` 则纳入冲突扫描；缺失不阻断、不追讨。
- **设计语言与原型必有（有 UI）**：用户未提供则 Agent 生成；不能出图 → Mermaid 结构化多态线框 + Design Tokens 规范（[`product_prototype.md`](product_prototype.md) / [`product_design.md`](product_design.md)）。纯 API/批处理在 PRD 写「无 UI，豁免原型与设计语言」。
- S：数行 DoD/影响面即可，不强制完整 PRD；DoD 须从用户与产品功能视角可断言。
- M/L：正式完成产品设计（设计语言 + 功能规格书）；再选型/详设/编码。
- **产品设计对齐与规划双支柱**：
  1. **支柱一：产品设计语言 (Design Language)**：具象对标参照物与视觉调性、Design Tokens（色/字/空/圆角/阴影）、核心组件六态规范（Default/Hover/Active/Loading/Disabled/Error）、交互微动效与设计禁忌（Do's & Don'ts）。
  2. **支柱二：产品功能规格 (Features & Functionality)**：产品价值与用户画像、功能架构全景树、用户端到端核心旅程、详细功能规格矩阵（输入/触发/业务规则/输出/边界异常）、界面信息架构与页面四态（Empty/Loading/Populated/Error）、产品验收标准 (DoD)。
- **冲突扫描**：对照会话、可选商业计划、原型、既有 PRD/词典、代码与全局偏好，消除矛盾。

### 3. 产出文档
- （可选）`hs_dev_docs/_01_product_design/_01_business_plan/…`
- `hs_dev_docs/_01_product_design/_02_product_design/{feature_name}_prd.md`（产品功能规格书，专注功能架构、旅程、规格矩阵与功能 DoD）
- （有 UI）`hs_dev_docs/_01_product_design/_03_product_figma/{feature_name}_prototype.md`（产品设计语言与多态界面原型，包含 Tokens、组件状态与四态线框，并同步项目根 `DESIGN.md`）
- 更新 `_01_product_design/_00_product_design.idx`

### 4. 产品需求冻结门禁（进入阶段 1 的硬前提）

下列条件**全部**满足方可进入阶段 1；任一项不满足则停在阶段 0（询问或补齐），开发者确认后更新 PRD/原型再检：

| 条件 | 含义 |
|---|---|
| **设计语言完备** | 有 UI 时：具象调性定位清晰、Design Tokens（色/字/空/圆角/阴影）完整、核心组件六态定义完备； |
| **产品功能完备** | 功能架构树、用户端到端旅程、详细功能规格矩阵（输入/规则/输出/边界）清晰；页面覆盖四态（空/加载/正常/错误）；产品 DoD 从功能交互视角清晰可测； |
| **纯净无技术侵入** | 严格杜绝在阶段 0 文档中提前塞入底层技术选型、物理表 DDL、RPC 接口签名、Saga 补偿、代码单测覆盖率等研发实现细节； |
| **无冲突一致性** | PRD 内部及与设计语言、原型、既有资料（含可选商业计划）之间无未裁决矛盾； |
| **原型齐套** | 有 UI：原型与设计语言文档存在且四态可读；无 UI：PRD 已声明豁免； |

通过后**立即**进入阶段 1，不得空等。不强制对整份 PRD 做「全文请确认」——冻结依据是上述客观门禁，而非仪式性签字。


---

## 阶段 1：技术选型与论证 (Tech Selection & ADR)

### 1. 核心目标
在**已冻结的产品需求**约束下，针对多端（后端/前端/移动端/桌面端）、语言、存储引擎、中间件、网络协议进行多方案对比分析，输出明确的架构决策记录（ADR）。

### 2. Agent 行为准则
- **前置**：阶段 0 产品需求冻结门禁已通过；未通过则禁止本阶段任何落盘与选型结论。
- 选型前读 `~/.hs-dev-skill/preferences.yaml`；新技术写 `~/.hs-dev-skill/tech_learning/` 笔记；模糊路线先 GitHub 高星对标（≥2 候选）；
- 梳理至少 2 种备选方案（例如：MySQL vs PostgreSQL，gRPC vs RESTful，Redis vs 本地缓存）；
- 从性能、开发成本、可维护性、团队技术栈契合度等维度打分评估（含置信度）；
- 推荐首选方案并阐述理由；**与现有栈一致或大家通用的最优解直接选定并写入 ADR**；
- 选型结论必须可追溯到已冻结 PRD 的约束与 DoD；
- 仅当影响面广、项目特有、资料与全局偏好未提及且顶部分数接近时，结构化询问开发者；答复后更新全局偏好账本；
- 若选型暴露产品语义未决：**回退阶段 0**，闭合后再继续。

### 3. 产出文档
- `hs_dev_docs/_02_tech_select/_{platform}_tech_select.md`（如 `_07_backend_tech_select.md`）
- `hs_dev_docs/_00_project/_05_decision_record/ADR_{xxx}.md`
- 必要时：`~/.hs-dev-skill/tech_learning/{tech}_notes.md`、更新 `~/.hs-dev-skill/preferences.yaml`
- 更新对应 `.idx`

### 4. 阶段门禁
选型文档与 ADR 齐套；涉及新技术时全局学习笔记就绪；无未关闭的询问闸门事项；且仍建立在已冻结 PRD 之上（PRD 未回退破坏冻结）。

---

## 阶段 2：范式落地与架构设计 (Paradigm & Architecture)

### 1. 核心目标
按规模/类型选定开发范式（后端 B 阶 / 前端 F 阶），再落模块边界与术语；**仅当范式含 DDD** 才做战略/战术领域模型。主详规：**[dev_paradigm.md](dev_paradigm.md)**；子集：**[ddd_design.md](ddd_design.md)** / **[backend_arch.md](backend_arch.md)** / **[frontend_arch.md](frontend_arch.md)**。

### 2. Agent 行为准则
- L2 优先读 `dev_paradigm.md`（本会话未读时）；按选定阶再读 `backend_arch` / `frontend_arch` /（若 B4+）`ddd_design`（各每会话最多一次）；
- 非 DDD：模块图 + 依赖方向 + 词典即可；禁止硬套聚合/BC 仪式；
- DDD 档：BC 图 + 上下文映射 + 聚合/VO/事件；前端 feature 与边界对齐（或显式 BFF）；
- 依赖只向内；外部经 Adapter；模板见 `resources/templates/architecture_design/arch_design_template.md`；
- 常规分层高置信自主推进；范式升级/BC 切割若触询问闸门四条件则询问；
- 仍不够 → `rule_fetch`：按范式选 `ciembor.*` / `wshobson.*` / `fsd.skill` 等。

### 3. 产出文档
- `hs_dev_docs/_03_architecture_design/_{platform}_architecture_design.md`（含范式阶 + 模块/BC 与前端对齐表）
- `hs_dev_docs/_00_project/_02_project_word.dict.yaml`
- 更新对应 `.idx`

### 4. 阶段门禁
范式阶与「不升级」理由已写；模块（或 BC）边界清晰；词典完备；前端模块对齐表已填（若有 UI）；触发的询问项已关闭。

---

## 阶段 3：详细规格设计四要素 (Detailed Spec Design)

### 1. 核心目标
L：四维契约齐套后再编码。M：只更新触达维。S：跳过。范式见 `dev_paradigm.md`；DDD 档见 `ddd_design.md`；后端见 `backend_arch.md`；前端结构见 `frontend_arch.md`；接口见 `api_engineering.md`；UI 手艺/视觉见 `frontend_craft.md` / `design_md.md`。

### 2. 四维产出物
1. **数据库设计与迁移 (DB Schema)**：
   - 表结构设计：`_04_db_schema/_01_{model}/_01_{table}_design.md`（强制字段：`id`, `created_at`, `updated_at`, `description`, `is_del`, `version`，**严禁使用 SQL 关键字 `desc`**）；
   - 前向脚本：`migrations/V1.0.0__init_{table}.sql`；
   - 回滚脚本：`migrations/U1.0.0__init_{table}.sql`（V/U 强制原子配对）。
2. **接口契约设计 (Interface Design)**：
   - 接口文档：`_05_interface_design/_01_{model}/_01_{api}_design.md`（错误码、分页、幂等）；
   - Mock 契约：`_00_project/_13_mock_contract/{contract_name}.json`。
3. **六元组方法设计 (Six-Tuple Method Design)**：
   - 方法设计：`_06_method_design/_01_{model}/_01_{method}_design.md`；
   - 主方法、`_compensate`、`_fallback`、`_metrics`、`_recall`。
4. **调用链拓扑分析 (Call Chain)**：
   - `_07_call_chain/_01_{source}/_01_{source}_call_chain.md`。

### 3. 阶段门禁
路径要求的设计与 V/U（若触达 DB）及 `.idx` 齐套。骨架不询问；契约语义/业务字段/不可逆补偿若触询问闸门须先关闭。

---

## 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

### 1. 核心目标
将经过评审的详细设计拆解为独立、原子、可验证的工程任务项，并通过渐进式四级路由 / SQLite 检索组装**物化**上下文包（见 [`token_budget.md`](token_budget.md)）。

### 2. Agent 行为准则
- 运行 `python scripts/task_manager.py create --id {task_id} --title "{task_title}"`（Linux/macOS 可用 `python3`；Windows 可用 `py -3`）；
- 自动生成 `_02_task_detail/`、`_01_task_brief/`、`_03_task_context_pack/` 与 `_01_plan_log/{task_id}_plan.md`；
- 优先 `python scripts/doc_index_db.py --root . search|slice` 定位阶段 0~3 切片，将**原文**写入 `_00_context_pack.md`（禁止只写路径）；控制 Token 预算。
- 改代码/设计文件前：`python scripts/process_log.py checkpoint --id {task_id} --step … --summary "…" --paths …`（见 [`process_continuity.md`](process_continuity.md)）。

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
1. **运行全量测试**：`make test` 确保 100% PASS。
2. **运行一致性门禁检查**：`python3 scripts/verify_consistency.py --root .`。
3. **运行死代码与孤儿方法扫描**：`python3 scripts/dead_code_scanner.py --root .`。
4. **流转任务状态并归档**：`python3 scripts/task_manager.py status --id {task_id} --set COMPLETED`（自动归档至 `_00_task_archive.idx`）。
5. **Git 规范提交**：按照 `<type>(<scope>): <subject>` 规范生成本地 Commit。**默认不** `git push`；**仅当用户明确要求推送**时代为执行并回报结果。
