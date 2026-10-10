# 文档驱动开发（DDD）全生命周期驱动引擎指南

本指南定义了 `hs-dev-skill` 的核心驱动力——**7 阶段跃迁驱动生命周期（The 7-Stage Spec-Driven Lifecycle）**。

交互与自主边界见 **[置信度决策协议](confidence_decision.md)** 与 **[技术学习 / 偏好记忆 / GitHub 对标](learn_and_prefer.md)**：通用方案与偏好命中自主推进；新技术先学；模糊新技术/UI 先对标 GitHub 高星项目；仅当影响面广、项目特有、资料与偏好未提及且多选项置信接近时才询问开发者。

```text
  [阶段 0: 需求对齐与澄清] -- 按置信度澄清未决项，深挖场景、边界与 DoD
          | (产出齐套且无打开询问项)
          v
  [阶段 1: 技术选型与 ADR] -- 多端/多方案论证、架构决策记录 (ADR)
          | (通用/高置信自主定；接近分叉才问)
          v
  [阶段 2: 领域建模与架构] -- DDD 战略/战术划分、分层架构、统一术语词典
          | (产出齐套；触发询问闸门则先关闭)
          v
  [阶段 3: 详细设计四要素] -- DB (V/U) + 接口 (API) + 六元组方法 + 调用链
          | (完成详细设计与索引更新)
          v
  [阶段 4: 任务拆解与装载] -- 拆解为原子任务、生成 task_detail 与 context_pack
          | (进入任务执行状态机)
          v
  [阶段 5: 开发三同步实现] -- Mock先行 + 六元组代码 + V/U脚本 + 全覆盖单测
          | (代码与文档完全对齐)
          v
  [阶段 6: 全层级门禁自检] -- 一致性检查 + 死代码扫描 + 任务归档 + 本地 Commit（默认不 push）
```

**阶段跃迁总则**：不要求每阶段做一次「全文请确认」。产出物与索引齐套，且本阶段无未关闭的询问闸门事项，即可进入下一阶段。触发询问时将任务置 `BLOCKED`，用户决策落盘后再继续。

---

## 阶段 0：需求对齐与澄清 (Requirement Alignment)

### 1. 核心目标
杜绝“Agent 猜测项目特有需求直接写代码”，同时避免对通用做法逢项必问。先检索既有资料，再按置信度决策协议处理缺口。

### 2. Agent 行为准则
- 当用户提出新需求或新项目时，**第一步必须是需求对齐（阶段 0）**，而不是直接写代码或创建代码文件。
- 对齐维度（用作检查清单；**仅对满足询问闸门的项提问**）：
  1. **业务场景与目标**：核心业务流程是什么？谁是使用者？解决什么核心痛点？
  2. **输入与输出边界**：用户输入什么？预期产出什么？
  3. **异常与边缘用例**：网络超时、数据重复、并发冲突、权限越界时如何处理？（通用重试/幂等可高置信自定）
  4. **性能与规模预期**：预估 QPS、数据量级、时延要求？（无特有约束时可按常规默认并注明假设）
  5. **验收标准 (DoD)**：满足哪些具体断言才算任务完成？
- 用户只给一句话且核心场景/DoD 资料中不存在时，通常应询问；已足够清晰则直接产出 PRD，并列出高置信自主假设。

### 3. 产出文档
- `hs_dev_docs/_01_product_design/_02_product_design/{feature_name}_prd.md`
- 更新 `_01_product_design/_00_product_design.idx`

### 4. 阶段门禁
PRD 与索引齐套；打开的询问项已关闭（或未触发询问）。不强制「全文确认」阻塞跃迁。

---

## 阶段 1：技术选型与论证 (Tech Selection & ADR)

### 1. 核心目标
针对多端（后端/前端/移动端/桌面端）、语言、存储引擎、中间件、网络协议进行多方案对比分析，输出明确的架构决策记录（ADR）。

### 2. Agent 行为准则
- 选型前读 `~/.hs-dev-skill/preferences.yaml`；新技术写 `~/.hs-dev-skill/tech_learning/` 笔记；模糊路线先 GitHub 高星对标（≥2 候选）；
- 梳理至少 2 种备选方案（例如：MySQL vs PostgreSQL，gRPC vs RESTful，Redis vs 本地缓存）；
- 从性能、开发成本、可维护性、团队技术栈契合度等维度打分评估（含置信度）；
- 推荐首选方案并阐述理由；**与现有栈一致或大家通用的最优解直接选定并写入 ADR**；
- 仅当影响面广、项目特有、资料与全局偏好未提及且顶部分数接近时，结构化询问开发者；答复后更新全局偏好账本。

### 3. 产出文档
- `hs_dev_docs/_02_tech_select/_{platform}_tech_select.md`（如 `_07_backend_tech_select.md`）
- `hs_dev_docs/_00_project/_05_decision_record/ADR_{xxx}.md`
- 必要时：`~/.hs-dev-skill/tech_learning/{tech}_notes.md`、更新 `~/.hs-dev-skill/preferences.yaml`
- 更新对应 `.idx`

### 4. 阶段门禁
选型文档与 ADR 齐套；涉及新技术时全局学习笔记就绪；无未关闭的询问闸门事项。

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
在编写任何业务代码前，先建立完整的四维详细设计契约，作为系统实现的单一真理源。

### 2. 四维产出物
1. **数据库设计与迁移 (DB Schema)**：
   - 表结构设计：`_04_db_schema/_01_{model}/_01_{table}_design.md`（强制字段：`id`, `created_at`, `updated_at`, `description`, `is_del`, `version`，**严禁使用 SQL 关键字 `desc`**）；
   - 前向脚本：`migrations/V1.0.0__init_{table}.sql`；
   - 回滚脚本：`migrations/U1.0.0__init_{table}.sql`（V/U 强制原子配对）。
2. **接口契约设计 (Interface Design)**：
   - 接口文档：`_05_interface_design/_01_{model}/_01_{api}_design.md`；
   - Mock 契约：`_00_project/_13_mock_contract/{contract_name}.json`。
3. **六元组方法设计 (Six-Tuple Method Design)**：
   - 方法设计：`_06_method_design/_01_{model}/_01_{method}_design.md`；
   - 包含主方法、Saga 补偿方法（`_compensate`）、降级方法（`_fallback`）、度量（`_metrics`）、回调（`_recall`）。
4. **调用链拓扑分析 (Call Chain)**：
   - 调用时序图与依赖清单：`_07_call_chain/_01_{source}/_01_{source}_call_chain.md`。

### 3. 阶段门禁
四维设计文档与 V/U 脚本齐全，全量更新对应 `.idx` 索引。强制字段与六元组骨架不询问；对外契约语义、业务字段、不可逆补偿策略等若满足询问闸门则须先关闭再进入阶段 4。

---

## 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

### 1. 核心目标
将经过评审的详细设计拆解为独立、原子、可验证的工程任务项，并通过渐进式四级路由组装精准的上下文包。

### 2. Agent 行为准则
- 运行 `python3 scripts/task_manager.py create --id {task_id} --title "{task_title}"`；
- 自动生成 `_02_task_detail/`、`_01_task_brief/`（15行紧凑滚动清单）与 `_03_task_context_pack/`；
- 通过四级路由将阶段 0~3 的精准切片注入 `_00_context_pack.md`，控制 Token 预算。

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
