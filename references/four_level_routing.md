# 渐进式四级索引路由机制指南

## 1. 为什么需要渐进式索引？

在大型项目中，文档体系可能包含数百个文件与上万行设计。如果 Agent 在接到任务时全量加载所有文档，将导致：
1. **Token 预算严重超支**；
2. **上下文被无关信息稀释**（Attention Drift）；
3. **响应变慢且幻觉率上升**。

渐进式四级索引路由（Four-Level Progressive Routing）通过分层索引树，使 Agent 在定位任何模块时只需读取少量索引行，按需精确注入。

**工程加速（推荐）**：用跨平台 SQLite 查询缓存代替人工走树——`python scripts/doc_index_db.py --root . search --q ...` 直接返回 `path + summary`，再用 `slice` 取行段。JSONL `.idx` 仍是权威路由与 digest 源；SQLite 可随时 `rebuild`。详见 [`token_budget.md`](token_budget.md)。

---

## 2. 四级路由体系模型

```text
[Level 1: 根索引]  hs_dev_docs/_00_hs_dev_docs.idx
         │
         ├───► [Level 2: 一级功能索引]  _04_engineering_contract/_00_engineering_contract.idx
         │             │
         │             └───► [Level 3: 二级子功能索引]  _02_interface_design/_00_interface_design.idx
         │                           │
         │                           └───► [Level 4: 精确切片]  _01_order/_01_order_create_design.md (Line 15-45)
         │
         ├───► [Level 2: 一级功能索引]  _02_feature_spec/_00_feature_spec.idx
         └───► [Level 2: 一级功能索引]  _05_task_orchestration/_00_task_orchestration.idx
```

---

## 3. 各级索引规范

### 3.1 一级：全局根索引 (`hs_dev_docs/_00_hs_dev_docs.idx`)
* **定位**：整个文档体系的单一入口，枚举所有核心功能域。
* **格式**：
```jsonl
{"version":"1.0","category":"root","root":"hs_dev_docs"}
{"id":"domain_foundation","title":"项目基座与全局规范","path":"_00_project_foundation/_00_project_foundation.idx","status":"active"}
{"id":"domain_vision","title":"产品愿景与分阶段定界","path":"_01_product_vision/_00_product_vision.idx","status":"active"}
{"id":"domain_feature_spec","title":"特性详细规格与原型契约","path":"_02_feature_spec/_00_feature_spec.idx","status":"active"}
{"id":"domain_architecture","title":"系统架构设计与模式集群","path":"_03_architecture_design/_00_architecture_design.idx","status":"active"}
{"id":"domain_contract","title":"工程四要素详细契约","path":"_04_engineering_contract/_00_engineering_contract.idx","status":"active"}
{"id":"domain_task","title":"任务编排与极速装配","path":"_05_task_orchestration/_00_task_orchestration.idx","status":"active"}
{"id":"domain_process","title":"开发过程与治理审计","path":"_06_dev_process/_00_dev_process.idx","status":"active"}
```

### 3.2 二级：功能域索引 (`_0N_{domain}/_00_{domain}.idx`)
* **定位**：某一领域下的二级子功能或业务模块列表（如 `_04_engineering_contract` 下的 `db_schema`、`interface_design` 等）。
* **示例**（`_04_engineering_contract/_00_engineering_contract.idx`）：
```jsonl
{"version":"1.0","category":"domain_contract","root":"_04_engineering_contract"}
{"id":"sub_db","title":"数据库与迁移","path":"_01_db_schema/_00_db_schema.idx","status":"active"}
{"id":"sub_interface","title":"接口契约设计","path":"_02_interface_design/_00_interface_design.idx","status":"active"}
{"id":"sub_method","title":"方法分类画像","path":"_04_method_design/_00_method_design.idx","status":"active"}
{"id":"sub_call_chain","title":"调用链路拓扑","path":"_05_call_chain/_00_call_chain.idx","status":"active"}
```

### 3.3 三级：模块索引 (`_0N_{domain}/_01_{model_name}/_00_{model_name}_{domain}.idx`)
* **定位**：具体模块下的设计文档清单。
* **示例**（`_05_interface_design/_01_order/_00_order_interface_design.idx`）：
```jsonl
{"version":"1.0","category":"module_interface","root":"_05_interface_design/_01_order"}
{"id":"if_order_create","title":"创建交易订单接口","path":"_01_order_create_design.md","digest":"a7f3b8c2","status":"active"}
{"id":"if_order_cancel","title":"取消订单接口","path":"_02_order_cancel_design.md","digest":"c4d9e1f0","status":"active"}
```

### 3.4 四级：精确切片注入
Agent 在读取第三级锁定到 `_01_order_create_design.md` 后，利用局部阅读工具（指定 StartLine/EndLine）或：

```bash
python scripts/doc_index_db.py --root . slice --path hs_dev_docs/_05_interface_design/_01_order/_01_order_create_design.md --start 15 --end 45
```

仅将所需的签名、入参表和异常**物化**进 `_00_context_pack.md`，完成精确开发。禁止只写路径。

---

## 4. 索引维护与哈希防漂移机制（Digest）

条目中的 `digest` 字段记录目标文件的 SHA-256（前 8 位）。
* 当文档发生修改时，提交工具自动更新 `digest`。
* 启动时校验引擎可快速比对 `digest`，立即感知哪些设计文档被外部篡改或发生漂移。
* 批量变更后执行：`python scripts/doc_index_db.py --root . rebuild`，保持 SQLite 缓存与 `.idx` 对齐（三端同一命令）。
