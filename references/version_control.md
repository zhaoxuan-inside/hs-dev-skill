# 版本号控制与演进规则指南 (Version Control Rules)

**何时读**：
- 规划软件发布、版本升级、制定对外 API 策略、新增数据库迁移脚本（阶段 3 详设 / 阶段 6 交付归档）；
- 维护或升级 Skill 本身时（修改 `SKILL.md`、`README.md` 元数据或扩展规范）。
- 检索命令：`python scripts/skill_ref_index.py search --scenario 版本`

---

## 1. 核心定位与双轨控制原则

本指南确立**双轨版本控制体系**，以 **SemVer 2.0.0（语义化版本，Semantic Versioning）** 为统一基石：
1. **轨 A：Skill 自身版本控制（Skill Package Lifecycle）**：保障 `hs-dev-skill` 作为研发基础设施的单源一致、向下兼容与规范演进。
2. **轨 B：工程项目研发与交付版本控制（Project Deliverable Lifecycle）**：规范由本 Skill 驱动的业务系统在阶段 0～6 全生命周期中的软件版本发布、变更分级映射、API 演化、DB 迁移及 Git Tag 门禁。

---

## 2. 轨 A：Skill 自身版本控制规则 (Skill Package)

### 2.1 版本号格式与定义
格式采用语义化版本：`v{MAJOR}.{MINOR}` 或 `v{MAJOR}.{MINOR}.{PATCH}`（当前为 `v2.22`）。
- **MAJOR (主版本)**：发生破坏性方法论变更（例如状态机合法跃迁硬逻辑不兼容重构、核心目录或索引体系破坏性重写、移除或废弃核心 CLI/产物）；
- **MINOR (次版本)**：新增规约文档、新增阶段支持、新增 CLI 脚本/子命令、扩展门禁检查项（且兼容现有项目）；
- **PATCH (修订版本)**：文档错别字修正、Bug 修复、补充单测、微调示例与模板。

### 2.2 三处元数据单源一致性铁律 (Single Source of Truth)
Skill 自身发布或迭代时，必须保证以下三处版本号**绝对一致**，严禁出现版本漂移：
1. `SKILL.md` frontmatter 的 `metadata.version`（例如 `"2.22"`）；
2. `SKILL.md` 正文首部的 `版本：v2.22`；
3. `README.md` 的 Shields badge（例如 `[![Spec Version](https://img.shields.io/badge/skill-v2.22-blue.svg)](SKILL.md)`）。

`verify_consistency.py` 会将上述三处一致性作为门禁进行检查，发现不一致直接报错阻断。

---

## 3. 轨 B：工程研发与交付版本控制规则 (Project & Deliverable)

### 3.1 变更分级 (Right-Sizing) 与交付版本映射
需求与任务分级（[`right_sizing.md`](right_sizing.md)）直接决定发布版本号的跃迁梯度：

| 变更分级 | 对应版本跃迁 | 典型场景 | 门禁与发布策略 |
|---|---|---|---|
| **S (Small)** | **PATCH** (`X.Y.Z → X.Y.Z+1`) | 纯内部 Bugfix、安全热补丁、局部非逻辑重构、无对外影响的文档/样式调整 | 跑通单测与局部回归；不触发 API/DB 主版本变更 |
| **M (Medium)** | **MINOR** (`X.Y.Z → X.Y+1.0`) | 新增向下兼容的业务功能、新增接口/字段、新增数据库表或字段 | 阶段 0 PRD 冻结；DB 前向+回滚脚本；契约测试通过 |
| **L (Large)** | **MAJOR** (`X.Y.Z → X+1.0.0`) 或重首发 | 存在破坏性变更（Breaking Changes）、跨微服务边界重构、核心数据模型重做 | 阶段 0～6 满配；架构选型与 ADR；全层级测试 100% 绿 |

预发布流水线状态流转：`alpha`（内部开发自测）→ `beta`（联调与集成测试）→ `rc`（Release Candidate 阶段 6 准发布）→ `GA`（正式发布）。

### 3.2 API 接口版本控制 (API Versioning)
1. **单一现行版本优先**：优先采用「单一主版本 + 向后兼容只增可选字段」策略，避免维护多套运行中代码。
2. **破坏性变更显式版本化**：
   - 当必须变更已有字段类型、删除字段或改变鉴权方式时，禁止在原有路由上原地破坏。
   - 采用显式路由版本（如 `/api/v1/orders` → `/api/v2/orders`）或 Header 驱动版本（如 `Accept: application/vnd.company.v2+json`）。
3. **废弃声明周期 (Sunset & Deprecation)**：
   - 旧版本在下线前，必须至少经历一个 MINOR 版本的过渡期。
   - 响应中返回 `Deprecation: true` 与 `Sunset: <Date>` 标准头；接口文档明确标注文档标记 `[DEPRECATED]`。
