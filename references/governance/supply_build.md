# 3. 机制二：软件供应链与依赖合规机制 (Supply Chain & Security)

**何时读**：处理3. 机制二：软件供应链与依赖合规机制 (Supply Chain & Security)时；先沿用[入口公共约束](../auxiliary_governance.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
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
