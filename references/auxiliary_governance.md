# 工程附属机制与治理支撑规范指南 (Auxiliary Engineering & Governance Guide)

**何时读**：
- 需求规划与架构设计阶段（阶段 1～2），评估系统环境配置、依赖安全、日志监控与容灾回滚；
- 编码实现与 CI/CD 交付阶段（阶段 4～6），执行密钥防泄露、Lockfile 锁定、健康探针及 SBOM 归档；
- 检索命令：`python scripts/skill_ref_index.py search --scenario 附属机制` 或 `search --q "环境变量 密钥 CVE 探针"`

---

<!-- HS_SECTION_INDEX -->

**按业务装载**：正文已拆成独立文件。先沿用本页公共约束，只打开当前业务/阶段需要的分册；不要顺序读全套。分册独立进行变化检查；迁移后旧的行号/摘要须重新定位，已有签收不得自动迁移。

## 0. 功能模式启用控制机制 (Governance Feature Toggle)

正文见 [governance/controls.md](governance/controls.md)。

### 0.1 默认启用与停用策略清单

正文见 [governance/controls.md](governance/controls.md)。

### 0.2 CLI 快速控制命令

正文见 [governance/controls.md](governance/controls.md)。

## 1. 核心定位与治理矩阵

正文见 [governance/controls.md](governance/controls.md)。

## 2. 机制一：环境配置与机密凭据隔离 (Environment & Secrets)

正文见 [governance/environment.md](governance/environment.md)。

### 2.1 三态环境严格解耦

正文见 [governance/environment.md](governance/environment.md)。

### 2.2 配置单源与 `.env.example` 强契约

正文见 [governance/environment.md](governance/environment.md)。

### 2.3 零密钥硬编码与防泄露门禁 (Zero-Secrets Policy)

正文见 [governance/environment.md](governance/environment.md)。

## 3. 机制二：软件供应链与依赖合规机制 (Supply Chain & Security)

正文见 [governance/supply_build.md](governance/supply_build.md)。

### 3.1 不可变依赖锁强校验 (Lockfile Enforcement)

正文见 [governance/supply_build.md](governance/supply_build.md)。

### 3.2 CVE 漏洞扫描与阻断基线

正文见 [governance/supply_build.md](governance/supply_build.md)。

### 3.3 开源协议合规白名单 (License Compliance)

正文见 [governance/supply_build.md](governance/supply_build.md)。

## 4. 机制三：构建打包、本地自治与可选流水线机制 (Build, Local Autonomy & Optional CI/CD)

正文见 [governance/supply_build.md](governance/supply_build.md)。

### 4.1 本地自治优先与 CI/CD 解耦原则

正文见 [governance/supply_build.md](governance/supply_build.md)。

### 4.2 特性开关机制 (Feature Flags)

正文见 [governance/supply_build.md](governance/supply_build.md)。

### 4.3 软件物料清单 (SBOM) 与 SHA256 防伪验签

正文见 [governance/supply_build.md](governance/supply_build.md)。

## 5. 机制四：可观测性与运行时遥测机制 (Observability & Probes)

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

### 5.1 JSON 结构化日志契约

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

### 5.2 标准健康探针规范 (Health Probes)

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

### 5.3 崩溃堆栈与符号表强绑定归档

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

## 6. 机制五：数据韧性与容灾回滚机制 (Data Resilience & DR)

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

### 6.1 业务容灾目标 (RPO & RTO)

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

### 6.2 数据库迁移 V/U 原子配对与备份指引

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

### 6.3 外部依赖熔断与降级预案 (Circuit Breaker & Fallback)

正文见 [governance/operations_resilience.md](governance/operations_resilience.md)。

## 7. 机制六：安全防御与数据隐私合规 (Security & Privacy)

正文见 [governance/privacy_agent.md](governance/privacy_agent.md)。

### 7.1 PII 敏感数据脱敏规约 (Data Masking)

正文见 [governance/privacy_agent.md](governance/privacy_agent.md)。

### 7.2 OWASP Top 10 防御底线

正文见 [governance/privacy_agent.md](governance/privacy_agent.md)。

### 7.3 不可变审计流水 (Audit Trail)

正文见 [governance/privacy_agent.md](governance/privacy_agent.md)。

## 8. 机制七：Agent 执行安全沙箱与行为护栏 (Agent Guardrails)

正文见 [governance/privacy_agent.md](governance/privacy_agent.md)。
