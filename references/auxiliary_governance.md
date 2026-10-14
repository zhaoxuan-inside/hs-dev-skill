# 工程附属机制与治理支撑规范指南 (Auxiliary Engineering & Governance Guide)

**何时读**：
- 需求规划与架构设计阶段（阶段 1～2），评估系统环境配置、依赖安全、日志监控与容灾回滚；
- 编码实现与 CI/CD 交付阶段（阶段 4～6），执行密钥防泄露、Lockfile 锁定、健康探针及 SBOM 归档；
- 检索命令：`python scripts/skill_ref_index.py search --scenario 附属机制` 或 `search --q "环境变量 密钥 CVE 探针"`

---

## 1. 核心定位与治理矩阵

代码逻辑的正确性（通过 TDD 保证）是系统交付的基础，但生产级软件的抗脆弱性取决于其**附属工程治理机制**。本指南确立 7 大工程附属支撑机制，与版本控制（SemVer 四段式）协同构成完整的工程防护网：

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   hs-dev-skill 工程附属治理支撑矩阵                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 环境配置与机密隔离   │ 多环境解耦 · .env.example 强契约 · 零密钥硬编码      │
│ 2. 软件供应链与依赖安全 │ Lockfile 不可变锁定 · CVE 脆弱性审计 · 开源协议合规  │
│ 3. CI/CD 制品与发布防伪 │ 五阶流水线 · 特性开关 Feature Flags · SBOM 资产清册  │
│ 4. 可观测性与运行时遥测 │ JSON 结构化日志 · 链路 TraceID 穿透 · 三态健康探针   │
│ 5. 数据韧性与容灾回滚   │ RPO/RTO 明确 · 数据库双向迁移 V/U · 外部依赖熔断降级 │
│ 6. 安全防御与隐私合规   │ PII 数据脱敏 · OWASP Top 10 防线 · 不可篡改审计流水  │
│ 7. Agent 执行安全护栏   │ 高危命令拦截 · 工作区越界防御 · 资源超时熔断        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 机制一：环境配置与机密凭据隔离 (Environment & Secrets)

### 2.1 三态环境严格解耦
禁止一套配置跑天下。系统强制划分三态环境配置：
- `development`：本地开发调试，支持 Mock 适配器与本地 SQLite/Redis；
- `staging`：集成测试环境，对接测试数据库与沙箱三方服务；
- `production`：生产运行环境，强制开启强鉴权、SSL/TLS、连接池与真实监控。

### 2.2 配置单源与 `.env.example` 强契约
1. **权威字典清单**：项目根目录或 `config/` 必须维护 `.env.example`，列出所有运行期所需的环境变量。
2. **三元要素注释**：每个变量必须包含：**类型与默认值**、**用途说明**、**环境必填性**。
   ```bash
   # [必需] 数据库连接串 (PostgreSQL 格式)
   DATABASE_URL=postgresql://user:password@localhost:5432/app_db
   
   # [可选] 服务监听端口，默认 8080
   PORT=8080
   
   # [生产必需] JWT 签名密钥 (至少 32 字符随机串)
   JWT_SECRET=change-me-in-production-random-32-chars
   ```
3. **启动期强校验 (Fail-Fast)**：应用启动入口必须前置校验环境变量。若关键环境变量缺失或格式非法，立即 Panic 退出并打印明确错误，严禁静默回退造成运行态脏数据。

### 2.3 零密钥硬编码与防泄露门禁 (Zero-Secrets Policy)
1. **零密钥入库**：真实 API Key、私钥证书（`.pem`, `.key`）、生产数据库密码绝对禁止提交进 Git 版本库。
2. **Pre-commit 扫描规则**：`verify_consistency.py` 与 Git Hooks 对提交内容实施模式匹配拦截：
   - 典型特征：包含 `BEGIN RSA PRIVATE KEY`、`AKIA[0-9A-Z]{16}`、`ghp_[0-9a-zA-Z]{36}`、`sk-[a-zA-Z0-9]{48}` 等模式立即阻断。

---

## 3. 机制二：软件供应链与依赖合规机制 (Supply Chain & Security)

### 3.1 不可变依赖锁强校验 (Lockfile Enforcement)
1. **锁文件强制签入**：不同语言必须签入其锁文件，消除间接依赖小版本自动升级引发的不可预期漂移：
   - Python: `poetry.lock` 或 `requirements.txt` (带精确版本与哈希)；
   - Node: `package-lock.json` 或 `pnpm-lock.yaml`；
   - Go: `go.sum`；
   - Rust: `Cargo.lock`。
