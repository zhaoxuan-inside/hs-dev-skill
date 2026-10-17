## 1. 文档体系核心架构与三层收敛漏斗

为解决复杂项目中 Agent 和人类工程师读取文档时的 Token 爆炸与盲目性，本体系构建了严格的**三层数据收敛漏斗**：

```text
[顶层 L2: 索引大脑]  doc_index.sqlite (FTS5 / 关键词倒排索引 / 毫秒级快速路由)
        │            ▲
        ▼            │ 【第 1 次收口：意图检索 (feature/page/schema/method-search)】
[中层 L1: 业务总结]  hs_dev_docs/ (接口契约 / 方法七维画像 / 模式集群 / 调用链路)
        │            ▲ 高信噪比派生视图，记录业务意图与符号锚点 (Symbol Anchor)
        ▼            │ 【第 2 次收口：契约锁定与符号定位】
[底层 L0: 物理真理]  7 大最底层数据资产 (产品原型 + 架构决策 + 源码 + DDL + 测试 + 配置 + 变更历史)
                     ▲ 【第 3 次收口：精准行段切片 (10~30 行)】
```

### 1.1 两级目录规约
整个 `hs_dev_docs` 严格遵循**两级目录规约**：一级功能域 `_00_` ~ `_06_` + 二级子功能原子拆分，严格遵循 `_01_xxx` 顺序命名规则，彻底消除深层任意嵌套，实现 `Domain + Category` 二元高信噪比精准检索与极速切片装配。

---

## 2. 全功能域直接索引导航目录表 (Direct Index Catalog)

以下为系统所有功能域及二级子域的直接索引表，点击相对路径直达对应目录或文件：

| 序号 | 功能域 | 相对路径 | 权威 .idx 索引 | 职责定位与核心产出物 |
|:---|:---|:---|:---|:---|
| **00** | **项目基座与全局规范**<br/>`_00_project_foundation` | [`_00_project_foundation/`](./_00_project_foundation/) | [`_00_project_foundation.idx`](./_00_project_foundation/_00_project_foundation.idx) | **系统底座与通用规则**<br/>• `_01_dev_rule`: 编码规范与 Lint 门禁<br/>• `_02_dictionary`: [`_02_project_word.dict.yaml`](./_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml) 统一术语单一事实源<br/>• `_03_decision_record`: 架构决策记录 (ADR)<br/>• `_04_code_map`: 代码地图与模块拓扑 (按需/SQLite 索引承载)<br/>• `_05_doc_index`: [`doc_index.sqlite`](./_00_project_foundation/_05_doc_index/doc_index.sqlite) 倒排索引数据库 |
| **01** | **产品愿景与分阶段定界**<br/>`_01_product_vision` | [`_01_product_vision/`](./_01_product_vision/) | [`_00_product_vision.idx`](./_01_product_vision/_00_product_vision.idx) | **业务意图第一因与阶段定界**<br/>• `_01_design_charter`: 品味宪章、物理隐喻与 Design Tokens (`DESIGN.md`)<br/>• `_02_phased_roadmap`: 分阶段路线图、MVP 激进裁剪决策书<br/>• `_03_business_plan`: 商业模式与核心业务假设 (可选/按需) |
| **02** | **特性规格与原型契约**<br/>`_02_feature_spec` | [`_02_feature_spec/`](./_02_feature_spec/) | [`_00_feature_spec.idx`](./_02_feature_spec/_00_feature_spec.idx) | **产品特性规格与人机双视图**<br/>• `_01_human_prd`: 面向人类的产品需求文档<br/>• `_02_vibe_spec`: 面向机器/VibeCoding的契约规格 (`vibe_spec.md`)<br/>• `_03_prototype_html`: 单文件零依赖可交互原型 (`{feature}_prototype.html`)<br/>• `_04_prototype_wireframe`: 空间拓扑与多端线框标注 |
| **03** | **系统架构设计与模式蓝图**<br/>`_03_architecture_design` | [`_03_architecture_design/`](./_03_architecture_design/) | [`_00_architecture_design.idx`](./_03_architecture_design/_00_architecture_design.idx) | **工程结构第一因与模式协同**<br/>• `_01_system_architecture`: 整体架构与分层蓝图<br/>• `_02_pattern_clusters`: GoF 设计模式协同集群档案与防破坏指针<br/>• `_03_adapter_spec`: 第三方/专用 SDK 防腐适配层规范 |
| **04** | **工程四要素详细契约**<br/>`_04_engineering_contract` | [`_04_engineering_contract/`](./_04_engineering_contract/) | [`_00_engineering_contract.idx`](./_04_engineering_contract/_00_engineering_contract.idx) | **工程实现物理契约真理**<br/>• `_01_db_schema`: 数据库表结构、DDL 与迁移基线 ([`_00_db_schema.idx`](./_04_engineering_contract/_01_db_schema/_00_db_schema.idx))<br/>• `_02_interface_design`: RESTful/RPC 接口契约 ([`_00_interface_design.idx`](./_04_engineering_contract/_02_interface_design/_00_interface_design.idx))<br/>• `_03_mock_contract`: Mock 数据契约与 Profile<br/>• `_04_method_design`: 方法七维画像与测试矩阵 ([`_00_method_design.idx`](./_04_engineering_contract/_04_method_design/_00_method_design.idx))<br/>• `_05_call_chain`: 核心调用链与时序拓扑 ([`_00_call_chain.idx`](./_04_engineering_contract/_05_call_chain/_00_call_chain.idx)) |
| **05** | **任务编排与上下文装配**<br/>`_05_task_orchestration` | [`_05_task_orchestration/`](./_05_task_orchestration/) | [`_00_task_orchestration.idx`](./_05_task_orchestration/_00_task_orchestration.idx) | **敏捷工程交付与上下文装载**<br/>• `_01_task_brief`: 任务简述清单 ([`_00_task_brief.idx`](./_05_task_orchestration/_01_task_brief/_00_task_brief.idx))<br/>• `_02_task_detail`: 任务状态机详述 ([`_00_task_detail.idx`](./_05_task_orchestration/_02_task_detail/_00_task_detail.idx))<br/>• `_03_task_context_pack`: 编译装配的高信噪比上下文包 ([`_00_context_pack.idx`](./_05_task_orchestration/_03_task_context_pack/_00_context_pack.idx))<br/>• `_04_task_archive`: 历史已完成任务归档 ([`_00_task_archive.idx`](./_05_task_orchestration/_00_task_archive.idx)) |
| **06** | **开发过程与治理审计**<br/>`_06_dev_process` | [`_06_dev_process/`](./_06_dev_process/) | [`_00_dev_process.idx`](./_06_dev_process/_00_dev_process.idx) | **过程账本与抗脆弱回滚镜像**<br/>• `_01_plan_log`: 计划与里程碑日志<br/>• `_02_change_log`: 变更流水账本 (非 Git 物理回滚依据)<br/>• `_03_verify_log`: 测试与一致性验证审计记录 (按需)<br/>• `_04_error_recovery`: 故障恢复与快照 (Snapshots)<br/>• `_05_tech_debt`: 技术债务清单与还债规划 (按需) |

---
