# 4. 索引维护与哈希防漂移机制（Digest）

**何时读**：处理4. 索引维护与哈希防漂移机制（Digest）时；先沿用[入口公共约束](../four_level_routing.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
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
7. **版本控制与过程审计真理 (`.git/` / `_06_dev_process/_01_plan_log/` / `_06_dev_process/_02_change_log/*.jsonl`)**：
   - 记录每一行物理代码的增删改历史、任务状态机断点与无损物理回滚镜像。

### 5.2 派生总结与索引层定位

- **中层总结 (L1 - Derived Summaries)**：如 `_04_engineering_contract/_04_method_design`（方法七维画像）、`_04_engineering_contract/_02_interface_design`（接口契约）、`_04_engineering_contract/_05_call_chain`（调用拓扑）。它们是从上述 L0 物理真理中提炼出来的高密度业务契约视图。
- **顶层索引 (L2 - Index of Summaries)**：`doc_index.sqlite`（FTS5 / JSONL），对 L1 总结建立的毫秒级倒排索引。
- **全局文档阅读与直接索引导航 (`hs_dev_docs/_00_docs_compass.md`)**：作为连接人类工程师与协同 Agent 的全局导航罗盘，置顶 `[VIBE_CONTRACT]` 机器索引契约，提供 7 大功能域直接索引表与 10 大专用 CLI 指令（详见 [`doc_reading_guide.md`](../doc_reading_guide.md)）。可通过 `make doc-guide` 或 `python scripts/doc_index_db.py --root . generate-guide` 自动生成与刷新。

**抗脆弱铁律**：严禁在文档中硬编码绝对行号。改用**符号锚点 (Symbol Anchor)**，由底层 AST 动态求值物理行号，消除代码格式化或修改造成的行号漂移。

---
