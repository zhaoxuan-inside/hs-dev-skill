# 1. 项目文件组织架构

**何时读**：处理1. 项目文件组织架构时；先沿用[入口公共约束](../spec_v2_4.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
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
