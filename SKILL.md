---
name: hs-dev-skill
description: >-
  标准化文档驱动开发（DDD）与六元组架构执行引擎。支持 Windows / Linux / macOS 三端运行。提供 7 阶段生命周期驱动、置信度决策、跨项目全局偏好与技术学习（Path.home()/.hs-dev-skill）、模糊新技术/UI优先对标 GitHub 高星成熟方案、渐进式四级索引（JSONL）、六元组方法运行时、数据库迁移原子同步（V/U）、Mock契约隔离。默认流程终点为本地 Git Commit，不主动 push；仅当用户明确要求推送时代为执行 git push。当用户提出新项目开发、旧项目优化、需求变更、领域建模、重构或编写六元组业务逻辑时，必须以此技能作为主线引擎驱动执行。
---

# 产品开发 Skill (hs-dev-skill)

版本：v2.8  
核心定位：**文档驱动开发（DDD） + 三端可运行（Windows/Linux/macOS）+ 7 阶段生命周期 + 置信度决策 + 学习/偏好记忆 + 六元组运行时；默认止于本地 Commit，明确要求时可推送**

---

## ⚠️ 核心驱动铁律（Agent 强制遵守）

作为文档驱动开发引擎，你**必须主动扮演架构师与技术主管的角色，强力推进研发流程**，严禁未经阶段跃迁直接跳跃写代码：

1. **严禁无对齐跳步**：当用户提出任何需求时，**绝不允许直接编写代码或自行凭空创建任务**！第一步必须执行【阶段 0：需求对齐与澄清】。
2. **严禁无设计编码**：在编写具体业务代码前，必须依次完成【阶段 1：技术选型】、【阶段 2：架构设计】与【阶段 3：详细设计四要素（DB+API+六元组+调用链）】。
3. **单向门禁流转**：每个阶段均有明确产出与门禁检查，未完成上一阶段前严禁越级进入下一阶段。
4. **置信度决策（询问闸门）**：落盘或编码前先评估置信度。**大家通用的解决方案不询问、自主推进**。**仅当同时满足**——影响面广、且为项目特有、且用户在之前的所有资料中都没有提到、且存在多种置信度接近的选择——时，才向开发者询问并由其决策；否则禁止用猜测填项目特有空白，也禁止为显然项打断用户。细则见 [`references/confidence_decision.md`](references/confidence_decision.md)。
5. **新技术学习与偏好记忆（全局共享）**：凡用到新技术必须先学习并落盘到 **`Path.home() / ".hs-dev-skill" / "tech_learning"`**；偏好写入同目录下 **`preferences.yaml`**（Linux/macOS：`$HOME/.hs-dev-skill/`；Windows：`%USERPROFILE%\.hs-dev-skill\`）。目录缺失时先运行 `python scripts/init_hs_global.py`（或 `python3` / `py -3`）。细则见 [`references/learn_and_prefer.md`](references/learn_and_prefer.md) 与 [`references/cross_platform.md`](references/cross_platform.md)。
6. **模糊新技术/UI 优先 GitHub 高星对标**：新技术以及 UI 等用户描述模糊的需求，**优先**从 GitHub 检索高 Star、仍维护的成熟项目方案，学模式后写入选型/设计依据（可复用结论进全局学习笔记），再评估置信度；禁止无对标凭空臆造交互与落地方式。
7. **三端可运行（Windows / Linux / macOS）**：本 Skill、CLI 与全局目录必须在三端可用；路径用 `pathlib`，命令同时兼容 `python3` / `python` / `py -3`，无 make 时用等价 Python 命令。禁止只按单一 OS 写死路径或 shell。细则见 [`references/cross_platform.md`](references/cross_platform.md)。
8. **默认止于提交；明确要求才推送**：常规流程终点是**本地 Git Commit**（门禁通过后按 Conventional Commits 提交），**禁止主动** `git push`。**仅当用户明确提出推送**（如「推送代码」「帮我 push」「push 到远程」等）时，Agent 才可代为执行 `git push`（含首次 `-u`）；未明确授权时不得推送。

---

## 🔄 7 大阶段执行驱动流程 (The 7-Stage Workflow)

```text
[阶段 0: 需求对齐与澄清] ──(按置信度澄清未决项、输出 PRD；无打开询问项即可跃迁)
       │
