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
