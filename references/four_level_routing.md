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
[中层 L1: 业务总结]  hs_dev_docs/ (接口参数契约 / 方法七维画像 / 调用链路)
        │            ▲ 高信噪比派生视图，记录业务意图与符号锚点 (Symbol Anchor)
        ▼            │ 【第 2 次收口：契约锁定与符号定位】
[底层 L0: 物理真理]  7 大最底层数据资产 (产品原型 + 架构决策 + 源码 + DDL + 测试 + 配置 + 变更历史)
                     ▲ 【第 3 次收口：精准行段切片 (10~30 行)】
```

### 5.1 七大最底层物理数据资产矩阵 (The 7 Ground-Truth Pillars)

在系统工程中，代码不是凭空产生的，**产品设计是“业务意图的第一因”，架构设计是“工程结构的第一因”**。以下 7 类构成了软件系统绝不说谎的不可替代底层资产：

1. **产品设计与交互原型真理 (`DESIGN.md` / `{feature}_prototype.html` / PRD)**：
   - 业务意图与人机体验的第一事实源。包含宏观品味宪章、Design Tokens、单文件零依赖可交互 HTML 原型以及面向机器的 `vibe_spec.md`。
2. **系统架构与技术选型真理 (`ADR` / 深模块 / `[VIBE_CONTRACT]`)**：
   - 工程结构与非功能约束的第一事实源。包含架构决策记录（不可逆约束）、系统深模块词汇、设计模式协同集群与顶置机器执行契约。
3. **业务源码实现真理 (`backend/` / `frontend/` / `apps/` / `packages/` / `src/`)**：
   - 机器运行态物理执行与控制流的唯一实现体。
4. **数据模式与持久层真理 (`migrations/V*.sql` / `U*.sql`)**：
   - 物理存储骨架、表结构、字段类型、索引与主外键完整性约束。
5. **自动化测试与行为验证真理 (`test/` / `_08_test_data/` / Mock Profiles)**：
   - 系统可执行行为正确性的物理裁决者。代码对不对，以测试断言（Assert）能否通过为硬指标。
6. **运行环境与构建配置真理 (`config/` / `.env.example` / `Makefile` / `package.json`)**：
   - 声明底层系统依赖、编译器工具链、网络拓扑与密钥隔离规约。
7. **版本控制与过程审计真理 (`.git/` / `_01_plan_log/` / `_02_change_log/*.jsonl`)**：
   - 记录每一行物理代码的增删改历史、任务状态机断点与无损物理回滚镜像。

### 5.2 派生总结与索引层定位

- **中层总结 (L1 - Derived Summaries)**：如 `_06_method_design`（方法七维画像）、`_05_interface_design`（接口契约）、`_07_call_chain`（调用拓扑）。它们是从上述 L0 物理真理中提炼出来的高密度业务契约视图。
- **顶层索引 (L2 - Index of Summaries)**：`doc_index.sqlite`（FTS5 / JSONL），对 L1 总结建立的毫秒级倒排索引。

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

---

## 7. 全维度精准索引路由表与 CLI 映射指南 (Universal Index Routing Matrix)

为了防止 Agent 在面对开发需求时退化为暴力整盘扫描，系统为 7 大底层物理真理建立了对应的毫秒级专用索引工具。在执行各阶段任务时，**强制优先运行对应命令**：

| 探索 / 开发意图 | 目标底层真理源 | 强制执行的索引 CLI 指令 | 产出物与下游动作 |
|---|---|---|---|
| **找功能 / 查业务特性** | `_01_product_design/` (PRD) | `python scripts/doc_index_db.py feature-search --q <关键词>` | 返回关联特性 ID、摘要与 PRD 文件路径 |
| **找页面 / 布局 / 线框图** | `_01_product_design/` (Pages) | `python scripts/doc_index_db.py page-search --q <关键词>` | 返回页面路由、布局模型与线框图切片 |
| **查架构设计模式 / 防破坏** | `_02_pattern_clusters/` | `python scripts/doc_index_db.py pattern-search --q <模式名>` | 返回协同方法清单与抗劣化安全护栏 |
| **查数据表 / DDL 结构** | `migrations/V*.sql`, `data_schemas` | `python scripts/doc_index_db.py schema-search --q <表名>` | 返回字段摘要、关联特性与 DDL 迁移文件路径 |
| **查方法依赖 / 爆炸半径** | 源码 AST / 调用拓扑 | `python scripts/doc_index_db.py dep-graph --symbol <方法名>` | 输出上游调用者（爆炸半径）与下游被调者（Mock范围）Mermaid 图 |
| **查全局调用拓扑** | 全局依赖关系表 | `python scripts/doc_index_db.py dep-graph` | 输出系统核心高频 Top 枢纽方法与全局调用拓扑 |
| **新建方法前意图查重** | `_06_method_design` | `python scripts/doc_index_db.py method-search --q <业务意图>` | 匹配重合度 ≥80% 强制复用，严禁新建同义影子方法 |
| **代码精准切片** | 源码业务实现 | `python scripts/doc_index_db.py symbol-slice --name <符号名>` | 直接返回函数的精确行号与源码切片（免读大文件） |
| **查测试用例 / 单跑指令** | `_07_test_design/`, `tests/` | `python scripts/doc_index_db.py test-search --q <关键词>` | 瞬间返回精准单跑命令（如 `pytest test.py::case`） |
| **查过程账本 / 恢复快照** | `_02_change_log/*.jsonl` | `python scripts/doc_index_db.py audit-search --since <时间>` | 返回指定时间段内的变更快照、修改前状态与影响文件 |


