# 版本号控制与多级包区分演进指南 (Version Control & Multi-Level Packaging)

**何时读**：
- 规划软件发布、版本升级、制定对外 API 策略、新增数据库迁移脚本（阶段 3 详设 / 阶段 6 交付归档）；
- 进行多端分包构建、区分环境构建包、管理 CI/CD 流水线产物（Web/Mobile/Desktop/Server 独立包标识）；
- 维护或升级 Skill 本身时（修改 `SKILL.md`、`README.md` 元数据或扩展规范）。
- 检索命令：`python scripts/skill_ref_index.py search --scenario 版本` 或 `search --q "版本号 四段式 打包版本"`

---

## 1. 核心定位与四段式版本定义体系

本规范确立统一的四段式多级版本号体系：

$$\mathbf{v[\text{主版本}].[\text{需求版本}].[\text{修复版本}].[\text{打包版本}]} \quad (\mathbf{v\text{MAJOR}.\text{FEATURE}.\text{PATCH}.\text{BUILD}})$$

通过**多级子版本号**，精准承载架构演化、业务需求、缺陷修复与多端/多环境工程打包区分：

| 层级 | 名称 | 字段位 | 递增与触发场景 | 演进示例 | 归零规则 |
|---|---|---|---|---|---|
| **L1** | **主版本 (Major)** | 第一位 | 架构性重构、破坏性变更 (Breaking Changes)、系统边界重新划分、协议不可逆升级 | `v1.2.3.10` → `v2.0.0.0` | 需求/修复/打包版本全部归 0 |
| **L2** | **需求版本 (Feature)** | 第二位 | 阶段 0~6 新业务功能上线、新增向下兼容模块/API/DB表、对应需求 PRD 冻结与实施 (M/L) | `v1.2.3.10` → `v1.3.0.0` | 修复/打包版本全部归 0 |
| **L3** | **修复版本 (Patch)** | 第三位 | 缺陷 Bugfix (S 分级)、内部非功能重构、安全补丁、测试扩充与局部性能优化 | `v1.2.3.10` → `v1.2.4.0` | 打包版本归 0 |
| **L4** | **打包版本 (Build)** | 第四位 | CI/CD 构建批次、流水线自增序列、多端与多平台分包、多环境部署包区分 | `v1.2.3.10` → `v1.2.3.11` | 独立单调递增或附加子包后缀 |

---

## 2. 多级子版本号与包区分机制 (Multi-Level Package Differentiation)

在现代全栈与多端软件研发中，同一套业务源码往往需要在同一发布周期输出不同目标平台（Web, Android, iOS, Desktop, Server）及不同生命周期阶段（Alpha, Beta, RC, GA）的软件包。**第四段【打包版本】专用于多级包区分**：

### 2.1 流水线构建序列号区分 (Pipeline Build Sequence)
- 格式：`v{MAJOR}.{FEATURE}.{PATCH}.{BUILD_NUMBER}`
- 规则：每次由 CI/CD 流水线触发编译打包时，`BUILD_NUMBER` 严格单调递增（例如 `v1.2.0.1024`）。
- 作用：构建产物、SBOM 资产清册及 `SHA256SUMS` 唯一锚定特定构建事件，彻底消灭“同名包覆盖”造成的生产灾难。

### 2.2 运行生命周期与环境包区分 (Lifecycle & Environment Tier)
通过第四位附加环境阶段标识，区分研发流转阶段：
- **开发内测包**：`v1.2.0.1-alpha` 或 `v1.2.0.1.dev`（用于开发者本地或极早期功能验证）；
- **联调集成包**：`v1.2.0.1-beta`（用于前后端联调、测试团队集成测试）；
- **准发布候选包**：`v1.2.0.1-rc.1`（Release Candidate，用于阶段 6 交付验收与预发冒烟）；
- **正式生产包**：`v1.2.0.1`（或 `v1.2.0.1-ga`，通过全量质量门禁后的线上签发包）。

### 2.3 多端/多平台分包区分 (Multi-Client Target Sub-Packaging)
依据 Skill 规约，跨端客户端源码收敛于 `apps/<client>/`，打包产出物收敛于 `output/<client>/`。当同一批次触发多端构建时，通过多级子版本号后缀区分各端独立交付包：

```text
源码版本基线: v1.2.0.1
   ├─ Web 交付包:      output/web/app-v1.2.0.1+web.tar.gz
   ├─ Android 客户端:   output/mobile/app-v1.2.0.1+apk.apk (配套 mapping-v1.2.0.1+apk.txt)
   ├─ iOS 客户端:       output/mobile/app-v1.2.0.1+ipa.ipa (配套 dSYM-v1.2.0.1+ipa.zip)
   ├─ Desktop 桌面端:   output/desktop/app-v1.2.0.1+desktop.dmg / .exe
   └─ Server 容器镜像:  registry.example.com/app:v1.2.0.1-srv
```

*注：遵循 SemVer 2.0.0 构建元数据规约，`+` 或 `-` 后续子串属于包区分元数据，包版本比较时以基础四段式为准。*

---