2. **构建安装模式**：CI/CD 和生产构建必须使用冻结模式（例如 `npm ci`、`pnpm install --frozen-lockfile`），禁止生成新的解析结果。

### 3.2 CVE 漏洞扫描与阻断基线
1. 阶段 6 交付验收与 CI 流程中，必须执行依赖包漏洞审计工具（如 `npm audit`, `pip-audit`, `cargo-audit`）。
2. **阻断红线**：存在 **Critical (严重)** 或 **High (高危)** 漏洞的第三方依赖，硬阻断发布，必须修复或升级后方可交付。

### 3.3 开源协议合规白名单 (License Compliance)
1. **商业友好许可**：推荐优先选用 `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`。
2. **传染性协议隔离**：在商业闭源或企业交付项目中，未经法务或技术委员会特批，禁止引入 `GPL-2.0`, `GPL-3.0`, `AGPL-3.0` 等强传染性开源库。

---

## 4. 机制三：构建打包、本地自治与可选流水线机制 (Build, Local Autonomy & Optional CI/CD)

### 4.1 本地自治优先与 CI/CD 解耦原则
1. **无需强绑外部 CI/CD**：构建、验证与版本发布流程**不强制依赖外部 CI/CD 平台**（如 GitHub Actions、GitLab CI 均属可选增强）。
2. **版本号本地自主生成**：版本号严禁依赖外部流水线环境变量注入，必须通过内置工具自主生成，**打包版本优先使用时间戳格式 `MMddHHmmss`**（10位月日时分秒，如 `python scripts/version_tool.py generate`）。
3. **标准本地五阶门禁**：本地单机即可完全闭环执行交付验证：
   - ① **Lint**：`python scripts/verify_consistency.py --root . --strict`（静态规范零告警零错误）；
   - ② **Test**：`make test`（单元测试与契约测试 100% PASS 且 0 报错）；
   - ③ **Security**：凭证泄露扫描与 Lockfile 校验（门禁自动执行）；
   - ④ **Build**：本地自主打包并生成时间戳版本号与产物；
   - ⑤ **Smoke**：针对构建产物执行冒烟验证与健康探针校验。
4. **云端流水线定位**：云端 CI/CD 仅作为团队多人协作与仓库远程合规时的“镜像备份流水线”，绝不阻断单机开发流转。

### 4.2 特性开关机制 (Feature Flags)
1. 针对变更分级为 M 或 L 的重大功能模块，必须使用特性开关包裹，支持主干开发与平滑灰度。
2. **开关生命周期**：
   - `Flag Defined` -> `Active & Controlled (灰度中)` -> `Full Rollout (100%全量)` -> `Flag Retired (废弃拔除代码)`。
   - 禁止让特性开关长期沉淀为技术债务（全量上线 2 个版本内必须清理开关分支代码）。

### 4.3 软件物料清单 (SBOM) 与 SHA256 防伪验签
1. **SBOM 生成**：阶段 6 正式发布时，自动生成 `output/sbom.json`（支持 SPDX 或 CycloneDX 格式），完整记录所有直接与传递依赖的名称、版本与来源。
2. **校验和清册**：所有对外发布的二进制包、归档包必须生成 `SHA256SUMS` 文件，供下载者和运维部署进行完整性与防篡改校验。

---

## 5. 机制四：可观测性与运行时遥测机制 (Observability & Probes)

### 5.1 JSON 结构化日志契约
生产环境禁止使用控制台裸字符串 `print` 或 `console.log`，必须统一采用结构化日志记录器，每条日志至少包含以下标准字段：
- `timestamp`：ISO-8601 标准 UTC 时间戳（如 `2026-10-14T09:15:00.000Z`）；
- `level`：日志级别（`DEBUG`, `INFO`, `WARN`, `ERROR`）；
- `trace_id`：全局分布式追踪 ID（由网关生成并在所有微服务间通过 HTTP Header 穿透）；
- `span_id`：当前调用跨度 ID；
- `message`：人类可读事件简述；
- `context`：结构化键值对（如 `user_id`, `order_no`, `duration_ms`）。

### 5.2 标准健康探针规范 (Health Probes)
微服务与后端应用必须提供标准的 HTTP 探针端点：
- `GET /livez` (Liveness)：进程存活探针，返回 `200 OK` 表示主进程未死锁、未崩溃；
- `GET /readyz` (Readiness)：服务就绪探针，检查关键依赖（如数据库连接池、Redis 缓存）是否正常可用，就绪返回 `200`，否则返回 `503` 并切断流量；
- `GET /healthz` (Diagnostics)：健康诊断端点，返回当前系统版本号（符合四段式）、运行耗时、各子模块健康状态摘要。

