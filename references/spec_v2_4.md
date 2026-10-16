# 产品开发 Skill 规格定义书

版本：随当前 Skill 包维护（版本以 SKILL.md 与 resources/skill_routes.json 为准；文件名为历史兼容路径）
定位：文档驱动开发 + 六元组标准化运行时 + Agent 上下文引擎

---

## 1. 项目文件组织架构

跨项目共享（不在仓库内）：`Path.home() / ".hs-dev-skill"`（Windows / Linux / macOS；`preferences.yaml`、`tech_learning/`），由 `scripts/init_hs_global.py` 初始化；协议见 `references/learn_and_prefer.md`，三端约定见 `references/cross_platform.md`。

```text
/project_home_path/
├── {project_name}/
│   ├── .gitignore
│   ├── README.md
│   ├── LICENSE
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md
│   ├── .editorconfig
│   ├── .env.example
│   ├── Makefile
│   ├── docker-compose.yml
│   │
│   ├── backend/
│   ├── frontend/
│   ├── linux/
│   ├── mac/
│   ├── windows/
│   ├── android/
│   ├── ios/
│   │
│   ├── test/
│   │   ├── _00_e2e/
│   │   ├── _01_method_test/
│   │   ├── _02_integration_test/
│   │   ├── _03_contract_test/
│   │   ├── _04_regression_test/
│   │   ├── _05_performance_test/
│   │   ├── _06_security_test/
│   │   ├── _07_compatibility_test/
│   │   └── _08_test_data/
│   │
│   ├── mock/
│   │   ├── _00_mock.idx
│   │   ├── _01_mock_server/
│   │   │   ├── _00_mock_server.idx
│   │   │   ├── _01_route/
│   │   │   ├── _02_handler/
│   │   │   ├── _03_middleware/
│   │   │   ├── _04_config/
│   │   │   └── _05_start_script/
│   │   ├── _02_mock_data/
│   │   │   ├── _00_mock_data.idx
│   │   │   ├── _01_dataset/
│   │   │   │   └── _01_{dataset_name}/
│   │   │   │       ├── _00_dataset.idx
│   │   │   │       ├── _01_data.json
│   │   │   │       └── _02_override.json
│   │   │   ├── _02_schema/
│   │   │   └── _03_fixture/
│   │   ├── _03_scenario/
│   │   │   ├── _00_scenario.idx
│   │   │   └── _01_{scenario_name}.md
│   │   ├── _04_error_inject/
│   │   ├── _05_delay_inject/
│   │   └── _06_test_profile/
│   │       ├── _00_test_profile.idx
│   │       └── _01_{profile_name}.yaml
│   │
│   ├── output/
│   ├── logs/
│   ├── config/
│   ├── scripts/
│   │
│   └── hs_dev_docs/
│       ├── _00_docs_compass.md                        # [全局罗盘] 项目文档阅读说明与直接索引导航（置顶 [VIBE_CONTRACT]）
│       ├── _00_hs_dev_docs.idx                       # 全局根索引（一级路由）
│       ├── _00_project_foundation/                   # [00 基座与全局规范]
│       │   ├── _00_project_foundation.idx
│       │   ├── _01_dev_rule/
│       │   ├── _02_dictionary/                       # _02_project_word.dict.yaml
│       │   ├── _03_decision_record/                  # ADR 架构决策记录
│       │   └── _05_doc_index/                        # doc_index.sqlite (FTS5 倒排索引库)
│       ├── _01_product_vision/                       # [01 产品愿景与定界]
│       │   ├── _00_product_vision.idx
│       │   ├── _01_design_charter/                   # DESIGN.md 宏观品味宪章
│       │   ├── _02_phased_roadmap/                   # MVP 范围裁定（审讯）与路线图
│       │   └── _03_business_plan/                    # 可选，按需创建的商业计划
│       ├── _02_feature_spec/                         # [02 特性规格与原型契约]
│       │   ├── _00_feature_spec.idx
│       │   ├── _01_human_prd/                        # 人类 PRD
│       │   ├── _02_vibe_spec/                        # 机器执行契约 vibe_spec.md
│       │   ├── _03_prototype_html/                   # 单文件多端可交互原型
│       │   └── _04_prototype_wireframe/              # 空间拓扑与多态线框
│       ├── _03_architecture_design/                  # [03 系统架构设计与模式蓝图]
│       │   ├── _00_architecture_design.idx
│       │   ├── _01_system_architecture/              # 整体架构拓扑与分层蓝图
│       │   ├── _02_pattern_clusters/                 # GoF 设计模式协同集群档案
│       │   └── _03_adapter_spec/                     # 第三方/专用 SDK 防腐层规范
│       ├── _04_engineering_contract/                 # [04 工程四要素详细契约]
│       │   ├── _00_engineering_contract.idx
│       │   ├── _01_db_schema/                        # 表结构 DDL 与迁移基线
│       │   ├── _02_interface_design/                 # RESTful/RPC 接口契约
│       │   ├── _03_mock_contract/                    # Mock 契约与数据 Profile
│       │   ├── _04_method_design/                    # 方法七维画像与精准单跑测试
│       │   └── _05_call_chain/                       # 核心业务调用链 Mermaid 时序拓扑
│       ├── _05_task_orchestration/                   # [05 任务编排与上下文装载]
│       │   ├── _00_task_orchestration.idx
│       │   ├── _01_task_brief/
│       │   ├── _02_task_detail/
│       │   ├── _03_task_context_pack/
│       │   └── _04_task_archive/
│       └── _06_dev_process/                          # [06 开发过程与治理记录]
│           ├── _00_dev_process.idx
│           ├── _01_plan_log/                         # 有序计划与断点账本
│           ├── _02_change_log/                       # 变更流水账本与快照 (非 Git 物理回滚依据)
│           ├── _03_qa_log/                           # 关键问答、裁定与冻结证据
│           └── _04_error_recovery/snapshots/         # 故障恢复物理快照
```