[阶段 1: 技术选型与 ADR] ──(多方案对比；通用/高置信自主定，接近分叉才问)
       │
[阶段 2: 领域建模与架构] ──(DDD 战略/战术划分、架构图、维护术语词典)
       │
[阶段 3: 详细设计四要素] ──(DB 表设计+V/U脚本 + 接口设计 + 六元组方法 + 调用链)
       │
[阶段 4: 任务拆解与装载] ──(拆解原子任务、生成 task_brief 与 context_pack)
       │
[阶段 5: 开发三同步实现] ──(Mock契约隔离 + 六元组代码实现 + 全覆盖单测)
       │
[阶段 6: 门禁自检与归档] ──(门禁 + 任务归档 + 本地 Commit；默认不 push，用户明确要求时代推)
```

阶段跃迁：**产出齐套且无未关闭的询问闸门事项**即可进入下一阶段；不要求每阶段全文请用户确认。触发询问时任务置 `BLOCKED`，用户决策写入文档后再继续。

---

### 阶段 0：需求对齐与澄清 (Requirement Alignment)

当收到用户的原始需求时，先读既有资料（含全局 `~/.hs-dev-skill/preferences.yaml`），再按置信度决策协议处理缺口（不是逢项必问）：

1. **对齐检查清单**（仅对「资料未覆盖 + 项目特有 + 影响面广」且选项置信接近的项提问）：
   - **用户场景与角色**：目标用户是谁？在什么业务链路下触发？
   - **正向业务流与边界**：输入载荷、核心处理节点、期望输出。
   - **异常与逆向流**：网络超时、第三方不可用、数据冲突时如何降级与补偿？（通用降级/重试可高置信自定）
   - **性能与规模诉求**：预估并发量、QPS 峰值、数据保留周期。（无特有约束时可按常规默认并注明假设）
   - **完成定义 (DoD)**：哪些指标和断言满足时判定功能完成？
2. **模糊新技术 / UI**：描述不清时，先按 [`learn_and_prefer.md`](references/learn_and_prefer.md) 做 GitHub 高星对标与（如需）技术学习，再写 PRD；对标后能定案则不询问。
3. **产出物**：
   - 编写 `hs_dev_docs/_01_product_design/_02_product_design/{feature}_prd.md`
   - 更新 `_01_product_design/_00_product_design.idx`
4. **阶段门禁**：PRD 与索引齐套；打开的询问项已关闭（或本阶段无触发询问）。摘要中可列出「高置信自主假设」供纠偏，不因此阻塞跃迁。

---

### 阶段 1：技术选型与论证 (Tech Selection & ADR)

1. **学习与对标（选型前）**：
   - 读 `~/.hs-dev-skill/preferences.yaml`，同类偏好直接继承（跨项目）；
   - 新技术：学习并落盘 `~/.hs-dev-skill/tech_learning/{tech}_notes.md`；
   - 模糊选型/UI 技术路线：检索 GitHub 高星成熟项目，至少对比 2 个候选，将采纳点写入选型文档（可复用模式写入全局笔记）。
2. **方案对比与论证**：
   - 梳理至少 2 种备选方案（前端/后端/多端 OS/存储/通信协议/框架）；
   - 从性能、可维护性、复杂度、团队技术栈契合度等维度评估并打分（含置信度）；
   - 给出推荐方案与充分理由；**与现有栈一致或通用最优解直接选定**；仅当影响面广、项目特有、资料/全局偏好未提及且顶部分数接近时询问。
3. **产出物**：
   - 编写 `hs_dev_docs/_02_tech_select/_{platform}_tech_select.md`
   - 编写 `hs_dev_docs/_00_project/_05_decision_record/ADR_{xxx}.md`
   - 更新对应 `.idx`；用户拍板或纠偏后同步更新 **`~/.hs-dev-skill/preferences.yaml`**
4. **阶段门禁**：选型文档与 ADR 齐套；无未关闭的询问闸门事项；涉及新技术时全局学习笔记已就绪。

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
3. **阶段门禁**：架构分层明确、实体边界清晰、词典与索引齐套；上下文切割等若触发询问闸门则须先关闭。

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
6. **阶段门禁**：四维设计与索引齐套；对外契约/业务字段/不可逆补偿等若触发询问闸门则须先关闭，通用字段与骨架不询问。

---

### 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

1. **任务原子化拆解**：
   - 运行 `python scripts/task_manager.py create --id {task_id} --title "{task_title}" --priority "{P0/P1/P2}"`；
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
   - 运行 `python scripts/task_manager.py status --id {task_id} --set IN_PROGRESS`
   - 完成开发并发起验证：`python scripts/task_manager.py status --id {task_id} --set VERIFYING`
3. **实现期分叉**：新暴露的选择点同样走置信度决策；触发询问则 `BLOCKED`，禁止静默猜测业务特有规则。

---

### 阶段 6：全层级门禁自检与交付归档 (Quality Gate & Closure)

1. **执行自动化门禁自检**：
   - 运行单元与契约测试：`make test` 或 `python -m unittest discover -s tests -p "test_*.py"`（确保 100% PASS）；
   - 运行一致性与规范门禁：`python scripts/verify_consistency.py --root .`（检查三文件一致性、索引防漂移、DB 迁移 V/U 配对、SQL 保留字）；
   - 运行死代码扫描：`python scripts/dead_code_scanner.py --root .`（确保所有方法均在调用链有引用）。
2. **任务归档与本地提交**（默认流程终点）：
   - 运行 `python scripts/task_manager.py status --id {task_id} --set COMPLETED`（自动从活跃索引移入 `_00_task_archive.idx`）；
   - 按照 `<type>(<scope>): <subject>` 规范生成**本地** Git Commit；
   - **默认不推送**；仅当用户**明确要求推送**时再执行 `git push`（必要时 `-u`），完成后回报远程结果。

---

## 🛠️ CLI 工具箱速查

| 工具脚本 | 功能职责 | 常用命令 |
|---|---|---|
| [`hs_paths.py`](scripts/hs_paths.py) | 打印当前 OS 下全局路径解析（Win/Linux/macOS） | `python scripts/hs_paths.py` |
| [`init_hs_global.py`](scripts/init_hs_global.py) | 初始化全局共享区 `Path.home()/.hs-dev-skill` | `python scripts/init_hs_global.py` |
| [`init_hs_dev_docs.py`](scripts/init_hs_dev_docs.py) | 初始化/对齐规范目录与 JSONL 索引 | `python scripts/init_hs_dev_docs.py --root .` |
| [`task_manager.py`](scripts/task_manager.py) | 任务创建、状态机流转、三文件强一致性同步、会话交接 | `python scripts/task_manager.py create --id {id} --title "{title}"` |
| [`verify_consistency.py`](scripts/verify_consistency.py) | 提交前全量门禁自检（三文件/索引/SQL/迁移） | `python scripts/verify_consistency.py --root .` |
| [`dead_code_scanner.py`](scripts/dead_code_scanner.py) | 基于调用链拓扑的死代码/孤儿方法扫描 | `python scripts/dead_code_scanner.py --root .` |
| [`idx_manager.py`](scripts/idx_manager.py) | JSONL `.idx` 索引增删改查与哈希校验 | `python scripts/idx_manager.py verify {idx_path}` |

> 解释器：Linux/macOS 优先 `python3`；Windows 可用 `python` 或 `py -3`。下文 `python` 均表示「当前平台可用的 Python 3」。

---

## 📚 规范与脚手架参考手册

- [跨平台支持（Windows / Linux / macOS）](references/cross_platform.md)
- [置信度决策协议](references/confidence_decision.md)
- [技术学习、偏好记忆与 GitHub 对标](references/learn_and_prefer.md)
- [全生命周期驱动引擎指南](references/spec_driven_lifecycle.md)
- [规格定义书 v2.4 正式版](references/spec_v2_4.md)
- [六元组标准化运行时指南](references/six_tuple_runtime.md)
- [渐进式四级索引路由指南](references/four_level_routing.md)
- [任务生命周期与状态机指南](references/task_state_machine.md)
- [Mock 规范与契约测试指南](references/mock_contract_guide.md)
- [全层级质量门禁指南](references/quality_gates.md)
- [脚手架与文档模板库](resources/templates/)
- [端到端订单服务参考实现](examples/order_service/)
