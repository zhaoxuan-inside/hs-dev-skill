# 全层级测试与质量门禁指南

**阶段 6 文档验收**：按 [`engineering_acceptance.md`](engineering_acceptance.md) 的 DELIV 项核对基线、断言、执行报告与交付确认，遵循 [`stage_acceptance.md`](stage_acceptance.md)。现有脚本不自动验证人类签收或测试证据真实性，退出成功不能代替验收。

**何时读**：提交前 / 阶段 6；核对覆盖率与分层目录。  
**方法与节奏（一等公民）**：先读 [`testing.md`](testing.md)（seam、垂直 TDD、分档义务）；本文 = **分层目录 + 覆盖率数字 + 提交清单**。

**质量铁律**：全量测试 100% PASS 且 0 报错；静态检测 0 告警 0 错误；未达标前绝对禁止 Commit 与流转 COMPLETED 交付；分步红绿通过才算该切片完成。

## 1. 九级质量保障分层（融合 DevTools / a11y / 性能审计）

| 目录分层 | 测试类型 | 门禁与覆盖率要求 |
|---|---|---|
| `test/_00_e2e` | 端到端全链路冒烟与运行态测试 | 主流程用例 100% 通过；致命异常链路 100% 覆盖；**双轨制 E2E**：开发期走 Mock Profile 快速冒烟，交付门禁强制直连官方沙箱或 Testcontainers 真实轻量容器（严禁全量假 Mock 蒙混过关）；**集成 Chrome DevTools CDP 自动化**：真实/无头浏览器 Console 错误与未捕获 Promise 异常 100% 清零，关键网络请求 0 挂起 |
| `test/_01_method_test` | 方法级单元测试 | 核心业务逻辑分支覆盖率 ≥ 85%；降级（Fallback）与补偿（Compensate）逻辑 100% 覆盖 |
| `test/_02_integration_test` | 数据库/中间件/RPC 联调测试 | 事务原子性、分布式补偿生效、超时熔断与重试正常生效 |
| `test/_03_contract_test` | 多端/服务契约测试 | 接口请求与响应字段必须与 `_04_engineering_contract/_03_mock_contract/` 中的 Schema 严格一致 |
| `test/_04_regression_test` | 历史缺陷回归测试 | 历史已知缺陷库中的所有用例持续 100% 通过 |
| `test/_05_performance_test` | 性能基准与 CWV 指标测试 | 核心接口响应耗时 P99、QPS 无劣化；**集成 LCP/内存泄漏诊断**：LCP ≤ 2.5s（关键资源预加载）、前端 SPA 路由切换与长任务下**无游离 DOM 与事件监听内存泄漏**（Heap Snapshot 稳定） |
| `test/_06_security_test` | 安全合规扫描 | SQL/NoSQL 注入、XSS、垂直/水平越权、敏感字段日志脱敏校验 |
| `test/_07_compatibility_test`| 多端兼容与无障碍（a11y）测试 | 覆盖目标 OS、不同语言运行时与浏览器引擎矩阵；**集成 a11y 审计**：WCAG 2.1 AA 对比度 ≥ 4.5:1、ARIA 属性合法性、键盘导航全路径闭环 |
| `test/_08_test_data` | 测试数据集管理 | 数据脱敏合规，具备自动化初始化与重入清理机制；**支持数据驱动测试（DDT）**，严禁全量相等脆弱比对，采用 Schema Match + 核心业务字段与领域不变量精准断言；与 `mock/` 外部环境桩数据职责清晰解耦 |

---

## 2. 提交前门禁自检（Pre-Commit Checklist）