---

## 2. 个人开发规范

### 2.1 基本原则

1. 零死代码、零桩代码；
2. 配置与代码分离，禁止硬编码；
3. DDD 架构边界，模块自治，只访问自己的库和表；
4. 方法长度 20–40 行，超长强制拆分；
5. 逻辑控制与数据处理分离；
6. 通用控制逻辑沉淀到公共模块。

### 2.2 六元组标准化方法签名

```text
exception method_name(input, output, context, isolate, metrics, recall);
exception method_name_fallback(input, output, context, isolate, metrics, recall);
exception method_name_compensate(input, output, context, isolate, metrics, recall);
exception method_name_metrics(input, output, context, isolate, metrics, recall);
exception method_name_recall(input, output, context, isolate, metrics, recall);
```

| 字段 | 含义 | 约束 |
|---|---|---|
| `exception` | 执行结果状态 | 成功时为 `null` / `None` / `Ok(())`；失败时为 map/struct，含 `code`、`msg`、`retryable`、`details` |
| `input` | 输入 | 扁平化键名或类型载荷，如 `user.profile.age` |
| `output` | 输出 | 扁平化键名或容器对象 |
| `context` | 运行时上下文 | traceId、时间戳等；补偿/降级时挂载 `context.last_exception` |
| `isolate` | 隔离与安全 | 只读，包含 `tenant_id`、安全凭据等，严格限制透传 |
| `metrics` | 度量统计 | 耗时、计数、链路 |
| `recall` | 回调控制器 | 封装流程挂起、重试、安全与事件回调控制器 |

**异常结构标准**：

```json
{
  "code": "ORDER_STOCK_LOCK_TIMEOUT",
  "msg": "库存服务响应超时",
  "retryable": true,
  "details": {}
}
```

### 2.3 数据库设计与迁移规范

强制字段：
* `id`：主键（BIGINT / UUID）
* `created_at`：创建时间（UTC 时间戳 / DATETIME(6)）
* `updated_at`：更新时间（UTC 时间戳 / DATETIME(6)）
* `description`：描述与备注（**禁止使用 SQL 保留关键字 `desc`**）
* `is_del`：软删除标记（`0` 未删，大于 0 表示已删）
* `version`：乐观锁版本（默认 `1`，自增递增）

外键命名：`{table_name}_id`。

表设计文档必须包含：当前表结构表格、按版本倒序的变更历史、对应 V/U 脚本路径。
Design、V、U 三者原子同步。

迁移脚本命名：
```text
V{主}.{次}.{补丁}__{描述}.sql
U{主}.{次}.{补丁}__{描述}.sql
```

---

## 3. Git 提交信息规范