### 5.3 崩溃堆栈与符号表强绑定归档
移动端（Android/iOS）及桌面端打包时，符号表（Android Proguard `mapping.txt`、iOS `dSYM`、Web/Electron `source-map`）必须与四段式打包版本号绝对一致，并自动归档至 `output/<client>/symbols/`，严禁遗失导致线上崩溃无法还原堆栈。

---

## 6. 机制五：数据韧性与容灾回滚机制 (Data Resilience & DR)

### 6.1 业务容灾目标 (RPO & RTO)
在阶段 2 架构设计文档中，必须明确核心数据存储的容灾指标：
- **RPO (Recovery Point Objective)**：系统遭遇严重故障时允许丢失的最大数据时间范围（如核心交易 RPO < 1 分钟）；
- **RTO (Recovery Time Objective)**：从故障发生到服务完全恢复所需的最大时间（如核心服务 RTO < 15 分钟）。

### 6.2 数据库迁移 V/U 原子配对与备份指引
1. 每一份前向数据库升级脚本 `V{ver}__{desc}.sql` 必须配对 `U{ver}__{desc}.sql` 回滚脚本。
2. 在执行任何涉及 `ALTER TABLE DROP COLUMN`、`TRUNCATE` 或大表重构的 DDL 前，必须在前置步骤中提供物理快照/逻辑备份命令说明。

### 6.3 外部依赖熔断与降级预案 (Circuit Breaker & Fallback)
调用三方依赖（如第三方支付、短信网关、大模型推理 API）时：
- 必须配置合理的超时时间（Timeout）与指数避退重试策略（Exponential Backoff）；
- 必须具备熔断器（连续失败阈值触发熔断，避免级联雪崩）；
- 必须提供降级兜底方案（Fallback），例如返回默认展示、降级走本地缓存或返回友好排队提示。

---

## 7. 机制六：安全防御与数据隐私合规 (Security & Privacy)

### 7.1 PII 敏感数据脱敏规约 (Data Masking)
涉及个人敏感信息（PII - Personally Identifiable Information）时，必须遵守脱敏红线：
- **手机号**：中间 4 位脱敏（如 `138****8888`）；
- **身份证号**：仅保留前 6 位与后 4 位；
- **银行卡号**：仅保留后 4 位；
- **密码 / Token**：禁止在日志、URL 参数及错误返回中出现任何明文或脱敏值，直接屏蔽；
- **存储加密**：敏感凭据在数据库中必须采用不可逆加密（如 Argon2id / BCrypt）或强对称加密（AES-256-GCM）。

### 7.2 OWASP Top 10 防御底线
1. **注入防御**：数据库查询 100% 使用参数化查询或 ORM，严禁 SQL 字符串拼接；
2. **XSS 与内容安全**：前端渲染富文本必须使用经过审计的 Sanitizer（如 DOMPurify）；
3. **CORS 最小权限**：禁止在生产环境配置通配符 `Access-Control-Allow-Origin: *` 且同时携带 `Allow-Credentials: true`。

### 7.3 不可变审计流水 (Audit Trail)
对于涉及权限变更、敏感数据导出、重要配置修改等关键业务操作，必须记录不可伪造的审计流水表（操作人、来源 IP、时间戳、操作前后差异快照）。

---

## 8. 机制七：Agent 执行安全沙箱与行为护栏 (Agent Guardrails)

针对自主 AI Agent 协助编程与执行命令，强制设立三道安全护栏：
1. **高危破坏性命令硬拦截**：
   - 严禁执行未加保护的系统级清盘命令（如 `rm -rf /`, `mkfs`, `dd if=/dev/zero`）；
   - 严禁执行破坏 Git 历史的未经许可指令（如非受控的 `git push --force` 覆盖主分支）；
2. **工作区边界隔离**：
   - Agent 的读写操作必须收敛于当前项目工作区根目录下，严禁擅自修改宿主机的用户全局凭证目录（如 `~/.ssh/`, `~/.aws/`, `~/.gnupg/`）；
3. **资源占用与超时熔断**：
   - 任何由 Agent 触发的长时间运行命令（测试套件、构建任务）必须设置合理的执行超时阈值（如单命令默认不超过 180 秒），防止无限死循环耗尽算力与 Token。