在执行 Git 提交或合并前，必须通过以下自检项：
0. **全量测试 100% PASS 与 0 报错（硬阻断门禁）**：`make test`（或项目等价命令）100% PASS，**无任何失败、报错或挂起用例**；若有任一报错，**绝对禁止流转 COMPLETED 与交付**，严禁向用户汇报“已完成但有报错待修”，必须就地排查修复直到全绿；触达 seam 的自动化测已存在；**前端页面无未捕获 Console 报错与网络死锁**（Chrome DevTools 审计通过）。
0b. **代码静态检测零告警零错误（Zero Warnings, Zero Errors Gate）**：语言对应 Linter（Python: Ruff/Mypy, Go: golangci-lint, Rust: clippy, TS/JS/Vue: ESLint/TSC, Java: Checkstyle/SpotBugs 等，详见 [`coding_standards.md`](coding_standards.md)）、死代码扫描（`dead_code_scanner.py`）、规范检查（`verify_consistency.py`）**必须 0 警告（0 Warning）且 0 错误（0 Error）**；任何 Warning 均须当场清理修复，严禁带 Warning 提交或交付。
0c. **术语防歧义与词态矩阵门禁（Zero Forbidden Synonyms & Lifecycle Grammar Gate）**：统一术语词典 `_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml` 格式完备；`verify_consistency.py` 扫描无 `forbidden_alias` 违规命名，无事件动词原形（如 `order.update`）与时间戳（如 `updated_at`）混用，事件主题必须使用过去分词（如 `order.updated`），事件常量收敛导出无裸字符串。
0d. **需求追踪与 100% 验证覆盖率门禁（Requirement Traceability & 100% Coverage Gate）**：任务卡片中若声明了原子需求清单（`REQ-*`），在流转至 `COMPLETED` 终态前必须达到 **100% 验证覆盖率**（$\text{Coverage} = \frac{\text{已验证需求数}}{\text{全部必需需求数}} = 100\%$）；每一项原子需求必须显式映射至自动化测试用例与断言证据；严禁任何必需需求在 `pending`、`failed` 或 `unverified` 状态下宣告任务成功交付（由 `verify_consistency.py` 自动硬阻断）。
1. **死代码与孤儿方法扫描**：所有新增或修改的方法均在 `_04_engineering_contract/_05_call_chain` 中有合法引用路径，或具备白名单注解。
2. **三同步完整性**：业务逻辑修改已同步更新方法设计文档、DB 迁移脚本（V/U）及单元/契约测试。
3. **索引完整性**：新增/重命名/删除的文件已同步更新对应的 `.idx` 索引文件。
4. **三文件一致性**：`_05_task_orchestration/` 下的 `_00_task.idx`、`_01_task_brief/`、`_02_task_detail/` 任务状态与元数据完全吻合。
5. **专项体验与性能合规**：满足 WCAG a11y 关键对比度与键盘访问；无突出的 LCP 阻塞与内存泄漏隐患。
6. **多端产物收敛与环境安全**：打包产物必须通过脚手架配置重定向至 `output/<client>` 对应子目录，工作区根目录下严禁散落二进制安装包；移动端发布包强制配对混淆符号表（Mapping/dSYM）；敏感 `.env` 绝不上库，具备 `config/.env.example` 声明契约。
7. **Git Commit 规范**：提交信息符合 `<type>(<scope>): <subject>` 及相关 Footer 规范；默认仅本地 commit，**用户明确要求推送**时方可 `git push`。

---

## 3. 多端代码与产出目录控制门禁（Workspace & Output Isolation Gate）

在执行提交、打包或发布前，必须确保各端代码与打包产物符合物理隔离标准：
- **应用代码收敛**：各端代码存放于 `apps/<client_name>/`，跨端共享库与类型存放于 `packages/`；
- **产出收敛铁律**：Web、桌面端（Desktop）、移动端（Mobile）所有打包产物（`.html`/`.js`, `.exe`/`.dmg`, `.apk`/`.ipa`）**必须通过构建配置强制重定向至根目录 `output/` 对应子目录**，严禁在子应用内堆积散落产物；
- **符号表齐套门禁**：移动端 Android `mapping.txt` 与 iOS `dSYM.zip` 必须与安装包成对输出归档至 `output/app_mobile/`，缺失符号表禁止发版；
- **配置与密钥安全**：环境配置收敛于 `config/`，敏感密钥绝不上库，必须提供 `config/.env.example` 声明变量契约。
