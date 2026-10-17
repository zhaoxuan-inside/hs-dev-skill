# 0. 功能模式启用控制机制 (Governance Feature Toggle)

**何时读**：处理0. 功能模式启用控制机制 (Governance Feature Toggle)时；先沿用[入口公共约束](../auxiliary_governance.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 0. 功能模式启用控制机制 (Governance Feature Toggle)

Skill 具备**功能模式动态启停控制能力**，杜绝无脑强塞重型机制。系统通过项目配置文件 `config/governance.yaml` 或内置 CLI 工具按需管理各治理维度的启用与关闭：

### 0.1 默认启用与停用策略清单
| 治理功能模式 | 默认状态 | 核心说明 |
|---|---|---|
| `version_control` | **[ENABLED]** | 四段式多级版本控制与自主 `MMddHHmmss` 时间戳生成 |
| `env_and_secrets` | **[ENABLED]** | 环境配置 `.env.example` 强契约与代码敏感密钥防泄露扫描 |
| `supply_chain_security` | **[ENABLED]** | 软件供应链安全与依赖锁文件 (Lockfile) 不可变校验 |
| `cicd_and_artifacts` | **[DISABLED]** | **CI/CD 流水线与交付制品防伪机制（当前模式不启用，解耦云端流水线）** |
| `observability_telemetry` | **[DISABLED]** | **可观测性与运行时遥测机制（当前模式不启用，免探针与 APM 门禁负担）** |
| `data_resilience_dr` | **[DISABLED]** | **数据韧性与容灾回滚机制（当前模式不启用，免轻量项目重型灾备负担）** |
| `security_privacy` | **[ENABLED]** | 安全防御矩阵、OWASP 底线与个人敏感信息 (PII) 脱敏合规 |
| `agent_guardrails` | **[ENABLED]** | Agent 执行安全沙箱与高危破坏命令拦截护栏 |

### 0.2 CLI 快速控制命令
```bash
# 查看当前所有功能模式启用状态
python scripts/governance_toggle.py status

# 初始化默认配置文件 (config/governance.yaml)
python scripts/governance_toggle.py init

# 动态启用 / 禁用指定功能模式
python scripts/governance_toggle.py enable cicd_and_artifacts
python scripts/governance_toggle.py disable cicd_and_artifacts

# 脚本与门禁快速检查 (返回 0 表示已启用，1 表示未启用)
python scripts/governance_toggle.py check cicd_and_artifacts
```

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
