# 项目文档阅读说明与跨 Agent 索引机制规范 (Documentation Reading Guide Spec)

**何时读**：需要理解或接入项目的 `hs_dev_docs/` 体系、多 Agent 协同索引导航、或者需要为存量/新项目生成全景文档阅读说明时。

---

## 1. 为什么需要统一的「项目文档阅读说明」？

在多 Agent（如 Claude、GPT-4o、DeepSeek、Gemini 或 IDE Agent）协作与复杂产品工程中，常常面临两大极端痛点：
1. **盲目全量通读引发 Token 爆炸与失忆**：Agent 介入项目时，直接递归通读 `hs_dev_docs/` 或扫描源码，导致上下文窗口迅速耗尽、信噪比骤降、注意力被无关背景冲淡。
2. **缺乏全景索引导致割裂与重复实现**：不同 Agent 无法快速定位既有业务 PRD、数据表 Schema、RESTful 接口或通用工具方法，极易导致方案漂移、影子函数（Shadow Functions）暴增与架构坏味道。

为此，本体系在 `hs_dev_docs/` 根目录下强制生成**《项目文档阅读说明与全局索引导航》（`hs_dev_docs/_00_docs_compass.md`）**。该文件充当人机双重视角下的**统一文档索引中枢与全局导航罗盘**。

---

## 2. 核心架构与三层收敛漏斗 (Convergence Funnel)

项目文档体系通过**三层收敛漏斗**实现高信噪比索引：

```text
[顶层 L2: 索引大脑]  doc_index.sqlite (FTS5 / 倒排索引 / 毫秒级) + _00_hs_dev_docs.idx
        │            ▲
        ▼            │ 【第 1 次收口：意图检索 (feature/page/schema/method-search)】
[中层 L1: 业务总结]  hs_dev_docs/ (接口契约 / 方法七维画像 / 模式集群 / 调用链路)
        │            ▲ 高信噪比派生视图，记录业务意图与符号锚点 (Symbol Anchor)
        ▼            │ 【第 2 次收口：契约锁定与符号定位】
[底层 L0: 物理真理]  7 大最底层数据资产 (产品原型 + 架构决策 + 源码 + DDL + 测试 + 配置 + 变更历史)
                     ▲ 【第 3 次收口：精准行段切片 (10~30 行)】
```

- **两级目录规约**：一级功能域 `_00_` ~ `_06_` + 二级子功能原子拆分，严格遵循 `_01_xxx` 顺序命名规则，彻底消除深层任意嵌套。
- **天然人机同构**：人类工程师通过 Markdown 表格与链接直观阅读；Agent 通过置顶的 `[VIBE_CONTRACT]` YAML 契约与标准 CLI 子命令进行毫秒级切片装配。

---

## 3. 《项目文档阅读说明》规范要素

生成的 `hs_dev_docs/_00_docs_compass.md` 必须包含以下六大核心区块：

### 3.1 [VIBE_CONTRACT] 机器极速索引契约 (顶部 [VIBE_CONTRACT] 至下一同级标题)
置顶于文档顶部，供 LLM / Agent 切片读取。包含：
- 文档根目录与索引数据库路径 (`doc_index.sqlite`)
- 一级功能域与权威 JSONL `.idx` 映射表
- 专用 CLI 检索指令快捷方式清单
- Agent 行为禁令（如禁止通读、强制使用切片、强制对齐统一词典）

### 3.2 体系架构与漏斗图解
展示从顶层索引到底层物理真理的三层收敛拓扑，明确中层契约的派生属性与底层代码的一等地位。

### 3.3 全功能域直接索引导航表 (Direct Index Catalog)
以 Markdown 表格形式罗列全部 7 大功能域（`_00_project_foundation` 到 `_06_dev_process`）及其核心子目录，提供可直接点击跳转的相对路径链接、对应权威 `.idx` 文件与核心产出物说明。

### 3.4 Agent 专属检索操作手册 (Playbook)
提供 10 大专用检索子命令的完整矩阵，供外部 Agent 在不扫描全盘的前提下，精准召回所需上下文：
- `feature-search`：按业务关键词检索 PRD
- `page-search`：检索页面路由与线框规范
- `pattern-search`：检索 GoF 设计模式集群与防破坏护栏
- `schema-search`：检索数据库表结构与 DDL
- `dep-graph`：查询方法调用拓扑与爆炸半径
- `method-search`：写前意图检索（查重率 ≥80% 强制复用）
- `symbol-slice`：获取 AST 符号源码精准切片
- `test-search`：获取测试用例与单跑命令
- `audit-search`：查阅变更账本与快照
- `slice`：截取指定文档高信噪比行段

### 3.5 意图驱动的推荐阅读路径 (Scenario Reading Pathways)
为不同任务意图（`BUILD` 从零构建、`REVERSE` 存量反向重建、`FIX` 缺陷修复、`REFACTOR` 行为等价重构、`EXPLORE` 代码理解、`RESUME` 任务续做）给出明确的推荐阅读次序，指引 Agent 快速完成上下文装载。

### 3.6 协同与防漂移治理铁律
- **统一术语 (Ubiquitous Language)**：以 `_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml` 为单一事实源。
- **符号锚点 (Symbol Anchor)**：严禁硬编码绝对物理行号，通过 AST 动态求值。
- **自愈索引**：变更设计文档后必须执行 `python scripts/doc_index_db.py --root . rebuild` 更新 SHA-256 Digest。

---

## 4. 自动化生成与增量维护

本规范提供开箱即用的自动化生成与自愈命令：

1. **工作区初始化自动生成**：
   ```bash
   python scripts/init_hs_dev_docs.py --root .
   ```
   在初始化目录与索引时，自动根据项目特征生成 `hs_dev_docs/_00_docs_compass.md`，并在全局根索引 `_00_hs_dev_docs.idx` 中完成注册与摘要校验。

2. **独立生成或刷新指令**：
   ```bash
   # 方式一：通过 init 脚本专用参数刷新
   python scripts/init_hs_dev_docs.py --root . --generate-guide

   # 方式二：通过文档索引库子命令刷新并自动重建 SQLite 索引
   python scripts/doc_index_db.py --root . generate-guide

   # 方式三：Makefile 快捷命令
   make doc-guide
   ```

3. **双层索引同步**：
   生成器在产出 `hs_dev_docs/_00_docs_compass.md` 后，会自动向 `_00_hs_dev_docs.idx` 写入 `doc_reading_guide` 条目并计算 SHA-256 前 8 位 Digest，确保在 `make verify` 时通过哈希防漂移门禁。