4. **Mock 契约与版本同步**：
   - 契约文件 `_13_mock_contract/` 中记录版本标签，严格防止客户端与服务端假想对齐。

### 3.3 数据库迁移版本控制 (Database Migration Versioning)
1. **Flyway 风格单调递增**：
   - 脚本必须严格遵循：`V{MAJOR}.{MINOR}.{PATCH}__{description}.sql`；
   - 回滚脚本必须强制配对：`U{MAJOR}.{MINOR}.{PATCH}__{description}.sql`；
   - 版本号必须在所属模块下单调严格递增，严禁在已执行的旧版本之间强插历史版本。
2. **基线脚本不可篡改**：已合并/已发布的迁移脚本严禁二次修改；如有修正必须新建前向迁移版本。
3. **数据行级乐观锁版本号**：
   - 核心业务表强制包含 `version INT NOT NULL DEFAULT 1` 字段；
   - 严禁使用 `desc` 作为列名（避免保留字冲突，用 `description`）。

### 3.4 阶段 6 交付发布与 Git Tag 门禁
1. **版本发布门禁**：
   - 全量测试 `make test` 100% 通过；
   - 规范检查 `python scripts/verify_consistency.py --root .` 100% 通过；
   - 死代码扫描 `python scripts/dead_code_scanner.py --root .` 零孤儿方法。
2. **Git Tag 规范**：
   - Tag 命名遵循 `v{MAJOR}.{MINOR}.{PATCH}`（如 `v1.2.0`）；
   - 提交信息遵循 Conventional Commits（`feat:`, `fix:`, `refactor:`, `BREAKING CHANGE:`）；
   - 在任务详情与交付说明中记录版本发布日志（Release Notes / CHANGELOG）。

---

### 3.5 运行环境依赖与基线声明 (Runtime Environment & Toolchain Declaration)
业界主流研发框架与优秀 Skill 的实践表明：**代码离开运行环境声明是无法自愈执行的**。系统必须在最底层数据物理骨架中固化运行环境基线：
1. **声明式环境清单 (Declarative Environment Manifests)**：
   - **Python**：通过 `pyproject.toml` 或 `requirements.txt` 固化核心依赖版本；通过 `.python-version` 锁定 Python 大版本（例如 `>=3.10`）。
   - **Node / Frontend**：在 `package.json` 中声明 `engines: { "node": ">=18.0.0", "npm": ">=9.0.0" }`，并签入 `package-lock.json` 或 `pnpm-lock.yaml` 消除间接依赖漂移。
   - **Go / Rust / Java**：通过 `go.mod`、`Cargo.toml` 或 `pom.xml` 声明依赖版本与最低编译工具链要求。
2. **运行时环境变量真理与安全隔离**：
   - 根目录必须提供 `.env.example`，作为所有运行期环境变量配置项的权威字典清单；
   - 严禁将真实敏感密钥（API Key、生产数据库密码）提交进 Git 版本库；
   - 架构设计文档中必须配套 `hs_dev_docs/_03_arch_design/runtime_env.md`，记录网络拓扑、监听端口与三方中间件（Redis/MQ/S3）基线。
3. **三端跨平台兼容铁律**：
   - 所有运行时脚本与路径处理必须坚持 POSIX 风格正斜杠 `/` 与 UTF-8 编码；
   - 严禁在脚本中硬编码操作系统专属路径（如 `C:\\...` 或 `/usr/local/...`）或强依赖平台专属 shell 外部程序。

---

### 3.6 变更账本与版本审计双索引 (Process Audit & Change Log Dual-Indexing)
面向 Agent 辅助研发与连续性续做，版本审计采用**双轨记录与双索引检索**体系：
1. **双轨版本账本**：
   - **宏观业务发布轨**：`CHANGELOG.md` 遵循 Keep a Changelog 规范（Added, Changed, Deprecated, Removed, Fixed, Security），供团队人类开发者查阅；
   - **微观过程审计轨**：`_02_change_log/{task_id}_changes.jsonl` 记录每一步改动的物理快照、修改前状态与精准文件列表，供非 Git 毫秒级回滚与断点续做。
2. **时间与简述双索引物理加速**：
   - **时间索引 (Time B-Tree Index)**：在 `audit_changes(timestamp)` 建立物理索引，支持按毫秒/秒级时间窗口 (`--since`, `--until`) 极速切片审计时间线，无需全盘扫描巨型 JSONL。
   - **简述与影响面索引 (Summary & Impact FTS5 Index)**：在 `audit_changes_fts(checkpoint_id, summary, affected_files, affected_symbols)` 建立全文索引，支持通过文件路径、方法名或意图关键字秒级定位历史断点。