### 3.1 提交信息格式

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 type 类型

| type | 含义 |
|---|---|
| feat | 新增功能 |
| fix | 修复缺陷 |
| docs | 文档变更 |
| style | 格式调整，不影响逻辑 |
| refactor | 重构，不新增功能不修复缺陷 |
| perf | 性能优化 |
| test | 测试相关 |
| build | 构建、依赖、脚本变更 |
| chore | 杂项，不影响 src 与 test |
| revert | 回滚 |
| spec | 设计文档、接口、方法、DB、调用链变更 |
| migrate | 数据库迁移脚本变更 |
| mock | Mock 服务、Mock 数据、测试集配置变更 |

### 3.3 提交与推送边界（强制）

- 常规流程：Agent 在门禁通过后执行**本地** `git commit`，**不主动**推送。
- **仅当用户明确要求推送**（如「推送代码」「帮我 push」「push 到远程」）时，Agent 可代为执行 `git push`（含首次 `-u`）并回报结果。
- 未获明确推送授权时，禁止 `git push` / 等价远程推送。

---

## 4. 全层级质量保障机制

| 层级 | 范围 | 门禁 |
|---|---|---|
| `_00_e2e` | 端到端全链路 | 冒烟全通过，覆盖主流程与致命错误 |
| `_01_method_test` | 方法级单元测试 | 核心域业务逻辑分支覆盖率 ≥ 85%，核心方法降级与补偿分支 100% 覆盖 |
| `_02_integration_test` | DB、缓存、中间件联调 | 事务原子性、补偿生效、超时熔断 |
| `_03_contract_test` | 前后端/多端协议 | 字段增删改必须静态比对与协议断言 |
| `_04_regression_test` | 回归 | 历史缺陷用例全通过 |
| `_05_performance_test` | 性能 | 基准达标，无退化 |
| `_06_security_test` | 安全 | 注入、越权、脱敏、密钥检查 |
| `_07_compatibility_test` | 兼容 | 浏览器、OS、设备、版本矩阵 |
| `_08_test_data` | 测试数据 | 脱敏、可重复、可清理 |

---

## 5. Mock 规范

1. 业务代码中严禁包含 Mock 桩、Mock 分支、测试数据硬编码；
2. Mock 必须作为独立服务启动，通过接口或网络层接入；
3. Mock 代码与 Mock 数据必须分离；
4. Mock 契约必须与 `_04_engineering_contract/_02_interface_design`、`_03_contract_test` 保持一致；
5. 测试集通过 profile 组合，不改代码即可切换数据、场景、错误与延迟；
6. Mock 契约单一真理源位于 `hs_dev_docs/_04_engineering_contract/_03_mock_contract/`。

---

## 6. Skill 执行引擎运行时机制

### 6.1 `.idx` 索引文件规范（JSONL）

`.idx` 统一采用 **JSONL（JSON Lines）** 格式：每行一个独立 JSON 对象。

首行为元数据行，包含 `version`、`category`、`root`；其余每行为一个索引条目。

```jsonl
{"version":"1.0","category":"interface","root":"_04_engineering_contract/_02_interface_design"}
{"id":"order_create","title":"创建订单与锁库","path":"_04_engineering_contract/_02_interface_design/_01_order/_01_order_create_design.md","digest":"a1b2c3d4","status":"active"}
{"id":"order_cancel","title":"取消订单","path":"_04_engineering_contract/_02_interface_design/_01_order/_02_order_cancel_design.md","digest":"e5f6g7h8","status":"active"}
```

### 6.2 渐进式四级路由体系

1. **一级（根索引）**：读 `hs_dev_docs/_00_hs_dev_docs.idx` 定位功能域；
2. **二级（域索引）**：读 `_0N_{domain}/_00_{domain}.idx` 定位子模块；
3. **三级（模块索引）**：读 `_00_{model_name}_{domain}.idx` 锁定目标文档；
4. **四级（精确注入）**：仅注入目标文档精确章节/行号。

### 6.3 任务三文件一致性约束

- `task_id` 为唯一主键。
- `_05_task_orchestration/` 下的 `_00_task.idx`、`_01_task_brief/`、`_02_task_detail/` 中的 `task_id`、`title`、`status`、`updated` 必须一致。
- 变更顺序：先改 `task_detail`，再同步 `task_brief`，最后更新 `task.idx`。
