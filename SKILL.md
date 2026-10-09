---
name: hs-dev-skill
description: >-
  标准化文档驱动开发（DDD）与六元组架构执行引擎。提供 7 阶段生命周期驱动（需求多轮对齐澄清 -> 技术选型与ADR -> DDD领域架构设计 -> 四维详细设计 -> 任务拆解与渐进式装载 -> 开发三同步实现 -> 全层级门禁自检与归档）、渐进式四级索引（JSONL）检索、六元组方法运行时、数据库迁移原子同步（V/U）、Mock契约隔离。当用户提出新项目开发、需求变更、领域建模、重构或编写六元组业务逻辑时，必须以此技能作为主线引擎驱动执行。
---

# 产品开发 Skill (hs-dev-skill)

版本：v2.4  
核心定位：**文档驱动开发（DDD） + 7 阶段生命周期驱动引擎 + 六元组标准化运行时**

---

## ⚠️ 核心驱动铁律（Agent 强制遵守）

作为文档驱动开发引擎，你**必须主动扮演架构师与技术主管的角色，强力推进研发流程**，严禁未经阶段跃迁直接跳跃写代码：

1. **严禁无对齐跳步**：当用户提出任何需求时，**绝不允许直接编写代码或自行凭空创建任务**！第一步必须执行【阶段 0：多轮沟通与需求澄清】。
2. **严禁无设计编码**：在编写具体业务代码前，必须依次完成【阶段 1：技术选型】、【阶段 2：架构设计】与【阶段 3：详细设计四要素（DB+API+六元组+调用链）】。
3. **单向门禁流转**：每个阶段均有明确产出与门禁检查，未完成上一阶段前严禁越级进入下一阶段。

---

## 🔄 7 大阶段执行驱动流程 (The 7-Stage Workflow)

```text
[阶段 0: 需求对齐与澄清] ──(主动多轮提问、澄清场景、输出 PRD 并确认)
       │
[阶段 1: 技术选型与 ADR] ──(多端方案对比、输出选型方案与 ADR 并确认)
       │
[阶段 2: 领域建模与架构] ──(DDD 战略/战术划分、架构图、维护术语词典)
       │
[阶段 3: 详细设计四要素] ──(DB 表设计+V/U脚本 + 接口设计 + 六元组方法 + 调用链)
       │
[阶段 4: 任务拆解与装载] ──(拆解原子任务、生成 task_brief 与 context_pack)
       │
[阶段 5: 开发三同步实现] ──(Mock契约隔离 + 六元组代码实现 + 全覆盖单测)
       │
[阶段 6: 门禁自检与归档] ──(三文件校验 + 索引防漂移 + 死代码扫描 + 任务归档)
```

---

### 阶段 0：需求对齐与多轮深度沟通 (Requirement Alignment)

当收到用户的原始需求时，Agent 必须**主动提问并与用户多轮沟通**：

1. **主动发起结构化澄清**：
   - **用户场景与角色**：目标用户是谁？在什么业务链路下触发？
   - **正向业务流与边界**：输入载荷、核心处理节点、期望输出。
   - **异常与逆向流**：网络超时、第三方不可用、数据冲突时如何降级与补偿？
   - **性能与规模诉求**：预估并发量、QPS 峰值、数据保留周期。
   - **完成定义 (DoD)**：哪些指标和断言满足时判定功能完成？
2. **产出物**：
   - 编写 `hs_dev_docs/_01_product_design/_02_product_design/{feature}_prd.md`
   - 更新 `_01_product_design/_00_product_design.idx`
3. **阶段门禁**：向用户输出需求规格摘要，**获得用户确认后**方可进入阶段 1。

---

### 阶段 1：技术选型与论证 (Tech Selection & ADR)

1. **方案对比与论证**：
   - 梳理至少 2 种备选方案（前端/后端/多端 OS/存储/通信协议/框架）；
   - 从性能、可维护性、复杂度、团队技术栈契合度等维度评估并打分；
   - 给出推荐方案与充分理由。
2. **产出物**：
   - 编写 `hs_dev_docs/_02_tech_select/_{platform}_tech_select.md`
   - 编写 `hs_dev_docs/_00_project/_05_decision_record/ADR_{xxx}.md`
   - 更新对应 `.idx`
3. **阶段门禁**：向用户阐述技术选型理由，获得用户确认后进入阶段 2。

---

### 阶段 2：领域建模与架构设计 (Domain Modeling & Architecture)

1. **DDD 战略与战术建模**：
   - 划定限界上下文（Bounded Context）与上下文映射图；
   - 确立分层架构（接口层、应用编排层、领域层、基础设施层）；
   - 梳理聚合根、实体、值对象与领域事件；
   - 维护 `hs_dev_docs/_00_project/_02_project_word.dict.yaml`，统一全项目名词、实体、动词命名与禁止别名。
2. **产出物**：
   - 编写 `hs_dev_docs/_03_architecture_design/_{platform}_architecture_design.md`
   - 更新 `_00_project/_02_project_word.dict.yaml` 与对应 `.idx`
3. **阶段门禁**：架构分层明确、实体边界清晰。

---

### 阶段 3：详细规格设计四要素 (Detailed Spec Design)

在进入具体代码实现前，必须产出完整的四维详细设计规范：

