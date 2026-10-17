# 6. 多端工程目录收敛规约 (Multi-Client Codebase Taxonomy)

**何时读**：处理6. 多端工程目录收敛规约 (Multi-Client Codebase Taxonomy)时；先沿用[入口公共约束](../four_level_routing.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
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
| **找功能 / 查业务特性** | `_02_feature_spec/_01_human_prd/` | `python scripts/doc_index_db.py feature-search --q <关键词>` | 返回关联特性 ID、摘要与 PRD 文件路径 |
| **找页面 / 布局 / 线框图** | `_02_feature_spec/_04_prototype_wireframe/` | `python scripts/doc_index_db.py page-search --q <关键词>` | 返回页面路由、布局模型与线框图切片 |
| **查架构设计模式 / 防破坏** | `_03_architecture_design/_02_pattern_clusters/` | `python scripts/doc_index_db.py pattern-search --q <模式名>` | 返回协同方法清单与抗劣化安全护栏 |
| **查数据表 / DDL 结构** | `migrations/V*.sql`, `data_schemas` | `python scripts/doc_index_db.py schema-search --q <表名>` | 返回字段摘要、关联特性与 DDL 迁移文件路径 |
| **查方法依赖 / 爆炸半径** | 源码 AST / 调用拓扑 | `python scripts/doc_index_db.py dep-graph --symbol <方法名>` | 输出上游调用者（爆炸半径）与下游被调者（Mock范围）Mermaid 图 |
| **查全局调用拓扑** | 全局依赖关系表 | `python scripts/doc_index_db.py dep-graph` | 输出系统核心高频 Top 枢纽方法与全局调用拓扑 |
| **新建方法前意图查重** | `_04_engineering_contract/_04_method_design` | `python scripts/doc_index_db.py method-search --q <业务意图>` | 匹配重合度 ≥80% 强制复用，严禁新建同义影子方法 |
| **代码精准切片** | 源码业务实现 | `python scripts/doc_index_db.py symbol-slice --name <符号名>` | 直接返回函数的精确行号与源码切片（免读大文件） |
| **查测试用例 / 单跑指令** | `_04_engineering_contract/`, `test/` | `python scripts/doc_index_db.py test-search --q <关键词>` | 瞬间返回精准单跑命令（如 `pytest test.py::case`） |
| **查过程账本 / 恢复快照** | `_06_dev_process/_02_change_log/*.jsonl` | `python scripts/doc_index_db.py audit-search --since <时间>` | 返回指定时间段内的变更快照、修改前状态与影响文件 |
