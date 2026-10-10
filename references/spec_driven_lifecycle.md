# 文档驱动开发（DDD）全生命周期驱动引擎指南

本指南定义 `hs-dev-skill` 的 **7 阶段满配链（L）**。  
**任意需求第一步**先做变更分级：见 **[right_sizing.md](right_sizing.md)**（S/M 缩短路径；未分级禁止按满配开工）。

交互边界：**[confidence_decision.md](confidence_decision.md)**、**[learn_and_prefer.md](learn_and_prefer.md)**。  
UI/API 详设与实现按需：**[frontend_craft.md](frontend_craft.md)**、**[api_engineering.md](api_engineering.md)**。

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

## 阶段 0：需求对齐与澄清 (Requirement Alignment)

### 1. 核心目标
产出可冻结的产品需求（M/L）或轻量对齐记录（S），作为后续路径的产品真理源；杜绝带着产品空白选型，同时避免对通用做法逢项必问。

### 2. Agent 行为准则
- **第一步是分级**（`right_sizing.md`），再进入本阶段的对齐深度。
- S：数行 DoD/影响面即可，不强制完整 PRD。
- M/L：正式需求对齐；再选型/详设/编码。
- 对齐维度（用作完整性检查清单；产品缺口优先闭合）：
  1. **业务场景与目标**：核心业务流程是什么？谁是使用者？解决什么核心痛点？
  2. **输入与输出边界**：用户输入什么？预期产出什么？
  3. **异常与边缘用例**：网络超时、数据重复、并发冲突、权限越界时如何处理？（通用重试/幂等可高置信自定）
  4. **性能与规模预期**：预估 QPS、数据量级、时延要求？（无特有约束时可按常规默认并注明假设）
  5. **验收标准 (DoD)**：满足哪些具体断言才算任务完成？
- **冲突扫描**：对照会话、既有 PRD/ADR/词典、代码与全局偏好，消除互相矛盾的目标、边界、优先级与验收口径。
- 用户只给一句话且核心场景/DoD 资料中不存在时，必须询问并闭合后再冻结；工程通用假设可写入 PRD「自主假设」节，**不得**用假设填补会影响选型/架构的产品空白。

### 3. 产出文档
- `hs_dev_docs/_01_product_design/_02_product_design/{feature_name}_prd.md`
- 更新 `_01_product_design/_00_product_design.idx`

### 4. 产品需求冻结门禁（进入阶段 1 的硬前提）

三项**全部**满足方可进入阶段 1；任一项不满足则停在阶段 0（询问或补齐），开发者确认后更新 PRD 再检：

| 条件 | 含义 |
|---|---|
| **完整** | 场景/角色、正向流与 I/O 边界、影响架构的约束、可验证 DoD 均已写清；会影响选型或架构的产品空白已闭合（资料 / 偏好 / 对标 / 开发者确认） |
| **正确** | 与用户已表态、既有资料及全局偏好一致；高置信工程假设仅限通用惯例，且不改写业务语义 |
| **无冲突** | PRD 内部及与既有资料之间无未裁决矛盾 |

通过后**立即**进入阶段 1，不得空等。不强制对整份 PRD 做「全文请确认」——冻结依据是上述三项客观门禁，而非仪式性签字。

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

## 阶段 2：领域建模与架构设计 (Domain Modeling & Architecture)

### 1. 核心目标
建立 DDD 战略与战术模型，划分限界上下文（Bounded Context），确立分层架构与实体边界，统一定义项目术语词典。

### 2. Agent 行为准则
- 梳理核心领域对象（聚合根、实体、值对象、领域服务、仓储）；
- 绘制分层架构图与模块依赖拓扑；
- 维护 `_00_project/_02_project_word.dict.yaml`，统一全项目名词、实体、动词命名与禁止别名；
- 标准分层与常规聚合拆分高置信自主推进；限界上下文切割等若同时满足询问闸门四条件则询问。

### 3. 产出文档
- `hs_dev_docs/_03_architecture_design/_{platform}_architecture_design.md`
- `hs_dev_docs/_00_project/_02_project_word.dict.yaml`
- 更新对应 `.idx`

### 4. 阶段门禁
架构分层与实体边界清晰，术语词典完备；触发的询问项已关闭。

---

## 阶段 3：详细规格设计四要素 (Detailed Spec Design)

### 1. 核心目标
L：四维契约齐套后再编码。M：只更新触达维。S：跳过。接口细则见 `api_engineering.md`；UI 见 `frontend_craft.md`。

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
- 自动生成 `_02_task_detail/`、`_01_task_brief/`（15行紧凑滚动清单）与 `_03_task_context_pack/`；
- 优先 `python scripts/doc_index_db.py --root . search|slice` 定位阶段 0~3 切片，将**原文**写入 `_00_context_pack.md`（禁止只写路径）；控制 Token 预算。

---

## 阶段 5：开发三同步实现 (Implementation & Three-Sync)

### 1. 核心目标
以 TDD 和六元组规范驱动编码，保证业务代码、设计文档、迁移脚本、测试用例的绝对一致性。

### 2. 执行原则
1. **Mock 先行与契约隔离**：在 `mock/_06_test_profile/` 配置测试集 Profile，业务代码零 Mock 污染。
2. **六元组业务逻辑**：在 `backend/` 或对应端实现 `method`、`method_compensate`、`method_fallback`。
3. **全覆盖单元与契约测试**：在 `test/_01_method_test/` 编写测试，核心域分支覆盖率 ≥ 85%，降级与补偿分支 100% 覆盖。
4. **实现期分叉**：新暴露的选择点同样适用置信度决策；触发询问则 `status --set BLOCKED`，禁止静默猜测业务特有规则。

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