## 3. 双轨控制体系

### 3.1 轨 A：Skill 自身版本控制规则 (Skill Package)
保障 `hs-dev-skill` 作为研发基础设施的单源一致性与兼容性：
- 采用四段式多级版本号：`v{MAJOR}.{FEATURE}.{PATCH}.{BUILD}`（当前为 `v2.41.0.0`）。
  - **MAJOR (主版本)**：发生方法论与架构破裂（如状态机破坏性重构、核心目录结构废弃、硬门禁逻辑变更）；
  - **FEATURE (需求版本)**：新增大规约文档、新增全套生命周期机制（如本期的工程附属机制矩阵）；
  - **PATCH (修复版本)**：规约细化、Bugfix、单测补充、文档格式修正；
  - **BUILD (打包版本)**：Skill 发行构建序列、发布打包流水线批次。

#### 三处元数据单源一致性铁律 (Single Source of Truth)
Skill 自身发布时，以下三处版本号必须**绝对一致**，由 `verify_consistency.py` 自动化检查阻断：
1. `SKILL.md` frontmatter 的 `metadata.version`（例如 `"2.41.0.0"`）；
2. `SKILL.md` 正文首部的 `版本：v2.41.0.0`；
3. `README.md` 的 Shields badge（例如 `[![Spec Version](https://img.shields.io/badge/skill-v2.41.0.0-blue.svg)](SKILL.md)`）。

---

### 3.2 轨 B：工程研发与交付版本控制规则 (Project & Deliverable)

#### 变更分级 (Right-Sizing) 与四段式版本映射
需求与任务分级（[`right_sizing.md`](right_sizing.md)）直接驱动版本跃迁：

| 变更分级 | 对应版本跃迁 | 典型场景 | 门禁与发布策略 |
|---|---|---|---|
| **S (Small)** | **PATCH** (`X.Y.Z.B → X.Y.Z+1.0`) | 内部 Bugfix、安全补丁、无对外影响的非逻辑微调 | 跑通单测与局部回归；不触发 API/DB 主版本与需求版本变更 |
| **M (Medium)** | **FEATURE** (`X.Y.Z.B → X.Y+1.0.0`) | 新增向下兼容的业务功能、新增接口/字段、新增数据库表或字段 | 阶段 0 PRD 冻结；DB 前向+回滚双向脚本；契约测试全通过 |
| **L (Large)** | **MAJOR** (`X.Y.Z.B → X+1.0.0.0`) | 破坏性重构、跨领域边界大版本升级、核心数据模型颠覆 | 阶段 0～6 满配；架构 ADR；全量测试 100% 绿；依赖与安全硬阻断 |
| **BUILD** | **BUILD** (`X.Y.Z.B → X.Y.Z.B+1`) | 仅触发打包、多端重新编译、容器重新打镜像 | 静态检测与冒烟验证，输出多端包及 SBOM |

---

## 4. API、数据库与 Git Tag 的多级版本协同规约

### 4.1 API 接口版本控制 (API Versioning)
1. **URL 路由聚焦主版本**：路由路径只保留主版本（如 `/api/v1/orders`），避免因为需求小特性频繁破坏客户端路由。
2. **HTTP Header 携带完整四段式**：
   - 客户端请求可携带：`X-Client-Version: v1.2.0.1+apk`；
   - 服务端响应返回：`X-App-Version: v1.2.0.1`，实现精细化客户端版本识别与灰度分流。
3. **破坏性变更与废弃声明 (Sunset)**：
   - 当旧接口需下线时，必须在需求版本变更时标记 `[DEPRECATED]`，并在响应头返回 `Deprecation: true` 与 `Sunset: <Date>`。

### 4.2 数据库迁移版本控制 (Database Migration Versioning)
1. **四段式或三段式单调递增脚本**：
   - 升级脚本：`V{MAJOR}_{FEATURE}_{PATCH}_{BUILD}__{description}.sql`（或精简为 `V{MAJOR}.{FEATURE}.{PATCH}__{desc}.sql`）；
   - 回滚脚本强制配对：`U{MAJOR}_{FEATURE}_{PATCH}_{BUILD}__{description}.sql`；
   - 严禁在已发布的历史脚本之间强插新版本。
2. **数据表行级乐观锁版本号**：
   - 核心业务表强制包含 `version INT NOT NULL DEFAULT 1` 字段，杜绝并发覆写。

### 4.3 Git Tag 规范与交付门禁
1. **Git Tag 命名**：
   - 全局发布 Tag：`v{MAJOR}.{FEATURE}.{PATCH}.{BUILD}`（例如 `v1.2.0.1`）；
   - 客户端专属 Tag：`v1.2.0.1-web`、`v1.2.0.1-apk`。
2. **阶段 6 交付门禁硬阻断**：
   - 全量测试 `make test` 100% 通过（0 报错）；
   - 规范检查 `python scripts/verify_consistency.py --root . --strict` 100% 通过；
   - 环境变量与机密扫描 0 泄露，Lockfile 100% 对齐；
   - Conventional Commits 规范校验通过，Release Notes 归档。