1. **数据库设计与迁移 (DB Schema)**：
   - 编写 `_04_db_schema/_01_{model}/_01_{table}_design.md`（强制字段：`id`, `created_at`, `updated_at`, `description`, `is_del`, `version`，**严禁使用 SQL 保留字 `desc`**）；
   - 编写前向迁移 `migrations/V1.0.0__init_{table}.sql` 与回滚脚本 `migrations/U1.0.0__init_{table}.sql`（原子同步）。
2. **接口契约设计 (Interface Design)**：
   - 编写 `_05_interface_design/_01_{model}/_01_{interface}_design.md`；
   - 编写 Mock 契约 `_00_project/_13_mock_contract/{contract_name}.json`。
3. **六元组方法设计 (Six-Tuple Method Design)**：
   - 编写 `_06_method_design/_01_{model}/_01_{method}_design.md`；
   - 定义 5 个衍生方法：主方法、`_compensate`（Saga 补偿）、`_fallback`（熔断降级）、`_metrics`（度量）、`_recall`（回调）。
4. **调用链拓扑分析 (Call Chain)**：
   - 编写 `_07_call_chain/_01_{source}/_01_{source}_call_chain.md`，绘制时序图并记录依赖方法清单。
5. **产出物**：更新以上所有功能域的 `.idx` 索引文件。

---

### 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

1. **任务原子化拆解**：
   - 运行 `python3 scripts/task_manager.py create --id {task_id} --title "{task_title}" --priority "{P0/P1/P2}"`；
   - 自动生成 `_02_task_detail/`、`_01_task_brief/`（≤15 行滚动简述清单）与 `_03_task_context_pack/`。
2. **渐进式四级路由装载**：
   - 严格按照 `根索引 -> 域索引 -> 模块索引 -> 精确切片` 装载上下文；
   - 将阶段 0~3 中所需的精确设计注入 `_00_context_pack.md`，保障 Token 预算受控。

---

### 阶段 5：开发三同步实现 (Implementation & Three-Sync)

1. **执行开发三同步**：
   - **Mock 契约隔离**：配置 `mock/_06_test_profile/{profile}.yaml`，生产代码严禁硬编码 Mock 分支；
   - **六元组业务代码**：在 `backend/` 或指定端实现业务主方法、`_compensate` 补偿逻辑与 `_fallback` 降级逻辑；
   - **全覆盖单元与契约测试**：在 `test/_01_method_test/` 编写测试，核心分支覆盖率 ≥ 85%，降级与补偿分支 100% 覆盖。
2. **状态流转**：
   - 运行 `python3 scripts/task_manager.py status --id {task_id} --set IN_PROGRESS`
   - 完成开发并发起验证：`python3 scripts/task_manager.py status --id {task_id} --set VERIFYING`

---

### 阶段 6：全层级门禁自检与交付归档 (Quality Gate & Closure)

1. **执行自动化门禁自检**：
   - 运行单元与契约测试：`make test`（确保 100% PASS）；
   - 运行一致性与规范门禁：`python3 scripts/verify_consistency.py --root .`（检查三文件一致性、索引防漂移、DB 迁移 V/U 配对、SQL 保留字）；
   - 运行死代码扫描：`python3 scripts/dead_code_scanner.py --root .`（确保所有方法均在调用链有引用）。
2. **任务归档与提交**：
   - 运行 `python3 scripts/task_manager.py status --id {task_id} --set COMPLETED`（自动从活跃索引移入 `_00_task_archive.idx`）；
   - 按照 `<type>(<scope>): <subject>` 规范生成 Git Commit 并推送。

---

## 🛠️ CLI 工具箱速查

| 工具脚本 | 功能职责 | 常用命令 |
|---|---|---|
| [`init_hs_dev_docs.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/init_hs_dev_docs.py) | 初始化/对齐规范目录与 JSONL 索引 | `python3 scripts/init_hs_dev_docs.py --root .` |
| [`task_manager.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/task_manager.py) | 任务创建、状态机流转、三文件强一致性同步、会话交接 | `python3 scripts/task_manager.py create --id {id} --title "{title}"`<br>`python3 scripts/task_manager.py status --id {id} --set IN_PROGRESS` |
| [`verify_consistency.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/verify_consistency.py) | 提交前全量门禁自检（三文件/索引/SQL/迁移） | `python3 scripts/verify_consistency.py --root .` |
| [`dead_code_scanner.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/dead_code_scanner.py) | 基于调用链拓扑的死代码/孤儿方法扫描 | `python3 scripts/dead_code_scanner.py --root .` |
| [`idx_manager.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/idx_manager.py) | JSONL `.idx` 索引增删改查与哈希校验 | `python3 scripts/idx_manager.py verify {idx_path}` |

---

## 📚 规范与脚手架参考手册

- [全生命周期驱动引擎指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/spec_driven_lifecycle.md)
- [规格定义书 v2.4 正式版](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/spec_v2_4.md)
- [六元组标准化运行时指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/six_tuple_runtime.md)
- [渐进式四级索引路由指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/four_level_routing.md)
- [任务生命周期与状态机指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/task_state_machine.md)
- [Mock 规范与契约测试指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/mock_contract_guide.md)
- [全层级质量门禁指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/quality_gates.md)
- [脚手架与文档模板库](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/resources/templates/)
- [端到端订单服务参考实现](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/examples/order_service/)
