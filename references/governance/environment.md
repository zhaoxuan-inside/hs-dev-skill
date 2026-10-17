# 2. 机制一：环境配置与机密凭据隔离 (Environment & Secrets)

**何时读**：处理2. 机制一：环境配置与机密凭据隔离 (Environment & Secrets)时；先沿用[入口公共约束](../auxiliary_governance.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
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
