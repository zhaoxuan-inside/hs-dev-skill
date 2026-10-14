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

---

## 5. 三层收口漏斗与底层数据真理源 (The Three-Tier Convergence Funnel)

为解决大型工程中直接扫代码导致的 Token 爆炸与盲目性，本体系构建了清晰的**三层数据收敛漏斗**：

```text
[顶层 L2: 索引大脑]  doc_index.sqlite (FTS5 / 关键词倒排索引)
        │            ▲
        ▼            │ 【第 1 次收口：意图检索】
[中层 L1: 业务总结]  hs_dev_docs/ (PRD 规格 / 接口契约 / 方法七维画像)
        │            ▲ 过滤 90% 语法噪音，记录业务契约与符号锚点 (Symbol Anchor)
        ▼            │ 【第 2 次收口：契约锁定与符号定位】
[底层 L0: 物理真理]  源码 (backend/apps) + DDL (migrations/*.sql) + 测试 (test/)
                     ▲ 【第 3 次收口：精准行段切片 (10~30 行)】
```

1. **底层物理真实数据 (Level 0 - Ground Truth)**：
   - 业务源代码（执行态唯一真理）；
   - 数据库迁移脚本 `migrations/*.sql`（数据骨架约束）；
   - 测试用例与断言 `test/`（行为合法性真理）；
   - 环境变量与配置 `config/.env.example`。
2. **中层业务契约与总结 (Level 1 - High-Density Summaries)**：
   - 对底层代码的高度抽象，记录业务语义、改动敏感度（`CRITICAL`）、模式护栏及符号锚点；
3. **顶层轻量索引 (Level 2 - Index of Summaries)**：
   - 建立在文档总结之上，体积小（几十 KB），毫秒级召回。

**抗脆弱铁律**：严禁在文档中硬编码绝对行号。改用**符号锚点 (Symbol Anchor)**，由底层 AST 动态求值物理行号，消除代码格式化或修改造成的行号漂移。

---

## 6. 多端工程目录收敛规约 (Multi-Client Codebase Taxonomy)

针对项目各端源码的存放边界，强制执行收敛隔离：

| 目录 | 适用场景 | 职责与内容 |
|---|---|---|
| **`backend/`** | 单工程 / Web 分离架构 | 服务端 API、领域逻辑、DB 持久化、中间件集成 |
| **`frontend/`** | 单工程 / Web 分离架构 | **特指 Web 网页前端**（React/Vue/Svelte），不包含原生移动与桌面客户端 |
| **`src/`** | 单体工程 / 纯库开发 | 单一语言/职责的主源码目录 |
| **`apps/<client>/`** | **多端与客户端架构（强制）** | 包含移动端（`apps/mobile`）、桌面端（`apps/desktop`）、Web端（`apps/web`）与服务端（`apps/server`）入口 |
| **`packages/`** | **多端跨端共享库（强制）** | 跨端统一数据模型（DTO/Types）、API 客户端 SDK、设计规范 Tokens |
| **`output/<client>/`** | **构建产物隔离区（强制）** | 安装包（`.apk`, `.ipa`, `.exe`, `.dmg`）必须重定向输出至此，移动端强制成对归档符号表（`mapping.txt` / `dSYM.zip`） |

