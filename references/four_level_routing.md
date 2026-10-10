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
         ├───► [Level 2: 域索引]  _05_interface_design/_00_interface_design.idx
         │             │
         │             └───► [Level 3: 模块索引]  _05_interface_design/_01_order/_00_order_interface_design.idx
         │                           │
         │                           └───► [Level 4: 精确切片]  _01_order_create_design.md (Line 15-45)
         │
         ├───► [Level 2: 域索引]  _04_db_schema/_00_db_schema.idx
         └───► [Level 2: 域索引]  _08_dev_process/_00_dev_process.idx
```

---

## 3. 各级索引规范

### 3.1 一级：全局根索引 (`hs_dev_docs/_00_hs_dev_docs.idx`)
* **定位**：整个文档体系的单一入口，枚举所有业务功能域。
* **格式**：
```jsonl
{"version":"1.0","category":"root","root":"hs_dev_docs"}
{"id":"domain_project","title":"项目基础配置与规范域","path":"_00_project/_00_project.idx","status":"active"}
{"id":"domain_product","title":"产品需求与规划域","path":"_01_product_design/_00_product_design.idx","status":"active"}
{"id":"domain_tech","title":"技术选型域","path":"_02_tech_select/_00_tech_select.idx","status":"active"}
{"id":"domain_arch","title":"架构设计域","path":"_03_architecture_design/_00_architecture_design.idx","status":"active"}
{"id":"domain_db","title":"数据库与迁移域","path":"_04_db_schema/_00_db_schema.idx","status":"active"}
{"id":"domain_interface","title":"接口设计域","path":"_05_interface_design/_00_interface_design.idx","status":"active"}
{"id":"domain_method","title":"方法设计域","path":"_06_method_design/_00_method_design.idx","status":"active"}
{"id":"domain_call_chain","title":"调用链分析域","path":"_07_call_chain/_00_call_chain.idx","status":"active"}
{"id":"domain_process","title":"开发过程与任务域","path":"_08_dev_process/_00_dev_process.idx","status":"active"}
```

### 3.2 二级：功能域索引 (`_0N_{domain}/_00_{domain}.idx`)
* **定位**：某一领域下的业务模块列表（如 `order`、`user`、`payment`）。
* **示例**（`_05_interface_design/_00_interface_design.idx`）：
```jsonl
{"version":"1.0","category":"domain_interface","root":"_05_interface_design"}
{"id":"model_order","title":"订单模型接口","path":"_01_order/_00_order_interface_design.idx","status":"active"}
{"id":"model_user","title":"用户模型接口","path":"_02_user/_00_user_interface_design.idx","status":"active"}
{"id":"model_payment","title":"支付模型接口","path":"_03_payment/_00_payment_interface_design.idx","status":"active"}
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
